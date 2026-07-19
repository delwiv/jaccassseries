from __future__ import annotations

import qtawesome as qta
from PySide6.QtWidgets import QWidget, QPushButton, QMenu
from PySide6.QtCore import Qt, QSize, Signal, QPoint
from PySide6.QtGui import QColor, QMouseEvent

from src.pipeline.orchestrator import State


COLORS = {
    State.IDLE: "#9E9E9E",
    State.RECORDING: "#F44336",
    State.TRANSCRIBING: "#FF9800",
    State.LLM: "#2196F3",
    State.TTS: "#4CAF50",
}

ICONS = {
    State.IDLE: "fa6s.microphone",
    State.RECORDING: "fa6s.microphone",
    State.TRANSCRIBING: "fa6s.pen",
    State.LLM: "fa6s.robot",
    State.TTS: "fa6s.volume-high",
}

FAB_SIZE = 56


class FAB(QWidget):
    clicked = Signal()
    config_requested = Signal()
    quit_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._state = State.IDLE
        self._drag_pos: QPoint | None = None
        self._setup_window()
        self._setup_ui()

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(FAB_SIZE, FAB_SIZE)

    def _setup_ui(self) -> None:
        self.button = QPushButton(self)
        self.button.setFixedSize(FAB_SIZE, FAB_SIZE)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setIconSize(QSize(24, 24))
        self.button.clicked.connect(self.clicked.emit)
        self._update_button()

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, new_state: State) -> None:
        if new_state != self._state:
            self._state = new_state
            self._update_button()

    def _update_button(self) -> None:
        color = COLORS.get(self._state, COLORS[State.IDLE])
        icon_name = ICONS.get(self._state, ICONS[State.IDLE])
        icon = qta.icon(icon_name, color="#FFFFFF")
        self.button.setIcon(icon)
        self.button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                border-radius: {FAB_SIZE // 2}px;
            }}
            QPushButton:hover {{
                background-color: {color}CC;
            }}
            """
        )

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        config_action = menu.addAction("Configuration")
        config_action.triggered.connect(self.config_requested.emit)
        menu.addSeparator()
        quit_action = menu.addAction("Quitter")
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.exec(event.globalPos())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
