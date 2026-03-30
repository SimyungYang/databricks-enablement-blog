# Databricks notebook source
# MAGIC %md
# MAGIC # 05. AI/BI 대시보드 & Genie Space 구성
# MAGIC
# MAGIC Gold 테이블을 기반으로 **AI/BI 대시보드** 와 **Genie Space** 를 구성합니다.
# MAGIC
# MAGIC | 기능 | 설명 | 대상 사용자 |
# MAGIC |------|------|------------|
# MAGIC |**AI/BI Dashboard**| SQL 기반 시각화 대시보드 | 데이터 분석가, 경영진 |
# MAGIC |**Genie Space**| 자연어로 데이터 탐색 | 비기술 비즈니스 사용자 |
# MAGIC
# MAGIC >**사전 조건:** 이 노트북을 실행하기 전에 **03_silver_gold_ctas** 노트북을 먼저 실행하세요.
# MAGIC > 이 노트북의 모든 쿼리는 03에서 생성한 Gold 테이블(suffix 없음)에 의존합니다.
# MAGIC >
# MAGIC >**이 노트북은 대시보드/Genie에 사용할 쿼리를 검증하는 용도입니다.**
# MAGIC > 실제 대시보드와 Genie Space 생성은 Claude Code(AI Dev Kit)를 통해 수행합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 공통 설정

# COMMAND ----------

# 현재 사용자 이메일에서 prefix 추출
username = spark.sql("SELECT current_user()").collect()[0][0]
user_prefix = username.split("@")[0].replace(".", "_").replace("-", "_")
CATALOG = f"{user_prefix}_smarttv_training"

spark.sql(f"USE CATALOG {CATALOG}")
print(f"👤 사용자: {username}")
print(f"✅ 카탈로그: {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold 테이블 현황 확인

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT table_name,
# MAGIC    CASE
# MAGIC     WHEN table_name IN ('daily_viewing_summary','user_profiles','ad_performance','content_rankings') THEN '기본 Gold'
# MAGIC     ELSE '심화 Gold (대시보드용)'
# MAGIC    END AS category
# MAGIC FROM information_schema.tables
# MAGIC WHERE table_schema = 'gold'
# MAGIC ORDER BY category, table_name;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 1: 대시보드 쿼리 검증
# MAGIC
# MAGIC 아래 쿼리들은 AI/BI 대시보드의 각 위젯(차트/테이블/KPI 카드)에 사용됩니다.
# MAGIC 먼저 노트북에서 검증한 후, 대시보드로 배포합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### 📊 Page 1: Executive Overview (경영진 요약)

# COMMAND ----------

# MAGIC %md
# MAGIC #### KPI 카드: 최근 주간 핵심 지표

# COMMAND ----------

# MAGIC %sql
# MAGIC -- KPI 카드용: 최신 주간 지표 + 전주 대비 변화율
# MAGIC SELECT
# MAGIC  week_start,
# MAGIC  weekly_active_users AS active_users,
# MAGIC  users_wow_pct AS users_change_pct,
# MAGIC  ROUND(total_viewing_minutes / 60, 0) AS viewing_hours,
# MAGIC  minutes_wow_pct AS viewing_change_pct,
# MAGIC  weekly_ad_revenue_usd AS ad_revenue,
# MAGIC  revenue_wow_pct AS revenue_change_pct,
# MAGIC  weekly_ctr AS avg_ctr
# MAGIC FROM gold.weekly_kpi_trends
# MAGIC ORDER BY week_start DESC
# MAGIC LIMIT 1;

# COMMAND ----------

# MAGIC %md
# MAGIC #### 라인 차트: 주간 KPI 추이

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 주간 Active Users & 광고 수익 추이
# MAGIC SELECT
# MAGIC  week_start,
# MAGIC  weekly_active_users,
# MAGIC  ROUND(total_viewing_minutes / 60, 0) AS total_viewing_hours,
# MAGIC  weekly_ad_revenue_usd
# MAGIC FROM gold.weekly_kpi_trends
# MAGIC ORDER BY week_start;

# COMMAND ----------

# MAGIC %md
# MAGIC #### 파이 차트: 사용자 가치 세그먼트 분포

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 사용자 가치 세그먼트 분포
# MAGIC SELECT
# MAGIC  value_segment,
# MAGIC  COUNT(*) AS user_count,
# MAGIC  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
# MAGIC FROM gold.user_segments
# MAGIC GROUP BY value_segment
# MAGIC ORDER BY user_count DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 📊 Page 2: 시청 분석 (Viewing Analytics)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 히트맵: 요일 × 시간대별 시청자 수 (Korea)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 히트맵용: 요일 × 시간대 active devices
# MAGIC SELECT day_name, hour_of_day, SUM(active_devices) AS devices
# MAGIC FROM gold.hourly_heatmap
# MAGIC WHERE region = 'Korea'
# MAGIC GROUP BY day_name, day_of_week, hour_of_day
# MAGIC ORDER BY day_of_week, hour_of_day;

# COMMAND ----------

# MAGIC %md
# MAGIC #### 바 차트: 콘텐츠 인기도 Top 10

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 전체 기간 인기 콘텐츠/채널 Top 10
# MAGIC SELECT channel_or_app, genre,
# MAGIC    SUM(daily_unique_viewers) AS total_viewers,
# MAGIC    SUM(daily_total_minutes) AS total_minutes,
# MAGIC    ROUND(AVG(avg_completion_rate), 2) AS avg_completion
# MAGIC FROM gold.content_rankings
# MAGIC GROUP BY channel_or_app, genre
# MAGIC ORDER BY total_viewers DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC #### 스택 바 차트: 지역별 콘텐츠 유형 분포

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 지역별 × 콘텐츠 유형별 시청 비율
# MAGIC SELECT
# MAGIC  region,
# MAGIC  content_type,
# MAGIC  SUM(total_views) AS views,
# MAGIC  ROUND(SUM(total_views) * 100.0 / SUM(SUM(total_views)) OVER (PARTITION BY region), 1) AS pct
# MAGIC FROM gold.daily_viewing_summary
# MAGIC GROUP BY region, content_type
# MAGIC ORDER BY region, views DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 📊 Page 3: FastTV 광고 수익 (Ad Revenue)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 라인 차트: 일별 광고 수익 추이

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 일별 광고 수익 추이 (지역별)
# MAGIC SELECT impression_date, region,
# MAGIC    SUM(revenue_usd) AS daily_revenue,
# MAGIC    SUM(impressions) AS daily_impressions,
# MAGIC    ROUND(AVG(ecpm_usd), 4) AS avg_ecpm
# MAGIC FROM gold.fasttv_revenue_analysis
# MAGIC GROUP BY impression_date, region
# MAGIC ORDER BY impression_date;

# COMMAND ----------

# MAGIC %md
# MAGIC #### 테이블: 광고주별 성과 랭킹

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 광고주별 총합 성과 (대시보드 테이블용)
# MAGIC SELECT
# MAGIC  advertiser,
# MAGIC  ad_category,
# MAGIC  SUM(impressions) AS total_impressions,
# MAGIC  SUM(clicks) AS total_clicks,
# MAGIC  ROUND(SUM(clicks) * 100.0 / SUM(impressions), 2) AS ctr,
# MAGIC  SUM(conversions) AS total_conversions,
# MAGIC  ROUND(SUM(total_spend_usd), 2) AS total_revenue_usd,
# MAGIC  ROUND(SUM(total_spend_usd) / NULLIF(SUM(impressions), 0) * 1000, 4) AS ecpm
# MAGIC FROM gold.ad_performance
# MAGIC GROUP BY advertiser, ad_category
# MAGIC ORDER BY total_revenue_usd DESC
# MAGIC LIMIT 15;

# COMMAND ----------

# MAGIC %md
# MAGIC #### 바 차트: 시간대 × 광고 형식별 eCPM

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 시간대별 광고 형식별 eCPM 비교
# MAGIC SELECT
# MAGIC  time_slot,
# MAGIC  ad_format,
# MAGIC  ROUND(AVG(ecpm_usd), 4) AS avg_ecpm,
# MAGIC  SUM(revenue_usd) AS total_revenue
# MAGIC FROM gold.fasttv_revenue_analysis
# MAGIC GROUP BY time_slot, ad_format
# MAGIC ORDER BY time_slot, avg_ecpm DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 📊 Page 4: 콘텐츠 퍼널 & 사용자 세그먼트

# COMMAND ----------

# MAGIC %md
# MAGIC #### 퍼널 차트: 콘텐츠 소비 퍼널 (전체 평균)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 퍼널 차트용: 단계별 평균 전환율
# MAGIC SELECT
# MAGIC  'Home Impressions' AS stage, 1 AS stage_order,
# MAGIC  ROUND(AVG(home_impressions), 0) AS avg_daily_count,
# MAGIC  100.0 AS rate_pct
# MAGIC FROM gold.content_engagement_funnel
# MAGIC UNION ALL
# MAGIC SELECT 'Content Selections', 2,
# MAGIC  ROUND(AVG(content_selections), 0),
# MAGIC  ROUND(AVG(selection_rate_pct), 1)
# MAGIC FROM gold.content_engagement_funnel
# MAGIC UNION ALL
# MAGIC SELECT 'Viewing Starts', 3,
# MAGIC  ROUND(AVG(viewing_starts), 0),
# MAGIC  ROUND(AVG(start_rate_pct), 1)
# MAGIC FROM gold.content_engagement_funnel
# MAGIC UNION ALL
# MAGIC SELECT 'Viewing Completions', 4,
# MAGIC  ROUND(AVG(viewing_completions), 0),
# MAGIC  ROUND(AVG(completion_rate_pct), 1)
# MAGIC FROM gold.content_engagement_funnel
# MAGIC ORDER BY stage_order;

# COMMAND ----------

# MAGIC %md
# MAGIC #### 버블 차트: 세그먼트별 시청시간 vs 광고 CTR

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 세그먼트별 시청시간 × 광고 CTR 분포 (버블 차트용)
# MAGIC SELECT
# MAGIC  viewing_segment,
# MAGIC  ad_segment,
# MAGIC  COUNT(*) AS user_count,
# MAGIC  ROUND(AVG(avg_daily_viewing_minutes), 1) AS avg_daily_minutes,
# MAGIC  ROUND(AVG(ad_ctr), 2) AS avg_ad_ctr,
# MAGIC  ROUND(AVG(total_viewing_minutes), 0) AS avg_total_minutes
# MAGIC FROM gold.user_segments
# MAGIC GROUP BY viewing_segment, ad_segment
# MAGIC ORDER BY user_count DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 2: Claude Code로 대시보드 & Genie 생성하기
# MAGIC
# MAGIC 위 쿼리가 모두 검증되었으면, Claude Code에서 아래 프롬프트로 생성합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### AI/BI 대시보드 생성 프롬프트
# MAGIC
# MAGIC ```
# MAGIC AI/BI 대시보드를 만들어줘.
# MAGIC
# MAGIC 대시보드 이름: SmartTV Analytics Dashboard
# MAGIC 카탈로그: {현재 사용자}_smarttv_training
# MAGIC
# MAGIC === Page 1: Executive Overview ===
# MAGIC - KPI 카드 4개: Active Users (전주대비%), 시청시간(전주대비%), 광고수익(전주대비%), 평균CTR
# MAGIC  → gold.weekly_kpi_trends 최신 1행
# MAGIC - 라인 차트: 주간 Active Users & 광고 수익 추이
# MAGIC  → gold.weekly_kpi_trends
# MAGIC - 파이 차트: 사용자 가치 세그먼트 (high/medium/low value)
# MAGIC  → gold.user_segments
# MAGIC
# MAGIC === Page 2: Viewing Analytics ===
# MAGIC - 히트맵: 요일 × 시간대 시청자 수 (필터: region)
# MAGIC  → gold.hourly_heatmap
# MAGIC - 바 차트: 인기 콘텐츠 Top 10
# MAGIC  → gold.content_rankings
# MAGIC - 스택 바 차트: 지역별 콘텐츠 유형 비율
# MAGIC  → gold.daily_viewing_summary
# MAGIC
# MAGIC === Page 3: FastTV Ad Revenue ===
# MAGIC - 라인 차트: 일별 광고 수익 추이 (지역별)
# MAGIC  → gold.fasttv_revenue_analysis
# MAGIC - 테이블: 광고주별 성과 랭킹 (impressions, CTR, revenue, eCPM)
# MAGIC  → gold.ad_performance
# MAGIC - 바 차트: 시간대 × 광고형식별 eCPM
# MAGIC  → gold.fasttv_revenue_analysis
# MAGIC
# MAGIC === Page 4: Funnel & Segments ===
# MAGIC - 퍼널 차트: 홈노출 → 콘텐츠선택 → 시청시작 → 시청완료
# MAGIC  → gold.content_engagement_funnel
# MAGIC - 버블 차트: 세그먼트별 시청시간 vs CTR (버블크기=사용자수)
# MAGIC  → gold.user_segments
# MAGIC
# MAGIC 모든 쿼리는 위 노트북(05)에서 검증 완료됨.
# MAGIC SQL 쿼리를 먼저 execute_sql로 테스트한 후 대시보드를 생성해줘.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### Genie Space 생성 프롬프트
# MAGIC
# MAGIC ```
# MAGIC Genie Space를 만들어줘.
# MAGIC
# MAGIC 이름: SmartTV Intelligence
# MAGIC 카탈로그: {현재 사용자}_smarttv_training
# MAGIC
# MAGIC 연결 테이블 (9개):
# MAGIC - gold.weekly_kpi_trends (주간 KPI + 전주대비 변화율)
# MAGIC - gold.daily_viewing_summary (일별 시청 요약)
# MAGIC - gold.user_profiles (사용자 프로필 피처)
# MAGIC - gold.user_segments (사용자 세그먼트: viewing/ad/fasttv/value)
# MAGIC - gold.ad_performance (광고주별 성과)
# MAGIC - gold.fasttv_revenue_analysis (FastTV 수익 심층분석: eCPM, 수익변화율)
# MAGIC - gold.content_rankings (콘텐츠 인기도 랭킹)
# MAGIC - gold.content_engagement_funnel (소비 퍼널: 노출→선택→시청→완료)
# MAGIC - gold.hourly_heatmap (시간대별 시청/광고 히트맵)
# MAGIC
# MAGIC Instructions:
# MAGIC - 한국어 질문을 이해하고 SQL로 변환
# MAGIC - 가능하면 수치와 함께 비즈니스 인사이트를 제공
# MAGIC - 비교 질문에는 퍼센트 변화율을 포함
# MAGIC
# MAGIC Sample Questions:
# MAGIC 1. "이번 주 핵심 KPI 보여줘"
# MAGIC 2. "Korea 지역 프라임타임 시청자 수 추이는?"
# MAGIC 3. "광고 CTR이 가장 높은 시간대와 광고 형식 조합은?"
# MAGIC 4. "high_value 세그먼트 사용자의 선호 장르와 시청 패턴은?"
# MAGIC 5. "FastTV 광고 eCPM이 가장 높은 지역 Top 5는?"
# MAGIC 6. "콘텐츠 소비 퍼널에서 이탈이 가장 많은 단계는?"
# MAGIC 7. "주말 vs 평일 광고 수익 차이는?"
# MAGIC 8. "이탈 위험(ad_resistant) 사용자가 많은 지역은?"
# MAGIC 9. "쿠팡 광고 성과 요약해줘 (CTR, 전환율, 수익)"
# MAGIC 10. "전주 대비 시청시간이 가장 많이 증가한 콘텐츠 유형은?"
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 학습 정리
# MAGIC
# MAGIC ### AI/BI Dashboard의 장점
# MAGIC -**SQL만으로 시각화**: 별도 BI 도구(Tableau, Power BI) 없이 Databricks 안에서 완결
# MAGIC -**실시간 데이터 연결**: Gold 테이블이 갱신되면 대시보드도 자동 반영
# MAGIC -**공유 & 임베딩**: URL 공유, iframe 임베딩, 이메일 스케줄 전송 가능
# MAGIC -**파라미터 필터**: region, date_range 등 인터랙티브 필터 지원
# MAGIC
# MAGIC ### Genie Space의 장점
# MAGIC -**자연어 → SQL**: "이번 주 광고 수익은?" → SELECT 자동 생성
# MAGIC -**비기술 사용자 접근성**: SQL 몰라도 데이터 탐색 가능
# MAGIC -**Unity Catalog 연동**: 테이블 메타데이터/COMMENT 활용하여 정확한 SQL 생성
# MAGIC -**검증된 쿼리 저장**: 자주 쓰는 질문을 Verified Query로 등록 → 일관된 결과 보장
# MAGIC
# MAGIC ### 대시보드 vs Genie 선택 기준
# MAGIC
# MAGIC | | AI/BI Dashboard | Genie Space |
# MAGIC |---|---|---|
# MAGIC |**용도**| 정해진 KPI를 정기적으로 모니터링 | 자유로운 탐색, ad-hoc 질문 |
# MAGIC |**대상**| 경영진, 정기 리포트 수신자 | 비즈니스 분석가, PM, 마케터 |
# MAGIC |**강점**| 시각화, 레이아웃, 스케줄 공유 | 유연성, 새로운 질문에 즉시 대응 |
# MAGIC |**조합**| 대시보드로 이상 징후 발견 → Genie로 원인 파악 | |
