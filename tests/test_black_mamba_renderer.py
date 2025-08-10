"""
Tests for the Black Mamba Racer rendering system.
"""

import pytest
import pygame
from src.rendering.black_mamba_renderer import BlackMambaRenderer, ColorPalette


class TestColorPalette:
    """Test the color palette definitions."""
    
    def test_color_palette_values(self):
        """Test that color palette has expected values."""
        palette = ColorPalette()
        
        # Test that colors are RGB tuples
        assert isinstance(palette.BACKGROUND_GRAY, tuple)
        assert len(palette.BACKGROUND_GRAY) == 3
        assert all(0 <= c <= 255 for c in palette.BACKGROUND_GRAY)
        
        # Test muted color characteristics
        assert palette.BACKGROUND_GRAY[0] == palette.BACKGROUND_GRAY[1] == palette.BACKGROUND_GRAY[2]  # Gray
        assert palette.TRACK_GRAY[0] == palette.TRACK_GRAY[1] == palette.TRACK_GRAY[2]  # Gray
        
        # Test accent colors are more vibrant
        assert palette.ACCENT_RED[0] > palette.ACCENT_RED[1]  # More red than green
        assert palette.ACCENT_YELLOW[0] >= 200 and palette.ACCENT_YELLOW[1] >= 200  # Bright yellow


class TestBlackMambaRenderer:
    """Test the main renderer class."""
    
    @pytest.fixture
    def renderer(self):
        """Create a renderer instance for testing."""
        pygame.init()
        return BlackMambaRenderer(800, 600)
    
    def test_renderer_initialization(self, renderer):
        """Test renderer initializes correctly."""
        assert renderer.screen_width == 800
        assert renderer.screen_height == 600
        assert isinstance(renderer.colors, ColorPalette)
        assert renderer.screen is not None
        assert renderer.track_surface is not None
        assert renderer.ui_surface is not None
    
    def test_car_sprite_generation(self, renderer):
        """Test car sprite generation."""
        color = (100, 100, 100)
        sprite = renderer.generate_car_sprite(color, 0)
        
        assert isinstance(sprite, pygame.Surface)
        assert sprite.get_width() > 0
        assert sprite.get_height() > 0
    
    def test_car_sprite_caching(self, renderer):
        """Test that car sprites are cached properly."""
        color = (100, 100, 100)
        angle = 45.0
        
        sprite1 = renderer.generate_car_sprite(color, angle)
        sprite2 = renderer.generate_car_sprite(color, angle)
        
        # Should return the same cached sprite
        assert sprite1 is sprite2
    
    def test_car_sprite_different_angles(self, renderer):
        """Test car sprites at different angles."""
        color = (100, 100, 100)
        
        sprite_0 = renderer.generate_car_sprite(color, 0)
        sprite_90 = renderer.generate_car_sprite(color, 90)
        
        # Different angles should produce different sprites
        assert sprite_0 is not sprite_90
    
    def test_clear_screen(self, renderer):
        """Test screen clearing."""
        # Should not raise any exceptions
        renderer.clear_screen()
    
    def test_clear_ui_surface(self, renderer):
        """Test UI surface clearing."""
        # Should not raise any exceptions
        renderer.clear_ui_surface()
    
    def test_draw_car(self, renderer):
        """Test car drawing."""
        position = (100, 100)
        angle = 45.0
        color = (150, 150, 150)
        
        # Should not raise any exceptions
        renderer.draw_car(position, angle, color)
    
    def test_draw_tire_barrier(self, renderer):
        """Test tire barrier drawing."""
        position = (200, 200)
        radius = 10
        
        # Should not raise any exceptions
        renderer.draw_tire_barrier(position, radius)
    
    def test_draw_checkered_pattern(self, renderer):
        """Test checkered pattern drawing."""
        rect = pygame.Rect(50, 50, 100, 100)
        
        # Should not raise any exceptions
        renderer.draw_checkered_pattern(rect, 8)
    
    def test_draw_track_boundary_checkered(self, renderer):
        """Test track boundary with checkered pattern."""
        points = [(0, 0), (100, 0), (100, 100), (0, 100)]
        
        # Should not raise any exceptions
        renderer.draw_track_boundary(points, width=20, use_checkered=True)
    
    def test_draw_track_boundary_tire_barriers(self, renderer):
        """Test track boundary with tire barriers."""
        points = [(0, 0), (100, 0), (100, 100), (0, 100)]
        
        # Should not raise any exceptions
        renderer.draw_track_boundary(points, width=20, use_checkered=False)
    
    def test_draw_hud_text(self, renderer):
        """Test HUD text drawing."""
        text = "Test Text"
        position = (10, 10)
        
        # Should not raise any exceptions
        renderer.draw_hud_text(text, position, "medium")
    
    def test_draw_mini_map(self, renderer):
        """Test mini-map drawing."""
        position = (650, 50)
        size = (140, 100)
        track_points = [(0, 0), (100, 0), (100, 100), (0, 100)]
        car_positions = [(50, 50), (75, 25)]
        
        # Should not raise any exceptions
        renderer.draw_mini_map(position, size, track_points, car_positions)
    
    def test_present(self, renderer):
        """Test frame presentation."""
        # Should not raise any exceptions
        renderer.present()
    
    def test_get_surfaces(self, renderer):
        """Test surface getters."""
        screen = renderer.get_screen_surface()
        ui = renderer.get_ui_surface()
        
        assert isinstance(screen, pygame.Surface)
        assert isinstance(ui, pygame.Surface)
        assert screen is renderer.screen
        assert ui is renderer.ui_surface