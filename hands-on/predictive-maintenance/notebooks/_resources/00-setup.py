# Databricks notebook source
# MAGIC %md
# MAGIC # 환경 설정 (Setup)
# MAGIC 이 노트북은 LG Innotek MLOps PoC 데모에 필요한 환경을 설정합니다.

# COMMAND ----------

dbutils.widgets.dropdown("reset_all_data", "false", ["true", "false"], "Reset all data")
reset_all_data = dbutils.widgets.get("reset_all_data") == "true"

# COMMAND ----------

import re

current_user = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
reformat_current_user = current_user.split("@")[0].lower().replace(".", "_")

# ============================================================
# 카탈로그 및 스키마 설정 (사용자별 자동 분리)
# ============================================================
# 여러 사용자가 동시에 교육을 진행해도 테이블/모델이 충돌하지 않도록
# 사용자 이메일 기반으로 카탈로그 이름을 자동 생성합니다.
#
# 예: simyung.yang@databricks.com → catalog = "simyung_yang"
#     taehee.kim@lginnotek.com   → catalog = "taehee_kim"
#
# 교육 환경에서는 각 수강자가 자신만의 카탈로그를 사용하므로
# 다른 수강자의 데이터와 모델에 영향을 주지 않습니다.
# ============================================================

catalog = reformat_current_user  # 사용자별 고유 카탈로그
db = "lgit_mlops_poc"            # 스키마는 동일 (카탈로그로 분리되므로)

# 모델 이름 (3-Level Namespace: catalog.schema.model)
structured_model_name = f"{catalog}.{db}.lgit_predictive_maintenance"
unstructured_model_name = f"{catalog}.{db}.lgit_anomaly_detection"

print(f"=" * 60)
print(f"🔧 환경 설정 (사용자별 자동 분리)")
print(f"=" * 60)
print(f"  사용자:    {current_user}")
print(f"  카탈로그:  {catalog} (← 사용자별 고유)")
print(f"  스키마:    {db}")
print(f"  모델 경로: {structured_model_name}")
print(f"=" * 60)

# COMMAND ----------

# 카탈로그 및 스키마 생성
spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{db}")
spark.sql(f"USE SCHEMA {db}")

print(f"현재 카탈로그: {catalog}, 스키마: {db}")

# COMMAND ----------

# DBTITLE 1,MLflow 레지스트리 설정
import mlflow
mlflow.set_registry_uri("databricks-uc")

# COMMAND ----------

# DBTITLE 1,AI4I 2020 예지보전 데이터 로드
import pandas as pd
import requests
from io import StringIO

bronze_table = "lgit_pm_bronze"

if reset_all_data or not spark.catalog.tableExists(bronze_table):
    print("AI4I 2020 Predictive Maintenance 데이터셋을 다운로드합니다...")

    # UCI ML Repository에서 AI4I 2020 데이터셋 다운로드
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
    response = requests.get(url)

    if response.status_code == 200:
        df = pd.read_csv(StringIO(response.text))
    else:
        # 대체 URL 시도
        print("UCI에서 직접 다운로드 실패, 대체 데이터 생성...")
        import numpy as np
        np.random.seed(42)
        n = 10000
        df = pd.DataFrame({
            'UDI': range(1, n+1),
            'Product ID': [f"{'LMH'[np.random.randint(0,3)]}{np.random.randint(10000,99999)}" for _ in range(n)],
            'Type': np.random.choice(['L', 'M', 'H'], n, p=[0.6, 0.3, 0.1]),
            'Air temperature [K]': np.random.normal(300, 2, n),
            'Process temperature [K]': np.random.normal(310, 1.5, n),
            'Rotational speed [rpm]': np.random.normal(1539, 180, n).astype(int),
            'Torque [Nm]': np.random.normal(40, 10, n),
            'Tool wear [min]': np.random.randint(0, 240, n),
            'Machine failure': np.random.choice([0, 1], n, p=[0.966, 0.034]),
            'TWF': np.zeros(n, dtype=int),
            'HDF': np.zeros(n, dtype=int),
            'PWF': np.zeros(n, dtype=int),
            'OSF': np.zeros(n, dtype=int),
            'RNF': np.zeros(n, dtype=int)
        })
        # 고장 유형 분배
        fail_idx = df[df['Machine failure'] == 1].index
        for idx in fail_idx:
            fail_type = np.random.choice(['TWF', 'HDF', 'PWF', 'OSF', 'RNF'], p=[0.1, 0.35, 0.25, 0.2, 0.1])
            df.loc[idx, fail_type] = 1

    # 컬럼명 정리
    df.columns = [
        c.lower()
        .replace(' [k]', '_k')
        .replace(' [rpm]', '_rpm')
        .replace(' [nm]', '_nm')
        .replace(' [min]', '_min')
        .replace(' ', '_')
        for c in df.columns
    ]

    spark.createDataFrame(df).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(bronze_table)
    print(f"'{bronze_table}' 테이블 생성 완료 ({len(df)} rows)")
else:
    print(f"'{bronze_table}' 테이블이 이미 존재합니다.")

# COMMAND ----------

# DBTITLE 1,Volume 생성 (비정형 데이터 저장용)
volume_name = "lgit_images"
spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{db}.{volume_name}")
print(f"Volume 생성 완료: {catalog}.{db}.{volume_name}")

# COMMAND ----------

# DBTITLE 1,경고 및 로깅 설정
import warnings
import logging

warnings.filterwarnings("ignore")
logging.getLogger("mlflow").setLevel(logging.ERROR)
logging.getLogger("py4j").setLevel(logging.ERROR)

print("✅ 환경 설정 완료")
