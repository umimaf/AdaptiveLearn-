"""Flask application factory and entry point.

Run locally:
    python app.py
Then open http://127.0.0.1:5001
"""
import os

from flask import Flask

from backend import auth, services
from backend.db import close_db, get_db, init_db
from backend.routes import bp
from config import Config

# Maps stored accessibility flags to CSS classes on <body>.
CLASS_MAP = [
    ("dyslexia-font", "dyslexia_font"),
    ("high-contrast", "high_contrast"),
    ("reduced-motion", "reduced_motion"),
    ("focus-mode", "focus_mode"),
]


def create_app(overrides=None):
    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static",
    )
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    os.makedirs(os.path.dirname(os.path.abspath(app.config["DATABASE"])), exist_ok=True)
    init_db(app.config["DATABASE"])
    app.teardown_appcontext(close_db)
    app.register_blueprint(bp)

    @app.context_processor
    def inject_globals():
        """Make the user, their accessibility settings and CSS classes available everywhere."""
        user = auth.current_user()
        if user:
            prefs = services.get_preferences(get_db(), user["id"])
        else:
            prefs = dict(services.DEFAULT_PREFS)
        classes = [css for css, key in CLASS_MAP if prefs[key]]
        return {
            "user": user,
            "prefs": prefs,
            "a11y_classes": " ".join(classes),
            "a11y_scale": float(prefs["font_scale"]),
        }

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
