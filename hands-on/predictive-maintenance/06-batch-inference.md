# 06. 배치 추론 (Batch Inference)

> **전체 노트북 코드**: [06_batch_inference.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/06_batch_inference.py)


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

---

## 5. 고장 유형별 확률 추정 (Fault Type Probability)

> **전체 노트북 코드**: [06_batch_inference.py (고장 유형별 확률 추정 섹션)](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/06_batch_inference.py)

현재 모델은 이진 분류(고장/정상)만 수행합니다. 고장 유형별 확률은 학습 데이터의 고장 유형 분포를 기반으로 **사후 추정**합니다.

```python
# 학습 데이터의 고장 유형 비율 (AI4I 2020 기준)
fault_type_ratios = {
    "TWF": 0.10,   # Tool Wear Failure (공구 마모)
    "HDF": 0.35,   # Heat Dissipation Failure (열 방출 고장)
    "PWF": 0.25,   # Power Failure (전력 고장)
    "OSF": 0.20,   # Overstrain Failure (과부하 고장)
    "RNF": 0.10    # Random Failure (랜덤 고장)
}

# 고장 확률 × 유형별 비율 = 유형별 확률
for fault_type, ratio in fault_type_ratios.items():
    predictions = predictions.withColumn(
        f"prob_{fault_type.lower()}",
        F.round(F.col("failure_probability") * F.lit(ratio), 4)
    )
```

{% hint style="info" %}
이 방식은 사후 추정(post-hoc estimation)으로, 실제 운영에서는 고장 유형별 **멀티레이블 분류 모델**을 별도로 학습하는 것을 권장합니다.
{% endhint %}

## 6. 우선순위 기반 유지보수 스케줄링

위험 설비 목록을 기반으로 **즉시 점검 일정**을 수립합니다.

| 우선순위 | 조건 | 조치 | 타임라인 |
|----------|------|------|----------|
| **P0 (긴급)** | CRITICAL + tool_wear > 200분 | 즉시 라인 정지, 공구 교체 | 발견 즉시 |
| **P1 (높음)** | CRITICAL 등급 | 당일 내 점검 | 4시간 이내 |
| **P2 (보통)** | HIGH 등급 | 다음 교대 시 점검 | 8시간 이내 |
| **P3 (낮음)** | MEDIUM 등급 | 다음 정기 점검 시 확인 | 1주일 이내 |

### 자동 알림 설정 방법

1. **Databricks SQL Alert**: CRITICAL 건수가 임계값을 초과하면 이메일/Slack 자동 알림
2. **Workflows 알림**: 배치 추론 Job 완료 시 결과 요약을 이메일로 발송
3. **SQL Dashboard**: 정비팀이 웹 브라우저에서 실시간으로 위험 설비 현황을 확인

## 7. 센서 해석 가이드

CRITICAL/HIGH 위험 설비가 감지되었을 때, 각 센서값의 의미와 점검 포인트입니다.

| 센서 | 의미 | 이상 징후 | 점검 포인트 |
|------|------|----------|------------|
| **`tool_wear_min`** | 공구 마모도 | 200분 이상이면 수명 임박 | 공구 교체 시점 판단 |
| **`torque_nm`** | 토크 | 비정상적으로 높음 | 설비 부하 과다 또는 윤활 문제 |
| **`rotational_speed_rpm`** | 회전속도 | 급격한 변동 | 베어링 이상 징후 |
| **`air_temperature_k`** | 공기 온도 | 급등 | 냉각 시스템 이상 |

{% hint style="warning" %}
예측 결과를 기존의 MES(Manufacturing Execution System)나 CMMS(Computerized Maintenance Management System)와 연동하면, 정비 작업 지시가 자동으로 생성되는 **완전 자동화된 예지보전 시스템**을 구축할 수 있습니다.
{% endhint %}

**다음 단계**: [07. 비정형 이상탐지](07-anomaly-detection.md)
