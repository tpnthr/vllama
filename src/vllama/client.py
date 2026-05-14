from __future__ import annotations

from collections.abc import Iterable

import httpx

from vllama.config import AppConfig


class VllmClient:
    def __init__(self, config: AppConfig, timeout: float = 120.0) -> None:
        self.config = config
        self.base_url = f"http://{config.host}:{config.port}/v1"
        self.timeout = timeout

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        stream: bool = False,
        extra: dict[str, object] | None = None,
    ) -> str | Iterable[str]:
        payload: dict[str, object] = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        if extra:
            payload.update(extra)

        if stream:
            return self._stream_chat(payload)

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            return str(data["choices"][0]["message"].get("content", ""))

    def _stream_chat(self, payload: dict[str, object]) -> Iterable[str]:
        with httpx.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            json=payload,
            timeout=self.timeout,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line or line == "data: [DONE]":
                    continue
                if line.startswith("data: "):
                    # Keep the streaming client simple for the MVP. The CLI uses
                    # non-streaming mode by default and richer parsing can land later.
                    yield line.removeprefix("data: ")

