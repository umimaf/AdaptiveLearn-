"""Application configuration. Override values with environment variables."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Change SECRET_KEY in any real deployment; it signs the session cookie.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DATABASE = os.environ.get(
        "ADAPTIVELEARN_DB", os.path.join(BASE_DIR, "database", "adaptivelearn.db")
    )
    TESTING = False
