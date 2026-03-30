# Databricks notebook source
# MAGIC %md
# MAGIC # 10. Agent Bricks + Lakebase — GenAI 에이전트와 운영 데이터 연동
# MAGIC
# MAGIC 이 노트북에서는 **Agent Bricks**(KA, Genie, Supervisor)를 구축하고,
# MAGIC**Lakebase**(PostgreSQL 호환 OLTP DB)와 연동하여
# MAGIC 에이전트가 사용자 설정 조회/수정, 추천 결과 서빙, 피드백 수집까지
# MAGIC 수행하는 **End-to-End 운영 가능한 AI 시스템** 을 만듭니다.
# MAGIC
# MAGIC ### Agent Bricks란?
# MAGIC
# MAGIC Databricks에서 제공하는 **엔터프라이즈 AI 에이전트 구축 프레임워크** 입니다.
# MAGIC 코드 없이(또는 최소 코드로) AI 에이전트를 만들고, Unity Catalog 거버넌스를 그대로 상속합니다.
# MAGIC
# MAGIC | 에이전트 유형 | 역할 | 구축 방식 |
# MAGIC |-------------|------|----------|
# MAGIC |**Knowledge Assistant (KA)**| 문서 기반 Q&A (RAG) | UC Volume 문서 → 자동 인덱싱 |
# MAGIC |**Genie Space**| 자연어 → SQL 데이터 탐색 | Gold 테이블 연결 |
# MAGIC |**Supervisor Agent (MAS)**| 멀티 에이전트 오케스트레이션 | KA + Genie + UC Function 통합 |
# MAGIC
# MAGIC ### 이 노트북의 아키텍처
# MAGIC
# MAGIC ```
# MAGIC ┌──────────────────────────────────────────────────────────────┐
# MAGIC │          Supervisor Agent             │
# MAGIC │       "SmartTV 통합 어시스턴트"            │
# MAGIC │                               │
# MAGIC │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
# MAGIC │ │Knowledge │ │ Genie  │ │UC Func. │ │UC Func.  │ │
# MAGIC │ │Assistant │ │ Space  │ │광고 분석 │ │Lakebase  │ │
# MAGIC │ │(사용가이드)│ │(데이터탐색)│ │     │ │연동    │ │
# MAGIC │ └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬──────┘ │
# MAGIC └───────┼──────────────┼──────────────┼──────────────┼────────┘
# MAGIC     │       │       │       │
# MAGIC  UC Volume   Gold Tables  ad_performance  Lakebase
# MAGIC  (문서 5개)   (8개 테이블)          (user_prefs,
# MAGIC                          rec_cache,
# MAGIC                          feedback)
# MAGIC ```
# MAGIC
# MAGIC**사전 조건:**01~03 노트북 실행 완료 (카탈로그/데이터/Gold 테이블)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: 환경 설정

# COMMAND ----------

import re
import json
username = spark.sql("SELECT current_user()").first()[0]
user_prefix = re.sub(r'[^a-zA-Z0-9]', '_', username.split('@')[0])
CATALOG = f"{user_prefix}_smarttv_training"
spark.sql(f"USE CATALOG {CATALOG}")
print(f"카탈로그: {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part A: Knowledge Assistant — TV 사용 가이드 Q&A 봇
# MAGIC
# MAGIC ### Knowledge Assistant의 동작 원리 (RAG)
# MAGIC
# MAGIC ```
# MAGIC 사용자 질문          Knowledge Assistant
# MAGIC "FastTV에서 무료 채널은?"  ┌─────────────────────────┐
# MAGIC     │          │ 1. 질문 임베딩      │
# MAGIC     │          │ 2. 벡터 검색 (문서에서) │
# MAGIC     ├───────────────────→│ 3. 관련 문서 조각 추출  │
# MAGIC     │          │ 4. LLM에게 문맥+질문 전달│
# MAGIC     │          │ 5. 문서 기반 답변 생성  │
# MAGIC     │          └─────────────────────────┘
# MAGIC     │               │
# MAGIC     │   "FastTV에서는 뉴스,   │
# MAGIC     │    스포츠, 영화 등     │
# MAGIC     │    100개 이상의 무료    │
# MAGIC     │    채널을 제공합니다..."  │
# MAGIC     ←──────────────────────────────┘
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 2: TV 사용 가이드 문서 생성 → UC Volume 업로드

# COMMAND ----------

# 가이드 문서 5개 생성
docs = {
  "fasttv_guide.md": """# FastTV 사용 가이드

## FastTV란?
FastTV는 인터넷에 연결된 스마트TV에서 **무료로 시청할 수 있는 스트리밍 서비스** 입니다.
별도의 앱 설치나 구독 없이, TV를 켜면 바로 이용할 수 있습니다.

## 무료 채널 목록
-**뉴스 **: YTN, MBN, 연합뉴스TV, 뉴스Y
-**스포츠 **: 스포츠 하이라이트, K리그, KBO
-**영화/드라마 **: 무비 클래식, K-Drama, 액션 영화
-**키즈 **: 뽀로로, 타요, 핑크퐁, 교육 채널
-**라이프스타일 **: 요리, 여행, 뷰티, 테크

## 즐겨찾기 설정
1. FastTV 화면에서 원하는 채널로 이동
2. 리모컨의 ★ 버튼을 누르면 즐겨찾기에 추가됩니다
3. 즐겨찾기 탭에서 등록된 채널을 한눈에 볼 수 있습니다
""",

  "personalization_guide.md": """# 개인화 설정 가이드

## 사용자 프로필
하나의 TV에 최대 4개의 사용자 프로필을 생성할 수 있습니다.
각 프로필은 독립된 시청 기록과 추천을 제공합니다.

## 프로필 생성 방법
1. 설정 → 일반 → 사용자 프로필 관리
2. "프로필 추가" 선택
3. 이름과 아바타 설정
4. 관심 장르 선택 (최대 5개)

## 추천 알고리즘
- 시청 이력 기반: 많이 본 장르/채널을 우선 추천
- 시간대 기반: 아침에는 뉴스, 저녁에는 드라마/예능
- 유사 사용자 기반: 비슷한 취향의 다른 사용자가 시청한 콘텐츠
- 피드백 반영: 좋아요/관심없음 표시가 즉시 반영됩니다
""",

  "ad_settings_guide.md": """# 광고 설정 및 개인정보 가이드

## 맞춤형 광고란?
시청 패턴과 관심사를 분석하여 관련성 높은 광고를 보여주는 기능입니다.

## 맞춤형 광고 설정/해제
1. 설정 → 일반 → 개인정보 → 광고 설정
2. "맞춤형 광고" 토글을 ON/OFF
3. OFF로 설정하면 일반 광고가 표시됩니다 (광고 자체는 사라지지 않음)

## 수집하는 데이터
- 시청한 채널 및 앱
- 시청 시간대 패턴
- 검색 키워드
- 클릭한 배너/광고
※ 개인 식별 정보(이름, 주소 등)는 수집하지 않습니다

## 데이터 삭제 요청
설정 → 개인정보 → "시청 데이터 초기화"를 선택하면
최근 30일 데이터가 삭제됩니다.
""",

  "voice_control_guide.md": """# 음성 제어 가이드

## 음성 명령어 목록
- "채널 [번호]번" — 채널 변경
- "볼륨 올려/내려" — 볼륨 조절
- "[앱 이름] 실행" — 앱 실행 (예: "넷플릭스 실행")
- "[프로그램 이름] 검색" — 콘텐츠 검색
- "지금 뭐 해?" — 현재 방영 중인 프로그램 안내
- "10분 후 꺼줘" — 취침 타이머 설정
- "자막 켜/꺼" — 자막 토글
- "화면 밝기 올려/내려" — 화면 설정

## 음성 인식이 안 될 때
1. 리모컨의 마이크 버튼을 길게 누르고 말하세요
2. TV에서 2m 이내 거리에서 명령하세요
3. 주변 소음이 적은 환경에서 사용하세요
""",

  "troubleshooting_guide.md": """# 문제 해결 가이드

## 화면이 안 나올 때
1. 전원 코드가 제대로 연결되어 있는지 확인
2. 리모컨의 전원 버튼을 10초간 길게 눌러 강제 재부팅
3. 다른 HDMI 포트로 연결 변경 시도
4. 위 방법으로 해결되지 않으면 고객센터 문의

## 인터넷 연결 문제
1. 설정 → 네트워크 → 연결 테스트 실행
2. 공유기를 재부팅 (전원 빼고 30초 후 재연결)
3. 유선 랜 연결 시도 (Wi-Fi 불안정한 경우)
4. DNS를 8.8.8.8로 수동 설정

## 리모컨 페어링
1. 리모컨의 홈 버튼과 설정 버튼을 동시에 5초간 누르기
2. TV 화면에 "리모컨 등록" 메시지가 나타나면 확인 선택
3. 리모컨 배터리를 교체 후 다시 시도
"""
}

# Volume에 문서 업로드
doc_volume_path = f"/Volumes/{CATALOG}/gold"

# gold 스키마에 Volume 생성 (없으면)
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.gold.tv_guide_docs COMMENT 'TV 사용 가이드 문서'")
doc_volume_path = f"/Volumes/{CATALOG}/gold/tv_guide_docs"

for filename, content in docs.items():
  path = f"{doc_volume_path}/{filename}"
  dbutils.fs.put(path, content, overwrite=True)
  print(f" ✅ {filename} → {path}")

print(f"\n총 {len(docs)}개 문서 업로드 완료")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 3: Knowledge Assistant 생성
# MAGIC
# MAGIC >**Note:**Agent Bricks KA 생성은 UI 또는 MCP 도구로 수행합니다.
# MAGIC > 아래는 MCP 도구 호출 예시입니다 (Claude Code / AI Dev Kit 환경에서 실행).

# COMMAND ----------

# Knowledge Assistant 생성 (MCP 도구 호출 형태)
ka_config = {
  "name": "SmartTV Guide Assistant",
  "description": "스마트TV 사용법, FastTV 가이드, 문제 해결에 대한 Q&A 어시스턴트",
  "instructions": """당신은 Smart TV 사용 가이드 전문 어시스턴트입니다.

규칙:
- 한국어로 답변합니다
- 제공된 문서에 있는 내용만 기반으로 답변합니다 (환각 방지)
- 친절하고 단계별로 설명합니다
- 문서에 없는 내용이면 "해당 정보를 찾을 수 없습니다. 고객센터에 문의해주세요."라고 안내합니다
""",
  "data_sources": [
    {"type": "uc_volume", "path": f"{CATALOG}.gold.tv_guide_docs"}
  ]
}

print("=== Knowledge Assistant 설정 ===")
print(json.dumps(ka_config, indent=2, ensure_ascii=False))
print("\n→ Claude Code에서: 'Agent Bricks KA를 위 설정으로 만들어줘'")
print("→ Databricks UI에서: Agents > New Knowledge Assistant")

# COMMAND ----------

# MAGIC %md
# MAGIC ### KA 테스트 질문

# COMMAND ----------

ka_test_questions = [
  "FastTV에서 무료로 볼 수 있는 채널이 뭐야?",
  "맞춤형 광고를 끄고 싶은데 어떻게 해?",
  "리모컨이 안 되는데 어떻게 해야 돼?",
  "음성 명령으로 넷플릭스 실행하는 방법 알려줘",
  "사용자 프로필은 몇 개까지 만들 수 있어?",
]

print("=== KA 테스트 질문 ===\n")
for i, q in enumerate(ka_test_questions, 1):
  print(f" {i}. {q}")

print("""
→ Agent Bricks KA 생성 후, 위 질문으로 테스트합니다.
→ 각 질문에 대해 문서 기반의 정확한 답변이 나오는지 확인합니다.
→ 문서에 없는 질문 ("TV 가격이 얼마야?")은 고객센터 안내가 나와야 합니다.
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part B: Genie Space — 자연어 데이터 탐색
# MAGIC
# MAGIC ### Genie Space란?
# MAGIC
# MAGIC 비즈니스 사용자가 **자연어로 질문하면 SQL로 자동 변환** 하여
# MAGIC 데이터를 조회하고 시각화하는 AI 에이전트입니다.
# MAGIC
# MAGIC | 비교 | Knowledge Assistant | Genie Space |
# MAGIC |------|-------------------|-------------|
# MAGIC |**데이터 소스**| 문서 (마크다운, PDF 등) | 테이블 (Delta Lake) |
# MAGIC |**답변 방식**| 문서 기반 텍스트 | SQL 실행 → 결과 테이블/차트 |
# MAGIC |**대상**| TV 사용법 질문 | 데이터 분석 질문 |

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 4: Genie Space 생성

# COMMAND ----------

genie_config = {
  "name": "SmartTV Data Explorer",
  "description": "시청 데이터, 광고 성과, 사용자 행동을 자연어로 탐색하는 Genie Space",
  "tables": [
    f"{CATALOG}.gold.daily_viewing_summary",
    f"{CATALOG}.gold.user_profiles",
    f"{CATALOG}.gold.ad_performance",
    f"{CATALOG}.gold.content_rankings",
    f"{CATALOG}.gold.weekly_kpi_trends",
    f"{CATALOG}.gold.user_segments",
    f"{CATALOG}.gold.fasttv_revenue_analysis",
    f"{CATALOG}.gold.hourly_heatmap",
  ],
  "instructions": """한국어 질문을 이해하고 정확한 SQL로 변환합니다.
날짜 필터가 없으면 최근 30일을 기본 적용합니다.
금액은 USD, 비율은 %로 표시합니다.
결과를 비즈니스 관점에서 해석하여 인사이트를 제공합니다.""",
  "sample_questions": [
    "이번 달 가장 인기 있는 콘텐츠 Top 10은?",
    "주말과 평일의 시청 패턴 차이를 보여줘",
    "FastTV 광고 중 CTR이 가장 높은 광고 형식은?",
    "premium 티어 사용자의 시청 행동이 entry 사용자와 어떻게 달라?",
    "광고 수익이 가장 높은 시간대는?",
  ]
}

print("=== Genie Space 설정 ===")
print(f"연결 테이블: {len(genie_config['tables'])}개")
for t in genie_config["tables"]:
  print(f" - {t}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part C: UC Function — 광고 분석 + Lakebase 연동
# MAGIC
# MAGIC ### UC Function이란?
# MAGIC
# MAGIC Unity Catalog에 등록하는 **재사용 가능한 SQL/Python 함수** 입니다.
# MAGIC Agent가 도구(Tool)로 호출할 수 있어, Supervisor Agent의 핵심 구성 요소입니다.
# MAGIC
# MAGIC ### Lakebase 연동의 의미
# MAGIC
# MAGIC Agent가 **분석 데이터(Delta Lake)** 뿐만 아니라
# MAGIC**운영 데이터(Lakebase)** 도 읽기/쓰기할 수 있게 됩니다.
# MAGIC
# MAGIC ```
# MAGIC ┌─────────────────┐   ┌─────────────────┐
# MAGIC │ Delta Lake   │   │ Lakebase    │
# MAGIC │ (분석 저장소)  │   │ (운영 저장소)  │
# MAGIC │         │   │         │
# MAGIC │ - 시청 로그   │   │ - 사용자 설정  │
# MAGIC │ - 광고 성과   │   │ - 추천 캐시   │
# MAGIC │ - ML 피처    │   │ - 사용자 피드백 │
# MAGIC │ → 초~분 응답  │   │ → 밀리초 응답  │
# MAGIC └────────┬────────┘   └────────┬────────┘
# MAGIC     │            │
# MAGIC     └──────────┬─────────────┘
# MAGIC           │
# MAGIC       UC Function (Agent Tool)
# MAGIC       "사용자 설정 조회/수정"
# MAGIC       "추천 결과 서빙"
# MAGIC       "피드백 저장"
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 5: Lakebase 테이블 생성

# COMMAND ----------

# Lakebase 테이블 DDL (PostgreSQL 호환)
# 실제로는 databricks CLI 또는 MCP 도구로 Lakebase 인스턴스를 생성합니다.

lakebase_ddl = {
  "user_preferences": """
CREATE TABLE user_preferences (
  user_id VARCHAR(100) PRIMARY KEY,     -- device_id + user_profile_id
  display_name VARCHAR(200),
  language VARCHAR(10) DEFAULT 'ko',
  subtitle_enabled BOOLEAN DEFAULT false,
  ad_personalization BOOLEAN DEFAULT true,  -- 맞춤형 광고 ON/OFF
  content_rating_limit VARCHAR(20) DEFAULT 'all', -- all, 15+, 18+
  parental_control_pin VARCHAR(10),
  theme VARCHAR(20) DEFAULT 'dark',
  notification_enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);""",

  "recommendation_cache": """
CREATE TABLE recommendation_cache (
  user_id VARCHAR(100),
  recommendation_type VARCHAR(50),      -- als, vector, hybrid, ad_target
  recommendations JSONB,           -- [{content_id, title, score, reason}]
  model_version VARCHAR(50),
  generated_at TIMESTAMP DEFAULT now(),
  expires_at TIMESTAMP,
  PRIMARY KEY (user_id, recommendation_type)
);""",

  "user_feedback": """
CREATE TABLE user_feedback (
  feedback_id SERIAL PRIMARY KEY,
  user_id VARCHAR(100) NOT NULL,
  content_id VARCHAR(100),
  agent_session_id VARCHAR(100),       -- 어떤 에이전트 세션에서 발생
  feedback_type VARCHAR(20) NOT NULL,    -- like, dislike, not_interested, helpful, unhelpful
  feedback_text TEXT,             -- 자유 텍스트 피드백
  context JSONB,               -- {source: "genie", question: "...", answer: "..."}
  created_at TIMESTAMP DEFAULT now()
);""",

  "agent_interaction_log": """
CREATE TABLE agent_interaction_log (
  log_id SERIAL PRIMARY KEY,
  session_id VARCHAR(100),
  user_id VARCHAR(100),
  agent_type VARCHAR(50),          -- supervisor, ka, genie, uc_function
  user_query TEXT,
  agent_response TEXT,
  routed_to VARCHAR(50),           -- 어디로 라우팅되었는지
  response_time_ms INTEGER,
  feedback VARCHAR(20),           -- thumbs_up, thumbs_down
  created_at TIMESTAMP DEFAULT now()
);"""
}

print("=== Lakebase 테이블 DDL ===\n")
for name, ddl in lakebase_ddl.items():
  print(f"--- {name} ---")
  print(ddl)
  print()

print("""
→ Lakebase 인스턴스 생성:
 Claude Code에서: "smarttv-demo-lakebase 이름으로 Lakebase 인스턴스 만들어줘"
 또는 Databricks UI: Database > Create Lakebase

→ 테이블 생성: 위 DDL을 Lakebase에서 실행
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 6: UC Function 생성 — Lakebase 연동 함수들

# COMMAND ----------

# UC Function: 사용자 설정 조회 (Agent Tool로 사용)
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.gold.get_user_preferences(
  p_user_id STRING COMMENT '사용자 ID (device_id_userN 형식)'
)
RETURNS STRING
COMMENT 'Lakebase에서 사용자 개인 설정을 조회합니다. 언어, 광고 개인화, 자녀보호 등의 설정을 반환합니다.'
LANGUAGE SQL
RETURN (
  SELECT CONCAT(
    '사용자 설정 (', p_user_id, '):\\n',
    '- 언어: ko\\n',
    '- 맞춤형 광고: ON\\n',
    '- 자막: OFF\\n',
    '- 콘텐츠 등급 제한: 전체\\n',
    '- 테마: 다크 모드'
  )
)
""")
print("✅ UC Function: get_user_preferences 생성")

# UC Function: 광고 성과 분석
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.gold.analyze_ad_performance(
  p_advertiser STRING COMMENT '광고주명 (NULL이면 전체 광고주)',
  p_date_from STRING COMMENT '시작일 (YYYY-MM-DD)',
  p_date_to STRING COMMENT '종료일 (YYYY-MM-DD)'
)
RETURNS STRING
COMMENT '지정 기간의 광고 성과를 분석합니다. 노출/클릭/전환, CTR/CVR, 광고비, CPC 등을 반환합니다.'
LANGUAGE SQL
RETURN (
  SELECT CONCAT(
    '광고 성과 분석 (', COALESCE(p_advertiser, '전체'), ', ', p_date_from, ' ~ ', p_date_to, '):\\n',
    '- 총 노출: ', CAST(SUM(impressions) AS STRING), '\\n',
    '- 총 클릭: ', CAST(SUM(clicks) AS STRING), '\\n',
    '- CTR: ', CAST(ROUND(SUM(clicks) * 100.0 / NULLIF(SUM(impressions), 0), 2) AS STRING), '%\\n',
    '- 총 광고비: $', CAST(ROUND(SUM(total_spend_usd), 2) AS STRING), '\\n',
    '- CPC: $', CAST(ROUND(SUM(total_spend_usd) / NULLIF(SUM(clicks), 0), 4) AS STRING)
  )
  FROM gold.ad_performance
  WHERE impression_date BETWEEN p_date_from AND p_date_to
    AND (p_advertiser IS NULL OR advertiser = p_advertiser)
)
""")
print("✅ UC Function: analyze_ad_performance 생성")

# UC Function: 추천 콘텐츠 조회
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.gold.get_content_recommendations(
  p_user_id STRING COMMENT '사용자 ID'
)
RETURNS STRING
COMMENT '사용자의 시청 패턴 기반 개인화 콘텐츠를 추천합니다. 선호 장르, 시청 시간대를 고려합니다.'
LANGUAGE SQL
RETURN (
  SELECT CONCAT(
    '추천 콘텐츠 (', p_user_id, '):\\n',
    '선호 장르: ', COALESCE(favorite_genre, 'N/A'), '\\n',
    '선호 시간대: ', COALESCE(preferred_time_slot, 'N/A'), '\\n',
    '일평균 시청: ', CAST(ROUND(avg_daily_viewing_minutes, 0) AS STRING), '분\\n',
    '\\n추천: 선호 장르 기반 Top 콘텐츠를 시청해보세요!'
  )
  FROM gold.user_profiles
  WHERE CONCAT(device_id, '_', user_profile_id) LIKE CONCAT('%', p_user_id, '%')
  LIMIT 1
)
""")
print("✅ UC Function: get_content_recommendations 생성")

# 함수 테스트
print("\n=== UC Function 테스트 ===")
result = spark.sql(f"SELECT {CATALOG}.gold.analyze_ad_performance('쿠팡', '2025-01-01', '2025-02-28') AS result").first()
print(result.result)

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part D: Supervisor Agent — 모든 것을 통합
# MAGIC
# MAGIC ### Supervisor Agent란?
# MAGIC
# MAGIC 여러 서브 에이전트(KA, Genie, UC Function)를 **하나로 통합** 하는 오케스트레이터입니다.
# MAGIC 사용자 질문을 분석하여 **최적의 서브 에이전트로 라우팅** 합니다.
# MAGIC
# MAGIC ### ALHF (Agent Learning on Human Feedback)
# MAGIC
# MAGIC Supervisor Agent는 사용자 피드백(👍/👎)을 통해 **라우팅 정확도를 자동으로 향상** 합니다.
# MAGIC 코드 수정 없이, 자연어 피드백만으로 에이전트 품질이 개선됩니다.

# COMMAND ----------

supervisor_config = {
  "name": "SmartTV 통합 어시스턴트",
  "description": "Smart TV 관련 사용 가이드, 데이터 분석, 콘텐츠 추천, 광고 성과를 통합 지원하는 AI 어시스턴트",
  "sub_agents": [
    {
      "type": "knowledge_assistant",
      "name": "TV 사용 가이드",
      "description": "TV 사용법, FastTV 가이드, 문제 해결 등 스마트TV 사용 관련 질문 답변",
    },
    {
      "type": "genie_space",
      "name": "데이터 분석",
      "description": "시청 데이터, 사용자 행동, 광고 성과 등 데이터 기반 질문에 SQL로 답변",
    },
    {
      "type": "uc_function",
      "name": "광고 성과 분석",
      "function": f"{CATALOG}.gold.analyze_ad_performance",
      "description": "특정 광고주나 기간의 광고 성과를 상세 분석",
    },
    {
      "type": "uc_function",
      "name": "사용자 설정 조회",
      "function": f"{CATALOG}.gold.get_user_preferences",
      "description": "사용자 개인 설정 조회 (언어, 광고, 자녀보호 등)",
    },
    {
      "type": "uc_function",
      "name": "콘텐츠 추천",
      "function": f"{CATALOG}.gold.get_content_recommendations",
      "description": "사용자 시청 패턴 기반 개인화 콘텐츠 추천",
    },
  ],
  "instructions": """당신은 Smart TV 통합 AI 어시스턴트입니다.

라우팅 규칙:
1. TV 사용법, 설정, 문제해결 질문 → TV 사용 가이드 (KA)
2. 데이터 조회, 통계, 트렌드 질문 → 데이터 분석 (Genie)
3. 특정 광고주/기간 광고 분석 → 광고 성과 분석 (UC Function)
4. 사용자 설정 확인/변경 → 사용자 설정 조회 (UC Function → Lakebase)
5. 콘텐츠 추천 요청 → 콘텐츠 추천 (UC Function)

한국어로 답변하고, 필요시 여러 서브에이전트를 조합하여 답변하세요.
사용자 피드백을 Lakebase의 user_feedback 테이블에 기록하세요.
""",
  "test_questions": [
    ("FastTV에서 무료 채널 목록 알려줘", "→ KA 라우팅"),
    ("이번 주 시청률 Top 5 보여줘", "→ Genie 라우팅"),
    ("쿠팡 광고 2월 성과 어때?", "→ UC Function (광고분석)"),
    ("내 맞춤형 광고 설정 확인해줘", "→ UC Function (Lakebase)"),
    ("나에게 맞는 콘텐츠 추천해줘", "→ UC Function (추천)"),
    ("premium 사용자 광고 반응 + 추천 콘텐츠는?", "→ 복합 라우팅 (Genie + 추천)"),
  ]
}

print("=== Supervisor Agent 설정 ===\n")
print(f"서브 에이전트: {len(supervisor_config['sub_agents'])}개")
for sa in supervisor_config["sub_agents"]:
  print(f" [{sa['type']}] {sa['name']}: {sa['description']}")

print(f"\n테스트 질문: {len(supervisor_config['test_questions'])}개")
for q, route in supervisor_config["test_questions"]:
  print(f" Q: {q}")
  print(f"   {route}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 4-B: AI Playground에서 Agent 테스트
# MAGIC
# MAGIC UC Function을 만들었으면,**AI Playground** 에서 바로 테스트할 수 있습니다.
# MAGIC AI Playground는 Databricks UI에서 LLM + Tools를 조합하여 Agent를 빌드하고 테스트하는 인터랙티브 환경입니다.
# MAGIC
# MAGIC #### AI Playground 사용법
# MAGIC 1. Databricks 워크스페이스 >**Playground** 메뉴 클릭
# MAGIC 2. 모델 선택: `databricks-claude-sonnet-4` 또는 `databricks-meta-llama-3-3-70b-instruct`
# MAGIC 3.**Tools** 섹션에서 우리가 만든 UC Function 추가:
# MAGIC  - `{catalog}.gold.analyze_ad_performance`
# MAGIC  - `{catalog}.gold.get_user_preferences`
# MAGIC  - `{catalog}.gold.get_content_recommendations`
# MAGIC 4. System Prompt에 Supervisor Instructions 붙여넣기
# MAGIC 5. 질문 입력 → Agent가 어떤 Tool을 호출하는지 실시간 확인
# MAGIC
# MAGIC >**핵심:**AI Playground에서 프로토타이핑 → 만족스러우면 Agent Bricks로 정식 배포
# MAGIC
# MAGIC <!-- 📸 스크린샷 추천: AI Playground에서 Tool 선택 + 질문 → Tool 호출 과정 -->

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 4-C: MLflow Evaluate로 Agent 품질 평가
# MAGIC
# MAGIC Agent를 만들었으면 **체계적으로 품질을 평가** 해야 합니다.
# MAGIC `mlflow.genai.evaluate()`는 평가 데이터셋을 기반으로 Agent의 답변을 자동 채점합니다.
# MAGIC
# MAGIC #### 평가 흐름
# MAGIC ```
# MAGIC 평가 데이터셋 → Agent 실행 → LLM Judge 채점 → MLflow UI에서 결과 확인
# MAGIC (질문 + 기대답변) (실제 답변 생성) (관련성, 정확성, 안전성) (점수 비교)
# MAGIC ```

# COMMAND ----------

# Agent 평가 데이터셋 정의
eval_dataset = [
  {
    "question": "FastTV에서 무료로 볼 수 있는 채널이 뭐야?",
    "expected_routing": "knowledge_assistant",
    "expected_facts": ["뉴스", "스포츠", "영화", "키즈"],
  },
  {
    "question": "이번 달 시청률 Top 5 보여줘",
    "expected_routing": "genie_space",
    "expected_facts": ["채널명", "시청자 수", "순위"],
  },
  {
    "question": "쿠팡 광고 2월 성과 어때?",
    "expected_routing": "uc_function",
    "expected_facts": ["노출", "클릭", "CTR", "광고비"],
  },
  {
    "question": "맞춤형 광고 끄는 방법 알려줘",
    "expected_routing": "knowledge_assistant",
    "expected_facts": ["설정", "개인정보", "토글"],
  },
  {
    "question": "premium 사용자와 entry 사용자 차이",
    "expected_routing": "genie_space",
    "expected_facts": ["시청 시간", "CTR", "세그먼트"],
  },
]

print(f"평가 데이터셋: {len(eval_dataset)}개 질문")
for i, d in enumerate(eval_dataset, 1):
  print(f" {i}. [{d['expected_routing']}] {d['question']}")

# COMMAND ----------

# MLflow Evaluate 실행 (Agent 배포 후 실행)
# 실행하려면 주석을 해제하세요

# import mlflow
#
# # 평가 데이터를 DataFrame으로 변환
# eval_df = pd.DataFrame([
#   {"inputs": d["question"], "ground_truth": ", ".join(d["expected_facts"])}
#   for d in eval_dataset
# ])
#
# # Agent Serving Endpoint를 대상으로 평가
# eval_results = mlflow.genai.evaluate(
#   data=eval_df,
#   model="endpoints:/smarttv-demo-supervisor", # Serving endpoint 이름
#   evaluators="default",
# )
#
# print("=== 평가 결과 ===")
# print(f"평균 관련성 점수: {eval_results.metrics.get('relevance/mean', 'N/A')}")
# print(f"평균 근거성 점수: {eval_results.metrics.get('groundedness/mean', 'N/A')}")
# print(f"→ MLflow Experiment UI에서 상세 결과 확인 가능")

print("Agent 배포 후 주석 해제하여 평가를 실행하세요")
print("참고: mlflow.genai.evaluate()는 Agent Serving Endpoint가 필요합니다")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part E: Agent + Lakebase 연동 시나리오
# MAGIC
# MAGIC ### 시나리오 1: 사용자 피드백 → 모델 재학습 트리거
# MAGIC
# MAGIC ```
# MAGIC 사용자: "추천이 별로야" (thumbs_down)
# MAGIC   ↓
# MAGIC Agent: Lakebase user_feedback에 기록
# MAGIC   ↓
# MAGIC 모니터링: 부정 피드백 비율 > 30% 감지
# MAGIC   ↓
# MAGIC Agent: 재학습 Job 트리거 (08번 노트북의 retrain_model)
# MAGIC   ↓
# MAGIC 새 모델: 피드백 반영한 추천 → Champion 교체
# MAGIC ```
# MAGIC
# MAGIC ### 시나리오 2: 실시간 설정 변경 → 즉시 반영
# MAGIC
# MAGIC ```
# MAGIC 사용자: "맞춤형 광고 꺼줘"
# MAGIC   ↓
# MAGIC Agent → KA: 설정 방법 안내
# MAGIC Agent → UC Function: Lakebase user_preferences UPDATE
# MAGIC   ↓
# MAGIC 다음 광고 노출 시: 맞춤형 광고 OFF 상태 반영
# MAGIC ```
# MAGIC
# MAGIC ### 시나리오 3: Agent가 MLOps 파이프라인 트리거
# MAGIC
# MAGIC ```
# MAGIC 운영자: "이상 탐지 모델 재학습 시켜줘"
# MAGIC   ↓
# MAGIC Agent → UC Function: Databricks Job 트리거
# MAGIC   ↓
# MAGIC Job: 09번 노트북 실행 (AutoEncoder 재학습)
# MAGIC   ↓
# MAGIC Agent: "재학습 완료. 새 모델 AUC: 0.95. Champion으로 등록되었습니다."
# MAGIC ```

# COMMAND ----------

# MLOps 트리거 UC Function 예시
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.gold.trigger_model_retrain(
  p_model_type STRING COMMENT '모델 유형: ad_click, anomaly_detection, recommendation',
  p_reason STRING COMMENT '재학습 사유: scheduled, drift_detected, feedback_threshold, manual'
)
RETURNS STRING
COMMENT 'ML 모델 재학습을 트리거합니다. Databricks Job을 실행하고 결과를 반환합니다.'
LANGUAGE SQL
RETURN (
  SELECT CONCAT(
    '재학습 요청 접수:\\n',
    '- 모델: ', p_model_type, '\\n',
    '- 사유: ', p_reason, '\\n',
    '- 상태: Job 트리거됨\\n',
    '- 예상 소요: 정형 모델 ~10분, 비정형 모델 ~1시간\\n',
    '\\n실제 환경에서는 databricks.sdk.WorkspaceClient().jobs.run_now()로 Job을 실행합니다.'
  )
)
""")
print("✅ UC Function: trigger_model_retrain 생성")

# 테스트
result = spark.sql(f"""
  SELECT {CATALOG}.gold.trigger_model_retrain('ad_click', 'drift_detected') AS result
""").first()
print(result.result)

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 학습 정리
# MAGIC
# MAGIC | 구성 요소 | 역할 | 데이터 소스 |
# MAGIC |----------|------|-----------|
# MAGIC |**Knowledge Assistant**| 문서 기반 Q&A (RAG) | UC Volume (마크다운 5개) |
# MAGIC |**Genie Space**| 자연어 → SQL 데이터 탐색 | Gold 테이블 (8개) |
# MAGIC |**UC Function (광고)**| 광고 성과 상세 분석 | Delta Lake (ad_performance) |
# MAGIC |**UC Function (Lakebase)**| 사용자 설정, 피드백 | Lakebase (PostgreSQL) |
# MAGIC |**UC Function (MLOps)**| 모델 재학습 트리거 | Databricks Jobs |
# MAGIC |**Supervisor Agent**| 위 5개를 통합 라우팅 | — |
# MAGIC
# MAGIC ### Agent + Lakebase 연동의 가치
# MAGIC
# MAGIC | 시나리오 | Agent 동작 | Lakebase 역할 |
# MAGIC |---------|-----------|--------------|
# MAGIC | 사용자 설정 조회/변경 | UC Function 호출 | 밀리초 응답으로 설정 읽기/쓰기 |
# MAGIC | 추천 결과 서빙 | 추천 캐시 조회 | Delta Lake 대신 빠른 서빙 |
# MAGIC | 피드백 수집 | 대화 중 피드백 저장 | 실시간 피드백 축적 |
# MAGIC | 재학습 트리거 | 피드백 임계값 모니터링 | 피드백 데이터 집계 |
# MAGIC | 에이전트 로그 | 모든 대화 기록 | 품질 분석, ALHF 학습 데이터 |
