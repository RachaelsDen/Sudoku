# application.py
#
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

import gi
import platform
import logging
import logging.handlers

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gio, Adw, Gtk

from .window import SudokuWindow
from .screens.about_dialog import SudokuAboutDialog
from .screens.help_dialog import HowToPlayDialog
from . import log_utils
from .base.log_paths import get_log_file_path


class SudokuApplication(Adw.Application):
    def __init__(self, version):
        super().__init__(
            application_id="io.github.sepehr_rs.Sudoku",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.version = version
        self._setup_actions()
        self._setup_accelerators()
        self.log_handler = log_utils._log_buffer_handler or log_utils.setup_logging()
        log_utils.set_debug_logging(log_utils.is_debug_logging_enabled())

    def _setup_actions(self):
        """Set up application actions."""
        self.create_action("quit", self._on_close_request, ["<primary>q", "<primary>w"])
        self.create_action("about", self.on_about_action)
        self.create_action("how_to_play", self.on_how_to_play, ["F1"])

    def _setup_accelerators(self):
        """Set up keyboard accelerators for window actions."""
        self.set_accels_for_action("win.pencil-toggled", ["p"])
        self.set_accels_for_action("win.back-to-menu", ["<Ctrl>m"])
        self.set_accels_for_action("win.show-primary-menu", ["F10"])
        self.set_accels_for_action("win.show-shortcuts-overlay", ["<Ctrl>question"])
        self.set_accels_for_action("win.show-preferences", ["<primary>comma"])

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = SudokuWindow(application=self)
        win.present()

    def generate_debug_info(self) -> str:
        system = platform.system()
        dist = (
            f"Dist: {platform.freedesktop_os_release()['PRETTY_NAME']}"
            if system == "Linux"
            else ""
        )

        log_file_path = get_log_file_path()
        root_logger = logging.getLogger()
        log_level = "INFO"
        for handler in root_logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                log_level = "DEBUG" if handler.level == logging.DEBUG else "INFO"
                break

        info = (
            f"Sudoku {self.version}\n"
            f"System: {system}\n"
            f"{dist}\n"
            f"Python {platform.python_version()}\n"
            f"GTK {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}\n"
            f"Adwaita {Adw.MAJOR_VERSION}.{Adw.MINOR_VERSION}.{Adw.MICRO_VERSION}\n"
            f"PyGObject {'.'.join(map(str, gi.version_info))}\n"
            f"Log File: {log_file_path}\n"
            f"Log Level: {log_level}\n"
            "\n--- Logs ---\n"
            f"{self.log_handler.get_logs()}"
        )
        return info

    def on_about_action(self, *_):
        dialog = SudokuAboutDialog(self.props.active_window, self.version)
        dialog.present()

    def on_how_to_play(self, _action, _param):
        """Show how to play dialog."""
        dialog = HowToPlayDialog()
        dialog.present(self.props.active_window)

    def _on_close_request(self, *_args):
        self.quit()

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)
