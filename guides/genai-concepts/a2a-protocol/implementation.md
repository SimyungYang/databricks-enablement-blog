# 구현 가이드

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

사용자 요청: "**3월 15일~18일 제주도 여행을 예약해주세요. 항공편과 호텔, 결제까지 해주세요.**"

| 단계 | Agent | 작업 | A2A 상태 |
|------|-------|------|----------|
| 1 | **여행 플래너 Agent**(Coordinator) | 요청 분석, 하위 작업 분배 | — |
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

| 통신 | 발신 Agent | 수신 Agent / 도구 | 프로토콜 |
|------|----------|-----------------|----------|
| 사용자 → 조율자 | 사용자 | 여행 플래너 Agent | UI/API |
| 조율자 → 항공 | 여행 플래너 | 항공 Agent | **A2A** |
| 항공 → 도구 | 항공 Agent | 항공사 API, 가격 DB | **MCP** |
| 조율자 → 호텔 | 여행 플래너 | 호텔 Agent | **A2A** |
| 호텔 → 도구 | 호텔 Agent | 호텔 예약 시스템 | **MCP** |
| 조율자 → 결제 | 여행 플래너 | 결제 Agent | **A2A** |
| 결제 → 도구 | 결제 Agent | PG사 API | **MCP** |

| 레이어 | 프로토콜 | 역할 | 예시 |
|--------|----------|------|------|
| Agent ↔ Agent | **A2A** | 전문 Agent 간 작업 위임 | 여행 Agent → 항공 Agent |
| Agent ↔ Tool | **MCP** | Agent가 외부 도구/데이터 접근 | 항공 Agent → 항공사 API |
| Agent ↔ Human | UI/API | 사용자 인터페이스 | 챗봇 UI |

{% hint style="info" %}
**설계 원칙**: "Agent 간 대화"에는 A2A, "Agent가 도구를 사용"하는 데에는 MCP. 이 구분이 명확하면 아키텍처가 깔끔해집니다.
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
