# Monitoring and Logging Strategy

## 1. 개요
안정적인 서비스 운영을 위해 시스템의 상태를 실시간으로 감시하고, 문제 발생 시 빠르게 원인을 파악할 수 있도록 로깅 시스템을 구축합니다.

## 2. 모니터링 아키텍처 (Prometheus + Grafana)
- **Prometheus**: 시계열 메트릭 수집
- **Grafana**: 대시보드 시각화
- **Node Exporter**: 서버 리소스(CPU, RAM, Disk) 모니터링
- **cAdvisor**: 도커 컨테이너 리소스 모니터링

### 주요 모니터링 메트릭
1. **System**: CPU 사용량, 메모리 점유율, 디스크 I/O
2. **Application (FastAPI)**:
   - `http_requests_total`: 총 요청 수 (QPS)
   - `http_request_duration_seconds`: 응답 지연 시간 (Latency)
   - `error_rate`: 500/400 에러 비율
3. **Database**:
   - Active Connections
   - Cache Grid Ratio
   - Long Running Queries
4. **Celery**:
   - Queue Length
   - Worker Status

## 3. 로깅 전략 (Logging)

### Centralized Logging (ELK or EFK Stack)
소규모 운영 시에는 파일 로깅 + CloudWatch(AWS) 조합을 권장하며, 규모 확장 시 ELK 스택 도입을 고려합니다.

### 로그 레벨 정책
- **ERROR**: 시스템 동작 불가, 데이터 유실, 500 에러 (즉시 알림 필요)
- **WARNING**: 예상치 못한 상황이나 처리 가능, 향후 문제 소지 (일일 리포트)
- **INFO**: 주요 비즈니스 이벤트 (로그인, 문제 생성, 결제 등)
- **DEBUG**: 개발 및 디버깅 용도 (운영 환경에서는 비활성화 원칙)

### 로그 포맷 (Json)
기계 가독성을 위해 JSON 포맷 로그를 사용합니다.
```json
{
  "timestamp": "2025-12-23T10:00:00Z",
  "level": "INFO",
  "service": "backend",
  "trace_id": "12345",
  "message": "User login successful",
  "user_id": "user-uuid"
}
```

## 4. 알림 (Alerting)
- **채널**: Slack, Email, PagerDuty
- **알림 규칙**:
  - CPU 사용률 > 80% (5분 지속 시)
  - 5xx 에러율 > 1%
  - 디스크 여유 공간 < 10%
