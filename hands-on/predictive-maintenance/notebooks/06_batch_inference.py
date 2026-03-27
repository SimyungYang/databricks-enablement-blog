# Databricks notebook source
# MAGIC %md
# MAGIC # 배치 추론 (Batch Inference)
# MAGIC
# MAGIC Unity Catalog에 등록된 **Champion 모델**을 사용하여 대규모 배치 예측을 수행합니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC - **PySpark UDF**: 모델을 Spark UDF로 변환하여 클러스터 전체에 분산 추론
# MAGIC - **에일리어스 기반 배포**: `@Champion` 참조로 코드 변경 없이 모델 교체
# MAGIC - **Delta Lake**: 예측 결과를 ACID 트랜잭션으로 안전하게 저장
# MAGIC - **Workflows 통합**: 일 4회 배치 예측 스케줄링
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 운영 환경 스펙
# MAGIC - **실행 주기**: 일 4회 (6시간 간격)
# MAGIC - **입력**: 설비 센서 데이터 테이블
# MAGIC - **출력**: 고장 예측 확률 + 위험 등급 + 타임스탬프

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

# COMMAND ----------

# DBTITLE 1,Champion 모델 로드 (PySpark UDF)
import mlflow
from mlflow import MlflowClient

model_name = f"{catalog}.{db}.lgit_predictive_maintenance"
client = MlflowClient()

# Champion 모델 존재 확인
champion_info = client.get_model_version_by_alias(model_name, "Champion")
print(f"Champion 모델: v{champion_info.version}")

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
# MAGIC 실제 운영에서는 센서 데이터가 스트리밍/배치로 지속 유입됩니다.
# MAGIC 여기서는 학습 데이터에서 레이블을 제거한 데이터를 추론 입력으로 사용합니다.

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
# MAGIC Champion 모델을 **PySpark UDF**로 호출하여 전체 데이터에 대한 예측을 수행합니다.
# MAGIC Spark가 자동으로 클러스터의 모든 노드에 작업을 분산합니다.

# COMMAND ----------

# DBTITLE 1,배치 예측 수행
# 모델 예측 수행 (분산 처리)
preds_df = (
    inference_df
    .withColumn("failure_probability", champion_udf(*feature_columns))
    .withColumn("predicted_failure", F.when(F.col("failure_probability") > 0.5, 1).otherwise(0))
    # 위험 등급 분류
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
# MAGIC ## 4. 예측 결과 저장

# COMMAND ----------

# DBTITLE 1,Delta Lake 테이블에 예측 결과 저장
inference_table = "lgit_pm_inference_results"

# Append 모드로 저장 (일 4회 누적)
(preds_df.write
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(inference_table))

print(f"예측 결과 저장 완료: {catalog}.{db}.{inference_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. 예측 결과 분석

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
# MAGIC ## 요약
# MAGIC
# MAGIC 이 노트북에서 수행한 작업:
# MAGIC 1. Champion 모델을 **PySpark UDF**로 로드 (분산 추론)
# MAGIC 2. 전체 센서 데이터에 대한 **배치 예측** 수행
# MAGIC 3. 예측 결과에 **위험 등급** 부여 (CRITICAL/HIGH/MEDIUM/LOW)
# MAGIC 4. Delta Lake 테이블에 **Append 모드**로 결과 저장 (이력 누적)
# MAGIC 5. 위험 설비 목록 생성 → 정비팀 액션 아이템
# MAGIC
# MAGIC **운영 환경**: 이 노트북은 Databricks Workflow에서 **일 4회** 자동 실행됩니다.
# MAGIC
# MAGIC **다음 단계:** [비정형 이상탐지]($./07_unstructured_anomaly_detection)
