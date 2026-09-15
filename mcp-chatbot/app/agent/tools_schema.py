"""
OpenAI / Groq compatible tool schemas for the agent loop.
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


def _fn(name: str, description: str, properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
            },
        },
    }


def get_tool_schemas() -> list[dict[str, Any]]:
    return [
        # Public
        _fn(
            "search_destinations",
            "Search cities/destinations in GlobeTrotter.",
            {
                "search": {"type": "string"},
                "country": {"type": "string"},
                "region": {"type": "string"},
                "min_cost": {"type": "number"},
                "max_cost": {"type": "number"},
                "sort_by": {
                    "type": "string",
                    "enum": ["name", "popularity", "cost_index", "country"],
                },
                "order": {"type": "string", "enum": ["asc", "desc"]},
                "group_by": {"type": "string", "enum": ["region", "country"]},
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
            "Search activities; optionally filter by city_id, category, cost, rating.",
            {
                "search": {"type": "string"},
                "city_id": {"type": "integer"},
                "category": {"type": "string"},
                "min_cost": {"type": "number"},
                "max_cost": {"type": "number"},
                "min_rating": {"type": "number"},
                "sort_by": {
                    "type": "string",
                    "enum": ["name", "cost", "rating", "duration_minutes"],
                },
                "order": {"type": "string", "enum": ["asc", "desc"]},
                "group_by": {"type": "string", "enum": ["category"]},
            },
        ),
        _fn(
            "get_activity_details",
            "Get details for one activity by activity_id.",
            {"activity_id": {"type": "integer"}},
            ["activity_id"],
        ),
        # Auth required – trips
        _fn(
            "list_trips",
            "List the logged-in user's trips. Requires authentication.",
            {
                "search": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["ongoing", "upcoming", "completed"],
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["start_date", "name", "created_at"],
                },
                "order": {"type": "string", "enum": ["asc", "desc"]},
                "group_by": {"type": "string", "enum": ["status"]},
            },
        ),
        _fn(
            "create_trip",
            "Create a new trip for the logged-in user. Dates YYYY-MM-DD. Requires auth.",
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
            "Update trip name/description/dates. Requires auth.",
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
            "Get budget breakdown by category and day. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "daily_budget": {"type": "number"},
            },
            ["trip_id"],
        ),
        _fn(
            "share_trip",
            "Make trip publicly shareable and return share URL. Requires auth.",
            {"trip_id": {"type": "integer"}},
            ["trip_id"],
        ),
        _fn(
            "unshare_trip",
            "Revoke public sharing. Requires auth.",
            {"trip_id": {"type": "integer"}},
            ["trip_id"],
        ),
        # Stops
        _fn(
            "add_stop_to_trip",
            "Add a city stop to a trip. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "city_id": {"type": "integer"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "order_index": {"type": "integer"},
            },
            ["trip_id", "city_id", "start_date", "end_date"],
        ),
        _fn(
            "update_stop",
            "Update a stop's city or dates. Requires auth.",
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
            "Reorder stops; order is a list of stop_id values. Requires auth.",
            {
                "trip_id": {"type": "integer"},
                "order": {
                    "type": "array",
                    "items": {"type": "integer"},
                },
            },
            ["trip_id", "order"],
        ),
        # Itinerary
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
            "Add an activity to a stop's itinerary on a given day. Requires auth.",
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
                "order_index": {"type": "integer"},
                "new_stop_id": {"type": "integer"},
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
