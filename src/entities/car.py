"""
Car entity implementation integrating physics, rendering, and game logic.

This module provides the Car class that combines the physics simulation from CarBody
with rendering capabilities and game state management for the retro racing game.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, Callable
import pygame
import pymunk
import math

from src.physics.car_physics import CarBody, CarPhysicsConfig, CarPhysicsPresets
from src.rendering.black_mamba_renderer import BlackMambaRenderer


@dataclass
class CarState:
    """Car game state information."""
    
    # Identity
    car_id: str
    is_player: bool = False
    
    # Race state
    current_lap: int = 0
    lap_time: float = 0.0
    best_lap_time: Optional[float] = None
    position_in_race: int = 1
    
    # Performance metrics
    top_speed: float = 0.0
    distance_traveled: float = 0.0
    
    # Status flags
    is_finished: bool = False
    is_crashed: bool = False
    respawn_timer: float = 0.0


class Car:
    """
    Main car entity integrating physics body with game logic.
    
    Combines CarBody physics simulation with rendering, state management,
    and game-specific functionality like lap tracking and collision handling.
    """
    
    def __init__(self,
                 car_id: str,
                 physics_space: pymunk.Space,
                 position: Tuple[float, float] = (0, 0),
                 angle: float = 0.0,
                 is_player: bool = False,
                 physics_config: Optional[CarPhysicsConfig] = None,
                 car_color: Optional[Tuple[int, int, int]] = None):
        """
        Initialize car entity.
        
        Args:
            car_id: Unique identifier for this car
            physics_space: Pymunk space for physics simulation
            position: Initial position (x, y)
            angle: Initial angle in radians
            is_player: Whether this is the player's car
            physics_config: Physics configuration (uses arcade preset if None)
            car_color: RGB color for rendering (auto-assigned if None)
        """
        # Initialize car state
        self.state = CarState(car_id=car_id, is_player=is_player)
        
        # Initialize physics body
        config = physics_config or CarPhysicsPresets.arcade()
        self.physics_body = CarBody(physics_space, position, angle, config)
        
        # Set up collision callback
        self.physics_body.set_collision_callback(self._handle_collision)
        
        # Rendering properties
        self.car_color = car_color or self._get_default_color()
        self._last_render_position = position
        self._last_render_angle = angle
        
        # Control inputs (for player cars or AI)
        self.throttle_input: float = 0.0
        self.steering_input: float = 0.0
        self.brake_input: float = 0.0
        
        # Collision handling
        self.collision_callback: Optional[Callable] = None
        self.crash_threshold: float = 300.0  # Impact force threshold for crashes
        
        # Performance tracking
        self._last_position = pymunk.Vec2d(*position)
        self._frame_count = 0
    
    def _get_default_color(self) -> Tuple[int, int, int]:
        """Get default color based on car type."""
        if self.state.is_player:
            return (220, 50, 50)  # Red for player
        else:
            # Cycle through gray tones for AI cars
            colors = [
                (120, 120, 120),  # Light gray
                (80, 80, 80),     # Medium gray
                (60, 60, 60),     # Dark gray
            ]
            # Use car_id hash to pick consistent color
            color_index = hash(self.state.car_id) % len(colors)
            return colors[color_index]
    
    def _handle_collision(self, collision_info: Dict[str, Any]) -> None:
        """
        Handle collision events from physics system.
        
        Args:
            collision_info: Collision information from CarBody
        """
        # Calculate impact force magnitude
        impulse = collision_info.get('impulse', pymunk.Vec2d(0, 0))
        impact_force = impulse.length
        
        # Check for crash conditions
        if impact_force > self.crash_threshold:
            self.state.is_crashed = True
            self.state.respawn_timer = 2.0  # 2 second respawn delay
        
        # Call external collision callback if set
        if self.collision_callback:
            self.collision_callback(self, collision_info)
    
    def set_collision_callback(self, callback: Callable[['Car', Dict[str, Any]], None]) -> None:
        """
        Set callback for collision events.
        
        Args:
            callback: Function to call on collision with (car, collision_info)
        """
        self.collision_callback = callback
    
    def apply_controls(self, throttle: float, steering: float, brake: float) -> None:
        """
        Apply control inputs to the car.
        
        Args:
            throttle: Throttle input (-1.0 to 1.0, reverse to forward)
            steering: Steering input (-1.0 to 1.0, left to right)
            brake: Brake input (0.0 to 1.0, no brake to full brake)
        """
        # Clamp inputs to valid ranges
        self.throttle_input = max(-1.0, min(1.0, throttle))
        self.steering_input = max(-1.0, min(1.0, steering))
        self.brake_input = max(0.0, min(1.0, brake))
        
        # Apply to physics body
        self.physics_body.apply_controls(self.throttle_input, self.steering_input, self.brake_input)
    
    def update(self, dt: float) -> None:
        """
        Update car state and physics.
        
        Args:
            dt: Delta time in seconds
        """
        # Handle respawn timer
        if self.state.is_crashed and self.state.respawn_timer > 0:
            self.state.respawn_timer -= dt
            if self.state.respawn_timer <= 0:
                self.state.is_crashed = False
                self.state.respawn_timer = 0.0  # Ensure it doesn't go negative
                # Reset velocity but keep position
                self.physics_body.body.velocity = (0, 0)
                self.physics_body.body.angular_velocity = 0
        
        # Update physics if not crashed
        if not self.state.is_crashed:
            self.physics_body.update_physics(dt)
        
        # Update performance metrics
        self._update_performance_metrics(dt)
        
        # Update lap timing
        self.state.lap_time += dt
        
        self._frame_count += 1
    
    def _update_performance_metrics(self, dt: float) -> None:
        """Update performance tracking metrics."""
        current_position = pymunk.Vec2d(*self.get_position())
        
        # Update distance traveled
        distance_delta = current_position.get_distance(self._last_position)
        self.state.distance_traveled += distance_delta
        self._last_position = current_position
        
        # Update top speed
        current_speed = self.get_speed()
        if current_speed > self.state.top_speed:
            self.state.top_speed = current_speed
    
    def render(self, renderer: BlackMambaRenderer) -> None:
        """
        Render the car using the Black Mamba renderer.
        
        Args:
            renderer: BlackMambaRenderer instance
        """
        if self.state.is_crashed:
            # Render crashed car with different visual (darker, maybe spinning)
            crash_color = tuple(max(0, c - 50) for c in self.car_color)
            renderer.draw_car(self.get_position(), self.get_angle_degrees(), crash_color)
        else:
            # Normal rendering
            renderer.draw_car(self.get_position(), self.get_angle_degrees(), self.car_color)
        
        # Update render tracking
        self._last_render_position = self.get_position()
        self._last_render_angle = self.get_angle_degrees()
    
    def get_position(self) -> Tuple[float, float]:
        """Get current car position."""
        return tuple(self.physics_body.body.position)
    
    def get_angle_radians(self) -> float:
        """Get current car angle in radians."""
        return self.physics_body.body.angle
    
    def get_angle_degrees(self) -> float:
        """Get current car angle in degrees."""
        return math.degrees(self.physics_body.body.angle)
    
    def get_velocity(self) -> Tuple[float, float]:
        """Get current velocity vector."""
        return tuple(self.physics_body.body.velocity)
    
    def get_speed(self) -> float:
        """Get current speed in pixels per second."""
        return self.physics_body.get_speed()
    
    def get_forward_speed(self) -> float:
        """Get speed in the forward direction."""
        return self.physics_body.get_forward_speed()
    
    def get_lateral_speed(self) -> float:
        """Get lateral (sideways) speed."""
        return self.physics_body.get_lateral_speed()
    
    def is_sliding(self, threshold: float = 50.0) -> bool:
        """Check if the car is sliding."""
        return self.physics_body.is_sliding(threshold)
    
    def reset_position(self, position: Tuple[float, float], angle: float = 0.0) -> None:
        """
        Reset car to a new position and clear state.
        
        Args:
            position: New position (x, y)
            angle: New angle in radians
        """
        self.physics_body.reset_position(position, angle)
        
        # Reset state
        self.state.is_crashed = False
        self.state.respawn_timer = 0.0
        self._last_position = pymunk.Vec2d(*position)
    
    def complete_lap(self, lap_time: float) -> None:
        """
        Mark a lap as completed and update lap timing.
        
        Args:
            lap_time: Time taken for this lap
        """
        self.state.current_lap += 1
        
        # Update best lap time
        if self.state.best_lap_time is None or lap_time < self.state.best_lap_time:
            self.state.best_lap_time = lap_time
        
        # Reset lap timer
        self.state.lap_time = 0.0
    
    def finish_race(self, final_position: int) -> None:
        """
        Mark the race as finished for this car.
        
        Args:
            final_position: Final position in the race
        """
        self.state.is_finished = True
        self.state.position_in_race = final_position
    
    def switch_physics_model(self, model: str) -> None:
        """
        Switch between arcade and realistic physics models.
        
        Args:
            model: Physics model ('arcade' or 'realistic')
        """
        if model == 'arcade':
            config = CarPhysicsPresets.arcade()
        elif model == 'realistic':
            config = CarPhysicsPresets.realistic()
        else:
            raise ValueError(f"Invalid physics model: {model}")
        
        self.physics_body.switch_physics_config(config)
    
    def get_car_info(self) -> Dict[str, Any]:
        """
        Get comprehensive car information for debugging and UI.
        
        Returns:
            Dictionary with car state and physics information
        """
        physics_info = self.physics_body.get_physics_info()
        
        return {
            # Car identity and state
            'car_id': self.state.car_id,
            'is_player': self.state.is_player,
            'is_crashed': self.state.is_crashed,
            'is_finished': self.state.is_finished,
            
            # Race information
            'current_lap': self.state.current_lap,
            'lap_time': self.state.lap_time,
            'best_lap_time': self.state.best_lap_time,
            'position_in_race': self.state.position_in_race,
            
            # Performance metrics
            'top_speed': self.state.top_speed,
            'distance_traveled': self.state.distance_traveled,
            
            # Current physics state
            'position': physics_info['position'],
            'angle_degrees': math.degrees(physics_info['angle']),
            'speed': physics_info['speed'],
            'forward_speed': physics_info['forward_speed'],
            'lateral_speed': physics_info['lateral_speed'],
            'is_sliding': physics_info['is_sliding'],
            
            # Control inputs
            'throttle': self.throttle_input,
            'steering': self.steering_input,
            'brake': self.brake_input,
            
            # Physics configuration
            'physics_model': 'arcade' if physics_info['friction'] > 0.8 else 'realistic',
            'mass': physics_info['mass']
        }
    
    def cleanup(self) -> None:
        """Clean up car resources."""
        self.physics_body.cleanup()