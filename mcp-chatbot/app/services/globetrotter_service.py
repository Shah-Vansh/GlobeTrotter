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

    def __init__(self, base_url: Optional[str] = None, timeout: float = 30.0):
        settings = get_settings()
        self.base_url = (base_url or settings.globetrotter_api_url).rstrip("/")
        self.timeout = timeout

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

        # GlobeTrotter success envelope is usually {"success": true, "data": ...}
        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]
        return payload

    # ------------------------------------------------------------------
    # Cities / Destinations (public)
    # ------------------------------------------------------------------

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
        """GET /api/cities – list/search cities."""
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "order": order,
        }
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
        self,
        city_id: int,
        *,
        request_id: Optional[str] = None,
    ) -> Any:
        """GET /api/cities/{id}."""
        return await self._request("GET", f"/api/cities/{city_id}", request_id=request_id)

    # ------------------------------------------------------------------
    # Activities (public)
    # ------------------------------------------------------------------

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
        """GET /api/activities."""
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "order": order,
        }
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
        self,
        activity_id: int,
        *,
        request_id: Optional[str] = None,
    ) -> Any:
        """GET /api/activities/{id}."""
        return await self._request(
            "GET", f"/api/activities/{activity_id}", request_id=request_id
        )


# Singleton-style helper used by tools
_service: Optional[GlobeTrotterService] = None


def get_globetrotter_service() -> GlobeTrotterService:
    global _service
    if _service is None:
        _service = GlobeTrotterService()
    return _service
