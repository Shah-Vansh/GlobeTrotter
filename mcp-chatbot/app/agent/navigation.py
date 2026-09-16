"""
Map successful MCP tool results to existing GlobeTrotter frontend routes.

No new pages — only paths the React app already has:
  /trips, /trips/:id, /search/cities, /search/activities
"""

from __future__ import annotations

from typing import Any, Optional

# Tools that should trigger in-app navigation after success (last one wins).
_NAV_TOOLS = {
    "create_trip",
    "get_trip",
    "update_trip",
    "add_stop_to_trip",
    "update_stop",
    "remove_stop",
    "reorder_stops",
    "add_activity_to_itinerary",
    "update_itinerary_activity",
    "remove_activity_from_itinerary",
    "get_trip_budget",
    "share_trip",
}


def _id_from_data(data: Any) -> Optional[int]:
    if isinstance(data, dict):
        for key in ("id", "trip_id"):
            if data.get(key) is not None:
                try:
                    return int(data[key])
                except (TypeError, ValueError):
                    pass
    return None


def extract_navigation(
    tool_name: str,
    arguments: dict,
    tool_result: dict,
) -> Optional[dict[str, Any]]:
    """
    Return { path, label, tool } for the React client, or None.
    Uses existing routes only.
    """
    if not tool_result.get("success"):
        return None
    if tool_name not in _NAV_TOOLS:
        return None

    data = tool_result.get("data")
    trip_id = _id_from_data(data)

    # Prefer trip_id from args when mutating nested resources
    if trip_id is None and arguments.get("trip_id") is not None:
        try:
            trip_id = int(arguments["trip_id"])
        except (TypeError, ValueError):
            trip_id = None

    if tool_name == "create_trip" and trip_id is not None:
        return {
            "path": f"/trips/{trip_id}",
            "label": "Open trip",
            "tool": tool_name,
            "trip_id": trip_id,
        }

    if trip_id is not None and tool_name in _NAV_TOOLS:
        return {
            "path": f"/trips/{trip_id}",
            "label": "Open trip",
            "tool": tool_name,
            "trip_id": trip_id,
        }

    return None
