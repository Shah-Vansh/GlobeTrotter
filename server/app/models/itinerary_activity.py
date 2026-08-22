"""
ItineraryActivity model.
The join between a Stop and an Activity, scoped to a specific day of the
trip. This is what powers the Itinerary View's day-wise activity cards
and the automatic per-day / per-trip budget calculation. Storing `cost`
here (rather than only reading Activity.cost) lets a user override the
estimated cost with an actual spend without mutating the shared Activity.
"""
from app.extensions import db


class ItineraryActivity(db.Model):
    __tablename__ = "itinerary_activities"

    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey("stops.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)

    day_number = db.Column(db.Integer, nullable=False)  # 1-indexed day within the stop
    date = db.Column(db.Date, nullable=True)  # absolute calendar date, for the Calendar screen
    start_time = db.Column(db.Time, nullable=True)
    order_index = db.Column(db.Integer, default=0)  # position within the day, for reordering

    # Snapshot/override of the activity's cost for this specific trip.
    cost = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "stop_id": self.stop_id,
            "activity_id": self.activity_id,
            "activity": self.activity.to_dict() if self.activity else None,
            "day_number": self.day_number,
            "date": self.date.isoformat() if self.date else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "order_index": self.order_index,
            "cost": self.cost if self.cost is not None else (self.activity.cost if self.activity else 0),
            "notes": self.notes,
        }

    def __repr__(self):
        return f"<ItineraryActivity stop={self.stop_id} activity={self.activity_id} day={self.day_number}>"
