# 핵심 평가 메트릭

## 정확성 메트릭

### Faithfulness (충실도)

" ** 응답이 제공된 컨텍스트에 근거하는가?**" — RAG 시스템에서 가장 중요한 메트릭입니다.

| 상황 | 컨텍스트 (검색된 문서) | 모델 응답 | 판정 |
|------|----------------------|-----------|------|
| 성공 | "2024년 매출은 100억원" | "2024년 매출은 100억원입니다" | Faithful |
| 실패 | "2024년 매출은 100억원" | "2024년 매출은 **200억원** 입니다" | Not Faithful (수치 왜곡) |
| 실패 | "2024년 매출은 100억원" | "2024년 매출은 100억원이며 **전년 대비 20% 성장** 했습니다" | Not Faithful (근거 없는 추가 정보) |

### Relevance (관련성)

" ** 응답이 질문에 적절히 답하는가?**"

| 질문 | 모델 응답 | 판정 |
|------|-----------|------|
| "제품 가격이 얼마인가요?" | "Pro Plan은 월 $49, Enterprise는 월 $199입니다" | Relevant |
| "제품 가격이 얼마인가요?" | "우리 회사는 2015년에 설립되었습니다" | Not Relevant (질문과 무관) |
| "제품 가격이 얼마인가요?" | "Pro Plan은 강력한 기능을 제공합니다" | Partially Relevant (가격 미포함) |

### Groundedness (근거성)

" ** 출처에 기반한 응답인가?**" — Faithfulness와 유사하지만, 검색된 문서의 어느 부분에서 근거를 찾을 수 있는지까지 추적합니다.

### Correctness (정확성)

" ** 응답이 사실적으로 정확한가?**" — 정답 레이블이 있을 때 사용합니다.

---

## 안전성 메트릭

| 메트릭 | 설명 | 실패 예시 |
|--------|------|-----------|
| **Toxicity**(유해성) | 욕설, 혐오, 차별 표현 | "그런 질문은 바보나 하는 거죠" |
| **Bias**(편향) | 성별, 인종, 국적 등에 대한 편향 | "여성은 리더십에 적합하지 않습니다" |
| **PII Leakage** | 개인정보 노출 | "김철수님의 전화번호는 010-1234-5678입니다" |

---

## 검색(Retrieval) 메트릭 — RAG 시스템 전용

RAG 시스템을 평가할 때는 " ** 검색이 잘 되는가?**"와 " ** 생성이 잘 되는가?**"를 반드시 분리하여 측정해야 합니다. 검색 품질이 낮으면 아무리 좋은 LLM도 좋은 답변을 생성할 수 없습니다.

### Precision@K (정밀도)

**상위 K개 검색 결과 중 실제 관련 문서의 비율** 입니다. 검색된 5개 문서 중 3개가 관련 있다면 P@5 = 0.6입니다.

### Recall@K (재현율)

**전체 관련 문서 중 상위 K개에 포함된 비율** 입니다. 관련 문서가 총 10개인데 상위 5개에 5개가 포함되었다면 R@5 = 0.5입니다.

### MRR (Mean Reciprocal Rank)

**첫 번째 관련 문서의 순위 역수 평균** 입니다. 관련 문서가 3번째에 나오면 1/3, 1번째에 나오면 1/1입니다. 여러 질문에 대해 이 값을 평균합니다.

### NDCG (Normalized Discounted Cumulative Gain)

**상위 결과일수록 높은 가중치를 부여하여 전체 순위 품질을 측정** 합니다. 관련 문서가 위에 있을수록 NDCG가 높아집니다. 1에 가까울수록 이상적인 순위입니다.

| 메트릭 | 측정 대상 | 사용 시기 | 직관적 해석 |
|--------|----------|----------|------------|
| **Precision@K** | 검색 정확도 | "쓸모없는 결과가 너무 많은가?" | 높을수록 노이즈 적음 |
| **Recall@K** | 검색 완전성 | "빠뜨린 관련 문서가 있는가?" | 높을수록 누락 적음 |
| **MRR** | 첫 관련 결과 순위 | "관련 문서가 위에 나오는가?" | 높을수록 빠른 발견 |
| **NDCG** | 전체 순위 품질 | "전체적으로 순위가 적절한가?" | 1에 가까울수록 완벽 |

{% hint style="info" %}
**RAG 디버깅 팁**: RAG 시스템에서 Faithfulness 점수가 낮다면, 원인이 '검색'인지 '생성'인지를 먼저 구분하세요. Retrieval 메트릭이 낮으면 검색 개선(청킹 전략 변경, 임베딩 모델 교체)이 필요하고, Retrieval은 좋은데 생성이 나쁘면 프롬프트 수정이 필요합니다.
{% endhint %}

---

## 운영 메트릭

| 메트릭 | 설명 | 목표 |
|--------|------|------|
| **Latency**(지연시간) | 응답 생성까지 소요 시간 | < 3초 (대화형), < 30초 (분석형) |
| **Cost**(비용) | 토큰당 비용 | 사용 사례별 예산 내 |
| **Throughput**(처리량) | 초당 처리 요청 수 | 동시 사용자 기준 |
| **Token Efficiency** | 답변 대비 사용 토큰 수 | 불필요한 장문 응답 감지 |

---

## Agent 전용 평가 메트릭

Agent 평가는 단순 LLM Q\&A 평가와 근본적으로 다릅니다. 일반적인 LLM 평가가 " ** 입력 → 출력**"의 단일 단계를 측정한다면, Agent 평가는 " ** 입력 → 추론 → 도구 선택 → 실행 → 관찰 → 재추론 → ... → 최종 출력**"이라는 **다단계 의사결정 전체 경로** 를 측정해야 합니다.

{% hint style="info" %}
**왜 Agent 평가가 더 어려운가?** 같은 질문에 대해 Agent가 선택할 수 있는 경로가 여러 개 존재합니다. "서울 날씨 알려줘"라는 질문에 `weather_api()` → 응답 생성 경로와 `web_search("서울 날씨")` → 파싱 → 응답 생성 경로 모두 정답일 수 있습니다. 따라서 **최종 결과** 뿐 아니라 **경로의 효율성과 합리성** 도 함께 평가해야 합니다.
{% endhint %}

### 핵심 Agent 메트릭

| 메트릭 | 측정 대상 | 설명 | 계산 방법 |
|--------|----------|------|----------|
| **Tool Selection Accuracy** | 올바른 도구 선택 비율 | Agent가 질문에 적합한 도구를 선택했는가 | 정답 도구 선택 수 / 전체 도구 호출 수 |
| **Task Completion Rate** | 작업 완료 비율 | Agent가 사용자 요청을 끝까지 완수했는가 | 성공적으로 완료된 Task / 전체 요청 |
| **Step Efficiency** | 단계 효율성 | 최소 몇 단계로 완료할 수 있었는가 vs 실제 사용한 단계 | 최적 단계 수 / 실제 단계 수 |
| **Error Recovery Rate** | 오류 복구율 | 도구 호출 실패 후 대안을 찾아 성공했는가 | 복구 성공 수 / 전체 오류 수 |
| **Trajectory Quality** | 추론 경로 품질 | Agent의 Thought→Action→Observation 경로가 합리적이었는가 | LLM-as-Judge로 경로 평가 (1-5점) |
| **Multi-turn Consistency** | 다턴 일관성 | 여러 턴에 걸친 응답이 일관적인가 | 모순 발생 비율 |

{% hint style="warning" %}
**Tool Selection Accuracy가 가장 중요한 이유**: Agent가 잘못된 도구를 선택하면, 이후 모든 단계가 잘못된 방향으로 진행됩니다. 예를 들어 "지난 달 매출"을 묻는데 `search_documents()` 대신 `search_products()`를 호출하면, 아무리 후속 처리가 정확해도 최종 답변은 틀립니다. **Agent 품질 개선의 첫 번째 단계는 항상 Tool Selection 정확도를 높이는 것** 입니다.
{% endhint %}

### Agent 평가 방법론

Agent를 평가하는 세 가지 대표적인 접근법이 있습니다. 각각 장단점이 뚜렷하므로, 실무에서는 보통 **Component 평가로 병목을 찾고**→ **Trajectory 기반 평가로 원인을 분석** 하는 조합을 사용합니다.

#### 1. Trajectory 기반 평가 (가장 상세)

Agent의 **전체 추론 경로를 기록** 하고, 각 단계가 합리적인지 개별 평가합니다. MLflow Tracing을 사용하면 Thought → Action → Observation 전체 경로가 자동으로 기록됩니다.

```
Trajectory 기반 평가 예시:

  질문: "지난 달 매출 Top 5 제품은?"

  Step 1: Thought "매출 데이터를 조회해야 한다"
          → ✅ 합리적 추론

  Step 2: Action  search_products()
          → ❌ 잘못된 도구 선택 (query_sales가 맞음)

  Step 3: Observation "제품 목록 반환됨"
          → Agent가 오류를 인식하지 못함 ❌

  Step 4: Action  format_response()
          → 잘못된 데이터 기반으로 응답 생성

  평가 결과:
  - Tool Selection Accuracy: 0/1 = 0%
  - 근본 원인: search_products와 query_sales의 도구 설명이 모호
  - 개선 방향: 도구 Description을 더 구체적으로 작성
```

{% hint style="info" %}
**MLflow Tracing 연동**: Databricks에서 Agent를 배포하면 MLflow Tracing이 자동으로 모든 Trace를 기록합니다. 이 Trace 데이터를 평가 데이터셋으로 직접 활용할 수 있어, 별도의 로깅 파이프라인 없이도 Trajectory 기반 평가를 바로 시작할 수 있습니다.
{% endhint %}

#### 2. End-to-end 평가 (가장 빠름)

**최종 결과만 평가** 합니다 (입력 → 최종 출력). 내부 과정은 블랙박스로 취급합니다.

- **장점**: 평가 데이터셋 구성이 간단하고, 실행 속도가 빠름
- **단점**: "왜 틀렸는지" 파악이 어렵고, 개선 방향을 잡기 힘듦
- **사용 시기**: 빠른 회귀 테스트, A/B 테스트, 프로덕션 모니터링

#### 3. Component 평가 (가장 실용적)

Tool Selection, Retrieval, Generation을 **분리하여 각각 독립적으로 평가** 합니다.

- **장점**: "어디가 병목인가"를 정확히 식별 가능
- **단점**: 컴포넌트 간 상호작용 효과를 놓칠 수 있음
- **사용 시기**: 성능 저하 원인 분석, 특정 컴포넌트 개선 후 효과 측정

| 평가 방법 | 평가 범위 | 디버깅 용이성 | 데이터셋 복잡도 | 추천 사용 시기 |
|----------|----------|-------------|---------------|--------------|
| **Trajectory** | 전체 경로 | 매우 높음 | 높음 | 개발 단계, 심층 분석 |
| **End-to-end** | 최종 결과만 | 낮음 | 낮음 | CI/CD, 회귀 테스트 |
| **Component** | 개별 모듈 | 높음 | 중간 | 병목 식별, 최적화 |

### Agent 평가 데이터셋 설계

단순 Q\&A 평가셋과 달리, Agent 평가셋은 **기대하는 도구 호출 순서**, **최대 허용 단계 수**, **범위 밖 질문에 대한 기대 동작** 까지 정의해야 합니다.

#### 평가셋 구조 예시

```python
eval_data = [
    {
        "input": "지난 달 매출 Top 5 제품",
        "expected_tools": ["query_sql"],            # 기대하는 도구
        "expected_sql_contains": ["ORDER BY", "LIMIT 5"],  # SQL 검증
        "expected_response_contains": ["제품명", "매출"],    # 응답 검증
        "max_steps": 3,                              # 최대 허용 단계
    },
    {
        "input": "오늘 날씨 알려줘",                    # 범위 밖 질문
        "expected_tools": [],                         # 도구 호출하면 안 됨
        "expected_response_contains": ["지원하지 않"],   # Guardrail 응답 검증
    },
    {
        "input": "지난 분기 대비 이번 분기 매출 증감률",
        "expected_tools": ["query_sql", "query_sql"],  # 2번 호출 기대
        "expected_response_contains": ["증감률", "%"],
        "max_steps": 5,
    },
]
```

{% hint style="warning" %}
**범위 밖(Out-of-scope) 질문 필수 포함**: 평가셋에 "Agent가 답하면 안 되는 질문"을 반드시 포함하세요. Agent가 모든 질문에 무리하게 답변을 시도하면, 잘못된 도구를 호출하거나 Hallucination이 발생합니다. `expected_tools: []`로 설정하여 도구 호출 자체가 없어야 하는 케이스를 검증하세요.
{% endhint %}

#### 평가셋 설계 시 고려할 카테고리

| 카테고리 | 설명 | 예시 질문 | 비율 권장 |
|---------|------|----------|----------|
| **Happy Path** | 정상적인 단일 도구 호출 | "지난 달 매출은?" | 40% |
| **Multi-tool** | 여러 도구 조합이 필요 | "매출 추이 그래프 그려줘" | 20% |
| **Out-of-scope** | 범위 밖 질문 | "오늘 날씨는?" | 15% |
| **Ambiguous** | 모호한 질문 (확인 질문 기대) | "매출 알려줘" (기간 미지정) | 15% |
| **Error Recovery** | 도구 오류 시나리오 | DB 타임아웃 후 재시도 | 10% |

### MLflow에서 Agent 평가 구현

Databricks의 MLflow는 Agent 평가를 위한 **Custom Scorer** 를 지원합니다. 아래는 Tool Selection Accuracy를 측정하는 커스텀 스코어러 예시입니다.

```python
from mlflow.genai.scorers import scorer

@scorer
def tool_selection_accuracy(inputs, outputs, expectations):
    """Agent가 올바른 도구를 선택했는지 평가"""
    expected_tools = expectations.get("expected_tools", [])
    actual_tools = [
        step["tool"] for step in outputs.get("steps", [])
        if "tool" in step
    ]

    if not expected_tools:
        # 도구 호출이 없어야 하는 경우
        score = 1.0 if len(actual_tools) == 0 else 0.0
        justification = (
            "도구 호출 없음 (정상)" if score == 1.0
            else f"불필요한 도구 호출 발생: {actual_tools}"
        )
    else:
        matches = sum(1 for t in expected_tools if t in actual_tools)
        score = matches / len(expected_tools)
        justification = f"Expected: {expected_tools}, Got: {actual_tools}"

    return {
        "score": score,
        "justification": justification
    }


@scorer
def step_efficiency(inputs, outputs, expectations):
    """Agent가 최적 단계 수 대비 얼마나 효율적인지 평가"""
    max_steps = expectations.get("max_steps", 5)
    actual_steps = len(outputs.get("steps", []))

    if actual_steps == 0:
        return {"score": 0.0, "justification": "단계 정보 없음"}

    score = min(max_steps / actual_steps, 1.0)
    return {
        "score": score,
        "justification": f"최대 허용 {max_steps}단계, 실제 {actual_steps}단계 사용"
    }
```

위 스코어러를 사용하여 Agent를 평가하는 전체 흐름은 다음과 같습니다.

```python
import mlflow

# 평가 실행
results = mlflow.genai.evaluate(
    data=eval_data,
    predict_fn=agent.predict,
    scorers=[
        tool_selection_accuracy,
        step_efficiency,
        "faithfulness",     # 내장 스코어러
        "relevance",        # 내장 스코어러
    ],
)

# 결과 확인
print(results.tables["eval_results"])
```

{% hint style="info" %}
**실무 팁**: Agent 평가를 CI/CD 파이프라인에 통합하세요. 도구 설명(Description)이나 시스템 프롬프트를 수정할 때마다 자동으로 평가가 실행되어야 합니다. Tool Selection Accuracy가 기존 대비 5% 이상 하락하면 배포를 차단하는 게이트를 설정하는 것을 권장합니다.
{% endhint %}

---

## 추가 핵심 메트릭 — 실무에서 자주 간과되는 것들

### Context Relevance (컨텍스트 관련성)

" ** 검색된 문서가 질문에 관련이 있는가?**" — Faithfulness와 혼동하기 쉽지만 완전히 다른 메트릭입니다.

| 메트릭 | 비교 대상 | 질문 | 핵심 |
|--------|----------|------|------|
| **Faithfulness** | 답변 vs 검색 문서 | "답변이 문서 내용에 충실한가?" | 생성 단계 품질 |
| **Context Relevance** | 질문 vs 검색 문서 | "검색된 문서가 질문에 관련이 있는가?" | 검색 단계 품질 |

**구체적 예시**:

| 질문 | 검색된 문서 | Context Relevance | 설명 |
|------|-----------|-------------------|------|
| "2024년 매출 실적은?" | 2024년 재무보고서 | 높음 | 질문과 직접 관련된 문서 |
| "2024년 매출 실적은?" | 2023년 재무보고서 | 낮음 | 연도가 다른 문서. 모델이 이 문서를 참조하면 잘못된 수치를 답변할 위험 |
| "2024년 매출 실적은?" | 회사 연혁 소개 페이지 | 매우 낮음 | 매출과 전혀 무관한 문서 |

{% hint style="warning" %}
**실무 함정**: Context Relevance가 낮으면 Faithfulness가 높아도 의미가 없습니다. 엉뚱한 문서를 충실히 인용하면 "충실하지만 틀린 답변"이 됩니다. 예를 들어 2023년 재무보고서를 충실히 인용해서 "2024년 매출은 500억입니다"라고 답하면 Faithful하지만 Correct하지는 않습니다.
{% endhint %}

### Answer Completeness (답변 완전성)

" ** 질문의 모든 부분에 답변했는가?**" — 복합 질문에서 특히 중요합니다.

| 질문 | 답변 | Completeness | 누락 부분 |
|------|------|-------------|----------|
| "A, B, C 제품의 가격과 배송기간을 비교해줘" | "A는 10만원(3일), B는 15만원(2일), C는 20만원(5일)입니다" | 완전 | 없음 |
| "A, B, C 제품의 가격과 배송기간을 비교해줘" | "A는 10만원, B는 15만원, C는 20만원입니다" | 불완전 | 배송기간 누락 |
| "A, B, C 제품의 가격과 배송기간을 비교해줘" | "A는 10만원(3일), B는 15만원(2일)입니다" | 불완전 | C 제품 정보 누락 |

**Answer Completeness가 중요한 이유**: 사용자는 불완전한 답변을 받으면 후속 질문을 해야 합니다. 이는 사용자 경험을 악화시키고, 멀티턴 대화 비용을 증가시킵니다. 특히 보고서 생성, 비교 분석 등의 사용 사례에서는 불완전한 답변이 잘못된 의사결정으로 이어질 수 있습니다.

### Latency vs Quality 트레이드오프

응답 품질과 속도는 거의 항상 트레이드오프 관계에 있습니다. 모델이 더 많이 "생각"할수록 품질은 높아지지만 속도는 느려집니다.

| 사용 사례 | 적정 Latency | 품질 기대치 | 트레이드오프 전략 |
|----------|-------------|-----------|----------------|
| **대화형 챗봇** | 3초 이내 | 중간 (간결한 답변) | 작은 모델 + 스트리밍 출력. 사용자가 기다리지 않도록 첫 토큰 빠르게 |
| **분석/보고서** | 30초 이내 | 높음 (정확한 수치, 포괄적 분석) | 큰 모델 + 체인 오브 씽킹. 로딩 UI로 사용자 기대치 관리 |
| **리서치/탐색** | 수분 허용 | 매우 높음 (깊이 있는 분석) | 멀티 에이전트 + 반복 검증. 진행 상황 표시 필수 |
| **실시간 추천** | 500ms 이내 | 낮음~중간 (빠른 제안) | 캐싱 + 사전 계산. 모델 호출 최소화 |

{% hint style="info" %}
**측정 팁**: Latency는 단순 평균이 아닌 **P50, P95, P99 백분위수** 로 측정하세요. 평균 2초여도 P99가 15초면 100명 중 1명은 15초를 기다리는 것입니다. 사용자 불만은 항상 꼬리(tail) 지연에서 발생합니다.
{% endhint %}

---

## 흔한 오해 (Common Misconceptions)

평가 메트릭을 선택할 때 흔히 빠지는 오해들입니다.

| 오해 | 사실 |
|------|------|
| "BLEU/ROUGE 점수가 높으면 좋은 답변이다" | 이 메트릭들은 단어 겹침만 측정합니다. 의미적으로 동일하지만 다른 표현을 사용하면 낮게 나옵니다. LLM-as-Judge가 더 적합합니다. |
| "모든 메트릭을 다 측정해야 한다" | 사용 사례에 맞는 핵심 메트릭 3~5개에 집중하세요. RAG라면 Faithfulness와 Relevance가 최우선입니다. |
