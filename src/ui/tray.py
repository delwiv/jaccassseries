from __future__ import annotations

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush


class SystemTray(QSystemTrayIcon):
    show_requested = Signal()
    config_requested = Signal()
    quit_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setIcon(self._make_icon())
        self.setToolTip("jacasseries")
        menu = QMenu()
        show_action = menu.addAction("Afficher / Masquer")
        show_action.triggered.connect(self.show_requested.emit)
        config_action = menu.addAction("Configuration")
        config_action.triggered.connect(self.config_requested.emit)
        menu.addSeparator()
        quit_action = menu.addAction("Quitter")
        quit_action.triggered.connect(self.quit_requested.emit)
        self.setContextMenu(menu)
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_requested.emit()

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
