# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from unittest.mock import MagicMock

import pytest

pytest.skip(
    "Window logging tests require full GTK environment (Adw.Dialog)",
    allow_module_level=True,
)

sys.modules["gi"] = MagicMock()
sys.modules["gi.repository"] = MagicMock()
