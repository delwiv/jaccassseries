from __future__ import annotations

import sounddevice as sd
import numpy as np
from typing import Optional


class AudioOutput:
    def __init__(self) -> None:
        self._stopped = False

    def play(self, audio: np.ndarray, samplerate: int = 22050) -> None:
        self._stopped = False
        sd.play(audio, samplerate)
        sd.wait()

    def stop(self) -> None:
        self._stopped = True
        sd.stop()

    @staticmethod
    def wait() -> None:
        sd.wait()
