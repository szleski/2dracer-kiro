"""
Input handling system for the retro racing game.

This module provides the InputManager class for handling keyboard input
and mapping it to car controls with smooth input processing.
"""

from dataclasses import dataclass
from typing import Dict, Set, Optional, Callable, Any
import pygame
from enum import Enum


class InputAction(Enum):
    """Enumeration of possible input actions."""
    ACCELERATE = "accelerate"
    BRAKE = "brake"
    STEER_LEFT = "steer_left"
    STEER_RIGHT = "steer_right"
    REVERSE = "reverse"
    PAUSE = "pause"
    RESET = "reset"
    SWITCH_PHYSICS = "switch_physics"


@dataclass
class InputState:
    """Current state of all input actions."""
    accelerate: float = 0.0      # 0.0 to 1.0
    brake: float = 0.0           # 0.0 to 1.0
    steer_left: float = 0.0      # 0.0 to 1.0
    steer_right: float = 0.0     # 0.0 to 1.0
    reverse: float = 0.0         # 0.0 to 1.0
    
    # Digital inputs
    pause: bool = False
    reset: bool = False
    switch_physics: bool = False
    
    def get_throttle(self) -> float:
        """Get combined throttle input (-1.0 to 1.0)."""
        if self.reverse > 0.0:
            return -self.reverse
        return self.accelerate
    
    def get_steering(self) -> float:
        """Get combined steering input (-1.0 to 1.0)."""
        return self.steer_right - self.steer_left
    
    def get_brake(self) -> float:
        """Get brake input (0.0 to 1.0)."""
        return self.brake


@dataclass
class InputConfig:
    """Configuration for input handling."""
    
    # Key mappings (pygame key constants)
    key_mappings: Dict[int, InputAction] = None
    
    # Input smoothing parameters
    acceleration_smoothing: float = 0.1    # How quickly acceleration builds up
    steering_smoothing: float = 0.05       # How quickly steering builds up
    brake_smoothing: float = 0.05          # How quickly braking builds up
    
    # Input decay parameters (how quickly inputs fade when released)
    acceleration_decay: float = 0.2
    steering_decay: float = 0.15
    brake_decay: float = 0.3
    
    # Deadzone for analog-like behavior
    input_deadzone: float = 0.05
    
    def __post_init__(self):
        """Initialize default key mappings if not provided."""
        if self.key_mappings is None:
            self.key_mappings = self._get_default_key_mappings()
    
    def _get_default_key_mappings(self) -> Dict[int, InputAction]:
        """Get default WASD + Arrow key mappings."""
        return {
            # WASD controls
            pygame.K_w: InputAction.ACCELERATE,
            pygame.K_s: InputAction.BRAKE,
            pygame.K_a: InputAction.STEER_LEFT,
            pygame.K_d: InputAction.STEER_RIGHT,
            
            # Arrow key controls
            pygame.K_UP: InputAction.ACCELERATE,
            pygame.K_DOWN: InputAction.BRAKE,
            pygame.K_LEFT: InputAction.STEER_LEFT,
            pygame.K_RIGHT: InputAction.STEER_RIGHT,
            
            # Additional controls
            pygame.K_LSHIFT: InputAction.REVERSE,
            pygame.K_RSHIFT: InputAction.REVERSE,
            pygame.K_SPACE: InputAction.BRAKE,  # Alternative brake
            
            # System controls
            pygame.K_p: InputAction.PAUSE,
            pygame.K_r: InputAction.RESET,
            pygame.K_TAB: InputAction.SWITCH_PHYSICS,
        }


class InputManager:
    """
    Manages keyboard input and converts it to smooth car controls.
    
    Provides smooth input handling with proper force application,
    supporting both digital and analog-like input behavior.
    """
    
    def __init__(self, config: Optional[InputConfig] = None):
        """
        Initialize the input manager.
        
        Args:
            config: Input configuration. Uses default if None.
        """
        self.config = config or InputConfig()
        
        # Current input state
        self.input_state = InputState()
        
        # Raw key states (for immediate digital inputs)
        self.pressed_keys: Set[int] = set()
        self.just_pressed_keys: Set[int] = set()
        self.just_released_keys: Set[int] = set()
        
        # Previous frame key states for edge detection
        self._previous_keys: Set[int] = set()
        
        # Event callbacks
        self.action_callbacks: Dict[InputAction, Callable] = {}
        
        # Input history for debugging
        self.input_history: list = []
        self.max_history_length: int = 60  # 1 second at 60 FPS
    
    def set_action_callback(self, action: InputAction, callback: Callable) -> None:
        """
        Set callback for specific input actions.
        
        Args:
            action: Input action to bind
            callback: Function to call when action is triggered
        """
        self.action_callbacks[action] = callback
    
    def update(self, dt: float) -> None:
        """
        Update input state based on current keyboard state.
        
        Args:
            dt: Delta time in seconds
        """
        # Get current keyboard state
        keys = pygame.key.get_pressed()
        current_keys = set()
        
        # Build current key set
        for key_code in range(len(keys)):
            if keys[key_code]:
                current_keys.add(key_code)
        
        # Detect key press/release events
        self.just_pressed_keys = current_keys - self._previous_keys
        self.just_released_keys = self._previous_keys - current_keys
        self.pressed_keys = current_keys
        
        # Update input state with smoothing
        self._update_analog_inputs(dt)
        self._update_digital_inputs()
        
        # Store previous keys for next frame
        self._previous_keys = current_keys.copy()
        
        # Record input history
        self._record_input_history()
        
        # Trigger action callbacks for just-pressed keys
        self._trigger_action_callbacks()
    
    def _update_analog_inputs(self, dt: float) -> None:
        """Update analog-style inputs with smoothing."""
        # Check which analog actions are currently pressed
        accelerate_pressed = any(key in self.pressed_keys 
                               for key, action in self.config.key_mappings.items() 
                               if action == InputAction.ACCELERATE)
        
        brake_pressed = any(key in self.pressed_keys 
                          for key, action in self.config.key_mappings.items() 
                          if action == InputAction.BRAKE)
        
        steer_left_pressed = any(key in self.pressed_keys 
                               for key, action in self.config.key_mappings.items() 
                               if action == InputAction.STEER_LEFT)
        
        steer_right_pressed = any(key in self.pressed_keys 
                                for key, action in self.config.key_mappings.items() 
                                if action == InputAction.STEER_RIGHT)
        
        reverse_pressed = any(key in self.pressed_keys 
                            for key, action in self.config.key_mappings.items() 
                            if action == InputAction.REVERSE)
        
        # Update acceleration
        if accelerate_pressed:
            self.input_state.accelerate = min(1.0, 
                self.input_state.accelerate + self.config.acceleration_smoothing)
        else:
            self.input_state.accelerate = max(0.0, 
                self.input_state.accelerate - self.config.acceleration_decay * dt)
        
        # Update braking
        if brake_pressed:
            self.input_state.brake = min(1.0, 
                self.input_state.brake + self.config.brake_smoothing)
        else:
            self.input_state.brake = max(0.0, 
                self.input_state.brake - self.config.brake_decay * dt)
        
        # Update steering left
        if steer_left_pressed:
            self.input_state.steer_left = min(1.0, 
                self.input_state.steer_left + self.config.steering_smoothing)
        else:
            self.input_state.steer_left = max(0.0, 
                self.input_state.steer_left - self.config.steering_decay * dt)
        
        # Update steering right
        if steer_right_pressed:
            self.input_state.steer_right = min(1.0, 
                self.input_state.steer_right + self.config.steering_smoothing)
        else:
            self.input_state.steer_right = max(0.0, 
                self.input_state.steer_right - self.config.steering_decay * dt)
        
        # Update reverse
        if reverse_pressed:
            self.input_state.reverse = min(1.0, 
                self.input_state.reverse + self.config.acceleration_smoothing)
        else:
            self.input_state.reverse = max(0.0, 
                self.input_state.reverse - self.config.acceleration_decay * dt)
        
        # Apply deadzone
        self._apply_deadzone()
    
    def _update_digital_inputs(self) -> None:
        """Update digital inputs (triggered on key press)."""
        # Reset digital inputs
        self.input_state.pause = False
        self.input_state.reset = False
        self.input_state.switch_physics = False
        
        # Check for just-pressed digital inputs
        for key in self.just_pressed_keys:
            action = self.config.key_mappings.get(key)
            if action == InputAction.PAUSE:
                self.input_state.pause = True
            elif action == InputAction.RESET:
                self.input_state.reset = True
            elif action == InputAction.SWITCH_PHYSICS:
                self.input_state.switch_physics = True
    
    def _apply_deadzone(self) -> None:
        """Apply deadzone to analog inputs."""
        deadzone = self.config.input_deadzone
        
        if self.input_state.accelerate < deadzone:
            self.input_state.accelerate = 0.0
        
        if self.input_state.brake < deadzone:
            self.input_state.brake = 0.0
        
        if self.input_state.steer_left < deadzone:
            self.input_state.steer_left = 0.0
        
        if self.input_state.steer_right < deadzone:
            self.input_state.steer_right = 0.0
        
        if self.input_state.reverse < deadzone:
            self.input_state.reverse = 0.0
    
    def _record_input_history(self) -> None:
        """Record current input state for debugging."""
        history_entry = {
            'throttle': self.input_state.get_throttle(),
            'steering': self.input_state.get_steering(),
            'brake': self.input_state.get_brake(),
            'raw_accelerate': self.input_state.accelerate,
            'raw_brake': self.input_state.brake,
            'raw_steer_left': self.input_state.steer_left,
            'raw_steer_right': self.input_state.steer_right,
            'raw_reverse': self.input_state.reverse,
        }
        
        self.input_history.append(history_entry)
        
        # Limit history length
        if len(self.input_history) > self.max_history_length:
            self.input_history.pop(0)
    
    def _trigger_action_callbacks(self) -> None:
        """Trigger callbacks for just-pressed actions."""
        for key in self.just_pressed_keys:
            action = self.config.key_mappings.get(key)
            if action and action in self.action_callbacks:
                self.action_callbacks[action]()
    
    def get_car_controls(self) -> tuple[float, float, float]:
        """
        Get current car control inputs.
        
        Returns:
            Tuple of (throttle, steering, brake) values
            - throttle: -1.0 to 1.0 (reverse to forward)
            - steering: -1.0 to 1.0 (left to right)
            - brake: 0.0 to 1.0 (no brake to full brake)
        """
        return (
            self.input_state.get_throttle(),
            self.input_state.get_steering(),
            self.input_state.get_brake()
        )
    
    def is_action_pressed(self, action: InputAction) -> bool:
        """
        Check if an action is currently pressed.
        
        Args:
            action: Action to check
            
        Returns:
            True if action is currently pressed
        """
        for key, mapped_action in self.config.key_mappings.items():
            if mapped_action == action and key in self.pressed_keys:
                return True
        return False
    
    def is_action_just_pressed(self, action: InputAction) -> bool:
        """
        Check if an action was just pressed this frame.
        
        Args:
            action: Action to check
            
        Returns:
            True if action was just pressed
        """
        for key, mapped_action in self.config.key_mappings.items():
            if mapped_action == action and key in self.just_pressed_keys:
                return True
        return False
    
    def is_action_just_released(self, action: InputAction) -> bool:
        """
        Check if an action was just released this frame.
        
        Args:
            action: Action to check
            
        Returns:
            True if action was just released
        """
        for key, mapped_action in self.config.key_mappings.items():
            if mapped_action == action and key in self.just_released_keys:
                return True
        return False
    
    def get_input_info(self) -> Dict[str, Any]:
        """
        Get comprehensive input information for debugging.
        
        Returns:
            Dictionary with current input state and configuration
        """
        return {
            # Current control outputs
            'throttle': self.input_state.get_throttle(),
            'steering': self.input_state.get_steering(),
            'brake': self.input_state.get_brake(),
            
            # Raw analog inputs
            'raw_accelerate': self.input_state.accelerate,
            'raw_brake': self.input_state.brake,
            'raw_steer_left': self.input_state.steer_left,
            'raw_steer_right': self.input_state.steer_right,
            'raw_reverse': self.input_state.reverse,
            
            # Digital inputs
            'pause': self.input_state.pause,
            'reset': self.input_state.reset,
            'switch_physics': self.input_state.switch_physics,
            
            # Key states
            'pressed_keys': list(self.pressed_keys),
            'just_pressed': list(self.just_pressed_keys),
            'just_released': list(self.just_released_keys),
            
            # Configuration
            'deadzone': self.config.input_deadzone,
            'acceleration_smoothing': self.config.acceleration_smoothing,
            'steering_smoothing': self.config.steering_smoothing,
            'brake_smoothing': self.config.brake_smoothing,
        }
    
    def reset_input_state(self) -> None:
        """Reset all input states to default values."""
        self.input_state = InputState()
        self.pressed_keys.clear()
        self.just_pressed_keys.clear()
        self.just_released_keys.clear()
        self._previous_keys.clear()
        self.input_history.clear()
    
    def set_key_mapping(self, key: int, action: InputAction) -> None:
        """
        Set or change a key mapping.
        
        Args:
            key: Pygame key constant
            action: Action to map to the key
        """
        self.config.key_mappings[key] = action
    
    def remove_key_mapping(self, key: int) -> None:
        """
        Remove a key mapping.
        
        Args:
            key: Pygame key constant to remove
        """
        if key in self.config.key_mappings:
            del self.config.key_mappings[key]
    
    def get_key_mappings(self) -> Dict[int, InputAction]:
        """
        Get current key mappings.
        
        Returns:
            Dictionary of key mappings
        """
        return self.config.key_mappings.copy()