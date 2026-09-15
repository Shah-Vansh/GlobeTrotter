"""Conversation memory management endpoints (Phase 7)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.state import (
    clear_conversation,
    get_conversation,
    list_conversation_ids,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationSummary(BaseModel):
    conversation_id: str
    message_count: int = 0
    metadata: dict = Field(default_factory=dict)
    updated_at: float | None = None


@router.get("")
async def list_conversations():
    """List known conversation ids (memory + disk)."""
    ids = list_conversation_ids()
    return {"success": True, "data": {"conversation_ids": ids, "count": len(ids)}}


@router.get("/{conversation_id}")
async def get_conversation_detail(conversation_id: str):
    """Fetch conversation metadata and message count (not full tool payloads by default)."""
    state = get_conversation(conversation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Summarise messages for inspection without dumping huge tool JSON
    summary_messages = []
    for m in state.messages:
        role = m.get("role")
        entry = {"role": role}
        if role == "user":
            entry["content"] = (m.get("content") or "")[:500]
        elif role == "assistant":
            entry["content"] = (m.get("content") or "")[:500]
            if m.get("tool_calls"):
                entry["tool_call_names"] = [
                    tc.get("function", {}).get("name") for tc in m["tool_calls"]
                ]
        elif role == "tool":
            entry["name"] = m.get("name")
            entry["content_preview"] = (m.get("content") or "")[:200]
        summary_messages.append(entry)

    return {
        "success": True,
        "data": {
            "conversation_id": state.conversation_id,
            "message_count": len(state.messages),
            "metadata": state.metadata,
            "created_at": state.created_at,
            "updated_at": state.updated_at,
            "messages": summary_messages,
        },
    }


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Clear a conversation from memory and disk."""
    ok = clear_conversation(conversation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "message": f"Conversation {conversation_id} cleared."}
