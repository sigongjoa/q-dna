# Math Advanced Service Design Specification

## 1. 개요
본 문서는 초등 수학 심화 학습을 위한 문제 분석 및 생성 서비스의 기술적 설계를 다룬다. `Q-DNA` 플랫폼의 기존 인프라를 확장하여 구현하며, **AI 기반 메타데이터 분석**과 **Twin Problem 생성**을 핵심 기능으로 한다.

## 2. Data Model Design

### 2.1. Question Schema Extension

`backend/app/schemas/question.py`의 `QuestionBase` 모델 내 `content_metadata` 필드를 구조화된 형태로 정의한다. DB 레벨에서는 JSONB로 저장되지만, 애플리케이션 레벨에서는 Pydantic 모델로 검증한다.

```python
from typing import Literal, List, Optional
from pydantic import BaseModel

class ExamSourceInfo(BaseModel):
    name: str  # e.g., "KMC", "HME", "Sungkyunkwan"
    year: int
    session: Optional[str] = None  # e.g., "Pre", "Final" (전기/후기)
    grade: int # Target grade level (1-6)
    number: int # Question number in the original exam

class MathDomainInfo(BaseModel):
    # 5 Major Domains (Standard Curriculum)
    major_domain: Literal["Number", "Geometry", "Measurement", "Regularity", "Data"]
    # Specific Advanced Topic (e.g., "Pigeonhole Principle", "Combinatorics")
    advanced_topic: Optional[str] = None
    
class DifficultyMetrics(BaseModel):
    estimated_level: int = Field(ge=1, le=5) # 1: Easy, 5: Extreme
    required_skills: List[str] # e.g., ["Reasoning", "Calculation", "Spatial"]

class QuestionMetadata(BaseModel):
    source: ExamSourceInfo
    domain: MathDomainInfo
    difficulty: DifficultyMetrics
    is_twin_generated: bool = False
    original_question_id: Optional[str] = None # If twin, link to original
```

### 2.2. Tag Hierarchy (Ltree Strategy)

PostgreSQL `ltree` 확장을 활용하여 태그를 계층적으로 관리한다.

```
Subject.Math.Elementary
├── Exam
│   ├── HME
│   ├── KMC
│   └── KJMO
├── Domain
│   ├── Number (수와 연산)
│   ├── Geometry (도형)
│   ├── Pattern (규칙성)
│   └── Logic (논리/사고력)
└── Difficulty
    ├── L1 (Basic)
    └── L5 (Extreme)
```

## 3. Logic & Algorithms

### 3.1. Analysis Pipeline (AI Agent)
*   **Input**: Raw Text / Image of Question
*   **Process**:
    1.  **OCR & Text Normalization**: 텍스트 추출.
    2.  **Metadata Classification (LLM)**: 문제 내용을 분석하여 `ExamSourceInfo`, `MathDomainInfo` 추출.
    3.  **Tagging**: 추출된 정보를 `Tag` 테이블의 `path`로 매핑.

### 3.2. Twin Problem Generator (LLM)
*   **Input**: Source Question Metadata & Content
*   **Prompt Strategy**:
    *   **Role**: Professional Math Item Writer.
    *   **Task**: Create a structurally identical problem with different numbers/objects.
    *   **Constraint**: Maintain the exact logic and difficulty.
*   **Output**: New Question Stem, Answer Key, Solution Explanation.

## 4. API Specification

### 4.1. Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/questions/analyze` | raw 텍스트/이미지를 받아 메타데이터 분석 결과 반환 (AI) |
| `POST` | `/api/v1/questions/twin` | 특정 문제 ID를 기반으로 유사 문제 생성 |
| `GET` | `/api/v1/questions/search` | 메타데이터(대회, 영역 등) 기반 상세 검색 |

## 5. Frontend Components

### 5.1. Question Card
*   기존 문제 뷰어 확장.
*   하단에 "Metadata Badge" (예: `KMC 2023 | Geometry | Lv.5`) 표시.
*   "Generate Twin" 버튼 추가 -> 클릭 시 생성 로딩 후 결과 표시.

### 5.2. Analysis Dashboard
*   `KnowledgeSunburst` 컴포넌트 활용.
*   데이터 소스를 `UserHistory`와 조인하여, 각 영역(Domain)별 정답률 및 풀이 이력 시각화.
