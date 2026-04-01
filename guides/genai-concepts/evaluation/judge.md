# Human vs LLM-as-Judge

## Human Evaluation vs LLM-as-Judge 비교

| 항목 | Human Evaluation | LLM-as-Judge |
|------|-----------------|--------------|
| **비용** | 높음 (평가자 인건비) | 낮음 (API 호출 비용) |
| ** 속도** | 느림 (시간~일 단위) | 빠름 (초~분 단위) |
| ** 확장성** | 제한적 (수백 건) | 높음 (수만 건 가능) |
| ** 일관성** | 평가자 간 편차 있음 | 동일 기준으로 일관 평가 |
| ** 뉘앙스 파악** | 우수 (문화적 맥락 이해) | 제한적 (미묘한 뉘앙스 놓칠 수 있음) |
| ** 도메인 전문성** | 전문가 투입 시 높음 | 일반적 기준만 평가 가능 |
| ** 적합 시기** | 최종 검증, 엣지 케이스 | 일상적 모니터링, 대량 평가 |

{% hint style="success" %}
** 권장 조합**: LLM-as-Judge로 대량 자동 평가 → 낮은 점수의 응답만 Human Evaluation으로 정밀 검토. 이 조합이 비용 대비 가장 효과적입니다.
{% endhint %}

---

## LLM-as-Judge 패턴

사람 대신 ** 다른 LLM을 평가자로 활용**하는 패턴입니다. 대량 평가를 자동화할 수 있어 실무에서 가장 많이 사용됩니다.

### 동작 원리

| 단계 | 설명 |
|------|------|
| 1. 평가 기준 정의 | "1~5점 척도로 관련성을 평가하세요" |
| 2. 평가 프롬프트 작성 | 질문, 응답, 컨텍스트를 Judge 모델에 전달 |
| 3. Judge 모델 실행 | GPT-4, Claude 등 강력한 모델이 점수와 이유 생성 |
| 4. 결과 집계 | 메트릭별 평균 점수, 분포 분석 |

{% hint style="info" %}
** 팁**: Judge 모델은 평가 대상 모델보다 ** 같거나 더 강력한 모델**을 사용하세요. 약한 모델이 강한 모델을 평가하면 신뢰도가 낮습니다.
{% endhint %}

### LLM-as-Judge의 한계

- Judge 모델 자체의 편향이 평가에 영향
- 위치 편향(Position Bias): 먼저 제시된 응답에 높은 점수 경향
- 장문 편향: 긴 응답에 높은 점수를 주는 경향
- 해결책: 여러 Judge를 사용하거나, 인간 평가와 병행

---

## Databricks MLflow Evaluate

MLflow Evaluate는 Databricks에서 제공하는 LLM 평가 통합 도구입니다.

| 기능 | 설명 |
|------|------|
| 내장 메트릭 | Faithfulness, Relevance, Toxicity 등 사전 정의 |
| 커스텀 메트릭 | 비즈니스 요구에 맞는 평가 기준 추가 |
| LLM-as-Judge | GPT-4 등을 Judge로 자동 평가 |
| 비교 평가 | 여러 모델/프롬프트 버전 간 성능 비교 |
| 시각화 | MLflow UI에서 결과 대시보드 확인 |

### 기본 사용 예시

```python
import mlflow
import pandas as pd

# 1. 평가 데이터셋 준비
eval_data = pd.DataFrame({
    "inputs": [
        {"messages": [{"role": "user", "content": "Delta Lake란?"}]},
        {"messages": [{"role": "user", "content": "Unity Catalog의 장점은?"}]},
    ],
    "expected_response": [
        "Delta Lake는 데이터 레이크에 ACID 트랜잭션을 제공하는 오픈소스 스토리지 레이어입니다.",
        "Unity Catalog는 통합 거버넌스, 데이터 검색, 접근 제어를 제공합니다.",
    ],
})

# 2. Agent 평가 실행
results = mlflow.evaluate(
    model=my_agent,                    # 평가할 Agent
    data=eval_data,                    # 평가 데이터셋
    model_type="databricks-agent",     # Agent 타입 지정
)

# 3. 전체 메트릭 확인
print(results.metrics)
# {
#   'faithfulness/v1/mean': 0.85,
#   'relevance/v1/mean': 0.92,
#   'groundedness/v1/mean': 0.88,
#   'safety/v1/mean': 0.99,
# }

# 4. 개별 응답별 상세 결과 확인
display(results.tables["eval_results"])
```

### 커스텀 메트릭 추가 예시

```python
from mlflow.metrics import make_metric

# "한국어 응답 여부"를 평가하는 커스텀 메트릭
def is_korean(predictions, targets, metrics):
    import re
    scores = []
    for pred in predictions:
        has_korean = bool(re.search('[가-힣]', pred))
        scores.append(1.0 if has_korean else 0.0)
    return scores

korean_metric = make_metric(
    eval_fn=is_korean,
    name="korean_response",
    greater_is_better=True,
)
```

---

## 최신 API: MLflow 3 Scorer 패턴

MLflow 3에서는 `Scorer` API를 통해 더 직관적으로 평가를 구성할 수 있습니다. 내장 scorer와 커스텀 scorer를 조합하여 사용합니다.

```python
from mlflow.genai.scorers import Guidelines, RetrievalGroundedness, Safety

# Built-in scorer 사용
results = mlflow.genai.evaluate(
    data=eval_data,
    predict_fn=my_agent.predict,
    scorers=[
        Guidelines(name="korean_response", guidelines="응답은 반드시 한국어로 작성되어야 합니다"),
        RetrievalGroundedness(),
        Safety(),
    ],
)

# Custom scorer 정의 (@scorer 데코레이터)
from mlflow.genai.scorers import scorer

@scorer
def format_checker(inputs, outputs, expectations):
    """응답이 JSON 형식인지 확인합니다."""
    import json
    try:
        json.loads(outputs["content"])
        return {"score": 1.0, "justification": "Valid JSON"}
    except:
        return {"score": 0.0, "justification": "Invalid JSON format"}
```

{% hint style="info" %}
**MLflow 3 변경사항**: 기존 `mlflow.evaluate()`의 `model_type="databricks-agent"` 방식은 계속 사용 가능하지만, 새 프로젝트에서는 `mlflow.genai.evaluate()` + Scorer 패턴을 권장합니다. `@scorer` 데코레이터로 비즈니스 로직에 맞는 평가 기준을 자유롭게 정의할 수 있습니다.
{% endhint %}
