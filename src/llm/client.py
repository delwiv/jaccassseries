from __future__ import annotations

from typing import Optional


class LLMClient:
    def __init__(self, base_url: str = "http://localhost:8080", api_key: str = "") -> None:
        self.base_url = base_url
        self.api_key = api_key

    def list_models(self) -> list[str]:
        return []

    def send_message(self, text: str, callback) -> None:
        pass
