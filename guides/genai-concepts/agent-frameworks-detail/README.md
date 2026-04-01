# AI Agent 프레임워크 생태계

AI Agent를 구축하기 위한 프레임워크는 2023년 이후 폭발적으로 증가했습니다. 이 가이드는 주요 프레임워크의 설계 철학, 아키텍처, 코드 수준의 차이를 비교하고, 프로젝트 요구사항에 맞는 최적의 선택을 돕습니다.

{% hint style="info" %}
**학습 목표**
- 주요 Agent 프레임워크의 설계 철학과 아키텍처 차이를 이해한다
- LangChain에서 LangGraph로의 진화 과정과 그 이유를 설명할 수 있다
- 프로젝트 요구사항에 맞는 프레임워크를 선택할 수 있다
- Databricks Agent Framework와 오픈소스 프레임워크의 역할 분담을 이해한다
{% endhint %}

---

## 서브 페이지 구성

| 페이지 | 설명 |
|--------|------|
| [LangChain & LangGraph](langchain-langgraph.md) | LangChain의 LCEL, LangGraph의 StateGraph, Checkpoint, 코드 예시 및 비교 |
| [CrewAI, OpenAI Agents SDK & AutoGen](crewai-openai-autogen.md) | CrewAI 역할 기반 멀티에이전트, OpenAI Handoff 패턴, AutoGen 대화 기반 협업 |
| [Databricks Agent Framework](databricks-af.md) | ChatAgent 인터페이스, UC Functions as Tools, MLflow 통합, LangGraph 조합 |
| [종합 비교 & 선택 가이드](comparison.md) | 전체 비교 테이블, 의사결정 트리, Agent UI 개요, 2025 트렌드, 고객 FAQ, 연습문제 |

---

## Agent 프레임워크의 진화 -- 왜 이렇게 많은가?

Agent 프레임워크의 역사는 "**LLM을 어떻게 실용적으로 쓸 것인가**"에 대한 답을 찾아가는 과정입니다. 각 프레임워크는 이전 세대의 한계를 해결하기 위해 등장했습니다.

{% hint style="success" %}
** 비유**: 웹 프레임워크의 역사와 유사합니다. jQuery(단순 DOM 조작) -> Angular(구조화) -> React(컴포넌트 기반) -> Next.js(풀스택)로 진화한 것처럼, Agent 프레임워크도 단순 체인에서 그래프 기반, 멀티에이전트, 엔터프라이즈 플랫폼으로 진화하고 있습니다.
{% endhint %}

### 타임라인

| 시기 | 주요 이벤트 | 의미 |
|------|------------|------|
| 2022.11 | ChatGPT 출시 | LLM 대중화의 시작 |
| 2022.12 | ReAct 논문 발표 (Yao et al.) | Agent 패턴의 이론적 기반 |
| 2023.03 | LangChain 0.0.1 릴리스 | 최초의 범용 LLM 프레임워크 |
| 2023.06 | OpenAI Function Calling 출시 | Tool Use의 표준화 |
| 2023.10 | AutoGen (Microsoft) 공개 | 멀티에이전트 대화 패러다임 |
| 2024.01 | LangGraph 정식 출시 | 그래프 기반 워크플로의 등장 |
| 2024.02 | CrewAI 인기 급상승 | 역할 기반 멀티에이전트 간소화 |
| 2024.06 | Databricks Agent Framework 출시 | 엔터프라이즈 Agent 거버넌스 |
| 2024.11 | Anthropic MCP 표준 발표 | 도구 접근 프로토콜 표준화 |
| 2025.01 | OpenAI Agents SDK 출시 | 핸드오프 패턴 + 가드레일 내장 |
| 2025.03 | Google A2A 프로토콜 발표 | Agent 간 통신 표준화 |
| 2025.Q1 | 프레임워크 수렴 시작 | LangGraph + Databricks 조합이 엔터프라이즈 표준으로 부상 |

### 왜 하나의 프레임워크로 통일되지 않는가?

각 프레임워크는 서로 다른 문제를 해결합니다.

| 문제 영역 | 적합한 프레임워크 |
|-----------|-----------------|
| LLM 호출 추상화 + 빠른 프로토타이핑 | LangChain |
| 복잡한 워크플로 (조건 분기, 루프, 상태 관리) | LangGraph |
| 역할 기반 멀티에이전트 협업 | CrewAI |
| 에이전트 간 대화 기반 문제 해결 | AutoGen |
| OpenAI 생태계 내 프로덕션 Agent | OpenAI Agents SDK |
| 엔터프라이즈 거버넌스 + 배포 + 모니터링 | Databricks Agent Framework |

---

다음 페이지: [LangChain & LangGraph](langchain-langgraph.md)
