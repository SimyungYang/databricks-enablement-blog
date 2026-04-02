# MCP 연동

## MCP 개요

### MCP란 무엇인가?

MCP(Model Context Protocol)는 **Anthropic이 개발한 오픈소스 프로토콜** 로, AI 에이전트가 외부 도구, 데이터 소스, 워크플로에 접근하기 위한 **표준 인터페이스** 입니다. USB-C가 다양한 전자기기를 하나의 규격으로 연결하듯, MCP는 AI 애플리케이션과 외부 시스템을 하나의 표준으로 연결합니다.

### MCP가 Genie Code를 어떻게 변환하는가 — 전략적 관점

MCP 없이 Genie Code는 **Databricks 워크스페이스 안에 갇힌** 강력한 AI입니다. 데이터를 분석하고 코드를 생성할 수 있지만, 그 결과를 Slack으로 공유하거나, JIRA 티켓을 생성하거나, GitHub에서 관련 코드를 검색하려면 사용자가 **수동으로 컨텍스트 전환** 을 해야 합니다.

MCP를 연결하면 Genie Code는 **워크스페이스의 경계를 넘어서는 AI 에이전트** 로 변환됩니다:

| MCP 없는 Genie Code | MCP가 있는 Genie Code |
|---------------------|----------------------|
| 분석 완료 → 사용자가 Slack을 열어 결과를 복사/붙여넣기 | 분석 완료 → "Slack #team에 결과 공유해줘" 한 마디로 전송 |
| 이슈 발견 → 사용자가 JIRA를 열어 티켓 수동 생성 | 이슈 발견 → "JIRA에 Bug 티켓 만들어줘" 로 자동 생성 |
| 코드 참조 필요 → 사용자가 GitHub을 열어 수동 검색 | "GitHub에서 비슷한 파이프라인 코드 찾아줘" → 즉시 검색 |
| 분석 결과 문서화 → 사용자가 Notion/Confluence에 수동 작성 | "이 분석을 Notion에 정리해줘" → 자동 문서화 |

이것은 단순한 편의 기능이 아닙니다. **워크플로의 단절을 제거** 함으로써, 하나의 프롬프트로 "분석 → 발견 → 알림 → 추적"이라는 완전한 업무 사이클을 자동화할 수 있게 됩니다.

{% hint style="info" %}
MCP 연동의 진정한 가치는 **개별 도구의 기능** 이 아니라, 여러 도구를 **하나의 워크플로로 연결** 하는 데 있습니다. "데이터 품질 점검 → 이상 발견 → Slack 알림 → JIRA 티켓 생성"을 하나의 Agent 프롬프트로 실행할 수 있다는 것이 핵심입니다.
{% endhint %}

### 핵심 아키텍처

MCP는 **클라이언트-서버 아키텍처** 를 따르며, 세 가지 핵심 참여자로 구성됩니다:

| 참여자 | 역할 | Databricks 예시 |
|--------|------|-----------------|
| **MCP Host** | AI 애플리케이션. 하나 이상의 MCP Client를 관리 | Genie Code, AI Playground |
| **MCP Client** | MCP Server와의 연결을 유지하고 컨텍스트를 획득 | Genie Code 내부 클라이언트 |
| **MCP Server** | 도구, 리소스, 프롬프트 등 컨텍스트를 제공하는 프로그램 | GitHub MCP, Unity Catalog Functions 등 |

### MCP 서버가 제공하는 3가지 기본 구성 요소

| 구성 요소 | 설명 | 예시 |
|-----------|------|------|
| **Tools** | AI가 호출할 수 있는 실행 가능한 함수 | 파일 검색, API 호출, DB 쿼리 |
| **Resources** | AI에 컨텍스트를 제공하는 데이터 소스 | 파일 내용, DB 레코드, API 응답 |
| **Prompts** | LLM과의 상호작용을 구조화하는 재사용 가능한 템플릿 | 시스템 프롬프트, Few-shot 예시 |

### MCP 통신 방식

MCP는 **JSON-RPC 2.0** 기반의 데이터 계층과 두 가지 전송 메커니즘을 지원합니다:

| 전송 방식 | 설명 | 사용 환경 |
|----------|------|----------|
| **Stdio** | 표준 입출력 스트림을 통한 로컬 프로세스 통신 | 로컬 개발 환경 |
| **Streamable HTTP** | HTTP POST + Server-Sent Events | 원격 서버 통신 (Databricks 기본) |

{% hint style="info" %}
Databricks에서 외부 MCP 서버를 연결하려면 해당 서버가 **Streamable HTTP 전송 방식** 을 지원해야 합니다.
{% endhint %}

---

## Databricks에서 MCP 서버 설정

Databricks는 세 가지 유형의 MCP 서버를 지원합니다:

### 유형 1: Managed MCP (관리형)

Databricks가 사전 구성한 즉시 사용 가능한 MCP 서버입니다. Unity Catalog 권한이 자동으로 적용됩니다.

| 서버 | 용도 | 엔드포인트 패턴 |
|------|------|----------------|
| **Unity Catalog Functions** | 사전 정의된 SQL 함수 실행 | `/api/2.0/mcp/functions/{catalog}/{schema}/{function}` |
| **Vector Search** | 벡터 검색 인덱스 쿼리 | `/api/2.0/mcp/vector-search/{catalog}/{schema}/{index}` |
| **Genie Space** | 자연어 데이터 분석 (읽기 전용) | `/api/2.0/mcp/genie/{genie_space_id}` |
| **Databricks SQL** | AI 생성 SQL 실행 (읽기/쓰기) | `/api/2.0/mcp/sql` |

### 유형 2: External MCP (외부)

Unity Catalog Connection을 통해 외부 MCP 서버에 안전하게 연결합니다. 자격 증명이 직접 노출되지 않으며, 관리형 프록시를 통해 통신합니다.

**지원되는 연결 방법:**

| 방법 | 설명 |
|------|------|
| **Managed OAuth (권장)** | Databricks가 OAuth 흐름을 관리. GitHub, Glean, Google Drive, SharePoint 등 지원 |
| **Databricks Marketplace** | 마켓플레이스에서 사전 빌드된 통합 설치 |
| **Custom HTTP Connection** | Streamable HTTP를 지원하는 모든 MCP 서버에 커스텀 연결 생성 |
| **Dynamic Client Registration (실험적)** | RFC7591 지원 서버의 자동 OAuth 등록 |

외부 MCP 서버의 프록시 엔드포인트 형식:

```
https://<workspace-hostname>/api/2.0/mcp/external/{connection_name}
```

**인증 방식:**

* **공유 인증(Shared Principal)**: Bearer 토큰, OAuth M2M, 공유 OAuth U2M
* **사용자별 인증(Per-user)**: 리소스별 개별 사용자 자격 증명

### 유형 3: Custom MCP (커스텀)

자체 MCP 서버를 **Databricks App** 으로 호스팅합니다. Streamable HTTP 전송 방식을 구현해야 합니다.

**배포 절차:**

1. MCP 서버 코드 작성 (`pyproject.toml`, `app.yaml` 구성)
2. Databricks App 생성: `databricks apps create <app-name>`
3. 소스 코드 업로드 및 배포
4. MCP 엔드포인트: `https://<app-url>/mcp`

{% hint style="warning" %}
커스텀 MCP 앱은 **stateless 아키텍처** 로 구현해야 하며, 동일 워크스페이스 내에 배포해야 합니다. CORS 이슈 방지를 위해 워크스페이스 URL을 허용 오리진에 추가하세요.
{% endhint %}

### MCP 서버 확인 방법

워크스페이스에서 사용 가능한 MCP 서버를 확인하려면:

1. 워크스페이스의 **Agents** 섹션으로 이동합니다.
2. **MCP Servers** 탭을 선택합니다.
3. 등록된 서버 목록과 상태를 확인할 수 있습니다.

---

## Genie Code에서 MCP 활용

### MCP 서버를 Genie Code에 연결하기

{% hint style="warning" %}
MCP 서버는 **Genie Code Agent 모드에서만** 지원됩니다. Chat 모드에서는 사용할 수 없습니다.
{% endhint %}

**설정 단계:**

1. Genie Code 패널을 열고 **설정 아이콘** 을 클릭합니다.
2. **MCP Servers** 섹션에서 **Add Server** 를 선택합니다.
3. 사용할 서버 유형을 선택합니다:
   * Unity Catalog Functions
   * Vector Search Indexes
   * Genie Spaces
   * Unity Catalog Connections (외부 MCP)
   * Databricks Apps (커스텀 MCP)
4. **Save** 를 클릭하면 즉시 사용 가능합니다.

### 방법 2: `.mcp_servers.json` 파일 (Workspace 내부 구성)

Databricks Workspace의 `.assistant/.mcp_servers.json` 파일은 Genie Code의 MCP 서버 구성을 저장하는 파일입니다. UI에서 MCP 서버를 추가/제거하면 이 파일이 자동으로 업데이트됩니다.

**파일 위치**: Workspace 파일 브라우저 → `.assistant/.mcp_servers.json` (`skills` 폴더와 같은 레벨)

{% hint style="warning" %}
**중요**: 이 파일은 Genie Code UI 설정의 **내부 저장소** 입니다. 2026년 4월 현재, 공식 문서에서 권장하는 구성 방법은 **방법 1(UI 기반 설정)** 입니다. 이 파일을 직접 편집하는 것은 공식적으로 문서화되지 않았으므로, 프로덕션 환경에서는 UI를 통해 설정하세요.

공식 문서: [Connect Genie Code to MCP servers](https://docs.databricks.com/aws/en/genie-code/mcp)
{% endhint %}

{% hint style="info" %}
UI에서 설정한 MCP 서버 구성이 이 JSON 파일에 어떤 형태로 저장되는지 확인하면, Genie Code의 내부 동작을 이해하는 데 도움이 됩니다.
{% endhint %}

**기본 구조:**

```json
[
  {
    "type": "uc_function",
    "uc_function_name": "catalog.schema.function_name"
  },
  {
    "type": "vector_search",
    "vector_search_index": "catalog.schema.index_name"
  },
  {
    "type": "genie_space",
    "genie_space_id": "01ef1234567890abcdef"
  },
  {
    "type": "uc_connection",
    "connection_name": "github-mcp-connection"
  },
  {
    "type": "databricks_app",
    "app_name": "my-custom-mcp-app"
  }
]
```

각 MCP 서버 유형별 JSON 설정을 정리하면 다음과 같습니다.

| 유형 | `type` 값 | 필수 필드 | 설명 |
|------|----------|---------|------|
| **Unity Catalog Function** | `uc_function` | `uc_function_name` | UC에 등록된 SQL/Python 함수를 Tool로 노출 |
| **Vector Search Index** | `vector_search` | `vector_search_index` | 벡터 인덱스를 검색 도구로 노출 |
| **Genie Space** | `genie_space` | `genie_space_id` | Genie Space를 자연어 SQL 도구로 노출 |
| **UC Connection (외부 MCP)** | `uc_connection` | `connection_name` | GitHub, Slack, JIRA 등 외부 서비스 연결 |
| **Databricks App** | `databricks_app` | `app_name` | 자체 MCP 서버(Databricks App으로 호스팅) |

**실전 예시 — 데이터팀 MCP 설정:**

다음은 데이터 엔지니어링 팀에서 실제로 사용할 수 있는 `.mcp_servers.json` 구성입니다. Genie Space로 데이터를 분석하고, Vector Search로 문서를 검색하고, GitHub에서 코드를 찾고, UC Function으로 커스텀 로직을 실행합니다.

```json
[
  {
    "type": "genie_space",
    "genie_space_id": "01ef7a8b9c0d1e2f3a4b"
  },
  {
    "type": "vector_search",
    "vector_search_index": "prod_catalog.docs.knowledge_base_index"
  },
  {
    "type": "uc_connection",
    "connection_name": "github-enterprise"
  },
  {
    "type": "uc_function",
    "uc_function_name": "prod_catalog.tools.search_jira_tickets"
  },
  {
    "type": "uc_function",
    "uc_function_name": "prod_catalog.tools.send_slack_notification"
  }
]
```

{% hint style="warning" %}
**주의사항:**
- JSON 배열 형태(`[...]`)로 작성합니다. 빈 배열 `[]` 은 MCP 서버가 없음을 의미합니다.
- `genie_space_id` 는 Genie Space URL에서 확인할 수 있습니다: `https://<workspace>/genie/rooms/<genie_space_id>`
- `connection_name` 은 Catalog Explorer → External Connections에서 생성한 연결 이름입니다.
- **최대 20개 Tool** 제한을 초과하지 않도록 필요한 서버만 등록하세요.
{% endhint %}

---

### MCP로 Genie Code가 할 수 있게 되는 일

MCP 서버를 연결하면 Genie Code의 Agent 모드가 **단순 코딩 도우미에서 종합 업무 자동화 에이전트** 로 변환됩니다. 각 MCP 서버 유형별로 가능해지는 작업을 정리합니다.

#### 1. Unity Catalog Functions → 커스텀 비즈니스 로직 실행

UC에 등록한 SQL/Python 함수를 Genie Code가 자연어 요청에 따라 자동 호출합니다.

| 함수 예시 | 프롬프트 예시 | Genie Code 동작 |
|---------|-----------|--------------|
| `search_customer(name)` | "김철수 고객 정보 찾아줘" | `search_customer('김철수')` 호출 → 결과 표시 |
| `calculate_churn_risk(customer_id)` | "이 고객의 이탈 위험도는?" | 함수 호출 → 위험 점수 + 해석 제공 |
| `send_slack_notification(channel, msg)` | "분석 결과를 #data-team에 공유해줘" | Slack 메시지 전송 |

{% hint style="info" %}
UC Function의 `COMMENT` 가 Genie Code가 도구를 선택할 때 참고하는 설명이 됩니다. 예: `COMMENT '고객 이름 또는 이메일로 CRM 데이터를 검색합니다'` 처럼 명확하게 작성하세요.
{% endhint %}

#### 2. Vector Search → RAG 기반 문서 검색

Vector Search 인덱스를 연결하면 Genie Code가 사내 문서, 기술 문서, 매뉴얼을 검색하여 답변에 활용합니다.

| 프롬프트 예시 | Genie Code 동작 |
|-----------|--------------|
| "온보딩 가이드에서 VPN 설정 방법 찾아줘" | Vector Search로 관련 문서 검색 → 핵심 내용 요약 |
| "이전에 비슷한 에러를 어떻게 해결했는지 찾아줘" | 과거 트러블슈팅 문서 검색 → 해결 방법 제시 |
| "Delta Lake Liquid Clustering 관련 공식 문서 내용 요약해줘" | 기술 문서 검색 → 구조화된 요약 생성 |

#### 3. Genie Space → 자연어 데이터 분석

Genie Space를 연결하면 Genie Code가 코딩 작업 중에 데이터를 직접 분석할 수 있습니다. 코드를 짜다가 "이 테이블의 최근 데이터 현황은?" 같은 질문을 바로 할 수 있습니다.

| 프롬프트 예시 | Genie Code 동작 |
|-----------|--------------|
| "지난 달 매출 상위 5개 제품 알려줘" | Genie Space가 SQL 생성 → 실행 → 결과 반환 |
| "이 테이블의 null 비율을 확인해줘" | 데이터 품질 쿼리 자동 생성 → 결과 분석 |
| "고객 세그먼트별 평균 주문 금액 비교해줘" | 분석 쿼리 생성 → 차트용 데이터 반환 |

{% hint style="success" %}
**강력한 조합**: Vector Search(문서 검색) + Genie Space(데이터 분석) + UC Function(비즈니스 로직)을 모두 연결하면, Genie Code가 "이 고객의 최근 주문을 분석하고, 관련 정책 문서를 찾고, CS팀에 요약을 보내줘" 같은 복합 작업을 한 번의 요청으로 처리할 수 있습니다.
{% endhint %}

#### 4. UC Connection (외부 MCP) → 외부 서비스 연동

GitHub, Slack, JIRA, Google Drive 등 외부 서비스의 MCP 서버를 Unity Catalog Connection으로 연결하면, Genie Code가 워크스페이스 밖의 시스템과도 상호작용합니다.

| 외부 서비스 | 프롬프트 예시 | Genie Code 동작 |
|---------|-----------|--------------|
| **GitHub** | "우리 리포에서 ETL 관련 코드 찾아줘" | GitHub MCP로 코드 검색 → 관련 파일 표시 |
| **Slack** | "이 분석 결과를 #analytics에 공유해줘" | Slack MCP로 메시지 전송 |
| **JIRA** | "이 버그에 대한 JIRA 티켓 만들어줘" | JIRA MCP로 이슈 생성 |
| **Google Drive** | "공유 드라이브에서 Q4 보고서 찾아줘" | Drive MCP로 파일 검색 |

#### 5. Databricks App (커스텀 MCP) → 사내 시스템 연동

자체 개발한 MCP 서버를 Databricks App으로 배포하면, 사내 ERP, CRM, HR 시스템 등 어떤 시스템이든 Genie Code에 연결할 수 있습니다.

| 커스텀 MCP 예시 | 프롬프트 예시 | 가능한 작업 |
|-------------|-----------|---------|
| ERP 연동 MCP | "지난 달 재고 부족 품목 확인해줘" | ERP API 호출 → 재고 데이터 조회 |
| HR 연동 MCP | "우리 팀 휴가 현황 알려줘" | HR 시스템 API 호출 → 캘린더 데이터 |
| 모니터링 MCP | "프로덕션 서버 상태 확인해줘" | 모니터링 API 호출 → 상태 요약 |

---

### MCP 연결 전후 비교

MCP 연결이 Genie Code를 어떻게 변화시키는지 한눈에 비교합니다.

| 항목 | MCP 연결 전 | MCP 연결 후 |
|------|----------|----------|
| **데이터 접근** | 현재 노트북/파일만 접근 | 워크스페이스 전체 데이터 + 외부 시스템 |
| **문서 검색** | 불가 (직접 검색해야 함) | Vector Search로 사내 문서 자동 검색 |
| **데이터 분석** | SQL을 직접 작성해야 함 | "매출 추이 보여줘" 한마디로 분석 |
| **외부 서비스** | 불가 | GitHub, Slack, JIRA 등 연동 |
| **업무 자동화** | 코딩 지원만 가능 | 코딩 + 분석 + 검색 + 알림 통합 자동화 |
| **역할** | 코딩 어시스턴트 | **종합 업무 자동화 에이전트** |

### 사용 방식

MCP 서버가 추가되면, Genie Code는 **자동으로** 관련 서버의 도구를 활용합니다. 프롬프트나 인스트럭션을 변경할 필요가 없습니다. Agent 모드에서 질문을 하면 Genie Code가 필요에 따라 적절한 MCP 서버의 도구를 호출합니다.

### 실전 MCP 구성 예시: GitHub + Slack + Databricks SQL 조합

가장 범용적이고 효과적인 MCP 조합은 **코드 관리(GitHub) + 커뮤니케이션(Slack) + 데이터(Databricks SQL)** 입니다. 이 세 가지를 연결하면 다음과 같은 통합 워크플로가 가능합니다:

```
프롬프트: "@orders 테이블에서 지난 주 대비 주문량이 30% 이상 감소한 지역을 찾고,
         GitHub에서 관련 ETL 코드의 최근 변경사항을 확인해서,
         데이터 이슈인지 코드 변경 때문인지 분석한 뒤
         Slack #data-ops에 분석 결과를 공유해줘."
```

**Agent 동작 흐름:**
1. **Databricks SQL MCP**→ 주간 주문량 비교 쿼리 실행 → 감소 지역 3곳 식별
2. **GitHub MCP**→ ETL 파이프라인 리포에서 최근 1주 커밋/PR 확인
3. **LLM 분석**→ 코드 변경(특정 필터 조건 추가)이 원인일 가능성 높다고 판단
4. **Slack MCP**→ 분석 결과 + 원인 추정 + GitHub PR 링크를 `#data-ops`에 전송

이 전체 과정이 **하나의 프롬프트** 로 3-5분 만에 완료됩니다.

### MCP 보안 고려사항

MCP를 통해 외부 시스템에 접근하므로, 보안에 대한 심도 있는 고려가 필요합니다:

| 보안 영역 | 고려사항 | Databricks의 대응 |
|----------|---------|------------------|
| **인증 정보 보호** | API 키/토큰이 노출되지 않아야 함 | Unity Catalog Connection이 자격 증명을 안전하게 관리 — 사용자에게 직접 노출 안 됨 |
| **최소 권한 원칙** | MCP 서버가 필요 이상의 권한을 갖지 않아야 함 | OAuth 스코프 제한 가능 (예: GitHub read-only) |
| **데이터 유출 방지** | 민감 데이터가 외부 서비스로 전송되지 않아야 함 | Managed MCP Proxy가 트래픽을 중계하며 감사 로그 기록 |
| **사용자별 인증** | 각 사용자가 자신의 권한으로만 외부 서비스에 접근 | Per-user OAuth로 개별 인증 지원 |
| **도구 실행 감사** | 어떤 사용자가 어떤 MCP 도구를 호출했는지 추적 | Unity Catalog 감사 로그에 MCP 호출 기록 |

{% hint style="warning" %}
**프로덕션 환경 체크리스트**: MCP를 프로덕션에 배포하기 전에 다음을 확인하세요:
- 모든 외부 MCP 연결이 Managed OAuth 또는 Per-user 인증을 사용하는가?
- 쓰기 권한이 필요한 MCP 서버(Slack 메시지 전송, JIRA 티켓 생성 등)에 대해 적절한 승인 절차가 있는가?
- Shared Principal 인증을 사용하는 경우, 공유 계정의 권한이 최소화되어 있는가?
{% endhint %}

### 활용 예시: GitHub MCP 서버

GitHub MCP 서버를 연결하면 Genie Code에서 엔터프라이즈 코드 검색이 가능합니다.

**설정 순서:**

1. **GitHub App 생성**: GitHub > Settings > Developer settings에서 앱 생성
   * Callback URL: `https://<databricks-workspace-url>/login/oauth/http.html`
2. **Unity Catalog Connection 생성**:
   * Auth type: OAuth User to Machine
   * Host: `https://api.githubcopilot.com`
   * OAuth scope: `mcp:access read:user user:email repo read:org`
   * Base path: `/mcp`
   * "Is mcp connection" 체크박스 활성화
3. **Genie Code에서 연결 추가**: Settings > MCP Servers > Add Server

**사용 가능한 도구:**

| 도구 | 기능 |
|------|------|
| `search_code` | 리포지토리에서 코드 패턴 검색 |
| `get_file_contents` | 리포지토리의 파일 내용 조회 |

**사용 예시:**

```
프롬프트: "우리 리포지토리에서 데이터 처리 파이프라인 관련 코드를 찾아줘"
프롬프트: "main 브랜치의 config.yaml 파일 내용을 보여줘"
```

{% hint style="tip" %}
특정 리포지토리를 대상으로 검색하려면 Genie Code 인스트럭션 파일에 `repo: repository_name, owner: username` 형식으로 지정할 수 있습니다.
{% endhint %}

### 활용 예시: 기타 외부 서비스

| 서비스 | 활용 시나리오 |
|--------|-------------|
| **Slack** | 작업 완료 후 채널에 결과 알림, 대화 검색 및 요약 |
| **Microsoft Teams** | 분석 결과를 Teams 채널에 공유, 회의 요약 전송 |
| **Glean** | 내부 문서 검색, 사전 사례 참조 |
| **Google Drive** | 팀 문서에서 필요한 정보 추출 |
| **SharePoint** | 조직 내부 문서 및 데이터 접근 |
| **JIRA** | 분석 중 발견한 이슈를 티켓으로 생성, 상태 업데이트 |
| **GitHub** | 엔터프라이즈 리포에서 코드 패턴 검색, PR 조회 |
| **Notion** | 분석 결과를 위키에 자동 기록, 팀 DB 조회 |
| **Genie Space** | 자연어로 데이터 분석 (Agent 모드에서 MCP를 통해 호출) |
| **Vector Search** | RAG 패턴으로 관련 문서 검색 후 분석에 활용 |

{% hint style="tip" %}
업계에서 많이 활용되는 MCP 서버 전체 목록과 실전 자동화 시나리오는 [인기 MCP 서버 & 활용 시나리오](../mcp/popular-servers.md)에서 확인하세요. Slack/Teams 알림, JIRA 티켓 생성, 스프린트 보고서 자동화 등 10가지 실전 시나리오를 다룹니다.
{% endhint %}

### 제한 사항

| 제한 | 상세 |
|------|------|
| **Agent 모드 전용** | MCP 서버는 Agent 모드에서만 사용 가능 |
| **도구 수 제한** | 전체 MCP 서버에 걸쳐 **최대 20개 도구** 만 사용 가능 |
| **전송 방식** | 외부 MCP 서버는 Streamable HTTP만 지원 |
| **도구 이름 하드코딩 금지** | 도구 목록이 변경될 수 있으므로 동적 탐색 권장 |
| **출력 형식 비보장** | 도구 출력 형식이 안정적이지 않으므로 프로그래밍적 파싱 비권장 |

{% hint style="info" %}
MCP 서버가 제공하는 도구가 20개를 초과하는 경우, Genie Code 설정에서 특정 도구나 서버를 선택적으로 활성화/비활성화하여 20개 한도 내에서 관리할 수 있습니다.
{% endhint %}

---

## MCP 비용 구조

MCP 서버 사용 시 각 리소스 유형에 따라 컴퓨팅 비용이 발생합니다:

| 리소스 | 비용 유형 |
|--------|----------|
| Unity Catalog Functions | Serverless General Compute |
| Genie Spaces | Serverless SQL Compute |
| Databricks SQL | SQL 전용 가격 |
| Vector Search Indexes | Vector Search 가격 |
| Custom MCP Servers | Databricks Apps 가격 |

{% hint style="info" %}
MCP 프로토콜 자체에 대한 추가 비용은 없습니다. 실제 도구를 실행할 때 사용되는 컴퓨팅 리소스에 대해서만 비용이 부과됩니다.
{% endhint %}

**비용 최적화 팁**: MCP 도구 호출 자체는 무료이지만, 도구가 많을수록 LLM 프롬프트에 포함되는 도구 정의 토큰이 증가합니다. 20개 도구가 모두 등록되면 매 요청마다 수천 토큰이 도구 정의에 소비됩니다. 실제로 사용하는 도구만 활성화하면 AI 추론 비용을 절약할 수 있습니다.

---

## MCP 에이전트 개발 베스트 프랙티스

MCP를 활용한 에이전트를 개발할 때 다음 권장 사항을 따르세요:

1. **도구 이름 하드코딩 금지**: MCP 서버의 도구 목록은 변경될 수 있으므로, 에이전트가 런타임에 `tools/list`를 호출하여 **동적으로 도구를 탐색** 하도록 구현합니다.
2. **출력 파싱 금지**: 도구 출력 형식은 안정적이지 않으므로, 결과 해석은 **LLM에 위임** 합니다.
3. **LLM 기반 도구 선택**: 어떤 도구를 호출할지는 LLM이 사용자 요청에 따라 자동으로 결정하도록 합니다.

**프로그래밍 방식으로 MCP 서버 연결하기 (로컬 개발):**

```bash
# 1. OAuth 인증
databricks auth login --host https://<workspace-hostname>

# 2. 의존성 설치
pip install -U "mcp>=1.9" "databricks-sdk[openai]" "mlflow>=3.1.0" \
    "databricks-agents>=1.0.0" "databricks-mcp"
```

```python
# 3. DatabricksMCPClient를 사용한 연결
from databricks_mcp import DatabricksMCPClient

client = DatabricksMCPClient(
    server_url="https://<hostname>/api/2.0/mcp/functions/{catalog}/{schema}/{func}",
    databricks_cli_profile="DEFAULT"
)
```

---

## MCP 활용 성숙도 모델

MCP를 단계적으로 도입하여 점진적으로 가치를 높이는 로드맵입니다:

| 단계 | 수준 | 사용 패턴 | 기대 효과 |
|------|------|----------|----------|
| **Level 1** | 기본 | Genie Code Agent 모드만 사용 (MCP 없이) | 코딩 생산성 2-3배 향상 |
| **Level 2** | 연결 | Managed MCP 1-2개 추가 (UC Functions, Genie Space) | Databricks 내부 자산 통합 활용 |
| **Level 3** | 확장 | External MCP 2-3개 추가 (Slack, GitHub, JIRA) | 외부 도구와 연결된 자동화 워크플로 |
| **Level 4** | 맞춤 | Custom MCP 개발 (사내 시스템 래핑) | 조직 전용 AI 에이전트 완성 |

{% hint style="tip" %}
대부분의 팀은 Level 1에서 시작하여 2-3개월에 걸쳐 Level 3까지 도달합니다. Level 4(Custom MCP)는 사내에 MCP로 래핑할 가치가 있는 API가 있을 때만 진행하세요. 무리하게 Custom MCP를 개발하기보다, 기존 External MCP 서버를 최대한 활용하는 것이 비용 대비 효과가 높습니다.
{% endhint %}

---

## MCP 관련 상세 가이드

MCP에 대한 더 깊은 내용은 별도의 MCP 가이드에서 다룹니다:

| 가이드 | 내용 |
|--------|------|
| [MCP 개요](../mcp/README.md) | MCP 프로토콜의 전략적 의미, 아키텍처, 표준화 동향 |
| [일반 MCP 설정](../mcp/setup-general.md) | Claude Desktop, Claude Code, Cursor 등에서 MCP 설정 |
| [Databricks MCP 활용](../mcp/databricks-mcp.md) | Managed/External/Custom MCP의 아키텍처와 보안 |
| [인기 서버 & 시나리오](../mcp/popular-servers.md) | 카테고리별 인기 MCP 서버, 실전 조합 전략 |
| [베스트 프랙티스](../mcp/best-practices.md) | Tool 설계, 비용 최적화, 프로덕션 운영 가이드 |
