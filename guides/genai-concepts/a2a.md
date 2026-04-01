# A2A (Agent-to-Agent Protocol)

A2A는 Google이 2025년 4월에 발표한 **에이전트 간 통신을 위한 개방형 프로토콜**입니다. 서로 다른 프레임워크와 벤더에서 만든 AI Agent들이 표준화된 방식으로 협업할 수 있게 합니다.

{% hint style="info" %}
**학습 목표**
- A2A가 등장하게 된 배경(단일 에이전트의 한계)을 설명할 수 있다
- A2A와 MCP의 차이를 명확히 구분하고, 함께 사용하는 아키텍처를 설계할 수 있다
- Agent Card의 구조와 역할을 JSON 수준에서 이해한다
- Task 라이프사이클(submitted → working → completed)을 추적할 수 있다
- 실제 시나리오(여행 예약 등)에서 A2A 기반 에이전트 협업을 설계할 수 있다
{% endhint %}

---

## A2A 등장 배경: 왜 에이전트 간 통신 표준이 필요한가?

### 단일 에이전트의 한계

하나의 AI Agent가 모든 작업을 처리하는 데에는 근본적인 한계가 있습니다.

| 한계 | 설명 |
|------|------|
| **도구 수 제한** | Agent에 도구가 15~20개를 넘으면 LLM의 도구 선택 정확도가 급감 |
| **전문성 분산** | 한 Agent가 모든 도메인을 다루면 각 영역의 정확도가 떨어짐 |
| **컨텍스트 한계** | System Prompt + 도구 설명 + 대화 이력이 컨텍스트 윈도우를 빠르게 소모 |
| **벤더 종속** | 같은 프레임워크 안에서만 Agent 협업 가능 (LangGraph↔LangGraph만 가능) |

{% hint style="success" %}
**비유**: 한 사람이 회계, 법률, 마케팅, 개발을 모두 하면 전문성이 떨어집니다. 각 분야 전문가가 **표준화된 업무 프로토콜**로 협업하는 것이 더 효율적입니다. A2A는 이 "업무 프로토콜"에 해당합니다.
{% endhint %}

### 기존 Multi-Agent의 문제

기존에는 여러 Agent를 협업시키려면 동일한 프레임워크 안에서만 가능했습니다. A2A는 이 제약을 없애고, **이기종 Agent 간 상호운용성**을 제공합니다.

| 기존 방식 | A2A 방식 |
|-----------|----------|
| 같은 프레임워크 안에서만 협업 | 프레임워크 무관하게 HTTP로 협업 |
| Agent 내부 구현을 알아야 연동 | Agent Card만 읽으면 연동 가능 |
| 독자적 통신 방식 | JSON-RPC 2.0 표준 |
| 벤더 종속 | 오픈 프로토콜 |

---

## A2A 핵심 설계 원칙

| 원칙 | 설명 |
|------|------|
| **Agentic** | Agent는 도구가 아닌 자율적 행위자로 취급 |
| **Composable** | 기존 표준(HTTP, JSON-RPC, SSE)을 조합하여 구현 |
| **Opaque** | Agent 내부 구현(프롬프트, 모델)을 공개하지 않음 |
| **Enterprise-ready** | 인증, 보안, 모니터링 등 엔터프라이즈 요구사항 충족 |

---

## A2A vs MCP 비교

| 항목 | MCP (Model Context Protocol) | A2A (Agent-to-Agent) |
|------|------------------------------|----------------------|
| **개발사** | Anthropic (2024.11) | Google (2025.04) |
| **목적** | LLM이 외부 도구/데이터에 접근 | Agent 간 작업 위임 및 협업 |
| **통신 대상** | LLM ↔ Tool/Data Source | Agent ↔ Agent |
| **비유** | USB-C 포트 (장치 연결) | 표준 외교 프로토콜 (국가 간 통신) |
| **Agent 취급** | 도구 제공자 (수동적) | 자율적 행위자 (능동적) |
| **상태 관리** | Stateless (각 호출 독립) | Stateful (Task 생명주기 관리) |
| **스트리밍** | 지원 | 지원 (SSE 기반) |
| **관계** | 보완적 — 함께 사용 가능 | 보완적 — 함께 사용 가능 |

{% hint style="success" %}
**한 마디 정리**: MCP는 "Agent가 도구를 쓰는 방법", A2A는 "Agent가 다른 Agent에게 일을 맡기는 방법"입니다.
{% endhint %}

---

## A2A 핵심 개념

### 1. Agent Card (에이전트 자기소개)

각 Agent는 자신의 능력, 입력/출력 형식, 엔드포인트를 JSON 형태로 공개합니다. 다른 Agent가 이 카드를 읽고 협업 대상을 선택합니다.

**게시 위치**: `/.well-known/agent.json`

**Agent Card JSON 예시**:

```json
{
  "name": "항공권 예약 에이전트",
  "description": "국내외 항공권 검색 및 예약을 처리합니다",
  "url": "https://flights.example.com/a2a",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true
  },
  "skills": [
    {
      "id": "search_flights",
      "name": "항공편 검색",
      "description": "출발지, 도착지, 날짜로 항공편을 검색합니다",
      "inputModes": ["text/plain", "application/json"],
      "outputModes": ["application/json"]
    },
    {
      "id": "book_flight",
      "name": "항공편 예약",
      "description": "선택한 항공편을 예약합니다",
      "inputModes": ["application/json"],
      "outputModes": ["application/json"]
    }
  ],
  "authentication": {
    "schemes": ["OAuth2"]
  }
}
```

| 필드 | 설명 |
|------|------|
| `name` | Agent 이름 — 사람과 다른 Agent가 읽을 수 있는 이름 |
| `description` | 능력 설명 — 어떤 작업을 할 수 있는지 |
| `url` | A2A 엔드포인트 — 작업 요청을 보낼 주소 |
| `capabilities` | 지원 기능 — 스트리밍, 푸시 알림 등 |
| `skills` | 수행 가능한 작업 목록 — 각 스킬의 입출력 형식 포함 |
| `authentication` | 인증 방식 — OAuth2, API Key 등 |

### 2. Task (작업 단위) — 라이프사이클

A2A에서 모든 상호작용은 Task 중심으로 이루어집니다. Task는 명확한 상태 전이를 거칩니다.

```
submitted → working → completed
              │
              ├→ input-required → (추가 입력 제공) → working
              │
              ├→ failed
              │
              └→ canceled
```

| 상태 | 설명 | 전이 가능 상태 |
|------|------|---------------|
| `submitted` | 작업 제출됨 | working, failed, canceled |
| `working` | 처리 중 | completed, input-required, failed, canceled |
| `input-required` | 추가 정보 필요 | working (정보 제공 후), canceled |
| `completed` | 완료 | (종료) |
| `failed` | 실패 | (종료) |
| `canceled` | 취소 | (종료) |

{% hint style="info" %}
`input-required`는 A2A의 핵심 상태입니다. Agent가 작업 중 "추가 정보가 필요합니다"라고 요청할 수 있어, 진정한 **대화형 협업**이 가능합니다.
{% endhint %}

### 3. Message & Artifact

- **Message**: Agent 간 대화 메시지 (텍스트, 구조화 데이터)
- **Artifact**: Task의 결과물 (파일, 이미지, JSON 등)
- 하나의 Task에 여러 Message와 Artifact가 포함될 수 있음

### 4. Streaming & Push Notifications

- **Streaming (SSE)**: 장기 실행 Task의 중간 진행 상황을 실시간 스트리밍
- **Push Notifications**: Task 상태 변경 시 콜백 URL로 알림 전송

---

## A2A 동작 흐름

| 단계 | Client Agent | Server Agent |
|------|-------------|-------------|
| 1. 발견 | Agent Card 조회 (`/.well-known/agent.json`) | Agent Card 제공 |
| 2. 요청 | Task 생성 (`tasks/send`) | Task 수신 |
| 3. 처리 | 대기 또는 스트리밍 수신 | 자율적으로 작업 수행 |
| 4. 협의 | 추가 정보 제공 (`input-required` 응답 시) | 추가 정보 요청 가능 |
| 5. 완료 | Artifact 수신 | 결과 + Artifact 반환 |

{% hint style="info" %}
A2A는 JSON-RPC 2.0 기반으로, HTTP POST를 통해 통신합니다. 기존 웹 인프라와 자연스럽게 통합됩니다.
{% endhint %}

---

## 구체적 시나리오: 여행 예약 시스템

사용자 요청: **"3월 15일~18일 제주도 여행을 예약해주세요. 항공편과 호텔, 결제까지 해주세요."**

| 단계 | Agent | 작업 | A2A 상태 |
|------|-------|------|----------|
| 1 | **여행 플래너 Agent** (Coordinator) | 요청 분석, 하위 작업 분배 | — |
| 2 | 여행 → **항공 Agent** | "3/15 서울→제주, 3/18 제주→서울" 검색 요청 | submitted → working |
| 3 | **항공 Agent** | 3개 항공편 옵션 반환 | completed (Artifact: 항공편 목록) |
| 4 | 여행 → **호텔 Agent** | "3/15~18 제주 호텔" 검색 요청 | submitted → working |
| 5 | **호텔 Agent** | 추가 정보 필요: "1인실? 2인실?" | input-required |
| 6 | 여행 → **호텔 Agent** | "2인실, 조식 포함" 추가 정보 제공 | working |
| 7 | **호텔 Agent** | 3개 호텔 옵션 반환 | completed (Artifact: 호텔 목록) |
| 8 | **여행 플래너** | 항공+호텔 옵션 종합하여 사용자에게 제시 | — |
| 9 | 여행 → **결제 Agent** | 선택된 옵션 결제 요청 | submitted → working → completed |
| 10 | **여행 플래너** | 최종 예약 확인서 생성 | 전체 완료 |

{% hint style="success" %}
**핵심 포인트**: 각 Agent는 서로 다른 회사/프레임워크로 만들어졌을 수 있습니다. 항공 Agent는 Python + LangGraph, 호텔 Agent는 Java + Spring AI, 결제 Agent는 Node.js — 모두 A2A라는 공통 프로토콜로 통신합니다.
{% endhint %}

---

## A2A + MCP 결합 아키텍처

실제 엔터프라이즈 환경에서는 A2A와 MCP가 함께 사용됩니다.

```
사용자 ──→ [여행 플래너 Agent]
               │
               ├── A2A ──→ [항공 Agent] ──── MCP ──→ 항공사 API (도구)
               │                        ──── MCP ──→ 가격 DB (데이터)
               │
               ├── A2A ──→ [호텔 Agent] ──── MCP ──→ 호텔 예약 시스템
               │
               └── A2A ──→ [결제 Agent] ──── MCP ──→ PG사 API
```

| 레이어 | 프로토콜 | 역할 | 예시 |
|--------|----------|------|------|
| Agent ↔ Agent | **A2A** | 전문 Agent 간 작업 위임 | 여행 Agent → 항공 Agent |
| Agent ↔ Tool | **MCP** | Agent가 외부 도구/데이터 접근 | 항공 Agent → 항공사 API |
| Agent ↔ Human | UI/API | 사용자 인터페이스 | 챗봇 UI |

{% hint style="info" %}
**설계 원칙**: "Agent 간 대화"에는 A2A, "Agent가 도구를 사용"하는 데에는 MCP. 이 구분이 명확하면 아키텍처가 깔끔해집니다.
{% endhint %}

---

## A2A 보안 고려사항

엔터프라이즈 환경에서 A2A를 도입할 때, 보안은 가장 중요한 설계 요소입니다.

### 인증 (Authentication)

- Agent Card의 `authentication.schemes` 필드로 지원하는 인증 방식을 명시합니다
- **OAuth2**가 권장 방식입니다. 토큰 만료, 스코프 제한 등 세밀한 제어가 가능합니다
- **API Key**는 구현이 간단하지만 보안이 약합니다. 개발/테스트 환경에만 권장합니다
- **Mutual TLS (mTLS)**는 양방향 인증서 검증으로, 높은 보안이 필요한 금융/의료 환경에 권장됩니다

### 인가 (Authorization)

- Agent가 요청할 수 있는 skill 범위를 제한해야 합니다
- Task 생성 권한과 특정 skill 호출 권한을 분리하여 관리합니다
- 예: "항공 Agent는 `search_flights`만 가능, `book_flight`는 별도 권한 필요"와 같이 세분화합니다

### 데이터 보안

- Agent 간 전달되는 모든 데이터는 **TLS 암호화가 필수**입니다
- PII(개인정보) 전달 시 마스킹 또는 토큰화를 적용합니다
- 민감 데이터는 Artifact로 직접 전달하지 않고, **참조 ID만 전달**하여 수신 Agent가 별도 인증 후 조회하도록 합니다

### Trust Boundary (신뢰 경계)

- **내부 Agent**와 **외부 Agent**를 명확히 구분합니다
- 외부 Agent의 응답은 항상 검증합니다 (LLM-as-Judge 또는 규칙 기반 검증)
- 외부 Agent에게 **쓰기 권한**을 부여할 때는 특히 주의가 필요합니다

### 주요 위협과 대응 방안

| 위협 | 설명 | 대응 방안 |
|------|------|----------|
| **Agent 위장** | 악의적 Agent가 정상 Agent를 사칭 | Agent Card 서명 검증, mTLS |
| **데이터 유출** | 민감 정보가 외부 Agent에 전달 | PII 마스킹, 참조 ID 사용 |
| **권한 상승** | Agent가 허용 범위 밖의 행동 수행 | skill별 세분화된 인가 |
| **중간자 공격** | 통신 가로채기 | TLS 암호화 필수 |

{% hint style="warning" %}
보안 설계의 핵심 원칙: **최소 권한 원칙(Principle of Least Privilege)**을 적용하세요. 각 Agent에게는 작업 수행에 필요한 최소한의 skill과 데이터 접근 권한만 부여합니다.
{% endhint %}

---

## A2A 구현 예시 (Python)

{% hint style="info" %}
A2A는 아직 초기 단계이며, 공식 SDK가 활발히 발전 중입니다. 아래는 핵심 흐름을 이해하기 위한 간소화된 예시입니다.
{% endhint %}

### A2A Server (Agent 제공자)

```python
# a2a_server.py — 간단한 A2A 서버 예시 (FastAPI 기반)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Agent Card 제공
@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": "데이터 분석 Agent",
        "description": "SQL 쿼리 기반 데이터 분석을 수행합니다",
        "url": "https://data-agent.example.com",
        "version": "1.0.0",
        "capabilities": {"streaming": False},
        "skills": [{
            "id": "analyze_data",
            "name": "데이터 분석",
            "description": "자연어 질문을 SQL로 변환하여 데이터를 분석합니다",
            "inputModes": ["text/plain"],
            "outputModes": ["application/json"]
        }]
    }

class TaskRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict
    id: str

# Task 수신 및 처리
@app.post("/")
async def handle_task(request: TaskRequest):
    if request.method == "tasks/send":
        # Task 처리 로직
        user_message = request.params["message"]["parts"][0]["text"]
        # LLM + SQL 실행으로 분석 수행
        result = await analyze_with_llm(user_message)

        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "id": request.params.get("id", "task-001"),
                "status": {"state": "completed"},
                "artifacts": [{
                    "parts": [{"type": "text", "text": result}]
                }]
            }
        }
```

### A2A Client (Agent 소비자)

```python
# a2a_client.py — A2A 서버에 Task 요청
import httpx
import json

async def discover_agent(agent_url: str):
    """Agent Card를 조회하여 능력 확인"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{agent_url}/.well-known/agent.json")
        return response.json()

async def send_task(agent_url: str, message: str):
    """Agent에게 Task 전송"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "id": "task-001",
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}]
            }
        },
        "id": "req-001"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(agent_url, json=payload)
        result = response.json()
        return result["result"]["artifacts"][0]["parts"][0]["text"]

# 사용 예시
agent_url = "https://data-agent.example.com"
card = await discover_agent(agent_url)
print(f"Agent: {card['name']} — {card['description']}")

result = await send_task(agent_url, "지난 분기 매출 상위 5개 제품은?")
print(result)
```

{% hint style="info" %}
위 코드는 A2A의 핵심 흐름을 보여주는 간소화된 예시입니다. 프로덕션 구현 시에는 인증, 에러 핸들링, 스트리밍 등을 추가해야 합니다. 최신 구현 예시는 [A2A GitHub](https://github.com/google/A2A)을 참고하세요.
{% endhint %}

---

## Databricks에서의 활용 전망

| 시나리오 | 설명 |
|----------|------|
| **Cross-team Agent 협업** | 데이터팀 Agent와 보안팀 Agent가 A2A로 통신 |
| **외부 벤더 Agent 연동** | SaaS 벤더가 제공하는 Agent와 사내 Agent 협업 |
| **Multi-Cloud Agent** | AWS/Azure/GCP 각 환경의 Agent가 표준 프로토콜로 통신 |
| **Supervisor 패턴 확장** | Databricks Supervisor Agent가 A2A로 외부 Agent에 작업 위임 |

{% hint style="warning" %}
A2A는 2025년 초 발표된 프로토콜로, 아직 초기 단계입니다. Databricks의 공식 A2A 지원은 추후 발표를 확인하세요.
{% endhint %}

---

## 흔한 오해 (Common Misconceptions)

| 오해 | 사실 |
|------|------|
| "A2A는 MCP를 대체한다" | A2A와 MCP는 서로 다른 문제를 해결합니다. 보완 관계이며 함께 사용합니다. |
| "A2A를 쓰면 모든 Agent가 자동으로 협업한다" | Agent Card를 잘 설계하고, 각 Agent의 스킬을 명확히 정의해야 협업이 원활합니다. |
| "A2A는 Google 전용 기술이다" | A2A는 오픈 프로토콜입니다. Google, Salesforce, SAP 등 50개 이상의 기업이 참여합니다. |
| "기존 Multi-Agent 시스템을 A2A로 교체해야 한다" | 같은 조직 내 Agent는 기존 프레임워크 내부 통신이 효율적일 수 있습니다. A2A는 **이기종 시스템 간** 통신에 가장 가치가 있습니다. |

---

## 고객이 자주 묻는 질문

### "A2A를 지금 도입해야 하나요?"

아직 초기 단계입니다. 내부 Multi-Agent 시스템은 기존 프레임워크(LangGraph, Databricks Agent Framework 등)로 충분히 구현할 수 있습니다. **외부 벤더의 Agent와 연동**이 필요하거나, **이기종 프레임워크 간 협업**이 요구될 때 A2A 도입을 검토하세요.

### "A2A와 REST API의 차이가 뭔가요?"

REST API는 사전에 정의된 엔드포인트를 호출하는 방식입니다. A2A는 Agent가 **자율적으로 상대방의 능력을 발견**하고 작업을 위임합니다. 핵심 차이는 세 가지입니다:
- **자기소개 (Agent Card)**: Agent가 자신의 능력을 표준화된 형식으로 공개
- **상태 관리 (Task lifecycle)**: 작업의 진행 상황을 추적하고, 추가 정보 요청도 가능
- **스트리밍**: 장기 실행 작업의 중간 결과를 실시간으로 수신

### "MCP만 쓰면 안 되나요?"

단일 Agent가 여러 도구를 사용하는 데에는 MCP만으로 충분합니다. 하지만 **여러 독립적인 Agent가 협업**해야 하는 경우에는 A2A가 필요합니다. 규모와 요구사항에 따라 선택하세요:
- 도구 연동만 필요 → **MCP**
- Agent 간 협업 필요 → **A2A**
- 둘 다 필요 → **A2A + MCP 결합**

---

## 연습 문제

1. MCP와 A2A의 핵심 차이를 "택배 시스템"에 비유하여 설명하세요.
2. Agent Card에서 `skills` 필드가 왜 중요한지, 이 필드가 없다면 어떤 문제가 발생하는지 설명하세요.
3. Task 상태 중 `input-required`가 존재하는 이유와, 이 상태가 없다면 어떤 한계가 있을지 설명하세요.
4. "사내 IT 헬프데스크"를 A2A로 설계한다면 어떤 Agent들이 필요하고, 각 Agent의 Agent Card를 어떻게 정의하겠습니까?

---

## 참고 자료

- [Google A2A Protocol 공식 사이트](https://google.github.io/A2A/)
- [A2A GitHub 리포지토리](https://github.com/google/A2A)
- [A2A 공식 스펙 문서](https://google.github.io/A2A/specification/)
- [Google Cloud Blog - A2A 발표](https://cloud.google.com/blog/products/ai-machine-learning/a2a-a-new-era-of-agent-interoperability)
- [Anthropic MCP 공식 문서](https://modelcontextprotocol.io/)
