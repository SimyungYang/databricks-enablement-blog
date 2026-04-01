# 리소스 & 환경변수

---

## 리소스 (Resources)

리소스는 앱이 Databricks 플랫폼 기능에 접근하기 위한 선언적 의존성입니다. 하드코딩 대신 리소스를 사용하면 **자격 증명 자동 관리, 환경 간 이식성, 보안 접근** 이 보장됩니다.

### 지원 리소스 유형

| 리소스 유형 | 기본 키 | 용도 |
|-------------|---------|------|
| Databricks App | `app` | 앱 간 통신 |
| Genie Space | `genie-space` | 자연어 분석 인터페이스 |
| Lakebase Database | `postgres` / `database` | PostgreSQL 데이터 저장소 |
| LakeFlow Job | `job` | 데이터 워크플로우 |
| MLflow Experiments | `experiment` | ML 실험 추적 |
| Model Serving Endpoint | `serving-endpoint` | ML 모델 추론 |
| Secret | `secret` | 민감 정보 저장 |
| SQL Warehouse | `sql-warehouse` | SQL 쿼리 컴퓨트 |
| UC Connection | `connection` | 외부 데이터 소스 접근 |
| UC Table | `table` | 구조화 데이터 저장 |
| User-defined Function | `function` | SQL/Python 함수 |
| UC Volume | `volume` | 파일 저장소 |
| Vector Search Index | `vector-search-index` | 시맨틱 검색 |

### 리소스 추가 방법 (UI)

1. 앱 생성/편집 시 **Configure** 단계로 이동
2. **App resources**섹션에서 **+ Add resource** 클릭
3. 리소스 유형 선택 (예: SQL Warehouse)
4. 앱 서비스 프린시펄에 적절한 권한 설정
5. 리소스 키 지정 (app.yaml에서 참조할 이름)

### SQL Warehouse 연결 예시

**app.yaml:**

```yaml
command: ['streamlit', 'run', 'app.py']
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
```

**app.py:**

```python
import os
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()
warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
http_path = f"/sql/1.0/warehouses/{warehouse_id}"

conn = sql.connect(
    server_hostname=cfg.host.replace("https://", ""),
    http_path=http_path,
    credentials_provider=lambda: cfg.authenticate,
)
```

### Serving Endpoint 연결 예시

**app.yaml:**

```yaml
command: ['python', 'app.py']
env:
  - name: SERVING_ENDPOINT
    valueFrom: serving_endpoint
```

**app.py:**

```python
import os
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
endpoint_name = os.getenv("SERVING_ENDPOINT")

response = w.serving_endpoints.query(
    name=endpoint_name,
    dataframe_records=[{"prompt": "Hello, world!"}]
)
```

### Secret 사용 예시

**app.yaml:**

```yaml
env:
  - name: EXTERNAL_API_KEY
    valueFrom: my_api_secret
```

**app.py:**

```python
import os

api_key = os.getenv("EXTERNAL_API_KEY")
# api_key를 사용하여 외부 API 호출
```

### 권한 모델

각 리소스 유형마다 설정 가능한 권한:

| 리소스 | 권한 옵션 |
|--------|-----------|
| SQL Warehouse | Can use, Can manage |
| Model Serving Endpoint | Can view, Can query, Can manage |
| Secret | Can read, Can write, Can manage |

{% hint style="tip" %}
**최소 권한 원칙**: 앱에 필요한 최소한의 권한만 부여하세요. 예를 들어, 쿼리만 실행한다면 SQL Warehouse에 `CAN USE`만 부여합니다.
{% endhint %}

---

## 환경 변수

### 자동 주입 환경 변수

Databricks가 앱 런타임에 자동으로 주입하는 변수:

| 변수 | 설명 |
|------|------|
| `DATABRICKS_CLIENT_ID` | 서비스 프린시펄 OAuth 클라이언트 ID |
| `DATABRICKS_CLIENT_SECRET` | 서비스 프린시펄 OAuth 클라이언트 시크릿 |
| `DATABRICKS_HOST` | 워크스페이스 URL |
| `DATABRICKS_APP_PORT` | 앱이 리슨해야 할 포트 번호 |

### 커스텀 환경 변수 정의

```yaml
env:
  # 정적 값 (하드코딩 허용: 피처 토글, 리전, 타임존 등)
  - name: FEATURE_FLAG_NEW_UI
    value: 'true'
  - name: DEFAULT_TIMEZONE
    value: 'Asia/Seoul'

  # 리소스 참조 (시크릿, 웨어하우스 등)
  - name: WAREHOUSE_ID
    valueFrom: sql_warehouse
  - name: SECRET_KEY
    valueFrom: secret
```

### 코드에서 접근

**Python:**

```python
import os
warehouse_id = os.getenv("WAREHOUSE_ID")
```

**JavaScript:**

```javascript
const warehouseId = process.env.WAREHOUSE_ID;
```

{% hint style="warning" %}
`app.yaml` 외부에서 정의한 환경 변수는 앱에서 사용할 수 없습니다. 유일한 예외는 `DATABRICKS_APP_PORT`입니다.
{% endhint %}
