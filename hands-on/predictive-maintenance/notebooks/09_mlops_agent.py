# Databricks notebook source
# MAGIC %md
# MAGIC # MLOps Agent: AI 기반 학습/예측 오케스트레이션
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## AI Agent(에이전트)란 무엇인가?
# MAGIC
# MAGIC **AI Agent**란 주어진 목표를 달성하기 위해 **스스로 상황을 관찰(Observe)하고, 판단(Decide)하고, 행동(Act)하는 자율형 AI 시스템** 입니다.
# MAGIC
# MAGIC ### 제조 현장 비유: Agent = 자동화된 공장 관리자(Supervisor)
# MAGIC
# MAGIC | 공장 관리자의 역할 | AI Agent의 역할 | 구체적 예시 |
# MAGIC |-------------------|----------------|-----------|
# MAGIC | **상황 파악** (현장 순회) | 관찰 (Observation) | 센서 데이터 드리프트 확인, 모델 성능 지표 조회 |
# MAGIC | **판단** (이상 여부 결정) | 의사결정 (Decision) | "드리프트가 임계치를 초과했으므로 재학습이 필요하다" |
# MAGIC | **조치** (정비 지시, 라인 변경) | 행동 (Action) | 재학습 Job 실행, 배치 예측 수행, 알림 발송 |
# MAGIC | **보고** (일일 보고서 작성) | 결과 기록 (Logging) | 수행 결과를 JSON으로 반환, MLflow에 기록 |
# MAGIC
# MAGIC 숙련된 공장 관리자는 설비 소리만 듣고도 이상을 감지하고, 적절한 조치를 즉시 취합니다. AI Agent도 마찬가지입니다. 데이터를 보고, 이상 여부를 판단하고, 필요한 조치를 자동으로 수행합니다.
# MAGIC
# MAGIC ### 자동화의 발전 역사
# MAGIC
# MAGIC ```
# MAGIC [1단계] 규칙 기반 자동화       → "온도 > 100도이면 알림 발송" (단순 If-Else 조건)
# MAGIC [2단계] 스크립트 파이프라인     → "매일 06:00에 학습 → 평가 → 배포 순서로 실행" (고정된 순서)
# MAGIC [3단계] 조건부 파이프라인       → "드리프트가 감지되면 재학습, 아니면 건너뜀" (분기 로직)
# MAGIC [4단계] AI Agent (지금 단계)   → "상황을 종합적으로 판단하여 최적의 행동을 스스로 선택" (자율 판단) ← 우리가 구현하는 것
# MAGIC ```
# MAGIC
# MAGIC > **핵심 차이점**: 기존 자동화는 "미리 정해진 규칙"대로만 동작합니다. AI Agent는 **자연어로 된 지침(System Prompt)**을 이해하고, 상황에 맞게 **어떤 Tool을 어떤 순서로 호출할지 스스로 결정** 합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Databricks에서 Agent를 만드는 이점
# MAGIC
# MAGIC Databricks는 **Mosaic AI Agent Framework** 를 통해 엔터프라이즈급 AI Agent를 쉽게 구축할 수 있습니다:
# MAGIC
# MAGIC | 기능 | 설명 | 이점 |
# MAGIC |------|------|------|
# MAGIC | **ChatAgent 인터페이스** | MLflow의 표준 Agent 인터페이스 | 코드 몇 줄로 Agent를 정의하고 배포 가능 |
# MAGIC | **UC Functions as Tools** | Unity Catalog 함수를 Agent의 도구로 등록 | 기존 SQL/Python 함수를 그대로 Agent가 호출 가능 |
# MAGIC | **Model Serving 배포** | Agent를 REST API 엔드포인트로 배포 | 외부 시스템에서 HTTP 요청으로 Agent 호출 가능 |
# MAGIC | **Guardrails (안전 장치)** | Agent의 행동 범위를 제한 | 위험한 작업(예: 운영 모델 삭제)을 방지 |
# MAGIC | **Evaluation (평가)** | Agent 성능을 체계적으로 평가 | Agent가 올바른 판단을 내리는지 검증 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Agent가 이 PoC에서 수행하는 작업
# MAGIC
# MAGIC | # | 트리거 (Trigger) | Agent의 판단 | Agent의 행동 | 제조 비유 |
# MAGIC |---|-----------------|-------------|-------------|----------|
# MAGIC | 1 | 데이터 드리프트 감지 시 | "센서 데이터 분포가 변했다. 기존 모델이 부정확해질 수 있다" | 재학습 트리거 | 원재료 로트가 변경되어 공정 조건 재설정 필요 |
# MAGIC | 2 | 스케줄(일 4회) 도래 시 | "정해진 시간이 되었다. 최신 데이터로 예측해야 한다" | 배치 예측 실행 | 교대조(Shift) 시작 시 품질 예측 수행 |
# MAGIC | 3 | 모델 성능 저하 감지 시 | "예측 정확도가 임계치 이하로 떨어졌다" | 알림 및 자동 롤백 | SPC 관리 한계 초과 시 라인 정지 및 조치 |
# MAGIC | 4 | 새 데이터 유입 시 | "새로운 센서 데이터가 들어왔다. 피처를 업데이트해야 한다" | 피처 파이프라인 실행 | 새 원재료 입고 시 수입 검사 수행 |

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
# MAGIC ### Tool(도구)이란?
# MAGIC
# MAGIC AI Agent에서 **Tool**이란 Agent가 호출할 수 있는 **구체적인 기능(함수)** 을 말합니다.
# MAGIC
# MAGIC 제조 현장에 비유하면, 공장 관리자(Agent)가 사용할 수 있는 **장비와 시스템** 입니다:
# MAGIC - SPC 모니터링 시스템 → `check_data_drift` (데이터 이상 감지)
# MAGIC - MES 재작업 지시 시스템 → `trigger_retraining` (모델 재학습 명령)
# MAGIC - 자동 검사 장비 → `run_batch_prediction` (대량 예측 수행)
# MAGIC - 설비 상태 모니터 → `get_model_status` (현재 모델 상태 확인)
# MAGIC
# MAGIC Agent는 상황에 따라 이 Tool들을 **자율적으로 선택하여 호출** 합니다. 어떤 Tool을 어떤 순서로 호출할지는 Agent가 판단합니다.
# MAGIC
# MAGIC 실제 운영 환경에서는 이 함수들을 **Unity Catalog Function** 으로 등록하여 사용합니다. 그러면 Databricks의 권한 관리(Governance)가 적용되어, 누가 어떤 Tool을 호출했는지 추적(Audit)할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,MLOps Tool 함수들
import json
from datetime import datetime
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# ──────────────────────────────────────────────────────────────
# Tool 1: check_data_drift (데이터 드리프트 확인)
# ──────────────────────────────────────────────────────────────
# [역할] 학습 데이터와 최신 추론 데이터의 분포를 비교하여 "드리프트"를 탐지합니다.
#
# [드리프트(Drift)란?]
# 시간이 지남에 따라 데이터의 통계적 분포가 변하는 현상입니다.
# 제조 비유: 원재료 로트가 바뀌면 원재료의 특성(경도, 순도 등)이 달라지듯이,
# 센서 데이터도 계절, 설비 노후화 등으로 분포가 변합니다.
# 모델은 "옛날 데이터"로 학습했으므로, 데이터가 변하면 예측 정확도가 떨어집니다.
#
# [PSI(Population Stability Index) 지표]
# PSI > 0.1: 경미한 변화 (관찰 필요)
# PSI > 0.2: 유의미한 변화 (재학습 권장) ← 이 PoC의 임계치
# PSI > 0.25: 심각한 변화 (즉시 재학습 필요)
#
# [언제 트리거되나?] Agent가 정기 점검 시 또는 Workflow 스케줄에 따라 호출
# ──────────────────────────────────────────────────────────────
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


# ──────────────────────────────────────────────────────────────
# Tool 2: trigger_retraining (모델 재학습 트리거)
# ──────────────────────────────────────────────────────────────
# [역할] 모델 재학습 파이프라인을 실행합니다.
# 실제 환경에서는 Databricks Jobs API(w.jobs.run_now())를 호출하여
# 피처 엔지니어링 → 학습 → 등록 → 검증까지 전체 파이프라인을 수행합니다.
#
# [제조 비유] 공정 조건이 변경되었을 때, MES 시스템이 자동으로
# 새로운 조건에 맞는 레시피(Recipe)를 다시 계산하고 설비에 적용하는 것과 같습니다.
#
# [트리거 사유(reason)]
# - "scheduled": 정기 스케줄에 의한 재학습 (예: 매주 월요일)
# - "data_drift_detected": 드리프트 감지로 인한 긴급 재학습
# - "performance_degradation": 모델 성능 저하로 인한 재학습
# ──────────────────────────────────────────────────────────────
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


# ──────────────────────────────────────────────────────────────
# Tool 3: run_batch_prediction (배치 예측 실행)
# ──────────────────────────────────────────────────────────────
# [역할] Champion(현재 운영 중인 최고 성능) 모델을 사용하여
# 최신 센서 데이터 전체에 대해 한꺼번에 고장 예측을 수행합니다.
#
# [배치 예측 vs 실시간 예측]
# - 배치 예측: 대량의 데이터를 정해진 시간에 한꺼번에 처리 (이 PoC: 일 4회)
#   → 제조 비유: 교대조(Shift) 시작 시 전체 설비 상태를 한꺼번에 점검
# - 실시간 예측: 데이터가 들어올 때마다 즉시 처리 (API 호출)
#   → 제조 비유: 인라인(In-line) 검사 장비가 제품 하나하나를 즉시 판정
#
# [기술적 동작]
# 1. MLflow에서 Champion 별칭(Alias)이 부여된 모델을 로드
# 2. Spark UDF(User Defined Function)로 변환하여 분산 처리
# 3. 전체 데이터에 대해 병렬로 예측 수행 (수백만 건도 가능)
# ──────────────────────────────────────────────────────────────
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


# ──────────────────────────────────────────────────────────────
# Tool 4: get_model_status (현재 모델 상태 확인)
# ──────────────────────────────────────────────────────────────
# [역할] Unity Catalog에 등록된 Champion 모델의 현재 상태를 조회합니다.
# 모델 버전, 성능 지표(F1 Score, AUC) 등을 반환합니다.
#
# [제조 비유] 설비 관리 시스템에서 현재 가동 중인 설비의 상태(가동률,
# 최근 정비 이력, 잔여 수명 등)를 조회하는 것과 같습니다.
#
# [반환 지표 설명]
# - F1 Score: 정밀도(Precision)와 재현율(Recall)의 조화 평균.
#   0~1 사이 값이며 1에 가까울수록 좋습니다.
#   제조 비유: 불량 탐지율과 오탐율을 동시에 고려한 종합 성능 지표.
# - AUC(Area Under Curve): 모델의 분류 능력을 종합적으로 평가하는 지표.
#   0.5 = 동전 던지기 수준, 1.0 = 완벽한 분류.
# ──────────────────────────────────────────────────────────────
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
# MAGIC ### 시스템 프롬프트(System Prompt)란?
# MAGIC
# MAGIC **시스템 프롬프트**는 AI Agent에게 주어지는 **역할 정의서이자 업무 지침서** 입니다.
# MAGIC
# MAGIC 제조 현장에 비유하면, 새로 부임한 공장 관리자에게 전달하는 **"직무 기술서(Job Description) + 업무 매뉴얼"** 입니다:
# MAGIC - "당신은 LG Innotek 제조 현장의 MLOps Agent입니다" → **역할 정의** (직책)
# MAGIC - "다음 도구를 사용하여..." → **사용 가능한 장비/시스템 목록**
# MAGIC - "데이터 드리프트가 감지되면 자동으로 재학습을 트리거합니다" → **업무 규칙/SOP(표준작업절차)**
# MAGIC
# MAGIC 시스템 프롬프트를 잘 작성하면 Agent의 행동이 정확해지고, 잘못 작성하면 예기치 않은 행동을 할 수 있습니다. 마치 업무 매뉴얼이 명확해야 직원이 올바른 판단을 내리는 것과 같습니다.
# MAGIC
# MAGIC Agent는 이 시스템 프롬프트와 **Tool 목록** 을 기반으로, 주어진 상황에서 어떤 Tool을 어떤 순서로 호출할지 자동으로 판단하여 작업을 수행합니다.

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
# MAGIC 이제 Agent가 실제 운영 환경에서 마주칠 수 있는 **세 가지 대표적인 시나리오** 를 시뮬레이션합니다.
# MAGIC
# MAGIC 각 시나리오는 제조 현장에서 실제로 발생하는 상황을 모델링한 것입니다:
# MAGIC
# MAGIC | 시나리오 | 제조 현장 상황 | Agent의 대응 |
# MAGIC |---------|-------------|-------------|
# MAGIC | **시나리오 1: 정기 상태 점검** | 교대조 인수인계 시 설비 상태 확인 | 현재 Champion 모델의 버전, 성능 지표 등을 조회 |
# MAGIC | **시나리오 2: 드리프트 기반 재학습** | 계절 변화로 원재료 특성이 바뀜 → 기존 공정 조건이 맞지 않음 | 데이터 분포 변화를 감지하고, 변화가 크면 자동으로 재학습을 실행 |
# MAGIC | **시나리오 3: 배치 예측** | 근무조(Shift) 시작 시 전체 설비 상태를 한꺼번에 점검 | Champion 모델로 전체 센서 데이터에 대해 고장 확률을 예측 |

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
# MAGIC ### 왜 패키징이 필요한가?
# MAGIC
# MAGIC 위에서 시뮬레이션한 Agent 로직을 **실제 운영 환경**에서 사용하려면, 이 Agent를 하나의 **독립된 서비스** 로 배포해야 합니다.
# MAGIC
# MAGIC 제조 비유로 설명하면:
# MAGIC - **지금까지**: 수동으로 버튼을 눌러 Agent를 실행 (노트북에서 직접 실행)
# MAGIC - **패키징 후**: Agent가 24시간 자동으로 대기하며, 이벤트가 발생하면 스스로 작동 (API 서비스로 배포)
# MAGIC
# MAGIC 이것은 공장에서 **수동 검사 장비를 인라인(In-line) 자동 검사 장비로 교체** 하는 것과 같습니다.
# MAGIC
# MAGIC ### 배포 옵션
# MAGIC
# MAGIC | 배포 방식 | 설명 | 사용 시점 |
# MAGIC |----------|------|----------|
# MAGIC | **Model Serving 엔드포인트** | REST API로 Agent를 호출 | 외부 시스템(ERP, MES)에서 Agent를 호출할 때 |
# MAGIC | **Workflow Task** | Databricks Job의 태스크로 Agent를 실행 | 정기 스케줄에 따라 Agent를 실행할 때 |
# MAGIC | **Trigger 기반** | 특정 이벤트(테이블 업데이트, 알림 등) 발생 시 자동 실행 | 새 데이터 유입, 드리프트 감지 등 이벤트 기반 자동화 |

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
# MAGIC ### 이 노트북에서 배운 내용
# MAGIC
# MAGIC | # | 학습 항목 | 핵심 내용 | 제조 비유 |
# MAGIC |---|---------|---------|----------|
# MAGIC | 1 | **MLOps Tool 함수** 정의 | 드리프트 확인, 재학습, 배치 예측, 상태 확인 4가지 Tool | 공장 관리자가 사용하는 장비/시스템 |
# MAGIC | 2 | **Agent 시스템 프롬프트** | Agent의 역할과 행동 규칙을 자연어로 정의 | 직무 기술서 + SOP(표준작업절차서) |
# MAGIC | 3 | **시나리오별 시뮬레이션** | 정기 점검, 드리프트 재학습, 배치 예측 시나리오 | 교대조 인수인계, 원재료 변경 대응, 생산 시작 점검 |
# MAGIC | 4 | **Agent 워크플로우 패키징** | Agent를 API 서비스로 배포하기 위한 준비 | 수동 검사 → 인라인 자동 검사 전환 |
# MAGIC
# MAGIC ### 핵심 포인트
# MAGIC
# MAGIC > AI Agent는 단순한 자동화 스크립트가 아닙니다. **상황을 이해하고, 판단하고, 최적의 행동을 선택** 하는 자율형 시스템입니다.
# MAGIC > 이를 통해 ML 모델 운영에 필요한 반복적인 작업(모니터링, 재학습 판단, 예측 수행)을 사람의 개입 없이 자동화할 수 있습니다.
# MAGIC
# MAGIC ### 최신 트렌드: AI Agent의 미래
# MAGIC
# MAGIC - **Multi-Agent 시스템**: 여러 Agent가 협업하여 더 복잡한 작업을 수행 (예: 정형 데이터 Agent + 비정형 데이터 Agent + 보고서 Agent)
# MAGIC - **Human-in-the-Loop**: 중요한 결정(예: Champion 모델 교체)은 사람의 승인을 받고 실행
# MAGIC - **Autonomous MLOps**: 2025~2026년 트렌드로, Agent가 전체 ML 생명주기를 자율적으로 관리
# MAGIC
# MAGIC **다음 단계:**[Job 스케줄링]($./10_job_scheduling) -- Agent가 자동으로 실행되려면, 이를 호출하는 **스케줄(Workflow)** 이 필요합니다.
