"""
Lightweight in-process metrics for Phase 8 observability.

Tracks request counts, token usage, latencies, and tool success/failure.
Not a replacement for Prometheus — sufficient for dev/ops dashboards via /api/metrics.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class MetricsSnapshot:
    started_at: float
    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    llm_calls: int = 0
    llm_errors: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    tool_calls: int = 0
    tool_success: int = 0
    tool_failures: int = 0
    latency_sum: float = 0.0
    latency_count: int = 0
    latency_max: float = 0.0
    tools_by_name: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def to_dict(self) -> dict[str, Any]:
        avg = (self.latency_sum / self.latency_count) if self.latency_count else 0.0
        return {
            "uptime_seconds": round(time.time() - self.started_at, 1),
            "requests": {
                "total": self.requests_total,
                "success": self.requests_success,
                "failed": self.requests_failed,
            },
            "llm": {
                "calls": self.llm_calls,
                "errors": self.llm_errors,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "total_tokens": self.total_tokens,
            },
            "tools": {
                "calls": self.tool_calls,
                "success": self.tool_success,
                "failures": self.tool_failures,
                "by_name": dict(self.tools_by_name),
            },
            "latency_seconds": {
                "avg": round(avg, 3),
                "max": round(self.latency_max, 3),
                "samples": self.latency_count,
            },
        }


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._snap = MetricsSnapshot(started_at=time.time())

    def record_request(
        self,
        *,
        success: bool,
        latency_seconds: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
        tool_calls: Optional[list[dict]] = None,
        llm_calls: int = 0,
        llm_errors: int = 0,
    ) -> None:
        with self._lock:
            s = self._snap
            s.requests_total += 1
            if success:
                s.requests_success += 1
            else:
                s.requests_failed += 1

            s.latency_sum += latency_seconds
            s.latency_count += 1
            if latency_seconds > s.latency_max:
                s.latency_max = latency_seconds

            s.llm_calls += llm_calls
            s.llm_errors += llm_errors
            s.input_tokens += input_tokens
            s.output_tokens += output_tokens
            s.total_tokens += input_tokens + output_tokens

            for tc in tool_calls or []:
                s.tool_calls += 1
                name = tc.get("tool") or "unknown"
                s.tools_by_name[name] += 1
                if tc.get("success"):
                    s.tool_success += 1
                else:
                    s.tool_failures += 1

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return self._snap.to_dict()

    def reset(self) -> None:
        with self._lock:
            self._snap = MetricsSnapshot(started_at=time.time())


_metrics: Optional[MetricsRegistry] = None


def get_metrics() -> MetricsRegistry:
    global _metrics
    if _metrics is None:
        _metrics = MetricsRegistry()
    return _metrics
