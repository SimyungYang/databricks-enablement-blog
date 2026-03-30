# Module 7: Databricks Apps & Lakebase

## 이 가이드 사용 방법

>**이 교육 자료는 Claude Code (또는 Cursor)와 함께 사용합니다.**>
> 이 모듈에서는 Databricks Apps로 웹 애플리케이션을 배포하고,
> Lakebase(PostgreSQL 호환 OLTP DB)를 활용한 운영 데이터 저장소를 구축합니다.

---

## 학습 목표

-**Databricks Apps**: FastAPI/Gradio 기반 웹 앱 배포
-**Lakebase**: PostgreSQL 호환 OLTP 데이터베이스 생성 및 활용
-**Apps + Lakebase 연동**: 웹 앱에서 Lakebase 읽기/쓰기
-**활용 시나리오**: 사용자 설정 저장, 추천 결과 캐싱, 피드백 수집

---

## Databricks Apps vs Lakebase

| |**Databricks Apps**|**Lakebase**|
|---|---|---|
|**역할**| 웹 앱 배포 플랫폼 | OLTP 데이터베이스 |
|**용도**| UI, API 서버, 대시보드 | 사용자 데이터, 설정, 캐싱 |
|**기술**| FastAPI, Gradio, Streamlit | PostgreSQL 호환 |
|**조합**| 앱이 Lakebase에서 읽기/쓰기 → 빠른 응답 |

---

## Part A: Databricks Apps

### Step 1: AI 챗봇 App 배포 (Gradio)

#### Claude에게 요청하기

```
Smart TV AI 어시스턴트 챗봇을 Databricks App으로 배포해줘.
Gradio 프레임워크를 사용하고, Supervisor Agent 엔드포인트를 호출하는 앱이야.

앱 이름: smarttv-demo-chatbot
프레임워크: Gradio

기능:
- 채팅 인터페이스 (한국어)
- Supervisor Agent의 Model Serving 엔드포인트 호출
- 대화 히스토리 유지 (세션별)
- 사이드바에 샘플 질문 목록:
 - "FastTV에서 무료로 볼 수 있는 채널은?"
 - "이번 주 시청률 Top 5 보여줘"
 - "나에게 맞는 콘텐츠 추천해줘"
 - "쿠팡 광고 이번 달 성과 분석해줘"
 - "리모컨이 안 돼요, 도와주세요"

app.yaml:
 command: ["python", "app.py"]
 resources:
  - name: serving-endpoint
   serving_endpoint: smarttv-demo-supervisor

앱을 생성하고 배포해줘. 배포 후 URL에서 테스트해줘.
```

---

### Step 2: 데이터 탐색 대시보드 App (Streamlit)

#### Claude에게 요청하기

```
Gold 테이블의 데이터를 탐색할 수 있는 대시보드 앱을 Databricks App으로 배포해줘.

앱 이름: smarttv-data-explorer
프레임워크: Streamlit

기능:
1. 시청 분석 탭
  - 날짜 범위 선택 (date picker)
  - 지역 선택 (multiselect)
  - 시청 추이 차트 (plotly line chart)
  - Top 10 콘텐츠 테이블

2. 광고 분석 탭
  - 광고주 선택
  - CTR/CVR 추이 차트
  - 광고 형식별 성과 비교 (bar chart)

3. 사용자 세그먼트 탭
  - 세그먼트 분포 (pie chart)
  - 세그먼트별 상세 프로필 (table)
  - 특정 사용자 검색 → 추천 결과 표시

app.yaml:
 command: ["streamlit", "run", "app.py"]
 resources:
  - name: sql-warehouse
   sql_warehouse: auto

SQL Warehouse를 통해 Gold 테이블을 직접 쿼리하는 방식으로 구현해줘.
앱을 생성하고 배포해줘.
```

---

## Part B: Lakebase — 운영 데이터 저장소

### Step 3: Lakebase 인스턴스 생성

#### Claude에게 요청하기

```
Lakebase(PostgreSQL 호환 데이터베이스) 인스턴스를 만들어줘.

인스턴스 이름: smarttv-demo-lakebase
카탈로그: {catalog}

Lakebase 설명:
- Databricks에서 제공하는 PostgreSQL 호환 OLTP 데이터베이스
- Delta Lake(분석용)와 Lakebase(운영용)를 하나의 플랫폼에서 관리
- 자동 스케일링, Scale to zero 지원
- Unity Catalog로 거버넌스 통합

인스턴스 생성 후:
1. 연결 정보 확인 (호스트, 포트, 데이터베이스)
2. 테스트 쿼리 실행 (SELECT 1)
3. Lakebase가 기존 PostgreSQL과 어떻게 다른지 설명해줘
```

---

### Step 4: Lakebase 테이블 생성 — 사용자 설정/선호도

#### Claude에게 요청하기

```
Lakebase에 스마트TV 운영에 필요한 테이블들을 만들어줘.

1. user_preferences — 사용자 개인 설정
  - user_id VARCHAR(100) PRIMARY KEY (device_id + user_profile_id)
  - display_name VARCHAR(200)
  - language VARCHAR(10) DEFAULT 'ko'
  - subtitle_enabled BOOLEAN DEFAULT false
  - ad_personalization BOOLEAN DEFAULT true
  - content_rating_limit VARCHAR(20) DEFAULT 'all'
  - parental_control_pin VARCHAR(10)
  - theme VARCHAR(20) DEFAULT 'dark'
  - created_at TIMESTAMP DEFAULT now()
  - updated_at TIMESTAMP DEFAULT now()

2. recommendation_cache — 추천 결과 캐시
  - user_id VARCHAR(100)
  - recommendation_type VARCHAR(50) (als/vector/hybrid)
  - recommendations JSONB (추천 콘텐츠 배열)
  - generated_at TIMESTAMP
  - expires_at TIMESTAMP
  - model_version VARCHAR(50)
  - PRIMARY KEY (user_id, recommendation_type)

3. user_feedback — 사용자 피드백
  - feedback_id SERIAL PRIMARY KEY
  - user_id VARCHAR(100)
  - content_id VARCHAR(100)
  - feedback_type VARCHAR(20) (like/dislike/not_interested/watch_later)
  - feedback_timestamp TIMESTAMP DEFAULT now()
  - context JSONB (어디서 추천받았는지 등)

4. watch_history_cache — 최근 시청 이력 캐시 (빠른 조회용)
  - user_id VARCHAR(100)
  - content_id VARCHAR(100)
  - last_watched_at TIMESTAMP
  - watch_progress FLOAT (0.0~1.0)
  - PRIMARY KEY (user_id, content_id)

테이블 생성 후 샘플 데이터를 넣고 조회해줘.

Lakebase(OLTP)와 Delta Lake(분석)의 차이점:
- Delta Lake: 대용량 분석, 배치 처리, 히스토리 보관
- Lakebase: 빠른 읽기/쓰기, 트랜잭션, 실시간 서빙

이 사용 분리를 설명해줘.
```

---

### Step 5: 추천 결과 캐싱 파이프라인

#### Claude에게 요청하기

```
Gold 테이블의 추천 결과를 Lakebase에 캐싱하는 파이프라인을 만들어줘.

파이프라인 흐름:
1. gold.user_recommendations (Delta Lake) → 최신 추천 결과 읽기
2. 결과를 Lakebase recommendation_cache에 UPSERT
3. 오래된 캐시(24시간 이상) 자동 삭제

Python 스크립트로 구현:
- databricks-sdk로 Delta Lake 쿼리
- psycopg2 (또는 Lakebase SDK)로 Lakebase 쓰기
- UPSERT: ON CONFLICT (user_id, recommendation_type) DO UPDATE

스크립트 실행 후:
- Lakebase에 캐싱된 추천 건수 확인
- 캐시 조회 속도 vs Delta Lake 직접 조회 속도 비교
- Lakebase가 서빙 레이어로서 왜 필요한지 설명

이 패턴은 실무에서 "ML 추론 결과를 캐싱하여 API 응답 속도를 높이는" 일반적인 아키텍처입니다.
```

---

### Step 6: Apps + Lakebase 연동

#### Claude에게 요청하기

```
Databricks App에서 Lakebase를 읽기/쓰기하는 연동을 구현해줘.

앱 이름: smarttv-demo-portal (FastAPI + 간단한 HTML UI)

기능:
1. GET /api/preferences/{user_id}
  → Lakebase user_preferences에서 설정 조회

2. PUT /api/preferences/{user_id}
  → 사용자 설정 업데이트 (언어, 광고 개인화 등)

3. GET /api/recommendations/{user_id}
  → Lakebase recommendation_cache에서 캐싱된 추천 조회
  → 캐시 없으면 Delta Lake에서 조회 후 캐싱

4. POST /api/feedback
  → 사용자 피드백 저장 (좋아요/싫어요)

5. GET /api/watch-history/{user_id}?limit=10
  → 최근 시청 이력 조회

app.yaml:
 command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
 resources:
  - name: sql-warehouse
   sql_warehouse: auto
  - name: lakebase
   lakebase: smarttv-demo-lakebase

앱을 생성하고 배포 후, 각 API 엔드포인트를 테스트해줘.
```

---

## 전체 아키텍처 정리

```
┌─────────────────────────────────────────────────────────────┐
│          Databricks Platform            │
│                               │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│ │ Delta Lake  │  │ Lakebase  │  │ Model    │ │
│ │ (분석 저장소) │  │ (운영 저장소) │  │ Serving   │ │
│ │       │  │       │  │       │ │
│ │ Gold Tables │───→│ 추천 캐시  │←──│ ALS 모델   │ │
│ │ Bronze/Silver│  │ 사용자 설정 │  │ Agent    │ │
│ │ ML 피처   │  │ 피드백    │  │ Endpoint   │ │
│ └──────────────┘  └──────────────┘  └──────────────┘ │
│     │          ↕          │     │
│ ┌──────┴───────────────────┴────────────────────┴──────┐ │
│ │       Databricks Apps             │ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │ │
│ │ │ 챗봇 App │ │ 대시보드 │ │ TV 포탈 App   │  │ │
│ │ │ (Gradio) │ │ (Stream.) │ │ (FastAPI)    │  │ │
│ │ └──────────┘ └──────────┘ └──────────────────┘  │ │
│ └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 학습 정리

| 개념 | 실습 내용 |
|------|-----------|
|**Databricks Apps**| Gradio 챗봇, Streamlit 대시보드, FastAPI 포탈 앱 배포 |
|**App 리소스**| SQL Warehouse, Serving Endpoint, Lakebase 연결 |
|**Lakebase**| PostgreSQL 호환 OLTP DB, 테이블 생성, CRUD |
|**운영 데이터**| 사용자 설정, 추천 캐시, 피드백, 시청 이력 |
|**캐싱 패턴**| Delta Lake → Lakebase UPSERT, 빠른 서빙 |
|**Apps + Lakebase**| REST API에서 Lakebase 읽기/쓰기 연동 |

---

## 비즈니스 가치

| 시나리오 | Databricks 기능 | 효과 |
|---------|-----------------|------|
| TV 사용자 설정 관리 | Lakebase + Apps | 밀리초 응답, 트랜잭션 보장 |
| 추천 결과 서빙 | Model Serving + Lakebase 캐시 | 빠른 API 응답 |
| 고객 피드백 수집 | Apps + Lakebase | 실시간 피드백 → 모델 개선 |
| 내부 대시보드 | Apps + SQL Warehouse | 코드 한 줄로 배포 |
| AI 챗봇 | Apps + Agent Bricks | 고객 지원 자동화 |
