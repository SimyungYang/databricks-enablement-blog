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

### 검색(Retrieval) 메트릭 — RAG 시스템 전용

RAG 시스템을 평가할 때는 **"검색이 잘 되는가?"**와 **"생성이 잘 되는가?"**를 반드시 분리하여 측정해야 합니다. 검색 품질이 낮으면 아무리 좋은 LLM도 좋은 답변을 생성할 수 없습니다.

#### Precision@K (정밀도)

**상위 K개 검색 결과 중 실제 관련 문서의 비율**입니다. 검색된 5개 문서 중 3개가 관련 있다면 P@5 = 0.6입니다.

#### Recall@K (재현율)

**전체 관련 문서 중 상위 K개에 포함된 비율**입니다. 관련 문서가 총 10개인데 상위 5개에 5개가 포함되었다면 R@5 = 0.5입니다.

#### MRR (Mean Reciprocal Rank)

**첫 번째 관련 문서의 순위 역수 평균**입니다. 관련 문서가 3번째에 나오면 1/3, 1번째에 나오면 1/1입니다. 여러 질문에 대해 이 값을 평균합니다.

#### NDCG (Normalized Discounted Cumulative Gain)

**상위 결과일수록 높은 가중치를 부여하여 전체 순위 품질을 측정**합니다. 관련 문서가 위에 있을수록 NDCG가 높아집니다. 1에 가까울수록 이상적인 순위입니다.

| 메트릭 | 측정 대상 | 사용 시기 | 직관적 해석 |
|--------|----------|----------|------------|
| **Precision@K** | 검색 정확도 | "쓸모없는 결과가 너무 많은가?" | 높을수록 노이즈 적음 |
| **Recall@K** | 검색 완전성 | "빠뜨린 관련 문서가 있는가?" | 높을수록 누락 적음 |
| **MRR** | 첫 관련 결과 순위 | "관련 문서가 위에 나오는가?" | 높을수록 빠른 발견 |
| **NDCG** | 전체 순위 품질 | "전체적으로 순위가 적절한가?" | 1에 가까울수록 완벽 |

{% hint style="info" %}
**RAG 디버깅 팁**: RAG 시스템에서 Faithfulness 점수가 낮다면, 원인이 '검색'인지 '생성'인지를 먼저 구분하세요. Retrieval 메트릭이 낮으면 검색 개선(청킹 전략 변경, 임베딩 모델 교체)이 필요하고, Retrieval은 좋은데 생성이 나쁘면 프롬프트 수정이 필요합니다.
{% endhint %}

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

### 최신 API: MLflow 3 Scorer 패턴

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

## 평가 데이터셋 설계 가이드

"어떤 질문으로 테스트할 것인가"는 평가에서 가장 중요한 결정입니다. 아무리 좋은 메트릭과 도구를 사용하더라도, 평가 데이터셋이 실제 사용 패턴을 반영하지 못하면 의미 없는 결과를 얻게 됩니다.

### 커버리지 원칙

- **주요 사용 사례별 최소 10개 질문**을 포함하세요
- 비율 가이드: **정상 케이스 60%** + **엣지 케이스 30%** + **적대적 케이스 10%**

### 엣지 케이스 유형

| 유형 | 예시 | 왜 중요한가 |
|------|------|-----------|
| 모호한 질문 | "그거 얼마예요?" | 컨텍스트 부족 시 행동 확인 |
| 다국어 혼용 | "Delta Lake의 time travel 기능 알려줘" | 한영 혼용 처리 확인 |
| 도메인 밖 질문 | "오늘 날씨 어때?" (HR 챗봇에) | 범위 밖 질문 거절 능력 |
| 최신 정보 질문 | "이번 달 신제품은?" | 학습 데이터 이후 정보 처리 |
| 수치/계산 질문 | "지난 3분기 평균 매출은?" | 정확한 수치 계산 능력 |

### 데이터셋 크기 가이드

| 단계 | 권장 크기 | 목적 |
|------|----------|------|
| **PoC 단계** | 30~50개 | 기본 동작 확인, 주요 시나리오 커버 |
| **파일럿 단계** | 100~200개 | 엣지 케이스 포함, 메트릭 기반 비교 |
| **프로덕션 단계** | 500개 이상 | 포괄적 커버리지, 회귀 테스트 포함 |

### Ground Truth 작성 원칙

- **도메인 전문가(SME)가 작성**: 개발자가 아닌 실제 업무 전문가가 정답을 만들어야 합니다
- **단일 정답이 아닌 "허용 가능한 답변 범위" 정의**: "연차는 15일입니다"도, "입사 1년 후 15일의 연차가 부여됩니다"도 정답으로 인정
- **정답에 근거 문서 출처 포함**: 어떤 문서에서 답을 찾을 수 있는지 함께 기록

{% hint style="warning" %}
**평가셋은 살아있는 문서입니다**: 프로덕션 운영 중 Review App에서 수집된 실패 케이스를 지속적으로 평가셋에 추가하세요. 시간이 지날수록 평가셋의 품질이 높아지고, 회귀 테스트 역할을 합니다.
{% endhint %}

---

## Offline vs Online 평가

### Offline 평가 (배포 전)

고정된 평가 데이터셋으로 반복 테스트하는 방식입니다. **개발 중 빠른 피드백 루프**를 제공합니다.

| 특징 | 설명 |
|------|------|
| 데이터 | 고정 평가셋 (사전 준비) |
| 속도 | 빠름 (분 단위) |
| 실행 시기 | 프롬프트 변경, 모델 교체, 검색 설정 변경 시마다 |
| 도구 | MLflow Evaluate |
| 장점 | 빠른 실험, 재현 가능, 비용 낮음 |
| 한계 | 실제 사용 패턴을 완전히 반영하지 못함 |

### Online 평가 (배포 후)

실제 사용자 트래픽으로 평가하는 방식입니다. **프로덕션 환경에서의 실제 성능**을 측정합니다.

| 특징 | 설명 |
|------|------|
| 데이터 | 실제 사용자 트래픽 |
| 속도 | 느림 (일~주 단위) |
| A/B 테스트 | 기존 모델(A) vs 새 모델(B)에 트래픽 분배하여 비교 |
| Shadow Deployment | 새 모델이 실제 응답하지 않고, 기존 모델과 결과만 비교 |
| 도구 | Inference Table, Model Serving |
| 장점 | 높은 현실성, 실제 사용자 반응 측정 |
| 한계 | 시간 소요, 실 서빙 비용 발생 |

### Offline vs Online 비교

| 항목 | Offline | Online |
|------|---------|--------|
| 데이터 | 고정 평가셋 | 실제 사용자 트래픽 |
| 속도 | 빠름 (분) | 느림 (일~주) |
| 현실성 | 제한적 | 높음 |
| 비용 | 낮음 | 높음 (실 서빙 비용) |
| 적합 시기 | 개발/실험 중 | 배포 전 최종 검증, 배포 후 모니터링 |

{% hint style="info" %}
**권장 순서**: Offline 평가를 통과한 모델만 Online 평가로 진행하세요. Online 평가는 실제 사용자에게 영향을 미치므로, shadow deployment부터 시작하는 것을 권장합니다.
{% endhint %}

---

## 고객이 자주 묻는 질문

### "평가 없이 바로 배포해도 되나요?"

**절대 No.** 최소 30개 테스트 질문으로 Offline 평가를 수행해야 합니다. "잘 되는 것 같다"는 데모에서의 인상일 뿐, 프로덕션에서는 예상치 못한 질문에 환각이나 유해 응답이 발생할 수 있습니다. 평가 없는 배포는 테스트 없이 코드를 릴리스하는 것과 같습니다.

### "평가 비용이 너무 비싸지 않나요?"

**LLM-as-Judge로 자동화하면 건당 수 원 수준**입니다. 100개 질문 평가에 수천 원이면 충분합니다. 반면, 환각 응답이 고객에게 전달되었을 때의 비즈니스 손실(신뢰도 하락, 오보 정정, 법적 리스크)은 비교할 수 없이 큽니다.

### "어떤 메트릭을 봐야 하나요?"

사용 사례에 따라 핵심 메트릭 **3~5개에 집중**하세요.

| 사용 사례 | 최우선 메트릭 |
|----------|-------------|
| **RAG (문서 Q&A)** | Faithfulness, Relevance, Retrieval Precision |
| **Agent (도구 사용)** | Tool Selection Accuracy, Task Completion Rate |
| **고객 대면 챗봇** | Safety, Relevance, Latency |
| **내부 분석 도구** | Correctness, Groundedness |

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
5. RAG 시스템에서 Faithfulness는 높은데 Relevance가 낮은 경우, 원인이 검색 단계인지 생성 단계인지 어떻게 판별할 수 있는지 Retrieval 메트릭을 활용하여 설명하세요.
6. PoC 단계의 평가 데이터셋(30~50개)을 설계할 때, 정상/엣지/적대적 케이스를 각각 몇 개씩, 어떤 유형으로 구성할지 구체적인 예시를 작성하세요.
7. Offline 평가는 통과했지만 Online 평가(A/B 테스트)에서 성능이 크게 떨어지는 상황이 발생했습니다. 가능한 원인 3가지와 각각의 대응 방안을 제시하세요.

---

## 참고 자료

- [Databricks MLflow Evaluate 문서](https://docs.databricks.com/en/mlflow/llm-evaluate.html)
- [Databricks Review App 문서](https://docs.databricks.com/en/generative-ai/agent-evaluation/review-app.html)
- [Zheng et al., "Judging LLM-as-a-Judge" (2023)](https://arxiv.org/abs/2306.05685)
- [RAGAS: Evaluation Framework for RAG](https://docs.ragas.io/)
- [Databricks Agent Evaluation 가이드](https://docs.databricks.com/en/generative-ai/agent-evaluation/index.html)
