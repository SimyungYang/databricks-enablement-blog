# Genie Code 사용 가이드

> **최종 업데이트**: 2026-03-27

Databricks Genie Code는 AI 기반 코딩 어시스턴트로, Notebook, SQL Editor, Dashboard, Lakeflow Pipeline 등에서 자연어로 코드를 생성하고 디버깅할 수 있습니다.

## Genie Code 사용법

### Genie Code 패널 열기

페이지 우측 상단의 **Sparkle 아이콘**을 클릭하면 Genie Code 패널이 열립니다.

### 두 가지 모드

Genie Code는 **Chat 모드**와 **Agent 모드**를 제공합니다:

| 모드 | 기능 | 적합한 상황 | 예시 프롬프트 |
|------|------|-------------|---------------|
| **Chat** | 질문 답변, 코드 생성/실행 | 코드 설명, 개념 학습, 간단한 코드 생성 | "이 함수는 뭘 하는 거야?", "Unity Catalog가 뭐야?", "이 함수의 단위 테스트 작성해줘" |
| **Agent** | 다단계 워크플로 자동화, 솔루션 계획, 자산 탐색, 코드 실행, 오류 자동 수정 | EDA, 노트북 정리, 대시보드 생성, 파이프라인 구축 | "`@example_table`에 대해 EDA 수행하고 인사이트 요약해줘", "이 데이터로 대시보드를 만들어줘", "매일 `@example_table`을 업데이트하는 파이프라인 만들어줘" |

{% hint style="warning" %}
Agent 모드는 일부 제품 영역에서만 사용 가능합니다. Notebooks, Dashboards, Lakeflow Pipelines Editor 등에서 지원됩니다.
{% endhint %}

### 주요 기능

#### 인라인 코드 제안 및 자동완성

코드를 작성하는 동안 Genie Code가 실시간으로 코드 제안을 제공합니다. Python과 SQL에서 지원됩니다.

#### Quick Fix

기본적인 코드 오류를 자동 감지하고 수정 제안을 표시합니다. **Accept and run**을 클릭하면 즉시 적용됩니다.

#### Diagnose Error

복잡한 오류(환경 오류 포함)를 분석하고 수정을 시도합니다.

#### Slash 명령어

자주 사용하는 프롬프트를 빠르게 입력할 수 있습니다:

| 명령어 | 기능 |
|--------|------|
| `/explain` | 선택한 코드 설명 |
| `/fix` | 코드 오류 수정 |
| `/optimize` | 코드 최적화 |
| `/test` | 단위 테스트 생성 |
| `/doc` | 문서/주석 생성 |

#### 자연어 데이터 필터링

데이터 테이블에서 자연어로 필터 조건을 지정할 수 있습니다.

#### 문서 기반 응답

Databricks 공식 문서를 검색하여 답변합니다. 응답에 **Searched documentation** 단계가 표시되며, 출처 링크를 요청할 수 있습니다.

### 패널 설정

| 설정 | 설명 |
|------|------|
| **Docked** | 하단에 고정 (드래그 앤 드롭으로 이동 가능) |
| **Side** | 우측에 고정 |
| **History** | 이전 대화 스레드 조회/삭제 |
| **Custom Instructions** | 사용자/워크스페이스 수준 커스텀 인스트럭션 설정 |

### 피드백

응답 하단에 마우스를 올리면 **Useful/Not useful** 버튼이 표시됩니다. 적극적인 피드백이 서비스 품질 향상에 기여합니다.

---

## Genie Code 활용 시나리오

### 시나리오 1: 데이터 사이언스 (Notebooks)

Genie Code는 전문 ML 엔지니어처럼 동작하여 전체 ML 워크플로를 자동화합니다.

**활용 예시:**

```
프롬프트: "@customers 테이블에 대해 고객 세그멘테이션 분석을 수행해줘.
         K-means 클러스터링을 사용하고 MLflow에 실험을 기록해줘."
```

Genie Code가 수행하는 작업:
1. 테이블 스키마 분석 및 EDA
2. 피처 엔지니어링
3. 최적 클러스터 수 결정 (Elbow method)
4. 모델 학습 및 MLflow 실험 로깅
5. 결과 시각화 및 인사이트 요약

### 시나리오 2: 데이터 엔지니어링 (Lakeflow Pipelines)

ETL 워크로드를 자동화하고 Lakeflow Spark Declarative Pipeline을 구축합니다.

**활용 예시:**

```
프롬프트: "raw_orders와 raw_customers 테이블을 조인하여
         daily_order_summary 테이블을 업데이트하는 파이프라인을 만들어줘."
```

### 시나리오 3: 분석 및 대시보드 (Dashboards)

데이터 자산을 탐색하고 프로덕션 수준 대시보드를 자동 생성합니다.

**활용 예시:**

```
프롬프트: "@sales_data를 분석하고 월별 매출 추이,
         지역별 성과, 상위 제품을 보여주는 대시보드를 만들어줘."
```

### 시나리오 4: GenAI 앱 디버깅 (MLflow)

GenAI 애플리케이션을 이해하고, 디버깅하며, 성능을 개선합니다.

**활용 예시:**

```
프롬프트: "이 RAG 체인의 evaluation 결과를 분석하고
         응답 품질이 낮은 케이스를 식별해줘."
```

---

## Genie Space vs Genie Code 비교

| 비교 항목 | Genie Space | Genie Code |
|-----------|-------------|------------|
| **대상 사용자** | 비즈니스 사용자, 비기술 인력 | 데이터 엔지니어, 사이언티스트, 분석가 |
| **주요 목적** | 자연어 데이터 질의 | AI 기반 코딩 지원 및 자동화 |
| **인터페이스** | 전용 채팅 공간 | 워크스페이스 전체에 내장된 패널 |
| **입력 방식** | 자연어 질문 | 자연어 + 코드 + Slash 명령어 |
| **출력** | SQL 결과 테이블, 시각화, 요약 | 코드, 노트북 셀, 대시보드, 파이프라인 |
| **설정** | 도메인 전문가가 테이블/인스트럭션 사전 구성 | 별도 설정 불필요 (Unity Catalog 자동 참조) |
| **거버넌스** | Space 단위 권한 관리 | 워크스페이스 및 Unity Catalog 권한 |
| **비용** | SQL Warehouse 컴퓨팅 | 노트북/쿼리/작업 컴퓨팅 |
| **Agent Mode** | 다단계 연구 분석, PDF 보고서 | 다단계 워크플로 자동화, 코드 생성/실행 |
| **적합한 사용 사례** | "지난 달 매출은 얼마야?" | "ETL 파이프라인을 만들어줘" |

### 언제 무엇을 사용할까?

**Genie Space를 사용하세요:**

* 비기술 사용자가 데이터에 접근해야 할 때
* 반복적인 비즈니스 질의를 셀프서비스로 제공할 때
* 도메인 특화된 데이터 질의 환경이 필요할 때
* SQL을 모르는 팀원도 데이터 분석을 해야 할 때

**Genie Code를 사용하세요:**

* 복잡한 데이터 파이프라인을 구축할 때
* ML 모델을 학습하고 배포할 때
* 대시보드를 생성하고 관리할 때
* 코드 디버깅과 최적화가 필요할 때
* GenAI 애플리케이션을 개발할 때

---

## 14. MCP(Model Context Protocol)와 Genie Code 연동

### 14.1 MCP 개요

#### MCP란 무엇인가?

MCP(Model Context Protocol)는 **Anthropic이 개발한 오픈소스 프로토콜**로, AI 에이전트가 외부 도구, 데이터 소스, 워크플로에 접근하기 위한 **표준 인터페이스**입니다. USB-C가 다양한 전자기기를 하나의 규격으로 연결하듯, MCP는 AI 애플리케이션과 외부 시스템을 하나의 표준으로 연결합니다.

#### 핵심 아키텍처

MCP는 **클라이언트-서버 아키텍처**를 따르며, 세 가지 핵심 참여자로 구성됩니다:

| 참여자 | 역할 | Databricks 예시 |
|--------|------|-----------------|
| **MCP Host** | AI 애플리케이션. 하나 이상의 MCP Client를 관리 | Genie Code, AI Playground |
| **MCP Client** | MCP Server와의 연결을 유지하고 컨텍스트를 획득 | Genie Code 내부 클라이언트 |
| **MCP Server** | 도구, 리소스, 프롬프트 등 컨텍스트를 제공하는 프로그램 | GitHub MCP, Unity Catalog Functions 등 |

#### MCP 서버가 제공하는 3가지 프리미티브

| 프리미티브 | 설명 | 예시 |
|-----------|------|------|
| **Tools** | AI가 호출할 수 있는 실행 가능한 함수 | 파일 검색, API 호출, DB 쿼리 |
| **Resources** | AI에 컨텍스트를 제공하는 데이터 소스 | 파일 내용, DB 레코드, API 응답 |
| **Prompts** | LLM과의 상호작용을 구조화하는 재사용 가능한 템플릿 | 시스템 프롬프트, Few-shot 예시 |

#### MCP 통신 방식

MCP는 **JSON-RPC 2.0** 기반의 데이터 계층과 두 가지 전송 메커니즘을 지원합니다:

| 전송 방식 | 설명 | 사용 환경 |
|----------|------|----------|
| **Stdio** | 표준 입출력 스트림을 통한 로컬 프로세스 통신 | 로컬 개발 환경 |
| **Streamable HTTP** | HTTP POST + Server-Sent Events | 원격 서버 통신 (Databricks 기본) |

{% hint style="info" %}
Databricks에서 외부 MCP 서버를 연결하려면 해당 서버가 **Streamable HTTP 전송 방식**을 지원해야 합니다.
{% endhint %}

---

### 14.2 Databricks에서 MCP 서버 설정

Databricks는 세 가지 유형의 MCP 서버를 지원합니다:

#### 유형 1: Managed MCP (관리형)

Databricks가 사전 구성한 즉시 사용 가능한 MCP 서버입니다. Unity Catalog 권한이 자동으로 적용됩니다.

| 서버 | 용도 | 엔드포인트 패턴 |
|------|------|----------------|
| **Unity Catalog Functions** | 사전 정의된 SQL 함수 실행 | `/api/2.0/mcp/functions/{catalog}/{schema}/{function}` |
| **Vector Search** | 벡터 검색 인덱스 쿼리 | `/api/2.0/mcp/vector-search/{catalog}/{schema}/{index}` |
| **Genie Space** | 자연어 데이터 분석 (읽기 전용) | `/api/2.0/mcp/genie/{genie_space_id}` |
| **Databricks SQL** | AI 생성 SQL 실행 (읽기/쓰기) | `/api/2.0/mcp/sql` |

#### 유형 2: External MCP (외부)

Unity Catalog Connection을 통해 외부 MCP 서버에 안전하게 연결합니다. 자격 증명이 직접 노출되지 않으며, 관리형 프록시를 통해 통신합니다.

**지원되는 연결 방법:**

| 방법 | 설명 |
|------|------|
| **Managed OAuth (권장)** | Databricks가 OAuth 흐름을 관리. GitHub, Glean, Google Drive, SharePoint 등 지원 |
| **Databricks Marketplace** | 마켓플레이스에서 사전 빌드된 통합 설치 |
| **Custom HTTP Connection** | Streamable HTTP를 지원하는 모든 MCP 서버에 커스텀 연결 생성 |
| **Dynamic Client Registration (실험적)** | RFC7591 지원 서버의 자동 OAuth 등록 |

외부 MCP 서버의 프록시 엔드포인트 형식:

```
https://<workspace-hostname>/api/2.0/mcp/external/{connection_name}
```

**인증 방식:**

* **공유 인증(Shared Principal)**: Bearer 토큰, OAuth M2M, 공유 OAuth U2M
* **사용자별 인증(Per-user)**: 리소스별 개별 사용자 자격 증명

#### 유형 3: Custom MCP (커스텀)

자체 MCP 서버를 **Databricks App**으로 호스팅합니다. Streamable HTTP 전송 방식을 구현해야 합니다.

**배포 절차:**

1. MCP 서버 코드 작성 (`pyproject.toml`, `app.yaml` 구성)
2. Databricks App 생성: `databricks apps create <app-name>`
3. 소스 코드 업로드 및 배포
4. MCP 엔드포인트: `https://<app-url>/mcp`

{% hint style="warning" %}
커스텀 MCP 앱은 **stateless 아키텍처**로 구현해야 하며, 동일 워크스페이스 내에 배포해야 합니다. CORS 이슈 방지를 위해 워크스페이스 URL을 허용 오리진에 추가하세요.
{% endhint %}

#### MCP 서버 확인 방법

워크스페이스에서 사용 가능한 MCP 서버를 확인하려면:

1. 워크스페이스의 **Agents** 섹션으로 이동합니다.
2. **MCP Servers** 탭을 선택합니다.
3. 등록된 서버 목록과 상태를 확인할 수 있습니다.

---

### 14.3 Genie Code에서 MCP 활용

#### MCP 서버를 Genie Code에 연결하기

{% hint style="warning" %}
MCP 서버는 **Genie Code Agent 모드에서만** 지원됩니다. Chat 모드에서는 사용할 수 없습니다.
{% endhint %}

**설정 단계:**

1. Genie Code 패널을 열고 **설정(⚙️) 아이콘**을 클릭합니다.
2. **MCP Servers** 섹션에서 **Add Server**를 선택합니다.
3. 사용할 서버 유형을 선택합니다:
   * Unity Catalog Functions
   * Vector Search Indexes
   * Genie Spaces
   * Unity Catalog Connections (외부 MCP)
   * Databricks Apps (커스텀 MCP)
4. **Save**를 클릭하면 즉시 사용 가능합니다.

#### 사용 방식

MCP 서버가 추가되면, Genie Code는 **자동으로** 관련 서버의 도구를 활용합니다. 프롬프트나 인스트럭션을 변경할 필요가 없습니다. Agent 모드에서 질문을 하면 Genie Code가 필요에 따라 적절한 MCP 서버의 도구를 호출합니다.

#### 활용 예시: GitHub MCP 서버

GitHub MCP 서버를 연결하면 Genie Code에서 엔터프라이즈 코드 검색이 가능합니다.

**설정 순서:**

1. **GitHub App 생성**: GitHub > Settings > Developer settings에서 앱 생성
   * Callback URL: `https://<databricks-workspace-url>/login/oauth/http.html`
2. **Unity Catalog Connection 생성**:
   * Auth type: OAuth User to Machine
   * Host: `https://api.githubcopilot.com`
   * OAuth scope: `mcp:access read:user user:email repo read:org`
   * Base path: `/mcp`
   * "Is mcp connection" 체크박스 활성화
3. **Genie Code에서 연결 추가**: Settings > MCP Servers > Add Server

**사용 가능한 도구:**

| 도구 | 기능 |
|------|------|
| `search_code` | 리포지토리에서 코드 패턴 검색 |
| `get_file_contents` | 리포지토리의 파일 내용 조회 |

**사용 예시:**

```
프롬프트: "우리 리포지토리에서 데이터 처리 파이프라인 관련 코드를 찾아줘"
프롬프트: "main 브랜치의 config.yaml 파일 내용을 보여줘"
```

{% hint style="tip" %}
특정 리포지토리를 대상으로 검색하려면 Genie Code 인스트럭션 파일에 `repo: repository_name, owner: username` 형식으로 지정할 수 있습니다.
{% endhint %}

#### 활용 예시: 기타 외부 서비스

| 서비스 | 활용 시나리오 |
|--------|-------------|
| **Glean** | 내부 문서 검색, 사전 사례 참조 |
| **Google Drive** | 팀 문서에서 필요한 정보 추출 |
| **SharePoint** | 조직 내부 문서 및 데이터 접근 |
| **Genie Space** | 자연어로 데이터 분석 (Agent 모드에서 MCP를 통해 호출) |
| **Vector Search** | RAG 패턴으로 관련 문서 검색 후 분석에 활용 |

#### 제한 사항

| 제한 | 상세 |
|------|------|
| **Agent 모드 전용** | MCP 서버는 Agent 모드에서만 사용 가능 |
| **도구 수 제한** | 전체 MCP 서버에 걸쳐 **최대 20개 도구**만 사용 가능 |
| **전송 방식** | 외부 MCP 서버는 Streamable HTTP만 지원 |
| **도구 이름 하드코딩 금지** | 도구 목록이 변경될 수 있으므로 동적 탐색 권장 |
| **출력 형식 비보장** | 도구 출력 형식이 안정적이지 않으므로 프로그래밍적 파싱 비권장 |

{% hint style="info" %}
MCP 서버가 제공하는 도구가 20개를 초과하는 경우, Genie Code 설정에서 특정 도구나 서버를 선택적으로 활성화/비활성화하여 20개 한도 내에서 관리할 수 있습니다.
{% endhint %}

---

### 14.4 MCP 비용 구조

MCP 서버 사용 시 각 리소스 유형에 따라 컴퓨팅 비용이 발생합니다:

| 리소스 | 비용 유형 |
|--------|----------|
| Unity Catalog Functions | Serverless General Compute |
| Genie Spaces | Serverless SQL Compute |
| Databricks SQL | SQL 전용 가격 |
| Vector Search Indexes | Vector Search 가격 |
| Custom MCP Servers | Databricks Apps 가격 |

{% hint style="info" %}
MCP 프로토콜 자체에 대한 추가 비용은 없습니다. 실제 도구를 실행할 때 사용되는 컴퓨팅 리소스에 대해서만 비용이 부과됩니다.
{% endhint %}

---

### 14.5 MCP 에이전트 개발 베스트 프랙티스

MCP를 활용한 에이전트를 개발할 때 다음 권장 사항을 따르세요:

1. **도구 이름 하드코딩 금지**: MCP 서버의 도구 목록은 변경될 수 있으므로, 에이전트가 런타임에 `tools/list`를 호출하여 **동적으로 도구를 탐색**하도록 구현합니다.
2. **출력 파싱 금지**: 도구 출력 형식은 안정적이지 않으므로, 결과 해석은 **LLM에 위임**합니다.
3. **LLM 기반 도구 선택**: 어떤 도구를 호출할지는 LLM이 사용자 요청에 따라 자동으로 결정하도록 합니다.

**프로그래밍 방식으로 MCP 서버 연결하기 (로컬 개발):**

```bash
# 1. OAuth 인증
databricks auth login --host https://<workspace-hostname>

# 2. 의존성 설치
pip install -U "mcp>=1.9" "databricks-sdk[openai]" "mlflow>=3.1.0" \
    "databricks-agents>=1.0.0" "databricks-mcp"
```

```python
# 3. DatabricksMCPClient를 사용한 연결
from databricks_mcp import DatabricksMCPClient

client = DatabricksMCPClient(
    server_url="https://<hostname>/api/2.0/mcp/functions/{catalog}/{schema}/{func}",
    databricks_cli_profile="DEFAULT"
)
```

---

## 참고 자료

* [Databricks Genie Space 공식 문서](https://docs.databricks.com/aws/en/genie/)
* [Genie Space 설정 가이드](https://docs.databricks.com/aws/en/genie/set-up)
* [Genie Space 베스트 프랙티스](https://docs.databricks.com/aws/en/genie/best-practices)
* [Genie Code 공식 문서](https://docs.databricks.com/aws/en/genie-code/)
* [Genie Code 사용법 (Azure)](https://learn.microsoft.com/en-us/azure/databricks/genie-code/use-genie-code)
* [Genie Agent Mode](https://docs.databricks.com/aws/en/genie/agent-mode)
