---
original_title: "Evolving the Lakehouse: Announcing Databricks Apps, Lakebase, Lakewatch, and Semantic Layer"
authors: "Databricks"
date: "2026-03-17"
category: "Announcements"
original_url: "https://www.databricks.com/blog/evolving-lakehouse-announcing-databricks-apps-lakebase-lakewatch-and-semantic-layer"
translated_date: "2026-04-07"
note: "원문 URL이 404로 확인되어, 동일 주제를 커버하는 관련 블로그 포스트(Lakewatch 발표, Lakebase GA, Unity Catalog Semantic Layer GA)를 기반으로 번역했습니다."
---

> **원문**: [Evolving the Lakehouse: Announcing Databricks Apps, Lakebase, Lakewatch, and Semantic Layer](https://www.databricks.com/blog/evolving-lakehouse-announcing-databricks-apps-lakebase-lakewatch-and-semantic-layer)

{% hint style="warning" %}
**참고**: 위 원문 URL은 현재 접근이 불가합니다(404). 본 번역은 동일 주제를 다루는 Databricks 공식 블로그 포스트들 — [Lakewatch 발표](https://www.databricks.com/blog/databricks-announces-lakewatch-new-open-agentic-siem)(2026년 3월 24일), [Lakebase GA](https://www.databricks.com/blog/databricks-lakebase-generally-available)(2026년 2월 3일), [Unity Catalog Business Semantics GA](https://www.databricks.com/blog/redefining-semantics-data-layer-future-bi-and-ai)(2026년 4월 2일) — 의 내용을 종합하여 작성했습니다.
{% endhint %}

# 레이크하우스의 진화: Databricks Apps, Lakebase, Lakewatch, Semantic Layer 발표

**게시일**: 2026년 3월 | **카테고리**: Announcements

---

{% hint style="info" %}
**요약**
- **Databricks Apps** — 보안과 거버넌스가 내장된 데이터 및 AI 애플리케이션을 Databricks 플랫폼 위에서 직접 빌드하고 배포하는 가장 빠른 방법.
- **Lakebase** — AI 에이전트와 애플리케이션을 위한 완전 관리형 서버리스 Postgres. 트랜잭션, 분석, AI 워크로드를 하나의 거버넌스된 기반 위에서 통합.
- **Lakewatch** — AI 에이전트 공격자에 맞서 조직을 방어하도록 설계된 새로운 오픈형 에이전틱 SIEM(보안 정보 및 이벤트 관리). Private Preview로 출시.
- **Semantic Layer** (Unity Catalog Business Semantics) — 비즈니스 메트릭을 데이터 레이어에서 정의하여 BI, AI, 데이터 엔지니어링 등 모든 워크로드에서 재사용할 수 있는 단일 시맨틱 기반.
{% endhint %}

---

레이크하우스(Lakehouse)는 계속해서 진화하고 있습니다. Databricks는 분석과 AI의 단일 플랫폼으로 출발했지만, 이제 운영 데이터베이스, 데이터 및 AI 애플리케이션, 사이버 보안 운영, 그리고 통합된 비즈니스 시맨틱까지 아우르는 완전한 데이터 인텔리전스 플랫폼으로 거듭나고 있습니다. 오늘 우리는 이 진화를 대표하는 네 가지 주요 제품을 발표합니다.

---

## Databricks Apps: 데이터 및 AI 애플리케이션을 빌드하는 가장 빠른 방법

전통적인 방식으로 내부 도구나 AI 기반 애플리케이션을 빌드하는 일은 개발자를 반복적이고 오류가 발생하기 쉬운 작업의 미로로 몰아넣습니다. 먼저 전용 Postgres 인스턴스를 구동하고, 네트워킹·백업·모니터링을 구성하고, 사용하는 프론트엔드 프레임워크에 그 데이터베이스를 연결하는 데 수 시간에서 수 일이 걸립니다. 그 위에 커스텀 인증 흐름을 작성하고, 세분화된 권한을 매핑하고, 여러 데이터베이스를 동기화하는 취약한 파이프라인을 유지해야 합니다.

**Databricks Apps** 는 이 모든 과정을 근본적으로 단순화합니다. Databricks Apps를 사용하면 Dash, Shiny, Gradio, Streamlit, Flask 등의 인기 있는 프레임워크로 앱을 빌드하고, Databricks 플랫폼 내에서 직접 배포 및 완전 관리할 수 있습니다. 앱은 Unity Catalog에 이미 구성된 데이터 접근 제어를 자동으로 적용받아 완전히 거버넌스됩니다.

![Databricks Apps 아키텍처](https://www.databricks.com/sites/default/files/2025-04/introducing-databricks-apps-2x.png)

### 핵심 역량

- **서버리스 런타임**: 인프라 프로비저닝이나 유지보수 없이 앱이 자동으로 관리됩니다.
- **내장 거버넌스**: Unity Catalog의 접근 제어, OIDC/OAuth 2.0, SSO가 기본으로 제공됩니다.
- **Lakebase 네이티브 통합**: Databricks Apps는 Lakebase를 네이티브 리소스 타입으로 지원하여 트랜잭션 상호작용을 위한 풀스택 애플리케이션 빌드가 가능합니다.
- **AI 컴포넌트 통합**: 감정 분석, 예측 모델링 등 정교한 AI 기능을 앱에 직접 통합할 수 있습니다.

easyJet은 Lakebase와 Databricks Apps를 활용해 10년 된 레거시 데스크톱 애플리케이션과 유럽 최대 규모의 레거시 SQL Server 환경 중 하나를 교체했습니다. 100개 이상의 Git 리포지토리를 2개로 통합하고, 개발 주기를 9개월에서 4개월로 단축했습니다.

> "레거시 시스템의 한계에 직면했지만, Databricks Data Intelligence Platform — 특히 Lakebase와 Databricks Apps — 덕분에 더 빠르고 단순하며 훨씬 안정적인 수익 관리 앱을 구축했습니다. 예전에는 수개월이 걸렸던 일이 이제는 훨씬 짧은 시간에 완성되어, 상업적 의사결정의 토대가 되고 팀이 데이터 중심의 현대 항공사처럼 분석하고 결정하고 행동할 수 있게 되었습니다."
>
> — **Dennis Michon**, Head of Data Product, easyJet

---

## Lakebase: AI 에이전트를 위한 데이터베이스

수십 년 동안 데이터베이스는 거의 변하지 않았습니다. 컴퓨팅과 스토리지를 단단히 묶은 전통적인 아키텍처는 고비용의 프로비저닝, 팀을 느리게 만드는 구조적 제약, 운영 데이터와 분석 데이터 사이의 사일로를 만들어냈습니다. 애플리케이션이 점점 자동화되고 시스템이 실시간으로 데이터에 기반해 행동하는 시대에, 이러한 경직되고 취약한 인프라는 더욱 심각한 걸림돌이 됩니다.

이 아키텍처적 병목을 해소하기 위해 Databricks는 레이크베이스(lakebase) 카테고리를 만들었습니다. 이것은 컴퓨팅과 스토리지를 분리하는 운영 데이터베이스를 위한 새로운 아키텍처입니다. **Databricks Lakebase** — 이 카테고리의 첫 번째 구현 — 는 현재 AWS에서 **일반 공급(GA, Generally Available)** 되었으며 Azure에서는 베타 서비스 중입니다.

![Lakebase 아키텍처](https://www.databricks.com/sites/default/files/inline-images/image4_29.png)

### Lakebase가 해결하는 문제

> "수십 년 동안 운영 데이터와 분석 데이터를 분리해서 보관해야 하는 아키텍처적 '세금'이 기업의 혁신을 저해해왔습니다. 스토리지 레이어를 분리하고 데이터 레이크와 직접 통합함으로써, Lakebase는 인프라를 유연한 온디맨드 서비스로 취급하는 새로운 클래스의 운영 데이터베이스로 자리매김합니다. 고급 AI 역량을 구축하는 기업에게 이는 데이터베이스가 더 이상 수동 병목이 될 가능성이 낮다는 것을 의미합니다. 에이전트가 AI 개발의 속도에 맞춰 더 독립적으로 구동하고 관리할 수 있는 도구가 됩니다."
>
> — **Devin Pratt**, Research Director, IDC

2025년 6월 출시 이후 Lakebase 도입률은 Databricks의 데이터 웨어하우징 제품의 2배 이상 속도로 성장했으며, 수천 개의 기업이 운영 데이터 위에서 직접 프로덕션 워크로드를 실행하고 있습니다.

### 주요 기능

- **서버리스 자동 확장 및 제로로 스케일 다운**: 컴퓨팅 리소스가 트래픽 급등에 맞게 동적으로 조정되고, 유휴 시에는 완전히 종료되어 낭비 비용을 제거합니다.
- **즉시 데이터베이스 브랜칭**: 제로 카피 클론(zero-copy clone)으로 프로덕션 데이터의 격리된 환경을 수 초 만에 생성하여 위험 없이 테스트하고 개발할 수 있습니다.
- **포인트 인 타임 복구 (PITR)**: 밀리초 단위 복원으로 실수로 인한 삭제나 버그를 방지합니다.
- **통합 거버넌스**: Unity Catalog를 통해 전체 데이터 자산에 걸쳐 단일 보안 모델로 접근 제어와 감사를 관리합니다.
- **동기화 테이블**: 취약한 파이프라인을 유지하지 않고 운영 데이터와 레이크하우스 컨텍스트를 동기화 상태로 유지합니다.

### 데이터베이스 아키텍처의 진화: 3세대

데이터베이스 아키텍처는 세 가지 뚜렷한 세대를 거쳐 발전해왔습니다.

**1세대 — 모놀리스 (예: MySQL, Postgres, Oracle 클래식)**: 클라우드 이전 시대에는 네트워크가 가장 느린 부분이었습니다. 유일한 고성능 설계 방법은 CPU/RAM과 디스크를 하나의 물리 머신 내에서 긴밀하게 결합하는 것이었습니다. 그 결과 데이터는 독점 포맷에 갇히고, 확장은 더 큰 서버 구입을 의미했습니다.

**2세대 — 독점적 스토리지 분리 (예: Aurora, Oracle Exadata)**: 클라우드 인프라의 발전으로 스토리지가 독점 백엔드 계층으로 물리적으로 분리되었습니다. 하지만 이것은 내부 최적화에 불과했습니다. 데이터는 여전히 단일 엔진을 통해서만 접근 가능한 독점 포맷으로 잠겨 있었고, 분석 마찰, 클라우드 종속, 단일 엔진 병목이라는 구조적 한계가 남았습니다.

**3세대 — Lakebase: 레이크 위의 오픈 스토리지**: Lakebase는 분리 아키텍처를 논리적인 궁극적 결론까지 밀어붙입니다. 2세대처럼 컴퓨팅과 스토리지를 분리하지만, 결정적인 차이가 있습니다. **스토리지 인프라와 데이터 포맷 모두가 완전히 오픈**되어 있습니다. 이를 통해 더 나은 안정성과 낮은 비용, Git 같은 개발자 경험, 그리고 극단적인 벤더 종속 문제가 해결됩니다.

### AI 에이전트와 앱 구축

Lakebase를 사용하면 운영 워크로드가 Databricks 플랫폼에서 직접 실행됩니다. 애플리케이션은 분석과 AI에 이미 신뢰받는 동일한 거버넌스, 보안, 데이터 기반을 공유합니다. 관리할 사일로 데이터베이스도, 유지할 별도 접근 제어도, 동기화를 유지할 데이터 이동도 없습니다.

대표적인 활용 패턴:
- 신선한 데이터에 낮은 지연 접근을 위한 **머신러닝 실시간 피처 서빙**
- 레이크하우스와 일관성을 유지하는 **AI 에이전트의 영구 메모리**
- 운영 데이터와 과거 인사이트를 결합하는 **임베디드 분석**

> "Lakebase는 분석과 운영 워크로드가 실시간으로 함께 동작하는 통합 기반을 제공합니다. 인사이트를 프로덕션 시스템으로 직접 전달함으로써 더 빠르게 대응하고, 자신감을 갖고 혁신하며, 신뢰성을 타협하지 않고 새로운 기능을 출시할 수 있습니다. 이 속도와 통합 능력은 고객을 위한 경험을 확장해나가는 데 있어 매우 중요합니다."
>
> — **Mike Jones**, Director of Software Engineering, Warner Music Group

---

## Lakewatch: AI 에이전틱 시대를 위한 보안

오늘 우리는 점점 더 정교해지는 에이전트 공격자로부터 조직을 방어하도록 설계된 새로운 오픈형 에이전틱 SIEM(Security Information and Event Management), **Lakewatch** 를 발표합니다. Lakewatch는 보안, IT, 비즈니스 데이터를 단일의 거버넌스된 환경으로 통합하여 AI 기반 탐지 및 대응을 가능하게 합니다. 오픈 포맷을 통해 Lakewatch는 고객이 전례 없는 규모의 멀티모달 데이터를 수집·보존·분석하면서도 비용을 절감하고 벤더 종속성(Vendor Lock-in)을 제거할 수 있도록 지원합니다. 보안 팀은 기업 전반에 걸친 완전한 가시성을 확보하고, 방어용 보안 에이전트를 배포하여 대규모 위협 탐지와 대응을 자동화할 수 있습니다. Lakewatch는 현재 **Private Preview** 로 출시되며, Adobe와 Dropbox 같은 업계 선도 기업이 고객으로 참여하고 있습니다.

![Lakewatch 아키텍처 개요](https://www.databricks.com/sites/default/files/inline-images/databricks-announces-lakewatch-agentic-siem-blog-img-1.png)

### 에이전틱 시대의 보안

보안은 근본적으로 변화하고 있습니다. 사이버 공격은 더 이상 인간이 운용하는 것에만 국한되지 않습니다. AI 기반의 자동화된 공격이 점점 증가하고 있습니다. LLM이 오픈소스 코드에서 500개 이상의 제로데이 취약점을 발견했고, AI 에이전트는 버그 바운티 플랫폼에서 최상위 해커로 부상했으며, 국가 지원 집단들이 AI를 무기화하여 침입을 자동화하고 있습니다. 공격자들은 이제 머신 스케일로 운용되며, 취약점을 구성하고 공격을 조율하기 위해 24시간 365일 동작합니다.

이러한 머신 스케일 공격에 직면하여, 최고의 보안 운영 팀도 구조적 제약에 직면합니다. 오늘날의 보안 도구는 분석가가 경보를 수동으로 보강하고, 탐지 규칙을 직접 작성하고, 위협 헌팅 가설을 수 일에서 수 주에 걸쳐 검증하도록 요구합니다. 이러한 워크플로우는 인간 속도의 위협에는 효과적일 수 있었습니다. 하지만 24시간 365일 머신 속도로 동작하는 AI 기반 공격에 대해서는 아키텍처 자체가 병목이 됩니다. ZeroDayClock.com에 따르면, 취약점 노출부터 실제 공격까지의 평균 시간(Mean Time to Exploit)이 2025년의 23.2일에서 2026년에는 불과 1.6일로 줄었습니다.

대형 기업들은 매일 테라바이트, 심지어 페타바이트의 보안 데이터를 생성하지만, 전통적인 SIEM은 스토리지와 컴퓨팅을 결합하여 수집되는 모든 바이트에 금전적 패널티를 부과합니다. 팀은 수집을 제한하고, 라우팅 레이어를 통해 데이터를 필터링하고, 과거 데이터를 삭제하며, 채팅 로그와 영상 같은 멀티모달 소스를 완전히 무시하는 방식으로 대응합니다. 이는 위험한 비대칭을 만들어냅니다. 공격자는 AI 에이전트를 활용해 모든 것을 분석하고 어디서든 공격을 감행하는 반면, 방어자들은 자신들의 데이터 중 일부만 볼 수 있습니다.

### Lakewatch가 보안 운영을 바꾸는 방법

![Lakewatch 보안 운영 변환](https://www.databricks.com/sites/default/files/inline-images/databricks-announces-lakewatch-agentic-siem-blog-img-2.png)

**Lakewatch는 다음을 통해 이를 가능하게 합니다:**

- **엔터프라이즈 전체 거버넌스**: 테이블, 행, 열, 속성 수준의 세분화된 접근 제어와 모든 데이터에 대한 완전한 감사 가능성.
- **오픈 표준**: 오픈 사이버 보안 스키마 프레임워크(OCSF, Open Cybersecurity Schema Framework) 기반으로 구축되어 데이터가 독점 포맷에 잠기지 않습니다.
- **자동화된 수집**: Lakeflow Connect가 주요 보안 소스(AWS, Okta, Zscaler 등)의 수집 및 표준화된 테이블로의 정규화를 처리합니다.
- **진정한 데이터 소유권**: Delta Lake 또는 Apache Iceberg에 자체 클라우드 스토리지에 데이터를 저장하고, 어떤 클라우드에서도 쿼리를 실행하며, 벤더 종속을 방지합니다.

#### 에이전트로 에이전트에 맞서다

전통적인 SIEM은 데이터의 전체 컨텍스트에 접근할 수 없는 볼트온(bolt-on) AI 기능에 의존합니다. Lakewatch는 임베디드 AI를 보안 데이터가 실제로 존재하는 곳으로 직접 가져옵니다. **Genie** 는 새로운 로그 소스의 OCSF 파싱 및 수집, 최신 위협 인텔리전스에 기반한 신규 탐지 규칙 작성, 오탐(false positive)을 줄이기 위한 기존 규칙 수정, 자연어 질문의 SQL 쿼리 변환 등 중요한 워크플로우를 자동화합니다. **Genie Spaces** 는 보안 팀이 전문 쿼리 언어 대신 일반 영어로 페타바이트의 데이터를 쿼리할 수 있게 하여, 기술 수준에 관계없이 위협 헌팅을 민주화합니다.

![Genie를 통한 자연어 위협 헌팅](https://www.databricks.com/sites/default/files/inline-images/databricks-announces-lakewatch-agentic-siem-blog-img-3.png)

**주요 역량:**

- **Genie Code**: AI 어시스턴트가 수집 자동화, 신규 탐지 규칙 작성, 오탐 감소를 위한 규칙 수정, 조사를 위한 자연어 질문의 SQL 쿼리 변환을 수행합니다.
- **Genie Spaces**: 자연어 쿼리 인터페이스 및 에이전틱 하니스(harness)를 통해 모든 사용자가 복잡한 쿼리 언어를 배우지 않고도 복잡한 다단계 위협 헌팅을 수행할 수 있습니다.
- **Detection-as-Code**: YAML과 SQL 쿼리 또는 Python 노트북으로 탐지 규칙을 정의하고, 과거 데이터에 대해 백테스트하고, CI/CD 파이프라인을 통해 배포합니다.
- **커스텀 ML 탐지**: MLflow, Feature Store, Model Serving을 사용하여 보안 데이터에서 직접 ML 모델을 훈련하고 배포하여 이상 탐지, 행동 분석, 엔티티 리스크 스코어링 등을 가능하게 합니다.
- **강력한 대시보드**: 실시간 모니터링을 위한 AI 강화 시각화로 경영진, 운영, 컴플라이언스 대시보드를 생성합니다.

![Detection-as-Code 파이프라인](https://www.databricks.com/sites/default/files/inline-images/databricks-announces-lakewatch-agentic-siem-blog-img-4.png)

#### 페타바이트 규모의 효율적인 SecOps

스토리지와 컴퓨팅을 분리함으로써, 자체 클라우드 스토리지에 완전한 정합성의 보안 텔레메트리를 페타바이트 단위로 저장하고 컴퓨팅 비용만 지불할 수 있습니다. 서버리스 컴퓨팅을 사용하여 필요할 때만 분석을 실행합니다. 수 주 대신 수 년간의 핫 쿼리 가능한 데이터를 유지합니다.

- **데이터 소유권**: 오픈 포맷으로 사용자가 제어하는 클라우드 오브젝트 스토리지(S3, ADLS, GCS)에 보안 텔레메트리 저장.
- **장기 보존**: 비용 패널티 없이 수년간에 걸친 위협 헌팅을 위한 컴플라이언스 요구사항 충족.
- **예측 가능한 경제성**: 바이트당 라이선스 비용 없이 완전한 정합성의 로그를 대규모로 저장.
- **온디맨드 탄력적 컴퓨팅**: 세분화된 비용 제어로 필요할 때만 강력한 분석 및 ML 워크로드 프로비저닝.
- **서버리스 성능**: 관리할 인프라 없음. 쿼리 비용만 지불.

### Anthropic과의 파트너십 심화

두 회사의 기존 전략적 파트너십의 성공을 바탕으로, Databricks와 Anthropic은 에이전틱 보안 운영을 제공하기 위한 협력을 심화하고 있습니다. Anthropic의 Claude 모델이 Lakewatch를 구동하며, Claude의 고급 추론 능력을 활용하여 보안, IT, 비즈니스 데이터 전반의 신호를 상관 분석함으로써 위협을 더 빠르게 식별합니다. 또한 Anthropic은 Databricks를 자체 보안 레이크하우스로 활용하여 보안 및 비즈니스 데이터 전반에 걸친 완전한 가시성을 확보하고 위협을 조기에 탐지합니다.

### 오픈 보안 레이크하우스 에코시스템

Databricks는 오늘날의 위협이 고객이 데이터를 완전히 통제하는 가운데 에코시스템 전반의 오픈 협력을 필요로 한다고 믿습니다. 이에 우리는 **"오픈 보안 레이크하우스 에코시스템(Open Security Lakehouse Ecosystem)"** 을 발표합니다. 이는 고객이 텔레메트리를 오픈 포맷으로 자동 정규화하고, 자동화된 머신 속도 방어로 위협에 대응할 수 있도록 돕는 선도적인 보안 벤더 및 딜리버리 파트너 그룹입니다. Akamai, Anvilogic, Arctic Wolf, Cribl, Deloitte, Obsidian, Okta, 1Password, Palo Alto Networks, Panther, Proofpoint, Rearc, Slack, TrendAI, Wiz(현재 Google Cloud의 일부), Zscaler가 참여합니다.

> "Zscaler는 Databricks의 오픈 에코시스템에 대한 헌신을 공유합니다. 오픈 보안 레이크하우스 에코시스템에 합류하게 되어 기쁘며, 공동 고객에게 AI 네이티브 솔루션으로 AI 네이티브 공격을 방어하는 데 필요한 데이터와 도구를 제공하게 되었습니다."
>
> — **Eddie Parra**, VP Solutions Architect Partner Ecosystem, Zscaler

> "사이버 위협이 AI 기반의 머신 스케일 공격으로 진화함에 따라, 조직은 이에 맞설 근본적으로 새로운 아키텍처가 필요할 수 있습니다. Lakewatch는 보안 운영의 발전을 대표하며, Databricks 레이크하우스의 강력함을 SOC에 가져와 팀이 데이터를 활용하고, 지능형 에이전트를 배포하며, 진화하는 위협에 앞서 대응할 수 있도록 지원합니다."
>
> — **Jennifer Vitalbo**, Managing Director, Deloitte & Touche LLP

### Antimatter 및 SiftD.ai 인수로 보안 리더십 확장

오픈 에이전틱 SIEM 접근 방식을 가속화하기 위해 Databricks는 **Antimatter** 와 **SiftD.ai** 인수를 발표합니다.

**Antimatter** 는 UC Berkeley 보안 연구자들이 창업한 회사로, AI 에이전트를 위한 증명 가능한 안전 인증(Authentication) 및 권한 부여(Authorization)의 토대를 마련했습니다.

**SiftD.ai** 는 Splunk의 검색 처리 언어(SPL, Search Processing Language)를 만든 창업자와 Splunk 검색 스택의 수석 아키텍트들이 설립한 회사로, 대규모 탐지 엔지니어링과 현대적인 위협 분석에 깊은 전문성을 가져옵니다.

---

## Semantic Layer: Unity Catalog Business Semantics GA

AI와 데이터가 모든 기업의 핵심이 되면서, 비즈니스 개념에 대한 일관된 이해가 필수적이 되었습니다. 분석가, 엔지니어, 임원, 그리고 이제는 AI 에이전트까지 종종 동일한 데이터를 다르게 해석하여 메트릭 불일치, 상충하는 보고서, 신뢰 저하를 초래합니다.

수년 동안 기업들은 비즈니스 시맨틱을 BI 도구 내에서만 정의해왔습니다. 이 접근 방식에는 근본적인 결함이 있습니다. 도구별 메트릭 정의는 고립되어 다른 시스템에서 재사용할 수 없고, 데이터 파이프라인이나 AI 모델에 거버넌스가 없으며, 쿼리 엔진이 성능을 위해 알아야 하는 집계 및 필터링 로직이 숨겨집니다.

**Unity Catalog Business Semantics** 는 비즈니스 메트릭을 데이터 레이어에서 직접 정의하는 새로운 접근 방식입니다. 이 접근 방식은 세 가지 중요한 변화를 가져옵니다:

첫째, 단 한 번 정의된 메트릭이 대시보드, AI 모델, 데이터 엔지니어링 작업 등 조직 전반의 모든 워크로드에서 **재사용** 될 수 있습니다. 둘째, 메트릭이 Unity Catalog의 거버넌스를 상속받아 누가 어떤 비즈니스 개념에 접근하고 사용하는지 **완전한 감사 추적** 이 제공됩니다. 셋째, AI 에이전트가 비즈니스 컨텍스트를 이해하고 **신뢰할 수 있는 메트릭** 을 사용하여 올바른 분석을 수행합니다.

### 작동 방식

Unity Catalog Business Semantics는 메트릭 뷰(Metric Views)를 통해 비즈니스 개념을 정의합니다. 메트릭 뷰는 기본 델타 테이블 위에 비즈니스 로직을 캡슐화하는 거버넌스된 오브젝트입니다.

```sql
-- Unity Catalog에서 메트릭 뷰 정의
CREATE METRIC VIEW main.sales.monthly_revenue AS
SELECT
  date_trunc('month', order_date) AS month,
  SUM(order_amount) AS revenue,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM main.sales.orders
WHERE status = 'completed'
```

이렇게 한 번 정의하면, SQL 쿼리, AI/BI 대시보드, Genie 대화, 데이터 파이프라인 어디에서든 동일한 메트릭을 참조할 수 있습니다.

### 주요 역량

- **단일 진실 원천(Single Source of Truth)**: 메트릭을 한 번 정의하고 어디에서나 사용. 도구 간 KPI 불일치를 해소합니다.
- **AI 에이전트를 위한 비즈니스 컨텍스트**: Genie와 Agent Bricks가 비즈니스 개념을 이해하고 올바른 계산 로직으로 데이터를 분석합니다.
- **자동 집계 인식**: 쿼리 엔진이 메트릭 정의를 이해하여 불필요한 재계산 없이 최적의 쿼리를 실행합니다.
- **거버넌스 내장**: Unity Catalog의 접근 제어, 계보(lineage), 감사가 비즈니스 시맨틱에도 자동으로 적용됩니다.
- **오픈 소스**: Unity Catalog Business Semantics 스펙이 오픈 소스로 공개되어 광범위한 에코시스템 통합을 지원합니다.

---

## 레이크하우스의 진화: 하나의 플랫폼

이 네 가지 제품은 각각 독립적이지만, 함께 보면 Databricks 플랫폼이 어떻게 진화하고 있는지를 나타냅니다.

아래 표는 각 제품이 해결하는 문제와 레이크하우스 진화에서의 역할을 요약합니다.

| 제품 | 해결하는 문제 | 레이크하우스에서의 역할 |
|------|-------------|----------------------|
| **Databricks Apps** | 데이터/AI 앱 개발의 복잡성, 거버넌스 부재 | 레이크하우스 위에서 직접 앱을 빌드하고 배포하는 서버리스 앱 런타임 |
| **Lakebase** | OLTP와 OLAP의 사일로, 레거시 DB의 운영 부담 | 레이크하우스에 통합된 완전 관리형 서버리스 Postgres 운영 DB |
| **Lakewatch** | AI 기반 사이버 공격의 급증, 전통 SIEM의 비용 및 확장 한계 | 레이크하우스 위에서 동작하는 오픈형 에이전틱 SIEM |
| **Semantic Layer** | BI 도구별 메트릭 파편화, AI 에이전트의 비즈니스 컨텍스트 부재 | Unity Catalog에서 메트릭을 한 번 정의하고 모든 곳에서 재사용 |

이 표가 보여주는 것처럼, 각 제품은 레이크하우스의 빈틈을 채웁니다. Lakebase는 트랜잭션 레이어를 추가하고, Apps는 애플리케이션 레이어를 추가하며, Lakewatch는 보안 레이어를 추가하고, Semantic Layer는 비즈니스 의미 레이어를 추가합니다. 결과적으로 레이크하우스는 더 이상 단순한 분석 플랫폼이 아니라 현대 AI 기반 기업의 완전한 데이터 인텔리전스 플랫폼이 됩니다.

---

{% hint style="info" %}
**지금 시작하기**

- **Databricks Apps**: [databricks.com/product/databricks-apps](https://www.databricks.com/product/databricks-apps)
- **Lakebase**: [databricks.com/product/lakebase](https://www.databricks.com/product/lakebase) | [시작 가이드](https://docs.databricks.com/aws/en/oltp/projects/get-started)
- **Lakewatch**: [databricks.com/product/lakewatch](https://www.databricks.com/product/lakewatch) (Private Preview)
- **Unity Catalog Business Semantics**: [공식 블로그](https://www.databricks.com/blog/redefining-semantics-data-layer-future-bi-and-ai)
{% endhint %}
