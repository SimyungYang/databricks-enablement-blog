# MCP (Model Context Protocol)

## MCP란 무엇인가?

MCP(Model Context Protocol)는 **Anthropic이 2024년 11월에 발표한 오픈소스 프로토콜** 로, AI 애플리케이션이 외부 도구, 데이터 소스, 워크플로에 접근하기 위한 **범용 표준 인터페이스** 입니다.

USB-C가 다양한 전자기기를 하나의 규격으로 연결하듯, MCP는 AI 애플리케이션과 외부 시스템을 **하나의 표준으로 연결** 합니다.

{% hint style="info" %}
MCP는 특정 벤더에 종속되지 않는 오픈 프로토콜입니다. Claude, ChatGPT, VS Code Copilot, Cursor, Databricks Genie Code 등 다양한 AI 클라이언트가 MCP를 지원합니다.
{% endhint %}

### 왜 MCP가 AI의 미래인가

AI 에이전트가 실제 업무에서 가치를 창출하려면 **외부 세계와 상호작용** 해야 합니다. 아무리 뛰어난 LLM이라도, 이메일을 보내지 못하고, DB를 조회하지 못하고, 코드를 검색하지 못하면 실용적 가치가 제한됩니다. MCP는 이 "AI의 손과 발" 문제를 해결하는 **업계 표준** 으로 자리잡고 있습니다.

MCP의 전략적 중요성을 이해하기 위한 핵심 관점:

| 관점 | 설명 |
|------|------|
| **생태계 효과** | MCP 서버가 많아질수록 AI 에이전트의 활용 범위가 넓어지고, 활용 범위가 넓어질수록 더 많은 MCP 서버가 개발되는 **선순환 구조** |
| **개발 비용 절감** | 한 번 구현한 MCP 서버는 Claude, ChatGPT, Genie Code 등 **모든 MCP 호환 클라이언트** 에서 재사용 가능 |
| **벤더 독립성** | 특정 AI 벤더에 종속되지 않으므로, AI 클라이언트를 변경해도 MCP 서버 투자가 유지됨 |
| **보안 표준화** | 인증, 권한, 감사 로그 등 보안 관련 사항이 프로토콜 레벨에서 표준화 |

### AAIF(Linux Foundation) 기부의 의미

2025년 3월, Anthropic은 MCP를 **AAIF(AI Alliance Interoperability Framework)** 를 통해 **Linux Foundation에 기부** 했습니다. 이것은 단순한 오픈소스 공개가 아니라, **업계 전체의 표준으로 발전** 시키겠다는 의지의 표현입니다.

Linux Foundation 기부가 의미하는 것:

- **거버넌스 중립성**: Anthropic 단독이 아닌, 커뮤니티 전체가 프로토콜의 발전 방향을 결정
- **기업 신뢰**: Linux Foundation의 거버넌스 아래 있으므로, 대기업도 프로덕션 환경에 안심하고 채택 가능
- **장기 안정성**: 특정 기업의 사업 전략 변경에 프로토콜이 영향받지 않음
- **표준화 가속**: HTTP, JSON 같은 웹 표준처럼 MCP가 AI 에이전트 통신의 기본 인프라로 자리잡을 가능성

{% hint style="tip" %}
MCP가 Linux Foundation에 기부되었다는 것은, 기업이 MCP 기반 인프라에 투자해도 **장기적으로 안전** 하다는 신호입니다. 마치 Kubernetes가 CNCF에 기부된 후 업계 표준이 된 것과 유사한 경로를 밟고 있습니다.
{% endhint %}

### MCP 표준화 동향 (2025-2026)

MCP 생태계는 빠르게 성장하며 새로운 기능이 지속적으로 추가되고 있습니다:

| 시기 | 주요 발전 |
|------|----------|
| **2024.11** | Anthropic, MCP 최초 발표. Claude Desktop에서 첫 지원 |
| **2025.03** | Streamable HTTP 전송 방식 추가. 원격 서버 배포 가능 |
| **2025.03** | Linux Foundation 기부 발표 |
| **2025.Q2** | OpenAI(ChatGPT), Microsoft(Copilot)가 MCP 지원 발표 |
| **2025.H2** | Databricks, MCP를 플랫폼 레벨에서 통합 (Managed/External/Custom) |
| **2026.Q1** | 수천 개의 MCP 서버가 공개, 주요 SaaS 벤더들이 공식 MCP 서버 제공 |

이 동향에서 주목할 점은 **경쟁사를 포함한 업계 전체** 가 MCP를 채택하고 있다는 것입니다. 이는 MCP가 일시적 유행이 아니라 **지속적 표준** 이 될 가능성이 높음을 시사합니다.

---

## 왜 MCP가 필요한가?

기존에는 AI 에이전트가 외부 시스템에 접근하려면, 각 시스템마다 **개별 통합 코드** 를 작성해야 했습니다. N개의 AI 앱이 M개의 외부 시스템과 통합하려면 **N x M개의 커넥터** 가 필요했습니다.

이 "N x M 문제"는 실제로 업계에서 큰 고통이었습니다. 예를 들어, GitHub과 연동하는 코드를 Claude, ChatGPT, Cursor 각각에 대해 별도로 작성해야 했고, Slack 연동도 마찬가지였습니다. 5개 AI 앱과 10개 외부 시스템을 연동하려면 50개의 커스텀 통합이 필요했습니다. MCP는 이를 **15개(5+10)의 구현** 으로 줄입니다.

MCP는 이 문제를 해결합니다:

| 기존 방식 | MCP 방식 |
|----------|---------|
| AI 앱마다 각 시스템별 커스텀 통합 | 표준 프로토콜로 한 번만 구현 |
| N x M개의 커넥터 필요 | N + M개의 구현으로 충분 |
| 인증, 에러 처리 등 매번 재구현 | 프로토콜 레벨에서 표준화 |
| 벤더 종속 | 오픈 표준, 어떤 AI 앱에서든 재사용 |

---

## MCP 아키텍처

MCP는 **Host - Client - Server**3계층 아키텍처를 따릅니다:

| 계층 | 구성 요소 | 역할 |
|------|----------|------|
| **MCP Host** | Claude Desktop, Genie Code 등 | AI 애플리케이션 — 하나 이상의 MCP Client를 관리 |
| **MCP Client** | Host 내부에 자동 생성 | 각 MCP Server와 1:1 연결 유지 |
| **MCP Server** | GitHub MCP, Slack MCP 등 | 도구, 리소스, 프롬프트를 외부에 노출 |

| 참여자 | 역할 | 예시 |
|--------|------|------|
| **Host** | AI 애플리케이션. 하나 이상의 Client를 관리 | Claude Desktop, Genie Code, Cursor, VS Code |
| **Client** | Server와의 1:1 연결을 유지하며 컨텍스트 획득 | Host 내부에서 자동 생성 |
| **Server** | 도구, 리소스, 프롬프트를 외부에 노출하는 프로그램 | GitHub MCP, Slack MCP, PostgreSQL MCP |

**아키텍처 이해의 핵심 포인트**: Host-Client-Server의 관계에서 중요한 것은 **Client와 Server가 1:1로 연결** 된다는 점입니다. 하나의 Host(예: Claude Desktop)에서 GitHub, Slack, PostgreSQL 세 개의 MCP 서버를 사용하면, 내부에 세 개의 MCP Client가 생성되어 각각 독립적으로 연결을 유지합니다. 이 구조 덕분에 하나의 MCP 서버가 다운되어도 나머지 서버는 정상 동작합니다.

---

## 3가지 기본 구성 요소

MCP 서버는 세 가지 유형의 기능을 제공할 수 있습니다:

| 구성 요소 | 설명 | 누가 제어하는가 | 예시 |
|-----------|------|---------------|------|
| **Tools** | LLM이 호출하는 실행 가능한 함수 | LLM이 판단하여 호출 | 파일 검색, API 호출, DB 쿼리, 메시지 전송 |
| **Resources** | 컨텍스트를 제공하는 데이터 소스 | 클라이언트/사용자가 선택 | 파일 내용, DB 레코드, API 응답 |
| **Prompts** | 재사용 가능한 프롬프트 템플릿 | 사용자가 선택 | 코드 리뷰 템플릿, 분석 프롬프트 |

{% hint style="tip" %}
실무에서 가장 많이 사용되는 구성 요소는 **Tools** 입니다. AI 에이전트가 자율적으로 외부 시스템의 함수를 호출할 수 있게 해주는 핵심 기능입니다.
{% endhint %}

### 세 가지 구성 요소의 실전 사용 비율

실무에서 세 구성 요소의 사용 빈도는 크게 다릅니다:

| 구성 요소 | 실전 사용 비율 | 이유 |
|-----------|-------------|------|
| **Tools** | ~90% | AI 에이전트의 핵심 기능. 모든 자동화 워크플로의 기반 |
| **Resources** | ~8% | 컨텍스트 제공에 유용하지만, 많은 클라이언트에서 아직 완벽히 지원하지 않음 |
| **Prompts** | ~2% | 재사용 가능한 프롬프트는 유용하지만, 대부분의 클라이언트가 자체 프롬프트 관리 기능을 보유 |

따라서 MCP를 처음 학습할 때는 **Tools에 집중** 하는 것이 효율적입니다. Resources와 Prompts는 필요에 따라 나중에 학습해도 됩니다.

---

## 통신 방식

MCP는 **JSON-RPC 2.0** 기반이며, 두 가지 전송 메커니즘을 지원합니다:

| 전송 방식 | 설명 | 사용 환경 |
|----------|------|----------|
| **stdio** | 표준 입출력 스트림을 통한 로컬 프로세스 통신 | 로컬 개발 (Claude Desktop, Claude Code) |
| **Streamable HTTP** | HTTP POST + Server-Sent Events | 원격 서버 통신 (Databricks, 클라우드 배포) |

- **stdio**: MCP 서버를 로컬 프로세스로 실행하고, stdin/stdout으로 통신합니다. 설정이 간단하며 로컬 개발에 적합합니다.
- **Streamable HTTP**: 원격 서버에 HTTP로 요청을 보내고 SSE(Server-Sent Events)로 응답을 받습니다. 프로덕션 배포에 적합합니다.

**실전에서의 전송 방식 선택:**

| 시나리오 | 권장 방식 | 이유 |
|---------|----------|------|
| 개인 로컬 개발 (Claude Desktop, Claude Code) | **stdio** | 설정이 간단, 별도 서버 불필요, `npx`로 즉시 실행 |
| 팀 공유 MCP 서버 | **Streamable HTTP** | 중앙 서버에 배포하여 팀 전체가 접근 |
| Databricks Genie Code 연동 | **Streamable HTTP**(필수) | 원격 통신만 지원 |
| 프로덕션 환경 | **Streamable HTTP** | 로드밸런싱, 모니터링, 고가용성 구현 가능 |

{% hint style="info" %}
**중요**: 많은 오픈소스 MCP 서버가 stdio만 지원합니다. Databricks Genie Code에서 사용하려면 Streamable HTTP를 지원하는 서버를 선택하거나, Custom MCP 서버로 래핑해야 합니다. [인기 서버 & 활용 시나리오](popular-servers.md)에서 각 서버의 지원 전송 방식을 확인하세요.
{% endhint %}

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
MCP는 REST API를 **대체** 하는 것이 아니라, AI 에이전트가 기존 API를 **쉽게 사용할 수 있도록 감싸는(wrapping)** 표준입니다. 대부분의 MCP 서버는 내부적으로 REST API를 호출합니다.
{% endhint %}

핵심적인 차이를 한 문장으로 요약하면: **REST API는 "개발자가 코드로 호출"하는 것이고, MCP는 "AI가 자율적으로 호출"하는 것** 입니다. REST API로 구현한 기능은 프로그램 코드에 하드코딩되지만, MCP로 구현하면 AI 에이전트가 사용자의 자연어 요청에 따라 **동적으로 적절한 도구를 선택** 하고 호출합니다.

---

## MCP vs A2A (Agent-to-Agent)

MCP와 Google이 발표한 A2A 프로토콜은 **보완적 관계** 입니다:

| 비교 항목 | MCP | A2A |
|----------|-----|-----|
| 목적 | 에이전트가 **도구/데이터** 에 접근 | **에이전트 간** 통신 |
| 비유 | 사람이 도구를 사용하는 것 | 사람과 사람이 대화하는 것 |
| 통신 대상 | 에이전트 → 도구/데이터 소스 | 에이전트 → 에이전트 |
| 활용 예시 | GitHub에서 코드 검색, DB 쿼리 | 여행 에이전트가 결제 에이전트에게 위임 |
| 성숙도 | 성숙 (수천 개 서버, 주요 클라이언트 지원) | 초기 단계 (2025년 발표, 생태계 형성 중) |
| 도입 시기 | 지금 (즉시 도입 가능) | 대기 (생태계 성숙 후) |

미래에는 MCP와 A2A가 **함께 사용** 되는 아키텍처가 일반화될 것입니다. 예를 들어, "데이터 분석 에이전트"가 MCP를 통해 Databricks에서 데이터를 분석하고, A2A를 통해 "보고서 작성 에이전트"에게 결과를 전달하는 구조입니다. 현재는 MCP가 훨씬 성숙한 단계이므로, MCP 먼저 도입하고 A2A는 생태계가 성숙해지면 추가하는 것이 현실적입니다.

---

## MCP 도입 로드맵

조직에서 MCP를 처음 도입할 때의 단계별 로드맵입니다:

| 단계 | 기간 | 활동 | 성과 지표 |
|------|------|------|----------|
| **1. 탐색** | 1-2주 | 개인 환경에서 Claude Desktop + 2-3개 MCP 서버 체험 | "MCP가 무엇인지 이해" |
| **2. 팀 파일럿** | 2-4주 | 팀 내 2-3명이 업무에 MCP 활용 (Slack + DB + GitHub) | "실무 효과 검증" |
| **3. 팀 전체 도입** | 4-8주 | 팀 전체 MCP 환경 구성, `.mcp.json` 표준화 | "팀 생산성 측정 가능" |
| **4. 조직 확대** | 2-3개월 | Databricks Unity Catalog Connection으로 중앙 관리, Custom MCP 개발 | "조직 단위 자동화" |

{% hint style="info" %}
MCP 도입의 가장 큰 장벽은 기술적 복잡성이 아니라 **습관의 변화** 입니다. "Slack을 직접 열어서 메시지를 보내는" 습관을 "AI에게 메시지 전송을 요청하는" 습관으로 바꾸는 것이 핵심입니다. 작은 성공 경험을 축적하면 자연스럽게 전환됩니다.
{% endhint %}

---

## 현재 생태계

MCP는 빠르게 성장하는 생태계를 보유하고 있습니다:

- **수천 개의 MCP 서버** 가 이미 오픈소스로 공개 (GitHub, Slack, Jira, Google Drive, PostgreSQL, Notion, Brave Search 등)
- **주요 AI 클라이언트 지원**: Claude Desktop, Claude Code, ChatGPT, VS Code Copilot, Cursor, Windsurf, Databricks Genie Code
- **서버 디렉토리**: [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers), [smithery.ai](https://smithery.ai), [mcp.so](https://mcp.so)

### 생태계 참여자별 역할

MCP 생태계는 네 가지 참여자로 구성됩니다:

| 참여자 | 역할 | 예시 |
|--------|------|------|
| **프로토콜 관리자** | MCP 사양(spec) 관리 및 발전 | Linux Foundation AAIF, Anthropic |
| **클라이언트 개발사** | AI 애플리케이션에 MCP 지원 추가 | Anthropic(Claude), OpenAI(ChatGPT), Databricks(Genie Code), Microsoft(Copilot) |
| **서버 개발사/커뮤니티** | MCP 서버 개발 및 공개 | Anthropic 공식 서버, SaaS 벤더 공식 서버, 오픈소스 커뮤니티 |
| **엔드유저/기업** | MCP를 활용하여 워크플로 자동화 | 데이터 팀, DevOps 팀, 비즈니스 팀 |

### MCP의 미래 전망

MCP가 가져올 변화를 예측하면:

- **단기(2026)**: 대부분의 AI 코딩 도구와 AI 비서가 MCP를 기본 지원. 주요 SaaS 서비스가 공식 MCP 서버 제공
- **중기(2027-2028)**: MCP가 "AI 에이전트의 API"로 자리잡음. 새로운 서비스를 출시할 때 REST API와 MCP 서버를 동시에 제공하는 것이 관행
- **장기(2029+)**: AI 에이전트가 MCP를 통해 수백 개의 도구를 자유롭게 조합하여 복잡한 업무를 자율적으로 수행. 사람은 목표만 지시하고 AI가 실행

{% hint style="tip" %}
지금 MCP를 학습하고 도입하는 것은 **미래 투자** 입니다. AI 에이전트 시대의 기본 인프라가 될 MCP를 일찍 이해하고 활용하면, 조직의 AI 활용 역량에서 앞서 나갈 수 있습니다.
{% endhint %}

---

## 다음 단계

| 가이드 | 내용 |
|--------|------|
| [일반 MCP 설정](setup-general.md) | Claude Desktop, Claude Code, Cursor에서 MCP 서버 설정하기 |
| [인기 서버 & 활용 시나리오](popular-servers.md) | 카테고리별 인기 MCP 서버, 실전 자동화 시나리오 10선 |
| [Databricks MCP 활용](databricks-mcp.md) | Databricks 환경에서 Managed/External/Custom MCP 활용하기 |
| [베스트 프랙티스](best-practices.md) | 보안, Tool 설계, 에러 핸들링, 디버깅 팁 |
