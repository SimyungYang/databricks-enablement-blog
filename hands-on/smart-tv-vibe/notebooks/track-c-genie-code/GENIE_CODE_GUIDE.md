# Track C: Genie Code 기반 가이드

## Genie Code란?

Genie Code는 Databricks 노트북/콘솔에 **내장된 AI 에이전트**입니다.
별도의 도구 설치 없이 Databricks 환경에서 바로 자연어로 코드를 생성하고 실행할 수 있습니다.

### Genie Code vs AI Dev Kit (Claude Code)

| |**Genie Code**|**AI Dev Kit (Claude Code)**|
|---|---|---|
|**설치**| 불필요 (Databricks 내장) | Claude Code + AI Dev Kit 설치 필요 |
|**사용 환경**| Databricks 노트북/콘솔 | 로컬 터미널/IDE |
|**장점**| 즉시 시작, Databricks 최적화 | 높은 커스터마이징, 다양한 도구 |
|**적합한 상황**| 노트북 내 빠른 작업 | 복잡한 프로젝트, 멀티파일 |

### Genie Code 활성화

1. Databricks 워크스페이스 접속
2. 노트북 열기
3. 셀 오른쪽 상단의 **Genie Code**아이콘 클릭 (또는 `Cmd+I` / `Ctrl+I`)
4. 자연어로 요청 입력

---

## Genie Code로 전체 파이프라인 한번에 생성

Genie Code의 "**Create pipeline with AI**" 기능을 사용하면, 자연어 프롬프트 하나로 Bronze→Silver→Gold SDP 파이프라인 전체를 한번에 생성할 수 있습니다. 이 기능은 **Track C (Genie Code)에서만 사용 가능**하며, Track A/B에서는 지원되지 않는 "one-shot pipeline" 기능입니다.

>**참고:**이 기능은 [databricks/tmm Genie-Code-Lakeflow](https://github.com/databricks/tmm/tree/master/Genie-Code-Lakeflow) 데모에서 영감을 받았습니다.

### 단계별 플로우

1.**New > ETL Pipeline**— Databricks 워크스페이스에서 새 ETL 파이프라인 생성을 시작합니다.
2."**Create pipeline with AI**" 클릭 — AI 기반 파이프라인 생성 모드로 진입합니다.
3.**자연어 프롬프트 입력**— 원하는 파이프라인 구조를 자연어로 설명합니다.
4.**아키텍처 리뷰**— Genie Code가 제안하는 파이프라인 아키텍처(테이블 구조, 의존성 그래프)를 확인합니다.
5.**"ok" 입력**— 아키텍처가 만족스러우면 승인합니다.
6.**생성된 코드 리뷰**— 각 테이블별 변환 로직, 데이터 품질 규칙 등을 검토합니다.
7.**Accept All**— 모든 코드를 수락하여 파이프라인에 반영합니다.
8.**Run**— 파이프라인을 실행하여 전체 데이터 처리를 수행합니다.

### 예시 프롬프트

```
Smart TV 시청 로그와 광고 데이터를 Bronze→Silver→Gold로 처리하는 SDP 파이프라인을 만들어줘.
bronze 스키마의 devices, viewing_logs, click_events, ad_impressions 테이블을 소스로 사용하고,
Silver에서는 NULL 제거와 타입 변환, Gold에서는 일별 집계와 사용자 프로필을 만들어줘.
```

>**Track C만의 장점:**Track A (AI Dev Kit)나 Track B (AI Dev Kit + SDP)에서는 파이프라인 코드를 직접 작성하거나 모듈별로 나눠서 생성해야 합니다. Genie Code의 "Create pipeline with AI"는 전체 파이프라인을 한번에 설계하고 생성하는 유일한 방법입니다. 빠른 프로토타이핑이나 데모에 특히 유용합니다.

---

## 사용 방법

각 모듈별로 아래 프롬프트를 **Genie Code 입력창**에 붙여넣기하세요.
Genie Code가 코드를 자동 생성하고, "Apply" 버튼을 누르면 셀에 삽입됩니다.

>**Tip:**생성된 코드를 검토한 후 실행하세요. 수정이 필요하면 다시 Genie Code에 요청하면 됩니다.

---

## Module 1: Foundation & 데이터 생성

### 1-1. 카탈로그 & 스키마 생성

```
교육용 카탈로그와 스키마를 만드는 SQL을 작성해줘.

- 카탈로그 이름은 current_user()에서 이메일 prefix를 추출해서 {prefix}_smarttv_training 형식
- bronze, silver, gold 3개 스키마
- 각 스키마에 COMMENT 추가
- 생성 후 SHOW SCHEMAS 확인 쿼리도 포함
```

### 1-2. 디바이스 마스터 데이터 생성

```
Smart TV 디바이스 마스터 가상 데이터를 PySpark로 생성해줘.

테이블: {catalog}.bronze.devices (10,000건)
컬럼: device_id(UUID), model_name(OLED65C4/OLED55B4/QNED85/NANO75/UHD50UR 등 10개),
screen_size(43~86), region(Korea/US/EU/Japan/SEA 등 8개),
country(15개국), registered_at(2023~2025), firmware_version(webOS 6.0~24.0),
has_fasttv(80% true), price_tier(premium/mid/entry), subscription_tier(free/basic/premium)

생성 후 모델별/지역별 분포 통계도 보여줘.
```

### 1-3. 시청 로그 데이터 생성

```
스마트TV 시청 로그 가상 데이터를 생성해줘.

테이블: {catalog}.bronze.viewing_logs (500,000건)
컬럼: log_id, device_id(FK), user_profile_id(1~4), content_type(live_tv/vod/app/fasttv),
channel_or_app(MBC/Netflix/YouTube 등), genre, start_time(2025-01~03),
duration_minutes(평균 45분 로그정규분포), completion_rate(0~1)

시간대별 현실적 분포: 평일 저녁 집중(60%), 주말 분산, 새벽 최소(5%)
```

### 1-4. 클릭 이벤트 데이터 생성

```
스마트TV UI 클릭 이벤트 데이터를 생성해줘.

테이블: {catalog}.bronze.click_events (1,000,000건)
event_type 11종(app_launch/channel_change/search/banner_click/ad_click 등),
screen_name 7종, element_id, session_id(power_on~off 세션)
```

### 1-5. 광고 로그 데이터 생성

```
FastTV 광고 노출/클릭/전환 로그를 생성해줘.

테이블: {catalog}.bronze.ad_impressions (200,000건)
advertiser 30개(삼성전자/현대자동차/쿠팡/네이버 등 한국 기업),
ad_format 6종, placement 5종, bid/win price, was_clicked, was_converted

현실적 CTR: video_pre_roll(3~5%), banner(1~2%), native(4~7%), screensaver(0.5~1%)
```

---

## Module 2: Data Engineering

### 2-1. Silver 변환 (CTAS)

```
Bronze 데이터를 Silver로 정제하는 SQL CTAS를 작성해줘.

1. silver.devices_ctas ← bronze.devices
  NULL 제거, model_name 대문자, price_tier 파생(OLED→premium, QNED/NANO→mid, UHD→entry)

2. silver.viewing_logs_ctas ← bronze.viewing_logs JOIN silver.devices_ctas
  duration 0이하/480초과 제거, viewing_date/hour/day_of_week/is_weekend/time_slot 파생

3. silver.click_events_ctas ← bronze.click_events JOIN silver.devices_ctas
  session_id 기반 세션 통계 CTE, 디바이스 정보 JOIN

4. silver.ad_impressions_ctas ← bronze.ad_impressions JOIN silver.devices_ctas
  bid_price>0 필터, was_clicked 정합성 보정, impression_date/time_slot 파생
```

### 2-2. Gold 집계 (CTAS)

```
Silver 데이터를 Gold로 집계하는 SQL CTAS를 작성해줘.

1. gold.daily_viewing_summary - viewing_date/region/content_type/genre/time_slot 기준 집계
2. gold.user_profiles - device_id+user_profile_id별 시청/클릭/광고 피처 (윈도우 함수)
3. gold.ad_performance - 날짜/광고주/형식/지역 기준 CTR/CVR/CPC/RPM
4. gold.content_rankings - 날짜/채널/장르별 RANK 순위
```

### 2-3. SDP 파이프라인

```
위와 동일한 Bronze→Silver→Gold 변환을 SDP(Spark Declarative Pipeline)로 구현해줘.

최신 API 사용: from pyspark import pipelines as dp
- Silver: @dp.table() + @dp.expect_or_fail/@dp.expect_or_drop
- Gold: @dp.materialized_view()
- 읽기: spark.read.table() (dlt.read() 사용하지 마)

suffix: _sdp
```

---

## Module 3: AI/BI Dashboard & Genie

### 3-1. 심화 Gold 테이블 (대시보드용)

```
대시보드에서 다양한 차트를 보여주기 위한 심화 Gold 테이블 5개를 생성해줘.

1. gold.weekly_kpi_trends - 주간 KPI + WoW 변화율 (Counter/Line 차트용)
2. gold.user_segments - heavy/moderate/light/dormant 세그먼트 (Pie/Bar 차트용)
3. gold.fasttv_revenue_analysis - 광고 수익 심화 (Stacked Bar/Scatter 차트용)
4. gold.content_engagement_funnel - 소비 퍼널 4단계 (Funnel 차트용)
5. gold.hourly_heatmap - 요일×시간 히트맵 (Heatmap 차트용)
```

### 3-2. AI/BI Dashboard SQL 쿼리 검증

```
아래 대시보드 차트용 SQL 쿼리들이 정상 동작하는지 검증해줘.

1. 주간 KPI Counter: SELECT * FROM gold.weekly_kpi_trends ORDER BY week_start DESC LIMIT 1
2. 시청량 Line: 최근 8주 weekly_kpi_trends
3. 세그먼트 Pie: user_segments 전체
4. 히트맵: hourly_heatmap 전체
5. Top10 콘텐츠 Bar: content_rankings 최근 7일 합산 순위
6. 광고 Scatter: ad_performance 최근 30일 광고주별 합산 (impressions vs CTR)
7. 수익 Stacked Bar: fasttv_revenue_analysis 주간 집계
8. 퍼널: content_engagement_funnel 전체

각 쿼리 결과를 보여줘.
```

>**Genie Code에서 대시보드 생성하기:**> Genie Code에 "위 쿼리들로 AI/BI 대시보드를 만들어줘. 대시보드 이름: SmartTV Analytics"라고 요청하면,
> Genie Code가 대시보드를 자동 구성합니다.

### 3-3. Genie Space 자연어 질문 실습

> Genie Space는 별도로 UI에서 생성해야 합니다.
> 1. Genie > New Genie Space 클릭
> 2. Gold 테이블 8개 연결
> 3. 아래 질문을 입력하며 실습

```
=== 시청 분석 (4개) ===
1. "이번 달 가장 인기 있는 콘텐츠 Top 10은?"
2. "주말과 평일의 시청 패턴 차이를 보여줘"
3. "Korea 지역에서 프라임타임에 가장 많이 보는 장르는?"
4. "시청 완료율이 가장 높은 콘텐츠 유형은?"

=== 광고 분석 (4개) ===
5. "FastTV 광고 중 CTR이 가장 높은 광고 형식은?"
6. "광고 수익이 가장 높은 시간대는?"
7. "쿠팡 광고의 지난 달 성과 요약해줘"
8. "native 광고와 banner 광고의 전환율 차이는?"

=== 사용자 분석 (4개) ===
9. "premium 티어와 entry 티어 사용자의 시청 행동 차이는?"
10. "heavy viewer 세그먼트의 특성을 알려줘"
11. "음성 명령 사용률이 가장 높은 사용자 그룹은?"
12. "시청 시간이 가장 많은 지역 Top 5와 각 지역의 인기 장르는?"

=== 심화 질문 (3개) ===
13. "광고 CTR이 높은 사용자는 어떤 콘텐츠를 주로 시청하나?"
14. "OLED TV와 일반 TV 사용자의 FastTV 광고 반응 차이는?"
15. "가장 빠르게 성장하는 콘텐츠/채널은?"
```

---

## Module 4: Structured Streaming

### 4-1. Volume & Landing Zone

```
실시간 이벤트 데이터를 수집할 UC Volume과 디렉토리 구조를 만들어줘.

Volume: {catalog}.bronze.landing_zone (MANAGED)
디렉토리: viewing_events/, click_events/, ad_events/
```

### 4-2. 이벤트 생성기

```
실시간 시뮬레이션용 이벤트 생성기를 만들어줘.
배치당 viewing 100건, click 200건, ad 50건을 JSON으로 Volume에 저장.

파일명: {type}_{timestamp}_{batch}.json
기존 bronze.devices에서 device_id 참조.
테스트로 1배치 생성해줘.
```

### 4-3. Auto Loader + SDP 스트리밍

```
SDP 파이프라인으로 Auto Loader를 사용한 스트리밍 수집을 구현해줘.

Bronze: @dp.table + cloudFiles로 Volume에서 JSON 자동 수집
Silver: @dp.table + 정제 + devices JOIN
Gold: @dp.materialized_view + 실시간 집계

from pyspark import pipelines as dp 사용.
```

---

## Module 5: ML 추천 모델

### 5-1. 콘텐츠 메타데이터

```
개인화 추천용 콘텐츠 메타데이터 500건을 생성해줘.
gold.content_metadata 테이블에 저장.

title(한국어), content_type, genre, sub_genre, description(2~3문장 한국어),
target_audience, rating, tags 포함.
```

### 5-2. ALS 추천 모델 학습

```
사용자-콘텐츠 상호작용 매트릭스를 생성하고 ALS 모델을 학습해줘.

1. viewing_logs에서 (user, content) 상호작용 점수 계산
2. 80/20 Train/Test 분할
3. PySpark ML ALS로 3가지 하이퍼파라미터 비교
4. MLflow로 실험 로깅
5. 최적 모델을 Unity Catalog에 등록

MLflow 실험 이름: /smarttv_demo/content_recommendation
```

### 5-3. Vector Search

```
콘텐츠 description 임베딩으로 Vector Search 인덱스를 만들어줘.
유사도 검색 테스트: "가족이 함께 볼 수 있는 따뜻한 드라마"
```

---

## Module 6: GenAI & Agent Bricks

### 6-1. Knowledge Assistant

```
Smart TV 사용 가이드 Q&A 봇을 Agent Bricks Knowledge Assistant로 만들어줘.

1. UC Volume에 가이드 문서 5개 업로드 (FastTV, 개인화, 광고설정, 음성제어, 문제해결)
2. Knowledge Assistant 생성
3. 테스트: "FastTV에서 무료 채널은?", "맞춤형 광고 끄는 법", "리모컨 문제"
```

### 6-2. Genie Space Agent

```
Gold 테이블 기반 Genie Space를 Agent Bricks로 만들어줘.
비즈니스 사용자가 자연어로 데이터 탐색 가능하도록.

연결 테이블: gold.daily_viewing_summary, user_profiles, ad_performance, content_rankings
```

### 6-3. Supervisor Agent

```
Knowledge Assistant + Genie Space + UC Function(광고분석)을 통합하는
Supervisor Agent를 만들어줘.

이름: SmartTV 통합 어시스턴트

라우팅 규칙:
- TV 사용법 → Knowledge Assistant
- 데이터 조회 → Genie Space
- 광고 분석 → UC Function

테스트: "FastTV 무료 채널", "시청률 Top 5", "쿠팡 광고 성과", "premium 사용자 광고 반응+추천 콘텐츠"
```

---

## Module 7: Apps & Lakebase

### 7-1. Lakebase 생성

```
Lakebase(PostgreSQL 호환) 인스턴스를 생성하고
사용자 설정, 추천 캐시, 피드백 테이블을 만들어줘.

인스턴스: smarttv-demo-lakebase
테이블: user_preferences, recommendation_cache, user_feedback, watch_history_cache
```

### 7-2. Databricks App 배포

```
SmartTV AI 챗봇을 Gradio Databricks App으로 배포해줘.

앱이름: smarttv-demo-chatbot
기능: 채팅 인터페이스, Supervisor Agent 호출, 대화 히스토리
사이드바: 샘플 질문 5개
```

### 7-3. Apps + Lakebase 연동

```
FastAPI 앱에서 Lakebase 읽기/쓰기하는 포탈 앱을 만들어줘.

앱이름: smarttv-demo-portal
API: GET/PUT preferences, GET recommendations, POST feedback, GET watch-history
Lakebase에서 빠른 조회, Delta Lake에서 분석 데이터 조회
```

---

## 참고: Genie Code 프롬프트 작성 팁

### 좋은 프롬프트 패턴

1.**목적 먼저**: "~하는 코드를 작성해줘"
2.**테이블 명시**: 카탈로그.스키마.테이블 전체 경로
3.**컬럼 구체적**: 이름, 타입, 생성 규칙
4.**변환 로직 명시**: WHERE 조건, 파생 컬럼 공식
5.**검증 요청**: "생성 후 통계도 보여줘"

### Genie Code가 잘하는 것

- SQL 쿼리 생성 (CTAS, 집계, 윈도우 함수)
- PySpark 코드 생성 (DataFrame API, ML)
- 데이터 생성 (가상 데이터, 테스트 데이터)
- 차트 생성 (matplotlib, plotly)
- 코드 설명 및 디버깅

### Genie Code 한계 (AI Dev Kit이 더 나은 경우)

- 다중 파일 프로젝트 구성 (앱 배포 등)
- Databricks 외부 작업 (Git, 로컬 파일)
- 복잡한 워크플로우 오케스트레이션
