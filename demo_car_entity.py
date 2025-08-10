#!/usr/bin/env python3
"""
Demo script for the Car entity class.

Demonstrates the Car entity integrating physics simulation with rendering
and game state management.
"""

import pygame
import pymunk
import math
import sys
from typing import List

from src.entities.car import Car
from src.physics.physics_engine import PhysicsEngine
from src.rendering.black_mamba_renderer import BlackMambaRenderer


class CarEntityDemo:
    """Demo application for the Car entity."""
    
    def __init__(self):
        """Initialize the demo."""
        pygame.init()
        
        # Screen setup
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Car Entity Demo - WASD to control, SPACE to switch physics")
        
        # Initialize physics engine
        self.physics_engine = PhysicsEngine()
        
        # Initialize renderer
        self.renderer = BlackMambaRenderer(self.screen_width, self.screen_height)
        
        # Create cars
        self.cars: List[Car] = []
        self._create_cars()
        
        # Demo state
        self.clock = pygame.time.Clock()
        self.running = True
        self.physics_model = "arcade"
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        print("Car Entity Demo")
        print("Controls:")
        print("  WASD - Control player car")
        print("  SPACE - Switch physics model")
        print("  ESC - Exit")
        print(f"Current physics model: {self.physics_model}")
    
    def _create_cars(self) -> None:
        """Create demo cars."""
        # Player car (red)
        player_car = Car(
            car_id="player",
            physics_space=self.physics_engine.space,
            position=(400, 300),
            angle=0,
            is_player=True
        )
        self.cars.append(player_car)
        
        # AI cars (gray)
        ai_positions = [
            (300, 200),
            (500, 400),
            (350, 450)
        ]
        
        for i, pos in enumerate(ai_positions):
            ai_car = Car(
                car_id=f"ai_{i}",
                physics_space=self.physics_engine.space,
                position=pos,
                angle=math.pi * i / 4  # Different starting angles
            )
            self.cars.append(ai_car)
    
    def handle_input(self) -> None:
        """Handle user input."""
        keys = pygame.key.get_pressed()
        
        # Get player car
        player_car = self.cars[0]  # First car is player
        
        # Calculate control inputs
        throttle = 0.0
        steering = 0.0
        brake = 0.0
        
        if keys[pygame.K_w]:
            throttle = 1.0
        elif keys[pygame.K_s]:
            throttle = -0.5  # Reverse is slower
        
        if keys[pygame.K_a]:
            steering = -1.0
        elif keys[pygame.K_d]:
            steering = 1.0
        
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            brake = 1.0
        
        # Apply controls to player car
        player_car.apply_controls(throttle, steering, brake)
        
        # Simple AI for other cars (just drive forward with slight steering)
        for i, car in enumerate(self.cars[1:], 1):
            ai_throttle = 0.3
            ai_steering = math.sin(pygame.time.get_ticks() * 0.001 + i) * 0.2
            car.apply_controls(ai_throttle, ai_steering, 0.0)
    
    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Switch physics model
                    self.physics_model = "realistic" if self.physics_model == "arcade" else "arcade"
                    for car in self.cars:
                        car.switch_physics_model(self.physics_model)
                    print(f"Switched to {self.physics_model} physics")
    
    def update(self, dt: float) -> None:
        """Update game state."""
        # Update all cars
        for car in self.cars:
            car.update(dt)
        
        # Step physics simulation
        self.physics_engine.step(dt)
        
        # Update camera to follow player car
        player_pos = self.cars[0].get_position()
        self.camera_x = player_pos[0] - self.screen_width // 2
        self.camera_y = player_pos[1] - self.screen_height // 2
    
    def render(self) -> None:
        """Render the demo."""
        # Clear screen
        self.renderer.clear_screen()
        self.renderer.clear_ui_surface()
        
        # Save current transform
        screen = self.renderer.get_screen_surface()
        
        # Apply camera transform
        for car in self.cars:
            pos = car.get_position()
            screen_pos = (pos[0] - self.camera_x, pos[1] - self.camera_y)
            
            # Only render if on screen
            if (-50 <= screen_pos[0] <= self.screen_width + 50 and
                -50 <= screen_pos[1] <= self.screen_height + 50):
                
                # Temporarily modify renderer for camera offset
                original_draw_car = self.renderer.draw_car
                
                def draw_car_with_camera(position, angle, color=None):
                    camera_pos = (position[0] - self.camera_x, position[1] - self.camera_y)
                    original_draw_car(camera_pos, angle, color)
                
                self.renderer.draw_car = draw_car_with_camera
                car.render(self.renderer)
                self.renderer.draw_car = original_draw_car
        
        # Render HUD
        self._render_hud()
        
        # Present frame
        self.renderer.present()
    
    def _render_hud(self) -> None:
        """Render HUD information."""
        player_car = self.cars[0]
        car_info = player_car.get_car_info()
        
        # Car information
        # Convert from pixels/second to km/h (assuming 1 pixel = 1 meter for racing scale)
        speed_kmh = car_info['speed'] * 3.6  # m/s to km/h conversion
        self.renderer.draw_hud_text(f"Speed: {speed_kmh:.0f} km/h", (10, 10), "medium")
        self.renderer.draw_hud_text(f"Physics: {self.physics_model.title()}", (10, 40), "medium")
        
        # Position and angle
        pos = car_info['position']
        self.renderer.draw_hud_text(f"Position: ({pos[0]:.0f}, {pos[1]:.0f})", (10, 70), "small")
        self.renderer.draw_hud_text(f"Angle: {car_info['angle_degrees']:.0f}°", (10, 90), "small")
        
        # Control inputs
        self.renderer.draw_hud_text(f"Throttle: {car_info['throttle']:.2f}", (10, 120), "small")
        self.renderer.draw_hud_text(f"Steering: {car_info['steering']:.2f}", (10, 140), "small")
        self.renderer.draw_hud_text(f"Brake: {car_info['brake']:.2f}", (10, 160), "small")
        
        # Physics info
        if player_car.is_sliding():
            self.renderer.draw_hud_text("SLIDING!", (10, 190), "medium", (255, 255, 0))
        
        # Performance metrics
        self.renderer.draw_hud_text(f"Top Speed: {car_info['top_speed'] * 3.6:.0f} km/h", (10, 220), "small")
        self.renderer.draw_hud_text(f"Distance: {car_info['distance_traveled']:.0f}m", (10, 240), "small")
        
        # Instructions
        instructions = [
            "WASD - Drive",
            "SHIFT - Brake", 
            "SPACE - Switch Physics",
            "ESC - Exit"
        ]
        
        for i, instruction in enumerate(instructions):
            self.renderer.draw_hud_text(instruction, (self.screen_width - 200, 10 + i * 20), "small")
    
    def run(self) -> None:
        """Run the demo."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # 60 FPS, convert to seconds
            
            self.handle_events()
            self.handle_input()
            self.update(dt)
            self.render()
        
        # Cleanup
        for car in self.cars:
            car.cleanup()
        
        pygame.quit()


def main():
    """Main function."""
    try:
        demo = CarEntityDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())