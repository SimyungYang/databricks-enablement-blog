# Agent Memory 시스템

[← AI Agent 아키텍처 개요](README.md)

---

Agent가 맥락을 유지하고 과거 경험으로부터 학습하려면 **메모리(Memory)** 가 필요합니다. 인간의 기억 체계와 유사하게, Agent의 메모리도 여러 유형으로 나뉩니다.

---

## 왜 Agent Memory가 핵심인가

### 메모리 없는 Agent의 한계

메모리가 없는 Agent는 **매 대화가 "첫 만남"처럼 시작** 됩니다. 사용자가 누구인지, 이전에 어떤 대화를 나눴는지, 어떤 선호를 가지고 있는지 전혀 기억하지 못합니다.

{% hint style="warning" %}
**비유**: 메모리 없는 Agent = **매일 기억을 잃는 직원**. 어제 했던 일을 오늘 또 처음부터 설명해야 합니다. 고객이 "지난주에 말씀드린 환불 건이요"라고 하면, "어떤 환불 건이요?"라고 되물어야 합니다. 이런 Agent에게 복잡한 업무를 맡길 수 있을까요?
{% endhint %}

구체적으로 메모리가 없을 때 발생하는 문제는 다음과 같습니다:

| 문제 | 설명 | 영향 |
|------|------|------|
| **반복 질문** | 매 세션마다 동일한 정보를 다시 요청 | 사용자 피로도 급증 |
| **맥락 단절** | 이전 대화와 연결된 후속 질문에 대응 불가 | 복잡한 업무 처리 불가 |
| **개인화 불가** | 사용자 선호/습관을 반영한 응답 생성 불가 | 일률적이고 기계적인 경험 |
| **학습 불가** | 과거 실수를 반복하고 성공 패턴을 축적하지 못함 | Agent 품질이 정체 |
| **멀티턴 실패** | 긴 대화에서 초반 맥락을 잊어버림 | 복잡한 작업 완료율 저하 |

### 메모리가 Agent 성능에 미치는 영향

업계 벤치마크와 실제 운영 데이터에 따르면, 적절한 메모리 시스템을 도입한 Agent는 다음과 같은 성능 개선을 보입니다:

- **작업 완료율 +30%**: 이전 맥락을 기억하므로 멀티스텝 작업에서 중간에 실패하는 빈도가 대폭 감소
- **사용자 만족도 +40%**: 반복 질문이 줄어들고 개인화된 응답을 제공하여 체감 품질 향상
- **평균 대화 턴 수 -25%**: 이미 알고 있는 정보를 다시 물어볼 필요가 없어 업무 처리 속도 향상
- **재방문율 +50%**: "기억해주는 Agent"에 대한 사용자 신뢰도 상승

{% hint style="info" %}
**핵심**: Memory는 Agent를 **단순 도구에서 신뢰할 수 있는 동료** 로 격상시키는 핵심 요소입니다. 단순 Q&A 챗봇이라면 메모리 없이도 가능하지만, **업무 자동화 Agent** 를 목표로 한다면 메모리 설계가 필수입니다.
{% endhint %}

---

## 메모리 유형

### Short-term Memory (단기 기억)

현재 대화의 히스토리(메시지 목록)를 의미합니다. LLM의 Context Window 크기에 의해 제한되며, 모든 Agent가 기본적으로 가지는 가장 기본적인 메모리입니다.

#### Context Window 관리 전략

LLM의 Context Window는 무한하지 않습니다. 대화가 길어질수록 토큰 예산이 소진되며, 이를 효과적으로 관리하는 전략이 필요합니다.

| 전략 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **Sliding Window** | 최근 N개 메시지만 유지 | 구현 간단 | 오래된 중요 맥락 손실 |
| **Summarization** | 오래된 대화를 요약하여 압축 | 핵심 정보 보존 | 요약 품질에 의존, 추가 LLM 호출 비용 |
| **Token Budget** | 토큰 수 기준으로 관리 | 정밀한 비용 제어 | 메시지 중간에 잘릴 수 있음 |
| **Selective Retention** | 중요도 점수 기반 선별 유지 | 최적의 정보 밀도 | 구현 복잡도 높음 |

#### LangGraph에서 대화 히스토리 관리

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_databricks import ChatDatabricks

# 모델 설정
model = ChatDatabricks(endpoint="databricks-claude-sonnet-4")

# 체크포인트로 대화 상태 자동 저장
checkpointer = MemorySaver()
agent = create_react_agent(model, tools=[], checkpointer=checkpointer)

# thread_id로 대화 세션 구분 — 같은 thread_id면 이전 대화를 기억
config = {"configurable": {"thread_id": "user-123-session-1"}}

# 첫 번째 대화
result1 = agent.invoke(
    {"messages": [("user", "저는 데이터 엔지니어 김철수입니다.")]},
    config
)

# 두 번째 대화 — 같은 thread_id이므로 이전 대화를 기억
result2 = agent.invoke(
    {"messages": [("user", "제 이름이 뭐였죠?")]},
    config
)
# → "김철수님이시죠" (이전 대화를 기억)
```

#### Context Window가 가득 찼을 때 전략

대화가 매우 길어져 Context Window 한계에 도달하면 세 가지 접근법을 선택할 수 있습니다:

**1. 요약 후 교체 (추천)**

```python
from langchain_core.messages import SystemMessage

def summarize_and_compress(messages, model, max_tokens=50000):
    """오래된 메시지를 요약하여 Context Window 공간 확보"""
    if estimate_tokens(messages) < max_tokens:
        return messages

    # 오래된 메시지들을 요약
    old_messages = messages[:-10]  # 최근 10개는 유지
    recent_messages = messages[-10:]

    summary = model.invoke([
        SystemMessage(content="아래 대화를 핵심 정보만 간결하게 요약하세요."),
        *old_messages
    ])

    # 요약본 + 최근 메시지로 교체
    return [
        SystemMessage(content=f"[이전 대화 요약]\n{summary.content}"),
        *recent_messages
    ]
```

**2. Sliding Window (단순하지만 효과적)**

```python
def sliding_window(messages, window_size=20):
    """최근 N개 메시지만 유지"""
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    conversation = [m for m in messages if not isinstance(m, SystemMessage)]
    return system_msgs + conversation[-window_size:]
```

**3. 중요도 기반 선별 유지 (고급)**

```python
def selective_retention(messages, model, max_tokens=50000):
    """각 메시지의 중요도를 평가하여 선별 유지"""
    scored = []
    for msg in messages:
        # 숫자, 이름, 날짜 등 핵심 정보 포함 여부로 점수 부여
        score = calculate_importance(msg)
        scored.append((score, msg))

    scored.sort(key=lambda x: x[0], reverse=True)

    retained = []
    total_tokens = 0
    for score, msg in scored:
        tokens = estimate_tokens([msg])
        if total_tokens + tokens <= max_tokens:
            retained.append(msg)
            total_tokens += tokens

    # 시간순 재정렬
    return sort_by_timestamp(retained)
```

---

### Long-term Memory (장기 기억)

세션을 넘어 영속적으로 저장되는 정보입니다. 일반적으로 Vector DB나 외부 데이터베이스로 구현하며, Agent가 관련성이 있을 때 과거 상호작용을 검색하여 활용합니다.

#### 구현 아키텍처 3가지

| 아키텍처 | 저장 방식 | 검색 방식 | 장점 | 단점 |
|----------|----------|----------|------|------|
| **Vector DB 기반** | 대화/문서를 임베딩하여 벡터 저장 | 의미적 유사도 검색 | 자연어로 검색 가능, 유연함 | 정확한 필터링 어려움 |
| **구조화 DB 기반** | (user_id, key, value) 테이블 저장 | SQL 쿼리로 정확 조회 | 정확하고 빠른 조회 | 의미적 검색 불가 |
| **하이브리드** | Vector DB + 구조화 DB 결합 | 유사도 검색 + SQL 필터링 | 두 장점 결합, **가장 실용적** | 구현 복잡도 높음 |

#### Databricks Vector Search로 Long-term Memory 구현

```python
from databricks.vector_search.client import VectorSearchClient
from datetime import datetime

vsc = VectorSearchClient()
index = vsc.get_index(
    endpoint_name="memory_vs_endpoint",
    index_name="catalog.schema.memory_index"
)

def store_memory(user_id: str, content: str, metadata: dict = None):
    """대화 내용을 임베딩하여 Vector Search에 저장"""
    timestamp = datetime.now().isoformat()
    record = {
        "id": f"{user_id}_{timestamp}",
        "text": content,
        "user_id": user_id,
        "timestamp": timestamp,
        "memory_type": "conversation",
    }
    if metadata:
        record.update(metadata)
    index.upsert([record])

def recall_memory(user_id: str, query: str, top_k: int = 5):
    """관련 기억을 의미 검색으로 가져오기"""
    results = index.similarity_search(
        query_text=query,
        columns=["text", "timestamp", "memory_type"],
        filters={"user_id": user_id},
        num_results=top_k
    )
    return results.get("result", {}).get("data_array", [])

# 사용 예시
store_memory("user-456", "고객이 환불 정책에 대해 문의함. 30일 이내 전액 환불 안내 완료.")
memories = recall_memory("user-456", "환불 관련 이전 문의")
```

#### Lakebase(PostgreSQL)로 구조화 메모리 구현

```python
import psycopg2
from datetime import datetime

# Lakebase 연결 (Databricks 서버리스 PostgreSQL)
conn = psycopg2.connect(
    host="<lakebase-endpoint>.cloud.databricks.com",
    port=5432,
    dbname="agent_memory_db",
    user="token",
    password="<databricks-token>"
)
cursor = conn.cursor()

def store_user_preference(user_id: str, key: str, value: str):
    """사용자 프로필 메모리 저장 (UPSERT)"""
    cursor.execute("""
        INSERT INTO agent_memory (user_id, key, value, updated_at)
        VALUES (%s, %s, %s, NOW())
        ON CONFLICT (user_id, key)
        DO UPDATE SET value = %s, updated_at = NOW()
    """, (user_id, key, value, value))
    conn.commit()

def get_user_preferences(user_id: str) -> list:
    """사용자의 모든 저장된 선호/프로필 조회"""
    cursor.execute(
        "SELECT key, value FROM agent_memory WHERE user_id = %s ORDER BY updated_at DESC",
        (user_id,)
    )
    return cursor.fetchall()

# 사용 예시
store_user_preference("user-456", "preferred_language", "한국어")
store_user_preference("user-456", "department", "데이터 엔지니어링팀")
store_user_preference("user-456", "timezone", "Asia/Seoul")

prefs = get_user_preferences("user-456")
# → [("timezone", "Asia/Seoul"), ("department", "데이터 엔지니어링팀"), ...]
```

#### 하이브리드 메모리 아키텍처 (권장)

실무에서 가장 효과적인 방식은 **Vector Search + Lakebase를 함께 사용** 하는 것입니다:

```
┌─────────────────────────────────────────────────────┐
│                 Agent System Prompt                  │
│                                                     │
│  [Profile Memory]    ← Lakebase (구조화 데이터)       │
│  이름: 김철수, 부서: DE팀, 언어: 한국어                │
│                                                     │
│  [Recent Context]    ← Short-term (현재 대화)         │
│  최근 3개 메시지                                      │
│                                                     │
│  [Relevant History]  ← Vector Search (의미 검색)      │
│  과거 유사한 대화 3건                                  │
└─────────────────────────────────────────────────────┘
```

---

### Episodic Memory (에피소드 기억)

과거 문제 해결 과정의 기록입니다. "지난번에 비슷한 오류가 발생했을 때, 이렇게 해결했다..."와 같은 경험 기반 학습을 가능하게 합니다.

#### 구현 패턴: MLflow Tracing 기반 경험 학습

Agent의 모든 실행은 MLflow Tracing을 통해 기록됩니다. 성공한 실행 경로와 실패한 경로를 분류하고, 유사한 상황에서 성공 패턴을 우선 추천하는 방식으로 Episodic Memory를 구현할 수 있습니다.

```python
import mlflow
from mlflow.client import MlflowClient

client = MlflowClient()

def search_successful_episodes(query: str, top_k: int = 3) -> list:
    """과거 성공한 에피소드를 검색하여 참고"""
    # MLflow에서 성공한 실행 이력 조회
    runs = client.search_runs(
        experiment_ids=["<experiment_id>"],
        filter_string='attributes.status = "FINISHED" AND tags.outcome = "success"',
        order_by=["metrics.user_satisfaction DESC"],
        max_results=top_k
    )

    episodes = []
    for run in runs:
        episodes.append({
            "task": run.data.tags.get("task_description", ""),
            "approach": run.data.tags.get("approach", ""),
            "tools_used": run.data.tags.get("tools_used", ""),
            "outcome": run.data.tags.get("outcome", ""),
            "duration_sec": run.data.metrics.get("duration_sec", 0),
        })
    return episodes

def record_episode(task: str, approach: str, tools: list, outcome: str):
    """현재 에피소드를 기록하여 미래 참조용으로 저장"""
    with mlflow.start_run(tags={
        "task_description": task,
        "approach": approach,
        "tools_used": ",".join(tools),
        "outcome": outcome,
    }) as run:
        mlflow.log_metric("user_satisfaction", 1.0 if outcome == "success" else 0.0)

# 사용 예시: 유사 에피소드 검색 후 프롬프트에 주입
past_episodes = search_successful_episodes("ETL 파이프라인 오류 해결")
episode_context = "\n".join([
    f"- 과거 사례: {ep['task']} → {ep['approach']} (결과: {ep['outcome']})"
    for ep in past_episodes
])
# → System Prompt에 [Past Experiences] 섹션으로 삽입
```

#### 경험 기반 학습 아키텍처

```
[사용자 요청] → [유사 과거 에피소드 검색]
                        ↓
               성공 에피소드 발견?
              ┌── Yes ──┐── No ──┐
              ↓                   ↓
      성공 경로 우선 시도     기본 추론으로 진행
              ↓                   ↓
         결과 기록 ←──────── 결과 기록
              ↓
      [새 에피소드로 저장]
```

---

### Working Memory (작업 기억)

현재 진행 중인 추론을 위한 임시 메모장입니다. 계획(Plan), 중간 결과, 현재 상태 등을 저장하며, Agent State로 구현되는 경우가 많습니다.

#### LangGraph State를 활용한 Working Memory

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

class AgentState(TypedDict):
    """Agent의 Working Memory를 State로 관리"""
    messages: Annotated[list, operator.add]  # 대화 히스토리
    plan: list[str]                           # 현재 실행 계획
    current_step: int                         # 진행 중인 단계
    intermediate_results: dict                # 중간 결과 저장
    scratchpad: str                           # Agent의 메모장

def planning_node(state: AgentState) -> dict:
    """작업 계획을 수립하고 Working Memory에 저장"""
    plan = generate_plan(state["messages"][-1])
    return {
        "plan": plan,
        "current_step": 0,
        "scratchpad": f"총 {len(plan)}단계 계획 수립 완료"
    }

def execution_node(state: AgentState) -> dict:
    """현재 단계를 실행하고 중간 결과를 Working Memory에 기록"""
    step = state["plan"][state["current_step"]]
    result = execute_step(step, state["intermediate_results"])

    new_results = {**state["intermediate_results"], f"step_{state['current_step']}": result}
    return {
        "current_step": state["current_step"] + 1,
        "intermediate_results": new_results,
        "scratchpad": state["scratchpad"] + f"\n단계 {state['current_step']} 완료: {result}"
    }

# 그래프 구성
graph = StateGraph(AgentState)
graph.add_node("plan", planning_node)
graph.add_node("execute", execution_node)
```

#### Agent Scratchpad 패턴

**Scratchpad** 는 Agent가 추론 과정에서 중간 메모를 남기는 공간입니다. 복잡한 멀티스텝 작업에서 특히 유용합니다.

```python
def build_scratchpad_prompt(state: AgentState) -> str:
    """Working Memory의 scratchpad를 프롬프트에 반영"""
    scratchpad = state.get("scratchpad", "")
    intermediate = state.get("intermediate_results", {})

    prompt_section = "[Working Memory - 현재 진행 상황]\n"
    if scratchpad:
        prompt_section += f"메모: {scratchpad}\n"
    if intermediate:
        prompt_section += "중간 결과:\n"
        for key, val in intermediate.items():
            prompt_section += f"  - {key}: {val}\n"

    return prompt_section
```

---

## 메모리 유형별 비교

| 메모리 유형 | 저장 메커니즘 | Databricks 도구 | 예시 |
|------------|-------------|----------------|------|
| **Short-term** | LLM Context Window (메시지 리스트) | ChatAgent messages 파라미터 | 현재 대화의 이전 질문/답변 참조 |
| **Long-term** | Vector DB / 외부 DB | Vector Search, Lakebase (PostgreSQL) | 3개월 전 고객 문의 내역 검색 |
| **Episodic** | 구조화된 로그 저장소 | MLflow Tracking, Delta Table | "지난번 ETL 실패는 스키마 변경 때문이었음" |
| **Working** | Agent State (인메모리) | LangGraph State, ChatAgent context | 현재 5단계 중 3단계 진행 중, 중간 계산 결과 |

{% hint style="success" %}
**예시**: 고객 지원 Agent가 "지난번에 문의하신 환불 건은 어떻게 되셨나요?"라고 물을 수 있으려면 **Long-term Memory** 가 필요합니다. 현재 세션의 대화만으로는 이전 세션의 맥락을 알 수 없기 때문입니다.
{% endhint %}

{% hint style="warning" %}
현재 대부분의 Agent는 **Short-term Memory만** 가집니다. Long-term Memory는 Vector Search나 Lakebase(PostgreSQL)를 활용하여 별도 구현해야 합니다. Agent 프레임워크가 자동으로 제공하는 것이 아닙니다.
{% endhint %}

---

## 현업에서의 Agent Memory 구현 패턴

실제 기업들이 운영 환경에서 채택하는 메모리 패턴은 다음과 같이 분류됩니다:

| 패턴 | 설명 | 적합한 사용 사례 | 복잡도 |
|------|------|---------------|--------|
| **Session Memory** | 대화 세션 동안만 유지, 세션 종료 시 소멸 | FAQ 챗봇, 단순 Q&A | 낮음 |
| **User Profile Memory** | 사용자별 선호/이력을 영속적으로 저장 | 개인화 서비스, CRM 연동 Agent | 중간 |
| **Knowledge Memory** | Agent가 학습한 도메인 지식을 축적 | 도메인 전문 Agent, 사내 정책 Agent | 높음 |
| **Team Memory** | 여러 Agent가 공유하는 공동 기억 | Multi-Agent 시스템, Supervisor 패턴 | 매우 높음 |

### Session Memory

가장 기본적인 패턴으로, ChatAgent의 `messages` 파라미터가 이에 해당합니다. 별도 인프라 없이 구현 가능하며, 대부분의 Agent 프레임워크에서 기본 제공합니다.

### User Profile Memory

사용자가 처음 접속했을 때 프로필 정보를 로드하여 System Prompt에 주입합니다. 대화 중 새롭게 파악된 정보(직책 변경, 새로운 선호 등)를 자동 갱신합니다.

### Knowledge Memory

Agent가 업무를 수행하면서 새로 학습한 지식을 축적합니다. 예를 들어, "이 회사의 환불 정책은 구매 후 30일 이내"라는 정보를 한 번 확인하면 메모리에 저장하여, 이후 같은 질문에 즉시 답변합니다.

### Team Memory

Multi-Agent 시스템에서 Supervisor Agent와 Worker Agent들이 공유하는 메모리입니다. 한 Agent가 발견한 정보를 다른 Agent가 활용할 수 있어, 중복 작업을 방지합니다.

---

## Memory 솔루션 비교

| 솔루션 | 유형 | 특징 | Databricks 연동 |
|--------|------|------|---------------|
| **Databricks Vector Search** | 벡터 기반 | Unity Catalog 통합, 권한 자동 적용, 서버리스 | 네이티브 |
| **Databricks Lakebase** | 구조화 DB | PostgreSQL 호환, 서버리스, ACID 트랜잭션 | 네이티브 |
| **Redis** | 인메모리 KV | 초고속 읽기/쓰기, TTL 자동 만료 지원 | External 연결 필요 |
| **Mem0** | AI 메모리 전용 | 자동 메모리 추출/정리/검색, LLM 기반 | External 연결 필요 |
| **LangGraph Checkpointer** | 상태 관리 | 대화 상태 자동 저장/복구, thread 기반 | MLflow 통합 가능 |
| **Amazon Bedrock AgentCore Memory** | AWS 관리형 | Bedrock Agent 전용 메모리 서비스 | External 연결 필요 |
| **Azure Cosmos DB Agent Memory** | Azure 관리형 | 글로벌 분산 DB 기반, 낮은 레이턴시 | External 연결 필요 |

{% hint style="info" %}
**Databricks 환경에서의 권장 조합**: **Vector Search**(의미 검색용 Long-term Memory) + **Lakebase**(구조화 프로필 데이터) + **LangGraph Checkpointer**(세션 관리). 이 조합은 별도 외부 서비스 없이 Databricks 플랫폼 내에서 완결됩니다.
{% endhint %}

---

## 메모리 설계 베스트 프랙티스

### 1. TTL(Time-To-Live) 설정

오래된 메모리는 **가치가 떨어지거나 오히려 해로울 수 있습니다**. 3년 전 선호했던 제품을 지금도 추천하면 오히려 역효과입니다.

| 메모리 유형 | 권장 TTL | 근거 |
|------------|---------|------|
| 대화 히스토리 (세부) | 30일 | 세부 대화는 빠르게 가치 감소 |
| 사용자 선호 | 90일 | 선호는 비교적 안정적이나 변할 수 있음 |
| 학습된 도메인 지식 | 1년 | 정책/규정 변경 주기에 맞춤 |
| 에피소드 (성공 패턴) | 6개월 | 도구/API 변경으로 오래된 패턴이 무효화될 수 있음 |

### 2. 메모리 요약(Consolidation)

주기적으로 세부 기억을 요약하여 저장 공간을 절약하고 검색 품질을 높입니다.

```python
def consolidate_memories(user_id: str, days_old: int = 30):
    """30일 이상 된 세부 기억을 요약하여 압축"""
    old_memories = get_memories_older_than(user_id, days_old)

    if not old_memories:
        return

    # LLM으로 오래된 기억들을 요약
    summary = model.invoke(f"""
    다음은 사용자 {user_id}의 과거 대화 기록입니다.
    핵심 정보만 추출하여 간결하게 요약하세요:
    {format_memories(old_memories)}
    """)

    # 요약본 저장 + 원본 삭제
    store_memory(user_id, summary.content, {"memory_type": "consolidated"})
    delete_memories(old_memories)
```

### 3. 선택적 망각(Selective Forgetting)

모든 것을 기억하는 것이 능사가 아닙니다. 관련 없는 기억은 삭제하고, 특히 **개인정보 삭제 요청(GDPR Right to Erasure)** 에 대응할 수 있어야 합니다.

```python
def forget_user_data(user_id: str):
    """GDPR 삭제 요청 대응: 특정 사용자의 모든 메모리 삭제"""
    # Vector Search에서 삭제
    index.delete(filter={"user_id": user_id})

    # Lakebase에서 삭제
    cursor.execute("DELETE FROM agent_memory WHERE user_id = %s", (user_id,))
    conn.commit()

    # MLflow 에피소드에서 태그 익명화
    anonymize_episodes(user_id)
```

### 4. 메모리 범위(Scoping)

메모리의 접근 범위를 명확히 구분해야 합니다:

| 범위 | 접근 주체 | 예시 |
|------|----------|------|
| **Session-level** | 현재 대화 세션만 | 현재 대화의 맥락 |
| **User-level** | 특정 사용자의 모든 세션 | 사용자 선호, 과거 이력 |
| **Agent-level** | 특정 Agent의 모든 사용자 | Agent가 학습한 도메인 지식 |
| **Global-level** | 모든 Agent, 모든 사용자 | 공통 정책, 회사 규정 |

### 5. 검색 전략: 복합 랭킹

메모리 검색 시 Vector similarity만으로는 부족합니다. 여러 신호를 결합하여 최적의 기억을 찾아야 합니다.

```python
def recall_with_ranking(user_id: str, query: str, top_k: int = 5):
    """복합 랭킹으로 최적의 메모리 검색"""
    # 1단계: Vector similarity로 후보 검색 (넉넉하게)
    candidates = recall_memory(user_id, query, top_k=top_k * 3)

    # 2단계: 복합 점수 계산
    scored = []
    for mem in candidates:
        similarity_score = mem["score"]  # 의미적 유사도
        recency_score = calculate_recency_weight(mem["timestamp"])  # 최신성
        importance_score = mem.get("importance", 0.5)  # 메타데이터 중요도

        # 가중 합산
        final_score = (
            0.5 * similarity_score +
            0.3 * recency_score +
            0.2 * importance_score
        )
        scored.append((final_score, mem))

    # 3단계: 최종 순위로 반환
    scored.sort(key=lambda x: x[0], reverse=True)
    return [mem for _, mem in scored[:top_k]]
```

---

## 메모리 안티패턴

실무에서 흔히 발견되는 메모리 설계 실수와 해결 방법입니다:

| 안티패턴 | 문제 | 해결 |
|---------|------|------|
| **무한 축적** | 메모리가 무한히 커져 검색 성능 저하, 비용 증가 | TTL 설정 + 주기적 Consolidation |
| **Privacy 위반** | 개인정보(PII)가 메모리에 영구 저장 | PII 마스킹, 삭제 정책, GDPR 대응 로직 |
| **Context Pollution** | 관련 없는 기억이 프롬프트에 포함되어 답변 품질 저하 | 관련도 임계값 설정 (예: similarity > 0.7만 포함) |
| **메모리 충돌** | 서로 모순되는 기억이 공존 (예: "부서: 마케팅" vs "부서: 영업") | 최신 기억 우선(timestamp), 충돌 감지 및 해결 로직 |
| **과도한 의존** | 메모리 시스템 장애 시 Agent 전체가 멈춤 | 메모리를 graceful degradation으로 설계 (없어도 기본 동작) |
| **비용 폭발** | 모든 대화를 벡터 임베딩하여 저장하면 스토리지/컴퓨팅 비용 급증 | 중요한 정보만 선별 저장, 요약 후 저장 |

{% hint style="warning" %}
**Context Pollution은 가장 흔한 안티패턴** 입니다. 관련 없는 과거 기억이 프롬프트에 포함되면 LLM이 혼란을 일으켜 오히려 메모리가 없는 것보다 나쁜 결과를 만들 수 있습니다. 반드시 **관련도 임계값** 을 설정하세요.
{% endhint %}

---

## Databricks에서 Agent Memory 구축 가이드

실전에서 Databricks 플랫폼 위에 Agent Memory를 단계별로 구축하는 방법입니다.

### Step 1. Session Memory — 기본 제공

ChatAgent의 `messages` 파라미터를 활용하면 별도 구현 없이 세션 내 메모리를 사용할 수 있습니다.

```python
from databricks.agents import ChatAgent

class MyAgent(ChatAgent):
    def predict(self, messages, context=None):
        # messages에 이전 대화 히스토리가 자동 포함됨
        # → 별도 메모리 구현 불필요 (세션 내 한정)
        response = self.model.invoke(messages)
        return response
```

### Step 2. User Profile Memory — Lakebase 활용

```sql
-- Lakebase에 사용자 프로필 테이블 생성
CREATE TABLE agent_memory (
    user_id     VARCHAR(255) NOT NULL,
    key         VARCHAR(255) NOT NULL,
    value       TEXT,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    expires_at  TIMESTAMP,  -- TTL 지원
    PRIMARY KEY (user_id, key)
);

-- 인덱스 추가
CREATE INDEX idx_memory_user ON agent_memory(user_id);
CREATE INDEX idx_memory_expires ON agent_memory(expires_at);
```

### Step 3. Semantic Memory — Vector Search 활용

```sql
-- Delta Table로 메모리 저장소 생성
CREATE TABLE catalog.schema.conversation_memory (
    id          STRING,
    user_id     STRING,
    content     STRING,
    timestamp   TIMESTAMP,
    memory_type STRING,
    importance  DOUBLE DEFAULT 0.5
);

-- Vector Search Index 생성
CREATE VECTOR SEARCH INDEX memory_index
ON catalog.schema.conversation_memory (content)
USING MODEL `databricks-gte-large-en`
WITH (endpoint_name = "memory_vs_endpoint");
```

### Step 4. 하이브리드 통합 — System Prompt에 메모리 주입

모든 메모리를 통합하여 Agent의 System Prompt에 주입하는 최종 단계입니다.

```python
def build_memory_enhanced_prompt(user_id: str, current_query: str) -> str:
    """모든 메모리 소스를 결합하여 풍부한 프롬프트 생성"""

    # 1. User Profile Memory (Lakebase)
    profile = get_user_preferences(user_id)
    profile_section = "[사용자 프로필]\n"
    for key, value in profile:
        profile_section += f"- {key}: {value}\n"

    # 2. Relevant History (Vector Search)
    relevant_memories = recall_with_ranking(user_id, current_query, top_k=3)
    history_section = "[관련 과거 대화]\n"
    for mem in relevant_memories:
        history_section += f"- ({mem['timestamp']}): {mem['text']}\n"

    # 3. Episodic Memory (MLflow)
    episodes = search_successful_episodes(current_query, top_k=2)
    episode_section = "[참고할 과거 경험]\n"
    for ep in episodes:
        episode_section += f"- {ep['task']}: {ep['approach']} → {ep['outcome']}\n"

    # 통합 System Prompt
    system_prompt = f"""당신은 전문 업무 지원 Agent입니다.

{profile_section}
{history_section}
{episode_section}

위 메모리를 참고하여 사용자에게 개인화되고 맥락에 맞는 답변을 제공하세요.
새롭게 파악된 중요 정보는 메모리에 저장하세요."""

    return system_prompt
```

---

## 고객 FAQ

### "메모리 없이 Agent를 운영할 수 있나요?"

**단순 Q&A는 가능합니다.**"오늘 날씨 알려줘", "이 함수 사용법 알려줘" 같은 단발성 질문에는 메모리가 필요 없습니다. 하지만 다음 중 하나라도 해당되면 메모리가 필수입니다:

- 사용자별 **개인화** 가 필요한 경우
- 이전 대화의 **맥락을 이어가야** 하는 경우
- Agent가 **과거 경험으로부터 학습** 해야 하는 경우
- **멀티스텝 작업** 에서 중간 결과를 추적해야 하는 경우

### "메모리 구현에 어떤 DB를 써야 하나요?"

Databricks 환경이라면 **Vector Search + Lakebase 조합을 권장** 합니다.

- **Vector Search**: 자연어 기반 의미 검색. "지난번 환불 관련 대화" 같은 퍼지 검색에 적합. Unity Catalog 통합으로 권한 관리 자동.
- **Lakebase (PostgreSQL)**: 구조화된 데이터 저장. 사용자 프로필, 설정값 등 정확한 조회에 적합. 서버리스로 관리 부담 최소.
- **두 가지를 결합** 하면 "이름이 뭐였지?" (구조화 조회)와 "비슷한 문제를 겪은 적 있나?" (의미 검색)를 모두 처리할 수 있습니다.

### "메모리 데이터는 어떻게 보호하나요?"

세 가지 계층으로 보호합니다:

1. **접근 제어**: Unity Catalog ACL을 통해 메모리 테이블/인덱스에 대한 읽기/쓰기 권한을 세밀하게 관리합니다. Agent별, 팀별로 접근 가능한 메모리 범위를 제한할 수 있습니다.
2. **PII 마스킹**: 메모리 저장 전에 개인정보(이름, 전화번호, 주민번호 등)를 자동 탐지하여 마스킹합니다. Databricks의 AI Functions(`ai_mask()`)를 활용하면 편리합니다.
3. **TTL 기반 삭제**: 보존 기한이 지난 메모리는 자동 삭제하여 불필요한 데이터 보유를 방지합니다. GDPR/PIPA 등 개인정보 보호법 준수에 필수적입니다.

### "메모리가 많아지면 성능이 느려지지 않나요?"

적절히 설계하면 문제가 되지 않습니다. 핵심 전략은 다음과 같습니다:

- **TTL + Consolidation**: 오래된 세부 기억은 요약하고, 만료된 기억은 삭제
- **관련도 임계값**: Vector Search에서 유사도가 낮은 결과는 필터링
- **인덱싱 최적화**: Lakebase에 적절한 인덱스 설정, Vector Search에 메타데이터 필터 활용
- **비동기 저장**: 메모리 저장은 응답 반환 후 비동기로 처리하여 사용자 체감 지연 최소화

---

[다음: Multi-Agent 패턴 →](multi-agent.md)
