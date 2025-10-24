"""Cerebras LLM client utilities using the official Cerebras Cloud SDK.

Tool use documentation: https://inference-docs.cerebras.ai/capabilities/tool-use
"""

from __future__ import annotations

from typing import Any, Iterator, Optional

from cerebras.cloud.sdk import Cerebras

from ..settings import settings


class CerebrasClientError(RuntimeError):
    """Raised when a Cerebras API call fails."""


class CerebrasClient:
    """Wrapper for interacting with Cerebras API using the official SDK."""

    _DEFAULT_MODEL = "gpt-oss-120b"
    _DEFAULT_TEMPERATURE = 0.7
    _DEFAULT_TOP_P = 1.0
    _DEFAULT_MAX_TOKENS = 4096
    _DEFAULT_REASONING_EFFORT = "low"

    def __init__(self, api_key: str) -> None:
        self._client = Cerebras(api_key=api_key)

    def chat_completion(
        self,
        *,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        stream: bool = False,
    ) -> Any:
        """Call the Cerebras chat completions endpoint with optimal defaults.
        
        Args:
            messages: Chat messages with role and content
            tools: Optional list of function tools (auto-populated from registry)
            stream: Whether to stream the response
            
        Returns:
            Completion response object or stream iterator
            
        Reference:
            https://inference-docs.cerebras.ai/capabilities/tool-use
        """
        try:
            params: dict[str, Any] = {
                "model": self._DEFAULT_MODEL,
                "messages": messages,
                "stream": stream,
                "temperature": self._DEFAULT_TEMPERATURE,
                "top_p": self._DEFAULT_TOP_P,
                "max_completion_tokens": self._DEFAULT_MAX_TOKENS,
                "reasoning_effort": self._DEFAULT_REASONING_EFFORT,
            }
            
            if tools is not None:
                params["tools"] = tools
            
            return self._client.chat.completions.create(**params)
            
        except Exception as exc:
            raise CerebrasClientError(f"Cerebras API call failed: {exc}") from exc

    def chat_completion_stream(
        self,
        *,
        messages: list[dict[str, str]],
    ) -> Iterator[Any]:
        """Stream chat completion chunks (without tool calling).
        
        Yields delta chunks from the model response.
        """
        response_stream = self.chat_completion(
            messages=messages,
            stream=True,
        )
        
        for chunk in response_stream:
            yield chunk


_client_instance: Optional[CerebrasClient] = None


def get_cerebras_client() -> CerebrasClient:
    """Return a cached CerebrasClient instance configured from settings."""

    global _client_instance
    if _client_instance is None:
        _client_instance = CerebrasClient(settings.cerebras_api_key)
    return _client_instance


