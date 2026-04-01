# Builder App 배포 가이드

이 가이드는 AI Dev Kit Builder App을 Databricks Workspace에 배포하는 전체 절차를 다룹니다.

## 배포 아키텍처 이해

Builder App을 Databricks Apps에 배포하면, 다음과 같은 아키텍처로 운영됩니다:

```
사용자 브라우저
     │
     ▼
Databricks Apps (서버리스 컨테이너)
  ├─ FastAPI + 빌드된 React (정적 파일)
  ├─ Claude Agent SDK + MCP Server (내장)
  └─ Lakebase 연결 (대화 이력 영구 저장)
     │
     ▼
Databricks Workspace APIs
  ├─ SQL Warehouse
  ├─ Clusters
  ├─ Unity Catalog
  └─ ... (30+ 서비스)
```

### 로컬 개발 vs Databricks Apps 배포 비교

| 항목 | 로컬 개발 | Databricks Apps |
|------|----------|-----------------|
| ** 인증**| `DATABRICKS_TOKEN` 직접 설정 | `X-Forwarded-Access-Token` 자동 전달 |
| **LLM**| Anthropic API Key 필요 | Databricks FMAPI 사용 가능 (키 불필요) |
| ** 접근 범위**| 개인만 사용 | 팀 전체 접근 가능 |
| ** 영속성**| 로컬 파일 시스템 | Lakebase 영구 저장 |
| ** 스케일링**| 단일 프로세스 | Databricks Apps 자동 관리 |
| **URL**| `localhost:3000` | `<app-name>-<workspace-id>.aws.databricksapps.com` |

### CI/CD 통합

프로덕션 환경에서는 배포를 자동화하는 것이 좋습니다. GitHub Actions를 활용한 CI/CD 파이프라인 예시:

```yaml
# .github/workflows/deploy.yml
name: Deploy Builder App
on:
  push:
    branches: [main]
    paths: ['databricks-builder-app/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: databricks/setup-cli@main
      - name: Build Frontend
        run: cd databricks-builder-app/client && npm install && npm run build
      - name: Deploy to Databricks Apps
        run: cd databricks-builder-app && bash scripts/deploy.sh ${{ vars.APP_NAME }}
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
```

{% hint style="tip" %}
CI/CD 파이프라인을 사용하면 코드 변경 시 자동으로 테스트 → 빌드 → 배포가 수행됩니다. `main` 브랜치에 머지하면 프로덕션 환경에 자동 배포되는 GitOps 패턴을 구현할 수 있습니다.
{% endhint %}

## 사전 요구사항

| 항목 | 필수 여부 | 설명 |
|------|---------|------|
| **Databricks Workspace**| 필수 | Premium 이상, Apps 기능 활성화 |
| **Databricks CLI**| 필수 | v0.278.0 이상 (`databricks --version`) |
| **Node.js**| 필수 | v18+ (프론트엔드 빌드용) |
| **Git**| 필수 | 소스코드 clone |
| **Lakebase**| 선택 | 대화 기록 영구 저장 (없으면 메모리 저장) |

## Step 1: 소스코드 준비

```bash
git clone https://github.com/databricks-solutions/ai-dev-kit.git
cd ai-dev-kit/databricks-builder-app
```

## Step 2: Databricks CLI 인증

```bash
databricks auth login --host https://<workspace-url>.cloud.databricks.com
```

브라우저에서 SSO 인증을 완료합니다.

## Step 3: 앱 생성

```bash
databricks apps create <app-name>
```

{% hint style="info" %}
앱 이름은 소문자, 숫자, 하이픈만 사용 가능합니다. 예: `my-builder-app`
{% endhint %}

## Step 4: app.yaml 설정

`app.yaml.example`을 복사하여 `app.yaml`로 만듭니다:

```bash
cp app.yaml.example app.yaml
```

### Option A: Lakebase 없이 배포 (간단)

대화 기록이 메모리에만 저장됩니다. 앱 재시작 시 기록이 사라지지만, 빠르게 시작할 수 있습니다.

```yaml
command:
  - "uvicorn"
  - "server.app:app"
  - "--host"
  - "0.0.0.0"
  - "--port"
  - "$DATABRICKS_APP_PORT"

env:
  - name: ENV
    value: "production"
  - name: PROJECTS_BASE_DIR
    value: "./projects"
  - name: PYTHONPATH
    value: "/app/python/source_code/packages"
  - name: ENABLED_SKILLS
    value: ""
  - name: SKILLS_ONLY_MODE
    value: "false"

  # LLM - Databricks Foundation Models
  - name: LLM_PROVIDER
    value: "DATABRICKS"
  - name: DATABRICKS_MODEL
    value: "databricks-claude-sonnet-4-6"
  - name: DATABRICKS_MODEL_MINI
    value: "databricks-gpt-5-4-mini"

  - name: CLAUDE_CODE_STREAM_CLOSE_TIMEOUT
    value: "3600000"
  - name: MLFLOW_TRACKING_URI
    value: "databricks"
  - name: AUTO_GRANT_PERMISSIONS_TO
    value: "account users"
```

### Option B: Lakebase Autoscale로 배포 (권장)

대화 기록이 PostgreSQL에 영구 저장됩니다. Scale-to-zero로 비용 효율적입니다.

1. **Lakebase 프로젝트 생성**: Workspace → Catalog → Lakebase → Create project
2. **Endpoint 이름 확인**: Lakebase → 프로젝트 → Branches → Endpoints

```yaml
env:
  # ... 위 공통 설정 동일 ...

  # Lakebase Autoscale
  - name: LAKEBASE_ENDPOINT
    value: "projects/<project-name>/branches/production/endpoints/<endpoint>"
  - name: LAKEBASE_DATABASE_NAME
    value: "databricks_postgres"
```

{% hint style="warning" %}
Lakebase Autoscale는 Databricks App의 리소스로 추가할 필요 없이 OAuth로 자동 연결됩니다.
{% endhint %}

### Option C: Lakebase Provisioned로 배포

고정 용량 인스턴스를 사용합니다. 리소스로 명시적 추가가 필요합니다.

```bash
databricks apps add-resource <app-name> \
  --resource-type database \
  --resource-name lakebase \
  --database-instance <instance-name>
```

```yaml
env:
  # ... 공통 설정 ...

  # Lakebase Provisioned
  - name: LAKEBASE_INSTANCE_NAME
    value: "<instance-name>"
  - name: LAKEBASE_DATABASE_NAME
    value: "databricks_postgres"
```

### LLM 모델 선택

| 옵션 | 설정 | 특징 |
|------|------|------|
| **Databricks FMAPI**(기본) | `LLM_PROVIDER=DATABRICKS` | 별도 API 키 불필요, 워크스페이스 과금 |
| **Anthropic 직접**| `ANTHROPIC_API_KEY=sk-ant-...` | Claude API 키 필요, 별도 과금 |
| **Azure OpenAI**| `LLM_PROVIDER=AZURE` | Azure 리소스 필요 |

## Step 5: 배포

```bash
bash scripts/deploy.sh <app-name>
```

이 스크립트가 자동으로 수행하는 작업:
1. **Databricks CLI 버전 확인**— v0.278.0 이상이 필요합니다. 이전 버전에는 Apps 관련 버그가 있을 수 있습니다.
2. ** 프론트엔드 빌드**— React 소스를 Webpack으로 번들링하여 `client/dist/` 디렉토리에 정적 파일로 생성합니다.
3. **35개 스킬 다운로드**— `databricks-skills` 레포에서 최신 스킬 파일을 다운로드합니다.
4. **Workspace에 소스코드 업로드**— Databricks Workspace Files에 소스코드를 동기화합니다.
5. ** 앱 배포 및 시작**— Databricks Apps가 컨테이너를 생성하고, `uvicorn`으로 FastAPI 서버를 시작합니다.

{% hint style="info" %}
프론트엔드가 이미 빌드되어 있으면 `--skip-build` 옵션으로 빌드를 건너뛸 수 있습니다:
```bash
bash scripts/deploy.sh <app-name> --skip-build
```
{% endhint %}

## Step 6: 확인

배포 완료 후:

```bash
databricks apps list | grep <app-name>
```

상태가 `ACTIVE` + `SUCCEEDED`이면 성공입니다.

앱 URL: `https://<app-name>-<workspace-id>.aws.databricksapps.com`

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| Apps 쿼타 초과 (300개) | 워크스페이스 앱 수 한도 | STOPPED 앱 삭제 또는 다른 워크스페이스 사용 |
| 배포 실패 (FAILED) | app.yaml 오류 또는 의존성 문제 | `databricks apps get <app-name>` 로 에러 메시지 확인 |
| LLM 응답 없음 | 모델 엔드포인트 비활성 | `databricks serving-endpoints list`로 모델 상태 확인 |
| Lakebase 연결 실패 | Endpoint 이름 오류 또는 권한 | Lakebase 프로젝트에서 Endpoint 이름 재확인 |
| 빌드 시 npm 오류 | Node.js 버전 불일치 | `node --version`으로 v18+ 확인, `nvm use 18` |
| 앱 시작 후 502 에러 | 앱 초기화 중 | 2~3분 후 재시도, 로그에서 에러 확인 |
| MCP 도구 로드 실패 | 스킬 파일 누락 | `deploy.sh`가 스킬 다운로드를 포함하는지 확인 |

### 상세 디버깅

배포 문제가 발생하면 다음 명령으로 상세 로그를 확인합니다:

```bash
# 앱 상태 확인
databricks apps get <app-name>

# 앱 로그 확인 (최근 100줄)
databricks apps get-logs <app-name> --num-lines 100

# 앱 재배포 (설정 변경 후)
databricks apps deploy <app-name> --source-code-path .
```

## 배포 후 운영 가이드

### 업데이트 배포

코드나 설정을 변경한 후 재배포하려면:

```bash
# 프론트엔드 변경 시: 빌드 후 배포
cd client && npm run build && cd ..
bash scripts/deploy.sh <app-name>

# 백엔드만 변경 시: 빌드 건너뛰기
bash scripts/deploy.sh <app-name> --skip-build
```

### 앱 관리 명령

| 명령 | 설명 |
|------|------|
| `databricks apps list` | 전체 앱 목록 조회 |
| `databricks apps get <name>` | 앱 상태 상세 조회 |
| `databricks apps stop <name>` | 앱 중지 (비용 절약) |
| `databricks apps start <name>` | 중지된 앱 재시작 |
| `databricks apps delete <name>` | 앱 완전 삭제 |

{% hint style="tip" %}
사용하지 않는 앱은 `stop`으로 중지하여 비용을 절약할 수 있습니다. 중지된 앱은 URL에 접근할 수 없지만, 설정과 데이터는 유지됩니다. `start`로 언제든 재시작할 수 있습니다.
{% endhint %}

## 참고

- [AI Dev Kit GitHub](https://github.com/databricks-solutions/ai-dev-kit)
- [Databricks Apps 문서](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/index.html)
- [Lakebase Autoscale 문서](https://docs.databricks.com/aws/en/database/lakebase/autoscale/index.html)
- [Databricks CLI 문서](https://docs.databricks.com/dev-tools/cli/index.html)
