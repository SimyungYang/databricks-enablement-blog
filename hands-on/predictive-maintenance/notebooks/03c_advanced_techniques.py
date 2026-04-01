# Databricks notebook source
# MAGIC %md
# MAGIC # 고급 ML 기법 적용 (Advanced Techniques)
# MAGIC
# MAGIC 본 노트북에서는 예지보전 모델의 성능을 더욱 향상시키기 위한 **최신 ML 기법** 들을 적용합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 왜 고급 기법이 필요한가?
# MAGIC
# MAGIC 기본 ML 모델(03a, 03b)만으로도 일정 수준의 예측 성능을 확보할 수 있지만, **실제 제조 현장에서는 그것만으로 충분하지 않습니다.**
# MAGIC
# MAGIC 대표적인 문제:
# MAGIC - **불균형 데이터** : LG Innotek 카메라 모듈 라인에서 실제 불량률은 1~3% 수준. 모델이 "항상 정상"이라고 예측해도 정확도 97%가 나옴 → **불량을 하나도 못 잡으면서 높은 정확도를 보이는 착시 현상**
# MAGIC - **하이퍼파라미터 미최적화** : 모델의 수십 개 설정값(하이퍼파라미터)을 수동으로 조정하면, 최적 조합을 찾는 데 수 주가 소요될 수 있음
# MAGIC - **단일 모델의 한계** : 하나의 모델은 데이터의 특정 패턴만 잘 학습. 복합적인 고장 원인(열적 + 기계적 + 전기적)을 하나의 모델로 모두 포착하기 어려움
# MAGIC
# MAGIC 이 노트북의 고급 기법들은 이러한 문제를 **체계적으로 해결** 합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 적용 기법 목차
# MAGIC
# MAGIC | # | 기법 | 해결하는 문제 | 제조 현장 비유 |
# MAGIC |---|------|-------------|-------------|
# MAGIC | 1 | **SMOTE-ENN** | 불균형 데이터 (희소한 불량 샘플) | 불량품 사례 교육 자료를 인위적으로 늘려 교육 효과 극대화 |
# MAGIC | 2 | **Optuna HPO** | 하이퍼파라미터 최적화 | 공정 조건(온도, 압력, 시간)을 자동으로 최적화하는 것과 동일 |
# MAGIC | 3 | **Stacking Ensemble** | 단일 모델의 한계 | 여러 전문가(열/기계/전기)의 의견을 종합하여 최종 판단 |
# MAGIC | 4 | **Databricks AutoML** | ML 전문 인력 부족 | 코드 한 줄로 수십 개 알고리즘 자동 탐색, 노트북 코드까지 생성 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Databricks 플랫폼 활용
# MAGIC
# MAGIC | 기능 | 설명 | 이 노트북에서의 활용 |
# MAGIC |------|------|-------------------|
# MAGIC | **MLflow Tracking** | 모든 실험 결과 자동 기록 | 기법별 성능을 한눈에 비교, 최적 기법 선택 근거 확보 |
# MAGIC | **MLflow Nested Runs** | 부모-자식 Run 구조 | HPO 30회 시행을 구조적으로 정리 |
# MAGIC | **Databricks AutoML** | 자동 모델 탐색 | 15분 만에 베이스라인 확보, 생성된 코드로 추가 개선 |
# MAGIC | **Autolog** | 코드 변경 없이 기록 | 파라미터/메트릭/모델 아티팩트를 자동으로 MLflow에 저장 |
# MAGIC
# MAGIC > **Databricks 장점** : 위 4가지 고급 기법을 **하나의 플랫폼에서 통합 실행** 하고, 모든 실험 결과를 **MLflow로 일원화** 하여 관리할 수 있습니다. 타 플랫폼에서는 각 기법별로 별도 도구를 설치/관리해야 하는 번거로움이 있습니다.

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost lightgbm catboost imbalanced-learn "optuna-integration[mlflow]" optuna --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# DBTITLE 1,공통 데이터 로드
import mlflow
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import f1_score, roc_auc_score, classification_report

feature_columns = [
    "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "temp_diff", "power", "tool_wear_rate", "strain",
    "overheat_flag", "product_quality", "risk_score"
]
label_col = "machine_failure"

df = spark.table("lgit_pm_training")
train_pdf = df.filter("split = 'train'").select(*feature_columns, label_col).toPandas()
test_pdf = df.filter("split = 'test'").select(*feature_columns, label_col).toPandas()
X_train, Y_train = train_pdf[feature_columns], train_pdf[label_col]
X_test, Y_test = test_pdf[feature_columns], test_pdf[label_col]

# MLflow 실험 설정
xp_name = "lgit_advanced_techniques"
xp_path = f"/Users/{current_user}"
experiment_name = f"{xp_path}/{xp_name}"
try:
    experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
except:
    experiment_id = mlflow.create_experiment(name=experiment_name)
mlflow.set_experiment(experiment_name)

print(f"학습: {len(X_train)}건, 테스트: {len(X_test)}건")
print(f"고장 비율: {Y_train.mean():.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 기법 1: SMOTE-ENN (불균형 데이터 처리)
# MAGIC
# MAGIC ## 제조 현장의 근본 문제: 클래스 불균형
# MAGIC
# MAGIC 제조 환경에서 설비 고장이나 제품 불량은 **극히 드문 사건** 입니다.
# MAGIC LG Innotek 카메라 모듈 생산라인을 예로 들면:
# MAGIC
# MAGIC ```
# MAGIC 일일 생산량:   10,000개
# MAGIC 불량 발생:     100~300개 (1~3%)
# MAGIC 정상 제품:     9,700~9,900개 (97~99%)
# MAGIC ```
# MAGIC
# MAGIC 이 데이터를 그대로 ML 모델에 넣으면 어떻게 될까요?
# MAGIC
# MAGIC **모델은 "항상 정상"이라고 예측하는 것을 학습합니다.**
# MAGIC 왜냐하면 그것만으로도 정확도 97%를 달성할 수 있기 때문입니다.
# MAGIC 하지만 이 모델은 **불량을 단 하나도 잡지 못합니다** — 이것이 바로 **정확도의 함정(Accuracy Paradox)** 입니다.
# MAGIC
# MAGIC > **핵심** : 제조 현장에서 정말 중요한 것은 "정상을 정상으로 맞추는 것"이 아니라, **"불량을 불량으로 잡아내는 것(Recall)"** 입니다. 놓친 불량 하나가 고객 클레임, 리콜, 브랜드 이미지 훼손으로 이어질 수 있습니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 불균형 학습의 역사와 발전
# MAGIC
# MAGIC 이 문제를 해결하기 위해 ML 커뮤니티는 수십 년간 다양한 기법을 발전시켜 왔습니다:
# MAGIC
# MAGIC | 시기 | 기법 | 원리 | 한계 |
# MAGIC |------|------|------|------|
# MAGIC | 1990년대 | **Random Oversampling** | 소수 클래스를 단순 복제 | 과적합(Overfitting) 심화 |
# MAGIC | 2002 | **SMOTE** | 소수 클래스 사이를 보간하여 합성 샘플 생성 | 노이즈 영역에도 합성 샘플 생성 |
# MAGIC | 2005 | **Borderline-SMOTE** | 경계선 근처의 소수 클래스만 오버샘플링 | 경계선 정의가 어려움 |
# MAGIC | 2011 | **ADASYN** | 학습이 어려운 샘플 주변에 더 많은 합성 샘플 생성 | 극단적 노이즈 증폭 가능 |
# MAGIC | 2012+ | **SMOTE-ENN/SMOTE-Tomek** | 오버샘플링 + 노이즈 제거 결합 | 현재 실무 표준 |
# MAGIC | 2020+ | **Deep Learning 기반** | GAN, VAE로 합성 데이터 생성 | 정형 데이터에서는 과도한 복잡성 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## SMOTE란?
# MAGIC
# MAGIC **SMOTE (Synthetic Minority Over-sampling Technique)** 는 소수 클래스의 샘플을 **합성(Synthetic)** 하여
# MAGIC 클래스 균형을 맞추는 기법입니다. 단순 복제와 달리 **새로운 데이터 포인트를 생성** 하므로 과적합 위험이 낮습니다.
# MAGIC
# MAGIC ```
# MAGIC 원리 (공장 비유: 불량 사례 교육 자료 제작):
# MAGIC
# MAGIC 1. 기존 불량 사례(A) 하나를 선택
# MAGIC 2. 가장 유사한 불량 사례(B)를 k개 찾음
# MAGIC 3. A와 B 사이의 특성을 섞어 "새로운 불량 사례"를 생성
# MAGIC    → 실제로는 없었지만, 충분히 있을 법한 불량 사례
# MAGIC
# MAGIC 예시 (2D 공간):
# MAGIC   A(토크=50, 온도=310) --- 합성(토크=55, 온도=312) --- B(토크=60, 온도=315)
# MAGIC   (실제 고장 사례)                                        (실제 고장 사례)
# MAGIC
# MAGIC   → 합성 샘플: 토크 50~60, 온도 310~315 사이의 새로운 고장 시나리오
# MAGIC ```
# MAGIC
# MAGIC ## ENN이란?
# MAGIC
# MAGIC **ENN (Edited Nearest Neighbors)** 는 데이터에서 **노이즈(잘못 분류된 샘플)를 제거** 하는 기법입니다.
# MAGIC
# MAGIC 제조 현장 비유: 품질 데이터에는 **오기록(센서 오류, 수동 입력 실수)** 이 섞여 있습니다. ENN은 이러한 노이즈를 자동으로 찾아 제거합니다.
# MAGIC
# MAGIC - k-NN으로 각 샘플의 이웃 k개를 확인
# MAGIC - 이웃의 다수가 다른 클래스이면 → 해당 샘플은 **노이즈로 판단하여 제거**
# MAGIC - 예: "정상" 샘플인데 주변에 "고장" 샘플만 있다면 → 잘못 기록된 데이터일 가능성 높음
# MAGIC
# MAGIC ## SMOTE-ENN = SMOTE + ENN (현재 실무 표준)
# MAGIC
# MAGIC 두 기법을 결합하면 **상호 보완적 효과** 를 얻습니다:
# MAGIC 1. **SMOTE** 로 소수 클래스(불량)를 오버샘플링 → 학습 데이터 균형 확보
# MAGIC 2. **ENN** 으로 양쪽 클래스의 노이즈 제거 → 깨끗한 결정 경계 확보
# MAGIC → 결과: **깨끗하고 균형 잡힌** 학습 데이터 → 모델이 불량 패턴을 제대로 학습
# MAGIC
# MAGIC > **Databricks 장점** : `imbalanced-learn` 라이브러리가 Databricks 클러스터에서 원활히 동작하며, 대규모 데이터에서도 Spark DataFrame → Pandas 변환을 통해 효율적으로 처리할 수 있습니다. MLflow로 리샘플링 전후 데이터 분포를 기록하여 감사(Audit) 추적이 가능합니다.

# COMMAND ----------

# DBTITLE 1,SMOTE-ENN 적용
from imblearn.combine import SMOTEENN
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
import xgboost as xgb

print(f"원본 데이터 - 정상: {(Y_train==0).sum()}, 고장: {(Y_train==1).sum()}")

# SMOTE-ENN 적용
smote_enn = SMOTEENN(
    smote=SMOTE(sampling_strategy=0.5, k_neighbors=5, random_state=42),
    random_state=42
)
X_resampled, Y_resampled = smote_enn.fit_resample(X_train, Y_train)
print(f"SMOTE-ENN 후 - 정상: {(Y_resampled==0).sum()}, 고장: {(Y_resampled==1).sum()}")

# SMOTE-ENN 적용 데이터로 XGBoost 학습
with mlflow.start_run(run_name="SMOTE_ENN_XGBoost") as run:
    mlflow.log_param("technique", "SMOTE-ENN")
    mlflow.log_param("algorithm", "XGBoost")
    mlflow.log_param("original_size", len(X_train))
    mlflow.log_param("resampled_size", len(X_resampled))

    model_smote = xgb.XGBClassifier(
        max_depth=6, learning_rate=0.1, n_estimators=200,
        random_state=42, eval_metric="logloss", use_label_encoder=False
    )
    model_smote.fit(X_resampled, Y_resampled, verbose=False)

    test_pred = model_smote.predict(X_test)
    test_proba = model_smote.predict_proba(X_test)[:, 1]
    f1 = f1_score(Y_test, test_pred)
    auc_val = roc_auc_score(Y_test, test_proba)

    mlflow.log_metrics({"test_f1_score": f1, "test_auc": auc_val})
    print(f"\nSMOTE-ENN + XGBoost 결과:")
    print(classification_report(Y_test, test_pred, target_names=["정상", "고장"]))

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 기법 2: Optuna HPO (베이지안 하이퍼파라미터 최적화)
# MAGIC
# MAGIC ## 하이퍼파라미터란? — 공정 설정값과의 비유
# MAGIC
# MAGIC ML 모델에는 **데이터로부터 자동으로 학습되는 값(파라미터)** 과 **사람이 미리 정해줘야 하는 값(하이퍼파라미터)** 이 있습니다.
# MAGIC
# MAGIC ```
# MAGIC 제조 공정 비유:
# MAGIC
# MAGIC   제품 품질 = f(원자재 특성, 공정 설정값)
# MAGIC                 ↑ 입력 데이터       ↑ 하이퍼파라미터
# MAGIC
# MAGIC   카메라 모듈 렌즈 접합 공정의 "공정 설정값":
# MAGIC   - 접합 온도: 180℃? 200℃? 220℃?      → ML의 learning_rate
# MAGIC   - 접합 압력: 50kPa? 70kPa?           → ML의 max_depth
# MAGIC   - 경화 시간: 30초? 60초? 120초?        → ML의 n_estimators
# MAGIC   - UV 노출량: 100mJ? 200mJ?           → ML의 subsample
# MAGIC
# MAGIC   공정 설정값이 최적이 아니면 제품 품질이 떨어지듯이,
# MAGIC   하이퍼파라미터가 최적이 아니면 모델 성능이 떨어집니다.
# MAGIC ```
# MAGIC
# MAGIC ## 왜 하이퍼파라미터 튜닝이 중요한가?
# MAGIC
# MAGIC 같은 알고리즘(XGBoost)이라도 하이퍼파라미터에 따라 성능이 **F1 0.6 ~ 0.9까지 차이** 가 날 수 있습니다.
# MAGIC 하지만 XGBoost만 해도 주요 하이퍼파라미터가 **9개 이상** 이며, 가능한 조합은 **수십억 개** 에 달합니다.
# MAGIC 이것을 수작업으로 최적화하는 것은 사실상 불가능합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Optuna란?
# MAGIC
# MAGIC **Optuna** 는 2019년 일본 Preferred Networks가 개발한 **베이지안 최적화** 기반의 하이퍼파라미터 튜닝 프레임워크입니다. 현재 가장 널리 사용되는 HPO 도구 중 하나입니다.
# MAGIC
# MAGIC ### 탐색 전략 비교: Grid Search vs Random Search vs Optuna
# MAGIC
# MAGIC ```
# MAGIC Grid Search (격자 탐색):
# MAGIC   모든 조합을 빠짐없이 시도 → 확실하지만 매우 느림
# MAGIC   예: 9개 파라미터 × 각 5개 값 = 5^9 = 약 200만 번 시도 필요!
# MAGIC   → 현실적으로 불가능. 파라미터 2~3개일 때만 사용 가능.
# MAGIC
# MAGIC Random Search (무작위 탐색):
# MAGIC   랜덤하게 조합을 시도 → Grid보다 빠르지만 비효율적
# MAGIC   실제로 Grid Search보다 같은 시간 대비 더 좋은 결과를 내는 경우가 많음
# MAGIC   (Bergstra & Bengio, 2012 논문에서 입증)
# MAGIC
# MAGIC Optuna (TPE 베이지안 최적화):
# MAGIC   이전 시행 결과를 학습하여 다음 탐색점을 '지능적으로' 선택
# MAGIC
# MAGIC   시행 1: 랜덤 시도 → F1=0.65
# MAGIC   시행 2: 시행 1 결과를 분석, 더 좋을 것 같은 영역 탐색 → F1=0.72
# MAGIC   시행 3: 시행 1~2를 분석, 패턴을 파악하여 유망 영역 집중 → F1=0.78
# MAGIC   ...
# MAGIC   시행 30: 누적 학습으로 최적 영역에 수렴 → F1=0.88
# MAGIC
# MAGIC   → 30번의 시행으로 200만 번 Grid Search에 준하는 결과 달성!
# MAGIC ```
# MAGIC
# MAGIC > **제조 비유** : Grid Search는 공정 설정값을 모든 조합으로 시험하는 것(DOE Full Factorial). Optuna는 이전 시험 결과를 참고하여 다음 시험 조건을 지능적으로 선택하는 **적응형 실험 계획법** 과 같습니다.
# MAGIC
# MAGIC ### Optuna의 핵심 기능:
# MAGIC - **TPE (Tree-structured Parzen Estimator)** : 베이지안 최적화 알고리즘. 좋은 결과/나쁜 결과의 분포를 모델링하여 다음 탐색점을 결정
# MAGIC - **Pruning (조기 중단)** : 학습 도중 성능이 나쁜 시행을 조기 중단하여 **계산 비용 50% 이상 절감**
# MAGIC - **시각화** : 파라미터 중요도, 최적화 히스토리, 파라미터 간 상관관계 등 **내장 시각화** 제공
# MAGIC - **MLflow 연동** : 각 시행(trial)을 자동으로 MLflow Nested Run으로 기록 → 모든 실험 이력 추적
# MAGIC
# MAGIC > **Databricks 장점** : Optuna + MLflow 연동이 네이티브로 지원되어, 30회 시행의 모든 파라미터/메트릭이 MLflow에 자동 기록됩니다. MLflow UI에서 시행 간 비교, 파라미터-성능 상관관계 분석이 가능합니다. 또한 Databricks 클러스터의 분산 환경에서 Optuna의 병렬 시행도 지원됩니다.

# COMMAND ----------

# DBTITLE 1,Optuna HPO 실행
import optuna
from optuna_integration import MLflowCallback

# Optuna + MLflow 콜백 설정
mlflow_callback = MLflowCallback(
    tracking_uri=mlflow.get_tracking_uri(),
    metric_name="val_f1_score",
    create_experiment=False,
)

def objective(trial):
    """
    Optuna가 최적화할 목적 함수입니다.
    각 시행(trial)에서 하이퍼파라미터를 제안받고, 모델을 학습하여 F1 Score를 반환합니다.
    """
    # 하이퍼파라미터 탐색 공간 정의
    params = {
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "gamma": trial.suggest_float("gamma", 0.0, 0.5),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.0, 1.0),
    }

    # 학습 데이터 분할
    X_tr, X_val, Y_tr, Y_val = train_test_split(
        X_train, Y_train, test_size=0.2, random_state=42, stratify=Y_train
    )

    model = xgb.XGBClassifier(
        **params,
        scale_pos_weight=(Y_train == 0).sum() / (Y_train == 1).sum(),
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False,
    )
    model.fit(X_tr, Y_tr, eval_set=[(X_val, Y_val)], verbose=False)

    val_pred = model.predict(X_val)
    return f1_score(Y_val, val_pred)

# Optuna Study 생성 및 최적화
with mlflow.start_run(run_name="Optuna_HPO_XGBoost") as parent_run:
    mlflow.log_param("technique", "Optuna_HPO")
    mlflow.log_param("n_trials", 30)

    study = optuna.create_study(
        direction="maximize",
        study_name="lgit_pm_xgboost_hpo",
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner()
    )

    study.optimize(objective, n_trials=30, show_progress_bar=True)

    # 최적 결과 기록
    mlflow.log_params({f"best_{k}": v for k, v in study.best_params.items()})
    mlflow.log_metric("best_val_f1_score", study.best_value)

    print(f"\n=== Optuna HPO 결과 ===")
    print(f"최적 F1 Score: {study.best_value:.4f}")
    print(f"최적 파라미터:")
    for k, v in study.best_params.items():
        print(f"  {k}: {v}")

# COMMAND ----------

# DBTITLE 1,Optuna 최적 파라미터로 최종 모델 학습
with mlflow.start_run(run_name="Optuna_Best_XGBoost") as run:
    mlflow.log_param("technique", "Optuna_HPO_best")

    best_model = xgb.XGBClassifier(
        **study.best_params,
        scale_pos_weight=(Y_train == 0).sum() / (Y_train == 1).sum(),
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False,
    )
    best_model.fit(X_train, Y_train, verbose=False)

    test_pred = best_model.predict(X_test)
    test_proba = best_model.predict_proba(X_test)[:, 1]
    optuna_f1 = f1_score(Y_test, test_pred)
    optuna_auc = roc_auc_score(Y_test, test_proba)

    mlflow.log_metrics({"test_f1_score": optuna_f1, "test_auc": optuna_auc})
    print(f"Optuna 최적 모델 - Test F1: {optuna_f1:.4f}, AUC: {optuna_auc:.4f}")
    print(classification_report(Y_test, test_pred, target_names=["정상", "고장"]))

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 기법 3: Stacking Ensemble (스태킹 앙상블)
# MAGIC
# MAGIC ## 앙상블의 핵심 철학: "여러 전문가의 의견을 종합하면 한 명의 의견보다 낫다"
# MAGIC
# MAGIC 제조 현장에서 복잡한 불량 원인을 분석할 때, 한 명의 엔지니어보다 **여러 분야 전문가가 함께 논의** 하면 더 정확한 판단을 내릴 수 있습니다. ML에서의 앙상블도 동일한 원리입니다.
# MAGIC
# MAGIC ```
# MAGIC 제조 비유:
# MAGIC
# MAGIC   [카메라 모듈 불량 판정 회의]
# MAGIC
# MAGIC   열 전문가:  "열화상 패턴으로 보면 접합 불량 가능성 70%"     → XGBoost
# MAGIC   기계 전문가: "진동 데이터로 보면 접합 불량 가능성 60%"      → LightGBM
# MAGIC   전기 전문가: "전기 특성으로 보면 접합 불량 가능성 80%"      → CatBoost
# MAGIC
# MAGIC   품질 팀장(메타 모델): 세 전문가의 의견을 종합적으로 고려하여 최종 판정
# MAGIC   → "접합 불량 확률 75%" (각 전문가의 신뢰도를 가중 반영)
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 앙상블 기법의 발전 역사
# MAGIC
# MAGIC | 시기 | 기법 | 원리 |
# MAGIC |------|------|------|
# MAGIC | 1990 | **Bagging** (Random Forest) | 같은 알고리즘을 다른 데이터 부분집합으로 학습, 다수결 투표 |
# MAGIC | 1997 | **Boosting** (AdaBoost, XGBoost) | 이전 모델이 틀린 샘플에 가중치를 주며 순차 학습 |
# MAGIC | 1992 | **Stacking**| 서로 다른 알고리즘의 예측을 메타 모델이 결합 ← **이 노트북에서 사용** |
# MAGIC | 2017 | **Blending** | Stacking의 간소화 버전 (교차 검증 대신 Hold-out 사용) |
# MAGIC
# MAGIC Kaggle 등 ML 경진대회에서 상위 솔루션의 **90% 이상이 앙상블** 을 사용합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Stacking이란?
# MAGIC
# MAGIC **Stacking** 은 **서로 다른 알고리즘** 의 예측을 **메타 모델(Meta-Learner)** 이 최종 결합하는 2단계 앙상블 기법입니다.
# MAGIC
# MAGIC **1단계: Base Learners** - 각기 다른 관점으로 데이터 분석
# MAGIC
# MAGIC 입력 데이터 X (센서 12개 피처)
# MAGIC - → **XGBoost** → 예측 확률 P1 (트리 분할 기반, 피처 상호작용에 강함)
# MAGIC - → **LightGBM** → 예측 확률 P2 (리프 중심 분할, 대규모 데이터에 빠름)
# MAGIC - → **CatBoost** → 예측 확률 P3 (순서 기반 부스팅, 과적합에 강함)
# MAGIC
# MAGIC **2단계: Meta-Learner** - 전문가 의견 종합
# MAGIC - → [P1, P2, P3] → **Logistic Regression** → 최종 예측 (각 모델의 신뢰도를 학습하여 가중 결합)
# MAGIC
# MAGIC ### 왜 효과적인가?
# MAGIC - 각 모델(XGBoost, LightGBM, CatBoost)이 데이터의 **다른 패턴** 을 학습합니다 — 같은 Gradient Boosting 계열이지만 트리 구축 방식이 서로 다르므로 **상호 보완적** 입니다
# MAGIC - 메타 모델이 "어떤 상황에서 어떤 모델의 예측이 더 정확한지"를 학습하여 **각 모델의 강점을 최적 조합** 합니다
# MAGIC - 단일 모델보다 **분산(variance)이 낮아** 안정적이고 일관된 예측 성능을 보입니다
# MAGIC
# MAGIC ### 데이터 누출(Leakage) 방지: 교차 검증의 중요성
# MAGIC - Base Learner가 학습 데이터 전체로 예측하면, 메타 모델이 "답을 미리 본" 것과 같음 → **과적합**
# MAGIC - **5-Fold 교차 검증** 으로 메타 모델 학습 데이터를 생성하여 이 문제를 해결
# MAGIC - scikit-learn의 `StackingClassifier`가 이를 자동으로 처리합니다
# MAGIC
# MAGIC > **Databricks 장점** : Stacking은 Base Learner 3개 x 5-Fold = 15번의 모델 학습이 필요하여 계산량이 큽니다. Databricks 클러스터의 `n_jobs=-1` 옵션으로 **병렬 처리** 하면 학습 시간을 대폭 단축할 수 있습니다. MLflow에 전체 Stacking 모델을 하나의 아티팩트로 저장하여 배포 시 복잡성을 제거합니다.

# COMMAND ----------

# DBTITLE 1,Stacking Ensemble 구현
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression
import lightgbm as lgb
from catboost import CatBoostClassifier

with mlflow.start_run(run_name="Stacking_Ensemble") as run:
    mlflow.log_param("technique", "Stacking_Ensemble")
    mlflow.log_param("base_learners", "XGBoost, LightGBM, CatBoost")
    mlflow.log_param("meta_learner", "LogisticRegression")

    # 불균형 가중치
    sw = (Y_train == 0).sum() / (Y_train == 1).sum()

    # Base Learners 정의
    estimators = [
        ('xgboost', xgb.XGBClassifier(
            max_depth=6, learning_rate=0.1, n_estimators=150,
            scale_pos_weight=sw, random_state=42, eval_metric="logloss",
            use_label_encoder=False, verbosity=0)),
        ('lightgbm', lgb.LGBMClassifier(
            max_depth=6, learning_rate=0.1, n_estimators=150,
            scale_pos_weight=sw, random_state=42, verbose=-1)),
        ('catboost', CatBoostClassifier(
            depth=6, learning_rate=0.1, iterations=150,
            auto_class_weights="Balanced", random_seed=42, verbose=0)),
    ]

    # Stacking Classifier (메타 모델: Logistic Regression)
    stacking_model = StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(max_iter=1000, random_state=42),
        cv=5,  # 5-fold 교차검증으로 메타 피처 생성
        stack_method='predict_proba',  # 확률값을 메타 피처로 사용
        n_jobs=-1
    )

    print("Stacking Ensemble 학습 중... (교차 검증 포함, 시간 소요)")
    stacking_model.fit(X_train, Y_train)

    # 평가
    test_pred = stacking_model.predict(X_test)
    test_proba = stacking_model.predict_proba(X_test)[:, 1]
    stack_f1 = f1_score(Y_test, test_pred)
    stack_auc = roc_auc_score(Y_test, test_proba)

    mlflow.log_metrics({"test_f1_score": stack_f1, "test_auc": stack_auc})

    from mlflow.models import infer_signature
    signature = infer_signature(X_train, stacking_model.predict(X_train))
    mlflow.sklearn.log_model(stacking_model, "model", signature=signature)

    print(f"\nStacking Ensemble 결과:")
    print(f"  Test F1: {stack_f1:.4f}, Test AUC: {stack_auc:.4f}")
    print(classification_report(Y_test, test_pred, target_names=["정상", "고장"]))

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 기법 4: Databricks AutoML
# MAGIC
# MAGIC ## AutoML이란?
# MAGIC
# MAGIC **AutoML (Automated Machine Learning)** 은 ML 모델 개발의 전 과정 — 데이터 전처리, 피처 엔지니어링, 알고리즘 선택, 하이퍼파라미터 튜닝 — 을 **자동으로** 수행하는 기술입니다.
# MAGIC
# MAGIC ### AutoML의 발전 역사
# MAGIC
# MAGIC | 시기 | 도구 | 특징 |
# MAGIC |------|------|------|
# MAGIC | 2013 | **Auto-WEKA** | 최초의 AutoML. 알고리즘 선택 + HPO 자동화 |
# MAGIC | 2016 | **Auto-sklearn** | scikit-learn 기반, 메타 학습으로 탐색 효율화 |
# MAGIC | 2018 | **Google AutoML** | 클라우드 기반, 딥러닝 특화. 완전 블랙박스 |
# MAGIC | 2019 | **H2O AutoML** | 오픈소스, 다양한 알고리즘 지원 |
# MAGIC | 2020+ | **Databricks AutoML**| Glass-box 접근. 코드 생성 + MLflow 통합 ← **이 노트북에서 사용** |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Databricks AutoML이 특별한 이유: Glass-box 접근
# MAGIC
# MAGIC 대부분의 AutoML 도구는 **블랙박스** 입니다. 결과는 나오지만 "왜 이 모델이 선택되었는지", "어떤 전처리가 적용되었는지" 알 수 없습니다. 이는 제조 현장에서 큰 문제입니다 — **품질 감사(Audit)나 규제 대응 시 모델의 작동 원리를 설명해야 하기 때문** 입니다.
# MAGIC
# MAGIC ```
# MAGIC 블랙박스 AutoML (Google, Azure 등):
# MAGIC   데이터 → [???] → 모델
# MAGIC   "결과는 좋은데, 어떻게 만들어졌는지 모릅니다"
# MAGIC   → 규제 대응 불가, 커스터마이징 불가
# MAGIC
# MAGIC Databricks AutoML (Glass-box):
# MAGIC   데이터 → [자동 탐색] → 모델 + 학습 노트북 코드
# MAGIC   "이 모델은 XGBoost 기반이며, 이런 전처리와 이런 파라미터로 학습되었습니다"
# MAGIC   "생성된 노트북을 열어서 코드를 직접 확인하고 수정할 수 있습니다"
# MAGIC   → 완전한 투명성, 자유로운 커스터마이징
# MAGIC ```
# MAGIC
# MAGIC ### Databricks AutoML의 핵심 기능:
# MAGIC - **코드 한 줄** (`automl.classify()`)로 XGBoost, LightGBM, Random Forest, Logistic Regression 등 **자동 탐색**
# MAGIC - 결과를 **MLflow 실험** 으로 자동 기록 → 모든 시행의 파라미터/메트릭 추적
# MAGIC - 최적 모델의 **학습 코드가 담긴 Databricks 노트북** 을 자동 생성 → 코드를 열어 검토/수정 가능
# MAGIC - 데이터 **탐색(EDA) 노트북** 도 자동 생성 → 피처 분포, 상관관계, 결측값 분석 포함
# MAGIC - **불균형 데이터 자동 처리** : class_weight, sample_weight를 자동 적용
# MAGIC
# MAGIC ### 실무 활용 전략:
# MAGIC - **빠른 프로토타이핑** : ML 전문가 없이도 15분 만에 베이스라인 모델 확보 → "AI/ML 도입이 가능한가?"에 대한 빠른 답변
# MAGIC - **알고리즘 선택 가이드** : AutoML이 추천하는 알고리즘/파라미터를 출발점으로, 도메인 지식을 반영하여 개선
# MAGIC - **교육 도구** : 생성된 노트북이 ML 코드 작성법의 교과서 역할 — LG Innotek 엔지니어분들이 ML을 배우는 데 최적의 참고 자료
# MAGIC
# MAGIC > **Databricks 장점** : AutoML은 Databricks 플랫폼에서만 제공하는 고유 기능입니다. Unity Catalog의 테이블을 직접 입력으로 받고, 결과를 MLflow에 자동 기록하며, 생성된 노트북을 바로 실행할 수 있는 **완전한 통합 경험** 을 제공합니다.

# COMMAND ----------

# DBTITLE 1,Databricks AutoML 실행
# AutoML은 Classic Compute 환경에서 실행 가능합니다.
# Serverless 환경에서는 제한될 수 있으므로 try-except로 처리합니다.
try:
    from databricks import automl

    # AutoML 분류 실행
    # timeout_minutes를 조절하여 탐색 시간을 제어할 수 있습니다.
    summary = automl.classify(
        dataset=spark.table("lgit_pm_training").filter("split = 'train'").select(*feature_columns, label_col),
        target_col=label_col,
        primary_metric="f1",
        timeout_minutes=15,  # 최대 15분 탐색
        experiment_name=f"{xp_path}/lgit_automl_pm",
    )

    # 결과 확인
    print(f"\n=== Databricks AutoML 결과 ===")
    print(f"최적 모델 Run: {summary.best_trial.mlflow_run_id}")
    print(f"최적 F1 Score: {summary.best_trial.metrics.get('val-f1_score', 'N/A')}")
    print(f"\n생성된 노트북 경로:")
    print(f"  베스트 모델: {summary.best_trial.notebook_path}")
    print(f"  데이터 탐색: {summary.output_table_name}")
    automl_available = True
except ImportError:
    print("참고: AutoML은 Classic Compute (All-Purpose Cluster)에서만 실행 가능합니다.")
    print("Serverless 환경에서는 아래 코드를 Classic 클러스터의 노트북에서 실행하세요:")
    print()
    print("  from databricks import automl")
    print("  summary = automl.classify(")
    print("      dataset=spark.table('lgit_pm_training'),")
    print("      target_col='machine_failure',")
    print("      primary_metric='f1',")
    print("      timeout_minutes=15")
    print("  )")
    automl_available = False

# COMMAND ----------

# MAGIC %md
# MAGIC ## 전체 기법 비교 요약
# MAGIC
# MAGIC 지금까지 4가지 고급 기법을 동일한 데이터(AI4I 예지보전)에 적용했습니다.
# MAGIC 아래 코드에서 **각 기법의 F1 Score와 AUC를 비교** 하여, 어떤 기법이 가장 효과적인지 확인합니다.
# MAGIC
# MAGIC > **참고** : 각 기법은 독립적으로 적용할 수도 있고, **조합** 할 수도 있습니다. 예를 들어 "SMOTE-ENN으로 데이터 균형 → Optuna로 파라미터 최적화 → Stacking으로 앙상블"처럼 **3단 콤보** 를 구성하면 최고 성능을 기대할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,전체 기법 비교
results_summary = {
    "SMOTE-ENN + XGBoost": {"f1": f1, "auc": auc_val},
    "Optuna HPO + XGBoost": {"f1": optuna_f1, "auc": optuna_auc},
    "Stacking Ensemble": {"f1": stack_f1, "auc": stack_auc},
}

print("=" * 60)
print("              고급 기법 비교 결과")
print("=" * 60)
for name, metrics in results_summary.items():
    print(f"  {name:30s}: F1={metrics['f1']:.4f}, AUC={metrics['auc']:.4f}")
print("=" * 60)

best_technique = max(results_summary, key=lambda x: results_summary[x]['f1'])
print(f"\n최적 기법: {best_technique} (F1: {results_summary[best_technique]['f1']:.4f})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC ### 학습한 내용
# MAGIC
# MAGIC | 기법 | 해결 문제 | 핵심 원리 | 제조 현장 가치 |
# MAGIC |------|----------|----------|-------------|
# MAGIC | **SMOTE-ENN** | 불균형 데이터 | 합성 오버샘플링 + 노이즈 제거 | 희소한 불량 사례를 효과적으로 학습 |
# MAGIC | **Optuna HPO** | 파라미터 최적화 | 베이지안 최적화 (TPE) | 수작업 대비 10배 빠른 최적 조건 탐색 |
# MAGIC | **Stacking** | 단일 모델 한계 | 여러 모델 + 메타 모델 결합 | 복합적 고장 원인을 다각도로 분석 |
# MAGIC | **AutoML** | 전문 인력 부족 | 알고리즘/파라미터 자동 최적화 | ML 비전문가도 15분 만에 모델 생성 |
# MAGIC
# MAGIC ### LG Innotek 실무 적용 가이드 (권장 순서)
# MAGIC
# MAGIC 1. **Step 1: AutoML로 빠른 베이스라인 확보 (15분)** — "이 데이터로 AI/ML이 가능한가?" 빠르게 검증
# MAGIC 1. **Step 2: AutoML 결과를 참고하여 멀티 알고리즘 비교 (03b)** — 추천된 알고리즘 중 도메인에 적합한 것 선택
# MAGIC 1. **Step 3: SMOTE-ENN으로 데이터 균형 + Optuna HPO로 파라미터 최적화** — 불량 탐지 성능(Recall/F1)을 극대화
# MAGIC 1. **Step 4: Stacking으로 최종 앙상블 구성** — 안정적이고 일관된 예측 성능 확보 → 운영 환경 배포
# MAGIC
# MAGIC ### 최신 트렌드 (참고)
# MAGIC
# MAGIC - **Foundation Model Fine-tuning** : GPT-4, LLaMA 등 대규모 언어 모델을 정형 데이터 분류에 활용하는 연구 진행 중 (TabPFN, 2023)
# MAGIC - **Neural Architecture Search (NAS)** : 신경망 구조 자체를 자동 설계하는 기술
# MAGIC - **Self-supervised Pre-training for Tabular Data** : 정형 데이터에 자기 지도 학습을 적용하여 레이블 없이도 피처 표현을 학습 (SAINT, TabNet)
# MAGIC - **Causal ML** : 상관관계를 넘어 인과관계를 학습하는 모델 → "이 공정 조건을 변경하면 불량률이 얼마나 줄어드는가?"
# MAGIC
# MAGIC **다음 단계:** [04: 모델 등록]($./04_model_registration_uc)으로 최적 모델을 UC에 등록합니다.
