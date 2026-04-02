# 프로덕션 운영

## A2A 보안 고려사항

엔터프라이즈 환경에서 A2A를 도입할 때, 보안은 가장 중요한 설계 요소입니다.

### 인증 (Authentication)

- Agent Card의 `authentication.schemes` 필드로 지원하는 인증 방식을 명시합니다
- **OAuth2** 가 권장 방식입니다. 토큰 만료, 스코프 제한 등 세밀한 제어가 가능합니다
- **API Key** 는 구현이 간단하지만 보안이 약합니다. 개발/테스트 환경에만 권장합니다
- **Mutual TLS (mTLS)** 는 양방향 인증서 검증으로, 높은 보안이 필요한 금융/의료 환경에 권장됩니다

### 인가 (Authorization)

- Agent가 요청할 수 있는 skill 범위를 제한해야 합니다
- Task 생성 권한과 특정 skill 호출 권한을 분리하여 관리합니다
- 예: "항공 Agent는 `search_flights`만 가능, `book_flight`는 별도 권한 필요"와 같이 세분화합니다

### 데이터 보안

- Agent 간 전달되는 모든 데이터는 **TLS 암호화가 필수** 입니다
- PII(개인정보) 전달 시 마스킹 또는 토큰화를 적용합니다
- 민감 데이터는 Artifact로 직접 전달하지 않고, **참조 ID만 전달** 하여 수신 Agent가 별도 인증 후 조회하도록 합니다

### Trust Boundary (신뢰 경계)

- **내부 Agent** 와 **외부 Agent** 를 명확히 구분합니다
- 외부 Agent의 응답은 항상 검증합니다 (LLM-as-Judge 또는 규칙 기반 검증)
- 외부 Agent에게 **쓰기 권한** 을 부여할 때는 특히 주의가 필요합니다

### 주요 위협과 대응 방안

| 위협 | 설명 | 대응 방안 |
|------|------|----------|
| **Agent 위장** | 악의적 Agent가 정상 Agent를 사칭 | Agent Card 서명 검증, mTLS |
| **데이터 유출** | 민감 정보가 외부 Agent에 전달 | PII 마스킹, 참조 ID 사용 |
| **권한 상승** | Agent가 허용 범위 밖의 행동 수행 | skill별 세분화된 인가 |
| **중간자 공격** | 통신 가로채기 | TLS 암호화 필수 |

{% hint style="warning" %}
보안 설계의 핵심 원칙: **최소 권한 원칙(Principle of Least Privilege)** 을 적용하세요. 각 Agent에게는 작업 수행에 필요한 최소한의 skill과 데이터 접근 권한만 부여합니다.
{% endhint %}

---

## A2A의 현실적 한계와 대안

### 현재 A2A 채택 현실

A2A는 강력한 비전을 가지고 있지만, 2026년 현재 채택 현실은 냉정하게 바라볼 필요가 있습니다.

| 항목 | 현실 |
|------|------|
| **주도 기업** | Google Cloud 중심. Salesforce, SAP 등 참여하지만 실제 프로덕션 구현은 제한적 |
| **SDK 성숙도** | Python/JS SDK 제공되지만 빠르게 변경 중. 프로덕션 안정성 미검증 |
| **실제 사용 사례** | 대부분 PoC 또는 데모 수준. 대규모 프로덕션 배포 사례는 희소 |
| **대부분의 기업 현실** | MCP만으로 도구 연동 충분. 내부 Multi-Agent는 프레임워크 내부 통신으로 해결 |

**A2A가 진짜 필요한 시나리오는 제한적입니다:**

1. **이기종 벤더의 Agent가 협업** 해야 하는 경우 (예: 우리 Agent + 파트너사 Agent)
2. **조직 간 경계를 넘는 Agent 통신**(예: 본사 Agent + 자회사 Agent)
3. **Agent 마켓플레이스** 구축 시 (다양한 3rd party Agent를 플러그인처럼 연결)

그 외의 경우 — 예를 들어 같은 팀이 만든 여러 Agent를 협업시키는 것이라면 — LangGraph, CrewAI, Databricks Agent Framework 등의 내부 오케스트레이션이 훨씬 간단하고 효율적입니다.

### MCP로 Multi-Agent를 구현하는 패턴

A2A 없이도 MCP만으로 Agent 간 통신이 가능합니다. 핵심 아이디어는 **Agent를 MCP 서버로 래핑** 하는 것입니다.

```
[Orchestrator Agent]
    │
    ├── MCP ──→ [데이터 분석 Agent (MCP Server로 래핑)]
    │              └── Tool: "analyze" (내부적으로 LLM 호출)
    │
    ├── MCP ──→ [리포트 생성 Agent (MCP Server로 래핑)]
    │              └── Tool: "generate_report" (내부적으로 LLM 호출)
    │
    └── MCP ──→ [Slack 알림 Agent (MCP Server로 래핑)]
                   └── Tool: "notify" (내부적으로 LLM 호출)
```

이 방식의 **장점과 한계**:

| 항목 | MCP 래핑 방식 | A2A 방식 |
|------|-------------|----------|
| 구현 복잡도 | 낮음 (기존 MCP 인프라 활용) | 높음 (새 프로토콜 도입) |
| 상태 관리 | 없음 (Stateless) | 있음 (Task lifecycle) |
| Agent 발견 | 수동 설정 | Agent Card로 자동 발견 |
| 중간 결과 스트리밍 | 제한적 | SSE로 네이티브 지원 |
| `input-required` 패턴 | 구현 어려움 | 프로토콜 수준에서 지원 |

{% hint style="info" %}
**실용적 조언**: 지금 당장 Multi-Agent가 필요하다면 MCP 래핑 방식으로 시작하세요. 상태 관리나 Agent 발견이 절실해지는 시점에 A2A로 전환해도 늦지 않습니다.
{% endhint %}

### 현실적 도입 로드맵

| 단계 | 시기 | 기술 | 목표 |
|------|------|------|------|
| **1단계** | 지금 | **MCP** | Agent가 도구와 데이터에 접근하는 기반 구축 |
| **2단계** | 6개월 내 | **LangGraph / Databricks Agent SDK** | 내부 Multi-Agent 오케스트레이션. 같은 조직 내 Agent 협업 |
| **3단계** | 필요시 (1년+) | **A2A** | 외부 Agent 연동. 이기종 벤더/조직 간 Agent 협업 |

각 단계는 이전 단계를 대체하는 것이 아니라 **쌓아 올리는 것** 입니다. 3단계에서도 MCP와 내부 오케스트레이션은 그대로 사용됩니다.

---

## A2A 설계 패턴 카탈로그

A2A를 활용한 Agent 간 협업에는 몇 가지 반복되는 설계 패턴이 있습니다. 각 패턴의 특성과 적합한 시나리오를 이해하면, 아키텍처 설계 시 올바른 선택을 할 수 있습니다.

### 1. 위임 패턴 (Delegation)

가장 기본적인 패턴입니다. Client Agent가 Server Agent에 전체 작업을 맡기고 결과만 받습니다.

```
Client Agent ──tasks/send──→ Server Agent
Client Agent ←──completed───── Server Agent (Artifact 포함)
```

**적합한 시나리오**: 작업이 명확하고, 추가 협의 없이 처리 가능한 경우.
- 번역 요청: "이 문서를 영어로 번역해줘"
- 데이터 조회: "지난 달 매출 합계를 알려줘"
- 코드 리뷰: "이 PR을 리뷰해줘"

### 2. 협상 패턴 (Negotiation)

`input-required` 상태를 활용하여 Agent 간 **여러 라운드의 대화** 로 요구사항을 구체화합니다.

```
Client Agent ──tasks/send──→ Server Agent
Client Agent ←──input-required── Server Agent ("예산 범위는?")
Client Agent ──message 추가──→ Server Agent ("100만원 이내")
Client Agent ←──input-required── Server Agent ("조식 포함 필요?")
Client Agent ──message 추가──→ Server Agent ("네, 조식 포함")
Client Agent ←──completed───── Server Agent (최종 결과)
```

**적합한 시나리오**: 초기 요구사항이 모호하거나, 단계적 구체화가 필요한 경우.
- 호텔 예약: 날짜만 주어지고 세부 조건은 대화로 확인
- 보고서 작성: 대략적 주제에서 구체적 분석 방향을 좁혀감
- IT 헬프데스크: 증상 설명 → 추가 진단 질문 → 해결책 제시

### 3. 파이프라인 패턴 (Pipeline)

Agent A의 output이 Agent B의 input이 되는 **순차 처리** 패턴입니다.

```
Orchestrator ──Task 1──→ Agent A (데이터 수집)
Orchestrator ←──Artifact 1─── Agent A
Orchestrator ──Task 2 (Artifact 1 포함)──→ Agent B (데이터 정제)
Orchestrator ←──Artifact 2─── Agent B
Orchestrator ──Task 3 (Artifact 2 포함)──→ Agent C (시각화)
Orchestrator ←──Artifact 3─── Agent C
```

**적합한 시나리오**: 작업이 명확한 단계로 나뉘고, 각 단계가 서로 다른 전문성을 요구하는 경우.
- ETL 파이프라인: 추출 Agent → 변환 Agent → 적재 Agent
- 콘텐츠 제작: 리서치 Agent → 초안 작성 Agent → 편집 Agent
- 보안 분석: 로그 수집 Agent → 이상 탐지 Agent → 대응 권고 Agent

**주의사항**: Orchestrator Agent가 전체 파이프라인의 흐름을 관리해야 하며, 중간 단계 실패 시 처리 전략(재시도 또는 중단)을 미리 정의해야 합니다.

### 4. 경쟁 패턴 (Competition)

같은 Task를 **여러 Agent에 동시 전송** 하고, 가장 빠르거나 가장 좋은 결과를 채택합니다.

```
Orchestrator ──Task (동일)──→ Agent A (GPT 기반)
Orchestrator ──Task (동일)──→ Agent B (Claude 기반)
Orchestrator ──Task (동일)──→ Agent C (Gemini 기반)

Orchestrator ←──결과 A── Agent A (3초)
Orchestrator ←──결과 B── Agent B (2초)  ← 가장 빠름
Orchestrator ←──결과 C── Agent C (5초)

→ 결과 B 채택 (또는 3개 결과를 비교하여 최선 선택)
```

**적합한 시나리오**: 결과의 품질이 중요하거나, 여러 관점이 필요한 경우.
- 번역 품질 비교: 여러 번역 Agent의 결과를 비교하여 최선 채택
- 가격 비교: 여러 항공사/호텔 Agent에 동시 검색하여 최저가 선택
- LLM-as-Judge: 여러 Agent의 답변을 평가 Agent가 비교 채점

**비용 고려**: 동일 Task를 여러 Agent에 보내므로 비용이 N배 증가합니다. 품질이 중요한 고가치 작업에만 사용하세요.

### 5. 패턴 선택 가이드

| 상황 | 권장 패턴 |
|------|----------|
| 작업이 명확하고 단순 | 위임 (Delegation) |
| 요구사항이 모호하여 대화가 필요 | 협상 (Negotiation) |
| 작업이 여러 단계로 나뉨 | 파이프라인 (Pipeline) |
| 최선의 결과를 얻어야 함 | 경쟁 (Competition) |
| 복잡한 실제 시나리오 | 패턴 조합 (예: 파이프라인 + 각 단계에서 협상) |

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

A2A 도입을 검토하는 고객이 자주 가지는 오해들입니다. 특히 MCP와의 관계를 정확히 이해하는 것이 중요합니다.

| 오해 | 사실 |
|------|------|
| "A2A는 MCP를 대체한다" | A2A와 MCP는 서로 다른 문제를 해결합니다. 보완 관계이며 함께 사용합니다. |
| "A2A를 쓰면 모든 Agent가 자동으로 협업한다" | Agent Card를 잘 설계하고, 각 Agent의 스킬을 명확히 정의해야 협업이 원활합니다. |
| "A2A는 Google 전용 기술이다" | A2A는 오픈 프로토콜입니다. Google, Salesforce, SAP 등 50개 이상의 기업이 참여합니다. |
| "기존 Multi-Agent 시스템을 A2A로 교체해야 한다" | 같은 조직 내 Agent는 기존 프레임워크 내부 통신이 효율적일 수 있습니다. A2A는 **이기종 시스템 간** 통신에 가장 가치가 있습니다. |

---

## 고객이 자주 묻는 질문

### "A2A를 지금 도입해야 하나요?"

아직 초기 단계입니다. 내부 Multi-Agent 시스템은 기존 프레임워크(LangGraph, Databricks Agent Framework 등)로 충분히 구현할 수 있습니다. **외부 벤더의 Agent와 연동** 이 필요하거나, **이기종 프레임워크 간 협업** 이 요구될 때 A2A 도입을 검토하세요.

### "A2A와 REST API의 차이가 뭔가요?"

REST API는 사전에 정의된 엔드포인트를 호출하는 방식입니다. A2A는 Agent가 **자율적으로 상대방의 능력을 발견** 하고 작업을 위임합니다. 핵심 차이는 세 가지입니다:
- **자기소개 (Agent Card)**: Agent가 자신의 능력을 표준화된 형식으로 공개
- **상태 관리 (Task lifecycle)**: 작업의 진행 상황을 추적하고, 추가 정보 요청도 가능
- **스트리밍**: 장기 실행 작업의 중간 결과를 실시간으로 수신

### "MCP만 쓰면 안 되나요?"

단일 Agent가 여러 도구를 사용하는 데에는 MCP만으로 충분합니다. 하지만 **여러 독립적인 Agent가 협업** 해야 하는 경우에는 A2A가 필요합니다. 규모와 요구사항에 따라 선택하세요:
- 도구 연동만 필요 → **MCP**
- Agent 간 협업 필요 → **A2A**
- 둘 다 필요 → **A2A + MCP 결합**

---

## 연습 문제

1. MCP와 A2A의 핵심 차이를 "택배 시스템"에 비유하여 설명하세요.
2. Agent Card에서 `skills` 필드가 왜 중요한지, 이 필드가 없다면 어떤 문제가 발생하는지 설명하세요.
3. Task 상태 중 `input-required`가 존재하는 이유와, 이 상태가 없다면 어떤 한계가 있을지 설명하세요.
4. "사내 IT 헬프데스크"를 A2A로 설계한다면 어떤 Agent들이 필요하고, 각 Agent의 Agent Card를 어떻게 정의하겠습니까?
