"""High-level service helpers for Cerebras LLM interactions."""

from __future__ import annotations

from typing import Iterable, Iterator

from .client import CerebrasClient, get_cerebras_client


def stream_chat_completion(
    *,
    model: str,
    messages: Iterable[dict[str, str]],
    temperature: float | None = None,
    top_p: float | None = None,
    client: CerebrasClient | None = None,
) -> Iterator[dict[str, object]]:
    """Yield delta chunks from a streaming chat completion call."""

    active_client = client or get_cerebras_client()
    payload: dict[str, object] = {
        "model": model,
        "messages": list(messages),
        "stream": True,
    }
    if temperature is not None:
        payload["temperature"] = temperature
    if top_p is not None:
        payload["top_p"] = top_p

    response = active_client.chat_completion(**payload)

    choices = response.get("choices", [])
    for choice in choices:
        delta = choice.get("delta")
        if delta:
            yield delta


def chat_completion(
    *,
    model: str,
    messages: Iterable[dict[str, str]],
    temperature: float | None = None,
    top_p: float | None = None,
    client: CerebrasClient | None = None,
) -> dict[str, object]:
    """Return a blocking chat completion response."""

    active_client = client or get_cerebras_client()
    payload: dict[str, object] = {
        "model": model,
        "messages": list(messages),
        "stream": False,
    }
    if temperature is not None:
        payload["temperature"] = temperature
    if top_p is not None:
        payload["top_p"] = top_p

    return active_client.chat_completion(**payload)


