# 10. Job 스케줄링 (Databricks Workflows)

**목적**: 운영/개발 환경별 MLOps 파이프라인을 Databricks Workflows로 스케줄링합니다.

**사용 Databricks 기능**: `Databricks Workflows`, `Multi-task Jobs`, `Serverless Compute`, `이메일/Slack 알림`

---

## 워크플로우 아키텍처

```
[운영 환경 — 주 1회 재학습]
 02_Feature_Eng → 03_Model_Train → 04_Model_Reg → 05_Validation

[운영 환경 — 일 4회 배치 예측]
 06_Batch_Infer → 08_Monitoring

[개발 환경 — 일 4회 재학습]
 02_Feature_Eng → 03_Model_Train → 04_Model_Reg
```

## 스케줄 요약

| Job | 환경 | Cron (KST) | 설명 |
|-----|------|------------|------|
| `Prod_Weekly_Retraining` | 운영 | `0 2 * * 1` | 매주 월 02:00 재학습 |
| `Prod_Batch_Inference` | 운영 | `0 0,6,12,18 * * *` | 일 4회 배치 예측 |
| `Dev_Daily_Retraining` | 개발 | `0 0,6,12,18 * * *` | 일 4회 실험 재학습 |

## Databricks SDK로 Job 생성

Multi-task Job을 프로그래밍 방식으로 정의합니다. 태스크 간 의존성을 `depends_on`으로 지정합니다.

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

prod_training_tasks = [
    {
        "task_key": "feature_engineering",
        "notebook_task": {"notebook_path": f"{notebook_base}/02_structured_feature_engineering"},
    },
    {
        "task_key": "model_training",
        "notebook_task": {"notebook_path": f"{notebook_base}/03_structured_model_training"},
        "depends_on": [{"task_key": "feature_engineering"}],
    },
    {
        "task_key": "model_registration",
        "notebook_task": {"notebook_path": f"{notebook_base}/04_model_registration_uc"},
        "depends_on": [{"task_key": "model_training"}],
    },
    {
        "task_key": "challenger_validation",
        "notebook_task": {"notebook_path": f"{notebook_base}/05_challenger_validation"},
        "depends_on": [{"task_key": "model_registration"}],
    },
]
```

## 비용 최적화 가이드

| 용도 | 추천 인스턴스 | 비고 |
|------|--------------|------|
| 정형 학습/추론 (XGBoost) | m5.large ~ m5.xlarge | CPU 충분 |
| 비정형 학습 (Anomalib) | g5.2xlarge | GPU 필수 |
| 비정형 추론 | g4dn.2xlarge | 비용 최적화 GPU |
| 간단한 태스크 | Serverless | 가장 비용 효율적 |

{% hint style="success" %}
Databricks **Serverless Compute**를 사용하면 클러스터 관리 없이 자동으로 리소스가 할당됩니다. 정형 데이터 처리에는 Serverless를 권장합니다. 비정형(GPU) 작업만 전용 클러스터를 사용하세요.
{% endhint %}

## 전체 데모에서 다룬 Databricks MLOps 기능

| # | 기능 | 노트북 |
|---|------|--------|
| 1 | Delta Lake + Unity Catalog 데이터 관리 | 02 피처 엔지니어링 |
| 2 | MLflow 실험 추적 + Autolog | 03 모델 학습 |
| 3 | SHAP 모델 해석 | 03 모델 학습 |
| 4 | UC 모델 레지스트리 + Lineage | 04 모델 등록 |
| 5 | Champion/Challenger 패턴 | 05 챌린저 검증 |
| 6 | PySpark UDF 배치 추론 | 06 배치 추론 |
| 7 | Volumes + GPU 비정형 처리 | 07 이상탐지 |
| 8 | Lakehouse Monitoring | 08 모니터링 |
| 9 | AI Agent 오케스트레이션 | 09 MLOps Agent |
| 10 | Workflows 스케줄링 | 10 Job 스케줄링 |
