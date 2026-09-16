"""
Map successful MCP tool results to existing GlobeTrotter frontend routes.

No new pages — only paths the React app already has:
  /trips/:id

Important: stop/itinerary API payloads have their own `id` fields.
Those are NOT trip ids. Prefer:
  1) arguments["trip_id"] for nested tools
  2) data["id"] only for create_trip / get_trip / update_trip responses
"""

from __future__ import annotations

from typing import Any, Optional

# Trip-level tools: response `id` is the trip id
_TRIP_ENTITY_TOOLS = {
    "create_trip",
    "get_trip",
    "update_trip",
    "get_trip_budget",
    "share_trip",
    "unshare_trip",
    "delete_trip",
}

# Nested tools: must use arguments.trip_id (response.id is stop/entry id)
_NESTED_TOOLS = {
    "add_stop_to_trip",
    "update_stop",
    "remove_stop",
    "reorder_stops",
    "add_activity_to_itinerary",
    "update_itinerary_activity",
    "remove_activity_from_itinerary",
    "list_itinerary",
}

_NAV_TOOLS = _TRIP_ENTITY_TOOLS | _NESTED_TOOLS


def _as_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _trip_id_from_result(
    tool_name: str,
    arguments: dict,
    tool_result: dict,
) -> Optional[int]:
    args = arguments or {}
    data = tool_result.get("data")

    # Nested mutations: never trust response.id (that's stop/entry id)
    if tool_name in _NESTED_TOOLS:
        return _as_int(args.get("trip_id"))

    # Trip entity tools: response body is the trip
    if tool_name in _TRIP_ENTITY_TOOLS:
        if isinstance(data, dict):
            tid = _as_int(data.get("trip_id")) or _as_int(data.get("id"))
            if tid is not None:
                return tid
        return _as_int(args.get("trip_id"))

    return _as_int(args.get("trip_id"))


def extract_navigation(
    tool_name: str,
    arguments: dict,
    tool_result: dict,
) -> Optional[dict[str, Any]]:
    """
    Return { path, label, tool, trip_id } for the React client, or None.
    Uses existing /trips/:id route only.
    """
    if not tool_result.get("success"):
        return None
    if tool_name not in _NAV_TOOLS:
        return None

    trip_id = _trip_id_from_result(tool_name, arguments, tool_result)
    if trip_id is None:
        return None

    return {
        "path": f"/trips/{trip_id}",
        "label": "Open trip",
        "tool": tool_name,
        "trip_id": trip_id,
    }
