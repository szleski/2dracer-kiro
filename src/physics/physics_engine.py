"""
Physics engine implementation using Pymunk for 2D physics simulation.

This module provides the core physics engine for the retro racing game,
supporting both arcade and realistic physics models with debug rendering capabilities.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import pymunk
import pygame
import math


@dataclass
class PhysicsConfig:
    """Configuration for physics simulation parameters."""
    
    model: str = "arcade"  # 'arcade' or 'realistic'
    gravity: Tuple[float, float] = (0, 0)  # Top-down view, no gravity
    damping: float = 0.1  # Air resistance/global damping
    time_step: float = 1.0 / 60.0  # 60 FPS physics
    iterations: int = 10  # Pymunk solver iterations for accuracy
    
    # Model-specific parameters
    arcade_friction: float = 0.9  # Higher friction for easier control
    realistic_friction: float = 0.7  # More realistic tire friction
    
    # Collision parameters
    collision_slop: float = 0.1  # Collision tolerance
    bias_factor: float = 0.9  # Collision bias for stability


class PhysicsEngine:
    """
    Main physics engine managing the Pymunk physics world.
    
    Handles physics simulation, configuration switching, and debug rendering
    for the retro racing game.
    """
    
    def __init__(self, config: Optional[PhysicsConfig] = None):
        """
        Initialize the physics engine with given configuration.
        
        Args:
            config: Physics configuration. Uses default if None.
        """
        self.config = config or PhysicsConfig()
        self.space = pymunk.Space()
        self.debug_renderer: Optional[pygame.Surface] = None
        self.debug_enabled = False
        
        # Track all bodies for debug rendering
        self.tracked_bodies: List[pymunk.Body] = []
        
        self._configure_space()
    
    def _configure_space(self) -> None:
        """Configure the Pymunk space with current settings."""
        self.space.gravity = self.config.gravity
        self.space.damping = self.config.damping
        self.space.iterations = self.config.iterations
        self.space.collision_slop = self.config.collision_slop
        self.space.collision_bias = self.config.bias_factor
    
    def step(self, dt: Optional[float] = None) -> None:
        """
        Step the physics simulation forward by one frame.
        
        Args:
            dt: Time step in seconds. Uses config time_step if None.
        """
        time_step = dt or self.config.time_step
        self.space.step(time_step)
    
    def add_body(self, body: pymunk.Body, shape: pymunk.Shape) -> None:
        """
        Add a body and shape to the physics world.
        
        Args:
            body: Pymunk body to add
            shape: Pymunk shape to add
        """
        self.space.add(body, shape)
        if body not in self.tracked_bodies:
            self.tracked_bodies.append(body)
    
    def remove_body(self, body: pymunk.Body, shape: pymunk.Shape) -> None:
        """
        Remove a body and shape from the physics world.
        
        Args:
            body: Pymunk body to remove
            shape: Pymunk shape to remove
        """
        if body in self.space.bodies:
            self.space.remove(body, shape)
        if body in self.tracked_bodies:
            self.tracked_bodies.remove(body)
    
    def add_static_body(self, shape: pymunk.Shape) -> None:
        """
        Add a static shape to the physics world.
        
        Args:
            shape: Static shape to add (attached to space.static_body)
        """
        self.space.add(shape)
    
    def remove_static_body(self, shape: pymunk.Shape) -> None:
        """
        Remove a static shape from the physics world.
        
        Args:
            shape: Static shape to remove
        """
        if shape in self.space.shapes:
            self.space.remove(shape)
    
    def switch_physics_model(self, model: str) -> None:
        """
        Switch between arcade and realistic physics models.
        
        Args:
            model: Physics model ('arcade' or 'realistic')
        """
        if model not in ['arcade', 'realistic']:
            raise ValueError(f"Invalid physics model: {model}")
        
        self.config.model = model
        
        # Update friction for all existing shapes
        friction = (self.config.arcade_friction if model == 'arcade' 
                   else self.config.realistic_friction)
        
        for shape in self.space.shapes:
            if hasattr(shape, 'friction'):
                shape.friction = friction
        
        # Reconfigure space parameters
        self._configure_space()
    
    def get_bodies_at_point(self, point: Tuple[float, float], 
                           max_distance: float = 0.0) -> List[pymunk.Body]:
        """
        Get all bodies at or near a specific point.
        
        Args:
            point: World coordinates (x, y)
            max_distance: Maximum distance from point
            
        Returns:
            List of bodies at the point
        """
        query = self.space.point_query(point, max_distance, pymunk.ShapeFilter())
        return [hit.shape.body for hit in query if hit.shape.body]
    
    def raycast(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[Dict[str, Any]]:
        """
        Cast a ray and return the first hit.
        
        Args:
            start: Ray start point (x, y)
            end: Ray end point (x, y)
            
        Returns:
            Dictionary with hit information or None if no hit
        """
        hit = self.space.segment_query_first(start, end, 0, pymunk.ShapeFilter())
        if hit:
            return {
                'point': hit.point,
                'normal': hit.normal,
                'alpha': hit.alpha,
                'shape': hit.shape,
                'body': hit.shape.body
            }
        return None
    
    def enable_debug_rendering(self, surface: pygame.Surface) -> None:
        """
        Enable debug rendering of physics bodies.
        
        Args:
            surface: Pygame surface to render debug info on
        """
        self.debug_enabled = True
        self.debug_renderer = surface
    
    def disable_debug_rendering(self) -> None:
        """Disable debug rendering."""
        self.debug_enabled = False
        self.debug_renderer = None
    
    def render_debug(self) -> None:
        """Render debug visualization of all physics bodies."""
        if not self.debug_enabled or not self.debug_renderer:
            return
        
        # Debug colors
        DYNAMIC_COLOR = pygame.Color(255, 0, 0, 128)  # Red for dynamic bodies
        STATIC_COLOR = pygame.Color(0, 255, 0, 128)   # Green for static bodies
        KINEMATIC_COLOR = pygame.Color(0, 0, 255, 128)  # Blue for kinematic bodies
        
        # Render all shapes
        for shape in self.space.shapes:
            body = shape.body
            
            # Choose color based on body type
            if body.body_type == pymunk.Body.DYNAMIC:
                color = DYNAMIC_COLOR
            elif body.body_type == pymunk.Body.STATIC:
                color = STATIC_COLOR
            else:  # KINEMATIC
                color = KINEMATIC_COLOR
            
            # Render based on shape type
            if isinstance(shape, pymunk.Circle):
                self._render_debug_circle(shape, color)
            elif isinstance(shape, pymunk.Poly):
                self._render_debug_poly(shape, color)
            elif isinstance(shape, pymunk.Segment):
                self._render_debug_segment(shape, color)
    
    def _render_debug_circle(self, shape: pymunk.Circle, color: pygame.Color) -> None:
        """Render debug visualization for a circle shape."""
        body = shape.body
        pos = int(body.position.x), int(body.position.y)
        radius = int(shape.radius)
        
        # Draw circle outline
        pygame.draw.circle(self.debug_renderer, color, pos, radius, 2)
        
        # Draw center point
        pygame.draw.circle(self.debug_renderer, color, pos, 2)
        
        # Draw direction line for rotation
        angle = body.angle
        end_x = pos[0] + radius * math.cos(angle)
        end_y = pos[1] + radius * math.sin(angle)
        pygame.draw.line(self.debug_renderer, color, pos, (int(end_x), int(end_y)), 1)
    
    def _render_debug_poly(self, shape: pymunk.Poly, color: pygame.Color) -> None:
        """Render debug visualization for a polygon shape."""
        body = shape.body
        vertices = []
        
        for v in shape.get_vertices():
            # Transform vertex to world coordinates
            world_v = body.local_to_world(v)
            vertices.append((int(world_v.x), int(world_v.y)))
        
        if len(vertices) >= 3:
            pygame.draw.polygon(self.debug_renderer, color, vertices, 2)
    
    def _render_debug_segment(self, shape: pymunk.Segment, color: pygame.Color) -> None:
        """Render debug visualization for a segment shape."""
        body = shape.body
        
        # Transform endpoints to world coordinates
        start = body.local_to_world(shape.a)
        end = body.local_to_world(shape.b)
        
        start_pos = (int(start.x), int(start.y))
        end_pos = (int(end.x), int(end.y))
        
        # Draw the segment
        pygame.draw.line(self.debug_renderer, color, start_pos, end_pos, 
                        max(1, int(shape.radius * 2)))
    
    def get_physics_info(self) -> Dict[str, Any]:
        """
        Get current physics engine information for debugging.
        
        Returns:
            Dictionary with physics engine stats
        """
        return {
            'model': self.config.model,
            'bodies': len(self.space.bodies),
            'shapes': len(self.space.shapes),
            'constraints': len(self.space.constraints),
            'gravity': self.space.gravity,
            'damping': self.space.damping,
            'iterations': self.space.iterations,
            'time_step': self.config.time_step
        }
    
    def cleanup(self) -> None:
        """Clean up physics engine resources."""
        # Remove all bodies and shapes
        for body in list(self.space.bodies):
            shapes = list(body.shapes)
            for shape in shapes:
                self.space.remove(body, shape)
        
        # Remove all static shapes
        for shape in list(self.space.shapes):
            if shape.body == self.space.static_body:
                self.space.remove(shape)
        
        # Clear tracking lists
        self.tracked_bodies.clear()
        
        # Disable debug rendering
        self.disable_debug_rendering()