"""Helpers to keep multi-step tool results within reasonable context size."""

from __future__ import annotations

import json
from typing import Any

# Keep tool messages from exploding the LLM context on large city/activity lists
MAX_LIST_ITEMS = 12
MAX_JSON_CHARS = 6000


def compact_tool_result(payload: Any) -> str:
    """
    Serialise a tool result for the LLM, trimming oversized lists.

    Preserves success/error flags and request_id; truncates long data arrays.
    """
    if not isinstance(payload, dict):
        text = json.dumps(payload, default=str)
        return text[:MAX_JSON_CHARS] + ("…" if len(text) > MAX_JSON_CHARS else "")

    out: dict[str, Any] = {
        k: payload[k]
        for k in ("success", "request_id", "error", "status_code")
        if k in payload
    }

    data = payload.get("data")
    if data is None:
        text = json.dumps(out if out else payload, default=str)
        return text[:MAX_JSON_CHARS]

    out["data"] = _compact_data(data)
    text = json.dumps(out, default=str)
    if len(text) > MAX_JSON_CHARS:
        return text[:MAX_JSON_CHARS] + "…[truncated]"
    return text


def _compact_data(data: Any) -> Any:
    if isinstance(data, list):
        trimmed = data[:MAX_LIST_ITEMS]
        result: dict[str, Any] = {
            "items": trimmed,
            "returned": len(trimmed),
            "total_available": len(data),
        }
        if len(data) > MAX_LIST_ITEMS:
            result["note"] = (
                f"Showing first {MAX_LIST_ITEMS} of {len(data)} items. "
                "Use more specific filters if needed."
            )
        return result

    if isinstance(data, dict):
        # Grouped responses e.g. {"groups": {...}}
        if "groups" in data and isinstance(data["groups"], dict):
            groups_out = {}
            for key, items in list(data["groups"].items())[:8]:
                if isinstance(items, list):
                    groups_out[key] = items[:MAX_LIST_ITEMS]
                else:
                    groups_out[key] = items
            return {"groups": groups_out, "group_count": len(data["groups"])}
        return data

    return data
