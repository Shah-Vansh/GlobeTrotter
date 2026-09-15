"""
Chat API routes.

- POST /api/chat       – full agent (LLM + tools), optional Bearer JWT
- POST /api/chat/test  – LLM only (no tools)
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.agent.agent import get_agent
from app.services.llm_service import LLMServiceError, get_llm_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

SYSTEM_PROMPT_TEST = (
    "You are the GlobeTrotter travel assistant. "
    "Be concise, friendly, and accurate. "
    "Do not invent booking or payment features."
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None
    # Optional body token (prefer Authorization header)
    access_token: Optional[str] = None


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


def _extract_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip() or None
    return None


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(
    body: ChatRequest,
    authorization: Optional[str] = Header(default=None),
):
    """
    Full agent endpoint.

    Send the user's GlobeTrotter JWT as:
      Authorization: Bearer <access_token>
    or in the body as access_token.

    Without a token, only public tools (destinations/activities) work.
    Trip/itinerary tools require a valid token with the same privileges
    as the frontend user.
    """
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    token = _extract_bearer(authorization) or body.access_token

    logger.info(
        "REQUEST_START request_id=%s conversation_id=%s authenticated=%s message=%s",
        request_id,
        body.conversation_id or "(new)",
        bool(token),
        body.message[:120],
    )

    agent = get_agent()
    result = await agent.run(
        body.message,
        conversation_id=body.conversation_id,
        request_id=request_id,
        access_token=token,
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
    """Phase 3 smoke-test: Groq only, no tools."""
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    conversation_id = body.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"

    llm = get_llm_service()
    try:
        result = await llm.chat(
            messages=[{"role": "user", "content": body.message}],
            system_prompt=SYSTEM_PROMPT_TEST,
            request_id=request_id,
        )
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail={"success": False, "request_id": request_id, "error": str(exc)},
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
