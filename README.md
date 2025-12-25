# Intelligent Question Bank & Tagging System (Q-DNA)

AI 기반의 적응형 학습 플랫폼을 구축하기 위한 지능형 문제 은행 및 태깅 시스템입니다.

## 🎯 주요 기능

### ✅ 실제 구현된 기능 (Production Ready)

- **AI 기반 OCR**: Tesseract + Ollama Vision으로 문제 이미지에서 텍스트와 수식 추출
- **자동 태깅**: Ollama LLM을 활용한 지능형 태그 자동 생성
- **학습 추적**: 실제 BKT (Bayesian Knowledge Tracing) 알고리즘 구현
- **개인화 추천**: 학생 능력치 기반 IRT 문제 추천
- **계층형 교육과정**: PostgreSQL ltree를 활용한 효율적인 커리큘럼 관리
- **실시간 분석**: 학생별 숙련도 맵 및 성취도 분석

## 🚀 빠른 시작

자세한 설치 및 실행 방법은 [QUICKSTART.md](./QUICKSTART.md)를 참조하세요.

### 최소 요구사항

```bash
# 1. Ollama 설치 및 모델 다운로드
ollama pull llama3.2-vision:11b
ollama pull llama3.1:8b

# 2. Docker Compose로 전체 스택 실행
docker-compose up --build

# 3. 데이터베이스 시드
docker-compose exec backend python -m scripts.seed_database
```

접속:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 기술 스택

### Backend
- **FastAPI** - 고성능 비동기 Python 웹 프레임워크
- **SQLAlchemy 2.0** - 비동기 ORM
- **PostgreSQL 14+** - ltree, JSONB, 파티셔닝 활용
- **Ollama** - 로컬 LLM 실행 (llama3.2-vision, llama3.1)
- **Tesseract OCR** - 텍스트 인식
- **Alembic** - 데이터베이스 마이그레이션

### Frontend
- **React 19** + **TypeScript**
- **Vite** - 빌드 도구
- **Material-UI (MUI)** - UI 컴포넌트
- **Nivo Charts** - 데이터 시각화
- **TanStack Query** - 서버 상태 관리
- **Zustand** - 전역 상태 관리

### Infrastructure
- **Docker** + **Docker Compose**
- **Poetry** - Python 패키지 관리
- **npm** - JavaScript 패키지 관리

## 🏗️ 프로젝트 구조

```
q-dna/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # REST API 엔드포인트
│   │   ├── core/                 # 설정, DB 연결
│   │   ├── models/               # SQLAlchemy 모델
│   │   ├── schemas/              # Pydantic 스키마
│   │   └── services/
│   │       ├── ollama_service.py     # Ollama LLM 클라이언트
│   │       ├── ocr_service.py        # OCR (Tesseract + Vision)
│   │       ├── tagging_service.py    # AI 자동 태깅
│   │       ├── analytics_service.py  # BKT & IRT 분석
│   │       └── question_service.py   # 문제 생성 워크플로우
│   ├── alembic/                  # DB 마이그레이션
│   └── scripts/                  # 유틸리티 스크립트
├── frontend/
│   └── src/
│       ├── components/           # 재사용 컴포넌트
│       ├── pages/                # 페이지 (Dashboard, Editor, Analytics)
│       └── services/             # API 클라이언트
├── docs/                         # 프로젝트 문서
└── docker-compose.yml
```

## 🔌 주요 API 엔드포인트

### Questions
- `POST /api/v1/questions/` - 문제 생성
- `GET /api/v1/questions/` - 문제 목록

### Curriculum
- `GET /api/v1/curriculum/tree` - 커리큘럼 계층 구조
- `POST /api/v1/curriculum/` - 노드 생성

### Tags
- `GET /api/v1/tags/` - 태그 목록
- `GET /api/v1/tags/suggest?text=...` - AI 태그 추천

### Analytics
- `POST /api/v1/analytics/attempt` - 학습 시도 기록 & BKT 업데이트
- `GET /api/v1/analytics/report/{user_id}` - 학생 리포트
- `GET /api/v1/analytics/recommend/{user_id}` - 개인화 추천

## 🤖 AI 기능 상세

### 1. OCR Service
**Tesseract + Ollama Vision 통합**
- 한글/영어 텍스트 인식
- LaTeX 수식 추출
- 구조화된 JSON 반환

```python
ocr_result = await ocr_service.extract_from_image_bytes(image_bytes)
# Returns: {"text": "...", "latex": [...], "combined": "...", "has_math": true}
```

### 2. AI Auto-Tagging
**Ollama LLM 기반 태깅**
- Bloom's Taxonomy 인지 수준 분류
- 과목/개념/스킬 자동 태깅
- 신뢰도 점수 제공 (0.0-1.0)

```python
tags = await tagging_service.get_tag_recommendations(question_text)
# Returns: [{"tag": "Algebra", "type": "concept", "confidence": 0.95}, ...]
```

### 3. BKT Knowledge Tracing
**실제 베이지안 지식 추적**
- 학생-스킬별 숙련도 추적
- P(L), P(T), P(S), P(G) 파라미터 관리
- 실시간 숙련도 업데이트

```python
mastery = await analytics_service.update_bkt(db, user_id, skill_id, is_correct)
# Returns: 0.85 (85% mastery probability)
```

### 4. IRT Recommendation
**문제 난이도 매칭**
- 학생 능력치 추정
- Zone of Proximal Development 기반 추천
- 난이도 범위 자동 조정

## 📊 데이터베이스 스키마

### 주요 테이블

**Questions** - 문제 본문, 정답, 메타데이터
- UUID 기본키
- JSONB content_metadata, answer_key
- IRT 파라미터 (difficulty, discrimination)

**CurriculumNodes** - ltree 계층 구조
- `Math.Algebra.Quadratics.Factoring` 형태의 경로
- GIST 인덱스로 서브트리 쿼리 최적화

**StudentMastery** - BKT 상태 추적
- user_id + skill_id 복합 키
- BKT 파라미터 (p_mastery, p_transit, p_slip, p_guess)

**AttemptLogs** - 월별 파티셔닝 로그
- 학습 이력 추적
- 시계열 분석용

## 🔧 개발 가이드

### 로컬 개발 환경

```bash
# Backend
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### 새 마이그레이션 생성

```bash
cd backend
poetry run alembic revision --autogenerate -m "Add new feature"
poetry run alembic upgrade head
```

### Ollama 모델 관리

```bash
# 모델 확인
ollama list

# 새 모델 추가
ollama pull <model-name>

# 모델 삭제
ollama rm <model-name>
```

## 📖 문서

- **[QUICKSTART.md](./QUICKSTART.md)** - 빠른 시작 가이드
- **[docs/architecture/](./docs/architecture/)** - 시스템 아키텍처
- **[docs/dev/](./docs/dev/)** - 개발자 가이드
- **[docs/ops/](./docs/ops/)** - 운영 가이드

## 🐛 트러블슈팅

### Ollama 연결 실패
```bash
# Ollama 상태 확인
curl http://localhost:11434/api/tags

# 재시작
ollama serve
```

### DB 마이그레이션 오류
```bash
# 마이그레이션 초기화
docker-compose down -v
docker-compose up -d postgres
poetry run alembic upgrade head
```

### 프론트엔드 빌드 오류
```bash
rm -rf node_modules package-lock.json
npm install
```

## 🎓 학습 리소스

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/
- **Ollama**: https://ollama.com/library
- **PostgreSQL ltree**: https://www.postgresql.org/docs/current/ltree.html
- **React Query**: https://tanstack.com/query/latest

## 📝 라이선스

ISC

## 👥 기여

이슈 및 PR은 GitHub 저장소에서 환영합니다.

---

**Built with ❤️ using Ollama, FastAPI, and React**
