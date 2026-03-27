# Databricks notebook source
# MAGIC %md
# MAGIC # MLOps Agent: AI 기반 학습/예측 오케스트레이션
# MAGIC
# MAGIC **Agent**가 Trigger에 따라 MLOps 환경의 Tool들을 호출하여 학습/예측을 자동 수행합니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC - **AI Agent (ChatAgent)**: 자연어 기반 MLOps 작업 수행
# MAGIC - **UC Functions as Tools**: Unity Catalog 함수를 Agent Tool로 활용
# MAGIC - **Model Serving**: Agent를 서빙 엔드포인트로 배포
# MAGIC - **Workflows 통합**: Trigger 기반 자동화
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Agent가 수행하는 작업
# MAGIC 1. 데이터 드리프트 감지 시 → 재학습 트리거
# MAGIC 2. 스케줄에 따라 → 배치 예측 실행
# MAGIC 3. 모델 성능 저하 시 → 알림 및 자동 롤백
# MAGIC 4. 새 데이터 유입 시 → 피처 파이프라인 실행

# COMMAND ----------

# MAGIC %pip install --quiet mlflow databricks-sdk --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. MLOps Tool 함수 정의
# MAGIC
# MAGIC Agent가 호출할 수 있는 **Tool 함수**들을 정의합니다.
# MAGIC 실제 환경에서는 이 함수들을 **Unity Catalog Function**으로 등록하여 사용합니다.

# COMMAND ----------

# DBTITLE 1,MLOps Tool 함수들
import json
from datetime import datetime
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()


def check_data_drift(table_name: str = "lgit_pm_inference_results") -> dict:
    """
    데이터 드리프트를 확인합니다.
    PSI > 0.2 이면 드리프트로 판단합니다.
    """
    import numpy as np

    feature_columns = ["air_temperature_k", "process_temperature_k",
                       "rotational_speed_rpm", "torque_nm", "tool_wear_min"]

    train_pdf = spark.table("lgit_pm_training").filter("split='train'").select(*feature_columns).toPandas()

    try:
        infer_pdf = spark.table(table_name).select(*feature_columns).toPandas()
    except Exception:
        return {"drift_detected": False, "message": "추론 테이블이 없습니다.", "psi_values": {}}

    psi_values = {}
    for col in feature_columns:
        breakpoints = np.linspace(
            min(train_pdf[col].min(), infer_pdf[col].min()),
            max(train_pdf[col].max(), infer_pdf[col].max()), 11
        )
        expected = np.maximum(np.histogram(train_pdf[col], bins=breakpoints)[0] / len(train_pdf), 0.001)
        actual = np.maximum(np.histogram(infer_pdf[col], bins=breakpoints)[0] / len(infer_pdf), 0.001)
        psi_values[col] = float(np.sum((actual - expected) * np.log(actual / expected)))

    drift_detected = any(v > 0.2 for v in psi_values.values())
    return {
        "drift_detected": drift_detected,
        "psi_values": psi_values,
        "timestamp": datetime.now().isoformat()
    }


def trigger_retraining(reason: str = "scheduled") -> dict:
    """
    모델 재학습을 트리거합니다.
    Databricks Job을 실행하여 학습 파이프라인을 수행합니다.
    """
    print(f"재학습 트리거 — 사유: {reason}")
    # 실제 환경에서는 w.jobs.run_now()를 호출
    return {
        "status": "triggered",
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
        "message": f"재학습이 트리거되었습니다. 사유: {reason}"
    }


def run_batch_prediction() -> dict:
    """
    배치 예측을 실행합니다.
    Champion 모델을 사용하여 최신 센서 데이터에 대한 예측을 수행합니다.
    """
    import mlflow
    import pyspark.sql.functions as F

    model_name = f"{catalog}.{db}.lgit_predictive_maintenance"
    feature_columns = [
        "air_temperature_k", "process_temperature_k",
        "rotational_speed_rpm", "torque_nm", "tool_wear_min",
        "temp_diff", "power", "tool_wear_rate", "strain",
        "overheat_flag", "product_quality", "risk_score"
    ]

    try:
        champion_udf = mlflow.pyfunc.spark_udf(spark, model_uri=f"models:/{model_name}@Champion")
        inference_df = spark.table("lgit_pm_training").select("udi", "type", *feature_columns)
        preds = inference_df.withColumn("failure_probability", champion_udf(*feature_columns))
        count = preds.count()

        return {
            "status": "success",
            "predictions_count": count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_model_status() -> dict:
    """
    현재 Champion 모델의 상태를 확인합니다.
    """
    from mlflow import MlflowClient
    client = MlflowClient()
    model_name = f"{catalog}.{db}.lgit_predictive_maintenance"

    try:
        champion = client.get_model_version_by_alias(model_name, "Champion")
        run = mlflow.get_run(champion.run_id)
        return {
            "model_name": model_name,
            "champion_version": champion.version,
            "val_f1_score": run.data.metrics.get("val_f1_score", "N/A"),
            "val_auc": run.data.metrics.get("val_auc", "N/A"),
            "status": "active"
        }
    except Exception as e:
        return {"status": "no_champion", "message": str(e)}

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. MLOps Agent 정의
# MAGIC
# MAGIC Agent는 **시스템 프롬프트**와 **Tool 목록**을 기반으로 작업을 자동 수행합니다.

# COMMAND ----------

# DBTITLE 1,MLOps Agent 클래스 정의
import mlflow
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import (
    ChatAgentMessage,
    ChatAgentResponse,
    ChatAgentChunk,
)

SYSTEM_PROMPT = """당신은 LG Innotek 제조 현장의 MLOps Agent입니다.
다음 도구를 사용하여 예지보전 모델의 운영을 자동화합니다:

1. check_data_drift: 데이터 드리프트 확인
2. trigger_retraining: 모델 재학습 트리거
3. run_batch_prediction: 배치 예측 실행
4. get_model_status: 현재 모델 상태 확인

주요 자동화 규칙:
- 데이터 드리프트가 감지되면 자동으로 재학습을 트리거합니다.
- 스케줄에 따라 배치 예측을 실행합니다.
- 모델 성능이 임계값 이하이면 알림을 생성합니다.
"""

TOOLS = {
    "check_data_drift": check_data_drift,
    "trigger_retraining": trigger_retraining,
    "run_batch_prediction": run_batch_prediction,
    "get_model_status": get_model_status,
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Agent 실행 시뮬레이션
# MAGIC
# MAGIC Agent가 다양한 시나리오에서 어떻게 동작하는지 시뮬레이션합니다.

# COMMAND ----------

# DBTITLE 1,시나리오 1: 정기 상태 점검
print("=== 시나리오 1: 정기 상태 점검 ===\n")

# 모델 상태 확인
status = get_model_status()
print(f"모델 상태: {json.dumps(status, indent=2, ensure_ascii=False)}")

# COMMAND ----------

# DBTITLE 1,시나리오 2: 드리프트 기반 재학습 판단
print("=== 시나리오 2: 드리프트 기반 자동 재학습 ===\n")

# 1. 드리프트 확인
drift_result = check_data_drift()
print(f"드리프트 결과: {json.dumps(drift_result, indent=2, ensure_ascii=False)}")

# 2. 드리프트 감지 시 재학습 트리거
if drift_result["drift_detected"]:
    print("\n⚠️ 드리프트 감지! 재학습을 트리거합니다.")
    retrain_result = trigger_retraining(reason="data_drift_detected")
    print(f"재학습 결과: {json.dumps(retrain_result, indent=2, ensure_ascii=False)}")
else:
    print("\n✅ 드리프트 없음. 현재 모델 유지.")

# COMMAND ----------

# DBTITLE 1,시나리오 3: 배치 예측 실행
print("=== 시나리오 3: 스케줄 기반 배치 예측 ===\n")

pred_result = run_batch_prediction()
print(f"배치 예측 결과: {json.dumps(pred_result, indent=2, ensure_ascii=False)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Agent를 ChatAgent로 패키징 (배포용)
# MAGIC
# MAGIC 실제 운영에서는 이 Agent를 **Model Serving 엔드포인트**로 배포하여,
# MAGIC API 호출이나 Workflow Trigger로 자동 실행할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,MLOps Agent 워크플로우 정의
def mlops_agent_workflow(trigger_type: str = "scheduled"):
    """
    MLOps Agent의 전체 워크플로우를 실행합니다.

    Args:
        trigger_type: 트리거 유형
            - "scheduled": 정기 스케줄 (배치 예측 + 상태 점검)
            - "drift_check": 드리프트 확인 및 필요 시 재학습
            - "full_cycle": 전체 주기 (드리프트 → 재학습 → 예측)
    """
    results = {"trigger_type": trigger_type, "timestamp": datetime.now().isoformat()}

    if trigger_type in ["scheduled", "full_cycle"]:
        # 배치 예측 실행
        results["batch_prediction"] = run_batch_prediction()

    if trigger_type in ["drift_check", "full_cycle"]:
        # 드리프트 확인
        drift = check_data_drift()
        results["drift_check"] = drift

        if drift["drift_detected"]:
            results["retraining"] = trigger_retraining(reason="auto_drift_detection")

    # 항상 모델 상태 확인
    results["model_status"] = get_model_status()

    return results

# 워크플로우 실행 예시
print("=== MLOps Agent 전체 워크플로우 ===\n")
workflow_result = mlops_agent_workflow("full_cycle")
print(json.dumps(workflow_result, indent=2, ensure_ascii=False, default=str))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC 이 노트북에서 수행한 작업:
# MAGIC 1. **MLOps Tool 함수** 정의 (드리프트 확인, 재학습, 배치 예측, 상태 확인)
# MAGIC 2. **Agent 시스템 프롬프트** 및 Tool 매핑 정의
# MAGIC 3. **시나리오별 시뮬레이션** (정기 점검, 드리프트 재학습, 배치 예측)
# MAGIC 4. Agent **워크플로우** 패키징 (배포 준비)
# MAGIC
# MAGIC **다음 단계:** [Job 스케줄링]($./10_job_scheduling)
