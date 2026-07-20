from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
from huggingface_hub import hf_hub_download

VOICES_DIR = Path.home() / ".local" / "share" / "jacasseries" / "voices"
PIPER_REPO = "rhasspy/piper-voices"

KNOWN_VOICES = {
    "fr_FR-siwis-medium": {
        "path": "fr/fr_FR/siwis/medium",
    },
    "fr_FR-mls-medium": {
        "path": "fr/fr_FR/mls/medium",
    },
    "fr_FR-tom-medium": {
        "path": "fr/fr_FR/tom/medium",
    },
    "fr_FR-upmc-medium": {
        "path": "fr/fr_FR/upmc/medium",
    },
}


class Synthesizer:
    def __init__(self, voice: str = "fr_FR-siwis-medium") -> None:
        self.voice = voice
        self._voice_obj = None
        self._stopped = False
        self.sample_rate: int = 22050
        self._model_path: Optional[Path] = None
        self._config_path: Optional[Path] = None

    def _ensure_voice(self) -> None:
        if self._model_path is not None and self._model_path.exists():
            return

        if self.voice not in KNOWN_VOICES:
            msg = f"Unknown voice: {self.voice}. Known: {list(KNOWN_VOICES)}"
            raise ValueError(msg)

        info = KNOWN_VOICES[self.voice]
        VOICES_DIR.mkdir(parents=True, exist_ok=True)

        subdir = info["path"]
        model_filename = f"{subdir}/{self.voice}.onnx"
        config_filename = f"{subdir}/{self.voice}.onnx.json"

        print(f"[tts] downloading {self.voice}...")
        self._model_path = Path(
            hf_hub_download(
                repo_id=PIPER_REPO,
                filename=model_filename,
                local_dir=VOICES_DIR,
            )
        )
        self._config_path = Path(
            hf_hub_download(
                repo_id=PIPER_REPO,
                filename=config_filename,
                local_dir=VOICES_DIR,
            )
        )
        print("[tts] download done")

    def load_voice(self) -> None:
        if self._voice_obj is not None:
            return
        self._ensure_voice()
        from piper import PiperVoice

        self._voice_obj = PiperVoice.load(
            str(self._model_path),
            config_path=str(self._config_path),
            use_cuda=False,
        )

    def synthesize(self, text: str) -> np.ndarray:
        self.load_voice()
        self._stopped = False
        chunks = list(self._voice_obj.synthesize(text))
        if not chunks:
            return np.zeros((0,), dtype="float32")
        self.sample_rate = chunks[0].sample_rate
        audio = np.concatenate([c.audio_float_array for c in chunks])
        return audio

    def speak(self, text: str) -> np.ndarray:
        return self.synthesize(text)

    def stop(self) -> None:
        self._stopped = True
