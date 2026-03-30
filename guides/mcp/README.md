# MCP (Model Context Protocol)

## MCP란 무엇인가?

MCP(Model Context Protocol)는 **Anthropic이 2024년 11월에 발표한 오픈소스 프로토콜**로, AI 애플리케이션이 외부 도구, 데이터 소스, 워크플로에 접근하기 위한 **범용 표준 인터페이스**입니다.

USB-C가 다양한 전자기기를 하나의 규격으로 연결하듯, MCP는 AI 애플리케이션과 외부 시스템을 **하나의 표준으로 연결**합니다.

{% hint style="info" %}
MCP는 특정 벤더에 종속되지 않는 오픈 프로토콜입니다. Claude, ChatGPT, VS Code Copilot, Cursor, Databricks Genie Code 등 다양한 AI 클라이언트가 MCP를 지원합니다.
{% endhint %}

---

## 왜 MCP가 필요한가?

기존에는 AI 에이전트가 외부 시스템에 접근하려면, 각 시스템마다 **개별 통합 코드**를 작성해야 했습니다. N개의 AI 앱이 M개의 외부 시스템과 통합하려면 **N x M개의 커넥터**가 필요했습니다.

MCP는 이 문제를 해결합니다:

| 기존 방식 | MCP 방식 |
|----------|---------|
| AI 앱마다 각 시스템별 커스텀 통합 | 표준 프로토콜로 한 번만 구현 |
| N x M개의 커넥터 필요 | N + M개의 구현으로 충분 |
| 인증, 에러 처리 등 매번 재구현 | 프로토콜 레벨에서 표준화 |
| 벤더 종속 | 오픈 표준, 어떤 AI 앱에서든 재사용 |

---

## MCP 아키텍처

MCP는 **Host - Client - Server** 3계층 아키텍처를 따릅니다:

```
┌─────────────────────────────────────────┐
│  MCP Host (예: Claude Desktop, Genie Code) │
│                                         │
│  ┌─────────────┐  ┌─────────────┐      │
│  │ MCP Client  │  │ MCP Client  │      │
│  └──────┬──────┘  └──────┬──────┘      │
└─────────┼────────────────┼──────────────┘
          │                │
   ┌──────▼──────┐  ┌─────▼───────┐
   │ MCP Server  │  │ MCP Server  │
   │ (GitHub)    │  │ (Slack)     │
   └─────────────┘  └─────────────┘
```

| 참여자 | 역할 | 예시 |
|--------|------|------|
| **Host** | AI 애플리케이션. 하나 이상의 Client를 관리 | Claude Desktop, Genie Code, Cursor, VS Code |
| **Client** | Server와의 1:1 연결을 유지하며 컨텍스트 획득 | Host 내부에서 자동 생성 |
| **Server** | 도구, 리소스, 프롬프트를 외부에 노출하는 프로그램 | GitHub MCP, Slack MCP, PostgreSQL MCP |

---

## 3가지 프리미티브

MCP 서버는 세 가지 유형의 기능을 제공할 수 있습니다:

| 프리미티브 | 설명 | 누가 제어하는가 | 예시 |
|-----------|------|---------------|------|
| **Tools** | LLM이 호출하는 실행 가능한 함수 | LLM이 판단하여 호출 | 파일 검색, API 호출, DB 쿼리, 메시지 전송 |
| **Resources** | 컨텍스트를 제공하는 데이터 소스 | 클라이언트/사용자가 선택 | 파일 내용, DB 레코드, API 응답 |
| **Prompts** | 재사용 가능한 프롬프트 템플릿 | 사용자가 선택 | 코드 리뷰 템플릿, 분석 프롬프트 |

{% hint style="tip" %}
실무에서 가장 많이 사용되는 프리미티브는 **Tools**입니다. AI 에이전트가 자율적으로 외부 시스템의 함수를 호출할 수 있게 해주는 핵심 기능입니다.
{% endhint %}

---

## 통신 방식

MCP는 **JSON-RPC 2.0** 기반이며, 두 가지 전송 메커니즘을 지원합니다:

| 전송 방식 | 설명 | 사용 환경 |
|----------|------|----------|
| **stdio** | 표준 입출력 스트림을 통한 로컬 프로세스 통신 | 로컬 개발 (Claude Desktop, Claude Code) |
| **Streamable HTTP** | HTTP POST + Server-Sent Events | 원격 서버 통신 (Databricks, 클라우드 배포) |

- **stdio**: MCP 서버를 로컬 프로세스로 실행하고, stdin/stdout으로 통신합니다. 설정이 간단하며 로컬 개발에 적합합니다.
- **Streamable HTTP**: 원격 서버에 HTTP로 요청을 보내고 SSE(Server-Sent Events)로 응답을 받습니다. 프로덕션 배포에 적합합니다.

---

## MCP vs REST API

"기존 REST API가 있는데 왜 MCP가 필요하지?"라는 질문에 대한 답입니다:

| 비교 항목 | REST API | MCP |
|----------|---------|-----|
| 대상 사용자 | 개발자가 코드로 호출 | AI가 자율적으로 호출 |
| 도구 발견 | 문서를 읽고 개발자가 구현 | `tools/list`로 자동 발견 |
| 스키마 | OpenAPI 등 별도 문서 | 프로토콜에 스키마 내장 |
| 인증 | 앱마다 개별 구현 | 프로토콜 레벨에서 표준화 |
| 양방향 통신 | 요청-응답만 가능 | SSE로 실시간 스트리밍 가능 |

{% hint style="info" %}
MCP는 REST API를 **대체**하는 것이 아니라, AI 에이전트가 기존 API를 **쉽게 사용할 수 있도록 감싸는(wrapping)** 표준입니다. 대부분의 MCP 서버는 내부적으로 REST API를 호출합니다.
{% endhint %}

---

## MCP vs A2A (Agent-to-Agent)

MCP와 Google이 발표한 A2A 프로토콜은 **보완적 관계**입니다:

| 비교 항목 | MCP | A2A |
|----------|-----|-----|
| 목적 | 에이전트가 **도구/데이터**에 접근 | **에이전트 간** 통신 |
| 비유 | 사람이 도구를 사용하는 것 | 사람과 사람이 대화하는 것 |
| 통신 대상 | 에이전트 → 도구/데이터 소스 | 에이전트 → 에이전트 |
| 활용 예시 | GitHub에서 코드 검색, DB 쿼리 | 여행 에이전트가 결제 에이전트에게 위임 |

---

## 현재 생태계

MCP는 빠르게 성장하는 생태계를 보유하고 있습니다:

- **수천 개의 MCP 서버**가 이미 오픈소스로 공개 (GitHub, Slack, Jira, Google Drive, PostgreSQL, Notion, Brave Search 등)
- **주요 AI 클라이언트 지원**: Claude Desktop, Claude Code, ChatGPT, VS Code Copilot, Cursor, Windsurf, Databricks Genie Code
- **서버 디렉토리**: [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers), [smithery.ai](https://smithery.ai), [mcp.so](https://mcp.so)

---

## 다음 단계

| 가이드 | 내용 |
|--------|------|
| [일반 MCP 설정](setup-general.md) | Claude Desktop, Claude Code, Cursor에서 MCP 서버 설정하기 |
| [Databricks MCP 활용](databricks-mcp.md) | Databricks 환경에서 Managed/External/Custom MCP 활용하기 |
| [베스트 프랙티스](best-practices.md) | 보안, Tool 설계, 에러 핸들링, 디버깅 팁 |
