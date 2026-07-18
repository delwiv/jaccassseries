from __future__ import annotations

import sounddevice as sd
import numpy as np
from typing import Optional, Callable

BufferCallback = Callable[[np.ndarray], None]

SAMPLE_RATE = 16000
BLOCK_SIZE = 3200


class AudioCapture:
    def __init__(self) -> None:
        self.stream: Optional[sd.InputStream] = None
        self._device: Optional[str | int] = None
        self._buffers: list[np.ndarray] = []
        self._recording = False
        self.on_buffer: Optional[BufferCallback] = None

    @property
    def device(self) -> Optional[str | int]:
        return self._device

    @device.setter
    def device(self, device_id: Optional[str | int]) -> None:
        self._device = device_id

    def start(self) -> None:
        if self.stream is not None:
            return
        self._buffers.clear()
        self._recording = True
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            device=self._device,
            channels=1,
            dtype="float32",
            callback=self._audio_callback,
        )
        self.stream.start()

    def stop(self) -> np.ndarray:
        self._recording = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        if not self._buffers:
            return np.zeros((0,), dtype="float32")
        return np.concatenate(self._buffers)

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info,
        status: sd.CallbackFlags,
    ) -> None:
        if status:
            return
        audio = indata.copy().flatten()
        if self._recording:
            self._buffers.append(audio)
        if self.on_buffer:
            self.on_buffer(audio)

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
