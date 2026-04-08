---
original_title: "Building a Multi-Agent System with OpenAI Agents SDK on Databricks"
authors: "David Huang, Qian Yu"
date: "2025-04-08"
category: "GenAI / Agents"
original_url: "https://medium.com/@AI-on-Databricks/building-a-multi-agent-system-with-openai-agents-sdk-on-databricks-6b6ad6774477"
translated_date: "2026-04-07"
---

> **원문**: [Building a Multi-Agent System with OpenAI Agents SDK on Databricks](https://medium.com/@AI-on-Databricks/building-a-multi-agent-system-with-openai-agents-sdk-on-databricks-6b6ad6774477)

# Databricks에서 OpenAI Agents SDK로 멀티 에이전트 시스템 구축하기

**저자**: David Huang, Qian Yu — Specialist Solutions Architects @ Databricks

---

## AI 에이전트의 시대

업계 리더들은 2025년을 "AI 에이전트의 해"로 명명했습니다. OpenAI의 Operator와 Salesforce의 Agentforce 같은 신규 출시 사례들은 자체 데이터를 기반으로 추론하고 자율적으로 행동하는 시스템 개발에 대한 기업들의 높아지는 관심을 반영합니다.

효과적인 에이전트를 구축하는 것은 상당한 도전을 수반합니다. 일반적으로 언어 모델 엔드포인트에 대한 반복적인 호출을 포함하는 커스텀 워크플로우가 필요하기 때문입니다. LangGraph, LlamaIndex, AutoGen, CrewAI 같은 프레임워크들이 주목을 받아온 가운데, OpenAI는 최근 멀티 에이전트 시스템 구축을 위한 경량의 자체 Agents SDK를 선보였습니다.

Databricks는 프레임워크에 종속되지 않는 접근 방식을 유지하며, 기업 에이전트 개발 및 배포를 위한 최적의 플랫폼이 되고자 합니다. 이 글에서는 OpenAI Agents SDK와 Databricks의 기능을 통합하여 보험 정책 챗봇을 구축하는 방법을 소개합니다.

---

## AI 에이전트 구축의 핵심 요소

성공적인 에이전틱 시스템을 만들려면 다음과 같은 몇 가지 핵심 구성 요소가 필요합니다.

**LLM(대규모 언어 모델, Large Language Models):** 에이전트 기능을 가능하게 하는 기반 기술입니다. 에이전틱 시스템은 일반적으로 서로 다른 목적으로 동일한 LLM을 여러 번 호출하거나, 여러 개의 특화된 모델을 활용합니다. 이 튜토리얼에서는 OpenAI의 GPT-4o를 사용합니다.

**오케스트레이터(Orchestrator):** LLM과의 상호작용과 함수 실행을 위한 외부 API 호출을 관리하는 도구입니다. 오케스트레이터는 저수준의 구현 세부 사항을 추상화하면서도 확장성과 모듈성을 유지합니다. 이 역할을 OpenAI Agents SDK가 담당합니다.

**도구와 지식 베이스(Tools and Knowledge Bases):** 에이전트를 특정 유즈케이스에서 실용적으로 만들어 주는 데이터 보강 리소스입니다. Databricks는 도구와 지식 베이스를 간편하게 생성하고, 거버넌스를 적용하며, 에이전트에 통합할 수 있도록 지원합니다.

**평가(Evaluation):** 철저한 테스트를 통해 프로덕션 준비 여부를 판단합니다. Mosaic AI Agent Evaluation 프레임워크는 Databricks에서 포괄적인 온라인 및 오프라인 평가를 가능하게 합니다. 평가에 대한 상세한 내용은 이후 별도 콘텐츠에서 다룰 예정입니다.

---

## 구현 아키텍처

이 데모에서는 다음을 지원하는 멀티 에이전트 보험 챗봇을 구축합니다.

- 멀티턴(multi-turn) 대화
- 데이터베이스에서의 정형 데이터 조회
- 벡터 데이터베이스에서의 비정형 정보 검색
- 모델 등록 및 REST API 배포

**필요 라이브러리:**

```python
openai-agents==0.0.7
unitycatalog-openai[databricks]==0.2.0
mlflow==2.21.0
```

구현은 노트북 내 Databricks Serverless 컴퓨트를 사용합니다.

---

## Unity Catalog 함수를 통한 도구 접근

도구 호출(Tool calling)을 통해 LLM은 특정 함수를 실행하는 구조화된 JSON 응답을 생성할 수 있습니다. LLM이 함수를 직접 실행하는 것이 아니라, 함수 호출을 신호로 보내는 방식입니다.

Databricks에서는 Unity Catalog(UC)를 통해 커스텀 함수를 에이전트 도구로 활용할 수 있습니다. UC는 정형 데이터(Delta Tables)와 비정형 데이터(Vector Databases) 모두에 대해 보안, 검색 가능성, 재사용성, 운영 효율성을 보장하며 기업 데이터와 AI 자산에 대한 중앙집중식 거버넌스를 제공합니다.

### UC 함수 생성

보험 에이전트를 지원하는 두 가지 함수를 생성합니다.

**search_claims_details_by_policy_no:** 정책 번호로 고객 청구 이력을 조회하는 SQL 함수로, UC의 3단계 네임스페이스 규칙을 따릅니다.

**policy_docs_vector_search:** 근사 최근접 이웃(Approximate Nearest Neighbor) 알고리즘을 사용해 Vector Search 인덱스에서 관련 문서 청크를 검색하는 Databricks SQL AI 함수입니다. Databricks AI Bridge의 `VectorSearchRetrieverTool`을 통한 대안적 구현 방법도 존재합니다.

```sql
-- 정책 번호로 청구 내역 조회
CREATE OR REPLACE FUNCTION catalog.schema.search_claims_details_by_policy_no (
    input_policy_no STRING COMMENT 'Policy number'
)
RETURNS TABLE
COMMENT 'Returns policy details about a customer given policy_no.'
RETURN
SELECT *
FROM catalog.schema.claims_table
WHERE policy_no = input_policy_no;

-- 정책 문서 벡터 검색
CREATE OR REPLACE FUNCTION catalog.schema.policy_docs_vector_search (
    query STRING
    COMMENT 'Query string for insurance policy documentation.'
)
RETURNS TABLE
COMMENT 'Searches policy documentation, retrieving most relevant text documents.'
RETURN
SELECT
    chunked_text as page_content,
    map('doc_path', path, 'chunk_id', chunk_id) as metadata
FROM
    vector_search(
        index => 'catalog.schema.policy_docs_chunked_files_vs_index',
        query => query,
        num_results => 3
    );
```

함수는 Unity Catalog에서 지정된 스키마의 Functions 탭 아래에 표시됩니다.

### OpenAI Agents SDK용 함수 래핑

Unity Catalog AI(UC-AI) 라이브러리는 OpenAI, Anthropic, CrewAI 등 다양한 프레임워크와 통합됩니다. 게시 시점에서 OpenAI Agents SDK와의 완전한 통합은 진행 중이었지만, UC-AI 클라이언트는 UC 함수를 직접 실행할 수 있습니다.

UC 함수는 `function_tool` 데코레이터로 래핑해야 합니다. Pydantic 모델은 에이전트, 도구, 핸드오프에 컨텍스트를 주입하면서 출력 타입을 강제합니다. `UserInfo` 클래스는 고객 ID와 정책 번호를 관리하며, 컨텍스트는 코드 실행 로컬에만 유지되고 LLM으로는 전달되지 않습니다.

```python
from unitycatalog.ai.core.databricks import (
    DatabricksFunctionClient,
    FunctionExecutionResult,
)
from agents import function_tool, RunContextWrapper
from pydantic import BaseModel

class UserInfo(BaseModel):
    cust_id: str | None = None
    policy_no: str | None = None

@function_tool
def search_claims_details_by_policy_no(
    wrapper: RunContextWrapper[UserInfo], policy_no: str
) -> FunctionExecutionResult:
    print("[DEBUG]: search_claims_details_by_policy_no tool called")
    wrapper.context.policy_no = policy_no
    client = DatabricksFunctionClient()
    return client.execute_function(
        function_name="ai.insurance_agent.search_claims_details_by_policy_no",
        parameters={"input_policy_no": wrapper.context.policy_no},
    )

@function_tool
def policy_docs_vector_search(query: str) -> FunctionExecutionResult:
    print("[DEBUG]: policy_docs_vector_search tool called")
    client = DatabricksFunctionClient()
    return client.execute_function(
        function_name="ai.insurance_agent.policy_docs_vector_search",
        parameters={"query": query},
    )
```

---

## OpenAI Agents SDK와 MLflow Tracing을 활용한 오케스트레이션

멀티 에이전트 시스템은 언어 모델들이 "핸드오프(handoff)" 메커니즘을 통해 협력하며 문제를 해결합니다. 프롬프트, 컨텍스트, 출력이 에이전트 간에 전달되는 이 핸드오프 패턴이 OpenAI Agents SDK의 핵심입니다.

### 개별 에이전트 정의

각 에이전트는 특정 작업, 루틴, 지정된 LLM, 접근 가능한 도구, 그리고 원하는 보호 장치가 필요합니다. OpenAI API 키가 환경 변수로 설정되어 있는지 확인하세요.

```python
import os
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(...)

claims_detail_retrieval_agent = Agent[UserInfo](
    name="Claims Details Retrieval Agent",
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX}"
        "You are a claims details retrieval agent. "
        "If speaking to a customer, you were transferred from the triage agent. "
        "Use this routine:\n"
        "1. Identify the customer's last question.\n"
        "2. Use search tools to retrieve claim data.\n"
        "3. Transfer back if unable to answer.\n"
    ),
    tools=[search_claims_details_by_policy_no],
    model="gpt-4o",
)

policy_qa_agent = Agent[UserInfo](
    name="Policy Q&A Agent",
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX}"
        "You are an insurance policy Q&A agent. "
        "If speaking to a customer, you were transferred from the triage agent. "
        "Use this routine:\n"
        "1. Identify the customer's last question.\n"
        "2. Use search tools to answer policy questions.\n"
        "3. Transfer back if unable to answer.\n"
    ),
    tools=[policy_docs_vector_search],
    model="gpt-4o",
)
```

`instructions` 필드에는 에이전트 프롬프트가 들어갑니다. 선택적으로 사용하는 `RECOMMENDED_PROMPT_PREFIX`는 핸드오프 기능을 향상시킵니다. `tools` 필드는 사용 가능한 함수 목록을 지정하고, `model` 필드는 기반 LLM을 지정하며 모든 OpenAI 모델을 지원합니다.

Anthropic의 Claude 3.7 Sonnet(현재 Databricks에서 네이티브로 사용 가능)과 같은 대안 모델의 경우, `OpenAIChatCompletionsModel` 객체를 다음과 같이 정의합니다.

```python
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

BASE_URL = "https://your-databricks-workspace.com/serving-endpoints"
API_KEY = dbutils.secrets.get(...)

client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

custom_llm = OpenAIChatCompletionsModel(
    model="databricks-claude-3-7-sonnet",
    openai_client=client
)
```

### 트리아지 에이전트 생성

트리아지(Triage) 에이전트는 질문을 적절한 전문 에이전트로 라우팅합니다.

```python
triage_agent = Agent[UserInfo](
    name="Triage agent",
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX}"
        "You are a helpful triaging agent. "
        "Delegate questions to appropriate agents. "
        "If customers have no further questions, wish them well."
    ),
    handoffs=[claims_detail_retrieval_agent, policy_qa_agent],
    model="gpt-4o",
)
```

SDK의 시각화 함수를 사용하면 멀티 에이전트 시스템 아키텍처의 그래픽 표현을 생성할 수 있습니다.

### 에이전트와 대화하기

```python
import mlflow
from agents import Runner

user_info = UserInfo(cust_id="7852", policy_no="102070455")

with mlflow.start_span(name="insurance_agent", span_type="AGENT") as span:
    print("[AGENT] Hello! How may I assist you?")
    while True:
        user_input = input("[USER]: ")
        if user_input.lower() == "exit":
            print("[AGENT]: Bye!")
            break
        if not user_input:
            continue
        try:
            result = await Runner.run(
                starting_agent=triage_agent,
                input=user_input,
                context=user_info
            )
            print("\n[AGENT]:", result.final_output)
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
```

`Runner.run()` 메서드는 트리아지 에이전트를 시작 지점으로 사용하며, 사용자 입력과 컨텍스트를 인수로 받습니다.

### MLflow Tracing을 통한 실행 가시성

MLflow Tracing은 워크플로우 실행에 대한 상세한 정보를 캡처하여 각 단계의 입력, 출력, 메타데이터를 기록합니다. 이를 통해 디버깅과 동작 분석이 용이해집니다.

`mlflow.start_span()`으로 실행을 감싸면 전체 채팅 세션이 단일 트레이스에 캡처되어, 핸드오프와 도구 사용이 발생한 중간 단계를 확인할 수 있습니다. 트레이싱 UI는 시스템 프롬프트, 입력 문자열, 사용 가능한 도구, 에이전트 응답, 모델 선택 및 토큰 수 같은 속성을 포함한 계층적 실행 구조를 보여줍니다.

트레이스가 OpenAI로 자동 전송되는 것을 막고 데이터를 Databricks 내에 유지하길 원하는 보안에 민감한 기업을 위해:

```python
import os
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

from agents import set_tracing_disabled
set_tracing_disabled(disabled=True)
```

또는 Databricks Model Serving을 통해 제공되는 External Model 엔드포인트와 함께 `OpenAIChatCompletionsModel`을 사용하면 OpenAI 모델 사용을 유지하면서 MLflow 트레이싱을 Databricks 내에서만 수행할 수 있습니다.

---

## Mosaic AI Agent Framework로 로깅, 등록, 배포하기

프로덕션 수준의 에이전트 품질을 확보하려면 도메인 전문가의 피드백을 수집하는 엄격한 평가 루프가 필요합니다. Mosaic AI Agent Framework는 포괄적인 평가를 지원하며, 상세한 평가 방법론은 별도 콘텐츠에서 다룰 예정입니다.

배포는 크게 세 단계로 이루어집니다.

### 1단계: MLflow ChatAgent 인터페이스로 에이전트 래핑

`ChatAgent` 인터페이스는 다중 메시지 반환, 중간 도구 호출 단계, 도구 호출 확인, 멀티 에이전트 시나리오를 지원합니다. `ChatAgent`를 상속하는 Python 클래스를 생성합니다.

```python
import mlflow
from mlflow.pyfunc import ChatAgent

mlflow.openai.autolog()

class InsuranceChatAgent(ChatAgent):
    def __init__(self, starting_agent: Agent):
        self.starting_agent = starting_agent

    def _convert_to_input_text(self, messages: List[ChatAgentMessage]) -> str:
        """가장 최근의 사용자 메시지를 입력 텍스트로 추출"""
        for message in reversed(messages):
            if message.role == "user":
                return message.content
        return ""

    def _create_user_context(
        self,
        context: Optional[ChatContext] = None,
        custom_inputs: Optional[Dict[str, Any]] = None
    ) -> UserInfo:
        """MLflow 입력을 UserInfo 객체로 변환"""
        user_info = UserInfo()
        if context:
            conversation_id = getattr(context, "conversation_id", None)
            if conversation_id:
                user_info.conversation_id = conversation_id

            user_id = getattr(context, "user_id", None)
            if user_id:
                user_info.user_id = user_id
        return user_info
```

커스텀 `predict()`와 `predict_stream()` 메서드를 구현합니다.

```python
from mlflow.entities import SpanType

class InsuranceChatAgent(ChatAgent):
    ...

    @mlflow.trace(name="insurance_chat_agent", span_type=SpanType.AGENT)
    def predict(
        self,
        messages: list[ChatAgentMessage],
        context: Optional[ChatContext] = None,
        custom_inputs: Optional[Dict[str, Any]] = None
    ) -> ChatAgentResponse:
        input_text = self._convert_to_input_text(messages)
        user_info = self._create_user_context(context, custom_inputs)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                Runner.run(
                    starting_agent=self.starting_agent,
                    input=input_text,
                    context=user_info,
                )
            )
        finally:
            loop.close()
        return ChatAgentResponse(
            messages=[
                ChatAgentMessage(
                    role="assistant",
                    content=result.final_output,
                    id=str(uuid4())
                )
            ]
        )

    @mlflow.trace(name="insurance_chat_agent_stream", span_type=SpanType.AGENT)
    def predict_stream(
        self,
        messages: list[ChatAgentMessage],
        context: Optional[ChatContext] = None,
        custom_inputs: Optional[Dict[str, Any]] = None
    ) -> Generator[ChatAgentResponse, None, None]:
        response = self.predict(messages, context, custom_inputs)
        for message in response.messages:
            yield ChatAgentChunk(delta=message)
```

챗봇을 초기화하고 모델 객체로 설정합니다.

```python
AGENT = InsuranceChatAgent(starting_agent=triage_agent)
mlflow.models.set_model(AGENT)
```

### 2단계: 모델 로깅 및 등록

챗봇은 Databricks 데이터에 접근해야 하므로, 의존 리소스를 지정하여 자동 인증 패스스루(authentication passthrough)가 이루어지도록 MLflow를 통해 모델을 로깅합니다.

```python
import os
from mlflow.models.resources import (
    DatabricksFunction,
    DatabricksServingEndpoint,
    DatabricksVectorSearchIndex
)

resources = [
    DatabricksVectorSearchIndex("catalog.schema.policy_docs_chunked_files_vs_index"),
    DatabricksServingEndpoint("databricks-bge-large-en"),
    DatabricksFunction("catalog.schema.search_claims_details_by_policy_no"),
    DatabricksFunction("catalog.schema.policy_docs_vector_search")
]

mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment("/Users/user@company.com/insurance_agent_experiment")
mlflow.openai.autolog()

with mlflow.start_run():
    logged_model_info = mlflow.pyfunc.log_model(
        artifact_path="insurance_chat_agent",
        python_model=os.path.join(os.getcwd(), "insurance_chat_agent.py"),
        input_example={
            "messages": [
                {
                    "role": "user",
                    "content": "hi, id like to check on my existing claims?",
                }
            ],
            "context": {"conversation_id": "123", "user_id": "123"},
        },
        pip_requirements=[
            "mlflow",
            "openai-agents",
            "unitycatalog-openai[databricks]==0.2.0",
            "pydantic",
        ],
        resources=resources
    )
```

Unity Catalog에 에이전트를 모델로 등록합니다.

```python
model_name = "insurance_chat_agent"
UC_MODEL_NAME = f"catalog.schema.{model_name}"

uc_registered_model_info = mlflow.register_model(
    model_uri=logged_model_info.model_uri,
    name=UC_MODEL_NAME
)
```

### 3단계: REST API 엔드포인트로 배포

`agents.deploy()` 함수를 사용해 챗봇을 배포합니다.

```python
from databricks import agents

agents.deploy(
    UC_MODEL_NAME,
    uc_registered_model_info.version,
    environment_vars={
        "OPENAI_API_KEY": "{{secrets/my_scope/my_api_key}}",
        "DATABRICKS_TOKEN": "{{secrets/my_scope/my_token}}",
    },
    tags={"endpoint_desc": "insurance_chat_agent"},
)
```

배포를 통해 얻을 수 있는 이점은 다음과 같습니다.

- **REST API 엔드포인트**: 다운스트림 애플리케이션, 테스트를 위한 AI Playground, 배치 추론 워크플로우와 통합됩니다.
- **Review App**: 도메인 전문가의 피드백 로깅을 가능하게 하며, `payload_request_logs`와 `payload_assessment_logs` Delta 테이블에 자동으로 업데이트됩니다.

10~15분이 지나면 Serving 페이지에서 엔드포인트가 "Ready" 상태로 표시됩니다. "Use" 옆의 화살표 버튼으로 AI Playground, 배치 추론, 쿼리, Review App 모드를 선택할 수 있습니다. 쿼리 관련 권장 사항은 Databricks 문서에서 확인할 수 있습니다.

---

## 마치며

이 글에서는 에이전트 구축의 핵심 구성 요소들을 살펴보았습니다. UC AI 도구 생성, OpenAI Agents SDK를 활용한 에이전트 오케스트레이션, 그리고 Databricks Model Serving에 라이브 엔드포인트로 챗봇을 배포하는 전 과정을 다루었습니다.

이것은 견고한 에이전틱 시스템을 향한 첫걸음에 불과합니다. 이후 반복 작업에서는 지속적인 개선을 위한 도메인 전문가의 피드백 수집이 필요합니다. 평가 방법론은 추후 콘텐츠에서 상세히 다룰 예정입니다.

전체 코드는 [GitHub 저장소](https://github.com/qian-yu-db/OpenAI_Agents_SDK_on_Databricks)에서 확인할 수 있습니다.

궁금한 사항은 Databricks 계정 팀에 문의하세요.
