# Databricks notebook source
# MAGIC %md
# MAGIC # 멀티 알고리즘 비교 학습 (Multi-Algorithm Comparison)
# MAGIC
# MAGIC 본 노트북에서는 **동일한 데이터셋(AI4I 2020 예지보전)** 에 대해 **4가지 대표 ML 알고리즘** 을 학습하고,
# MAGIC MLflow의 실험 추적 기능을 활용하여 **과학적이고 공정하게 비교** 합니다.
# MAGIC
# MAGIC 이 과정은 실제 제조 현장에서 ML 모델을 도입할 때 반드시 거쳐야 하는 **알고리즘 선정(Algorithm Selection)** 단계입니다.
# MAGIC "어떤 알고리즘이 우리 데이터에 가장 적합한가?"에 대한 답을 **감이 아닌 데이터 기반으로** 도출합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 왜 여러 알고리즘을 비교해야 하나요? — No Free Lunch Theorem
# MAGIC
# MAGIC > **"No Free Lunch Theorem" (Wolpert & Macready, 1997)** :
# MAGIC > 수학적으로 증명된 정리로, **모든 문제에 최적인 단일 알고리즘은 존재하지 않습니다.**
# MAGIC
# MAGIC **제조 현장 비유** : 이것은 마치 "모든 공정에 최적인 단 하나의 공구"가 없는 것과 같습니다.
# MAGIC 드릴링에는 드릴이, 절삭에는 밀링 커터가, 연마에는 그라인더가 각각 최적입니다.
# MAGIC ML 알고리즘도 마찬가지입니다:
# MAGIC
# MAGIC - **데이터 크기** 에 따라 최적 알고리즘이 다릅니다 (1만 건 vs 1억 건)
# MAGIC - **피처 유형** 에 따라 다릅니다 (연속형 센서값 vs 범주형 설비 코드)
# MAGIC - **클래스 불균형 정도** 에 따라 다릅니다 (고장률 3% vs 30%)
# MAGIC - **노이즈 수준** 에 따라 다릅니다 (정밀 센서 vs 노후 센서)
# MAGIC
# MAGIC 따라서 **동일한 데이터, 동일한 전처리, 동일한 평가 기준** 으로 여러 알고리즘을 비교하여
# MAGIC **데이터에 가장 잘 맞는 알고리즘** 을 선택해야 합니다. 이것이 바로 이 노트북의 목적입니다.
# MAGIC
# MAGIC ### 비교 대상 알고리즘 — 4가지 접근법
# MAGIC
# MAGIC 아래 4개 알고리즘은 현재 **정형 데이터(Tabular Data) 분류/회귀에서 세계적으로 가장 널리 사용** 되는 알고리즘입니다.
# MAGIC Kaggle 데이터 과학 대회에서도 상위 솔루션의 **80% 이상** 이 이들 중 하나 이상을 사용합니다.
# MAGIC
# MAGIC | 알고리즘 | 핵심 원리 | 개발 | 특징 | 제조 적합성 |
# MAGIC |----------|----------|------|------|-----------|
# MAGIC | **XGBoost**| Gradient Boosting + L1/L2 정규화 | 2014, Tianqi Chen | **산업 표준**, 가장 검증된 알고리즘 | 범용 고장 예측의 첫 번째 선택지 |
# MAGIC | **LightGBM**| Leaf-wise 성장 + GOSS/EFB | 2017, Microsoft | **최고 속도**, 대용량 데이터 특화 | 수백만 행 센서 로그 처리 |
# MAGIC | **CatBoost**| Ordered Boosting + 범주형 자동 인코딩 | 2017, Yandex | **범주형 피처 최강**, 과적합 방지 | 설비 타입, 제품 등급 등 범주형 다수 |
# MAGIC | **Random Forest**| 배깅(Bagging) + 랜덤 피처 선택 | 2001, Leo Breiman | **안정적, 해석 쉬움**, 과적합에 강함 | 초기 탐색, 피처 중요도 분석 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Databricks에서 알고리즘 비교가 특별한 이유
# MAGIC
# MAGIC 엑셀이나 Jupyter Notebook에서도 알고리즘 비교는 가능합니다. 하지만 Databricks의 **MLflow 통합** 은
# MAGIC 비교 과정을 **재현 가능하고 체계적으로** 관리할 수 있게 합니다.
# MAGIC
# MAGIC | Databricks 기능 | 설명 | 제조 현장 가치 |
# MAGIC |----------------|------|-------------|
# MAGIC | **MLflow Experiment**| 모든 학습 실행(파라미터, 메트릭, 모델)을 자동 기록 | "왜 이 알고리즘을 선택했는가?"에 대한 **감사(Audit) 추적** 가능 |
# MAGIC | **MLflow Autolog**| 코드 한 줄 추가 없이 모든 정보 자동 기록 | 기록 누락 방지, **실수 없는** 실험 관리 |
# MAGIC | **MLflow UI Compare**| 여러 Run을 선택하여 **차트로 즉시 비교**| 경영진/설비팀에 **시각적으로** 결과 공유 |
# MAGIC | **Model Registry**| 선택된 모델을 버전 관리하며 운영 배포 | 개발 → 스테이징 → 프로덕션 **단계별 승인 체계** |

# COMMAND ----------

# MAGIC %md
# MAGIC ### 사전 지식: Gradient Boosting이란?
# MAGIC
# MAGIC **Gradient Boosting** 은 여러 개의 약한 학습기(주로 결정 트리)를 **순차적으로** 학습시키는 앙상블 기법입니다.
# MAGIC 2001년 Jerome Friedman이 제안한 이 기법은, 현재까지도 정형 데이터 분석에서 **가장 강력한 알고리즘 패밀리** 입니다.
# MAGIC
# MAGIC **제조 비유로 이해하기** :
# MAGIC
# MAGIC 품질 검사 라인에 200명의 검사원이 있다고 상상해보세요.
# MAGIC
# MAGIC ```
# MAGIC 1단계: 1번 검사원이 제품을 검사 → 10개 오판 (8개 불량을 양품으로, 2개 양품을 불량으로)
# MAGIC 2단계: 2번 검사원은 1번이 틀린 10개에 특히 집중하여 검사 → 4개 추가 정정, 나머지 6개 오판
# MAGIC 3단계: 3번 검사원은 2번이 틀린 6개에 집중 → 3개 추가 정정...
# MAGIC ...
# MAGIC 200단계: 200번 검사원까지 순차적으로 보완
# MAGIC
# MAGIC 최종 판정 = 200명 모든 검사원의 의견을 합산하여 결정
# MAGIC
# MAGIC 핵심은 **"이전 검사원의 실수에 집중하여 보완한다"** 는 것입니다.
# MAGIC 이것이 "Gradient(경사)" + "Boosting(강화)"의 의미입니다.
# MAGIC
# MAGIC ### Boosting vs Bagging — 두 가지 앙상블 철학
# MAGIC
# MAGIC | 구분 | Boosting (순차 학습) | Bagging (병렬 학습) |
# MAGIC |------|---------------------|-------------------|
# MAGIC | **비유**| 검사원들이 **릴레이** 처럼 순차적으로 보완 | 검사원들이 **독립적으로** 검사 후 다수결 |
# MAGIC | **대표 알고리즘** | XGBoost, LightGBM, CatBoost | Random Forest |
# MAGIC | **학습 방식** | 이전 모델의 오차를 다음 모델이 학습 | 각 모델이 랜덤 서브셋으로 독립 학습 |
# MAGIC | **장점**| 일반적으로 **더 높은 정확도**| **안정적**, 과적합에 강함 |
# MAGIC | **단점** | 과적합 위험, 학습 시간 길음 | 정확도 한계 |
# MAGIC | **제조 적합성**| 최고 성능이 필요한 **운영 모델**| 빠른 탐색, **피처 중요도 분석** |

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost lightgbm catboost shap --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 데이터 준비 — 공정한 비교의 기본 원칙
# MAGIC
# MAGIC 02번 노트북에서 준비한 피처 테이블을 로드합니다.
# MAGIC
# MAGIC **공정한 알고리즘 비교를 위한 3가지 원칙** :
# MAGIC
# MAGIC 1. **동일한 데이터** : 모든 알고리즘이 **완전히 동일한** 학습/검증/테스트 데이터를 사용
# MAGIC 2. **동일한 전처리** : 피처 엔지니어링, 스케일링 등이 모든 알고리즘에 동일하게 적용
# MAGIC 3. **동일한 평가 기준** : F1, AUC, Recall, Precision을 동일 테스트셋으로 계산
# MAGIC
# MAGIC 이 중 하나라도 다르면 **사과와 오렌지를 비교하는 것** 과 같아서, 알고리즘 자체의 성능 차이를 알 수 없습니다.
# MAGIC
# MAGIC > **참고** : `stratify=Y_train` 옵션으로 학습/검증 분할 시 **고장 비율을 동일하게 유지** 합니다.
# MAGIC > 이것이 없으면, 우연히 검증셋에 고장 데이터가 몰리거나 빠져서 평가가 왜곡될 수 있습니다.

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
# MAGIC ### MLflow 실험이란? — ML의 "실험 노트"
# MAGIC
# MAGIC **MLflow 실험(Experiment)** 은 여러 번의 학습 실행(Run)을 묶어서 관리하는 컨테이너입니다.
# MAGIC 제조 비유로, 품질 시험에서 여러 조건(온도, 압력, 시간)을 바꿔가며 시험하고,
# MAGIC 그 결과를 **시험 성적서** 에 기록하는 것과 같습니다.
# MAGIC
# MAGIC 실험: **"lgit_multi_algorithm_comparison"** (시험 성적서, 하나의 실험 단위)
# MAGIC - Run 1: XGBoost (F1=0.85, AUC=0.92) — 1번 시험 조건 + 결과
# MAGIC - Run 2: LightGBM (F1=0.87, AUC=0.93) — 2번 시험 조건 + 결과
# MAGIC - Run 3: CatBoost (F1=0.86, AUC=0.94) — 3번 시험 조건 + 결과
# MAGIC - Run 4: RandomForest (F1=0.82, AUC=0.90) — 4번 시험 조건 + 결과
# MAGIC
# MAGIC ### 각 Run에 자동 기록되는 정보
# MAGIC
# MAGIC | 기록 항목 | 내용 | 제조 비유 |
# MAGIC |----------|------|----------|
# MAGIC | **파라미터 (Parameters)** | max_depth=6, learning_rate=0.1 등 | 시험 조건 (온도 150도, 시간 30분) |
# MAGIC | **메트릭 (Metrics)** | F1=0.85, AUC=0.92, Recall=0.78 등 | 시험 결과 (불량률, 강도, 수율) |
# MAGIC | **모델 아티팩트 (Artifacts)** | 학습된 모델 파일 (.pkl, .model) | 시험 결과물 (시제품, 샘플) |
# MAGIC | **소스 코드** | 학습에 사용된 노트북 링크 | 시험 절차서 |
# MAGIC | **태그 (Tags)** | project=lgit, type=comparison 등 | 시험 분류 라벨 |
# MAGIC
# MAGIC > **왜 MLflow가 강력한가?** : 전통적으로 ML 실험 결과는 엑셀에 수작업으로 기록했습니다.
# MAGIC > 이는 기록 누락, 재현 불가, 버전 혼란의 원인이 됩니다.
# MAGIC > MLflow는 **코드 실행과 동시에 자동으로 모든 정보를 기록** 하여 이 문제를 완전히 해결합니다.
# MAGIC > Databricks 노트북의 **오른쪽 패널 > 실험 아이콘(플라스크 모양)** 을 클릭하면 실시간으로 확인할 수 있습니다.

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
# MAGIC ### 주요 평가 메트릭 — 공장 품질검사 비유로 이해하기
# MAGIC
# MAGIC 공장에서 100개 제품을 검사한다고 가정합시다. 실제로 5개가 불량이고 95개가 양품입니다.
# MAGIC ML 모델이 "이것은 불량이다"라고 예측한 것이 8개였고, 그 중 4개가 진짜 불량, 4개가 양품(오탐)이었습니다.
# MAGIC
# MAGIC ```
# MAGIC                        모델 예측
# MAGIC                   불량(Positive)    양품(Negative)
# MAGIC 실제  불량(5개)     4개 (TP)         1개 (FN) ← 놓친 불량! 위험!
# MAGIC 결과  양품(95개)    4개 (FP)         91개 (TN)
# MAGIC                    ↑ 불필요 정비 발생
# MAGIC ```
# MAGIC
# MAGIC | 메트릭 | 계산 | 위 예시 값 | 공장 비유 | 제조 예지보전에서의 의미 |
# MAGIC |--------|------|-----------|----------|----------------------|
# MAGIC | **Recall (재현율)**| TP / (TP+FN) | 4/5 = **80%**| "실제 불량 5개 중 4개를 찾아냄" | **가장 중요!** 놓친 고장(FN)은 설비 파손/라인 정지 |
# MAGIC | **Precision (정밀도)**| TP / (TP+FP) | 4/8 = **50%**| "불량이라 한 8개 중 4개만 진짜 불량" | 낮으면 **불필요한 예방 정비** 비용 증가 |
# MAGIC | **F1 Score** | 2 * P * R / (P+R) | 2*0.5*0.8/(0.5+0.8) = **0.615**| Recall과 Precision의 균형점 | **종합 성능 지표** — 둘 다 높아야 높음 |
# MAGIC | **AUC-ROC**| ROC 커브 아래 면적 | (별도 계산 필요) | "분류 기준을 바꿔도 성능이 얼마나 일관적인가" | **전반적 분류 능력** — 임계값에 무관한 성능 |
# MAGIC
# MAGIC ### 제조 예지보전에서의 메트릭 우선순위
# MAGIC
# MAGIC | 관점 | Recall이 낮으면? (위험도) | Precision이 낮으면? (비용) |
# MAGIC |------|--------------------------|---------------------------|
# MAGIC | 결과 | 고장을 놓침 | 불필요한 정비 발생 |
# MAGIC | 영향 | 설비 파손/라인 정지 | 정비 비용 증가 |
# MAGIC | 손실 | 수억원 손실 가능 | 수백만원 비용 증가 |
# MAGIC | **결론** | **치명적!** | **아쉽지만 감수 가능** |
# MAGIC
# MAGIC > **따라서** : 제조 예지보전에서는 **Recall을 최우선** 으로 확보한 후,
# MAGIC > F1 Score를 통해 Precision과의 **균형을 최적화** 하는 것이 올바른 전략입니다.

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
# MAGIC 이제 4가지 알고리즘을 하나씩 학습합니다. 각 알고리즘은 **독립된 MLflow Run** 으로 기록되어,
# MAGIC 나중에 MLflow UI에서 **한 화면에서 모든 결과를 비교** 할 수 있습니다.
# MAGIC
# MAGIC 각 Track에서는 해당 알고리즘의 **탄생 배경, 핵심 원리, 강점/약점, 제조 적용 포인트** 를 설명합니다.
# MAGIC
# MAGIC ### 알고리즘 선택 의사결정 트리 — "우리 데이터에는 어떤 알고리즘이 좋을까?"
# MAGIC
# MAGIC - **Q1: 데이터에 범주형 변수가 많은가?** (설비 타입, 제품 등급, 작업자 ID 등)
# MAGIC   - YES → **CatBoost** (범주형 자동 인코딩, 전처리 최소화)
# MAGIC   - NO → Q2로
# MAGIC - **Q2: 데이터가 대용량인가?** (100만 행 이상)
# MAGIC   - YES → **LightGBM** (Leaf-wise 성장으로 2~10배 빠름)
# MAGIC   - NO → Q3로
# MAGIC - **Q3: 모델의 안정성과 해석이 중요한가?**
# MAGIC   - YES → **Random Forest** (과적합에 강하고 피처 중요도 제공)
# MAGIC   - NO → **XGBoost** (범용 최고 성능, 산업 표준)
# MAGIC
# MAGIC > **중요** : 위 의사결정 트리는 **출발점** 입니다. 실제로는 아래처럼 4개 모두 돌려보고
# MAGIC > **데이터가 알려주는 결과** 를 따르는 것이 가장 정확합니다. 그것이 이 노트북의 목적입니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Track 1: XGBoost — 산업 ML의 표준
# MAGIC
# MAGIC **XGBoost (eXtreme Gradient Boosting)**
# MAGIC
# MAGIC | 항목 | 내용 |
# MAGIC |------|------|
# MAGIC | **개발자** | Tianqi Chen (워싱턴대학교), 2014년 |
# MAGIC | **탄생 배경** | 기존 Gradient Boosting의 속도와 정규화를 개선하기 위해 개발 |
# MAGIC | **역사적 의의**| 2015~2017년 Kaggle 대회 우승 솔루션의 **60% 이상** 에서 사용, ML의 "산업 표준"으로 자리잡음 |
# MAGIC
# MAGIC **핵심 원리 (제조 비유)** :
# MAGIC - **L1/L2 정규화** : 검사 기준을 너무 엄격하게(과적합) 만들지 않도록 **브레이크** 역할
# MAGIC - **병렬 트리 구축** : 트리 내부의 분할점을 찾을 때 **여러 CPU 코어가 동시에** 탐색
# MAGIC - **결측치 자동 처리** : 센서 결측(통신 장애 등)이 있어도 **자동으로 최적 방향** 결정
# MAGIC
# MAGIC **강점** : 안정적 성능, 방대한 커뮤니티/문서, 거의 모든 데이터에서 상위권 성능
# MAGIC **약점** : LightGBM보다 학습 속도 느림, 범주형 피처 직접 처리 불가 (인코딩 필요)
# MAGIC
# MAGIC **제조 적용** : 설비 고장 예측, 공정 품질 분류 등 **범용적인 첫 번째 선택지** 로 가장 적합합니다.
# MAGIC 특히 모델의 신뢰성이 중요한 운영 환경에서, 오랜 검증 이력이 있는 XGBoost는 **안심하고 선택** 할 수 있습니다.

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
# MAGIC ### Track 2: LightGBM — 속도의 제왕
# MAGIC
# MAGIC **LightGBM (Light Gradient Boosting Machine)**
# MAGIC
# MAGIC | 항목 | 내용 |
# MAGIC |------|------|
# MAGIC | **개발자** | Microsoft Research, 2017년 (Ke et al.) |
# MAGIC | **탄생 배경** | XGBoost의 학습 속도 한계를 극복하기 위해 개발. Bing 검색 랭킹에 적용하기 위해 시작 |
# MAGIC | **역사적 의의**| 대용량 데이터 처리의 패러다임 전환. 현재 산업계에서 XGBoost와 함께 **양대 산맥** |
# MAGIC
# MAGIC **핵심 혁신 3가지 (제조 비유)** :
# MAGIC
# MAGIC 1. **Leaf-wise 성장** (vs XGBoost의 Level-wise):
# MAGIC    - XGBoost: 트리의 **같은 깊이를 한꺼번에** 확장 (층별 검사 — 1층 전체 → 2층 전체 → ...)
# MAGIC    - LightGBM: **가장 오차가 큰 리프를 먼저** 분할 (문제 있는 곳부터 집중 검사)
# MAGIC    - 결과: 같은 횟수의 분할로 **더 빠르게 성능 수렴**
# MAGIC
# MAGIC 2. **GOSS** (Gradient-based One-Side Sampling):
# MAGIC    - 오차(Gradient)가 큰 샘플은 전부 유지, 작은 샘플은 일부만 샘플링
# MAGIC    - 제조 비유: "확실한 양품은 일부만 재검사하고, 불량 의심 건은 전수 검사"
# MAGIC    - 결과: 데이터 양을 줄이면서 **정보 손실 최소화**
# MAGIC
# MAGIC 3. **EFB** (Exclusive Feature Bundling):
# MAGIC    - 동시에 0이 아닌 값을 갖지 않는 피처들을 묶어서 처리
# MAGIC    - 제조 비유: "A 공정과 B 공정이 동시에 가동되지 않으면, 하나의 변수로 통합 가능"
# MAGIC    - 결과: **고차원 데이터의 차원을 자동 축소**
# MAGIC
# MAGIC **강점** : XGBoost 대비 2~10배 빠른 학습, 대용량 데이터 처리 능력, 메모리 효율적
# MAGIC **약점** : Leaf-wise 성장 때문에 소량 데이터에서 **과적합 위험** (max_depth 제한 필요)
# MAGIC
# MAGIC **제조 적용** : 수백만~수천만 행의 센서 로그를 빠르게 학습해야 할 때, 또는
# MAGIC **반복적인 재학습** (일간/주간 모델 업데이트)이 필요한 운영 환경에서 최적입니다.

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
# MAGIC ### Track 3: CatBoost — 범주형 데이터의 전문가
# MAGIC
# MAGIC **CatBoost (Categorical Boosting)**
# MAGIC
# MAGIC | 항목 | 내용 |
# MAGIC |------|------|
# MAGIC | **개발자** | Yandex (러시아 최대 IT 기업), 2017년 (Prokhorenkova et al.) |
# MAGIC | **탄생 배경** | 검색 엔진 랭킹에서 범주형 피처(검색어, 카테고리 등)를 효과적으로 처리하기 위해 개발 |
# MAGIC | **역사적 의의**| **범주형 피처 처리의 혁신** — One-hot 인코딩 없이도 범주형 데이터를 직접 학습 |
# MAGIC
# MAGIC **핵심 혁신 (제조 비유)** :
# MAGIC
# MAGIC 1. **범주형 피처 자동 인코딩 (Target Statistics)** :
# MAGIC    - 기존 방식: "H/M/L" 제품 타입을 숫자로 변환 (One-hot: [1,0,0], [0,1,0], [0,0,1])
# MAGIC    - CatBoost: 각 카테고리의 **타겟 변수 평균** 을 자동 계산하여 의미 있는 숫자로 변환
# MAGIC    - 제조 비유: "H등급 제품의 고장률은 5%, M등급은 3%, L등급은 2%"라는 **도메인 지식을 자동 학습**
# MAGIC
# MAGIC 2. **Ordered Boosting (순서 기반 부스팅)** :
# MAGIC    - 문제: 일반 Gradient Boosting은 **전체 데이터의 통계** 를 사용하여 각 샘플을 학습
# MAGIC    - 이는 "시험 답안을 보고 공부하는 것"과 같은 **데이터 누출(Data Leakage)**
# MAGIC    - CatBoost: 각 샘플 학습 시 **해당 샘플 이전의 데이터만** 사용
# MAGIC    - 결과: **과적합이 크게 감소**, 특히 소량 데이터에서 효과적
# MAGIC
# MAGIC **강점** : 범주형 피처 전처리 불필요, 과적합에 강함, 기본 설정으로도 좋은 성능
# MAGIC **약점** : XGBoost/LightGBM보다 학습 속도 느릴 수 있음, GPU 환경에서 최적화 필요
# MAGIC
# MAGIC **제조 적용** : AI4I 2020 데이터의 **'Type' (L/M/H)** 같은 범주형 변수가 있을 때,
# MAGIC 그리고 **설비 코드, 작업자 ID, 시프트(주간/야간)** 등 범주형 피처가 많은 제조 데이터에서 특히 유리합니다.
# MAGIC 또한 **auto_class_weights="Balanced"** 옵션으로 불균형 데이터를 내장 기능으로 자동 처리합니다.

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
# MAGIC ### Track 4: Random Forest — 안정성의 대명사
# MAGIC
# MAGIC **Random Forest (랜덤 포레스트)**
# MAGIC
# MAGIC | 항목 | 내용 |
# MAGIC |------|------|
# MAGIC | **개발자** | Leo Breiman (UC Berkeley), 2001년 |
# MAGIC | **탄생 배경**| 단일 결정 트리의 **불안정성(높은 분산)** 문제를 해결하기 위해 개발 |
# MAGIC | **역사적 의의**| "앙상블이 단일 모델보다 강하다"는 원리를 대중화. 2010년대까지 **가장 인기 있는 ML 알고리즘** |
# MAGIC
# MAGIC **핵심 원리 (제조 비유)** :
# MAGIC - **배깅(Bagging)** : 전체 데이터에서 **랜덤하게 부분 집합** 을 뽑아 각 트리 독립 학습
# MAGIC   - 비유: 10명의 검사원에게 각각 **다른 샘플 세트** 를 줘서 독립적으로 검사
# MAGIC - **랜덤 피처 선택** : 각 트리가 분할할 때 **일부 피처만** 랜덤 선택
# MAGIC   - 비유: 검사원마다 **다른 항목(온도, 진동, 소리 등)** 에 집중하도록 역할 분담
# MAGIC - **다수결 투표** : 모든 트리의 예측을 모아 **과반수** 로 최종 결정
# MAGIC   - 비유: 10명 중 7명이 "불량"이라 했으면 불량으로 판정
# MAGIC
# MAGIC **강점** :
# MAGIC - **과적합에 매우 강함** — 트리 수를 늘려도 성능이 떨어지지 않음 (Boosting과 다른 점)
# MAGIC - **피처 중요도(Feature Importance)** 를 자연스럽게 제공 — "어떤 센서가 고장 예측에 가장 기여하는가?"
# MAGIC - **하이퍼파라미터 민감도 낮음** — 기본 설정으로도 합리적인 성능
# MAGIC - **병렬 학습** 지원 — `n_jobs=-1`로 모든 CPU 코어 활용
# MAGIC
# MAGIC **약점** : Boosting 계열(XGBoost, LightGBM, CatBoost)보다 **일반적으로 2~5%p 낮은 정확도**
# MAGIC
# MAGIC **제조 적용** :
# MAGIC - **초기 데이터 탐색** 단계에서 빠르게 "어떤 센서가 중요한가?"를 파악
# MAGIC - **베이스라인 모델** 로 활용하여 Boosting 모델의 성능 향상 정도를 측정
# MAGIC - 모델 **해석이 중요한 상황** (경영진 보고, 규제 대응)에서 피처 중요도 시각화

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
# MAGIC ### MLflow UI에서 비교하는 방법 — 3단계
# MAGIC
# MAGIC **Step 1** : 노트북 오른쪽의 **실험(Experiment) 아이콘** (플라스크 모양) 클릭
# MAGIC
# MAGIC **Step 2** : 4개 Run 모두 **체크박스 선택** 후 **"Compare"** 버튼 클릭
# MAGIC
# MAGIC **Step 3** : 비교 화면에서 다음을 확인:
# MAGIC - **Parameters 탭** : 각 알고리즘의 하이퍼파라미터 비교
# MAGIC - **Metrics 탭** : F1, AUC, Recall, Precision을 **차트와 표** 로 비교
# MAGIC - **Artifacts 탭** : 저장된 모델 파일 확인
# MAGIC
# MAGIC ### MLflow 비교의 강력함 — 왜 엑셀보다 나은가?
# MAGIC
# MAGIC | 기능 | 엑셀/수작업 | MLflow |
# MAGIC |------|-----------|--------|
# MAGIC | 실험 결과 기록 | 수동 복사/붙여넣기 | **자동 기록** — 누락 없음 |
# MAGIC | 재현 가능성 | 코드 버전, 데이터 버전 불명확 | **코드 + 데이터 + 환경 모두 기록** |
# MAGIC | 비교 시각화 | 차트 직접 그려야 함 | **자동 차트 생성** — 클릭 2번 |
# MAGIC | 모델 공유 | 파일 전달, 버전 혼란 | **Model Registry** 로 중앙 관리 |
# MAGIC | 과거 실험 추적 | "지난달에 어떤 파라미터였지?" | **모든 히스토리 영구 보관** |
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
# MAGIC ### 모델 선택 기준 — 비즈니스 요구사항에서 출발
# MAGIC
# MAGIC 모델 선택은 단순히 "가장 높은 F1"을 고르는 것이 아닙니다.
# MAGIC **비즈니스 목표와 리스크 허용 범위** 에 따라 선택 기준이 달라집니다.
# MAGIC
# MAGIC 제조 예지보전에서는 **Recall (고장 탐지율)** 이 가장 중요합니다:
# MAGIC
# MAGIC | 시나리오 | 결과 | 비용 | 심각도 |
# MAGIC |---------|------|------|--------|
# MAGIC | Recall 낮음 (고장을 놓침) | 설비 파손, 라인 정지, 납기 지연 | **수천만~수억원**| **치명적** |
# MAGIC | Precision 낮음 (오탐 과다) | 불필요한 예방 정비 실시 | **수십~수백만원**| **관리 가능** |
# MAGIC
# MAGIC 따라서 선택 우선순위:
# MAGIC 1. **Recall**>= 0.7 이상 (** 필수 조건** — 이 임계값 미달 시 해당 모델은 부적격)
# MAGIC 2. **F1 Score** 최대화 (Recall 조건 충족 모델 중에서 Precision과의 균형 최적화)
# MAGIC 3. **AUC** 참고 (임계값 변경에 대한 모델의 강건성 평가)
# MAGIC
# MAGIC ### 결과 해석 가이드 — "이 알고리즘이 이겼다면 무엇을 의미하는가?"
# MAGIC
# MAGIC | 최종 선택 알고리즘 | 데이터에 대한 시사점 | 다음 단계 제안 |
# MAGIC |-------------------|-------------------|-------------|
# MAGIC | **XGBoost 승리**| 데이터가 정규화된 패턴이 강하고 균형 잡힘 | Optuna로 HPO 수행 시 **추가 2~5%p 향상** 기대 |
# MAGIC | **LightGBM 승리**| 데이터 규모가 크거나, 피처 상호작용이 복잡 | GOSS/EFB 파라미터 미세 조정으로 **속도+성능 동시 최적화** |
# MAGIC | **CatBoost 승리** | 범주형 피처가 중요한 역할, 또는 데이터 누출 패턴 존재 | Ordered Boosting의 이점이 큼 — 범주형 피처 추가 발굴 권장 |
# MAGIC | **Random Forest 승리** | 데이터에 노이즈가 많거나, Boosting이 과적합되는 상황 | 데이터 품질 점검 필요 — 노이즈 제거 후 Boosting 재시도 권장 |
# MAGIC
# MAGIC > **참고** : 4개 알고리즘의 성능이 **비슷하다면** (F1 차이 < 2%p), 이는 좋은 신호입니다.
# MAGIC > 데이터 품질이 좋고 피처 엔지니어링이 잘 되어 있어, **알고리즘보다 데이터가 성능을 지배** 하고 있다는 뜻입니다.
# MAGIC > 이 경우 **Stacking 앙상블** 로 여러 모델을 결합하면 추가 향상이 가능합니다.

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
# MAGIC ## 요약 — 이 노트북에서 배운 것
# MAGIC
# MAGIC ### 핵심 학습 내용
# MAGIC
# MAGIC | 주제 | 배운 내용 | 실무 적용 |
# MAGIC |------|----------|---------|
# MAGIC | **멀티 알고리즘 비교** | 4가지 알고리즘(XGBoost, LightGBM, CatBoost, RF)을 동일 조건에서 비교 | "감이 아닌 데이터 기반"으로 알고리즘 선택 |
# MAGIC | **MLflow 실험 추적** | 파라미터, 메트릭, 모델을 자동 기록 및 시각적 비교 | 재현 가능한 실험 관리, 감사 추적 |
# MAGIC | **평가 메트릭 이해** | F1, AUC, Recall, Precision의 제조 현장 의미 | 비즈니스 목표에 맞는 메트릭 선택 |
# MAGIC | **알고리즘 특성** | Boosting vs Bagging, 각 알고리즘의 강점/약점 | 데이터 특성에 맞는 알고리즘 매칭 |
# MAGIC
# MAGIC ### 이 비교 결과를 어떻게 활용할 것인가?
# MAGIC
# MAGIC 1. **최적 알고리즘이 선정** 되었으면 → 다음 단계인 **Optuna HPO** 로 하이퍼파라미터를 미세 조정
# MAGIC 2. **여러 알고리즘의 성능이 비슷** 하면 → **Stacking 앙상블** 로 결합하여 추가 향상
# MAGIC 3. **Recall이 부족** 하면 → **SMOTE-ENN** 불균형 처리를 적용하여 고장 탐지율 개선
# MAGIC 4. 모든 과정을 자동화하고 싶으면 → **Databricks AutoML** 로 한번에 수행
# MAGIC
# MAGIC ### MLflow UI 활용 팁
# MAGIC
# MAGIC | 작업 | 방법 |
# MAGIC |------|------|
# MAGIC | 전체 Run 확인 | 노트북 우측 패널 > **실험 아이콘(플라스크)** 클릭 |
# MAGIC | 알고리즘 비교 | Run들을 체크 후 **Compare** 버튼 → 차트/표 자동 생성 |
# MAGIC | 모델 다운로드 | Run 클릭 > **Artifacts** 탭 > model 폴더 |
# MAGIC | 최적 모델 등록 | Run 클릭 > **Register Model** → Model Registry에 버전 관리 시작 |
# MAGIC | 과거 실험 검색 | 실험 페이지에서 **필터/정렬** 활용 (예: test_f1_score 내림차순) |
# MAGIC
# MAGIC > **핵심 메시지** : ML 프로젝트에서 **"어떤 알고리즘을 쓸 것인가?"** 는 중요한 질문이지만,
# MAGIC > 더 중요한 것은 **"어떻게 체계적으로 비교하고 추적할 것인가?"** 입니다.
# MAGIC > MLflow는 이 체계적인 실험 관리를 가능하게 하며, 이것이 Databricks를 활용하는 가장 큰 가치입니다.
# MAGIC
# MAGIC **다음 단계:** [03c: 고급 기법 적용]($./03c_advanced_techniques) — SMOTE, Optuna HPO, Stacking, AutoML
