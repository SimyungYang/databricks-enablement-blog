# 앱 생성하기

---

## 왜 Databricks Apps인가?

앱을 배포하는 방법은 여러 가지가 있습니다. EC2에 직접 올리거나, ECS/Fargate를 사용하거나, Cloud Run에 배포할 수 있습니다. 하지만 이 모든 방법에는 공통적인 문제가 있습니다: **Databricks 데이터에 접근하기 위한 인증과 네트워크 설정을 직접 구성해야 한다는 것** 입니다.

예를 들어, EC2에서 Streamlit 앱을 운영하려면 다음을 모두 직접 해야 합니다:
- VPC 보안 그룹에서 Databricks 워크스페이스로의 아웃바운드 트래픽 허용
- PAT(Personal Access Token)를 AWS Secrets Manager에 저장하고 주기적으로 로테이션
- SSL 인증서 발급 및 ALB 구성
- 사용자 인증 시스템(Cognito, Auth0 등) 별도 구축

Databricks Apps는 이 모든 것을 **자동으로 처리** 합니다. 서비스 프린시펄이 자동 생성되고, HTTPS가 자동 적용되며, 워크스페이스 SSO가 그대로 사용됩니다. 데이터 엔지니어가 인프라 엔지니어 역할까지 맡지 않아도 됩니다.

---

## 사전 준비

시작 전 아래 항목을 확인하세요. 각 항목이 왜 필요한지 함께 설명합니다.

| # | 항목 | 설명 |
|---|------|------|
| 1 | **워크스페이스 접근 권한** | Databricks 워크스페이스에 로그인 가능 |
| 2 | **앱 생성 권한** | `CAN MANAGE` 또는 워크스페이스 관리자 권한 |
| 3 | **리소스 권한** | 앱에서 사용할 SQL Warehouse, Serving Endpoint 등에 대한 접근 권한 |
| 4 | **로컬 개발 환경** | Python 3.10+ 또는 Node.js 18+ 설치 |
| 5 | **Databricks CLI** | `pip install databricks-cli` 또는 `brew install databricks` |

{% hint style="info" %}
**사전 준비가 중요한 이유**: 앱 생성 자체는 수 분이면 되지만, 권한 부족으로 인한 디버깅에 수 시간을 소모하는 경우가 흔합니다. 특히 **리소스 권한**(항목 3)이 누락되면 앱은 정상 배포되지만 데이터 조회 시 `Permission denied` 오류가 발생합니다. 앱의 서비스 프린시펄에 대한 권한이 아니라 본인 계정의 권한만 확인하는 실수가 가장 빈번합니다.
{% endhint %}

---

## 방법 1: UI에서 앱 생성

### Step 1: 앱 생성 시작

1. 워크스페이스 사이드바에서 **+ New**> **App** 클릭
2. 다음 중 하나를 선택합니다:
   - **템플릿 사용**: `Streamlit`, `Gradio Hello world`, `Flask`, `FastAPI` 등 사전 구성된 템플릿
   - **빈 앱 생성**: 처음부터 직접 코드 작성

{% hint style="info" %}
**이 단계에서 실제로 무슨 일이 일어나는가**: "App" 버튼을 클릭하는 순간 Databricks는 내부적으로 **Kubernetes 네임스페이스를 예약** 합니다. 이 네임스페이스는 앱 전용의 격리된 실행 환경이 됩니다. 템플릿을 선택하면 사전 작성된 `app.py`, `app.yaml`, `requirements.txt`가 자동으로 해당 네임스페이스에 복사됩니다. 빈 앱을 선택하면 네임스페이스만 생성되고, 이후에 코드를 직접 업로드합니다.

**템플릿 선택 가이드**: 처음이라면 반드시 **템플릿** 으로 시작하세요. 템플릿은 `app.yaml`의 올바른 구조, `requirements.txt`의 필수 패키지, 프레임워크별 실행 명령을 모두 포함하고 있어 "무엇이 빠졌는지" 고민할 필요가 없습니다. 빈 앱은 이미 Databricks Apps에 익숙한 경우에만 사용하세요.
{% endhint %}

### Step 2: 앱 정보 입력

| 필드 | 설명 | 예시 |
|------|------|------|
| **App name** | 앱의 고유 이름 (URL에 포함됨, 변경 불가) | `my-dashboard-app` |
| **Description** | 앱 설명 (선택사항) | "매출 분석 대시보드" |

{% hint style="warning" %}
**앱 이름 규칙**: 소문자, 숫자, 하이픈만 사용 가능합니다. 앱 이름은 생성 후 변경할 수 없으며 URL에 직접 반영되므로 신중하게 지정하세요.
{% endhint %}

{% hint style="info" %}
**이 단계에서 실제로 무슨 일이 일어나는가**: 앱 이름은 단순한 라벨이 아닙니다. 이 이름이 곧 **앱의 URL 경로** 가 됩니다. 예를 들어 `my-dashboard-app`이라는 이름을 지정하면 URL은 `https://my-dashboard-app-<workspace-id>.<region>.databricksapps.com`이 됩니다.

**이름 짓기 베스트 프랙티스**:
- **팀명-기능명** 패턴을 사용하세요 (예: `data-team-sales-dashboard`)
- 환경을 이름에 포함하지 마세요 (예: `my-app-dev`보다는 환경별 별도 앱 생성)
- 이름은 변경 불가하므로, 임시 이름보다는 영구적으로 사용할 이름을 선택하세요
- URL에 표시되므로 외부에 노출되어도 문제없는 이름을 사용하세요
{% endhint %}

### Step 3: 리소스 연결 (선택)

앱에서 Databricks 리소스에 접근해야 한다면 이 단계에서 설정합니다.

| 리소스 유형 | 용도 | 설정 값 |
|------------|------|---------|
| **SQL Warehouse** | 데이터 조회 | Warehouse ID |
| **Serving Endpoint** | ML 모델 호출 | Endpoint 이름 |
| **Secret** | API 키, 비밀번호 | Secret scope/key |

리소스는 `app.yaml`의 `resources` 섹션에 정의되며, 앱 코드에서 `valueFrom`으로 참조합니다.

{% hint style="info" %}
**이 단계에서 실제로 무슨 일이 일어나는가**: 리소스를 연결하면 Databricks는 앱의 **서비스 프린시펄(SP)에 해당 리소스에 대한 접근 권한을 자동으로 부여** 합니다. 내부적으로는 `app.yaml`에 리소스 정의가 추가되고, 앱 실행 시 해당 리소스의 연결 정보가 환경변수로 자동 주입됩니다.

**왜 PAT 대신 서비스 프린시펄인가?**PAT(Personal Access Token)는 특정 사용자에게 귀속되므로, 해당 사용자가 퇴사하거나 비밀번호를 변경하면 토큰이 무효화됩니다. 또한 PAT는 해당 사용자의 모든 권한을 상속하므로 최소 권한 원칙을 위반할 수 있습니다. 서비스 프린시펄은 앱 전용 아이덴티티로서, 앱에 필요한 최소한의 권한만 부여할 수 있고, 사람의 라이프사이클과 무관하게 동작합니다.
{% endhint %}

{% hint style="warning" %}
**흔한 실수**: 리소스를 연결했지만 서비스 프린시펄에 실제 권한을 부여하지 않는 경우가 많습니다. 리소스 연결은 "이 앱이 이 리소스를 사용한다"는 선언일 뿐, 권한 부여는 별도로 해야 합니다. SQL Warehouse의 경우 Warehouse 설정에서 앱의 SP에 `CAN USE` 권한을, UC 테이블의 경우 SQL로 `GRANT SELECT ON TABLE ... TO <sp-id>`를 실행해야 합니다.
{% endhint %}

### Step 4: Install 클릭

**Install** 버튼을 클릭하면 Databricks가 다음을 자동으로 수행합니다:

1. 전용 **서비스 프린시펄** 생성
2. 컨테이너 환경 프로비저닝
3. 앱 코드 배포 및 실행
4. 공개 URL 생성

{% hint style="info" %}
**이 단계에서 실제로 무슨 일이 일어나는가**: Install 버튼 뒤에서 일어나는 과정을 단계별로 설명합니다.

1. **서비스 프린시펄 생성**: 앱 전용 OAuth 클라이언트가 생성됩니다. `DATABRICKS_CLIENT_ID`와 `DATABRICKS_CLIENT_SECRET`가 이 SP의 자격 증명입니다.
2. **컨테이너 빌드**: `requirements.txt`에 명시된 패키지가 설치되고, Python/Node.js 런타임이 구성됩니다. 이 과정이 배포 시간의 대부분을 차지합니다.
3. **앱 실행**: `app.yaml`의 `command`에 지정된 명령이 컨테이너 내에서 실행됩니다.
4. **헬스체크**: Databricks가 앱이 지정된 포트에서 HTTP 요청에 응답하는지 확인합니다. 응답이 오면 `Running` 상태로 전환됩니다.
5. **URL 라우팅**: 앱의 고유 URL이 리버스 프록시에 등록되고, HTTPS가 자동으로 적용됩니다.

이 전체 과정은 보통 **2~5분** 이 소요됩니다. `requirements.txt`에 `torch`나 `tensorflow` 같은 대용량 패키지가 있으면 10분 이상 걸릴 수도 있습니다.
{% endhint %}

### Step 5: 배포 확인

배포 완료 후 **Overview** 페이지에서 다음을 확인합니다:

- **앱 URL**: `https://<app-name>-<workspace-id>.<region>.databricksapps.com`
- **실행 상태**: `Running`, `Deploying`, `Crashed` 등
- **로그**: 앱 실행 로그 (디버깅에 필수)
- **서비스 프린시펄**: 자동 생성된 SP 정보

{% hint style="info" %}
**각 상태의 의미와 대처법**:

- **Running**: 앱이 정상적으로 실행 중이며 URL로 접속 가능합니다. 이 상태에서도 로그를 주기적으로 확인하여 런타임 오류가 발생하고 있지 않은지 모니터링하세요.
- **Deploying**: 컨테이너 빌드 또는 패키지 설치가 진행 중입니다. 보통 2~5분 내에 완료됩니다. 10분 이상 이 상태가 지속되면 `requirements.txt`에 설치에 오래 걸리는 패키지가 있거나, 네트워크 문제가 있을 수 있습니다.
- **Crashed**: 앱 코드에 오류가 있어 프로세스가 비정상 종료된 상태입니다. **반드시 Logs 탭에서 에러 메시지를 확인** 하세요. 가장 흔한 원인은 `ModuleNotFoundError`(패키지 누락), `PermissionError`(SP 권한 부족), `ConnectionError`(Warehouse/Endpoint 접속 실패)입니다.
- **Stopped**: 사용자가 수동으로 앱을 중지한 상태입니다. 과금이 발생하지 않으며, 다시 시작하려면 Start 버튼을 클릭하세요.
{% endhint %}

---

## 방법 2: Databricks CLI로 앱 생성

UI 대신 CLI를 사용하면 스크립팅과 자동화가 가능합니다. **프로덕션 환경에서는 UI보다 CLI가 권장** 됩니다. CLI를 사용하면 배포 과정을 코드화(Infrastructure as Code)할 수 있고, CI/CD 파이프라인에 통합하여 일관된 배포를 보장할 수 있기 때문입니다.

### 앱 생성

아래 명령은 빈 앱을 생성합니다. 이 시점에서 서비스 프린시펄이 생성되고 Kubernetes 네임스페이스가 예약됩니다. 아직 코드가 배포되지 않았으므로 앱은 실행되지 않습니다.

```bash
# 앱 생성 (빈 앱)
databricks apps create --name my-dashboard-app \
  --description "매출 분석 대시보드"
```

이 명령은 내부적으로 Databricks REST API의 `POST /api/2.0/apps` 엔드포인트를 호출합니다. 성공하면 앱의 메타데이터(이름, URL, 서비스 프린시펄 정보 등)가 JSON 형태로 반환됩니다.

### 앱 배포

아래 명령은 로컬 디렉토리의 소스 코드를 앱에 업로드하고 배포합니다. `--source-code-path`는 `app.py`, `app.yaml`, `requirements.txt` 등이 포함된 디렉토리 경로입니다.

```bash
# 로컬 소스 코드를 앱에 배포
databricks apps deploy my-dashboard-app \
  --source-code-path /path/to/local/app
```

이 명령이 실행되면 디렉토리의 모든 파일이 패키징되어 Databricks에 업로드됩니다. 이후 컨테이너 빌드, 패키지 설치, 앱 실행이 자동으로 진행됩니다. 파일이 10MB를 초과하면 배포가 실패합니다.

### 앱 상태 확인

```bash
# 앱 상태 조회
databricks apps get my-dashboard-app

# 앱 목록 조회
databricks apps list
```

`get` 명령은 앱의 현재 상태, URL, 서비스 프린시펄 ID, 마지막 배포 시간 등 상세 정보를 반환합니다. `list` 명령은 워크스페이스의 모든 앱 목록을 보여줍니다.

{% hint style="info" %}
**CLI 활용 팁**: `databricks apps get` 출력을 `jq`와 조합하면 특정 필드만 추출할 수 있습니다. 예를 들어 `databricks apps get my-app --output json | jq '.status'`로 상태만 확인하거나, `jq '.url'`로 URL만 추출할 수 있습니다. CI/CD 파이프라인에서 배포 후 상태를 검증할 때 유용합니다.
{% endhint %}

---

## 소스 코드 다운로드 및 로컬 개발

Overview 페이지의 **Sync the files** 섹션에서 제공하는 커맨드를 복사하여 실행합니다.

```bash
mkdir my-dashboard-app && cd my-dashboard-app
# Overview 페이지에서 제공하는 sync 커맨드 실행
```

다운로드되는 파일 구성과 각 파일의 역할은 다음과 같습니다.

| 파일 | 역할 |
|------|------|
| `app.py` | 앱 기능 및 UI 구현 |
| `app.yaml` | 앱 설정 (런타임, 환경 변수, 리소스) |
| `requirements.txt` | Python 패키지 의존성 |

이 세 파일은 Databricks Apps의 **최소 배포 단위** 입니다. `app.py`가 실제 로직, `app.yaml`이 실행 환경 설정, `requirements.txt`가 의존성 목록입니다. 이 구조를 이해하면 어떤 프레임워크를 사용하든 동일한 패턴으로 앱을 구성할 수 있습니다.

### 로컬 실행 및 테스트

로컬에서 앱을 테스트하는 것은 **배포 전 반드시 거쳐야 할 단계** 입니다. 배포 후 오류를 발견하면 디버깅에 수 분~수십 분이 소요되지만, 로컬에서는 즉시 확인할 수 있습니다.

```bash
# 의존성 설치
pip install -r requirements.txt

# Databricks CLI로 로컬 실행 (권장 — Databricks 인증 자동 처리)
databricks apps run-local --prepare-environment --debug

# 또는 프레임워크별 직접 실행
streamlit run app.py          # Streamlit
uvicorn app:app --reload      # FastAPI
python app.py                 # Gradio / Flask
```

위 명령에서 `--prepare-environment`는 `app.yaml`에 정의된 환경변수와 리소스 참조를 자동으로 설정합니다. `--debug`는 상세한 디버그 로그를 출력하여 문제 발생 시 원인 파악을 도와줍니다. 프레임워크별 직접 실행은 빠른 반복 개발에 유용하지만, `DATABRICKS_WAREHOUSE_ID` 등의 환경변수를 수동으로 설정해야 합니다.

### 재배포

```bash
# 수정된 코드를 워크스페이스에 재배포
databricks apps deploy my-dashboard-app \
  --source-code-path /path/to/local/app
```

재배포 시에는 **전체 파일이 다시 업로드** 됩니다. 변경된 파일만 업로드하는 증분 배포는 지원되지 않습니다. 하지만 의존성이 동일하면 패키지 설치 캐시가 활용되어 배포 시간이 단축됩니다.

---

## 앱 생성 후 확인 체크리스트

앱을 배포한 직후 아래 항목을 순서대로 확인하세요. 이 체크리스트를 따르면 운영 중 발생할 수 있는 대부분의 문제를 사전에 발견할 수 있습니다.

| # | 확인 항목 | 방법 |
|---|----------|------|
| 1 | 앱 상태가 `Running`인지 | Overview 페이지에서 상태 확인 |
| 2 | 앱 URL에 접속 가능한지 | 브라우저에서 URL 직접 접속 |
| 3 | 서비스 프린시펄에 필요한 권한이 있는지 | UC 권한, SQL Warehouse 접근 권한 확인 |
| 4 | 리소스 연결이 정상인지 | 앱에서 데이터 조회/모델 호출 테스트 |
| 5 | 로그에 에러가 없는지 | Overview > Logs 탭 확인 |

{% hint style="warning" %}
**체크 순서가 중요합니다**: 항목 1-2가 정상이더라도 항목 3-4에서 실패하는 경우가 매우 흔합니다. 앱 자체는 실행되지만 데이터에 접근하지 못하는 것입니다. 반드시 **실제 데이터 조회나 모델 호출까지 테스트** 하세요.
{% endhint %}

---

## 일반적인 오류와 해결 방법

아래 표는 Databricks Apps에서 가장 자주 발생하는 오류와 해결 방법을 정리합니다. 오류가 발생하면 **항상 Logs 탭을 먼저 확인** 하세요. 대부분의 오류 원인이 로그에 명확하게 기록됩니다.

| 오류 | 원인 | 해결 방법 |
|------|------|-----------|
| **`CRASHED` 상태** | 앱 코드에 런타임 에러 | Logs 탭에서 에러 메시지 확인 후 코드 수정, 재배포 |
| **`Permission denied`** | 서비스 프린시펄 권한 부족 | 앱의 SP에 필요한 UC 테이블/Warehouse 접근 권한 부여 |
| **배포 실패 (파일 크기)** | 개별 파일이 10MB 초과 | 대용량 파일을 Volume에 업로드하고 런타임에 다운로드 |
| **`ModuleNotFoundError`** | `requirements.txt`에 패키지 누락 | 필요한 패키지를 `requirements.txt`에 추가 후 재배포 |
| **포트 충돌** | 앱이 올바른 포트에서 실행되지 않음 | `app.yaml`의 `command`에서 포트를 `$DATABRICKS_APP_PORT`로 설정 |
| **앱 URL 접속 불가** | 배포가 아직 진행 중 | 상태가 `Running`이 될 때까지 대기 (보통 2~5분) |
| **`ConnectionError` / Timeout** | SQL Warehouse가 중지되어 있거나 네트워크 문제 | Warehouse가 Running 상태인지 확인, Serverless Warehouse 사용 권장 |
| **`ImportError: cannot import name`** | 패키지 버전 충돌 | `requirements.txt`에서 호환되는 버전 명시 (예: `streamlit==1.32.0`) |
| **배포는 성공했지만 빈 화면** | 앱이 잘못된 호스트/포트에 바인딩 | `host=0.0.0.0`, `port=$DATABRICKS_APP_PORT`로 설정 확인 |

{% hint style="info" %}
**디버깅 팁**: `databricks apps run-local --debug` 명령으로 로컬에서 먼저 테스트하면, 배포 후 발생하는 대부분의 오류를 사전에 잡을 수 있습니다.
{% endhint %}

{% hint style="warning" %}
**가장 빈번한 실수 TOP 3**:
1. **SP 권한 미부여**: 앱이 `Running`이지만 데이터 접근 시 `Permission denied`. 앱의 서비스 프린시펄에 `GRANT SELECT`와 Warehouse `CAN USE` 권한을 부여했는지 확인하세요.
2. **포트 미설정**: FastAPI/Flask에서 `host=0.0.0.0`과 `port=$DATABRICKS_APP_PORT`를 지정하지 않으면 앱이 시작되지만 외부에서 접속할 수 없습니다.
3. **requirements.txt 불일치**: 로컬에서는 잘 되지만 배포 후 에러가 나는 경우, 로컬에 설치된 패키지가 `requirements.txt`에 누락되었을 가능성이 높습니다. `pip freeze > requirements.txt`로 현재 환경을 캡처하세요 (단, 불필요한 패키지는 제거).
{% endhint %}
