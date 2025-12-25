# Math Advanced Data Inventory & Acquisition Strategy

## 1. Overview
본 문서는 초등 심화 수학 서비스 구현에 필요한 핵심 데이터(기출문제, 학습자료)의 확보 경로와 현재 수집 현황을 기록한다.

## 2. Data Acquisition Channels (획득 경로)

### 2.1. Official & Public Channels (White Market)
| Channel | URL / Source | Content Type | Cost | Reliability |
| :--- | :--- | :--- | :--- | :--- |
| **KJMO (대한수학회)** | [kms.or.kr](https://www.kms.or.kr/math/kjmo/past) | PDF (Problem, Answer) | Free | High |
| **KMA (AI교육평가원)** | [kma-e.com](http://www.kma-e.com) | PDF (Pre-test) | Free | High |
| **EBS Math** | [ebsmath.co.kr](https://www.ebsmath.co.kr) | Problems, Videos | Free | High |

### 2.2. Commercial Channels (Paid)
| Channel | Source | Content Type | Cost | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Yes24 / Kyobo** | [yes24.com](http://www.yes24.com) | Physical Books (Scanned) | 20k-30k KRW | Detailed solutions included |
| **Matholic** | [matholic.com](https://www.matholic.com) | Solution SaaS | Monthly Sub | Generated PDFs are standardized |

### 2.3. Community & Sharing (Grey Market)
| Channel | Keywords / Source | Content Type | Notes |
| :--- | :--- | :--- | :--- |
| **Scribd** | `최상위수학`, `3% 올림피아드 pdf` | Scanned PDF | Requires Subscription/Upload |
| **Tistory Blogs** | `modoo-math`, `dev-review` | Links, HWP files | Hard to verify version |
| **Mothers' Communities** | `Momschool`, `Naver Cafe` | Image Captures | Fragmented data |

## 3. Data Inventory Status (수집 현황)

### 3.1. Collected Assets (확보 완료)
*   [ ] **KJMO 기출문제 (2019-2023)**: 대한수학회 사이트에서 일괄 다운로드 예정.
*   [ ] **HME 기출문제 (Sample)**: 천재교육 사이트 샘플 문항.
*   [ ] **성대경시 (Mock Data)**: 시중 문제집 기반으로 유형화된 Mock Data 생성.

### 3.2. Target Assets (확보 예정)
*   **Target**: 2024년도 주요 경시대회(KMC, 성대경시) 기출 문항.
*   **Method**:
    1.  서점에서 기출문제집 구매 후 OCR 스캔.
    2.  또는 온라인 공유 플랫폼에서 스캔본 검색 및 다운로드.
    3.  확보된 이미지를 `backend/scripts/ingest_exam.py`를 통해 DB화.

## 4. Action Plan (데이터 수집 실행)

### Step 1: Web Crawling & Downloading
*   `KJMO` 및 `KMA` 공식 사이트의 공개 PDF를 자동으로 수집하는 크롤러(`scripts/crawl_exams.py`) 가동.
*   수집 폴더: `data/raw/exams/`

### Step 2: Manual Ingestion
*   상용 문제집(스캔본)은 저작권 문제로 자동 크롤링 불가.
*   사용자가 직접 `data/raw/uploads/`에 PDF를 넣으면, 시스템이 이를 감지하여 텍스트 추출 시작.

### Step 3: AI Processing
*   수집된 Raw Data를 `Question` 스키마(Metadata 포함)로 변환하여 DB 적재.

---
**Note**: 본 문서는 데이터 획득 경로를 정리한 것이며, 실제 저작권이 있는 파일은 저장소에 커밋하지 않고 로컬 `data/` 디렉토리에서만 관리한다.
