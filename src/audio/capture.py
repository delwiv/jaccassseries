from __future__ import annotations

import sounddevice as sd
import numpy as np
from typing import Optional, Callable

BufferCallback = Callable[[np.ndarray], None]

SAMPLE_RATE = 16000
BLOCK_SIZE = 3200  # 200ms at 16kHz


class AudioCapture:
    def __init__(self, callback: Optional[BufferCallback] = None) -> None:
        self.callback = callback
        self.stream: Optional[sd.InputStream] = None
        self._device: Optional[int] = None

    @property
    def device(self) -> Optional[int]:
        return self._device

    @device.setter
    def device(self, device_id: Optional[int]) -> None:
        self._device = device_id

    def start(self) -> None:
        if self.stream is not None:
            return
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            device=self._device,
            channels=1,
            dtype="float32",
            callback=self._audio_callback,
        )
        self.stream.start()

    def stop(self) -> None:
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info,
        status: sd.CallbackFlags,
    ) -> None:
        if status:
            return
        if self.callback:
            self.callback(indata.copy())

    @staticmethod
    def list_devices() -> list[dict]:
        return sd.query_devices()

    @staticmethod
    def list_input_devices() -> list[str]:
        devices = sd.query_devices()
        return [
            f"{i}: {d['name']}"
            for i, d in enumerate(devices)
            if d["max_input_channels"] > 0
        ]
