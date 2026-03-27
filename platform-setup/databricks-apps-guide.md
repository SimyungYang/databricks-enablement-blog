# Databricks Apps 완벽 가이드

> Databricks 플랫폼 위에서 데이터 & AI 애플리케이션을 직접 호스팅하고 배포하는 Databricks Apps의 실전 가이드

---

## 목차

1. [Databricks Apps란?](#databricks-apps란)
2. [핵심 개념](#핵심-개념)
3. [지원 프레임워크](#지원-프레임워크)
4. [앱 생성하기 (UI 기반)](#앱-생성하기-ui-기반)
5. [app.yaml 설정](#appyaml-설정)
6. [컴퓨트 사이즈](#컴퓨트-사이즈)
7. [인증 (Authentication & Authorization)](#인증-authentication--authorization)
8. [리소스 (Resources)](#리소스-resources)
9. [환경 변수](#환경-변수)
10. [배포 워크플로우](#배포-워크플로우)
11. [예제: Streamlit 앱으로 테이블 조회](#예제-streamlit-앱으로-테이블-조회)
12. [예제: FastAPI REST 엔드포인트](#예제-fastapi-rest-엔드포인트)
13. [제한 사항 및 베스트 프랙티스](#제한-사항-및-베스트-프랙티스)

---

## Databricks Apps란?

Databricks Apps는 **Databricks 인프라 위에서 직접 데이터 및 AI 애플리케이션을 개발, 배포, 호스팅**할 수 있는 플랫폼 기능입니다. 별도의 서버나 클라우드 인프라를 구성할 필요 없이, 서버리스 환경에서 앱이 실행됩니다.

### 주요 특징

| 특징 | 설명 |
|------|------|
| **서버리스 호스팅** | 별도 인프라 관리 없이 Databricks가 컨테이너 기반으로 앱을 실행 |
| **Unity Catalog 통합** | 데이터 거버넌스와 접근 제어가 자동으로 적용 |
| **OAuth 기반 인증** | 서비스 프린시펄 및 사용자 인증 모두 지원 |
| **자동 URL 생성** | `https://<app-name>-<workspace-id>.<region>.databricksapps.com` |
| **과금 모델** | 실행 중인 시간 기준, 프로비저닝된 용량에 따라 DBU 과금 |

### 활용 사례

- **인터랙티브 대시보드** — Streamlit/Dash로 실시간 데이터 시각화
- **RAG 챗봇** — Gradio로 검색 증강 생성 AI 챗 인터페이스
- **데이터 입력 폼** — 현업 사용자가 직접 데이터를 입력/수정
- **ML 모델 서빙 UI** — 모델 서빙 엔드포인트를 감싸는 웹 인터페이스
- **REST API** — FastAPI/Flask로 데이터 파이프라인 트리거 또는 조회 API 제공

---

## 핵심 개념

### 아키텍처

Databricks Apps는 **컨테이너화된 서버리스 서비스**로 실행됩니다.

- 전용 컴퓨트 리소스, 네트워크 분리, 저장/전송 암호화 적용
- 서버리스 컴퓨트와 동일한 격리 계층(isolation layer)에서 동작
- 컨트롤 플레인 서비스로서 데이터 플레인 서비스에 접근

### 서비스 프린시펄 (Service Principal)

- 앱 생성 시 **전용 서비스 프린시펄이 자동 생성**됨
- 앱의 영구적인 아이덴티티로 동작
- 다른 앱과 공유하거나 변경할 수 없음
- 앱 삭제 시 함께 삭제됨

### 앱 상태 (Lifecycle)

| 상태 | 설명 |
|------|------|
| `Running` | 정상 실행 중 |
| `Deploying` | 배포 진행 중 |
| `Stopped` | 중지됨 |
| `Crashed` | 오류로 비정상 종료 |

> **중요**: 인메모리 상태는 재시작 시 초기화됩니다. 영속적 데이터는 Unity Catalog 테이블, Volume, 또는 Lakebase를 사용하세요.

---

## 지원 프레임워크

### Python 프레임워크

| 프레임워크 | 용도 | 기본 실행 커맨드 |
|------------|------|-----------------|
| **Streamlit** | 데이터 대시보드, 데이터 입력 폼 | `streamlit run app.py` |
| **Dash** | 인터랙티브 분석 대시보드 | `python app.py` |
| **Gradio** | AI/ML 모델 데모, 챗봇 UI | `python app.py` |
| **Flask** | 커스텀 웹 앱, REST API | `gunicorn app:app` |
| **FastAPI** | 고성능 REST API | `uvicorn app:app` |

### Node.js 프레임워크

| 프레임워크 | 용도 |
|------------|------|
| **React** | SPA (Single Page Application) |
| **Angular** | 엔터프라이즈 웹 앱 |
| **Svelte** | 경량 웹 앱 |
| **Express** | 서버사이드 API |

> 기본 실행 커맨드: Python 앱은 `python <my-app.py>`, Node.js 앱은 `npm run start`

---

## 앱 생성하기 (UI 기반)

### 사전 준비

- Databricks 워크스페이스 접근 권한
- 앱에서 사용할 리소스(SQL Warehouse 등)에 대한 권한
- 로컬 개발 환경 (Python 또는 Node.js 설치)

### Step 1: 앱 생성

1. 워크스페이스 사이드바에서 **+ New** > **App** 클릭
2. 템플릿 선택 (예: `Streamlit`, `Gradio Hello world` 등) 또는 빈 앱 생성
3. 앱 이름 입력 (예: `my-dashboard-app`)
4. **Install** 클릭

앱이 자동으로 워크스페이스에 배포됩니다.

### Step 2: 배포 확인

배포 완료 후 **Overview** 페이지에서:

- 앱 URL 확인 (자동 생성)
- 실행 상태 확인
- 로그 확인

### Step 3: 소스 코드 다운로드

Overview 페이지의 **Sync the files** 섹션에서 제공하는 커맨드를 복사하여 실행합니다.

```bash
mkdir my-dashboard-app
cd my-dashboard-app
# Overview 페이지에서 제공하는 sync 커맨드 실행
```

다운로드되는 파일:

| 파일 | 역할 |
|------|------|
| `app.py` | 앱 기능 및 UI 구현 |
| `app.yaml` | 앱 설정 (런타임, 환경 변수, 리소스) |
| `requirements.txt` | Python 패키지 의존성 |

### Step 4: 로컬 개발 및 테스트

```bash
# 의존성 설치
pip install -r requirements.txt

# 로컬 실행
python app.py

# 또는 Databricks CLI로 로컬 실행 (디버그 모드)
databricks apps run-local --prepare-environment --debug
```

### Step 5: 재배포

Overview 페이지의 **Deploy to Databricks Apps** 커맨드를 복사하여 실행합니다.

```bash
# Overview 페이지에서 제공하는 deploy 커맨드 실행
databricks apps deploy <app-name> --source-code-path /path/to/local/app
```

---

## app.yaml 설정

`app.yaml`은 앱의 런타임, 환경 변수, 리소스를 정의하는 핵심 설정 파일입니다.

### 전체 구조

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

### command 필드

커스텀 실행 커맨드를 배열로 지정합니다. 셸 환경에서 실행되지 않으므로 파이프(`|`)나 리다이렉트(`>`)는 사용할 수 없습니다.

#### 프레임워크별 커맨드 예시

**Streamlit:**

```yaml
command: ['streamlit', 'run', 'app.py']
```

**Flask (Gunicorn):**

```yaml
command:
  - gunicorn
  - app:app
  - -w
  - '4'
```

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

**Gradio:**

```yaml
command: ['python', 'app.py']
```

**Dash:**

```yaml
command: ['python', 'app.py']
```

> **참고**: `DATABRICKS_APP_PORT` 환경 변수는 런타임에 실제 포트 번호로 자동 치환됩니다.

### env 필드

환경 변수를 정의합니다. 두 가지 방식이 있습니다:

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

> **보안 주의**: 시크릿이나 민감 정보는 절대 `value`에 직접 넣지 마세요. 반드시 `valueFrom`을 사용하여 리소스로 관리하세요.

---

## 컴퓨트 사이즈

앱의 CPU 및 메모리를 선택할 수 있습니다.

| 사이즈 | CPU | 메모리 | 비용 | 용도 |
|--------|-----|--------|------|------|
| **Medium** (기본값) | 최대 2 vCPU | 6 GB | 0.5 DBU/시간 | 대시보드, 간단한 시각화, 폼 |
| **Large** | 최대 4 vCPU | 12 GB | 1 DBU/시간 | 대용량 데이터 처리, 고동시성, 연산 집약적 작업 |

> **권장**: 대부분의 앱은 Medium으로 충분합니다. 성능 이슈가 발생하거나 리소스 요구가 높은 경우에만 Large로 업그레이드하세요.

---

## 인증 (Authentication & Authorization)

Databricks Apps는 OAuth 2.0 기반으로 두 가지 인증 모델을 제공합니다.

### 1. 앱 인증 (App Authorization)

앱의 **서비스 프린시펄** 아이덴티티로 Databricks 리소스에 접근합니다.

#### 특징

- 앱 생성 시 자동으로 서비스 프린시펄이 생성됨
- `DATABRICKS_CLIENT_ID`와 `DATABRICKS_CLIENT_SECRET`가 자동 주입됨
- 모든 사용자가 동일한 권한으로 접근 (사용자별 접근 제어 불가)
- 배포 간에 아이덴티티가 유지됨

#### 사용 시나리오

- 백그라운드 작업 실행
- 공유 설정/메타데이터 관리
- 로깅 및 사용 메트릭
- 외부 서비스 호출

#### 코드 예시 (Python)

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

#### 코드 예시 (JavaScript)

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

### 2. 사용자 인증 (User Authorization)

현재 로그인한 **사용자의 아이덴티티와 권한**으로 리소스에 접근합니다.

> **상태**: Public Preview. 워크스페이스 관리자가 기능을 활성화해야 합니다.

#### 특징

- 사용자별 접근 제어 가능 (Unity Catalog 정책 자동 적용)
- Row-level 필터, Column 마스킹이 자동으로 적용됨
- 스코프(scope) 기반으로 접근 범위 제한
- HTTP 헤더 `x-forwarded-access-token`으로 사용자 토큰 전달

#### 주요 스코프

| 스코프 | 설명 |
|--------|------|
| `sql` | SQL 웨어하우스 쿼리 |
| `dashboards.genie` | Genie 스페이스 관리 |
| `files.files` | 파일/디렉토리 관리 |
| `iam.access-control:read` | 접근 제어 읽기 (기본) |
| `iam.current-user:read` | 현재 사용자 정보 읽기 (기본) |

#### 사용 시나리오

- 사용자별 데이터 접근이 필요한 경우
- Unity Catalog 정책(RLS, Column Masking) 적용이 필요한 경우
- 사용자별 권한에 따른 차등 기능 제공

#### 프레임워크별 사용자 토큰 가져오기

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

#### 코드 예시: 사용자 인증으로 쿼리 실행

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

### 비교: 어떤 인증을 사용해야 할까?

| 모델 | 사용 시점 | 예시 |
|------|-----------|------|
| **앱 인증** | 사용자 아이덴티티와 무관한 작업 | 로그 기록, 공유 설정 접근, 외부 서비스 호출 |
| **사용자 인증** | 현재 사용자 컨텍스트가 필요한 경우 | Unity Catalog 쿼리, 컴퓨트 실행, RLS 적용 |
| **둘 다 병행** | 혼합 작업 | 앱 인증으로 로깅 + 사용자 인증으로 필터된 데이터 조회 |

---

## 리소스 (Resources)

리소스는 앱이 Databricks 플랫폼 기능에 접근하기 위한 선언적 의존성입니다. 하드코딩 대신 리소스를 사용하면 **자격 증명 자동 관리, 환경 간 이식성, 보안 접근**이 보장됩니다.

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
2. **App resources** 섹션에서 **+ Add resource** 클릭
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

> **최소 권한 원칙**: 앱에 필요한 최소한의 권한만 부여하세요. 예를 들어, 쿼리만 실행한다면 SQL Warehouse에 `CAN USE`만 부여합니다.

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

> **중요**: `app.yaml` 외부에서 정의한 환경 변수는 앱에서 사용할 수 없습니다. 유일한 예외는 `DATABRICKS_APP_PORT`입니다.

---

## 배포 워크플로우

### 전체 흐름

```
[로컬 개발] → [로컬 테스트] → [워크스페이스 배포] → [설정/리소스 연결] → [운영]
```

### 1. 로컬 개발

선호하는 IDE(VS Code, PyCharm, IntelliJ 등)에서 개발합니다. Databricks VS Code Extension 사용을 권장합니다.

```bash
# 프로젝트 구조
my-app/
├── app.py              # 앱 코드
├── app.yaml            # 앱 설정
├── requirements.txt    # Python 의존성
└── static/             # 정적 파일 (선택)
```

### 2. 로컬 테스트

```bash
# Databricks CLI 로컬 실행
databricks apps run-local --prepare-environment --debug
```

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

### 3. 워크스페이스 배포

```bash
# Databricks CLI를 통한 배포
databricks apps deploy <app-name> --source-code-path /path/to/local/app
```

### 4. 환경 간 이동

리소스를 하드코딩하지 않고 `app.yaml`의 `valueFrom`을 사용하면, 코드 수정 없이 다른 워크스페이스로 앱을 이동할 수 있습니다.

### 의존성 관리

| 언어 | 파일 |
|------|------|
| Python (pip) | `requirements.txt` |
| Python (uv) | `pyproject.toml` |
| Node.js | `package.json` |

> **파일 크기 제한**: 앱 파일은 개별 10 MB를 초과할 수 없습니다. 초과 시 배포가 실패합니다.

---

## 예제: Streamlit 앱으로 테이블 조회

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

## 예제: FastAPI REST 엔드포인트

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

---

## 제한 사항 및 베스트 프랙티스

### 제한 사항

| 항목 | 제한 |
|------|------|
| **파일 크기** | 개별 파일 최대 10 MB (초과 시 배포 실패) |
| **워크스페이스당 앱 수** | 워크스페이스 쿼터에 따름 |
| **컴퓨트 사이즈** | Medium (2 vCPU/6 GB) 또는 Large (4 vCPU/12 GB)만 선택 가능 |
| **앱 URL** | 생성 후 변경 불가 |
| **인메모리 상태** | 재시작 시 초기화됨 |
| **셸 기능** | `command`에서 파이프, 리다이렉트 등 셸 기능 사용 불가 |
| **Free Edition** | 추가 제한 사항 적용 |
| **사용자 인증** | Public Preview 상태 |

### 보안 베스트 프랙티스

1. **PAT 하드코딩 금지** — 절대로 개인 액세스 토큰을 코드에 직접 넣지 마세요. 자동 주입되는 서비스 프린시펄 인증을 사용하세요.
2. **최소 권한 원칙** — 앱에 필요한 최소한의 권한만 부여하세요.
3. **시크릿은 리소스로 관리** — `valueFrom`을 사용하여 런타임에 안전하게 주입하세요.
4. **앱 간 자격 증명 공유 금지** — 각 앱은 독립적인 서비스 프린시펄을 사용합니다.

### 사용자 인증 보안 베스트 프랙티스

1. 앱 코드를 **소유자/신뢰할 수 있는 사용자만 접근 가능한 폴더**에 저장
2. `CAN MANAGE` 권한은 **신뢰할 수 있는 시니어 개발자**에게만 부여
3. `CAN USE` 권한은 **승인된 사용자/그룹**에게만 부여
4. **토큰을 절대 출력, 로깅, 파일에 기록하지 않기**
5. 최소 필요 스코프만 요청
6. 코드 리뷰 시 스코프와 권한 정합성 검증
7. 프로덕션 배포 전 **피어 리뷰** 필수
8. 사용자 액션에 대한 **구조화된 감사 로그** 기록

### 개발 베스트 프랙티스

1. **로컬 테스트 먼저** — `databricks apps run-local`로 배포 전 검증
2. **리소스 하드코딩 금지** — `valueFrom`을 사용하여 환경 간 이식성 확보
3. **상태는 외부 저장소에** — Unity Catalog, Volume, Lakebase 사용
4. **의존성 버전 명시** — `requirements.txt`에 버전을 명시하여 재현 가능한 빌드
5. **에러 핸들링** — 연결 실패, 권한 오류 등에 대한 적절한 에러 처리
6. **Medium 사이즈로 시작** — 성능 이슈가 확인될 때만 Large로 업그레이드

---

## 참고 자료

- [Databricks Apps 공식 문서](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)
- [앱 개발 가이드](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development)
- [인증 설정](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/auth)
- [리소스 설정](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/resources)
- [Streamlit 튜토리얼](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/tutorial-streamlit)
- [앱 런타임 설정 (app.yaml)](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-runtime)
- [컴퓨트 사이즈](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/compute-size)
- [환경 변수](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/environment-variables)
