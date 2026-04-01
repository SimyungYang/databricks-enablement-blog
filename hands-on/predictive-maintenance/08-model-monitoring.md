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
Lakehouse Monitoring이 생성되면 자동으로 **드리프트 분석 테이블**과 **프로필 테이블** 이 생성됩니다. 이를 기반으로 AI/BI Dashboard를 구성하거나, 임계값 초과 시 Slack/이메일 알림을 설정할 수 있습니다.
{% endhint %}

{% hint style="warning" %}
제조 데이터는 계절 변화, 설비 노후화, 공정 변경 등으로 인해 드리프트가 빈번합니다. 스케줄 기반 재학습만으로는 부족하며, **드리프트 기반 + 성능 기반 하이브리드 트리거** 를 권장합니다.
{% endhint %}

---

## 4. Level 2 자동화: 드리프트 감지 → 재학습 트리거

> **전체 노트북 코드**: [08_model_monitoring.py (Section 2-1)](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/08_model_monitoring.py)

드리프트를 감지하는 것(Level 1)과 **자동으로 행동하는 것(Level 2)** 은 완전히 다른 레벨입니다. Level 1에서는 사람이 PSI 리포트를 보고 재학습을 결정하지만, Level 2에서는 시스템이 자동으로 재학습을 트리거합니다.

### `dbutils.jobs.taskValues`를 사용한 드리프트 플래그 전달

Databricks Workflows의 **taskValues** 메커니즘을 사용하여, 모니터링 태스크에서 감지한 드리프트 결과를 다음 태스크(재학습)로 자동 전달합니다.

```python
# PSI 결과에서 드리프트 여부 판단
drift_features = []
PSI_THRESHOLD = 0.2  # 업계 표준 임계값

for feature, psi_value in psi_results.items():
    if psi_value > PSI_THRESHOLD:
        drift_features.append(f"{feature} (PSI={psi_value:.3f})")

# Databricks Jobs taskValues로 다음 태스크에 플래그 전달
dbutils.jobs.taskValues.set(key="drift_detected", value=drift_detected)
dbutils.jobs.taskValues.set(key="drift_features", value=str(drift_features))
dbutils.jobs.taskValues.set(key="max_psi", value=float(max(psi_results.values())))
```

{% hint style="info" %}
`taskValues`는 Databricks Workflows Job 내에서만 동작합니다. 노트북을 단독으로 실행할 때는 `taskValues` 호출이 무시되므로, try/except로 감싸서 방어적으로 처리합니다.
{% endhint %}

### 5단계 드리프트 대응 절차

| 단계 | 행동 | 담당 | 예시 |
|------|------|------|------|
| **1. 식별**| PSI > 0.2인 피처 확인 | 데이터 엔지니어 | "torque_nm PSI = 0.35" |
| **2. 원인 조사**| 해당 기간의 공정 변경 이력 확인 | 공정 엔지니어 | "지난주 절삭유 교체" |
| **3. 영향 평가**| 드리프트가 모델 성능에 미치는 영향 측정 | ML 엔지니어 | "F1 Score 0.95 → 0.87 하락" |
| **4. 재학습**| 새 데이터 포함하여 모델 재학습 | ML 엔지니어 | 03d 노트북 자동 실행 |
| **5. 재배포**| 검증 후 새 모델 배포 | MLOps | 05번 → 06번 자동 실행 |

{% hint style="warning" %}
드리프트가 감지되었다고 해서 반드시 모델이 나빠진 것은 아닙니다. 공정이 **개선** 되어 데이터 분포가 바뀐 경우도 있으므로, 드리프트 원인을 반드시 공정팀과 함께 분석해야 합니다.
{% endhint %}

### Workflows와의 연동

Level 2 파이프라인에서는 이 모니터링 태스크 다음에 **03d_retraining_strategies** 태스크가 연결됩니다. `drift_detected` 값이 `True`이면 자동 재학습이 수행되고, `False`이면 재학습을 건너뜁니다.

```
[08_model_monitoring] → taskValues.set("drift_detected", True/False)
        ↓
[03d_retraining_strategies] → taskValues.get("drift_detected")
        ↓ (True인 경우에만)
   자동 재학습 → 모델 등록 → Champion 교체
```

**다음 단계**: [09. MLOps Agent](09-mlops-agent.md)
