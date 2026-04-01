# 05. 챌린저 검증 (Challenger Validation)

> **전체 노트북 코드**: [05_challenger_validation.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/05_challenger_validation.py)


**목적**: 새 모델을 운영에 배포하기 전 4단계 체계적 검증을 수행하고, 통과 시 Champion으로 자동 승급합니다.

**사용 Databricks 기능**: `mlflow.evaluate()`, `모델 에일리어스 기반 배포`, `태그 기반 검증 추적`

---

## 검증 체크리스트

| Check | 항목 | 기준 |
|-------|------|------|
| 1 | 모델 문서화 | 설명 20자 이상 |
| 2 | 운영 데이터 추론 테스트 | Spark UDF로 정상 예측 |
| 3 | Champion 대비 성능 비교 | F1 Score >= Champion |
| 4 | 비즈니스 KPI 평가 | 순 비즈니스 가치 > 0 |

## Check 2: 운영 데이터 추론 테스트

모델을 PySpark UDF로 로드하여 운영 환경 데이터에서 정상 예측이 되는지 확인합니다.

```python
# 모델을 Spark UDF로 로드하여 추론 수행
model_udf = mlflow.pyfunc.spark_udf(
    spark,
    model_uri=f"models:/{model_name}@Challenger",
    result_type="double"
)
preds_df = test_df.withColumn("prediction", model_udf(*feature_columns))
inference_passed = preds_df.count() > 0
```

## Check 4: 비즈니스 가치 평가

제조 현장의 비용 구조를 반영하여 모델의 실질적 가치를 금액으로 산출합니다.

```python
# 제조 현장 비용 파라미터
COST_DOWNTIME = 50000       # 미탐지 고장 → 다운타임 비용 (원)
COST_FALSE_ALARM = 3000     # 오탐 → 불필요 정비 비용 (원)
SAVING_PREVENTED = 45000    # 예방 정비 → 절감 비용 (원)
COST_PREVENTIVE = 5000      # 정비 수행 비용 (원)

tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
business_value = (
    tp * SAVING_PREVENTED     # 예방 성공
    - fp * COST_FALSE_ALARM   # 오탐 비용
    - fn * COST_DOWNTIME      # 미탐지 비용
    - tp * COST_PREVENTIVE    # 정비 비용
)
```

{% hint style="warning" %}
비즈니스 KPI 평가에서 **False Negative(미탐지 고장)**의 비용이 **False Positive(오탐)** 보다 훨씬 높습니다. 이는 Recall을 우선시하는 이유이기도 합니다.
{% endhint %}

## 종합 검증 및 Champion 승급

모든 검증을 통과하면 Challenger를 Champion으로 자동 승급합니다.

```python
all_passed = all([has_description, inference_passed, metric_passed, business_kpi_passed])

if all_passed:
    client.set_registered_model_alias(
        name=model_name, alias="Champion", version=model_version
    )
    client.set_model_version_tag(
        name=model_name, version=str(model_version),
        key="validation_status", value="approved"
    )
    print(f"모델 v{model_version} → Champion 승급!")
else:
    client.set_model_version_tag(
        name=model_name, version=str(model_version),
        key="validation_status", value="rejected"
    )
```

{% hint style="info" %}
Champion/Challenger 패턴은 **코드 변경 없이** 모델을 교체할 수 있게 합니다. 추론 코드는 항상 `models:/{model_name}@Champion`을 참조하므로, Alias만 변경하면 운영 모델이 자동으로 전환됩니다.
{% endhint %}

**다음 단계**: [06. 배치 추론](06-batch-inference.md)
