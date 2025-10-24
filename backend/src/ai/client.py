"""Cerebras LLM client utilities."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from ..settings import settings


class CerebrasClientError(RuntimeError):
    """Raised when a Cerebras API call fails."""


class CerebrasClient:
    """Lightweight wrapper for interacting with the Cerebras API."""

    _BASE_URL = "https://api.cerebras.ai/v1"

    def __init__(self, api_key: str, *, timeout: float = 30.0) -> None:
        self._api_key = api_key
        self._timeout = timeout
        self._client = httpx.Client(
            base_url=self._BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def chat_completion(self, *, model: str, messages: list[dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """Call the Cerebras chat completions endpoint."""

        payload: Dict[str, Any] = {"model": model, "messages": messages}
        payload.update(kwargs)

        response = self._client.post("/chat/completions", json=payload)
        if response.status_code >= 400:
            raise CerebrasClientError(
                f"Cerebras API returned {response.status_code}: {response.text}"
            )
        return response.json()


_client_instance: Optional[CerebrasClient] = None


def get_cerebras_client() -> CerebrasClient:
    """Return a cached CerebrasClient instance configured from settings."""

    global _client_instance
    if _client_instance is None:
        _client_instance = CerebrasClient(settings.cerebras_api_key)
    return _client_instance


