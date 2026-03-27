# Databricks MLOps 완전 가이드: 예지보전 & 이상탐지 파이프라인

> **최종 업데이트**: 2026-03-27 | **대상**: Databricks Lakehouse 기반 MLOps 구축을 위한 실전 가이드

---

## 1. MLOps 개요

### MLOps란?

MLOps(Machine Learning Operations)는 ML 모델의 **개발 → 배포 → 운영 → 모니터링**을 자동화하는 엔지니어링 프랙티스입니다. 데이터 사이언스와 운영(Ops)을 연결하여, 모델이 실험실을 벗어나 실제 비즈니스 가치를 창출하도록 합니다.

### 왜 MLOps가 필요한가?

- **재현성**: 동일한 데이터와 코드로 동일한 결과를 보장
- **자동화**: 수동 작업을 줄이고 반복 가능한 파이프라인 구축
- **거버넌스**: 모델의 계보(Lineage), 버전, 접근 권한을 중앙에서 관리
- **모니터링**: 운영 중 모델 성능 저하(Data Drift, Concept Drift)를 자동 탐지

### Databricks MLOps 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MLOps 파이프라인 아키텍처                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │  정형 데이터   │    │ 비정형 데이터  │    │   Unity Catalog      │  │
│  │  (AI4I 2020)  │    │ (MVTec AD)   │    │   (거버넌스/계보)     │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────────────────┘  │
│         │                   │                                       │
│         ▼                   ▼                                       │
│  ┌──────────────┐    ┌──────────────┐                              │
│  │ Feature Eng.  │    │ Image Proc.  │                              │
│  │ (Spark/Pandas)│    │ (Anomalib)   │                              │
│  └──────┬───────┘    └──────┬───────┘                              │
│         │                   │                                       │
│         ▼                   ▼                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │ XGBoost Train │    │ PatchCore    │    │   MLflow Tracking    │  │
│  │ + SHAP        │    │ Train        │    │   (실험/메트릭/모델)  │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────────────────┘  │
│         │                   │                                       │
│         ▼                   ▼                                       │
│  ┌─────────────────────────────────────┐                           │
│  │     UC Model Registry                │                           │
│  │  (Champion / Challenger 에일리어스)    │                           │
│  └──────────────┬──────────────────────┘                           │
│         ┌───────┴───────┐                                          │
│         ▼               ▼                                          │
│  ┌──────────────┐ ┌──────────────┐    ┌──────────────────────┐    │
│  │ Batch Predict │ │ Model Serve  │    │  Lakehouse Monitor   │    │
│  │ (일 4회)      │ │ (실시간)     │    │  (드리프트 탐지)      │    │
│  └──────────────┘ └──────────────┘    └──────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              MLOps Agent + Databricks Workflows               │   │
│  │     운영: 주1회 재학습 + 일4회 배치예측                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 핵심 Databricks 기능 매핑

| 기능 영역 | Databricks 서비스 | 역할 |
|-----------|------------------|------|
| 데이터 관리 | Delta Lake, Unity Catalog, Volumes | ACID 트랜잭션, 거버넌스, 비정형 데이터 |
| 실험 추적 | MLflow Tracking, Autolog | 파라미터/메트릭/아티팩트 자동 기록 |
| 모델 관리 | UC Model Registry | 버전 관리, Alias(Champion/Challenger) |
| 추론 | PySpark UDF, Model Serving | 배치/실시간 예측 |
| 모니터링 | Lakehouse Monitoring | 데이터 드리프트, 성능 추적 |
| 자동화 | Workflows, AI Agent | 파이프라인 스케줄링, 자동 오케스트레이션 |

---

## 2. 노트북별 상세 설명

### 01. Overview — 전체 아키텍처 소개

**목적**: PoC 시나리오 정의 및 전체 파이프라인 아키텍처를 소개합니다.

**주요 개념**:
- **정형 데이터**: UCI AI4I 2020 Predictive Maintenance Dataset (10,000건) — XGBoost 기반 설비 고장 예측
- **비정형 데이터**: MVTec AD 산업용 이미지 — Anomalib PatchCore 기반 표면 이상탐지
- **운영 환경**: 주 1회 재학습 + 일 4회 배치 예측

{% hint style="info" %}
이 데모는 제조 현장의 예지보전(Predictive Maintenance)과 비전 기반 이상탐지를 하나의 MLOps 파이프라인으로 통합합니다. 정형/비정형 모델 모두 동일한 Unity Catalog 거버넌스 체계로 관리됩니다.
{% endhint %}

---

### 02. 피처 엔지니어링 (Feature Engineering)

**목적**: 센서 데이터를 탐색하고, 예지보전에 유용한 파생 피처를 생성합니다.

**주요 개념**:
- EDA (탐색적 데이터 분석) — SQL과 Pandas on Spark API 활용
- 도메인 지식 기반 파생 피처 7개 생성
- Train/Test 80:20 분할 후 Delta Lake 저장

**핵심 코드 — 피처 엔지니어링 함수**:

```python
def engineer_pm_features(df: DataFrame) -> DataFrame:
    df_features = (
        df
        # 온도차: 과열 징후 탐지
        .withColumn("temp_diff",
                    F.col("process_temperature_k") - F.col("air_temperature_k"))
        # 기계 전력 (W): 토크 x 회전속도
        .withColumn("power",
                    F.col("torque_nm") * F.col("rotational_speed_rpm") * F.lit(2 * math.pi / 60))
        # 기계적 스트레인: 토크 x 공구 마모
        .withColumn("strain", F.col("torque_nm") * F.col("tool_wear_min"))
        # 과열 플래그
        .withColumn("overheat_flag",
                    F.when(F.col("process_temperature_k") - F.col("air_temperature_k") > 8.6, 1)
                    .otherwise(0))
        # 복합 위험 점수
        .withColumn("risk_score",
                    (F.col("tool_wear_min") / F.lit(240.0)) * 0.3 +
                    (F.col("torque_nm") / F.lit(80.0)) * 0.3 +
                    F.when(F.col("process_temperature_k") - F.col("air_temperature_k") > 8.6, 0.4)
                    .otherwise(0.0))
    )
    return df_features
```

**사용 Databricks 기능**: Delta Lake, Pandas on Spark API, Unity Catalog 메타데이터

{% hint style="success" %}
Unity Catalog에 테이블을 저장하면 **데이터 계보(Lineage)** 가 자동으로 추적됩니다. 이후 모델 학습 시 어떤 테이블의 어떤 버전으로 학습했는지 추적할 수 있습니다.
{% endhint %}

---

### 03. 모델 학습 (XGBoost Training)

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

### 03a~03d. ML 트렌드 및 고급 기법

#### 03a. ML 트렌드 가이드

예지보전에 적용할 수 있는 최신 기술 트렌드를 정리합니다: 멀티 알고리즘 비교, SMOTE 불균형 처리, Optuna HPO, AutoML, Stacking 앙상블 등.

#### 03b. 멀티 알고리즘 비교

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

#### 03c. 고급 기법

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

#### 03d. 재학습 전략

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

---

### 04. 모델 등록 (Unity Catalog Model Registry)

**목적**: 최적 모델을 UC 모델 레지스트리에 등록하고, Alias를 통해 생애 주기를 관리합니다.

**주요 개념**:
- `mlflow.search_runs()` 로 최적 모델 자동 검색
- `mlflow.register_model()` 로 UC 등록
- Challenger/Champion 에일리어스를 통한 안전한 배포

**핵심 코드**:

```python
# 최적 모델 검색 (val_f1_score 기준)
best_run = mlflow.search_runs(
    experiment_ids=experiment_id,
    order_by=["metrics.val_f1_score DESC"],
    max_results=1,
)

# Unity Catalog에 모델 등록
model_details = mlflow.register_model(
    model_uri=f"runs:/{run_id}/xgboost_model",
    name=f"{catalog}.{db}.lgit_predictive_maintenance"
)

# Challenger 에일리어스 설정
client.set_registered_model_alias(
    name=model_name, alias="Challenger", version=model_details.version
)
```

**사용 Databricks 기능**: Unity Catalog Model Registry, Model Lineage, 태그 기반 거버넌스

---

### 05. 챌린저 검증 (Challenger Validation)

**목적**: 새 모델을 운영에 배포하기 전 체계적인 4단계 검증을 수행합니다.

**주요 개념**:
- Check 1: 모델 문서화 확인
- Check 2: 운영 데이터 추론 테스트
- Check 3: Champion 대비 성능 비교
- Check 4: 비즈니스 KPI 평가 (비용 분석)

**핵심 코드 — 비즈니스 가치 평가**:

```python
COST_DOWNTIME = 50000       # 미탐지 고장 비용
SAVING_PREVENTED = 45000    # 예방 정비 절감 비용

tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
business_value = (
    tp * SAVING_PREVENTED - fp * COST_FALSE_ALARM
    - fn * COST_DOWNTIME - tp * COST_PREVENTIVE
)

# 모든 검증 통과 시 Champion 자동 승급
if all_passed:
    client.set_registered_model_alias(
        name=model_name, alias="Champion", version=model_version
    )
```

**사용 Databricks 기능**: `mlflow.evaluate()`, 모델 에일리어스 기반 배포, 태그 기반 검증 추적

{% hint style="info" %}
Champion/Challenger 패턴은 **코드 변경 없이** 모델을 교체할 수 있게 합니다. 추론 코드는 항상 `models:/{model_name}@Champion`을 참조하므로, Alias만 변경하면 운영 모델이 자동으로 전환됩니다.
{% endhint %}

---

### 06. 배치 추론 (Batch Inference)

**목적**: Champion 모델을 PySpark UDF로 변환하여 클러스터 전체에서 분산 추론합니다.

**주요 개념**:
- `mlflow.pyfunc.spark_udf()` — 모델을 Spark UDF로 변환
- 위험 등급 자동 분류 (CRITICAL / HIGH / MEDIUM / LOW)
- Delta Lake Append 모드로 예측 이력 누적

**핵심 코드**:

```python
# Champion 모델을 PySpark UDF로 로드
champion_udf = mlflow.pyfunc.spark_udf(
    spark,
    model_uri=f"models:/{model_name}@Champion",
    result_type="double"
)

# 분산 배치 예측 + 위험 등급 부여
preds_df = (
    inference_df
    .withColumn("failure_probability", champion_udf(*feature_columns))
    .withColumn("risk_level",
        F.when(F.col("failure_probability") > 0.8, "CRITICAL")
        .when(F.col("failure_probability") > 0.5, "HIGH")
        .when(F.col("failure_probability") > 0.3, "MEDIUM")
        .otherwise("LOW"))
)

# Delta Lake에 Append (이력 누적)
preds_df.write.mode("append").saveAsTable("lgit_pm_inference_results")
```

**사용 Databricks 기능**: PySpark UDF 분산 추론, Delta Lake ACID 트랜잭션, Workflows 연동

---

### 07. 비정형 이상탐지 (Anomalib PatchCore)

**목적**: MVTec AD 이미지 데이터로 PatchCore 비지도 학습 기반 이상탐지 모델을 학습합니다.

**주요 개념**:
- PatchCore — 정상 이미지의 CNN 피처를 메모리 뱅크에 저장, 거리 기반 이상 점수 산출
- Unity Catalog Volumes — 이미지 데이터 중앙 관리
- GPU 클러스터 필수 (g5.2xlarge 권장)

**핵심 코드**:

```python
from anomalib.data import MVTec
from anomalib.models import Patchcore
from anomalib.engine import Engine

datamodule = MVTec(root=data_path, category="bottle", image_size=(256, 256))

model = Patchcore(
    backbone="wide_resnet50_2",
    layers_to_extract=["layer2", "layer3"],
    coreset_sampling_ratio=0.1,
)

engine = Engine(max_epochs=1, accelerator="auto")
engine.fit(model=model, datamodule=datamodule)
test_results = engine.test(model=model, datamodule=datamodule)
```

**사용 Databricks 기능**: Volumes (이미지 관리), GPU Cluster, MLflow 아티팩트 추적, UC 모델 등록

{% hint style="success" %}
비정형 모델도 정형 모델과 **동일한 Unity Catalog 거버넌스** 체계로 관리됩니다. 에일리어스, 태그, 접근 제어 모두 통일된 방식으로 적용됩니다.
{% endhint %}

---

### 08. 모델 모니터링 (Model Monitoring)

**목적**: 운영 중인 모델의 데이터 드리프트 및 성능 저하를 자동 탐지합니다.

**주요 개념**:
- 학습 vs 추론 데이터 분포 비교 (PSI)
- 시계열 기반 예측 분포 추이 모니터링
- Lakehouse Monitoring 자동 설정

**핵심 코드 — Lakehouse Monitor 생성**:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

monitor = w.quality_monitors.create(
    table_name=f"{catalog}.{db}.lgit_pm_inference_results",
    assets_dir=f"/Workspace/Users/{current_user}/lgit_monitoring",
    output_schema_name=f"{catalog}.{db}",
    inference_log={
        "model_id_col": "model_name",
        "prediction_col": "failure_probability",
        "timestamp_col": "inference_timestamp",
        "problem_type": "PROBLEM_TYPE_CLASSIFICATION",
    },
)
```

**사용 Databricks 기능**: Lakehouse Monitoring, Delta Lake Time Travel, SQL Analytics 대시보드

---

### 09. MLOps Agent

**목적**: AI Agent가 Trigger에 따라 MLOps Tool을 자동 호출하여 학습/예측을 오케스트레이션합니다.

**주요 개념**:
- Tool 함수 정의: `check_data_drift`, `trigger_retraining`, `run_batch_prediction`, `get_model_status`
- 시스템 프롬프트 기반 자동화 규칙
- 드리프트 감지 시 자동 재학습, 스케줄 기반 배치 예측

**핵심 코드 — Agent 워크플로우**:

```python
def mlops_agent_workflow(trigger_type: str = "full_cycle"):
    results = {}
    if trigger_type in ["scheduled", "full_cycle"]:
        results["batch_prediction"] = run_batch_prediction()
    if trigger_type in ["drift_check", "full_cycle"]:
        drift = check_data_drift()
        results["drift_check"] = drift
        if drift["drift_detected"]:
            results["retraining"] = trigger_retraining(reason="auto_drift_detection")
    results["model_status"] = get_model_status()
    return results
```

**사용 Databricks 기능**: AI Agent (ChatAgent), UC Functions as Tools, Model Serving, MLflow Tracing

---

### 10. Job 스케줄링 (Databricks Workflows)

**목적**: 운영/개발 환경별 MLOps 파이프라인을 Databricks Workflows로 스케줄링합니다.

**주요 개념**:
- Multi-task Jobs: 여러 노트북을 DAG로 연결
- 환경별 분리: 운영(주 1회 재학습, 일 4회 추론) / 개발(일 4회 재학습)

**운영 워크플로우 구조**:

```
[주 1회 재학습]
 02_Feature_Eng → 03_Model_Train → 04_Model_Reg → 05_Validation

[일 4회 배치 예측]
 06_Batch_Infer → 08_Monitoring
```

**스케줄 요약**:

| Job | 환경 | Cron (KST) | 설명 |
|-----|------|------------|------|
| Prod Weekly Retraining | 운영 | `0 2 * * 1` | 매주 월 02:00 재학습 |
| Prod Batch Inference | 운영 | `0 0,6,12,18 * * *` | 일 4회 배치 예측 |
| Dev Daily Retraining | 개발 | `0 0,6,12,18 * * *` | 일 4회 실험 재학습 |

**사용 Databricks 기능**: Databricks Workflows, Serverless Compute, 이메일/Slack 알림

---

## 3. 전체 파이프라인 흐름

### End-to-End 데이터 흐름

```
[데이터 수집]
    │
    ▼
02. 피처 엔지니어링 ──────────── Delta Lake 테이블 저장
    │                              (Unity Catalog 계보 추적)
    ▼
03. 모델 학습 ────────────────── MLflow 실험 추적
    │  (XGBoost / LightGBM /       (Autolog, SHAP, HPO)
    │   CatBoost / Stacking)
    ▼
04. 모델 등록 ────────────────── UC Model Registry
    │                              (Challenger 에일리어스)
    ▼
05. 챌린저 검증 ──────────────── 4단계 검증
    │  (문서화/추론/성능/KPI)        통과 시 Champion 승급
    ▼
06. 배치 추론 ────────────────── PySpark UDF 분산 추론
    │  (일 4회 자동 실행)            결과 Delta Lake 저장
    ▼
08. 모니터링 ─────────────────── Lakehouse Monitoring
    │  (PSI 드리프트 탐지)           성능 저하 시 알림
    ▼
09. MLOps Agent ──────────────── 자동 오케스트레이션
    │  (드리프트 → 재학습 트리거)
    ▼
10. Job 스케줄링 ─────────────── Databricks Workflows
    (운영/개발 환경 분리)
```

### 비정형 데이터 흐름 (병렬)

```
이미지 데이터 (UC Volumes)
    │
    ▼
07. Anomalib PatchCore 학습 ──── GPU Cluster
    │                              MLflow 아티팩트 추적
    ▼
UC Model Registry ────────────── 정형 모델과 동일 거버넌스
```

{% hint style="info" %}
정형 모델과 비정형 모델이 **동일한 Unity Catalog** 내에서 관리되므로, 향후 두 모델의 예측을 결합한 **복합 판단 시스템(Compound AI System)** 으로 확장할 수 있습니다.
{% endhint %}

---

## 4. 참고 문서

### Databricks 공식 문서

| 주제 | 링크 |
|------|------|
| MLflow Experiment Tracking | [docs.databricks.com/mlflow/tracking](https://docs.databricks.com/en/mlflow/tracking-and-model-registry.html) |
| Unity Catalog Model Registry | [docs.databricks.com/machine-learning/manage-model-lifecycle](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/index.html) |
| Lakehouse Monitoring | [docs.databricks.com/lakehouse-monitoring](https://docs.databricks.com/en/lakehouse-monitoring/index.html) |
| Databricks AutoML | [docs.databricks.com/machine-learning/automl](https://docs.databricks.com/en/machine-learning/automl/index.html) |
| Feature Engineering | [docs.databricks.com/machine-learning/feature-store](https://docs.databricks.com/en/machine-learning/feature-store/index.html) |
| Model Serving | [docs.databricks.com/machine-learning/model-serving](https://docs.databricks.com/en/machine-learning/model-serving/index.html) |
| Databricks Workflows | [docs.databricks.com/workflows](https://docs.databricks.com/en/workflows/index.html) |
| AI Agent Framework | [docs.databricks.com/generative-ai/agent-framework](https://docs.databricks.com/en/generative-ai/agent-framework/index.html) |

### 외부 참고 자료

| 주제 | 링크 |
|------|------|
| MLflow 공식 문서 | [mlflow.org/docs/latest](https://mlflow.org/docs/latest/index.html) |
| XGBoost 문서 | [xgboost.readthedocs.io](https://xgboost.readthedocs.io/) |
| Anomalib (이상탐지) | [github.com/openvinotoolkit/anomalib](https://github.com/openvinotoolkit/anomalib) |
| SHAP (모델 해석) | [shap.readthedocs.io](https://shap.readthedocs.io/) |
| Optuna (HPO) | [optuna.readthedocs.io](https://optuna.readthedocs.io/) |
| imbalanced-learn (SMOTE) | [imbalanced-learn.org](https://imbalanced-learn.org/) |
