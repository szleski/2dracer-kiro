"""
Tests for the Car entity class.

Tests the integration of physics, rendering, and game logic in the Car entity.
"""

import pytest
import pygame
import pymunk
import math
from unittest.mock import Mock, patch

from src.entities.car import Car, CarState
from src.physics.car_physics import CarPhysicsPresets
from src.rendering.black_mamba_renderer import BlackMambaRenderer


class TestCarState:
    """Test CarState dataclass."""
    
    def test_car_state_initialization(self):
        """Test CarState initialization with default values."""
        state = CarState(car_id="test_car")
        
        assert state.car_id == "test_car"
        assert state.is_player is False
        assert state.current_lap == 0
        assert state.lap_time == 0.0
        assert state.best_lap_time is None
        assert state.position_in_race == 1
        assert state.top_speed == 0.0
        assert state.distance_traveled == 0.0
        assert state.is_finished is False
        assert state.is_crashed is False
        assert state.respawn_timer == 0.0
    
    def test_car_state_player_initialization(self):
        """Test CarState initialization for player car."""
        state = CarState(car_id="player", is_player=True)
        
        assert state.car_id == "player"
        assert state.is_player is True


class TestCar:
    """Test Car entity class."""
    
    @pytest.fixture
    def physics_space(self):
        """Create a Pymunk space for testing."""
        space = pymunk.Space()
        space.gravity = (0, 0)
        return space
    
    @pytest.fixture
    def mock_renderer(self):
        """Create a mock BlackMambaRenderer for testing."""
        with patch('pygame.display.set_mode'), \
             patch('pygame.font.init'), \
             patch('pygame.font.Font'):
            renderer = Mock(spec=BlackMambaRenderer)
            return renderer
    
    def test_car_initialization(self, physics_space):
        """Test basic car initialization."""
        car = Car("test_car", physics_space, position=(100, 200), angle=math.pi/4)
        
        assert car.state.car_id == "test_car"
        assert car.state.is_player is False
        assert car.get_position() == (100, 200)
        assert abs(car.get_angle_radians() - math.pi/4) < 0.001
        assert car.throttle_input == 0.0
        assert car.steering_input == 0.0
        assert car.brake_input == 0.0
    
    def test_player_car_initialization(self, physics_space):
        """Test player car initialization."""
        car = Car("player", physics_space, is_player=True)
        
        assert car.state.car_id == "player"
        assert car.state.is_player is True
        # Player cars should get red color
        assert car.car_color == (220, 50, 50)
    
    def test_ai_car_color_assignment(self, physics_space):
        """Test AI car color assignment."""
        car1 = Car("ai_1", physics_space)
        car2 = Car("ai_2", physics_space)
        
        # AI cars should get gray colors
        assert car1.car_color in [(120, 120, 120), (80, 80, 80), (60, 60, 60)]
        assert car2.car_color in [(120, 120, 120), (80, 80, 80), (60, 60, 60)]
        
        # Same ID should get same color
        car1_duplicate = Car("ai_1", physics_space)
        assert car1_duplicate.car_color == car1.car_color
    
    def test_apply_controls(self, physics_space):
        """Test applying control inputs."""
        car = Car("test_car", physics_space)
        
        car.apply_controls(0.8, -0.5, 0.3)
        
        assert car.throttle_input == 0.8
        assert car.steering_input == -0.5
        assert car.brake_input == 0.3
        
        # Test clamping
        car.apply_controls(2.0, -2.0, 2.0)
        assert car.throttle_input == 1.0
        assert car.steering_input == -1.0
        assert car.brake_input == 1.0
    
    def test_update_basic(self, physics_space):
        """Test basic car update functionality."""
        car = Car("test_car", physics_space)
        initial_position = car.get_position()
        
        # Apply some throttle and update multiple times to see movement
        car.apply_controls(0.5, 0.0, 0.0)
        for _ in range(10):  # Multiple physics steps
            car.update(1/60.0)  # 60 FPS update
            physics_space.step(1/60.0)  # Step physics simulation
        
        # Car should have moved forward
        new_position = car.get_position()
        assert new_position != initial_position
        
        # Lap time should increase
        assert car.state.lap_time > 0.0
    
    def test_crash_handling(self, physics_space):
        """Test crash detection and recovery."""
        car = Car("test_car", physics_space)
        
        # Simulate a high-impact collision
        collision_info = {
            'impulse': pymunk.Vec2d(500, 0),  # High impact force
            'point': (100, 100),
            'normal': pymunk.Vec2d(1, 0),
            'other_shape': Mock()
        }
        
        car._handle_collision(collision_info)
        
        assert car.state.is_crashed is True
        assert car.state.respawn_timer > 0
        
        # Update until respawn timer expires
        while car.state.respawn_timer > 0:
            car.update(1/60.0)
        
        assert car.state.is_crashed is False
        assert car.state.respawn_timer == 0.0
    
    def test_lap_completion(self, physics_space):
        """Test lap completion functionality."""
        car = Car("test_car", physics_space)
        
        # Simulate some lap time
        car.state.lap_time = 45.5
        
        car.complete_lap(45.5)
        
        assert car.state.current_lap == 1
        assert car.state.best_lap_time == 45.5
        assert car.state.lap_time == 0.0
        
        # Complete another lap with better time
        car.state.lap_time = 42.3
        car.complete_lap(42.3)
        
        assert car.state.current_lap == 2
        assert car.state.best_lap_time == 42.3
    
    def test_race_finish(self, physics_space):
        """Test race finishing functionality."""
        car = Car("test_car", physics_space)
        
        car.finish_race(3)
        
        assert car.state.is_finished is True
        assert car.state.position_in_race == 3
    
    def test_physics_model_switching(self, physics_space):
        """Test switching between physics models."""
        car = Car("test_car", physics_space)
        
        # Start with arcade physics
        initial_friction = car.physics_body.shape.friction
        
        # Switch to realistic
        car.switch_physics_model('realistic')
        realistic_friction = car.physics_body.shape.friction
        
        # Switch back to arcade
        car.switch_physics_model('arcade')
        arcade_friction = car.physics_body.shape.friction
        
        # Realistic should have lower friction than arcade
        assert realistic_friction < arcade_friction
        assert arcade_friction == initial_friction
    
    def test_position_reset(self, physics_space):
        """Test position reset functionality."""
        car = Car("test_car", physics_space, position=(100, 100))
        
        # Move the car and crash it
        car.apply_controls(1.0, 0.0, 0.0)
        car.update(1.0)  # Large time step to move significantly
        car.state.is_crashed = True
        
        # Reset position
        new_position = (200, 300)
        new_angle = math.pi/2
        car.reset_position(new_position, new_angle)
        
        assert car.get_position() == new_position
        assert abs(car.get_angle_radians() - new_angle) < 0.001
        assert car.state.is_crashed is False
        assert car.state.respawn_timer == 0.0
        assert car.get_velocity() == (0, 0)
    
    def test_performance_metrics(self, physics_space):
        """Test performance metrics tracking."""
        car = Car("test_car", physics_space)
        
        # Apply throttle and update multiple times
        car.apply_controls(1.0, 0.0, 0.0)
        for _ in range(60):  # 1 second at 60 FPS
            car.update(1/60.0)
            physics_space.step(1/60.0)  # Step physics simulation
        
        # Should have tracked distance and speed
        assert car.state.distance_traveled > 0
        assert car.state.top_speed > 0
    
    def test_get_car_info(self, physics_space):
        """Test comprehensive car information retrieval."""
        car = Car("test_car", physics_space, is_player=True)
        car.apply_controls(0.5, 0.2, 0.1)
        car.state.current_lap = 2
        car.state.best_lap_time = 45.5
        
        info = car.get_car_info()
        
        # Check all expected fields are present
        expected_fields = [
            'car_id', 'is_player', 'is_crashed', 'is_finished',
            'current_lap', 'lap_time', 'best_lap_time', 'position_in_race',
            'top_speed', 'distance_traveled', 'position', 'angle_degrees',
            'speed', 'forward_speed', 'lateral_speed', 'is_sliding',
            'throttle', 'steering', 'brake', 'physics_model', 'mass'
        ]
        
        for field in expected_fields:
            assert field in info
        
        assert info['car_id'] == "test_car"
        assert info['is_player'] is True
        assert info['current_lap'] == 2
        assert info['best_lap_time'] == 45.5
        assert info['throttle'] == 0.5
        assert info['steering'] == 0.2
        assert info['brake'] == 0.1
    
    def test_collision_callback(self, physics_space):
        """Test collision callback functionality."""
        car = Car("test_car", physics_space)
        callback_called = False
        collision_data = None
        
        def test_callback(car_obj, collision_info):
            nonlocal callback_called, collision_data
            callback_called = True
            collision_data = collision_info
        
        car.set_collision_callback(test_callback)
        
        # Simulate collision
        collision_info = {
            'impulse': pymunk.Vec2d(100, 0),
            'point': (100, 100),
            'normal': pymunk.Vec2d(1, 0),
            'other_shape': Mock()
        }
        
        car._handle_collision(collision_info)
        
        assert callback_called is True
        assert collision_data == collision_info
    
    def test_cleanup(self, physics_space):
        """Test car cleanup functionality."""
        car = Car("test_car", physics_space)
        
        # Verify car is in physics space
        assert car.physics_body.body in physics_space.bodies
        assert car.physics_body.shape in physics_space.shapes
        
        # Cleanup
        car.cleanup()
        
        # Verify car is removed from physics space
        assert car.physics_body.body not in physics_space.bodies
        assert car.physics_body.shape not in physics_space.shapes


if __name__ == "__main__":
    pytest.main([__file__])