# 인증 (Authentication & Authorization)

Databricks Apps는 OAuth 2.0 기반으로 두 가지 인증 모델을 제공합니다.

---

## Databricks Apps 인증이 특별한 이유

일반적인 웹 앱을 배포할 때 인증(Authentication)은 가장 복잡하고 실수하기 쉬운 영역입니다. 전통적인 웹 앱에서는 다음을 직접 구현해야 합니다:

- ** 사용자 인증 시스템**: 로그인/로그아웃, 세션 관리, 비밀번호 해싱, OAuth 플로우
- **API 인증**: Databricks에 접근하기 위한 PAT 관리, 토큰 로테이션, Secret Manager 연동
- ** 권한 관리**: 사용자별 접근 제어, 역할 기반 권한(RBAC) 구현

Databricks Apps는 이 모든 것을 ** 플랫폼 레벨에서 자동으로 처리** 합니다. 앱에 접근하는 사용자는 Databricks 워크스페이스 로그인을 통해 자동으로 인증되고, 앱 자체는 서비스 프린시펄을 통해 Databricks 리소스에 접근합니다. 개발자는 인증 코드를 한 줄도 작성하지 않아도 됩니다.

{% hint style="info" %}
** 핵심 개념**: Databricks Apps의 인증은 두 가지 레이어로 구성됩니다. 첫째, ** 사용자가 앱에 접근하는 인증**(워크스페이스 SSO가 자동 처리). 둘째, ** 앱이 Databricks 리소스에 접근하는 인증**(서비스 프린시펄 또는 사용자 토큰). 이 두 레이어를 구분하지 못하면 인증 설계에서 혼란이 발생합니다.
{% endhint %}

---

## 1. 앱 인증 (App Authorization)

앱의 ** 서비스 프린시펄** 아이덴티티로 Databricks 리소스에 접근합니다.

### 서비스 프린시펄(SP) 심층 이해

서비스 프린시펄은 앱의 ** 기계 아이덴티티** 입니다. 사람이 아닌 프로그램이 Databricks에 접근할 때 사용하는 전용 계정이라고 이해하면 됩니다.

**SP의 생명주기를 단계별로 살펴보면:**

| 단계 | 시점 | 무슨 일이 일어나는가 |
|------|------|-------------------|
| ** 생성**| 앱 생성 시 | Databricks가 앱 전용 SP를 자동 생성. `DATABRICKS_CLIENT_ID`와 `DATABRICKS_CLIENT_SECRET` 발급 |
| ** 인증 주입**| 앱 실행 시 | 위 두 자격 증명이 환경변수로 컨테이너에 자동 주입됨 |
| ** 권한 부여**| 앱 설정 시 (관리자가 수동) | SP에 필요한 UC 테이블, Warehouse, Endpoint 접근 권한 부여 |
| **API 호출**| 앱 런타임 | SP가 OAuth 토큰을 발급받아 Databricks API에 접근 |
| ** 삭제**| 앱 삭제 시 | SP와 모든 관련 토큰이 자동 삭제됨 |

**SP를 통한 API 호출 흐름:**

| 순서 | 주체 | 동작 | 설명 |
|------|------|------|------|
| 1 | 앱 코드 | `Config()` 초기화 | `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`, `DATABRICKS_HOST` 환경변수를 읽음 |
| 2 | Databricks SDK | OAuth 토큰 요청 | SP 자격 증명으로 Databricks OAuth 서버에 토큰 요청 |
| 3 | OAuth 서버 | 토큰 발급 | 단기 유효 액세스 토큰 발급 (자동 갱신) |
| 4 | Databricks SDK | API 호출 | 발급받은 토큰으로 SQL Warehouse, UC, Serving Endpoint 등에 접근 |
| 5 | Databricks | 권한 확인 | SP에 부여된 권한 범위 내에서만 접근 허용 |

이 전체 흐름이 `Config()` 한 줄로 자동 처리됩니다. 개발자가 토큰 발급이나 갱신을 직접 구현할 필요가 없습니다.

### 특징

- 앱 생성 시 자동으로 서비스 프린시펄이 생성됨
- `DATABRICKS_CLIENT_ID`와 `DATABRICKS_CLIENT_SECRET`가 자동 주입됨
- 모든 사용자가 동일한 권한으로 접근 (사용자별 접근 제어 불가)
- 배포 간에 아이덴티티가 유지됨

{% hint style="warning" %}
**"모든 사용자가 동일한 권한"의 의미**: 앱 인증을 사용하면 앱에 접속하는 모든 사용자가 SP의 권한으로 데이터에 접근합니다. 즉, SP에 `sales` 테이블에 대한 `SELECT` 권한이 있다면 모든 앱 사용자가 해당 테이블의 모든 행을 볼 수 있습니다. Unity Catalog의 Row-Level Security나 Column Masking을 사용자별로 적용하려면 ** 사용자 인증** 을 사용해야 합니다.
{% endhint %}

### 사용 시나리오

- 백그라운드 작업 실행
- 공유 설정/메타데이터 관리
- 로깅 및 사용 메트릭
- 외부 서비스 호출

### 코드 예시 (Python)

아래 코드는 서비스 프린시펄 인증으로 SQL Warehouse에 쿼리를 실행하는 가장 기본적인 패턴입니다. `Config()` 한 줄이 전체 인증 과정을 처리합니다.

```python
from databricks import sql
from databricks.sdk.core import Config

# 서비스 프린시펄 인증 자동 사용
cfg = Config()

conn = sql.connect(
    server_hostname=cfg.host,
    http_path="/sql/1.0/warehouses/<warehouse-id>",
    credentials_provider=lambda: cfg.authenticate,
)

query = "SELECT * FROM catalog.schema.my_table LIMIT 1000"
with conn.cursor() as cursor:
    cursor.execute(query)
    df = cursor.fetchall_arrow().to_pandas()
```

`Config()`는 환경변수에서 `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`를 자동으로 읽습니다. 이 세 환경변수는 Databricks Apps가 컨테이너 시작 시 자동으로 주입하므로 개발자가 별도로 설정할 필요가 없습니다. `credentials_provider=lambda: cfg.authenticate`는 SDK가 OAuth 토큰을 자동으로 발급/갱신하도록 위임합니다.

### 코드 예시 (JavaScript)

```javascript
import { DBSQLClient } from '@databricks/sql';

const client = new DBSQLClient();
const connection = await client.connect({
    authType: 'databricks-oauth',
    host: process.env.DATABRICKS_SERVER_HOSTNAME,
    path: process.env.DATABRICKS_HTTP_PATH,
    oauthClientId: process.env.DATABRICKS_CLIENT_ID,
    oauthClientSecret: process.env.DATABRICKS_CLIENT_SECRET,
});

const query = 'SELECT * FROM catalog.schema.my_table LIMIT 1000';
const cursor = await connection.cursor(query);
const rows = [];
for await (const row of cursor) {
    rows.push(row);
}
```

JavaScript SDK에서는 Python과 달리 환경변수를 명시적으로 전달해야 합니다. `authType: 'databricks-oauth'`를 지정하면 SDK가 OAuth 2.0 Client Credentials 플로우를 사용하여 토큰을 발급받습니다.

---

## 2. 사용자 인증 (User Authorization)

현재 로그인한 ** 사용자의 아이덴티티와 권한** 으로 리소스에 접근합니다.

{% hint style="info" %}
** 상태**: Public Preview. 워크스페이스 관리자가 기능을 활성화해야 합니다.
{% endhint %}

### 사용자 인증이 필요한 이유

앱 인증(서비스 프린시펄)은 편리하지만 한계가 있습니다. ** 모든 사용자가 동일한 권한으로 데이터에 접근** 하기 때문입니다.

예를 들어, HR 대시보드를 만든다고 가정합니다. 팀장은 자기 팀 전체 급여를 볼 수 있어야 하고, 일반 직원은 자기 급여만 볼 수 있어야 합니다. SP 인증을 사용하면 SP에 부여된 권한이 모든 사용자에게 동일하게 적용되므로 이런 구분이 불가능합니다.

사용자 인증을 사용하면 **Unity Catalog의 Row-Level Security와 Column Masking이 현재 로그인한 사용자에게 자동으로 적용** 됩니다. 팀장 A가 앱을 사용하면 A의 UC 권한으로 쿼리가 실행되고, 직원 B가 사용하면 B의 권한으로 실행됩니다.

### 특징

- 사용자별 접근 제어 가능 (Unity Catalog 정책 자동 적용)
- Row-level 필터, Column 마스킹이 자동으로 적용됨
- 스코프(scope) 기반으로 접근 범위 제한
- HTTP 헤더 `x-forwarded-access-token`으로 사용자 토큰 전달

{% hint style="info" %}
** 동작 원리**: 사용자가 앱 URL에 접속하면, Databricks는 워크스페이스 SSO를 통해 사용자를 인증합니다. 인증이 완료되면 해당 사용자의 ** 단기 유효 액세스 토큰** 이 HTTP 요청의 `x-forwarded-access-token` 헤더에 자동으로 포함되어 앱에 전달됩니다. 앱은 이 토큰을 사용하여 Databricks API를 호출하면, 해당 사용자의 권한으로 실행됩니다.
{% endhint %}

### 주요 스코프

스코프는 앱이 사용자 대신 접근할 수 있는 ** 권한의 범위를 제한** 합니다. 최소 권한 원칙에 따라 앱에 필요한 스코프만 요청해야 합니다.

| 스코프 | 설명 |
|--------|------|
| `sql` | SQL 웨어하우스 쿼리 |
| `dashboards.genie` | Genie 스페이스 관리 |
| `files.files` | 파일/디렉토리 관리 |
| `iam.access-control:read` | 접근 제어 읽기 (기본) |
| `iam.current-user:read` | 현재 사용자 정보 읽기 (기본) |

### 사용 시나리오

- 사용자별 데이터 접근이 필요한 경우
- Unity Catalog 정책(RLS, Column Masking) 적용이 필요한 경우
- 사용자별 권한에 따른 차등 기능 제공

### 프레임워크별 사용자 토큰 가져오기

각 프레임워크마다 HTTP 헤더에 접근하는 방법이 다릅니다. 아래 코드에서 핵심은 모두 동일합니다: `x-forwarded-access-token` 헤더에서 사용자의 액세스 토큰을 추출하는 것입니다.

**Streamlit:**

```python
import streamlit as st

user_access_token = st.context.headers.get('x-forwarded-access-token')
```

Streamlit은 `st.context.headers`를 통해 HTTP 헤더에 접근합니다. 이 방법은 Streamlit 1.31+ 에서 지원됩니다.

**Gradio:**

```python
import gradio as gr

def query_fn(message, history, request: gr.Request):
    access_token = request.headers.get("x-forwarded-access-token")
    # access_token으로 Databricks 리소스 접근
```

Gradio에서는 함수의 `request` 매개변수를 통해 HTTP 헤더에 접근합니다. `gr.Request` 타입 힌트를 반드시 추가해야 Gradio가 자동으로 request 객체를 주입합니다.

**Flask:**

```python
from flask import request

user_token = request.headers.get('x-forwarded-access-token')
```

**FastAPI:**

```python
from fastapi import Request

@app.get("/data")
async def get_data(request: Request):
    user_token = request.headers.get("x-forwarded-access-token")
    # user_token으로 쿼리 실행
```

**Express (Node.js):**

```javascript
const userAccessToken = req.header('x-forwarded-access-token');
```

{% hint style="warning" %}
** 토큰 보안 주의**: 사용자 토큰을 로그에 기록하거나 외부 서비스에 전달하지 마세요. 이 토큰은 해당 사용자의 Databricks 리소스에 접근할 수 있는 자격 증명이므로, 유출 시 해당 사용자의 모든 권한이 노출됩니다.
{% endhint %}

### 코드 예시: 사용자 인증으로 쿼리 실행

아래 코드는 앱 인증이 아닌 ** 현재 로그인한 사용자의 권한** 으로 쿼리를 실행합니다. 이렇게 하면 Unity Catalog의 RLS(Row-Level Security)와 Column Masking이 해당 사용자에게 자동으로 적용됩니다.

```python
from databricks import sql
from databricks.sdk.core import Config
from flask import request

cfg = Config()
user_token = request.headers.get("x-forwarded-access-token")

conn = sql.connect(
    server_hostname=cfg.host,
    http_path="/sql/1.0/warehouses/<warehouse-id>",
    access_token=user_token   # 사용자 토큰으로 접근
)

query = "SELECT * FROM catalog.schema.my_table LIMIT 1000"
with conn.cursor() as cursor:
    cursor.execute(query)
    df = cursor.fetchall_arrow().to_pandas()
```

앱 인증 코드와 비교하면 차이는 단 하나입니다: `credentials_provider=lambda: cfg.authenticate` 대신 `access_token=user_token`을 사용합니다. 전자는 SP의 권한으로, 후자는 현재 사용자의 권한으로 쿼리가 실행됩니다.

---

## 비교: 어떤 인증을 사용해야 할까?

두 인증 모델을 언제 사용해야 하는지 결정하는 것은 앱 설계의 핵심 결정 사항입니다. 아래 표를 참고하여 앱의 요구사항에 맞는 인증 모델을 선택하세요.

| 모델 | 사용 시점 | 예시 |
|------|-----------|------|
| ** 앱 인증**| 사용자 아이덴티티와 무관한 작업 | 로그 기록, 공유 설정 접근, 외부 서비스 호출 |
| ** 사용자 인증**| 현재 사용자 컨텍스트가 필요한 경우 | Unity Catalog 쿼리, 컴퓨트 실행, RLS 적용 |
| ** 둘 다 병행**| 혼합 작업 | 앱 인증으로 로깅 + 사용자 인증으로 필터된 데이터 조회 |

{% hint style="info" %}
** 실무 가이드라인**:
- ** 대부분의 내부 대시보드** 는 앱 인증만으로 충분합니다. 모든 사용자가 동일한 데이터를 볼 수 있다면 SP 인증이 더 간단합니다.
- ** 민감 데이터를 다루는 앱**(급여, 개인정보, 보안 로그 등)은 반드시 사용자 인증을 사용하세요. UC의 RLS/Column Masking이 자동 적용됩니다.
- ** 혼합 패턴이 가장 일반적** 입니다. 앱의 기본 설정 로딩, 감사 로그 기록은 SP 인증으로, 사용자별 데이터 조회는 사용자 인증으로 처리합니다.
{% endhint %}

---

## 보안 베스트 프랙티스

안전한 Databricks App을 구축하기 위한 핵심 원칙을 정리합니다. 이 원칙들은 "하면 좋은 것"이 아니라, 프로덕션 앱에서 ** 반드시 준수해야 하는 필수 사항** 입니다.

### 1. Secret 관리

외부 API 키, 비밀번호 등 민감 정보는 반드시 **Databricks Secret Scope** 에 저장하고, `app.yaml`에서 `valueFrom`으로 참조합니다.

```yaml
# 올바른 방법: Secret 리소스로 관리
env:
  - name: EXTERNAL_API_KEY
    valueFrom: my_api_secret
resources:
  - name: my_api_secret
    type: secret
```

이렇게 하면 API 키가 코드나 설정 파일에 노출되지 않습니다. Secret 값은 Databricks가 런타임에 안전하게 주입합니다.

### 2. 환경변수 보안

`app.yaml`의 `value` 필드에는 ** 절대 민감 정보를 넣지 마세요**. 이 파일은 Git에 커밋되므로 평문 값이 노출됩니다.

### 3. HTTPS 자동 적용

Databricks Apps는 모든 앱 URL에 **HTTPS를 자동으로 적용** 합니다. SSL 인증서를 직접 관리할 필요가 없습니다. 앱과 사용자 간의 모든 통신은 TLS로 암호화됩니다.

### 4. CORS 설정

Databricks Apps는 앱 URL에 대한 CORS(Cross-Origin Resource Sharing)를 자동으로 관리합니다. 외부 도메인에서 앱의 API를 호출해야 하는 경우에만 앱 코드에서 추가 CORS 설정이 필요합니다.

{% hint style="warning" %}
** 보안 체크리스트**:
- 코드에 PAT, API 키, 비밀번호가 하드코딩되어 있지 않은가?
- `app.yaml`의 `value`에 민감 정보가 없는가?
- SP에 최소 권한만 부여되었는가?
- 사용자 토큰을 로그에 기록하고 있지 않은가?
- `.gitignore`에 `.env` 파일이 포함되어 있는가?
{% endhint %}
