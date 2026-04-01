# LangChain & LangGraph

LangChain은 최초의 범용 LLM 프레임워크이며, LangGraph는 그 한계를 극복한 차세대 그래프 기반 프레임워크입니다. 이 페이지에서는 두 프레임워크의 핵심 개념, 코드 예시, 비교를 다룹니다.

---

## LangChain -- Agent 프레임워크의 원조

LangChain은 2023년 초 Harrison Chase가 만든, LLM 애플리케이션 구축을 위한 최초의 범용 프레임워크입니다. "LLM 호출을 레고 블록처럼 연결한다"는 아이디어에서 출발했습니다.

### 핵심 컴포넌트

| 컴포넌트 | 역할 | 비유 |
|----------|------|------|
| **Chain** | 여러 단계를 순서대로 연결 | 공장의 컨베이어 벨트 |
| **Agent** | LLM이 다음 행동을 스스로 결정 | 자율적인 작업자 |
| **Tools** | 외부 API, DB, 검색 등 호출 | 작업자의 도구 상자 |
| **Memory** | 대화 히스토리 유지 | 작업자의 메모장 |
| **Retriever** | 벡터 DB에서 관련 문서 검색 | 도서관 사서 |

### LangChain Expression Language (LCEL)

LCEL은 LangChain의 핵심 추상화로, Unix 파이프(`|`) 연산자로 컴포넌트를 연결합니다.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 기본 RAG Chain
prompt = ChatPromptTemplate.from_template(
    "다음 컨텍스트를 참고하여 질문에 답하세요.\n\n"
    "컨텍스트: {context}\n\n"
    "질문: {question}"
)
model = ChatOpenAI(model="gpt-4o")

# LCEL 파이프 연산자로 체인 구성
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# 실행
result = chain.invoke("Delta Lake란 무엇인가요?")
print(result)
```

{% hint style="info" %}
**LCEL의 장점**: 파이프 연산자(`|`)로 체인을 구성하면 스트리밍, 배치 처리, 비동기 실행이 자동으로 지원됩니다. 각 컴포넌트는 `Runnable` 인터페이스를 구현하므로 어디서나 교체 가능합니다.
{% endhint %}

### LangChain의 장점과 한계

** 장점:**
- ** 가장 큰 생태계**: 700+ 통합 (OpenAI, Anthropic, AWS Bedrock, Databricks, 등)
- ** 풍부한 문서와 튜토리얼**: 가장 많은 커뮤니티 자료
- ** 빠른 프로토타이핑**: 수십 줄 코드로 RAG, Agent 구축 가능
- ** 표준화된 인터페이스**: 모든 LLM을 동일한 API로 사용

** 한계:**
- ** 과도한 추상화**: 간단한 LLM 호출도 여러 클래스를 거쳐야 하는 경우 발생
- ** 디버깅 어려움**: 추상화 레이어가 많아 에러 추적이 복잡
- "**LangChain Fatigue**": 빈번한 API 변경으로 코드가 빠르게 구식화
- ** 선형 흐름의 한계**: Chain은 본질적으로 순차 실행이므로 조건 분기, 루프 표현이 어려움

{% hint style="warning" %}
**LangChain Fatigue란?**2024년 중반부터 커뮤니티에서 나타난 현상으로, LangChain의 빈번한 breaking change, 과도한 추상화, 불필요한 의존성에 대한 피로감을 표현합니다. 이는 LangGraph의 등장 배경이 되었습니다.
{% endhint %}

---

## LangGraph -- "Chain의 한계를 넘어서"

LangGraph는 LangChain 팀이 만든 차세대 프레임워크로, ** 유향 그래프(Directed Graph)**를 사용하여 Agent 워크플로를 정의합니다. Chain의 "순차 실행" 한계를 극복하기 위해 탄생했습니다.

### 왜 LangGraph가 필요한가?

{% hint style="success" %}
** 비유**: LangChain이 "** 레시피(순서대로 실행)**"라면, LangGraph는 "** 지도(여러 경로가 가능한 네비게이션)**"입니다. 레시피는 항상 1번 -> 2번 -> 3번 순서로 진행하지만, 지도는 교차로에서 상황에 따라 다른 길을 선택할 수 있습니다.
{% endhint %}

| 상황 | LangChain (Chain) | LangGraph (Graph) |
|------|-------------------|-------------------|
| A -> B -> C 순차 실행 | 가능 | 가능 |
| A 결과에 따라 B 또는 C 선택 | 어려움 (별도 로직 필요) | 네이티브 지원 (Conditional Edge) |
| 실패 시 이전 단계로 돌아가기 | 불가 | 가능 (Edge로 루프 구성) |
| 도구 호출 결과에 따라 반복 | 수동 구현 필요 | ReAct 루프로 자연스럽게 표현 |
| 중간에 사람 승인 받기 | 불가 | Checkpoint + Human-in-the-loop |
| 실행 중 상태 저장/복구 | 불가 | Checkpoint로 자동 지원 |

### 핵심 개념

**StateGraph**: Agent의 전체 워크플로를 정의하는 그래프. 노드(Node)와 엣지(Edge)로 구성됩니다.

| 개념 | 설명 | 비유 |
|------|------|------|
| **State** | 그래프 전체에서 공유되는 상태 객체 | 팀 공유 화이트보드 |
| **Node** | 하나의 작업 단위 (함수) | 각 부서 / 담당자 |
| **Edge** | 노드 간 연결 (다음 단계 지정) | 업무 전달 경로 |
| **Conditional Edge** | 조건에 따라 다른 노드로 분기 | 교차로에서의 방향 선택 |
| **Checkpoint** | 실행 중 상태 스냅샷 저장 | 게임 세이브 포인트 |

### 코드 예제 1: 내장 ReAct Agent

LangGraph에는 가장 흔한 패턴인 ReAct Agent가 미리 구현되어 있습니다.

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults

# 모델과 도구 정의
model = ChatOpenAI(model="gpt-4o")
tools = [TavilySearchResults(max_results=3)]

# ReAct Agent 생성 (단 2줄!)
agent = create_react_agent(model, tools)

# 실행
result = agent.invoke({
    "messages": [("user", "최신 Databricks 뉴스를 알려줘")]
})

for msg in result["messages"]:
    print(f"[{msg.type}] {msg.content[:200]}")
```

### 코드 예제 2: Custom StateGraph (조건 분기)

실전에서는 내장 Agent보다 커스텀 그래프를 직접 설계하는 경우가 많습니다.

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# 1. 상태 정의 -- 그래프 전체에서 공유
class AgentState(TypedDict):
    question: str
    category: str
    answer: str

# 2. 노드 정의 -- 각 단계의 로직
def classify(state: AgentState) -> AgentState:
    """질문을 분류하는 노드"""
    question = state["question"]
    if "가격" in question or "비용" in question:
        return {"category": "pricing"}
    elif "기술" in question or "아키텍처" in question:
        return {"category": "technical"}
    else:
        return {"category": "general"}

def handle_pricing(state: AgentState) -> AgentState:
    """가격 관련 질문 처리"""
    return {"answer": f"가격 팀에서 답변: {state['question']}에 대한 견적 안내입니다."}

def handle_technical(state: AgentState) -> AgentState:
    """기술 관련 질문 처리"""
    return {"answer": f"기술 팀에서 답변: {state['question']}에 대한 아키텍처 가이드입니다."}

def handle_general(state: AgentState) -> AgentState:
    """일반 질문 처리"""
    return {"answer": f"일반 답변: {state['question']}에 대한 정보입니다."}

# 3. 라우터 함수 -- 조건 분기 로직
def route_question(state: AgentState) -> Literal["pricing", "technical", "general"]:
    return state["category"]

# 4. 그래프 조립
graph = StateGraph(AgentState)

# 노드 추가
graph.add_node("classify", classify)
graph.add_node("pricing", handle_pricing)
graph.add_node("technical", handle_technical)
graph.add_node("general", handle_general)

# 엣지 연결
graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", route_question, {
    "pricing": "pricing",
    "technical": "technical",
    "general": "general",
})
graph.add_edge("pricing", END)
graph.add_edge("technical", END)
graph.add_edge("general", END)

# 5. 컴파일 & 실행
app = graph.compile()
result = app.invoke({"question": "Databricks 가격이 어떻게 되나요?"})
print(result["answer"])
# 출력: "가격 팀에서 답변: Databricks 가격이 어떻게 되나요?에 대한 견적 안내입니다."
```

### Checkpoint: 상태 저장과 Human-in-the-loop

Checkpoint는 LangGraph의 가장 강력한 기능 중 하나입니다. 장기 실행 Agent의 상태를 저장하고, 사람의 승인을 기다린 뒤 이어서 실행할 수 있습니다.

```python
from langgraph.checkpoint.memory import MemorySaver

# 메모리 기반 Checkpoint (프로덕션에서는 PostgreSQL 등 사용)
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# thread_id로 대화 상태를 구분
config = {"configurable": {"thread_id": "user-123"}}

# 첫 번째 실행 -- 상태가 자동 저장됨
result1 = app.invoke({"question": "기술 아키텍처 설명해주세요"}, config)

# 이후 같은 thread_id로 실행하면 이전 상태를 이어받음
result2 = app.invoke({"question": "좀 더 상세하게"}, config)
```

{% hint style="info" %}
**Human-in-the-loop**: `interrupt_before` 또는 `interrupt_after` 파라미터로 특정 노드 실행 전후에 Agent를 일시 중지하고 사람의 승인을 기다릴 수 있습니다. 금융 거래 승인, 민감한 데이터 접근 등에 활용됩니다.
{% endhint %}

### LangGraph 내장 패턴

LangGraph는 자주 사용되는 Agent 패턴을 미리 구현해 제공합니다.

| 패턴 | 설명 | 적합한 시나리오 |
|------|------|---------------|
| **ReAct Agent** | Thought-Action-Observation 루프 | 도구 활용 범용 Agent |
| **Plan-and-Execute** | 먼저 계획 수립 -> 순서대로 실행 | 복잡한 멀티스텝 작업 |
| **Reflection** | 자기 출력을 검토하고 개선 | 코드 생성, 글쓰기 |
| **Multi-Agent Supervisor** | 감독자가 하위 Agent에게 작업 배분 | 역할 분리된 팀 작업 |
| **Swarm** | Agent 간 자유로운 핸드오프 | 고객 서비스 라우팅 |

### LangGraph vs LangChain 비교

| 항목 | LangChain | LangGraph |
|------|-----------|-----------|
| 워크플로 모델 | 선형 체인 (DAG 형태) | 유향 그래프 (사이클 가능) |
| 조건 분기 | 수동 구현 (RunnableBranch) | Conditional Edge (네이티브) |
| 루프 | 불가 (별도 while 루프 필요) | Edge로 자연스럽게 표현 |
| 상태 관리 | Memory 클래스 (제한적) | TypedDict 기반 공유 State |
| 장기 실행 | 미지원 | Checkpoint로 저장/복구 |
| Human-in-the-loop | 미지원 | interrupt_before/after |
| 디버깅 | 어려움 | LangSmith + 그래프 시각화 |
| 학습 난이도 | 중간 | 높음 (그래프 개념 이해 필요) |
| 프로덕션 적합성 | 부분적 | 우수 |

{% hint style="warning" %}
**LangChain과 LangGraph의 관계**: LangGraph는 LangChain을 ** 대체**하는 것이 아니라 ** 보완**합니다. LangGraph는 LangChain의 모델, 도구, 프롬프트 컴포넌트를 그대로 사용하면서 워크플로 오케스트레이션을 그래프로 강화합니다. 즉, `langchain-openai`, `langchain-community` 같은 통합 패키지는 LangGraph에서도 계속 사용합니다.
{% endhint %}

---

[README로 돌아가기](README.md) | 다음: [CrewAI, OpenAI Agents SDK & AutoGen](crewai-openai-autogen.md)
