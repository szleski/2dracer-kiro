#!/usr/bin/env python3
"""
Demo script for the Black Mamba Racer rendering system.

This script demonstrates the key visual elements and aesthetic features
of the BlackMambaRenderer class.
"""

import pygame
import sys
import math
import time
from src.rendering.black_mamba_renderer import BlackMambaRenderer


def main():
    """Run the Black Mamba Racer rendering demo."""
    pygame.init()
    
    # Initialize renderer
    renderer = BlackMambaRenderer(800, 600)
    clock = pygame.time.Clock()
    
    # Demo state
    running = True
    demo_time = 0
    
    # Sample track points for mini-map
    track_points = [
        (100, 100), (300, 100), (400, 150), (450, 250),
        (400, 350), (300, 400), (200, 450), (100, 400),
        (50, 300), (50, 200)
    ]
    
    print("Black Mamba Racer Rendering Demo")
    print("Press ESC to exit")
    print("Demonstrating:")
    print("- Muted color palette")
    print("- Geometric car sprites")
    print("- Tire barriers and checkered patterns")
    print("- Clean HUD typography")
    print("- Minimalist mini-map")
    
    while running:
        dt = clock.tick(60) / 1000.0
        demo_time += dt
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen
        renderer.clear_screen()
        renderer.clear_ui_surface()
        
        # Demo 1: Draw track boundaries with checkered pattern
        boundary_points = [
            (50, 50), (750, 50), (750, 150), (50, 150)
        ]
        renderer.draw_track_boundary(boundary_points, width=30, use_checkered=True)
        
        # Demo 2: Draw tire barriers
        for i in range(10):
            x = 100 + i * 60
            y = 250
            renderer.draw_tire_barrier((x, y), 12)
        
        # Demo 3: Draw animated cars with different colors
        car_positions = [
            (200 + math.sin(demo_time) * 100, 350, renderer.colors.LIGHT_GRAY),
            (400 + math.cos(demo_time * 1.5) * 80, 380, renderer.colors.ACCENT_RED),
            (600 + math.sin(demo_time * 0.8) * 60, 320, renderer.colors.WHITE)
        ]
        
        for i, (x, y, color) in enumerate(car_positions):
            angle = demo_time * 50 + i * 45  # Rotating cars
            renderer.draw_car((x, y), angle, color)
        
        # Demo 4: Draw checkered pattern area
        checkered_rect = pygame.Rect(50, 450, 200, 100)
        renderer.draw_checkered_pattern(checkered_rect, 12)
        
        # Demo 5: HUD elements
        renderer.draw_hud_text("Black Mamba Racer Demo", (20, 20), "large", renderer.colors.HUD_ACCENT)
        renderer.draw_hud_text(f"Time: {demo_time:.1f}s", (20, 70), "medium")
        renderer.draw_hud_text("Lap: 1/3", (20, 100), "medium")
        renderer.draw_hud_text("Position: 2nd", (20, 130), "medium")
        renderer.draw_hud_text("Speed: 85 mph", (20, 160), "small")
        
        # Demo 6: Mini-map
        car_map_positions = [(pos[0], pos[1]) for pos in car_positions]
        renderer.draw_mini_map((640, 20), (140, 100), track_points, car_map_positions)
        
        # Demo 7: Color palette showcase
        palette_y = 200
        colors_to_show = [
            ("Background", renderer.colors.BACKGROUND_GRAY),
            ("Track", renderer.colors.TRACK_GRAY),
            ("Light Gray", renderer.colors.LIGHT_GRAY),
            ("White", renderer.colors.WHITE),
            ("Accent Red", renderer.colors.ACCENT_RED),
            ("Accent Yellow", renderer.colors.ACCENT_YELLOW),
        ]
        
        for i, (name, color) in enumerate(colors_to_show):
            x = 500 + (i % 3) * 90
            y = palette_y + (i // 3) * 40
            pygame.draw.rect(renderer.get_screen_surface(), color, (x, y, 30, 20))
            renderer.draw_hud_text(name, (x, y + 25), "small")
        
        # Present the frame
        renderer.present()
    
    pygame.quit()
    print("Demo completed!")


if __name__ == "__main__":
    main()