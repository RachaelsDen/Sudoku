# SPDX-License-Identifier: GPL-3.0-or-later

import importlib
import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def _module_cleanup():
    yield
    sys.modules.pop("src.log_utils", None)
    sys.modules.pop("src.screens.preferences_page", None)
    sys.modules.pop("gi", None)
    sys.modules.pop("gi.repository", None)
    sys.modules.pop("gi.repository.Gtk", None)
    sys.modules.pop("gi.repository.Adw", None)


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


def _import_preferences_page_module():
    sys.modules.pop("src.screens.preferences_page", None)
    return importlib.import_module("src.screens.preferences_page")


def _install_fake_log_utils() -> MagicMock:
    fake = ModuleType("src.log_utils")
    fake.log_preference_change = MagicMock()
    sys.modules["src.log_utils"] = fake
    return fake.log_preference_change


def test_general_preferences_toggle_logs_change_and_saves():
    _install_fake_gi()
    mock_log_preference_change = _install_fake_log_utils()
    module = _import_preferences_page_module()

    page = module.GeneralPreferencesPage.__new__(module.GeneralPreferencesPage)
    page.general_preferences = {"highlight_row": True}
    page.auto_save_function = MagicMock()

    switch = MagicMock()
    switch.get_active.return_value = False

    page.on_toggle_changed(switch, None, "highlight_row")

    mock_log_preference_change.assert_called_once_with(
        "general", "highlight_row", False
    )
    page.auto_save_function.assert_called_once()


def test_variant_preferences_toggle_logs_change_and_saves():
    _install_fake_gi()
    mock_log_preference_change = _install_fake_log_utils()
    module = _import_preferences_page_module()

    page = module.VariantPreferencesPage.__new__(module.VariantPreferencesPage)
    page.variant_preferences = {"highlight_block": True}
    page.auto_save_function = MagicMock()

    switch = MagicMock()
    switch.get_active.return_value = False

    page.on_toggle_changed(switch, None, "highlight_block")

    mock_log_preference_change.assert_called_once_with(
        "variant", "highlight_block", False
    )
    page.auto_save_function.assert_called_once()
