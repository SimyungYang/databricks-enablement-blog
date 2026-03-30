# Databricks notebook source
# MAGIC %md
# MAGIC # 03. Bronze → Silver → Gold 변환 (CTAS 수동 방식)
# MAGIC
# MAGIC SQL `CREATE OR REPLACE TABLE AS SELECT` 문으로 단계별 변환을 수행합니다.
# MAGIC 각 변환이 **무엇을 하는지** 이해하는 데 집중하세요.
# MAGIC
# MAGIC >**참고:** 이 노트북에서 생성하는 Silver 테이블은 `_ctas` suffix가 붙습니다.
# MAGIC > 다음 노트북 `04_sdp_pipeline`에서 동일한 변환을 SDP(DLT)로 수행하며 `_sdp` suffix로 생성합니다.
# MAGIC > 두 결과를 비교해볼 수 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 공통 설정

# COMMAND ----------

# 현재 사용자 이메일에서 prefix 추출
username = spark.sql("SELECT current_user()").collect()[0][0]
user_prefix = username.split("@")[0].replace(".", "_").replace("-", "_")
CATALOG = f"{user_prefix}_smarttv_training"

spark.sql(f"USE CATALOG {CATALOG}")
print(f"👤 사용자: {username}")
print(f"✅ 카탈로그: {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 배경지식: Medallion Architecture (메달리온 아키텍처)
# MAGIC
# MAGIC ### Medallion Architecture란?
# MAGIC
# MAGIC Databricks가 권장하는 **데이터 레이크하우스의 표준 설계 패턴**입니다.
# MAGIC 원본 데이터를 3단계로 점진적으로 정제하여, 최종적으로 비즈니스에서 바로 사용할 수 있는 형태로 만듭니다.
# MAGIC
# MAGIC ### 왜 3단계로 나누는가?
# MAGIC
# MAGIC 데이터를 한번에 최종 형태로 변환하면 다음 문제가 발생합니다:
# MAGIC - **디버깅 불가**: 변환 중간에 문제가 생기면 원인을 찾기 어려움
# MAGIC - **재처리 비용**: 원본이 없으면 전체를 처음부터 다시 해야 함
# MAGIC - **유연성 부족**: 새로운 분석 요구가 생기면 원본부터 다시 처리해야 함
# MAGIC
# MAGIC 3단계로 나누면:
# MAGIC - **Bronze에 원본 보관** → 언제든 재처리 가능
# MAGIC - **Silver에서 정제** → 여러 Gold 테이블의 공통 소스
# MAGIC - **Gold에서 목적별 집계** → 대시보드, ML, 리포트 각각의 요구에 맞춤
# MAGIC
# MAGIC ### 각 레이어의 역할
# MAGIC
# MAGIC | 레이어 | 역할 | 데이터 특성 | 사용자 |
# MAGIC |--------|------|------------|--------|
# MAGIC | **Bronze** | 원본 보존 | 가공 없이 그대로 저장, NULL/중복 포함 | 데이터 엔지니어 |
# MAGIC | **Silver** | 정제/변환 | NULL 제거, 타입 통일, 파생 컬럼, JOIN | 데이터 분석가, ML 엔지니어 |
# MAGIC | **Gold** | 비즈니스 서빙 | 집계, KPI, 사용자 프로필, 랭킹 | 경영진, 대시보드, ML 모델 |
# MAGIC
# MAGIC ### 이 노트북에서의 적용
# MAGIC
# MAGIC ```
# MAGIC Bronze (원본 4개 테이블)          Silver (정제 4개)              Gold (집계 9개)
# MAGIC ┌─────────────────┐         ┌──────────────────┐         ┌──────────────────┐
# MAGIC │ devices         │ ──정제──→ │ devices_ctas     │         │ daily_viewing    │
# MAGIC │ viewing_logs    │ ──정제──→ │ viewing_logs_ctas│ ──집계──→ │ user_profiles    │
# MAGIC │ click_events    │ ──정제──→ │ click_events_ctas│ ──집계──→ │ ad_performance   │
# MAGIC │ ad_impressions  │ ──정제──→ │ ad_impressions   │         │ content_rankings │
# MAGIC └─────────────────┘         └──────────────────┘         │ + 심화 5개       │
# MAGIC                                                           └──────────────────┘
# MAGIC ```
# MAGIC
# MAGIC 이제 아래에서 실제로 Bronze → Silver → Gold 변환을 수행합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 1: Bronze → Silver 변환
# MAGIC
# MAGIC Silver 레이어에서는 원본 데이터를 **정제(Cleansing)** 합니다:
# MAGIC
# MAGIC - NULL / 이상치 제거
# MAGIC - 데이터 타입 통일
# MAGIC - 파생 컬럼 추가
# MAGIC - 참조 테이블 JOIN

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1-1. 디바이스 정제 (silver.devices_ctas)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE silver.devices_ctas AS
# MAGIC SELECT
# MAGIC  device_id,
# MAGIC  UPPER(model_name) AS model_name,
# MAGIC  screen_size,
# MAGIC  region,
# MAGIC  country,
# MAGIC  registered_at,
# MAGIC  firmware_version,
# MAGIC  has_fasttv,
# MAGIC  -- 가격대 분류
# MAGIC  CASE
# MAGIC   WHEN model_name LIKE 'OLED%' THEN 'premium'
# MAGIC   WHEN model_name LIKE 'QNED%' OR model_name LIKE 'NANO%' THEN 'mid'
# MAGIC   WHEN model_name LIKE 'UHD%' THEN 'entry'
# MAGIC   ELSE 'unknown'
# MAGIC  END AS price_tier,
# MAGIC  subscription_tier,
# MAGIC  -- 디바이스 연식 (일수)
# MAGIC  DATEDIFF(current_date(), registered_at) AS device_age_days
# MAGIC FROM bronze.devices
# MAGIC WHERE device_id IS NOT NULL
# MAGIC  AND registered_at <= current_timestamp();

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 정제 결과 확인
# MAGIC SELECT
# MAGIC  '원본 (bronze)' AS layer,
# MAGIC  COUNT(*) AS row_count
# MAGIC FROM bronze.devices
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC  '정제 (silver_ctas)' AS layer,
# MAGIC  COUNT(*) AS row_count
# MAGIC FROM silver.devices_ctas;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1-2. 시청 로그 정제 (silver.viewing_logs_ctas)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE silver.viewing_logs_ctas AS
# MAGIC SELECT
# MAGIC  v.log_id,
# MAGIC  v.device_id,
# MAGIC  v.user_profile_id,
# MAGIC  v.content_type,
# MAGIC  v.channel_or_app,
# MAGIC  v.genre,
# MAGIC  v.start_time,
# MAGIC  v.duration_minutes,
# MAGIC  v.completion_rate,
# MAGIC  -- 파생 컬럼: 날짜/시간 분류
# MAGIC  DATE(v.start_time) AS viewing_date,
# MAGIC  HOUR(v.start_time) AS viewing_hour,
# MAGIC  DAYOFWEEK(v.start_time) AS day_of_week,
# MAGIC  CASE WHEN DAYOFWEEK(v.start_time) IN (1, 7) THEN true ELSE false END AS is_weekend,
# MAGIC  CASE
# MAGIC   WHEN HOUR(v.start_time) BETWEEN 6 AND 11 THEN 'morning'
# MAGIC   WHEN HOUR(v.start_time) BETWEEN 12 AND 17 THEN 'afternoon'
# MAGIC   WHEN HOUR(v.start_time) BETWEEN 18 AND 22 THEN 'prime_time'
# MAGIC   ELSE 'late_night'
# MAGIC  END AS time_slot,
# MAGIC  -- 종료 시간
# MAGIC  v.start_time + INTERVAL '1' MINUTE * v.duration_minutes AS end_time,
# MAGIC  -- 디바이스 정보 JOIN
# MAGIC  d.model_name,
# MAGIC  d.region,
# MAGIC  d.price_tier
# MAGIC FROM bronze.viewing_logs v
# MAGIC INNER JOIN silver.devices_ctas d ON v.device_id = d.device_id
# MAGIC WHERE v.duration_minutes > 0
# MAGIC  AND v.duration_minutes <= 480
# MAGIC  AND v.start_time >= '2025-01-01'
# MAGIC  AND v.start_time < '2025-03-01';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 시간대별 시청 분포 확인
# MAGIC SELECT
# MAGIC  time_slot,
# MAGIC  COUNT(*) AS views,
# MAGIC  ROUND(AVG(duration_minutes), 1) AS avg_duration,
# MAGIC  ROUND(AVG(completion_rate), 2) AS avg_completion
# MAGIC FROM silver.viewing_logs_ctas
# MAGIC GROUP BY time_slot
# MAGIC ORDER BY views DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1-3. 클릭 이벤트 정제 (silver.click_events_ctas)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE silver.click_events_ctas AS
# MAGIC WITH session_stats AS (
# MAGIC  -- 세션별 통계 계산
# MAGIC  SELECT
# MAGIC   session_id,
# MAGIC   MIN(event_timestamp) AS session_start_time,
# MAGIC   MAX(event_timestamp) AS session_end_time,
# MAGIC   COUNT(*) AS events_in_session,
# MAGIC   (UNIX_TIMESTAMP(MAX(event_timestamp)) - UNIX_TIMESTAMP(MIN(event_timestamp))) / 60 AS session_duration_minutes
# MAGIC  FROM bronze.click_events
# MAGIC  GROUP BY session_id
# MAGIC )
# MAGIC SELECT
# MAGIC  e.event_id,
# MAGIC  e.device_id,
# MAGIC  e.user_profile_id,
# MAGIC  e.event_timestamp,
# MAGIC  e.event_type,
# MAGIC  e.screen_name,
# MAGIC  e.element_id,
# MAGIC  e.session_id,
# MAGIC  -- 파생 컬럼
# MAGIC  DATE(e.event_timestamp) AS event_date,
# MAGIC  HOUR(e.event_timestamp) AS event_hour,
# MAGIC  -- 세션 정보
# MAGIC  s.session_start_time,
# MAGIC  s.session_duration_minutes,
# MAGIC  s.events_in_session,
# MAGIC  -- 디바이스 정보
# MAGIC  d.model_name,
# MAGIC  d.region,
# MAGIC  d.price_tier
# MAGIC FROM bronze.click_events e
# MAGIC INNER JOIN silver.devices_ctas d ON e.device_id = d.device_id
# MAGIC LEFT JOIN session_stats s ON e.session_id = s.session_id
# MAGIC WHERE e.event_timestamp IS NOT NULL
# MAGIC  AND e.event_timestamp >= '2025-01-01'
# MAGIC  AND e.event_timestamp < '2025-03-01';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 이벤트 유형별 분포
# MAGIC SELECT event_type, COUNT(*) AS cnt,
# MAGIC    COUNT(DISTINCT device_id) AS unique_devices
# MAGIC FROM silver.click_events_ctas
# MAGIC GROUP BY event_type
# MAGIC ORDER BY cnt DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1-4. 광고 로그 정제 (silver.ad_impressions_ctas)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE silver.ad_impressions_ctas AS
# MAGIC SELECT
# MAGIC  a.impression_id,
# MAGIC  a.device_id,
# MAGIC  a.user_profile_id,
# MAGIC  a.ad_id,
# MAGIC  a.advertiser,
# MAGIC  a.ad_category,
# MAGIC  a.ad_format,
# MAGIC  a.placement,
# MAGIC  a.impression_timestamp,
# MAGIC  -- 클릭 정합성 보정: was_clicked=true인데 click_timestamp이 NULL이면 false로
# MAGIC  CASE
# MAGIC   WHEN a.was_clicked = true AND a.click_timestamp IS NULL THEN false
# MAGIC   ELSE a.was_clicked
# MAGIC  END AS was_clicked,
# MAGIC  a.click_timestamp,
# MAGIC  a.was_converted,
# MAGIC  a.bid_price_usd,
# MAGIC  a.win_price_usd,
# MAGIC  a.duration_seconds,
# MAGIC  -- 파생 컬럼
# MAGIC  DATE(a.impression_timestamp) AS impression_date,
# MAGIC  HOUR(a.impression_timestamp) AS impression_hour,
# MAGIC  CASE
# MAGIC   WHEN HOUR(a.impression_timestamp) BETWEEN 18 AND 22 THEN 'prime_time'
# MAGIC   WHEN HOUR(a.impression_timestamp) BETWEEN 6 AND 11 THEN 'morning'
# MAGIC   WHEN HOUR(a.impression_timestamp) BETWEEN 12 AND 17 THEN 'afternoon'
# MAGIC   ELSE 'late_night'
# MAGIC  END AS time_slot,
# MAGIC  -- 클릭 소요 시간 (초)
# MAGIC  CASE
# MAGIC   WHEN a.click_timestamp IS NOT NULL
# MAGIC   THEN UNIX_TIMESTAMP(a.click_timestamp) - UNIX_TIMESTAMP(a.impression_timestamp)
# MAGIC   ELSE NULL
# MAGIC  END AS time_to_click_seconds,
# MAGIC  -- 디바이스 정보
# MAGIC  d.model_name,
# MAGIC  d.region,
# MAGIC  d.price_tier
# MAGIC FROM bronze.ad_impressions a
# MAGIC INNER JOIN silver.devices_ctas d ON a.device_id = d.device_id
# MAGIC WHERE a.bid_price_usd > 0
# MAGIC  AND a.impression_timestamp >= '2025-01-01'
# MAGIC  AND a.impression_timestamp < '2025-03-01';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 광고 형식별 CTR
# MAGIC SELECT
# MAGIC  ad_format,
# MAGIC  COUNT(*) AS impressions,
# MAGIC  SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END) AS clicks,
# MAGIC  ROUND(SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ctr_pct
# MAGIC FROM silver.ad_impressions_ctas
# MAGIC GROUP BY ad_format
# MAGIC ORDER BY ctr_pct DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 2: Silver → Gold 집계
# MAGIC
# MAGIC Gold 레이어는 **비즈니스 질문에 바로 답할 수 있는** 집계 테이블입니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2-1. 일별 시청 요약 (gold.daily_viewing_summary)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold.daily_viewing_summary AS
# MAGIC SELECT
# MAGIC  viewing_date,
# MAGIC  region,
# MAGIC  content_type,
# MAGIC  genre,
# MAGIC  time_slot,
# MAGIC  COUNT(*) AS total_views,
# MAGIC  COUNT(DISTINCT device_id) AS unique_devices,
# MAGIC  COUNT(DISTINCT user_profile_id) AS unique_users,
# MAGIC  SUM(duration_minutes) AS total_minutes,
# MAGIC  ROUND(AVG(duration_minutes), 1) AS avg_duration_minutes,
# MAGIC  ROUND(AVG(completion_rate), 2) AS avg_completion_rate,
# MAGIC  PERCENTILE_APPROX(duration_minutes, 0.5) AS p50_duration,
# MAGIC  PERCENTILE_APPROX(duration_minutes, 0.9) AS p90_duration
# MAGIC FROM silver.viewing_logs_ctas
# MAGIC GROUP BY viewing_date, region, content_type, genre, time_slot;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 날짜별 총 시청량 추이 (최근 14일)
# MAGIC SELECT viewing_date, SUM(total_views) AS views, SUM(unique_users) AS users
# MAGIC FROM gold.daily_viewing_summary
# MAGIC GROUP BY viewing_date
# MAGIC ORDER BY viewing_date DESC
# MAGIC LIMIT 14;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2-2. 사용자 프로필 (gold.user_profiles)
# MAGIC
# MAGIC 개인화 추천 엔진의 핵심 피처 테이블입니다.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold.user_profiles AS
# MAGIC -- 장르/콘텐츠유형/시간대별 Top 1을 ROW_NUMBER로 계산
# MAGIC WITH genre_rank AS (
# MAGIC  SELECT device_id, user_profile_id, genre,
# MAGIC     ROW_NUMBER() OVER (PARTITION BY device_id, user_profile_id ORDER BY COUNT(*) DESC) AS rn
# MAGIC  FROM silver.viewing_logs_ctas
# MAGIC  GROUP BY device_id, user_profile_id, genre
# MAGIC ),
# MAGIC content_rank AS (
# MAGIC  SELECT device_id, user_profile_id, content_type,
# MAGIC     ROW_NUMBER() OVER (PARTITION BY device_id, user_profile_id ORDER BY COUNT(*) DESC) AS rn
# MAGIC  FROM silver.viewing_logs_ctas
# MAGIC  GROUP BY device_id, user_profile_id, content_type
# MAGIC ),
# MAGIC slot_rank AS (
# MAGIC  SELECT device_id, user_profile_id, time_slot,
# MAGIC     ROW_NUMBER() OVER (PARTITION BY device_id, user_profile_id ORDER BY COUNT(*) DESC) AS rn
# MAGIC  FROM silver.viewing_logs_ctas
# MAGIC  GROUP BY device_id, user_profile_id, time_slot
# MAGIC ),
# MAGIC viewing_agg AS (
# MAGIC  SELECT
# MAGIC   device_id,
# MAGIC   user_profile_id,
# MAGIC   COUNT(DISTINCT viewing_date) AS total_viewing_days,
# MAGIC   SUM(duration_minutes) AS total_viewing_minutes,
# MAGIC   ROUND(SUM(duration_minutes) / NULLIF(COUNT(DISTINCT viewing_date), 0), 1) AS avg_daily_viewing_minutes,
# MAGIC   ROUND(SUM(CASE WHEN is_weekend THEN 1 ELSE 0 END) * 1.0 / COUNT(*), 2) AS weekend_ratio
# MAGIC  FROM silver.viewing_logs_ctas
# MAGIC  GROUP BY device_id, user_profile_id
# MAGIC ),
# MAGIC click_features AS (
# MAGIC  SELECT
# MAGIC   device_id,
# MAGIC   user_profile_id,
# MAGIC   COUNT(*) AS total_click_events,
# MAGIC   ROUND(AVG(session_duration_minutes), 1) AS avg_session_duration,
# MAGIC   SUM(CASE WHEN event_type = 'search' THEN 1 ELSE 0 END) AS search_count,
# MAGIC   SUM(CASE WHEN event_type = 'voice_command' THEN 1 ELSE 0 END) AS voice_command_count
# MAGIC  FROM silver.click_events_ctas
# MAGIC  GROUP BY device_id, user_profile_id
# MAGIC ),
# MAGIC ad_features AS (
# MAGIC  SELECT
# MAGIC   device_id,
# MAGIC   user_profile_id,
# MAGIC   COUNT(*) AS total_ad_impressions,
# MAGIC   SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END) AS total_ad_clicks,
# MAGIC   ROUND(SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS ad_ctr,
# MAGIC   ROUND(AVG(time_to_click_seconds), 1) AS avg_time_to_click
# MAGIC  FROM silver.ad_impressions_ctas
# MAGIC  GROUP BY device_id, user_profile_id
# MAGIC )
# MAGIC SELECT
# MAGIC  v.device_id,
# MAGIC  v.user_profile_id,
# MAGIC  -- 시청 피처
# MAGIC  v.total_viewing_days,
# MAGIC  v.total_viewing_minutes,
# MAGIC  v.avg_daily_viewing_minutes,
# MAGIC  g.genre AS favorite_genre,
# MAGIC  ct.content_type AS favorite_content_type,
# MAGIC  sl.time_slot AS preferred_time_slot,
# MAGIC  v.weekend_ratio,
# MAGIC  -- 클릭 피처
# MAGIC  COALESCE(c.total_click_events, 0) AS total_click_events,
# MAGIC  c.avg_session_duration,
# MAGIC  COALESCE(c.search_count, 0) AS search_count,
# MAGIC  COALESCE(c.voice_command_count, 0) AS voice_command_count,
# MAGIC  -- 광고 피처
# MAGIC  COALESCE(a.total_ad_impressions, 0) AS total_ad_impressions,
# MAGIC  COALESCE(a.total_ad_clicks, 0) AS total_ad_clicks,
# MAGIC  COALESCE(a.ad_ctr, 0) AS ad_ctr,
# MAGIC  a.avg_time_to_click,
# MAGIC  -- 디바이스 정보
# MAGIC  d.model_name,
# MAGIC  d.region,
# MAGIC  d.price_tier,
# MAGIC  d.has_fasttv
# MAGIC FROM viewing_agg v
# MAGIC LEFT JOIN genre_rank g ON v.device_id = g.device_id AND v.user_profile_id = g.user_profile_id AND g.rn = 1
# MAGIC LEFT JOIN content_rank ct ON v.device_id = ct.device_id AND v.user_profile_id = ct.user_profile_id AND ct.rn = 1
# MAGIC LEFT JOIN slot_rank sl ON v.device_id = sl.device_id AND v.user_profile_id = sl.user_profile_id AND sl.rn = 1
# MAGIC LEFT JOIN click_features c ON v.device_id = c.device_id AND v.user_profile_id = c.user_profile_id
# MAGIC LEFT JOIN ad_features a ON v.device_id = a.device_id AND v.user_profile_id = a.user_profile_id
# MAGIC LEFT JOIN silver.devices_ctas d ON v.device_id = d.device_id;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 사용자 프로필 요약
# MAGIC SELECT
# MAGIC  COUNT(*) AS total_users,
# MAGIC  ROUND(AVG(total_viewing_minutes), 0) AS avg_total_minutes,
# MAGIC  ROUND(AVG(ad_ctr), 2) AS avg_ad_ctr
# MAGIC FROM gold.user_profiles;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2-3. 광고 성과 (gold.ad_performance)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold.ad_performance AS
# MAGIC SELECT
# MAGIC  impression_date,
# MAGIC  advertiser,
# MAGIC  ad_category,
# MAGIC  ad_format,
# MAGIC  placement,
# MAGIC  region,
# MAGIC  COUNT(*) AS impressions,
# MAGIC  SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END) AS clicks,
# MAGIC  SUM(CASE WHEN was_converted THEN 1 ELSE 0 END) AS conversions,
# MAGIC  ROUND(SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ctr,
# MAGIC  ROUND(SUM(CASE WHEN was_converted THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END), 0), 2) AS cvr,
# MAGIC  ROUND(SUM(win_price_usd), 4) AS total_spend_usd,
# MAGIC  ROUND(SUM(win_price_usd) / NULLIF(SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END), 0), 4) AS cost_per_click_usd,
# MAGIC  ROUND(SUM(win_price_usd) / COUNT(*) * 1000, 4) AS revenue_per_mille_usd
# MAGIC FROM silver.ad_impressions_ctas
# MAGIC GROUP BY impression_date, advertiser, ad_category, ad_format, placement, region;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 광고주별 총 성과 Top 10
# MAGIC SELECT advertiser,
# MAGIC    SUM(impressions) AS total_impressions,
# MAGIC    SUM(clicks) AS total_clicks,
# MAGIC    ROUND(SUM(clicks) * 100.0 / SUM(impressions), 2) AS overall_ctr,
# MAGIC    ROUND(SUM(total_spend_usd), 2) AS total_spend
# MAGIC FROM gold.ad_performance
# MAGIC GROUP BY advertiser
# MAGIC ORDER BY total_impressions DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2-4. 콘텐츠 인기도 랭킹 (gold.content_rankings)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold.content_rankings AS
# MAGIC SELECT
# MAGIC  viewing_date,
# MAGIC  channel_or_app,
# MAGIC  genre,
# MAGIC  COUNT(*) AS daily_views,
# MAGIC  COUNT(DISTINCT device_id) AS daily_unique_viewers,
# MAGIC  SUM(duration_minutes) AS daily_total_minutes,
# MAGIC  ROUND(AVG(completion_rate), 2) AS avg_completion_rate,
# MAGIC  -- 일별 순위 (시청자 수 기준)
# MAGIC  RANK() OVER (PARTITION BY viewing_date ORDER BY COUNT(DISTINCT device_id) DESC) AS daily_rank
# MAGIC FROM silver.viewing_logs_ctas
# MAGIC GROUP BY viewing_date, channel_or_app, genre;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 전체 기간 인기 콘텐츠 Top 10
# MAGIC SELECT channel_or_app, genre,
# MAGIC    SUM(daily_views) AS total_views,
# MAGIC    SUM(daily_unique_viewers) AS total_viewers,
# MAGIC    ROUND(AVG(avg_completion_rate), 2) AS avg_completion
# MAGIC FROM gold.content_rankings
# MAGIC GROUP BY channel_or_app, genre
# MAGIC ORDER BY total_viewers DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 3: 대시보드 & Genie용 심화 Gold 테이블
# MAGIC
# MAGIC 아래 5개 테이블은 AI/BI 대시보드와 Genie Space에서
# MAGIC **풍부한 인사이트**를 제공하기 위한 심화 집계입니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3-1. 주간 KPI 트렌드 (gold.weekly_kpi_trends)
# MAGIC
# MAGIC 경영진 대시보드 첫 화면용: 핵심 지표 + 전주 대비 변화율

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold.weekly_kpi_trends AS
# MAGIC WITH weekly AS (
# MAGIC  SELECT
# MAGIC   DATE_TRUNC('WEEK', viewing_date) AS week_start,
# MAGIC   SUM(total_views) AS total_views,
# MAGIC   SUM(unique_devices) AS weekly_active_devices,
# MAGIC   SUM(unique_users) AS weekly_active_users,
# MAGIC   SUM(total_minutes) AS total_viewing_minutes,
# MAGIC   ROUND(SUM(total_minutes) / NULLIF(SUM(unique_users), 0), 1) AS minutes_per_user
# MAGIC  FROM gold.daily_viewing_summary
# MAGIC  GROUP BY DATE_TRUNC('WEEK', viewing_date)
# MAGIC ),
# MAGIC ad_weekly AS (
# MAGIC  SELECT
# MAGIC   DATE_TRUNC('WEEK', impression_date) AS week_start,
# MAGIC   SUM(impressions) AS total_impressions,
# MAGIC   SUM(clicks) AS total_clicks,
# MAGIC   ROUND(SUM(clicks) * 100.0 / NULLIF(SUM(impressions), 0), 2) AS weekly_ctr,
# MAGIC   ROUND(SUM(total_spend_usd), 2) AS weekly_ad_revenue_usd
# MAGIC  FROM gold.ad_performance
# MAGIC  GROUP BY DATE_TRUNC('WEEK', impression_date)
# MAGIC )
# MAGIC SELECT
# MAGIC  w.week_start,
# MAGIC  w.total_views,
# MAGIC  w.weekly_active_devices,
# MAGIC  w.weekly_active_users,
# MAGIC  w.total_viewing_minutes,
# MAGIC  w.minutes_per_user,
# MAGIC  a.total_impressions AS ad_impressions,
# MAGIC  a.total_clicks AS ad_clicks,
# MAGIC  a.weekly_ctr,
# MAGIC  a.weekly_ad_revenue_usd,
# MAGIC  -- 전주 대비 변화율
# MAGIC  ROUND((w.weekly_active_users - LAG(w.weekly_active_users) OVER (ORDER BY w.week_start))
# MAGIC   * 100.0 / NULLIF(LAG(w.weekly_active_users) OVER (ORDER BY w.week_start), 0), 1) AS users_wow_pct,
# MAGIC  ROUND((w.total_viewing_minutes - LAG(w.total_viewing_minutes) OVER (ORDER BY w.week_start))
# MAGIC   * 100.0 / NULLIF(LAG(w.total_viewing_minutes) OVER (ORDER BY w.week_start), 0), 1) AS minutes_wow_pct,
# MAGIC  ROUND((a.weekly_ad_revenue_usd - LAG(a.weekly_ad_revenue_usd) OVER (ORDER BY w.week_start))
# MAGIC   * 100.0 / NULLIF(LAG(a.weekly_ad_revenue_usd) OVER (ORDER BY w.week_start), 0), 1) AS revenue_wow_pct
# MAGIC FROM weekly w
# MAGIC LEFT JOIN ad_weekly a ON w.week_start = a.week_start
# MAGIC ORDER BY w.week_start;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM gold.weekly_kpi_trends ORDER BY week_start DESC LIMIT 5;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3-2. 사용자 세그먼트 (gold.user_segments)
# MAGIC
# MAGIC user_profiles 기반 비즈니스 세그먼트 분류 → 타겟 마케팅, 리텐션 전략

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold.user_segments AS
# MAGIC SELECT
# MAGIC  *,
# MAGIC  -- 시청 행동 세그먼트
# MAGIC  CASE
# MAGIC   WHEN avg_daily_viewing_minutes >= 120 THEN 'heavy_viewer'
# MAGIC   WHEN avg_daily_viewing_minutes >= 30 THEN 'regular_viewer'
# MAGIC   ELSE 'casual_viewer'
# MAGIC  END AS viewing_segment,
# MAGIC  -- 광고 반응 세그먼트
# MAGIC  CASE
# MAGIC   WHEN ad_ctr >= 5.0 THEN 'ad_enthusiast'
# MAGIC   WHEN ad_ctr >= 2.0 THEN 'ad_responsive'
# MAGIC   WHEN total_ad_clicks > 0 THEN 'ad_occasional'
# MAGIC   ELSE 'ad_resistant'
# MAGIC  END AS ad_segment,
# MAGIC  -- FastTV 참여도
# MAGIC  CASE
# MAGIC   WHEN favorite_content_type = 'fasttv' THEN 'fasttv_primary'
# MAGIC   WHEN total_ad_impressions > 50 THEN 'fasttv_exposed'
# MAGIC   ELSE 'fasttv_minimal'
# MAGIC  END AS fasttv_segment,
# MAGIC  -- 가치 세그먼트 (시청시간 × 광고반응 종합)
# MAGIC  CASE
# MAGIC   WHEN avg_daily_viewing_minutes >= 60 AND ad_ctr >= 2.0 THEN 'high_value'
# MAGIC   WHEN avg_daily_viewing_minutes >= 60 OR ad_ctr >= 2.0 THEN 'medium_value'
# MAGIC   ELSE 'low_value'
# MAGIC  END AS value_segment
# MAGIC FROM gold.user_profiles;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 세그먼트별 사용자 분포
# MAGIC SELECT value_segment, viewing_segment, ad_segment,
# MAGIC    COUNT(*) AS users,
# MAGIC    ROUND(AVG(total_viewing_minutes), 0) AS avg_minutes,
# MAGIC    ROUND(AVG(ad_ctr), 2) AS avg_ctr
# MAGIC FROM gold.user_segments
# MAGIC GROUP BY value_segment, viewing_segment, ad_segment
# MAGIC ORDER BY users DESC
# MAGIC LIMIT 15;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3-3. FastTV 광고 수익 분석 (gold.fasttv_revenue_analysis)
# MAGIC
# MAGIC 사업 모델 핵심: FastTV 광고 슬롯별 수익성 심층 분석

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold.fasttv_revenue_analysis AS
# MAGIC -- silver 테이블에서 직접 집계 (time_slot은 gold.ad_performance에 없으므로)
# MAGIC WITH daily_revenue AS (
# MAGIC  SELECT
# MAGIC   impression_date,
# MAGIC   region,
# MAGIC   ad_format,
# MAGIC   time_slot,
# MAGIC   COUNT(*) AS impressions,
# MAGIC   SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END) AS clicks,
# MAGIC   SUM(CASE WHEN was_converted THEN 1 ELSE 0 END) AS conversions,
# MAGIC   ROUND(SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS ctr,
# MAGIC   ROUND(SUM(win_price_usd), 4) AS revenue_usd,
# MAGIC   ROUND(SUM(win_price_usd) / NULLIF(COUNT(*), 0) * 1000, 4) AS ecpm_usd
# MAGIC  FROM silver.ad_impressions_ctas
# MAGIC  GROUP BY impression_date, region, ad_format, time_slot
# MAGIC )
# MAGIC SELECT
# MAGIC  *,
# MAGIC  -- 전일 대비 수익 변화
# MAGIC  LAG(revenue_usd) OVER (PARTITION BY region, ad_format, time_slot ORDER BY impression_date) AS prev_day_revenue,
# MAGIC  ROUND((revenue_usd - LAG(revenue_usd) OVER (PARTITION BY region, ad_format, time_slot ORDER BY impression_date))
# MAGIC   * 100.0 / NULLIF(LAG(revenue_usd) OVER (PARTITION BY region, ad_format, time_slot ORDER BY impression_date), 0), 1)
# MAGIC   AS revenue_dod_pct
# MAGIC FROM daily_revenue;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 지역별 × 시간대별 eCPM 비교
# MAGIC SELECT region, time_slot,
# MAGIC    ROUND(AVG(ecpm_usd), 4) AS avg_ecpm,
# MAGIC    ROUND(SUM(revenue_usd), 2) AS total_revenue
# MAGIC FROM gold.fasttv_revenue_analysis
# MAGIC GROUP BY region, time_slot
# MAGIC ORDER BY total_revenue DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3-4. 콘텐츠 소비 퍼널 (gold.content_engagement_funnel)
# MAGIC
# MAGIC 홈화면 노출 → 콘텐츠 선택 → 시청 시작 → 시청 완료 전환율

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold.content_engagement_funnel AS
# MAGIC WITH home_events AS (
# MAGIC  -- 홈 화면 활동 (노출 proxy)
# MAGIC  SELECT event_date, region, COUNT(*) AS home_impressions,
# MAGIC     COUNT(DISTINCT device_id) AS home_active_devices
# MAGIC  FROM silver.click_events_ctas
# MAGIC  WHERE screen_name = 'home'
# MAGIC  GROUP BY event_date, region
# MAGIC ),
# MAGIC selections AS (
# MAGIC  -- 콘텐츠 선택 이벤트
# MAGIC  SELECT event_date, region, COUNT(*) AS content_selections
# MAGIC  FROM silver.click_events_ctas
# MAGIC  WHERE event_type = 'content_select'
# MAGIC  GROUP BY event_date, region
# MAGIC ),
# MAGIC views AS (
# MAGIC  -- 실제 시청
# MAGIC  SELECT viewing_date AS event_date, region,
# MAGIC     COUNT(*) AS viewing_starts,
# MAGIC     SUM(CASE WHEN completion_rate >= 0.8 THEN 1 ELSE 0 END) AS viewing_completions
# MAGIC  FROM silver.viewing_logs_ctas
# MAGIC  GROUP BY viewing_date, region
# MAGIC )
# MAGIC SELECT
# MAGIC  h.event_date,
# MAGIC  h.region,
# MAGIC  h.home_impressions,
# MAGIC  h.home_active_devices,
# MAGIC  COALESCE(s.content_selections, 0) AS content_selections,
# MAGIC  COALESCE(v.viewing_starts, 0) AS viewing_starts,
# MAGIC  COALESCE(v.viewing_completions, 0) AS viewing_completions,
# MAGIC  -- 퍼널 전환율
# MAGIC  ROUND(COALESCE(s.content_selections, 0) * 100.0 / NULLIF(h.home_impressions, 0), 2) AS selection_rate_pct,
# MAGIC  ROUND(COALESCE(v.viewing_starts, 0) * 100.0 / NULLIF(s.content_selections, 0), 2) AS start_rate_pct,
# MAGIC  ROUND(COALESCE(v.viewing_completions, 0) * 100.0 / NULLIF(v.viewing_starts, 0), 2) AS completion_rate_pct,
# MAGIC  -- 전체 퍼널 전환율 (홈 → 시청완료)
# MAGIC  ROUND(COALESCE(v.viewing_completions, 0) * 100.0 / NULLIF(h.home_impressions, 0), 2) AS overall_conversion_pct
# MAGIC FROM home_events h
# MAGIC LEFT JOIN selections s ON h.event_date = s.event_date AND h.region = s.region
# MAGIC LEFT JOIN views v ON h.event_date = v.event_date AND h.region = v.region;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 지역별 퍼널 요약
# MAGIC SELECT region,
# MAGIC    ROUND(AVG(selection_rate_pct), 1) AS avg_selection_rate,
# MAGIC    ROUND(AVG(start_rate_pct), 1) AS avg_start_rate,
# MAGIC    ROUND(AVG(completion_rate_pct), 1) AS avg_completion_rate,
# MAGIC    ROUND(AVG(overall_conversion_pct), 1) AS avg_overall_conversion
# MAGIC FROM gold.content_engagement_funnel
# MAGIC GROUP BY region
# MAGIC ORDER BY avg_overall_conversion DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3-5. 시간대별 히트맵 (gold.hourly_heatmap)
# MAGIC
# MAGIC 24시간 × 7요일 히트맵 시각화 최적화 테이블

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold.hourly_heatmap AS
# MAGIC WITH viewing_heat AS (
# MAGIC  SELECT
# MAGIC   CASE day_of_week
# MAGIC    WHEN 1 THEN 'Sun' WHEN 2 THEN 'Mon' WHEN 3 THEN 'Tue'
# MAGIC    WHEN 4 THEN 'Wed' WHEN 5 THEN 'Thu' WHEN 6 THEN 'Fri' WHEN 7 THEN 'Sat'
# MAGIC   END AS day_name,
# MAGIC   day_of_week,
# MAGIC   viewing_hour AS hour_of_day,
# MAGIC   region,
# MAGIC   COUNT(DISTINCT device_id) AS active_devices,
# MAGIC   COUNT(*) AS total_views,
# MAGIC   SUM(duration_minutes) AS total_minutes,
# MAGIC   ROUND(AVG(duration_minutes), 1) AS avg_duration
# MAGIC  FROM silver.viewing_logs_ctas
# MAGIC  GROUP BY day_of_week, viewing_hour, region
# MAGIC ),
# MAGIC ad_heat AS (
# MAGIC  SELECT
# MAGIC   DAYOFWEEK(impression_timestamp) AS day_of_week,
# MAGIC   impression_hour AS hour_of_day,
# MAGIC   region,
# MAGIC   COUNT(*) AS ad_impressions,
# MAGIC   ROUND(SUM(win_price_usd), 4) AS ad_revenue_usd
# MAGIC  FROM silver.ad_impressions_ctas
# MAGIC  GROUP BY DAYOFWEEK(impression_timestamp), impression_hour, region
# MAGIC )
# MAGIC SELECT
# MAGIC  v.day_name,
# MAGIC  v.day_of_week,
# MAGIC  v.hour_of_day,
# MAGIC  v.region,
# MAGIC  v.active_devices,
# MAGIC  v.total_views,
# MAGIC  v.total_minutes,
# MAGIC  v.avg_duration,
# MAGIC  COALESCE(a.ad_impressions, 0) AS ad_impressions,
# MAGIC  COALESCE(a.ad_revenue_usd, 0) AS ad_revenue_usd,
# MAGIC  -- 시간대 분류
# MAGIC  CASE
# MAGIC   WHEN v.hour_of_day BETWEEN 6 AND 11 THEN 'morning'
# MAGIC   WHEN v.hour_of_day BETWEEN 12 AND 17 THEN 'afternoon'
# MAGIC   WHEN v.hour_of_day BETWEEN 18 AND 22 THEN 'prime_time'
# MAGIC   ELSE 'late_night'
# MAGIC  END AS time_slot
# MAGIC FROM viewing_heat v
# MAGIC LEFT JOIN ad_heat a ON v.day_of_week = a.day_of_week
# MAGIC  AND v.hour_of_day = a.hour_of_day AND v.region = a.region;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Korea 지역 시청 히트맵 (요일 × 시간)
# MAGIC SELECT day_name, hour_of_day, active_devices, ad_revenue_usd
# MAGIC FROM gold.hourly_heatmap
# MAGIC WHERE region = 'Korea'
# MAGIC ORDER BY day_of_week, hour_of_day;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 4: 전체 결과 요약

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 전체 테이블 현황
# MAGIC SELECT 'bronze.devices' AS table_name, COUNT(*) AS rows FROM bronze.devices
# MAGIC UNION ALL SELECT 'bronze.viewing_logs', COUNT(*) FROM bronze.viewing_logs
# MAGIC UNION ALL SELECT 'bronze.click_events', COUNT(*) FROM bronze.click_events
# MAGIC UNION ALL SELECT 'bronze.ad_impressions', COUNT(*) FROM bronze.ad_impressions
# MAGIC UNION ALL SELECT '---', 0
# MAGIC UNION ALL SELECT 'silver.devices_ctas', COUNT(*) FROM silver.devices_ctas
# MAGIC UNION ALL SELECT 'silver.viewing_logs_ctas', COUNT(*) FROM silver.viewing_logs_ctas
# MAGIC UNION ALL SELECT 'silver.click_events_ctas', COUNT(*) FROM silver.click_events_ctas
# MAGIC UNION ALL SELECT 'silver.ad_impressions_ctas', COUNT(*) FROM silver.ad_impressions_ctas
# MAGIC UNION ALL SELECT '---', 0
# MAGIC UNION ALL SELECT 'gold.daily_viewing_summary', COUNT(*) FROM gold.daily_viewing_summary
# MAGIC UNION ALL SELECT 'gold.user_profiles', COUNT(*) FROM gold.user_profiles
# MAGIC UNION ALL SELECT 'gold.ad_performance', COUNT(*) FROM gold.ad_performance
# MAGIC UNION ALL SELECT 'gold.content_rankings', COUNT(*) FROM gold.content_rankings
# MAGIC UNION ALL SELECT '---', 0
# MAGIC UNION ALL SELECT 'gold.weekly_kpi_trends', COUNT(*) FROM gold.weekly_kpi_trends
# MAGIC UNION ALL SELECT 'gold.user_segments', COUNT(*) FROM gold.user_segments
# MAGIC UNION ALL SELECT 'gold.fasttv_revenue_analysis', COUNT(*) FROM gold.fasttv_revenue_analysis
# MAGIC UNION ALL SELECT 'gold.content_engagement_funnel', COUNT(*) FROM gold.content_engagement_funnel
# MAGIC UNION ALL SELECT 'gold.hourly_heatmap', COUNT(*) FROM gold.hourly_heatmap;

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ CTAS 수동 변환 완료!
# MAGIC
# MAGIC ### 배운 것
# MAGIC - SQL `CREATE OR REPLACE TABLE ... AS SELECT` 로 단계별 변환
# MAGIC - Silver: NULL 제거, 이상치 필터, 파생 컬럼, JOIN enrichment
# MAGIC - Gold: 집계(GROUP BY), 윈도우 함수(RANK, ROW_NUMBER), 다중 CTE
# MAGIC
# MAGIC ### 한계
# MAGIC - **수동 실행**: 매번 노트북을 돌려야 함
# MAGIC - **전체 재처리**: 데이터가 추가되면 전체를 다시 계산 (증분 처리 없음)
# MAGIC - **의존성 관리 없음**: 테이블 순서를 직접 관리해야 함
# MAGIC - **데이터 품질 검증 없음**: 별도로 체크해야 함
# MAGIC
# MAGIC ### 다음 단계
# MAGIC → `04_sdp_pipeline` 노트북에서 **동일한 변환을 SDP(DLT)로** 수행합니다.
# MAGIC 위 한계를 SDP가 어떻게 해결하는지 확인해보세요!
