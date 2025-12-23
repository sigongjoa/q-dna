# API Specification (Draft)

## 개요
RESTful 원칙을 따르며, JSON 포맷을 기반으로 통신합니다. 모든 API는 인증 헤더(`Authorization: Bearer <token>`)를 요구합니다.

## Base URL
- Dev: `https://dev-api.q-dna.com/api/v1`
- Prod: `https://api.q-dna.com/api/v1`

## 주요 엔드포인트

### 1. Questions (문제 관리)

#### `POST /questions`
새로운 문제를 생성합니다.
- **Request**:
  ```json
  {
    "type": "mcq",
    "content": "이차방정식 x^2 - 4x + 4 = 0 의 해는?",
    "answer": {"correct": ["2"]},
    "difficulty": 0.3
  }
  ```
- **Response**: `201 Created`
  ```json
  { "id": "uuid-...", "status": "draft", ... }
  ```

#### `GET /questions`
문제 목록을 조회합니다 (필터링 지원).
- **Query Params**:
  - `page`: 페이지 번호
  - `limit`: 페이지 당 개수
  - `tags`: 태그 ID 목록 (comma separated)
  - `curriculum`: ltree 경로 (예: `Math.Algebra.*`)

#### `GET /questions/{id}`
특정 문제의 상세 정보를 조회합니다.

### 2. Curriculum (교육과정)

#### `GET /curriculum/tree`
전체 또는 특정 하위 트리의 커리큘럼 구조를 반환합니다.
- **Response**:
  ```json
  [
    {
      "id": 1,
      "name": "Math",
      "path": "Math",
      "children": [ ... ]
    }
  ]
  ```

### 3. Analytics (학습 분석)

#### `POST /analytics/attempt`
학생의 문제 풀이 결과를 전송합니다.
- **Request**:
  ```json
  {
    "question_id": "uuid...",
    "user_response": "3",
    "is_correct": false,
    "time_taken": 4500
  }
  ```
- **Response**: `200 OK`
  - BKT 모델 업데이트 트리거됨.

#### `GET /analytics/report/{user_id}`
특정 학생의 학습 리포트를 조회합니다 (지식 맵 데이터 포함).

## 에러 처리 (Error Handling)
일관된 에러 응답 포맷을 사용합니다.
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested question does not exist.",
    "details": { ... }
  }
}
```

## 인증 (Authentication)
- JWT (JSON Web Token) 기반 인증
- Access Token 만료 시간: 30분
- Refresh Token 만료 시간: 14일
