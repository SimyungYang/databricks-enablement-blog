# FastAPI -- Agent API 서버의 표준

FastAPI는 UI 프레임워크가 아니라, Agent의 기능을 REST API/WebSocket으로 노출하는 백엔드 서버입니다. 프론트엔드는 React, Next.js, Vue.js 등 별도의 프레임워크로 구현하거나, Streamlit을 클라이언트로 연결합니다.

---

## 등장 배경

2018년, Sebastian Ramirez가 "Python 웹 프레임워크의 세 가지 고질적 문제 -- 느린 속도, 불편한 타입 체크, 문서 자동화 부재 -- 를 한 번에 해결하자"는 목표로 FastAPI를 출시했습니다. Flask가 동기 처리 중심이라면, FastAPI는 비동기(async/await) 네이티브이고, Pydantic 기반 타입 검증과 자동 API 문서(Swagger UI)를 제공합니다.

---

## REST API로 Agent 노출

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="MLOps Agent API", version="1.0.0")

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "databricks-meta-llama-3-3-70b-instruct"
    temperature: Optional[float] = 0.1

class ChatResponse(BaseModel):
    message: ChatMessage
    tool_calls: Optional[List[dict]] = None
    usage: Optional[dict] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Agent 대화 엔드포인트"""
    result = await agent.ainvoke(
        [{"role": m.role, "content": m.content} for m in request.messages]
    )
    return ChatResponse(
        message=ChatMessage(role="assistant", content=result.content),
        tool_calls=result.tool_calls,
        usage={"total_tokens": result.usage.total_tokens}
    )
```

---

## 스트리밍 응답 (Server-Sent Events, SSE)

LLM 응답을 실시간으로 전달하는 SSE 구현:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """스트리밍 Agent 대화 엔드포인트"""
    async def generate():
        async for chunk in agent.astream(
            [{"role": m.role, "content": m.content} for m in request.messages]
        ):
            # SSE 형식으로 전송
            data = json.dumps({
                "content": chunk.content,
                "tool_call": chunk.tool_call if hasattr(chunk, "tool_call") else None,
                "done": False
            }, ensure_ascii=False)
            yield f"data: {data}\n\n"

        # 완료 신호
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
```

---

## WebSocket을 활용한 양방향 통신

SSE는 서버→클라이언트 단방향이지만, WebSocket은 양방향 통신이 가능합니다. Agent의 중간 상태(Tool 호출 결과 등)를 실시간으로 전달할 때 유용합니다.

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI()

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # 클라이언트에서 메시지 수신
            data = await websocket.receive_text()
            request = json.loads(data)

            # Agent 실행 (중간 과정도 전송)
            async for event in agent.astream_events(
                {"messages": [("user", request["message"])]},
                version="v2"
            ):
                if event["event"] == "on_tool_start":
                    await websocket.send_json({
                        "type": "tool_start",
                        "tool": event["name"],
                        "input": str(event["data"].get("input", ""))
                    })
                elif event["event"] == "on_tool_end":
                    await websocket.send_json({
                        "type": "tool_end",
                        "tool": event["name"],
                        "output": str(event["data"].get("output", ""))
                    })
                elif event["event"] == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        await websocket.send_json({
                            "type": "stream",
                            "content": content
                        })

            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        pass
```

---

## Frontend 분리 아키텍처

| 계층 | 구성 요소 | 기능 | 통신 방식 |
|------|----------|------|----------|
| **Frontend**| React / Next.js | 채팅 UI, 대시보드, 인증 UI | HTTP, SSE/WebSocket |
| **Backend**| FastAPI | Agent 로직, Tool 관리, 세션 관리 | — |
| **데이터 플랫폼**| Databricks | Model Serving, SQL Warehouse, Unity Catalog | Backend에서 SDK로 호출 |

---

## 장점과 한계

**장점:**
- **최대 유연성**: 프론트엔드와 백엔드를 완전히 분리, 각각 최적의 기술 선택 가능
- **프로덕션 최적**: 비동기 처리, 수천 동시접속 처리 가능 (Uvicorn + Gunicorn)
- **API 문서 자동화**: `/docs` 경로에 Swagger UI 자동 생성 → 프론트엔드 팀과 협업 용이
- **Databricks Apps 지원**: FastAPI 앱을 Databricks Apps로 배포 가능
- **마이크로서비스**: 여러 Agent를 독립적으로 배포하고 API Gateway로 라우팅 가능

**한계:**
- **프론트엔드 별도 구현**: UI가 없으므로 React/Next.js 등 별도 구현 필요 → 풀스택 역량 요구
- **개발 공수**: Streamlit 대비 3~5배의 개발 시간 (백엔드 + 프론트엔드)
- **운영 복잡성**: 프론트엔드와 백엔드를 별도로 빌드, 배포, 모니터링해야 함

{% hint style="success" %}
**언제 FastAPI를 선택하는가**: (1) 사용자 수 100명 이상의 프로덕션 서비스, (2) 커스텀 UX/브랜딩이 필수인 경우, (3) 모바일 앱이나 기존 포털에 Agent를 통합해야 하는 경우, (4) 여러 프론트엔드가 하나의 Agent 백엔드를 공유하는 경우. 이 중 하나라도 해당하면 FastAPI를 고려하세요.
{% endhint %}

---

[README로 돌아가기](README.md) | 다음: [Databricks Apps & 종합 가이드](databricks-apps.md)
