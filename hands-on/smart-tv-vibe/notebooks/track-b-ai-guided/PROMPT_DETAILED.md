# Track B: 상세 자연어 프롬프트 가이드

>**간단 버전**(PROMPT_GUIDE.md): 핵심만 전달 — 빠르게 시작하고 싶을 때
>**상세 버전**(이 파일): 구체적 사양까지 지정 — 원하는 결과를 정확히 얻고 싶을 때
>
> 상세 버전을 Claude Code에 붙여넣으면, AI가 더 정확하고 일관된 결과를 생성합니다.

---

## 01. 카탈로그 & 스키마 설정 (상세)

```
Databricks에 교육용 환경을 셋업해줘. 아래 요구사항을 정확히 따라줘.

=== 카탈로그 ===
- current_user() 함수로 현재 로그인한 사용자 이메일을 가져와
- 이메일에서 @ 앞 부분만 추출하고, ".", "-" 를 "_"로 치환해서 prefix 생성
- 카탈로그 이름: {prefix}_smarttv_training
- COMMENT: 'Smart TV Workshop catalog for {사용자 이메일}'
- CREATE CATALOG IF NOT EXISTS 사용 (이미 있으면 skip)

=== 스키마 3개 ===
- {catalog}.bronze — COMMENT: '원본 데이터 저장 (Raw ingestion layer)'
- {catalog}.silver — COMMENT: '정제 및 변환된 데이터 (Cleaned & enriched)'
- {catalog}.gold  — COMMENT: '분석 및 서빙용 집계 데이터 (Business-level aggregates)'

=== UC Volume ===
- {catalog}.bronze.landing (MANAGED Volume) — 실시간 이벤트 파일 랜딩존
- 하위 디렉토리 3개: viewing_events/, click_events/, ad_events/

=== 실행 후 확인 ===
- SHOW SCHEMAS 실행해서 3개 스키마 확인
- Volume 경로에 디렉토리 생성 확인
- 최종 요약 출력 (카탈로그명, 스키마 목록, Volume 경로)

노트북으로 만들어서 워크스페이스에 업로드해줘.
경로: /Workspace/Users/{내 이메일}/smarttv-training/common/01_setup_catalog_schema.py
```

---

## 02. 가상 데이터 생성 (상세)

```
Smart TV 시나리오의 가상 데이터를 생성하는 노트북을 만들어줘.
총 170만건 이상을 생성하며, 각 테이블의 사양을 아래에 정확히 명시합니다.

카탈로그: 01에서 만든 {prefix}_smarttv_training 동적 생성
스키마: bronze

=== 테이블 1: bronze.devices (10,000건) ===
TV 디바이스 마스터 정보. 모든 로그 테이블의 기준(Dimension) 테이블.

컬럼:
- device_id: STRING (UUID v4, 고유)
- model_name: STRING — 아래 10개 모델 중 랜덤 선택
 OLED65C4, OLED55C4, OLED77G4, OLED55B4, OLED65B4,
 QNED85, QNED80, NANO75, UHD50UR, UHD43UR
- screen_size: INT — 모델에 따라 가능한 크기 (43/50/55/65/75/77/86)
 예: OLED65C4는 65만 가능, QNED85는 55/65/75 가능
- region: STRING — 8개 지역, 가중치 적용
 Korea(25%), US(20%), EU(20%), Japan(10%), SEA(10%), LatAm(8%), MiddleEast(4%), Oceania(3%)
- country: STRING — region에 매핑되는 국가코드 (15개국)
 Korea→KR, US→US, EU→DE/FR/GB/IT/ES, Japan→JP, SEA→TH/VN/ID/PH/MY 등
- registered_at: TIMESTAMP — 2023-01-01 ~ 2025-03-01 균일분포
- firmware_version: STRING — webOS 6.0, 22.0, 23.0, 23.5, 24.0 중 랜덤
- has_fasttv: BOOLEAN — 80% true, 20% false
- price_tier: STRING — 모델명 기반 자동 분류
 OLED* → premium, QNED*/NANO* → mid, UHD* → entry
- subscription_tier: STRING — free(60%), basic(25%), premium(15%)

=== 테이블 2: bronze.viewing_logs (500,000건) ===
사용자 시청 기록. 개인화 추천 엔진의 핵심 입력 데이터.

컬럼:
- log_id: STRING (UUID)
- device_id: STRING — devices 테이블의 device_id를 FK로 참조 (랜덤 선택)
- user_profile_id: STRING — "{device_id[:8]}_user{1~4}" 형식 (가구당 1~4명)
- content_type: STRING — live_tv(30%), vod(25%), app(30%), fasttv(15%)
- channel_or_app: STRING — content_type별 채널/앱명
 live_tv: MBC, KBS, SBS, JTBC, tvN, MBN, YTN, EBS, OCN, Channel A
 vod: Netflix, Disney+, Tving, Wavve, Coupang Play, Apple TV+, Watcha
 app: YouTube, Twitch, Spotify, TikTok, Instagram, Melon, Bugs
 fasttv: FastTV News/Sports/Movie/Kids/Docu/Music/Food/Travel/Tech/Lifestyle
- genre: STRING — content_type별 가능한 장르
 live_tv: drama/entertainment/news/sports/documentary
 vod: drama/movie/entertainment/documentary/kids/anime
 app: entertainment/music/sports/education/social
 fasttv: news/sports/movie/kids/documentary/music/food/travel
- start_time: TIMESTAMP — 2025-01-01 ~ 2025-03-01
**시간대별 현실적 분포 적용 필수:**- 평일: 저녁 6~11시에 60% 집중 (프라임타임)
 - 주말: 오전~오후에도 분산
 - 새벽 2~6시: 5% 미만
 - 주말 비율: 35%
- duration_minutes: INT — 로그정규분포 (mean=3.5, sigma=0.8), min 1, max 240
- completion_rate: DOUBLE — Beta 분포 (alpha=2, beta=1.5), 0.0~1.0

=== 테이블 3: bronze.click_events (1,000,000건) ===
TV UI 조작/클릭 로그. UX 분석, 소비 퍼널, 광고 효과 측정에 사용.

컬럼:
- event_id: STRING (UUID)
- device_id: STRING (devices FK)
- user_profile_id: STRING
- event_timestamp: TIMESTAMP — 시간 분포는 viewing_logs와 동일
- event_type: STRING — 11종, 아래 가중치:
 app_launch(15%), channel_change(18%), search(8%), banner_click(7%), ad_click(5%),
 menu_navigate(12%), content_select(15%), voice_command(4%), settings_change(3%),
 power_on(7%), power_off(6%)
- screen_name: STRING — 7종, 가중치:
 home(30%), fasttv(20%), app_store(12%), settings(5%), search(10%),
 channel_guide(13%), content_detail(10%)
- element_id: STRING — screen_name별 클릭 가능한 UI 요소
 home: banner_01~03, app_icon_netflix/youtube/tving, recommended_01~02, continue_watching_01
 fasttv: channel_card_01~03, ad_slot_top/side, genre_filter, search_bar, favorites_btn
 기타 화면도 각각 5~8개 요소
- session_id: STRING — power_on과 power_off 사이의 세션 (UUID[:12])

=== 테이블 4: bronze.ad_impressions (200,000건) ===
광고 노출/클릭/전환. 광고 수익 분석, eCPM 최적화의 핵심 데이터.

컬럼:
- impression_id: STRING (UUID)
- device_id: STRING (devices FK)
- user_profile_id: STRING
- ad_id: STRING — "ad_001" ~ "ad_200" (200개 소재)
- advertiser: STRING — 30개 광고주
 삼성전자, 현대자동차, CJ제일제당, 신한카드, 쿠팡, 네이버, 카카오, SK텔레콤, KT,
 LG생활건강, 아모레퍼시픽, 롯데칠성, 하이트진로, 대한항공, 신세계, 배달의민족, 토스,
 당근마켓, 마켓컬리, 야놀자, 무신사, 오늘의집, 리디, 넷마블, 크래프톤, 한화생명,
 삼성생명, 현대해상, 기아, 볼보코리아
- ad_category: STRING — 광고주에 매핑 (electronics, automotive, food, finance 등)
- ad_format: STRING — 6종, 가중치:
 banner(30%), video_pre_roll(20%), video_mid_roll(10%), native(15%),
 interstitial(10%), screensaver(15%)
- placement: STRING — fasttv_home(30%), fasttv_channel(25%), app_launch(20%),
 channel_guide(15%), screensaver(10%)
- impression_timestamp: TIMESTAMP
- was_clicked: BOOLEAN —**광고 형식별 차등 CTR 필수:**native: 4~7%, video_pre_roll: 3~5%, banner: 1~2%, screensaver: 0.5~1%
 video_mid_roll: 2~4%, interstitial: 2~4%
- click_timestamp: TIMESTAMP — 클릭 시 노출 후 1~30초 후, 미클릭 시 NULL
- was_converted: BOOLEAN — 클릭된 것 중 10~20% 전환
- bid_price_usd: DOUBLE — 0.001 ~ 0.05 균일분포
- win_price_usd: DOUBLE — bid_price의 60~90%
- duration_seconds: INT — 15(40%), 30(40%), 60(20%)

=== 생성 방식 ===
- PySpark + random/numpy로 생성
- 대용량은 배치 처리 (10만건씩 나눠서 메모리 효율적으로)
- random.seed(42), np.random.seed(42)로 재현 가능
- 각 테이블 생성 후 통계 확인 셀 (건수, 컬럼별 분포)
- 마지막에 전체 4개 테이블 요약 + 참조 무결성 검증 (device_id FK 체크)

노트북 파일명: 02_generate_synthetic_data.py
워크스페이스에 업로드해줘.
```

---

## 03. Bronze → Silver → Gold 변환 (상세)

```
Bronze 데이터를 Silver, Gold로 변환하는 SQL CTAS 노트북을 만들어줘.
카탈로그: current_user() 기반 동적 생성
Silver 테이블은 _ctas suffix 사용 (나중에 SDP 결과 _sdp와 비교용)

=== Part 1: Silver 변환 (4개 테이블) ===

1. silver.devices_ctas ← bronze.devices
  - device_id IS NOT NULL 필터
  - registered_at <= current_timestamp() 필터 (미래 날짜 제거)
  - model_name을 UPPER()로 대문자 통일
  - price_tier 파생: CASE WHEN model_name LIKE 'OLED%' THEN 'premium'
   WHEN model_name LIKE 'QNED%' OR model_name LIKE 'NANO%' THEN 'mid'
   WHEN model_name LIKE 'UHD%' THEN 'entry' ELSE 'unknown' END
  - device_age_days 파생: DATEDIFF(current_date(), registered_at)
  - 변환 전후 건수 비교 셀 포함

2. silver.viewing_logs_ctas ← bronze.viewing_logs INNER JOIN silver.devices_ctas
  - duration_minutes > 0 AND <= 480 필터 (이상치 제거)
  - start_time >= '2025-01-01' AND < '2025-03-01' 날짜 범위 검증
  - 파생 컬럼 6개:
   viewing_date = DATE(start_time)
   viewing_hour = HOUR(start_time)
   day_of_week = DAYOFWEEK(start_time)
   is_weekend = CASE WHEN DAYOFWEEK(start_time) IN (1, 7) THEN true ELSE false END
   time_slot = CASE WHEN HOUR BETWEEN 6 AND 11 THEN 'morning'
    WHEN 12~17 THEN 'afternoon' WHEN 18~22 THEN 'prime_time' ELSE 'late_night' END
   end_time = start_time + INTERVAL duration_minutes MINUTE
  - devices JOIN으로 model_name, region, price_tier 추가
  - 시간대별 시청 분포 통계 확인 셀

3. silver.click_events_ctas ← bronze.click_events INNER JOIN silver.devices_ctas
  - event_timestamp IS NOT NULL AND 날짜 범위 검증
  - CTE로 session_stats 계산: session_id별 MIN/MAX timestamp, event COUNT,
   session_duration_minutes
  - LEFT JOIN session_stats로 세션 정보 추가
  - event_date, event_hour 파생
  - devices JOIN
  - 이벤트 유형별 분포 통계

4. silver.ad_impressions_ctas ← bronze.ad_impressions INNER JOIN silver.devices_ctas
  - bid_price_usd > 0 필터
  - 클릭 정합성 보정: was_clicked=true AND click_timestamp IS NULL → was_clicked=false
  - 파생: impression_date, impression_hour, time_slot,
   time_to_click_seconds = UNIX_TIMESTAMP(click) - UNIX_TIMESTAMP(impression)
  - devices JOIN
  - 광고 형식별 CTR 통계

=== Part 2: Gold 집계 (4개 기본 + 5개 심화 = 9개 테이블) ===

기본 4개:
1. gold.daily_viewing_summary — viewing_date/region/content_type/genre/time_slot별 집계
  total_views, unique_devices, unique_users, total_minutes, avg_duration, avg_completion,
  p50_duration(PERCENTILE_APPROX 0.5), p90_duration(0.9)

2. gold.user_profiles — device_id + user_profile_id별 종합 피처
  시청 피처: total_viewing_days, total_viewing_minutes, avg_daily_viewing_minutes,
   favorite_genre(ROW_NUMBER Top 1), favorite_content_type, preferred_time_slot, weekend_ratio
  클릭 피처: total_click_events, avg_session_duration, search_count, voice_command_count
  광고 피처: total_ad_impressions, total_ad_clicks, ad_ctr, avg_time_to_click
  디바이스: model_name, region, price_tier, has_fasttv
  → 5개 CTE (genre_rank, content_rank, slot_rank, viewing_agg, click_features, ad_features)
   를 최종 JOIN하는 복합 쿼리

3. gold.ad_performance — impression_date/advertiser/ad_category/ad_format/placement/region별
  impressions, clicks, conversions, ctr, cvr, total_spend_usd, cost_per_click, rpm

4. gold.content_rankings — viewing_date/channel_or_app/genre별
  daily_views, daily_unique_viewers, daily_total_minutes, avg_completion,
  RANK() OVER (PARTITION BY viewing_date ORDER BY unique_viewers DESC) AS daily_rank

심화 5개 (대시보드/Genie용):
5. gold.weekly_kpi_trends — 주간 집계 + LAG 윈도우로 WoW 변화율
6. gold.user_segments — user_profiles 기반 viewing/ad/fasttv/value 4차원 세그먼트
7. gold.fasttv_revenue_analysis — silver.ad_impressions에서 직접 집계, eCPM, DoD 변화율
8. gold.content_engagement_funnel — home 이벤트→콘텐츠 선택→시청 시작→시청 완료 퍼널
9. gold.hourly_heatmap — day_of_week x hour_of_day 히트맵, 시청+광고 조인

=== 마지막 셀 ===
전체 Bronze(4) → Silver(4) → Gold(9) 테이블 현황을 UNION ALL로 한눈에 표시

노트북 파일명: 03_silver_gold_ctas.py
워크스페이스에 업로드해줘.
```

---

## 04. SDP 선언적 파이프라인 (상세)

```
03 노트북에서 CTAS로 수동 실행한 동일한 Bronze→Silver→Gold 변환을
Spark Declarative Pipeline (SDP)로 구현하는 노트북을 만들어줘.

=== 중요: 최신 API 사용 ===
- import: from pyspark import pipelines as dp
- 테이블 정의: @dp.table(name="...")
- Materialized View: @dp.materialized_view(name="...")
- 소스 읽기: spark.read.table("table_name") — dlt.read() 사용하지 마
- Expectations: @dp.expect_or_fail(), @dp.expect_or_drop(), @dp.expect()
- 이전 "import dlt" 방식은 레거시이므로 절대 사용하지 마

카탈로그: spark.conf.get("source_catalog") 파라미터로 받기
Silver: _sdp suffix, Gold: _sdp suffix

=== Silver (@dp.table + Expectations) ===

1. devices_sdp
  @dp.expect_or_fail("valid_device_id", "device_id IS NOT NULL")
  @dp.expect("valid_registration", "registered_at <= current_timestamp()")
  03과 동일 변환 로직 (price_tier, device_age_days)

2. viewing_logs_sdp
  @dp.expect_or_drop("valid_duration", "duration_minutes > 0 AND duration_minutes <= 480")
  @dp.expect_or_drop("valid_date_range", "start_time >= '2025-01-01' AND start_time < '2025-03-01'")
  spark.read.table("devices_sdp")로 JOIN — 의존성 자동 추적

3. click_events_sdp
  @dp.expect_or_fail("valid_timestamp", "event_timestamp IS NOT NULL")
  세션 통계 window로 계산 후 JOIN

4. ad_impressions_sdp
  @dp.expect_or_drop("valid_bid_price", "bid_price_usd > 0")
  was_clicked 정합성 보정

=== Gold (@dp.materialized_view) ===
5. daily_viewing_summary_sdp
6. ad_performance_sdp
7. content_rankings_sdp

=== 노트북 마지막에 포함할 것 ===
- 파이프라인 설정 JSON 예시 (catalog, target_schema, source_catalog 파라미터)
- DLT(레거시) vs SDP(최신) API 비교표
- CTAS vs SDP 비교표 (증분처리, 의존성, 품질검증, 모니터링)

이 노트북은 Workflows > Pipelines에서 파이프라인으로 실행됨 (Run All 아님).
노트북 파일명: 04_sdp_pipeline.py
워크스페이스에 업로드해줘.
```

---

## 05. AI/BI Dashboard (상세)

```
Gold 테이블들로 AI/BI 대시보드를 만들어줘.
가능한 한 다양한 차트 유형을 활용해서 "이런 것도 가능하다"를 보여주는게 목적이야.

대시보드 이름: SmartTV Analytics Dashboard

=== 먼저 각 차트의 SQL 쿼리를 execute_sql로 검증한 후 대시보드 생성 ===

=== Page 1: Executive Overview (6개 위젯) ===
1. Counter 차트 4개 가로 배치 — 최신 주간 KPI
  - 총 시청 수 + WoW 변화율 (weekly_kpi_trends 최신 주)
  - 순 사용자 수 + WoW 변화율
  - 총 광고 수익 ($) + WoW 변화율
  - 평균 CTR (%) + WoW 변화율
2. Line 차트 — 주간 시청량 추이 (최근 8주, X: week_start, Y: total_views + unique_users)
3. Pie 차트 — 사용자 세그먼트 분포 (value_segment별 user_count)

=== Page 2: Viewing Analytics (4개 위젯) ===
4. Heatmap — 시간대별 시청 히트맵 (X: hour 0~23, Y: day_name Mon~Sun, 값: active_devices)
5. Bar (Grouped) — Top 10 인기 콘텐츠 (X: channel_or_app, Y: total_viewers, Color: genre)
6. Line — 지역별 시청량 추이 (X: viewing_date, Y: total_views, Color: region 상위 5개)
7. Donut — 장르별 시청 비율 (최근 30일 total_minutes 기준)

=== Page 3: FastTV Ad Revenue (4개 위젯) ===
8. Line — 일별 광고 수익 추이 + 7일 이동평균 (fasttv_revenue_analysis 집계)
9. Stacked Bar — 광고 형식별 수익 구성 (주간 집계, X: week, Y: revenue, Color: ad_format)
10. Scatter — 광고주별 노출 vs CTR (X: impressions, Y: ctr, Size: revenue, Label: advertiser)
11. Bar (Horizontal) — Top 10 광고주 수익 랭킹

=== Page 4: Funnel & Segments (3개 위젯) ===
12. 퍼널 시각화 — home → content_select → viewing_start → viewing_complete 단계별 전환율
13. Bubble — 세그먼트별 참여도(X: avg_minutes) vs 광고반응(Y: avg_ctr) vs 규모(Size: users)
14. Pivot Table — region × content_type 매트릭스 (값: unique_users)

=== 대시보드 설정 ===
- 날짜 필터 위젯 추가 (전체 페이지 공통)
- 지역 필터 위젯 추가
- 대시보드 publish (공유 가능하게)

생성 후 대시보드 URL을 알려줘.
```

---

## 06. Genie Space + 15개 질문 (상세)

```
AI/BI Genie Space를 생성하고 15개 비즈니스 질문으로 테스트해줘.

=== Genie Space 설정 ===
이름: SmartTV Data Explorer
설명: Smart TV 시청/광고/사용자 데이터를 자연어로 탐색하는 Genie Space

연결 테이블 8개 (모두 gold 스키마):
1. daily_viewing_summary — 일별 시청 요약 (날짜/지역/콘텐츠/장르/시간대별)
2. user_profiles — 사용자 종합 프로필 (시청/클릭/광고 피처)
3. ad_performance — 광고 성과 (광고주/형식/지역별)
4. content_rankings — 콘텐츠 인기도 랭킹 (일별 순위)
5. weekly_kpi_trends — 주간 KPI + WoW 변화율
6. user_segments — 사용자 세그먼트 (시청/광고/가치 분류)
7. fasttv_revenue_analysis — FastTV 광고 수익 심화 (eCPM, DoD)
8. hourly_heatmap — 요일×시간 히트맵 (시청+광고)

Instructions:
"""
당신은 Smart TV 데이터 분석 전문가입니다.
- 한국어 질문을 이해하고 정확한 Databricks SQL로 변환합니다
- 날짜 필터가 명시되지 않으면 최근 30일을 기본 적용합니다
- 금액은 USD, 비율은 %로 표시합니다
- 결과를 비즈니스 관점에서 해석하여 인사이트를 함께 제공합니다
- 가능하면 시각화에 적합한 차트 유형을 제안합니다
"""

Sample Questions 5개:
1. "이번 달 가장 인기 있는 콘텐츠 Top 10은?"
2. "주말과 평일의 시청 패턴 차이를 보여줘"
3. "FastTV 광고 중 CTR이 가장 높은 광고 형식은?"
4. "premium 티어 사용자의 시청 행동이 entry 사용자와 어떻게 달라?"
5. "광고 수익이 가장 높은 시간대는?"

=== Genie Space 생성 후 15개 질문 테스트 ===

각 질문에 대해 보여줄 것:
1. Genie가 생성한 SQL 쿼리
2. 쿼리 실행 결과 (상위 5건)
3. 비즈니스 인사이트 해석
4. Genie가 잘못 이해한 부분이 있으면 지적

시청 분석 (4개):
Q1: "이번 달 가장 인기 있는 콘텐츠 Top 10은?"
Q2: "주말과 평일의 시청 패턴 차이를 보여줘"
Q3: "Korea 지역에서 프라임타임에 가장 많이 보는 장르는?"
Q4: "시청 완료율이 가장 높은 콘텐츠 유형은?"

광고 분석 (4개):
Q5: "FastTV 광고 중 CTR이 가장 높은 광고 형식은?"
Q6: "광고 수익이 가장 높은 시간대는?"
Q7: "쿠팡 광고의 지난 달 성과 요약해줘"
Q8: "native 광고와 banner 광고의 전환율 차이는?"

사용자 분석 (4개):
Q9: "premium 티어와 entry 티어 사용자의 시청 행동 차이는?"
Q10: "heavy viewer 세그먼트의 특성을 알려줘"
Q11: "음성 명령 사용률이 가장 높은 사용자 그룹은?"
Q12: "시청 시간이 가장 많은 지역 Top 5와 각 지역의 인기 장르는?"

심화 (3개):
Q13: "광고 CTR이 높은 사용자는 어떤 콘텐츠를 주로 시청하나?"
Q14: "OLED TV와 일반 TV 사용자의 FastTV 광고 반응 차이는?"
Q15: "가장 빠르게 성장하는 콘텐츠/채널은?"
```

---

## 07. Agent Bricks — Supervisor + KA + Genie (상세)

```
Agent Bricks로 Smart TV 통합 AI 어시스턴트를 만들어줘.
Supervisor Agent가 앞에서 사용자 질문을 받고,
뒤에 Knowledge Assistant와 Genie Space가 도구로서 활용되는 구성이야.

=== Step 1: Knowledge Assistant (KA) 생성 ===

이름: SmartTV Guide Assistant
설명: Smart TV 사용법, FastTV, 문제 해결에 대한 Q&A 어시스턴트

먼저 UC Volume에 가이드 문서 5개를 만들어서 업로드해줘:
- Volume: {catalog}.gold.tv_guide_docs

문서 내용:
1. fasttv_guide.md — FastTV란? 무료 채널 목록 (뉴스/스포츠/영화/키즈/라이프), 즐겨찾기 설정법
2. personalization_guide.md — 사용자 프로필 생성(최대 4개), 추천 알고리즘 설명, 관심사 설정
3. ad_settings_guide.md — 맞춤형 광고 ON/OFF 방법, 수집 데이터 범위, 데이터 삭제 요청
4. voice_control_guide.md — 음성 명령어 10개+, 인식 안 될 때 해결법
5. troubleshooting_guide.md — 화면 안 나올 때/인터넷 문제/앱 오류/리모컨 페어링

각 문서 500~1000자, 한국어, 단계별 설명 형식

KA Instructions:
"""
당신은 Smart TV 사용 가이드 전문 어시스턴트입니다.
- 한국어로 친절하고 단계별로 답변합니다
- 제공된 문서에 있는 내용만 기반으로 답변합니다 (환각 방지)
- 문서에 없는 내용이면 "해당 정보를 찾을 수 없습니다. 고객센터에 문의해주세요." 안내
- 답변 마지막에 관련 문서명을 출처로 표시합니다
"""

KA 테스트 질문 5개:
1. "FastTV에서 무료로 볼 수 있는 채널이 뭐야?"
2. "맞춤형 광고를 끄고 싶은데 어떻게 해?"
3. "리모컨이 안 되는데 어떻게 해야 돼?"
4. "음성 명령으로 넷플릭스 실행하는 방법"
5. "사용자 프로필은 몇 개까지 만들 수 있어?"

=== Step 2: Genie Space (Agent) 생성 ===

이름: SmartTV Analytics
연결 테이블: gold 스키마 8개 테이블 (daily_viewing_summary, user_profiles,
 ad_performance, content_rankings, weekly_kpi_trends, user_segments,
 fasttv_revenue_analysis, hourly_heatmap)

=== Step 3: UC Function 생성 (3개) ===

1. {catalog}.gold.analyze_ad_performance(advertiser STRING, date_from STRING, date_to STRING)
  → 광고 성과 상세 분석 (노출/클릭/전환/CTR/CVR/CPC/RPM)

2. {catalog}.gold.get_user_preferences(user_id STRING)
  → 사용자 설정 조회 (Lakebase 연동용)

3. {catalog}.gold.trigger_model_retrain(model_type STRING, reason STRING)
  → ML 모델 재학습 트리거 (Jobs API 호출)

=== Step 4: Supervisor Agent 생성 ===

이름: SmartTV 통합 어시스턴트
설명: Smart TV 사용 가이드, 데이터 분석, 광고 성과, 설정 관리를 통합 지원하는 AI 어시스턴트

서브 에이전트/도구:
1. TV 사용 가이드 (KA) — "TV 사용법, FastTV, 설정, 문제해결 질문에 답변"
2. 데이터 분석 (Genie) — "시청 데이터, 사용자 행동, 광고 성과 등 데이터 기반 질문에 SQL로 답변"
3. 광고 성과 분석 (UC Function) — "특정 광고주나 기간의 광고 성과를 상세 분석"
4. 사용자 설정 (UC Function) — "사용자 개인 설정 조회 및 변경"
5. ML 재학습 (UC Function) — "모델 재학습 트리거"

Supervisor Instructions:
"""
당신은 Smart TV 통합 AI 어시스턴트입니다.

라우팅 규칙:
1. TV 사용법, 설정 방법, 문제해결 → TV 사용 가이드 (KA)
2. 데이터 조회, 통계, 트렌드, "보여줘/알려줘" → 데이터 분석 (Genie)
3. 특정 광고주 성과, "광고 분석해줘" → 광고 성과 분석 (UC Function)
4. "내 설정", "설정 변경", "광고 끄기" → 사용자 설정 (UC Function + KA 조합)
5. "모델 재학습", "추천 업데이트" → ML 재학습 (UC Function)

한국어로 답변하고, 필요시 여러 도구를 조합하여 답변하세요.
복합 질문은 순서대로 처리하고 결과를 종합합니다.
"""

=== Step 5: 통합 테스트 (6개 질문) ===

1. "FastTV에서 무료 채널 목록 알려줘" → KA 라우팅 확인
2. "이번 주 시청률 Top 5 보여줘" → Genie 라우팅 확인
3. "쿠팡 광고 2월 성과 어때?" → UC Function 라우팅 확인
4. "내 맞춤형 광고 설정 확인해줘" → UC Function (설정) 라우팅 확인
5. "premium 사용자의 광고 반응이 좋은 시간대와 추천 콘텐츠는?" → 복합 라우팅 (Genie + 분석)
6. "리모컨 문제가 있는데, 이 문제가 많이 보고되나?" → 복합 라우팅 (KA + Genie)

각 질문에 대해:
- 어디로 라우팅되었는지
- 답변 내용 요약
- 라우팅이 올바른지 평가
- 답변 품질 (1~5점) 평가
```

---

## 참고: 간단 vs 상세 프롬프트 사용 가이드

| | 간단 버전 (PROMPT_GUIDE.md) | 상세 버전 (이 파일) |
|---|---|---|
|**언제 사용**| 빠르게 시작, AI에게 재량 부여 | 정확한 결과가 필요할 때 |
|**장점**| 짧고 빠름, 다양한 결과 | 일관된 결과, 사양 정확 |
|**단점**| 결과가 기대와 다를 수 있음 | 입력이 길어 복사 시간 필요 |
|**추천 대상**| AI 도구에 익숙한 사용자 | 처음 사용하거나 정확도 중요 |

### 프롬프트 작성 팁

1.**목적을 먼저 명시**— "~하는 노트북을 만들어줘"
2.**테이블/컬럼을 구체적으로**— 이름, 타입, 생성 규칙까지
3.**변환 로직 명시**— WHERE 조건, 파생 컬럼 공식
4.**기대 결과 명시**— "검증 셀 포함", "통계 보여줘"
5.**제약 사항 명시**— "dlt 사용하지 마", "_ctas suffix 붙여줘"
