"""Authentication helpers: password hashing, session login and route protection."""
from functools import wraps

from flask import g, jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from backend.db import get_db


def hash_password(password):
    return generate_password_hash(password)


def check_password(password_hash, password):
    return check_password_hash(password_hash, password)


def login_user(user_id):
    session.clear()
    session["user_id"] = user_id


def logout_user():
    session.clear()


def current_user():
    """Return the logged-in user row, or None. Cached per request."""
    if "user" not in g:
        uid = session.get("user_id")
        g.user = (
            get_db().execute(
                "SELECT id, name, email, role FROM users WHERE id = ?", (uid,)
            ).fetchone()
            if uid
            else None
        )
    return g.user


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            if request.path.startswith("/api/"):
                return jsonify(error="login required"), 401
            return redirect(url_for("main.login", next=request.path))
        return view(*args, **kwargs)

    return wrapper
