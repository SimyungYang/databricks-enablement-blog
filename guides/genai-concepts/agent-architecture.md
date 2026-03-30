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

## ReAct 패턴 (Reasoning + Acting)

ReAct는 2022년 Yao et al.이 제안한 패턴으로, LLM이 **추론(Reasoning)**과 **행동(Acting)**을 번갈아 수행합니다.

### ReAct 루프 상세 예시

사용자 질문: **"지난 분기 매출이 가장 높은 제품 3개와 그 이유를 분석해주세요"**

| 단계 | 내용 |
|------|------|
| **Thought 1** | 매출 데이터를 DB에서 조회해야 합니다. SQL을 실행하겠습니다. |
| **Action 1** | `query_sql("SELECT product_name, SUM(revenue) as total FROM sales WHERE quarter='2025Q4' GROUP BY product_name ORDER BY total DESC LIMIT 3")` |
| **Observation 1** | 결과: [{"product_name": "Pro Plan", "total": 12억}, {"product_name": "Enterprise", "total": 9.5억}, {"product_name": "Starter", "total": 7.2억}] |
| **Thought 2** | 상위 3개 제품을 확인했습니다. 이유를 분석하려면 마케팅 캠페인 데이터도 확인해야 합니다. |
| **Action 2** | `search_documents("2025 Q4 마케팅 캠페인 결과 보고서")` |
| **Observation 2** | 문서 발견: "Pro Plan 할인 프로모션(11월), Enterprise 대기업 계약 3건 체결..." |
| **Thought 3** | 매출 데이터와 마케팅 정보를 종합하여 분석 보고서를 작성할 수 있습니다. |
| **Answer** | 최종 분석 보고서 생성 |

{% hint style="warning" %}
ReAct 루프가 무한히 반복되지 않도록 **최대 반복 횟수**(보통 5~15회)와 **타임아웃**을 반드시 설정하세요.
{% endhint %}

---

## Tool Use / Function Calling

Tool Use는 LLM이 외부 도구(함수)를 호출할 수 있는 기능입니다. LLM이 직접 코드를 실행하는 것이 아니라, **"어떤 함수를 어떤 인자로 호출할지"를 JSON으로 결정**하고, 시스템이 실제 실행합니다.

### 동작 흐름 (JSON 수준)

**1단계: 사용자 질문**
```json
{"role": "user", "content": "서울 날씨 알려줘"}
```

**2단계: LLM이 도구 호출을 결정** (LLM이 생성하는 JSON)
```json
{
  "tool_calls": [{
    "function": {
      "name": "get_weather",
      "arguments": "{\"city\": \"Seoul\", \"unit\": \"celsius\"}"
    }
  }]
}
```

**3단계: 시스템이 함수 실행 후 결과 반환**
```json
{"role": "tool", "content": "{\"temperature\": 22, \"condition\": \"맑음\", \"humidity\": 45}"}
```

**4단계: LLM이 결과를 해석하여 최종 응답**
```json
{"role": "assistant", "content": "서울은 현재 22도이고 맑은 날씨입니다. 습도는 45%입니다."}
```

### 도구 정의 예시 (Databricks Agent Framework)

```python
from databricks.sdk import WorkspaceClient

# Unity Catalog Function을 도구로 등록
tools = [
    {"function_name": "catalog.schema.search_documents"},
    {"function_name": "catalog.schema.get_customer_info"},
    {"function_name": "catalog.schema.execute_sql_query"},
]
```

{% hint style="info" %}
**핵심 포인트**: LLM은 함수를 직접 실행하지 않습니다. "어떤 함수를 호출할지"를 결정할 뿐이고, 실제 실행은 Agent Framework가 담당합니다. 이 분리가 보안과 제어의 핵심입니다.
{% endhint %}

---

## Agent 프레임워크 비교

| 프레임워크 | 개발사 | 특징 | Databricks 통합 |
|-----------|--------|------|-----------------|
| **Databricks Agent Framework** | Databricks | Unity Catalog 통합, MLflow 추적, 원클릭 배포 | 네이티브 |
| **LangChain / LangGraph** | LangChain Inc. | 가장 큰 생태계, 유연한 그래프 구성 | MLflow 통합 |
| **CrewAI** | CrewAI | 역할 기반 멀티에이전트, 직관적 API | MLflow 로깅 |
| **AutoGen** | Microsoft | 멀티에이전트 대화, 코드 실행 | 커스텀 통합 |
| **OpenAI Agents SDK** | OpenAI | Handoff 패턴, Guardrail 내장 | 커스텀 통합 |

### Databricks Agent Framework (ChatAgent 패턴)

```python
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import (
    ChatAgentMessage,
    ChatAgentResponse,
    ChatContext,
)

class MyAgent(ChatAgent):
    def predict(
        self,
        messages: list[ChatAgentMessage],
        context: ChatContext
    ) -> ChatAgentResponse:
        # 1. 메시지 분석
        # 2. 도구 호출 결정
        # 3. 결과 종합 및 응답 생성
        return ChatAgentResponse(
            messages=[ChatAgentMessage(role="assistant", content="...")]
        )
```

### LangGraph (StateGraph 패턴)

```python
from langgraph.graph import StateGraph, START, END

# 상태 정의
class AgentState(TypedDict):
    messages: list
    next_action: str

# 노드 정의 (각 처리 단계)
def analyze_query(state: AgentState):
    # LLM으로 사용자 의도 분석
    ...

def execute_tool(state: AgentState):
    # 도구 실행
    ...

# 그래프 구성 (노드 + 엣지)
graph = StateGraph(AgentState)
graph.add_node("analyze", analyze_query)
graph.add_node("execute", execute_tool)
graph.add_edge(START, "analyze")
graph.add_conditional_edges("analyze", route_decision)
graph.add_edge("execute", END)

agent = graph.compile()
```

### CrewAI (Agent-Task-Crew 패턴)

```python
from crewai import Agent, Task, Crew

# 에이전트 정의 (역할/목표/배경)
researcher = Agent(
    role="데이터 분석가",
    goal="매출 데이터를 분석하여 인사이트 도출",
    backstory="10년 경력의 비즈니스 인텔리전스 전문가",
)

# 태스크 정의 (설명/기대출력/담당 에이전트)
analysis_task = Task(
    description="지난 분기 매출 트렌드를 분석하세요",
    expected_output="트렌드 요약 보고서 (Markdown)",
    agent=researcher,
)

# 크루 구성 및 실행
crew = Crew(agents=[researcher], tasks=[analysis_task])
result = crew.kickoff()
```

{% hint style="success" %}
**Databricks 환경 권장**: Databricks Agent Framework(ChatAgent)를 기본으로 사용하고, 복잡한 워크플로우가 필요한 경우 LangGraph를 MLflow와 함께 활용하세요.
{% endhint %}

---

## Single Agent vs Multi-Agent

### Single Agent

하나의 LLM이 모든 도구와 추론을 담당합니다.

- **장점**: 단순, 디버깅 쉬움, 지연시간 낮음
- **단점**: 복잡한 작업에서 정확도 저하, 도구 수 제한 (보통 10~15개 이상이면 성능 저하)
- **적합**: FAQ 봇, 문서 검색, 단순 데이터 조회

### Multi-Agent

여러 전문 Agent가 협업하여 복잡한 작업을 수행합니다.

- **장점**: 역할 분담으로 정확도 향상, 확장 가능
- **단점**: 복잡도 증가, 에이전트 간 통신 오버헤드, 디버깅 난이도 상승
- **적합**: 복합 분석, 크로스 도메인 질의, 자동화 워크플로우

---

## Multi-Agent 아키텍처 패턴

### 패턴 비교 요약

| 항목 | Supervisor 패턴 | Swarm 패턴 | 계층형 패턴 |
|------|----------------|------------|------------|
| **구조** | 중앙 컨트롤러가 분배 | 에이전트 간 직접 핸드오프 | 다계층 Supervisor 트리 |
| **의사결정** | Supervisor가 결정 | 각 Agent가 자율 결정 | 각 레벨 Supervisor가 결정 |
| **확장성** | Worker 추가 용이 | 에이전트 추가 용이 | 팀 단위 확장 |
| **디버깅** | 중앙 로그로 추적 용이 | 핸드오프 추적 필요 | 계층별 추적 |
| **적합 시나리오** | 5~10개 Worker | 순차적 전문가 릴레이 | 대규모 조직 (팀별 에이전트) |
| **대표 구현** | Databricks Agent Bricks | OpenAI Agents SDK Handoff | LangGraph 중첩 그래프 |

### 1. Supervisor 패턴

```
         사용자 요청
              │
       ┌──────▼──────┐
       │  Supervisor  │ ← 작업 분석, 분배, 결과 종합
       │   Agent      │
       └──┬───┬───┬───┘
          │   │   │
     ┌────▼┐ ┌▼───┐ ┌▼────┐
     │검색  │ │SQL │ │요약  │
     │Agent│ │Agent│ │Agent│
     └─────┘ └────┘ └─────┘
```

Supervisor가 사용자 요청을 분석하고, 적합한 Worker에게 하위 작업을 위임합니다. Databricks Agent Bricks의 Supervisor Agent가 이 패턴을 사용합니다.

### 2. Swarm 패턴

```
사용자 요청 → [접수 Agent] ──handoff──→ [분석 Agent] ──handoff──→ [보고서 Agent] → 최종 응답
                                              │
                                         (필요시)
                                              │
                                        [데이터 Agent]
```

중앙 관리자 없이 Agent들이 **Handoff** 방식으로 작업을 전달합니다.

- Agent A가 작업 중 자신의 범위를 벗어나면 Agent B에게 전달
- 각 Agent가 자율적으로 다음 Agent를 결정
- OpenAI Agents SDK의 Handoff가 이 패턴의 대표 구현

### 3. 계층형 패턴

```
              ┌─────────────┐
              │ Top-level   │
              │ Supervisor  │
              └──┬───────┬──┘
          ┌──────▼──┐  ┌─▼────────┐
          │ 데이터팀 │  │ 보고서팀  │
          │ Sub-Sup │  │ Sub-Sup  │
          └──┬───┬──┘  └──┬───┬───┘
          ┌──▼┐ ┌▼──┐  ┌──▼┐ ┌▼──┐
          │SQL│ │ETL│  │차트│ │문서│
          └───┘ └───┘  └───┘ └───┘
```

Supervisor 패턴을 다층으로 확장하여, Sub-Supervisor가 하위 Agent 그룹을 관리합니다. 대규모 조직에서 팀별 전문 에이전트 그룹을 구성할 때 적합합니다.

---

## Databricks Agent Framework 활용

| 기능 | 설명 |
|------|------|
| **UC Functions as Tools** | Unity Catalog 함수를 Agent 도구로 등록 |
| **Vector Search** | RAG를 위한 벡터 검색 통합 |
| **MLflow Tracing** | Agent 실행 과정 전체 추적 (각 Tool Call, LLM 호출 기록) |
| **Review App** | 인간 피드백 수집 인터페이스 |
| **Model Serving** | 원클릭 Agent 배포 (서버리스) |
| **Guardrails** | 입출력 안전성 필터링 |
| **Agent Evaluation** | MLflow Evaluate로 Agent 품질 자동 측정 |

---

## 흔한 오해 (Common Misconceptions)

| 오해 | 사실 |
|------|------|
| "Agent는 항상 Single Agent보다 Multi-Agent가 낫다" | 단순한 작업에 Multi-Agent를 사용하면 오히려 지연시간, 비용, 오류율이 증가합니다. Single Agent로 충분한지 먼저 검증하세요. |
| "도구를 많이 줄수록 Agent가 강력해진다" | 도구가 10~15개를 넘으면 LLM이 적합한 도구를 선택하는 정확도가 떨어집니다. 도구 설명(description)의 품질이 더 중요합니다. |
| "Agent가 스스로 학습하고 진화한다" | 현재 대부분의 Agent는 매 세션마다 새로 시작합니다. 장기 메모리와 자가 개선은 별도로 구현해야 합니다. |

---

## 연습 문제

1. ReAct 패턴에서 Thought, Action, Observation 각각의 역할을 자신만의 예시로 설명하세요.
2. Tool Use에서 LLM이 직접 함수를 실행하지 않는 이유는 무엇이며, 이것이 보안에 어떤 이점을 주나요?
3. 고객 지원 챗봇(FAQ 응답 + 주문 조회 + 환불 처리)을 만든다면, Single Agent와 Multi-Agent 중 어떤 구조를 선택하겠습니까? 이유와 함께 설명하세요.
4. Supervisor 패턴과 Swarm 패턴의 핵심 차이를 "회사 조직 구조"에 비유하여 설명하세요.

---

## 참고 자료

- [Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022)](https://arxiv.org/abs/2210.03629)
- [Databricks Agent Framework 문서](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [CrewAI 문서](https://docs.crewai.com/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [AutoGen 문서](https://microsoft.github.io/autogen/)
