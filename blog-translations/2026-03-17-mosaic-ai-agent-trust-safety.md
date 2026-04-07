---
original_title: "Announcing Mosaic AI Agent Framework and Agent Evaluation"
authors: "Eric Peter, Akhil Gupta, Mani Parkhe, Alkis Polyzotis, Chenen Liang, Maheswaran Venkatachalam, Michael Carbin, Niall Turbitt"
date: "2024-07-02"
category: "Data Science and ML"
original_url: "https://www.databricks.com/blog/announcing-mosaic-ai-agent-framework-and-agent-evaluation"
translated_date: "2026-04-07"
note: "요청한 원본 URL(https://www.databricks.com/blog/how-mosaic-ai-agent-framework-enables-trust-and-safety-agentic-systems)은 404를 반환합니다. 동일 주제의 공식 Databricks 블로그 포스트 2편을 번역했습니다: (1) Mosaic AI Agent Framework & Agent Evaluation 발표 포스트, (2) Agent Bricks AI Gateway 보안·거버넌스 발표 포스트(2024-09-09, 저자: Ahmed Bilal, Kasey Uhlenhuth, Archika Dogra)."
---

> **원문**: [Announcing Mosaic AI Agent Framework and Agent Evaluation](https://www.databricks.com/blog/announcing-mosaic-ai-agent-framework-and-agent-evaluation)

# Mosaic AI Agent Framework와 Agent Evaluation 발표: 신뢰할 수 있는 에이전틱 시스템을 위한 안전 및 거버넌스

{% hint style="info" %}
**번역 참고**: 요청한 원본 URL은 현재 접근 불가(404) 상태입니다. 동일 주제를 다루는 공식 Databricks 블로그 포스트 2편을 함께 번역했습니다. (1) **Mosaic AI Agent Framework & Agent Evaluation 발표** (2024-07-02), (2) **Agent Bricks AI Gateway의 고급 보안 및 거버넌스 발표** (2024-09-09).
{% endhint %}

---

## 파트 1 — Mosaic AI Agent Framework와 Agent Evaluation 발표

**프로덕션 품질의 에이전틱 및 Retrieval Augmented Generation 앱 구축**

**저자**: Eric Peter, Akhil Gupta, Mani Parkhe, Alkis Polyzotis, Chenen Liang, Maheswaran Venkatachalam, Michael Carbin, Niall Turbitt
**게시일**: 2024년 7월 2일

---

Databricks는 Data + AI Summit 2024에서 **Mosaic AI Agent Framework** 와 **Agent Evaluation** 의 퍼블릭 프리뷰를 **Generative AI Cookbook** 과 함께 발표했습니다.

이 도구들은 개발자들이 Databricks Data Intelligence Platform 내에서 고품질의 에이전틱(Agentic) 및 검색 증강 생성(RAG, Retrieval Augmented Generation) 애플리케이션을 구축하고 배포할 수 있도록 설계되었습니다.

### 고품질 생성형 AI 애플리케이션 구축의 과제

GenAI 애플리케이션의 개념 증명(PoC)을 구축하는 것은 비교적 간단하지만, 고품질 애플리케이션을 실제로 제공하는 것은 많은 고객들에게 큰 도전으로 증명되었습니다. 고객 대면 애플리케이션에 요구되는 품질 기준을 충족하려면 AI 출력이 **정확하고(accurate), 안전하며(safe), 거버넌스를 갖추어야(governed)** 합니다. 이 수준의 품질에 도달하기 위해 개발자들은 다음과 같은 어려움을 겪습니다:

- 애플리케이션의 품질을 평가하기 위한 올바른 지표 선택
- 애플리케이션 품질을 측정하기 위한 효율적인 사람의 피드백 수집
- 품질 문제의 근본 원인 파악
- 프로덕션 배포 전 애플리케이션 품질을 빠르게 개선하기 위한 반복(iteration)

### Mosaic AI Agent Framework와 Agent Evaluation 소개

Databricks AI Research 팀과의 긴밀한 협업을 통해 구축된 **Agent Framework** 와 **Agent Evaluation** 은 이러한 과제들을 해결하기 위해 특별히 설계된 여러 기능을 제공합니다:

**빠른 사람 피드백 수집** — Agent Evaluation을 통해 GenAI 애플리케이션의 고품질 답변이 어떤 모습이어야 하는지 정의할 수 있습니다. Databricks 사용자가 아닌 조직 내 도메인 전문가들을 초대해 애플리케이션 응답의 품질을 검토하고 피드백을 제공하도록 할 수 있습니다.

**GenAI 애플리케이션의 손쉬운 평가** — Agent Evaluation은 Databricks AI Research와 협력하여 개발된 지표(metrics) 모음을 제공하여 애플리케이션의 품질을 측정합니다. 응답과 사람의 피드백을 자동으로 평가 테이블에 기록하고 결과를 빠르게 분석하여 잠재적인 품질 문제를 식별할 수 있습니다. 시스템 제공 AI 심사위원(AI judges)들은 정확성, 환각(hallucination), 유해성(harmfulness), 유용성(helpfulness) 등 일반적인 기준에 따라 이러한 응답들을 평가하며, 품질 문제의 근본 원인을 파악합니다. 이 심사위원들은 도메인 전문가의 피드백을 사용하여 보정되지만, 사람의 레이블 없이도 품질을 측정할 수 있습니다.

그런 다음 Agent Framework를 사용하여 애플리케이션의 다양한 구성을 실험하고 조정함으로써 이러한 품질 문제를 해결하고 각 변경 사항이 앱 품질에 미치는 영향을 측정할 수 있습니다. 품질 임계값에 도달하면 Agent Evaluation의 비용 및 지연(latency) 지표를 사용하여 품질/비용/지연 간의 최적 트레이드오프를 결정할 수 있습니다.

**빠른 엔드투엔드 개발 워크플로우** — Agent Framework는 MLflow와 통합되어 개발자들이 `log_model` 및 `mlflow.evaluate`와 같은 표준 MLflow API를 사용하여 GenAI 애플리케이션을 기록하고 품질을 평가할 수 있게 합니다. 품질에 만족하면 개발자들은 MLflow를 사용하여 이러한 애플리케이션을 프로덕션에 배포하고 사용자의 피드백을 받아 품질을 더욱 향상시킬 수 있습니다. Agent Framework와 Agent Evaluation은 MLflow 및 Data Intelligence Platform과 통합되어 GenAI 애플리케이션을 구축하고 배포하는 완전히 포장된 경로를 제공합니다.

**앱 수명 주기 관리(App Lifecycle Management)** — Agent Framework는 권한 관리부터 Databricks Model Serving을 통한 배포에 이르기까지 에이전틱 애플리케이션의 수명 주기를 관리하기 위한 간소화된 SDK를 제공합니다.

Agent Framework와 Agent Evaluation을 사용하여 고품질 애플리케이션 구축을 시작하는 데 도움이 되도록, **Generative AI Cookbook** 은 앱을 PoC에서 프로덕션으로 가져가기 위한 모든 단계를 보여주는 확정적인 방법론 가이드이며, 애플리케이션 품질을 높일 수 있는 가장 중요한 구성 옵션 및 접근 방식을 설명합니다.

### 고품질 RAG 에이전트 구축하기

이 새로운 기능들을 이해하기 위해, Agent Framework를 사용하여 고품질 에이전틱 애플리케이션을 구축하고 Agent Evaluation을 사용하여 품질을 개선하는 예를 살펴보겠습니다.

이 예시에서 우리는 사전 생성된 벡터 인덱스에서 관련 청크를 검색하고 이를 쿼리에 대한 응답으로 요약하는 간단한 RAG 애플리케이션을 구축하고 배포할 것입니다. LangChain을 포함한 어떤 프레임워크나 네이티브 Python 코드를 사용하여 RAG 애플리케이션을 구축할 수 있지만, 이 예에서는 LangChain을 사용합니다.

**1단계: MLflow 트레이싱 활성화**

먼저 MLflow를 활용하여 트레이싱(tracing)을 활성화하고 애플리케이션을 배포합니다. 이는 Agent Framework가 트레이스와 애플리케이션을 관찰 및 디버깅하기 쉬운 방법을 제공할 수 있도록 하는 세 줄의 간단한 코드를 추가하여 수행할 수 있습니다.

![MLflow 트레이싱은 개발 및 프로덕션 중 애플리케이션에 대한 가시성을 제공합니다](https://www.databricks.com/sites/default/files/inline-images/image2_2.gif)

**2단계: Unity Catalog에 등록 및 PoC 배포**

다음 단계는 GenAI 애플리케이션을 Unity Catalog에 등록하고 Agent Evaluation의 리뷰 애플리케이션을 사용하여 이해관계자들의 피드백을 받기 위한 개념 증명(PoC)으로 배포하는 것입니다. 브라우저 링크를 이해관계자들과 공유하면 즉시 피드백 수집을 시작할 수 있습니다. 피드백은 Unity Catalog의 델타 테이블에 저장되며 평가 데이터셋 구축에 사용될 수 있습니다.

![리뷰 애플리케이션을 사용하여 PoC에 대한 이해관계자 피드백 수집](https://www.databricks.com/sites/default/files/inline-images/image3_1.gif)

{% hint style="info" %}
**고객 사례 — Corning**: "우리는 수십만 개의 미국 특허청 데이터를 포함한 문서들을 색인화하기 위해 Databricks Mosaic AI Agent Framework를 사용하여 AI 연구 보조 도구를 구축했습니다. LLM 기반 보조 도구가 높은 정확도로 질문에 답변하는 것이 우리에게는 매우 중요했습니다. Databricks Data Intelligence Platform을 활용함으로써 검색 속도, 응답 품질, 정확도를 크게 향상시켰습니다."
— Denis Kamotsky, Principal Software Engineer, Corning
{% endhint %}

**3단계: AI 심사위원으로 품질 평가**

평가 데이터셋 구축을 위한 피드백을 받기 시작하면 Agent Evaluation과 내장된 AI 심사위원을 사용하여 다음과 같은 사전 구축된 지표를 기반으로 각 응답을 품질 기준에 따라 검토할 수 있습니다:

- **정답 정확성(Answer Correctness)** — 앱의 응답이 정확한가?
- **근거성(Groundedness)** — 앱의 응답이 검색된 데이터에 기반하는가, 아니면 환각하고 있는가?
- **검색 관련성(Retrieval Relevance)** — 검색된 데이터가 사용자의 질문과 관련이 있는가?
- **답변 관련성(Answer Relevance)** — 앱의 응답이 사용자의 질문에 적합한가?
- **안전성(Safety)** — 앱의 응답에 유해한 콘텐츠가 포함되어 있는가?

집계된 지표와 평가 세트의 각 질문에 대한 평가는 MLflow에 기록됩니다. 각 LLM 기반 판단에는 그 이유에 대한 서면 근거가 뒷받침됩니다. 이 평가 결과를 사용하여 품질 문제의 근본 원인을 파악할 수 있습니다.

![Agent Evaluation의 집계 지표를 MLflow 내에서 확인](https://www.databricks.com/sites/default/files/inline-images/image4_4.gif)

평가 데이터셋의 각 개별 레코드를 검사하여 무슨 일이 일어나고 있는지 더 잘 이해하거나 MLflow 트레이스를 사용하여 잠재적인 품질 문제를 파악할 수도 있습니다.

![평가 세트의 각 개별 레코드를 검사하여 상황 파악](https://www.databricks.com/sites/default/files/inline-images/image1_5.gif)

{% hint style="info" %}
**고객 사례 — Lippert**: "Mosaic AI Agent Framework는 우리에게 게임 체인저였습니다. GenAI 애플리케이션의 결과를 평가하고 데이터 소스에 대한 완전한 제어를 유지하면서 출력의 정확도를 입증할 수 있었습니다. Databricks Data Intelligence Platform 덕분에 프로덕션 배포에 자신감을 갖게 되었습니다."
— Kenan Colson, VP Data & AI, Lippert
{% endhint %}

**4단계: 프로덕션 배포**

품질을 반복적으로 개선하고 만족스러운 수준에 도달하면, 애플리케이션이 이미 Unity Catalog에 등록되어 있기 때문에 최소한의 노력으로 프로덕션 워크스페이스에 배포할 수 있습니다.

{% hint style="info" %}
**고객 사례 — Burberry**: "Mosaic AI Agent Framework를 통해 모든 개인 데이터가 우리 통제 하에 있다는 확신 속에서 강화된 LLM을 빠르게 실험할 수 있었습니다. MLflow 및 Model Serving과의 원활한 통합으로 ML 엔지니어링 팀이 최소한의 복잡성으로 PoC에서 프로덕션으로 확장할 수 있었습니다."
— Ben Halsall, Analytics Director, Burberry
{% endhint %}

### 거버넌스, 추적성, 안전성의 통합

이러한 기능들은 거버넌스를 위해 **Unity Catalog** 와, 계보(lineage) 및 메타데이터 관리를 위해 **MLflow** 와, 안전성을 위해 **LLM Guardrails** 와 긴밀하게 통합되어 있습니다. 거버넌스와 가드레일이 적용되면 유해한 응답을 방지하고 애플리케이션이 조직의 정책을 따르도록 보장할 수 있습니다.

{% hint style="info" %}
**고객 사례 — FordDirect**: "Databricks Mosaic AI Agent Framework를 통해 RAG를 사용하는 생성형 AI 솔루션에 우리의 독자적인 데이터와 문서를 통합할 수 있었습니다. Mosaic AI와 Databricks Delta Tables 및 Unity Catalog의 통합으로 배포된 모델을 건드리지 않고도 소스 데이터가 업데이트될 때 벡터 인덱스를 실시간으로 원활하게 유지할 수 있었습니다."
— Tom Thomas, VP of Analytics, FordDirect
{% endhint %}

### 가격 책정

- **Agent Evaluation** — Judge 요청당 가격 책정
- **Databricks Model Serving** — Databricks Model Serving 요율에 따라 가격 책정

### 다음 단계

Agent Framework와 Agent Evaluation은 프로덕션 품질의 에이전틱 및 RAG 애플리케이션을 구축하는 최선의 방법입니다. 시작하려면 다음 리소스를 참조하세요:

- [Agent Framework 문서 (AWS | Azure)](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
- [Agent Framework 및 Agent Evaluation 데모 노트북](https://www.databricks.com/resources/demos/tutorials/data-science-and-ai/lakehouse-ai-deploy-your-llm-chatbot)
- [Generative AI Cookbook](https://ai-cookbook.io/)

---

## 파트 2 — Agent Bricks AI Gateway의 고급 보안 및 거버넌스 발표

**엔터프라이즈 전체의 모든 GenAI 모델 지원**

**저자**: Ahmed Bilal, Kasey Uhlenhuth, Archika Dogra
**게시일**: 2024년 9월 9일
**원문**: [https://www.databricks.com/blog/new-updates-mosaic-ai-gateway-bring-security-and-governance-genai-models](https://www.databricks.com/blog/new-updates-mosaic-ai-gateway-bring-security-and-governance-genai-models)

---

우리는 고객들이 더 큰 단순성, 보안, 거버넌스로 AI 이니셔티브를 가속화할 수 있도록 설계된 **Agent Bricks AI Gateway** 의 강력한 새 기능들을 소개하게 되어 기쁩니다.

![Agent Bricks AI Gateway 보안 및 거버넌스 개요](https://www.databricks.com/sites/default/files/2025-01/new-updates-mosaic-ai-gateway-bring-security-and-governance-genai-models.png)

### 엔터프라이즈 AI의 보안·컴플라이언스 과제

기업들이 AI 솔루션 도입에 박차를 가하면서 보안, 컴플라이언스, 비용 관리가 점점 더 어려워지고 있습니다. 이것이 바로 우리가 지난해 **Agent Bricks AI Gateway** 를 출시한 이유입니다. 현재 많은 조직들이 OpenAI GPT, Anthropic Claude, Meta Llama 모델 등 다양한 모델의 AI 트래픽을 관리하는 데 이 Gateway를 사용하고 있습니다.

이번 업데이트는 사용량 추적, 페이로드 로깅, 가드레일(guardrails)을 위한 고급 기능을 도입하여, 기업들이 Databricks Data Intelligence Platform 내의 모든 AI 모델에 보안과 거버넌스를 적용할 수 있게 합니다. 이 릴리스를 통해 **Agent Bricks AI Gateway** 는 가장 민감한 데이터와 트래픽에도 프로덕션 수준의 보안과 거버넌스를 제공합니다.

### Agent Bricks AI Gateway란?

많은 기업들이 복합 AI 시스템(예: RAG, 멀티 에이전트 아키텍처)을 구축하기 위해 다양한 제공업체의 여러 AI 모델을 혼합하여 사용합니다. 그러나 다양한 오픈 모델과 독점 모델을 통합하면서 운영 비효율성, 비용 초과, 잠재적 보안 취약점이라는 과제에 직면하게 됩니다.

**Agent Bricks AI Gateway** 는 AI 트래픽에 접근하고, 관리하고, 보호하기 위한 통합 서비스를 제공함으로써 이러한 과제를 해결합니다. 엔터프라이즈 관리자는 가드레일을 적용하고 AI 사용을 모니터링할 수 있으며, 개발자는 애플리케이션을 빠르게 실험하고 결합하여 프로덕션에 안전하게 배포할 수 있는 간단한 인터페이스를 활용합니다. OMV, Edmunds와 같이 Agent Bricks AI Gateway를 도입한 기업들은 이러한 이점을 직접 경험하고 있습니다.

### Agent Bricks AI Gateway로 할 수 있는 것

#### 모든 AI 모델에 안전하게 접근 (Securely Access Any AI Models)

Agent Bricks AI Gateway는 단일 인터페이스(API, SDK, SQL)를 통해 모든 LLM에 대한 접근을 단순화하여 개발 시간과 통합 비용을 크게 줄입니다. 클라이언트 앱을 변경하지 않고도 독점 모델과 오픈 모델 간에 쉽게 전환할 수 있습니다. Agent Bricks AI Gateway를 차별화하는 것은 전통적인 모델, GenAI 모델, 체인(chains), 에이전트 등 모든 AI 자산에 대한 지원으로, 여러 솔루션의 필요성을 없앤다는 점입니다.

#### 프로덕션 AI 트래픽 모니터링 및 디버깅 (Monitor and Debug Production AI Traffic)

Agent Bricks AI Gateway는 이제 엔드포인트로 유입되고 나가는 모든 트래픽의 사용량과 페이로드 데이터를 Unity Catalog Delta Tables에 캡처합니다. 두 가지 핵심 테이블이 도입됩니다:

- **Endpoint Usage Table**: 이 시스템 테이블은 요청자 세부 정보, 사용 통계, 사용자 정의 메타데이터를 포함하여 계정의 모든 서빙 엔드포인트에 걸친 모든 요청을 기록합니다. 이 데이터는 지출을 최적화하고 ROI를 극대화하는 데 도움이 됩니다. 예를 들어, 실험적 엔드포인트에 요청 제한을 설정하는 데 활용할 수 있습니다.
- **Inference Table**: 이 테이블은 각 서빙 엔드포인트의 원시 입력, 출력, HTTP 상태 코드, 지연 시간을 지속적으로 캡처합니다. 이 데이터를 사용하여 AI 앱 품질을 모니터링하고, 문제를 디버깅하거나, AI 모델을 파인튜닝하기 위한 훈련 코퍼스로도 활용할 수 있습니다.

가장 좋은 점은 모든 데이터가 Unity Catalog에 캡처되어 친숙한 데이터 도구를 사용하여 안전하게 공유하고, 검색하고, 시각화하고, 분석하기 쉽다는 것입니다.

![Agent Bricks AI Gateway 모니터링 및 로깅 화면](https://www.databricks.com/sites/default/files/inline-images/image2_26.png)

#### 사용자와 애플리케이션을 지속적으로 보호 (Continuously Safeguard Users and Applications)

**Agent Bricks AI Gateway** 는 모든 모델 API에 대한 트래픽을 보호하고, 안전 정책을 적용하며, 민감한 정보를 실시간으로 보호하기 위한 포괄적인 가드레일을 포함합니다. 이러한 가드레일에는 다음이 포함됩니다:

- **안전 필터링(Safety Filtering)**: 혐오 발언, 모욕, 성적 콘텐츠, 폭력, 위법 행위 등의 유해 콘텐츠를 필터링합니다.
- **PII 필터(PII Filters)**: 사용자 입력에서 주민등록번호, 신용카드 번호 등 개인 식별 가능 정보(PII)를 포함하는 민감한 콘텐츠가 포함된 요청을 감지하고 차단합니다.
- **키워드 필터(Keyword Filters)**: 비즈니스 및 정책에 맞는 안전하고 관련성 있는 상호작용을 보장하기 위해 애플리케이션에서 원치 않는 주제를 차단합니다.
- **토픽 필터(Topic Filters)**: 관련 없거나 위험한 주제에 대한 응답을 피함으로써 애플리케이션을 훈련된 범위에 집중시켜 책임 위험을 최소화합니다.

이러한 가드레일은 특정 사용 사례와 정책에 맞게 엔드포인트 또는 요청 수준에서 설정할 수 있습니다. 모든 데이터는 Inference Tables에 기록되며, 이를 통해 Lakehouse Monitoring으로 분석하여 시간 경과에 따른 모델 안전성을 추적할 수 있습니다.

![Agent Bricks AI Gateway 가드레일 구성 화면](https://www.databricks.com/sites/default/files/inline-images/image3_27.png)

#### 데이터와 AI를 손쉽게 연결 (Connect AI with Your Data Effortlessly)

Agent Bricks AI Gateway는 Databricks Data Intelligence Platform 위에 구축되어, 기업들이 RAG, 에이전트 워크플로우, 파인튜닝과 같은 기법을 사용하여 LLM을 데이터와 쉽게 연결할 수 있게 합니다. 이를 통해 일반적인 지능을 실행 가능한 데이터 인텔리전스로 변환하는 데 도움을 줍니다.

이미 많은 고객들이 Mosaic AI의 Vector Search를 외부 모델과 함께 사용하여 임베딩을 생성하거나 외부 언어 모델을 활용하여 Databricks 플랫폼에 저장된 데이터를 기반으로 결론을 내리고 있습니다.

### Agent Bricks AI Gateway 시작하기

Agent Bricks AI Gateway의 새로운 모니터링 및 가드레일은 이제 모든 모델 서빙 워크스페이스에서 사용 가능합니다. 몇 번의 클릭만으로 새 외부 모델과 기존 외부 모델에서 Agent Bricks AI Gateway를 활성화할 수 있습니다. 추가 엔드포인트에 대한 지원은 곧 출시될 예정입니다.

**참고 자료:**

- [Agent Bricks AI Gateway 노트북 데모](https://www.databricks.com/resources/demos/tutorials/governance/ai-gateway)
- [Agent Bricks AI Gateway 문서 (AWS | Azure)](https://docs.databricks.com/en/machine-learning/model-serving/api-gateway.html)

---

## 핵심 요약: Mosaic AI Agent Framework가 신뢰와 안전을 가능하게 하는 방법

아래 표는 Mosaic AI Agent Framework가 에이전틱 시스템에서 신뢰와 안전을 구현하는 핵심 메커니즘을 정리한 것입니다.

| 신뢰/안전 레이어 | 구현 방법 | 활용 도구 |
|---|---|---|
| **콘텐츠 안전성** | 유해 콘텐츠 필터링(혐오 발언, 폭력 등) | AI Gateway — Safety Filtering |
| **데이터 프라이버시** | 입출력 단의 PII 감지 및 차단 | AI Gateway — PII Filters |
| **토픽 제어** | 비즈니스 범위 밖의 주제 응답 방지 | AI Gateway — Keyword/Topic Filters |
| **정확성 보장** | AI 심사위원 기반 환각·정확도 자동 평가 | Agent Evaluation — AI Judges |
| **거버넌스** | 모든 모델/에이전트 자산에 대한 통합 접근 제어 | Unity Catalog 통합 |
| **추적성** | 요청별 입출력·상태·지연 전체 기록 | Inference Tables + MLflow 트레이싱 |
| **사람 피드백** | 도메인 전문가의 응답 품질 검토 루프 | Agent Evaluation — Review App |

이 표는 Mosaic AI Agent Framework가 단순한 LLM 래퍼를 넘어, **품질 평가 → 콘텐츠 안전 → 데이터 거버넌스 → 감사 추적** 에 이르는 완전한 신뢰 스택(trust stack)을 제공한다는 것을 보여줍니다. 에이전틱 시스템이 더 많은 자율성을 가질수록 이 레이어들의 중요성은 더욱 커집니다.
