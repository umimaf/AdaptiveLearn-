"""Recommendation logic: a transparent rule-based baseline plus a content-based ranker.

Topics are represented as feature vectors (subject one-hot + normalised difficulty).
The student's profile is the mastery-weighted average of topics already mastered.
"""
import numpy as np


def _status(pm, tid):
    p = pm.get(tid)
    return p["status"] if p else None


def is_ready(topic, pm):
    """A topic is ready when its prerequisite is mastered (or it has none)."""
    pre = topic.get("prerequisite_id")
    return pre is None or _status(pm, pre) == "mastered"


def rule_based_next(topics, pm):
    """Baseline: first ready topic that is not mastered and not flagged for revision."""
    for t in topics:
        if _status(pm, t["id"]) in ("mastered", "needs_revision"):
            continue
        if is_ready(t, pm):
            return t
    return None


def revision_topics(topics, pm):
    return [t for t in topics if _status(pm, t["id"]) == "needs_revision"]


def topic_vector(topic, subject_ids):
    one_hot = [1.0 if topic["subject_id"] == sid else 0.0 for sid in subject_ids]
    return np.array(one_hot + [topic["difficulty_level"] / 3.0])


def content_based_rank(topics, pm):
    """Rank ready, unmastered topics by cosine similarity to the student's mastered profile.

    Cold start (nothing mastered yet): easiest-first ordering.
    """
    candidates = [t for t in topics
                  if _status(pm, t["id"]) not in ("mastered", "needs_revision") and is_ready(t, pm)]
    if not candidates:
        return []
    mastered = [t for t in topics if _status(pm, t["id"]) == "mastered"]
    if not mastered:
        ordered = sorted(candidates, key=lambda t: (t["difficulty_level"], t["order_index"]))
        return [(t, 1.0 / t["difficulty_level"]) for t in ordered]

    sids = sorted({t["subject_id"] for t in topics})
    weights = np.array([pm[t["id"]]["mastery_score"] for t in mastered], dtype=float)
    if weights.sum() == 0:
        weights = np.ones(len(mastered))
    profile = np.average(np.vstack([topic_vector(t, sids) for t in mastered]), axis=0, weights=weights)
    norm_p = np.linalg.norm(profile)
    scored = []
    for t in candidates:
        v = topic_vector(t, sids)
        denom = norm_p * np.linalg.norm(v)
        scored.append((t, float(profile @ v / denom) if denom else 0.0))
    return sorted(scored, key=lambda x: -x[1])
