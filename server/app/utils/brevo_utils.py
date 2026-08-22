"""
Brevo (formerly Sendinblue) email helper - pure API based, no SMTP.
Used for things like welcome emails on registration, trip-share
notifications, and "forgot password" flows.

Docs: https://developers.brevo.com/reference/sendtransacemail
"""
import requests
from flask import current_app

BREVO_ENDPOINT = "https://api.brevo.com/v3/smtp/email"


def send_email(to_email: str, to_name: str, subject: str, html_content: str) -> bool:
    """Send a transactional email via the Brevo REST API.

    Returns True on success (HTTP 2xx from Brevo), False otherwise.
    Never raises - email failures should not break the calling request
    (e.g. registration should still succeed even if the welcome email
    fails to send).
    """
    api_key = current_app.config.get("BREVO_API_KEY")
    if not api_key:
        current_app.logger.warning("BREVO_API_KEY not set - skipping email send.")
        return False

    payload = {
        "sender": {
            "name": current_app.config.get("BREVO_SENDER_NAME"),
            "email": current_app.config.get("BREVO_SENDER_EMAIL"),
        },
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content,
    }
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    try:
        response = requests.post(BREVO_ENDPOINT, json=payload, headers=headers, timeout=10)
        return response.status_code in (200, 201)
    except requests.RequestException as exc:
        current_app.logger.error(f"Brevo email send failed: {exc}")
        return False


def send_welcome_email(user) -> bool:
    """Convenience wrapper: welcome email fired after successful registration."""
    subject = "Welcome to GlobeTrotter! 🌍"
    html_content = f"""
        <h2>Welcome aboard, {user.first_name}!</h2>
        <p>Your GlobeTrotter account has been created successfully.</p>
        <p>Start planning your next multi-city adventure right away.</p>
    """
    return send_email(user.email, f"{user.first_name} {user.last_name}", subject, html_content)


def send_password_reset_email(user, reset_url: str) -> bool:
    """Convenience wrapper: password-reset link for the "Forgot Password" flow."""
    subject = "Reset your GlobeTrotter password"
    html_content = f"""
        <h2>Hi {user.first_name},</h2>
        <p>We received a request to reset your GlobeTrotter password.</p>
        <p>Click the link below to choose a new one. This link expires in 30 minutes:</p>
        <p><a href="{reset_url}">Reset my password</a></p>
        <p>If you didn't request this, you can safely ignore this email.</p>
    """
    return send_email(user.email, f"{user.first_name} {user.last_name}", subject, html_content)


def send_trip_shared_email(to_email: str, to_name: str, share_url: str) -> bool:
    """Convenience wrapper: notify someone a trip was shared with them."""
    subject = "A GlobeTrotter itinerary was shared with you"
    html_content = f"""
        <h2>You've got a new travel itinerary!</h2>
        <p>Check it out here: <a href="{share_url}">{share_url}</a></p>
    """
    return send_email(to_email, to_name, subject, html_content)
