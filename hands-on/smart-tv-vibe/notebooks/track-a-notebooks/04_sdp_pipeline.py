# Databricks notebook source
# MAGIC %md
# MAGIC # 04. Bronze → Silver → Gold 변환 (SDP 선언적 파이프라인)
# MAGIC
# MAGIC 03 노트북에서 CTAS로 수동 실행한 **동일한 변환** 을 Spark Declarative Pipeline(SDP)로 구현합니다.
# MAGIC
# MAGIC | 비교 항목 | 03 (CTAS 수동) | 04 (SDP 파이프라인) |
# MAGIC |-----------|---------------|-------------------|
# MAGIC | 실행 방식 | 수동 노트북 실행 | 파이프라인 자동 실행 |
# MAGIC | 증분 처리 | ❌ 전체 재계산 | ✅ 자동 증분 |
# MAGIC | 의존성 관리 | ❌ 수동 순서 | ✅ 자동 해결 |
# MAGIC | 데이터 품질 | ❌ 별도 체크 | ✅ Expectations 내장 |
# MAGIC | 오류 복구 | ❌ 수동 | ✅ 자동 재시도 |
# MAGIC
# MAGIC >**중요:** 이 노트북은 SDP 파이프라인 소스코드입니다.
# MAGIC > 직접 "Run All"로 실행하지 마시고,**Workflows > Pipelines** 에서 파이프라인으로 실행하세요.
# MAGIC > Silver 테이블은 `_sdp` suffix로 생성되어 CTAS 결과와 비교할 수 있습니다.
# MAGIC
# MAGIC ### API 버전 안내
# MAGIC > 이 노트북은 최신 `pyspark.pipelines` (dp) API를 사용합니다.
# MAGIC > 이전 `import dlt` 방식은 레거시이며, 새 프로젝트에서는 `dp` API를 사용하세요.

# COMMAND ----------

# MAGIC %md
# MAGIC ## SDP 핵심 개념 정리
# MAGIC
# MAGIC ### 데이터 품질 제어: Expectations
# MAGIC
# MAGIC SDP는 데이터 품질을 **선언적으로** 관리합니다. 03 CTAS에서 WHERE절로 수동 필터하던 것을 자동화합니다.
# MAGIC
# MAGIC | Decorator | 조건 위반 시 동작 | 용도 |
# MAGIC |-----------|----------------|------|
# MAGIC | `@dp.expect("name", "조건")` |**경고만**— 위반 행도 통과 | 모니터링용 (위반 건수 추적) |
# MAGIC | `@dp.expect_or_drop("name", "조건")` |**해당 행 제거**| 데이터 정제 (이상치 필터) |
# MAGIC | `@dp.expect_or_fail("name", "조건")` |**파이프라인 중단**| 필수 조건 (NOT NULL 등) |
# MAGIC
# MAGIC ### 테이블 유형: Table vs Materialized View
# MAGIC
# MAGIC | 유형 | 데코레이터 | 데이터 갱신 | 주 용도 |
# MAGIC |------|-----------|-----------|--------|
# MAGIC |**Streaming Table**| `@dp.table` | 증분 (새 데이터만 처리) | Bronze/Silver — 대량 로그 데이터 |
# MAGIC |**Materialized View**| `@dp.materialized_view` | 전체 재계산 (자동 최적화) | Gold — 집계 테이블, 비즈니스 KPI |
# MAGIC
# MAGIC ### 읽기 방식: read vs readStream
# MAGIC
# MAGIC | 방식 | 코드 | 설명 |
# MAGIC |------|------|------|
# MAGIC | `spark.read.table()` | 배치 읽기 | 전체 테이블 스냅샷 (Bronze→Silver에서 사용) |
# MAGIC | `spark.readStream.table()` | 스트리밍 읽기 | 새로 추가된 데이터만 읽기 (실시간 수집에서 사용) |
# MAGIC
# MAGIC >**팁:**SDP가 의존성을 자동 추적하므로, 어떤 방식이든 `spark.read.table("테이블명")`으로 읽으면 됩니다.
# MAGIC > 외부 카탈로그 테이블은 `spark.read.table("catalog.schema.table")` 전체 경로를 사용합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver Layer: Bronze → 정제

# COMMAND ----------

from pyspark import pipelines as dp
from pyspark.sql.functions import *
from pyspark.sql.window import Window

# 소스 카탈로그: 파이프라인 설정(Configuration)에서 전달
# ⚠️ 이 노트북은 직접 "Run All" 하면 에러가 납니다!
#  반드시 Workflows > Pipelines 에서 파이프라인으로 실행하세요.
try:
  SOURCE_CATALOG = spark.conf.get("source_catalog")
except Exception:
  raise RuntimeError(
    "❌ source_catalog 설정이 없습니다!\n"
    "  이 노트북은 SDP 파이프라인 소스코드입니다.\n"
    "  Workflows > Pipelines에서 파이프라인을 생성하고,\n"
    "  Configuration에 'source_catalog' 키를 추가하세요.\n"
    "  예: source_catalog = <사용자>_smarttv_training"
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Silver: 디바이스 정제

# COMMAND ----------

@dp.table(
  name="devices_sdp",
  comment="정제된 디바이스 마스터 (SDP)",
  table_properties={"quality": "silver"}
)
@dp.expect_or_fail("valid_device_id", "device_id IS NOT NULL")
@dp.expect("valid_registration", "registered_at <= current_timestamp()")
def devices_sdp():
  return (
    spark.read.table(f"{SOURCE_CATALOG}.bronze.devices")
    .withColumn("model_name", upper(col("model_name")))
    .withColumn("price_tier",
      when(col("model_name").like("OLED%"), "premium")
      .when(col("model_name").like("QNED%") | col("model_name").like("NANO%"), "mid")
      .when(col("model_name").like("UHD%"), "entry")
      .otherwise("unknown")
    )
    .withColumn("device_age_days", datediff(current_date(), col("registered_at")))
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Silver: 시청 로그 정제

# COMMAND ----------

@dp.table(
  name="viewing_logs_sdp",
  comment="정제된 시청 로그 (SDP)",
  table_properties={"quality": "silver"}
)
@dp.expect_or_drop("valid_duration", "duration_minutes > 0 AND duration_minutes <= 480")
@dp.expect_or_drop("valid_date_range", "start_time >= '2025-01-01' AND start_time < '2025-03-01'")
def viewing_logs_sdp():
  # spark.read.table()로 파이프라인 내부 테이블 읽기 (SDP가 의존성 자동 추적)
  devices = spark.read.table("devices_sdp")
  viewing = spark.read.table(f"{SOURCE_CATALOG}.bronze.viewing_logs")

  return (
    viewing.join(devices, "device_id", "inner")
    .withColumn("viewing_date", to_date("start_time"))
    .withColumn("viewing_hour", hour("start_time"))
    .withColumn("day_of_week", dayofweek("start_time"))
    .withColumn("is_weekend", dayofweek("start_time").isin(1, 7))
    .withColumn("time_slot",
      when(hour("start_time").between(6, 11), "morning")
      .when(hour("start_time").between(12, 17), "afternoon")
      .when(hour("start_time").between(18, 22), "prime_time")
      .otherwise("late_night")
    )
    .withColumn("end_time", col("start_time") + (col("duration_minutes").cast("int") * expr("INTERVAL 1 MINUTE")))
    .select(
      viewing["*"],
      "viewing_date", "viewing_hour", "day_of_week", "is_weekend",
      "time_slot", "end_time",
      devices["model_name"], devices["region"], "price_tier"
    )
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Silver: 클릭 이벤트 정제

# COMMAND ----------

@dp.table(
  name="click_events_sdp",
  comment="정제된 클릭 이벤트 (SDP)",
  table_properties={"quality": "silver"}
)
@dp.expect_or_fail("valid_timestamp", "event_timestamp IS NOT NULL")
@dp.expect_or_drop("valid_date_range", "event_timestamp >= '2025-01-01' AND event_timestamp < '2025-03-01'")
def click_events_sdp():
  devices = spark.read.table("devices_sdp")
  clicks = spark.read.table(f"{SOURCE_CATALOG}.bronze.click_events")

  # 세션 통계
  session_stats = (
    clicks.groupBy("session_id")
    .agg(
      min("event_timestamp").alias("session_start_time"),
      max("event_timestamp").alias("session_end_time"),
      count("*").alias("events_in_session"),
      ((unix_timestamp(max("event_timestamp")) - unix_timestamp(min("event_timestamp"))) / 60)
        .alias("session_duration_minutes")
    )
  )

  return (
    clicks.join(devices, "device_id", "inner")
    .join(session_stats, "session_id", "left")
    .withColumn("event_date", to_date("event_timestamp"))
    .withColumn("event_hour", hour("event_timestamp"))
    .select(
      clicks["*"],
      "event_date", "event_hour",
      "session_start_time", "session_duration_minutes", "events_in_session",
      devices["model_name"], devices["region"], "price_tier"
    )
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Silver: 광고 로그 정제

# COMMAND ----------

@dp.table(
  name="ad_impressions_sdp",
  comment="정제된 광고 노출 로그 (SDP)",
  table_properties={"quality": "silver"}
)
@dp.expect_or_drop("valid_bid_price", "bid_price_usd > 0")
@dp.expect_or_drop("valid_date_range", "impression_timestamp >= '2025-01-01' AND impression_timestamp < '2025-03-01'")
def ad_impressions_sdp():
  devices = spark.read.table("devices_sdp")
  ads = spark.read.table(f"{SOURCE_CATALOG}.bronze.ad_impressions")

  return (
    ads.join(devices, "device_id", "inner")
    .withColumn("was_clicked",
      when((col("was_clicked") == True) & col("click_timestamp").isNull(), False)
      .otherwise(col("was_clicked"))
    )
    .withColumn("impression_date", to_date("impression_timestamp"))
    .withColumn("impression_hour", hour("impression_timestamp"))
    .withColumn("time_slot",
      when(hour("impression_timestamp").between(18, 22), "prime_time")
      .when(hour("impression_timestamp").between(6, 11), "morning")
      .when(hour("impression_timestamp").between(12, 17), "afternoon")
      .otherwise("late_night")
    )
    .withColumn("time_to_click_seconds",
      when(col("click_timestamp").isNotNull(),
         unix_timestamp("click_timestamp") - unix_timestamp("impression_timestamp"))
    )
    .select(
      ads["impression_id"], ads["device_id"], ads["user_profile_id"],
      ads["ad_id"], ads["advertiser"], ads["ad_category"], ads["ad_format"],
      ads["placement"], ads["impression_timestamp"],
      "was_clicked", ads["click_timestamp"], ads["was_converted"],
      ads["bid_price_usd"], ads["win_price_usd"], ads["duration_seconds"],
      "impression_date", "impression_hour", "time_slot", "time_to_click_seconds",
      devices["model_name"], devices["region"], "price_tier"
    )
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Gold Layer: Silver → 집계
# MAGIC
# MAGIC Gold는 Materialized View로 생성합니다.
# MAGIC SDP가 자동으로 Silver 테이블 변경을 감지하고 Gold를 증분 갱신합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Gold: 일별 시청 요약

# COMMAND ----------

@dp.materialized_view(
  name="daily_viewing_summary_sdp",
  comment="일별 시청 요약 (SDP)"
)
def daily_viewing_summary_sdp():
  return (
    spark.read.table("viewing_logs_sdp")
    .groupBy("viewing_date", "region", "content_type", "genre", "time_slot")
    .agg(
      count("*").alias("total_views"),
      countDistinct("device_id").alias("unique_devices"),
      countDistinct("user_profile_id").alias("unique_users"),
      sum("duration_minutes").alias("total_minutes"),
      round(avg("duration_minutes"), 1).alias("avg_duration_minutes"),
      round(avg("completion_rate"), 2).alias("avg_completion_rate")
    )
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Gold: 광고 성과

# COMMAND ----------

@dp.materialized_view(
  name="ad_performance_sdp",
  comment="광고 성과 집계 (SDP)"
)
def ad_performance_sdp():
  return (
    spark.read.table("ad_impressions_sdp")
    .groupBy("impression_date", "advertiser", "ad_category", "ad_format", "placement", "region")
    .agg(
      count("*").alias("impressions"),
      sum(when(col("was_clicked"), 1).otherwise(0)).alias("clicks"),
      sum(when(col("was_converted"), 1).otherwise(0)).alias("conversions"),
      round(sum(when(col("was_clicked"), 1).otherwise(0)) * 100.0 / count("*"), 2).alias("ctr"),
      round(sum("win_price_usd"), 4).alias("total_spend_usd")
    )
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Gold: 콘텐츠 인기도 랭킹

# COMMAND ----------

@dp.materialized_view(
  name="content_rankings_sdp",
  comment="콘텐츠 인기도 랭킹 (SDP)"
)
def content_rankings_sdp():
  base = (
    spark.read.table("viewing_logs_sdp")
    .groupBy("viewing_date", "channel_or_app", "genre")
    .agg(
      count("*").alias("daily_views"),
      countDistinct("device_id").alias("daily_unique_viewers"),
      sum("duration_minutes").alias("daily_total_minutes"),
      round(avg("completion_rate"), 2).alias("avg_completion_rate")
    )
  )
  w = Window.partitionBy("viewing_date").orderBy(col("daily_unique_viewers").desc())
  return base.withColumn("daily_rank", rank().over(w))

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Streaming Layer: Auto Loader로 실시간 이벤트 수집
# MAGIC
# MAGIC 06_realtime_event_generator 앱이 UC Volume에 적재한 JSON 파일을
# MAGIC**Auto Loader(cloudFiles)** 로 자동 감지하여 Bronze Streaming Table로 수집합니다.
# MAGIC
# MAGIC >**왜 `readStream`인가?**# MAGIC > 위 Silver 테이블들은 `spark.read.table()`(배치)로 한번에 읽었습니다.
# MAGIC > 하지만 실시간 파일 수집은 **새 파일이 도착할 때마다** 처리해야 하므로 `readStream`을 사용합니다.
# MAGIC > Auto Loader가 체크포인트를 관리하여 이미 처리한 파일은 다시 읽지 않습니다.
# MAGIC
# MAGIC ```
# MAGIC App → /Volumes/.../landing/viewing_events/*.json
# MAGIC          ↓ Auto Loader (새 파일 자동 감지)
# MAGIC       bronze_live_viewing (Streaming Table)
# MAGIC          ↓ 증분 처리
# MAGIC       silver_live_viewing (Streaming Table)
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### Bronze Streaming: 시청 이벤트 실시간 수집

# COMMAND ----------

LANDING_PATH = spark.conf.get("landing_path", f"/Volumes/{SOURCE_CATALOG}/bronze/landing")

@dp.table(
  name="bronze_live_viewing",
  comment="실시간 시청 이벤트 (Auto Loader from UC Volume)",
  table_properties={"quality": "bronze"}
)
def bronze_live_viewing():
  return (
    spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaLocation", f"{LANDING_PATH}/_schemas/viewing_events")
    .load(f"{LANDING_PATH}/viewing_events/")
    .withColumn("_ingested_at", current_timestamp())
    .withColumn("_source_file", col("_metadata.file_path"))
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Bronze Streaming: 클릭 이벤트 실시간 수집

# COMMAND ----------

@dp.table(
  name="bronze_live_clicks",
  comment="실시간 클릭 이벤트 (Auto Loader from UC Volume)",
  table_properties={"quality": "bronze"}
)
def bronze_live_clicks():
  return (
    spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaLocation", f"{LANDING_PATH}/_schemas/click_events")
    .load(f"{LANDING_PATH}/click_events/")
    .withColumn("_ingested_at", current_timestamp())
    .withColumn("_source_file", col("_metadata.file_path"))
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Bronze Streaming: 광고 이벤트 실시간 수집

# COMMAND ----------

@dp.table(
  name="bronze_live_ads",
  comment="실시간 광고 이벤트 (Auto Loader from UC Volume)",
  table_properties={"quality": "bronze"}
)
def bronze_live_ads():
  return (
    spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaLocation", f"{LANDING_PATH}/_schemas/ad_events")
    .load(f"{LANDING_PATH}/ad_events/")
    .withColumn("_ingested_at", current_timestamp())
    .withColumn("_source_file", col("_metadata.file_path"))
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Silver Streaming: 실시간 시청 이벤트 정제

# COMMAND ----------

@dp.table(
  name="silver_live_viewing",
  comment="정제된 실시간 시청 이벤트",
  table_properties={"quality": "silver"}
)
@dp.expect_or_drop("valid_device", "device_id IS NOT NULL")
@dp.expect_or_drop("valid_duration", "duration_minutes > 0 AND duration_minutes <= 480")
def silver_live_viewing():
  devices = spark.read.table("devices_sdp")
  live = spark.readStream.table("bronze_live_viewing")

  return (
    live.join(devices, "device_id", "inner")
    .withColumn("viewing_date", to_date("start_time"))
    .withColumn("viewing_hour", hour("start_time"))
    .withColumn("time_slot",
      when(hour("start_time").between(6, 11), "morning")
      .when(hour("start_time").between(12, 17), "afternoon")
      .when(hour("start_time").between(18, 22), "prime_time")
      .otherwise("late_night")
    )
    .select(
      live["*"],
      "viewing_date", "viewing_hour", "time_slot",
      devices["model_name"], devices["region"], "price_tier"
    )
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 파이프라인 설정 가이드
# MAGIC
# MAGIC 이 노트북을 SDP 파이프라인으로 실행하려면 Workflows > Pipelines에서:
# MAGIC
# MAGIC ```json
# MAGIC {
# MAGIC  "name": "<username>_smarttv_demo_pipeline",
# MAGIC  "target_catalog": "<username>_smarttv_training",
# MAGIC  "target_schema": "silver",
# MAGIC  "development": true,
# MAGIC  "serverless": true,
# MAGIC  "configuration": {
# MAGIC   "source_catalog": "<username>_smarttv_training",
# MAGIC   "landing_path": "/Volumes/<username>_smarttv_training/bronze/landing"
# MAGIC  },
# MAGIC  "notebook_paths": [
# MAGIC   "/Workspace/Users/<you>/smarttv-training/04_sdp_pipeline"
# MAGIC  ]
# MAGIC }
# MAGIC ```
# MAGIC
# MAGIC ### 레거시 DLT vs 최신 SDP API 비교
# MAGIC
# MAGIC | 항목 | 레거시 (DLT) | 최신 (SDP) |
# MAGIC |------|-------------|-----------|
# MAGIC | Import | `import dlt` | `from pyspark import pipelines as dp` |
# MAGIC | 테이블 생성 | `@dlt.table()` | `@dp.table()` |
# MAGIC | MV 생성 | `@dlt.table()` | `@dp.materialized_view()` |
# MAGIC | 읽기 | `dlt.read("table")` | `spark.read.table("table")` |
# MAGIC | 스트림 읽기 | `dlt.read_stream("table")` | `spark.readStream.table("table")` |
# MAGIC | Expectations | `@dlt.expect_or_fail()` | `@dp.expect_or_fail()` |
# MAGIC | CDC | `dlt.apply_changes()` | `dp.create_auto_cdc_flow()` |
# MAGIC
# MAGIC ### SDP가 해결하는 문제
# MAGIC
# MAGIC | CTAS 수동 방식의 한계 | SDP가 해결하는 방법 |
# MAGIC |----------------------|-------------------|
# MAGIC | 매번 전체 재계산 | Streaming Table로 증분 처리 |
# MAGIC | 테이블 순서 수동 관리 | `spark.read.table()`로 의존성 자동 해결 |
# MAGIC | 데이터 품질 별도 체크 | `@dp.expect`로 인라인 검증 |
# MAGIC | 오류 시 수동 복구 | 자동 재시도 & 체크포인트 |
# MAGIC | 스케줄링 별도 구성 | Workflows에서 통합 관리 |
# MAGIC
# MAGIC ### CTAS 결과와 비교하기
# MAGIC
# MAGIC ```sql
# MAGIC -- Silver 건수 비교
# MAGIC SELECT 'CTAS' AS method, COUNT(*) AS cnt FROM silver.devices_ctas
# MAGIC UNION ALL
# MAGIC SELECT 'SDP', COUNT(*) FROM silver.devices_sdp;
# MAGIC
# MAGIC -- Expectations로 걸러진 레코드 수는 파이프라인 UI에서 확인 가능
# MAGIC ```
