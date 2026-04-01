# 데이터 엔지니어링 비교

## ETL 파이프라인

| 항목 | Databricks | Snowflake | AWS Redshift/Glue | BigQuery/Dataflow | MS Fabric |
|---|---|---|---|---|---|
| ** 파이프라인 엔진**| Lakeflow (DLT) — 선언적 | Dynamic Tables / Snowpark | Glue (Spark 기반) | Dataflow (Apache Beam) | Data Factory + Dataflow Gen2 |
| ** 프로그래밍 모델**| 선언적 ("무엇을" 정의하면 자동 실행) | Dynamic Tables: 선언적(SQL만), Snowpark: 명령적 | 명령적 (모든 단계를 코드로) | 명령적 (Beam Pipeline) | GUI 기반 + Spark |
| ** 언어 지원**| SQL + Python | SQL (Dynamic Tables), Python/Java/Scala (Snowpark) | Python, Scala (Glue) | Java, Python (Beam) | SQL + Python + GUI |
| ** 자동 오류 복구**| 자동 재시도, 체크포인트, idempotent 보장 | 제한적 | 수동 구현 필요 | Beam Checkpoint | 제한적 |
| ** 의존성 관리**| 자동 DAG 생성 및 실행 순서 결정 | Dynamic Tables: 자동 | Glue: 수동 / Step Functions | 수동 (Composer) | Data Factory 오케스트레이션 |

## 데이터 수집 및 CDC

| 항목 | Databricks | Snowflake | AWS | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| ** 파일 수집**| Auto Loader — 증분 자동 감지, 스키마 진화 자동 | Snowpipe (파일 기반) | Glue Crawler + S3 이벤트 | Load / Transfer Service | Dataflow Gen2 |
| ** 스트리밍 수집**| Structured Streaming + Kafka 네이티브 | Snowpipe Streaming | Kinesis + MSK (별도 서비스) | Pub/Sub + Dataflow | Event Streams |
| **CDC**| `APPLY CHANGES` — SCD Type 1/2 자동, 코드 한 줄 | Streams + Tasks (다단계) | DMS + Glue (복잡) | Datastream (별도 서비스) | Mirroring |
| ** 스키마 진화**| Auto Loader 자동 스키마 감지/진화 | 수동 ALTER TABLE | Glue Crawler (주기적 스캔) | 자동 스키마 감지 | 자동 감지 |
| ** 배치/스트리밍 통합**| 동일 코드로 배치↔스트리밍 전환 | 별도 구현 필요 | Glue(배치) vs Kinesis(스트리밍) 분리 | Dataflow 통합 가능 (복잡) | 분리 |
| **Exactly-once**| Delta Lake 트랜잭션 보장 | At-least-once | 서비스마다 상이 | Dataflow: Exactly-once | 제한적 |
| **SaaS 커넥터**| Lakeflow Connect (Salesforce, Workday 등) | Snowflake Connectors (제한적) | Glue + AppFlow | Transfer Service | Data Factory 커넥터 |

## 데이터 품질

| 항목 | Databricks | Snowflake | AWS | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| ** 품질 검증**| DLT Expectations (파이프라인 내장, 선언적) | Data Metric Functions | Glue Data Quality (Deequ) | Dataplex Data Quality | 제한적 |
| ** 위반 처리**| FAIL / DROP / WARN 선택 가능 | 알림만 | 중단 또는 로그 | 알림만 | 알림 기반 |
| ** 자동 모니터링**| Expectation 메트릭 자동 수집 + 대시보드 | 수동 모니터링 | CloudWatch 연동 | Dataplex 대시보드 | 제한적 |
| **Lakehouse Monitor**| 프로파일링 + 드리프트 감지 + 알림 | 미지원 | 미지원 | 미지원 | 미지원 |

{% hint style="success" %}
**Databricks Lakeflow(DLT)의 핵심**: "무엇을" 원하는지만 선언하면, 실행 계획, 오류 복구, 데이터 품질 검증, 의존성 관리를 플랫폼이 자동 처리합니다. `APPLY CHANGES`는 CDC를 코드 한 줄로 해결하며, 배치와 스트리밍도 동일한 코드로 통합됩니다.
{% endhint %}

{% hint style="warning" %}
** 경쟁사 장점**: Snowflake의 Dynamic Tables는 SQL만으로 선언적 파이프라인을 구성할 수 있어 SQL 전문가에게 친숙합니다. MS Fabric의 Data Factory는 GUI 기반 파이프라인 설계로 코딩이 부담스러운 팀에게 적합합니다. BigQuery의 완전 서버리스 특성은 인프라 관리 부담을 최소화합니다.
{% endhint %}

---

## Lakeflow (DLT) vs 경쟁사 ETL 엔진 심층 비교

### 선언적 vs 명령적 파이프라인

데이터 엔지니어링에서 가장 중요한 패러다임 차이는 ** 선언적(Declarative)**vs ** 명령적(Imperative)** 접근 방식입니다.

| 접근 방식 | 설명 | 장점 | 단점 |
|---|---|---|---|
| ** 선언적**(Databricks DLT, Snowflake Dynamic Tables) | "무엇을" 원하는지만 정의 | 코드 간결, 자동 의존성/오류 관리 | 세밀한 제어 어려움 |
| ** 명령적**(Glue, Dataflow, Airflow) | "어떻게" 처리할지 모든 단계를 코드로 | 완전한 제어 가능 | 코드 복잡, 오류 처리 수동 |

### DLT vs Dynamic Tables vs dbt 비교

| 항목 | Databricks DLT | Snowflake Dynamic Tables | dbt (3rd party) |
|---|---|---|---|
| ** 실행 모델**| 선언적 — 자동 DAG + 자동 실행 | 선언적 — SQL 기반 자동 갱신 | 선언적 — SQL 기반, 외부 오케스트레이션 필요 |
| ** 지원 언어**| SQL + Python | SQL Only | SQL (Jinja 템플릿) |
| ** 스트리밍 지원**| 네이티브 (배치↔스트리밍 동일 코드) | 미지원 (배치만) | 미지원 (배치만) |
| **CDC 지원**| `APPLY CHANGES` 내장 (SCD Type 1/2) | Streams + Tasks (다단계 수동) | Snapshot (SCD Type 2, 제한적) |
| ** 데이터 품질**| Expectations 내장 (FAIL/DROP/WARN) | Data Metric Functions (별도) | dbt tests (별도 실행) |
| ** 자동 복구**| 체크포인트 + idempotent 자동 | 제한적 | 없음 (오케스트레이터 의존) |
| ** 의존성 관리**| 자동 DAG 생성 | 자동 (SQL 참조 기반) | 자동 (ref() 함수) |
| ** 오케스트레이션**| 내장 (Workflows / Jobs) | 내장 (자동 스케줄) | 외부 필요 (Airflow/Dagster) |
| ** 환경 관리**| Development/Production 모드 내장 | 없음 | Profiles 기반 |
| ** 비용**| Databricks DBU | Snowflake Credit | 오픈소스 (무료) + Compute 비용 |

{% hint style="info" %}
**DLT의 핵심 장점 3가지**: (1) SQL과 Python 모두 선언적으로 사용 가능, (2) 스트리밍과 배치를 동일 코드로 통합, (3) 데이터 품질 검증이 파이프라인에 내장. dbt는 SQL만 지원하고 스트리밍이 불가하며, Dynamic Tables도 SQL만 지원합니다.
{% endhint %}

### DLT 파이프라인 코드 예시 (경쟁사 대비 간결함)

**Databricks DLT — CDC 처리 (코드 한 줄)**

```sql
-- CDC 스트리밍 수집 + SCD Type 2 자동 적용
CREATE OR REFRESH STREAMING TABLE customers;

APPLY CHANGES INTO LIVE.customers
FROM STREAM(LIVE.customers_cdc)
KEYS (customer_id)
APPLY AS DELETE WHEN operation = 'DELETE'
SEQUENCE BY updated_at
STORED AS SCD TYPE 2;
```

**Snowflake — 동일 CDC 처리 (다단계)**

```sql
-- 1단계: Stream 생성
CREATE STREAM customers_stream ON TABLE raw_customers;

-- 2단계: Task 생성
CREATE TASK customers_merge_task
  WAREHOUSE = 'ETL_WH'
  SCHEDULE = '1 MINUTE'
AS
  MERGE INTO customers t
  USING customers_stream s ON t.customer_id = s.customer_id
  WHEN MATCHED AND s.METADATA$ACTION = 'DELETE' THEN DELETE
  WHEN MATCHED THEN UPDATE SET ...
  WHEN NOT MATCHED THEN INSERT ...;

-- 3단계: SCD Type 2는 별도 로직 구현 필요 (수십 줄)
-- 4단계: Task 시작
ALTER TASK customers_merge_task RESUME;
```

---

## Auto Loader vs 경쟁사 파일 수집

### Auto Loader 상세 기능

| 기능 | Auto Loader | Snowpipe | Glue Crawler + S3 Events | BigQuery Transfer |
|---|---|---|---|---|
| ** 수집 방식**| 클라우드 스토리지 이벤트 기반 (증분) | S3/Azure 이벤트 기반 | S3 이벤트 + Lambda | 스케줄 기반 |
| ** 새 파일 감지**| 자동 (이벤트 + 디렉토리 리스팅 폴백) | 자동 (이벤트 기반) | 수동 설정 필요 | 스케줄 기반 |
| ** 스키마 추론**| 자동 (첫 배치에서 추론) | 수동 (CREATE TABLE 필요) | Crawler 주기적 스캔 | 자동 |
| ** 스키마 진화**| 자동 (신규 컬럼 추가, 타입 변경 감지) | 수동 (ALTER TABLE 필요) | Crawler 재실행 필요 | 제한적 |
| ** 스키마 힌트**| `cloudFiles.schemaHints`로 타입 명시 가능 | N/A | N/A | N/A |
| **Rescue 컬럼**| 스키마 불일치 데이터를 _rescued_data에 자동 저장 | 오류 발생/누락 | 오류 발생/누락 | 오류 발생 |
| ** 파일 포맷**| JSON, CSV, Parquet, Avro, ORC, Text, Binary | CSV, JSON, Parquet, Avro | 다양 | CSV, JSON, Parquet, Avro, ORC |
| ** 중복 방지**| 내장 (파일별 체크포인트) | 내장 | 수동 구현 | 제한적 |
| ** 확장성**| 수십억 파일까지 확장 | 대규모 가능 | 복잡도 증가 | 대규모 가능 |
| ** 비용**| Databricks 컴퓨팅 비용만 | Snowpipe Credit | Glue + Lambda 비용 | Transfer Service 비용 |

{% hint style="success" %}
**Auto Loader의 핵심 차별화**: ** 스키마 진화 자동 처리** 와 **Rescue 컬럼** 입니다. 실 운영 환경에서 소스 시스템의 스키마 변경은 불가피합니다. Auto Loader는 새 컬럼이 추가되면 자동으로 테이블에 반영하고, 스키마 불일치 레코드는 _rescued_data에 보관하여 데이터 손실 Zero를 보장합니다.
{% endhint %}

---

## Structured Streaming vs 경쟁사 스트리밍

### 스트리밍 아키텍처 비교

| 항목 | Databricks Structured Streaming | Snowflake Snowpipe Streaming | AWS Kinesis + MSK | GCP Pub/Sub + Dataflow | MS Fabric Event Streams |
|---|---|---|---|---|---|
| ** 엔진**| Apache Spark Structured Streaming | 독점 스트리밍 엔진 | Kinesis Data Streams / MSK | Apache Beam on Dataflow | Event Hubs + Spark |
| ** 프로그래밍 모델**| DataFrame API (배치와 동일) | API 기반 (Row 삽입) | KCL / Kafka Consumer API | Beam Pipeline API | Event Hubs SDK |
| **Exactly-once**| Delta Lake 트랜잭션 보장 | At-least-once | Kinesis: At-least-once | Beam: Exactly-once | At-least-once |
| ** 지연 시간**| Trigger Once / 마이크로 배치 (초 단위) | 실시간 (초 단위) | 실시간 (밀리초) | 실시간 (초 단위) | 실시간 |
| ** 배치 통합**| 동일 코드 (trigger 옵션만 변경) | 별도 구현 | 완전 별도 서비스 | Beam으로 통합 가능 (복잡) | 별도 |
| ** 상태 관리**| 내장 (체크포인트, 워터마크) | 제한적 | KCL 체크포인트 | Beam State API | 제한적 |
| ** 윈도우 연산**| Tumbling, Sliding, Session 윈도우 | 미지원 | 수동 구현 | Beam 윈도우 (풍부) | 제한적 |
| **Kafka 통합**| 네이티브 (Spark-Kafka 커넥터) | 별도 (Kafka Connector) | MSK 네이티브 | Pub/Sub 사용 | Event Hubs (Kafka 호환) |

### 배치↔스트리밍 통합의 가치

Databricks의 핵심 차별점 중 하나는 ** 동일 코드로 배치와 스트리밍을 전환** 할 수 있다는 점입니다.

```python
# 스트리밍 모드
df = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "json") \
  .load("/data/events/")

df.writeStream.format("delta") \
  .option("checkpointLocation", "/checkpoints/events") \
  .trigger(processingTime="10 seconds") \  # ← 이 줄만 변경
  .toTable("catalog.schema.events")

# 배치 모드로 전환: trigger만 변경
# .trigger(availableNow=True)  ← 배치로 전환
```

경쟁사에서는 스트리밍과 배치가 ** 완전히 다른 서비스/코드** 를 요구합니다.

| 플랫폼 | 스트리밍 서비스 | 배치 서비스 | 코드 재사용 |
|---|---|---|---|
| **Databricks**| Structured Streaming | Spark Batch | **100% 동일 코드**|
| **Snowflake**| Snowpipe Streaming | Dynamic Tables / SQL | 별도 코드 |
| **AWS**| Kinesis / MSK | Glue | 완전 별도 |
| **GCP**| Pub/Sub + Dataflow | BigQuery Load | Beam으로 일부 통합 가능 |
| **Fabric**| Event Streams | Data Factory | 별도 |

---

## Lakeflow Connect — SaaS 데이터 수집

### Lakeflow Connect vs 경쟁사 SaaS 커넥터

| 항목 | Databricks Lakeflow Connect | Snowflake Connectors | AWS AppFlow + Glue | Fivetran/Airbyte (3rd party) |
|---|---|---|---|---|
| ** 통합 수준**| 네이티브 (Unity Catalog 통합) | 네이티브 | AWS 서비스 조합 | 별도 SaaS |
| ** 지원 소스**| Salesforce, Workday, SharePoint, ServiceNow 등 | Salesforce 등 (제한적) | Salesforce, SAP 등 | 300+ 소스 |
| ** 증분 동기화**| 자동 (변경 데이터만) | 소스별 상이 | AppFlow: 지원 | 자동 |
| ** 스키마 관리**| Unity Catalog 자동 등록 | Snowflake 스키마 자동 | Glue Catalog | 자동 |
| ** 거버넌스**| Unity Catalog로 즉시 관리 | Snowflake 내부 | Lake Formation 별도 설정 | 별도 |
| ** 비용**| Databricks 컴퓨팅 비용 | Snowflake Credit | AppFlow + Glue 비용 | 별도 SaaS 라이선스 |
| ** 셋업 복잡도**| GUI에서 수 분 내 설정 | 소스별 상이 | 복잡 | 간단 (SaaS) |

{% hint style="info" %}
**Lakeflow Connect의 전략적 의미**: Fivetran, Airbyte 같은 3rd party 데이터 수집 도구를 **Databricks 네이티브로 대체** 합니다. 별도 SaaS 비용 절감 + Unity Catalog 거버넌스 자동 적용 + 단일 플랫폼 운영이라는 3가지 이점이 있습니다.
{% endhint %}

---

## 데이터 품질 관리 심층 비교

### DLT Expectations vs 경쟁사 데이터 품질

| 항목 | DLT Expectations | Snowflake Data Metric Functions | Glue Data Quality (Deequ) | Dataplex Data Quality | Great Expectations (OSS) |
|---|---|---|---|---|---|
| ** 통합 수준**| 파이프라인 내장 (코드 한 줄) | 테이블 레벨 (별도 설정) | 별도 Job 실행 | 별도 서비스 | 별도 프레임워크 |
| ** 검증 시점**| 데이터 처리 시 실시간 | 스케줄 기반 | Job 실행 시 | 스캔 스케줄 | 파이프라인에 삽입 |
| ** 위반 처리**| FAIL (파이프라인 중단) / DROP (레코드 제거) / WARN (로그만) | 알림만 | 중단 또는 로그 | 알림만 | 커스텀 핸들러 |
| ** 메트릭 수집**| 자동 (위반 건수, 비율 자동 기록) | 자동 (제한적) | 수동 | 자동 | 수동 |
| ** 대시보드**| DLT 이벤트 로그 + AI/BI Dashboard | 수동 구성 | CloudWatch | Dataplex UI | 수동 |
| **Quarantine**| DROP된 레코드를 별도 테이블에 자동 저장 | 미지원 | 수동 구현 | 미지원 | 수동 |

### Expectations 코드 예시

```sql
-- DLT에서 데이터 품질 검증 (선언적)
CREATE OR REFRESH STREAMING TABLE orders (
  CONSTRAINT valid_amount EXPECT (amount > 0) ON VIOLATION DROP ROW,
  CONSTRAINT valid_customer EXPECT (customer_id IS NOT NULL) ON VIOLATION FAIL UPDATE,
  CONSTRAINT valid_date EXPECT (order_date >= '2020-01-01') ON VIOLATION WARN
)
AS SELECT * FROM STREAM(LIVE.raw_orders);
```

위 코드 한 줄로 3가지 품질 규칙이 적용되며, 위반 레코드는 자동으로 DROP/FAIL/WARN 처리됩니다.

---

## Lakehouse Monitor — 데이터 품질 자동 모니터링

### Lakehouse Monitor vs 경쟁사

**Lakehouse Monitor** 는 Databricks만의 고유 기능으로, 테이블의 ** 프로파일링, 드리프트 감지, 이상치 알림** 을 자동 수행합니다.

| 기능 | Databricks Lakehouse Monitor | 경쟁사 |
|---|---|---|
| ** 자동 프로파일링**| 테이블 통계 자동 수집 (null 비율, 분포, 카디널리티) | 없음 (수동 쿼리 필요) |
| ** 데이터 드리프트 감지**| 시간에 따른 분포 변화 자동 감지 | 없음 (별도 도구 필요) |
| **ML 모델 모니터링**| 모델 입력/출력 데이터 품질 + 예측 드리프트 | SageMaker Monitor (별도) |
| ** 알림**| Slack, Email, PagerDuty 자동 알림 | 서비스별 상이 |
| ** 대시보드**| 자동 생성 (프로파일링 + 드리프트 + 이상치) | 수동 구성 |
| ** 설정**| SQL 한 줄로 모니터 생성 | 복잡한 설정 필요 |

```sql
-- Lakehouse Monitor 생성 (SQL 한 줄)
CREATE MONITOR catalog.schema.orders
WITH (
  GRANULARITIES = ('1 day'),
  TIME_COL = 'order_date'
);
```

{% hint style="success" %}
**SA/SE 핵심 메시지**: Databricks는 데이터 품질을 ** 파이프라인 레벨(DLT Expectations)** 과 ** 테이블 레벨(Lakehouse Monitor)** 에서 이중으로 보장합니다. 경쟁사에서는 Great Expectations, Monte Carlo, Soda 같은 ** 별도 3rd party 도구** 를 도입해야 동일한 수준의 품질 관리가 가능합니다.
{% endhint %}

---

## 오케스트레이션 비교

### 파이프라인 오케스트레이션

| 항목 | Databricks Workflows | Snowflake Tasks | AWS Step Functions + Glue | GCP Composer (Airflow) | Fabric Data Factory |
|---|---|---|---|---|---|
| ** 유형**| 네이티브 Job 오케스트레이터 | SQL 기반 Task 스케줄러 | 상태 머신 기반 | Apache Airflow 관리형 | GUI 기반 파이프라인 |
| **DAG 정의**| GUI + YAML + API | SQL (CREATE TASK) | JSON (State Machine) | Python (Airflow DAG) | GUI 드래그앤드롭 |
| ** 워크로드 통합**| SQL + Python + DLT + ML 모두 하나의 Job | SQL 전용 | AWS 서비스 연결 | 다양한 오퍼레이터 | 다양한 활동 |
| ** 오류 처리**| 자동 재시도 + 알림 + 조건부 실행 | 제한적 | Step Functions 분기 | Airflow 재시도 | 재시도 + 알림 |
| ** 모니터링**| 내장 (실행 이력, 비용, 성능) | 제한적 | CloudWatch | Airflow UI | 내장 모니터링 |
| **CI/CD**| Databricks Asset Bundles (DABs) | 수동 | CDK/CloudFormation | Terraform/Helm | ARM Templates |
| ** 비용**| 포함 (별도 비용 없음) | 포함 | Step Functions 비용 + Glue 비용 | Composer 비용 (비쌈) | 포함 |

{% hint style="info" %}
**Databricks Workflows의 핵심**: 하나의 Job에서 **DLT 파이프라인 → SQL 쿼리 → ML 학습 → 모델 배포** 까지 전체 워크플로를 오케스트레이션할 수 있습니다. 경쟁사에서는 ETL(Glue) → SQL(Redshift) → ML(SageMaker)을 Step Functions로 연결하는 복잡한 구성이 필요합니다.
{% endhint %}
