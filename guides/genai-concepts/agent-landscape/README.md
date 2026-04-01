# AI Agent 업계 동향 (2024\~2025)

2024년 하반기부터 2025년 상반기까지, AI 업계의 중심 화두는 "**Agent**"로 수렴했다. 단순 챗봇을 넘어 도구를 사용하고, 계획을 세우고, 자율적으로 실행하는 AI Agent가 모든 주요 벤더의 제품 로드맵 최상단에 올랐다. 이 섹션에서는 OpenAI, Anthropic, Google, AWS, Microsoft, Meta 등 주요 기업의 Agent 전략을 비교 분석하고, Databricks 환경에서의 전략적 포지셔닝을 이해한다.

---

## 학습 목표

이 섹션을 완료하면 다음을 수행할 수 있다:

* 주요 AI 기업의 **Agent 전략과 제품 포트폴리오** 를 이해한다
* 각 벤더의 **Agent 아키텍처 접근 방식 차이** 를 비교할 수 있다
* ** 멀티에이전트 오케스트레이션** 트렌드와 ** 표준화 동향**(MCP, A2A)을 파악한다
* Databricks 환경에서의 ** 전략적 포지셔닝** 을 이해한다

---

## 왜 Agent 업계 동향을 알아야 하는가?

{% hint style="info" %}
**SA/CE 필수 역량**: 고객이 _"OpenAI도 Agent 플랫폼 있고, Google ADK도 있고, AWS Bedrock Agents도 있는데... Databricks Agent Framework를 왜 써야 하나요?"_ 라고 물을 때, 명확한 근거와 차별점을 제시할 수 있어야 한다.
{% endhint %}

### 실무적 필요성

1. ** 고객 대응력**: 각 벤더의 강점과 약점을 이해해야 올바른 아키텍처를 제안할 수 있다. "우리 고객은 이미 Azure를 쓰고 있으니 Copilot Studio가 맞지 않을까?"라는 질문에 데이터 플랫폼 관점의 차별화된 답변이 필요하다.

2. ** 기술 의사결정 지원**: Agent 표준(MCP, A2A)의 수렴 방향을 파악하면, 고객의 장기 아키텍처 설계를 도울 수 있다. 6개월 후 어떤 표준이 살아남을지 예측하는 것이 아니라, ** 어떤 표준에 베팅하더라도 리스크가 최소화되는 아키텍처** 를 설계하는 것이 핵심이다.

3. ** 경쟁 인텔리전스**: 고객 미팅에서 경쟁사 제품이 언급될 때, 표면적 기능 비교가 아닌 ** 아키텍처 철학 수준의 차이** 를 설명할 수 있어야 신뢰를 얻는다.

{% hint style="warning" %}
** 주의**: 이 문서의 정보는 2025년 상반기 기준이다. AI Agent 시장은 분기 단위로 급변하므로, 특정 제품의 GA 여부나 가격 정책은 반드시 최신 공식 문서를 확인해야 한다.
{% endhint %}

---

## 전체 시장 스냅샷 (2025)

| 지표 | 수치 |
| --- | --- |
| 2025년 Agentic AI 시장 규모 | **\~$7.6B**|
| 2030년 예상 시장 규모 | **$52\~100B**(CAGR 46%) |
| Enterprise AI Agent 도입율 | **40%**(2026년 예상, Gartner) |
| 2028년 자율 의사결정 비율 | **15%**(Gartner) |

{% hint style="info" %}
** 시장 해석**: 2025년 $7.6B에서 2030년 최대 $100B까지 성장한다는 것은, 현재 시장이 아직 ** 극초기 단계** 라는 의미다. 즉, 지금 Agent 아키텍처를 올바르게 설계하면 고객에게 5년간 유효한 플랫폼 전략을 제공할 수 있다. 반대로 특정 벤더에 lock-in되면 전환 비용이 매우 크다.
{% endhint %}

---

## 벤더별 Agent 전략 한눈에 비교

| 벤더 | Agent 플랫폼 | 핵심 모델 | 멀티에이전트 | 핵심 차별점 | 오픈소스 |
| --- | --- | --- | --- | --- | --- |
| **OpenAI**| Agents SDK + Responses API | GPT-4.1, o3, GPT-5.2 | Handoff 패턴 | Consumer + Developer 이중 전략, Codex | SDK만 |
| **Anthropic**| Agent SDK + MCP | Claude 4 Opus/Sonnet | Orchestrator-Workers | MCP 표준화(AAIF), Computer Use, 7시간 자율 운영 | MCP, SDK |
| **Google**| ADK + Vertex AI Agent Builder | Gemini 2.5 Pro | A2A + ADK 패턴 | Full-stack (모델 → 프레임워크 → 배포 → 프로토콜), Jules | ADK |
| **AWS**| Bedrock Agents + AgentCore | Nova 2, 타사 모델 | Supervisor/Routing | 프로덕션 인프라, 프레임워크 무관, Guardrails | Strands SDK |
| **Microsoft**| Azure AI Foundry + Copilot Studio | GPT-4o, 타사 모델 | A2A + MCP | M365 통합, 오픈 프로토콜 우선 | AutoGen + SK |
| **Meta**| Llama Stack | Llama 4 | 커뮤니티 | 오픈웨이트, 10M 컨텍스트 | Llama, Stack |
| **Databricks**| Agent Bricks + Mosaic AI | 다중 모델 | Supervisor Agent | 데이터 네이티브 자동 최적화, Unity Catalog 거버넌스 | MLflow |

### 핵심 인사이트

{% hint style="info" %}
** 패턴 분석**: 벤더별 전략을 관통하는 3가지 축이 있다.

1. ** 수직 통합 vs 수평 개방**: OpenAI/Google은 모델부터 배포까지 수직 통합, AWS/Databricks는 모델 중립적 수평 플랫폼
2. **Consumer vs Enterprise**: OpenAI는 ChatGPT로 Consumer 시장을 장악한 뒤 Enterprise로 확장, Databricks/AWS는 Enterprise-first
3. ** 프로토콜 주도 vs 플랫폼 주도**: Anthropic은 MCP로 생태계를 만들고, Google은 A2A로, Microsoft는 둘 다 수용하는 전략
{% endhint %}

---

## Agent 기술 표준화 동향

2025년 상반기 기준, Agent 생태계의 ** 상호운용성(interoperability)** 을 위한 두 가지 핵심 프로토콜이 빠르게 수렴하고 있다.

### MCP (Model Context Protocol)

* ** 주도**: Anthropic이 창안 → **AAIF (Agentic AI Foundation, Linux Foundation 산하)** 로 이관
* ** 역할**: Agent와 Tool/Data Source 간 연결 표준 (수직 통합)
* ** 채택 현황**: 사실상 업계 표준. OpenAI, Google, Microsoft, AWS, Databricks 모두 지원
* ** 핵심 가치**: 한 번 MCP 서버를 구현하면 모든 MCP 클라이언트에서 재사용 가능

### A2A (Agent-to-Agent Protocol)

* ** 주도**: Google이 창안 → **Linux Foundation** 기증
* ** 역할**: Agent와 Agent 간 통신 표준 (수평 통합)
* ** 채택 현황**: Google Cloud 중심 활용. Microsoft, Salesforce 등 지원 표명
* ** 핵심 가치**: 서로 다른 벤더/프레임워크로 만든 Agent끼리 협업 가능

### AAIF (Agentic AI Foundation)

* ** 조직**: Linux Foundation 산하, Anthropic + OpenAI + Block 공동 설립
* ** 목표**: MCP를 벤더 중립적 거버넌스 아래 발전시키는 것
* ** 의미**: Anthropic이 MCP의 "소유권"을 포기함으로써 업계 표준으로서의 신뢰성을 확보

### 상호보완 관계

```
┌─────────────────────────────────────────────────┐
│              Agentic AI System                   │
│                                                  │
│   ┌──────────┐   A2A Protocol   ┌──────────┐   │
│   │ Agent A  │◄────────────────►│ Agent B  │   │
│   └────┬─────┘   (수평: Agent   └────┬─────┘   │
│        │          ↔ Agent)           │          │
│        │ MCP                         │ MCP      │
│        │ (수직:                      │ (수직:   │
│        │ Agent→Tool)                 │ Agent    │
│        ▼                             ▼ →Tool)   │
│   ┌──────────┐                 ┌──────────┐    │
│   │ Tool/DB  │                 │ API/SaaS │    │
│   └──────────┘                 └──────────┘    │
└─────────────────────────────────────────────────┘

MCP = 수직 연결 (Agent가 Tool을 사용)
A2A = 수평 연결 (Agent끼리 협업)
→ 두 프로토콜은 경쟁이 아닌 상호보완 관계
```

{% hint style="warning" %}
** 실무 가이드**: 현재 시점에서 **MCP는 필수 도입**, A2A는 ** 선택적 도입** 이 권장된다. MCP는 이미 모든 주요 벤더가 지원하며 생태계가 성숙한 반면, A2A는 아직 초기 단계로 프로덕션 사례가 제한적이다.
{% endhint %}

---

## "Agentic AI" vs "AI Agent" 용어 정리

이 두 용어는 혼용되지만, 정확한 의미 차이가 있다.

| 구분 | AI Agent | Agentic AI |
| --- | --- | --- |
| ** 정의**| 특정 작업을 수행하는 ** 개별 구성 요소**| 여러 Agent를 계획/조율/실행하는 ** 상위 시스템**|
| ** 비유**| 직원 (Specialist) | 팀/조직 (Organization) |
| ** 예시**| "이메일 초안을 작성하는 Agent" | "고객 문의를 분류하고, 적절한 Agent에 라우팅하고, 결과를 검증하는 시스템" |
| ** 핵심 속성**| Tool 사용, 반복 실행, 자율성 | 계획(Planning), 오케스트레이션, 메모리, 안전성 |
| **Databricks 대응**| Knowledge Assistant, Genie Agent | Supervisor Agent, Agent Bricks 전체 |

{% hint style="info" %}
** 실전 팁**: 고객 미팅에서 "Agent"라는 단어가 나올 때, 고객이 의미하는 것이 ** 단일 챗봇 수준** 인지 ** 멀티에이전트 오케스트레이션** 인지를 먼저 확인하라. 이 구분에 따라 제안 아키텍처가 완전히 달라진다.
{% endhint %}

---

## 서브 페이지 안내

각 벤더/주제별 심층 분석은 다음 서브 페이지에서 다룬다:

| 가이드 | 내용 |
| --- | --- |
| [OpenAI](openai.md) | Agents SDK, Responses API, GPT-4.1, Codex, Operator, Deep Research |
| [Anthropic](anthropic.md) | Claude Code, MCP/AAIF, Agent SDK, Computer Use, 멀티에이전트 패턴 |
| [Google](google.md) | ADK, Vertex AI Agent Builder, Gemini 2.5, A2A, Jules, Mariner, Astra |
| [AWS, Microsoft & Meta](aws-others.md) | Bedrock Agents, AgentCore, Copilot Studio, Llama 4 |
| [Databricks](databricks.md) | Agent Bricks, TAO/ALHF, Supervisor Agent, Gateway, MLflow 3.0 |
| [멀티에이전트 트렌드](multi-agent-trends.md) | 오케스트레이션 패턴, Observability, 메모리, 안전성, Vibe Coding |

---

## 다음 단계

이 섹션의 벤더별 분석을 마친 후, 다음 개념 가이드에서 기술적 깊이를 더할 수 있다:

* [AI Agent 아키텍처](../agent-architecture/README.md) — ReAct, Planning, Tool Use 등 Agent의 내부 동작 원리
* [Agent 프레임워크 생태계](../agent-frameworks.md) — LangGraph, CrewAI, AutoGen 등 실제 구현 프레임워크 비교
* [A2A (Agent-to-Agent)](../a2a.md) — A2A 프로토콜의 기술 상세와 구현 가이드
