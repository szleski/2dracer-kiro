"""
Tests for the input management system.

Tests InputManager, InputConfig, and control schemes functionality.
"""

import unittest
from unittest.mock import Mock, patch
import pygame
from src.input.input_manager import InputManager, InputAction, InputState, InputConfig
from src.input.controls import ControlSchemes, ControlsHelper


class TestInputState(unittest.TestCase):
    """Test InputState functionality."""
    
    def test_input_state_initialization(self):
        """Test InputState initializes with correct defaults."""
        state = InputState()
        
        self.assertEqual(state.accelerate, 0.0)
        self.assertEqual(state.brake, 0.0)
        self.assertEqual(state.steer_left, 0.0)
        self.assertEqual(state.steer_right, 0.0)
        self.assertEqual(state.reverse, 0.0)
        self.assertFalse(state.pause)
        self.assertFalse(state.reset)
        self.assertFalse(state.switch_physics)
    
    def test_get_throttle(self):
        """Test throttle calculation from accelerate and reverse."""
        state = InputState()
        
        # Test forward acceleration
        state.accelerate = 0.8
        self.assertEqual(state.get_throttle(), 0.8)
        
        # Test reverse takes priority
        state.reverse = 0.6
        self.assertEqual(state.get_throttle(), -0.6)
        
        # Test no input
        state.accelerate = 0.0
        state.reverse = 0.0
        self.assertEqual(state.get_throttle(), 0.0)
    
    def test_get_steering(self):
        """Test steering calculation from left and right inputs."""
        state = InputState()
        
        # Test right steering
        state.steer_right = 0.7
        self.assertEqual(state.get_steering(), 0.7)
        
        # Test left steering
        state.steer_left = 0.5
        state.steer_right = 0.0
        self.assertEqual(state.get_steering(), -0.5)
        
        # Test combined steering (should cancel out partially)
        state.steer_left = 0.3
        state.steer_right = 0.8
        self.assertEqual(state.get_steering(), 0.5)  # 0.8 - 0.3
    
    def test_get_brake(self):
        """Test brake input passthrough."""
        state = InputState()
        
        state.brake = 0.6
        self.assertEqual(state.get_brake(), 0.6)


class TestInputConfig(unittest.TestCase):
    """Test InputConfig functionality."""
    
    def test_default_initialization(self):
        """Test InputConfig initializes with default key mappings."""
        config = InputConfig()
        
        # Check that default key mappings are created
        self.assertIsNotNone(config.key_mappings)
        self.assertIn(pygame.K_w, config.key_mappings)
        self.assertEqual(config.key_mappings[pygame.K_w], InputAction.ACCELERATE)
        
        # Check default smoothing values
        self.assertEqual(config.acceleration_smoothing, 0.1)
        self.assertEqual(config.steering_smoothing, 0.05)
        self.assertEqual(config.brake_smoothing, 0.05)
    
    def test_custom_key_mappings(self):
        """Test InputConfig with custom key mappings."""
        custom_mappings = {
            pygame.K_SPACE: InputAction.ACCELERATE,
            pygame.K_x: InputAction.BRAKE,
        }
        
        config = InputConfig(key_mappings=custom_mappings)
        
        self.assertEqual(config.key_mappings, custom_mappings)
        self.assertNotIn(pygame.K_w, config.key_mappings)


class TestInputManager(unittest.TestCase):
    """Test InputManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.input_manager = InputManager()
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_initialization(self):
        """Test InputManager initializes correctly."""
        self.assertIsInstance(self.input_manager.input_state, InputState)
        self.assertIsInstance(self.input_manager.config, InputConfig)
        self.assertEqual(len(self.input_manager.pressed_keys), 0)
        self.assertEqual(len(self.input_manager.just_pressed_keys), 0)
        self.assertEqual(len(self.input_manager.just_released_keys), 0)
    
    @patch('pygame.key.get_pressed')
    def test_update_with_no_input(self, mock_get_pressed):
        """Test update with no keys pressed."""
        # Mock no keys pressed
        mock_keys = [False] * 512  # Pygame has up to 512 key codes
        mock_get_pressed.return_value = mock_keys
        
        self.input_manager.update(0.016)  # 60 FPS delta time
        
        throttle, steering, brake = self.input_manager.get_car_controls()
        self.assertEqual(throttle, 0.0)
        self.assertEqual(steering, 0.0)
        self.assertEqual(brake, 0.0)
    
    @patch('pygame.key.get_pressed')
    def test_update_with_acceleration(self, mock_get_pressed):
        """Test update with acceleration key pressed."""
        # Mock W key pressed
        mock_keys = [False] * 512
        mock_keys[pygame.K_w] = True
        mock_get_pressed.return_value = mock_keys
        
        # Update multiple times to build up input
        for _ in range(10):
            self.input_manager.update(0.016)
        
        throttle, steering, brake = self.input_manager.get_car_controls()
        self.assertGreater(throttle, 0.0)
        self.assertEqual(steering, 0.0)
        self.assertEqual(brake, 0.0)
    
    @patch('pygame.key.get_pressed')
    def test_update_with_steering(self, mock_get_pressed):
        """Test update with steering keys pressed."""
        # Mock A key pressed (steer left)
        mock_keys = [False] * 512
        mock_keys[pygame.K_a] = True
        mock_get_pressed.return_value = mock_keys
        
        # Update multiple times to build up input
        for _ in range(10):
            self.input_manager.update(0.016)
        
        throttle, steering, brake = self.input_manager.get_car_controls()
        self.assertEqual(throttle, 0.0)
        self.assertLess(steering, 0.0)  # Left steering is negative
        self.assertEqual(brake, 0.0)
    
    @patch('pygame.key.get_pressed')
    def test_input_smoothing(self, mock_get_pressed):
        """Test that input smoothing works correctly."""
        # Mock W key pressed
        mock_keys = [False] * 512
        mock_keys[pygame.K_w] = True
        mock_get_pressed.return_value = mock_keys
        
        # First update should have small throttle
        self.input_manager.update(0.016)
        throttle1, _, _ = self.input_manager.get_car_controls()
        
        # Second update should have higher throttle
        self.input_manager.update(0.016)
        throttle2, _, _ = self.input_manager.get_car_controls()
        
        self.assertGreater(throttle2, throttle1)
        self.assertLess(throttle1, 1.0)  # Should not reach max immediately
    
    @patch('pygame.key.get_pressed')
    def test_input_decay(self, mock_get_pressed):
        """Test that input decays when keys are released."""
        # First, build up some input
        mock_keys = [False] * 512
        mock_keys[pygame.K_w] = True
        mock_get_pressed.return_value = mock_keys
        
        for _ in range(10):
            self.input_manager.update(0.016)
        
        throttle_with_input, _, _ = self.input_manager.get_car_controls()
        self.assertGreater(throttle_with_input, 0.5)
        
        # Now release the key
        mock_keys[pygame.K_w] = False
        mock_get_pressed.return_value = mock_keys
        
        # Update and check that input decays
        self.input_manager.update(0.016)
        throttle_after_release, _, _ = self.input_manager.get_car_controls()
        
        self.assertLess(throttle_after_release, throttle_with_input)
    
    def test_action_callbacks(self):
        """Test that action callbacks are triggered correctly."""
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        self.input_manager.set_action_callback(InputAction.PAUSE, test_callback)
        
        # Simulate P key press
        with patch('pygame.key.get_pressed') as mock_get_pressed:
            mock_keys = [False] * 512
            mock_keys[pygame.K_p] = True
            mock_get_pressed.return_value = mock_keys
            
            self.input_manager.update(0.016)
        
        self.assertTrue(callback_called)
    
    def test_get_input_info(self):
        """Test that input info is returned correctly."""
        info = self.input_manager.get_input_info()
        
        self.assertIn('throttle', info)
        self.assertIn('steering', info)
        self.assertIn('brake', info)
        self.assertIn('raw_accelerate', info)
        self.assertIn('pressed_keys', info)
        self.assertIn('deadzone', info)
    
    def test_reset_input_state(self):
        """Test that input state resets correctly."""
        # Build up some input first
        with patch('pygame.key.get_pressed') as mock_get_pressed:
            mock_keys = [False] * 512
            mock_keys[pygame.K_w] = True
            mock_get_pressed.return_value = mock_keys
            
            for _ in range(5):
                self.input_manager.update(0.016)
        
        # Verify input exists
        throttle_before, _, _ = self.input_manager.get_car_controls()
        self.assertGreater(throttle_before, 0.0)
        
        # Reset and verify
        self.input_manager.reset_input_state()
        throttle_after, steering_after, brake_after = self.input_manager.get_car_controls()
        
        self.assertEqual(throttle_after, 0.0)
        self.assertEqual(steering_after, 0.0)
        self.assertEqual(brake_after, 0.0)


class TestControlSchemes(unittest.TestCase):
    """Test control scheme functionality."""
    
    def test_wasd_scheme(self):
        """Test WASD control scheme."""
        scheme = ControlSchemes.wasd_scheme()
        
        self.assertEqual(scheme.name, "WASD")
        self.assertIn(pygame.K_w, scheme.key_mappings)
        self.assertEqual(scheme.key_mappings[pygame.K_w], InputAction.ACCELERATE)
        self.assertNotIn(pygame.K_UP, scheme.key_mappings)  # Should not have arrow keys
    
    def test_arrow_keys_scheme(self):
        """Test arrow keys control scheme."""
        scheme = ControlSchemes.arrow_keys_scheme()
        
        self.assertEqual(scheme.name, "Arrow Keys")
        self.assertIn(pygame.K_UP, scheme.key_mappings)
        self.assertEqual(scheme.key_mappings[pygame.K_UP], InputAction.ACCELERATE)
        self.assertNotIn(pygame.K_w, scheme.key_mappings)  # Should not have WASD
    
    def test_combined_scheme(self):
        """Test combined control scheme."""
        scheme = ControlSchemes.combined_scheme()
        
        self.assertEqual(scheme.name, "Combined")
        self.assertIn(pygame.K_w, scheme.key_mappings)
        self.assertIn(pygame.K_UP, scheme.key_mappings)
        self.assertEqual(scheme.key_mappings[pygame.K_w], InputAction.ACCELERATE)
        self.assertEqual(scheme.key_mappings[pygame.K_UP], InputAction.ACCELERATE)
    
    def test_arcade_scheme_settings(self):
        """Test arcade scheme has faster settings."""
        arcade = ControlSchemes.arcade_scheme()
        combined = ControlSchemes.combined_scheme()
        
        # Arcade should have faster smoothing
        self.assertGreater(arcade.input_config.acceleration_smoothing, 
                          combined.input_config.acceleration_smoothing)
        self.assertGreater(arcade.input_config.steering_smoothing, 
                          combined.input_config.steering_smoothing)
    
    def test_realistic_scheme_settings(self):
        """Test realistic scheme has slower settings."""
        realistic = ControlSchemes.realistic_scheme()
        combined = ControlSchemes.combined_scheme()
        
        # Realistic should have slower smoothing
        self.assertLess(realistic.input_config.acceleration_smoothing, 
                       combined.input_config.acceleration_smoothing)
        self.assertLess(realistic.input_config.steering_smoothing, 
                       combined.input_config.steering_smoothing)
    
    def test_get_all_schemes(self):
        """Test getting all control schemes."""
        schemes = ControlSchemes.get_all_schemes()
        
        self.assertGreater(len(schemes), 0)
        scheme_names = [scheme.name for scheme in schemes]
        self.assertIn("Combined", scheme_names)
        self.assertIn("WASD", scheme_names)
        self.assertIn("Arrow Keys", scheme_names)
        self.assertIn("Arcade", scheme_names)
        self.assertIn("Realistic", scheme_names)
    
    def test_get_scheme_by_name(self):
        """Test getting scheme by name."""
        scheme = ControlSchemes.get_scheme_by_name("WASD")
        self.assertEqual(scheme.name, "WASD")
        
        # Test invalid name
        with self.assertRaises(ValueError):
            ControlSchemes.get_scheme_by_name("NonExistent")


class TestControlsHelper(unittest.TestCase):
    """Test ControlsHelper functionality."""
    
    def test_get_key_name(self):
        """Test getting human-readable key names."""
        # Test common keys
        self.assertEqual(ControlsHelper.get_key_name(pygame.K_w), "W")
        self.assertEqual(ControlsHelper.get_key_name(pygame.K_SPACE), "SPACE")
        self.assertEqual(ControlsHelper.get_key_name(pygame.K_UP), "UP")
    
    def test_get_action_description(self):
        """Test getting action descriptions."""
        self.assertEqual(ControlsHelper.get_action_description(InputAction.ACCELERATE), 
                        "Accelerate Forward")
        self.assertEqual(ControlsHelper.get_action_description(InputAction.BRAKE), 
                        "Brake")
        self.assertEqual(ControlsHelper.get_action_description(InputAction.STEER_LEFT), 
                        "Steer Left")
    
    def test_format_control_scheme(self):
        """Test formatting control scheme for display."""
        scheme = ControlSchemes.wasd_scheme()
        formatted = ControlsHelper.format_control_scheme(scheme)
        
        self.assertIn("Control Scheme: WASD", formatted)
        self.assertIn("Accelerate Forward: W", formatted)
        self.assertIn("Steer Left: A", formatted)


if __name__ == '__main__':
    unittest.main()