#!/usr/bin/env python3
"""
Demo script for the InputManager system.

This script demonstrates the input handling system with real-time feedback
showing how keyboard inputs are processed and converted to car controls.
"""

import pygame
import sys
import time
from src.input import InputManager, InputAction, ControlSchemes, ControlsHelper


def main():
    """Run the input manager demo."""
    print("Input Manager Demo")
    print("==================")
    print()
    
    # Initialize pygame
    pygame.init()
    
    # Create display for pygame event handling
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Input Manager Demo")
    clock = pygame.time.Clock()
    
    # Create input manager with combined control scheme
    control_scheme = ControlSchemes.combined_scheme()
    input_manager = InputManager(control_scheme.input_config)
    
    print("Control Scheme:")
    print(ControlsHelper.format_control_scheme(control_scheme))
    print()
    print("Press keys to see input response. Press ESC to quit.")
    print("=" * 60)
    
    # Demo variables
    running = True
    last_info_time = 0
    info_update_interval = 0.1  # Update info display 10 times per second
    
    # Set up action callbacks
    def on_pause():
        print("PAUSE action triggered!")
    
    def on_reset():
        print("RESET action triggered!")
    
    def on_switch_physics():
        print("SWITCH PHYSICS action triggered!")
    
    input_manager.set_action_callback(InputAction.PAUSE, on_pause)
    input_manager.set_action_callback(InputAction.RESET, on_reset)
    input_manager.set_action_callback(InputAction.SWITCH_PHYSICS, on_switch_physics)
    
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
        
        # Update input manager
        input_manager.update(dt)
        
        # Get car controls
        throttle, steering, brake = input_manager.get_car_controls()
        
        # Display info periodically
        if current_time - last_info_time >= info_update_interval:
            # Clear screen (simple console output)
            print("\033[2J\033[H", end="")  # ANSI clear screen and move cursor to top
            
            print("Input Manager Demo - Real-time Input Display")
            print("=" * 60)
            print()
            
            # Display car controls
            print("CAR CONTROLS:")
            print(f"  Throttle: {throttle:6.3f} {'█' * int(abs(throttle) * 20)}")
            print(f"  Steering: {steering:6.3f} {'█' * int(abs(steering) * 20)}")
            print(f"  Brake:    {brake:6.3f} {'█' * int(brake * 20)}")
            print()
            
            # Display raw input state
            info = input_manager.get_input_info()
            print("RAW INPUT STATE:")
            print(f"  Accelerate:   {info['raw_accelerate']:6.3f}")
            print(f"  Brake:        {info['raw_brake']:6.3f}")
            print(f"  Steer Left:   {info['raw_steer_left']:6.3f}")
            print(f"  Steer Right:  {info['raw_steer_right']:6.3f}")
            print(f"  Reverse:      {info['raw_reverse']:6.3f}")
            print()
            
            # Display digital inputs
            print("DIGITAL INPUTS:")
            print(f"  Pause:         {'YES' if info['pause'] else 'NO'}")
            print(f"  Reset:         {'YES' if info['reset'] else 'NO'}")
            print(f"  Switch Physics:{'YES' if info['switch_physics'] else 'NO'}")
            print()
            
            # Display currently pressed keys
            if info['pressed_keys']:
                key_names = [ControlsHelper.get_key_name(key) for key in info['pressed_keys']]
                print(f"PRESSED KEYS: {', '.join(key_names)}")
            else:
                print("PRESSED KEYS: None")
            print()
            
            # Display configuration
            print("INPUT CONFIGURATION:")
            print(f"  Acceleration Smoothing: {info['acceleration_smoothing']}")
            print(f"  Steering Smoothing:     {info['steering_smoothing']}")
            print(f"  Brake Smoothing:        {info['brake_smoothing']}")
            print(f"  Input Deadzone:         {info['deadzone']}")
            print()
            
            print("Controls: WASD/Arrow Keys to drive, Shift for reverse, Space for brake")
            print("System: P=Pause, R=Reset, Tab=Switch Physics, ESC=Quit")
            
            last_info_time = current_time
        
        # Fill screen with black (required for pygame)
        screen.fill((0, 0, 0))
        pygame.display.flip()
    
    # Cleanup
    pygame.quit()
    print("\nDemo finished!")


def test_control_schemes():
    """Test different control schemes."""
    print("\nTesting Control Schemes:")
    print("=" * 40)
    
    schemes = ControlSchemes.get_all_schemes()
    
    for scheme in schemes:
        print(f"\n{scheme.name} Scheme:")
        print(f"Description: {scheme.description}")
        
        # Show key mappings for movement
        movement_actions = [
            InputAction.ACCELERATE,
            InputAction.BRAKE,
            InputAction.STEER_LEFT,
            InputAction.STEER_RIGHT,
            InputAction.REVERSE
        ]
        
        for action in movement_actions:
            keys = [key for key, mapped_action in scheme.key_mappings.items() 
                   if mapped_action == action]
            if keys:
                key_names = [ControlsHelper.get_key_name(key) for key in keys]
                action_desc = ControlsHelper.get_action_description(action)
                print(f"  {action_desc}: {', '.join(key_names)}")
        
        # Show input settings
        config = scheme.input_config
        print(f"  Settings: Accel={config.acceleration_smoothing}, "
              f"Steer={config.steering_smoothing}, "
              f"Brake={config.brake_smoothing}")


def test_input_manager_basic():
    """Test basic InputManager functionality without pygame display."""
    print("\nTesting InputManager Basic Functionality:")
    print("=" * 50)
    
    # Initialize pygame for key constants
    pygame.init()
    
    # Create input manager
    input_manager = InputManager()
    
    print("✓ InputManager created successfully")
    
    # Test getting car controls with no input
    throttle, steering, brake = input_manager.get_car_controls()
    print(f"✓ Initial controls: throttle={throttle}, steering={steering}, brake={brake}")
    
    # Test input info
    info = input_manager.get_input_info()
    print(f"✓ Input info contains {len(info)} fields")
    
    # Test action callbacks
    callback_triggered = False
    
    def test_callback():
        nonlocal callback_triggered
        callback_triggered = True
    
    input_manager.set_action_callback(InputAction.PAUSE, test_callback)
    print("✓ Action callback set successfully")
    
    # Test reset
    input_manager.reset_input_state()
    print("✓ Input state reset successfully")
    
    pygame.quit()
    print("✓ All basic tests passed!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run tests without GUI
        test_input_manager_basic()
        test_control_schemes()
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