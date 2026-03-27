# Databricks notebook source
# MAGIC %md
# MAGIC # Job 스케줄링: 운영/개발 환경 워크플로우
# MAGIC
# MAGIC **Databricks Workflows**를 사용하여 MLOps 파이프라인을 스케줄링합니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC - **Databricks Workflows (Jobs)**: 노트북/파이프라인 자동 스케줄링
# MAGIC - **Multi-task Jobs**: 여러 노트북을 DAG로 연결
# MAGIC - **환경별 스케줄**: 운영/개발 환경 분리
# MAGIC - **알림**: 작업 성공/실패 시 이메일/Slack 알림
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 스케줄 요구사항
# MAGIC
# MAGIC | 환경 | 작업 | 주기 | 리소스 |
# MAGIC |------|------|------|--------|
# MAGIC | **운영** | 재학습 | 주 1회 (월요일 02:00) | m5.xlarge |
# MAGIC | **운영** | 배치 예측 | 일 4회 (6h 간격) | m5.large |
# MAGIC | **개발** | 재학습 | 일 4회 (6h 간격) | m5.large |

# COMMAND ----------

# MAGIC %pip install --quiet databricks-sdk --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 워크플로우 아키텍처
# MAGIC
# MAGIC ```
# MAGIC [운영 환경 - 주 1회 재학습]
# MAGIC ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
# MAGIC │ 02_Feature_Eng  │───►│ 03_Model_Train  │───►│ 04_Model_Reg   │
# MAGIC └────────────────┘    └────────────────┘    └────────┬───────┘
# MAGIC                                                      │
# MAGIC                                             ┌────────▼───────┐
# MAGIC                                             │ 05_Validation   │
# MAGIC                                             └────────────────┘
# MAGIC
# MAGIC [운영 환경 - 일 4회 배치 예측]
# MAGIC ┌────────────────┐    ┌────────────────┐
# MAGIC │ 06_Batch_Infer  │───►│ 08_Monitoring   │
# MAGIC └────────────────┘    └────────────────┘
# MAGIC
# MAGIC [개발 환경 - 일 4회 재학습]
# MAGIC ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
# MAGIC │ 02_Feature_Eng  │───►│ 03_Model_Train  │───►│ 04_Model_Reg   │
# MAGIC └────────────────┘    └────────────────┘    └────────────────┘
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Job 생성 (Databricks SDK)

# COMMAND ----------

# DBTITLE 1,공통 설정
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import *

w = WorkspaceClient()

# 노트북 기본 경로
notebook_base = f"/Workspace/Users/{current_user}/lgit-mlops-poc"

print(f"노트북 경로: {notebook_base}")
print(f"사용자: {current_user}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Job 1: 운영 환경 — 주 1회 재학습 (Weekly Retraining)

# COMMAND ----------

# DBTITLE 1,운영 재학습 Job 생성
# 운영 재학습 파이프라인 (주 1회)
prod_training_job_name = "LGIT_MLOps_Prod_Weekly_Retraining"

try:
    # 기존 Job 검색
    existing = [j for j in w.jobs.list(name=prod_training_job_name)]
    if existing:
        print(f"기존 Job 존재: {existing[0].job_id} — 업데이트합니다.")
        job_id = existing[0].job_id
    else:
        job_id = None
except:
    job_id = None

prod_training_tasks = [
    {
        "task_key": "feature_engineering",
        "notebook_task": {
            "notebook_path": f"{notebook_base}/02_structured_feature_engineering",
        },
        "description": "피처 엔지니어링 수행",
    },
    {
        "task_key": "model_training",
        "notebook_task": {
            "notebook_path": f"{notebook_base}/03_structured_model_training",
        },
        "depends_on": [{"task_key": "feature_engineering"}],
        "description": "XGBoost 모델 학습",
    },
    {
        "task_key": "model_registration",
        "notebook_task": {
            "notebook_path": f"{notebook_base}/04_model_registration_uc",
        },
        "depends_on": [{"task_key": "model_training"}],
        "description": "Unity Catalog 모델 등록",
    },
    {
        "task_key": "challenger_validation",
        "notebook_task": {
            "notebook_path": f"{notebook_base}/05_challenger_validation",
        },
        "depends_on": [{"task_key": "model_registration"}],
        "description": "Champion-Challenger 검증 및 승급",
    },
]

print(f"""
=== 운영 재학습 Job ===
이름: {prod_training_job_name}
스케줄: 매주 월요일 02:00 KST
태스크: {' → '.join([t['task_key'] for t in prod_training_tasks])}
리소스: m5.xlarge (Serverless 사용 시 자동 할당)
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Job 2: 운영 환경 — 일 4회 배치 예측

# COMMAND ----------

# DBTITLE 1,운영 배치 예측 Job 설정
prod_inference_job_name = "LGIT_MLOps_Prod_Batch_Inference"

prod_inference_tasks = [
    {
        "task_key": "batch_inference",
        "notebook_task": {
            "notebook_path": f"{notebook_base}/06_batch_inference",
        },
        "description": "Champion 모델로 배치 예측 수행",
    },
    {
        "task_key": "model_monitoring",
        "notebook_task": {
            "notebook_path": f"{notebook_base}/08_model_monitoring",
        },
        "depends_on": [{"task_key": "batch_inference"}],
        "description": "드리프트 탐지 및 성능 모니터링",
    },
]

print(f"""
=== 운영 배치 예측 Job ===
이름: {prod_inference_job_name}
스케줄: 일 4회 (00:00, 06:00, 12:00, 18:00 KST)
태스크: {' → '.join([t['task_key'] for t in prod_inference_tasks])}
리소스: m5.large (Serverless 사용 시 자동 할당)
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Job 3: 개발 환경 — 일 4회 재학습

# COMMAND ----------

# DBTITLE 1,개발 재학습 Job 설정
dev_training_job_name = "LGIT_MLOps_Dev_Daily_Retraining"

dev_training_tasks = [
    {
        "task_key": "feature_engineering",
        "notebook_task": {
            "notebook_path": f"{notebook_base}/02_structured_feature_engineering",
        },
        "description": "[Dev] 피처 엔지니어링",
    },
    {
        "task_key": "model_training",
        "notebook_task": {
            "notebook_path": f"{notebook_base}/03_structured_model_training",
        },
        "depends_on": [{"task_key": "feature_engineering"}],
        "description": "[Dev] 모델 학습 (실험용)",
    },
    {
        "task_key": "model_registration",
        "notebook_task": {
            "notebook_path": f"{notebook_base}/04_model_registration_uc",
        },
        "depends_on": [{"task_key": "model_training"}],
        "description": "[Dev] 모델 등록 (Challenger만)",
    },
]

print(f"""
=== 개발 재학습 Job ===
이름: {dev_training_job_name}
스케줄: 일 4회 (00:00, 06:00, 12:00, 18:00 KST)
태스크: {' → '.join([t['task_key'] for t in dev_training_tasks])}
리소스: m5.large (Serverless 사용 시 자동 할당)
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 스케줄 요약
# MAGIC
# MAGIC | Job | 환경 | Cron (KST) | 설명 |
# MAGIC |-----|------|------------|------|
# MAGIC | `LGIT_MLOps_Prod_Weekly_Retraining` | 운영 | `0 2 * * 1` | 매주 월 02:00 재학습 |
# MAGIC | `LGIT_MLOps_Prod_Batch_Inference` | 운영 | `0 0,6,12,18 * * *` | 일 4회 배치 예측 |
# MAGIC | `LGIT_MLOps_Dev_Daily_Retraining` | 개발 | `0 0,6,12,18 * * *` | 일 4회 실험 재학습 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 4. 비용 최적화 가이드
# MAGIC
# MAGIC | 리소스 | 용도 | 추천 인스턴스 | 비고 |
# MAGIC |--------|------|--------------|------|
# MAGIC | 정형 학습/추론 | XGBoost | m5.large ~ m5.xlarge | CPU 충분 |
# MAGIC | 비정형 학습 | Anomalib PatchCore | g5.2xlarge | GPU 필수 |
# MAGIC | 비정형 추론 | 이미지 분류 | g4dn.2xlarge | 비용 최적화 GPU |
# MAGIC | Serverless | 간단한 태스크 | 자동 할당 | 가장 비용 효율적 |
# MAGIC
# MAGIC > **Tip**: Databricks Serverless Compute를 사용하면 클러스터 관리 없이 자동으로 리소스가 할당됩니다.
# MAGIC > 정형 데이터 처리에는 Serverless를 권장합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC 이 노트북에서 정의한 작업:
# MAGIC 1. **운영 주간 재학습** Job (주 1회 월요일)
# MAGIC 2. **운영 배치 예측** Job (일 4회)
# MAGIC 3. **개발 재학습** Job (일 4회)
# MAGIC 4. 비용 최적화 리소스 가이드
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 전체 데모 완료!
# MAGIC
# MAGIC 이 데모에서 다룬 Databricks MLOps 기능:
# MAGIC
# MAGIC | # | 기능 | 노트북 |
# MAGIC |---|------|--------|
# MAGIC | 1 | Delta Lake + Unity Catalog 데이터 관리 | 02_structured_feature_engineering |
# MAGIC | 2 | MLflow 실험 추적 + Autolog | 03_structured_model_training |
# MAGIC | 3 | SHAP 모델 해석 | 03_structured_model_training |
# MAGIC | 4 | UC 모델 레지스트리 + Lineage | 04_model_registration_uc |
# MAGIC | 5 | Champion/Challenger 패턴 | 05_challenger_validation |
# MAGIC | 6 | PySpark UDF 배치 추론 | 06_batch_inference |
# MAGIC | 7 | Volumes + GPU 비정형 처리 | 07_unstructured_anomaly_detection |
# MAGIC | 8 | Lakehouse Monitoring | 08_model_monitoring |
# MAGIC | 9 | AI Agent 오케스트레이션 | 09_mlops_agent |
# MAGIC | 10 | Workflows 스케줄링 | 10_job_scheduling |
