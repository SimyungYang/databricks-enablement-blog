# 인증 (Authentication & Authorization)

Databricks Apps는 OAuth 2.0 기반으로 두 가지 인증 모델을 제공합니다.

---

## 1. 앱 인증 (App Authorization)

앱의 **서비스 프린시펄** 아이덴티티로 Databricks 리소스에 접근합니다.

### 특징

- 앱 생성 시 자동으로 서비스 프린시펄이 생성됨
- `DATABRICKS_CLIENT_ID`와 `DATABRICKS_CLIENT_SECRET`가 자동 주입됨
- 모든 사용자가 동일한 권한으로 접근 (사용자별 접근 제어 불가)
- 배포 간에 아이덴티티가 유지됨

### 사용 시나리오

- 백그라운드 작업 실행
- 공유 설정/메타데이터 관리
- 로깅 및 사용 메트릭
- 외부 서비스 호출

### 코드 예시 (Python)

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

---

## 2. 사용자 인증 (User Authorization)

현재 로그인한 **사용자의 아이덴티티와 권한** 으로 리소스에 접근합니다.

{% hint style="info" %}
** 상태**: Public Preview. 워크스페이스 관리자가 기능을 활성화해야 합니다.
{% endhint %}

### 특징

- 사용자별 접근 제어 가능 (Unity Catalog 정책 자동 적용)
- Row-level 필터, Column 마스킹이 자동으로 적용됨
- 스코프(scope) 기반으로 접근 범위 제한
- HTTP 헤더 `x-forwarded-access-token`으로 사용자 토큰 전달

### 주요 스코프

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

**Streamlit:**

```python
import streamlit as st

user_access_token = st.context.headers.get('x-forwarded-access-token')
```

**Gradio:**

```python
import gradio as gr

def query_fn(message, history, request: gr.Request):
    access_token = request.headers.get("x-forwarded-access-token")
    # access_token으로 Databricks 리소스 접근
```

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

### 코드 예시: 사용자 인증으로 쿼리 실행

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

---

## 비교: 어떤 인증을 사용해야 할까?

| 모델 | 사용 시점 | 예시 |
|------|-----------|------|
| **앱 인증**| 사용자 아이덴티티와 무관한 작업 | 로그 기록, 공유 설정 접근, 외부 서비스 호출 |
| ** 사용자 인증**| 현재 사용자 컨텍스트가 필요한 경우 | Unity Catalog 쿼리, 컴퓨트 실행, RLS 적용 |
| ** 둘 다 병행**| 혼합 작업 | 앱 인증으로 로깅 + 사용자 인증으로 필터된 데이터 조회 |
