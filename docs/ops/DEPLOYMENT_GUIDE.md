# Deployment Guide

## 1. 인프라 요구사항
- **OS**: Linux (Ubuntu 22.04 LTS 권장)
- **Container Runtime**: Docker 20.10+, Docker Compose v2
- **Database**: PostgreSQL 14+ (Managed Service 권장: AWS RDS, GCP Cloud SQL)

## 2. Docker 구성
서비스는 `docker-compose.yml`을 통해 오케스트레이션됩니다.

### 서비스 목록
1. **backend**: FastAPI Application
2. **frontend**: Nginx serving React Build
3. **worker**: Celery Worker for AI/Async tasks
4. **redis**: Message Broker & Cache
5. **postgres**: (Local Dev Only) Database

### docker-compose.yml 예시
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    env_file: .env.prod
    ports:
      - "8000:8000"
    depends_on:
      - redis
      
  worker:
    build: ./backend
    command: celery -A app.core.celery_app worker -l info
    env_file: .env.prod
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
```

## 3. 배포 프로세스 (CI/CD)

### GitHub Actions 워크플로우
1. **Build & Test**: Main 브랜치 푸시 시 자동 실행
   - Frontend: `npm run build`, `npm run test`
   - Backend: `pytest`
2. **Docker Build & Push**: 테스트 통과 시 DockerHub/ECR로 이미지 푸시
3. **Deploy**:
   - 운영 서버에 SSH 접속
   - `docker-compose pull`
   - `docker-compose up -d`

## 4. 환경 변수 설정
`.env.prod` 파일은 보안상 저장소에 포함되지 않아야 합니다.

```ini
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=very_secure_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
OPENAI_API_KEY=sk-...
MATHPIX_APP_ID=...
MATHPIX_APP_KEY=...
```

## 5. SSL 인증서
- Let's Encrypt 및 Certbot을 사용하여 Nginx 컨테이너에 SSL 적용
- 또는 AWS ACM + Load Balancer 사용 권장
