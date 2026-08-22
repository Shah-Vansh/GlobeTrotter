"""
Flask extension instances.
Declared here (separate from __init__.py) so that models and routes
can import `db`, `jwt`, etc. without causing circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
