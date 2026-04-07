> **원문**: [Announcing managed MCP servers with Unity Catalog and Mosaic AI Integration](https://www.databricks.com/blog/announcing-managed-mcp-servers-unity-catalog-and-mosaic-ai-integration)

{% hint style="info" %}
**번역 참고**: 원래 요청된 URL(`/blog/announcing-databricks-mcp-server`)은 404로 접근이 불가합니다. 이 문서는 동일 주제의 공식 Databricks 블로그 포스트 **"Announcing managed MCP servers with Unity Catalog and Mosaic AI Integration"** (2025년 6월 18일)을 번역한 것입니다.
{% endhint %}

---

# Unity Catalog 및 Mosaic AI 통합으로 관리형 MCP 서버 발표

| 항목 | 내용 |
| --- | --- |
| **원문 제목** | Announcing managed MCP servers with Unity Catalog and Mosaic AI Integration |
| **저자** | Databricks 제품 팀 |
| **발행일** | 2025년 6월 18일 |
| **원문 URL** | https://www.databricks.com/blog/announcing-managed-mcp-servers-unity-catalog-and-mosaic-ai-integration |

---

## 개요

MCP(Model Context Protocol)는 최근 몇 달 사이 업계 전반에 걸쳐 큰 주목을 받고 있는 표준으로, LLM(대형 언어 모델)에 도구(tool)를 제공하는 방식을 정의합니다. 이는 중요한 진보입니다. LLM이 행동(action)을 취하기 위해 필요한 맥락(context)을 보다 자연스러운 형태로 공급할 수 있기 때문입니다.

Databricks는 MCP를 Unity Catalog 및 Mosaic AI의 강점과 결합하여, 세 가지 요소의 장점을 모두 제공합니다. **에이전트가 행동을 취할 수 있도록 하는 MCP**, **에이전트를 빌드하고 평가하기 위한 Mosaic AI**, 그리고 **거버넌스와 탐색(discovery)을 위한 Unity Catalog** 가 하나로 통합됩니다.

---

## 관리형 MCP 서버란 무엇인가

Databricks **관리형 MCP 서버(Managed MCP Servers)** 는 Unity Catalog에 저장된 데이터, Databricks Vector Search 인덱스, Genie 스페이스, 그리고 커스텀 함수에 AI 에이전트를 연결하는 즉시 사용 가능한(ready-to-use) 서버입니다.

Databricks가 제공하는 최초의 관리형 서버 집합은 다음과 같은 방식으로 Databricks의 데이터에 안전하게 접근할 수 있도록 합니다.

- **Genie** — 자연어를 통해 구조화된 데이터를 조회하는 Genie 스페이스
- **Vector Search** — 관련 문서를 찾기 위한 Vector Search 인덱스 쿼리
- **UC Functions** — Unity Catalog 함수를 통한 사전 정의된 SQL 쿼리 실행

이 관리형 MCP 서버들은 **엔터프라이즈급 보안** 을 염두에 두고 설계되었습니다. 서버는 자동으로 사용자의 권한을 준수하므로, Unity Catalog에서 모든 데이터를 계속 거버넌싱하면서 MCP를 활용할 수 있습니다. 거버넌스를 별도로 관리해야 하는 추가적인 장소가 필요하지 않습니다.

특히 주목할 점은 **온-비하프-오브-유저(on-behalf-of-user) 인증** 을 기본으로 지원한다는 것입니다. 관리형 MCP 서버는 이미 Unity Catalog에 구축된 거버넌스를 그대로 존중합니다.

---

## 사용 가능한 관리형 서버

Databricks가 즉시 사용할 수 있도록 제공하는 MCP 서버는 다음과 같습니다. 온-비하프-오브-유저 인증을 사용하여 관리형 MCP 서버에 연결할 때는, 애플리케이션이 접근해야 하는 각 서버에 대한 OAuth 스코프(scope)를 포함해야 합니다.

아래 표는 각 관리형 MCP 서버의 URL 패턴과 OAuth 스코프를 정리한 것입니다.

| MCP 서버 | URL 패턴 | OAuth 스코프 |
| --- | --- | --- |
| **Vector Search** — Databricks 관리형 임베딩을 사용하는 Vector Search 인덱스를 쿼리하여 관련 문서를 탐색 | `https://<workspace-hostname>/api/2.0/mcp/vector-search/{catalog}/{schema}/{index_name}` | `vector-search` |
| **Genie Space** — 자연어를 사용한 구조화 데이터 분석을 위해 Genie 스페이스를 쿼리. 읽기 전용. 장시간 실행 쿼리의 결과는 폴링(polling) 필요 | `https://<workspace-hostname>/api/2.0/mcp/genie/{genie_space_id}` | `genie` |
| **Databricks SQL** — Claude Code, Cursor, Codex 등 AI 코딩 도구를 활용한 데이터 파이프라인 작성을 위해 AI 생성 SQL 실행. 읽기/쓰기 지원. 장시간 실행 쿼리의 결과는 폴링 필요 | `https://<workspace-hostname>/api/2.0/mcp/sql` | `sql` |
| **Unity Catalog Functions** — UC 함수를 사용하여 사전 정의된 SQL 쿼리 실행 | `https://<workspace-hostname>/api/2.0/mcp/functions/{catalog}/{schema}/{function_name}` | `unity-catalog` |

Unity Catalog의 권한은 항상 적용되므로, 에이전트와 사용자는 자신이 허용된 도구와 데이터에만 접근할 수 있습니다.

---

## MCP 서버 유형

Databricks는 세 가지 범주의 MCP 서버를 제공합니다.

### 1. 관리형 MCP (Managed MCP)

사전 구성된 MCP 서버를 사용하여 Databricks 기능에 즉시 접근할 수 있습니다. 별도의 설정이나 코딩이 필요하지 않습니다.

### 2. 외부 MCP (External MCP)

관리형 연결(managed connections)을 통해 Databricks 외부에 호스팅된 MCP 서버에 안전하게 연결할 수 있습니다. Databricks Marketplace에서 큐레이팅된 외부 MCP 서버를 설치하거나, Unity Catalog HTTP 연결을 통해 커스텀 MCP 서버를 구성할 수 있습니다.

### 3. 커스텀 MCP (Custom MCP)

Databricks Apps를 사용하여 커스텀 MCP 서버를 직접 호스팅할 수 있습니다. Databricks Apps는 에이전트를 실제 서비스로 구현하는 데 필요한 **OAuth 기본 지원**, **Git 기반 배포**, **권한 및 거버넌스** 가 내장되어 있습니다. Databricks의 서버리스 인프라 위에서 동작하기 때문에, 에이전트의 사용량이 늘어나더라도 확장성에 대해 걱정할 필요가 없습니다.

---

## MCP 사용 방법

MCP는 동적으로 사용 가능한 도구를 탐색하고, 어떤 도구를 호출할지 결정하며, 출력을 해석하는 LLM과 함께 사용하도록 설계되었습니다. MCP 서버를 사용하는 에이전트를 구축할 때 Databricks가 권장하는 세 가지 원칙이 있습니다.

첫째, **도구 이름을 하드코딩하지 마십시오.** Databricks가 새로운 기능을 추가하거나 기존 기능을 수정함에 따라 사용 가능한 도구 집합이 변경될 수 있습니다. 에이전트는 런타임에 도구를 나열(list tools)함으로써 동적으로 탐색해야 합니다.

둘째, **도구 출력을 프로그래밍 방식으로 파싱하지 마십시오.** 도구 출력 형식은 안정성이 보장되지 않습니다. LLM이 도구 응답에서 정보를 해석하고 추출하도록 하십시오.

셋째, **LLM이 결정하도록 하십시오.** 에이전트의 LLM은 사용자의 요청과 MCP 서버가 제공하는 도구 설명을 기반으로 어떤 도구를 호출할지 결정해야 합니다.

이러한 방식을 따르면, 코드 변경 없이도 MCP 서버 개선 사항으로부터 에이전트가 자동으로 혜택을 받을 수 있습니다.

---

## AI Playground에서의 MCP 프로토타이핑

**AI Playground** 는 코드를 작성하기 전에 MCP를 활용한 에이전트를 프로토타이핑할 수 있는 안전한 환경입니다. 도구가 활성화된(Tools enabled) LLM을 선택한 후 **Tools** 드롭다운을 사용하면, 관리형 서버나 Databricks Apps를 통한 커스텀 서버 모두 쉽게 테스트해 볼 수 있습니다.

이를 통해 에이전트 로직과 MCP 서버 연동을 실제 코드 배포 전에 빠르게 검증할 수 있습니다.

---

## 시나리오 예시: 고객 지원 에이전트

여러 관리형 MCP 서버에 연결된 고객 지원 에이전트를 예로 들어보겠습니다.

- **Vector Search**: `https://<workspace-hostname>/api/2.0/mcp/vector-search/prod/customer_support`
  - 지원 티켓 및 문서를 검색
- **Genie Space**: `https://<workspace-hostname>/api/2.0/mcp/genie/{billing_space_id}`
  - 청구 데이터 및 고객 정보 조회
- **UC Functions**: `https://<workspace-hostname>/api/2.0/mcp/functions/prod/billing`
  - 계정 조회 및 업데이트를 위한 커스텀 함수 실행

이를 통해 에이전트는 비정형 데이터(지원 티켓), 구조화 데이터(청구 테이블), 그리고 커스텀 비즈니스 로직에 모두 접근할 수 있게 됩니다.

---

## 로컬 개발 환경에서 시작하기

Databricks MCP 서버에 연결하는 방법은 다른 원격 MCP 서버에 연결하는 방식과 유사합니다. MCP Python SDK와 같은 표준 SDK를 사용할 수 있습니다. 주요 차이점은 Databricks MCP 서버가 기본적으로 보안이 적용되어 있으며, 클라이언트가 인증을 지정해야 한다는 것입니다.

`databricks-mcp` Python 라이브러리는 커스텀 에이전트 코드에서 인증을 단순화하는 데 도움을 줍니다.

### 환경 설정

먼저 워크스페이스에 OAuth로 인증합니다.

```bash
databricks auth login --host https://<your-workspace-hostname>
```

그런 다음 필요한 패키지를 설치합니다.

```bash
pip install -U "mcp>=1.9" "databricks-sdk[openai]" "mlflow>=3.1.0" "databricks-agents>=1.0.0" "databricks-mcp"
```

### 연결 테스트

아래 코드로 MCP 서버와의 연결을 검증하고, 사용 가능한 Unity Catalog 도구를 나열해 볼 수 있습니다.

```python
from databricks_mcp import DatabricksMCPClient
from databricks.sdk import WorkspaceClient

# TODO: Databricks CLI 프로파일 이름으로 교체하세요
databricks_cli_profile = "YOUR_DATABRICKS_CLI_PROFILE"
workspace_client = WorkspaceClient(profile=databricks_cli_profile)
workspace_hostname = workspace_client.config.host
mcp_server_url = f"{workspace_hostname}/api/2.0/mcp/functions/system/ai"

def test_connect_to_server():
    mcp_client = DatabricksMCPClient(
        server_url=mcp_server_url,
        workspace_client=workspace_client
    )
    tools = mcp_client.list_tools()
    print(
        f"MCP 서버 {mcp_server_url}에서 발견된 도구: {[t.name for t in tools]}"
    )
    result = mcp_client.call_tool(
        "system__ai__python_exec", {"code": "print('Hello, world!')"}
    )
    print(f"system__ai__python_exec 도구 호출 결과: {result.content}")

if __name__ == "__main__":
    test_connect_to_server()
```

---

## 에이전트 배포하기

관리형 MCP 서버에 연결하는 에이전트를 배포할 준비가 되면, 로깅 시점에 에이전트에 필요한 모든 리소스를 지정해야 합니다. 예를 들어 에이전트가 아래의 MCP 서버 URL을 사용하는 경우, `prod.customer_support` 및 `prod.billing` 스키마의 모든 벡터 검색 인덱스와 `prod.billing`의 모든 Unity Catalog 함수를 지정해야 합니다.

```
https://<your-workspace-hostname>/api/2.0/mcp/vector-search/prod/customer_support
https://<your-workspace-hostname>/api/2.0/mcp/vector-search/prod/billing
https://<your-workspace-hostname>/api/2.0/mcp/functions/prod/billing
```

`databricks_mcp.DatabricksMCPClient().get_databricks_resources(<server_url>)` 를 사용하면 관리형 MCP 서버에 필요한 리소스를 자동으로 가져올 수 있습니다.

---

## 컴퓨팅 가격

MCP 서버 유형에 따라 다른 가격 정책이 적용됩니다.

| MCP 서버 유형 | 가격 정책 |
| --- | --- |
| 커스텀 MCP (Databricks Apps 호스팅) | Databricks Apps 가격 |
| Unity Catalog 함수 | 서버리스 일반 컴퓨팅 가격 |
| Genie 스페이스 | 서버리스 SQL 컴퓨팅 가격 |
| Databricks SQL 서버 | Databricks SQL 가격 |
| Vector Search 인덱스 | Vector Search 가격 |

이 표에서 각 MCP 서버 유형마다 서로 다른 컴퓨팅 리소스가 소비됨을 알 수 있습니다. 에이전트 설계 시 비용 구조를 고려하여 적합한 서버 유형을 선택하는 것이 중요합니다.

---

## 예제 노트북: Databricks MCP 서버를 활용한 에이전트 구축

Databricks는 관리형 MCP 서버를 활용하는 LangGraph 및 OpenAI 에이전트 구축 방법을 보여주는 예제 노트북을 제공합니다.

- **LangGraph MCP 도구 호출 에이전트**: LangGraph 프레임워크를 사용한 MCP 도구 호출 에이전트
- **OpenAI MCP 도구 호출 에이전트**: OpenAI API를 사용한 MCP 도구 호출 에이전트
- **Agents SDK MCP 도구 호출 에이전트**: Databricks Agents SDK를 활용한 MCP 도구 호출 에이전트

---

## 현재 상태 및 향후 계획

Databricks 관리형 MCP 서버는 현재 **베타(Beta)** 상태입니다. 향후 Databricks는 다음 방향으로 기능을 확장할 계획입니다.

- DBSQL 등 더 많은 Databricks 리소스 유형에 대한 관리형 서버 지원 확대
- 다른 기업 및 서비스가 제공하는 MCP 서버를 관리, 탐색, 거버닝할 수 있는 카탈로그 지원 구축

{% hint style="info" %}
**관련 문서**
- [Databricks MCP 서버 공식 문서 (AWS)](https://docs.databricks.com/aws/en/generative-ai/mcp/)
- [관리형 MCP 서버 사용 방법 (AWS)](https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp)
- [외부 MCP 서버 사용 방법 (AWS)](https://docs.databricks.com/aws/en/generative-ai/mcp/external-mcp)
- [Azure Databricks MCP 문서](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/mcp/)
{% endhint %}
