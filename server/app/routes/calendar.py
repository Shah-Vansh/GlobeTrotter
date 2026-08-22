"""
Calendar routes.
Aggregates a user's trips and itinerary activities into a single feed of
calendar "events" for the Calendar View screen, scoped to a given month
(or an arbitrary date range) so the frontend can render month navigation.
"""
from datetime import datetime, date, timedelta

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import Trip
from app.utils.responses import success, error

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("", methods=["GET"])
@jwt_required()
def get_calendar():
    """GET /api/calendar?month=YYYY-MM  (defaults to current month)

    Returns two kinds of events:
    - "trip" events spanning the trip's full start_date -> end_date
    - "activity" events for any ItineraryActivity that has an explicit date
    """
    user_id = get_jwt_identity()

    month_param = request.args.get("month")
    if month_param:
        try:
            year, month = map(int, month_param.split("-"))
        except ValueError:
            return error("month must be formatted as YYYY-MM.", 400)
    else:
        today = date.today()
        year, month = today.year, today.month

    range_start = date(year, month, 1)
    range_end = date(year + (month == 12), (month % 12) + 1, 1) - timedelta(days=1)

    trips = Trip.query.filter_by(user_id=user_id).all()

    events = []
    for trip in trips:
        # Trip spans the calendar window at all?
        if trip.end_date >= range_start and trip.start_date <= range_end:
            events.append(
                {
                    "type": "trip",
                    "id": trip.id,
                    "title": trip.name,
                    "start_date": trip.start_date.isoformat(),
                    "end_date": trip.end_date.isoformat(),
                    "status": trip.status,
                }
            )
        for stop in trip.stops:
            for entry in stop.itinerary_activities:
                if entry.date and range_start <= entry.date <= range_end:
                    events.append(
                        {
                            "type": "activity",
                            "id": entry.id,
                            "trip_id": trip.id,
                            "title": entry.activity.name if entry.activity else "Activity",
                            "date": entry.date.isoformat(),
                            "start_time": entry.start_time.isoformat() if entry.start_time else None,
                            "city": stop.city.name if stop.city else None,
                        }
                    )

    return success({"month": f"{year:04d}-{month:02d}", "events": events})
