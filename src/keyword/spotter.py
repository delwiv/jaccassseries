from __future__ import annotations

from typing import Optional

from pynput import keyboard

_HOTKEY_MAP = {
    "ctrl+space": "<ctrl>+<space>",
    "ctrl+shift+space": "<ctrl>+<shift>+<space>",
    "alt+space": "<alt>+<space>",
    "ctrl+`": "<ctrl>+`",
    "ctrl+shift+a": "<ctrl>+<shift>+a",
    "ctrl+alt+a": "<ctrl>+<alt>+a",
    "f4": "<media_play_pause>",
}

_PARSE_MAP = {
    "ctrl": "<ctrl>",
    "shift": "<shift>",
    "alt": "<alt>",
    "space": "<space>",
    "enter": "<enter>",
    "tab": "<tab>",
    "escape": "<esc>",
    "backspace": "<backspace>",
    "up": "<up>",
    "down": "<down>",
    "left": "<left>",
    "right": "<right>",
    "f1": "<f1>",
    "f2": "<f2>",
    "f3": "<f3>",
    "f4": "<f4>",
    "f5": "<f5>",
    "f6": "<f6>",
    "f7": "<f7>",
    "f8": "<f8>",
    "f9": "<f9>",
    "f10": "<f10>",
    "f11": "<f11>",
    "f12": "<f12>",
}


def _parse_shortcut(text: str) -> list:
    parts = text.lower().replace(" ", "").split("+")
    result = []
    for p in parts:
        if p in _PARSE_MAP:
            result.append(_PARSE_MAP[p])
        elif len(p) == 1:
            result.append(p)
    return result


class GlobalShortcut:
    def __init__(self) -> None:
        self._listener: Optional[keyboard.Listener] = None
        self._hotkey: Optional[keyboard.HotKey] = None
        self.on_activate: Optional[callable] = None

    def register(self, shortcut: str) -> None:
        self.unregister()
        if not shortcut:
            return
        keys = _parse_shortcut(shortcut)
        if not keys:
            return
        self._hotkey = keyboard.HotKey(keys, self._on_activate)
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()
        print(f"[shortcut] registered: {shortcut}")

    def unregister(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
            self._hotkey = None

    def _on_press(self, key) -> None:
        if self._hotkey is not None:
            self._hotkey.press(key)

    def _on_activate(self) -> None:
        if self.on_activate:
            self.on_activate()
