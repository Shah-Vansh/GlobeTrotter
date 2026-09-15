"""
MCP tools for destinations (cities).

These are thin wrappers around the existing public GlobeTrotter APIs:
  GET /api/cities
  GET /api/cities/{id}
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Optional

from app.services.globetrotter_service import (
    GlobeTrotterAPIError,
    get_globetrotter_service,
)
from app.utils.logger import get_logger, get_ai_logger

logger = get_logger(__name__)
ai_logger = get_ai_logger()


def _new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:8]}"


async def search_destinations(
    search: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    sort_by: str = "popularity",
    order: str = "desc",
    group_by: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search and list destinations (cities) available in GlobeTrotter.

    Mirrors the existing frontend City Search screen and GET /api/cities.

    Args:
        search: Free-text search matching city name or country (partial, case-insensitive).
        country: Filter by country name.
        region: Filter by region.
        min_cost: Minimum cost_index filter.
        max_cost: Maximum cost_index filter.
        sort_by: One of name | popularity | cost_index | country (default: popularity).
        order: asc or desc (default: desc).
        group_by: Optional grouping: region | country.

    Returns:
        Dictionary with success flag and the list (or grouped) of cities from the backend.
    """
    request_id = _new_request_id()
    start = time.perf_counter()

    logger.info("MCP_TOOL_START request_id=%s tool=search_destinations", request_id)
    ai_logger.info("MCP_TOOL_START request_id=%s tool=search_destinations", request_id)

    try:
        service = get_globetrotter_service()
        data = await service.search_destinations(
            search=search,
            country=country,
            region=region,
            min_cost=min_cost,
            max_cost=max_cost,
            sort_by=sort_by,
            order=order,
            group_by=group_by,
            request_id=request_id,
        )
        latency = time.perf_counter() - start
        logger.info(
            "MCP_TOOL_SUCCESS request_id=%s tool=search_destinations latency=%.3fs",
            request_id,
            latency,
        )
        ai_logger.info(
            "MCP_TOOL_SUCCESS request_id=%s tool=search_destinations latency=%.3fs",
            request_id,
            latency,
        )
        return {
            "success": True,
            "request_id": request_id,
            "data": data,
        }
    except GlobeTrotterAPIError as exc:
        latency = time.perf_counter() - start
        logger.error(
            "MCP_TOOL_ERROR request_id=%s tool=search_destinations error=%s latency=%.3fs",
            request_id,
            str(exc),
            latency,
        )
        ai_logger.error(
            "MCP_TOOL_ERROR request_id=%s tool=search_destinations error=%s",
            request_id,
            str(exc),
        )
        return {
            "success": False,
            "request_id": request_id,
            "error": str(exc),
            "status_code": exc.status_code,
        }
    except Exception as exc:  # noqa: BLE001
        latency = time.perf_counter() - start
        logger.exception(
            "MCP_TOOL_ERROR request_id=%s tool=search_destinations unexpected=%s latency=%.3fs",
            request_id,
            str(exc),
            latency,
        )
        return {
            "success": False,
            "request_id": request_id,
            "error": f"Unexpected error: {exc}",
        }


async def get_destination_details(city_id: int) -> dict[str, Any]:
    """
    Get full details for a single destination (city) by its ID.

    Mirrors GET /api/cities/{id}.

    Args:
        city_id: The numeric ID of the city.

    Returns:
        Dictionary with success flag and the city details from the backend.
    """
    request_id = _new_request_id()
    start = time.perf_counter()

    logger.info(
        "MCP_TOOL_START request_id=%s tool=get_destination_details city_id=%s",
        request_id,
        city_id,
    )
    ai_logger.info(
        "MCP_TOOL_START request_id=%s tool=get_destination_details city_id=%s",
        request_id,
        city_id,
    )

    try:
        service = get_globetrotter_service()
        data = await service.get_destination_details(city_id, request_id=request_id)
        latency = time.perf_counter() - start
        logger.info(
            "MCP_TOOL_SUCCESS request_id=%s tool=get_destination_details latency=%.3fs",
            request_id,
            latency,
        )
        ai_logger.info(
            "MCP_TOOL_SUCCESS request_id=%s tool=get_destination_details latency=%.3fs",
            request_id,
            latency,
        )
        return {
            "success": True,
            "request_id": request_id,
            "data": data,
        }
    except GlobeTrotterAPIError as exc:
        latency = time.perf_counter() - start
        logger.error(
            "MCP_TOOL_ERROR request_id=%s tool=get_destination_details error=%s latency=%.3fs",
            request_id,
            str(exc),
            latency,
        )
        return {
            "success": False,
            "request_id": request_id,
            "error": str(exc),
            "status_code": exc.status_code,
        }
    except Exception as exc:  # noqa: BLE001
        latency = time.perf_counter() - start
        logger.exception(
            "MCP_TOOL_ERROR request_id=%s tool=get_destination_details unexpected=%s",
            request_id,
            str(exc),
        )
        return {
            "success": False,
            "request_id": request_id,
            "error": f"Unexpected error: {exc}",
        }
