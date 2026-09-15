"""Auth enforcement: trip tools must fail without an access token."""

from __future__ import annotations

import pytest

from app.tools.trips import create_trip, list_trips, get_trip
from app.utils.auth_context import set_access_token


@pytest.mark.asyncio
async def test_list_trips_requires_auth():
    set_access_token(None)
    result = await list_trips()
    assert result["success"] is False
    assert result.get("status_code") == 401 or "auth" in result.get("error", "").lower()


@pytest.mark.asyncio
async def test_create_trip_requires_auth():
    set_access_token(None)
    result = await create_trip(
        name="Test",
        start_date="2026-12-01",
        end_date="2026-12-05",
    )
    assert result["success"] is False
    assert result.get("status_code") == 401 or "auth" in result.get("error", "").lower()


@pytest.mark.asyncio
async def test_get_trip_requires_auth():
    set_access_token(None)
    result = await get_trip(1)
    assert result["success"] is False
