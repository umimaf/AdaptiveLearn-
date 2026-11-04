# AdaptiveLearn AI

An adaptive learning platform for students with different learning needs. It adjusts
question difficulty, suggests the next topic and recommends a learning format from each
student's own quiz results. Accessibility settings are always chosen by the student, never
diagnosed.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m ml_engine.generate_dataset                # synthetic development data
python -m ml_engine.train_models                    # trains and evaluates the models
python -m unittest discover -s tests -v             # run the test suite
python app.py                                       # open http://127.0.0.1:5000
```

The app starts without the models. If `ml_engine/saved_models/` is missing, every ML
feature falls back to the rule-based baseline.

## What is implemented

| Area | Status |
|---|---|
| Registration, login (hashed passwords), sessions, route protection | Done |
| Accessibility: dyslexia font, text size, high contrast, reduced motion, focus mode, read-aloud, speech input | Done |
| Three learning formats per topic (text, audio via TTS, illustrated visual lessons) | Done |
| Searchable, filterable topic library with mastery progress | Done |
| Adaptive quizzes: multiple choice and true/false, instant feedback with explanations, attempt tracking | Done |
| Match-the-following and image-based questions | Not yet |
| Progress tracking: mastery, revision flags, prerequisite-aware next topic | Done |
| K-Means learning profiles, Random Forest support model, rule-based baseline, content-based ranking | Done, with evaluation |
| Student dashboard with charts, goals, recommendations | Done |
| AI tutor: explanations, summaries, practice questions from the library | Done (rule-based, no external API) |
| Q&A over uploaded PDFs, Tesseract OCR | Not yet |
| Teacher dashboard: uploads, quiz authoring, cohort reports | Not yet |
| Lesson content for Operating Systems and Java | Not yet. Demo covers Python (4 topics), DBMS (3 topics), and Data Structures and Algorithms (3 topics) |

## Architecture

```
app.py                 Flask app factory
config.py              Settings (environment overridable)
backend/
  db.py                SQLite schema, connection handling, initialisation
  content.py           Sample subjects, topics, questions
  auth.py              Password hashing, session login, login_required
  services.py          Scoring, progress, feature building, adaptivity, dashboard, tutor
  routes.py            Pages and JSON API
ml_engine/
  generate_dataset.py  Synthetic data generator (labelled data_source = synthetic)
  preprocessing.py     Shared feature names and missing-value handling
  train_models.py      Training, evaluation, saving
  prediction.py        Loads Joblib artifacts, serves predictions
  recommendation.py    Rule-based next topic, revision, content-based ranking
frontend/
  templates/           Jinja2 pages (Bootstrap 5)
  static/css/, js/     Styling, accessibility, quiz and tutor behaviour
  static/images/       Local lesson illustrations
tests/test_app.py      unittest suite
```

## Machine learning

**Data.** `ml_engine/dataset/synthetic_student_attempts.csv` holds 4,200 rows (600 students
× 7 topics). Every row is labelled `data_source = synthetic`. The generator uses a hidden
ability variable, so the target is not a copy of an observed feature. This dataset tests
that the pipeline works. It cannot show that the system helps real students.

**K-Means (learning profiles).** Clusters students on four overall features: mean score,
mean time, attempts per topic, and repeat-mistake rate. Clusters are named by mean score.
Silhouette score is 0.24 at k = 4. It is highest at k = 2 (0.31), so k = 4 was chosen for
interpretable profiles, not for cluster quality. The elbow results are in
`ml_engine/saved_models/metrics.json`.

**Random Forest (support need).** Predicts whether a student needs extra support on a
topic. Inputs: topic score, attempts, time, repeat rate, trend, preferred format, difficulty,
K-Means cluster, and overall score. Evaluation uses a group split by student, so no student
appears in both training and test data, plus 5-fold grouped cross-validation.

**Baseline.** A fixed rule: flag support when the topic average is below 60%. Every
ML result is compared against this rule.

Held-out results from the last training run (synthetic data):

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Rule-based baseline | 0.574 | 0.508 | 0.970 | 0.667 | 0.888 |
| Random Forest | 0.847 | 0.849 | 0.792 | 0.819 | 0.889 |

The Random Forest improves accuracy and F1 over the baseline. Its ROC-AUC is the same as
the baseline's. The baseline's threshold was set once and not tuned. The synthetic
generator was designed by the author, so these numbers reflect that design. Expect
different results on real data.

**Adaptivity.** Difficulty starts at the topic's level. It rises after three strong answers
(80%+) and falls after two weak answers (below 50%). If the support model gives a
probability of 70% or more, difficulty drops one level. Recommendations are recalculated
after every answer. Models are not retrained automatically.

## Known limitations

- **Feature definitions differ between training and the app.** The synthetic generator
  produces repeat-rate and attempt-count features directly. The app derives them from real
  attempts with simple definitions. This is a train/serve gap for the Random Forest. Fix it
  by generating the training data from the same attempt-level logic.
- **Small real-data samples are noisy.** A student with two answers gives unstable features.
  The models are most reliable after several weeks of use.
- **Format suggestion is confounded.** Accuracy by format reflects choices students make
  for themselves, not what format causes learning.
- **Synthetic labels describe the simulation.** They are not clinical or educational
  judgements about any person.
- **Security.** Suitable for a demonstration deployment. Before real use, add CSRF
  protection, rate limiting, email verification, HTTPS, and a real secret key.
- **Consent.** Teacher access to student progress needs consent flows, which are not built.
- **Dependencies.** Replace the sqlite3 layer with SQLAlchemy if you adopt the original
  brief's stack. The schema is a direct mapping.
- **Tutor scope.** Answers come from the lesson library by keyword overlap. It can
  miss questions that use different words from the lessons.

## Testing

`tests/test_app.py` covers registration and login, password hashing, route protection, quiz
scoring and progress, the tutor, accessibility settings, prerequisite-aware recommendations,
missing-value handling, and the full training pipeline with prediction.
