# 09. MLOps Agent

> **전체 노트북 코드**: [09_mlops_agent.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/09_mlops_agent.py)


**목적**: AI Agent가 Trigger에 따라 MLOps Tool을 자동 호출하여 학습/예측/모니터링을 오케스트레이션합니다.

**사용 Databricks 기능**: `AI Agent (ChatAgent)`, `UC Functions as Tools`, `Model Serving`, `MLflow Tracing`

---

## Agent가 수행하는 작업

| 시나리오 | 트리거 | Agent 행동 |
|---------|--------|-----------|
| 정기 점검 | 스케줄 | 모델 상태 확인 |
| 드리프트 감지 | PSI > 0.2 | 자동 재학습 트리거 |
| 배치 예측 | 스케줄 | Champion 모델로 예측 실행 |
| 성능 저하 | F1 < 임계값 | 알림 및 자동 롤백 |

## 1. MLOps Tool 함수 정의

Agent가 호출할 수 있는 Tool 함수를 정의합니다. 실제 환경에서는 **UC Function** 으로 등록합니다.

```python
def check_data_drift(table_name: str = "lgit_pm_inference_results") -> dict:
    """PSI 기반 데이터 드리프트 확인"""
    psi_values = {}
    for col in feature_columns:
        breakpoints = np.linspace(
            min(train_pdf[col].min(), infer_pdf[col].min()),
            max(train_pdf[col].max(), infer_pdf[col].max()), 11)
        expected = np.maximum(np.histogram(train_pdf[col], bins=breakpoints)[0] / len(train_pdf), 0.001)
        actual = np.maximum(np.histogram(infer_pdf[col], bins=breakpoints)[0] / len(infer_pdf), 0.001)
        psi_values[col] = float(np.sum((actual - expected) * np.log(actual / expected)))
    drift_detected = any(v > 0.2 for v in psi_values.values())
    return {"drift_detected": drift_detected, "psi_values": psi_values}

def trigger_retraining(reason: str = "scheduled") -> dict:
    """모델 재학습 트리거 — 실제 환경에서는 w.jobs.run_now() 호출"""
    return {"status": "triggered", "reason": reason}

def run_batch_prediction() -> dict:
    """Champion 모델로 배치 예측 실행"""
    champion_udf = mlflow.pyfunc.spark_udf(spark, model_uri=f"models:/{model_name}@Champion")
    # ... 예측 수행 ...
    return {"status": "success", "predictions_count": count}
```

## 2. Agent 시스템 프롬프트 및 Tool 매핑

Agent의 자동화 규칙과 사용 가능한 Tool을 정의합니다.

```python
SYSTEM_PROMPT = """당신은 LG Innotek 제조 현장의 MLOps Agent입니다.
도구: check_data_drift, trigger_retraining, run_batch_prediction, get_model_status

자동화 규칙:
- 데이터 드리프트 감지 시 자동으로 재학습을 트리거합니다.
- 스케줄에 따라 배치 예측을 실행합니다.
- 모델 성능이 임계값 이하이면 알림을 생성합니다."""

TOOLS = {
    "check_data_drift": check_data_drift,
    "trigger_retraining": trigger_retraining,
    "run_batch_prediction": run_batch_prediction,
    "get_model_status": get_model_status,
}
```

## 3. Agent 전체 워크플로우

드리프트 확인 → 재학습 판단 → 배치 예측 → 상태 보고를 하나의 흐름으로 실행합니다.

```python
def mlops_agent_workflow(trigger_type: str = "full_cycle"):
    results = {"trigger_type": trigger_type}

    if trigger_type in ["scheduled", "full_cycle"]:
        results["batch_prediction"] = run_batch_prediction()

    if trigger_type in ["drift_check", "full_cycle"]:
        drift = check_data_drift()
        results["drift_check"] = drift
        if drift["drift_detected"]:
            results["retraining"] = trigger_retraining(reason="auto_drift_detection")

    results["model_status"] = get_model_status()
    return results
```

{% hint style="info" %}
실제 운영에서는 이 Agent를 **Model Serving 엔드포인트** 로 배포하여, Workflow Trigger나 API 호출로 자동 실행할 수 있습니다. MLflow Tracing으로 Agent의 모든 Tool 호출 이력이 추적됩니다.
{% endhint %}

**다음 단계**: [10. Job 스케줄링](10-job-scheduling.md)
