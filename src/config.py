from __future__ import annotations

import tomllib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


CONFIG_DIR = Path.home() / ".config" / "jacasseries"
CONFIG_PATH = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG = {
    "api": {
        "url": "http://localhost:8080",
        "key": "",
    },
    "llm": {
        "model": "",
    },
    "stt": {
        "language": "fr",
    },
    "tts": {
        "voice": "",
    },
    "audio": {
        "microphone": "",
    },
    "general": {
        "keyboard_shortcut": "",
    },
}


@dataclass
class Config:
    api_url: str = "http://localhost:8080"
    api_key: str = ""
    llm_model: str = ""
    stt_language: str = "fr"
    tts_voice: str = ""
    microphone: str = ""
    keyboard_shortcut: str = ""

    @classmethod
    def load(cls) -> Config:
        if not CONFIG_PATH.exists():
            return cls()
        raw = CONFIG_PATH.read_text()
        data = tomllib.loads(raw)
        cfg = cls()
        cfg.api_url = data.get("api", {}).get("url", cfg.api_url)
        cfg.api_key = data.get("api", {}).get("key", cfg.api_key)
        cfg.llm_model = data.get("llm", {}).get("model", cfg.llm_model)
        cfg.stt_language = data.get("stt", {}).get("language", cfg.stt_language)
        cfg.tts_voice = data.get("tts", {}).get("voice", cfg.tts_voice)
        cfg.microphone = data.get("audio", {}).get("microphone", cfg.microphone)
        cfg.keyboard_shortcut = data.get("general", {}).get("keyboard_shortcut", cfg.keyboard_shortcut)
        return cfg

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        content = (
            f"[api]\n"
            f'url = "{self.api_url}"\n'
            f'key = "{self.api_key}"\n'
            f"\n"
            f"[llm]\n"
            f'model = "{self.llm_model}"\n'
            f"\n"
            f"[stt]\n"
            f'language = "{self.stt_language}"\n'
            f"\n"
            f"[tts]\n"
            f'voice = "{self.tts_voice}"\n'
            f"\n"
            f"[audio]\n"
            f'microphone = "{self.microphone}"\n'
            f"\n"
            f"[general]\n"
            f'keyboard_shortcut = "{self.keyboard_shortcut}"\n'
        )
        CONFIG_PATH.write_text(content)
