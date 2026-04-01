# 01. Overview — 전체 아키텍처 소개

> **전체 노트북 코드**: [01_overview.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/01_overview.py)


** 목적**: PoC 시나리오 정의 및 전체 파이프라인 아키텍처를 소개합니다.

---

## PoC 시나리오

| 구분 | 상세 |
|------|------|
| ** 정형 데이터**| UCI AI4I 2020 Predictive Maintenance Dataset (10,000건) |
| ** 비정형 데이터**| MVTec AD 산업용 이상탐지 벤치마크 이미지 |
| ** 정형 모델**| XGBoost — 설비 고장 예측 (이진 분류) |
| ** 비정형 모델**| Anomalib PatchCore — 제품 표면 이상탐지 |
| ** 운영 환경**| 주 1회 재학습, 일 4회 배치 예측 |
| ** 개발 환경**| 일 4회 재학습 |
| **Agent**| Trigger에 따라 MLOps Tool의 학습/예측 자동 수행 |

## 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│  정형 데이터(AI4I 2020)     비정형 데이터(MVTec AD)               │
│       │                         │                               │
│       ▼                         ▼                               │
│  Feature Eng.(Spark)       Image Proc.(Anomalib)                │
│       │                         │                               │
│       ▼                         ▼                               │
│  XGBoost Train + SHAP      PatchCore Train   ← MLflow Tracking │
│       │                         │                               │
│       └────────┬────────────────┘                               │
│                ▼                                                │
│       UC Model Registry (Champion / Challenger)                 │
│          │                  │                                   │
│    Batch Predict(일4회)  Model Serve(실시간)  Lakehouse Monitor  │
│                                                                 │
│    MLOps Agent (드리프트→재학습 자동화)                           │
│    Databricks Workflows (운영: 주1회 + 일4회 / 개발: 일4회)      │
└─────────────────────────────────────────────────────────────────┘
```

## Databricks 핵심 기능 매핑

데모에서 활용되는 Databricks 플랫폼 기능의 전체 목록입니다.

```python
# 노트북 목차 — 각 단계에서 사용하는 Databricks 기능
notebooks = {
    "02_feature_engineering":   ["Delta Lake", "Feature Store", "Unity Catalog"],
    "03_model_training":        ["MLflow Tracking", "Autolog", "Data Lineage"],
    "03a_ml_trends":            ["ML 최신 기술 트렌드", "알고리즘 진화 역사"],
    "03b_multi_algorithm":      ["MLflow 실험 비교 UI"],
    "03c_advanced_techniques":  ["Databricks AutoML", "Optuna", "SMOTE"],
    "03d_retraining_strategies":["재학습 전략", "Incremental/Continual/Online Learning"],
    "04_model_registration":    ["UC Model Registry", "Alias", "Lineage"],
    "05_challenger_validation": ["mlflow.evaluate()", "태그 기반 검증"],
    "06_batch_inference":       ["PySpark UDF", "Delta Lake"],
    "07_anomaly_detection":     ["Volumes", "GPU Cluster", "MLflow"],
    "08_model_monitoring":      ["Lakehouse Monitoring", "PSI"],
    "09_mlops_agent":           ["AI Agent", "UC Functions as Tools"],
    "10_job_scheduling":        ["Databricks Workflows"],
}
```

{% hint style="info" %}
이 데모는 제조 현장의 예지보전(Predictive Maintenance)과 비전 기반 이상탐지를 하나의 MLOps 파이프라인으로 통합합니다. 정형/비정형 모델 모두 동일한 Unity Catalog 거버넌스 체계로 관리됩니다.
{% endhint %}

## 데이터셋 소개

** 정형 데이터**— 입력 피처 6개(공기 온도, 공정 온도, 회전속도, 토크, 공구 마모, 제품 타입)로 고장 여부를 이진 분류합니다.

```sql
-- 고장 유형별 분포 확인
SELECT
  machine_failure,
  SUM(twf) as tool_wear_failure,
  SUM(hdf) as heat_dissipation_failure,
  SUM(pwf) as power_failure,
  SUM(osf) as overstrain_failure,
  COUNT(*) as total_count
FROM lgit_pm_bronze
GROUP BY machine_failure
```

**비정형 데이터**— MVTec AD 15개 카테고리, 5,000장 이상 고해상도 이미지. 정상 이미지로 학습하고, 이상 이미지로 테스트합니다.

{% hint style="success" %}
정형 모델과 비정형 모델이 ** 동일한 Unity Catalog** 내에서 관리되므로, 향후 두 모델의 예측을 결합한 ** 복합 판단 시스템(Compound AI System)** 으로 확장할 수 있습니다.
{% endhint %}

** 다음 단계**: [02. 피처 엔지니어링](02-feature-engineering.md)
