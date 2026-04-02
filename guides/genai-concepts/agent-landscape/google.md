# Google의 AI Agent 전략

Google은 AI Agent 시대에 **Full-Stack Agent 플랫폼** 전략을 추구합니다. 모델(Gemini), 프로토콜(A2A), 프레임워크(ADK), 빌더 플랫폼(Vertex AI Agent Builder), 엔터프라이즈 배포(Agentspace/Gemini Enterprise), 소비자 에이전트(Jules, Mariner, Astra)까지 -- 에이전트의 전체 생애주기를 수직 통합하는 것이 핵심입니다.

{% hint style="info" %}
**학습 목표**
- Google의 AI Agent 전략이 다른 빅테크(Microsoft, Amazon, Anthropic)와 어떻게 다른지 설명할 수 있다
- A2A 프로토콜의 설계 원칙과 MCP와의 관계를 이해한다
- Vertex AI Agent Builder의 구성 요소와 엔터프라이즈 Agent 구축 방법을 파악한다
- ADK(Agent Development Kit)의 멀티에이전트 패턴을 코드 수준에서 이해한다
- Google의 소비자 에이전트(Jules, Mariner, Astra)의 현재 상태와 전략적 위치를 분석한다
- Databricks 고객 관점에서 Google Agent 생태계의 시사점을 도출한다
{% endhint %}

---

## 1. 전략 개요 -- Google의 Full-Stack Agent 비전

Google의 AI Agent 전략은 " ** 모델에서 프로토콜까지, 하나의 생태계로**"라는 비전 아래 설계되었습니다. 이는 OpenAI(모델 + API 중심), Microsoft(Copilot + Azure 통합 중심), Anthropic(모델 품질 + 안전성 중심)과는 근본적으로 다른 접근입니다.

### Google Agent 스택 전체 구조

| 레이어 | 구성 요소 | 역할 |
|--------|-----------|------|
| **모델** | Gemini 2.5 Pro, Deep Think | Agent의 두뇌. 추론, 계획, 코드 생성 |
| **프로토콜** | A2A (Agent-to-Agent) | Agent 간 통신 표준. MCP와 상호 보완 |
| **프레임워크** | ADK (Agent Development Kit) | 코드 중심 Agent 개발. 멀티에이전트 패턴 내장 |
| **빌더** | Vertex AI Agent Builder | 노코드/로우코드 Agent 구축 + 거버넌스 |
| **엔터프라이즈** | Agentspace / Gemini Enterprise | 기업 내 Agent 배포, 검색, 갤러리 |
| **소비자** | Jules, Mariner, Astra, NotebookLM | 특화 도메인별 에이전트 제품 |

{% hint style="warning" %}
**전략적 맥락**: Google은 검색 시장에서의 지배력이 AI Agent 시대에 약화될 수 있다는 위기감을 갖고 있습니다. 사용자가 "검색" 대신 "에이전트에게 질문"하는 패턴으로 이동하면, 광고 기반 수익 모델의 근간이 흔들립니다. 이것이 Google이 Agent 생태계 전체를 수직 통합하려는 핵심 동기입니다.
{% endhint %}

### 타임라인

| 시기 | 이벤트 | 의미 |
|------|--------|------|
| 2024.12 | Gemini 2.0 Flash + Project Mariner, Jules 발표 | 소비자 Agent 시장 진출 선언 |
| 2024.12 | Project Astra 데모 | 실시간 멀티모달 Agent 비전 |
| 2025.03 | Gemini 2.5 Pro 출시, Vertex AI Agent Builder GA | Agent의 두뇌 + 빌더 플랫폼 동시 완성 |
| 2025.04 | A2A 프로토콜 v0.2 공개, ADK v1.0(Python) 출시 | 프로토콜 + 프레임워크 레이어 확립 |
| 2025.06 | A2A v0.3 (gRPC 지원) | 프로토콜 성능 강화 |
| 2025.08 | Jules GA 출시 | 코딩 Agent 상용화 |
| 2025.10 | Agentspace -> Gemini Enterprise 리브랜딩 | 엔터프라이즈 Agent 플랫폼 본격화 |
| 2025.11 | A2A, Linux Foundation에 기부 | 개방형 표준으로의 전환 |

---

## 2. A2A 프로토콜 (Agent-to-Agent)

A2A는 Google이 2025년 4월에 공개한 **Agent 간 통신을 위한 개방형 프로토콜** 입니다. 서로 다른 프레임워크, 벤더, 언어로 구현된 Agent들이 상호 운용(interoperate)할 수 있도록 하는 것이 목표입니다.

### 핵심 설계 원칙

| 원칙 | 설명 |
|------|------|
| **Agent Card** | 각 Agent가 자신의 능력(capabilities), 입력/출력 형식, 인증 방식을 JSON으로 기술하는 자기 소개서 |
| **Task 기반 통신** | Agent 간 상호작용은 Task(작업) 단위로 이루어짐. 상태 머신: `submitted -> working -> completed/failed` |
| **Streaming 지원** | SSE(Server-Sent Events) 기반 실시간 스트리밍. v0.3부터 gRPC도 지원 |
| **Push Notification** | 장시간 실행 Task에 대한 비동기 알림 지원 |
| **Opaque 실행** | 요청하는 Agent는 실행 Agent의 내부 구현을 알 필요 없음 (캡슐화) |

### A2A vs MCP -- 상호 보완 관계

{% hint style="info" %}
**핵심**: A2A와 MCP는 경쟁이 아닌 **상호 보완** 관계입니다. MCP는 "Agent가 도구를 어떻게 사용하는가"(수직적), A2A는 "Agent가 다른 Agent와 어떻게 대화하는가"(수평적)를 정의합니다.
{% endhint %}

| 비교 항목 | A2A | MCP (Anthropic) |
|-----------|-----|-----------------|
| **목적** | Agent-to-Agent 통신 | Agent-to-Tool 연결 |
| **관계 유형** | 대등한 피어(peer-to-peer) | 클라이언트-서버 (Agent가 Tool을 호출) |
| **추상화 수준** | 고수준 (Task, 대화, 협업) | 저수준 (함수 호출, 데이터 조회) |
| **상태 관리** | Task 상태 머신 내장 | 상태 없음 (stateless) |
| **스트리밍** | SSE + gRPC | SSE |
| **표준화 기구** | Linux Foundation 기부 (2025.11) | 오픈 소스 (Anthropic 주도) |
| **생태계 규모** | 150+ 참여 조직 | 수천 개 커뮤니티 서버 |

### Agent Card 예시

```json
{
  "name": "expense-report-agent",
  "description": "경비 보고서를 자동으로 생성하고 승인 워크플로를 관리합니다",
  "url": "https://agents.example.com/expense",
  "version": "1.2.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true
  },
  "authentication": {
    "schemes": ["OAuth2"],
    "credentials": "https://auth.example.com/.well-known/oauth"
  },
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain", "application/json", "image/png"],
  "skills": [
    {
      "id": "create-report",
      "name": "경비 보고서 생성",
      "description": "영수증 이미지와 설명을 받아 경비 보고서를 생성합니다",
      "tags": ["finance", "expense", "report"]
    },
    {
      "id": "approval-workflow",
      "name": "승인 워크플로",
      "description": "생성된 보고서에 대한 다단계 승인을 관리합니다",
      "tags": ["workflow", "approval"]
    }
  ]
}
```

### 현실적 평가

{% hint style="warning" %}
**솔직한 평가**: A2A는 비전은 매력적이나, 2025년 말 현재 실제 도입 속도는 예상보다 느립니다.

- **150+ 참여 조직** 이라는 숫자는 "관심 표명" 수준이며, 프로덕션 배포는 소수
- MCP가 "도구 연결"이라는 즉각적인 실용성으로 빠르게 확산된 반면, A2A의 "Agent 간 협업"은 아직 대부분의 기업에서 필요 단계에 도달하지 않음
- Linux Foundation 기부는 중립성을 높이려는 시도이나, 실제 거버넌스 주도권은 여전히 Google에 집중
- gRPC 지원(v0.3)은 대규모 배포에서의 성능 문제를 해결하려는 진전

**결론**: A2A는 "필요할 때 알아야 하는 기술"이지, "지금 당장 도입해야 하는 기술"은 아닙니다. 하지만 멀티에이전트 시스템이 보편화되면 핵심 인프라가 될 가능성이 높습니다.
{% endhint %}

---

## 3. Vertex AI Agent Builder

Vertex AI Agent Builder는 Google Cloud의 **엔터프라이즈 Agent 구축 플랫폼** 으로, 2025년 3월 GA(General Availability)되었습니다. "코드를 모르는 비즈니스 사용자부터 코드를 선호하는 개발자까지" 모두를 타겟으로 합니다.

### 핵심 구성 요소

| 구성 요소 | 역할 | 상세 |
|-----------|------|------|
| **Agent Engine** | Agent 런타임 + 관리 | Agent 실행, 세션 관리, 메모리, 로깅. ADK/LangGraph 등 다양한 프레임워크 지원 |
| **Agent Designer** | 노코드 Agent 빌더 | 드래그 앤 드롭으로 Agent 워크플로 설계. 비개발자용 |
| **Tool Governance** | 도구 접근 제어 | 어떤 Agent가 어떤 Tool을 사용할 수 있는지 중앙에서 관리. IAM 연동 |
| **Context Layers** | 문맥 관리 | 세션 문맥, 사용자 프로필, 조직 정책 등 다층 문맥 주입 |
| **Agent Identity** | Agent 인증/인가 | 각 Agent에 고유 ID 부여. OAuth, OIDC 기반 인증. 감사 추적 |

### 아키텍처

```
┌─────────────────────────────────────────────────┐
│              Vertex AI Agent Builder             │
├───────────┬───────────┬──────────┬──────────────┤
│  Agent    │  Agent    │  Tool    │  Agent       │
│  Designer │  Engine   │  Gov.    │  Identity    │
├───────────┴───────────┴──────────┴──────────────┤
│              Context Layers                      │
│  (Session | User Profile | Org Policy | RAG)     │
├─────────────────────────────────────────────────┤
│              Foundation Models                   │
│  (Gemini 2.5 Pro | Gemini Flash | 3rd Party)    │
├─────────────────────────────────────────────────┤
│              Google Cloud Infrastructure         │
│  (Vertex AI | Cloud Run | BigQuery | AlloyDB)    │
└─────────────────────────────────────────────────┘
```

### Agent Engine -- 핵심 런타임

Agent Engine은 Vertex AI Agent Builder의 중추로, Agent의 실행 생명주기를 관리합니다.

**주요 기능:**

| 기능 | 설명 |
|------|------|
| **세션 관리** | 멀티턴 대화의 상태 유지. 세션 ID 기반 문맥 복원 |
| **메모리** | 단기(세션 내) + 장기(사용자별) 메모리. 자동 요약 및 압축 |
| **Tool Registry** | 등록된 Tool 목록 관리. OpenAPI spec 기반 자동 등록 |
| **Observability** | Cloud Trace, Cloud Logging과 통합. Agent 결정 과정 추적 |
| **프레임워크 연동** | ADK, LangGraph, LangChain, CrewAI 등 다양한 프레임워크를 Agent Engine 위에서 실행 가능 |

### Agent Designer -- 노코드 빌더

Agent Designer는 비개발자가 자연어와 시각적 인터페이스로 Agent를 만들 수 있는 도구입니다.

{% hint style="info" %}
**Databricks와의 비교**: Databricks Agent Bricks(Knowledge Assistant, Genie Agent)가 노코드 Agent 빌더라면, Google Agent Designer는 더 넓은 범위의 워크플로 설계를 지원합니다. 하지만 Databricks의 강점은 **데이터와의 깊은 통합**(Unity Catalog, Feature Store, Vector Search)에 있습니다.
{% endhint %}

### Tool Governance -- 핵심 차별점

Tool Governance는 엔터프라이즈 환경에서 " ** 어떤 Agent가 어떤 Tool을 언제 사용할 수 있는가**"를 중앙에서 관리합니다.

| 정책 유형 | 예시 |
|-----------|------|
| **접근 제어** | "경비 에이전트는 SAP API만 호출 가능" |
| **승인 워크플로** | "1000만원 이상 결제 Tool 호출 시 관리자 승인 필요" |
| **사용량 제한** | "분당 최대 100회 외부 API 호출" |
| **데이터 분류** | "PII 데이터를 포함하는 Tool은 특정 Agent만 접근" |
| **감사 로그** | "모든 Tool 호출을 Cloud Audit Logs에 기록" |

---

## 4. Gemini 2.5 Pro & Deep Research

Gemini 2.5 Pro는 2025년 3월 출시된 Google의 최신 플래그십 모델로, **Agent의 두뇌** 역할을 합니다.

### 핵심 역량

| 역량 | 설명 |
|------|------|
| **Thinking Model** | 답변 전에 내부적으로 추론 과정(chain-of-thought)을 수행. "생각하는 모델" |
| **Deep Think** | 복잡한 문제에 대해 더 깊은 추론을 수행하는 모드. 수학, 코딩, 과학 문제에서 탁월 |
| **1M+ Context** | 100만 토큰 이상의 컨텍스트 윈도우. 대규모 코드베이스, 긴 문서 전체를 한 번에 처리 |
| **네이티브 Tool Use** | Function Calling이 모델 학습 과정에 내장. 별도의 프롬프트 엔지니어링 없이 Tool 사용 |
| **멀티모달** | 텍스트, 이미지, 오디오, 비디오를 동시에 처리 |

### Deep Research Agent

Deep Research는 Gemini 2.5 Pro 위에 구축된 **연구 특화 Agent** 입니다.

**작동 방식:**

1. **연구 계획 수립**: 사용자의 질문을 분석하여 다단계 연구 계획을 자동 생성
2. **반복적 검색 & 분석**: 수십 개의 웹 소스를 자동으로 검색, 읽기, 분석
3. **교차 검증**: 여러 소스의 정보를 교차 비교하여 정확성 검증
4. **구조화된 보고서 생성**: 참고 문헌이 포함된 종합 보고서를 자동 작성

{% hint style="info" %}
**활용 시나리오**: Deep Research는 시장 조사, 기술 동향 분석, 학술 리뷰, 경쟁사 분석 등에 특히 유용합니다. 기존에 수일이 걸리던 리서치 작업을 분 단위로 압축합니다.
{% endhint %}

### Gemini 모델 비교

| 모델 | 특징 | Agent 활용 |
|------|------|-----------|
| **Gemini 2.5 Pro** | 최고 성능 추론, Deep Think, 1M+ context | 복잡한 계획 수립, 코드 생성, 다단계 추론이 필요한 Agent |
| **Gemini 2.5 Flash** | 빠른 응답, 비용 효율, Thinking 지원 | 대량 처리, 실시간 응답이 필요한 Agent |
| **Gemini 2.0 Flash** | 멀티모달 네이티브, Tool Use 최적화 | Mariner, Astra 등 실시간 멀티모달 Agent |

---

## 5. ADK (Agent Development Kit)

ADK는 Google이 2025년 4월에 오픈소스로 공개한 **코드 중심(code-first) Agent 개발 프레임워크** 입니다. LangGraph, CrewAI 등과 같은 카테고리이지만, Google의 Agent 인프라(Vertex AI, A2A)와의 긴밀한 통합이 차별점입니다.

### 기본 정보

| 항목 | 내용 |
|------|------|
| **출시** | 2025년 4월 |
| **라이선스** | Apache 2.0 (오픈소스) |
| **언어 지원** | Python v1.0 (안정), TypeScript (안정), Java v0.1 (초기) |
| **모델** | 모델 비종속(model-agnostic). Gemini, GPT, Claude, Llama 등 모두 지원 |
| **핵심 철학** | 코드 중심, 모듈화, 멀티에이전트 네이티브 |

### 기본 Agent 정의

```python
from google.adk import Agent, Tool
from google.adk.models import Gemini

# Tool 정의
@Tool
def search_database(query: str) -> str:
    """회사 내부 데이터베이스에서 정보를 검색합니다."""
    # 실제 DB 쿼리 로직
    return f"검색 결과: {query}에 대한 3건의 결과를 찾았습니다"

@Tool
def send_email(to: str, subject: str, body: str) -> str:
    """이메일을 발송합니다."""
    return f"{to}에게 '{subject}' 이메일을 발송했습니다"

# Agent 정의
agent = Agent(
    name="customer-support-agent",
    model=Gemini("gemini-2.5-pro"),
    instruction="""당신은 고객 지원 에이전트입니다.
    고객의 질문에 데이터베이스를 검색하여 답변하고,
    필요한 경우 관련 부서에 이메일을 발송합니다.""",
    tools=[search_database, send_email],
)

# 실행
response = agent.run("주문번호 12345의 배송 상태를 알려주세요")
```

### 멀티에이전트 -- Sequential 패턴

```python
from google.adk import Agent, SequentialAgent

# 개별 Agent 정의
researcher = Agent(
    name="researcher",
    model=Gemini("gemini-2.5-pro"),
    instruction="주어진 주제에 대해 웹 검색을 수행하고 핵심 정보를 수집합니다.",
    tools=[web_search],
)

writer = Agent(
    name="writer",
    model=Gemini("gemini-2.5-pro"),
    instruction="수집된 정보를 바탕으로 보고서를 작성합니다.",
    tools=[document_writer],
)

reviewer = Agent(
    name="reviewer",
    model=Gemini("gemini-2.5-flash"),
    instruction="보고서의 정확성, 논리, 문법을 검토합니다.",
)

# Sequential Agent: researcher -> writer -> reviewer
pipeline = SequentialAgent(
    name="report-pipeline",
    sub_agents=[researcher, writer, reviewer],
)

result = pipeline.run("2025년 글로벌 AI Agent 시장 동향 보고서를 작성해주세요")
```

### 멀티에이전트 -- Dispatcher 패턴

```python
from google.adk import Agent, DispatcherAgent

# 전문 Agent들
billing_agent = Agent(
    name="billing",
    model=Gemini("gemini-2.5-flash"),
    instruction="결제, 환불, 청구 관련 질문을 처리합니다.",
    tools=[billing_api],
)

tech_support_agent = Agent(
    name="tech-support",
    model=Gemini("gemini-2.5-pro"),
    instruction="기술적 문제를 진단하고 해결책을 제시합니다.",
    tools=[diagnostics, knowledge_base],
)

general_agent = Agent(
    name="general",
    model=Gemini("gemini-2.5-flash"),
    instruction="일반적인 문의사항에 응답합니다.",
)

# Dispatcher: 입력을 분석하여 적절한 Agent로 라우팅
dispatcher = DispatcherAgent(
    name="customer-service-dispatcher",
    sub_agents=[billing_agent, tech_support_agent, general_agent],
    description="고객 문의를 적절한 전문 에이전트에게 라우팅합니다.",
)

result = dispatcher.run("지난달 청구서에서 이중 결제가 된 것 같아요")
# -> billing_agent로 자동 라우팅
```

### 멀티에이전트 -- Generator-Critic 패턴

```python
from google.adk import Agent, GeneratorCriticAgent

generator = Agent(
    name="code-generator",
    model=Gemini("gemini-2.5-pro"),
    instruction="요구사항에 맞는 Python 코드를 생성합니다.",
)

critic = Agent(
    name="code-reviewer",
    model=Gemini("gemini-2.5-pro"),
    instruction="""코드를 검토하고 다음 기준으로 평가합니다:
    - 정확성: 요구사항을 충족하는가
    - 효율성: 시간/공간 복잡도가 적절한가
    - 가독성: 코드가 명확한가
    - 보안: 취약점이 없는가
    문제가 있으면 구체적 개선 방안을 제시합니다.""",
)

# Generator-Critic: 반복적 개선
code_agent = GeneratorCriticAgent(
    name="code-writer",
    generator=generator,
    critic=critic,
    max_iterations=3,  # 최대 3회 개선 반복
)

result = code_agent.run("Redis를 사용하는 rate limiter를 구현해주세요")
```

### 멀티에이전트 -- Parallel 패턴

```python
from google.adk import Agent, ParallelAgent

# 병렬로 실행할 Agent들
market_analyst = Agent(
    name="market-analyst",
    model=Gemini("gemini-2.5-pro"),
    instruction="시장 규모, 성장률, 트렌드를 분석합니다.",
    tools=[market_data_api],
)

competitor_analyst = Agent(
    name="competitor-analyst",
    model=Gemini("gemini-2.5-pro"),
    instruction="경쟁사의 전략, 제품, 시장 점유율을 분석합니다.",
    tools=[web_search, company_database],
)

financial_analyst = Agent(
    name="financial-analyst",
    model=Gemini("gemini-2.5-flash"),
    instruction="재무 데이터를 분석하고 투자 관점의 인사이트를 도출합니다.",
    tools=[financial_api],
)

# Parallel Agent: 동시 실행 후 결과 병합
parallel = ParallelAgent(
    name="comprehensive-analysis",
    sub_agents=[market_analyst, competitor_analyst, financial_analyst],
)

results = parallel.run("한국 AI Agent 시장에 대한 종합 분석을 수행하세요")
```

### ADK vs 다른 프레임워크 비교

| 비교 항목 | ADK | LangGraph | CrewAI | OpenAI Agents SDK |
|-----------|-----|-----------|--------|-------------------|
| **주도** | Google (OSS) | LangChain (OSS) | CrewAI (OSS) | OpenAI (OSS) |
| **모델** | 모델 비종속 | 모델 비종속 | 모델 비종속 | OpenAI 중심 |
| **멀티에이전트** | 네이티브 (4가지 패턴) | 그래프 기반 | 역할 기반 | 핸드오프 기반 |
| **상태 관리** | 세션 내장 | 체크포인트 내장 | 제한적 | 제한적 |
| **A2A 통합** | 네이티브 | 커뮤니티 | 커뮤니티 | 미지원 |
| **엔터프라이즈** | Vertex AI 통합 | LangSmith 통합 | 제한적 | API 기반 |
| **학습 곡선** | 중간 | 높음 (그래프 개념) | 낮음 | 낮음 |

---

## 6. Agentspace / Gemini Enterprise

### 배경

Google은 2025년 10월, 기존의 **Agentspace** 를 **Gemini Enterprise** 로 리브랜딩했습니다. 이는 단순한 이름 변경이 아니라, 기업 내 AI Agent 배포를 위한 **통합 엔터프라이즈 플랫폼** 으로의 전략적 확장을 의미합니다.

### 핵심 기능

| 기능 | 설명 |
|------|------|
| **Agent Gallery** | 기업 내에서 사용 가능한 Agent 목록을 카탈로그 형태로 제공. IT 관리자가 승인한 Agent만 노출 |
| **Agent Designer** | 비개발자가 시각적 인터페이스로 커스텀 Agent를 생성. Vertex AI Agent Builder의 간소화 버전 |
| **Enterprise Search** | Google 검색 기술 기반의 기업 내부 검색. Google Drive, SharePoint, Confluence 등 100+ 커넥터 |
| **데이터 커넥터** | SAP, Salesforce, ServiceNow, Workday 등 주요 SaaS 및 온프레미스 시스템 연동 |
| **보안 & 컴플라이언스** | DLP, 접근 제어, 감사 로그. Google Workspace 보안 정책과 통합 |

### 아키텍처

```
┌────────────────────────────────────────────────────┐
│               Gemini Enterprise (UI)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Agent   │  │  Agent   │  │  Enterprise      │ │
│  │  Gallery │  │  Designer│  │  Search           │ │
│  └──────────┘  └──────────┘  └──────────────────┘ │
├────────────────────────────────────────────────────┤
│               Data Connectors (100+)               │
│  Google Workspace | SharePoint | SAP | Salesforce  │
│  ServiceNow | Workday | Confluence | JIRA | ...    │
├────────────────────────────────────────────────────┤
│            Vertex AI Agent Builder (Backend)        │
│  Agent Engine | Tool Governance | Context Layers    │
├────────────────────────────────────────────────────┤
│               Google Cloud Platform                 │
└────────────────────────────────────────────────────┘
```

### 포지셔닝 -- Microsoft Copilot과의 비교

| 비교 항목 | Gemini Enterprise | Microsoft 365 Copilot |
|-----------|-------------------|----------------------|
| **기반 모델** | Gemini 2.5 Pro | GPT-4o |
| **검색 기술** | Google Search 기술 (강점) | Microsoft Graph + Bing |
| **오피스 통합** | Google Workspace 네이티브 | Microsoft 365 네이티브 |
| **Agent 확장** | Agent Gallery + ADK | Copilot Studio + AI Agents |
| **타겟 고객** | Google Workspace 기업 | Microsoft 365 기업 |
| **커넥터** | 100+ (빠르게 확장 중) | 1000+ (성숙) |

{% hint style="warning" %}
**시장 현실**: Microsoft 365 Copilot이 기업 시장에서 선점 우위를 가지고 있으며, 대부분의 기업이 Microsoft 365를 사용합니다. Gemini Enterprise는 Google Workspace 사용 기업에서 강점을 가지지만, 전체 시장 점유율에서는 추격자 위치입니다.
{% endhint %}

---

## 7. 소비자 Agent 제품군

Google은 특정 도메인에 특화된 소비자 Agent 제품을 적극적으로 출시하고 있습니다.

### Jules -- AI 코딩 Agent

| 항목 | 내용 |
|------|------|
| **발표** | 2024년 12월 (프리뷰), 2025년 8월 (GA) |
| **모델** | Gemini 2.5 Pro |
| **핵심 기능** | GitHub 이슈 자동 해결, 코드 변경 생성, PR 자동 생성 |
| **실행 환경** | 클라우드 VM (샌드박스) |
| **GitHub 통합** | Issue 할당 -> 코드 분석 -> 변경 생성 -> PR 생성 -> 리뷰 반영 |

**요금제:**

| 티어 | 가격 | 포함 내용 |
|------|------|-----------|
| **Free** | $0/월 | 월 5회 Task, 기본 기능 |
| **Pro** | $19.99/월 (Google One AI Premium 포함) | 무제한 Task, 우선 처리 |
| **Ultra** | $249.99/월 (AI Ultra 포함) | 최고 성능, Deep Think, Mariner 포함 |

{% hint style="info" %}
**경쟁 구도**: Jules는 GitHub Copilot Workspace(Microsoft), Devin(Cognition), Cursor Agent와 직접 경쟁합니다. 차별점은 Gemini 2.5 Pro의 1M+ 컨텍스트로 대규모 코드베이스 전체를 이해할 수 있다는 점입니다.
{% endhint %}

### Project Mariner -- 브라우저 Agent

| 항목 | 내용 |
|------|------|
| **발표** | 2024년 12월 |
| **핵심 기능** | 웹 브라우저를 자율적으로 조작하여 복잡한 웹 작업 수행 |
| **실행 환경** | Google Cloud VM에서 Chrome 브라우저를 원격 조작 |
| **사용 가능** | AI Ultra 구독 ($249.99/월) 필요 |

**주요 유스케이스:**

| 유스케이스 | 설명 |
|-----------|------|
| **웹 리서치** | 여러 사이트를 순회하며 정보 수집, 비교, 종합 |
| **폼 작성** | 복잡한 웹 폼을 자동으로 작성 (보험 청구, 관공서 서류 등) |
| **쇼핑 비교** | 여러 쇼핑몰에서 가격/리뷰 비교 |
| **예약** | 레스토랑, 항공권, 호텔 등 예약 자동화 |

{% hint style="warning" %}
**제약**: Mariner는 클라우드 VM에서 실행되므로, 사용자 로컬 브라우저의 쿠키/세션을 활용할 수 없습니다. 또한 결제, 로그인 등 민감한 작업에서는 사용자 확인을 요청합니다. 가격이 월 $249.99(AI Ultra)로 높아 대중 시장 침투에는 시간이 걸릴 전망입니다.
{% endhint %}

### Project Astra -- 실시간 멀티모달 Agent

| 항목 | 내용 |
|------|------|
| **비전** | "모든 것을 보고, 듣고, 이해하는" 범용 AI 비서 |
| **입력** | 카메라(실시간 영상), 마이크(음성), 화면 공유 |
| **출력** | 음성(자연스러운 대화), 텍스트, 시각적 표시 |
| **연동** | Google Search, Google Maps, Google Lens 통합 |
| **디바이스** | 스마트폰, 스마트 글래스(프로토타입), 데스크톱 |

**핵심 기술:**

| 기술 | 역할 |
|------|------|
| **Search Live** | Astra가 실시간으로 Google 검색을 수행하여 정보 보강 |
| **Spatial Understanding** | 카메라 입력에서 공간/물체를 이해하고 맥락적 정보 제공 |
| **Persistent Memory** | 이전 대화와 관찰을 기억하여 지속적인 도움 제공 |

{% hint style="info" %}
**장기적 시사점**: Astra는 Google이 그리는 AI Agent의 **최종 형태** 입니다. 키보드/마우스가 아닌 자연어+시각으로 상호작용하는 "항상 함께하는 AI 비서". 현재는 데모 수준이지만, 이 방향이 곧 모든 빅테크의 목표가 될 것입니다.
{% endhint %}

### NotebookLM -- 연구 워크스페이스

| 항목 | 내용 |
|------|------|
| **목적** | 문서 기반 AI 연구 도우미 |
| **컨텍스트** | 최대 1M 토큰 (약 100만 단어 분량) |
| **소스** | 최대 300개 소스 문서 (PDF, 웹페이지, Google Docs, YouTube 등) |
| **핵심 기능** | 소스 기반 Q&A, 요약, 브리핑 문서 생성, 오디오 개요(Audio Overview) |
| **에이전트 기능** | 2025년 업데이트로 에이전트적 능력 추가: 소스 자동 발견, 관련 문서 추천, 능동적 인사이트 제공 |

**NotebookLM의 에이전트적 진화:**

| 기존 (수동적) | 2025 (에이전트적) |
|--------------|------------------|
| 사용자가 소스를 수동 추가 | AI가 관련 소스를 자동 발견/추천 |
| 질문에만 반응 | 능동적으로 인사이트 제안 |
| 단일 소스 분석 | 여러 소스 간 교차 분석 |
| 텍스트 출력만 | 오디오 개요, 시각적 요약 생성 |

---

## 8. ADK 멀티에이전트 패턴 심화

ADK가 제공하는 네 가지 멀티에이전트 패턴은 각각 다른 문제 유형에 최적화되어 있습니다. 적절한 패턴 선택이 Agent 시스템의 성공을 좌우합니다.

### 패턴 선택 가이드

| 패턴 | 최적 유스케이스 | 핵심 특성 |
|------|----------------|-----------|
| **Sequential** | 명확한 단계별 파이프라인. 각 단계의 출력이 다음 단계의 입력 | 예측 가능, 디버깅 용이, 순서 보장 |
| **Dispatcher** | 입력 유형에 따라 다른 전문가가 처리해야 하는 경우 | 라우팅 정확도가 핵심, 확장 용이 |
| **Generator-Critic** | 결과물의 품질을 반복적으로 개선해야 하는 경우 | 자기 개선, 품질 보장, 비용 증가 주의 |
| **Parallel** | 독립적인 여러 작업을 동시에 수행하여 응답 시간 단축 | 처리량 극대화, 결과 병합 전략 필요 |

### 패턴 조합 -- 실전 아키텍처

실제 프로덕션에서는 단일 패턴이 아닌 **패턴의 조합** 이 일반적입니다.

| 계층 | 파이프라인 | 패턴 | 처리 흐름 |
|------|----------|------|----------|
| **Dispatcher** | Dispatcher Agent | Routing | 고객 문의를 분류하여 적절한 파이프라인으로 라우팅 |
| **파이프라인 1** | Billing Pipeline | Sequential | 조회 → 분석 → 처리 → 확인 |
| **파이프라인 2** | Tech Support Pipeline | Sequential | 진단 → 해결 → 검증 → 안내 |
| **파이프라인 3** | Complaint Pipeline | Sequential + Gen-Critic | 분석 → 답변 작성 + 검토 (반복) → 에스컬레이션 |

{% hint style="info" %}
**설계 원칙**: 패턴 선택 시 다음을 고려하세요.
- **지연 시간(Latency)**: Sequential은 누적 지연, Parallel은 최대 Agent의 지연
- **비용**: Generator-Critic은 반복 횟수에 비례하여 비용 증가
- **안정성**: 각 Agent의 실패가 전체에 미치는 영향 분석 (blast radius)
- **관찰 가능성**: 복잡한 조합일수록 모니터링/디버깅 도구 필수
{% endhint %}

---

## 9. Databricks 고객 관점의 시사점

### Google Agent 생태계와 Databricks의 관계

| 영역 | Google | Databricks | 관계 |
|------|--------|------------|------|
| **모델** | Gemini 2.5 Pro | Foundation Model APIs (Gemini 포함) | Databricks에서 Gemini 호출 가능 |
| **Agent 빌더** | Agent Builder + Agent Designer | Agent Bricks + Builder App | 동일 카테고리, 다른 강점 |
| **데이터 접근** | BigQuery, AlloyDB | Unity Catalog, Delta Lake | Databricks의 데이터 거버넌스가 더 성숙 |
| **프레임워크** | ADK | Agent Framework (LangGraph 기반) | 모두 오픈소스 프레임워크 위에 거버넌스 레이어 |
| **프로토콜** | A2A | MCP 지원 (A2A도 향후 고려) | 상호 보완적 |
| **엔터프라이즈** | Gemini Enterprise | Databricks Workspace + Apps | 다른 레이어 |

### 핵심 시사점

{% hint style="success" %}
**Databricks 고객을 위한 권장 사항:**

1. **모델 선택의 자유**: Databricks Foundation Model APIs를 통해 Gemini 2.5 Pro를 호출할 수 있습니다. 특정 Task에서 Gemini가 더 나은 성능을 보인다면 자유롭게 활용하세요.

2. **데이터 레이어는 Databricks**: Google Agent Builder가 아무리 좋아도, 이미 Unity Catalog에 체계화된 데이터를 BigQuery로 옮길 이유는 없습니다. Databricks의 데이터 거버넌스 + Google의 모델 성능을 조합하는 것이 최적입니다.

3. **ADK는 참고, 실전은 LangGraph**: ADK의 멀티에이전트 패턴(Sequential, Dispatcher, Generator-Critic, Parallel)은 설계 패턴으로 참고할 가치가 높습니다. 하지만 Databricks 환경에서는 LangGraph + Agent Framework 조합이 거버넌스, 배포, 모니터링 측면에서 더 성숙합니다.

4. **A2A는 관망**: A2A 프로토콜은 아직 초기 단계입니다. MCP 기반 도구 통합에 먼저 집중하고, A2A는 멀티에이전트 시스템이 실제로 필요해질 때 검토하세요.

5. **Jules/Mariner는 개인 생산성 도구**: 이 제품들은 Databricks와 직접적으로 관련되지 않지만, AI Agent가 실제 업무를 수행하는 사례로 참고할 수 있습니다.
{% endhint %}

### Google Cloud + Databricks 통합 아키텍처

Google Cloud 위에서 Databricks를 운영하는 고객의 경우:

| 통합 포인트 | 방법 |
|------------|------|
| **Gemini 모델 호출** | Databricks Foundation Model APIs 또는 Vertex AI Endpoint 직접 호출 |
| **BigQuery 데이터** | Unity Catalog의 외부 테이블 또는 Lakehouse Federation으로 BigQuery 데이터 접근 |
| **Vertex AI Search** | Agent의 Tool로 Vertex AI Search API를 등록하여 Google의 검색 기술 활용 |
| **A2A 연동** | Databricks에서 구축한 Agent에 A2A Agent Card를 부여하여 Google 생태계 Agent와 통신 (향후) |

---

## 10. 고객 FAQ

### Q1. "Google의 AI Agent 전략이 우리 Databricks 환경에 어떤 영향을 미칩니까?"

직접적인 영향은 제한적입니다. Databricks는 모델 비종속(model-agnostic) 플랫폼이므로, Google의 Gemini 모델이 좋아질수록 Databricks 고객도 혜택을 받습니다. Agent Bricks/Builder App은 Google Agent Builder와 독립적으로 발전하며, 두 플랫폼은 경쟁보다는 상호 보완적 위치입니다.

### Q2. "A2A를 지금 도입해야 합니까?"

아닙니다. A2A는 "여러 벤더의 Agent가 협업해야 하는" 시나리오에서 가치가 있습니다. 대부분의 기업은 아직 단일 Agent도 제대로 구축하지 못한 단계이므로, 먼저 MCP 기반의 도구 통합과 단일 Agent 성숙에 집중하세요.

### Q3. "ADK를 써야 합니까, LangGraph를 써야 합니까?"

Databricks 환경에서는 **LangGraph를 권장** 합니다. 이유:
- Databricks Agent Framework이 LangGraph를 네이티브로 지원
- MLflow 연동, 모델 서빙, A/B 테스트 등 프로덕션 기능이 LangGraph 기반으로 최적화
- ADK는 Vertex AI와의 통합에 최적화되어 있어, Databricks 환경에서는 추가 작업이 필요

다만 ADK의 멀티에이전트 패턴 설계는 LangGraph 구현 시에도 참고할 가치가 있습니다.

### Q4. "Jules나 Mariner를 기업에서 활용할 수 있습니까?"

개인 생산성 도구로는 활용 가능하지만, 기업 워크플로에 통합하기에는 아직 이릅니다. 보안 정책(데이터가 Google Cloud VM에서 처리됨), 비용(AI Ultra $249.99/월), 커스터마이징 제한 등을 고려해야 합니다.

### Q5. "Gemini Enterprise와 Databricks 중 엔터프라이즈 AI 플랫폼으로 어느 것을 선택해야 합니까?"

역할이 다릅니다:
- **Gemini Enterprise**: 엔드유저를 위한 AI 비서 (검색, 문서 요약, 일상 업무 자동화)
- **Databricks**: 데이터 팀을 위한 AI/ML 플랫폼 (데이터 엔지니어링, ML, Agent 구축, 거버넌스)

두 플랫폼은 경쟁이 아닌 **다른 레이어** 에 위치합니다. 대부분의 기업은 둘 다 필요합니다.

### Q6. "NotebookLM을 사내 지식 관리에 활용할 수 있습니까?"

개인 또는 소규모 팀의 리서치 도구로는 우수합니다. 하지만 기업 수준의 지식 관리에는 접근 제어, 감사 로그, 데이터 거버넌스 등이 부족합니다. 기업 환경에서는 Databricks의 Vector Search + Agent Bricks(Knowledge Assistant)가 더 적합합니다.

---

## 11. 참고 자료

### 공식 문서
- [A2A Protocol Specification](https://github.com/google/A2A) -- A2A 프로토콜 GitHub 저장소
- [Google ADK Documentation](https://google.github.io/adk-docs/) -- Agent Development Kit 공식 문서
- [Vertex AI Agent Builder](https://cloud.google.com/products/agent-builder) -- Google Cloud 공식 페이지
- [Gemini 2.5 Pro Technical Report](https://deepmind.google/technologies/gemini/) -- DeepMind 기술 보고서
- [Jules](https://jules.google/) -- Jules 공식 사이트
- [NotebookLM](https://notebooklm.google/) -- NotebookLM 공식 사이트

### 발표 및 블로그
- [A2A: A new open protocol for agent-to-agent communication](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) -- Google Developers Blog
- [Introducing the Agent Development Kit](https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/) -- ADK 공식 소개
- [Announcing Gemini 2.5 Pro](https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/) -- Google Blog
- [Project Astra: Our vision for AI assistants](https://deepmind.google/technologies/project-astra/) -- DeepMind

### 관련 가이드 (본 블로그 내)
- [A2A (Agent-to-Agent) 프로토콜](../a2a-protocol/README.md) -- A2A 프로토콜 상세 가이드
- [AI Agent 아키텍처](../agent-architecture/README.md) -- Agent 아키텍처 기초
- [Agent 프레임워크 생태계](../agent-frameworks-detail/README.md) -- 프레임워크 비교
- [MCP (Model Context Protocol)](../../mcp/README.md) -- MCP 가이드
