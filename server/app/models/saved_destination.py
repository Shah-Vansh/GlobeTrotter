"""
SavedDestination model.
Lets a user bookmark a City to their profile ("saved destinations list"
on the User Profile / Settings screen) without it being tied to a trip.
"""
from datetime import datetime

from app.extensions import db


class SavedDestination(db.Model):
    __tablename__ = "saved_destinations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    city = db.relationship("City")

    __table_args__ = (
        db.UniqueConstraint("user_id", "city_id", name="uq_user_saved_city"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "city": self.city.to_dict() if self.city else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
