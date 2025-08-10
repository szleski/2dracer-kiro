#!/usr/bin/env python3
"""
Demo script for the PhysicsEngine class.

This script demonstrates the basic functionality of the physics engine
including body creation, physics simulation, and debug rendering.
"""

import pygame
import pymunk
import sys
import math
from src.physics.physics_engine import PhysicsEngine, PhysicsConfig


def main():
    """Run the physics engine demo."""
    # Initialize Pygame
    pygame.init()
    
    # Set up display
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Physics Engine Demo")
    clock = pygame.time.Clock()
    
    # Create physics engine with debug rendering enabled
    config = PhysicsConfig(model="arcade")
    physics_engine = PhysicsEngine(config)
    physics_engine.enable_debug_rendering(screen)
    
    # Create static boundaries (walls)
    wall_thickness = 10
    walls = [
        # Top wall
        pymunk.Segment(physics_engine.space.static_body, 
                      (0, wall_thickness), (WIDTH, wall_thickness), wall_thickness),
        # Bottom wall
        pymunk.Segment(physics_engine.space.static_body, 
                      (0, HEIGHT - wall_thickness), (WIDTH, HEIGHT - wall_thickness), wall_thickness),
        # Left wall
        pymunk.Segment(physics_engine.space.static_body, 
                      (wall_thickness, 0), (wall_thickness, HEIGHT), wall_thickness),
        # Right wall
        pymunk.Segment(physics_engine.space.static_body, 
                      (WIDTH - wall_thickness, 0), (WIDTH - wall_thickness, HEIGHT), wall_thickness),
    ]
    
    for wall in walls:
        wall.friction = 0.7
        physics_engine.add_static_body(wall)
    
    # Create some dynamic bodies (balls)
    balls = []
    for i in range(5):
        # Create ball at random position
        x = 100 + i * 120
        y = 100 + (i % 2) * 200
        
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 20))
        body.position = x, y
        
        shape = pymunk.Circle(body, 20)
        shape.friction = 0.7
        shape.elasticity = 0.8  # Bouncy balls
        
        physics_engine.add_body(body, shape)
        balls.append((body, shape))
    
    # Create a car-like object (rectangle)
    car_body = pymunk.Body(2, pymunk.moment_for_box(2, (40, 20)))
    car_body.position = WIDTH // 2, HEIGHT // 2
    car_shape = pymunk.Poly.create_box(car_body, (40, 20))
    car_shape.friction = 0.9
    car_shape.elasticity = 0.3
    physics_engine.add_body(car_body, car_shape)
    
    # Demo variables
    font = pygame.font.Font(None, 36)
    physics_model = "arcade"
    show_info = True
    
    print("Physics Engine Demo Controls:")
    print("- Arrow keys: Apply forces to the car")
    print("- SPACE: Switch physics model (arcade/realistic)")
    print("- I: Toggle info display")
    print("- R: Reset simulation")
    print("- ESC: Exit")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Switch physics model
                    physics_model = "realistic" if physics_model == "arcade" else "arcade"
                    physics_engine.switch_physics_model(physics_model)
                    print(f"Switched to {physics_model} physics")
                elif event.key == pygame.K_i:
                    show_info = not show_info
                elif event.key == pygame.K_r:
                    # Reset car position
                    car_body.position = WIDTH // 2, HEIGHT // 2
                    car_body.velocity = 0, 0
                    car_body.angular_velocity = 0
                    car_body.angle = 0
        
        # Handle continuous input (car controls)
        keys = pygame.key.get_pressed()
        force_magnitude = 2000
        
        if keys[pygame.K_UP]:
            # Apply forward force
            angle = car_body.angle
            force_x = force_magnitude * math.cos(angle)
            force_y = force_magnitude * math.sin(angle)
            car_body.apply_force_at_local_point((force_x, force_y), (0, 0))
        
        if keys[pygame.K_DOWN]:
            # Apply backward force
            angle = car_body.angle
            force_x = -force_magnitude * 0.5 * math.cos(angle)
            force_y = -force_magnitude * 0.5 * math.sin(angle)
            car_body.apply_force_at_local_point((force_x, force_y), (0, 0))
        
        if keys[pygame.K_LEFT]:
            # Apply left turning torque
            car_body.apply_force_at_local_point((-force_magnitude * 0.3, 0), (0, 10))
        
        if keys[pygame.K_RIGHT]:
            # Apply right turning torque
            car_body.apply_force_at_local_point((force_magnitude * 0.3, 0), (0, 10))
        
        # Step physics simulation
        physics_engine.step(dt)
        
        # Clear screen
        screen.fill((50, 50, 50))  # Dark gray background
        
        # Render debug physics
        physics_engine.render_debug()
        
        # Display information
        if show_info:
            info = physics_engine.get_physics_info()
            y_offset = 10
            
            texts = [
                f"Physics Model: {info['model'].upper()}",
                f"Bodies: {info['bodies']}",
                f"Shapes: {info['shapes']}",
                f"FPS: {clock.get_fps():.1f}",
                f"Car Position: ({car_body.position.x:.1f}, {car_body.position.y:.1f})",
                f"Car Velocity: {car_body.velocity.length:.1f}",
            ]
            
            for text in texts:
                surface = font.render(text, True, (255, 255, 255))
                screen.blit(surface, (10, y_offset))
                y_offset += 30
        
        # Update display
        pygame.display.flip()
    
    # Cleanup
    physics_engine.cleanup()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()