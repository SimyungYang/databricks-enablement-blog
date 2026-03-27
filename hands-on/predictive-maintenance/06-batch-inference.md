# 06. 배치 추론 (Batch Inference)

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
