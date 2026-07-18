from __future__ import annotations

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush


class SystemTray(QSystemTrayIcon):
    quit_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setIcon(self._make_icon())
        self.setToolTip("jacasseries")
        menu = QMenu()
        action = menu.addAction("Quitter")
        action.triggered.connect(self.quit_requested.emit)
        self.setContextMenu(menu)

    @staticmethod
    def _make_icon():
        pixmap = QPixmap(22, 22)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor("#9E9E9E")))
        painter.setPen(QColor(0, 0, 0, 0))
        painter.drawEllipse(1, 1, 20, 20)
        painter.end()
        return pixmap
