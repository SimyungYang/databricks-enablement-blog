# Chainlit & Dash

Agent 추론 과정 시각화에 특화된 Chainlit과, 데이터 대시보드의 정석인 Dash를 다룹니다.

---

## Chainlit -- LangChain/LangGraph 전용 채팅 UI

### 등장 배경

2023년, LangChain의 인기와 함께 "Agent의 추론 과정을 사용자에게 투명하게 보여주는 전용 UI"의 필요성이 대두되었습니다. 기존의 Streamlit이나 Gradio는 범용 UI 프레임워크이므로, Agent의 Thought→Action→Observation 루프를 시각화하려면 상당한 커스텀 작업이 필요했습니다. Chainlit은 이 간극을 메우기 위해 만들어졌습니다.

### 핵심 기능

**1. Agent 추론 과정 실시간 표시**

Chainlit의 가장 큰 차별점은 Agent의 내부 동작을 Step-by-Step으로 보여주는 것입니다.

```
🧠 Thought: 사용자가 모델 성능을 물어보고 있습니다. MLflow에서 최근 실험 결과를 조회해야 합니다.
🔧 Action: query_mlflow_experiments(model_name="predictive_maintenance_v3")
📋 Observation: {"accuracy": 0.94, "f1_score": 0.91, "drift_detected": false, ...}
🧠 Thought: 모델 성능이 양호합니다. 사용자에게 결과를 요약하겠습니다.
💬 Answer: 예지보전 모델(v3)의 최근 성능은...
```

일반 채팅 UI에서는 최종 Answer만 보여주지만, Chainlit은 중간 과정을 접을 수 있는(collapsible) Step으로 표시합니다. 이는 Agent의 신뢰성을 검증하는 데 핵심적입니다.

**2. 파일 업로드/다운로드 내장**: 문서 분석 Agent에서 PDF 업로드 → 분석 → 보고서 다운로드 흐름을 자연스럽게 구현

**3. 스트리밍 응답**: LLM 응답을 토큰 단위로 실시간 표시

**4. 인증 통합**: OAuth, 헤더 기반 인증 등 다양한 인증 방식 지원

### LangGraph 통합 예시

```python
import chainlit as cl
from langchain_databricks import ChatDatabricks
from langgraph.prebuilt import create_react_agent

# Tool 정의
from langchain_core.tools import tool

@tool
def query_model_metrics(model_name: str) -> str:
    """MLflow에서 모델의 최신 메트릭을 조회합니다."""
    import mlflow
    client = mlflow.tracking.MlflowClient()
    versions = client.search_model_versions(f"name='{model_name}'")
    if versions:
        run = client.get_run(versions[0].run_id)
        return str(run.data.metrics)
    return "모델을 찾을 수 없습니다."

@tool
def check_data_drift(table_name: str) -> str:
    """Unity Catalog 모니터에서 데이터 드리프트 상태를 확인합니다."""
    from databricks.sdk import WorkspaceClient
    w = WorkspaceClient()
    # 모니터 조회 로직
    return "드리프트 미감지. 모든 피처가 정상 범위 내에 있습니다."

# Agent 구성
model = ChatDatabricks(endpoint="databricks-meta-llama-3-3-70b-instruct")
tools = [query_model_metrics, check_data_drift]
agent = create_react_agent(model, tools)

@cl.on_chat_start
async def start():
    """채팅 시작 시 초기화"""
    await cl.Message(
        content="안녕하세요! MLOps Agent입니다. 모델 성능, 드리프트, 배포 상태에 대해 물어보세요."
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """사용자 메시지 처리"""
    # Agent 실행 (중간 Step 자동 표시)
    result = await cl.make_async(agent.invoke)(
        {"messages": [("user", message.content)]}
    )

    # 최종 응답 전송
    final_message = result["messages"][-1].content
    await cl.Message(content=final_message).send()
```

### Step 시각화 상세 구현

```python
import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    # Step을 명시적으로 표시
    async with cl.Step(name="DB 조회", type="tool") as step:
        step.input = "sales 테이블에서 최근 분기 데이터 조회"
        result = query_database("SELECT * FROM sales WHERE quarter = '2025Q4'")
        step.output = f"조회 결과: {len(result)}건"

    async with cl.Step(name="분석", type="llm") as step:
        step.input = f"조회된 {len(result)}건의 데이터를 분석"
        analysis = llm.invoke(f"다음 데이터를 분석해주세요: {result}")
        step.output = analysis

    await cl.Message(content=analysis).send()
```

### 장점과 한계

**장점:**
- Agent 추론 과정을 가장 잘 시각화 -- PoC 데모에서 "Agent가 어떻게 생각하는지" 보여주기에 최적
- LangChain/LangGraph와의 깊은 통합 -- 콜백 자동 연동
- 비동기(async) 네이티브 -- 스트리밍 응답이 자연스러움
- 파일 처리 내장 -- 문서 분석 Agent에 바로 적용 가능

**한계:**
- **대시보드 기능 없음**: 차트, 테이블, 사이드바 등의 대시보드 컴포넌트가 없음
- **위젯 부족**: Streamlit의 slider, selectbox, checkbox 같은 입력 위젯이 없음
- **Databricks Apps 미지원**: 현재 Databricks Apps에서 Chainlit을 직접 호스팅할 수 없음 (FastAPI 래핑으로 우회 가능)
- **생태계 규모**: Streamlit/Gradio 대비 커뮤니티, 플러그인, 예제가 적음

{% hint style="warning" %}
**Databricks 환경에서의 Chainlit 사용**: Chainlit은 Databricks Apps에서 직접 지원하지 않습니다. Databricks Apps 배포가 목표라면 Streamlit을 사용하고, Chainlit의 Step 시각화가 꼭 필요하다면 로컬 PoC 단계에서만 활용하는 것을 권장합니다.
{% endhint %}

---

## Dash (Plotly) -- 데이터 대시보드의 정석

### 등장 배경

2017년, Plotly 팀이 "Python으로 프로덕션 수준의 분석 대시보드를 만들자"는 목표로 Dash를 출시했습니다. Streamlit이 "빠른 프로토타입"에 초점을 둔다면, Dash는 "프로덕션 안정성과 커스텀 자유도"에 초점을 둡니다.

### 핵심 원리: 콜백(Callback) 패턴

Streamlit이 스크립트 전체를 재실행하는 반면, Dash는 **콜백 함수** 를 통해 특정 컴포넌트만 업데이트합니다. 이 방식은 React의 상태 관리와 유사합니다.

```python
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("모델 모니터링 대시보드"),

    # 모델 선택
    dcc.Dropdown(
        id="model-selector",
        options=[
            {"label": "예지보전 v3", "value": "pred_maint_v3"},
            {"label": "이상탐지 v2", "value": "anomaly_v2"},
        ],
        value="pred_maint_v3"
    ),

    # 차트 영역
    dcc.Graph(id="accuracy-chart"),
    dcc.Graph(id="drift-chart"),

    # 채팅 영역 (간단한 Q&A)
    html.Div([
        dcc.Input(id="chat-input", type="text", placeholder="Agent에게 질문하세요..."),
        html.Button("전송", id="send-button"),
        html.Div(id="chat-output")
    ])
])

@app.callback(
    Output("accuracy-chart", "figure"),
    Input("model-selector", "value")
)
def update_accuracy_chart(model_name):
    """모델 선택 시 정확도 차트 업데이트"""
    # MLflow에서 메트릭 조회
    data = get_model_metrics(model_name)
    fig = px.line(data, x="date", y="accuracy", title=f"{model_name} 정확도 추이")
    return fig

@app.callback(
    Output("chat-output", "children"),
    Input("send-button", "n_clicks"),
    State("chat-input", "value"),
    prevent_initial_call=True
)
def handle_chat(n_clicks, message):
    """Agent 대화 처리"""
    if message:
        response = agent.invoke(message)
        return html.P(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

### Dash의 포지션

| 강점 영역 | 설명 |
|----------|------|
| **복잡한 대시보드** | 다수의 차트, 필터, 탭이 연동되는 분석 대시보드 |
| **프로덕션 안정성** | Flask 기반, WSGI 호환, Gunicorn 등 표준 배포 가능 |
| **Plotly 차트** | 인터랙티브 차트의 최고 품질 (확대/축소, 호버, 선택 등) |
| **콜백 패턴** | 특정 컴포넌트만 업데이트 → 대규모 앱에서도 성능 유지 |
| **Databricks Apps 지원** | 공식 지원 프레임워크 |

### 한계

- **채팅 UI 구현 복잡**: 채팅 인터페이스를 만들려면 직접 HTML/CSS를 조합해야 함
- **학습 곡선**: 콜백 패턴, Input/Output/State 개념 학습 필요 (Streamlit 대비 러닝커브 2~3배)
- **개발 속도 느림**: 같은 기능을 Streamlit의 2~3배 코드로 구현
- **채팅보다 대시보드**: Agent 채팅 UI로는 비효율적, 모니터링/분석 대시보드에 특화

{% hint style="info" %}
**적합 사례**: 모델 모니터링 대시보드, A/B 테스트 결과 시각화, 비즈니스 KPI 대시보드 등 **차트와 필터가 중심** 인 앱에 Dash가 적합합니다. Agent 채팅이 주요 기능이라면 Streamlit이나 Chainlit을 선택하세요.
{% endhint %}

---

[README로 돌아가기](README.md) | 다음: [FastAPI 백엔드](fastapi-backend.md)
