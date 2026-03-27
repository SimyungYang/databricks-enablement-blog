# 05. 챌린저 검증 (Challenger Validation)

**목적**: 새 모델을 운영에 배포하기 전 체계적인 4단계 검증을 수행합니다.

**주요 개념**:
- Check 1: 모델 문서화 확인
- Check 2: 운영 데이터 추론 테스트
- Check 3: Champion 대비 성능 비교
- Check 4: 비즈니스 KPI 평가 (비용 분석)

**핵심 코드 — 비즈니스 가치 평가**:

```python
COST_DOWNTIME = 50000       # 미탐지 고장 비용
SAVING_PREVENTED = 45000    # 예방 정비 절감 비용

tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
business_value = (
    tp * SAVING_PREVENTED - fp * COST_FALSE_ALARM
    - fn * COST_DOWNTIME - tp * COST_PREVENTIVE
)

# 모든 검증 통과 시 Champion 자동 승급
if all_passed:
    client.set_registered_model_alias(
        name=model_name, alias="Champion", version=model_version
    )
```

**사용 Databricks 기능**: `mlflow.evaluate()`, 모델 에일리어스 기반 배포, 태그 기반 검증 추적

{% hint style="info" %}
Champion/Challenger 패턴은 **코드 변경 없이** 모델을 교체할 수 있게 합니다. 추론 코드는 항상 `models:/{model_name}@Champion`을 참조하므로, Alias만 변경하면 운영 모델이 자동으로 전환됩니다.
{% endhint %}
