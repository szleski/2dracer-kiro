#!/usr/bin/env python3
"""
Demo script showing integration between InputManager and Car entity.

This script demonstrates how the InputManager provides smooth input handling
that integrates seamlessly with the Car entity's physics simulation.
"""

import pygame
import pymunk
import sys
import time
from src.input import InputManager, InputAction, ControlSchemes
from src.entities.car import Car
from src.physics.physics_engine import PhysicsEngine
from src.rendering.black_mamba_renderer import BlackMambaRenderer


def main():
    """Run the car input integration demo."""
    print("Car Input Integration Demo")
    print("==========================")
    print()
    
    # Initialize pygame
    pygame.init()
    
    # Create display
    screen_width, screen_height = 1000, 700
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Car Input Integration Demo")
    clock = pygame.time.Clock()
    
    # Create physics engine
    physics_engine = PhysicsEngine()
    
    # Create renderer
    renderer = BlackMambaRenderer(screen_width, screen_height)
    
    # Create input manager with arcade control scheme for responsive demo
    control_scheme = ControlSchemes.arcade_scheme()
    input_manager = InputManager(control_scheme.input_config)
    
    # Create player car
    car_start_position = (screen_width // 2, screen_height // 2)
    player_car = Car(
        car_id="player",
        physics_space=physics_engine.space,
        position=car_start_position,
        angle=0.0,
        is_player=True,
        car_color=(220, 50, 50)  # Red for player
    )
    
    # Set up input callbacks for system actions
    def reset_car():
        print("Resetting car position...")
        player_car.reset_position(car_start_position, 0.0)
    
    def switch_physics():
        current_model = "arcade" if player_car.physics_body.config.friction > 0.8 else "realistic"
        new_model = "realistic" if current_model == "arcade" else "arcade"
        print(f"Switching physics from {current_model} to {new_model}")
        player_car.switch_physics_model(new_model)
    
    input_manager.set_action_callback(InputAction.RESET, reset_car)
    input_manager.set_action_callback(InputAction.SWITCH_PHYSICS, switch_physics)
    
    print("Controls:")
    print("  WASD or Arrow Keys: Drive the car")
    print("  Shift: Reverse")
    print("  Space: Brake")
    print("  R: Reset car position")
    print("  Tab: Switch physics model")
    print("  ESC: Quit")
    print()
    print("Watch how the input smoothing creates natural car movement!")
    print("=" * 60)
    
    # Demo variables
    running = True
    last_info_time = 0
    info_update_interval = 0.5  # Update info display twice per second
    paused = False
    
    while running:
        dt = clock.tick(60) / 1000.0  # 60 FPS, convert to seconds
        current_time = time.time()
        
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    paused = not paused
                    print(f"Game {'paused' if paused else 'resumed'}")
        
        if not paused:
            # Update input manager
            input_manager.update(dt)
            
            # Get car controls from input manager
            throttle, steering, brake = input_manager.get_car_controls()
            
            # Apply controls to car
            player_car.apply_controls(throttle, steering, brake)
            
            # Update physics
            physics_engine.step(dt)
            
            # Update car
            player_car.update(dt)
        
        # Render everything
        renderer.clear_screen()
        
        # Draw car
        player_car.render(renderer)
        
        # Draw input visualization
        draw_input_visualization(renderer, input_manager, screen_width, screen_height)
        
        # Draw car info
        draw_car_info(renderer, player_car, screen_width)
        
        # Present frame
        renderer.present()
        
        # Display periodic info to console
        if current_time - last_info_time >= info_update_interval:
            display_console_info(player_car, input_manager)
            last_info_time = current_time
    
    # Cleanup
    player_car.cleanup()
    physics_engine.cleanup()
    pygame.quit()
    print("\nDemo finished!")


def draw_input_visualization(renderer, input_manager, screen_width, screen_height):
    """Draw visual representation of input state."""
    # Get input info
    info = input_manager.get_input_info()
    
    # Input bars position
    bar_x = 20
    bar_y = screen_height - 150
    bar_width = 200
    bar_height = 20
    
    # Draw background for input display
    pygame.draw.rect(renderer.screen, (40, 40, 40), 
                    (bar_x - 10, bar_y - 10, bar_width + 20, 120))
    
    # Draw throttle bar
    throttle = info['throttle']
    throttle_color = (0, 255, 0) if throttle > 0 else (255, 100, 100) if throttle < 0 else (100, 100, 100)
    throttle_width = int(abs(throttle) * bar_width)
    if throttle_width > 0:
        pygame.draw.rect(renderer.screen, throttle_color, 
                        (bar_x, bar_y, throttle_width, bar_height))
    
    # Draw steering bar
    steering = info['steering']
    steering_center = bar_x + bar_width // 2
    steering_width = int(abs(steering) * bar_width // 2)
    if steering_width > 0:
        steering_color = (100, 100, 255)
        if steering > 0:  # Right
            pygame.draw.rect(renderer.screen, steering_color, 
                            (steering_center, bar_y + 25, steering_width, bar_height))
        else:  # Left
            pygame.draw.rect(renderer.screen, steering_color, 
                            (steering_center - steering_width, bar_y + 25, steering_width, bar_height))
    
    # Draw brake bar
    brake = info['brake']
    brake_width = int(brake * bar_width)
    if brake_width > 0:
        pygame.draw.rect(renderer.screen, (255, 255, 0), 
                        (bar_x, bar_y + 50, brake_width, bar_height))
    
    # Draw labels
    renderer.draw_hud_text("Throttle", (bar_x, bar_y - 20), "small")
    renderer.draw_hud_text("Steering", (bar_x, bar_y + 5), "small")
    renderer.draw_hud_text("Brake", (bar_x, bar_y + 30), "small")
    
    # Draw values
    renderer.draw_hud_text(f"{throttle:+.2f}", (bar_x + bar_width + 10, bar_y), "small")
    renderer.draw_hud_text(f"{steering:+.2f}", (bar_x + bar_width + 10, bar_y + 25), "small")
    renderer.draw_hud_text(f"{brake:.2f}", (bar_x + bar_width + 10, bar_y + 50), "small")


def draw_car_info(renderer, car, screen_width):
    """Draw car information on screen."""
    car_info = car.get_car_info()
    
    # Position for car info
    info_x = screen_width - 250
    info_y = 20
    
    # Draw background
    pygame.draw.rect(renderer.screen, (40, 40, 40), 
                    (info_x - 10, info_y - 10, 240, 160))
    
    # Draw car info
    renderer.draw_hud_text("CAR INFO", (info_x, info_y), "medium")
    
    y_offset = 25
    info_items = [
        f"Speed: {car_info['speed']:.1f} px/s",
        f"Forward: {car_info['forward_speed']:.1f} px/s",
        f"Lateral: {car_info['lateral_speed']:.1f} px/s",
        f"Sliding: {'YES' if car_info['is_sliding'] else 'NO'}",
        f"Physics: {car_info['physics_model'].title()}",
        f"Position: ({car_info['position'][0]:.0f}, {car_info['position'][1]:.0f})",
        f"Angle: {car_info['angle_degrees']:.1f}°"
    ]
    
    for item in info_items:
        renderer.draw_hud_text(item, (info_x, info_y + y_offset), "small")
        y_offset += 18


def display_console_info(car, input_manager):
    """Display information to console."""
    car_info = car.get_car_info()
    input_info = input_manager.get_input_info()
    
    print(f"Speed: {car_info['speed']:6.1f} | "
          f"Throttle: {input_info['throttle']:+6.3f} | "
          f"Steering: {input_info['steering']:+6.3f} | "
          f"Brake: {input_info['brake']:6.3f} | "
          f"Physics: {car_info['physics_model']}")


def test_integration():
    """Test the integration without GUI."""
    print("Testing Car-Input Integration:")
    print("=" * 40)
    
    # Initialize pygame for key constants
    pygame.init()
    
    # Create physics engine
    physics_engine = PhysicsEngine()
    print("✓ Physics engine created")
    
    # Create input manager
    input_manager = InputManager()
    print("✓ Input manager created")
    
    # Create car
    car = Car(
        car_id="test_car",
        physics_space=physics_engine.space,
        position=(400, 300),
        is_player=True
    )
    print("✓ Car created")
    
    # Test applying controls
    input_manager.input_state.accelerate = 0.5
    input_manager.input_state.steer_right = 0.3
    
    throttle, steering, brake = input_manager.get_car_controls()
    car.apply_controls(throttle, steering, brake)
    print(f"✓ Controls applied: throttle={throttle}, steering={steering}, brake={brake}")
    
    # Test physics update
    physics_engine.step(0.016)  # 60 FPS
    car.update(0.016)
    print("✓ Physics and car updated")
    
    # Check that car moved
    position = car.get_position()
    speed = car.get_speed()
    print(f"✓ Car position: {position}, speed: {speed:.2f}")
    
    # Cleanup
    car.cleanup()
    physics_engine.cleanup()
    pygame.quit()
    
    print("✓ Integration test passed!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run test without GUI
        test_integration()
    else:
        # Run interactive demo
        try:
            main()
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        except Exception as e:
            print(f"\nError running demo: {e}")
            import traceback
            traceback.print_exc()