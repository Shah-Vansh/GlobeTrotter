"""
User model.
Represents a registered GlobeTrotter account (traveler or admin).
Passwords are never stored in plain text - only their bcrypt-style hash
(generated via werkzeug.security) is persisted.
"""
import uuid
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # --- Identity / login fields ---
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # --- Registration form fields (see Registration Page spec) ---
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(30), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    country = db.Column(db.String(120), nullable=True)
    additional_info = db.Column(db.Text, nullable=True)
    profile_photo_url = db.Column(db.String(500), nullable=True)

    # --- Preferences (persisted per-user, e.g. theme, language) ---
    theme_preference = db.Column(db.String(10), default="light")  # "light" | "dark"
    language = db.Column(db.String(10), default="en")  # ISO code, e.g. "en", "hi", "fr"

    # --- Access control ---
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relationships ---
    trips = db.relationship("Trip", backref="owner", lazy=True, cascade="all, delete-orphan")
    saved_destinations = db.relationship(
        "SavedDestination", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    community_posts = db.relationship(
        "CommunityPost", backref="author", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        """Hash and store the given plain-text password."""
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self, include_private: bool = False) -> dict:
        """Serialize the user for API responses.

        include_private=True adds fields only the owner/admin should see
        (email, phone) - public views (e.g. community posts) can omit them.
        """
        data = {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": f"{self.first_name} {self.last_name}",
            "profile_photo_url": self.profile_photo_url,
            "city": self.city,
            "country": self.country,
            "is_admin": self.is_admin,
            "theme_preference": self.theme_preference,
            "language": self.language,
        }
        if include_private:
            data.update(
                {
                    "email": self.email,
                    "phone_number": self.phone_number,
                    "additional_info": self.additional_info,
                    "is_active": self.is_active,
                    "created_at": self.created_at.isoformat() if self.created_at else None,
                }
            )
        return data

    def __repr__(self):
        return f"<User {self.username}>"
