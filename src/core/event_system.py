"""
Event System - Event handling and messaging system.

This module provides utilities for handling pygame events and
implementing a custom event messaging system for game components.
"""

import pygame
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass


class GameEventType(Enum):
    """Custom game event types beyond pygame events."""

    SCENE_CHANGE_REQUESTED = "scene_change_requested"
    CAR_COLLISION = "car_collision"
    LAP_COMPLETED = "lap_completed"
    RACE_FINISHED = "race_finished"
    TRACK_LOADED = "track_loaded"
    PHYSICS_MODEL_CHANGED = "physics_model_changed"


@dataclass
class GameEvent:
    """
    Custom game event data structure.

    This allows for game-specific events beyond pygame's event system.
    """

    event_type: GameEventType
    data: Dict[str, Any]
    timestamp: float
    source: Optional[str] = None


class EventSystem:
    """
    Event handling and messaging system for the game.

    This class manages both pygame events and custom game events,
    providing a centralized event handling mechanism.
    """

    def __init__(self) -> None:
        """Initialize the event system."""
        # Pygame event handlers
        self.pygame_handlers: Dict[int, List[Callable]] = {}

        # Custom game event handlers
        self.game_event_handlers: Dict[GameEventType, List[Callable]] = {}

        # Event queue for custom events
        self.event_queue: List[GameEvent] = []

        # Event statistics
        self.events_processed = 0

    def register_pygame_handler(
        self, event_type: int, handler: Callable[[pygame.event.Event], None]
    ) -> None:
        """
        Register a handler for pygame events.

        Args:
            event_type: pygame event type constant (e.g., pygame.KEYDOWN)
            handler: Function to call when this event occurs
        """
        if event_type not in self.pygame_handlers:
            self.pygame_handlers[event_type] = []
        self.pygame_handlers[event_type].append(handler)

    def register_game_event_handler(
        self, event_type: GameEventType, handler: Callable[[GameEvent], None]
    ) -> None:
        """
        Register a handler for custom game events.

        Args:
            event_type: Custom game event type
            handler: Function to call when this event occurs
        """
        if event_type not in self.game_event_handlers:
            self.game_event_handlers[event_type] = []
        self.game_event_handlers[event_type].append(handler)

    def unregister_pygame_handler(self, event_type: int, handler: Callable) -> bool:
        """
        Unregister a pygame event handler.

        Args:
            event_type: pygame event type constant
            handler: Handler function to remove

        Returns:
            bool: True if handler was found and removed, False otherwise
        """
        if event_type in self.pygame_handlers:
            try:
                self.pygame_handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False

    def unregister_game_event_handler(
        self, event_type: GameEventType, handler: Callable
    ) -> bool:
        """
        Unregister a custom game event handler.

        Args:
            event_type: Custom game event type
            handler: Handler function to remove

        Returns:
            bool: True if handler was found and removed, False otherwise
        """
        if event_type in self.game_event_handlers:
            try:
                self.game_event_handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False

    def post_game_event(
        self,
        event_type: GameEventType,
        data: Dict[str, Any],
        source: Optional[str] = None,
    ) -> None:
        """
        Post a custom game event to the event queue.

        Args:
            event_type: Type of game event
            data: Event data dictionary
            source: Optional source identifier for the event
        """
        event = GameEvent(
            event_type=event_type,
            data=data,
            timestamp=pygame.time.get_ticks() / 1000.0,
            source=source,
        )
        self.event_queue.append(event)

    def process_pygame_events(self) -> List[pygame.event.Event]:
        """
        Process all pygame events and dispatch to registered handlers.

        Returns:
            List[pygame.event.Event]: List of all pygame events processed
        """
        events = pygame.event.get()

        for event in events:
            # Dispatch to registered handlers
            if event.type in self.pygame_handlers:
                for handler in self.pygame_handlers[event.type]:
                    try:
                        handler(event)
                    except Exception as e:
                        print(f"Error in pygame event handler: {e}")

            self.events_processed += 1

        return events

    def process_game_events(self) -> None:
        """Process all custom game events in the queue."""
        while self.event_queue:
            event = self.event_queue.pop(0)

            # Dispatch to registered handlers
            if event.event_type in self.game_event_handlers:
                for handler in self.game_event_handlers[event.event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        print(f"Error in game event handler: {e}")

            self.events_processed += 1

    def clear_event_queue(self) -> None:
        """Clear all pending custom game events."""
        self.event_queue.clear()

    def get_events_processed(self) -> int:
        """
        Get the total number of events processed.

        Returns:
            int: Total events processed since initialization
        """
        return self.events_processed


class InputManager:
    """
    Input management system for handling keyboard and mouse input.

    This class provides utilities for checking input states and
    managing input mappings for the game.
    """

    def __init__(self) -> None:
        """Initialize the input manager."""
        self.keys_pressed: set[int] = set()
        self.keys_just_pressed: set[int] = set()
        self.keys_just_released: set[int] = set()

        self.mouse_pos = (0, 0)
        self.mouse_buttons: set[int] = set()
        self.mouse_just_pressed: set[int] = set()
        self.mouse_just_released: set[int] = set()

    def update(self, events: List[pygame.event.Event]) -> None:
        """
        Update input state based on pygame events.

        Args:
            events: List of pygame events to process
        """
        # Clear frame-specific input states
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_just_pressed.clear()
        self.mouse_just_released.clear()

        # Process events
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.keys_just_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                self.keys_just_released.add(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons.add(event.button)
                self.mouse_just_pressed.add(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons.discard(event.button)
                self.mouse_just_released.add(event.button)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

    def is_key_pressed(self, key: int) -> bool:
        """
        Check if a key is currently pressed.

        Args:
            key: pygame key constant

        Returns:
            bool: True if key is currently pressed
        """
        return key in self.keys_pressed

    def is_key_just_pressed(self, key: int) -> bool:
        """
        Check if a key was just pressed this frame.

        Args:
            key: pygame key constant

        Returns:
            bool: True if key was just pressed
        """
        return key in self.keys_just_pressed

    def is_key_just_released(self, key: int) -> bool:
        """
        Check if a key was just released this frame.

        Args:
            key: pygame key constant

        Returns:
            bool: True if key was just released
        """
        return key in self.keys_just_released

    def is_mouse_button_pressed(self, button: int) -> bool:
        """
        Check if a mouse button is currently pressed.

        Args:
            button: pygame mouse button constant

        Returns:
            bool: True if mouse button is currently pressed
        """
        return button in self.mouse_buttons

    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """
        Check if a mouse button was just pressed this frame.

        Args:
            button: pygame mouse button constant

        Returns:
            bool: True if mouse button was just pressed
        """
        return button in self.mouse_just_pressed

    def get_mouse_position(self) -> tuple[int, int]:
        """
        Get the current mouse position.

        Returns:
            tuple[int, int]: Mouse position (x, y)
        """
        return self.mouse_pos
