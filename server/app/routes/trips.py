"""
Trip routes.
Covers Create Trip, My Trips (Ongoing/Upcoming/Completed), trip CRUD,
Stop (city leg) management, budget breakdown, and public sharing -
the core of screens 3, 4, 6, 9 and 11 from the product spec.
"""
from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Trip, Stop, City
from app.utils.responses import success, error
from app.utils.decorators import get_current_user

trips_bp = Blueprint("trips", __name__)


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


# --- Trip CRUD ---

@trips_bp.route("", methods=["GET"])
@jwt_required()
def list_trips():
    """GET /api/trips?search=&status=&sort_by=&order=&group_by=status

    status filter: ongoing|upcoming|completed (derived property, filtered in Python
    since it depends on today's date rather than a stored column).
    """
    user_id = get_jwt_identity()
    query = Trip.query.filter_by(user_id=user_id)

    search = request.args.get("search")
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(Trip.name.ilike(like), Trip.description.ilike(like)))

    sort_by = request.args.get("sort_by", "start_date")
    order = request.args.get("order", "desc")
    sort_column = {"start_date": Trip.start_date, "name": Trip.name, "created_at": Trip.created_at}.get(
        sort_by, Trip.start_date
    )
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    trips = query.all()

    status_filter = request.args.get("status")
    if status_filter in ("ongoing", "upcoming", "completed"):
        trips = [t for t in trips if t.status == status_filter]

    group_by = request.args.get("group_by")
    if group_by == "status":
        groups = {"ongoing": [], "upcoming": [], "completed": []}
        for t in trips:
            groups[t.status].append(t.to_dict())
        return success({"groups": groups})

    return success([t.to_dict() for t in trips])


@trips_bp.route("", methods=["POST"])
@jwt_required()
def create_trip():
    """POST /api/trips - Create Trip screen. Accepts JSON or multipart (cover photo)."""
    user_id = get_jwt_identity()
    data = request.form if request.form else (request.json or {})

    required = ["name", "start_date", "end_date"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error(f"Missing required fields: {', '.join(missing)}", 400)

    try:
        start_date = _parse_date(data["start_date"])
        end_date = _parse_date(data["end_date"])
    except ValueError:
        return error("Dates must be in YYYY-MM-DD format.", 400)

    if end_date < start_date:
        return error("end_date cannot be before start_date.", 400)

    cover_photo_url = None
    if "cover_photo" in request.files:
        from app.utils.cloudinary_utils import upload_image

        cover_photo_url = upload_image(request.files["cover_photo"], folder="globetrotter/trips")

    trip = Trip(
        user_id=user_id,
        name=data["name"],
        description=data.get("description"),
        start_date=start_date,
        end_date=end_date,
        cover_photo_url=cover_photo_url,
    )
    db.session.add(trip)
    db.session.commit()
    return success(trip.to_dict(), message="Trip created.", status_code=201)


@trips_bp.route("/<int:trip_id>", methods=["GET"])
@jwt_required()
def get_trip(trip_id):
    """GET /api/trips/<id> - full trip with stops + itinerary (Itinerary View screen)."""
    user_id = get_jwt_identity()
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return error("Trip not found.", 404)
    return success(trip.to_dict(include_stops=True))


@trips_bp.route("/<int:trip_id>", methods=["PUT"])
@jwt_required()
def update_trip(trip_id):
    """PUT /api/trips/<id>"""
    user_id = get_jwt_identity()
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return error("Trip not found.", 404)

    data = request.json or {}
    if "name" in data:
        trip.name = data["name"]
    if "description" in data:
        trip.description = data["description"]
    if "start_date" in data:
        trip.start_date = _parse_date(data["start_date"])
    if "end_date" in data:
        trip.end_date = _parse_date(data["end_date"])
    if "cover_photo_url" in data:
        trip.cover_photo_url = data["cover_photo_url"]

    db.session.commit()
    return success(trip.to_dict(), message="Trip updated.")


@trips_bp.route("/<int:trip_id>", methods=["DELETE"])
@jwt_required()
def delete_trip(trip_id):
    """DELETE /api/trips/<id>"""
    user_id = get_jwt_identity()
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return error("Trip not found.", 404)
    db.session.delete(trip)
    db.session.commit()
    return success(message="Trip deleted.")


# --- Stops (Itinerary Builder: "Add Stop") ---

@trips_bp.route("/<int:trip_id>/stops", methods=["POST"])
@jwt_required()
def add_stop(trip_id):
    """POST /api/trips/<id>/stops  body: { city_id, start_date, end_date }"""
    user_id = get_jwt_identity()
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return error("Trip not found.", 404)

    data = request.json or {}
    if not data.get("city_id") or not data.get("start_date") or not data.get("end_date"):
        return error("city_id, start_date and end_date are required.", 400)
    if not City.query.get(data["city_id"]):
        return error("City not found.", 404)

    stop = Stop(
        trip_id=trip.id,
        city_id=data["city_id"],
        start_date=_parse_date(data["start_date"]),
        end_date=_parse_date(data["end_date"]),
        order_index=data.get("order_index", len(trip.stops)),
    )
    db.session.add(stop)
    db.session.commit()
    return success(stop.to_dict(), message="Stop added.", status_code=201)


@trips_bp.route("/<int:trip_id>/stops/reorder", methods=["PUT"])
@jwt_required()
def reorder_stops(trip_id):
    """PUT /api/trips/<id>/stops/reorder  body: { order: [stop_id, stop_id, ...] }"""
    user_id = get_jwt_identity()
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return error("Trip not found.", 404)

    order = (request.json or {}).get("order", [])
    stops_by_id = {s.id: s for s in trip.stops}
    for index, stop_id in enumerate(order):
        if stop_id in stops_by_id:
            stops_by_id[stop_id].order_index = index
    db.session.commit()
    return success([s.to_dict() for s in trip.stops], message="Stops reordered.")


@trips_bp.route("/<int:trip_id>/stops/<int:stop_id>", methods=["PUT"])
@jwt_required()
def update_stop(trip_id, stop_id):
    """PUT /api/trips/<id>/stops/<stop_id>"""
    user_id = get_jwt_identity()
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return error("Trip not found.", 404)
    stop = Stop.query.filter_by(id=stop_id, trip_id=trip_id).first()
    if not stop:
        return error("Stop not found.", 404)

    data = request.json or {}
    if "start_date" in data:
        stop.start_date = _parse_date(data["start_date"])
    if "end_date" in data:
        stop.end_date = _parse_date(data["end_date"])
    if "city_id" in data:
        stop.city_id = data["city_id"]
    db.session.commit()
    return success(stop.to_dict(), message="Stop updated.")


@trips_bp.route("/<int:trip_id>/stops/<int:stop_id>", methods=["DELETE"])
@jwt_required()
def delete_stop(trip_id, stop_id):
    """DELETE /api/trips/<id>/stops/<stop_id>"""
    user_id = get_jwt_identity()
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return error("Trip not found.", 404)
    stop = Stop.query.filter_by(id=stop_id, trip_id=trip_id).first()
    if not stop:
        return error("Stop not found.", 404)
    db.session.delete(stop)
    db.session.commit()
    return success(message="Stop removed.")


# --- Budget breakdown ---

@trips_bp.route("/<int:trip_id>/budget", methods=["GET"])
@jwt_required()
def get_budget(trip_id):
    """GET /api/trips/<id>/budget - Trip Budget & Cost Breakdown screen."""
    user_id = get_jwt_identity()
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return error("Trip not found.", 404)

    by_category = {}
    by_day = {}
    for stop in trip.stops:
        for entry in stop.itinerary_activities:
            cost = entry.cost if entry.cost is not None else (entry.activity.cost if entry.activity else 0)
            category = entry.activity.category if entry.activity else "other"
            by_category[category] = round(by_category.get(category, 0) + cost, 2)

            day_key = entry.date.isoformat() if entry.date else f"stop{stop.id}-day{entry.day_number}"
            by_day[day_key] = round(by_day.get(day_key, 0) + cost, 2)

    trip_days = max((trip.end_date - trip.start_date).days + 1, 1)
    average_per_day = round(trip.total_budget / trip_days, 2)

    return success(
        {
            "total_budget": trip.total_budget,
            "average_cost_per_day": average_per_day,
            "by_category": by_category,
            "by_day": by_day,
        }
    )


# --- Public sharing ---

@trips_bp.route("/<int:trip_id>/share", methods=["POST"])
@jwt_required()
def share_trip(trip_id):
    """POST /api/trips/<id>/share - toggle public sharing and generate a slug."""
    user_id = get_jwt_identity()
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return error("Trip not found.", 404)

    trip.is_public = True
    if not trip.share_slug:
        trip.generate_share_slug()
    db.session.commit()

    from flask import current_app

    share_url = f"{current_app.config.get('FRONTEND_URL')}/public/trips/{trip.share_slug}"
    return success({"share_url": share_url, "share_slug": trip.share_slug}, message="Trip is now shareable.")


@trips_bp.route("/<int:trip_id>/unshare", methods=["POST"])
@jwt_required()
def unshare_trip(trip_id):
    """POST /api/trips/<id>/unshare - revoke public access."""
    user_id = get_jwt_identity()
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return error("Trip not found.", 404)
    trip.is_public = False
    db.session.commit()
    return success(message="Trip is no longer public.")
