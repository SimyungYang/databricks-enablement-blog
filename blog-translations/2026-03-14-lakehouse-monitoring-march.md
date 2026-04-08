---
title: "Lakehouse Monitoring GA: 지능형 데이터 품질 프로파일링, 진단 및 적용"
date: 2024-08-01
authors: Jacqueline Li, Kasey Uhlenhuth, Paul Lappas, Danny Chiao
tags: [lakehouse-monitoring, data-quality, unity-catalog, mlops]
---

> **원문**: [Lakehouse Monitoring GA: Profiling, Diagnosing, and Enforcing Data Quality with Intelligence](https://www.databricks.com/blog/lakehouse-monitoring-ga-profiling-diagnosing-and-enforcing-data-quality-intelligence)

{% hint style="info" %}
이 블로그 포스트는 2024년 Data and AI Summit에서 발표된 Databricks Data Quality Monitoring (Lakehouse Monitoring) GA 출시를 다룹니다. 요청하신 URL(databricks-lakehouse-monitoring-update-march-2026)은 현재 존재하지 않으며, 가장 관련성 높은 공식 블로그 포스트를 번역하였습니다.
{% endhint %}

Data and AI Summit에서 우리는 **Databricks Data Quality Monitoring** 의 정식 출시(General Availability)를 발표했습니다. 데이터와 AI를 모니터링하는 통합적인 접근 방식을 통해, **Databricks Data Intelligence Platform** 내에서 품질을 손쉽게 프로파일링하고, 진단하고, 적용할 수 있습니다. **Unity Catalog** 위에 직접 구축된 Lakehouse Monitoring([AWS](https://docs.databricks.com/aws/en/lakehouse-monitoring) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-monitoring))은 추가적인 도구나 복잡성 없이 사용할 수 있습니다. 다운스트림 프로세스가 영향을 받기 전에 품질 문제를 발견함으로써, 조직은 데이터에 대한 접근을 민주화하고 신뢰를 회복할 수 있습니다.

## 데이터 및 모델 품질이 중요한 이유

오늘날 데이터 중심의 세계에서 고품질 데이터와 모델은 신뢰를 구축하고, 자율성을 창출하며, 비즈니스 성공을 이끄는 데 필수적입니다. 하지만 **품질 문제는 너무 늦을 때까지 눈에 띄지 않는 경우가 많습니다.**

이런 상황이 익숙하게 들리지 않으신가요? 파이프라인이 순조롭게 실행되고 있는 것처럼 보이다가, 데이터 분석가가 다운스트림 데이터가 손상되었다고 문제를 제기하는 상황 말입니다. 혹은 머신 러닝의 경우, 프로덕션에서 성능 문제가 명백하게 드러날 때까지 모델을 재학습해야 한다는 사실을 모르는 경우도 있습니다. 그러면 팀은 몇 주에 걸친 디버깅과 변경 사항 롤백이라는 과제에 직면하게 됩니다! 이러한 운영 오버헤드는 핵심 비즈니스 요구사항 전달을 늦출 뿐 아니라, 중요한 의사결정이 잘못된 데이터를 기반으로 내려졌을 수 있다는 우려를 불러일으킵니다. 이러한 문제를 예방하려면 조직에 품질 모니터링 솔루션이 필요합니다.

Lakehouse Monitoring을 사용하면 데이터와 AI 전반에 걸쳐 쉽게 시작하고 품질을 확장할 수 있습니다. Lakehouse Monitoring은 Unity Catalog 위에 구축되어 있어, 서로 다른 도구를 통합하는 번거로움 없이 거버넌스와 함께 품질을 추적할 수 있습니다. Databricks Data Intelligence Platform에서 품질을 직접 관리함으로써 조직이 달성할 수 있는 것들을 살펴보겠습니다.

Lakehouse Monitoring이 어떻게 데이터와 AI의 신뢰성을 향상시키면서 신뢰, 자율성, 비즈니스 가치를 구축하는지 알아보세요.

## 자동화된 프로파일링으로 인사이트 확보

Lakehouse Monitoring은 Unity Catalog의 모든 Delta Table([AWS](https://docs.databricks.com/aws/en/delta/index.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/delta/))에 대해 기본으로 자동화된 프로파일링을 제공합니다. 계정 내에 두 개의 메트릭 테이블([AWS](https://docs.databricks.com/aws/en/lakehouse-monitoring/monitor-output.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-monitoring/monitor-output))이 생성됩니다. 하나는 프로파일 메트릭용이고, 다른 하나는 드리프트 메트릭용입니다. 모델 입력과 출력을 나타내는 Inference Table([AWS](https://docs.databricks.com/aws/en/mlflow/inference-tables.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/mlflow/inference-tables))의 경우, 모델 성능 및 드리프트 메트릭도 함께 제공됩니다. 테이블 중심 솔루션으로서 Lakehouse Monitoring은 전체 데이터 및 AI 자산의 품질을 간단하고 확장 가능하게 모니터링할 수 있도록 합니다.

계산된 메트릭을 활용하여 Lakehouse Monitoring은 시간에 따른 트렌드와 이상 징후를 플롯하는 대시보드를 자동으로 생성합니다. count(레코드 수), percent nulls(null 비율), numerical distribution change(수치 분포 변화), categorical distribution change(범주 분포 변화) 등 주요 메트릭을 시간 흐름에 따라 시각화함으로써, Lakehouse Monitoring은 인사이트를 제공하고 문제가 있는 컬럼을 식별합니다. ML 모델을 모니터링하는 경우에는 정확도(accuracy), F1 점수, 정밀도(precision), 재현율(recall) 같은 메트릭을 추적하여 모델 재학습 시점을 파악할 수 있습니다. Lakehouse Monitoring을 사용하면 **번거로움 없이 품질 문제가 드러나며, 데이터와 모델이 지속적으로 신뢰할 수 있고 효과적인 상태를 유지할 수 있습니다.**

> "Lakehouse Monitoring은 판도를 바꾸는 솔루션입니다. 플랫폼 내에서 직접 데이터 품질 문제를 해결하는 데 도움을 줍니다... 시스템의 심장 박동과 같습니다. 데이터 사이언티스트들은 마침내 복잡한 과정 없이 데이터 품질을 이해할 수 있게 되어 기뻐하고 있습니다." — Yannis Katsanos, Ecolab 데이터 사이언스, 운영 및 혁신 이사

Lakehouse Monitoring은 비즈니스 요구사항에 맞게 완전히 커스터마이징할 수 있습니다. 사용 사례에 맞게 추가로 조정하는 방법은 다음과 같습니다:

- **Custom metrics(커스텀 메트릭)** ([AWS](https://docs.databricks.com/aws/en/lakehouse-monitoring/custom-metrics.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-monitoring/custom-metrics)): 기본 제공 메트릭 외에도 SQL 표현식으로 커스텀 메트릭을 작성할 수 있으며, 모니터 갱신 시 함께 계산됩니다. 모든 메트릭은 Delta 테이블에 저장되므로, 더 깊은 분석을 위해 계정 내 다른 테이블과 쉽게 쿼리하고 조인할 수 있습니다.
- **Slicing Expressions(슬라이싱 표현식)** ([AWS](https://docs.databricks.com/aws/en/lakehouse-monitoring/create-monitor-api.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-monitoring/create-monitor-api)): 테이블 전체뿐 아니라 테이블의 하위 집합을 모니터링하기 위한 슬라이싱 표현식을 설정할 수 있습니다. 특정 범주별로 그룹화된 메트릭을 보려면 임의의 컬럼으로 슬라이싱할 수 있습니다. 예를 들어 제품 라인별 매출, 민족이나 성별로 슬라이싱된 공정성 및 편향 메트릭 등이 있습니다.
- **Edit the Dashboard(대시보드 편집)** ([AWS](https://docs.databricks.com/aws/en/lakehouse-monitoring/monitor-dashboard.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-monitoring/monitor-dashboard)): 자동 생성된 대시보드는 Lakeview Dashboards([AWS](https://docs.databricks.com/aws/en/dashboards/) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/dashboards/))로 구축되어 있으므로, 커스텀 시각화 및 워크스페이스, 팀, 이해관계자 간 협업을 포함한 모든 Lakeview 기능을 활용할 수 있습니다.

다음으로, Lakehouse Monitoring은 사후 대응 프로세스에서 사전 예방적 알림으로 전환하여 데이터와 모델 품질을 한층 더 보장합니다. 새로운 Expectations 기능을 통해 품질 문제가 발생하는 즉시 알림을 받을 수 있습니다.

## Expectations로 품질 문제 사전 감지

Databricks는 품질을 데이터 실행에 더 가까이 가져와, 파이프라인 내에서 직접 문제를 감지하고, 예방하고, 해결할 수 있도록 합니다.

현재 Materialized View와 Streaming Table에 데이터 품질 Expectations([AWS](https://docs.databricks.com/aws/en/delta-live-tables/expectations.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/delta-live-tables/expectations))을 설정하여 `null` 레코드 삭제와 같은 행(row) 수준 제약조건을 적용할 수 있습니다. Expectations는 문제가 다운스트림 소비자에게 영향을 미치기 전에 미리 드러내어 조치를 취할 수 있게 해줍니다. 우리는 Databricks 전반에서 Expectations를 통합할 계획으로, Delta Table([AWS](https://docs.databricks.com/aws/en/delta/index.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/delta/)), Streaming Table([AWS](https://docs.databricks.com/aws/en/dlt/index.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/dlt/)), Materialized View([AWS](https://docs.databricks.com/aws/en/dlt/index.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/dlt/))를 포함한 Unity Catalog의 모든 테이블에 품질 규칙을 설정할 수 있게 됩니다. 이를 통해 중복 데이터, 높은 null 비율, 데이터의 분포 변화 같은 일반적인 문제를 예방하고, 모델 재학습 시점을 알 수 있게 됩니다.

Delta 테이블로 Expectations를 확장하기 위해 향후 몇 달 안에 다음과 같은 기능을 추가할 예정입니다:

*현재 Private Preview*

- **Aggregate Expectations(집계 Expectations)**: 기본 키(primary key), 외래 키(foreign key), `percent_null` 또는 `count`와 같은 집계 제약조건에 대한 Expectations를 정의합니다.
- **Notifications(알림)**: 품질 위반 시 알림을 받거나 작업(job)을 실패 처리하여 품질 문제를 사전에 해결합니다.
- **Observability(관찰 가능성)**: 데이터가 품질 Expectations를 충족하는지 여부를 신호하는 녹색/빨간색 건강 지표를 Unity Catalog에 통합합니다. 이를 통해 누구든 스키마 페이지를 방문하여 데이터 품질을 쉽게 평가할 수 있습니다. 어떤 테이블에 주의가 필요한지 빠르게 파악하여 이해관계자가 데이터를 안전하게 사용할 수 있는지 판단할 수 있습니다.
- **Intelligent forecasting(지능형 예측)**: 노이즈가 많은 알림을 최소화하고 불확실성을 줄이기 위해 Expectations에 대한 권장 임계값을 제공합니다.

## Lakehouse Monitoring 시작하기

Lakehouse Monitoring을 시작하려면 Unity Catalog의 원하는 테이블 **Quality** 탭으로 이동하여 "Get Started"를 클릭하기만 하면 됩니다. 선택할 수 있는 프로파일 유형([AWS](https://docs.databricks.com/aws/en/lakehouse-monitoring/create-monitor-api.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-monitoring/create-monitor-api))은 3가지입니다:

- **Time series(시계열)**: 품질 메트릭이 시간 창(time window)별로 집계되어 일별, 시간별, 주별 등으로 그룹화된 메트릭을 얻을 수 있습니다.
- **Snapshot(스냅샷)**: 품질 메트릭이 전체 테이블에 대해 계산됩니다. 이는 메트릭이 갱신될 때마다 전체 테이블에 대해 재계산됨을 의미합니다.
- **Inference(추론)**: 데이터 품질 메트릭 외에 모델 성능 및 드리프트 메트릭이 함께 계산됩니다. 이러한 메트릭을 시간 경과에 따라 비교하거나, 선택적으로 기준선(baseline) 또는 정답 레이블(ground-truth labels)과 비교할 수 있습니다.

{% hint style="info" %}
**모범 사례 팁**: 대규모 모니터링을 위해 테이블에 Change Data Feed (CDF)([AWS](https://docs.databricks.com/aws/en/delta/delta-change-data-feed.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/delta/delta-change-data-feed))를 활성화할 것을 권장합니다. 이를 통해 증분 처리(incremental processing)가 가능해져, 매번 갱신 시 전체 테이블을 재처리하는 대신 테이블에 새로 추가된 데이터만 처리합니다. 결과적으로 실행이 더 효율적이고, 여러 테이블에 걸쳐 모니터링을 확장할 때 비용을 절감할 수 있습니다. 이 기능은 Snapshot이 매번 전체 테이블 스캔을 필요로 하기 때문에 Time series 또는 Inference 프로파일에서만 사용 가능합니다.
{% endhint %}

Lakehouse Monitoring에 대해 더 자세히 알아보거나 직접 사용해 보려면 아래 제품 링크를 확인하세요:

- [DAIS 2024 Deep Dive and Demo](https://www.youtube.com/watch?v=dummy) 보기
- 제품 튜토리얼을 위한 [Lakehouse Monitoring DBdemo](https://github.com/databrickslabs/dbdemos) 계정에 로드하기
- 제품 문서 읽기 ([AWS](https://docs.databricks.com/aws/en/lakehouse-monitoring) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-monitoring))
- Expectations Preview [여기에서](https://docs.databricks.com/aws/en/lakehouse-monitoring) 신청하기

---

데이터 품질을 모니터링하고, 적용하고, 민주화함으로써 우리는 팀이 데이터에 대한 신뢰를 구축하고 자율성을 창출할 수 있도록 지원하고 있습니다. 조직에도 동일한 신뢰성을 가져오고, 오늘 바로 **Databricks Data Quality Monitoring** ([AWS](https://docs.databricks.com/aws/en/lakehouse-monitoring) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-monitoring))을 시작해 보세요.
