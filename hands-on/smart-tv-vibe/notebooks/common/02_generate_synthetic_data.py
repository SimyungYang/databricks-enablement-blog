# Databricks notebook source
# MAGIC %md
# MAGIC # 02. 가상 데이터 생성 — Smart TV 시나리오
# MAGIC
# MAGIC 실제 고객 데이터를 사용할 수 없으므로,**Smart TV 환경을 시뮬레이션하는 가상 데이터** 를 생성합니다.
# MAGIC 총 **170만건** 이상의 현실적인 데이터를 만들어, 이후 모든 실습의 기반이 됩니다.
# MAGIC
# MAGIC ### 생성할 테이블 4개
# MAGIC
# MAGIC | 테이블 | 건수 | 설명 | 실무에서의 원본 |
# MAGIC |--------|------|------|----------------|
# MAGIC | `bronze.devices` | 10,000 | TV 디바이스 마스터 정보 | CRM/디바이스 등록 시스템 |
# MAGIC | `bronze.viewing_logs` | 500,000 | 채널/앱 시청 기록 | TV 시청 로그 수집 서버 |
# MAGIC | `bronze.click_events` | 1,000,000 | 리모컨/UI 조작 이벤트 | webOS 이벤트 트래커 |
# MAGIC | `bronze.ad_impressions` | 200,000 | FastTV 광고 노출/클릭/전환 | 광고 서버 (Ad Exchange) |
# MAGIC
# MAGIC ### 데이터의 현실성
# MAGIC - 시간대별 시청 분포 (저녁 프라임타임 집중, 새벽 최소)
# MAGIC - 광고 형식별 차등 CTR (native 4~7%, banner 1~2%)
# MAGIC - 지역별 가중치 (Korea 25%, US 20%, EU 20% 등)
# MAGIC
# MAGIC**소요 시간:** 약 5~10분 (서버리스 컴퓨트 기준)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 공통 설정

# COMMAND ----------

# 현재 사용자 이메일에서 prefix 추출
username = spark.sql("SELECT current_user()").collect()[0][0]
user_prefix = username.split("@")[0].replace(".", "_").replace("-", "_")
CATALOG = f"{user_prefix}_smarttv_training"
SCHEMA = "bronze"

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

print(f"👤 사용자: {username}")
print(f"✅ 카탈로그: {CATALOG}, 스키마: {SCHEMA}")

# COMMAND ----------

import uuid
import random
import numpy as np
from datetime import datetime, timedelta
from pyspark.sql import functions as F
from pyspark.sql.types import *

# 재현 가능하도록 시드 고정
random.seed(42)
np.random.seed(42)

# 날짜 범위
DATE_START = datetime(2025, 1, 1)
DATE_END = datetime(2025, 3, 1)
REGISTER_START = datetime(2023, 1, 1)
REGISTER_END = datetime(2025, 3, 1)

print("✅ 공통 라이브러리 로드 완료")

# COMMAND ----------

# MAGIC %md
# MAGIC ### PySpark란?
# MAGIC
# MAGIC 이 노트북에서는 **PySpark** 를 사용하여 데이터를 생성합니다.
# MAGIC
# MAGIC -**PySpark** 는 Apache Spark의 Python API로,**여러 대의 머신에 데이터를 분산하여 병렬 처리하는 프레임워크** 입니다.
# MAGIC - pandas와 비슷한 DataFrame API를 제공하지만, pandas는 단일 머신의 메모리에 모든 데이터를 올려야 하는 반면, PySpark는 **TB(테라바이트) 규모의 데이터도 처리** 할 수 있습니다.
# MAGIC - 아래 코드에서 `spark.createDataFrame()`으로 분산 DataFrame을 만들고, `.saveAsTable()`로 **Delta Lake 테이블로 Unity Catalog에 저장** 합니다.
# MAGIC  - `saveAsTable()`은 데이터를 클라우드 스토리지에 Parquet 형식으로 쓰고, Unity Catalog에 메타데이터를 등록합니다.
# MAGIC  - 이렇게 저장하면 SQL로도, Python으로도, 다른 노트북에서도 바로 조회할 수 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 디바이스 마스터 데이터 (10,000건)
# MAGIC
# MAGIC >**이 테이블은 Dimension(차원) 테이블입니다**— 데이터 분석에서 "누구(어떤 디바이스)인가?"를 정의하는 기준 테이블입니다.
# MAGIC > 다른 모든 테이블(시청 로그, 클릭, 광고)이 이 테이블의 `device_id`를 참조합니다.
# MAGIC
# MAGIC 전 세계에 판매된 Smart TV 디바이스 정보입니다. 모든 로그 데이터의 **기준 테이블(Dimension)** 입니다.
# MAGIC
# MAGIC | 컬럼 | 타입 | 설명 | 예시 |
# MAGIC |------|------|------|------|
# MAGIC | `device_id` | STRING | 고유 디바이스 ID (UUID) | `a1b2c3d4-...` |
# MAGIC | `model_name` | STRING | TV 모델명 (10종) | `OLED65C4`, `NANO75` |
# MAGIC | `screen_size` | INT | 화면 크기 (인치) | 43, 55, 65, 75 |
# MAGIC | `region` | STRING | 판매 지역 (8개) | Korea, US, EU, Japan |
# MAGIC | `country` | STRING | 국가 코드 (15개국) | KR, US, DE, JP |
# MAGIC | `registered_at` | TIMESTAMP | 디바이스 등록일 | 2023-01-15 |
# MAGIC | `firmware_version` | STRING | webOS 버전 | webOS 24.0 |
# MAGIC | `has_fasttv` | BOOLEAN | FastTV 지원 여부 (80% true) | true |
# MAGIC | `price_tier` | STRING | 가격대 (OLED=premium, QNED=mid, UHD=entry) | premium |
# MAGIC | `subscription_tier` | STRING | 구독 등급 | free, basic, premium |

# COMMAND ----------

NUM_DEVICES = 10_000

# 모델 정보 (모델명, 화면 크기 옵션, 가격대)
MODELS = [
  ("OLED65C4", [65], "premium"),
  ("OLED55C4", [55], "premium"),
  ("OLED77G4", [77], "premium"),
  ("OLED55B4", [55], "premium"),
  ("OLED65B4", [65], "premium"),
  ("QNED85", [55, 65, 75], "mid"),
  ("QNED80", [50, 55, 65, 75], "mid"),
  ("NANO75", [43, 50, 55, 65], "mid"),
  ("UHD50UR", [43, 50, 55], "entry"),
  ("UHD43UR", [43, 50], "entry"),
]

# 지역 / 국가 매핑 (가중치 포함)
REGIONS = {
  "Korea":   (["KR"], 0.25),
  "US":     (["US"], 0.20),
  "EU":     (["DE", "FR", "GB", "IT", "ES"], 0.20),
  "Japan":   (["JP"], 0.10),
  "SEA":    (["TH", "VN", "ID", "PH", "MY"], 0.10),
  "LatAm":   (["BR", "MX", "AR"], 0.08),
  "MiddleEast": (["AE", "SA"], 0.04),
  "Oceania":  (["AU", "NZ"], 0.03),
}

FIRMWARE_VERSIONS = [f"webOS {v}" for v in ["6.0", "22.0", "23.0", "23.5", "24.0"]]
SUBSCRIPTION_TIERS = ["free", "basic", "premium"]
TIER_WEIGHTS = [0.60, 0.25, 0.15]

def generate_devices(n):
  rows = []
  region_names = list(REGIONS.keys())
  region_weights = [REGIONS[r][1] for r in region_names]

  for _ in range(n):
    device_id = str(uuid.uuid4())
    model_name, screen_sizes, price_tier = random.choice(MODELS)
    screen_size = random.choice(screen_sizes)
    region = random.choices(region_names, weights=region_weights, k=1)[0]
    countries = REGIONS[region][0]
    country = random.choice(countries)
    reg_ts = REGISTER_START + timedelta(
      seconds=random.randint(0, int((REGISTER_END - REGISTER_START).total_seconds()))
    )
    firmware = random.choice(FIRMWARE_VERSIONS)
    has_fasttv = random.random() < 0.80
    tier = random.choices(SUBSCRIPTION_TIERS, weights=TIER_WEIGHTS, k=1)[0]

    rows.append((
      device_id, model_name, screen_size, region, country,
      reg_ts.strftime("%Y-%m-%d %H:%M:%S"), firmware,
      has_fasttv, price_tier, tier
    ))
  return rows

device_rows = generate_devices(NUM_DEVICES)

device_schema = StructType([
  StructField("device_id", StringType()),
  StructField("model_name", StringType()),
  StructField("screen_size", IntegerType()),
  StructField("region", StringType()),
  StructField("country", StringType()),
  StructField("registered_at", StringType()),
  StructField("firmware_version", StringType()),
  StructField("has_fasttv", BooleanType()),
  StructField("price_tier", StringType()),
  StructField("subscription_tier", StringType()),
])

df_devices = spark.createDataFrame(device_rows, schema=device_schema)
df_devices = df_devices.withColumn("registered_at", F.to_timestamp("registered_at"))

df_devices.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.devices")

cnt = spark.table(f"{CATALOG}.{SCHEMA}.devices").count()
print(f"✅ devices 테이블 생성 완료: {cnt:,}건")

# COMMAND ----------

# 디바이스 데이터 통계 확인
display(
  spark.sql(f"""
    SELECT
      model_name,
      price_tier,
      COUNT(*) as cnt,
      ROUND(COUNT(*) * 100.0 / {NUM_DEVICES}, 1) as pct
    FROM {CATALOG}.{SCHEMA}.devices
    GROUP BY model_name, price_tier
    ORDER BY cnt DESC
  """)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. 시청 로그 데이터 (500,000건)
# MAGIC
# MAGIC >**이 테이블은 Fact(사실) 테이블입니다**— "무슨 일이 일어났는가?"를 기록하는 테이블입니다.
# MAGIC > 시청 행동이라는 "사실"을 하나하나 기록하며, 개인화 추천 모델과 콘텐츠 편성 전략의 핵심 원천 데이터가 됩니다.
# MAGIC
# MAGIC 사용자가 **무엇을 얼마나 시청했는지** 기록합니다. 개인화 추천과 콘텐츠 편성 전략의 핵심 데이터입니다.
# MAGIC
# MAGIC | 컬럼 | 타입 | 설명 | 예시 |
# MAGIC |------|------|------|------|
# MAGIC | `log_id` | STRING | 시청 로그 고유 ID | `uuid` |
# MAGIC | `device_id` | STRING | 디바이스 ID (devices FK) | `a1b2c3d4-...` |
# MAGIC | `user_profile_id` | STRING | TV 내 사용자 프로필 (가구당 1~4명) | `a1b2c3d4_user2` |
# MAGIC | `content_type` | STRING | 콘텐츠 유형 | live_tv, vod, app, fasttv |
# MAGIC | `channel_or_app` | STRING | 채널명 또는 앱명 | Netflix, MBC, YouTube |
# MAGIC | `genre` | STRING | 장르 | drama, sports, news |
# MAGIC | `start_time` | TIMESTAMP | 시청 시작 시간 | 2025-01-15 20:30:00 |
# MAGIC | `duration_minutes` | INT | 시청 시간(분), 로그정규분포 평균 45분 | 67 |
# MAGIC | `completion_rate` | DOUBLE | 콘텐츠 시청 완료율 (0.0~1.0) | 0.85 |
# MAGIC
# MAGIC**현실적 분포 적용:**
# MAGIC - 평일 저녁 6~11시에 시청의 60% 집중 (프라임타임)
# MAGIC - 주말은 오전~오후에도 분산, 새벽 2~6시는 5% 미만

# COMMAND ----------

NUM_VIEWING = 500_000

# 디바이스 ID 목록 캐싱
device_ids = [row.device_id for row in spark.table(f"{CATALOG}.{SCHEMA}.devices").select("device_id").collect()]

CONTENT_TYPES = ["live_tv", "vod", "app", "fasttv"]
CONTENT_TYPE_WEIGHTS = [0.30, 0.25, 0.30, 0.15]

CHANNELS_APPS = {
  "live_tv": ["MBC", "KBS", "SBS", "JTBC", "tvN", "MBN", "YTN", "EBS", "OCN", "Channel A"],
  "vod":   ["Netflix", "Disney+", "Tving", "Wavve", "Coupang Play", "Apple TV+", "Watcha"],
  "app":   ["YouTube", "Twitch", "Spotify", "TikTok", "Instagram", "Melon", "Bugs"],
  "fasttv": ["FastTV News", "FastTV Sports", "FastTV Movie", "FastTV Kids", "FastTV Docu",
        "FastTV Music", "FastTV Food", "FastTV Travel", "FastTV Tech", "FastTV Lifestyle"],
}

GENRES = {
  "live_tv": ["drama", "entertainment", "news", "sports", "documentary"],
  "vod":   ["drama", "movie", "entertainment", "documentary", "kids", "anime"],
  "app":   ["entertainment", "music", "sports", "education", "social"],
  "fasttv": ["news", "sports", "movie", "kids", "documentary", "music", "food", "travel"],
}

# 시간대별 시청 가중치 (0~23시)
WEEKDAY_HOUR_WEIGHTS = [
  0.02, 0.01, 0.005, 0.005, 0.005, 0.01, # 0-5시
  0.02, 0.03, 0.03, 0.02, 0.02, 0.02,   # 6-11시
  0.03, 0.02, 0.02, 0.02, 0.03, 0.04,   # 12-17시
  0.08, 0.10, 0.12, 0.12, 0.10, 0.06,   # 18-23시
]

WEEKEND_HOUR_WEIGHTS = [
  0.02, 0.01, 0.005, 0.005, 0.005, 0.01,  # 0-5시
  0.02, 0.03, 0.04, 0.05, 0.05, 0.05,   # 6-11시
  0.05, 0.05, 0.05, 0.05, 0.05, 0.05,   # 12-17시
  0.07, 0.08, 0.09, 0.09, 0.07, 0.05,   # 18-23시
]

def random_datetime_with_hour_weights(is_weekend):
  weights = WEEKEND_HOUR_WEIGHTS if is_weekend else WEEKDAY_HOUR_WEIGHTS
  # 랜덤 날짜
  days_range = (DATE_END - DATE_START).days
  rand_date = DATE_START + timedelta(days=random.randint(0, days_range - 1))
  # 요일 체크해서 주말/평일 맞추기
  actual_is_weekend = rand_date.weekday() >= 5
  if actual_is_weekend != is_weekend:
    # 주말/평일 맞추기 위해 +-1일 조정
    if is_weekend and not actual_is_weekend:
      rand_date += timedelta(days=(5 - rand_date.weekday()) % 7)
    elif not is_weekend and actual_is_weekend:
      rand_date += timedelta(days=(7 - rand_date.weekday()) % 7)
    if rand_date >= DATE_END:
      rand_date = DATE_START + timedelta(days=random.randint(0, days_range - 1))

  hour = random.choices(range(24), weights=weights, k=1)[0]
  minute = random.randint(0, 59)
  second = random.randint(0, 59)
  return rand_date.replace(hour=hour, minute=minute, second=second)

def generate_viewing_logs(n):
  rows = []
  for _ in range(n):
    device_id = random.choice(device_ids)
    user_profile_id = f"{device_id[:8]}_user{random.randint(1, 4)}"
    content_type = random.choices(CONTENT_TYPES, weights=CONTENT_TYPE_WEIGHTS, k=1)[0]
    channel_or_app = random.choice(CHANNELS_APPS[content_type])
    genre = random.choice(GENRES[content_type])

    is_weekend = random.random() < 0.35 # 35% 주말
    start_time = random_datetime_with_hour_weights(is_weekend)

    # 시청 시간: 로그 정규분포 (평균 45분, 표준편차 30분, 최소 1분, 최대 240분)
    duration = max(1, min(240, int(np.random.lognormal(mean=3.5, sigma=0.8))))
    completion_rate = round(min(1.0, max(0.0, np.random.beta(2, 1.5))), 2)

    rows.append((
      str(uuid.uuid4()), device_id, user_profile_id,
      content_type, channel_or_app, genre,
      start_time.strftime("%Y-%m-%d %H:%M:%S"),
      duration, completion_rate
    ))
  return rows

# 배치 생성 (메모리 효율)
BATCH_SIZE = 100_000
all_viewing_dfs = []

viewing_schema = StructType([
  StructField("log_id", StringType()),
  StructField("device_id", StringType()),
  StructField("user_profile_id", StringType()),
  StructField("content_type", StringType()),
  StructField("channel_or_app", StringType()),
  StructField("genre", StringType()),
  StructField("start_time", StringType()),
  StructField("duration_minutes", IntegerType()),
  StructField("completion_rate", DoubleType()),
])

for batch_num in range(NUM_VIEWING // BATCH_SIZE):
  batch_rows = generate_viewing_logs(BATCH_SIZE)
  df_batch = spark.createDataFrame(batch_rows, schema=viewing_schema)
  all_viewing_dfs.append(df_batch)
  print(f" 배치 {batch_num + 1}/{NUM_VIEWING // BATCH_SIZE} 생성 완료")

from functools import reduce
df_viewing = reduce(lambda a, b: a.unionAll(b), all_viewing_dfs)
df_viewing = df_viewing.withColumn("start_time", F.to_timestamp("start_time"))

df_viewing.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.viewing_logs")

cnt = spark.table(f"{CATALOG}.{SCHEMA}.viewing_logs").count()
print(f"✅ viewing_logs 테이블 생성 완료: {cnt:,}건")

# COMMAND ----------

# 시청 로그 통계
display(
  spark.sql(f"""
    SELECT
      content_type,
      COUNT(*) as total_views,
      ROUND(AVG(duration_minutes), 1) as avg_duration,
      ROUND(AVG(completion_rate), 2) as avg_completion
    FROM {CATALOG}.{SCHEMA}.viewing_logs
    GROUP BY content_type
    ORDER BY total_views DESC
  """)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 이벤트/클릭 로그 (1,000,000건)
# MAGIC
# MAGIC >**이 테이블은 사용자의 TV UI 인터랙션을 캡처합니다**— UX 분석의 핵심 데이터입니다.
# MAGIC > "사용자가 홈 화면에서 어떤 배너를 클릭했는지", "검색을 얼마나 자주 사용하는지" 등을 분석하여
# MAGIC > UI 레이아웃 최적화, A/B 테스트, 전환 퍼널 분석에 활용합니다.
# MAGIC
# MAGIC 사용자가 TV UI에서 **어떤 버튼을 누르고, 어떤 화면을 탐색했는지** 기록합니다.
# MAGIC UX 개선, 콘텐츠 소비 퍼널 분석, 광고 클릭 추적에 사용됩니다.
# MAGIC
# MAGIC | 컬럼 | 타입 | 설명 | 예시 |
# MAGIC |------|------|------|------|
# MAGIC | `event_id` | STRING | 이벤트 고유 ID | `uuid` |
# MAGIC | `device_id` | STRING | 디바이스 ID (devices FK) | `a1b2c3d4-...` |
# MAGIC | `user_profile_id` | STRING | 사용자 프로필 | `a1b2c3d4_user1` |
# MAGIC | `event_timestamp` | TIMESTAMP | 이벤트 발생 시간 | 2025-02-01 19:15:33 |
# MAGIC | `event_type` | STRING | 이벤트 유형 (11종) | app_launch, ad_click, search |
# MAGIC | `screen_name` | STRING | 현재 화면 (7종) | home, fasttv, app_store |
# MAGIC | `element_id` | STRING | 클릭한 UI 요소 | banner_01, app_icon_netflix |
# MAGIC | `session_id` | STRING | 세션 ID (전원ON~OFF) | `a1b2c3d4e5f6` |

# COMMAND ----------

NUM_CLICKS = 1_000_000

EVENT_TYPES = [
  "app_launch", "channel_change", "search", "banner_click",
  "ad_click", "menu_navigate", "content_select", "voice_command",
  "settings_change", "power_on", "power_off"
]
EVENT_TYPE_WEIGHTS = [0.15, 0.18, 0.08, 0.07, 0.05, 0.12, 0.15, 0.04, 0.03, 0.07, 0.06]

SCREEN_NAMES = ["home", "fasttv", "app_store", "settings", "search", "channel_guide", "content_detail"]
SCREEN_WEIGHTS = [0.30, 0.20, 0.12, 0.05, 0.10, 0.13, 0.10]

ELEMENT_IDS = {
  "home":      ["banner_01", "banner_02", "banner_03", "app_icon_netflix", "app_icon_youtube",
            "app_icon_tving", "recommended_01", "recommended_02", "continue_watching_01"],
  "fasttv":     ["channel_card_01", "channel_card_02", "channel_card_03", "ad_slot_top",
            "ad_slot_side", "genre_filter", "search_bar", "favorites_btn"],
  "app_store":   ["app_tile_01", "app_tile_02", "app_tile_03", "category_tab", "search_btn",
            "install_btn", "update_btn"],
  "settings":    ["network_btn", "display_btn", "sound_btn", "account_btn", "privacy_btn",
            "about_btn"],
  "search":     ["search_input", "voice_search_btn", "suggestion_01", "suggestion_02",
            "result_01", "result_02", "result_03"],
  "channel_guide": ["channel_row_01", "channel_row_02", "channel_row_03", "time_nav_left",
            "time_nav_right", "genre_filter", "favorites_tab"],
  "content_detail": ["play_btn", "add_to_list_btn", "share_btn", "trailer_btn", "season_selector",
            "episode_01", "episode_02", "related_01"],
}

def generate_click_events(n):
  rows = []
  # 세션 관리
  session_map = {}

  for _ in range(n):
    device_id = random.choice(device_ids)
    user_profile_id = f"{device_id[:8]}_user{random.randint(1, 4)}"
    event_type = random.choices(EVENT_TYPES, weights=EVENT_TYPE_WEIGHTS, k=1)[0]
    screen_name = random.choices(SCREEN_NAMES, weights=SCREEN_WEIGHTS, k=1)[0]
    element_id = random.choice(ELEMENT_IDS[screen_name])

    is_weekend = random.random() < 0.35
    event_ts = random_datetime_with_hour_weights(is_weekend)

    # 세션 ID: 같은 디바이스의 power_on ~ power_off
    if event_type == "power_on" or device_id not in session_map:
      session_map[device_id] = str(uuid.uuid4())[:12]
    session_id = session_map.get(device_id, str(uuid.uuid4())[:12])
    if event_type == "power_off":
      session_map.pop(device_id, None)

    rows.append((
      str(uuid.uuid4()), device_id, user_profile_id,
      event_ts.strftime("%Y-%m-%d %H:%M:%S"),
      event_type, screen_name, element_id, session_id
    ))
  return rows

click_schema = StructType([
  StructField("event_id", StringType()),
  StructField("device_id", StringType()),
  StructField("user_profile_id", StringType()),
  StructField("event_timestamp", StringType()),
  StructField("event_type", StringType()),
  StructField("screen_name", StringType()),
  StructField("element_id", StringType()),
  StructField("session_id", StringType()),
])

BATCH_SIZE_CLICK = 200_000
all_click_dfs = []

for batch_num in range(NUM_CLICKS // BATCH_SIZE_CLICK):
  batch_rows = generate_click_events(BATCH_SIZE_CLICK)
  df_batch = spark.createDataFrame(batch_rows, schema=click_schema)
  all_click_dfs.append(df_batch)
  print(f" 배치 {batch_num + 1}/{NUM_CLICKS // BATCH_SIZE_CLICK} 생성 완료")

df_clicks = reduce(lambda a, b: a.unionAll(b), all_click_dfs)
df_clicks = df_clicks.withColumn("event_timestamp", F.to_timestamp("event_timestamp"))

df_clicks.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.click_events")

cnt = spark.table(f"{CATALOG}.{SCHEMA}.click_events").count()
print(f"✅ click_events 테이블 생성 완료: {cnt:,}건")

# COMMAND ----------

# 클릭 이벤트 통계
display(
  spark.sql(f"""
    SELECT
      event_type,
      COUNT(*) as total_events,
      COUNT(DISTINCT device_id) as unique_devices
    FROM {CATALOG}.{SCHEMA}.click_events
    GROUP BY event_type
    ORDER BY total_events DESC
  """)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. FastTV 광고 로그 (200,000건)
# MAGIC
# MAGIC >**이 테이블은 수익(Revenue) 데이터입니다**— 광고 1건이 노출될 때마다, 클릭 여부와 전환(구매/설치) 여부를 기록합니다.
# MAGIC > Smart TV 플랫폼의 핵심 비즈니스 모델이며, 이 데이터를 기반으로 광고 단가(eCPM)를 산정하고 광고주에게 리포트를 제공합니다.
# MAGIC
# MAGIC 핵심 수익 모델인 **FastTV 광고의 노출/클릭/전환 데이터** 입니다.
# MAGIC 광고주별 성과 분석, 시간대별 eCPM 최적화, 광고 슬롯 가격 책정에 사용됩니다.
# MAGIC
# MAGIC | 컬럼 | 타입 | 설명 | 예시 |
# MAGIC |------|------|------|------|
# MAGIC | `impression_id` | STRING | 광고 노출 고유 ID | `uuid` |
# MAGIC | `device_id` | STRING | 디바이스 ID (devices FK) | `a1b2c3d4-...` |
# MAGIC | `ad_id` | STRING | 광고 소재 ID (200종) | ad_042 |
# MAGIC | `advertiser` | STRING | 광고주 (30개 한국 기업) | 삼성전자, 쿠팡, 네이버 |
# MAGIC | `ad_category` | STRING | 광고 카테고리 | electronics, ecommerce |
# MAGIC | `ad_format` | STRING | 광고 형식 (6종) | banner, video_pre_roll, native |
# MAGIC | `placement` | STRING | 노출 위치 (5종) | fasttv_home, app_launch |
# MAGIC | `impression_timestamp` | TIMESTAMP | 노출 시간 | 2025-01-20 21:05:12 |
# MAGIC | `was_clicked` | BOOLEAN | 클릭 여부 (형식별 차등 CTR) | true |
# MAGIC | `was_converted` | BOOLEAN | 전환 여부 (클릭 중 10~20%) | false |
# MAGIC | `bid_price_usd` | DOUBLE | 입찰가 ($) | 0.035 |
# MAGIC | `win_price_usd` | DOUBLE | 낙찰가 (=수익, 입찰의 60~90%) | 0.028 |
# MAGIC
# MAGIC**광고 형식별 현실적 CTR:**
# MAGIC `native(4~7%)` > `video_pre_roll(3~5%)` > `banner(1~2%)` > `screensaver(0.5~1%)`

# COMMAND ----------

NUM_ADS = 200_000

ADVERTISERS = [
  "삼성전자", "현대자동차", "CJ제일제당", "신한카드", "쿠팡",
  "네이버", "카카오", "SK텔레콤", "KT", "LG생활건강",
  "아모레퍼시픽", "롯데칠성", "하이트진로", "대한항공", "신세계",
  "배달의민족", "토스", "당근마켓", "마켓컬리", "야놀자",
  "무신사", "오늘의집", "리디", "넷마블", "크래프톤",
  "한화생명", "삼성생명", "현대해상", "기아", "볼보코리아",
]

AD_CATEGORIES = {
  "삼성전자": "electronics", "현대자동차": "automotive", "CJ제일제당": "food",
  "신한카드": "finance", "쿠팡": "ecommerce", "네이버": "tech",
  "카카오": "tech", "SK텔레콤": "telecom", "KT": "telecom",
  "LG생활건강": "beauty", "아모레퍼시픽": "beauty", "롯데칠성": "food",
  "하이트진로": "food", "대한항공": "travel", "신세계": "ecommerce",
  "배달의민족": "food", "토스": "finance", "당근마켓": "ecommerce",
  "마켓컬리": "ecommerce", "야놀자": "travel", "무신사": "fashion",
  "오늘의집": "lifestyle", "리디": "entertainment", "넷마블": "gaming",
  "크래프톤": "gaming", "한화생명": "finance", "삼성생명": "finance",
  "현대해상": "finance", "기아": "automotive", "볼보코리아": "automotive",
}

AD_FORMATS = ["banner", "video_pre_roll", "video_mid_roll", "native", "interstitial", "screensaver"]
AD_FORMAT_WEIGHTS = [0.30, 0.20, 0.10, 0.15, 0.10, 0.15]

# 광고 형식별 CTR 범위
CTR_RANGES = {
  "banner":     (0.01, 0.02),
  "video_pre_roll": (0.03, 0.05),
  "video_mid_roll": (0.02, 0.04),
  "native":     (0.04, 0.07),
  "interstitial":  (0.02, 0.04),
  "screensaver":  (0.005, 0.01),
}

PLACEMENTS = ["fasttv_home", "fasttv_channel", "app_launch", "channel_guide", "screensaver"]
PLACEMENT_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.10]

AD_DURATIONS = [15, 30, 60]
AD_DURATION_WEIGHTS = [0.40, 0.40, 0.20]

def generate_ad_impressions(n):
  rows = []
  for _ in range(n):
    device_id = random.choice(device_ids)
    user_profile_id = f"{device_id[:8]}_user{random.randint(1, 4)}"
    ad_id = f"ad_{random.randint(1, 200):03d}"
    advertiser = random.choice(ADVERTISERS)
    ad_category = AD_CATEGORIES.get(advertiser, "other")
    ad_format = random.choices(AD_FORMATS, weights=AD_FORMAT_WEIGHTS, k=1)[0]
    placement = random.choices(PLACEMENTS, weights=PLACEMENT_WEIGHTS, k=1)[0]

    is_weekend = random.random() < 0.35
    impression_ts = random_datetime_with_hour_weights(is_weekend)

    # CTR은 광고 형식에 따라 다름
    ctr_min, ctr_max = CTR_RANGES[ad_format]
    was_clicked = random.random() < random.uniform(ctr_min, ctr_max)

    click_ts = None
    was_converted = False
    if was_clicked:
      # 클릭까지 소요 시간: 1~30초
      click_delay = random.randint(1, 30)
      click_dt = impression_ts + timedelta(seconds=click_delay)
      click_ts = click_dt.strftime("%Y-%m-%d %H:%M:%S")
      # 전환율: 클릭 중 10~20%
      was_converted = random.random() < random.uniform(0.10, 0.20)

    bid_price = round(random.uniform(0.001, 0.05), 4)
    win_price = round(bid_price * random.uniform(0.60, 0.90), 4)
    duration = random.choices(AD_DURATIONS, weights=AD_DURATION_WEIGHTS, k=1)[0]

    rows.append((
      str(uuid.uuid4()), device_id, user_profile_id,
      ad_id, advertiser, ad_category, ad_format, placement,
      impression_ts.strftime("%Y-%m-%d %H:%M:%S"),
      was_clicked, click_ts, was_converted,
      bid_price, win_price, duration
    ))
  return rows

ad_schema = StructType([
  StructField("impression_id", StringType()),
  StructField("device_id", StringType()),
  StructField("user_profile_id", StringType()),
  StructField("ad_id", StringType()),
  StructField("advertiser", StringType()),
  StructField("ad_category", StringType()),
  StructField("ad_format", StringType()),
  StructField("placement", StringType()),
  StructField("impression_timestamp", StringType()),
  StructField("was_clicked", BooleanType()),
  StructField("click_timestamp", StringType()),
  StructField("was_converted", BooleanType()),
  StructField("bid_price_usd", DoubleType()),
  StructField("win_price_usd", DoubleType()),
  StructField("duration_seconds", IntegerType()),
])

BATCH_SIZE_AD = 100_000
all_ad_dfs = []

for batch_num in range(NUM_ADS // BATCH_SIZE_AD):
  batch_rows = generate_ad_impressions(BATCH_SIZE_AD)
  df_batch = spark.createDataFrame(batch_rows, schema=ad_schema)
  all_ad_dfs.append(df_batch)
  print(f" 배치 {batch_num + 1}/{NUM_ADS // BATCH_SIZE_AD} 생성 완료")

df_ads = reduce(lambda a, b: a.unionAll(b), all_ad_dfs)
df_ads = (
  df_ads
  .withColumn("impression_timestamp", F.to_timestamp("impression_timestamp"))
  .withColumn("click_timestamp", F.to_timestamp("click_timestamp"))
)

df_ads.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.ad_impressions")

cnt = spark.table(f"{CATALOG}.{SCHEMA}.ad_impressions").count()
print(f"✅ ad_impressions 테이블 생성 완료: {cnt:,}건")

# COMMAND ----------

# 광고 로그 통계
display(
  spark.sql(f"""
    SELECT
      ad_format,
      COUNT(*) as impressions,
      SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END) as clicks,
      ROUND(SUM(CASE WHEN was_clicked THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as ctr_pct,
      ROUND(AVG(win_price_usd), 4) as avg_win_price
    FROM {CATALOG}.{SCHEMA}.ad_impressions
    GROUP BY ad_format
    ORDER BY impressions DESC
  """)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. 전체 데이터 검증
# MAGIC
# MAGIC 생성된 모든 테이블의 건수를 확인하고, 테이블 간 **참조 무결성**(device_id 연결)을 검증합니다.
# MAGIC 데이터 파이프라인에서 이런 검증은 필수입니다 — 원본이 잘못되면 이후 모든 분석이 틀립니다.
# MAGIC
# MAGIC ### 참조 무결성(Referential Integrity)이란?
# MAGIC
# MAGIC 시청 로그, 클릭 이벤트, 광고 로그의 `device_id`가 반드시 `devices` 테이블에 존재해야 합니다.
# MAGIC 만약 존재하지 않는 `device_id`를 참조하는 레코드("고아 레코드", orphan record)가 있다면:
# MAGIC
# MAGIC -**JOIN 시 데이터 누락**: `devices`와 JOIN하면 해당 로그가 사라져 분석 결과가 왜곡됩니다.
# MAGIC -**잘못된 집계**: 디바이스 속성(지역, 모델명 등)과 연결할 수 없어 비즈니스 인사이트를 얻을 수 없습니다.
# MAGIC -**디버깅 난이도 증가**: 데이터가 많아질수록 원인을 추적하기 어려워지므로, 생성 단계에서 미리 검증하는 것이 핵심입니다.
# MAGIC
# MAGIC 아래 코드는 각 테이블의 `device_id`를 `devices` 테이블과 LEFT JOIN하여, 매칭되지 않는 레코드가 0건인지 확인합니다.

# COMMAND ----------

# 전체 테이블 요약
tables = ["devices", "viewing_logs", "click_events", "ad_impressions"]

summary_rows = []
for t in tables:
  full_name = f"{CATALOG}.{SCHEMA}.{t}"
  cnt = spark.table(full_name).count()
  cols = len(spark.table(full_name).columns)
  summary_rows.append((t, cnt, cols))

df_summary = spark.createDataFrame(summary_rows, ["table_name", "row_count", "column_count"])
display(df_summary)

# COMMAND ----------

# 참조 무결성 검증: 다른 테이블의 device_id가 devices에 존재하는지
for t in ["viewing_logs", "click_events", "ad_impressions"]:
  result = spark.sql(f"""
    SELECT COUNT(*) as orphan_count
    FROM {CATALOG}.{SCHEMA}.{t} t
    LEFT JOIN {CATALOG}.{SCHEMA}.devices d ON t.device_id = d.device_id
    WHERE d.device_id IS NULL
  """).collect()[0]["orphan_count"]
  status = "✅" if result == 0 else f"⚠️ {result}건 불일치"
  print(f" {t} → devices 참조 무결성: {status}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ 데이터 생성 완료!
# MAGIC
# MAGIC | 테이블 | 건수 | 내용 |
# MAGIC |--------|------|------|
# MAGIC | `{카탈로그}.bronze.devices` | 10,000 | TV 디바이스 마스터 |
# MAGIC | `{카탈로그}.bronze.viewing_logs` | 500,000 | 시청 로그 |
# MAGIC | `{카탈로그}.bronze.click_events` | 1,000,000 | UI 이벤트/클릭 로그 |
# MAGIC | `{카탈로그}.bronze.ad_impressions` | 200,000 | FastTV 광고 노출/클릭/전환 |
# MAGIC
# MAGIC ### 다음 단계
# MAGIC - Module 2의 Data Engineering 실습에서 Bronze → Silver → Gold 파이프라인을 구축합니다.
# MAGIC - Claude Code에서 자연어로 파이프라인 구축을 요청할 수 있습니다.
