# 03. 모델 학습 (XGBoost Training)

**목적**: XGBoost 모델을 학습하고, MLflow로 실험을 추적하며, SHAP으로 해석합니다.

**주요 개념**:
- MLflow Autolog — 코드 수정 없이 학습 과정 자동 기록
- Data Lineage — 학습 데이터 테이블 버전과 모델 간 계보 캡처
- SHAP 기반 피처 중요도 및 개별 예측 해석

**핵심 코드 — MLflow 데이터 계보 캡처**:

```python
# 최신 테이블 버전으로 데이터셋 계보 객체 생성
src_dataset = mlflow.data.load_delta(
    table_name=f"{catalog}.{db}.lgit_pm_training",
    version=str(latest_version)
)

with mlflow.start_run(run_name="xgboost_baseline") as run:
    mlflow.xgboost.autolog(log_models=False, silent=True)
    # ... 모델 학습 ...
    mlflow.log_input(src_dataset, context="training-input")  # 계보 기록
```

**핵심 코드 — SHAP 해석**:

```python
explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test, feature_names=feature_columns)
```

**사용 Databricks 기능**: MLflow Experiment Tracking, Autolog, Data Lineage, `mlflow.evaluate()`

---

## 03a~03d. ML 트렌드 및 고급 기법

### 03a. ML 트렌드 가이드

예지보전에 적용할 수 있는 최신 기술 트렌드를 정리합니다: 멀티 알고리즘 비교, SMOTE 불균형 처리, Optuna HPO, AutoML, Stacking 앙상블 등.

### 03b. 멀티 알고리즘 비교

**목적**: XGBoost, LightGBM, CatBoost, Random Forest를 동일 조건에서 비교합니다.

```python
# 예시: CatBoost — 불균형 데이터에 auto_class_weights 적용
model_cat = CatBoostClassifier(
    depth=6, learning_rate=0.1, iterations=200,
    auto_class_weights="Balanced",
    random_seed=42, eval_metric="F1",
)
model_cat.fit(X_tr, Y_tr, eval_set=(X_val, Y_val))
```

**사용 Databricks 기능**: MLflow 실험 비교 UI, Nested Runs

### 03c. 고급 기법

**SMOTE-ENN** (불균형 처리), **Optuna HPO** (베이지안 최적화), **Stacking Ensemble**, **Databricks AutoML**을 적용합니다.

```python
# Optuna HPO — 베이지안 최적화로 30회 시행
def objective(trial):
    params = {
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
    }
    model = xgb.XGBClassifier(**params, scale_pos_weight=sw)
    model.fit(X_tr, Y_tr)
    return f1_score(Y_val, model.predict(X_val))

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=30)
```

```python
# Databricks AutoML — 한 줄로 최적 모델 탐색
from databricks import automl
summary = automl.classify(
    dataset=spark.table("lgit_pm_training"),
    target_col="machine_failure",
    primary_metric="f1",
    timeout_minutes=15,
)
```

### 03d. 재학습 전략

Data Drift와 Concept Drift의 원리, PSI 기반 드리프트 탐지, Full Retraining 자동화 파이프라인을 다룹니다.

```python
# PSI (Population Stability Index) 계산 — 드리프트 탐지 핵심
def calculate_psi(expected, actual, bins=10):
    breakpoints = np.linspace(min(expected.min(), actual.min()),
                             max(expected.max(), actual.max()), bins + 1)
    expected_counts = np.maximum(
        np.histogram(expected, bins=breakpoints)[0] / len(expected), 0.001)
    actual_counts = np.maximum(
        np.histogram(actual, bins=breakpoints)[0] / len(actual), 0.001)
    psi = np.sum((actual_counts - expected_counts) * np.log(actual_counts / expected_counts))
    return psi
# PSI < 0.1: 안정 | 0.1~0.2: 주의 | > 0.2: 재학습 권장
```

{% hint style="warning" %}
제조 데이터는 계절 변화, 설비 노후화, 공정 변경 등으로 인해 드리프트가 빈번합니다. 스케줄 기반 재학습만으로는 부족하며, **드리프트 기반 + 성능 기반 하이브리드 트리거**를 권장합니다.
{% endhint %}
