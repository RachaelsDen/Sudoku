# log_paths.py
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

import os
from pathlib import Path


def get_log_file_path() -> str:
    """Get the full path to the Sudoku log file.

    Environment variable overrides (in order of precedence):
    - SUDOKU_LOG_FILE: If set, use this exact path
    - SUDOKU_LOG_DIR: If set, use this directory with 'sudoku.log' filename
    - XDG_STATE_HOME: If set, use XDG state directory

    Returns:
        The absolute path to the log file.
    """
    log_file_override = os.environ.get('SUDOKU_LOG_FILE')
    if log_file_override:
        return log_file_override

    log_dir_override = os.environ.get('SUDOKU_LOG_DIR')
    if log_dir_override:
        return str(Path(log_dir_override) / 'sudoku.log')

    xdg_state_home = os.environ.get('XDG_STATE_HOME', Path.home() / '.local' / 'state')
    app_dir = Path(xdg_state_home) / 'io.github.sepehr_rs.Sudoku'
    return str(app_dir / 'sudoku.log')
