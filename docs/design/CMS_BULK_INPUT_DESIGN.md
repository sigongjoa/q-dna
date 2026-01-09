# CMS Bulk Input Design

## 1. Problem Statement
Current CMS allows only single-record entry, making it time-consuming for tutors to input data for 15-30 students (approx. 30 problems/day).

## 2. Solution: Bulk Input Panel

### 2.1. UI Layout
*   **Grid Layout**: Spread-sheet like interface.
*   **Columns**:
    *   Student Name (Dropdown/Search)
    *   Problem ID / Number (Autocomplete)
    *   Correct/Incorrect (Toggle or Checkbox)
    *   Solving Time (Optional, Minutes)
    *   Notes (Text)
    *   Action (Delete Row)

### 2.2. Interaction Design
*   **Keyboard Support**:
    *   `Tab`: Move to next cell.
    *   `Enter`: Move to next row (new entry).
    *   `Arrow Keys`: Navigate grid.
*   **Auto-Save**: Save draft to `localStorage` on every change. Restore on page load.
*   **Validation**: Highlight invalid Problem IDs immediately.

### 2.3. Data Structure (Frontend State)
```typescript
interface BulkInputRow {
  id: string; // Temporary UUID for UI key
  studentId: string;
  problemId: string;
  isCorrect: boolean;
  solvingTime?: number;
  notes?: string;
}
```

### 2.4. API Integration
*   **Endpoint**: `POST /api/cms/bulk-submit`
*   **Payload**: `List<StudentProblemAttempt>`
*   **Response**: 
    *   Success: Count of inserted records.
    *   Partial Failure: List of failed records with reasons (e.g., Invalid Student ID).

## 3. Implementation Steps
1.  Create `BulkInputPanel` component.
2.  Implement `useBulkInput` hook for state management (local storage, validation).
3.  Design layout using existing CSS system (flex/grid).
4.  Integrate with `CmsService` for submission.
