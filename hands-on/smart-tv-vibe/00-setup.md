# Module 0: Databricks AI Dev Kit 설치 및 환경 구성

## 개요

Databricks AI Dev Kit은 AI 코딩 어시스턴트(Claude Code, Cursor, Windsurf 등)에게 Databricks 작업을 직접 실행할 수 있는 능력을 부여하는 오픈소스 툴킷입니다.

이 모듈에서는 AI Dev Kit을 설치하고, Databricks 워크스페이스에 연결하여 "AI 기반 개발(Vibe Coding)" 환경을 구축합니다.

---

## 사전 준비 사항

### 1. 필수 소프트웨어

| 도구 | 용도 | 설치 확인 |
|------|------|-----------|
| **Python 3.10+** | AI Dev Kit 실행 | `python3 --version` |
| **uv** | Python 패키지 관리자 | `uv --version` |
| **Databricks CLI** | 워크스페이스 연결 | `databricks --version` |
| **Claude Code**(또는 Cursor) | AI 코딩 어시스턴트 | `claude --version` |
| **Git** | 버전 관리 | `git --version` |

### 2. 필수 소프트웨어 설치

```bash
# uv 설치 (Python 패키지 관리자)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Databricks CLI 설치
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Claude Code 설치 (Node.js 필요)
npm install -g @anthropic-ai/claude-code
```

### 3. Databricks 워크스페이스 정보

교육 전에 아래 정보를 확인하세요:

| 항목 | 예시 |
|------|------|
| Workspace URL | `https://adb-xxxx.azuredatabricks.net` |
| Personal Access Token | `dapi...` |
| Catalog 이름 | `{catalog}` |
| Schema 이름 | `smart_tv` |

---

## Step 1: Databricks CLI 인증 설정

```bash
# Databricks CLI 프로파일 설정
databricks configure --profile SMARTTV_TRAINING

# 프롬프트에 아래 정보 입력:
# - Databricks Host: https://adb-xxxx.azuredatabricks.net
# - Personal Access Token: dapi...

# 연결 확인
databricks auth env --profile SMARTTV_TRAINING
```

### 환경 변수 설정 (대안)

```bash
export DATABRICKS_HOST="https://adb-xxxx.azuredatabricks.net"
export DATABRICKS_TOKEN="dapi..."
```

---

## Step 2: AI Dev Kit 설치

### Mac / Linux

```bash
# 원라인 설치 (권장)
bash <(curl -sL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/install.sh)
```

### 고급 설치 옵션

```bash
# 특정 Databricks CLI 프로파일 지정
bash <(curl -sL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/install.sh) \
 --profile SMARTTV_TRAINING --force

# 특정 도구만 설치 (예: Claude Code만)
bash <(curl -sL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/install.sh) \
 --tools claude

# 글로벌 설치 (모든 프로젝트에서 사용)
bash <(curl -sL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/install.sh) \
 --global --force
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/install.ps1 | iex
```

### 설치 확인

설치가 완료되면 아래 디렉토리가 생성됩니다:

```
~/.ai-dev-kit/
 repo/             # ai-dev-kit 소스코드
  databricks-mcp-server/    # MCP 서버 (50+ 도구)
  databricks-tools-core/    # Python 라이브러리
  databricks-skills/      # 19개 마크다운 스킬
  databricks-builder-app/   # Builder 웹앱
 .venv/             # Python 가상환경
 version            # 설치 버전
```

---

## Step 3: 설치 구성 요소 이해

### AI Dev Kit 아키텍처

```
┌─────────────────────────────────────────────────────┐
│         AI 코딩 어시스턴트           │
│     (Claude Code / Cursor / Windsurf)      │
├──────────────┬──────────────────────────────────────┤
│       │                    │
│ Skills   │    MCP Server           │
│ (마크다운)  │   (50+ 실행 도구)          │
│       │                    │
│ · 패턴   │ · SQL 실행    · 카탈로그 관리   │
│ · 베스트   │ · 잡 생성/관리   · MLflow 연동    │
│  프랙티스  │ · 파이프라인 관리  · 벡터 검색     │
│ · 코드 규약 │ · 앱 배포     · Agent Bricks   │
│       │                    │
├──────────────┴──────────────────────────────────────┤
│       databricks-tools-core          │
│       (공유 Python 라이브러리)          │
├─────────────────────────────────────────────────────┤
│       Databricks Workspace           │
│    (Unity Catalog, SQL Warehouse, Compute)     │
└─────────────────────────────────────────────────────┘
```

### 핵심 구성 요소

| 구성 요소 | 역할 | 교육에서의 활용 |
|-----------|------|-----------------|
| **databricks-skills** | AI에게 Databricks 패턴/규약을 가르치는 마크다운 문서 | 모든 실습에서 자동으로 활용됨 |
| **databricks-mcp-server** | AI가 Databricks 작업을 직접 실행하는 MCP 도구 | SQL 실행, 테이블 생성, 잡 관리 등 |
| **databricks-tools-core** | 공유 Python 라이브러리 | LangChain/OpenAI 등과 통합 시 활용 |

### 포함된 19개 스킬 목록

| 카테고리 | 스킬 |
|----------|------|
| **데이터 엔지니어링** | spark-declarative-pipelines, jobs, asset-bundles, synthetic-data-gen, iceberg |
| **SQL & 분석** | aibi-dashboards, unity-catalog, python-sdk |
| **GenAI & 에이전트** | vector-search, parsing, agent-evaluation, mlflow-tracing, mlflow-onboarding |
| **앱 개발** | app-apx (FastAPI+React), app-python (Streamlit/Dash/Flask) |
| **MLflow** | analyze-mlflow-trace, analyze-mlflow-chat-session, querying-mlflow-metrics |

---

## Step 4: 프로젝트 설정

### 교육용 프로젝트 디렉토리 구성

```bash
# 프로젝트 디렉토리 생성
mkdir -p ~/smarttv-training && cd ~/smarttv-training

# Git 초기화
git init

# AI Dev Kit 프로젝트 스코프 설치
bash <(curl -sL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/install.sh) \
 --profile SMARTTV_TRAINING
```

### 프로젝트 설정 파일 (.databricks-ai-dev-kit.yaml)

프로젝트 루트에 자동 생성되며, 팀과 공유할 수 있습니다:

```yaml
# .databricks-ai-dev-kit.yaml
project_name: smarttv-workshop
tags:
 team: smarttv-training
 domain: smart-tv
 use_case: personalized-recommendation
```

---

## Step 5: 연결 테스트

### Claude Code에서 테스트

```bash
# 프로젝트 디렉토리에서 Claude Code 실행
cd ~/smarttv-training
claude
```

Claude Code에서 아래 명령을 시도해보세요:

```
> Databricks에 연결되어 있는지 확인해줘

> 현재 워크스페이스에서 사용 가능한 카탈로그 목록을 보여줘

> SQL Warehouse 목록을 보여줘

> 다음 SQL을 실행해줘: SELECT current_user(), current_catalog(), current_schema()
```

### 기대 결과

- Databricks 워크스페이스 연결 상태 확인
- Unity Catalog의 카탈로그/스키마 목록 조회
- SQL Warehouse를 통한 쿼리 실행 성공

---

## 실습 체크리스트

- [ ] Python 3.10+ 설치 확인
- [ ] uv 설치 확인
- [ ] Databricks CLI 설치 및 프로파일 설정
- [ ] Claude Code (또는 Cursor) 설치
- [ ] AI Dev Kit 설치 완료
- [ ] Databricks 워크스페이스 연결 테스트 성공
- [ ] SQL 쿼리 실행 테스트 성공

---

## 트러블슈팅

### 자주 발생하는 문제

| 문제 | 해결 방법 |
|------|-----------|
| `databricks: command not found` | Databricks CLI 설치 후 터미널 재시작 |
| `uv: command not found` | `source ~/.bashrc` 또는 터미널 재시작 |
| 인증 오류 (401/403) | 토큰 만료 여부 확인, `databricks configure` 재실행 |
| MCP 서버 연결 실패 | `~/.ai-dev-kit/.venv/bin/python` 경로 확인 |
| Skills 로딩 안됨 | 프로젝트 디렉토리에서 Claude Code 실행 여부 확인 |

### MCP 서버 수동 테스트

```bash
# MCP 서버 직접 실행 테스트
~/.ai-dev-kit/.venv/bin/python -m databricks_mcp_server
```

---

## 다음 단계

환경 구성이 완료되었으면 **Module 1: Foundation** 으로 이동하여 Databricks Lakehouse 기초를 학습합니다.

→ [Module 1: Foundation - Lakehouse & Unity Catalog](../01-foundation/README.md)
