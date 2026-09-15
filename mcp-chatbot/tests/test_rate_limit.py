"""Rate limit middleware unit-style test via MetricsRegistry-style logic."""

from __future__ import annotations

import time
from collections import defaultdict, deque


def _would_block(hits: dict, client: str, limit: int, window: float) -> bool:
    now = time.monotonic()
    q = hits[client]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= limit:
        return True
    q.append(now)
    return False


def test_rate_limit_allows_under_threshold():
    hits: dict = defaultdict(deque)
    for _ in range(5):
        assert _would_block(hits, "1.2.3.4", limit=5, window=60.0) is False
    assert _would_block(hits, "1.2.3.4", limit=5, window=60.0) is True


def test_rate_limit_independent_per_client():
    hits: dict = defaultdict(deque)
    for _ in range(3):
        assert _would_block(hits, "a", limit=3, window=60.0) is False
    assert _would_block(hits, "a", limit=3, window=60.0) is True
    assert _would_block(hits, "b", limit=3, window=60.0) is False
