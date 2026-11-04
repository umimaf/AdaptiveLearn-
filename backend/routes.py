"""HTTP routes: server-rendered pages plus a small JSON API used by the frontend."""
import json
from collections import OrderedDict

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for

from backend import auth, services
from backend.db import get_db
from ml_engine.preprocessing import FORMATS

bp = Blueprint("main", __name__)

BOOL_PREFS = ("dyslexia_font", "high_contrast", "reduced_motion", "focus_mode", "tts_enabled")
ALLOWED_SCALES = (1.0, 1.2, 1.4)


def _safe_next(target):
    """Only allow local redirects after login."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = get_db()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        fmt = request.form.get("preferred_format", "text")
        if not name or not email or len(password) < 8:
            flash("Please enter your name, an email address and a password of at least 8 characters.", "danger")
        elif conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            flash("An account with that email already exists.", "danger")
        else:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, auth.hash_password(password)),
            )
            conn.execute(
                "INSERT INTO accessibility_preferences (user_id, preferred_format) VALUES (?, ?)",
                (cur.lastrowid, fmt if fmt in FORMATS else "text"),
            )
            conn.commit()
            auth.login_user(cur.lastrowid)
            flash("Welcome! Your learning dashboard is ready.", "success")
            return redirect(url_for("main.dashboard"))
    return render_template("auth.html", mode="register")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        row = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row and auth.check_password(row["password_hash"], password):
            auth.login_user(row["id"])
            return redirect(_safe_next(request.args.get("next")) or url_for("main.dashboard"))
        flash("Incorrect email or password.", "danger")
    return render_template("auth.html", mode="login")


@bp.route("/logout")
def logout():
    auth.logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@bp.route("/dashboard")
@auth.login_required
def dashboard():
    data = services.dashboard_data(get_db(), auth.current_user()["id"])
    return render_template("dashboard.html", d=data)


@bp.route("/library")
def library():
    conn = get_db()
    user = auth.current_user()
    pm = services.progress_map(conn, user["id"]) if user else {}
    subjects = OrderedDict()
    for t in services.list_topics(conn):
        subjects.setdefault(t["subject_name"], []).append(t)
    return render_template("library.html", subjects=subjects, pm=pm)


@bp.route("/topic/<int:topic_id>")
@auth.login_required
def topic(topic_id):
    conn = get_db()
    uid = auth.current_user()["id"]
    t = services.get_topic(conn, topic_id)
    if t is None:
        abort(404)
    difficulty, diff_source = services.recommended_difficulty(conn, uid, t)
    questions = services.pick_questions(conn, topic_id, difficulty)
    for q in questions:
        q["options"] = json.loads(q["options"])
    fmt, fmt_source = services.suggest_format(conn, uid, services.get_preferences(conn, uid))
    return render_template(
        "topic.html", t=t, questions=questions, difficulty=difficulty,
        difficulty_source=diff_source, default_format=fmt, format_source=fmt_source, formats=FORMATS,
    )


@bp.route("/settings")
def settings():
    user = auth.current_user()
    prefs = services.get_preferences(get_db(), user["id"]) if user else dict(services.DEFAULT_PREFS)
    return render_template("settings.html", p=prefs, formats=FORMATS)


# ---------------------------------------------------------------- JSON API
@bp.route("/api/quiz/<int:question_id>/submit", methods=["POST"])
@auth.login_required
def submit_answer(question_id):
    conn = get_db()
    uid = auth.current_user()["id"]
    q = conn.execute("SELECT * FROM quiz_questions WHERE id = ?", (question_id,)).fetchone()
    if q is None:
        return jsonify(error="question not found"), 404
    data = request.get_json(silent=True) or {}
    if data.get("selected") is None:
        return jsonify(error="a selected answer is required"), 400

    is_correct = services.record_attempt(
        conn, uid, q, data.get("selected"), data.get("time_taken"), data.get("format_used"),
    )
    bundle = services.refresh(conn, uid)  # trigger recommendations after every answer
    prog = bundle["progress"].get(q["topic_id"], {})
    return jsonify(
        correct=is_correct,
        correct_answer=q["answer"],
        explanation=q["explanation"],
        mastery=prog.get("mastery_score", 0),
        status=prog.get("status", "in_progress"),
        recommendations=bundle["recommendations"][:3],
    )


@bp.route("/api/tutor", methods=["POST"])
def tutor():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify(error="Please enter a question."), 400
    return jsonify(services.tutor_reply(get_db(), question))


@bp.route("/api/accessibility", methods=["GET", "POST"])
@auth.login_required
def accessibility_api():
    conn = get_db()
    uid = auth.current_user()["id"]
    if request.method == "POST":
        d = request.get_json(silent=True) or {}
        try:
            scale = float(d.get("font_scale", 1.0))
        except (TypeError, ValueError):
            scale = 1.0
        if scale not in ALLOWED_SCALES:
            scale = 1.0
        fmt = d.get("preferred_format", "text")
        if fmt not in FORMATS:
            fmt = "text"
        flags = [1 if d.get(k) else 0 for k in BOOL_PREFS]
        conn.execute(
            """INSERT INTO accessibility_preferences (user_id, dyslexia_font, font_scale, high_contrast,
               reduced_motion, focus_mode, tts_enabled, preferred_format)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                 dyslexia_font = excluded.dyslexia_font, font_scale = excluded.font_scale,
                 high_contrast = excluded.high_contrast, reduced_motion = excluded.reduced_motion,
                 focus_mode = excluded.focus_mode, tts_enabled = excluded.tts_enabled,
                 preferred_format = excluded.preferred_format""",
            (uid, flags[0], scale, flags[1], flags[2], flags[3], flags[4], fmt),
        )
        conn.commit()
    return jsonify(services.get_preferences(conn, uid))
