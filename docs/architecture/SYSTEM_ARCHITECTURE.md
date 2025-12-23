# System Architecture

## 1. 시스템 개요
본 시스템은 MSA(Microservice Architecture) 지향적인 모듈러 모놀리스(Modular Monolith) 구조로 시작하여, 향후 확장을 고려한 설계를 따릅니다.

## 2. 전체 아키텍처 다이어그램 (Mermaid)

```mermaid
graph TD
    User[User (Student/Teacher/Admin)] -->|HTTPS| CDN[CloudFront CDN]
    CDN --> LB[Load Balancer]
    
    subgraph Frontend Layer
        Web[React SPA (Vite)]
        Admin[Admin Dashboard]
    end
    
    LB --> Web
    LB --> Admin
    
    subgraph Application Layer
        API[FastAPI Server]
        Worker[Celery Worker]
    end
    
    Web -->|REST API| API
    Admin -->|REST API| API
    
    API -->|Async Task| Redis[Redis MQ & Cache]
    Redis --> Worker
    
    subgraph Data Layer
        DB[(PostgreSQL 14+)]
        VectorDB[(Pinecone/Milvus)]
        S3[AWS S3 (Images/Files)]
    end
    
    API -->|SQL| DB
    Worker -->|Write| DB
    Worker -->|OCR/Tagging| AI[AI Service (LLM/OCR)]
    
    API -->|Embedding Search| VectorDB
    API -->|File Upload| S3
    
    subgraph Analysis Layer
        BKT[BKT Engine]
        IRT[IRT Engine]
    end
    
    Worker --> BKT
    Worker --> IRT
```

## 3. 기술 스택 상세

### Frontend
- **Framework**: React 18, TypeScript
- **State Management**: Zustand (Global Store), React Query (Server State)
- **UI Toolkit**: Ant Design (Admin), TailwindCSS (Custom Styling)
- **Visualization**: D3.js, Recharts, KaTeX (Math)

### Backend
- **Framework**: FastAPI (Python 3.11)
- **ORM**: SQLAlchemy 2.0 (AsyncIO)
- **Task Queue**: Celery + RabbitMQ/Redis
- **API Documentation**: OpenAPI (Swagger UI)

### Database
- **Primary DB**: PostgreSQL 14+
  - Extensions: `ltree` (Curriculum Hierarchy), `pg_trgm` (Text Search)
- **Vector DB**: Pinecone (Managed) or Milvus (Self-hosted)
- **Cache**: Redis

### AI & Analytics
- **OCR**: Mathpix API (Initial), Tesseract (Fallback)
- **LLM**: GPT-4 or Claude 3.5 Sonnet (via API)
- **Analytics**: pyBKT (Knowledge Tracing), py-irt (Item Response Theory)

## 4. 데이터 흐름

### 4.1 문제 생성 및 태깅
1. 관리자가 문제 이미지 업로드 (Admin UI)
2. API 서버가 이미지를 S3에 저장하고 Celery Task 발행
3. Worker가 OCR 수행 및 텍스트/수식 추출
4. Worker가 LLM을 호출하여 메타데이터(단원, 난이도 등) 추출 및 자동 태깅
5. 결과가 DB에 'Draft' 상태로 저장
6. 관리자가 최종 검수 후 'Active'로 변경

### 4.2 학습 및 추천
1. 학생이 문제 풀이 제출
2. API 서버가 로그를 `attempt_logs` 테이블에 기록 (비동기)
3. 배치/실시간 작업으로 BKT 모델 업데이트 (학생의 개념별 숙련도 갱신)
4. 다음 문제 요청 시, IRT 엔진이 학생 능력치($\theta$)와 문제 난이도($b$)를 고려하여 최적 문제 추천
