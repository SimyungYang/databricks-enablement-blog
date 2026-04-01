# Module 1: Foundation - Lakehouse 아키텍처 & Unity Catalog

## 이 가이드 사용 방법

>**이 교육 자료는 Claude Code (또는 Cursor)와 함께 사용합니다.**>
> 1. 터미널에서 프로젝트 디렉토리로 이동: `cd ~/smarttv-training`
> 2. Claude Code 실행: `claude`
> 3. 이 문서의 각 Step에 있는 "**Claude에게 요청하기**" 박스의 내용을 복사하여 Claude에게 붙여넣기
> 4. Claude가 AI Dev Kit의 MCP 도구를 사용하여 Databricks에서 직접 실행합니다
> 5. 실행 결과를 확인하고, 이해가 안 되는 부분은 Claude에게 질문하세요
>
>**핵심:**여러분이 직접 코드를 작성할 필요 없이, Claude에게 자연어로 요청하면 됩니다!

---

## 📓 노트북으로 빠르게 시작하기

> 가상 데이터 생성은 **Databricks 노트북으로 한번에 실행**할 수 있습니다.
>
> 워크스페이스 경로: `/Workspace/Users/{your_email}/smarttv-training/`
>
> 1.**`01_setup_catalog_schema`**— 카탈로그/스키마 생성 (1분)
> 2.**`02_generate_synthetic_data`**— 전체 가상 데이터 170만건 생성 (5~10분)
>
> 노트북을 순서대로 실행한 후, 아래 Step 6부터 Delta Lake 기능을 체험하세요.

---

## 학습 목표

- Databricks Lakehouse 아키텍처 이해
- Unity Catalog의 3단계 네임스페이스 (Catalog > Schema > Table) 이해
- Delta Lake 기본 기능 체험 (ACID 트랜잭션, Time Travel, Schema Evolution)
-**Smart TV 시나리오의 가상 데이터 생성**---

## 시나리오 소개: Smart TV 데이터

이번 교육에서는 Smart TV의 스마트TV 데이터를 시뮬레이션합니다:

| 데이터 | 설명 | 예시 |
|--------|------|------|
|**디바이스 정보**| TV 모델, 지역, 등록일 | OLED65C4, Korea, 2024-01-15 |
|**시청 로그**| 채널/앱 시청 기록 | Netflix 시청 2시간, 지상파 MBC 30분 |
|**이벤트/클릭 로그**| 리모컨 조작, UI 클릭 | FastTV 배너 클릭, 앱 실행, 설정 변경 |
|**FastTV 광고 로그**| 광고 노출/클릭/전환 | 삼성전자 광고 노출 → 클릭 → 구매페이지 이동 |
|**콘텐츠 메타데이터**| 프로그램/앱 정보 | 장르, 등급, 키워드 |

---

## Step 1: 교육용 카탈로그 & 스키마 생성

### Claude에게 요청하기

```
Databricks에 교육용 환경을 만들어줘.

1. 카탈로그 생성: {catalog}
2. 스키마 3개 생성:
  - {catalog}.bronze (원본 데이터)
  - {catalog}.silver (정제 데이터)
  - {catalog}.gold (분석/서빙 데이터)
3. 각 스키마에 대한 설명(COMMENT)도 추가해줘

생성 후 카탈로그 구조를 확인해서 보여줘.
```

### 기대 결과

```
{catalog} (카탈로그)
├── bronze (스키마) - 원본 데이터 저장
├── silver (스키마) - 정제/변환 데이터
└── gold (스키마)  - 분석/서빙용 집계 데이터
```

### 핵심 개념: Medallion Architecture

```
Bronze (원본)    Silver (정제)     Gold (서빙)
┌──────────┐   ┌──────────────┐   ┌──────────────┐
│ 원본 로그 │ ──→ │ 중복 제거   │ ──→ │ 일별 집계   │
│ JSON/CSV │   │ 타입 변환   │   │ 사용자 프로필 │
│ 비정형   │   │ 유효성 검증  │   │ 추천 피처   │
└──────────┘   └──────────────┘   └──────────────┘
```

---

## Step 2: 가상 데이터 생성 - 디바이스 마스터

### Claude에게 요청하기

```
Smart TV 디바이스 마스터 데이터를 생성해줘.

테이블: {catalog}.bronze.devices
레코드 수: 10,000대

컬럼 정의:
- device_id: UUID (고유 디바이스 ID)
- model_name: LG TV 모델명 (OLED65C4, OLED55B4, NANO75, UHD50UR, QNED85 등 10개 모델)
- screen_size: 화면 크기 (43, 50, 55, 65, 75, 86 인치)
- region: 판매 지역 (Korea, US, EU, Japan, SEA 등)
- country: 국가 (KR, US, DE, JP, TH 등 15개국)
- registered_at: 등록일 (2023-01-01 ~ 2025-03-01 랜덤)
- firmware_version: 펌웨어 버전 (webOS 6.0 ~ 24.0)
- has_fasttv: FastTV 지원 여부 (boolean, 80% true)
- subscription_tier: 구독 등급 (free, basic, premium)

Faker와 Spark를 사용해서 현실적인 데이터를 만들어줘.
생성 후 샘플 10건과 전체 통계를 보여줘.
```

### 기대 결과

- 10,000건의 디바이스 마스터 데이터 생성
- 모델별, 지역별 분포 통계 확인

---

## Step 3: 가상 데이터 생성 - 시청 로그

### Claude에게 요청하기

```
스마트TV 시청 로그 데이터를 생성해줘.

테이블: {catalog}.bronze.viewing_logs
레코드 수: 500,000건

컬럼 정의:
- log_id: UUID
- device_id: devices 테이블의 device_id 참조 (FK)
- user_profile_id: 디바이스 내 사용자 프로필 (1개 디바이스에 1~4명)
- content_type: 콘텐츠 유형 (live_tv, vod, app, fasttv)
- channel_or_app: 채널명/앱명 (MBC, KBS, SBS, Netflix, YouTube, Disney+, Tving, Coupang Play 등)
- genre: 장르 (drama, entertainment, news, sports, movie, kids, documentary)
- start_time: 시청 시작 시간 (2025-01-01 ~ 2025-03-01)
- duration_minutes: 시청 시간(분) (1~240, 평균 45분 정규분포)
- completion_rate: 시청 완료율 (0.0 ~ 1.0)

시간대별로 현실적인 분포를 적용해줘:
- 평일: 저녁 6시~11시에 집중 (60%)
- 주말: 오전~오후도 포함 (분산)
- 새벽 2시~6시는 매우 적게 (5%)

생성 후 시간대별 시청량 분포와 콘텐츠 유형별 통계를 보여줘.
```

---

## Step 4: 가상 데이터 생성 - 이벤트/클릭 로그

### Claude에게 요청하기

```
스마트TV UI 이벤트/클릭 로그를 생성해줘.

테이블: {catalog}.bronze.click_events
레코드 수: 1,000,000건

컬럼 정의:
- event_id: UUID
- device_id: devices 테이블 참조
- user_profile_id: 사용자 프로필 ID
- event_timestamp: 이벤트 발생 시간 (2025-01-01 ~ 2025-03-01)
- event_type: 이벤트 유형
 - app_launch (앱 실행)
 - channel_change (채널 전환)
 - search (검색)
 - banner_click (배너 클릭)
 - ad_click (광고 클릭)
 - menu_navigate (메뉴 탐색)
 - content_select (콘텐츠 선택)
 - voice_command (음성 명령)
 - settings_change (설정 변경)
 - power_on / power_off
- screen_name: 화면명 (home, fasttv, app_store, settings, search, channel_guide)
- element_id: 클릭 요소 ID (banner_01, app_icon_netflix, ad_slot_top 등)
- session_id: 세션 ID (power_on ~ power_off 사이)

생성 후 이벤트 유형별 분포와 화면별 클릭 히트맵 통계를 보여줘.
```

---

## Step 5: 가상 데이터 생성 - FastTV 광고 로그

### Claude에게 요청하기

```
FastTV 광고 노출/클릭/전환 로그를 생성해줘.

테이블: {catalog}.bronze.ad_impressions
레코드 수: 200,000건

컬럼 정의:
- impression_id: UUID
- device_id: devices 테이블 참조
- user_profile_id: 사용자 프로필 ID
- ad_id: 광고 ID (ad_001 ~ ad_200)
- advertiser: 광고주 (삼성전자, 현대자동차, CJ제일제당, 신한카드, 쿠팡, 네이버, 카카오 등 30개)
- ad_category: 광고 카테고리 (electronics, automotive, food, finance, ecommerce, telecom, beauty, travel)
- ad_format: 광고 형식 (banner, video_pre_roll, video_mid_roll, native, interstitial, screensaver)
- placement: 노출 위치 (fasttv_home, fasttv_channel, app_launch, channel_guide, screensaver)
- impression_timestamp: 노출 시간
- was_clicked: 클릭 여부 (boolean, CTR 약 2~5%)
- click_timestamp: 클릭 시간 (nullable)
- was_converted: 전환 여부 (클릭 중 10~20%)
- bid_price_usd: 입찰가 (0.001 ~ 0.05)
- win_price_usd: 낙찰가 (bid_price의 60~90%)
- duration_seconds: 광고 노출 시간 (15, 30, 60초)

현실적인 CTR 분포를 적용해줘:
- video_pre_roll: CTR 3~5%
- banner: CTR 1~2%
- native: CTR 4~7%
- screensaver: CTR 0.5~1%

생성 후 광고 형식별 CTR, 광고주별 노출수, 시간대별 광고 효과 통계를 보여줘.
```

---

## Step 6: Delta Lake 기본 기능 체험

### 6-1. 테이블 히스토리 & Time Travel

#### Claude에게 요청하기

```
Delta Lake의 Time Travel 기능을 체험해볼게.

1. {catalog}.bronze.devices 테이블의 히스토리를 보여줘
2. devices 테이블에서 model_name이 'OLED65C4'인 디바이스의 region을 'Korea' → 'KR'로 업데이트해줘
3. 업데이트 후 히스토리를 다시 보여줘
4. Time Travel로 업데이트 전 버전의 데이터를 조회해줘 (VERSION AS OF)
5. RESTORE 명령으로 원래 상태로 복원해줘

각 단계에서 어떤 일이 일어나는지 설명도 해줘.
```

### 6-2. Schema Evolution

#### Claude에게 요청하기

```
Schema Evolution을 테스트해볼게.

1. devices 테이블에 새로운 컬럼 'ai_recommendation_enabled' (boolean, default true)를 추가해줘
2. ALTER TABLE로 컬럼을 추가하고
3. 추가된 컬럼이 기존 데이터에 어떻게 반영되는지 보여줘 (기존 행은 null)
4. 새 컬럼에 기본값으로 업데이트해줘

Delta Lake에서 Schema Evolution이 어떻게 동작하는지 설명해줘.
```

---

## Step 7: Unity Catalog 탐색

### Claude에게 요청하기

```
Unity Catalog의 거버넌스 기능을 살펴볼게.

1. 현재 생성된 모든 테이블의 메타데이터를 보여줘 (information_schema 활용)
2. devices 테이블에 태그를 추가해줘: domain='smart_tv', sensitivity='internal'
3. 테이블 간의 관계를 설명해줘 (device_id를 통한 연결)
4. 각 테이블의 row count, 크기, 마지막 수정일을 조회해줘

Unity Catalog에서 데이터 거버넌스가 왜 중요한지,
특히 Smart TV OEM 같은 대기업에서 어떤 이점이 있는지 설명해줘.
```

---

## Step 8: 생성된 데이터 검증

### Claude에게 요청하기

```
지금까지 생성한 모든 데이터를 종합 검증해줘.

1. 각 테이블별 레코드 수, 컬럼 수, 용량
2. devices → viewing_logs → click_events → ad_impressions 간 device_id 참조 무결성 확인
3. 각 테이블의 NULL 값 비율
4. 날짜 범위가 올바른지 확인
5. 전체 데이터 요약 대시보드 형태로 정리

결과를 표 형태로 깔끔하게 보여줘.
```

---

## 학습 정리

이 모듈에서 학습한 내용:

| 개념 | 실습 내용 |
|------|-----------|
|**Lakehouse Architecture**| 카탈로그 > 스키마 구조로 Medallion (Bronze/Silver/Gold) 패턴 구성 |
|**Unity Catalog**| 3단계 네임스페이스, 메타데이터 관리, 태그, 거버넌스 |
|**Delta Lake**| ACID 트랜잭션, Time Travel, RESTORE, Schema Evolution |
|**가상 데이터 생성**| Faker + Spark로 현실적인 Smart TV 데이터 100만건+ 생성 |
|**AI Dev Kit 활용**| Claude에게 자연어로 요청 → MCP 도구가 Databricks에서 직접 실행 |

---

## 다음 단계

→ [Module 2: Data Engineering - 스마트TV 데이터 파이프라인](../02-data-engineering/README.md)
