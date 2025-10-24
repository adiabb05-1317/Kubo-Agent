"""Routes for interacting with Cerebras LLMs."""

from __future__ import annotations

from typing import Iterable

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from ..ai.models import CEREBRAS_LATEST_MODELS
from ..ai.service import chat_completion, stream_chat_completion


router = APIRouter(prefix="/ai", tags=["ai"])


class MessageSchema(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[MessageSchema]
    temperature: float | None = None
    top_p: float | None = None


@router.get("/models")
async def list_models() -> list[dict[str, object]]:
    """Return the known Cerebras models."""

    return [model.__dict__ for model in CEREBRAS_LATEST_MODELS]


@router.post("/chat")
async def create_chat_completion(payload: ChatRequest) -> dict[str, object]:
    """Return a non-streaming chat completion."""

    try:
        return chat_completion(
            model=payload.model,
            messages=_to_messages(payload.messages),
            temperature=payload.temperature,
            top_p=payload.top_p,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/chat/stream")
async def stream_chat(payload: ChatRequest) -> StreamingResponse:
    """Stream chat completion deltas."""

    def event_stream():
        try:
            for chunk in stream_chat_completion(
                model=payload.model,
                messages=_to_messages(payload.messages),
                temperature=payload.temperature,
                top_p=payload.top_p,
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"event: error\ndata: {str(exc)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _to_messages(entries: Iterable[MessageSchema]) -> list[dict[str, str]]:
    return [
        {
            "role": entry.role,
            "content": entry.content,
        }
        for entry in entries
    ]


