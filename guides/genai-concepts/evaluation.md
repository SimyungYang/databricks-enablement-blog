# GenAI 평가 방법론

GenAI 시스템의 품질을 측정하고 개선하는 것은 프로덕션 배포의 필수 과정입니다. 전통적인 ML과 달리 LLM 평가는 정답이 명확하지 않아 체계적인 접근이 필요합니다.

{% hint style="info" %}
**학습 목표**
- GenAI 평가가 전통 ML 평가와 근본적으로 다른 이유를 설명할 수 있다
- Faithfulness, Relevance, Groundedness 등 핵심 메트릭을 구체적 예시로 구분할 수 있다
- Human Evaluation과 LLM-as-Judge의 장단점을 비교하여 적합한 방법을 선택할 수 있다
- MLflow Evaluate를 사용하여 Agent를 평가하는 코드를 작성할 수 있다
- Review App을 활용한 피드백 수집 → 개선 워크플로우를 설계할 수 있다
{% endhint %}

---

## 왜 GenAI 평가가 특별히 어려운가?

전통 ML과 GenAI는 평가 패러다임이 근본적으로 다릅니다.

| 항목 | 전통 ML | GenAI/LLM |
|------|---------|-----------|
| 정답 | 레이블이 명확 (스팸/정상) | "좋은 답변"의 기준이 주관적 |
| 메트릭 | Accuracy, F1, AUC 등 정량적 | 유창성, 관련성, 안전성 등 정성적 |
| 출력 형태 | 수치/범주 (0 or 1, 3.14) | 자유 형식 텍스트 (무한한 가능성) |
| 재현성 | 동일 입력 = 동일 출력 | 동일 질문에 다른 응답 가능 (Temperature > 0) |
| 평가 비용 | 자동화 용이, 저비용 | 인간 평가 필요, 고비용 |

{% hint style="warning" %}
**핵심 문제**: "서울의 맛집을 추천해주세요"라는 질문에 정답이 하나가 아닙니다. "강남역 근처 이탈리안 레스토랑"도, "을지로 골목 칼국수집"도 좋은 답변이 될 수 있습니다. 이런 환경에서 어떻게 "품질"을 측정할 것인가가 GenAI 평가의 핵심 과제입니다.
{% endhint %}

{% hint style="danger" %}
"잘 동작하는 것 같다"라는 주관적 판단만으로 프로덕션에 배포하면, 환각(Hallucination)이나 유해 응답 문제가 발생할 수 있습니다. 반드시 체계적으로 평가하세요.
{% endhint %}

---

## 핵심 평가 메트릭 — 구체적 예시와 함께

### 정확성 메트릭

#### Faithfulness (충실도)

**"응답이 제공된 컨텍스트에 근거하는가?"** — RAG 시스템에서 가장 중요한 메트릭입니다.

| 상황 | 컨텍스트 (검색된 문서) | 모델 응답 | 판정 |
|------|----------------------|-----------|------|
| 성공 | "2024년 매출은 100억원" | "2024년 매출은 100억원입니다" | Faithful |
| 실패 | "2024년 매출은 100억원" | "2024년 매출은 **200억원**입니다" | Not Faithful (수치 왜곡) |
| 실패 | "2024년 매출은 100억원" | "2024년 매출은 100억원이며 **전년 대비 20% 성장**했습니다" | Not Faithful (근거 없는 추가 정보) |

#### Relevance (관련성)

**"응답이 질문에 적절히 답하는가?"**

| 질문 | 모델 응답 | 판정 |
|------|-----------|------|
| "제품 가격이 얼마인가요?" | "Pro Plan은 월 $49, Enterprise는 월 $199입니다" | Relevant |
| "제품 가격이 얼마인가요?" | "우리 회사는 2015년에 설립되었습니다" | Not Relevant (질문과 무관) |
| "제품 가격이 얼마인가요?" | "Pro Plan은 강력한 기능을 제공합니다" | Partially Relevant (가격 미포함) |

#### Groundedness (근거성)

**"출처에 기반한 응답인가?"** — Faithfulness와 유사하지만, 검색된 문서의 어느 부분에서 근거를 찾을 수 있는지까지 추적합니다.

#### Correctness (정확성)

**"응답이 사실적으로 정확한가?"** — 정답 레이블이 있을 때 사용합니다.

### 안전성 메트릭

| 메트릭 | 설명 | 실패 예시 |
|--------|------|-----------|
| **Toxicity** (유해성) | 욕설, 혐오, 차별 표현 | "그런 질문은 바보나 하는 거죠" |
| **Bias** (편향) | 성별, 인종, 국적 등에 대한 편향 | "여성은 리더십에 적합하지 않습니다" |
| **PII Leakage** | 개인정보 노출 | "김철수님의 전화번호는 010-1234-5678입니다" |

### 운영 메트릭

| 메트릭 | 설명 | 목표 |
|--------|------|------|
| **Latency** (지연시간) | 응답 생성까지 소요 시간 | < 3초 (대화형), < 30초 (분석형) |
| **Cost** (비용) | 토큰당 비용 | 사용 사례별 예산 내 |
| **Throughput** (처리량) | 초당 처리 요청 수 | 동시 사용자 기준 |
| **Token Efficiency** | 답변 대비 사용 토큰 수 | 불필요한 장문 응답 감지 |

---

## Human Evaluation vs LLM-as-Judge 비교

| 항목 | Human Evaluation | LLM-as-Judge |
|------|-----------------|--------------|
| **비용** | 높음 (평가자 인건비) | 낮음 (API 호출 비용) |
| **속도** | 느림 (시간~일 단위) | 빠름 (초~분 단위) |
| **확장성** | 제한적 (수백 건) | 높음 (수만 건 가능) |
| **일관성** | 평가자 간 편차 있음 | 동일 기준으로 일관 평가 |
| **뉘앙스 파악** | 우수 (문화적 맥락 이해) | 제한적 (미묘한 뉘앙스 놓칠 수 있음) |
| **도메인 전문성** | 전문가 투입 시 높음 | 일반적 기준만 평가 가능 |
| **적합 시기** | 최종 검증, 엣지 케이스 | 일상적 모니터링, 대량 평가 |

{% hint style="success" %}
**권장 조합**: LLM-as-Judge로 대량 자동 평가 → 낮은 점수의 응답만 Human Evaluation으로 정밀 검토. 이 조합이 비용 대비 가장 효과적입니다.
{% endhint %}

---

## LLM-as-Judge 패턴

사람 대신 **다른 LLM을 평가자로 활용**하는 패턴입니다. 대량 평가를 자동화할 수 있어 실무에서 가장 많이 사용됩니다.

### 동작 원리

| 단계 | 설명 |
|------|------|
| 1. 평가 기준 정의 | "1~5점 척도로 관련성을 평가하세요" |
| 2. 평가 프롬프트 작성 | 질문, 응답, 컨텍스트를 Judge 모델에 전달 |
| 3. Judge 모델 실행 | GPT-4, Claude 등 강력한 모델이 점수와 이유 생성 |
| 4. 결과 집계 | 메트릭별 평균 점수, 분포 분석 |

{% hint style="info" %}
**팁**: Judge 모델은 평가 대상 모델보다 **같거나 더 강력한 모델**을 사용하세요. 약한 모델이 강한 모델을 평가하면 신뢰도가 낮습니다.
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

## Human-in-the-Loop: Review App 워크플로우

자동 평가만으로는 한계가 있으므로, **인간 피드백**을 체계적으로 수집하는 것이 중요합니다.

### Review App 기능

| 기능 | 설명 |
|------|------|
| 웹 UI | 비기술 인력도 쉽게 피드백 제공 |
| 엄지 척 평가 | 좋음/나쁨 간단 피드백 |
| 상세 피드백 | 텍스트 코멘트, 올바른 답변 제공 |
| 데이터 수집 | 피드백이 Inference Table에 자동 저장 |
| 평가셋 구축 | 수집된 피드백을 평가 데이터셋으로 활용 |

### 전체 개선 워크플로우 (5단계)

| 단계 | 활동 | Databricks 도구 |
|------|------|-----------------|
| **1. 배포** | Agent를 Model Serving으로 배포 | Model Serving |
| **2. 사용자 테스트** | Review App에서 SME(Subject Matter Expert)가 테스트 | Review App |
| **3. 피드백 수집** | 좋음/나쁨 + 코멘트를 Inference Table에 저장 | Inference Tables |
| **4. 분석 및 개선** | 낮은 평가 응답 분석 → 프롬프트 수정 또는 검색 개선 | MLflow Evaluate |
| **5. 재배포** | 개선된 Agent를 재배포하고 다시 평가 | Model Serving |

{% hint style="info" %}
**핵심**: 이 워크플로우는 **일회성이 아닌 지속적 반복**입니다. 프로덕션 운영 중에도 Inference Table에서 실제 사용자 상호작용을 모니터링하고, 품질이 저하되면 즉시 개선 사이클을 시작하세요.
{% endhint %}

---

## 흔한 오해 (Common Misconceptions)

| 오해 | 사실 |
|------|------|
| "BLEU/ROUGE 점수가 높으면 좋은 답변이다" | 이 메트릭들은 단어 겹침만 측정합니다. 의미적으로 동일하지만 다른 표현을 사용하면 낮게 나옵니다. LLM-as-Judge가 더 적합합니다. |
| "평가 데이터셋은 한 번 만들면 된다" | 사용 패턴이 변하면 평가셋도 업데이트해야 합니다. Review App 피드백을 평가셋에 지속 추가하세요. |
| "LLM-as-Judge는 항상 정확하다" | Judge 모델도 편향이 있습니다. 중요한 평가에서는 Human Evaluation과 병행하세요. |
| "모든 메트릭을 다 측정해야 한다" | 사용 사례에 맞는 핵심 메트릭 3~5개에 집중하세요. RAG라면 Faithfulness와 Relevance가 최우선입니다. |

---

## 연습 문제

1. 사내 HR 규정 Q&A 챗봇에서 가장 중요한 평가 메트릭 3가지를 선택하고, 그 이유를 설명하세요.
2. 다음 응답이 Faithful한지 판단하세요: 컨텍스트 "연차는 입사 1년 후 15일 부여", 응답 "연차는 입사 1년 후 15일이 부여되며, 매년 1일씩 추가됩니다."
3. LLM-as-Judge의 "장문 편향"을 완화하기 위한 구체적 방법을 2가지 제안하세요.
4. Review App에서 수집한 "나쁨" 피드백을 어떻게 Agent 개선에 활용할 수 있는지 단계별로 설명하세요.

---

## 참고 자료

- [Databricks MLflow Evaluate 문서](https://docs.databricks.com/en/mlflow/llm-evaluate.html)
- [Databricks Review App 문서](https://docs.databricks.com/en/generative-ai/agent-evaluation/review-app.html)
- [Zheng et al., "Judging LLM-as-a-Judge" (2023)](https://arxiv.org/abs/2306.05685)
- [RAGAS: Evaluation Framework for RAG](https://docs.ragas.io/)
- [Databricks Agent Evaluation 가이드](https://docs.databricks.com/en/generative-ai/agent-evaluation/index.html)
