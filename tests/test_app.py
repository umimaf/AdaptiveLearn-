"""Tests: auth, database, API, quiz submission, tutor, accessibility, recommendations and ML.

Run from the project root:
    python -m unittest discover -s tests -v
"""
import os
import sqlite3
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

from app import create_app  # noqa: E402
from ml_engine import prediction, recommendation, train_models  # noqa: E402
from ml_engine.preprocessing import fill_missing, FEATURE_COLS  # noqa: E402


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test.db")
        self.app = create_app({"DATABASE": self.db_path, "TESTING": True, "SECRET_KEY": "test"})
        self.client = self.app.test_client()

    def register(self, email="asha@example.com", password="password123", fmt="audio"):
        return self.client.post("/register", data={
            "name": "Asha", "email": email, "password": password, "preferred_format": fmt,
        })

    def first_question(self, topic_id=1):
        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            "SELECT id, answer FROM quiz_questions WHERE topic_id = ? ORDER BY id LIMIT 1", (topic_id,)
        ).fetchone()
        conn.close()
        return row


class TestPagesAndAuth(AppTestCase):
    def test_public_pages_render(self):
        for path in ("/", "/library", "/settings"):
            self.assertEqual(self.client.get(path).status_code, 200, path)

    def test_library_includes_new_subject_and_filters(self):
        page = self.client.get("/library")
        self.assertIn(b"Data Structures and Algorithms", page.data)
        self.assertIn(b"library-search", page.data)
        self.assertIn(b"status-filter", page.data)
        self.assertIn(b"Searching and Sorting", page.data)

    def test_topic_has_illustrated_visual_and_no_video_format(self):
        self.register()
        conn = sqlite3.connect(self.db_path)
        topic_id = conn.execute(
            "SELECT id FROM topics WHERE title = ?", ("Searching and Sorting",)
        ).fetchone()[0]
        conn.close()
        page = self.client.get(f"/topic/{topic_id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"algorithms-learning.svg", page.data)
        self.assertNotIn(b'data-format-tab="video"', page.data)
        image = self.client.get("/static/images/algorithms-learning.svg")
        self.assertEqual(image.status_code, 200)
        image.close()

    def test_reinitializing_database_does_not_duplicate_topics(self):
        self.register()
        conn = sqlite3.connect(self.db_path)
        user_id = conn.execute("SELECT id FROM users WHERE email = ?", ("asha@example.com",)).fetchone()[0]
        question_id = conn.execute("SELECT id FROM quiz_questions ORDER BY id LIMIT 1").fetchone()[0]
        conn.execute(
            "UPDATE accessibility_preferences SET preferred_format = 'video' WHERE user_id = ?", (user_id,)
        )
        conn.execute(
            """INSERT INTO quiz_attempts
               (user_id, question_id, selected, is_correct, attempt_number, format_used)
               VALUES (?, ?, 'legacy', 0, 1, 'video')""",
            (user_id, question_id),
        )
        conn.commit()
        before = sqlite3.connect(self.db_path)
        counts = before.execute("SELECT COUNT(*) FROM subjects").fetchone()[0], before.execute(
            "SELECT COUNT(*) FROM topics"
        ).fetchone()[0]
        before.close()
        conn.close()
        create_app({"DATABASE": self.db_path, "TESTING": True, "SECRET_KEY": "test"})
        after = sqlite3.connect(self.db_path)
        new_counts = after.execute("SELECT COUNT(*) FROM subjects").fetchone()[0], after.execute(
            "SELECT COUNT(*) FROM topics"
        ).fetchone()[0]
        old_preference = after.execute(
            "SELECT preferred_format FROM accessibility_preferences WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
        old_attempt_format = after.execute(
            "SELECT format_used FROM quiz_attempts WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
        after.close()
        self.assertEqual(counts, new_counts)
        self.assertEqual(old_preference, "text")
        self.assertEqual(old_attempt_format, "text")

    def test_dashboard_requires_login(self):
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.headers["Location"])

    def test_register_then_dashboard(self):
        resp = self.register()
        self.assertEqual(resp.status_code, 302)
        page = self.client.get("/dashboard")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Hello, Asha", page.data)

    def test_duplicate_email_rejected(self):
        self.register()
        self.client.get("/logout")
        resp = self.register()
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"already exists", resp.data)

    def test_wrong_password_rejected(self):
        self.register()
        self.client.get("/logout")
        resp = self.client.post("/login", data={"email": "asha@example.com", "password": "wrong"})
        self.assertIn(b"Incorrect email or password", resp.data)

    def test_login_succeeds_with_correct_password(self):
        self.register()
        self.client.get("/logout")
        resp = self.client.post("/login", data={"email": "asha@example.com", "password": "password123"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.client.get("/dashboard").status_code, 200)

    def test_password_is_hashed(self):
        self.register()
        conn = sqlite3.connect(self.db_path)
        stored = conn.execute("SELECT password_hash FROM users").fetchone()[0]
        conn.close()
        self.assertNotIn("password123", stored)


class TestQuizAndProgress(AppTestCase):
    def test_api_requires_login(self):
        qid, _ = self.first_question()
        resp = self.client.post(f"/api/quiz/{qid}/submit", json={"selected": "x"})
        self.assertEqual(resp.status_code, 401)

    def test_correct_and_incorrect_answers_are_scored(self):
        self.register()
        qid, answer = self.first_question()
        ok = self.client.post(f"/api/quiz/{qid}/submit",
                              json={"selected": answer, "time_taken": 4.2, "format_used": "text"}).get_json()
        self.assertTrue(ok["correct"])
        self.assertEqual(ok["correct_answer"], answer)
        self.assertIn("explanation", ok)

        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM quiz_attempts")  # isolate the wrong-answer check
        conn.commit()
        conn.close()
        bad = self.client.post(f"/api/quiz/{qid}/submit",
                               json={"selected": "definitely wrong", "time_taken": 9, "format_used": "video"}).get_json()
        self.assertFalse(bad["correct"])

    def test_attempts_are_stored_and_progress_updated(self):
        self.register()
        qid, answer = self.first_question()
        self.client.post(f"/api/quiz/{qid}/submit", json={"selected": answer, "format_used": "text"})
        conn = sqlite3.connect(self.db_path)
        attempts = conn.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0]
        status = conn.execute("SELECT status FROM student_progress").fetchone()
        conn.close()
        self.assertEqual(attempts, 1)
        self.assertIsNotNone(status)

    def test_missing_selection_is_rejected(self):
        self.register()
        qid, _ = self.first_question()
        resp = self.client.post(f"/api/quiz/{qid}/submit", json={})
        self.assertEqual(resp.status_code, 400)

    def test_topic_page_shows_questions(self):
        self.register()
        resp = self.client.get("/topic/1")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"quiz-option", resp.data)


class TestTutorAndAccessibility(AppTestCase):
    def test_tutor_finds_relevant_topic(self):
        resp = self.client.post("/api/tutor", json={"question": "Explain variables and data types"})
        self.assertEqual(resp.get_json()["topic_id"], 1)

    def test_tutor_returns_practice_questions(self):
        data = self.client.post("/api/tutor", json={"question": "Explain functions with practice questions"}).get_json()
        self.assertEqual(data["topic_id"], 3)
        self.assertIn("Practice questions", data["reply"])

    def test_tutor_rejects_empty_question(self):
        self.assertEqual(self.client.post("/api/tutor", json={"question": " "}).status_code, 400)

    def test_accessibility_settings_round_trip(self):
        self.register()
        self.client.post("/api/accessibility", json={
            "high_contrast": True, "font_scale": 1.2, "preferred_format": "visual", "dyslexia_font": True,
        })
        prefs = self.client.get("/api/accessibility").get_json()
        self.assertEqual(prefs["high_contrast"], 1)
        self.assertEqual(prefs["font_scale"], 1.2)
        self.assertEqual(prefs["preferred_format"], "visual")
        self.assertIn(b"high-contrast", self.client.get("/dashboard").data)

    def test_invalid_accessibility_values_fall_back_to_defaults(self):
        self.register()
        prefs = self.client.post("/api/accessibility", json={"font_scale": 9, "preferred_format": "video"}).get_json()
        self.assertEqual(prefs["font_scale"], 1.0)
        self.assertEqual(prefs["preferred_format"], "text")


class TestRecommendations(unittest.TestCase):
    topics = [
        {"id": 1, "subject_id": 1, "title": "A", "difficulty_level": 1, "order_index": 1, "prerequisite_id": None},
        {"id": 2, "subject_id": 1, "title": "B", "difficulty_level": 2, "order_index": 2, "prerequisite_id": 1},
        {"id": 3, "subject_id": 2, "title": "C", "difficulty_level": 1, "order_index": 1, "prerequisite_id": None},
    ]

    def test_next_topic_respects_prerequisites(self):
        self.assertEqual(recommendation.rule_based_next(self.topics, {})["id"], 1)
        pm = {1: {"status": "in_progress", "mastery_score": 0.6}}
        self.assertEqual(recommendation.rule_based_next(self.topics, pm)["id"], 1)
        pm = {1: {"status": "mastered", "mastery_score": 0.9}}
        self.assertEqual(recommendation.rule_based_next(self.topics, pm)["id"], 2)

    def test_revision_topics_are_listed(self):
        pm = {1: {"status": "needs_revision", "mastery_score": 0.3}}
        self.assertEqual([t["id"] for t in recommendation.revision_topics(self.topics, pm)], [1])

    def test_content_based_ranks_similar_subject_first(self):
        pm = {1: {"status": "mastered", "mastery_score": 0.9}}
        ranked = recommendation.content_based_rank(self.topics, pm)
        self.assertEqual(ranked[0][0]["id"], 2)  # same subject as the mastered topic

    def test_missing_values_are_filled(self):
        df = pd.DataFrame({"a": [1.0, None, 3.0], "b": ["x", "y", "z"]})
        out = fill_missing(df)
        self.assertFalse(out["a"].isna().any())
        self.assertEqual(out["a"].iloc[1], 2.0)


class TestMLPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics = train_models.main()
        prediction._cache = None

    def test_training_saves_artifacts_and_metrics(self):
        self.assertTrue(prediction.is_available())
        models = {r["model"]: r for r in self.metrics["held_out_results"]}
        self.assertIn("rule_based_baseline", models)
        self.assertIn("random_forest", models)
        self.assertEqual(self.metrics["data_source"], "synthetic")

    def test_prediction_returns_probability(self):
        s = {"student_score_mean": 0.4, "student_time_mean": 35.0,
             "student_attempt_rate": 3.0, "student_repeat_rate": 0.5}
        t = {"topic_score_mean": 0.35, "topic_attempts": 4, "topic_avg_time": 40.0,
             "topic_repeat_rate": 0.6, "topic_trend": -0.1, "format_idx": 0, "difficulty": 2}
        prob = prediction.predict_support(s, t)
        self.assertIsNotNone(prob)
        self.assertTrue(0.0 <= prob <= 1.0)
        self.assertIsNotNone(prediction.student_cluster_name(s))

    def test_feature_columns_match_model(self):
        m = prediction.load()
        self.assertEqual(list(m["random_forest"].feature_names_in_), FEATURE_COLS)


if __name__ == "__main__":
    unittest.main()
