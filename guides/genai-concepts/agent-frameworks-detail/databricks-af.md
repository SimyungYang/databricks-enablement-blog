# Databricks Agent Framework (Mosaic AI)

Databricks Agent Framework는 "** 빌드보다 배포가 중요하다**"는 철학 아래 설계되었습니다. 오픈소스 프레임워크들이 "Agent를 어떻게 만들 것인가"에 집중한다면, Databricks는 "** Agent를 어떻게 안전하게 운영할 것인가**"에 집중합니다.

{% hint style="info" %}
**핵심 인사이트**: 실제 엔터프라이즈에서 Agent를 프로덕션에 배포할 때 가장 큰 과제는 "Agent를 만드는 것"이 아니라 "누가 어떤 데이터에 접근하는지 통제하고, 응답 품질을 모니터링하고, 문제 발생 시 원인을 추적하는 것"입니다. Databricks Agent Framework는 이 문제를 해결합니다.
{% endhint %}

---

## 설계 철학: 거버넌스 + 배포 + 모니터링 통합

| 단계 | 구성 요소 | 포함 기능 |
|------|----------|----------|
| **Build** | ChatAgent, LangGraph, UC Tools, VS Index | Agent 개발 |
| **Deploy** | Model Serving (Serverless, One-click, Auto-scaling) | 원클릭 서버리스 배포 |
| **Monitor** | MLflow Tracing, Review App, Agent Evaluation, Inference Tables | 추적, 평가, 모니터링 |
| **거버넌스** | Unity Catalog (함수 권한, 데이터 접근 제어, 모델 레지스트리) | 전 계층 통합 거버넌스 |

---

## 핵심 차별점

| 기능 | 설명 | 오픈소스 대비 장점 |
|------|------|-----------------|
| **Unity Catalog Functions as Tools** | UC에 등록된 함수를 Agent 도구로 사용 | 함수에 대한 권한(GRANT/REVOKE)이 자동 적용 |
| **MLflow Tracing** | 전체 추론 과정(LLM 호출, 도구 실행, 에러)을 자동 기록 | 별도 설정 없이 네이티브 통합 |
| **Review App** | 비개발자가 웹 UI에서 Agent 응답을 평가/피드백 | 인간 피드백을 쉽게 수집 |
| **One-click Model Serving** | 서버리스 엔드포인트로 즉시 배포 | 인프라 관리 불필요 |
| **AI Guardrails** | Llama Guard 기반 입출력 안전성 검증 | 엔드포인트 레벨에서 자동 적용 |
| **Agent Evaluation** | LLM-as-Judge로 응답 품질 자동 평가 | MLflow Evaluate와 통합 |
| **Inference Tables** | 모든 요청/응답을 Delta 테이블에 자동 저장 | 감사 추적 + 품질 모니터링 |

---

## ChatAgent 인터페이스

Databricks Agent Framework의 모든 Agent는 `ChatAgent` 인터페이스를 구현합니다. 이것은 LangGraph, 순수 Python, 어떤 프레임워크로 만들든 동일한 배포/모니터링 체계에 통합되도록 해줍니다.

```python
import mlflow
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import (
    ChatAgentMessage,
    ChatAgentResponse,
    ChatAgentChunk,
)
from databricks.sdk import WorkspaceClient
from typing import Generator

class CustomerServiceAgent(ChatAgent):
    """Databricks Agent Framework 기반 고객 서비스 Agent"""

    def __init__(self):
        # Databricks Foundation Model API 사용
        self.client = WorkspaceClient()
        self.model_endpoint = "databricks-meta-llama-3-3-70b-instruct"

    def predict(
        self,
        messages: list[ChatAgentMessage],
        context=None,
        custom_inputs=None,
    ) -> ChatAgentResponse:
        """동기 응답 -- 전체 결과를 한 번에 반환"""

        # Unity Catalog 함수를 도구로 사용
        response = self.client.serving_endpoints.query(
            name=self.model_endpoint,
            messages=[m.to_dict() for m in messages],
            tools=[
                {
                    "type": "uc_function",
                    "function": {
                        "name": "main.default.search_knowledge_base"
                    }
                },
                {
                    "type": "uc_function",
                    "function": {
                        "name": "main.default.get_order_status"
                    }
                },
            ],
        )

        return ChatAgentResponse(
            messages=[
                ChatAgentMessage(
                    role="assistant",
                    content=response.choices[0].message.content,
                )
            ]
        )

    def predict_stream(
        self,
        messages: list[ChatAgentMessage],
        context=None,
        custom_inputs=None,
    ) -> Generator[ChatAgentChunk, None, None]:
        """스트리밍 응답 -- 토큰 단위로 반환"""
        # 스트리밍 구현 (생략)
        pass

# MLflow에 Agent 로깅
mlflow.set_experiment("/Users/user@company.com/customer-service-agent")

with mlflow.start_run():
    model_info = mlflow.pyfunc.log_model(
        artifact_path="agent",
        python_model=CustomerServiceAgent(),
        pip_requirements=[
            "mlflow>=2.21",
            "databricks-sdk>=0.40",
        ],
    )

# Unity Catalog에 모델 등록
mlflow.set_registry_uri("databricks-uc")
mlflow.register_model(
    model_uri=model_info.model_uri,
    name="main.default.customer_service_agent",
)
```

---

## LangGraph + Databricks: 최적의 조합

실전에서는 LangGraph로 복잡한 Agent 로직을 구현하고, Databricks Agent Framework로 배포/모니터링하는 조합이 가장 강력합니다.

```python
import mlflow
from mlflow.pyfunc import ChatAgent
from langgraph.prebuilt import create_react_agent
from langchain_databricks import ChatDatabricks
from langchain_community.tools.databricks import UCFunctionToolkit

class LangGraphOnDatabricks(ChatAgent):
    """LangGraph Agent를 Databricks에서 운영하는 패턴"""

    def __init__(self):
        # Databricks Foundation Model 사용
        model = ChatDatabricks(
            endpoint="databricks-meta-llama-3-3-70b-instruct",
            temperature=0.1,
        )

        # Unity Catalog 함수를 LangGraph 도구로 변환
        uc_toolkit = UCFunctionToolkit(
            function_names=[
                "main.default.search_knowledge_base",
                "main.default.execute_sql_query",
            ]
        )
        tools = uc_toolkit.get_tools()

        # LangGraph ReAct Agent 생성
        self.agent = create_react_agent(model, tools)

    @mlflow.trace  # MLflow Tracing 자동 적용
    def predict(self, messages, context=None, custom_inputs=None):
        # LangGraph Agent 실행
        result = self.agent.invoke({
            "messages": [m.to_dict() for m in messages]
        })
        return ChatAgentResponse(
            messages=[
                ChatAgentMessage(
                    role="assistant",
                    content=result["messages"][-1].content,
                )
            ]
        )
```

{% hint style="success" %}
**Databricks Agent Framework의 진짜 가치**: 오픈소스 프레임워크는 "Agent를 만드는 10%의 시간"을 줄여주고, Databricks Agent Framework는 "나머지 90%인 배포, 모니터링, 거버넌스, 평가"를 해결합니다.
{% endhint %}

---

[README로 돌아가기](README.md) | 다음: [종합 비교 & 선택 가이드](comparison.md)
