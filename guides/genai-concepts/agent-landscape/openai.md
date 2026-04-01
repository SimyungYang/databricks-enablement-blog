# OpenAI의 AI Agent 전략

OpenAI는 2025년을 기점으로 단순 챗봇 회사에서 **AI Agent 플랫폼 기업**으로 전환했습니다. Consumer(ChatGPT)와 Developer(API/SDK) 양축에서 동시에 Agent 생태계를 구축하고 있으며, 모든 것의 기반에는 **Responses API**가 있습니다.

{% hint style="info" %}
**학습 목표**
- OpenAI의 Consumer + Developer 이중 Agent 전략을 설명할 수 있다
- Agents SDK의 4가지 프리미티브(Agent, Handoff, Guardrail, Tracing)를 코드 수준에서 이해한다
- Responses API가 Chat Completions를 대체하는 이유와 장점을 설명할 수 있다
- GPT-4.1, o3, Codex 등 Agent 특화 모델들의 차이를 비교할 수 있다
- Databricks 환경에서 OpenAI Agent 기술을 활용하는 패턴을 설계할 수 있다
{% endhint %}

---

## 1. OpenAI Agent 전략 개요

### Consumer + Developer 이중 전략

OpenAI의 Agent 전략은 두 축으로 나뉩니다:

| 축 | 대상 | 핵심 제품 | 목표 |
|---|---|---|---|
| **Consumer** | 일반 사용자 | ChatGPT Agent Mode, Operator, Deep Research | "누구나 Agent를 사용" |
| **Developer** | 개발자/기업 | Responses API, Agents SDK, Codex | "누구나 Agent를 구축" |

### 전략 스택 구조

```
┌────────────────────────────────────────────────────────────┐
│                    Consumer Products                        │
│   ChatGPT Agent Mode  │  Operator  │  Deep Research        │
├────────────────────────────────────────────────────────────┤
│                    Developer Tools                          │
│     Agents SDK  │  Codex  │  MCP Support                   │
├────────────────────────────────────────────────────────────┤
│                    Responses API                            │
│   web_search │ file_search │ code_interpreter │ computer_use│
├────────────────────────────────────────────────────────────┤
│                    Foundation Models                         │
│   GPT-4.1  │  o3/o4-mini  │  GPT-5/5.2  │  codex-1        │
└────────────────────────────────────────────────────────────┘
```

{% hint style="success" %}
**핵심 인사이트**: OpenAI의 모든 Agent 제품은 궁극적으로 **Responses API** 위에 구축됩니다. ChatGPT의 Agent Mode도, Codex도, Operator도 내부적으로 Responses API의 built-in tool을 사용합니다. 이 API를 이해하면 OpenAI Agent 생태계 전체를 관통할 수 있습니다.
{% endhint %}

---

## 2. Agents SDK — 멀티에이전트 오케스트레이션

### 배경: Swarm에서 Agents SDK로

| 구분 | Swarm (2024.10) | Agents SDK (2025.03) |
|---|---|---|
| 성격 | 실험적 교육용 프레임워크 | 프로덕션 레디 SDK |
| 지원 언어 | Python만 | Python + TypeScript |
| 모델 | OpenAI만 | 모델 무관(Model-agnostic) |
| 추적 | 없음 | 내장 Tracing + OpenTelemetry |
| MCP | 없음 | 네이티브 지원 |
| 라이선스 | MIT | MIT (오픈소스) |

Swarm은 멀티에이전트 패턴의 **개념 증명**이었고, Agents SDK는 이를 **프로덕션 수준**으로 발전시킨 것입니다.

### 4가지 프리미티브

Agents SDK는 딱 **4개의 핵심 프리미티브**만으로 복잡한 에이전트 시스템을 구축합니다:

#### (1) Agent — 역할 정의

Agent는 특정 역할과 도구를 가진 **자율적 실행 단위**입니다.

```python
from agents import Agent, Runner

# Agent 정의 — instructions로 역할과 행동 규칙 지정
sales_agent = Agent(
    name="Sales Agent",
    instructions="""당신은 영업팀 전문 상담사입니다.
    - 제품 가격, 라이선스, 할인 정책에 대해 정확히 답변하세요.
    - 기술적 질문은 직접 답하지 말고, 기술 상담 에이전트로 넘기세요.
    - 항상 고객의 회사 규모와 요구사항을 먼저 파악하세요.""",
    model="gpt-4.1",
    tools=[pricing_tool, crm_lookup_tool],
)
```

{% hint style="info" %}
**`instructions`는 Agent의 성격을 결정합니다.** 역할, 행동 규칙, 경계(무엇을 하지 말아야 하는지)를 명확히 정의하세요. GPT-4.1은 instruction following 성능이 크게 향상되어, 복잡한 규칙도 정확히 따릅니다.
{% endhint %}

#### (2) Handoff — 에이전트 간 위임

Handoff는 한 에이전트가 다른 에이전트에게 **대화의 제어권을 넘기는** 메커니즘입니다.

```python
from agents import Agent, handoff

tech_agent = Agent(
    name="Tech Support Agent",
    instructions="기술적인 질문에 답변합니다. 가격 질문은 영업 에이전트로 넘기세요.",
    tools=[docs_search_tool, code_executor_tool],
    handoffs=[handoff(sales_agent)],  # 영업 에이전트로 핸드오프 가능
)

# Triage Agent — 모든 요청을 분류하여 적절한 에이전트로 라우팅
triage_agent = Agent(
    name="Triage Agent",
    instructions="""사용자 요청을 분석하여 적절한 에이전트로 라우팅하세요:
    - 가격, 라이선스, 할인 → Sales Agent
    - 기술 지원, 버그, 설정 → Tech Support Agent
    - 판단이 어려우면 추가 질문으로 의도를 파악하세요.""",
    handoffs=[
        handoff(sales_agent),
        handoff(tech_agent),
    ],
)
```

{% hint style="warning" %}
**Handoff 설계 원칙**: Triage Agent는 가능한 한 **간단한 라우팅 로직만** 담당하게 하세요. Triage에 복잡한 도구를 주면 분류 정확도가 떨어집니다. 각 Specialist Agent가 자체 도구와 전문성을 갖도록 설계하는 것이 핵심입니다.
{% endhint %}

#### (3) Guardrail — 입출력 안전장치

Guardrail은 에이전트의 입력과 출력을 **자동으로 검증**합니다.

```python
from agents import Agent, InputGuardrail, GuardrailFunctionOutput
from pydantic import BaseModel

class SafetyCheck(BaseModel):
    is_safe: bool
    reason: str

# Guardrail Agent — 입력이 안전한지 판단하는 별도 에이전트
safety_agent = Agent(
    name="Safety Checker",
    instructions="사용자 입력이 안전한지 판단하세요. 개인정보, 욕설, 유해 콘텐츠가 있으면 unsafe로 분류하세요.",
    output_type=SafetyCheck,
)

async def check_safety(ctx, agent, input_text):
    result = await Runner.run(safety_agent, input_text, context=ctx)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_safe,
    )

# Guardrail을 Agent에 부착
main_agent = Agent(
    name="Main Agent",
    instructions="사용자의 질문에 답변합니다.",
    input_guardrails=[
        InputGuardrail(guardrail_function=check_safety),
    ],
)
```

#### (4) Tracing — 실행 추적

Tracing은 에이전트의 **모든 실행 과정을 자동으로 기록**합니다.

```python
from agents import Agent, Runner, trace

# 기본 Tracing — Runner.run()을 호출하면 자동으로 트레이스 생성
result = await Runner.run(triage_agent, "Pro Plan 가격이 얼마인가요?")

# 커스텀 Trace 그룹핑 — 여러 실행을 하나의 워크플로우로 묶기
with trace("customer-support-workflow"):
    classification = await Runner.run(triage_agent, user_message)
    # 이후 실행도 같은 trace에 포함됨
```

{% hint style="info" %}
**Tracing은 OpenAI Dashboard에서 시각적으로 확인 가능**하며, OpenTelemetry 프로토콜을 지원하므로 Datadog, Jaeger 등 기존 관측 인프라에 통합할 수 있습니다.
{% endhint %}

### 완성 예제: 멀티에이전트 고객 상담 시스템

```python
from agents import Agent, Runner, handoff, InputGuardrail, trace
import asyncio

# ── Tool 정의 ──
def lookup_order(order_id: str) -> str:
    """주문 상태를 조회합니다."""
    # 실제로는 DB 호출
    return f"주문 {order_id}: 배송 중 (예상 도착일: 2026-04-02)"

def check_refund_policy(product: str) -> str:
    """환불 정책을 확인합니다."""
    return f"{product}의 환불 가능 기간은 구매 후 30일입니다."

# ── Specialist Agents ──
order_agent = Agent(
    name="Order Agent",
    instructions="주문 조회, 배송 상태 확인을 담당합니다.",
    tools=[lookup_order],
)

refund_agent = Agent(
    name="Refund Agent",
    instructions="환불, 반품 관련 문의를 처리합니다.",
    tools=[check_refund_policy],
)

# ── Triage Agent ──
triage_agent = Agent(
    name="Triage Agent",
    instructions="""고객 문의를 분류하여 적절한 에이전트로 전달하세요:
    - 주문, 배송 → Order Agent
    - 환불, 반품 → Refund Agent
    - 일반 문의는 직접 답변하세요.""",
    handoffs=[
        handoff(order_agent),
        handoff(refund_agent),
    ],
)

# ── 실행 ──
async def main():
    with trace("customer-support"):
        result = await Runner.run(
            triage_agent,
            "주문번호 ORD-2026-1234 배송이 언제 오나요?"
        )
        print(result.final_output)
        # → "주문 ORD-2026-1234: 배송 중 (예상 도착일: 2026-04-02)"

asyncio.run(main())
```

---

## 3. Responses API — Agent의 기반 API

### Chat Completions vs Responses API

2025년 3월, OpenAI는 **Responses API**를 발표하며 Agent 시대의 새로운 기반 API로 제시했습니다.

| 비교 항목 | Chat Completions API | Responses API |
|---|---|---|
| 출시 | 2023.03 | 2025.03 |
| 패러다임 | 단일 요청-응답 | **에이전틱 루프** (단일 API 호출로 다단계 실행) |
| 도구 호출 | function calling (개발자 구현) | **Built-in tools** (OpenAI가 호스팅) |
| 상태 관리 | 개발자가 직접 관리 | `previous_response_id`로 자동 연결 |
| 내장 도구 | 없음 | `web_search`, `file_search`, `code_interpreter`, `computer_use` |
| 스트리밍 | SSE | SSE + 네이티브 이벤트 |
| 폐기 예정 | 당장 아님 (유지) | 차세대 표준 |

### Built-in Tools 상세

| 도구 | 용도 | 설명 |
|---|---|---|
| `web_search` | 실시간 검색 | Bing/자체 인덱스 기반 웹 검색. 최신 정보 필요 시 자동 호출 |
| `file_search` | 파일 검색 | 벡터 스토어에 업로드한 파일에서 RAG 검색 |
| `code_interpreter` | 코드 실행 | Python 샌드박스에서 코드 실행. 데이터 분석, 차트 생성 |
| `computer_use` | 컴퓨터 제어 | 스크린샷 기반 GUI 자동화 (Operator의 기반 기술) |

```python
from openai import OpenAI

client = OpenAI()

# Responses API — 단일 호출로 에이전틱 작업 수행
response = client.responses.create(
    model="gpt-4.1",
    input="2026년 1분기 AI Agent 시장 트렌드를 분석해주세요.",
    tools=[
        {"type": "web_search"},          # 웹 검색 자동 사용
        {"type": "code_interpreter"},     # 데이터 분석 필요 시 코드 실행
    ],
)

# 단일 API 호출이지만, 내부적으로:
# 1) web_search로 최신 정보 수집
# 2) code_interpreter로 데이터 정리/분석
# 3) 최종 분석 보고서 생성
# → 이 모든 것이 하나의 response에 담김
print(response.output_text)
```

{% hint style="warning" %}
**Assistants API는 2026년 상반기 중 폐기 예정**입니다. Threads, Runs 등 Assistants API의 개념을 사용 중이라면, Responses API + Agents SDK 조합으로 마이그레이션을 계획하세요. OpenAI는 공식 마이그레이션 가이드를 제공하고 있습니다.
{% endhint %}

### 마이그레이션 타임라인

| 시점 | 상태 |
|---|---|
| 2025.03 | Responses API GA, Assistants API 신규 기능 동결 |
| 2025 하반기 | Assistants API 공식 deprecated 선언 |
| 2026 상반기 | Assistants API 완전 종료 예정 |

---

## 4. GPT-4.1 — Agent 특화 모델

### 왜 "Agent 특화"인가?

GPT-4.1(2025년 4월)은 OpenAI가 **처음으로 "Agent용"을 명시적으로 표방한** 모델입니다. API 전용으로 출시되었으며 ChatGPT에는 탑재되지 않았습니다.

Agent에 중요한 3가지 측면에서 대폭 개선되었습니다:

| 개선 영역 | 내용 |
|---|---|
| **Instruction Following** | 시스템 프롬프트의 복잡한 규칙을 정확히 준수. 에이전트의 "역할 이탈" 감소 |
| **Tool Calling 신뢰성** | Function calling 정확도 향상. 잘못된 파라미터, 불필요한 호출 대폭 감소 |
| **Long Context 처리** | 1M 토큰 컨텍스트. 대용량 코드베이스, 긴 대화 이력 처리 가능 |

### 벤치마크 성능

| 벤치마크 | GPT-4o | GPT-4.1 | 개선폭 |
|---|---|---|---|
| SWE-bench (코딩) | 33.2% | **54.6%** | +21.4%p |
| MMLU (지식) | 85.7% | **87.1%** | +1.4%p |
| Instruction Following | 78.3% | **89.7%** | +11.4%p |
| Tool Use Accuracy | 82.1% | **93.4%** | +11.3%p |

### 가격 비교

| 모델 | Input (1M tokens) | Output (1M tokens) | 컨텍스트 | 용도 |
|---|---|---|---|---|
| **GPT-4.1** | $2.00 | $8.00 | 1M | Agent 메인 모델 |
| **GPT-4.1 mini** | $0.40 | $1.60 | 1M | 경량 Agent, 분류 |
| **GPT-4.1 nano** | $0.10 | $0.40 | 1M | 가드레일, 라우팅 |
| GPT-4o (비교) | $2.50 | $10.00 | 128K | 범용 |

{% hint style="success" %}
**비용 최적화 팁**: 멀티에이전트 시스템에서 Triage Agent에는 **nano**, Specialist Agent에는 **mini** 또는 **4.1**, 최종 품질이 중요한 응답에만 **4.1**을 사용하면 비용을 90% 이상 절감할 수 있습니다. Agents SDK에서 각 Agent마다 다른 모델을 지정할 수 있습니다.
{% endhint %}

```python
# 모델별 에이전트 — 비용 최적화 패턴
triage = Agent(name="Triage", model="gpt-4.1-nano", ...)      # 라우팅만
classifier = Agent(name="Classifier", model="gpt-4.1-mini", ...) # 분류
analyst = Agent(name="Analyst", model="gpt-4.1", ...)           # 심층 분석
```

---

## 5. Codex — 코딩 에이전트

### Cloud Codex vs CLI Codex

OpenAI Codex(2025년 5월 프리뷰, 10월 GA)는 **자율적으로 코드를 작성, 테스트, 디버깅**하는 코딩 에이전트입니다.

| 구분 | Cloud Codex | CLI Codex |
|---|---|---|
| 환경 | ChatGPT 내 클라우드 실행 | 로컬 터미널 |
| 모델 | codex-1, GPT-5-Codex | codex-1, GPT-5-Codex |
| 실행 방식 | 샌드박스 VM에서 자율 실행 | 로컬 repo에서 직접 실행 |
| 병렬성 | 여러 태스크 동시 실행 가능 | 단일 세션 |
| 소스 | SaaS | **오픈소스 (Rust)** |
| 주요 용도 | PR 생성, 리팩토링, 버그 수정 | 로컬 개발 보조 |

### 작동 방식

1. 사용자가 자연어로 태스크 지시 (예: "이 함수에 에러 핸들링 추가해줘")
2. Codex가 전체 코드베이스를 분석
3. 필요한 파일을 수정하고 테스트 실행
4. 테스트 통과 시 PR 생성 또는 diff 제시
5. 실패 시 자동으로 디버깅 및 재시도

### 실제 도입 사례

| 기업 | 활용 방식 |
|---|---|
| **Duolingo** | 코드 리뷰 자동화, 단위 테스트 생성 |
| **Cisco** | 레거시 코드 마이그레이션, 보안 패치 자동화 |

{% hint style="info" %}
**GitHub Copilot과의 관계**: GPT-4.1은 GitHub Copilot의 기본 모델로 채택되었습니다. Codex는 Copilot보다 더 자율적이고 큰 단위의 작업(PR 단위)을 처리하는 반면, Copilot은 코드 에디터 내 실시간 보조에 초점을 맞춥니다.
{% endhint %}

---

## 6. Operator & Deep Research

### Operator — 브라우저 자동화 에이전트

Operator(2025년 1월 프리뷰)는 **Computer-Using Agent(CUA)** 기술 기반의 브라우저 자동화 에이전트입니다.

#### CUA 작동 원리

```
┌─────────────────────────────────────────┐
│           CUA 실행 루프                  │
│                                         │
│  1. 스크린샷 캡처                        │
│       ↓                                 │
│  2. 화면 분석 (현재 상태 이해)            │
│       ↓                                 │
│  3. 다음 행동 결정 (클릭/타이핑/스크롤)    │
│       ↓                                 │
│  4. 행동 실행                            │
│       ↓                                 │
│  5. 새 스크린샷 캡처 → 1로 돌아감         │
│                                         │
│  * 로그인/결제 시 사용자에게 제어권 반환   │
└─────────────────────────────────────────┘
```

| 특징 | 설명 |
|---|---|
| 입력 | 자연어 지시 ("항공편 예약해줘") |
| 처리 | 스크린샷 → 추론 → 마우스/키보드 제어 반복 |
| 보안 | 샌드박스 브라우저, 민감 정보 입력 시 사용자에게 제어권 반환 |
| API | Responses API의 `computer_use` tool로 개발자도 사용 가능 |

### Deep Research — 자율 리서치 에이전트

Deep Research(2025년 2월 GA)는 **o3 모델** 기반으로, 복잡한 연구 질문에 대해 **자율적으로 다단계 웹 리서치**를 수행합니다.

#### 자율 리서치 루프

1. 사용자 질문을 **하위 연구 질문**으로 분해
2. 각 질문에 대해 웹 검색 수행 (수십~수백 개 소스)
3. 검색 결과를 분석하며 **추가 질문 생성** (재귀적 탐색)
4. 모든 정보를 종합하여 **구조화된 보고서** 생성
5. 출처와 인용 포함

{% hint style="info" %}
Deep Research는 5~30분에 걸쳐 수십 개의 웹 페이지를 탐색합니다. 단순 검색이 아닌 **사람이 며칠간 할 리서치를 자동화**하는 개념입니다.
{% endhint %}

### ChatGPT Agent Mode로의 통합

2025년 7월, OpenAI는 Operator + Deep Research + 기존 도구들을 **ChatGPT Agent Mode**라는 통합 경험으로 결합했습니다.

| 기존 (분리) | 통합 후 (Agent Mode) |
|---|---|
| ChatGPT: 대화만 | 대화 + 검색 + 코드 실행 + 브라우저 자동화 |
| Operator: 별도 앱 | ChatGPT 내 기능으로 통합 |
| Deep Research: 별도 모드 | Agent Mode의 리서치 기능으로 통합 |

o3가 **최초로 ChatGPT의 모든 도구를 에이전틱하게 사용**할 수 있는 모델이며, Agent Mode의 핵심 엔진입니다.

---

## 7. 추론 모델 (o3, o4-mini)

### Reasoning + Tool Use의 결합

o3과 o4-mini(2025년 4월)는 **체인 오브 쏘트(Chain-of-Thought) 추론 중에 도구를 호출**할 수 있는 최초의 모델입니다.

기존 모델은 "추론 → 도구 호출 → 결과 수신 → 응답"이 순차적이었지만, o3/o4-mini는 **추론 과정 자체에서 도구를 사용**합니다.

```
[기존 모델]
User → LLM 추론 → Tool 호출 결정 → Tool 실행 → LLM 응답

[o3/o4-mini]
User → 추론 시작 → (추론 중) Tool 호출 → 결과 반영하며 추론 계속
       → (추론 중) 또 다른 Tool 호출 → 결과 반영 → 최종 응답
```

### 가격/성능 비교

| 모델 | Input (1M) | Output (1M) | 특징 |
|---|---|---|---|
| **o3** | $10.00 | $40.00 | 최고 추론 성능. 복잡한 분석, 수학, 코딩 |
| **o4-mini** | $1.10 | $4.40 | o3 대비 80% 저렴, 추론 성능의 90% 유지 |
| GPT-4.1 (비교) | $2.00 | $8.00 | 추론 없음. 빠른 응답, Agent 최적화 |

{% hint style="warning" %}
**o3 vs GPT-4.1 선택 기준**:
- **정확한 추론이 필수인 작업** (수학, 논리, 복잡한 코딩) → o3
- **빠른 응답과 도구 활용이 중요한 Agent** (고객 상담, 데이터 조회) → GPT-4.1
- o3는 "생각하는 시간"이 있어 응답이 느릴 수 있습니다. Agent의 사용자 경험을 고려하세요.
{% endhint %}

---

## 8. GPT-5 / GPT-5.2 — 최신 모델 동향

| 모델 | 출시 | 주요 특징 |
|---|---|---|
| **GPT-5** | 2025년 중반 | GPT-4.1 대비 전반적 성능 도약. 추론+생성 통합 |
| **GPT-5.2** | 2025년 12월 | 환각(hallucination) 30% 감소. 가장 신뢰할 수 있는 모델 |

GPT-5.2의 환각 감소는 Agent 환경에서 특히 중요합니다. Agent가 잘못된 정보를 기반으로 도구를 호출하거나 의사결정을 내리면 연쇄 오류(cascading error)가 발생하기 때문입니다.

---

## 9. Databricks 환경에서의 시사점

### OpenAI 모델을 Databricks에서 사용하는 방법

Databricks는 OpenAI 모델을 **External Models** 기능으로 네이티브하게 지원합니다.

| 방법 | 설명 | 적합한 경우 |
|---|---|---|
| **Foundation Model APIs** | Databricks가 호스팅하는 모델 (DBRX, Llama 등) | 오픈소스 모델 사용 시 |
| **External Models** | 외부 모델(OpenAI, Anthropic 등)을 Model Serving endpoint로 래핑 | OpenAI 모델 필요 시 |
| **직접 API 호출** | 코드에서 OpenAI API 직접 호출 | 간단한 프로토타이핑 |

```python
# Databricks Model Serving으로 GPT-4.1 호출 (External Model 설정 후)
import mlflow.deployments

client = mlflow.deployments.get_deploy_client("databricks")

response = client.predict(
    endpoint="openai-gpt-4-1",  # External Model endpoint 이름
    inputs={
        "messages": [
            {"role": "system", "content": "당신은 데이터 분석 전문가입니다."},
            {"role": "user", "content": "매출 트렌드를 분석해주세요."},
        ],
        "temperature": 0.1,
    },
)
```

{% hint style="success" %}
**External Models의 장점**: OpenAI API 키를 개발자에게 직접 배포하지 않고, Databricks의 **거버넌스(Unity Catalog)와 모니터링**을 통해 중앙 관리할 수 있습니다. 토큰 사용량, 비용, 레이턴시를 Model Serving 대시보드에서 추적할 수 있습니다.
{% endhint %}

### Agents SDK + Databricks Agent Framework 조합

| 시나리오 | 권장 조합 |
|---|---|
| Databricks 데이터 기반 Agent | **Databricks Agent Framework** (Mosaic AI) — Unity Catalog, MLflow 통합 |
| 외부 시스템 연동 멀티에이전트 | **OpenAI Agents SDK** — 다양한 외부 API, 브라우저 자동화 필요 시 |
| 하이브리드 | Agents SDK로 오케스트레이션 + Databricks Model Serving으로 모델 호출 |

```python
# 하이브리드 패턴 예시: Agents SDK + Databricks 데이터
from agents import Agent, function_tool
import mlflow.deployments

db_client = mlflow.deployments.get_deploy_client("databricks")

@function_tool
def query_lakehouse(sql: str) -> str:
    """Databricks SQL Warehouse로 데이터를 조회합니다."""
    from databricks import sql as dbsql
    with dbsql.connect(server_hostname="...", http_path="...") as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        return str(cursor.fetchall())

data_agent = Agent(
    name="Data Analyst",
    instructions="Databricks Lakehouse의 데이터를 분석합니다.",
    model="gpt-4.1",
    tools=[query_lakehouse],
)
```

---

## 10. 고객이 자주 묻는 질문

### Q1. Chat Completions API를 당장 Responses API로 바꿔야 하나요?

{% hint style="info" %}
**아니요, 당장은 아닙니다.** Chat Completions API는 계속 유지됩니다. 다만 Assistants API를 사용 중이라면 Responses API로의 마이그레이션을 2025년 내에 계획하세요. 새로운 Agent 프로젝트를 시작한다면 처음부터 Responses API를 권장합니다.
{% endhint %}

### Q2. Agents SDK vs LangGraph vs Databricks Agent Framework, 어떤 것을 선택해야 하나요?

| 기준 | OpenAI Agents SDK | LangGraph | Databricks Agent Framework |
|---|---|---|---|
| 모델 의존성 | OpenAI 최적화 (타 모델 가능) | 모델 무관 | Databricks 모델 최적화 |
| 복잡도 | 낮음 (4 프리미티브) | 높음 (그래프 설계) | 중간 (노코드 가능) |
| 데이터 거버넌스 | 별도 구현 | 별도 구현 | Unity Catalog 내장 |
| 배포 | 자체 인프라 | 자체 인프라/LangServe | Model Serving 원클릭 |
| 추천 상황 | OpenAI 중심 멀티에이전트 | 복잡한 워크플로우 | Databricks 데이터 중심 Agent |

### Q3. GPT-4.1과 o3 중 어떤 모델을 Agent에 사용해야 하나요?

{% hint style="info" %}
**대부분의 Agent에는 GPT-4.1이 적합합니다.** o3는 수학적 추론이나 복잡한 논리 문제에서 우수하지만, 일반적인 Agent(도구 호출, 대화, 데이터 조회)에는 GPT-4.1이 더 빠르고 저렴합니다. 비용을 고려하면 GPT-4.1 mini/nano를 보조 Agent에 활용하는 것이 효율적입니다.
{% endhint %}

### Q4. OpenAI Agent 기술을 Databricks 환경에서 사용할 때 보안/거버넌스는 어떻게 하나요?

{% hint style="info" %}
**External Models + Unity Catalog 조합을 권장합니다.**
1. OpenAI API 키를 Databricks Secret으로 관리
2. External Model endpoint로 래핑하여 API 키를 개발자에게 노출하지 않음
3. Unity Catalog의 권한 관리로 endpoint 접근 제어
4. Model Serving의 로깅으로 모든 호출 기록 추적
5. AI Gateway를 통한 rate limiting 및 비용 제어
{% endhint %}

---

## 11. 참고 자료

### 공식 문서

| 자료 | 링크 |
|---|---|
| Agents SDK GitHub | [https://github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python) |
| Agents SDK 문서 | [https://openai.github.io/openai-agents-python/](https://openai.github.io/openai-agents-python/) |
| Responses API 가이드 | [https://platform.openai.com/docs/guides/responses-vs-chat-completions](https://platform.openai.com/docs/guides/responses-vs-chat-completions) |
| GPT-4.1 발표 | [https://openai.com/index/gpt-4-1/](https://openai.com/index/gpt-4-1/) |
| Codex | [https://openai.com/index/introducing-codex/](https://openai.com/index/introducing-codex/) |
| Codex CLI GitHub | [https://github.com/openai/codex](https://github.com/openai/codex) |
| Operator 소개 | [https://openai.com/index/introducing-operator/](https://openai.com/index/introducing-operator/) |
| Deep Research | [https://openai.com/index/deep-research/](https://openai.com/index/deep-research/) |

### Databricks 관련

| 자료 | 링크 |
|---|---|
| External Models 설정 | [https://docs.databricks.com/en/generative-ai/external-models/index.html](https://docs.databricks.com/en/generative-ai/external-models/index.html) |
| AI Gateway | [https://docs.databricks.com/en/generative-ai/ai-gateway/index.html](https://docs.databricks.com/en/generative-ai/ai-gateway/index.html) |
| Mosaic AI Agent Framework | [https://docs.databricks.com/en/generative-ai/agent-framework/index.html](https://docs.databricks.com/en/generative-ai/agent-framework/index.html) |
