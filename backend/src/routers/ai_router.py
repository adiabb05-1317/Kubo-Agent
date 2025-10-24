"""Routes for interacting with Cerebras LLMs.

Tool use reference: https://inference-docs.cerebras.ai/capabilities/tool-use
"""

from __future__ import annotations

import json
from typing import Any, Iterable

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..ai.executor import execute_with_tools, execute_with_tools_streaming
from ..ai.models import CEREBRAS_LATEST_MODELS
from ..ai.tools import get_tool_registry


router = APIRouter(prefix="/ai", tags=["ai"])


class MessageSchema(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[MessageSchema]


@router.get("/models")
async def list_models() -> list[dict[str, object]]:
    """Return the known Cerebras models."""
    return [model.__dict__ for model in CEREBRAS_LATEST_MODELS]


@router.get("/tools")
async def list_tools() -> dict[str, Any]:
    """Return the available tools/functions that the LLM can call."""
    registry = get_tool_registry()
    return {
        "tools": registry.get_all_schemas(),
        "count": len(registry.get_all_schemas())
    }


@router.post("/chat/auto")
async def create_chat_completion_with_tools(payload: ChatRequest) -> dict[str, Any]:
    """Return a chat completion with AUTOMATIC tool execution.
    
    This endpoint handles the full tool calling loop:
    1. Calls the LLM with available tools
    2. If LLM requests tool calls, executes them automatically
    3. Sends results back to LLM
    4. Returns final response
    
    If no tools are specified, uses all registered tools from the tool registry.
    
    Example request:
        POST /ai/chat/auto
        {
            "messages": [{"role": "user", "content": "What is 25 multiplied by 4?"}]
        }
    
    See: https://inference-docs.cerebras.ai/capabilities/tool-use
    """

    try:
        response, conversation = execute_with_tools(messages=_to_messages(payload.messages))
        
        # Convert response to dict
        response_dict = response.model_dump() if hasattr(response, 'model_dump') else response
        
        # Extract the final text response
        final_message = ""
        if isinstance(response_dict, dict):
            choices = response_dict.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                final_message = message.get("content", "")
        
        return {
            "response": response_dict,
            "text": final_message,  # Convenience field for the final answer
            "conversation": conversation,
            "tool_calls_executed": len([msg for msg in conversation if msg.get("role") == "tool"])
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/chat/auto/stream")
async def stream_chat_with_tools(payload: ChatRequest) -> StreamingResponse:
    """Stream chat completion with AUTOMATIC tool execution.
    
    This endpoint:
    1. Executes tool calls automatically (blocking)
    2. Streams only the final response after all tools are executed
    3. Provides real-time token generation for the final answer
    
    Example request:
        POST /ai/chat/auto/stream
        {
            "messages": [{"role": "user", "content": "What is 25 multiplied by 4?"}]
        }
    
    Note: Tool execution happens before streaming starts, then streams the final response.
    
    See: https://inference-docs.cerebras.ai/capabilities/tool-use
    """

    def event_stream():
        try:
            for chunk in execute_with_tools_streaming(messages=_to_messages(payload.messages)):
                # Serialize chunk to JSON
                if hasattr(chunk, 'model_dump'):
                    chunk_data = chunk.model_dump()
                elif hasattr(chunk, 'dict'):
                    chunk_data = chunk.dict()
                else:
                    chunk_data = chunk
                    
                yield f"data: {json.dumps(chunk_data)}\n\n"
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




