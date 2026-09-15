"""
MCP tools for trips, stops, itinerary, budget, and sharing.

All of these call existing JWT-protected GlobeTrotter APIs only.
Access token is taken from request-scoped auth context (never invented).
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Optional

from app.services.globetrotter_service import (
    GlobeTrotterAPIError,
    get_globetrotter_service,
)
from app.utils.auth_context import require_access_token
from app.utils.logger import get_logger, get_ai_logger

logger = get_logger(__name__)
ai_logger = get_ai_logger()


def _rid() -> str:
    return f"req_{uuid.uuid4().hex[:8]}"


def _ok(request_id: str, data: Any) -> dict:
    return {"success": True, "request_id": request_id, "data": data}


def _err(request_id: str, exc: Exception, status: Optional[int] = None) -> dict:
    payload: dict[str, Any] = {
        "success": False,
        "request_id": request_id,
        "error": str(exc),
    }
    if status is not None:
        payload["status_code"] = status
    return payload


async def _run(tool_name: str, coro_factory):
    request_id = _rid()
    start = time.perf_counter()
    logger.info("MCP_TOOL_START request_id=%s tool=%s", request_id, tool_name)
    ai_logger.info("MCP_TOOL_START request_id=%s tool=%s", request_id, tool_name)
    try:
        token = require_access_token()
        data = await coro_factory(token, request_id)
        latency = time.perf_counter() - start
        logger.info(
            "MCP_TOOL_SUCCESS request_id=%s tool=%s latency=%.3fs",
            request_id,
            tool_name,
            latency,
        )
        ai_logger.info(
            "MCP_TOOL_SUCCESS request_id=%s tool=%s latency=%.3fs",
            request_id,
            tool_name,
            latency,
        )
        return _ok(request_id, data)
    except PermissionError as exc:
        return _err(request_id, exc, 401)
    except GlobeTrotterAPIError as exc:
        latency = time.perf_counter() - start
        logger.error(
            "MCP_TOOL_ERROR request_id=%s tool=%s error=%s latency=%.3fs",
            request_id,
            tool_name,
            str(exc),
            latency,
        )
        return _err(request_id, exc, exc.status_code)
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "MCP_TOOL_ERROR request_id=%s tool=%s unexpected=%s", request_id, tool_name, exc
        )
        return _err(request_id, exc)


# ---- Trips ----

async def list_trips(
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "start_date",
    order: str = "desc",
    group_by: Optional[str] = None,
) -> dict:
    """List the authenticated user's trips (GET /api/trips)."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().list_trips(
            access_token=token,
            search=search,
            status=status,
            sort_by=sort_by,
            order=order,
            group_by=group_by,
            request_id=rid,
        )

    return await _run("list_trips", _call)


async def create_trip(
    name: str,
    start_date: str,
    end_date: str,
    description: Optional[str] = None,
) -> dict:
    """Create a trip (POST /api/trips). Dates must be YYYY-MM-DD."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().create_trip(
            access_token=token,
            name=name,
            start_date=start_date,
            end_date=end_date,
            description=description,
            request_id=rid,
        )

    return await _run("create_trip", _call)


async def get_trip(trip_id: int) -> dict:
    """Get full trip with stops and itinerary (GET /api/trips/{id})."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().get_trip(
            trip_id, access_token=token, request_id=rid
        )

    return await _run("get_trip", _call)


async def update_trip(
    trip_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Update trip fields (PUT /api/trips/{id})."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().update_trip(
            trip_id,
            access_token=token,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            request_id=rid,
        )

    return await _run("update_trip", _call)


async def delete_trip(trip_id: int) -> dict:
    """Delete a trip (DELETE /api/trips/{id})."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().delete_trip(
            trip_id, access_token=token, request_id=rid
        )

    return await _run("delete_trip", _call)


async def get_trip_budget(trip_id: int, daily_budget: Optional[float] = None) -> dict:
    """Get budget breakdown (GET /api/trips/{id}/budget)."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().get_trip_budget(
            trip_id,
            access_token=token,
            daily_budget=daily_budget,
            request_id=rid,
        )

    return await _run("get_trip_budget", _call)


async def share_trip(trip_id: int) -> dict:
    """Make trip public and return share URL (POST .../share)."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().share_trip(
            trip_id, access_token=token, request_id=rid
        )

    return await _run("share_trip", _call)


async def unshare_trip(trip_id: int) -> dict:
    """Revoke public access (POST .../unshare)."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().unshare_trip(
            trip_id, access_token=token, request_id=rid
        )

    return await _run("unshare_trip", _call)


# ---- Stops ----

async def add_stop_to_trip(
    trip_id: int,
    city_id: int,
    start_date: str,
    end_date: str,
    order_index: Optional[int] = None,
) -> dict:
    """Add a city stop to a trip (POST /api/trips/{id}/stops)."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().add_stop(
            trip_id,
            access_token=token,
            city_id=city_id,
            start_date=start_date,
            end_date=end_date,
            order_index=order_index,
            request_id=rid,
        )

    return await _run("add_stop_to_trip", _call)


async def update_stop(
    trip_id: int,
    stop_id: int,
    city_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Update a stop (PUT .../stops/{stop_id})."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().update_stop(
            trip_id,
            stop_id,
            access_token=token,
            city_id=city_id,
            start_date=start_date,
            end_date=end_date,
            request_id=rid,
        )

    return await _run("update_stop", _call)


async def remove_stop(trip_id: int, stop_id: int) -> dict:
    """Remove a stop (DELETE .../stops/{stop_id})."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().delete_stop(
            trip_id, stop_id, access_token=token, request_id=rid
        )

    return await _run("remove_stop", _call)


async def reorder_stops(trip_id: int, order: list[int]) -> dict:
    """Reorder stops (PUT .../stops/reorder). order = list of stop ids."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().reorder_stops(
            trip_id, access_token=token, order=order, request_id=rid
        )

    return await _run("reorder_stops", _call)


# ---- Itinerary ----

async def list_itinerary(trip_id: int, stop_id: int) -> dict:
    """List itinerary activities for a stop, grouped by day."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().list_itinerary(
            trip_id, stop_id, access_token=token, request_id=rid
        )

    return await _run("list_itinerary", _call)


async def add_activity_to_itinerary(
    trip_id: int,
    stop_id: int,
    activity_id: int,
    day_number: int,
    date: Optional[str] = None,
    start_time: Optional[str] = None,
    cost: Optional[float] = None,
    notes: Optional[str] = None,
) -> dict:
    """Add activity to itinerary (POST .../itinerary)."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().add_itinerary_activity(
            trip_id,
            stop_id,
            access_token=token,
            activity_id=activity_id,
            day_number=day_number,
            date=date,
            start_time=start_time,
            cost=cost,
            notes=notes,
            request_id=rid,
        )

    return await _run("add_activity_to_itinerary", _call)


async def update_itinerary_activity(
    trip_id: int,
    stop_id: int,
    entry_id: int,
    day_number: Optional[int] = None,
    date: Optional[str] = None,
    start_time: Optional[str] = None,
    cost: Optional[float] = None,
    notes: Optional[str] = None,
    order_index: Optional[int] = None,
    new_stop_id: Optional[int] = None,
) -> dict:
    """Update or move an itinerary entry (PUT .../itinerary/{entry_id})."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().update_itinerary_activity(
            trip_id,
            stop_id,
            entry_id,
            access_token=token,
            day_number=day_number,
            date=date,
            start_time=start_time,
            cost=cost,
            notes=notes,
            order_index=order_index,
            new_stop_id=new_stop_id,
            request_id=rid,
        )

    return await _run("update_itinerary_activity", _call)


async def remove_activity_from_itinerary(
    trip_id: int, stop_id: int, entry_id: int
) -> dict:
    """Remove activity from itinerary (DELETE .../itinerary/{entry_id})."""

    async def _call(token: str, rid: str):
        return await get_globetrotter_service().delete_itinerary_activity(
            trip_id, stop_id, entry_id, access_token=token, request_id=rid
        )

    return await _run("remove_activity_from_itinerary", _call)
