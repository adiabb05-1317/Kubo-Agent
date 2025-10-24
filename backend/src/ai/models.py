"""Model registry for Cerebras LLM offerings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CerebrasModel:
    """Descriptor for a Cerebras model deployment."""

    identifier: str
    description: str
    context_window: int | None = None
    release: str | None = None


CEREBRAS_LATEST_MODELS: tuple[CerebrasModel, ...] = (
    CerebrasModel(
        identifier="cerebras-gpt-4.5",
        description="Flagship GPT-4.5 compatible large context model.",
        context_window=200_000,
        release="2024-09",
    ),
    CerebrasModel(
        identifier="cerebras-gpt-4.5-mini",
        description="Optimized GPT-4.5 mini variant balancing quality and latency.",
        context_window=128_000,
        release="2024-09",
    ),
    CerebrasModel(
        identifier="cerebras-llama-3.1-405b",
        description="Cerebras hosted Llama 3.1 405B instruction-tuned model.",
        context_window=200_000,
        release="2024-07",
    ),
    CerebrasModel(
        identifier="cerebras-llama-3.1-70b",
        description="Cerebras hosted Llama 3.1 70B instruction model ideal for production.",
        context_window=128_000,
        release="2024-07",
    ),
)


