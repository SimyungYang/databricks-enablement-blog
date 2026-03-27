# Databricks notebook source
# MAGIC %md
# MAGIC # 예지보전 ML 최신 기술 트렌드 및 적용 가이드
# MAGIC
# MAGIC 본 노트북에서는 LG Innotek의 **예지보전(Predictive Maintenance)** 및 **비전 이상탐지** 모델에
# MAGIC 적용할 수 있는 **최신 ML 기술 트렌드**를 정리하고, 각 기법의 원리와 적용 방법을 상세히 설명합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 목차
# MAGIC 1. [정형 데이터 — 최신 학습 기법](#1-정형-데이터-최신-학습-기법)
# MAGIC 2. [비정형 데이터 — 최신 이상탐지 기법](#2-비정형-데이터-최신-이상탐지-기법)
# MAGIC 3. [MLOps 자동화 — 최신 트렌드](#3-mlops-자동화-최신-트렌드)
# MAGIC 4. [적용 권장 사항](#4-적용-권장-사항)

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 1. 정형 데이터 — 최신 학습 기법
# MAGIC
# MAGIC ## 1.1 Gradient Boosting 앙상블 계열 발전
# MAGIC
# MAGIC | 알고리즘 | 특징 | 장점 | 적용 시나리오 |
# MAGIC |----------|------|------|-------------|
# MAGIC | **XGBoost** | 정규화된 부스팅, 병렬 학습 | 안정적 성능, 산업 표준 | 범용 분류/회귀 |
# MAGIC | **LightGBM** | Leaf-wise 성장, GOSS/EFB | 대규모 데이터에서 빠른 학습 | 고차원 피처, 대용량 데이터 |
# MAGIC | **CatBoost** | 범주형 자동 인코딩, Ordered Boosting | 범주형 피처 처리 우수, 과적합 방지 | 범주형 다수 포함 데이터 |
# MAGIC | **HistGradientBoosting** | scikit-learn 내장, 히스토그램 기반 | 별도 설치 불필요, 결측치 자동 처리 | 빠른 프로토타이핑 |
# MAGIC
# MAGIC ### 왜 멀티 알고리즘 비교가 중요한가?
# MAGIC - 데이터 특성에 따라 **최적 알고리즘이 다름** (No Free Lunch Theorem)
# MAGIC - AI4I 2020 데이터는 **불균형** + **연속형/범주형 혼합** → CatBoost가 유리할 수 있음
# MAGIC - 제조 데이터는 **시계열 패턴** → LightGBM의 빠른 반복 학습이 유리
# MAGIC - MLflow로 **동일 조건 비교**가 가능 → 공정한 알고리즘 선택
# MAGIC
# MAGIC > **실습**: [03b_multi_algorithm_comparison]($./03b_multi_algorithm_comparison) 노트북에서 4개 알고리즘을 동시 비교합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.2 불균형 데이터 처리 (Imbalanced Learning)
# MAGIC
# MAGIC 제조 예지보전 데이터는 **극심한 클래스 불균형**이 특징입니다 (고장률 ~3.4%).
# MAGIC
# MAGIC ### 최신 기법들:
# MAGIC
# MAGIC | 기법 | 원리 | 장점 | 단점 |
# MAGIC |------|------|------|------|
# MAGIC | **SMOTE** (Synthetic Minority Over-sampling) | 소수 클래스 샘플 사이에 합성 데이터 생성 | 간단, 효과적 | 노이즈 생성 가능 |
# MAGIC | **ADASYN** (Adaptive Synthetic) | 학습하기 어려운 영역에 더 많은 합성 데이터 생성 | SMOTE보다 적응적 | 경계 과적합 |
# MAGIC | **BorderlineSMOTE** | 결정 경계 근처의 소수 클래스만 오버샘플링 | 노이즈 감소 | 파라미터 민감 |
# MAGIC | **SMOTE-ENN** | SMOTE + Edited Nearest Neighbors | 오버샘플링 + 노이즈 제거 | 계산 비용 높음 |
# MAGIC | **class_weight / scale_pos_weight** | 모델 내부 가중치 조정 | 데이터 변형 없음 | 효과 제한적일 수 있음 |
# MAGIC | **Focal Loss** | 쉬운 샘플의 가중치를 줄여 어려운 샘플에 집중 | 딥러닝에 효과적 | 하이퍼파라미터 튜닝 필요 |
# MAGIC
# MAGIC ### AI4I 2020 데이터에 권장:
# MAGIC ```
# MAGIC 1순위: SMOTE-ENN (오버샘플링 + 노이즈 제거)
# MAGIC 2순위: scale_pos_weight (모델 내장, 가장 간단)
# MAGIC 3순위: BorderlineSMOTE (경계 중심 오버샘플링)
# MAGIC ```
# MAGIC
# MAGIC > **실습**: [03c_advanced_techniques]($./03c_advanced_techniques) 노트북에서 SMOTE 계열 기법을 적용합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.3 하이퍼파라미터 최적화 (HPO) 최신 기법
# MAGIC
# MAGIC | 기법 | 원리 | 장점 | Databricks 지원 |
# MAGIC |------|------|------|----------------|
# MAGIC | **Grid Search** | 모든 조합 탐색 | 확실한 최적화 | scikit-learn 내장 |
# MAGIC | **Random Search** | 랜덤 샘플링 | 효율적 | scikit-learn 내장 |
# MAGIC | **Bayesian Optimization (Optuna)** | 이전 결과 기반 다음 탐색점 선택 | 적은 시행으로 최적화 | MLflow 자동 연동 |
# MAGIC | **Hyperopt (TPE)** | Tree of Parzen Estimators | Databricks 최적화됨 | SparkTrials 분산 지원 |
# MAGIC | **FLAML** | Fast Lightweight AutoML | 초고속 AutoML | 자동 알고리즘 선택 |
# MAGIC
# MAGIC ### Optuna vs Hyperopt
# MAGIC - **Optuna**: API가 직관적, 시각화 내장, Pruning 지원 → **권장**
# MAGIC - **Hyperopt + SparkTrials**: Databricks에서 **분산 HPO** 가능 → 대규모 탐색 시 유리
# MAGIC
# MAGIC ```python
# MAGIC # Optuna 예시
# MAGIC import optuna
# MAGIC
# MAGIC def objective(trial):
# MAGIC     params = {
# MAGIC         "max_depth": trial.suggest_int("max_depth", 3, 10),
# MAGIC         "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
# MAGIC         "subsample": trial.suggest_float("subsample", 0.6, 1.0),
# MAGIC     }
# MAGIC     # 모델 학습 및 F1 반환
# MAGIC     return train_and_evaluate(params)
# MAGIC
# MAGIC study = optuna.create_study(direction="maximize")
# MAGIC study.optimize(objective, n_trials=50)
# MAGIC ```
# MAGIC
# MAGIC > **실습**: [03c_advanced_techniques]($./03c_advanced_techniques) 노트북에서 Optuna HPO를 적용합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.4 AutoML (자동 머신러닝)
# MAGIC
# MAGIC ### Databricks AutoML
# MAGIC - **코드 없이** 최적 모델 자동 탐색
# MAGIC - 여러 알고리즘 + HPO + 피처 엔지니어링을 자동 수행
# MAGIC - 결과를 **MLflow 실험**으로 자동 기록
# MAGIC - **생성된 노트북**을 수정하여 커스터마이징 가능
# MAGIC
# MAGIC ```python
# MAGIC from databricks import automl
# MAGIC
# MAGIC summary = automl.classify(
# MAGIC     dataset=spark.table("lgit_pm_training"),
# MAGIC     target_col="machine_failure",
# MAGIC     primary_metric="f1",
# MAGIC     timeout_minutes=30,
# MAGIC )
# MAGIC ```
# MAGIC
# MAGIC ### 장점:
# MAGIC - 빠른 프로토타이핑 (30분 내 최적 모델)
# MAGIC - 데이터 사이언티스트가 없어도 시작 가능
# MAGIC - 생성된 노트북으로 학습 과정 투명하게 확인
# MAGIC
# MAGIC > **실습**: [03c_advanced_techniques]($./03c_advanced_techniques) 노트북에서 AutoML을 실행합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.5 앙상블 기법 (Ensemble Methods)
# MAGIC
# MAGIC ### Stacking (스태킹)
# MAGIC - 여러 기본 모델(Base Learner)의 예측을 **메타 모델**이 결합
# MAGIC - 단일 알고리즘보다 **일관된 성능 향상**
# MAGIC
# MAGIC ```
# MAGIC ┌─────────┐  ┌──────────┐  ┌──────────┐
# MAGIC │ XGBoost │  │ LightGBM │  │ CatBoost │   ← Base Learners
# MAGIC └────┬────┘  └────┬─────┘  └────┬─────┘
# MAGIC      │            │             │
# MAGIC      └────────────┼─────────────┘
# MAGIC                   ▼
# MAGIC           ┌───────────────┐
# MAGIC           │ Logistic Reg  │              ← Meta Learner
# MAGIC           └───────────────┘
# MAGIC ```
# MAGIC
# MAGIC ### Weighted Voting (가중 투표)
# MAGIC - 각 모델의 성능에 비례하여 가중 평균
# MAGIC - Stacking보다 단순하지만 효과적
# MAGIC
# MAGIC > **실습**: [03c_advanced_techniques]($./03c_advanced_techniques) 노트북에서 Stacking을 구현합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.6 피처 선택 (Feature Selection) 최신 기법
# MAGIC
# MAGIC | 기법 | 원리 | 적용 시나리오 |
# MAGIC |------|------|-------------|
# MAGIC | **Boruta** | 랜덤 포레스트 기반 통계적 피처 중요도 | 중요 피처 자동 선택 |
# MAGIC | **Recursive Feature Elimination (RFE)** | 반복적으로 가장 약한 피처 제거 | 피처 수 줄이기 |
# MAGIC | **SHAP-based Selection** | SHAP 값 기반 피처 선택 | 해석 가능한 피처 선택 |
# MAGIC | **Mutual Information** | 정보 이론 기반 피처 관련성 | 비선형 관계 탐지 |

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 2. 비정형 데이터 — 최신 이상탐지 기법
# MAGIC
# MAGIC ## 2.1 Anomalib 지원 모델 비교
# MAGIC
# MAGIC | 모델 | 원리 | AUROC (MVTec) | 추론 속도 | 메모리 |
# MAGIC |------|------|--------------|----------|--------|
# MAGIC | **PatchCore** | 사전학습 CNN의 패치 피처 + Core-set 메모리 뱅크 | **99.1%** | 보통 | 높음 |
# MAGIC | **Reverse Distillation** | Teacher-Student 구조의 역방향 지식 증류 | 98.5% | **빠름** | 낮음 |
# MAGIC | **EfficientAD** | 경량 Teacher-Student + Autoencoder | 98.8% | **가장 빠름** | **가장 낮음** |
# MAGIC | **PADIM** | 사전학습 CNN + 다변량 가우시안 | 97.9% | 빠름 | 보통 |
# MAGIC | **FastFlow** | 정규화 흐름 (Normalizing Flows) | 98.0% | 빠름 | 보통 |
# MAGIC | **GANomaly** | GAN 기반 생성 모델 | 96.0% | 보통 | 보통 |
# MAGIC
# MAGIC ### 제조 현장 권장:
# MAGIC ```
# MAGIC 정확도 우선 → PatchCore
# MAGIC 속도/비용 우선 → EfficientAD 또는 Reverse Distillation
# MAGIC 실시간 추론 → EfficientAD (엣지 디바이스 가능)
# MAGIC ```
# MAGIC
# MAGIC ## 2.2 최신 트렌드: Foundation Model 기반 이상탐지
# MAGIC
# MAGIC - **WinCLIP**: CLIP 기반 Zero-shot 이상탐지 (학습 데이터 불필요)
# MAGIC - **AnomalyCLIP**: 프롬프트 기반 이상탐지
# MAGIC - **SAA+** (Segment Any Anomaly): SAM + CLIP 결합
# MAGIC
# MAGIC → 데이터가 부족한 **초기 PoC 단계**에서 활용 가능

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 3. MLOps 자동화 — 최신 트렌드
# MAGIC
# MAGIC ## 3.1 Feature Store 발전
# MAGIC
# MAGIC | 기능 | 설명 | Databricks 지원 |
# MAGIC |------|------|----------------|
# MAGIC | **Offline Feature Store** | 배치 학습/추론용 피처 관리 | Unity Catalog 테이블 |
# MAGIC | **Online Feature Store** | 실시간 서빙용 피처 | Online Tables |
# MAGIC | **Feature Function** | 동적 피처 계산 | Python UDF |
# MAGIC | **Point-in-Time Lookups** | 시점 기반 피처 조인 (시계열) | Feature Engineering Client |
# MAGIC
# MAGIC ## 3.2 Model Monitoring 발전
# MAGIC
# MAGIC | 기능 | 설명 |
# MAGIC |------|------|
# MAGIC | **Lakehouse Monitoring** | 자동 드리프트 탐지 + 대시보드 |
# MAGIC | **Inference Tables** | 서빙 엔드포인트의 입출력 자동 로깅 |
# MAGIC | **Custom Metrics** | 비즈니스 KPI 기반 커스텀 모니터링 |
# MAGIC | **Alerts** | 임계값 초과 시 자동 알림 |
# MAGIC
# MAGIC ## 3.3 LLMOps / Agent-based MLOps
# MAGIC
# MAGIC | 기법 | 설명 | 적용 |
# MAGIC |------|------|------|
# MAGIC | **MLOps Agent** | LLM이 MLOps 도구를 호출하여 자동 운영 | 드리프트 → 재학습 자동화 |
# MAGIC | **Compound AI Systems** | 여러 모델을 Agent가 조합 | 정형 + 비정형 통합 판단 |
# MAGIC | **MLflow Tracing** | LLM/Agent 호출 추적 | Agent 행동 디버깅 |

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 4. 적용 권장 사항
# MAGIC
# MAGIC ## LG Innotek PoC에 즉시 적용 가능한 기법 (우선순위순)
# MAGIC
# MAGIC | 우선순위 | 기법 | 적용 대상 | 기대 효과 | 난이도 |
# MAGIC |---------|------|----------|----------|--------|
# MAGIC | 1 | **멀티 알고리즘 비교** | 정형 모델 | 최적 알고리즘 선택 | 낮음 |
# MAGIC | 2 | **SMOTE-ENN** 불균형 처리 | 정형 모델 | 소수 클래스 성능 향상 | 낮음 |
# MAGIC | 3 | **Optuna HPO** | 정형 모델 | 하이퍼파라미터 최적화 | 중간 |
# MAGIC | 4 | **Stacking 앙상블** | 정형 모델 | 안정적 성능 향상 | 중간 |
# MAGIC | 5 | **Databricks AutoML** | 정형 모델 | 빠른 베이스라인 확보 | 낮음 |
# MAGIC | 6 | **PatchCore + EfficientAD** | 비정형 모델 | 정확도/속도 비교 | 중간 |
# MAGIC | 7 | **Lakehouse Monitoring** | 운영 환경 | 자동 드리프트 탐지 | 낮음 |
# MAGIC | 8 | **MLOps Agent** | 운영 자동화 | 무인 운영 실현 | 높음 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 다음 실습 노트북
# MAGIC - [03b: 멀티 알고리즘 비교 학습]($./03b_multi_algorithm_comparison) — XGBoost, LightGBM, CatBoost, RF 동시 비교
# MAGIC - [03c: 고급 기법 적용]($./03c_advanced_techniques) — SMOTE, Optuna, Stacking, AutoML
