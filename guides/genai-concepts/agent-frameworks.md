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

## 1. Agent 프레임워크의 진화 -- 왜 이렇게 많은가?

Agent 프레임워크의 역사는 **"LLM을 어떻게 실용적으로 쓸 것인가"**에 대한 답을 찾아가는 과정입니다. 각 프레임워크는 이전 세대의 한계를 해결하기 위해 등장했습니다.

{% hint style="success" %}
**비유**: 웹 프레임워크의 역사와 유사합니다. jQuery(단순 DOM 조작) -> Angular(구조화) -> React(컴포넌트 기반) -> Next.js(풀스택)로 진화한 것처럼, Agent 프레임워크도 단순 체인에서 그래프 기반, 멀티에이전트, 엔터프라이즈 플랫폼으로 진화하고 있습니다.
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

## 2. LangChain -- Agent 프레임워크의 원조

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

**장점:**
- **가장 큰 생태계**: 700+ 통합 (OpenAI, Anthropic, AWS Bedrock, Databricks, 등)
- **풍부한 문서와 튜토리얼**: 가장 많은 커뮤니티 자료
- **빠른 프로토타이핑**: 수십 줄 코드로 RAG, Agent 구축 가능
- **표준화된 인터페이스**: 모든 LLM을 동일한 API로 사용

**한계:**
- **과도한 추상화**: 간단한 LLM 호출도 여러 클래스를 거쳐야 하는 경우 발생
- **디버깅 어려움**: 추상화 레이어가 많아 에러 추적이 복잡
- **"LangChain Fatigue"**: 빈번한 API 변경으로 코드가 빠르게 구식화
- **선형 흐름의 한계**: Chain은 본질적으로 순차 실행이므로 조건 분기, 루프 표현이 어려움

{% hint style="warning" %}
**LangChain Fatigue란?** 2024년 중반부터 커뮤니티에서 나타난 현상으로, LangChain의 빈번한 breaking change, 과도한 추상화, 불필요한 의존성에 대한 피로감을 표현합니다. 이는 LangGraph의 등장 배경이 되었습니다.
{% endhint %}

---

## 3. LangGraph -- "Chain의 한계를 넘어서"

LangGraph는 LangChain 팀이 만든 차세대 프레임워크로, **유향 그래프(Directed Graph)**를 사용하여 Agent 워크플로를 정의합니다. Chain의 "순차 실행" 한계를 극복하기 위해 탄생했습니다.

### 왜 LangGraph가 필요한가?

{% hint style="success" %}
**비유**: LangChain이 **"레시피(순서대로 실행)"**라면, LangGraph는 **"지도(여러 경로가 가능한 네비게이션)"**입니다. 레시피는 항상 1번 -> 2번 -> 3번 순서로 진행하지만, 지도는 교차로에서 상황에 따라 다른 길을 선택할 수 있습니다.
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
**LangChain과 LangGraph의 관계**: LangGraph는 LangChain을 **대체**하는 것이 아니라 **보완**합니다. LangGraph는 LangChain의 모델, 도구, 프롬프트 컴포넌트를 그대로 사용하면서 워크플로 오케스트레이션을 그래프로 강화합니다. 즉, `langchain-openai`, `langchain-community` 같은 통합 패키지는 LangGraph에서도 계속 사용합니다.
{% endhint %}

---

## 4. CrewAI -- 역할 기반 멀티에이전트

CrewAI는 "사람 팀처럼 동작하는 AI 에이전트 팀"이라는 직관적인 메타포를 기반으로 설계된 프레임워크입니다. 비개발자도 이해할 수 있는 선언적 API가 특징입니다.

### 설계 철학: 팀 메타포

{% hint style="success" %}
**비유**: 회사 프로젝트를 수행할 때 팀장이 각 팀원에게 역할(리서처, 분석가, 작성자)을 부여하고 업무를 배분하듯이, CrewAI는 Agent에게 역할(role)을 부여하고 Task를 할당합니다.
{% endhint %}

| CrewAI 개념 | 팀 비유 | 설명 |
|-------------|---------|------|
| **Agent** | 팀원 | 역할, 목표, 배경 스토리를 가진 AI 작업자 |
| **Task** | 업무 | 구체적인 작업 지시 + 기대 결과물 |
| **Crew** | 팀 | Agent들을 모아 프로세스에 따라 실행 |
| **Process** | 업무 방식 | Sequential(순차) 또는 Hierarchical(계층) |

### 코드 예제: 리서치 + 보고서 작성 팀

```python
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# 도구 정의
search_tool = SerperDevTool()

# Agent 1: 리서처
researcher = Agent(
    role="시니어 데이터 리서처",
    goal="Databricks의 최신 기술 동향을 조사하여 핵심 인사이트를 도출한다",
    backstory=(
        "당신은 10년 경력의 데이터 플랫폼 분석가입니다. "
        "기술 트렌드를 빠르게 파악하고 비즈니스 임팩트를 연결하는 데 탁월합니다."
    ),
    tools=[search_tool],
    verbose=True,
)

# Agent 2: 보고서 작성자
writer = Agent(
    role="테크 라이터",
    goal="리서처의 조사 결과를 기반으로 경영진용 보고서를 작성한다",
    backstory=(
        "당신은 기술 콘텐츠를 비기술 임원이 이해할 수 있도록 "
        "변환하는 전문 테크 라이터입니다."
    ),
    verbose=True,
)

# Task 1: 조사
research_task = Task(
    description="2025년 Databricks의 주요 제품 업데이트와 시장 동향을 조사하세요.",
    expected_output="핵심 업데이트 5개와 각각의 비즈니스 임팩트 분석",
    agent=researcher,
)

# Task 2: 보고서 작성
writing_task = Task(
    description="리서치 결과를 기반으로 경영진용 1페이지 브리핑을 작성하세요.",
    expected_output="제목, 핵심 요약 3줄, 상세 분석 5개 항목의 구조화된 보고서",
    agent=writer,
)

# Crew 구성 및 실행
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,  # 순차 실행: 리서치 -> 작성
    verbose=True,
)

result = crew.kickoff()
print(result)
```

### Process 타입

| Process | 동작 방식 | 적합한 시나리오 |
|---------|----------|---------------|
| **Sequential** | Task를 순서대로 실행. 이전 Task 결과가 다음 Task의 입력 | 파이프라인형 작업 (조사 -> 분석 -> 보고서) |
| **Hierarchical** | Manager Agent가 하위 Agent에게 작업 위임 및 조율 | 복잡한 프로젝트 관리, 여러 전문가 협업 |

### CrewAI의 장점과 한계

**장점:**
- **직관적**: 역할/팀 메타포가 명확하여 비개발자도 구조를 이해 가능
- **빠른 프로토타이핑**: 10분 내에 멀티에이전트 시스템 구축 가능
- **선언적 API**: 코드보다는 "설정"에 가까운 구성 방식

**한계:**
- **세밀한 제어 어려움**: 에이전트 간 통신의 세부 흐름을 커스텀하기 어려움
- **조건 분기 제한**: LangGraph 대비 복잡한 분기/루프 표현 능력 부족
- **프로덕션 미성숙**: 에러 처리, 모니터링, 거버넌스 기능이 약함
- **비결정적 동작**: Agent의 "대화"가 매번 다르게 전개될 수 있음

---

## 5. OpenAI Agents SDK -- Handoff 패턴의 정석

2025년 1월 출시된 OpenAI Agents SDK는 OpenAI가 직접 제공하는 공식 Agent 프레임워크입니다. **Handoff(대화 인계)**, **Guardrail(안전장치)**, **Tracing(추적)**을 핵심 기능으로 내세웁니다.

### 핵심 개념

| 개념 | 설명 | 비유 |
|------|------|------|
| **Agent** | 시스템 프롬프트 + 도구 + 모델로 구성된 실행 단위 | 전문 상담원 |
| **Handoff** | Agent A가 대화 전체를 Agent B에게 넘기기 | 콜센터 상담 전환 |
| **Guardrail** | 입력/출력을 프레임워크 레벨에서 검증 | 보안 검색대 |
| **Tracing** | 전체 실행 과정을 자동으로 기록 | CCTV 녹화 |

### Handoff 패턴

Handoff는 OpenAI Agents SDK의 가장 독특한 기능입니다. Agent A가 자신의 전문 영역이 아닌 질문을 받으면, 대화 히스토리 전체를 포함하여 Agent B에게 인계합니다.

{% hint style="info" %}
**Handoff vs Tool Call**: Tool Call은 "특정 함수를 호출하고 결과를 받아오는 것"이고, Handoff는 "대화의 주도권 자체를 다른 Agent에게 넘기는 것"입니다. 콜센터에서 "잠시만요, 기술팀으로 연결해드리겠습니다"라고 하는 것이 Handoff입니다.
{% endhint %}

### 코드 예제: 고객 서비스 Agent (Handoff 포함)

```python
from openai import agents

# 전문 Agent 정의
billing_agent = agents.Agent(
    name="billing_agent",
    instructions=(
        "당신은 청구/결제 전문 상담원입니다. "
        "청구 관련 질문에만 답변하세요. "
        "기술 지원 질문은 tech_agent로 핸드오프하세요."
    ),
    model="gpt-4o",
)

tech_agent = agents.Agent(
    name="tech_agent",
    instructions=(
        "당신은 기술 지원 전문 상담원입니다. "
        "기술적인 문제에 대해 답변하세요. "
        "청구 관련 질문은 billing_agent로 핸드오프하세요."
    ),
    model="gpt-4o",
)

# Triage Agent -- 첫 진입점
triage_agent = agents.Agent(
    name="triage_agent",
    instructions=(
        "당신은 고객 문의를 분류하는 접수 담당입니다. "
        "고객의 질문을 파악하여 적절한 전문 상담원에게 연결하세요."
    ),
    model="gpt-4o",
    handoffs=[billing_agent, tech_agent],  # 핸드오프 대상 지정
)

# 실행
result = agents.run(
    triage_agent,
    messages=[{"role": "user", "content": "지난달 청구서가 이상합니다"}],
)

# triage_agent -> billing_agent로 자동 핸드오프됨
print(result.final_output)
```

### Guardrail (입력/출력 검증)

```python
from openai.agents import guardrail, GuardrailFunctionOutput

@guardrail
def no_pii_guardrail(text: str) -> GuardrailFunctionOutput:
    """개인정보(PII)가 포함된 입력을 차단"""
    import re
    # 주민등록번호 패턴 체크
    if re.search(r'\d{6}-\d{7}', text):
        return GuardrailFunctionOutput(
            output_info="주민등록번호가 감지되었습니다.",
            tripwire_triggered=True,  # 실행 중단
        )
    return GuardrailFunctionOutput(
        output_info="안전한 입력입니다.",
        tripwire_triggered=False,
    )

agent = agents.Agent(
    name="safe_agent",
    instructions="고객 문의에 답변하세요.",
    model="gpt-4o",
    input_guardrails=[no_pii_guardrail],  # 입력 가드레일 적용
)
```

### OpenAI Agents SDK의 장점과 한계

**장점:**
- **간결한 API**: 최소한의 코드로 Agent 구축 가능
- **Handoff 패턴 내장**: 멀티에이전트 라우팅이 매우 깔끔
- **Guardrail 내장**: 별도 라이브러리 없이 입출력 검증
- **자동 Tracing**: OpenAI 대시보드에서 실행 과정 시각화
- **프로덕션 지향**: OpenAI 인프라와 긴밀하게 통합

**한계:**
- **OpenAI 종속**: 기본적으로 OpenAI 모델만 지원 (커스텀 확장 필요)
- **복잡한 그래프 표현 제한**: LangGraph 수준의 복잡한 워크플로는 어려움
- **상태 관리 제한**: LangGraph Checkpoint 같은 장기 상태 관리 기능 부족
- **자체 호스팅 어려움**: OpenAI API 의존도가 높음

---

## 6. AutoGen (Microsoft) -- 멀티에이전트 대화

AutoGen은 Microsoft Research에서 개발한 프레임워크로, Agent들이 자유롭게 "대화"하며 문제를 해결하는 패러다임을 제안합니다.

### 설계 철학

{% hint style="success" %}
**비유**: 다른 프레임워크가 "조직도에 따른 업무 배분"이라면, AutoGen은 "회의실에서 자유 토론"에 가깝습니다. 참가자들이 돌아가며 발언하고, 서로의 의견에 반응하며, 합의에 도달합니다.
{% endhint %}

### 핵심 컴포넌트

| 컴포넌트 | 역할 |
|----------|------|
| **ConversableAgent** | 대화 가능한 Agent의 기본 클래스 |
| **AssistantAgent** | LLM 기반 Agent (추론 담당) |
| **UserProxyAgent** | 사용자를 대리하는 Agent (코드 실행, 승인 등) |
| **GroupChat** | 여러 Agent가 참여하는 그룹 대화 |
| **GroupChatManager** | 그룹 대화의 발언 순서와 종료 조건 관리 |

### 코드 예제: 코드 생성 + 리뷰 Agent

```python
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

# LLM 설정
config_list = [{"model": "gpt-4o", "api_key": "YOUR_API_KEY"}]

# Agent 1: 코드 작성자
coder = AssistantAgent(
    name="coder",
    system_message=(
        "당신은 시니어 Python 개발자입니다. "
        "요청받은 기능을 깔끔한 Python 코드로 구현하세요. "
        "코드 블록으로 감싸서 응답하세요."
    ),
    llm_config={"config_list": config_list},
)

# Agent 2: 코드 리뷰어
reviewer = AssistantAgent(
    name="reviewer",
    system_message=(
        "당신은 코드 리뷰 전문가입니다. "
        "coder가 작성한 코드를 리뷰하고 개선점을 제안하세요. "
        "보안, 성능, 가독성 관점에서 평가하세요."
    ),
    llm_config={"config_list": config_list},
)

# Agent 3: 사용자 대리 (코드 실행 가능)
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",  # 자동 실행 (사람 개입 없음)
    code_execution_config={"work_dir": "coding_output"},
    max_consecutive_auto_reply=3,
)

# 대화 시작: user_proxy가 coder에게 요청
user_proxy.initiate_chat(
    coder,
    message="Delta Lake 테이블의 변경 이력을 조회하는 Python 함수를 작성해주세요.",
)
```

### AutoGen의 장점과 한계

**장점:**
- **코드 실행 내장**: Agent가 직접 Python/Shell 코드를 실행하고 결과 확인 가능
- **자유도 높은 대화**: 정해진 워크플로 없이 Agent들이 자율적으로 협업
- **연구/실험에 최적**: 다양한 에이전트 구성을 빠르게 실험 가능
- **GroupChat**: 3개 이상의 Agent가 동시에 참여하는 토론 가능

**한계:**
- **비결정적 흐름**: 매번 다른 대화 흐름이 전개될 수 있어 프로덕션에서 예측 가능성 낮음
- **프로덕션 배포 복잡**: 모니터링, 에러 처리, 스케일링이 쉽지 않음
- **대화 비용**: 불필요한 왕복 대화로 토큰 비용 증가 가능
- **종료 조건 설정 어려움**: "언제 대화를 끝낼 것인가"의 판단이 까다로움

{% hint style="warning" %}
**AutoGen v0.4 주의사항**: AutoGen은 v0.2에서 v0.4로 대규모 리팩토링을 거쳤습니다. 이전 버전의 블로그/튜토리얼 코드는 v0.4에서 동작하지 않을 수 있습니다. 반드시 최신 공식 문서를 참고하세요.
{% endhint %}

---

## 7. Databricks Agent Framework (Mosaic AI) -- 엔터프라이즈 정답

Databricks Agent Framework는 "**빌드보다 배포가 중요하다**"는 철학 아래 설계되었습니다. 오픈소스 프레임워크들이 "Agent를 어떻게 만들 것인가"에 집중한다면, Databricks는 "**Agent를 어떻게 안전하게 운영할 것인가**"에 집중합니다.

{% hint style="info" %}
**핵심 인사이트**: 실제 엔터프라이즈에서 Agent를 프로덕션에 배포할 때 가장 큰 과제는 "Agent를 만드는 것"이 아니라 "누가 어떤 데이터에 접근하는지 통제하고, 응답 품질을 모니터링하고, 문제 발생 시 원인을 추적하는 것"입니다. Databricks Agent Framework는 이 문제를 해결합니다.
{% endhint %}

### 설계 철학: 거버넌스 + 배포 + 모니터링 통합

```
┌─────────────────────────────────────────────────────────────┐
│                 Databricks Agent Framework                  │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │  Build   │  │   Deploy     │  │    Monitor         │    │
│  │          │  │              │  │                    │    │
│  │ ChatAgent│  │ Model Serving│  │ MLflow Tracing     │    │
│  │ LangGraph│  │ (Serverless) │  │ Review App         │    │
│  │ UC Tools │  │ One-click    │  │ Agent Evaluation   │    │
│  │ VS Index │  │ Auto-scaling │  │ Inference Tables   │    │
│  └──────────┘  └──────────────┘  └────────────────────┘    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │              Unity Catalog (거버넌스 레이어)         │     │
│  │  함수 권한 | 데이터 접근 제어 | 모델 레지스트리       │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 핵심 차별점

| 기능 | 설명 | 오픈소스 대비 장점 |
|------|------|-----------------|
| **Unity Catalog Functions as Tools** | UC에 등록된 함수를 Agent 도구로 사용 | 함수에 대한 권한(GRANT/REVOKE)이 자동 적용 |
| **MLflow Tracing** | 전체 추론 과정(LLM 호출, 도구 실행, 에러)을 자동 기록 | 별도 설정 없이 네이티브 통합 |
| **Review App** | 비개발자가 웹 UI에서 Agent 응답을 평가/피드백 | 인간 피드백을 쉽게 수집 |
| **One-click Model Serving** | 서버리스 엔드포인트로 즉시 배포 | 인프라 관리 불필요 |
| **AI Guardrails** | Llama Guard 기반 입출력 안전성 검증 | 엔드포인트 레벨에서 자동 적용 |
| **Agent Evaluation** | LLM-as-Judge로 응답 품질 자동 평가 | MLflow Evaluate와 통합 |
| **Inference Tables** | 모든 요청/응답을 Delta 테이블에 자동 저장 | 감사 추적 + 품질 모니터링 |

### ChatAgent 인터페이스

Databricks Agent Framework의 모든 Agent는 `ChatAgent` 인터페이스를 구현합니다. 이것은 LangGraph, 순수 Python, 어떤 프레임워크로 만들든 동일한 배포/모니터링 체계에 통합되도록 해줍니다.

```python
import mlflow
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import (
    ChatAgentMessage,
    ChatAgentResponse,
    ChatAgentChunk,
)
from databricks.sdk import WorkspaceClient
from typing import Generator

class CustomerServiceAgent(ChatAgent):
    """Databricks Agent Framework 기반 고객 서비스 Agent"""

    def __init__(self):
        # Databricks Foundation Model API 사용
        self.client = WorkspaceClient()
        self.model_endpoint = "databricks-meta-llama-3-3-70b-instruct"

    def predict(
        self,
        messages: list[ChatAgentMessage],
        context=None,
        custom_inputs=None,
    ) -> ChatAgentResponse:
        """동기 응답 -- 전체 결과를 한 번에 반환"""

        # Unity Catalog 함수를 도구로 사용
        response = self.client.serving_endpoints.query(
            name=self.model_endpoint,
            messages=[m.to_dict() for m in messages],
            tools=[
                {
                    "type": "uc_function",
                    "function": {
                        "name": "main.default.search_knowledge_base"
                    }
                },
                {
                    "type": "uc_function",
                    "function": {
                        "name": "main.default.get_order_status"
                    }
                },
            ],
        )

        return ChatAgentResponse(
            messages=[
                ChatAgentMessage(
                    role="assistant",
                    content=response.choices[0].message.content,
                )
            ]
        )

    def predict_stream(
        self,
        messages: list[ChatAgentMessage],
        context=None,
        custom_inputs=None,
    ) -> Generator[ChatAgentChunk, None, None]:
        """스트리밍 응답 -- 토큰 단위로 반환"""
        # 스트리밍 구현 (생략)
        pass

# MLflow에 Agent 로깅
mlflow.set_experiment("/Users/user@company.com/customer-service-agent")

with mlflow.start_run():
    model_info = mlflow.pyfunc.log_model(
        artifact_path="agent",
        python_model=CustomerServiceAgent(),
        pip_requirements=[
            "mlflow>=2.21",
            "databricks-sdk>=0.40",
        ],
    )

# Unity Catalog에 모델 등록
mlflow.set_registry_uri("databricks-uc")
mlflow.register_model(
    model_uri=model_info.model_uri,
    name="main.default.customer_service_agent",
)
```

### LangGraph + Databricks: 최적의 조합

실전에서는 LangGraph로 복잡한 Agent 로직을 구현하고, Databricks Agent Framework로 배포/모니터링하는 조합이 가장 강력합니다.

```python
import mlflow
from mlflow.pyfunc import ChatAgent
from langgraph.prebuilt import create_react_agent
from langchain_databricks import ChatDatabricks
from langchain_community.tools.databricks import UCFunctionToolkit

class LangGraphOnDatabricks(ChatAgent):
    """LangGraph Agent를 Databricks에서 운영하는 패턴"""

    def __init__(self):
        # Databricks Foundation Model 사용
        model = ChatDatabricks(
            endpoint="databricks-meta-llama-3-3-70b-instruct",
            temperature=0.1,
        )

        # Unity Catalog 함수를 LangGraph 도구로 변환
        uc_toolkit = UCFunctionToolkit(
            function_names=[
                "main.default.search_knowledge_base",
                "main.default.execute_sql_query",
            ]
        )
        tools = uc_toolkit.get_tools()

        # LangGraph ReAct Agent 생성
        self.agent = create_react_agent(model, tools)

    @mlflow.trace  # MLflow Tracing 자동 적용
    def predict(self, messages, context=None, custom_inputs=None):
        # LangGraph Agent 실행
        result = self.agent.invoke({
            "messages": [m.to_dict() for m in messages]
        })
        return ChatAgentResponse(
            messages=[
                ChatAgentMessage(
                    role="assistant",
                    content=result["messages"][-1].content,
                )
            ]
        )
```

{% hint style="success" %}
**Databricks Agent Framework의 진짜 가치**: 오픈소스 프레임워크는 "Agent를 만드는 10%의 시간"을 줄여주고, Databricks Agent Framework는 "나머지 90%인 배포, 모니터링, 거버넌스, 평가"를 해결합니다.
{% endhint %}

---

## 8. 프레임워크 종합 비교

### 전체 비교표

| 항목 | LangChain | LangGraph | CrewAI | OpenAI SDK | AutoGen | Databricks |
|------|-----------|-----------|--------|-----------|---------|------------|
| **설계 철학** | 체인 (순차 연결) | 그래프 (유향 그래프) | 역할/팀 | 핸드오프 | 대화 기반 | 엔터프라이즈 운영 |
| **학습 난이도** | 중간 | 높음 | 낮음 | 낮음 | 중간 | 중간 |
| **유연성** | 높음 | 매우 높음 | 중간 | 중간 | 높음 | 중간 |
| **프로덕션 적합성** | 부분적 | 좋음 | 제한적 | 좋음 | 제한적 | 최적 |
| **Multi-Agent** | 기본 | 우수 | 우수 | 좋음 | 우수 | 좋음 |
| **상태 관리** | Memory (제한적) | Checkpoint (강력) | 내부 관리 | 기본 | 대화 히스토리 | MLflow + UC |
| **모델 종속성** | 없음 (700+) | 없음 | 없음 | OpenAI 중심 | 없음 | 없음 (FMAPI) |
| **거버넌스** | 없음 | 없음 | 없음 | 기본 | 없음 | 네이티브 (UC) |
| **MLflow 통합** | 플러그인 | 플러그인 | 플러그인 | 커스텀 | 커스텀 | 네이티브 |
| **배포** | 자체 구축 필요 | 자체 구축 필요 | 자체 구축 필요 | OpenAI 호스팅 | 자체 구축 필요 | 원클릭 서버리스 |
| **Tracing** | LangSmith (유료) | LangSmith (유료) | 제한적 | OpenAI 대시보드 | 제한적 | MLflow Tracing (무료) |
| **커뮤니티** | 매우 큼 | 큼 | 중간 | 큼 | 중간 | Databricks 커뮤니티 |
| **주요 사용처** | PoC, 프로토타입 | 복잡한 워크플로 | 빠른 데모 | OpenAI 생태계 | 연구/실험 | 엔터프라이즈 배포 |

### 성격별 비교

{% hint style="info" %}
**한 줄 요약**:
- **LangChain** = "레고 블록 세트" (다양하지만 복잡)
- **LangGraph** = "프로그래밍 가능한 회로판" (강력하지만 어려움)
- **CrewAI** = "팀 빌딩 게임" (직관적이지만 제한적)
- **OpenAI SDK** = "콜센터 시스템" (깔끔하지만 OpenAI 한정)
- **AutoGen** = "자유 토론방" (창의적이지만 예측 불가)
- **Databricks** = "기업용 관제탑" (안전하지만 플랫폼 종속)
{% endhint %}

---

## 9. 프레임워크 선택 가이드 -- 의사결정 트리

### 시나리오별 추천

| 시나리오 | 추천 프레임워크 | 이유 |
|----------|----------------|------|
| 빠른 프로토타입/데모가 목표 | **CrewAI** | 10분 내에 멀티에이전트 데모 가능 |
| 복잡한 워크플로 + 조건 분기 | **LangGraph** | 유향 그래프로 어떤 흐름이든 표현 가능 |
| OpenAI만 사용 + 핸드오프 패턴 | **OpenAI Agents SDK** | 가장 깔끔한 Handoff 구현 |
| Databricks 환경에서 프로덕션 배포 | **Databricks Agent Framework** (+ LangGraph) | 거버넌스, 모니터링, 원클릭 배포 |
| 연구/실험 + 코드 실행 | **AutoGen** | Agent 간 자유 대화 + 코드 실행 내장 |
| RAG 파이프라인만 필요 | **LangChain** (LCEL) | 간단한 파이프라인에 적합 |
| 기존 LangChain 코드 마이그레이션 | **LangGraph** | LangChain 컴포넌트 재사용 가능 |

### 의사결정 흐름

```
[시작] 어떤 Agent를 만들려는가?
│
├── "단순 RAG / QA 봇"
│   └── LangChain LCEL 또는 Databricks Agent Bricks (Knowledge Assistant)
│
├── "복잡한 멀티스텝 워크플로"
│   ├── Databricks 환경?
│   │   ├── YES → LangGraph + Databricks Agent Framework
│   │   └── NO  → LangGraph 단독
│   └── 조건 분기/루프 필요?
│       ├── YES → LangGraph
│       └── NO  → LangChain LCEL
│
├── "멀티에이전트 협업"
│   ├── 역할 기반 (리서처, 작성자 등)?
│   │   ├── 프로덕션? → LangGraph Multi-Agent
│   │   └── PoC/데모? → CrewAI
│   ├── 대화 기반 (자유 토론)?
│   │   └── AutoGen
│   └── 라우팅/핸드오프?
│       ├── OpenAI만 사용? → OpenAI Agents SDK
│       └── 모델 무관? → LangGraph Swarm 패턴
│
└── "엔터프라이즈 프로덕션"
    └── Databricks Agent Framework (빌드 프레임워크는 선택)
        ├── 복잡한 로직 → + LangGraph
        ├── 간단한 로직 → + 순수 Python
        └── 노코드 → Agent Bricks
```

{% hint style="warning" %}
**실전 팁**: 프레임워크 선택에 너무 많은 시간을 쓰지 마세요. 중요한 것은 "어떤 프레임워크를 쓰느냐"가 아니라 "Agent가 해결하는 비즈니스 문제가 무엇인가"입니다. 대부분의 엔터프라이즈 시나리오에서는 **LangGraph + Databricks Agent Framework** 조합이 정답입니다.
{% endhint %}

---

## 10. Agent UI/배포 기술 스택

Agent를 만들었다면 사용자가 상호작용할 UI가 필요합니다. 용도와 환경에 따라 적합한 프론트엔드 기술이 다릅니다.

### 주요 프론트엔드 기술

| 기술 | 특징 | 적합한 용도 |
|------|------|------------|
| **Streamlit** | Python만으로 웹앱 구축. 가장 빠른 프로토타이핑 | PoC, 내부 도구, 데이터 대시보드 |
| **Gradio** | ML 모델 데모 특화. Hugging Face 통합 | 모델 데모, 인터랙티브 ML 실험 |
| **Chainlit** | LangChain/LangGraph 전용 채팅 UI. 대화형 Agent에 최적화 | Agent 채팅 인터페이스 |
| **Databricks Apps** | Databricks 네이티브 웹앱 호스팅. OAuth 통합 | 프로덕션 엔터프라이즈 앱 |

### 비교표

| 항목 | Streamlit | Gradio | Chainlit | Databricks Apps |
|------|-----------|--------|----------|----------------|
| **언어** | Python | Python | Python | Python (Streamlit/Dash/FastAPI) |
| **학습 난이도** | 매우 낮음 | 낮음 | 낮음 | 중간 |
| **UI 자유도** | 중간 | 낮음 | 낮음 (채팅 특화) | 높음 (프레임워크 선택 가능) |
| **채팅 UI** | `st.chat_message` | `gr.ChatInterface` | 네이티브 지원 | Streamlit 기반 |
| **스트리밍** | `st.write_stream` | 지원 | 네이티브 지원 | Streamlit 기반 |
| **인증** | 없음 (자체 구현) | 없음 | 없음 | OAuth 통합 (Databricks) |
| **프로덕션 적합성** | 제한적 | 제한적 | 제한적 | 우수 |
| **배포** | Streamlit Cloud / 자체 서버 | HF Spaces / 자체 서버 | 자체 서버 | Databricks 서버리스 |
| **Databricks 통합** | SDK 연동 필요 | SDK 연동 필요 | SDK 연동 필요 | 네이티브 (서비스 프린시펄) |

{% hint style="info" %}
**추천 경로**: PoC 단계에서는 Streamlit으로 빠르게 만들고, 프로덕션에서는 Databricks Apps(Streamlit 호스팅)로 배포하면 코드 변경 최소화로 인증/보안이 자동 적용됩니다.
{% endhint %}

### Agent UI 코드 예시 (Streamlit + Databricks Model Serving)

```python
import streamlit as st
from databricks.sdk import WorkspaceClient

st.title("고객 서비스 Agent")

# Databricks 클라이언트 초기화
w = WorkspaceClient()

# 대화 히스토리 관리
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 메시지 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent 호출 (Model Serving Endpoint)
    with st.chat_message("assistant"):
        response = w.serving_endpoints.query(
            name="customer-service-agent",
            messages=st.session_state.messages,
        )
        answer = response.choices[0].message.content
        st.markdown(answer)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
```

---

## 11. 2025 Agent 생태계 트렌드

### 1) Agentic AI의 부상

2025년은 "LLM의 시대"에서 "Agent의 시대"로 전환하는 원년입니다. 단순히 질문에 답하는 것을 넘어, 스스로 계획하고 도구를 사용하고 결과를 검증하는 Agentic AI가 엔터프라이즈의 핵심 화두가 되었습니다.

| 세대 | 특징 | 예시 |
|------|------|------|
| **1세대 (2023)** | LLM 호출 + 프롬프트 엔지니어링 | ChatGPT, Copilot Chat |
| **2세대 (2024)** | RAG + Tool Use + 단일 Agent | 지식 검색 봇, SQL Agent |
| **3세대 (2025)** | 멀티에이전트 + 자율적 워크플로 | Supervisor Agent, 업무 자동화 시스템 |

### 2) MCP + A2A: 도구 접근과 Agent 간 통신의 표준화

| 프로토콜 | 주도 | 목적 | 비유 |
|----------|------|------|------|
| **MCP (Model Context Protocol)** | Anthropic | LLM이 외부 도구/데이터에 접근하는 표준 | USB-C (기기와 주변기기 연결) |
| **A2A (Agent-to-Agent)** | Google | Agent 간 통신/협업의 표준 | HTTP (서버 간 통신) |

이 두 프로토콜이 결합되면, 서로 다른 프레임워크로 만든 Agent들이 표준 프로토콜로 도구를 공유하고 협업할 수 있게 됩니다.

### 3) Vibe Coding: AI가 코드를 짜는 시대

Agent가 개발자의 IDE 안에 들어와 코드를 직접 작성하는 "Vibe Coding" 트렌드가 가속화되고 있습니다.

| 도구 | 특징 |
|------|------|
| **Claude Code** | 터미널 기반 Agent. 파일 읽기/쓰기/실행까지 자율 수행 |
| **Cursor** | AI 네이티브 IDE. 코드베이스 컨텍스트 이해 |
| **GitHub Copilot Agent Mode** | PR 생성, 이슈 해결까지 자동화 |
| **Databricks AI Dev Kit** | Databricks 리소스 생성/관리를 IDE에서 수행 |

### 4) Agent Observability: "블랙박스를 열다"

Agent의 동작을 추적하고 디버깅하는 Observability 도구가 필수가 되었습니다.

| 도구 | 특징 | 가격 |
|------|------|------|
| **MLflow Tracing** | Databricks 네이티브. 자동 계측 | 무료 (Databricks 포함) |
| **LangSmith** | LangChain/LangGraph 전용 | 유료 (월 $39~) |
| **Arize AI** | 모델 모니터링 + Agent 추적 | 유료 |
| **Weights & Biases Weave** | 실험 추적 + Agent 로깅 | 유료 |

### 5) 프레임워크 수렴 추세

2024년의 "프레임워크 춘추전국시대"에서 2025년은 2~3개 핵심 프레임워크로 수렴하는 추세입니다.

| 수렴 방향 | 설명 |
|-----------|------|
| **LangGraph** | 오픈소스 Agent 워크플로의 사실상 표준 (de facto standard) |
| **Databricks Agent Framework** | 엔터프라이즈 배포/운영의 표준 |
| **OpenAI Agents SDK** | OpenAI 생태계 내 표준 |

{% hint style="success" %}
**2025년 핵심 메시지**: "어떤 프레임워크를 쓸지 고민하는 시간"보다 "Agent가 해결할 비즈니스 문제를 정의하는 시간"이 더 중요합니다. 프레임워크는 도구일 뿐이고, 진짜 가치는 비즈니스 문제 해결에 있습니다.
{% endhint %}

---

## 12. 고객이 자주 묻는 질문

### Q1. "어떤 프레임워크를 써야 하나요?"

**A**: Databricks 환경이라면 **Databricks Agent Framework + LangGraph** 조합을 권장합니다. LangGraph로 복잡한 Agent 로직(조건 분기, 멀티에이전트, Human-in-the-loop)을 구현하고, Databricks Agent Framework로 배포/모니터링/거버넌스를 처리하세요. 이 조합이 프로덕션까지의 가장 짧은 경로입니다.

### Q2. "LangChain을 배워야 하나요?"

**A**: LangChain의 핵심 컴포넌트(모델, 프롬프트, 도구)는 알아두면 좋지만, **Chain 기반 Agent 패턴은 레거시**입니다. 새로 시작한다면 **LangGraph를 직접 배우세요**. LangGraph는 LangChain의 컴포넌트를 재사용하면서 더 강력한 워크플로를 제공합니다. `langchain-core`, `langchain-openai` 같은 통합 패키지는 LangGraph에서도 그대로 사용합니다.

### Q3. "프레임워크 없이 직접 구현하면 안 되나요?"

**A**: 간단한 Agent(1개 LLM + 2~3개 도구)는 순수 Python으로 충분합니다. 그러나 아래 요구사항이 생기면 결국 프레임워크를 다시 만들게 됩니다:

| 요구사항 | 직접 구현 시 복잡도 |
|----------|------------------|
| 조건 분기 / 루프 | 높음 (상태 머신 직접 구현) |
| 대화 메모리 관리 | 중간 (토큰 제한 대응 필요) |
| 에러 복구 / 재시도 | 높음 (각 도구별 에러 처리) |
| Human-in-the-loop | 매우 높음 (상태 직렬화/역직렬화) |
| 멀티에이전트 | 매우 높음 (메시지 라우팅, 동기화) |
| Tracing / 디버깅 | 높음 (로깅 체계 설계) |

{% hint style="warning" %}
**경험적 법칙**: "2주 안에 프레임워크를 직접 만들 수 있다"고 생각한 팀이, 6개월 뒤에 "그냥 LangGraph 썼으면..."이라고 후회하는 경우가 많습니다.
{% endhint %}

### Q4. "Streamlit으로 프로덕션 배포해도 되나요?"

**A**: PoC/데모 목적이라면 Streamlit만으로 충분합니다. 그러나 프로덕션에서는 아래 문제가 발생합니다:

- **인증 부재**: Streamlit 자체에는 로그인/인증 기능이 없음
- **보안**: 민감한 API 키/토큰을 클라이언트 사이드에서 관리해야 함
- **스케일링**: 동시 사용자 처리에 한계
- **감사 추적**: 누가 언제 무엇을 질문했는지 기록 어려움

**권장 경로**: Streamlit 코드를 **Databricks Apps**로 배포하세요. 코드 변경 최소화로 OAuth 인증, 서비스 프린시펄 기반 보안, 자동 스케일링이 적용됩니다.

### Q5. "여러 프레임워크를 섞어 써도 되나요?"

**A**: 가능하지만, 명확한 역할 분담이 필요합니다. 권장 패턴은 다음과 같습니다:

| 레이어 | 역할 | 기술 |
|--------|------|------|
| **Agent 로직** | 워크플로, 조건 분기, 상태 관리 | LangGraph |
| **LLM 호출** | 모델 추상화, 프롬프트 관리 | LangChain Core (langchain-openai 등) |
| **도구** | UC Functions, Vector Search, API 호출 | Databricks SDK + LangChain Tools |
| **배포/운영** | 서빙, 모니터링, 거버넌스 | Databricks Agent Framework |
| **UI** | 사용자 인터페이스 | Streamlit on Databricks Apps |

---

## 13. 연습 문제

### 문제 1: 프레임워크 선택 (입문)

아래 시나리오에 가장 적합한 프레임워크를 선택하고 이유를 설명하세요.

> "마케팅팀이 1시간 내에 경쟁사 분석 Agent의 PoC 데모를 만들어야 합니다. 3명의 Agent(조사원, 분석가, 보고서 작성자)가 협업하는 형태입니다."

<details>
<summary>정답 보기</summary>

**CrewAI**가 가장 적합합니다.
- **이유 1**: 역할 기반 멀티에이전트가 CrewAI의 핵심 강점이며, 조사원/분석가/작성자라는 역할을 그대로 Agent에 매핑할 수 있습니다.
- **이유 2**: "1시간 내 PoC"라는 시간 제약을 고려하면 CrewAI의 선언적 API가 가장 빠릅니다.
- **이유 3**: 프로덕션이 아닌 데모 목적이므로 CrewAI의 한계(세밀한 제어, 프로덕션 성숙도)가 문제가 되지 않습니다.

</details>

### 문제 2: LangGraph 그래프 설계 (중급)

다음 요구사항을 LangGraph StateGraph로 설계하세요 (코드가 아닌 노드/엣지 구조).

> "고객 문의를 분류(classification) -> 기술/요금/일반 중 하나로 라우팅 -> 해당 전문 Agent가 처리 -> 응답 품질을 자체 검증(reflection) -> 품질 미달이면 다시 처리, 합격이면 최종 응답"

<details>
<summary>정답 보기</summary>

**노드**: classify, tech_agent, billing_agent, general_agent, quality_check
**엣지**:
- START -> classify
- classify --(conditional)--> tech_agent | billing_agent | general_agent (category에 따라)
- tech_agent -> quality_check
- billing_agent -> quality_check
- general_agent -> quality_check
- quality_check --(conditional)--> END (합격) | 원래 agent 노드 (미달, 루프)

**핵심 포인트**: quality_check에서 원래 agent로 돌아가는 **루프**가 LangGraph에서만 자연스럽게 표현 가능합니다. LangChain Chain으로는 이 패턴을 구현할 수 없습니다. 또한, 무한 루프 방지를 위해 State에 retry_count를 두고 최대 3회까지만 재시도하도록 설계해야 합니다.

</details>

### 문제 3: Databricks Agent Framework 아키텍처 (중급)

아래 코드의 빈칸을 채우세요.

```python
import mlflow
from mlflow.pyfunc import _______(1)_______

class MyAgent(_______(1)_______):
    def _______(2)_______(self, messages, context=None, custom_inputs=None):
        # Agent 로직
        pass

with mlflow.start_run():
    mlflow.pyfunc._______(3)_______(
        artifact_path="agent",
        python_model=MyAgent(),
    )
```

<details>
<summary>정답 보기</summary>

1. `ChatAgent` -- Databricks Agent Framework의 표준 인터페이스
2. `predict` -- 동기 응답 메서드 (스트리밍은 `predict_stream`)
3. `log_model` -- MLflow에 모델 아티팩트를 로깅

</details>

### 문제 4: 프레임워크 비교 분석 (고급)

"LangGraph와 OpenAI Agents SDK의 가장 큰 아키텍처 차이"를 상태 관리(State Management) 관점에서 설명하세요.

<details>
<summary>정답 보기</summary>

**LangGraph**: 명시적 State 객체(TypedDict)를 정의하고, 모든 노드가 이 State를 읽고 수정합니다. Checkpoint를 통해 State의 스냅샷을 저장하고 복원할 수 있어, 장기 실행 워크플로와 Human-in-the-loop에 적합합니다. 개발자가 State 스키마를 직접 설계해야 하므로 유연성이 높지만 복잡합니다.

**OpenAI Agents SDK**: 상태 관리는 주로 대화 히스토리(messages)를 통해 이루어집니다. Handoff 시 전체 대화 히스토리가 다음 Agent에게 전달되며, 별도의 State 객체는 없습니다. 간결하지만, 대화 히스토리 외의 구조화된 상태(예: 주문 처리 단계, 승인 상태)를 관리하기 어렵습니다.

**핵심 차이**: LangGraph는 **"데이터 중심 상태 관리"** (구조화된 State), OpenAI SDK는 **"대화 중심 상태 관리"** (메시지 히스토리)입니다.

</details>

### 문제 5: 실전 아키텍처 설계 (고급)

대기업 고객이 다음 요구사항을 제시했습니다. 전체 아키텍처를 설계하세요.

> "사내 인사(HR) 챗봇을 만들려고 합니다. 급여 문의는 급여 시스템 API를 호출하고, 규정 문의는 사내 문서를 검색하고, 휴가 신청은 사람(HR 담당자) 승인을 받아야 합니다. 200명 직원이 동시에 사용할 수 있어야 합니다."

<details>
<summary>정답 보기</summary>

**추천 아키텍처**: LangGraph + Databricks Agent Framework + Databricks Apps

**LangGraph 워크플로 설계**:
- **Triage Node**: 질문 분류 (급여/규정/휴가/기타)
- **Salary Node**: 급여 시스템 API 호출 (UC Function as Tool)
- **Policy Node**: Vector Search로 사내 규정 문서 RAG
- **Leave Node**: 휴가 신청서 생성 -> `interrupt_before`로 HR 담당자 승인 대기 -> 승인 시 인사 시스템에 등록
- **Quality Check Node**: 응답 적절성 검증 (Reflection)

**Databricks 컴포넌트**:
- **배포**: Databricks Model Serving (서버리스, 200명 동시접속 자동 스케일링)
- **도구**: Unity Catalog Functions (급여 API, 인사 시스템 API) -- 권한 자동 적용
- **검색**: Databricks Vector Search (사내 규정 문서 인덱스)
- **모니터링**: MLflow Tracing (모든 대화/도구 호출 기록)
- **피드백**: Review App (HR팀이 응답 품질 평가)
- **감사**: Inference Tables (모든 요청/응답 Delta 테이블 자동 저장)
- **UI**: Streamlit on Databricks Apps (OAuth 통합으로 SSO 로그인)
- **안전성**: AI Guardrails (개인정보 유출 방지)

**핵심 포인트**:
1. 휴가 신청의 Human-in-the-loop은 LangGraph Checkpoint의 `interrupt_before`로 구현
2. 200명 동시접속은 Model Serving의 서버리스 자동 스케일링으로 해결
3. 급여 데이터 접근 권한은 UC Function의 GRANT/REVOKE로 통제

</details>

---

## 14. 참고 자료

### 공식 문서

| 프레임워크 | 문서 URL |
|-----------|----------|
| LangChain | [https://python.langchain.com/docs/](https://python.langchain.com/docs/) |
| LangGraph | [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/) |
| CrewAI | [https://docs.crewai.com/](https://docs.crewai.com/) |
| OpenAI Agents SDK | [https://openai.github.io/openai-agents-python/](https://openai.github.io/openai-agents-python/) |
| AutoGen | [https://microsoft.github.io/autogen/](https://microsoft.github.io/autogen/) |
| Databricks Agent Framework | [https://docs.databricks.com/en/generative-ai/agent-framework/](https://docs.databricks.com/en/generative-ai/agent-framework/) |
| MLflow Tracing | [https://mlflow.org/docs/latest/tracing/](https://mlflow.org/docs/latest/tracing/) |

### 프로토콜 표준

| 프로토콜 | 문서 URL |
|----------|----------|
| MCP (Model Context Protocol) | [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/) |
| A2A (Agent-to-Agent) | [https://google.github.io/A2A/](https://google.github.io/A2A/) |

### 추가 학습 자료

- **Databricks Agent Bricks 가이드**: [Agent Bricks](../agent-bricks/README.md) -- Knowledge Assistant, Genie Agent, Supervisor Agent 실전 구축
- **RAG 가이드**: [RAG (검색 증강 생성)](../rag/README.md) -- Agent의 도구로 활용되는 RAG 파이프라인 구축
- **MCP 가이드**: [MCP (Model Context Protocol)](../mcp/README.md) -- Agent의 도구 접근 프로토콜 표준
- **A2A 가이드**: [A2A (Agent-to-Agent)](a2a.md) -- Agent 간 통신 프로토콜
- **AI Agent 아키텍처**: [Agent 아키텍처](agent-architecture.md) -- ReAct, Tool Use, Multi-Agent 패턴의 기초
