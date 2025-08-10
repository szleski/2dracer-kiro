#!/usr/bin/env python3
"""
Retro Racing Game - Main Entry Point

A top-down 2D racing game with retro aesthetics featuring:
- Physics-based car simulation with Pymunk
- AI opponents with multiple difficulty levels
- Track editor for custom track creation
- Retro visual and audio styling
"""

import sys
from src.core.game_engine import GameEngine, GameConfig, GameScene
from src.core.scene_manager import MenuScene, RaceScene, EditorScene, SettingsScene


def main() -> int:
    """
    Main entry point for the retro racing game.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Create game configuration
        config = GameConfig(
            window_width=1024,
            window_height=768,
            window_title="Retro Racing Game",
            target_fps=60,
            background_color=(32, 32, 32),  # Dark gray retro background
        )

        # Create game engine
        engine = GameEngine(config)

        # Register scenes
        engine.register_scene(GameScene.MENU, MenuScene())
        engine.register_scene(GameScene.RACE, RaceScene())
        engine.register_scene(GameScene.EDITOR, EditorScene())
        engine.register_scene(GameScene.SETTINGS, SettingsScene())

        # Run the game
        engine.run()
        engine.cleanup()

        return 0
    except Exception as e:
        print(f"Game crashed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
