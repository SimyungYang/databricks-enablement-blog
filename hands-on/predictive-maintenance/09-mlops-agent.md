# 09. MLOps Agent

**목적**: AI Agent가 Trigger에 따라 MLOps Tool을 자동 호출하여 학습/예측을 오케스트레이션합니다.

**주요 개념**:
- Tool 함수 정의: `check_data_drift`, `trigger_retraining`, `run_batch_prediction`, `get_model_status`
- 시스템 프롬프트 기반 자동화 규칙
- 드리프트 감지 시 자동 재학습, 스케줄 기반 배치 예측

**핵심 코드 — Agent 워크플로우**:

```python
def mlops_agent_workflow(trigger_type: str = "full_cycle"):
    results = {}
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

**사용 Databricks 기능**: AI Agent (ChatAgent), UC Functions as Tools, Model Serving, MLflow Tracing
