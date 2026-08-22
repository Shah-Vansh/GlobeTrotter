"""
Admin routes.
Powers the Admin / Analytics Dashboard: user management, and platform
analytics (popular cities, popular activities, trends), all restricted
via the admin_required decorator.
"""
from collections import Counter

from flask import Blueprint, request

from app.extensions import db
from app.models import User, Trip, Stop, ItineraryActivity, City, Activity
from app.utils.responses import success, error
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


# --- Manage Users ---

@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """GET /api/admin/users?search=&is_active="""
    query = User.query

    search = request.args.get("search")
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(User.username.ilike(like), User.email.ilike(like), User.first_name.ilike(like))
        )

    is_active = request.args.get("is_active")
    if is_active is not None:
        query = query.filter(User.is_active == (is_active.lower() == "true"))

    users = query.order_by(User.created_at.desc()).all()
    return success(
        [
            {**u.to_dict(include_private=True), "trip_count": len(u.trips)}
            for u in users
        ]
    )


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user_detail(user_id):
    """GET /api/admin/users/<id> - includes their trips for admin review."""
    user = User.query.get(user_id)
    if not user:
        return error("User not found.", 404)
    data = user.to_dict(include_private=True)
    data["trips"] = [t.to_dict() for t in user.trips]
    return success(data)


@admin_bp.route("/users/<int:user_id>/status", methods=["PUT"])
@admin_required
def update_user_status(user_id):
    """PUT /api/admin/users/<id>/status  body: { is_active: bool } - activate/deactivate."""
    user = User.query.get(user_id)
    if not user:
        return error("User not found.", 404)
    is_active = (request.json or {}).get("is_active")
    if is_active is None:
        return error("is_active is required.", 400)
    user.is_active = bool(is_active)
    db.session.commit()
    return success(user.to_dict(include_private=True), message="User status updated.")


# --- Analytics ---

@admin_bp.route("/analytics/popular-cities", methods=["GET"])
@admin_required
def popular_cities():
    """GET /api/admin/analytics/popular-cities - top cities by stop count across all trips."""
    counts = (
        db.session.query(City.name, City.country, db.func.count(Stop.id).label("stop_count"))
        .join(Stop, Stop.city_id == City.id)
        .group_by(City.id)
        .order_by(db.desc("stop_count"))
        .limit(10)
        .all()
    )
    return success([{"city": name, "country": country, "count": count} for name, country, count in counts])


@admin_bp.route("/analytics/popular-activities", methods=["GET"])
@admin_required
def popular_activities():
    """GET /api/admin/analytics/popular-activities - top activities by usage in itineraries."""
    counts = (
        db.session.query(Activity.name, Activity.category, db.func.count(ItineraryActivity.id).label("use_count"))
        .join(ItineraryActivity, ItineraryActivity.activity_id == Activity.id)
        .group_by(Activity.id)
        .order_by(db.desc("use_count"))
        .limit(10)
        .all()
    )
    return success(
        [{"activity": name, "category": category, "count": count} for name, category, count in counts]
    )


@admin_bp.route("/analytics/trends", methods=["GET"])
@admin_required
def user_trends():
    """GET /api/admin/analytics/trends - overall platform stats + trip status breakdown."""
    total_users = User.query.count()
    total_trips = Trip.query.count()
    total_active_users = User.query.filter_by(is_active=True).count()

    status_counter = Counter(t.status for t in Trip.query.all())

    return success(
        {
            "total_users": total_users,
            "active_users": total_active_users,
            "total_trips": total_trips,
            "trips_by_status": dict(status_counter),
            "total_cities": City.query.count(),
            "total_activities": Activity.query.count(),
        }
    )
