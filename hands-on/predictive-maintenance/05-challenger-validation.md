# 05. 챌린저 검증 (Challenger Validation)

> ** 전체 노트북 코드**: [05_challenger_validation.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/05_challenger_validation.py)


** 목적**: 새 모델을 운영에 배포하기 전 4단계 체계적 검증을 수행하고, 통과 시 Champion으로 자동 승급합니다.

** 사용 Databricks 기능**: `mlflow.evaluate()`, `모델 에일리어스 기반 배포`, `태그 기반 검증 추적`

---

## 왜 모델 검증이 필요한가?

새로운 AI 모델을 운영 환경에 배포하기 전에, 반드시 ** 체계적인 검증** 을 거쳐야 합니다. 이것은 제조 현장의 ** 품질 검사(QC)** 와 완전히 동일한 개념입니다.

### Champion-Challenger 패턴이란?

MLOps에서 널리 사용되는 모델 배포 전략입니다.

- **Champion (챔피언)**: 현재 운영 중인 모델. 검증을 통과해서 "현역"으로 일하고 있는 모델입니다.
- **Challenger (챌린저)**: 새로 학습된 모델. Champion의 자리를 "도전"하는 후보 모델입니다.
- Challenger가 모든 검증을 통과하면 Champion으로 ** 승급** 되어 운영에 투입됩니다.

## 검증 프로세스 개요

이 노트북은 새 모델(Challenger)을 운영에 배포하기 전 **4단계 검증** 을 자동으로 수행합니다. 제조 현장의 ** 게이트 검사(Gate Review)** 와 같은 구조입니다 -- 각 단계(Gate)를 통과해야 다음으로 진행할 수 있습니다.

## 검증 체크리스트

| Check | 항목 | 통과 기준 | 제조 비유 |
|-------|------|-----------|-----------|
| **Check 1**| 모델 문서화 확인 | 모델 설명이 20자 이상 작성되어야 함 | 제품 사양서가 작성되어 있는지 확인 |
| **Check 2**| 운영 데이터 추론 테스트 | 에러 없이 예측이 정상 수행되어야 함 | 시제품이 실제 라인에서 문제없이 조립되는지 확인 |
| **Check 3**| Champion 대비 성능 비교 | Challenger F1 >= Champion F1 | 새 공정이 기존 공정보다 수율이 높은지 비교 |
| **Check 4**| 비즈니스 KPI 평가 | 예상 순 비즈니스 가치 > 0 | 새 공정 도입 시 총 비용 대비 이익이 양수인지 확인 |

** 핵심 원칙: 4가지 검증을 모두 통과해야만 Champion으로 승급됩니다.** 하나라도 실패하면 Challenger는 "rejected(거부)" 태그가 붙고, 기존 Champion이 계속 운영됩니다.

## Check 1: 모델 문서화 확인

6개월 후에 "이 모델은 어떤 데이터로 학습했지?", "어떤 알고리즘을 썼지?"라는 질문에 답할 수 없다면, 모델을 유지보수하거나 개선하는 것이 불가능해집니다. 문서화는 ISO 품질 인증에서도 필수입니다.

## Check 2: 운영 데이터 추론 테스트

모델이 학습 환경에서는 잘 작동하더라도, 운영 환경의 데이터에서는 에러가 발생할 수 있습니다. 추론 테스트에서 가장 흔하게 발생하는 문제 3가지는 (1) 학습 때 없던 NULL 값, (2) 피처 순서 불일치, (3) 데이터 타입 변경입니다.

이 검증에서는 예측값의 품질도 함께 확인합니다 -- NULL 예측값, 범위 이탈(0~1 밖), 모든 예측값이 동일한 경우를 모두 검증합니다.

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

## Check 3: Champion 대비 성능 비교

Challenger의 F1 Score가 Champion의 F1 Score보다 ** 같거나 높으면** 통과합니다. Champion이 아직 없는 경우(첫 번째 모델)는 자동으로 통과 처리됩니다.

{% hint style="info" %}
전체 성능만 보면 안 됩니다. 제품 유형(L/M/H)별, 교대 시간대별, 특정 설비별로 성능을 슬라이스해서 봐야 합니다. 전체 F1이 0.9여도 특정 제품 유형에서 F1이 0.3이면, 그 유형의 설비는 사실상 보호받지 못하고 있는 것입니다. 이것을 **Slice-based Evaluation** 이라고 하며, Responsible AI의 핵심 요소입니다.
{% endhint %}

## Check 4: 비즈니스 가치 평가

순수 ML 메트릭만으로 모델을 평가하면 현업에서 외면받습니다. "정확도 92%입니다"는 경영진에게 아무 의미가 없습니다. "이 모델을 배포하면 연간 예방정비 비용 3억을 절감하면서 돌발 고장은 70% 줄일 수 있습니다"라고 해야 합니다.

### 혼동행렬과 비즈니스 비용 매핑

- **FN (미탐지) = 가장 비싼 실수**: 설비가 고장 나는데 모델이 "정상"이라고 판단 → 갑작스러운 라인 중단, 납기 지연
- **FP (오탐) = 낭비 비용**: 정상 설비인데 모델이 "고장 예측" → 불필요한 정비 인력 투입
- **TP (정탐) = 가장 큰 가치**: 고장을 사전에 감지 → 계획된 정비로 대처, 다운타임 최소화

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
비즈니스 KPI 평가에서 **False Negative(미탐지 고장)** 의 비용이 **False Positive(오탐)** 보다 훨씬 높습니다. 이는 Recall을 우선시하는 이유이기도 합니다.
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
Champion/Challenger 패턴은 ** 코드 변경 없이** 모델을 교체할 수 있게 합니다. 추론 코드는 항상 `models:/{model_name}@Champion`을 참조하므로, Alias만 변경하면 운영 모델이 자동으로 전환됩니다.
{% endhint %}

---

## 요약

### 이 노트북에서 수행한 작업

| 단계 | 검증 내용 | 의미 |
|------|-----------|------|
| **Check 1**| 모델 문서화 확인 | 모델의 추적 가능성 보장 |
| **Check 2**| 운영 데이터 추론 테스트 | 실제 환경에서의 안정성 확인 |
| **Check 3**| Champion-Challenger 성능 비교 | ML 성능 기준 통과 확인 |
| **Check 4**| 비즈니스 KPI 평가 | 제조 현장 비용 관점의 가치 검증 |
| ** 최종**| Champion 자동 승급/거부 | 안전한 모델 배포 보장 |

### 핵심 포인트

- **ML 성능(F1 Score)과 비즈니스 가치(비용 분석)를 모두 평가** 합니다. 둘 다 통과해야 승급됩니다.
- 모든 검증 결과는 **Unity Catalog 태그로 기록** 되어 감사 추적(Audit Trail)이 가능합니다.
- Lakeflow Jobs와 연동하면 ** 모델 학습 → 검증 → 승급** 이 완전 자동화됩니다.
- 검증 실패 시 기존 Champion이 유지되므로, 운영 서비스에 영향이 없습니다 ( ** 무중단 배포**).

** 다음 단계**: [06. 배치 추론](06-batch-inference.md)
