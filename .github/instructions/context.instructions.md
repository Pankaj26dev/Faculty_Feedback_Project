PROJECT CONTEXT DOCUMENT

Project Title:
Unfiltered: AI-Powered Faculty Insight and Feedback Analytics Platform

Project Type:
BCA Summer AI Project (Academic Prototype)

Development Philosophy:
This project is intentionally being developed as a lightweight academic prototype and not as a production-grade enterprise application.

The objective is to demonstrate meaningful AI-powered feedback analytics within a one-month project timeline while maintaining simplicity, explainability, and high completion probability.

The project should prioritize:

* Simplicity
* Maintainability
* Demonstrability
* Educational value

The project should NOT introduce:

* Authentication systems
* User management
* JWT
* OAuth
* Docker
* Redis
* Microservices
* Cloud infrastructure
* Complex APIs
* Production deployment concerns

The goal is to build a functional prototype that can be demonstrated to faculty members.

---

PROJECT BACKGROUND

Educational institutions regularly collect student feedback through questionnaires and feedback forms.

However, faculty members often receive a large number of textual responses.

Problems with existing feedback systems:

1. Large volume of responses.
2. Manual analysis is time-consuming.
3. Similar concerns are expressed using different wording.
4. Important concerns may remain unnoticed.
5. Feedback often remains unused because extracting insights requires significant effort.

This project aims to solve that problem.

Instead of faculty reading hundreds of comments manually, the system should:

* Collect feedback.
* Store feedback.
* Analyze feedback.
* Identify recurring concerns.
* Detect overall sentiment.
* Generate improvement suggestions.
* Present insights through a dashboard.

---

TARGET USERS

Primary User:
Faculty Members

Secondary Users:
Students

Potential Future Users:
Department Coordinators
Academic Administrators

---

CURRENT SYSTEM WORKFLOW

Student
↓
Feedback Form
↓
SQLite Database
↓
Analytics Layer
↓
Faculty Dashboard

Future Workflow

Student
↓
Feedback Form
↓
SQLite Database
↓
Sentiment Analysis
↓
Semantic Analysis
↓
Recommendation Engine
↓
Faculty Dashboard

---

CURRENT PROJECT STATUS

COMPLETED

1. Development Environment Setup

* Python environment configured
* Virtual environment configured
* Required libraries installed

2. Database Layer

* SQLite integrated
* feedback.db created

Database Table:

feedback

Columns:

* id
* faculty_name
* subject
* rating
* feedback_text

Implemented Functions:

create_table()

insert_feedback()

fetch_feedback()

3. Student Feedback Form

Implemented Using Streamlit

Fields:

* Faculty Name
* Subject
* Rating
* Feedback Text

Functionality:

* User enters feedback
* Data stored in SQLite

4. Faculty Dashboard

Implemented:

* Feedback retrieval
* DataFrame display
* Total Feedback metric
* Average Rating metric

End-to-End Workflow Verified:

Feedback Form
↓
Database Storage
↓
Data Retrieval
↓
Dashboard Display

---

IMPORTANT PROJECT ASSET

FEEDBACK TAXONOMY DATASET

A custom educational feedback taxonomy dataset has already been created.

This is a critical project asset.

Purpose:

Instead of relying entirely on external AI models, the system uses a manually curated repository of realistic student feedback statements.

The dataset contains feedback patterns that represent the majority of real classroom feedback scenarios.

Estimated Coverage:
More than 95% of common student feedback patterns.

Categories include:

* Teaching Pace
* Concept Clarity
* Practical Learning
* Assignments
* Faculty Interaction
* Classroom Engagement
* Learning Resources
* Assessment Methods
* Communication Quality
* Overall Teaching Effectiveness

Examples:

Teaching Pace:

* Lecture is too fast
* Difficult to follow pace
* Need slower explanations

Concept Clarity:

* Concepts are confusing
* Need more examples
* Explanations are unclear

Practical Learning:

* Need more hands-on sessions
* More demonstrations required

This dataset will serve as the foundation for:

* Theme Detection
* Semantic Matching
* Recommendation Generation
* Knowledge Base Reasoning

This dataset is one of the most important components of the project and should be integrated into future analytics modules.

---

PLANNED AI COMPONENTS

MODULE 1
Sentiment Analysis

Technology:
VADER Sentiment Analyzer

Input:
feedback_text

Output:
Positive
Neutral
Negative

Purpose:
Measure overall emotional tone.

---

MODULE 2
Semantic Analysis

Technology:
Sentence Transformers
BGE Embeddings

Purpose:

Identify semantically similar feedback even when wording differs.

Example:

Feedback A:
"Lecture pace is too fast"

Feedback B:
"Professor moves through topics very quickly"

Desired Output:

Common Theme:
Teaching Pace

---

MODULE 3
Recommendation Engine

Purpose:

Generate actionable faculty recommendations.

Architecture:

Detected Theme
+
Feedback Taxonomy Knowledge Base
↓
Recommendation

Example:

Theme:
Teaching Pace

Recommendation:
Reduce lecture speed and provide additional examples for difficult concepts.

---

MODULE 4
Dashboard Analytics

Planned Features:

* Total Feedback
* Average Rating
* Positive Feedback Count
* Neutral Feedback Count
* Negative Feedback Count
* Sentiment Distribution Chart
* Common Theme Analysis
* Recommendation Display
* Faculty Insights

---

TECHNOLOGY STACK

Frontend:
Streamlit

Backend:
Python

Database:
SQLite

Data Handling:
Pandas

Visualization:
Plotly
Matplotlib

Sentiment Analysis:
VADER

Semantic Analysis:
Sentence Transformers
BGE Embeddings

---

PROJECT STRUCTURE

student-feedback-ai/

app.py

database/
db.py
feedback.db

pages/
1_Submit_Feedback.py
2_Faculty_Dashboard.py

ai/
sentiment.py
semantic_analysis.py
recommendation_engine.py
knowledge_base.py

utils/
charts.py

---

CRITICAL DEVELOPMENT RULES

1. Preserve existing project architecture.

2. Reuse existing database functions.

3. Do not redesign the project.

4. Do not introduce enterprise architecture.

5. Keep implementation beginner-friendly.

6. Explain where every new file should be created.

7. Provide complete code for each feature.

8. Implement one feature at a time.

9. Assume this is an academic prototype.

10. Prefer local solutions over API-dependent solutions.

---

NEXT DEVELOPMENT PRIORITY

1. Complete Faculty Dashboard.
2. Implement VADER Sentiment Analysis.
3. Add Sentiment Metrics.
4. Add Sentiment Distribution Chart.
5. Integrate Feedback Taxonomy Dataset.
6. Implement Theme Detection.
7. Implement Recommendation Engine.
8. Improve Dashboard Visualizations.
