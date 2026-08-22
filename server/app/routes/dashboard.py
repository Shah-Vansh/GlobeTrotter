"""
Dashboard routes.
Powers the Dashboard / Home screen with a single aggregate call: recent and
upcoming trips, recommended destinations (popular cities), and budget
highlights - saving the frontend from stitching several requests together.
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import Trip, City
from app.utils.responses import success

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("", methods=["GET"])
@jwt_required()
def get_dashboard():
    """GET /api/dashboard - everything the Home screen needs in one payload."""
    user_id = get_jwt_identity()

    trips = Trip.query.filter_by(user_id=user_id).all()

    recent_trips = sorted(trips, key=lambda t: t.created_at, reverse=True)[:5]
    upcoming_trips = sorted(
        [t for t in trips if t.status == "upcoming"], key=lambda t: t.start_date
    )[:5]

    # "Recommended destinations" = most popular cities on the platform.
    recommended = (
        City.query.order_by(City.popularity.desc()).limit(6).all()
    )

    # Budget highlights across all of the user's trips.
    total_planned_spend = round(sum(t.total_budget for t in trips), 2)
    status_counts = {"ongoing": 0, "upcoming": 0, "completed": 0}
    for t in trips:
        status_counts[t.status] += 1

    return success(
        {
            "recent_trips": [t.to_dict() for t in recent_trips],
            "upcoming_trips": [t.to_dict() for t in upcoming_trips],
            "recommended_destinations": [c.to_dict() for c in recommended],
            "budget_highlights": {
                "total_planned_spend": total_planned_spend,
                "trip_count": len(trips),
                "trips_by_status": status_counts,
            },
        }
    )
