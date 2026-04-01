# Databricks notebook source
# MAGIC %md
# MAGIC # 예지보전 ML 최신 기술 트렌드 및 적용 가이드
# MAGIC
# MAGIC 본 노트북에서는 LG Innotek의 **예지보전(Predictive Maintenance)**및 **비전 이상탐지** 모델에
# MAGIC 적용할 수 있는 **최신 ML 기술 트렌드** 를 정리하고, 각 기법의 원리와 적용 방법을 상세히 설명합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 왜 제조업에 ML이 필요한가?
# MAGIC
# MAGIC 전통적인 제조 품질관리는 **규칙 기반(Rule-based)** 접근법에 의존합니다.
# MAGIC 예를 들어, "토크가 60Nm을 초과하면 경고"와 같은 고정 임계값을 사용합니다.
# MAGIC 하지만 실제 설비 고장은 **여러 변수의 복합적 상호작용** 에 의해 발생합니다.
# MAGIC
# MAGIC | 접근법 | 원리 | 한계 |
# MAGIC |--------|------|------|
# MAGIC | **고정 임계값** | 단일 센서값 기준 알람 | 복합 원인 탐지 불가, 오탐 과다 |
# MAGIC | **통계적 공정 관리 (SPC)** | 관리도 기반 이상 탐지 | 비선형 패턴 탐지 어려움 |
# MAGIC | **머신러닝** | 다변량 패턴 자동 학습 | 데이터 품질과 양에 의존 |
# MAGIC
# MAGIC ML은 온도, 회전수, 토크, 공구 마모량 등 **수십 개 센서의 상호작용 패턴** 을 자동으로 학습하여,
# MAGIC 사람이 발견하기 어려운 **고장 전조 징후(Precursor Signal)** 를 포착합니다.
# MAGIC 이는 마치 숙련된 엔지니어가 "이 소리와 진동 조합이면 곧 고장나겠다"고 판단하는 것을,
# MAGIC 데이터로부터 자동 학습하는 것과 같습니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## ML 알고리즘의 진화 — 70년의 여정
# MAGIC
# MAGIC ML 기술은 1950년대부터 꾸준히 발전해왔습니다. 제조업에서 실질적으로 활용 가능한 수준에 도달한 것은
# MAGIC 2010년대 이후이며, 현재는 **자동화(AutoML)**와 **기반 모델(Foundation Models)** 시대로 진입하고 있습니다.
# MAGIC
# MAGIC ```
# MAGIC 1950s  Perceptron (단층 신경망) — 최초의 학습 가능한 모델
# MAGIC   │
# MAGIC 1980s  Decision Tree, Neural Networks — 규칙 학습, 역전파 알고리즘 등장
# MAGIC   │
# MAGIC 1990s  SVM, Random Forest — 통계적 학습 이론의 전성기
# MAGIC   │
# MAGIC 2000s  Ensemble Methods (AdaBoost, GBM) — "약한 학습기를 결합하면 강해진다"
# MAGIC   │
# MAGIC 2014   XGBoost 등장 — Kaggle 대회 석권, 산업 표준으로 자리잡음
# MAGIC   │
# MAGIC 2017   LightGBM, CatBoost — 더 빠르고, 더 똑똑한 Gradient Boosting
# MAGIC   │
# MAGIC 2020s  AutoML, Foundation Models — 알고리즘 선택과 튜닝까지 자동화
# MAGIC   │
# MAGIC 2024~  TabPFN, CARTE — 정형 데이터용 Foundation Model 시대 개막
# MAGIC ```
# MAGIC
# MAGIC > **제조업 관점**: 2014년 XGBoost의 등장이 전환점이었습니다. 이전에는 ML 적용에 깊은 통계 지식이
# MAGIC > 필요했지만, XGBoost 이후로는 **데이터만 잘 준비하면** 강력한 예측 모델을 구축할 수 있게 되었습니다.
# MAGIC > 현재는 AutoML이 등장하여 알고리즘 선택과 하이퍼파라미터 튜닝까지 자동화되고 있습니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 알고리즘 패밀리 — 직관적 이해
# MAGIC
# MAGIC ML 알고리즘은 크게 세 가지 "가족"으로 분류할 수 있습니다. 각 가족은 서로 다른 철학으로 데이터를 학습합니다.
# MAGIC
# MAGIC | 알고리즘 패밀리 | 비유 (제조 현장) | 대표 알고리즘 | 핵심 원리 |
# MAGIC |----------------|-----------------|-------------|----------|
# MAGIC | **배깅 (Bagging)**| 10명의 검사원이 **독립적으로** 검사 후 다수결 | Random Forest | 여러 트리를 병렬로 학습, 다수결 투표 |
# MAGIC | **부스팅 (Boosting)**| 선배 검사원의 **실수를 후배가 보완** 하며 연쇄 학습 | XGBoost, LightGBM, CatBoost | 순차 학습, 이전 오차를 다음 모델이 보정 |
# MAGIC | **딥러닝 (Deep Learning)**| 수천 장의 불량 이미지를 보며 **자체적으로 판단 기준** 형성 | CNN, Transformer | 다층 신경망으로 특징 자동 추출 |
# MAGIC
# MAGIC > **부스팅을 제조 비유로 설명하면**: 첫 번째 검사원이 100개 제품을 검사합니다. 그 중 10개를 오판합니다.
# MAGIC > 두 번째 검사원은 **그 10개에 특히 집중** 하여 검사합니다. 세 번째 검사원은 두 번째가 놓친 것에 집중합니다.
# MAGIC > 이렇게 200명의 검사원이 순차적으로 보완하면, 최종 판정 정확도는 개별 검사원보다 **압도적으로 높아집니다**.
# MAGIC > 이것이 Gradient Boosting의 핵심 원리입니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 제조업에서 알고리즘을 고르는 기준
# MAGIC
# MAGIC | 제조 상황 | 추천 알고리즘 | 이유 |
# MAGIC |----------|-------------|------|
# MAGIC | 센서 데이터 기반 고장 예측 | **XGBoost / LightGBM** | 정형 데이터 분류에서 최고 성능 |
# MAGIC | 범주형 변수 다수 (설비 타입, 제품 등급) | **CatBoost** | 범주형 자동 인코딩, 전처리 최소화 |
# MAGIC | 빠른 프로토타이핑, 피처 중요도 분석 | **Random Forest** | 안정적이고 해석이 쉬움 |
# MAGIC | 대용량 데이터 (수백만 행 이상) | **LightGBM** | 속도 2~10배 빠름, 메모리 효율적 |
# MAGIC | 이미지 기반 외관 검사 | **CNN / Vision Transformer** | 시각 패턴 자동 학습 |
# MAGIC | 데이터 부족한 초기 PoC | **AutoML + TabPFN** | 사전 학습 모델로 소량 데이터에서도 성능 확보 |
# MAGIC | 모델 선택을 자동화하고 싶다면 | **Databricks AutoML / FLAML** | 알고리즘 + 하이퍼파라미터 자동 탐색 |
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
# MAGIC 정형 데이터(Tabular Data)란 **엑셀 표처럼 행(샘플)과 열(변수)로 정리된 데이터** 입니다.
# MAGIC 제조 현장에서 수집되는 센서 데이터(온도, 회전수, 토크 등)가 대표적인 정형 데이터입니다.
# MAGIC 정형 데이터 분석에서는 2024년 현재까지도 **Gradient Boosting 계열 알고리즘** 이 최고 성능을 보이며,
# MAGIC 딥러닝이 아직 이 영역에서 우위를 점하지 못하고 있습니다.
# MAGIC
# MAGIC ## 1.1 Gradient Boosting 앙상블 계열 발전
# MAGIC
# MAGIC Gradient Boosting은 **"실수를 반복 학습하여 점점 더 정확해지는"** 알고리즘입니다.
# MAGIC 제조 비유로, 품질 검사 라인에서 1번 검사원이 놓친 불량을 2번 검사원이 잡고,
# MAGIC 2번이 놓친 것을 3번이 잡는 식으로 **연쇄적으로 보완** 하는 구조입니다.
# MAGIC
# MAGIC 아래 표는 Gradient Boosting의 주요 변형들을 비교합니다:
# MAGIC
# MAGIC | 알고리즘 | 개발 | 핵심 혁신 | 장점 | 제조 적용 시나리오 |
# MAGIC |----------|------|----------|------|-------------------|
# MAGIC | **XGBoost**| 2014, Tianqi Chen (워싱턴대) | L1/L2 정규화 + 병렬 트리 구축 | 안정적 성능, **산업 표준**, 커뮤니티 최대 | 범용 고장 예측, 품질 분류 |
# MAGIC | **LightGBM**| 2017, Microsoft Research | Leaf-wise 성장, GOSS, EFB | 대규모 데이터에서 **2~10배 빠른** 학습 | 고차원 센서 데이터, 실시간 스코어링 |
# MAGIC | **CatBoost**| 2017, Yandex | 범주형 자동 인코딩, Ordered Boosting | 범주형 피처 전처리 불필요, **과적합 방지** | 설비 타입/제품 등급 등 범주형 다수 |
# MAGIC | **HistGradientBoosting**| 2019, scikit-learn | 히스토그램 기반 분할 | 별도 설치 불필요, **결측치 자동 처리** | 빠른 프로토타이핑, PoC |
# MAGIC
# MAGIC ### 최신 트렌드: 정형 데이터용 Foundation Model
# MAGIC
# MAGIC 2024년부터 정형 데이터에서도 **사전 학습된 기반 모델** 이 등장하고 있습니다:
# MAGIC
# MAGIC | 기술 | 원리 | 제조 적용 가능성 |
# MAGIC |------|------|----------------|
# MAGIC | **TabPFN**(2024) | 수백만 개의 합성 테이블로 사전 학습된 Transformer | **소량 데이터에서 XGBoost를 능가** — 신규 설비 초기 데이터 부족 시 유용 |
# MAGIC | **CARTE**(2024) | 컬럼명의 의미를 활용한 사전 학습 | 유사한 설비의 데이터를 **전이 학습** 으로 활용 가능 |
# MAGIC | **TabR** (2023) | Retrieval-augmented 정형 데이터 학습 | 과거 유사 고장 사례를 검색하여 예측에 활용 |
# MAGIC
# MAGIC > **시사점**: 아직 Gradient Boosting이 대부분의 제조 데이터에서 최고 성능이지만,
# MAGIC > **데이터가 적은 상황** (신규 설비, 희귀 고장)에서는 TabPFN 같은 Foundation Model이 대안이 될 수 있습니다.
# MAGIC
# MAGIC ### 왜 멀티 알고리즘 비교가 중요한가?
# MAGIC
# MAGIC **No Free Lunch Theorem (공짜 점심은 없다)**: 수학적으로 증명된 정리로, ** 모든 문제에 최적인
# MAGIC 단일 알고리즘은 존재하지 않습니다**. 이는 제조 현장에서도 동일합니다.
# MAGIC
# MAGIC - AI4I 2020 데이터는 **불균형(고장 3.4%)**+ **연속형/범주형 혼합** → CatBoost가 유리할 수 있음
# MAGIC - 제조 데이터는 **시계열 패턴** → LightGBM의 빠른 반복 학습이 유리
# MAGIC - 고차원 센서 데이터(수백 개 피처) → LightGBM의 EFB(Exclusive Feature Bundling)가 유리
# MAGIC - MLflow로 **동일 조건 비교**가 가능 → 감이 아닌 **데이터 기반 알고리즘 선택**
# MAGIC
# MAGIC > **Databricks 장점**: Databricks에서는 MLflow가 내장되어 있어, 별도 설정 없이
# MAGIC > 여러 알고리즘의 파라미터/메트릭/모델을 자동으로 기록하고 **UI에서 한눈에 비교** 할 수 있습니다.
# MAGIC > 이것이 Excel이나 수작업으로는 불가능한, **체계적인 실험 관리** 입니다.
# MAGIC
# MAGIC > **실습**: [03b_multi_algorithm_comparison]($./03b_multi_algorithm_comparison) 노트북에서 4개 알고리즘을 동시 비교합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.2 불균형 데이터 처리 (Imbalanced Learning)
# MAGIC
# MAGIC ### 제조 데이터의 본질적 특성: 극심한 클래스 불균형
# MAGIC
# MAGIC 제조 예지보전 데이터는 **극심한 클래스 불균형** 이 특징입니다.
# MAGIC AI4I 2020 데이터의 경우 고장률이 **약 3.4%** 에 불과합니다.
# MAGIC
# MAGIC **왜 이것이 문제인가?**
# MAGIC
# MAGIC 공장 비유로 설명하면: 100개 제품 중 97개가 양품이고 3개가 불량인 검사 라인을 상상해보세요.
# MAGIC 만약 검사원이 "모두 양품"이라고 판정하면, **정확도가 97%** 나 됩니다.
# MAGIC 하지만 이 검사원은 **불량을 단 하나도 찾지 못합니다**.
# MAGIC ML 모델도 마찬가지로, 불균형 데이터를 그대로 학습하면 "모두 정상"으로 예측하는 편향이 생깁니다.
# MAGIC
# MAGIC ### 불균형 처리 기법의 체계적 분류
# MAGIC
# MAGIC 불균형 처리 기법은 크게 **데이터 레벨**과 **알고리즘 레벨** 로 나뉩니다:
# MAGIC
# MAGIC #### 데이터 레벨 (학습 데이터 자체를 변형)
# MAGIC
# MAGIC | 기법 | 원리 | 제조 비유 | 장점 | 단점 |
# MAGIC |------|------|----------|------|------|
# MAGIC | **SMOTE** | 소수 클래스 샘플 사이에 합성 데이터 생성 | 불량 샘플 사이의 "중간" 특성을 가진 가상 불량 생성 | 간단, 효과적 | 노이즈 생성 가능 |
# MAGIC | **ADASYN** | 학습하기 어려운 영역에 더 많은 합성 데이터 생성 | 경계선에서 양품/불량 구분이 어려운 영역에 집중 보강 | SMOTE보다 적응적 | 경계 과적합 |
# MAGIC | **BorderlineSMOTE** | 결정 경계 근처의 소수 클래스만 오버샘플링 | 양품과 불량의 "경계선" 근처에서만 합성 데이터 생성 | 노이즈 감소 | 파라미터 민감 |
# MAGIC | **SMOTE-ENN** | SMOTE 후 모호한 샘플 제거 | 합성 불량 데이터 생성 후, 양품과 너무 비슷한 것은 제거 | 오버샘플링 + 정제 | 계산 비용 높음 |
# MAGIC
# MAGIC #### 알고리즘 레벨 (모델 학습 방식을 변형)
# MAGIC
# MAGIC | 기법 | 원리 | 제조 비유 | 장점 | 단점 |
# MAGIC |------|------|----------|------|------|
# MAGIC | **class_weight / scale_pos_weight**| 소수 클래스 오분류에 더 큰 패널티 부여 | 불량을 놓치면 양품 놓칠 때보다 **30배 더 큰 벌점** 부과 | 데이터 변형 없음 | 효과 제한적일 수 있음 |
# MAGIC | **Focal Loss** | 쉬운 샘플의 가중치를 줄여 어려운 샘플에 집중 | "확실한 양품" 판정에는 학습 비중을 줄이고, "애매한 것"에 집중 | 딥러닝에 효과적 | 하이퍼파라미터 튜닝 필요 |
# MAGIC | **Cost-sensitive Learning** | 오분류 비용 행렬을 직접 정의 | 불량 미탐지 비용(설비 파손)이 오탐 비용(불필요 정비)보다 크다고 명시 | 비즈니스 로직 반영 | 비용 정의가 어려움 |
# MAGIC
# MAGIC ### AI4I 2020 데이터에 권장 전략:
# MAGIC ```
# MAGIC 1순위: SMOTE-ENN — 합성 데이터 생성 + 노이즈 제거, 가장 균형 잡힌 접근
# MAGIC 2순위: scale_pos_weight — 모델 내장 기능으로 가장 간단, 추가 라이브러리 불필요
# MAGIC 3순위: BorderlineSMOTE — 경계선 중심 합성, SMOTE보다 정교한 오버샘플링
# MAGIC ```
# MAGIC
# MAGIC > **Databricks 장점**: MLflow로 각 불균형 처리 기법의 결과를 **동일 조건에서 비교** 할 수 있습니다.
# MAGIC > "SMOTE-ENN을 적용했을 때 Recall이 0.72에서 0.85로 향상"과 같은 **정량적 근거 기반 의사결정** 이 가능합니다.
# MAGIC
# MAGIC > **실습**: [03c_advanced_techniques]($./03c_advanced_techniques) 노트북에서 SMOTE 계열 기법을 적용합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.3 하이퍼파라미터 최적화 (HPO) 최신 기법
# MAGIC
# MAGIC ### 하이퍼파라미터란?
# MAGIC
# MAGIC ML 모델에는 두 종류의 파라미터가 있습니다:
# MAGIC - **학습 파라미터**: 모델이 데이터로부터 **자동으로 학습** 하는 값 (예: 트리의 분할 기준)
# MAGIC - **하이퍼파라미터**: 사람이 **사전에 설정** 해야 하는 값 (예: 트리 깊이, 학습률)
# MAGIC
# MAGIC 제조 비유로, 하이퍼파라미터는 **검사 장비의 세팅값** 과 같습니다.
# MAGIC 카메라 검사 장비에서 "밝기", "대비", "확대율"을 어떻게 설정하느냐에 따라
# MAGIC 불량 검출 성능이 달라지는 것과 같습니다.
# MAGIC 최적의 세팅을 찾는 과정이 바로 **하이퍼파라미터 최적화(HPO)** 입니다.
# MAGIC
# MAGIC ### HPO 기법의 진화 — 무작위에서 지능적 탐색으로
# MAGIC
# MAGIC | 기법 | 원리 | 제조 비유 | 장점 | Databricks 지원 |
# MAGIC |------|------|----------|------|----------------|
# MAGIC | **Grid Search** | 모든 조합을 격자형으로 탐색 | 가능한 모든 세팅 조합을 일일이 시험 | 확실한 최적화 | scikit-learn 내장 |
# MAGIC | **Random Search** | 랜덤하게 조합 선택 | 무작위로 세팅을 바꿔보며 시험 | Grid보다 효율적 (2012, Bergstra 증명) | scikit-learn 내장 |
# MAGIC | **Optuna**(2019, Preferred Networks) | 이전 결과를 학습하여 유망한 영역 집중 탐색 | 이전 시험 결과를 보고 "이 방향이 좋겠다" 판단 | **적은 시행으로 최적화**, 시각화 내장 | MLflow 자동 연동 |
# MAGIC | **Hyperopt**(2013, Bergstra) | Tree of Parzen Estimators (TPE) | Optuna와 유사하나 Databricks 분산 환경에 최적화 | **Spark 클러스터 전체를 활용한 분산 HPO** | SparkTrials 네이티브 지원 |
# MAGIC | **FLAML**(2021, Microsoft) | 경량 AutoML, 알고리즘까지 자동 선택 | 검사 장비 종류와 세팅을 **동시에**자동 최적화 | **초고속**, 자원 효율적 | pip install로 바로 사용 |
# MAGIC | **Ray Tune** (2018, Anyscale) | 대규모 분산 HPO 프레임워크 | 수백 대의 장비에서 동시에 세팅 시험 | 대규모 탐색, 다양한 알고리즘 지원 | Databricks에서 Ray 클러스터 연동 |
# MAGIC
# MAGIC ### Optuna vs Hyperopt vs FLAML — 실무 선택 가이드
# MAGIC
# MAGIC | 상황 | 추천 도구 | 이유 |
# MAGIC |------|----------|------|
# MAGIC | **처음 HPO를 시도한다면**| **Optuna** | API가 직관적, 시각화 내장, 학습 곡선 낮음 |
# MAGIC | **Databricks 클러스터 자원을 최대 활용하고 싶다면**| **Hyperopt + SparkTrials** | 워커 노드에 분산하여 병렬 HPO, Databricks 네이티브 |
# MAGIC | **알고리즘 선택부터 자동화하고 싶다면**| **FLAML** | 알고리즘 + 하이퍼파라미터를 동시에 자동 탐색, 1시간 내 최적 모델 |
# MAGIC | **GPU 기반 딥러닝 HPO**| **Ray Tune** | GPU 분산 학습, 스케줄링 최적화 |
# MAGIC
# MAGIC ### Optuna의 핵심 기능 — Pruning (조기 중단)
# MAGIC
# MAGIC Optuna의 가장 강력한 기능은 **Pruning** 입니다. 학습 도중 "이 하이퍼파라미터 조합은 가망이 없다"고
# MAGIC 판단되면 **즉시 학습을 중단** 하고 다음 조합으로 넘어갑니다.
# MAGIC 제조 비유로, 품질 시험 중 초기 몇 개만 봐도 "이 세팅은 안 되겠다"고 판단하여 빠르게 다음 세팅으로 넘어가는 것과 같습니다.
# MAGIC 이를 통해 HPO 시간을 **50~80% 절감** 할 수 있습니다.
# MAGIC
# MAGIC ```python
# MAGIC # Optuna 예시 — Pruning 포함
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
# MAGIC
# MAGIC # Optuna 내장 시각화 — 파라미터 중요도, 최적화 히스토리 등을 자동 시각화
# MAGIC # optuna.visualization.plot_param_importances(study)
# MAGIC # optuna.visualization.plot_optimization_history(study)
# MAGIC ```
# MAGIC
# MAGIC > **Databricks 장점**: Optuna의 모든 시행(trial) 결과가 MLflow에 자동 기록되어,
# MAGIC > 나중에 "왜 이 하이퍼파라미터 조합을 선택했는지" **재현 가능한 근거** 를 남길 수 있습니다.
# MAGIC
# MAGIC > **실습**: [03c_advanced_techniques]($./03c_advanced_techniques) 노트북에서 Optuna HPO를 적용합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.4 AutoML (자동 머신러닝) — ML 민주화의 핵심
# MAGIC
# MAGIC ### AutoML이란?
# MAGIC
# MAGIC AutoML은 **알고리즘 선택, 하이퍼파라미터 튜닝, 피처 엔지니어링** 을 모두 자동으로 수행하는 기술입니다.
# MAGIC 제조 비유로, 숙련된 데이터 과학자가 수주간 수행할 작업을 **30분~1시간** 내에 자동으로 완료합니다.
# MAGIC
# MAGIC **AutoML의 역사와 발전**:
# MAGIC - **2013**: Auto-WEKA — 최초의 체계적 AutoML 프레임워크
# MAGIC - **2015**: Auto-sklearn — WEKA의 Python 버전, Kaggle 경쟁력 입증
# MAGIC - **2020**: Google AutoML Tables, Azure AutoML — 클라우드 서비스화
# MAGIC - **2021**: FLAML (Microsoft) — 경량화, 100배 빠른 AutoML
# MAGIC - **2023~**: Databricks AutoML — Lakehouse 통합, MLflow 자동 연동
# MAGIC
# MAGIC ### Databricks AutoML — 제조업에 최적화된 이유
# MAGIC
# MAGIC | 기능 | 설명 | 제조업 가치 |
# MAGIC |------|------|-----------|
# MAGIC | **코드 없이 시작** | UI에서 테이블과 타겟 컬럼만 선택 | 데이터 사이언티스트 없이도 PoC 가능 |
# MAGIC | **자동 알고리즘 탐색** | XGBoost, LightGBM, RF 등 자동 비교 | 편향 없는 알고리즘 선택 |
# MAGIC | **자동 HPO** | Bayesian Optimization으로 최적 파라미터 탐색 | 수작업 대비 5~10배 빠른 최적화 |
# MAGIC | **MLflow 자동 기록** | 모든 실험을 재현 가능하게 기록 | 감사(Audit) 추적 가능 |
# MAGIC | **노트북 자동 생성**| 최적 모델의 코드를 노트북으로 제공 | **블랙박스가 아님** — 코드를 수정하여 커스터마이징 가능 |
# MAGIC | **불균형 자동 처리** | 클래스 불균형을 감지하고 자동 보정 | 제조 데이터의 고장률 3~5% 문제 자동 해결 |
# MAGIC
# MAGIC ```python
# MAGIC from databricks import automl
# MAGIC
# MAGIC # 단 5줄로 전체 ML 파이프라인 자동 실행
# MAGIC summary = automl.classify(
# MAGIC     dataset=spark.table("lgit_pm_training"),
# MAGIC     target_col="machine_failure",
# MAGIC     primary_metric="f1",
# MAGIC     timeout_minutes=30,
# MAGIC )
# MAGIC # summary.best_trial — 최적 모델 정보
# MAGIC # summary.output_table_name — 결과 테이블
# MAGIC ```
# MAGIC
# MAGIC ### AutoML vs 수동 ML — 언제 무엇을 쓸 것인가?
# MAGIC
# MAGIC | 상황 | AutoML | 수동 ML |
# MAGIC |------|--------|--------|
# MAGIC | **초기 PoC, 베이스라인 확보** | 적합 | 과잉 투자 |
# MAGIC | **도메인 지식 반영 필요**| 보조 | **필수** (피처 엔지니어링 직접 설계) |
# MAGIC | **규제/설명 요구 (XAI)**| 제한적 | **필수** (SHAP, LIME 등 직접 적용) |
# MAGIC | **반복 재학습 자동화** | 적합 | Job 스케줄링 필요 |
# MAGIC
# MAGIC > **권장 전략**: AutoML로 **30분 내 베이스라인** 을 확보한 후,
# MAGIC > 생성된 노트북을 기반으로 **도메인 지식을 반영한 커스터마이징** 을 수행하세요.
# MAGIC > 이것이 가장 효율적인 접근법입니다.
# MAGIC
# MAGIC > **실습**: [03c_advanced_techniques]($./03c_advanced_techniques) 노트북에서 AutoML을 실행합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.5 앙상블 기법 (Ensemble Methods) — "집단 지성"의 원리
# MAGIC
# MAGIC ### 앙상블이란?
# MAGIC
# MAGIC 앙상블(Ensemble)은 **여러 모델의 예측을 결합** 하여 단일 모델보다 더 좋은 성능을 얻는 기법입니다.
# MAGIC 제조 비유로, 한 명의 수석 엔지니어보다 **여러 분야 전문가의 합의** 가 더 정확한 판단을 내리는 것과 같습니다.
# MAGIC
# MAGIC 실제로 Kaggle 데이터 과학 대회의 상위 솔루션 중 **90% 이상** 이 앙상블을 사용하며,
# MAGIC 실무에서도 **0.5~3% 포인트** 의 추가 성능 향상을 안정적으로 얻을 수 있습니다.
# MAGIC
# MAGIC ### Stacking (스태킹) — 가장 강력한 앙상블
# MAGIC
# MAGIC Stacking은 여러 기본 모델(Base Learner)의 예측을 **메타 모델(Meta Learner)** 이 결합하는 기법입니다.
# MAGIC 각 Base Learner가 서로 다른 관점에서 데이터를 분석하고, Meta Learner가 그 결과를 종합합니다.
# MAGIC
# MAGIC ```
# MAGIC ┌─────────┐  ┌──────────┐  ┌──────────┐
# MAGIC │ XGBoost │  │ LightGBM │  │ CatBoost │   ← Base Learners (각각 다른 관점으로 분석)
# MAGIC └────┬────┘  └────┬─────┘  └────┬─────┘
# MAGIC      │            │             │
# MAGIC      └────────────┼─────────────┘
# MAGIC                   ▼
# MAGIC           ┌───────────────┐
# MAGIC           │ Logistic Reg  │              ← Meta Learner (종합 판단)
# MAGIC           └───────────────┘
# MAGIC ```
# MAGIC
# MAGIC **왜 Stacking이 효과적인가?**
# MAGIC - XGBoost는 **정규화 패턴**에 강하고, CatBoost는 **범주형 패턴**에 강하고, LightGBM은 **대규모 패턴** 에 강합니다
# MAGIC - Meta Learner는 **각 모델이 잘하는 영역을 자동으로 파악** 하여 최적의 가중치로 결합합니다
# MAGIC - 결과적으로, 개별 모델의 약점이 상호 보완되어 **안정적인 성능 향상** 을 달성합니다
# MAGIC
# MAGIC ### Weighted Voting (가중 투표) — 간단하지만 효과적
# MAGIC - 각 모델의 검증 성능에 비례하여 **가중 평균**
# MAGIC - Stacking보다 단순하지만 과적합 위험이 낮음
# MAGIC - 제조 비유: F1=0.85인 XGBoost의 의견에 F1=0.80인 RF보다 더 큰 비중을 둠
# MAGIC
# MAGIC ### 앙상블 적용 시 주의점
# MAGIC
# MAGIC | 고려사항 | 설명 |
# MAGIC |---------|------|
# MAGIC | **다양성 확보**| 동일한 알고리즘끼리 결합하면 효과 미미 — **서로 다른 계열** 을 결합 |
# MAGIC | **과적합 위험**| Base Learner 수가 너무 많으면 과적합 — 보통 **3~5개** 가 적정 |
# MAGIC | **추론 시간**| 모델 수만큼 추론 시간 증가 — 실시간 서빙 시 **속도/성능 트레이드오프** 고려 |
# MAGIC | **유지보수 복잡도**| 모델이 많을수록 관리 부담 — **MLflow로 체계적 관리** 필수 |
# MAGIC
# MAGIC > **실습**: [03c_advanced_techniques]($./03c_advanced_techniques) 노트북에서 Stacking을 구현합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.6 피처 선택 (Feature Selection) — "어떤 센서가 중요한가?"
# MAGIC
# MAGIC ### 왜 피처 선택이 중요한가?
# MAGIC
# MAGIC 제조 현장에는 수십~수백 개의 센서가 있지만, 실제로 고장 예측에 **핵심적인 역할을 하는 센서는 일부** 입니다.
# MAGIC 불필요한 피처(센서 데이터)를 포함하면:
# MAGIC - **모델 학습 시간 증가** — 불필요한 정보를 처리하느라 비효율
# MAGIC - **과적합 위험 증가** — 노이즈를 패턴으로 오인
# MAGIC - **해석 어려움** — 어떤 요인이 실제로 중요한지 파악 곤란
# MAGIC - **추론 지연** — 실시간 서빙 시 불필요한 센서 데이터 수집/처리 부담
# MAGIC
# MAGIC 피처 선택을 통해 **"핵심 센서 5~10개"** 를 식별하면,
# MAGIC 모델 성능은 유지하면서 **운영 효율성과 해석 가능성** 을 크게 높일 수 있습니다.
# MAGIC
# MAGIC ### 최신 피처 선택 기법
# MAGIC
# MAGIC | 기법 | 원리 | 제조 비유 | 적용 시나리오 |
# MAGIC |------|------|----------|-------------|
# MAGIC | **Boruta**| 랜덤 포레스트 기반 통계적 피처 중요도 검정 | 각 센서의 기여도를 **랜덤 노이즈와 비교** 하여 유의미한 센서만 선별 | 중요 피처 자동 선택 (권장) |
# MAGIC | **RFE** (Recursive Feature Elimination) | 반복적으로 가장 약한 피처 제거 | 가장 덜 중요한 센서부터 하나씩 제거하며 성능 변화 관찰 | 피처 수를 특정 개수로 줄이기 |
# MAGIC | **SHAP-based Selection**| SHAP 값 기반 피처 선택 | 각 센서가 예측에 **얼마나, 어떤 방향으로**기여하는지 정량화 | **설명 가능한** 피처 선택 (XAI 요구 시) |
# MAGIC | **Mutual Information**| 정보 이론 기반 피처-타겟 관련성 측정 | 각 센서가 고장 여부와 얼마나 **정보를 공유** 하는지 계산 | 비선형 관계 탐지 |
# MAGIC | **L1 정규화 (Lasso)**| 불필요한 피처의 가중치를 0으로 수렴 | 모델 학습 과정에서 자동으로 불필요한 센서를 **비활성화** | 빠른 피처 선택 (내장형) |
# MAGIC
# MAGIC > **Explainable AI (XAI) 트렌드**: 2024년 현재, 제조업에서는 **"왜 이 모델이 이렇게 판단했는가?"** 에 대한
# MAGIC > 설명 요구가 급증하고 있습니다. SHAP 기반 피처 선택은 단순히 피처를 선별하는 것을 넘어,
# MAGIC > **"토크와 온도 차이가 고장 예측에 가장 큰 영향을 미친다"** 는 비즈니스 인사이트를 제공합니다.
# MAGIC > 이는 설비 엔지니어와 데이터 과학자 간의 **공통 언어** 가 됩니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 2. 비정형 데이터 — 최신 이상탐지 기법
# MAGIC
# MAGIC ### 비정형 데이터란?
# MAGIC
# MAGIC 비정형 데이터(Unstructured Data)란 **이미지, 텍스트, 음성** 등 표 형태로 정리할 수 없는 데이터입니다.
# MAGIC 제조 현장에서는 **카메라로 촬영한 외관 이미지** 가 대표적인 비정형 데이터입니다.
# MAGIC 예를 들어, LG Innotek의 카메라 모듈, LED 기판, 반도체 패키징의 **외관 불량 검사** 가 이에 해당합니다.
# MAGIC
# MAGIC **비정형 이상탐지의 핵심 원리**: "정상이 어떻게 생겼는지"를 학습한 후,
# MAGIC 정상과 **다르게 생긴 부분**을 이상으로 탐지합니다. 이를 **비지도 이상탐지(Unsupervised Anomaly Detection)** 라 하며,
# MAGIC **불량 이미지 없이 정상 이미지만으로 학습** 할 수 있다는 것이 최대 장점입니다.
# MAGIC
# MAGIC ## 2.1 Anomalib 지원 모델 비교
# MAGIC
# MAGIC **Anomalib** 은 Intel이 개발한 오픈소스 이상탐지 라이브러리로,
# MAGIC 최신 이상탐지 알고리즘을 **통일된 인터페이스** 로 비교할 수 있습니다.
# MAGIC
# MAGIC | 모델 | 원리 | AUROC (MVTec) | 추론 속도 | 메모리 | 제조 적용 포인트 |
# MAGIC |------|------|--------------|----------|--------|----------------|
# MAGIC | **PatchCore**(2022) | 사전학습 CNN의 패치 피처 + Core-set 메모리 뱅크 | **99.1%**| 보통 | 높음 | **정확도 최우선** — 고가 부품 외관 검사 |
# MAGIC | **Reverse Distillation**(2022) | Teacher-Student 구조의 역방향 지식 증류 | 98.5% | **빠름** | 낮음 | 속도와 정확도 균형 — 중속 라인 검사 |
# MAGIC | **EfficientAD**(2023) | 경량 Teacher-Student + Autoencoder | 98.8% | **가장 빠름**| **가장 낮음**| **실시간 검사** — 엣지 디바이스, 고속 라인 |
# MAGIC | **PADIM** (2021) | 사전학습 CNN + 다변량 가우시안 분포 | 97.9% | 빠름 | 보통 | 구현 간단 — 빠른 PoC |
# MAGIC | **FastFlow** (2022) | Normalizing Flows (정규화 흐름) | 98.0% | 빠름 | 보통 | 이론적 확률 기반 — 신뢰도 산출 필요 시 |
# MAGIC | **GANomaly** (2018) | GAN 기반 생성/재구성 모델 | 96.0% | 보통 | 보통 | 레거시 환경 — 구형 GPU에서도 동작 |
# MAGIC
# MAGIC ### 제조 현장 권장 — 의사결정 트리:
# MAGIC ```
# MAGIC Q1: 실시간 추론이 필요한가? (라인 택트타임 < 1초)
# MAGIC   ├─ YES → EfficientAD (엣지 GPU에서도 구동 가능, ~5ms/장)
# MAGIC   └─ NO →
# MAGIC       Q2: 정확도가 최우선인가? (고가 부품, 안전 관련)
# MAGIC         ├─ YES → PatchCore (AUROC 99.1%, 업계 최고)
# MAGIC         └─ NO → Reverse Distillation (속도/정확도 최적 균형)
# MAGIC ```
# MAGIC
# MAGIC ## 2.2 최신 트렌드: Foundation Model 기반 이상탐지 (2024~)
# MAGIC
# MAGIC 가장 주목할 트렌드는 **"학습 없이 불량을 탐지하는"** Zero-shot 이상탐지입니다.
# MAGIC 이는 대규모 비전-언어 모델(Vision-Language Model)을 활용하여,
# MAGIC **정상 이미지도 불량 이미지도 없이** "이 이미지에서 이상한 부분을 찾아라"고 지시할 수 있습니다.
# MAGIC
# MAGIC | 기술 | 원리 | 제조 적용 가치 |
# MAGIC |------|------|-------------|
# MAGIC | **WinCLIP**(2023) | CLIP 기반 Zero-shot 이상탐지 | **학습 데이터 불필요** — 신규 제품 라인 즉시 검사 가능 |
# MAGIC | **AnomalyCLIP**(2024) | 프롬프트 기반 이상탐지 ("스크래치가 있는 부분을 찾아라") | 불량 유형별 **텍스트 설명** 만으로 탐지 가능 |
# MAGIC | **SAA+**(Segment Any Anomaly) | SAM + CLIP 결합 | 이상 영역을 **픽셀 단위로 정확히** 세그멘테이션 |
# MAGIC | **GPT-4V / Gemini Vision**| 멀티모달 LLM 기반 이상 판단 | 이상 탐지 + **자연어 설명 생성** ("3시 방향에 0.5mm 스크래치") |
# MAGIC
# MAGIC > **제조업 시사점**: 데이터가 부족한 **신규 제품 라인 초기 PoC 단계** 에서 Zero-shot 모델로 빠르게 시작하고,
# MAGIC > 데이터가 축적되면 PatchCore/EfficientAD로 전환하는 **2단계 전략** 이 가장 현실적입니다.
# MAGIC > Databricks에서는 MLflow를 통해 두 접근법의 성능을 체계적으로 비교할 수 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 3. MLOps 자동화 — 최신 트렌드
# MAGIC
# MAGIC ### MLOps란?
# MAGIC
# MAGIC MLOps는 **ML 모델의 개발, 배포, 운영, 모니터링을 체계적으로 자동화** 하는 방법론입니다.
# MAGIC 제조업에서 ML 모델은 한번 만들고 끝나는 것이 아닙니다. 설비가 노후화되고, 원자재가 바뀌고,
# MAGIC 공정 조건이 변하면 모델 성능이 저하됩니다. MLOps는 이러한 **모델 생애주기 전체** 를 관리합니다.
# MAGIC
# MAGIC **모델 개발이 전체 노력의 20%라면, 운영/유지보수가 80%입니다.**
# MAGIC MLOps 없이 모델을 배포하면, "처음엔 잘 작동하다가 3개월 후 성능이 급락"하는 현상을 경험하게 됩니다.
# MAGIC
# MAGIC ## 3.1 Feature Store — 피처(변수)의 중앙 관리
# MAGIC
# MAGIC Feature Store는 **ML 모델에 입력되는 피처(변수)를 중앙에서 관리** 하는 시스템입니다.
# MAGIC 제조 비유로, 각 설비의 센서 데이터를 **표준화된 형식으로 한곳에 모아놓는 창고** 입니다.
# MAGIC
# MAGIC 왜 필요한가? 실무에서 데이터 과학자의 **80% 이상의 시간이 데이터 준비** 에 소요됩니다.
# MAGIC Feature Store는 한번 가공한 피처를 **재사용 가능한 자산** 으로 관리하여 이 비효율을 해소합니다.
# MAGIC
# MAGIC | 기능 | 설명 | Databricks 지원 | 제조 적용 예 |
# MAGIC |------|------|----------------|-----------|
# MAGIC | **Offline Feature Store** | 배치 학습/추론용 피처 | Unity Catalog 테이블 | 일간 배치 고장 예측용 피처 |
# MAGIC | **Online Feature Store** | 실시간 서빙용 피처 (ms 단위 응답) | Online Tables | 실시간 센서 모니터링 피처 |
# MAGIC | **Feature Function** | 동적 피처 계산 (요청 시 계산) | Python UDF | 직전 10분 이동평균, 변화율 등 |
# MAGIC | **Point-in-Time Lookups** | 시점 기반 피처 조인 (데이터 누출 방지) | Feature Engineering Client | "고장 시점 1시간 전"의 센서 데이터만 정확히 조인 |
# MAGIC
# MAGIC ## 3.2 Model Monitoring — 모델 성능 자동 감시
# MAGIC
# MAGIC 배포된 모델은 시간이 지남에 따라 성능이 저하됩니다. 이를 **모델 드리프트(Model Drift)** 라 합니다.
# MAGIC 원인은 다양합니다: 원자재 변경, 계절적 환경 변화, 설비 노후화, 신규 제품 투입 등.
# MAGIC
# MAGIC | 기능 | 설명 | 제조 적용 가치 |
# MAGIC |------|------|-------------|
# MAGIC | **Data Quality Monitoring(구 Data Quality Monitoring)**| 자동 드리프트 탐지 + 대시보드 | 센서 데이터 분포 변화를 **자동 감지** 하여 알림 |
# MAGIC | **Inference Tables**| 서빙 엔드포인트의 입출력 자동 로깅 | 모든 예측 결과를 기록하여 **사후 분석** 가능 |
# MAGIC | **Custom Metrics**| 비즈니스 KPI 기반 커스텀 모니터링 | "월간 오탐률", "고장 미탐지율" 등 **비즈니스 의미 있는 지표** 추적 |
# MAGIC | **Alerts**| 임계값 초과 시 자동 알림 | Recall이 0.7 미만으로 떨어지면 **Slack/이메일 자동 알림** |
# MAGIC
# MAGIC ## 3.3 LLMOps / Agent-based MLOps — 2024년 최신 트렌드
# MAGIC
# MAGIC AI Agent가 MLOps 운영을 자동화하는 시대가 열리고 있습니다.
# MAGIC 예를 들어, "모델 성능이 저하되면 자동으로 재학습을 트리거하고, 새 모델이 기존보다 좋으면 자동 배포"하는
# MAGIC **완전 자동화 파이프라인** 이 가능해지고 있습니다.
# MAGIC
# MAGIC | 기법 | 설명 | 제조 적용 시나리오 |
# MAGIC |------|------|----------------|
# MAGIC | **MLOps Agent**| LLM이 MLOps 도구를 호출하여 자동 운영 | 드리프트 감지 → 데이터 분석 → 재학습 → 검증 → 배포 **전 과정 자동화** |
# MAGIC | **Compound AI Systems**| 여러 모델을 Agent가 조합하여 판단 | 센서 데이터(정형) + 외관 이미지(비정형) → **통합 품질 판정** |
# MAGIC | **MLflow Tracing**| LLM/Agent 호출 체인 추적 | Agent가 "왜 재학습을 결정했는지" **의사결정 과정 투명화** |
# MAGIC
# MAGIC > **미래 비전**: 궁극적으로 제조 MLOps는 "사람이 모델을 관리"하는 것에서
# MAGIC > "Agent가 모델을 관리하고, 사람은 비즈니스 목표만 설정"하는 방향으로 진화하고 있습니다.
# MAGIC > Databricks의 Mosaic AI Agent Framework가 이 비전을 현실화하고 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 4. 적용 권장 사항
# MAGIC
# MAGIC ## LG Innotek PoC 적용 로드맵 — 단계별 접근
# MAGIC
# MAGIC 아래 표는 **즉시 적용 가능한 기법부터 장기 목표까지** 우선순위를 정리한 것입니다.
# MAGIC 각 기법은 이전 단계의 성과 위에 쌓이도록 설계되었습니다.
# MAGIC
# MAGIC ### Phase 1: 빠른 성과 확보 (1~2주)
# MAGIC
# MAGIC | 우선순위 | 기법 | 적용 대상 | 기대 효과 | 난이도 | 소요 시간 |
# MAGIC |---------|------|----------|----------|--------|----------|
# MAGIC | 1 | **멀티 알고리즘 비교** | 정형 모델 | 데이터에 최적인 알고리즘 식별 | 낮음 | 2시간 |
# MAGIC | 2 | **Databricks AutoML** | 정형 모델 | 코드 없이 베이스라인 확보 | 낮음 | 30분 |
# MAGIC | 3 | **SMOTE-ENN** 불균형 처리 | 정형 모델 | Recall 5~15%p 향상 기대 | 낮음 | 1시간 |
# MAGIC
# MAGIC ### Phase 2: 성능 최적화 (2~4주)
# MAGIC
# MAGIC | 우선순위 | 기법 | 적용 대상 | 기대 효과 | 난이도 | 소요 시간 |
# MAGIC |---------|------|----------|----------|--------|----------|
# MAGIC | 4 | **Optuna HPO** | 정형 모델 | 최적 하이퍼파라미터로 F1 2~5%p 추가 향상 | 중간 | 반일 |
# MAGIC | 5 | **Stacking 앙상블** | 정형 모델 | 안정적인 1~3%p 추가 향상 | 중간 | 반일 |
# MAGIC | 6 | **PatchCore + EfficientAD** | 비정형 모델 | 외관 검사 정확도/속도 최적 모델 선정 | 중간 | 1일 |
# MAGIC
# MAGIC ### Phase 3: 운영 안정화 (1~3개월)
# MAGIC
# MAGIC | 우선순위 | 기법 | 적용 대상 | 기대 효과 | 난이도 | 소요 시간 |
# MAGIC |---------|------|----------|----------|--------|----------|
# MAGIC | 7 | **Data Quality Monitoring** | 운영 환경 | 모델 드리프트 자동 감지, 성능 저하 사전 대응 | 낮음 | 1일 |
# MAGIC | 8 | **Feature Store** | 데이터 파이프라인 | 피처 재사용, 학습/서빙 일관성 보장 | 중간 | 1주 |
# MAGIC | 9 | **MLOps Agent** | 운영 자동화 | 드리프트 → 재학습 → 배포 완전 자동화 | 높음 | 2주 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 핵심 메시지
# MAGIC
# MAGIC > **ML 프로젝트 성공의 열쇠는 "최신 알고리즘"이 아니라 "체계적인 실험 관리"입니다.**
# MAGIC > 아무리 좋은 알고리즘도 데이터 품질이 나쁘면 무용지물이고,
# MAGIC > 아무리 정확한 모델도 운영 환경에서 관리되지 않으면 3개월 후 쓸모없어집니다.
# MAGIC > Databricks의 Lakehouse 아키텍처는 데이터 관리(Delta Lake) + 실험 관리(MLflow) + 운영 관리(Model Serving)를
# MAGIC > **하나의 플랫폼에서 통합** 하여, 이 전체 생애주기를 지원합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 다음 실습 노트북
# MAGIC - [03b: 멀티 알고리즘 비교 학습]($./03b_multi_algorithm_comparison) — XGBoost, LightGBM, CatBoost, RF 동시 비교
# MAGIC - [03c: 고급 기법 적용]($./03c_advanced_techniques) — SMOTE, Optuna, Stacking, AutoML
