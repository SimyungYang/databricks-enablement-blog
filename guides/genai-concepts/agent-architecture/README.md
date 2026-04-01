# AI Agent 아키텍처

AI Agent는 LLM에 도구 사용(Tool Use)과 추론 루프(Reasoning Loop)를 결합하여, 복잡한 작업을 자율적으로 수행하는 시스템입니다.

{% hint style="info" %}
**학습 목표**
- AI Agent와 단순 LLM 호출의 핵심 차이를 설명할 수 있다
- ReAct 패턴의 Thought→Action→Observation 루프를 구체적으로 이해한다
- Tool Use/Function Calling의 동작 방식을 JSON 수준에서 설명할 수 있다
- LangGraph, CrewAI, Databricks Agent Framework의 차이를 코드 수준에서 비교할 수 있다
- Multi-Agent 패턴 3가지(Supervisor, Swarm, 계층형)를 시나리오에 맞게 선택할 수 있다
{% endhint %}

---

## AI Agent란?

AI Agent는 단순 LLM 호출과 다릅니다. 핵심 차이는 **자율적 의사결정**과 **행동 실행** 능력입니다.

{% hint style="success" %}
**비유**: 일반 LLM은 "질문하면 답하는 백과사전"이라면, AI Agent는 "스스로 조사하고, 도구를 사용하고, 결과를 종합하는 리서치 어시스턴트"입니다.
{% endhint %}

| 구분 | 일반 LLM 호출 | AI Agent |
|------|---------------|----------|
| 입력 → 출력 | 1회 호출, 1회 응답 | 다단계 추론 및 행동 반복 |
| 도구 사용 | 없음 | API, DB, 검색 등 도구 호출 |
| 의사결정 | 없음 | 다음 행동을 스스로 결정 |
| 상태 관리 | 없음 | 작업 진행 상태 유지 |
| 오류 처리 | 없음 | 실패 시 대안 전략 수행 |

### Agent의 핵심 구성 요소

```
┌─────────────────────────────────┐
│           AI Agent              │
│                                 │
│  ┌─────────┐  ┌──────────────┐  │
│  │   LLM   │──│ Reasoning    │  │
│  │ (Brain) │  │ Loop (ReAct) │  │
│  └────┬────┘  └──────────────┘  │
│       │                         │
│  ┌────▼────────────────────┐    │
│  │     Tool Use            │    │
│  │  (API, DB, Search, ...) │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

---

## 서브 페이지

| 페이지 | 내용 |
|--------|------|
| [ReAct 패턴 & Planning](react-planning.md) | ReAct 루프 상세, 실패 모드 3가지, Plan-and-Execute 비교, 실전 System Prompt |
| [Tool Use / Function Calling](tool-use.md) | JSON 수준 동작 흐름, Tool Description 노하우, 도구 설계 원칙 7가지 |
| [Agent Memory 시스템](memory.md) | 단기/장기/에피소드/작업 기억 유형별 비교와 Databricks 구현 |
| [Multi-Agent 패턴](multi-agent.md) | Supervisor/Swarm/계층형 패턴, 통신 패턴, 비용 분석, 디버깅 |
| [Agent 프레임워크 비교](frameworks.md) | Databricks, LangGraph, CrewAI, OpenAI, AutoGen 코드 비교 |
| [프로덕션 운영 가이드](production.md) | 안전성, 디버깅, 안티패턴 5가지, PoC 가이드, 고객 FAQ |

---

## 연습 문제

1. ReAct 패턴에서 Thought, Action, Observation 각각의 역할을 자신만의 예시로 설명하세요.
2. Tool Use에서 LLM이 직접 함수를 실행하지 않는 이유는 무엇이며, 이것이 보안에 어떤 이점을 주나요?
3. 고객 지원 챗봇(FAQ 응답 + 주문 조회 + 환불 처리)을 만든다면, Single Agent와 Multi-Agent 중 어떤 구조를 선택하겠습니까? 이유와 함께 설명하세요.
4. Supervisor 패턴과 Swarm 패턴의 핵심 차이를 "회사 조직 구조"에 비유하여 설명하세요.

---

## 흔한 오해 (Common Misconceptions)

Agent를 처음 도입하는 팀이 빠지기 쉬운 대표적 오해 3가지입니다. 이 오해를 피하는 것만으로도 PoC 성공률이 크게 높아집니다.

| 오해 | 사실 |
|------|------|
| "Agent는 항상 Single Agent보다 Multi-Agent가 낫다" | 단순한 작업에 Multi-Agent를 사용하면 오히려 지연시간, 비용, 오류율이 증가합니다. Single Agent로 충분한지 먼저 검증하세요. |
| "도구를 많이 줄수록 Agent가 강력해진다" | 도구가 10~15개를 넘으면 LLM이 적합한 도구를 선택하는 정확도가 떨어집니다. 도구 설명(description)의 품질이 더 중요합니다. |
| "Agent가 스스로 학습하고 진화한다" | 현재 대부분의 Agent는 매 세션마다 새로 시작합니다. 장기 메모리와 자가 개선은 별도로 구현해야 합니다. |

---

## 참고 자료

- [Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022)](https://arxiv.org/abs/2210.03629)
- [Databricks Agent Framework 문서](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [CrewAI 문서](https://docs.crewai.com/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [AutoGen 문서](https://microsoft.github.io/autogen/)
