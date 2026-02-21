# SPDX-License-Identifier: GPL-3.0-or-later

import importlib
import json
import logging
import sys
from types import ModuleType


def _install_fake_gi(monkeypatch) -> None:
    gi = ModuleType("gi")
    repository = ModuleType("gi.repository")

    Gtk = ModuleType("Gtk")

    class _Template:
        def __init__(self, resource_path=None):
            self.resource_path = resource_path

        def __call__(self, cls):
            return cls

        class Child:
            def __init__(self, *args, **kwargs):
                pass

    Gtk.Template = _Template

    Adw = ModuleType("Adw")
    Adw.ApplicationWindow = type("ApplicationWindow", (), {})

    Gio = ModuleType("Gio")

    repository.Gtk = Gtk
    repository.Adw = Adw
    repository.Gio = Gio
    gi.repository = repository

    monkeypatch.setitem(sys.modules, "gi", gi)
    monkeypatch.setitem(sys.modules, "gi.repository", repository)
    monkeypatch.setitem(sys.modules, "gi.repository.Gtk", Gtk)
    monkeypatch.setitem(sys.modules, "gi.repository.Adw", Adw)
    monkeypatch.setitem(sys.modules, "gi.repository.Gio", Gio)


def _install_fake_window_imports(monkeypatch) -> None:
    def _stub_module(module_name: str, **attrs) -> None:
        mod = ModuleType(module_name)
        for k, v in attrs.items():
            setattr(mod, k, v)
        monkeypatch.setitem(sys.modules, module_name, mod)

    _stub_module(
        "src.screens.game_setup_dialog",
        GameSetupDialog=type("GameSetupDialog", (), {}),
    )
    _stub_module(
        "src.screens.shortcuts_overlay",
        ShortcutsOverlay=type("ShortcutsOverlay", (), {}),
    )
    _stub_module(
        "src.screens.finished_page",
        FinishedPage=type("FinishedPage", (), {}),
    )
    _stub_module(
        "src.screens.loading_screen",
        LoadingScreen=type("LoadingScreen", (), {}),
    )
    _stub_module(
        "src.screens.preferences_dialog",
        PreferencesDialog=type("PreferencesDialog", (), {}),
    )

    _stub_module(
        "src.variants.classic_sudoku.manager",
        ClassicSudokuManager=type("ClassicSudokuManager", (), {}),
    )
    _stub_module(
        "src.variants.classic_sudoku.preferences",
        ClassicSudokuPreferences=type("ClassicSudokuPreferences", (), {}),
    )
    _stub_module(
        "src.variants.diagonal_sudoku.manager",
        DiagonalSudokuManager=type("DiagonalSudokuManager", (), {}),
    )
    _stub_module(
        "src.variants.diagonal_sudoku.preferences",
        DiagonalSudokuPreferences=type("DiagonalSudokuPreferences", (), {}),
    )

    class PreferencesManager:
        @staticmethod
        def set_preferences(_prefs) -> None:
            return None

    _stub_module("src.base.preferences_manager", PreferencesManager=PreferencesManager)


def _import_window_module(monkeypatch):
    _install_fake_gi(monkeypatch)
    _install_fake_window_imports(monkeypatch)
    sys.modules.pop("src.window", None)
    return importlib.import_module("src.window")


def test_get_manager_type_returns_none_when_save_missing(monkeypatch, tmp_path):
    window_module = _import_window_module(monkeypatch)
    SudokuWindow = window_module.SudokuWindow

    win = SudokuWindow.__new__(SudokuWindow)
    win.logger = logging.getLogger("src.window")

    missing = tmp_path / "missing.json"
    assert win.get_manager_type(str(missing)) is None


def test_get_manager_type_returns_variant_from_metadata(monkeypatch, tmp_path):
    window_module = _import_window_module(monkeypatch)
    SudokuWindow = window_module.SudokuWindow

    win = SudokuWindow.__new__(SudokuWindow)
    win.logger = logging.getLogger("src.window")

    path = tmp_path / "board.json"
    path.write_text(json.dumps({"variant": "classic"}), encoding="utf-8")
    assert win.get_manager_type(str(path)) == "classic"


def test_get_manager_type_defaults_unknown_when_variant_missing(monkeypatch, tmp_path):
    window_module = _import_window_module(monkeypatch)
    SudokuWindow = window_module.SudokuWindow

    win = SudokuWindow.__new__(SudokuWindow)
    win.logger = logging.getLogger("src.window")

    path = tmp_path / "board.json"
    path.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
    assert win.get_manager_type(str(path)) == "Unknown"


def test_get_manager_type_logs_error_when_metadata_invalid_json(
    monkeypatch, tmp_path, caplog
):
    window_module = _import_window_module(monkeypatch)
    SudokuWindow = window_module.SudokuWindow

    win = SudokuWindow.__new__(SudokuWindow)
    win.logger = logging.getLogger("src.window")

    path = tmp_path / "board.json"
    path.write_text("{not-json", encoding="utf-8")

    with caplog.at_level(logging.ERROR, logger="src.window"):
        assert win.get_manager_type(str(path)) is None

    assert "Failed to read saved-game metadata" in caplog.text
    assert any(rec.exc_info is not None for rec in caplog.records)
