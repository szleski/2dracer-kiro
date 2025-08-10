"""Tests for the main game application."""

import pytest
from unittest.mock import patch, MagicMock
from src.main import GameApplication, main


class TestGameApplication:
    """Test cases for the GameApplication class."""

    def test_game_application_init(self):
        """Test GameApplication initialization."""
        game = GameApplication()
        assert game.screen is None
        assert game.clock is None
        assert game.running is False

    @patch("pygame.init")
    @patch("pygame.display.set_mode")
    @patch("pygame.display.set_caption")
    @patch("pygame.time.Clock")
    def test_initialize_success(
        self, mock_clock, mock_caption, mock_set_mode, mock_init
    ):
        """Test successful game initialization."""
        mock_surface = MagicMock()
        mock_set_mode.return_value = mock_surface
        mock_clock_instance = MagicMock()
        mock_clock.return_value = mock_clock_instance

        game = GameApplication()
        result = game.initialize()

        assert result is True
        assert game.screen == mock_surface
        assert game.clock == mock_clock_instance
        mock_init.assert_called_once()
        mock_set_mode.assert_called_once_with((1024, 768))
        mock_caption.assert_called_once_with("Retro Racing Game")

    @patch("pygame.init")
    def test_initialize_failure(self, mock_init):
        """Test game initialization failure."""
        mock_init.side_effect = Exception("Pygame init failed")

        game = GameApplication()

        # The initialize method should catch the exception and return False
        with patch("builtins.print"):  # Suppress error output during test
            result = game.initialize()

        assert result is False


def test_main_function():
    """Test the main function entry point."""
    with patch("src.main.GameApplication") as mock_game_class:
        mock_game = MagicMock()
        mock_game_class.return_value = mock_game

        result = main()

        assert result == 0
        mock_game.run.assert_called_once()
        mock_game.cleanup.assert_called_once()


def test_main_function_with_exception():
    """Test main function handles exceptions properly."""
    with patch("src.main.GameApplication") as mock_game_class:
        mock_game_class.side_effect = Exception("Test error")

        result = main()

        assert result == 1
