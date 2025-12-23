# Roadmap & Milestones

본 로드맵은 `IMPLEMENTATION_WORKFLOW.md`를 기반으로 구체화되었습니다.

## Q1: Foundation & Core System (Month 1-2)

### Sprint 1: 인프라 및 DB 설계 (Week 1-2)
- [ ] PostgreSQL 설치 및 ltree 확장 설정
- [ ] Questions, Tags, Curriculum 테이블 스키마 구현
- [ ] Backend Scaffolding (FastAPI)

### Sprint 2: 핵심 API 개발 (Week 3-4)
- [ ] 문제 CRUD API 구현
- [ ] 커리큘럼 트리 조회 API 구현
- [ ] 관리자용 기본 UI 프로토타입 (문제 입력)

## Q2: AI & Advanced Features (Month 3-4)

### Sprint 3: OCR 및 자동 태깅 (Week 5-7)
- [ ] Mathpix/Tesseract OCR 파이프라인 연동
- [ ] LLM (GPT-4) 기반 자동 태깅 프롬프트 최적화
- [ ] 비동기 작업 큐 (Celery) 구축

### Sprint 4: 학습 분석 및 학생 UI (Week 8-10)
- [ ] 학생용 문제 풀이 UI 구현
- [ ] BKT(Bayesian Knowledge Tracing) 알고리즘 구현
- [ ] 학습 데이터 수집 로그 시스템 구축

## Q3: Polishing & Launch (Month 5)

### Sprint 5: 대시보드 및 최적화 (Week 11-12)
- [ ] 교사/관리자용 통계 대시보드
- [ ] 성능 테스트 및 쿼리 튜닝
- [ ] 베타 배포

## Risk Management (리스크 관리)

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **OCR 정확도 저하** | High | Medium | Mathpix(유료) 사용 및 수동 보정 UI 제공 |
| **LLM 비용 증가** | Medium | High | 캐싱 적용, 소형 모델(Llama 3 등) 파인튜닝 고려 |
| **복잡한 쿼리 성능** | High | Medium | Redis 캐싱, Read Replica 도입, Materialized View 활용 |
| **일정 지연** | High | Medium | 핵심 기능 위주로 MVP 범위 축소 (Phase 1, 2 집중) |
