# Databricks notebook source
# MAGIC %md
# MAGIC # LG Innotek MLOps PoC: 엔드투엔드(End-to-End) 예지보전 & 이상탐지
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## MLOps란 무엇이고, 왜 제조업에 중요한가?
# MAGIC
# MAGIC **MLOps(Machine Learning Operations)** 란 머신러닝 모델을 개발(Dev)하고, 운영(Ops)하고, 지속적으로 개선하는 전체 생명주기를 체계적으로 관리하는 방법론입니다.
# MAGIC
# MAGIC 제조업에 비유하면 이렇게 이해할 수 있습니다:
# MAGIC
# MAGIC | 제조 현장 개념 | MLOps 대응 개념 | 설명 |
# MAGIC |---------------|---------------|------|
# MAGIC | **제품 설계** | 모델 개발 (Training) | 센서 데이터를 분석하여 고장 예측 모델을 만드는 과정 |
# MAGIC | **양산 이관** | 모델 배포 (Deployment) | 개발된 모델을 실제 운영 환경에 적용하는 과정 |
# MAGIC | **품질 검사 (SPC)** | 모델 모니터링 (Monitoring) | 모델이 정확하게 예측하고 있는지 지속적으로 확인하는 과정 |
# MAGIC | **공정 개선** | 모델 재학습 (Retraining) | 새로운 데이터로 모델 성능을 향상시키는 과정 |
# MAGIC | **MES 자동화** | 파이프라인 자동화 (Automation) | 위의 모든 과정을 사람 개입 없이 자동으로 실행하는 것 |
# MAGIC
# MAGIC ### ML은 어떻게 발전해왔나?
# MAGIC
# MAGIC ```
# MAGIC [1단계] 규칙 기반 (Rule-based)      → "토크 40Nm 이상이면 경고" (사람이 직접 기준 설정)
# MAGIC [2단계] 통계 모델 (Statistical)      → "회귀분석으로 고장 확률 계산" (데이터에서 패턴 추출)
# MAGIC [3단계] 머신러닝 (Machine Learning)  → "XGBoost가 100개 변수 조합으로 예측" (복잡한 패턴 자동 발견)
# MAGIC [4단계] 딥러닝 (Deep Learning)       → "이미지에서 미세 결함 자동 탐지" (비정형 데이터 처리)
# MAGIC [5단계] MLOps                        → "모델이 스스로 성능을 모니터링하고 재학습" (운영 자동화) ← 우리가 오늘 할 것
# MAGIC ```
# MAGIC
# MAGIC > **핵심 메시지**: AI/ML 모델은 한 번 만들면 끝이 아닙니다. 공장의 설비가 지속적인 유지보수가 필요하듯, AI 모델도 **지속적인 관리와 개선** 이 필요합니다. 이것이 바로 MLOps입니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 오늘 무엇을 배우나요? (학습 목표)
# MAGIC
# MAGIC 이 교육을 마치면 다음을 이해하고 직접 실행할 수 있게 됩니다:
# MAGIC
# MAGIC 1. **데이터 준비**: 센서 데이터를 ML 모델이 이해할 수 있는 형태로 변환하기 (피처 엔지니어링)
# MAGIC 2. **모델 학습**: XGBoost로 설비 고장을 예측하는 모델 만들기
# MAGIC 3. **모델 관리**: 학습된 모델을 버전 관리하고 안전하게 배포하기
# MAGIC 4. **배치 추론**: 대량의 센서 데이터에 대해 한꺼번에 예측 수행하기
# MAGIC 5. **비전 AI**: 제품 이미지에서 결함을 자동 탐지하기
# MAGIC 6. **모니터링**: 모델 성능이 떨어지는 것을 자동으로 감지하기
# MAGIC 7. **자동화**: 위의 모든 과정을 스케줄에 따라 자동 실행하기
# MAGIC
# MAGIC > **비유**: 오늘 우리는 "AI 품질관리 시스템"의 설계도를 그리고, 각 부품을 조립하고, 자동화 라인까지 완성합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 왜 Databricks인가? (기존 도구와의 비교)
# MAGIC
# MAGIC 기존에 데이터 분석을 해보셨다면 Jupyter Notebook이나 Excel을 사용해보셨을 수 있습니다. Databricks가 왜 다른지 비교해보겠습니다:
# MAGIC
# MAGIC | 항목 | 기존 방식 (Jupyter + 수작업) | Databricks Lakehouse |
# MAGIC |------|---------------------------|---------------------|
# MAGIC | **데이터 저장** | CSV 파일, 개인 PC | Delta Lake (버전 관리, 공유, 보안) |
# MAGIC | **실험 기록** | 수기 메모, 스프레드시트 | MLflow (자동 기록, 비교, 재현) |
# MAGIC | **모델 관리** | 폴더에 pickle 파일 저장 | Unity Catalog (버전, 권한, 계보 추적) |
# MAGIC | **대용량 처리** | 메모리 부족으로 실패 | Spark 분산 처리 (수십TB도 가능) |
# MAGIC | **협업** | 파일 주고받기 | 같은 플랫폼에서 동시 작업 |
# MAGIC | **자동화** | 크론탭 + 스크립트 수작업 | Workflows (GUI로 스케줄 설정) |
# MAGIC | **모니터링** | 없음 (문제 발생 후 인지) | Data Quality Monitoring(구 Data Quality Monitoring) (자동 알림) |
# MAGIC | **보안/거버넌스** | 없음 | Unity Catalog (세밀한 권한 제어) |
# MAGIC
# MAGIC > **제조업 비유**: Jupyter Notebook은 "수공구로 하나씩 가공하는 것"이고, Databricks는 "자동화된 스마트 공장 라인"입니다. 소량 시제품은 수공구로도 되지만, 양산에는 자동화 라인이 필수입니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 개요
# MAGIC
# MAGIC 본 데모는 **Databricks Lakehouse 플랫폼**을 활용하여 제조 현장의 **예지보전(Predictive Maintenance, 설비가 고장나기 전에 미리 예측하여 정비하는 기술)**및 **비전 기반 이상탐지(Anomaly Detection, 카메라 이미지로 불량품을 자동 식별하는 기술)** 를 위한 완전한 MLOps 파이프라인을 구축하는 과정을 보여줍니다.
# MAGIC
# MAGIC 이 파이프라인(Pipeline, 데이터가 순서대로 흘러가며 처리되는 자동화된 작업 흐름)은 데이터 수집부터 모델 학습, 배포, 모니터링, 재학습까지 **사람의 개입 없이 자동으로 동작** 하도록 설계됩니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## PoC 시나리오
# MAGIC
# MAGIC > **PoC(Proof of Concept)** 란 "개념 검증"이라는 뜻으로, 본격적인 시스템 구축 전에 핵심 기능이 실제로 동작하는지 작은 규모로 먼저 확인하는 과정입니다. 제조업에서 양산 전 파일럿 라인(Pilot Line)을 운영하는 것과 같습니다.
# MAGIC
# MAGIC | 구분 | 상세 | 제조 현장 대응 |
# MAGIC |------|------|--------------|
# MAGIC | **정형 데이터** | UCI AI4I 2020 Predictive Maintenance Dataset (10,000건) | 설비 센서에서 수집되는 온도, 회전수, 토크 등의 숫자 데이터 |
# MAGIC | **비정형 데이터** | MVTec AD 산업용 이상탐지 벤치마크 이미지 | AOI(자동광학검사), 카메라로 촬영한 제품 표면 이미지 |
# MAGIC | **정형 모델** | XGBoost -- 설비 고장 예측 (이진 분류) | "이 설비가 고장날 것인가 / 아닌가"를 예측 |
# MAGIC | **비정형 모델** | Anomalib PatchCore -- 제품 표면 이상탐지 | "이 제품 이미지에서 결함이 있는가 / 없는가"를 판별 |
# MAGIC | **운영 환경** | 주 1회 재학습, 일 4회 배치 예측 | 실제 생산 라인에 적용되는 안정적 환경 |
# MAGIC | **개발 환경** | 일 4회 재학습 | 새로운 모델/기법을 실험하는 테스트 환경 |
# MAGIC | **Agent** | Trigger에 따라 MLOps Tool의 학습/예측 자동 수행 | 자동화된 공장 관리 시스템(MES)이 상황에 따라 판단하고 실행하는 것과 유사 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Databricks MLOps 핵심 기능 활용
# MAGIC
# MAGIC 본 데모에서 활용되는 Databricks 플랫폼의 핵심 MLOps 기능은 다음과 같습니다. 각 기능을 제조 현장에 비유하여 설명합니다:
# MAGIC
# MAGIC ### 1. 데이터 관리 & 거버넌스 (Governance, 데이터 통제/관리 체계)
# MAGIC - **Unity Catalog (통합 카탈로그)**: 데이터, 피처, 모델의 통합 거버넌스. 공장으로 비유하면 **자재관리시스템(MRP)** 과 같습니다. 모든 데이터가 어디에 있고, 누가 접근할 수 있는지, 어디서 왔는지를 중앙에서 관리합니다.
# MAGIC - **Delta Lake (델타 레이크)**: ACID 트랜잭션(데이터의 무결성을 보장하는 처리 방식) 기반의 신뢰할 수 있는 데이터 레이크. 공장의 **ERP 시스템** 처럼 데이터의 변경 이력을 모두 추적하고, 과거 시점으로 되돌릴 수 있습니다(Time Travel 기능).
# MAGIC - **Feature Store (피처 저장소)**: 피처(Feature, ML 모델의 입력 변수)의 중앙 관리, 공유 및 재사용. 공장에서 **표준 부품 라이브러리** 를 관리하는 것과 같습니다. 한 번 만든 피처를 여러 모델에서 재사용할 수 있습니다.
# MAGIC - **Volumes (볼륨)**: 비정형 데이터(이미지, 비디오 등) 관리. 공장의 **AOI(자동광학검사) 이미지 서버** 와 같은 역할입니다.
# MAGIC
# MAGIC ### 2. 실험 & 모델 학습
# MAGIC - **MLflow Experiment Tracking**: 실험 파라미터(Parameter, 모델 학습 시 설정하는 값), 메트릭(Metric, 모델 성능 측정 지표), 아티팩트(Artifact, 학습된 모델 파일 등) 자동 추적. 공장에서 **실험일지/양산 시험 성적서** 를 자동으로 작성하는 것과 같습니다.
# MAGIC - **MLflow Autolog**: 코드 변경 없이 자동 로깅. 모든 실험 결과가 자동으로 기록되므로, "어떤 설정으로 학습했더니 정확도가 몇 %였다"를 나중에 정확히 재현할 수 있습니다.
# MAGIC - **Data Lineage (데이터 계보)**: 학습 데이터 → 모델 간 계보 추적. 제품의 **로트(Lot) 추적** 과 같습니다. "이 모델은 어떤 데이터로 학습되었는가?"를 추적할 수 있습니다.
# MAGIC
# MAGIC ### 3. 모델 관리 & 배포
# MAGIC - **Unity Catalog Model Registry (모델 등록소)**: 모델 버전 관리 및 에일리어스(Alias, 별칭). 소프트웨어의 **버전 관리 시스템** 과 같습니다. 모델 v1, v2, v3를 관리하고, 현재 운영 중인 모델에 "Champion"이라는 별칭을 부여합니다.
# MAGIC - **Champion/Challenger 패턴**: 안전한 모델 교체 프로세스. 공장에서 **신규 설비를 도입할 때 기존 설비와 병행 운전(Parallel Run)** 하여 검증하는 것과 같습니다. 새 모델(Challenger)이 기존 모델(Champion)보다 나은 성능을 증명해야만 교체됩니다.
# MAGIC - **Model Serving**: 실시간 추론(Inference, 모델이 새로운 데이터에 대해 예측하는 것) 엔드포인트. API로 호출하면 즉시 예측 결과를 반환합니다.
# MAGIC - **Batch Inference (배치 추론)**: PySpark UDF를 통한 대규모 배치 예측. 수천~수백만 건의 데이터를 한꺼번에 예측합니다.
# MAGIC
# MAGIC ### 4. 모니터링 & 자동화
# MAGIC - **Data Quality Monitoring**: 데이터 드리프트(Drift, 시간이 지남에 따라 데이터의 분포가 변하는 현상) 및 모델 성능 모니터링. 공장의 **SPC(통계적 공정 관리)** 와 같은 역할입니다. 관리도(Control Chart)처럼 모델 성능이 관리 한계를 벗어나면 자동으로 알림을 보냅니다.
# MAGIC - **Lakeflow Jobs**: 학습/추론 파이프라인 스케줄링. 공장의 **MES(제조실행시스템)** 와 같습니다. 정해진 스케줄에 따라 자동으로 작업을 실행합니다.
# MAGIC - **AI Agent**: Trigger(특정 조건/이벤트) 기반 자동 학습/예측 오케스트레이션(Orchestration, 여러 작업을 조율하여 실행하는 것). 공장의 **자동 설비 관리 시스템** 이 이상 징후를 감지하고 스스로 조치하는 것과 유사합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 데모 구성
# MAGIC
# MAGIC ### LG Innotek MLOps PoC Architecture
# MAGIC
# MAGIC 아래 표는 이 PoC의 전체 아키텍처를 8단계로 정리한 것입니다. 각 단계가 무엇을 하고, 왜 필요한지를 함께 설명합니다:
# MAGIC
# MAGIC | 단계 | 정형 데이터 (AI4I 2020) | 비정형 데이터 (MVTec AD) | Databricks 기능 | 왜 필요한가? |
# MAGIC |------|----------------------|------------------------|----------------|------------|
# MAGIC | **1. 데이터** | 센서값 10,000건 | 제품 이미지 5,000장+ | Unity Catalog (거버넌스) | 원재료(데이터)가 없으면 AI 모델을 만들 수 없습니다 |
# MAGIC | **2. 피처** | Spark/Pandas FE | Anomalib 전처리 | Feature Store, Delta Lake | 원재료를 가공(피처 엔지니어링)해야 모델이 학습할 수 있습니다 |
# MAGIC | **3. 학습** | XGBoost + SHAP | PatchCore | MLflow Tracking (자동 기록) | 가공된 데이터로 패턴을 학습합니다 (= AI 모델 생성) |
# MAGIC | **4. 등록** | UC Model Registry | UC Model Registry | Champion/Challenger Alias | 학습된 모델을 중앙 저장소에 등록하고 버전을 관리합니다 |
# MAGIC | **5. 검증** | 4단계 자동 검증 | 이상 점수 평가 | mlflow.evaluate() | 새 모델이 기존 모델보다 나은지 검증합니다 (품질 검사) |
# MAGIC | **6. 추론** | Spark UDF 배치 (일 4회) | 히트맵 생성 | 분산 처리 | 검증된 모델로 실제 예측을 수행합니다 (양산) |
# MAGIC | **7. 모니터링** | PSI 드리프트 탐지 | -- | Data Quality Monitor | 모델이 여전히 잘 작동하는지 감시합니다 (SPC) |
# MAGIC | **8. 자동화** | Agent + Workflows | -- | 재학습/배포 자동화 | 위의 모든 과정을 사람 개입 없이 자동 실행합니다 |
# MAGIC
# MAGIC **파이프라인 흐름**: 데이터 → 피처 → 학습 → 등록 → 검증 → 추론 → 모니터링 → (드리프트 감지 시) 자동 재학습
# MAGIC
# MAGIC > **제조 비유**: 이 파이프라인은 공장의 생산 라인과 동일한 구조입니다. 원재료(데이터) 투입 → 가공(피처) → 조립(학습) → 품질검사(검증) → 출하(추론) → 고객 피드백(모니터링) → 공정 개선(재학습). 다만 여기서는 **"제품"이 "AI 예측 모델"** 입니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 노트북 목차
# MAGIC
# MAGIC | # | 노트북 | 설명 | Databricks 기능 |
# MAGIC |---|--------|------|-----------------|
# MAGIC | 01 | [Overview (본 노트북)]($./01_overview) | 전체 아키텍처 및 시나리오 소개 | -- |
# MAGIC | 02 | [피처 엔지니어링]($./02_structured_feature_engineering) | AI4I 2020 데이터 탐색 및 피처 생성 | Delta Lake, Feature Store, Unity Catalog |
# MAGIC | 03 | [모델 학습]($./03_structured_model_training) | XGBoost 학습, HPO, SHAP 해석 | MLflow Tracking, Autolog |
# MAGIC | 03a | [ML 트렌드]($./03a_ml_trends_and_techniques) | 최신 ML 기술 트렌드 가이드 | -- |
# MAGIC | 03b | [멀티 알고리즘]($./03b_multi_algorithm_comparison) | XGBoost/LightGBM/CatBoost/RF 비교 | MLflow 실험 비교 |
# MAGIC | 03c | [고급 기법]($./03c_advanced_techniques) | SMOTE, Optuna, Stacking, AutoML | Databricks AutoML |
# MAGIC | 03d | [재학습 전략]($./03d_retraining_strategies) | Incremental, Continual, Online, RL, Active Learning | Streaming, Delta Time Travel |
# MAGIC | 04 | [모델 등록]($./04_model_registration_uc) | UC 모델 레지스트리 등록 및 에일리어스 | Unity Catalog Models, Lineage |
# MAGIC | 05 | [챌린저 검증]($./05_challenger_validation) | Champion-Challenger 비교 검증 | Model Validation, A/B Testing |
# MAGIC | 06 | [배치 추론]($./06_batch_inference) | PySpark UDF 기반 대규모 배치 예측 | Spark UDF, Delta Lake |
# MAGIC | 07 | [비정형 이상탐지]($./07_unstructured_anomaly_detection) | MVTec AD + Anomalib PatchCore | Volumes, GPU Cluster, MLflow |
# MAGIC | 08 | [모델 모니터링]($./08_model_monitoring) | 데이터 드리프트 및 성능 모니터링 | Data Quality Monitoring |
# MAGIC | 09 | [MLOps Agent]($./09_mlops_agent) | Agent 기반 학습/예측 오케스트레이션 | AI Agent, Tool Use |
# MAGIC | 10 | [Job 스케줄링]($./10_job_scheduling) | 운영/개발 환경 워크플로우 설정 | Lakeflow Jobs |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 정형 데이터: AI4I 2020 Predictive Maintenance Dataset
# MAGIC
# MAGIC **정형 데이터(Structured Data)** 란 엑셀 표처럼 행(Row)과 열(Column)로 구성된 숫자/텍스트 데이터를 말합니다. 공장의 센서에서 수집되는 온도, 압력, 회전수 등이 대표적인 정형 데이터입니다.
# MAGIC
# MAGIC **AI4I 2020 데이터셋** 은 독일 뮌헨 공대 연구팀이 실제 산업 현장의 설비 고장 패턴을 반영하여 만든 합성(Synthetic) 데이터입니다. 실제 데이터는 보안상 공개가 어려우므로, 통계적 특성을 동일하게 유지한 대체 데이터를 사용합니다.
# MAGIC
# MAGIC | 항목 | 상세 | 부가 설명 |
# MAGIC |------|------|----------|
# MAGIC | **데이터** | UCI AI4I 2020 -- 실제 산업 데이터 기반 합성 데이터셋 | UCI는 캘리포니아대학교 어바인 캠퍼스에서 운영하는 ML 데이터 저장소입니다 |
# MAGIC | **규모** | 10,000건 | 실습에 적합한 크기이며, Databricks는 수억 건도 처리 가능합니다 |
# MAGIC | **입력 피처** | 공기 온도(K), 공정 온도(K), 회전속도(rpm), 토크(Nm), 공구 마모(min), 제품 타입 | 이 6개 값을 조합하여 고장 여부를 예측합니다 |
# MAGIC | **출력** | 고장 발생 여부 (이진 분류), 고장 유형 확률, 위험 점수 | 이진 분류(Binary Classification) = "예/아니오" 중 하나를 답하는 문제 |
# MAGIC | **모델** | XGBoost (eXtreme Gradient Boosting) | 2025~2026년 기준 정형 데이터 분류/회귀에서 가장 널리 사용되는 알고리즘입니다 |
# MAGIC | **해석** | SHAP 기반 피처 중요도 및 개별 예측 해석 | SHAP = "이 예측에 어떤 피처가 얼마나 기여했는가"를 설명하는 기법. 제조 현장에서 "왜 이 설비가 위험한가"를 설명할 수 있습니다 |
# MAGIC
# MAGIC > **제조 현장 적용 예시**: 공기 온도가 평소보다 5도 높고, 토크가 급격히 증가했을 때 → 모델이 "고장 확률 87%"라고 예측 → SHAP이 "토크 증가가 가장 큰 원인"이라고 설명 → 현장 엔지니어가 토크 관련 부품을 선제적으로 점검
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 비정형 데이터: MVTec AD
# MAGIC
# MAGIC **비정형 데이터(Unstructured Data)** 란 이미지, 비디오, 텍스트처럼 엑셀 표 형태가 아닌 데이터를 말합니다. 공장에서는 AOI(자동광학검사) 카메라로 촬영한 제품 사진, 현미경 이미지 등이 해당됩니다.
# MAGIC
# MAGIC **MVTec AD** 는 독일 뮌헨의 MVTec 사가 산업용 결함 탐지 연구를 위해 공개한 세계적으로 가장 유명한 벤치마크(기준) 데이터셋입니다.
# MAGIC
# MAGIC | 항목 | 상세 | 부가 설명 |
# MAGIC |------|------|----------|
# MAGIC | **데이터** | MVTec AD -- Industrial Inspection 벤치마크 | 나사, 금속 표면, 가죽, 타일 등 15가지 산업 제품 포함 |
# MAGIC | **규모** | 15개 카테고리, 5,000장 이상 고해상도 이미지 | 정상 이미지와 다양한 결함(흠집, 균열, 오염 등) 이미지 포함 |
# MAGIC | **구조** | 정상 이미지로 학습, 이상 이미지로 테스트 | 핵심 아이디어: "정상이 어떻게 생겼는지"만 학습하면, "정상과 다른 것"을 결함으로 탐지할 수 있습니다 |
# MAGIC | **입력** | 제품 표면 이미지 (RGB 컬러) | 실제 AOI 검사 이미지와 유사한 형태입니다 |
# MAGIC | **출력** | 정상/이상, 이상 점수(0~1), 이상 위치 히트맵(Heatmap) | 히트맵 = 이미지에서 어디가 결함인지를 색상으로 표시한 그림 |
# MAGIC | **모델** | Anomalib PatchCore (또는 Reverse Distillation) | PatchCore는 2022년 발표 이후 산업용 이상탐지에서 최고 성능을 기록한 알고리즘입니다 |
# MAGIC
# MAGIC > **왜 정상 이미지만으로 학습하나요?**: 제조 현장에서는 불량 데이터가 극히 드뭅니다 (보통 전체의 0.1~1%). 불량 데이터를 충분히 모으기 어렵기 때문에, "정상 패턴"만 학습하고 정상에서 벗어나면 이상으로 판정하는 방식이 실용적입니다. 이를 **비지도 학습 기반 이상탐지(Unsupervised Anomaly Detection)** 라고 합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 시작하기
# MAGIC
# MAGIC 이제 MLOps의 전체 그림을 이해하셨습니다. 다음 단계부터 실제로 각 구성 요소를 하나씩 만들어 보겠습니다.
# MAGIC
# MAGIC ### 학습 진행 순서
# MAGIC
# MAGIC ```
# MAGIC [현재] 01_Overview (전체 그림 이해)
# MAGIC    ↓
# MAGIC [다음] 02_피처 엔지니어링 (원재료 가공)
# MAGIC    ↓
# MAGIC    03_모델 학습 (AI 모델 생성)
# MAGIC    ↓
# MAGIC    04_모델 등록 → 05_검증 → 06_배치 추론
# MAGIC    ↓
# MAGIC    07_비전 AI → 08_모니터링
# MAGIC    ↓
# MAGIC    09_Agent → 10_Job 스케줄링 (자동화 완성)
# MAGIC ```
# MAGIC
# MAGIC > **Tip**: 각 노트북은 독립적으로 실행할 수 있지만, 순서대로 진행하면 전체 MLOps 파이프라인을 점진적으로 이해할 수 있습니다.
# MAGIC
# MAGIC 다음 단계: [피처 엔지니어링]($./02_structured_feature_engineering)으로 진행하여 AI4I 2020 센서 데이터를 탐색하고, ML 모델이 학습할 수 있는 형태로 가공(피처 엔지니어링)합니다.
