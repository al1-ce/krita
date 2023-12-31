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

from PyQt5.QtWidgets import QPushButton, QStackedWidget, QSizePolicy
from PyQt5.QtCore import QSize, QEvent

from .kbpanel import KBPanel
from .kbmainwidget import KBMainWidget
from .kbborrowmanager import KBBorrowManager
from .kbconfigmanager import KBConfigManager

class KBPanelStack(QStackedWidget):

    def __init__(self, parent=None):
        super(KBPanelStack, self).__init__(parent)
        super().currentChanged.connect(self.currentChanged)
        self._panels = {}
        self._borrower = KBBorrowManager()
        self.shortcutConnections = []
        
        self._mainWidget = KBMainWidget()
        self.addPanel('MAIN', self._mainWidget)
        self.appendShortcutAction('MAIN')
        self.initPanels()


    def initPanels(self):
        configManager = KBConfigManager()
        panelConfig = configManager.loadConfig('DOCKERS')
        properties = configManager.loadProperties('dockers')
        for entry in panelConfig:
            if panelConfig.getboolean(entry):
                self.loadPanel(properties[entry])


    def addPanel(self, ID, widget):
        panel = KBPanel(widget)

        if self.count() > 0:
            backButton = KBPanelCloseButton(lambda: self.setCurrentIndex(0))
            panel.layout().addWidget(backButton)

        self._panels[ID] = panel
        super().addWidget(panel)


    def loadPanel(self, properties):
        ID = properties['id']        
        widget = self._borrower.borrowDockerWidget(ID)
        title = self._borrower.dockerWindowTitle(ID)

        self.addPanel(ID, widget)
        if properties['size']:
            self.panel(ID).setSizeHint(properties['size'])
        if ID == 'PresetDocker':
            widget.presetChanged.connect(self._mainWidget.synchronizeSliders)
            
        self._mainWidget.addDockerButton(properties, self.panel(ID).activate, title)
        self.appendShortcutAction(ID)


    def appendShortcutAction(self, ID):
        i = str(self.count() - 1)  #account for main panel
        name = "KBPanel" + i
        action = Application.activeWindow().createAction(name, "KanvasBuddy")
        self.shortcutConnections.append(
            action.triggered.connect(self.panel(ID).activate)
        )
        self.shortcutConnections.append(
            action.triggered.connect(lambda: self.activateWindow())
        )


    def currentChanged(self, index):
        for i in range(0, self.count()):
            policy = QSizePolicy.Ignored
            if i == index:
                policy = QSizePolicy.Expanding
                self.widget(i).setEnabled(True)
            else:
                self.widget(i).setDisabled(False)

            self.widget(i).setSizePolicy(policy, policy)
            self.widget(i).updateGeometry()

        self.adjustSize()
        self.parentWidget().adjustSize()
    

    def event(self, e):
        r = super().event(e) # Get the return value of the parent class' event method first
        pinned = Application.readSetting("KanvasBuddy", "KBPinnedMode", "false")

        if (e.type() == QEvent.WindowDeactivate and pinned == "false"):
            self.setCurrentIndex(0)
        
        return r
    
    
    def dismantle(self):
        self._borrower.returnAll()
        for c in self.shortcutConnections:
            self.disconnect(c)


    def panel(self, name):
        return self._panels[name]


class KBPanelCloseButton(QPushButton):
    _config = KBConfigManager()
    _height = int(_config.loadConfig('SIZES')['dockerBack'])
    _iconSize = _height-2

    def __init__(self, onClick, parent=None):
        super(KBPanelCloseButton, self).__init__(parent)
        self.setIcon(Krita.instance().action('move_layer_up').icon())
        self.setIconSize(QSize(self._iconSize, self._iconSize))
        self.setFixedHeight(self._height)
        self.clicked.connect(onClick)