# 02. 피처 엔지니어링 (Feature Engineering)

> **전체 노트북 코드**: [02_structured_feature_engineering.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/02_structured_feature_engineering.py)


**목적**: AI4I 2020 센서 데이터를 탐색하고, 예지보전에 유용한 7개 파생 피처를 생성합니다.

**사용 Databricks 기능**: `Delta Lake`, `Pandas on Spark API`, `Unity Catalog` 메타데이터/계보

---

## 왜 "피처 엔지니어링"이 필요한가?

**피처 엔지니어링이 모델 성능의 80%를 결정합니다.** 아무리 최신 알고리즘을 써도 피처가 나쁘면 정확도가 안 나옵니다. 반대로, 좋은 피처 하나가 알고리즘 10개를 이깁니다.

제조 현장에서 수집되는 센서 데이터(온도, 회전속도, 토크 등)는 그 자체로도 의미가 있지만, **숙련된 설비 엔지니어가 여러 센서값을 종합하여 판단하듯**ML 모델에게도 "종합 판단 지표"를 만들어 주면 예측 정확도가 크게 향상됩니다.

### Databricks 핵심 기능

| 기능 | 설명 | 제조 현장에서의 이점 |
|------|------|---------------------|
| **Delta Lake** | ACID 트랜잭션을 지원하는 데이터 저장 포맷 | 데이터 변환 중 오류가 나도 원본이 안전하게 보존됨. Time Travel로 과거 데이터 재현 가능 |
| **Pandas on Spark API** | 대규모 데이터에서도 Pandas 문법 사용 가능 | Python/Pandas에 익숙한 분석가도 빅데이터를 바로 다룰 수 있음 |
| **Unity Catalog** | 테이블, 모델, 피처의 중앙 관리 및 계보(Lineage) 추적 | "이 모델이 어떤 데이터로 학습되었는가?"를 자동으로 추적 |
| **Apache Spark** | 분산 병렬 처리 엔진 | 월 데이터가 수천만 건이 되면 Pandas로는 처리 불가능. Spark로 자동 분산 처리 |

---

## 1. 데이터 탐색 (EDA)

### EDA란 무엇이고, 왜 해야 하나?

ML 모델을 학습시키기 **전에** 반드시 데이터를 눈으로 확인하는 과정을 **EDA(탐색적 데이터 분석)** 라고 합니다. EDA에서 확인할 핵심 포인트는 다음과 같습니다.

| 확인 항목 | 이유 | 제조 현장 비유 |
|----------|------|---------------|
| **데이터 건수** | 학습에 충분한 양인지 확인. 고장 건수가 최소 200건 이상이어야 의미 있는 학습 가능 | 품질 검사에서 샘플 수가 충분한지 확인 |
| **결측치(빈 값)** | 센서 오작동이나 수집 누락 파악. 결측률 5% 이상이면 수집 파이프라인 점검 필수 | 계기판의 값이 빠져있으면 판단할 수 없음 |
| **고장 비율** | 정상:고장 비율이 극단적이면 모델이 "항상 정상"이라고만 예측할 위험 | 10,000건 중 고장은 약 340건(3.4%)뿐 - 매우 불균형 |
| **센서값 분포** | 이상치(outlier)나 비정상적 패턴 발견 | 회전속도가 갑자기 0이 되거나 온도가 비현실적으로 높은 경우 |

### 데이터 품질 검증 (Data Quality Check)

모델 학습 전 최소한의 품질 검증은 **필수** 입니다. 센서값의 물리적 범위를 검증하여 이상 데이터를 사전에 걸러냅니다.

```python
# 센서값 물리적 범위 검증 (실제 공장에서 매우 중요!)
range_checks = {
    "air_temperature_k": (250, 350),      # 절대온도 범위
    "process_temperature_k": (250, 400),
    "rotational_speed_rpm": (0, 5000),     # RPM 범위
    "torque_nm": (0, 200),                 # 토크 범위
    "tool_wear_min": (0, 500),             # 마모 시간 범위
}
for col, (low, high) in range_checks.items():
    out_of_range = df_bronze.filter((F.col(col) < low) | (F.col(col) > high)).count()
    status = "OK" if out_of_range == 0 else f"{out_of_range}건 이탈"
    print(f"  {col}: [{low}~{high}] {status}")
```

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

### 생성할 7개 파생 피처

도메인 지식 기반으로 7개 파생 피처를 생성합니다. 각 피처의 물리적 의미와 고장 예측에서의 역할은 다음과 같습니다.

| # | 피처명 | 계산 방법 | 물리적 의미 | 고장 예측에서의 역할 |
|---|--------|----------|-----------|-------------------|
| 1 | **temp_diff** | 공정온도 - 공기온도 | 설비 내부의 발열 정도 | 온도차가 클수록 냉각 불량 또는 마찰 과열 의심 |
| 2 | **power** | 토크 x 회전속도 x 2pi/60 | 설비가 소비하는 기계적 전력(와트) | 전력이 비정상적으로 높으면 과부하 상태 |
| 3 | **tool_wear_rate** | 공구마모 / 회전속도 | 단위 회전당 마모 속도 | 마모 속도가 빠르면 공구 교체 시기 임박 |
| 4 | **strain** | 토크 x 공구마모 | 기계적 변형(스트레인) 지수 | 높은 토크 + 높은 마모 = 고장 위험 급증 |
| 5 | **overheat_flag** | 온도차 > 8.6K이면 1 | 과열 경고 플래그 | 이진(0/1) 변수로 과열 상태 직접 표시 |
| 6 | **product_quality** | L->0, M->1, H->2 | 제품 품질 등급 수치화 | ML 모델은 숫자만 입력받으므로 문자를 숫자로 변환 |
| 7 | **risk_score** | 정규화된 종합 위험 점수 | 여러 피처를 종합한 위험도 | 단일 지표로 설비 위험 수준 파악 |

### 피처 생성의 물리학적 근거

- **전력(Power) = 토크 x 각속도**: 기계공학의 기본 공식입니다. rpm을 rad/s로 변환하기 위해 `2pi/60`을 곱합니다. 이 값이 설비의 정격 전력을 초과하면 과부하(Power Failure) 발생 가능성이 높아집니다.
- **스트레인(Strain) = 토크 x 공구마모**: 공구가 마모된 상태에서 높은 토크가 가해지면, 공구 파손이나 가공 불량이 발생할 확률이 급격히 증가합니다. 이는 두 독립 변수의 **교호작용(Interaction Effect)** 을 포착합니다.
- **과열 임계값 8.6K**: EDA에서 도출한 값으로, 공정온도와 공기온도의 차이가 8.6K(켈빈)을 초과하면 방열(Heat Dissipation) 고장이 빈번하게 발생하는 것으로 확인되었습니다.

{% hint style="warning" %}
과열 임계값 8.6K은 **현재 데이터 기준** 이므로, 계절이 바뀌거나 설비가 교체되면 반드시 재검토해야 합니다. 실무에서는 이런 임계값을 하드코딩하지 않고, **주기적으로 데이터 기반 재산출하는 파이프라인** 을 구축합니다.
{% endhint %}

Spark DataFrame 기반이므로 대규모 데이터에서도 확장 가능합니다.

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

### 왜 데이터를 나누어야 하나?

ML 모델의 목적은 **아직 보지 못한 새로운 데이터** 에 대해 정확하게 예측하는 것입니다. 전체 데이터로 학습하고 같은 데이터로 성능을 평가하면, 시험 문제를 미리 알려주고 시험을 보는 것과 같습니다. 이를 **과적합(Overfitting)** 이라고 합니다.

| 구분 | 비율 | 역할 | 비유 |
|------|------|------|------|
| **학습 데이터 (Train)** | 80% (약 8,000건) | 모델이 패턴을 학습하는 데 사용 | 교과서로 공부하는 것 |
| **테스트 데이터 (Test)** | 20% (약 2,000건) | 학습 후 모델의 실제 성능을 평가 | 처음 보는 시험 문제를 푸는 것 |

{% hint style="info" %}
시계열 센서 데이터에서는 무작위 분할 대신 **시간 기반 분할(Time-based Split)** 을 강력히 권장합니다. 무작위 분할은 미래 데이터가 학습에 섞일 수 있어 **데이터 누수(Data Leakage)** 위험이 있습니다. 이 실습에서는 교육 목적으로 무작위 분할을 사용하지만, 실무에서는 반드시 시간 기반으로 전환하세요.
{% endhint %}

### Delta Lake로 저장하는 이유

| 기능 | 설명 | ML 프로젝트에서의 이점 |
|------|------|---------------------|
| **ACID 트랜잭션** | 저장 도중 오류가 나도 데이터가 깨지지 않음 | 야간 배치에서 피처 업데이트 중 에러가 나도 이전 버전이 유지됨 |
| **Time Travel** | 과거 버전의 데이터를 조회/복원 가능 | "지난주 모델 학습 때 사용한 데이터"를 정확히 재현 가능 |
| **스키마 적용** | 컬럼 타입이 변경되면 자동으로 감지/방지 | 피처 타입이 실수로 바뀌는 것을 방지 |
| **Unity Catalog 연동** | 테이블-모델 간 계보(Lineage) 자동 추적 | 감사(Audit)나 규제 대응에 필수 |

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
Unity Catalog에 테이블을 저장하면 **데이터 계보(Lineage)** 가 자동으로 추적됩니다. 이후 모델 학습 시 어떤 테이블의 어떤 버전으로 학습했는지 추적할 수 있습니다.
{% endhint %}

## 4. 피처-타겟 상관관계 분석

### 상관관계 분석이란?

피처 엔지니어링으로 7개의 새로운 피처를 만들었지만, 이 피처들이 실제로 **고장 예측에 도움이 되는지** 검증해야 합니다. 피처를 만들어 놓고 검증하지 않으면, 쓸모없는 피처가 모델에 노이즈를 추가하여 오히려 성능을 떨어뜨리는 결과를 초래합니다.

**상관계수(r)** 의 해석 기준은 다음과 같습니다.

| 상관계수 범위 | 의미 | 제조 데이터에서의 해석 |
|-------------|------|------|
| **+0.5 ~ +1.0** | 강한 양의 상관관계 | 매우 강한 예측력. 이런 피처가 2~3개만 있어도 모델 성능이 크게 향상 |
| **+0.3 ~ +0.5** | 중간 양의 상관관계 | 유의미한 피처. 제조 센서 데이터에서 0.3 이상이면 반드시 포함 |
| **-0.3 ~ +0.3** | 약한 상관관계 | 선형적으로는 약하지만, 비선형 패턴이 숨어 있을 수 있어 바로 버리지 마세요 |
| **-1.0 ~ -0.3** | 음의 상관관계 | 역시 유의미합니다. 반비례 관계를 의미 |

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

## 5. Feature Store 등록 (Databricks Feature Engineering)

Feature Store에 등록하면 (1) 피처 검색/재사용, (2) 학습-서빙 일관성 자동 보장, (3) 피처 계보 자동 추적이 가능합니다. 이것 없이 MLOps를 하면, 6개월 후 "이 피처가 어디서 왔는지 아무도 모르는" 상황이 발생합니다.

### Feature Store vs 일반 Delta Table

| 항목 | Delta Table만 | Feature Store |
|------|:---:|:---:|
| 피처 검색/재사용 | 수동 | **카탈로그에서 검색** |
| 학습-서빙 일관성 | 보장 불가 | **자동 보장** |
| 피처 계보 추적 | 없음 | **자동** |
| Online Serving | 직접 구현 | **내장** |

```python
from databricks.feature_engineering import FeatureEngineeringClient

fe = FeatureEngineeringClient()
fe_table = fe.create_table(
    name=f"{catalog}.{db}.lgit_pm_features",
    primary_keys=["udi"],
    df=spark.table("lgit_pm_training"),
    description="AI4I 2020 예지보전 피처 테이블 — 7개 파생 피처 포함"
)
```

{% hint style="info" %}
2025년 현재, Feature Store는 ML 플랫폼의 필수 구성 요소가 되었습니다. Feature Store 없이 MLOps를 한다는 것은 버전 관리 없이 소프트웨어를 개발하는 것과 같습니다. 학습 시와 실시간 추론 시에 피처 계산이 달라서 성능이 떨어지는 **Training-Serving Skew** 는 가장 흔하면서도 찾기 어려운 버그입니다.
{% endhint %}

---

## 요약

### 수행한 작업

| 단계 | 수행 내용 | 핵심 개념 |
|------|----------|----------|
| **1. 데이터 탐색 (EDA)** | 10,000건의 센서 데이터를 확인하고, 고장 비율(3.4%)과 고장 유형 분포를 분석 | 데이터를 이해하지 못하면 좋은 모델을 만들 수 없다 |
| **2. 피처 엔지니어링** | 원본 5개 센서 피처로부터 7개의 파생 피처를 생성 | 도메인 지식을 수학적으로 모델링하여 예측 성능 향상 |
| **3. Train/Test 분할** | 학습용 80% / 테스트용 20%로 데이터를 분할 (seed=42로 재현성 보장) | 과적합 방지를 위해 학습과 평가 데이터를 분리 |
| **4. Delta Lake 저장** | 피처 테이블을 Delta Lake 형식으로 Unity Catalog에 저장 | ACID 트랜잭션, Time Travel, Lineage 자동 추적 |
| **5. 상관관계 분석** | 각 피처와 고장 여부 간의 상관계수를 계산하여 피처 유효성 검증 | 상관계수가 높은 피처가 모델 예측에 더 기여 |
| **6. Feature Store** | 피처 테이블을 Feature Store에 등록 | 학습-서빙 일관성 자동 보장 |

### 실무 전환 시 로드맵

- **PoC 단계 (지금)**: 정적 피처 7개, 배치 학습, 기본 Train/Test 분할
- **파일럿 단계 (3개월 후)**: 시계열 피처 추가(이동 평균, 변화율), 시간 기반 데이터 분할, Feature Store 연동
- **운영 단계 (6개월 후)**: 실시간 스트리밍 피처, 자동 피처 모니터링(드리프트 감지), A/B 테스트 기반 피처 실험

**다음 단계**: [03. 모델 학습](03-model-training.md)
