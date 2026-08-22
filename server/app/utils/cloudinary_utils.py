"""
Cloudinary helper for uploading images (profile photos, trip cover photos,
community post images). Wraps the cloudinary SDK so routes only ever call
`upload_image(file_storage)` and get back a plain URL string.
"""
import cloudinary
import cloudinary.uploader

from flask import current_app


def _configure():
    """Configure the cloudinary SDK from the current Flask app's config.

    Called lazily (per-request) rather than at import time so that it
    always picks up values loaded from .env, even under the app factory
    pattern / testing configs.
    """
    cloudinary.config(
        cloud_name=current_app.config.get("CLOUDINARY_CLOUD_NAME"),
        api_key=current_app.config.get("CLOUDINARY_API_KEY"),
        api_secret=current_app.config.get("CLOUDINARY_API_SECRET"),
        secure=True,
    )


def upload_image(file_storage, folder="globetrotter"):
    """Upload a werkzeug FileStorage (from request.files) to Cloudinary.

    Returns the secure HTTPS URL of the uploaded image, or None if no
    file was provided.
    """
    if file_storage is None:
        return None

    _configure()
    result = cloudinary.uploader.upload(file_storage, folder=folder)
    return result.get("secure_url")


def delete_image(public_id):
    """Delete a previously uploaded image by its Cloudinary public_id."""
    _configure()
    return cloudinary.uploader.destroy(public_id)
