"""
Itinerary routes.
Manages day-wise ItineraryActivity entries within a Trip's Stops -
add/edit/remove/reorder activities per day, and move an activity between
days (recalculating budgets automatically since ItineraryActivity.cost
drives Trip.total_budget / Stop.subtotal).
Mounted at /api/trips/<trip_id>/stops/<stop_id>/itinerary/...
"""
from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Trip, Stop, Activity, ItineraryActivity
from app.utils.responses import success, error

itinerary_bp = Blueprint("itinerary", __name__)


def _get_owned_stop(trip_id, stop_id, user_id):
    """Fetch a Stop, verifying it belongs to a Trip owned by user_id."""
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return None, None
    stop = Stop.query.filter_by(id=stop_id, trip_id=trip_id).first()
    return trip, stop


@itinerary_bp.route("/<int:trip_id>/stops/<int:stop_id>/itinerary", methods=["GET"])
@jwt_required()
def list_itinerary(trip_id, stop_id):
    """GET .../itinerary - all activities for this stop, grouped by day."""
    user_id = get_jwt_identity()
    trip, stop = _get_owned_stop(trip_id, stop_id, user_id)
    if not trip or not stop:
        return error("Trip or stop not found.", 404)

    days = {}
    for entry in stop.itinerary_activities:
        days.setdefault(entry.day_number, []).append(entry.to_dict())
    return success({"stop": stop.to_dict(), "days": days})


@itinerary_bp.route("/<int:trip_id>/stops/<int:stop_id>/itinerary", methods=["POST"])
@jwt_required()
def add_itinerary_activity(trip_id, stop_id):
    """POST .../itinerary  body: { activity_id, day_number, date?, start_time?, cost?, notes? }"""
    user_id = get_jwt_identity()
    trip, stop = _get_owned_stop(trip_id, stop_id, user_id)
    if not trip or not stop:
        return error("Trip or stop not found.", 404)

    data = request.json or {}
    if not data.get("activity_id") or not data.get("day_number"):
        return error("activity_id and day_number are required.", 400)
    if not Activity.query.get(data["activity_id"]):
        return error("Activity not found.", 404)

    entry = ItineraryActivity(
        stop_id=stop.id,
        activity_id=data["activity_id"],
        day_number=data["day_number"],
        date=datetime.strptime(data["date"], "%Y-%m-%d").date() if data.get("date") else None,
        start_time=datetime.strptime(data["start_time"], "%H:%M").time() if data.get("start_time") else None,
        order_index=data.get("order_index", len(stop.itinerary_activities)),
        cost=data.get("cost"),
        notes=data.get("notes"),
    )
    db.session.add(entry)
    db.session.commit()
    return success(entry.to_dict(), message="Activity added to itinerary.", status_code=201)


@itinerary_bp.route(
    "/<int:trip_id>/stops/<int:stop_id>/itinerary/<int:entry_id>", methods=["PUT"]
)
@jwt_required()
def update_itinerary_activity(trip_id, stop_id, entry_id):
    """PUT .../itinerary/<entry_id> - edit, reorder, or MOVE to a different day/stop.

    Moving an activity to a different day (or even a different stop within
    the same trip) is done by changing day_number / stop_id here; because
    cost is read from this same row, the day and trip totals recompute
    automatically on the next GET of budget/itinerary - no separate
    "move" endpoint is required.
    """
    user_id = get_jwt_identity()
    trip, stop = _get_owned_stop(trip_id, stop_id, user_id)
    if not trip or not stop:
        return error("Trip or stop not found.", 404)

    entry = ItineraryActivity.query.filter_by(id=entry_id, stop_id=stop.id).first()
    if not entry:
        return error("Itinerary entry not found.", 404)

    data = request.json or {}
    if "day_number" in data:
        entry.day_number = data["day_number"]
    if "date" in data:
        entry.date = datetime.strptime(data["date"], "%Y-%m-%d").date() if data["date"] else None
    if "start_time" in data:
        entry.start_time = datetime.strptime(data["start_time"], "%H:%M").time() if data["start_time"] else None
    if "order_index" in data:
        entry.order_index = data["order_index"]
    if "cost" in data:
        entry.cost = data["cost"]
    if "notes" in data:
        entry.notes = data["notes"]
    if "stop_id" in data and data["stop_id"] != stop.id:
        # Move to a different stop within the SAME trip only.
        new_stop = Stop.query.filter_by(id=data["stop_id"], trip_id=trip.id).first()
        if not new_stop:
            return error("Target stop not found on this trip.", 404)
        entry.stop_id = new_stop.id

    db.session.commit()
    return success(entry.to_dict(), message="Itinerary entry updated.")


@itinerary_bp.route(
    "/<int:trip_id>/stops/<int:stop_id>/itinerary/<int:entry_id>", methods=["DELETE"]
)
@jwt_required()
def delete_itinerary_activity(trip_id, stop_id, entry_id):
    """DELETE .../itinerary/<entry_id>"""
    user_id = get_jwt_identity()
    trip, stop = _get_owned_stop(trip_id, stop_id, user_id)
    if not trip or not stop:
        return error("Trip or stop not found.", 404)

    entry = ItineraryActivity.query.filter_by(id=entry_id, stop_id=stop.id).first()
    if not entry:
        return error("Itinerary entry not found.", 404)

    db.session.delete(entry)
    db.session.commit()
    return success(message="Activity removed from itinerary.")
