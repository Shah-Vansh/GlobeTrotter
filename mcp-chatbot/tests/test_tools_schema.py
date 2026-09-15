"""Ensure tool schemas stay aligned with implementations."""

from app.agent.tools_schema import TOOL_IMPLEMENTATIONS, get_tool_schemas

REQUIRED_PUBLIC = {
    "search_destinations",
    "get_destination_details",
    "search_activities",
    "get_activity_details",
}

REQUIRED_AUTH = {
    "list_trips",
    "create_trip",
    "get_trip",
    "update_trip",
    "delete_trip",
    "add_stop_to_trip",
    "list_itinerary",
    "add_activity_to_itinerary",
}


def test_all_implementations_have_schemas():
    schemas = get_tool_schemas()
    names = {s["function"]["name"] for s in schemas}
    for name in TOOL_IMPLEMENTATIONS:
        assert name in names, f"Missing schema for {name}"


def test_schemas_have_implementations():
    schemas = get_tool_schemas()
    for s in schemas:
        name = s["function"]["name"]
        assert name in TOOL_IMPLEMENTATIONS, f"Missing implementation for {name}"


def test_required_tools_present():
    names = set(TOOL_IMPLEMENTATIONS.keys())
    assert REQUIRED_PUBLIC.issubset(names)
    assert REQUIRED_AUTH.issubset(names)
