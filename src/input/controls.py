"""
Control scheme definitions and presets for the retro racing game.

This module provides predefined control schemes and utilities for
managing different input configurations.
"""

from dataclasses import dataclass
from typing import Dict, List
import pygame
from .input_manager import InputAction, InputConfig


@dataclass
class ControlScheme:
    """A named control scheme with key mappings and settings."""
    name: str
    description: str
    key_mappings: Dict[int, InputAction]
    input_config: InputConfig


class ControlSchemes:
    """Predefined control schemes for different player preferences."""
    
    @staticmethod
    def wasd_scheme() -> ControlScheme:
        """WASD control scheme (default)."""
        key_mappings = {
            # WASD controls
            pygame.K_w: InputAction.ACCELERATE,
            pygame.K_s: InputAction.BRAKE,
            pygame.K_a: InputAction.STEER_LEFT,
            pygame.K_d: InputAction.STEER_RIGHT,
            
            # Additional controls
            pygame.K_LSHIFT: InputAction.REVERSE,
            pygame.K_SPACE: InputAction.BRAKE,  # Alternative brake
            
            # System controls
            pygame.K_p: InputAction.PAUSE,
            pygame.K_r: InputAction.RESET,
            pygame.K_TAB: InputAction.SWITCH_PHYSICS,
        }
        
        config = InputConfig(
            key_mappings=key_mappings,
            acceleration_smoothing=0.1,
            steering_smoothing=0.05,
            brake_smoothing=0.05,
            acceleration_decay=0.2,
            steering_decay=0.15,
            brake_decay=0.3,
            input_deadzone=0.05
        )
        
        return ControlScheme(
            name="WASD",
            description="WASD keys for movement, Shift for reverse, Space for brake",
            key_mappings=key_mappings,
            input_config=config
        )
    
    @staticmethod
    def arrow_keys_scheme() -> ControlScheme:
        """Arrow keys control scheme."""
        key_mappings = {
            # Arrow key controls
            pygame.K_UP: InputAction.ACCELERATE,
            pygame.K_DOWN: InputAction.BRAKE,
            pygame.K_LEFT: InputAction.STEER_LEFT,
            pygame.K_RIGHT: InputAction.STEER_RIGHT,
            
            # Additional controls
            pygame.K_RSHIFT: InputAction.REVERSE,
            pygame.K_RCTRL: InputAction.BRAKE,  # Alternative brake
            
            # System controls
            pygame.K_p: InputAction.PAUSE,
            pygame.K_r: InputAction.RESET,
            pygame.K_TAB: InputAction.SWITCH_PHYSICS,
        }
        
        config = InputConfig(
            key_mappings=key_mappings,
            acceleration_smoothing=0.1,
            steering_smoothing=0.05,
            brake_smoothing=0.05,
            acceleration_decay=0.2,
            steering_decay=0.15,
            brake_decay=0.3,
            input_deadzone=0.05
        )
        
        return ControlScheme(
            name="Arrow Keys",
            description="Arrow keys for movement, Right Shift for reverse, Right Ctrl for brake",
            key_mappings=key_mappings,
            input_config=config
        )
    
    @staticmethod
    def combined_scheme() -> ControlScheme:
        """Combined WASD + Arrow keys scheme (default)."""
        key_mappings = {
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
        
        config = InputConfig(
            key_mappings=key_mappings,
            acceleration_smoothing=0.1,
            steering_smoothing=0.05,
            brake_smoothing=0.05,
            acceleration_decay=0.2,
            steering_decay=0.15,
            brake_decay=0.3,
            input_deadzone=0.05
        )
        
        return ControlScheme(
            name="Combined",
            description="Both WASD and Arrow keys supported",
            key_mappings=key_mappings,
            input_config=config
        )
    
    @staticmethod
    def arcade_scheme() -> ControlScheme:
        """Arcade-style control scheme with faster response."""
        key_mappings = {
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
            pygame.K_SPACE: InputAction.BRAKE,
            
            # System controls
            pygame.K_p: InputAction.PAUSE,
            pygame.K_r: InputAction.RESET,
            pygame.K_TAB: InputAction.SWITCH_PHYSICS,
        }
        
        # Faster, more responsive settings for arcade feel
        config = InputConfig(
            key_mappings=key_mappings,
            acceleration_smoothing=0.2,    # Faster acceleration buildup
            steering_smoothing=0.15,       # Much faster steering
            brake_smoothing=0.2,           # Faster braking
            acceleration_decay=0.3,        # Faster decay
            steering_decay=0.25,           # Faster steering decay
            brake_decay=0.4,               # Faster brake decay
            input_deadzone=0.02            # Smaller deadzone
        )
        
        return ControlScheme(
            name="Arcade",
            description="Fast, responsive controls for arcade-style gameplay",
            key_mappings=key_mappings,
            input_config=config
        )
    
    @staticmethod
    def realistic_scheme() -> ControlScheme:
        """Realistic control scheme with slower, more gradual response."""
        key_mappings = {
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
            pygame.K_SPACE: InputAction.BRAKE,
            
            # System controls
            pygame.K_p: InputAction.PAUSE,
            pygame.K_r: InputAction.RESET,
            pygame.K_TAB: InputAction.SWITCH_PHYSICS,
        }
        
        # Slower, more gradual settings for realistic feel
        config = InputConfig(
            key_mappings=key_mappings,
            acceleration_smoothing=0.05,   # Slower acceleration buildup
            steering_smoothing=0.03,       # Slower steering
            brake_smoothing=0.03,          # Slower braking
            acceleration_decay=0.1,        # Slower decay
            steering_decay=0.08,           # Slower steering decay
            brake_decay=0.15,              # Slower brake decay
            input_deadzone=0.08            # Larger deadzone
        )
        
        return ControlScheme(
            name="Realistic",
            description="Gradual, realistic controls for simulation-style gameplay",
            key_mappings=key_mappings,
            input_config=config
        )
    
    @staticmethod
    def get_all_schemes() -> List[ControlScheme]:
        """Get all available control schemes."""
        return [
            ControlSchemes.combined_scheme(),      # Default
            ControlSchemes.wasd_scheme(),
            ControlSchemes.arrow_keys_scheme(),
            ControlSchemes.arcade_scheme(),
            ControlSchemes.realistic_scheme(),
        ]
    
    @staticmethod
    def get_scheme_by_name(name: str) -> ControlScheme:
        """
        Get a control scheme by name.
        
        Args:
            name: Name of the control scheme
            
        Returns:
            ControlScheme instance
            
        Raises:
            ValueError: If scheme name is not found
        """
        schemes = {scheme.name: scheme for scheme in ControlSchemes.get_all_schemes()}
        
        if name not in schemes:
            available = ", ".join(schemes.keys())
            raise ValueError(f"Control scheme '{name}' not found. Available: {available}")
        
        return schemes[name]


class ControlsHelper:
    """Helper utilities for working with controls."""
    
    @staticmethod
    def get_key_name(key_code: int) -> str:
        """
        Get human-readable name for a pygame key code.
        
        Args:
            key_code: Pygame key constant
            
        Returns:
            Human-readable key name
        """
        try:
            return pygame.key.name(key_code).upper()
        except:
            return f"KEY_{key_code}"
    
    @staticmethod
    def get_action_description(action: InputAction) -> str:
        """
        Get human-readable description for an input action.
        
        Args:
            action: Input action
            
        Returns:
            Human-readable action description
        """
        descriptions = {
            InputAction.ACCELERATE: "Accelerate Forward",
            InputAction.BRAKE: "Brake",
            InputAction.STEER_LEFT: "Steer Left",
            InputAction.STEER_RIGHT: "Steer Right",
            InputAction.REVERSE: "Reverse",
            InputAction.PAUSE: "Pause Game",
            InputAction.RESET: "Reset Car",
            InputAction.SWITCH_PHYSICS: "Switch Physics Model",
        }
        return descriptions.get(action, action.value.title())
    
    @staticmethod
    def format_control_scheme(scheme: ControlScheme) -> str:
        """
        Format a control scheme for display.
        
        Args:
            scheme: Control scheme to format
            
        Returns:
            Formatted string representation
        """
        lines = [
            f"Control Scheme: {scheme.name}",
            f"Description: {scheme.description}",
            "",
            "Key Mappings:"
        ]
        
        # Group mappings by action
        action_keys = {}
        for key, action in scheme.key_mappings.items():
            if action not in action_keys:
                action_keys[action] = []
            action_keys[action].append(key)
        
        # Format each action
        for action in InputAction:
            if action in action_keys:
                keys = action_keys[action]
                key_names = [ControlsHelper.get_key_name(key) for key in keys]
                action_desc = ControlsHelper.get_action_description(action)
                lines.append(f"  {action_desc}: {', '.join(key_names)}")
        
        return "\n".join(lines)