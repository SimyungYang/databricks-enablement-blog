# A2A (Agent-to-Agent Protocol)

A2A는 Google이 2025년 4월에 발표한 **에이전트 간 통신을 위한 개방형 프로토콜**입니다. 서로 다른 프레임워크와 벤더에서 만든 AI Agent들이 표준화된 방식으로 협업할 수 있게 합니다.

{% hint style="info" %}
A2A와 MCP는 경쟁이 아닌 **보완 관계**입니다. MCP는 Agent가 도구에 접근하는 방법을, A2A는 Agent끼리 대화하는 방법을 정의합니다.
{% endhint %}

---

## A2A란?

기존에는 여러 Agent를 협업시키려면 동일한 프레임워크 안에서만 가능했습니다. A2A는 이 제약을 없애고, **이기종 Agent 간 상호운용성**을 제공합니다.

### 핵심 설계 원칙

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

```
/.well-known/agent.json 에 게시
```

| 필드 | 설명 |
|------|------|
| `name` | Agent 이름 |
| `description` | 능력 설명 |
| `url` | A2A 엔드포인트 |
| `skills` | 수행 가능한 작업 목록 |
| `authentication` | 인증 방식 |

### 2. Task (작업 단위)

A2A에서 모든 상호작용은 Task 중심으로 이루어집니다.

| 상태 | 설명 |
|------|------|
| `submitted` | 작업 제출됨 |
| `working` | 처리 중 |
| `input-required` | 추가 정보 필요 |
| `completed` | 완료 |
| `failed` | 실패 |
| `canceled` | 취소 |

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

## A2A + MCP 결합 아키텍처

실제 엔터프라이즈 환경에서는 A2A와 MCP가 함께 사용됩니다.

| 레이어 | 프로토콜 | 역할 |
|--------|----------|------|
| Agent ↔ Agent | **A2A** | 전문 Agent 간 작업 위임 |
| Agent ↔ Tool | **MCP** | Agent가 외부 도구/데이터 접근 |
| Agent ↔ Human | UI/API | 사용자 인터페이스 |

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

## 참고 자료

- [Google A2A Protocol 공식 사이트](https://google.github.io/A2A/)
- [A2A GitHub 리포지토리](https://github.com/google/A2A)
- [Google Cloud Blog - A2A 발표](https://cloud.google.com/blog/products/ai-machine-learning/a2a-a-new-era-of-agent-interoperability)
- [Anthropic MCP 공식 문서](https://modelcontextprotocol.io/)
