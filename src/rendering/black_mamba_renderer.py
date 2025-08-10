"""
Black Mamba Racer style rendering system.

Implements the clean, minimalist aesthetic with muted colors and geometric shapes
characteristic of classic mobile racing games like Black Mamba Racer.
"""

import pygame
import math
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class ColorPalette:
    """Black Mamba Racer color palette with muted tones and selective accents."""
    
    # Base colors - muted grays and whites
    BACKGROUND_GRAY = (45, 45, 45)
    TRACK_GRAY = (80, 80, 80)
    LIGHT_GRAY = (120, 120, 120)
    WHITE = (255, 255, 255)
    OFF_WHITE = (240, 240, 240)
    
    # Accent colors - selective use only
    ACCENT_RED = (220, 50, 50)
    ACCENT_YELLOW = (255, 200, 50)
    
    # Track elements
    TIRE_BARRIER_BLACK = (25, 25, 25)
    CHECKERED_DARK = (60, 60, 60)
    CHECKERED_LIGHT = (100, 100, 100)
    
    # UI elements
    HUD_TEXT = (200, 200, 200)
    HUD_ACCENT = (255, 255, 255)


class BlackMambaRenderer:
    """
    Main rendering class for Black Mamba Racer aesthetic.
    
    Manages pygame surfaces and implements the clean, geometric visual style
    with muted color palette and minimalist design principles.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize the Black Mamba renderer.
        
        Args:
            screen_width: Width of the game screen in pixels
            screen_height: Height of the game screen in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.colors = ColorPalette()
        
        # Initialize pygame surfaces
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.track_surface = pygame.Surface((screen_width * 2, screen_height * 2))
        self.ui_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        # Car sprite cache for different angles
        self._car_sprite_cache = {}
        self._car_sprite_size = (20, 12)
        
        # Initialize fonts for clean typography
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
    
    def clear_screen(self) -> None:
        """Clear the screen with background color."""
        self.screen.fill(self.colors.BACKGROUND_GRAY)
    
    def clear_ui_surface(self) -> None:
        """Clear the UI overlay surface."""
        self.ui_surface.fill((0, 0, 0, 0))  # Transparent
    
    def generate_car_sprite(self, color: Tuple[int, int, int], angle: float = 0.0) -> pygame.Surface:
        """
        Generate a geometric arrow-like car sprite.
        
        Args:
            color: RGB color tuple for the car
            angle: Rotation angle in degrees
            
        Returns:
            pygame.Surface containing the car sprite
        """
        cache_key = (color, int(angle))
        if cache_key in self._car_sprite_cache:
            return self._car_sprite_cache[cache_key]
        
        width, height = self._car_sprite_size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Create arrow-like car shape (pointing right by default)
        points = [
            (width - 2, height // 2),      # Front point
            (width - 8, 2),                # Front top
            (2, 2),                        # Rear top
            (2, height - 2),               # Rear bottom
            (width - 8, height - 2),       # Front bottom
        ]
        
        # Draw main car body
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, self.colors.WHITE, points, 1)
        
        # Add small accent details
        pygame.draw.circle(surface, self.colors.LIGHT_GRAY, (6, height // 2), 2)
        
        # Rotate if needed
        if angle != 0:
            surface = pygame.transform.rotate(surface, -angle)
        
        # Cache the sprite
        self._car_sprite_cache[cache_key] = surface
        return surface
    
    def draw_car(self, position: Tuple[float, float], angle: float, 
                 color: Tuple[int, int, int] = None) -> None:
        """
        Draw a car at the specified position and angle.
        
        Args:
            position: (x, y) position in world coordinates
            angle: Rotation angle in degrees
            color: Car color (defaults to light gray)
        """
        if color is None:
            color = self.colors.LIGHT_GRAY
        
        sprite = self.generate_car_sprite(color, angle)
        rect = sprite.get_rect(center=position)
        self.screen.blit(sprite, rect)
    
    def draw_tire_barrier(self, position: Tuple[float, float], radius: float = 8) -> None:
        """
        Draw a tire barrier element.
        
        Args:
            position: (x, y) center position
            radius: Radius of the tire barrier
        """
        pygame.draw.circle(self.screen, self.colors.TIRE_BARRIER_BLACK, 
                          (int(position[0]), int(position[1])), int(radius))
        pygame.draw.circle(self.screen, self.colors.LIGHT_GRAY, 
                          (int(position[0]), int(position[1])), int(radius), 1)
    
    def draw_checkered_pattern(self, rect: pygame.Rect, square_size: int = 8) -> None:
        """
        Draw a checkered pattern within the given rectangle.
        
        Args:
            rect: Rectangle to fill with checkered pattern
            square_size: Size of each checkered square
        """
        for x in range(rect.left, rect.right, square_size):
            for y in range(rect.top, rect.bottom, square_size):
                # Determine if this square should be dark or light
                square_x = (x - rect.left) // square_size
                square_y = (y - rect.top) // square_size
                is_dark = (square_x + square_y) % 2 == 0
                
                color = self.colors.CHECKERED_DARK if is_dark else self.colors.CHECKERED_LIGHT
                square_rect = pygame.Rect(x, y, square_size, square_size)
                clipped_rect = square_rect.clip(rect)  # Clip to boundary
                if clipped_rect.width > 0 and clipped_rect.height > 0:
                    pygame.draw.rect(self.screen, color, clipped_rect)
    
    def draw_track_boundary(self, points: List[Tuple[float, float]], 
                           width: float = 20, use_checkered: bool = True) -> None:
        """
        Draw track boundary with tire barriers or checkered pattern.
        
        Args:
            points: List of points defining the boundary
            width: Width of the boundary
            use_checkered: Whether to use checkered pattern or tire barriers
        """
        if len(points) < 2:
            return
        
        if use_checkered:
            # Draw checkered boundary
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i + 1]
                
                # Calculate perpendicular vector for width
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                length = math.sqrt(dx*dx + dy*dy)
                if length == 0:
                    continue
                
                # Normalize and get perpendicular
                dx /= length
                dy /= length
                perp_x = -dy * width / 2
                perp_y = dx * width / 2
                
                # Create rectangle for this segment
                rect_points = [
                    (start[0] + perp_x, start[1] + perp_y),
                    (start[0] - perp_x, start[1] - perp_y),
                    (end[0] - perp_x, end[1] - perp_y),
                    (end[0] + perp_x, end[1] + perp_y)
                ]
                
                # Draw the segment
                pygame.draw.polygon(self.screen, self.colors.CHECKERED_DARK, rect_points)
        else:
            # Draw tire barriers along the boundary
            barrier_spacing = 16
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i + 1]
                
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                length = math.sqrt(dx*dx + dy*dy)
                
                if length == 0:
                    continue
                
                # Place tire barriers along the segment
                num_barriers = max(1, int(length / barrier_spacing))
                for j in range(num_barriers + 1):
                    t = j / num_barriers if num_barriers > 0 else 0
                    pos = (start[0] + t * dx, start[1] + t * dy)
                    self.draw_tire_barrier(pos)
    
    def draw_hud_text(self, text: str, position: Tuple[int, int], 
                      font_size: str = "medium", color: Tuple[int, int, int] = None) -> None:
        """
        Draw HUD text with clean typography.
        
        Args:
            text: Text to display
            position: (x, y) position for the text
            font_size: "small", "medium", or "large"
            color: Text color (defaults to HUD_TEXT)
        """
        if color is None:
            color = self.colors.HUD_TEXT
        
        font = {
            "small": self.font_small,
            "medium": self.font_medium,
            "large": self.font_large
        }.get(font_size, self.font_medium)
        
        text_surface = font.render(text, True, color)
        self.ui_surface.blit(text_surface, position)
    
    def draw_mini_map(self, position: Tuple[int, int], size: Tuple[int, int],
                      track_points: List[Tuple[float, float]], 
                      car_positions: List[Tuple[float, float]]) -> None:
        """
        Draw a minimalist mini-map in the corner.
        
        Args:
            position: (x, y) position of the mini-map
            size: (width, height) of the mini-map
            track_points: Track outline points
            car_positions: Current car positions
        """
        # Draw mini-map background
        map_rect = pygame.Rect(position[0], position[1], size[0], size[1])
        pygame.draw.rect(self.ui_surface, self.colors.BACKGROUND_GRAY, map_rect)
        pygame.draw.rect(self.ui_surface, self.colors.WHITE, map_rect, 1)
        
        if not track_points:
            return
        
        # Calculate scale to fit track in mini-map
        min_x = min(p[0] for p in track_points)
        max_x = max(p[0] for p in track_points)
        min_y = min(p[1] for p in track_points)
        max_y = max(p[1] for p in track_points)
        
        track_width = max_x - min_x
        track_height = max_y - min_y
        
        if track_width == 0 or track_height == 0:
            return
        
        scale_x = (size[0] - 10) / track_width
        scale_y = (size[1] - 10) / track_height
        scale = min(scale_x, scale_y)
        
        # Draw track outline
        scaled_points = []
        for point in track_points:
            scaled_x = position[0] + 5 + (point[0] - min_x) * scale
            scaled_y = position[1] + 5 + (point[1] - min_y) * scale
            scaled_points.append((scaled_x, scaled_y))
        
        if len(scaled_points) > 2:
            pygame.draw.lines(self.ui_surface, self.colors.LIGHT_GRAY, True, scaled_points, 2)
        
        # Draw car positions
        for car_pos in car_positions:
            scaled_x = position[0] + 5 + (car_pos[0] - min_x) * scale
            scaled_y = position[1] + 5 + (car_pos[1] - min_y) * scale
            pygame.draw.circle(self.ui_surface, self.colors.ACCENT_RED, 
                             (int(scaled_x), int(scaled_y)), 2)
    
    def present(self) -> None:
        """Present the final rendered frame to the screen."""
        # Blit UI overlay on top of everything
        self.screen.blit(self.ui_surface, (0, 0))
        pygame.display.flip()
    
    def get_screen_surface(self) -> pygame.Surface:
        """Get the main screen surface for direct drawing."""
        return self.screen
    
    def get_ui_surface(self) -> pygame.Surface:
        """Get the UI overlay surface for HUD elements."""
        return self.ui_surface