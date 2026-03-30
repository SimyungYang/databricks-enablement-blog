# 08. 모델 모니터링 (Model Monitoring)

> **전체 노트북 코드**: [08_model_monitoring.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/08_model_monitoring.py)


**목적**: 운영 중인 모델의 데이터 드리프트 및 성능 저하를 PSI 기반으로 탐지하고, Lakehouse Monitoring을 설정합니다.

**사용 Databricks 기능**: `Lakehouse Monitoring`, `Delta Lake Time Travel`, `SQL Analytics 대시보드`

---

## 1. 데이터 드리프트 탐지 — PSI

**PSI (Population Stability Index)** 로 학습 데이터와 추론 데이터의 분포 차이를 정량적으로 측정합니다.

| PSI 값 | 판정 |
|--------|------|
| < 0.1 | 안정 |
| 0.1 ~ 0.2 | 주의 |
| > 0.2 | 드리프트 감지 — 재학습 권장 |

```python
def calculate_psi(expected, actual, bins=10):
    """Population Stability Index 계산"""
    breakpoints = np.linspace(min(expected.min(), actual.min()),
                             max(expected.max(), actual.max()), bins + 1)
    expected_counts = np.maximum(
        np.histogram(expected, bins=breakpoints)[0] / len(expected), 0.001)
    actual_counts = np.maximum(
        np.histogram(actual, bins=breakpoints)[0] / len(actual), 0.001)
    psi = np.sum((actual_counts - expected_counts) * np.log(actual_counts / expected_counts))
    return psi

# 피처별 PSI 계산
for col in feature_columns:
    psi = calculate_psi(train_pdf[col].values, infer_pdf[col].values)
    status = "안정" if psi < 0.1 else ("주의" if psi < 0.2 else "드리프트!")
    print(f"  {col:30s}: PSI = {psi:.4f} ({status})")
```

## 2. 예측 분포 추이 모니터링

시간별 예측 결과 분포 변화를 SQL로 추적합니다.

```sql
SELECT
  date_trunc('hour', inference_timestamp) as prediction_hour,
  COUNT(*) as total_predictions,
  SUM(predicted_failure) as predicted_failures,
  ROUND(AVG(failure_probability), 4) as avg_failure_prob,
  model_version
FROM lgit_pm_inference_results
GROUP BY date_trunc('hour', inference_timestamp), model_version
ORDER BY prediction_hour DESC
LIMIT 24
```

## 3. Lakehouse Monitoring 자동 설정

Databricks Lakehouse Monitoring을 프로그래밍 방식으로 생성합니다. 드리프트 탐지, 데이터 품질, 모델 성능을 자동 추적합니다.

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

{% hint style="info" %}
Lakehouse Monitoring이 생성되면 자동으로 **드리프트 분석 테이블**과 **프로필 테이블**이 생성됩니다. 이를 기반으로 AI/BI Dashboard를 구성하거나, 임계값 초과 시 Slack/이메일 알림을 설정할 수 있습니다.
{% endhint %}

{% hint style="warning" %}
제조 데이터는 계절 변화, 설비 노후화, 공정 변경 등으로 인해 드리프트가 빈번합니다. 스케줄 기반 재학습만으로는 부족하며, **드리프트 기반 + 성능 기반 하이브리드 트리거**를 권장합니다.
{% endhint %}

**다음 단계**: [09. MLOps Agent](09-mlops-agent.md)
