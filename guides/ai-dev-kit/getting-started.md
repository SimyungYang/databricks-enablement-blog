# Getting Started

AI Dev Kit Builder App을 로컬 환경에 설치하고 Databricks 워크스페이스에 연결하는 단계별 가이드입니다.

---

## 사전 요구 사항

{% hint style="warning" %}
다음 항목이 모두 준비되어야 합니다:
- **Databricks Workspace**(Premium 이상)
- **SQL Warehouse**(Serverless 권장)
- **Cluster**(범용 클러스터 1개 이상)
- **Python 3.11+**
- **Node.js 18+**
- **uv** 패키지 매니저 (`pip install uv`)
- **Anthropic API Key**(Claude 모델 사용)
{% endhint %}

---

## 1단계: 레포지토리 클론

AI Dev Kit 전체 레포지토리를 클론합니다. Builder App은 `databricks-builder-app` 디렉토리에 있습니다.

```bash
git clone https://github.com/databricks-solutions/ai-dev-kit.git
cd ai-dev-kit/databricks-builder-app
```

{% hint style="info" %}
**왜 전체 레포를 클론하나요?** Builder App은 `databricks-mcp-server`에 의존합니다. 전체 레포를 클론해야 MCP Server가 로컬에서 올바르게 참조됩니다. `pyproject.toml`의 `[project.optional-dependencies]`에서 `databricks-mcp-server`가 로컬 경로로 참조되는 것을 확인할 수 있습니다.
{% endhint %}

---

## 2단계: 자동 설치 (권장)

`setup.sh` 스크립트가 백엔드와 프론트엔드를 한 번에 설정합니다.

```bash
./scripts/setup.sh
```

이 스크립트는 다음을 수행합니다:
- Python 가상환경 생성 및 의존성 설치
- Node.js 의존성 설치
- `.env.local` 템플릿 생성
- Alembic DB 마이그레이션 실행

**왜 `uv`를 사용하나요?**`uv`는 Rust로 작성된 초고속 Python 패키지 매니저입니다. `pip`보다 10~100배 빠르며, 의존성 해결이 더 정확합니다. AI Dev Kit의 복잡한 의존성 트리(LangChain, Claude SDK, MCP Server 등)를 안정적으로 설치하기 위해 `uv`를 기본으로 사용합니다.

{% hint style="tip" %}
자동 설치가 실패하면 아래 수동 설치 절차를 따르세요.
{% endhint %}

---

## 2단계 (대안): 수동 설치

### Backend 설정

```bash
# Python 가상환경 생성
uv venv
source .venv/bin/activate

# 의존성 설치
uv pip install -e ".[dev]"
```

### Frontend 설정

```bash
cd client
npm install
cd ..
```

---

## 3단계: 환경 변수 구성

프로젝트 루트에 `.env.local` 파일을 생성합니다. 이 파일은 Builder App의 모든 외부 연결 정보를 관리합니다.

**왜 `.env.local`인가?** Builder App은 환경 변수를 세 단계로 로드합니다: `.env` (기본값) → `.env.local` (로컬 오버라이드) → 시스템 환경 변수. `.env.local`은 `.gitignore`에 포함되어 있어 **민감한 정보가 Git에 커밋되지 않습니다**.

```bash
# .env.local

# Anthropic API Key (필수)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Databricks 연결 정보 (필수)
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapixxxxxxxxxxxxxxxx

# Lakebase 데이터베이스 (택 1)
# 옵션 A: Autoscale Endpoint
LAKEBASE_ENDPOINT=your-lakebase-endpoint

# 옵션 B: Provisioned Instance
LAKEBASE_INSTANCE_NAME=your-instance-name

# 옵션 C: 직접 PostgreSQL URL
LAKEBASE_PG_URL=postgresql://user:pass@host:port/dbname
```

### 환경 변수 상세 설명

| 변수 | 필수 | 용도 | 발급 방법 |
|------|------|------|-----------|
| `ANTHROPIC_API_KEY` | 필수 (로컬) | Claude 모델 호출 | [Anthropic Console](https://console.anthropic.com/) → API Keys |
| `DATABRICKS_HOST` | 필수 | Workspace 연결 URL | Workspace URL 복사 (예: `https://adb-123.12.azuredatabricks.net`) |
| `DATABRICKS_TOKEN` | 필수 (로컬) | API 인증 | Workspace → User Settings → Developer → Access Tokens |
| `LAKEBASE_ENDPOINT` | 선택 | 대화 이력 영구 저장 | Workspace → Catalog → Lakebase → Endpoints |

{% hint style="warning" %}
**Databricks Apps로 배포할 때는**`ANTHROPIC_API_KEY`와 `DATABRICKS_TOKEN`을 직접 설정할 필요가 없습니다. Apps 환경에서는 Databricks Foundation Model API(FMAPI)를 사용하고, 사용자 인증은 `X-Forwarded-Access-Token` 헤더로 자동 전달됩니다.
{% endhint %}

### LLM 선택: Anthropic 직접 vs Databricks FMAPI

| 옵션 | 설정 | 장점 | 단점 |
|------|------|------|------|
| **Anthropic 직접** | `ANTHROPIC_API_KEY` 설정 | 최신 모델 즉시 사용, 안정적 | API 키 관리 필요, 별도 과금 |
| **Databricks FMAPI** | `LLM_PROVIDER=DATABRICKS` | API 키 불필요, 워크스페이스 과금 통합 | 사용 가능한 모델 한정 |
| **Azure OpenAI** | `LLM_PROVIDER=AZURE` | Azure 엔터프라이즈 환경 통합 | Azure 리소스 별도 구성 필요 |

---

## 4단계: 데이터베이스 마이그레이션

Lakebase를 사용하는 경우 Alembic 마이그레이션을 실행합니다.

```bash
alembic upgrade head
```

**Alembic 마이그레이션이란?** Alembic은 SQLAlchemy 기반의 데이터베이스 스키마 버전 관리 도구입니다. `upgrade head` 명령은 현재 DB 스키마를 최신 버전으로 업데이트합니다. Builder App의 DB 스키마가 변경될 때(새 테이블 추가, 컬럼 변경 등) 이 명령으로 안전하게 마이그레이션합니다.

### Lakebase 데이터 모델

Builder App은 다음 테이블들을 Lakebase에 저장합니다:

| 테이블 | 역할 | 주요 필드 |
|--------|------|-----------|
| **projects** | 프로젝트 메타데이터 | id, name, created_at, user_id |
| **conversations** | 대화 세션 | id, project_id, title, created_at |
| **messages** | 개별 메시지 | id, conversation_id, role, content |
| **executions** | 에이전트 실행 기록 | id, conversation_id, status, tool_calls |

{% hint style="warning" %}
Lakebase 없이도 Builder App을 실행할 수 있습니다. 이 경우 프로젝트 데이터는 로컬 파일 시스템(`projects/` 디렉토리)에만 저장됩니다. 프로덕션 환경에서는 Lakebase 사용을 강력히 권장합니다.
{% endhint %}

---

## 5단계: 개발 서버 실행

```bash
./scripts/start_dev.sh
```

또는 수동으로 백엔드와 프론트엔드를 각각 실행합니다:

```bash
# 터미널 1: Backend (FastAPI)
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload

# 터미널 2: Frontend (React)
cd client
npm run dev
```

**왜 두 개의 서버를 실행하나요?** 개발 환경에서는 프론트엔드(React)와 백엔드(FastAPI)를 분리하여 실행합니다. React의 Hot Module Replacement(HMR)로 프론트엔드 코드 변경이 즉시 반영되고, FastAPI의 `--reload` 옵션으로 백엔드 코드 변경도 자동 재시작됩니다. **프로덕션 배포 시에는** 프론트엔드를 빌드하여 정적 파일로 만든 후 FastAPI가 함께 서빙합니다.

### 개발 서버 아키텍처

```
개발 환경:
  브라우저 → React Dev Server (:3000) → API Proxy → FastAPI (:8000) → MCP Server

프로덕션 환경:
  브라우저 → FastAPI (:8000) → 정적 파일 서빙 (빌드된 React)
                             → API 엔드포인트
                             → MCP Server
```

실행 후 접속:
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs` (Swagger UI 자동 생성)

---

## 6단계: 첫 프로젝트 생성 및 테스트

1. 브라우저에서 `http://localhost:3000`에 접속합니다.
2. **New Project** 버튼을 클릭하여 새 프로젝트를 생성합니다.
3. 채팅 창에 다음과 같은 메시지를 입력합니다:

```
내 워크스페이스에 있는 카탈로그 목록을 보여줘
```

4. 에이전트가 `execute_sql` 도구를 호출하여 `SHOW CATALOGS` 결과를 반환합니다.

### 무엇이 일어나고 있는가?

사용자의 자연어 요청이 에이전트에게 전달되면, 다음과 같은 과정이 **자동으로** 수행됩니다:

```
1. [Claude Agent] "카탈로그 목록" 요청을 분석
2. [Claude Agent] 사용 가능한 MCP 도구 중 execute_sql을 선택
3. [MCP Server]  execute_sql 도구에 "SHOW CATALOGS" SQL 전달
4. [Databricks]  SQL Warehouse에서 쿼리 실행
5. [MCP Server]  결과를 에이전트에게 반환
6. [Claude Agent] 결과를 사용자 친화적 형태로 포매팅하여 응답
```

{% hint style="tip" %}
에이전트가 사용하는 도구 호출 과정이 실시간으로 스트리밍됩니다. 어떤 MCP 도구가 호출되었는지, 어떤 SQL이 실행되었는지 확인할 수 있습니다. 이 투명성은 에이전트의 행동을 검증하고 디버깅하는 데 필수적입니다.
{% endhint %}

### 추가 테스트 시나리오

첫 프로젝트가 성공적으로 동작하면, 다음 시나리오를 시도해보세요:

| 테스트 | 입력 예시 | 확인 사항 |
|--------|----------|-----------|
| **SQL 실행** | "main 카탈로그의 테이블 목록 보여줘" | `execute_sql` 도구 호출 확인 |
| **클러스터 상태** | "현재 실행 중인 클러스터 보여줘" | `list_clusters` 도구 호출 확인 |
| **파일 업로드** | "이 CSV 파일을 Volume에 업로드해줘" | `upload_to_volume` 도구 호출 확인 |
| **스킬 활용** | "합성 데이터로 매출 테이블 만들어줘" | `synthetic-data` 스킬 로드 + SQL 실행 |

---

## Databricks Apps로 배포 (프로덕션)

Builder App을 Databricks Apps에 배포하면 팀 전체가 사용할 수 있습니다.

### 프론트엔드 빌드

```bash
cd client
npm run build
cd ..
```

### app.yaml 구성

```yaml
command:
  - uvicorn
  - server.app:app
  - --host
  - 0.0.0.0
  - --port
  - "8000"

env:
  - name: ANTHROPIC_API_KEY
    valueFrom: secret
  - name: LAKEBASE_ENDPOINT
    value: your-lakebase-endpoint
```

### 배포

```bash
databricks apps deploy builder-app --source-code-path .
```

{% hint style="info" %}
Databricks Apps로 배포하면 `X-Forwarded-User`와 `X-Forwarded-Access-Token` 헤더를 통해 자동으로 사용자별 인증이 적용됩니다. 별도의 `DATABRICKS_TOKEN` 설정이 필요 없습니다.
{% endhint %}

---

## 문제 해결

| 증상 | 원인 | 해결 방법 |
|---|---|---|
| `ANTHROPIC_API_KEY not set` | 환경 변수 누락 | `.env.local` 파일에 키 추가 |
| SQL 실행 실패 | Warehouse 미실행 | Workspace에서 SQL Warehouse 시작 |
| MCP 도구 로드 실패 | `databricks-mcp-server` 미설치 | `uv pip install -e ".[dev]"` 재실행 |
| DB 마이그레이션 오류 | Lakebase 연결 실패 | `LAKEBASE_*` 환경 변수 확인 |
| 프론트엔드 빈 화면 | Node 의존성 누락 | `cd client && npm install` |

---

## 다음 단계

- [Tool 목록 및 상세](tools.md) - MCP 도구 전체 목록과 스킬 시스템
- [활용 사례](use-cases.md) - Builder App 실전 시나리오
- [Databricks Apps 배포 가이드](../apps/README.md) - Apps 배포 상세
