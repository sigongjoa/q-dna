# Q-DNA MVP Requirements & Roadmap

**Target**: Deploy MVP for 15-30 tutoring students within 4 weeks (1 Month).
**Core Value**: Save tutor's time & Improve parent's trust.

## 1. Feature Requirements

### 1.1. Bulk Data Entry (CMS)
*   **Goal**: Minimize time spent entering student records.
*   **Target Performance**: 5-10 students entered simultaneously; < 3 seconds to submit 30 records.
*   **Features**:
    *   Bulk Input UI: Grid/Table view for entering multiple students' data at once.
    *   Keyboard Navigation: Tab/Enter support for rapid entry.
    *   Draft Saving: LocalStorage-based temporary save to prevent data loss.
    *   Excel Import: Migration tool for existing data.

### 1.2. Advanced Knowledge Map Visualization
*   **Goal**: "WOW" factor for parents; intuitive understanding of student status.
*   **Features**:
    *   Mastery Color Coding: Red (Weak), Yellow (Average), Green (Excellent).
    *   Interactive Detail: Click to show learning history and accuracy.
    *   PDF Export: High-res SVG to PDF for reports.
    *   Time-series Animation: Visualizing growth (e.g., 3 months ago vs. Now).

### 1.3. Automated Weekly Reports (Critical)
*   **Goal**: Reduce reporting time from 5 hrs/week to 10 mins/week.
*   **Format**: PDF (sent via Email/KakaoTalk).
*   **Content**:
    *   Weekly Summary (Study time, Problem count, Accuracy).
    *   Strengths (Concepts with >90% accuracy).
    *   Weaknesses (Concepts with <70% accuracy) with Root Cause Analysis.
    *   Grade Prediction (Current level vs. Predicted Goal).
    *   Next Week's Plan.
    *   Attachments: Knowledge Map, Recommended remedial problems.

### 1.4. Grade Prediction Model (V1)
*   **Goal**: Provide strategic learning guidance.
*   **Logic (MVP)**: Weighted scoring based on recent accuracy and weak concepts.
    *   `Predicted Score = (Recent 4-week Accuracy * 0.7) + (Weakness Weight * 0.3)`
*   **Trusted Range**: ±5 points.

## 2. Technical Architecture Changes

### 2.1. Frontend (React + TS)
*   New Component: `BulkInputPanel.tsx`
*   Enhanced Component: `KnowledgeSunburst.tsx` (Add interaction & animation)
*   New Service: Report Generation Client

### 2.2. Backend (FastAPI)
*   New Endpoint: `POST /bulk-submit` (Transactional batch processing)
*   New Service: `ReportService` (Data aggregation, PDF generation using WeasyPrint/Playwright)
*   New Service: `PredictionService` (V1 logic implementation)
*   Task Queue: Celery + Redis for asynchronous report generation.

### 2.3. Database (PostgreSQL)
*   Schema updates to support bulk operations efficienty.

## 3. Roadmap (4 Weeks)

*   **Week 1**: Infrastructure (AWS) & CMS Optimization.
*   **Week 2**: Knowledge Map Visuals (Coloring, Export).
*   **Week 3**: Automated Report System (Template, Pipeline).
*   **Week 4**: Prediction Model & Integrated Testing.
