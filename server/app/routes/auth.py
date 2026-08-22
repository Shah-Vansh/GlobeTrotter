"""
Auth routes: register, login, refresh, and "who am I".
Uses Flask-JWT-Extended for access + refresh tokens, matching the
Login/Registration screens in the product spec.
"""
import re

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)

from app.extensions import db
from app.models import User
from app.utils.responses import success, error
from app.utils.brevo_utils import send_welcome_email

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^[0-9+\-\s()]{7,20}$")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Create a new user account. POST /api/auth/register

    Expects multipart/form-data (so an optional profile photo can be
    attached) or plain JSON if no photo is being uploaded.
    """
    data = request.form if request.form else (request.json or {})

    required_fields = ["first_name", "last_name", "email", "username", "password"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return error(f"Missing required fields: {', '.join(missing)}", 400)

    email = data["email"].strip().lower()
    if not EMAIL_REGEX.match(email):
        return error("Invalid email address format.", 400)

    phone_number = data.get("phone_number", "").strip()
    if phone_number and not PHONE_REGEX.match(phone_number):
        return error("Invalid phone number format.", 400)

    if User.query.filter_by(email=email).first():
        return error("Email address is already registered.", 409)
    if User.query.filter_by(username=data["username"].strip()).first():
        return error("Username is already taken.", 409)

    # Optional profile photo upload via Cloudinary.
    profile_photo_url = None
    if "profile_photo" in request.files:
        from app.utils.cloudinary_utils import upload_image

        profile_photo_url = upload_image(request.files["profile_photo"], folder="globetrotter/profiles")

    user = User(
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
        email=email,
        username=data["username"].strip(),
        phone_number=phone_number or None,
        city=data.get("city"),
        country=data.get("country"),
        additional_info=data.get("additional_info"),
        profile_photo_url=profile_photo_url,
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    # Fire-and-forget welcome email; failures here must not break registration.
    try:
        send_welcome_email(user)
    except Exception:  # noqa: BLE001
        pass

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success(
        {
            "user": user.to_dict(include_private=True),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        message="Registration successful.",
        status_code=201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate a user by username/email + password. POST /api/auth/login"""
    data = request.json or {}
    identifier = (data.get("username") or data.get("email") or "").strip()
    password = data.get("password") or ""

    if not identifier or not password:
        return error("Username/email and password are required.", 400)

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return error("Invalid username or password.", 401)

    if not user.is_active:
        return error("This account has been deactivated. Contact support.", 403)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success(
        {
            "user": user.to_dict(include_private=True),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        message="Login successful.",
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Exchange a valid refresh token for a new access token. POST /api/auth/refresh"""
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return success({"access_token": new_access_token}, message="Token refreshed.")


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Return the currently authenticated user. GET /api/auth/me"""
    user = User.query.get(get_jwt_identity())
    if not user:
        return error("User not found.", 404)
    return success(user.to_dict(include_private=True))
