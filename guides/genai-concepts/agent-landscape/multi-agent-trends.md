# 멀티에이전트 & Agentic AI 트렌드 (2025)

2025년은 AI Agent가 "데모 단계"에서 "프로덕션 단계"로 전환되는 변곡점입니다. 단일 Agent의 한계가 명확해지면서, 멀티에이전트 시스템(MAS)이 엔터프라이즈 AI의 핵심 아키텍처로 부상하고 있습니다. 이 가이드는 오케스트레이션 패턴, 프로토콜 표준화, 관측성, 메모리 아키텍처, 안전성, 시장 동향, 그리고 Vibe Coding까지 -- 2025년 Agentic AI 지형의 전체 그림을 제공합니다.

{% hint style="info" %}
**학습 목표**
- 멀티에이전트 오케스트레이션 5대 패턴의 설계 원리와 적용 기준을 설명할 수 있다
- MCP와 A2A 프로토콜의 역할 분담과 상호보완 관계를 이해한다
- Agent 관측성(Observability)의 핵심 메트릭과 도구 생태계를 파악한다
- Agent Memory의 유형별 설계 전략을 수립할 수 있다
- 엔터프라이즈 Agent 거버넌스 프레임워크를 적용할 수 있다
- Databricks 플랫폼에서의 멀티에이전트 구현 전략을 수립할 수 있다
{% endhint %}

{% hint style="warning" %}
** 용어 정리**: 이 문서에서 "Agentic AI"는 ** 복수의 Agent가 협업하는 시스템 전체**를, "AI Agent"는 ** 그 시스템을 구성하는 개별 컴포넌트**를 지칭합니다. 이 구분은 Gartner, Forrester 등 주요 애널리스트 기관에서도 채택한 표준 용법입니다.
{% endhint %}

---

## 1. 멀티에이전트 오케스트레이션 패턴 -- 5종 심층 비교

멀티에이전트 시스템의 성패는 "Agent를 어떻게 조율하는가"에 달려 있습니다. 2025년 현재 프로덕션에서 검증된 5가지 핵심 패턴을 비교합니다.

### 1.1 패턴 총괄 비교

| 패턴 | 핵심 원리 | Agent 수 | 적합 시나리오 | 대표 프레임워크 | 토큰 효율 |
|------|-----------|----------|--------------|----------------|-----------|
| **Supervisor/Router** | 중앙 라우터가 의도 분류 후 전문 Agent에 위임 | 3~15 | CS 봇, 사내 포탈 | LangGraph, Databricks | 높음 |
| **Swarm/Handoff** | Agent 간 직접 핸드오프, 공유 블랙보드 | 5~20 | 탐색적 리서치, 브레인스토밍 | OpenAI Agents SDK | 중간 |
| **Hierarchical** | 다단계 관리자 체인, 트리 구조 | 50+ | 대규모 엔터프라이즈 워크플로 | CrewAI, IBM Research | 낮음 |
| **Collaborative/Debate** | 에이전트 간 다회전 토론, 합의 도출 | 2~5 | 의사결정, 코드 리뷰 | AutoGen (MS) | 낮음 |
| **Pipeline** | 순차적 처리, 각 단계가 전문화 | 3~10 | 콘텐츠 생성, 데이터 처리 | LangGraph, AWS Strands | 높음 |

### 1.2 Supervisor/Router 패턴 (프로덕션 최다 채택)

** 원리**: 하나의 Supervisor Agent가 사용자 입력의 ** 의도(intent)를 분류**한 뒤, 해당 도메인의 전문 Agent에게 작업을 위임합니다. 전문 Agent의 결과를 수집하여 최종 응답을 생성합니다.

```
사용자 요청
    │
    ▼
┌─────────────┐
│  Supervisor  │  ← 의도 분류 (routing)
│  (Router)    │
└─────┬───────┘
      │
  ┌───┼───┬───┐
  ▼   ▼   ▼   ▼
 HR  IT  재무  법무   ← 전문 Agent들
Agent Agent Agent Agent
```

** 왜 프로덕션에서 가장 많이 쓰이는가?**

1. ** 토큰 효율성**: 라우팅 단계에서 소형 모델(예: GPT-4o-mini, DBRX)을 사용하고, 전문 Agent에서만 대형 모델을 호출하면 ** 토큰 비용을 60~80% 절감**가능
2. ** 장애 격리**: 한 전문 Agent가 실패해도 다른 Agent에 영향 없음
3. ** 점진적 확장**: 새 도메인 추가 시 전문 Agent만 추가하면 됨
4. ** 디버깅 용이**: 라우팅 로그만 보면 어떤 Agent가 호출되었는지 즉시 파악

{% hint style="success" %}
**Databricks 매핑**: Databricks의 **Supervisor Agent**(Agent Bricks)가 정확히 이 패턴입니다. Knowledge Assistant, Genie Agent 등을 하위 Agent로 등록하고, Supervisor가 라우팅합니다.
{% endhint %}

### 1.3 Swarm/Handoff 패턴

** 원리**: OpenAI가 제안한 패턴으로, Agent들이 ** 공유 블랙보드(shared context)**를 통해 상태를 공유하며, 한 Agent가 작업을 완료하면 다음 Agent에게 직접 ** 핸드오프**합니다. 중앙 제어자 없이 Agent 간 자율적 협업이 이루어집니다.

```
Agent A ──handoff──▶ Agent B ──handoff──▶ Agent C
    │                    │                    │
    └────────────────────┴────────────────────┘
                공유 블랙보드 (Shared State)
```

** 장점**:
- 탐색적 작업에 강함 (각 Agent가 자율적으로 경로 결정)
- 중앙 병목 없음
- OpenAI Agents SDK에서 네이티브 지원 (`handoff()` 함수)

** 단점**:
- 무한 루프 위험 (Agent A → B → A → B...)
- 디버깅 난이도 높음 (제어 흐름이 분산)
- 토큰 소비 예측 어려움

{% hint style="warning" %}
** 주의**: Swarm 패턴은 ** 탐색적 리서치, 브레인스토밍**등에 적합하지만, ** 결정론적 비즈니스 프로세스**(예: 결재, 주문 처리)에는 부적합합니다. 이런 경우 Supervisor 또는 Pipeline 패턴을 사용하세요.
{% endhint %}

### 1.4 Hierarchical 패턴 (대규모 시스템)

** 원리**: IBM Research에서 검증한 패턴으로, **50개 이상의 Agent** 를 관리해야 하는 대규모 시스템에 적합합니다. Supervisor 패턴을 재귀적으로 중첩하여 트리 구조를 형성합니다.

```
              CEO Agent
             /    |    \
        영업팀   기술팀   운영팀
        /  \     / \     / \
      A1  A2   A3  A4  A5  A6   ← 실행 Agent
```

**핵심 설계 원칙**:
- **Span of Control**: 한 관리자 Agent가 관할하는 하위 Agent는 **5~7개** 이내 (인간 조직론과 동일)
- **Escalation Path**: 하위 Agent가 해결 못한 문제는 상위로 에스컬레이션
- **Context Compression**: 상위로 올릴 때 컨텍스트를 요약하여 토큰 절약

** 대표 사례**: CrewAI의 `hierarchical` process 모드

### 1.5 Collaborative/Debate 패턴

** 원리**: Microsoft AutoGen이 대표하는 패턴으로, 2개 이상의 Agent가 ** 다회전 대화(multi-turn conversation)**를 통해 문제를 해결합니다. "토론을 통한 합의" 메커니즘입니다.

```
┌──────────┐      ┌──────────┐
│ Agent A   │ ◄──► │ Agent B   │   ← 다회전 토론
│ (찬성 측)  │      │ (반대 측)  │
└──────────┘      └──────────┘
      │                  │
      └──────┬───────────┘
             ▼
        합의 도출 / 최종 판단
```

** 적합 시나리오**:
- 코드 리뷰 (작성자 Agent vs 리뷰어 Agent)
- 투자 의사결정 (낙관론 Agent vs 비관론 Agent)
- 법률 검토 (규정 준수 Agent vs 비즈니스 Agent)

** 주의점**: 토론 라운드가 늘어날수록 토큰 소비가 ** 기하급수적**으로 증가합니다. 반드시 ** 최대 라운드 수(max_turns)**를 설정하세요.

### 1.6 Pipeline 패턴 (순차 처리)

** 원리**: 공장의 조립 라인처럼 각 Agent가 ** 하나의 전문 단계**를 담당하고, 결과물을 다음 Agent에게 넘깁니다.

```
Researcher → Writer → Editor → Fact-Checker → Publisher
    │           │         │          │            │
    ▼           ▼         ▼          ▼            ▼
 자료수집    초안작성    교정/편집   사실확인     최종발행
```

** 장점**:
- 각 단계를 독립적으로 최적화 가능 (모델, 프롬프트, 도구 각각 튜닝)
- 결정론적 실행 흐름 (디버깅 용이)
- 중간 결과물 캐싱으로 재실행 비용 절감

**Databricks에서의 구현**: Databricks Jobs의 **Task Dependencies** 를 활용하면 각 단계를 별도 Task로 관리하고, 실패 시 해당 단계만 재실행 가능

### 1.7 프레임워크별 패턴 매핑

| 프레임워크 | 기본 패턴 | 지원 패턴 | 특징 |
|-----------|----------|----------|------|
| **LangGraph** | Supervisor/Router | 모든 패턴 | 그래프 기반으로 어떤 패턴이든 구현 가능. 가장 유연 |
| **CrewAI** | Hierarchical | Pipeline, Collaborative | 역할(Role) 기반 설계. YAML로 Agent 정의 |
| **OpenAI Agents SDK** | Swarm/Handoff | Supervisor | `handoff()` 네이티브 지원. 가드레일 내장 |
| **AWS Strands** | Pipeline | Supervisor | 프로덕션 우선 설계. AWS 서비스 네이티브 통합 |
| **Google ADK** | 멀티패턴 | 모든 패턴 | A2A 프로토콜 네이티브. Google Cloud 통합 |
| **Databricks Agent Framework** | Supervisor | Pipeline | MLflow 통합 추적. Unity Catalog 거버넌스 |

{% hint style="info" %}
** 실전 권장 조합**: 대부분의 엔터프라이즈 프로젝트에서는 **LangGraph(오케스트레이션) + Databricks Agent Framework(거버넌스/배포/모니터링)** 조합이 최적입니다. LangGraph로 복잡한 흐름을 설계하고, Databricks로 프로덕션 운영을 관리하세요.
{% endhint %}

---

## 2. 프로토콜 표준화 -- MCP, A2A, 그리고 AAIF

2025년 멀티에이전트 생태계의 가장 중요한 변화는 **상호운용성 프로토콜의 표준화** 입니다. 더 이상 특정 프레임워크에 종속되지 않고, Agent와 도구, Agent와 Agent가 표준 프로토콜로 통신하는 시대가 열리고 있습니다.

### 2.1 프로토콜 스택 개요

```
┌─────────────────────────────────────────┐
│           Application Layer              │
│    (LangGraph, CrewAI, Databricks...)    │
├─────────────────────────────────────────┤
│         Agent-to-Agent (A2A)             │  ← Agent 간 통신
│    Agent Cards, Task Lifecycle, Streaming │
├─────────────────────────────────────────┤
│      Model Context Protocol (MCP)        │  ← Agent → Tool 연결
│    Resources, Tools, Prompts, Sampling    │
├─────────────────────────────────────────┤
│         Transport Layer                  │
│     HTTP/SSE, WebSocket, stdio           │
└─────────────────────────────────────────┘
```

### 2.2 MCP (Model Context Protocol) -- Agent-to-Tool 표준

| 항목 | 내용 |
|------|------|
| **발표** | Anthropic, 2024년 11월 |
| ** 역할** | Agent가 외부 도구/데이터 소스에 접근하는 표준 인터페이스 |
| ** 채택 규모** | npm 기준 **9,700만+ 다운로드**(2025 Q1) |
| ** 거버넌스** | AAIF (Agentic AI Forum, Linux Foundation 산하) |
| ** 핵심 개념** | Resources (데이터), Tools (함수 호출), Prompts (템플릿), Sampling (LLM 호출) |

**MCP가 해결하는 문제**:
- Agent 프레임워크마다 Tool 연결 방식이 달랐음 → **N x M 통합 문제**
- MCP 도입 후 → Agent는 MCP Client, Tool은 MCP Server → **N + M** 으로 축소

**MCP 아키텍처**:

```
┌──────────┐     MCP Protocol     ┌──────────────┐
│ MCP Host  │ ◄──────────────────► │ MCP Server    │
│ (Agent)   │   JSON-RPC over     │ (Tool/Data)   │
│           │   stdio / HTTP+SSE  │               │
└──────────┘                      └──────────────┘
    │
    ├── Databricks MCP Server (SQL, Unity Catalog, Vector Search)
    ├── GitHub MCP Server
    ├── Slack MCP Server
    └── ... (수천 개의 MCP Server)
```

{% hint style="success" %}
**Databricks MCP**: Databricks는 공식 MCP Server를 제공합니다. SQL 실행, Unity Catalog 탐색, Vector Search 쿼리, Genie 질의 등을 MCP 프로토콜로 통합할 수 있습니다. Claude Desktop, Cursor 등에서 바로 연결 가능합니다.
{% endhint %}

### 2.3 A2A (Agent-to-Agent) -- Agent 간 통신 표준

| 항목 | 내용 |
|------|------|
| ** 발표** | Google, 2025년 3월 |
| ** 역할** | 서로 다른 프레임워크/벤더의 Agent가 상호 통신하는 표준 |
| ** 채택 규모** | **150개+ 조직** 참여 (Salesforce, SAP, Databricks 등) |
| **현재 버전** | v0.3 (2025 Q1) |
| ** 거버넌스** | Linux Foundation |

**A2A의 핵심 개념**:

| 개념 | 설명 |
|------|------|
| **Agent Card** | Agent의 능력, 엔드포인트, 인증 정보를 기술하는 JSON 메타데이터 (`/.well-known/agent.json`) |
| **Task** | Agent 간 작업 단위. `submitted` → `working` → `completed/failed` 라이프사이클 |
| **Message** | Agent 간 주고받는 메시지. 텍스트, 파일, 구조화 데이터 포함 가능 |
| **Artifact** | Task 실행 결과물 (보고서, 이미지, 데이터셋 등) |
| **Streaming** | SSE 기반 실시간 진행 상황 전달 |

**MCP vs A2A -- 역할이 다르다**:

| 비교 항목 | MCP | A2A |
|----------|-----|-----|
| ** 통신 방향** | Agent → Tool (단방향) | Agent ↔ Agent (양방향) |
| ** 역할** | 도구 접근 표준화 | Agent 간 협업 표준화 |
| ** 비유** | USB 포트 (기기 연결) | HTTP 프로토콜 (서버 간 통신) |
| ** 성숙도** | 사실상 표준 (de facto) | 초기 채택 단계 |
| ** 채택 속도** | 매우 빠름 | 상대적으로 느림 |
| ** 상호 관계** | A2A와 상호보완 | MCP와 상호보완 |

{% hint style="warning" %}
**A2A 채택이 느린 이유**: A2A는 "Agent가 다른 Agent를 발견하고 협업하는" 시나리오를 전제합니다. 하지만 2025년 현재 대부분의 엔터프라이즈는 ** 단일 벤더 스택**내에서 Agent를 운영하고 있어, 크로스 벤더 Agent 협업 수요가 아직 제한적입니다. 2026~2027년에 본격적으로 채택될 것으로 전망됩니다.
{% endhint %}

### 2.4 AAIF (Agentic AI Forum) -- 표준화 거버넌스

2025년, Linux Foundation 산하에 **AAIF (Agentic AI Forum)** 가 설립되었습니다. MCP와 A2A를 포함한 Agentic AI 관련 표준을 통합 관리하는 것이 목표입니다.

**참여 조직**: Anthropic, Google, Microsoft, Databricks, Salesforce, SAP, AWS, Meta 등

**AAIF의 표준화 스택**:

| 레이어 | 프로토콜 | 상태 |
|--------|---------|------|
| Agent-to-Tool | MCP | 사실상 표준 |
| Agent-to-Agent | A2A | v0.3, 초기 채택 |
| Agent Communication Protocol | ACP | 신규, 설계 단계 |
| Agent Network Protocol | ANP | 신규, 설계 단계 |

### 2.5 실전 권장사항

1. ** 지금 당장**: MCP를 적극 도입하세요. 도구 통합의 표준이 이미 확정되었습니다.
2. **2025년 하반기**: A2A Agent Card를 설계해두세요. 멀티벤더 Agent 협업이 시작될 때 대비할 수 있습니다.
3. **ACP/ANP**: 아직 설계 단계이므로 관망하되, AAIF 발표를 모니터링하세요.

---

## 3. Agent Observability -- 관측성과 모니터링

멀티에이전트 시스템의 가장 큰 운영 과제는 "** 무엇이 잘못되었는지 알기 어렵다**"는 것입니다. 단일 LLM 호출은 입력/출력만 보면 되지만, 멀티에이전트 시스템은 **Agent 간 상호작용, 도구 호출 체인, 컨텍스트 전달** 등 추적해야 할 대상이 기하급수적으로 늘어납니다.

### 3.1 핵심 메트릭 체계

| 카테고리 | 메트릭 | 설명 | 허용 범위 (참고) |
|----------|--------|------|-----------------|
| **비용** | 토큰 사용량 | 에이전트별, 태스크별 토큰 소비 | 동일 태스크 대비 **50x 편차** 발생 가능! |
| **비용** | 달러/태스크 | 태스크 1건 처리 비용 | 비즈니스 가치 대비 ROI 계산 |
| ** 지연** | E2E Latency | 사용자 요청~최종 응답 시간 | 대화형: < 5s, 배치: SLA 기준 |
| ** 지연** | TTFT | Time to First Token | < 2s (사용자 체감 기준) |
| ** 신뢰성** | Tool Call 성공률 | 도구 호출 성공/실패 비율 | > 95% (이하면 프롬프트 튜닝 필요) |
| ** 신뢰성** | Task 완료율 | 태스크 정상 완료 비율 | > 90% |
| ** 품질** | Trajectory 분석 | Agent의 행동 경로가 최적이었는지 | 불필요한 Tool Call 3회 이상이면 비효율 |
| ** 품질** | 환각(Hallucination) 비율 | 사실과 다른 응답 비율 | < 5% |

{% hint style="warning" %}
** 토큰 비용의 50x 편차**: 동일한 질문에 대해 Agent의 경로 선택에 따라 토큰 소비가 ** 최대 50배**차이날 수 있습니다. 예를 들어, 단순 질문에 불필요하게 여러 Tool을 호출하거나, 대규모 컨텍스트를 반복 전달하는 경우입니다. **Trajectory 분석** 을 통해 이런 비효율을 탐지하고 최적화해야 합니다.
{% endhint %}

### 3.2 Tool Calling Accuracy -- 지배적 신뢰성 이슈

2025년 프로덕션 Agent 시스템의 **가장 빈번한 실패 원인** 은 Tool Calling 오류입니다.

| 실패 유형 | 설명 | 대응 방안 |
|-----------|------|----------|
| **잘못된 도구 선택** | 의도와 다른 도구 호출 | 도구 설명(description) 정밀화, Few-shot 예시 추가 |
| ** 잘못된 파라미터** | 필수 파라미터 누락/오류 | JSON Schema 검증 강화, 파라미터 기본값 설정 |
| ** 불필요한 호출** | 이미 답을 알지만 도구를 호출 | 프롬프트에 "도구 없이 답할 수 있으면 직접 답하라" 지시 |
| ** 호출 실패 후 무한 재시도** | 같은 오류를 반복 | 최대 재시도 횟수 설정, 폴백 전략 |

### 3.3 Observability 도구 비교

| 도구 | 유형 | 강점 | Databricks 통합 | 가격 모델 |
|------|------|------|-----------------|----------|
| **MLflow Tracing** | 오픈소스 | Databricks 네이티브. 자동 추적. Unity Catalog 연동 | 네이티브 | 무료 (Databricks 내) |
| **LangSmith** | SaaS | LangGraph 심층 통합. Playground. 데이터셋 관리 | API 연동 | 프리미엄 $39+/월 |
| **Arize Phoenix** | 오픈소스/SaaS | LLM 관측성 특화. Embedding 시각화 | 별도 연동 | 오픈소스 무료 |
| **Braintrust** | SaaS | 평가(Eval) 중심. CI/CD 통합 | API 연동 | 사용량 기반 |
| **Langfuse** | 오픈소스/SaaS | 자체 호스팅 가능. 비용 추적 우수 | 별도 연동 | 오픈소스 무료 |
| **AgentOps** | SaaS | Agent 전용. 세션 리플레이 | 별도 연동 | 프리미엄 |

{% hint style="success" %}
**Databricks 고객 권장**: **MLflow Tracing** 을 1차 관측 도구로 사용하세요. Databricks 환경에서 자동으로 trace가 수집되며, Unity Catalog의 거버넌스와 통합됩니다. LangGraph를 사용하는 경우 LangSmith를 보조 도구로 추가하면 개발 단계에서의 디버깅이 수월합니다.
{% endhint %}

### 3.4 관측성 구현 체크리스트

- [ ] 모든 Agent 호출에 **trace ID** 부여 (분산 추적)
- [ ] Tool Call별 **성공/실패, 지연시간, 토큰 수** 기록
- [ ] 태스크별 **총 비용** 자동 계산 및 대시보드 표시
- [ ] **이상 탐지 알림**: 평균 대비 3x 이상 토큰 소비 시 알림
- [ ] 주간 **Trajectory 분석** 리뷰: 비효율적 경로 패턴 식별
- [ ] A/B 테스트: 프롬프트/모델 변경의 영향을 정량적으로 측정

---

## 4. Agent Memory 아키텍처

Agent의 "기억"은 사용자 경험과 태스크 품질을 결정하는 핵심 요소입니다. 2025년에는 단순한 대화 히스토리를 넘어, **구조화된 장기 기억과 집단 기억** 이 중요해지고 있습니다.

### 4.1 메모리 유형 분류

| 유형 | 저장 위치 | 수명 | 용도 | 비유 |
|------|----------|------|------|------|
| **단기 기억 (Short-term)** | 컨텍스트 윈도우 | 세션 내 | 현재 대화 맥락 유지 | 작업 기억 (Working Memory) |
| ** 장기 기억 (Long-term)** | 벡터 DB / 관계형 DB | 영구 | 사용자 선호, 과거 상호작용 | 장기 기억 (Long-term Memory) |
| ** 공유/집단 기억 (Shared)** | 공유 저장소 | 영구 | Agent 간 지식 공유 | 조직의 공유 지식 (Institutional Knowledge) |

### 4.2 단기 기억 -- 컨텍스트 윈도우 관리

컨텍스트 윈도우는 유한합니다. 대화가 길어지면 초기 맥락이 잘려나가면서 Agent의 성능이 저하됩니다.

** 최적화 전략**:

| 전략 | 설명 | 적용 시점 |
|------|------|----------|
| **Sliding Window** | 최근 N 턴만 유지 | 범용적. 단순하지만 효과적 |
| ** 요약 압축 (Summarization)** | 이전 대화를 요약하여 축소 | 장기 대화. 비용 절감 |
| ** 선택적 망각 (Selective Forgetting)** | 중요도 낮은 턴 제거 | 토큰 제약이 심한 경우 |
| ** 스코핑 (Scoping)** | 태스크에 관련된 컨텍스트만 포함 | 멀티에이전트 핸드오프 시 |

### 4.3 장기 기억 -- 벡터 DB + 구조화 검색

** 하이브리드 검색 (Hybrid Retrieval)**이 2025년의 표준 패턴입니다.

```
┌─────────────────────────────────────────────┐
│              메모리 검색 요청                    │
├───────────────────┬─────────────────────────┤
│  벡터 검색 (Semantic)│  구조화 검색 (Structured)   │
│  "비슷한 맥락 찾기"   │  "user_id=123 AND        │
│                    │   topic='billing'"       │
├───────────────────┴─────────────────────────┤
│            결과 통합 (RRF / 가중 합산)            │
└─────────────────────────────────────────────┘
```

** 벡터 검색만으로는 부족한 이유**:
- "지난주 화요일에 논의한 예산 건" → ** 시간 필터링**필요
- "김 과장과의 대화에서 언급된 API 키" → ** 메타데이터 필터링**필요
- 의미적 유사도만으로는 ** 정확한 사실(fact)**검색이 어려움

### 4.4 기술 스택 비교

| 기술 | 유형 | 강점 | Databricks 통합 |
|------|------|------|-----------------|
| **Databricks Vector Search** | 벡터 DB (관리형) | Unity Catalog 네이티브. Delta 자동 동기화 | 네이티브 |
| **pgvector** | PostgreSQL 확장 | 기존 PostgreSQL 인프라 활용 | 외부 연동 |
| **Redis** | 인메모리 | 초저지연. 세션 기반 단기 기억에 최적 | 외부 연동 |
| **Azure Cosmos DB** | 멀티모델 DB | 글로벌 분산. 벡터 + 문서 + 그래프 | Azure 네이티브 |
| **Bedrock AgentCore Memory** | 관리형 | AWS Agent 생태계 통합 | 외부 연동 |

{% hint style="info" %}
**Databricks 고객 권장**: **Databricks Vector Search** 를 장기 기억의 핵심 저장소로 사용하세요. Delta 테이블과 자동 동기화되므로, 기존 데이터 파이프라인에 자연스럽게 통합됩니다. 구조화 검색은 Unity Catalog의 SQL 인터페이스를 활용하여 하이브리드 검색을 구현할 수 있습니다.
{% endhint %}

### 4.5 공유 기억 (Shared/Collective Memory) 패턴

멀티에이전트 시스템에서 각 Agent가 학습한 지식을 **다른 Agent와 공유** 하는 패턴입니다.

**구현 패턴**:

| 패턴 | 설명 | 예시 |
|------|------|------|
| ** 중앙 지식 저장소** | 모든 Agent가 읽기/쓰기하는 공유 DB | FAQ DB: CS Agent가 답변한 내용을 다른 Agent도 참조 |
| ** 이벤트 기반 동기화** | Agent의 학습 결과를 이벤트로 발행 | Agent A가 새로운 패턴 발견 → 이벤트 발행 → Agent B가 구독 |
| **Consolidation** | 주기적으로 개별 기억을 통합/정제 | 매일 밤 배치로 Agent별 기억을 병합하고 중복 제거 |

### 4.6 메모리 설계 반패턴 (Anti-patterns)

| 반패턴 | 문제점 | 해결책 |
|--------|--------|--------|
| ** 무한 축적** | 벡터 DB 크기 무한 증가, 검색 성능 저하 | TTL 설정, 주기적 정리 |
| ** 비구조적 저장** | "모든 것을 벡터로" → 정확한 사실 검색 실패 | 구조화 메타데이터 + 벡터 하이브리드 |
| **Agent 간 기억 격리** | 같은 사용자에 대해 Agent마다 다른 기억 | 공유 사용자 프로필 저장소 |
| ** 과도한 컨텍스트 주입** | 기억을 너무 많이 컨텍스트에 넣어 성능 저하 | Top-K 제한, 관련성 임계값 |

---

## 5. Agent 안전성 & 거버넌스

멀티에이전트 시스템은 ** 자율적으로 도구를 호출하고, 데이터에 접근하며, 다른 Agent와 협업**합니다. 이는 기존 소프트웨어와는 차원이 다른 보안/거버넌스 과제를 제기합니다.

### 5.1 Forrester AEGIS 프레임워크

Forrester Research가 2025년 발표한 **AEGIS (Agentic Enterprise Governance and Intelligence Standards)** 프레임워크는 엔터프라이즈 Agent 거버넌스의 표준 참조 모델입니다.

**AEGIS의 5대 축**:

| 축 | 영문 | 핵심 질문 |
|----|------|----------|
| ** 인증/권한** | Authorization | Agent가 무엇을 할 수 있는가? |
| ** 감사** | Audit | Agent가 무엇을 했는가? |
| ** 격리** | Isolation | Agent의 영향 범위를 제한할 수 있는가? |
| ** 품질** | Quality | Agent의 출력을 신뢰할 수 있는가? |
| ** 사람 개입** | Human Oversight | 언제 사람이 개입해야 하는가? |

### 5.2 Zero Trust for Agents

기존 Zero Trust 보안 모델을 Agent에 적용합니다. "** 어떤 Agent도 기본적으로 신뢰하지 않는다**"는 원칙입니다.

| 원칙 | Agent 적용 |
|------|-----------|
| ** 최소 권한** | Agent는 태스크에 필요한 최소한의 도구/데이터에만 접근 |
| ** 지속적 검증** | 매 Tool Call마다 권한 재검증 |
| ** 세그멘테이션** | Agent 간 네트워크/데이터 격리 |
| ** 암호화** | Agent 간 통신 암호화 (MCP/A2A 모두 TLS) |
| ** 모니터링** | 모든 Agent 활동 실시간 감시 |

### 5.3 Risk-Tiered HITL (Human-In-The-Loop)

모든 Agent 행동에 사람이 개입하면 Agent의 의미가 없고, 모든 행동을 자율에 맡기면 위험합니다. ** 리스크 기반 3단계 HITL**모델을 적용합니다.

| 등급 | 이름 | 인간 개입 | 예시 |
|------|------|----------|------|
| **Tier 1** | Autonomous | 개입 없음. 사후 감사만 | 정보 조회, FAQ 답변, 데이터 조회 |
| **Tier 2** | Step-up | 특정 조건 충족 시 승인 요청 | 데이터 수정, 비용 발생 API 호출, 외부 시스템 연동 |
| **Tier 3** | Prohibited | Agent 실행 금지. 반드시 인간이 수행 | PII 삭제, 금융 거래, 인사 결정, 법적 결정 |

{% hint style="warning" %}
** 핵심 원칙**: Tier 분류는 "** 되돌릴 수 있는가(reversibility)**"를 기준으로 합니다. 되돌릴 수 있는 행동은 Tier 1~2, 되돌릴 수 없는 행동은 반드시 Tier 2~3으로 분류하세요.
{% endhint %}

### 5.4 권한 부여 모델 비교

| 모델 | 설명 | 적합 시나리오 |
|------|------|-------------|
| **RBAC**(Role-Based) | 역할 기반 권한. "CS Agent는 고객 정보 읽기 가능" | 역할이 고정된 시스템 |
| **ABAC**(Attribute-Based) | 속성 기반 동적 권한. "근무시간 + 부서 + 데이터 분류 등급" 조합 | 복잡한 규칙 기반 시스템 |
| **IBAC**(Intent-Based) | 의도 기반 권한. Agent의 의도를 분석하여 동적 권한 부여 | 차세대 Agent 보안. 2025년 신규 개념 |

**IBAC 예시**:
- Agent가 "고객 전화번호 조회" 의도 → 허용
- Agent가 "고객 전화번호를 외부 API로 전송" 의도 → 차단 (데이터 유출 위험)
- 동일한 데이터 접근이지만, ** 의도에 따라 권한이 달라짐**

### 5.5 전체 감사 추적 (Full Audit Trail)

** 필수 기록 항목**:

| 항목 | 설명 |
|------|------|
| `timestamp` | 행동 발생 시각 (밀리초 단위) |
| `agent_id` | 행동 주체 Agent 식별자 |
| `action_type` | tool_call, llm_inference, handoff, human_escalation |
| `input` | 입력 데이터 (PII 마스킹 적용) |
| `output` | 출력 데이터 (PII 마스킹 적용) |
| `decision_rationale` | Agent가 이 행동을 선택한 이유 (Chain of Thought) |
| `authorization_check` | 권한 검증 결과 |
| `token_usage` | 해당 행동의 토큰 소비 |
| `latency_ms` | 행동 소요 시간 |

{% hint style="info" %}
**Databricks 장점**: Unity Catalog의 ** 감사 로그(Audit Log)**와 ** 데이터 계보(Lineage)**기능을 Agent 거버넌스에 활용할 수 있습니다. Agent가 어떤 테이블에 접근했는지, 어떤 쿼리를 실행했는지가 자동으로 추적됩니다.
{% endhint %}

---

## 6. 시장 동향 & 전망

### 6.1 시장 규모

| 지표 | 수치 |
|------|------|
| **2025년 시장 규모** | $7.6B (약 10조원) |
| **2030년 예상** | $52B ~ $100B (기관별 편차) |
| **CAGR** | 약 46% |
| ** 임원 88%** | AI 예산 증가 계획 |

### 6.2 Gartner 예측

| 시점 | 예측 |
|------|------|
| **2026년** | 엔터프라이즈 애플리케이션의 **40%** 가 Agentic AI 포함 |
| **2028년** | 소프트웨어의 **33%** 가 Agent 컴포넌트 포함 |

### 6.3 "Agentic AI" vs "AI Agent" -- 용어의 차이

| 용어 | 의미 | 범위 |
|------|------|------|
| **Agentic AI** | 자율적으로 목표를 달성하는 **AI 시스템 전체** | 시스템, 아키텍처, 패러다임 |
| **AI Agent** | Agentic AI를 구성하는 ** 개별 컴포넌트** | 단일 Agent, 실행 단위 |

이 구분이 중요한 이유: 고객과 대화할 때 "AI Agent를 도입하겠다"와 "Agentic AI로 전환하겠다"는 전혀 다른 수준의 프로젝트입니다. 전자는 챗봇 하나를 만드는 것이고, 후자는 조직의 업무 프로세스를 AI 중심으로 재설계하는 것입니다.

### 6.4 산업별 채택 현황

| 산업 | 주요 유스케이스 | 성숙도 |
|------|--------------|--------|
| ** 금융** | 리스크 분석, 규정 준수 모니터링, 고객 상담 자동화 | 높음 |
| ** 제조** | 예지보전, 품질 관리, 공급망 최적화 | 중간 |
| ** 헬스케어** | 임상 문서 자동화, 약물 상호작용 분석 | 초기 |
| ** 리테일** | 개인화 추천, 재고 관리, CS 자동화 | 중간 |
| ** 공공** | 민원 처리, 정책 분석, 문서 관리 | 초기 |

---

## 7. Vibe Coding & Agentic Engineering

### 7.1 Vibe Coding이란?

**Vibe Coding** 은 2025년 2월 Andrej Karpathy (OpenAI 공동 창립자, 전 Tesla AI 디렉터)가 제안한 개념으로, "**코드를 직접 작성하지 않고 AI와의 대화로 소프트웨어를 만드는**" 새로운 프로그래밍 패러다임입니다.

> "I just see stuff, say stuff, run stuff, and copy paste stuff, and it mostly works." -- Andrej Karpathy

### 7.2 주요 도구 생태계

| 도구 | 유형 | 특징 | 채택 현황 |
|------|------|------|----------|
| **Claude Code** | CLI Agent | 터미널 네이티브. MCP 통합. 코드베이스 전체 이해 | **"가장 사랑받는 도구" 46%**(LangSmith 조사) |
| **Cursor** | IDE | AI-first IDE. Tab 자동완성 + Agent Mode | 개발자 인기 1위 AI IDE |
| **GitHub Copilot** | IDE 플러그인 | Agent Mode (2025). 멀티파일 편집. PR 자동 생성 | 가장 넓은 설치 기반 |
| **Windsurf** | IDE | Cascade 기능. 컨텍스트 연속성 | 빠른 성장 |
| **Replit Agent** | 클라우드 IDE | 완전 자동 배포. 비개발자 대상 | 교육/프로토타이핑 |

### 7.3 생산성 논쟁 -- 체감 vs 실제

{% hint style="warning" %}
** 주목할 연구 결과**: METR(Model Evaluation and Threat Research)의 2025년 연구에 따르면, 숙련된 오픈소스 개발자들이 AI 코딩 도구를 사용했을 때 ** 체감 생산성은 20% 향상**되었지만, ** 실제 작업 완료 시간은 19% 더 길었습니다**. 이 역설적 결과는 다음을 시사합니다:

1. ** 코드 리뷰 시간 증가**: AI가 생성한 코드를 검증하는 데 추가 시간 소요
2. ** 맥락 전환 비용**: AI와의 대화 ↔ 코드 검토를 오가는 오버헤드
3. ** 과도한 위임**: AI에 맡기는 것이 나을 것 같지만, 결국 수정이 필요한 경우
{% endhint %}

** 그러나**이것이 Vibe Coding의 무용론을 의미하지는 않습니다. 해당 연구는 "이미 익숙한 코드베이스에서 숙련 개발자가 사용한 경우"의 결과이며, 다음 경우에는 생산성이 확실히 향상됩니다:

- ** 새로운 기술 스택**학습 시 (보일러플레이트 생성)
- ** 프로토타이핑**단계 (아이디어 → 동작하는 코드)
- ** 문서화, 테스트 작성**(반복적 작업)
- ** 비개발자**의 코딩 접근성 확대

### 7.4 Vibe Coding에서 Agentic Engineering으로

2025년 하반기, Vibe Coding의 한계가 드러나면서 **Agentic Engineering** 이라는 더 성숙한 개념으로 진화하고 있습니다.

| 비교 | Vibe Coding | Agentic Engineering |
|------|------------|-------------------|
| **접근 방식** | "AI에게 말하면 코드가 나온다" | "AI Agent를 체계적으로 엔지니어링한다" |
| ** 품질 보증** | 수동 검토에 의존 | 자동화된 테스트, CI/CD 통합 |
| ** 거버넌스** | 없음 | 코드 리뷰 Agent, 보안 스캔 Agent |
| ** 확장성** | 개인 생산성 도구 | 팀/조직 수준의 개발 프로세스 |
| ** 대상** | 개인 개발자, 프로토타이핑 | 엔터프라이즈 소프트웨어 개발 |

{% hint style="info" %}
**Databricks에서의 Vibe Coding**: Databricks 환경에서는 **Genie Code**(자연어 → SQL/Python), **AI Dev Kit**(Builder App 개발), **MCP 연동 Claude Code/Cursor**(Databricks 리소스 접근)가 Vibe Coding을 지원합니다. 특히 데이터 엔지니어가 SQL만 알아도 Python UDF를 작성하거나, 비즈니스 분석가가 대시보드 자동 생성을 할 수 있게 합니다.
{% endhint %}

---

## 8. Databricks 포지셔닝

Databricks는 "Agent를 만드는 프레임워크"가 아닌, "**Agent를 엔터프라이즈에서 안전하게 운영하는 플랫폼**"으로 포지셔닝합니다. 이 차이가 중요합니다.

### 8.1 Databricks Agent 스택

```
┌───────────────────────────────────────────────────────────┐
│                    사용자 인터페이스                          │
│         Genie Space / Genie Code / Databricks Apps          │
├───────────────────────────────────────────────────────────┤
│                   Agent Bricks (No-Code)                    │
│     Knowledge Assistant │ Genie Agent │ Supervisor Agent    │
├───────────────────────────────────────────────────────────┤
│              Agent Framework (Pro-Code)                     │
│        LangGraph / OpenAI SDK / 커스텀 Agent 코드            │
│              + MLflow Tracing 자동 추적                      │
├───────────────────────────────────────────────────────────┤
│                AI Dev Kit (Builder App)                     │
│           로컬 개발 → Databricks Apps 배포                    │
├───────────────────────────────────────────────────────────┤
│                 Foundation Layer                            │
│   Unity Catalog │ Vector Search │ Model Serving │ MCP       │
│         Mosaic AI Gateway │ Lakehouse Monitoring             │
└───────────────────────────────────────────────────────────┘
```

### 8.2 경쟁 플랫폼 대비 Databricks 강점

| 비교 축 | Databricks | AWS Bedrock | Azure AI Studio | Google Vertex AI |
|---------|-----------|-------------|-----------------|-----------------|
| ** 데이터 거버넌스** | Unity Catalog (통합) | IAM + Glue (분산) | Purview (별도) | Dataplex (별도) |
| **Agent 추적** | MLflow Tracing (내장) | CloudWatch (범용) | App Insights (범용) | Cloud Trace (범용) |
| **No-Code Agent** | Agent Bricks | Bedrock Agents | AI Studio Agents | Agent Builder |
| **Pro-Code 자유도** | LangGraph, OpenAI 등 자유 선택 | Bedrock 종속적 | Semantic Kernel 중심 | ADK + Vertex |
| ** 멀티클라우드** | AWS, Azure, GCP 모두 지원 | AWS 전용 | Azure 전용 | GCP 전용 |
| ** 데이터와의 거리** | 제로 (Lakehouse 위에 Agent) | ETL 필요 | ETL 필요 | ETL 필요 |

{% hint style="success" %}
** 핵심 차별점**: Databricks의 가장 큰 강점은 "**Agent가 데이터 바로 위에 앉는다**"는 것입니다. 다른 플랫폼에서는 Agent가 데이터를 가져오기 위해 ETL 파이프라인을 거쳐야 하지만, Databricks에서는 Agent가 Unity Catalog를 통해 ** 원본 데이터에 직접 접근**하며, 동일한 거버넌스 정책이 적용됩니다.
{% endhint %}

### 8.3 구현 시나리오별 권장 아키텍처

| 시나리오 | 권장 스택 | 이유 |
|---------|---------|------|
| ** 사내 Q&A 봇** | Agent Bricks (Knowledge Assistant) | No-Code, 빠른 배포, RAG 자동 구성 |
| ** 데이터 질의 Agent** | Agent Bricks (Genie Agent) | Genie Space + 자연어 SQL |
| ** 멀티도메인 포탈** | Agent Bricks (Supervisor) + 전문 Agent들 | Supervisor 패턴. No-Code 구성 |
| ** 커스텀 워크플로** | LangGraph + Databricks Agent Framework | 복잡한 분기/루프. Pro-Code 필요 |
| ** 외부 서비스 연동 앱** | AI Dev Kit (Builder App) → Databricks Apps 배포 | 로컬 개발 + 원클릭 배포 |
| ** 대규모 배치 Agent** | Databricks Jobs + Model Serving | 스케줄링, 재시도, 모니터링 |

---

## 9. 고객 FAQ

### Q1. "멀티에이전트가 단일 Agent보다 항상 좋은가요?"

아닙니다. 멀티에이전트는 ** 복잡성 비용**이 있습니다. 다음 기준으로 판단하세요:

| 기준 | 단일 Agent 적합 | 멀티에이전트 적합 |
|------|----------------|-----------------|
| 도메인 수 | 1~2개 | 3개 이상 |
| 도구 수 | 5개 이하 | 10개 이상 |
| 프로세스 복잡도 | 선형 | 분기/병렬 필요 |
| 전문성 요구 | 범용 | 도메인별 전문 프롬프트 필요 |
| 장애 격리 | 전체 재시도 가능 | 부분 실패 허용 필요 |

### Q2. "MCP 도입은 지금 해야 하나요, 더 기다려야 하나요?"

** 지금 하세요.**MCP는 이미 사실상 표준(de facto standard)입니다. 9,700만+ 다운로드가 이를 증명합니다. 기다릴 이유가 없습니다. Databricks MCP Server도 공식 지원되고 있으므로, 기존 Databricks 환경에 바로 연동 가능합니다.

### Q3. "Agent의 비용을 어떻게 관리하나요?"

1. ** 라우팅 최적화**: Supervisor에서 소형 모델 사용 (GPT-4o-mini, DBRX)
2. ** 캐싱**: 반복적인 Tool Call 결과 캐싱
3. ** 토큰 예산**: Agent별 토큰 상한선 설정
4. **Trajectory 분석**: 불필요한 Tool Call 패턴 식별 및 제거
5. ** 모니터링**: MLflow Tracing으로 실시간 비용 추적

### Q4. "Agent 보안이 걱정됩니다. 어떻게 시작해야 하나요?"

단계적 접근을 권장합니다:

1. **1단계**: 읽기 전용 Agent부터 시작 (정보 조회, FAQ)
2. **2단계**: Risk-Tiered HITL 적용 (Tier 1만 자동화)
3. **3단계**: RBAC 기반 Agent 권한 체계 구축
4. **4단계**: 감사 로그 + 이상 탐지 구축
5. **5단계**: 점진적으로 Tier 2 자동화 범위 확대

### Q5. "A2A가 MCP를 대체하나요?"

아닙니다. ** 역할이 다릅니다.**MCP는 Agent → Tool (USB 포트), A2A는 Agent ↔ Agent (HTTP 프로토콜)입니다. 둘은 상호보완적이며, 성숙한 멀티에이전트 시스템에서는 둘 다 필요합니다.

### Q6. "Databricks 없이 멀티에이전트를 구축할 수 있나요?"

기술적으로 가능합니다. 하지만 다음을 직접 구축해야 합니다:
- 데이터 거버넌스 (Unity Catalog 대체)
- Agent 추적 (MLflow Tracing 대체)
- 벡터 검색 인프라 (Vector Search 대체)
- 모델 서빙 인프라 (Model Serving 대체)
- 배포 인프라 (Databricks Apps 대체)

이 모든 것을 조합하면 **6~12개월의 추가 인프라 구축 시간** 이 필요합니다.

---

## 10. 참고 자료

### 프로토콜 & 표준
- [Anthropic MCP 공식 문서](https://modelcontextprotocol.io/)
- [Google A2A 프로토콜](https://google.github.io/A2A/)
- [AAIF (Linux Foundation)](https://www.linuxfoundation.org/press/linux-foundation-launches-agentic-ai-forum)

### 프레임워크
- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [CrewAI 공식 문서](https://docs.crewai.com/)
- [AutoGen (Microsoft)](https://microsoft.github.io/autogen/)
- [AWS Strands](https://strandsagents.com/)
- [Google Agent Development Kit](https://google.github.io/adk-docs/)

### 관측성
- [MLflow Tracing](https://mlflow.org/docs/latest/llms/tracing/index.html)
- [LangSmith](https://docs.smith.langchain.com/)
- [Arize Phoenix](https://docs.arize.com/phoenix)

### Databricks
- [Databricks Agent Bricks](https://docs.databricks.com/en/generative-ai/agent-bricks/index.html)
- [Databricks AI Dev Kit](https://docs.databricks.com/en/dev-tools/ai-dev-kit.html)
- [Databricks MCP Server](https://docs.databricks.com/en/dev-tools/mcp.html)

### 시장 분석
- Gartner, "Predicts 2025: Agentic AI" (2024)
- Forrester, "The AEGIS Framework for Agentic AI Governance" (2025)
- McKinsey, "The State of AI in 2025" (2025)

### Vibe Coding
- Andrej Karpathy, "Vibe Coding" (2025.02)
- METR, "Measuring the Impact of AI Coding Tools on Developer Productivity" (2025)
- LangSmith, "State of AI Coding Tools" (2025)

---

{% hint style="info" %}
**이 문서는 2025년 Q1 기준으로 작성되었습니다.**Agentic AI 분야는 매우 빠르게 변화하고 있으므로, 분기별 업데이트를 권장합니다. 최신 정보는 [Databricks 블로그](https://www.databricks.com/blog)와 [AAIF 공지](https://www.linuxfoundation.org/press)를 참조하세요.
{% endhint %}
