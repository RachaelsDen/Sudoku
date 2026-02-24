# about_dialog.py
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

from gettext import gettext as _

from gi.repository import Adw


class SudokuAboutDialog(Adw.PreferencesWindow):
    def __init__(self, parent, version: str):
        super().__init__(title=_("About Sudoku"))
        self.set_default_size(580, 520)
        self.set_transient_for(parent)
        self.set_modal(True)

        page = Adw.PreferencesPage()

        about_group = Adw.PreferencesGroup(title=_("About"))
        about_group.add(self._info_row(_("Application"), _("Sudoku")))
        about_group.add(self._info_row(_("Version"), version))
        about_group.add(self._info_row(_("Developers"), "Sepehr, Revisto"))
        page.add(about_group)

        self.add(page)

    def _info_row(self, title: str, subtitle: str) -> Adw.ActionRow:
        row = Adw.ActionRow(title=title)
        row.set_subtitle(subtitle)
        row.set_activatable(False)
        return row
