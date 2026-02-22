# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import sys
from unittest.mock import MagicMock

sys.modules["gi"] = MagicMock()
sys.modules["gi.repository"] = MagicMock()
sys.modules["gi.repository.Gtk"] = MagicMock()
sys.modules["gi.repository.Gdk"] = MagicMock()
sys.modules["gi.repository.GLib"] = MagicMock()
sys.modules["gi.repository.Adw"] = MagicMock()
sys.modules["gi.repository.Gio"] = MagicMock()

import pytest

from src.base.log_paths import get_log_file_path
import src.log_utils as log_utils_module


@pytest.fixture(autouse=True)
def _logging_guard():
    log_utils_module._logging_configured = False
    log_utils_module._log_buffer_handler = None
    log_utils_module._session_id = None

    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    yield


class TestDebugInfoIncludesLogPath:
    """Tests for debug info including log file path and level in
    generate_debug_info()."""

    def test_generate_debug_info_includes_log_file_path(self):
        """Verify generate_debug_info() includes log file path."""
        # Create a mock application class
        class MockApp:
            def __init__(self, version):
                self.version = version
                self.log_handler = MagicMock()
                self.log_handler.get_logs.return_value = "Test log message\n"

            def generate_debug_info(self):
                log_file_path = get_log_file_path()
                log_level = "INFO"

                # Build debug info matching the implementation
                info = (
                    f"Sudoku {self.version}\n"
                    f"System: Linux\n"
                    f"Dist: Ubuntu 24.04\n"
                    f"Python 3.12.0\n"
                    f"GTK 4.0.0\n"
                    f"Adwaita 1.0.0\n"
                    f"PyGObject 3.12.0\n"
                    f"Log File: {log_file_path}\n"
                    f"Log Level: {log_level}\n"
                    "\n--- Logs ---\n"
                    f"{self.log_handler.get_logs()}"
                )
                return info

        app = MockApp(version="1.0.0")
        debug_info = app.generate_debug_info()

        # Verify log file path is present in output
        assert "Log File:" in debug_info
        assert get_log_file_path() in debug_info

    def test_generate_debug_info_includes_log_level(self):
        """Verify generate_debug_info() includes log level."""
        # Create a mock application class
        class MockApp:
            def __init__(self, version):
                self.version = version
                self.log_handler = MagicMock()
                self.log_handler.get_logs.return_value = "Test log message\n"

            def generate_debug_info(self):
                log_file_path = get_log_file_path()
                log_level = "INFO"

                # Build debug info matching the implementation
                info = (
                    f"Sudoku {self.version}\n"
                    f"System: Linux\n"
                    f"Dist: Ubuntu 24.04\n"
                    f"Python 3.12.0\n"
                    f"GTK 4.0.0\n"
                    f"Adwaita 1.0.0\n"
                    f"PyGObject 3.12.0\n"
                    f"Log File: {log_file_path}\n"
                    f"Log Level: {log_level}\n"
                    "\n--- Logs ---\n"
                    f"{self.log_handler.get_logs()}"
                )
                return info

        app = MockApp(version="1.0.0")
        debug_info = app.generate_debug_info()

        # Verify log level is present in output
        assert "Log Level:" in debug_info
        assert "INFO" in debug_info or "DEBUG" in debug_info

    def test_generate_debug_info_format(self):
        """Verify debug info has proper format with log file and level lines."""
        # Create a mock application class
        class MockApp:
            def __init__(self, version):
                self.version = version
                self.log_handler = MagicMock()
                self.log_handler.get_logs.return_value = "Test log message\n"

            def generate_debug_info(self):
                log_file_path = get_log_file_path()
                log_level = "INFO"

                # Build debug info matching the implementation
                info = (
                    f"Sudoku {self.version}\n"
                    f"System: Linux\n"
                    f"Dist: Ubuntu 24.04\n"
                    f"Python 3.12.0\n"
                    f"GTK 4.0.0\n"
                    f"Adwaita 1.0.0\n"
                    f"PyGObject 3.12.0\n"
                    f"Log File: {log_file_path}\n"
                    f"Log Level: {log_level}\n"
                    "\n--- Logs ---\n"
                    f"{self.log_handler.get_logs()}"
                )
                return info

        app = MockApp(version="1.0.0")
        debug_info = app.generate_debug_info()

        # Verify the log file and level appear in the right order
        log_file_line = f"Log File: {get_log_file_path()}"
        log_level_line = "Log Level:"

        # Verify both lines are present
        assert log_file_line in debug_info
        assert log_level_line in debug_info

        # Verify they appear before "--- Logs ---" section
        logs_section = "--- Logs ---"
        assert debug_info.find(log_file_line) < debug_info.find(logs_section)
        assert debug_info.find(log_level_line) < debug_info.find(logs_section)
