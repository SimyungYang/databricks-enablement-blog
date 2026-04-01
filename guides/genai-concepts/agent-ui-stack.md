# AI Agent UI & 배포 기술 스택

AI Agent를 사용자에게 전달하려면 "무엇을 만들 것인가"만큼이나 "어떻게 보여줄 것인가"가 중요합니다. 이 가이드는 Agent 프로젝트에서 사용되는 UI/UX 프레임워크와 배포 기술을 비교하고, 프로젝트 단계별 최적의 기술 스택을 선택하는 기준을 제공합니다.

{% hint style="info" %}
**학습 목표**
- Agent 프로젝트에서 UI/UX 기술 선택 기준을 이해한다
- Streamlit, Gradio, Chainlit, Dash, FastAPI의 특성과 적합한 사용 사례를 구분할 수 있다
- Databricks Apps를 활용한 프로덕션 배포 아키텍처를 설계할 수 있다
- PoC → 파일럿 → 프로덕션 단계별 적합한 기술 스택을 선택할 수 있다
{% endhint %}

---

## 1. 왜 Agent에 UI가 필요한가?

AI Agent는 API만으로도 동작합니다. `curl`로 엔드포인트를 호출하면 응답이 돌아오고, 노트북에서 함수를 실행하면 결과를 확인할 수 있습니다. 그런데 왜 UI를 만들어야 할까요?

### 채택(Adoption)의 벽

Agent의 기술적 완성도와 실제 사용률은 별개입니다. 아무리 정교한 RAG 파이프라인과 Tool Calling 로직을 구현해도, 사용자가 접근할 수 없으면 의미가 없습니다.

| 사용자 유형 | 선호 인터페이스 | 이유 |
|------------|---------------|------|
| **개발자** | API / CLI / SDK | 자동화 파이프라인에 Agent를 통합해야 하므로 프로그래밍 인터페이스가 자연스러움 |
| **데이터 분석가** | 노트북 (Databricks, Jupyter) | 이미 노트북 환경에서 작업하므로, Agent를 함수 호출로 사용 가능 |
| **현업 사용자** | 웹 앱 (채팅, 대시보드) | CLI나 노트북을 사용할 수 없으므로 브라우저 기반 인터페이스가 유일한 접점 |
| **경영진** | 데모 화면 (웹 앱) | 투자 의사결정을 위해 "동작하는 화면"을 봐야 확신 |

{% hint style="warning" %}
**PoC의 성패를 UI가 좌우한다**: 기술적으로 완벽한 Agent라도, 경영진 데모에서 터미널에 JSON을 보여주면 프로젝트 승인이 어렵습니다. 반대로, 간단한 채팅 UI 하나만 있어도 "이걸 우리 팀도 쓸 수 있겠는데?"라는 반응을 이끌어낼 수 있습니다. UI는 기술이 아니라 커뮤니케이션 도구입니다.
{% endhint %}

### UI의 세 가지 역할

1. **접근성 확보**: 비기술 사용자가 Agent를 사용할 수 있는 유일한 경로
2. **신뢰 구축**: Agent의 추론 과정, Tool 호출 결과, 출처를 투명하게 보여줌으로써 사용자 신뢰 확보
3. **피드백 수집**: 사용자가 "좋아요/싫어요", 수정 요청 등의 피드백을 남길 수 있는 인터페이스 제공

---

## 2. Streamlit -- Python 개발자의 최애 도구

### 등장 배경

2019년, Adrien Treuille(전 카네기멜론 교수)가 "Python 개발자가 HTML/CSS/JS를 몰라도 웹 앱을 만들 수 있어야 한다"는 철학으로 Streamlit을 출시했습니다. 2022년 Snowflake에 인수되어 현재는 Snowflake 생태계의 핵심 도구이기도 하지만, Databricks Apps에서도 공식 지원하는 프레임워크입니다.

### 핵심 원리: Top-Down 리렌더링

Streamlit의 동작 방식은 다른 웹 프레임워크와 근본적으로 다릅니다.

```
[사용자 입력] → [전체 스크립트 재실행 (위→아래)] → [UI 갱신]
```

**일반적인 웹 프레임워크** (React, Flask 등)는 이벤트 핸들러를 등록하고, 해당 이벤트가 발생하면 특정 컴포넌트만 업데이트합니다. 반면 **Streamlit**은 사용자가 버튼을 클릭하거나, 슬라이더를 움직이거나, 텍스트를 입력할 때마다 **Python 스크립트 전체를 처음부터 다시 실행**합니다.

이 방식의 장점은 상태 관리 로직이 극도로 단순해진다는 것이고, 단점은 스크립트가 길어지면 성능 문제가 발생한다는 것입니다.

### 핵심 컴포넌트 (Agent UI 관점)

| 컴포넌트 | 역할 | 비고 |
|----------|------|------|
| `st.chat_input()` | 채팅 입력창 (화면 하단 고정) | Agent 대화의 시작점 |
| `st.chat_message()` | 사용자/어시스턴트 메시지 표시 | role 기반 아이콘 자동 표시 |
| `st.session_state` | 세션별 상태 저장 | 리렌더링 시에도 유지되는 저장소 |
| `st.sidebar` | 좌측 패널 (설정, 모델 선택 등) | Agent 설정 UI에 활용 |
| `st.dataframe()` | 테이블 표시 | Agent가 조회한 데이터 시각화 |
| `st.plotly_chart()` | Plotly 차트 렌더링 | Agent가 생성한 시각화 표시 |
| `st.spinner()` | 로딩 인디케이터 | Agent 처리 중 표시 |
| `st.write_stream()` | 스트리밍 텍스트 표시 | LLM 응답 실시간 출력 |

### 채팅 UI 구현 패턴

```python
import streamlit as st
from databricks.sdk import WorkspaceClient

st.set_page_config(page_title="MLOps Agent", page_icon="🤖")
st.title("MLOps Agent 🤖")

# 사이드바: Agent 설정
with st.sidebar:
    st.header("설정")
    model_name = st.selectbox("모델", ["databricks-meta-llama-3-3-70b-instruct", "databricks-claude-sonnet-4"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1)

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 표시 (리렌더링 시마다 실행)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요"):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent 호출 (Databricks Model Serving 예시)
    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):
            w = WorkspaceClient()
            response = w.serving_endpoints.query(
                name="mlops-agent-endpoint",
                messages=[{"role": m["role"], "content": m["content"]}
                         for m in st.session_state.messages]
            )
            result = response.choices[0].message.content
            st.markdown(result)

    # 어시스턴트 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": result})
```

### 스트리밍 응답 구현

실시간 타이핑 효과를 위한 스트리밍 패턴:

```python
import streamlit as st

def stream_response(prompt):
    """Agent 스트리밍 응답 제너레이터"""
    w = WorkspaceClient()
    for chunk in w.serving_endpoints.query(
        name="agent-endpoint",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    ):
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# 스트리밍 표시
if prompt := st.chat_input("질문을 입력하세요"):
    with st.chat_message("assistant"):
        response = st.write_stream(stream_response(prompt))
    st.session_state.messages.append({"role": "assistant", "content": response})
```

### Streamlit의 장점과 한계

**장점:**
- Python만으로 완결되는 풀스택 개발 -- HTML, CSS, JavaScript 지식 불필요
- 가장 빠른 개발 속도 -- 채팅 UI를 30분 이내에 구현 가능
- 풍부한 위젯 생태계 -- 차트, 테이블, 지도, 파일 업로드 등 100여 개 내장 컴포넌트
- Databricks Apps 공식 지원 -- 프로덕션 배포까지 원활

**한계:**
- **전체 리렌더링**: 사용자 입력마다 스크립트 전체 재실행 → 대규모 앱에서 성능 저하
- **멀티유저 세션 관리 제한**: `st.session_state`는 브라우저 탭 단위 → 서버 측 세션 공유 불가
- **커스텀 디자인 어려움**: CSS 오버라이드가 제한적, 기업 브랜딩 적용 까다로움
- **WebSocket 기반**: 동시접속 50명 이상 시 서버 부하 급증 (Databricks Apps에서는 자동 스케일링으로 완화)
- **SEO 불가**: 서버 사이드 렌더링이 아닌 WebSocket 기반이므로 검색엔진 노출 불가 (Agent 앱에서는 대부분 문제 아님)

{% hint style="success" %}
**실전 팁**: Streamlit은 PoC와 파일럿 단계에서 "속도 vs 완성도" 트레이드오프의 최적 지점입니다. 2주 안에 경영진에게 데모를 보여야 한다면, Streamlit이 정답입니다.
{% endhint %}

---

## 3. Gradio -- ML 데모의 표준

### 등장 배경

2019년, Stanford 박사과정이던 Abubakar Abid가 "ML 모델을 비개발자에게 시연할 수 있는 가장 쉬운 방법"을 목표로 Gradio를 만들었습니다. 2021년 Hugging Face에 인수된 후, Hugging Face Spaces의 기본 프레임워크가 되면서 ML/AI 데모의 사실상 표준으로 자리잡았습니다.

Gradio의 핵심 철학은 **"입력 → 함수 → 출력" 패턴**입니다. 모든 ML 모델은 결국 입력을 받아 출력을 반환하는 함수이므로, 이 패턴만 정의하면 UI가 자동 생성됩니다.

### 핵심 컴포넌트

| 컴포넌트 | 역할 | 비고 |
|----------|------|------|
| `gr.Interface()` | 입력→함수→출력 패턴의 자동 UI 생성 | 가장 기본적인 사용 방식 |
| `gr.ChatInterface()` | 채팅 전용 UI (대화 기록 자동 관리) | Agent UI에 최적 |
| `gr.Blocks()` | 커스텀 레이아웃 (Streamlit의 자유도에 근접) | 복잡한 UI 필요 시 |
| `gr.Textbox()` | 텍스트 입력/출력 | 다양한 옵션 지원 |
| `gr.Image()` | 이미지 입력/출력 | 멀티모달 Agent에 유용 |
| `gr.File()` | 파일 업로드/다운로드 | 문서 처리 Agent에 유용 |

### ChatInterface 패턴

```python
import gradio as gr

def respond(message, history):
    """
    Agent 호출 함수
    Args:
        message: 현재 사용자 입력
        history: 대화 기록 [["user_msg", "bot_msg"], ...]
    """
    # Databricks Model Serving 호출
    from databricks.sdk import WorkspaceClient
    w = WorkspaceClient()

    # 대화 기록을 messages 형식으로 변환
    messages = []
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})

    response = w.serving_endpoints.query(
        name="predictive-maintenance-agent",
        messages=messages
    )
    return response.choices[0].message.content

demo = gr.ChatInterface(
    fn=respond,
    title="예지보전 Agent",
    description="설비 상태를 분석하고 유지보수를 권장하는 AI Agent입니다.",
    examples=[
        "모터 A-301의 진동 데이터가 정상인가요?",
        "지난 주 드리프트가 발생한 모델 목록을 보여주세요",
        "다음 유지보수 일정을 추천해주세요"
    ],
    theme="soft"
)

demo.launch(server_name="0.0.0.0", server_port=8080)
```

### Hugging Face Spaces 연동

Gradio의 킬러 기능 중 하나는 `share=True` 한 줄로 공개 URL을 생성할 수 있다는 점입니다.

```python
demo.launch(share=True)
# → "Running on public URL: https://xxxx.gradio.live" (72시간 유효)
```

Hugging Face Spaces에 배포하면 영구 URL을 얻을 수 있습니다. GitHub 리포지토리를 연결하면 코드 push만으로 자동 배포됩니다.

### Gradio vs Streamlit: 언제 무엇을 쓰는가?

| 기준 | Gradio | Streamlit |
|------|--------|-----------|
| **설계 철학** | 입력 → 함수 → 출력 | 스크립트 위→아래 실행 |
| **채팅 UI** | `ChatInterface` (간결) | `st.chat_input` + `st.chat_message` (유연) |
| **공유** | `share=True`로 즉시 공개 URL | 별도 배포 필요 |
| **대시보드** | 제한적 (Blocks로 가능하나 번거로움) | 강력 (대시보드 특화) |
| **레이아웃** | 제한적 | columns, tabs, sidebar 등 유연 |
| **생태계** | Hugging Face Spaces | Snowflake, Databricks Apps |
| **멀티모달** | 이미지/오디오/비디오 입출력 내장 | 별도 구현 필요 |

{% hint style="info" %}
**선택 기준**: ML 모델 데모, Hugging Face 모델 활용, 멀티모달 Agent라면 Gradio. 대시보드가 포함된 Agent 앱, Databricks Apps 배포가 목표라면 Streamlit.
{% endhint %}

### 한계

- **복잡한 레이아웃 어려움**: 대시보드 + 채팅 + 사이드바 같은 복합 레이아웃 구현이 번거로움
- **세밀한 UX 커스텀 제한**: 테마 변경은 가능하지만, 컴포넌트 수준의 디자인 커스텀은 제한적
- **프로덕션 안정성**: 대규모 동시접속 환경에서의 검증 사례가 Streamlit 대비 적음
- **Databricks Apps 지원은 되지만**: Streamlit보다 Databricks 생태계 통합 예제가 적음

---

## 4. Chainlit -- LangChain/LangGraph 전용 채팅 UI

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

## 5. Dash (Plotly) -- 데이터 대시보드의 정석

### 등장 배경

2017년, Plotly 팀이 "Python으로 프로덕션 수준의 분석 대시보드를 만들자"는 목표로 Dash를 출시했습니다. Streamlit이 "빠른 프로토타입"에 초점을 둔다면, Dash는 "프로덕션 안정성과 커스텀 자유도"에 초점을 둡니다.

### 핵심 원리: 콜백(Callback) 패턴

Streamlit이 스크립트 전체를 재실행하는 반면, Dash는 **콜백 함수**를 통해 특정 컴포넌트만 업데이트합니다. 이 방식은 React의 상태 관리와 유사합니다.

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
**적합 사례**: 모델 모니터링 대시보드, A/B 테스트 결과 시각화, 비즈니스 KPI 대시보드 등 **차트와 필터가 중심**인 앱에 Dash가 적합합니다. Agent 채팅이 주요 기능이라면 Streamlit이나 Chainlit을 선택하세요.
{% endhint %}

---

## 6. FastAPI -- Agent API 서버의 표준

### 등장 배경

2018년, Sebastian Ramirez가 "Python 웹 프레임워크의 세 가지 고질적 문제 -- 느린 속도, 불편한 타입 체크, 문서 자동화 부재 -- 를 한 번에 해결하자"는 목표로 FastAPI를 출시했습니다. Flask가 동기 처리 중심이라면, FastAPI는 비동기(async/await) 네이티브이고, Pydantic 기반 타입 검증과 자동 API 문서(Swagger UI)를 제공합니다.

FastAPI는 UI 프레임워크가 아닙니다. Agent의 기능을 **REST API/WebSocket으로 노출**하는 백엔드 서버입니다. 프론트엔드는 React, Next.js, Vue.js 등 별도의 프레임워크로 구현하거나, Streamlit을 클라이언트로 연결합니다.

### REST API로 Agent 노출

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

### 스트리밍 응답 (Server-Sent Events, SSE)

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

### WebSocket을 활용한 양방향 통신

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

### Frontend 분리 아키텍처

```
┌──────────────────┐        ┌──────────────────┐
│    Frontend      │  HTTP   │    Backend       │
│  (React/Next.js) │◄──────►│  (FastAPI)       │
│                  │  SSE/WS │                  │
│  - 채팅 UI       │        │  - Agent 로직    │
│  - 대시보드      │        │  - Tool 관리     │
│  - 인증 UI       │        │  - 세션 관리     │
└──────────────────┘        └────────┬─────────┘
                                     │
                            ┌────────▼─────────┐
                            │ Databricks       │
                            │ - Model Serving  │
                            │ - SQL Warehouse  │
                            │ - Unity Catalog  │
                            └──────────────────┘
```

### 장점과 한계

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

## 7. Databricks Apps -- 프로덕션 배포의 정답

### 왜 Databricks Apps인가?

Agent 앱을 프로덕션에 배포할 때 가장 큰 장벽은 기술 자체가 아니라 **인프라 운영**입니다.

| 직접 배포 시 해야 할 것 | Databricks Apps가 해결하는 것 |
|------------------------|-----------------------------|
| 서버 프로비저닝 (EC2, VM) | 서버리스 컨테이너 자동 실행 |
| SSL 인증서 발급/갱신 | HTTPS 자동 적용 |
| 인증/인가 시스템 구현 | OAuth 기반 Databricks 사용자 인증 자동 통합 |
| SQL Warehouse 연결 설정 | `DATABRICKS_WAREHOUSE_ID` 환경 변수로 자동 연결 |
| Model Serving 엔드포인트 연결 | 서비스 프린시펄을 통한 직접 접근 |
| 네트워크 보안 (VPN, 방화벽) | Databricks 네트워크 내 격리 실행 |
| Unity Catalog 권한 관리 | 서비스 프린시펄에 UC 권한 부여로 해결 |
| CI/CD 파이프라인 구성 | `databricks apps deploy` 명령어로 즉시 배포 |

### 지원 프레임워크

| 프레임워크 | 지원 여부 | 권장 사용 사례 |
|-----------|----------|---------------|
| **Streamlit** | 공식 지원 | 채팅 UI + 대시보드, 가장 많은 예제 |
| **Dash** | 공식 지원 | 차트 중심 모니터링 대시보드 |
| **Gradio** | 공식 지원 | ML 모델 데모, 멀티모달 앱 |
| **Flask** | 공식 지원 | 경량 웹 서버, API + 간단한 UI |
| **FastAPI** | 공식 지원 | API 서버, SSE/WebSocket |
| **Chainlit** | 미지원 | (FastAPI 래핑으로 우회 가능하나 비권장) |

### app.yaml 설정 예시

**Streamlit Agent 앱 (가장 일반적):**

```yaml
command:
  - "streamlit"
  - "run"
  - "app.py"
  - "--server.port"
  - "8000"
  - "--server.address"
  - "0.0.0.0"

env:
  - name: "DATABRICKS_WAREHOUSE_ID"
    valueFrom: "warehouse-id"
  - name: "SERVING_ENDPOINT"
    value: "mlops-agent-endpoint"

resources:
  - name: "warehouse-id"
    type: "sql_warehouse"
    sql_warehouse:
      id: "abc123def456"
      permission: "CAN_USE"
  - name: "serving-endpoint"
    type: "serving_endpoint"
    serving_endpoint:
      name: "mlops-agent-endpoint"
      permission: "CAN_QUERY"
```

**FastAPI API 서버:**

```yaml
command:
  - "uvicorn"
  - "main:app"
  - "--host"
  - "0.0.0.0"
  - "--port"
  - "8000"

env:
  - name: "DATABRICKS_WAREHOUSE_ID"
    valueFrom: "warehouse-id"

resources:
  - name: "warehouse-id"
    type: "sql_warehouse"
    sql_warehouse:
      id: "abc123def456"
      permission: "CAN_USE"
```

### 배포 워크플로

```bash
# 1. 앱 생성 (최초 1회)
databricks apps create \
  --name mlops-agent-app \
  --description "MLOps 모니터링 및 Agent 채팅"

# 2. 앱 배포 (코드 변경 시마다)
databricks apps deploy mlops-agent-app \
  --source-code-path ./app

# 3. 배포 상태 확인
databricks apps get mlops-agent-app

# 4. 로그 확인
databricks apps get-logs mlops-agent-app
```

### PoC Streamlit → Databricks Apps 마이그레이션

로컬에서 `streamlit run app.py`로 개발한 앱을 Databricks Apps로 마이그레이션하는 단계:

**Step 1: 인증 방식 변경**

```python
# Before (로컬 개발)
from databricks.sdk import WorkspaceClient
w = WorkspaceClient(
    host="https://xxx.cloud.databricks.com",
    token="dapi..."  # PAT 하드코딩
)

# After (Databricks Apps)
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()  # 서비스 프린시펄 자동 인증
```

**Step 2: 환경 변수 사용**

```python
import os

# 하드코딩 제거, 환경 변수 사용
warehouse_id = os.environ.get("DATABRICKS_WAREHOUSE_ID")
endpoint_name = os.environ.get("SERVING_ENDPOINT", "default-agent")
```

**Step 3: requirements.txt 정리**

```
streamlit>=1.38.0
databricks-sdk>=0.30.0
plotly>=5.0.0
```

**Step 4: app.yaml 작성 및 배포**

{% hint style="success" %}
**마이그레이션 핵심 원칙**: (1) PAT/토큰 하드코딩 → 서비스 프린시펄 자동 인증, (2) 호스트/엔드포인트 하드코딩 → 환경 변수, (3) `requirements.txt`에 모든 의존성 명시. 이 세 가지만 지키면 대부분의 로컬 Streamlit 앱은 Databricks Apps로 바로 배포 가능합니다.
{% endhint %}

---

## 8. 단계별 기술 스택 선택 가이드

Agent 프로젝트는 PoC → 파일럿 → 프로덕션의 단계를 거칩니다. 각 단계마다 최적의 기술 스택이 다릅니다.

### PoC (1~2주): "동작하는 데모"

| 항목 | 선택 | 이유 |
|------|------|------|
| **프론트엔드** | Streamlit 또는 Chainlit | 최소 코드로 채팅 UI 구현 (Streamlit: 30분, Chainlit: Agent 추론 과정 시각화) |
| **백엔드** | Agent 직접 호출 (인프로세스) | API 서버 없이 앱 내에서 직접 LLM/Tool 호출 |
| **배포** | 로컬 (`streamlit run`) 또는 노트북 | 배포 인프라 불필요, 로컬에서 데모 |
| **인증** | PAT (Personal Access Token) | 개인 토큰으로 빠른 설정 |
| **데이터** | 하드코딩 또는 직접 SQL | 유연하고 빠른 반복 개발 |

```
┌──────────────┐
│  Streamlit   │─── Agent 직접 호출 ──→ Databricks
│  (로컬 실행)  │      (인프로세스)       (Model Serving)
└──────────────┘
```

### 파일럿 (1~2개월): "팀 내부 사용"

| 항목 | 선택 | 이유 |
|------|------|------|
| **프론트엔드** | Streamlit + Databricks Apps | 팀원들이 URL로 접근 가능, OAuth 자동 인증 |
| **백엔드** | Model Serving 엔드포인트 | Agent를 엔드포인트로 배포, 안정적 API 제공 |
| **배포** | Databricks Apps | 서버리스 호스팅, SSL, 인증 자동화 |
| **인증** | 서비스 프린시펄 (자동) | PAT 노출 위험 제거 |
| **데이터** | SQL Warehouse + Unity Catalog | 거버넌스 적용, 접근 제어 |

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Streamlit   │─────→│Model Serving │─────→│ Unity Catalog│
│  (Dbx Apps)  │ HTTP │  (Agent EP)  │      │ SQL Warehouse│
└──────────────┘      └──────────────┘      └──────────────┘
```

### 프로덕션 (지속 운영): "전사 사용"

**옵션 A: Streamlit/Dash + Databricks Apps** (사용자 수 < 100명)

| 항목 | 선택 | 이유 |
|------|------|------|
| **프론트엔드** | Streamlit 또는 Dash | 유지보수 용이, Python 단일 스택 |
| **백엔드** | Model Serving + Agent Framework | 안정적 엔드포인트, A/B 테스팅 가능 |
| **배포** | Databricks Apps + CI/CD | GitHub Actions 또는 Azure DevOps 연동 |
| **모니터링** | Inference Table + Lakehouse Monitoring | 요청/응답 로깅, 품질 모니터링 |

**옵션 B: React/Next.js + FastAPI** (사용자 수 100명+ 또는 커스텀 UX 필수)

| 항목 | 선택 | 이유 |
|------|------|------|
| **프론트엔드** | React/Next.js | 커스텀 디자인, 기업 포털 통합, 모바일 대응 |
| **백엔드** | FastAPI (Databricks Apps) | API 서버로 Agent 기능 노출 |
| **배포** | Databricks Apps (백엔드) + CDN/Vercel (프론트) | 프론트/백 독립 배포 |
| **모니터링** | Inference Table + 외부 APM (Datadog 등) | 엔드투엔드 모니터링 |

{% hint style="warning" %}
**프로덕션 전환 시 반드시 확인할 것**:
1. **인증**: PAT → 서비스 프린시펄 전환 완료 여부
2. **시크릿 관리**: 환경 변수 또는 Databricks Secret Scope 사용 여부
3. **에러 핸들링**: Agent 호출 실패 시 사용자에게 적절한 메시지 표시 여부
4. **Rate Limiting**: Model Serving 엔드포인트의 동시 요청 제한 설정 여부
5. **로깅**: 모든 요청/응답이 Inference Table에 기록되는지 확인
{% endhint %}

---

## 9. 종합 비교 테이블

### 기능별 비교

| 항목 | Streamlit | Gradio | Chainlit | Dash | FastAPI |
|------|-----------|--------|----------|------|---------|
| **주요 용도** | 대시보드 + 채팅 | ML 데모 | Agent 채팅 | 대시보드 | API 서버 |
| **개발 속도** | 매우 빠름 | 빠름 | 빠름 | 보통 | 보통 |
| **채팅 UI** | 좋음 | 좋음 | 최고 | 어려움 | 직접 구현 |
| **대시보드** | 좋음 | 제한적 | 없음 | 최고 | 직접 구현 |
| **프로덕션 적합성** | 보통 | 제한적 | 제한적 | 좋음 | 최고 |
| **Databricks Apps** | 지원 | 지원 | 미지원 | 지원 | 지원 |
| **멀티유저 지원** | 제한적 | 제한적 | 제한적 | 좋음 | 최고 |
| **커스텀 디자인** | 제한적 | 제한적 | 보통 | 좋음 | 완전 자유 |
| **스트리밍** | `write_stream` | 내장 | 내장 | 어려움 | SSE/WS |
| **Agent 추론 시각화** | 직접 구현 | 제한적 | 내장 (최고) | 직접 구현 | 직접 구현 |

### 의사결정 흐름도

```
Agent UI 기술 선택
│
├─ "2주 안에 데모를 보여줘야 한다"
│   └─→ Streamlit (채팅+대시보드) 또는 Chainlit (Agent 추론 시각화)
│
├─ "Hugging Face 모델을 데모하고 싶다"
│   └─→ Gradio
│
├─ "차트 중심 모니터링 대시보드를 만든다"
│   └─→ Dash
│
├─ "기존 웹 포털에 Agent를 통합해야 한다"
│   └─→ FastAPI (백엔드) + 기존 프론트엔드
│
├─ "Databricks Apps에 배포해야 한다"
│   ├─ 채팅 UI 중심 → Streamlit
│   ├─ 대시보드 중심 → Dash
│   └─ API 서버 → FastAPI
│
└─ "사용자 100명+, 커스텀 UX 필수"
    └─→ FastAPI + React/Next.js
```

### 비용 관점 비교

| 항목 | Streamlit | Gradio | Chainlit | Dash | FastAPI + React |
|------|-----------|--------|----------|------|-----------------|
| **개발 인력** | Python 1명 | Python 1명 | Python 1명 | Python 1명 | Python + Frontend 2명 |
| **초기 개발 기간** | 1~2주 | 1~2주 | 1~2주 | 2~4주 | 4~8주 |
| **유지보수 난이도** | 낮음 | 낮음 | 보통 | 보통 | 높음 |
| **인프라 비용** | Databricks Apps DBU | Databricks Apps DBU | 별도 서버 | Databricks Apps DBU | Databricks Apps + CDN |

---

## 10. 고객이 자주 묻는 질문

### Q1: "Streamlit으로 프로덕션 가능한가요?"

**단독 배포는 비권장. Databricks Apps 위에서는 가능합니다.**

Streamlit을 EC2나 VM에 직접 배포하면 SSL, 인증, 스케일링을 모두 직접 관리해야 합니다. 또한 WebSocket 기반 아키텍처로 인해 동시접속 50명 이상 시 성능 문제가 발생할 수 있습니다.

그러나 Databricks Apps 위에서 실행하면 이야기가 달라집니다. SSL 자동 적용, OAuth 인증 통합, 서버리스 스케일링이 모두 Databricks가 처리하므로, 팀 단위(10~50명) 사용에는 충분합니다.

**결론**: 사용자 수 50명 이하 + Databricks Apps 배포 → Streamlit으로 프로덕션 가능. 50명 이상이거나 커스텀 UX가 필수라면 FastAPI + React 검토.

### Q2: "React로 만들어야 하나요?"

**대부분의 경우, 아닙니다.**

React를 도입하면 프론트엔드 전문 인력, 빌드 파이프라인, 별도 호스팅이 추가로 필요합니다. Agent 프로젝트의 핵심 가치는 UI가 아니라 Agent의 기능입니다.

| 상황 | 권장 |
|------|------|
| PoC/파일럿, 팀 내부 사용 | Streamlit으로 충분 |
| 사용자 100명+, 전사 서비스 | React + FastAPI 검토 |
| 기존 웹 포털에 Agent 내장 | FastAPI API + iframe 또는 웹 컴포넌트 |
| 모바일 앱에 Agent 통합 | FastAPI API 필수 (Streamlit 불가) |
| 기업 브랜딩/디자인 시스템 적용 | React + FastAPI |

### Q3: "가장 빨리 데모를 만들 수 있는 방법은?"

**Streamlit + Databricks Agent Framework. 2시간이면 채팅 UI 완성 가능합니다.**

```python
# 이 코드만으로 Agent 채팅 앱 완성 (약 20줄)
import streamlit as st
from databricks.sdk import WorkspaceClient

st.title("My Agent")
w = WorkspaceClient()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("질문하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = w.serving_endpoints.query(
        name="my-agent-endpoint",
        messages=st.session_state.messages
    )
    result = response.choices[0].message.content

    with st.chat_message("assistant"):
        st.markdown(result)
    st.session_state.messages.append({"role": "assistant", "content": result})
```

### Q4: "Databricks Apps 비용은?"

Databricks Apps는 **서버리스 컴퓨팅 기반**으로 과금됩니다.

| 항목 | 설명 |
|------|------|
| **과금 기준** | 앱이 실행 중인 시간 + 프로비저닝된 리소스(CPU, 메모리) 기준 DBU |
| **유휴 시 비용** | 앱이 STOPPED 상태이면 과금 없음 |
| **자동 중지** | 설정한 비활성 시간 이후 자동 중지 가능 |
| **추가 비용** | SQL Warehouse 사용 시 별도 DBU, Model Serving 사용 시 별도 DBU |

{% hint style="info" %}
**비용 최적화 팁**: PoC/파일럿 단계에서는 앱 자동 중지(idle timeout)를 짧게 설정(예: 30분)하여 비용을 절감하세요. 프로덕션에서는 always-on으로 설정하되, 사용 패턴에 따라 비활성 시간대에 수동 중지를 고려하세요.
{% endhint %}

### Q5: "Chainlit을 Databricks에서 쓸 수 있나요?"

Databricks Apps에서 Chainlit을 직접 호스팅하는 것은 현재 지원되지 않습니다. 대안으로 두 가지 방법이 있습니다.

1. **PoC 단계에서만 로컬 사용**: 개발 머신에서 `chainlit run app.py`로 실행하고 데모
2. **FastAPI 래핑**: Chainlit을 FastAPI 앱 내에 마운트하여 Databricks Apps에 배포 (공식 지원이 아니므로 안정성 보장 어려움)

Agent 추론 과정 시각화가 중요하다면, Streamlit에서 `st.expander`를 활용하여 유사한 UX를 구현하는 것을 권장합니다.

---

## 11. 연습 문제

### 문제 1: 기술 스택 선택

> 제조업 고객이 설비 예지보전 Agent를 만들고 싶어합니다. 현재 상황:
> - PoC 2주 후 경영진 데모 예정
> - 데이터 엔지니어 2명 (Python 가능, 프론트엔드 경험 없음)
> - 이후 현장 작업자 30명이 사용할 예정
> - Databricks 환경 구축 완료
>
> PoC와 프로덕션 각 단계에서 어떤 기술 스택을 추천하시겠습니까? 이유를 포함하여 설명하세요.

{% hint style="info" %}
**모범 답안 방향**: PoC는 Streamlit(빠른 개발, Python만으로 완결), 프로덕션은 Streamlit + Databricks Apps(현장 작업자 30명은 Streamlit으로 충분, 별도 프론트 개발 인력 없음, OAuth로 인증 해결).
{% endhint %}

### 문제 2: 아키텍처 설계

> 금융 고객이 다음 요구사항을 가진 Agent 앱을 설계해야 합니다:
> - 채팅으로 포트폴리오 분석 질문 가능
> - 실시간 차트 대시보드 (주가 추이, 포트폴리오 구성 등)
> - 사용자 200명+, 기업 포털에 통합 필요
> - 규제 준수를 위해 모든 대화 로깅 필수
>
> 적절한 아키텍처(프론트엔드, 백엔드, 배포, 모니터링)를 설계하고 그 이유를 설명하세요.

{% hint style="info" %}
**모범 답안 방향**: FastAPI(백엔드, Databricks Apps) + React(프론트엔드, 기업 포털 통합). 사용자 200명+ 및 포털 통합 → Streamlit 한계 초과. Inference Table로 대화 로깅, Lakehouse Monitoring으로 품질 관리. Dash가 아닌 React를 선택하는 이유: 기업 포털 통합에는 기존 디자인 시스템과의 호환이 필수이므로.
{% endhint %}

### 문제 3: 마이그레이션 계획

> 팀에서 로컬 Streamlit 앱(PAT 인증, 하드코딩된 엔드포인트)을 Databricks Apps로 마이그레이션하려고 합니다. 다음 코드를 Databricks Apps에 배포 가능한 형태로 수정하세요.

```python
import streamlit as st
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(
    host="https://my-workspace.cloud.databricks.com",
    token="dapi1234567890abcdef"
)

response = w.serving_endpoints.query(
    name="my-agent",
    messages=[{"role": "user", "content": "안녕"}]
)
st.write(response.choices[0].message.content)
```

{% hint style="info" %}
**모범 답안 방향**: (1) `WorkspaceClient()` 인자 제거 (서비스 프린시펄 자동 인증), (2) 엔드포인트 이름을 환경 변수로 변경, (3) `app.yaml`에 `serving_endpoint` 리소스 정의, (4) `requirements.txt` 작성.
{% endhint %}

### 문제 4: 트레이드오프 분석

> 다음 세 가지 시나리오에서 각각 Streamlit, Gradio, FastAPI 중 어떤 기술이 가장 적합한지 선택하고, 나머지 두 기술이 부적합한 이유를 설명하세요.
>
> (A) Hugging Face의 오픈소스 LLM을 미세조정한 모델을 팀 외부 이해관계자에게 빠르게 데모
> (B) 고객사의 기존 React 포털에 Agent 채팅 기능을 추가
> (C) 데이터 분석가가 내부적으로 사용할 Agent + 차트 대시보드

{% hint style="info" %}
**모범 답안 방향**: (A) Gradio -- `share=True`로 즉시 공유, HF Spaces 배포 가능. Streamlit은 배포 필요, FastAPI는 UI 없음. (B) FastAPI -- React 포털이 이미 있으므로 API만 제공하면 됨. Streamlit/Gradio는 별도 페이지로만 존재. (C) Streamlit -- 대시보드+채팅 모두 지원, Python만으로 완결. Gradio는 대시보드 약함, FastAPI는 UI 별도 구현 필요.
{% endhint %}

---

## 12. 참고 자료

### 공식 문서

| 리소스 | URL |
|--------|-----|
| Streamlit 공식 문서 | [docs.streamlit.io](https://docs.streamlit.io/) |
| Gradio 공식 문서 | [gradio.app/docs](https://www.gradio.app/docs/) |
| Chainlit 공식 문서 | [docs.chainlit.io](https://docs.chainlit.io/) |
| Dash 공식 문서 | [dash.plotly.com](https://dash.plotly.com/) |
| FastAPI 공식 문서 | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| Databricks Apps 문서 | [docs.databricks.com/apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html) |

### Databricks 관련 자료

| 리소스 | 설명 |
|--------|------|
| [Databricks Apps 가이드](../apps/README.md) | 이 블로그의 Databricks Apps 상세 가이드 |
| [Agent Bricks 가이드](../agent-bricks/README.md) | Knowledge Assistant, Genie Agent, Supervisor Agent |
| [Builder App (AI Dev Kit)](../builder-app/README.md) | Agent 개발 프레임워크 |
| [AI Agent 아키텍처](agent-architecture.md) | ReAct, Tool Use, Multi-Agent 패턴 |

### 추천 학습 경로

1. **입문**: Streamlit 공식 튜토리얼 → 채팅 앱 만들기 (2시간)
2. **심화**: Databricks Apps에 Streamlit 배포 (1시간)
3. **응용**: FastAPI + SSE로 스트리밍 Agent API 구현 (4시간)
4. **프로덕션**: CI/CD 파이프라인 + 모니터링 구축 (1일)
