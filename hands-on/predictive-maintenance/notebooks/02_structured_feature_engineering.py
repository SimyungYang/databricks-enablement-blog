# Databricks notebook source
# MAGIC %md
# MAGIC # 예지보전 피처 엔지니어링 (Predictive Maintenance Feature Engineering)
# MAGIC
# MAGIC 본 노트북에서는 **AI4I 2020 Predictive Maintenance Dataset**을 탐색하고, 모델 학습에 필요한 피처를 준비합니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC - **Delta Lake**: ACID 트랜잭션 기반 테이블 저장
# MAGIC - **Pandas on Spark API**: 대규모 데이터에서도 Pandas 문법 사용
# MAGIC - **Unity Catalog**: 피처 테이블의 중앙 관리 및 계보(Lineage) 추적
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **데이터 소스**: UCI AI4I 2020 Predictive Maintenance Dataset
# MAGIC - 10,000건 규모의 산업 센서 데이터
# MAGIC - 피처: 공기 온도, 공정 온도, 회전속도, 토크, 공구 마모 등
# MAGIC - 타겟: 기계 고장 여부 (Machine failure)

# COMMAND ----------

# MAGIC %pip install --quiet mlflow --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 데이터 탐색 (Exploratory Data Analysis)
# MAGIC
# MAGIC Databricks에서는 노트북의 기본 시각화 도구를 활용하거나, SQL 쿼리 결과에서 바로 차트를 생성할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,원본 Bronze 데이터 확인
df_bronze = spark.table("lgit_pm_bronze")
display(df_bronze)

# COMMAND ----------

# DBTITLE 1,데이터 통계 요약
display(df_bronze.describe())

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 고장 유형별 분포 확인
# MAGIC SELECT
# MAGIC   machine_failure,
# MAGIC   SUM(twf) as tool_wear_failure,
# MAGIC   SUM(hdf) as heat_dissipation_failure,
# MAGIC   SUM(pwf) as power_failure,
# MAGIC   SUM(osf) as overstrain_failure,
# MAGIC   SUM(rnf) as random_failure,
# MAGIC   COUNT(*) as total_count
# MAGIC FROM lgit_pm_bronze
# MAGIC GROUP BY machine_failure

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 제품 타입별 고장률 분석
# MAGIC SELECT
# MAGIC   type as product_type,
# MAGIC   COUNT(*) as total,
# MAGIC   SUM(machine_failure) as failures,
# MAGIC   ROUND(SUM(machine_failure) / COUNT(*) * 100, 2) as failure_rate_pct
# MAGIC FROM lgit_pm_bronze
# MAGIC GROUP BY type
# MAGIC ORDER BY failure_rate_pct DESC

# COMMAND ----------

# DBTITLE 1,센서 데이터 분포 시각화 (Pandas on Spark)
# Pandas on Spark API를 활용하면 대규모 데이터에서도 Pandas 문법으로 분석 가능
psdf = df_bronze.pandas_api()
display(psdf[['air_temperature_k', 'process_temperature_k', 'rotational_speed_rpm', 'torque_nm', 'tool_wear_min']].describe())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. 피처 엔지니어링 (Feature Engineering)
# MAGIC
# MAGIC 센서 데이터로부터 예지보전에 유용한 파생 피처를 생성합니다.
# MAGIC
# MAGIC ### 생성할 피처:
# MAGIC 1. **온도차 (temp_diff)**: 공정 온도 - 공기 온도 → 과열 징후
# MAGIC 2. **전력 (power)**: 토크 × 회전속도 × (2π/60) → 기계 부하 지표
# MAGIC 3. **공구 마모율 (tool_wear_rate)**: 마모/회전속도 → 공구 열화 속도
# MAGIC 4. **토크 변동 지수 (strain)**: 토크 × 공구 마모 → 기계적 스트레인
# MAGIC 5. **과열 플래그 (overheat_flag)**: 온도차 > 임계값 → 과열 경고
# MAGIC 6. **제품 품질 등급 인코딩**: L/M/H → 0/1/2

# COMMAND ----------

# DBTITLE 1,피처 엔지니어링 함수 정의
import pyspark.sql.functions as F
from pyspark.sql import DataFrame
import math


def engineer_pm_features(df: DataFrame) -> DataFrame:
    """
    예지보전 피처 엔지니어링 함수
    - 센서 데이터로부터 파생 피처를 생성합니다.
    - Spark DataFrame 기반으로 대규모 데이터에서도 확장 가능합니다.
    """

    df_features = (
        df
        # 1. 온도차: 과열 징후 탐지
        .withColumn("temp_diff",
                    F.col("process_temperature_k") - F.col("air_temperature_k"))

        # 2. 기계 전력 (W): 토크 × 회전속도 × (2π/60)
        .withColumn("power",
                    F.col("torque_nm") * F.col("rotational_speed_rpm") * F.lit(2 * math.pi / 60))

        # 3. 공구 마모율: 마모도 / 회전속도
        .withColumn("tool_wear_rate",
                    F.when(F.col("rotational_speed_rpm") > 0,
                           F.col("tool_wear_min") / F.col("rotational_speed_rpm"))
                    .otherwise(0))

        # 4. 기계적 스트레인: 토크 × 공구 마모
        .withColumn("strain",
                    F.col("torque_nm") * F.col("tool_wear_min"))

        # 5. 과열 플래그: 온도차 > 8.6K (데이터셋 기준 상위 분위수)
        .withColumn("overheat_flag",
                    F.when(F.col("process_temperature_k") - F.col("air_temperature_k") > 8.6, 1)
                    .otherwise(0))

        # 6. 제품 품질 등급 인코딩: L=0, M=1, H=2
        .withColumn("product_quality",
                    F.when(F.col("type") == "L", 0)
                    .when(F.col("type") == "M", 1)
                    .otherwise(2))

        # 7. 위험 점수 (복합 지표): 정규화된 복합 위험도
        .withColumn("risk_score",
                    (F.col("tool_wear_min") / F.lit(240.0)) * 0.3 +
                    (F.col("torque_nm") / F.lit(80.0)) * 0.3 +
                    F.when(F.col("process_temperature_k") - F.col("air_temperature_k") > 8.6, 0.4)
                    .otherwise(0.0))
    )

    return df_features

# COMMAND ----------

# DBTITLE 1,피처 생성 및 확인
df_features = engineer_pm_features(df_bronze)
display(df_features.select(
    "udi", "type", "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "temp_diff", "power", "tool_wear_rate", "strain",
    "overheat_flag", "product_quality", "risk_score",
    "machine_failure"
))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 학습/테스트 데이터 분할 및 저장
# MAGIC
# MAGIC 준비된 피처를 **Delta Lake 테이블**로 저장합니다.
# MAGIC - 학습(Train) 80% / 테스트(Test) 20% 분할
# MAGIC - Unity Catalog를 통해 테이블-모델 간 **계보(Lineage)** 가 자동 추적됩니다.

# COMMAND ----------

# DBTITLE 1,학습용 피처 컬럼 선택
feature_columns = [
    "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "temp_diff", "power", "tool_wear_rate", "strain",
    "overheat_flag", "product_quality", "risk_score"
]

label_column = "machine_failure"

# 고장 유형 컬럼 (멀티라벨)
failure_type_columns = ["twf", "hdf", "pwf", "osf", "rnf"]

# 학습에 사용할 컬럼만 선택
df_training = df_features.select(
    "udi",  # Primary Key
    *feature_columns,
    *failure_type_columns,
    label_column
)

# COMMAND ----------

# DBTITLE 1,Train/Test 분할
df_training = (
    df_training
    .withColumn("random", F.rand(seed=42))
    .withColumn("split",
                F.when(F.col("random") < 0.8, "train")
                .otherwise("test"))
    .drop("random")
)

# 분할 확인
display(df_training.groupBy("split").count())

# COMMAND ----------

# DBTITLE 1,Delta Lake 테이블로 저장
training_table = "lgit_pm_training"

(df_training.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(training_table))

# 테이블 설명 추가 (Unity Catalog 메타데이터)
spark.sql(f"""
    COMMENT ON TABLE {catalog}.{db}.{training_table}
    IS '예지보전 학습 데이터: AI4I 2020 데이터셋 기반. 센서 피처 및 파생 피처 포함.
    원본: lgit_pm_bronze 테이블에서 피처 엔지니어링 수행.'
""")

print(f"학습 테이블 저장 완료: {catalog}.{db}.{training_table}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 저장된 데이터 확인
# MAGIC SELECT * FROM lgit_pm_training LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. 피처 상관관계 분석
# MAGIC
# MAGIC 생성된 피처와 타겟(고장 여부) 간의 상관관계를 확인합니다.

# COMMAND ----------

# DBTITLE 1,피처 상관관계 히트맵
import pandas as pd

# Pandas DataFrame으로 변환하여 상관관계 분석
pdf = df_training.filter("split = 'train'").select(*feature_columns, label_column).toPandas()
corr_matrix = pdf.corr()

# 타겟과의 상관관계만 표시
target_corr = corr_matrix[label_column].drop(label_column).sort_values(ascending=False)
print("=== 피처-고장 상관관계 (절대값 기준) ===")
for feat, corr_val in target_corr.items():
    print(f"  {feat:30s}: {corr_val:+.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC 이 노트북에서 수행한 작업:
# MAGIC 1. AI4I 2020 원본 데이터 탐색 (EDA)
# MAGIC 2. 예지보전에 유용한 7개의 파생 피처 생성
# MAGIC 3. Train/Test 분할 후 Delta Lake 테이블 저장
# MAGIC 4. Unity Catalog를 통한 메타데이터 및 계보 관리
# MAGIC
# MAGIC **다음 단계:** [XGBoost 모델 학습]($./03_structured_model_training)
