# 지능형 문제 은행 및 태깅 시스템 구현 워크플로우

## 프로젝트 개요
교육 데이터 관리 위기를 해결하기 위한 AI 기반 적응형 학습 플랫폼 구축

---

## Phase 1: 데이터베이스 아키텍처 구축 (2주)

### 1.1 PostgreSQL 환경 설정
**담당**: Backend Developer
**산출물**:
- PostgreSQL 14+ 설치 및 설정
- ltree, JSONB 확장 모듈 활성화
- 백업 및 복구 전략 수립

**구현 작업**:
```sql
-- Extension 설치
CREATE EXTENSION IF NOT EXISTS ltree;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 1.2 핵심 스키마 설계 및 구현
**담당**: Database Architect + Backend Developer
**산출물**: DDL 스크립트, ERD 다이어그램

**핵심 테이블**:

#### A. 문제 관리 테이블
```sql
CREATE TABLE questions (
    question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_type VARCHAR(50) NOT NULL CHECK (question_type IN ('mcq', 'short_answer', 'essay', 'matching')),
    content_stem TEXT NOT NULL,
    content_metadata JSONB DEFAULT '{}',
    answer_key JSONB NOT NULL,
    difficulty_index FLOAT DEFAULT 0.5 CHECK (difficulty_index BETWEEN 0 AND 1),
    discrimination FLOAT,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'review_pending', 'active', 'flagged', 'archived')),
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_questions_status ON questions(status);
CREATE INDEX idx_questions_difficulty ON questions(difficulty_index);
```

#### B. 계층형 커리큘럼 (Ltree 활용)
```sql
CREATE TABLE curriculum_nodes (
    node_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    path ltree NOT NULL,
    standard_code VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX curriculum_path_gist_idx ON curriculum_nodes USING GIST (path);
CREATE UNIQUE INDEX curriculum_path_idx ON curriculum_nodes(path);
```

#### C. 태그 시스템 (다차원)
```sql
CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    tag_type VARCHAR(50) NOT NULL CHECK (tag_type IN ('concept', 'cognitive_level', 'source', 'skill', 'custom')),
    parent_tag_id INTEGER REFERENCES tags(tag_id),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE question_tags (
    question_id UUID REFERENCES questions(question_id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(tag_id) ON DELETE CASCADE,
    confidence FLOAT DEFAULT 1.0,
    auto_tagged BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (question_id, tag_id)
);

CREATE INDEX idx_qtags_question ON question_tags(question_id);
CREATE INDEX idx_qtags_tag ON question_tags(tag_id);
```

#### D. 문제-커리큘럼 매핑
```sql
CREATE TABLE question_curriculum (
    question_id UUID REFERENCES questions(question_id) ON DELETE CASCADE,
    node_id INTEGER REFERENCES curriculum_nodes(node_id) ON DELETE CASCADE,
    relevance_score FLOAT DEFAULT 1.0,
    PRIMARY KEY (question_id, node_id)
);
```

#### E. 학생 풀이 로그 (파티셔닝)
```sql
CREATE TABLE attempt_logs (
    log_id BIGSERIAL,
    user_id UUID NOT NULL,
    question_id UUID REFERENCES questions(question_id),
    quiz_session_id UUID,
    response_data JSONB NOT NULL,
    is_correct BOOLEAN NOT NULL,
    score FLOAT NOT NULL,
    time_taken_ms INTEGER,
    device_info JSONB,
    attempted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (log_id, attempted_at)
) PARTITION BY RANGE (attempted_at);

-- 월별 파티션 생성 예시
CREATE TABLE attempt_logs_2025_01 PARTITION OF attempt_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE INDEX idx_logs_user_question ON attempt_logs(user_id, question_id);
CREATE INDEX idx_logs_attempted_at ON attempt_logs(attempted_at);
```

### 1.3 데이터 무결성 및 트리거 설정
**구현**:
```sql
-- 버전 관리 트리거
CREATE OR REPLACE FUNCTION update_question_version()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.content_stem != NEW.content_stem OR OLD.answer_key != NEW.answer_key THEN
        NEW.version = OLD.version + 1;
        NEW.updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER question_version_trigger
BEFORE UPDATE ON questions
FOR EACH ROW EXECUTE FUNCTION update_question_version();
```

---

## Phase 2: 백엔드 API 개발 (3주)

### 2.1 프로젝트 구조 설정
**기술 스택**: Python 3.11+ / FastAPI / SQLAlchemy 2.0
**산출물**:
- 프로젝트 scaffolding
- Poetry/pip 의존성 관리
- 환경 변수 설정 (.env)

**디렉토리 구조**:
```
question-bank-api/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── questions.py
│   │   │   ├── tags.py
│   │   │   ├── curriculum.py
│   │   │   └── analytics.py
│   ├── models/
│   │   ├── question.py
│   │   ├── tag.py
│   │   └── attempt.py
│   ├── schemas/
│   │   └── question.py
│   ├── services/
│   │   ├── question_service.py
│   │   ├── tagging_service.py
│   │   └── analytics_service.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   └── main.py
├── tests/
├── alembic/
└── requirements.txt
```

### 2.2 핵심 API 엔드포인트 구현

#### A. 문제 관리 API
```python
# POST /api/v1/questions - 문제 생성
# GET /api/v1/questions/{id} - 문제 조회
# PUT /api/v1/questions/{id} - 문제 수정
# DELETE /api/v1/questions/{id} - 문제 삭제 (soft delete)
# GET /api/v1/questions/search - 복합 필터 검색
```

**검색 파라미터**:
- `curriculum_path`: ltree 경로 (예: "Math.Algebra.*")
- `tags`: 태그 ID 배열
- `difficulty_range`: [min, max]
- `status`: 문제 상태
- `cognitive_level`: Bloom's taxonomy 레벨
- `unused_since`: 최근 사용되지 않은 문제

#### B. 태깅 API
```python
# POST /api/v1/tags - 태그 생성
# POST /api/v1/questions/{id}/tags - 문제에 태그 추가
# POST /api/v1/questions/bulk-tag - 대량 태깅
# GET /api/v1/tags/suggest - AI 자동 태깅 추천
```

#### C. 커리큘럼 API
```python
# GET /api/v1/curriculum/tree - 전체 커리큘럼 트리
# GET /api/v1/curriculum/path/{path} - 특정 경로 하위 노드
# POST /api/v1/curriculum/import - 국가 교육과정 표준 임포트
```

### 2.3 복잡한 쿼리 최적화
**Ltree 활용 예시**:
```python
# "Math.Algebra" 하위의 모든 문제 검색
query = """
SELECT q.* FROM questions q
JOIN question_curriculum qc ON q.question_id = qc.question_id
JOIN curriculum_nodes cn ON qc.node_id = cn.node_id
WHERE cn.path <@ 'Math.Algebra'
"""
```

---

## Phase 3: 관리자 UI/UX 개발 (4주)

### 3.1 프론트엔드 프로젝트 설정
**기술 스택**: React 18 + TypeScript + Vite
**라이브러리**:
- UI: Material-UI (MUI) 또는 Ant Design
- 폼: React Hook Form + Zod 검증
- 상태관리: Zustand 또는 Redux Toolkit
- 수식 렌더링: KaTeX
- 에디터: TinyMCE + MathType 플러그인

### 3.2 핵심 컴포넌트 개발

#### A. 문제 입력 에디터 (QuestionEditor)
**기능**:
- WYSIWYG 에디터 (이미지, 수식 포함)
- 실시간 미리보기
- 정답 키 입력 (문제 유형별 동적 폼)
- 드래그 앤 드롭 이미지 업로드
- LaTeX 인라인 입력 지원

**컴포넌트 구조**:
```tsx
<QuestionEditor>
  <ContentEditor />  {/* TinyMCE */}
  <MathToolbar />    {/* LaTeX 단축키 */}
  <AnswerKeyForm />  {/* 문제 유형별 동적 */}
  <PreviewPane />    {/* KaTeX 렌더링 */}
</QuestionEditor>
```

#### B. 태깅 패널 (TaggingPanel)
**기능**:
- 계층형 태그 트리 뷰 (React Tree View)
- 드래그 앤 드롭 태그 적용
- 인라인 태그 생성
- AI 추천 태그 표시 (신뢰도 점수 포함)

```tsx
<TaggingPanel>
  <TreeView data={curriculumTree} />
  <TagChipContainer>
    {appliedTags.map(tag => <Chip key={tag.id} />)}
  </TagChipContainer>
  <AIRecommendations />
</TaggingPanel>
```

#### C. 대량 태깅 그리드 (BulkTaggingGrid)
**기능**:
- 가상 스크롤 (react-window) - 수천 개 문제 렌더링
- 멀티 셀렉트 (Shift/Ctrl 지원)
- 인라인 편집
- 일괄 작업 툴바

```tsx
<BulkTaggingGrid>
  <FilterBar />  {/* 복합 필터 */}
  <ActionToolbar>
    <Button>태그 추가</Button>
    <Button>상태 변경</Button>
    <Button>난이도 수정</Button>
  </ActionToolbar>
  <VirtualizedDataGrid />
</BulkTaggingGrid>
```

### 3.3 관리자 대시보드
**화면**:
- 문제 은행 통계 (총 문제 수, 상태별 분포)
- 미태깅 문제 알림
- 문제 품질 이슈 (변별도 음수, 정답률 이상치)
- 최근 활동 로그

---

## Phase 4: AI 자동화 시스템 (3주)

### 4.1 Math OCR 파이프라인 구축

#### A. OCR 서비스 통합
**선택**: Mathpix API (유료) 또는 자체 구축 (Tesseract + LaTeX-OCR)

**API 래퍼 구현**:
```python
# app/services/ocr_service.py
import requests

class MathpixOCRService:
    def __init__(self, app_id, app_key):
        self.api_url = "https://api.mathpix.com/v3/text"
        self.headers = {
            "app_id": app_id,
            "app_key": app_key
        }

    def extract_from_image(self, image_path):
        with open(image_path, 'rb') as f:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                files={'file': f},
                data={'formats': ['text', 'latex_styled']}
            )
        return response.json()
```

#### B. 이미지 전처리 파이프라인
**라이브러리**: OpenCV, PIL
**프로세스**:
1. 이미지 업로드
2. 그레이스케일 변환
3. 노이즈 제거 (Gaussian Blur)
4. 문제 영역 자동 분할 (Contour Detection)
5. 각 영역을 OCR 처리
6. 결과 병합 및 DB 저장

### 4.2 LLM 자동 태깅 시스템

#### A. 프롬프트 엔지니어링
**GPT-4 / Claude 활용**:
```python
TAGGING_PROMPT = """
다음은 한국 고등학교 수학 문제입니다:

{question_text}

작업:
1. 이 문제가 다루는 교육과정 단원을 정확히 식별하세요.
2. Bloom's Taxonomy 기준으로 인지 수준을 분류하세요.
3. 주요 개념 키워드 3개를 추출하세요.

응답 형식 (JSON):
{{
  "curriculum_path": "수학(상).다항식.인수분해",
  "cognitive_level": "Apply",
  "keywords": ["복잡한 식", "인수분해", "치환"],
  "confidence": 0.95
}}
"""
```

#### B. 임베딩 기반 유사 문제 검색
**라이브러리**: sentence-transformers, Pinecone/Milvus
**프로세스**:
1. 모든 기존 문제를 임베딩 벡터로 변환
2. Pinecone에 인덱싱
3. 새 문제 입력 시 유사도 검색 (Top-5)
4. 유사 문제들의 공통 태그 추출
5. 빈도 기반 추천 (신뢰도 점수 계산)

```python
from sentence_transformers import SentenceTransformer
import pinecone

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

def get_tag_recommendations(question_text):
    # 벡터 변환
    query_vector = model.encode(question_text).tolist()

    # 유사 문제 검색
    results = index.query(vector=query_vector, top_k=5, include_metadata=True)

    # 태그 빈도 분석
    tag_freq = {}
    for match in results['matches']:
        for tag in match['metadata']['tags']:
            tag_freq[tag] = tag_freq.get(tag, 0) + match['score']

    # 정규화 및 반환
    recommendations = [
        {"tag": tag, "confidence": score / len(results['matches'])}
        for tag, score in sorted(tag_freq.items(), key=lambda x: -x[1])
    ]
    return recommendations[:10]
```

### 4.3 자동 태깅 워크플로우 통합
**UI 흐름**:
1. 관리자가 OCR로 문제 일괄 업로드
2. 백그라운드 작업: 각 문제에 대해 LLM + 임베딩 추천 실행
3. 문제 상태를 "AI Tagged - Pending Review"로 변경
4. 검수자 대시보드에 알림
5. 검수자가 추천 태그 승인/수정

---

## Phase 5: 학습 분석 알고리즘 (4주)

### 5.1 데이터 수집 인프라
**요구사항**: 모든 학생 활동 로그 수집
- 문제 풀이 시작/종료 시간
- 선택한 답안 (오답 선지 포함)
- 디바이스 정보
- 힌트 사용 여부

### 5.2 베이지안 지식 추적 (BKT) 구현
**라이브러리**: pyBKT
**모델 파라미터**:
- $P(L_0)$: 초기 학습 확률
- $P(T)$: 학습 전이 확률
- $P(G)$: 추측 확률
- $P(S)$: 실수 확률

```python
from pyBKT.models import Model

# 모델 초기화
model = Model(seed=42, num_fits=1)

# 데이터 준비 (user_id, item_id, correct, skill)
data = pd.DataFrame({
    'user_id': [1, 1, 1, 2, 2],
    'skill_name': ['algebra', 'algebra', 'geometry', 'algebra', 'algebra'],
    'correct': [0, 1, 1, 1, 1],
    'order_id': [1, 2, 3, 1, 2]
})

# 모델 학습
model.fit(data=data)

# 개별 학생의 스킬 마스터리 예측
predictions = model.predict(data=student_data)
```

**적용**:
- 각 태그(개념)별로 BKT 모델 유지
- 학생이 문제를 풀 때마다 해당 태그의 마스터 확률 업데이트
- 마스터 확률 < 0.7인 태그를 "취약점"으로 식별

### 5.3 문항 반응 이론 (IRT) 구현
**라이브러리**: py-irt
**모델**: 2-Parameter Logistic Model (2PL)

```python
from py_irt import irt

# 데이터 준비: 학생 x 문제 행렬
response_matrix = [
    [1, 0, 1, 1],  # 학생 1
    [1, 1, 1, 0],  # 학생 2
    [0, 0, 1, 0],  # 학생 3
]

# IRT 모델 학습
item_params, user_params = irt(
    response_matrix,
    num_theta=100,  # 능력치 해상도
    max_iter=100
)

# 결과: item_params['b'] = 난이도, item_params['a'] = 변별도
# user_params['theta'] = 학생 능력치
```

**활용**:
- 문제 난이도 동적 업데이트 (매주 재계산)
- 학생 능력치 추정
- 적응형 문제 선택: $|\theta - b| < 0.3$ 범위의 문제 추천

### 5.4 오답 패턴 분석
**구현**:
```python
# 오답 선지에 오개념 태그 매핑
distractor_tags = {
    "option_b": ["misconception:order_of_operations"],
    "option_c": ["misconception:negative_sign"]
}

# 학생의 오답 패턴 집계
def analyze_error_patterns(user_id):
    errors = db.query(AttemptLog).filter(
        AttemptLog.user_id == user_id,
        AttemptLog.is_correct == False
    ).all()

    misconception_count = {}
    for error in errors:
        selected = error.response_data['selected_option']
        if selected in distractor_tags:
            for tag in distractor_tags[selected]:
                misconception_count[tag] = misconception_count.get(tag, 0) + 1

    # 빈도 상위 3개 오개념 반환
    return sorted(misconception_count.items(), key=lambda x: -x[1])[:3]
```

---

## Phase 6: 시각화 및 대시보드 (2주)

### 6.1 학생용 대시보드

#### A. 지식 맵 시각화
**라이브러리**: D3.js 또는 ECharts
**차트 타입**: 썬버스트(Sunburst) 또는 트리맵(Treemap)

```tsx
import { Sunburst } from '@nivo/sunburst';

<Sunburst
  data={curriculumData}
  value="mastery_score"
  colorBy="mastery_level"
  animate={true}
/>
```

**데이터 구조**:
```json
{
  "name": "수학",
  "children": [
    {
      "name": "대수",
      "mastery_score": 0.85,
      "children": [
        {"name": "인수분해", "mastery_score": 0.95},
        {"name": "이차방정식", "mastery_score": 0.75}
      ]
    }
  ]
}
```

#### B. 성장 곡선 그래프
**차트**: 시계열 라인 차트 (능력치 변화)
```tsx
<LineChart>
  <XAxis dataKey="date" />
  <YAxis domain={[-3, 3]} label="Ability (θ)" />
  <Line dataKey="theta" stroke="#8884d8" />
</LineChart>
```

### 6.2 교사용 대시보드

#### A. 학급 취약점 히트맵
**라이브러리**: Recharts Heatmap
```tsx
<ResponsiveHeatMap
  data={classHeatmapData}
  axisTop={{ legend: '단원' }}
  axisLeft={{ legend: '학생' }}
  colors={{
    type: 'diverging',
    scheme: 'red_yellow_green',
    divergeAt: 0.5
  }}
/>
```

#### B. 문제 품질 대시보드
**지표**:
- 정답률 < 10% 또는 > 95% (난이도 이상치)
- 변별도 < 0 (상위권이 더 많이 틀림)
- 최근 30일간 미사용 문제
- 오류 신고 건수

---

## Phase 7: 통합 테스트 및 배포 (2주)

### 7.1 단위 테스트
**프레임워크**: pytest (Backend), Jest (Frontend)
**커버리지 목표**: 80% 이상

**테스트 범위**:
- API 엔드포인트 (FastAPI TestClient)
- 데이터베이스 쿼리 (fixtures)
- BKT/IRT 알고리즘 정확도
- OCR 파이프라인 (모킹)

### 7.2 통합 테스트
**시나리오**:
1. 문제 입력 → OCR 추출 → 자동 태깅 → 검수 → 활성화
2. 학생 풀이 → 로그 수집 → BKT 업데이트 → 추천 문제 생성
3. 대량 태깅 → 커리큘럼 필터링 → 시험지 생성

### 7.3 성능 테스트
**도구**: Locust, k6
**부하 시나리오**:
- 동시 접속 1,000명
- 초당 100개 문제 풀이 로그 생성
- 복잡한 ltree 쿼리 응답 시간 < 200ms

### 7.4 배포 전략
**인프라**: AWS / GCP
**서비스**:
- RDS (PostgreSQL) - Multi-AZ
- EC2 / ECS (API 서버) - Auto Scaling
- S3 (이미지 저장)
- CloudFront (CDN)
- Lambda (OCR 백그라운드 작업)

**CI/CD**:
- GitHub Actions
- Docker 컨테이너화
- 블루-그린 배포

---

## Phase 8: 운영 및 개선 (지속)

### 8.1 모니터링
**도구**: Prometheus + Grafana
**메트릭**:
- API 응답 시간
- DB 커넥션 풀 사용률
- OCR API 사용량
- BKT 모델 재학습 주기

### 8.2 데이터 품질 관리
**자동화 작업**:
- 매주 IRT 모델 재계산
- 문제 품질 이슈 자동 감지 및 알림
- 미사용 문제 자동 아카이빙

### 8.3 피드백 루프
**수집**:
- 학생 오류 신고
- 교사 태깅 수정 패턴 분석
- AI 추천 태그 승인률 추적

**개선**:
- LLM 프롬프트 최적화
- 임베딩 모델 파인튜닝
- BKT 파라미터 조정

---

## 핵심 성공 요소 (Critical Success Factors)

### 1. 데이터 품질
- **초기 커리큘럼 구조**: 한국 교육과정 2015/2022 개정안 정확 반영
- **태그 표준화**: 블룸 택소노미 엄격 준수
- **검수 프로세스**: AI 태깅 후 반드시 인간 검수

### 2. 확장성
- **DB 파티셔닝**: 로그 테이블 월별 파티션 필수
- **캐싱 전략**: Redis로 커리큘럼 트리, 빈번한 쿼리 캐싱
- **비동기 처리**: OCR, AI 태깅은 Celery/RabbitMQ로 백그라운드 처리

### 3. 사용자 경험
- **관리자 도구**: 태깅 작업 시간 50% 단축 목표
- **학생 대시보드**: 3초 이내 로딩
- **모바일 최적화**: 반응형 디자인 필수

---

## 기술 스택 최종 정리

| 계층 | 기술 | 선정 이유 |
|------|------|----------|
| **Database** | PostgreSQL 14+ | ltree, JSONB, 강력한 쿼리 최적화 |
| **Backend** | Python 3.11 + FastAPI | AI 라이브러리 생태계, 비동기 지원 |
| **ORM** | SQLAlchemy 2.0 | 복잡한 쿼리, 마이그레이션 지원 |
| **Frontend** | React 18 + TypeScript | 컴포넌트 재사용성, 타입 안전성 |
| **UI Library** | Ant Design | 관리자 UI에 최적화된 컴포넌트 |
| **Math Rendering** | KaTeX | MathJax보다 5배 빠름 |
| **OCR** | Mathpix API | 수식 인식 최고 정확도 |
| **LLM** | GPT-4 / Claude 3.5 | 한국어 이해도, 태깅 정확도 |
| **Vector DB** | Pinecone | 관리형, 낮은 레이턴시 |
| **Analytics** | pyBKT, py-irt | 검증된 교육 데이터 알고리즘 |
| **Infra** | AWS (RDS, ECS, S3) | 엔터프라이즈 안정성 |
| **CI/CD** | GitHub Actions | 무료, Git 통합 |

---

## 예상 타임라인

| Phase | 기간 | 병렬 가능 여부 |
|-------|------|----------------|
| Phase 1: DB 설계 | 2주 | - |
| Phase 2: Backend API | 3주 | Phase 3과 일부 병렬 |
| Phase 3: Admin UI | 4주 | Phase 2 완료 후 |
| Phase 4: AI 자동화 | 3주 | Phase 5와 병렬 |
| Phase 5: 학습 분석 | 4주 | Phase 4와 병렬 |
| Phase 6: 대시보드 | 2주 | Phase 5 완료 후 |
| Phase 7: 테스트/배포 | 2주 | - |
| **총 소요 기간** | **약 16주 (4개월)** | 최적화 시 12주 가능 |

---

## 다음 단계 (Next Actions)

1. **즉시 시작 가능한 작업**:
   - PostgreSQL 설치 및 ltree 확장 활성화
   - 한국 교육과정 목차 수집 (curriculum_nodes 초기 데이터)
   - FastAPI 프로젝트 scaffolding

2. **의사결정 필요 사항**:
   - OCR: Mathpix (유료) vs 오픈소스 (Tesseract)
   - LLM: GPT-4 (OpenAI) vs Claude (Anthropic) vs 자체 모델
   - 클라우드: AWS vs GCP vs 온프레미스

3. **리소스 확보**:
   - Backend 개발자 1명
   - Frontend 개발자 1명
   - 교육 데이터 검수자 (교사) 1명
   - 초기 문제 데이터 1,000개 이상

---

## 참고 자료
- [Moodle Question Bank Documentation](https://docs.moodle.org/dev/Question_database_structure)
- [pyBKT GitHub](https://github.com/CAHLR/pyBKT)
- [PostgreSQL ltree Documentation](https://www.postgresql.org/docs/current/ltree.html)
- [Mathpix API](https://mathpix.com/docs)
- [IMS QTI 3.0 Standard](https://www.imsglobal.org/spec/qti/v3p0)
