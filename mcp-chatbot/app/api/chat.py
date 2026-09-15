"""
Chat API routes.

Phase 3: simple test endpoint that calls Groq directly (no MCP tools yet).
Phase 4 will replace this with the full agentic loop.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.llm_service import LLMServiceError, get_llm_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

SYSTEM_PROMPT = (
    "You are the GlobeTrotter travel assistant. "
    "You help users plan trips using the GlobeTrotter application. "
    "Be concise, friendly, and accurate. "
    "Do not invent booking, payment, or other features that do not exist."
)


class ChatTestRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None


class ChatTestResponse(BaseModel):
    success: bool
    request_id: str
    conversation_id: str
    reply: str
    model: str
    latency_seconds: float
    usage: dict


@router.post("/chat/test", response_model=ChatTestResponse, tags=["chat"])
async def chat_test(body: ChatTestRequest):
    """
    Phase 3 smoke-test endpoint.

    Sends the user message to Groq (openai/gpt-oss-120b) and returns the reply
    together with token usage and latency. No MCP tools are used yet.
    """
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    conversation_id = body.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"

    logger.info(
        "REQUEST_START request_id=%s conversation_id=%s message=%s",
        request_id,
        conversation_id,
        body.message[:120],
    )

    llm = get_llm_service()

    try:
        result = await llm.chat(
            messages=[{"role": "user", "content": body.message}],
            system_prompt=SYSTEM_PROMPT,
            request_id=request_id,
        )
    except LLMServiceError as exc:
        logger.error(
            "REQUEST_FAILED request_id=%s error=%s",
            request_id,
            str(exc),
        )
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "request_id": request_id,
                "error": str(exc),
            },
        ) from exc

    logger.info(
        "REQUEST_SUCCESS request_id=%s total_latency=%.3fs",
        request_id,
        result.latency_seconds,
    )

    return ChatTestResponse(
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
    )
