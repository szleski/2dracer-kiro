#!/usr/bin/env python3
"""
Demo script for car physics implementation.

This script demonstrates the CarBody class with both arcade and realistic
physics configurations, showing car movement, steering, and collision detection.
"""

import pygame
import pymunk
import math
import sys
from src.physics.car_physics import CarBody, CarPhysicsPresets
from src.physics.physics_engine import PhysicsEngine


def main():
    """Run the car physics demo."""
    # Initialize Pygame
    pygame.init()
    
    # Screen dimensions
    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Car Physics Demo - WASD to drive, R to reset, P to switch physics")
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 68, 68)
    GRAY = (128, 128, 128)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
    # Create physics engine
    physics_engine = PhysicsEngine()
    physics_engine.enable_debug_rendering(screen)
    
    # Create car with arcade physics
    car = CarBody(physics_engine.space, position=(WIDTH//2, HEIGHT//2))
    current_physics = "arcade"
    
    # Create track boundaries
    boundaries = []
    boundary_thickness = 10
    
    # Top boundary
    top_boundary = pymunk.Segment(physics_engine.space.static_body, 
                                 (0, boundary_thickness), (WIDTH, boundary_thickness), 
                                 boundary_thickness)
    top_boundary.collision_type = 2
    top_boundary.friction = 0.8
    boundaries.append(top_boundary)
    
    # Bottom boundary
    bottom_boundary = pymunk.Segment(physics_engine.space.static_body, 
                                   (0, HEIGHT - boundary_thickness), (WIDTH, HEIGHT - boundary_thickness), 
                                   boundary_thickness)
    bottom_boundary.collision_type = 2
    bottom_boundary.friction = 0.8
    boundaries.append(bottom_boundary)
    
    # Left boundary
    left_boundary = pymunk.Segment(physics_engine.space.static_body, 
                                 (boundary_thickness, 0), (boundary_thickness, HEIGHT), 
                                 boundary_thickness)
    left_boundary.collision_type = 2
    left_boundary.friction = 0.8
    boundaries.append(left_boundary)
    
    # Right boundary
    right_boundary = pymunk.Segment(physics_engine.space.static_body, 
                                  (WIDTH - boundary_thickness, 0), (WIDTH - boundary_thickness, HEIGHT), 
                                  boundary_thickness)
    right_boundary.collision_type = 2
    right_boundary.friction = 0.8
    boundaries.append(right_boundary)
    
    # Add boundaries to space
    for boundary in boundaries:
        physics_engine.space.add(boundary)
    
    # Add some obstacles
    obstacles = []
    for i in range(3):
        x = 200 + i * 200
        y = 200 + (i % 2) * 200
        obstacle = pymunk.Circle(physics_engine.space.static_body, 30, (x, y))
        obstacle.collision_type = 2
        obstacle.friction = 0.8
        obstacles.append(obstacle)
        physics_engine.space.add(obstacle)
    
    # Collision callback
    collision_count = 0
    def on_collision(info):
        nonlocal collision_count
        collision_count += 1
        print(f"Collision {collision_count}: {info['point']}")
    
    car.set_collision_callback(on_collision)
    
    # Game loop
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset car position
                    car.reset_position((WIDTH//2, HEIGHT//2), 0)
                    collision_count = 0
                elif event.key == pygame.K_p:
                    # Switch physics model
                    if current_physics == "arcade":
                        car.switch_physics_config(CarPhysicsPresets.realistic())
                        current_physics = "realistic"
                    else:
                        car.switch_physics_config(CarPhysicsPresets.arcade())
                        current_physics = "arcade"
                    print(f"Switched to {current_physics} physics")
        
        # Handle input
        keys = pygame.key.get_pressed()
        throttle = 0.0
        steering = 0.0
        brake = 0.0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            throttle = 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            throttle = -1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            steering = -1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            steering = 1.0
        if keys[pygame.K_SPACE]:
            brake = 1.0
        
        # Apply controls to car
        car.apply_controls(throttle, steering, brake)
        
        # Update physics
        car.update_physics(dt)
        physics_engine.step(dt)
        
        # Clear screen
        screen.fill(WHITE)
        
        # Draw boundaries
        for boundary in boundaries:
            if hasattr(boundary, 'a') and hasattr(boundary, 'b'):
                start = (int(boundary.a.x), int(boundary.a.y))
                end = (int(boundary.b.x), int(boundary.b.y))
                pygame.draw.line(screen, BLACK, start, end, boundary_thickness * 2)
        
        # Draw obstacles
        for obstacle in obstacles:
            pos = (int(obstacle.offset.x), int(obstacle.offset.y))
            pygame.draw.circle(screen, GRAY, pos, int(obstacle.radius))
        
        # Draw car
        car_pos = (int(car.body.position.x), int(car.body.position.y))
        car_angle = car.body.angle
        
        # Calculate car corners for drawing
        half_width = car.config.width / 2
        half_height = car.config.height / 2
        
        corners = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height)
        ]
        
        # Rotate and translate corners
        rotated_corners = []
        for corner in corners:
            rotated_x = corner[0] * math.cos(car_angle) - corner[1] * math.sin(car_angle)
            rotated_y = corner[0] * math.sin(car_angle) + corner[1] * math.cos(car_angle)
            rotated_corners.append((
                int(car_pos[0] + rotated_x),
                int(car_pos[1] + rotated_y)
            ))
        
        pygame.draw.polygon(screen, RED, rotated_corners)
        
        # Draw forward direction indicator
        forward = car.get_forward_vector()
        forward_end = (
            int(car_pos[0] + forward.x * 30),
            int(car_pos[1] + forward.y * 30)
        )
        pygame.draw.line(screen, BLACK, car_pos, forward_end, 3)
        
        # Draw velocity vector
        velocity = car.body.velocity
        if velocity.length > 1:
            vel_scale = min(velocity.length / 5, 50)
            vel_end = (
                int(car_pos[0] + velocity.x / velocity.length * vel_scale),
                int(car_pos[1] + velocity.y / velocity.length * vel_scale)
            )
            pygame.draw.line(screen, BLUE, car_pos, vel_end, 2)
        
        # Draw debug physics
        physics_engine.render_debug()
        
        # Draw UI
        physics_info = car.get_physics_info()
        
        # Title
        title_text = font.render(f"Car Physics Demo - {current_physics.title()} Mode", True, BLACK)
        screen.blit(title_text, (10, 10))
        
        # Instructions
        instructions = [
            "WASD/Arrow Keys: Drive",
            "Space: Brake",
            "R: Reset position",
            "P: Switch physics model"
        ]
        
        for i, instruction in enumerate(instructions):
            text = small_font.render(instruction, True, BLACK)
            screen.blit(text, (10, 50 + i * 20))
        
        # Physics info
        info_lines = [
            f"Speed: {physics_info['speed']:.1f} px/s",
            f"Forward Speed: {physics_info['forward_speed']:.1f} px/s",
            f"Lateral Speed: {physics_info['lateral_speed']:.1f} px/s",
            f"Sliding: {'Yes' if physics_info['is_sliding'] else 'No'}",
            f"Throttle: {physics_info['throttle']:.2f}",
            f"Steering: {physics_info['steering']:.2f}",
            f"Brake: {physics_info['brake']:.2f}",
            f"Collisions: {collision_count}"
        ]
        
        for i, line in enumerate(info_lines):
            color = RED if "Sliding: Yes" in line else BLACK
            text = small_font.render(line, True, color)
            screen.blit(text, (WIDTH - 200, 50 + i * 20))
        
        # Update display
        pygame.display.flip()
    
    # Cleanup
    car.cleanup()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()