# Streamlit & Gradio

Python 개발자를 위한 빠른 프로토타이핑 UI 프레임워크 두 가지를 비교합니다. Streamlit은 대시보드 + 채팅에, Gradio는 ML 모델 데모에 각각 특화되어 있습니다.

---

## Streamlit -- Python 개발자의 최애 도구

### 등장 배경

2019년, Adrien Treuille(전 카네기멜론 교수)가 "Python 개발자가 HTML/CSS/JS를 몰라도 웹 앱을 만들 수 있어야 한다"는 철학으로 Streamlit을 출시했습니다. 2022년 Snowflake에 인수되어 현재는 Snowflake 생태계의 핵심 도구이기도 하지만, Databricks Apps에서도 공식 지원하는 프레임워크입니다.

### 핵심 원리: Top-Down 리렌더링

Streamlit의 동작 방식은 다른 웹 프레임워크와 근본적으로 다릅니다.

```
[사용자 입력] → [전체 스크립트 재실행 (위→아래)] → [UI 갱신]
```

**일반적인 웹 프레임워크**(React, Flask 등)는 이벤트 핸들러를 등록하고, 해당 이벤트가 발생하면 특정 컴포넌트만 업데이트합니다. 반면 **Streamlit** 은 사용자가 버튼을 클릭하거나, 슬라이더를 움직이거나, 텍스트를 입력할 때마다 **Python 스크립트 전체를 처음부터 다시 실행** 합니다.

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

** 장점:**
- Python만으로 완결되는 풀스택 개발 -- HTML, CSS, JavaScript 지식 불필요
- 가장 빠른 개발 속도 -- 채팅 UI를 30분 이내에 구현 가능
- 풍부한 위젯 생태계 -- 차트, 테이블, 지도, 파일 업로드 등 100여 개 내장 컴포넌트
- Databricks Apps 공식 지원 -- 프로덕션 배포까지 원활

** 한계:**
- ** 전체 리렌더링**: 사용자 입력마다 스크립트 전체 재실행 → 대규모 앱에서 성능 저하
- ** 멀티유저 세션 관리 제한**: `st.session_state`는 브라우저 탭 단위 → 서버 측 세션 공유 불가
- ** 커스텀 디자인 어려움**: CSS 오버라이드가 제한적, 기업 브랜딩 적용 까다로움
- **WebSocket 기반**: 동시접속 50명 이상 시 서버 부하 급증 (Databricks Apps에서는 자동 스케일링으로 완화)
- **SEO 불가**: 서버 사이드 렌더링이 아닌 WebSocket 기반이므로 검색엔진 노출 불가 (Agent 앱에서는 대부분 문제 아님)

{% hint style="success" %}
** 실전 팁**: Streamlit은 PoC와 파일럿 단계에서 "속도 vs 완성도" 트레이드오프의 최적 지점입니다. 2주 안에 경영진에게 데모를 보여야 한다면, Streamlit이 정답입니다.
{% endhint %}

---

## Gradio -- ML 데모의 표준

### 등장 배경

2019년, Stanford 박사과정이던 Abubakar Abid가 "ML 모델을 비개발자에게 시연할 수 있는 가장 쉬운 방법"을 목표로 Gradio를 만들었습니다. 2021년 Hugging Face에 인수된 후, Hugging Face Spaces의 기본 프레임워크가 되면서 ML/AI 데모의 사실상 표준으로 자리잡았습니다.

Gradio의 핵심 철학은 **"입력 → 함수 → 출력" 패턴** 입니다. 모든 ML 모델은 결국 입력을 받아 출력을 반환하는 함수이므로, 이 패턴만 정의하면 UI가 자동 생성됩니다.

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
| ** 설계 철학**| 입력 → 함수 → 출력 | 스크립트 위→아래 실행 |
| ** 채팅 UI**| `ChatInterface` (간결) | `st.chat_input` + `st.chat_message` (유연) |
| ** 공유**| `share=True`로 즉시 공개 URL | 별도 배포 필요 |
| ** 대시보드**| 제한적 (Blocks로 가능하나 번거로움) | 강력 (대시보드 특화) |
| ** 레이아웃**| 제한적 | columns, tabs, sidebar 등 유연 |
| ** 생태계**| Hugging Face Spaces | Snowflake, Databricks Apps |
| ** 멀티모달**| 이미지/오디오/비디오 입출력 내장 | 별도 구현 필요 |

{% hint style="info" %}
** 선택 기준**: ML 모델 데모, Hugging Face 모델 활용, 멀티모달 Agent라면 Gradio. 대시보드가 포함된 Agent 앱, Databricks Apps 배포가 목표라면 Streamlit.
{% endhint %}

### Gradio의 한계

- ** 복잡한 레이아웃 어려움**: 대시보드 + 채팅 + 사이드바 같은 복합 레이아웃 구현이 번거로움
- ** 세밀한 UX 커스텀 제한**: 테마 변경은 가능하지만, 컴포넌트 수준의 디자인 커스텀은 제한적
- ** 프로덕션 안정성**: 대규모 동시접속 환경에서의 검증 사례가 Streamlit 대비 적음
- **Databricks Apps 지원은 되지만**: Streamlit보다 Databricks 생태계 통합 예제가 적음

---

[README로 돌아가기](README.md) | 다음: [Chainlit & Dash](chainlit-dash.md)
