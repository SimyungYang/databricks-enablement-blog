# Databricks notebook source
# MAGIC %md
# MAGIC # Job 스케줄링: 운영/개발 환경 워크플로우
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Lakeflow Jobs(구 Lakeflow Jobs)란?
# MAGIC
# MAGIC **Lakeflow Jobs**는 여러 개의 작업(Task)을 정해진 순서와 스케줄에 따라 자동으로 실행하는 **작업 오케스트레이터(Orchestrator, 지휘자)** 입니다.
# MAGIC
# MAGIC ### 제조 현장 비유: MES(제조실행시스템)와 같은 역할
# MAGIC
# MAGIC | MES의 역할 | Lakeflow Jobs의 역할 |
# MAGIC |-----------|---------------------------|
# MAGIC | 생산 스케줄 관리 (언제 어떤 라인을 가동할지) | Job 스케줄 관리 (언제 어떤 노트북을 실행할지) |
# MAGIC | 공정 순서 제어 (A공정 → B공정 → C공정) | Task 의존성 관리 (피처 → 학습 → 등록 → 검증) |
# MAGIC | 설비 할당 (어떤 기계를 사용할지) | 클러스터 할당 (어떤 컴퓨팅 자원을 사용할지) |
# MAGIC | 이상 발생 시 알림 | Job 실패 시 이메일/Slack 알림 |
# MAGIC | 생산 이력 추적 | Job 실행 이력 자동 기록 |
# MAGIC
# MAGIC ### DAG(Directed Acyclic Graph, 방향성 비순환 그래프)란?
# MAGIC
# MAGIC 여러 Task 간의 **실행 순서와 의존 관계** 를 표현하는 방법입니다.
# MAGIC
# MAGIC ```
# MAGIC [간단한 예시]
# MAGIC
# MAGIC Task A (피처 엔지니어링) ──→ Task B (모델 학습) ──→ Task C (모델 등록)
# MAGIC                                                          │
# MAGIC                                                          ↓
# MAGIC                                                    Task D (검증)
# MAGIC ```
# MAGIC
# MAGIC - **방향성(Directed)**: 화살표 방향으로만 실행 (A가 끝나야 B 시작)
# MAGIC - **비순환(Acyclic)**: 순환하지 않음 (A→B→C→A 같은 무한 루프 불가)
# MAGIC - 제조 비유: 부품 가공(A) → 조립(B) → 검사(C)처럼, **이전 공정이 완료되어야 다음 공정 시작**
# MAGIC
# MAGIC ### Cron 표현식 이해하기
# MAGIC
# MAGIC Job의 실행 시간을 지정할 때 **Cron 표현식** 이라는 형식을 사용합니다. 5개의 숫자/기호로 "언제 실행할지"를 표현합니다:
# MAGIC
# MAGIC ```
# MAGIC ┌───────────── 분 (0-59)
# MAGIC │ ┌───────────── 시 (0-23)
# MAGIC │ │ ┌───────────── 일 (1-31)
# MAGIC │ │ │ ┌───────────── 월 (1-12)
# MAGIC │ │ │ │ ┌───────────── 요일 (0=일, 1=월, ..., 6=토)
# MAGIC │ │ │ │ │
# MAGIC * * * * *
# MAGIC ```
# MAGIC
# MAGIC | Cron 표현식 | 의미 | 이 PoC에서의 용도 |
# MAGIC |------------|------|-----------------|
# MAGIC | `0 2 * * 1` | 매주 **월요일** 02:00 | 운영 환경 주간 재학습 |
# MAGIC | `0 0,6,12,18 * * *` | 매일 00:00, 06:00, 12:00, 18:00 (일 4회) | 운영 배치 예측 / 개발 재학습 |
# MAGIC | `*/30 * * * *` | 매 30분마다 | (참고) 빈번한 모니터링용 |
# MAGIC | `0 9 1 * *` | 매월 1일 09:00 | (참고) 월간 보고서 생성용 |
# MAGIC
# MAGIC ### 왜 Job 스케줄링이 MLOps에 중요한가?
# MAGIC
# MAGIC MLOps의 핵심 원칙 중 하나는 **CT(Continuous Training, 지속적 학습)** 입니다.
# MAGIC
# MAGIC - 공장에서 설비를 한 번 설치하면 끝이 아니라, **정기 점검과 유지보수** 가 필수인 것처럼
# MAGIC - AI 모델도 한 번 학습하면 끝이 아니라, **정기적으로 새 데이터로 재학습** 해야 합니다
# MAGIC - Job 스케줄링은 이 "정기적 재학습"을 **사람이 매번 수동으로 실행하지 않아도 되도록** 자동화합니다
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 개발 환경 vs 운영 환경: 왜 분리하나?
# MAGIC
# MAGIC | 항목 | 개발(Dev) 환경 | 운영(Prod) 환경 |
# MAGIC |------|-------------|---------------|
# MAGIC | **목적** | 새로운 모델/기법 실험 | 실제 예측 결과를 생산 현장에 제공 |
# MAGIC | **데이터** | 샘플 데이터 또는 전체 데이터 | 실시간 생산 데이터 |
# MAGIC | **재학습 빈도** | 자주 (일 4회, 빠른 실험) | 안정적 (주 1회, 충분한 검증 후) |
# MAGIC | **모델 배포** | Challenger(도전자)로만 등록 | Champion(챔피언)으로 승급 필요 |
# MAGIC | **장애 영향** | 없음 (실험 환경) | 심각 (생산 라인에 영향) |
# MAGIC | **제조 비유** | 파일럿 라인(Pilot Line) | 양산 라인(Mass Production Line) |
# MAGIC
# MAGIC > **핵심 원칙**: 개발 환경에서 충분히 실험하고 검증한 후, 운영 환경에 적용합니다. 이것은 제조업에서 "시제품 → 파일럿 → 양산"의 단계별 이관과 동일한 원칙입니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC - **Lakeflow Jobs**: 노트북/파이프라인 자동 스케줄링
# MAGIC - **Multi-task Jobs**: 여러 노트북을 DAG로 연결
# MAGIC - **환경별 스케줄**: 운영/개발 환경 분리
# MAGIC - **알림**: 작업 성공/실패 시 이메일/Slack 알림
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 스케줄 요구사항
# MAGIC
# MAGIC | 환경 | 작업 | 주기 | 리소스 | 비유 |
# MAGIC |------|------|------|--------|------|
# MAGIC | **운영** | 재학습 | 주 1회 (월요일 02:00) | m5.xlarge | 양산 라인 주간 정비 |
# MAGIC | **운영** | 배치 예측 | 일 4회 (6h 간격) | m5.large | 교대조별 품질 예측 |
# MAGIC | **개발** | 재학습 | 일 4회 (6h 간격) | m5.large | 파일럿 라인 실험 |

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
# MAGIC 아래 다이어그램은 이 PoC에서 구성하는 **3개 Job의 DAG(작업 흐름도)** 를 보여줍니다. 화살표(→)는 "앞 작업이 성공적으로 완료된 후에 다음 작업을 시작한다"는 의미입니다.
# MAGIC
# MAGIC ```
# MAGIC ═══════════════════════════════════════════════════════════════════
# MAGIC [Job 1] 운영 환경 - 주 1회 재학습 (매주 월요일 02:00 KST)
# MAGIC ═══════════════════════════════════════════════════════════════════
# MAGIC ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
# MAGIC │ 02_Feature_Eng  │───►│ 03_Model_Train  │───►│ 04_Model_Reg   │
# MAGIC │ (원재료 가공)    │    │ (모델 생성)      │    │ (모델 등록)     │
# MAGIC └────────────────┘    └────────────────┘    └────────┬───────┘
# MAGIC                                                      │
# MAGIC                                             ┌────────▼───────┐
# MAGIC                                             │ 05_Validation   │
# MAGIC                                             │ (품질 검증)      │
# MAGIC                                             └────────────────┘
# MAGIC
# MAGIC ═══════════════════════════════════════════════════════════════════
# MAGIC [Job 2] 운영 환경 - 일 4회 배치 예측 (00:00, 06:00, 12:00, 18:00)
# MAGIC ═══════════════════════════════════════════════════════════════════
# MAGIC ┌────────────────┐    ┌────────────────┐
# MAGIC │ 06_Batch_Infer  │───►│ 08_Monitoring   │
# MAGIC │ (예측 수행)      │    │ (결과 모니터링)  │
# MAGIC └────────────────┘    └────────────────┘
# MAGIC
# MAGIC ═══════════════════════════════════════════════════════════════════
# MAGIC [Job 3] 개발 환경 - 일 4회 재학습 (00:00, 06:00, 12:00, 18:00)
# MAGIC ═══════════════════════════════════════════════════════════════════
# MAGIC ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
# MAGIC │ 02_Feature_Eng  │───►│ 03_Model_Train  │───►│ 04_Model_Reg   │
# MAGIC │ (피처 실험)      │    │ (모델 실험)      │    │ (Challenger만) │
# MAGIC └────────────────┘    └────────────────┘    └────────────────┘
# MAGIC ```
# MAGIC
# MAGIC > **운영 vs 개발 차이점**: 운영 Job 1에는 `05_Validation`(검증) 단계가 있습니다. 새 모델이 기존 Champion 모델보다 나은 성능을 증명해야만 교체됩니다. 개발 Job 3에는 검증 없이 Challenger로만 등록하여 빠른 실험을 가능하게 합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Job 생성 (Databricks SDK)
# MAGIC
# MAGIC ### Job 생성 방법: 두 가지 방식
# MAGIC
# MAGIC Databricks에서 Job을 만드는 방법은 크게 두 가지입니다:
# MAGIC
# MAGIC | 방식 | 설명 | 장점 | 단점 |
# MAGIC |------|------|------|------|
# MAGIC | **UI(화면)에서 생성** | Databricks 웹 화면에서 클릭으로 설정 | 직관적, 처음 배우기 쉬움 | 여러 환경에 동일 설정 반복 어려움 |
# MAGIC | **SDK(코드)로 생성** | Python 코드로 Job을 프로그래밍 방식으로 생성 | 재현 가능, 버전 관리, 자동화 | 코드 작성 필요 |
# MAGIC
# MAGIC 이 노트북에서는 **Databricks SDK(Software Development Kit)** 를 사용하여 코드로 Job을 생성합니다. 이렇게 하면 Job 설정 자체가 코드로 남아 버전 관리가 가능하고, 다른 환경에 동일한 설정을 쉽게 복제할 수 있습니다.
# MAGIC
# MAGIC ### Databricks UI에서 Job 만드는 방법 (참고)
# MAGIC
# MAGIC 코드가 아닌 웹 화면에서도 동일한 Job을 만들 수 있습니다:
# MAGIC
# MAGIC 1. **좌측 메뉴** → `Workflows` 클릭
# MAGIC 2. **Create Job** 버튼 클릭
# MAGIC 3. **Task 추가**: "Add task" → 노트북 경로 지정 → 의존성(depends_on) 설정
# MAGIC 4. **스케줄 설정**: "Add trigger" → "Scheduled" → Cron 표현식 또는 캘린더에서 선택
# MAGIC 5. **클러스터 설정**: "Compute" → Serverless 또는 클러스터 유형 선택
# MAGIC 6. **알림 설정**: "Notifications" → 이메일/Slack 알림 추가
# MAGIC 7. **Create** 버튼으로 Job 생성 완료

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
# MAGIC ### Job 1: 운영 환경 -- 주 1회 재학습 (Weekly Retraining)
# MAGIC
# MAGIC 이 Job은 **양산 라인의 주간 정비** 에 해당합니다. 매주 월요일 새벽 02:00(생산이 적은 시간대)에 자동으로 실행되어, 최신 데이터로 모델을 재학습하고, 기존 모델보다 성능이 좋으면 교체합니다.
# MAGIC
# MAGIC **Task 흐름**: 피처 엔지니어링 → 모델 학습 → 모델 등록 → Champion/Challenger 검증
# MAGIC
# MAGIC > **왜 주 1회인가?**: 운영 환경에서는 안정성이 최우선입니다. 너무 자주 모델을 교체하면 예측 결과의 일관성이 떨어지고, 문제 발생 시 원인 추적이 어렵습니다. 주 1회는 "충분한 새 데이터가 쌓이되, 안정적으로 운영"하기 위한 균형점입니다.

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
# MAGIC ### Job 2: 운영 환경 -- 일 4회 배치 예측
# MAGIC
# MAGIC 이 Job은 **교대조(Shift)마다 전체 설비 상태를 점검** 하는 것에 해당합니다. 하루 4번(00:00, 06:00, 12:00, 18:00), Champion 모델이 최신 센서 데이터에 대해 고장 확률을 예측하고, 예측 결과를 모니터링합니다.
# MAGIC
# MAGIC **Task 흐름**: 배치 추론(예측 수행) → 모델 모니터링(드리프트 탐지)
# MAGIC
# MAGIC > **왜 일 4회인가?**: 6시간 간격은 생산 현장의 3교대 체계와 유사합니다. 각 교대조가 시작될 때 최신 예측 결과를 확인할 수 있습니다. 더 실시간 예측이 필요하면 Model Serving(실시간 API)을 사용할 수 있습니다.

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
# MAGIC ### Job 3: 개발 환경 -- 일 4회 재학습
# MAGIC
# MAGIC 이 Job은 **파일럿 라인(Pilot Line)에서의 빠른 실험** 에 해당합니다. 하루 4번 새로운 모델을 학습하여, 다양한 알고리즘/하이퍼파라미터 조합을 빠르게 테스트합니다.
# MAGIC
# MAGIC **Task 흐름**: 피처 엔지니어링 → 모델 학습 → 모델 등록 (Challenger만, Champion 승급 없음)
# MAGIC
# MAGIC > **운영 Job과의 차이점**: 검증(Validation) 단계가 없습니다. 개발 환경에서는 빠른 실험이 목적이므로, Champion/Challenger 비교 없이 Challenger로만 등록합니다. 유망한 Challenger는 수동으로 검토한 후 운영 환경에서 검증을 거쳐 Champion으로 승급됩니다.

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
# MAGIC | Job | 환경 | Cron (KST) | 해석 | 제조 비유 |
# MAGIC |-----|------|------------|------|----------|
# MAGIC | `LGIT_MLOps_Prod_Weekly_Retraining` | 운영 | `0 2 * * 1` | 매주 **월요일 02:00** | 양산 라인 주간 정비 |
# MAGIC | `LGIT_MLOps_Prod_Batch_Inference` | 운영 | `0 0,6,12,18 * * *` | 매일 **00/06/12/18시** (일 4회) | 교대조별 품질 예측 |
# MAGIC | `LGIT_MLOps_Dev_Daily_Retraining` | 개발 | `0 0,6,12,18 * * *` | 매일 **00/06/12/18시** (일 4회) | 파일럿 라인 실험 |
# MAGIC
# MAGIC > **Cron 표현식 복습**: `0 2 * * 1`에서 `0`=0분, `2`=2시, `*`=매일, `*`=매월, `1`=월요일 → "매주 월요일 02시 00분"
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 4. 비용 최적화 가이드
# MAGIC
# MAGIC 클라우드 환경에서 ML 워크로드를 실행할 때, **적절한 컴퓨팅 리소스 선택** 이 비용에 큰 영향을 미칩니다. 제조업에서 공정별로 적합한 설비를 선택하는 것과 같습니다.
# MAGIC
# MAGIC ### Serverless vs Dedicated 클러스터
# MAGIC
# MAGIC | 항목 | Serverless (서버리스) | Dedicated Cluster (전용 클러스터) |
# MAGIC |------|---------------------|-------------------------------|
# MAGIC | **개념** | Databricks가 자동으로 컴퓨팅 자원을 할당/해제 | 사용자가 직접 클러스터 유형과 크기를 지정 |
# MAGIC | **시작 시간** | 수 초 이내 (매우 빠름) | 수 분 (클러스터 생성 시간 필요) |
# MAGIC | **비용 구조** | 사용한 만큼만 과금 (초 단위) | 클러스터 가동 시간 전체 과금 |
# MAGIC | **관리 부담** | 없음 (자동) | 클러스터 설정, 모니터링, 종료 관리 필요 |
# MAGIC | **적합한 작업** | 간단한 ETL, 피처 엔지니어링, 배치 추론 | GPU 학습, 대규모 분산 처리 |
# MAGIC | **제조 비유** | 외주 가공 (필요할 때만 의뢰) | 자사 설비 (항상 보유, 유지비 발생) |
# MAGIC
# MAGIC ### 작업 유형별 추천 리소스
# MAGIC
# MAGIC | 리소스 | 용도 | 추천 인스턴스 | 예상 비용 수준 | 비고 |
# MAGIC |--------|------|--------------|-------------|------|
# MAGIC | 정형 학습/추론 | XGBoost | m5.large ~ m5.xlarge | 낮음 | CPU만으로 충분. XGBoost는 GPU 없이도 빠름 |
# MAGIC | 비정형 학습 | Anomalib PatchCore | g5.2xlarge | 높음 | GPU 필수. 딥러닝 모델은 GPU가 있어야 합리적 시간 내 학습 |
# MAGIC | 비정형 추론 | 이미지 분류 | g4dn.2xlarge | 중간 | 추론은 학습보다 리소스가 적게 필요하므로 저렴한 GPU 사용 |
# MAGIC | Serverless | 피처 엔지니어링, 간단한 태스크 | 자동 할당 | 가장 낮음 | 클러스터 관리 불필요, 가장 비용 효율적 |
# MAGIC
# MAGIC > **Tip**: Databricks Serverless Compute를 사용하면 클러스터 관리 없이 자동으로 리소스가 할당됩니다.
# MAGIC > 정형 데이터 처리(피처 엔지니어링, XGBoost 학습/추론)에는 **Serverless를 우선 권장** 합니다. GPU가 필요한 비정형 데이터 처리만 전용 클러스터를 사용하세요.
# MAGIC
# MAGIC > **비용 절감 팁**: 개발 환경에서는 Spot Instance(AWS의 예비 컴퓨팅 자원, 최대 90% 저렴)를 활용하면 비용을 크게 줄일 수 있습니다. 다만 Spot은 언제든 회수될 수 있으므로, 운영 환경에서는 On-Demand(안정적)를 사용합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC ### 이 노트북에서 배운 내용
# MAGIC
# MAGIC | # | 학습 항목 | 핵심 내용 | 제조 비유 |
# MAGIC |---|---------|---------|----------|
# MAGIC | 1 | **Lakeflow Jobs** | 여러 Task를 DAG로 연결하여 자동 실행 | MES(제조실행시스템) |
# MAGIC | 2 | **Cron 스케줄링** | 시간/요일/주기를 5자리 표현식으로 지정 | 생산 계획 스케줄러 |
# MAGIC | 3 | **운영/개발 환경 분리** | 안정성(운영)과 실험 속도(개발)의 균형 | 양산 라인 vs 파일럿 라인 |
# MAGIC | 4 | **비용 최적화** | Serverless, Spot Instance, 작업별 적정 리소스 | 공정별 적합 설비 선택 |
# MAGIC
# MAGIC ### MLOps에서 Job 스케줄링의 위치
# MAGIC
# MAGIC ```
# MAGIC [MLOps 자동화 3요소]
# MAGIC
# MAGIC 1. CI/CD (Continuous Integration/Deployment)  → 코드 변경 시 자동 테스트 & 배포
# MAGIC 2. CT (Continuous Training)                    → 정기적 모델 재학습 ← Job 스케줄링이 담당
# MAGIC 3. CM (Continuous Monitoring)                  → 모델 성능 지속 감시
# MAGIC ```
# MAGIC
# MAGIC Job 스케줄링은 이 중에서 **CT(Continuous Training, 지속적 학습)** 를 실현하는 핵심 수단입니다. 이것이 없으면 데이터 과학자가 매번 수동으로 재학습을 실행해야 하며, 이는 확장 불가능(Scalable하지 않음)합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 전체 데모 완료!
# MAGIC
# MAGIC 축하합니다! 10개의 노트북을 통해 **Databricks MLOps의 전체 생명주기** 를 경험하셨습니다.
# MAGIC
# MAGIC 이 데모에서 다룬 Databricks MLOps 기능과 제조 현장 대응 개념을 정리합니다:
# MAGIC
# MAGIC | # | Databricks 기능 | 노트북 | 제조 현장 대응 개념 |
# MAGIC |---|----------------|--------|------------------|
# MAGIC | 1 | Delta Lake + Unity Catalog 데이터 관리 | 02_structured_feature_engineering | ERP + MRP (자재/데이터 관리) |
# MAGIC | 2 | MLflow 실험 추적 + Autolog | 03_structured_model_training | 실험일지/양산 시험 성적서 |
# MAGIC | 3 | SHAP 모델 해석 | 03_structured_model_training | 불량 원인 분석 (Root Cause Analysis) |
# MAGIC | 4 | UC 모델 레지스트리 + Lineage | 04_model_registration_uc | 버전 관리 + 로트 추적 |
# MAGIC | 5 | Champion/Challenger 패턴 | 05_challenger_validation | 신규 설비 병행 운전 (Parallel Run) |
# MAGIC | 6 | PySpark UDF 배치 추론 | 06_batch_inference | 교대조별 전체 설비 점검 |
# MAGIC | 7 | Volumes + GPU 비정형 처리 | 07_unstructured_anomaly_detection | AOI 자동 광학 검사 |
# MAGIC | 8 | Data Quality Monitoring(구 Data Quality Monitoring) | 08_model_monitoring | SPC 통계적 공정 관리 |
# MAGIC | 9 | AI Agent 오케스트레이션 | 09_mlops_agent | 자동화된 공장 관리자 (Supervisor) |
# MAGIC | 10 | Workflows 스케줄링 | 10_job_scheduling | MES 제조실행시스템 |
# MAGIC
# MAGIC > **다음 단계 제안**: 이 PoC를 기반으로 LG Innotek의 실제 데이터(센서 데이터, 검사 이미지)에 적용하여, 실제 비즈니스 가치를 검증하는 것을 권장합니다. 데이터만 교체하면 동일한 파이프라인 구조를 그대로 활용할 수 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Level 2 MLOps 파이프라인 Job 생성
# MAGIC
# MAGIC > **이 섹션은 실제로 Databricks Job을 생성합니다.**
# MAGIC > 위의 섹션들은 Job 구성을 설명하기 위한 것이었고, 여기서 실제 Level 2 파이프라인을 만듭니다.
# MAGIC >
# MAGIC > **Level 2 파이프라인 흐름:**
# MAGIC > 1. 피처 엔지니어링 (02)
# MAGIC > 2. 모델 학습 (03)
# MAGIC > 3. 모델 등록 (04)
# MAGIC > 4. Champion/Challenger 검증 (05)
# MAGIC > 5. 배치 추론 (06)
# MAGIC > 6. 모니터링 & 드리프트 감지 (08)
# MAGIC > 7. **[조건부] 드리프트 감지 시 → 자동 재학습 (03d)**
# MAGIC >
# MAGIC > 기존 Level 1 파이프라인에 **드리프트 기반 자동 재학습** 이 추가된 것이 Level 2의 핵심입니다.

# COMMAND ----------

# DBTITLE 1,Level 2 MLOps 파이프라인 Job 실제 생성
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import (
    Task, NotebookTask, TaskDependency,
    CronSchedule, PauseStatus,
)

w = WorkspaceClient()

# 노트북 경로
notebook_base = f"/Workspace/Users/{current_user}/lgit-mlops-poc"

# Level 2 파이프라인 Job 정의
job_name = "LGIT_MLOps_Level2_AutoRetrain_Pipeline"

# 기존 동일 이름 Job 확인
existing_jobs = [j for j in w.jobs.list(name=job_name)]

tasks = [
    # Task 1: 피처 엔지니어링
    Task(
        task_key="feature_engineering",
        description="센서 데이터 → 7개 파생 피처 생성 (Bronze → Silver → Gold)",
        notebook_task=NotebookTask(
            notebook_path=f"{notebook_base}/02_structured_feature_engineering",
            source="WORKSPACE"
        ),
    ),
    # Task 2: 모델 학습
    Task(
        task_key="model_training",
        description="XGBoost 학습 + SHAP 해석 + MLflow Autolog",
        depends_on=[TaskDependency(task_key="feature_engineering")],
        notebook_task=NotebookTask(
            notebook_path=f"{notebook_base}/03_structured_model_training",
            source="WORKSPACE"
        ),
    ),
    # Task 3: 모델 등록
    Task(
        task_key="model_registration",
        description="UC Model Registry 등록 + Challenger 에일리어스 설정",
        depends_on=[TaskDependency(task_key="model_training")],
        notebook_task=NotebookTask(
            notebook_path=f"{notebook_base}/04_model_registration_uc",
            source="WORKSPACE"
        ),
    ),
    # Task 4: Champion/Challenger 검증
    Task(
        task_key="challenger_validation",
        description="4단계 자동 검증 (문서화/추론/성능/비즈니스KPI)",
        depends_on=[TaskDependency(task_key="model_registration")],
        notebook_task=NotebookTask(
            notebook_path=f"{notebook_base}/05_challenger_validation",
            source="WORKSPACE"
        ),
    ),
    # Task 5: 배치 추론
    Task(
        task_key="batch_inference",
        description="Champion 모델로 전체 설비 배치 예측",
        depends_on=[TaskDependency(task_key="challenger_validation")],
        notebook_task=NotebookTask(
            notebook_path=f"{notebook_base}/06_batch_inference",
            source="WORKSPACE"
        ),
    ),
    # Task 6: 모니터링 & 드리프트 감지
    Task(
        task_key="model_monitoring",
        description="PSI 드리프트 탐지 + taskValues로 플래그 전달",
        depends_on=[TaskDependency(task_key="batch_inference")],
        notebook_task=NotebookTask(
            notebook_path=f"{notebook_base}/08_model_monitoring",
            source="WORKSPACE"
        ),
    ),
    # Task 7: [Level 2] 드리프트 기반 자동 재학습
    Task(
        task_key="auto_retrain_if_drift",
        description="[Level 2] 드리프트 감지 시 자동 재학습 → Champion 교체",
        depends_on=[TaskDependency(task_key="model_monitoring")],
        notebook_task=NotebookTask(
            notebook_path=f"{notebook_base}/03d_retraining_strategies",
            source="WORKSPACE"
        ),
    ),
]

# Job 생성 또는 업데이트
try:
    if existing_jobs:
        # 기존 Job 업데이트
        existing_job = existing_jobs[0]
        w.jobs.reset(
            job_id=existing_job.job_id,
            new_settings={
                "name": job_name,
                "tasks": tasks,
                "schedule": CronSchedule(
                    quartz_cron_expression="0 0 2 ? * MON",  # 매주 월요일 02:00
                    timezone_id="Asia/Seoul",
                    pause_status=PauseStatus.PAUSED  # 교육용이므로 일시 정지
                ),
                "tags": {"project": "lgit-mlops-poc", "level": "2", "type": "auto-retrain"},
                "max_concurrent_runs": 1
            }
        )
        print(f"✅ 기존 Job 업데이트 완료!")
        print(f"   Job ID: {existing_job.job_id}")
        print(f"   Job Name: {job_name}")
    else:
        # 새 Job 생성
        created_job = w.jobs.create(
            name=job_name,
            tasks=tasks,
            schedule=CronSchedule(
                quartz_cron_expression="0 0 2 ? * MON",  # 매주 월요일 02:00
                timezone_id="Asia/Seoul",
                pause_status=PauseStatus.PAUSED  # 교육용이므로 일시 정지
            ),
            tags={"project": "lgit-mlops-poc", "level": "2", "type": "auto-retrain"},
            max_concurrent_runs=1
        )
        print(f"✅ Level 2 MLOps Job 생성 완료!")
        print(f"   Job ID: {created_job.job_id}")
        print(f"   Job Name: {job_name}")

    print(f"\n📋 태스크 구성 (7개):")
    print(f"   1. feature_engineering → 02_structured_feature_engineering")
    print(f"   2. model_training → 03_structured_model_training")
    print(f"   3. model_registration → 04_model_registration_uc")
    print(f"   4. challenger_validation → 05_challenger_validation")
    print(f"   5. batch_inference → 06_batch_inference")
    print(f"   6. model_monitoring → 08_model_monitoring (드리프트 감지)")
    print(f"   7. auto_retrain_if_drift → 03d_retraining_strategies (Level 2)")
    print(f"\n⏰ 스케줄: 매주 월요일 02:00 KST (현재 PAUSED)")
    print(f"   → Databricks UI에서 Resume하면 자동 실행됩니다")

except Exception as e:
    print(f"⚠️ Job 생성 중 오류: {e}")
    print(f"   권한 또는 클러스터 설정을 확인하세요.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Job 확인 방법
# MAGIC 1. 좌측 사이드바 → **Workflows** 클릭
# MAGIC 2. **LGIT_MLOps_Level2_AutoRetrain_Pipeline** 검색
# MAGIC 3. **Tasks** 탭에서 DAG(의존성 그래프) 확인 — 7개 태스크가 순차 연결
# MAGIC 4. **Schedule** 탭에서 스케줄 확인 (현재 PAUSED)
# MAGIC 5. **Run now** 버튼으로 즉시 실행 테스트 가능
# MAGIC
# MAGIC > **Level 1 vs Level 2 차이**: Level 1 Job은 6개 태스크(02→03→04→05→06→08)로 모니터링까지만 합니다.
# MAGIC > Level 2 Job은 7번째 태스크(03d)가 추가되어, 드리프트 감지 시 **자동 재학습** 까지 수행합니다.
