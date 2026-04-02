# 추론 모델 (Reasoning Models)

[< LLM 기초 목차로 돌아가기](README.md)

---

{% hint style="info" %}
**학습 목표**
- 추론 모델(o1, o3, R1)이 기존 LLM과 어떻게 다른지 설명할 수 있다
- "Test-time Compute" 패러다임을 이해하고 비용/성능 트레이드오프를 판단할 수 있다
- Agent 설계에서 추론 모델을 언제 사용해야 하는지 결정할 수 있다
{% endhint %}

2024년 9월, OpenAI가 **o1** 을 공개하면서 LLM의 새로운 패러다임이 시작되었습니다. 기존 LLM이 "즉시 답하는" 모델이었다면, 추론 모델은 **"생각하는 시간을 들여 더 정확하게 답하는" **모델입니다. 이 차이는 단순한 성능 개선이 아니라, AI 시스템 설계 방식 자체를 바꾸는 패러다임 전환입니다.

---

## 1. 추론 모델이란?

### System 1 vs System 2 사고

노벨 경제학상 수상자 Daniel Kahneman은 인간의 사고를 두 가지 시스템으로 설명했습니다:

| 구분 | **System 1 (빠른 사고)** | **System 2 (느린 사고)** |
|------|------------------------|------------------------|
| **특징** | 직관적, 자동적, 빠름 | 분석적, 의도적, 느림 |
| **인간 예시** | "2+2는?" → 즉답 | "17 x 24는?" → 계산 과정 필요 |
| **LLM 비유** | 기존 LLM (GPT-4o, Sonnet) | 추론 모델 (o3, Extended Thinking) |
| **compute 투자 시점** | 학습(training) 시 집중 | 추론(inference) 시에도 추가 투자 |

**기존 LLM** 은 학습 시에 막대한 compute를 투자하고, 추론 시에는 빠르게 응답합니다. 입력 토큰을 받으면 즉시 다음 토큰을 예측하는 방식입니다. 이것은 System 1 사고에 해당합니다.

**추론 모델** 은 추론 시에도 추가 compute를 투자합니다. 모델이 최종 답변을 생성하기 전에 **내부적으로 "생각하는" 과정** 을 거칩니다. 이 과정에서 문제를 분해하고, 여러 접근법을 검토하고, 중간 결과를 검증합니다. 이것은 System 2 사고에 해당합니다.

### "더 오래 생각하면 더 정확하다"

이 원리는 수학, 코딩, 논리 추론 같은 **정답이 명확한 복잡한 작업** 에서 극적인 효과를 보입니다. 기존 모델이 30% 정도의 정확도를 보이던 수학 경시대회 수준의 문제에서, 추론 모델은 **90% 이상** 의 정확도를 달성합니다.

{% hint style="info" %}
**비유**: 기존 LLM은 "시험에서 바로 답을 적는 학생"이고, 추론 모델은 "연습장에 풀이 과정을 쓴 후 답을 적는 학생"입니다. 풀이 과정(thinking tokens)에 시간과 비용이 들지만, 정확도가 비약적으로 향상됩니다.
{% endhint %}

---

## 2. 주요 추론 모델 비교

| 모델 | 개발사 | 출시 | 핵심 특징 | 가격대 (1M 입력 토큰) |
|------|--------|------|----------|----------------------|
| **o1** | OpenAI | 2024.09 | 최초의 추론 모델. 수학/코딩 벤치마크 급상승 | ~$15.00 |
| **o3** | OpenAI | 2025.04 | o1 후속. Tool Use 결합. 모든 ChatGPT 도구와 연동 | ~$10.00 |
| **o4-mini** | OpenAI | 2025.04 | 경량 추론 모델. 빠르고 저렴하면서도 추론 능력 보유 | ~$1.10 |
| **DeepSeek R1** | DeepSeek | 2025.01 | 오픈소스 추론 모델. 저비용 고성능의 가능성 입증 | 셀프호스팅 가능 |
| **Claude Extended Thinking** | Anthropic | 2025.02 | Configurable thinking budget. Interleaved thinking + tool use | Sonnet 기준 ~$3.00 |
| **Gemini 2.5 Pro** | Google | 2025.03 | Deep Think mode. 1M+ 컨텍스트 윈도우 | ~$1.25 |

{% hint style="warning" %}
추론 모델의 가격은 **thinking tokens(내부 추론 토큰)** 비용이 별도로 발생합니다. 위 가격은 입력 토큰 기준이며, thinking tokens은 일반 출력 토큰보다 비싼 경우가 많습니다. 공식 가격표를 반드시 확인하세요.
{% endhint %}

---

## 3. 작동 원리: Chain-of-Thought at Inference

### 기존 LLM의 생성 과정

```
[사용자 프롬프트] → [모델] → [바로 최종 출력]
```

기존 LLM은 입력을 받으면 즉시 출력 토큰을 생성합니다. 내부적으로는 Forward Pass 한 번에 하나의 토큰을 예측하는 과정을 반복합니다. 중간에 "생각하는" 단계가 없습니다.

### 추론 모델의 생성 과정

```
[사용자 프롬프트] → [모델] → [내부 reasoning tokens 생성] → [최종 출력]
```

추론 모델은 최종 답변 전에 **reasoning tokens(추론 토큰)** 을 내부적으로 생성합니다. 이 토큰들은 사용자에게 보이지 않지만, 모델이 문제를 분석하고 풀이하는 과정을 담고 있습니다.

### Thinking Tokens의 특성

| 항목 | 설명 |
|------|------|
| **가시성** | 사용자에게 보이지 않음 (API 응답에 포함되지 않음) |
| **비용** | 토큰 비용은 발생함. 일반 출력 토큰보다 비싼 경우도 있음 |
| **양** | 문제 복잡도에 따라 수백~수만 토큰. 간단한 질문에도 수천 토큰 사용 가능 |
| **제어** | Anthropic: thinking budget으로 configurable / OpenAI: 자동 (reasoning_effort 파라미터) |

### 예시: 수학 문제에서의 차이

**문제**: "한 변의 길이가 7인 정육면체의 대각선 길이를 구하세요."

**기존 LLM (GPT-4o)**: 바로 답변 시도. 때때로 계산 오류 발생.

**추론 모델 (o3)**: 내부적으로 다음과 같은 사고 과정을 거침:
1. 정육면체의 대각선 = sqrt(a^2 + a^2 + a^2)
2. a = 7이므로 sqrt(49 + 49 + 49) = sqrt(147)
3. sqrt(147) = 7 * sqrt(3) ≈ 12.124
4. 검증: 7^2 * 3 = 147, sqrt(147) ≈ 12.124 ✓

이 풀이 과정이 **thinking tokens** 로 생성되고, 최종적으로 정답만 사용자에게 전달됩니다.

---

## 4. Test-time Compute Scaling

### 기존 패러다임: Training-time Scaling

지금까지 LLM 성능 향상의 핵심 전략은 **학습 시점의 스케일링** 이었습니다:

- **더 큰 모델**: 파라미터 수 증가 (GPT-3 175B → GPT-4 추정 1.8T)
- **더 많은 데이터**: 학습 데이터 규모 증가
- **더 많은 compute**: 학습에 투입하는 GPU 시간 증가

이것이 바로 **Scaling Law**(Kaplan et al., 2020)의 핵심이었습니다. 하지만 이 접근법은 한계에 도달하고 있습니다: 모델을 10배 크게 만드는 데 드는 비용이 기하급수적으로 증가합니다.

### 새로운 패러다임: Test-time Scaling

추론 모델은 완전히 다른 방향을 제시합니다:

> **추론 시 더 많은 토큰을 "생각"에 쓰면(test-time compute), 성능이 향상된다.**

이것은 모델 크기를 키우지 않고도 성능을 높일 수 있는 새로운 경로입니다.

### Inference-time Scaling Law

연구 결과에 따르면, 추론 모델의 정확도는 thinking tokens 수에 대해 **log-linear** 하게 증가합니다:

```
정확도 ∝ log(thinking tokens 수)
```

이는 thinking tokens을 2배로 늘리면 정확도가 일정량 증가하고, 다시 2배로 늘리면 같은 양만큼 증가하는 패턴입니다. 수확 체감(diminishing returns)이 있지만, 복잡한 문제에서는 추가 compute 투자가 확실한 가치를 제공합니다.

### 비용 임팩트

| 시나리오 | 입력 토큰 | Thinking 토큰 | 출력 토큰 | 총 비용 비율 |
|----------|----------|--------------|----------|-------------|
| 기존 LLM (GPT-4o) | 1,000 | 0 | 500 | 1x |
| 추론 모델 (낮은 추론) | 1,000 | 2,000 | 500 | ~3x |
| 추론 모델 (중간 추론) | 1,000 | 10,000 | 500 | ~8x |
| 추론 모델 (높은 추론) | 1,000 | 50,000 | 500 | ~30x |

{% hint style="warning" %}
같은 질문에 **10배 이상 많은 토큰** 을 소비할 수 있습니다. 단순 질문에 추론 모델을 사용하면 비용만 늘고 정확도 개선은 미미합니다. **정확도가 비즈니스 가치에 직결되는 작업** 에서만 추론 모델을 선택하세요.
{% endhint %}

---

## 5. Agent에서의 추론 모델 활용

### 언제 추론 모델을 쓰는가

추론 모델은 다음과 같은 작업에서 **일반 LLM 대비 압도적 성능 향상** 을 보입니다:

- **복잡한 계획 수립**: 다단계 작업의 순서와 의존성 파악
- **코드 생성 및 디버깅**: 복잡한 알고리즘, 시스템 설계
- **수학/논리 추론**: 정량적 분석, 증명, 최적화 문제
- **데이터 분석 전략**: 여러 데이터 소스를 결합한 분석 계획

### 언제 일반 모델이 나은가

속도와 비용이 중요한 작업에서는 일반 LLM이 더 적합합니다:

- **단순 분류/추출**: 감정 분석, 엔티티 추출
- **텍스트 검색/요약**: RAG 기반 Q&A
- **번역**: 다국어 변환
- **일상 대화**: 챗봇, 고객 응대

### Cascade 패턴

실무에서 가장 많이 사용되는 패턴은 **Cascade (단계적 에스컬레이션)** 입니다:

```
1단계: 일반 모델(GPT-4o-mini)로 먼저 시도
    ↓ (불확실하거나 복잡한 경우)
2단계: 추론 모델(o3)로 재시도
```

**구현 방식**:
- 1단계 모델의 **confidence score** 가 임계값 이하이면 2단계로 에스컬레이션
- 특정 **작업 유형** 을 감지하면 바로 2단계로 라우팅 (예: 수학 문제, 코드 생성)
- Databricks **Mosaic AI Gateway** 에서 라우팅 규칙으로 구현 가능

### Interleaved Thinking (Anthropic)

Anthropic의 Claude Extended Thinking은 **생각하면서 도구를 호출** 할 수 있는 독특한 기능을 제공합니다:

```
[사고 시작] → 문제 분석 → [도구 호출: 데이터 검색] → 결과 분석 →
[추가 사고] → [도구 호출: 계산] → 최종 답변 도출 → [사고 종료] → [출력]
```

이것은 Agent 설계에서 매우 강력합니다. 기존 추론 모델(o1)은 "생각을 다 끝내고 나서" 도구를 호출했지만, Interleaved Thinking은 **사고 과정 중에 필요한 정보를 실시간으로 수집** 할 수 있습니다.

{% hint style="info" %}
**Agent 설계 팁**: Interleaved Thinking이 가능한 모델은 "계획(Plan)" 과 "실행(Act)"을 분리하지 않아도 됩니다. 모델이 자연스럽게 생각 → 도구 호출 → 추가 사고를 반복하므로, ReAct 패턴이 모델 내부에 내장된 것과 같은 효과를 얻습니다.
{% endhint %}

---

## 6. DeepSeek R1: 오픈소스 추론 모델의 충격

### 2025년 1월, AI 업계를 뒤흔든 발표

DeepSeek R1은 중국의 AI 스타트업 DeepSeek이 2025년 1월에 공개한 **오픈소스 추론 모델** 입니다. 이 모델이 충격적이었던 이유는 다음과 같습니다:

**성능**: 기존 OpenAI o1과 비슷한 수준의 수학/코딩 벤치마크 성능을 달성

**비용**: 추정 학습 비용이 o1 대비 **1/50 수준**(약 $5.6M)

**오픈소스**: 모델 가중치를 완전 공개하여 누구나 자체 호스팅 가능

### 의미와 시사점

| 측면 | 영향 |
|------|------|
| **비용 민주화** | 추론 모델이 대형 테크 기업만의 전유물이 아님을 입증 |
| **데이터 주권** | 오픈소스 → 자체 호스팅 → 데이터가 외부로 나가지 않음 |
| **커스터마이징** | Fine-tuning 가능 → 도메인 특화 추론 모델 구축 가능 |
| **경쟁 촉진** | OpenAI, Google, Anthropic의 가격 인하 촉발 |

### 한계

- **영어 외 언어 성능**: 한국어 등 비영어권 언어에서 성능 불안정
- **안전성 필터**: 상용 모델 대비 안전성 가드레일이 부족
- **Hallucination**: 추론 과정에서 잘못된 중간 단계가 최종 답에 전파될 수 있음
- **지원 및 SLA**: 상용 API 대비 기업용 지원 체계 부재

{% hint style="warning" %}
**고객 대응 시 주의**: R1의 벤치마크 성능은 인상적이지만, Enterprise 환경에서는 **안전성, 다국어 지원, SLA** 를 종합적으로 평가해야 합니다. "R1이 o1만큼 좋다고 하는데 왜 비싼 모델을 써야 하나?"라는 질문에는, 벤치마크와 실제 업무 성능의 차이, 그리고 운영 부담을 설명하세요.
{% endhint %}

---

## 7. 비용/성능 트레이드오프 가이드

### 사용 사례별 권장 모델

| 사용 사례 | 권장 모델 | 이유 |
|----------|----------|------|
| 단순 분류/추출 | GPT-4o-mini / Haiku | 빠르고 저렴. 추론 불필요 |
| 일반 대화/요약 | GPT-4o / Sonnet | 속도와 품질의 균형 |
| 복잡한 코딩 | o3 / Claude 4 Opus | 정확도가 개발 생산성에 직결 |
| 수학/논리 추론 | o3 / R1 | 추론 능력이 필수인 영역 |
| Agent 계획 수립 | o3 + Tool Use | 계획 수립 + 실행을 결합 |
| 비용 최적화 필요 | o4-mini / R1 | 추론 성능을 유지하면서 비용 절감 |
| 대량 배치 처리 | GPT-4o-mini / Haiku | 건당 비용이 핵심 |
| 규제 산업 (금융/의료) | Claude 4 Opus (Extended Thinking) | 정확도 + 안전성 + 추론 과정 추적 가능 |

### 의사결정 플로우

```
질문: "이 작업에 추론 모델이 필요한가?"

1. 작업이 복잡한 논리/계산/코딩을 포함하는가?
   → No: 일반 모델 사용 (GPT-4o-mini, Sonnet)
   → Yes: 다음 단계로

2. 정확도 실패의 비즈니스 비용이 높은가?
   → No: 일반 모델 + 검증 레이어
   → Yes: 다음 단계로

3. 실시간 응답이 필요한가?
   → Yes: o4-mini (빠른 추론) 또는 Cascade 패턴
   → No: o3 / Claude Extended Thinking (최대 정확도)
```

{% hint style="info" %}
**핵심 원칙**: 추론 모델은 "모든 곳에 쓰는 것"이 아니라, **"정확도가 비용보다 중요한 병목 지점" **에 선택적으로 배치하는 것이 최적입니다. 전체 시스템의 80%는 일반 모델로, 20%의 핵심 작업만 추론 모델로 처리하는 것이 일반적입니다.
{% endhint %}

---

## 8. Databricks에서 추론 모델 활용

### Foundation Model APIs

Databricks Foundation Model APIs를 통해 주요 추론 모델을 바로 사용할 수 있습니다:

| 모델 | 가용 여부 | 비고 |
|------|----------|------|
| **o3** | Pay-per-token (External Models) | OpenAI API 키 연동 |
| **Claude 4 Opus (Extended Thinking)** | Pay-per-token (External Models) | Anthropic API 키 연동 |
| **DeepSeek R1** | Provisioned Throughput 또는 External Models | 셀프호스팅 시 Model Serving 활용 |
| **Gemini 2.5 Pro** | External Models | Google API 키 연동 |

### Mosaic AI Gateway로 지능형 라우팅

**AI Gateway** 를 사용하면 일반 모델과 추론 모델 간의 **자동 라우팅** 을 구현할 수 있습니다:

- **규칙 기반 라우팅**: 프롬프트 내 키워드 또는 메타데이터 기반으로 모델 선택
- **Fallback 체인**: 1차 모델 실패 시 자동으로 2차 모델로 전환
- **A/B 테스트**: 일반 모델 vs 추론 모델의 성능을 비교 실험

### 비용 모니터링

추론 모델 사용 시 **thinking tokens** 이 전체 비용의 대부분을 차지할 수 있습니다. AI Gateway에서 다음을 추적하세요:

- **토큰 사용량 분해**: 입력 토큰 / thinking 토큰 / 출력 토큰 별도 집계
- **요청당 평균 비용**: 추론 모델 요청의 평균 비용 추이
- **비용 이상 탐지**: thinking tokens이 비정상적으로 많은 요청 감지
- **예산 제한**: 일/월 단위 비용 한도 설정

{% hint style="info" %}
**실무 팁**: AI Gateway의 usage dashboard에서 thinking tokens 비율을 모니터링하세요. 만약 thinking tokens이 전체 비용의 90% 이상을 차지하고 있다면, 해당 작업이 정말 추론 모델이 필요한지 재검토가 필요합니다.
{% endhint %}

---

## 9. 고객 FAQ

### Q1. "추론 모델이 더 좋으면 모든 곳에 추론 모델을 쓰면 되지 않나요?"

아닙니다. 추론 모델은 **응답 시간이 길고 비용이 높습니다.**"오늘 날씨 어때?"라는 질문에 30초간 "생각"할 필요가 없습니다. 단순 분류, 검색, 번역 같은 작업에서는 일반 모델이 더 빠르고 저렴하면서도 충분한 품질을 제공합니다. 추론 모델은 **정확도가 비즈니스 임팩트에 직결되는 복잡한 작업** 에만 선택적으로 사용하세요.

### Q2. "DeepSeek R1을 자체 호스팅하면 비용을 대폭 절감할 수 있나요?"

이론적으로 가능하지만, **GPU 인프라 비용, 운영 인력, 모니터링 시스템** 등 총소유비용(TCO)을 고려해야 합니다. 하루에 수만 건 이상의 추론 요청이 있다면 자체 호스팅이 유리할 수 있지만, 소량이라면 API 호출이 더 경제적입니다. 또한 R1은 안전성 필터가 부족하므로, Enterprise 환경에서는 **별도의 Guardrail 레이어** 를 구축해야 합니다.

### Q3. "추론 모델의 thinking process를 고객에게 보여줄 수 있나요?"

모델마다 다릅니다. OpenAI의 o3는 thinking tokens을 API 응답에 포함하지 않습니다 (요약만 제공). Anthropic의 Extended Thinking은 thinking 내용을 API에서 조회할 수 있습니다. 규제 산업(금융, 의료)에서 **의사결정 근거를 추적** 해야 한다면, thinking 내용을 확인할 수 있는 모델을 선택하는 것이 유리합니다.

### Q4. "기존 Agent를 추론 모델로 바꾸면 바로 성능이 올라가나요?"

단순히 모델만 교체하면 성능이 오를 수도 있지만, **프롬프트 최적화** 가 필요합니다. 기존 모델용 프롬프트에는 "단계적으로 생각하세요(Let's think step by step)" 같은 Chain-of-Thought 유도 문구가 포함되어 있을 수 있는데, 추론 모델에서는 이것이 오히려 **불필요한 중복** 이 됩니다. 추론 모델은 자체적으로 사고 과정을 수행하므로, 프롬프트를 간결하게 수정하는 것이 좋습니다.

---

## 10. 참고 자료

**논문 및 공식 문서**:
- [Scaling LLMs with Test-time Compute (Snell et al., 2024)](https://arxiv.org/abs/2408.03314) — Test-time Compute Scaling의 핵심 논문
- [OpenAI o1 System Card](https://openai.com/index/openai-o1-system-card/) — o1의 설계 원칙과 안전성 평가
- [DeepSeek R1 Technical Report](https://arxiv.org/abs/2501.12948) — R1 학습 방법론 상세
- [Anthropic Extended Thinking Documentation](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking) — Extended Thinking API 가이드

**벤치마크 및 비교**:
- [LMSYS Chatbot Arena](https://chat.lmsys.org/) — 실시간 모델 성능 비교
- [Artificial Analysis](https://artificialanalysis.ai/) — 모델별 가격/성능/속도 비교

**Databricks 관련**:
- [Databricks Foundation Model APIs](https://docs.databricks.com/en/machine-learning/foundation-models/index.html) — 모델 API 사용 가이드
- [Mosaic AI Gateway](https://docs.databricks.com/en/machine-learning/model-serving/ai-gateway.html) — AI Gateway 라우팅 설정

---

## LLM 기초 시리즈 탐색

| 페이지 | 내용 |
|--------|------|
| [Transformer 아키텍처](transformer.md) | Self-Attention, Multi-Head Attention, Positional Encoding |
| [핵심 개념](core-concepts.md) | Token, 토큰화, Context Window, Temperature, Top-p |
| [LLM 학습 과정](training.md) | Pre-training, SFT, RLHF/DPO 3단계 |
| [LLM 내부 작동 직관적 이해](internals.md) | 패턴 매칭, 세계 모델, Scaling, 비유 모음 |
| [Hallucination](hallucination.md) | 유형, 원인, 해결, 업종별 리스크 |
| [주요 LLM 모델 비교](models.md) | 모델 비교표, MoE 아키텍처, Emergent Abilities |
| [실전 가이드](practical.md) | Fine-tuning vs RAG vs Prompting, 추론 최적화, 비용 최적화 |
| **추론 모델**(현재 페이지) | o1, o3, R1, Extended Thinking, Test-time Compute |

---

[< LLM 기초 목차로 돌아가기](README.md) · [다음: Transformer 아키텍처 →](transformer.md)
