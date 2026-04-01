# AWS, Microsoft & Meta의 AI Agent 전략

2025-2026년, 주요 클라우드 벤더와 AI 기업들은 **AI Agent를 차세대 컴퓨팅 패러다임** 으로 선언하고 각자의 전략적 포지션을 구축하고 있습니다. 이 가이드는 AWS, Microsoft, Meta의 Agent 전략을 심층 비교합니다. Databricks의 전략은 [별도 페이지](databricks.md)에서 다룹니다.

{% hint style="info" %}
** 학습 목표**
- AWS, Microsoft, Meta 각각의 AI Agent 전략과 핵심 제품을 이해한다
- 각 벤더의 멀티에이전트 아키텍처 접근 방식의 차이를 설명할 수 있다
- 각 벤더 생태계와 Databricks가 어떻게 연동되는지 파악한다
- 프로젝트 요구사항에 따라 적합한 벤더 조합을 선택할 수 있다
{% endhint %}

{% hint style="warning" %}
** 기준 시점**: 2026년 3월 기준입니다. AI Agent 시장은 빠르게 변화하므로, 각 벤더의 공식 문서를 병행 확인하시기 바랍니다.
{% endhint %}

---

## 1. AWS -- "풀스택 Agent 인프라"

### 1.1 전략 개요

AWS의 Agent 전략은 "** 빌딩 블록 접근법**"으로 요약됩니다. 단일 통합 제품이 아닌, 각 계층(모델, 런타임, 오케스트레이션, 안전장치, 지식)별로 독립적인 서비스를 제공하고 고객이 조합하도록 합니다. 이는 AWS의 전통적인 "undifferentiated heavy lifting"을 제거하는 철학과 일맥상통합니다.

{% hint style="success" %}
** 핵심 메시지**: "Agent를 빌드하는 것은 쉽지만, 프로덕션에서 안전하고 확장 가능하게 운영하는 것이 진짜 도전이다. AWS는 그 운영 계층을 제공한다."
{% endhint %}

### 1.2 핵심 제품 스택

#### Amazon Bedrock Agents (GA)

Bedrock Agents는 AWS의 ** 관리형 Agent 오케스트레이션 서비스** 로, 두 가지 실행 모드를 지원합니다.

| 모드 | 설명 | 사용 시나리오 |
|------|------|-------------|
| **Supervisor Mode**| 하나의 관리자 Agent가 하위 Agent를 호출하고 결과를 종합 | 복잡한 멀티스텝 업무, 의사결정 체인 |
| **Routing Mode**| 사용자 의도에 따라 가장 적합한 Agent로 직접 라우팅 | 명확한 의도 분류가 가능한 시나리오 |

두 모드 모두 ** 병렬 실행(Parallel Execution)** 을 지원하여, 독립적인 하위 작업을 동시에 수행할 수 있습니다. 예를 들어, "지난 분기 매출 분석 + 경쟁사 뉴스 요약"이라는 요청이 오면 두 작업을 병렬로 실행합니다.

**Supervisor Mode 흐름:**
1. 사용자 요청 → Supervisor Agent (작업 분석)
2. Supervisor → Agent A, Agent B, Agent C (병렬 실행)
3. 모든 Agent 결과 → Supervisor (결과 종합) → 최종 응답

#### Amazon Nova 2 모델 패밀리

AWS의 자체 Foundation Model 라인업으로, Agent 시나리오에 최적화된 세 가지 티어를 제공합니다.

| 모델 | 파라미터 규모 | 컨텍스트 | 특징 | 가격대 |
|------|------------|---------|------|--------|
| **Nova Pro**| 비공개 (대형) | 1M 토큰 | Extended Thinking, 복잡한 추론 | 중-상 |
| **Nova Lite**| 비공개 (중형) | 1M 토큰 | 빠른 응답, 비용 효율 | 저-중 |
| **Nova Sonic**| 비공개 | 실시간 | 음성 Agent (Speech-to-Speech) | 음성 과금 |

{% hint style="info" %}
**Extended Thinking**: Nova Pro는 Claude의 Extended Thinking과 유사한 기능을 제공합니다. Agent가 복잡한 문제를 단계별로 분해하여 추론하므로, 멀티스텝 도구 호출의 정확도가 크게 향상됩니다. 1M 컨텍스트 윈도우는 대용량 문서 분석 Agent에 적합합니다.
{% endhint %}

#### Amazon Nova Act (Research Preview)

Nova Act은 ** 브라우저 자동화를 위한 Agent 모델** 입니다. 웹 페이지를 시각적으로 이해하고, 클릭/타이핑/네비게이션 등의 액션을 수행합니다.

- ** 상태**: Research Preview (프로덕션 사용 불가)
- ** 용도**: RPA 대체, 웹 기반 워크플로 자동화, 테스트 자동화
- ** 경쟁 제품**: Anthropic Computer Use, Google Mariner

#### AgentCore (2025년 10월 GA)

AgentCore는 AWS의 **Agent 운영 플랫폼** 으로, Agent 빌딩이 아닌 **Agent 운영(Deploy & Govern)** 에 초점을 맞춥니다. 프레임워크에 종속되지 않으며 LangGraph, CrewAI, 자체 코드 등 어떤 Agent든 배포 가능합니다.

| 기능 | 설명 |
|------|------|
| **Policy (Cedar 기반)**| AWS의 Cedar 정책 언어를 사용하여 Agent의 행동 범위를 세밀하게 제어. "이 Agent는 S3 버킷 X에만 접근 가능" 같은 선언적 정책 |
| **Evaluations**| Agent 성능을 자동 평가하는 프레임워크. 정확도, 안전성, 비용 효율성 등 다차원 평가 |
| **Memory**| Agent의 장기 기억을 관리하는 서비스. 세션 간 컨텍스트 유지, 사용자 선호도 학습 |
| **Identity**| IAM 기반 Agent 인증/인가. Agent가 다른 AWS 서비스에 접근할 때의 최소 권한 원칙 적용 |

{% hint style="warning" %}
**Cedar 정책 엔진**: Cedar는 원래 Amazon Verified Permissions에서 사용하는 정책 언어입니다. AgentCore에서는 이를 Agent 행동 제어에 확장 적용했습니다. `permit(principal == Agent::"sales-bot", action == Action::"query", resource == Table::"customers")`와 같은 형태로 Agent 권한을 선언적으로 관리합니다.
{% endhint %}

#### Strands Agents SDK (오픈소스)

AWS가 공개한 ** 오픈소스 멀티에이전트 프레임워크** 입니다. LangGraph, CrewAI 등과 경쟁하는 포지션이며, AgentCore와의 네이티브 통합이 최대 강점입니다.

- ** 설계 철학**: "Model-driven" -- LLM이 루프의 중심에서 도구 선택과 실행을 주도
- ** 특징**: 20+ 내장 도구, 비동기 멀티에이전트, AgentCore 네이티브 배포
- ** 라이선스**: Apache 2.0

#### Amazon Q Developer

Amazon Q Developer는 AWS의 **Agentic 코딩 어시스턴트** 로, SWE-bench 벤치마크에서 상위권 성능을 기록하고 있습니다.

| 기능 | 설명 |
|------|------|
| **Agentic Coding**| 코드 생성을 넘어 리팩토링, 테스트 작성, 디버깅까지 자율적 수행 |
| **MCP 지원**| Model Context Protocol을 통해 외부 도구/데이터 소스 연결 |
| **/transform**| Java 8 → 17 등 대규모 코드 마이그레이션 자동화 |
| **/review**| 보안 취약점, 코드 품질 자동 리뷰 |

#### Kiro IDE (2025년 11월 GA)

AWS의 **Agentic IDE** 로, VS Code 기반이지만 Agent-first 설계를 채택했습니다. Spec-driven 개발 방식(요구사항 → 설계 → 구현을 Agent가 주도)이 특징입니다.

#### Guardrails for Bedrock

Bedrock Guardrails는 **Agent 안전장치** 로 6가지 유형의 세이프가드를 제공합니다.

| 세이프가드 | 설명 |
|-----------|------|
| **Content Filters**| 유해 콘텐츠 차단 (혐오, 폭력, 성적 콘텐츠 등) |
| **Denied Topics**| 특정 주제 논의 차단 (경쟁사 비교, 정치 등) |
| **Word Filters**| 특정 단어/구문 차단 |
| **PII Redaction**| 개인정보 자동 마스킹 (이름, 전화번호, 주민번호 등) |
| **Contextual Grounding**| 환각(Hallucination) 탐지 -- 응답이 소스에 근거하는지 검증 |
| **Automated Reasoning**| 수학적 추론 검증으로 **99% 정확도** 보장 |

{% hint style="success" %}
**Automated Reasoning**: 이 기능은 AWS가 2024년 re:Invent에서 발표한 차별화 기능입니다. 형식 검증(Formal Verification) 기술을 적용하여, Agent의 논리적 추론이 수학적으로 올바른지 검증합니다. 특히 금융, 보험, 법률 분야에서 Agent 응답의 신뢰성을 극적으로 높입니다.
{% endhint %}

#### Knowledge Bases for Bedrock

| 기능 | 설명 |
|------|------|
| **S3 Vectors**| S3에 벡터 저장. 기존 벡터 DB 대비 ** 최대 90% 비용 절감**|
| **GraphRAG**| 지식 그래프 기반 RAG. 엔티티 간 관계를 활용한 정밀 검색 |
| **Hybrid Search**| 시맨틱 검색 + 키워드 검색 자동 조합 |

### 1.3 멀티에이전트 아키텍처

AWS의 멀티에이전트 전략은 **3-tier 구조** 입니다.

| 계층 | 서비스 | 역할 |
|------|--------|------|
| ** 빌드**| Strands SDK / Bedrock Agents | Agent 개발 및 오케스트레이션 |
| ** 운영**| AgentCore | 배포, 정책, 모니터링, 메모리 |
| ** 보호**| Guardrails | 안전장치, 환각 방지, 권한 제어 |

### 1.4 차별점 요약

- ** 프레임워크 비종속**: AgentCore는 LangGraph, CrewAI 등 어떤 프레임워크든 수용
- **Cedar 기반 선언적 정책**: Agent 행동을 코드가 아닌 정책으로 제어
- **Automated Reasoning**: 수학적 검증 기반 안전장치
- ** 비용 최적화**: S3 Vectors로 벡터 스토리지 비용 90% 절감
- ** 모델 선택의 자유**: Bedrock에서 Claude, Llama, Nova, Mistral 등 교차 사용

### 1.5 Databricks 연동 시사점

{% hint style="info" %}
**Databricks on AWS 고객이라면**:
- **Bedrock Agent + Databricks Vector Search**: Bedrock Agent가 Databricks의 Vector Search Index를 Tool로 호출하는 하이브리드 구성 가능
- **AgentCore + MLflow**: Agent 배포는 AgentCore, 실험 추적/모니터링은 MLflow 3.0으로 이원화
- **Nova/Claude + Mosaic AI Gateway**: 여러 모델을 Gateway에서 통합 관리하면서, Bedrock Endpoint를 External Model로 등록
- **Unity Catalog 거버넌스**: Agent가 접근하는 데이터의 거버넌스는 Unity Catalog가 담당하고, Agent 자체의 행동 정책은 AgentCore가 담당하는 역할 분리
{% endhint %}

---

## 2. Microsoft -- "오픈 에이전틱 웹"

### 2.1 전략 개요

Microsoft의 Agent 전략은 "**Open Agentic Web**"이라는 비전 아래, Agent가 웹 서비스처럼 상호 운용 가능한 생태계를 만드는 것을 목표로 합니다. OpenAI와의 전략적 파트너십, GitHub/LinkedIn/Dynamics 365 등 SaaS 자산, 그리고 Azure 클라우드를 결합한 ** 수직 통합 전략** 이 핵심입니다.

{% hint style="success" %}
** 핵심 메시지**: "AI Agent는 고립된 봇이 아니라, 서로 대화하고 협업하는 네트워크다. Microsoft는 그 네트워크의 프로토콜과 플랫폼을 모두 제공한다."
{% endhint %}

### 2.2 핵심 제품 스택

#### Agent Framework (2025년 10월 통합)

Microsoft는 두 개의 독립적인 Agent 프레임워크를 ** 하나의 통합 프레임워크** 로 수렴시켰습니다.

| 기존 프레임워크 | 강점 | 통합 후 역할 |
|----------------|------|-------------|
| **AutoGen**| 멀티에이전트 대화, 연구 혁신 | Agent 간 협업 패턴, 대화 기반 문제 해결 |
| **Semantic Kernel**| 엔터프라이즈 통합, .NET 생태계 | 플러그인 시스템, 메모리 관리, 프로덕션 인프라 |

통합된 Agent Framework는 다음을 제공합니다:

- **A2A (Agent-to-Agent) 프로토콜 네이티브 지원**: Google이 주도하는 A2A 표준을 1등 시민으로 구현
- **MCP (Model Context Protocol) 네이티브 지원**: Anthropic의 MCP를 통해 외부 데이터/도구 연결
- **OpenAI Agents SDK 호환**: OpenAI 생태계와의 원활한 마이그레이션 경로

#### Azure AI Foundry Agent Service (GA)

Azure AI Foundry는 Microsoft의 ** 관리형 AI 플랫폼** 이며, Agent Service는 그 위에서 Agent를 빌드하고 배포하는 서비스입니다.

| 기능 | 설명 |
|------|------|
| ** 모델 카탈로그**| OpenAI GPT-4o, Claude, Llama, Phi, Mistral 등 1,800+ 모델 |
| **A2A + MCP**| 두 프로토콜을 모두 GA 수준으로 지원 |
| **Prompt Shields**| 프롬프트 인젝션 공격 자동 탐지 및 차단 |
| **Content Safety**| 유해 콘텐츠 필터링 (8개 카테고리) |
| **Tracing & Evaluation**| OpenTelemetry 기반 Agent 실행 추적, 자동 평가 |

#### Copilot Studio 2025

Copilot Studio는 Microsoft의 ** 로우코드/노코드 Agent 빌더** 로, 비개발자가 Agent를 만들고 운영할 수 있는 플랫폼입니다.

| 기능 | 설명 |
|------|------|
| ** 멀티에이전트 오케스트레이션**| 여러 Copilot Agent를 하나의 워크플로로 조합 |
| ** 자율형 에이전트**| 트리거 기반으로 자동 실행되는 Agent (이메일 수신 시, 데이터 변경 시 등) |
| **Microsoft 365 통합**| Teams, Outlook, SharePoint, Dynamics 365와 네이티브 연결 |
| ** 커넥터 생태계**| 1,400+ 사전 구축 커넥터 (SAP, Salesforce, ServiceNow 등) |

{% hint style="warning" %}
**Copilot Studio의 포지션**: Copilot Studio는 "시민 개발자"를 타겟으로 합니다. 프로 개발자는 Agent Framework + Azure AI Foundry를 사용하고, 비즈니스 사용자는 Copilot Studio를 사용하는 이원 전략입니다. Databricks의 Agent Bricks (노코드) vs. AI Dev Kit (프로코드) 이원 전략과 유사합니다.
{% endhint %}

#### "Open Agentic Web" 전략

Microsoft는 Agent 생태계의 ** 표준화와 상호 운용성** 을 핵심 전략으로 내세우고 있습니다.

- **A2A 얼리 어답터**: Google이 주도하는 A2A 프로토콜의 초기 지지자이자 구현자
- **MCP 네이티브 지원**: Windows, VS Code, Copilot Studio 등 전 제품군에 MCP 통합
- **NLWeb**: 웹사이트가 자연어로 쿼리 가능한 Agent-ready 엔드포인트를 노출하는 프로토콜 제안

### 2.3 멀티에이전트 아키텍처

Microsoft의 멀티에이전트 모델은 "**Agent Network**" 패러다임입니다.

| 계층 | 구성 요소 | 설명 |
|------|----------|------|
| ** 오케스트레이터**| Copilot Studio | 전체 Agent Network 관리 |
| ** 내부 Agent**| HR Agent (Dynamics), Finance Agent, IT Support Agent | Microsoft 생태계 기반 전문 Agent |
| ** 통신 계층**| A2A Protocol Layer | 내부/외부 Agent 간 표준 통신 |
| ** 외부 Agent**| 외부 Agent, 파트너 Agent, 고객 Agent | Salesforce, SAP 등 외부 Agent와 동일 프로토콜로 통신 |

핵심은 ** 내부 Agent와 외부 Agent가 동일한 프로토콜(A2A)로 통신** 한다는 점입니다. 자사 Copilot뿐 아니라 Salesforce, SAP, 파트너사의 Agent도 동일한 네트워크에 참여할 수 있습니다.

### 2.4 차별점 요약

- **SaaS 생태계 통합**: Microsoft 365, Dynamics 365, GitHub, LinkedIn -- 엔터프라이즈 워크플로 전반을 커버
- **A2A + MCP 이중 프로토콜**: Agent 간 통신(A2A)과 도구 접근(MCP)을 모두 1등 시민으로 지원
- **AutoGen + Semantic Kernel 통합**: 연구 혁신과 엔터프라이즈 안정성을 하나의 프레임워크에
- ** 로우코드 경로**: Copilot Studio를 통해 비개발자도 Agent 구축 가능
- **OpenAI 파트너십**: GPT-4o, o1 등 최신 모델에 가장 먼저 접근

### 2.5 Databricks 연동 시사점

{% hint style="info" %}
**Databricks on Azure 고객이라면**:
- **Azure AI Foundry + Databricks Agent Bricks**: Foundry의 모델 카탈로그에서 모델을 선택하고, Databricks Agent Bricks에서 Agent를 빌드하는 조합이 최적
- **Copilot Studio → Databricks Genie Agent**: Copilot Studio에서 Genie Agent를 외부 Agent로 호출하여, 자연어 데이터 분석을 Microsoft 365 워크플로에 내장
- **Unity Catalog + Purview**: 데이터 거버넌스를 Databricks Unity Catalog와 Microsoft Purview 양쪽에서 통합 관리
- **Mosaic AI Gateway + Azure OpenAI**: Azure OpenAI 엔드포인트를 Gateway의 External Model로 등록하여 비용/성능 모니터링 통합
{% endhint %}

---

## 3. Meta -- "오픈소스 Agent 민주화"

### 3.1 전략 개요

Meta의 전략은 명확합니다: "** 최고 수준의 오픈소스 모델과 도구를 제공하여, Agent 생태계의 표준이 된다.**" 클라우드 서비스 매출이 아닌, 오픈소스를 통한 생태계 장악과 자사 서비스(Instagram, WhatsApp, Workplace) 연동이 핵심 수익 모델입니다.

{% hint style="success" %}
** 핵심 메시지**: "가장 좋은 AI 모델은 누구나 사용할 수 있어야 한다. 오픈소스는 선의가 아니라 전략이다 -- 개발자 생태계를 장악하면 플랫폼이 된다."
{% endhint %}

### 3.2 핵심 제품 스택

#### Llama 4 모델 패밀리

Llama 4는 Meta의 최신 오픈소스 LLM 패밀리로, **Mixture of Experts (MoE)** 아키텍처를 전면 채택했습니다.

| 모델 | 전체 파라미터 | 활성 파라미터 | 컨텍스트 | 특징 |
|------|------------|------------|---------|------|
| **Llama 4 Scout**| 109B | 17B | **10M 토큰**| 초대용량 컨텍스트, 효율적 추론 |
| **Llama 4 Maverick**| 400B | 약 100B | **1M 토큰**| GPT-4o 급 성능, 오픈소스 최강 |

{% hint style="info" %}
**MoE(Mixture of Experts) 아키텍처의 의미**:

Scout의 경우 전체 109B 파라미터 중 매 토큰마다 17B만 활성화됩니다. 이는 다음을 의미합니다:
- ** 추론 비용**: 17B 모델 수준의 GPU 요구량으로 109B 수준의 지식을 활용
- **Agent 시나리오**: 비용 효율이 극도로 중요한 대규모 Agent 배포에 적합
- **10M 컨텍스트**: 전체 코드베이스나 수백 페이지 문서를 한 번에 처리 가능

Maverick은 반대로 최고 성능을 추구합니다. 400B 규모로 GPT-4o와 직접 경쟁하며, 1M 컨텍스트로 복잡한 Agent 추론을 지원합니다.
{% endhint %}

#### Llama Stack

Llama Stack은 Meta가 제공하는 **Agent 빌딩을 위한 통합 API 레이어** 입니다. 모델만 오픈소스하는 것이 아니라, Agent 구축에 필요한 전체 스택을 표준화합니다.

| API 카테고리 | 포함 기능 |
|-------------|----------|
| **Inference**| 텍스트 생성, Tool Calling, Structured Output |
| **Safety**| 입력/출력 필터링, Llama Guard 통합 |
| **Memory**| 벡터 스토어, 대화 히스토리, 장기 기억 |
| **Agents**| Agent 루프, 도구 실행, 멀티턴 관리 |
| **Evaluation**| 자동 평가, 벤치마크 실행 |
| **Post-training**| Fine-tuning, RLHF, DPO |

```python
# Llama Stack Agent 예시
from llama_stack_client import LlamaStackClient

client = LlamaStackClient(base_url="http://localhost:5000")

# Agent 생성
agent = client.agents.create(
    agent_config={
        "model": "Llama4-Scout-109B-MoE",
        "instructions": "당신은 데이터 분석 전문가입니다.",
        "tools": [
            {"type": "code_interpreter"},
            {"type": "brave_search"},
            {"type": "function", "function": custom_tool}
        ],
        "tool_choice": "auto",
        "max_infer_iters": 10  # 최대 추론 반복 횟수
    }
)
```

#### 오픈소스 전략의 의미

Meta의 오픈소스 전략은 단순한 모델 공개가 아닙니다.

| 계층 | 오픈소스 여부 | 설명 |
|------|-------------|------|
| ** 모델 가중치**| 공개 (Llama License) | 상업적 사용 가능, 7억 MAU 이상 시 라이선스 필요 |
| ** 학습 코드**| 일부 공개 | 학습 레시피, 데이터 처리 파이프라인 |
| ** 평가 프레임워크**| 공개 | Llama Stack Evals |
| ** 안전 도구**| 공개 | Llama Guard, CyberSecEval, Purple Llama |
| **Agent 프레임워크**| 공개 | Llama Stack |

{% hint style="warning" %}
**Llama 라이선스 주의사항**: Llama 4는 "오픈소스"로 불리지만, 엄밀히는 ** 오픈 웨이트(Open Weight)** 모델입니다. 월간 활성 사용자 7억 명 이상인 서비스에서 사용하려면 별도 라이선스가 필요합니다. 또한, Llama 출력으로 다른 LLM을 학습시키는 것은 라이선스 위반입니다.
{% endhint %}

### 3.3 멀티에이전트 아키텍처

Meta는 AWS나 Microsoft처럼 자체 관리형 오케스트레이션 서비스를 제공하지 않습니다. 대신 Llama Stack의 Agent API를 통해 ** 프레임워크 수준의 멀티에이전트** 를 지원합니다.

실제 프로덕션 멀티에이전트 배포는 다음 조합으로 이루어집니다:

- **Llama 4 모델**+ **LangGraph/CrewAI/Strands**(오케스트레이션) + ** 클라우드 서비스**(인프라)
- 즉, Meta는 "두뇌(모델)"를 제공하고, "몸(인프라)"은 클라우드 벤더가 제공하는 구조

### 3.4 차별점 요약

- ** 오픈 웨이트 최강 모델**: Llama 4 Maverick은 오픈소스 모델 중 최고 성능
- ** 극한 비용 효율**: Scout의 MoE 아키텍처로 17B 활성 파라미터에 109B 지식 활용
- **10M 컨텍스트**: 오픈소스 모델 중 최대 컨텍스트 윈도우
- ** 벤더 종속 없음**: 어떤 클라우드, 어떤 프레임워크에서든 사용 가능
- ** 자체 호스팅 가능**: 민감 데이터를 클라우드 밖에서 처리해야 하는 규제 환경에 적합

### 3.5 Databricks 연동 시사점

{% hint style="info" %}
**Databricks에서 Llama 4를 활용하려면**:
- **Mosaic AI Gateway**: Llama 4 모델을 Databricks Model Serving에 배포하고, Gateway에서 통합 관리. 자체 호스팅으로 데이터 주권 확보
- **Foundation Model API**: Databricks가 관리하는 Llama 4 엔드포인트를 바로 사용 (Pay-per-token)
- **Fine-tuning**: Databricks에서 Llama 4를 도메인 특화 데이터로 Fine-tuning 가능 (PEFT, QLoRA)
- **Agent Bricks + Llama 4**: Agent Bricks에서 Serving Endpoint로 배포된 Llama 4를 백엔드 모델로 사용
- ** 비용 최적화**: Scout 모델을 고빈도/저복잡도 Agent에, Maverick을 저빈도/고복잡도 Agent에 배치하는 티어드 전략
{% endhint %}

---

## 4. 종합 비교

{% hint style="info" %}
Databricks의 Agent 전략은 별도 페이지에서 심층적으로 다룹니다: [Databricks의 AI Agent 전략](databricks.md)
{% endhint %}

### 4.1 벤더별 전략 비교 테이블

| 비교 항목 | AWS | Microsoft | Meta | Databricks |
|----------|-----|-----------|------|-----------|
| ** 전략 키워드**| 풀스택 빌딩 블록 | 오픈 에이전틱 웹 | 오픈소스 민주화 | 데이터 중심 Agent |
| ** 자체 모델**| Nova 2 (Pro/Lite/Sonic) | 없음 (OpenAI 파트너십) | Llama 4 (Scout/Maverick) | DBRX (보조), 외부 모델 중심 |
| **Agent 빌더**| Bedrock Agents | Azure AI Foundry Agent | Llama Stack | Agent Bricks |
| ** 오케스트레이션**| Supervisor/Routing Mode | Copilot Studio | 프레임워크 위임 | Supervisor Agent |
| ** 운영 플랫폼**| AgentCore | Azure AI Foundry | 없음 (클라우드 위임) | Model Serving + Gateway |
| ** 안전장치**| Guardrails (Automated Reasoning) | Prompt Shields + Content Safety | Llama Guard | Unity Catalog Guardrails |
| ** 정책 엔진**| Cedar (선언적) | Azure RBAC | 없음 | Unity Catalog ACL |
| ** 코딩 도구**| Q Developer, Kiro IDE | GitHub Copilot | 없음 | Genie Code, AI Dev Kit |
| ** 프레임워크**| Strands SDK (오픈소스) | Agent Framework (AutoGen+SK) | Llama Stack (오픈소스) | Agent Framework (MLflow 통합) |
| ** 프로토콜**| MCP 지원 | A2A + MCP | 표준 따름 | MCP 지원 |
| ** 멀티클라우드**| AWS only | Azure 중심 | 클라우드 무관 | AWS, Azure, GCP |
| ** 데이터 거버넌스**| Lake Formation | Purview | 없음 | Unity Catalog |
| ** 비용 모델**| Pay-per-use | Pay-per-use | 자체 호스팅 가능 | DBU 기반 |
| ** 주요 타겟**| AWS 올인 고객 | Microsoft 365 + Azure 고객 | 오픈소스 선호, 자체 인프라 보유 | 데이터 레이크하우스 고객 |

### 4.2 시나리오별 최적 조합

| 시나리오 | 권장 조합 | 이유 |
|---------|----------|------|
| **AWS 기반 엔터프라이즈**| Bedrock Agents + Databricks Agent Bricks + MLflow | AWS 인프라 활용 + 데이터 거버넌스 통합 |
| **Azure 기반 엔터프라이즈**| Azure AI Foundry + Databricks + Copilot Studio | Microsoft 365 연동 + 데이터 레이크하우스 |
| ** 비용 최적화 우선**| Llama 4 Scout (Databricks 호스팅) + Agent Bricks | MoE로 추론 비용 절감 + 자체 호스팅 |
| ** 최고 성능 우선**| Claude/GPT-4o (Gateway 경유) + Agent Bricks | 최고 모델 + 자동 Fallback |
| ** 데이터 규제 환경**| Llama 4 (온프레미스) + Databricks (VPC 내) | 데이터 주권 + 모델 자체 호스팅 |
| ** 멀티클라우드**| Databricks (멀티클라우드) + Mosaic AI Gateway | 클라우드 간 일관된 Agent 경험 |

### 4.3 기능 계층별 비교

| 계층 | AWS | Microsoft | Meta | Databricks |
|------|-----|-----------|------|-----------|
| ** 모델 접근**| Bedrock (멀티모델) | AI Foundry (1,800+) | Llama 직접 | Gateway (무제한) |
| **RAG/검색**| Knowledge Bases, GraphRAG | AI Search | Llama Stack Memory | Vector Search, UC 함수 |
| ** 멀티에이전트**| Supervisor/Routing | Copilot Studio 오케스트레이션 | 프레임워크 의존 | Supervisor Agent |
| ** 평가**| AgentCore Evaluations | AI Foundry Evaluation | Llama Stack Evals | MLflow 3.0 GenAI Metrics |
| ** 모니터링**| CloudWatch + AgentCore | Azure Monitor + Foundry | 자체 구축 필요 | MLflow Trace + Lakehouse Monitor |
| ** 거버넌스**| IAM + Cedar | Entra ID + Purview | 자체 구축 필요 | Unity Catalog (데이터+모델+Agent) |

---

## 5. 고객 FAQ

### Q1: "우리는 AWS를 쓰는데, Bedrock Agents만으로 충분한가요?"

{% hint style="info" %}
Bedrock Agents는 Agent 오케스트레이션에 우수하지만, ** 데이터 거버넌스와 평가 자동화** 에서 한계가 있습니다. 권장 조합:
- **Agent 빌드/오케스트레이션**: Bedrock Agents 또는 Databricks Agent Bricks
- ** 데이터 거버넌스**: Databricks Unity Catalog
- ** 모니터링/평가**: MLflow 3.0
- ** 모델 관리**: Mosaic AI Gateway (Bedrock 모델 포함)
{% endhint %}

### Q2: "Llama 4를 자체 호스팅하면 비용이 정말 절감되나요?"

{% hint style="info" %}
** 상황에 따라 다릅니다.**
- ** 고빈도 호출**(일 100만+ 요청): 자체 호스팅이 API 비용 대비 50-70% 절감 가능
- ** 저빈도 호출**(일 1만 이하): API(Pay-per-token)가 더 경제적. GPU 유휴 비용 발생
- ** 권장**: Databricks Model Serving에 Llama 4를 배포하면 서버리스 스케일링으로 유휴 비용을 최소화할 수 있습니다. Scout(17B 활성)은 단일 A100에서도 추론 가능합니다.
{% endhint %}

### Q3: "Microsoft Copilot Studio와 Databricks Agent Bricks 중 무엇을 써야 하나요?"

{% hint style="info" %}
** 타겟 사용자가 다릅니다.**
- **Copilot Studio**: 비개발자가 Microsoft 365 워크플로 내에서 간단한 Agent를 만들 때
- **Agent Bricks**: 데이터 팀이 데이터 레이크하우스의 데이터를 활용하는 Agent를 만들 때

가장 좋은 전략은 ** 양쪽 모두 사용** 하고, Copilot Studio의 Agent가 Databricks Genie Agent를 A2A/MCP로 호출하는 구조입니다.
{% endhint %}

### Q4: "A2A vs MCP -- 우리에게 어떤 프로토콜이 필요한가요?"

{% hint style="info" %}
둘은 ** 경쟁이 아니라 보완 관계** 입니다.
- **MCP**: Agent가 ** 도구/데이터** 에 접근하는 프로토콜 (Agent → Tool)
- **A2A**: Agent가 ** 다른 Agent** 와 통신하는 프로토콜 (Agent → Agent)

대부분의 엔터프라이즈 Agent에는 **MCP가 먼저 필요** 합니다. A2A는 조직 간 Agent 연동이 필요할 때 도입하세요.
{% endhint %}

### Q5: "AWS Guardrails의 Automated Reasoning이 정말 99% 정확한가요?"

{% hint style="info" %}
AWS가 발표한 99% 수치는 ** 형식 검증(Formal Verification)** 이 적용 가능한 도메인(수학, 논리, 정책 규칙)에서의 정확도입니다. 자연어 추론 전반에 대한 수치가 아닙니다.

- ** 적합**: 보험 약관 해석, 대출 적격 여부 판단, 세금 계산 등 규칙 기반 추론
- ** 한계**: 창의적 글쓰기, 감정 분석, 주관적 판단 등에는 적용 불가

Databricks 환경에서는 MLflow 3.0의 GenAI Metrics + Bedrock Guardrails를 ** 조합** 하여 다층적 안전장치를 구축하는 것을 권장합니다.
{% endhint %}

### Q6: "멀티클라우드 환경에서 Agent를 어떻게 통합 관리하나요?"

{% hint style="info" %}
Databricks의 멀티클라우드 아키텍처가 핵심입니다:

1. **Mosaic AI Gateway**: AWS Bedrock, Azure OpenAI, 자체 호스팅 모델을 하나의 엔드포인트로 통합
2. **Unity Catalog**: 클라우드 간 데이터 거버넌스 일관성 유지
3. **MLflow 3.0**: 클라우드 무관하게 Agent 추적/평가 통합
4. **Agent Bricks**: 동일한 Agent 정의를 AWS/Azure/GCP 어디서든 배포
{% endhint %}

---

## 6. 참고 자료

### AWS
- [Amazon Bedrock Agents 공식 문서](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Amazon AgentCore 소개](https://aws.amazon.com/agentcore/)
- [Strands Agents SDK GitHub](https://github.com/strands-agents/sdk-python)
- [Amazon Nova 모델 카드](https://aws.amazon.com/ai/generative-ai/nova/)
- [Guardrails for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)

### Microsoft
- [Azure AI Foundry Agent Service](https://learn.microsoft.com/azure/ai-services/agents/)
- [Microsoft Copilot Studio](https://www.microsoft.com/copilot/copilot-studio)
- [AutoGen GitHub](https://github.com/microsoft/autogen)
- [Semantic Kernel GitHub](https://github.com/microsoft/semantic-kernel)

### Meta
- [Llama 4 모델 카드](https://ai.meta.com/llama/)
- [Llama Stack GitHub](https://github.com/meta-llama/llama-stack)
- [Llama Guard](https://ai.meta.com/research/publications/llama-guard/)

### Databricks
- [Agent Bricks 문서](https://docs.databricks.com/en/generative-ai/agent-bricks/index.html)
- [Mosaic AI Gateway](https://docs.databricks.com/en/generative-ai/external-models/index.html)
- [MLflow 3.0 GenAI](https://mlflow.org/docs/latest/genai/index.html)
- [Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)

### 프로토콜 & 표준
- [A2A (Agent-to-Agent) 프로토콜](https://google.github.io/A2A/)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
