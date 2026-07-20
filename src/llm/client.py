from __future__ import annotations

import json
from typing import Optional

import httpx

SYSTEM_PROMPT = (
    "Tu es un assistant vocal. Réponds uniquement en texte brut, "
    "sans aucun formatage markdown (pas d'astérisques, tirets, crochets, "
    "numéros, ou autres symboles de mise en forme). "
    "N'utilise pas d'emojis ou d'émoticônes. "
    "Écris comme tu parles à l'oral : des phrases naturelles et fluides. "
    "Pour les nombres, écris-les sous forme parlée si approprié. "
    "Sois concis et va droit au but."
)


class LLMClient:
    def __init__(self, base_url: str = "http://localhost:8080", api_key: str = "", model: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.system_prompt = SYSTEM_PROMPT
        self.messages: list[dict] = []
        self._headers = {"Content-Type": "application/json"}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

    def reset(self) -> None:
        self.messages.clear()

    def list_models(self) -> list[str]:
        with httpx.Client() as client:
            r = client.get(
                f"{self.base_url}/v1/models",
                headers=self._headers,
                timeout=10,
            )
            r.raise_for_status()
            return [m["id"] for m in r.json()["data"]]

    def send_message(
        self,
        text: str,
        on_token: Optional[callable] = None,
    ) -> str:
        full = ""
        payload_messages = [{"role": "system", "content": self.system_prompt}]
        payload_messages.extend(self.messages)
        payload_messages.append({"role": "user", "content": text})
        self.messages.append({"role": "user", "content": text})
        payload = {
            "model": self.model,
            "messages": payload_messages,
            "stream": True,
        }
        with httpx.Client() as client:
            with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                headers=self._headers,
                json=payload,
                timeout=120,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload_str = line[6:]
                    if payload_str == "[DONE]":
                        break
                    data = json.loads(payload_str)
                    delta = data["choices"][0]["delta"].get("content", "")
                    if delta:
                        full += delta
                        if on_token:
                            on_token(delta)
        self.messages.append({"role": "assistant", "content": full})
        return full
