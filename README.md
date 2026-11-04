# AdaptiveLearn AI
### An AI-Based Adaptive Learning Platform for Students with Disabilities

## 1. Project Overview

AdaptiveLearn AI is a Python and Machine Learning-based educational platform designed to provide personalised and accessible learning experiences for students with disabilities.

Traditional learning platforms often follow a standard approach that may not accommodate the different learning requirements of every student. AdaptiveLearn AI addresses this limitation by adapting learning content, difficulty levels, and recommendations according to individual student performance and preferences.

The platform analyses learning activity, quiz results, topic completion, and learning preferences to recommend suitable learning resources. It also provides accessibility customisation options to help students access educational content in a comfortable and convenient way.

The primary objective is to make digital education more inclusive, accessible, and personalised.

## 2. Problem Statement

Students with disabilities may encounter various challenges while using traditional digital learning platforms.

Some common challenges include:

- Limited accessibility options in educational applications.
- Difficulty understanding complex learning materials.
- Lack of personalised learning recommendations.
- Limited availability of alternative learning formats.
- Standardised assessments that may not suit individual learning requirements.
- Difficulty tracking individual learning progress.

Therefore, an adaptive learning platform is required to provide flexible content delivery and personalised educational support.

## 3. Proposed Solution

AdaptiveLearn AI provides an intelligent learning environment that adapts to the individual needs and preferences of students.

The platform uses Machine Learning techniques to analyse student learning patterns and recommend suitable learning materials. It also provides accessibility settings, interactive assessments, and progress monitoring.

The system aims to improve the learning experience by allowing students to access educational content through different formats and at a suitable difficulty level.

## 4. Objectives

- Develop an accessible digital learning platform.
- Provide personalised learning recommendations using Machine Learning.
- Adapt content difficulty according to student performance.
- Support different learning preferences.
- Provide accessibility customisation options.
- Improve understanding through interactive quizzes and feedback.
- Monitor and analyse student learning progress.
- Promote inclusive and independent learning.

## 5. Key Features

### 5.1 Personalised Learning

The platform analyses student learning activity and provides personalised learning recommendations based on:

- Quiz scores.
- Number of attempts.
- Topic completion.
- Time spent on learning activities.
- Previous performance.
- Learning format preferences.

Based on this information, the system recommends suitable learning materials and difficulty levels.

### 5.2 Accessibility Customisation

Students can customise the learning interface according to their individual requirements.

Accessibility options include:

- Adjustable font size.
- Dyslexia-friendly font options.
- High-contrast mode.
- Customisable text and background colours.
- Line and letter spacing.
- Text-to-speech support.
- Speech-to-text support.
- Keyboard-friendly navigation.

### 5.3 Multiple Learning Formats

The platform supports different learning formats to make educational content easier to access and understand.

These may include:

- Text-based explanations.
- Audio-based learning.
- Images and illustrations.
- Educational videos.
- Captions and transcripts where available.

Students can use the available formats according to their preferences.

### 5.4 Adaptive Quiz System

The platform provides interactive quizzes to evaluate student understanding.

Features include:

- Topic-based assessments.
- Different difficulty levels.
- Instant feedback.
- Automatic score calculation.
- Explanation of incorrect answers.
- Learning recommendations based on quiz performance.

### 5.5 Learning Progress Dashboard

The dashboard provides an overview of student learning activity and performance.

It includes:

- Completed topics.
- Quiz scores.
- Learning progress.
- Performance summaries.
- Areas requiring additional practice.
- Recommended learning topics.

### 5.6 Learning Assistant

The learning assistant provides additional academic support by helping students understand educational concepts.

It can support:

- Simple explanations of difficult topics.
- Topic summaries.
- Examples.
- Answers to learning-related questions.
- Explanations of incorrect quiz answers.

The availability of these capabilities depends on the AI integration used in the application.

## 6. Machine Learning Implementation

Machine Learning is a core component of AdaptiveLearn AI. It analyses student learning activity and generates personalised recommendations.

### Input Parameters

| Parameter | Description |
|---|---|
| Quiz Score | Performance in assessments |
| Attempts | Number of attempts made |
| Time Spent | Time spent studying a topic |
| Topic Completion | Completion status of learning material |
| Incorrect Answers | Number of incorrect responses |
| Learning Preference | Preferred learning format |
| Previous Performance | Earlier assessment results |

### Algorithms Considered

**K-Means Clustering**

Used to explore and group similar learning activity patterns.

**Random Forest**

Can be used to predict learning categories or suitable difficulty levels when appropriate training data is available.

**Content-Based Recommendation**

Recommends learning materials based on student preferences and previous learning activity.

**Rule-Based Recommendation**

Provides initial recommendations based on predefined learning conditions.

### Machine Learning Workflow

1. Collect student learning activity with appropriate consent.
2. Preprocess and clean the collected data.
3. Extract relevant learning features.
4. Train and evaluate the selected ML model.
5. Save the trained model using Joblib.
6. Integrate the model with the Python backend.
7. Generate personalised learning recommendations.
8. Update recommendations based on new learning activity.

The system provides educational recommendations and does not diagnose disabilities or determine a student's intellectual ability.

## 7. Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Machine Learning | Scikit-learn |
| Data Processing | Pandas, NumPy |
| Data Visualisation | Matplotlib, Chart.js |
| Database | SQLite / MySQL |
| Model Persistence | Joblib |
| OCR | Tesseract OCR |
| PDF Processing | PyMuPDF / PyPDF2 |
| Text-to-Speech | gTTS / Web Speech API |
| Version Control | Git and GitHub |
| Deployment | Render / Railway |

*The table should reflect the technologies actually used in the final implementation.*

## 8. System Architecture

The application follows a modular architecture consisting of the user interface, Python backend, Machine Learning component, database, and learning modules.

```text
              STUDENT
                 |
                 v
          USER INTERFACE
          HTML / CSS / JS
                 |
                 v
          PYTHON BACKEND
              FLASK
                 |
       +---------+---------+
       |         |         |
       v         v         v
   USER       LEARNING   ACCESSIBILITY
  MODULE      MODULE      MODULE
       |         |         |
       v         v         v
   DATABASE   ML ENGINE  CONTENT
       |         |       FORMATS
       |         v
       |    RECOMMENDATION
       |         |
       +---------+
                 |
                 v
         PERSONALIZED CONTENT
                 |
                 v
          STUDENT DASHBOARD
```

## 9. Project Structure

```text
AdaptiveLearn-AI/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── dataset/
│   └── student_learning_data.csv
│
├── models/
│   └── adaptive_model.pkl
│
├── ml/
│   ├── preprocessing.py
│   ├── train_model.py
│   ├── predict.py
│   └── recommendation.py
│
├── database/
│   ├── db.py
│   └── models.py
│
├── modules/
│   ├── authentication.py
│   ├── accessibility.py
│   ├── learning.py
│   ├── quiz.py
│   └── dashboard.py
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── learning.html
│   ├── quiz.html
│   └── profile.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│
├── uploads/
│
└── tests/
    ├── test_app.py
    └── test_ml.py
```

This is a suggested directory structure and should be adjusted according to the actual implementation.

## 10. Installation and Setup

### Prerequisites

- Python 3.10 or later.
- pip package manager.
- Git.
- VS Code or another Python IDE.
- Modern web browser.

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/AdaptiveLearn-AI.git
```

### Step 2: Navigate to the Project Directory

```bash
cd AdaptiveLearn-AI
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

For Windows:

```powershell
venv\Scripts\activate
```

For Linux or macOS:

```bash
source venv/bin/activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Configure Environment Variables

Create a `.env` file in the root directory if required.

Example:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
AI_API_KEY=your_api_key
```

Do not upload confidential credentials or API keys to GitHub.

### Step 7: Run the Application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

The port number should match the configuration in your application.

### Step 8: Train the Machine Learning Model

If model training is not performed automatically, run:

```bash
python ml/train_model.py
```

The trained model should be saved in the `models/` directory.

## 11. Database Design

The application can use the following database tables.

### Users

Stores user account information.

- user_id
- name
- email
- password_hash
- role
- created_at

### Student Preferences

Stores individual learning and accessibility preferences.

- preference_id
- user_id
- font_size
- contrast_mode
- preferred_learning_format
- accessibility_settings

### Learning Materials

Stores educational content.

- material_id
- title
- subject
- topic
- difficulty_level
- content_type
- content_location

### Quiz Results

Stores student assessment results.

- result_id
- user_id
- topic_id
- score
- attempts
- incorrect_answers
- completion_time

### Learning Progress

Stores student learning activity.

- progress_id
- user_id
- topic_id
- completion_status
- time_spent
- last_accessed

### Recommendations

Stores personalised learning recommendations.

- recommendation_id
- user_id
- recommended_topic
- recommended_format
- recommended_difficulty
- created_at

## 12. Testing

The application should be tested to ensure that all modules function correctly.

| Testing Area | Test Description |
|---|---|
| Authentication | Registration, login, and logout |
| Accessibility | Font size, contrast, and keyboard navigation |
| Learning Module | Lesson loading and content display |
| ML Model | Prediction and recommendation accuracy |
| Quiz Module | Question display, scoring, and feedback |
| Database | Data storage and retrieval |
| Dashboard | Progress and score display |
| Security | Input validation and access control |
| Compatibility | Browser and screen-size compatibility |

Accessibility testing should also include manual checks and, where possible, feedback from students with disabilities.


## 14. Privacy and Security

The platform may process personal learning information and accessibility preferences. Therefore, appropriate privacy and security measures should be followed.

- Use secure password hashing.
- Protect user sessions.
- Validate user inputs.
- Restrict access to uploaded documents.
- Store API keys and secret credentials securely.
- Obtain consent before collecting learning activity.
- Avoid collecting unnecessary personal information.
- Provide appropriate controls for accessing and sharing student information.

## 15. Expected Outcome

AdaptiveLearn AI aims to provide an accessible and personalised digital learning environment for students with disabilities.

The expected outcomes include:

- Improved access to educational content.
- Personalised learning recommendations.
- Flexible learning formats.
- Customisable accessibility settings.
- Better understanding through interactive assessments.
- Continuous monitoring of learning progress.
- A more inclusive digital learning experience.

## 16. Future Scope

The project can be extended through improvements in Machine Learning algorithms, additional educational content, multilingual support, mobile compatibility, and integration with other educational platforms.

Further development can also focus on improving recommendation accuracy through larger, consented, and appropriately evaluated learning datasets.

## 17. Project Information

| Field | Details |
|---|---|
| Project Name | AdaptiveLearn AI |
| Project Domain | Artificial Intelligence and Machine Learning |
| Application Area | Educational Technology |
| Primary Language | Python |
| Backend | Flask |
| ML Framework | Scikit-learn |
| Database | SQLite / MySQL |
| Project Type | Academic Project |

**Team Name:** code crushers
**Developed By:** 
Syeda Umima Fatima
Aditi V Jaiswal
Jessie Ranvita Kandikatla


## 18. Conclusion

AdaptiveLearn AI focuses on making digital education more accessible through personalised learning and Machine Learning-based recommendations.

By combining accessibility customisation, adaptive assessments, multiple learning formats, and progress tracking, the platform aims to create a flexible learning environment that considers the individual requirements of students.

The project promotes inclusive education by ensuring that students have greater control over how they access and interact with learning materials.
