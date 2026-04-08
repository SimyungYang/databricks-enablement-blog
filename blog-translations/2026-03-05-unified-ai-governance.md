---
title: "AI Agent를 확신 있게 확장하기 위한 새로운 거버넌스 기능 소개"
date: 2025-03-10
author: "Archika Dogra, Vladimir Kolovski, Sid Murching"
tags: [ai-governance, ai-agents, unity-catalog, ai-gateway, genie]
---

> **원문**: [Introducing New Governance Capabilities to Scale AI Agents with Confidence](https://www.databricks.com/blog/introducing-new-governance-capabilities-scale-ai-agents-confidence)

![Scaling AI Agents with Confidence: Unified Governance Across Models, Tools, and Data](https://www.databricks.com/sites/default/files/2025-03/week-of-ai-agents-og-day-5.png)

이번 주 초 [블로그](https://www.databricks.com/blog/unlocking-potential-ai-agents-pilots-production-success)에서 언급했듯이, AI Agent가 프로덕션 수준의 품질을 달성하려면 엔터프라이즈 데이터 통합과 출력 거버넌스가 반드시 필요합니다. 오늘 우리는 Agent Bricks AI Gateway, Unity Catalog 도구, 그리고 AI/BI Genie에 대한 업데이트를 출시하며, 이를 통해 조직이 견고한 거버넌스와 데이터 통합 기능을 갖춘 프로덕션 수준의 AI Agent를 구축할 수 있게 됩니다.

이것이 왜 중요한지 생각해 보겠습니다. 개발자들이 우선순위가 높은 고객 불만을 요약하고 Slack을 통해 부서에 알림을 보내는 AI Agent를 구축했다고 가정해 보십시오. 높은 품질의 성능 없이는 부서가 불필요한 알림에 압도될 수 있으며, 그로 인해 진정으로 긴급한 사항을 놓칠 수 있습니다. 더 나쁜 경우, 개발자들이 안전한 엔터프라이즈 통합을 사용하는 대신 Slack API 자격 증명에 직접 접근할 경우, 악의적인 행위자가 이 자격 증명을 탈취하여 회사 전체에 피싱 링크를 배포할 수도 있습니다.

AI Agent의 핵심에는 세 가지 필수 구성 요소가 있습니다: **모델(Models)**, **도구(Tools)**, **데이터(Data)**. 오늘의 업데이트가 어떻게 잘 관리되고 고품질인 AI Agent를 전반적으로 구축할 수 있게 해주는지 살펴보겠습니다:

- **Models** – [Agent Bricks AI Gateway](https://docs.databricks.com/aws/en/ai-gateway)(Public Preview)를 활용하여 Foundation Model 접근을 관리하고, 품질을 모니터링하며, 제공자 전반에 걸쳐 사용량을 추적합니다. 이제 향상된 모델 안정성을 위한 자동 트래픽 Fallback을 활성화하고, [커스텀 제공자 LLM](https://docs.databricks.com/aws/en/generative-ai/external-models#model-providers)을 External Model로 통합할 수 있습니다.
- **Tools** – 위험한 자격 증명 관리와 작별하세요. [Unity Catalog Connections 및 Functions](https://docs.databricks.com/aws/en/generative-ai/agent-framework/external-connection-tools)가 엔터프라이즈 및 외부 API를 AI Agent를 위한 강력한 도구로 안전하게 통합합니다.
- **Data** – AI Agent가 엔터프라이즈 데이터에 안전하게 접근할 수 있도록 합니다. [AI/BI Genie Conversation APIs](https://www.databricks.com/blog/genie-conversation-apis-public-preview)(Public Preview)와 [Vector Search retrieval tool](https://docs.databricks.com/aws/en/generative-ai/agent-framework/unstructured-retrieval-tools)이 Agent Framework와 직접 통합되어, Unity Catalog 데이터에 대한 안전한 파이프라인을 구축하는 동시에 귀중한 인사이트를 제공합니다.

![AI Agent 시스템을 위한 거버넌스](https://www.databricks.com/sites/default/files/inline-images/agent-systems-inline-image-navy900-01-3.png)

Databricks는 모든 AI Agent에 대해 통합된 엔드투엔드 거버넌스 프레임워크를 제공하여, 단편적인 솔루션의 필요성을 없애고 전반적인 품질과 보안을 높입니다. 이제 이러한 핵심 거버넌스 구성 요소 각각에 대한 최신 업데이트를 살펴보겠습니다.

## 최신 Foundation Model로 AI Agent를 안전하게 구동하기

Databricks에서 우리는 오픈소스든 독점적이든, 적합한 Foundation Model을 사용하는 것이 고품질 AI Agent를 구축하는 데 근본적임을 알고 있습니다.

[Agent Bricks AI Gateway](https://docs.databricks.com/aws/en/ai-gateway)는 엔터프라이즈급 AI를 위한 중앙 제어 허브로서, 모든 Foundation Model과 AI Agent 전반에 걸쳐 거버넌스와 품질을 모두 보장합니다. AI Gateway를 통해 다음을 수행할 수 있습니다:

- AI Agent 내에서 사용되는 주요 모델(OpenAI GPT, Claude, Llama, Gemini)에 대해 중앙 집중식 권한, 가드레일, 속도 제한을 통한 안전한 제어를 적용합니다.
- [자동 페이로드 로깅](https://docs.databricks.com/aws/en/ai-gateway/inference-tables)을 통해 프로덕션에서 AI Agent 품질을 모니터링하고 컴플라이언스를 위해 감사합니다.
- 모든 제공자 전반에 걸쳐 사용량 추적을 통합하여 비용 귀속 및 사용량 감사를 간소화합니다.

Agent Bricks AI Gateway는 거버넌스와 유연성을 결합하여 혁신을 가속화하고 고품질 AI Agent를 제공합니다. 개발자들은 모두 관리되고 중앙 집중화된 프레임워크 내에서 AI Agent에 가장 최적화된 모델에 대한 통합 접근권을 얻게 됩니다.

우리는 이것이 고객들에게 얼마나 큰 가치를 창출했는지를 확인했으며, 신뢰할 수 있고 고품질인 AI Agent를 구축하기 위해 AI Gateway를 통해 제공되는 두 가지 새로운 기능을 발표하게 되어 기쁩니다:

## 1. Agent Bricks AI Gateway의 Custom Provider 지원 소개 (Public Preview)

많은 기업들이 고유한 필요에 맞는 커스텀 프록시를 개발했지만, AI Agent를 Databricks에서 엔드투엔드로 구축하고 배포하고자 합니다. 또한 자체 호스팅 또는 서드파티 모델을 AI Gateway에 통합하여 AI Agent에 최적의 모델을 활용해야 하는 경우도 있습니다.

오늘부터 AI Gateway는 커스텀 프록시에 호스팅되어 있든 대체 제공자에서 제공되든 상관없이, OpenAI 스키마와 호환되는 모든 Foundation Model을 External Model로 지원합니다. 이를 통해 중앙 집중식 모델 접근 관리가 가능해지며, Foundation Model이 어디에 호스팅되어 있는지 상관없이 보안을 보장하고 품질 모니터링을 위한 귀중한 데이터를 캡처할 수 있습니다.

오늘 당장 모든 Foundation Model을 AI Agent에 안전하게 통합하려면, [커스텀 제공자의 LLM을 등록](https://docs.databricks.com/aws/en/generative-ai/external-models)하여 Agent Bricks AI Gateway를 사용한 접근 관리 및 품질 모니터링을 시작하십시오.

## 2. AI Model Fallback으로 안정적인 AI Agent 구동하기 (Public Preview)

신뢰할 수 있는 고트래픽 AI Agent를 프로덕션화해야 하는 팀들은 서드파티 AI 모델 제공자의 가용성 문제에 자주 부딪힙니다. 서드파티 서비스가 예기치 않게 중단되거나 사용량 급증으로 인해 할당량 제한에 도달하면, 이러한 Foundation Model(및 그에 의존하는 AI Agent)에 접근할 수 없게 됩니다.

Agent Bricks AI Gateway의 새로운 트래픽 Fallback은 여러 제공자, 리전, 리소스 전반에 걸쳐 원활한 Failover를 보장하여 클라이언트 측 중단을 방지합니다. 자동 Fallback 메커니즘을 통해 기업은 사용량 급증이나 중단 중에도 AI Agent 시스템을 원활하게 운영할 수 있습니다.

> *"Erste Group에서 안정적인 AI 기반 운영 보장은 우리의 성공에 매우 중요합니다. Agent Bricks AI Gateway의 Fallback 기능은 주요 모델에 문제가 발생할 때 자동으로 트래픽을 재라우팅함으로써 시스템의 복원력을 강화했습니다."*
>
> — Jürgen Neulinger, Sr. Solutions Manager, Erste Group

![모델별 평균 실행 시간](https://www.databricks.com/sites/default/files/inline-images/average-execution-duration-by-model.png)

기본 모델을 사용할 수 없을 때 백업 모델로 트래픽을 자동으로 리다이렉트합니다.

## 안전한 API 접근 및 도구 통합으로 AI Agent 기능 향상

AI Agent는 외부 서비스(예: Teams, Slack)와 엔터프라이즈 백엔드(예: 내부 API)와 통합될 때 더욱 강력해져 의사 결정을 내리고 행동을 취할 수 있게 됩니다. 그러나 특히 대규모로 개발자들에게 이러한 민감한 API 자격 증명을 배포하는 것은 심각한 보안 문제를 야기할 수 있습니다.

[Unity Catalog(UC) Connections 및 Functions](https://docs.databricks.com/aws/en/generative-ai/agent-framework/external-connection-tools#create-a-connection-to-the-external-service)(Public Preview)를 통해 개발자들은 보안 위험 없이 완전히 관리되는 API 통합을 AI Agent에 통합할 수 있습니다.

특히, IT 팀은 UC Connections를 사용하여 모든 API 자격 증명을 중앙에서 안전하게 관리할 수 있습니다. 접근 권한에 따라 개발자들은 사전 승인된 연결을 도구로 AI Agent에 통합하고, 선택적으로 이를 호출하는 UC Functions를 생성 및 공유할 수 있습니다. 이를 통해 개발자와 해당 코드가 원격 API 토큰에 접근할 수 없으며, UC Connections를 통한 모든 API 접근은 완전히 감사됩니다.

다음은 개발자가 UC Connection을 통해 Slack REST API에 인증하는 "Slack 메시지 보내기" 도구를 Python으로 정의하는 방법의 예시입니다:

```python
from langchain_core.tools import tool

# @tool 어노테이션은 이 Python 함수를 LangChain에서 도구로 사용할 수 있게 해주지만,
# 다른 Agent 작성 프레임워크에서도 사용할 수 있습니다
@tool
def send_slack_message(message):
    w = WorkspaceClient()
    # UC HTTP connections를 사용하여 Slack에 인증
    ws_client = WorkspaceClient()
    return ws_client.connections.request(
        conn="slack_connection",
        method="POST",
        path="/api/chat.postMessage",
        json={"channel": "C07MB25Q6H3", "text": message},
    ).text
```

UC Connections는 안전하고, 재사용 가능하며, 발견 가능합니다. 이제 개발자들은 철저한 API 거버넌스를 유지하면서 실제 데이터 및 행동과 상호작용하는 민첩한 AI Agent를 구축할 수 있습니다.

## Agent 시스템에 엔터프라이즈 데이터를 안전하게 통합하기

AI Agent는 차별화된 품질과 성능을 이끌어내기 위해 독점 데이터에 의존합니다. 따라서 고품질 인사이트와 행동을 제공하는 엔터프라이즈 데이터와 상호작용하는 안전하고 효율적인 방법이 필수적입니다.

안전하고 고성능인 AI Agent를 보장하기 위해, 우리는 구조화된 데이터와 비구조화된 엔터프라이즈 데이터를 AI Agent에 손쉽게 통합할 수 있는 두 가지 새로운 기능을 소개합니다.

### AI/BI Genie Conversation APIs

개발자들은 비즈니스 팀이 자연어를 사용하여 데이터와 상호작용할 수 있게 해주는 강력한 AI/BI 도구인 Genie를 AI Agent에 통합하는 방법을 요청해 왔습니다. **Genie Conversation APIs**가 이제 이를 가능하게 합니다!

Unity Catalog가 모든 Genie 데이터를 관리하므로, 서로 다른 부서의 비즈니스 사용자들이 "내 비용이 얼마야?"라고 질문해도 자신의 부서와 관련된 결과만 볼 수 있습니다. Genie Conversation APIs를 Agent Framework에 통합하면, Unity Catalog 데이터와 상호작용하는 안전한 멀티 에이전트 시스템을 그 어느 때보다 쉽게 구축할 수 있습니다.

> *"Genie가 Teams와 통합된 것은 데이터 민주화를 위한 큰 도약이었습니다. 기술적 배경과 상관없이 모든 사람이 데이터 인사이트에 접근할 수 있게 해줍니다."*
>
> — Cezar Steinz, Data Operations Manager, Grupo Casas Bahia

시작하려면, Genie Conversation APIs를 발표하는 자세한 블로그를 [여기](https://www.databricks.com/blog/genie-conversation-apis-public-preview)서 확인하십시오.

![MLflow Trace UI](https://www.databricks.com/sites/default/files/inline-images/ml-flow-trace-ui_0.png)

Genie Conversation APIs를 Agent Framework에 통합합니다.

### Vector Search Retrieval Tool

많은 AI Agent가 Databricks Vector Search를 활용하여 비구조화 데이터와 안전하게 통신합니다. Unity Catalog의 데이터 거버넌스 기능을 유지하면서 이를 AI Agent 시스템의 도구로 통합하는 것을 단순화하기 위해, [Vector Search Retrieval Tool](https://docs.databricks.com/aws/en/generative-ai/agent-framework/unstructured-retrieval-tools) APIs를 도입했습니다.

이 APIs를 통해 AI Agent 내에서 Vector Search Retriever를 도구로 원활하게 통합할 수 있으며, 민감한 정보를 보호하면서 확신 있게 고품질 인사이트를 제공할 수 있습니다.

```python
from databricks_langchain import VectorSearchRetrieverTool, ChatDatabricks

# Retriever 도구 초기화
vs_tool = VectorSearchRetrieverTool(
    index_name="catalog.schema.my_databricks_docs_index",
    tool_name="databricks_docs_retriever",
    tool_description="공식 Databricks 문서에서 Databricks 제품에 대한 정보를 검색합니다."
)

# Retriever 도구를 원하는 LangChain LLM에 바인딩
llm = ChatDatabricks(endpoint="databricks-meta-llama-3-1-70b-instruct")
llm_with_tools = llm.bind_tools([vs_tool])

# LLM으로 채팅하여 도구 호출 기능 테스트
llm_with_tools.invoke("Databricks 문서를 기반으로, Databricks Agent Framework는 무엇인가요?")
```

엔터프라이즈 데이터로 AI Agent를 안전하게 강화하는 것이 이제 몇 줄의 코드만큼 간단해졌습니다.

## 지금 바로 AI Agent 구축 및 거버넌스 시작하기

최고의 기업들은 거버넌스를 활용하여 프로덕션에서 안전하고 고품질인 AI Agent를 구동합니다. Databricks를 사용하면 모든 모델, 도구, 데이터셋에서 확신 있게 고품질 AI Agent를 확장할 수 있습니다.

오늘 당장 통합된 방식으로 Agent 시스템을 엔드투엔드로 거버넌스하기 시작하십시오:

- AI Agent에 필요한 Foundation Model과 함께 **[Agent Bricks AI Gateway](https://docs.databricks.com/aws/en/ai-gateway)를 설정**합니다.
- Unity Catalog Connections를 사용하여 **[AI Agent 도구를 외부 서비스에 안전하게 연결](https://docs.databricks.com/aws/en/generative-ai/agent-framework/external-connection-tools)**합니다.
- **[Genie Conversation APIs](https://docs.databricks.com/aws/en/genie/set-up)**를 Mosaic AI Agent Framework에 통합합니다.
- **[Vector Search Retrieval Tool](https://docs.databricks.com/aws/en/generative-ai/agent-framework/unstructured-retrieval-tools)**을 Agent 시스템에서 사용하여 비구조화 데이터에 안전하게 접근합니다.
- [데모 영상](https://www.youtube.com/watch?v=-Bzyf7nyZsY&ab_channel=Databricks)을 시청합니다.

그리고 GenAI 투자에서 최대한의 수익을 얻는 방법을 알아보려면 [AI Agent 컴팩트 가이드](https://www.databricks.com/resources/guide/boost-genai-roi-ai-agents)를 꼭 확인하십시오.
