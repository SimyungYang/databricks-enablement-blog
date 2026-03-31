# Builder App 배포 가이드

이 가이드는 AI Dev Kit Builder App을 Databricks Workspace에 배포하는 전체 절차를 다룹니다.

## 사전 요구사항

| 항목 | 필수 여부 | 설명 |
|------|---------|------|
| **Databricks Workspace** | 필수 | Premium 이상, Apps 기능 활성화 |
| **Databricks CLI** | 필수 | v0.278.0 이상 (`databricks --version`) |
| **Node.js** | 필수 | v18+ (프론트엔드 빌드용) |
| **Git** | 필수 | 소스코드 clone |
| **Lakebase** | 선택 | 대화 기록 영구 저장 (없으면 메모리 저장) |

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
| **Databricks FMAPI** (기본) | `LLM_PROVIDER=DATABRICKS` | 별도 API 키 불필요, 워크스페이스 과금 |
| **Anthropic 직접** | `ANTHROPIC_API_KEY=sk-ant-...` | Claude API 키 필요, 별도 과금 |
| **Azure OpenAI** | `LLM_PROVIDER=AZURE` | Azure 리소스 필요 |

## Step 5: 배포

```bash
bash scripts/deploy.sh <app-name>
```

이 스크립트가 자동으로 수행하는 작업:
1. Databricks CLI 버전 확인
2. 프론트엔드 빌드 (React → 정적 파일)
3. 35개 스킬 다운로드 및 설치
4. Workspace에 소스코드 업로드
5. 앱 배포 및 시작

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

## 참고

- [AI Dev Kit GitHub](https://github.com/databricks-solutions/ai-dev-kit)
- [Databricks Apps 문서](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/index.html)
- [Lakebase Autoscale 문서](https://docs.databricks.com/aws/en/database/lakebase/autoscale/index.html)
