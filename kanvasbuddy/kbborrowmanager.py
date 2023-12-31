# This file is part of KanvasBuddy.

# KanvasBuddy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# KanvasBuddy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KanvasBuddy. If not, see <https://www.gnu.org/licenses/>.

from krita import Krita
from PyQt5.QtWidgets import QWidget
from .kbpresetchooser import KBPresetChooser

class KBBorrowManager():
    _parents = {}
    _widgets = {}

    def __init__(self):
        self._qWin = Krita.instance().activeWindow().qwindow()


    def widget(self, ID):
        return self._widgets[ID]


    def borrowDockerWidget(self, ID):
        if ID == 'PresetDocker':
            return KBPresetChooser()
        else:
            self._parents[ID] = self._qWin.findChild(QWidget, ID)
            self._widgets[ID] = self._parents[ID].widget()
            return self._parents[ID].widget()
            
        return None


    def returnWidget(self, ID):
        self._parents[ID].setWidget(self._widgets[ID])
        self._parents[ID].widget().setEnabled(True)


    def returnAll(self):
        for ID in self._parents:
            self.returnWidget(ID)


    def dockerWindowTitle(self, ID):
        title = self._qWin.findChild(QWidget, ID).windowTitle()
        return title.replace('&', '')