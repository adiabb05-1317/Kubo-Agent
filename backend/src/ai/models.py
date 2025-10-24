"""Model registry for Cerebras LLM offerings.

Reference: https://inference-docs.cerebras.ai/
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CerebrasModel:
    """Descriptor for a Cerebras model deployment."""

    identifier: str
    description: str
    context_window: int | None = None
    supports_tools: bool = True
    supports_reasoning: bool = False


CEREBRAS_LATEST_MODELS: tuple[CerebrasModel, ...] = (
    CerebrasModel(
        identifier="gpt-oss-120b",
        description="GPT OSS 120B - Default model with strong performance and reasoning capabilities.",
        context_window=65536,
        supports_tools=True,
        supports_reasoning=True,
    ),
    CerebrasModel(
        identifier="llama3.1-8b",
        description="Llama 3.1 8B - Efficient model for general tasks.",
        context_window=128_000,
        supports_tools=True,
    ),
    CerebrasModel(
        identifier="llama3.1-70b",
        description="Llama 3.1 70B - Powerful model for complex reasoning.",
        context_window=128_000,
        supports_tools=True,
    ),
    CerebrasModel(
        identifier="llama3.3-70b",
        description="Llama 3.3 70B - Latest Llama model with improved capabilities.",
        context_window=128_000,
        supports_tools=True,
    ),
)


