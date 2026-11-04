"""Generate a SYNTHETIC development dataset.

Every row is a student-topic summary. The hidden variable `latent` stands in for
true ability and is NOT stored, so the label is not a copy of an observed feature.
The output is labelled data_source = "synthetic". It shows the pipeline works;
it says nothing about real students.

Run from the project root:
    python -m ml_engine.generate_dataset
"""
import os

import numpy as np
import pandas as pd

from ml_engine.preprocessing import FORMATS

DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
DATASET_PATH = os.path.join(DATASET_DIR, "synthetic_student_attempts.csv")


def generate(n_students=600, n_topics=7, seed=42):
    rng = np.random.default_rng(seed)
    ability = np.clip(rng.normal(0.6, 0.18, n_students), 0.05, 0.98)
    speed = np.clip(rng.normal(30, 8, n_students), 8, 90)          # seconds per question
    preferred = rng.integers(0, len(FORMATS), n_students)
    topic_difficulty = rng.integers(1, 4, n_topics)                 # levels 1..3

    rows = []
    for s in range(n_students):
        topic_rows = []
        for t in range(n_topics):
            latent = ability[s] - 0.12 * topic_difficulty[t] + rng.normal(0, 0.08)
            score_mean = float(np.clip(latent + rng.normal(0, 0.08), 0, 1))
            attempts = int(rng.poisson(2)) + 1
            avg_time = float(max(5.0, speed[s] * (1 + 0.4 * (1 - ability[s]))
                                 * (1 + 0.1 * topic_difficulty[t]) + rng.normal(0, 3)))
            repeat = float(np.clip((1 - score_mean) * rng.uniform(0.6, 1.1), 0, 1))
            trend = float(np.clip((ability[s] - 0.6) * 0.25 + rng.normal(0, 0.08), -0.5, 0.5))
            fmt = int(preferred[s]) if rng.random() < 0.7 else int(rng.integers(0, len(FORMATS)))
            # Label from latent ability, with 8% label noise.
            needs = bool(latent < 0.30) != bool(rng.random() < 0.08)
            topic_rows.append((t + 1, score_mean, attempts, avg_time, repeat, trend,
                               fmt, int(topic_difficulty[t]), int(needs)))

        arr = np.array([r[1:] for r in topic_rows], dtype=float)
        student_stats = {
            "student_score_mean": arr[:, 0].mean(),
            "student_time_mean": arr[:, 2].mean(),
            "student_attempt_rate": arr[:, 1].mean(),
            "student_repeat_rate": arr[:, 3].mean(),
        }
        for r in topic_rows:
            rows.append({
                "student_id": s + 1, "topic_id": r[0],
                "topic_score_mean": r[1], "topic_attempts": r[2], "topic_avg_time": r[3],
                "topic_repeat_rate": r[4], "topic_trend": r[5], "format_idx": r[6],
                "difficulty": r[7], **student_stats,
                "needs_support": r[8], "data_source": "synthetic",
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    os.makedirs(DATASET_DIR, exist_ok=True)
    df = generate()
    df.to_csv(DATASET_PATH, index=False)
    print(f"Wrote {len(df)} SYNTHETIC rows for {df['student_id'].nunique()} students to {DATASET_PATH}")
    print(f"Support-need rate: {df['needs_support'].mean():.2%}")
