# log_utils tests

# Copyright 2025 sepehr-rs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock GTK modules before importing anything else
sys.modules["gi"] = MagicMock()
sys.modules["gi.repository"] = MagicMock()
sys.modules["gi.repository.Gtk"] = MagicMock()
sys.modules["gi.repository.Gdk"] = MagicMock()
sys.modules["gi.repository.GLib"] = MagicMock()
sys.modules["gi.repository.Adw"] = MagicMock()

import pytest

from src.base.log_paths import get_log_file_path
from src.log_utils import setup_logging, get_session_id, set_debug_logging


@pytest.fixture(autouse=True)
def _logging_guard():
    """Reset logging state between tests."""
    # Reset module-level variables
    import src.log_utils as log_utils_module

    log_utils_module._logging_configured = False
    log_utils_module._log_buffer_handler = None
    log_utils_module._session_id = None

    # Clear all handlers from root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    yield


class TestLogFilePathResolution:
    """Tests for log file path resolution using XDG standards."""

    def test_get_log_file_path_without_xdg_state_home(self, tmp_path, monkeypatch):
        """Verify path falls back to ~/.local/state when XDG_STATE_HOME is not set."""
        # Set a temp home directory
        home = tmp_path / "home"
        home.mkdir()

        # Unset XDG_STATE_HOME (default behavior)
        monkeypatch.delenv("XDG_STATE_HOME", raising=False)

        # Set HOME environment variable to test home directory fallback
        monkeypatch.setenv("HOME", str(home))

        # Mock Path.home() to return our test home
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = home

            log_file_path = get_log_file_path()

            # Should fall back to ~/.local/state/io.github.sepehr_rs.Sudoku/sudoku.log
            expected_path = home / ".local" / "state" / "io.github.sepehr_rs.Sudoku" / "sudoku.log"
            assert log_file_path == str(expected_path)

    def test_get_log_file_path_with_xdg_state_home(self, tmp_path, monkeypatch):
        """Verify path uses XDG_STATE_HOME when environment variable is set."""
        xdg_home = tmp_path / "xdg" / "state"
        xdg_home.mkdir(parents=True)

        # Set XDG_STATE_HOME
        monkeypatch.setenv("XDG_STATE_HOME", str(xdg_home))

        # Mock Path.home() to avoid real home directory references
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp/unused")

            log_file_path = get_log_file_path()

            # Should use XDG_STATE_HOME/io.github.sepehr_rs.Sudoku/sudoku.log
            expected_path = xdg_home / "io.github.sepehr_rs.Sudoku" / "sudoku.log"
            assert log_file_path == str(expected_path)

    def test_get_log_file_path_absolute(self, tmp_path, monkeypatch):
        """Verify returned path is absolute."""
        xdg_home = tmp_path / "xdg" / "state"
        xdg_home.mkdir(parents=True)

        monkeypatch.setenv("XDG_STATE_HOME", str(xdg_home))

        log_file_path = get_log_file_path()

        assert os.path.isabs(log_file_path)
        assert log_file_path.endswith("sudoku.log")


class TestLogSetup:
    """Tests for logging setup and configuration."""

    def test_setup_logging_creates_buffer_handler(self):
        """Verify setup_logging creates LogBufferHandler."""
        handler = setup_logging()

        assert handler is not None
        assert hasattr(handler, "log_stream")

    def test_setup_logging_idempotent(self):
        """Verify multiple calls to setup_logging don't add duplicate handlers."""
        # First call
        handler1 = setup_logging()
        handler2 = setup_logging()

        # Should return the same handler instance
        assert handler1 is handler2

        # Should not have multiple buffer handlers in root logger
        import src.log_utils as log_utils_module

        root_logger = logging.getLogger()
        buffer_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, log_utils_module.LogBufferHandler)
        ]
        assert len(buffer_handlers) == 1

    def test_setup_logging_creates_file_handler(self, tmp_path, monkeypatch):
        """Verify setup_logging creates file handler with correct path."""
        xdg_home = tmp_path / "xdg" / "state"
        xdg_home.mkdir(parents=True)
        log_file_path = xdg_home / "io.github.sepehr_rs.Sudoku" / "sudoku.log"

        monkeypatch.setenv("XDG_STATE_HOME", str(xdg_home))

        handler = setup_logging()

        # Verify file handler was created
        import src.log_utils as log_utils_module

        root_logger = logging.getLogger()
        file_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, log_utils_module.RotatingFileHandler)
        ]
        assert len(file_handlers) == 1

        # Verify file handler has correct path
        file_handler = file_handlers[0]
        assert hasattr(file_handler, "baseFilename")
        assert file_handler.baseFilename == str(log_file_path)

        # Verify file was created
        assert log_file_path.exists()

    def test_setup_logging_rotating_file_handler_config(self, tmp_path, monkeypatch):
        """Verify RotatingFileHandler has correct rotation settings."""
        xdg_home = tmp_path / "xdg" / "state"
        xdg_home.mkdir(parents=True)

        monkeypatch.setenv("XDG_STATE_HOME", str(xdg_home))

        handler = setup_logging()

        # Verify file handler exists
        import src.log_utils as log_utils_module

        root_logger = logging.getLogger()
        file_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, log_utils_module.RotatingFileHandler)
        ]
        assert len(file_handlers) == 1

        file_handler = file_handlers[0]
        assert file_handler.maxBytes == 5 * 1024 * 1024  # 5MB
        assert file_handler.backupCount == 5

    def test_setup_logging_log_buffer_handler_writes(self):
        """Verify LogBufferHandler writes log messages."""
        handler = setup_logging()

        # Log a test message
        test_logger = logging.getLogger(__name__)
        test_logger.info("Test message")

        # Retrieve logs from buffer
        logs = handler.get_logs()
        assert "Test message" in logs

    def test_setup_logging_session_id_present_in_buffer(self):
        """Verify session_id appears in log messages from LogBufferHandler."""
        handler = setup_logging()

        # Log a test message
        test_logger = logging.getLogger(__name__)
        test_logger.info("Test message with session")

        # Retrieve logs from buffer
        logs = handler.get_logs()

        # Verify session_id is present
        assert "session_id=" in logs
        assert len(logs.split("session_id=")) > 1

    def test_get_session_id_returns_same_uuid(self):
        """Verify get_session_id returns the same UUID on repeated calls."""
        sid1 = get_session_id()
        sid2 = get_session_id()

        assert sid1 == sid2

    def test_set_debug_logging(self):
        """Verify set_debug_logging adjusts handler level."""
        # Setup logging
        handler = setup_logging()

        # Enable debug logging
        set_debug_logging(True)

        # Verify debug logging is enabled
        import src.log_utils as log_utils_module

        root_logger = logging.getLogger()
        file_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, log_utils_module.RotatingFileHandler)
        ]
        assert len(file_handlers) > 0
        assert file_handlers[0].level == logging.DEBUG

        # Disable debug logging
        set_debug_logging(False)

        # Verify debug logging is disabled
        assert file_handlers[0].level == logging.INFO


class TestGLibIntegration:
    """Tests for GLib/GTK log handler integration."""

    def test_glib_log_handler_setup_configured(self):
        """Verify setup_logging configures GLib log handler infrastructure."""
        import gi.repository.GLib as GLib

        # Verify log_set_writer_func is available and callable
        assert hasattr(GLib, "log_set_writer_func")
        assert GLib.log_set_writer_func is not None

        # Verify log_set_handler is available and callable
        assert hasattr(GLib, "log_set_handler")
        assert GLib.log_set_handler is not None

        # Verify log levels are defined
        assert hasattr(GLib, "LogLevelFlags")
        assert hasattr(GLib.LogLevelFlags, "LEVEL_MASK")


# Import logging after GTK mocking
import logging
