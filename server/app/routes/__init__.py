"""
Routes package.
`register_blueprints(app)` is called once from the app factory
(app/__init__.py) to wire every blueprint onto the Flask app under a
consistent /api prefix.
"""


def register_blueprints(app):
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.cities import cities_bp
    from app.routes.activities import activities_bp
    from app.routes.trips import trips_bp
    from app.routes.itinerary import itinerary_bp
    from app.routes.community import community_bp
    from app.routes.calendar import calendar_bp
    from app.routes.admin import admin_bp
    from app.routes.export import export_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(health_bp, url_prefix="/api/health")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(cities_bp, url_prefix="/api/cities")
    app.register_blueprint(activities_bp, url_prefix="/api/activities")
    app.register_blueprint(trips_bp, url_prefix="/api/trips")
    app.register_blueprint(itinerary_bp, url_prefix="/api/trips")
    app.register_blueprint(community_bp, url_prefix="/api/community")
    app.register_blueprint(calendar_bp, url_prefix="/api/calendar")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(export_bp, url_prefix="/api/export")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
