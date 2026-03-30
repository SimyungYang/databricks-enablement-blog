# LLM 기초 (Large Language Model)

LLM은 대규모 텍스트 데이터로 학습된 딥러닝 모델로, 자연어를 이해하고 생성할 수 있습니다. GenAI의 핵심 기반 기술입니다.

{% hint style="info" %}
Databricks AI Playground에서 다양한 LLM을 직접 테스트해볼 수 있습니다.
{% endhint %}

---

## LLM이란?

**Large Language Model (대규모 언어 모델)**은 수십억~수조 개의 파라미터를 가진 신경망 모델입니다. 대량의 텍스트 데이터에서 언어 패턴을 학습하여, 주어진 입력(Prompt)에 대해 자연스러운 텍스트를 생성합니다.

### LLM의 주요 능력

- **텍스트 생성**: 자연스러운 문장, 코드, 요약 생성
- **질의응답**: 지식 기반 Q&A
- **추론**: 논리적 사고와 문제 해결
- **번역**: 다국어 텍스트 변환
- **코드 생성**: 프로그래밍 코드 작성 및 디버깅

---

## Transformer 아키텍처

2017년 Google의 "Attention Is All You Need" 논문에서 소개된 Transformer는 모든 현대 LLM의 기반 아키텍처입니다.

| 구성 요소 | 역할 | 설명 |
|-----------|------|------|
| Self-Attention | 문맥 파악 | 입력 토큰 간 관계를 계산 |
| Multi-Head Attention | 다양한 관점 | 여러 Attention을 병렬 수행 |
| Feed-Forward Network | 변환 | 각 위치의 표현을 비선형 변환 |
| Positional Encoding | 순서 정보 | 토큰의 위치 정보를 부여 |

{% hint style="info" %}
**핵심 원리**: Self-Attention 메커니즘은 "이 단어가 문장 내 다른 단어들과 얼마나 관련 있는지"를 계산합니다. 이를 통해 긴 문맥도 효과적으로 처리할 수 있습니다.
{% endhint %}

---

## 핵심 개념

### 토큰 (Token)

LLM이 텍스트를 처리하는 최소 단위입니다. 영어는 약 1 토큰 = 0.75 단어, 한국어는 음절/형태소 단위로 분리되어 토큰 수가 더 많습니다.

### 컨텍스트 윈도우 (Context Window)

모델이 한 번에 처리할 수 있는 최대 토큰 수입니다.

| 모델 | 컨텍스트 윈도우 |
|------|-----------------|
| GPT-4o | 128K 토큰 |
| Claude 3.5 Sonnet | 200K 토큰 |
| Llama 3.1 405B | 128K 토큰 |
| DBRX | 32K 토큰 |

### Temperature

모델 출력의 무작위성을 조절하는 파라미터입니다.

| 값 | 특성 | 용도 |
|----|------|------|
| 0.0 | 결정적 (항상 같은 응답) | 분류, 추출, 코드 |
| 0.3~0.7 | 균형 | 일반 대화, 요약 |
| 0.8~1.0 | 창의적 (다양한 응답) | 브레인스토밍, 창작 |

### Top-p (Nucleus Sampling)

누적 확률이 p에 도달할 때까지의 토큰만 후보로 사용합니다. Temperature와 함께 출력 다양성을 조절합니다.

---

## Prompt 구조 (System / User / Assistant)

대부분의 LLM API는 세 가지 역할의 메시지를 사용합니다.

| 역할 | 목적 | 예시 |
|------|------|------|
| **System** | 모델의 행동 규칙 정의 | "당신은 한국어 전문 번역가입니다" |
| **User** | 사용자 입력 | "이 문장을 영어로 번역해주세요" |
| **Assistant** | 모델의 응답 | "Here is the translation..." |

---

## 주요 LLM 모델 비교

| 모델 | 개발사 | 파라미터 | 특징 | 오픈소스 |
|------|--------|----------|------|----------|
| GPT-4o | OpenAI | 비공개 | 멀티모달, 범용 최강 | X |
| Claude 3.5 Sonnet | Anthropic | 비공개 | 긴 컨텍스트, 안전성 | X |
| Llama 3.1 | Meta | 8B~405B | 오픈웨이트, 커스텀 가능 | O |
| DBRX | Databricks | 132B (MoE) | MoE 아키텍처, 효율적 | O |
| Mistral Large | Mistral AI | 비공개 | 유럽 기반, 다국어 강점 | 부분 |

{% hint style="warning" %}
모델 성능은 빠르게 변화합니다. 최신 벤치마크는 [LMSYS Chatbot Arena](https://chat.lmsys.org/)를 참고하세요.
{% endhint %}

---

## Fine-tuning vs Prompting vs RAG 비교

| 항목 | Prompting | RAG | Fine-tuning |
|------|-----------|-----|-------------|
| **비용** | 낮음 | 중간 | 높음 |
| **구현 난이도** | 쉬움 | 중간 | 어려움 |
| **지식 업데이트** | 즉시 | 즉시 (문서 업데이트) | 재학습 필요 |
| **정확도** | 보통 | 높음 (검색 품질 의존) | 높음 (데이터 품질 의존) |
| **환각(Hallucination)** | 높음 | 낮음 (출처 기반) | 중간 |
| **Databricks 도구** | AI Playground | Vector Search + Agent | Mosaic AI Training |
| **적합한 경우** | 범용 작업, 빠른 테스트 | 사내 문서 Q&A | 도메인 특화 언어/스타일 |

{% hint style="success" %}
**실무 권장 순서**: Prompting으로 시작 → 부족하면 RAG 추가 → 그래도 부족하면 Fine-tuning 검토. 대부분의 Enterprise 사용 사례는 RAG로 충분합니다.
{% endhint %}

---

## 참고 자료

- [Vaswani et al., "Attention Is All You Need" (2017)](https://arxiv.org/abs/1706.03762)
- [Databricks Foundation Model APIs](https://docs.databricks.com/en/machine-learning/foundation-models/index.html)
- [Databricks AI Playground](https://docs.databricks.com/en/large-language-models/ai-playground.html)
- [DBRX 기술 블로그](https://www.databricks.com/blog/introducing-dbrx-new-state-art-open-llm)
