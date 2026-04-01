# Module 4: Structured Streaming — 실시간 데이터 처리

## 이 가이드 사용 방법

>** 이 교육 자료는 Claude Code (또는 Cursor)와 함께 사용합니다.**>
> 이 모듈에서는 UC Volume에 주기적으로 이벤트 데이터를 생성하고,
> Auto Loader + Structured Streaming으로 실시간 처리하는 End-to-End 흐름을 구축합니다.

---

## 학습 목표

- UC Volume에 ** 주기적으로 가상 데이터 생성**(Databricks App 활용)
-**Auto Loader** 로 새 파일 자동 감지 및 수집
-**Structured Streaming** 으로 실시간 Bronze → Silver 처리
-**SDP + Streaming Table** 로 선언적 실시간 파이프라인 구축

---

## End-to-End 아키텍처

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Event    │  │ UC Volume  │  │ Auto Loader │  │ SDP Pipeline │  │ Gold MV   │
│ Generator  │───→│ /landing/  │───→│ cloudFiles  │───→│ Bronze→Silver│───→│ 집계 자동  │
│ (DB App)   │  │ *.json    │  │ 자동 감지  │  │ 증분 처리  │  │ 갱신     │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
   주기적 생성     파일 저장      스트림 수집     정제+검증      대시보드 반영
```

### 실무 대응

| 교육 (이 워크샵) | 실무 (Smart TV OEM) |
|-----------------|---------------|
| Databricks App (이벤트 생성기) | IoT Gateway → S3/ADLS/Event Hub |
| UC Volume (JSON 파일) | S3 버킷 / ADLS / Event Hub |
| Auto Loader | Auto Loader (동일) 또는 Kafka Connector |
| SDP Pipeline | SDP Pipeline (동일) |

---

## Step 1: Volume 및 Landing Zone 생성

### Claude에게 요청하기

```
실시간 이벤트 데이터를 수집할 Volume과 Landing Zone을 만들어줘.

카탈로그: current_user() 기반 동적 생성

1. Volume 생성:
  - {catalog}.bronze.landing_zone (MANAGED Volume)

2. Landing Zone 디렉토리 구조:
  /Volumes/{catalog}/bronze/landing_zone/
  ├── viewing_events/   ← 시청 이벤트 JSON
  ├── click_events/    ← 클릭 이벤트 JSON
  └── ad_events/     ← 광고 이벤트 JSON

3. 디렉토리를 생성하고 구조를 확인해줘.

Volume이 뭔지, 실무에서 S3/ADLS 대신 Volume을 사용하는 이점도 설명해줘.
```

---

## Step 2: 이벤트 생성기 스크립트

### Claude에게 요청하기

```
실시간 시뮬레이션을 위한 이벤트 생성기 스크립트를 만들어줘.
이 스크립트는 주기적으로 JSON 이벤트 파일을 Volume에 생성합니다.

=== 시청 이벤트 (viewing_events) ===
배치당 100건, JSON 형식:
{
 "event_id": "uuid",
 "device_id": "기존 bronze.devices에서 랜덤 선택",
 "user_profile_id": "1~4",
 "content_type": "live_tv/vod/app/fasttv",
 "channel_or_app": "MBC/Netflix/YouTube 등",
 "genre": "drama/entertainment/news 등",
 "start_time": "현재 시간 기준 랜덤",
 "duration_minutes": "1~120 (로그정규분포)",
 "completion_rate": "0.0~1.0",
 "event_timestamp": "현재 시간"
}

=== 클릭 이벤트 (click_events) ===
배치당 200건

=== 광고 이벤트 (ad_events) ===
배치당 50건

파일 이름 형식: {event_type}_{timestamp}_{batch_id}.json
예: viewing_events_20250301_120000_001.json

먼저 테스트로 각 이벤트 타입별 1배치씩 생성하고,
Volume에 파일이 잘 저장되었는지 확인해줘.
```

---

## Step 3: Databricks App으로 이벤트 생성기 배포

### Claude에게 요청하기

```
이벤트 생성기를 Databricks App으로 배포해줘.
주기적으로 (30초마다) 이벤트를 생성하는 앱이야.

앱 이름: smarttv-event-generator
프레임워크: FastAPI

기능:
- GET / : 앱 상태 확인 (생성 건수, 마지막 생성 시간)
- POST /generate : 수동 이벤트 생성 트리거
- 백그라운드 스케줄러: 30초마다 자동으로 이벤트 배치 생성

설정:
- 배치 크기: viewing 100건, click 200건, ad 50건
- Volume 경로: /Volumes/{catalog}/bronze/landing_zone/

app.yaml에 SQL Warehouse 리소스도 추가해줘.
앱을 생성하고 배포해줘.
```

---

## Step 4: Auto Loader로 스트리밍 수집

### Claude에게 요청하기

```
Auto Loader를 사용해서 Volume에 들어오는 JSON 파일을 자동으로 수집하는
Structured Streaming 쿼리를 만들어줘.

=== 시청 이벤트 Auto Loader ===

spark.readStream
 .format("cloudFiles")
 .option("cloudFiles.format", "json")
 .option("cloudFiles.inferColumnTypes", "true")
 .option("cloudFiles.schemaLocation", "/Volumes/.../landing_zone/_schema/viewing")
 .load("/Volumes/.../landing_zone/viewing_events/")
 .withColumn("_ingested_at", current_timestamp())
 .withColumn("_source_file", input_file_name())

타겟: bronze.live_viewing_events (append 모드)

=== 클릭 이벤트, 광고 이벤트도 동일하게 ===

3개 스트리밍 쿼리를 각각 실행하고,
이벤트 생성기가 새 파일을 추가하면 자동으로 수집되는지 확인해줘.

Auto Loader의 핵심 장점:
- 새 파일 자동 감지 (폴링 불필요)
- 스키마 추론 + 진화 자동 처리
- Exactly-once 보장 (체크포인트)
- 수십만 파일도 효율적 처리

이 내용도 설명해줘.
```

---

## Step 5: SDP로 실시간 파이프라인 구성

### Claude에게 요청하기

```
Auto Loader 수집부터 Silver 정제까지를 SDP 파이프라인으로 구성해줘.

파이프라인 이름: smarttv_demo_streaming_pipeline

=== Bronze Streaming Tables (Auto Loader) ===

1. bronze_live_viewing (@dp.table)
  - cloudFiles로 viewing_events/ 수집
  - @dp.expect_or_fail("valid_event_id", "event_id IS NOT NULL")
  - _ingested_at, _source_file 메타 컬럼 추가

2. bronze_live_clicks (@dp.table)
  - cloudFiles로 click_events/ 수집
  - @dp.expect_or_fail("valid_timestamp", "event_timestamp IS NOT NULL")

3. bronze_live_ads (@dp.table)
  - cloudFiles로 ad_events/ 수집
  - @dp.expect_or_drop("valid_bid", "bid_price_usd > 0")

=== Silver Streaming Tables (증분 정제) ===

4. silver_live_viewing (@dp.table)
  - bronze_live_viewing 읽기
  - duration 검증, time_slot 파생
  - devices 테이블 JOIN (model_name, region)

5. silver_live_clicks (@dp.table)
  - 세션 통계 추가
  - devices JOIN

6. silver_live_ads (@dp.table)
  - CTR 관련 파생 컬럼
  - devices JOIN

=== Gold Materialized Views (집계) ===

7. gold_live_viewing_summary (@dp.materialized_view)
  - 최근 1시간 기준 실시간 시청 요약
  - region, content_type별 집계

8. gold_live_ad_performance (@dp.materialized_view)
  - 실시간 광고 성과

파이프라인을 생성하고, 이벤트 생성기가 데이터를 넣으면
실시간으로 Bronze→Silver→Gold가 처리되는지 확인해줘.

SDP에서 Streaming Table과 Materialized View의 차이도 설명해줘.
```

---

## Step 6: 실시간 모니터링

### Claude에게 요청하기

```
실시간 파이프라인이 잘 동작하는지 모니터링해줘.

1. 이벤트 생성기 상태 확인
  - 앱이 정상 실행 중인지
  - 최근 생성된 파일 목록 (Volume)

2. 스트리밍 수집 상태
  - Bronze 테이블에 새 데이터가 들어오고 있는지
  - 각 테이블의 최근 _ingested_at 시간

3. 파이프라인 처리 상태
  - Silver, Gold 테이블 갱신 확인
  - Expectations 통과/실패 비율

4. End-to-End 레이턴시
  - 이벤트 생성 → Volume 저장 → Bronze 수집 → Silver 정제 → Gold 집계
  - 각 단계별 소요 시간 측정

결과를 요약 대시보드 형태로 보여줘.
```

---

## 학습 정리

| 개념 | 실습 내용 |
|------|-----------|
|**UC Volume**| 파일 기반 데이터 랜딩존 (실무 S3/ADLS 대응) |
|**Databricks App**| 이벤트 생성기 배포 (FastAPI) |
|**Auto Loader**| cloudFiles 포맷, 새 파일 자동 감지, 스키마 추론 |
|**Structured Streaming**| readStream, append 모드, 체크포인트 |
|**SDP + Streaming**| @dp.table + Auto Loader, 실시간 Bronze→Silver→Gold |
|** 실시간 모니터링**| 레이턴시 측정, Expectations 확인 |

---

## 다음 단계

→ [Module 5: ML/AI - 개인화 추천 모델](../05-ml/README.md)
