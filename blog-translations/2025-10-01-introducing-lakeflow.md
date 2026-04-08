---
title: "Databricks Lakeflow 소개: 데이터 엔지니어링을 위한 통합 지능형 솔루션"
date: 2024-06-12
author: "Michael Armbrust, Bilal Aslam"
original_url: "https://www.databricks.com/blog/introducing-databricks-lakeflow"
tags: [lakeflow, data-engineering, etl, ingestion, pipelines, jobs, unity-catalog, streaming]
---

> **원문**: [Introducing Databricks Lakeflow: A unified, intelligent solution for data engineering](https://www.databricks.com/blog/introducing-databricks-lakeflow)

{% hint style="info" %}
요청하신 URL(`introducing-lakeflow-databricks-native-etl`)은 현재 404 오류를 반환합니다. 검색 결과, 해당 주제를 다루는 공식 블로그 포스트의 실제 URL은 위 원문 링크이며, 본 번역은 2024년 6월 12일 Data + AI Summit에서 공개된 해당 공식 발표 포스트를 기반으로 합니다.
{% endhint %}

# Databricks Lakeflow 소개: 데이터 엔지니어링을 위한 통합 지능형 솔루션

**게시일**: 2024년 6월 12일 | **저자**: Michael Armbrust, Bilal Aslam

---

오늘 우리는 **Databricks Lakeflow** 를 발표합니다. Lakeflow는 데이터 수집 (Ingestion) 에서 변환 (Transformation) 과 오케스트레이션 (Orchestration) 에 이르기까지 데이터 엔지니어링의 모든 측면을 단순화하고 통합하는 새로운 솔루션입니다.

Lakeflow를 통해 데이터 팀은 MySQL, Postgres, Oracle 같은 데이터베이스와 Salesforce, Dynamics, SharePoint, Workday, NetSuite, Google Analytics 같은 엔터프라이즈 애플리케이션으로부터 데이터를 대규모로 손쉽게 수집할 수 있습니다. 또한 Databricks는 Apache Spark™를 위한 **Real Time Mode** 를 도입합니다. 이 기능은 마이크로배치 방식보다 훨씬 낮은 지연 시간으로 스트림 처리를 가능하게 합니다.

Lakeflow는 내장된 CI/CD 지원과 트리거링, 분기 (Branching), 조건부 실행을 지원하는 고급 워크플로우를 통해 프로덕션 환경에서의 파이프라인 배포, 운영, 모니터링을 자동화합니다. 데이터 품질 검사 및 상태 모니터링 기능이 내장되어 있으며 PagerDuty 같은 알림 시스템과도 통합됩니다. Lakeflow는 프로덕션 수준의 데이터 파이프라인을 구축하고 운영하는 과정을 단순하고 효율적으로 만들면서도 가장 복잡한 데이터 엔지니어링 요구사항까지 처리할 수 있어, 바쁜 데이터 팀도 신뢰할 수 있는 데이터와 AI에 대한 증가하는 수요를 충족할 수 있게 합니다.

---

## 신뢰할 수 있는 데이터 파이프라인 구축과 운영의 어려움

데이터 엔지니어링은 기업 내 데이터와 AI 민주화에 필수적이지만, 여전히 복잡하고 어려운 분야로 남아 있습니다. 데이터 팀은 사일로화되어 있고 독점적인 데이터베이스와 엔터프라이즈 애플리케이션 등 다양한 시스템에서 데이터를 수집해야 하며, 이를 위해 복잡하고 취약한 커넥터를 직접 개발해야 하는 경우가 많습니다. 데이터 준비 단계에서는 복잡한 로직을 유지 관리해야 하고, 장애와 지연 시간 급증은 운영 중단과 고객 불만으로 이어집니다. 파이프라인 배포 및 데이터 품질 모니터링에는 별도의 분산된 도구가 필요해 프로세스가 더욱 복잡해집니다. 기존 솔루션들은 단편화되어 있고 불완전하여 낮은 데이터 품질, 신뢰성 문제, 높은 비용, 그리고 끊임없이 증가하는 작업 백로그를 초래하고 있습니다.

Lakeflow는 Databricks Data Intelligence Platform 위에 구축된 단일 통합 경험을 통해 데이터 엔지니어링의 모든 측면을 단순화함으로써 이러한 문제를 해결합니다. Unity Catalog와의 깊은 통합을 통해 엔드-투-엔드 (End-to-End) 거버넌스 (Governance) 를 제공하며, 서버리스 (Serverless) 컴퓨팅을 통해 효율적이고 확장 가능한 실행 환경을 제공합니다.

---

## Lakeflow의 핵심 기능

### Lakeflow Connect: 모든 데이터 소스에서 간편하고 확장 가능한 데이터 수집

**Lakeflow Connect** 는 MySQL, Postgres, SQL Server, Oracle 같은 데이터베이스와 Salesforce, Dynamics, SharePoint, Workday, NetSuite 같은 엔터프라이즈 애플리케이션을 위한 광범위한 네이티브 (Native) 고확장 커넥터 (Connector) 를 제공합니다. 이 커넥터들은 Unity Catalog와 완전히 통합되어 강력한 데이터 거버넌스를 지원합니다.

Lakeflow Connect는 Databricks가 2023년 11월에 인수한 **Arcion** 의 저지연 고효율 기술을 내재화하고 있습니다. **변경 데이터 캡처 (CDC, Change Data Capture)** 기술을 활용하여 레이크하우스 (Lakehouse) 로의 데이터 이전을 단순하고 신뢰할 수 있으며 운영 효율적으로 만듭니다. Lakeflow Connect는 크기, 형식, 위치에 관계없이 모든 데이터를 배치 및 실시간 분석에 활용할 수 있도록 지원합니다.

{% hint style="info" %}
**고객 사례 — Insulet:** 웨어러블 인슐린 관리 시스템인 Omnipod의 제조사 Insulet은 Lakeflow Connect의 Salesforce 수집 커넥터를 활용하여 고객 피드백 관련 데이터를 Databricks 기반 데이터 솔루션으로 수집합니다. 분산된 시스템을 중앙화된 확장 가능한 아키텍처로 대체함으로써, Insulet은 모든 팀이 실시간 데이터에 원활하게 접근하여 제조 워크플로우 모니터링, Omnipod 성능 최적화, 그리고 모든 AI 애플리케이션 지원을 가능하게 했습니다.
{% endhint %}

### Lakeflow Pipelines: 실시간 데이터 파이프라인의 단순화와 자동화

Databricks의 고확장성 **Delta Live Tables (DLT)** 기술을 기반으로 구축된 **Lakeflow Pipelines** 는 데이터 팀이 SQL 또는 Python으로 데이터 변환과 ETL (Extract, Transform, Load) 을 구현할 수 있게 합니다. 이제 고객은 코드 변경 없이 **Real Time Mode** 를 활성화하여 저지연 스트리밍을 구현할 수 있습니다.

Lakeflow는 수동 오케스트레이션의 필요성을 없애고 배치 (Batch) 와 스트림 (Stream) 처리를 통합합니다. 최적의 가격 대비 성능을 위한 증분 데이터 처리 (Incremental Processing) 를 제공하며, 가장 복잡한 스트리밍 및 배치 데이터 변환도 쉽게 구축하고 운영할 수 있게 합니다.

**Real Time Mode for Apache Spark** 는 이번 발표의 핵심 혁신 중 하나입니다. 기존 마이크로배치 방식 대비 수십 배 더 빠른 지연 시간으로 스트림 처리를 가능하게 합니다. 시간에 민감한 데이터셋을 지속적으로 저지연으로 전달해야 하는 워크로드에서 코드 변경 없이 이 모드를 활성화할 수 있습니다.

### Lakeflow Jobs: Data Intelligence Platform 전반의 워크플로우 오케스트레이션

**Lakeflow Jobs** 는 노트북 (Notebook) 과 SQL 쿼리 스케줄링부터 머신러닝 (ML) 학습 및 자동 대시보드 업데이트에 이르기까지 데이터 상태 및 전달을 아우르는 자동화된 오케스트레이션 (Orchestration) 을 제공합니다.

향상된 제어 흐름 기능과 완전한 가시성 (Observability) 을 통해 데이터 문제를 감지하고, 진단하고, 완화하여 파이프라인 신뢰성을 높입니다. Lakeflow Jobs는 단일 장소에서 데이터 파이프라인의 배포, 오케스트레이션, 모니터링을 자동화하여 데이터 팀이 데이터 전달 약속을 지킬 수 있게 합니다.

주요 기능으로는 다음이 포함됩니다.

- **CI/CD 지원**: 프로덕션 환경으로의 파이프라인 배포를 자동화하여 개발과 운영의 경계를 허뭅니다.
- **고급 제어 흐름**: 트리거링, 분기, 조건부 실행을 지원하는 정교한 워크플로우 구성이 가능합니다.
- **데이터 품질 내장**: 데이터 품질 검사가 파이프라인에 내장되어 있어 별도의 도구 없이 품질을 관리합니다.
- **알림 통합**: PagerDuty를 비롯한 알림 시스템과 통합되어 이상 징후 발생 시 즉시 대응이 가능합니다.

---

## AI 기반 지능이 모든 것에 녹아들다

AI 기반 인텔리전스 (AI-Powered Intelligence) 는 Lakeflow의 모든 측면을 아우르는 기반 역량입니다. **Databricks Assistant** 가 데이터 파이프라인의 탐색, 작성, 모니터링 전반을 지원합니다. 또한 Lakeflow는 Unity Catalog와 깊이 통합되어 계보 (Lineage) 추적과 데이터 품질 관리 기능을 제공합니다.

이를 통해 데이터 팀은 반복적인 수동 작업에서 벗어나 비즈니스 가치를 창출하는 고부가가치 작업에 집중할 수 있습니다.

---

## Databricks Data Intelligence Platform과의 네이티브 통합

Lakeflow는 Databricks Data Intelligence Platform에 완전히 통합된 네이티브 솔루션입니다. 이를 통해 다음과 같은 이점을 제공합니다.

- **서버리스 컴퓨팅 (Serverless Compute)**: 인프라 관리 부담 없이 효율적이고 확장 가능한 파이프라인 실행이 가능합니다.
- **Unity Catalog 통합**: 모든 파이프라인에 걸쳐 통합된 거버넌스와 데이터 계보 (Data Lineage) 를 제공합니다.
- **단일 플랫폼 경험**: 수집, 변환, 오케스트레이션을 하나의 일관된 경험으로 통합하여 도구 파편화 문제를 해결합니다.
- **Databricks Assistant**: AI 기반 어시스턴트가 파이프라인 탐색, 코드 작성, 문제 진단을 지원합니다.

---

## 왜 Lakeflow인가 — 기존 솔루션의 한계를 넘어서

기존 데이터 엔지니어링 스택은 수집, 변환, 오케스트레이션을 위한 별도의 도구들로 구성되어 있어 다음과 같은 문제를 야기했습니다.

아래 표는 기존 분산 접근 방식과 Lakeflow의 통합 접근 방식을 비교한 것입니다.

| 영역 | 기존 분산 접근 방식 | Lakeflow 통합 접근 방식 |
|---|---|---|
| 데이터 수집 | 독점 커넥터, 취약한 코드, 별도 도구 | 네이티브 CDC 커넥터, 클릭 기반 설정 |
| 스트림 처리 | 마이크로배치 지연 한계 | Real Time Mode for Apache Spark |
| 파이프라인 변환 | 수동 오케스트레이션, 코드 복잡도 | 선언형 SQL/Python, 자동 증분 처리 |
| 거버넌스 | 각 도구별 분리된 거버넌스 | Unity Catalog 기반 엔드-투-엔드 통합 |
| 운영 모니터링 | 별도 모니터링 도구, 수동 알림 | 내장 품질 검사, PagerDuty 통합 |
| 배포 자동화 | 수동 배포, 환경 불일치 | 내장 CI/CD 지원 |

이처럼 단편화된 스택은 낮은 데이터 품질, 신뢰성 문제, 높은 총소유비용 (TCO, Total Cost of Ownership) 과 끊임없이 증가하는 작업 백로그로 이어졌습니다. Lakeflow는 이 모든 것을 하나의 통합된 경험으로 해결합니다.

---

## 가용성 안내

Lakeflow는 **Lakeflow Connect** 를 시작으로 곧 프리뷰 (Preview) 를 시작할 예정입니다. 현재 웨이트리스트 (Waitlist) 에 등록하면 우선 접근 기회를 얻을 수 있습니다.

{% hint style="warning" %}
**프리뷰 참여 안내**: Lakeflow Connect 프리뷰에 참여하려면 Unity Catalog가 활성화되어 있고 서버리스 컴퓨팅이 지원되는 워크스페이스 (Workspace) 가 필요합니다. Lakeflow Connect 커넥터 파이프라인을 생성하기 전에 Unity Catalog가 활성화된 워크스페이스에서 서버리스 컴퓨팅을 활성화해야 합니다.
{% endhint %}

---

## 마무리

데이터 엔지니어링의 미래는 통합되고 지능적입니다. **Lakeflow** 는 Databricks Data Intelligence Platform의 힘을 바탕으로, 데이터 팀이 복잡성을 줄이고 신뢰할 수 있는 프로덕션 데이터 파이프라인을 더 빠르게 구축하고 운영할 수 있도록 합니다.

수집에서 변환, 오케스트레이션까지 — 하나의 통합된 플랫폼에서, 하나의 일관된 경험으로. 이것이 Databricks Lakeflow가 약속하는 미래입니다.

**Lakeflow Connect 프리뷰 웨이트리스트에 지금 등록하세요.**

---

## Databricks 소개

Databricks는 데이터와 AI 기업입니다. Block, Comcast, Condé Nast, Rivian, Shell을 포함한 전 세계 10,000개 이상의 조직과 Fortune 500 기업의 60% 이상이 Databricks Data Intelligence Platform을 통해 데이터를 장악하고 AI를 활용합니다. Databricks는 레이크하우스 (Lakehouse), Apache Spark™, Delta Lake, MLflow의 원조 창시자들이 설립했으며, 샌프란시스코에 본사를 두고 전 세계에 지사를 운영하고 있습니다.
