# Multi-Agent 패턴

[← AI Agent 아키텍처 개요](README.md)

---

## Single Agent vs Multi-Agent

### Single Agent

하나의 LLM이 모든 도구와 추론을 담당합니다.

- **장점**: 단순, 디버깅 쉬움, 지연시간 낮음
- **단점**: 복잡한 작업에서 정확도 저하, 도구 수 제한 (보통 10~15개 이상이면 성능 저하)
- **적합**: FAQ 봇, 문서 검색, 단순 데이터 조회

### Multi-Agent

여러 전문 Agent가 협업하여 복잡한 작업을 수행합니다.

- **장점**: 역할 분담으로 정확도 향상, 확장 가능
- **단점**: 복잡도 증가, 에이전트 간 통신 오버헤드, 디버깅 난이도 상승
- **적합**: 복합 분석, 크로스 도메인 질의, 자동화 워크플로우

---

## Multi-Agent 아키텍처 패턴

### 패턴 비교 요약

| 항목 | Supervisor 패턴 | Swarm 패턴 | 계층형 패턴 |
|------|----------------|------------|------------|
| **구조**| 중앙 컨트롤러가 분배 | 에이전트 간 직접 핸드오프 | 다계층 Supervisor 트리 |
| **의사결정**| Supervisor가 결정 | 각 Agent가 자율 결정 | 각 레벨 Supervisor가 결정 |
| **확장성**| Worker 추가 용이 | 에이전트 추가 용이 | 팀 단위 확장 |
| **디버깅**| 중앙 로그로 추적 용이 | 핸드오프 추적 필요 | 계층별 추적 |
| **적합 시나리오**| 5~10개 Worker | 순차적 전문가 릴레이 | 대규모 조직 (팀별 에이전트) |
| **대표 구현**| Databricks Agent Bricks | OpenAI Agents SDK Handoff | LangGraph 중첩 그래프 |

### 1. Supervisor 패턴

```
         사용자 요청
              │
       ┌──────▼──────┐
       │  Supervisor  │ ← 작업 분석, 분배, 결과 종합
       │   Agent      │
       └──┬───┬───┬───┘
          │   │   │
     ┌────▼┐ ┌▼───┐ ┌▼────┐
     │검색  │ │SQL │ │요약  │
     │Agent│ │Agent│ │Agent│
     └─────┘ └────┘ └─────┘
```

Supervisor가 사용자 요청을 분석하고, 적합한 Worker에게 하위 작업을 위임합니다. Databricks Agent Bricks의 Supervisor Agent가 이 패턴을 사용합니다.

### 2. Swarm 패턴

```
사용자 요청 → [접수 Agent] ──handoff──→ [분석 Agent] ──handoff──→ [보고서 Agent] → 최종 응답
                                              │
                                         (필요시)
                                              │
                                        [데이터 Agent]
```

중앙 관리자 없이 Agent들이 **Handoff**방식으로 작업을 전달합니다.

- Agent A가 작업 중 자신의 범위를 벗어나면 Agent B에게 전달
- 각 Agent가 자율적으로 다음 Agent를 결정
- OpenAI Agents SDK의 Handoff가 이 패턴의 대표 구현

### 3. 계층형 패턴

```
              ┌─────────────┐
              │ Top-level   │
              │ Supervisor  │
              └──┬───────┬──┘
          ┌──────▼──┐  ┌─▼────────┐
          │ 데이터팀 │  │ 보고서팀  │
          │ Sub-Sup │  │ Sub-Sup  │
          └──┬───┬──┘  └──┬───┬───┘
          ┌──▼┐ ┌▼──┐  ┌──▼┐ ┌▼──┐
          │SQL│ │ETL│  │차트│ │문서│
          └───┘ └───┘  └───┘ └───┘
```

Supervisor 패턴을 다층으로 확장하여, Sub-Supervisor가 하위 Agent 그룹을 관리합니다. 대규모 조직에서 팀별 전문 에이전트 그룹을 구성할 때 적합합니다.

---

## 언제 Single Agent로 충분한가?

Multi-Agent를 도입하기 전에 아래 체크리스트를 확인하세요. **모두 "예"라면 Single Agent로 충분합니다.**

- [ ] 도구 수가 15개 미만인가?
- [ ] 단일 도메인(예: 고객 지원만, 데이터 분석만)인가?
- [ ] 평균 대화 턴이 5턴 이하인가?
- [ ] 병렬 실행이 필요한 독립 작업이 없는가?
- [ ] 서로 다른 LLM 모델이나 설정이 필요한 하위 작업이 없는가?

{% hint style="info" %}
**실전 경험 법칙**: 고객 PoC의 80% 이상은 Single Agent로 충분합니다. Multi-Agent를 너무 일찍 도입하면 개발 기간이 3배 이상 늘어나고, 디버깅 비용이 기하급수적으로 증가합니다.
{% endhint %}

---

## Multi-Agent 통신 패턴 심화

Multi-Agent 시스템에서 에이전트 간 정보를 주고받는 방식은 크게 3가지입니다.

| 통신 패턴 | 구조 | 장점 | 단점 | 구현 복잡도 |
|-----------|------|------|------|------------|
| **공유 메모리 (Blackboard)**| 모든 Agent가 공유 상태(State)를 읽고 씀 | 구현 단순, 전체 상태 파악 용이 | 동시 쓰기 충돌, 상태 비대화 | 낮음 |
| **메시지 패싱 (Queue)**| Agent 간 비동기 메시지 교환 | 느슨한 결합, 확장 용이 | 메시지 순서 보장 어려움, 디버깅 복잡 | 중간 |
| **직접 호출 (Function Call)**| Agent A가 Agent B를 함수처럼 호출 | 명확한 인터페이스, 동기 실행 | 강한 결합, 호출 체인 깊어질 수 있음 | 낮음~중간 |

**Databricks 환경에서의 권장 패턴**: Agent Bricks의 Supervisor Agent는 **직접 호출**패턴을 사용합니다. Supervisor가 Worker Agent를 함수처럼 호출하고 결과를 받는 구조로, 가장 직관적이고 MLflow Tracing과의 호환성도 좋습니다.

---

## Multi-Agent 디버깅의 현실

Multi-Agent 시스템의 디버깅은 Single Agent와 차원이 다릅니다. 아래는 실전에서 자주 만나는 문제와 대응 전략입니다.

### 1. 비결정적 행동 (Non-deterministic Behavior)

같은 입력에도 Agent A가 Agent B를 호출할 때도 있고, Agent C를 호출할 때도 있습니다. 원인은 LLM의 temperature, 컨텍스트의 미묘한 차이 등입니다.

- **대응**: MLflow Tracing으로 모든 실행을 기록하고, 실패 케이스의 Trace를 수집하여 패턴을 분석합니다. temperature=0으로 설정하면 재현성이 높아지지만 다양성은 줄어듭니다.

### 2. 에이전트 간 핑퐁 (Agent Ping-Pong)

Agent A가 "이건 B의 영역이야"라며 B에게 넘기고, B가 "이건 A의 영역이야"라며 다시 A에게 넘기는 무한 루프입니다.

- **대응**: 각 Agent의 역할 경계를 명확히 정의하고, **handoff 횟수에 제한**을 두세요. "같은 Agent에게 2회 이상 핸드오프 금지" 규칙이 효과적입니다.

### 3. 상태 불일치 (State Inconsistency)

Agent A가 DB를 업데이트한 후 Agent B에게 넘겼는데, B가 업데이트 전 캐시된 데이터를 참조하는 문제입니다.

- **대응**: 공유 상태를 사용하되, 각 Agent가 도구 호출 시 항상 최신 데이터를 조회하도록 설계합니다. 캐시 사용 시 TTL(Time-to-Live)을 짧게 설정하세요.

{% hint style="warning" %}
**MLflow Tracing 필수**: Multi-Agent 시스템에서 Tracing 없이 디버깅하는 것은 불가능에 가깝습니다. 각 Agent의 입출력, Tool Call, LLM 추론을 모두 기록해야 문제의 근본 원인을 파악할 수 있습니다.
{% endhint %}

---

## Multi-Agent 비용 폭발 주의

Multi-Agent의 가장 과소평가되는 리스크는 **비용**입니다.

```
사용자 질문 1회
  → Supervisor LLM 호출 (1회)
    → Agent A LLM 호출 (1회) + Tool Call (2회) + 결과 해석 LLM (1회)
    → Agent B LLM 호출 (1회) + Tool Call (3회) + 결과 해석 LLM (1회)
  → Supervisor 결과 종합 LLM 호출 (1회)
= 총 LLM 호출 6회, Tool Call 5회
```

사용자 입장에서는 "질문 1개"지만, 내부적으로는 6회의 LLM 호출이 발생합니다. Agent 수가 늘어나면 이 비용은 기하급수적으로 증가합니다.

| 구조 | 평균 LLM 호출/질문 | 예상 비용 (GPT-4o 기준) |
|------|-------------------|----------------------|
| Single Agent | 2~3회 | $0.01~0.03 |
| 2-Agent Supervisor | 5~7회 | $0.03~0.07 |
| 3-Agent Supervisor | 8~12회 | $0.05~0.15 |
| 계층형 (5+ Agent) | 15~25회 | $0.10~0.30 |

**비용 제어 전략**:
1. **토큰 예산 설정**: 요청당 최대 토큰 사용량을 설정하고, 초과 시 가장 비용 효율적인 경로로 우회
2. **캐싱**: 자주 반복되는 도구 호출 결과를 캐싱하여 LLM 호출 횟수 절감
3. **라우팅 최적화**: Supervisor의 라우팅 정확도를 높여 불필요한 Agent 호출 방지
4. **모델 혼합**: Supervisor는 고성능 모델(GPT-4o), Worker는 경량 모델(GPT-4o-mini)로 비용 절감

---

[다음: Agent 프레임워크 비교 →](frameworks.md)
