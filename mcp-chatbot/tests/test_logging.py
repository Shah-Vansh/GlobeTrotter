"""Phase 8 – logging and metrics tests."""

from __future__ import annotations

import logging
from pathlib import Path

from app.services.metrics import MetricsRegistry
from app.utils.logger import get_ai_logger, get_logger, setup_logging


def test_setup_logging_creates_handlers(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    # Force re-init
    import app.utils.logger as logger_mod

    logger_mod._configured = False

    from app.config import get_settings

    get_settings.cache_clear()

    setup_logging()

    root = logging.getLogger()
    assert root.handlers, "root logger should have handlers"

    # Rotating file handlers should target the temp log dir
    log_files = list(Path(tmp_path).glob("*.log"))
    # Files may be created on first write; force a write
    get_logger("test").info("hello-app")
    get_ai_logger().info("hello-ai")

    names = {p.name for p in Path(tmp_path).glob("*.log")}
    assert "app.log" in names or any(tmp_path.iterdir())


def test_metrics_registry_counts():
    m = MetricsRegistry()
    m.record_request(
        success=True,
        latency_seconds=1.5,
        input_tokens=10,
        output_tokens=20,
        tool_calls=[
            {"tool": "search_destinations", "success": True},
            {"tool": "create_trip", "success": False},
        ],
        llm_calls=2,
    )
    m.record_request(success=False, latency_seconds=0.2, llm_errors=1)

    snap = m.snapshot()
    assert snap["requests"]["total"] == 2
    assert snap["requests"]["success"] == 1
    assert snap["requests"]["failed"] == 1
    assert snap["llm"]["input_tokens"] == 10
    assert snap["llm"]["output_tokens"] == 20
    assert snap["tools"]["calls"] == 2
    assert snap["tools"]["success"] == 1
    assert snap["tools"]["failures"] == 1
    assert snap["tools"]["by_name"]["search_destinations"] == 1
    assert snap["latency_seconds"]["samples"] == 2
    assert snap["latency_seconds"]["max"] >= 1.5


def test_metrics_reset():
    m = MetricsRegistry()
    m.record_request(success=True, latency_seconds=0.1)
    m.reset()
    snap = m.snapshot()
    assert snap["requests"]["total"] == 0
