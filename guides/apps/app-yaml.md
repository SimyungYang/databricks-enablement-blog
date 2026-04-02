# app.yaml 설정

`app.yaml`은 앱의 런타임, 환경 변수, 리소스를 정의하는 핵심 설정 파일입니다.

---

## app.yaml이 하는 역할

`app.yaml`은 Databricks Apps에서 **앱의 실행 방법을 선언적으로 정의하는 설정 파일** 입니다. Kubernetes에 익숙하다면 `Deployment YAML`과 유사한 역할이라고 이해하면 됩니다. Databricks가 이 파일을 읽어서 "어떤 명령으로 앱을 시작할지", "어떤 환경변수를 주입할지", "어떤 Databricks 리소스에 접근할지"를 결정합니다.

코드가 "무엇을 하는가"를 정의한다면, `app.yaml`은 **"어떻게 실행되는가" **를 정의합니다. 잘 작성된 코드도 `app.yaml`이 잘못되면 배포가 실패하거나 앱이 비정상적으로 동작합니다. 반대로 `app.yaml`을 정확하게 구성하면 코드 수정 없이 다른 환경(dev/staging/prod)으로 앱을 이동할 수 있습니다.

{% hint style="info" %}
**핵심 원칙**: `app.yaml`에는 "무엇이 바뀔 수 있는가"를 넣고, 코드에는 "어떻게 동작하는가"를 넣습니다. Warehouse ID, Endpoint 이름, Secret 값 등은 환경에 따라 바뀌므로 `app.yaml`에서 관리하고, 코드에서는 `os.getenv()`로 참조합니다. 이 분리 원칙을 지키면 하나의 코드베이스로 여러 환경에 배포할 수 있습니다.
{% endhint %}

---

## 전체 구조

아래는 `app.yaml`의 전체 구조를 보여주는 예시입니다. 각 섹션의 역할을 주석으로 표시했습니다.

```yaml
# 실행 커맨드 (배열 형태)
command: ['streamlit', 'run', 'app.py']

# 환경 변수
env:
  - name: 'DATABRICKS_WAREHOUSE_ID'
    value: '<warehouse-id>'
  - name: 'LOG_LEVEL'
    value: 'info'
  - name: 'SECRET_KEY'
    valueFrom: my_secret           # 리소스 키 참조

# 리소스 (UI에서 설정 후 참조)
resources:
  - name: sql_warehouse
    type: sql-warehouse
  - name: my_secret
    type: secret
  - name: serving_endpoint
    type: serving-endpoint
```

이 YAML 파일은 세 가지 섹션으로 구성됩니다: `command`(앱을 어떻게 시작할지), `env`(실행 시 어떤 환경변수를 주입할지), `resources`(어떤 Databricks 리소스에 접근할지). 각 섹션은 독립적이며, 필요한 섹션만 사용해도 됩니다. 예를 들어 환경변수나 리소스가 필요 없는 간단한 앱이라면 `command`만 있어도 됩니다.

---

## command 필드

커스텀 실행 커맨드를 배열로 지정합니다. 셸 환경에서 실행되지 않으므로 파이프(`|`)나 리다이렉트(`>`)는 사용할 수 없습니다.

{% hint style="info" %}
**왜 배열 형태인가?**`command`가 문자열이 아닌 배열인 이유는 **셸 해석 없이 직접 실행** 되기 때문입니다. Docker의 `ENTRYPOINT`나 Kubernetes의 `command`와 동일한 방식입니다. 배열의 첫 번째 요소가 실행 파일이 되고, 나머지가 인수가 됩니다. 셸을 거치지 않으므로 환경변수 확장(`$VAR`)을 제외한 셸 기능(파이프, 리다이렉트, glob 등)은 사용할 수 없습니다. `$DATABRICKS_APP_PORT` 같은 환경변수만 예외적으로 치환됩니다.
{% endhint %}

### 프레임워크별 커맨드 예시

아래 각 프레임워크별로 올바른 `command` 설정과, **왜 그렇게 설정하는지** 를 설명합니다.

**Streamlit:**

```yaml
command: ['streamlit', 'run', 'app.py']
```

Streamlit은 자체적으로 포트를 관리합니다. 기본 포트(8501)가 Databricks Apps의 내부 포트와 자동으로 매핑되므로 별도로 포트를 지정하지 않아도 됩니다. 만약 포트를 명시적으로 지정하고 싶다면 `['streamlit', 'run', 'app.py', '--server.port', '${DATABRICKS_APP_PORT}']`를 사용하세요.

**Flask (Gunicorn):**

```yaml
command:
  - gunicorn
  - app:app
  - -w
  - '4'
```

Flask 단독으로는 개발 서버만 제공하므로, 프로덕션에서는 반드시 **Gunicorn**(WSGI 서버)을 사용합니다. `app:app`은 "app.py 파일의 app 객체"를 의미합니다. `-w 4`는 워커 프로세스 수인데, Medium 사이즈(2 vCPU) 기준으로 CPU 코어 수의 2배인 4가 적절합니다. Gunicorn은 기본적으로 `0.0.0.0:8000`에 바인딩하므로 별도 호스트/포트 설정이 필요 없는 경우가 많습니다.

**FastAPI (Uvicorn):**

```yaml
command:
  - uvicorn
  - app:app
  - --host
  - '0.0.0.0'
  - --port
  - '${DATABRICKS_APP_PORT}'
```

FastAPI는 **Uvicorn**(ASGI 서버)으로 실행합니다. 여기서 `--host 0.0.0.0`은 **모든 네트워크 인터페이스에서 접속을 허용** 한다는 의미입니다. 이것이 `127.0.0.1`(localhost)가 아닌 이유는, 컨테이너 내부에서 실행되는 앱이 외부(리버스 프록시)로부터 요청을 받아야 하기 때문입니다. `127.0.0.1`로 바인딩하면 컨테이너 외부에서 접근할 수 없어 앱이 시작되지만 URL 접속이 불가능합니다. `--port`에 `${DATABRICKS_APP_PORT}`를 사용하는 이유는, Databricks가 동적으로 할당한 포트에서 앱이 리슨해야 리버스 프록시가 트래픽을 전달할 수 있기 때문입니다.

**Gradio:**

```yaml
command: ['python', 'app.py']
```

Gradio는 `app.py` 내에서 `demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("DATABRICKS_APP_PORT", 7860)))`으로 서버 설정을 코드에서 직접 합니다. 따라서 `command`는 단순히 Python 스크립트를 실행하기만 하면 됩니다.

**Dash:**

```yaml
command: ['python', 'app.py']
```

Dash도 Gradio와 마찬가지로 코드 내에서 `app.run(host="0.0.0.0", port=int(os.environ.get("DATABRICKS_APP_PORT", 8050)))`으로 서버를 설정합니다.

{% hint style="info" %}
`DATABRICKS_APP_PORT` 환경 변수는 런타임에 실제 포트 번호로 자동 치환됩니다.
{% endhint %}

{% hint style="warning" %}
**command 관련 흔한 실수**:
1. **셸 문법 사용**: `command: 'streamlit run app.py && echo done'` — 파이프나 `&&`는 사용할 수 없습니다.
2. **문자열로 지정**: `command: 'uvicorn app:app'` — 반드시 배열 형태여야 합니다.
3. **포트 미지정**: FastAPI/Flask에서 포트를 지정하지 않으면 기본 포트와 Databricks 포트가 불일치하여 접속 불가.
4. **host 미설정**: `0.0.0.0` 대신 `127.0.0.1`로 바인딩하면 컨테이너 외부에서 접근 불가.
{% endhint %}

---

## env 필드

환경 변수를 정의합니다. 두 가지 방식이 있으며, **보안 수준에 따라 반드시 올바른 방식을 선택** 해야 합니다.

```yaml
env:
  # 방법 1: 직접 값 지정 (정적, 비민감 데이터만)
  - name: LOG_LEVEL
    value: 'debug'

  # 방법 2: 리소스 참조 (시크릿, 웨어하우스 ID 등)
  - name: WAREHOUSE_ID
    valueFrom: sql_warehouse

  - name: API_KEY
    valueFrom: my_api_secret
```

**`value`와 `valueFrom`의 차이가 중요합니다.**

| 방식 | 동작 | 보안 수준 | 사용 대상 |
|------|------|----------|----------|
| `value` | 값이 `app.yaml`에 평문으로 저장됨 | **낮음**— Git에 커밋되면 노출됨 | 기능 플래그, 로그 레벨, 타임존 등 비민감 설정 |
| `valueFrom` | 리소스 이름만 참조, 실제 값은 런타임에 Databricks가 주입 | **높음**— 코드나 설정 파일에 값이 노출되지 않음 | Warehouse ID, Endpoint 이름, API 키, 비밀번호 |

`valueFrom`을 사용하면 `app.yaml`에는 리소스의 **이름** 만 기록되고, 실제 값(Warehouse ID, Secret 값 등)은 Databricks가 앱 실행 시 자동으로 주입합니다. 이는 Kubernetes의 `secretKeyRef`와 동일한 패턴입니다.

{% hint style="warning" %}
시크릿이나 민감 정보는 절대 `value`에 직접 넣지 마세요. 반드시 `valueFrom`을 사용하여 리소스로 관리하세요.
{% endhint %}

{% hint style="info" %}
**실무 팁**: `value`에 넣어도 되는지 판단하는 기준은 간단합니다. "이 값이 GitHub 퍼블릭 리포지토리에 올라가도 문제없는가?"를 생각해 보세요. `LOG_LEVEL=debug`는 노출되어도 문제가 없지만, Warehouse ID는 워크스페이스 구조를 노출하므로 `valueFrom`을 사용하는 것이 바람직합니다.
{% endhint %}

---

## resources 필드

`resources` 섹션은 앱이 사용할 Databricks 리소스를 선언합니다. 여기서 선언한 리소스는 `env` 섹션에서 `valueFrom`으로 참조할 수 있습니다.

```yaml
resources:
  - name: sql_warehouse        # 코드에서 참조할 이름
    type: sql-warehouse        # 리소스 유형
  - name: my_secret
    type: secret
  - name: serving_endpoint
    type: serving-endpoint
```

각 리소스의 `name`은 `app.yaml` 내에서 고유해야 하며, `env` 섹션의 `valueFrom`에서 이 이름으로 참조합니다. `type`은 Databricks가 지원하는 리소스 유형을 지정합니다. 리소스의 실제 값(Warehouse ID, Endpoint 이름 등)은 UI의 Configure 화면에서 설정하거나, 배포 시 지정합니다.

{% hint style="info" %}
**resources와 env의 관계**: `resources`는 "이 앱이 어떤 리소스를 사용하는지" 선언하고, `env`의 `valueFrom`은 "그 리소스의 값을 어떤 환경변수로 주입할지" 지정합니다. 이 2단계 분리 덕분에 리소스 값이 바뀌어도 코드를 수정할 필요가 없습니다.
{% endhint %}

---

## 프레임워크별 완전한 app.yaml 예시

아래는 각 프레임워크별로 실제 프로덕션에서 사용할 수 있는 완전한 `app.yaml` 예시입니다. 각 설정의 이유를 함께 설명합니다.

### Streamlit (데이터 대시보드)

```yaml
command:
  - streamlit
  - run
  - app.py
  - --server.port
  - '${DATABRICKS_APP_PORT}'
  - --server.headless
  - 'true'
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
  - name: STREAMLIT_GATHER_USAGE_STATS
    value: 'false'
resources:
  - name: sql_warehouse
    type: sql-warehouse
```

`--server.headless true`는 Streamlit이 브라우저를 자동으로 열지 않도록 합니다 (서버 환경에서는 브라우저가 없으므로 필수). `STREAMLIT_GATHER_USAGE_STATS=false`는 Streamlit의 사용 통계 수집을 비활성화합니다.

### FastAPI (REST API)

```yaml
command:
  - uvicorn
  - app:app
  - --host
  - '0.0.0.0'
  - --port
  - '${DATABRICKS_APP_PORT}'
  - --workers
  - '2'
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
  - name: ENVIRONMENT
    value: 'production'
resources:
  - name: sql_warehouse
    type: sql-warehouse
```

`--workers 2`는 Medium 사이즈(2 vCPU) 기준으로 적절한 워커 수입니다. 워커 수를 CPU 코어 수보다 많이 설정하면 오히려 컨텍스트 스위칭 오버헤드로 성능이 저하됩니다.

### Gradio (AI 챗봇)

```yaml
command:
  - python
  - app.py
env:
  - name: SERVING_ENDPOINT
    valueFrom: serving_endpoint
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
resources:
  - name: serving_endpoint
    type: serving-endpoint
  - name: sql_warehouse
    type: sql-warehouse
```

Gradio 앱은 보통 Model Serving Endpoint를 호출하므로 `serving-endpoint` 리소스가 필요합니다. 대화 이력을 저장하려면 `sql-warehouse`도 함께 설정합니다.

### Dash (인터랙티브 대시보드)

```yaml
command:
  - python
  - app.py
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
  - name: DASH_DEBUG
    value: 'false'
resources:
  - name: sql_warehouse
    type: sql-warehouse
```

Dash의 `DASH_DEBUG=false`는 프로덕션에서 디버그 모드를 비활성화합니다. 디버그 모드가 켜져 있으면 에러 발생 시 스택 트레이스가 사용자에게 노출될 수 있어 보안상 위험합니다.

---

## 컴퓨트 사이즈

앱의 CPU 및 메모리를 선택할 수 있습니다. 아래 표는 각 사이즈의 사양과 비용, 적합한 사용 사례를 보여줍니다.

| 사이즈 | CPU | 메모리 | 비용 | 용도 |
|--------|-----|--------|------|------|
| **Medium**(기본값) | 최대 2 vCPU | 6 GB | 0.5 DBU/시간 | 대시보드, 간단한 시각화, 폼 |
| **Large** | 최대 4 vCPU | 12 GB | 1 DBU/시간 | 대용량 데이터 처리, 고동시성, 연산 집약적 작업 |

{% hint style="tip" %}
대부분의 앱은 Medium으로 충분합니다. 성능 이슈가 발생하거나 리소스 요구가 높은 경우에만 Large로 업그레이드하세요.
{% endhint %}

{% hint style="info" %}
**사이즈 선택 가이드**: Streamlit 대시보드나 Gradio 챗봇처럼 사용자 요청을 받아 SQL Warehouse나 Model Serving에 전달하는 "프록시" 역할의 앱은 자체적으로 연산을 거의 하지 않으므로 **Medium** 으로 충분합니다. 앱 내부에서 Pandas로 대용량 DataFrame을 처리하거나, 이미지/비디오 변환 등 CPU 집약적 작업을 수행하는 경우에만 **Large** 가 필요합니다. 확신이 없다면 Medium으로 시작하고, 앱 로그에서 OOM(Out of Memory) 에러가 발생하면 Large로 전환하세요.
{% endhint %}

---

## 흔한 실수 5가지와 해결 방법

`app.yaml` 작성 시 가장 빈번하게 발생하는 실수와 해결 방법을 정리합니다.

| # | 실수 | 증상 | 해결 방법 |
|---|------|------|-----------|
| 1 | **포트 불일치** | 앱이 `Running`이지만 URL 접속 시 502 에러 | `command`에서 `--port ${DATABRICKS_APP_PORT}` 사용. Streamlit은 `--server.port`, FastAPI는 `--port`, Flask/Gunicorn은 `-b 0.0.0.0:${DATABRICKS_APP_PORT}` |
| 2 | **command를 문자열로 지정** | 배포 실패 또는 앱 시작 실패 | `command: 'streamlit run app.py'`가 아닌 `command: ['streamlit', 'run', 'app.py']` 배열 형태 사용 |
| 3 | **리소스 이름 오타** | `valueFrom`에서 참조하는 이름이 `resources`에 없어 환경변수가 빈 값 | `resources`의 `name`과 `env`의 `valueFrom`이 정확히 일치하는지 확인 |
| 4 | **requirements.txt 누락** | `ModuleNotFoundError`로 앱 Crash | 로컬에서 `pip freeze`로 확인하고, 사용하는 모든 패키지를 `requirements.txt`에 포함 |
| 5 | **Python 버전 충돌** | 특정 패키지가 설치 실패 | Databricks Apps는 Python 3.10+를 사용합니다. Python 3.8 전용 패키지가 있다면 호환되는 버전을 명시 |

{% hint style="warning" %}
**가장 디버깅이 어려운 실수**: 리소스 이름 오타(#3)입니다. 이 경우 배포는 성공하고 앱도 `Running`이 되지만, 환경변수가 빈 값이 되어 런타임에 예상치 못한 오류가 발생합니다. `app.yaml`에서 `resources`의 `name`과 `env`의 `valueFrom` 값을 복사-붙여넣기로 동일하게 맞추는 것이 안전합니다.
{% endhint %}
