# 앱 생성하기

---

## 사전 준비

시작 전 아래 항목을 확인하세요.

| # | 항목 | 설명 |
|---|------|------|
| 1 | **워크스페이스 접근 권한** | Databricks 워크스페이스에 로그인 가능 |
| 2 | ** 앱 생성 권한** | `CAN MANAGE` 또는 워크스페이스 관리자 권한 |
| 3 | ** 리소스 권한** | 앱에서 사용할 SQL Warehouse, Serving Endpoint 등에 대한 접근 권한 |
| 4 | ** 로컬 개발 환경** | Python 3.10+ 또는 Node.js 18+ 설치 |
| 5 | **Databricks CLI** | `pip install databricks-cli` 또는 `brew install databricks` |

---

## 방법 1: UI에서 앱 생성

### Step 1: 앱 생성 시작

1. 워크스페이스 사이드바에서 **+ New** > **App** 클릭
2. 다음 중 하나를 선택합니다:
   - **템플릿 사용**: `Streamlit`, `Gradio Hello world`, `Flask`, `FastAPI` 등 사전 구성된 템플릿
   - ** 빈 앱 생성**: 처음부터 직접 코드 작성

### Step 2: 앱 정보 입력

| 필드 | 설명 | 예시 |
|------|------|------|
| **App name** | 앱의 고유 이름 (URL에 포함됨, 변경 불가) | `my-dashboard-app` |
| **Description** | 앱 설명 (선택사항) | "매출 분석 대시보드" |

{% hint style="warning" %}
** 앱 이름 규칙**: 소문자, 숫자, 하이픈만 사용 가능합니다. 앱 이름은 생성 후 변경할 수 없으며 URL에 직접 반영되므로 신중하게 지정하세요.
{% endhint %}

### Step 3: 리소스 연결 (선택)

앱에서 Databricks 리소스에 접근해야 한다면 이 단계에서 설정합니다.

| 리소스 유형 | 용도 | 설정 값 |
|------------|------|---------|
| **SQL Warehouse** | 데이터 조회 | Warehouse ID |
| **Serving Endpoint** | ML 모델 호출 | Endpoint 이름 |
| **Secret** | API 키, 비밀번호 | Secret scope/key |

리소스는 `app.yaml`의 `resources` 섹션에 정의되며, 앱 코드에서 `valueFrom`으로 참조합니다.

### Step 4: Install 클릭

**Install** 버튼을 클릭하면 Databricks가 다음을 자동으로 수행합니다:

1. 전용 **서비스 프린시펄** 생성
2. 컨테이너 환경 프로비저닝
3. 앱 코드 배포 및 실행
4. 공개 URL 생성

### Step 5: 배포 확인

배포 완료 후 **Overview** 페이지에서 다음을 확인합니다:

- **앱 URL**: `https://<app-name>-<workspace-id>.<region>.databricksapps.com`
- ** 실행 상태**: `Running`, `Deploying`, `Crashed` 등
- ** 로그**: 앱 실행 로그 (디버깅에 필수)
- ** 서비스 프린시펄**: 자동 생성된 SP 정보

---

## 방법 2: Databricks CLI로 앱 생성

UI 대신 CLI를 사용하면 스크립팅과 자동화가 가능합니다.

### 앱 생성

```bash
# 앱 생성 (빈 앱)
databricks apps create --name my-dashboard-app \
  --description "매출 분석 대시보드"
```

### 앱 배포

```bash
# 로컬 소스 코드를 앱에 배포
databricks apps deploy my-dashboard-app \
  --source-code-path /path/to/local/app
```

### 앱 상태 확인

```bash
# 앱 상태 조회
databricks apps get my-dashboard-app

# 앱 목록 조회
databricks apps list
```

---

## 소스 코드 다운로드 및 로컬 개발

Overview 페이지의 **Sync the files** 섹션에서 제공하는 커맨드를 복사하여 실행합니다.

```bash
mkdir my-dashboard-app && cd my-dashboard-app
# Overview 페이지에서 제공하는 sync 커맨드 실행
```

다운로드되는 파일:

| 파일 | 역할 |
|------|------|
| `app.py` | 앱 기능 및 UI 구현 |
| `app.yaml` | 앱 설정 (런타임, 환경 변수, 리소스) |
| `requirements.txt` | Python 패키지 의존성 |

### 로컬 실행 및 테스트

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

### 재배포

```bash
# 수정된 코드를 워크스페이스에 재배포
databricks apps deploy my-dashboard-app \
  --source-code-path /path/to/local/app
```

---

## 앱 생성 후 확인 체크리스트

| # | 확인 항목 | 방법 |
|---|----------|------|
| 1 | 앱 상태가 `Running`인지 | Overview 페이지에서 상태 확인 |
| 2 | 앱 URL에 접속 가능한지 | 브라우저에서 URL 직접 접속 |
| 3 | 서비스 프린시펄에 필요한 권한이 있는지 | UC 권한, SQL Warehouse 접근 권한 확인 |
| 4 | 리소스 연결이 정상인지 | 앱에서 데이터 조회/모델 호출 테스트 |
| 5 | 로그에 에러가 없는지 | Overview > Logs 탭 확인 |

---

## 일반적인 오류와 해결 방법

| 오류 | 원인 | 해결 방법 |
|------|------|-----------|
| **`CRASHED` 상태** | 앱 코드에 런타임 에러 | Logs 탭에서 에러 메시지 확인 후 코드 수정, 재배포 |
| **`Permission denied`** | 서비스 프린시펄 권한 부족 | 앱의 SP에 필요한 UC 테이블/Warehouse 접근 권한 부여 |
| ** 배포 실패 (파일 크기)** | 개별 파일이 10MB 초과 | 대용량 파일을 Volume에 업로드하고 런타임에 다운로드 |
| **`ModuleNotFoundError`** | `requirements.txt`에 패키지 누락 | 필요한 패키지를 `requirements.txt`에 추가 후 재배포 |
| ** 포트 충돌** | 앱이 올바른 포트에서 실행되지 않음 | `app.yaml`의 `command`에서 포트를 `$DATABRICKS_APP_PORT`로 설정 |
| ** 앱 URL 접속 불가** | 배포가 아직 진행 중 | 상태가 `Running`이 될 때까지 대기 (보통 2~5분) |

{% hint style="info" %}
** 디버깅 팁**: `databricks apps run-local --debug` 명령으로 로컬에서 먼저 테스트하면, 배포 후 발생하는 대부분의 오류를 사전에 잡을 수 있습니다.
{% endhint %}
