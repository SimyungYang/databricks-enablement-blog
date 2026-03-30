# Databricks notebook source
# MAGIC %md
# MAGIC # 07. Structured Streaming — 실시간 데이터 처리
# MAGIC
# MAGIC 이 노트북에서는 UC Volume에 주기적으로 이벤트 데이터를 생성하고,
# MAGIC Auto Loader + Structured Streaming으로 실시간 Bronze → Silver → Gold 처리를 구현합니다.
# MAGIC
# MAGIC**사전 조건:**01, 02 노트북을 먼저 실행하여 카탈로그/스키마/데이터가 준비되어 있어야 합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: 환경 변수 설정

# COMMAND ----------

import re
username = spark.sql("SELECT current_user()").first()[0]
user_prefix = re.sub(r'[^a-zA-Z0-9]', '_', username.split('@')[0])
CATALOG = f"{user_prefix}_smarttv_training"
print(f"카탈로그: {CATALOG}")

spark.sql(f"USE CATALOG {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Volume & Landing Zone 생성

# COMMAND ----------

spark.sql(f"""
CREATE VOLUME IF NOT EXISTS {CATALOG}.bronze.landing_zone
COMMENT 'Landing zone for streaming events'
""")

# Landing Zone 디렉토리 구조 생성
import os

volume_path = f"/Volumes/{CATALOG}/bronze/landing_zone"
for event_type in ["viewing_events", "click_events", "ad_events"]:
  dir_path = f"{volume_path}/{event_type}"
  dbutils.fs.mkdirs(dir_path)
  print(f"Created: {dir_path}")

# 디렉토리 확인
display(dbutils.fs.ls(volume_path))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: 이벤트 생성기 함수

# COMMAND ----------

import json
import random
import uuid
from datetime import datetime, timedelta

# 기존 devices에서 device_id 목록 가져오기
device_ids = [row.device_id for row in spark.sql(f"SELECT device_id FROM {CATALOG}.bronze.devices").collect()]
print(f"사용 가능한 디바이스: {len(device_ids)}대")

# 이벤트 생성 설정
CHANNELS = ["MBC", "KBS", "SBS", "Netflix", "YouTube", "Disney+", "Tving", "Coupang Play", "JTBC", "tvN"]
GENRES = ["drama", "entertainment", "news", "sports", "movie", "kids", "documentary"]
CONTENT_TYPES = ["live_tv", "vod", "app", "fasttv"]
EVENT_TYPES = ["app_launch", "channel_change", "search", "banner_click", "ad_click",
        "menu_navigate", "content_select", "voice_command", "settings_change", "power_on", "power_off"]
SCREEN_NAMES = ["home", "fasttv", "app_store", "settings", "search", "channel_guide", "content_detail"]
ADVERTISERS = ["삼성전자", "현대자동차", "CJ제일제당", "신한카드", "쿠팡", "네이버", "카카오",
        "LG생활건강", "SK텔레콤", "농심", "오리온", "아모레퍼시픽", "한국타이어"]
AD_FORMATS = ["banner", "video_pre_roll", "video_mid_roll", "native", "interstitial", "screensaver"]

def generate_viewing_events(batch_size=100):
  events = []
  now = datetime.now()
  for _ in range(batch_size):
    events.append({
      "event_id": str(uuid.uuid4()),
      "device_id": random.choice(device_ids),
      "user_profile_id": str(random.randint(1, 4)),
      "content_type": random.choice(CONTENT_TYPES),
      "channel_or_app": random.choice(CHANNELS),
      "genre": random.choice(GENRES),
      "start_time": (now - timedelta(minutes=random.randint(0, 60))).isoformat(),
      "duration_minutes": max(1, int(random.lognormvariate(3.5, 0.8))),
      "completion_rate": round(random.random(), 2),
      "event_timestamp": now.isoformat()
    })
  return events

def generate_click_events(batch_size=200):
  events = []
  now = datetime.now()
  session_id = str(uuid.uuid4())[:8]
  for _ in range(batch_size):
    events.append({
      "event_id": str(uuid.uuid4()),
      "device_id": random.choice(device_ids),
      "user_profile_id": str(random.randint(1, 4)),
      "event_timestamp": (now - timedelta(seconds=random.randint(0, 3600))).isoformat(),
      "event_type": random.choice(EVENT_TYPES),
      "screen_name": random.choice(SCREEN_NAMES),
      "element_id": f"element_{random.randint(1, 50)}",
      "session_id": f"session_{session_id}_{random.randint(1, 20)}"
    })
  return events

def generate_ad_events(batch_size=50):
  events = []
  now = datetime.now()
  for _ in range(batch_size):
    was_clicked = random.random() < 0.03 # ~3% CTR
    events.append({
      "impression_id": str(uuid.uuid4()),
      "device_id": random.choice(device_ids),
      "user_profile_id": str(random.randint(1, 4)),
      "advertiser": random.choice(ADVERTISERS),
      "ad_format": random.choice(AD_FORMATS),
      "placement": random.choice(["fasttv_home", "fasttv_channel", "app_launch", "channel_guide", "screensaver"]),
      "impression_timestamp": now.isoformat(),
      "was_clicked": was_clicked,
      "click_timestamp": (now + timedelta(seconds=random.randint(1, 30))).isoformat() if was_clicked else None,
      "was_converted": was_clicked and random.random() < 0.15,
      "bid_price_usd": round(random.uniform(0.001, 0.05), 4),
      "win_price_usd": round(random.uniform(0.001, 0.04), 4)
    })
  return events

print("이벤트 생성기 함수 준비 완료")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: 이벤트 배치 생성 및 Volume에 저장

# COMMAND ----------

def write_events_to_volume(events, event_type):
  """이벤트를 JSON Lines 형식으로 Volume에 저장"""
  now = datetime.now()
  batch_id = now.strftime("%Y%m%d_%H%M%S")
  filename = f"{event_type}_{batch_id}.json"
  filepath = f"/Volumes/{CATALOG}/bronze/landing_zone/{event_type}/{filename}"

  # JSON Lines 형식 (한 줄에 하나의 JSON 객체)
  content = "\n".join([json.dumps(e, ensure_ascii=False) for e in events])
  dbutils.fs.put(filepath, content, overwrite=True)
  return filepath, len(events)

# 첫 번째 배치 생성
viewing = generate_viewing_events(100)
clicks = generate_click_events(200)
ads = generate_ad_events(50)

f1, c1 = write_events_to_volume(viewing, "viewing_events")
f2, c2 = write_events_to_volume(clicks, "click_events")
f3, c3 = write_events_to_volume(ads, "ad_events")

print(f"시청 이벤트: {c1}건 → {f1}")
print(f"클릭 이벤트: {c2}건 → {f2}")
print(f"광고 이벤트: {c3}건 → {f3}")

# COMMAND ----------

# Volume에 파일이 잘 저장되었는지 확인
for event_type in ["viewing_events", "click_events", "ad_events"]:
  files = dbutils.fs.ls(f"/Volumes/{CATALOG}/bronze/landing_zone/{event_type}/")
  print(f"\n{event_type}: {len(files)}개 파일")
  for f in files[:3]:
    print(f" {f.name} ({f.size} bytes)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Auto Loader로 스트리밍 수집

# COMMAND ----------

# 시청 이벤트 Auto Loader 수집
viewing_stream = (
  spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.inferColumnTypes", "true")
  .option("cloudFiles.schemaLocation", f"/Volumes/{CATALOG}/bronze/landing_zone/_schema/viewing")
  .load(f"/Volumes/{CATALOG}/bronze/landing_zone/viewing_events/")
  .withColumn("_ingested_at", F.current_timestamp())
  .withColumn("_source_file", F.input_file_name())
)

from pyspark.sql import functions as F

# Bronze 테이블에 쓰기 (append 모드)
query_viewing = (
  viewing_stream
  .writeStream
  .format("delta")
  .outputMode("append")
  .option("checkpointLocation", f"/Volumes/{CATALOG}/bronze/landing_zone/_checkpoints/viewing")
  .toTable(f"{CATALOG}.bronze.live_viewing_events")
)

print("시청 이벤트 스트리밍 수집 시작...")

# COMMAND ----------

# 클릭 이벤트 Auto Loader
from pyspark.sql import functions as F

click_stream = (
  spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.inferColumnTypes", "true")
  .option("cloudFiles.schemaLocation", f"/Volumes/{CATALOG}/bronze/landing_zone/_schema/clicks")
  .load(f"/Volumes/{CATALOG}/bronze/landing_zone/click_events/")
  .withColumn("_ingested_at", F.current_timestamp())
  .withColumn("_source_file", F.input_file_name())
)

query_clicks = (
  click_stream
  .writeStream
  .format("delta")
  .outputMode("append")
  .option("checkpointLocation", f"/Volumes/{CATALOG}/bronze/landing_zone/_checkpoints/clicks")
  .toTable(f"{CATALOG}.bronze.live_click_events")
)

print("클릭 이벤트 스트리밍 수집 시작...")

# COMMAND ----------

# 광고 이벤트 Auto Loader
ad_stream = (
  spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.inferColumnTypes", "true")
  .option("cloudFiles.schemaLocation", f"/Volumes/{CATALOG}/bronze/landing_zone/_schema/ads")
  .load(f"/Volumes/{CATALOG}/bronze/landing_zone/ad_events/")
  .withColumn("_ingested_at", F.current_timestamp())
  .withColumn("_source_file", F.input_file_name())
)

query_ads = (
  ad_stream
  .writeStream
  .format("delta")
  .outputMode("append")
  .option("checkpointLocation", f"/Volumes/{CATALOG}/bronze/landing_zone/_checkpoints/ads")
  .toTable(f"{CATALOG}.bronze.live_ad_events")
)

print("광고 이벤트 스트리밍 수집 시작...")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: 추가 배치 생성 (스트리밍 테스트)

# COMMAND ----------

import time

# 3배치 더 생성하여 스트리밍이 자동으로 수집하는지 확인
for i in range(3):
  viewing = generate_viewing_events(100)
  clicks = generate_click_events(200)
  ads = generate_ad_events(50)

  write_events_to_volume(viewing, "viewing_events")
  write_events_to_volume(clicks, "click_events")
  write_events_to_volume(ads, "ad_events")

  print(f"배치 {i+1} 생성 완료")
  time.sleep(5)

print("\n3배치 추가 생성 완료! Auto Loader가 자동으로 수집합니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: 수집 결과 확인

# COMMAND ----------

# 잠시 대기 후 결과 확인
time.sleep(10)

print("=== 실시간 수집 결과 ===")
for table_name in ["live_viewing_events", "live_click_events", "live_ad_events"]:
  count = spark.sql(f"SELECT COUNT(*) as cnt FROM {CATALOG}.bronze.{table_name}").first().cnt
  print(f" {table_name}: {count:,}건")

# COMMAND ----------

# 최근 수집된 데이터 샘플
display(spark.sql(f"""
SELECT event_id, device_id, content_type, channel_or_app, genre,
    duration_minutes, _ingested_at, _source_file
FROM {CATALOG}.bronze.live_viewing_events
ORDER BY _ingested_at DESC
LIMIT 10
"""))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8: 스트림 정리

# COMMAND ----------

# 스트리밍 쿼리 중지
for q in spark.streams.active:
  print(f"Stopping: {q.name}")
  q.stop()

print("모든 스트리밍 쿼리 중지 완료")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 학습 정리
# MAGIC
# MAGIC | 개념 | 실습 내용 |
# MAGIC |------|-----------|
# MAGIC |**UC Volume**| 파일 기반 Landing Zone 생성 |
# MAGIC |**이벤트 생성기**| JSON Lines 형식으로 시청/클릭/광고 이벤트 생성 |
# MAGIC |**Auto Loader**| cloudFiles 포맷, 새 파일 자동 감지, 스키마 추론 |
# MAGIC |**Structured Streaming**| readStream → writeStream, append 모드, 체크포인트 |
# MAGIC |**실시간 모니터링**| 수집 건수, 최근 데이터 확인 |
# MAGIC
# MAGIC**다음 단계:**SDP 파이프라인에서 이 스트리밍 테이블을 활용하려면 04_sdp_pipeline.py 참고
