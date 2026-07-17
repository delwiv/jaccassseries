from __future__ import annotations

from typing import Optional, Callable

import numpy as np

AudioCallback = Callable[[np.ndarray], None]


class Synthesizer:
    def __init__(self, voice: str = "") -> None:
        self.voice = voice

    def speak(self, text: str, callback: Optional[AudioCallback] = None) -> None:
        pass

    def stop(self) -> None:
        pass
