# 데이터 엔지니어링 비교

## ETL 파이프라인

| 항목 | Databricks | Snowflake | AWS Redshift/Glue | BigQuery/Dataflow | MS Fabric |
|---|---|---|---|---|---|
| **파이프라인 엔진**| Lakeflow (DLT) — 선언적 | Dynamic Tables / Snowpark | Glue (Spark 기반) | Dataflow (Apache Beam) | Data Factory + Dataflow Gen2 |
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
