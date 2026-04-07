---
original_title: "Databricks Announces Lakewatch: New Open, Agentic SIEM"
authors: "Reynold Xin, Andrew Krioukov, Molly Limaye, Taylor Kain, Keegan Dubbs"
date: "2026-03-24"
category: "Announcements"
original_url: "https://www.databricks.com/blog/databricks-announces-lakewatch-new-open-agentic-siem"
translated_date: "2026-04-07"
---

> **원문**: [Databricks Announces Lakewatch: New Open, Agentic SIEM](https://www.databricks.com/blog/databricks-announces-lakewatch-new-open-agentic-siem)

# Databricks Lakewatch 발표: 새로운 오픈형 에이전틱 SIEM

**게시일**: 2026년 3월 24일 | **저자**: Reynold Xin, Andrew Krioukov, Molly Limaye, Taylor Kain, Keegan Dubbs | **카테고리**: Announcements | **읽기 시간**: 7분

![Lakewatch SIEM 출시 이미지](https://www.databricks.com/sites/default/files/2026-03/03-2026-launch-post-og-1200x630.png)

## 요약

- **오픈 Security Lakehouse의 비전**: 전통적인 SIEM(보안 정보 및 이벤트 관리 시스템)이 확장성 측면에서 한계를 갖는 이유, 그리고 Lakewatch가 오픈 보안 레이크하우스 위에서 100%의 텔레메트리를 통합함으로써 데이터 사일로를 어떻게 제거하는지.
- **에이전트로 에이전트를 막는다**: 임베디드 AI와 "Genie" 에이전트가 머신 속도로 위협 탐지, 자연어 기반 위협 헌팅(Threat Hunting), 사고 대응(Incident Response)을 어떻게 자동화하는지.
- **현대적인 SecOps 경제성**: 컴퓨트(Compute)와 스토리지(Storage)를 분리함으로써 비용을 최대 80%까지 절감하면서도 페타바이트(Petabyte) 규모의 데이터를 수년간 보유하는 방법.

---

오늘, 우리는 점점 더 정교해지는 에이전트형 공격자에 맞서 조직이 방어할 수 있도록 설계된 새로운 오픈형 에이전틱 SIEM인 [Lakewatch](https://www.databricks.com/lakewatch)를 발표합니다. Lakewatch는 보안, IT, 비즈니스 데이터를 단일의 거버넌스(Governance)된 환경으로 통합하여 AI 기반 탐지 및 대응을 가능하게 합니다. 오픈 포맷(Open Format)을 통해 Lakewatch는 고객이 전례 없는 규모의 멀티모달(Multi-modal) 데이터를 수집, 보존, 분석할 수 있게 하는 동시에 비용을 대폭 절감하고 벤더 종속(Vendor Lock-in)을 제거합니다. 보안 팀은 엔터프라이즈 전체에 대한 완전한 가시성을 확보하고, 방어적 보안 에이전트를 배포하여 대규모로 위협 탐지와 대응을 자동화할 수 있습니다. Lakewatch는 오늘 **Private Preview** 로 출시되며, Adobe와 Dropbox 같은 업계 선도 기업들이 고객으로 참여하고 있습니다.

또한 우리는 "오픈 Security Lakehouse 에코시스템(Open Security Lakehouse Ecosystem)"을 함께 출시합니다. 이 에코시스템은 고객이 텔레메트리(Telemetry)를 오픈 포맷으로 자동 정규화하고, 현대적인 위협에 자동화된 머신 속도의 방어로 대응하는 데 필요한 통합 규모를 갖출 수 있도록 지원하는 주요 보안 및 전달 파트너들로 구성됩니다.

---

## 에이전틱 시대의 보안

보안의 패러다임이 근본적으로 변화하고 있습니다. 사이버 공격은 더 이상 인간만이 조작하는 것이 아닙니다. 공격은 점점 더 AI 기반의 자동화된 방식으로 이루어지고 있습니다. [LLM(대형 언어 모델)은 오픈소스 코드에서 500개 이상의 제로데이(Zero-day) 취약점을 발견했으며](https://www.axios.com/2026/02/05/anthropic-claude-opus-46-software-hunting), [AI 에이전트는 버그 바운티(Bug Bounty) 플랫폼에서 최상위 해커로 자리매김했습니다](https://xbow.com/blog/top-1-how-xbow-did-it). 그리고 [국가 지원 그룹들은 AI를 무기화하여 침투를 자동화하고 있습니다](https://sean.heelan.io/2026/01/18/on-the-coming-industrialisation-of-exploit-generation-with-llms/). 공격자들은 이제 머신 규모로 운영되며, 24/7로 익스플로잇(Exploit)을 구성하고 공격을 조율합니다.

이러한 머신 규모의 공격에 맞서, 최고의 보안 운영 팀조차 구조적인 제약에 직면해 있습니다. 오늘날의 보안 도구는 애널리스트가 수동으로 알림을 강화하고, 탐지 규칙을 직접 작성하며, 위협 헌팅 가설을 수일 또는 수주에 걸쳐 테스트하도록 요구합니다. 이러한 워크플로우는 인간 속도의 위협에는 효과적일 수 있었습니다. 하지만 24/7 머신 속도로 운영되는 AI 기반 공격에 맞서면, 아키텍처 자체가 병목이 됩니다. [ZeroDayClock.com](https://zerodayclock.com/)에 따르면, 익스플로잇까지의 평균 시간(Mean Time to Exploit)은 2025년 23.2일에서 2026년에는 불과 1.6일로 급격히 단축되었습니다.

데이터 측면을 살펴보면 문제는 더욱 심각해집니다. 대규모 엔터프라이즈는 매일 테라바이트, 심지어 페타바이트에 달하는 보안 데이터를 생성합니다. 하지만 전통적인 SIEM은 스토리지와 컴퓨트를 결합시켜, 수집하는 모든 바이트에 재정적 패널티를 부과합니다. 팀들은 결국 데이터 수집을 제한하고, 라우팅 레이어를 통해 데이터를 필터링하고, 과거 데이터를 삭제하며, 채팅 로그나 비디오 같은 멀티모달 소스를 완전히 무시하는 방식으로 대응합니다. 이로 인해 위험한 비대칭성이 발생합니다. 공격자는 AI 에이전트를 사용해 모든 것을 분석하고 어디서든 공격하는 반면, 방어자는 자신의 데이터 중 일부만 볼 수 있습니다. 전통적인 SIEM은 멀티모달 데이터를 처리하지 못하지만, 바로 그곳에 소셜 엔지니어링(Social Engineering) 공격, 내부자 위협, 프롬프트 인젝션(Prompt Injection) 시도가 숨어 있습니다.

이것은 단순히 비용이나 규모의 문제가 아닙니다. 우리가 직면한 위협과 그것을 맞서 싸울 도구 사이의 근본적인 아키텍처 불일치입니다. 우리는 이 동일한 문제를 이전에도 해결한 적이 있습니다. 데이터 웨어하우스도 동일한 한계를 가지고 있었습니다. 비싼 수집 비용, 사일로화된 데이터, 특정 사용 사례에 국한된 활용. 레이크하우스(Lakehouse)는 오픈 포맷, 저렴한 스토리지, 모든 데이터 유형 지원으로 그 모델을 혁신했습니다. 이제 우리는 그 동일한 변혁을 보안 영역에 가져옵니다.

Lakewatch는 레이크하우스의 경제성과 아키텍처를 보안 운영에 적용합니다. 보안 텔레메트리의 100%(멀티모달 데이터 포함)를 수집하고 보존하며, 모든 비즈니스 데이터와 함께 분석하고, AI 기반 에이전트를 탐지와 대응에 배포할 수 있습니다. 이 모든 것이 레거시 비용의 극히 일부로 가능합니다.

---

## Lakewatch가 보안 운영을 변화시키는 방법

### 모든 데이터에 대한 완전한 가시성

조직들은 이미 위협을 조사하는 데 필요한 컨텍스트(Context)를 보유하고 있습니다. HR 시스템, 협업 플랫폼, 애플리케이션 로그, 거래 데이터가 이미 레이크(Lake)에 존재하지만, 전통적인 보안 도구는 비용이 많이 드는 데이터 복제 없이는 이에 접근할 수 없습니다. Lakewatch는 모델을 뒤집습니다. 보안이 레이크하우스 위에서 직접 실행됩니다. [Unity Catalog](https://www.databricks.com/product/unity-catalog) 위에 구축된 Lakewatch에서는 보안 데이터가 다른 모든 데이터와 함께 존재합니다. 알림이 발생하면, 파일을 이동하거나 도구를 전환하지 않고도 즉시 모든 데이터 소스에서 상관관계를 분석할 수 있습니다. 현대적인 공격은 시스템 간 격차를 악용하며, 레거시 도구가 처리할 수 없는 소셜 엔지니어링, 내부자 컨텍스트, 멀티모달 신호에 의존합니다. 모든 컨텍스트가 한 곳에 있으면, 애널리스트는 수일이 아닌 수분 만에 위협을 탐지하고 차단할 수 있습니다.

Lakewatch는 다음을 통해 이를 가능하게 합니다:

- **엔터프라이즈 전반의 거버넌스**: 모든 데이터에 대한 완전한 감사 추적과 함께 테이블, 행, 열, 속성 수준의 세밀한 접근 제어.
- **오픈 표준**: OCSF(Open Cybersecurity Schema Framework — 오픈 사이버보안 스키마 프레임워크) 위에 구축되어, 데이터가 독점적 포맷에 종속되지 않습니다.
- **자동화된 수집**: [Lakeflow Connect](https://docs.databricks.com/aws/en/ingestion/overview)가 주요 보안 소스(AWS, Okta, Zscaler 등)의 수집 및 표준화된 테이블로의 정규화를 처리합니다.
- **진정한 데이터 소유권**: 자체 클라우드 스토리지의 Delta Lake 또는 Apache Iceberg에 데이터를 저장하고, 모든 클라우드에서 쿼리를 실행하며, 벤더 종속을 방지합니다.

### 에이전트로 에이전트를 막는다

전통적인 SIEM은 데이터의 전체 컨텍스트에 접근할 수 없는 부가적인 AI 기능에 의존합니다. Lakewatch는 임베디드 AI를 보안 데이터가 실제로 있는 곳으로 직접 가져옵니다. [Genie](https://www.databricks.com/product/business-intelligence/genie)는 새로운 로그 소스를 OCSF로 수집 및 파싱하고, 최신 위협 인텔리전스(Threat Intelligence)를 기반으로 새로운 탐지를 작성하고, 기존 규칙을 수정하여 오탐(False Positive)을 줄이고, 자연어 질문을 SQL 쿼리로 번역하는 등의 핵심 워크플로우를 자동화합니다. [Genie Spaces](https://docs.databricks.com/aws/en/genie/)는 보안 팀이 전문 쿼리 언어 대신 평이한 영어로 페타바이트의 데이터를 쿼리할 수 있게 하여, 기술 수준에 관계없이 위협 헌팅을 민주화합니다.

**주요 기능은 다음과 같습니다:**

- **Genie Code**: 수집 자동화, 새로운 탐지 작성, 오탐 감소를 위한 규칙 수정, 조사를 위한 자연어 질문의 SQL 쿼리 번역을 수행하는 AI 어시스턴트.
- **Genie Spaces**: 자연어 쿼리 인터페이스 및 에이전틱 하네스(Agentic Harness)로, 복잡한 쿼리 언어를 배우지 않고도 모든 사용자가 복잡한 다단계 위협 헌팅을 수행하고 데이터에 질문할 수 있습니다.
- **Detection-as-Code (코드로서의 탐지)**: SQL 쿼리나 Python 노트북이 포함된 YAML로 탐지 규칙을 정의하고, 과거 데이터에 대해 백테스트하며, CI/CD 파이프라인을 통해 배포합니다.
- **커스텀 ML 탐지**: MLflow, Feature Store, Model Serving을 사용하여 보안 데이터에서 직접 머신러닝 모델을 학습하고 배포하여, 이상 탐지(Anomaly Detection), 행동 분석(Behavioral Analytics), 엔터티 위험 점수화(Entity Risk Scoring) 등을 구현합니다.
- **강력한 대시보드**: 실시간 모니터링을 위한 AI 강화 시각화로 경영진, 운영, 컴플라이언스(Compliance) 대시보드를 생성합니다.

### 페타바이트 규모의 효율적인 SecOps

스토리지와 컴퓨트를 분리함으로써, 자체 클라우드 스토리지에 전체 품질의 보안 텔레메트리 페타바이트를 저장하고 컴퓨트 비용만 지불할 수 있습니다. 서버리스(Serverless) 컴퓨트를 사용하여 필요할 때만 분석을 실행하세요. 수주 대신 수년간의 핫 쿼리(Hot Query) 가능한 데이터를 유지하세요. 데이터는 귀하의 소유입니다. 비용도 귀하가 제어합니다.

이것이 의미하는 바는 다음과 같습니다:

- **데이터 소유**: 오픈 포맷을 사용하여 귀하가 제어하는 클라우드 오브젝트 스토리지(S3, ADLS, GCS)에 보안 텔레메트리를 저장합니다.
- **장기 보존**: 비용 패널티 없이 다년간에 걸친 컴플라이언스 요건을 충족하고 위협 헌팅을 수행합니다.
- **예측 가능한 경제성**: 바이트당 라이선스 비용 없이 전체 품질의 로그를 대규모로 저장합니다.
- **온디맨드 탄력적 컴퓨트**: 세밀한 비용 제어와 함께 필요할 때만 강력한 분석 및 ML 워크로드를 프로비저닝합니다.
- **서버리스 성능**: 관리할 인프라가 없습니다. 쿼리에 대해서만 비용을 지불합니다.

### Anthropic과의 파트너십 심화

두 회사의 [기존 전략적 파트너십](https://www.databricks.com/company/newsroom/press-releases/databricks-and-anthropic-sign-landmark-deal-bring-claude-models)의 성공을 바탕으로, Databricks와 Anthropic은 에이전틱 보안 운영을 제공하기 위한 협력을 강화하고 있습니다. Anthropic의 Claude 모델은 Lakewatch를 구동하는 데 도움을 주며, Claude의 고급 추론 능력을 활용하여 보안, IT, 비즈니스 데이터 전반에서 신호를 상관관계 분석하여 위협을 더 빠르게 표면화합니다. 또한 Anthropic은 자체 보안 레이크하우스를 위해 Databricks를 사용하여 보안 및 비즈니스 데이터 전반에 대한 완전한 가시성을 확보하고 위협을 더 일찍 탐지합니다.

---

## 오픈 Security Lakehouse 에코시스템

Databricks는 오늘날의 위협이 고객이 자신의 데이터를 완전히 제어하는 에코시스템 전반에 걸친 오픈 협력을 필요로 한다고 믿습니다. 그래서 우리는 "오픈 Security Lakehouse 에코시스템"을 발표하게 되어 기쁩니다. 이는 [Akamai](https://www.akamai.com/), [Anvilogic](https://www.anvilogic.com/), [Arctic Wolf](https://arcticwolf.com/), [Cribl](https://cribl.io/), [Deloitte](https://www.deloitte.com/us/en/alliances/articles/enhancing-cyber-defense-with-databricks-dbx.html), [Obsidian](https://www.obsidiansecurity.com/), [Okta](https://www.okta.com/), [1Password](https://1password.com/), [Palo Alto Networks](https://www.paloaltonetworks.com/), [Panther](https://panther.com/), [Proofpoint](https://www.proofpoint.com/us), [Rearc](https://rearc.io/services/databricks-cyber-intelligence), [Slack](https://slack.com/), [TrendAI](https://www.trendmicro.com/en_us/business.html), [Wiz](https://www.wiz.io/)(현재 Google Cloud의 일부), [Zscaler](https://www.zscaler.com/)를 포함한 빠르게 성장하는 주요 보안 벤더 및 전달 파트너 그룹입니다.

{% hint style="info" %}
"Zscaler는 오픈 에코시스템에 대한 Databricks의 헌신을 공유합니다. 우리는 오픈 Security Lakehouse 에코시스템에 합류하게 되어 기쁘며, 상호 고객에게 AI 네이티브 솔루션으로 AI 네이티브 공격을 방어하는 데 필요한 데이터와 도구를 제공할 것입니다."

— **Eddie Parra**, VP Solutions Architect Partner Ecosystem, Zscaler
{% endhint %}

{% hint style="info" %}
"사이버 위협이 AI 기반의 머신 규모 공격으로 진화함에 따라, 조직들은 이에 발맞추기 위한 근본적으로 새로운 아키텍처가 필요할 수 있습니다. Lakewatch는 보안 운영에서 한 걸음 앞선 접근 방식을 제시하며, Databricks 레이크하우스의 힘을 SOC(보안 운영 센터)에 가져와 팀이 데이터를 활용하고, 지능형 에이전트를 배포하며, 진화하는 위협보다 앞서 나갈 수 있도록 지원합니다."

— **Jennifer Vitalbo**, Managing Director, Government and Public Services Cyber Defense and Resilience Offering Leader, Deloitte & Touche LLP
{% endhint %}

---

## Antimatter 및 SiftD.ai 인수를 통한 보안 리더십 강화

오픈형 에이전틱 SIEM 접근 방식을 발전시키기 위해, Databricks는 Antimatter와 SiftD.ai 두 회사의 인수를 발표합니다. Antimatter는 AI 에이전트를 위한 증명 가능한 안전한 인증 및 인가(Authorization)의 기반을 마련한 UC Berkeley 보안 연구자들이 설립했습니다. SiftD.ai는 Splunk의 SPL(Search Processing Language — 검색 처리 언어)의 창시자와 Splunk 검색 스택의 수석 아키텍트들이 설립했으며, 대규모 탐지 엔지니어링과 현대적인 위협 분석에 깊은 전문성을 가져올 것입니다.

---

## 더 알아보기

Lakewatch는 보안 운영 방식의 근본적인 전환을 의미합니다. 오픈 보안 레이크하우스로서, 경제성은 더 우수하고, 아키텍처는 더 유연하며, AI 기능은 부가적으로 추가된 것이 아니라 네이티브입니다.

Lakewatch는 더 넓은 가용성을 향해 나아가는 과정에서 Private Preview로 출시됩니다. 비용 압박, 보존 한계에 직면해 있거나, 대규모 보안 워크로드를 데이터 플랫폼으로 이전하고자 한다면, 우리는 여러분의 이야기를 듣고 싶습니다.

SOC를 현대화하는 방법에 대해 자세히 알아보려면 [Lakewatch 제품 페이지](https://www.databricks.com/lakewatch)를 방문하세요.
