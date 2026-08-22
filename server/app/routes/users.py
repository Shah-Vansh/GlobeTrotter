"""
User profile routes: view/update own profile, upload profile photo,
manage theme preference, and manage saved destinations.
Matches the "User Profile / Settings Screen" spec.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import User, City, SavedDestination
from app.utils.responses import success, error
from app.utils.decorators import get_current_user

users_bp = Blueprint("users", __name__)


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    """GET /api/users/me - fetch the logged-in user's full profile."""
    user = get_current_user()
    if not user:
        return error("User not found.", 404)
    return success(user.to_dict(include_private=True))


@users_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_profile():
    """PUT /api/users/me - update editable profile fields."""
    user = get_current_user()
    if not user:
        return error("User not found.", 404)

    data = request.json or {}
    editable_fields = [
        "first_name", "last_name", "phone_number", "city",
        "country", "additional_info", "language",
    ]
    for field in editable_fields:
        if field in data:
            setattr(user, field, data[field])

    # Email changes require uniqueness re-validation.
    new_email = data.get("email")
    if new_email and new_email.lower() != user.email:
        if User.query.filter_by(email=new_email.lower()).first():
            return error("Email address is already in use.", 409)
        user.email = new_email.lower()

    db.session.commit()
    return success(user.to_dict(include_private=True), message="Profile updated.")


@users_bp.route("/me/photo", methods=["POST"])
@jwt_required()
def upload_profile_photo():
    """POST /api/users/me/photo - upload/replace the profile photo via Cloudinary."""
    user = get_current_user()
    if "profile_photo" not in request.files:
        return error("No file uploaded under 'profile_photo'.", 400)

    from app.utils.cloudinary_utils import upload_image

    url = upload_image(request.files["profile_photo"], folder="globetrotter/profiles")
    user.profile_photo_url = url
    db.session.commit()
    return success({"profile_photo_url": url}, message="Profile photo updated.")


@users_bp.route("/me/theme", methods=["PUT"])
@jwt_required()
def update_theme():
    """PUT /api/users/me/theme - persist light/dark mode preference (themeSlice sync)."""
    user = get_current_user()
    theme = (request.json or {}).get("theme")
    if theme not in ("light", "dark"):
        return error("theme must be 'light' or 'dark'.", 400)
    user.theme_preference = theme
    db.session.commit()
    return success({"theme_preference": user.theme_preference}, message="Theme preference saved.")


@users_bp.route("/me/language", methods=["PUT"])
@jwt_required()
def update_language():
    """PUT /api/users/me/language - persist the user's preferred language (Settings screen)."""
    user = get_current_user()
    language = (request.json or {}).get("language")
    if not language or not isinstance(language, str) or len(language) > 10:
        return error("language must be a valid ISO code, e.g. 'en'.", 400)
    user.language = language.lower()
    db.session.commit()
    return success({"language": user.language}, message="Language preference saved.")


@users_bp.route("/me", methods=["DELETE"])
@jwt_required()
def delete_account():
    """DELETE /api/users/me - permanently delete the current account."""
    user = get_current_user()
    db.session.delete(user)
    db.session.commit()
    return success(message="Account deleted.")


# --- Saved destinations ---

@users_bp.route("/me/saved-destinations", methods=["GET"])
@jwt_required()
def list_saved_destinations():
    """GET /api/users/me/saved-destinations"""
    user_id = get_jwt_identity()
    saved = SavedDestination.query.filter_by(user_id=user_id).all()
    return success([s.to_dict() for s in saved])


@users_bp.route("/me/saved-destinations", methods=["POST"])
@jwt_required()
def add_saved_destination():
    """POST /api/users/me/saved-destinations  body: { city_id }"""
    user_id = get_jwt_identity()
    city_id = (request.json or {}).get("city_id")
    if not City.query.get(city_id):
        return error("City not found.", 404)

    existing = SavedDestination.query.filter_by(user_id=user_id, city_id=city_id).first()
    if existing:
        return error("City already saved.", 409)

    saved = SavedDestination(user_id=user_id, city_id=city_id)
    db.session.add(saved)
    db.session.commit()
    return success(saved.to_dict(), message="Destination saved.", status_code=201)


@users_bp.route("/me/saved-destinations/<int:saved_id>", methods=["DELETE"])
@jwt_required()
def remove_saved_destination(saved_id):
    """DELETE /api/users/me/saved-destinations/<id>"""
    user_id = get_jwt_identity()
    saved = SavedDestination.query.filter_by(id=saved_id, user_id=user_id).first()
    if not saved:
        return error("Saved destination not found.", 404)
    db.session.delete(saved)
    db.session.commit()
    return success(message="Removed from saved destinations.")
