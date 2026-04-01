# 02. 피처 엔지니어링 (Feature Engineering)

> **전체 노트북 코드**: [02_structured_feature_engineering.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/02_structured_feature_engineering.py)


**목적**: AI4I 2020 센서 데이터를 탐색하고, 예지보전에 유용한 7개 파생 피처를 생성합니다.

**사용 Databricks 기능**: `Delta Lake`, `Pandas on Spark API`, `Unity Catalog` 메타데이터/계보

---

## 1. 데이터 탐색 (EDA)

SQL 쿼리로 고장 유형별 분포와 제품 타입별 고장률을 바로 확인합니다.

```sql
-- 제품 타입별 고장률 분석
SELECT
  type as product_type,
  COUNT(*) as total,
  SUM(machine_failure) as failures,
  ROUND(SUM(machine_failure) / COUNT(*) * 100, 2) as failure_rate_pct
FROM lgit_pm_bronze
GROUP BY type
ORDER BY failure_rate_pct DESC
```

Pandas on Spark API를 활용하면 대규모 데이터에서도 Pandas 문법으로 탐색할 수 있습니다.

```python
psdf = df_bronze.pandas_api()
display(psdf[['air_temperature_k', 'process_temperature_k',
              'rotational_speed_rpm', 'torque_nm', 'tool_wear_min']].describe())
```

## 2. 피처 엔지니어링 함수

도메인 지식 기반으로 7개 파생 피처를 생성합니다. Spark DataFrame 기반이므로 대규모 데이터에서도 확장 가능합니다.

```python
def engineer_pm_features(df: DataFrame) -> DataFrame:
    return (df
        .withColumn("temp_diff", F.col("process_temperature_k") - F.col("air_temperature_k"))
        .withColumn("power", F.col("torque_nm") * F.col("rotational_speed_rpm") * F.lit(2 * math.pi / 60))
        .withColumn("tool_wear_rate",
                    F.when(F.col("rotational_speed_rpm") > 0,
                           F.col("tool_wear_min") / F.col("rotational_speed_rpm")).otherwise(0))
        .withColumn("strain", F.col("torque_nm") * F.col("tool_wear_min"))
        .withColumn("overheat_flag",
                    F.when(F.col("process_temperature_k") - F.col("air_temperature_k") > 8.6, 1).otherwise(0))
        .withColumn("product_quality",
                    F.when(F.col("type") == "L", 0).when(F.col("type") == "M", 1).otherwise(2))
        .withColumn("risk_score",
                    (F.col("tool_wear_min") / F.lit(240.0)) * 0.3 +
                    (F.col("torque_nm") / F.lit(80.0)) * 0.3 +
                    F.when(F.col("process_temperature_k") - F.col("air_temperature_k") > 8.6, 0.4).otherwise(0.0))
    )
```

## 3. Train/Test 분할 및 Delta Lake 저장

80:20 비율로 데이터를 분할하고, Unity Catalog 테이블로 저장합니다.

```python
# Train/Test 분할
df_training = (
    df_training
    .withColumn("random", F.rand(seed=42))
    .withColumn("split", F.when(F.col("random") < 0.8, "train").otherwise("test"))
    .drop("random")
)

# Delta Lake 테이블로 저장
df_training.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("lgit_pm_training")

# Unity Catalog 메타데이터 추가
spark.sql(f"""
    COMMENT ON TABLE {catalog}.{db}.lgit_pm_training
    IS '예지보전 학습 데이터: AI4I 2020 데이터셋 기반. 센서 피처 및 파생 피처 포함.'
""")
```

{% hint style="success" %}
Unity Catalog에 테이블을 저장하면 **데이터 계보(Lineage)**가 자동으로 추적됩니다. 이후 모델 학습 시 어떤 테이블의 어떤 버전으로 학습했는지 추적할 수 있습니다.
{% endhint %}

## 4. 피처-타겟 상관관계 분석

생성된 피처와 고장 여부(machine_failure) 간 상관관계를 확인하여 피처의 유효성을 검증합니다.

```python
pdf = df_training.filter("split = 'train'").select(*feature_columns, label_column).toPandas()
target_corr = pdf.corr()[label_column].drop(label_column).sort_values(ascending=False)
for feat, corr_val in target_corr.items():
    print(f"  {feat:30s}: {corr_val:+.4f}")
```

{% hint style="info" %}
`risk_score`, `overheat_flag`, `strain` 등 도메인 지식 기반 파생 피처가 원본 센서값보다 타겟과의 상관관계가 높게 나타나는 경향이 있습니다. 이는 피처 엔지니어링의 효과를 보여줍니다.
{% endhint %}

**다음 단계**: [03. 모델 학습](03-model-training.md)
