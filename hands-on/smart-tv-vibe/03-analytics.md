# Module 3: AI/BI Dashboard & Genie Space

## 이 가이드 사용 방법

>**이 교육 자료는 Claude Code (또는 Cursor)와 함께 사용합니다.**>
> 1. 터미널에서 프로젝트 디렉토리로 이동: `cd ~/smarttv-training`
> 2. Claude Code 실행: `claude`
> 3. 각 Step의 "**Claude에게 요청하기**" 박스 내용을 복사하여 Claude에게 붙여넣기
> 4. Claude가 코드를 생성하고 Databricks에서 실행합니다
>
>**이 모듈의 핵심:**"이런 것도 표현할 수 있다"를 **보여주는 것**이 목표!

---

## 학습 목표

- AI/BI Dashboard로 **다양한 차트 유형**을 활용한 대시보드 구성
- AI/BI Genie Space로 **자연어 데이터 탐색**체험
- 비즈니스 사용자 관점에서 데이터 인사이트 도출

---

## Part A: AI/BI Dashboard — 다양한 차트로 인사이트 시각화

### Dashboard vs Genie

| |**AI/BI Dashboard**|**AI/BI Genie**|
|---|---|---|
|**용도**| 정해진 KPI 모니터링 | 자유 탐색, ad-hoc 질문 |
|**대상**| 경영진, 정기 리포트 | PM, 마케터, 분석가 |
|**조합**| 대시보드에서 이상 발견 → Genie로 원인 파악 |

---

### Step 1: 심화 Gold 테이블 생성 (대시보드용)

#### Claude에게 요청하기

```
대시보드에서 다양한 차트를 보여주기 위한 심화 Gold 테이블 5개를 추가로 만들어줘.
기존 Gold 테이블(daily_viewing_summary, user_profiles, ad_performance, content_rankings)을 기반으로.

카탈로그: current_user() 기반 동적 생성

1. gold.weekly_kpi_trends - 주간 KPI 추이 (Counter, Line 차트용)
  - week_start, total_views, unique_users, avg_daily_minutes
  - total_ad_revenue, avg_ctr, total_sessions
  - wow_views_change_pct (전주 대비 증감률)
  - wow_revenue_change_pct

2. gold.user_segments - 사용자 세그먼트 (Pie, Bar 차트용)
  - segment_name: heavy_viewer/moderate/light/dormant
   (일 평균 시청 120분 이상/60~120/15~60/15 미만)
  - user_count, avg_viewing_minutes, avg_ad_ctr
  - top_genre, top_content_type

3. gold.fasttv_revenue_analysis - FastTV 광고 수익 심화 (Stacked Bar, Scatter 차트용)
  - date, advertiser, ad_format, region
  - impressions, clicks, revenue_usd
  - ecpm (revenue/impressions*1000), fill_rate

4. gold.content_engagement_funnel - 콘텐츠 소비 퍼널 (Funnel 차트용)
  - content_type, funnel_stage 4단계:
   - impression (광고 노출) → click (클릭) → view_start (시청 시작) → view_complete (시청 완료)
  - user_count, conversion_rate (이전 단계 대비)

5. gold.hourly_heatmap - 시간대별 히트맵 (Heatmap 차트용)
  - day_of_week (Mon~Sun), hour (0~23)
  - avg_viewers, avg_duration, avg_events
  - peak_content_type (해당 시간 인기 콘텐츠)

모든 테이블 생성 후 각 테이블의 샘플 데이터와 통계를 보여줘.
```

---

### Step 2: AI/BI Dashboard 생성 — Executive Overview 페이지

#### Claude에게 요청하기

```
AI/BI 대시보드의 첫 번째 페이지 "Executive Overview"를 만들어줘.

대시보드 이름: SmartTV Analytics Dashboard

=== Page 1: Executive Overview ===

차트 구성 (6개):

1. Counter 차트 (4개 가로 배치) - 주요 KPI
  - 총 시청 수 (최근 주) + WoW 변화율
  - 순 사용자 수 + WoW 변화율
  - 총 광고 수익 ($) + WoW 변화율
  - 평균 CTR (%) + WoW 변화율
  데이터: gold.weekly_kpi_trends (가장 최근 주)

2. Line 차트 - 주간 시청량 추이
  - X축: week_start, Y축: total_views, unique_users (듀얼 Y축)
  - 최근 8주 데이터
  데이터: gold.weekly_kpi_trends

3. Pie 차트 - 사용자 세그먼트 분포
  - heavy_viewer, moderate, light, dormant 비율
  데이터: gold.user_segments

4. Bar 차트 (Horizontal) - 세그먼트별 평균 시청 시간
  - 각 세그먼트의 avg_viewing_minutes 비교
  데이터: gold.user_segments

5. Stacked Area 차트 - 콘텐츠 유형별 시청 추이
  - X축: viewing_date, Y축: total_views, Color: content_type
  데이터: gold.daily_viewing_summary

6. Table 차트 - 주간 KPI 상세
  - 모든 KPI 지표를 테이블로 표시
  - WoW 변화율에 조건부 색상 (양수: 초록, 음수: 빨강)
  데이터: gold.weekly_kpi_trends

먼저 각 차트의 SQL 쿼리를 검증한 후 대시보드를 생성해줘.
```

---

### Step 3: AI/BI Dashboard — Viewing Analytics 페이지

#### Claude에게 요청하기

```
대시보드 두 번째 페이지 "Viewing Analytics"를 추가해줘.

=== Page 2: Viewing Analytics ===

차트 구성 (5개):

1. Heatmap 차트 - 시간대별 시청 히트맵
  - X축: hour (0~23), Y축: day_of_week (Mon~Sun)
  - 값: avg_viewers
  - 색상 강도로 시청 집중 시간대 한눈에 파악
  데이터: gold.hourly_heatmap

2. Bar 차트 (Vertical, Grouped) - Top 10 인기 콘텐츠
  - X축: channel_or_app, Y축: daily_unique_viewers (합계)
  - 색상: genre
  - 최근 7일 기준
  데이터: gold.content_rankings

3. Line 차트 - 지역별 시청량 추이
  - X축: viewing_date, Y축: total_views
  - 색상/그룹: region (Korea, US, EU, Japan, SEA)
  데이터: gold.daily_viewing_summary

4. Donut 차트 - 장르별 시청 비율
  - genre별 total_minutes 비율
  데이터: gold.daily_viewing_summary (최근 30일 합산)

5. Bar 차트 (Horizontal) - 시간대(time_slot)별 평균 시청 시간
  - prime_time, afternoon, morning, late_night 비교
  - 평균 duration_minutes
  데이터: gold.daily_viewing_summary

대시보드에 추가하고 레이아웃을 정리해줘.
```

---

### Step 4: AI/BI Dashboard — FastTV Ad Revenue 페이지

#### Claude에게 요청하기

```
대시보드 세 번째 페이지 "FastTV Ad Revenue"를 추가해줘.

=== Page 3: FastTV Ad Revenue ===

차트 구성 (5개):

1. Line 차트 - 일별 광고 수익 추이
  - X축: date, Y축: SUM(revenue_usd)
  - 7일 이동평균 라인도 추가
  데이터: gold.fasttv_revenue_analysis

2. Stacked Bar 차트 - 광고 형식별 수익 구성
  - X축: date (주 단위 집계), Y축: revenue_usd
  - 색상: ad_format (banner, video_pre_roll, native 등)
  데이터: gold.fasttv_revenue_analysis

3. Scatter 차트 - 광고주별 노출 vs CTR
  - X축: impressions, Y축: ctr (clicks/impressions*100)
  - 버블 크기: revenue_usd
  - 라벨: advertiser
  - 어떤 광고주가 효율적인지 한눈에 파악
  데이터: gold.ad_performance (최근 30일 합산)

4. Bar 차트 - Top 10 광고주 수익 랭킹
  - X축: advertiser, Y축: total_spend_usd
  - 색상: CTR 기준 (고: 초록, 저: 빨강)
  데이터: gold.ad_performance

5. Counter + Bar 조합 - eCPM 비교
  - 전체 평균 eCPM (Counter)
  - 광고 형식별 eCPM 비교 (Bar)
  - native > video_pre_roll > banner 순서 예상
  데이터: gold.fasttv_revenue_analysis

대시보드에 추가해줘.
```

---

### Step 5: AI/BI Dashboard — Funnel & User Segments 페이지

#### Claude에게 요청하기

```
대시보드 네 번째 페이지 "Funnel & User Segments"를 추가해줘.

=== Page 4: Funnel & User Segments ===

차트 구성 (4개):

1. Funnel 차트 - 콘텐츠 소비 퍼널
  - impression → click → view_start → view_complete
  - 각 단계별 사용자 수와 전환율
  - content_type별로 필터 가능
  데이터: gold.content_engagement_funnel

2. Bubble 차트 - 세그먼트별 가치 분석
  - X축: avg_viewing_minutes (참여도)
  - Y축: avg_ad_ctr (광고 반응도)
  - 버블 크기: user_count
  - 라벨: segment_name
  데이터: gold.user_segments

3. Bar 차트 (Grouped) - 세그먼트별 선호 장르
  - X축: segment_name, Y축: user_count
  - 색상: top_genre
  데이터: gold.user_segments

4. Pivot Table - 지역 × 콘텐츠 유형 매트릭스
  - 행: region, 열: content_type
  - 값: unique_users, avg_duration
  데이터: gold.daily_viewing_summary (최근 30일)

대시보드에 추가하고 전체 4페이지 레이아웃을 최종 정리해줘.
대시보드를 publish해서 공유 가능하게 만들어줘.
```

---

### AI/BI Dashboard 차트 유형 총정리

| 차트 유형 | 사용 위치 | 용도 |
|-----------|----------|------|
|**Counter**| Executive Overview | KPI 숫자 한눈에, WoW 변화율 |
|**Line**| Overview, Viewing, Ad Revenue | 시계열 추이 |
|**Pie / Donut**| Overview, Viewing | 비율/구성 |
|**Bar (V/H)**| 전체 페이지 | 비교, 랭킹 |
|**Stacked Bar**| Ad Revenue | 구성 요소별 누적 |
|**Stacked Area**| Overview | 트렌드 + 구성 |
|**Heatmap**| Viewing Analytics | 2차원 밀도 (시간×요일) |
|**Scatter / Bubble**| Ad Revenue, Funnel | 상관관계, 다차원 비교 |
|**Funnel**| Funnel & Segments | 전환율 분석 |
|**Table**| Overview | 상세 데이터, 조건부 서식 |

---

## Part B: AI/BI Genie Space — 자연어로 데이터 탐색

### Step 6: Genie Space 생성

#### Claude에게 요청하기

```
AI/BI Genie Space를 만들어서 비즈니스 사용자가 자연어로 데이터를 탐색할 수 있게 해줘.

Genie Space 이름: SmartTV Data Explorer

연결 테이블:
- gold.daily_viewing_summary
- gold.user_profiles
- gold.ad_performance
- gold.content_rankings
- gold.weekly_kpi_trends
- gold.user_segments
- gold.fasttv_revenue_analysis
- gold.hourly_heatmap

Instructions:
- 한국어 질문을 이해하고 정확한 SQL로 변환
- 결과를 비즈니스 관점에서 해석하여 인사이트 제공
- 가능하면 시각화 제안 (어떤 차트가 적합한지)
- 금액은 USD, 비율은 % 단위로 표시
- 날짜 필터가 없으면 최근 30일 기본 적용

Sample Questions (12개):
1. "이번 달 가장 인기 있는 콘텐츠 Top 10은?"
2. "주말과 평일의 시청 패턴 차이를 보여줘"
3. "FastTV 광고 중 CTR이 가장 높은 광고 형식은?"
4. "Korea 지역의 프라임타임 시청률 추이는?"
5. "premium 티어 사용자의 시청 행동이 entry 사용자와 어떻게 달라?"

Genie Space를 생성해줘.
```

---

### Step 7: Genie Space 실습 — 12가지 비즈니스 질문

이 질문들을 Genie Space에 직접 입력하면서 결과를 확인합니다.

#### 시청 분석 질문 (4개)

```
질문 1: "이번 달 가장 인기 있는 콘텐츠 Top 10은?"
→ content_rankings에서 unique_viewers 합산 순위

질문 2: "주말과 평일의 시청 패턴 차이를 보여줘"
→ daily_viewing_summary에서 is_weekend 기준 비교

질문 3: "Korea 지역에서 프라임타임에 가장 많이 보는 장르는?"
→ daily_viewing_summary에서 region='Korea', time_slot='prime_time' 필터

질문 4: "시청 완료율이 가장 높은 콘텐츠 유형은?"
→ daily_viewing_summary에서 avg_completion_rate 비교
```

#### 광고 분석 질문 (4개)

```
질문 5: "FastTV 광고 중 CTR이 가장 높은 광고 형식은?"
→ ad_performance에서 ad_format별 CTR 비교

질문 6: "광고 수익이 가장 높은 시간대는?"
→ fasttv_revenue_analysis에서 시간대별 revenue 합산

질문 7: "쿠팡 광고의 지난 달 성과 요약해줘"
→ ad_performance에서 advertiser='쿠팡' 필터

질문 8: "native 광고와 banner 광고의 전환율 차이는?"
→ ad_performance에서 ad_format별 CVR 비교
```

#### 사용자 분석 질문 (4개)

```
질문 9: "premium 티어 사용자와 entry 티어 사용자의 시청 행동 차이는?"
→ user_profiles에서 price_tier별 시청 피처 비교

질문 10: "heavy viewer 세그먼트의 특성을 알려줘"
→ user_segments에서 segment_name='heavy_viewer' 상세

질문 11: "음성 명령 사용률이 가장 높은 사용자 그룹은?"
→ user_profiles에서 voice_command_usage 기준 분석

질문 12: "시청 시간이 가장 많은 지역 Top 5와 각 지역의 인기 장르는?"
→ daily_viewing_summary에서 region별 합산 + favorite_genre
```

#### Claude에게 요청하기

```
위 12개 질문을 Genie Space에서 테스트해줘.

각 질문에 대해:
1. Genie가 생성한 SQL 쿼리
2. 쿼리 결과 요약
3. 비즈니스 인사이트 해석

을 정리해서 보여줘. Genie가 잘못 이해한 질문이 있으면 알려줘.
```

---

### Step 8: Genie Space 추가 질문 (심화)

#### Claude에게 요청하기

```
아래 심화 질문도 Genie Space에서 테스트해줘.

=== 크로스 분석 질문 ===
질문 13: "광고 CTR이 높은 사용자 세그먼트는 어떤 콘텐츠를 주로 시청하나?"
질문 14: "OLED TV 사용자와 일반 TV 사용자의 FastTV 광고 반응 차이는?"
질문 15: "저녁 시간대에 가장 효율적인 광고 형식은?"

=== 트렌드 질문 ===
질문 16: "지난 4주간 시청량 변화 추이를 주 단위로 보여줘"
질문 17: "가장 빠르게 성장하는 콘텐츠/채널은?"

각 질문의 결과와 인사이트를 보여줘.
```

---

## 학습 정리

| 개념 | 실습 내용 |
|------|-----------|
|**AI/BI Dashboard**| 4페이지 대시보드, 10+ 차트 유형 (Counter/Line/Bar/Pie/Heatmap/Scatter/Funnel/Table) |
|**대시보드 설계**| KPI 모니터링, 시청 분석, 광고 수익, 사용자 세그먼트 |
|**AI/BI Genie Space**| 자연어 → SQL 변환, 비즈니스 사용자 데이터 탐색 |
|**Genie 실습**| 17개 자연어 질문 (시청/광고/사용자/크로스/트렌드) |

---

## 다음 단계

→ [Module 4: Structured Streaming - 실시간 데이터 처리](../04-streaming/README.md)
