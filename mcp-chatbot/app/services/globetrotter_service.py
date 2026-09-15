"""
HTTP client that talks to the existing GlobeTrotter Flask backend.

All MCP tools must go through this service so we never re-implement
business logic and we always respect the same auth / validation rules.
"""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from app.config import get_settings
from app.utils.logger import get_logger, get_ai_logger

logger = get_logger(__name__)
ai_logger = get_ai_logger()


class GlobeTrotterAPIError(Exception):
    """Raised when the GlobeTrotter backend returns an error status."""

    def __init__(self, status_code: int, message: str, payload: Any = None):
        self.status_code = status_code
        self.message = message
        self.payload = payload
        super().__init__(f"[{status_code}] {message}")


class GlobeTrotterService:
    """Thin async HTTP client for the existing GlobeTrotter APIs."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        settings = get_settings()
        self.base_url = (base_url or settings.globetrotter_api_url).rstrip("/")
        self.timeout = timeout if timeout is not None else settings.api_timeout_seconds

    def _headers(self, access_token: Optional[str] = None) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        access_token: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        start = time.perf_counter()
        rid = request_id or "-"

        logger.info(
            "API_REQUEST request_id=%s method=%s endpoint=%s",
            rid,
            method.upper(),
            path,
        )
        ai_logger.info(
            "API_REQUEST request_id=%s method=%s endpoint=%s",
            rid,
            method.upper(),
            path,
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json,
                    headers=self._headers(access_token),
                )
        except httpx.RequestError as exc:
            latency = time.perf_counter() - start
            logger.error(
                "API_ERROR request_id=%s method=%s endpoint=%s error=%s latency=%.3fs",
                rid,
                method.upper(),
                path,
                str(exc),
                latency,
            )
            raise GlobeTrotterAPIError(0, f"Network error talking to GlobeTrotter: {exc}") from exc

        latency = time.perf_counter() - start
        logger.info(
            "API_RESPONSE request_id=%s method=%s endpoint=%s status=%s latency=%.3fs",
            rid,
            method.upper(),
            path,
            response.status_code,
            latency,
        )
        ai_logger.info(
            "API_RESPONSE request_id=%s status=%s latency=%.3fs",
            rid,
            response.status_code,
            latency,
        )

        try:
            payload = response.json()
        except Exception:
            payload = {"raw": response.text}

        if response.status_code >= 400:
            message = (
                payload.get("message")
                if isinstance(payload, dict)
                else f"HTTP {response.status_code}"
            )
            raise GlobeTrotterAPIError(response.status_code, str(message), payload)

        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]
        return payload

    async def search_destinations(
        self,
        *,
        search: Optional[str] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        min_cost: Optional[float] = None,
        max_cost: Optional[float] = None,
        sort_by: str = "popularity",
        order: str = "desc",
        group_by: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        params: dict[str, Any] = {"sort_by": sort_by, "order": order}
        if search:
            params["search"] = search
        if country:
            params["country"] = country
        if region:
            params["region"] = region
        if min_cost is not None:
            params["min_cost"] = min_cost
        if max_cost is not None:
            params["max_cost"] = max_cost
        if group_by:
            params["group_by"] = group_by
        return await self._request("GET", "/api/cities", params=params, request_id=request_id)

    async def get_destination_details(
        self, city_id: int, *, request_id: Optional[str] = None
    ) -> Any:
        return await self._request("GET", f"/api/cities/{city_id}", request_id=request_id)

    async def search_activities(
        self,
        *,
        search: Optional[str] = None,
        city_id: Optional[int] = None,
        category: Optional[str] = None,
        min_cost: Optional[float] = None,
        max_cost: Optional[float] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "rating",
        order: str = "desc",
        group_by: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        params: dict[str, Any] = {"sort_by": sort_by, "order": order}
        if search:
            params["search"] = search
        if city_id is not None:
            params["city_id"] = city_id
        if category:
            params["category"] = category
        if min_cost is not None:
            params["min_cost"] = min_cost
        if max_cost is not None:
            params["max_cost"] = max_cost
        if min_rating is not None:
            params["min_rating"] = min_rating
        if group_by:
            params["group_by"] = group_by
        return await self._request("GET", "/api/activities", params=params, request_id=request_id)

    async def get_activity_details(
        self, activity_id: int, *, request_id: Optional[str] = None
    ) -> Any:
        return await self._request(
            "GET", f"/api/activities/{activity_id}", request_id=request_id
        )

    async def list_trips(
        self,
        *,
        access_token: str,
        search: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "start_date",
        order: str = "desc",
        group_by: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        params: dict[str, Any] = {"sort_by": sort_by, "order": order}
        if search:
            params["search"] = search
        if status:
            params["status"] = status
        if group_by:
            params["group_by"] = group_by
        return await self._request(
            "GET", "/api/trips", params=params, access_token=access_token, request_id=request_id
        )

    async def create_trip(
        self,
        *,
        access_token: str,
        name: str,
        start_date: str,
        end_date: str,
        description: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        body: dict[str, Any] = {
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
        }
        if description is not None:
            body["description"] = description
        return await self._request(
            "POST", "/api/trips", json=body, access_token=access_token, request_id=request_id
        )

    async def get_trip(
        self, trip_id: int, *, access_token: str, request_id: Optional[str] = None
    ) -> Any:
        return await self._request(
            "GET",
            f"/api/trips/{trip_id}",
            access_token=access_token,
            request_id=request_id,
        )

    async def update_trip(
        self,
        trip_id: int,
        *,
        access_token: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if start_date is not None:
            body["start_date"] = start_date
        if end_date is not None:
            body["end_date"] = end_date
        return await self._request(
            "PUT",
            f"/api/trips/{trip_id}",
            json=body,
            access_token=access_token,
            request_id=request_id,
        )

    async def delete_trip(
        self, trip_id: int, *, access_token: str, request_id: Optional[str] = None
    ) -> Any:
        return await self._request(
            "DELETE",
            f"/api/trips/{trip_id}",
            access_token=access_token,
            request_id=request_id,
        )

    async def get_trip_budget(
        self,
        trip_id: int,
        *,
        access_token: str,
        daily_budget: Optional[float] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        params: dict[str, Any] = {}
        if daily_budget is not None:
            params["daily_budget"] = daily_budget
        return await self._request(
            "GET",
            f"/api/trips/{trip_id}/budget",
            params=params or None,
            access_token=access_token,
            request_id=request_id,
        )

    async def share_trip(
        self, trip_id: int, *, access_token: str, request_id: Optional[str] = None
    ) -> Any:
        return await self._request(
            "POST",
            f"/api/trips/{trip_id}/share",
            access_token=access_token,
            request_id=request_id,
        )

    async def unshare_trip(
        self, trip_id: int, *, access_token: str, request_id: Optional[str] = None
    ) -> Any:
        return await self._request(
            "POST",
            f"/api/trips/{trip_id}/unshare",
            access_token=access_token,
            request_id=request_id,
        )

    async def add_stop(
        self,
        trip_id: int,
        *,
        access_token: str,
        city_id: int,
        start_date: str,
        end_date: str,
        order_index: Optional[int] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        body: dict[str, Any] = {
            "city_id": city_id,
            "start_date": start_date,
            "end_date": end_date,
        }
        if order_index is not None:
            body["order_index"] = order_index
        return await self._request(
            "POST",
            f"/api/trips/{trip_id}/stops",
            json=body,
            access_token=access_token,
            request_id=request_id,
        )

    async def update_stop(
        self,
        trip_id: int,
        stop_id: int,
        *,
        access_token: str,
        city_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        body: dict[str, Any] = {}
        if city_id is not None:
            body["city_id"] = city_id
        if start_date is not None:
            body["start_date"] = start_date
        if end_date is not None:
            body["end_date"] = end_date
        return await self._request(
            "PUT",
            f"/api/trips/{trip_id}/stops/{stop_id}",
            json=body,
            access_token=access_token,
            request_id=request_id,
        )

    async def delete_stop(
        self,
        trip_id: int,
        stop_id: int,
        *,
        access_token: str,
        request_id: Optional[str] = None,
    ) -> Any:
        return await self._request(
            "DELETE",
            f"/api/trips/{trip_id}/stops/{stop_id}",
            access_token=access_token,
            request_id=request_id,
        )

    async def reorder_stops(
        self,
        trip_id: int,
        *,
        access_token: str,
        order: list[int],
        request_id: Optional[str] = None,
    ) -> Any:
        return await self._request(
            "PUT",
            f"/api/trips/{trip_id}/stops/reorder",
            json={"order": order},
            access_token=access_token,
            request_id=request_id,
        )

    async def list_itinerary(
        self,
        trip_id: int,
        stop_id: int,
        *,
        access_token: str,
        request_id: Optional[str] = None,
    ) -> Any:
        return await self._request(
            "GET",
            f"/api/trips/{trip_id}/stops/{stop_id}/itinerary",
            access_token=access_token,
            request_id=request_id,
        )

    async def add_itinerary_activity(
        self,
        trip_id: int,
        stop_id: int,
        *,
        access_token: str,
        activity_id: int,
        day_number: int,
        date: Optional[str] = None,
        start_time: Optional[str] = None,
        cost: Optional[float] = None,
        notes: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        body: dict[str, Any] = {
            "activity_id": activity_id,
            "day_number": day_number,
        }
        if date is not None:
            body["date"] = date
        if start_time is not None:
            body["start_time"] = start_time
        if cost is not None:
            body["cost"] = cost
        if notes is not None:
            body["notes"] = notes
        return await self._request(
            "POST",
            f"/api/trips/{trip_id}/stops/{stop_id}/itinerary",
            json=body,
            access_token=access_token,
            request_id=request_id,
        )

    async def update_itinerary_activity(
        self,
        trip_id: int,
        stop_id: int,
        entry_id: int,
        *,
        access_token: str,
        day_number: Optional[int] = None,
        date: Optional[str] = None,
        start_time: Optional[str] = None,
        cost: Optional[float] = None,
        notes: Optional[str] = None,
        order_index: Optional[int] = None,
        new_stop_id: Optional[int] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        body: dict[str, Any] = {}
        if day_number is not None:
            body["day_number"] = day_number
        if date is not None:
            body["date"] = date
        if start_time is not None:
            body["start_time"] = start_time
        if cost is not None:
            body["cost"] = cost
        if notes is not None:
            body["notes"] = notes
        if order_index is not None:
            body["order_index"] = order_index
        if new_stop_id is not None:
            body["stop_id"] = new_stop_id
        return await self._request(
            "PUT",
            f"/api/trips/{trip_id}/stops/{stop_id}/itinerary/{entry_id}",
            json=body,
            access_token=access_token,
            request_id=request_id,
        )

    async def delete_itinerary_activity(
        self,
        trip_id: int,
        stop_id: int,
        entry_id: int,
        *,
        access_token: str,
        request_id: Optional[str] = None,
    ) -> Any:
        return await self._request(
            "DELETE",
            f"/api/trips/{trip_id}/stops/{stop_id}/itinerary/{entry_id}",
            access_token=access_token,
            request_id=request_id,
        )


_service: Optional[GlobeTrotterService] = None


def get_globetrotter_service() -> GlobeTrotterService:
    global _service
    if _service is None:
        _service = GlobeTrotterService()
    return _service
