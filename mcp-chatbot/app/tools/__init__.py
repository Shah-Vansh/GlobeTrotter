"""MCP tools – thin wrappers around existing GlobeTrotter APIs."""

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

__all__ = [
    "search_destinations",
    "get_destination_details",
    "search_activities",
    "get_activity_details",
    "list_trips",
    "create_trip",
    "get_trip",
    "update_trip",
    "delete_trip",
    "get_trip_budget",
    "share_trip",
    "unshare_trip",
    "add_stop_to_trip",
    "update_stop",
    "remove_stop",
    "reorder_stops",
    "list_itinerary",
    "add_activity_to_itinerary",
    "update_itinerary_activity",
    "remove_activity_from_itinerary",
]
