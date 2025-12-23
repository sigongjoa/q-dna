# Risk Management Plan

## 1. 개요
프로젝트 성공을 저해할 수 있는 잠재적 리스크를 식별하고, 이에 대한 예방 및 대응 계획을 수립합니다.

## 2. 리스크 매트릭스

| ID | 리스크 (Risk) | 발생 가능성 (Likelihood) | 영향도 (Impact) | 심각도 (Severity) | 대응 전략 (Mitigation) |
|----|--------------|------------------------|-----------------|-------------------|---------------------|
| R1 | **OCR 인식률 저하** | Medium | High | **High** | - Mathpix(유료) API 사용으로 정확도 확보 <br> - 수동 보정 UI 제공으로 Human-in-the-loop 구축 |
| R2 | **LLM 비용 초과** | High | Medium | **High** | - 토큰 사용량 모니터링 및 일일 한도 설정 <br> - 결과 캐싱 (Redis) <br> - 소형 LLM (Llama 3 등) 자체 호스팅 검토 |
| R3 | **복잡한 쿼리 성능 이슈** | Medium | High | **High** | - PostgreSQL 실행 계획 분석 <br> - Redis 캐싱 전략 고도화 <br> - 필요한 경우 ElasticSearch 도입 검토 |
| R4 | **일정 지연** | Medium | Medium | **Medium** | - 핵심 기능(Phase 1, 2) 우선순위 집중 <br> - MVP 스펙 조정 (Nice-to-have 기능 제외) |
| R5 | **데이터 개인정보 유출** | Low | Critical | **High** | - DB 암호화 및 접근 제어 강화 <br> - 개인 식별 정보(PII) 최소화 수집 |

## 3. 리스크 모니터링
- **주기**: 매주 스프린트 회의 시 리스크 테이블 검토 및 업데이트
- **책임자**: Project Manager (PM) 및 Tech Lead
