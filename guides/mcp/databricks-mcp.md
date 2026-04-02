# Databricks에서 MCP 활용

Databricks는 MCP를 플랫폼 전반에 걸쳐 지원합니다. 세 가지 유형의 MCP 서버를 제공하며, Genie Code와 Databricks ONE(CLI)에서 MCP 도구를 사용할 수 있습니다.

Databricks의 MCP 전략은 **"데이터 플랫폼 자체를 AI 에이전트의 도구로 노출" ** 하는 것입니다. Unity Catalog에 등록된 모든 자산(테이블, 함수, 벡터 인덱스, Genie Space)을 MCP 프로토콜로 접근할 수 있게 하여, Databricks 외부의 AI 에이전트(Claude Desktop, Claude Code, Cursor 등)도 Databricks 데이터를 안전하게 활용할 수 있습니다. 동시에 외부 서비스(GitHub, Slack, JIRA 등)를 Databricks 내부로 가져와서 Genie Code가 활용할 수 있도록 합니다.

---

## Databricks MCP 서버 유형

Databricks는 세 가지 MCP 서버 유형을 제공하며, 각각의 목적과 아키텍처가 다릅니다. 어떤 유형을 사용할지는 "누가 어디에 접근하는가"에 따라 결정됩니다:

| 유형 | 방향 | 핵심 질문 | 예시 |
|------|------|----------|------|
| **Managed MCP** | Databricks 내부 자산 노출 | "Databricks 데이터를 AI에게 어떻게 제공할까?" | UC 함수, Vector Search, Genie Space |
| **External MCP** | 외부 서비스를 Databricks로 연결 | "외부 도구를 Genie Code에서 어떻게 사용할까?" | GitHub, Slack, JIRA |
| **Custom MCP** | 자체 API를 MCP로 래핑 | "사내 시스템을 AI 에이전트에서 어떻게 활용할까?" | 사내 CRM, ERP, 모니터링 시스템 |

### 1. Managed MCP (관리형)

Databricks가 사전 구성한 즉시 사용 가능한 MCP 서버입니다. Unity Catalog 권한이 자동으로 적용됩니다.

| 서버 | 용도 | 엔드포인트 패턴 |
|------|------|----------------|
| **Unity Catalog Functions** | 사전 정의된 SQL/Python 함수 실행 | `/api/2.0/mcp/functions/{catalog}/{schema}/{function}` |
| **Vector Search** | 벡터 검색 인덱스 쿼리 | `/api/2.0/mcp/vector-search/{catalog}/{schema}/{index}` |
| **Genie Space** | 자연어 데이터 분석 (읽기 전용) | `/api/2.0/mcp/genie/{genie_space_id}` |
| **Databricks SQL** | AI 생성 SQL 실행 (읽기/쓰기) | `/api/2.0/mcp/sql` |

{% hint style="info" %}
Managed MCP 서버는 별도의 설정 없이 워크스페이스에서 바로 사용할 수 있습니다. Unity Catalog 권한으로 접근이 제어됩니다.
{% endhint %}

**Managed MCP의 아키텍처 심화**: Managed MCP가 강력한 이유는 **Unity Catalog의 거버넌스가 자동 적용** 되기 때문입니다. 외부 AI 에이전트가 Databricks SQL MCP를 통해 쿼리를 실행하면, 해당 사용자의 UC 권한에 따라 접근 가능한 테이블만 조회됩니다. Row-level security, Column masking 등 모든 보안 정책이 투명하게 적용됩니다. 별도의 보안 설정 없이도 엔터프라이즈 수준의 데이터 보호가 보장되는 것입니다.

각 Managed MCP 서버의 내부 동작:

| 서버 | 내부 동작 | 보안 메커니즘 |
|------|----------|-------------|
| **Unity Catalog Functions** | 등록된 SQL/Python 함수를 Serverless Compute에서 실행 | 함수 소유자의 EXECUTE 권한 필요, 함수 내부에서 접근하는 테이블도 UC 권한 확인 |
| **Vector Search** | 벡터 인덱스에 대해 유사도 검색 쿼리 실행 | 인덱스에 대한 READ 권한 필요, 소스 테이블의 UC 권한도 간접 적용 |
| **Genie Space** | 자연어 질문을 SQL로 변환하여 SQL Warehouse에서 실행 | Space에 대한 CAN VIEW 이상 권한 + Space에 등록된 테이블의 UC 권한 |
| **Databricks SQL** | AI가 생성한 SQL을 SQL Warehouse에서 직접 실행 | 실행 사용자의 UC 권한으로 모든 테이블 접근 제어 |

### 2. External MCP (외부 서버 연결)

Unity Catalog Connection을 통해 외부 MCP 서버에 안전하게 연결합니다. 자격 증명이 직접 노출되지 않으며, 관리형 프록시를 통해 통신합니다.

| 연결 방법 | 설명 |
|----------|------|
| **Managed OAuth (권장)** | Databricks가 OAuth 흐름을 관리. GitHub, Glean, Google Drive, SharePoint 등 지원 |
| **Databricks Marketplace** | 마켓플레이스에서 사전 빌드된 통합 설치 |
| **Custom HTTP Connection** | Streamable HTTP를 지원하는 모든 MCP 서버에 커스텀 연결 |
| **Dynamic Client Registration** | RFC7591 지원 서버의 자동 OAuth 등록 (실험적) |

외부 MCP 서버의 프록시 엔드포인트:

```
https://<workspace-hostname>/api/2.0/mcp/external/{connection_name}
```

{% hint style="warning" %}
외부 MCP 서버를 연결하려면 해당 서버가 **Streamable HTTP 전송 방식** 을 지원해야 합니다. stdio 방식만 지원하는 서버는 직접 연결할 수 없습니다.
{% endhint %}

**Unity Catalog Connection의 보안 메커니즘 심화**: External MCP의 핵심은 **자격 증명이 사용자에게 노출되지 않는다** 는 것입니다. 전통적으로 Slack MCP 서버를 사용하려면 각 사용자가 Slack Bot Token을 보유해야 했습니다. 이는 보안 위험이고 관리 부담입니다. Databricks의 External MCP는 이 문제를 다음과 같이 해결합니다:

1. **관리자** 가 Unity Catalog Connection을 생성하며 OAuth 또는 Token 인증을 설정
2. 자격 증명은 **Databricks 내부에 암호화 저장**— 사용자에게 절대 노출 안 됨
3. 사용자가 MCP 도구를 호출하면, Databricks의 **Managed Proxy** 가 자격 증명을 주입하여 외부 서버에 요청
4. 모든 호출은 **Unity Catalog 감사 로그** 에 기록됨

인증 방식별 사용 시나리오:

| 인증 방식 | 동작 | 적합한 시나리오 |
|----------|------|--------------|
| **Shared Principal (공유)** | 하나의 서비스 계정으로 모든 사용자가 접근 | 내부 API, 읽기 전용 서비스 |
| **Per-user OAuth (개별)** | 각 사용자가 자신의 OAuth로 인증 | GitHub, Slack 등 개인 권한이 중요한 서비스 |
| **Bearer Token** | 고정 토큰으로 인증 | API 키 기반 서비스, 간단한 HTTP API |

### 3. Custom MCP (자체 서버 호스팅)

자체 MCP 서버를 **Databricks App** 으로 배포합니다. 사내 API를 MCP로 래핑하거나, 특수한 비즈니스 로직을 구현할 때 사용합니다.

**배포 절차:**

1. FastAPI + MCP SDK로 서버 코드 작성
2. `app.yaml` 구성 (Databricks Apps 배포 설정)
3. Databricks App 생성 및 배포:
   ```bash
   databricks apps create my-mcp-server
   databricks apps deploy my-mcp-server --source-code-path ./src
   ```
4. MCP 엔드포인트 확인: `https://<app-url>/mcp`

{% hint style="warning" %}
커스텀 MCP 앱은 **stateless 아키텍처** 로 구현해야 합니다. CORS 이슈 방지를 위해 워크스페이스 URL을 허용 오리진에 추가하세요.
{% endhint %}

**Custom MCP 서버 개발 실전 가이드**: 자체 MCP 서버를 개발할 때 자주 겪는 문제와 해결 방법입니다:

### Custom MCP 개발 시 체크리스트

| 항목 | 설명 | 중요도 |
|------|------|--------|
| **Streamable HTTP 구현** | `POST /mcp` 엔드포인트에서 JSON-RPC 요청 수신 + SSE 응답 | 필수 |
| **상태 비저장(Stateless)** | 앱 인스턴스가 재시작되어도 기능에 영향 없어야 함 | 필수 |
| **CORS 설정** | 워크스페이스 URL을 `Access-Control-Allow-Origin`에 추가 | 필수 |
| **에러 메시지 자연어화** | 에러 발생 시 LLM이 이해할 수 있는 자연어 메시지 반환 | 권장 |
| **Tool 설명 상세 작성** | 각 Tool의 이름, 설명, 파라미터를 LLM이 이해할 수 있도록 명확히 작성 | 권장 |
| **응답 크기 제한** | 대량 데이터 반환 시 페이지네이션 또는 요약 적용 (LLM 토큰 절약) | 권장 |
| **인증 구현** | Databricks에서 전달하는 Bearer 토큰 검증 로직 구현 | 보안 필수 |

### Custom MCP 서버 구조 예시

```python
# 사내 모니터링 시스템을 MCP로 래핑하는 예시
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI

app = FastAPI()
mcp = FastMCP("internal-monitoring")

@mcp.tool()
async def get_pipeline_health(pipeline_name: str) -> str:
    """데이터 파이프라인의 최근 실행 상태를 조회합니다.

    성공/실패 횟수, 평균 실행 시간, 마지막 성공 시각을 반환합니다.

    Args:
        pipeline_name: 조회할 파이프라인 이름 (예: 'daily_orders_etl')
    """
    # 사내 모니터링 API 호출
    status = await internal_api.get_pipeline_status(pipeline_name)
    return f"""
    파이프라인: {pipeline_name}
    최근 7일: 성공 {status.success_count}회, 실패 {status.fail_count}회
    평균 실행 시간: {status.avg_duration}분
    마지막 성공: {status.last_success}
    """

@mcp.tool()
async def get_data_freshness(table_name: str) -> str:
    """테이블의 데이터 최신성을 확인합니다.

    마지막 업데이트 시각과 현재까지의 지연 시간을 반환합니다.

    Args:
        table_name: Unity Catalog 테이블 전체 경로 (예: 'catalog.schema.table')
    """
    # 메타데이터 조회
    freshness = await internal_api.check_freshness(table_name)
    return f"테이블 {table_name}: 마지막 업데이트 {freshness.last_update}, 지연 {freshness.delay}"

# FastAPI에 MCP 마운트
app.mount("/mcp", mcp.get_asgi_app())
```

{% hint style="tip" %}
Custom MCP 서버를 개발할 때 가장 중요한 것은 **Tool의 설명(docstring)** 입니다. LLM은 이 설명만 보고 언제 이 도구를 호출할지 결정합니다. "모니터링 조회"보다 "데이터 파이프라인의 최근 실행 상태를 조회합니다. 성공/실패 횟수, 평균 실행 시간, 마지막 성공 시각을 반환합니다."처럼 **구체적으로** 작성하세요.
{% endhint %}

---

## Genie Code에서 MCP 사용

{% hint style="warning" %}
MCP 서버는 **Genie Code Agent 모드에서만** 지원됩니다. Chat 모드에서는 사용할 수 없습니다.
{% endhint %}

### 설정 단계

1. Genie Code 패널을 열고 **설정 아이콘** 을 클릭합니다.
2. **MCP Servers** 섹션에서 **Add Server** 를 선택합니다.
3. 사용할 서버 유형을 선택합니다:
   - Unity Catalog Functions
   - Vector Search Indexes
   - Genie Spaces
   - Unity Catalog Connections (외부 MCP)
   - Databricks Apps (커스텀 MCP)
4. **Save** 를 클릭하면 즉시 사용 가능합니다.

### 사용 예시

MCP 서버가 추가되면, Genie Code의 Agent 모드에서 자연어로 질문하면 적절한 MCP 도구가 자동으로 호출됩니다:

```
"GitHub에서 최근 PR 목록 가져와"
→ GitHub MCP의 search_pull_requests 도구 호출

"Slack #data-team 채널에 분석 결과 요약 보내줘"
→ Slack MCP의 send_message 도구 호출

"customers 테이블에서 서울 지역 고객 수 조회해줘"
→ Databricks SQL MCP의 쿼리 도구 호출
```

---

## Databricks ONE (CLI)에서 MCP 사용

Databricks ONE CLI에서도 MCP 서버를 사용할 수 있습니다.

### 설정 방법

```bash
# Managed MCP 서버는 자동으로 감지됩니다
# External MCP 서버 추가:
databricks mcp add --connection-name github-mcp

# 등록된 MCP 서버 확인
databricks mcp list
```

프로젝트별 설정은 `.databricks/.mcp.json` 파일에 저장됩니다.

### Databricks ONE과 Claude Code의 차이

| 측면 | Databricks ONE | Claude Code |
|------|---------------|-------------|
| **MCP 서버 소스** | Databricks Managed MCP 자동 감지 + External MCP | 수동 설정 (`.mcp.json` 또는 CLI) |
| **인증** | Databricks CLI 인증 자동 활용 | 환경변수로 개별 토큰 관리 |
| **데이터 접근** | Unity Catalog 통합 (Databricks 데이터에 직접 접근) | Databricks MCP Python 패키지로 간접 접근 |
| **적합한 사용 환경** | Databricks 중심 워크플로 | 범용 개발 환경 |

---

## Unity Catalog Functions을 MCP Tool로 노출

Unity Catalog에 등록된 SQL/Python 함수는 자동으로 MCP Tool로 노출됩니다. 함수의 **이름** 과 **COMMENT** 가 각각 Tool 이름과 설명이 됩니다.

### SQL 함수 예시

```sql
CREATE OR REPLACE FUNCTION catalog.schema.search_customer(
  query STRING COMMENT '검색할 고객명 또는 이메일'
)
RETURNS TABLE (id INT, name STRING, email STRING)
LANGUAGE SQL
COMMENT '고객 정보를 이름 또는 이메일로 검색합니다'
AS
SELECT id, name, email
FROM catalog.schema.customers
WHERE name LIKE CONCAT('%', query, '%')
   OR email LIKE CONCAT('%', query, '%');
```

### Python 함수 예시

```python
# Unity Catalog에 Python UDF로 등록
CREATE OR REPLACE FUNCTION catalog.schema.summarize_ticket(
  ticket_id STRING COMMENT 'Jira 티켓 번호'
)
RETURNS STRING
LANGUAGE PYTHON
COMMENT 'Jira 티켓 내용을 요약합니다'
AS $$
  import requests
  # 티켓 조회 로직
  return summary
$$;
```

{% hint style="tip" %}
함수의 `COMMENT`가 LLM이 도구를 선택할 때 참고하는 설명이 됩니다. 명확하고 구체적으로 작성하세요. 예를 들어 "검색" 대신 "고객 정보를 이름 또는 이메일로 검색합니다"처럼 작성합니다.
{% endhint %}

### UC Functions를 MCP Tool로 활용하는 실전 패턴

Unity Catalog Functions을 MCP Tool로 노출하면, **보안이 보장된 데이터 접근 레이어** 를 구축할 수 있습니다. 직접 SQL을 실행하게 하는 것보다, 사전 정의된 함수를 통해 접근하면 다음과 같은 이점이 있습니다:

| 직접 SQL 실행 (Databricks SQL MCP) | UC Functions을 통한 접근 |
|----------------------------------|----------------------|
| 사용자가 자유롭게 SQL을 작성 → 예측 불가능한 쿼리 | 사전 정의된 함수만 호출 → 예측 가능한 동작 |
| 무거운 full table scan 가능 | 함수 내부에서 최적화된 쿼리만 실행 |
| 민감 컬럼 접근 가능 (UC 권한 범위 내) | 함수가 필요한 컬럼만 반환하도록 제어 |
| 비용 예측 어려움 | 함수 단위로 비용 예측 가능 |

{% hint style="info" %}
**실전 권장 패턴**: 외부 AI 에이전트(Claude Desktop, Claude Code 등)에서 Databricks 데이터에 접근할 때는, Databricks SQL MCP보다 **Unity Catalog Functions MCP** 를 우선 사용하세요. 사전 정의된 함수로 접근을 제한하면 보안과 비용 모두를 관리할 수 있습니다.
{% endhint %}

---

## MCP 서버 확인 방법

워크스페이스에서 사용 가능한 MCP 서버를 확인하려면:

1. 워크스페이스의 **Agents** 섹션으로 이동합니다.
2. **MCP Servers** 탭을 선택합니다.
3. 등록된 서버 목록과 상태를 확인할 수 있습니다.

---

## 비용 구조

MCP 프로토콜 자체에는 추가 비용이 없습니다. 도구 실행 시 사용되는 컴퓨팅 리소스에 대해서만 비용이 부과됩니다:

| 리소스 | 비용 유형 |
|--------|----------|
| Unity Catalog Functions | Serverless General Compute |
| Genie Spaces | Serverless SQL Compute |
| Databricks SQL | SQL 전용 가격 |
| Vector Search Indexes | Vector Search 가격 |
| Custom MCP Servers (Apps) | Databricks Apps 가격 |

---

## 활용 시나리오

| 시나리오 | 사용할 MCP 서버 | 효과 |
|---------|---------------|------|
| 코드 검색 & PR 리뷰 | GitHub MCP (External) | 엔터프라이즈 리포에서 코드 패턴 검색 |
| 내부 문서 검색 | Glean MCP (External) | Confluence, Slack 등 통합 검색 |
| 고객 데이터 조회 | UC Functions (Managed) | SQL 함수로 안전하게 데이터 접근 |
| RAG 검색 | Vector Search (Managed) | 벡터 인덱스 기반 유사도 검색 |
| 사내 API 연동 | Custom MCP (Apps) | 내부 시스템을 MCP로 래핑 |

---

## Databricks MCP 도입 시 의사결정 가이드

어떤 유형의 MCP 서버를 사용할지 결정하는 흐름입니다:

| 질문 | 답변 | 권장 유형 |
|------|------|----------|
| Databricks 내부 데이터/함수에 접근하고 싶은가? | Yes | **Managed MCP** |
| 외부 SaaS 서비스(Slack, GitHub 등)를 사용하고 싶은가? | Yes | **External MCP**(Unity Catalog Connection) |
| 사내 전용 API/시스템을 MCP로 노출하고 싶은가? | Yes | **Custom MCP**(Databricks Apps) |
| Claude Desktop/Code에서 Databricks 데이터에 접근하고 싶은가? | Yes | **Databricks MCP Python 패키지**(로컬) |

### Managed vs External vs Custom 비교

| 측면 | Managed | External | Custom |
|------|---------|----------|--------|
| **설정 난이도** | 매우 쉬움 (즉시 사용) | 쉬움 (UI에서 Connection 생성) | 보통 (코드 개발 + 배포 필요) |
| **유지보수** | Databricks가 관리 | Connection 인증 갱신 정도 | 자체 코드 유지보수 |
| **유연성** | 사전 정의된 기능만 | 외부 서버가 제공하는 기능 | 완전한 자유도 |
| **보안** | UC 권한 자동 적용 | Managed Proxy + OAuth | 자체 인증 구현 필요 |
| **비용** | 기존 컴퓨팅 비용 | 기존 + 외부 서비스 비용 | Apps 호스팅 비용 + 개발 비용 |

{% hint style="tip" %}
**시작 권장**: Managed MCP(특히 Unity Catalog Functions)로 시작하여 MCP의 동작을 이해한 후, External MCP(Slack, GitHub)를 추가하고, 마지막으로 필요시 Custom MCP를 개발하세요.
{% endhint %}

---

## 다음 단계

- [일반 MCP 설정](setup-general.md): Claude Desktop, Claude Code 등에서 MCP 설정하기
- [인기 서버 & 시나리오](popular-servers.md): 카테고리별 인기 MCP 서버, 실전 조합 전략
- [베스트 프랙티스](best-practices.md): 보안, Tool 설계, 디버깅 팁
