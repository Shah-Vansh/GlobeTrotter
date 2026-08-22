"""
Application factory for the GlobeTrotter Flask backend.
Creates the Flask app, wires up extensions (db, migrate, jwt, cors),
registers every route blueprint, and sets up global JSON error handlers.
"""
from flask import Flask

from app.config import Config
from app.extensions import db, migrate, jwt, cors
from app.utils.responses import error


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # --- Models must be imported after db.init_app so they register on the metadata ---
    with app.app_context():
        from app import models  # noqa: F401

    # --- Blueprints ---
    from app.routes import register_blueprints
    from app.routes.public import public_bp

    register_blueprints(app)
    app.register_blueprint(public_bp, url_prefix="/api/public")

    # --- Global error handlers (keep responses consistent JSON, not HTML) ---
    @app.errorhandler(404)
    def not_found(e):
        return error("Resource not found.", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error("Method not allowed.", 405)

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return error("Internal server error.", 500)

    # --- JWT error handlers: return consistent JSON instead of default HTML ---
    @jwt.unauthorized_loader
    def missing_token(reason):
        return error("Authentication token is missing.", 401)

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return error("Authentication token is invalid.", 401)

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return error("Authentication token has expired.", 401)

    return app
