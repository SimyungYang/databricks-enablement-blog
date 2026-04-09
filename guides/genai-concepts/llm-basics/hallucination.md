# Hallucination (환각)

[< LLM 기초 목차로 돌아가기](README.md)

---

LLM이 **사실이 아닌 내용을 자신있게 생성** 하는 현상입니다. GenAI의 가장 큰 실무적 리스크 중 하나입니다.

## 왜 Hallucination이 발생하는가?

1. **확률적 생성**: LLM은 "사실"을 검색하는 것이 아니라 "가장 그럴듯한 다음 토큰"을 예측합니다. 학습 데이터에서 자주 등장한 패턴을 조합하다 보면, 실제로 존재하지 않는 조합이 생성됩니다.
2. **학습 데이터 한계**: 학습 데이터에 오류가 있거나, 학습 이후에 변경된 정보는 반영되지 않습니다.
3. **과도한 일반화**: 학습된 패턴을 새로운 맥락에 부적절하게 적용합니다.

## 해결 방법

| 방법 | 원리 | 효과 |
|------|------|------|
| **RAG**(Retrieval-Augmented Generation) | 외부 문서를 검색하여 컨텍스트로 제공 → 문서 기반으로 답변 생성 | 출처 기반 답변으로 환각 대폭 감소 |
| **Grounding** | 특정 데이터 소스를 "근거"로 지정, 근거 없으면 답변 거부 | 근거 없는 답변 원천 차단 |
| **프롬프트 기법** | "모르면 모른다고 답하세요" 지시 추가 | 간단하지만 제한적 |
| **Self-Consistency** | 같은 질문을 여러 번 생성 → 일관된 답변만 채택 | 정확도 향상, 비용 증가 |

{% hint style="warning" %}
**핵심 원칙**: Enterprise 환경에서는 LLM 단독 사용을 지양하고, 반드시 **RAG + Guardrails** 를 결합하여 환각을 관리하세요.
{% endhint %}

## Hallucination 유형 분류

Hallucination을 효과적으로 관리하려면, 유형을 구분해야 합니다. 모든 Hallucination이 같은 것이 아닙니다.

| 유형 | 정의 | 예시 | 위험도 |
|------|------|------|--------|
| **Intrinsic Hallucination** | 입력 데이터에 **모순** 되는 출력 | 문서에 "매출 100억"이라고 있는데 "매출 150억"이라고 답변 | 매우 높음 |
| **Extrinsic Hallucination** | 입력에 **없는 정보** 를 생성 | 질문에 없는 "2023년 4분기 실적"을 자체 생성하여 답변 | 높음 |
| **Factual Hallucination** | 세계 지식과 **모순** 되는 사실 생성 | "서울의 인구는 약 2,000만 명입니다" (실제 ~950만) | 높음 |
| **Faithful but Wrong** | 입력에 충실하지만 입력 자체가 잘못된 경우 | 잘못된 문서를 RAG로 제공 → 그 문서에 충실하게 오답 생성 | 중간 |

{% hint style="info" %}
**실무 포인트**: Intrinsic Hallucination은 RAG를 사용해도 발생합니다. 모델이 검색된 문서를 **잘못 해석** 하거나 **부분적으로만 참조** 할 수 있기 때문입니다. RAG를 도입했다고 안심하지 말고, 출력 검증 레이어를 추가하세요.
{% endhint %}

## 왜 100% 제거가 불가능한가?

고객에게 가장 자주 받는 질문이 **"Hallucination을 완전히 없앨 수 있나요?"** 입니다. 솔직한 답변: **불가능합니다.** 그 이유를 설명합니다.

LLM의 생성 원리 자체가 **확률적(stochastic)** 입니다. 매 토큰 생성 시 확률 분포에서 샘플링하는 구조이므로, 아무리 정교하게 설계해도 **확률적 오류의 가능성이 0이 되지 않습니다.** Temperature를 0으로 설정해도 이는 "가장 높은 확률의 토큰을 선택"할 뿐, "사실적으로 정확한 토큰을 선택"하는 것이 아닙니다.

**"환각 0%"를 약속하면 안 되는 이유**:

1. **기술적으로 불가능**: 위에서 설명한 확률적 생성 원리
2. **평판 리스크**: 약속 후 환각이 발생하면 기술 신뢰도 전체가 하락
3. **비현실적 기대 설정**: 고객이 검증 없이 LLM 출력을 신뢰하게 됨

**고객에게 어떻게 설명할 것인가**:

> "LLM의 Hallucination은 자동차의 사고 위험과 같습니다. 안전벨트(RAG), 에어백(Guardrails), ABS(Self-Consistency)로 리스크를 95%+ 줄일 수 있지만, '사고 확률 0%'를 보장하는 자동차는 없습니다. 핵심은 **리스크를 수용 가능한 수준으로 관리** 하는 것입니다."

## 업종별 Hallucination 리스크와 방어 전략

Hallucination의 영향은 업종마다 크게 다릅니다. 잘못된 식당 추천은 큰 문제가 아니지만, 잘못된 약물 용량은 생명을 위협합니다.

**금융 — 잘못된 수치의 위험**

| 리스크 | 사례 | 방어 전략 |
|--------|------|----------|
| 잘못된 재무 수치 | "삼성전자의 2024년 영업이익은 75조원" (실제와 다른 수치) | 수치는 반드시 DB 쿼리로 검증. LLM은 해석/요약만 담당 |
| 존재하지 않는 규정 인용 | "금융위원회 고시 제2024-15호에 따르면..." (존재하지 않는 고시) | RAG에 공식 규정 문서만 인덱싱. 출처 미확인 시 답변 거부 |
| 잘못된 투자 조언 | 모델이 특정 종목 추천을 생성 | Guardrails로 투자 관련 출력 필터링. 면책 조항 필수 |

**의료 — 생명에 직결되는 정확성**

| 리스크 | 사례 | 방어 전략 |
|--------|------|----------|
| 잘못된 약물 상호작용 | "이 두 약은 함께 복용 가능합니다" (실제로는 금기) | 의학 DB(DrugBank 등)와 반드시 교차 검증 |
| 부정확한 진단 제안 | 증상 설명에 기반한 잘못된 진단 추론 | "참고용" 명시, 최종 판단은 반드시 의료 전문가 |
| 오래된 가이드라인 인용 | 학습 데이터 이후 변경된 치료 가이드라인 적용 | RAG에 최신 가이드라인 반영, 문서 날짜 검증 |

**법률 — 존재하지 않는 판례의 위험**

| 리스크 | 사례 | 방어 전략 |
|--------|------|----------|
| 허구의 판례 인용 | "대법원 2023다12345 판결에 의하면..." (실존하지 않는 판례번호) | 판례 DB API와 연동, 판례번호 실존 여부 자동 검증 |
| 법률 조항 오인 | 폐지된 법률 조항을 현행법으로 인용 | 법령정보센터 API 연동, 현행 여부 확인 |

{% hint style="warning" %}
**업종별 황금률**: 리스크가 높은 업종(금융, 의료, 법률)에서는 LLM을 "초안 생성기"로만 사용하고, 최종 출력은 반드시 **도메인 전문가 검토** 또는 **외부 DB 검증** 을 거치는 아키텍처를 설계하세요. 이것을 "Human-in-the-Loop" 또는 "LLM-assisted, Human-verified" 패턴이라고 합니다.
{% endhint %}

---

## 환각 측정 메트릭

환각을 관리하려면 먼저 **측정** 할 수 있어야 합니다. 주관적 판단이 아닌 정량적 메트릭으로 환각 수준을 평가합니다.

### 주요 환각 평가 벤치마크

| 메트릭/벤치마크 | 측정 대상 | 방식 | 점수 범위 |
|---------------|----------|------|----------|
| **TruthfulQA** | 모델의 사실적 정확성 | 817개 질문에 대한 답변의 진실성 평가 | 0~100% (높을수록 좋음) |
| **FActScore** | 긴 텍스트 생성의 사실 정확도 | 생성 텍스트를 원자적 사실(atomic fact)로 분해 → 각각 검증 | 0~100% |
| **RAGAS Faithfulness** | RAG 응답이 검색 문서에 충실한 정도 | 응답의 각 주장이 컨텍스트에서 추론 가능한지 NLI로 평가 | 0~1.0 |
| **RAGAS Answer Relevancy** | 응답이 질문에 관련된 정도 | 응답에서 질문을 역생성하여 원래 질문과 유사도 비교 | 0~1.0 |
| **HaluEval** | 다양한 유형의 환각 감지 | QA, 요약, 대화 등 여러 과제에서 환각 여부 판별 | 정확도 % |

### 모델별 환각률 벤치마크 (2025년 기준)

| 모델 | TruthfulQA (%) | RAGAS Faithfulness | FActScore (인물 전기) | 비고 |
|------|---------------|-------------------|---------------------|------|
| **GPT-4o** | ~82% | 0.85~0.92 | ~78% | 범용 최강급 |
| **Claude 4 Sonnet** | ~85% | 0.88~0.94 | ~81% | 사실 정확성에 강함 |
| **Claude 4 Opus** | ~88% | 0.90~0.95 | ~84% | 최고 수준의 정확성 |
| **Llama 3.3 70B** | ~68% | 0.78~0.85 | ~65% | 오픈소스 기준 우수 |
| **Llama 4 Maverick** | ~75% | 0.82~0.88 | ~72% | MoE 효율 + 정확성 개선 |
| **Mistral Large** | ~72% | 0.80~0.87 | ~68% | 유럽 언어에 강점 |

{% hint style="warning" %}
위 수치는 공개 벤치마크와 커뮤니티 평가를 종합한 **대략적 참고값** 입니다. 실제 성능은 프롬프트, 도메인, 언어에 따라 크게 달라질 수 있습니다. 자사 데이터로 직접 평가하는 것을 권장합니다.
{% endhint %}

---

## 자동 환각 감지 기법

### SelfCheckGPT: 일관성 기반 환각 감지

LLM에게 **같은 질문을 여러 번** 던져, 응답 간 **일관성** 을 비교합니다. 환각된 내용은 매번 다른 답변을 생성하고, 사실에 기반한 내용은 일관되게 반복됩니다.

```python
# SelfCheckGPT 개념적 구현
def selfcheck_gpt(question, model, n_samples=5):
    """같은 질문에 대해 n번 생성 → 일관성 측정"""
    responses = []
    for _ in range(n_samples):
        resp = model.generate(question, temperature=0.7)
        responses.append(resp)

    # 각 문장별로 다른 응답에서도 지지되는지 NLI로 확인
    main_response = responses[0]
    sentences = split_into_sentences(main_response)

    hallucination_scores = []
    for sentence in sentences:
        support_count = 0
        for other_resp in responses[1:]:
            if nli_check(premise=other_resp, hypothesis=sentence) == "entailment":
                support_count += 1
        score = support_count / (n_samples - 1)
        hallucination_scores.append({"sentence": sentence, "support": score})

    return hallucination_scores
    # support가 낮은 문장 = 환각 가능성 높음
```

### NLI (Natural Language Inference) 기반 일관성 검사

검색된 문서(premise)와 LLM 응답(hypothesis) 간의 **함의(entailment) 관계** 를 판단합니다.

| NLI 판정 | 의미 | 환각 여부 |
|---------|------|----------|
| **Entailment** | 문서가 응답을 뒷받침 | 환각 아님 |
| **Contradiction** | 문서와 응답이 모순 | Intrinsic Hallucination |
| **Neutral** | 문서에 관련 정보 없음 | Extrinsic Hallucination 가능성 |

### Chain-of-Verification (CoVe) 패턴

LLM이 스스로 생성한 답변을 **자체 검증** 하는 프롬프트 패턴입니다.

```
Step 1: [초안 생성] 질문에 답변하세요.
Step 2: [검증 질문 생성] 초안의 각 사실적 주장에 대해 검증 질문을 만드세요.
Step 3: [독립 검증] 각 검증 질문에 독립적으로 답변하세요 (초안을 보지 않고).
Step 4: [최종 답변] 검증 결과와 일치하지 않는 주장을 수정하여 최종 답변을 생성하세요.
```

{% hint style="info" %}
**실무 적용**: CoVe는 단일 호출 대비 **3~4배의 토큰** 을 소비하지만, 사실 정확성이 중요한 고위험 사용 사례(금융 보고서, 의료 요약)에서는 비용 대비 효과가 매우 높습니다.
{% endhint %}

---

## Guardrails 구현: Databricks에서의 환각 방어

### MLflow Evaluate로 Faithfulness 자동 측정

```python
import mlflow
import pandas as pd

# 평가 데이터셋 준비
eval_data = pd.DataFrame({
    "inputs": [
        "Unity Catalog의 3단계 네임스페이스는?",
        "Databricks의 창립 연도는?",
    ],
    "context": [
        "Unity Catalog는 catalog.schema.table의 3단계 네임스페이스를 사용합니다.",
        "Databricks는 2013년에 Apache Spark의 창시자들이 설립했습니다.",
    ],
    "ground_truth": [
        "catalog.schema.table",
        "2013년",
    ],
})

# MLflow Evaluate 실행
results = mlflow.evaluate(
    model="endpoints:/databricks-claude-sonnet-4",
    data=eval_data,
    model_type="question-answering",
    evaluators="default",
    extra_metrics=[
        mlflow.metrics.genai.faithfulness(
            model="endpoints:/databricks-claude-sonnet-4"
        ),
        mlflow.metrics.genai.relevance(
            model="endpoints:/databricks-claude-sonnet-4"
        ),
    ],
)

# 결과 확인
print(f"Faithfulness: {results.metrics['faithfulness/v1/mean']:.3f}")
print(f"Relevance: {results.metrics['relevance/v1/mean']:.3f}")
```

### Databricks AI Guardrails 설정

Agent Framework에서 Guardrails를 설정하여 환각을 실시간으로 차단합니다.

```yaml
# guardrails_config.yaml
safety:
  input_guardrails:
    - type: "topic_filter"
      blocked_topics: ["정치적 의견", "투자 조언"]
  output_guardrails:
    - type: "faithfulness_check"
      threshold: 0.7              # Faithfulness 점수 0.7 미만이면 차단
      fallback_message: "제공된 문서에서 해당 정보를 찾을 수 없습니다."
    - type: "pii_filter"
      entities: ["주민등록번호", "신용카드번호", "전화번호"]
```

---

## 인용/출처 추적: RAG 답변에 출처 표시하기

환각을 줄이는 가장 실용적인 방법 중 하나는 **답변에 출처를 명시** 하는 것입니다. 출처가 있으면 사용자가 직접 검증할 수 있고, 모델도 출처에 충실하게 답변하려는 경향이 강해집니다.

### 인용 추가 프롬프트 패턴

```
당신은 Databricks 문서 기반 질의응답 어시스턴트입니다.

규칙:
1. 반드시 아래 제공된 문서만을 기반으로 답변하세요.
2. 답변의 각 주장에 [Source N] 형식으로 출처를 표기하세요.
3. 문서에 없는 내용은 "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답하세요.
4. 여러 문서의 정보를 종합할 때는 모든 관련 출처를 표기하세요.

문서:
[Source 1] {document_1_title}: {document_1_content}
[Source 2] {document_2_title}: {document_2_content}
[Source 3] {document_3_title}: {document_3_content}

질문: {user_question}
```

### 출처 추적이 환각을 줄이는 이유

| 메커니즘 | 설명 |
|---------|------|
| **Grounding 강화** | 출처 표기를 요구하면 모델이 문서 내용에 더 집중 |
| **사용자 검증 가능** | 잘못된 인용은 사용자가 즉시 발견 가능 |
| **자신감 조절** | 출처를 찾지 못하면 "모르겠다"고 답할 확률 증가 |
| **감사 추적(Audit Trail)** | 규제 산업에서 요구하는 의사결정 근거 확보 |

{% hint style="info" %}
**인용 정확도 팁**: 출처 번호만 표기하는 것보다, **"문서 제목 + 관련 문장 인용"** 을 함께 요구하면 Intrinsic Hallucination(문서를 잘못 해석하는 환각)이 추가로 20~30% 감소합니다.
{% endhint %}

---

[< 이전: LLM 내부 작동 직관적 이해](internals.md) | [다음: 주요 LLM 모델 비교 >](models.md)
