---
original_title: "Introducing Agent Bricks: Auto-Optimized Agents Using Your Data"
authors: "Databricks"
date: "2025-06-11"
category: "Product"
original_url: "https://www.databricks.com/blog/introducing-agent-bricks"
translated_date: "2026-04-07"
---

# Agent Bricks 소개: 여러분의 데이터로 자동 최적화되는 AI 에이전트

> **원문**: [Introducing Agent Bricks: Auto-Optimized Agents Using Your Data](https://www.databricks.com/blog/introducing-agent-bricks)

Databricks는 오늘 **Agent Bricks** 를 소개합니다. Agent Bricks는 비즈니스에 최적화된 고성능 AI 에이전트를 만드는 새로운 자동화 방식입니다. 에이전트가 수행할 작업을 고수준(high-level)으로 설명하고 엔터프라이즈 데이터를 연결하기만 하면, 나머지는 Agent Bricks가 알아서 처리합니다. Agent Bricks는 정형 정보 추출(structured information extraction), 신뢰할 수 있는 지식 지원(reliable knowledge assistance), 커스텀 텍스트 변환(custom text transformation), 그리고 오케스트레이션 멀티 에이전트 시스템(orchestrated multi-agent systems) 등 주요 산업 전반에 걸친 공통 사용 사례에 최적화되어 있습니다. Agent Bricks는 오늘부터 Beta로 제공됩니다.

Agent Bricks는 Mosaic AI Research가 개발한 혁신적인 연구 기법을 활용하여 도메인 특화 합성 데이터(domain-specific synthetic data)와 태스크 인지 벤치마크(task-aware benchmarks)를 자동으로 생성합니다. 이 벤치마크를 기반으로 비용과 품질을 자동 최적화함으로써, 기존 접근 방식의 지루한 시행착오에서 기업을 해방시킵니다. 이제 팀은 처음부터 프로덕션 수준의 정확도와 비용 효율성을 달성할 수 있습니다. 내장된 거버넌스(governance)와 엔터프라이즈 컨트롤(enterprise controls) 덕분에 별도의 도구들을 조합할 필요 없이 개념에서 프로덕션으로 빠르게 이동할 수 있습니다.

## 왜 에이전트에 새로운 접근 방식이 필요한가

**품질과 비용** 은 대부분의 에이전트 실험이 프로덕션에 도달하지 못하게 막는 주요 장벽입니다. 고품질 평가(evaluation) 없이는 대부분의 팀이 직관에 의존해 에이전트를 판단하게 되어, 품질이 일관되지 않고 확장이 불가능한 비용 낭비적인 실험으로 이어집니다. 새로운 모델과 기법이 끊임없이 등장하는 AI의 복잡성은 이 문제를 더욱 심화시킵니다. 기업은 신뢰하고 감당할 수 있는 AI 에이전트를 출시하기 위해 도메인 특화적이고, 반복 가능하며, 객관적이고 지속적인 평가가 필요합니다. 그리고 팀을 재교육하거나 막대한 비용 없이도 최신 기술을 활용할 수 있어야 합니다. Databricks는 업계에서 현재 충족되지 않은 이러한 중요한 고객 요구사항을 해결하기 위해 Agent Bricks를 구축했습니다.

## Agent Bricks: 엔터프라이즈 데이터로 AI 에이전트를 즉시 빌드하고 최적화하기

Agent Bricks의 자동화 워크플로우는 다음과 같이 작동합니다.

먼저, Agent Bricks는 품질을 평가하기 위한 태스크 특화 평가(task-specific evaluations)와 LLM 판정자(LLM judges)를 자동으로 생성합니다. 다음으로, 에이전트의 학습을 실질적으로 보완하기 위해 고객의 데이터와 유사한 합성 데이터(synthetic data)를 생성합니다. 마지막으로, Agent Bricks는 에이전트를 정교하게 다듬기 위한 다양한 최적화 기법들을 탐색합니다. 이 자동화 워크플로우가 끝나면, 고객은 에이전트가 달성하기를 원하는 품질과 비용의 균형에 맞는 반복(iteration)을 선택하기만 하면 됩니다. 결과물은 일관되고 지능적인 출력을 빠르게 제공하는 프로덕션급(production-grade) 도메인 특화 AI 에이전트입니다.

Agent Bricks는 주요 산업에 걸쳐 다양한 공통 고객 사용 사례를 지원합니다.

- **Information Extraction Agent**: 이메일, PDF, 보고서와 같은 문서를 이름, 날짜, 제품 상세 정보 등의 정형 필드(structured fields)로 변환합니다. 유통 조직은 문서가 복잡하거나 형식이 다르더라도 공급업체 PDF에서 제품 세부 정보, 가격, 설명을 손쉽게 추출할 수 있습니다.

- **Knowledge Assistant Agent**: 챗봇에서 모호하거나 완전히 틀린 답변을 받는 문제를 해결하여, 엔터프라이즈 데이터에 기반한 빠르고 정확한 답변을 제공합니다. 제조 조직은 기술자가 바인더를 뒤적일 필요 없이 표준 운영 절차(SOP)와 유지보수 매뉴얼에서 즉각적인 인용 기반 답변을 받을 수 있도록 지원할 수 있습니다.

- **Multi-Agent Supervisor**: Genie Space, 다른 LLM 에이전트, MCP와 같은 도구 전반에 걸쳐 에이전트를 원활하게 연결하는 멀티 에이전트 시스템을 구축할 수 있습니다. 금융 서비스 조직은 의도 감지(intent detection), 문서 검색, 컴플라이언스(compliance) 검토를 처리하는 여러 에이전트를 오케스트레이션하여 어드바이저와 고객에게 완전하고 개인화된 응답을 제공할 수 있습니다.

- **Custom LLM Agent**: 콘텐츠 생성이나 커스텀 채팅과 같은 맞춤형 태스크를 위한 텍스트를 변환하며, 해당 산업에 맞게 최적화됩니다. 마케팅 팀은 조직의 브랜드 정체성을 반영하는 마케팅 카피, 블로그, 보도자료를 생성하는 커스텀 에이전트를 구축할 수 있습니다.

## 경영진 코멘트

> "Agent Bricks는 AI 에이전트를 빌드하고 배포하는 완전히 새로운 방식입니다. 에이전트는 여러분의 데이터를 기반으로 추론할 수 있습니다. 처음으로 기업들이 자신만의 데이터 위에서 속도와 자신감을 갖고 아이디어에서 프로덕션급 AI로 이동할 수 있으며, 품질과 비용 트레이드오프에 대한 통제권을 가집니다. 수동 튜닝도 없고, 추측도 없으며, Databricks가 제공하는 모든 보안과 거버넌스가 포함됩니다. 이것이야말로 엔터프라이즈 AI 에이전트를 실용적이고 강력하게 만드는 돌파구입니다."
>
> — Ali Ghodsi, CEO 겸 Co-founder, Databricks

## 고객 도입 사례

Agent Bricks를 통해 이미 혁신을 경험하고 있는 고객들의 목소리를 들어보겠습니다.

> "Agent Bricks를 통해 저희 팀은 단 한 줄의 코드도 작성하지 않고 40만 건 이상의 임상시험 문서를 파싱하여 정형 데이터 포인트를 추출할 수 있었습니다. 60분도 채 안 되어 복잡한 비정형 데이터를 분석에 활용 가능한 형태로 변환할 수 있는 에이전트가 완성되었습니다."
>
> — Joseph Roemer, Head of Data & AI, Commercial IT, AstraZeneca

> "Agent Bricks를 통해 저희는 고객 지원 통화에서 인사이트를 추출하는 것과 같은 도메인 특화 AI 에이전트를 빠르게 프로덕션화할 수 있었습니다. 이전에는 수 주간의 수동 검토가 필요했던 작업입니다. 덕분에 엔터프라이즈 전반의 AI 역량이 가속화되었고, 그라운딩 루프(grounding loop)에서의 품질 개선을 가이드받으며 동등하게 잘 작동하는 더 저렴한 옵션을 식별할 수 있었습니다."
>
> — Chris Nishnick, Director of AI, Lippert

> "Agent Bricks는 표준 상용 LLM 대비 의료 정확도를 두 배로 높이면서 Flo Health의 임상적 정확성, 안전성, 개인정보 보호 및 보안에 대한 높은 내부 기준을 충족할 수 있게 해주었습니다. Flo의 전문적인 건강 전문 지식과 데이터를 활용하여 Agent Bricks는 합성 데이터 생성(synthetic data generation)과 커스텀 평가 기법을 통해 훨씬 낮은 비용으로 더 높은 품질의 결과를 제공합니다. 이를 통해 수억 명의 사용자를 위한 여성 건강 증진에 앞장서는 Flo의 고유한 포지셔닝을 강화하면서 개인화된 AI 건강 지원을 효율적이고 안전하게 확장할 수 있습니다."
>
> — Roman Bugaev, CTO, Flo Health

> "Agent Bricks를 통해 프로덕션에서 신뢰할 수 있는 비용 효율적인 에이전트를 구축할 수 있었습니다. 맞춤화된 평가 덕분에 비정형 입법 일정(legislative calendars)을 파싱하는 정보 추출 에이전트를 자신감 있게 개발했습니다. 덕분에 수동 시행착오 최적화에 소요되던 30일을 절약할 수 있었습니다."
>
> — Ryan Jockers, Assistant Director of Reporting and Analytics, North Dakota University System

> "40,000건 이상의 복잡한 법률 문서를 보유한 저희는 내부 '규제 채팅 도구(Regulatory Chat Tool)'에서 높은 정밀도가 필요했습니다. Agent Bricks는 LLM-as-judge 및 인간 평가 정확도 지표 모두에서 LangChain 기반의 기존 오픈소스 구현을 크게 능가했습니다."
>
> — Joel Wasson, Manager Enterprise Data & Analytics, Hawaiian Electric

## Data + AI Summit에서 함께 발표된 Mosaic AI 추가 기능

Agent Bricks와 함께, Databricks는 다음과 같은 추가 혁신 기능들을 선보였습니다.

**서버리스 GPU(Serverless GPU) 지원**: Databricks는 이제 서버리스 GPU를 지원하여, GPU 인프라를 프로비저닝하거나 관리할 필요 없이 모델 파인튜닝(fine-tuning), 고전적인 머신러닝 또는 딥러닝 워크로드 실행, LLM 실험을 모두 처리할 수 있습니다. 서버리스 GPU 컴퓨트를 통해 사용자는 고성능 컴퓨팅 리소스에 빠르고 온디맨드로 확장 가능하게 접근할 수 있어, 기존 GPU 클러스터의 운영 오버헤드나 비용 비효율 없이 AI 애플리케이션을 더 빠르게 구축할 수 있습니다.

**MLflow 3.0: AI 라이프사이클 관리를 위한 통합 플랫폼**: Databricks는 세계에서 가장 인기 있는 AI 개발 프레임워크의 최신 버전인 MLflow 3.0을 오늘 출시했습니다. GenAI를 위해 완전히 새롭게 설계된 MLflow 3.0은 어느 플랫폼에서 호스팅되는 AI 에이전트든 모니터링, 추적(trace), 최적화할 수 있도록 합니다. 통합된 프롬프트 관리(prompt management), 품질 지표(quality metrics), 인간 피드백(human feedback), LLM 기반 평가를 통해 팀은 환경 전반에서 AI 에이전트의 성능을 쉽게 시각화하고 비교하며 디버깅할 수 있습니다. MLflow 트레이스와 평가 결과는 기존 데이터 레이크하우스(data lakehouse)와 통합될 수 있어, 사용자가 프로덕션 트레이스 데이터를 활용하여 에이전트의 정확도를 개선할 수 있습니다. MLflow는 오픈소스이며 매달 3천만 회 이상 다운로드됩니다.

Agent Bricks와 함께 이러한 혁신들은 Databricks를 빌딩·튜닝부터 평가·비교·안전한 배포까지 프로덕션급 GenAI를 위한 가장 완전한 플랫폼으로 만들어줍니다.

## 제공 시기

**Agent Bricks** 와 **서버리스 GPU 컴퓨트(Serverless GPU Compute)** 는 오늘부터 Beta로 제공됩니다. **MLflow 3.0** 은 일반 공개(GA)되었습니다.

---

{% hint style="info" %}
**Agent Bricks 시작하기**

Agent Bricks는 Databricks 플랫폼 내에서 바로 사용할 수 있습니다. Knowledge Assistant, Information Extraction Agent, Multi-Agent Supervisor, Custom LLM Agent의 네 가지 에이전트 유형 중 비즈니스 목적에 맞는 유형을 선택하고, 자연어로 작업을 설명한 뒤 데이터 소스를 연결하면 됩니다. 자세한 내용은 [공식 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/)를 참조하세요.
{% endhint %}
