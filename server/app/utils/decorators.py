"""
Custom route decorators layered on top of Flask-JWT-Extended.
`admin_required` enforces that only users with is_admin=True can hit
Admin Panel endpoints, returning a 403 for everyone else.
"""
from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.models import User
from app.utils.responses import error


def admin_required(fn):
    """Require a valid JWT AND an admin account to call the wrapped view."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return error("Admin privileges required.", 403)
        return fn(*args, **kwargs)

    return wrapper


def get_current_user():
    """Fetch the User row for the currently authenticated JWT identity."""
    user_id = get_jwt_identity()
    return User.query.get(user_id)
