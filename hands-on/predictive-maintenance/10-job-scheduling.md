# 10. Job 스케줄링 (Databricks Workflows)

> **전체 노트북 코드**: [10_job_scheduling.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/10_job_scheduling.py)


**목적**: 운영/개발 환경별 MLOps 파이프라인을 Databricks Workflows로 스케줄링합니다.

**사용 Databricks 기능**: `Databricks Workflows`, `Multi-task Jobs`, `Serverless Compute`, `이메일/Slack 알림`

---

## Lakeflow Jobs란?

**Lakeflow Jobs** 는 여러 개의 작업(Task)을 정해진 순서와 스케줄에 따라 자동으로 실행하는 **작업 오케스트레이터(Orchestrator, 지휘자)** 입니다. 제조 현장의 MES(제조실행시스템)와 같은 역할을 합니다.

| MES의 역할 | Lakeflow Jobs의 역할 |
|-----------|---------------------------|
| 생산 스케줄 관리 (언제 어떤 라인을 가동할지) | Job 스케줄 관리 (언제 어떤 노트북을 실행할지) |
| 공정 순서 제어 (A공정 → B공정 → C공정) | Task 의존성 관리 (피처 → 학습 → 등록 → 검증) |
| 설비 할당 (어떤 기계를 사용할지) | 클러스터 할당 (어떤 컴퓨팅 자원을 사용할지) |
| 이상 발생 시 알림 | Job 실패 시 이메일/Slack 알림 |

### Cron 표현식 이해하기

Job의 실행 시간을 지정할 때 **Cron 표현식** 이라는 형식을 사용합니다. 다음 표는 이 PoC에서 사용하는 Cron 표현식입니다.

| Cron 표현식 | 의미 | 이 PoC에서의 용도 |
|------------|------|-----------------|
| `0 2 * * 1` | 매주 **월요일**02:00 | 운영 환경 주간 재학습 |
| `0 0,6,12,18 * * *` | 매일 00:00, 06:00, 12:00, 18:00 (일 4회) | 운영 배치 예측 / 개발 재학습 |
| `*/30 * * * *` | 매 30분마다 | (참고) 빈번한 모니터링용 |

### 왜 Job 스케줄링이 MLOps에 중요한가?

MLOps의 핵심 원칙 중 하나는 **CT(Continuous Training, 지속적 학습)** 입니다. 공장에서 설비를 한 번 설치하면 끝이 아니라 **정기 점검과 유지보수** 가 필수인 것처럼, AI 모델도 **정기적으로 새 데이터로 재학습** 해야 합니다. Job 스케줄링은 이 "정기적 재학습"을 사람이 매번 수동으로 실행하지 않아도 되도록 자동화합니다.

### 개발 환경 vs 운영 환경: 왜 분리하나?

| 항목 | 개발(Dev) 환경 | 운영(Prod) 환경 |
|------|-------------|---------------|
| **목적** | 새로운 모델/기법 실험 | 실제 예측 결과를 생산 현장에 제공 |
| **데이터** | 샘플 데이터 또는 전체 데이터 | 실시간 생산 데이터 |
| **재학습 빈도** | 자주 (일 4회, 빠른 실험) | 안정적 (주 1회, 충분한 검증 후) |
| **모델 배포** | Challenger(도전자)로만 등록 | Champion(챔피언)으로 승급 필요 |
| **장애 영향** | 없음 (실험 환경) | 심각 (생산 라인에 영향) |
| **제조 비유** | 파일럿 라인(Pilot Line) | 양산 라인(Mass Production Line) |

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

## Job 생성 방법: 두 가지 방식

Databricks에서 Job을 만드는 방법은 크게 두 가지입니다.

| 방식 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **UI(화면)에서 생성** | Databricks 웹 화면에서 클릭으로 설정 | 직관적, 처음 배우기 쉬움 | 여러 환경에 동일 설정 반복 어려움 |
| **SDK(코드)로 생성** | Python 코드로 Job을 프로그래밍 방식으로 생성 | 재현 가능, 버전 관리, 자동화 | 코드 작성 필요 |

### Databricks UI에서 Job 만드는 방법 (참고)

1. **좌측 메뉴**→ `Workflows` 클릭
2. **Create Job** 버튼 클릭
3. **Task 추가**: "Add task" → 노트북 경로 지정 → 의존성(depends_on) 설정
4. **스케줄 설정**: "Add trigger" → "Scheduled" → Cron 표현식 또는 캘린더에서 선택
5. **클러스터 설정**: "Compute" → Serverless 또는 클러스터 유형 선택
6. **알림 설정**: "Notifications" → 이메일/Slack 알림 추가
7. **Create** 버튼으로 Job 생성 완료

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

## 비정형 모델 (비전 이상탐지) Job 설정

비전 이상탐지(07번 노트북)는 GPU 클러스터가 필요하므로 별도 Job으로 분리합니다. g5.2xlarge (NVIDIA A10G GPU)를 사용하며, 주 1회 재학습 + 일 1회 배치 추론으로 설정합니다.

{% hint style="warning" %}
GPU 클러스터(g5.2xlarge)는 CPU 클러스터 대비 약 10배 비쌉니다. 주 1회 15분 실행 기준 월 약 8 DBU로, 전체 파이프라인 비용의 약 30%를 차지합니다. 비용 최적화를 위해 Spot Instance 활용과 Auto-termination 5분 설정을 권장합니다.
{% endhint %}

## 비용 최적화 가이드

클라우드 환경에서 ML 워크로드를 실행할 때, **적절한 컴퓨팅 리소스 선택** 이 비용에 큰 영향을 미칩니다. 제조업에서 공정별로 적합한 설비를 선택하는 것과 같습니다.

### Serverless vs Dedicated 클러스터

| 항목 | Serverless (서버리스) | Dedicated Cluster (전용 클러스터) |
|------|---------------------|-------------------------------|
| **개념** | Databricks가 자동으로 컴퓨팅 자원을 할당/해제 | 사용자가 직접 클러스터 유형과 크기를 지정 |
| **시작 시간** | 수 초 이내 (매우 빠름) | 수 분 (클러스터 생성 시간 필요) |
| **비용 구조** | 사용한 만큼만 과금 (초 단위) | 클러스터 가동 시간 전체 과금 |
| **관리 부담** | 없음 (자동) | 클러스터 설정, 모니터링, 종료 관리 필요 |
| **적합한 작업** | 간단한 ETL, 피처 엔지니어링, 배치 추론 | GPU 학습, 대규모 분산 처리 |
| **제조 비유** | 외주 가공 (필요할 때만 의뢰) | 자사 설비 (항상 보유, 유지비 발생) |

### 작업 유형별 추천 리소스

| 용도 | 추천 인스턴스 | 예상 비용 수준 | 비고 |
|------|--------------|-------------|------|
| 정형 학습/추론 (XGBoost) | m5.large ~ m5.xlarge | 낮음 | CPU만으로 충분. XGBoost는 GPU 없이도 빠름 |
| 비정형 학습 (Anomalib) | g5.2xlarge | 높음 | GPU 필수. 딥러닝 모델은 GPU가 있어야 합리적 시간 내 학습 |
| 비정형 추론 | g4dn.2xlarge | 중간 | 추론은 학습보다 리소스가 적게 필요 |
| 간단한 태스크 | Serverless | 가장 낮음 | 클러스터 관리 불필요, 가장 비용 효율적 |

{% hint style="success" %}
Databricks **Serverless Compute** 를 사용하면 클러스터 관리 없이 자동으로 리소스가 할당됩니다. 정형 데이터 처리에는 Serverless를 권장합니다. 비정형(GPU) 작업만 전용 클러스터를 사용하세요. 개발 환경에서는 Spot Instance(최대 90% 저렴)를 활용하면 비용을 크게 줄일 수 있습니다.
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

기존 Level 1 파이프라인(6개 태스크)에 **드리프트 기반 자동 재학습** 이 추가된 것이 Level 2의 핵심입니다.

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
**Level 1 vs Level 2 차이**: Level 1 Job은 6개 태스크(02→03→04→05→06→08)로 모니터링까지만 수행합니다. Level 2 Job은 7번째 태스크(03d)가 추가되어, 드리프트 감지 시 **자동 재학습** 까지 수행합니다.
{% endhint %}

### Job 확인 방법

1. 좌측 사이드바 → **Workflows** 클릭
2. **LGIT_MLOps_Level2_AutoRetrain_Pipeline** 검색
3. **Tasks** 탭에서 DAG(의존성 그래프) 확인 — 7개 태스크가 순차 연결
4. **Schedule** 탭에서 스케줄 확인 (현재 PAUSED)
5. **Run now** 버튼으로 즉시 실행 테스트 가능
