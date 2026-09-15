"""Observability endpoints – metrics snapshot and health of logging."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from app.config import get_settings
from app.services.metrics import get_metrics

router = APIRouter(tags=["observability"])


@router.get("/metrics")
async def metrics():
    """In-process counters: requests, tokens, tools, latency."""
    return {"success": True, "data": get_metrics().snapshot()}


@router.post("/metrics/reset")
async def metrics_reset():
    """Reset counters (dev/ops only)."""
    get_metrics().reset()
    return {"success": True, "message": "Metrics reset."}


@router.get("/observability")
async def observability_status():
    """Confirm log files exist and report basic log directory status."""
    settings = get_settings()
    log_dir = Path(settings.log_dir)
    files = {}
    for name in ("app.log", "error.log", "ai.log"):
        path = log_dir / name
        if path.exists():
            files[name] = {
                "exists": True,
                "size_bytes": path.stat().st_size,
            }
        else:
            files[name] = {"exists": False, "size_bytes": 0}

    return {
        "success": True,
        "data": {
            "log_dir": str(log_dir.resolve()),
            "log_level": settings.log_level,
            "files": files,
            "metrics": get_metrics().snapshot(),
        },
    }
