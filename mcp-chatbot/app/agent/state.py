"""
Conversation memory for the GlobeTrotter agent (Phase 7).

- In-process store keyed by conversation_id
- Optional JSON persistence under data/conversations/
- Message windowing so context stays within model limits
- Lightweight metadata: user hint, last trip_id, tool summary
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from app.config import get_settings

# Keep enough turns for multi-step planning without blowing the context window.
# Counts messages of all roles (user/assistant/tool).
MAX_MESSAGES = 40
# Soft TTL for idle conversations (seconds); cleaned on access
CONVERSATION_TTL_SECONDS = 60 * 60 * 12  # 12 hours

_lock = threading.Lock()
_conversations: dict[str, "ConversationState"] = {}


def _persist_dir() -> Path:
    settings = get_settings()
    # Reuse log parent or project-relative data/
    base = Path(settings.log_dir).resolve().parent / "data" / "conversations"
    base.mkdir(parents=True, exist_ok=True)
    return base


@dataclass
class ConversationState:
    conversation_id: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    # Soft context the agent can use in prompts / debugging
    metadata: dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = time.time()

    def add_user(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})
        self._trim()
        self.touch()

    def add_assistant(self, content: str, tool_calls: list | None = None) -> None:
        msg: dict[str, Any] = {"role": "assistant", "content": content or None}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.messages.append(msg)
        self._trim()
        self.touch()

    def add_tool_result(self, tool_call_id: str, name: str, content: str) -> None:
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": name,
                "content": content,
            }
        )
        # Track last successful tool names for debugging / UI
        recent = self.metadata.setdefault("recent_tools", [])
        recent.append(name)
        self.metadata["recent_tools"] = recent[-20:]
        self._maybe_extract_ids(name, content)
        self._trim()
        self.touch()

    def _maybe_extract_ids(self, tool_name: str, content: str) -> None:
        """Best-effort capture of trip_id from tool JSON for session context."""
        try:
            payload = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            return
        if not isinstance(payload, dict) or not payload.get("success"):
            return
        data = payload.get("data")
        if not isinstance(data, dict):
            return
        if "id" in data and tool_name in (
            "create_trip",
            "get_trip",
            "update_trip",
        ):
            self.metadata["last_trip_id"] = data["id"]
        if tool_name == "add_stop_to_trip" and "id" in data:
            self.metadata["last_stop_id"] = data["id"]

    def _trim(self) -> None:
        """Drop oldest messages but never split a tool_call group mid-flight."""
        if len(self.messages) <= MAX_MESSAGES:
            return
        # Drop from the front until under limit; prefer dropping full user turns
        while len(self.messages) > MAX_MESSAGES:
            self.messages.pop(0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "messages": self.messages,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "message_count": len(self.messages),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationState":
        return cls(
            conversation_id=data["conversation_id"],
            messages=list(data.get("messages") or []),
            created_at=float(data.get("created_at") or time.time()),
            updated_at=float(data.get("updated_at") or time.time()),
            metadata=dict(data.get("metadata") or {}),
        )

    def save(self) -> None:
        path = _persist_dir() / f"{self.conversation_id}.json"
        path.write_text(json.dumps(self.to_dict(), default=str), encoding="utf-8")

    @classmethod
    def load(cls, conversation_id: str) -> Optional["ConversationState"]:
        path = _persist_dir() / f"{conversation_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls.from_dict(data)
        except (json.JSONDecodeError, OSError, KeyError):
            return None


def get_or_create_conversation(conversation_id: str) -> ConversationState:
    with _lock:
        _purge_expired_unlocked()
        state = _conversations.get(conversation_id)
        if state is None:
            loaded = ConversationState.load(conversation_id)
            state = loaded or ConversationState(conversation_id=conversation_id)
            _conversations[conversation_id] = state
        state.touch()
        return state


def get_conversation(conversation_id: str) -> Optional[ConversationState]:
    with _lock:
        if conversation_id in _conversations:
            return _conversations[conversation_id]
        loaded = ConversationState.load(conversation_id)
        if loaded:
            _conversations[conversation_id] = loaded
        return loaded


def save_conversation(conversation_id: str) -> bool:
    with _lock:
        state = _conversations.get(conversation_id)
        if not state:
            return False
        state.save()
        return True


def clear_conversation(conversation_id: str) -> bool:
    with _lock:
        existed = conversation_id in _conversations
        _conversations.pop(conversation_id, None)
        path = _persist_dir() / f"{conversation_id}.json"
        if path.exists():
            path.unlink(missing_ok=True)
            existed = True
        return existed


def list_conversation_ids() -> list[str]:
    with _lock:
        ids = set(_conversations.keys())
        for p in _persist_dir().glob("*.json"):
            ids.add(p.stem)
        return sorted(ids)


def _purge_expired_unlocked() -> None:
    now = time.time()
    expired = [
        cid
        for cid, st in _conversations.items()
        if now - st.updated_at > CONVERSATION_TTL_SECONDS
    ]
    for cid in expired:
        _conversations.pop(cid, None)
