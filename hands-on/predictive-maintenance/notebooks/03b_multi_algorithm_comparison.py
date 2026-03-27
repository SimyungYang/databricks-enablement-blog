# Databricks notebook source
# MAGIC %md
# MAGIC # 멀티 알고리즘 비교 학습 (Multi-Algorithm Comparison)
# MAGIC
# MAGIC 본 노트북에서는 **동일한 데이터셋**에 대해 **4가지 알고리즘**을 학습하고,
# MAGIC MLflow의 실험 추적 기능을 활용하여 **공정하게 비교**합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 왜 여러 알고리즘을 비교해야 하나요?
# MAGIC
# MAGIC > **"No Free Lunch Theorem"**: 모든 문제에 최적인 단일 알고리즘은 존재하지 않습니다.
# MAGIC
# MAGIC 데이터의 특성(크기, 피처 유형, 불균형 정도 등)에 따라 각 알고리즘의 성능이 달라집니다.
# MAGIC 따라서 여러 알고리즘을 동일 조건에서 비교하여 **최적의 모델**을 선택해야 합니다.
# MAGIC
# MAGIC ### 비교 대상 알고리즘
# MAGIC
# MAGIC | 알고리즘 | 핵심 원리 | 특징 |
# MAGIC |----------|----------|------|
# MAGIC | **XGBoost** | Gradient Boosting + 정규화 | 산업 표준, 안정적 성능 |
# MAGIC | **LightGBM** | Leaf-wise 성장 + GOSS | 대용량 데이터에서 빠름 |
# MAGIC | **CatBoost** | Ordered Boosting + 범주형 자동 처리 | 범주형 피처에 강함 |
# MAGIC | **Random Forest** | 배깅 (Bagging) + 랜덤 피처 선택 | 해석 쉬움, 과적합에 강함 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Databricks 기능 활용
# MAGIC
# MAGIC | 기능 | 설명 | 왜 중요한가? |
# MAGIC |------|------|-------------|
# MAGIC | **MLflow Experiment** | 모든 학습 실행을 자동 기록 | 실험 결과 재현 및 비교 가능 |
# MAGIC | **MLflow Autolog** | 코드 변경 없이 파라미터/메트릭 기록 | 생산성 향상, 실수 방지 |
# MAGIC | **Nested Runs** | 하나의 실험 안에서 알고리즘별 그룹화 | 체계적인 실험 관리 |
# MAGIC | **MLflow UI** | 실험 결과 시각화 비교 | 최적 모델 직관적 선택 |

# COMMAND ----------

# MAGIC %md
# MAGIC ### 사전 지식: Gradient Boosting이란?
# MAGIC
# MAGIC **Gradient Boosting**은 여러 개의 약한 학습기(주로 결정 트리)를 **순차적으로** 학습시키는 앙상블 기법입니다.
# MAGIC
# MAGIC ```
# MAGIC 1단계: 첫 번째 트리 학습 → 예측 오차(잔차) 계산
# MAGIC 2단계: 두 번째 트리가 1단계의 오차를 학습 → 남은 오차 계산
# MAGIC 3단계: 세 번째 트리가 2단계의 오차를 학습 → ...
# MAGIC ...
# MAGIC N단계: N번째 트리까지 반복
# MAGIC
# MAGIC 최종 예측 = 모든 트리의 예측을 합산
# MAGIC ```
# MAGIC
# MAGIC - **XGBoost, LightGBM, CatBoost**는 모두 Gradient Boosting의 변형입니다.
# MAGIC - **Random Forest**는 Boosting이 아닌 **Bagging** 방식으로, 여러 트리를 **독립적으로** 학습합니다.

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost lightgbm catboost shap --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 데이터 준비
# MAGIC
# MAGIC 02번 노트북에서 준비한 피처 테이블을 로드합니다.
# MAGIC 모든 알고리즘이 **동일한 데이터**로 학습해야 공정한 비교가 가능합니다.

# COMMAND ----------

# DBTITLE 1,학습/테스트 데이터 로드
import mlflow
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    f1_score, roc_auc_score, precision_score, recall_score,
    classification_report, confusion_matrix
)

# 피처 컬럼 정의
feature_columns = [
    "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "temp_diff", "power", "tool_wear_rate", "strain",
    "overheat_flag", "product_quality", "risk_score"
]
label_col = "machine_failure"

# 데이터 로드
df = spark.table("lgit_pm_training")
train_pdf = df.filter("split = 'train'").select(*feature_columns, label_col).toPandas()
test_pdf = df.filter("split = 'test'").select(*feature_columns, label_col).toPandas()

X_train, Y_train = train_pdf[feature_columns], train_pdf[label_col]
X_test, Y_test = test_pdf[feature_columns], test_pdf[label_col]

# 검증 세트 분할 (학습의 20%를 검증용으로)
X_tr, X_val, Y_tr, Y_val = train_test_split(
    X_train, Y_train, test_size=0.2, random_state=42, stratify=Y_train
)

# 불균형 비율 확인
pos_ratio = Y_train.mean()
scale_weight = (1 - pos_ratio) / pos_ratio
print(f"학습 데이터: {len(X_train)} 건")
print(f"테스트 데이터: {len(X_test)} 건")
print(f"고장 비율: {pos_ratio:.4f} (약 {pos_ratio*100:.1f}%)")
print(f"불균형 보정 가중치: {scale_weight:.1f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. MLflow 실험 설정
# MAGIC
# MAGIC ### MLflow 실험이란?
# MAGIC
# MAGIC **MLflow 실험(Experiment)** 은 여러 번의 학습 실행(Run)을 묶어서 관리하는 컨테이너입니다.
# MAGIC
# MAGIC ```
# MAGIC 실험: "lgit_multi_algorithm_comparison"
# MAGIC  ├─ Run 1: XGBoost (F1=0.85, AUC=0.92)
# MAGIC  ├─ Run 2: LightGBM (F1=0.87, AUC=0.93)
# MAGIC  ├─ Run 3: CatBoost (F1=0.86, AUC=0.94)
# MAGIC  └─ Run 4: RandomForest (F1=0.82, AUC=0.90)
# MAGIC ```
# MAGIC
# MAGIC 각 Run에는 **파라미터**, **메트릭**, **모델 아티팩트**가 자동으로 기록됩니다.
# MAGIC Databricks 노트북의 **오른쪽 패널 > 실험** 에서 실시간으로 확인할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,MLflow 실험 생성
xp_name = "lgit_multi_algorithm_comparison"
xp_path = f"/Users/{current_user}"
experiment_name = f"{xp_path}/{xp_name}"

try:
    experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
except:
    experiment_id = mlflow.create_experiment(
        name=experiment_name,
        tags={"project": "lgit-mlops-poc", "type": "multi-algorithm-comparison"}
    )

mlflow.set_experiment(experiment_name)
print(f"실험: {experiment_name} (ID: {experiment_id})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 공통 평가 함수 정의
# MAGIC
# MAGIC 모든 알고리즘에 동일한 평가 메트릭을 적용하여 공정한 비교를 보장합니다.
# MAGIC
# MAGIC ### 주요 평가 메트릭 설명
# MAGIC
# MAGIC | 메트릭 | 설명 | 제조 예지보전에서의 의미 |
# MAGIC |--------|------|----------------------|
# MAGIC | **F1 Score** | Precision과 Recall의 조화평균 | 고장 탐지 정확도와 커버리지의 균형 |
# MAGIC | **AUC-ROC** | 분류 임계값 전체에서의 성능 | 전반적인 분류 능력 |
# MAGIC | **Precision** | 고장 예측 중 실제 고장 비율 | 불필요한 정비 방지 (오탐 최소화) |
# MAGIC | **Recall** | 실제 고장 중 탐지된 비율 | 고장 미탐지 방지 (가장 중요!) |

# COMMAND ----------

# DBTITLE 1,공통 평가 함수
from mlflow.models import infer_signature

def evaluate_model(model, X_val, Y_val, X_test, Y_test, model_name_str):
    """
    모델을 평가하고 메트릭을 반환합니다.

    Args:
        model: 학습된 모델 (predict, predict_proba 메서드 필요)
        X_val: 검증 데이터
        Y_val: 검증 레이블
        X_test: 테스트 데이터
        Y_test: 테스트 레이블
        model_name_str: 모델 이름 (로깅용)

    Returns:
        dict: 평가 메트릭
    """
    # 검증 세트 예측
    val_pred = model.predict(X_val)
    val_proba = model.predict_proba(X_val)[:, 1] if hasattr(model, 'predict_proba') else val_pred

    # 테스트 세트 예측
    test_pred = model.predict(X_test)
    test_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else test_pred

    metrics = {
        "val_f1_score": f1_score(Y_val, val_pred),
        "val_auc": roc_auc_score(Y_val, val_proba),
        "val_precision": precision_score(Y_val, val_pred, zero_division=0),
        "val_recall": recall_score(Y_val, val_pred, zero_division=0),
        "test_f1_score": f1_score(Y_test, test_pred),
        "test_auc": roc_auc_score(Y_test, test_proba),
        "test_precision": precision_score(Y_test, test_pred, zero_division=0),
        "test_recall": recall_score(Y_test, test_pred, zero_division=0),
    }

    # Classification Report 출력
    print(f"\n=== {model_name_str} 평가 결과 ===")
    print(classification_report(Y_test, test_pred, target_names=["정상", "고장"]))

    return metrics

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. 알고리즘별 학습 (Track 분리)
# MAGIC
# MAGIC 각 알고리즘을 **독립된 MLflow Run**으로 학습합니다.
# MAGIC MLflow UI에서 알고리즘별로 결과를 비교할 수 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Track 1: XGBoost
# MAGIC
# MAGIC **XGBoost (eXtreme Gradient Boosting)**
# MAGIC - 2016년 Kaggle 대회에서 압도적 성능으로 유명해진 알고리즘
# MAGIC - **정규화(Regularization)** 를 통해 과적합 방지
# MAGIC - **병렬 학습** 지원으로 빠른 학습 속도
# MAGIC - 제조업에서 **가장 널리 사용**되는 ML 알고리즘

# COMMAND ----------

# DBTITLE 1,Track 1: XGBoost 학습
import xgboost as xgb

with mlflow.start_run(run_name="Track1_XGBoost") as run_xgb:
    mlflow.log_param("algorithm", "XGBoost")
    mlflow.log_param("algorithm_family", "gradient_boosting")

    # XGBoost 파라미터
    params = {
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 200,
        "scale_pos_weight": scale_weight,  # 불균형 보정
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "gamma": 0.1,
        "random_state": 42,
        "eval_metric": "logloss",
        "use_label_encoder": False,
    }

    model_xgb = xgb.XGBClassifier(**params)
    model_xgb.fit(
        X_tr, Y_tr,
        eval_set=[(X_val, Y_val)],
        verbose=False
    )

    # 평가
    metrics_xgb = evaluate_model(model_xgb, X_val, Y_val, X_test, Y_test, "XGBoost")
    mlflow.log_metrics(metrics_xgb)

    # 모델 저장
    signature = infer_signature(X_tr, model_xgb.predict(X_tr))
    mlflow.sklearn.log_model(model_xgb, "model", signature=signature)

    print(f"Run ID: {run_xgb.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Track 2: LightGBM
# MAGIC
# MAGIC **LightGBM (Light Gradient Boosting Machine)**
# MAGIC - Microsoft에서 개발한 고속 Gradient Boosting 프레임워크
# MAGIC - **Leaf-wise** 트리 성장 전략 (XGBoost는 Level-wise)
# MAGIC   - 가장 손실이 큰 리프를 먼저 분할 → 더 빠른 수렴
# MAGIC - **GOSS** (Gradient-based One-Side Sampling): 큰 gradient 샘플 위주 학습
# MAGIC - **EFB** (Exclusive Feature Bundling): 상호배타적 피처를 묶어 차원 축소
# MAGIC - 대용량 데이터에서 XGBoost보다 **2~10배 빠른** 학습 속도

# COMMAND ----------

# DBTITLE 1,Track 2: LightGBM 학습
import lightgbm as lgb

with mlflow.start_run(run_name="Track2_LightGBM") as run_lgb:
    mlflow.log_param("algorithm", "LightGBM")
    mlflow.log_param("algorithm_family", "gradient_boosting")

    model_lgb = lgb.LGBMClassifier(
        max_depth=6,
        learning_rate=0.1,
        n_estimators=200,
        scale_pos_weight=scale_weight,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        reg_alpha=0.1,
        reg_lambda=0.1,
        random_state=42,
        verbose=-1,
    )

    model_lgb.fit(
        X_tr, Y_tr,
        eval_set=[(X_val, Y_val)],
    )

    metrics_lgb = evaluate_model(model_lgb, X_val, Y_val, X_test, Y_test, "LightGBM")
    mlflow.log_metrics(metrics_lgb)

    signature = infer_signature(X_tr, model_lgb.predict(X_tr))
    mlflow.sklearn.log_model(model_lgb, "model", signature=signature)

    print(f"Run ID: {run_lgb.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Track 3: CatBoost
# MAGIC
# MAGIC **CatBoost (Categorical Boosting)**
# MAGIC - Yandex에서 개발한 Gradient Boosting 프레임워크
# MAGIC - **범주형 피처 자동 인코딩**: One-hot 인코딩 없이 범주형 데이터 직접 처리
# MAGIC - **Ordered Boosting**: 데이터 누출(Leakage) 방지를 위한 순서 기반 학습
# MAGIC - **과적합 방지**에 특히 강함
# MAGIC - AI4I 2020 데이터에서 'Type' (L/M/H) 컬럼 처리에 유리

# COMMAND ----------

# DBTITLE 1,Track 3: CatBoost 학습
from catboost import CatBoostClassifier

with mlflow.start_run(run_name="Track3_CatBoost") as run_cat:
    mlflow.log_param("algorithm", "CatBoost")
    mlflow.log_param("algorithm_family", "gradient_boosting")

    model_cat = CatBoostClassifier(
        depth=6,
        learning_rate=0.1,
        iterations=200,
        auto_class_weights="Balanced",  # CatBoost의 불균형 처리
        random_seed=42,
        verbose=0,
        eval_metric="F1",
    )

    model_cat.fit(
        X_tr, Y_tr,
        eval_set=(X_val, Y_val),
        verbose=False
    )

    metrics_cat = evaluate_model(model_cat, X_val, Y_val, X_test, Y_test, "CatBoost")
    mlflow.log_metrics(metrics_cat)

    signature = infer_signature(X_tr, model_cat.predict(X_tr))
    mlflow.sklearn.log_model(model_cat, "model", signature=signature)

    print(f"Run ID: {run_cat.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Track 4: Random Forest
# MAGIC
# MAGIC **Random Forest (랜덤 포레스트)**
# MAGIC - 여러 개의 결정 트리를 **독립적으로** 학습하고 **다수결 투표**로 예측
# MAGIC - Gradient Boosting과 달리 **배깅(Bagging)** 기반
# MAGIC - **장점**: 과적합에 강하고, 해석이 쉽고, 안정적
# MAGIC - **단점**: Boosting 계열보다 성능이 약간 낮을 수 있음
# MAGIC - **활용**: 빠른 프로토타이핑, 피처 중요도 분석

# COMMAND ----------

# DBTITLE 1,Track 4: Random Forest 학습
from sklearn.ensemble import RandomForestClassifier

with mlflow.start_run(run_name="Track4_RandomForest") as run_rf:
    mlflow.log_param("algorithm", "RandomForest")
    mlflow.log_param("algorithm_family", "bagging")

    model_rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight="balanced",  # 불균형 보정
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,  # 모든 CPU 코어 활용
    )

    model_rf.fit(X_tr, Y_tr)

    metrics_rf = evaluate_model(model_rf, X_val, Y_val, X_test, Y_test, "RandomForest")
    mlflow.log_metrics(metrics_rf)

    signature = infer_signature(X_tr, model_rf.predict(X_tr))
    mlflow.sklearn.log_model(model_rf, "model", signature=signature)

    print(f"Run ID: {run_rf.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. 알고리즘 비교 분석
# MAGIC
# MAGIC ### MLflow에서 비교하는 방법 (UI)
# MAGIC 1. 노트북 오른쪽의 **실험(Experiment)** 패널 클릭
# MAGIC 2. 4개 Run 모두 체크박스 선택
# MAGIC 3. **"Compare"** 버튼 클릭
# MAGIC 4. 차트 탭에서 메트릭별 비교 그래프 확인
# MAGIC
# MAGIC 아래에서는 코드로도 비교 결과를 정리합니다.

# COMMAND ----------

# DBTITLE 1,알고리즘 비교 테이블
results = {
    "XGBoost": metrics_xgb,
    "LightGBM": metrics_lgb,
    "CatBoost": metrics_cat,
    "RandomForest": metrics_rf,
}

comparison_df = pd.DataFrame(results).T
comparison_df = comparison_df.round(4)

# 각 메트릭에서 최고 성능 표시
print("=" * 80)
print("                    알고리즘 비교 결과 요약")
print("=" * 80)
print(comparison_df.to_string())
print("\n")

# 메트릭별 최고 알고리즘
for metric in ["test_f1_score", "test_auc", "test_recall", "test_precision"]:
    best_algo = comparison_df[metric].idxmax()
    best_val = comparison_df[metric].max()
    print(f"  {metric:20s} 최고: {best_algo} ({best_val:.4f})")

# COMMAND ----------

# DBTITLE 1,시각화: 알고리즘 비교 차트
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 4, figsize=(20, 5))
fig.suptitle("알고리즘별 테스트 성능 비교", fontsize=14)

metrics_to_plot = [
    ("test_f1_score", "F1 Score"),
    ("test_auc", "AUC-ROC"),
    ("test_recall", "Recall (고장 탐지율)"),
    ("test_precision", "Precision (정밀도)")
]

colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
algos = list(results.keys())

for i, (metric, title) in enumerate(metrics_to_plot):
    values = [results[a][metric] for a in algos]
    bars = axes[i].bar(algos, values, color=colors)
    axes[i].set_title(title)
    axes[i].set_ylim(0, 1)
    axes[i].tick_params(axis='x', rotation=45)

    # 값 표시
    for bar, val in zip(bars, values):
        axes[i].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()

# MLflow에 비교 차트 기록
with mlflow.start_run(run_name="algorithm_comparison_summary"):
    mlflow.log_figure(fig, "algorithm_comparison.png")
    # 최종 비교 결과도 기록
    best_algo = comparison_df["test_f1_score"].idxmax()
    mlflow.log_param("best_algorithm", best_algo)
    mlflow.log_metric("best_test_f1", comparison_df["test_f1_score"].max())

plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. 최종 권장 모델 선택
# MAGIC
# MAGIC ### 선택 기준
# MAGIC
# MAGIC 제조 예지보전에서는 **Recall (고장 탐지율)** 이 가장 중요합니다.
# MAGIC - Recall이 낮으면 → 실제 고장을 놓침 → **설비 다운타임 발생**
# MAGIC - Precision이 낮으면 → 불필요한 정비 → **비용 증가 (상대적으로 낮은 리스크)**
# MAGIC
# MAGIC 따라서 선택 우선순위:
# MAGIC 1. **Recall** ≥ 0.7 이상 (필수 조건)
# MAGIC 2. **F1 Score** 최대화 (Recall과 Precision 균형)
# MAGIC 3. **AUC** 참고 (전반적 분류 능력)

# COMMAND ----------

# DBTITLE 1,최종 모델 선택
# Recall 임계값 필터링
min_recall = 0.5
candidates = comparison_df[comparison_df["test_recall"] >= min_recall]

if len(candidates) > 0:
    # F1 기준 최고 모델 선택
    best_algo = candidates["test_f1_score"].idxmax()
    print(f"=== 최종 선택: {best_algo} ===")
    print(f"  Test F1:        {candidates.loc[best_algo, 'test_f1_score']:.4f}")
    print(f"  Test AUC:       {candidates.loc[best_algo, 'test_auc']:.4f}")
    print(f"  Test Recall:    {candidates.loc[best_algo, 'test_recall']:.4f}")
    print(f"  Test Precision: {candidates.loc[best_algo, 'test_precision']:.4f}")
else:
    best_algo = comparison_df["test_f1_score"].idxmax()
    print(f"Recall 임계값({min_recall}) 충족하는 모델이 없습니다.")
    print(f"F1 기준 선택: {best_algo}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC ### 학습한 내용:
# MAGIC 1. **4가지 알고리즘** (XGBoost, LightGBM, CatBoost, RandomForest)을 동일 조건에서 비교
# MAGIC 2. **MLflow 실험 추적**으로 모든 결과를 체계적으로 기록
# MAGIC 3. 제조 예지보전에서의 **메트릭 선택 기준** (Recall 우선)
# MAGIC 4. **알고리즘별 특성** 이해 (Boosting vs Bagging, 불균형 처리 등)
# MAGIC
# MAGIC ### MLflow UI 활용 팁:
# MAGIC - 노트북 우측 패널 > **실험** 클릭 → 모든 Run 확인
# MAGIC - Run 선택 후 **Compare** → 차트로 비교
# MAGIC - **Artifacts** 탭 → 저장된 모델 아티팩트 확인
# MAGIC
# MAGIC **다음 단계:** [03c: 고급 기법 적용]($./03c_advanced_techniques) — SMOTE, Optuna HPO, Stacking, AutoML
