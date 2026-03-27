# 08. 모델 모니터링 (Model Monitoring)

**목적**: 운영 중인 모델의 데이터 드리프트 및 성능 저하를 자동 탐지합니다.

**주요 개념**:
- 학습 vs 추론 데이터 분포 비교 (PSI)
- 시계열 기반 예측 분포 추이 모니터링
- Lakehouse Monitoring 자동 설정

**핵심 코드 — Lakehouse Monitor 생성**:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

monitor = w.quality_monitors.create(
    table_name=f"{catalog}.{db}.lgit_pm_inference_results",
    assets_dir=f"/Workspace/Users/{current_user}/lgit_monitoring",
    output_schema_name=f"{catalog}.{db}",
    inference_log={
        "model_id_col": "model_name",
        "prediction_col": "failure_probability",
        "timestamp_col": "inference_timestamp",
        "problem_type": "PROBLEM_TYPE_CLASSIFICATION",
    },
)
```

**사용 Databricks 기능**: Lakehouse Monitoring, Delta Lake Time Travel, SQL Analytics 대시보드
