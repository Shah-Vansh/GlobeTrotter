"""
Public (unauthenticated) routes.
Powers the "Shared/Public Itinerary View" screen: anyone with the link
can view a read-only version of a trip someone chose to make public.
"""
from flask import Blueprint

from app.models import Trip
from app.utils.responses import success, error

public_bp = Blueprint("public", __name__)


@public_bp.route("/trips/<string:share_slug>", methods=["GET"])
def get_public_trip(share_slug):
    """GET /api/public/trips/<share_slug> - read-only itinerary view."""
    trip = Trip.query.filter_by(share_slug=share_slug, is_public=True).first()
    if not trip:
        return error("This shared trip does not exist or is no longer public.", 404)

    data = trip.to_dict(include_stops=True)
    # Public viewers should not see the owning user's private info.
    data["owner"] = trip.owner.to_dict(include_private=False) if trip.owner else None
    return success(data)


@public_bp.route("/trips/<string:share_slug>/copy", methods=["POST"])
def copy_public_trip_hint(share_slug):
    """POST /api/public/trips/<share_slug>/copy

    Public "Copy Trip" affordance: since copying requires an authenticated
    owner, this endpoint simply validates the slug exists and returns the
    trip payload for the frontend to pre-fill a new (authenticated)
    Create Trip flow with.
    """
    trip = Trip.query.filter_by(share_slug=share_slug, is_public=True).first()
    if not trip:
        return error("This shared trip does not exist or is no longer public.", 404)
    return success(trip.to_dict(include_stops=True), message="Log in to copy this trip to your account.")
