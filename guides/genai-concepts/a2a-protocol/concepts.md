# 핵심 개념

## 1. Agent Card (에이전트 자기소개)

각 Agent는 자신의 능력, 입력/출력 형식, 엔드포인트를 JSON 형태로 공개합니다. 다른 Agent가 이 카드를 읽고 협업 대상을 선택합니다.

**게시 위치**: `/.well-known/agent.json`

**Agent Card JSON 예시**:

```json
{
  "name": "항공권 예약 에이전트",
  "description": "국내외 항공권 검색 및 예약을 처리합니다",
  "url": "https://flights.example.com/a2a",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true
  },
  "skills": [
    {
      "id": "search_flights",
      "name": "항공편 검색",
      "description": "출발지, 도착지, 날짜로 항공편을 검색합니다",
      "inputModes": ["text/plain", "application/json"],
      "outputModes": ["application/json"]
    },
    {
      "id": "book_flight",
      "name": "항공편 예약",
      "description": "선택한 항공편을 예약합니다",
      "inputModes": ["application/json"],
      "outputModes": ["application/json"]
    }
  ],
  "authentication": {
    "schemes": ["OAuth2"]
  }
}
```

| 필드 | 설명 |
|------|------|
| `name` | Agent 이름 — 사람과 다른 Agent가 읽을 수 있는 이름 |
| `description` | 능력 설명 — 어떤 작업을 할 수 있는지 |
| `url` | A2A 엔드포인트 — 작업 요청을 보낼 주소 |
| `capabilities` | 지원 기능 — 스트리밍, 푸시 알림 등 |
| `skills` | 수행 가능한 작업 목록 — 각 스킬의 입출력 형식 포함 |
| `authentication` | 인증 방식 — OAuth2, API Key 등 |

### Agent Card 설계 베스트 프랙티스

Agent Card는 사람만 읽는 것이 아닙니다. ** 다른 Agent의 LLM이 읽고 판단**합니다. 따라서 설계 시 LLM 친화적인 작성이 중요합니다.

**1. `description`은 구체적이고 명확하게**

```json
// 나쁜 예 — LLM이 언제 이 Agent를 선택해야 하는지 판단 불가
"description": "데이터 관련 작업을 처리합니다"

// 좋은 예 — 범위와 능력이 명확
"description": "Databricks SQL Warehouse에 연결하여 자연어 질문을 SQL로 변환하고 실행합니다. 집계, 필터링, 조인을 포함한 분석 쿼리를 처리하며, 결과를 표 또는 차트 JSON으로 반환합니다."
```

**2. `skills`는 가능한 좁게 정의**

| skills 설계 | 장점 | 단점 |
|-------------|------|------|
| 넓은 범위 (예: "데이터 분석") | 유연함 | LLM이 적합한 Agent를 잘못 선택할 확률 높음 |
| 좁은 범위 (예: "SQL 기반 매출 분석") | 선택 정확도 높음 | Agent가 많아질 수 있음 |

경험적으로 **skill당 하나의 명확한 작업** 을 정의하는 것이 가장 좋습니다. "이 skill이 정확히 무엇을 하는지" 한 문장으로 설명할 수 없다면, 더 쪼개야 합니다.

**3. `inputModes`/`outputModes`를 정확히 명시**

```json
// 이미지를 입력받아 분석하는 Agent라면 반드시 명시
"inputModes": ["text/plain", "image/png", "image/jpeg"],
"outputModes": ["application/json", "text/markdown"]
```

입출력 형식이 부정확하면 런타임에 파싱 에러가 발생합니다. 특히 `application/json`을 출력하는 경우, 반환되는 JSON 스키마를 description에 설명하는 것을 권장합니다.

### Agent Card 버전 관리

Agent의 능력은 시간이 지나면 변합니다. 새로운 skill이 추가되거나, 기존 skill의 입출력이 바뀔 수 있습니다. **SemVer(Semantic Versioning)** 를 적용하여 하위 호환성을 관리하세요.

| 변경 유형 | 버전 변경 | 예시 |
|-----------|----------|------|
| 새 skill 추가 | Minor (1.0 → 1.1) | `analyze_trend` skill 추가 |
| 기존 skill 입출력 변경 | Major (1.x → 2.0) | `search_flights`의 응답 스키마 변경 |
| 설명/메타데이터만 변경 | Patch (1.0.0 → 1.0.1) | description 오타 수정 |

{% hint style="warning" %}
**Breaking Change 주의**: 기존 skill의 입출력 스키마를 변경하면, 이 Agent에 의존하는 모든 Client Agent가 영향받습니다. Major 버전을 올리고, 이전 버전 엔드포인트를 일정 기간 유지하는 것이 안전합니다.
{% endhint %}

### Agent Discovery 패턴

Client Agent가 적합한 Server Agent를 어떻게 찾을까요? 세 가지 패턴이 있습니다.

| 패턴 | 방식 | 장점 | 단점 |
|------|------|------|------|
| ** 수동 등록** | 개발자가 Agent URL을 직접 설정 | 가장 간단 | 확장 어려움, 변경 시 재배포 |
| **DNS-SD 기반 자동 발견** | DNS Service Discovery로 네트워크 내 Agent 탐색 | 자동화, 동적 | 네트워크 경계 밖 Agent 발견 불가 |
| ** 중앙 레지스트리** | Agent Catalog 서비스에 등록/검색 | 검색, 버전 관리, 접근 제어 가능 | 레지스트리 자체가 SPOF 가능 |

** 엔터프라이즈 환경에서는 중앙 레지스트리(Agent Catalog) 패턴을 권장합니다.**이유는 다음과 같습니다:

- ** 거버넌스**: 어떤 Agent가 등록되어 있는지 한눈에 파악 가능
- ** 접근 제어**: Agent별로 누가 호출할 수 있는지 관리
- ** 모니터링**: Agent 상태(healthy/unhealthy)를 중앙에서 추적
- ** 버전 관리**: 같은 Agent의 여러 버전을 동시에 운영 가능

---

## 2. Task (작업 단위) — 라이프사이클

A2A에서 모든 상호작용은 Task 중심으로 이루어집니다. Task는 명확한 상태 전이를 거칩니다.

```
submitted → working → completed
              │
              ├→ input-required → (추가 입력 제공) → working
              │
              ├→ failed
              │
              └→ canceled
```

| 상태 | 설명 | 전이 가능 상태 |
|------|------|---------------|
| `submitted` | 작업 제출됨 | working, failed, canceled |
| `working` | 처리 중 | completed, input-required, failed, canceled |
| `input-required` | 추가 정보 필요 | working (정보 제공 후), canceled |
| `completed` | 완료 | (종료) |
| `failed` | 실패 | (종료) |
| `canceled` | 취소 | (종료) |

{% hint style="info" %}
`input-required`는 A2A의 핵심 상태입니다. Agent가 작업 중 "추가 정보가 필요합니다"라고 요청할 수 있어, 진정한 ** 대화형 협업**이 가능합니다.
{% endhint %}

### 에러 핸들링 심화

Task가 `failed` 상태로 전이되면, Client Agent는 어떻게 대응해야 할까요?

** 재시도 전략: Exponential Backoff**

```
1차 시도 실패 → 1초 대기 → 재시도
2차 시도 실패 → 2초 대기 → 재시도
3차 시도 실패 → 4초 대기 → 재시도
4차 시도 실패 → 8초 대기 → 재시도 (최대 대기 시간 설정)
5차 시도 실패 → 최종 실패 처리
```

단순히 같은 요청을 반복하는 것이 아니라, 실패 원인에 따라 전략이 달라져야 합니다:

| 실패 유형 | 재시도 여부 | 권장 전략 |
|-----------|-----------|----------|
| 일시적 네트워크 장애 (5xx) | 재시도 가능 | Exponential Backoff (최대 3~5회) |
| 인증 실패 (401/403) | 재시도 불가 | 토큰 갱신 후 재시도 |
| 잘못된 요청 (400) | 재시도 불가 | 요청 내용 수정 필요 |
| Agent 과부하 (429) | 지연 후 재시도 | `Retry-After` 헤더 존중 |
| 타임아웃 | 조건부 재시도 | 멱등성(Idempotency) 확인 후 재시도 |

** 부분 실패 처리**: 여행 예약 시나리오에서 항공 Agent는 성공했지만 호텔 Agent가 실패한 경우, 전체를 실패로 처리할까요? 부분 성공으로 처리할까요?

- **All-or-Nothing**: 하나라도 실패하면 전체 롤백. 금융 거래처럼 일관성이 중요한 경우.
- **Best-Effort**: 성공한 결과만 반환하고, 실패한 부분을 사용자에게 알림. 정보 검색처럼 부분 결과도 가치가 있는 경우.
- **Saga 패턴**: 각 단계에 보상 트랜잭션(Compensating Transaction)을 정의. 호텔 예약 실패 시 → 항공권 예약 취소.

### 장기 실행 Task 관리

수 분에서 수 시간이 걸리는 Task(예: 대규모 데이터 분석, 복잡한 리서치)는 어떻게 관리할까요?

| 방식 | 동작 | 적합한 경우 |
|------|------|-----------|
| **Polling** | Client가 주기적으로 `tasks/get`으로 상태 확인 | 간단한 구현, 짧은 작업 (수 분) |
| **Streaming (SSE)** | Server가 진행 상황을 실시간 스트리밍 | 사용자에게 진행률 표시 필요 시 |
| **Push Notification** | Task 완료 시 콜백 URL로 알림 | 긴 작업 (수 시간), 리소스 절약 |

** 연결 끊김 시 Task 복구**: A2A의 Task는 고유한 `id`를 가지므로, 연결이 끊겨도 `tasks/get`으로 상태를 복구할 수 있습니다. 이것이 A2A가 Stateful한 이유이며, Stateless REST API와의 핵심 차이입니다.

### Task 체이닝

Task A의 결과를 Task B의 입력으로 사용하는 ** 파이프라인**을 구성할 수 있습니다.

```
Task A (데이터 수집) → Artifact (원본 데이터)
    ↓
Task B (데이터 정제) → Artifact (정제된 데이터)
    ↓
Task C (분석 및 시각화) → Artifact (차트 JSON)
```

체이닝 시 주의사항:
- 각 Task의 **outputModes** 와 다음 Task의 **inputModes** 가 호환되는지 확인해야 합니다
- 중간 Task 실패 시 전체 체인의 처리 전략을 미리 정의해야 합니다
- Artifact의 크기가 클 경우, 직접 전달 대신 **참조(Reference)** 를 전달하는 것이 효율적입니다

---

## 3. Message & Artifact

- **Message**: Agent 간 대화 메시지 (텍스트, 구조화 데이터)
- **Artifact**: Task의 결과물 (파일, 이미지, JSON 등)
- 하나의 Task에 여러 Message와 Artifact가 포함될 수 있음

---

## 4. Streaming & Push Notifications

- **Streaming (SSE)**: 장기 실행 Task의 중간 진행 상황을 실시간 스트리밍
- **Push Notifications**: Task 상태 변경 시 콜백 URL로 알림 전송
