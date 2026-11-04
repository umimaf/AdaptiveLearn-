"""Business logic: quiz scoring, progress tracking, feature building,
adaptive difficulty, recommendations, dashboard data and the rule-based tutor."""
import json
import re
from collections import Counter
from datetime import datetime, timezone
from statistics import mean

from ml_engine import prediction, recommendation
from ml_engine.preprocessing import FORMATS, SUPPORT_THRESHOLD

MASTERY_TARGET = 0.8   # mean of the last 5 answers at or above this -> mastered
REVISION_BELOW = 0.5   # below this after 2+ attempts -> needs revision
SUPPORT_ALERT = 0.7    # support probability at or above this raises an alert

DEFAULT_PREFS = {
    "dyslexia_font": 0, "font_scale": 1.0, "high_contrast": 0, "reduced_motion": 0,
    "focus_mode": 0, "tts_enabled": 0, "preferred_format": "text",
}
STOPWORDS = {
    "the", "and", "for", "what", "how", "why", "with", "can", "you", "explain", "about",
    "does", "are", "this", "that", "tell", "me", "give", "please", "question", "questions",
    "practice", "summary", "summarise", "summarize", "example", "examples", "is", "a", "an",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- preferences
def get_preferences(conn, user_id):
    row = conn.execute(
        "SELECT * FROM accessibility_preferences WHERE user_id = ?", (user_id,)
    ).fetchone()
    return dict(row) if row else dict(DEFAULT_PREFS)


# ---------------------------------------------------------------- content
def list_topics(conn):
    rows = conn.execute(
        """SELECT t.*, s.name AS subject_name
           FROM topics t JOIN subjects s ON s.id = t.subject_id
           ORDER BY s.id, t.order_index"""
    ).fetchall()
    return [dict(r) for r in rows]


def get_topic(conn, topic_id):
    row = conn.execute(
        """SELECT t.*, s.name AS subject_name
           FROM topics t JOIN subjects s ON s.id = t.subject_id WHERE t.id = ?""",
        (topic_id,),
    ).fetchone()
    return dict(row) if row else None


def pick_questions(conn, topic_id, difficulty):
    """Return up to two questions closest to the recommended difficulty."""
    rows = conn.execute("SELECT * FROM quiz_questions WHERE topic_id = ?", (topic_id,)).fetchall()
    rows = sorted(rows, key=lambda q: (abs(q["difficulty"] - difficulty), q["id"]))
    return [dict(q) for q in rows[:2]]


# ---------------------------------------------------------------- attempts & progress
def _recent_correctness(conn, user_id, topic_id, limit):
    rows = conn.execute(
        """SELECT a.is_correct FROM quiz_attempts a
           JOIN quiz_questions q ON q.id = a.question_id
           WHERE a.user_id = ? AND q.topic_id = ? ORDER BY a.id DESC LIMIT ?""",
        (user_id, topic_id, limit),
    ).fetchall()
    return [r[0] for r in rows]


def update_progress(conn, user_id, topic_id):
    recent = _recent_correctness(conn, user_id, topic_id, 5)
    total = conn.execute(
        """SELECT COUNT(*) FROM quiz_attempts a JOIN quiz_questions q ON q.id = a.question_id
           WHERE a.user_id = ? AND q.topic_id = ?""",
        (user_id, topic_id),
    ).fetchone()[0]
    mastery = sum(recent) / len(recent) if recent else 0.0
    if total >= 3 and mastery >= MASTERY_TARGET:
        status = "mastered"
    elif total >= 2 and mastery < REVISION_BELOW:
        status = "needs_revision"
    else:
        status = "in_progress"
    conn.execute(
        """INSERT INTO student_progress (user_id, topic_id, mastery_score, attempts, status, last_updated)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(user_id, topic_id) DO UPDATE SET
             mastery_score = excluded.mastery_score, attempts = excluded.attempts,
             status = excluded.status, last_updated = excluded.last_updated""",
        (user_id, topic_id, round(mastery, 3), total, status, now_iso()),
    )


def record_attempt(conn, user_id, question, selected, time_taken, format_used):
    """Score an answer, store the attempt, update progress. Returns True if correct."""
    selected = str(selected or "").strip()
    is_correct = selected.lower() == question["answer"].strip().lower()
    n = conn.execute(
        "SELECT COUNT(*) FROM quiz_attempts WHERE user_id = ? AND question_id = ?",
        (user_id, question["id"]),
    ).fetchone()[0]
    fmt = format_used if format_used in FORMATS else "text"
    conn.execute(
        """INSERT INTO quiz_attempts (user_id, question_id, selected, is_correct, time_taken,
           attempt_number, format_used, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, question["id"], selected, int(is_correct), float(time_taken or 0),
         n + 1, fmt, now_iso()),
    )
    update_progress(conn, user_id, question["topic_id"])
    conn.commit()
    return is_correct


def progress_map(conn, user_id):
    rows = conn.execute("SELECT * FROM student_progress WHERE user_id = ?", (user_id,)).fetchall()
    return {r["topic_id"]: dict(r) for r in rows}


# ---------------------------------------------------------------- ML feature building
def _attempt_rows(conn, user_id, topic_id=None):
    sql = """SELECT a.question_id, a.is_correct, a.time_taken, a.format_used, q.topic_id
             FROM quiz_attempts a JOIN quiz_questions q ON q.id = a.question_id
             WHERE a.user_id = ?"""
    params = [user_id]
    if topic_id is not None:
        sql += " AND q.topic_id = ?"
        params.append(topic_id)
    return conn.execute(sql + " ORDER BY a.id", params).fetchall()


def _repeat_rate(rows):
    """Share of wrong answers on a question the student had already got wrong."""
    seen_wrong, repeats, wrong = set(), 0, 0
    for r in rows:
        if not r["is_correct"]:
            wrong += 1
            if r["question_id"] in seen_wrong:
                repeats += 1
            seen_wrong.add(r["question_id"])
    return repeats / wrong if wrong else 0.0


def build_student_features(conn, user_id):
    rows = _attempt_rows(conn, user_id)
    if not rows:
        return None
    n_topics = len({r["topic_id"] for r in rows})
    return {
        "student_score_mean": mean(r["is_correct"] for r in rows),
        "student_time_mean": mean(r["time_taken"] for r in rows),
        "student_attempt_rate": len(rows) / n_topics,
        "student_repeat_rate": _repeat_rate(rows),
    }


def build_topic_features(conn, user_id, topic):
    rows = _attempt_rows(conn, user_id, topic["id"])
    if not rows:
        return None
    scores = [r["is_correct"] for r in rows]
    trend = mean(scores[-3:]) - mean(scores[:-3]) if len(scores) >= 4 else 0.0
    fmts = Counter(r["format_used"] for r in rows if r["format_used"])
    fmt = fmts.most_common(1)[0][0] if fmts else "text"
    return {
        "topic_score_mean": mean(scores),
        "topic_attempts": len(rows),
        "topic_avg_time": mean(r["time_taken"] for r in rows),
        "topic_repeat_rate": _repeat_rate(rows),
        "topic_trend": trend,
        "format_idx": FORMATS.index(fmt),
        "difficulty": topic["difficulty_level"],
    }


def _support_signal(conn, user_id, topic):
    """Return (probability, source). Uses the Random Forest if trained, else the baseline rule."""
    s = build_student_features(conn, user_id)
    t = build_topic_features(conn, user_id, topic)
    if s is None or t is None:
        return None, "insufficient_data"
    prob = prediction.predict_support(s, t)
    if prob is not None:
        return prob, "random_forest"
    return (1.0 if t["topic_score_mean"] < SUPPORT_THRESHOLD else 0.0), "baseline"


def support_signals(conn, user_id, topics, pm):
    out = {}
    for t in topics:
        p = pm.get(t["id"])
        if p is None or p["status"] == "mastered":
            continue
        out[t["id"]] = _support_signal(conn, user_id, t)
    return out


def _profile_name(conn, user_id):
    s = build_student_features(conn, user_id)
    if s is None or not prediction.is_available():
        return None
    return prediction.student_cluster_name(s)


# ---------------------------------------------------------------- adaptivity
def recommended_difficulty(conn, user_id, topic):
    """Start from the topic's level, adjust from recent accuracy, then lower it if support is likely."""
    recent = _recent_correctness(conn, user_id, topic["id"], 3)
    adjust = 0
    if len(recent) >= 3 and sum(recent) / len(recent) >= 0.8:
        adjust += 1
    elif len(recent) >= 2 and sum(recent) / len(recent) < 0.5:
        adjust -= 1
    source = "baseline"
    prob, sig_source = _support_signal(conn, user_id, topic)
    if prob is not None and sig_source == "random_forest":
        source = "random_forest"
        if prob >= SUPPORT_ALERT:
            adjust -= 1
    level = min(3, max(1, topic["difficulty_level"] + adjust))
    return level, source


def suggest_format(conn, user_id, prefs):
    """Pick the format with the best quiz accuracy once there is enough data; else use the preference."""
    rows = conn.execute(
        """SELECT format_used, AVG(is_correct) AS acc, COUNT(*) AS n FROM quiz_attempts
           WHERE user_id = ? GROUP BY format_used HAVING n >= 3""",
        (user_id,),
    ).fetchall()
    if rows:
        best = max(rows, key=lambda r: r["acc"])
        return best["format_used"], "quiz_results"
    return prefs["preferred_format"], "preference"


# ---------------------------------------------------------------- recommendations
def refresh(conn, user_id):
    """Recompute recommendations from current data, store them, and return a summary bundle."""
    topics = list_topics(conn)
    by_id = {t["id"]: t for t in topics}
    pm = progress_map(conn, user_id)
    signals = support_signals(conn, user_id, topics, pm)

    recs = []

    def add(topic, rec_type, score, source):
        recs.append({"topic_id": topic["id"], "title": topic["title"], "type": rec_type,
                     "score": score, "source": source})

    nxt = recommendation.rule_based_next(topics, pm)
    if nxt:
        add(nxt, "next_topic", None, "baseline")
    for t in recommendation.revision_topics(topics, pm):
        add(t, "revision", round(pm[t["id"]]["mastery_score"], 3), "baseline")
    for tid, (prob, src) in signals.items():
        if prob is not None and prob >= SUPPORT_ALERT:
            add(by_id[tid], "support_alert", round(prob, 3), src)
    for t, score in recommendation.content_based_rank(topics, pm)[:3]:
        add(t, "content_based", round(score, 3), "content_similarity")

    conn.execute("DELETE FROM ml_recommendations WHERE user_id = ?", (user_id,))
    conn.executemany(
        """INSERT INTO ml_recommendations (user_id, topic_id, rec_type, score, model_source, generated_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [(user_id, r["topic_id"], r["type"], r["score"], r["source"], now_iso()) for r in recs],
    )
    conn.commit()
    return {"topics": topics, "progress": pm, "signals": signals,
            "recommendations": recs, "profile": _profile_name(conn, user_id)}


def dashboard_data(conn, user_id):
    b = refresh(conn, user_id)
    topics, pm, recs = b["topics"], b["progress"], b["recommendations"]

    row = conn.execute(
        "SELECT COUNT(*) AS n, AVG(is_correct) AS acc FROM quiz_attempts WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    accuracy = round(row["acc"] * 100) if row["acc"] is not None else None
    completed = sum(1 for p in pm.values() if p["status"] == "mastered")

    probs = [p for p, _ in b["signals"].values() if p is not None]
    sources = {s for _, s in b["signals"].values() if s != "insufficient_data"}
    if "random_forest" in sources:
        support_source = "random_forest"
    elif sources:
        support_source = "baseline"
    else:
        support_source = "insufficient_data"

    next_rec = next((r for r in recs if r["type"] == "next_topic"), None)
    if next_rec:
        goal = f"Next goal: reach mastery in {next_rec['title']}."
    elif completed:
        goal = "Every available topic is mastered. A quick review keeps knowledge fresh."
    else:
        goal = "Start with your first quiz to get personalised recommendations."

    fmt, fsrc = suggest_format(conn, user_id, get_preferences(conn, user_id))
    attempted = [t for t in topics if t["id"] in pm]
    return {
        "stats": {"completed": completed, "total": len(topics), "accuracy": accuracy,
                  "attempts": row["n"]},
        "goal": goal,
        "profile": b["profile"],
        "support": {"probability": round(mean(probs), 3) if probs else None,
                    "source": support_source,
                    "flagged": [r["title"] for r in recs if r["type"] == "support_alert"]},
        "format": {"value": fmt, "source": fsrc},
        "next": next_rec,
        "recommendations": recs,
        "revision": [t for t in topics if t["id"] in pm and pm[t["id"]]["status"] == "needs_revision"],
        "strong": [t for t in topics if t["id"] in pm and pm[t["id"]]["status"] == "mastered"],
        "chart": {"labels": [t["title"] for t in attempted],
                  "values": [round(pm[t["id"]]["mastery_score"] * 100) for t in attempted]},
    }


# ---------------------------------------------------------------- rule-based tutor
def tutor_reply(conn, text):
    """Answer from the lesson library by keyword overlap. No external AI service is used."""
    lower = text.lower()
    words = {w for w in re.findall(r"[a-z]+", lower) if len(w) > 2 and w not in STOPWORDS}
    topics = list_topics(conn)

    best, best_score = None, 0
    for t in topics:
        blob = " ".join([t["title"], t["simple_text"], t["detailed_text"], t["example_text"]])
        score = len(words & set(re.findall(r"[a-z]+", blob.lower())))
        if score > best_score:
            best, best_score = t, score

    if best is None:
        titles = ", ".join(t["title"] for t in topics)
        return {"reply": f"I can help with these topics: {titles}. Try asking about one of them.",
                "topic_id": None}

    parts = [best["title"]]
    if "summar" in lower:
        parts.append(best["simple_text"])
    else:
        parts += [f"Simple explanation: {best['simple_text']}",
                  f"More detail: {best['detailed_text']}",
                  f"Real-world example: {best['example_text']}"]
    if "practice" in lower or "question" in lower:
        qs = conn.execute(
            "SELECT prompt FROM quiz_questions WHERE topic_id = ? ORDER BY difficulty, id",
            (best["id"],),
        ).fetchall()
        lines = [f"{i}. {q['prompt']}" for i, q in enumerate(qs, start=1)]
        parts.append("Practice questions:\n" + "\n".join(lines))
    return {"reply": "\n\n".join(parts), "topic_id": best["id"]}
