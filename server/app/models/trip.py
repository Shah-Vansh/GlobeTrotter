"""
Trip model.
The top-level container for a user's travel plan: a name, a date range,
a description/cover photo, and (via Stop) a sequence of cities to visit.
"""
import secrets
from datetime import datetime, date

from app.extensions import db


class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    cover_photo_url = db.Column(db.String(500), nullable=True)

    # Public sharing: when is_public is True, the trip can be viewed
    # read-only at /api/public/trips/<share_slug>.
    is_public = db.Column(db.Boolean, default=False)
    share_slug = db.Column(db.String(32), unique=True, nullable=True, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relationships ---
    stops = db.relationship(
        "Stop", backref="trip", lazy=True, cascade="all, delete-orphan",
        order_by="Stop.order_index",
    )
    community_posts = db.relationship("CommunityPost", backref="trip", lazy=True)

    def generate_share_slug(self) -> str:
        """Create a short, unique, URL-safe slug for public sharing."""
        self.share_slug = secrets.token_urlsafe(8)
        return self.share_slug

    @property
    def status(self) -> str:
        """Derive Ongoing / Upcoming / Completed from today's date."""
        today = date.today()
        if today < self.start_date:
            return "upcoming"
        if today > self.end_date:
            return "completed"
        return "ongoing"

    @property
    def total_budget(self) -> float:
        """Sum the cost of every itinerary activity across every stop."""
        total = 0.0
        for stop in self.stops:
            for entry in stop.itinerary_activities:
                if entry.cost is not None:
                    total += entry.cost
                elif entry.activity is not None:
                    # Fall back to the activity's base cost when this entry
                    # hasn't been given its own override (keeps this in sync
                    # with the /budget breakdown endpoint's logic).
                    total += entry.activity.cost or 0.0
        return round(total, 2)

    @property
    def destination_count(self) -> int:
        return len(self.stops)

    def to_dict(self, include_stops: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "cover_photo_url": self.cover_photo_url,
            "is_public": self.is_public,
            "share_slug": self.share_slug,
            "status": self.status,
            "destination_count": self.destination_count,
            "total_budget": self.total_budget,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_stops:
            data["stops"] = [s.to_dict(include_activities=True) for s in self.stops]
        return data

    def __repr__(self):
        return f"<Trip {self.name}>"
