"""Simple in-memory conversation state for Phase 4.

Later phases can replace this with Redis / DB-backed memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversationState:
    conversation_id: str
    messages: list[dict[str, Any]] = field(default_factory=list)

    def add_user(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str, tool_calls: list | None = None) -> None:
        msg: dict[str, Any] = {"role": "assistant", "content": content or None}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.messages.append(msg)

    def add_tool_result(self, tool_call_id: str, name: str, content: str) -> None:
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": name,
                "content": content,
            }
        )


# Process-local store (fine for single-process Phase 4)
_conversations: dict[str, ConversationState] = {}


def get_or_create_conversation(conversation_id: str) -> ConversationState:
    if conversation_id not in _conversations:
        _conversations[conversation_id] = ConversationState(conversation_id=conversation_id)
    return _conversations[conversation_id]
