# Copyright 2026
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib
import sys
from types import ModuleType
from unittest.mock import MagicMock


def _install_fake_gi() -> None:
    gi = ModuleType("gi")
    repository = ModuleType("gi.repository")

    Gtk = ModuleType("Gtk")
    Gtk.Align = type("Align", (), {"CENTER": 0})
    Gtk.Switch = type("Switch", (), {})

    Adw = ModuleType("Adw")
    Adw.PreferencesGroup = type("PreferencesGroup", (), {})
    Adw.ActionRow = type("ActionRow", (), {})

    repository.Gtk = Gtk
    repository.Adw = Adw
    gi.repository = repository

    sys.modules["gi"] = gi
    sys.modules["gi.repository"] = repository
    sys.modules["gi.repository.Gtk"] = Gtk
    sys.modules["gi.repository.Adw"] = Adw


def _install_fake_log_utils(mock_set_debug_logging: MagicMock) -> None:
    fake = ModuleType("src.log_utils")
    fake.set_debug_logging = mock_set_debug_logging
    sys.modules["src.log_utils"] = fake


def _import_general_preferences_page():
    sys.modules.pop("src.screens.preferences_page", None)
    module = importlib.import_module("src.screens.preferences_page")
    return module.GeneralPreferencesPage


def test_debug_logging_toggle_enables_calls_set_debug_logging():
    mock_set_debug_logging = MagicMock()
    _install_fake_gi()
    _install_fake_log_utils(mock_set_debug_logging)

    GeneralPreferencesPage = _import_general_preferences_page()

    page = GeneralPreferencesPage.__new__(GeneralPreferencesPage)
    page.general_preferences = {"debug_logging": ["Enable verbose debug logging to file", False]}
    page.auto_save_function = MagicMock()

    switch = MagicMock()
    switch.get_active.return_value = True

    page.on_toggle_changed(switch, None, "debug_logging")

    assert page.general_preferences["debug_logging"][1] is True
    mock_set_debug_logging.assert_called_once_with(True)


def test_debug_logging_toggle_disables_calls_set_debug_logging():
    mock_set_debug_logging = MagicMock()
    _install_fake_gi()
    _install_fake_log_utils(mock_set_debug_logging)

    GeneralPreferencesPage = _import_general_preferences_page()

    page = GeneralPreferencesPage.__new__(GeneralPreferencesPage)
    page.general_preferences = {"debug_logging": ["Enable verbose debug logging to file", True]}
    page.auto_save_function = MagicMock()

    switch = MagicMock()
    switch.get_active.return_value = False

    page.on_toggle_changed(switch, None, "debug_logging")

    assert page.general_preferences["debug_logging"][1] is False
    mock_set_debug_logging.assert_called_once_with(False)
