# Databricks notebook source
# MAGIC %md
# MAGIC # XGBoost 예지보전 모델 학습
# MAGIC
# MAGIC 본 노트북에서는 **XGBoost** 모델을 학습시키고, MLflow로 실험을 추적하며, SHAP을 통해 모델을 해석합니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC - **MLflow Experiment Tracking**: 파라미터, 메트릭, 아티팩트 자동 추적
# MAGIC - **MLflow Autolog**: 코드 변경 없이 학습 과정 자동 기록
# MAGIC - **Data Lineage**: 학습 데이터와 모델 간 계보 캡처
# MAGIC - **mlflow.evaluate()**: 자동화된 모델 평가 (혼동행렬, ROC, PR 곡선 등)

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost shap --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. MLflow 실험 설정
# MAGIC
# MAGIC MLflow 실험(Experiment)은 여러 번의 학습 실행(Run)을 그룹화하여 비교할 수 있게 해줍니다.
# MAGIC 워크스페이스의 사이드바에서 실험 결과를 실시간으로 확인할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,MLflow 실험 생성/설정
import mlflow

xp_name = "lgit_predictive_maintenance"
xp_path = f"/Users/{current_user}"
experiment_name = f"{xp_path}/{xp_name}"

try:
    experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
    print(f"기존 실험 사용: {experiment_name} (ID: {experiment_id})")
except:
    experiment_id = mlflow.create_experiment(
        name=experiment_name,
        tags={"project": "lgit-mlops-poc", "domain": "predictive-maintenance"}
    )
    print(f"새 실험 생성: {experiment_name} (ID: {experiment_id})")

mlflow.set_experiment(experiment_name)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. 데이터 계보 (Data Lineage) 캡처
# MAGIC
# MAGIC **MLflow Data Lineage**를 통해 모델이 어떤 데이터로 학습되었는지 추적합니다.
# MAGIC - Unity Catalog에서 테이블 버전을 기반으로 데이터셋 객체를 생성합니다.
# MAGIC - 이를 통해 모델 문제 발생 시 **근본 원인 분석(RCA)** 이 가능합니다.

# COMMAND ----------

# DBTITLE 1,학습 데이터셋 Lineage 객체 생성
# 최신 테이블 버전 확인
latest_version = max(
    spark.sql(f"DESCRIBE HISTORY {catalog}.{db}.lgit_pm_training").toPandas()["version"]
)

# MLflow 데이터셋 객체 생성 (Unity Catalog 테이블 + 버전)
src_dataset = mlflow.data.load_delta(
    table_name=f"{catalog}.{db}.lgit_pm_training",
    version=str(latest_version)
)

print(f"데이터 계보: {catalog}.{db}.lgit_pm_training @ version {latest_version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 학습 데이터 준비

# COMMAND ----------

# DBTITLE 1,학습 데이터 로드
feature_columns = [
    "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "temp_diff", "power", "tool_wear_rate", "strain",
    "overheat_flag", "product_quality", "risk_score"
]
label_col = "machine_failure"

# Train/Test 분할 데이터 로드
df_train = src_dataset.df.filter("split = 'train'").select(*feature_columns, label_col)
df_test = src_dataset.df.filter("split = 'test'").select(*feature_columns, label_col)

X_train = df_train.toPandas()
X_test = df_test.toPandas()

Y_train = X_train.pop(label_col)
Y_test = X_test.pop(label_col)

print(f"학습 데이터: {len(X_train)} rows, 테스트 데이터: {len(X_test)} rows")
print(f"고장 비율 - 학습: {Y_train.mean():.4f}, 테스트: {Y_test.mean():.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. XGBoost 모델 학습
# MAGIC
# MAGIC ### MLflow Autolog
# MAGIC `mlflow.xgboost.autolog()`을 사용하면 하이퍼파라미터, 학습 메트릭, 피처 중요도가 **자동으로** MLflow에 기록됩니다.
# MAGIC 코드를 수정할 필요 없이 모든 실험이 추적됩니다.

# COMMAND ----------

# DBTITLE 1,학습 함수 정의
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix, f1_score,
    roc_auc_score, precision_recall_curve, auc
)
from mlflow.models import infer_signature
import xgboost as xgb
import numpy as np


def train_xgboost(params, run_name="xgboost_baseline"):
    """
    XGBoost 모델을 학습하고 MLflow에 기록합니다.

    Args:
        params: XGBoost 하이퍼파라미터
        run_name: MLflow Run 이름
    """
    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name) as run:
        # Autolog 활성화 (모델 아티팩트는 수동 기록)
        mlflow.xgboost.autolog(log_models=False, silent=True)

        # 불균형 데이터 보정: scale_pos_weight
        n_neg = (Y_train == 0).sum()
        n_pos = (Y_train == 1).sum()
        scale_pos_weight = n_neg / n_pos if n_pos > 0 else 1.0

        # 검증 데이터 분할
        X_tr, X_val, Y_tr, Y_val = train_test_split(
            X_train, Y_train, test_size=0.2, random_state=42, stratify=Y_train
        )

        # XGBoost DMatrix 생성
        dtrain = xgb.DMatrix(X_tr, label=Y_tr, feature_names=feature_columns)
        dval = xgb.DMatrix(X_val, label=Y_val, feature_names=feature_columns)

        # 기본 파라미터 + 사용자 파라미터
        default_params = {
            "objective": "binary:logistic",
            "eval_metric": ["logloss", "auc", "error"],
            "scale_pos_weight": scale_pos_weight,
            "tree_method": "hist",
            "seed": 42
        }
        default_params.update(params)

        # 모델 학습
        model = xgb.train(
            default_params,
            dtrain,
            num_boost_round=params.get("num_boost_round", 200),
            evals=[(dtrain, "train"), (dval, "val")],
            early_stopping_rounds=20,
            verbose_eval=50
        )

        # 검증 세트 예측
        y_pred_proba = model.predict(dval)
        y_pred = (y_pred_proba > 0.5).astype(int)

        # 메트릭 계산 및 기록
        val_f1 = f1_score(Y_val, y_pred)
        val_auc = roc_auc_score(Y_val, y_pred_proba)
        precision, recall, _ = precision_recall_curve(Y_val, y_pred_proba)
        val_pr_auc = auc(recall, precision)

        mlflow.log_metrics({
            "val_f1_score": val_f1,
            "val_auc": val_auc,
            "val_pr_auc": val_pr_auc,
            "scale_pos_weight": scale_pos_weight
        })

        # 모델 Signature 생성 및 기록
        signature = infer_signature(X_tr, y_pred_proba)
        mlflow.xgboost.log_model(
            model, "xgboost_model",
            input_example=X_tr.iloc[:5],
            signature=signature
        )

        # 데이터 계보 기록
        mlflow.log_input(src_dataset, context="training-input")

        # 테스트 세트 평가 (mlflow.evaluate 활용)
        dtest = xgb.DMatrix(X_test, feature_names=feature_columns)
        test_pred = model.predict(dtest)
        test_pred_label = (test_pred > 0.5).astype(int)
        test_f1 = f1_score(Y_test, test_pred_label)
        test_auc = roc_auc_score(Y_test, test_pred)
        mlflow.log_metrics({"test_f1_score": test_f1, "test_auc": test_auc})

        # Classification Report 기록
        report = classification_report(Y_val, y_pred, target_names=["정상", "고장"])
        mlflow.log_text(report, "classification_report.txt")
        print(report)

        return {
            "model": model,
            "run": run,
            "val_f1": val_f1,
            "val_auc": val_auc,
            "test_f1": test_f1,
            "test_auc": test_auc
        }

# COMMAND ----------

# MAGIC %md
# MAGIC ### Baseline 모델 학습

# COMMAND ----------

# DBTITLE 1,Baseline XGBoost 학습
baseline_params = {
    "max_depth": 6,
    "learning_rate": 0.1,
    "n_estimators": 200,
    "num_boost_round": 200,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 5,
    "gamma": 0.1
}

result = train_xgboost(baseline_params, run_name="xgboost_baseline")
print(f"\n=== Baseline 결과 ===")
print(f"Val F1: {result['val_f1']:.4f}, Val AUC: {result['val_auc']:.4f}")
print(f"Test F1: {result['test_f1']:.4f}, Test AUC: {result['test_auc']:.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. 하이퍼파라미터 튜닝 (HPO)
# MAGIC
# MAGIC 다양한 파라미터 조합을 시도하여 최적의 모델을 찾습니다.
# MAGIC MLflow에 모든 실행이 자동 기록되므로, 실험 UI에서 비교할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,하이퍼파라미터 그리드 탐색
hpo_configs = [
    {"max_depth": 4, "learning_rate": 0.05, "num_boost_round": 300, "subsample": 0.7, "colsample_bytree": 0.7, "min_child_weight": 3, "gamma": 0.05},
    {"max_depth": 8, "learning_rate": 0.1, "num_boost_round": 200, "subsample": 0.9, "colsample_bytree": 0.9, "min_child_weight": 7, "gamma": 0.2},
    {"max_depth": 5, "learning_rate": 0.08, "num_boost_round": 250, "subsample": 0.85, "colsample_bytree": 0.85, "min_child_weight": 5, "gamma": 0.1},
]

best_result = result  # baseline부터 시작
for i, params in enumerate(hpo_configs):
    r = train_xgboost(params, run_name=f"xgboost_hpo_{i+1}")
    print(f"HPO #{i+1}: Val F1={r['val_f1']:.4f}, Val AUC={r['val_auc']:.4f}")
    if r['val_f1'] > best_result['val_f1']:
        best_result = r

print(f"\n=== 최적 모델 ===")
print(f"Run ID: {best_result['run'].info.run_id}")
print(f"Val F1: {best_result['val_f1']:.4f}, Test F1: {best_result['test_f1']:.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. SHAP 기반 모델 해석
# MAGIC
# MAGIC **SHAP (SHapley Additive exPlanations)** 을 통해 모델의 예측을 해석합니다.
# MAGIC - 피처 중요도 (Feature Importance)
# MAGIC - 개별 예측에 대한 피처 기여도
# MAGIC - 제조 현장에서 **왜 고장이 예측되었는지** 설명 가능

# COMMAND ----------

# DBTITLE 1,SHAP 값 계산 및 시각화
import shap

# 최적 모델로 SHAP 값 계산
best_model = best_result['model']
explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test)

# SHAP Summary Plot (피처 중요도)
print("=== SHAP Feature Importance (피처 중요도) ===")
shap.summary_plot(shap_values, X_test, feature_names=feature_columns, show=False)

import matplotlib.pyplot as plt
fig = plt.gcf()
fig.tight_layout()

# MLflow에 SHAP plot 기록
with mlflow.start_run(run_id=best_result['run'].info.run_id):
    mlflow.log_figure(fig, "shap_summary_plot.png")

plt.show()

# COMMAND ----------

# DBTITLE 1,개별 예측 해석 (고장 예측 사례)
# 고장으로 예측된 첫 번째 사례의 SHAP 해석
dtest = xgb.DMatrix(X_test, feature_names=feature_columns)
preds = best_model.predict(dtest)
failure_idx = np.where(preds > 0.5)[0]

if len(failure_idx) > 0:
    idx = failure_idx[0]
    print(f"=== 고장 예측 사례 #{idx} ===")
    print(f"예측 확률: {preds[idx]:.4f}")
    print(f"실제 레이블: {Y_test.iloc[idx]}")
    print(f"\n피처 기여도:")
    for feat, val, sv in sorted(
        zip(feature_columns, X_test.iloc[idx], shap_values[idx]),
        key=lambda x: abs(x[2]), reverse=True
    ):
        direction = "↑ 고장" if sv > 0 else "↓ 정상"
        print(f"  {feat:30s}: {val:10.2f} → SHAP {sv:+.4f} ({direction})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC 이 노트북에서 수행한 작업:
# MAGIC 1. **MLflow 실험 설정** 및 데이터 계보(Lineage) 캡처
# MAGIC 2. **XGBoost Baseline 모델** 학습 (불균형 보정 포함)
# MAGIC 3. **하이퍼파라미터 튜닝** (3개 조합 탐색)
# MAGIC 4. **SHAP 해석**: 피처 중요도 및 개별 예측 설명
# MAGIC 5. 모든 실험이 MLflow에 자동 기록됨
# MAGIC
# MAGIC **다음 단계:** [Unity Catalog 모델 등록]($./04_model_registration_uc)
