from __future__ import annotations

import threading
import traceback
from typing import Optional

import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from src.audio.capture import AudioCapture
from src.audio.output import AudioOutput
from src.config import Config
from src.llm.client import LLMClient
from src.pipeline.orchestrator import Orchestrator, State
from src.stt.transcriber import Transcriber
from src.tts.synthesizer import Synthesizer
from src.keyword.spotter import GlobalShortcut
from src.ui.config_window import ConfigWindow
from src.ui.fab import FAB
from src.ui.tray import SystemTray


class _MainThread(QObject):
    invoke = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.invoke.connect(lambda fn: fn())

_main = _MainThread()


def _run_in_thread(target, on_done=None, on_error=None, label=""):
    def wrapper():
        try:
            print(f"[thread:{label}] starting")
            result = target()
            print(f"[thread:{label}] done, result={repr(result)[:80]}")
            if on_done:
                _main.invoke.emit(lambda: on_done(result))
        except Exception as exc:
            print(f"[thread:{label}] EXCEPTION: {exc}")
            traceback.print_exc()
            if on_error:
                _main.invoke.emit(lambda err=exc: on_error(err))
    threading.Thread(target=wrapper, daemon=True).start()


class JacasseriesApp(QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setApplicationName("jacasseries")
        self.setOrganizationName("jacasseries")
        self.setQuitOnLastWindowClosed(False)

        self.config = Config.load()
        self.orchestrator = Orchestrator()
        self.fab = FAB()
        self.tray = SystemTray()
        self.audio = AudioCapture()
        self.transcriber = Transcriber(
            model_size=self.config.stt_model_size,
            language=self.config.stt_language,
            device=self.config.stt_device,
            compute_type=self.config.stt_compute_type,
        )
        self.llm = LLMClient(
            base_url=self.config.api_url,
            api_key=self.config.api_key,
            model=self.config.llm_model,
        )
        self.synthesizer = Synthesizer(voice=self.config.tts_voice or "fr_FR-siwis-medium")
        self.audio_out = AudioOutput()
        self.shortcut = GlobalShortcut()
        self.shortcut.on_activate = self._on_shortcut
        self._connect_signals()

    def _connect_signals(self) -> None:
        self.fab.clicked.connect(self._on_fab_click)
        self.fab.config_requested.connect(self._open_config)
        self.fab.quit_requested.connect(self.quit)
        self.orchestrator.on_state_change(self._on_state_change)
        self.orchestrator.on_transcription_ready = self._on_transcription_ready
        self.orchestrator.on_llm_token = self._on_llm_token
        self.orchestrator.on_llm_ready = self._on_llm_ready
        self.tray.show_requested.connect(self._toggle_visible)
        self.tray.config_requested.connect(self._open_config)
        self.tray.quit_requested.connect(self.quit)

    def _toggle_visible(self) -> None:
        if self.fab.isVisible():
            self.fab.hide()
        else:
            self.fab.show()

    def _open_config(self) -> None:
        dialog = ConfigWindow(self.config, llm_client=self.llm)
        if dialog.exec():
            self._reload_config()

    def _reload_config(self) -> None:
        self.llm.base_url = self.config.api_url
        self.llm.api_key = self.config.api_key
        self.llm.model = self.config.llm_model
        self.transcriber.model_size = self.config.stt_model_size
        self.transcriber.language = self.config.stt_language
        self.synthesizer = Synthesizer(
            voice=self.config.tts_voice or "fr_FR-siwis-medium"
        )
        if self.config.microphone:
            self.audio.device = int(self.config.microphone)
        self.shortcut.register(self.config.keyboard_shortcut)
        print("[config] reloaded")

    def _on_state_change(self, state: State) -> None:
        print(f"[orchestrator] -> {state.name}")
        self.fab.state = state

    def _on_fab_click(self) -> None:
        current = self.orchestrator.state
        print(f"[fab] click, state={current.name}")
        if current in (State.IDLE, State.TTS):
            if current == State.TTS:
                self.audio_out.stop()
                self.synthesizer.stop()
            self.orchestrator.start_recording()
            self.audio.start()
            print("\n--- recording ---")
        elif current == State.RECORDING:
            audio = self.audio.stop()
            self.orchestrator.stop_recording()
            print(f"--- transcribed ({len(audio) / 16000:.1f}s) ---")
            _run_in_thread(
                lambda: self.transcriber.transcribe(audio),
                on_done=self.orchestrator.transcription_done,
                on_error=lambda _: self.orchestrator.interrupt(),
                label="stt",
            )
        else:
            self.audio.stop()
            self.audio_out.stop()
            self.synthesizer.stop()
            self.orchestrator.interrupt()
            print("\n--- interrupted ---")

    def _on_transcription_ready(self, text: str) -> None:
        print(f"[pipe] transcription ready, text={repr(text[:120])}")
        if not text.strip():
            print("[pipe] empty transcription, back to idle")
            self.orchestrator.interrupt()
            return
        print(f">> {text}")
        print("--- llm ---")
        _run_in_thread(
            lambda: self.llm.send_message(text, on_token=self._on_llm_token),
            on_done=self.orchestrator.llm_done,
            on_error=lambda _: self.orchestrator.interrupt(),
            label="llm",
        )

    def _on_llm_token(self, token: str) -> None:
        if token:
            print(token, end="", flush=True)

    def _on_llm_ready(self, text: str) -> None:
        print(f"\n--- done ({len(text)} chars) ---")
        print("--- tts ---")
        _run_in_thread(
            lambda: self._speak(text),
            on_done=lambda _: self.orchestrator.tts_done(),
            on_error=lambda _: self.orchestrator.interrupt(),
            label="tts",
        )

    def _speak(self, text: str) -> None:
        audio = self.synthesizer.synthesize(text)
        if len(audio) == 0:
            return
        self.audio_out.play(audio, samplerate=self.synthesizer.sample_rate)

    def _on_shortcut(self) -> None:
        _main.invoke.emit(lambda: self._on_fab_click())

    def run(self) -> None:
        self.fab.show()
        self.tray.show()
        self.shortcut.register(self.config.keyboard_shortcut)
