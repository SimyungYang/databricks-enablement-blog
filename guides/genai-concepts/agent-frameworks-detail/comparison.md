# 종합 비교 & 선택 가이드

프레임워크 종합 비교 테이블, 의사결정 트리, Agent UI 개요, 2025년 생태계 트렌드, 고객 FAQ, 연습문제를 다룹니다.

---

## 프레임워크 종합 비교

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

## 프레임워크 선택 가이드 -- 의사결정 트리

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

## Agent UI/배포 기술 스택

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

## 2025 Agent 생태계 트렌드

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

## 고객이 자주 묻는 질문

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

## 연습 문제

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

**핵심 차이**: LangGraph는 "**데이터 중심 상태 관리**" (구조화된 State), OpenAI SDK는 "**대화 중심 상태 관리**" (메시지 히스토리)입니다.

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

## 참고 자료

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

- **Databricks Agent Bricks 가이드**: [Agent Bricks](../../agent-bricks/README.md) -- Knowledge Assistant, Genie Agent, Supervisor Agent 실전 구축
- **RAG 가이드**: [RAG (검색 증강 생성)](../../rag/README.md) -- Agent의 도구로 활용되는 RAG 파이프라인 구축
- **MCP 가이드**: [MCP (Model Context Protocol)](../../mcp/README.md) -- Agent의 도구 접근 프로토콜 표준
- **A2A 가이드**: [A2A (Agent-to-Agent)](../a2a.md) -- Agent 간 통신 프로토콜
- **AI Agent 아키텍처**: [Agent 아키텍처](../agent-architecture.md) -- ReAct, Tool Use, Multi-Agent 패턴의 기초

---

[README로 돌아가기](README.md)
