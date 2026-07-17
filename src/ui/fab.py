from __future__ import annotations

from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont

from src.pipeline.orchestrator import State


COLORS = {
    State.IDLE: QColor("#9E9E9E"),
    State.RECORDING: QColor("#F44336"),
    State.TRANSCRIBING: QColor("#FF9800"),
    State.LLM: QColor("#2196F3"),
    State.TTS: QColor("#4CAF50"),
}

ICONS = {
    State.IDLE: "🎤",
    State.RECORDING: "🎤",
    State.TRANSCRIBING: "✏️",
    State.LLM: "🤖",
    State.TTS: "🔊",
}

FAB_SIZE = 56


class FAB(QWidget):
    clicked = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._state = State.IDLE
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
        icon = ICONS.get(self._state, ICONS[State.IDLE])
        self.button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color.name()};
                border-radius: {FAB_SIZE // 2}px;
                font-size: 24px;
                color: white;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            """
        )
        self.button.setText(icon)

    def paintEvent(self, event) -> None:
        pass
