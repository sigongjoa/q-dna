# 초등 심화 수학 분석 및 생성 서비스 전략 (Q-DNA Extension)

## 1. 개요 및 배경
본 문서는 대한민국 초등 수학 심화 교육 생태계(경시대회, 학력평가 등)를 분석하고, 이를 바탕으로 **Q-DNA 플랫폼 내에 AI 기반 심화 문제 분석 및 변형 문제 생성 서비스**를 구현하기 위한 전략을 기술한다. 

본 프로젝트는 상업적 배포가 아닌 **개인 학습 및 연구 목적(Private Use)**의 SaaS 형태 시스템으로 구축되며, 기존 문제의 메타데이터 분석과 AI를 활용한 유사 문제(Twin Problem) 무제한 생성을 핵심 가치로 둔다.

## 2. 시장 분석 요약 (Context)
*   **이원화된 시장**: '보편적 점검(HME)'과 '엘리트 선발(성대경시, KJMO)'로 양분됨.
*   **니즈(Needs)**: 단순 교과를 넘어선 심화 사고력 문제와 이에 대한 상세한 해설, 그리고 취약점을 보완할 수 있는 추가 문제에 대한 수요가 높음.
*   **자료 접근성 이슈**: 기출문제는 서점(유료), 공식 사이트(PDF), 음지(공유) 등 다양한 경로로 유통되나, 체계적인 분석과 변형 학습 자료는 부족함.

## 3. 서비스 방향성 (Strategic Decisions)

사용자의 요구사항에 따른 핵심 의사결정 사항은 다음과 같다.

### 3.1. 타겟 및 범위 (Target & Scope)
*   **All-in-One Cover**: 보편적 수준(Mass)과 최상위권(Premium) 영역을 모두 포괄한다. 수학적 원리와 학습 메커니즘은 동일하므로 단일 시스템에서 난이도/유형 태깅으로 구분하여 처리한다.
*   **개인용 SaaS (Private SaaS)**: 대규모 상용 서비스가 아닌, 본인(Super Admin)이 직접 데이터를 넣고 결과를 활용하는 **내부 도구(Internal Tool)** 성격의 SaaS로 구축한다.

### 3.2. 핵심 모델: AI 기반 무한 기출 변형기 (Scenario B)
*   단순한 정보 제공을 넘어, **콘텐츠(문제) 자체를 생산**하는 것에 집중한다.
*   **메타데이터 검색엔진**: 기출문제의 유형, 난이도, 사고력 영역 등을 구조화하여 검색 가능하게 한다.
*   **AI Twin Problem Generator**: 저작권 이슈가 없는 학습용 '쌍둥이 문제(Twin Problem)'를 AI로 생성하여 무제한 학습 소스를 제공한다.
    *   *Note: 상업적 판매 목적이 아니므로 저작권 분쟁 소지 없음.*

### 3.3. 비즈니스 모델 및 로드맵
*   **Non-Profit**: 수익화 모델(구독, 결제 등)은 고려하지 않는다.
*   **Tech-Driven**: 로드맵 추천 같은 복잡한 비즈니스 로직보다는 **기술적 구현(분석 및 생성)**에 집중한다. SuperClaude Framework의 분석 방법론을 차용하여 고도화한다.

## 4. 시스템 아키텍처 및 기능 명세

### 4.1. 시스템 구조 (Architecture)
Q-DNA의 기존 `Question` 스키마와 `KnowledgeSunburst` 시각화 도구를 확장하여 통합한다.

1.  **Input Layer (Data Ingestion)**
    *   HME, KMC, 성대경시, KJMO 등의 기출문제(PDF/Text) 입력.
    *   OCR 및 텍스트 추출 (기존 도구 활용).
2.  **Analysis Layer (AI Core)**
    *   **Metadata Tagging**: 영역(정수, 기하, 조합 등), 난이도, 필요 사고력(추론, 문제해결 등) 자동 태깅.
    *   **Logic Extraction**: 문제의 풀이 논리 및 수식 구조 추출.
3.  **Generation Layer (Twin Engine)**
    *   추출된 논리를 바탕으로 숫자, 상황, 문맥을 변형한 새로운 문제 생성.
    *   문제에 대한 상세 해설 및 정답 자동 생성.
4.  **Presentation Layer (Frontend)**
    *   **Knowledge Sunburst**: 학생(사용자)의 영역별 성취도 및 기출문제 분포 시각화.
    *   **Editor & Viewer**: 생성된 문제 확인 및 PDF 내보내기.

### 4.2. 핵심 기능 상세

#### A. 메타데이터 분석 및 검색 (Analyzer)
*   **기능**: 업로드된 기출문제를 분석하여 Q-DNA의 `Tag` 시스템에 매핑.
*   **Data Fields**:
    *   `Source`: 대회명(HME, KMC...), 연도, 회차, 번호.
    *   `Domain`: 초등 수학 5대 영역 (수와 연산, 도형, 측정, 규칙성, 자료와 가능성) + 경시 심화 영역 (정수론, 조합 등).
    *   `Difficulty`: 정답률 기반 추정 또는 AI 평가 (L1 ~ L5).

#### B. AI 변형 문제 생성 (Generator)
*   **기능**: 선택한 특정 문제와 논리적으로 동형인 문제를 N개 생성.
*   **Prompt Strategy**: 
    *   "Extract the core mathematical logic and constraints from this problem."
    *   "Generate a new problem using different distinct objects and numbers but requiring the same solving steps."
*   **Validation**: 생성된 문제의 풀이 가능성 및 정답 오류 검증 (Self-Correction).

#### C. 개인화 대시보드 (Dashboard)
*   **기능**: 사용자의 학습 상태를 시각적으로 확인.
*   **Visualization**: `KnowledgeSunburst` 컴포넌트를 재활용하여 대단원-중단원-소단원 위계에 따른 강/약점 표시.

## 5. 구현 계획 (Implementation Plan)

### Phase 1: 데이터 스키마 확장
*   `Question` 모델에 경시대회 관련 메타데이터 필드 추가 (`source_exam`, `difficulty_level`, `exam_type` 등).
*   초등 심화 수학용 태그 트리(Tag Tree) 구축.

### Phase 2: 분석 파이프라인 구축
*   기출문제 텍스트를 입력받아 분류 결과를 반환하는 AI Agent(Script) 개발.
*   `backend/scripts` 내 분석 스크립트 작성.

### Phase 3: 생성 엔진 개발
*   LLM을 활용한 Twin Problem 생성 프롬프트 엔지니어링.
*   생성된 데이터를 DB에 저장하고 관리하는 API 개발.

### Phase 4: UI 통합
*   Frontend에 문제 입력/생성/조회 인터페이스 구현.
*   Sunburst Chart와 연동하여 분석 결과 시각화.
