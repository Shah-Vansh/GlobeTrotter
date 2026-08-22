"""
City model.
Represents a searchable destination that can be added as a Stop on a Trip.
Includes a cost index and popularity score used for sorting/filtering on the
City Search screen.
"""
from app.extensions import db


class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    country = db.Column(db.String(120), nullable=False, index=True)
    region = db.Column(db.String(120), nullable=True)  # e.g. "Europe", "South Asia"
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

    # Relative cost of visiting the city (1 = cheap, 10 = very expensive).
    cost_index = db.Column(db.Float, default=5.0)
    # Popularity score used to power "Top Regional Selections".
    popularity = db.Column(db.Integer, default=0)

    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # --- Relationships ---
    activities = db.relationship("Activity", backref="city", lazy=True)
    stops = db.relationship("Stop", backref="city", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "region": self.region,
            "description": self.description,
            "image_url": self.image_url,
            "cost_index": self.cost_index,
            "popularity": self.popularity,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def __repr__(self):
        return f"<City {self.name}, {self.country}>"
