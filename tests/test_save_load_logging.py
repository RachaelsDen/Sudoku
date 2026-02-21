import json
import logging
import sys
from unittest.mock import MagicMock, patch

sys.modules["gi"] = MagicMock()
sys.modules["gi.repository"] = MagicMock()
sys.modules["gi.repository.Gtk"] = MagicMock()
sys.modules["gi.repository.Gdk"] = MagicMock()
sys.modules["gi.repository.GLib"] = MagicMock()
sys.modules["gi.repository.Adw"] = MagicMock()

import pytest

from src.base.preferences_manager import PreferencesManager
from src.variants.classic_sudoku.board import ClassicSudokuBoard


class _DummyPreferences:
    def __init__(self):
        self.variant_defaults = {}
        self.general_defaults = {}

    def general(self, _key, default=None):
        return default


def _prefs_guard_impl():
    PreferencesManager.set_preferences(_DummyPreferences())
    try:
        yield
    finally:
        PreferencesManager.set_preferences(None)


_prefs_guard = pytest.fixture(autouse=True)(_prefs_guard_impl)


def _make_deterministic_board():
    puzzle = [[None] * 9 for _ in range(9)]
    solution = [[str((i * 9 + j + 1) % 9 + 1) for j in range(9)] for i in range(9)]
    with patch(
        "src.variants.classic_sudoku.generator.ClassicSudokuGenerator.generate",
        return_value=(puzzle, solution),
    ):
        return ClassicSudokuBoard(0.5, "Medium", "classic")


class TestBoardSaveLoadLogging:
    def test_save_emits_info_log_with_path_and_duration(self, tmp_path, caplog):
        board = _make_deterministic_board()
        save_file = tmp_path / "save.json"

        with caplog.at_level(logging.INFO, logger="src.base.board_base"):
            board.save_to_file(str(save_file))

        messages = [r.getMessage() for r in caplog.records]
        assert any(
            "board_save_success" in m
            and str(save_file) in m
            and "duration_ms=" in m
            for m in messages
        )

    def test_corrupt_json_load_emits_one_error_log_with_path_and_exc_info(
        self, tmp_path, caplog
    ):
        save_file = tmp_path / "corrupt.json"
        save_file.write_text("{not valid json", encoding="utf-8")

        with caplog.at_level(logging.INFO, logger="src.base.board_base"):
            with pytest.raises(json.JSONDecodeError):
                ClassicSudokuBoard.load_from_file(str(save_file))

        error_records = [
            r
            for r in caplog.records
            if r.name == "src.base.board_base" and r.levelno == logging.ERROR
        ]
        assert len(error_records) == 1
        assert str(save_file) in error_records[0].getMessage()
        assert error_records[0].exc_info is not None
