# 06. 배치 추론 (Batch Inference)

> ** 전체 노트북 코드**: [06_batch_inference.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/06_batch_inference.py)


** 목적**: Champion 모델을 PySpark UDF로 변환하여 클러스터 전체에서 분산 추론하고, 위험 등급을 자동 부여합니다.

** 사용 Databricks 기능**: `PySpark UDF 분산 추론`, `Delta Lake ACID 트랜잭션`, `Workflows 연동`

---

## 이 노트북은 무엇을 하는가?

지금까지 모델을 학습하고(04), 검증하여 Champion으로 승급시켰습니다(05). ** 이제 모델이 실제로 일을 시작할 차례입니다.**

** 배치 추론(Batch Inference)** 이란, 쌓여 있는 데이터를 한꺼번에 모델에 넣어서 예측 결과를 얻는 방식입니다. "배치(Batch)"는 "묶음"이라는 뜻으로, 데이터를 하나씩 처리하는 것이 아니라 ** 대량의 데이터를 한 번에 처리** 합니다.

### 실시간 추론 vs 배치 추론

다음 표는 실시간 추론과 배치 추론의 차이를 정리한 것입니다.

| 구분 | 실시간 추론 (Real-time) | 배치 추론 (Batch) |
|------|------------------------|-------------------|
| ** 처리 방식**| 요청 1건마다 즉시 응답 | 대량 데이터를 한꺼번에 처리 |
| ** 응답 시간**| 밀리초 단위 | 분~시간 단위 |
| ** 적합한 상황**| 웹 서비스, 챗봇 | 정기 보고, 대량 예측 |
| ** 예지보전 활용**| 센서 이상 즉시 알림 | 6시간마다 전체 설비 점검 |

예지보전에서는 ** 배치 추론이 더 적합** 합니다. 설비 고장은 수초 내에 급변하는 것이 아니라 서서히 진행되므로, 6시간 간격으로 전체 설비를 점검하는 것이 효율적입니다.

{% hint style="info" %}
배치 추론의 핵심은 "얼마나 빠르게 대량 예측을 하느냐"입니다. Spark UDF의 진짜 위력은 단일 모델을 클러스터 전체 노드에서 동시에 실행한다는 것입니다. 10만 대 설비를 예측하는 데 단일 서버로 10분 걸리던 것이 10노드 클러스터에서 1분으로 줄어듭니다.
{% endhint %}

## Databricks 핵심 기능

다음은 이 노트북에서 활용하는 Databricks 핵심 기능입니다.

| 기능 | 설명 | 장점 |
|------|------|------|
| **PySpark UDF**| 모델을 Spark 함수로 변환하여 클러스터 전체에 분산 추론 | 1만 건이든 100만 건이든 자동으로 병렬 처리 |
| ** 에일리어스 기반 배포**| `@Champion` 이름으로 모델 참조 | 05번에서 새 Champion이 되면 이 코드 변경 없이 자동 적용 |
| **Delta Lake**| 예측 결과를 ACID 트랜잭션으로 안전하게 저장 | 저장 중 장애가 발생해도 데이터 손상 없음 |
| **Workflows**| 일 4회 자동 실행 스케줄링 | 사람 개입 없이 24/7 운영 |

---

## 운영 스펙

| 항목 | 설정 |
|------|------|
| 실행 주기 | 일 4회 (6시간 간격 - 06:00, 12:00, 18:00, 24:00) |
| 입력 | 설비 센서 데이터 테이블 (`lgit_pm_training`) |
| 출력 | 고장 확률 + 위험 등급(CRITICAL/HIGH/MEDIUM/LOW) + 타임스탬프 |
| 저장 | Delta Lake 테이블에 Append 모드로 이력 누적 |

## 1. Champion 모델을 PySpark UDF로 로드

### PySpark UDF란?

**UDF (User Defined Function)** 는 사용자가 직접 정의한 함수입니다. **PySpark UDF** 는 이 함수를 Spark 클러스터의 모든 노드(컴퓨터)에서 동시에 실행할 수 있게 만든 것입니다. 품질 검사원이 한 명이라면 1,000개 제품을 검사하는 데 1,000분이 걸리지만, 검사원 100명이 동시에 검사하면 10분이면 끝납니다. PySpark UDF는 이 "검사원 100명"을 자동으로 배치해주는 기능입니다.

`@Champion` 에일리어스를 참조하므로 모델 버전이 바뀌어도 코드 수정이 필요 없습니다.

```python
champion_udf = mlflow.pyfunc.spark_udf(
    spark,
    model_uri=f"models:/{model_name}@Champion",
    result_type="double"
)
```

{% hint style="warning" %}
Spark UDF로 모델을 분산 실행하면, 각 노드에 모델이 복제됩니다. 모델 크기가 큰 경우(예: 딥러닝 모델 2GB 이상) 메모리 문제가 발생할 수 있습니다. XGBoost 같은 트리 모델은 보통 수 MB~수십 MB 수준이라 전혀 문제없지만, 비전 모델을 Spark UDF로 돌리려면 메모리 계획을 세워야 합니다. 이런 경우에는 Model Serving endpoint를 사용하는 것이 더 적합합니다.
{% endhint %}

## 2. 추론 데이터 준비

** 실제 운영 환경** 에서는 센서 데이터가 IoT 게이트웨이를 통해 실시간으로 Delta Lake에 유입됩니다. 이 교육에서는 학습 데이터에서 ** 정답 레이블(machine_failure)** 을 제거한 데이터를 추론 입력으로 사용합니다.

`current_timestamp()`로 추론 시각을 기록하는 이유는, 나중에 "언제 예측한 결과인지"를 추적하기 위해서입니다. 하루 4회 실행되므로 어느 회차(06시/12시/18시/24시)의 예측인지 구분이 필요합니다.

```python
inference_df = (
    spark.table("lgit_pm_training")
    .select("udi", *feature_columns)
    .withColumn("inference_timestamp", F.current_timestamp())
)
```

## 3. 분산 배치 예측 + 위험 등급 부여

Champion 모델을 **PySpark UDF** 로 호출하여 전체 데이터에 대한 예측을 수행합니다. Spark가 자동으로 클러스터의 모든 노드에 작업을 분산합니다.

### 추론 결과에 포함되는 정보

| 컬럼 | 설명 | 예시 |
|------|------|------|
| `failure_probability` | 고장 확률 (0.0 ~ 1.0) | 0.82 = 82% 확률로 고장 예상 |
| `predicted_failure` | 이진 판정 (0 또는 1) | 확률 > 0.5이면 1(고장) |
| `risk_level` | 위험 등급 (4단계) | CRITICAL / HIGH / MEDIUM / LOW |
| `model_version` | 예측에 사용된 모델 버전 | 나중에 모델별 성능 비교 가능 |

### 위험 등급 분류 기준 및 현장 대응 방법

다음 표는 위험 등급별 의미와 현장 대응 방법을 정리한 것입니다.

| 등급 | 고장 확률 | 의미 | 현장 대응 |
|------|-----------|------|-----------|
| **CRITICAL**| > 80% | 고장이 임박한 상태 | ** 즉시 라인 정지하고 점검**. 해당 설비 비상 정비 투입 |
| **HIGH**| 50~80% | 고장 가능성이 높은 상태 | ** 현재 교대 근무 내 점검 필수**. 정비팀에 즉시 통보 |
| **MEDIUM**| 30~50% | 주의가 필요한 상태 | ** 다음 정기 점검 시 우선 확인**. 모니터링 강화 |
| **LOW**| < 30% | 정상 운영 상태 | ** 통상적인 모니터링 유지**. 추가 조치 불필요 |

{% hint style="warning" %}
위험 등급 임계값(0.3/0.5/0.8)은 교육용 예시입니다. 실무에서는 반드시 ** 현장 엔지니어와 함께** 결정해야 합니다. 처음에는 보수적으로(CRITICAL 기준을 낮게, 예: 0.7) 시작하고, 오탐이 많으면 점진적으로 기준을 올리는 것이 안전합니다. ** 현장의 신뢰를 한 번 잃으면 회복하는 데 6개월이 걸립니다.**
{% endhint %}

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

## 4. Delta Lake에 예측 결과 저장

### 왜 예측 결과를 저장해야 하는가?

예측 결과를 Delta Lake 테이블에 저장하면 다음과 같은 가치를 얻습니다.

1. ** 이력 추적 (Trending)**: "이 설비의 고장 확률이 지난 1주일 동안 어떻게 변했는가?" 분석 가능
2. ** 모델 모니터링**: 예측 분포가 시간이 지남에 따라 변하는지 확인 (08번 노트북에서 활용)
3. ** 정비 계획 수립**: 과거 예측 결과를 기반으로 설비별 정비 주기 최적화
4. ** 감사 추적 (Audit Trail)**: "언제, 어떤 모델이, 어떤 예측을 했는지" 완전한 기록 유지

Append 모드로 저장하여 시간별 예측 이력이 누적됩니다. ACID 트랜잭션이 보장됩니다.

```python
preds_df.write.mode("append").option("mergeSchema", "true") \
    .saveAsTable("lgit_pm_inference_results")
```

{% hint style="info" %}
append vs overwrite는 사소해 보이지만 운영에서 매우 중요한 결정입니다. append를 써야 예측 이력이 쌓이고, 시간이 지나면서 "모델이 점점 CRITICAL을 많이 예측하고 있다 → 드리프트 의심" 같은 분석이 가능합니다. ** 예측 이력은 한 번 잃으면 복구할 수 없습니다.** 디스크 비용은 싸지만, 3개월치 이력 데이터는 돈으로 살 수 없습니다.
{% endhint %}

### Databricks UI 확인 포인트

1. **Catalog > lgit_mlops_poc > Tables > lgit_pm_inference_results** 클릭
2. **Sample Data** 탭: 예측 결과 (failure_probability, risk_level, 고장 유형 확률) 확인
3. **Details** 탭: 행 수가 이전보다 증가했는지 확인 (append 모드이므로 누적)
4. **History** 탭: 각 배치 실행의 타임스탬프 확인
5. 우측 상단 **Create**> **Quick Dashboard**: 위험 등급 분포 시각화를 즉시 생성 가능

## 5. 예측 결과 분석

저장된 예측 결과를 **SQL** 로 분석합니다. Databricks에서는 Python과 SQL을 하나의 노트북에서 자유롭게 전환할 수 있습니다.

```sql
-- 위험 등급별 분포
SELECT
  risk_level,
  COUNT(*) as count,
  ROUND(AVG(failure_probability), 4) as avg_failure_prob,
  ROUND(MIN(failure_probability), 4) as min_prob,
  ROUND(MAX(failure_probability), 4) as max_prob
FROM lgit_pm_inference_results
GROUP BY risk_level
ORDER BY avg_failure_prob DESC
```

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
이 노트북은 Databricks Workflow에서 ** 일 4회** 자동 실행됩니다. `model_version` 컬럼이 함께 저장되므로, 모델 변경 전후의 예측 결과를 비교 분석할 수 있습니다.
{% endhint %}

---

## 6. 고장 유형별 확률 추정 (Fault Type Probability)

> ** 전체 노트북 코드**: [06_batch_inference.py (고장 유형별 확률 추정 섹션)](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/06_batch_inference.py)

현재 모델은 이진 분류(고장/정상)만 수행합니다. 고장 유형별 확률은 학습 데이터의 고장 유형 분포를 기반으로 ** 사후 추정** 합니다.

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
이 방식은 사후 추정(post-hoc estimation)으로, 실제 운영에서는 고장 유형별 ** 멀티레이블 분류 모델** 을 별도로 학습하는 것을 권장합니다.
{% endhint %}

## 7. 우선순위 기반 유지보수 스케줄링

위험 설비 목록을 기반으로 ** 즉시 점검 일정** 을 수립합니다.

| 우선순위 | 조건 | 조치 | 타임라인 |
|----------|------|------|----------|
| **P0 (긴급)**| CRITICAL + tool_wear > 200분 | 즉시 라인 정지, 공구 교체 | 발견 즉시 |
| **P1 (높음)**| CRITICAL 등급 | 당일 내 점검 | 4시간 이내 |
| **P2 (보통)**| HIGH 등급 | 다음 교대 시 점검 | 8시간 이내 |
| **P3 (낮음)**| MEDIUM 등급 | 다음 정기 점검 시 확인 | 1주일 이내 |

### 자동 알림 설정 방법

이 목록을 정비팀에 자동으로 전달하는 방법입니다.

1. **Databricks SQL Alert**: CRITICAL 건수가 임계값을 초과하면 이메일/Slack 자동 알림
2. **Workflows 알림**: 배치 추론 Job 완료 시 결과 요약을 이메일로 발송
3. **SQL Dashboard**: 정비팀이 웹 브라우저에서 실시간으로 위험 설비 현황을 확인

## 8. 센서 해석 가이드

CRITICAL/HIGH 위험 설비가 감지되었을 때, 각 센서값의 의미와 점검 포인트입니다.

| 센서 | 의미 | 이상 징후 | 점검 포인트 |
|------|------|----------|------------|
| **`tool_wear_min`**| 공구 마모도 | 200분 이상이면 수명 임박 | 공구 교체 시점 판단 |
| **`torque_nm`**| 토크 | 비정상적으로 높음 | 설비 부하 과다 또는 윤활 문제 |
| **`rotational_speed_rpm`**| 회전속도 | 급격한 변동 | 베어링 이상 징후 |
| **`air_temperature_k`**| 공기 온도 | 급등 | 냉각 시스템 이상 |

{% hint style="warning" %}
예측 결과를 기존의 MES(Manufacturing Execution System)나 CMMS(Computerized Maintenance Management System)와 연동하면, 정비 작업 지시가 자동으로 생성되는 ** 완전 자동화된 예지보전 시스템** 을 구축할 수 있습니다.
{% endhint %}

---

## 9. Feature Store가 추론에서 빛나는 이유

> ** 전체 노트북 코드**: [06_batch_inference.py (Feature Store 섹션)](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/06_batch_inference.py)

Feature Store의 진짜 가치는 학습 시가 아니라 ** 추론 시** 나타납니다. 운영 6개월 후, 피처 계산 로직이 바뀌었는데 학습 때와 추론 때 ** 다른 버전의 피처** 가 사용되고 있다면, 모델 성능이 떨어지는데 원인을 찾을 수 없는 **Training-Serving Skew** 가 발생합니다.

### Feature Store 없이 vs 있을 때

| 상황 | Feature Store 없이 | Feature Store 있을 때 |
|------|-------------------|---------------------|
| 학습 시 피처 | `temp_diff = process_temp - air_temp` | Feature Table에서 자동 조회 |
| 추론 시 피처 | 같은 수식을 다시 코딩 (복사-붙여넣기) | ** 동일한 Feature Table** 에서 자동 조회 |
| 수식 변경 시 | 학습 코드/추론 코드 ** 둘 다** 수정 필요 | Feature Table ** 한 곳만** 수정 |
| 6개월 후 | "학습 때 어떤 수식이었지?" → 추적 불가 | **Lineage로 자동 추적**|
| 결과 | Training-Serving Skew → 성능 저하 | ** 일관성 자동 보장**|

### Feature Lookup 기반 추론 (참고 패턴)

Feature Store의 `score_batch` 기능을 사용하면, 추론 시 피처를 ** 자동으로 조인** 하는 패턴입니다. 현재 실습에서는 피처를 직접 계산하여 사용하지만, 운영 환경에서는 이 패턴을 권장합니다.

```python
from databricks.feature_engineering import FeatureEngineeringClient, FeatureLookup

fe = FeatureEngineeringClient()

lookups = [
    FeatureLookup(
        table_name="catalog.schema.lgit_pm_features",  # Feature Table
        feature_names=["temp_diff", "power_w", "strain", "risk_score"],
        lookup_key="udi"  # 조인 키 (설비 ID)
    )
]

# score_batch: 모델 + Feature Lookup을 한번에 실행
predictions = fe.score_batch(
    model_uri="models:/lgit_predictive_maintenance@Champion",
    df=new_sensor_data,  # 새로 들어온 센서 데이터 (udi만 있으면 됨!)
    feature_lookups=lookups
)
```

{% hint style="info" %}
`new_sensor_data`에는 `udi`(설비 ID)만 있으면 됩니다. `temp_diff`, `power_w` 등의 피처는 Feature Store가 ** 자동으로 조인** 합니다. 피처 계산 로직이 바뀌어도 ** 추론 코드를 수정할 필요 없음**-- Feature Table만 업데이트하면 됩니다.
{% endhint %}

## 10. 모델이 변경되어도 추론이 끊기지 않는 이유

에일리어스 + Feature Store의 진짜 위력은 ** 무중단 모델 교체** 에 있습니다.

### 시나리오: Champion v5 → v6 교체 시 추론 코드 변화

다음 표는 Champion 모델이 교체되는 과정에서 추론 코드가 한 번도 변경되지 않음을 보여줍니다.

| 시점 | Champion 에일리어스 | 가리키는 모델 | 추론 코드 수정? |
|------|------------------|------------|:---:|
| 3월 | @Champion | v5 (F1=0.87) | 없음 |
| 드리프트 감지 | -- | -- | 없음 |
| 자동 재학습 | -- | v6 학습 완료 | 없음 |
| 검증 통과 | @Champion → v6 | v6 (F1=0.91) | ** 없음!**|
| 4월 | @Champion | v6 (F1=0.91) | 없음 |

v5에서 v6으로 바뀌는 순간, 추론 코드는 한 줄도 바꾸지 않았지만 자동으로 v6 모델을 사용합니다. 이것이 DNS처럼 작동하는 에일리어스의 힘이고, MLOps Level 2 무중단 배포의 핵심입니다.

### 만약 v6에 문제가 생기면? (롤백)

```python
# 관리자가 한 줄 실행 — 즉시 v5로 롤백!
client.set_registered_model_alias("lgit_predictive_maintenance", "Champion", version=5)
# → 다음 추론부터 자동으로 v5 사용 (코드 수정 없음)
```

{% hint style="info" %}
이 구조 덕분에 "새 모델 배포"가 무서운 일이 아니게 됩니다. 잘못되면 30초 안에 롤백할 수 있으니까요. 이 안전장치가 없으면 팀은 모델 업데이트를 두려워하게 되고, 결국 6개월 된 낡은 모델로 운영하게 됩니다.
{% endhint %}

---

## 요약

### 이 노트북에서 수행한 작업

| 단계 | 수행 내용 | 사용된 Databricks 기능 |
|------|-----------|----------------------|
| **1**| Champion 모델을 PySpark UDF로 로드 | Unity Catalog 에일리어스, MLflow |
| **2**| 추론 데이터 준비 (센서 데이터 + 타임스탬프) | Delta Lake, PySpark |
| **3**| 전체 설비에 대한 배치 예측 수행 | PySpark UDF 분산 추론 |
| **4**| 예측 결과에 위험 등급 부여 | PySpark 조건문 |
| **5**| Delta Lake에 Append 모드로 이력 저장 | Delta Lake ACID 트랜잭션 |
| **6**| 위험 설비 목록 분석 및 정비 액션 아이템 도출 | SQL Analytics |

### 운영 이슈 3가지

배치 추론 파이프라인에서 가장 자주 발생하는 운영 이슈입니다.

1. ** 입력 테이블이 비어있는 경우**-- 업스트림 ETL이 실패하면 빈 테이블에 추론을 돌리게 됩니다. 반드시 입력 건수 체크 로직을 추가하세요.
2. ** 모델 버전 불일치**-- Champion 에일리어스가 실수로 삭제되면 에러가 납니다. 에일리어스 존재 여부를 먼저 확인하는 방어 코드가 필요합니다.
3. ** 디스크 용량 초과**-- append 모드로 수개월 쌓다 보면 테이블이 커집니다. 파티셔닝과 OPTIMIZE/VACUUM 전략을 미리 세워두세요.

** 다음 단계**: [07. 비정형 이상탐지](07-anomaly-detection.md)
