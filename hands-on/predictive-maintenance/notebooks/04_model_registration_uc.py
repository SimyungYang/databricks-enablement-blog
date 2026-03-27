# Databricks notebook source
# MAGIC %md
# MAGIC # Unity Catalog 모델 레지스트리 등록
# MAGIC
# MAGIC 최적의 모델을 **Unity Catalog 모델 레지스트리**에 등록하고, 에일리어스(Alias)를 통해 모델의 생애 주기를 관리합니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC - **Unity Catalog Model Registry**: 모델 버전의 중앙 관리
# MAGIC - **모델 에일리어스 (Alias)**: Champion/Challenger 패턴으로 안전한 배포
# MAGIC - **모델 계보 (Lineage)**: 데이터 → 실험 → 모델 간 전체 추적
# MAGIC - **접근 제어**: 모델에 대한 세분화된 권한 관리

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 최적 모델 검색
# MAGIC
# MAGIC MLflow의 `search_runs` API를 사용하여 가장 성능이 좋은 모델을 프로그래밍 방식으로 찾습니다.

# COMMAND ----------

# DBTITLE 1,최적 실험 Run 검색
import mlflow
from mlflow import MlflowClient

client = MlflowClient()
model_name = f"{catalog}.{db}.lgit_predictive_maintenance"

# 실험 검색
xp_name = "lgit_predictive_maintenance"
xp_path = f"/Users/{current_user}"
mlflow.set_experiment(f"{xp_path}/{xp_name}")

experiment_id = mlflow.search_experiments(
    filter_string=f"name LIKE '{xp_path}/{xp_name}%'",
    order_by=["last_update_time DESC"]
)[0].experiment_id

# 최적 모델 검색 (val_f1_score 기준)
best_run = mlflow.search_runs(
    experiment_ids=experiment_id,
    order_by=["metrics.val_f1_score DESC"],
    max_results=1,
    filter_string="status = 'FINISHED'"
)

print(f"=== 최적 모델 ===")
print(f"Run ID: {best_run.iloc[0]['run_id']}")
print(f"Run Name: {best_run.iloc[0]['tags.mlflow.runName']}")
print(f"Val F1: {best_run.iloc[0]['metrics.val_f1_score']:.4f}")
print(f"Val AUC: {best_run.iloc[0]['metrics.val_auc']:.4f}")

display(best_run)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Unity Catalog에 모델 등록
# MAGIC
# MAGIC `mlflow.register_model()`을 통해 모델을 UC 레지스트리에 등록합니다.
# MAGIC 등록된 모델은 **카탈로그.스키마.모델명** 의 3-Level 네임스페이스로 관리됩니다.

# COMMAND ----------

# DBTITLE 1,모델 등록
run_id = best_run.iloc[0]['run_id']
print(f"모델 등록: {model_name}")

model_details = mlflow.register_model(
    model_uri=f"runs:/{run_id}/xgboost_model",
    name=model_name
)

print(f"등록 완료 — 모델: {model_details.name}, 버전: {model_details.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 모델 메타데이터 추가
# MAGIC
# MAGIC 등록된 모델에 설명, 태그 등의 메타데이터를 추가하여 **거버넌스**를 강화합니다.

# COMMAND ----------

# DBTITLE 1,모델 설명 추가
# 모델 전체 설명
client.update_registered_model(
    name=model_name,
    description="""LG Innotek 예지보전(Predictive Maintenance) 모델.
    AI4I 2020 데이터셋 기반 XGBoost 분류기.
    입력: 설비 센서값 (온도, 회전속도, 토크, 공구 마모 등)
    출력: 고장 발생 확률 및 이진 분류 결과.
    용도: 제조 설비의 고장을 사전에 예측하여 예방 정비 수행."""
)

# 버전별 상세 정보
best_f1 = best_run.iloc[0]['metrics.val_f1_score']
best_auc = best_run.iloc[0]['metrics.val_auc']
run_name = best_run.iloc[0]['tags.mlflow.runName']

client.update_model_version(
    name=model_name,
    version=model_details.version,
    description=f"XGBoost 모델 (Run: {run_name}). Val F1: {best_f1:.4f}, Val AUC: {best_auc:.4f}."
)

# 태그 추가
client.set_model_version_tag(name=model_name, version=model_details.version, key="val_f1_score", value=f"{best_f1:.4f}")
client.set_model_version_tag(name=model_name, version=model_details.version, key="val_auc", value=f"{best_auc:.4f}")
# 참고: 워크스페이스에 태그 정책이 설정된 경우, 허용된 값만 사용 가능합니다.
# 태그 정책 오류 방지를 위해 try-except 처리
try:
    client.set_model_version_tag(name=model_name, version=model_details.version, key="domain", value="customer_demo")
except Exception as e:
    print(f"domain 태그 설정 참고: {e}")

try:
    client.set_model_version_tag(name=model_name, version=model_details.version, key="data_source", value="ai4i_2020")
except Exception as e:
    print(f"data_source 태그 설정 참고: {e}")

print("모델 메타데이터 추가 완료")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. 모델 에일리어스 (Alias) 설정
# MAGIC
# MAGIC **에일리어스(Alias)** 는 모델의 생애 주기 단계를 나타내는 레이블입니다.
# MAGIC
# MAGIC | 에일리어스 | 설명 |
# MAGIC |-----------|------|
# MAGIC | `Baseline` | 최초 등록 시 부여 |
# MAGIC | `Challenger` | 검증 대기 중인 후보 모델 |
# MAGIC | `Champion` | 현재 운영 중인 모델 |
# MAGIC
# MAGIC 배포 시 에일리어스를 참조하므로, 코드 변경 없이 모델 교체가 가능합니다.

# COMMAND ----------

# DBTITLE 1,Challenger 에일리어스 설정
# 새 모델을 Challenger로 설정
client.set_registered_model_alias(
    name=model_name,
    alias="Challenger",
    version=model_details.version
)

print(f"모델 '{model_name}' v{model_details.version} → Challenger 에일리어스 설정 완료")

# Champion이 없는 경우 바로 Champion으로도 설정
try:
    champion = client.get_model_version_by_alias(model_name, "Champion")
    print(f"기존 Champion 존재: v{champion.version}")
except:
    print("기존 Champion이 없으므로, 이 버전을 Champion으로도 설정합니다.")
    client.set_registered_model_alias(
        name=model_name,
        alias="Champion",
        version=model_details.version
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. 등록된 모델 확인
# MAGIC
# MAGIC Unity Catalog Explorer에서 모델의 버전, 에일리어스, 계보(Lineage)를 시각적으로 확인할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,등록된 모델 정보 조회
model_info = client.get_registered_model(model_name)
print(f"모델: {model_info.name}")
print(f"설명: {model_info.description[:100]}...")

if model_info.aliases:
    for alias_info in model_info.aliases:
        # alias_info가 문자열인 경우와 객체인 경우 모두 처리
        alias_name = alias_info.alias if hasattr(alias_info, 'alias') else str(alias_info)
        try:
            version = client.get_model_version_by_alias(model_name, alias_name)
            print(f"\n에일리어스: {alias_name}")
            print(f"  버전: {version.version}")
            print(f"  상태: {version.status}")
            desc = version.description or "N/A"
            print(f"  설명: {desc[:80]}...")
        except Exception as e:
            print(f"\n에일리어스 {alias_name} 조회 오류: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC 이 노트북에서 수행한 작업:
# MAGIC 1. MLflow에서 **최적 모델 자동 검색** (val_f1_score 기준)
# MAGIC 2. **Unity Catalog 모델 레지스트리** 에 모델 등록
# MAGIC 3. 모델 **설명, 태그** 등 메타데이터 추가 (거버넌스)
# MAGIC 4. **Challenger/Champion 에일리어스** 설정
# MAGIC
# MAGIC **다음 단계:** [챌린저 모델 검증]($./05_challenger_validation)
