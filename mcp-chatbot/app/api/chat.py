"""
Chat API routes.

- POST /api/chat/test  – Phase 3: LLM only (no tools)
- POST /api/chat       – Phase 4: full agent (LLM + MCP tools → GlobeTrotter APIs)
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.agent import get_agent
from app.services.llm_service import LLMServiceError, get_llm_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

SYSTEM_PROMPT_TEST = (
    "You are the GlobeTrotter travel assistant. "
    "You help users plan trips using the GlobeTrotter application. "
    "Be concise, friendly, and accurate. "
    "Do not invent booking, payment, or other features that do not exist."
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    request_id: str
    conversation_id: str
    reply: str
    model: str
    latency_seconds: float
    usage: dict[str, int] = Field(default_factory=dict)
    tool_calls_made: list[dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(body: ChatRequest):
    """
    Phase 4 agent endpoint.

    Flow:
      User message
        → Groq (tool schemas)
        → optional tool calls (search_destinations, search_activities, …)
        → existing GlobeTrotter APIs
        → final natural-language reply
    """
    request_id = f"req_{uuid.uuid4().hex[:8]}"

    logger.info(
        "REQUEST_START request_id=%s conversation_id=%s message=%s",
        request_id,
        body.conversation_id or "(new)",
        body.message[:120],
    )

    agent = get_agent()
    result = await agent.run(
        body.message,
        conversation_id=body.conversation_id,
        request_id=request_id,
    )

    if not result.success:
        logger.error(
            "REQUEST_FAILED request_id=%s error=%s",
            result.request_id,
            result.error,
        )
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "request_id": result.request_id,
                "conversation_id": result.conversation_id,
                "error": result.error,
            },
        )

    logger.info(
        "REQUEST_SUCCESS request_id=%s tools=%d latency=%.3fs",
        result.request_id,
        len(result.tool_calls_made),
        result.total_latency_seconds,
    )

    return ChatResponse(
        success=True,
        request_id=result.request_id,
        conversation_id=result.conversation_id,
        reply=result.reply,
        model=result.model,
        latency_seconds=result.total_latency_seconds,
        usage=result.usage,
        tool_calls_made=result.tool_calls_made,
    )


@router.post("/chat/test", response_model=ChatResponse, tags=["chat"])
async def chat_test(body: ChatRequest):
    """
    Phase 3 smoke-test: Groq only, no tools.
    Kept for debugging LLM connectivity.
    """
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    conversation_id = body.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"

    logger.info(
        "REQUEST_START (test) request_id=%s message=%s",
        request_id,
        body.message[:120],
    )

    llm = get_llm_service()

    try:
        result = await llm.chat(
            messages=[{"role": "user", "content": body.message}],
            system_prompt=SYSTEM_PROMPT_TEST,
            request_id=request_id,
        )
    except LLMServiceError as exc:
        logger.error("REQUEST_FAILED request_id=%s error=%s", request_id, str(exc))
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "request_id": request_id,
                "error": str(exc),
            },
        ) from exc

    return ChatResponse(
        success=True,
        request_id=request_id,
        conversation_id=conversation_id,
        reply=result.content,
        model=result.model,
        latency_seconds=round(result.latency_seconds, 3),
        usage={
            "input_tokens": result.usage.input_tokens,
            "output_tokens": result.usage.output_tokens,
            "total_tokens": result.usage.total_tokens,
        },
        tool_calls_made=[],
    )
