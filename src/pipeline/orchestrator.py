from __future__ import annotations

from enum import Enum, auto
from typing import Optional


class State(Enum):
    IDLE = auto()
    RECORDING = auto()
    TRANSCRIBING = auto()
    LLM = auto()
    TTS = auto()


class Orchestrator:
    def __init__(self) -> None:
        self._state = State.IDLE
        self._listeners: list[callable] = []

    @property
    def state(self) -> State:
        return self._state

    def on_state_change(self, listener: callable) -> None:
        self._listeners.append(listener)

    def _set_state(self, new_state: State) -> None:
        if new_state == self._state:
            return
        self._state = new_state
        for listener in self._listeners:
            listener(new_state)

    def start_recording(self) -> None:
        if self._state == State.TTS:
            self._set_state(State.IDLE)
        self._set_state(State.RECORDING)

    def stop_recording(self) -> None:
        if self._state == State.RECORDING:
            self._set_state(State.TRANSCRIBING)

    def transcription_done(self) -> None:
        if self._state == State.TRANSCRIBING:
            self._set_state(State.LLM)

    def llm_response_done(self) -> None:
        if self._state == State.LLM:
            self._set_state(State.TTS)

    def tts_done(self) -> None:
        if self._state == State.TTS:
            self._set_state(State.IDLE)

    def interrupt(self) -> None:
        if self._state in (State.TTS, State.LLM):
            self._set_state(State.IDLE)
