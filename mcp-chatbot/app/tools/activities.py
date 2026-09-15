"""
MCP tools for activities.

Thin wrappers around the existing public GlobeTrotter APIs:
  GET /api/activities
  GET /api/activities/{id}
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


async def search_activities(
    search: Optional[str] = None,
    city_id: Optional[int] = None,
    category: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "rating",
    order: str = "desc",
    group_by: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search and list activities available in GlobeTrotter.

    Mirrors the existing frontend Activity Search screen and GET /api/activities.

    Args:
        search: Free-text search on activity name or description.
        city_id: Filter activities belonging to a specific city.
        category: Filter by category (e.g. sightseeing, food, adventure).
        min_cost: Minimum cost filter.
        max_cost: Maximum cost filter.
        min_rating: Minimum rating filter.
        sort_by: name | cost | rating | duration_minutes (default: rating).
        order: asc or desc (default: desc).
        group_by: Optional grouping by category.

    Returns:
        Dictionary with success flag and the list (or grouped) of activities.
    """
    request_id = _new_request_id()
    start = time.perf_counter()

    logger.info("MCP_TOOL_START request_id=%s tool=search_activities", request_id)
    ai_logger.info("MCP_TOOL_START request_id=%s tool=search_activities", request_id)

    try:
        service = get_globetrotter_service()
        data = await service.search_activities(
            search=search,
            city_id=city_id,
            category=category,
            min_cost=min_cost,
            max_cost=max_cost,
            min_rating=min_rating,
            sort_by=sort_by,
            order=order,
            group_by=group_by,
            request_id=request_id,
        )
        latency = time.perf_counter() - start
        logger.info(
            "MCP_TOOL_SUCCESS request_id=%s tool=search_activities latency=%.3fs",
            request_id,
            latency,
        )
        ai_logger.info(
            "MCP_TOOL_SUCCESS request_id=%s tool=search_activities latency=%.3fs",
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
            "MCP_TOOL_ERROR request_id=%s tool=search_activities error=%s latency=%.3fs",
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
            "MCP_TOOL_ERROR request_id=%s tool=search_activities unexpected=%s",
            request_id,
            str(exc),
        )
        return {
            "success": False,
            "request_id": request_id,
            "error": f"Unexpected error: {exc}",
        }


async def get_activity_details(activity_id: int) -> dict[str, Any]:
    """
    Get full details for a single activity by its ID.

    Mirrors GET /api/activities/{id}.

    Args:
        activity_id: The numeric ID of the activity.

    Returns:
        Dictionary with success flag and the activity details.
    """
    request_id = _new_request_id()
    start = time.perf_counter()

    logger.info(
        "MCP_TOOL_START request_id=%s tool=get_activity_details activity_id=%s",
        request_id,
        activity_id,
    )
    ai_logger.info(
        "MCP_TOOL_START request_id=%s tool=get_activity_details activity_id=%s",
        request_id,
        activity_id,
    )

    try:
        service = get_globetrotter_service()
        data = await service.get_activity_details(activity_id, request_id=request_id)
        latency = time.perf_counter() - start
        logger.info(
            "MCP_TOOL_SUCCESS request_id=%s tool=get_activity_details latency=%.3fs",
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
            "MCP_TOOL_ERROR request_id=%s tool=get_activity_details error=%s latency=%.3fs",
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
        logger.exception(
            "MCP_TOOL_ERROR request_id=%s tool=get_activity_details unexpected=%s",
            request_id,
            str(exc),
        )
        return {
            "success": False,
            "request_id": request_id,
            "error": f"Unexpected error: {exc}",
        }
