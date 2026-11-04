"""Load trained Joblib artifacts and serve predictions.

If the artifacts are missing, every function returns None and the app falls
back to the rule-based baseline.
"""
import os

import joblib
import pandas as pd

from ml_engine.preprocessing import STUDENT_COLS

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")
KEYS = ["random_forest", "kmeans", "student_scaler", "metadata"]
_cache = None


def is_available():
    return all(os.path.exists(os.path.join(MODEL_DIR, f"{k}.joblib")) for k in KEYS)


def load():
    global _cache
    if _cache is None and is_available():
        _cache = {k: joblib.load(os.path.join(MODEL_DIR, f"{k}.joblib")) for k in KEYS}
    return _cache


def _cluster(m, student_feats):
    s_df = pd.DataFrame([student_feats])[STUDENT_COLS]
    return int(m["kmeans"].predict(m["student_scaler"].transform(s_df))[0])


def student_cluster_name(student_feats):
    m = load()
    if m is None:
        return None
    return m["metadata"]["cluster_names"].get(_cluster(m, student_feats))


def predict_support(student_feats, topic_feats):
    """Probability that the student needs extra support on this topic, or None."""
    m = load()
    if m is None:
        return None
    cluster = _cluster(m, student_feats)
    row = {**topic_feats, **student_feats, "cluster_id": cluster}
    X = pd.DataFrame([row])[m["metadata"]["feature_cols"]]
    return float(m["random_forest"].predict_proba(X)[0, 1])
