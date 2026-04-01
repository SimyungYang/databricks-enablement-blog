# Agent 프레임워크 비교

[← AI Agent 아키텍처 개요](README.md)

---

## 프레임워크 비교 요약

| 프레임워크 | 개발사 | 특징 | Databricks 통합 |
|-----------|--------|------|-----------------|
| **Databricks Agent Framework**| Databricks | Unity Catalog 통합, MLflow 추적, 원클릭 배포 | 네이티브 |
| **LangChain / LangGraph**| LangChain Inc. | 가장 큰 생태계, 유연한 그래프 구성 | MLflow 통합 |
| **CrewAI**| CrewAI | 역할 기반 멀티에이전트, 직관적 API | MLflow 로깅 |
| **AutoGen**| Microsoft | 멀티에이전트 대화, 코드 실행 | 커스텀 통합 |
| **OpenAI Agents SDK**| OpenAI | Handoff 패턴, Guardrail 내장 | 커스텀 통합 |

---

## Databricks Agent Framework (ChatAgent 패턴)

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

---

## LangGraph (StateGraph 패턴)

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

---

## CrewAI (Agent-Task-Crew 패턴)

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

## Databricks Agent Framework 활용

| 기능 | 설명 |
|------|------|
| **UC Functions as Tools**| Unity Catalog 함수를 Agent 도구로 등록 |
| **Vector Search**| RAG를 위한 벡터 검색 통합 |
| **MLflow Tracing**| Agent 실행 과정 전체 추적 (각 Tool Call, LLM 호출 기록) |
| **Review App**| 인간 피드백 수집 인터페이스 |
| **Model Serving**| 원클릭 Agent 배포 (서버리스) |
| **Guardrails**| 입출력 안전성 필터링 |
| **Agent Evaluation**| MLflow Evaluate로 Agent 품질 자동 측정 |

---

[다음: 프로덕션 운영 가이드 →](production.md)
