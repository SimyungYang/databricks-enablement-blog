# Databricks Apps & 종합 가이드

Databricks Apps를 활용한 프로덕션 배포, 단계별 기술 스택 선택 가이드, 종합 비교 테이블, 고객 FAQ, 연습문제를 다룹니다.

---

## Databricks Apps -- 프로덕션 배포의 정답

### 왜 Databricks Apps인가?

Agent 앱을 프로덕션에 배포할 때 가장 큰 장벽은 기술 자체가 아니라 **인프라 운영**입니다.

| 직접 배포 시 해야 할 것 | Databricks Apps가 해결하는 것 |
|------------------------|-----------------------------|
| 서버 프로비저닝 (EC2, VM) | 서버리스 컨테이너 자동 실행 |
| SSL 인증서 발급/갱신 | HTTPS 자동 적용 |
| 인증/인가 시스템 구현 | OAuth 기반 Databricks 사용자 인증 자동 통합 |
| SQL Warehouse 연결 설정 | `DATABRICKS_WAREHOUSE_ID` 환경 변수로 자동 연결 |
| Model Serving 엔드포인트 연결 | 서비스 프린시펄을 통한 직접 접근 |
| 네트워크 보안 (VPN, 방화벽) | Databricks 네트워크 내 격리 실행 |
| Unity Catalog 권한 관리 | 서비스 프린시펄에 UC 권한 부여로 해결 |
| CI/CD 파이프라인 구성 | `databricks apps deploy` 명령어로 즉시 배포 |

### 지원 프레임워크

| 프레임워크 | 지원 여부 | 권장 사용 사례 |
|-----------|----------|---------------|
| **Streamlit**| 공식 지원 | 채팅 UI + 대시보드, 가장 많은 예제 |
| **Dash**| 공식 지원 | 차트 중심 모니터링 대시보드 |
| **Gradio**| 공식 지원 | ML 모델 데모, 멀티모달 앱 |
| **Flask**| 공식 지원 | 경량 웹 서버, API + 간단한 UI |
| **FastAPI**| 공식 지원 | API 서버, SSE/WebSocket |
| **Chainlit**| 미지원 | (FastAPI 래핑으로 우회 가능하나 비권장) |

### app.yaml 설정 예시

**Streamlit Agent 앱 (가장 일반적):**

```yaml
command:
  - "streamlit"
  - "run"
  - "app.py"
  - "--server.port"
  - "8000"
  - "--server.address"
  - "0.0.0.0"

env:
  - name: "DATABRICKS_WAREHOUSE_ID"
    valueFrom: "warehouse-id"
  - name: "SERVING_ENDPOINT"
    value: "mlops-agent-endpoint"

resources:
  - name: "warehouse-id"
    type: "sql_warehouse"
    sql_warehouse:
      id: "abc123def456"
      permission: "CAN_USE"
  - name: "serving-endpoint"
    type: "serving_endpoint"
    serving_endpoint:
      name: "mlops-agent-endpoint"
      permission: "CAN_QUERY"
```

**FastAPI API 서버:**

```yaml
command:
  - "uvicorn"
  - "main:app"
  - "--host"
  - "0.0.0.0"
  - "--port"
  - "8000"

env:
  - name: "DATABRICKS_WAREHOUSE_ID"
    valueFrom: "warehouse-id"

resources:
  - name: "warehouse-id"
    type: "sql_warehouse"
    sql_warehouse:
      id: "abc123def456"
      permission: "CAN_USE"
```

### 배포 워크플로

```bash
# 1. 앱 생성 (최초 1회)
databricks apps create \
  --name mlops-agent-app \
  --description "MLOps 모니터링 및 Agent 채팅"

# 2. 앱 배포 (코드 변경 시마다)
databricks apps deploy mlops-agent-app \
  --source-code-path ./app

# 3. 배포 상태 확인
databricks apps get mlops-agent-app

# 4. 로그 확인
databricks apps get-logs mlops-agent-app
```

### PoC Streamlit → Databricks Apps 마이그레이션

로컬에서 `streamlit run app.py`로 개발한 앱을 Databricks Apps로 마이그레이션하는 단계:

**Step 1: 인증 방식 변경**

```python
# Before (로컬 개발)
from databricks.sdk import WorkspaceClient
w = WorkspaceClient(
    host="https://xxx.cloud.databricks.com",
    token="dapi..."  # PAT 하드코딩
)

# After (Databricks Apps)
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()  # 서비스 프린시펄 자동 인증
```

**Step 2: 환경 변수 사용**

```python
import os

# 하드코딩 제거, 환경 변수 사용
warehouse_id = os.environ.get("DATABRICKS_WAREHOUSE_ID")
endpoint_name = os.environ.get("SERVING_ENDPOINT", "default-agent")
```

**Step 3: requirements.txt 정리**

```
streamlit>=1.38.0
databricks-sdk>=0.30.0
plotly>=5.0.0
```

**Step 4: app.yaml 작성 및 배포**

{% hint style="success" %}
**마이그레이션 핵심 원칙**: (1) PAT/토큰 하드코딩 → 서비스 프린시펄 자동 인증, (2) 호스트/엔드포인트 하드코딩 → 환경 변수, (3) `requirements.txt`에 모든 의존성 명시. 이 세 가지만 지키면 대부분의 로컬 Streamlit 앱은 Databricks Apps로 바로 배포 가능합니다.
{% endhint %}

---

## 단계별 기술 스택 선택 가이드

Agent 프로젝트는 PoC → 파일럿 → 프로덕션의 단계를 거칩니다. 각 단계마다 최적의 기술 스택이 다릅니다.

### PoC (1~2주): "동작하는 데모"

| 항목 | 선택 | 이유 |
|------|------|------|
| **프론트엔드**| Streamlit 또는 Chainlit | 최소 코드로 채팅 UI 구현 (Streamlit: 30분, Chainlit: Agent 추론 과정 시각화) |
| **백엔드**| Agent 직접 호출 (인프로세스) | API 서버 없이 앱 내에서 직접 LLM/Tool 호출 |
| **배포**| 로컬 (`streamlit run`) 또는 노트북 | 배포 인프라 불필요, 로컬에서 데모 |
| **인증**| PAT (Personal Access Token) | 개인 토큰으로 빠른 설정 |
| **데이터**| 하드코딩 또는 직접 SQL | 유연하고 빠른 반복 개발 |

```
┌──────────────┐
│  Streamlit   │─── Agent 직접 호출 ──→ Databricks
│  (로컬 실행)  │      (인프로세스)       (Model Serving)
└──────────────┘
```

### 파일럿 (1~2개월): "팀 내부 사용"

| 항목 | 선택 | 이유 |
|------|------|------|
| **프론트엔드**| Streamlit + Databricks Apps | 팀원들이 URL로 접근 가능, OAuth 자동 인증 |
| **백엔드**| Model Serving 엔드포인트 | Agent를 엔드포인트로 배포, 안정적 API 제공 |
| **배포**| Databricks Apps | 서버리스 호스팅, SSL, 인증 자동화 |
| **인증**| 서비스 프린시펄 (자동) | PAT 노출 위험 제거 |
| **데이터**| SQL Warehouse + Unity Catalog | 거버넌스 적용, 접근 제어 |

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Streamlit   │─────→│Model Serving │─────→│ Unity Catalog│
│  (Dbx Apps)  │ HTTP │  (Agent EP)  │      │ SQL Warehouse│
└──────────────┘      └──────────────┘      └──────────────┘
```

### 프로덕션 (지속 운영): "전사 사용"

**옵션 A: Streamlit/Dash + Databricks Apps**(사용자 수 < 100명)

| 항목 | 선택 | 이유 |
|------|------|------|
| **프론트엔드**| Streamlit 또는 Dash | 유지보수 용이, Python 단일 스택 |
| **백엔드**| Model Serving + Agent Framework | 안정적 엔드포인트, A/B 테스팅 가능 |
| **배포**| Databricks Apps + CI/CD | GitHub Actions 또는 Azure DevOps 연동 |
| **모니터링**| Inference Table + Lakehouse Monitoring | 요청/응답 로깅, 품질 모니터링 |

**옵션 B: React/Next.js + FastAPI**(사용자 수 100명+ 또는 커스텀 UX 필수)

| 항목 | 선택 | 이유 |
|------|------|------|
| **프론트엔드**| React/Next.js | 커스텀 디자인, 기업 포털 통합, 모바일 대응 |
| **백엔드**| FastAPI (Databricks Apps) | API 서버로 Agent 기능 노출 |
| **배포**| Databricks Apps (백엔드) + CDN/Vercel (프론트) | 프론트/백 독립 배포 |
| **모니터링**| Inference Table + 외부 APM (Datadog 등) | 엔드투엔드 모니터링 |

{% hint style="warning" %}
**프로덕션 전환 시 반드시 확인할 것**:
1. **인증**: PAT → 서비스 프린시펄 전환 완료 여부
2. **시크릿 관리**: 환경 변수 또는 Databricks Secret Scope 사용 여부
3. **에러 핸들링**: Agent 호출 실패 시 사용자에게 적절한 메시지 표시 여부
4. **Rate Limiting**: Model Serving 엔드포인트의 동시 요청 제한 설정 여부
5. **로깅**: 모든 요청/응답이 Inference Table에 기록되는지 확인
{% endhint %}

---

## 종합 비교 테이블

### 기능별 비교

| 항목 | Streamlit | Gradio | Chainlit | Dash | FastAPI |
|------|-----------|--------|----------|------|---------|
| **주요 용도**| 대시보드 + 채팅 | ML 데모 | Agent 채팅 | 대시보드 | API 서버 |
| **개발 속도**| 매우 빠름 | 빠름 | 빠름 | 보통 | 보통 |
| **채팅 UI**| 좋음 | 좋음 | 최고 | 어려움 | 직접 구현 |
| **대시보드**| 좋음 | 제한적 | 없음 | 최고 | 직접 구현 |
| **프로덕션 적합성**| 보통 | 제한적 | 제한적 | 좋음 | 최고 |
| **Databricks Apps**| 지원 | 지원 | 미지원 | 지원 | 지원 |
| **멀티유저 지원**| 제한적 | 제한적 | 제한적 | 좋음 | 최고 |
| **커스텀 디자인**| 제한적 | 제한적 | 보통 | 좋음 | 완전 자유 |
| **스트리밍**| `write_stream` | 내장 | 내장 | 어려움 | SSE/WS |
| **Agent 추론 시각화**| 직접 구현 | 제한적 | 내장 (최고) | 직접 구현 | 직접 구현 |

### 의사결정 흐름도

```
Agent UI 기술 선택
│
├─ "2주 안에 데모를 보여줘야 한다"
│   └─→ Streamlit (채팅+대시보드) 또는 Chainlit (Agent 추론 시각화)
│
├─ "Hugging Face 모델을 데모하고 싶다"
│   └─→ Gradio
│
├─ "차트 중심 모니터링 대시보드를 만든다"
│   └─→ Dash
│
├─ "기존 웹 포털에 Agent를 통합해야 한다"
│   └─→ FastAPI (백엔드) + 기존 프론트엔드
│
├─ "Databricks Apps에 배포해야 한다"
│   ├─ 채팅 UI 중심 → Streamlit
│   ├─ 대시보드 중심 → Dash
│   └─ API 서버 → FastAPI
│
└─ "사용자 100명+, 커스텀 UX 필수"
    └─→ FastAPI + React/Next.js
```

### 비용 관점 비교

| 항목 | Streamlit | Gradio | Chainlit | Dash | FastAPI + React |
|------|-----------|--------|----------|------|-----------------|
| **개발 인력**| Python 1명 | Python 1명 | Python 1명 | Python 1명 | Python + Frontend 2명 |
| **초기 개발 기간**| 1~2주 | 1~2주 | 1~2주 | 2~4주 | 4~8주 |
| **유지보수 난이도**| 낮음 | 낮음 | 보통 | 보통 | 높음 |
| **인프라 비용**| Databricks Apps DBU | Databricks Apps DBU | 별도 서버 | Databricks Apps DBU | Databricks Apps + CDN |

---

## 고객이 자주 묻는 질문

### Q1: "Streamlit으로 프로덕션 가능한가요?"

**단독 배포는 비권장. Databricks Apps 위에서는 가능합니다.**

Streamlit을 EC2나 VM에 직접 배포하면 SSL, 인증, 스케일링을 모두 직접 관리해야 합니다. 또한 WebSocket 기반 아키텍처로 인해 동시접속 50명 이상 시 성능 문제가 발생할 수 있습니다.

그러나 Databricks Apps 위에서 실행하면 이야기가 달라집니다. SSL 자동 적용, OAuth 인증 통합, 서버리스 스케일링이 모두 Databricks가 처리하므로, 팀 단위(10~50명) 사용에는 충분합니다.

**결론**: 사용자 수 50명 이하 + Databricks Apps 배포 → Streamlit으로 프로덕션 가능. 50명 이상이거나 커스텀 UX가 필수라면 FastAPI + React 검토.

### Q2: "React로 만들어야 하나요?"

**대부분의 경우, 아닙니다.**

React를 도입하면 프론트엔드 전문 인력, 빌드 파이프라인, 별도 호스팅이 추가로 필요합니다. Agent 프로젝트의 핵심 가치는 UI가 아니라 Agent의 기능입니다.

| 상황 | 권장 |
|------|------|
| PoC/파일럿, 팀 내부 사용 | Streamlit으로 충분 |
| 사용자 100명+, 전사 서비스 | React + FastAPI 검토 |
| 기존 웹 포털에 Agent 내장 | FastAPI API + iframe 또는 웹 컴포넌트 |
| 모바일 앱에 Agent 통합 | FastAPI API 필수 (Streamlit 불가) |
| 기업 브랜딩/디자인 시스템 적용 | React + FastAPI |

### Q3: "가장 빨리 데모를 만들 수 있는 방법은?"

**Streamlit + Databricks Agent Framework. 2시간이면 채팅 UI 완성 가능합니다.**

```python
# 이 코드만으로 Agent 채팅 앱 완성 (약 20줄)
import streamlit as st
from databricks.sdk import WorkspaceClient

st.title("My Agent")
w = WorkspaceClient()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("질문하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = w.serving_endpoints.query(
        name="my-agent-endpoint",
        messages=st.session_state.messages
    )
    result = response.choices[0].message.content

    with st.chat_message("assistant"):
        st.markdown(result)
    st.session_state.messages.append({"role": "assistant", "content": result})
```

### Q4: "Databricks Apps 비용은?"

Databricks Apps는 **서버리스 컴퓨팅 기반**으로 과금됩니다.

| 항목 | 설명 |
|------|------|
| **과금 기준**| 앱이 실행 중인 시간 + 프로비저닝된 리소스(CPU, 메모리) 기준 DBU |
| **유휴 시 비용**| 앱이 STOPPED 상태이면 과금 없음 |
| **자동 중지**| 설정한 비활성 시간 이후 자동 중지 가능 |
| **추가 비용**| SQL Warehouse 사용 시 별도 DBU, Model Serving 사용 시 별도 DBU |

{% hint style="info" %}
**비용 최적화 팁**: PoC/파일럿 단계에서는 앱 자동 중지(idle timeout)를 짧게 설정(예: 30분)하여 비용을 절감하세요. 프로덕션에서는 always-on으로 설정하되, 사용 패턴에 따라 비활성 시간대에 수동 중지를 고려하세요.
{% endhint %}

### Q5: "Chainlit을 Databricks에서 쓸 수 있나요?"

Databricks Apps에서 Chainlit을 직접 호스팅하는 것은 현재 지원되지 않습니다. 대안으로 두 가지 방법이 있습니다.

1. **PoC 단계에서만 로컬 사용**: 개발 머신에서 `chainlit run app.py`로 실행하고 데모
2. **FastAPI 래핑**: Chainlit을 FastAPI 앱 내에 마운트하여 Databricks Apps에 배포 (공식 지원이 아니므로 안정성 보장 어려움)

Agent 추론 과정 시각화가 중요하다면, Streamlit에서 `st.expander`를 활용하여 유사한 UX를 구현하는 것을 권장합니다.

---

## 연습 문제

### 문제 1: 기술 스택 선택

> 제조업 고객이 설비 예지보전 Agent를 만들고 싶어합니다. 현재 상황:
> - PoC 2주 후 경영진 데모 예정
> - 데이터 엔지니어 2명 (Python 가능, 프론트엔드 경험 없음)
> - 이후 현장 작업자 30명이 사용할 예정
> - Databricks 환경 구축 완료
>
> PoC와 프로덕션 각 단계에서 어떤 기술 스택을 추천하시겠습니까? 이유를 포함하여 설명하세요.

{% hint style="info" %}
**모범 답안 방향**: PoC는 Streamlit(빠른 개발, Python만으로 완결), 프로덕션은 Streamlit + Databricks Apps(현장 작업자 30명은 Streamlit으로 충분, 별도 프론트 개발 인력 없음, OAuth로 인증 해결).
{% endhint %}

### 문제 2: 아키텍처 설계

> 금융 고객이 다음 요구사항을 가진 Agent 앱을 설계해야 합니다:
> - 채팅으로 포트폴리오 분석 질문 가능
> - 실시간 차트 대시보드 (주가 추이, 포트폴리오 구성 등)
> - 사용자 200명+, 기업 포털에 통합 필요
> - 규제 준수를 위해 모든 대화 로깅 필수
>
> 적절한 아키텍처(프론트엔드, 백엔드, 배포, 모니터링)를 설계하고 그 이유를 설명하세요.

{% hint style="info" %}
**모범 답안 방향**: FastAPI(백엔드, Databricks Apps) + React(프론트엔드, 기업 포털 통합). 사용자 200명+ 및 포털 통합 → Streamlit 한계 초과. Inference Table로 대화 로깅, Lakehouse Monitoring으로 품질 관리. Dash가 아닌 React를 선택하는 이유: 기업 포털 통합에는 기존 디자인 시스템과의 호환이 필수이므로.
{% endhint %}

### 문제 3: 마이그레이션 계획

> 팀에서 로컬 Streamlit 앱(PAT 인증, 하드코딩된 엔드포인트)을 Databricks Apps로 마이그레이션하려고 합니다. 다음 코드를 Databricks Apps에 배포 가능한 형태로 수정하세요.

```python
import streamlit as st
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(
    host="https://my-workspace.cloud.databricks.com",
    token="dapi1234567890abcdef"
)

response = w.serving_endpoints.query(
    name="my-agent",
    messages=[{"role": "user", "content": "안녕"}]
)
st.write(response.choices[0].message.content)
```

{% hint style="info" %}
**모범 답안 방향**: (1) `WorkspaceClient()` 인자 제거 (서비스 프린시펄 자동 인증), (2) 엔드포인트 이름을 환경 변수로 변경, (3) `app.yaml`에 `serving_endpoint` 리소스 정의, (4) `requirements.txt` 작성.
{% endhint %}

### 문제 4: 트레이드오프 분석

> 다음 세 가지 시나리오에서 각각 Streamlit, Gradio, FastAPI 중 어떤 기술이 가장 적합한지 선택하고, 나머지 두 기술이 부적합한 이유를 설명하세요.
>
> (A) Hugging Face의 오픈소스 LLM을 미세조정한 모델을 팀 외부 이해관계자에게 빠르게 데모
> (B) 고객사의 기존 React 포털에 Agent 채팅 기능을 추가
> (C) 데이터 분석가가 내부적으로 사용할 Agent + 차트 대시보드

{% hint style="info" %}
**모범 답안 방향**: (A) Gradio -- `share=True`로 즉시 공유, HF Spaces 배포 가능. Streamlit은 배포 필요, FastAPI는 UI 없음. (B) FastAPI -- React 포털이 이미 있으므로 API만 제공하면 됨. Streamlit/Gradio는 별도 페이지로만 존재. (C) Streamlit -- 대시보드+채팅 모두 지원, Python만으로 완결. Gradio는 대시보드 약함, FastAPI는 UI 별도 구현 필요.
{% endhint %}

---

## 참고 자료

### 공식 문서

| 리소스 | URL |
|--------|-----|
| Streamlit 공식 문서 | [docs.streamlit.io](https://docs.streamlit.io/) |
| Gradio 공식 문서 | [gradio.app/docs](https://www.gradio.app/docs/) |
| Chainlit 공식 문서 | [docs.chainlit.io](https://docs.chainlit.io/) |
| Dash 공식 문서 | [dash.plotly.com](https://dash.plotly.com/) |
| FastAPI 공식 문서 | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| Databricks Apps 문서 | [docs.databricks.com/apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html) |

### Databricks 관련 자료

| 리소스 | 설명 |
|--------|------|
| [Databricks Apps 가이드](../../apps/README.md) | 이 블로그의 Databricks Apps 상세 가이드 |
| [Agent Bricks 가이드](../../agent-bricks/README.md) | Knowledge Assistant, Genie Agent, Supervisor Agent |
| [Builder App (AI Dev Kit)](../../builder-app/README.md) | Agent 개발 프레임워크 |
| [AI Agent 아키텍처](../agent-architecture.md) | ReAct, Tool Use, Multi-Agent 패턴 |

### 추천 학습 경로

1. **입문**: Streamlit 공식 튜토리얼 → 채팅 앱 만들기 (2시간)
2. **심화**: Databricks Apps에 Streamlit 배포 (1시간)
3. **응용**: FastAPI + SSE로 스트리밍 Agent API 구현 (4시간)
4. **프로덕션**: CI/CD 파이프라인 + 모니터링 구축 (1일)

---

[README로 돌아가기](README.md)
