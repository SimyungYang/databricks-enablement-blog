# 배포 워크플로우

---

## 배포 아키텍처: 코드에서 실행까지

Databricks Apps의 배포 과정을 이해하면 배포 실패 시 문제를 빠르게 진단할 수 있습니다. 배포는 크게 **5단계** 로 진행됩니다.

| 단계 | 동작 | 소요 시간 | 실패 시 증상 |
|------|------|----------|-------------|
| 1. ** 소스 업로드**| 로컬 파일이 Databricks 컨트롤 플레인으로 전송 | 수 초 | "파일 크기 초과" 에러 (개별 10MB 제한) |
| 2. ** 의존성 설치**| `requirements.txt` 기반 패키지 설치 | 1~5분 | `ModuleNotFoundError`, 빌드 타임아웃 |
| 3. ** 컨테이너 시작**| `app.yaml`의 `command`로 앱 프로세스 시작 | 수 초 | `command` 오류, 포트 바인딩 실패 |
| 4. ** 헬스체크**| 지정된 포트에서 HTTP 응답 확인 | 30초~2분 | 앱이 포트에 바인딩하지 않음, Crash |
| 5. **URL 라우팅**| 리버스 프록시에 앱 URL 등록 | 수 초 | 내부 라우팅 오류 (드물게 발생) |

{% hint style="info" %}
** 배포 시간의 핵심**: 전체 배포 시간의 대부분은 **2단계(의존성 설치)** 에서 소요됩니다. `torch`, `tensorflow` 같은 대용량 패키지가 있으면 10분 이상 걸릴 수 있습니다. 이미 설치된 패키지가 동일하면 캐시가 활용되어 재배포 시간이 크게 단축됩니다. `requirements.txt`에서 버전을 고정하면 캐시 적중률이 높아져 배포 속도가 빨라집니다.
{% endhint %}

### 배포 전략: Databricks Apps는 어떻게 배포하는가?

Databricks Apps는 ** 롤링 업데이트(Rolling Update)** 방식을 사용합니다. 새 버전의 컨테이너가 시작되어 헬스체크를 통과하면, 이전 버전의 컨테이너가 종료됩니다.

| 배포 전략 | Databricks Apps 지원 | 설명 |
|-----------|---------------------|------|
| ** 롤링 업데이트**| 기본 동작 | 새 버전이 준비되면 이전 버전 교체. 짧은 전환 시간 발생 |
| ** 블루-그린 배포**| 수동 구현 가능 | 별도 앱(v2)을 만들어 테스트 후 전환. 롤백이 빠름 |
| ** 카나리 배포**| 지원하지 않음 | 일부 트래픽만 새 버전으로 보내는 것은 불가 |

{% hint style="warning" %}
** 배포 중 다운타임**: 롤링 업데이트 중에 짧은 시간(수 초~수십 초) 동안 앱 접속이 불안정할 수 있습니다. 프로덕션 앱에서 무중단 배포가 필요하면, 별도 앱으로 블루-그린 배포를 수동으로 구성하는 것을 권장합니다.
{% endhint %}

---

## 전체 흐름

```
[로컬 개발] → [로컬 테스트] → [워크스페이스 배포] → [설정/리소스 연결] → [운영]
```

이 흐름의 각 단계는 독립적인 목적을 가지고 있습니다. ** 로컬 개발** 에서는 빠른 반복으로 코드를 작성하고, ** 로컬 테스트** 에서는 Databricks 인증과 리소스 접근이 정상적인지 검증하며, ** 워크스페이스 배포** 에서는 실제 환경에 앱을 올리고, ** 운영** 에서는 모니터링과 유지보수를 수행합니다.

---

## 1. 로컬 개발 환경 설정

### 필수 도구 설치

```bash
# Databricks CLI 설치
pip install databricks-cli
# 또는
brew install databricks
```

이 명령은 Databricks CLI를 설치합니다. CLI는 앱 생성, 배포, 상태 확인, 로그 조회 등 모든 배포 작업을 커맨드라인에서 수행할 수 있게 합니다.

```bash
# 인증 설정 (OAuth 기반 — 권장)
databricks auth login --host https://<workspace-url>
```

이 명령은 브라우저 기반 OAuth 인증을 시작합니다. PAT(Personal Access Token)보다 OAuth가 권장되는 이유는 토큰 자동 갱신이 지원되고, 토큰이 파일에 평문으로 저장되지 않기 때문입니다.

```bash
# 인증 확인
databricks current-user me
```

이 명령으로 인증이 정상적으로 설정되었는지 확인합니다. 현재 로그인한 사용자 정보가 반환되면 인증이 올바르게 구성된 것입니다.

### 프로젝트 구조

선호하는 IDE(VS Code, PyCharm, IntelliJ 등)에서 개발합니다. Databricks VS Code Extension 사용을 권장합니다.

```bash
my-app/
├── app.py              # 앱 코드
├── app.yaml            # 앱 설정 (런타임, 리소스, 환경 변수)
├── requirements.txt    # Python 의존성
└── static/             # 정적 파일 (선택)
```

이 4개 파일이 Databricks App의 전체입니다. `app.py`가 비즈니스 로직, `app.yaml`이 실행 환경, `requirements.txt`가 의존성, `static/`이 정적 에셋입니다.

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

이 예시는 Streamlit 앱의 전형적인 설정입니다. `command`로 Streamlit을 시작하고, `env`로 환경 정보를 주입하며, `resources`로 SQL Warehouse와 Serving Endpoint에 대한 접근을 선언합니다.

---

## 2. 로컬 테스트

로컬 테스트는 ** 배포 전 반드시 거쳐야 할 단계** 입니다. 배포 후 오류를 발견하면 코드 수정 후 재배포 후 대기(2~5분)의 사이클을 반복해야 하지만, 로컬에서는 즉시 확인할 수 있습니다.

```bash
# Databricks CLI 로컬 실행 (권장 — Databricks 인증, 환경 변수 자동 처리)
databricks apps run-local --prepare-environment --debug
```

`--prepare-environment`는 `app.yaml`에 정의된 모든 환경변수와 리소스 참조를 로컬 환경에 자동으로 설정합니다. `--debug`는 상세 로그를 출력하여 인증 문제나 리소스 접근 오류를 즉시 확인할 수 있게 합니다.

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

직접 실행할 때는 `DATABRICKS_WAREHOUSE_ID`, `DATABRICKS_HOST` 등의 환경변수를 수동으로 설정해야 합니다.

{% hint style="info" %}
**`run-local` vs 직접 실행**: `databricks apps run-local`은 `app.yaml`에 정의된 환경 변수와 리소스를 자동으로 주입합니다. 직접 실행 시에는 환경 변수를 수동으로 설정해야 합니다.
{% endhint %}

{% hint style="warning" %}
** 로컬 테스트의 한계**: 로컬에서는 Databricks의 리버스 프록시, SSL 종료, 포트 매핑 등이 없으므로, 네트워크 관련 문제는 로컬에서 재현되지 않을 수 있습니다. 코드 로직, 데이터 접근, 인증 문제는 로컬에서 검증하고, 네트워크 관련 문제는 배포 후 확인하세요.
{% endhint %}

---

## 3. Databricks CLI deploy 명령어

### 기본 배포

```bash
# 로컬 소스 코드를 워크스페이스에 배포
databricks apps deploy <app-name> --source-code-path /path/to/local/app
```

이 명령은 지정된 디렉토리의 모든 파일을 패키징하여 Databricks에 업로드하고, 컨테이너 빌드와 앱 실행을 트리거합니다. 10MB를 초과하는 개별 파일이 있으면 배포가 실패합니다.

### 배포 상태 확인

```bash
# 배포 상태 조회
databricks apps get <app-name>

# 배포 로그 확인 (디버깅 시)
databricks apps logs <app-name>
```

`get` 명령은 앱의 현재 상태, URL, 서비스 프린시펄 정보, 마지막 배포 시간을 반환합니다. `logs` 명령은 Python의 `print()` 출력, 프레임워크의 로그 메시지, 에러 트레이스백을 보여줍니다.

### 앱 중지/재시작

```bash
# 앱 중지
databricks apps stop <app-name>

# 앱 시작
databricks apps start <app-name>
```

앱을 중지하면 과금이 중지됩니다. 인메모리 상태는 초기화되므로 영속적 데이터는 미리 저장해야 합니다.

---

## 4. 환경 간 이동 (dev → staging → prod)

리소스를 하드코딩하지 않고 `app.yaml`의 `valueFrom`을 사용하면, 코드 수정 없이 다른 워크스페이스로 앱을 이동할 수 있습니다. 이것이 ** 리소스 추상화의 핵심 가치** 입니다.

### 전략: 환경별 app.yaml 분리

```bash
my-app/
├── app.py
├── app.yaml              # 기본 설정 (dev)
├── app.staging.yaml      # 스테이징 설정
├── app.prod.yaml         # 프로덕션 설정
└── requirements.txt
```

이 구조에서 `app.py`는 환경에 따라 변경되지 않습니다. 환경변수를 통해 Warehouse ID, Endpoint 이름 등이 주입되므로, 코드 수정 없이 설정 파일만 교체하면 다른 환경에 배포할 수 있습니다.

### 환경별 리소스 매핑 예시

아래 표는 동일한 앱이 환경에 따라 다른 리소스를 사용하는 예를 보여줍니다.

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

{% hint style="info" %}
** 환경 분리 전략**: 가장 간단한 방법은 환경별로 별도 앱을 생성하는 것입니다 (`my-app-dev`, `my-app-staging`, `my-app-prod`). 각 앱에서 UI Configure 화면에서 해당 환경의 리소스를 연결하면 됩니다.
{% endhint %}

---

## 5. CI/CD 파이프라인 구성 예시

프로덕션 앱은 수동 배포 대신 **CI/CD 파이프라인을 통한 자동 배포** 가 권장됩니다. 자동 배포는 인적 오류를 줄이고, 배포 이력을 추적 가능하게 하며, 일관된 배포 프로세스를 보장합니다.

### GitHub Actions 예시

아래 워크플로우는 `main` 브랜치에 `my-app/` 디렉토리의 변경이 푸시되면 자동으로 앱을 배포합니다.

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

이 워크플로우에서 핵심 포인트는 다음과 같습니다:
- `paths: ['my-app/**']`로 앱 코드가 변경될 때만 배포가 트리거됩니다.
- `DATABRICKS_HOST`와 `DATABRICKS_TOKEN`은 **GitHub Secrets** 에 저장됩니다. 절대 코드에 직접 넣지 마세요.
- 배포 후 상태 확인 단계를 추가하면 더 안전합니다.

### Azure DevOps 예시

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - my-app/**

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.10'

  - script: pip install databricks-cli
    displayName: 'Install Databricks CLI'

  - script: |
      export DATABRICKS_HOST=$(DATABRICKS_HOST)
      export DATABRICKS_TOKEN=$(DATABRICKS_TOKEN)
      databricks apps deploy my-app --source-code-path ./my-app
    displayName: 'Deploy App'
    env:
      DATABRICKS_HOST: $(DATABRICKS_HOST)
      DATABRICKS_TOKEN: $(DATABRICKS_TOKEN)
```

Azure DevOps에서도 패턴은 동일합니다. `DATABRICKS_HOST`와 `DATABRICKS_TOKEN`을 Pipeline Variables(Secret)로 설정하세요.

{% hint style="warning" %}
** 보안 주의**: CI/CD에서 Databricks 인증 정보는 반드시 **GitHub Secrets** 또는 해당 CI 도구의 시크릿 관리 기능을 사용하세요. 코드에 토큰을 직접 넣지 마세요.
{% endhint %}

{% hint style="info" %}
**CI/CD 고급 패턴**: 프로덕션 배포 파이프라인에서는 다음 단계를 추가하는 것이 좋습니다:
1. ** 린트/테스트**: 코드 품질 검사 및 단위 테스트 실행
2. ** 스테이징 배포**: 프로덕션 전 스테이징 환경에 먼저 배포
3. ** 스모크 테스트**: 스테이징에서 기본 기능 동작 확인
4. ** 승인 게이트**: 수동 승인 후 프로덕션 배포
5. ** 프로덕션 배포**: 메인 앱 배포
6. ** 상태 검증**: 배포 후 앱 상태가 `Running`인지 확인
{% endhint %}

---

## 6. 모니터링과 로깅

배포 후 앱의 상태를 지속적으로 모니터링하는 것은 안정적인 운영의 핵심입니다.

### 앱 로그 확인

```bash
# CLI로 로그 확인
databricks apps logs <app-name>
```

앱 로그에는 Python의 `print()` 출력, 프레임워크의 액세스 로그, 에러 트레이스백이 포함됩니다. UI에서는 Overview > Logs 탭에서도 확인할 수 있습니다.

### 오류 디버깅 패턴

| 증상 | 확인할 곳 | 일반적인 원인 |
|------|----------|-------------|
| 앱 Crashed | Logs 탭에서 에러 트레이스백 확인 | `ImportError`, `SyntaxError`, OOM |
| 502 Bad Gateway | `app.yaml`의 `command` 포트 설정 확인 | 앱이 `DATABRICKS_APP_PORT`에 바인딩하지 않음 |
| Permission denied | Logs 탭에서 권한 에러 메시지 확인 | SP에 UC 테이블/Warehouse 권한 미부여 |
| 느린 응답 | 앱 코드의 쿼리 성능 확인 | 무거운 쿼리, Warehouse 콜드 스타트 |
| 간헐적 타임아웃 | Warehouse 상태 확인 | Classic Warehouse 자동 중지 후 재시작 지연 |

{% hint style="info" %}
** 효과적인 로깅 패턴**: 앱 코드에서 Python의 `logging` 모듈을 사용하면 로그 레벨을 제어할 수 있습니다. `print()`보다 `logging.info()`, `logging.error()`를 사용하고, 로그 레벨을 `app.yaml`의 `env`로 제어하세요 (`LOG_LEVEL=INFO`). 이렇게 하면 프로덕션에서는 중요 로그만, 디버깅 시에는 상세 로그를 볼 수 있습니다.
{% endhint %}

---

## 7. 스케일링

Databricks Apps는 현재 ** 수평적 자동 스케일링을 지원하지 않습니다**. 하나의 앱은 하나의 컨테이너(Medium 또는 Large)에서 실행됩니다.

| 스케일링 방식 | 지원 여부 | 대안 |
|--------------|----------|------|
| ** 수직 스케일링**(더 큰 컨테이너) | Medium에서 Large로 변경 가능 | 사이즈 변경 후 재배포 |
| ** 수평 스케일링**(컨테이너 복제) | 지원하지 않음 | 앱 내부에서 다중 워커 사용 (Gunicorn `-w`) |
| ** 트래픽 기반 자동 스케일링**| 지원하지 않음 | SQL Warehouse의 Serverless 스케일링 활용 |

{% hint style="info" %}
** 스케일링 팁**: 앱 자체의 스케일링보다 ** 백엔드 리소스의 스케일링** 에 집중하세요. Databricks Apps는 주로 프록시 역할(사용자 요청을 SQL Warehouse나 Model Serving에 전달)을 하므로, 병목은 대부분 백엔드에서 발생합니다. Serverless SQL Warehouse와 Model Serving Endpoint는 자동으로 스케일링되므로, 앱 컨테이너 자체가 병목이 되는 경우는 드뭅니다.
{% endhint %}

---

## 8. 비용 구조

Databricks Apps의 비용을 정확히 이해하면 예상치 못한 청구를 방지할 수 있습니다.

| 과금 항목 | 과금 조건 | DBU 단가 |
|-----------|----------|----------|
| ** 앱 컨테이너**| `Running` 또는 `Deploying` 상태일 때 | Medium: 0.5/hr, Large: 1.0/hr |
| **SQL Warehouse**| 쿼리 실행 시 | Serverless Warehouse 단가 적용 |
| **Model Serving**| 추론 요청 시 | Endpoint 설정에 따름 |

{% hint style="warning" %}
** 비용 주의사항**: 앱 컨테이너는 `Running` 상태에서 ** 트래픽이 없어도 과금** 됩니다. 이는 앱이 항상 대기 상태로 유지되기 때문입니다. 개발/테스트 앱은 사용하지 않을 때 반드시 `Stop`하세요.
{% endhint %}

{% hint style="info" %}
** 비용 최적화 체크리스트**:
1. 개발/테스트 앱은 퇴근 시 `Stop` (CLI 스크립트 또는 cron 활용)
2. Medium 사이즈로 시작, 필요할 때만 Large 업그레이드
3. SQL Warehouse는 Serverless 사용 (유휴 시 비과금)
4. 불필요한 앱은 삭제 (SP도 함께 정리됨)
{% endhint %}

---

## 9. 롤백 방법

Databricks Apps는 이전 배포 버전으로 롤백하는 내장 기능이 제한적입니다. 다음 전략을 사용하세요.

### Git 기반 롤백 (권장)

Git으로 소스 코드를 관리하면 ** 어떤 시점으로든 즉시 롤백** 할 수 있습니다. 이것이 앱 코드를 반드시 Git으로 관리해야 하는 가장 큰 이유입니다.

```bash
# 이전 커밋으로 소스 코드 되돌리기
git checkout <previous-commit-hash> -- my-app/

# 이전 버전으로 재배포
databricks apps deploy my-app --source-code-path ./my-app
```

첫 번째 명령은 Git의 이전 커밋에서 앱 디렉토리를 복원합니다. 두 번째 명령으로 해당 버전을 재배포합니다. 전체 롤백 소요 시간은 배포 시간(2~5분)과 동일합니다.

### 블루-그린 배포

블루-그린 배포는 ** 무중단 롤백** 이 필요할 때 사용합니다.

1. 새 버전을 별도 앱으로 배포 (`my-app-v2`)
2. 테스트 후 문제 없으면 기존 앱 중지, 새 앱으로 트래픽 전환
3. 문제 발생 시 기존 앱 재시작

{% hint style="info" %}
** 블루-그린의 한계**: 앱 URL이 이름에 포함되므로(`my-app-v1.xxx.databricksapps.com` vs `my-app-v2.xxx.databricksapps.com`), 사용자에게 URL 변경을 안내해야 합니다. 현재 Databricks Apps에서는 커스텀 도메인을 직접 지원하지 않습니다.
{% endhint %}

---

## 10. 의존성 관리

의존성 관리는 "어제 되던 앱이 오늘 안 되는" 문제를 방지하는 핵심입니다.

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

각 패키지에 버전을 명시하는 이유는 ** 재현 가능한 빌드를 보장** 하기 위해서입니다. 버전을 지정하지 않으면 배포할 때마다 최신 버전이 설치되어, 호환성 문제로 앱이 깨질 수 있습니다.

{% hint style="warning" %}
** 파일 크기 제한**: 앱 파일은 개별 10 MB를 초과할 수 없습니다. 초과 시 배포가 실패합니다. 대용량 파일(모델 가중치, 데이터 파일 등)은 Unity Catalog Volume에 저장하고 런타임에 다운로드하세요.
{% endhint %}

{% hint style="info" %}
** 의존성 버전을 반드시 명시하세요.** 버전을 지정하지 않으면 배포할 때마다 최신 버전이 설치되어, 어제 작동하던 앱이 오늘 갑자기 깨질 수 있습니다.
{% endhint %}

{% hint style="warning" %}
** 의존성 충돌 디버깅**: `ModuleNotFoundError`나 `ImportError`가 발생하면, 로컬에서 `pip install -r requirements.txt`를 깨끗한 가상환경에서 실행하여 재현하세요. 로컬에서는 작동하지만 배포 후 실패하는 경우, 로컬에 이미 설치된 패키지가 `requirements.txt`에 누락되었을 가능성이 높습니다.
{% endhint %}
