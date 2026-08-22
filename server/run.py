"""
Entry point for the GlobeTrotter Flask backend.
Loads environment variables, creates the Flask app via the
application factory, and starts the development server.
"""
import os
import sys

# Ensure the project root is importable regardless of where this
# script is invoked from.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables from .env BEFORE the app/config is created,
# so that os.getenv() calls inside app/config.py see the correct values.
load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    debug_mode = os.getenv("DEBUG", "True") == "True"
    app.run(debug=debug_mode, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
