from __future__ import annotations

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon


class SystemTray(QSystemTrayIcon):
    def __init__(self) -> None:
        super().__init__()
        menu = QMenu()
        menu.addAction("Quitter")
        self.setContextMenu(menu)
        self.setToolTip("jacasseries")
