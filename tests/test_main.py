"""Tests for the main game application."""

import pytest
from unittest.mock import patch, MagicMock
from src.main import main
from src.core.game_engine import GameEngine, GameConfig, GameScene
from src.core.scene_manager import MenuScene


class TestGameEngine:
    """Test cases for the GameEngine integration."""

    def test_game_config_creation(self):
        """Test GameConfig creation with default values."""
        config = GameConfig()
        assert config.window_width == 1024
        assert config.window_height == 768
        assert config.target_fps == 60
        assert config.window_title == "Retro Racing Game"

    @patch("pygame.init")
    @patch("pygame.display.set_mode")
    @patch("pygame.display.set_caption")
    @patch("pygame.time.Clock")
    @patch("pygame.time.get_ticks")
    def test_game_engine_initialization(
        self, mock_get_ticks, mock_clock, mock_caption, mock_set_mode, mock_init
    ):
        """Test GameEngine initialization."""
        mock_surface = MagicMock()
        mock_set_mode.return_value = mock_surface
        mock_clock_instance = MagicMock()
        mock_clock.return_value = mock_clock_instance
        mock_get_ticks.return_value = 0

        config = GameConfig()
        engine = GameEngine(config)
        result = engine.initialize()

        assert result is True
        assert engine.screen == mock_surface
        assert engine.clock == mock_clock_instance
        mock_init.assert_called_once()
        mock_set_mode.assert_called_once_with((1024, 768))
        mock_caption.assert_called_once_with("Retro Racing Game")

    def test_scene_registration(self):
        """Test scene registration functionality."""
        config = GameConfig()
        engine = GameEngine(config)
        menu_scene = MenuScene()

        engine.register_scene(GameScene.MENU, menu_scene)

        assert GameScene.MENU in engine.scenes
        assert engine.scenes[GameScene.MENU] == menu_scene

    def test_scene_change_request(self):
        """Test scene change request functionality."""
        config = GameConfig()
        engine = GameEngine(config)

        engine.change_scene(GameScene.RACE)

        assert engine.next_scene == GameScene.RACE
        assert engine.scene_transition_requested is True


def test_main_function():
    """Test the main function entry point."""
    with patch("src.main.GameEngine") as mock_engine_class:
        mock_engine = MagicMock()
        mock_engine_class.return_value = mock_engine

        result = main()

        assert result == 0
        mock_engine.run.assert_called_once()
        mock_engine.cleanup.assert_called_once()
        # Verify scenes were registered
        assert mock_engine.register_scene.call_count == 4


def test_main_function_with_exception():
    """Test main function handles exceptions properly."""
    with patch("src.main.GameEngine") as mock_engine_class:
        mock_engine_class.side_effect = Exception("Test error")

        with patch("builtins.print"):  # Suppress error output during test
            result = main()

        assert result == 1
