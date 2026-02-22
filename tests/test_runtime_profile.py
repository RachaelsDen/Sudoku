# SPDX-License-Identifier: GPL-3.0-or-later

from src.base.runtime_profile import default_debug_logging_enabled


def test_default_debug_logging_enabled_uses_flatpak_devel_id(monkeypatch):
    monkeypatch.setenv("FLATPAK_ID", "io.github.sepehr_rs.Sudoku.Devel")
    monkeypatch.delenv("SUDOKU_DEBUG_LOGGING_DEFAULT", raising=False)

    assert default_debug_logging_enabled() is True


def test_default_debug_logging_enabled_release_flatpak(monkeypatch):
    monkeypatch.setenv("FLATPAK_ID", "io.github.sepehr_rs.Sudoku")
    monkeypatch.delenv("SUDOKU_DEBUG_LOGGING_DEFAULT", raising=False)

    assert default_debug_logging_enabled() is False


def test_default_debug_logging_enabled_env_override(monkeypatch):
    monkeypatch.setenv("FLATPAK_ID", "io.github.sepehr_rs.Sudoku")
    monkeypatch.setenv("SUDOKU_DEBUG_LOGGING_DEFAULT", "true")

    assert default_debug_logging_enabled() is True
