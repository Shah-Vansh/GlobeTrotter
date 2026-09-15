"""
GlobeTrotter MCP Server (Phase 2).

Exposes real tools that call the existing GlobeTrotter backend APIs.
No LLM is involved here — this is pure MCP server + tool → API wiring.

Run standalone (stdio):
    python -m app.mcp.server

Or with the MCP CLI / Inspector:
    mcp run app/mcp/server.py
"""

from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP

from app.config import get_settings
from app.tools.activities import get_activity_details, search_activities
from app.tools.destinations import get_destination_details, search_destinations
from app.utils.logger import setup_logging, get_logger

# Ensure logging is ready when the server process starts
setup_logging()
logger = get_logger(__name__)
settings = get_settings()

mcp = FastMCP(
    settings.mcp_server_name,
    instructions=(
        "This MCP server exposes tools that wrap the existing GlobeTrotter "
        "travel-planning application APIs. Only capabilities that already "
        "exist in the GlobeTrotter backend are available. Do not invent "
        "booking, payment, or other unsupported operations."
    ),
)


# ---------------------------------------------------------------------------
# Destination tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def search_destinations_tool(
    search: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    sort_by: str = "popularity",
    order: str = "desc",
    group_by: Optional[str] = None,
) -> dict:
    """
    Search and list destinations (cities) from the GlobeTrotter application.

    Use this when the user wants to find cities/destinations to visit.
    Supports free-text search, country/region filters, cost range, sorting and grouping.
    """
    return await search_destinations(
        search=search,
        country=country,
        region=region,
        min_cost=min_cost,
        max_cost=max_cost,
        sort_by=sort_by,
        order=order,
        group_by=group_by,
    )


@mcp.tool()
async def get_destination_details_tool(city_id: int) -> dict:
    """
    Get full details for a single destination (city) by its numeric ID.

    Call this after search_destinations_tool when you need more information
    about a specific city returned from a search.
    """
    return await get_destination_details(city_id)


# ---------------------------------------------------------------------------
# Activity tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def search_activities_tool(
    search: Optional[str] = None,
    city_id: Optional[int] = None,
    category: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "rating",
    order: str = "desc",
    group_by: Optional[str] = None,
) -> dict:
    """
    Search and list activities available in GlobeTrotter.

    Optionally filter by city_id (after finding a destination), category,
    cost range or minimum rating. Mirrors the existing Activity Search screen.
    """
    return await search_activities(
        search=search,
        city_id=city_id,
        category=category,
        min_cost=min_cost,
        max_cost=max_cost,
        min_rating=min_rating,
        sort_by=sort_by,
        order=order,
        group_by=group_by,
    )


@mcp.tool()
async def get_activity_details_tool(activity_id: int) -> dict:
    """
    Get full details for a single activity by its numeric ID.
    """
    return await get_activity_details(activity_id)


if __name__ == "__main__":
    logger.info("Starting GlobeTrotter MCP server (stdio transport)")
    # Default transport is stdio — ideal for local MCP clients / Inspector
    mcp.run()
