# AI Dev Kit

> **최종 업데이트**: 2026-03-31

## AI Dev Kit이란?

**AI Dev Kit** 은 Databricks Field Engineering 팀이 개발하고 유지보수하는 **오픈소스 프로젝트** 입니다. Claude Code와 Databricks 워크스페이스를 연결하는 통합 도구 모음으로, 자연어로 Databricks의 모든 리소스를 조작할 수 있는 **AI 기반 개발 환경** 을 제공합니다.

{% hint style="info" %}
GitHub 저장소: [databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit)
{% endhint %}

기존에는 Databricks 워크스페이스에서 테이블을 생성하거나, 파이프라인을 구성하거나, 대시보드를 배포하려면 각각의 API를 직접 호출하거나 UI를 클릭해야 했습니다. AI Dev Kit은 이 모든 작업을 **자연어 한 문장** 으로 가능하게 만듭니다. "매출 데이터 분석 환경을 만들어줘"라고 말하면, 에이전트가 테이블 생성부터 대시보드 배포, Genie Space 구성까지 자동으로 수행합니다.

---

## 왜 AI Dev Kit인가?

### 기존 방식의 한계

| 작업 | 기존 방식 | AI Dev Kit |
|------|----------|------------|
| **테이블 생성** | SQL 에디터에서 DDL 직접 작성 | "고객 테이블을 만들어줘" |
| **DLT 파이프라인** | JSON 설정 작성 + API 호출 | "Bronze-Silver-Gold 파이프라인 구성해줘" |
| **대시보드** | Lakeview UI에서 수동 구성 | "매출 추이 대시보드를 만들어줘" |
| **RAG 구축** | Vector Search + Agent Framework 직접 코딩 | "PDF 기반 Q&A 챗봇 만들어줘" |
| **Job 스케줄링** | REST API 또는 UI에서 설정 | "매일 6시에 재학습 파이프라인 실행해줘" |

### AI Dev Kit이 해결하는 문제

1. **파편화된 도구 통합**-- Databricks에는 SQL Warehouse, Cluster, DLT, Jobs, Unity Catalog, Vector Search, Genie, Dashboard 등 수십 개의 서비스가 있습니다. AI Dev Kit은 이 모든 서비스를 하나의 에이전트 인터페이스로 통합합니다.

2. **진입 장벽 제거**-- Databricks API 사양을 몰라도 자연어로 원하는 작업을 요청할 수 있습니다. 에이전트가 올바른 API 호출 순서, 파라미터, 에러 처리를 자동으로 수행합니다.

3. **반복 작업 자동화**-- 데모 환경 구축, 합성 데이터 생성, 파이프라인 템플릿 구성 등 반복적인 작업을 대화 몇 문장으로 완료합니다.

4. **베스트 프랙티스 내장**-- 29개의 스킬 파일이 Databricks 권장 패턴(메달리온 아키텍처, Unity Catalog 권한 모델, Agent Bricks 구성 등)을 에이전트에게 가르칩니다.

---

## 핵심 구성 요소

AI Dev Kit은 크게 세 가지 핵심 컴포넌트로 구성됩니다.

### 1. Databricks MCP Server

**Model Context Protocol(MCP)** 표준을 사용하여 Databricks 워크스페이스의 **30개 이상의 도구** 를 외부 AI 에이전트에 노출합니다. Claude Code, VS Code Copilot, Cursor 등 MCP를 지원하는 모든 클라이언트에서 Databricks를 제어할 수 있습니다.

| 도구 카테고리 | 주요 기능 | 도구 수 |
|---|---|---|
| **SQL 실행** | 쿼리 실행, 멀티 쿼리 | 2 |
| **Compute** | 클러스터/Warehouse 관리 | 6 |
| **DLT 파이프라인** | 생성, 실행, 모니터링 | 10 |
| **파일 관리** | Volume 업로드/다운로드 | 9 |
| **Jobs** | Job 생성, 실행, 스케줄링 | 2 |
| **Genie** | Space 생성, 질의 | 4 |
| **Dashboard** | 생성, 배포 | 4 |
| **Model Serving** | 추론, 상태 조회 | 3 |
| **Unity Catalog** | 객체, 권한, 태그, 공유 관리 | 8 |
| **Vector Search** | Endpoint, Index, 검색 | 6 |
| **기타** | Workspace, Apps, KA, MAS 등 | 8 |

{% hint style="info" %}
MCP Server는 독립적으로 사용할 수 있습니다. Builder App 없이도 Claude Code의 `claude_desktop_config.json`에 MCP Server를 등록하면 바로 Databricks 도구를 사용할 수 있습니다.
{% endhint %}

### 2. Builder App

**React + FastAPI** 기반의 풀스택 웹 애플리케이션입니다. Claude Agent와 대화하며 Databricks 작업을 수행하는 **웹 기반 인터페이스** 를 제공합니다. Databricks Apps에 배포하면 팀 전체가 브라우저에서 에이전트를 사용할 수 있습니다.

| 계층 | 기술 스택 | 역할 |
|---|---|---|
| **Frontend** | React + TypeScript | 채팅 UI, 프로젝트 관리, 스킬 탐색 |
| **Backend** | FastAPI + Uvicorn | 에이전트 세션 관리, SSE 스트리밍, REST API |
| **Agent Runtime** | Claude Agent SDK | 도구 호출, 세션 재개, 비동기 실행 |
| **Persistence** | Lakebase (PostgreSQL) | 프로젝트, 대화 이력, 실행 결과 영구 저장 |
| **Auth** | contextvars 기반 | 요청별 자격 증명 격리, 멀티 유저 지원 |

{% hint style="tip" %}
Builder App에 대한 상세 소개는 [Builder App](builder-app.md) 서브페이지를 참고하세요.
{% endhint %}

### 3. Skills & Plugins

**29개의 마크다운 기반 스킬 파일** 이 에이전트에게 Databricks 작업 수행 방법을 가르칩니다. 합성 데이터 생성, 대시보드 구성, Genie Space 설정, DLT 파이프라인 패턴 등 Databricks 전문 지식이 스킬 파일로 인코딩되어 있습니다.

| 스킬 카테고리 | 포함 스킬 |
|---|---|
| **데이터 엔지니어링** | synthetic-data, sdp, unity-catalog, jobs |
| **분석 & BI** | dashboard, genie-space, metric-views |
| **AI & ML** | agent-bricks, vector-search, mlflow, model-serving |
| **인프라** | apps, dabs, lakebase, python-sdk |

에이전트는 사용자 요청에 따라 관련 스킬을 자동으로 로드하고, 스킬에 정의된 패턴에 맞춰 작업을 수행합니다. 예를 들어 "대시보드를 만들어줘"라고 요청하면, `dashboard` 스킬을 참조하여 올바른 Lakeview JSON 구조를 생성합니다.

---

## 아키텍처

AI Dev Kit의 전체 아키텍처는 다음과 같습니다.

| 계층 | 구성 요소 | 설명 |
|------|----------|------|
| **사용자** | 브라우저 / Claude Code CLI | 자연어 요청 입력 |
| **에이전트** | Claude Agent SDK | 요청 분석, 도구 선택, 실행 계획 수립 |
| **프로토콜** | MCP (Model Context Protocol) | 에이전트와 도구 사이의 표준 통신 규격 |
| **도구** | Databricks MCP Server | 30+ Databricks API를 MCP 도구로 노출 |
| **인프라** | Databricks Workspace | SQL Warehouse, Cluster, Unity Catalog 등 실제 리소스 |

### 동작 흐름

```
사용자 요청
   ↓
Claude Agent (요청 분석 + 스킬 로드)
   ↓
MCP Protocol
   ↓
Databricks MCP Server (도구 실행)
   ↓
Databricks Workspace (API 호출)
   ↓
결과 반환 → 에이전트 해석 → 사용자에게 응답
```

### 두 가지 사용 모드

| 모드 | 인터페이스 | 특징 |
|------|----------|------|
| **CLI 모드** | Claude Code 터미널 | 개발자 친화적, 파일 편집 + Databricks 도구 동시 사용 |
| **Web 모드** | Builder App 브라우저 | 비개발자도 사용 가능, 팀 공유, 프로젝트 관리 |

---

## 시작하기

### CLI 모드 (Claude Code + MCP Server)

Claude Code에서 Databricks MCP Server를 바로 사용하는 방법입니다.

**1단계: MCP Server 설치**

```bash
# AI Dev Kit 클론
git clone https://github.com/databricks-solutions/ai-dev-kit.git
cd ai-dev-kit/databricks-mcp-server

# 의존성 설치
uv venv && source .venv/bin/activate
uv pip install -e .
```

**2단계: Claude Code에 MCP Server 등록**

`~/.claude/claude_desktop_config.json`에 다음을 추가합니다:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uv",
      "args": ["--directory", "/path/to/ai-dev-kit/databricks-mcp-server", "run", "server"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapixxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

**3단계: 사용**

```bash
claude
> 내 워크스페이스의 카탈로그 목록을 보여줘
```

### Web 모드 (Builder App)

Builder App을 로컬 또는 Databricks Apps에 배포하여 사용하는 방법입니다. 상세 절차는 아래 서브페이지를 참고하세요.

---

## 서브페이지 안내

| 페이지 | 설명 |
|--------|------|
| [Builder App](builder-app.md) | Builder App 개요 -- 아키텍처, 핵심 컴포넌트, AI Playground와 비교 |
| [Getting Started](getting-started.md) | 로컬 환경 설치부터 첫 프로젝트 생성까지 단계별 가이드 |
| [배포 가이드](deployment-guide.md) | Databricks Apps 배포 전체 절차 -- Lakebase, LLM 선택, 트러블슈팅 |
| [Tool 목록 및 상세](tools.md) | MCP 도구 30개+ 전체 목록, Built-in Tools, Skills System 상세 |
| [활용 사례](use-cases.md) | 데이터 분석, RAG 구축, MLOps, 데모 환경 등 실전 시나리오 |

---

## 관련 자료

| 자료 | 링크 |
|------|------|
| **GitHub 저장소** | [databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit) |
| **MCP Server 소스** | [ai-dev-kit/databricks-mcp-server](https://github.com/databricks-solutions/ai-dev-kit/tree/main/databricks-mcp-server) |
| **Builder App 소스** | [ai-dev-kit/databricks-builder-app](https://github.com/databricks-solutions/ai-dev-kit/tree/main/databricks-builder-app) |
| **Skills 소스** | [ai-dev-kit/databricks-skills](https://github.com/databricks-solutions/ai-dev-kit/tree/main/databricks-skills) |
| **Claude Agent SDK** | [Anthropic Agent 문서](https://docs.anthropic.com/en/docs/agents) |
| **MCP 프로토콜 규격** | [modelcontextprotocol.io](https://modelcontextprotocol.io/) |
| **슬라이드** | [GenAI 소개 슬라이드](https://simyungyang.github.io/databricks-enablement-blog/genai-genie-code-ai-dev-kit.html) |
| **PDF** | [GenAI 소개](https://simyungyang.github.io/databricks-enablement-blog/genai-intro.pdf) / [AI Dev Kit 상세](https://simyungyang.github.io/databricks-enablement-blog/ai-dev-kit-guide.pdf) |

{% hint style="info" %}
AI Dev Kit은 활발히 개발 중인 프로젝트입니다. 최신 변경 사항은 [GitHub 저장소](https://github.com/databricks-solutions/ai-dev-kit)에서 확인하세요.
{% endhint %}
