# Databricks notebook source
# MAGIC %md
# MAGIC # LG Innotek MLOps PoC: 엔드투엔드(End-to-End) 예지보전 & 이상탐지
# MAGIC
# MAGIC ## 개요
# MAGIC
# MAGIC 본 데모는 **Databricks Lakehouse 플랫폼**을 활용하여 제조 현장의 **예지보전(Predictive Maintenance)** 및 **비전 기반 이상탐지(Anomaly Detection)** 를 위한 완전한 MLOps 파이프라인을 구축하는 과정을 보여줍니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## PoC 시나리오
# MAGIC
# MAGIC | 구분 | 상세 |
# MAGIC |------|------|
# MAGIC | **정형 데이터** | UCI AI4I 2020 Predictive Maintenance Dataset (10,000건) |
# MAGIC | **비정형 데이터** | MVTec AD 산업용 이상탐지 벤치마크 이미지 |
# MAGIC | **정형 모델** | XGBoost — 설비 고장 예측 (이진 분류) |
# MAGIC | **비정형 모델** | Anomalib PatchCore — 제품 표면 이상탐지 |
# MAGIC | **운영 환경** | 주 1회 재학습, 일 4회 배치 예측 |
# MAGIC | **개발 환경** | 일 4회 재학습 |
# MAGIC | **Agent** | Trigger에 따라 MLOps Tool의 학습/예측 자동 수행 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Databricks MLOps 핵심 기능 활용
# MAGIC
# MAGIC 본 데모에서 활용되는 Databricks 플랫폼의 핵심 MLOps 기능은 다음과 같습니다:
# MAGIC
# MAGIC ### 1. 데이터 관리 & 거버넌스
# MAGIC - **Unity Catalog**: 데이터, 피처, 모델의 통합 거버넌스
# MAGIC - **Delta Lake**: ACID 트랜잭션 기반의 신뢰할 수 있는 데이터 레이크
# MAGIC - **Feature Store**: 피처의 중앙 관리, 공유 및 재사용
# MAGIC - **Volumes**: 비정형 데이터(이미지) 관리
# MAGIC
# MAGIC ### 2. 실험 & 모델 학습
# MAGIC - **MLflow Experiment Tracking**: 실험 파라미터, 메트릭, 아티팩트 자동 추적
# MAGIC - **MLflow Autolog**: 코드 변경 없이 자동 로깅
# MAGIC - **Data Lineage**: 학습 데이터 → 모델 간 계보 추적
# MAGIC
# MAGIC ### 3. 모델 관리 & 배포
# MAGIC - **Unity Catalog Model Registry**: 모델 버전 관리 및 에일리어스(Alias)
# MAGIC - **Champion/Challenger 패턴**: 안전한 모델 교체 프로세스
# MAGIC - **Model Serving**: 실시간 추론 엔드포인트
# MAGIC - **Batch Inference**: PySpark UDF를 통한 대규모 배치 예측
# MAGIC
# MAGIC ### 4. 모니터링 & 자동화
# MAGIC - **Lakehouse Monitoring**: 데이터 드리프트 및 모델 성능 모니터링
# MAGIC - **Databricks Workflows (Jobs)**: 학습/추론 파이프라인 스케줄링
# MAGIC - **AI Agent**: Trigger 기반 자동 학습/예측 오케스트레이션
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 데모 구성
# MAGIC
# MAGIC ```
# MAGIC ┌─────────────────────────────────────────────────────────────────────┐
# MAGIC │                    LG Innotek MLOps PoC 아키텍처                      │
# MAGIC ├─────────────────────────────────────────────────────────────────────┤
# MAGIC │                                                                     │
# MAGIC │  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
# MAGIC │  │  정형 데이터   │    │ 비정형 데이터  │    │   Unity Catalog      │  │
# MAGIC │  │  (AI4I 2020)  │    │ (MVTec AD)   │    │   (거버넌스/계보)     │  │
# MAGIC │  └──────┬───────┘    └──────┬───────┘    └──────────────────────┘  │
# MAGIC │         │                   │                                       │
# MAGIC │         ▼                   ▼                                       │
# MAGIC │  ┌──────────────┐    ┌──────────────┐                              │
# MAGIC │  │ Feature Eng.  │    │ Image Proc.  │                              │
# MAGIC │  │ (Spark/Pandas)│    │ (Anomalib)   │                              │
# MAGIC │  └──────┬───────┘    └──────┬───────┘                              │
# MAGIC │         │                   │                                       │
# MAGIC │         ▼                   ▼                                       │
# MAGIC │  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
# MAGIC │  │ XGBoost Train │    │ PatchCore    │    │   MLflow Tracking    │  │
# MAGIC │  │ + SHAP        │    │ Train        │    │   (실험/메트릭/모델)  │  │
# MAGIC │  └──────┬───────┘    └──────┬───────┘    └──────────────────────┘  │
# MAGIC │         │                   │                                       │
# MAGIC │         ▼                   ▼                                       │
# MAGIC │  ┌─────────────────────────────────────┐                           │
# MAGIC │  │     UC Model Registry                │                           │
# MAGIC │  │  (Champion / Challenger 에일리어스)    │                           │
# MAGIC │  └──────────────┬──────────────────────┘                           │
# MAGIC │                 │                                                   │
# MAGIC │         ┌───────┴───────┐                                          │
# MAGIC │         ▼               ▼                                          │
# MAGIC │  ┌──────────────┐ ┌──────────────┐    ┌──────────────────────┐    │
# MAGIC │  │ Batch Predict │ │ Model Serve  │    │  Lakehouse Monitor   │    │
# MAGIC │  │ (일 4회)      │ │ (실시간)     │    │  (드리프트 탐지)      │    │
# MAGIC │  └──────────────┘ └──────────────┘    └──────────────────────┘    │
# MAGIC │                                                                     │
# MAGIC │  ┌─────────────────────────────────────────────────────────────┐   │
# MAGIC │  │              MLOps Agent (오케스트레이션)                      │   │
# MAGIC │  │     Trigger → 학습/예측/모니터링 자동 수행                     │   │
# MAGIC │  └─────────────────────────────────────────────────────────────┘   │
# MAGIC │                                                                     │
# MAGIC │  ┌─────────────────────────────────────────────────────────────┐   │
# MAGIC │  │              Databricks Workflows (Jobs)                     │   │
# MAGIC │  │     운영: 주1회 재학습 + 일4회 배치예측                        │   │
# MAGIC │  │     개발: 일4회 재학습                                        │   │
# MAGIC │  └─────────────────────────────────────────────────────────────┘   │
# MAGIC └─────────────────────────────────────────────────────────────────────┘
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 노트북 목차
# MAGIC
# MAGIC | # | 노트북 | 설명 | Databricks 기능 |
# MAGIC |---|--------|------|-----------------|
# MAGIC | 01 | [Overview (본 노트북)]($./01_overview) | 전체 아키텍처 및 시나리오 소개 | — |
# MAGIC | 02 | [피처 엔지니어링]($./02_structured_feature_engineering) | AI4I 2020 데이터 탐색 및 피처 생성 | Delta Lake, Feature Store, Unity Catalog |
# MAGIC | 03 | [모델 학습]($./03_structured_model_training) | XGBoost 학습, HPO, SHAP 해석 | MLflow Tracking, Autolog |
# MAGIC | 03a | [ML 트렌드]($./03a_ml_trends_and_techniques) | 최신 ML 기술 트렌드 가이드 | — |
# MAGIC | 03b | [멀티 알고리즘]($./03b_multi_algorithm_comparison) | XGBoost/LightGBM/CatBoost/RF 비교 | MLflow 실험 비교 |
# MAGIC | 03c | [고급 기법]($./03c_advanced_techniques) | SMOTE, Optuna, Stacking, AutoML | Databricks AutoML |
# MAGIC | 03d | [재학습 전략]($./03d_retraining_strategies) | Incremental, Continual, Online, RL, Active Learning | Streaming, Delta Time Travel |
# MAGIC | 04 | [모델 등록]($./04_model_registration_uc) | UC 모델 레지스트리 등록 및 에일리어스 | Unity Catalog Models, Lineage |
# MAGIC | 05 | [챌린저 검증]($./05_challenger_validation) | Champion-Challenger 비교 검증 | Model Validation, A/B Testing |
# MAGIC | 06 | [배치 추론]($./06_batch_inference) | PySpark UDF 기반 대규모 배치 예측 | Spark UDF, Delta Lake |
# MAGIC | 07 | [비정형 이상탐지]($./07_unstructured_anomaly_detection) | MVTec AD + Anomalib PatchCore | Volumes, GPU Cluster, MLflow |
# MAGIC | 08 | [모델 모니터링]($./08_model_monitoring) | 데이터 드리프트 및 성능 모니터링 | Lakehouse Monitoring |
# MAGIC | 09 | [MLOps Agent]($./09_mlops_agent) | Agent 기반 학습/예측 오케스트레이션 | AI Agent, Tool Use |
# MAGIC | 10 | [Job 스케줄링]($./10_job_scheduling) | 운영/개발 환경 워크플로우 설정 | Databricks Workflows |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 정형 데이터: AI4I 2020 Predictive Maintenance Dataset
# MAGIC
# MAGIC | 항목 | 상세 |
# MAGIC |------|------|
# MAGIC | **데이터** | UCI AI4I 2020 — 실제 산업 데이터 기반 합성 데이터셋 |
# MAGIC | **규모** | 10,000건 |
# MAGIC | **입력 피처** | 공기 온도(K), 공정 온도(K), 회전속도(rpm), 토크(Nm), 공구 마모(min), 제품 타입 |
# MAGIC | **출력** | 고장 발생 여부 (이진 분류), 고장 유형 확률, 위험 점수 |
# MAGIC | **모델** | XGBoost |
# MAGIC | **해석** | SHAP 기반 피처 중요도 및 개별 예측 해석 |
# MAGIC
# MAGIC ## 비정형 데이터: MVTec AD
# MAGIC
# MAGIC | 항목 | 상세 |
# MAGIC |------|------|
# MAGIC | **데이터** | MVTec AD — Industrial Inspection 벤치마크 |
# MAGIC | **규모** | 15개 카테고리, 5,000장 이상 고해상도 이미지 |
# MAGIC | **구조** | 정상 이미지로 학습, 이상 이미지로 테스트 |
# MAGIC | **입력** | 제품 표면 이미지 |
# MAGIC | **출력** | 정상/이상, 이상 점수, 이상 위치 heatmap |
# MAGIC | **모델** | Anomalib PatchCore (또는 Reverse Distillation) |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 시작하기
# MAGIC
# MAGIC 다음 단계: [피처 엔지니어링]($./02_structured_feature_engineering)으로 진행하여 AI4I 2020 데이터를 탐색하고 피처를 준비합니다.
