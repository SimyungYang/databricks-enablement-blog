# 06. 배치 추론 (Batch Inference)

**목적**: Champion 모델을 PySpark UDF로 변환하여 클러스터 전체에서 분산 추론하고, 위험 등급을 자동 부여합니다.

**사용 Databricks 기능**: `PySpark UDF 분산 추론`, `Delta Lake ACID 트랜잭션`, `Workflows 연동`

---

## 운영 스펙

| 항목 | 설정 |
|------|------|
| 실행 주기 | 일 4회 (6시간 간격) |
| 입력 | 설비 센서 데이터 테이블 |
| 출력 | 고장 확률 + 위험 등급 + 모델 버전 + 타임스탬프 |

## 1. Champion 모델을 PySpark UDF로 로드

`@Champion` 에일리어스를 참조하므로 모델 버전이 바뀌어도 코드 수정이 필요 없습니다.

```python
champion_udf = mlflow.pyfunc.spark_udf(
    spark,
    model_uri=f"models:/{model_name}@Champion",
    result_type="double"
)
```

## 2. 분산 배치 예측 + 위험 등급 부여

Spark가 자동으로 클러스터의 모든 노드에 작업을 분산합니다.

```python
preds_df = (
    inference_df
    .withColumn("failure_probability", champion_udf(*feature_columns))
    .withColumn("predicted_failure",
                F.when(F.col("failure_probability") > 0.5, 1).otherwise(0))
    .withColumn("risk_level",
        F.when(F.col("failure_probability") > 0.8, "CRITICAL")
        .when(F.col("failure_probability") > 0.5, "HIGH")
        .when(F.col("failure_probability") > 0.3, "MEDIUM")
        .otherwise("LOW"))
    .withColumn("model_name", F.lit(model_name))
    .withColumn("model_version", F.lit(int(champion_info.version)))
)
```

## 3. Delta Lake에 예측 결과 저장

Append 모드로 저장하여 시간별 예측 이력이 누적됩니다. ACID 트랜잭션이 보장됩니다.

```python
preds_df.write.mode("append").option("mergeSchema", "true") \
    .saveAsTable("lgit_pm_inference_results")
```

## 4. 위험 설비 분석 쿼리

저장된 예측 결과에서 CRITICAL/HIGH 위험 설비를 즉시 조회하여 정비팀 액션 아이템을 생성합니다.

```sql
-- CRITICAL/HIGH 위험 설비 목록 (즉시 점검 필요)
SELECT
  udi, product_quality, failure_probability, risk_level,
  air_temperature_k, rotational_speed_rpm, torque_nm, tool_wear_min,
  inference_timestamp
FROM lgit_pm_inference_results
WHERE risk_level IN ('CRITICAL', 'HIGH')
ORDER BY failure_probability DESC
LIMIT 20
```

{% hint style="success" %}
이 노트북은 Databricks Workflow에서 **일 4회** 자동 실행됩니다. `model_version` 컬럼이 함께 저장되므로, 모델 변경 전후의 예측 결과를 비교 분석할 수 있습니다.
{% endhint %}

**다음 단계**: [07. 비정형 이상탐지](07-anomaly-detection.md)
