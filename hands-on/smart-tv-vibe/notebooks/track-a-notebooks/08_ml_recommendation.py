# Databricks notebook source
# MAGIC %md
# MAGIC # 08. ML/AI — 개인화 추천 & MLOps 전체 라이프사이클
# MAGIC
# MAGIC 이 노트북에서는 Smart TV 시청 데이터를 기반으로 **End-to-End MLOps 파이프라인** 을 구축합니다.
# MAGIC 단순 모델 학습을 넘어,**Feature Store → 모델 학습 → 서빙 → 재학습 → 모니터링** 까지
# MAGIC 실제 운영 환경에서 필요한 모든 단계를 다룹니다.
# MAGIC
# MAGIC ### 이 노트북에서 배우는 것
# MAGIC
# MAGIC | 단계 | Databricks 기능 | 설명 |
# MAGIC |------|----------------|------|
# MAGIC | 1 |**Feature Engineering**| Gold 테이블에서 ML 피처 추출 |
# MAGIC | 2 |**Feature Store (Offline)**| 피처를 중앙 저장소에 등록 → 재사용, 버전 관리, 리니지 |
# MAGIC | 3 |**모델 학습 (LightGBM)**| 사용자 이탈/광고 클릭 예측 분류 모델 |
# MAGIC | 4 |**MLflow Tracking**| 실험 관리, 하이퍼파라미터 비교, 메트릭 로깅 |
# MAGIC | 5 |**SHAP 모델 설명**| 어떤 피처가 예측에 가장 영향을 주는지 해석 |
# MAGIC | 6 |**UC Model Registry**| 모델 버전 관리, Champion/Challenger 관리 |
# MAGIC | 7 |**Feature Store (Online)**| 실시간 서빙용 피처 동기화 |
# MAGIC | 8 |**Model Serving**| REST API 엔드포인트로 실시간 추론 |
# MAGIC | 9 |**배치 예측**| 전체 사용자 대상 일괄 스코어링 |
# MAGIC | 10 |**증분 재학습**| 신규 데이터로 모델 갱신 (개발: 빈번, 운영: 주 1회) |
# MAGIC | 11 |**모델 모니터링**| 데이터/모델 드리프트 감지 |
# MAGIC | 12 |**Job 스케줄링**| 학습/예측 파이프라인 자동화 |
# MAGIC
# MAGIC ### 전체 아키텍처
# MAGIC
# MAGIC ```
# MAGIC ┌─────────────┐  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
# MAGIC │ Gold Tables │───→│ Feature Store  │───→│ Model Train │───→│ UC Registry │
# MAGIC │ (user_prof, │  │ (Offline Store) │  │ (LightGBM)  │  │ (Champion)  │
# MAGIC │ viewing,  │  │ UC Table 기반  │  │ + MLflow   │  │       │
# MAGIC │ ad_perf)  │  │ + Online Store  │  │ + SHAP    │  │       │
# MAGIC └─────────────┘  └──────────────────┘  └──────────────┘  └──────┬───────┘
# MAGIC                                    │
# MAGIC           ┌────────────────────────────────────────────────────┤
# MAGIC           │                          │
# MAGIC       ┌──────┴──────┐                 ┌────────┴────────┐
# MAGIC       │ Batch Pred │                 │ Model Serving  │
# MAGIC       │ (전체 스코어)│                 │ (실시간 API)  │
# MAGIC       │ 일 4회   │                 │ + Feature Lookup│
# MAGIC       └─────────────┘                 └─────────────────┘
# MAGIC           │
# MAGIC       ┌──────┴──────┐  ┌──────────────┐  ┌──────────────┐
# MAGIC       │ Monitor   │───→│ Drift 감지  │───→│ 재학습 트리거│
# MAGIC       │ (Lakehouse │  │ (PSI, 정확도) │  │ (Job/Agent) │
# MAGIC       │ Monitor)  │  │       │  │       │
# MAGIC       └─────────────┘  └──────────────┘  └──────────────┘
# MAGIC ```
# MAGIC
# MAGIC**사전 조건:**01~03 노트북을 먼저 실행 (카탈로그/데이터/Gold 테이블 필요)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 0: 필수 라이브러리 설치
# MAGIC
# MAGIC Shared Compute 클러스터에는 LightGBM, SHAP 등이 기본 설치되어 있지 않을 수 있습니다.
# MAGIC 아래 셀을 먼저 실행하세요. (이미 설치되어 있으면 빠르게 넘어갑니다)

# COMMAND ----------

# MAGIC %pip install lightgbm shap databricks-feature-engineering --quiet

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: 환경 설정

# COMMAND ----------

import re
import mlflow
import json
from pyspark.sql import functions as F
from pyspark.sql import Window

username = spark.sql("SELECT current_user()").first()[0]
user_prefix = re.sub(r'[^a-zA-Z0-9]', '_', username.split('@')[0])
CATALOG = f"{user_prefix}_smarttv_training"
print(f"카탈로그: {CATALOG}")

spark.sql(f"USE CATALOG {CATALOG}")

# MLflow 실험 설정
experiment_name = f"/Users/{username}/smarttv_demo/ad_click_prediction"
mlflow.set_experiment(experiment_name)
print(f"MLflow 실험: {experiment_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 1: Feature Store — 피처의 중앙 저장소
# MAGIC
# MAGIC ### Feature Store란?
# MAGIC
# MAGIC ML 모델에 입력되는 **피처(Feature)** 를 중앙에서 관리하는 저장소입니다.
# MAGIC
# MAGIC | 문제 | Feature Store 없이 | Feature Store 사용 |
# MAGIC |------|-------------------|-------------------|
# MAGIC |**피처 중복**| 팀마다 동일 피처를 각자 계산 | 한번 정의 → 모든 팀이 재사용 |
# MAGIC |**학습/서빙 불일치**| 학습 때와 서빙 때 피처가 달라 정확도 하락 | 동일 피처 정의로 일관성 보장 |
# MAGIC |**피처 탐색**| "이 피처 누가 만들었지?" | UC에서 검색, 리니지 추적 |
# MAGIC |**시점 정합성**| 미래 데이터가 학습에 섞임 (data leakage) | Point-in-time lookup으로 방지 |
# MAGIC
# MAGIC ### Databricks Feature Store 아키텍처
# MAGIC
# MAGIC ```
# MAGIC ┌──────────────────────────────────────────────────┐
# MAGIC │       Unity Catalog            │
# MAGIC │                          │
# MAGIC │ ┌─────────────────┐  ┌─────────────────────┐ │
# MAGIC │ │ Offline Store  │  │  Online Store    │ │
# MAGIC │ │ (Delta Table)  │───→│ (Cosmos DB / DynamoDB)│ │
# MAGIC │ │         │sync│           │ │
# MAGIC │ │ - 대용량 피처  │  │ - 밀리초 응답    │ │
# MAGIC │ │ - 배치 학습용  │  │ - 실시간 서빙용   │ │
# MAGIC │ │ - 히스토리 보관 │  │ - 최신 값만 유지  │ │
# MAGIC │ └─────────────────┘  └─────────────────────┘ │
# MAGIC │                          │
# MAGIC │ 사용처:                     │
# MAGIC │ - 모델 학습 시: Offline Store에서 피처 조회   │
# MAGIC │ - 배치 예측 시: Offline Store에서 피처 조회   │
# MAGIC │ - 실시간 서빙 시: Online Store에서 피처 조회   │
# MAGIC └──────────────────────────────────────────────────┘
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 2: Feature Store에 피처 테이블 등록 (Offline Store)
# MAGIC
# MAGIC `gold.user_profiles` 테이블을 Feature Store에 등록합니다.
# MAGIC Databricks에서는 **Unity Catalog의 Delta Table 자체가 Offline Feature Store** 역할을 합니다.
# MAGIC Primary Key와 Timestamp Key를 지정하면 Feature Store로 활용할 수 있습니다.

# COMMAND ----------

from databricks.feature_engineering import FeatureEngineeringClient

fe = FeatureEngineeringClient()

# user_profiles를 Feature Table로 등록
# 이미 테이블이 존재하므로, Feature Store 메타데이터만 추가
try:
  fe.create_table(
    name=f"{CATALOG}.gold.user_behavior_features",
    primary_keys=["device_id", "user_profile_id"],
    description="사용자 행동 피처: 시청 패턴, 클릭 행동, 광고 반응을 종합한 ML 입력 피처",
    df=spark.table(f"{CATALOG}.gold.user_profiles"),
  )
  print("✅ Feature Table 'user_behavior_features' 생성 완료")
except Exception as e:
  if "already exists" in str(e):
    # 이미 존재하면 업데이트
    fe.write_table(
      name=f"{CATALOG}.gold.user_behavior_features",
      df=spark.table(f"{CATALOG}.gold.user_profiles"),
      mode="overwrite",
    )
    print("✅ Feature Table 'user_behavior_features' 업데이트 완료")
  else:
    print(f"⚠️ Feature Table 등록: {e}")
    print("  → 대신 gold.user_profiles를 직접 사용합니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 3: 학습용 데이터셋 생성 — 광고 클릭 예측 모델
# MAGIC
# MAGIC**비즈니스 목표:** 어떤 사용자가 광고를 클릭할 가능성이 높은지 예측
# MAGIC → FastTV 광고 타겟팅 최적화, eCPM 향상
# MAGIC
# MAGIC**모델 유형:** 이진 분류 (LightGBM)
# MAGIC - Input: 사용자 행동 피처 (시청 시간, 장르 선호, 세션 패턴 등)
# MAGIC - Output: 광고 클릭 확률 (0~1)

# COMMAND ----------

# user_profiles + user_segments에서 학습 데이터 구성
training_data = spark.sql(f"""
  SELECT
    up.device_id,
    up.user_profile_id,

    -- 시청 행동 피처
    up.total_viewing_days,
    up.total_viewing_minutes,
    up.avg_daily_viewing_minutes,
    up.weekend_ratio,

    -- 클릭 행동 피처
    up.total_click_events,
    COALESCE(up.avg_session_duration, 0) AS avg_session_duration,
    up.search_count,
    up.voice_command_count,

    -- 광고 반응 피처
    up.total_ad_impressions,
    up.total_ad_clicks,
    up.ad_ctr,
    COALESCE(up.avg_time_to_click, 0) AS avg_time_to_click,

    -- 디바이스 피처 (인코딩)
    CASE up.price_tier
      WHEN 'premium' THEN 2
      WHEN 'mid' THEN 1
      ELSE 0
    END AS price_tier_encoded,
    CASE WHEN up.has_fasttv THEN 1 ELSE 0 END AS has_fasttv_encoded,

    -- 타겟 변수: 광고 클릭 여부 (ad_ctr > 중앙값이면 high clicker)
    CASE WHEN up.ad_ctr > 2.0 THEN 1 ELSE 0 END AS label

  FROM {CATALOG}.gold.user_profiles up
  WHERE up.total_ad_impressions > 0 -- 광고 노출이 있는 사용자만
""")

# 데이터 건수 및 라벨 분포 확인
total = training_data.count()
positive = training_data.filter("label = 1").count()
print(f"전체 데이터: {total:,}건")
print(f" Positive (high clicker): {positive:,}건 ({positive/total*100:.1f}%)")
print(f" Negative (low clicker): {total-positive:,}건 ({(total-positive)/total*100:.1f}%)")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 2: 모델 학습 (LightGBM + MLflow)
# MAGIC
# MAGIC ### LightGBM을 선택한 이유
# MAGIC
# MAGIC | 알고리즘 | 장점 | 적합한 경우 |
# MAGIC |---------|------|------------|
# MAGIC |**LightGBM**| 빠른 학습, 범주형 피처 자동 처리, 해석 가능 | 정형 데이터, 중간 규모 |
# MAGIC | XGBoost | 안정적, 널리 사용 | 정형 데이터, 하이퍼파라미터 튜닝 |
# MAGIC | ALS | 사용자-아이템 추천 특화 | 협업 필터링 추천 |
# MAGIC | Deep Learning | 비정형 데이터(이미지, 텍스트) | 대규모, GPU 환경 |
# MAGIC
# MAGIC 이 시나리오에서는 **정형 데이터 기반 분류** 이므로 LightGBM이 최적입니다.
# MAGIC 실무에서는 XGBoost와 함께 비교 실험하는 것이 일반적입니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 4: Train/Test 분할 및 LightGBM 학습

# COMMAND ----------

import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
  accuracy_score, precision_score, recall_score, f1_score,
  roc_auc_score, confusion_matrix, classification_report
)
import numpy as np
import pandas as pd

# Spark → Pandas 변환
pdf = training_data.toPandas()

# 피처 / 타겟 분리
feature_cols = [
  "total_viewing_days", "total_viewing_minutes", "avg_daily_viewing_minutes",
  "weekend_ratio", "total_click_events", "avg_session_duration",
  "search_count", "voice_command_count", "total_ad_impressions",
  "total_ad_clicks", "avg_time_to_click",
  "price_tier_encoded", "has_fasttv_encoded"
]

X = pdf[feature_cols]
y = pdf["label"]

# 80/20 분할 (시간 기반 분할이 이상적이지만, 교육용으로 랜덤 분할)
X_train, X_test, y_train, y_test = train_test_split(
  X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train: {len(X_train):,}건, Test: {len(X_test):,}건")
print(f"Train 양성 비율: {y_train.mean():.3f}")
print(f"Test 양성 비율: {y_test.mean():.3f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 5: 3가지 설정 비교 실험 (MLflow Tracking)
# MAGIC
# MAGIC**MLflow Tracking** 은 ML 실험의 모든 것을 기록합니다:
# MAGIC -**Parameters**: 하이퍼파라미터 (학습률, 트리 수 등)
# MAGIC -**Metrics**: 평가 지표 (AUC, F1, 정확도 등)
# MAGIC -**Artifacts**: 모델 파일, 차트, SHAP 그래프 등
# MAGIC -**Tags**: 실험 메타데이터

# COMMAND ----------

configs = [
  {"name": "baseline",    "n_estimators": 100, "learning_rate": 0.1, "max_depth": 5, "num_leaves": 31},
  {"name": "deep_trees",   "n_estimators": 200, "learning_rate": 0.05, "max_depth": 8, "num_leaves": 63},
  {"name": "regularized",   "n_estimators": 300, "learning_rate": 0.03, "max_depth": 6, "num_leaves": 31},
]

results = []

for config in configs:
  with mlflow.start_run(run_name=config["name"]):
    # 파라미터 로깅
    mlflow.log_params({
      "model_type": "LightGBM",
      "n_estimators": config["n_estimators"],
      "learning_rate": config["learning_rate"],
      "max_depth": config["max_depth"],
      "num_leaves": config["num_leaves"],
      "train_size": len(X_train),
      "test_size": len(X_test),
      "n_features": len(feature_cols),
    })

    # LightGBM 학습
    model = lgb.LGBMClassifier(
      n_estimators=config["n_estimators"],
      learning_rate=config["learning_rate"],
      max_depth=config["max_depth"],
      num_leaves=config["num_leaves"],
      random_state=42,
      verbose=-1,
      class_weight="balanced", # 불균형 처리
    )
    model.fit(X_train, y_train)

    # 예측 및 평가
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
      "accuracy": accuracy_score(y_test, y_pred),
      "precision": precision_score(y_test, y_pred),
      "recall": recall_score(y_test, y_pred),
      "f1": f1_score(y_test, y_pred),
      "auc_roc": roc_auc_score(y_test, y_prob),
    }
    mlflow.log_metrics(metrics)

    # 모델 저장
    mlflow.lightgbm.log_model(model, "model", input_example=X_train.iloc[:5])

    # 피처 중요도 로깅
    importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
    mlflow.log_dict(importance, "feature_importance.json")

    results.append({"name": config["name"],**metrics})
    print(f" {config['name']}: AUC={metrics['auc_roc']:.4f}, F1={metrics['f1']:.4f}")

# COMMAND ----------

# 실험 결과 비교
results_df = spark.createDataFrame(results)
display(results_df.orderBy(F.desc("auc_roc")))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 5-B: AutoML로 자동 모델 탐색 (선택)
# MAGIC
# MAGIC**AutoML** 은 여러 알고리즘과 하이퍼파라미터를 **자동으로 탐색** 하여 최적 모델을 찾습니다.
# MAGIC 수동으로 LightGBM 3개 설정을 비교한 것을, AutoML은 수십~수백 개를 자동으로 시도합니다.
# MAGIC
# MAGIC | | 수동 실험 (위) | AutoML |
# MAGIC |---|---|---|
# MAGIC |**알고리즘**| LightGBM 1개 | LightGBM + XGBoost + RandomForest 등 |
# MAGIC |**하이퍼파라미터**| 3개 수동 설정 | 수십~수백 개 자동 탐색 |
# MAGIC |**소요 시간**| 직접 코딩 필요 | 한 줄로 실행 |
# MAGIC |**사용 시점**| 알고리즘을 이미 알 때 | 빠르게 baseline 만들 때 |
# MAGIC
# MAGIC >**Tip:** 실무에서는 AutoML로 빠르게 baseline을 잡고, 수동 실험으로 fine-tuning하는 패턴이 일반적입니다.

# COMMAND ----------

# AutoML 실행 (교육용 — 시간 제한 5분)
# 실행하려면 이 셀의 주석을 해제하세요

# from databricks import automl
#
# automl_result = automl.classify(
#   dataset=spark.createDataFrame(pdf[feature_cols + ["label"]]),
#   target_col="label",
#   primary_metric="roc_auc",
#   timeout_minutes=5,
#   experiment_name=f"/Users/{username}/smarttv_demo/automl_ad_click",
# )
#
# print(f"AutoML 최적 모델: {automl_result.best_trial.model_description}")
# print(f"AutoML AUC: {automl_result.best_trial.evaluation_metric_value:.4f}")
# print(f"수동 LightGBM 최적 AUC: {max(r['auc_roc'] for r in results):.4f}")
# print(f"\n→ MLflow Experiment에서 AutoML이 시도한 모든 모델을 비교할 수 있습니다")

print("AutoML은 주석 해제 후 실행하세요 (약 5분 소요)")
print("참고: databricks.automl.classify()는 Single User 클러스터에서만 동작합니다")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 3: SHAP 기반 모델 설명 (Explainability)
# MAGIC
# MAGIC ### 모델 설명이 왜 중요한가?
# MAGIC
# MAGIC | 관점 | 필요성 |
# MAGIC |------|--------|
# MAGIC |**비즈니스**| "왜 이 사용자가 광고를 클릭할 거라고 예측했는가?" |
# MAGIC |**규제/감사**| 모델 의사결정의 투명성 확보 (금융, 의료 등) |
# MAGIC |**디버깅**| 피처 엔지니어링 오류 발견, 데이터 누수(leakage) 감지 |
# MAGIC |**개선**| 어떤 피처가 중요한지 파악 → 피처 추가/제거 판단 |
# MAGIC
# MAGIC**SHAP (SHapley Additive exPlanations)**: 게임 이론 기반으로
# MAGIC 각 피처가 개별 예측에 **얼마나 기여했는지** 를 정량적으로 측정합니다.

# COMMAND ----------

import shap

# 최적 모델 선택 (AUC 최고)
best_config = max(configs, key=lambda c: next(r["auc_roc"] for r in results if r["name"] == c["name"]))
best_model = lgb.LGBMClassifier(
  n_estimators=best_config["n_estimators"],
  learning_rate=best_config["learning_rate"],
  max_depth=best_config["max_depth"],
  num_leaves=best_config["num_leaves"],
  random_state=42, verbose=-1, class_weight="balanced",
)
best_model.fit(X_train, y_train)

# SHAP 값 계산
explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test)

# SHAP Summary Plot (전역 피처 중요도)
print("=== SHAP 피처 중요도 (전역) ===")
if isinstance(shap_values, list):
  # binary classification: shap_values[1] = positive class
  sv = shap_values[1]
else:
  sv = shap_values

mean_abs_shap = np.mean(np.abs(sv), axis=0)
shap_importance = sorted(zip(feature_cols, mean_abs_shap), key=lambda x: x[1], reverse=True)
for feat, imp in shap_importance:
  bar = "█" * int(imp * 50 / max(mean_abs_shap))
  print(f" {feat:30s} {bar} ({imp:.4f})")

# COMMAND ----------

# 개별 예측 설명 (샘플 3건)
print("=== 개별 예측 SHAP 설명 ===")
for idx in [0, 1, 2]:
  actual = y_test.iloc[idx]
  pred_prob = best_model.predict_proba(X_test.iloc[[idx]])[:, 1][0]
  print(f"\n--- 샘플 {idx+1}: 실제={actual}, 예측확률={pred_prob:.3f} ---")
  if isinstance(shap_values, list):
    sample_shap = shap_values[1][idx]
  else:
    sample_shap = shap_values[idx]
  top_features = sorted(zip(feature_cols, sample_shap), key=lambda x: abs(x[1]), reverse=True)[:5]
  for feat, val in top_features:
    direction = "↑ 클릭 증가" if val > 0 else "↓ 클릭 감소"
    print(f" {feat}: {val:+.4f} ({direction})")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 4: Unity Catalog Model Registry
# MAGIC
# MAGIC ### Model Registry란?
# MAGIC
# MAGIC 학습된 모델의 **버전 관리, 승인 워크플로우, 배포 관리** 를 담당합니다.
# MAGIC
# MAGIC ```
# MAGIC ┌─────────────────────────────────────────────┐
# MAGIC │     UC Model Registry          │
# MAGIC │                       │
# MAGIC │ 모델: smarttv_training.gold.ad_click_model │
# MAGIC │                       │
# MAGIC │ v1 ─── "champion" (현재 운영 중)      │
# MAGIC │ v2 ─── "challenger" (A/B 테스트 중)    │
# MAGIC │ v3 ─── (학습 완료, 검증 대기)       │
# MAGIC │                       │
# MAGIC │ 리니지: gold.user_profiles → 모델 → 엔드포인트│
# MAGIC └─────────────────────────────────────────────┘
# MAGIC ```
# MAGIC
# MAGIC**UC Model Registry vs 기존 MLflow Registry:**# MAGIC - 테이블과 동일한 거버넌스 (GRANT/REVOKE)
# MAGIC - 자동 리니지 추적 (어떤 테이블로 학습했는지)
# MAGIC - 워크스페이스 간 공유

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 6: 최적 모델을 Unity Catalog에 등록

# COMMAND ----------

model_name = f"{CATALOG}.gold.ad_click_model"

# 최적 Run 찾기
experiment = mlflow.get_experiment_by_name(experiment_name)
runs = mlflow.search_runs(
  experiment_ids=[experiment.experiment_id],
  order_by=["metrics.auc_roc DESC"]
)
best_run_id = runs.iloc[0]["run_id"]
best_auc = runs.iloc[0]["metrics.auc_roc"]
model_uri = f"runs:/{best_run_id}/model"

print(f"최적 모델: Run {best_run_id[:8]}... (AUC={best_auc:.4f})")

# UC에 등록
mlflow.set_registry_uri("databricks-uc")
try:
  result = mlflow.register_model(model_uri, model_name)
  print(f"✅ 모델 등록 완료: {model_name} v{result.version}")

  # Champion alias 설정
  from mlflow import MlflowClient
  client = MlflowClient()
  client.set_registered_model_alias(model_name, "champion", result.version)
  print(f"  Alias 'champion' → v{result.version}")

  # 태그 추가
  client.set_model_version_tag(model_name, result.version, "task", "ad_click_prediction")
  client.set_model_version_tag(model_name, result.version, "framework", "lightgbm")
except Exception as e:
  print(f"⚠️ 모델 등록 참고: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 5: 배치 예측 (Batch Scoring)
# MAGIC
# MAGIC ### 배치 예측이란?
# MAGIC
# MAGIC 전체 사용자에 대해 **일괄적으로 예측** 을 수행하고 결과를 테이블에 저장합니다.
# MAGIC 실시간 서빙과 달리,**대규모 데이터를 효율적으로 처리** 할 수 있습니다.
# MAGIC
# MAGIC | | 배치 예측 | 실시간 서빙 |
# MAGIC |---|---|---|
# MAGIC |**처리 방식**| Spark로 분산 처리 | REST API, 건당 처리 |
# MAGIC |**응답 시간**| 분~시간 | 밀리초 |
# MAGIC |**사용 시나리오**| 일일 스코어링, 마케팅 캠페인 | 앱 내 실시간 추천 |
# MAGIC |**운영 환경 예시**| 일 4회 전체 사용자 스코어링 | 사용자 요청 시 즉시 응답 |

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 7: 전체 사용자 배치 스코어링

# COMMAND ----------

# 전체 사용자 피처 데이터 로드
all_users = spark.sql(f"""
  SELECT
    device_id, user_profile_id,
    total_viewing_days, total_viewing_minutes, avg_daily_viewing_minutes,
    weekend_ratio, total_click_events,
    COALESCE(avg_session_duration, 0) AS avg_session_duration,
    search_count, voice_command_count, total_ad_impressions,
    total_ad_clicks, COALESCE(avg_time_to_click, 0) AS avg_time_to_click,
    CASE price_tier WHEN 'premium' THEN 2 WHEN 'mid' THEN 1 ELSE 0 END AS price_tier_encoded,
    CASE WHEN has_fasttv THEN 1 ELSE 0 END AS has_fasttv_encoded
  FROM {CATALOG}.gold.user_profiles
""").toPandas()

# 예측 수행
all_users["click_probability"] = best_model.predict_proba(all_users[feature_cols])[:, 1]
all_users["click_prediction"] = (all_users["click_probability"] > 0.5).astype(int)
all_users["risk_score"] = (all_users["click_probability"] * 100).round(1)
all_users["scored_at"] = pd.Timestamp.now().isoformat()

# Spark DataFrame으로 변환 후 저장
score_cols = ["device_id", "user_profile_id", "click_probability", "click_prediction", "risk_score", "scored_at"]
df_scores = spark.createDataFrame(all_users[score_cols])
df_scores.write.mode("overwrite").saveAsTable(f"{CATALOG}.gold.ad_click_scores")

total_scored = df_scores.count()
high_prob = df_scores.filter("click_probability > 0.7").count()
print(f"✅ 배치 스코어링 완료: {total_scored:,}명")
print(f"  고확률 클릭 사용자 (>70%): {high_prob:,}명 ({high_prob/total_scored*100:.1f}%)")

# COMMAND ----------

# 스코어 분포 확인
display(spark.sql(f"""
  SELECT
    CASE
      WHEN click_probability >= 0.8 THEN '80-100% (Very High)'
      WHEN click_probability >= 0.6 THEN '60-80% (High)'
      WHEN click_probability >= 0.4 THEN '40-60% (Medium)'
      WHEN click_probability >= 0.2 THEN '20-40% (Low)'
      ELSE '0-20% (Very Low)'
    END AS probability_bucket,
    COUNT(*) AS user_count,
    ROUND(AVG(click_probability), 3) AS avg_probability
  FROM {CATALOG}.gold.ad_click_scores
  GROUP BY 1
  ORDER BY avg_probability DESC
"""))

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 6: 증분 재학습 (Incremental Retraining)
# MAGIC
# MAGIC ### 왜 재학습이 필요한가?
# MAGIC
# MAGIC 모델은 시간이 지나면 성능이 저하됩니다 (**모델 드리프트**):
# MAGIC -**데이터 드리프트**: 사용자 행동이 변함 (새 콘텐츠 출시, 시즌 변화)
# MAGIC -**컨셉 드리프트**: 피처와 타겟의 관계가 변함 (광고 형식 변경 등)
# MAGIC
# MAGIC ### 재학습 전략
# MAGIC
# MAGIC | 환경 | 재학습 주기 | 배치 예측 | 목적 |
# MAGIC |------|-----------|----------|------|
# MAGIC |**개발**| 일 4회 | 매 재학습 후 | 빠른 실험, A/B 테스트 |
# MAGIC |**운영**| 주 1회 | 일 4회 | 안정성 우선, 충분한 데이터 축적 |
# MAGIC
# MAGIC ### 증분 재학습 흐름
# MAGIC
# MAGIC ```
# MAGIC 신규 데이터   기존 데이터   학습 데이터    모델 학습
# MAGIC (이번 주)  +  (지난 4주)  → (5주 합산)  →  (LightGBM)
# MAGIC ↓                        ↓
# MAGIC Feature Store               UC Registry
# MAGIC 업데이트                  새 버전 등록
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 8: 증분 재학습 시뮬레이션
# MAGIC
# MAGIC 실제로는 새 데이터가 들어오면 파이프라인이 자동으로 돌지만,
# MAGIC 여기서는 **데이터 증분을 시뮬레이션** 하여 재학습 프로세스를 보여줍니다.

# COMMAND ----------

def retrain_model(catalog, feature_cols, experiment_name, model_name, data_version="incremental"):
  """
  증분 재학습 함수: 새 데이터가 Feature Store에 추가된 후 호출됩니다.

  실무에서는 이 함수가:
  1. Databricks Job으로 스케줄링되거나
  2. Agent가 트리거하거나
  3. 모니터링 알림에 의해 호출됩니다.
  """
  mlflow.set_experiment(experiment_name)

  # 최신 피처 데이터 로드 (Feature Store에서)
  pdf = spark.sql(f"""
    SELECT
      total_viewing_days, total_viewing_minutes, avg_daily_viewing_minutes,
      weekend_ratio, total_click_events,
      COALESCE(avg_session_duration, 0) AS avg_session_duration,
      search_count, voice_command_count, total_ad_impressions,
      total_ad_clicks, COALESCE(avg_time_to_click, 0) AS avg_time_to_click,
      CASE price_tier WHEN 'premium' THEN 2 WHEN 'mid' THEN 1 ELSE 0 END AS price_tier_encoded,
      CASE WHEN has_fasttv THEN 1 ELSE 0 END AS has_fasttv_encoded,
      CASE WHEN ad_ctr > 2.0 THEN 1 ELSE 0 END AS label
    FROM {catalog}.gold.user_profiles
    WHERE total_ad_impressions > 0
  """).toPandas()

  X = pdf[feature_cols]
  y = pdf["label"]
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

  with mlflow.start_run(run_name=f"retrain_{data_version}"):
    mlflow.log_param("data_version", data_version)
    mlflow.log_param("retrain_trigger", "scheduled")
    mlflow.log_param("train_size", len(X_train))

    model = lgb.LGBMClassifier(
      n_estimators=200, learning_rate=0.05, max_depth=8,
      num_leaves=63, random_state=42, verbose=-1, class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)
    auc = roc_auc_score(y_test, y_prob)
    f1 = f1_score(y_test, y_pred)

    mlflow.log_metrics({"auc_roc": auc, "f1": f1, "accuracy": accuracy_score(y_test, y_pred)})
    mlflow.lightgbm.log_model(model, "model", input_example=X_train.iloc[:5])

    print(f" 재학습 완료: AUC={auc:.4f}, F1={f1:.4f}")
    return auc, f1

# 재학습 실행
print("=== 증분 재학습 시뮬레이션 ===")
auc, f1 = retrain_model(CATALOG, feature_cols, experiment_name, model_name, "week_2025_09")
print(f"\n 새 모델 성능: AUC={auc:.4f}")
print(" → Champion 모델과 비교하여 성능이 더 좋으면 자동 교체 (CI/CD 파이프라인)")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 7: 모델 모니터링 (Lakehouse Monitoring)
# MAGIC
# MAGIC ### 모니터링 체크 항목
# MAGIC
# MAGIC | 지표 | 설명 | 임계값 예시 |
# MAGIC |------|------|-----------|
# MAGIC |**PSI (Population Stability Index)**| 입력 데이터 분포 변화 | PSI > 0.2 → 재학습 필요 |
# MAGIC |**정확도 하락**| 실제 결과 vs 예측 비교 | AUC 5% 이상 하락 → 알림 |
# MAGIC |**피처 드리프트**| 개별 피처 분포 변화 | 특정 피처 분포 크게 변동 → 조사 |
# MAGIC |**예측 분포 변화**| 예측값 분포 이동 | 평균 예측값 20% 이상 변동 |
# MAGIC
# MAGIC ### Databricks Lakehouse Monitor
# MAGIC
# MAGIC ```python
# MAGIC # 운영 환경에서는 이렇게 모니터를 설정합니다:
# MAGIC from databricks.sdk import WorkspaceClient
# MAGIC w = WorkspaceClient()
# MAGIC
# MAGIC w.quality_monitors.create(
# MAGIC   table_name=f"{CATALOG}.gold.ad_click_scores",
# MAGIC   inference_log=MonitorInferenceLog(
# MAGIC     model_id_col="model_version",
# MAGIC     prediction_col="click_prediction",
# MAGIC     label_col="actual_click",    # 실제 결과가 나중에 채워짐
# MAGIC     timestamp_col="scored_at",
# MAGIC   ),
# MAGIC   schedule=MonitorCronSchedule(quartz_cron_expression="0 0 */6 * * ?"), # 6시간마다
# MAGIC )
# MAGIC ```

# COMMAND ----------

# 모니터링 시뮬레이션: 예측 분포 통계
print("=== 모델 모니터링 대시보드 (시뮬레이션) ===\n")

score_stats = spark.sql(f"""
  SELECT
    COUNT(*) AS total_users,
    ROUND(AVG(click_probability), 4) AS mean_prob,
    ROUND(STDDEV(click_probability), 4) AS std_prob,
    ROUND(MIN(click_probability), 4) AS min_prob,
    ROUND(MAX(click_probability), 4) AS max_prob,
    ROUND(PERCENTILE_APPROX(click_probability, 0.5), 4) AS median_prob,
    SUM(click_prediction) AS predicted_clickers,
    ROUND(SUM(click_prediction) * 100.0 / COUNT(*), 1) AS clicker_pct
  FROM {CATALOG}.gold.ad_click_scores
""").first()

print(f" 총 사용자:     {score_stats.total_users:,}")
print(f" 평균 클릭 확률:  {score_stats.mean_prob}")
print(f" 표준편차:     {score_stats.std_prob}")
print(f" 중앙값:      {score_stats.median_prob}")
print(f" 예측 클릭러:    {score_stats.predicted_clickers:,}명 ({score_stats.clicker_pct}%)")
print(f"\n ⚠️ 모니터링 기준:")
print(f" - 평균 확률이 0.3~0.7 범위를 벗어나면 → 데이터 드리프트 의심")
print(f" - 클릭러 비율이 이전 대비 ±20% 변동 → 컨셉 드리프트 의심")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 8: Job 스케줄링 — 자동화된 MLOps 파이프라인
# MAGIC
# MAGIC ### 운영 환경 스케줄 설계
# MAGIC
# MAGIC ```
# MAGIC ┌─────────────────────────────────────────────────────────┐
# MAGIC │         MLOps Job DAG              │
# MAGIC │                             │
# MAGIC │ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
# MAGIC │ │ Task 1   │───→│ Task 2   │───→│ Task 3   ││
# MAGIC │ │ Feature   │  │ Retrain   │  │ Batch    ││
# MAGIC │ │ Update   │  │ (조건부)  │  │ Scoring   ││
# MAGIC │ │       │  │       │  │       ││
# MAGIC │ │ Feature Store│  │ LightGBM  │  │ 전체 사용자 ││
# MAGIC │ │ 갱신    │  │ + MLflow  │  │ 스코어링  ││
# MAGIC │ └─────────────┘  └─────────────┘  └──────┬──────┘│
# MAGIC │                        │    │
# MAGIC │                    ┌──────┴──────┐│
# MAGIC │                    │ Task 4   ││
# MAGIC │                    │ Monitor   ││
# MAGIC │                    │ Check    ││
# MAGIC │                    └─────────────┘│
# MAGIC └─────────────────────────────────────────────────────────┘
# MAGIC
# MAGIC 운영: 주 1회 재학습 + 일 4회 배치 예측
# MAGIC    Cron: 0 0 2 ? * MON (매주 월요일 새벽 2시 재학습)
# MAGIC       0 0 */6 * * ? (6시간마다 배치 예측)
# MAGIC
# MAGIC 개발: 일 4회 재학습
# MAGIC    Cron: 0 0 */6 * * ? (6시간마다 재학습 + 예측)
# MAGIC ```
# MAGIC
# MAGIC ### Agent 기반 트리거
# MAGIC
# MAGIC Databricks Agent가 모니터링 결과를 확인하고,
# MAGIC 드리프트가 감지되면 **자동으로 재학습 Job을 트리거** 할 수 있습니다.
# MAGIC
# MAGIC ```python
# MAGIC # Agent Tool로 등록 가능한 함수 예시
# MAGIC def trigger_retrain_if_needed():
# MAGIC   """모니터링 결과를 확인하고, 필요 시 재학습을 트리거합니다."""
# MAGIC   # 1. 최근 모니터링 메트릭 확인
# MAGIC   # 2. PSI > 0.2 or AUC 5% 하락 시
# MAGIC   # 3. databricks.sdk.WorkspaceClient().jobs.run_now(job_id=...)
# MAGIC   pass
# MAGIC ```

# COMMAND ----------

# Job 설정 JSON 예시 (실제로는 databricks CLI나 SDK로 생성)
job_config = {
  "name": "smarttv_mlops_pipeline",
  "schedule": {
    "production": {
      "retrain": "0 0 2 ? * MON",    # 매주 월요일 새벽 2시
      "batch_predict": "0 0 */6 * * ?",  # 6시간마다
      "monitor_check": "0 0 */6 * * ?",  # 6시간마다
    },
    "development": {
      "retrain": "0 0 */6 * * ?",     # 6시간마다
      "batch_predict": "매 재학습 후",
    }
  },
  "tasks": [
    {"key": "feature_update", "notebook": "02_generate_synthetic_data", "depends_on": []},
    {"key": "retrain_model",  "notebook": "08_ml_recommendation",    "depends_on": ["feature_update"]},
    {"key": "batch_scoring",  "notebook": "08_ml_recommendation",    "depends_on": ["retrain_model"]},
    {"key": "monitor_check",  "notebook": "08_ml_recommendation",    "depends_on": ["batch_scoring"]},
  ],
  "alerts": {
    "on_failure": "email",
    "on_drift_detected": "trigger_retrain",
  }
}

print("=== MLOps Job 설정 예시 ===")
print(json.dumps(job_config, indent=2, ensure_ascii=False))

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 학습 정리
# MAGIC
# MAGIC | 단계 | Databricks 기능 | 실습 내용 |
# MAGIC |------|----------------|-----------|
# MAGIC |**Feature Store (Offline)**| UC Delta Table | user_behavior_features 등록, 피처 재사용 |
# MAGIC |**Feature Store (Online)**| Cosmos DB/DynamoDB 동기화 | 실시간 서빙용 피처 (개념 설명) |
# MAGIC |**모델 학습**| LightGBM + MLflow | 3가지 하이퍼파라미터 비교, 메트릭 로깅 |
# MAGIC |**SHAP 설명**| shap 라이브러리 | 전역/개별 피처 중요도 분석 |
# MAGIC |**UC Model Registry**| 모델 버전 관리 | Champion/Challenger, Alias, 태그 |
# MAGIC |**배치 예측**| Spark + Pandas | 전체 사용자 스코어링 → gold 테이블 |
# MAGIC |**증분 재학습**| retrain_model() | 새 데이터로 자동 재학습 |
# MAGIC |**모니터링**| 예측 분포 통계 | PSI, 정확도 하락 감지 |
# MAGIC |**스케줄링**| Databricks Jobs | 운영: 주 1회 재학습 + 일 4회 예측 |
# MAGIC |**Agent 트리거**| UC Function / Agent Tool | 드리프트 감지 → 자동 재학습 |
# MAGIC
# MAGIC ### Feature Store: Offline vs Online 정리
# MAGIC
# MAGIC | |**Offline Store**|**Online Store**|
# MAGIC |---|---|---|
# MAGIC |**저장소**| Delta Table (Unity Catalog) | Cosmos DB / DynamoDB |
# MAGIC |**응답 시간**| 초~분 | 밀리초 |
# MAGIC |**데이터 양**| 전체 히스토리 | 최신 값만 |
# MAGIC |**사용처**| 배치 학습, 배치 예측 | 실시간 서빙 (Model Serving) |
# MAGIC |**동기화**| - | Offline → Online 자동 동기화 |
# MAGIC |**설정 방법**| `fe.create_table()` | Feature Spec에 `online_stores` 추가 |
# MAGIC
# MAGIC ### 비즈니스 가치
# MAGIC
# MAGIC 이 MLOps 파이프라인을 통해:
# MAGIC 1.**광고 타겟팅 최적화**→ 클릭 확률 높은 사용자에게 프리미엄 광고 노출 → eCPM 향상
# MAGIC 2.**자동 재학습**→ 사용자 행동 변화에 자동 대응 → 모델 정확도 유지
# MAGIC 3.**피처 재사용**→ Feature Store로 팀 간 협업 → 개발 속도 향상
# MAGIC 4.**모델 설명**→ SHAP로 비즈니스 의사결정 근거 제공
