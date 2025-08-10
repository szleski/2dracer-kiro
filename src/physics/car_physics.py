"""
Car physics implementation using Pymunk for realistic and arcade car simulation.

This module provides the CarBody class and physics configurations for different
driving experiences in the retro racing game.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Callable, Dict, Any
import pymunk
import math


@dataclass
class CarPhysicsConfig:
    """Configuration for car physics parameters."""
    
    # Basic car properties
    mass: float = 1000.0  # Car mass in kg
    width: float = 40.0   # Car width in pixels
    height: float = 20.0  # Car height in pixels
    
    # Physics model parameters
    friction: float = 0.7  # Tire friction coefficient
    max_force: float = 5000.0  # Maximum driving force
    max_torque: float = 2000.0  # Maximum steering torque
    
    # Damping parameters
    linear_damping: float = 0.1   # Linear velocity damping
    angular_damping: float = 0.1  # Angular velocity damping
    
    # Speed-dependent handling
    high_speed_threshold: float = 200.0  # Speed where handling becomes challenging
    handling_degradation: float = 0.5    # How much handling degrades at high speed
    
    # Collision parameters
    collision_elasticity: float = 0.3  # Bounciness in collisions
    collision_friction: float = 0.8    # Friction during collisions


class CarPhysicsPresets:
    """Predefined physics configurations for different driving experiences."""
    
    @staticmethod
    def arcade() -> CarPhysicsConfig:
        """Arcade physics: responsive, forgiving, fun-focused."""
        return CarPhysicsConfig(
            mass=800.0,  # Lighter for more responsive feel
            friction=0.9,  # High friction for easy control
            max_force=50000.0,  # Much higher force for racing speeds
            max_torque=400000.0,  # Extremely high torque for arcade responsiveness
            linear_damping=0.02,  # Much less damping for higher speeds
            angular_damping=0.005,   # Minimal angular damping for very responsive turning
            high_speed_threshold=400.0,  # Higher threshold for racing speeds
            handling_degradation=0.3,    # Less degradation
            collision_elasticity=0.4,    # More bouncy
            collision_friction=0.9       # High collision friction
        )
    
    @staticmethod
    def realistic() -> CarPhysicsConfig:
        """Realistic physics: authentic car handling simulation."""
        return CarPhysicsConfig(
            mass=1200.0,  # Heavier, more realistic mass
            friction=0.6,  # Lower friction, more sliding
            max_force=35000.0,  # Higher force for realistic acceleration
            max_torque=250000.0,  # High torque for realistic but responsive steering
            linear_damping=0.01,  # Very low damping for momentum
            angular_damping=0.01,  # Very low angular damping for better turning
            high_speed_threshold=300.0,  # Realistic high speed threshold
            handling_degradation=0.7,    # More degradation
            collision_elasticity=0.2,    # Less bouncy
            collision_friction=0.6       # Lower collision friction
        )


class CarBody:
    """
    Car physics body using Pymunk for realistic car simulation.
    
    Handles car physics including acceleration, steering, braking, and collisions
    with support for both arcade and realistic physics models.
    """
    
    def __init__(self, 
                 space: pymunk.Space,
                 position: Tuple[float, float] = (0, 0),
                 angle: float = 0.0,
                 config: Optional[CarPhysicsConfig] = None):
        """
        Initialize car physics body.
        
        Args:
            space: Pymunk space to add the car to
            position: Initial position (x, y)
            angle: Initial angle in radians
            config: Physics configuration. Uses arcade preset if None.
        """
        self.config = config or CarPhysicsPresets.arcade()
        self.space = space
        
        # Create Pymunk body and shape
        # Use reduced moment of inertia for more responsive turning
        moment = pymunk.moment_for_box(self.config.mass, 
                                     (self.config.width, self.config.height)) * 0.1
        self.body = pymunk.Body(self.config.mass, moment)
        self.body.position = position
        self.body.angle = angle
        
        # Create rectangular collision shape
        self.shape = pymunk.Poly.create_box(self.body, 
                                          (self.config.width, self.config.height))
        self.shape.friction = self.config.friction
        self.shape.elasticity = self.config.collision_elasticity
        
        # Set collision type for collision callbacks
        self.shape.collision_type = 1  # Car collision type
        
        # Control inputs
        self.throttle: float = 0.0      # -1.0 to 1.0 (reverse to forward)
        self.steering: float = 0.0      # -1.0 to 1.0 (left to right)
        self.brake: float = 0.0         # 0.0 to 1.0 (no brake to full brake)
        
        # Collision callback
        self.collision_callback: Optional[Callable] = None
        
        # Setup collision handler before adding to space
        self._setup_collision_handler()
        
        # Add to physics space
        self.space.add(self.body, self.shape)
    
    def _setup_collision_handler(self) -> None:
        """Setup collision detection callbacks."""
        def collision_handler(arbiter, space, data):
            """Handle collisions with track boundaries or other cars."""
            # Check if this collision involves our car
            if self.shape not in arbiter.shapes:
                return True
                
            if self.collision_callback:
                # Get collision information
                if len(arbiter.contact_point_set.points) > 0:
                    contact_point = arbiter.contact_point_set.points[0].point_a
                    normal = arbiter.contact_point_set.normal
                    impulse = arbiter.total_impulse
                    
                    collision_info = {
                        'point': contact_point,
                        'normal': normal,
                        'impulse': impulse,
                        'other_shape': arbiter.shapes[1] if arbiter.shapes[0] == self.shape else arbiter.shapes[0]
                    }
                    
                    self.collision_callback(collision_info)
            
            return True  # Process collision normally
        
        # Check if handlers already exist to avoid duplicates
        if not hasattr(self.space, '_car_boundary_handler_added'):
            # Add collision handler for car-to-boundary collisions
            handler = self.space.add_collision_handler(1, 2)  # Car to boundary
            handler.pre_solve = collision_handler
            self.space._car_boundary_handler_added = True
        
        if not hasattr(self.space, '_car_car_handler_added'):
            # Add collision handler for car-to-car collisions
            car_handler = self.space.add_collision_handler(1, 1)  # Car to car
            car_handler.pre_solve = collision_handler
            self.space._car_car_handler_added = True
    
    def set_collision_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Set callback function for collision events.
        
        Args:
            callback: Function to call on collision with collision info dict
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
        self.throttle = max(-1.0, min(1.0, throttle))
        self.steering = max(-1.0, min(1.0, steering))
        self.brake = max(0.0, min(1.0, brake))
    
    def update_physics(self, dt: float) -> None:
        """
        Update car physics based on current control inputs.
        
        Args:
            dt: Delta time in seconds
        """
        # Get current velocity and speed
        velocity = self.body.velocity
        speed = velocity.length
        
        # Calculate speed-dependent handling degradation
        speed_factor = 1.0
        if speed > self.config.high_speed_threshold:
            excess_speed = speed - self.config.high_speed_threshold
            speed_factor = 1.0 - (excess_speed / 200.0) * self.config.handling_degradation
            speed_factor = max(0.1, speed_factor)  # Don't completely lose control
        
        # Apply throttle force
        if abs(self.throttle) > 0.01:
            # Calculate forward direction
            forward = pymunk.Vec2d(math.cos(self.body.angle), math.sin(self.body.angle))
            
            # Apply driving force
            force_magnitude = self.throttle * self.config.max_force
            driving_force = forward * force_magnitude
            
            self.body.apply_force_at_world_point(driving_force, self.body.position)
        
        # Apply steering torque
        if abs(self.steering) > 0.01:
            # For arcade physics, maintain responsive steering at all speeds
            # For realistic physics, reduce steering at very high speeds only
            if speed > self.config.high_speed_threshold * 1.5:  # Only at very high speeds
                effective_steering = self.steering * speed_factor
            else:
                effective_steering = self.steering
            
            # Apply steering torque
            torque = effective_steering * self.config.max_torque
            self.body.torque = torque
        else:
            self.body.torque = 0
        
        # Apply braking
        if self.brake > 0.01:
            # Braking force opposes current velocity
            if speed > 0.1:  # Only brake if moving
                brake_direction = -velocity.normalized()
                brake_force = brake_direction * (self.brake * self.config.max_force * 1.5)
                self.body.apply_force_at_world_point(brake_force, self.body.position)
        
        # Apply damping (air resistance and rolling resistance)
        if speed > 0.1:
            # Linear damping
            linear_drag = -velocity * self.config.linear_damping * speed
            self.body.apply_force_at_world_point(linear_drag, self.body.position)
        
        # Angular damping
        if abs(self.body.angular_velocity) > 0.01:
            angular_drag = -self.body.angular_velocity * self.config.angular_damping
            self.body.torque += angular_drag
    
    def get_forward_vector(self) -> pymunk.Vec2d:
        """Get the car's forward direction vector."""
        return pymunk.Vec2d(math.cos(self.body.angle), math.sin(self.body.angle))
    
    def get_right_vector(self) -> pymunk.Vec2d:
        """Get the car's right direction vector."""
        return pymunk.Vec2d(math.cos(self.body.angle + math.pi/2), 
                           math.sin(self.body.angle + math.pi/2))
    
    def get_speed(self) -> float:
        """Get current speed in pixels per second."""
        return self.body.velocity.length
    
    def get_forward_speed(self) -> float:
        """Get speed in the forward direction (can be negative for reverse)."""
        forward = self.get_forward_vector()
        return self.body.velocity.dot(forward)
    
    def get_lateral_speed(self) -> float:
        """Get lateral (sideways) speed."""
        right = self.get_right_vector()
        return self.body.velocity.dot(right)
    
    def is_sliding(self, threshold: float = 50.0) -> bool:
        """
        Check if the car is sliding (lateral speed above threshold).
        
        Args:
            threshold: Lateral speed threshold for sliding detection
            
        Returns:
            True if car is sliding
        """
        return abs(self.get_lateral_speed()) > threshold
    
    def reset_position(self, position: Tuple[float, float], angle: float = 0.0) -> None:
        """
        Reset car position and clear velocities.
        
        Args:
            position: New position (x, y)
            angle: New angle in radians
        """
        self.body.position = position
        self.body.angle = angle
        self.body.velocity = (0, 0)
        self.body.angular_velocity = 0
        self.body.force = (0, 0)
        self.body.torque = 0
    
    def switch_physics_config(self, config: CarPhysicsConfig) -> None:
        """
        Switch to a different physics configuration.
        
        Args:
            config: New physics configuration
        """
        old_position = self.body.position
        old_angle = self.body.angle
        old_velocity = self.body.velocity
        old_angular_velocity = self.body.angular_velocity
        
        # Update configuration
        self.config = config
        
        # Update shape properties
        self.shape.friction = config.friction
        self.shape.elasticity = config.collision_elasticity
        
        # Update body mass and moment
        new_moment = pymunk.moment_for_box(config.mass, (config.width, config.height))
        self.body.mass = config.mass
        self.body.moment = new_moment
        
        # Preserve motion state
        self.body.position = old_position
        self.body.angle = old_angle
        self.body.velocity = old_velocity
        self.body.angular_velocity = old_angular_velocity
    
    def get_physics_info(self) -> Dict[str, Any]:
        """
        Get current physics information for debugging.
        
        Returns:
            Dictionary with car physics data
        """
        return {
            'position': tuple(self.body.position),
            'angle': self.body.angle,
            'velocity': tuple(self.body.velocity),
            'angular_velocity': self.body.angular_velocity,
            'speed': self.get_speed(),
            'forward_speed': self.get_forward_speed(),
            'lateral_speed': self.get_lateral_speed(),
            'is_sliding': self.is_sliding(),
            'throttle': self.throttle,
            'steering': self.steering,
            'brake': self.brake,
            'mass': self.body.mass,
            'friction': self.shape.friction
        }
    
    def cleanup(self) -> None:
        """Remove car from physics space and clean up resources."""
        if self.body in self.space.bodies:
            self.space.remove(self.body, self.shape)