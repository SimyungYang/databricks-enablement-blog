# Databricks notebook source
# MAGIC %md
# MAGIC # 챌린저(Challenger) 모델 검증
# MAGIC
# MAGIC 새로운 모델을 운영에 배포하기 전, **체계적인 검증**을 수행합니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC - **모델 에일리어스 기반 배포**: Challenger → Champion 승급 자동화
# MAGIC - **mlflow.evaluate()**: 표준화된 모델 평가 (혼동행렬, ROC, PR)
# MAGIC - **태그 기반 검증 추적**: 각 테스트 결과를 모델 태그로 기록
# MAGIC - **Workflows 통합**: 검증 노트북을 Job으로 자동 실행 가능
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 검증 체크리스트
# MAGIC 1. 모델 문서화 확인
# MAGIC 2. 운영 데이터 추론 테스트
# MAGIC 3. Champion 대비 성능 비교
# MAGIC 4. 비즈니스 KPI 평가

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

import mlflow
from mlflow import MlflowClient

client = MlflowClient()
model_name = f"{catalog}.{db}.lgit_predictive_maintenance"
model_alias = "Challenger"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 모델 정보 가져오기

# COMMAND ----------

# DBTITLE 1,Challenger 모델 정보 조회
model_details = client.get_model_version_by_alias(model_name, model_alias)
model_version = int(model_details.version)
model_run_id = model_details.run_id

print(f"검증 대상: {model_name} v{model_version} (@{model_alias})")
print(f"Run ID: {model_run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. 검증 체크 (Validation Checks)
# MAGIC
# MAGIC ### Check 1: 모델 문서화 확인

# COMMAND ----------

# DBTITLE 1,문서화 검증
has_description = bool(model_details.description and len(model_details.description) > 20)
print(f"모델 설명 존재: {has_description}")
if has_description:
    print(f"  → {model_details.description[:100]}...")
else:
    print("  → 경고: 모델에 충분한 설명이 없습니다. 최소 20자 이상 작성해주세요.")

client.set_model_version_tag(
    name=model_name, version=str(model_version),
    key="validation_has_description", value=str(has_description)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Check 2: 운영 데이터 추론 테스트
# MAGIC
# MAGIC 모델이 운영 환경의 데이터 형식에서 정상적으로 예측을 수행하는지 확인합니다.

# COMMAND ----------

# DBTITLE 1,추론 테스트
import pandas as pd

# 테스트 데이터 로드
test_df = spark.table("lgit_pm_training").filter("split = 'test'")
feature_columns = [
    "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "temp_diff", "power", "tool_wear_rate", "strain",
    "overheat_flag", "product_quality", "risk_score"
]

try:
    # 모델을 Spark UDF로 로드하여 추론 수행
    model_udf = mlflow.pyfunc.spark_udf(
        spark,
        model_uri=f"models:/{model_name}@{model_alias}",
        result_type="double"
    )
    preds_df = test_df.withColumn("prediction", model_udf(*feature_columns))
    pred_count = preds_df.count()

    inference_passed = pred_count > 0
    print(f"추론 테스트 통과: {pred_count}건 정상 예측")
    display(preds_df.select(*feature_columns[:5], "machine_failure", "prediction").limit(10))
except Exception as e:
    inference_passed = False
    print(f"추론 테스트 실패: {e}")

client.set_model_version_tag(
    name=model_name, version=str(model_version),
    key="validation_inference_passed", value=str(inference_passed)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Check 3: Champion 대비 성능 비교
# MAGIC
# MAGIC Challenger 모델의 F1 Score가 기존 Champion 이상인지 확인합니다.

# COMMAND ----------

# DBTITLE 1,성능 비교 검증
challenger_f1 = mlflow.get_run(model_run_id).data.metrics.get('val_f1_score', 0)

try:
    champion_model = client.get_model_version_by_alias(model_name, "Champion")
    if champion_model.version != model_details.version:
        champion_f1 = mlflow.get_run(champion_model.run_id).data.metrics.get('val_f1_score', 0)
        print(f"Champion F1: {champion_f1:.4f} vs Challenger F1: {challenger_f1:.4f}")
        metric_passed = challenger_f1 >= champion_f1
    else:
        print("Challenger = Champion (동일 버전). 첫 번째 모델이므로 승인합니다.")
        metric_passed = True
except Exception:
    print("Champion 모델이 없습니다. 첫 번째 모델이므로 승인합니다.")
    metric_passed = True

print(f"성능 검증 통과: {metric_passed}")

client.set_model_version_tag(
    name=model_name, version=str(model_version),
    key="validation_metric_passed", value=str(metric_passed)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Check 4: 비즈니스 KPI 평가
# MAGIC
# MAGIC 제조 현장의 비즈니스 관점에서 모델의 가치를 평가합니다.
# MAGIC - **미탐지 고장 (False Negative)**: 설비 다운타임 비용 발생
# MAGIC - **오탐 (False Positive)**: 불필요한 정비 비용 발생
# MAGIC - **정탐 (True Positive)**: 예방 정비로 다운타임 방지

# COMMAND ----------

# DBTITLE 1,비즈니스 가치 평가
from sklearn.metrics import confusion_matrix
import numpy as np

# 비용 파라미터 (제조 현장 기준)
COST_DOWNTIME = 50000       # 미탐지 고장으로 인한 다운타임 비용 (원)
COST_PREVENTIVE = 5000      # 예방 정비 비용 (원)
COST_FALSE_ALARM = 3000     # 오탐으로 인한 불필요 정비 비용 (원)
SAVING_PREVENTED = 45000    # 예방 정비로 절감한 비용 (원)

# 예측 수행
preds_pd = preds_df.select("machine_failure", "prediction").toPandas()
preds_pd["pred_label"] = (preds_pd["prediction"] > 0.5).astype(int)

tn, fp, fn, tp = confusion_matrix(preds_pd["machine_failure"], preds_pd["pred_label"]).ravel()

# 비즈니스 가치 계산
business_value = (
    tp * SAVING_PREVENTED          # 예방 성공
    - fp * COST_FALSE_ALARM        # 오탐 비용
    - fn * COST_DOWNTIME           # 미탐지 비용
    - tp * COST_PREVENTIVE         # 정비 비용
)

print(f"=== 비즈니스 가치 분석 ===")
print(f"True Positive (예방 성공):  {tp}건 → 절감: {tp * SAVING_PREVENTED:,}원")
print(f"False Positive (오탐):      {fp}건 → 비용: {fp * COST_FALSE_ALARM:,}원")
print(f"False Negative (미탐지):    {fn}건 → 비용: {fn * COST_DOWNTIME:,}원")
print(f"True Negative (정상):       {tn}건")
print(f"────────────────────────────────────")
print(f"예상 순 비즈니스 가치: {business_value:,}원")

business_kpi_passed = business_value > 0
print(f"\n비즈니스 KPI 통과: {business_kpi_passed}")

client.set_model_version_tag(
    name=model_name, version=str(model_version),
    key="validation_business_value", value=f"{business_value}"
)
client.set_model_version_tag(
    name=model_name, version=str(model_version),
    key="validation_business_kpi_passed", value=str(business_kpi_passed)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 종합 검증 결과 및 Champion 승급

# COMMAND ----------

# DBTITLE 1,검증 결과 종합 및 승급 결정
all_passed = all([has_description, inference_passed, metric_passed, business_kpi_passed])

print(f"=== 검증 결과 종합 ===")
print(f"  문서화 확인:     {'PASS' if has_description else 'FAIL'}")
print(f"  추론 테스트:     {'PASS' if inference_passed else 'FAIL'}")
print(f"  성능 비교:       {'PASS' if metric_passed else 'FAIL'}")
print(f"  비즈니스 KPI:    {'PASS' if business_kpi_passed else 'FAIL'}")
print(f"────────────────────────────────────")
print(f"  최종 결과:       {'PASS — Champion 승급!' if all_passed else 'FAIL — 재검토 필요'}")

if all_passed:
    # Champion으로 승급
    client.set_registered_model_alias(
        name=model_name,
        alias="Champion",
        version=model_version
    )
    client.set_model_version_tag(
        name=model_name, version=str(model_version),
        key="validation_status", value="approved"
    )
    print(f"\n모델 v{model_version}이 Champion으로 승급되었습니다!")
else:
    client.set_model_version_tag(
        name=model_name, version=str(model_version),
        key="validation_status", value="rejected"
    )
    print(f"\n모델 v{model_version}은 검증에 실패했습니다. 재검토가 필요합니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC 이 노트북에서 수행한 작업:
# MAGIC 1. **모델 문서화** 확인
# MAGIC 2. **운영 데이터 추론** 테스트
# MAGIC 3. **Champion-Challenger 성능** 비교
# MAGIC 4. **비즈니스 KPI** 평가 (제조 현장 비용 분석)
# MAGIC 5. 모든 테스트 통과 시 **Champion 자동 승급**
# MAGIC
# MAGIC **다음 단계:** [배치 추론]($./06_batch_inference)
