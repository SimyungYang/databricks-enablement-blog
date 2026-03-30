# Tool 연결

AI 에이전트에 실행 능력을 부여하는 Tool의 종류와 연결 방법을 설명합니다.

{% hint style="info" %}
Tool은 에이전트가 텍스트 생성 이상의 실질적 작업을 수행할 수 있게 해줍니다. 문서 검색, 데이터베이스 쿼리, REST API 호출, 커스텀 코드 실행 등이 가능합니다.
{% endhint %}

---

## 지원 Tool 유형 개요

| Tool 유형 | 설명 | 주요 용도 |
|---|---|---|
| **Unity Catalog Functions** | SQL/Python 함수를 도구로 등록 | 커스텀 비즈니스 로직, 코드 실행 |
| **Vector Search Index** | 벡터 인덱스 기반 문서 검색 | RAG, 문서 QA |
| **Genie Space** | 자연어 SQL 분석 | 데이터 분석, 리포팅 |
| **MCP Servers (Managed)** | Databricks 기본 제공 MCP | UC 데이터, Genie, Vector Search 접근 |
| **MCP Servers (External)** | 외부 MCP 서버 연결 | 외부 API, 서드파티 서비스 |
| **MCP Servers (Custom)** | 자체 MCP 서버 호스팅 | 커스텀 비즈니스 로직 |

---

## Unity Catalog Functions

Unity Catalog에 등록된 SQL 또는 Python 함수를 에이전트 Tool로 사용합니다.

### 기본 제공 함수

- `system.ai.python_exec` - Python 코드를 동적으로 실행
- 기타 시스템 함수

### 커스텀 UC Function 등록 예제

```sql
-- 고객 정보 조회 함수 생성
CREATE OR REPLACE FUNCTION main.agents.get_customer_info(
  customer_id STRING COMMENT '조회할 고객의 ID'
)
RETURNS TABLE (name STRING, email STRING, plan STRING)
COMMENT '고객 ID로 고객의 이름, 이메일, 요금제를 조회합니다.'
RETURN
  SELECT name, email, plan
  FROM main.crm.customers
  WHERE id = customer_id;
```

```sql
-- 주문 상태 조회 함수
CREATE OR REPLACE FUNCTION main.agents.get_order_status(
  order_id STRING COMMENT '주문 번호'
)
RETURNS TABLE (status STRING, shipped_date DATE, tracking_number STRING)
COMMENT '주문 번호로 배송 상태, 발송일, 운송장 번호를 조회합니다.'
RETURN
  SELECT status, shipped_date, tracking_number
  FROM main.sales.orders
  WHERE order_id = order_id;
```

{% hint style="tip" %}
**COMMENT**를 명확하게 작성하세요. LLM은 함수의 이름과 COMMENT를 기반으로 어떤 Tool을 호출할지 결정합니다. 파라미터 COMMENT도 마찬가지로 중요합니다.
{% endhint %}

### AI Playground에서 추가

1. **Tools** > **+ Add tool** > **UC Function** 선택
2. 카탈로그/스키마를 탐색하여 함수 선택
3. 자동으로 함수 시그니처와 설명이 Tool로 등록됨

{% hint style="warning" %}
UC Functions는 레거시 방식으로 분류되며, 새로운 구현에는 **MCP 기반 Tool**이 권장됩니다. 다만 기존 UC Function도 계속 지원됩니다.
{% endhint %}

---

## Vector Search Index

Vector Search Index를 연결하여 RAG(검색 증강 생성) 기반 문서 검색을 수행합니다.

### 사전 준비

1. Vector Search Endpoint가 생성되어 있어야 합니다.
2. 대상 데이터가 Vector Search Index로 인덱싱되어 있어야 합니다.

### AI Playground에서 추가

1. **Tools** > **+ Add tool** > **Vector Search** 선택
2. Vector Search Index를 선택합니다.
3. 에이전트가 질문을 받으면 자동으로 인덱스를 검색합니다.

### 특징

- 검색 결과에 **출처(Source Citation)**가 자동 포함됩니다.
- 유사도 기반 검색으로 관련 문서를 반환합니다.
- 여러 인덱스를 동시에 연결할 수 있습니다.

---

## Genie Space

Genie Space를 연결하면 에이전트가 자연어로 SQL 쿼리를 생성하고 실행할 수 있습니다.

### AI Playground에서 추가

1. **Tools** > **+ Add tool** > **Genie Space** 선택
2. 기존에 생성된 Genie Space를 선택합니다.
3. 에이전트가 데이터 분석 요청을 Genie Space로 전달합니다.

### 활용 시나리오

- "이번 달 매출 상위 10개 제품은?"
- "지난 분기 대비 반품률 변화를 알려줘"
- "부서별 인건비 추이를 차트로 보여줘"

---

## MCP Servers

**Model Context Protocol(MCP)**은 에이전트가 도구, 리소스, 프롬프트에 접근하는 오픈 소스 표준입니다.

### Managed MCP

Databricks가 기본 제공하는 MCP 서버입니다.

- Unity Catalog 데이터 접근
- Genie Space 연동
- Vector Search Index 검색
- Databricks SQL 실행

### External MCP

외부에서 운영되는 MCP 서버에 안전하게 연결합니다.

- Managed Connection을 통한 보안 연결
- 서드파티 API 통합 (Slack, GitHub, Jira 등)

### Custom MCP

Databricks Apps에서 자체 MCP 서버를 호스팅합니다.

- 커스텀 비즈니스 로직 구현
- 내부 시스템 연동

{% hint style="info" %}
**MCP 베스트 프랙티스**:
1. Tool 이름을 하드코딩하지 마세요 - 런타임에 동적으로 발견되어야 합니다.
2. Tool 응답을 프로그래밍으로 파싱하지 마세요 - LLM이 해석하도록 합니다.
3. 어떤 Tool을 호출할지는 LLM이 결정하도록 하세요.
{% endhint %}

---

## 비용 구조

| MCP 유형 | 과금 기준 |
|---|---|
| Custom MCP | Databricks Apps 가격 |
| Managed MCP (UC Functions) | Serverless General Compute |
| Managed MCP (Genie) | Serverless SQL Compute |
| Managed MCP (Vector Search) | Vector Search 가격 |

---

## 참고 링크

- [AI agent tools](https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-tool)
- [MCP on Databricks](https://docs.databricks.com/aws/en/generative-ai/mcp/)
- [Unity Catalog Functions](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-functions-udf.html)
- [Vector Search](https://docs.databricks.com/aws/en/generative-ai/vector-search/)
