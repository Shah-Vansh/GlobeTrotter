"""
Activity model.
Represents something a traveler can do at a City (sightseeing, food tour,
adventure activity, etc). Activities are browsed on the Activity Search
screen and attached to a Trip's itinerary via ItineraryActivity.
"""
from app.extensions import db


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(80), nullable=False, index=True)  # sightseeing, food, adventure...
    cost = db.Column(db.Float, default=0.0)
    duration_minutes = db.Column(db.Integer, default=60)
    rating = db.Column(db.Float, default=0.0)
    image_url = db.Column(db.String(500), nullable=True)

    # --- Relationships ---
    itinerary_entries = db.relationship("ItineraryActivity", backref="activity", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "city_id": self.city_id,
            "city_name": self.city.name if self.city else None,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "cost": self.cost,
            "duration_minutes": self.duration_minutes,
            "rating": self.rating,
            "image_url": self.image_url,
        }

    def __repr__(self):
        return f"<Activity {self.name}>"
