"""
Stop model.
A single city leg within a Trip (the Itinerary Builder's "Add Stop").
Stops are ordered via order_index so they can be reordered/drag-dropped
on the frontend, and each stop owns its own date range.
"""
from app.extensions import db


class Stop(db.Model):
    __tablename__ = "stops"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    order_index = db.Column(db.Integer, default=0)  # position of this stop within the trip

    # --- Relationships ---
    itinerary_activities = db.relationship(
        "ItineraryActivity", backref="stop", lazy=True, cascade="all, delete-orphan",
        order_by="ItineraryActivity.order_index",
    )

    @property
    def day_count(self) -> int:
        return (self.end_date - self.start_date).days + 1

    @property
    def subtotal(self) -> float:
        return round(sum(a.cost or 0.0 for a in self.itinerary_activities), 2)

    def to_dict(self, include_activities: bool = False) -> dict:
        data = {
            "id": self.id,
            "trip_id": self.trip_id,
            "city_id": self.city_id,
            "city": self.city.to_dict() if self.city else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "order_index": self.order_index,
            "day_count": self.day_count,
            "subtotal": self.subtotal,
        }
        if include_activities:
            data["itinerary_activities"] = [a.to_dict() for a in self.itinerary_activities]
        return data

    def __repr__(self):
        return f"<Stop trip={self.trip_id} city={self.city_id}>"
