# debug_settings.py
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

import json
import os
from pathlib import Path


def _state_dir() -> Path:
    xdg_state_home = os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")
    return Path(xdg_state_home) / "io.github.sepehr_rs.Sudoku"


def _settings_path() -> Path:
    return _state_dir() / "debug-settings.json"


def load_debug_logging_preference() -> bool | None:
    path = _settings_path()
    if not path.exists():
        return None

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None

    enabled = raw.get("debug_logging") if isinstance(raw, dict) else None
    if isinstance(enabled, bool):
        return enabled
    return None


def save_debug_logging_preference(enabled: bool) -> None:
    path = _settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"debug_logging": enabled}
    path.write_text(json.dumps(payload), encoding="utf-8")
