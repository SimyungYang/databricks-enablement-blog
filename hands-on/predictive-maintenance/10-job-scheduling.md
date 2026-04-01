# 10. Job 스케줄링 (Databricks Workflows)

> **전체 노트북 코드**: [10_job_scheduling.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/10_job_scheduling.py)


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

---

## Level 2 MLOps Pipeline Job

> **전체 노트북 코드**: [10_job_scheduling.py (Level 2 섹션)](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/10_job_scheduling.py)

기존 Level 1 파이프라인(6개 태스크)에 **드리프트 기반 자동 재학습**이 추가된 것이 Level 2의 핵심입니다.

### 7-Task 자동 재학습 파이프라인 구성

```
[Level 2 파이프라인 흐름]
 02_Feature_Eng → 03_Model_Train → 04_Model_Reg → 05_Validation
                                                        ↓
                                                   06_Batch_Infer
                                                        ↓
                                                   08_Monitoring (드리프트 감지)
                                                        ↓
                                                   03d_Retrain (조건부 자동 재학습)
```

| Task # | Task Key | 노트북 | 설명 |
|--------|----------|--------|------|
| 1 | `feature_engineering` | 02_structured_feature_engineering | 센서 데이터 → 7개 파생 피처 생성 |
| 2 | `model_training` | 03_structured_model_training | XGBoost 학습 + SHAP 해석 |
| 3 | `model_registration` | 04_model_registration_uc | UC Model Registry 등록 |
| 4 | `challenger_validation` | 05_challenger_validation | 4단계 자동 검증 |
| 5 | `batch_inference` | 06_batch_inference | Champion 모델 배치 예측 |
| 6 | `model_monitoring` | 08_model_monitoring | PSI 드리프트 탐지 + taskValues 플래그 전달 |
| 7 | `auto_retrain_if_drift` | 03d_retraining_strategies | 드리프트 감지 시 자동 재학습 → Champion 교체 |

### Databricks SDK로 Job 생성

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import (
    Task, NotebookTask, TaskDependency,
    CronSchedule, PauseStatus,
)

w = WorkspaceClient()
job_name = "LGIT_MLOps_Level2_AutoRetrain_Pipeline"

tasks = [
    Task(task_key="feature_engineering",
         notebook_task=NotebookTask(notebook_path=f"{notebook_base}/02_structured_feature_engineering")),
    Task(task_key="model_training",
         depends_on=[TaskDependency(task_key="feature_engineering")],
         notebook_task=NotebookTask(notebook_path=f"{notebook_base}/03_structured_model_training")),
    Task(task_key="model_registration",
         depends_on=[TaskDependency(task_key="model_training")],
         notebook_task=NotebookTask(notebook_path=f"{notebook_base}/04_model_registration_uc")),
    Task(task_key="challenger_validation",
         depends_on=[TaskDependency(task_key="model_registration")],
         notebook_task=NotebookTask(notebook_path=f"{notebook_base}/05_challenger_validation")),
    Task(task_key="batch_inference",
         depends_on=[TaskDependency(task_key="challenger_validation")],
         notebook_task=NotebookTask(notebook_path=f"{notebook_base}/06_batch_inference")),
    Task(task_key="model_monitoring",
         depends_on=[TaskDependency(task_key="batch_inference")],
         notebook_task=NotebookTask(notebook_path=f"{notebook_base}/08_model_monitoring")),
    Task(task_key="auto_retrain_if_drift",
         depends_on=[TaskDependency(task_key="model_monitoring")],
         notebook_task=NotebookTask(notebook_path=f"{notebook_base}/03d_retraining_strategies")),
]

created_job = w.jobs.create(
    name=job_name,
    tasks=tasks,
    schedule=CronSchedule(
        quartz_cron_expression="0 0 2 ? * MON",  # 매주 월요일 02:00 KST
        timezone_id="Asia/Seoul",
        pause_status=PauseStatus.PAUSED,
    ),
    tags={"project": "lgit-mlops-poc", "level": "2", "type": "auto-retrain"},
    max_concurrent_runs=1,
)
```

{% hint style="info" %}
**Level 1 vs Level 2 차이**: Level 1 Job은 6개 태스크(02→03→04→05→06→08)로 모니터링까지만 수행합니다. Level 2 Job은 7번째 태스크(03d)가 추가되어, 드리프트 감지 시 **자동 재학습**까지 수행합니다.
{% endhint %}

### Job 확인 방법

1. 좌측 사이드바 → **Workflows**클릭
2. **LGIT_MLOps_Level2_AutoRetrain_Pipeline**검색
3. **Tasks**탭에서 DAG(의존성 그래프) 확인 — 7개 태스크가 순차 연결
4. **Schedule**탭에서 스케줄 확인 (현재 PAUSED)
5. **Run now**버튼으로 즉시 실행 테스트 가능
