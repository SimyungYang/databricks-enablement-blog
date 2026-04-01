# Databricks notebook source
# MAGIC %md
# MAGIC > **사전 요구사항** : 이 노트북 실행 전 `05_challenger_validation` 노트북을 먼저 실행해야 합니다.
# MAGIC > 05번 노트북에서 Challenger 모델이 검증을 통과하여 Champion 에일리어스가 설정되어야 이 노트북이 정상 작동합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC # 배치 추론 (Batch Inference)
# MAGIC
# MAGIC ## 이 노트북은 무엇을 하는가?
# MAGIC
# MAGIC 지금까지 모델을 학습하고(04), 검증하여 Champion으로 승급시켰습니다(05).
# MAGIC **이제 모델이 실제로 일을 시작할 차례입니다.**
# MAGIC
# MAGIC **배치 추론(Batch Inference)** 이란, 쌓여 있는 데이터를 한꺼번에 모델에 넣어서 예측 결과를 얻는 방식입니다.
# MAGIC "배치(Batch)"는 "묶음"이라는 뜻으로, 데이터를 하나씩 처리하는 것이 아니라 **대량의 데이터를 한 번에 처리** 합니다.
# MAGIC
# MAGIC > **제조 비유** : 제품 하나하나를 수작업으로 검사하는 것(실시간 추론)이 아니라,
# MAGIC > 컨베이어 벨트 위에 올라온 제품들을 **자동 검사 장비로 한꺼번에 검사** 하는 것(배치 추론)과 같습니다.
# MAGIC > LG이노텍 공장에서 6시간마다 쌓인 센서 데이터를 모아서, 모든 설비의 고장 확률을 한 번에 예측합니다.
# MAGIC
# MAGIC ### 실시간 추론 vs 배치 추론
# MAGIC
# MAGIC | 구분 | 실시간 추론 (Real-time) | 배치 추론 (Batch) |
# MAGIC |------|------------------------|-------------------|
# MAGIC | **처리 방식** | 요청 1건마다 즉시 응답 | 대량 데이터를 한꺼번에 처리 |
# MAGIC | **응답 시간** | 밀리초 단위 | 분~시간 단위 |
# MAGIC | **적합한 상황** | 웹 서비스, 챗봇 | 정기 보고, 대량 예측 |
# MAGIC | **예지보전 활용** | 센서 이상 즉시 알림 | 6시간마다 전체 설비 점검 |
# MAGIC
# MAGIC 예지보전에서는 **배치 추론이 더 적합** 합니다. 설비 고장은 수초 내에 급변하는 것이 아니라
# MAGIC 서서히 진행되므로, 6시간 간격으로 전체 설비를 점검하는 것이 효율적입니다.
# MAGIC
# MAGIC > **멘토 조언** : 배치 추론의 핵심은 "얼마나 빠르게 대량 예측을 하느냐"입니다.
# MAGIC > Spark UDF의 진짜 위력은 단일 모델을 클러스터 전체 노드에서 동시에 실행한다는 것입니다.
# MAGIC > 10만 대 설비를 예측하는 데 단일 서버로 10분 걸리던 것이 10노드 클러스터에서 1분으로 줄어듭니다.
# MAGIC > 제가 모 자동차 부품사에서 실제로 경험한 수치입니다. 6시간 간격 배치에서 추론 시간이 10분이면,
# MAGIC > "6시간마다 10분 블라인드"가 생기는 겁니다. 이것을 1분으로 줄이면 운영 안정성이 완전히 달라집니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC
# MAGIC | 기능 | 설명 | 장점 |
# MAGIC |------|------|------|
# MAGIC | **PySpark UDF** | 모델을 Spark 함수로 변환하여 클러스터 전체에 분산 추론 | 1만 건이든 100만 건이든 자동으로 병렬 처리 |
# MAGIC | **에일리어스 기반 배포** | `@Champion` 이름으로 모델 참조 | 05번에서 새 Champion이 되면 이 코드 변경 없이 자동 적용 |
# MAGIC | **Delta Lake** | 예측 결과를 ACID 트랜잭션으로 안전하게 저장 | 저장 중 장애가 발생해도 데이터 손상 없음 |
# MAGIC | **Workflows** | 일 4회 자동 실행 스케줄링 | 사람 개입 없이 24/7 운영 |
# MAGIC
# MAGIC > **Databricks 장점** : 전통적인 방법에서는 모델 서빙 서버(Flask, FastAPI 등)를 직접 구축하고,
# MAGIC > 배치 스케줄러(Airflow, Cron 등)를 별도로 설정해야 합니다. Databricks에서는 노트북 하나에
# MAGIC > 추론 로직을 작성하고, Workflows에서 스케줄만 설정하면 전체 배치 추론 파이프라인이 완성됩니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 운영 환경 스펙
# MAGIC - **실행 주기** : 일 4회 (6시간 간격 - 06:00, 12:00, 18:00, 24:00)
# MAGIC - **입력** : 설비 센서 데이터 테이블 (`lgit_pm_training`)
# MAGIC - **출력** : 고장 예측 확률 + 위험 등급(CRITICAL/HIGH/MEDIUM/LOW) + 타임스탬프
# MAGIC - **저장** : Delta Lake 테이블에 Append 모드로 이력 누적

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Champion 모델 로드
# MAGIC
# MAGIC ### PySpark UDF란?
# MAGIC
# MAGIC **UDF (User Defined Function)** 는 사용자가 직접 정의한 함수입니다.
# MAGIC **PySpark UDF** 는 이 함수를 Spark 클러스터의 모든 노드(컴퓨터)에서 동시에 실행할 수 있게 만든 것입니다.
# MAGIC
# MAGIC > **제조 비유** : 품질 검사원이 한 명이라면, 1,000개 제품을 검사하는 데 1,000분이 걸립니다.
# MAGIC > 하지만 검사원 100명이 동시에 검사하면 10분이면 끝납니다.
# MAGIC > PySpark UDF는 이 "검사원 100명"을 자동으로 배치해주는 기능입니다.
# MAGIC > Databricks 클러스터에 10개 노드가 있으면, 100만 건의 데이터를 10개 노드가 나누어 동시에 처리합니다.
# MAGIC
# MAGIC > **실무 주의사항** : Spark UDF로 모델을 분산 실행하면, 각 노드에 모델이 복제됩니다.
# MAGIC > 모델 크기가 큰 경우(예: 딥러닝 모델 2GB 이상) 메모리 문제가 발생할 수 있습니다.
# MAGIC > XGBoost 같은 트리 모델은 보통 수 MB~수십 MB 수준이라 전혀 문제없지만,
# MAGIC > 나중에 비전 모델을 Spark UDF로 돌리려면 메모리 계획을 세워야 합니다.
# MAGIC > 이런 경우에는 Model Serving endpoint를 사용하는 것이 더 적합합니다.
# MAGIC
# MAGIC 아래 코드에서 `mlflow.pyfunc.spark_udf()`는 Unity Catalog에 저장된 Champion 모델을
# MAGIC Spark에서 사용할 수 있는 함수(UDF)로 변환합니다.
# MAGIC `models:/{model_name}@Champion` 형식으로 참조하면, 항상 현재 Champion 에일리어스가
# MAGIC 가리키는 최신 모델을 자동으로 로드합니다.

# COMMAND ----------

# DBTITLE 1,Champion 모델 로드 (PySpark UDF)
import mlflow
from mlflow import MlflowClient

model_name = f"{catalog}.{db}.lgit_predictive_maintenance"
client = MlflowClient()

# Champion 모델 존재 확인
champion_info = client.get_model_version_by_alias(model_name, "Champion")
print(f"Champion 모델: v{champion_info.version}")

# [Spark UDF 분산 추론 설명]
# Spark UDF로 변환하면 클러스터의 모든 노드에서 분산 추론이 가능합니다.
# 예: 100만 건 데이터를 100개 노드로 나누어 각 노드가 1만 건씩 처리 → 처리 속도 100배 향상
# 단일 서버에서 순차 처리하는 방식 대비 Databricks의 핵심 장점입니다.

# PySpark UDF로 로드 → 클러스터 전체에서 분산 추론 가능
# result_type="double"을 지정하여 단일 스칼라 값으로 반환
champion_udf = mlflow.pyfunc.spark_udf(
    spark,
    model_uri=f"models:/{model_name}@Champion",
    result_type="double"
)

print("Champion 모델을 PySpark UDF로 로드 완료")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. 추론 데이터 준비
# MAGIC
# MAGIC ### 운영 환경과의 차이점
# MAGIC
# MAGIC **실제 운영 환경** 에서는 센서 데이터가 IoT 게이트웨이를 통해 실시간으로 Delta Lake에 유입됩니다.
# MAGIC 이 교육에서는 학습 데이터에서 **정답 레이블(machine_failure)** 을 제거한 데이터를 추론 입력으로 사용합니다.
# MAGIC
# MAGIC > **실제 운영 시나리오 (LG이노텍)** :
# MAGIC > 1. 설비 센서에서 6시간 동안 데이터가 수집됩니다 (온도, 회전속도, 토크, 마모도 등)
# MAGIC > 2. 이 데이터가 Delta Lake 테이블에 적재됩니다 (Databricks Auto Loader 또는 Structured Streaming 활용)
# MAGIC > 3. Workflows가 6시간마다 이 노트북을 자동 실행합니다
# MAGIC > 4. 새로 쌓인 데이터에 대해 배치 추론을 수행합니다
# MAGIC
# MAGIC 아래 코드에서 `current_timestamp()`로 추론 시각을 기록하는 이유는,
# MAGIC 나중에 "언제 예측한 결과인지"를 추적하기 위해서입니다. 하루 4회 실행되므로
# MAGIC 어느 회차(06시/12시/18시/24시)의 예측인지 구분이 필요합니다.

# COMMAND ----------

# DBTITLE 1,추론 입력 데이터 준비
import pyspark.sql.functions as F

feature_columns = [
    "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "temp_diff", "power", "tool_wear_rate", "strain",
    "overheat_flag", "product_quality", "risk_score"
]

# 추론용 데이터 로드 (레이블 제외)
# current_timestamp()로 추론 시각을 기록하는 이유:
# - 일 4회 실행 시 어느 회차(6시, 12시, 18시, 24시)의 예측인지 구분 가능
# - 모델 성능 모니터링 시 시점 기준으로 드리프트 분석 가능
# - 예: "최근 1주일 내 CRITICAL 예측이 증가했는가?" 같은 시계열 분석 지원
inference_df = (
    spark.table("lgit_pm_training")
    .select("udi", *feature_columns)
    .withColumn("inference_timestamp", F.current_timestamp())
)

print(f"추론 대상: {inference_df.count()} 건")
display(inference_df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 배치 추론 실행
# MAGIC
# MAGIC Champion 모델을 **PySpark UDF** 로 호출하여 전체 데이터에 대한 예측을 수행합니다.
# MAGIC Spark가 자동으로 클러스터의 모든 노드에 작업을 분산합니다.
# MAGIC
# MAGIC ### 추론 결과에 포함되는 정보
# MAGIC
# MAGIC | 컬럼 | 설명 | 예시 |
# MAGIC |------|------|------|
# MAGIC | `failure_probability` | 고장 확률 (0.0 ~ 1.0) | 0.82 = 82% 확률로 고장 예상 |
# MAGIC | `predicted_failure` | 이진 판정 (0 또는 1) | 확률 > 0.5이면 1(고장) |
# MAGIC | `risk_level` | 위험 등급 (4단계) | CRITICAL / HIGH / MEDIUM / LOW |
# MAGIC | `model_version` | 예측에 사용된 모델 버전 | 나중에 모델별 성능 비교 가능 |
# MAGIC
# MAGIC ### 위험 등급 분류 기준 및 현장 대응 방법
# MAGIC
# MAGIC | 등급 | 고장 확률 | 의미 | 현장 대응 |
# MAGIC |------|-----------|------|-----------|
# MAGIC | **CRITICAL**| > 80% | 고장이 임박한 상태 | **즉시 라인 정지하고 점검** . 해당 설비 비상 정비 투입 |
# MAGIC | **HIGH**| 50~80% | 고장 가능성이 높은 상태 | **현재 교대 근무 내 점검 필수** . 정비팀에 즉시 통보 |
# MAGIC | **MEDIUM**| 30~50% | 주의가 필요한 상태 | **다음 정기 점검 시 우선 확인** . 모니터링 강화 |
# MAGIC | **LOW**| < 30% | 정상 운영 상태 | **통상적인 모니터링 유지** . 추가 조치 불필요 |
# MAGIC
# MAGIC > **LG이노텍 활용 시나리오** : CRITICAL 등급이 감지되면 Lakeflow Jobs의
# MAGIC > 알림 기능으로 정비팀 Slack 채널이나 이메일로 즉시 알림을 보낼 수 있습니다.
# MAGIC > "설비 UDI-1234가 CRITICAL 상태입니다. 고장 확률 92%. 즉시 점검이 필요합니다."
# MAGIC
# MAGIC > **멘토 조언** : 위험 등급 임계값(0.3/0.5/0.8)은 교육용 예시입니다.
# MAGIC > 실무에서는 반드시 **현장 엔지니어와 함께** 결정해야 합니다.
# MAGIC > 제 경험상, 처음에는 보수적으로(CRITICAL 기준을 낮게, 예: 0.7) 시작하고,
# MAGIC > 오탐이 많으면 점진적으로 기준을 올리는 것이 안전합니다.
# MAGIC > 처음부터 임계값을 높게 잡으면, 초기에 고장을 놓치면서 현장의 신뢰를 잃게 됩니다.
# MAGIC > **현장의 신뢰를 한 번 잃으면 회복하는 데 6개월이 걸립니다.** 오탐은 "너무 조심한 것"이지만,
# MAGIC > 미탐은 "무능한 것"으로 인식되기 때문입니다.

# COMMAND ----------

# DBTITLE 1,배치 예측 수행
# 모델 예측 수행 (분산 처리)
preds_df = (
    inference_df
    .withColumn("failure_probability", champion_udf(*feature_columns))
    .withColumn("predicted_failure", F.when(F.col("failure_probability") > 0.5, 1).otherwise(0))
    # 위험 등급 분류
    # [임계값 조정 안내] 이 임계값은 비즈니스 요구에 따라 조정 가능합니다:
    # - 오탐(False Alarm)을 줄이려면: CRITICAL 기준을 0.8 → 0.9로 높임
    # - 놓침(미탐지)을 줄이려면: CRITICAL 기준을 0.8 → 0.7로 낮춤
    # - 현장 운영 경험을 바탕으로 최적값을 점진적으로 조정하세요.
    .withColumn("risk_level",
        F.when(F.col("failure_probability") > 0.8, "CRITICAL")
        .when(F.col("failure_probability") > 0.5, "HIGH")
        .when(F.col("failure_probability") > 0.3, "MEDIUM")
        .otherwise("LOW"))
    # 모델 버전 기록 (추적용)
    .withColumn("model_name", F.lit(model_name))
    .withColumn("model_version", F.lit(int(champion_info.version)))
)

display(preds_df.select(
    "udi", "failure_probability", "predicted_failure",
    "risk_level", "inference_timestamp"
))

# COMMAND ----------

# MAGIC %md
# MAGIC ### 고장 유형별 확률 추정 (Fault Type Probability)
# MAGIC
# MAGIC > **참고** : 현재 모델은 이진 분류(고장/정상)만 수행합니다. 고장 유형(TWF/HDF/PWF/OSF/RNF)별 확률은
# MAGIC > 학습 데이터의 고장 유형 분포를 기반으로 사후 추정합니다.
# MAGIC > 실제 운영에서는 멀티레이블 분류 모델로 별도 학습하는 것을 권장합니다.

# COMMAND ----------

# DBTITLE 1,고장 유형별 사후 확률 추정
# 학습 데이터의 고장 유형 비율 (AI4I 2020 기준)
fault_type_ratios = {
    "TWF": 0.10,   # Tool Wear Failure (공구 마모)
    "HDF": 0.35,   # Heat Dissipation Failure (열 방출 고장)
    "PWF": 0.25,   # Power Failure (전력 고장)
    "OSF": 0.20,   # Overstrain Failure (과부하 고장)
    "RNF": 0.10    # Random Failure (랜덤 고장)
}

# 고장 확률 × 유형별 비율 = 유형별 확률
predictions = preds_df
for fault_type, ratio in fault_type_ratios.items():
    predictions = predictions.withColumn(
        f"prob_{fault_type.lower()}",
        F.round(F.col("failure_probability") * F.lit(ratio), 4)
    )

display(predictions.select("udi", "failure_probability", "risk_level",
                           *[f"prob_{ft.lower()}" for ft in fault_type_ratios.keys()]).limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. 예측 결과 저장
# MAGIC
# MAGIC ### 왜 예측 결과를 저장해야 하는가?
# MAGIC
# MAGIC 예측 결과를 Delta Lake 테이블에 저장하면 다음과 같은 가치를 얻습니다:
# MAGIC
# MAGIC 1. **이력 추적 (Trending)** : "이 설비의 고장 확률이 지난 1주일 동안 어떻게 변했는가?" 분석 가능
# MAGIC 2. **모델 모니터링** : 예측 분포가 시간이 지남에 따라 변하는지 확인 (08번 노트북에서 활용)
# MAGIC 3. **정비 계획 수립** : 과거 예측 결과를 기반으로 설비별 정비 주기 최적화
# MAGIC 4. **감사 추적 (Audit Trail)** : "언제, 어떤 모델이, 어떤 예측을 했는지" 완전한 기록 유지
# MAGIC
# MAGIC > **Delta Lake의 Append 모드** : 기존 데이터를 지우지 않고 새로운 예측 결과를 계속 쌓아갑니다.
# MAGIC > 이것은 공장의 **생산 일지** 와 같습니다 - 매일 새로운 기록을 추가하되, 이전 기록은 절대 삭제하지 않습니다.
# MAGIC > Delta Lake의 ACID 트랜잭션 덕분에, 저장 중 장애가 발생해도 데이터가 손상되거나 중복되지 않습니다.
# MAGIC
# MAGIC > **멘토 조언** : append vs overwrite는 사소해 보이지만 운영에서 매우 중요한 결정입니다.
# MAGIC > append를 써야 예측 이력이 쌓이고, 시간이 지나면서 "모델이 점점 CRITICAL을 많이 예측하고 있다
# MAGIC > → 드리프트 의심" 같은 분석이 가능합니다. 제가 한 프로젝트에서 overwrite로 시작했다가,
# MAGIC > 3개월 뒤에 "지난달 대비 예측 패턴이 어떻게 변했는지"를 분석할 수 없어서 처음부터 다시 쌓은 적이 있습니다.
# MAGIC > **예측 이력은 한 번 잃으면 복구할 수 없습니다.** 디스크 비용은 싸지만, 3개월치 이력 데이터는 돈으로 살 수 없습니다.

# COMMAND ----------

# DBTITLE 1,Delta Lake 테이블에 예측 결과 저장
inference_table = "lgit_pm_inference_results"

# [저장 모드 설명]
# append 모드: 이전 결과를 지우지 않고 누적 저장 → 시계열 분석 가능
#   예: "지난 30일 동안 이 설비의 고장 확률이 어떻게 변했는가?" 분석 가능
# overwrite 모드: 매번 이전 결과가 삭제 → 가장 최근 결과만 유지 (이력 없음)
# 예지보전 시스템에서는 이력 추적이 필수이므로 append 모드를 사용합니다.

# Append 모드로 저장 (일 4회 누적)
(preds_df.write
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(inference_table))

print(f"예측 결과 저장 완료: {catalog}.{db}.{inference_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Databricks UI 확인 포인트
# MAGIC
# MAGIC 1. **Catalog > lgit_mlops_poc > Tables > lgit_pm_inference_results** 클릭
# MAGIC 2. **Sample Data** 탭: 예측 결과 (failure_probability, risk_level, 고장 유형 확률) 확인
# MAGIC 3. **Details** 탭: 행 수가 이전보다 증가했는지 확인 (append 모드이므로 누적)
# MAGIC 4. **History** 탭: 각 배치 실행의 타임스탬프 확인
# MAGIC 5. 우측 상단 **Create** > **Quick Dashboard**: 위험 등급 분포 시각화를 즉시 생성 가능
# MAGIC
# MAGIC > **드릴다운 팁**: SQL Editor에서 `SELECT risk_level, COUNT(*) FROM lgit_pm_inference_results GROUP BY risk_level` 을 실행하면 위험 등급 분포를 즉시 확인할 수 있습니다

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. 예측 결과 분석
# MAGIC
# MAGIC 저장된 예측 결과를 **SQL** 로 분석합니다. Databricks에서는 Python과 SQL을 하나의 노트북에서
# MAGIC 자유롭게 전환할 수 있습니다 (`%sql` 매직 커맨드 사용).
# MAGIC
# MAGIC 아래 3개의 SQL 쿼리로 다음을 확인합니다:
# MAGIC 1. **위험 등급별 분포** - 전체 설비 중 각 위험 등급에 해당하는 비율 확인
# MAGIC 2. **제품 품질등급별 고장 예측 분포** - 품질 등급과 고장 예측의 상관관계 분석
# MAGIC 3. **CRITICAL/HIGH 위험 설비 목록** - 즉시 점검이 필요한 설비 식별
# MAGIC
# MAGIC > **Databricks 장점** : Delta Lake에 저장된 예측 결과를 바로 SQL로 분석할 수 있습니다.
# MAGIC > 별도의 BI 도구(Tableau, Power BI 등)를 연결하지 않아도, 노트북 안에서 바로 시각화와 분석이 가능합니다.
# MAGIC > 또한, 이 SQL 쿼리들을 Databricks SQL Dashboard로 만들면, 비개발자(정비팀, 관리자)도 웹 브라우저에서 실시간으로 확인할 수 있습니다.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 위험 등급별 분포
# MAGIC SELECT
# MAGIC   risk_level,
# MAGIC   COUNT(*) as count,
# MAGIC   ROUND(AVG(failure_probability), 4) as avg_failure_prob,
# MAGIC   ROUND(MIN(failure_probability), 4) as min_prob,
# MAGIC   ROUND(MAX(failure_probability), 4) as max_prob
# MAGIC FROM lgit_pm_inference_results
# MAGIC GROUP BY risk_level
# MAGIC ORDER BY avg_failure_prob DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 제품 품질등급별 고장 예측 분포 (0=L, 1=M, 2=H)
# MAGIC SELECT
# MAGIC   product_quality,
# MAGIC   COUNT(*) as total,
# MAGIC   SUM(predicted_failure) as predicted_failures,
# MAGIC   ROUND(SUM(predicted_failure) / COUNT(*) * 100, 2) as predicted_failure_rate_pct
# MAGIC FROM lgit_pm_inference_results
# MAGIC GROUP BY product_quality
# MAGIC ORDER BY predicted_failure_rate_pct DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- CRITICAL/HIGH 위험 설비 목록 (즉시 점검 필요)
# MAGIC SELECT
# MAGIC   udi, product_quality, failure_probability, risk_level,
# MAGIC   air_temperature_k, rotational_speed_rpm, torque_nm, tool_wear_min,
# MAGIC   inference_timestamp
# MAGIC FROM lgit_pm_inference_results
# MAGIC WHERE risk_level IN ('CRITICAL', 'HIGH')
# MAGIC ORDER BY failure_probability DESC
# MAGIC LIMIT 20

# COMMAND ----------

# MAGIC %md
# MAGIC ### 위험 설비 목록 활용 방법
# MAGIC
# MAGIC 위 쿼리 결과는 **정비팀의 핵심 액션 아이템** 입니다. 이 목록을 기반으로 즉시 점검 일정을 수립합니다.
# MAGIC
# MAGIC #### 우선순위 기반 정비 일정 수립
# MAGIC
# MAGIC | 우선순위 | 조건 | 조치 | 타임라인 |
# MAGIC |----------|------|------|----------|
# MAGIC | **P0 (긴급)** | CRITICAL 등급 + tool_wear > 200분 | 즉시 라인 정지, 공구 교체 | 발견 즉시 |
# MAGIC | **P1 (높음)** | CRITICAL 등급 | 당일 내 점검 | 4시간 이내 |
# MAGIC | **P2 (보통)** | HIGH 등급 | 다음 교대 시 점검 | 8시간 이내 |
# MAGIC | **P3 (낮음)** | MEDIUM 등급 | 다음 정기 점검 시 확인 | 1주일 이내 |
# MAGIC
# MAGIC #### 센서값 해석 가이드
# MAGIC - **`tool_wear_min`** (공구 마모도): 높을수록 공구 수명이 다해감. 200분 이상이면 교체 고려
# MAGIC - **`torque_nm`** (토크): 비정상적으로 높으면 설비 부하 과다 또는 윤활 문제
# MAGIC - **`rotational_speed_rpm`** (회전속도): 급격한 변동은 베어링 이상 징후
# MAGIC - **`air_temperature_k`** (공기 온도): 설비 주변 환경 온도. 냉각 시스템 이상 시 급등
# MAGIC
# MAGIC #### 자동 알림 설정 방법
# MAGIC 이 목록을 정비팀에 자동으로 전달하는 방법:
# MAGIC 1. **Databricks SQL Alert** : CRITICAL 건수가 임계값을 초과하면 이메일/Slack 자동 알림
# MAGIC 2. **Workflows 알림** : 배치 추론 Job 완료 시 결과 요약을 이메일로 발송
# MAGIC 3. **SQL Dashboard** : 정비팀이 웹 브라우저에서 실시간으로 위험 설비 현황을 확인
# MAGIC
# MAGIC > **LG이노텍 적용 시** : 이 예측 결과를 기존의 MES(Manufacturing Execution System)나
# MAGIC > CMMS(Computerized Maintenance Management System)와 연동하면,
# MAGIC > 정비 작업 지시가 자동으로 생성되는 **완전 자동화된 예지보전 시스템** 을 구축할 수 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC ### 이 노트북에서 수행한 작업
# MAGIC
# MAGIC | 단계 | 수행 내용 | 사용된 Databricks 기능 |
# MAGIC |------|-----------|----------------------|
# MAGIC | **1** | Champion 모델을 PySpark UDF로 로드 | Unity Catalog 에일리어스, MLflow |
# MAGIC | **2** | 추론 데이터 준비 (센서 데이터 + 타임스탬프) | Delta Lake, PySpark |
# MAGIC | **3** | 전체 설비에 대한 배치 예측 수행 | PySpark UDF 분산 추론 |
# MAGIC | **4** | 예측 결과에 위험 등급 부여 | PySpark 조건문 |
# MAGIC | **5** | Delta Lake에 Append 모드로 이력 저장 | Delta Lake ACID 트랜잭션 |
# MAGIC | **6** | 위험 설비 목록 분석 및 정비 액션 아이템 도출 | SQL Analytics |
# MAGIC
# MAGIC ### 핵심 포인트
# MAGIC
# MAGIC - **분산 추론** : PySpark UDF를 사용하여 대량의 센서 데이터를 클러스터 전체에서 병렬 처리합니다.
# MAGIC   단일 서버 대비 처리 속도가 노드 수에 비례하여 향상됩니다.
# MAGIC - **에일리어스 기반 배포** : `@Champion` 참조 덕분에, 05번에서 새 모델이 Champion으로 승급되면
# MAGIC   이 노트북의 코드를 수정하지 않아도 자동으로 새 모델로 추론됩니다.
# MAGIC - **이력 누적** : Append 모드로 저장하여 시계열 분석과 모델 모니터링의 기반 데이터를 구축합니다.
# MAGIC - **위험 등급** : 단순한 확률값이 아닌, 현장에서 바로 조치할 수 있는 4단계 등급으로 변환합니다.
# MAGIC
# MAGIC > **실무 경험담** : 배치 추론 파이프라인에서 가장 자주 발생하는 운영 이슈 3가지를 알려드리겠습니다.
# MAGIC > (1) **입력 테이블이 비어있는 경우** — 업스트림 ETL이 실패하면 빈 테이블에 추론을 돌리게 됩니다.
# MAGIC > 반드시 입력 건수 체크 로직을 추가하세요.
# MAGIC > (2) **모델 버전 불일치** — Champion 에일리어스가 실수로 삭제되면 에러가 납니다. 에일리어스 존재 여부를 먼저 확인하는 방어 코드가 필요합니다.
# MAGIC > (3) **디스크 용량 초과** — append 모드로 수개월 쌓다 보면 테이블이 커집니다. 파티셔닝과 OPTIMIZE/VACUUM 전략을 미리 세워두세요.
# MAGIC
# MAGIC **운영 환경** : 이 노트북은 Databricks Workflow에서 **일 4회 (6시간 간격)** 자동 실행됩니다.
# MAGIC
# MAGIC **다음 단계:** [비정형 이상탐지]($./07_unstructured_anomaly_detection) - 이미지 데이터를 활용한 외관 검사 AI

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 6. Feature Store가 추론에서 빛나는 이유
# MAGIC
# MAGIC > **20년차 현업 팁** : Feature Store의 진짜 가치는 학습 시가 아니라 **추론 시** 나타납니다.
# MAGIC > 학습할 때는 "그냥 Delta Table에서 읽으면 되지 않나?"라고 생각하기 쉽습니다.
# MAGIC > 하지만 운영 6개월 후, 피처 계산 로직이 바뀌었는데 학습 때와 추론 때 **다른 버전의 피처** 가 사용되고 있다면?
# MAGIC > 모델 성능이 떨어지는데 원인을 찾을 수 없는 **Training-Serving Skew** 가 발생합니다.
# MAGIC
# MAGIC ### 시나리오: Feature Store 없이 vs 있을 때
# MAGIC
# MAGIC | 상황 | Feature Store 없이 | Feature Store 있을 때 |
# MAGIC |------|-------------------|---------------------|
# MAGIC | 학습 시 피처 | `temp_diff = process_temp - air_temp` | Feature Table에서 자동 조회 |
# MAGIC | 추론 시 피처 | 같은 수식을 다시 코딩 (복사-붙여넣기) | **동일한 Feature Table** 에서 자동 조회 |
# MAGIC | 수식 변경 시 | 학습 코드/추론 코드 **둘 다** 수정 필요 | Feature Table **한 곳만** 수정 |
# MAGIC | 6개월 후 | "학습 때 어떤 수식이었지?" → 추적 불가 | **Lineage로 자동 추적** |
# MAGIC | 결과 | Training-Serving Skew → 성능 저하 | **일관성 자동 보장** |

# COMMAND ----------

# MAGIC %md
# MAGIC ### Feature Lookup 기반 추론 (참고 패턴)
# MAGIC
# MAGIC > 아래는 Feature Store의 `score_batch` 기능을 사용하면, 추론 시 피처를 **자동으로 조인** 하는 패턴입니다.
# MAGIC > 현재 실습에서는 피처를 직접 계산하여 사용하지만, 운영 환경에서는 이 패턴을 권장합니다.
# MAGIC
# MAGIC ```python
# MAGIC from databricks.feature_engineering import FeatureEngineeringClient, FeatureLookup
# MAGIC
# MAGIC fe = FeatureEngineeringClient()
# MAGIC
# MAGIC # 추론할 때 어떤 피처를 어디서 가져올지 정의
# MAGIC lookups = [
# MAGIC     FeatureLookup(
# MAGIC         table_name="catalog.schema.lgit_pm_features",  # Feature Table
# MAGIC         feature_names=["temp_diff", "power_w", "strain", "risk_score"],  # 필요한 피처
# MAGIC         lookup_key="udi"  # 조인 키 (설비 ID)
# MAGIC     )
# MAGIC ]
# MAGIC
# MAGIC # score_batch: 모델 + Feature Lookup을 한번에 실행
# MAGIC predictions = fe.score_batch(
# MAGIC     model_uri="models:/lgit_predictive_maintenance@Champion",
# MAGIC     df=new_sensor_data,  # 새로 들어온 센서 데이터 (udi만 있으면 됨!)
# MAGIC     feature_lookups=lookups
# MAGIC )
# MAGIC # → 피처를 자동으로 Feature Table에서 조인 + 모델로 예측 수행
# MAGIC ```
# MAGIC
# MAGIC > **핵심** : `new_sensor_data`에는 `udi`(설비 ID)만 있으면 됩니다.
# MAGIC > `temp_diff`, `power_w` 등의 피처는 Feature Store가 **자동으로 조인** 합니다.
# MAGIC > 피처 계산 로직이 바뀌어도 **추론 코드를 수정할 필요 없음** — Feature Table만 업데이트하면 됩니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. 모델이 변경되어도 추론이 끊기지 않는 이유
# MAGIC
# MAGIC > **이것이 에일리어스 + Feature Store의 진짜 위력입니다.**
# MAGIC
# MAGIC ### 시나리오: Champion v5 → v6 교체 시 추론 코드 변화
# MAGIC
# MAGIC ```python
# MAGIC # 추론 코드 — 이 코드는 한 번도 수정하지 않습니다!
# MAGIC predict_udf = mlflow.pyfunc.spark_udf(
# MAGIC     spark,
# MAGIC     model_uri="models:/lgit_predictive_maintenance@Champion",  # ← 버전 번호 아님!
# MAGIC     result_type="double"
# MAGIC )
# MAGIC ```
# MAGIC
# MAGIC | 시점 | Champion 에일리어스 | 가리키는 모델 | 추론 코드 수정? |
# MAGIC |------|------------------|------------|:---:|
# MAGIC | 3월 | @Champion | v5 (F1=0.87) | 없음 |
# MAGIC | 드리프트 감지 | — | — | 없음 |
# MAGIC | 자동 재학습 | — | v6 학습 완료 | 없음 |
# MAGIC | 검증 통과 | @Champion → v6 | v6 (F1=0.91) | **없음!** |
# MAGIC | 4월 | @Champion | v6 (F1=0.91) | 없음 |
# MAGIC
# MAGIC > **v5에서 v6으로 바뀌는 순간, 추론 코드는 한 줄도 바꾸지 않았지만 자동으로 v6 모델을 사용합니다.**
# MAGIC > 이것이 DNS처럼 작동하는 에일리어스의 힘이고, MLOps Level 2 무중단 배포의 핵심입니다.
# MAGIC
# MAGIC ### 만약 v6에 문제가 생기면? (롤백)
# MAGIC
# MAGIC ```python
# MAGIC # 관리자가 한 줄 실행 — 즉시 v5로 롤백!
# MAGIC client.set_registered_model_alias("lgit_predictive_maintenance", "Champion", version=5)
# MAGIC # → 다음 추론부터 자동으로 v5 사용 (코드 수정 없음)
# MAGIC ```
# MAGIC
# MAGIC > **현업 팁** : 이 구조 덕분에 "새 모델 배포"가 무서운 일이 아니게 됩니다.
# MAGIC > 잘못되면 30초 안에 롤백할 수 있으니까요. 이 안전장치가 없으면 팀은 모델 업데이트를 두려워하게 되고,
# MAGIC > 결국 6개월 된 낡은 모델로 운영하게 됩니다.
