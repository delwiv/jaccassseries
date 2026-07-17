from __future__ import annotations

import sounddevice as sd
import numpy as np
from typing import Optional


class AudioOutput:
    def __init__(self) -> None:
        self.stream: Optional[sd.OutputStream] = None

    def play(self, audio: np.ndarray, samplerate: int = 22050) -> None:
        sd.play(audio, samplerate)

    def stop(self) -> None:
        sd.stop()

    @staticmethod
    def wait() -> None:
        sd.wait()
