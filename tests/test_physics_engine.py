"""
Tests for the PhysicsEngine class.
"""

import pytest
import pygame
import pymunk
from src.physics.physics_engine import PhysicsEngine, PhysicsConfig


class TestPhysicsEngine:
    """Test cases for PhysicsEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.config = PhysicsConfig()
        self.engine = PhysicsEngine(self.config)
    
    def teardown_method(self):
        """Clean up after tests."""
        self.engine.cleanup()
        pygame.quit()
    
    def test_initialization(self):
        """Test physics engine initialization."""
        assert self.engine.space is not None
        assert self.engine.config.model == "arcade"
        assert self.engine.space.gravity == (0, 0)
        assert self.engine.space.damping == 0.1
        assert not self.engine.debug_enabled
    
    def test_step_simulation(self):
        """Test physics simulation stepping."""
        # Create a simple dynamic body
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        shape = pymunk.Circle(body, 10)
        
        self.engine.add_body(body, shape)
        
        # Apply a force and step simulation
        body.apply_force_at_local_point((100, 0), (0, 0))
        initial_velocity = body.velocity.x
        
        self.engine.step()
        
        # Velocity should have changed due to applied force
        assert body.velocity.x != initial_velocity
    
    def test_add_remove_body(self):
        """Test adding and removing bodies."""
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        shape = pymunk.Circle(body, 10)
        
        # Add body
        self.engine.add_body(body, shape)
        assert body in self.engine.space.bodies
        assert shape in self.engine.space.shapes
        assert body in self.engine.tracked_bodies
        
        # Remove body
        self.engine.remove_body(body, shape)
        assert body not in self.engine.space.bodies
        assert shape not in self.engine.space.shapes
        assert body not in self.engine.tracked_bodies
    
    def test_static_body_operations(self):
        """Test static body operations."""
        # Create a static segment
        shape = pymunk.Segment(self.engine.space.static_body, (0, 0), (100, 0), 5)
        
        # Add static shape
        self.engine.add_static_body(shape)
        assert shape in self.engine.space.shapes
        
        # Remove static shape
        self.engine.remove_static_body(shape)
        assert shape not in self.engine.space.shapes
    
    def test_physics_model_switching(self):
        """Test switching between physics models."""
        # Create a body with a shape
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        shape = pymunk.Circle(body, 10)
        self.engine.add_body(body, shape)
        
        # Switch to realistic model
        self.engine.switch_physics_model("realistic")
        assert self.engine.config.model == "realistic"
        assert shape.friction == self.config.realistic_friction
        
        # Switch back to arcade model
        self.engine.switch_physics_model("arcade")
        assert self.engine.config.model == "arcade"
        assert shape.friction == self.config.arcade_friction
    
    def test_invalid_physics_model(self):
        """Test invalid physics model raises error."""
        with pytest.raises(ValueError):
            self.engine.switch_physics_model("invalid")
    
    def test_point_query(self):
        """Test querying bodies at a point."""
        # Create a body at a specific position
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        body.position = 50, 50
        shape = pymunk.Circle(body, 10)
        self.engine.add_body(body, shape)
        
        # Query at the body's position
        bodies = self.engine.get_bodies_at_point((50, 50))
        assert len(bodies) == 1
        assert bodies[0] == body
        
        # Query at a different position
        bodies = self.engine.get_bodies_at_point((100, 100))
        assert len(bodies) == 0
    
    def test_raycast(self):
        """Test raycasting functionality."""
        # Create a static wall
        shape = pymunk.Segment(self.engine.space.static_body, (0, 50), (100, 50), 5)
        self.engine.add_static_body(shape)
        
        # Cast ray that should hit the wall
        hit = self.engine.raycast((50, 0), (50, 100))
        assert hit is not None
        assert hit['shape'] == shape
        
        # Cast ray that should miss
        hit = self.engine.raycast((200, 0), (200, 100))
        assert hit is None
    
    def test_debug_rendering(self):
        """Test debug rendering functionality."""
        surface = pygame.Surface((800, 600))
        
        # Enable debug rendering
        self.engine.enable_debug_rendering(surface)
        assert self.engine.debug_enabled
        assert self.engine.debug_renderer == surface
        
        # Disable debug rendering
        self.engine.disable_debug_rendering()
        assert not self.engine.debug_enabled
        assert self.engine.debug_renderer is None
    
    def test_physics_info(self):
        """Test getting physics engine information."""
        info = self.engine.get_physics_info()
        
        assert 'model' in info
        assert 'bodies' in info
        assert 'shapes' in info
        assert 'constraints' in info
        assert info['model'] == 'arcade'
        assert info['bodies'] == 0  # No bodies added yet
    
    def test_cleanup(self):
        """Test physics engine cleanup."""
        # Add some bodies
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        shape = pymunk.Circle(body, 10)
        self.engine.add_body(body, shape)
        
        # Add static shape
        static_shape = pymunk.Segment(self.engine.space.static_body, (0, 0), (100, 0), 5)
        self.engine.add_static_body(static_shape)
        
        # Cleanup
        self.engine.cleanup()
        
        assert len(self.engine.space.bodies) == 0
        assert len(self.engine.space.shapes) == 0
        assert len(self.engine.tracked_bodies) == 0
        assert not self.engine.debug_enabled


class TestPhysicsConfig:
    """Test cases for PhysicsConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PhysicsConfig()
        
        assert config.model == "arcade"
        assert config.gravity == (0, 0)
        assert config.damping == 0.1
        assert config.time_step == 1.0 / 60.0
        assert config.iterations == 10
        assert config.arcade_friction == 0.9
        assert config.realistic_friction == 0.7
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = PhysicsConfig(
            model="realistic",
            gravity=(0, -981),
            damping=0.2,
            time_step=1.0 / 120.0,
            iterations=20
        )
        
        assert config.model == "realistic"
        assert config.gravity == (0, -981)
        assert config.damping == 0.2
        assert config.time_step == 1.0 / 120.0
        assert config.iterations == 20