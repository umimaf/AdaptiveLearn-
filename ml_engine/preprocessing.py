"""Shared constants and preprocessing used by BOTH training and prediction.

Keeping feature names and helpers in one module prevents train/serve skew.
"""
import numpy as np

FORMATS = ["text", "audio", "visual"]

# Student-level features, averaged across all of a student's topics. Used for K-Means.
STUDENT_COLS = ["student_score_mean", "student_time_mean", "student_attempt_rate", "student_repeat_rate"]

# Topic-level features for one student on one topic.
TOPIC_COLS = ["topic_score_mean", "topic_attempts", "topic_avg_time", "topic_repeat_rate",
              "topic_trend", "format_idx", "difficulty"]

# Random Forest input: topic features + K-Means cluster + overall student score.
FEATURE_COLS = TOPIC_COLS + ["cluster_id", "student_score_mean"]

TARGET = "needs_support"
SUPPORT_THRESHOLD = 0.6  # baseline rule: topic average below this -> flag for support


def fill_missing(df):
    """Missing-value handling: numeric gaps are filled with the column median."""
    df = df.copy()
    numeric = df.select_dtypes(include="number").columns
    df[numeric] = df[numeric].fillna(df[numeric].median())
    return df
