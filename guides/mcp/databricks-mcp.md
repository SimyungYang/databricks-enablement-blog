# Databricks에서 MCP 활용

Databricks는 MCP를 플랫폼 전반에 걸쳐 지원합니다. 세 가지 유형의 MCP 서버를 제공하며, Genie Code와 Databricks ONE(CLI)에서 MCP 도구를 사용할 수 있습니다.

---

## Databricks MCP 서버 유형

### 1. Managed MCP (관리형)

Databricks가 사전 구성한 즉시 사용 가능한 MCP 서버입니다. Unity Catalog 권한이 자동으로 적용됩니다.

| 서버 | 용도 | 엔드포인트 패턴 |
|------|------|----------------|
| **Unity Catalog Functions**| 사전 정의된 SQL/Python 함수 실행 | `/api/2.0/mcp/functions/{catalog}/{schema}/{function}` |
| **Vector Search**| 벡터 검색 인덱스 쿼리 | `/api/2.0/mcp/vector-search/{catalog}/{schema}/{index}` |
| **Genie Space**| 자연어 데이터 분석 (읽기 전용) | `/api/2.0/mcp/genie/{genie_space_id}` |
| **Databricks SQL**| AI 생성 SQL 실행 (읽기/쓰기) | `/api/2.0/mcp/sql` |

{% hint style="info" %}
Managed MCP 서버는 별도의 설정 없이 워크스페이스에서 바로 사용할 수 있습니다. Unity Catalog 권한으로 접근이 제어됩니다.
{% endhint %}

### 2. External MCP (외부 서버 연결)

Unity Catalog Connection을 통해 외부 MCP 서버에 안전하게 연결합니다. 자격 증명이 직접 노출되지 않으며, 관리형 프록시를 통해 통신합니다.

| 연결 방법 | 설명 |
|----------|------|
| **Managed OAuth (권장)**| Databricks가 OAuth 흐름을 관리. GitHub, Glean, Google Drive, SharePoint 등 지원 |
| **Databricks Marketplace**| 마켓플레이스에서 사전 빌드된 통합 설치 |
| **Custom HTTP Connection**| Streamable HTTP를 지원하는 모든 MCP 서버에 커스텀 연결 |
| **Dynamic Client Registration**| RFC7591 지원 서버의 자동 OAuth 등록 (실험적) |

외부 MCP 서버의 프록시 엔드포인트:

```
https://<workspace-hostname>/api/2.0/mcp/external/{connection_name}
```

{% hint style="warning" %}
외부 MCP 서버를 연결하려면 해당 서버가 **Streamable HTTP 전송 방식** 을 지원해야 합니다. stdio 방식만 지원하는 서버는 직접 연결할 수 없습니다.
{% endhint %}

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

---

## Genie Code에서 MCP 사용

{% hint style="warning" %}
MCP 서버는 **Genie Code Agent 모드에서만** 지원됩니다. Chat 모드에서는 사용할 수 없습니다.
{% endhint %}

### 설정 단계

1. Genie Code 패널을 열고 **설정 아이콘** 을 클릭합니다.
2. **MCP Servers**섹션에서 **Add Server** 를 선택합니다.
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

---

## Unity Catalog Functions을 MCP Tool로 노출

Unity Catalog에 등록된 SQL/Python 함수는 자동으로 MCP Tool로 노출됩니다. 함수의 **이름**과 **COMMENT** 가 각각 Tool 이름과 설명이 됩니다.

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

## 다음 단계

- [일반 MCP 설정](setup-general.md): Claude Desktop, Claude Code 등에서 MCP 설정하기
- [베스트 프랙티스](best-practices.md): 보안, Tool 설계, 디버깅 팁
