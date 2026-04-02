# 예제 (Streamlit, FastAPI, Agent UI)

---

## 예제 1: Streamlit 앱으로 테이블 조회

Unity Catalog 테이블을 읽어 Streamlit 대시보드에 표시하고, 데이터를 편집하여 다시 저장하는 앱입니다. 이 예제를 통해 Databricks Apps의 핵심 패턴인 **SQL Warehouse 연결, 인증, 데이터 CRUD** 를 학습합니다.

### 사전 준비

서비스 프린시펄에 다음 권한 부여:

- Unity Catalog 테이블에 대한 `SELECT` 권한
- Unity Catalog 테이블에 대한 `MODIFY` 권한 (편집 기능 사용 시)
- SQL Warehouse에 대한 `CAN USE` 권한

{% hint style="warning" %}
**권한 부여를 잊지 마세요**: 가장 흔한 실수가 이 단계를 건너뛰는 것입니다. 앱은 정상 배포되지만 데이터 조회 시 `Permission denied` 오류가 발생합니다. 앱의 Overview 페이지에서 서비스 프린시펄 이름을 확인한 후, SQL Editor에서 다음을 실행하세요:
```sql
GRANT SELECT, MODIFY ON TABLE catalog.schema.table TO `<sp-application-id>`;
GRANT USE CATALOG ON CATALOG catalog TO `<sp-application-id>`;
GRANT USE SCHEMA ON SCHEMA catalog.schema TO `<sp-application-id>`;
```
{% endhint %}

### requirements.txt

```
databricks-sdk
databricks-sql-connector
streamlit
pandas
```

각 패키지의 역할은 다음과 같습니다: `databricks-sdk`는 인증 처리(Config), `databricks-sql-connector`는 SQL Warehouse 연결, `streamlit`은 웹 UI 프레임워크, `pandas`는 데이터 처리입니다. 프로덕션에서는 반드시 버전을 명시하세요 (예: `streamlit==1.32.0`).

### app.yaml

```yaml
command: ['streamlit', 'run', 'app.py']
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
  - name: STREAMLIT_GATHER_USAGE_STATS
    value: 'false'
```

`command`에서 Streamlit을 직접 실행합니다. Streamlit은 자체적으로 포트를 관리하므로 `DATABRICKS_APP_PORT`를 별도로 지정하지 않아도 됩니다. `STREAMLIT_GATHER_USAGE_STATS=false`는 Streamlit의 사용 통계 수집을 비활성화하여 외부로의 네트워크 요청을 줄입니다.

### app.py

아래 코드의 각 부분이 왜 이렇게 작성되었는지 설명합니다.

```python
import math
import os
import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()
```

`Config()`는 환경변수에서 Databricks 인증 정보를 자동으로 읽습니다. 앱 실행 시 `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`가 자동 주입되므로 별도 설정이 필요 없습니다.

```python
def get_connection():
    """SQL Warehouse에 연결합니다."""
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
    http_path = f"/sql/1.0/warehouses/{warehouse_id}"

    server_hostname = cfg.host
    if server_hostname.startswith("https://"):
        server_hostname = server_hostname.replace("https://", "")
    elif server_hostname.startswith("http://"):
        server_hostname = server_hostname.replace("http://", "")

    return sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
        _use_arrow_native_complex_types=False,
    )
```

`server_hostname`에서 `https://`를 제거하는 이유는 `sql.connect()`가 호스트명만 받기 때문입니다. `credentials_provider=lambda: cfg.authenticate`는 SDK가 OAuth 토큰을 자동으로 발급/갱신하도록 위임합니다. `_use_arrow_native_complex_types=False`는 Arrow의 복합 타입을 Pandas 네이티브 타입으로 변환하여 호환성을 보장합니다.

```python
def read_table(table_name: str, conn) -> pd.DataFrame:
    """Unity Catalog 테이블을 읽어 DataFrame으로 반환합니다."""
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()
```

`fetchall_arrow().to_pandas()`는 Arrow 포맷으로 데이터를 가져온 뒤 Pandas DataFrame으로 변환합니다. Arrow를 거치는 이유는 **대용량 데이터 전송에서 JSON 직렬화보다 훨씬 빠르기 때문** 입니다.

{% hint style="warning" %}
**SQL 인젝션 주의**: 이 예제에서 `f"SELECT * FROM {table_name}"`은 사용자 입력을 직접 SQL에 넣으므로 SQL 인젝션에 취약합니다. 프로덕션에서는 테이블 이름을 허용 목록으로 검증하거나, 파라미터화된 쿼리를 사용하세요.
{% endhint %}

```python
def format_value(val):
    """SQL INSERT용 값 포맷팅"""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "NULL"
    else:
        return repr(val)


def insert_overwrite_table(table_name: str, df: pd.DataFrame, conn):
    """편집된 데이터를 테이블에 저장합니다."""
    progress = st.empty()
    with conn.cursor() as cursor:
        rows = list(df.itertuples(index=False))
        values = ",".join(
            [f"({','.join(map(format_value, row))})" for row in rows]
        )
        with progress:
            st.info("Databricks SQL 실행 중...")
        cursor.execute(f"INSERT OVERWRITE {table_name} VALUES {values}")
    progress.empty()
    st.success("변경 사항이 저장되었습니다!")
```

`INSERT OVERWRITE`는 기존 데이터를 완전히 대체합니다. 이 방식은 소규모 테이블에서는 괜찮지만, 대용량 테이블에서는 `MERGE INTO`를 사용하는 것이 더 효율적입니다.

```python
# ===== UI 구성 =====
st.title("Unity Catalog 테이블 뷰어")

table_name = st.text_input(
    "Unity Catalog 테이블 이름:",
    placeholder="catalog.schema.table_name",
)

if table_name:
    conn = get_connection()
    if conn:
        st.success("SQL Warehouse 연결 성공!")

        # 테이블 읽기
        original_df = read_table(table_name, conn)

        # 편집 가능한 데이터 에디터
        edited_df = st.data_editor(
            original_df, num_rows="dynamic", hide_index=True
        )

        # 변경 사항 감지
        df_diff = pd.concat([original_df, edited_df]).drop_duplicates(
            keep=False
        )
        if not df_diff.empty:
            st.warning(f"저장되지 않은 변경 사항이 {len(df_diff) // 2}건 있습니다.")
            if st.button("변경 사항 저장"):
                insert_overwrite_table(table_name, edited_df, conn)
                st.rerun()
else:
    st.info("테이블 이름을 입력하면 데이터가 로드됩니다.")
```

`st.data_editor()`는 Streamlit의 내장 편집 가능 테이블 위젯입니다. `num_rows="dynamic"`은 행 추가/삭제를 허용합니다. `st.rerun()`은 저장 후 페이지를 새로고침하여 최신 데이터를 다시 로드합니다.

### 배포

```bash
# 1. 앱 생성 (UI에서 또는 CLI로)
databricks apps create my-streamlit-app

# 2. 리소스 연결 (UI의 Configure에서 SQL Warehouse 추가)

# 3. 배포
databricks apps deploy my-streamlit-app --source-code-path ./my-streamlit-app
```

### 프로덕션 전환 시 고려사항

이 예제를 프로덕션에서 사용하려면 다음 사항을 개선해야 합니다.

| 항목 | 현재 예제 | 프로덕션 권장 |
|------|----------|-------------|
| **SQL 인젝션** | 사용자 입력을 직접 SQL에 삽입 | 테이블 이름 허용 목록 검증, 파라미터화 쿼리 |
| **에러 핸들링** | 기본 에러만 처리 | try/except로 연결 실패, 권한 오류, 타임아웃 처리 |
| **성능** | 매 요청마다 새 연결 생성 | 연결 풀링 또는 `st.cache_resource`로 연결 재사용 |
| **대용량 데이터** | `SELECT *` 전체 조회 | 페이지네이션, 필터 조건 추가, LIMIT 강제 적용 |
| **의존성 버전** | 버전 미명시 | `streamlit==1.32.0`처럼 버전 고정 |

---

## 예제 2: FastAPI REST 엔드포인트

Unity Catalog 테이블에 대한 CRUD API를 FastAPI로 제공하는 예제입니다. 이 예제는 **Databricks 데이터를 REST API로 노출** 하여 외부 시스템이나 프론트엔드 앱에서 접근할 수 있게 하는 패턴을 보여줍니다.

### 왜 FastAPI인가?

Streamlit은 UI를 포함한 풀스택 앱에 적합하지만, **프론트엔드를 별도로 개발** 하거나 **다른 시스템에서 데이터를 호출** 해야 하는 경우에는 REST API가 필요합니다. FastAPI는 다음과 같은 이유로 Databricks Apps에서 API 서버로 가장 적합합니다:
- **자동 문서 생성**: Swagger UI (`/docs`)가 자동으로 생성되어 API 테스트와 문서화가 동시에 해결됩니다
- **타입 안전성**: Pydantic 모델로 요청/응답 형식을 엄격하게 정의하여 런타임 오류를 방지합니다
- **비동기 지원**: `async/await`으로 고성능 비동기 처리가 가능합니다

### requirements.txt

```
databricks-sdk
databricks-sql-connector
fastapi
uvicorn
pandas
```

`uvicorn`은 FastAPI의 ASGI 서버입니다. FastAPI는 프레임워크일 뿐이고, 실제로 HTTP 요청을 처리하는 것은 uvicorn입니다.

### app.yaml

```yaml
command:
  - uvicorn
  - app:app
  - --host
  - '0.0.0.0'
  - --port
  - '${DATABRICKS_APP_PORT}'
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
```

`--host 0.0.0.0`은 컨테이너 외부(리버스 프록시)에서 접근 가능하도록 모든 인터페이스에 바인딩합니다. `--port ${DATABRICKS_APP_PORT}`는 Databricks가 동적으로 할당한 포트를 사용합니다. 이 두 설정이 없으면 앱이 시작되어도 외부에서 접속할 수 없습니다.

### app.py

```python
import os
from typing import Optional

import pandas as pd
from databricks import sql
from databricks.sdk.core import Config
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(
    title="Databricks Data API",
    description="Unity Catalog 테이블 조회 REST API",
    version="1.0.0",
)

cfg = Config()
```

`FastAPI()` 인스턴스 생성 시 `title`, `description`, `version`을 지정하면 자동 생성되는 Swagger UI에 반영됩니다. 앱 URL에 `/docs`를 추가하면 이 API의 인터랙티브 문서를 볼 수 있습니다.

```python
def get_connection():
    """SQL Warehouse 연결을 반환합니다."""
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
    http_path = f"/sql/1.0/warehouses/{warehouse_id}"

    server_hostname = cfg.host
    if server_hostname.startswith("https://"):
        server_hostname = server_hostname.replace("https://", "")

    return sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )
```

연결 함수는 Streamlit 예제와 동일한 패턴입니다. `credentials_provider`가 OAuth 토큰의 발급과 갱신을 자동으로 처리합니다.

```python
class QueryRequest(BaseModel):
    """SQL 쿼리 요청 모델"""
    sql: str


class TableResponse(BaseModel):
    """테이블 조회 응답 모델"""
    columns: list[str]
    data: list[dict]
    row_count: int
```

Pydantic의 `BaseModel`로 요청/응답 형식을 정의합니다. 이렇게 하면 FastAPI가 자동으로 입력 유효성 검사, JSON 직렬화/역직렬화, API 문서 생성을 처리합니다. 잘못된 형식의 요청이 들어오면 422 에러와 함께 상세한 에러 메시지가 자동으로 반환됩니다.

```python
@app.get("/")
def root():
    """API 헬스 체크"""
    return {"status": "healthy", "message": "Databricks Data API is running"}
```

루트 엔드포인트는 **헬스체크** 용도입니다. CI/CD 파이프라인에서 배포 후 앱이 정상적으로 실행 중인지 확인할 수 있습니다.

```python
@app.get("/tables/{catalog}/{schema}/{table}", response_model=TableResponse)
def read_table(
    catalog: str,
    schema: str,
    table: str,
    limit: int = Query(default=100, le=10000),
    offset: int = Query(default=0, ge=0),
):
    """Unity Catalog 테이블을 조회합니다.

    Args:
        catalog: 카탈로그 이름
        schema: 스키마 이름
        table: 테이블 이름
        limit: 반환 행 수 (최대 10,000)
        offset: 시작 위치
    """
    table_name = f"`{catalog}`.`{schema}`.`{table}`"
    query = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query)
            df = cursor.fetchall_arrow().to_pandas()
        conn.close()

        return TableResponse(
            columns=df.columns.tolist(),
            data=df.to_dict(orient="records"),
            row_count=len(df),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

URL 경로에 `{catalog}/{schema}/{table}`을 사용하면 REST 스타일의 직관적인 API가 됩니다. `Query(default=100, le=10000)`은 `limit` 파라미터의 기본값을 100으로, 최대값을 10,000으로 제한합니다. 백틱(`)으로 테이블 이름을 감싸는 이유는 하이픈이나 특수문자가 포함된 이름을 안전하게 처리하기 위해서입니다.

```python
@app.get("/tables/{catalog}/{schema}/{table}/schema")
def get_table_schema(catalog: str, schema: str, table: str):
    """테이블 스키마(컬럼 정보)를 조회합니다."""
    table_name = f"`{catalog}`.`{schema}`.`{table}`"
    query = f"DESCRIBE TABLE {table_name}"

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query)
            df = cursor.fetchall_arrow().to_pandas()
        conn.close()

        return {
            "table": f"{catalog}.{schema}.{table}",
            "columns": df.to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

`DESCRIBE TABLE`은 테이블의 컬럼 이름, 데이터 타입, 설명 등 메타데이터를 반환합니다. 프론트엔드에서 동적으로 폼이나 테이블을 생성할 때 유용합니다.

```python
@app.post("/query")
def execute_query(request: QueryRequest):
    """커스텀 SQL 쿼리를 실행합니다.

    보안 주의: 프로덕션에서는 SQL 인젝션 방어 및 허용 쿼리 제한을 구현하세요.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(request.sql)
            df = cursor.fetchall_arrow().to_pandas()
        conn.close()

        return {
            "columns": df.columns.tolist(),
            "data": df.to_dict(orient="records"),
            "row_count": len(df),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

{% hint style="warning" %}
**보안 경고**: `/query` 엔드포인트는 임의의 SQL을 실행하므로, 프로덕션에서는 반드시 다음을 구현하세요:
1. **허용된 SQL 유형만 실행**(예: `SELECT`만 허용, `DROP`/`DELETE` 차단)
2. **쿼리 크기 제한**(LIMIT 강제 추가)
3. **접근 가능한 카탈로그/스키마 제한**
4. **감사 로그**(누가 어떤 쿼리를 실행했는지 기록)
{% endhint %}

### API 사용 예시

```bash
# 헬스 체크
curl https://<app-url>/

# 테이블 조회
curl "https://<app-url>/tables/my_catalog/my_schema/my_table?limit=50"

# 테이블 스키마 조회
curl "https://<app-url>/tables/my_catalog/my_schema/my_table/schema"

# 커스텀 쿼리 실행
curl -X POST "https://<app-url>/query" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT count(*) as cnt FROM my_catalog.my_schema.my_table"}'
```

{% hint style="info" %}
**API 문서 자동 생성**: 앱 URL에 `/docs`를 추가하면 Swagger UI가 열립니다. 여기서 모든 엔드포인트를 인터랙티브하게 테스트할 수 있습니다. `/redoc`에서는 ReDoc 스타일의 읽기 전용 문서를 볼 수 있습니다.
{% endhint %}

### 프로덕션 전환 시 고려사항

| 항목 | 현재 예제 | 프로덕션 권장 |
|------|----------|-------------|
| **SQL 인젝션** | 입력 검증 없음 | 허용 쿼리 유형 제한, 파라미터화 쿼리 |
| **인증** | Databricks SSO만 | API Key 추가 또는 사용자 인증 토큰 검증 |
| **Rate Limiting** | 없음 | `slowapi` 패키지로 요청 속도 제한 |
| **연결 관리** | 매 요청마다 새 연결 | 연결 풀링 구현 |
| **로깅** | 기본 로그만 | 구조화된 감사 로그 (사용자, 쿼리, 응답 시간) |
| **에러 응답** | 내부 에러를 그대로 반환 | 사용자 친화적 에러 메시지, 내부 상세는 로그에만 |

---

## 예제 3: Agent UI (Streamlit + Model Serving)

Databricks Model Serving 엔드포인트를 호출하는 AI 챗봇 UI입니다. 이 예제는 **Foundation Model API 또는 커스텀 Agent를 웹 인터페이스로 노출** 하는 가장 일반적인 패턴을 보여줍니다.

### 왜 Agent UI인가?

Databricks에서 AI Agent를 개발하면 Model Serving Endpoint로 배포할 수 있습니다. 하지만 엔드포인트 자체는 REST API일 뿐, **사용자가 직접 대화할 수 있는 UI가 없습니다**. Databricks Apps로 Agent UI를 만들면:
- 비기술 사용자도 Agent와 대화할 수 있습니다
- 워크스페이스 SSO로 인증이 자동 처리됩니다
- 대화 이력, 피드백 등 부가 기능을 추가할 수 있습니다

### requirements.txt

```
databricks-sdk
streamlit
```

Agent UI는 최소한의 패키지만 필요합니다. `databricks-sdk`가 Model Serving 호출과 인증을 모두 처리합니다. SQL 연결이 필요하면 `databricks-sql-connector`와 `pandas`를 추가하세요.

### app.yaml

```yaml
command: ['streamlit', 'run', 'app.py']
env:
  - name: SERVING_ENDPOINT
    valueFrom: serving_endpoint
resources:
  - name: serving_endpoint
    type: serving-endpoint
```

`serving-endpoint` 리소스를 선언하고, `SERVING_ENDPOINT` 환경변수로 엔드포인트 이름을 주입합니다. 앱의 SP에 해당 엔드포인트에 대한 `CAN QUERY` 권한을 부여해야 합니다.

### app.py

```python
import os
import streamlit as st
from databricks.sdk import WorkspaceClient

# Databricks 클라이언트 초기화 (인증 자동 처리)
w = WorkspaceClient()
endpoint_name = os.getenv("SERVING_ENDPOINT")

st.title("AI Assistant")
st.caption("Databricks Model Serving 기반 AI 챗봇")

# 세션 상태에 대화 이력 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 이력 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            try:
                response = w.serving_endpoints.query(
                    name=endpoint_name,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                )
                assistant_message = response.choices[0].message.content
                st.markdown(assistant_message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_message}
                )
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
```

이 코드의 핵심 패턴을 설명합니다.

**`WorkspaceClient()`**: `Config()`와 마찬가지로 환경변수에서 인증 정보를 자동으로 읽습니다. Model Serving 호출 시 SP의 OAuth 토큰이 자동으로 사용됩니다.

**`st.session_state.messages`**: Streamlit의 세션 상태에 대화 이력을 저장합니다. 이 상태는 사용자의 브라우저 세션에 귀속되므로, 다른 사용자의 대화와 섞이지 않습니다. 단, 앱이 재시작되면 초기화됩니다.

**`w.serving_endpoints.query()`**: Databricks SDK를 통해 Model Serving Endpoint에 ChatCompletion 형식의 요청을 보냅니다. `messages` 배열에 전체 대화 이력을 전달하여 문맥을 유지합니다.

**`response.choices[0].message.content`**: OpenAI ChatCompletion API와 동일한 응답 형식입니다. Databricks Model Serving은 이 형식을 표준으로 사용합니다.

{% hint style="info" %}
**Agent 앱 확장 아이디어**:
- **대화 이력 저장**: UC 테이블에 대화 이력을 저장하면 세션 간 대화가 유지됩니다
- **피드백 수집**: 각 응답에 좋아요/싫어요 버튼을 추가하여 모델 품질 개선에 활용
- **파일 업로드**: `st.file_uploader()`로 문서를 업로드하고 RAG에 활용
- **스트리밍 응답**: `stream=True`로 토큰 단위 스트리밍 지원 (UX 개선)
{% endhint %}

### 프로덕션 전환 시 고려사항

| 항목 | 현재 예제 | 프로덕션 권장 |
|------|----------|-------------|
| **대화 이력** | 세션 상태(메모리)에만 저장 | UC 테이블 또는 Lakebase에 영속 저장 |
| **에러 핸들링** | 기본 에러 메시지 | 에러 유형별 사용자 친화적 메시지 |
| **토큰 제한** | 전체 대화 이력 전송 | 최근 N개 메시지만 전송, 또는 요약 |
| **동시 사용** | 기본 Streamlit | `st.cache_resource`로 클라이언트 재사용 |
| **사용자 인증** | SP 인증 (모든 사용자 동일 권한) | 사용자 인증으로 개인화된 응답 |

---

## 흔한 오류와 디버깅 방법

모든 예제에서 공통으로 발생할 수 있는 오류와 해결 방법을 정리합니다.

| 오류 메시지 | 원인 | 해결 방법 |
|------------|------|-----------|
| `PERMISSION_DENIED: User does not have USE CATALOG` | SP에 카탈로그 접근 권한 미부여 | `GRANT USE CATALOG ON CATALOG <name> TO <sp-id>` |
| `TABLE_OR_VIEW_NOT_FOUND` | 테이블 이름 오타 또는 SP에 테이블 접근 권한 없음 | 테이블 이름 확인, `GRANT SELECT` 부여 |
| `ENDPOINT_NOT_FOUND` | Serving Endpoint 이름 오타 또는 SP에 접근 권한 없음 | 엔드포인트 이름 확인, `CAN QUERY` 권한 부여 |
| `Connection refused` / Timeout | SQL Warehouse가 중지됨 | Warehouse 시작 또는 Serverless 사용 |
| `ModuleNotFoundError: No module named 'xxx'` | `requirements.txt`에 패키지 누락 | 패키지 추가 후 재배포 |
| `OSError: [Errno 98] Address already in use` | 포트 충돌 | `$DATABRICKS_APP_PORT` 사용 확인 |
| `StreamlitAPIException` | Streamlit 버전 호환성 문제 | `requirements.txt`에서 Streamlit 버전 명시 |

{% hint style="info" %}
**디버깅 순서**: 오류가 발생하면 다음 순서로 확인하세요:
1. **Logs 탭** 에서 에러 메시지 확인 (가장 중요)
2. **SP 권한** 확인 — `GRANT` SQL 실행 여부
3. **환경변수** 확인 — `app.yaml`의 `valueFrom`과 `resources`의 `name` 일치 여부
4. **Warehouse/Endpoint 상태** 확인 — `Running` 상태인지
5. **로컬에서 재현**— `databricks apps run-local --debug`로 동일 오류 발생하는지
{% endhint %}
