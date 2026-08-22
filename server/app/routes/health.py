"""
Health check route.
Simple, unauthenticated endpoint used by uptime monitors, load balancers,
and local dev ("is the backend even running?").
"""
from flask import Blueprint
from datetime import datetime

from app.extensions import db
from app.utils.responses import success, error

health_bp = Blueprint("health", __name__)


@health_bp.route("", methods=["GET"])
def health_check():
    """Return 200 + basic app/db status. GET /api/health"""
    db_status = "ok"
    try:
        # Lightweight query to confirm the DB connection is alive.
        db.session.execute(db.text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - we want to report any DB error
        db_status = f"error: {exc}"
        return error("Service unhealthy", 503, errors={"database": db_status})

    return success(
        {
            "status": "healthy",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat(),
        },
        message="GlobeTrotter API is running",
    )
