from __future__ import annotations

from typing import Optional, Callable

import numpy as np

TranscriptionCallback = Callable[[str], None]


class Transcriber:
    def __init__(self, language: str = "fr") -> None:
        self.language = language
        self._model = None

    def load_model(self) -> None:
        pass

    def transcribe(self, audio: np.ndarray) -> str:
        return ""

    def transcribe_stream(
        self,
        audio: np.ndarray,
        callback: Optional[TranscriptionCallback] = None,
    ) -> None:
        pass
