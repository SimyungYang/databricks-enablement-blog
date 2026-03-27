# Databricks notebook source
# MAGIC %md
# MAGIC # 고급 ML 기법 적용 (Advanced Techniques)
# MAGIC
# MAGIC 본 노트북에서는 예지보전 모델의 성능을 더욱 향상시키기 위한 **최신 ML 기법**들을 적용합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 적용 기법 목차
# MAGIC 1. **SMOTE-ENN**: 불균형 데이터 처리 (오버샘플링 + 노이즈 제거)
# MAGIC 2. **Optuna HPO**: 베이지안 최적화 기반 하이퍼파라미터 튜닝
# MAGIC 3. **Stacking Ensemble**: 여러 모델의 예측을 결합하는 앙상블
# MAGIC 4. **Databricks AutoML**: 자동 머신러닝으로 빠른 베이스라인 확보
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Databricks 기능 활용
# MAGIC
# MAGIC | 기능 | 설명 | 이 노트북에서의 활용 |
# MAGIC |------|------|-------------------|
# MAGIC | **MLflow Tracking** | 모든 실험 결과 자동 기록 | 기법별 성능 비교 |
# MAGIC | **MLflow Nested Runs** | 부모-자식 Run 구조 | HPO의 개별 시행 기록 |
# MAGIC | **Databricks AutoML** | 자동 모델 탐색 | 베이스라인 빠른 확보 |
# MAGIC | **Autolog** | 코드 변경 없이 기록 | 생산성 향상 |

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
# MAGIC ## SMOTE란?
# MAGIC
# MAGIC **SMOTE (Synthetic Minority Over-sampling Technique)** 는 소수 클래스의 샘플을 **합성**하여
# MAGIC 클래스 균형을 맞추는 기법입니다.
# MAGIC
# MAGIC ```
# MAGIC 원리:
# MAGIC 1. 소수 클래스(고장) 샘플 하나를 선택
# MAGIC 2. 가장 가까운 k개의 이웃 중 하나를 랜덤 선택
# MAGIC 3. 두 샘플 사이의 선분 위에 새로운 합성 샘플 생성
# MAGIC
# MAGIC 예시 (2D):
# MAGIC   A(1,1) ---- 합성 샘플(1.5, 1.3) ---- B(2,1.5)
# MAGIC   (원본)                                 (이웃)
# MAGIC ```
# MAGIC
# MAGIC ## ENN이란?
# MAGIC
# MAGIC **ENN (Edited Nearest Neighbors)** 는 다수 클래스에서 **노이즈 샘플을 제거**하는 기법입니다.
# MAGIC - k-NN으로 각 샘플의 이웃을 확인
# MAGIC - 이웃의 다수가 다른 클래스이면 해당 샘플 제거
# MAGIC
# MAGIC ## SMOTE-ENN = SMOTE + ENN
# MAGIC
# MAGIC 두 기법을 결합하면:
# MAGIC 1. SMOTE로 소수 클래스를 오버샘플링
# MAGIC 2. ENN으로 양쪽 클래스의 노이즈 제거
# MAGIC → **깨끗하고 균형 잡힌** 학습 데이터 확보

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
# MAGIC ## Optuna란?
# MAGIC
# MAGIC **Optuna**는 **베이지안 최적화** 기반의 하이퍼파라미터 튜닝 프레임워크입니다.
# MAGIC
# MAGIC ### Grid Search vs Random Search vs Optuna
# MAGIC
# MAGIC ```
# MAGIC Grid Search:  모든 조합을 다 시도 → 확실하지만 느림
# MAGIC               [1,2,3] × [a,b,c] = 9번 시도
# MAGIC
# MAGIC Random Search: 랜덤하게 시도 → 빠르지만 최적해 보장 안 됨
# MAGIC               랜덤으로 N번 시도
# MAGIC
# MAGIC Optuna (TPE): 이전 결과를 학습하여 다음 탐색점을 '지능적으로' 선택
# MAGIC               1번째: 랜덤 시도
# MAGIC               2번째: 1번째 결과를 보고 더 좋을 것 같은 영역 탐색
# MAGIC               3번째: 1~2번째 결과를 보고 더 좋을 것 같은 영역 탐색
# MAGIC               ...
# MAGIC               → 적은 시행으로 최적해에 근접!
# MAGIC ```
# MAGIC
# MAGIC ### Optuna의 장점:
# MAGIC - **Pruning**: 성능이 나쁜 시행을 조기 중단하여 시간 절약
# MAGIC - **시각화**: 파라미터 중요도, 최적화 히스토리 등 내장 시각화
# MAGIC - **MLflow 연동**: 각 시행을 자동으로 MLflow Run으로 기록

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
# MAGIC ## Stacking이란?
# MAGIC
# MAGIC **Stacking**은 여러 모델의 예측을 **메타 모델**이 결합하는 앙상블 기법입니다.
# MAGIC
# MAGIC ```
# MAGIC 입력 데이터 X
# MAGIC     │
# MAGIC     ├─→ [XGBoost]   → 예측 P1
# MAGIC     ├─→ [LightGBM]  → 예측 P2
# MAGIC     ├─→ [CatBoost]  → 예측 P3
# MAGIC     │
# MAGIC     └─→ [P1, P2, P3] → [메타 모델 (Logistic Regression)] → 최종 예측
# MAGIC ```
# MAGIC
# MAGIC ### 왜 효과적인가?
# MAGIC - 각 모델이 데이터의 **다른 패턴**을 학습
# MAGIC - 메타 모델이 각 모델의 **강점을 조합**
# MAGIC - 단일 모델보다 **일관되게 높은 성능**
# MAGIC
# MAGIC ### 주의점:
# MAGIC - **교차 검증(Cross-Validation)** 을 사용하여 메타 모델 학습 데이터 생성
# MAGIC   → 데이터 누출(Leakage) 방지
# MAGIC - scikit-learn의 `StackingClassifier`가 이를 자동으로 처리

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
# MAGIC **AutoML (Automated Machine Learning)** 은 모델 선택, 하이퍼파라미터 튜닝, 피처 엔지니어링을
# MAGIC **자동으로** 수행하는 기술입니다.
# MAGIC
# MAGIC ### Databricks AutoML의 특징:
# MAGIC - **코드 한 줄**로 여러 알고리즘을 자동 탐색
# MAGIC - 결과를 **MLflow 실험**으로 자동 기록
# MAGIC - 최적 모델의 **학습 코드가 담긴 노트북**을 자동 생성
# MAGIC   → "블랙박스"가 아님! 생성된 코드를 검토하고 수정 가능
# MAGIC - 데이터 사이언티스트가 없는 팀도 **빠르게 시작** 가능
# MAGIC
# MAGIC ### 언제 사용하나요?
# MAGIC - **빠른 프로토타이핑**: 30분 내 베이스라인 확보
# MAGIC - **알고리즘 선택 가이드**: AutoML이 추천하는 알고리즘을 출발점으로
# MAGIC - **비전문가 활용**: ML 전문지식 없이도 모델 생성 가능

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
# MAGIC ### 학습한 내용:
# MAGIC
# MAGIC | 기법 | 목적 | 핵심 원리 |
# MAGIC |------|------|----------|
# MAGIC | **SMOTE-ENN** | 불균형 처리 | 합성 오버샘플링 + 노이즈 제거 |
# MAGIC | **Optuna HPO** | 파라미터 최적화 | 베이지안 최적화 (TPE) |
# MAGIC | **Stacking** | 앙상블 | 여러 모델 + 메타 모델 결합 |
# MAGIC | **AutoML** | 자동 탐색 | 알고리즘/파라미터 자동 최적화 |
# MAGIC
# MAGIC ### 실무 적용 가이드:
# MAGIC 1. **먼저 AutoML**로 빠른 베이스라인 확보 (15분)
# MAGIC 2. AutoML 결과를 참고하여 **멀티 알고리즘 비교** (03b)
# MAGIC 3. 선택된 알고리즘에 **SMOTE + Optuna HPO** 적용
# MAGIC 4. 최종적으로 **Stacking**으로 성능 극대화
# MAGIC
# MAGIC **다음 단계:** [04: 모델 등록]($./04_model_registration_uc)으로 최적 모델을 UC에 등록합니다.
