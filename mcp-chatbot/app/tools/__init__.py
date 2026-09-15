"""MCP tools – thin wrappers around existing GlobeTrotter APIs."""

from app.tools.destinations import get_destination_details, search_destinations
from app.tools.activities import get_activity_details, search_activities

__all__ = [
    "search_destinations",
    "get_destination_details",
    "search_activities",
    "get_activity_details",
]
