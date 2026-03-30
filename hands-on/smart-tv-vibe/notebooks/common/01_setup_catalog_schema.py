# Databricks notebook source
# MAGIC %md
# MAGIC # 01. 카탈로그 & 스키마 설정
# MAGIC
# MAGIC 이 노트북은 교육에 필요한 **Databricks 환경을 처음부터 구성** 합니다.
# MAGIC
# MAGIC >**Databricks가 처음이신가요?**# MAGIC > Databricks는 데이터를 저장하고, 가공하고, 분석하는 **클라우드 기반 통합 데이터 플랫폼** 입니다.
# MAGIC > 이 노트북에서는 데이터를 체계적으로 관리하기 위한 "폴더 구조"를 만든다고 생각하시면 됩니다.
# MAGIC
# MAGIC ### 무엇을 하나요?
# MAGIC 1. 사용자 전용 **카탈로그** 생성 (데이터를 담는 최상위 폴더)
# MAGIC 2.**Bronze / Silver / Gold 스키마** 생성 (Medallion Architecture)
# MAGIC 3.**UC Volume** 생성 (실시간 이벤트 파일 랜딩존)
# MAGIC
# MAGIC ### 왜 필요한가요?
# MAGIC - 참가자마다 **독립된 환경** 에서 실습하기 위해 사용자별 카탈로그를 만듭니다.
# MAGIC - 데이터 품질 단계(Bronze→Silver→Gold)를 **스키마 단위** 로 분리하는 것이 Databricks 모범사례입니다.
# MAGIC
# MAGIC ### 소요 시간: 약 1분

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: 사용자 이름 기반 카탈로그 이름 생성
# MAGIC
# MAGIC**무엇을 하나요?**# MAGIC 현재 Databricks에 로그인한 계정의 이메일 주소에서 사용자명을 추출하여,
# MAGIC 교육용 카탈로그 이름을 자동으로 만듭니다.
# MAGIC
# MAGIC**예시:**`john.doe@company.com` → `john_doe_smarttv_training`
# MAGIC
# MAGIC**왜 이렇게 하나요?**# MAGIC 교육 참가자가 여러 명이므로, 각자의 이메일을 기반으로 고유한 이름을 만들어
# MAGIC 서로의 데이터가 섞이지 않도록 합니다.
# MAGIC
# MAGIC**어떻게 동작하나요?**# MAGIC - `spark.sql("SELECT current_user()")` — Databricks에 내장된 SQL 함수로, 현재 로그인한 사용자의 이메일을 가져옵니다.
# MAGIC - 이메일에서 `@` 앞부분만 추출하고, `.`과 `-`를 `_`로 바꿔서 카탈로그 이름 규칙에 맞게 변환합니다.

# COMMAND ----------

# 현재 사용자 이메일에서 prefix 추출
username = spark.sql("SELECT current_user()").collect()[0][0]
user_prefix = username.split("@")[0].replace(".", "_").replace("-", "_")
CATALOG = f"{user_prefix}_smarttv_training"

print(f"👤 사용자: {username}")
print(f"📦 생성할 카탈로그: {CATALOG}")
print()
print("이 카탈로그 안에 모든 교육용 데이터가 저장됩니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: 카탈로그 생성
# MAGIC
# MAGIC ### Unity Catalog란?
# MAGIC**Unity Catalog** 는 Databricks의 **중앙 집중식 데이터 관리 시스템** 입니다.
# MAGIC 쉽게 말해, 회사의 모든 데이터(테이블, 파일, ML 모델 등)를 **하나의 장소에서 체계적으로 관리** 하는 "데이터 도서관"입니다.
# MAGIC
# MAGIC -**누가** 어떤 데이터에 접근할 수 있는지 (권한 관리)
# MAGIC -**어디에** 어떤 데이터가 있는지 (검색 & 탐색)
# MAGIC -**어떻게** 데이터가 사용되고 있는지 (데이터 계보 추적)
# MAGIC
# MAGIC 이 모든 것을 Unity Catalog가 담당합니다.
# MAGIC
# MAGIC ### 카탈로그(Catalog)란?
# MAGIC**카탈로그** 는 Unity Catalog의 **최상위 컨테이너** 로, 컴퓨터의 "드라이브(C:, D:)"와 비슷한 개념입니다.
# MAGIC 회사에서는 보통 환경별(`dev`, `prod`) 또는 부서별(`finance`, `marketing`)로 카탈로그를 나눕니다.
# MAGIC
# MAGIC 이 교육에서는 참가자별로 하나의 카탈로그를 생성합니다.
# MAGIC
# MAGIC**아래 코드가 하는 일:**# MAGIC - `CREATE CATALOG IF NOT EXISTS` — 카탈로그가 없으면 새로 만들고, 이미 있으면 건너뜁니다.
# MAGIC - `USE CATALOG` — 이후 명령에서 이 카탈로그를 기본으로 사용하겠다고 선언합니다.

# COMMAND ----------

spark.sql(f"""
  CREATE CATALOG IF NOT EXISTS {CATALOG}
  COMMENT 'Smart TV Workshop catalog for ({username})'
""")
spark.sql(f"USE CATALOG {CATALOG}")
print(f"✅ 카탈로그 '{CATALOG}' 생성 완료!")
print(f"  이제 이 카탈로그 안에 스키마와 테이블을 만들 수 있습니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Medallion Architecture 스키마 생성
# MAGIC
# MAGIC ### 스키마(Schema)란?
# MAGIC**스키마** 는 카탈로그 안에서 테이블을 그룹으로 묶는 단위입니다.
# MAGIC 컴퓨터로 비유하면 "폴더"에 해당합니다. (카탈로그가 드라이브라면, 스키마는 그 안의 폴더입니다.)
# MAGIC
# MAGIC ### Medallion Architecture란?
# MAGIC Databricks에서 권장하는 데이터 품질 관리 패턴으로, 데이터를 **3단계로 나누어 점진적으로 정제** 합니다.
# MAGIC
# MAGIC >**실생활 비유: 공장의 생산 라인을 떠올려 보세요.**# MAGIC > -**Bronze (원재료 창고)**— 공장에 도착한 원재료를 그대로 보관합니다. 불량품이 섞여 있을 수 있지만, 일단 모두 보관합니다.
# MAGIC > -**Silver (가공 공정)**— 원재료에서 불량품을 골라내고, 규격에 맞게 가공합니다. 사용 가능한 부품이 됩니다.
# MAGIC > -**Gold (완성품 매장)**— 가공된 부품을 조립하여 완성된 제품을 만듭니다. 고객(경영진, 대시보드)이 바로 사용할 수 있습니다.
# MAGIC
# MAGIC | 스키마 | 역할 | 데이터 특성 |
# MAGIC |--------|------|------------|
# MAGIC |**bronze**| 원본 저장 | 가공 없이 그대로 저장. 문제 시 여기서 재처리 |
# MAGIC |**silver**| 정제/변환 | NULL 제거, 타입 통일, 파생 컬럼 추가 |
# MAGIC |**gold**| 분석/서빙 | 비즈니스 KPI 집계, 대시보드/ML 모델이 직접 사용 |
# MAGIC
# MAGIC ```
# MAGIC {사용자}_smarttv_training (카탈로그)
# MAGIC ├── bronze ← 스마트TV에서 들어오는 원본 로그
# MAGIC ├── silver ← 정제된 데이터 (분석 가능한 상태)
# MAGIC └── gold  ← 비즈니스 인사이트 (대시보드, Genie에서 사용)
# MAGIC ```
# MAGIC
# MAGIC**아래 코드가 하는 일:**# MAGIC - `for` 루프로 bronze, silver, gold 세 개의 스키마를 한 번에 생성합니다.
# MAGIC - `CREATE SCHEMA IF NOT EXISTS` — 스키마가 없으면 새로 만들고, 이미 있으면 건너뜁니다.

# COMMAND ----------

for schema, comment in [
  ("bronze", "원본 데이터 저장 (Raw ingestion layer)"),
  ("silver", "정제 및 변환된 데이터 (Cleaned & enriched)"),
  ("gold",  "분석 및 서빙용 집계 데이터 (Business-level aggregates)"),
]:
  spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema} COMMENT '{comment}'")
  print(f" ✅ {CATALOG}.{schema} — {comment}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: UC Volume 생성 (실시간 이벤트 랜딩존)
# MAGIC
# MAGIC ### Volume이란?
# MAGIC**Volume** 은 Unity Catalog에서 파일을 저장하는 공간으로, 쉽게 말해 **클라우드 위의 공유 폴더** 입니다.
# MAGIC 일반 컴퓨터의 공유 드라이브(예: Google Drive, OneDrive)처럼,
# MAGIC 여러 사람이나 시스템이 파일을 올리고 읽을 수 있는 저장소라고 생각하면 됩니다.
# MAGIC
# MAGIC ### 왜 필요한가요?
# MAGIC 실무에서는 외부 시스템(IoT 장비, 앱 서버 등)이 클라우드 저장소(S3, ADLS)에 파일을 떨어뜨리면,
# MAGIC Databricks가 이 파일을 **자동으로 감지하여 읽어들입니다.** 이 교육에서는 **UC Volume** 이 그 역할을 합니다.
# MAGIC
# MAGIC ### 이 교육에서의 데이터 흐름:
# MAGIC 1.**06번 노트북** 의 이벤트 생성기 앱이 스마트TV 로그를 흉내 내어 이 Volume에 JSON 파일을 적재합니다.
# MAGIC 2.**04번 노트북** 의 SDP(Streaming Delta Pipeline)가 **Auto Loader** 로 새 파일을 자동 감지하여 수집합니다.
# MAGIC
# MAGIC**아래 코드가 하는 일:**# MAGIC - `CREATE VOLUME` — bronze 스키마 안에 `landing`이라는 Volume을 생성합니다.
# MAGIC - `dbutils.fs.mkdirs` — Volume 안에 이벤트 종류별 하위 폴더(viewing_events, click_events, ad_events)를 만듭니다.

# COMMAND ----------

spark.sql(f"CREATE VOLUME IF NOT EXISTS bronze.landing COMMENT '실시간 이벤트 파일 랜딩존 (Auto Loader 소스)'")
print(f" ✅ {CATALOG}.bronze.landing (Volume)")

# 랜딩존 하위 디렉토리 생성
landing_base = f"/Volumes/{CATALOG}/bronze/landing"
for subdir, desc in [
  ("viewing_events", "시청 이벤트 JSON"),
  ("click_events", "클릭 이벤트 JSON"),
  ("ad_events", "광고 이벤트 JSON"),
]:
  full_path = f"{landing_base}/{subdir}"
  try:
    dbutils.fs.mkdirs(full_path)
    print(f"  📁 {subdir}/ — {desc}")
  except:
    print(f"  📁 {subdir}/ — (이미 존재)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: 생성 결과 확인
# MAGIC
# MAGIC 아래 SQL 명령은 현재 카탈로그 안에 만들어진 **스키마 목록** 을 보여줍니다.
# MAGIC `bronze`, `silver`, `gold` 세 개의 스키마가 표시되면 정상입니다.
# MAGIC (기본적으로 `default`와 `information_schema`도 함께 표시될 수 있습니다.)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 스키마 목록 확인
# MAGIC SHOW SCHEMAS;

# COMMAND ----------

print(f"""
{'='*60}
 ✅ 환경 설정 완료!
{'='*60}

 카탈로그: {CATALOG}

 스키마:
  bronze — 원본 데이터 (디바이스, 시청로그, 클릭이벤트, 광고로그)
  silver — 정제 데이터 (NULL 제거, 타입 변환, 파생 컬럼)
  gold  — 분석용 집계 (KPI, 사용자 프로필, 광고 성과)

 Volume:
  /Volumes/{CATALOG}/bronze/landing/
  ├── viewing_events/ ← 시청 이벤트 JSON
  ├── click_events/  ← 클릭 이벤트 JSON
  └── ad_events/    ← 광고 이벤트 JSON

 다음 단계: 02_generate_synthetic_data 노트북을 실행하세요.
{'='*60}
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 요약 & 다음 단계
# MAGIC
# MAGIC ### 이 노트북에서 완료한 작업:
# MAGIC | 항목 | 설명 |
# MAGIC |------|------|
# MAGIC |**카탈로그**| `{사용자}_smarttv_training` — 교육용 데이터의 최상위 컨테이너 |
# MAGIC |**스키마 3개**| `bronze` (원본) → `silver` (정제) → `gold` (분석용) |
# MAGIC |**Volume**| `bronze.landing` — 실시간 이벤트 파일이 도착하는 공유 폴더 |
# MAGIC
# MAGIC ### 다음 노트북: `02_generate_synthetic_data`
# MAGIC 다음 노트북에서는 방금 만든 환경에 **스마트TV 가상 데이터(합성 데이터)** 를 생성합니다.
# MAGIC 디바이스 정보, 사용자 프로필, 시청 기록 등 실습에 필요한 기초 데이터를 Bronze 스키마에 적재합니다.
