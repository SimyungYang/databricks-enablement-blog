# GenAI 핵심 개념 총정리

이 섹션은 Databricks 플랫폼에서 Generative AI를 활용하기 위해 알아야 할 배경지식을 체계적으로 정리합니다.

{% hint style="info" %}
각 가이드는 독립적으로 읽을 수 있지만, LLM 기초 → Agent 아키텍처 → Prompt Engineering 순서로 읽으면 이해가 더 수월합니다.
{% endhint %}

---

## 이 섹션의 목적

Databricks의 GenAI 기능(Mosaic AI, Agent Framework, AI Playground 등)을 제대로 활용하려면, 그 기반이 되는 기술 개념을 이해해야 합니다. 이 섹션에서는 GenAI 핵심 개념을 실무 관점에서 설명합니다.

---

## 주요 개념 가이드

| 가이드 | 설명 | 난이도 |
|--------|------|--------|
| [LLM 기초](llm-basics.md) | Transformer, 토큰, 컨텍스트 윈도우, 주요 모델 비교 | 입문 |
| [AI Agent 아키텍처](agent-architecture.md) | ReAct, Tool Use, 멀티에이전트 패턴 | 중급 |
| [Prompt Engineering](prompt-engineering.md) | Zero-shot, CoT, System Prompt, Databricks 활용 | 입문~중급 |
| [GenAI 평가 방법론](evaluation.md) | Faithfulness, LLM-as-Judge, MLflow Evaluate | 중급 |
| [A2A (Agent-to-Agent)](a2a.md) | Google A2A 프로토콜, MCP 비교, 멀티에이전트 통신 | 중급~고급 |
| [AI Proficiency 성숙도](ai-proficiency.md) | 조직 AI 성숙도 모델, 단계별 Databricks 활용 | 전략 |

---

## GenAI 기술 발전 타임라인

| 시기 | 주요 이벤트 | 핵심 키워드 |
|------|-------------|-------------|
| 2017 | Google "Attention Is All You Need" 논문 발표 | Transformer |
| 2020 | GPT-3 공개, Few-shot 학습 가능성 입증 | Large Language Model |
| 2022.11 | ChatGPT 출시, GenAI 대중화 | Conversational AI |
| 2023.03 | GPT-4 출시, 멀티모달 지원 | Multimodal LLM |
| 2023.06 | RAG 패턴 확산, Vector DB 부상 | Retrieval-Augmented Generation |
| 2023.10 | AI Agent 개념 부상, LangChain/AutoGen 성장 | Agent, Tool Use |
| 2024.03 | Claude 3 Opus, DBRX 출시 | Open-weight LLM |
| 2024.04 | Databricks Agent Framework GA | Enterprise Agent |
| 2024.11 | Anthropic MCP 발표 | Model Context Protocol |
| 2025.04 | Google A2A 프로토콜 발표 | Agent-to-Agent |
| 2025.H1 | Multi-Agent 시스템 본격 도입 | Agentic AI, Orchestration |

---

## Databricks GenAI 기능과의 매핑

| GenAI 개념 | Databricks 기능 |
|------------|-----------------|
| LLM 사용 | AI Playground, Foundation Model APIs |
| Fine-tuning | Mosaic AI Training |
| RAG | Vector Search, Agent Framework |
| Agent | Mosaic AI Agent Framework |
| 평가 | MLflow Evaluate, Review App |
| 프롬프트 관리 | MLflow Prompt Registry |
| 배포 | Model Serving, Databricks Apps |
| 모니터링 | Lakehouse Monitoring, Inference Tables |

---

## 참고 자료

- [Databricks Generative AI 공식 문서](https://docs.databricks.com/en/generative-ai/index.html)
- [Mosaic AI Agent Framework](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Google A2A Protocol](https://google.github.io/A2A/)
- [Anthropic MCP](https://modelcontextprotocol.io/)

---

## 다음 단계

1. GenAI가 처음이라면 → [LLM 기초](llm-basics.md)부터 시작
2. Agent 개발에 관심이 있다면 → [AI Agent 아키텍처](agent-architecture.md)
3. 조직 전략을 수립 중이라면 → [AI Proficiency 성숙도](ai-proficiency.md)
4. 실습을 원한다면 → [RAG 가이드](../rag/README.md) 또는 [Agent Bricks](../agent-bricks/README.md)
