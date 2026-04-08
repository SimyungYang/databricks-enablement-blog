# Delta Live Tables: 선언적 ETL 파이프라인의 새로운 기준

**신뢰할 수 있는 데이터 파이프라인을 더 빠르고 쉽게 — Databricks DLT가 ETL을 재정의하는 방법**

작성자: Databricks Engineering Team | 2022년 4월 5일

> **원문**: [Delta Live Tables: Declarative ETL](https://www.databricks.com/blog/delta-live-tables-declarative-etl)

{% hint style="warning" %}
**참고**: 원문 URL(https://www.databricks.com/blog/delta-live-tables-declarative-etl)은 현재 404 오류를 반환합니다. 이 번역은 Databricks 공식 블로그 GA 발표(2022년 4월) 및 공식 DLT 문서를 기반으로 작성되었습니다. 관련 원문은 [Announcing General Availability of Databricks Delta Live Tables](https://www.databricks.com/blog/2022/04/05/announcing-generally-availability-of-databricks-delta-live-tables-dlt.html)에서 확인할 수 있습니다.
{% endhint %}

---

{% hint style="info" %}
**핵심 요약**
- **선언적 ETL**: Delta Live Tables(DLT)는 데이터 엔지니어가 "무엇을 원하는지"만 선언하면, 실행 방법·인프라·의존성 관리를 플랫폼이 자동으로 처리합니다.
- **배치 + 스트리밍 통합**: 동일한 코드로 배치 파일과 실시간 스트리밍 소스를 처리하며, DLT가 실행 시맨틱스를 자동으로 결정합니다.
- **내장 데이터 품질**: CONSTRAINT(제약 조건) 기반의 기대값(Expectations)으로 데이터 품질을 파이프라인 레벨에서 선언적으로 보장합니다.
- **완전 관리형 운영**: 클러스터 프로비저닝, 자동 스케일링, 재시도, 체크포인트, 리니지(Lineage) 추적이 모두 자동화됩니다.
{% endhint %}

---

## 전통적 ETL의 한계: 왜 새로운 접근이 필요한가

데이터 엔지니어링 팀은 수십 년간 동일한 문제와 씨름해 왔습니다. 데이터를 추출하고, 변환하고, 적재하는 것 자체는 단순해 보이지만, 실제 운영 환경에서는 수많은 질문에 답해야 합니다. 데이터를 어떻게 추출할 것인가? 변환 단계를 어떻게 오케스트레이션할 것인가? 인프라를 어떻게 관리하고 스케일링할 것인가? 파이프라인 간 의존성을 어떻게 추적할 것인가? 실패 시 어떻게 재시도할 것인가? 데이터 품질을 어떻게 보장할 것인가?

이 모든 질문은 비즈니스 가치와는 무관한 **도구적 복잡성** 입니다. 데이터 엔지니어가 실제 데이터 변환 로직이 아니라 인프라 관리와 오케스트레이션에 대부분의 시간을 소비하는 것이 전통적 ETL의 근본적인 문제입니다.

전통적인 ETL 파이프라인의 전형적인 과제를 구체적으로 살펴보면 다음과 같습니다. **명령형 코드(Imperative Code)** 방식에서는 각 처리 단계를 순서대로 기술하고 모든 실행 세부 사항을 명시해야 합니다. **수동 의존성 관리** 에서는 테이블 간 의존 관계를 개발자가 직접 정의하고 유지해야 하며, 의존성 변경 시 파이프라인 전체를 수동으로 업데이트해야 합니다. **인프라 부담** 측면에서는 클러스터 크기 결정, 자동 스케일링 설정, 장애 복구 로직 구현이 모두 개발자의 몫입니다. **데이터 품질 관리** 는 별도의 검증 코드를 작성해야 하며, 품질 이슈가 하류(Downstream)로 전파되는 것을 막기 위한 추가 로직이 필요합니다.

> "우리는 더 이상 Databricks에게 ETL을 '어떻게' 할지 알려주지 않습니다. 우리가 '무엇을 원하는지'만 말하면, Databricks가 나머지를 알아서 처리합니다."

---

## Delta Live Tables란 무엇인가

Delta Live Tables(DLT)는 Databricks가 개발한 **선언적 ETL 프레임워크** 입니다. DLT는 단순히 새로운 도구가 아니라, ETL 개발 패러다임을 근본적으로 바꾸는 접근 방식입니다. 데이터 엔지니어는 SQL 또는 Python을 사용해 데이터 변환의 **결과** 만 정의하면 되고, 실행 순서·클러스터 관리·의존성 해소·오케스트레이션은 DLT가 자동으로 처리합니다.

DLT의 핵심 철학은 **선언형 프로그래밍(Declarative Programming)** 에 있습니다. 개발자는 원하는 상태(What)를 기술하고, 플랫폼이 그 상태에 도달하는 방법(How)을 결정합니다. 이는 Terraform이 인프라를 선언적으로 관리하는 것과 동일한 원리입니다.

DLT로 데이터 엔지니어가 정의하는 것은 다음과 같습니다.

- **소스(Source)**: 데이터를 어디서 읽을 것인가
- **변환(Transformations)**: 데이터를 어떻게 바꿀 것인가
- **기대값(Expectations)**: 데이터 품질 조건은 무엇인가
- **의존성(Dependencies)**: 테이블 간 관계는 어떻게 되는가

그리고 DLT가 자동으로 처리하는 것은 다음과 같습니다.

- **오케스트레이션**: 실행 순서와 태스크 스케줄링
- **인프라 관리**: 클러스터 프로비저닝과 자동 스케일링
- **의존성 해소**: DAG 자동 생성 및 관리
- **리니지 추적**: 엔드투엔드 데이터 계보 자동 캡처
- **모니터링**: 파이프라인 상태와 데이터 품질 메트릭 추적
- **재시도와 복구**: 장애 시 자동 재시도 및 체크포인트 기반 복구
- **배치 + 스트리밍 통합**: 동일 코드로 두 처리 방식 지원

---

## DLT의 실행 모델: 내부에서 무슨 일이 일어나는가

DLT가 선언적 코드를 받아 실제로 실행하기까지의 과정을 단계별로 이해하면 프레임워크를 더욱 효과적으로 활용할 수 있습니다.

### 1단계: 선언적 코드 작성

가장 기본적인 DLT 예시를 보겠습니다.

```sql
CREATE STREAMING TABLE orders_silver_cleaned
AS
SELECT *
FROM STREAM(LIVE.bronze_orders)
WHERE order_status IS NOT NULL;
```

이 코드에서 개발자가 지정한 것은 세 가지뿐입니다. 원하는 테이블 이름, 소스 의존성, 그리고 변환 로직입니다. 실행 순서, 클러스터 크기, 재시도 로직, 장애 처리, 배치/스트리밍 결정 — 이 모든 것을 개발자는 지정하지 않습니다.

### 2단계: DAG 자동 컴파일

DLT는 코드 내 테이블 참조를 분석하여 Directed Acyclic Graph(방향성 비순환 그래프)를 자동으로 생성합니다. 복잡한 파이프라인도 마찬가지입니다.

| 레이어 | 테이블 | 소스 |
|--------|--------|------|
| Landing | 원시 파일 | 외부 소스 |
| Bronze | orders\_bronze | Landing 파일 |
| Silver | orders\_silver\_cleaned | orders\_bronze |
| Gold | daily\_sales\_gold | orders\_silver |

개발자가 이 DAG를 명시적으로 정의할 필요가 없습니다. DLT가 코드에서 의존성을 추론하여 자동으로 구성합니다.

### 3단계: 실행 시맨틱스 결정

DLT는 소스 유형에 따라 실행 방식을 자동으로 결정합니다.

- **정적 파일 소스** → 배치(Batch) 처리
- **스트리밍 소스(Kafka, Kinesis 등)** → 스트리밍 처리
- **혼합 소스** → 하이브리드 파이프라인

증분(Incremental) vs 전체(Full) 처리도 자동으로 결정됩니다. Append-only 소스는 증분 처리, CDC(Change Data Capture) 소스는 병합(Merge) 로직을 적용합니다.

### 4단계: 컴퓨팅 프로비저닝

DLT는 파이프라인 유형과 데이터 볼륨에 맞게 클러스터를 자동으로 선택하고 프로비저닝합니다. **서버리스 DLT(Serverless DLT)** 를 사용하면 클러스터 관리가 완전히 추상화되어, 개발자는 컴퓨팅 인프라에 대해 전혀 신경 쓸 필요가 없습니다.

### 5단계: 오케스트레이션, 재시도, 장애 처리

DLT는 DAG 기반으로 태스크 실행 순서를 자동으로 결정하고, 실패한 스테이지를 재시도하며, 마지막 일관된 체크포인트에서 재시작합니다. 이는 정확히 한 번 처리(Exactly-once Processing)를 보장합니다. 별도의 Airflow, ADF 같은 오케스트레이션 도구 없이 DLT가 이 역할을 대체합니다.

### 6단계: 자동 리니지 추적

DLT는 입력, 출력, 변환 로직을 모두 파악하고 있기 때문에 엔드투엔드 데이터 계보를 자동으로 구축합니다. 컬럼 수준의 리니지까지 별도 도구 없이 제공됩니다. Unity Catalog와 통합 시 이 리니지 정보는 Data Explorer에서 시각적으로 확인할 수 있습니다.

### 7단계: 지속적 최적화

DLT는 실행 과정에서 세 가지 방식으로 성능을 자동 최적화합니다. **증분 처리** 는 변경된 데이터만 재처리합니다. **의존성 가지치기(Dependency Pruning)** 는 업스트림이 변경되지 않으면 다운스트림 테이블 재계산을 건너뜁니다. **적응형 실행(Adaptive Execution)** 은 데이터 볼륨과 메트릭에 따라 실행 계획을 동적으로 조정합니다.

---

## 데이터 품질: 기대값(Expectations)으로 선언적 품질 보장

DLT의 가장 강력한 기능 중 하나는 **선언적 데이터 품질 관리** 입니다. 별도의 검증 코드를 작성하는 대신, 데이터 품질 조건을 테이블 정의에 직접 선언합니다.

```sql
CREATE STREAMING TABLE orders_silver_cleaned (
  CONSTRAINT valid_order_id EXPECT (order_id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT valid_amount   EXPECT (amount > 0)           ON VIOLATION DROP ROW,
  CONSTRAINT valid_customer EXPECT (customer_id IS NOT NULL) ON VIOLATION WARN
)
AS
SELECT
  orderid     AS order_id,
  orderdate   AS order_date,
  customerid  AS customer_id,
  totalamount AS amount,
  status
FROM STREAM(LIVE.orders_bronze);
```

위의 예시에서 세 가지 제약 조건을 정의했습니다. 각 제약 조건은 위반 시 행동 방침(ON VIOLATION)을 함께 선언합니다.

다음 표는 ON VIOLATION 옵션과 그 의미를 정리한 것입니다. 비즈니스 중요도에 따라 적절한 정책을 선택해야 합니다.

| ON VIOLATION 옵션 | 동작 | 사용 시나리오 |
|-------------------|------|---------------|
| `DROP ROW` | 위반 행을 제거하고 처리 계속 | 필수 식별자 누락, 음수 금액 등 치명적 오류 |
| `FAIL UPDATE` | 파이프라인 실행 중단 | 데이터 무결성이 절대적으로 중요한 경우 |
| `WARN` (기본값) | 경고 로그 기록, 처리 계속 | 소프트한 품질 이슈, 모니터링 목적 |

`DROP ROW`는 불량 데이터를 즉시 제거하여 다운스트림에 오염이 전파되는 것을 막습니다. `FAIL UPDATE`는 파이프라인 전체를 중단시켜 즉각적인 대응을 강제합니다. `WARN`은 기록을 남기되 처리를 계속하여 데이터 탐색 단계에서 유용합니다.

DLT는 이 기대값들을 자동으로 추적하고, UI에서 품질 메트릭 대시보드를 통해 시간에 따른 품질 트렌드를 시각화합니다. 이를 통해 데이터 품질 저하를 사전에 감지하고 근본 원인을 빠르게 파악할 수 있습니다.

---

## Medallion 아키텍처와 DLT의 자연스러운 통합

Delta Live Tables는 **Medallion 아키텍처(메달리온 아키텍처)** — Bronze, Silver, Gold 레이어 구조 — 와 완벽하게 설계적으로 정렬되어 있습니다. DLT의 선언적 의존성 모델은 레이어 간 데이터 흐름을 자연스럽게 표현합니다.

### Bronze 레이어: 원시 데이터 수집

Bronze 레이어는 소스 데이터를 최소한의 변환만으로 Delta 포맷으로 저장합니다. 이 레이어는 **진실의 원천(Source of Truth)** 역할을 하며, 불변성(Immutability)과 재처리 가능성(Replayability)이 핵심입니다.

```sql
-- Auto Loader를 사용한 클라우드 스토리지 수집
CREATE STREAMING TABLE orders_bronze
AS
SELECT
  *,
  _metadata.file_name AS filename,
  current_timestamp() AS load_time
FROM cloud_files(
  '/Volumes/catalog/schema/landing_volume/orders',
  'csv',
  map('cloudFiles.inferColumnTypes', 'true')
);
```

Auto Loader(`cloud_files`)는 새로운 파일이 도착하면 자동으로 감지하여 증분 수집합니다. 파일 메타데이터(`_metadata.file_name`)를 함께 저장하면 데이터 계보 추적이 용이해집니다.

### Silver 레이어: 정제와 풍부화

Silver 레이어는 Bronze 데이터를 정제하고, 비즈니스 규칙을 적용하며, 데이터 품질을 보장합니다. SCD Type 2(Slowly Changing Dimension Type 2)와 같은 복잡한 병합 로직도 선언적으로 처리할 수 있습니다.

```sql
-- 데이터 품질 기대값이 포함된 Silver 테이블
CREATE STREAMING TABLE orders_silver_cleaned (
  CONSTRAINT valid_order   EXPECT (order_id IS NOT NULL)   ON VIOLATION DROP ROW,
  CONSTRAINT valid_customer EXPECT (customer_id IS NOT NULL) ON VIOLATION DROP ROW
)
AS
SELECT
  orderid     AS order_id,
  orderdate   AS order_date,
  customerid  AS customer_id,
  totalamount AS total_amount,
  status,
  filename    AS file_name,
  load_time
FROM STREAM(LIVE.orders_bronze);
```

SCD Type 2가 필요한 고객 차원 테이블은 `APPLY CHANGES INTO` 또는 `AUTO CDC` 구문으로 선언적으로 처리합니다.

```sql
-- SCD Type 2: 고객 이력 추적
CREATE STREAMING TABLE customers_silver;

APPLY CHANGES INTO LIVE.customers_silver
FROM STREAM(LIVE.customers_silver_cleaned)
KEYS (customer_id)
SEQUENCE BY load_time
STORED AS SCD TYPE 2;
```

위 코드 몇 줄로 DLT는 자동으로 각 고객 레코드의 변경 이력을 관리합니다. 유효 기간(`valid_from`, `valid_to`), 현재 버전 플래그(`is_current`), 버전 번호 관리 등이 모두 자동화됩니다. 전통적인 방식으로 구현하면 수십 줄의 복잡한 MERGE SQL이 필요한 작업입니다.

### Gold 레이어: 비즈니스 집계

Gold 레이어는 분석가, 비즈니스 사용자, ML 팀을 위한 도메인별 집계 데이터를 제공합니다. DLT의 `MATERIALIZED VIEW`는 의존성이 변경될 때 자동으로 갱신됩니다.

```sql
-- 도시별 매출 집계 Materialized View
CREATE MATERIALIZED VIEW city_wise_sales_gold
AS
SELECT
  c.city,
  SUM(o.total_amount) AS total_sales,
  COUNT(DISTINCT o.order_id) AS order_count
FROM LIVE.orders_silver  AS o
JOIN LIVE.customers_silver AS c ON o.customer_id = c.customer_id
GROUP BY c.city;
```

---

## Python API로 작성하는 DLT 파이프라인

SQL만큼 Python API도 강력합니다. 복잡한 비즈니스 로직, 커스텀 UDF, 재사용 가능한 유틸리티 함수가 필요한 경우 Python DLT API를 활용합니다.

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import current_timestamp, col, sum as _sum

# 소스 경로 설정 (파이프라인 파라미터로 관리)
source_path = spark.conf.get("source_path")

# Bronze: 주문 데이터 수집
@dp.table(name="orders_bronze")
def orders_bronze():
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "csv")
            .option("cloudFiles.inferColumnTypes", "true")
            .load(f"{source_path}/orders")
            .withColumn("filename", col("_metadata.file_path"))
            .withColumn("load_time", current_timestamp())
    )

# Silver: 데이터 품질 기대값 적용
@dp.table()
@dp.expect_or_drop("valid_order_id", "order_id is not null")
@dp.expect_or_drop("valid_customer_id", "customer_id is not null")
def orders_silver_cleaned():
    return (
        spark.readStream.table("orders_bronze")
            .selectExpr(
                "orderid     AS order_id",
                "orderdate   AS order_date",
                "customerid  AS customer_id",
                "totalamount AS total_amount",
                "status",
                "filename AS file_name",
                "load_time"
            )
    )

# Gold: 도시별 매출 Materialized View
@dp.materialized_view()
def city_wise_sales_gold():
    orders    = spark.read.table("orders_silver")
    customers = spark.read.table("customers_silver")
    return (
        orders.join(customers, "customer_id")
              .groupBy("city")
              .agg(_sum("total_amount").alias("total_sales"))
    )
```

Python DLT API의 데코레이터 방식(`@dp.table`, `@dp.expect_or_drop`, `@dp.materialized_view`)은 코드를 직관적이고 테스트하기 쉽게 만들어 줍니다.

---

## AUTO CDC: 변경 데이터 캡처의 선언적 처리

**AUTO CDC(자동 변경 데이터 캡처)** 는 DLT의 최신 CDC 처리 방식으로, 전통적인 `APPLY CHANGES INTO`보다 더욱 간결하고 강력합니다.

```sql
-- AUTO CDC를 사용한 SCD Type 2
CREATE STREAMING TABLE customers_silver;

CREATE FLOW customer_silver_flow AS AUTO CDC
INTO customers_silver
FROM STREAM(customers_silver_cleaned)
KEYS (customer_id)
SEQUENCE BY load_time
STORED AS SCD TYPE 2;
```

AUTO CDC는 각 마이크로배치마다 타겟 테이블의 현재 상태를 조회하고, 유입 레코드와 비교하여 INSERT, UPDATE, DELETE 여부를 자동으로 판별합니다.

AUTO CDC가 지원하는 네 가지 재계산 전략은 다음과 같습니다.

| 전략 | 사용 시점 | DLT 동작 |
|------|-----------|----------|
| **단조 증분(Monotonic Append)** | 순서가 보장된 CDC 피드 | 신규 레코드만 처리, 이력 수정 불필요 |
| **병합 업데이트(Merge Updates)** | 키 수준 변경이 있는 경우 | 영향받은 키만 만료/재삽입, 전체 재계산 불필요 |
| **파티션 재계산(Partition Recompute)** | 늦게 도착한 데이터로 과거 이력 수정 필요 | 영향받은 파티션/시간 범위만 재계산 |
| **전체 재계산(Full Recompute)** | 대규모 백필, 변환 로직 전면 변경 | 테이블 전체 재구성, 코드 변경 불필요 |

`KEYS`는 비즈니스 엔티티의 식별자를 정의하고, `SEQUENCE BY`는 변경의 올바른 순서를 결정합니다. 이 두 요소가 없으면 SCD Type 2의 신뢰성을 보장할 수 없습니다.

---

## Unity Catalog와 서버리스 DLT: 현대적 DLT 파이프라인

DLT는 현재 두 가지 방식으로 운영됩니다.

다음 표는 레거시 방식과 현대적 방식의 주요 차이를 보여줍니다. 새로운 프로젝트에서는 Unity Catalog + 서버리스 조합이 권장됩니다.

| 항목 | 레거시 방식 | 현대적 방식 |
|------|-------------|-------------|
| **메타스토어** | Hive Metastore | Unity Catalog |
| **컴퓨팅** | Classic Job Cluster | Serverless DLT |
| **스토리지 참조** | Mount Points | Volumes (3-레벨 네임스페이스) |
| **CDC 구문** | `APPLY CHANGES INTO` | `AUTO CDC` (또는 혼용) |
| **네임스페이스** | 2-레벨 (database.table) | 3-레벨 (catalog.schema.table) |
| **LIVE 키워드** | 필요 | 불필요 |
| **거버넌스** | 제한적 | Unity Catalog 완전 통합 |

**서버리스 DLT** 는 클러스터 관리를 완전히 Databricks에 위임합니다. 클러스터 크기 선택, 스케일업/다운, 실행 시 프로비저닝, 완료 후 종료가 모두 자동화됩니다. 데이터 수집 워크로드에서 최대 5배 향상된 비용 대비 성능을 제공하며, 복잡한 변환에서는 최대 98%의 비용 절감 효과가 보고되었습니다.

**Unity Catalog** 와 통합 시 DLT 파이프라인은 자동으로 세밀한 접근 제어, 데이터 리니지 추적, 감사 로그를 활용할 수 있습니다. Mount Points를 Volumes로 교체하면 레거시 마운트 포인트의 보안 한계를 극복하고 Unity Catalog 거버넌스를 완전히 활용할 수 있습니다.

---

## 실제 도입 사례: 기업들이 DLT를 선택하는 이유

Delta Live Tables는 출시 이후 전 세계 1,000개 이상의 기업에서 채택되었습니다. ADP, Shell, H&R Block, Jumbo, Bread Finance, JLL을 포함한 다양한 산업의 선도 기업들이 DLT를 활용하여 다음 세대의 셀프서비스 분석과 데이터 애플리케이션을 구축하고 있습니다.

**Deloitte** 는 DLT를 활용하여 복잡한 데이터 파이프라인을 선언적으로 구축하는 내부 모범 사례를 개발했습니다. 팀의 생산성이 크게 향상되었고, 파이프라인 장애로 인한 운영 부담이 현저히 감소했습니다.

DLT 도입 기업들이 공통적으로 보고하는 비즈니스 효과는 세 가지입니다. **운영 부담 감소** 는 별도 오케스트레이션 도구, 수동 클러스터 관리, 커스텀 재시도 로직, 모니터링 프레임워크가 불필요해집니다. **데이터 신뢰성 향상** 은 내장 기대값과 자동 품질 추적으로 데이터 품질 이슈를 조기에 발견하고 하류 오염을 방지합니다. **개발 속도 가속** 은 인프라와 오케스트레이션이 아닌 비즈니스 로직과 데이터 모델링에 집중할 수 있어 파이프라인 개발 사이클이 단축됩니다.

---

## 선언적 ETL이 팀 생산성에 미치는 영향

선언적 ETL은 단순히 기술적 개선이 아니라 팀의 일하는 방식을 근본적으로 바꿉니다.

전통적인 명령형 ETL에서는 데이터 엔지니어가 비즈니스 로직을 구현하기 전에 먼저 인프라 설계, 오케스트레이션 구조, 재시도 전략을 결정해야 했습니다. 이는 높은 인지 부하(Cognitive Load)를 유발하고 실수를 낳습니다. DLT의 선언적 접근은 이 인지 부하를 플랫폼에 위임합니다.

또한, 선언적 코드는 의도가 명확하기 때문에 코드 리뷰와 유지보수가 쉽습니다. 새로운 팀원이 파이프라인 코드를 보더라도 "이 코드가 무엇을 하는가"를 즉시 이해할 수 있습니다.

실패 시 복구도 간단해집니다. DLT가 체크포인트와 상태를 관리하기 때문에, 파이프라인이 실패하면 마지막 일관된 상태에서 자동 재시작됩니다. 데이터 중복이나 상태 손상 없이 안전하게 재처리됩니다.

---

## DLT와 Lakeflow: 미래 방향

2025년 Databricks Data + AI Summit에서 Delta Live Tables는 **Lakeflow Declarative Pipelines** 라는 이름으로 더 넓은 Lakeflow 플랫폼에 통합되었습니다. Lakeflow는 세 가지 핵심 컴포넌트로 구성됩니다.

- **Lakeflow Connect**: SQL Server, Salesforce, Workday, Google Analytics, ServiceNow, SharePoint 등 엔터프라이즈 소스를 위한 네이티브 고스케일 커넥터
- **Lakeflow Declarative Pipelines** (기존 DLT): 선언적 변환 레이어
- **Lakeflow Jobs**: 워크플로우 오케스트레이션

이 통합은 DLT의 핵심 선언적 철학을 유지하면서 더 넓은 데이터 엔지니어링 생태계와 통합되는 방향입니다. 기존 DLT 파이프라인은 코드 변경 없이 Lakeflow Declarative Pipelines로 전환됩니다.

{% hint style="info" %}
**마이그레이션 가이드**: 기존 DLT 파이프라인을 Lakeflow Declarative Pipelines로 전환하는 방법은 [What happened to Delta Live Tables (DLT)?](https://docs.databricks.com/aws/en/ldp/where-is-dlt) 문서를 참고하세요.
{% endhint %}

---

## 결론: 현대 데이터 엔지니어링의 새로운 기준

Delta Live Tables는 ETL 개발의 패러다임 전환을 대표합니다. 파이프라인 코드를 도구 관리가 아닌 **데이터 모델링** 에 집중할 수 있게 해주는 이 프레임워크는, 현대 데이터 엔지니어링에서 점점 더 중요한 역할을 차지하고 있습니다.

선언적 접근, 내장 데이터 품질, 통합 배치+스트리밍 처리, 자동 리니지 추적 — 이 네 가지 특성이 DLT를 단순한 편의 도구가 아닌, 엔터프라이즈급 데이터 파이프라인의 근본적인 재설계로 만들어 줍니다.

> "현대 데이터 엔지니어링은 Spark 코드를 작성하는 것에 관한 것이 아닙니다. 실제 세계의 데이터 동작에 자동으로 적응하는 탄력적이고 상태 인식 가능한 데이터 시스템을 설계하는 것입니다."

---

## 추가 자료

- [Delta Live Tables 공식 문서](https://docs.databricks.com/aws/en/delta-live-tables/index.html)
- [Lakeflow Spark Declarative Pipelines](https://docs.databricks.com/aws/en/ldp)
- [Getting Started with Delta Live Tables](https://www.databricks.com/discover/pages/getting-started-with-delta-live-tables)
- [Announcing GA of Databricks Delta Live Tables](https://www.databricks.com/blog/2022/04/05/announcing-generally-availability-of-databricks-delta-live-tables-dlt.html)
- [Cost-effective Incremental ETL with Serverless DLT](https://www.databricks.com/blog/cost-effective-incremental-etl-serverless-compute-delta-live-tables-pipelines)
- [Introducing Databricks Lakeflow](https://www.databricks.com/blog/introducing-databricks-lakeflow)
