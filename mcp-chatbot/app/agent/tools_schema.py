"""
OpenAI / Groq compatible tool schemas for the agent loop.

These schemas describe the same capabilities exposed by the MCP server.
The agent uses them for tool calling; the underlying implementations live
in app.tools.* and also power the MCP server.
"""

from __future__ import annotations

from typing import Any, Callable, Awaitable

from app.tools.destinations import get_destination_details, search_destinations
from app.tools.activities import get_activity_details, search_activities

# Map tool name → async implementation
TOOL_IMPLEMENTATIONS: dict[str, Callable[..., Awaitable[dict]]] = {
    "search_destinations": search_destinations,
    "get_destination_details": get_destination_details,
    "search_activities": search_activities,
    "get_activity_details": get_activity_details,
}


def get_tool_schemas() -> list[dict[str, Any]]:
    """Return tool definitions in OpenAI function-calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": "search_destinations",
                "description": (
                    "Search and list destinations (cities) from GlobeTrotter. "
                    "Use when the user asks about cities, places to visit, or destinations."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search": {
                            "type": "string",
                            "description": "Free-text search on city name or country",
                        },
                        "country": {
                            "type": "string",
                            "description": "Filter by country name",
                        },
                        "region": {
                            "type": "string",
                            "description": "Filter by region",
                        },
                        "min_cost": {
                            "type": "number",
                            "description": "Minimum cost_index",
                        },
                        "max_cost": {
                            "type": "number",
                            "description": "Maximum cost_index",
                        },
                        "sort_by": {
                            "type": "string",
                            "enum": ["name", "popularity", "cost_index", "country"],
                            "description": "Sort field (default popularity)",
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Sort order (default desc)",
                        },
                        "group_by": {
                            "type": "string",
                            "enum": ["region", "country"],
                            "description": "Optional group by region or country",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_destination_details",
                "description": (
                    "Get full details for one destination by its numeric city_id. "
                    "Call after search_destinations when you need more info on a specific city."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city_id": {
                            "type": "integer",
                            "description": "Numeric city ID from search results",
                        },
                    },
                    "required": ["city_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_activities",
                "description": (
                    "Search and list activities in GlobeTrotter. "
                    "Optionally filter by city_id, category, cost, or rating."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search": {
                            "type": "string",
                            "description": "Free-text search on activity name or description",
                        },
                        "city_id": {
                            "type": "integer",
                            "description": "Filter activities for a specific city",
                        },
                        "category": {
                            "type": "string",
                            "description": "Category filter e.g. sightseeing, food, adventure",
                        },
                        "min_cost": {"type": "number"},
                        "max_cost": {"type": "number"},
                        "min_rating": {"type": "number"},
                        "sort_by": {
                            "type": "string",
                            "enum": ["name", "cost", "rating", "duration_minutes"],
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                        },
                        "group_by": {
                            "type": "string",
                            "enum": ["category"],
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_activity_details",
                "description": "Get full details for one activity by its numeric activity_id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "activity_id": {
                            "type": "integer",
                            "description": "Numeric activity ID",
                        },
                    },
                    "required": ["activity_id"],
                },
            },
        },
    ]
