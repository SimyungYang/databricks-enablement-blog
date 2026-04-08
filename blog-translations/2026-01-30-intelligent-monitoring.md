---
original_title: "Data Quality Monitoring at scale with Agentic AI"
authors: "Jacqueline Li, Danny Chiao, Saravanan Balasubramanian"
date: "2026-02-04"
category: "Product"
original_url: "https://www.databricks.com/blog/data-quality-monitoring-scale-agentic-ai"
translated_date: "2026-04-07"
note: "요청된 URL(introducing-intelligent-monitoring)은 404로 확인되지 않아, 동일 주제(Intelligent/Agentic Data Quality Monitoring)의 공식 블로그 포스트로 대체하였습니다."
---

# Agentic AI로 대규모 데이터 품질 모니터링하기

> **원문**: [Data Quality Monitoring at scale with Agentic AI](https://www.databricks.com/blog/data-quality-monitoring-scale-agentic-ai)

_Unity Catalog 기반으로 문제를 조기에 감지하고 신속하게 해결하기_

![데이터 품질 모니터링 개요](https://www.databricks.com/sites/default/files/2026-02/image1_0.png?v=1770221465)

**게시일:** 2026년 2월 4일 | **카테고리:** Product | **읽는 시간:** 5분

**저자:** Jacqueline Li, Danny Chiao, Saravanan Balasubramanian

---

#### 요약

- 수동으로 작성된 규칙 기반 데이터 품질 관리는 분석 및 AI 목적으로 데이터 자산이 성장할수록 확장되지 않습니다.
- 에이전틱(Agentic) 데이터 품질 모니터링은 정상적인 데이터 패턴을 학습하고 중요한 데이터셋 전반에서 문제를 감지합니다.
- Unity Catalog 리니지(lineage)와 같은 플랫폼 네이티브 신호는 팀이 엔터프라이즈 규모에서 더 빠르게 문제를 해결하도록 돕습니다.

---

## 대규모 데이터 품질의 과제

조직이 더 많은 데이터 및 AI 제품을 구축함에 따라 데이터 품질 유지는 점점 더 어려워집니다. 데이터는 경영진 대시보드부터 전사적 Q&A 봇까지 모든 것을 구동합니다. 테이블이 최신 상태가 아니면 오래된 정보 혹은 잘못된 답변으로 이어지고, 이는 비즈니스 결과에 직접적인 영향을 미칩니다.

대부분의 데이터 품질 접근 방식은 이러한 현실에 맞게 확장되지 못합니다. 데이터 팀은 소수의 테이블에만 수동으로 정의된 규칙을 적용합니다. 데이터 자산이 성장할수록 사각지대가 생기고 전체적인 상태에 대한 가시성이 제한됩니다.

팀은 각자 고유한 데이터 패턴을 가진 새로운 테이블을 지속적으로 추가합니다. 모든 데이터셋에 대해 커스텀 검사를 유지하는 것은 지속 가능하지 않습니다. 실제로는 소수의 중요한 테이블만 모니터링되고 대부분의 데이터 자산은 확인되지 않은 채로 남습니다.

그 결과, 조직은 그 어느 때보다 많은 데이터를 보유하고 있지만 이를 사용하는 데 대한 확신은 오히려 줄어들고 있습니다.

---

## Agentic 데이터 품질 모니터링 소개

오늘, Databricks는 AWS, Azure Databricks, GCP에서 **Data Quality Monitoring** 의 Public Preview를 발표합니다.

데이터 품질 모니터링(Data Quality Monitoring)은 단편적인 수동 검사를 대규모로 설계된 에이전틱(agentic) 접근 방식으로 대체합니다. 정적 임계값 대신, AI 에이전트가 정상적인 데이터 패턴을 학습하고 변화에 적응하며 데이터 자산을 지속적으로 모니터링합니다.

Databricks 플랫폼과의 깊은 통합은 단순한 감지 이상의 기능을 제공합니다.

- **근본 원인이 업스트림 Lakeflow 잡(job) 및 파이프라인에서 직접 표면화됩니다.** 팀은 데이터 품질 모니터링에서 영향받은 잡으로 바로 이동하고, Lakeflow의 내장 옵저버빌리티(observability) 기능을 활용해 장애에 대한 더 깊은 컨텍스트를 파악하고 더 빠르게 문제를 해결할 수 있습니다.
- **Unity Catalog 리니지(lineage)와 인증된 태그를 사용해 문제의 우선순위가 정해져** 영향도가 높은 데이터셋이 먼저 처리됩니다.

플랫폼 네이티브 모니터링을 통해 팀은 더 일찍 문제를 감지하고, 가장 중요한 것에 집중하며, 엔터프라이즈 규모에서 더 빠르게 문제를 해결할 수 있습니다.

{% hint style="info" %}
**고객 사례: Alinta Energy**

"우리의 목표는 항상 데이터 자체가 문제가 있을 때 우리에게 알려주는 것이었습니다. Databricks의 Data Quality Monitoring은 AI 기반 접근 방식을 통해 마침내 그것을 실현했습니다. UI에 완벽하게 통합되어 설정 없이 모든 테이블을 모니터링합니다. 설정이 부족한 것이 다른 제품들의 항상 한계였는데, 이제 사용자가 문제를 보고하는 대신 데이터 자체가 먼저 문제를 알려줘 플랫폼의 품질, 신뢰도 및 무결성을 향상시킵니다."

— Jake Roussis, Alinta Energy Lead Data Engineer
{% endhint %}

---

## Data Quality Monitoring의 작동 방식

데이터 품질 모니터링은 두 가지 상호 보완적인 방법을 통해 실행 가능한 인사이트를 제공합니다.

![데이터 품질 모니터링 아키텍처](https://www.databricks.com/sites/default/files/inline-images/image4_55.png?v=1770234757)

### 이상 감지 (Anomaly Detection)

스키마 수준에서 활성화되는 이상 감지(Anomaly Detection)는 수동 설정 없이 모든 중요한 테이블을 모니터링합니다. AI 에이전트는 역사적 패턴과 계절적 행동을 학습하여 예상치 못한 변화를 식별합니다.

- **학습된 행동, 정적 규칙이 아님:** 에이전트가 정상적인 변동에 적응하고 신선도(freshness)와 완전성(completeness) 같은 주요 품질 신호를 모니터링합니다. Null 비율, 고유성(uniqueness), 유효성(validity) 등 추가 검사에 대한 지원이 다음으로 제공될 예정입니다.
- **규모를 위한 지능형 스캐닝:** 스키마 내 모든 테이블이 한 번 스캔된 후, 테이블 중요도와 업데이트 빈도에 따라 재방문됩니다. Unity Catalog 리니지(lineage)와 인증(certification)이 어떤 테이블이 가장 중요한지를 결정합니다. 자주 사용되는 테이블은 더 자주 스캔되고, 정적이거나 더 이상 사용되지 않는 테이블은 자동으로 건너뜁니다.
- **가시성과 보고를 위한 시스템 테이블:** 테이블 상태, 학습된 임계값, 관찰된 패턴이 시스템 테이블에 기록됩니다. 팀은 이 데이터를 알림(alerting), 보고(reporting), 심층 분석에 활용합니다.

### 데이터 프로파일링 (Data Profiling)

테이블 수준에서 활성화되는 데이터 프로파일링(Data Profiling)은 요약 통계를 수집하고 시간에 따른 변화를 추적합니다. 이 메트릭은 역사적 컨텍스트를 제공하며 이상 감지에 제공되어 문제를 쉽게 포착할 수 있습니다.

아래 이미지는 Unity Catalog 내 데이터 프로파일링과 이상 감지 화면을 보여줍니다. 테이블 건강 상태, 감지된 이상 징후, 그리고 업스트림 파이프라인 연결 정보를 한눈에 확인할 수 있습니다.

![데이터 프로파일링 및 이상 감지 UI 화면](https://www.databricks.com/sites/default/files/inline-images/image2_72.png?v=1770222081)

{% hint style="info" %}
**고객 사례: OnePay**

"OnePay에서 우리의 미션은 사람들이 돈을 저축하고, 지출하고, 빌리고, 키울 수 있도록 지원하여 재정적 발전을 이루도록 돕는 것입니다. 모든 데이터셋에 걸친 높은 품질의 데이터는 그 미션을 실현하는 데 매우 중요합니다. Data Quality Monitoring을 통해 문제를 조기에 발견하고 신속하게 조치를 취할 수 있습니다. 분석, 보고, 견고한 ML 모델 개발에서 정확성을 보장할 수 있으며, 이 모든 것이 고객을 더 잘 서비스하는 데 기여합니다."

— Nameet Pai, OnePay Head of Platform & Data Engineering
{% endhint %}

---

## 지속적으로 성장하는 데이터 자산의 품질 보장

자동화된 품질 모니터링이 구축되면, 데이터 플랫폼 팀은 데이터의 전반적인 건강 상태를 지속적으로 파악하고 모든 문제를 적시에 해결할 수 있습니다.

아래 이미지는 Unity Catalog의 통합 데이터 건강 대시보드로, 모든 모니터링 테이블의 상태를 한눈에 볼 수 있습니다.

![Unity Catalog 통합 데이터 건강 대시보드](https://www.databricks.com/sites/default/files/inline-images/image4_52.png?v=1770222081)

**에이전틱(Agentic), 원클릭 모니터링:** 수동으로 규칙을 작성하거나 임계값을 설정하지 않고도 전체 스키마를 모니터링합니다. 데이터 품질 모니터링은 역사적 패턴과 계절적 행동(예: 주말 볼륨 감소, 세금 시즌 등)을 학습하여 모든 테이블에서 이상을 지능적으로 감지합니다.

**데이터 건강에 대한 전체적인 뷰:** 통합된 뷰에서 모든 테이블의 건강 상태를 쉽게 추적하고 문제가 해결되도록 보장합니다.

- **다운스트림 영향에 따른 문제 우선순위 결정:** 모든 테이블은 다운스트림 리니지(lineage)와 쿼리 볼륨을 기반으로 우선순위가 매겨집니다. 가장 중요한 테이블의 품질 문제가 먼저 플래그됩니다.
- **더 빠른 해결 시간:** Unity Catalog에서 데이터 품질 모니터링은 문제를 업스트림 Lakeflow Jobs 및 Spark Declarative Pipelines에 직접 연결합니다. 팀은 카탈로그에서 영향받은 잡으로 이동하여 특정 장애, 코드 변경 및 기타 근본 원인을 조사할 수 있습니다.

**건강 지표(Health Indicator):** 일관된 품질 신호가 업스트림 파이프라인에서 다운스트림 비즈니스 서피스(surface)까지 전파됩니다. 데이터 엔지니어링 팀은 문제를 가장 먼저 통보받고, 소비자는 데이터를 안전하게 사용할 수 있는지를 즉시 확인할 수 있습니다.

---

## 다음 단계 (Roadmap)

앞으로 몇 달 안에 로드맵에 있는 내용입니다.

| 기능 | 설명 |
|------|------|
| **더 많은 품질 규칙** | Null 비율(percent null), 고유성(uniqueness), 유효성(validity) 등 더 많은 검사 지원 |
| **자동화된 알림 및 근본 원인 분석** | 자동으로 알림을 받고 잡 및 파이프라인에 직접 내장된 지능형 근본 원인 포인터로 문제를 신속하게 해결 |
| **플랫폼 전반의 건강 지표** | Unity Catalog, Lakeflow Observability, Lineage, Notebooks, Genie 등 전반에 걸친 일관된 건강 신호 확인 |
| **불량 데이터 필터링 및 격리** | 불량 데이터를 사전에 식별하고 소비자에게 도달하기 전에 차단 |

이 로드맵은 현재 공개된 시점 기준으로, 향후 출시 일정이나 기능은 변경될 수 있습니다.

---

## 시작하기: Public Preview

지능형 모니터링을 대규모로 경험하고 신뢰할 수 있는 셀프서비스(self-serve) 데이터 플랫폼을 구축하세요. 오늘 바로 Public Preview를 사용해 보세요.

1. Unity Catalog의 **Schema Details** 탭에서 Data Quality Monitoring을 활성화합니다.
2. 제품 내에서 모든 모니터링 테이블의 전체적인 뷰를 확인합니다.
3. 제공된 템플릿으로 알림(alert)을 설정합니다.

{% hint style="info" %}
**관련 리소스**

- [Data Quality Monitoring 제품 페이지](https://www.databricks.com/product/machine-learning/lakehouse-monitoring)
- [AWS 문서: 데이터 품질 모니터링](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring)
- [Azure Databricks 문서: 데이터 품질 모니터링](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/data-quality-monitoring/)
{% endhint %}
