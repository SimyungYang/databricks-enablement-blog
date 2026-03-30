"""
SmartTV 실시간 이벤트 생성기 - Databricks App

스마트TV의 시청/클릭/광고 이벤트를 실시간으로 생성하여
UC Volume에 JSON 파일로 적재합니다.

SDP 파이프라인(04)의 Auto Loader가 이 파일을 자동 감지하여 처리합니다.
"""

import json
import uuid
import random
import time
import os
import threading
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from databricks.sdk import WorkspaceClient

# ─── Databricks SDK 초기화 ───
w = WorkspaceClient()
current_user = w.current_user.me()
user_prefix = current_user.user_name.split("@")[0].replace(".", "_").replace("-", "_")
CATALOG = f"{user_prefix}_smarttv_training"
LANDING_BASE = f"/Volumes/{CATALOG}/bronze/landing"

# ─── 이벤트 생성용 상수 (02 노트북과 동일) ───
DEVICE_IDS = None # 런타임에 로드
MODELS = ["OLED65C4", "OLED55C4", "OLED77G4", "OLED55B4", "QNED85", "QNED80", "NANO75", "UHD50UR", "UHD43UR"]
REGIONS = ["Korea", "US", "EU", "Japan", "SEA"]
CONTENT_TYPES = ["live_tv", "vod", "app", "fasttv"]
CHANNELS = {
  "live_tv": ["MBC", "KBS", "SBS", "JTBC", "tvN"],
  "vod": ["Netflix", "Disney+", "Tving", "Wavve", "Coupang Play"],
  "app": ["YouTube", "Twitch", "Spotify", "TikTok"],
  "fasttv": ["FastTV News", "FastTV Sports", "FastTV Movie", "FastTV Kids", "FastTV Music"],
}
GENRES = ["drama", "entertainment", "news", "sports", "movie", "kids", "documentary"]
EVENT_TYPES = ["app_launch", "channel_change", "search", "banner_click", "ad_click",
        "menu_navigate", "content_select", "voice_command"]
SCREENS = ["home", "fasttv", "app_store", "settings", "search", "channel_guide"]
ADVERTISERS = ["삼성전자", "현대자동차", "CJ제일제당", "쿠팡", "네이버", "카카오",
        "SK텔레콤", "신한카드", "배달의민족", "토스"]
AD_FORMATS = ["banner", "video_pre_roll", "native", "interstitial", "screensaver"]

# ─── 생성 상태 관리 ───
generator_state = {
  "running": False,
  "events_generated": 0,
  "files_written": 0,
  "last_event_time": None,
  "events_per_second": 5,
  "batch_size": 50,
}


def load_device_ids():
  """Bronze 디바이스 테이블에서 device_id 목록 로드"""
  global DEVICE_IDS
  try:
    from databricks.sdk.service.sql import StatementState
    warehouse_id = os.environ.get("DATABRICKS_WAREHOUSE_ID", "")

    if not warehouse_id:
      print("⚠️ DATABRICKS_WAREHOUSE_ID가 설정되지 않았습니다!")
      print("  app.yaml에서 SQL Warehouse ID를 설정하세요.")
      print("  임시 UUID를 사용하면 SDP JOIN에서 이벤트가 모두 제거됩니다.")
      DEVICE_IDS = [str(uuid.uuid4()) for _ in range(100)]
      return

    # SQL Warehouse로 디바이스 ID 조회
    result = w.statement_execution.execute_statement(
      warehouse_id=warehouse_id,
      catalog=CATALOG,
      schema="bronze",
      statement="SELECT device_id FROM devices LIMIT 1000"
    )
    if result.result and result.result.data_array:
      DEVICE_IDS = [row[0] for row in result.result.data_array]
      print(f"✅ {len(DEVICE_IDS)}개 디바이스 ID 로드 완료")
    else:
      DEVICE_IDS = [str(uuid.uuid4()) for _ in range(100)]
      print("⚠️ 디바이스 테이블 조회 실패 - 임시 ID 사용")
  except Exception as e:
    DEVICE_IDS = [str(uuid.uuid4()) for _ in range(100)]
    print(f"⚠️ 디바이스 ID 로드 실패: {e} - 임시 ID 사용")


def generate_viewing_event():
  device_id = random.choice(DEVICE_IDS)
  content_type = random.choice(CONTENT_TYPES)
  return {
    "log_id": str(uuid.uuid4()),
    "device_id": device_id,
    "user_profile_id": f"{device_id[:8]}_user{random.randint(1, 4)}",
    "content_type": content_type,
    "channel_or_app": random.choice(CHANNELS[content_type]),
    "genre": random.choice(GENRES),
    "start_time": datetime.now().isoformat(),
    "duration_minutes": max(1, int(random.gauss(45, 30))),
    "completion_rate": round(random.betavariate(2, 1.5), 2),
  }


def generate_click_event():
  device_id = random.choice(DEVICE_IDS)
  return {
    "event_id": str(uuid.uuid4()),
    "device_id": device_id,
    "user_profile_id": f"{device_id[:8]}_user{random.randint(1, 4)}",
    "event_timestamp": datetime.now().isoformat(),
    "event_type": random.choice(EVENT_TYPES),
    "screen_name": random.choice(SCREENS),
    "element_id": f"element_{random.randint(1, 50):03d}",
    "session_id": str(uuid.uuid4())[:12],
  }


AD_CATEGORY_MAP = {
  "삼성전자": "electronics", "현대자동차": "automotive", "CJ제일제당": "food",
  "쿠팡": "ecommerce", "네이버": "tech", "카카오": "tech",
  "SK텔레콤": "telecom", "신한카드": "finance", "배달의민족": "food", "토스": "finance",
}


def generate_ad_event():
  device_id = random.choice(DEVICE_IDS)
  ad_format = random.choice(AD_FORMATS)
  advertiser = random.choice(ADVERTISERS)
  was_clicked = random.random() < 0.03 # ~3% CTR
  bid_price = round(random.uniform(0.001, 0.05), 4)
  return {
    "impression_id": str(uuid.uuid4()),
    "device_id": device_id,
    "user_profile_id": f"{device_id[:8]}_user{random.randint(1, 4)}",
    "ad_id": f"ad_{random.randint(1, 200):03d}",
    "advertiser": advertiser,
    "ad_category": AD_CATEGORY_MAP.get(advertiser, "other"),
    "ad_format": ad_format,
    "placement": random.choice(["fasttv_home", "fasttv_channel", "app_launch"]),
    "impression_timestamp": datetime.now().isoformat(),
    "was_clicked": was_clicked,
    "click_timestamp": datetime.now().isoformat() if was_clicked else None,
    "was_converted": was_clicked and random.random() < 0.15,
    "bid_price_usd": bid_price,
    "win_price_usd": round(bid_price * random.uniform(0.60, 0.90), 4),
    "duration_seconds": random.choice([15, 30, 60]),
  }


def write_batch_to_volume(event_type: str, events: list):
  """이벤트 배치를 UC Volume에 JSON 파일로 저장"""
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
  filename = f"{event_type}_{timestamp}.json"
  volume_path = f"{LANDING_BASE}/{event_type}/{filename}"

  # NDJSON (줄바꿈 구분 JSON) 형식으로 저장
  content = "\n".join(json.dumps(e, ensure_ascii=False) for e in events)

  try:
    # dbutils 대신 SDK 사용
    w.files.upload(
      file_path=volume_path,
      contents=content.encode("utf-8"),
      overwrite=True
    )
    generator_state["files_written"] += 1
    return True
  except Exception as e:
    print(f"파일 저장 실패: {e}")
    return False


def event_generator_loop():
  """백그라운드 이벤트 생성 루프"""
  batch_size = generator_state["batch_size"]
  eps = generator_state["events_per_second"]

  while generator_state["running"]:
    # 시청 이벤트 배치
    viewing_events = [generate_viewing_event() for _ in range(batch_size)]
    write_batch_to_volume("viewing_events", viewing_events)

    # 클릭 이벤트 배치 (시청의 2배)
    click_events = [generate_click_event() for _ in range(batch_size * 2)]
    write_batch_to_volume("click_events", click_events)

    # 광고 이벤트 배치 (시청의 0.5배)
    ad_events = [generate_ad_event() for _ in range(max(1, batch_size // 2))]
    write_batch_to_volume("ad_events", ad_events)

    total = len(viewing_events) + len(click_events) + len(ad_events)
    generator_state["events_generated"] += total
    generator_state["last_event_time"] = datetime.now().isoformat()

    # 속도 조절
    sleep_time = batch_size / max(eps, 1)
    time.sleep(sleep_time)


# ─── FastAPI 앱 ───
app = FastAPI(title="SmartTV Event Generator")


@app.on_event("startup")
def startup():
  load_device_ids()


@app.get("/", response_class=HTMLResponse)
def dashboard():
  state = generator_state
  status_color = "#4CAF50" if state["running"] else "#f44336"
  status_text = "생성 중" if state["running"] else "정지"

  return f"""
  <html>
  <head>
    <title>SmartTV Event Generator</title>
    <meta http-equiv="refresh" content="5">
    <style>
      body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #1a1a2e; color: #eee; }}
      .card {{ background: #16213e; border-radius: 12px; padding: 24px; margin: 16px 0; }}
      .status {{ display: inline-block; padding: 6px 16px; border-radius: 20px; background: {status_color}; color: white; font-weight: bold; }}
      .metric {{ display: inline-block; text-align: center; margin: 0 24px; }}
      .metric-value {{ font-size: 2em; font-weight: bold; color: #e94560; }}
      .metric-label {{ font-size: 0.85em; color: #aaa; }}
      .btn {{ padding: 12px 24px; border: none; border-radius: 8px; font-size: 1em; cursor: pointer; margin: 4px; }}
      .btn-start {{ background: #4CAF50; color: white; }}
      .btn-stop {{ background: #f44336; color: white; }}
      h1 {{ color: #e94560; }}
      code {{ background: #0f3460; padding: 2px 8px; border-radius: 4px; }}
    </style>
  </head>
  <body>
    <h1>📺 SmartTV Event Generator</h1>
    <div class="card">
      <span class="status">{status_text}</span>
      <span style="margin-left: 16px;">카탈로그: <code>{CATALOG}</code></span>
    </div>
    <div class="card">
      <div class="metric">
        <div class="metric-value">{state['events_generated']:,}</div>
        <div class="metric-label">총 이벤트 수</div>
      </div>
      <div class="metric">
        <div class="metric-value">{state['files_written']:,}</div>
        <div class="metric-label">파일 수</div>
      </div>
      <div class="metric">
        <div class="metric-value">{state['events_per_second']}</div>
        <div class="metric-label">이벤트/초</div>
      </div>
    </div>
    <div class="card">
      <p>마지막 이벤트: <code>{state['last_event_time'] or 'N/A'}</code></p>
      <p>랜딩존: <code>{LANDING_BASE}/</code></p>
    </div>
    <div class="card">
      <a href="/start"><button class="btn btn-start">▶ 시작</button></a>
      <a href="/stop"><button class="btn btn-stop">⏹ 정지</button></a>
      <a href="/generate-once?count=100"><button class="btn" style="background:#0f3460;color:white;">📦 1회 배치 (100건)</button></a>
    </div>
    <div class="card" style="font-size: 0.85em; color: #888;">
      <p><b>데이터 흐름:</b> 이 앱 → UC Volume (JSON) → Auto Loader → SDP Pipeline → Silver/Gold → Dashboard</p>
      <p>페이지 5초마다 자동 새로고침됩니다.</p>
    </div>
  </body>
  </html>
  """


@app.get("/start")
def start_generator(
  eps: int = Query(5, description="Events per second"),
  batch_size: int = Query(50, description="Events per batch")
):
  if generator_state["running"]:
    return {"status": "already running"}

  generator_state["running"] = True
  generator_state["events_per_second"] = eps
  generator_state["batch_size"] = batch_size

  thread = threading.Thread(target=event_generator_loop, daemon=True)
  thread.start()

  return {"status": "started", "eps": eps, "batch_size": batch_size}


@app.get("/stop")
def stop_generator():
  generator_state["running"] = False
  return {"status": "stopped", "total_events": generator_state["events_generated"]}


@app.get("/generate-once")
def generate_once(count: int = Query(100, description="Number of events")):
  """1회성 배치 생성 (테스트용)"""
  if DEVICE_IDS is None:
    load_device_ids()

  viewing = [generate_viewing_event() for _ in range(count)]
  clicks = [generate_click_event() for _ in range(count * 2)]
  ads = [generate_ad_event() for _ in range(max(1, count // 2))]

  write_batch_to_volume("viewing_events", viewing)
  write_batch_to_volume("click_events", clicks)
  write_batch_to_volume("ad_events", ads)

  total = len(viewing) + len(clicks) + len(ads)
  generator_state["events_generated"] += total
  generator_state["last_event_time"] = datetime.now().isoformat()

  return {"status": "done", "events": total, "viewing": len(viewing), "clicks": len(clicks), "ads": len(ads)}


@app.get("/status")
def status():
  return generator_state
