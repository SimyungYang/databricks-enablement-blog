# Unity Catalog Business Semantics GA 발표: 데이터 시맨틱 레이어의 재정의

**BI와 AI를 위한 통합·오픈 비즈니스 시맨틱스**

작성자: Can Efeoglu, Sachin Thakur, Richard Tomlinson, Justin Talbot, Daniel Rosenthal, Jasmeet Jaggi | 2026년 4월 2일

> **원문**: [Bringing Structured Data to AI Agents with UC Business Semantics](https://www.databricks.com/blog/bringing-structured-data-ai-agents-uc-business-semantics)
>
> **참고**: 원문 URL(https://www.databricks.com/blog/bringing-structured-data-ai-agents-uc-business-semantics)은 현재 404 상태입니다. 동일한 주제의 실제 블로그 포스트 URL은 https://www.databricks.com/blog/redefining-semantics-data-layer-future-bi-and-ai 입니다.

![Hero Image](https://www.databricks.com/sites/default/files/2026-03/announcing-ga-unity-catalog-business-semantics-og-1.png?v=1773923272)

---

{% hint style="info" %}
**요약**

- Unity Catalog Business Semantics(비즈니스 시맨틱스)가 GA(정식 출시)되었습니다. 메트릭, 디멘션, 규칙을 데이터 레이어에서 한 번만 정의하면 모든 대시보드, SQL 쿼리, 노트북, AI 에이전트가 동일한 신뢰할 수 있는 정의를 기반으로 동작합니다.
- 핵심 구현이 Apache Spark에 오픈소스로 공개되어, 비즈니스 시맨틱스가 단일 플랫폼을 넘어 확장되고 개방성과 상호운용성에 대한 의지를 강화합니다.
- Metric Views(메트릭 뷰)는 리니지, 권한, 성능 제어와 함께 표시 이름, 형식, 동의어 같은 시맨틱 메타데이터를 포함하여 일관된 비즈니스 KPI를 제공합니다.
{% endhint %}

---

데이터와 AI가 모든 기업의 핵심이 되어감에 따라, 비즈니스 개념에 대한 일관된 이해가 필수적으로 요구되고 있습니다. 분석가, 엔지니어, 경영진, 그리고 이제는 AI 에이전트까지도 동일한 데이터를 서로 다르게 해석하는 경우가 많아, 메트릭 불일치(metric drift), 상충하는 보고서, 신뢰 저하로 이어집니다. 오랜 시간 동안 이러한 비즈니스 개념들은 BI 도구와 대시보드 내부에 갇혀 있었습니다. 에이전트 AI(agentic AI) 시대에서 에이전트가 데이터를 추론하고 자율적으로 행동하는 상황이 되면, 파편화된 정의는 단순히 혼란을 초래하는 데 그치지 않고 그 혼란을 더욱 확대시킵니다.

기업은 데이터와 AI 플랫폼의 핵심에서 정의되고, 한 번 거버닝되어 어디서나 적용될 수 있는 통합된 시맨틱 기반이 필요합니다. 그리고 그것은 반드시 개방형(open)이어야 합니다.

비즈니스 시맨틱스는 조직이 수익, 성장, 고객 가치, 리스크를 어떻게 측정하는지를 정의합니다. 이러한 정의들은 전략적 자산으로서, 독점 시스템에 종속되거나 단일 애플리케이션 레이어에만 국한될 수 없습니다.

오늘, 우리는 이를 바꾸고자 합니다. **Unity Catalog Business Semantics** 의 정식 출시(GA)를 발표합니다. 이는 BI 대시보드, 개발자 워크플로우, AI 에이전트 전반에 걸쳐 일관되고 신뢰할 수 있는 컨텍스트를 제공하는 통합·오픈 시맨틱 기반입니다. 이 기반을 진정으로 이식 가능하게 만들기 위해, Apache Spark에 핵심 구현도 오픈소스로 공개하며, Unity Catalog OSS v0.5에서의 지원도 곧 제공될 예정입니다.

## 기존 비즈니스 시맨틱스 접근 방식의 한계

고객들은 오랫동안 BI 도구별 시맨틱 레이어를 사용해 왔으며, 이 방식은 해당 도구 내에서는 일관성을 제공하지만 다음과 같은 한계가 있습니다:

- **독점적이고 파편화됨**: 멀티 도구·멀티 에이전트 환경에서 각 BI 모델은 자신만의 언어로 동작합니다. 그 결과, 정의들이 대시보드, 모델, 스프레드시트 내부에 갇혀 조직 전반에서 거버닝하거나, 액세스 정책을 집행하거나, 리니지를 추적하는 것이 거의 불가능해집니다.
- **너무 하위 레이어에 위치한 정의**: 이러한 레이어들이 데이터 기반이 아닌 표현 계층(presentation tier)에 위치하기 때문에, 팀들은 서로 다른 대시보드와 보고서를 위해 동일한 메트릭을 반복적으로 재정의합니다. 이 다운스트림 방식은 시맨틱스를 취약하고, 일관성 없고, 확장하기 어렵게 만듭니다.
- **AI에 비적합**: 기존 레이어는 빠르게 변화하는 비즈니스 질문이나 AI 에이전트의 열린 프롬프트에 따라가지 못하는 무거운 사전 모델링에 의존합니다. 변경이 생길 때마다 전문가 개입이 필요해 대응 속도가 저하되고 신뢰가 손상됩니다.

이러한 한계들은 오랫동안 데이터 및 AI 팀을 좌절시켜 왔습니다. 민첩성과 신뢰할 수 있는 답변이 협상 불가능한 오늘날 AI 중심 환경에서, 이는 발전을 가로막는 심각한 장벽이 되었습니다.

## Unity Catalog Business Semantics: 통합·오픈 접근 방식

Unity Catalog Business Semantics는 시맨틱스가 이제 Databricks Data Intelligence Platform의 핵심에서 통합·거버닝된다는 근본적인 전환을 의미합니다. Unity Catalog에 직접 내장되어, 이미 의존하고 있는 동일한 거버넌스, 보안, 리니지를 확장하며 이러한 정의를 업무 현장 어디서나 이용 가능하게 합니다.

이 접근 방식은 세 가지 핵심 이점을 제공합니다:

- **개방적이고 재사용 가능**: SQL과 API를 통해 액세스하며, 비즈니스 시맨틱스를 대시보드, 노트북, 애플리케이션, AI 에이전트 전반에서 쿼리할 수 있습니다. 개방형 포맷으로 저장되어 완전히 이식 가능하며, 독점 도구에 종속되지 않습니다.
- **핵심에서 거버닝**: 기반 데이터와 동일한 거버넌스 정책을 상속합니다. 이 업스트림 방식은 데이터와 비즈니스 의미 모두에 대한 단일 진실의 원천(single source of truth)을 제공하기 위해 일관된 사용, 거버넌스, 리니지, 액세스 제어를 보장합니다.
- **AI를 위해 설계**: 풍부한 시맨틱 메타데이터는 에이전트가 새로운 질문에 정확하게 답하고, 무거운 사전 모델링 없이 비즈니스 개념이 진화함에 따라 적응하는 데 필요한 컨텍스트를 제공합니다.

---

> Metric Views는 우리의 메트릭 표준화에 도움을 주었고, 숫자를 일치시키는 비즈니스 업무 부담을 극적으로 줄여주었습니다. 쿼리가 현저히 빨라졌는데, 어떤 경우에는 최대 10배까지 빨라졌고, 대시보드 구축도 더 쉬워졌으며, 더 일관되고 사전 집계된 데이터 덕분에 Genie의 정확도도 의미 있게 개선되었습니다.
>
> — Pedro Alves, Data Manager, Tech Growth, iFood

---

> Unity Catalog Business Semantics는 Zalando 전반에 걸쳐 비즈니스 메트릭이 정의되고 소비되는 방식에서 일관성, 신뢰, 통제를 확립할 수 있는 흥미로운 기회를 제공합니다. BI 대시보드, 노트북 및 기타 도구 전반에서 데이터 기반 의사결정을 정렬하는 데 유망한 기여가 될 것입니다.
>
> — Timur Yüre, Engineering Manager, Zalando

---

## 비즈니스 시맨틱스를 위한 오픈소스 기반

Unity Catalog Business Semantics의 핵심 목표 중 하나는 고객이 개방적이고, 이식 가능하며, 기존 에코시스템 전반에서 동작하도록 설계된 방식으로 비즈니스 의미를 정의할 수 있게 하는 것입니다. 잠금(lock-in) 없이 말입니다.

시맨틱 정의는 BI 도구, SQL 워크로드, AI 에이전트와 원활하게 통합되어야 하며, 플랫폼과 소비 패턴이 진화함에 따라 내구성 있게 유지되어야 합니다.

이를 실현하기 위해, 우리는 Apache Spark OSS에서 핵심 Metric View 구현을 오픈소스로 공개하고 있으며, 예정된 Apache Spark 릴리스를 목표로 합니다([SPARK-54119](https://issues.apache.org/jira/browse/SPARK-54119)에서 진행 상황을 확인할 수 있습니다). Unity Catalog OSS v0.5에서의 지원도 곧 제공될 예정입니다.

이를 통해 고객은 오픈 시스템에서 표준 SQL을 사용하여 비즈니스 시맨틱스를 정의하고, 다운스트림 도구가 아닌 데이터 기반에서 거버닝하며, 분석과 AI 영역 전반에서 일관되게 재사용할 수 있게 됩니다.

Databricks는 비즈니스 시맨틱스 분야의 상호운용성 개선을 위한 광범위한 업계 노력도 지원합니다. 회사는 OSI(Open Semantic Interchange) 이니셔티브에 참여하여 적극적으로 기여하고 있습니다. 우리는 OSI와 같은 이니셔티브를 에코시스템 정렬을 향한 중요한 단계로 보고 그에 맞게 기여하면서, 고객이 규모 있게 신뢰할 수 있는 개방적이고 거버닝된 시맨틱 기반 구축에 지속적으로 집중할 것입니다.

---

{% hint style="info" %}
**가이드**: [현대 분석을 위한 컴팩트 가이드 읽기](https://www.databricks.com/sites/default/files/2026-02/2026-01-eb-compact-guide-to-data-analytics-og-1200x628.png)
{% endhint %}

---

## GA 릴리스의 새로운 기능 상세

### Metric Views: 신뢰할 수 있는 일관된 KPI

이번 GA 릴리스의 핵심은 **Metric Views** 입니다. Metric Views는 표시 이름, 형식, 동의어 같은 시맨틱 메타데이터와 함께 비즈니스 KPI의 신뢰할 수 있는 일관된 정의를 확립하여, 사람과 AI 모두 그 정의를 자신 있게 해석하고 적용할 수 있게 합니다.

Metric Views를 통해 데이터 매핑, 측정값(measure), 디멘션(dimension)을 SQL로 중앙에서 정의하고 Unity Catalog에서 직접 거버닝할 수 있습니다. 이렇게 정의된 내용은 모든 서페이스(AI/BI 대시보드, Genie, 노트북, SQL 애플리케이션, Databricks에 연결된 서드파티 도구)에서 이식 가능하게 됩니다.

각 메트릭이 선언적으로 정의되기 때문에, 엔진은 쿼리 시 기반 SQL을 결정론적으로 컴파일하고 실행하여, 사람이든 AI 에이전트든 모든 소비자가 어디서 어떻게 액세스하든 동일한 정의로부터 동일한 결과를 얻도록 보장합니다.

![Metric Views Screenshot](https://www.databricks.com/sites/default/files/inline-images/ga-unity-catalog-business-semantics-02-1.png)

### 새로운 기능: 쿼리 성능을 위한 구체화(Materialization)

Unity Catalog Business Semantics는 거버닝된 정의와 대규모 성능을 **구체화(materialization)** 를 통해 결합합니다. 팀이 어떤 집계 테이블을 사용할지 결정하거나, 다른 성능 티어를 위해 로직을 중복하거나, 다른 워크로드를 위한 별도 파이프라인을 구축하도록 강요하는 대신, 시맨틱 레이어가 성능을 자동으로 처리합니다. 동작 방식은 다음과 같습니다:

- **자동 사전 집계**: 메트릭에 대한 구체화를 정의하면, 플랫폼이 수동 개입 없이 최적화된 사전 집계 결과를 유지합니다.
- **증분 갱신(Incremental refresh)**: 구체화된 결과는 증분 업데이트를 통해 최신 상태를 유지하므로, 메트릭이 오래되는 일이 없고 전체 재계산이 거의 필요하지 않습니다.
- **지능형 쿼리 재작성(Intelligent query rewriting)**: 쿼리 시 엔진이 최적의 구체화를 활용하도록 쿼리를 재작성합니다.
- **투명한 라우팅(Transparent routing)**: 사용자는 항상 동일한 방식으로 메트릭을 쿼리하고, 시스템은 뒤에서 각 요청을 가장 빠른 경로로 라우팅합니다.

구체화 기능은 현재 Preview 상태입니다. 자세한 내용은 문서([AWS](https://docs.databricks.com/aws/en/metric-views/), [Azure](https://docs.databricks.com/azure/en/metric-views/), [GCP](https://docs.databricks.com/gcp/en/metric-views/))를 참조하세요.

### 새로운 UI 및 에이전틱 AI 경험으로 작성(Authoring)

이제 Public Preview에서 Unity Catalog Explorer의 새로운 포인트-앤-클릭(point-and-click) UI를 통해 Metric Views를 생성하고 관리할 수 있습니다. 복잡한 SQL이나 깊은 데이터 모델링 전문 지식 없이 기술 및 비기술 사용자 모두가 시맨틱 모델링에 접근할 수 있게 됩니다. UI를 통해 테이블 간 관계를 시각적으로 정의하고, 메트릭을 인라인으로 차트화하며, 브라우저를 떠나지 않고 모든 것을 엔드-투-엔드로 테스트할 수 있습니다. UI 기반 작성에 대한 자세한 내용은 문서([AWS](https://docs.databricks.com/aws/en/metric-views/), [Azure](https://docs.databricks.com/azure/en/metric-views/), [GCP](https://docs.databricks.com/gcp/en/metric-views/))를 참조하세요.

Genie Code는 에이전틱 AI를 작성 워크플로우에 직접 도입함으로써 작성 프로세스를 더욱 가속화합니다. 빈 페이지에서 시작하는 대신, Genie Code는 다음을 수행할 수 있습니다:

- **시맨틱 모델 빠른 부트스트랩**: 측정값, 디멘션, 동의어, 문서를 제안하여 팀이 주 단위가 아닌 분 단위로 시작할 수 있게 합니다.
- **정제 및 리팩토링**: 기존 정의의 문제점을 파악하고 비즈니스 로직이 진화함에 따라 개선 사항을 추천합니다.
- **변경 사항 검증**: 실제 데이터에 대해 제안된 수정 사항을 테스트하여 오류가 전파되기 전에 잡아냅니다.
- **세밀한 변경 관리 지원**: 무엇이 변경되었는지 완전한 가시성을 제공하면서 개별 메트릭 변경 사항을 검토하고 승인합니다.

Metric Views는 KPI 정의를 넘어섭니다. 각 메트릭 뷰는 표시 이름, 형식, 동의어 같은 풍부한 시맨틱 메타데이터를 담고 있어, 사람과 AI 모두에게 이해하고 사용할 수 있게 합니다. 이를 통해 대시보드와 대화형 UI 전반에서 일관된 표현을 보장하는 동시에 AI가 비즈니스 용어와 자연어 쿼리를 올바르게 해석하도록 도와줍니다.

## 비즈니스 시맨틱스가 Databricks AI/BI를 강화하는 방법

이번 GA 릴리스로 AI/BI 대시보드와 Genie가 Unity Catalog Business Semantics와 완전히 통합되었습니다. 실제로 세 가지 핵심 이점이 실현됩니다:

- **거버닝된 메트릭으로 구동되는 AI/BI 대시보드**: Unity Catalog의 Metric Views를 기반으로 직접 대시보드를 구축할 수 있습니다. 모든 시각화, 필터, 드릴스루(drill-through), 비교가 동일한 인증된 측정값과 디멘션 세트를 사용하여 팀과 도구 전반에서 일관된 숫자를 보장합니다.

- **비즈니스 언어로 기반된 Genie**: Genie 스페이스를 Metric Views 바로 위에서 생성할 수 있습니다. 즉, Genie가 답하는 모든 자연어 쿼리가 추론된 로직이 아닌, 거버닝된 결정론적 정의에 기반합니다. Metric Views가 런타임 시 논리적 쿼리로 컴파일되기 때문에, 사용자는 항상 올바르고 일관된 결과를 얻습니다. Genie는 더 이상 메트릭을 환각(hallucination)하지 않고, 단일 진실의 원천으로부터 해결합니다.

- **대시보드 로직을 시맨틱 레이어로 승격**: 기존 Metric View 없이 새로운 AI/BI 대시보드를 생성할 때, 구축하는 모든 테이블 조인, 필터, 계산 필드를 단 하나의 액션으로 Unity Catalog의 새로운 Metric View로 승격할 수 있습니다. 이는 즉시 조직의 시맨틱 레이어의 일부가 되어 Genie, SQL, 노트북, 외부 BI 도구 전반에서 이용 가능해집니다. 또한 대시보드가 Metric View 구체화의 혜택을 자동으로 받아 기반 쿼리의 성능이 크게 향상됩니다.

![AI/BI Genie with Metric Views](https://www.databricks.com/sites/default/files/inline-images/GenieCodeMVNew-2.gif)

## 즐겨 사용하는 도구로 시맨틱스 확장

강력한 시맨틱 기반은 단일 플랫폼을 넘어 이동할 때 더욱 가치 있어집니다. 이것이 바로 Unity Catalog Business Semantics와 직접 통합하는 풍부한 기술 파트너 에코시스템과 긴밀히 협력하는 이유입니다.

![Partner Ecosystem](https://www.databricks.com/sites/default/files/inline-images/ga-unity-catalog-business-semantics-04-1.png)

**Tableau**: Tableau는 Databricks Unity Catalog Business Semantics를 포함한 외부 메트릭 공급자로부터의 위임된 시맨틱스(delegated semantics)를 관계형 데이터 모델 내에서 지원할 계획입니다. 이를 통해 분석가들이 메트릭이 기반 시맨틱 레이어에 의해 일관되게 정의되고 정확하게 집계된다는 것을 신뢰할 수 있게 됩니다. 이 통합은 2026년 말에 제공될 예정입니다.

> Tableau는 Unity Catalog Business Semantics를 관계형 데이터 모델에 도입하게 되어 기쁩니다. 분석가와 조직이 메트릭과 메타데이터를 한 번 정의하고 Tableau가 일관되고 신뢰할 수 있는 인사이트를 위해 올바른 시맨틱스를 자동으로 적용할 수 있게 됩니다.
>
> — Nicolas Brisoux, Sr. Director Product Management, Tableau

**Sigma Computing**: Sigma는 실시간으로 Metric Views를 쿼리하여 Databricks Unity Catalog Business Semantics와 직접 통합함으로써, 데이터 이동 없이 최신 정의가 즉시 반영되도록 합니다. 이 아키텍처를 통해 Sigma는 실행 시점에 Unity Catalog의 보안 및 거버넌스 프로토콜을 엄격하게 상속하며 Lakehouse의 투명한 확장으로 동작할 수 있습니다.

> Sigma에서 우리는 Unity Catalog Business Semantics와의 통합을 위해 열심히 작업하고 있습니다. 이를 통해 고객이 Sigma의 스프레드시트 같은 경험과 거버닝된 비즈니스 정의를 결합하여 모든 사람을 위한 빠르고, 일관되며, 신뢰할 수 있는 분석을 보장할 수 있기 때문입니다.
>
> — Jordan Stein, Product Manager, Sigma

**ThoughtSpot**: 올해 말, ThoughtSpot은 Unity Catalog Metric Views에 대한 네이티브 지원을 추가하여 Spotter 사용자가 자연어로 거버닝된 Databricks 메트릭을 즉시 쿼리할 수 있게 됩니다. 이를 통해 커스텀 SQL이 제거되고 조직이 데이터 스택 전반에서 신뢰할 수 있는 비즈니스 메트릭에 유연하고, 정확하며, 빠른 액세스를 얻게 됩니다.

> ThoughtSpot은 Unity Catalog Business Semantics를 통해 Databricks와의 파트너십을 심화하게 되어 기쁩니다. 고객이 비즈니스 시맨틱스를 관리하는 방법과 장소에서 훨씬 더 많은 유연성을 갖게 됩니다.
>
> — Francois Lopitaux, SVP of Product, ThoughtSpot

**Hex**: Unity Catalog Metric Views가 이제 Hex와 완전히 통합되었습니다. 사용자는 Databricks 연결에서 직접 Metric Views를 탐색하고, Hex 노트북에서 SQL로 쿼리하며, 거버닝된 정의를 기반으로 데이터 앱을 구축할 수 있습니다. 이를 통해 메트릭을 재정의하지 않고 탐색에서 프로덕션 앱으로 쉽게 이동할 수 있습니다.

> Databricks Unity Catalog Metric Views가 Hex에서 사용 가능해짐으로써, 팀들이 신뢰할 수 있는 거버닝된 메트릭으로 작업하여 불일치를 줄이고 신뢰할 수 있는 인사이트로 더 빠르게 나아갈 수 있습니다.
>
> — Armin Efendic, Partner Engineer, Hex

**Omni**: Omni를 통해 팀들은 스프레드시트, SQL, AI 기반 채팅 같은 친숙한 경험으로 Metric Views를 분석할 수 있습니다. Omni는 양방향 통합도 지원하여, Omni에서 이루어진 업데이트가 Unity Catalog로 다시 푸시될 수 있어 기업 전반에서 정의의 일관성을 유지합니다. 이를 통해 데이터 팀과 비즈니스 전문가 모두 시맨틱 모델에 직접 기여할 수 있습니다.

> AI를 비즈니스 컨텍스트에 기반시키는 것이 신뢰할 수 있게 만드는 유일한 방법입니다. Unity Catalog Metric Views와의 통합은 거버닝된 정의를 모든 인터페이스(AI, 스프레드시트, 대시보드, SQL)에 제공합니다. Omni와 Databricks 간의 양방향 동기화를 통해 팀들은 두 시스템 중 어디서든 메트릭을 정의하고 업데이트하면서 모든 것을 정렬 상태로 유지할 수 있습니다. 이러한 일관성은 고객이 셀프 서비스를 확장하고, AI 도입을 가속화하며, 신뢰할 수 있는 고객 대면 데이터 제품을 구동하는 데 도움을 줍니다.
>
> — Jamie Davidson, Co-founder, Omni

**Atlan**: Atlan의 UC Metrics와의 네이티브 통합은 가장 중요한 메트릭을 Atlan Context Graph에 직접 가져와 추가적인 권한 오버헤드 없이 리니지, 소유자, 비즈니스 정의와 연결합니다. 이를 통해 팀들이 업무 흐름 속에서 메트릭에 대한 단일하고 신뢰할 수 있는 뷰를 가지게 되어 더 빠른 문제 해결, 더 나은 의사결정, 대규모 AI 준비 데이터가 가능해집니다.

> 메트릭은 모든 기업의 Data & AI 플랫폼의 맥박입니다. UC Metrics를 리니지, 비즈니스 컨텍스트, 추가 권한 없이 Atlan의 Context Graph에 도입함으로써, 고객들은 이전에 접근하기 어려웠던 운영 인텔리전스를 얻게 됩니다. 이는 대규모 AI 준비 데이터를 향한 의미 있는 단계입니다.
>
> — Chandru, Product Leader, Atlan

**Monte Carlo**: Monte Carlo는 이제 Unity Catalog의 Metric Views를 지원하여 표준화된 비즈니스 메트릭과 이를 구동하는 파이프라인 전반에서 엔드-투-엔드 관측성을 제공합니다.

> 신뢰할 수 있는 데이터와 AI는 거버닝된 비즈니스 메트릭에서 시작됩니다. Unity Catalog Metrics는 대규모로 KPI를 표준화하기 쉽게 만들며, Monte Carlo와 함께 데이터 리더들은 그 인사이트가 실제 비즈니스 임팩트를 이끌 것이라 신뢰할 수 있습니다.
>
> — Lior Gavish, Co-founder and CTO, Monte Carlo

**Collibra**: Collibra는 Databricks 메트릭에 대한 신뢰할 수 있는 가시성을 제공하여 사람과 AI 에이전트 모두 비즈니스 의사결정을 위해 쉽게 발견하고 사용할 수 있도록 합니다. 향상된 통합은 메트릭 시각화를 개선하고, Collibra 승인된 메트릭이 Databricks로 직접 흐르게 하며, 데이터 자산 전반에서 일관되고 신뢰할 수 있는 메트릭을 보장하기 위한 양방향 동기화를 추가합니다.

> 거버닝되고 일관된 메트릭은 AI 에이전트와 데이터 사용자가 워크플로우를 이해하고, 신뢰하며, 자동화하는 데 필수적입니다. 공동 고객들은 Databricks와 Collibra 간의 긴밀한 협력을 지속적으로 원하고 있습니다.
>
> — Tom Dejonghe, VP, Product Management, Data Governance, Collibra

**Domo**: 이제 Unity Catalog Metric Views와 통합되어 거버닝된 Databricks 메트릭이 Domo의 대시보드, 분석, AI 기반 워크플로우로 직접 흐를 수 있습니다. 이를 통해 중복이 줄고, 거버넌스가 강화되며, 신뢰할 수 있는 KPI에 대한 인사이트 도출 시간이 단축됩니다.

> Databricks의 거버닝된 메트릭을 Domo와 통합함으로써 고객들이 중복을 줄이고, 거버넌스를 개선하며, 신뢰할 수 있는 KPI에 대한 인사이트를 가속화하는 데 도움을 줍니다.
>
> — Matthew Payne, VP Engineering, Domo

**Anomalo**: Anomalo는 Unity Catalog Governed Metrics의 런치 파트너로, Databricks의 통합 시맨틱 레이어와 Anomalo의 자동화된 메트릭 모니터링을 결합합니다. 이 통합은 기업이 드리프트와 데이터 품질 문제를 조기에 감지하여 중요한 의사결정을 위한 정확하고 신뢰할 수 있는 메트릭을 보장하도록 돕습니다.

> Databricks의 통합 시맨틱 레이어와 Anomalo의 메트릭 모니터링을 결합함으로써, 고객들이 드리프트를 조기에 감지하고 메트릭을 대규모로 정확하고 신뢰할 수 있게 유지하도록 돕습니다.
>
> — Amy Reams, Vice President of Business Development and Marketing, Anomalo

이러한 통합들과 향후 예정된 통합들이 함께, 일관되고 거버닝된 시맨틱스가 광범위한 분석 및 AI 에코시스템 전반에 흐르며 Databricks를 훨씬 넘어 도달하게 됩니다.

## Unity Catalog Business Semantics 시작하기

이번 런치에 매우 흥분됩니다. 시맨틱스가 이제 데이터 플랫폼의 핵심 부분이 되면서, 기업 컨텍스트가 대시보드와 AI 에이전트에서 노트북과 외부 BI 도구까지 어디서나 흐르게 되어, 메트릭 사일로, 벤더 종속, 도구 간 불일치가 제거됩니다. 개방형 기반 위에 구축되어, 데이터가 있는 모든 곳에서 시맨틱 레이어가 작동합니다.

비즈니스 시맨틱스 정의, 권한 제어, 다양한 소비 방법에 대한 시작 가이드는 문서([AWS](https://docs.databricks.com/aws/en/metric-views/), [Azure](https://docs.databricks.com/azure/en/metric-views/), [GCP](https://docs.databricks.com/gcp/en/metric-views/))를 참조하세요.

제품 데모를 통해 AI/BI 대시보드 및 Genie 스페이스와 함께하는 비즈니스 시맨틱스를 직접 확인해 보세요:

- Unity Catalog Metric Views 개요
- AI/BI에서 Metric Views 활용
- SQL 편집기에서 Metric Views 쿼리
