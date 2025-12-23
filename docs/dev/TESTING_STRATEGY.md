# Testing Strategy

## 1. 테스트 목적
모든 코드는 배포 전 자동화된 테스트를 통과해야 하며, 시스템의 신뢰성과 안정성을 보장해야 합니다.

## 2. 테스트 레벨

### Unit Test (단위 테스트)
- **범위**: 개별 함수, 클래스, 컴포넌트
- **책임**: 개발자 본인
- **Backend 도구**: `pytest`
  - Service 레이어의 비즈니스 로직 검증
  - Utils 함수 검증
- **Frontend 도구**: `Jest`, `React Testing Library`
  - 컴포넌트 렌더링 검증
  - Hook 상태 변화 검증

### Integration Test (통합 테스트)
- **범위**: 모듈 간 상호작용, API 엔드포인트, DB 연동
- **책임**: Backend 개발자
- **도구**: `pytest` + `TestClient` (FastAPI)
  - 실제 DB(Test DB)를 사용하여 CRUD 동작 검증
  - 외부 API(OCR, LLM)는 Mocking하여 테스트

### E2E Test (엔드투엔드 테스트)
- **범위**: 사용자 시나리오 전체 (UI -> API -> DB)
- **책임**: QA / 개발자
- **도구**: `Cypress` 또는 `Playwright`
  - 주요 시나리오(로그인, 문제 풀이, 결과 확인) 자동화

## 3. 테스트 데이터 관리
- `conftest.py` (Pytest) 내에 Fixture를 정의하여 테스트 간 데이터 오염을 방지합니다.
- 테스트 실행 시마다 DB 트랜잭션을 롤백하거나, 매번 스키마를 재생성합니다.

## 4. CI 연동
GitHub Actions에서 PR이 생성되거나 푸시될 때마다 다음 명령어가 성공해야 합니다.
```bash
# Backend
pytest --cov=app tests/

# Frontend
npm run test
```
커버리지 목표는 **80%** 이상입니다.
