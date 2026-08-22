"""
Small helpers for consistent JSON API responses across all blueprints.
Keeping the shape of success/error payloads identical makes the frontend's
axios interceptor logic (src/configs/api.js) simple and predictable.
"""
from flask import jsonify


def success(data=None, message="Success", status_code=200):
    """Standard success envelope: { success, message, data }."""
    payload = {"success": True, "message": message, "data": data}
    return jsonify(payload), status_code


def error(message="Something went wrong", status_code=400, errors=None):
    """Standard error envelope: { success, message, errors }."""
    payload = {"success": False, "message": message, "errors": errors}
    return jsonify(payload), status_code
