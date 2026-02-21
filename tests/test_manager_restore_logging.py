import logging
import os
import sys
from unittest.mock import MagicMock, patch

sys.modules["gi"] = MagicMock()
sys.modules["gi.repository"] = MagicMock()

import pytest

from src.base.preferences_manager import PreferencesManager
from src.base.manager_base import ManagerBase
from src.variants.classic_sudoku.board import ClassicSudokuBoard
from src.window import SudokuWindow


class _DummyPreferences:
    def __init__(self):
        self.variant_defaults = {}
        self.general_defaults = {}

    def general(self, _key, default=None):
        return default


_dummy_prefs = _DummyPreferences()


@pytest.fixture(autouse=True)
def _prefs_guard():
    PreferencesManager.set_preferences(_dummy_prefs)
    try:
        yield
    finally:
        PreferencesManager.set_preferences(None)


@pytest.fixture(autouse=True)
def _cleanup_save_file():
    """Clean up save file before and after each test."""
    save_path = ClassicSudokuBoard.DEFAULT_SAVE_PATH
    if os.path.exists(save_path):
        os.remove(save_path)
    try:
        yield
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)


@pytest.fixture
def manager():
    mock_window = MagicMock()
    mock_window.sudoku_window_title = MagicMock()
    mock_window.stack = MagicMock()
    mock_window.game_scrolled_window = MagicMock()
    mock_window.stack.set_visible_child = MagicMock()
    return ManagerBase(mock_window, ClassicSudokuBoard)


def _make_deterministic_board():
    puzzle = [[None] * 9 for _ in range(9)]
    solution = [[str((i * 9 + j + 1) % 9 + 1) for j in range(9)] for i in range(9)]

    with patch(
        "src.variants.classic_sudoku.generator.ClassicSudokuGenerator.generate",
        return_value=(puzzle, solution),
    ):
        return ClassicSudokuBoard(0.5, "Medium", "classic")


def test_no_save_found_logs_path_and_exists(manager, caplog):
    with caplog.at_level(logging.ERROR, logger="src.base.manager_base"):
        with patch.object(ManagerBase, "_restore_game_state"):
            manager.load_saved_game()

    error_records = [
        r
        for r in caplog.records
        if r.name == "src.base.manager_base" and r.levelno == logging.ERROR
    ]
    assert len(error_records) == 1

    message = error_records[0].getMessage()
    assert "No saved game found" in message
    assert "path=" in message
    assert "exists=" in message


def test_restore_success_logs_summary(manager, tmp_path, caplog):
    board = _make_deterministic_board()
    board.user_inputs[0][0] = "1"
    board.user_inputs[1][1] = "2"

    mock_window = MagicMock()
    mock_window.sudoku_window_title = MagicMock()
    mock_window.stack = MagicMock()
    mock_window.game_scrolled_window = MagicMock()
    mock_window.stack.set_visible_child = MagicMock()

    manager.window = mock_window

    # Mock load_from_file to return our board with user inputs
    with patch.object(ClassicSudokuBoard, "load_from_file", return_value=board):
        with patch.object(ManagerBase, "_restore_game_state"):
            with caplog.at_level(logging.INFO, logger="src.base.manager_base"):
                manager.load_saved_game()

    info_records = [
        r
        for r in caplog.records
        if r.name == "src.base.manager_base" and r.levelno == logging.INFO
    ]
    assert len(info_records) == 1

    message = info_records[0].getMessage()
    assert "Restored" in message
    assert "filled_cells=" in message
    assert "notes=" in message
    assert "filled_cells=2" in message


def test_no_save_found_when_file_does_not_exist(manager, caplog):
    with caplog.at_level(logging.ERROR, logger="src.base.manager_base"):
        with patch.object(ManagerBase, "_restore_game_state"):
            manager.load_saved_game()

    error_records = [
        r
        for r in caplog.records
        if r.name == "src.base.manager_base" and r.levelno == logging.ERROR
    ]
    assert len(error_records) == 1

    message = error_records[0].getMessage()
    assert "exists=False" in message


def test_no_save_found_when_file_exists_but_is_empty(manager, caplog):
    save_path = ClassicSudokuBoard.DEFAULT_SAVE_PATH
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write("{}")

    try:
        assert os.path.exists(save_path)

        with patch.object(ManagerBase, "_restore_game_state"):
            with patch.object(ClassicSudokuBoard, "load_from_file", return_value=None):
                with caplog.at_level(logging.INFO, logger="src.base.manager_base"):
                    manager.load_saved_game()

        error_records = [
            r
            for r in caplog.records
            if r.name == "src.base.manager_base" and r.levelno == logging.ERROR
        ]
        assert len(error_records) == 1

        message = error_records[0].getMessage()
        assert "exists=True" in message
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)
