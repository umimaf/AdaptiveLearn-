"""Train, evaluate and save the ML models.

Models:
  1. K-Means (learning patterns): clusters students on their overall profile.
  2. Random Forest (support need): predicts whether a student needs extra support on a topic.
  3. Rule-based baseline: the comparison point for the Random Forest.

Evaluation uses a GROUP split by student, so no student appears in both train and test.

Run from the project root:
    python -m ml_engine.generate_dataset
    python -m ml_engine.train_models
"""
import json
import os

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, f1_score, precision_score, recall_score,
                             roc_auc_score, silhouette_score)
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, cross_val_score
from sklearn.preprocessing import StandardScaler

from ml_engine import prediction
from ml_engine.generate_dataset import DATASET_PATH, generate
from ml_engine.preprocessing import FEATURE_COLS, STUDENT_COLS, SUPPORT_THRESHOLD, TARGET, fill_missing

N_CLUSTERS = 4
CLUSTER_NAMES = ["Needs foundational support", "Developing", "Consistent", "Advanced"]
MODEL_DIR = prediction.MODEL_DIR


def evaluate(name, y_true, y_pred, y_score):
    return {
        "model": name,
        "accuracy": round(accuracy_score(y_true, y_pred), 3),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 3),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 3),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 3),
        "roc_auc": round(roc_auc_score(y_true, y_score), 3),
    }


def main():
    if not os.path.exists(DATASET_PATH):
        os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
        generate().to_csv(DATASET_PATH, index=False)
    df = fill_missing(pd.read_csv(DATASET_PATH))

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    tr_idx, te_idx = next(splitter.split(df, df[TARGET], groups=df["student_id"]))
    train, test = df.iloc[tr_idx].copy(), df.iloc[te_idx].copy()

    # ---- K-Means, fitted on training students only
    students_tr = train.drop_duplicates("student_id")
    scaler = StandardScaler().fit(students_tr[STUDENT_COLS])
    X_students = scaler.transform(students_tr[STUDENT_COLS])

    elbow = {}
    for k in range(2, 7):
        km_k = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_students)
        elbow[k] = {"inertia": round(float(km_k.inertia_), 1),
                    "silhouette": round(float(silhouette_score(X_students, km_k.labels_)), 3)}

    kmeans = KMeans(n_clusters=N_CLUSTERS, n_init=10, random_state=42).fit(X_students)
    order = (students_tr.assign(c=kmeans.labels_).groupby("c")["student_score_mean"]
             .mean().sort_values().index)
    cluster_names = {int(c): CLUSTER_NAMES[i] for i, c in enumerate(order)}
    for part in (train, test):
        part["cluster_id"] = kmeans.predict(scaler.transform(part[STUDENT_COLS]))

    # ---- Random Forest
    X_tr, y_tr = train[FEATURE_COLS], train[TARGET]
    X_te, y_te = test[FEATURE_COLS], test[TARGET]
    rf = RandomForestClassifier(n_estimators=200, min_samples_leaf=5, class_weight="balanced",
                                random_state=42, n_jobs=-1)
    cv_f1 = cross_val_score(rf, X_tr, y_tr, groups=train["student_id"],
                            cv=GroupKFold(n_splits=5), scoring="f1")
    rf.fit(X_tr, y_tr)
    rf_score = rf.predict_proba(X_te)[:, 1]
    rf_pred = (rf_score >= 0.5).astype(int)

    # ---- Rule-based baseline
    base_pred = (test["topic_score_mean"] < SUPPORT_THRESHOLD).astype(int)
    base_score = 1 - test["topic_score_mean"]

    results = [
        evaluate("rule_based_baseline", y_te, base_pred, base_score),
        evaluate("random_forest", y_te, rf_pred, rf_score),
    ]
    importances = {c: round(float(v), 3) for c, v in zip(FEATURE_COLS, rf.feature_importances_)}
    metrics = {
        "data_source": "synthetic",
        "note": "Synthetic development data. Results show the pipeline works, not real-world effectiveness.",
        "train_rows": int(len(train)), "test_rows": int(len(test)),
        "train_students": int(train.student_id.nunique()), "test_students": int(test.student_id.nunique()),
        "kmeans": {"k": N_CLUSTERS, "silhouette": elbow[N_CLUSTERS]["silhouette"],
                   "elbow_search": elbow, "cluster_names": cluster_names},
        "random_forest_cv_f1_mean": round(float(cv_f1.mean()), 3),
        "random_forest_cv_f1_std": round(float(cv_f1.std()), 3),
        "held_out_results": results,
        "random_forest_feature_importance": importances,
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(rf, os.path.join(MODEL_DIR, "random_forest.joblib"))
    joblib.dump(kmeans, os.path.join(MODEL_DIR, "kmeans.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "student_scaler.joblib"))
    joblib.dump({"cluster_names": cluster_names, "feature_cols": FEATURE_COLS,
                 "student_cols": STUDENT_COLS, "data_source": "synthetic"},
                os.path.join(MODEL_DIR, "metadata.joblib"))
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps({"held_out_results": results, "cv_f1": metrics["random_forest_cv_f1_mean"]}, indent=2))
    print(f"Saved models to {MODEL_DIR}")
    return metrics


if __name__ == "__main__":
    main()
