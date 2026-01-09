# Automated Report System Design

## 1. Overview
The system automatically generates weekly learning reports for each student, synthesizing data from study history, knowledge mastery, and prediction models.

## 2. Report Structure (PDF)

### Section 1: Header
*   Student Name
*   Report Period (e.g., 2025-01-01 ~ 2025-01-07)
*   Tutor Name

### Section 2: Weekly Summary
*   **Total Study Time**: Hours/Minutes
*   **Problems Solved**: Count
*   **Accuracy**: Percentage (Change from last week, e.g., +5%p)

### Section 3: Analysis
*   **Strengths**: Top 3 concepts with highest mastery.
*   **Weaknesses**: Bottom 3 concepts.
    *   **Root Cause**: Recursive analysis using Ltree (e.g., Triangle Properties (Weak) -> Elementary Geometry (Weak)).

### Section 4: Prediction
*   **Current Level**: Estimated score.
*   **Predicted Exam Score**: Range (e.g., 80-85).

### Section 5: Action Plan
*   Specific topics to focus on next week.
*   Recommended time allocation.

## 3. Technical Implementation

### 3.1. Backend Service (`ReportService`)
*   **Data Aggregation**: Fetch stats from `AnalyticsService`.
*   **Logic**:
    *   `_analyze_strengths(student_id)`
    *   `_analyze_weaknesses(student_id)`
    *   `_find_root_knowledge_gaps(student_id, weaknesses)` (Critical: Ltree traversal)
*   **Template Rendering**: Jinja2 + HTML/CSS.
*   **PDF Conversion**: WeasyPrint (Python library) or Headless Chrome (Playwright). *Decision: Start with WeasyPrint for simplicity, switch to Playwright if complex charts need JS rendering.*

### 3.2. Asynchronous Processing
*   **Trigger**: Scheduled (Cron) or Manual (Admin Dashboard).
*   **Queue**: Celery + Redis.
*   **Concurrency**: Parallel generation for 30+ students.

### 3.3. Delivery
*   **Storage**: Save generated PDF to S3 `reports/{student_id}/{date}.pdf`.
*   **Notification**: Email via AWS SES or SMTP.

## 4. Root Cause Analysis Algorithm
```python
def find_root_cause(weak_concept):
    # Traverse Ltree ancestors
    ancestors = get_ancestors(weak_concept)
    for ancestor in ancestors:
        if mastery(ancestor) < threshold:
            return ancestor # Found the fundamental gap
    return weak_concept # No deeper gap found
```

## 5. Mock Data for MVP
For the mockup phase, we will use a static JSON structure to simulate the report data.
