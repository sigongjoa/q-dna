# Developer Setup Guide

## 필요 사전 지식
- **OS**: Windows (WSL2), Mac, Linux
- **Languages**: Python 3.11+, Node.js 18+
- **Tools**: Docker, Git, VSCode

## 1. 프로젝트 클론
```bash
git clone https://github.com/your-org/q-dna.git
cd q-dna
```

## 2. Backend 설정 (FastAPI)

### 가상환경 및 의존성 설치
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 환경 변수 설정
`backend/.env.example`을 `backend/.env`로 복사하고 설정값을 채워넣으세요.
```bash
cp .env.example .env
```

### 데이터베이스 마이그레이션
Docker로 로컬 DB를 띄운 후 실행합니다.
```bash
docker-compose up -d postgres redis
alembic upgrade head
```

### 서버 실행
```bash
uvicorn app.main:app --reload
```
서버는 `http://localhost:8000`에서 실행됩니다. Swagger 문서는 `/docs`에서 확인 가능합니다.

## 3. Frontend 설정 (React)

### 의존성 설치
```bash
cd frontend
npm install
```

### 환경 변수 설정
`frontend/.env.example` -> `frontend/.env`

### 개발 서버 실행
```bash
npm run dev
```
앱은 `http://localhost:5173` (Vite 기본)에서 실행됩니다.

## 4. 통합 개발 환경 (Docker Compose)
백엔드, 프론트엔드, DB를 한 번에 실행하려면:
```bash
docker-compose up --build
```

## 5. 트러블슈팅
- **PostgreSQL ltree 에러**: DB 접속 후 `CREATE EXTENSION ltree;` 쿼리를 직접 실행해 보세요.
- **Port 충돌**: 8000, 5432, 5173 포트가 사용 중인지 확인하세요.
