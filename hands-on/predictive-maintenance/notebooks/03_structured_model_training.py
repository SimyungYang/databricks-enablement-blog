# Databricks notebook source
# MAGIC %md
# MAGIC # XGBoost 예지보전 모델 학습
# MAGIC
# MAGIC 본 노트북에서는 **XGBoost** 모델을 학습시키고, MLflow로 실험을 추적하며, SHAP을 통해 모델을 해석합니다.
# MAGIC
# MAGIC ### 이 노트북에서 배우는 것
# MAGIC
# MAGIC 제조 현장에서 설비가 갑자기 멈추면 생산 라인 전체가 중단되고, 막대한 손실이 발생합니다.
# MAGIC **예지보전(Predictive Maintenance)** 이란 센서 데이터를 분석하여 설비가 고장나기 **전에** 미리 예측하는 기술입니다.
# MAGIC
# MAGIC 이 노트북에서는 다음 과정을 단계별로 진행합니다:
# MAGIC 1. 설비 센서 데이터(온도, 토크, 회전속도 등)를 입력으로 받아
# MAGIC 2. **"이 설비가 곧 고장날 것인가?"** 를 예측하는 AI 모델을 학습시키고
# MAGIC 3. 모델이 **왜 그런 판단을 내렸는지** 해석합니다
# MAGIC
# MAGIC > **현장 경험담:**20년 넘게 제조 AI 프로젝트를 해오면서 느낀 것은, 모델의 정확도보다 **"현장이 모델을 신뢰하는가"** 가 프로젝트 성패를 결정한다는 것입니다. 아무리 좋은 모델이라도 현장 엔지니어가 "저 AI 믿을 수 없어"라고 하면 끝입니다. 이 노트북에서는 단순히 모델을 만드는 것을 넘어, **왜 그렇게 판단했는지 설명할 수 있는 모델** 을 만드는 과정을 다룹니다.
# MAGIC
# MAGIC ### Databricks 핵심 기능
# MAGIC
# MAGIC | 기능 | 설명 | 제조 현장 가치 |
# MAGIC |------|------|----------------|
# MAGIC | **MLflow Experiment Tracking** | 파라미터, 메트릭, 아티팩트 자동 추적 | 어떤 조건에서 학습한 모델이 가장 좋았는지 기록이 남아, 나중에 동일한 결과를 재현할 수 있습니다 |
# MAGIC | **MLflow Autolog** | 코드 변경 없이 학습 과정 자동 기록 | 엔지니어가 추적 코드를 직접 작성할 필요 없이, 단 한 줄로 모든 학습 이력이 자동 저장됩니다 |
# MAGIC | **Data Lineage** | 학습 데이터와 모델 간 계보 캡처 | 모델에 문제가 생겼을 때 "어떤 데이터로 학습했는지" 즉시 추적 가능합니다 |
# MAGIC | **mlflow.evaluate()** | 자동화된 모델 평가 (혼동행렬, ROC, PR 곡선 등) | 모델 성능을 다양한 관점에서 자동으로 평가하여, 현장 투입 전 신뢰성을 검증합니다 |
# MAGIC
# MAGIC > **기존 방식 vs Databricks:** 전통적으로는 Excel이나 Python 스크립트로 모델을 학습하면 "어떤 파라미터로 학습했는지", "어떤 데이터를 썼는지" 기록이 남지 않아 재현이 불가능했습니다. Databricks MLflow는 이 모든 것을 **자동으로** 기록합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### ⚠️ 사전 요구사항
# MAGIC - **02_structured_feature_engineering** 노트북을 먼저 실행해야 합니다
# MAGIC - `lgit_pm_training` 테이블이 존재해야 합니다 (02번에서 생성됨)
# MAGIC - 테이블 없이 실행하면 오류가 발생합니다

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost shap --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %md
# MAGIC > **안내:** 패키지를 설치하고 Python 환경을 재시작합니다. 잠시 멈추는 것은 정상입니다.

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC > **환경 설정 완료.** `catalog`, `db`, `current_user` 변수를 사용할 수 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. MLflow 실험 설정
# MAGIC
# MAGIC ### 실험(Experiment)이란?
# MAGIC
# MAGIC **MLflow 실험(Experiment)** 은 과학자의 **실험 노트** 와 같습니다.
# MAGIC
# MAGIC 제조 현장에서 새로운 공정 조건을 테스트할 때, 엔지니어는 실험 노트에 "어떤 조건으로 테스트했는지, 결과가 어땠는지"를 꼼꼼히 기록합니다.
# MAGIC AI/ML에서도 마찬가지입니다. 모델을 학습시킬 때마다 다양한 조건(파라미터)을 바꿔가며 시도하는데,
# MAGIC 이 모든 시도를 체계적으로 기록하고 비교할 수 있게 해주는 것이 **MLflow 실험** 입니다.
# MAGIC
# MAGIC ### 왜 실험 추적이 중요한가?
# MAGIC
# MAGIC - **재현성(Reproducibility):** "3개월 전에 만든 모델이 왜 성능이 좋았지?" → 실험 기록을 보면 당시의 파라미터, 데이터, 결과를 그대로 확인할 수 있습니다
# MAGIC - **비교:** 여러 번의 학습 실행(Run)을 표로 나란히 비교하여, 어떤 조건이 최적인지 한눈에 파악합니다
# MAGIC - **팀 협업:** 팀원 누구나 실험 결과를 열람할 수 있어, "이 모델 어떻게 만들었어?"라는 질문에 즉시 답할 수 있습니다
# MAGIC
# MAGIC > **현장 경험담:** 실험 추적 없이 ML 프로젝트를 하면 반드시 "그때 어떤 설정으로 했더라?" 하는 순간이 옵니다. 경험상 3개월에 한 번은 이런 상황이 발생합니다. 특히 제조 현장에서는 "지난번에 잘 되던 모델이 왜 갑자기 안 되지?"라는 질문에 답할 수 있어야 하는데, 실험 기록 없이는 불가능합니다. MLflow는 이 문제를 근본적으로 해결합니다.
# MAGIC
# MAGIC ### 자동으로 기록되는 것들
# MAGIC - **파라미터(Parameters):** 학습에 사용한 설정값 (예: 학습률 0.1, 트리 깊이 6)
# MAGIC - **메트릭(Metrics):** 모델의 성능 수치 (예: 정확도 95%, F1 점수 0.87)
# MAGIC - **아티팩트(Artifacts):** 학습된 모델 파일, 그래프 이미지 등
# MAGIC - **소스 코드:** 어떤 노트북에서 실행되었는지
# MAGIC
# MAGIC > **Databricks 워크스페이스 좌측 사이드바 > Experiments** 에서 실험 결과를 실시간으로 확인할 수 있습니다.

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
# MAGIC ### 데이터 계보란?
# MAGIC
# MAGIC **데이터 계보(Data Lineage)** 란 "이 모델은 정확히 어떤 데이터의 어떤 버전으로 학습되었는가?"를 추적하는 것입니다.
# MAGIC
# MAGIC **제조 비유:** 완성된 제품에 문제가 발생했을 때, LOT 번호를 추적하여 "어떤 원자재를, 어떤 공정에서, 언제 사용했는지"를 역추적하는 것과 동일한 개념입니다.
# MAGIC AI 모델도 마찬가지로, 모델이 이상한 예측을 하면 "학습에 사용된 데이터에 문제가 있었는지"를 추적해야 합니다.
# MAGIC
# MAGIC ### MLflow Data Lineage가 기록하는 것
# MAGIC - **어떤 테이블:** Unity Catalog의 정확한 테이블명 (예: `lgit_mlops.default.lgit_pm_training`)
# MAGIC - **어떤 버전:** Delta Lake의 테이블 버전 번호 (데이터가 변경될 때마다 버전이 올라감)
# MAGIC - **언제:** 학습이 실행된 시점
# MAGIC
# MAGIC 이를 통해 모델 문제 발생 시 **근본 원인 분석(RCA)** 이 가능합니다.
# MAGIC 예를 들어, "이번 주부터 모델 예측이 이상해졌다" → 데이터 계보를 확인하면 "학습 데이터의 센서 범위가 변경되었구나"를 빠르게 파악할 수 있습니다.
# MAGIC
# MAGIC > **현장 경험담:** 실제 프로젝트에서 모델 성능이 갑자기 떨어진 적이 있었습니다. 원인을 추적해보니 데이터 파이프라인 업스트림에서 센서 단위가 바뀌어 있었습니다(섭씨 → 화씨). 데이터 계보가 없었다면 이 원인을 찾는 데 며칠이 걸렸을 것입니다. Lineage가 있으면 "이 모델은 어떤 버전의 데이터로 학습되었는가"를 즉시 확인하고, 해당 시점의 데이터 변경 이력을 역추적할 수 있습니다.

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
# MAGIC
# MAGIC ### X(입력 피처)와 Y(정답 레이블) 분리
# MAGIC
# MAGIC AI/ML 모델 학습의 핵심 원리는 간단합니다:
# MAGIC - **X (입력 피처, Features):** 모델에게 주어지는 "문제" - 센서가 측정한 값들 (온도, 토크, 회전속도 등)
# MAGIC - **Y (정답 레이블, Label):** 모델이 맞혀야 하는 "정답" - 이 설비가 실제로 고장났는가? (0=정상, 1=고장)
# MAGIC
# MAGIC 학교 시험에 비유하면, X는 "시험 문제"이고, Y는 "정답지"입니다.
# MAGIC 모델은 X와 Y의 관계를 학습하여, 나중에 새로운 X(센서 데이터)만 보고도 Y(고장 여부)를 예측할 수 있게 됩니다.
# MAGIC
# MAGIC ### toPandas()란?
# MAGIC
# MAGIC Databricks에서 데이터는 기본적으로 **Spark DataFrame** 형태로 존재합니다.
# MAGIC Spark는 대용량 데이터를 여러 서버에 분산하여 처리하는 엔진으로, 수억 건의 데이터도 처리할 수 있습니다.
# MAGIC 하지만 XGBoost 같은 ML 라이브러리는 **Pandas DataFrame** (단일 서버 메모리)을 사용합니다.
# MAGIC `toPandas()`는 분산된 데이터를 하나의 서버로 모으는 작업입니다.
# MAGIC
# MAGIC > **주의:** 데이터가 너무 크면(수백만 건 이상) `toPandas()` 시 메모리 부족이 발생할 수 있습니다.
# MAGIC > 대규모 데이터에서는 Spark ML이나 분산 학습(Distributed Training)을 사용합니다.
# MAGIC
# MAGIC ### 사용되는 피처(Features) 설명
# MAGIC
# MAGIC | 피처명 | 의미 | 고장 예측에서의 역할 |
# MAGIC |--------|------|---------------------|
# MAGIC | `air_temperature_k` | 공기 온도 (켈빈) | 과열 감지 |
# MAGIC | `process_temperature_k` | 공정 온도 (켈빈) | 공정 이상 감지 |
# MAGIC | `rotational_speed_rpm` | 회전 속도 (RPM) | 설비 부하 상태 |
# MAGIC | `torque_nm` | 토크 (Nm) | 기계적 부하/스트레스 |
# MAGIC | `tool_wear_min` | 공구 마모 시간 (분) | 공구 수명 예측 |
# MAGIC | `temp_diff`, `power`, `strain` 등 | 02번에서 만든 파생 피처 | 센서 간 상호작용 패턴 |

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

# .pop(): machine_failure 컬럼을 X에서 분리하여 Y(정답)에 저장
Y_train = X_train.pop(label_col)
Y_test = X_test.pop(label_col)

print(f"학습 데이터: {len(X_train)} rows, 테스트 데이터: {len(X_test)} rows")
print(f"고장 비율 - 학습: {Y_train.mean():.4f}, 테스트: {Y_test.mean():.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. XGBoost 모델 학습
# MAGIC
# MAGIC ### XGBoost란?
# MAGIC
# MAGIC **XGBoost (eXtreme Gradient Boosting)** 는 현재 정형 데이터(테이블 형태 데이터) 분석에서 **가장 널리 사용되는 ML 알고리즘** 중 하나입니다.
# MAGIC
# MAGIC > **현장 경험담:**XGBoost를 선택한 이유를 솔직히 말하면, 정형 데이터에서 이 알고리즘을 이긴 것을 거의 본 적이 없기 때문입니다. Kaggle 대회에서도, 실제 제조 프로젝트에서도 마찬가지입니다. 딥러닝이 대세라고 하지만, 센서 데이터 10,000건에 딥러닝을 쓰는 것은 대포로 파리를 잡는 격입니다. 딥러닝은 이미지, 텍스트, 시계열 수만 건 이상에서 빛을 발합니다. **정형 데이터 + 수천~수만 건 규모라면, XGBoost가 정답에 가장 가깝습니다.**
# MAGIC
# MAGIC 원리를 쉽게 설명하면:
# MAGIC 1. 먼저 간단한 의사결정 나무(Decision Tree) 하나를 만듭니다 - "토크가 40Nm 이상이면 고장 가능성 높음"
# MAGIC 2. 이 나무가 틀린 부분을 집중적으로 학습하는 **두 번째 나무** 를 추가합니다
# MAGIC 3. 두 번째 나무도 틀린 부분을 보완하는 **세 번째 나무** 를 추가합니다
# MAGIC 4. 이렇게 수십~수백 개의 나무가 **팀워크** 로 예측합니다
# MAGIC
# MAGIC **비유:** 한 명의 전문가보다 여러 명의 일반 전문가가 모여 토론하면 더 정확한 판단을 내리는 것과 같습니다.
# MAGIC 이것을 **앙상블(Ensemble)** 기법이라고 부릅니다.
# MAGIC
# MAGIC ### 주요 하이퍼파라미터 설명
# MAGIC
# MAGIC 하이퍼파라미터란, 모델 학습 **전에** 사람이 미리 정해주는 설정값입니다. 공정에서 온도, 압력, 시간을 설정하는 것과 비슷합니다.
# MAGIC
# MAGIC | 파라미터 | 의미 | 제조 비유 |
# MAGIC |----------|------|----------|
# MAGIC | `max_depth` (6) | 각 의사결정 나무의 최대 깊이 | 의사결정 단계 수. 너무 깊으면 학습 데이터에만 과적합 |
# MAGIC | `learning_rate` (0.1) | 각 나무가 기여하는 정도 | 보정 강도. 너무 크면 불안정, 너무 작으면 학습이 느림 |
# MAGIC | `n_estimators` (200) | 나무의 총 개수 | 투표에 참여하는 전문가 수 |
# MAGIC | `subsample` (0.8) | 각 나무가 사용할 데이터 비율 | 80%만 보고 판단하게 하여, 다양한 관점 확보 |
# MAGIC | `scale_pos_weight` | 고장 데이터 가중치 | 고장 사례가 적으므로 더 중요하게 학습 |
# MAGIC | `early_stopping_rounds` (20) | 성능 개선이 없으면 조기 종료 | 더 이상 개선되지 않으면 학습을 멈춰 과적합 방지 |
# MAGIC
# MAGIC > **현장 경험담 - scale_pos_weight:** 불균형 데이터 처리에서 가장 흔한 실수는 Accuracy에 속는 것입니다. 고장률 3.4%인 데이터에서 모든 것을 '정상'으로 예측해도 Accuracy 96.6%입니다. 보고서에 "정확도 96.6%"라고 쓰면 경영진은 감탄하겠지만, 이런 모델은 고장을 단 하나도 잡지 못하므로 **완전히 쓸모가 없습니다** . `scale_pos_weight`는 이 함정을 피하는 첫 번째 방법입니다. 소수 클래스(고장)의 오분류에 더 큰 패널티를 부여해서, 모델이 고장 케이스를 무시하지 못하게 만듭니다.
# MAGIC
# MAGIC ### MLflow Autolog - 한 줄의 마법
# MAGIC
# MAGIC `mlflow.xgboost.autolog()`은 **단 한 줄의 코드** 만으로 학습 과정의 모든 것을 자동 기록합니다:
# MAGIC - 위의 모든 하이퍼파라미터 값
# MAGIC - 매 학습 라운드마다의 성능 변화 (loss 곡선)
# MAGIC - 피처 중요도 (어떤 센서가 가장 중요했는지)
# MAGIC - 학습 소요 시간
# MAGIC
# MAGIC > **현장 경험담 - Autolog:**MLflow를 10년 가까이 써온 입장에서, Autolog은 게임 체인저였습니다. 이전에는 모든 실험마다 수동으로 파라미터를 기록했는데, 빠뜨리는 경우가 빈번했습니다. "그때 어떤 설정으로 했더라?" 하는 상황이 3개월에 한 번은 발생했습니다. 특히 여러 사람이 같은 프로젝트에서 실험을 돌릴 때, 기록 형식이 제각각이라 비교가 불가능한 경우도 많았습니다. Autolog은 이 모든 것을 표준화된 형식으로 자동 기록합니다. **한 줄의 코드가 수십 시간의 삽질을 방지합니다.**
# MAGIC
# MAGIC > **기존 방식 vs Databricks:** 전통적으로는 엔지니어가 학습 로그를 직접 파일로 저장하고, Excel에 정리해야 했습니다.
# MAGIC > Autolog을 사용하면 이 모든 과정이 자동화되어, 엔지니어는 모델 개발에만 집중할 수 있습니다.

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
            "objective": "binary:logistic",  # 이진 분류(0/1) 문제임을 XGBoost에 알림
            "eval_metric": ["logloss", "auc", "error"],
            "scale_pos_weight": scale_pos_weight,  # 고장 케이스(1)가 적으므로 가중치 부여하여 균형 보정
            "tree_method": "hist",  # 히스토그램 기반 분할: 대규모 데이터에 빠름
            "seed": 42
        }
        default_params.update(params)

        # 모델 학습
        model = xgb.train(
            default_params,
            dtrain,
            num_boost_round=params.get("num_boost_round", 200),
            evals=[(dtrain, "train"), (dval, "val")],
            early_stopping_rounds=20,  # 20라운드 연속 성능 개선 없으면 학습 조기 종료
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

        # F1 Score는 0~1 범위, 1에 가까울수록 좋음.
        # 불균형 데이터에서는 Accuracy보다 F1/PR-AUC가 더 신뢰할 수 있는 지표입니다.

        # 모델 Signature 생성 및 기록
        # 모델의 입력/출력 형식을 자동 감지하여 기록 → 다른 사람이 이 모델을 쓸 때 형식을 알 수 있음
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
# MAGIC
# MAGIC **Baseline(기준선)** 이란 "비교의 기준이 되는 첫 번째 모델"입니다.
# MAGIC 제조 공정에서 현재 수율이 95%라면, 이것이 Baseline이고, 새로운 공정 조건을 적용한 후 "95%보다 좋아졌는가?"를 비교합니다.
# MAGIC 마찬가지로, 먼저 기본 파라미터로 모델을 학습시킨 뒤, 다양한 조합을 시도하여 더 나은 모델을 찾습니다.
# MAGIC
# MAGIC > **현장 경험담:** Baseline 없이 바로 복잡한 모델로 뛰어드는 주니어 엔지니어를 많이 봤습니다. 그러면 나중에 "이 모델이 정말 좋은 건가, 아니면 원래 쉬운 문제인 건가?"를 판단할 수 없습니다. 항상 Baseline부터 시작하세요. 가끔은 Baseline이 이미 충분히 좋아서 더 복잡한 모델이 필요 없는 경우도 있습니다. 그것을 아는 것 자체가 중요한 발견입니다.

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
# MAGIC ### 하이퍼파라미터 튜닝이란?
# MAGIC
# MAGIC 위에서 Baseline 모델을 학습했지만, "이 파라미터 조합이 정말 최적인가?"는 알 수 없습니다.
# MAGIC **하이퍼파라미터 튜닝(HPO, Hyperparameter Optimization)** 은 다양한 파라미터 조합을 체계적으로 시도하여
# MAGIC 가장 성능이 좋은 조합을 찾는 과정입니다.
# MAGIC
# MAGIC **제조 비유:** 새로운 제품의 최적 공정 조건(온도, 압력, 시간)을 찾기 위해 DOE(Design of Experiments)를 수행하는 것과 같습니다.
# MAGIC
# MAGIC > **현장 경험담:** 솔직히 말하면, 현업에서는 하이퍼파라미터 튜닝에 너무 많은 시간을 쓰지 않는 것이 좋습니다. 경험상 **80%의 성능은 디폴트 파라미터로 나오고, 튜닝으로 얻는 개선은 보통 2~5%입니다.**그 시간에 피처를 하나 더 만드는 것이 훨씬 효과적입니다. 실제 프로젝트에서 성능을 극적으로 개선한 것은 항상 "새로운 피처 발견"이었지, 파라미터 미세 조정이 아니었습니다. HPO는 **마지막 1~2%를 짜낼 때** 하는 것이고, 그 전에 데이터와 피처를 충분히 탐색했는지 먼저 점검하세요.
# MAGIC
# MAGIC 아래에서는 3가지 파라미터 조합을 시도합니다. MLflow에 모든 실행이 자동 기록되므로,
# MAGIC Experiments UI에서 4개 모델(Baseline + 3개 HPO)을 표로 나란히 비교할 수 있습니다.
# MAGIC
# MAGIC > **Databricks 장점:** 대규모 HPO 시, Databricks의 분산 컴퓨팅을 활용하면 수백 가지 조합을 동시에 실행할 수 있습니다.
# MAGIC > Hyperopt, Optuna 등의 자동 탐색 라이브러리와도 쉽게 통합됩니다.

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
# MAGIC ### Databricks UI 확인 포인트
# MAGIC
# MAGIC 1. **좌측 사이드바 > Experiments** 클릭
# MAGIC 2. `lgit_predictive_maintenance` 실험 클릭
# MAGIC 3. **Run 목록** 에서 여러 실행 결과를 비교 (F1, AUC 컬럼 정렬)
# MAGIC 4. 최적 Run 클릭 > **Parameters** 탭: 하이퍼파라미터 값 확인
# MAGIC 5. **Metrics** 탭: 학습 곡선 (loss 그래프) 확인
# MAGIC 6. **Artifacts** 탭: 모델 파일, requirements.txt, SHAP plot 확인
# MAGIC 7. 여러 Run을 체크 > **Compare** 버튼: 성능 비교 차트 자동 생성
# MAGIC
# MAGIC > **팁**: Artifacts > shap_summary_plot.png 를 클릭하면 피처 중요도 시각화를 바로 볼 수 있습니다

# COMMAND ----------

# MAGIC %md
# MAGIC > **실험 결과 확인 방법:**
# MAGIC > 1. 좌측 사이드바에서 **Experiments** 아이콘을 클릭합니다
# MAGIC > 2. `lgit_predictive_maintenance` 실험을 선택합니다
# MAGIC > 3. 4개의 Run(Baseline + HPO 3개)이 목록에 표시됩니다
# MAGIC > 4. 비교하고 싶은 Run을 체크한 후 **Compare** 버튼을 클릭하면, 파라미터와 메트릭을 표와 차트로 비교할 수 있습니다
# MAGIC >
# MAGIC > 이 비교 기능 덕분에 "어떤 파라미터 조합이 가장 좋은 성능을 냈는지" 한눈에 파악할 수 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. SHAP 기반 모델 해석 - "모델이 왜 그런 판단을 내렸는가?"
# MAGIC
# MAGIC ### SHAP이란?
# MAGIC
# MAGIC **SHAP (SHapley Additive exPlanations)** 은 AI 모델의 예측을 **해석** 하는 기술입니다.
# MAGIC
# MAGIC AI 모델이 "이 설비가 고장날 것이다"라고 예측했을 때, 현장 엔지니어가 가장 궁금한 것은 **"왜?"** 입니다.
# MAGIC SHAP은 각 입력 피처(센서값)가 예측 결과에 **얼마나 기여했는지** 를 수치로 보여줍니다.
# MAGIC
# MAGIC > **현장 경험담:**SHAP의 진짜 가치는 기술적인 것이 아니라 **비즈니스적인 것** 입니다. 공장장에게 "AI가 이 설비가 위험하다고 합니다"라고 하면 십중팔구 의심합니다. "근거가 뭔데?" 하고 물어봅니다. 하지만 "AI가 **토크 72Nm(정상 대비 150%)과 공구 마모 215분(교체 기준 초과)** 을 근거로 위험하다고 판단했습니다"라고 하면 신뢰합니다. 왜냐하면 현장 엔지니어의 경험적 직관과 일치하기 때문입니다. SHAP은 AI와 현장 사이의 **신뢰 다리** 를 놓는 도구입니다.
# MAGIC
# MAGIC ### 제조 현장에서의 실제 활용
# MAGIC
# MAGIC 예를 들어, 모델이 특정 설비에 대해 "고장 확률 87%"라고 예측했을 때, SHAP 분석 결과가 다음과 같다면:
# MAGIC
# MAGIC | 피처 | SHAP 값 | 해석 |
# MAGIC |------|---------|------|
# MAGIC | `torque_nm` = 68.2 | +0.35 | 토크가 비정상적으로 높음 → 고장 방향으로 크게 기여 |
# MAGIC | `tool_wear_min` = 215 | +0.28 | 공구 마모가 심함 → 고장 방향으로 기여 |
# MAGIC | `rotational_speed_rpm` = 1200 | -0.05 | 회전속도는 정상 범위 → 고장 예측에 거의 영향 없음 |
# MAGIC
# MAGIC 이 결과를 바탕으로 정비 엔지니어에게 이렇게 보고할 수 있습니다:
# MAGIC > "모델이 이 설비의 고장을 예측한 주요 원인은 **토크가 비정상적으로 높고**, **공구 마모가 심하기** 때문입니다.
# MAGIC > 우선 공구 교체를 권장하며, 토크 이상의 원인을 점검해주세요."
# MAGIC
# MAGIC ### SHAP이 중요한 이유
# MAGIC
# MAGIC - **신뢰 구축:** "AI가 그냥 고장난다고 했어요"보다 "토크와 마모 때문에 고장 예측됨"이 훨씬 설득력 있습니다
# MAGIC - **조치 가능성:** 어떤 센서가 문제인지 알면, 구체적인 정비 조치를 취할 수 있습니다
# MAGIC - **감사/규제 대응:** 왜 그런 판단을 내렸는지 설명할 수 있어, 품질 감사에 대응 가능합니다
# MAGIC
# MAGIC > **현장 팁:**SHAP 결과를 현장에 전달할 때는 반드시 **도메인 언어** 로 번역하세요. "SHAP value +0.35"라고 하면 아무도 이해 못합니다. "토크가 정상 범위(30~50Nm)를 크게 벗어나 68.2Nm이며, 이것이 고장 예측의 가장 큰 원인입니다"라고 해야 합니다. 기술 지표를 현장 언어로 바꾸는 것이 ML 엔지니어의 핵심 역량입니다.
# MAGIC
# MAGIC 아래에서 두 가지 시각화를 생성합니다:
# MAGIC 1. **Summary Plot:** 전체적으로 어떤 피처가 가장 중요한지 (피처 중요도 순위)
# MAGIC 2. **개별 예측 해석:** 고장으로 예측된 특정 사례에서 각 피처의 기여도

# COMMAND ----------

# DBTITLE 1,SHAP 값 계산 및 시각화
import shap

# 최적 모델로 SHAP 값 계산
best_model = best_result['model']
explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test)

# SHAP Summary Plot (피처 중요도)
# SHAP 값의 절대값이 클수록 해당 피처의 영향력이 큼. 양수=고장 방향, 음수=정상 방향
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
# MAGIC ## 6. 임계값 최적화 & 모델 캘리브레이션 (Threshold Optimization & Calibration)
# MAGIC
# MAGIC > **20년차 현업 팁** : 대부분의 팀이 XGBoost의 예측 확률을 0.5 기준으로 이진 분류합니다. 하지만 이것은 **거의 항상 최적이 아닙니다.** 특히 고장 예측처럼 놓치는 것(FN)이 오탐(FP)보다 훨씬 비싼 경우, 임계값을 낮춰서 Recall을 높이는 것이 비즈니스적으로 올바릅니다.
# MAGIC
# MAGIC ### 임계값이란?
# MAGIC - 모델이 "고장 확률 0.65"를 출력했을 때, 이것을 "고장"으로 판정할지 "정상"으로 판정할지의 기준선
# MAGIC - 기본값 0.5는 FP와 FN의 비용이 같다고 가정 — **제조에서는 거의 해당하지 않음**
# MAGIC
# MAGIC ### 캘리브레이션이란?
# MAGIC - 모델이 "고장 확률 80%"라고 출력하면, 실제로 100건 중 80건이 고장이어야 함
# MAGIC - XGBoost의 raw probability는 종종 **과신(overconfident)** 하거나 **과소(underconfident)** 함
# MAGIC - Platt Scaling, Isotonic Regression으로 보정 가능

# COMMAND ----------

# DBTITLE 1,PR 곡선 기반 최적 임계값 탐색
from sklearn.metrics import precision_recall_curve
import numpy as np

# 테스트 데이터 예측 확률 (X_test/Y_test는 학습 함수 외부에서 정의된 홀드아웃 테스트셋)
y_pred_proba = best_model.predict(xgb.DMatrix(X_test, feature_names=feature_columns))

# PR 곡선 계산
precisions, recalls, thresholds = precision_recall_curve(Y_test, y_pred_proba)

# Recall >= 0.8을 만족하는 최적 임계값 (Precision이 가장 높은 것)
target_recall = 0.8
valid_idx = np.where(recalls[:-1] >= target_recall)[0]
if len(valid_idx) > 0:
    best_idx = valid_idx[np.argmax(precisions[:-1][valid_idx])]
    optimal_threshold = thresholds[best_idx]
    print(f"✅ 최적 임계값: {optimal_threshold:.3f} (Recall={recalls[best_idx]:.3f}, Precision={precisions[best_idx]:.3f})")
    print(f"   기본 임계값 0.5 대비 Recall 향상: {recalls[best_idx] - 0.5:.3f}")
else:
    optimal_threshold = 0.5
    print(f"⚠️ Recall >= {target_recall}을 만족하는 임계값을 찾지 못했습니다. 기본값 0.5 사용")

# MLflow에 최적 임계값 기록
mlflow.log_metric("optimal_threshold", optimal_threshold)
mlflow.log_metric("optimal_recall", float(recalls[best_idx]) if len(valid_idx) > 0 else 0.0)

# COMMAND ----------

# MAGIC %md
# MAGIC > **현업 팁** : 임계값은 비즈니스 요구사항에 따라 결정합니다.
# MAGIC > - **놓침이 치명적** (반도체, 자동차 부품) → 임계값 낮춤 (0.3~0.4) → Recall↑, Precision↓
# MAGIC > - **오탐 비용이 높음** (불필요 정비 비용 큼) → 임계값 높임 (0.6~0.7) → Precision↑, Recall↓
# MAGIC > - **최적점** : PR 곡선에서 비용함수를 최소화하는 점 = `cost = FN × 50000 + FP × 3000`

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC ### 이 노트북에서 수행한 작업
# MAGIC
# MAGIC | 단계 | 작업 내용 | 핵심 가치 |
# MAGIC |------|----------|----------|
# MAGIC | 1 | **MLflow 실험 설정** 및 데이터 계보(Lineage) 캡처 | 모든 학습 이력이 자동 기록되어 재현 가능 |
# MAGIC | 2 | **XGBoost Baseline 모델** 학습 (불균형 보정 포함) | 기준 성능 확보, 고장 사례 가중치 적용 |
# MAGIC | 3 | **하이퍼파라미터 튜닝** (3개 조합 탐색) | 최적 파라미터 탐색, MLflow에서 비교 |
# MAGIC | 4 | **SHAP 해석** : 피처 중요도 및 개별 예측 설명 | 현장 엔지니어에게 "왜 고장 예측인지" 설명 가능 |
# MAGIC | 5 | 모든 실험이 **MLflow에 자동 기록** | 팀 전체가 결과를 공유하고 감사에 대응 가능 |
# MAGIC
# MAGIC ### 핵심 메시지
# MAGIC
# MAGIC Databricks에서는 모델 학습 과정의 **모든 것** 이 자동으로 추적됩니다.
# MAGIC "어떤 데이터로, 어떤 파라미터로, 어떤 결과가 나왔는지"를 언제든 확인할 수 있으며,
# MAGIC SHAP을 통해 모델의 판단 근거까지 설명할 수 있습니다.
# MAGIC 이것이 **신뢰할 수 있는 AI** 의 첫걸음입니다.
# MAGIC
# MAGIC > **현장 경험담:** 제조 AI 프로젝트에서 가장 많이 실패하는 이유는 모델 성능이 낮아서가 아니라, **현장이 모델을 안 쓰기** 때문입니다. 모델이 F1 0.95를 달성해도, 현장 엔지니어가 "저거 믿을 수 없어"라고 하면 프로젝트는 실패입니다. 실험 추적(재현 가능성), 불균형 처리(실질적 성능), SHAP(설명 가능성)은 모두 **현장의 신뢰를 얻기 위한 도구** 입니다. 기술이 아니라 신뢰가 MLOps의 핵심입니다.
# MAGIC
# MAGIC **다음 단계:** [Unity Catalog 모델 등록]($./04_model_registration_uc) - 학습된 모델을 안전하게 저장하고, 버전 관리하며, 운영 환경에 배포하는 과정을 진행합니다.
