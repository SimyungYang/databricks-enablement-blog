# Tool Use / Function Calling

[← AI Agent 아키텍처 개요](README.md)

---

Tool Use는 LLM이 외부 도구(함수)를 호출할 수 있는 기능입니다. LLM이 직접 코드를 실행하는 것이 아니라, **"어떤 함수를 어떤 인자로 호출할지"를 JSON으로 결정**하고, 시스템이 실제 실행합니다.

## 동작 흐름 (JSON 수준)

**1단계: 사용자 질문**
```json
{"role": "user", "content": "서울 날씨 알려줘"}
```

**2단계: LLM이 도구 호출을 결정** (LLM이 생성하는 JSON)
```json
{
  "tool_calls": [{
    "function": {
      "name": "get_weather",
      "arguments": "{\"city\": \"Seoul\", \"unit\": \"celsius\"}"
    }
  }]
}
```

**3단계: 시스템이 함수 실행 후 결과 반환**
```json
{"role": "tool", "content": "{\"temperature\": 22, \"condition\": \"맑음\", \"humidity\": 45}"}
```

**4단계: LLM이 결과를 해석하여 최종 응답**
```json
{"role": "assistant", "content": "서울은 현재 22도이고 맑은 날씨입니다. 습도는 45%입니다."}
```

---

## 도구 정의 예시 (Databricks Agent Framework)

```python
from databricks.sdk import WorkspaceClient

# Unity Catalog Function을 도구로 등록
tools = [
    {"function_name": "catalog.schema.search_documents"},
    {"function_name": "catalog.schema.get_customer_info"},
    {"function_name": "catalog.schema.execute_sql_query"},
]
```

{% hint style="info" %}
**핵심 포인트**: LLM은 함수를 직접 실행하지 않습니다. "어떤 함수를 호출할지"를 결정할 뿐이고, 실제 실행은 Agent Framework가 담당합니다. 이 분리가 보안과 제어의 핵심입니다.
{% endhint %}

---

## Tool Description이 Agent 성능의 80%

Agent의 도구 선택 정확도는 도구 설명(description)의 품질에 가장 크게 좌우됩니다. 아래 3쌍의 비교를 보면 그 차이가 명확합니다.

### 비교 1: 검색 도구

| 구분 | 나쁜 설명 | 좋은 설명 |
|------|----------|----------|
| name | `search` | `search_customer_db` |
| description | "검색합니다" | "고객 데이터베이스에서 이름, 이메일, 계약 상태로 고객을 검색합니다. 최대 50건 반환. 부분 일치 지원." |
| **결과** | LLM이 문서 검색인지 고객 검색인지 혼동 | LLM이 고객 관련 질문에 정확히 이 도구를 선택 |

### 비교 2: SQL 도구

| 구분 | 나쁜 설명 | 좋은 설명 |
|------|----------|----------|
| name | `run_query` | `execute_readonly_sql` |
| description | "쿼리를 실행합니다" | "Unity Catalog의 sales_db 스키마에서 읽기 전용 SQL을 실행합니다. SELECT만 허용. 결과는 JSON 배열로 반환되며 최대 1000행." |
| **결과** | Agent가 UPDATE/DELETE를 시도할 수 있음 | 읽기 전용임을 인지하고 SELECT만 생성 |

### 비교 3: 알림 도구

| 구분 | 나쁜 설명 | 좋은 설명 |
|------|----------|----------|
| name | `notify` | `send_slack_notification` |
| description | "알림을 보냅니다" | "지정된 Slack 채널에 메시지를 전송합니다. channel_id(필수)와 message(필수, 최대 4000자)를 받습니다. 예시: channel_id='C0123ABC', message='배치 작업 완료'" |
| **결과** | 이메일인지 Slack인지 SMS인지 불명확 | 채널, 형식, 제한 사항까지 명확히 인지 |

---

## 도구 수와 성능의 관계

Agent에 등록된 도구 수가 늘어날수록 정확도가 떨어집니다. 이는 LLM의 Context Window에 모든 도구 설명이 포함되면서 주의력(attention)이 분산되기 때문입니다.

| 도구 수 | 도구 선택 정확도 (경험적) | 권장 대응 |
|---------|------------------------|----------|
| 1~5개 | 95%+ | 추가 조치 불필요 |
| 6~10개 | 85~90% | 도구 설명 품질 최적화 |
| 11~15개 | 70~80% | 카테고리 분류 도입 검토 |
| 16~20개 | 55~65% | 라우팅 Agent 또는 Multi-Agent 전환 필수 |
| 20개 초과 | 50% 이하 | 반드시 Multi-Agent로 분해 |

{% hint style="warning" %}
**도구가 15개를 넘어가면**, 단일 Agent로는 안정적인 서비스가 어렵습니다. 이때의 대응 전략:
1. **카테고리 라우팅**: 먼저 "어떤 카테고리의 도구가 필요한지" 판단하는 가벼운 LLM 호출을 추가하고, 해당 카테고리의 도구만 Agent에 전달합니다.
2. **Multi-Agent 전환**: 도메인별로 Agent를 분리하고, Supervisor가 적절한 Agent에게 라우팅합니다.
{% endhint %}

---

## 도구 설계 원칙 7가지

프로덕션 Agent의 도구를 설계할 때 지켜야 할 7가지 원칙입니다. 이 원칙을 따르면 Agent의 안정성과 디버깅 용이성이 크게 향상됩니다.

| # | 원칙 | 설명 | 나쁜 예 | 좋은 예 |
|---|------|------|---------|---------|
| 1 | **단일 책임** | 하나의 도구는 하나의 작업만 수행 | `manage_customer(action, ...)` | `get_customer()`, `update_customer()` 분리 |
| 2 | **유용한 에러 반환** | 실패 시 원인과 해결 힌트를 반환 | `{"error": "failed"}` | `{"error": "customer_id 'ABC'를 찾을 수 없습니다. 숫자 ID를 사용하세요."}` |
| 3 | **입력 검증** | 도구 내부에서 인자를 검증 | SQL Injection 가능 | 파라미터 바인딩, 타입 체크 |
| 4 | **타임아웃 설정** | 외부 API 호출에 반드시 타임아웃 | 무한 대기 가능 | 30초 타임아웃 + 재시도 1회 |
| 5 | **멱등성(Idempotency)** | 같은 입력으로 여러 번 호출해도 같은 결과 | 호출할 때마다 중복 레코드 생성 | 중복 체크 후 기존 결과 반환 |
| 6 | **결과 크기 제한** | 반환 데이터 크기를 제한 | 10만 행을 그대로 반환 | 최대 100행 + 전체 건수 메타데이터 |
| 7 | **설명에 예시 포함** | description에 호출 예시를 포함 | "고객을 검색합니다" | "고객을 검색합니다. 예시: name='홍길동', status='active'" |

{% hint style="success" %}
**원칙 2 (유용한 에러)가 가장 중요합니다.** Agent가 에러를 받았을 때 "무엇이 잘못되었고 어떻게 고칠 수 있는지"를 알 수 있어야 자율적으로 복구할 수 있습니다. `"error": "500"` 같은 에러는 Agent를 무한 루프에 빠뜨리는 주범입니다.
{% endhint %}

---

[다음: Agent Memory 시스템 →](memory.md)
