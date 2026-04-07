> **원문**: [Building a near real-time application with Zerobus Ingest and Lakebase](https://www.databricks.com/blog/building-near-real-time-application-zerobus-ingest-and-lakebase)

---

# Zerobus Ingest와 Lakebase로 준실시간 애플리케이션 구축하기

**원문 제목**: Building a near real-time application with Zerobus Ingest and Lakebase
**저자**: Grant Doyle, Benjamin Nwokeleme
**게시일**: 2026년 3월 6일
**원문 URL**: https://www.databricks.com/blog/building-near-real-time-application-zerobus-ingest-and-lakebase

{% hint style="info" %}
요청하신 URL(real-time-analytics-operational-data-without-etl)은 현재 404 상태입니다. 동일한 주제(ETL 없는 운영 데이터 실시간 분석)를 다루는 가장 관련성 높은 공식 Databricks 블로그 포스트를 번역했습니다.
{% endhint %}

---

**Databricks 데이터 인텔리전스 플랫폼과 결합하면, IoT, 클릭스트림, 애플리케이션 텔레메트리의 이벤트 데이터가 중요한 실시간 분석과 AI를 구동합니다.** 전통적으로 이 데이터를 수집하려면 데이터 소스와 레이크하우스 사이에 메시지 버스, Spark 작업 등 여러 단계의 데이터 홉(hop)이 필요했습니다. 이는 운영 오버헤드를 높이고, 데이터를 중복 저장하며, 전문 기술을 요구합니다. 레이크하우스가 유일한 데이터 목적지인 경우에는 특히 비효율적입니다.

일단 데이터가 레이크하우스에 적재되면, 다운스트림 분석 사용 사례를 위해 변환되고 정제됩니다. 그러나 팀은 종종 이 분석 데이터를 운영 사용 사례에도 활용해야 하며, 이러한 커스텀 애플리케이션을 구축하는 과정은 상당한 노력을 요구합니다. 전용 OLTP (Online Transaction Processing) 데이터베이스 인스턴스(네트워킹, 모니터링, 백업 등 포함)와 같은 필수 인프라 구성 요소를 프로비저닝하고 유지 관리해야 합니다. 게다가 분석 데이터를 데이터베이스로 역방향 전송하는 [Reverse ETL](https://www.databricks.com/blog/reverse-etl-lakebase-activate-your-lakehouse-data-operational-analytics) 프로세스도 관리해야 합니다. 이를 위해 레이크하우스에서 외부 운영 데이터베이스로 데이터를 푸시하는 추가 파이프라인을 구축해야 합니다. 이 파이프라인들은 개발자가 설정하고 유지해야 할 인프라를 더욱 복잡하게 만들며, 결국 핵심 목표인 비즈니스용 애플리케이션 구축에서 주의를 분산시킵니다.

그렇다면 Databricks는 레이크하우스로의 데이터 수집과 운영 워크로드를 지원하기 위한 골드(gold) 데이터 제공을 어떻게 단순화할까요?

**바로 Zerobus Ingest와 Lakebase가 그 답입니다.**

## Zerobus Ingest 소개

[Zerobus Ingest](https://www.databricks.com/product/data-engineering/lakeflow-connect/zerobus-ingest)는 [Lakeflow Connect](https://www.databricks.com/product/data-engineering/lakeflow-connect)의 일부로, 이벤트 데이터를 레이크하우스에 직접 푸시할 수 있는 간소화된 방법을 제공하는 API 집합입니다. 단일 싱크(single-sink) 메시지 버스 계층을 완전히 제거함으로써, Zerobus Ingest는 인프라를 줄이고, 운영을 단순화하며, 대규모 준실시간 수집을 실현합니다. 덕분에 데이터의 가치를 그 어느 때보다 쉽게 활용할 수 있습니다.

데이터를 생산하는 애플리케이션은 데이터를 쓸 대상 테이블을 지정하고, 메시지가 테이블 스키마에 올바르게 매핑되도록 확인한 후, Databricks로 데이터를 전송하는 스트림을 시작해야 합니다. Databricks 측에서는 API가 메시지와 테이블의 스키마를 검증하고, 데이터를 대상 테이블에 기록한 뒤, 데이터가 영속화(persist)되었다는 확인 응답을 클라이언트에 전송합니다.

### Zerobus Ingest의 주요 이점

- **간소화된 아키텍처:** 복잡한 워크플로우와 데이터 중복의 필요성을 제거합니다.
- **대규모 성능:** 준실시간 수집(최대 5초)을 지원하며, 수천 개의 클라이언트가 동일한 테이블에 동시 쓰기 가능(클라이언트당 최대 100MB/초 처리량)합니다.
- **데이터 인텔리전스 플랫폼과의 통합:** 사기 탐지를 위한 MLflow 같은 분석 및 AI 도구를 데이터에 직접 적용할 수 있도록 지원하여 가치 창출 시간을 단축합니다.

다음 표는 Zerobus Ingest의 핵심 성능 사양을 요약합니다. 이 수치들은 실시간에 가까운 데이터 처리가 실제로 가능함을 보여주며, 특히 수집 지연 시간과 처리량 면에서 기존 메시지 버스 방식 대비 명확한 이점을 제공합니다.

| Zerobus Ingest 기능 | 사양 |
|---|---|
| 수집 지연 시간 | 준실시간 (≤5초) |
| 클라이언트당 최대 처리량 | 최대 100MB/초 |
| 동시 클라이언트 수 | 테이블당 수천 개 |
| 연속 동기화 지연 (Delta → Lakebase) | 10–15초 |
| 실시간 ForeachWriter 지연 시간 | 200–300밀리초 |

이 사양은 준실시간 스트리밍 사용 사례에서 Zerobus Ingest가 기존 Kafka 기반 아키텍처를 대체할 수 있는 충분한 성능을 갖추고 있음을 보여줍니다.

## Lakebase 소개

[Lakebase](https://www.databricks.com/product/lakebase)는 Databricks 플랫폼에 내장된 완전 관리형, 서버리스, 확장 가능한 Postgres 데이터베이스입니다. 분석 및 AI 사용 사례를 구동하는 동일한 데이터 위에서 직접 실행되는 저지연 운영 및 트랜잭션 워크로드를 위해 설계되었습니다.

컴퓨팅과 스토리지의 완전한 분리는 빠른 프로비저닝과 탄력적 자동 스케일링을 실현합니다. Lakebase가 Databricks 플랫폼과 통합된다는 점은 기존 데이터베이스와의 주요 차별화 요소입니다. Lakebase는 복잡한 커스텀 데이터 파이프라인 없이도 레이크하우스 데이터를 실시간 애플리케이션과 AI 모두에서 직접 사용할 수 있게 합니다. 엔터프라이즈 애플리케이션과 에이전트형 워크로드를 구동하는 데 필요한 데이터베이스 생성, 쿼리 지연 시간, 동시성 요건을 충족하도록 구축되었습니다. 또한 개발자가 코드처럼 데이터베이스를 쉽게 버전 관리하고 브랜치할 수 있습니다.

### Lakebase의 주요 이점

- **자동 데이터 동기화:** 복잡한 외부 파이프라인 없이도 레이크하우스(분석 계층)에서 Lakebase로 스냅샷, 예약 또는 연속 방식으로 데이터를 쉽게 동기화할 수 있습니다.
- **Databricks 플랫폼과의 통합:** Lakebase는 Unity Catalog, Lakeflow Connect, Spark Declarative Pipelines, Databricks Apps 등과 통합됩니다.
- **통합 권한 및 거버넌스:** 운영 데이터와 분석 데이터에 대한 일관된 역할 및 권한 관리를 제공합니다. Postgres 프로토콜을 통해 네이티브 Postgres 권한도 여전히 유지할 수 있습니다.

이 두 도구를 함께 사용하면, 고객은 여러 시스템에서 데이터를 Delta 테이블에 직접 수집하고 대규모로 Reverse ETL 사용 사례를 구현할 수 있습니다. 이제 이러한 기술을 활용해 준실시간 애플리케이션을 구현하는 방법을 살펴보겠습니다!

## 준실시간 애플리케이션 구축 방법

실용적인 예시로, 음식 배달 회사 'Data Diners'의 관리 직원이 실시간으로 드라이버 활동과 주문 배달을 모니터링할 수 있는 애플리케이션을 구축해 보겠습니다. 현재 이 회사는 이러한 가시성이 부족하여 배달 중 발생하는 문제를 즉각적으로 해결하는 데 한계가 있습니다.

**왜 실시간 애플리케이션이 가치 있는가?**

- **운영 인식:** 관리자는 각 드라이버의 현재 위치와 배달 진행 상황을 즉시 파악할 수 있습니다. 늦은 주문이나 드라이버가 도움이 필요한 상황에서 사각지대가 줄어듭니다.
- **문제 완화:** 실시간 위치 및 상태 데이터를 통해 배차 담당자가 드라이버를 재배치하거나 우선순위를 조정하거나, 지연 발생 시 고객에게 선제적으로 연락하여 배달 실패나 지연을 줄일 수 있습니다.

Databricks 데이터 인텔리전스 플랫폼에서 Zerobus Ingest, Lakebase, Databricks Apps로 이것을 구축하는 방법을 살펴보겠습니다!

### 애플리케이션 아키텍처 개요

이 엔드투엔드 아키텍처는 네 단계를 따릅니다.

1. 데이터 프로듀서가 Zerobus SDK를 사용하여 Databricks Unity Catalog의 Delta 테이블에 이벤트를 직접 씁니다.
2. 연속 동기화 파이프라인이 Delta 테이블에서 Lakebase Postgres 인스턴스로 업데이트된 레코드를 푸시합니다.
3. FastAPI 백엔드가 WebSocket을 통해 Lakebase에 연결하여 실시간 업데이트를 스트리밍합니다.
4. Databricks Apps로 구축된 프론트엔드 애플리케이션이 최종 사용자에게 실시간 데이터를 시각화합니다.

![Application Architecture: Data Producer, Zerobus Ingest, Delta, Lakebase, Databricks Apps](https://www.databricks.com/sites/default/files/inline-images/blog-zerobus-lakebase-arch.png?v=1772426984)

데이터 프로듀서부터 시작해서, 드라이버의 휴대폰에 있는 Data Diner 앱은 주문 배달 경로에서 드라이버의 위치(위도 및 경도 좌표)에 대한 GPS 텔레메트리 데이터를 방출합니다. 이 데이터는 API 게이트웨이로 전송되고, 궁극적으로 수집 아키텍처의 다음 서비스로 전달됩니다.

Zerobus SDK를 사용하면 API 게이트웨이에서 대상 테이블로 이벤트를 전달하는 클라이언트를 빠르게 작성할 수 있습니다. 대상 테이블이 준실시간으로 업데이트되면, 연속 동기화 파이프라인을 생성하여 Lakebase 테이블을 업데이트할 수 있습니다. 마지막으로, Databricks Apps를 활용하여 Postgres에서 WebSocket을 통해 실시간 업데이트를 스트리밍하는 FastAPI 백엔드와 실시간 데이터 흐름을 시각화하는 프론트엔드 애플리케이션을 배포할 수 있습니다.

Zerobus SDK 도입 전에는 스트리밍 아키텍처가 대상 테이블에 도달하기 전에 여러 홉을 거쳐야 했습니다. API 게이트웨이는 Kafka와 같은 스테이징 영역에 데이터를 오프로드해야 했고, Delta 테이블에 트랜잭션을 쓰기 위해 Spark Structured Streaming이 필요했습니다. 레이크하우스가 유일한 목적지임에도 불구하고 이 모든 것이 불필요한 복잡성을 더했습니다. 위의 아키텍처는 이제 Databricks 데이터 인텔리전스 플랫폼이 데이터 수집부터 실시간 분석, 인터랙티브 애플리케이션 구현까지 엔드투엔드 엔터프라이즈 애플리케이션 개발을 어떻게 단순화하는지를 보여줍니다.

## 시작하기

**사전 요구 사항: 필요한 것**

- [Lakebase](https://docs.databricks.com/aws/en/oltp/): AWS와 Azure에서 일반 공개(Generally Available) 상태
- [Zerobus Ingest](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/zerobus-overview): AWS와 Azure에서 일반 공개(Generally Available) 상태
- [Databricks Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/): Databricks Apps를 생성할 수 있는 [권한](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/permissions) 확인

### 1단계: Databricks Unity Catalog에 대상 테이블 생성

클라이언트 애플리케이션이 생성하는 이벤트 데이터는 Delta 테이블에 저장됩니다. 아래 코드를 사용하여 원하는 카탈로그와 스키마에 대상 테이블을 생성하세요.

### 2단계: OAUTH를 이용한 인증

### 3단계: Zerobus 클라이언트 생성 및 대상 테이블에 데이터 수집

아래 코드는 Zerobus API를 사용하여 텔레메트리 이벤트 데이터를 Databricks로 푸시합니다.

#### Change Data Feed (CDF) 제한 사항 및 해결 방법

현재 Zerobus Ingest는 CDF (Change Data Feed)를 지원하지 않습니다. CDF는 Databricks가 Delta 테이블에 새로 기록된 데이터에 대한 변경 이벤트(삽입, 삭제, 업데이트)를 기록할 수 있게 해줍니다. 이 변경 이벤트를 사용하여 Lakebase의 동기화된 테이블을 업데이트할 수 있습니다. Lakebase와 데이터를 동기화하고 프로젝트를 계속하려면, 대상 테이블의 데이터를 새 테이블에 쓰고 해당 테이블에서 CDF를 활성화해야 합니다.

### 4단계: Lakebase 프로비저닝 및 데이터베이스 인스턴스에 데이터 동기화

앱을 구동하기 위해, 이 새로운 CDF 활성화 테이블에서 Lakebase 인스턴스로 데이터를 동기화합니다. 준실시간 대시보드를 지원하기 위해 이 테이블을 연속적으로 동기화합니다.

UI에서 다음을 선택합니다.

- **동기화 모드:** 낮은 지연 시간 업데이트를 위한 연속(Continuous) 모드
- **기본 키(Primary Key):** table_primary_key

이렇게 하면 앱이 최소한의 지연으로 최신 데이터를 반영할 수 있습니다.

{% hint style="info" %}
Databricks SDK를 사용하여 동기화 파이프라인을 프로그래밍 방식으로 생성할 수도 있습니다.
{% endhint %}

#### ForeachWriter를 통한 실시간 모드

Delta에서 Lakebase로의 연속 동기화는 10~15초의 지연이 있습니다. 더 낮은 지연 시간이 필요한 경우, ForeachWriter를 통한 실시간 모드를 사용하여 DataFrame에서 직접 Lakebase 테이블로 데이터를 동기화하는 것을 고려하세요. 이 방법은 데이터를 밀리초 단위로 동기화합니다.

[GitHub의 Lakebase ForeachWriter 코드](https://github.com/christophergrant/lakebase-foreachwriter)를 참조하세요.

![Create synched table into a Lakebase instance](https://www.databricks.com/sites/default/files/inline-images/blog-zerobus-lakebase-create-table.png?v=1772426984)

### 5단계: FastAPI 또는 원하는 프레임워크로 앱 구축

데이터가 Lakebase와 동기화되면 이제 코드를 배포하여 앱을 구축할 수 있습니다. 이 예시에서 앱은 Lakebase에서 이벤트 데이터를 가져와 음식 배달 경로를 이동 중인 드라이버의 활동을 추적하는 준실시간 애플리케이션을 업데이트하는 데 사용합니다. Databricks Apps로 앱 구축에 대한 자세한 내용은 [Databricks Apps 시작하기](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/) 문서를 참조하세요.

![Screenshot of RideShare360 application](https://www.databricks.com/sites/default/files/inline-images/blog-zerobus-lakebase-rideshare.png?v=1772426984)

## 추가 리소스

특정 요구 사항에 맞는 애플리케이션을 직접 구축하기 위한 더 많은 튜토리얼, 데모 및 솔루션 액셀러레이터를 확인하세요.

- **엔드투엔드 애플리케이션 구축:** Python SDK와 REST API를 사용하는 실시간 항해 시뮬레이터가 Databricks Apps와 Databricks Asset Bundles로 요트 선단을 추적합니다. [블로그 읽기](https://community.databricks.com/t5/technical-blog/data-drifter-charting-the-course-from-data-collection-to/ba-p/148397).
- **디지털 트윈 솔루션 구축:** Databricks Apps와 Lakebase로 운영 효율성을 극대화하고 실시간 인사이트와 예지보전을 가속화하는 방법을 알아보세요. [블로그 읽기](https://www.databricks.com/blog/how-build-digital-twins-operational-efficiency).

기술 문서에서 [Zerobus Ingest](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/zerobus-overview), [Lakebase](https://docs.databricks.com/aws/en/oltp/), [Databricks Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)에 대해 자세히 알아볼 수 있습니다. [Databricks Apps Cookbook](https://apps-cookbook.dev/)과 [Cookbook 리소스 컬렉션](https://apps-cookbook.dev/resources)도 참조해 보세요.

## 결론

IoT, 클릭스트림, 텔레메트리 및 유사한 애플리케이션들은 매일 수십억 개의 데이터 포인트를 생성하며, 이는 여러 산업에 걸쳐 중요한 실시간 애플리케이션을 구동하는 데 사용됩니다. 따라서 이러한 시스템에서의 수집을 단순화하는 것이 무엇보다 중요합니다. Zerobus Ingest는 이러한 시스템에서 레이크하우스로 이벤트 데이터를 직접 푸시하는 간소화된 방법을 제공하면서 높은 성능을 보장합니다. 엔드투엔드 엔터프라이즈 애플리케이션 개발을 단순화하기 위해 Lakebase와 잘 결합됩니다.
