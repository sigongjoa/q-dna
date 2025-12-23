# Backup & Recovery Plan

## 1. 개요
데이터는 교육 플랫폼의 가장 중요한 자산입니다. 시스템 장애, 데이터 손상, 랜섬웨어 등으로부터 데이터를 보호하고 신속하게 복구하기 위한 전략을 정의합니다.

## 2. 백업 대상
1. **Database (PostgreSQL)**: 사용자 정보, 문제 데이터, 학습 이력 (가장 중요)
2. **File Storage (S3)**: 문제 이미지, 첨부 파일
3. **Application Config**: `.env` 파일 (보안 백업), 인프라 설정 코드 (Git 관리)

## 3. 백업 전략 (PostgreSQL)

### A. Point-in-Time Recovery (PITR)
- **도구**: AWS RDS Automated Backups 또는 WAL-G
- **주기**: Transaction Log(WAL)를 실시간으로 저장
- **보관 기간**: 최근 7일 ~ 30일
- **목적**: 특정 시점(예: 사고 발생 1분 전)으로 데이터 복구

### B. Daily Snapshots
- **주기**: 매일 새벽 3시 (트래픽 최저 시간)
- **도구**: `pg_dump` 또는 클라우드 스냅샷
- **보관**: S3 Glacier로 이관하여 장기 보관 (1년)

## 4. 재해 복구 (Disaster Recovery)

### RTO (Recovery Time Objective)
- 목표: **4시간 이내** 서비스 정상화

### RPO (Recovery Point Objective)
- 목표: **최대 5분** 데이터 손실 허용 (PITR 적용 시 가능)

### 복구 시나리오
1. **DB 서버 장애**:
   - Standby Replica로 Failover (자동/수동)
2. **데이터 오염/삭제**:
   - 가장 최근의 안전한 시점으로 PITR 복구 수행
   - 복구된 DB 인스턴스로 어플리케이션 연결 정보 변경

## 5. 정기 훈련
- 분기별 1회, 백업본을 리스토어하여 데이터 무결성을 검증하는 모의 훈련을 실시합니다.
