# 인기 MCP 서버 & 실전 활용 시나리오

업계에서 가장 많이 사용되는 MCP 서버들과, 이들을 조합하여 실무 자동화를 구현하는 시나리오를 정리합니다.

{% hint style="info" %}
**학습 목표**
- 카테고리별 인기 MCP 서버와 주요 기능을 파악한다
- 여러 MCP 서버를 조합한 실전 자동화 시나리오를 설계할 수 있다
- Genie Code / Claude Code에 MCP 서버를 추가하는 방법을 이해한다
- MCP 서버 디렉토리에서 필요한 서버를 찾고 평가할 수 있다
{% endhint %}

---

## MCP 서버 디렉토리

MCP 서버를 찾을 수 있는 주요 사이트입니다:

| 디렉토리 | URL | 특징 |
|----------|-----|------|
| **공식 레퍼런스 서버**| [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | Anthropic이 직접 관리하는 공식 서버. 품질과 안정성 보장 |
| **Smithery**| [smithery.ai](https://smithery.ai) | 가장 큰 커뮤니티 마켓플레이스. 원클릭 설치, 인기순 정렬 |
| **MCP.so**| [mcp.so](https://mcp.so) | 서버 검색 및 비교. 카테고리별 분류 |
| **Glama**| [glama.ai/mcp/servers](https://glama.ai/mcp/servers) | 서버 평가 및 리뷰 |
| **Awesome MCP Servers**| [github.com/punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | GitHub Awesome 리스트. 커뮤니티 큐레이션 |
| **Cursor Directory**| [cursor.directory](https://cursor.directory) | Cursor IDE 중심의 MCP 서버 목록 |

{% hint style="tip" %}
**서버 선택 기준**: GitHub Star 수, 최근 커밋 활동, 이슈 응답 속도, 공식(Anthropic/벤더) 여부를 확인하세요. 커뮤니티 서버는 품질 편차가 큽니다.
{% endhint %}

---

## 카테고리별 인기 MCP 서버

### 커뮤니케이션 & 협업

| 서버 | 패키지 / 리포 | 주요 Tool | 활용 사례 |
|------|-------------|-----------|----------|
| **Slack**| `@modelcontextprotocol/server-slack` | `send_message`, `search_messages`, `list_channels`, `get_channel_history` | 채널 메시지 전송, 대화 검색, 스레드 요약 |
| **Microsoft Teams**| `mcp-server-microsoft-teams` (커뮤니티) | `send_message`, `list_teams`, `search_messages` | Teams 채널 알림, 회의 요약 전송 |
| **Discord**| `@modelcontextprotocol/server-discord` (커뮤니티) | `send_message`, `read_messages`, `manage_channels` | 커뮤니티 관리, 봇 응답 |
| **Gmail**| `@anthropic/gmail-mcp-server` | `search_emails`, `send_email`, `draft_email`, `read_email` | 이메일 초안 작성, 수신함 분석 |
| **Google Calendar**| `@anthropic/google-calendar-mcp` | `list_events`, `create_event`, `check_availability` | 일정 확인, 미팅 생성, 빈 시간 검색 |

### 개발 & DevOps

| 서버 | 패키지 / 리포 | 주요 Tool | 활용 사례 |
|------|-------------|-----------|----------|
| **GitHub**| `@modelcontextprotocol/server-github` | `search_repositories`, `create_issue`, `list_pull_requests`, `get_file_contents` | PR 리뷰, 이슈 관리, 코드 검색 |
| **GitLab**| `@modelcontextprotocol/server-gitlab` | `create_issue`, `list_merge_requests`, `search_code` | MR 관리, 파이프라인 모니터링 |
| **JIRA**| `mcp-server-atlassian` (커뮤니티) | `search_issues`, `create_issue`, `update_issue`, `add_comment` | 이슈 생성, 스프린트 관리, 상태 업데이트 |
| **Linear**| `mcp-server-linear` (커뮤니티) | `create_issue`, `list_issues`, `update_issue` | 이슈 트래킹, 프로젝트 관리 |
| **Sentry**| `mcp-server-sentry` (커뮤니티) | `list_issues`, `get_issue_details`, `resolve_issue` | 에러 모니터링, 이슈 분석 |

### 데이터베이스

| 서버 | 패키지 / 리포 | 주요 Tool | 활용 사례 |
|------|-------------|-----------|----------|
| **PostgreSQL**| `@modelcontextprotocol/server-postgres` | `query`, `list_tables`, `describe_table` | SQL 쿼리 실행, 스키마 탐색, 데이터 분석 |
| **MySQL**| `@benborla29/mcp-server-mysql` (커뮤니티) | `query`, `list_databases`, `describe_table` | DB 조회, 데이터 검증 |
| **MongoDB**| `mcp-server-mongodb` (커뮤니티) | `find`, `aggregate`, `list_collections` | 문서 검색, 집계 쿼리 |
| **SQLite**| `@modelcontextprotocol/server-sqlite` | `query`, `list_tables`, `describe_table` | 로컬 DB 분석, 프로토타이핑 |
| **Redis**| `mcp-server-redis` (커뮤니티) | `get`, `set`, `keys`, `info` | 캐시 관리, 세션 데이터 조회 |

### 클라우드 & 인프라

| 서버 | 패키지 / 리포 | 주요 Tool | 활용 사례 |
|------|-------------|-----------|----------|
| **AWS**| `@aws/mcp` (AWS 공식) | `s3_list`, `s3_get`, `cloudwatch_query`, `lambda_invoke` | S3 파일 관리, 로그 분석, Lambda 실행 |
| **GCP**| `@anthropic/gcp-mcp-server` | `bigquery_query`, `gcs_list`, `gcs_read` | BigQuery 분석, GCS 파일 관리 |
| **Azure**| `mcp-server-azure` (커뮤니티) | `blob_list`, `cosmos_query` | Blob Storage, CosmosDB 연동 |
| **Kubernetes**| `mcp-server-kubernetes` (커뮤니티) | `get_pods`, `get_logs`, `describe_resource` | 클러스터 상태 확인, 파드 로그 조회 |
| **Docker**| `mcp-server-docker` (커뮤니티) | `list_containers`, `get_logs`, `exec_command` | 컨테이너 관리, 로그 분석 |

### 문서 & 생산성

| 서버 | 패키지 / 리포 | 주요 Tool | 활용 사례 |
|------|-------------|-----------|----------|
| **Google Drive**| `@modelcontextprotocol/server-gdrive` | `search_files`, `read_file`, `list_files` | 문서 검색, 파일 내용 읽기 |
| **Notion**| `@notionhq/notion-mcp-server` (Notion 공식) | `search`, `read_page`, `create_page`, `update_page`, `query_database` | 위키 관리, DB 조회, 문서 생성 |
| **Confluence**| `mcp-server-confluence` (커뮤니티) | `search_pages`, `get_page`, `create_page` | 문서 검색, 페이지 생성 |
| **Google Sheets**| `mcp-server-google-sheets` (커뮤니티) | `read_sheet`, `write_cells`, `create_sheet` | 스프레드시트 자동화 |
| **Obsidian**| `mcp-server-obsidian` (커뮤니티) | `search_notes`, `read_note`, `create_note` | 노트 관리, 지식베이스 검색 |

### 웹 & 검색

| 서버 | 패키지 / 리포 | 주요 Tool | 활용 사례 |
|------|-------------|-----------|----------|
| **Brave Search**| `@modelcontextprotocol/server-brave-search` | `web_search`, `local_search` | 웹 검색, 로컬 비즈니스 검색 |
| **Puppeteer**| `@modelcontextprotocol/server-puppeteer` | `navigate`, `screenshot`, `click`, `evaluate` | 웹 스크래핑, UI 테스트, 스크린샷 |
| **Playwright**| `@anthropic/playwright-mcp` | `navigate`, `click`, `fill`, `screenshot` | 브라우저 자동화, E2E 테스트 |
| **Fetch**| `@modelcontextprotocol/server-fetch` | `fetch` | URL 내용 가져오기, API 호출 |

### 파일 & 스토리지

| 서버 | 패키지 / 리포 | 주요 Tool | 활용 사례 |
|------|-------------|-----------|----------|
| **Filesystem**| `@modelcontextprotocol/server-filesystem` | `read_file`, `write_file`, `search_files`, `list_directory` | 로컬 파일 관리, 코드 탐색 |
| **S3**| `@aws/s3-mcp-server` | `list_objects`, `get_object`, `put_object` | S3 파일 관리 |
| **Google Cloud Storage**| `mcp-server-gcs` (커뮤니티) | `list_blobs`, `read_blob`, `upload_blob` | GCS 파일 관리 |

### 모니터링 & 관측

| 서버 | 패키지 / 리포 | 주요 Tool | 활용 사례 |
|------|-------------|-----------|----------|
| **Datadog**| `mcp-server-datadog` (커뮤니티) | `query_metrics`, `list_monitors`, `get_events` | 메트릭 조회, 알림 관리 |
| **Grafana**| `mcp-server-grafana` (커뮤니티) | `query_dashboard`, `list_alerts`, `search_dashboards` | 대시보드 조회, 알림 확인 |
| **PagerDuty**| `mcp-server-pagerduty` (커뮤니티) | `list_incidents`, `acknowledge_incident`, `resolve_incident` | 인시던트 관리 |
| **Prometheus**| `mcp-server-prometheus` (커뮤니티) | `query`, `query_range`, `list_alerts` | 메트릭 쿼리, 알림 조회 |

---

## 실전 자동화 시나리오

여러 MCP 서버를 조합하여 강력한 워크플로를 구성할 수 있습니다. 아래는 업계에서 가장 많이 활용되는 시나리오들입니다.

### 시나리오 1: 데이터 파이프라인 모니터링 → 장애 알림

**사용 MCP**: Databricks SQL + Slack + JIRA

```
"어제 실행된 ETL 잡 중 실패한 것이 있는지 확인하고,
실패한 잡이 있으면 Slack #data-ops에 알리고 JIRA 티켓도 생성해"
```

**동작 흐름:**
1. **Databricks SQL MCP**→ `system.lakeflow.job_runs` 테이블에서 실패한 잡 조회
2. **Slack MCP**→ `#data-ops` 채널에 실패 요약 메시지 전송
3. **JIRA MCP**→ 실패 상세 내용으로 Bug 티켓 생성

{% hint style="info" %}
**Genie Code에서 구현**: Databricks SQL은 Managed MCP로 기본 제공됩니다. Slack과 JIRA는 External MCP(Unity Catalog Connection)로 연결합니다.
{% endhint %}

---

### 시나리오 2: PR 리뷰 → 코드 품질 보고

**사용 MCP**: GitHub + Slack

```
"이번 주에 올라온 PR들 목록을 가져와서 리뷰 상태를 확인하고,
리뷰 안 된 PR이 있으면 Slack #engineering에 리마인더 보내줘"
```

**동작 흐름:**
1. **GitHub MCP**→ 리포의 오픈 PR 목록 조회 + 리뷰 상태 확인
2. **LLM 분석**→ 리뷰 지연 PR 필터링, 담당자별 그룹핑
3. **Slack MCP**→ 리뷰어별 멘션과 함께 리마인더 메시지 전송

---

### 시나리오 3: 고객 문의 → 자동 응답 초안

**사용 MCP**: Gmail + PostgreSQL + Slack

```
"오늘 들어온 고객 문의 이메일을 확인하고,
고객 DB에서 해당 고객 정보를 조회한 뒤,
응답 초안을 작성해서 Slack #cs-team에 검토 요청해줘"
```

**동작 흐름:**
1. **Gmail MCP**→ 미읽은 고객 문의 이메일 검색 및 내용 읽기
2. **PostgreSQL MCP**→ 고객 이메일로 CRM DB에서 고객 정보, 계약 상태 조회
3. **LLM 분석**→ 문의 내용 + 고객 정보를 종합하여 응답 초안 작성
4. **Slack MCP**→ CS 팀 채널에 원문 + 초안 + 고객 정보 요약 전송

---

### 시나리오 4: 인시던트 대응 자동화

**사용 MCP**: PagerDuty/Datadog + Kubernetes + Slack

```
"현재 Critical 알림이 있는지 확인하고,
관련 파드 로그를 가져와서 원인을 분석한 뒤,
Slack #incident에 분석 결과를 포스팅해줘"
```

**동작 흐름:**
1. **Datadog MCP**→ 활성 Critical 알림 목록 조회
2. **Kubernetes MCP**→ 관련 서비스의 파드 로그 수집
3. **LLM 분석**→ 로그 패턴 분석, 가능한 원인 추론
4. **Slack MCP**→ `#incident` 채널에 분석 보고서 전송

---

### 시나리오 5: 스프린트 보고서 자동 생성

**사용 MCP**: JIRA + GitHub + Notion

```
"이번 스프린트의 완료/미완료 이슈를 JIRA에서 가져오고,
관련 PR의 머지 상태를 GitHub에서 확인한 뒤,
Notion에 스프린트 회고 문서를 생성해줘"
```

**동작 흐름:**
1. **JIRA MCP**→ 현재 스프린트의 이슈 목록 + 상태 조회
2. **GitHub MCP**→ 각 이슈에 연결된 PR의 머지 상태 확인
3. **LLM 분석**→ 완료율, 지연 원인, 다음 스프린트 주의점 분석
4. **Notion MCP**→ 회고 템플릿으로 문서 자동 생성

---

### 시나리오 6: 일일 업무 브리핑

**사용 MCP**: Google Calendar + Gmail + JIRA + Slack

```
"오늘 일정과 미읽은 이메일, 할당된 JIRA 티켓을 정리해서
아침 브리핑을 만들어줘"
```

**동작 흐름:**
1. **Google Calendar MCP**→ 오늘 일정 조회
2. **Gmail MCP**→ 미읽은 중요 이메일 요약
3. **JIRA MCP**→ 나에게 할당된 In Progress / To Do 이슈 조회
4. **LLM 분석**→ 우선순위 정리, 시간 배분 제안
5. **Slack MCP**→ DM으로 브리핑 전송 (선택)

---

### 시나리오 7: 데이터 품질 모니터링 → 보고

**사용 MCP**: Databricks SQL + Google Sheets + Slack

```
"주요 테이블의 null 비율, 중복 레코드, 최신성을 체크하고,
결과를 Google Sheets에 기록한 뒤, 이상이 있으면 Slack에 알려줘"
```

**동작 흐름:**
1. **Databricks SQL MCP**→ 데이터 품질 쿼리 실행 (null 비율, 중복, 최종 업데이트 시간)
2. **Google Sheets MCP**→ 품질 메트릭을 일별 시트에 기록
3. **LLM 분석**→ 임계치 초과 항목 판별
4. **Slack MCP**→ 이상 항목이 있으면 `#data-quality` 채널에 알림

---

### 시나리오 8: 경쟁사 모니터링

**사용 MCP**: Brave Search + Notion + Slack

```
"Snowflake, Redshift 관련 최신 뉴스를 검색하고,
주요 내용을 Notion '경쟁사 인텔리전스' DB에 추가하고,
요약을 Slack #competitive에 공유해줘"
```

**동작 흐름:**
1. **Brave Search MCP**→ 경쟁사 키워드로 최신 뉴스/블로그 검색
2. **LLM 분석**→ 핵심 내용 추출, 비즈니스 영향도 평가
3. **Notion MCP**→ 경쟁사 인텔리전스 DB에 새 항목 추가
4. **Slack MCP**→ 요약 리포트를 관련 채널에 공유

---

### 시나리오 9: 코드 변경 → 문서 자동 업데이트

**사용 MCP**: GitHub + Confluence

```
"최근 PR에서 API가 변경된 부분을 확인하고,
Confluence의 API 문서를 업데이트해줘"
```

**동작 흐름:**
1. **GitHub MCP**→ 최근 머지된 PR에서 API 관련 파일 변경 확인
2. **LLM 분석**→ 변경된 엔드포인트, 파라미터, 응답 포맷 정리
3. **Confluence MCP**→ 해당 API 문서 페이지 업데이트

---

### 시나리오 10: 주간 팀 성과 대시보드

**사용 MCP**: GitHub + JIRA + Slack + Google Sheets

```
"이번 주 팀의 PR 수, 코드 리뷰 수, 완료된 JIRA 이슈 수를 집계하고,
Google Sheets에 기록한 뒤 Slack에 요약 보고해줘"
```

**동작 흐름:**
1. **GitHub MCP**→ 이번 주 PR 수, 리뷰 수, 코드 변경량 집계
2. **JIRA MCP**→ 완료된 이슈 수, 스토리 포인트 합산
3. **Google Sheets MCP**→ 주간 트래킹 시트에 데이터 추가
4. **LLM 분석**→ 전주 대비 트렌드 분석
5. **Slack MCP**→ `#team-metrics` 채널에 주간 보고

---

## Genie Code에 외부 MCP 서버 추가하기

Databricks Genie Code에서 외부 MCP 서버를 사용하려면 **Unity Catalog Connection**을 통해 연결합니다.

### 방법 1: Managed OAuth (권장)

Databricks가 OAuth 흐름을 관리합니다. 현재 지원되는 서비스:

| 서비스 | 연결 방법 |
|--------|----------|
| **GitHub**| Workspace Settings → Connections → GitHub (OAuth) |
| **Slack**| Workspace Settings → Connections → Slack (OAuth) |
| **Google Drive**| Workspace Settings → Connections → Google Drive (OAuth) |
| **SharePoint**| Workspace Settings → Connections → SharePoint (OAuth) |
| **Glean**| Workspace Settings → Connections → Glean (OAuth) |
| **JIRA**| Workspace Settings → Connections → Jira (OAuth) |

**설정 절차:**

```
1. Databricks Workspace → Catalog Explorer → External Connections
2. "Create Connection" 클릭
3. Connection Type: "MCP Server" 선택
4. 서비스 선택 (GitHub, Slack 등)
5. OAuth 인증 완료
6. Genie Code 설정 → MCP Servers → 생성한 Connection 추가
```

### 방법 2: Custom HTTP Connection

Streamable HTTP를 지원하는 모든 MCP 서버에 연결할 수 있습니다.

```sql
-- Unity Catalog에서 HTTP Connection 생성
CREATE CONNECTION my_mcp_server
TYPE mcp
OPTIONS (
  url = 'https://my-mcp-server.example.com/mcp',
  auth_type = 'bearer',
  token = secret('scope', 'my-mcp-token')
);
```

### 방법 3: Databricks Apps로 커스텀 MCP 호스팅

자체 MCP 서버를 Databricks App으로 배포하고 Genie Code에 연결합니다:

```python
# app.py — FastAPI + MCP SDK
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("my-custom-tools")

@mcp.tool()
async def check_pipeline_status(pipeline_name: str) -> str:
    """데이터 파이프라인 상태를 확인합니다."""
    # Databricks API 호출
    ...

# MCP 엔드포인트를 FastAPI에 마운트
app.mount("/mcp", mcp.get_asgi_app())
```

```yaml
# app.yaml
command:
  - uvicorn
  - app:app
  - --host=0.0.0.0
  - --port=8000
env:
  - name: DATABRICKS_HOST
    valueFrom: resources.databricks_host
resources:
  - name: databricks_host
    type: databricks_host
```

{% hint style="warning" %}
**Genie Code 제한**: 전체 MCP 서버에 걸쳐 **최대 20개 Tool**만 사용할 수 있습니다. 핵심 도구만 선택적으로 등록하세요.
{% endhint %}

---

## Claude Code에 MCP 서버 추가하기

Claude Code(CLI)에서는 `claude mcp add` 명령어로 간편하게 추가합니다.

### 자주 사용하는 조합 예시

```bash
# Slack — 메시지 전송 및 검색
claude mcp add slack \
  -e SLACK_BOT_TOKEN=xoxb-your-token \
  -- npx -y @modelcontextprotocol/server-slack

# GitHub — 리포 관리, PR, 이슈
claude mcp add github \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx \
  -- npx -y @modelcontextprotocol/server-github

# PostgreSQL — DB 쿼리
claude mcp add postgres \
  -- npx -y @modelcontextprotocol/server-postgres \
  "postgresql://user:pass@localhost:5432/mydb"

# Notion — 문서 관리
claude mcp add notion \
  -e NOTION_API_KEY=ntn_xxx \
  -- npx -y @notionhq/notion-mcp-server

# Brave Search — 웹 검색
claude mcp add brave-search \
  -e BRAVE_API_KEY=BSA_xxx \
  -- npx -y @modelcontextprotocol/server-brave-search

# Filesystem — 로컬 파일 접근
claude mcp add files \
  -- npx -y @modelcontextprotocol/server-filesystem /path/to/project

# JIRA — 이슈 관리
claude mcp add jira \
  -e JIRA_URL=https://your-org.atlassian.net \
  -e JIRA_EMAIL=your@email.com \
  -e JIRA_API_TOKEN=xxx \
  -- npx -y mcp-server-atlassian

# 등록된 서버 확인
claude mcp list
```

### 프로젝트 설정 파일 (.mcp.json)

팀 전체가 같은 MCP 서버를 사용하도록 프로젝트 루트에 `.mcp.json`을 생성합니다:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-postgres",
        "${DATABASE_URL}"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

{% hint style="tip" %}
`${ENV_VAR}` 구문으로 환경변수를 참조하면, `.mcp.json`을 git에 커밋해도 토큰이 노출되지 않습니다. 팀원은 각자 환경변수만 설정하면 됩니다.
{% endhint %}

---

## 시나리오별 권장 MCP 조합

| 역할/업무 | 권장 MCP 서버 | 핵심 활용 |
|----------|-------------|----------|
| **데이터 엔지니어**| Databricks SQL + Slack + GitHub | 파이프라인 모니터링, 장애 알림, 코드 관리 |
| **데이터 분석가**| Databricks SQL + Google Sheets + Slack | 데이터 조회, 보고서 자동화, 결과 공유 |
| **백엔드 개발자**| GitHub + JIRA + PostgreSQL + Slack | 코드 리뷰, 이슈 추적, DB 디버깅 |
| **DevOps/SRE**| Kubernetes + Datadog + PagerDuty + Slack | 인시던트 대응, 로그 분석, 알림 관리 |
| **프로덕트 매니저**| JIRA + Notion + Slack + Google Calendar | 스프린트 관리, 문서화, 일정 관리 |
| **SA/SE (솔루션 아키텍트)**| Databricks MCP + GitHub + Slack + Brave Search | 고객 지원, PoC, 기술 리서치 |

---

## MCP 서버 선택 시 체크리스트

MCP 서버를 선택할 때 확인해야 할 항목들입니다:

| 항목 | 확인 사항 |
|------|----------|
| **공식 여부**| Anthropic 공식, 벤더 공식(Notion, AWS 등), 커뮤니티 중 어디에 해당하는가? |
| **활성도**| GitHub Star 수, 최근 커밋 날짜, 이슈 응답 속도 |
| **보안**| API 키 관리 방식, 최소 권한 지원, 데이터 전송 암호화 |
| **전송 방식**| stdio만 지원? Streamable HTTP도 지원? (Databricks 연동 시 HTTP 필수) |
| **Tool 수**| 제공하는 Tool이 너무 많으면 LLM의 선택 정확도 하락 |
| **에러 처리**| 실패 시 의미 있는 에러 메시지를 반환하는가? |
| **문서화**| 설치 가이드, Tool 설명, 예제가 충분한가? |

{% hint style="warning" %}
**커뮤니티 서버 주의사항**: 커뮤니티 MCP 서버는 공식 서버에 비해 유지보수가 불안정할 수 있습니다. 프로덕션 환경에서는 반드시 코드를 검토하고, 가능하면 공식 서버나 벤더 공식 서버를 우선 사용하세요.
{% endhint %}

---

## 다음 단계

- [MCP 개요](README.md): MCP 프로토콜의 기본 개념
- [일반 MCP 설정](setup-general.md): 클라이언트별 상세 설정 방법
- [Databricks MCP 활용](databricks-mcp.md): Databricks 환경의 Managed/External/Custom MCP
- [베스트 프랙티스](best-practices.md): 보안, Tool 설계, 비용 최적화
