# AI Agent 아키텍처

AI Agent는 LLM에 도구 사용(Tool Use)과 추론 루프(Reasoning Loop)를 결합하여, 복잡한 작업을 자율적으로 수행하는 시스템입니다.

{% hint style="info" %}
Databricks는 Mosaic AI Agent Framework를 통해 엔터프라이즈 환경에서 Agent를 구축, 평가, 배포할 수 있는 통합 환경을 제공합니다.
{% endhint %}

---

## AI Agent란?

AI Agent는 단순 LLM 호출과 다릅니다. 핵심 차이는 **자율적 의사결정**과 **행동 실행** 능력입니다.

| 구분 | 일반 LLM 호출 | AI Agent |
|------|---------------|----------|
| 입력 → 출력 | 1회 호출, 1회 응답 | 다단계 추론 및 행동 반복 |
| 도구 사용 | 없음 | API, DB, 검색 등 도구 호출 |
| 의사결정 | 없음 | 다음 행동을 스스로 결정 |
| 상태 관리 | 없음 | 작업 진행 상태 유지 |

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

| 단계 | 설명 | 예시 |
|------|------|------|
| **Thought** | 현재 상황 분석, 다음 행동 결정 | "매출 데이터를 확인해야 합니다" |
| **Action** | 도구 호출 또는 API 실행 | `query_sql("SELECT SUM(revenue)...")` |
| **Observation** | 도구 실행 결과 확인 | "총 매출: 1,234,567원" |
| **반복** | 목표 달성까지 위 과정 반복 | 최종 답변 생성 |

{% hint style="warning" %}
ReAct 루프가 무한히 반복되지 않도록 **최대 반복 횟수**와 **타임아웃**을 반드시 설정하세요.
{% endhint %}

---

## Tool Use / Function Calling

Tool Use는 LLM이 외부 도구(함수)를 호출할 수 있는 기능입니다.

### 동작 흐름

1. 사용자가 질문을 전송
2. LLM이 적합한 도구와 파라미터를 결정
3. 시스템이 도구를 실행하고 결과 반환
4. LLM이 결과를 해석하여 최종 응답 생성

### 도구 정의 예시 (Databricks Agent Framework)

```python
from databricks.sdk import WorkspaceClient

# Unity Catalog Function을 도구로 등록
tools = [
    {"function_name": "catalog.schema.search_documents"},
    {"function_name": "catalog.schema.get_customer_info"},
]
```

---

## Agent 프레임워크 비교

| 프레임워크 | 개발사 | 특징 | Databricks 통합 |
|-----------|--------|------|-----------------|
| **Databricks Agent Framework** | Databricks | Unity Catalog 통합, MLflow 추적, 원클릭 배포 | 네이티브 |
| **LangChain / LangGraph** | LangChain Inc. | 가장 큰 생태계, 유연한 체인 구성 | MLflow 통합 |
| **CrewAI** | CrewAI | 역할 기반 멀티에이전트, 직관적 API | MLflow 로깅 |
| **AutoGen** | Microsoft | 멀티에이전트 대화, 코드 실행 | 커스텀 통합 |
| **OpenAI Agents SDK** | OpenAI | Handoff 패턴, Guardrail 내장 | 커스텀 통합 |

{% hint style="success" %}
**Databricks 환경 권장**: Databricks Agent Framework를 기본으로 사용하고, 복잡한 워크플로우가 필요한 경우 LangGraph를 MLflow와 함께 활용하세요.
{% endhint %}

---

## Single Agent vs Multi-Agent

### Single Agent

하나의 LLM이 모든 도구와 추론을 담당합니다.

- **장점**: 단순, 디버깅 쉬움, 지연시간 낮음
- **단점**: 복잡한 작업에서 정확도 저하, 도구 수 제한
- **적합**: FAQ 봇, 문서 검색, 단순 데이터 조회

### Multi-Agent

여러 전문 Agent가 협업하여 복잡한 작업을 수행합니다.

- **장점**: 역할 분담으로 정확도 향상, 확장 가능
- **단점**: 복잡도 증가, 에이전트 간 통신 오버헤드
- **적합**: 복합 분석, 크로스 도메인 질의, 자동화 워크플로우

---

## Multi-Agent 아키텍처 패턴

### 1. Supervisor 패턴

| 구성 요소 | 역할 |
|-----------|------|
| **Supervisor Agent** | 작업 분배, 결과 종합, 최종 응답 |
| **Worker Agent A** | 데이터 검색 전문 |
| **Worker Agent B** | SQL 분석 전문 |
| **Worker Agent C** | 문서 요약 전문 |

Supervisor가 사용자 요청을 분석하고, 적합한 Worker에게 하위 작업을 위임합니다. Databricks Agent Bricks의 Supervisor Agent가 이 패턴을 사용합니다.

### 2. Swarm 패턴

중앙 관리자 없이 Agent들이 **Handoff** 방식으로 작업을 전달합니다.

- Agent A가 작업 중 자신의 범위를 벗어나면 Agent B에게 전달
- 각 Agent가 자율적으로 다음 Agent를 결정
- OpenAI Agents SDK의 Handoff가 이 패턴의 대표 구현

### 3. 계층형 패턴

Supervisor 패턴을 다층으로 확장하여, Sub-Supervisor가 하위 Agent 그룹을 관리합니다.

---

## Databricks Agent Framework 활용

| 기능 | 설명 |
|------|------|
| **UC Functions as Tools** | Unity Catalog 함수를 Agent 도구로 등록 |
| **Vector Search** | RAG를 위한 벡터 검색 통합 |
| **MLflow Tracing** | Agent 실행 과정 전체 추적 |
| **Review App** | 인간 피드백 수집 인터페이스 |
| **Model Serving** | 원클릭 Agent 배포 |
| **Guardrails** | 입출력 안전성 필터링 |

---

## 참고 자료

- [Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022)](https://arxiv.org/abs/2210.03629)
- [Databricks Agent Framework 문서](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [AutoGen 문서](https://microsoft.github.io/autogen/)
