"""Database layer: SQLite through the standard-library sqlite3 module.

The brief asked for SQLAlchemy. It was not available in the build environment,
so the schema is plain SQL. Each table maps directly onto an ORM model if you
migrate later.
"""
import sqlite3

from flask import current_app, g

from backend.content import seed_content

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'student',
    created_at    TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS accessibility_preferences (
    user_id          INTEGER PRIMARY KEY REFERENCES users(id),
    dyslexia_font    INTEGER DEFAULT 0,
    font_scale       REAL    DEFAULT 1.0,
    high_contrast    INTEGER DEFAULT 0,
    reduced_motion   INTEGER DEFAULT 0,
    focus_mode       INTEGER DEFAULT 0,
    tts_enabled      INTEGER DEFAULT 0,
    preferred_format TEXT    DEFAULT 'text'
);
CREATE TABLE IF NOT EXISTS subjects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT UNIQUE NOT NULL,
    description TEXT
);
CREATE TABLE IF NOT EXISTS topics (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id       INTEGER NOT NULL REFERENCES subjects(id),
    title            TEXT NOT NULL,
    difficulty_level INTEGER NOT NULL DEFAULT 1,
    order_index      INTEGER NOT NULL,
    prerequisite_id  INTEGER REFERENCES topics(id),
    simple_text      TEXT,
    detailed_text    TEXT,
    example_text     TEXT,
    visual_text      TEXT
);
CREATE TABLE IF NOT EXISTS quiz_questions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id   INTEGER NOT NULL REFERENCES topics(id),
    qtype      TEXT NOT NULL,
    difficulty INTEGER NOT NULL,
    prompt     TEXT NOT NULL,
    options    TEXT NOT NULL,
    answer     TEXT NOT NULL,
    explanation TEXT
);
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL REFERENCES users(id),
    question_id    INTEGER NOT NULL REFERENCES quiz_questions(id),
    selected       TEXT,
    is_correct     INTEGER NOT NULL,
    time_taken     REAL DEFAULT 0,
    attempt_number INTEGER NOT NULL,
    format_used    TEXT,
    created_at     TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_attempts_user_question ON quiz_attempts(user_id, question_id);
CREATE TABLE IF NOT EXISTS student_progress (
    user_id       INTEGER NOT NULL REFERENCES users(id),
    topic_id      INTEGER NOT NULL REFERENCES topics(id),
    mastery_score REAL DEFAULT 0,
    attempts      INTEGER DEFAULT 0,
    status        TEXT DEFAULT 'not_started',
    last_updated  TEXT,
    PRIMARY KEY (user_id, topic_id)
);
CREATE TABLE IF NOT EXISTS ml_recommendations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id),
    topic_id     INTEGER NOT NULL REFERENCES topics(id),
    rec_type     TEXT NOT NULL,
    score        REAL,
    model_source TEXT,
    generated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    """Return a per-request connection stored on Flask's `g` object."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(path):
    """Create tables and load the sample lessons if the database is new."""
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.execute(
        "UPDATE accessibility_preferences SET preferred_format = 'text' WHERE preferred_format = 'video'"
    )
    conn.execute("UPDATE quiz_attempts SET format_used = 'text' WHERE format_used = 'video'")
    seed_content(conn)
    conn.commit()
    conn.close()
