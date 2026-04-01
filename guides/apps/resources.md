# 리소스 & 환경변수

---

## 리소스 (Resources)

리소스는 앱이 Databricks 플랫폼 기능에 접근하기 위한 선언적 의존성입니다. 하드코딩 대신 리소스를 사용하면 ** 자격 증명 자동 관리, 환경 간 이식성, 보안 접근** 이 보장됩니다.

### 리소스란 무엇인가?

리소스는 ** 앱이 Databricks 서비스에 접근하기 위한 안전한 통로** 입니다. 왜 직접 API 키나 Warehouse ID를 코드에 넣지 않고 리소스를 사용하는지 이해하면, Databricks Apps의 설계 철학이 명확해집니다.

전통적인 방식에서는 앱이 외부 서비스에 접근하려면 **API 키나 연결 문자열을 코드나 환경변수에 직접 넣어야** 했습니다. 이 방식에는 여러 문제가 있습니다.

| 문제 | 직접 하드코딩 방식 | 리소스 방식 |
|------|-------------------|-----------|
| ** 보안**| 코드에 자격 증명 노출, Git에 커밋 위험 | 런타임에 Databricks가 안전하게 주입 |
| ** 환경 이동**| dev/staging/prod 환경마다 코드 수정 필요 | 리소스 매핑만 변경, 코드 수정 불필요 |
| ** 자격 증명 로테이션**| 토큰 만료 시 코드 재배포 필요 | Databricks가 자동 관리 |
| ** 권한 추적**| 어떤 앱이 어떤 리소스에 접근하는지 파악 어려움 | `app.yaml`에 명시적으로 선언되어 한눈에 파악 |

리소스는 **"이 앱이 이 서비스를 사용한다"는 의도를 선언** 하는 것입니다. 실제 연결 정보는 Databricks 플랫폼이 관리하고, 앱에는 런타임에 안전하게 주입됩니다.

{% hint style="info" %}
** 비유하자면**: 리소스는 회사 출입카드와 같습니다. 직원이 직접 열쇠를 복제하는 것이 아니라, 출입카드에 "어떤 구역에 접근할 수 있는가"를 등록하는 것입니다. 출입카드 자체에는 열쇠 정보가 없고, 카드를 대면 시스템이 권한을 확인하고 문을 열어줍니다.
{% endhint %}

### 지원 리소스 유형

아래 표는 Databricks Apps에서 지원하는 모든 리소스 유형을 정리합니다. 각 리소스의 기본 키는 `app.yaml`에서 `type` 필드에 지정하는 값입니다.

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

이 중에서 실무에서 가장 자주 사용하는 리소스는 **SQL Warehouse**, **Serving Endpoint**, **Secret** 세 가지입니다. 나머지는 특수한 사용 사례에서 필요합니다.

### 리소스 추가 방법 (UI)

1. 앱 생성/편집 시 **Configure** 단계로 이동
2. **App resources** 섹션에서 **+ Add resource** 클릭
3. 리소스 유형 선택 (예: SQL Warehouse)
4. 앱 서비스 프린시펄에 적절한 권한 설정
5. 리소스 키 지정 (app.yaml에서 참조할 이름)

{% hint style="info" %}
** 리소스 추가 시 주의**: 리소스를 추가하면 두 가지가 동시에 설정됩니다. 첫째, `app.yaml`에 리소스 선언이 추가됩니다. 둘째, 앱의 서비스 프린시펄에 해당 리소스에 대한 기본 권한이 부여됩니다. 하지만 UC 테이블에 대한 `SELECT` 권한처럼 세부 권한은 여전히 수동으로 부여해야 합니다.
{% endhint %}

---

### 리소스 유형별 상세 가이드

#### SQL Warehouse: 데이터 조회의 핵심

SQL Warehouse는 앱에서 **Unity Catalog 데이터를 조회하는 컴퓨트 엔진** 입니다. 대부분의 데이터 앱에서 필수적으로 사용됩니다.

** 왜 Serverless Warehouse를 권장하는가?**

| 비교 항목 | Classic Warehouse | Serverless Warehouse |
|-----------|------------------|---------------------|
| ** 시작 시간**| 수 분 (콜드 스타트) | 수 초 |
| ** 자동 중지**| 설정된 유휴 시간 후 | 사용하지 않으면 즉시 중지 |
| ** 비용**| 실행 중 항상 과금 | 쿼리 실행 시간만 과금 |
| ** 관리**| 클러스터 크기 수동 설정 | 자동 스케일링 |

Databricks Apps는 사용자 요청이 있을 때만 쿼리를 실행하므로, 유휴 시간이 긴 편입니다. Classic Warehouse는 유휴 시간에도 과금되지만, **Serverless Warehouse는 쿼리가 없으면 비용이 발생하지 않습니다**. 앱의 비용을 최적화하려면 Serverless를 강력히 권장합니다.

### SQL Warehouse 연결 예시

**app.yaml:**

```yaml
command: ['streamlit', 'run', 'app.py']
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
```

이 설정은 `sql_warehouse`라는 이름의 리소스 값을 `DATABRICKS_WAREHOUSE_ID` 환경변수로 주입합니다. 코드에서는 이 환경변수를 읽어 Warehouse에 연결합니다.

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

`cfg.host`에는 `https://`가 포함되어 있으므로 `replace()`로 제거합니다. `sql.connect()`의 `server_hostname`은 호스트명만 받기 때문입니다. `credentials_provider`는 서비스 프린시펄의 OAuth 토큰을 자동으로 발급/갱신합니다.

#### Serving Endpoint: AI/ML 모델 호출

Serving Endpoint는 앱에서 **ML 모델이나 Foundation Model API를 호출** 할 때 사용합니다.

| Endpoint 유형 | 설명 | 사용 사례 |
|---------------|------|----------|
| **Foundation Model API**| Databricks가 호스팅하는 대형 언어 모델 (DBRX, Llama 등) | RAG 챗봇, 텍스트 분석, 코드 생성 |
| **Custom Model Serving**| 사용자가 MLflow로 등록한 커스텀 모델 | 수요 예측, 이상 탐지, 추천 시스템 |
| **External Model**| OpenAI, Anthropic 등 외부 모델 프록시 | 외부 LLM을 Databricks 거버넌스 하에 사용 |

Agent UI 앱에서는 주로 Foundation Model API나 Custom Model Serving을 호출합니다. 앱의 서비스 프린시펄에 해당 Endpoint에 대한 `CAN QUERY` 권한을 부여해야 합니다.

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

`WorkspaceClient()`는 `Config()`와 마찬가지로 환경변수에서 자동으로 인증 정보를 읽습니다. `query()` 메서드는 내부적으로 Serving Endpoint의 REST API를 호출하고, SP의 OAuth 토큰을 자동으로 사용합니다.

#### Secret: 외부 API 키 관리

Secret은 **Databricks 외부 서비스의 API 키, 비밀번호 등 민감 정보** 를 안전하게 저장하고 앱에 주입하는 데 사용합니다.

**Secret 사용 패턴**: Databricks Secret Scope에 키-값 쌍을 저장하고, `app.yaml`에서 리소스로 선언한 뒤, `valueFrom`으로 환경변수에 주입합니다. 이렇게 하면 민감 정보가 코드나 설정 파일에 노출되지 않습니다.

### Secret 사용 예시

**app.yaml:**

```yaml
env:
  - name: EXTERNAL_API_KEY
    valueFrom: my_api_secret
```

이 설정은 `my_api_secret` 리소스의 값을 `EXTERNAL_API_KEY` 환경변수로 주입합니다. 이 값은 Databricks Secret Scope에 저장된 실제 시크릿 값입니다.

**app.py:**

```python
import os

api_key = os.getenv("EXTERNAL_API_KEY")
# api_key를 사용하여 외부 API 호출
```

코드에서는 단순히 환경변수를 읽기만 합니다. Secret 값의 저장, 암호화, 접근 제어는 Databricks가 관리합니다.

{% hint style="warning" %}
**Secret Scope 설정**: Secret을 앱에서 사용하려면 먼저 Databricks CLI로 Secret Scope를 생성하고 값을 저장해야 합니다. `databricks secrets create-scope --scope my-scope` 후 `databricks secrets put-secret --scope my-scope --key my-key`. 앱의 SP에 해당 Scope에 대한 `READ` 권한을 부여해야 합니다.
{% endhint %}

#### databricks_host: 워크스페이스 URL 동적 참조

`DATABRICKS_HOST`는 Databricks가 자동으로 주입하는 환경변수이지만, 멀티 환경 배포에서는 리소스로 명시적으로 관리하는 것이 유용합니다.

** 왜 동적 참조가 필요한가?** 개발 환경(`dev.databricks.com`)에서 만든 앱을 프로덕션(`prod.databricks.com`)으로 이동할 때, 코드에 워크스페이스 URL이 하드코딩되어 있으면 수정이 필요합니다. `os.getenv("DATABRICKS_HOST")`로 참조하면 환경에 따라 자동으로 올바른 URL이 주입됩니다.

---

### 권한 모델

각 리소스 유형마다 설정 가능한 권한이 다릅니다. 아래 표는 자주 사용하는 리소스의 권한 옵션과 ** 권장 설정** 을 정리합니다.

| 리소스 | 권한 옵션 | 권장 설정 |
|--------|-----------|----------|
| SQL Warehouse | Can use, Can manage | **Can use**(쿼리 실행만 필요한 경우) |
| Model Serving Endpoint | Can view, Can query, Can manage | **Can query**(모델 호출만 필요한 경우) |
| Secret | Can read, Can write, Can manage | **Can read**(읽기만 필요한 경우) |

{% hint style="tip" %}
** 최소 권한 원칙**: 앱에 필요한 최소한의 권한만 부여하세요. 예를 들어, 쿼리만 실행한다면 SQL Warehouse에 `CAN USE`만 부여합니다.
{% endhint %}

{% hint style="warning" %}
** 흔한 실수**: Warehouse에 `CAN USE`를 부여했지만 UC 테이블에 `SELECT`를 부여하지 않는 경우가 많습니다. Warehouse 접근 권한과 테이블 접근 권한은 ** 별도로 관리** 됩니다. 앱의 SP에 `GRANT SELECT ON TABLE catalog.schema.table TO <sp-application-id>`도 실행해야 합니다.
{% endhint %}

---

## 환경 변수

### 자동 주입 환경 변수

Databricks가 앱 런타임에 자동으로 주입하는 변수입니다. 이 변수들은 `app.yaml`에 정의하지 않아도 항상 사용할 수 있습니다.

| 변수 | 설명 |
|------|------|
| `DATABRICKS_CLIENT_ID` | 서비스 프린시펄 OAuth 클라이언트 ID |
| `DATABRICKS_CLIENT_SECRET` | 서비스 프린시펄 OAuth 클라이언트 시크릿 |
| `DATABRICKS_HOST` | 워크스페이스 URL |
| `DATABRICKS_APP_PORT` | 앱이 리슨해야 할 포트 번호 |

이 네 가지 환경변수가 Databricks Apps의 ** 인증과 네트워크 설정을 완전히 자동화** 합니다. `DATABRICKS_CLIENT_ID`와 `DATABRICKS_CLIENT_SECRET`는 서비스 프린시펄의 OAuth 자격 증명이며, `Config()` 또는 `WorkspaceClient()`가 자동으로 읽어 인증에 사용합니다. `DATABRICKS_HOST`는 워크스페이스 URL이며, `DATABRICKS_APP_PORT`는 앱이 바인딩해야 할 포트입니다.

{% hint style="info" %}
**`DATABRICKS_APP_PORT`의 중요성**: 이 환경변수를 무시하면 앱이 시작되지만 외부에서 접속할 수 없습니다. Databricks의 리버스 프록시가 이 포트로 트래픽을 전달하기 때문입니다. FastAPI, Flask 등에서 반드시 이 포트를 사용하세요. Streamlit과 Gradio는 자동으로 처리합니다.
{% endhint %}

---

### 환경변수 vs 리소스: 언제 무엇을 쓰는가

`env`의 `value`와 `valueFrom`, 그리고 `resources`의 관계가 혼동될 수 있습니다. 아래 가이드를 참고하세요.

| 상황 | 사용할 방법 | 이유 |
|------|-----------|------|
| 로그 레벨, 기능 플래그 등 비민감 설정 | `env` + `value` | 환경에 따라 바뀌지 않는 단순 설정값 |
| Warehouse ID, Endpoint 이름 | `env` + `valueFrom` + `resources` | 환경별로 다른 값이 필요하고, 코드 수정 없이 변경 가능해야 함 |
| API 키, 비밀번호 | `env` + `valueFrom` + `resources` (Secret 타입) | 민감 정보는 반드시 Secret으로 관리 |
| Databricks 인증 정보 | 사용하지 않음 (자동 주입) | `DATABRICKS_CLIENT_ID` 등은 Databricks가 자동 주입 |

{% hint style="info" %}
** 판단 기준 요약**: "이 값이 환경(dev/staging/prod)에 따라 바뀔 수 있는가?"가 기준입니다. 바뀔 수 있다면 `valueFrom`으로 리소스 참조를 사용하고, 바뀌지 않는 단순 설정이라면 `value`로 직접 지정합니다. 민감 정보는 무조건 `valueFrom` + Secret 리소스입니다.
{% endhint %}

---

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

`os.getenv()`는 환경변수가 없으면 `None`을 반환합니다. 프로덕션 코드에서는 기본값을 지정하거나 값이 없을 때 명확한 에러를 발생시키는 것이 좋습니다.

**JavaScript:**

```javascript
const warehouseId = process.env.WAREHOUSE_ID;
```

{% hint style="warning" %}
`app.yaml` 외부에서 정의한 환경 변수는 앱에서 사용할 수 없습니다. 유일한 예외는 `DATABRICKS_APP_PORT`입니다.
{% endhint %}

{% hint style="info" %}
** 실무 팁**: 환경변수가 올바르게 주입되었는지 확인하려면, 앱 시작 시 모든 필수 환경변수의 존재 여부를 검증하는 코드를 추가하세요. 이렇게 하면 리소스 이름 오타로 인한 런타임 에러를 앱 시작 시점에 즉시 발견할 수 있습니다.
{% endhint %}
