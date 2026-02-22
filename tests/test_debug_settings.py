# SPDX-License-Identifier: GPL-3.0-or-later

from src.base import debug_settings


def test_load_debug_logging_preference_returns_none_when_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))

    assert debug_settings.load_debug_logging_preference() is None


def test_save_and_load_debug_logging_preference(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))

    debug_settings.save_debug_logging_preference(True)
    assert debug_settings.load_debug_logging_preference() is True

    debug_settings.save_debug_logging_preference(False)
    assert debug_settings.load_debug_logging_preference() is False
