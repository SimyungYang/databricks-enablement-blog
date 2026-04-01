# Anthropic의 AI Agent 전략

Anthropic은 "AI 안전성 연구 기업"이라는 정체성 위에 **세계에서 가장 실용적인 AI Agent 생태계**를 구축하고 있습니다. 모델 성능 경쟁을 넘어, MCP(Model Context Protocol)라는 개방형 표준으로 Agent가 세상과 소통하는 방식 자체를 정의하고, Claude Code와 Agent SDK로 개발자가 Agent를 만들고 배포하는 전체 라이프사이클을 지원합니다.

{% hint style="info" %}
**학습 목표**
- Anthropic의 AI Agent 전략과 제품 포트폴리오의 전체 그림을 이해한다
- MCP가 AI Agent 생태계에서 차지하는 위치와 AAIF 기부의 의미를 설명할 수 있다
- Claude Code, Agent SDK, Computer Use 등 핵심 제품의 아키텍처와 차별점을 파악한다
- 5가지 멀티에이전트 패턴을 이해하고 적절한 상황에 적용할 수 있다
- Databricks 환경에서 Claude를 활용하는 실전 방법을 파악한다
{% endhint %}

---

## 1. 전략 개요 -- "도구를 든 지능"

Anthropic의 Agent 전략은 세 가지 축으로 구성됩니다.

| 축 | 핵심 질문 | 대응 제품 |
|---|---------|---------|
| **모델** | Agent가 얼마나 똑똑한가? | Claude 4 Family (Opus, Sonnet), Extended Thinking |
| **연결** | Agent가 세상과 어떻게 소통하는가? | MCP, Computer Use, Advanced Tool Use |
| **실행** | Agent를 어떻게 만들고 배포하는가? | Claude Code, Agent SDK, Claude Cowork |

{% hint style="success" %}
**Anthropic의 차별화 철학**: OpenAI가 "만능 AI 비서"를, Google이 "검색 + AI 통합"을 추구한다면, Anthropic은 "**개발자가 통제할 수 있는 안전한 Agent**"를 지향합니다. 모든 제품 설계에 "사람이 루프에 있다(Human-in-the-Loop)"는 원칙이 관통합니다.
{% endhint %}

### 타임라인

| 시기 | 제품/이벤트 | 의미 |
|------|-----------|------|
| 2024.10 | **Computer Use** (Beta) | 최초의 프론티어 모델 데스크톱 제어 |
| 2024.11 | **MCP** 표준 공개 | Agent 도구 연결의 개방형 프로토콜 |
| 2024.12 | **멀티에이전트 패턴** 블로그 | "단순하게 시작하라" 설계 철학 공유 |
| 2025.02 | **Claude Code** (GA), **Extended Thinking** | 터미널 기반 코딩 Agent + 사고 과정 가시화 |
| 2025.05 | **Claude Opus 4** | 7시간 자율 작업, 최강 코딩 모델 |
| 2025.09 | **Agent SDK** (Beta) | Claude Code의 능력을 프로그래밍 가능하게 |
| 2025.12 | **MCP를 AAIF에 기부** | OpenAI, Block과 함께 Linux Foundation 산하 표준화 |
| 2026.01 | **Claude Cowork** (Preview) | 지식 노동자를 위한 Agent |

---

## 2. MCP (Model Context Protocol) & AAIF

### MCP란 무엇인가?

MCP는 "**AI Agent를 위한 USB-C**"입니다. LLM이 외부 데이터 소스, 도구, 서비스에 접근하는 방식을 하나의 표준 프로토콜로 통합합니다.

{% hint style="info" %}
**비유**: USB-C가 등장하기 전, 노트북마다 충전기가 달랐습니다. MCP가 등장하기 전, 각 AI 모델마다 도구 연결 방식이 달랐습니다. MCP는 "어떤 LLM이든, 어떤 도구든" 하나의 방식으로 연결할 수 있게 합니다.
{% endhint %}

### 아키텍처

```
┌─────────────┐     JSON-RPC     ┌─────────────┐     ┌──────────────┐
│  MCP Host   │ ◄──────────────► │  MCP Server  │ ──► │ 외부 서비스    │
│ (Claude,    │    (stdio /      │ (DB, API,   │     │ (Slack, DB,  │
│  VS Code,   │     SSE /        │  파일 등)    │     │  GitHub 등)  │
│  커스텀 앱)  │     Streamable   │             │     │              │
│             │     HTTP)        │             │     │              │
└─────────────┘                  └─────────────┘     └──────────────┘
     │                                │
     │  MCP Client                    │  Resources, Tools, Prompts
     │  (내장 또는 SDK)                │  (서버가 노출하는 기능)
     └────────────────────────────────┘
```

### 핵심 개념

| 구성 요소 | 역할 | 예시 |
|----------|------|------|
| **Host** | MCP 클라이언트를 내장한 AI 애플리케이션 | Claude Desktop, VS Code, Genie Code |
| **Client** | Host 안에서 MCP 서버와 1:1 통신 | claude-code의 MCP 클라이언트 |
| **Server** | 특정 기능을 MCP 프로토콜로 노출 | Databricks MCP Server, GitHub MCP Server |
| **Resources** | 읽기 전용 데이터 (LLM의 컨텍스트) | 파일 내용, DB 스키마, 문서 |
| **Tools** | 모델이 호출할 수 있는 함수 | `execute_sql`, `create_issue`, `send_message` |
| **Prompts** | 재사용 가능한 프롬프트 템플릿 | "코드 리뷰해줘", "SQL 작성해줘" |

### 성장 지표 (2025.12 기준)

| 지표 | 수치 |
|------|------|
| 월간 SDK 다운로드 | **9,700만+** |
| 등록된 MCP 서버 | **10,000+** |
| 지원 호스트 | Claude Desktop, VS Code, JetBrains, Cursor, Windsurf, Genie Code 등 |

### AAIF (AI Alliance Interop Framework) 기부

2025년 12월, Anthropic은 MCP를 **Linux Foundation 산하 AAIF**에 기부했습니다. 이는 단일 기업의 프로토콜에서 **산업 표준**으로의 전환을 의미합니다.

| 항목 | 내용 |
|------|------|
| **공동 기부자** | Anthropic, **OpenAI**, Block (Square) |
| **거버넌스** | Linux Foundation의 오픈 거버넌스 모델 |
| **의미** | OpenAI가 합류함으로써 사실상 업계 표준 확정 |
| **호환성** | OpenAI Agents SDK도 MCP 네이티브 지원 |

{% hint style="warning" %}
**핵심 인사이트**: MCP가 AAIF로 갔다는 것은, 앞으로 AI Agent 도구 연결 방식이 **벤더 중립적 표준**이 된다는 뜻입니다. Databricks도 공식 MCP Server를 제공하고 있으며, Genie Code가 MCP Host 역할을 합니다. MCP를 이해하는 것은 선택이 아니라 필수입니다.
{% endhint %}

---

## 3. Claude Code -- 터미널 기반 코딩 Agent

### 개요

Claude Code는 2025년 2월 GA된 **터미널 네이티브 코딩 Agent**입니다. IDE의 보조 도구가 아니라, 터미널에서 직접 코드베이스를 이해하고, 수정하고, 테스트하고, 커밋하는 **자율적 개발자**입니다.

### 성장 지표

| 지표 | 수치 |
|------|------|
| 일일 활성 사용자 | **35만+** |
| 누적 생성 PR | **100만+** |
| 지원 IDE | VS Code, JetBrains (확장 프로그램) |

### 핵심 기능

| 기능 | 설명 |
|------|------|
| **코드베이스 이해** | 대규모 모노레포도 자동으로 파악. `CLAUDE.md`로 프로젝트 컨텍스트 제공 |
| **멀티파일 편집** | 여러 파일을 동시에 수정하고, 의존성까지 추적 |
| **Git 통합** | 커밋, 브랜치, PR 생성을 자연어로 수행 |
| **테스트 실행** | 코드 변경 후 자동으로 테스트 실행, 실패 시 수정 |
| **Subagents** | 복잡한 작업을 하위 Agent에 위임 (병렬 처리) |
| **Hooks** | 특정 이벤트(파일 저장, 커밋 전 등)에 자동 실행되는 스크립트 |
| **Background Tasks** | 장기 실행 작업을 백그라운드에서 수행하고 완료 시 알림 |
| **MCP 클라이언트** | MCP 서버 연결로 DB 쿼리, API 호출, 문서 검색 등 확장 |

### 아키텍처 특징

```
┌──────────────────────────────────────────────────┐
│                  Claude Code                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  Read    │  │  Edit    │  │  Bash        │   │
│  │  (파일)  │  │  (수정)   │  │  (명령 실행)  │   │
│  └──────────┘  └──────────┘  └──────────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  Grep    │  │  Glob    │  │  Git         │   │
│  │  (검색)  │  │  (패턴)   │  │  (버전관리)   │   │
│  └──────────┘  └──────────┘  └──────────────┘   │
│  ┌──────────────────────────────────────────┐    │
│  │  MCP Clients (여러 MCP 서버에 동시 연결)   │    │
│  └──────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────┐    │
│  │  Subagent Pool (병렬 하위 작업 실행)       │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

{% hint style="info" %}
**CLAUDE.md**: 프로젝트 루트에 `CLAUDE.md` 파일을 두면 Claude Code가 프로젝트의 컨텍스트(디렉토리 구조, 코딩 컨벤션, 빌드 방법 등)를 자동으로 이해합니다. 사용자별(`~/.claude/CLAUDE.md`), 프로젝트별, 디렉토리별로 계층적 설정이 가능합니다.
{% endhint %}

---

## 4. Computer Use -- 데스크톱 제어 Agent

### 개요

2024년 10월 베타 출시된 Computer Use는 **최초의 프론티어 모델 데스크톱 제어** 기능입니다. 스크린샷을 분석하고, 마우스 클릭과 키보드 입력을 수행하여 사람처럼 컴퓨터를 조작합니다.

### 작동 원리

```
                     반복 루프
         ┌──────────────────────────┐
         │                          │
         ▼                          │
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ Screenshot│───►│ Analyze  │───►│  Act     │
  │ (화면 캡처)│    │ (요소 파악)│    │ (클릭/   │
  │          │    │          │    │  타이핑)  │
  └──────────┘    └──────────┘    └──────────┘
```

| 단계 | 설명 |
|------|------|
| **Screenshot** | 현재 화면을 이미지로 캡처 |
| **Analyze** | Claude의 비전 능력으로 UI 요소, 텍스트, 버튼 위치 파악 |
| **Act** | 좌표 기반 마우스 이동/클릭, 키보드 입력 수행 |
| **Verify** | 결과 스크린샷으로 성공 여부 확인 후 다음 단계 진행 |

### 활용 시나리오

| 시나리오 | 설명 |
|---------|------|
| **레거시 시스템 자동화** | API가 없는 오래된 웹/데스크톱 앱 조작 |
| **UI 테스트** | 스크린샷 기반 E2E 테스트 자동화 |
| **데이터 수집** | 웹 브라우저를 통한 복잡한 데이터 수집 작업 |
| **RPA 대체** | 기존 RPA 도구보다 유연한 자동화 |

{% hint style="warning" %}
**주의사항**: Computer Use는 아직 Beta 상태입니다. 프로덕션 환경에서는 샌드박스(가상 머신, Docker 컨테이너) 내에서 실행하는 것을 권장합니다. 민감한 정보가 표시된 화면에서는 사용을 제한해야 합니다.
{% endhint %}

### macOS 통합

2025년 이후 macOS 네이티브 통합이 추가되었습니다. Accessibility API를 활용해 스크린샷 없이도 UI 요소에 직접 접근할 수 있어, 속도와 정확도가 크게 향상되었습니다.

---

## 5. Agent SDK -- 프로그래밍 가능한 Claude Code

### 개요

2025년 9월 베타 출시된 Agent SDK는 **Claude Code가 내부에서 사용하는 것과 동일한 도구 세트**를 Python과 TypeScript에서 프로그래밍 방식으로 사용할 수 있게 해줍니다.

{% hint style="info" %}
**핵심 차이점**: Claude Code는 "사람이 터미널에서 대화하며 사용", Agent SDK는 "프로그래머가 코드로 Agent를 구축"하는 데 사용합니다. 내부 엔진은 동일합니다.
{% endhint %}

### 핵심 기능

| 기능 | 설명 |
|------|------|
| **Claude Code 동일 도구** | Read, Edit, Bash, Grep, Glob 등 파일 시스템 도구 내장 |
| **MCP 통합** | MCP 서버를 코드로 연결하여 도구 확장 |
| **Structured Outputs** | Agent 출력을 JSON Schema로 구조화 |
| **1M 컨텍스트** | 100만 토큰 컨텍스트 윈도우 활용 |
| **Streaming** | 실시간 토큰 스트리밍 지원 |
| **비동기 실행** | async/await 패턴으로 병렬 Agent 실행 |

### Python 사용 예시

```python
from anthropic_agent import Agent, Tool
from anthropic_agent.tools import Read, Edit, Bash, Grep

# Agent 생성
agent = Agent(
    model="claude-opus-4-6",
    tools=[Read(), Edit(), Bash(), Grep()],
    system_prompt="당신은 시니어 백엔드 엔지니어입니다.",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 4096}
)

# MCP 서버 연결
agent.add_mcp_server(
    name="databricks",
    command="npx",
    args=["@anthropic/mcp-databricks"]
)

# Agent 실행
result = await agent.run(
    "src/ 디렉토리에서 SQL 인젝션 취약점을 찾아서 수정하고, "
    "수정 전후 diff를 보여줘."
)

# Structured Output
from pydantic import BaseModel

class SecurityReport(BaseModel):
    vulnerabilities: list[dict]
    fixes_applied: list[str]
    risk_level: str

result = await agent.run(
    "보안 취약점 분석 보고서를 작성해줘.",
    output_schema=SecurityReport
)
```

### Claude Code vs Agent SDK 비교

| 항목 | Claude Code | Agent SDK |
|------|-------------|-----------|
| **인터페이스** | 터미널 대화형 | 프로그래밍 API |
| **사용자** | 개발자 (직접 사용) | 개발자 (Agent 구축) |
| **사용 사례** | 코딩, 디버깅, PR 작성 | 커스텀 Agent 빌드, 자동화 파이프라인 |
| **MCP** | 설정 파일로 연결 | 코드로 연결 |
| **배포** | 로컬 터미널 | 서버, 클라우드, 컨테이너 |
| **확장성** | 단일 사용자 | 멀티테넌트, 스케일아웃 가능 |

---

## 6. Claude 4 모델 패밀리

### 모델 라인업

Claude 4 세대는 두 가지 라인으로 구분됩니다: **Opus** (최고 성능)와 **Sonnet** (효율성).

| 모델 | 출시 | 특징 | 주요 용도 |
|------|------|------|----------|
| **Opus 4** | 2025.05 | 7시간 자율 작업, 최강 코딩 | 복잡한 코딩, 장기 Agent 작업 |
| **Sonnet 4** | 2025.05 | Opus 대비 빠른 응답, 비용 효율 | 일상적 코딩, 분석 |
| **Sonnet 4.5** | 2025 H2 | Sonnet 라인 성능 향상 | 범용 작업 |
| **Opus 4.5** | 2025 H2 | Opus 라인 성능 향상 | 고급 추론 |
| **Opus 4.6** | 2026 | 최신 플래그십, 1M 컨텍스트 | Claude Code 기본 모델 |
| **Sonnet 4.6** | 2026 | 최신 효율 모델 | 대규모 배포, API 서비스 |

### Opus 4의 7시간 자율 작업

{% hint style="success" %}
**획기적 벤치마크**: Opus 4는 SWE-bench에서 72.5%를 기록하며, 단일 프롬프트로 최대 7시간 동안 자율적으로 코딩 작업을 수행할 수 있습니다. 이는 "하루 종일 코딩하는 주니어 개발자" 수준의 자율성입니다.
{% endhint %}

| 능력 | 상세 |
|------|------|
| **장기 작업** | 단일 프롬프트로 7시간 연속 작업 |
| **자가 수정** | 테스트 실패 시 스스로 코드 수정 후 재실행 |
| **컨텍스트 유지** | 장시간 작업에서도 초기 목표와 컨텍스트 유지 |
| **도구 체이닝** | 파일 읽기 → 분석 → 수정 → 테스트 → 커밋의 전체 사이클 |

### Hybrid Reasoning (하이브리드 추론)

Claude 4 패밀리의 핵심 혁신은 **Interleaved Thinking with Tool Use**입니다. 기존 모델이 "생각 → 도구 호출 → 응답"의 선형 구조였다면, Claude 4는 도구를 사용하면서 동시에 사고를 이어갑니다.

```
기존 모델:
  [생각] ──► [도구 호출] ──► [결과 수신] ──► [생각] ──► [응답]

Claude 4 (Interleaved):
  [생각 + 도구 호출] ──► [결과 수신 + 생각 계속] ──► [추가 도구 + 생각] ──► [응답]
```

이 방식의 장점:
- 도구 결과를 기다리는 동안에도 다음 단계를 미리 계획
- 여러 도구를 병렬로 호출하면서 중간 결과를 실시간 반영
- 전체 작업 완료 시간 단축

---

## 7. Advanced Tool Use -- 도구 사용의 진화

### Tool Search Tool

수천 개의 MCP 도구가 연결된 환경에서, 모델이 적절한 도구를 **검색**하여 찾는 메타 도구입니다.

| 특징 | 설명 |
|------|------|
| **문제** | 수천 개 도구를 모두 프롬프트에 넣으면 토큰 낭비 + 혼란 |
| **해결** | Tool Search Tool이 사용자 요청을 분석하여 관련 도구만 검색 |
| **방식** | 도구 이름, 설명, 파라미터를 인덱싱하고 시맨틱 검색 수행 |

```
사용자: "Databricks에서 테이블 목록을 보여줘"
  │
  ▼
Tool Search Tool: "databricks table list" 검색
  │
  ▼
결과: [execute_sql, get_table_details, manage_uc_objects]
  │
  ▼
Claude: execute_sql("SHOW TABLES IN catalog.schema") 호출
```

### Programmatic Tool Calling

모델이 JSON Schema 기반으로 도구를 호출하고, 결과를 구조화된 형태로 받는 표준 방식입니다.

```json
{
  "type": "tool_use",
  "name": "execute_sql",
  "input": {
    "query": "SELECT * FROM sales.orders LIMIT 10",
    "warehouse_id": "abc123"
  }
}
```

### Server Tools (빌트인 도구)

Anthropic이 서버 사이드에서 제공하는 도구로, 사용자 인프라 없이 바로 사용 가능합니다.

| 도구 | 기능 | 활용 |
|------|------|------|
| **web_search** | 실시간 웹 검색 | 최신 정보 조회, 팩트 체크 |
| **code_execution** | 샌드박스 Python 실행 | 데이터 분석, 시각화, 계산 |
| **web_fetch** | 웹 페이지 콘텐츠 가져오기 | 문서 읽기, API 응답 확인 |

{% hint style="info" %}
**Server Tools의 의미**: RAG나 외부 API 연동 없이도 Claude가 자체적으로 정보를 검색하고, 코드를 실행하고, 웹 콘텐츠를 가져올 수 있습니다. 특히 `code_execution`은 데이터 분석 작업에서 hallucination을 크게 줄여줍니다.
{% endhint %}

---

## 8. Extended Thinking (Adaptive Thinking)

### 개요

2025년 2월 도입된 Extended Thinking은 Claude가 **응답하기 전에 깊이 생각하는 과정**을 활성화합니다. 현재는 **Adaptive Thinking**으로 브랜딩되어, 작업 복잡도에 따라 사고 깊이를 자동 조절합니다.

### 작동 방식

```python
# API 호출 시 thinking 파라미터로 제어
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16384,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000   # 사고에 사용할 최대 토큰
    },
    messages=[{
        "role": "user",
        "content": "이 시스템의 보안 취약점을 분석하고 개선안을 제시해줘."
    }]
)

# 응답 구조
# response.content = [
#     {"type": "thinking", "thinking": "먼저 입력을 분석하면... (사고 과정)"},
#     {"type": "text", "text": "분석 결과... (최종 응답)"}
# ]
```

### 핵심 특징

| 특징 | 설명 |
|------|------|
| **Configurable Budget** | `budget_tokens`로 사고 깊이 조절 (1K ~ 128K) |
| **Interleaved with Tool Use** | 도구를 사용하면서 동시에 사고를 이어감 |
| **Adaptive** | 간단한 질문에는 짧게, 복잡한 문제에는 깊게 생각 |
| **투명성** | `thinking` 블록에서 사고 과정을 확인 가능 |

### 언제 사용하는가?

| 상황 | Extended Thinking | 일반 응답 |
|------|:-:|:-:|
| 복잡한 수학/논리 문제 | O | |
| 장문 코드 분석/디버깅 | O | |
| 다단계 추론이 필요한 작업 | O | |
| 간단한 Q&A | | O |
| 번역, 요약 | | O |
| 실시간 채팅 (낮은 지연 필요) | | O |

{% hint style="warning" %}
**비용 고려**: Extended Thinking의 사고 토큰도 과금 대상입니다. `budget_tokens`를 적절히 설정하여 비용과 품질의 균형을 맞추세요. 일반적으로 코딩 작업에는 4K~8K, 복잡한 분석에는 10K~32K를 권장합니다.
{% endhint %}

---

## 9. 멀티에이전트 패턴 (5가지 상세)

Anthropic은 2024년 12월 블로그에서 5가지 Agent 설계 패턴을 제시했습니다. 핵심 메시지는 "**단순하게 시작하라(Start Simple)**"입니다.

{% hint style="success" %}
**Anthropic의 철학**: "Agent를 만들 때 가장 흔한 실수는 처음부터 복잡한 멀티에이전트 시스템을 설계하는 것입니다. 대부분의 문제는 단일 LLM 호출 + 좋은 프롬프트로 해결됩니다. 복잡한 패턴은 단순한 접근이 한계에 부딪힐 때만 도입하세요."
{% endhint %}

### 패턴 1: Prompt Chaining (프롬프트 체이닝)

**하나의 작업을 여러 순차 단계로 분해**하여, 각 단계의 출력이 다음 단계의 입력이 되는 패턴입니다.

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Step 1  │────►│  Gate /  │────►│  Step 2  │────►│  Step 3  │
│  (생성)   │     │  Check   │     │  (변환)   │     │  (검증)   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                     │
                     │ 실패 시
                     ▼
               ┌──────────┐
               │  재시도 /  │
               │  에러 처리 │
               └──────────┘
```

| 항목 | 설명 |
|------|------|
| **적용 시기** | 작업을 명확한 순서의 하위 작업으로 분해할 수 있을 때 |
| **장점** | 각 단계의 품질을 독립적으로 검증 가능 |
| **단점** | 전체 지연 시간 증가 (직렬 실행) |
| **게이트/체크** | 각 단계 사이에 품질 검증 로직 삽입 가능 |

**실전 예시: 마케팅 콘텐츠 생성**

```
Step 1: 주제 키워드로 아웃라인 생성
  → Gate: 아웃라인에 필수 섹션 포함 여부 확인
Step 2: 아웃라인 기반으로 초안 작성
  → Gate: 글자 수, 톤 확인
Step 3: 초안을 한국어로 번역
Step 4: SEO 최적화 적용
```

### 패턴 2: Routing (라우팅)

**입력을 분류하여 전문화된 처리 경로로 분배**하는 패턴입니다.

```
                    ┌──────────────────┐
                    │    Router LLM    │
                    │  (입력 분류기)     │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │ Handler A │   │ Handler B │   │ Handler C │
       │ (코드 질문)│   │ (일반 Q&A)│   │ (데이터   │
       │           │   │           │   │  분석)    │
       └──────────┘   └──────────┘   └──────────┘
```

| 항목 | 설명 |
|------|------|
| **적용 시기** | 입력 유형에 따라 다른 처리가 필요할 때 |
| **장점** | 각 핸들러를 전문화하여 품질 향상 |
| **단점** | 라우팅 오류 시 잘못된 핸들러로 전달 |
| **구현** | LLM 분류기 또는 규칙 기반 분류 |

**실전 예시: 고객 지원 시스템**

```
Router: 고객 문의 유형 분류
  → "결제 문제"  → 결제 전문 Agent (PG사 API 연동)
  → "기술 지원"  → 기술 지원 Agent (RAG + 문서 검색)
  → "일반 문의"  → FAQ Agent (간단한 응답)
  → "해지 요청"  → 리텐션 Agent (맞춤 제안)
```

### 패턴 3: Parallelization (병렬화)

**하나의 작업을 독립적인 하위 작업으로 분해하여 동시 실행** 후 결과를 집계하는 패턴입니다. 두 가지 변형이 있습니다.

```
                         ┌──────────┐
                         │ Splitter │
                         └────┬─────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
       ┌──────────┐    ┌──────────┐    ┌──────────┐
       │ Worker A  │    │ Worker B  │    │ Worker C  │
       │ (보안 검토)│    │ (성능 검토)│    │ (코드 품질)│
       └─────┬────┘    └─────┬────┘    └─────┬────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                         ┌────▼─────┐
                         │Aggregator│
                         │ (결과 병합)│
                         └──────────┘
```

**변형 A: Sectioning (분할)**
- 같은 입력을 여러 관점에서 동시에 처리
- 예: 코드 리뷰 시 보안/성능/코드 품질을 각각 다른 Agent가 동시에 검토

**변형 B: Voting (투표)**
- 같은 작업을 여러 Agent가 독립적으로 수행하고 다수결
- 예: 콘텐츠 모더레이션에서 3개 Agent가 독립 판단 후 2/3 이상 동의 시 차단

| 항목 | 설명 |
|------|------|
| **적용 시기** | 하위 작업이 서로 독립적이거나, 신뢰도를 높여야 할 때 |
| **장점** | 처리 시간 단축 (병렬), 정확도 향상 (투표) |
| **단점** | 비용 증가 (LLM 호출 횟수 증가) |
| **집계 방식** | 병합(merge), 투표(vote), 가중 평균(weighted avg) |

**실전 예시: 코드 리뷰 자동화**

```python
import asyncio

async def parallel_code_review(code: str):
    # 세 가지 관점에서 동시 리뷰
    security, performance, style = await asyncio.gather(
        review_security(code),      # 보안 취약점 검토
        review_performance(code),   # 성능 이슈 검토
        review_code_style(code)     # 코드 스타일 검토
    )
    # 결과 병합
    return aggregate_reviews(security, performance, style)
```

### 패턴 4: Orchestrator-Workers (오케스트레이터-워커)

**중앙 오케스트레이터가 작업을 동적으로 분해하고 워커에게 할당**하는 패턴입니다. Parallelization과 달리, 하위 작업이 사전에 정해져 있지 않고 오케스트레이터가 실시간으로 결정합니다.

```
                    ┌───────────────────┐
                    │   Orchestrator    │
                    │  (작업 분해 & 할당) │
                    └────────┬──────────┘
                             │ 동적 할당
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │ Worker 1  │   │ Worker 2  │   │ Worker 3  │
       │ (검색)    │   │ (코드 수정)│   │ (테스트)  │
       └─────┬────┘   └─────┬────┘   └─────┬────┘
              │              │              │
              └──────────────┼──────────────┘
                             │ 결과 보고
                    ┌────────▼──────────┐
                    │   Orchestrator    │
                    │  (결과 종합 & 판단) │
                    └───────────────────┘
                             │
                    필요 시 추가 작업 할당
```

| 항목 | 설명 |
|------|------|
| **적용 시기** | 작업 복잡도가 높고, 하위 작업을 미리 예측할 수 없을 때 |
| **장점** | 유연성 극대화, 복잡한 문제에 적응적 대응 |
| **단점** | 오케스트레이터의 판단 품질에 의존, 비용 높음 |
| **핵심** | 오케스트레이터는 "무엇을 해야 하는지"를, 워커는 "어떻게 하는지"를 담당 |

**실전 예시: 대규모 리팩토링**

```
사용자: "이 프로젝트의 인증 시스템을 JWT에서 OAuth2로 마이그레이션해줘"

Orchestrator 판단:
  1. 현재 JWT 사용 위치 파악 → Worker 1 (코드 검색)
  2. OAuth2 설정 파일 생성 → Worker 2 (코드 생성)
  3. 인증 미들웨어 수정 → Worker 3 (코드 수정)
  4. 기존 테스트 수정 → Worker 4 (테스트)
  5. Worker 1 결과에 따라 추가 워커 동적 할당
```

{% hint style="info" %}
**Claude Code의 Subagent가 바로 이 패턴입니다.** Claude Code가 복잡한 작업을 받으면, 메인 Agent(Orchestrator)가 하위 Agent(Worker)를 생성하여 병렬로 작업을 수행합니다.
{% endhint %}

### 패턴 5: Evaluator-Optimizer (평가자-최적화자)

**하나의 Agent가 결과를 생성하고, 다른 Agent가 평가하여 개선을 반복**하는 패턴입니다.

```
              ┌──────────────────────────────────┐
              │            반복 루프               │
              │                                   │
              │  ┌──────────┐    ┌──────────────┐ │
              │  │ Generator│───►│  Evaluator   │ │
              │  │ (생성자)  │    │  (평가자)     │ │
              │  └─────▲────┘    └──────┬───────┘ │
              │        │               │          │
              │        │   피드백       │ 합격/불합격│
              │        └───────────────┘          │
              └──────────────────────────────────┘
                                       │
                                  합격 시 종료
                                       │
                                       ▼
                                  ┌──────────┐
                                  │ 최종 결과  │
                                  └──────────┘
```

| 항목 | 설명 |
|------|------|
| **적용 시기** | 명확한 품질 기준이 있고, 반복 개선이 가능한 작업 |
| **장점** | 결과 품질을 체계적으로 향상 |
| **단점** | 반복 횟수에 따라 비용/시간 증가 |
| **종료 조건** | 품질 기준 충족, 최대 반복 횟수, 개선 없음 |

**실전 예시: SQL 최적화**

```
Generator: 사용자 요청 기반 SQL 쿼리 생성
  "SELECT * FROM orders JOIN customers ON ..."

Evaluator: 쿼리 품질 평가
  - EXPLAIN PLAN 실행 → Full Table Scan 발견
  - 인덱스 사용 여부 확인
  - 쿼리 복잡도 점수 계산
  - 피드백: "customers 테이블에 인덱스 활용하도록 JOIN 순서 변경 필요"

Generator (2차): 피드백 반영하여 쿼리 수정
  "SELECT ... FROM customers c JOIN orders o ON ... WHERE ..."

Evaluator (2차): 재평가
  - Index Seek 확인, 실행 계획 개선 확인
  - 합격 → 최종 결과 반환
```

### 5가지 패턴 비교 요약

| 패턴 | 복잡도 | 적용 시점 | 핵심 특징 |
|------|:------:|---------|---------|
| **Prompt Chaining** | 낮음 | 순차적 작업 분해 가능 시 | 단계별 품질 게이트 |
| **Routing** | 낮음 | 입력 유형별 전문 처리 필요 시 | 분류 → 전문 핸들러 |
| **Parallelization** | 중간 | 독립 작업 동시 처리 or 신뢰도 향상 | 동시 실행 → 결과 집계 |
| **Orchestrator-Workers** | 높음 | 동적 작업 분해 필요 시 | 중앙 제어 + 유연한 워커 |
| **Evaluator-Optimizer** | 높음 | 반복 개선으로 품질 보장 필요 시 | 생성 → 평가 → 피드백 루프 |

{% hint style="warning" %}
**선택 가이드**: "단순한 것이 최선이다"를 원칙으로 삼으세요.
- **90%의 경우**: 단일 LLM 호출 + 좋은 프롬프트로 충분
- **나머지 9%**: Prompt Chaining 또는 Routing으로 해결
- **1%의 복잡한 경우**: Orchestrator-Workers 또는 Evaluator-Optimizer 도입
{% endhint %}

---

## 10. Claude Cowork -- 지식 노동자 Agent

2026년 1월 프리뷰로 공개된 Claude Cowork는 Claude Code가 개발자를 위한 Agent라면, **지식 노동자(마케터, 분석가, PM 등)**를 위한 Agent입니다.

| 특징 | 설명 |
|------|------|
| **목적** | 비개발자가 자연어로 복잡한 업무 자동화 |
| **인터페이스** | 웹 기반, 대화형 |
| **핵심 능력** | 문서 작성, 데이터 분석, 리서치, 보고서 생성 |
| **MCP 연동** | Google Workspace, Notion, Slack 등 업무 도구 연결 |
| **상태** | Preview (2026.01~) |

---

## 11. Databricks 시사점

### Claude on Databricks -- 세 가지 경로

Databricks 환경에서 Claude를 활용하는 방법은 세 가지입니다.

| 경로 | 방식 | 장점 | 고려사항 |
|------|------|------|---------|
| **Foundation Model APIs** | Databricks가 호스팅하는 Claude 엔드포인트 | Unity Catalog 거버넌스, 네트워크 격리 | 모델 버전 업데이트 지연 가능 |
| **Amazon Bedrock** | AWS 기반 Claude 접근 | AWS 인프라 활용, 최신 모델 빠른 접근 | 별도 Bedrock 설정 필요 |
| **Anthropic API 직접** | anthropic Python SDK 사용 | 최신 기능 즉시 사용 가능 | 네트워크 정책 확인 필요 |

### Foundation Model APIs 활용

```python
# Databricks 노트북에서 Claude 사용
from databricks.sdk import WorkspaceClient
import anthropic

# Foundation Model APIs를 통한 호출
w = WorkspaceClient()
response = w.serving_endpoints.query(
    name="databricks-claude-sonnet-4",
    messages=[{
        "role": "user",
        "content": "Unity Catalog에서 테이블 권한을 설정하는 SQL을 작성해줘."
    }],
    max_tokens=4096
)
```

### MCP + Genie Code 통합

Genie Code는 MCP Host 역할을 수행합니다. Databricks MCP Server를 연결하면, Genie Code에서 자연어로 Databricks 리소스를 관리할 수 있습니다.

```
┌────────────┐     MCP      ┌────────────────────┐     ┌──────────────┐
│ Genie Code │ ◄──────────► │ Databricks MCP     │────►│ Unity Catalog│
│ (MCP Host) │              │ Server             │────►│ SQL Warehouse│
│            │              │                    │────►│ Jobs/Workflows│
└────────────┘              └────────────────────┘     └──────────────┘
```

| 시나리오 | MCP + Genie Code 활용 |
|---------|---------------------|
| **데이터 탐색** | "sales 카탈로그에서 주문 관련 테이블을 찾아줘" |
| **쿼리 실행** | "지난 달 매출 상위 10개 제품을 조회해줘" |
| **파이프라인 관리** | "ETL 파이프라인 상태를 확인하고 실패한 것을 재실행해줘" |
| **거버넌스** | "이 테이블에 데이터 팀 읽기 권한을 부여해줘" |

### Agent Bricks에서 Claude 활용

Databricks Agent Bricks(Knowledge Assistant, Genie Agent, Supervisor)에서도 Claude를 LLM 백엔드로 사용할 수 있습니다.

```python
# Agent Bricks에서 Claude 모델 지정
from databricks.agents import KnowledgeAssistant

ka = KnowledgeAssistant(
    name="hr-assistant",
    model="databricks-claude-sonnet-4",  # Claude 모델 지정
    vector_search_index="hr_docs_index",
    instructions="당신은 HR 관련 질문에 답변하는 어시스턴트입니다."
)
```

{% hint style="info" %}
**Databricks에서의 베스트 프랙티스**
- **거버넌스가 중요한 경우**: Foundation Model APIs를 통해 Unity Catalog 거버넌스 적용
- **최신 모델이 필요한 경우**: Bedrock 또는 Anthropic API 직접 사용
- **Agent 개발**: Agent SDK + Databricks MCP Server 조합으로 데이터 플랫폼 연동 Agent 구축
- **비개발자 분석**: Genie Code + MCP로 자연어 데이터 분석
{% endhint %}

---

## 12. 고객 FAQ

### Q1. Claude Code와 GitHub Copilot의 차이는?

| 항목 | Claude Code | GitHub Copilot |
|------|-------------|----------------|
| **패러다임** | Agent (자율 실행) | Assistant (코드 제안) |
| **인터페이스** | 터미널 | IDE 내장 |
| **작업 단위** | 전체 기능 구현 ~ PR 생성 | 줄/블록 단위 코드 완성 |
| **도구 사용** | 파일 시스템, Git, MCP 등 | 제한적 |
| **자율성** | 높음 (스스로 테스트/수정) | 낮음 (사람이 수락/거부) |

### Q2. MCP와 OpenAI의 Function Calling은 어떻게 다른가?

| 항목 | MCP | Function Calling |
|------|-----|-----------------|
| **범위** | 프로토콜 (표준) | API 기능 (벤더 종속) |
| **호환성** | 모든 LLM에서 사용 가능 | OpenAI API 전용 |
| **서버 생태계** | 10,000+ 커뮤니티 서버 | 개발자가 직접 구현 |
| **거버넌스** | Linux Foundation (AAIF) | OpenAI 단독 |
| **현재 상태** | OpenAI도 MCP 채택 | MCP와 공존 |

### Q3. Opus 4와 Sonnet 4, 어떤 것을 사용해야 하나?

| 상황 | 추천 모델 |
|------|---------|
| 복잡한 코딩, 장기 Agent 작업 | **Opus 4.6** |
| 일상적 코딩, 분석, 대화 | **Sonnet 4.6** |
| 대규모 API 서비스 (비용 민감) | **Sonnet 4.6** |
| 최고 품질 필요 (비용 무관) | **Opus 4.6 + Extended Thinking** |

### Q4. Computer Use를 프로덕션에서 사용해도 되나?

현재 Beta 상태이므로 프로덕션에서는 다음 조건 하에 제한적으로 사용을 권장합니다:
- **샌드박스 환경**: Docker 컨테이너 또는 VM 내에서 실행
- **제한된 권한**: 최소 권한 원칙 적용
- **민감 정보 차단**: 비밀번호, 개인정보가 표시된 화면에서 사용 금지
- **사람 승인**: 중요한 액션 전 사람의 확인을 받는 워크플로 설계

### Q5. Anthropic과 Databricks의 관계는?

| 항목 | 내용 |
|------|------|
| **모델 제공** | Claude가 Foundation Model APIs, Bedrock을 통해 Databricks에서 사용 가능 |
| **MCP 호환** | Databricks가 공식 MCP Server를 제공, Genie Code가 MCP Host |
| **Agent 생태계** | Agent Bricks에서 Claude를 LLM 백엔드로 선택 가능 |
| **경쟁/협력** | AI 모델 계층에서는 경쟁(DBRX vs Claude), 플랫폼 계층에서는 협력 |

---

## 13. 참고 자료

| 자료 | 링크 |
|------|------|
| Anthropic 공식 문서 | [docs.anthropic.com](https://docs.anthropic.com) |
| MCP 공식 사이트 | [modelcontextprotocol.io](https://modelcontextprotocol.io) |
| Claude Code 문서 | [docs.anthropic.com/en/docs/claude-code](https://docs.anthropic.com/en/docs/claude-code) |
| Building Effective Agents (블로그) | [anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents) |
| Agent SDK 문서 | [docs.anthropic.com/en/docs/agent-sdk](https://docs.anthropic.com/en/docs/agent-sdk) |
| Computer Use 문서 | [docs.anthropic.com/en/docs/computer-use](https://docs.anthropic.com/en/docs/computer-use) |
| Extended Thinking 가이드 | [docs.anthropic.com/en/docs/extended-thinking](https://docs.anthropic.com/en/docs/extended-thinking) |
| AAIF (Linux Foundation) | [ai-alliance-interop.org](https://ai-alliance-interop.org) |
| Databricks MCP Server | [github.com/databricks/databricks-mcp](https://github.com/databricks/databricks-mcp) |
| Databricks Foundation Model APIs | [docs.databricks.com/machine-learning/foundation-models](https://docs.databricks.com/machine-learning/foundation-models) |
