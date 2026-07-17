from __future__ import annotations

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.config import Config
from src.pipeline.orchestrator import Orchestrator, State
from src.ui.fab import FAB


class JacasseriesApp(QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setApplicationName("jacasseries")
        self.setOrganizationName("jacasseries")
        self.setQuitOnLastWindowClosed(False)

        self.config = Config.load()
        self.orchestrator = Orchestrator()
        self.fab = FAB()
        self._connect_signals()

    def _connect_signals(self) -> None:
        self.fab.clicked.connect(self._on_fab_click)
        self.orchestrator.on_state_change(self._on_state_change)

    def _on_state_change(self, state: State) -> None:
        self.fab.state = state

    def _on_fab_click(self) -> None:
        current = self.orchestrator.state
        if current == State.IDLE:
            self.orchestrator.start_recording()
        elif current == State.RECORDING:
            self.orchestrator.stop_recording()
        elif current == State.TTS:
            self.orchestrator.interrupt()
        else:
            self.orchestrator.interrupt()

    def run(self) -> None:
        self.fab.show()
