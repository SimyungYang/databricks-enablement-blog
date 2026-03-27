# 02. 피처 엔지니어링 (Feature Engineering)

**목적**: 센서 데이터를 탐색하고, 예지보전에 유용한 파생 피처를 생성합니다.

**주요 개념**:
- EDA (탐색적 데이터 분석) — SQL과 Pandas on Spark API 활용
- 도메인 지식 기반 파생 피처 7개 생성
- Train/Test 80:20 분할 후 Delta Lake 저장

**핵심 코드 — 피처 엔지니어링 함수**:

```python
def engineer_pm_features(df: DataFrame) -> DataFrame:
    df_features = (
        df
        # 온도차: 과열 징후 탐지
        .withColumn("temp_diff",
                    F.col("process_temperature_k") - F.col("air_temperature_k"))
        # 기계 전력 (W): 토크 x 회전속도
        .withColumn("power",
                    F.col("torque_nm") * F.col("rotational_speed_rpm") * F.lit(2 * math.pi / 60))
        # 기계적 스트레인: 토크 x 공구 마모
        .withColumn("strain", F.col("torque_nm") * F.col("tool_wear_min"))
        # 과열 플래그
        .withColumn("overheat_flag",
                    F.when(F.col("process_temperature_k") - F.col("air_temperature_k") > 8.6, 1)
                    .otherwise(0))
        # 복합 위험 점수
        .withColumn("risk_score",
                    (F.col("tool_wear_min") / F.lit(240.0)) * 0.3 +
                    (F.col("torque_nm") / F.lit(80.0)) * 0.3 +
                    F.when(F.col("process_temperature_k") - F.col("air_temperature_k") > 8.6, 0.4)
                    .otherwise(0.0))
    )
    return df_features
```

**사용 Databricks 기능**: Delta Lake, Pandas on Spark API, Unity Catalog 메타데이터

{% hint style="success" %}
Unity Catalog에 테이블을 저장하면 **데이터 계보(Lineage)** 가 자동으로 추적됩니다. 이후 모델 학습 시 어떤 테이블의 어떤 버전으로 학습했는지 추적할 수 있습니다.
{% endhint %}
