# GenAI 핵심 개념 총정리

이 섹션은 Databricks 플랫폼에서 Generative AI를 활용하기 위해 알아야 할 배경지식을 체계적으로 정리합니다.

{% hint style="info" %}
각 가이드는 독립적으로 읽을 수 있지만, LLM 기초 → Agent 아키텍처 → Prompt Engineering 순서로 읽으면 이해가 더 수월합니다.
{% endhint %}

---

## 이 섹션의 목적

Databricks의 GenAI 기능(Mosaic AI, Agent Framework, AI Playground 등)을 제대로 활용하려면, 그 기반이 되는 기술 개념을 이해해야 합니다. 이 섹션에서는 GenAI 핵심 개념을 실무 관점에서 설명합니다.

### 대상 독자

- **SE/SA**: 고객 데모 및 PoC 수행 시 GenAI 배경지식이 필요한 경우
- **파트너 엔지니어**: Databricks 기반 GenAI 솔루션을 설계하는 경우
- **고객 기술 리더**: AI 전략 수립 시 기술 개념을 파악하고 싶은 경우

### 선수 지식

- 기본적인 프로그래밍 경험 (Python 권장)
- Databricks Workspace 접근 및 Notebook 사용 경험
- 머신러닝 기초 개념 (선택사항, 없어도 무방)

---

## 주요 개념 가이드

| 가이드 | 설명 | 난이도 |
|--------|------|--------|
| [LLM 기초](llm-basics.md) | Transformer, 토큰, 컨텍스트 윈도우, Hallucination, 주요 모델 비교 | 입문 |
| [AI Agent 아키텍처](agent-architecture.md) | ReAct, Tool Use (JSON 수준), 멀티에이전트 패턴, 프레임워크 비교 | 중급 |
| [Prompt Engineering](prompt-engineering.md) | Zero-shot/Few-shot/CoT 비교, System Prompt 5패턴, Prompt Injection 방어 | 입문~중급 |
| [GenAI 평가 방법론](evaluation.md) | Faithfulness/Relevance 구체 예시, LLM-as-Judge vs Human, MLflow Evaluate | 중급 |
| [A2A (Agent-to-Agent)](a2a.md) | A2A 등장 배경, Agent Card JSON, Task 라이프사이클, MCP 결합 아키텍처 | 중급~고급 |
| [AI Proficiency 성숙도](ai-proficiency.md) | 4단계 성숙도 모델, 레벨 전환 요건, 자가 진단 체크리스트 | 전략 |

---

## 학습 로드맵: 어디서부터 시작해야 하나?

역할과 목적에 따라 다른 순서로 학습할 수 있습니다.

### 역할별 권장 경로

| 역할 | 권장 순서 | 소요 시간 |
|------|-----------|-----------|
| **GenAI 입문자** | LLM 기초 → Prompt Engineering → 평가 방법론 | 3~4시간 |
| **Agent 개발자** | LLM 기초 → Agent 아키텍처 → A2A → 평가 방법론 | 4~5시간 |
| **기술 리더/전략가** | AI Proficiency → LLM 기초 → Agent 아키텍처 | 2~3시간 |
| **SE/SA (고객 대응)** | 전체 과정 (LLM → Prompt → Agent → 평가 → A2A → AI Proficiency) | 6~8시간 |

### 목적별 권장 경로

| 목적 | 필수 가이드 | 선택 가이드 |
|------|------------|------------|
| "고객에게 GenAI를 설명해야 한다" | LLM 기초, AI Proficiency | Prompt Engineering |
| "RAG 챗봇을 만들어야 한다" | LLM 기초, Prompt Engineering, 평가 방법론 | Agent 아키텍처 |
| "Agent를 설계해야 한다" | LLM 기초, Agent 아키텍처, A2A | 평가 방법론 |
| "AI 전략을 수립해야 한다" | AI Proficiency, LLM 기초 | Agent 아키텍처 |

---

## GenAI 기술 발전 타임라인

| 시기 | 주요 이벤트 | 핵심 키워드 | 영향 |
|------|-------------|-------------|------|
| 2017.06 | Google "Attention Is All You Need" 논문 | Transformer | 현대 LLM의 기반 아키텍처 탄생 |
| 2018.10 | Google BERT 공개 | Pre-training | 사전학습 → 파인튜닝 패러다임 시작 |
| 2020.06 | OpenAI GPT-3 공개 (175B) | Few-shot Learning | 프롬프트만으로 다양한 작업 수행 가능 |
| 2022.11 | ChatGPT 출시 | Conversational AI | GenAI 대중화, 2개월 만에 1억 사용자 |
| 2023.03 | GPT-4 출시 | Multimodal LLM | 이미지 이해, 추론 능력 대폭 향상 |
| 2023.06 | RAG 패턴 확산, Vector DB 부상 | Retrieval-Augmented Generation | 환각 감소, 사내 데이터 활용 |
| 2023.10 | AI Agent 개념 부상 | Agent, Tool Use | LangChain, AutoGen 성장, 도구 사용 LLM |
| 2024.03 | Claude 3 Opus, DBRX 출시 | Open-weight LLM | 오픈소스/오픈웨이트 모델 성능 향상 |
| 2024.04 | Databricks Agent Framework GA | Enterprise Agent | 기업용 Agent 구축/배포 통합 환경 |
| 2024.11 | Anthropic MCP 발표 | Model Context Protocol | LLM-도구 연결 표준화 |
| 2025.01 | DeepSeek R1 공개 | 추론 모델 | 저비용 고성능 추론 모델의 가능성 입증 |
| 2025.04 | Google A2A 프로토콜 발표 | Agent-to-Agent | 이기종 에이전트 간 통신 표준 |
| 2025.H1 | Claude 4, GPT-4.1 출시 | Agentic AI | 코딩/에이전트 특화 모델, Multi-Agent 시스템 본격 도입 |
| 2025.H2 | Multi-Agent 시스템 본격 확산 (예상) | Orchestration | A2A + MCP 결합, 기업용 에이전트 네트워크 |

---

## Databricks GenAI 기능과의 매핑

| GenAI 개념 | Databricks 기능 | 설명 |
|------------|-----------------|------|
| LLM 사용 | AI Playground, Foundation Model APIs | 다양한 모델을 UI/API로 호출 |
| Fine-tuning | Mosaic AI Training | 도메인 특화 모델 학습 |
| RAG | Vector Search, Agent Framework | 문서 검색 → LLM 답변 생성 |
| Agent | Mosaic AI Agent Framework | Agent 구축, 도구 등록, 배포 |
| 평가 | MLflow Evaluate, Review App | 자동 평가 + 인간 피드백 수집 |
| 프롬프트 관리 | MLflow Prompt Registry | 프롬프트 버전 관리, 팀 협업 |
| 배포 | Model Serving, Databricks Apps | 서버리스 배포, 웹 앱 배포 |
| 모니터링 | Lakehouse Monitoring, Inference Tables | 프로덕션 성능 추적, 이상 감지 |
| 거버넌스 | Unity Catalog, AI Guardrails | 접근 제어, 입출력 필터링, 감사 로그 |

---

## GenAI 핵심 용어 사전

| 용어 | 설명 |
|------|------|
| **LLM** | Large Language Model — 대규모 언어 모델. 수십억~수조 개의 파라미터로 학습된 딥러닝 모델 |
| **Transformer** | 현대 LLM의 기반 아키텍처. Self-Attention 메커니즘으로 문맥을 효과적으로 파악 |
| **Token** | LLM이 텍스트를 처리하는 최소 단위. 영어 1토큰 ≈ 0.75단어, 한국어는 더 많은 토큰 사용 |
| **Context Window** | 모델이 한 번에 처리할 수 있는 최대 토큰 수. 입력+출력 합산 |
| **Temperature** | 출력의 무작위성을 조절하는 파라미터. 0=결정적, 1=창의적 |
| **RAG** | Retrieval-Augmented Generation — 외부 문서를 검색하여 LLM에 컨텍스트로 제공하는 패턴 |
| **Agent** | LLM + 도구 사용 + 추론 루프를 결합한 자율 시스템 |
| **ReAct** | Reasoning + Acting — LLM이 추론과 행동을 번갈아 수행하는 패턴 |
| **Tool Use / Function Calling** | LLM이 외부 함수를 호출할 수 있는 기능 |
| **MCP** | Model Context Protocol — LLM과 외부 도구/데이터를 연결하는 표준 (Anthropic, 2024) |
| **A2A** | Agent-to-Agent Protocol — 에이전트 간 통신 표준 (Google, 2025) |
| **Fine-tuning** | 사전 학습된 모델을 특정 도메인 데이터로 추가 학습 |
| **Hallucination** | 모델이 사실이 아닌 내용을 자신있게 생성하는 현상 |
| **Embedding** | 텍스트를 고차원 벡터 공간에 매핑한 수치 표현. 의미적 유사도 계산에 사용 |
| **Vector Search** | 임베딩 벡터의 유사도를 기반으로 관련 문서를 검색하는 기술 |
| **Prompt Injection** | 악의적 입력으로 LLM의 원래 지시를 무시하게 만드는 공격 |
| **Guardrails** | LLM 입출력을 필터링하여 안전성을 확보하는 장치 |
| **LLM-as-Judge** | LLM 출력의 품질을 다른 LLM이 평가하는 패턴 |
| **Inference Table** | 모델 서빙 시 요청/응답을 자동으로 기록하는 Databricks 기능 |
| **MoE** | Mixture of Experts — 전체 파라미터 중 일부만 활성화하는 효율적 아키텍처 |
| **CoT** | Chain-of-Thought — 단계적 추론을 유도하여 정확도를 높이는 프롬프트 기법 |
| **Multi-Agent** | 여러 전문 Agent가 협업하여 복잡한 작업을 수행하는 시스템 |

---

## 참고 자료

- [Databricks Generative AI 공식 문서](https://docs.databricks.com/en/generative-ai/index.html)
- [Mosaic AI Agent Framework](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Google A2A Protocol](https://google.github.io/A2A/)
- [Anthropic MCP](https://modelcontextprotocol.io/)
- [Databricks AI Cookbook](https://docs.databricks.com/en/generative-ai/tutorials/ai-cookbook/index.html)

---

## 다음 단계

1. GenAI가 처음이라면 → [LLM 기초](llm-basics.md)부터 시작
2. Agent 개발에 관심이 있다면 → [AI Agent 아키텍처](agent-architecture.md)
3. 조직 전략을 수립 중이라면 → [AI Proficiency 성숙도](ai-proficiency.md)
4. 실습을 원한다면 → [RAG 가이드](../rag/README.md) 또는 [Agent Bricks](../agent-bricks/README.md)
