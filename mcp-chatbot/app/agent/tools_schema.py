"""
OpenAI / Groq compatible tool schemas for the agent loop.

Groq strictly validates tool arguments. Optional enum fields fail when the
model passes null. Strategy:
- Required fields: strict types (and enums only when required).
- Optional filters: plain string/number/integer, OR omitted from schema
  entirely when Python defaults are enough (e.g. list_trips).
- Agent still strips nulls before calling implementations.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from app.tools.activities import get_activity_details, search_activities
from app.tools.destinations import get_destination_details, search_destinations
from app.tools.trips import (
    add_activity_to_itinerary,
    add_stop_to_trip,
    create_trip,
    delete_trip,
    get_trip,
    get_trip_budget,
    list_itinerary,
    list_trips,
    remove_activity_from_itinerary,
    remove_stop,
    reorder_stops,
    share_trip,
    unshare_trip,
    update_itinerary_activity,
    update_stop,
    update_trip,
)

TOOL_IMPLEMENTATIONS: dict[str, Callable[..., Awaitable[dict]]] = {
    "search_destinations": search_destinations,
    "get_destination_details": get_destination_details,
    "search_activities": search_activities,
    "get_activity_details": get_activity_details,
    "list_trips": list_trips,
    "create_trip": create_trip,
    "get_trip": get_trip,
    "update_trip": update_trip,
    "delete_trip": delete_trip,
    "get_trip_budget": get_trip_budget,
    "share_trip": share_trip,
    "unshare_trip": unshare_trip,
    "add_stop_to_trip": add_stop_to_trip,
    "update_stop": update_stop,
    "remove_stop": remove_stop,
    "reorder_stops": reorder_stops,
    "list_itinerary": list_itinerary,
    "add_activity_to_itinerary": add_activity_to_itinerary,
    "update_itinerary_activity": update_itinerary_activity,
    "remove_activity_from_itinerary": remove_activity_from_itinerary,
}


def _fn(
    name: str,
    description: str,
    properties: dict | None = None,
    required: list[str] | None = None,
) -> dict:
    props = properties or {}
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


def get_tool_schemas() -> list[dict[str, Any]]:
    return [
        # ---- Public ----
        _fn(
            "search_destinations",
            "Search cities/destinations. Optional: search, country, region text filters.",
            {
                "search": {"type": "string", "description": "Free-text search query"},
                "country": {"type": "string"},
                "region": {"type": "string"},
            },
        ),
        _fn(
            "get_destination_details",
            "Get details for one city by city_id.",
            {"city_id": {"type": "integer"}},
            ["city_id"],
        ),
        _fn(
            "search_activities",
            "Search activities. Optional: search text, city_id, category.",
            {
                "search": {"type": "string"},
                "city_id": {"type": "integer"},
                "category": {"type": "string"},
            },
        ),
        _fn(
            "get_activity_details",
            "Get details for one activity by activity_id.",
            {"activity_id": {"type": "integer"}},
            ["activity_id"],
        ),
        # ---- Auth: trips ----
        # No optional params: model must call with {}. Python applies defaults.
        _fn(
            "list_trips",
            "List the logged-in user's trips. Call with empty arguments {}. Requires auth.",
            {},
        ),
        _fn(
            "create_trip",
            "Create a trip. Dates must be YYYY-MM-DD. Requires auth.",
            {
                "name": {"type": "string"},
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                "description": {"type": "string"},
            },
            ["name", "start_date", "end_date"],
        ),
        _fn(
            "get_trip",
            "Get full trip including stops and itinerary. Requires auth.",
            {"trip_id": {"type": "integer"}},
            ["trip_id"],
        ),
        _fn(
            "update_trip",
            "Update trip fields. Only pass fields you want to change. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
            },
            ["trip_id"],
        ),
        _fn(
            "delete_trip",
            "Delete a trip owned by the user. Requires auth.",
            {"trip_id": {"type": "integer"}},
            ["trip_id"],
        ),
        _fn(
            "get_trip_budget",
            "Get budget breakdown for a trip. Requires auth.",
            {"trip_id": {"type": "integer"}},
            ["trip_id"],
        ),
        _fn(
            "share_trip",
            "Make trip publicly shareable. Requires auth.",
            {"trip_id": {"type": "integer"}},
            ["trip_id"],
        ),
        _fn(
            "unshare_trip",
            "Revoke public sharing. Requires auth.",
            {"trip_id": {"type": "integer"}},
            ["trip_id"],
        ),
        # ---- Stops ----
        _fn(
            "add_stop_to_trip",
            "Add a city stop to a trip. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "city_id": {"type": "integer"},
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            ["trip_id", "city_id", "start_date", "end_date"],
        ),
        _fn(
            "update_stop",
            "Update a stop. Only pass fields to change. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "stop_id": {"type": "integer"},
                "city_id": {"type": "integer"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
            },
            ["trip_id", "stop_id"],
        ),
        _fn(
            "remove_stop",
            "Remove a stop from a trip. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "stop_id": {"type": "integer"},
            },
            ["trip_id", "stop_id"],
        ),
        _fn(
            "reorder_stops",
            "Reorder stops; order is an array of stop_id integers. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "order": {"type": "array", "items": {"type": "integer"}},
            },
            ["trip_id", "order"],
        ),
        # ---- Itinerary ----
        _fn(
            "list_itinerary",
            "List day-wise itinerary for a stop. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "stop_id": {"type": "integer"},
            },
            ["trip_id", "stop_id"],
        ),
        _fn(
            "add_activity_to_itinerary",
            "Add an activity to a stop's itinerary. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "stop_id": {"type": "integer"},
                "activity_id": {"type": "integer"},
                "day_number": {"type": "integer"},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "start_time": {"type": "string", "description": "HH:MM"},
                "cost": {"type": "number"},
                "notes": {"type": "string"},
            },
            ["trip_id", "stop_id", "activity_id", "day_number"],
        ),
        _fn(
            "update_itinerary_activity",
            "Update or move an itinerary entry. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "stop_id": {"type": "integer"},
                "entry_id": {"type": "integer"},
                "day_number": {"type": "integer"},
                "date": {"type": "string"},
                "start_time": {"type": "string"},
                "cost": {"type": "number"},
                "notes": {"type": "string"},
            },
            ["trip_id", "stop_id", "entry_id"],
        ),
        _fn(
            "remove_activity_from_itinerary",
            "Remove an activity from the itinerary. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "stop_id": {"type": "integer"},
                "entry_id": {"type": "integer"},
            },
            ["trip_id", "stop_id", "entry_id"],
        ),
    ]
