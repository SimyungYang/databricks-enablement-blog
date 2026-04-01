# Databricks notebook source
# MAGIC %md
# MAGIC # 예지보전 피처 엔지니어링 (Predictive Maintenance Feature Engineering)
# MAGIC
# MAGIC ## 이 노트북의 목적
# MAGIC
# MAGIC 본 노트북에서는 **AI4I 2020 Predictive Maintenance Dataset**(UCI 공개 데이터셋)을 탐색하고, ML 모델이 "설비 고장"을 정확히 예측할 수 있도록 **원본 센서 데이터를 가공(피처 엔지니어링)** 하는 과정을 실습합니다.
# MAGIC
# MAGIC ### 왜 "피처 엔지니어링"이 필요한가?
# MAGIC
# MAGIC 10년 넘게 제조 AI 프로젝트를 해오면서 확실히 말할 수 있는 것은, **피처 엔지니어링이 모델 성능의 80%를 결정한다** 는 것입니다. 아무리 최신 알고리즘을 써도 피처가 나쁘면 정확도가 안 나옵니다. 반대로, 좋은 피처 하나가 알고리즘 10개를 이깁니다.
# MAGIC
# MAGIC 제조 현장에서 수집되는 센서 데이터(온도, 회전속도, 토크 등)는 그 자체로도 의미가 있지만, **숙련된 설비 엔지니어가 여러 센서값을 종합하여 판단하듯**ML 모델에게도 "종합 판단 지표"를 만들어 주면 예측 정확도가 크게 향상됩니다. 이 과정을 **피처 엔지니어링(Feature Engineering)** 이라고 합니다.
# MAGIC
# MAGIC 예를 들어, 토크가 40Nm이고 회전속도가 1500rpm이면 각각은 정상 범위이지만, 이 둘을 곱하여 계산한 **기계적 전력(Power)**이 급격히 높다면 설비에 과부하가 걸리고 있다는 경고 신호입니다. 실제 반도체/전자부품 제조 현장에서도 개별 센서값이 아니라 이런 **복합 지표** 를 기준으로 설비 이상을 판단합니다.
# MAGIC
# MAGIC > **현업에서는 이렇게 합니다:** 프로젝트 초기에 설비 엔지니어와 2~3일 동안 "피처 설계 워크숍"을 반드시 진행합니다. 데이터 사이언티스트 혼자서는 절대 좋은 피처를 만들 수 없습니다. "이 센서값이 이 정도면 위험한가요?"라는 질문을 수십 번 던지면서 도메인 지식을 피처로 번역하는 과정이 핵심입니다.
# MAGIC
# MAGIC ### 이 노트북의 전체 흐름
# MAGIC
# MAGIC ```
# MAGIC [1단계] 데이터 탐색(EDA)  →  [2단계] 피처 엔지니어링  →  [3단계] Train/Test 분할  →  [4단계] Delta Lake 저장  →  [5단계] 상관관계 분석
# MAGIC ```
# MAGIC
# MAGIC ### 활용하는 Databricks 핵심 기능
# MAGIC
# MAGIC | 기능 | 설명 | 제조 현장에서의 이점 |
# MAGIC |------|------|---------------------|
# MAGIC | **Delta Lake**| ACID 트랜잭션을 지원하는 데이터 저장 포맷 | 데이터 변환 중 오류가 나도 원본이 안전하게 보존됨. "실행 취소(Time Travel)"가 가능. **"3개월 전 모델이 왜 잘 됐는지" 추적하려면 그때 데이터가 필요한데, Delta Lake 없이는 이것이 불가능합니다.** |
# MAGIC | **Pandas on Spark API** | 대규모 데이터에서도 Pandas 문법 사용 가능 | Python/Pandas에 익숙한 분석가도 빅데이터를 바로 다룰 수 있음 |
# MAGIC | **Unity Catalog** | 테이블, 모델, 피처의 중앙 관리 및 계보(Lineage) 추적 | "이 모델이 어떤 데이터로 학습되었는가?"를 자동으로 추적하여 감사(Audit) 대응 가능 |
# MAGIC | **Apache Spark** | 분산 병렬 처리 엔진 | 지금은 10,000건이지만, 실제 공장에서는 센서가 초당 수백 건을 생성합니다. 월 데이터가 수천만 건이 되면 Pandas로는 메모리 부족으로 처리가 불가능합니다. |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 데이터 소스: UCI AI4I 2020 Predictive Maintenance Dataset
# MAGIC - **규모**: 10,000건의 산업 센서 데이터 (실제 현장에서는 수백만 건 이상이지만, 교육용으로 축소된 데이터셋)
# MAGIC - **센서 피처**: 공기 온도(K), 공정 온도(K), 회전속도(rpm), 토크(Nm), 공구 마모(min)
# MAGIC - **타겟 변수**: `machine_failure` (0 = 정상 가동, 1 = 고장 발생)
# MAGIC - **고장 유형**: 공구 마모 고장(TWF), 방열 고장(HDF), 전력 고장(PWF), 과부하 고장(OSF), 랜덤 고장(RNF)
# MAGIC - **제품 품질 등급**: L(Low), M(Medium), H(High) - 제품 품질에 따라 공정 조건이 다를 수 있음
# MAGIC
# MAGIC > **업계 벤치마크:** 이 데이터셋의 고장률은 약 3.4%입니다. 실제 반도체/전자부품 공장의 예지보전 데이터도 고장 비율이 1~5% 수준으로 매우 불균형합니다. 이런 불균형 데이터를 다루는 능력이 제조 AI 엔지니어의 핵심 역량입니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### ⚠️ 사전 요구사항 (실행 전 반드시 확인)
# MAGIC
# MAGIC - 이 노트북은 **가장 먼저 실행하는 실습 노트북** 입니다 (`01_overview`는 개념 설명만 포함되어 있어 코드가 없습니다)
# MAGIC - **클러스터 상태 확인**: 좌측 사이드바 > **Compute** 메뉴에서 클러스터가 "Running" 상태인지 확인하세요. 클러스터가 꺼져 있으면 노트북을 실행할 수 없습니다.
# MAGIC - **첫 실행 시**: 데이터셋이 자동으로 다운로드되며, 약 1~2분이 소요될 수 있습니다
# MAGIC - **실행 방법**: 각 셀을 순서대로 실행하려면 셀 우측 상단의 ▶ 버튼을 클릭하거나, `Shift + Enter` 키를 누르세요. 전체를 한 번에 실행하려면 상단 메뉴에서 **Run All** 을 선택하세요.

# COMMAND ----------

# MAGIC %pip install --quiet mlflow --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %md
# MAGIC > **안내:**위 셀은 ML 실험 추적 도구인 **MLflow** 패키지를 최신 버전으로 업그레이드하고, Python 환경을 재시작합니다. 실행 후 잠시(10~30초) 멈추는 것은 정상적인 동작입니다. "Python interpreter restarted" 메시지가 표시되면 다음 셀로 진행하세요.

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC > **환경 설정 완료.** 위 셀(`00-setup`)이 실행되면서 다음 변수들이 자동으로 설정되었습니다:
# MAGIC > - `catalog`: 사용할 Unity Catalog 이름 (데이터가 저장되는 최상위 폴더 개념)
# MAGIC > - `db`: 사용할 데이터베이스(스키마) 이름
# MAGIC > - `current_user`: 현재 로그인한 사용자 이름
# MAGIC >
# MAGIC > 이 변수들은 이후 테이블을 저장하거나 조회할 때 자동으로 사용됩니다.
# MAGIC >
# MAGIC > **현업에서는 이렇게 합니다:**이 setup 스크립트처럼 환경 설정을 **코드로 중앙 관리** 하는 것은 MLOps에서 매우 중요한 패턴입니다. catalog, schema, 경로 등을 각 노트북에서 하드코딩하면, 환경이 바뀔 때(개발 -> 스테이징 -> 운영) 모든 노트북을 수정해야 합니다. setup 스크립트 하나만 수정하면 되도록 설계하세요.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 데이터 탐색 (Exploratory Data Analysis, EDA)
# MAGIC
# MAGIC ### EDA란 무엇이고, 왜 해야 하나?
# MAGIC
# MAGIC ML 모델을 학습시키기 **전에**반드시 데이터를 눈으로 확인하는 과정을 **EDA(탐색적 데이터 분석)** 라고 합니다. 이는 제조 현장에서 설비를 점검할 때 먼저 외관을 살펴보고, 이상 소음이 있는지 확인하는 것과 같습니다.
# MAGIC
# MAGIC 솔직히 말하면, **EDA를 건너뛰고 바로 모델을 만드는 팀이 많습니다.**그리고 거의 예외 없이 나중에 후회합니다. "왜 모델 성능이 안 나오지?" 하고 원인을 찾다 보면 결국 데이터 문제였거든요. 센서가 3일간 고장나서 같은 값만 찍히고 있었다거나, 특정 시간대에 결측치가 집중되어 있다거나. **EDA에 투자하는 시간이 나중에 디버깅 시간의 10배를 절약해 줍니다.**
# MAGIC
# MAGIC ### EDA에서 확인할 핵심 포인트
# MAGIC
# MAGIC | 확인 항목 | 이유 | 제조 현장 비유 |
# MAGIC |----------|------|---------------|
# MAGIC | **데이터 건수**| 학습에 충분한 양인지 확인. 경험적으로 **고장 건수가 최소 200건 이상** 이어야 의미 있는 모델 학습 가능 | 품질 검사에서 샘플 수가 충분한지 확인하는 것과 같음 |
# MAGIC | **결측치(빈 값)**| 센서 오작동이나 수집 누락 파악. **결측률 5% 이상이면 해당 센서 데이터 수집 파이프라인 점검 필수** | 계기판의 값이 빠져있으면 판단할 수 없음 |
# MAGIC | **고장 비율(클래스 불균형)** | 정상:고장 비율이 극단적이면 모델이 "항상 정상"이라고만 예측할 위험 | 10,000건 중 고장은 약 340건(3.4%)뿐 - 매우 불균형한 데이터 |
# MAGIC | **센서값 분포** | 이상치(outlier)나 비정상적 패턴 발견 | 회전속도가 갑자기 0이 되거나, 온도가 비현실적으로 높은 경우 등 |
# MAGIC | **고장 유형별 분포** | 어떤 고장이 가장 빈번한지 파악 | 대책을 세울 때 가장 빈번한 고장부터 해결하는 것이 효율적 |
# MAGIC
# MAGIC > **많은 팀이 실수하는 포인트:**EDA 단계에서 가장 경계해야 할 것이 **'데이터 누수(Data Leakage)'**입니다. 예를 들어, 고장이 발생한 **후에** 기록된 센서값이 학습 데이터에 포함되면, 학습 성능은 완벽하지만 실제 운영에서는 처참한 결과를 냅니다. EDA에서 시간축(timestamp)을 반드시 확인하고, "이 데이터가 고장 발생 전에 수집된 것인가?"를 검증하세요.
# MAGIC
# MAGIC ### Databricks에서의 EDA
# MAGIC Databricks 노트북에서는 `display()` 함수를 사용하면 테이블 형태로 데이터를 바로 확인할 수 있고, 결과 하단의 **+ (차트 추가)** 버튼을 클릭하면 막대그래프, 히스토그램 등을 코딩 없이 생성할 수 있습니다. 또한 `%sql` 매직 커맨드를 사용하면 SQL 쿼리로도 데이터를 분석할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,원본 Bronze 데이터 확인
df_bronze = spark.table("lgit_pm_bronze")
display(df_bronze)

# COMMAND ----------

# MAGIC %md
# MAGIC > **결과 확인 포인트:**
# MAGIC > - **행 수**: 10,000건이 표시되는지 확인하세요. 데이터가 제대로 로드된 것입니다.
# MAGIC > - **`machine_failure` 컬럼**: 0은 정상 가동, 1은 고장을 의미합니다. 대부분이 0(정상)이고, 1(고장)은 약 3.4%(340건)에 불과합니다.
# MAGIC > - **센서 컬럼**: `air_temperature_k`(공기 온도, 켈빈), `process_temperature_k`(공정 온도), `rotational_speed_rpm`(회전속도), `torque_nm`(토크), `tool_wear_min`(공구 마모 시간)
# MAGIC > - **`type` 컬럼**: 제품 품질 등급으로 L(Low, 저품질), M(Medium, 중품질), H(High, 고품질)을 나타냅니다.
# MAGIC >
# MAGIC > **Tip**: 테이블 하단의 `+` 버튼을 클릭하면 차트를 추가할 수 있습니다. 예를 들어, `machine_failure`를 기준으로 막대 차트를 생성하면 정상/고장 비율을 시각적으로 확인할 수 있습니다.
# MAGIC >
# MAGIC > **현업에서는 이렇게 합니다:**실제 공장 데이터를 처음 받으면, 가장 먼저 하는 일이 **각 센서 컬럼의 min/max를 물리적 한계와 대조**하는 것입니다. 예를 들어 공기 온도가 -50K이거나 회전속도가 음수라면 센서 오류입니다. 이 데이터셋은 이미 정제되어 있지만, 실제 현장 데이터에서는 이런 이상값이 전체의 1~3%를 차지하는 경우가 흔합니다. **이상값을 무시하고 모델을 학습하면 성능이 5~15% 하락** 할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,데이터 통계 요약
display(df_bronze.describe())

# COMMAND ----------

# MAGIC %sql
# MAGIC -- ──────────────────────────────────────────────────────────────
# MAGIC -- 고장 유형별 분포 확인
# MAGIC -- 이 쿼리는 고장(machine_failure=1)과 정상(=0) 그룹별로
# MAGIC -- 5가지 고장 유형이 각각 몇 건 발생했는지 집계합니다.
# MAGIC --   TWF: 공구 마모 고장 (Tool Wear Failure)
# MAGIC --   HDF: 방열 고장 (Heat Dissipation Failure) - 냉각 불량
# MAGIC --   PWF: 전력 고장 (Power Failure) - 과부하
# MAGIC --   OSF: 과부하 고장 (Overstrain Failure) - 과도한 기계적 응력
# MAGIC --   RNF: 랜덤 고장 (Random Failure) - 예측 불가능한 돌발 고장
# MAGIC -- ──────────────────────────────────────────────────────────────
# MAGIC SELECT
# MAGIC   machine_failure,
# MAGIC   SUM(twf) as tool_wear_failure,
# MAGIC   SUM(hdf) as heat_dissipation_failure,
# MAGIC   SUM(pwf) as power_failure,
# MAGIC   SUM(osf) as overstrain_failure,
# MAGIC   SUM(rnf) as random_failure,
# MAGIC   COUNT(*) as total_count
# MAGIC FROM lgit_pm_bronze
# MAGIC GROUP BY machine_failure

# COMMAND ----------

# MAGIC %sql
# MAGIC -- ──────────────────────────────────────────────────────────────
# MAGIC -- 제품 타입별 고장률 분석
# MAGIC -- 제품 품질 등급(L/M/H)에 따라 고장률이 다른지 확인합니다.
# MAGIC -- 일반적으로 저품질(L) 제품의 공정은 고장률이 더 높을 수 있습니다.
# MAGIC -- 결과: failure_rate_pct가 높은 순서로 정렬되어 표시됩니다.
# MAGIC -- ──────────────────────────────────────────────────────────────
# MAGIC SELECT
# MAGIC   type as product_type,
# MAGIC   COUNT(*) as total,
# MAGIC   SUM(machine_failure) as failures,
# MAGIC   ROUND(SUM(machine_failure) / COUNT(*) * 100, 2) as failure_rate_pct
# MAGIC FROM lgit_pm_bronze
# MAGIC GROUP BY type
# MAGIC ORDER BY failure_rate_pct DESC

# COMMAND ----------

# DBTITLE 1,센서 데이터 분포 시각화 (Pandas on Spark)
# Pandas on Spark API: Spark의 대규모 병렬 처리 능력 + Pandas의 직관적 문법
# .pandas_api()를 호출하면 Spark DataFrame을 Pandas처럼 사용할 수 있습니다.
# 내부적으로는 여전히 Spark가 분산 처리하므로, 수백만 건도 처리 가능합니다.
psdf = df_bronze.pandas_api()
# .describe()는 각 센서 컬럼의 기초 통계량을 보여줍니다:
#   count: 데이터 건수, mean: 평균, std: 표준편차,
#   min/25%/50%/75%/max: 최소/1사분위/중앙값/3사분위/최대값
display(psdf[['air_temperature_k', 'process_temperature_k', 'rotational_speed_rpm', 'torque_nm', 'tool_wear_min']].describe())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. 피처 엔지니어링 (Feature Engineering)
# MAGIC
# MAGIC ### 피처 엔지니어링이란?
# MAGIC
# MAGIC ML 모델은 원본 센서 데이터를 그대로 입력받아도 학습이 가능하지만, **도메인 전문가의 지식을 반영한 파생 변수(피처)를 추가하면 예측 정확도가 크게 향상** 됩니다.
# MAGIC 이는 마치 숙련된 설비 엔지니어가 계기판의 숫자만 보는 것이 아니라, 여러 수치를 종합하여 "이 설비는 위험하다"고 판단하는 과정을 수학적으로 모델링하는 것입니다.
# MAGIC
# MAGIC **예시**: 토크(Torque)가 65Nm이고 회전속도가 1400rpm일 때, 각각은 정상 범위이지만 **둘을 곱한 전력(Power)이 비정상적으로 높다면** 설비에 과부하가 걸리고 있다는 신호입니다. 이처럼 단일 센서값으로는 보이지 않는 패턴을 포착하는 것이 피처 엔지니어링의 핵심입니다.
# MAGIC
# MAGIC > **제가 수많은 프로젝트에서 배운 교훈:**피처 엔지니어링은 "한 번 하고 끝나는 작업"이 아닙니다. 처음에는 5~7개 피처로 시작하되, 모델 성능을 보면서 피처를 **반복적으로 추가/삭제/수정**해야 합니다. 실무에서는 보통 **20~50개 피처** 까지 확장합니다. 여기서 7개로 시작하는 것은 PoC에 적절한 규모이며, 운영 6개월 후에는 시계열 피처(이동 평균, 트렌드 등)를 반드시 추가하세요.
# MAGIC
# MAGIC ### Spark DataFrame을 쓰는 이유
# MAGIC Databricks의 **Apache Spark**엔진을 사용하면, 수백만 건의 센서 데이터도 클러스터의 여러 노드에서 **병렬로 변환**할 수 있습니다. 지금은 10,000건이지만, 실제 LG Innotek 공장에서는 센서가 초당 수백 건을 생성합니다. **월 데이터가 수천만 건** 이 되면 Pandas로는 메모리 부족으로 처리가 불가능합니다. 처음부터 Spark로 작성해 두면 데이터가 100배, 1000배로 늘어나도 코드 변경 없이 클러스터 스케일업만으로 대응할 수 있습니다.
# MAGIC
# MAGIC ### 생성할 7개 파생 피처
# MAGIC
# MAGIC | # | 피처명 | 계산 방법 | 물리적 의미 | 고장 예측에서의 역할 |
# MAGIC |---|--------|----------|-----------|-------------------|
# MAGIC | 1 | **temp_diff** | 공정온도 - 공기온도 | 설비 내부의 발열 정도 | 온도차가 클수록 냉각 불량 또는 마찰 과열 의심 |
# MAGIC | 2 | **power** | 토크 x 회전속도 x 2pi/60 | 설비가 소비하는 기계적 전력(와트) | 전력이 비정상적으로 높으면 과부하 상태 |
# MAGIC | 3 | **tool_wear_rate** | 공구마모 / 회전속도 | 단위 회전당 마모 속도 | 마모 속도가 빠르면 공구 교체 시기 임박 |
# MAGIC | 4 | **strain** | 토크 x 공구마모 | 기계적 변형(스트레인) 지수 | 높은 토크 + 높은 마모 = 고장 위험 급증 |
# MAGIC | 5 | **overheat_flag** | 온도차 > 8.6K이면 1 | 과열 경고 플래그 | 이진(0/1) 변수로 과열 상태 직접 표시 |
# MAGIC | 6 | **product_quality** | L->0, M->1, H->2 | 제품 품질 등급 수치화 | ML 모델은 숫자만 입력받으므로 문자를 숫자로 변환 |
# MAGIC | 7 | **risk_score** | 정규화된 종합 위험 점수 | 여러 피처를 종합한 위험도 | 단일 지표로 설비 위험 수준 파악 |
# MAGIC
# MAGIC > **피처 7개면 예지보전 PoC에 적절합니다.**너무 적으면 모델이 패턴을 충분히 학습하지 못하고, 너무 많으면 과적합 위험이 있습니다. 실무에서는 이 7개를 기반으로 **시계열 피처(최근 1시간 이동 평균, 변화율 등)**와 **설비 메타데이터(설비 나이, 마지막 정비 후 경과 시간 등)** 를 추가하여 20~50개까지 확장합니다.
# MAGIC
# MAGIC ### 피처 생성의 물리학적 근거
# MAGIC
# MAGIC - **전력(Power) = 토크 x 각속도**: 기계공학의 기본 공식입니다. rpm을 rad/s로 변환하기 위해 `2pi/60`을 곱합니다. 이 값이 설비의 정격 전력을 초과하면 과부하(Power Failure) 발생 가능성이 높아집니다.
# MAGIC - **스트레인(Strain) = 토크 x 공구마모**: 공구가 마모된 상태에서 높은 토크가 가해지면, 공구 파손이나 가공 불량이 발생할 확률이 급격히 증가합니다. 이는 두 독립 변수의 **교호작용(Interaction Effect)**을 포착합니다. 실제 반도체/전자부품 공장에서는 이 피처를 **설비별 정비 이력** 과 결합하여 "정비 후 몇 시간째에 위험 구간 진입"을 예측하는 데 활용합니다.
# MAGIC - **과열 임계값 8.6K**: EDA에서 도출한 값으로, 공정온도와 공기온도의 차이가 8.6K(켈빈)을 초과하면 방열(Heat Dissipation) 고장이 빈번하게 발생하는 것으로 확인되었습니다.
# MAGIC
# MAGIC > **경고 - 과열 임계값 8.6K 사용 시 주의할 점:**이 값은 **현재 데이터 기준**이므로, **계절이 바뀌거나 설비가 교체되면 반드시 재검토**해야 합니다. 여름에는 공기 온도 자체가 높아서 온도차가 줄어들 수 있고, 겨울에는 반대입니다. 실무에서는 이런 임계값을 하드코딩하지 않고, **주기적으로 데이터 기반 재산출하는 파이프라인** 을 구축합니다. 처음에는 고정값으로 시작하되, 운영 3개월 후에는 반드시 동적 임계값으로 전환하세요.
# MAGIC
# MAGIC > **핵심 포인트**: 피처 엔지니어링은 ML 프로젝트에서 **모델 성능의 80%를 결정** 합니다. 아무리 좋은 알고리즘을 사용해도, 입력 피처가 고장 패턴을 잘 포착하지 못하면 정확한 예측이 불가능합니다. Kaggle 상위 솔루션을 분석해 보면, 알고리즘보다 피처 엔지니어링에서 차이가 납니다.

# COMMAND ----------

# DBTITLE 1,피처 엔지니어링 함수 정의
import pyspark.sql.functions as F
from pyspark.sql import DataFrame
import math


def engineer_pm_features(df: DataFrame) -> DataFrame:
    """
    예지보전(Predictive Maintenance) 피처 엔지니어링 함수

    원본 센서 데이터(온도, 회전속도, 토크, 공구 마모)로부터 7개의 파생 피처를 생성합니다.
    각 피처는 설비 엔지니어의 도메인 지식을 수학적으로 모델링한 것입니다.

    Parameters:
        df (DataFrame): 원본 Bronze 테이블의 Spark DataFrame.
                        필수 컬럼: air_temperature_k, process_temperature_k,
                        rotational_speed_rpm, torque_nm, tool_wear_min, type

    Returns:
        DataFrame: 원본 컬럼 + 7개 파생 피처가 추가된 Spark DataFrame.
                   추가 컬럼: temp_diff, power, tool_wear_rate, strain,
                   overheat_flag, product_quality, risk_score

    Note:
        - Spark DataFrame 기반이므로 데이터 크기에 관계없이 분산 처리됩니다.
        - 이 함수는 순수 변환(transformation)만 수행하며, 데이터를 저장하지 않습니다.
        - 실제 운영 환경에서는 이 함수를 Databricks Feature Store에 등록하여
          학습과 서빙에서 동일한 피처 변환을 보장할 수 있습니다.
    """

    df_features = (
        df
        # ──────────────────────────────────────────────────────────────
        # 피처 1: 온도차 (temp_diff)
        # 물리적 의미: 공정 온도와 주변 공기 온도의 차이.
        #   → 이 차이가 크다 = 설비 내부에서 발열이 심하다 = 냉각이 제대로 안 되고 있다
        #   → 방열 고장(Heat Dissipation Failure, HDF)의 직접적 원인
        # 단위: K(켈빈). 섭씨와 차이값은 동일 (ΔK = ΔC)
        # ──────────────────────────────────────────────────────────────
        .withColumn("temp_diff",
                    F.col("process_temperature_k") - F.col("air_temperature_k"))

        # ──────────────────────────────────────────────────────────────
        # 피처 2: 기계적 전력 (power), 단위: 와트(W)
        # 물리학 공식: P = τ × ω (전력 = 토크 × 각속도)
        #   - τ (tau): 토크, 단위 Nm (뉴턴미터)
        #   - ω (omega): 각속도, 단위 rad/s (라디안/초)
        #   - rpm → rad/s 변환: ω = rpm × 2π / 60
        # 제조 현장 의미: 설비가 실제로 소비하는 기계적 에너지.
        #   → 정격 전력 대비 과도하게 높으면 과부하(Power Failure, PWF) 위험
        # ──────────────────────────────────────────────────────────────
        .withColumn("power",
                    F.col("torque_nm") * F.col("rotational_speed_rpm") * F.lit(2 * math.pi / 60))

        # ──────────────────────────────────────────────────────────────
        # 피처 3: 공구 마모율 (tool_wear_rate)
        # 계산: 공구 마모 시간(min) / 회전속도(rpm)
        # 물리적 의미: 회전 1회당 공구가 얼마나 빨리 닳고 있는지의 비율.
        #   → 같은 마모 시간이라도 고속 회전이면 마모율이 낮음 (정상)
        #   → 저속 회전인데 마모가 크면 마모율이 높음 (비정상 - 공구 불량 의심)
        # 주의: 회전속도가 0이면 0으로 처리 (0으로 나누기 방지)
        # ──────────────────────────────────────────────────────────────
        .withColumn("tool_wear_rate",
                    F.when(F.col("rotational_speed_rpm") > 0,
                           F.col("tool_wear_min") / F.col("rotational_speed_rpm"))
                    .otherwise(0))

        # ──────────────────────────────────────────────────────────────
        # 피처 4: 기계적 스트레인 (strain)
        # 계산: 토크(Nm) × 공구 마모(min)
        # 물리적 의미: 두 위험 요소의 교호작용(Interaction Effect).
        #   → 토크가 높아도 공구가 새것이면 견딜 수 있음
        #   → 공구가 닳았어도 토크가 낮으면 괜찮음
        #   → 하지만 둘 다 높으면? → 고장 확률이 "곱셈"으로 급증!
        # 이것이 교호작용 피처의 핵심: 개별 변수로는 보이지 않는 위험을 포착
        # ──────────────────────────────────────────────────────────────
        .withColumn("strain",
                    F.col("torque_nm") * F.col("tool_wear_min"))

        # ──────────────────────────────────────────────────────────────
        # 피처 5: 과열 플래그 (overheat_flag)
        # 계산: 온도차 > 8.6K이면 1, 아니면 0
        # 임계값 8.6K의 근거: EDA(탐색적 분석)에서 도출.
        #   → 데이터의 상위 분위수(약 75~90% 지점)에서 방열 고장이 집중 발생
        #   → 8.6K을 넘으면 "과열 상태"로 판단하는 것이 최적
        # 이런 이진(0/1) 피처를 "플래그 변수"라고 하며,
        #   모델이 명확한 경계를 학습하는 데 도움이 됩니다.
        # ──────────────────────────────────────────────────────────────
        .withColumn("overheat_flag",
                    F.when(F.col("process_temperature_k") - F.col("air_temperature_k") > 8.6, 1)
                    .otherwise(0))

        # ──────────────────────────────────────────────────────────────
        # 피처 6: 제품 품질 등급 인코딩 (product_quality)
        # 변환: L(Low)→0, M(Medium)→1, H(High)→2
        # 이유: ML 모델은 숫자만 입력받을 수 있습니다.
        #   → "L", "M", "H" 같은 문자(카테고리)를 숫자로 변환하는 과정을
        #     "인코딩(Encoding)"이라고 합니다.
        # 순서가 있는 카테고리(Low < Medium < High)이므로
        #   순서형 인코딩(Ordinal Encoding)을 사용합니다.
        # ──────────────────────────────────────────────────────────────
        .withColumn("product_quality",
                    F.when(F.col("type") == "L", 0)
                    .when(F.col("type") == "M", 1)
                    .otherwise(2))

        # ──────────────────────────────────────────────────────────────
        # 피처 7: 종합 위험 점수 (risk_score)
        # 계산: 여러 위험 요소를 0~1 범위로 정규화하여 가중 합산
        #   - 공구 마모 기여도: (마모시간 / 최대값 240) × 가중치 0.3
        #   - 토크 기여도: (토크 / 최대값 80) × 가중치 0.3
        #   - 과열 기여도: 과열이면 0.4, 아니면 0.0
        # 물리적 의미: 설비 엔지니어가 직관적으로 "위험도"를 판단할 수 있는
        #   종합 점수. 1에 가까울수록 고장 위험이 높음.
        # 실무 활용: 대시보드에서 실시간 모니터링 시 이 점수로 경보 수준 결정
        # ──────────────────────────────────────────────────────────────
        .withColumn("risk_score",
                    (F.col("tool_wear_min") / F.lit(240.0)) * 0.3 +
                    (F.col("torque_nm") / F.lit(80.0)) * 0.3 +
                    F.when(F.col("process_temperature_k") - F.col("air_temperature_k") > 8.6, 0.4)
                    .otherwise(0.0))
    )

    return df_features

# COMMAND ----------

# DBTITLE 1,피처 생성 및 확인
df_features = engineer_pm_features(df_bronze)
display(df_features.select(
    "udi", "type", "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "temp_diff", "power", "tool_wear_rate", "strain",
    "overheat_flag", "product_quality", "risk_score",
    "machine_failure"
))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 학습/테스트 데이터 분할 및 Delta Lake 저장
# MAGIC
# MAGIC ### 왜 데이터를 나누어야 하나? (Train/Test Split)
# MAGIC
# MAGIC ML 모델의 목적은 **아직 보지 못한 새로운 데이터** 에 대해 정확하게 예측하는 것입니다. 만약 전체 데이터로 학습하고, 같은 데이터로 성능을 평가하면 어떻게 될까요?
# MAGIC
# MAGIC 이는 마치 **시험 문제를 미리 알려주고 시험을 보는 것**과 같습니다. 당연히 점수가 높겠지만, 실제 능력을 반영하지 못합니다. 이를 ML에서는 **과적합(Overfitting)** 이라고 합니다.
# MAGIC
# MAGIC > **실제 프로젝트에서 겪은 일:**한 프로젝트에서 Train/Test 분할 없이 전체 데이터로 학습하고 "정확도 99%"라고 보고한 팀이 있었습니다. 실제 라인에 배포했더니 정확도가 60%대로 떨어졌습니다. 경영진 앞에서 매우 곤란한 상황이 되었고, 그 이후 그 팀은 **반드시 독립된 테스트 데이터로 평가하는 것** 을 철칙으로 삼게 되었습니다.
# MAGIC
# MAGIC 따라서 데이터를 두 그룹으로 나눕니다:
# MAGIC
# MAGIC | 구분 | 비율 | 역할 | 비유 |
# MAGIC |------|------|------|------|
# MAGIC | **학습 데이터 (Train)** | 80% (약 8,000건) | 모델이 패턴을 학습하는 데 사용 | 교과서로 공부하는 것 |
# MAGIC | **테스트 데이터 (Test)** | 20% (약 2,000건) | 학습 후 모델의 실제 성능을 평가 | 처음 보는 시험 문제를 푸는 것 |
# MAGIC
# MAGIC ### 왜 80:20인가?
# MAGIC - **학습 데이터가 너무 적으면**: 모델이 충분한 패턴을 학습하지 못합니다 (과소적합, Underfitting)
# MAGIC - **테스트 데이터가 너무 적으면**: 성능 평가의 신뢰도가 떨어집니다
# MAGIC - **80:20** 은 업계에서 가장 널리 사용되는 비율이며, 10,000건 규모의 데이터에서는 충분한 균형을 제공합니다
# MAGIC
# MAGIC > **현업에서는 이렇게 합니다:**시계열 센서 데이터에서는 무작위 분할 대신 **시간 기반 분할(Time-based Split)**을 강력히 권장합니다. 예를 들어, 1~8월 데이터로 학습하고 9~10월 데이터로 평가합니다. 무작위 분할은 미래 데이터가 학습에 섞일 수 있어 **데이터 누수(Data Leakage)** 위험이 있습니다. 이 실습에서는 교육 목적으로 무작위 분할을 사용하지만, 실무에서는 반드시 시간 기반으로 전환하세요.
# MAGIC
# MAGIC ### 재현성(Reproducibility)을 위한 `seed=42`
# MAGIC 데이터를 무작위로 섞어 나누지만, **`seed=42`를 고정**하면 매번 실행해도 **동일한 분할 결과** 가 나옵니다. 이는 ML 실험에서 매우 중요한데, 동료가 같은 코드를 실행했을 때 동일한 결과를 재현할 수 있어야 하기 때문입니다. (42라는 숫자 자체에 특별한 의미는 없으며, 관례적으로 많이 사용되는 값입니다.)
# MAGIC
# MAGIC > **재현성이 중요한 이유:**"지난달 모델은 잘 됐는데 이번 달은 왜 안 되죠?" 이 질문에 답하려면, 지난달 학습에 사용된 **정확히 같은 데이터, 같은 피처, 같은 분할** 을 재현할 수 있어야 합니다. seed 고정은 그 첫 걸음이고, Delta Lake의 Time Travel과 MLflow의 실험 추적이 나머지를 담당합니다.
# MAGIC
# MAGIC ### Delta Lake로 저장하는 이유
# MAGIC
# MAGIC 준비된 피처를 **Delta Lake 테이블** 로 저장합니다. 학습에 사용된 정확한 데이터를 나중에 재현할 수 있어야 합니다. "3개월 전 모델이 왜 잘 됐는지" 추적하려면 그때 데이터가 필요하고, Delta Lake 없이는 이것이 불가능합니다. CSV나 Parquet 파일로 저장하면 "누가 언제 이 파일을 덮어썼는지" 추적할 방법이 없습니다.
# MAGIC
# MAGIC | 기능 | 설명 | ML 프로젝트에서의 이점 |
# MAGIC |------|------|---------------------|
# MAGIC | **ACID 트랜잭션**| 저장 도중 오류가 나도 데이터가 깨지지 않음 | 대용량 피처 테이블을 안전하게 업데이트. **야간 배치에서 피처 업데이트 중 에러가 나도 이전 버전이 유지됨** |
# MAGIC | **Time Travel** | 과거 버전의 데이터를 조회/복원 가능 | "지난주 모델 학습 때 사용한 데이터"를 `VERSION AS OF` 구문 하나로 정확히 재현 가능 |
# MAGIC | **스키마 적용**| 컬럼 타입이 변경되면 자동으로 감지/방지 | 피처 타입이 실수로 바뀌는 것을 방지. **실무에서 피처 파이프라인이 깨지는 원인의 40%가 스키마 변경** |
# MAGIC | **Unity Catalog 연동**| 테이블-모델 간 계보(Lineage) 자동 추적 | "이 모델은 어떤 데이터로 학습되었는가?"를 자동으로 기록. **감사(Audit)나 규제 대응에 필수** |

# COMMAND ----------

# DBTITLE 1,학습용 피처 컬럼 선택
# ──────────────────────────────────────────────────────────────
# ML 모델에 입력할 피처(독립변수)를 명시적으로 정의합니다.
# 원본 센서 5개 + 파생 피처 7개 = 총 12개 피처
# ──────────────────────────────────────────────────────────────
feature_columns = [
    # --- 원본 센서 피처 (5개) ---
    "air_temperature_k",        # 공기 온도 (K)
    "process_temperature_k",    # 공정 온도 (K)
    "rotational_speed_rpm",     # 회전속도 (rpm)
    "torque_nm",                # 토크 (Nm)
    "tool_wear_min",            # 공구 마모 시간 (min)
    # --- 파생 피처 (7개) ---
    "temp_diff",                # 온도차 = 공정온도 - 공기온도
    "power",                    # 기계적 전력 (W)
    "tool_wear_rate",           # 공구 마모율 = 마모/회전속도
    "strain",                   # 기계적 스트레인 = 토크 x 마모
    "overheat_flag",            # 과열 플래그 (0 또는 1)
    "product_quality",          # 품질 등급 수치화 (0/1/2)
    "risk_score"                # 종합 위험 점수 (0~1)
]

# 타겟(종속변수): 모델이 예측해야 할 값. 0=정상, 1=고장
label_column = "machine_failure"

# 고장 유형 컬럼 (멀티라벨) - 추후 고장 원인 분석에 활용 가능
# 하나의 고장 사례가 여러 유형에 해당할 수 있어 "멀티라벨"이라고 합니다
failure_type_columns = ["twf", "hdf", "pwf", "osf", "rnf"]

# 학습에 필요한 컬럼만 선택하여 불필요한 데이터를 제거합니다
# "udi"는 각 행의 고유 식별자(Primary Key)로, 학습에는 사용하지 않지만
# 데이터 추적을 위해 유지합니다
df_training = df_features.select(
    "udi",  # Primary Key - 데이터 추적용
    *feature_columns,
    *failure_type_columns,
    label_column
)

# COMMAND ----------

# DBTITLE 1,Train/Test 분할
df_training = (
    df_training
    # 1단계: 각 행에 0~1 사이의 난수(random number)를 부여합니다.
    #   seed=42를 지정하면 매번 동일한 난수가 생성되어 결과를 재현할 수 있습니다.
    .withColumn("random", F.rand(seed=42))
    # 2단계: 난수가 0.8 미만이면 "train"(학습용, 약 80%),
    #   0.8 이상이면 "test"(테스트용, 약 20%)로 분류합니다.
    .withColumn("split",
                F.when(F.col("random") < 0.8, "train")
                .otherwise("test"))
    # 3단계: 분할에 사용한 임시 난수 컬럼을 제거합니다.
    .drop("random")
)

# 분할 결과를 확인합니다. train이 약 8,000건, test가 약 2,000건이면 정상입니다.
display(df_training.groupBy("split").count())

# COMMAND ----------

# DBTITLE 1,Delta Lake 테이블로 저장
training_table = "lgit_pm_training"

# Delta Lake 테이블로 저장합니다.
#   mode("overwrite"): 기존 테이블이 있으면 덮어씁니다 (재실행 시 안전)
#   overwriteSchema: 컬럼 구조가 변경되어도 허용합니다
#   saveAsTable: Unity Catalog에 등록되는 관리형(Managed) 테이블로 저장
#     → 이후 다른 노트북이나 사용자도 이 테이블을 조회할 수 있습니다
(df_training.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(training_table))

# Unity Catalog의 테이블 메타데이터에 설명을 추가합니다.
# 이렇게 하면 Catalog Explorer에서 이 테이블의 용도를 바로 확인할 수 있어,
# 팀원이 "이 테이블이 뭐지?"라고 고민하지 않아도 됩니다.
spark.sql(f"""
    COMMENT ON TABLE {catalog}.{db}.{training_table}
    IS '예지보전 학습 데이터: AI4I 2020 데이터셋 기반. 센서 피처 및 파생 피처 포함.
    원본: lgit_pm_bronze 테이블에서 피처 엔지니어링 수행.'
""")

print(f"학습 테이블 저장 완료: {catalog}.{db}.{training_table}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 저장된 Delta Lake 테이블을 조회하여 정상적으로 저장되었는지 확인합니다.
# MAGIC -- 12개 피처 컬럼 + 5개 고장 유형 컬럼 + machine_failure + udi + split
# MAGIC -- 총 20개 컬럼이 표시되어야 합니다.
# MAGIC SELECT * FROM lgit_pm_training LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. 피처 상관관계 분석
# MAGIC
# MAGIC ### 상관관계 분석이란?
# MAGIC
# MAGIC 피처 엔지니어링으로 7개의 새로운 피처를 만들었지만, 이 피처들이 실제로 **고장 예측에 도움이 되는지**검증해야 합니다. 이를 위해 **상관관계(Correlation)**를 분석합니다. 피처를 만들어 놓고 검증하지 않는 팀이 의외로 많은데, 이는 **쓸모없는 피처가 모델에 노이즈를 추가하여 오히려 성능을 떨어뜨리는** 결과를 초래합니다.
# MAGIC
# MAGIC **상관계수(r)** 는 -1에서 +1 사이의 값으로, 두 변수 간의 관계 강도를 나타냅니다:
# MAGIC
# MAGIC | 상관계수 범위 | 의미 | 제조 데이터에서의 해석 |
# MAGIC |-------------|------|------|
# MAGIC | **+0.5 ~ +1.0**| 강한 양의 상관관계 | **매우 강한 예측력.** 이런 피처가 2~3개만 있어도 모델 성능이 크게 향상됩니다 |
# MAGIC | **+0.3 ~ +0.5**| 중간 양의 상관관계 | **유의미한 피처.** 제조 센서 데이터에서 상관계수 0.3 이상이면 반드시 포함해야 합니다 |
# MAGIC | **-0.3 ~ +0.3**| 약한 상관관계 | 선형적으로는 약하지만, **비선형 패턴이 숨어 있을 수 있어** 바로 버리지 마세요 |
# MAGIC | **-1.0 ~ -0.3**| 음의 상관관계 | **역시 유의미합니다.** 부호가 음수라고 나쁜 것이 아니라, 반비례 관계를 의미합니다 |
# MAGIC
# MAGIC > **주의**: 상관계수는 **선형 관계** 만 측정합니다. XGBoost 같은 트리 기반 모델은 비선형 관계도 학습할 수 있으므로, 상관계수가 낮다고 해서 반드시 불필요한 피처는 아닙니다. 이 분석은 참고 지표로 활용합니다.
# MAGIC
# MAGIC > **현업에서는 이렇게 합니다:**상관관계 분석 외에도 **Feature Importance(피처 중요도)** 를 XGBoost의 `feature_importances_` 속성으로 확인합니다. 상관계수는 선형 관계만 보지만, Feature Importance는 트리 기반 모델이 실제로 어떤 피처를 많이 활용했는지를 보여줍니다. 두 결과를 교차 검증하면 피처의 실제 기여도를 더 정확히 판단할 수 있습니다. 다음 노트북(모델 학습)에서 이 부분을 확인하게 됩니다.
# MAGIC
# MAGIC ### 결과 해석 가이드
# MAGIC - 상관계수의 **절대값** 이 클수록 고장 예측에 유용한 피처입니다
# MAGIC - **양수(+)**: 해당 피처 값이 높을수록 고장 확률이 높아짐
# MAGIC - **음수(-)**: 해당 피처 값이 높을수록 고장 확률이 낮아짐 (반비례 관계)
# MAGIC - **피처 간 상관계수가 0.9 이상**인 쌍이 있다면 **다중공선성(Multicollinearity)** 문제를 의심하세요. 둘 중 하나를 제거하는 것이 모델 안정성에 도움이 됩니다

# COMMAND ----------

# DBTITLE 1,피처 상관관계 히트맵
import pandas as pd

# 상관관계 분석을 위해 학습 데이터만 Pandas DataFrame으로 변환합니다.
# 주의: toPandas()는 전체 데이터를 드라이버 노드의 메모리로 가져오므로,
# 대규모 데이터(수백만 건 이상)에서는 메모리 부족이 발생할 수 있습니다.
# 여기서는 8,000건(train) 정도이므로 문제가 없습니다.
pdf = df_training.filter("split = 'train'").select(*feature_columns, label_column).toPandas()

# 모든 피처 쌍 간의 상관계수(Pearson 상관계수)를 계산합니다.
# 결과는 피처 수 x 피처 수 크기의 대칭 행렬입니다.
corr_matrix = pdf.corr()

# 타겟 변수(machine_failure)와 각 피처 간의 상관계수만 추출하여 정렬합니다.
# 양수(+)가 클수록: 해당 피처가 높으면 고장 확률도 높음
# 음수(-)가 클수록: 해당 피처가 높으면 고장 확률이 낮음
# |r| > 0.3이면 "중간 이상의 상관관계"로, ML 모델에 유의미한 피처입니다.
target_corr = corr_matrix[label_column].drop(label_column).sort_values(ascending=False)
print("=== 피처-고장 상관관계 (절대값 기준) ===")
for feat, corr_val in target_corr.items():
    print(f"  {feat:30s}: {corr_val:+.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약: 이 노트북에서 배운 것
# MAGIC
# MAGIC ### 수행한 작업
# MAGIC
# MAGIC | 단계 | 수행 내용 | 핵심 개념 |
# MAGIC |------|----------|----------|
# MAGIC | **1. 데이터 탐색 (EDA)** | 10,000건의 센서 데이터를 확인하고, 고장 비율(3.4%)과 고장 유형 분포를 분석 | 데이터를 이해하지 못하면 좋은 모델을 만들 수 없다 |
# MAGIC | **2. 피처 엔지니어링** | 원본 5개 센서 피처로부터 7개의 파생 피처를 생성 (온도차, 전력, 마모율, 스트레인, 과열 플래그, 품질 인코딩, 위험 점수) | 도메인 지식을 수학적으로 모델링하여 예측 성능 향상 |
# MAGIC | **3. Train/Test 분할** | 학습용 80% / 테스트용 20%로 데이터를 분할 (seed=42로 재현성 보장) | 과적합 방지를 위해 학습과 평가 데이터를 분리 |
# MAGIC | **4. Delta Lake 저장** | 피처 테이블을 Delta Lake 형식으로 Unity Catalog에 저장 | ACID 트랜잭션, Time Travel, Lineage 자동 추적 |
# MAGIC | **5. 상관관계 분석** | 각 피처와 고장 여부 간의 상관계수를 계산하여 피처 유효성 검증 | 상관계수가 높은 피처가 모델 예측에 더 기여 |
# MAGIC
# MAGIC ### 핵심 학습 포인트
# MAGIC
# MAGIC 1. **피처 엔지니어링은 모델 성능의 핵심**: 아무리 좋은 알고리즘도 입력 데이터가 부실하면 좋은 결과를 낼 수 없습니다. "쓰레기가 들어가면 쓰레기가 나온다(Garbage In, Garbage Out)"는 ML의 기본 원칙입니다. 실제 프로젝트에서 모델 성능 개선의 80%는 알고리즘 변경이 아니라 피처 개선에서 나옵니다.
# MAGIC 2. **도메인 지식의 중요성**: 전력(P = T x omega), 스트레인(토크 x 마모) 같은 피처는 기계공학 지식 없이는 만들 수 없습니다. **제조 현장의 엔지니어와 데이터 사이언티스트의 협업** 이 필수적인 이유입니다. 성공하는 제조 AI 팀은 반드시 도메인 전문가가 팀에 포함되어 있습니다.
# MAGIC 3. **Databricks의 역할**: Delta Lake(안전한 저장), Unity Catalog(계보 추적), Spark(대규모 병렬 처리)를 통해 엔터프라이즈급 ML 파이프라인을 구축할 수 있습니다.
# MAGIC
# MAGIC ### 실무 전환 시 추가로 고려할 사항
# MAGIC
# MAGIC > **2025년 현재, Feature Store는 ML 플랫폼의 필수 구성 요소가 되었습니다.**5년 전만 해도 선택사항이었지만, 지금은 Feature Store 없이 MLOps를 한다는 것은 버전 관리 없이 소프트웨어를 개발하는 것과 같습니다. 이 실습에서 만든 피처 변환 로직(`engineer_pm_features` 함수)을 Databricks Feature Store에 등록하면, **학습과 서빙에서 동일한 피처 변환을 100% 보장**할 수 있습니다. 학습 시와 실시간 추론 시에 피처 계산이 달라서 성능이 떨어지는 **Training-Serving Skew** 는 가장 흔하면서도 찾기 어려운 버그입니다.
# MAGIC
# MAGIC > **앞으로의 로드맵:**
# MAGIC > - **PoC 단계 (지금):** 정적 피처 7개, 배치 학습, 기본 Train/Test 분할
# MAGIC > - **파일럿 단계 (3개월 후):** 시계열 피처 추가(이동 평균, 변화율), 시간 기반 데이터 분할, Feature Store 연동
# MAGIC > - **운영 단계 (6개월 후):** 실시간 스트리밍 피처, 자동 피처 모니터링(드리프트 감지), A/B 테스트 기반 피처 실험
# MAGIC
# MAGIC ### 다음 단계
# MAGIC
# MAGIC 다음 노트북에서는 이번에 생성한 피처 테이블(`lgit_pm_training`)을 사용하여 **XGBoost 모델을 학습** 합니다. XGBoost는 정형 데이터(테이블 형태)에서 가장 널리 사용되는 ML 알고리즘으로, 특히 제조 데이터의 고장 예측에 탁월한 성능을 보입니다. 피처 엔지니어링이 얼마나 모델 성능에 기여하는지, 원본 피처만 사용한 모델과 파생 피처를 포함한 모델의 성능 차이를 직접 확인하게 됩니다.
# MAGIC
# MAGIC **다음 단계:** [XGBoost 모델 학습]($./03_structured_model_training)
