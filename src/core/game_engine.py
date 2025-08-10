"""
Game Engine - Core game loop and coordination system.

This module provides the main GameEngine class that manages the game loop,
scene transitions, and event handling for the retro racing game.
"""

import pygame
from typing import Dict, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass


class GameScene(Enum):
    """Enumeration of available game scenes."""

    MENU = "menu"
    RACE = "race"
    EDITOR = "editor"
    SETTINGS = "settings"
    QUIT = "quit"


@dataclass
class GameConfig:
    """Configuration settings for the game engine."""

    window_width: int = 1024
    window_height: int = 768
    window_title: str = "Retro Racing Game"
    target_fps: int = 60
    background_color: tuple[int, int, int] = (32, 32, 32)  # Dark gray retro background


class GameEngine:
    """
    Main game engine that manages the game loop, scene management, and events.

    This class coordinates all game systems and provides a 60 FPS game loop
    with scene management capabilities for menu, race, and editor states.
    """

    def __init__(self, config: Optional[GameConfig] = None) -> None:
        """
        Initialize the game engine.

        Args:
            config: Game configuration settings. Uses defaults if None.
        """
        self.config = config or GameConfig()

        # Core pygame objects
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None

        # Game state
        self.running = False
        self.current_scene = GameScene.MENU
        self.next_scene: Optional[GameScene] = None

        # Scene management
        self.scenes: Dict[GameScene, Any] = {}
        self.scene_transition_requested = False

        # Event handling
        self.event_handlers: Dict[int, list] = {}

        # Performance tracking
        self.frame_count = 0
        self.delta_time = 0.0
        self.last_frame_time = 0.0

    def initialize(self) -> bool:
        """
        Initialize pygame and create the main game window.

        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Initialize pygame
            pygame.init()

            # Create the main window
            self.screen = pygame.display.set_mode(
                (self.config.window_width, self.config.window_height)
            )
            pygame.display.set_caption(self.config.window_title)

            # Initialize the game clock for 60 FPS control
            self.clock = pygame.time.Clock()

            # Initialize timing
            self.last_frame_time = pygame.time.get_ticks()

            print(
                f"GameEngine initialized - {self.config.window_width}x{self.config.window_height} @ {self.config.target_fps} FPS"
            )
            return True

        except Exception as e:
            print(f"Failed to initialize GameEngine: {e}")
            return False

    def register_scene(self, scene_type: GameScene, scene_object: Any) -> None:
        """
        Register a scene object for scene management.

        Args:
            scene_type: The type of scene to register
            scene_object: The scene object that handles this scene type
        """
        self.scenes[scene_type] = scene_object
        print(f"Registered scene: {scene_type.value}")

    def change_scene(self, new_scene: GameScene) -> None:
        """
        Request a scene change to occur at the end of the current frame.

        Args:
            new_scene: The scene to transition to
        """
        self.next_scene = new_scene
        self.scene_transition_requested = True
        print(
            f"Scene change requested: {self.current_scene.value} -> {new_scene.value}"
        )

    def add_event_handler(self, event_type: int, handler_func: Callable[[pygame.event.Event], None]) -> None:
        """
        Add an event handler for a specific pygame event type.

        Args:
            event_type: pygame event type constant (e.g., pygame.KEYDOWN)
            handler_func: Function to call when this event occurs
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler_func)

    def run(self) -> None:
        """
        Main game loop running at 60 FPS with scene management.

        This method implements the core game loop with proper timing,
        event handling, and scene management.
        """
        if not self.initialize():
            return

        self.running = True
        print("GameEngine started - entering main loop")

        while self.running:
            # Calculate delta time for frame-independent updates
            current_time = pygame.time.get_ticks()
            self.delta_time = (current_time - self.last_frame_time) / 1000.0
            self.last_frame_time = current_time

            # Handle pygame events
            self._handle_events()

            # Handle scene transitions
            if self.scene_transition_requested:
                self._perform_scene_transition()

            # Update current scene
            self._update_current_scene()

            # Render current scene
            self._render_current_scene()

            # Maintain 60 FPS
            if self.clock:
                self.clock.tick(self.config.target_fps)

            self.frame_count += 1

    def _handle_events(self) -> None:
        """Handle pygame events and dispatch to registered handlers."""
        for event in pygame.event.get():
            # Handle core engine events
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC key handling - return to menu or quit
                    if self.current_scene == GameScene.MENU:
                        self.quit()
                    else:
                        self.change_scene(GameScene.MENU)

            # Dispatch to registered event handlers
            if event.type in self.event_handlers:
                for handler in self.event_handlers[event.type]:
                    handler(event)

            # Pass event to current scene if it exists
            current_scene_obj = self.scenes.get(self.current_scene)
            if current_scene_obj and hasattr(current_scene_obj, "handle_event"):
                current_scene_obj.handle_event(event)

    def _perform_scene_transition(self) -> None:
        """Perform the requested scene transition."""
        if self.next_scene is None:
            return

        # Exit current scene
        current_scene_obj = self.scenes.get(self.current_scene)
        if current_scene_obj and hasattr(current_scene_obj, "exit"):
            current_scene_obj.exit()

        # Change to new scene
        old_scene = self.current_scene
        self.current_scene = self.next_scene

        # Handle quit scene
        if self.current_scene == GameScene.QUIT:
            self.quit()
            return

        # Enter new scene
        new_scene_obj = self.scenes.get(self.current_scene)
        if new_scene_obj and hasattr(new_scene_obj, "enter"):
            new_scene_obj.enter()

        print(
            f"Scene transition completed: {old_scene.value} -> {self.current_scene.value}"
        )

        # Reset transition flags
        self.scene_transition_requested = False
        self.next_scene = None

    def _update_current_scene(self) -> None:
        """Update the current scene."""
        current_scene_obj = self.scenes.get(self.current_scene)
        if current_scene_obj and hasattr(current_scene_obj, "update"):
            current_scene_obj.update(self.delta_time)

    def _render_current_scene(self) -> None:
        """Render the current scene."""
        if not self.screen:
            return

        # Clear screen with background color
        self.screen.fill(self.config.background_color)

        # Render current scene
        current_scene_obj = self.scenes.get(self.current_scene)
        if current_scene_obj and hasattr(current_scene_obj, "render"):
            current_scene_obj.render(self.screen)
        else:
            # Fallback rendering for unregistered scenes
            self._render_fallback_scene()

        # Update display
        pygame.display.flip()

    def _render_fallback_scene(self) -> None:
        """Render a fallback scene when no scene object is registered."""
        if not self.screen:
            return

        # Display scene name and basic info
        font = pygame.font.Font(None, 48)
        scene_text = font.render(
            f"{self.current_scene.value.upper()} SCENE", True, (255, 255, 255)
        )
        scene_rect = scene_text.get_rect(
            center=(self.config.window_width // 2, self.config.window_height // 2 - 50)
        )
        self.screen.blit(scene_text, scene_rect)

        # Display instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "Scene not implemented yet",
            "Press ESC to return to menu",
            f"FPS: {self.get_fps():.1f}",
        ]

        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(
                center=(
                    self.config.window_width // 2,
                    self.config.window_height // 2 + 20 + i * 30,
                )
            )
            self.screen.blit(text, text_rect)

    def get_fps(self) -> float:
        """
        Get the current frames per second.

        Returns:
            float: Current FPS, or 0 if clock is not initialized
        """
        if self.clock:
            return self.clock.get_fps()
        return 0.0

    def get_delta_time(self) -> float:
        """
        Get the time elapsed since the last frame in seconds.

        Returns:
            float: Delta time in seconds
        """
        return self.delta_time

    def quit(self) -> None:
        """Request the game engine to quit."""
        self.running = False
        print("GameEngine quit requested")

    def cleanup(self) -> None:
        """Clean up resources and quit pygame."""
        # Exit current scene
        current_scene_obj = self.scenes.get(self.current_scene)
        if current_scene_obj and hasattr(current_scene_obj, "exit"):
            current_scene_obj.exit()

        # Cleanup pygame
        pygame.quit()
        print("GameEngine cleanup completed")
