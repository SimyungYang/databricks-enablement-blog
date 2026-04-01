# AI Dev Kit Builder App

## Builder App이란?

**AI Dev Kit Builder App**은 Databricks 워크스페이스에서 Claude Code 에이전트와 대화하며 데이터 엔지니어링, 분석, AI 작업을 수행할 수 있는 **풀스택 웹 애플리케이션**입니다. React 프론트엔드와 FastAPI 백엔드로 구성되며, Claude Agent SDK와 Databricks MCP Server를 통합하여 30개 이상의 Databricks 도구를 자연어로 실행할 수 있습니다.

{% hint style="info" %}
Builder App은 [AI Dev Kit](https://github.com/databricks-solutions/ai-dev-kit) 프로젝트의 `databricks-builder-app` 컴포넌트입니다. Databricks Field Engineering 팀이 관리하는 공식 솔루션입니다.
{% endhint %}

---

## 아키텍처

Builder App은 프론트엔드, 백엔드, 에이전트 런타임, MCP 도구의 4계층으로 구성됩니다.

### Frontend (React)

| 모듈 | 역할 |
|---|---|
| **HomePage**| 프로젝트 목록 및 생성 |
| **ProjectPage**| 채팅 UI, 에이전트와 대화 |
| **DocPage**| 문서 뷰어 |
| **SkillsExplorer**| 스킬 탐색 및 관리 |
| **ProjectsContext**| 프로젝트 상태 관리 |
| **UserContext**| 사용자 인증 컨텍스트 |

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
| **Agent Service**| Claude Agent SDK 기반 세션 관리, SSE 스트리밍 |
| **Built-in Tools**| Read, Write, Edit, Glob, Grep, Skill |
| **MCP Tools**| SQL, Compute, Pipelines, Files, Jobs, Genie, Dashboards, Model Serving, UC 등 30+ 도구 |

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
| **성격**| 노코드 프로토타이핑 도구 | 풀스택 에이전트 애플리케이션 |
| **호스팅**| Databricks Workspace 내장 | 자체 배포 (Databricks Apps 또는 로컬) |
| **에이전트 런타임**| Databricks Agent Framework | Claude Agent SDK |
| **도구 접근**| UI에서 Tool 선택 | MCP Server 30+ 도구 자동 연결 |
| **코드 실행**| Export 후 노트북에서 실행 | 에이전트가 직접 파일 생성/편집/실행 |
| **데이터 영속성**| 세션 기반 | Lakebase(PostgreSQL)로 프로젝트/대화 영구 저장 |
| **멀티 유저**| Workspace 계정 기반 | 요청별 자격 증명 격리 |

{% hint style="tip" %}
AI Playground는 모델 비교와 빠른 프로토타이핑에 적합하고, Builder App은 Databricks 워크스페이스 전체를 에이전트가 관리하는 풀스택 개발 환경입니다.
{% endhint %}

---

## 참고 링크

- [AI Dev Kit GitHub](https://github.com/databricks-solutions/ai-dev-kit)
- [Builder App 소스코드](https://github.com/databricks-solutions/ai-dev-kit/tree/main/databricks-builder-app)
- [Databricks MCP Server](https://github.com/databricks-solutions/ai-dev-kit/tree/main/databricks-mcp-server)
- [Claude Agent SDK](https://docs.anthropic.com/en/docs/agents)
