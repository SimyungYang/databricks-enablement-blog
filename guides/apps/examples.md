# 예제 (Streamlit, FastAPI)

---

## 예제 1: Streamlit 앱으로 테이블 조회

Unity Catalog 테이블을 읽어 Streamlit 대시보드에 표시하고, 데이터를 편집하여 다시 저장하는 앱입니다.

### 사전 준비

서비스 프린시펄에 다음 권한 부여:

- Unity Catalog 테이블에 대한 `SELECT` 권한
- Unity Catalog 테이블에 대한 `MODIFY` 권한 (편집 기능 사용 시)
- SQL Warehouse에 대한 `CAN USE` 권한

### requirements.txt

```
databricks-sdk
databricks-sql-connector
streamlit
pandas
```

### app.yaml

```yaml
command: ['streamlit', 'run', 'app.py']
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
  - name: STREAMLIT_GATHER_USAGE_STATS
    value: 'false'
```

### app.py

```python
import math
import os
import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()

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


def read_table(table_name: str, conn) -> pd.DataFrame:
    """Unity Catalog 테이블을 읽어 DataFrame으로 반환합니다."""
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()


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

### 배포

```bash
# 1. 앱 생성 (UI에서 또는 CLI로)
databricks apps create my-streamlit-app

# 2. 리소스 연결 (UI의 Configure에서 SQL Warehouse 추가)

# 3. 배포
databricks apps deploy my-streamlit-app --source-code-path ./my-streamlit-app
```

---

## 예제 2: FastAPI REST 엔드포인트

Unity Catalog 테이블에 대한 CRUD API를 FastAPI로 제공하는 예제입니다.

### requirements.txt

```
databricks-sdk
databricks-sql-connector
fastapi
uvicorn
pandas
```

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


class QueryRequest(BaseModel):
    """SQL 쿼리 요청 모델"""
    sql: str


class TableResponse(BaseModel):
    """테이블 조회 응답 모델"""
    columns: list[str]
    data: list[dict]
    row_count: int


@app.get("/")
def root():
    """API 헬스 체크"""
    return {"status": "healthy", "message": "Databricks Data API is running"}


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
