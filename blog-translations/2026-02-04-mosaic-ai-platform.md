---
original_title: "Mosaic AI: Build and Deploy Production-quality AI Agent Systems"
authors: "Patrick Wendell, Naveen Rao"
date: "2024-06-12"
category: "Data Science and ML"
original_url: "https://www.databricks.com/blog/mosaic-ai-build-and-deploy-production-quality-compound-ai-systems"
translated_date: "2026-02-04"
note: "원문 URL(databricks-mosaic-ai-complete-platform)은 404로 확인되지 않아, 동일 주제의 가장 근접한 공식 블로그 포스트로 대체하였습니다."
---

# Mosaic AI: 프로덕션 수준의 AI Agent 시스템을 빌드하고 배포하기

> **원문**: [Mosaic AI: Build and Deploy Production-quality AI Agent Systems](https://www.databricks.com/blog/mosaic-ai-build-and-deploy-production-quality-compound-ai-systems)

_에이전트 및 RAG 개발, 모델 파인튜닝, AI 평가, 툴 거버넌스를 단순화하는 새로운 제품들을 발표합니다_

![Mosaic AI 플랫폼 개요](https://www.databricks.com/sites/default/files/2025-01/mosaic-ai-build-and-deploy-production-quality-compound-ai-systems.png?v=1738245224)

**게시일:** 2024년 6월 12일 | **카테고리:** Data Science and ML | **읽는 시간:** 8분

**저자:** Patrick Wendell, Naveen Rao

---

지난 한 해 동안, 일반 지식 태스크에서 강력한 추론 능력을 보여주는 상용 및 오픈소스 파운데이션 모델(foundation model)의 급속한 증가를 목격했습니다. 일반 모델은 중요한 빌딩 블록이지만, 프로덕션 AI 애플리케이션은 종종 **Compound AI System** 을 채택합니다. Compound AI System은 파인튜닝된 모델, 검색(retrieval), 툴 사용(tool use), 추론 에이전트(reasoning agents) 등 여러 컴포넌트를 결합해 활용합니다. 이러한 **AI 에이전트 시스템** 은 파운데이션 모델을 강화하여 훨씬 높은 품질을 달성하고, 고객이 GenAI 앱을 프로덕션에 자신 있게 배포할 수 있도록 도와줍니다.

오늘 Data and AI Summit에서, Databricks는 **Databricks Mosaic AI** 를 프로덕션 수준의 AI 에이전트 시스템을 구축하기 위한 최고의 플랫폼으로 만드는 여러 새로운 기능들을 발표했습니다. 이러한 기능들은 수천 개의 기업이 AI 기반 애플리케이션을 프로덕션에 배포하는 과정에서 쌓아온 경험을 바탕으로 합니다. 오늘 발표에는 파운데이션 모델 파인튜닝 지원, AI 툴을 위한 엔터프라이즈 카탈로그, AI 에이전트를 빌드·배포·평가하기 위한 새로운 SDK, 그리고 배포된 AI 서비스를 거버닝하기 위한 통합 AI 게이트웨이가 포함됩니다.

이번 발표를 통해 Databricks는 1년 전 MosaicML 인수에서 처음 포함된 모델 빌딩 기능을 완전히 통합하고 대폭 확장하였습니다.

![Compound AI 시스템 아키텍처 다이어그램](https://www.databricks.com/sites/default/files/inline-images/image6_6.png)

## Compound AI 시스템 빌드 및 배포

단일 모놀리식(monolithic) AI 모델에서 복합 시스템으로의 전환은 학계와 산업계 모두에서 활발히 연구되는 분야입니다. 최근 연구 결과에 따르면, "최첨단 AI 결과는 단일 모놀리식 모델이 아니라 여러 컴포넌트로 구성된 복합 시스템에서 점점 더 많이 나오고 있습니다." 이러한 결과는 우리 고객 기반에서 확인되는 사실과도 일치합니다. 금융 리서치 기업 FactSet을 예로 들면, 상용 LLM을 Text-to-Financial-Formula 사용 사례에 배포했을 때 생성된 수식의 정확도가 55%에 불과했지만, 모델을 컴파운드 시스템으로 모듈화하여 각 태스크를 전문화함으로써 정확도를 85%까지 높일 수 있었습니다. Databricks Mosaic AI는 다음과 같은 제품들을 통해 AI 시스템 구축을 지원합니다.

**Databricks Model Training을 활용한 파인튜닝:** 소규모 데이터셋으로 모델을 파인튜닝하든, 수조 개의 토큰과 3,000개 이상의 GPU로 처음부터 모델을 프리트레이닝(DBRX처럼)하든, 기반 인프라를 추상화한 사용하기 쉬운 관리형 API를 제공합니다. 비용과 레이턴시를 줄이면서도 독점 데이터로 엔터프라이즈 태스크에서 GPT-4 수준의 성능을 맞추기 위해 더 작은 오픈소스 모델을 파인튜닝하는 방식으로 성공을 거두는 고객들이 늘고 있습니다. Model Training은 고객이 모델과 데이터를 완전히 소유하고 품질을 반복적으로 개선할 수 있도록 지원합니다.

![Databricks Model Training UI - 태스크와 베이스 모델을 선택하고 학습 데이터를 제공하는 화면](https://www.databricks.com/sites/default/files/inline-images/image4_13.png)

사용자는 태스크와 베이스 모델을 선택하고 학습 데이터(Delta 테이블 또는 .jsonl 파일 형태)를 제공하기만 하면, 전문화된 태스크를 위해 완전히 파인튜닝된 모델을 소유할 수 있습니다.

**Shutterstock ImageAI, Powered by Databricks:** 파트너사 Shutterstock은 오늘 Databricks Model Training을 사용하여 Shutterstock의 세계적 수준 이미지 저장소로만 학습된 새로운 텍스트-이미지 모델을 발표했습니다. 이 모델은 특정 비즈니스 요구에 맞춘 커스터마이징된 고품질의 신뢰할 수 있는 이미지를 생성합니다.

**Customer Managed Keys 및 Hybrid Search를 지원하는 Mosaic AI Vector Search:** 최근 Vector Search를 정식 출시(GA)했습니다. 추가로 Vector Search는 이제 8K 컨텍스트 길이를 지원하며 검색 성능이 우수한 GTE-large 임베딩 모델을 지원합니다. 또한 Vector Search는 이제 데이터에 대한 더 많은 제어를 제공하는 Customer Managed Keys를 지원하고, 검색 품질을 향상시키기 위한 하이브리드 검색(hybrid search)을 지원합니다.

**빠른 개발을 위한 Mosaic AI Agent Framework:** RAG 애플리케이션은 우리 플랫폼에서 가장 많이 사용되는 GenAI 애플리케이션으로, 오늘 Agent Framework의 Public Preview를 발표하게 되어 매우 기쁩니다. 이를 통해 Unity Catalog에서 안전하게 거버닝되고 관리되는 독점 데이터로 강화된 AI 시스템을 매우 쉽게 구축할 수 있습니다.

**에이전트를 위한 Databricks Model Serving 지원 및 Foundation Model API 정식 출시:** 실시간 서빙 모델 외에도, 고객은 이제 Model Serving으로 에이전트와 RAG를 서빙할 수 있습니다. 또한 Foundation Model API를 정식 출시합니다. 고객은 프로덕션 워크로드를 위한 토큰당 요금제(pay-per-token)와 프로비저닝된 처리량(provisioned throughput) 방식으로 파운데이션 모델을 쉽게 사용할 수 있습니다.

**Mosaic AI Tool Catalog 및 Function-Calling:** 오늘 Mosaic AI Tool Catalog를 발표합니다. Tool Catalog는 고객이 내부 또는 외부의 공통 함수들로 구성된 엔터프라이즈 레지스트리를 생성하고, 이 툴들을 AI 애플리케이션에서 사용할 수 있도록 조직 전체에 공유할 수 있게 해줍니다. 툴은 SQL 함수, Python 함수, 모델 엔드포인트, 원격 함수, 또는 리트리버(retriever)가 될 수 있습니다. 또한 Model Serving을 개선하여 Function-Calling을 네이티브로 지원하도록 했습니다. 이를 통해 고객은 Llama 3-70B와 같은 인기 오픈소스 모델을 에이전트의 추론 엔진으로 활용할 수 있습니다.

![Databricks Model Serving Function-Calling 및 AI Playground](https://www.databricks.com/sites/default/files/inline-images/image3_21.png)

Databricks Model Serving은 이제 Function-Calling을 지원하며, 사용자는 AI Playground에서 함수와 베이스 모델을 빠르게 실험해볼 수 있습니다.

## AI 시스템 평가하기

범용 AI 모델은 MMLU와 같은 벤치마크에 최적화되어 있지만, 배포된 AI 시스템은 더 넓은 제품의 일부로서 특정 사용자 태스크를 해결하도록 설계됩니다(예: 지원 티켓 응답, 쿼리 생성, 답변 제안). 이러한 시스템이 잘 동작하는지 확인하려면, 품질 지표를 정의하고, 품질 신호를 수집하고, 성능을 반복적으로 개선하기 위한 견고한 평가 프레임워크가 필요합니다. 오늘 여러 새로운 평가 도구를 발표하게 되어 기쁩니다.

**자동화 및 휴먼 평가를 위한 Databricks MLflow:** Agent Evaluation을 사용하면 성공적인 상호작용의 "골든(golden)" 예시를 제공하여 AI 시스템에서 고품질 답변이 어떤 모습이어야 하는지 정의할 수 있습니다. 이 품질 기준이 마련되면, 시스템의 다양한 조합을 탐색하여 모델을 튜닝하거나, 검색 방식을 변경하거나, 툴을 추가하면서 시스템 변경이 품질에 어떤 영향을 미치는지 파악할 수 있습니다. Agent Evaluation은 또한 Databricks 계정이 없는 사람을 포함하여 조직 전반의 분야 전문가를 초대하여 AI 시스템 출력을 검토하고 레이블링함으로써 프로덕션 품질 평가를 수행하고 확장된 평가 데이터셋을 구축할 수 있게 합니다. 마지막으로, 시스템에서 제공하는 LLM 판정자(LLM judges)는 정확도나 유용성과 같은 공통 기준으로 응답을 평가하여 평가 데이터 수집을 더욱 확장할 수 있습니다. 상세한 프로덕션 트레이스(trace)는 저품질 응답을 진단하는 데 도움이 됩니다.

![Databricks MLflow AI 지원 메트릭 화면](https://www.databricks.com/sites/default/files/inline-images/image1_26.png)

Databricks MLflow는 개발자가 빠른 직관을 형성할 수 있도록 AI 지원 메트릭을 제공합니다.

![Databricks MLflow 스테이크홀더 평가 화면](https://www.databricks.com/sites/default/files/inline-images/image5_9.png)

Databricks MLflow는 Databricks 플랫폼 외부의 이해관계자들도 모델 출력을 평가하고 품질 반복 개선을 위한 평점을 제공할 수 있도록 합니다.

**MLflow 2.14:** MLflow는 LLM과 AI 시스템을 평가하기 위한 모델 비종속적(model-agnostic) 프레임워크로, 고객이 각 단계에서 파라미터를 측정하고 추적할 수 있게 합니다. MLflow 2.14에서 MLflow Tracing을 발표하게 되어 기쁩니다. Tracing을 통해 개발자는 모델 및 에이전트 인퍼런스의 각 단계를 기록하여 성능 문제를 디버그하고 향후 개선 사항을 테스트하기 위한 평가 데이터셋을 구축할 수 있습니다. Tracing은 Databricks MLflow Experiments, Databricks Notebooks, Databricks Inference Tables와 긴밀히 통합되어 개발부터 프로덕션까지 성능 인사이트를 제공합니다.

{% hint style="info" %}
**고객 사례 — Corning**

"Corning은 소재 과학 기업으로, 우리의 유리 및 세라믹 기술은 많은 산업 및 과학 응용 분야에 사용됩니다. 따라서 데이터를 이해하고 활용하는 것이 필수적입니다. 우리는 미국 특허청 데이터를 포함한 수십만 건의 문서를 인덱싱하기 위해 Databricks Mosaic AI Agent Framework를 활용하여 AI 리서치 어시스턴트를 구축했습니다. LLM 기반 어시스턴트가 높은 정확도로 질문에 답변하는 것이 우리에게 매우 중요했습니다. 그래야 연구원들이 진행 중인 작업을 쉽게 찾고 발전시킬 수 있기 때문입니다. 이를 구현하기 위해 미국 특허청 데이터로 강화된 Hi Hello Generative AI 솔루션을 구축하는 데 Databricks Mosaic AI Agent Framework를 활용했습니다. Databricks Data Intelligence Platform을 활용하여 검색 속도, 응답 품질, 정확도를 크게 향상시킬 수 있었습니다."

— Denis Kamotsky, Principal Software Engineer, Corning
{% endhint %}

## AI 시스템 거버닝하기

최첨단 파운데이션 모델의 폭발적 증가 속에서, 고객 기반이 새로운 모델을 빠르게 채택하는 것을 목격했습니다. DBRX는 출시 2주 만에 천 명의 고객이 실험했고, 최근 출시된 Llama 3 모델도 수백 명의 고객이 실험하고 있습니다. 많은 기업이 합리적인 시간 내에 플랫폼에서 이러한 새로운 모델을 지원하기 어렵다고 느끼며, 프롬프트 구조와 쿼리 인터페이스의 변화로 구현이 어렵습니다. 더 나아가, 기업들이 최신 최고 모델에 대한 접근을 열어두면 사람들은 흥분하여 많은 것을 만들기 시작하고, 이는 금세 거버넌스 문제의 눈덩이로 이어질 수 있습니다. 일반적인 거버넌스 문제로는 레이트 리밋(rate limit)에 도달하여 프로덕션 애플리케이션에 영향을 미치는 것, 대규모 테이블에서 GenAI 모델을 실행하면서 급증하는 비용, 그리고 PII가 서드파티 모델 제공업체에 전송되는 데이터 유출 우려 등이 있습니다. 오늘, AI Gateway의 새로운 거버넌스 기능과 모델 검색을 가능하게 하는 큐레이션된 모델 카탈로그를 발표하게 되어 기쁩니다. 포함된 기능들은 다음과 같습니다.

**중앙화된 AI 거버넌스를 위한 Mosaic AI Gateway:** Mosaic AI Gateway는 고객이 모델을 쉽게 관리, 거버닝, 평가, 전환할 수 있는 통합 인터페이스를 제공합니다. Model Serving 위에 위치하여 모델 API(외부 또는 내부)에 대한 레이트 리밋, 권한, 자격 증명 관리를 가능하게 합니다. 또한 파운데이션 모델 API를 쿼리하기 위한 단일 인터페이스를 제공하여, 고객이 시스템에서 모델을 쉽게 교체하고 빠른 실험을 통해 사용 사례에 가장 적합한 모델을 찾을 수 있도록 합니다. Gateway Usage Tracking은 각 모델 API를 누가 호출하는지 추적하고, Inference Tables는 어떤 데이터가 송수신되었는지 캡처합니다. 이를 통해 플랫폼 팀은 레이트 리밋을 어떻게 변경할지, 비용 청구(chargeback)를 어떻게 구현할지, 데이터 유출을 어떻게 감사할지 파악할 수 있습니다.

**Mosaic AI Guardrails:** 엔드포인트 수준 또는 요청 수준의 안전 필터링을 추가하여 안전하지 않은 응답을 방지하거나, PII 탐지 필터를 추가하여 민감한 데이터 유출을 방지할 수 있습니다.

**system.ai 카탈로그:** Unity Catalog에서 관리될 수 있는 최첨단 오픈소스 모델의 큐레이션 목록을 제공합니다. Model Serving Foundation Model API를 사용하여 이러한 모델을 쉽게 배포하거나 Model Training으로 파인튜닝할 수 있습니다. 고객은 또한 Settings > Developer > Personalized Homepage로 이동하여 Mosaic AI 홈페이지에서 지원되는 모든 모델을 확인할 수 있습니다.

{% hint style="info" %}
**고객 사례 — Edmunds.com**

"Databricks Model Serving은 Databricks 내외에서 호스팅된 모델을 포함하여 여러 SaaS 및 오픈 모델에 안전하게 접근하고 관리하기 쉽게 해줌으로써 AI 기반 프로젝트를 가속화하고 있습니다. 중앙화된 접근 방식은 보안과 비용 관리를 단순화하여, 우리 데이터 팀이 행정적인 오버헤드보다 혁신에 더 집중할 수 있게 합니다."

— Greg Rokita, AVP, Technology at Edmunds.com
{% endhint %}

## 마치며

Databricks Mosaic AI는 팀이 단일 플랫폼에서 중앙화된 거버넌스와 함께 Compound AI 시스템을 구축하고 협업할 수 있도록 지원합니다. 학습(train), 추적(track), 평가(evaluate), 교체(swap), 배포(deploy)를 위한 통합 인터페이스를 제공합니다. 엔터프라이즈 데이터를 활용함으로써, 조직은 일반적인 지식에서 데이터 인텔리전스로 나아갈 수 있습니다. 이러한 진화는 조직이 더 빠르게 더 관련성 높은 인사이트를 얻을 수 있도록 힘을 실어줍니다.

앞으로 고객들이 어떤 혁신을 만들어낼지 기대됩니다!

---

**관련 링크:**
- [Databricks Mosaic AI 제품 페이지](https://www.databricks.com/product/artificial-intelligence)
- [공식 문서](https://docs.databricks.com/machine-learning/index.html)
