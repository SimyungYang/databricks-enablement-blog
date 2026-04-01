# 03. 모델 학습 (XGBoost Training + 고급 기법)

> **전체 노트북 코드**: [03_structured_model_training.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/03_structured_model_training.py)


**목적**: XGBoost 모델을 학습하고, MLflow로 실험을 추적하며, SHAP으로 해석합니다. 멀티 알고리즘 비교, SMOTE, Optuna, Stacking 등 고급 기법도 다룹니다.

**사용 Databricks 기능**: `MLflow Experiment Tracking`, `Autolog`, `Data Lineage`, `mlflow.evaluate()`, `Databricks AutoML`

---

## 1. MLflow 데이터 계보 캡처

**MLflow Data Lineage**를 통해 모델이 어떤 데이터(테이블 + 버전)로 학습되었는지 추적합니다. 모델 문제 발생 시 **근본 원인 분석(RCA)** 에 활용됩니다.

```python
# 최신 테이블 버전으로 데이터셋 계보 객체 생성
latest_version = max(
    spark.sql(f"DESCRIBE HISTORY {catalog}.{db}.lgit_pm_training").toPandas()["version"]
)
src_dataset = mlflow.data.load_delta(
    table_name=f"{catalog}.{db}.lgit_pm_training",
    version=str(latest_version)
)
```

## 2. XGBoost 학습 + MLflow Autolog

`mlflow.xgboost.autolog()`으로 하이퍼파라미터, 메트릭, 피처 중요도가 **자동** 기록됩니다.

```python
with mlflow.start_run(run_name="xgboost_baseline") as run:
    mlflow.xgboost.autolog(log_models=False, silent=True)
    scale_pos_weight = (Y_train == 0).sum() / (Y_train == 1).sum()
    params = {"objective": "binary:logistic", "scale_pos_weight": scale_pos_weight,
              "max_depth": 6, "learning_rate": 0.1}
    model = xgb.train(params, dtrain, num_boost_round=200,
                       evals=[(dtrain, "train"), (dval, "val")], early_stopping_rounds=20)
    signature = infer_signature(X_tr, y_pred_proba)
    mlflow.xgboost.log_model(model, "xgboost_model", signature=signature)
    mlflow.log_input(src_dataset, context="training-input")  # 계보 기록
```

## 3. SHAP 기반 모델 해석

SHAP(SHapley Additive exPlanations)을 통해 **왜 고장이 예측되었는지** 설명 가능한 피처 중요도를 산출합니다.

```python
explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test, feature_names=feature_columns)

# 개별 고장 예측 사례의 피처 기여도 분석
for feat, val, sv in sorted(zip(feature_columns, X_test.iloc[idx], shap_values[idx]),
                             key=lambda x: abs(x[2]), reverse=True):
    direction = "고장" if sv > 0 else "정상"
    print(f"  {feat:30s}: {val:10.2f} → SHAP {sv:+.4f} ({direction})")
```

{% hint style="info" %}
SHAP 해석은 제조 현장에서 **"왜 이 설비가 고장 위험으로 판단되었는가?"** 에 답할 수 있게 합니다. 이는 정비팀의 신뢰도 확보와 의사결정에 핵심적입니다.
{% endhint %}

---

## 03b. 멀티 알고리즘 비교

XGBoost, LightGBM, CatBoost, Random Forest를 **동일 조건**에서 비교합니다. MLflow 실험 UI에서 한눈에 비교할 수 있습니다.

```python
# CatBoost — 범주형 피처 자동 처리 + 불균형 보정
model_cat = CatBoostClassifier(
    depth=6, learning_rate=0.1, iterations=200,
    auto_class_weights="Balanced", random_seed=42, eval_metric="F1",
)
model_cat.fit(X_tr, Y_tr, eval_set=(X_val, Y_val))

# LightGBM — Leaf-wise 성장으로 빠른 수렴
model_lgb = lgb.LGBMClassifier(
    max_depth=6, learning_rate=0.1, n_estimators=200,
    scale_pos_weight=scale_weight, verbose=-1,
)
model_lgb.fit(X_tr, Y_tr, eval_set=[(X_val, Y_val)])
```

{% hint style="warning" %}
제조 예지보전에서는 **Recall(고장 탐지율)** 이 가장 중요합니다. Recall이 낮으면 실제 고장을 놓쳐 설비 다운타임이 발생합니다. 알고리즘 선택 시 Recall >= 0.7을 필수 조건으로 설정하세요.
{% endhint %}

---

## 03c. 고급 기법: SMOTE-ENN, Optuna, Stacking, AutoML

**SMOTE-ENN** — 소수 클래스 오버샘플링 + 노이즈 제거로 불균형 데이터를 처리합니다.

```python
from imblearn.combine import SMOTEENN
smote_enn = SMOTEENN(smote=SMOTE(sampling_strategy=0.5, k_neighbors=5, random_state=42))
X_resampled, Y_resampled = smote_enn.fit_resample(X_train, Y_train)
# 원본: 정상 7,700 / 고장 270  →  SMOTE-ENN 후: 균형 잡힌 데이터
```

**Optuna HPO** — 베이지안 최적화로 이전 결과를 학습하여 다음 탐색점을 지능적으로 선택합니다.

```python
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

**Databricks AutoML** — 한 줄로 최적 모델을 자동 탐색하고, 결과 노트북까지 생성합니다.

```python
from databricks import automl
summary = automl.classify(
    dataset=spark.table("lgit_pm_training"),
    target_col="machine_failure",
    primary_metric="f1",
    timeout_minutes=15,
)
```

---

## 03d. 임계값 최적화 & 모델 캘리브레이션

> **전체 노트북 코드**: [03_structured_model_training.py (Section 6)](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/03_structured_model_training.py)

대부분의 팀이 XGBoost의 예측 확률을 **0.5 기준**으로 이진 분류합니다. 하지만 고장 예측처럼 **놓치는 것(FN)이 오탐(FP)보다 훨씬 비싼 경우**, 임계값을 낮춰서 Recall을 높이는 것이 비즈니스적으로 올바릅니다.

### PR-curve 기반 최적 임계값 탐색

Precision-Recall 곡선에서 **Recall >= 0.8을 만족하면서 Precision이 가장 높은 임계값**을 자동 탐색합니다.

```python
from sklearn.metrics import precision_recall_curve

y_pred_proba = best_model.predict(xgb.DMatrix(X_val))
precisions, recalls, thresholds = precision_recall_curve(Y_val, y_pred_proba)

# Recall >= 0.8을 만족하는 최적 임계값
target_recall = 0.8
valid_idx = np.where(recalls[:-1] >= target_recall)[0]
if len(valid_idx) > 0:
    best_idx = valid_idx[np.argmax(precisions[:-1][valid_idx])]
    optimal_threshold = thresholds[best_idx]

# MLflow에 최적 임계값 기록
mlflow.log_metric("optimal_threshold", optimal_threshold)
```

### 모델 캘리브레이션 (Platt Scaling, Isotonic Regression)

모델이 "고장 확률 80%"라고 출력하면, 실제로 100건 중 80건이 고장이어야 합니다. XGBoost의 raw probability는 종종 **과신(overconfident)** 하거나 **과소(underconfident)** 하기 때문에, 다음 기법으로 보정합니다:

| 기법 | 원리 | 적합 상황 |
|------|------|----------|
| **Platt Scaling** | 시그모이드 함수로 확률 보정 | 데이터가 적을 때, 단순한 보정 |
| **Isotonic Regression** | 비모수적 단조 함수 적합 | 데이터가 충분할 때, 복잡한 분포 |

### 비즈니스 기반 임계값 선택

{% hint style="warning" %}
임계값은 비즈니스 요구사항에 따라 결정합니다:
- **놓침이 치명적** (반도체, 자동차 부품) → 임계값 낮춤 (0.3~0.4) → Recall 상승, Precision 하락
- **오탐 비용이 높음** (불필요 정비 비용 큼) → 임계값 높임 (0.6~0.7) → Precision 상승, Recall 하락
- **최적점**: PR 곡선에서 비용함수를 최소화하는 점 = `cost = FN x 50000 + FP x 3000`
{% endhint %}

**다음 단계**: [04. 모델 등록](04-model-registration.md)
