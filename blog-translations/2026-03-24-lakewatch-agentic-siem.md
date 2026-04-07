---
original_title: "Databricks Announces Lakewatch: New Open, Agentic SIEM"
authors: "Databricks"
date: "2026-03-24"
category: "Product"
original_url: "https://www.databricks.com/blog/databricks-announces-lakewatch-new-open-agentic-siem"
translated_date: "2026-04-07"
---

> **원문**: [Databricks Announces Lakewatch: New Open, Agentic SIEM](https://www.databricks.com/blog/databricks-announces-lakewatch-new-open-agentic-siem)

# Databricks, 새로운 오픈형 에이전틱 SIEM 'Lakewatch' 발표

**Databricks**는 오늘 **Lakewatch**를 발표했습니다. Lakewatch는 점점 더 정교해지는 에이전트 공격자(Agent Attacker)로부터 조직을 방어하도록 설계된 새로운 오픈형 에이전틱 SIEM(Security Information and Event Management)입니다. Lakewatch는 보안, IT, 비즈니스 데이터를 단일의 거버넌스된 환경으로 통합하여 AI 기반 탐지 및 대응을 가능하게 합니다. 오픈 포맷과 오픈 에코시스템을 통해 Lakewatch는 고객이 전례 없는 규모의 멀티모달 데이터를 수집·보존·분석하면서도 비용을 절감하고 벤더 종속성(Vendor Lock-in)을 제거할 수 있도록 지원합니다. 보안 팀은 기업 전반에 걸친 완전한 가시성을 확보하고, 방어용 보안 에이전트를 배포하여 대규모 위협 탐지와 대응을 자동화할 수 있습니다. Lakewatch는 현재 **Private Preview**로 제공됩니다.

## 머신 속도로 방어하기

AI 위협은 인간 주도 방어가 따라가기 어려운 속도와 복잡성으로 진화하고 있습니다. 공격자는 이제 에이전트를 배포하여 시스템을 지속적으로 스캔하고, 취약점을 발견하며, 머신 속도로 조율된 공격을 실행할 수 있습니다. 반면 방어자들은 불완전한 데이터, 수동 워크플로우, 사일로화된 아키텍처로 인해 여전히 제약을 받고 있습니다. 높은 수집 비용으로 인해 방어자들은 데이터의 최대 75%를 폐기해야 하는 상황입니다. 이로 인해 위험한 비대칭이 발생합니다. 공격자는 AI 에이전트를 활용해 어디서든 공격을 감행하는 반면, 방어자들은 자신들 데이터의 극히 일부만 볼 수 있고 팀이 얼마나 빠르게 반응할 수 있느냐에 의해 제한됩니다.

Lakewatch는 이 간극을 해소합니다. 조직이 모든 데이터를 오픈 포맷으로 통합하여 데이터를 이동하거나 복제하지 않고도 수년간의 데이터를 비용 효율적으로 분석할 수 있게 합니다. 여기에는 소셜 엔지니어링, 내부자 위협, 이상 탐지를 식별하기 위한 영상·음성과 같은 멀티모달 데이터도 포함됩니다. Lakewatch를 통해 AI 에이전트 군집이 탐지, 트리아지(Triage), 위협 헌팅을 자동화함으로써 머신 속도의 공격자에 머신 속도의 방어로 맞설 수 있습니다.

> "보안 팀은 더 이상 AI 기반 공격을 수동 워크플로우로 따라잡을 수 없습니다. Lakewatch를 통해 우리는 기업에게 침체된 SIEM 도구를 대체할 수 있는 새로운 오픈 데이터 아키텍처와 에이전틱 역량을 제공합니다. 방어자들은 오늘날의 에이전트 공격자보다 더 뛰어난 가시성과 속도를 가져야 합니다."
>
> — **Ali Ghodsi**, Databricks 공동 창업자 겸 CEO

## 엔터프라이즈 속도와 규모를 위한 오픈 에이전틱 SIEM

Lakewatch는 오픈 보안 레이크하우스(Open Security Lakehouse)의 규모 위에서 에이전틱 보안을 제공하도록 설계되었습니다. 주요 기능은 다음과 같습니다:

### 에이전틱 트리아지 및 조사 (Agentic Triage and Investigation)

**Agent Bricks**로 커스텀 보안 에이전트를 구축, 최적화, 배포하여 복잡한 워크플로우를 엔드투엔드로 처리합니다. 에이전트는 수백 가지 포맷에 걸쳐 텔레메트리를 파싱하고 보강하여 **MTTD/R(Mean Time to Detect & Respond, 평균 탐지·대응 시간)**을 단축하는 동시에, 데이터가 이미 존재하는 안전하고 거버넌스된 환경 안에서 동작합니다.

### 자동화된 보안 인텔리전스 (Automated Security Intelligence)

**Genie**와 통합된 Lakewatch는 트리아지를 자동화하고, 다단계 접근법을 계획하며, 기업의 알림 피로도(Alert Fatigue)를 줄여 분석가가 고영향도 위협에 더 많은 시간을 집중할 수 있도록 지원합니다.

### 오픈 에코시스템 (Open Ecosystem)

모든 정형·비정형 보안 데이터를 어떤 도구와도 통합되는 단일 오픈, 클라우드 애그노스틱(Cloud-Agnostic) 플랫폼으로 통합하여 소셜 엔지니어링, 내부자 위협, 이상 탐지를 식별합니다. Databricks의 새로운 **오픈 보안 레이크하우스 에코시스템(Open Security Lakehouse Ecosystem)**은 빠르게 성장 중인 선도 보안 벤더 및 딜리버리 파트너 그룹으로, Anvilogic, Arctic Wolf, Cribl, Obsidian, Okta, Palo Alto Networks, 1Password, Panther, Proofpoint, Rearc, Slack, TrendAI, Wiz(현재 Google Cloud의 일부), Zscaler 등이 포함되어 있습니다.

### Detection-as-Code

탐지 규칙을 코드로 관리하고 자동화된 테스트 및 배포를 통해 방어가 항상 버전 관리되고 검증된 상태를 유지합니다.

### 거버넌스 및 대규모 컴플라이언스 (Governance and Compliance at Scale)

**Unity Catalog**를 통해 컴플라이언스와 일관된 정책 집행을 가능하게 합니다. 비용 효율적인 장기 보존 기능을 기본으로 제공하여, 글로벌 기업이 NIS2, DORA 등 엄격한 신규 규정을 충족할 수 있도록 지원합니다.

---

엔터프라이즈 조직들은 Lakewatch를 활용하여 데이터를 통합하고 AI로 위협을 더 빠르게 탐지하고 있습니다. Lakewatch 고객에는 Adobe, Dropbox와 같은 업계 선도 기업이 포함되어 있습니다.

> "보안 데이터의 양이 증가함에 따라, 조직은 그 정보를 빠르게 그리고 대규모로 분석하고 조치를 취할 새로운 방법이 필요합니다. Databricks는 데이터 중심에서 AI 중심의 보안 운영 방식으로 전환하는 데 필요한 기반을 제공하며, Lakewatch는 보안 인텔리전스를 데이터가 이미 존재하는 곳에 더 가깝게 가져오는 중요한 발걸음입니다."
>
> — **Karthik Venkatesan**, Adobe 보안 엔지니어링 리드

## Anthropic과의 파트너십 심화

두 회사의 기존 전략적 파트너십의 성공을 바탕으로, Databricks와 Anthropic은 에이전틱 보안 운영을 제공하기 위한 협력을 심화하고 있습니다. Anthropic의 Claude 모델이 Lakewatch를 구동하는 데 도움을 주며, Claude의 고급 추론 능력을 활용하여 보안, IT, 비즈니스 데이터 전반의 신호를 상관 분석함으로써 위협을 더 빠르게 식별합니다. 또한 Anthropic은 Databricks를 자체 보안 레이크하우스로 활용하여 보안 및 비즈니스 데이터 전반에 걸친 완전한 가시성을 확보하고 위협을 조기에 탐지합니다.

## Antimatter 및 SiftD.ai 인수로 보안 리더십 확장

오픈 에이전틱 SIEM 접근 방식을 가속화하기 위해 Databricks는 **Antimatter**와 **SiftD.ai** 인수를 발표합니다.

**Antimatter**는 UC Berkeley 보안 연구자들이 창업한 회사로, AI 에이전트를 위한 증명 가능한 안전 인증(Authentication) 및 권한 부여(Authorization)의 토대를 마련했습니다.

**SiftD.ai**는 Splunk의 검색 처리 언어(SPL, Search Processing Language)를 만든 창업자와 Splunk 검색 스택의 수석 아키텍트들이 설립한 회사로, 대규모 탐지 엔지니어링과 현대적인 위협 분석에 깊은 전문성을 가져옵니다.

## 제공 현황

Lakewatch는 현재 **Private Preview**로 제공됩니다.

---

{% hint style="info" %}
**Lakewatch에 대해 더 알아보기**

Lakewatch 제품 페이지: [databricks.com/product/lakewatch](https://www.databricks.com/product/lakewatch)
{% endhint %}

---

## 관련 주요 개념 해설

| 용어 | 설명 |
|------|------|
| **SIEM (Security Information and Event Management)** | 보안 정보 및 이벤트 관리. 다양한 소스의 로그와 이벤트를 수집·분석하여 위협을 탐지하는 플랫폼 |
| **에이전틱 AI (Agentic AI)** | 주어진 목표를 달성하기 위해 계획을 수립하고 도구를 호출하며 자율적으로 행동하는 AI |
| **OCSF (Open Cybersecurity Schema Framework)** | 다양한 보안 도구에서 생성되는 데이터를 표준화된 스키마로 정규화하는 오픈소스 프레임워크 |
| **Detection-as-Code** | 탐지 규칙을 소프트웨어 코드처럼 버전 관리·테스트·배포하는 보안 엔지니어링 방법론 |
| **Agent Bricks** | Databricks의 에이전트 구축·배포 플랫폼으로, 커스텀 보안 에이전트를 생성하고 운영할 수 있음 |
| **Genie** | Databricks의 AI 기반 데이터 분석 에이전트로, 자연어 질의를 SQL로 변환하고 자동화된 인사이트를 제공 |
| **Unity Catalog** | Databricks의 통합 거버넌스 솔루션으로, 데이터·모델·AI 자산에 대한 세분화된 접근 제어와 감사를 제공 |
| **Lakeflow Connect** | 다양한 소스에서 보안 데이터를 수집하고 OCSF 스키마로 정규화하는 Databricks의 데이터 수집 파이프라인 |
| **MTTD/R (Mean Time to Detect/Respond)** | 위협을 탐지하기까지 평균 소요 시간(MTTD)과 탐지된 위협에 대응하기까지 평균 소요 시간(MTTR) |
| **TCO (Total Cost of Ownership)** | 총 소유 비용. 하드웨어, 소프트웨어, 운영, 인력 비용을 모두 포함한 전체 비용 |
| **Antimatter** | UC Berkeley 보안 연구자들이 창업한 회사로, AI 에이전트를 위한 인증·권한 부여 기술을 보유. Databricks에 인수됨 |
| **SiftD.ai** | Splunk SPL 개발자와 아키텍트들이 설립한 탐지 엔지니어링 전문 회사. Databricks에 인수됨 |

---

## Databricks 소개

Databricks는 데이터 및 AI 전문 기업입니다. adidas, AT&T, Bayer, Block, Mastercard, Rivian, Unilever을 비롯한 Fortune 500 기업의 60% 이상을 포함하여 전 세계 20,000개 이상의 조직이 데이터 및 AI 앱, 분석, 에이전트를 구축하고 확장하기 위해 Databricks를 활용하고 있습니다. 샌프란시스코에 본사를 두고 전 세계 30개 이상의 오피스를 운영하는 Databricks는 Lakebase, Genie, Agent Bricks, Lakeflow, Lakehouse, Unity Catalog를 포함한 통합 플랫폼을 제공합니다.
