# 🧪 E2E Test Scenario: Error Worksheet Generation

**Objective**: Verify that a user can create a question and generate an "Error Worksheet" PDF from the Question Editor.

## 1. Preconditions
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:5173`
- Ollama running with `qwen2.5` model
- WeasyPrint dependencies installed

## 2. Test Steps

### Step 1: Open Question Editor
- **Action**: Navigate to `http://localhost:5173/questions/new` (or click "Question Editor" from home).
- **Result**: Editor page loads.

### Step 2: Input Question Data
- **Action**:
    - Enter Problem Text: "철수는 사과 5개를 가지고 있습니다. 영희에게 2개를 주면 몇 개가 남나요?" (Simple Arithmetic)
    - Set Answer: "3" or "3개"
    - Set Type: "Short Answer"
- **Action**: Click **Save Question**.
- **Result**: "Question Saved!" alert appears. `currentQuestionId` is set.

### Step 3: Open Error Worksheet Dialog
- **Action**: Click the **"Error Worksheet"** button (Bug Icon).
- **Result**: Dialog opens showing error types.

### Step 4: Select Error Types
- **Action**: Select "Arithmetic Error" and "Condition Omission".
- **Action**: Click **"Download PDF"**.

### Step 5: Verification
- **Expected Result**:
    - Frontend sends `POST /questions/{id}/erroneous-solution`.
    - Backend generates PDF.
    - Browser downloads `error_worksheet_{id}.pdf`.
