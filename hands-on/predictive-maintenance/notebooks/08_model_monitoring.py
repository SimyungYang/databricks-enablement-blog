# Databricks notebook source
# MAGIC %md
# MAGIC # 모델 모니터링 (Model Monitoring)
# MAGIC
# MAGIC 운영 중인 모델의 성능을 지속적으로 모니터링하고, **데이터 드리프트** 및 **성능 저하**를 탐지합니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC - **Lakehouse Monitoring**: 데이터 품질 및 모델 성능 자동 모니터링
# MAGIC - **Delta Lake Time Travel**: 시점별 데이터 비교
# MAGIC - **SQL Analytics**: 모니터링 대시보드 구축
# MAGIC - **Alerts**: 임계값 초과 시 자동 알림

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 모니터링 대상 데이터 확인

# COMMAND ----------

# DBTITLE 1,추론 결과 테이블 확인
display(spark.table("lgit_pm_inference_results").limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. 데이터 드리프트 탐지
# MAGIC
# MAGIC **데이터 드리프트**: 운영 데이터의 분포가 학습 데이터와 달라지는 현상.
# MAGIC 센서 데이터의 통계적 특성이 시간에 따라 변화하는지 모니터링합니다.

# COMMAND ----------

# DBTITLE 1,학습 vs 추론 데이터 분포 비교
import pyspark.sql.functions as F

feature_columns = [
    "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min"
]

# 학습 데이터 통계
train_stats = (
    spark.table("lgit_pm_training")
    .filter("split = 'train'")
    .select([F.mean(c).alias(f"{c}_mean") for c in feature_columns] +
            [F.stddev(c).alias(f"{c}_std") for c in feature_columns])
)

# 추론 데이터 통계
inference_stats = (
    spark.table("lgit_pm_inference_results")
    .select([F.mean(c).alias(f"{c}_mean") for c in feature_columns] +
            [F.stddev(c).alias(f"{c}_std") for c in feature_columns])
)

print("=== 학습 데이터 통계 ===")
display(train_stats)
print("=== 추론 데이터 통계 ===")
display(inference_stats)

# COMMAND ----------

# DBTITLE 1,PSI (Population Stability Index) 계산
import numpy as np
import pandas as pd

def calculate_psi(expected, actual, bins=10):
    """Population Stability Index 계산"""
    breakpoints = np.linspace(min(expected.min(), actual.min()),
                             max(expected.max(), actual.max()), bins + 1)
    expected_counts = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_counts = np.histogram(actual, bins=breakpoints)[0] / len(actual)

    # 0 방지
    expected_counts = np.maximum(expected_counts, 0.001)
    actual_counts = np.maximum(actual_counts, 0.001)

    psi = np.sum((actual_counts - expected_counts) * np.log(actual_counts / expected_counts))
    return psi

# 학습/추론 데이터 로드
train_pdf = spark.table("lgit_pm_training").filter("split='train'").select(*feature_columns).toPandas()
infer_pdf = spark.table("lgit_pm_inference_results").select(*feature_columns).toPandas()

print("=== PSI (Population Stability Index) ===")
print("PSI < 0.1: 안정 | 0.1~0.2: 주의 | > 0.2: 드리프트 감지")
print("─" * 50)

drift_detected = False
for col in feature_columns:
    psi = calculate_psi(train_pdf[col].values, infer_pdf[col].values)
    status = "안정" if psi < 0.1 else ("주의" if psi < 0.2 else "드리프트!")
    if psi >= 0.2:
        drift_detected = True
    print(f"  {col:30s}: PSI = {psi:.4f} ({status})")

if drift_detected:
    print("\n⚠️ 데이터 드리프트가 감지되었습니다. 모델 재학습을 검토하세요.")
else:
    print("\n✅ 데이터 분포가 안정적입니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 모델 성능 모니터링
# MAGIC
# MAGIC 실제 고장 레이블이 확보된 경우, 모델의 운영 성능을 추적합니다.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 예측 결과 분포 추이
# MAGIC SELECT
# MAGIC   date_trunc('hour', inference_timestamp) as prediction_hour,
# MAGIC   COUNT(*) as total_predictions,
# MAGIC   SUM(predicted_failure) as predicted_failures,
# MAGIC   ROUND(AVG(failure_probability), 4) as avg_failure_prob,
# MAGIC   model_version
# MAGIC FROM lgit_pm_inference_results
# MAGIC GROUP BY date_trunc('hour', inference_timestamp), model_version
# MAGIC ORDER BY prediction_hour DESC
# MAGIC LIMIT 24

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Lakehouse Monitoring 설정
# MAGIC
# MAGIC **Databricks Lakehouse Monitoring**을 사용하면 코드 없이 모니터를 생성하고,
# MAGIC 자동으로 드리프트 탐지, 데이터 품질, 모델 성능을 추적할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,Lakehouse Monitor 생성 (프로그래밍 방식)
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
inference_table_full = f"{catalog}.{db}.lgit_pm_inference_results"

# 기존 모니터 삭제 (재생성)
try:
    w.quality_monitors.delete(table_name=inference_table_full)
    print(f"기존 모니터 삭제: {inference_table_full}")
except Exception as e:
    print(f"기존 모니터 없음: {e}")

# 모니터 생성
try:
    monitor = w.quality_monitors.create(
        table_name=inference_table_full,
        assets_dir=f"/Workspace/Users/{current_user}/lgit_monitoring",
        output_schema_name=f"{catalog}.{db}",
        inference_log={
            "model_id_col": "model_name",
            "prediction_col": "failure_probability",
            "timestamp_col": "inference_timestamp",
            "problem_type": "PROBLEM_TYPE_CLASSIFICATION",
        },
    )
    print(f"Lakehouse Monitor 생성 완료: {inference_table_full}")
    print(f"대시보드 경로: /Workspace/Users/{current_user}/lgit_monitoring")
except Exception as e:
    print(f"Monitor 생성 참고: {e}")
    print("참고: Lakehouse Monitoring은 워크스페이스에서 수동으로도 설정 가능합니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC 이 노트북에서 수행한 작업:
# MAGIC 1. 추론 결과 데이터의 **통계적 분포** 비교
# MAGIC 2. **PSI (Population Stability Index)** 기반 드리프트 탐지
# MAGIC 3. 시계열 기반 **예측 분포 추이** 모니터링
# MAGIC 4. **Lakehouse Monitoring** 설정 (자동 드리프트/품질 탐지)
# MAGIC
# MAGIC **다음 단계:** [MLOps Agent]($./09_mlops_agent)
