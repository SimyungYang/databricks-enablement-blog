# A2A (Agent-to-Agent Protocol)

A2A는 Google이 2025년 4월에 발표한 ** 에이전트 간 통신을 위한 개방형 프로토콜** 입니다. 서로 다른 프레임워크와 벤더에서 만든 AI Agent들이 표준화된 방식으로 협업할 수 있게 합니다.

{% hint style="info" %}
** 학습 목표**
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
| ** 도구 수 제한**| Agent에 도구가 15~20개를 넘으면 LLM의 도구 선택 정확도가 급감 |
| ** 전문성 분산**| 한 Agent가 모든 도메인을 다루면 각 영역의 정확도가 떨어짐 |
| ** 컨텍스트 한계**| System Prompt + 도구 설명 + 대화 이력이 컨텍스트 윈도우를 빠르게 소모 |
| ** 벤더 종속**| 같은 프레임워크 안에서만 Agent 협업 가능 (LangGraph↔LangGraph만 가능) |

{% hint style="success" %}
** 비유**: 한 사람이 회계, 법률, 마케팅, 개발을 모두 하면 전문성이 떨어집니다. 각 분야 전문가가 ** 표준화된 업무 프로토콜** 로 협업하는 것이 더 효율적입니다. A2A는 이 "업무 프로토콜"에 해당합니다.
{% endhint %}

### 기존 Multi-Agent의 문제

기존에는 여러 Agent를 협업시키려면 동일한 프레임워크 안에서만 가능했습니다. A2A는 이 제약을 없애고, ** 이기종 Agent 간 상호운용성** 을 제공합니다.

| 기존 방식 | A2A 방식 |
|-----------|----------|
| 같은 프레임워크 안에서만 협업 | 프레임워크 무관하게 HTTP로 협업 |
| Agent 내부 구현을 알아야 연동 | Agent Card만 읽으면 연동 가능 |
| 독자적 통신 방식 | JSON-RPC 2.0 표준 |
| 벤더 종속 | 오픈 프로토콜 |

---

## A2A를 이해하기 위한 배경 지식

REST API를 설계해 본 경험이 있다면 A2A의 구조를 빠르게 이해할 수 있습니다. 하지만 A2A는 기존 API 통신과 근본적으로 다른 철학을 가지고 있으므로, 그 차이를 먼저 짚고 넘어가겠습니다.

### 분산 시스템의 기본 원리: CAP 정리와 Agent

분산 시스템을 설계할 때 빠지지 않는 이론이 **CAP 정리** 입니다. 어떤 분산 시스템도 다음 세 가지를 동시에 만족할 수 없다는 원칙입니다.

| CAP 요소 | 분산 DB에서의 의미 | Agent 통신에서의 의미 |
|----------|-------------------|---------------------|
| **Consistency**| 모든 노드가 같은 데이터를 봄 | 모든 Agent가 동일한 Task 상태를 봄 |
| **Availability**| 모든 요청에 항상 응답 | Agent가 항상 요청을 받아 처리 가능 |
| **Partition Tolerance**| 네트워크 장애에도 동작 | Agent 간 통신이 끊겨도 시스템 유지 |

A2A 프로토콜은 이 중 **AP(가용성 + 분할 내성)** 를 우선합니다. 그 이유는 다음과 같습니다:

- **Agent는 독립적으로 배포됩니다.** 항공 Agent가 다운되어도 호텔 Agent는 계속 작동해야 합니다.
- ** 네트워크 분할은 현실입니다.** 서로 다른 클라우드, 다른 VPC에 배포된 Agent 간 통신 장애는 일상적입니다.
- ** 일관성은 Task 단위로 보장합니다.** 전체 시스템의 강한 일관성(Strong Consistency) 대신, 각 Task의 상태 전이가 올바르게 이루어지는 ** 최종적 일관성(Eventual Consistency)** 을 채택합니다.

{% hint style="info" %}
**REST API 개발자를 위한 비유**: 마이크로서비스에서 서비스 A가 다운되어도 서비스 B가 동작하는 것과 같은 원리입니다. A2A에서도 각 Agent는 독립적인 서비스이며, 한 Agent의 장애가 전체 시스템을 멈추지 않습니다.
{% endhint %}

### RPC vs REST vs 이벤트 기반 vs A2A

기존 서비스 통신 방식과 A2A는 무엇이 근본적으로 다를까요?

| 통신 방식 | 철학 | 호출 예시 | 호출자가 아는 것 |
|-----------|------|----------|----------------|
| **RPC**| "이 함수를 이 인자로 실행해라" | `searchFlights(from, to, date)` | 함수 시그니처, 내부 로직 추측 가능 |
| **REST**| "이 리소스를 이렇게 조작해라" | `GET /flights?from=ICN&to=CJU` | 리소스 구조, HTTP 메서드 의미 |
| ** 이벤트 기반**| "이런 일이 발생했으니 알아서 처리해라" | `FlightBooked { flightId: 123 }` | 이벤트 스키마만 알면 됨 |
| **A2A**| "이 일을 맡긴다. 어떻게 하는지는 네가 알아서" | `tasks/send { "항공편 찾아줘" }` | Agent의 능력(Card)만 알면 됨 |

핵심 차이는 **Opacity(불투명성)** 입니다:

- REST API를 호출할 때, 클라이언트는 엔드포인트가 어떤 DB를 쓰는지, 어떤 로직을 거치는지 어느 정도 예측할 수 있습니다.
- A2A에서 Task를 위임할 때, 클라이언트는 상대 Agent가 ** 어떤 LLM을 쓰는지, 어떤 프롬프트를 사용하는지, 내부적으로 몇 단계를 거치는지** 전혀 모릅니다. 알 필요도 없습니다.

이것이 바로 A2A의 설계 원칙 중 **Opaque** 가 의미하는 것입니다.

```
REST API 호출:
  Client → "GET /flights?from=ICN&to=CJU&date=2026-03-15" → Server
  Client는 응답 스키마를 정확히 알고, 파싱 로직을 미리 작성

A2A Task 위임:
  Client → "3월 15일 인천-제주 항공편 찾아줘" → Agent
  Agent가 내부적으로 3개 API를 호출하든, LLM으로 추론하든, 사람에게 물어보든
  Client는 최종 결과만 받으면 됨
```

{% hint style="warning" %}
**Delegation(위임) vs Invocation(호출)**: REST API는 "무엇을 어떻게 해라"를 지시하는 ** 호출** 입니다. A2A는 "이 일을 맡긴다"는 ** 위임** 입니다. 위임의 핵심은 "방법의 자율성"을 상대에게 부여하는 것입니다. 이 차이가 Agent 간 통신을 기존 API와 근본적으로 구별합니다.
{% endhint %}

---

## A2A 핵심 설계 원칙

| 원칙 | 설명 |
|------|------|
| **Agentic**| Agent는 도구가 아닌 자율적 행위자로 취급 |
| **Composable**| 기존 표준(HTTP, JSON-RPC, SSE)을 조합하여 구현 |
| **Opaque**| Agent 내부 구현(프롬프트, 모델)을 공개하지 않음 |
| **Enterprise-ready**| 인증, 보안, 모니터링 등 엔터프라이즈 요구사항 충족 |

---

## A2A vs MCP 비교

| 항목 | MCP (Model Context Protocol) | A2A (Agent-to-Agent) |
|------|------------------------------|----------------------|
| ** 개발사**| Anthropic (2024.11) | Google (2025.04) |
| ** 목적**| LLM이 외부 도구/데이터에 접근 | Agent 간 작업 위임 및 협업 |
| ** 통신 대상**| LLM ↔ Tool/Data Source | Agent ↔ Agent |
| ** 비유**| USB-C 포트 (장치 연결) | 표준 외교 프로토콜 (국가 간 통신) |
| **Agent 취급**| 도구 제공자 (수동적) | 자율적 행위자 (능동적) |
| ** 상태 관리**| Stateless (각 호출 독립) | Stateful (Task 생명주기 관리) |
| ** 스트리밍**| 지원 | 지원 (SSE 기반) |
| ** 관계**| 보완적 — 함께 사용 가능 | 보완적 — 함께 사용 가능 |

{% hint style="success" %}
** 한 마디 정리**: MCP는 "Agent가 도구를 쓰는 방법", A2A는 "Agent가 다른 Agent에게 일을 맡기는 방법"입니다.
{% endhint %}

---

## 세부 페이지

| 페이지 | 내용 |
|--------|------|
| [핵심 개념](concepts.md) | Agent Card, Task 라이프사이클, Message & Artifact, Streaming |
| [구현 가이드](implementation.md) | 동작 흐름, 여행 예약 시나리오, A2A+MCP 결합, Python 구현 예시 |
| [프로덕션 운영](production.md) | 보안, 현실적 한계와 대안, 설계 패턴 카탈로그, Databricks 활용, FAQ |

---

## 참고 자료

- [Google A2A Protocol 공식 사이트](https://google.github.io/A2A/)
- [A2A GitHub 리포지토리](https://github.com/google/A2A)
- [A2A 공식 스펙 문서](https://google.github.io/A2A/specification/)
- [Google Cloud Blog - A2A 발표](https://cloud.google.com/blog/products/ai-machine-learning/a2a-a-new-era-of-agent-interoperability)
- [Anthropic MCP 공식 문서](https://modelcontextprotocol.io/)
