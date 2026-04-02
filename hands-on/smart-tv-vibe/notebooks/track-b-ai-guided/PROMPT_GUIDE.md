# 노트북 생성용 Claude Code 프롬프트 가이드

> 각 노트북을 처음부터 만들고 싶다면, 아래 프롬프트를 Claude Code에 붙여넣기하세요.
> Claude가 AI Dev Kit의 MCP 도구와 스킬을 활용해서 노트북을 자동 생성합니다.

---

## 01. 카탈로그 & 스키마 설정

```
Databricks에 교육용 환경을 셋업하는 노트북을 만들어줘.

요구사항:
- 현재 로그인한 사용자 이름(current_user())에서 prefix를 추출해서 카탈로그 이름을 동적으로 생성
 예: your.name@company.com → simyung_yang_smarttv_training
- Medallion Architecture 기반으로 bronze, silver, gold 3개 스키마 생성
- 각 스키마에 COMMENT 추가
- 생성 후 확인 쿼리 포함

노트북 파일명: 01_setup_catalog_schema.py
워크스페이스 경로: /Workspace/Users/{내 이메일}/smarttv-training/

만들고 워크스페이스에 업로드해줘.
```

---

## 02. 가상 데이터 생성

```
Smart TV 시나리오의 가상 데이터를 생성하는 노트북을 만들어줘.

카탈로그: current_user() 기반 동적 생성 ({user_prefix}_smarttv_training)
스키마: bronze

생성할 테이블 4개:

1. bronze.devices (10,000건) - TV 디바이스 마스터
  - device_id (UUID), model_name (OLED65C4, OLED55B4, QNED85, NANO75, UHD50UR 등 10개 모델)
  - screen_size (43~86인치), region (Korea/US/EU/Japan/SEA 등 8개 지역)
  - country (KR/US/DE/JP 등 15개국), registered_at (2023~2025)
  - firmware_version (webOS 6.0~24.0), has_fasttv (80% true)
  - price_tier (premium/mid/entry), subscription_tier (free/basic/premium)

2. bronze.viewing_logs (500,000건) - 시청 로그
  - device_id (devices FK), user_profile_id (디바이스당 1~4명)
  - content_type (live_tv/vod/app/fasttv), channel_or_app (MBC/Netflix/YouTube 등)
  - genre (drama/entertainment/news 등), start_time (2025-01~03)
  - duration_minutes (로그정규분포, 평균 45분), completion_rate (0~1)
  - 시간대별 현실적 분포: 평일 저녁 집중(60%), 주말 분산, 새벽 최소(5%)

3. bronze.click_events (1,000,000건) - UI 이벤트/클릭 로그
  - event_type 11종 (app_launch/channel_change/search/banner_click/ad_click 등)
  - screen_name 7종 (home/fasttv/app_store/settings/search 등)
  - element_id (화면별 클릭 요소), session_id (power_on~off 세션)

4. bronze.ad_impressions (200,000건) - FastTV 광고 로그
  - advertiser 30개 (삼성전자/현대자동차/쿠팡/네이버 등 한국 기업)
  - ad_format 6종 (banner/video_pre_roll/native 등), 형식별 차등 CTR
  - placement 5종 (fasttv_home/channel_guide 등)
  - bid_price_usd, win_price_usd, was_clicked, was_converted

PySpark + random/numpy로 생성하고, 배치 처리로 메모리 효율적으로 만들어줘.
각 테이블 생성 후 통계 확인 셀과 전체 검증 셀도 포함해줘.

노트북 파일명: 02_generate_synthetic_data.py
워크스페이스에 업로드해줘.
```

---

## 03. Bronze → Silver → Gold 변환 (CTAS 수동)

```
Bronze 데이터를 Silver, Gold로 변환하는 노트북을 SQL CTAS 방식으로 만들어줘.

카탈로그: current_user() 기반 동적 생성
Silver 테이블은 _ctas suffix를 붙여줘 (나중에 SDP 결과와 비교하기 위해).

=== Silver 변환 (4개 테이블) ===

1. silver.devices_ctas ← bronze.devices
  - NULL device_id 제거, 미래 날짜 제거
  - model_name 대문자 통일
  - price_tier 파생 (OLED→premium, QNED/NANO→mid, UHD→entry)
  - device_age_days 파생

2. silver.viewing_logs_ctas ← bronze.viewing_logs JOIN silver.devices_ctas
  - duration 0이하 또는 480초과 제거, 날짜 범위 검증
  - viewing_date, viewing_hour, day_of_week, is_weekend, time_slot 파생
  - 디바이스 정보 JOIN (model_name, region, price_tier)

3. silver.click_events_ctas ← bronze.click_events JOIN silver.devices_ctas
  - event_timestamp 범위 검증
  - session_id 기반 세션 통계 (CTE): session_start, duration, event_count
  - 디바이스 정보 JOIN

4. silver.ad_impressions_ctas ← bronze.ad_impressions JOIN silver.devices_ctas
  - bid_price > 0 필터
  - was_clicked=true인데 click_timestamp NULL이면 false로 보정
  - impression_date, impression_hour, time_slot, time_to_click_seconds 파생

=== Gold 집계 (4개 테이블, suffix 없음) ===

1. gold.daily_viewing_summary - viewing_date/region/content_type/genre/time_slot 기준
  total_views, unique_devices, unique_users, total_minutes, avg_duration, p50/p90

2. gold.user_profiles - device_id + user_profile_id 기준
  시청 피처(favorite_genre, preferred_time_slot, weekend_ratio)
  클릭 피처(total_events, search_count, voice_command_count)
  광고 피처(ad_ctr, avg_time_to_click)
  ROW_NUMBER 윈도우 함수로 Top 1 장르/콘텐츠/시간대 계산

3. gold.ad_performance - 날짜/광고주/형식/지역 기준
  impressions, clicks, conversions, ctr, cvr, total_spend, cpc, rpm

4. gold.content_rankings - 날짜/채널/장르 기준
  daily_views, unique_viewers, total_minutes, RANK() 순위

각 변환 후 통계 확인 셀, 마지막에 전체 Bronze→Silver→Gold 건수 비교 요약 셀 포함.

노트북 파일명: 03_silver_gold_ctas.py
워크스페이스에 업로드해줘.
```

---

## 04. SDP 선언적 파이프라인

>** 중요:** 최신 SDP API(`from pyspark import pipelines as dp`)를 사용하세요.
> 이전 `import dlt` 방식은 레거시입니다.

```
03 노트북에서 CTAS로 수동 실행한 동일한 Bronze→Silver→Gold 변환을
Spark Declarative Pipeline (SDP)로 구현하는 노트북을 만들어줘.

중요: 최신 pyspark.pipelines API를 사용해줘:
- import: from pyspark import pipelines as dp
- 테이블: @dp.table()
- MV: @dp.materialized_view()
- 읽기: spark.read.table("table_name") (dlt.read() 사용하지 마)
- Expectations: @dp.expect_or_fail(), @dp.expect_or_drop()
- 이전 import dlt 방식은 레거시이므로 사용하지 마

이 노트북은 SDP 파이프라인 소스코드이므로, 직접 Run All이 아니라
Workflows > Pipelines에서 파이프라인으로 실행됨.

카탈로그: 파이프라인 설정의 source_catalog 파라미터로 받기 (spark.conf.get("source_catalog"))
Silver 테이블은 _sdp suffix, Gold 테이블도 _sdp suffix.

=== Silver (@dp.table + Expectations) ===

1. devices_sdp
  - @dp.expect_or_fail("valid_device_id", "device_id IS NOT NULL")
  - @dp.expect("valid_registration", "registered_at <= current_timestamp()")
  - 03과 동일한 변환 로직 (price_tier, device_age_days)

2. viewing_logs_sdp
  - @dp.expect_or_drop("valid_duration", "duration_minutes > 0 AND duration_minutes <= 480")
  - @dp.expect_or_drop("valid_date_range", "...")
  - spark.read.table("devices_sdp")로 의존성 자동 추적 (JOIN)

3. click_events_sdp
  - @dp.expect_or_fail("valid_timestamp", "event_timestamp IS NOT NULL")
  - 세션 통계 집계 후 JOIN

4. ad_impressions_sdp
  - @dp.expect_or_drop("valid_bid_price", "bid_price_usd > 0")
  - was_clicked 정합성 보정

=== Gold (@dp.materialized_view) ===

5. daily_viewing_summary_sdp - viewing_logs_sdp 기반 집계
6. ad_performance_sdp - ad_impressions_sdp 기반 집계
7. content_rankings_sdp - viewing_logs_sdp 기반 + RANK 윈도우

마지막에 파이프라인 설정 JSON 예시, DLT vs SDP API 비교표, CTAS vs SDP 비교표도 마크다운으로 포함해줘.

노트북 파일명: 04_sdp_pipeline.py
워크스페이스에 업로드해줘.
```

---

## 노트북별 Databricks 핵심 기능 설명

### 01. 카탈로그 & 스키마 설정에서 사용하는 기능

#### Unity Catalog — 통합 데이터 거버넌스
모든 데이터 자산(테이블, 뷰, 모델, 함수)을 **하나의 카탈로그** 에서 관리합니다.

- **3단계 네임스페이스**(`catalog.schema.table`): 조직 구조에 맞게 데이터를 계층적으로 정리
- **중앙집중 권한 관리**: `GRANT USE SCHEMA gold TO analysts` 한 줄로 접근 제어
- **자동 데이터 리니지**: 테이블 간 데이터 흐름을 자동 추적 — "이 Gold 테이블은 어떤 Bronze 데이터에서 왔는가?"
- **기존 Hive Metastore 대비 장점**: 워크스페이스 간 공유, 세밀한 권한(행/열 수준), 감사 로그 내장

#### Medallion Architecture — Bronze/Silver/Gold 패턴
데이터 품질을 단계적으로 높이는 업계 표준 아키텍처입니다.

- **Bronze**: 원본 그대로 보존 → 문제 발생 시 언제든 재처리 가능
- **Silver**: 정제/검증 → 비즈니스 로직 적용 전 신뢰할 수 있는 데이터
- **Gold**: 비즈니스 관점 집계 → 대시보드, ML 모델이 바로 사용
- **핵심 가치**: 각 레이어가 독립적이라 한 곳이 바뀌어도 전체를 재구축할 필요 없음

---

### 02. 가상 데이터 생성에서 사용하는 기능

#### Delta Lake — 신뢰할 수 있는 데이터 저장소
Databricks의 모든 테이블은 기본적으로 Delta Lake 형식으로 저장됩니다.

- **ACID 트랜잭션**: 100만건 INSERT 중 실패해도 데이터가 깨지지 않음 (전부 성공 or 전부 롤백)
- **Time Travel**: `SELECT * FROM table VERSION AS OF 3` — 과거 시점 데이터 조회 및 복원
- **Schema Enforcement**: 잘못된 타입의 데이터가 들어오면 자동 차단
- **기존 Parquet/CSV 대비 장점**: 트랜잭션 보장, 업데이트/삭제 가능, 자동 최적화

#### PySpark — 대규모 분산 처리
단일 머신에서 처리 불가능한 대용량 데이터를 **클러스터 전체에 분산** 하여 처리합니다.

- **자동 병렬 처리**: 100만건 데이터를 여러 노드가 동시에 처리
- **Lazy Evaluation**: 실행 계획을 먼저 최적화한 후 한번에 실행 — 불필요한 연산 제거
- **DataFrame API**: SQL과 유사한 직관적 문법 (`df.filter().groupBy().agg()`)
- **기존 Pandas 대비 장점**: 메모리 한계 없음, TB 단위 데이터도 처리 가능

#### Serverless Compute — 인프라 관리 불필요
클러스터를 직접 생성/관리할 필요 없이, 노트북 실행 시 자동으로 컴퓨트가 할당됩니다.

- **즉시 시작**: 클러스터 대기 시간 없이 바로 실행
- **자동 스케일링**: 작업량에 따라 리소스 자동 조절
- **사용한 만큼 과금**: 유휴 비용 없음

---

### 03. CTAS 수동 변환에서 사용하는 기능

#### CREATE OR REPLACE TABLE AS SELECT (CTAS) — SQL 기반 ETL
가장 직관적인 데이터 변환 방식입니다. SQL만 알면 ETL 파이프라인을 구축할 수 있습니다.

- **한 문장으로 변환 완료**: SELECT로 변환 로직을 정의하면 결과가 바로 테이블로 저장
- **익숙한 SQL 문법**: JOIN, GROUP BY, 윈도우 함수 등 표준 SQL 그대로 사용
- **멱등성**: OR REPLACE로 재실행해도 동일한 결과 보장
- **한계**: 매번 전체 재계산, 증분 처리 불가, 의존성 수동 관리 → 이를 SDP가 해결

#### 윈도우 함수 (RANK, ROW_NUMBER) — 고급 분석
GROUP BY로는 불가능한 **행 단위 순위/비교** 분석을 제공합니다.

- `RANK() OVER (PARTITION BY date ORDER BY viewers DESC)`: 일별 콘텐츠 순위
- `ROW_NUMBER()`: 사용자별 선호 장르 Top 1 추출
- **기존 서브쿼리 대비 장점**: 성능 우수, 코드 간결, 여러 윈도우 동시 적용 가능

#### CTE (Common Table Expression) — 복잡한 쿼리 구조화
`WITH` 절로 복잡한 쿼리를 **이름 붙인 단계** 로 분리합니다.

- 사용자 프로필 생성 시: 시청 피처 CTE + 클릭 피처 CTE + 광고 피처 CTE → 최종 JOIN
- **가독성**: 300줄 쿼리를 논리적 블록으로 분리
- **재사용**: 같은 CTE를 여러 번 참조 가능

---

### 04. SDP 선언적 파이프라인에서 사용하는 기능

#### Spark Declarative Pipelines (SDP) — 선언적 데이터 파이프라인
"무엇을 만들 것인가"만 선언하면,** 어떻게 실행할지는 엔진이 자동 결정** 합니다.

- **자동 의존성 해결**: `spark.read.table("devices_sdp")`만 쓰면 devices 먼저 실행됨을 자동 감지
- **증분 처리**: 새로 추가된 데이터만 처리 — 전체 재계산 대비 10~100배 빠름
- **자동 오류 복구**: 실패 시 체크포인트에서 재시작 (처음부터 다시 하지 않음)
- **기존 노트북 ETL 대비 장점**: 스케줄링/모니터링/재처리가 모두 내장

#### @dp.table() vs @dp.materialized_view() — 두 가지 테이블 유형

| | `@dp.table()` | `@dp.materialized_view()` |
|---|---|---|
| **용도** | 증분 데이터 처리 (Silver) | 전체 재계산 집계 (Gold) |
| **처리 방식** | 새 데이터만 추가 처리 | 매 실행마다 전체 재계산 |
| **적합한 경우** | 로그 데이터, 이벤트 스트림 | 일별 요약, 랭킹, KPI |
| **기존 용어** | Streaming Table | Materialized View |

#### Expectations — 내장 데이터 품질 검증
변환 로직 **안에** 데이터 품질 규칙을 선언합니다. 별도 검증 코드가 필요 없습니다.

- `@dp.expect_or_fail("valid_id", "device_id IS NOT NULL")`: 위반 시 파이프라인 중단 — 치명적 오류용
- `@dp.expect_or_drop("valid_duration", "duration > 0")`: 위반 행만 제거 — 이상치 필터링용
- `@dp.expect("soft_check", "price > 0")`: 위반 기록만 남기고 계속 진행 — 모니터링용
- **파이프라인 UI에서 시각화**: 몇 건이 통과/실패했는지 대시보드로 확인 가능

#### 최신 API: pyspark.pipelines (dp) vs 레거시 dlt

```python
# ❌ 레거시 (더 이상 새 프로젝트에 권장하지 않음)
import dlt
@dlt.table()
def my_table():
  return dlt.read("source")

# ✅ 최신 (2025~ 권장)
from pyspark import pipelines as dp
@dp.table()
def my_table():
  return spark.read.table("source")
```

- **읽기 방식 변경**: `dlt.read()` → `spark.read.table()` (표준 Spark API 사용)
- **MV 전용 데코레이터**: `@dlt.table()` 하나로 통합 → `@dp.table()` + `@dp.materialized_view()` 분리
- **핵심 이점**: 표준 Spark 문법과 통일되어, SDP 밖에서도 동일한 코드를 재사용 가능

---

## 05. AI/BI Dashboard 심화 Gold 테이블

```
대시보드에서 다양한 차트를 보여주기 위한 심화 Gold 테이블 5개를 추가로 만들어줘.
기존 Gold 테이블을 기반으로.

카탈로그: current_user() 기반 동적 생성

1. gold.weekly_kpi_trends - 주간 KPI 추이 (Counter, Line 차트용)
  - week_start, total_views, unique_users, avg_daily_minutes
  - total_ad_revenue, avg_ctr, wow_views_change_pct, wow_revenue_change_pct

2. gold.user_segments - 사용자 세그먼트 (Pie, Bar 차트용)
  - segment_name: heavy_viewer(120분+)/moderate(60~120)/light(15~60)/dormant(15미만)
  - user_count, avg_viewing_minutes, avg_ad_ctr, top_genre

3. gold.fasttv_revenue_analysis - FastTV 수익 심화 (Stacked Bar, Scatter 차트용)
  - date, advertiser, ad_format, region, impressions, clicks, revenue_usd, ecpm

4. gold.content_engagement_funnel - 소비 퍼널 (Funnel 차트용)
  - content_type, funnel_stage(impression→click→view_start→view_complete)
  - user_count, conversion_rate

5. gold.hourly_heatmap - 시간대 히트맵 (Heatmap 차트용)
  - day_of_week(Mon~Sun), hour(0~23), avg_viewers, avg_duration, peak_content_type

노트북 파일명: 05_dashboard_gold_tables.py
워크스페이스에 업로드해줘.
```

---

## 06. AI/BI Dashboard 생성

```
위에서 만든 Gold 테이블들로 AI/BI 대시보드를 만들어줘.
가능한 한 다양한 차트 유형을 활용해서 "이런 것도 가능하다"를 보여주는게 목적이야.

대시보드 이름: SmartTV Analytics Dashboard

=== Page 1: Executive Overview ===
- Counter 차트 4개: 총 시청수/순 사용자/광고수익/CTR (WoW 변화율 포함)
- Line 차트: 주간 시청량 추이
- Pie 차트: 사용자 세그먼트 분포
- Stacked Area 차트: 콘텐츠 유형별 시청 추이

=== Page 2: Viewing Analytics ===
- Heatmap: 시간대별(hour×day_of_week) 시청 히트맵
- Bar (Grouped): Top 10 인기 콘텐츠 (genre별 색상)
- Line: 지역별 시청량 추이
- Donut: 장르별 시청 비율

=== Page 3: FastTV Ad Revenue ===
- Line: 일별 광고 수익 추이 + 7일 이동평균
- Stacked Bar: 광고 형식별 수익 구성
- Scatter: 광고주별 노출 vs CTR (버블 크기=수익)
- Bar: Top 10 광고주 수익 랭킹

=== Page 4: Funnel & Segments ===
- Funnel: impression→click→view_start→view_complete
- Bubble: 세그먼트별 참여도(x) vs 광고반응(y) vs 크기(user_count)

각 차트의 SQL 쿼리를 먼저 검증한 후, 대시보드를 생성하고 publish해줘.
```

---

## 07. AI/BI Genie Space 생성 + 15개 질문 테스트

```
AI/BI Genie Space를 생성하고 15개 비즈니스 질문으로 테스트해줘.

Genie Space 이름: SmartTV Data Explorer

연결 테이블 8개:
- gold.daily_viewing_summary, user_profiles, ad_performance, content_rankings
- gold.weekly_kpi_trends, user_segments, fasttv_revenue_analysis, hourly_heatmap

Instructions:
- 한국어 질문을 이해하고 SQL 변환
- 날짜 필터 없으면 최근 30일 기본 적용
- 금액 USD, 비율 % 표시

Sample Questions 15개:

시청 분석:
1. "이번 달 가장 인기 있는 콘텐츠 Top 10은?"
2. "주말과 평일의 시청 패턴 차이를 보여줘"
3. "Korea 지역에서 프라임타임에 가장 많이 보는 장르는?"
4. "시청 완료율이 가장 높은 콘텐츠 유형은?"

광고 분석:
5. "FastTV 광고 중 CTR이 가장 높은 광고 형식은?"
6. "광고 수익이 가장 높은 시간대는?"
7. "쿠팡 광고의 지난 달 성과 요약해줘"
8. "native 광고와 banner 광고의 전환율 차이는?"

사용자 분석:
9. "premium 티어와 entry 티어 사용자의 시청 행동 차이는?"
10. "heavy viewer 세그먼트의 특성을 알려줘"
11. "음성 명령 사용률이 가장 높은 사용자 그룹은?"
12. "시청 시간이 가장 많은 지역 Top 5와 각 지역의 인기 장르는?"

심화:
13. "광고 CTR이 높은 사용자는 어떤 콘텐츠를 주로 시청하나?"
14. "OLED TV와 일반 TV 사용자의 FastTV 광고 반응 차이는?"
15. "가장 빠르게 성장하는 콘텐츠/채널은?"

Genie Space 생성 후 각 질문의 SQL과 결과를 보여줘.
```

---

## 08. Structured Streaming (Volume → Auto Loader)

```
UC Volume에 주기적으로 이벤트를 생성하고, Auto Loader로 실시간 수집하는 노트북을 만들어줘.

=== Volume & Landing Zone ===
- Volume: bronze.landing_zone (MANAGED)
- 디렉토리: viewing_events/, click_events/, ad_events/

=== 이벤트 생성기 ===
배치당: viewing 100건, click 200건, ad 50건
형식: JSON Lines (한 줄 하나의 JSON)
기존 bronze.devices에서 device_id 참조

=== Auto Loader 수집 ===
spark.readStream.format("cloudFiles")로 각 이벤트 타입 수집
Bronze 테이블: live_viewing_events, live_click_events, live_ad_events
_ingested_at, _source_file 메타 컬럼 추가

=== 테스트 ===
- 1배치 생성 → 수집 확인
- 3배치 추가 → 자동 수집 확인
- 각 테이블 건수 확인

노트북 파일명: 07_structured_streaming.py
워크스페이스에 업로드해줘.
```

---

## 09. ML 개인화 추천 모델

```
Gold 테이블 기반으로 ALS 협업 필터링 추천 모델을 학습하는 노트북을 만들어줘.

=== 콘텐츠 메타데이터 ===
gold.content_metadata 500건 생성 (한국어 제목, 장르, description)

=== 상호작용 매트릭스 ===
viewing_logs에서 (user, content) 조합 집계 → interaction_score 계산
user_idx, content_idx 정수 인덱싱

=== ALS 학습 (MLflow) ===
실험: /smarttv_demo/content_recommendation
3가지 설정 비교:
- rank=10/maxIter=10/regParam=0.01
- rank=50/maxIter=15/regParam=0.01
- rank=30/maxIter=15/regParam=0.1
RMSE, MAE 메트릭 비교

=== 모델 등록 ===
최적 모델을 Unity Catalog에 등록: gold.content_recommender
Champion alias 설정

=== 추천 생성 ===
전체 사용자 Top 10 추천 → gold.user_recommendations 저장
샘플 3명의 추천 결과 상세 확인

노트북 파일명: 08_ml_recommendation.py
워크스페이스에 업로드해줘.
```

---

## 10. Lakebase & Apps

```
Lakebase(PostgreSQL 호환 OLTP DB)와 Databricks Apps를 구성해줘.

=== Lakebase ===
인스턴스: smarttv-demo-lakebase
테이블 4개:
1. user_preferences (설정: 언어, 광고개인화, 자녀보호 등)
2. recommendation_cache (추천 결과 캐시: user_id, type, JSONB, expires)
3. user_feedback (피드백: like/dislike/not_interested)
4. watch_history_cache (시청이력 캐시: progress, last_watched)

=== 추천 캐싱 파이프라인 ===
gold.user_recommendations → Lakebase recommendation_cache UPSERT

=== Databricks App (챗봇) ===
앱이름: smarttv-demo-chatbot
Gradio 프레임워크
Supervisor Agent 엔드포인트 호출
샘플 질문 사이드바

노트북 파일명: 09_lakebase_apps.py
워크스페이스에 업로드해줘.
```

---

## 참고: 프롬프트 작성 팁

### 좋은 프롬프트의 공통 패턴

1. **목적을 먼저 명시**- "~하는 노트북을 만들어줘"
2. **동적 prefix 요구**- "current_user() 기반 카탈로그 이름"
3. **테이블/컬럼을 구체적으로**- 이름, 타입, 생성 규칙까지
4. **변환 로직을 명시**- WHERE 조건, 파생 컬럼 공식
5. **검증 셀 포함 요청**- "통계 확인", "건수 비교"
6. **업로드까지 요청**- "워크스페이스에 업로드해줘"

### 프롬프트에서 자유롭게 변경 가능한 부분

- 테이블 건수 (10K → 1K로 줄여서 빠르게 테스트)
- 광고주 이름 (한국 기업 → 글로벌 기업)
- 도메인 시나리오 (스마트TV → IoT센서, 이커머스 등)
- suffix 규칙 (_ctas, _sdp → _manual, _auto 등)
