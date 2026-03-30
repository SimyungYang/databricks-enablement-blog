# Prompt Engineering

Prompt Engineering은 LLM에게 원하는 결과를 이끌어내기 위해 입력(Prompt)을 체계적으로 설계하는 기술입니다. 코드 한 줄 없이 AI의 성능을 극대화할 수 있는 가장 접근성 높은 방법입니다.

{% hint style="info" %}
Databricks AI Playground에서 다양한 프롬프트 기법을 즉시 실험할 수 있습니다.
{% endhint %}

---

## Prompt Engineering이란?

LLM은 입력(프롬프트)에 따라 출력 품질이 크게 달라집니다. Prompt Engineering은 **최적의 입력을 설계하여 최적의 출력을 얻는 체계적 방법론**입니다.

| 요소 | 설명 |
|------|------|
| **명확성** | 모호하지 않은 명확한 지시 |
| **구체성** | 원하는 형식, 길이, 스타일 명시 |
| **맥락** | 충분한 배경 정보 제공 |
| **예시** | 입출력 예시를 통한 패턴 학습 |

---

## 기본 기법

### Zero-shot Prompting

예시 없이 직접 지시하는 방식입니다. 간단한 작업에 효과적입니다.

```
다음 리뷰의 감정을 분류하세요: 긍정, 부정, 중립
리뷰: "이 제품 정말 좋아요! 배송도 빨랐습니다."
```

### Few-shot Prompting

입출력 예시를 제공하여 패턴을 학습시키는 방식입니다.

```
리뷰: "최고의 서비스입니다" → 긍정
리뷰: "다시는 안 삽니다" → 부정
리뷰: "그냥 평범합니다" → 중립
리뷰: "포장이 좀 아쉽지만 제품은 좋아요" → ?
```

### Chain-of-Thought (CoT)

단계적 추론을 유도하여 복잡한 문제를 해결합니다.

```
문제를 단계별로 풀어보세요:
1단계: 주어진 조건을 정리합니다
2단계: 필요한 계산을 수행합니다
3단계: 최종 답을 도출합니다
```

{% hint style="success" %}
**팁**: "단계별로 생각해보세요 (Let's think step by step)"를 추가하는 것만으로도 추론 정확도가 크게 향상됩니다.
{% endhint %}

### System Prompt 설계 패턴

System Prompt는 모델의 역할, 행동 규칙, 제약 조건을 정의합니다.

| 구성 요소 | 예시 |
|-----------|------|
| **역할 정의** | "당신은 Databricks 전문 기술 컨설턴트입니다" |
| **행동 규칙** | "모르는 내용은 '확인이 필요합니다'라고 답하세요" |
| **출력 형식** | "JSON 형식으로 응답하세요" |
| **제약 조건** | "답변은 200자 이내로 작성하세요" |
| **언어 지정** | "항상 한국어로 응답하세요" |

---

## 고급 기법

### ReAct Prompting

추론(Reasoning)과 행동(Acting)을 결합한 프롬프트 패턴입니다. Agent 시스템에서 핵심적으로 사용됩니다.

```
Thought: 사용자가 매출 데이터를 요청하고 있습니다. DB를 조회해야 합니다.
Action: query_database("SELECT SUM(revenue) FROM sales WHERE year=2025")
Observation: 총 매출은 50억원입니다.
Thought: 결과를 사용자에게 정리해서 전달합니다.
Answer: 2025년 총 매출은 50억원입니다.
```

### Tree-of-Thought (ToT)

여러 추론 경로를 탐색하고 최적의 경로를 선택합니다.

| 단계 | 설명 |
|------|------|
| 확장 | 여러 가능한 추론 경로 생성 |
| 평가 | 각 경로의 유망성 점수 부여 |
| 선택 | 최적 경로 선택하여 계속 진행 |

### Self-Consistency

동일 질문에 여러 번 추론하고, 가장 빈번한 답을 최종 결과로 채택합니다. Temperature > 0으로 설정하여 다양한 추론 경로를 생성합니다.

### Structured Output (JSON Mode)

LLM 출력을 JSON 등 구조화된 형식으로 제한합니다.

```
다음 정보를 JSON 형식으로 추출하세요:
{"name": "이름", "company": "회사명", "role": "직책"}

입력: "삼성전자 AI센터장 김철수입니다"
```

{% hint style="warning" %}
JSON Mode를 사용할 때는 반드시 출력 스키마를 명시하세요. 스키마 없이 "JSON으로 응답해" 라고만 하면 불안정한 출력이 발생할 수 있습니다.
{% endhint %}

---

## Databricks에서 Prompt Engineering

### AI Playground에서 테스트

AI Playground는 다양한 모델과 프롬프트를 실시간으로 실험할 수 있는 UI입니다.

| 기능 | 설명 |
|------|------|
| 모델 비교 | 동일 프롬프트로 여러 모델 응답 비교 |
| 파라미터 조절 | Temperature, Top-p, Max Tokens 실시간 조정 |
| System Prompt | System 프롬프트 별도 입력 가능 |
| Tool 연결 | Unity Catalog Function을 도구로 연결 |

### MLflow Prompt Registry

프롬프트를 코드처럼 **버전 관리**할 수 있는 기능입니다.

| 기능 | 설명 |
|------|------|
| 버전 관리 | 프롬프트 변경 이력 추적 |
| 템플릿 변수 | `{variable}` 형태로 동적 프롬프트 구성 |
| A/B 테스트 | 프롬프트 버전 간 성능 비교 |
| 팀 협업 | 프롬프트를 팀과 공유 및 리뷰 |

### 프롬프트 버전 관리 워크플로우

1. MLflow Prompt Registry에 프롬프트 등록
2. 변경 시 새 버전 생성 (기존 버전 보존)
3. MLflow Evaluate로 버전 간 품질 비교
4. 최적 버전을 프로덕션에 적용

---

## 참고 자료

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)
- [Wei et al., "Chain-of-Thought Prompting" (2022)](https://arxiv.org/abs/2201.11903)
- [Yao et al., "Tree of Thoughts" (2023)](https://arxiv.org/abs/2305.10601)
- [Databricks AI Playground 문서](https://docs.databricks.com/en/large-language-models/ai-playground.html)
