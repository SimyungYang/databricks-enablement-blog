# app.yaml 설정

`app.yaml`은 앱의 런타임, 환경 변수, 리소스를 정의하는 핵심 설정 파일입니다.

---

## 전체 구조

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

---

## command 필드

커스텀 실행 커맨드를 배열로 지정합니다. 셸 환경에서 실행되지 않으므로 파이프(`|`)나 리다이렉트(`>`)는 사용할 수 없습니다.

### 프레임워크별 커맨드 예시

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

{% hint style="info" %}
`DATABRICKS_APP_PORT` 환경 변수는 런타임에 실제 포트 번호로 자동 치환됩니다.
{% endhint %}

---

## env 필드

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

{% hint style="warning" %}
시크릿이나 민감 정보는 절대 `value`에 직접 넣지 마세요. 반드시 `valueFrom`을 사용하여 리소스로 관리하세요.
{% endhint %}

---

## 컴퓨트 사이즈

앱의 CPU 및 메모리를 선택할 수 있습니다.

| 사이즈 | CPU | 메모리 | 비용 | 용도 |
|--------|-----|--------|------|------|
| **Medium**(기본값) | 최대 2 vCPU | 6 GB | 0.5 DBU/시간 | 대시보드, 간단한 시각화, 폼 |
| **Large**| 최대 4 vCPU | 12 GB | 1 DBU/시간 | 대용량 데이터 처리, 고동시성, 연산 집약적 작업 |

{% hint style="tip" %}
대부분의 앱은 Medium으로 충분합니다. 성능 이슈가 발생하거나 리소스 요구가 높은 경우에만 Large로 업그레이드하세요.
{% endhint %}
