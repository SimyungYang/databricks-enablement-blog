# MCP(Model Context Protocol) 연동

---

## MCP가 Genie Space를 변화시키는 방식

### 전략적 관점: Genie Space가 "AI Agent의 도구"가 된다

MCP 연동의 전략적 의미를 이해하려면, Genie Space의 역할 변화를 살펴봐야 합니다.

**MCP 연동 전**: Genie Space는 사용자가 직접 채팅창에서 질문하는 **독립형 인터페이스** 입니다. 사용자가 브라우저를 열고, Space에 접속하고, 질문을 타이핑해야 합니다.

**MCP 연동 후**: Genie Space는 **AI Agent가 호출할 수 있는 도구(Tool)** 가 됩니다. Claude, Genie Code, 커스텀 에이전트 같은 AI가 "매출 데이터가 필요하다"고 판단하면, MCP를 통해 Genie Space에 자동으로 질문하고 결과를 받아옵니다.

이 변화는 세 가지 새로운 가능성을 열어줍니다:

| 가능성 | 설명 | 예시 |
|--------|------|------|
| **멀티 소스 분석** | AI Agent가 여러 Genie Space/데이터 소스를 조합 | "매출 데이터(Genie) + 내부 문서(Glean) + GitHub 코드를 종합 분석" |
| **워크플로 자동화** | 데이터 분석을 자동화된 워크플로의 일부로 편입 | "매일 아침 매출 현황을 확인하고, 이상이 있으면 Slack에 알림" |
| **Agent-to-Agent 협업** | Supervisor Agent가 Genie Agent를 하위 에이전트로 호출 | Agent Bricks의 Supervisor가 Genie Space를 도구로 사용 |

{% hint style="info" %}
**핵심 인사이트**: MCP는 Genie Space를 "사람이 사용하는 채팅 도구"에서 "AI 생태계의 데이터 인터페이스"로 격상시킵니다. 잘 구축된 Genie Space(정확한 메타데이터, 풍부한 인스트럭션)는 MCP를 통해 조직 전체의 AI Agent들이 공유하는 **데이터 접근 표준 레이어** 가 됩니다.
{% endhint %}

### Genie Space MCP 활용 시나리오

| 시나리오 | MCP Host | Genie Space 역할 | 비즈니스 가치 |
|----------|----------|-----------------|-------------|
| **일일 리포트 자동화** | Databricks Workflow + Agent | 전일 매출/재고 데이터 조회 | 수동 리포트 작성 시간 제거 |
| **이상 탐지 알림** | 모니터링 Agent | KPI 임계치 초과 여부 확인 | 실시간 비즈니스 이상 감지 |
| **고객 응대 지원** | 고객 서비스 Agent | 고객 주문/배송 현황 조회 | CS 담당자 응답 시간 단축 |
| **경영진 브리핑** | Slack Bot Agent | 주간 핵심 KPI 요약 생성 | 경영진 데이터 접근 간소화 |

---

## MCP 개요

### MCP란 무엇인가?

MCP(Model Context Protocol)는 **Anthropic이 개발한 오픈소스 프로토콜** 로, AI 에이전트가 외부 도구, 데이터 소스, 워크플로에 접근하기 위한 **표준 인터페이스** 입니다. USB-C가 다양한 전자기기를 하나의 규격으로 연결하듯, MCP는 AI 애플리케이션과 외부 시스템을 하나의 표준으로 연결합니다.

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

MCP를 통해 Genie Code는 단순한 코드 생성 도구에서 **다양한 데이터 소스와 서비스에 접근할 수 있는 AI Agent** 로 진화합니다. 예를 들어, "우리 리포지토리(GitHub MCP)에서 ETL 코드를 찾고, 해당 파이프라인의 출력 테이블(Genie Space MCP)에서 매출 데이터를 확인하고, 내부 문서(Glean MCP)에서 관련 가이드를 참고해서 보고서를 작성해줘"라는 복합 요청을 처리할 수 있습니다.

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

### 사용 방식

MCP 서버가 추가되면, Genie Code는 **자동으로** 관련 서버의 도구를 활용합니다. 프롬프트나 인스트럭션을 변경할 필요가 없습니다. Agent 모드에서 질문을 하면 Genie Code가 필요에 따라 적절한 MCP 서버의 도구를 호출합니다.

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
| **Glean** | 내부 문서 검색, 사전 사례 참조 |
| **Google Drive** | 팀 문서에서 필요한 정보 추출 |
| **SharePoint** | 조직 내부 문서 및 데이터 접근 |
| **Genie Space** | 자연어로 데이터 분석 (Agent 모드에서 MCP를 통해 호출) |
| **Vector Search** | RAG 패턴으로 관련 문서 검색 후 분석에 활용 |

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

---

## MCP 보안 고려사항

MCP를 통해 AI Agent가 데이터에 접근하므로, 보안 측면을 반드시 고려해야 합니다:

| 보안 항목 | 설명 | 권장 사항 |
|-----------|------|----------|
| **인증** | MCP 서버 접근에 사용되는 자격 증명 | OAuth 기반 인증 권장, API 키 직접 노출 금지 |
| **권한 범위** | AI Agent가 접근할 수 있는 데이터 범위 | 최소 권한 원칙. Genie Space MCP는 읽기 전용 |
| **감사 추적** | AI Agent의 MCP 호출 이력 | Audit Log에서 MCP 호출 이벤트 모니터링 |
| **데이터 흐름** | Agent가 가져간 데이터의 사용처 | 민감 데이터가 외부 LLM으로 전송되지 않도록 확인 |

{% hint style="warning" %}
**Genie Space MCP는 읽기 전용** 입니다. AI Agent가 Genie Space를 통해 데이터를 조회할 수 있지만, 데이터를 수정하거나 삭제할 수는 없습니다. 반면 **Databricks SQL MCP는 읽기/쓰기** 가 가능하므로, 권한 설정에 더욱 주의가 필요합니다.
{% endhint %}

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

## MCP 트러블슈팅

MCP 연동 시 자주 발생하는 문제와 해결 방법:

| 문제 | 원인 | 해결 방법 |
|------|------|----------|
| MCP 서버 연결 실패 | OAuth 토큰 만료 | 연결을 재설정하고 OAuth 재인증 |
| 도구가 목록에 나타나지 않음 | MCP 서버가 20개 도구 한도 초과 | 불필요한 서버/도구 비활성화 |
| Genie Space MCP 응답이 느림 | Warehouse 콜드 스타트 | Serverless Warehouse 사용 또는 Warehouse 웜업 설정 |
| 외부 MCP 서버 통신 오류 | 네트워크/방화벽 문제 | Workspace의 아웃바운드 네트워크 설정 확인 |
| 인증 팝업이 반복됨 | Per-user OAuth 토큰 갱신 실패 | 브라우저 쿠키 삭제 후 재인증 |

---

## MCP 도입 전략 — 단계적 접근

MCP를 도입할 때는 단계적으로 접근하는 것이 좋습니다:

| 단계 | 활동 | 목표 |
|------|------|------|
| **1단계: Managed MCP** | Genie Space, UC Functions 등 Databricks 내장 MCP 먼저 활용 | MCP 동작 방식 이해, 내부 데이터 연동 |
| **2단계: External MCP** | GitHub, Glean, Google Drive 등 외부 서비스 연결 | 멀티 소스 분석 능력 확보 |
| **3단계: Custom MCP** | 조직 고유 시스템(ERP, CRM 등)용 커스텀 MCP 서버 개발 | 완전한 AI Agent 생태계 구축 |

{% hint style="tip" %}
**MCP와 Genie Space의 시너지**: Genie Space의 Knowledge Store를 풍부하게 구축해두면, MCP를 통해 AI Agent가 호출할 때도 동일한 정확도를 보장받습니다. "사람이 사용할 때 정확한 Space = AI Agent가 사용할 때도 정확한 Space"입니다.
{% endhint %}

---

## 참고 자료

* [MCP on Databricks 공식 문서](https://docs.databricks.com/aws/en/generative-ai/mcp/)
* [Genie Code MCP 연결 가이드](https://docs.databricks.com/aws/en/genie-code/mcp)
* [Databricks Managed MCP 서버](https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp)
* [외부 MCP 서버 연결](https://docs.databricks.com/aws/en/generative-ai/mcp/external-mcp)
* [커스텀 MCP 서버 호스팅](https://docs.databricks.com/aws/en/generative-ai/mcp/custom-mcp)
* [GitHub MCP 서버 연동](https://docs.databricks.com/aws/en/genie-code/github-mcp)
* [MCP 공식 사이트](https://modelcontextprotocol.io/introduction)
