# Databricks notebook source
# MAGIC %md
# MAGIC # 06. 실시간 이벤트 생성기 - Databricks App 배포
# MAGIC
# MAGIC 스마트TV 이벤트를 실시간으로 생성하여 UC Volume에 JSON 파일로 적재하는
# MAGIC**Databricks App** 을 배포합니다.
# MAGIC
# MAGIC ### End-to-End 데이터 흐름
# MAGIC
# MAGIC ```
# MAGIC 이 App (FastAPI)     UC Volume       SDP Pipeline (04)     Dashboard (05)
# MAGIC ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
# MAGIC │ 이벤트 생성  │────→│ JSON 파일  │────→│ Auto Loader   │────→│ 실시간 반영  │
# MAGIC │ 시청/클릭/광고 │   │ landing/   │   │ → Bronze ST   │   │ Gold → 대시보드│
# MAGIC │ (1~10건/초) │   │ *.json   │   │ → Silver ST   │   │       │
# MAGIC └──────────────┘   └──────────────┘   │ → Gold MV    │   └──────────────┘
# MAGIC                      └──────────────────┘
# MAGIC ```
# MAGIC
# MAGIC ### 이 노트북에서 배우는 것
# MAGIC
# MAGIC | Databricks 기능 | 설명 |
# MAGIC |----------------|------|
# MAGIC |**Databricks Apps**| FastAPI 웹앱을 Databricks에 배포 — 별도 서버 불필요 |
# MAGIC |**UC Volume**| 파일 기반 데이터 랜딩존 (실무에서 S3/ADLS 역할) |
# MAGIC |**Auto Loader**| 새 파일 자동 감지 → Streaming Table로 수집 |
# MAGIC |**SDP Streaming Table**| 증분 처리의 진정한 가치를 실시간으로 체험 |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 공통 설정

# COMMAND ----------

username = spark.sql("SELECT current_user()").collect()[0][0]
user_prefix = username.split("@")[0].replace(".", "_").replace("-", "_")
CATALOG = f"{user_prefix}_smarttv_training"
LANDING_BASE = f"/Volumes/{CATALOG}/bronze/landing"
APP_NAME = f"{user_prefix}-smarttv-generator"

print(f"👤 사용자: {username}")
print(f"📦 카탈로그: {CATALOG}")
print(f"📁 랜딩존: {LANDING_BASE}")
print(f"🚀 앱 이름: {APP_NAME}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: 랜딩존 Volume 확인
# MAGIC
# MAGIC 01 노트북에서 생성한 Volume과 디렉토리가 존재하는지 확인합니다.

# COMMAND ----------

# Volume 존재 확인
for subdir in ["viewing_events", "click_events", "ad_events"]:
  path = f"{LANDING_BASE}/{subdir}"
  try:
    files = dbutils.fs.ls(path)
    print(f" ✅ {path} ({len(files)}개 파일)")
  except Exception as e:
    print(f" ⚠️ {path} - 없음 (01 노트북을 먼저 실행하세요)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Claude Code로 App 배포하기
# MAGIC
# MAGIC 아래 프롬프트를 Claude Code에 붙여넣어 앱을 배포합니다.
# MAGIC
# MAGIC ```
# MAGIC Databricks App을 배포해줘.
# MAGIC
# MAGIC 앱 소스: notebooks/06_event_generator_app/ 폴더
# MAGIC 앱 이름: {사용자}_smarttv_generator
# MAGIC
# MAGIC 이 앱은 FastAPI로 스마트TV 이벤트를 실시간 생성하여
# MAGIC UC Volume (/Volumes/{카탈로그}/bronze/landing/)에 JSON 파일로 적재하는 앱이야.
# MAGIC
# MAGIC 배포하고 URL 알려줘.
# MAGIC ```
# MAGIC
# MAGIC ### 또는 Databricks CLI로 직접 배포:
# MAGIC
# MAGIC ```bash
# MAGIC # 앱 소스 업로드
# MAGIC databricks workspace import-dir \
# MAGIC  notebooks/06_event_generator_app/ \
# MAGIC  /Workspace/Users/{email}/smarttv-training/06_event_generator_app/ \
# MAGIC  --profile e2-demo-west
# MAGIC
# MAGIC # 앱 생성 및 배포
# MAGIC databricks apps create {username}-smarttv-generator \
# MAGIC  --profile e2-demo-west
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: 앱 테스트 - 1회 배치 생성
# MAGIC
# MAGIC 앱을 배포하기 전에 노트북에서 직접 이벤트를 생성해 테스트할 수 있습니다.

# COMMAND ----------

import json
import uuid
import random
from datetime import datetime

# 02 노트북에서 생성한 device_id 목록 로드
device_ids = [row.device_id for row in spark.table(f"{CATALOG}.bronze.devices").select("device_id").limit(500).collect()]
print(f"✅ {len(device_ids)}개 디바이스 ID 로드")

# COMMAND ----------

def generate_test_viewing_events(n=50):
  """시청 이벤트 N개 생성"""
  content_types = ["live_tv", "vod", "app", "fasttv"]
  channels = {"live_tv": ["MBC", "KBS", "SBS"], "vod": ["Netflix", "Tving"], "app": ["YouTube"], "fasttv": ["FastTV News", "FastTV Sports"]}
  genres = ["drama", "entertainment", "news", "sports", "movie"]
  events = []
  for _ in range(n):
    did = random.choice(device_ids)
    ct = random.choice(content_types)
    events.append({
      "log_id": str(uuid.uuid4()),
      "device_id": did,
      "user_profile_id": f"{did[:8]}_user{random.randint(1, 4)}",
      "content_type": ct,
      "channel_or_app": random.choice(channels[ct]),
      "genre": random.choice(genres),
      "start_time": datetime.now().isoformat(),
      "duration_minutes": max(1, int(random.gauss(45, 30))),
      "completion_rate": round(random.betavariate(2, 1.5), 2),
    })
  return events

# 테스트 이벤트 생성 및 Volume에 저장
test_events = generate_test_viewing_events(100)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
content = "\n".join(json.dumps(e, ensure_ascii=False) for e in test_events)

test_path = f"{LANDING_BASE}/viewing_events/test_{timestamp}.json"
dbutils.fs.put(test_path, content, overwrite=True)
print(f"✅ 테스트 이벤트 100건 생성: {test_path}")

# COMMAND ----------

# 생성된 파일 확인
files = dbutils.fs.ls(f"{LANDING_BASE}/viewing_events/")
print(f"viewing_events 폴더 파일 수: {len(files)}")
for f in files[:5]:
  print(f" {f.name} ({f.size:,} bytes)")

# COMMAND ----------

# JSON 내용 샘플 확인
sample_content = dbutils.fs.head(test_path, 500)
print("=== JSON 샘플 (첫 500자) ===")
print(sample_content)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: SDP 파이프라인에서 확인
# MAGIC
# MAGIC 이제 04_sdp_pipeline을 파이프라인으로 실행하면,
# MAGIC Auto Loader가 위에서 생성한 JSON 파일을 자동으로 감지하여
# MAGIC `bronze_live_viewing` → `silver_live_viewing` 으로 처리합니다.
# MAGIC
# MAGIC ### 확인 방법
# MAGIC ```sql
# MAGIC -- SDP 파이프라인 실행 후 확인
# MAGIC SELECT COUNT(*) FROM silver.bronze_live_viewing;
# MAGIC SELECT COUNT(*) FROM silver.silver_live_viewing;
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## 학습 정리
# MAGIC
# MAGIC ### 이 노트북에서 체험한 End-to-End 흐름
# MAGIC
# MAGIC ```
# MAGIC 1. Databricks App (이벤트 생성)
# MAGIC  ↓ JSON 파일 쓰기
# MAGIC 2. UC Volume (Landing Zone)
# MAGIC  ↓ Auto Loader 자동 감지
# MAGIC 3. SDP Bronze Streaming Table
# MAGIC  ↓ 증분 정제
# MAGIC 4. SDP Silver Streaming Table
# MAGIC  ↓ 증분 집계
# MAGIC 5. SDP Gold Materialized View
# MAGIC  ↓ 자동 반영
# MAGIC 6. AI/BI Dashboard (실시간 시각화)
# MAGIC ```
# MAGIC
# MAGIC ### 실무 적용 시 대응 관계
# MAGIC
# MAGIC | 교육 (이 노트북) | 실무 (Smart TV OEM) |
# MAGIC |-----------------|-------------|
# MAGIC | Databricks App (이벤트 생성기) | 스마트TV → IoT Gateway → S3/ADLS |
# MAGIC | UC Volume (JSON 파일) | S3 버킷 또는 ADLS Container |
# MAGIC | Auto Loader (read_files) | Auto Loader (동일) 또는 Kafka Connector |
# MAGIC | SDP Streaming Table | SDP Streaming Table (동일) |
# MAGIC
# MAGIC 핵심 메시지:**수집 방식만 다르고, 처리 파이프라인(SDP)은 동일합니다.**
