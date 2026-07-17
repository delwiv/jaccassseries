from __future__ import annotations

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel


class ConfigWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Configuration jacasseries")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Configuration à venir"))
        self.setLayout(layout)
