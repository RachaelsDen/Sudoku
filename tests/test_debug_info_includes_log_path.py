# SPDX-License-Identifier: GPL-3.0-or-later

import importlib
import logging
import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from src.base.log_paths import get_log_file_path
import src.log_utils as log_utils_module


@pytest.fixture(autouse=True)
def _module_cleanup():
    yield
    sys.modules.pop("src.application", None)
    sys.modules.pop("src.window", None)
    sys.modules.pop("src.screens.about_dialog", None)
    sys.modules.pop("src.screens.help_dialog", None)
    sys.modules.pop("gi", None)
    sys.modules.pop("gi.repository", None)
    sys.modules.pop("gi.repository.Gtk", None)
    sys.modules.pop("gi.repository.Adw", None)
    sys.modules.pop("gi.repository.Gio", None)
    sys.modules.pop("gi.repository.GLib", None)


@pytest.fixture(autouse=True)
def _logging_guard():
    log_utils_module._logging_configured = False
    log_utils_module._log_buffer_handler = None
    log_utils_module._session_id = None

    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    yield


def _install_fake_application_imports(monkeypatch) -> None:
    gi = ModuleType("gi")
    repository = ModuleType("gi.repository")

    Gtk = ModuleType("Gtk")
    Gtk.MAJOR_VERSION = 4
    Gtk.MINOR_VERSION = 14
    Gtk.MICRO_VERSION = 0

    Adw = ModuleType("Adw")
    Adw.MAJOR_VERSION = 1
    Adw.MINOR_VERSION = 6
    Adw.MICRO_VERSION = 0
    Adw.Application = type("Application", (), {})

    Gio = ModuleType("Gio")
    Gio.ApplicationFlags = type("ApplicationFlags", (), {"FLAGS_NONE": 0})

    GLib = ModuleType("GLib")

    repository.Gtk = Gtk
    repository.Adw = Adw
    repository.Gio = Gio
    repository.GLib = GLib

    gi.require_version = lambda *_args: None
    gi.repository = repository
    gi.version_info = (3, 48, 2)

    monkeypatch.setitem(sys.modules, "gi", gi)
    monkeypatch.setitem(sys.modules, "gi.repository", repository)
    monkeypatch.setitem(sys.modules, "gi.repository.Gtk", Gtk)
    monkeypatch.setitem(sys.modules, "gi.repository.Adw", Adw)
    monkeypatch.setitem(sys.modules, "gi.repository.Gio", Gio)
    monkeypatch.setitem(sys.modules, "gi.repository.GLib", GLib)

    window_module = ModuleType("src.window")
    window_module.SudokuWindow = type("SudokuWindow", (), {})
    monkeypatch.setitem(sys.modules, "src.window", window_module)

    about_module = ModuleType("src.screens.about_dialog")
    about_module.SudokuAboutDialog = type("SudokuAboutDialog", (), {})
    monkeypatch.setitem(sys.modules, "src.screens.about_dialog", about_module)

    help_module = ModuleType("src.screens.help_dialog")
    help_module.HowToPlayDialog = type("HowToPlayDialog", (), {})
    monkeypatch.setitem(sys.modules, "src.screens.help_dialog", help_module)


def _import_application_module(monkeypatch):
    _install_fake_application_imports(monkeypatch)
    sys.modules.pop("src.application", None)
    return importlib.import_module("src.application")


def _make_application_instance(application_module):
    app = application_module.SudokuApplication.__new__(
        application_module.SudokuApplication
    )
    app.version = "1.0.0"
    app.log_handler = MagicMock()
    app.log_handler.get_logs.return_value = "Test log message\n"
    return app


def test_generate_debug_info_includes_log_file_path(monkeypatch):
    application_module = _import_application_module(monkeypatch)
    app = _make_application_instance(application_module)

    monkeypatch.setattr(application_module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        application_module.platform,
        "freedesktop_os_release",
        lambda: {"PRETTY_NAME": "Ubuntu 24.04"},
    )

    debug_info = app.generate_debug_info()

    assert "Log File:" in debug_info
    assert get_log_file_path() in debug_info


def test_generate_debug_info_includes_log_level(monkeypatch):
    application_module = _import_application_module(monkeypatch)
    app = _make_application_instance(application_module)

    monkeypatch.setattr(application_module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        application_module.platform,
        "freedesktop_os_release",
        lambda: {"PRETTY_NAME": "Ubuntu 24.04"},
    )

    debug_info = app.generate_debug_info()

    assert "Log Level:" in debug_info
    assert "Log Level: INFO" in debug_info


def test_generate_debug_info_format(monkeypatch):
    application_module = _import_application_module(monkeypatch)
    app = _make_application_instance(application_module)

    monkeypatch.setattr(application_module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        application_module.platform,
        "freedesktop_os_release",
        lambda: {"PRETTY_NAME": "Ubuntu 24.04"},
    )

    debug_info = app.generate_debug_info()

    log_file_line = f"Log File: {get_log_file_path()}"
    log_level_line = "Log Level:"

    assert log_file_line in debug_info
    assert log_level_line in debug_info

    logs_section = "--- Logs ---"
    assert debug_info.find(log_file_line) < debug_info.find(logs_section)
    assert debug_info.find(log_level_line) < debug_info.find(logs_section)
