"""
Models package.
Importing every model here means `from app.models import db` style
imports elsewhere always see the full mapped schema, which matters
for Flask-Migrate autogeneration and for seed.py.
"""
from app.extensions import db

from app.models.user import User
from app.models.city import City
from app.models.activity import Activity
from app.models.trip import Trip
from app.models.stop import Stop
from app.models.itinerary_activity import ItineraryActivity
from app.models.saved_destination import SavedDestination
from app.models.community import CommunityPost, CommunityComment, CommunityLike

__all__ = [
    "db",
    "User",
    "City",
    "Activity",
    "Trip",
    "Stop",
    "ItineraryActivity",
    "SavedDestination",
    "CommunityPost",
    "CommunityComment",
    "CommunityLike",
]
