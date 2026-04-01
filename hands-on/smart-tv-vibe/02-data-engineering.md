# Module 2: Data Engineering - 스마트TV 데이터 파이프라인

## 이 가이드 사용 방법

>**이 교육 자료는 Claude Code (또는 Cursor)와 함께 사용합니다.**>
> 1. 터미널에서 프로젝트 디렉토리로 이동: `cd ~/smarttv-training`
> 2. Claude Code 실행: `claude`
> 3. 각 Step의 "**Claude에게 요청하기**" 박스 내용을 복사하여 Claude에게 붙여넣기
> 4. Claude가 코드를 생성하고 Databricks에서 실행합니다
> 5. 결과를 확인하고 궁금한 점은 바로 질문하세요
>
>**Tip:** 각 Step을 순서대로 진행하세요. 이전 Step의 결과가 다음 Step의 입력이 됩니다.

---

## 학습 목표

- Bronze → Silver → Gold Medallion 파이프라인 구축
- Spark Declarative Pipelines (DLT) 활용법 이해
- 데이터 품질 검증 (Expectations) 적용
- 스마트TV 로그 데이터를 분석 가능한 형태로 변환
- Databricks Jobs로 파이프라인 스케줄링

---

## 파이프라인 아키텍처

```
Bronze (원본 로그)        Silver (정제)          Gold (분석/서빙)
┌───────────────┐       ┌──────────────────┐      ┌──────────────────┐
│ devices    │       │ silver_devices  │      │ daily_viewing   │
│ viewing_logs  │ ──Clean──→ │ silver_viewing  │ ──Agg──→ │ _summary     │
│ click_events  │  Filter  │ silver_clicks   │  Join   │ user_profiles   │
│ ad_impressions │  Dedup   │ silver_ads    │  Enrich  │ ad_performance  │
└───────────────┘       └──────────────────┘      │ content_rankings │
                               └──────────────────┘
```

---

## Step 1: Bronze → Silver 변환 - 디바이스 데이터 정제

### Claude에게 요청하기

```
Bronze 디바이스 데이터를 Silver로 정제하는 파이프라인을 만들어줘.

소스: {catalog}.bronze.devices
타겟: {catalog}.silver.devices_clean

변환 규칙:
1. device_id가 NULL인 행 제거
2. registered_at이 미래 날짜인 행 제거
3. model_name을 대문자로 통일
4. region과 country 매핑 검증 (Korea-KR, US-US, EU-DE 등)
5. 디바이스 연식 컬럼 추가: device_age_days = current_date - registered_at
6. 가격대 컬럼 추가: model_name 기준으로 premium/mid/entry 분류
  - OLED* → premium
  - QNED*, NANO* → mid
  - UHD* → entry

SQL로 CREATE OR REPLACE TABLE 문을 작성하고 실행해줘.
실행 후 원본 대비 정제 결과 통계를 보여줘 (제거된 행 수, 각 분류별 분포).
```

---

## Step 2: Bronze → Silver 변환 - 시청 로그 정제

### Claude에게 요청하기

```
시청 로그를 Silver로 정제해줘.

소스: {catalog}.bronze.viewing_logs
타겟: {catalog}.silver.viewing_logs_clean

변환 규칙:
1. duration_minutes <= 0 또는 > 480 (8시간) 인 비정상 레코드 제거
2. start_time이 데이터 범위(2025-01-01 ~ 2025-03-01) 밖인 행 제거
3. 중복 log_id 제거 (가장 최신 것 유지)
4. 파생 컬럼 추가:
  - viewing_date: start_time에서 날짜 추출
  - viewing_hour: 시간대 (0~23)
  - day_of_week: 요일 (Monday~Sunday)
  - is_weekend: 주말 여부
  - time_slot: 시간대 분류
   - morning (6~12시)
   - afternoon (12~18시)
   - prime_time (18~23시)
   - late_night (23~6시)
  - end_time: start_time + duration_minutes
5. devices_clean과 JOIN하여 model_name, region, price_tier 추가

실행 후:
- 원본 대비 제거된 레코드 수
- 시간대(time_slot)별 시청 분포
- 콘텐츠 유형별 평균 시청 시간
을 보여줘.
```

---

## Step 3: Bronze → Silver 변환 - 클릭 이벤트 & 광고 로그

### Claude에게 요청하기

```
클릭 이벤트와 광고 로그도 Silver로 정제해줘. 두 테이블을 한번에 처리해줘.

=== 클릭 이벤트 ===
소스: {catalog}.bronze.click_events
타겟: {catalog}.silver.click_events_clean

변환:
1. event_timestamp 범위 검증
2. session_id 기반 세션 정보 추가:
  - session_start_time: 세션 내 첫 이벤트 시간
  - session_duration_minutes: 세션 지속 시간
  - events_in_session: 세션 내 이벤트 수
3. 이전 이벤트와의 시간 간격: time_since_last_event_seconds
4. devices_clean JOIN으로 디바이스 정보 추가

=== 광고 로그 ===
소스: {catalog}.bronze.ad_impressions
타겟: {catalog}.silver.ad_impressions_clean

변환:
1. bid_price <= 0 인 비정상 레코드 제거
2. was_clicked=true인데 click_timestamp이 NULL인 데이터 정합성 체크/수정
3. 파생 컬럼:
  - impression_date: 노출 날짜
  - impression_hour: 노출 시간대
  - time_to_click_seconds: 노출 → 클릭 소요 시간
  - cost_efficiency: win_price / (1 if clicked else 0.001)
4. devices_clean JOIN으로 디바이스 정보 추가

두 테이블 모두 실행 후 요약 통계를 보여줘.
```

---

## Step 4: Silver → Gold 집계 - 일별 시청 요약

### Claude에게 요청하기

```
Silver 데이터를 Gold로 집계해줘. 일별 시청 요약 테이블부터 만들자.

타겟: {catalog}.gold.daily_viewing_summary

집계 기준: viewing_date, region, content_type, genre, time_slot

집계 컬럼:
- total_views: 총 시청 수
- unique_devices: 순 디바이스 수
- unique_users: 순 사용자 수
- total_minutes: 총 시청 시간(분)
- avg_duration_minutes: 평균 시청 시간
- avg_completion_rate: 평균 시청 완료율
- p50_duration: 시청 시간 중앙값
- p90_duration: 시청 시간 90 퍼센타일

실행 후:
- 날짜별 총 시청량 추이
- region별 인기 콘텐츠 유형 Top 3
- prime_time vs late_night 시청 패턴 비교
를 보여줘.
```

---

## Step 5: Silver → Gold 집계 - 사용자 프로필

### Claude에게 요청하기

```
개인화 추천을 위한 사용자 프로필 테이블을 만들어줘.

타겟: {catalog}.gold.user_profiles

device_id + user_profile_id 기준으로 아래 피처를 집계:

=== 시청 행동 피처 ===
- total_viewing_days: 총 시청 일수
- total_viewing_minutes: 총 시청 시간
- avg_daily_viewing_minutes: 일평균 시청 시간
- favorite_genre: 가장 많이 본 장르 (Top 1)
- top3_genres: 상위 3개 장르 (배열)
- favorite_content_type: 선호 콘텐츠 유형
- preferred_time_slot: 주로 시청하는 시간대
- weekend_ratio: 주말 시청 비율

=== 클릭 행동 피처 ===
- total_click_events: 총 클릭 이벤트 수
- avg_session_duration: 평균 세션 시간
- most_visited_screen: 가장 많이 방문한 화면
- search_frequency: 검색 빈도
- voice_command_usage: 음성 명령 사용 빈도

=== 광고 반응 피처 ===
- total_ad_impressions: 총 광고 노출 수
- total_ad_clicks: 총 광고 클릭 수
- ad_ctr: 광고 클릭률
- preferred_ad_category: 선호 광고 카테고리
- avg_time_to_click: 평균 클릭 소요 시간

=== 디바이스 정보 ===
- model_name, region, price_tier, has_fasttv

전체 사용자 수와 주요 세그먼트별 분포를 보여줘.
```

---

## Step 6: Silver → Gold 집계 - 광고 성과 리포트

### Claude에게 요청하기

```
FastTV 광고 성과 분석 테이블을 만들어줘.

타겟: {catalog}.gold.ad_performance

집계 기준: impression_date, advertiser, ad_category, ad_format, placement, region

집계 컬럼:
- impressions: 총 노출 수
- clicks: 총 클릭 수
- conversions: 총 전환 수
- ctr: 클릭률 (clicks/impressions * 100)
- cvr: 전환률 (conversions/clicks * 100)
- total_spend_usd: 총 광고비
- cost_per_click_usd: CPC
- cost_per_conversion_usd: CPA
- revenue_per_mille_usd: RPM (1000 노출당 수익)

실행 후 다음 인사이트를 보여줘:
1. 광고주별 총 지출 및 CTR 랭킹
2. 광고 형식별 성과 비교 (CTR, CVR, CPC)
3. 시간대별 광고 효율 (prime_time vs 기타)
4. 지역별 광고 수익 비교
```

---

## Step 7: Silver → Gold 집계 - 콘텐츠 인기도 랭킹

### Claude에게 요청하기

```
콘텐츠 인기도 랭킹 테이블을 만들어줘.

타겟: {catalog}.gold.content_rankings

viewing_date, channel_or_app, genre 기준으로:

- daily_views: 일별 시청 수
- daily_unique_viewers: 일별 순 시청자 수
- daily_total_minutes: 일별 총 시청 시간
- avg_completion_rate: 평균 완료율
- daily_rank: 일별 순위 (시청자 수 기준 RANK)
- weekly_trend: 전주 대비 시청자 증감률
- genre_rank: 장르 내 순위

실행 후:
1. 전체 Top 10 인기 콘텐츠/채널
2. 장르별 Top 3
3. 주간 성장률이 가장 높은 콘텐츠 5개
를 보여줘.
```

---

## Step 8: Spark Declarative Pipeline (DLT) 구성

### Claude에게 요청하기

```
지금까지 수동으로 실행한 Bronze → Silver → Gold 변환을
Spark Declarative Pipeline (DLT)로 자동화해줘.

파이프라인 이름: {catalog}_pipeline

포함할 테이블:
1. Streaming Table: silver_devices (Bronze devices → 정제)
2. Streaming Table: silver_viewing_logs (Bronze viewing_logs → 정제)
3. Streaming Table: silver_click_events (Bronze click_events → 정제)
4. Streaming Table: silver_ad_impressions (Bronze ad_impressions → 정제)
5. Materialized View: gold_daily_viewing_summary (Silver → 일별 집계)
6. Materialized View: gold_user_profiles (Silver → 사용자 프로필)
7. Materialized View: gold_ad_performance (Silver → 광고 성과)
8. Materialized View: gold_content_rankings (Silver → 콘텐츠 랭킹)

데이터 품질 Expectations 추가:
- devices: device_id IS NOT NULL (expect or fail)
- viewing_logs: duration_minutes > 0 AND duration_minutes <= 480 (expect or drop)
- ad_impressions: bid_price > 0 (expect or drop)
- click_events: event_timestamp IS NOT NULL (expect or fail)

파이프라인 설정:
- target catalog: {catalog}
- target schema: pipeline_output
- development mode: true (교육용)
- serverless: true

파이프라인 코드(SQL)와 설정을 생성하고,
파이프라인을 생성해줘. DLT의 핵심 개념도 설명해줘.
```

### 핵심 개념: Spark Declarative Pipelines

```
┌─────────────────────────────────────────────────┐
│       DLT Pipeline            │
│                         │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│ │Streaming│  │Streaming│  │Material.│   │
│ │ Table  │───→│ Table  │───→│ View  │   │
│ │(Bronze) │  │(Silver) │  │ (Gold) │   │
│ └─────────┘  └─────────┘  └─────────┘   │
│    │       │       │      │
│ ┌────┴────┐  ┌────┴────┐  ┌────┴────┐   │
│ │Expect: │  │Expect: │  │ Auto  │   │
│ │NOT NULL │  │Range  │  │ Refresh │   │
│ └─────────┘  └─────────┘  └─────────┘   │
│                         │
│ ✅ 자동 의존성 해결 ✅ 증분 처리        │
│ ✅ 데이터 품질 관리 ✅ 자동 복구        │
└─────────────────────────────────────────────────┘
```

---

## Step 9: Databricks Jobs로 스케줄링

### Claude에게 요청하기

```
DLT 파이프라인을 Databricks Job으로 스케줄링해줘.

Job 이름: {catalog}_daily_job

구성:
- Task 1: "refresh_pipeline" - DLT 파이프라인 실행 (위에서 만든 파이프라인)
- Task 2: "validate_data" - 데이터 품질 검증 SQL 실행 (Task 1 이후)
 - gold 테이블들의 레코드 수 체크
 - 최신 날짜 데이터 존재 여부 확인

스케줄: 매일 새벽 2시 (KST) - Cron: 0 17 * * * (UTC)

알림 설정:
- 실패 시 이메일 알림

Job을 생성하고, 구조를 설명해줘.
(실제 실행은 하지 않아도 됨 - 구조만 확인)
```

---

## Step 10: 파이프라인 검증 & 모니터링

### Claude에게 요청하기

```
전체 파이프라인의 결과를 종합 검증해줘.

1. Gold 테이블 데이터 품질 체크:
  - 각 테이블별 레코드 수
  - NULL 값 비율이 5% 이상인 컬럼 찾기
  - 날짜 범위 정합성

2. Bronze → Silver → Gold 간 데이터 흐름 검증:
  - Bronze 원본 건수 vs Silver 정제 건수 vs Gold 집계 건수
  - 데이터 손실률 계산

3. 비즈니스 로직 검증:
  - user_profiles의 총 사용자 수가 devices의 디바이스 수와 합리적으로 연관되는지
  - ad_performance의 총 impressions가 bronze 원본과 일치하는지
  - CTR이 0~100% 범위 내인지

결과를 요약 리포트 형태로 보여줘.
```

---

## 학습 정리

| 개념 | 실습 내용 |
|------|-----------|
|**Medallion Architecture**| Bronze(원본) → Silver(정제) → Gold(집계) 3단계 파이프라인 |
|** 데이터 정제**| NULL 처리, 중복 제거, 타입 변환, 범위 검증 |
|** 피처 엔지니어링**| 시간대 분류, 사용자 프로필, 세션 분석 |
|**Spark Declarative Pipelines**| Streaming Table, Materialized View, Expectations |
|**Databricks Jobs**| 멀티태스크 DAG, Cron 스케줄링, 알림 설정 |
|** 데이터 품질 관리**| Expectations, 정합성 검증, 모니터링 |

---

## 비즈니스 가치

이 파이프라인을 통해 Smart TV는:

1.** 시청 패턴 분석**→ 콘텐츠 편성 최적화
2.** 사용자 프로필**→ 개인화 추천 엔진의 입력 피처
3.** 광고 성과 분석**→ FastTV 광고 수익 최적화, 광고주 리포팅
4.** 콘텐츠 랭킹**→ 인기 콘텐츠 기반 큐레이션

---

## 다음 단계

→ [Module 3: Generative AI - 개인화 추천 & Agent Bricks](../03-genai/README.md)
