# 배포 워크플로우

---

## 전체 흐름

```
[로컬 개발] → [로컬 테스트] → [워크스페이스 배포] → [설정/리소스 연결] → [운영]
```

---

## 1. 로컬 개발 환경 설정

### 필수 도구 설치

```bash
# Databricks CLI 설치
pip install databricks-cli
# 또는
brew install databricks

# 인증 설정 (OAuth 기반 — 권장)
databricks auth login --host https://<workspace-url>

# 인증 확인
databricks current-user me
```

### 프로젝트 구조

선호하는 IDE(VS Code, PyCharm, IntelliJ 등)에서 개발합니다. Databricks VS Code Extension 사용을 권장합니다.

```bash
my-app/
├── app.py              # 앱 코드
├── app.yaml            # 앱 설정 (런타임, 리소스, 환경 변수)
├── requirements.txt    # Python 의존성
└── static/             # 정적 파일 (선택)
```

### app.yaml 예시

```yaml
command:
  - "streamlit"
  - "run"
  - "app.py"
  - "--server.port"
  - "$DATABRICKS_APP_PORT"

env:
  - name: "ENVIRONMENT"
    value: "production"

resources:
  - name: "sql-warehouse"
    sql_warehouse:
      id: "abc123def456"
      permission: "CAN_USE"
  - name: "serving-endpoint"
    serving_endpoint:
      name: "my-model-endpoint"
      permission: "CAN_QUERY"
```

---

## 2. 로컬 테스트

```bash
# Databricks CLI 로컬 실행 (권장 — Databricks 인증, 환경 변수 자동 처리)
databricks apps run-local --prepare-environment --debug
```

또는 프레임워크별로 직접 실행:

```bash
# Streamlit
streamlit run app.py

# Flask
gunicorn app:app -w 4

# FastAPI
uvicorn app:app --reload

# Gradio
python app.py
```

{% hint style="info" %}
**`run-local` vs 직접 실행**: `databricks apps run-local`은 `app.yaml`에 정의된 환경 변수와 리소스를 자동으로 주입합니다. 직접 실행 시에는 환경 변수를 수동으로 설정해야 합니다.
{% endhint %}

---

## 3. Databricks CLI deploy 명령어

### 기본 배포

```bash
# 로컬 소스 코드를 워크스페이스에 배포
databricks apps deploy <app-name> --source-code-path /path/to/local/app
```

### 배포 상태 확인

```bash
# 배포 상태 조회
databricks apps get <app-name>

# 배포 로그 확인 (디버깅 시)
databricks apps logs <app-name>
```

### 앱 중지/재시작

```bash
# 앱 중지
databricks apps stop <app-name>

# 앱 시작
databricks apps start <app-name>
```

---

## 4. 환경 간 이동 (dev → staging → prod)

리소스를 하드코딩하지 않고 `app.yaml`의 `valueFrom`을 사용하면, 코드 수정 없이 다른 워크스페이스로 앱을 이동할 수 있습니다.

### 전략: 환경별 app.yaml 분리

```bash
my-app/
├── app.py
├── app.yaml              # 기본 설정 (dev)
├── app.staging.yaml      # 스테이징 설정
├── app.prod.yaml         # 프로덕션 설정
└── requirements.txt
```

### 환경별 리소스 매핑 예시

| 리소스 | dev | staging | prod |
|--------|-----|---------|------|
| SQL Warehouse | `dev-warehouse-id` | `staging-warehouse-id` | `prod-warehouse-id` |
| Serving Endpoint | `model-dev` | `model-staging` | `model-prod` |
| Secret Scope | `dev-secrets` | `staging-secrets` | `prod-secrets` |

```bash
# 스테이징 배포
databricks apps deploy my-app-staging --source-code-path ./my-app

# 프로덕션 배포
databricks apps deploy my-app-prod --source-code-path ./my-app
```

---

## 5. CI/CD 파이프라인 구성 예시

### GitHub Actions 예시

```yaml
# .github/workflows/deploy-app.yml
name: Deploy Databricks App

on:
  push:
    branches: [main]
    paths: ['my-app/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Databricks CLI
        run: pip install databricks-cli

      - name: Configure Databricks Auth
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks configure --token <<EOF
          $DATABRICKS_HOST
          $DATABRICKS_TOKEN
          EOF

      - name: Deploy App
        run: |
          databricks apps deploy my-app \
            --source-code-path ./my-app
```

{% hint style="warning" %}
**보안 주의**: CI/CD에서 Databricks 인증 정보는 반드시 **GitHub Secrets** 또는 해당 CI 도구의 시크릿 관리 기능을 사용하세요. 코드에 토큰을 직접 넣지 마세요.
{% endhint %}

---

## 6. 롤백 방법

Databricks Apps는 이전 배포 버전으로 롤백하는 내장 기능이 제한적입니다. 다음 전략을 사용하세요.

### Git 기반 롤백 (권장)

```bash
# 이전 커밋으로 소스 코드 되돌리기
git checkout <previous-commit-hash> -- my-app/

# 이전 버전으로 재배포
databricks apps deploy my-app --source-code-path ./my-app
```

### 블루-그린 배포

1. 새 버전을 별도 앱으로 배포 (`my-app-v2`)
2. 테스트 후 문제 없으면 기존 앱 중지, 새 앱으로 트래픽 전환
3. 문제 발생 시 기존 앱 재시작

---

## 7. 의존성 관리

| 언어 | 파일 | 권장사항 |
|------|------|----------|
| Python (pip) | `requirements.txt` | 버전 명시: `streamlit==1.32.0` |
| Python (uv) | `pyproject.toml` | `[project.dependencies]` 섹션에 명시 |
| Node.js | `package.json` | `npm ci`로 lock 파일 기반 설치 |

### requirements.txt 모범 예시

```text
# 프레임워크
streamlit==1.32.0

# Databricks SDK
databricks-sdk==0.20.0

# 데이터 처리
pandas==2.2.0
plotly==5.18.0
```

{% hint style="warning" %}
**파일 크기 제한**: 앱 파일은 개별 10 MB를 초과할 수 없습니다. 초과 시 배포가 실패합니다. 대용량 파일(모델 가중치, 데이터 파일 등)은 Unity Catalog Volume에 저장하고 런타임에 다운로드하세요.
{% endhint %}

{% hint style="info" %}
**의존성 버전을 반드시 명시하세요.** 버전을 지정하지 않으면 배포할 때마다 최신 버전이 설치되어, 어제 작동하던 앱이 오늘 갑자기 깨질 수 있습니다.
{% endhint %}
