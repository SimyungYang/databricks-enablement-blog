# AI Dev Kit Builder App

## Builder App이란?

**AI Dev Kit Builder App** 은 Databricks 워크스페이스에서 Claude Code 에이전트와 대화하며 데이터 엔지니어링, 분석, AI 작업을 수행할 수 있는 **풀스택 웹 애플리케이션** 입니다. React 프론트엔드와 FastAPI 백엔드로 구성되며, Claude Agent SDK와 Databricks MCP Server를 통합하여 30개 이상의 Databricks 도구를 자연어로 실행할 수 있습니다.

{% hint style="info" %}
Builder App은 [AI Dev Kit](https://github.com/databricks-solutions/ai-dev-kit) 프로젝트의 `databricks-builder-app` 컴포넌트입니다. Databricks Field Engineering 팀이 관리하는 공식 솔루션입니다.
{% endhint %}

### Builder App이 필요한 이유

Claude Code CLI는 개발자에게 최적화되어 있지만, **비개발자(분석가, PM, 관리자)** 가 사용하기에는 진입 장벽이 있습니다. Builder App은 다음 문제를 해결합니다:

| 문제 | CLI 모드 | Builder App |
|------|---------|-------------|
| **비개발자 접근성** | 터미널 사용 필요 | 브라우저 기반 채팅 UI |
| **팀 공유** | 개인 환경에서만 사용 | Databricks Apps로 팀 전체에 배포 |
| **대화 이력** | 세션 종료 시 소실 | Lakebase에 영구 저장 |
| **프로젝트 관리** | 파일 시스템 기반 | 웹 UI에서 프로젝트별 분리 관리 |
| **인증 관리** | 개인 토큰 | 요청별 자격 증명 격리 (멀티 유저) |

### MCP 통합 아키텍처

Builder App의 핵심은 **MCP (Model Context Protocol)** 통합입니다. MCP는 에이전트와 도구 사이의 표준 통신 규격으로, Builder App에서는 다음과 같이 작동합니다:

```
[사용자 입력] → [FastAPI 백엔드] → [Claude Agent SDK]
                                        │
                                   MCP Protocol
                                        │
                                 [Databricks MCP Server]
                                        │
                              ┌─────────┼─────────┐
                              │         │         │
                          SQL API   Jobs API   VS API  ... (30+ 도구)
```

**MCP 통합의 장점:**
- **자동 도구 발견**: 에이전트가 사용 가능한 도구를 자동으로 인식합니다. 새 도구가 추가되면 코드 변경 없이 바로 사용 가능합니다.
- **표준화된 인터페이스**: 모든 도구가 동일한 프로토콜로 통신하므로, 에이전트의 도구 호출 로직이 단순해집니다.
- **확장성**: 커스텀 MCP Server를 추가하여 Databricks 외 도구(Slack, JIRA, Confluence 등)도 통합할 수 있습니다.

---

## 아키텍처

Builder App은 프론트엔드, 백엔드, 에이전트 런타임, MCP 도구의 4계층으로 구성됩니다. 각 계층은 독립적으로 확장 가능하며, 명확한 인터페이스로 분리되어 있습니다.

### Frontend (React)

| 모듈 | 역할 |
|---|---|
| **HomePage** | 프로젝트 목록 및 생성 |
| **ProjectPage** | 채팅 UI, 에이전트와 대화 |
| **DocPage** | 문서 뷰어 |
| **SkillsExplorer** | 스킬 탐색 및 관리 |
| **ProjectsContext** | 프로젝트 상태 관리 |
| **UserContext** | 사용자 인증 컨텍스트 |

### Backend (FastAPI)

| 엔드포인트 | 역할 |
|---|---|
| `POST /api/invoke_agent` | 에이전트 실행 시작, execution_id 반환 |
| `POST /api/stream_progress/{id}` | SSE 스트리밍으로 에이전트 이벤트 수신 |
| `POST /api/stop_stream/{id}` | 실행 중인 에이전트 취소 |
| `/api/projects` CRUD | 프로젝트 관리 |
| `/api/conversations` CRUD | 대화 이력 관리 |
| `/api/clusters`, `/api/warehouses` | 컴퓨팅 리소스 조회 |
| `/api/skills` | 스킬 파일 관리 |

### Agent Runtime & Tools

| 계층 | 구성 |
|---|---|
| **Agent Service** | Claude Agent SDK 기반 세션 관리, SSE 스트리밍 |
| **Built-in Tools** | Read, Write, Edit, Glob, Grep, Skill |
| **MCP Tools** | SQL, Compute, Pipelines, Files, Jobs, Genie, Dashboards, Model Serving, UC 등 30+ 도구 |

---

## 핵심 컴포넌트 6가지

### 1. Databricks MCP Server Tools
30개 이상의 도구로 SQL 실행, 클러스터 관리, DLT 파이프라인, 파일 업로드, Genie Space, 대시보드, 모델 서빙, Unity Catalog 등을 에이전트가 직접 제어합니다.

### 2. Claude Agent SDK
프로덕션급 에이전트 런타임으로, 세션 재개(Session Resumption), 빌트인 도구, SSE 스트리밍을 지원합니다.

### 3. Skills System
29개의 마크다운 기반 스킬 파일이 에이전트에게 Databricks 작업 수행 방법을 가르칩니다. 합성 데이터 생성, 대시보드 구성, Genie, SDP, UC, Python SDK, Agent Bricks, Lakebase, Jobs 등의 패턴을 포함합니다.

### 4. Async Operation Handling
10초 이상 소요되는 장시간 작업을 백그라운드 스레드에서 실행하고, `operation_id`로 폴링하여 결과를 수신합니다.

### 5. Lakebase Persistence
PostgreSQL(Lakebase) 스키마와 Alembic 마이그레이션으로 Projects, Conversations, Messages, Executions를 영구 저장합니다.

### 6. Multi-User Auth
Python `contextvars`를 사용하여 요청별 자격 증명을 격리하고, 각 사용자의 Databricks 권한으로 도구를 실행합니다.

---

## 무엇을 할 수 있나?

Builder App 에이전트와 대화하여 다음 작업을 수행할 수 있습니다:

- **SQL 실행**- 자연어로 쿼리 작성 및 실행, 결과 분석
- **대시보드 생성**- AI/BI 대시보드를 코드 없이 구성 및 배포
- **Genie Space 관리**- Genie Space 생성, 업데이트, 질의
- **DLT 파이프라인 구성**- Spark Declarative Pipeline 생성 및 실행
- **파일 관리**- Volume에 파일 업로드/다운로드
- **Job 스케줄링**- Databricks Jobs 생성 및 실행 관리
- **모델 서빙**- Serving Endpoint 상태 확인 및 쿼리
- **Unity Catalog 관리**- 카탈로그, 스키마, 테이블, 권한 관리
- **벡터 검색**- Vector Search Index 생성 및 쿼리

---

## AI Playground와의 차이점

| 비교 항목 | AI Playground | AI Dev Kit Builder App |
|---|---|---|
| **성격** | 노코드 프로토타이핑 도구 | 풀스택 에이전트 애플리케이션 |
| **호스팅** | Databricks Workspace 내장 | 자체 배포 (Databricks Apps 또는 로컬) |
| **에이전트 런타임** | Databricks Agent Framework | Claude Agent SDK |
| **도구 접근** | UI에서 Tool 선택 | MCP Server 30+ 도구 자동 연결 |
| **코드 실행** | Export 후 노트북에서 실행 | 에이전트가 직접 파일 생성/편집/실행 |
| **데이터 영속성** | 세션 기반 | Lakebase(PostgreSQL)로 프로젝트/대화 영구 저장 |
| **멀티 유저** | Workspace 계정 기반 | 요청별 자격 증명 격리 |

{% hint style="tip" %}
AI Playground는 모델 비교와 빠른 프로토타이핑에 적합하고, Builder App은 Databricks 워크스페이스 전체를 에이전트가 관리하는 풀스택 개발 환경입니다.
{% endhint %}

---

## Builder App의 보안 모델

### 멀티 유저 인증 격리

Builder App은 **요청별 자격 증명 격리** 를 구현합니다. Python의 `contextvars`를 사용하여 각 HTTP 요청에 바인딩된 사용자 토큰이 해당 요청의 MCP 도구 호출에만 사용됩니다.

```
사용자 A (admin 권한) → 요청 A → MCP 도구 호출 시 admin 토큰 사용
사용자 B (viewer 권한) → 요청 B → MCP 도구 호출 시 viewer 토큰 사용
→ 사용자 B는 쓰기 작업 불가 (Databricks 권한 모델에 의해 차단)
```

이 설계의 핵심 장점:
- **권한 상속**: 사용자의 Databricks 워크스페이스 권한이 그대로 적용됩니다
- **감사 추적**: 모든 API 호출이 실제 사용자 계정으로 기록됩니다
- **격리 보장**: 한 사용자의 요청이 다른 사용자의 권한으로 실행되는 것이 불가능합니다

### Databricks Apps 환경의 자동 인증

Databricks Apps에 배포하면 **별도의 토큰 관리가 필요 없습니다**:

1. 사용자가 Databricks 워크스페이스에 SSO로 로그인합니다
2. Builder App에 접근하면, 워크스페이스가 `X-Forwarded-User`와 `X-Forwarded-Access-Token` 헤더를 자동으로 주입합니다
3. Builder App은 이 헤더에서 사용자 정보와 토큰을 추출하여 MCP 도구 호출에 사용합니다

{% hint style="warning" %}
Builder App은 에이전트가 **사용자의 권한으로**Databricks API를 호출합니다. 에이전트에게 "이 카탈로그를 삭제해줘"라고 요청하면, 해당 사용자에게 삭제 권한이 있다면 실제로 삭제됩니다. **프로덕션 환경에서는 사용자 권한을 적절히 제한하세요**.
{% endhint %}

---

## 주요 사용 패턴

Builder App을 효과적으로 활용하기 위한 주요 대화 패턴입니다:

### 구체적 요청이 더 좋은 결과를 만든다

| 모호한 요청 | 구체적 요청 | 차이 |
|------------|-----------|------|
| "테이블 만들어줘" | "main.analytics 스키마에 고객 테이블을 만들어줘. customer_id, name, email, created_at 컬럼으로" | 스키마, 컬럼 구조 명확 |
| "데이터 보여줘" | "main.sales.orders 테이블의 최근 7일 매출을 일별로 집계해서 보여줘" | 테이블명, 기간, 집계 방식 명확 |
| "대시보드 만들어" | "매출 추이 라인 차트와 카테고리별 파이 차트로 대시보드를 만들어줘" | 차트 유형 명확 |

### 단계별 대화가 복잡한 작업에 효과적

복잡한 작업은 한 번에 요청하기보다 **단계별로 대화** 하는 것이 효과적입니다:

1. "먼저 IoT 센서 데이터용 테이블 스키마를 설계해줘" (스키마 리뷰)
2. "좋아, 이 스키마로 테이블을 만들고 샘플 데이터 100건을 넣어줘" (리소스 생성)
3. "이 데이터로 실시간 모니터링 대시보드를 만들어줘" (시각화)

---

## 참고 링크

- [AI Dev Kit GitHub](https://github.com/databricks-solutions/ai-dev-kit)
- [Builder App 소스코드](https://github.com/databricks-solutions/ai-dev-kit/tree/main/databricks-builder-app)
- [Databricks MCP Server](https://github.com/databricks-solutions/ai-dev-kit/tree/main/databricks-mcp-server)
- [Claude Agent SDK](https://docs.anthropic.com/en/docs/agents)
- [MCP Protocol 규격](https://modelcontextprotocol.io/)
