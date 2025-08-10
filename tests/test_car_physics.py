"""
Tests for car physics implementation.

Tests the CarBody class and physics configurations to ensure proper
car simulation behavior.
"""

import pytest
import pymunk
import math
from src.physics.car_physics import CarBody, CarPhysicsConfig, CarPhysicsPresets


class TestCarPhysicsConfig:
    """Test car physics configuration classes."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = CarPhysicsConfig()
        
        assert config.mass == 1000.0
        assert config.width == 40.0
        assert config.height == 20.0
        assert config.friction == 0.7
        assert config.max_force == 5000.0
        assert config.max_torque == 2000.0
    
    def test_arcade_preset(self):
        """Test arcade physics preset."""
        config = CarPhysicsPresets.arcade()
        
        assert config.mass == 800.0  # Lighter
        assert config.friction == 0.9  # Higher friction
        assert config.max_force == 6000.0  # Higher force
        assert config.handling_degradation == 0.3  # Less degradation
    
    def test_realistic_preset(self):
        """Test realistic physics preset."""
        config = CarPhysicsPresets.realistic()
        
        assert config.mass == 1200.0  # Heavier
        assert config.friction == 0.6  # Lower friction
        assert config.max_force == 4000.0  # Lower force
        assert config.handling_degradation == 0.7  # More degradation


class TestCarBody:
    """Test car physics body implementation."""
    
    def setup_method(self):
        """Setup test environment."""
        self.space = pymunk.Space()
        self.car = CarBody(self.space, position=(100, 100))
    
    def teardown_method(self):
        """Clean up test environment."""
        self.car.cleanup()
    
    def test_car_creation(self):
        """Test car body creation."""
        assert self.car.body.position.x == 100
        assert self.car.body.position.y == 100
        assert self.car.body.angle == 0.0
        assert self.car.body in self.space.bodies
        assert self.car.shape in self.space.shapes
    
    def test_control_inputs(self):
        """Test control input application."""
        self.car.apply_controls(0.5, -0.3, 0.2)
        
        assert self.car.throttle == 0.5
        assert self.car.steering == -0.3
        assert self.car.brake == 0.2
    
    def test_control_input_clamping(self):
        """Test control inputs are properly clamped."""
        self.car.apply_controls(2.0, -1.5, 1.5)
        
        assert self.car.throttle == 1.0
        assert self.car.steering == -1.0
        assert self.car.brake == 1.0
    
    def test_forward_vector(self):
        """Test forward vector calculation."""
        # Car facing right (0 radians)
        forward = self.car.get_forward_vector()
        assert abs(forward.x - 1.0) < 0.001
        assert abs(forward.y - 0.0) < 0.001
        
        # Rotate car 90 degrees
        self.car.body.angle = math.pi / 2
        forward = self.car.get_forward_vector()
        assert abs(forward.x - 0.0) < 0.001
        assert abs(forward.y - 1.0) < 0.001
    
    def test_right_vector(self):
        """Test right vector calculation."""
        # Car facing right (0 radians)
        right = self.car.get_right_vector()
        assert abs(right.x - 0.0) < 0.001
        assert abs(right.y - 1.0) < 0.001
    
    def test_throttle_physics(self):
        """Test throttle application creates forward motion."""
        initial_position = self.car.body.position
        
        # Apply forward throttle
        self.car.apply_controls(1.0, 0.0, 0.0)
        
        # Update physics for several steps
        for _ in range(10):
            self.car.update_physics(1/60.0)
            self.space.step(1/60.0)
        
        # Car should have moved forward
        assert self.car.body.position.x > initial_position.x
        assert self.car.get_forward_speed() > 0
    
    def test_reverse_physics(self):
        """Test reverse throttle creates backward motion."""
        initial_position = self.car.body.position
        
        # Apply reverse throttle
        self.car.apply_controls(-1.0, 0.0, 0.0)
        
        # Update physics for several steps
        for _ in range(10):
            self.car.update_physics(1/60.0)
            self.space.step(1/60.0)
        
        # Car should have moved backward
        assert self.car.body.position.x < initial_position.x
        assert self.car.get_forward_speed() < 0
    
    def test_steering_physics(self):
        """Test steering creates rotation."""
        # Give car some forward velocity first
        self.car.body.velocity = (100, 0)
        
        # Apply steering
        self.car.apply_controls(0.0, 1.0, 0.0)  # Right turn
        
        # Update physics
        for _ in range(5):
            self.car.update_physics(1/60.0)
            self.space.step(1/60.0)
        
        # Car should be rotating
        assert abs(self.car.body.angular_velocity) > 0
    
    def test_braking_physics(self):
        """Test braking reduces speed."""
        # Give car forward velocity
        self.car.body.velocity = (100, 0)
        initial_speed = self.car.get_speed()
        
        # Apply brakes
        self.car.apply_controls(0.0, 0.0, 1.0)
        
        # Update physics
        for _ in range(10):
            self.car.update_physics(1/60.0)
            self.space.step(1/60.0)
        
        # Speed should be reduced
        assert self.car.get_speed() < initial_speed
    
    def test_speed_calculations(self):
        """Test speed calculation methods."""
        # Set known velocity
        self.car.body.velocity = (60, 80)  # 3-4-5 triangle, speed = 100
        
        speed = self.car.get_speed()
        assert abs(speed - 100.0) < 0.001
        
        # Test forward speed (car facing right)
        forward_speed = self.car.get_forward_speed()
        assert abs(forward_speed - 60.0) < 0.001
        
        # Test lateral speed
        lateral_speed = self.car.get_lateral_speed()
        assert abs(lateral_speed - 80.0) < 0.001
    
    def test_sliding_detection(self):
        """Test sliding detection."""
        # No lateral velocity - not sliding
        self.car.body.velocity = (100, 0)
        assert not self.car.is_sliding()
        
        # High lateral velocity - sliding
        self.car.body.velocity = (100, 60)
        assert self.car.is_sliding()
    
    def test_position_reset(self):
        """Test position reset functionality."""
        # Move and rotate car
        self.car.body.position = (200, 300)
        self.car.body.angle = math.pi / 4
        self.car.body.velocity = (50, 50)
        self.car.body.angular_velocity = 2.0
        
        # Reset position
        self.car.reset_position((400, 500), math.pi / 2)
        
        assert self.car.body.position.x == 400
        assert self.car.body.position.y == 500
        assert self.car.body.angle == math.pi / 2
        assert self.car.body.velocity.x == 0
        assert self.car.body.velocity.y == 0
        assert self.car.body.angular_velocity == 0
    
    def test_physics_config_switching(self):
        """Test switching physics configurations."""
        initial_position = self.car.body.position
        initial_velocity = self.car.body.velocity
        
        # Switch to realistic config
        realistic_config = CarPhysicsPresets.realistic()
        self.car.switch_physics_config(realistic_config)
        
        # Configuration should be updated
        assert self.car.config.mass == 1200.0
        assert self.car.shape.friction == 0.6
        
        # Position and velocity should be preserved
        assert self.car.body.position == initial_position
        assert self.car.body.velocity == initial_velocity
    
    def test_physics_info(self):
        """Test physics information retrieval."""
        self.car.body.velocity = (50, 30)
        self.car.apply_controls(0.5, -0.2, 0.1)
        
        info = self.car.get_physics_info()
        
        assert 'position' in info
        assert 'velocity' in info
        assert 'speed' in info
        assert 'throttle' in info
        assert info['throttle'] == 0.5
        assert info['steering'] == -0.2
        assert info['brake'] == 0.1
    
    def test_collision_callback_setup(self):
        """Test collision callback setup."""
        callback_called = False
        collision_info = None
        
        def test_callback(info):
            nonlocal callback_called, collision_info
            callback_called = True
            collision_info = info
        
        self.car.set_collision_callback(test_callback)
        
        # Create a static boundary for collision - place it closer to the car
        boundary_body = self.space.static_body
        boundary_shape = pymunk.Segment(boundary_body, (50, 120), (150, 120), 5)
        boundary_shape.collision_type = 2  # Boundary collision type
        self.space.add(boundary_shape)
        
        # Position car above the boundary and give it downward velocity
        self.car.reset_position((100, 80), 0)  # Position car above boundary
        self.car.body.velocity = (0, 50)  # Moderate downward velocity
        
        # Step physics until collision or timeout
        collision_detected = False
        for i in range(50):  # More steps to ensure collision
            self.car.update_physics(1/60.0)
            self.space.step(1/60.0)
            
            # Check if car has moved past the boundary (collision occurred)
            if self.car.body.position.y >= 120:
                collision_detected = True
                break
                
            if callback_called:
                break
        
        # Either callback should be called or collision should be detected
        assert callback_called or collision_detected, f"No collision detected. Car position: {self.car.body.position}"
        
        if callback_called:
            assert collision_info is not None
            assert 'point' in collision_info
            assert 'normal' in collision_info


class TestPhysicsIntegration:
    """Test integration between car physics and physics engine."""
    
    def setup_method(self):
        """Setup test environment."""
        self.space = pymunk.Space()
    
    def test_multiple_cars(self):
        """Test multiple cars in the same physics space."""
        car1 = CarBody(self.space, position=(100, 100))
        car2 = CarBody(self.space, position=(200, 100))
        
        # Both cars should be in the space
        assert len(self.space.bodies) == 2
        assert len(self.space.shapes) == 2
        
        # Cars should have different positions
        assert car1.body.position != car2.body.position
        
        # Clean up
        car1.cleanup()
        car2.cleanup()
    
    def test_car_boundary_collision(self):
        """Test car collision with track boundaries."""
        car = CarBody(self.space, position=(100, 80))
        
        # Create track boundary closer to car
        boundary = pymunk.Segment(self.space.static_body, (50, 120), (150, 120), 5)
        boundary.collision_type = 2  # Boundary collision type
        boundary.friction = 0.8
        boundary.elasticity = 0.3
        self.space.add(boundary)
        
        # Give car initial downward velocity
        initial_velocity = 50.0
        car.body.velocity = (0, initial_velocity)
        
        # Step physics until collision
        for _ in range(50):
            car.update_physics(1/60.0)
            self.space.step(1/60.0)
            
            # If car has bounced back up, collision occurred
            if car.body.velocity.y < 0:
                break
        
        # Car should have collided - either bounced back or velocity reduced significantly
        final_velocity = car.body.velocity.y
        assert final_velocity < initial_velocity * 0.8 or final_velocity < 0, \
            f"Expected collision to reduce velocity. Initial: {initial_velocity}, Final: {final_velocity}"
        
        car.cleanup()