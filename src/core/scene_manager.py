"""
Scene Manager - Manages different game scenes and transitions.

This module provides base classes and utilities for managing game scenes
such as menu, race, and editor states.
"""

import pygame
from abc import ABC, abstractmethod
from typing import Optional


class Scene(ABC):
    """
    Abstract base class for all game scenes.

    All scenes (menu, race, editor) should inherit from this class
    and implement the required methods.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the scene.

        Args:
            name: Human-readable name for this scene
        """
        self.name = name
        self.active = False

    def enter(self) -> None:
        """
        Called when entering this scene.

        Override this method to perform scene initialization,
        load resources, or set up scene-specific state.
        """
        self.active = True
        print(f"Entering scene: {self.name}")

    def exit(self) -> None:
        """
        Called when exiting this scene.

        Override this method to perform cleanup, save state,
        or release scene-specific resources.
        """
        self.active = False
        print(f"Exiting scene: {self.name}")

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """
        Update the scene logic.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the scene to the screen.

        Args:
            screen: Pygame surface to render to
        """
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events for this scene.

        Args:
            event: Pygame event to handle
        """
        pass


class MenuScene(Scene):
    """
    Basic menu scene implementation.

    This is a placeholder implementation that will be expanded
    in future tasks with proper menu functionality.
    """

    def __init__(self) -> None:
        super().__init__("Menu")
        self.menu_items = ["Start Race", "Track Editor", "Settings", "Quit"]
        self.selected_item = 0

    def update(self, delta_time: float) -> None:
        """Update menu logic."""
        pass

    def render(self, screen: pygame.Surface) -> None:
        """Render the menu scene."""
        # Get screen dimensions
        width, height = screen.get_size()

        # Render title
        font_title = pygame.font.Font(None, 72)
        title_text = font_title.render("RETRO RACING", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, height // 4))
        screen.blit(title_text, title_rect)

        # Render menu items
        font_menu = pygame.font.Font(None, 36)
        start_y = height // 2

        for i, item in enumerate(self.menu_items):
            color = (255, 255, 0) if i == self.selected_item else (200, 200, 200)
            text = font_menu.render(item, True, color)
            text_rect = text.get_rect(center=(width // 2, start_y + i * 50))
            screen.blit(text, text_rect)

        # Render instructions
        font_small = pygame.font.Font(None, 24)
        instructions = font_small.render(
            "Use UP/DOWN arrows to navigate, ENTER to select", True, (150, 150, 150)
        )
        inst_rect = instructions.get_rect(center=(width // 2, height - 50))
        screen.blit(instructions, inst_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle menu-specific events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                self._handle_menu_selection()

    def _handle_menu_selection(self) -> None:
        """Handle menu item selection."""
        selected = self.menu_items[self.selected_item]
        print(f"Menu selection: {selected}")
        # Menu actions will be implemented in future tasks


class RaceScene(Scene):
    """
    Basic race scene implementation.

    This is a placeholder implementation that will be expanded
    in future tasks with proper racing functionality.
    """

    def __init__(self) -> None:
        super().__init__("Race")

    def update(self, delta_time: float) -> None:
        """Update race logic."""
        pass

    def render(self, screen: pygame.Surface) -> None:
        """Render the race scene."""
        width, height = screen.get_size()

        # Render race placeholder
        font = pygame.font.Font(None, 48)
        text = font.render("RACE SCENE", True, (255, 255, 255))
        text_rect = text.get_rect(center=(width // 2, height // 2 - 50))
        screen.blit(text, text_rect)

        # Render instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "Race implementation coming soon...",
            "Press ESC to return to menu",
        ]

        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(center=(width // 2, height // 2 + 20 + i * 30))
            screen.blit(text, text_rect)


class EditorScene(Scene):
    """
    Basic editor scene implementation.

    This is a placeholder implementation that will be expanded
    in future tasks with proper track editor functionality.
    """

    def __init__(self) -> None:
        super().__init__("Editor")

    def update(self, delta_time: float) -> None:
        """Update editor logic."""
        pass

    def render(self, screen: pygame.Surface) -> None:
        """Render the editor scene."""
        width, height = screen.get_size()

        # Render editor placeholder
        font = pygame.font.Font(None, 48)
        text = font.render("TRACK EDITOR", True, (255, 255, 255))
        text_rect = text.get_rect(center=(width // 2, height // 2 - 50))
        screen.blit(text, text_rect)

        # Render instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "Track editor implementation coming soon...",
            "Press ESC to return to menu",
        ]

        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(center=(width // 2, height // 2 + 20 + i * 30))
            screen.blit(text, text_rect)


class SettingsScene(Scene):
    """
    Basic settings scene implementation.

    This is a placeholder implementation for game settings.
    """

    def __init__(self) -> None:
        super().__init__("Settings")

    def update(self, delta_time: float) -> None:
        """Update settings logic."""
        pass

    def render(self, screen: pygame.Surface) -> None:
        """Render the settings scene."""
        width, height = screen.get_size()

        # Render settings placeholder
        font = pygame.font.Font(None, 48)
        text = font.render("SETTINGS", True, (255, 255, 255))
        text_rect = text.get_rect(center=(width // 2, height // 2 - 50))
        screen.blit(text, text_rect)

        # Render instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "Settings implementation coming soon...",
            "Press ESC to return to menu",
        ]

        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(center=(width // 2, height // 2 + 20 + i * 30))
            screen.blit(text, text_rect)
