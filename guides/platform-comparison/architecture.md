# 아키텍처 비교

## 아키텍처 패러다임

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric/Synapse |
|---|---|---|---|---|---|
| **아키텍처 유형** | Lakehouse | Cloud DW | Cloud DW (MPP) | Serverless DW | Lakehouse (OneLake) |
| **스토리지 포맷** | Delta Lake (오픈소스, Linux Foundation) | 독점 포맷 (Iceberg 전환 중) | 독점 + S3 외부 테이블 | BigQuery Storage (독점) + BigLake | Delta Lake (OneLake) |
| **컴퓨팅-스토리지 분리** | 완전 분리 | 분리 (내부적) | RA3: 분리, DC: 결합 | 완전 분리 | 분리 (OneLake) |
| **데이터 저장 위치** | 고객 클라우드 스토리지 (S3/ADLS/GCS) | Snowflake 관리형 스토리지 | AWS 관리형 + S3 | Google 관리형 | OneLake (ADLS 기반) |
| **오픈 포맷** | Delta Lake + UniForm(Iceberg 호환) | Iceberg 전환 중 (독점 우선) | Iceberg/Hudi 외부 지원 | BigLake로 제한적 지원 | Delta Lake |
| **멀티클라우드** | AWS, Azure, GCP 동일 경험 | AWS, Azure, GCP 지원 | AWS Only | GCP Only (Omni 제한적) | Azure 중심 (일부 멀티클라우드) |
| **벤더 종속 리스크** | 최소 (오픈 포맷 + 고객 소유 스토리지) | 높음 (독점 포맷, 이관 시 COPY 필요) | 중간 (AWS 종속) | 중간-높음 (GCP 종속 + 독점 포맷) | 중간 (Azure/MS 생태계 종속) |

{% hint style="success" %}
**Databricks 차별점**: 데이터를 **고객의 클라우드 스토리지에 오픈 포맷(Delta Lake)** 으로 저장하므로, 다른 엔진(Spark, Trino, Flink 등)에서도 직접 읽을 수 있습니다. UniForm을 통해 Iceberg 호환도 자동 보장됩니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: Snowflake는 완전 관리형 SaaS로 인프라 관리 부담이 거의 없고, BigQuery는 서버리스 아키텍처로 프로비저닝 자체가 불필요합니다. MS Fabric은 Microsoft 365/Power BI와의 긴밀한 통합이 강점입니다.
{% endhint %}

## 데이터 소유권 및 개방성

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **데이터 소유권** | 고객 소유 (S3/ADLS/GCS) | 벤더 관리 스토리지 | AWS 관리형 | Google 관리형 | MS 관리형 (OneLake) |
| **포맷 잠금(Lock-in)** | Zero — 오픈 포맷 | 높음 — 독점 포맷 | 중간 | 중간-높음 | 낮음 (Delta Lake) |
| **데이터 공유 프로토콜** | Delta Sharing (오픈, 크로스 플랫폼) | Secure Data Sharing (Snowflake 내부) | Data Exchange (유료) | Analytics Hub | OneLake Sharing |
| **크로스 플랫폼 공유** | Spark, Pandas, Power BI, Tableau 등 수십 개 클라이언트 | Snowflake 계정 간만 | AWS 내부 | GCP 내부 + 제한적 외부 | MS 생태계 중심 |

---

## Lakehouse vs Data Warehouse — 아키텍처 근본 차이

### 전통적 데이터 아키텍처의 한계

기존 데이터 아키텍처는 **Data Lake** 와 **Data Warehouse** 를 별도로 운영하는 **Two-tier 아키텍처** 였습니다.

| 계층 | 역할 | 기술 | 문제점 |
|---|---|---|---|
| **Data Lake (1계층)** | 원천 데이터 저장 (정형+비정형) | S3/ADLS + Parquet/JSON | ACID 미보장, 품질 관리 불가, "Data Swamp" 화 |
| **Data Warehouse (2계층)** | 정제 데이터 분석 | Snowflake/Redshift/BigQuery | 데이터 복사 비용, 비정형 미지원, ML 불가 |

**문제의 핵심**: 데이터를 Lake에서 Warehouse로 **복사** 해야 하므로, ETL 비용 증가 + 데이터 일관성 문제 + 거버넌스 이중화가 발생합니다.

### Lakehouse 아키텍처 — 하나로 통합

**Lakehouse** 는 Data Lake의 유연성과 Data Warehouse의 성능/ACID를 **하나의 아키텍처** 로 통합합니다.

| 특성 | Data Lake | Data Warehouse | **Lakehouse** |
|---|---|---|---|
| **ACID 트랜잭션** | 미지원 | 지원 | **지원 (Delta Lake)** |
| **스키마 강제** | 미지원 (Schema-on-Read) | 지원 (Schema-on-Write) | **둘 다 지원** |
| **비정형 데이터** | 지원 | 미지원 | **지원 (Volumes)** |
| **ML/AI 워크로드** | 가능하지만 품질 문제 | 미지원 (데이터 반출 필요) | **네이티브 지원** |
| **SQL 분석** | 느리고 불안정 | 최적화됨 | **Photon 엔진으로 최적화** |
| **실시간 스트리밍** | 가능하지만 복잡 | 제한적 | **Structured Streaming 통합** |
| **비용** | 저렴 (오브젝트 스토리지) | 비쌈 (전용 스토리지) | **저렴 (오브젝트 스토리지 직접)** |
| **거버넌스** | 별도 도구 필요 | 내장 (제한적) | **Unity Catalog 통합** |

{% hint style="info" %}
**Lakehouse의 핵심 혁신**: Delta Lake가 오브젝트 스토리지(S3/ADLS/GCS) 위에 **ACID 트랜잭션, 스키마 강제, 타임 트래블, 인덱싱** 을 추가하여, 저렴한 클라우드 스토리지에서 DW급 성능과 신뢰성을 달성했습니다.
{% endhint %}

---

## Delta Lake vs Iceberg vs Hudi — 오픈 테이블 포맷 비교

| 항목 | Delta Lake | Apache Iceberg | Apache Hudi |
|---|---|---|---|
| **개발 주체** | Databricks (Linux Foundation 기증) | Netflix → Apache | Uber → Apache |
| **커뮤니티 규모** | GitHub Stars 7.5K+, 기업 채택 최다 | GitHub Stars 6K+, 빠른 성장 | GitHub Stars 5K+, Uber 중심 |
| **ACID 트랜잭션** | 지원 (트랜잭션 로그 기반) | 지원 (스냅샷 기반) | 지원 (타임라인 기반) |
| **타임 트래블** | 지원 (버전 기반, SQL로 조회) | 지원 (스냅샷 기반) | 지원 (타임라인 기반) |
| **스키마 진화** | 완전 지원 (추가/삭제/변경) | 완전 지원 | 제한적 지원 |
| **파티션 진화** | Liquid Clustering (자동) | Hidden Partitioning (자동) | 수동 파티셔닝 |
| **스트리밍 지원** | Structured Streaming 네이티브 | Flink 통합 | Flink/Spark 통합 |
| **DML 성능 (UPDATE/DELETE/MERGE)** | 매우 높음 (Copy-on-Write + Merge-on-Read) | 높음 (Copy-on-Write + Merge-on-Read) | 높음 (Merge-on-Read 특화) |
| **CDC 지원** | `APPLY CHANGES` (DLT 내장) | 외부 도구 필요 | 네이티브 CDC 지원 |
| **엔진 호환성** | Spark, Flink, Trino, Presto, Hive + **UniForm** | Spark, Flink, Trino, Presto, Dremio | Spark, Flink, Presto, Hive |
| **Unity Catalog 통합** | 네이티브 | UniForm으로 호환 | 외부 카탈로그 필요 |

### UniForm — 포맷 간 호환성 문제 해결

**Databricks UniForm** 은 Delta Lake 테이블을 **Iceberg 및 Hudi 형식으로 자동 노출** 합니다. 데이터는 Delta Lake로 한 번만 저장하고, 다른 엔진에서는 Iceberg/Hudi로 읽을 수 있습니다.

```
Delta Lake 테이블 (원본)
  ├─ Spark/Databricks → Delta Lake 프로토콜로 직접 읽기
  ├─ Trino/Snowflake  → Iceberg 프로토콜로 읽기 (UniForm 자동 변환)
  └─ 기타 엔진        → Hudi 프로토콜로 읽기 (UniForm 자동 변환)
```

{% hint style="success" %}
**UniForm의 전략적 의미**: 고객은 Delta Lake를 선택하면서도 Iceberg 생태계 도구를 자유롭게 활용할 수 있습니다. "어떤 포맷을 선택해야 하나?"라는 질문 자체가 불필요해집니다. 이것이 **오픈 포맷 전략의 완성** 입니다.
{% endhint %}

---

## 컴퓨팅-스토리지 분리 아키텍처 상세

### 각 플랫폼의 분리 수준

| 플랫폼 | 스토리지 계층 | 컴퓨팅 계층 | 분리 수준 | 독립 확장 |
|---|---|---|---|---|
| **Databricks** | 고객 소유 S3/ADLS/GCS | SQL Warehouse, Cluster, Serverless | **완전 분리** | 스토리지/컴퓨팅 독립 확장 |
| **Snowflake** | Snowflake 관리형 S3/Azure Blob/GCS | Virtual Warehouse (독립 컴퓨팅) | **논리적 분리** | 컴퓨팅 독립 확장, 스토리지는 벤더 관리 |
| **Redshift RA3** | Redshift Managed Storage (S3 기반) | RA3 노드 | **부분 분리** | RA3에서만 분리, DC는 결합형 |
| **BigQuery** | Capacitor 컬럼 포맷 (Google 관리) | Dremel 서버리스 엔진 | **완전 분리** | 사용자 개입 없이 자동 |
| **MS Fabric** | OneLake (ADLS Gen2 기반) | Spark, SQL Endpoint | **분리** | Capacity Unit 기반 |

### 분리 아키텍처가 중요한 이유

| 이점 | 설명 |
|---|---|
| **비용 독립성** | 스토리지 1PB + 컴퓨팅 소규모 → 저렴. 결합형은 1PB 저장 시 컴퓨팅도 함께 확장 |
| **워크로드 격리** | ETL, SQL 분석, ML 학습이 서로 다른 컴퓨팅을 사용 → 상호 영향 Zero |
| **탄력적 확장** | 월말 보고서 시 컴퓨팅만 일시 확장 → 비용 최적화 |
| **데이터 공유** | 하나의 스토리지를 여러 컴퓨팅 엔진이 공유 → 데이터 복사 불필요 |

{% hint style="info" %}
**Databricks만의 차별점**: 스토리지가 **고객 소유 클라우드 계정** 에 있으므로, Databricks 계약 종료 후에도 데이터를 100% 보유합니다. Snowflake는 벤더 관리 스토리지이므로, 이관 시 별도 COPY 작업이 필요합니다.
{% endhint %}

---

## 카탈로그 및 메타데이터 관리 아키텍처

### Unity Catalog vs 경쟁사 카탈로그

| 항목 | Unity Catalog | Snowflake Catalog | AWS Glue Catalog / Lake Formation | BigQuery Catalog | MS Purview |
|---|---|---|---|---|---|
| **범위** | 테이블+뷰+모델+Feature+Vector+Agent+Volume | 테이블+뷰+스테이지 | 테이블+뷰 (Glue) | 테이블+뷰+모델(BQML) | 테이블+뷰+파이프라인 |
| **3-level namespace** | Catalog.Schema.Object | Database.Schema.Object | Database.Table | Project.Dataset.Table | Collection.Asset |
| **크로스 워크스페이스** | 하나의 메타스토어로 여러 워크스페이스 통합 | 계정 내 공유 | 계정 내 공유 | 프로젝트 내 | 테넌트 내 |
| **멀티클라우드 카탈로그** | AWS+Azure+GCP 동일 카탈로그 | 리전별 분리 (Replication 필요) | AWS Only | GCP Only | Azure 중심 |
| **오픈소스** | **오픈소스화 완료 (2025)** | 비공개 | 비공개 | 비공개 | 비공개 |
| **외부 엔진 호환** | Spark, Trino, Flink, dbt 등 | Snowflake Only | AWS 서비스 | GCP 서비스 | Azure 서비스 |

### 메타데이터 아키텍처 차이

```
[Databricks Unity Catalog]
  ├─ 중앙 메타스토어 (Account 레벨)
  │   ├─ Catalog A (프로덕션)
  │   │   ├─ Schema: sales → Tables, Views, Functions
  │   │   ├─ Schema: ml_models → Models, Feature Tables
  │   │   └─ Schema: genai → Vector Indexes, Agents
  │   ├─ Catalog B (개발)
  │   └─ Catalog C (외부 공유용)
  ├─ 접근 제어 (GRANT/REVOKE, Row Filter, Column Mask)
  ├─ 리니지 (테이블→컬럼→모델→Agent 자동 추적)
  └─ 감사 로그 (System Tables — SQL로 분석)

[Snowflake]
  ├─ Account 내 Database들
  │   ├─ Database A → Schema → Tables/Views
  │   └─ (모델, Feature, Vector는 별도 관리 또는 미지원)
  ├─ 접근 제어 (GRANT/REVOKE, Masking Policy)
  └─ 리니지 (Object Dependencies, 테이블 레벨만)

[AWS]
  ├─ Glue Data Catalog (테이블 메타데이터)
  ├─ Lake Formation (접근 제어)
  ├─ SageMaker (모델 레지스트리 — 별도)
  └─ CloudTrail (감사 — JSON 로그, 분석 어려움)
```

---

## 각 플랫폼의 기술 스택 상세 비교

### 전체 기술 스택 매핑

| 기능 영역 | Databricks | Snowflake | AWS 조합 | GCP 조합 | MS Fabric/Azure 조합 |
|---|---|---|---|---|---|
| **오브젝트 스토리지** | 고객 S3/ADLS/GCS | Snowflake 관리형 | S3 | GCS | OneLake (ADLS) |
| **테이블 포맷** | Delta Lake + UniForm | 독점 (Iceberg 전환 중) | Parquet/Iceberg | Capacitor (독점) | Delta Lake |
| **SQL 엔진** | Photon (C++ 벡터화) | 독점 MPP 엔진 | Redshift (PostgreSQL 기반) | Dremel | Spark SQL + Direct Lake |
| **ETL 엔진** | Lakeflow (DLT) + Spark | Dynamic Tables + Snowpark | Glue (Spark) + Step Functions | Dataflow (Beam) | Data Factory + Dataflow Gen2 |
| **스트리밍** | Structured Streaming | Snowpipe Streaming | Kinesis + MSK | Pub/Sub + Dataflow | Event Streams |
| **ML 플랫폼** | Mosaic AI + MLflow | Snowpark ML + Cortex | SageMaker | Vertex AI | Synapse ML |
| **GenAI** | Foundation Model APIs + Agent Framework | Cortex LLM Functions | Bedrock | Gemini + Vertex AI | Azure OpenAI |
| **벡터 검색** | Vector Search (UC 통합) | Cortex Search | OpenSearch / Bedrock KB | Vertex AI Vector Search | Azure AI Search |
| **카탈로그** | Unity Catalog | Snowflake Catalog | Glue Catalog + Lake Formation | Dataplex | Purview |
| **BI** | AI/BI Dashboard | Snowsight | QuickSight | Looker / Looker Studio | Power BI |
| **자연어 분석** | Genie Spaces + Genie Code | Cortex Analyst | QuickSight Q | BQ NL Query | Copilot in Power BI |
| **데이터 공유** | Delta Sharing (오픈 프로토콜) | Secure Data Sharing | Data Exchange | Analytics Hub | OneLake Sharing |
| **앱 개발** | Databricks Apps + AI Dev Kit | Streamlit in Snowflake | Lambda + API Gateway | Cloud Run | Power Apps |
| **감사/모니터링** | System Tables (SQL 분석) | Access History | CloudTrail + CloudWatch | Cloud Audit Logs | 통합 감사 로그 |

### 기술 스택 관점에서의 핵심 차이

**통합 vs 조합** 이 가장 중요한 차이입니다.

| 관점 | Databricks | 경쟁사 |
|---|---|---|
| **서비스 수** | 1개 플랫폼 | Snowflake: 1개(SQL)+α / AWS: 5-10개 서비스 조합 / GCP: 3-5개 조합 |
| **거버넌스** | 1개 카탈로그 (Unity Catalog) | 서비스마다 별도 거버넌스 또는 외부 도구 |
| **리니지** | 자동, End-to-End | 서비스 경계에서 단절 |
| **사용자 경험** | 하나의 워크스페이스 | 서비스마다 다른 UI/UX |
| **비용 추적** | System Tables 하나로 전체 분석 | 서비스별 별도 비용 모니터링 |

{% hint style="success" %}
**SA/SE 핵심 메시지**: "Databricks는 하나의 플랫폼에서 데이터 수집→ETL→SQL 분석→ML→GenAI→거버넌스를 모두 수행합니다. AWS에서 동일한 구성을 하려면 S3 + Glue + Redshift + SageMaker + Bedrock + Lake Formation + CloudTrail을 조합해야 하며, 각 서비스 간 데이터 복사와 거버넌스 이중화가 불가피합니다."
{% endhint %}

---

## 멀티클라우드 아키텍처 상세

### 멀티클라우드 지원 수준

| 항목 | Databricks | Snowflake | Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **지원 클라우드** | AWS, Azure, GCP | AWS, Azure, GCP | AWS Only | GCP Only (BigQuery Omni 제한적) | Azure 중심 |
| **동일 기능 경험** | 3개 클라우드 동일 기능 | 대부분 동일 (일부 기능 차이) | N/A | Omni는 제한된 기능만 | Azure 최적화 |
| **크로스 클라우드 거버넌스** | Unity Catalog 하나로 통합 관리 | 리전별 계정 분리, Replication 필요 | N/A | N/A | Azure 중심 |
| **크로스 클라우드 데이터 공유** | Delta Sharing (클라우드 무관) | Data Sharing (Snowflake 계정 간) | N/A | Analytics Hub (GCP 내) | 제한적 |
| **크로스 클라우드 DR** | Active-Active 가능 | Replication 기반 | N/A | N/A | Azure Paired Region |

{% hint style="info" %}
**멀티클라우드가 중요한 이유**: M&A로 인한 클라우드 혼용, 리전별 규제(데이터 주권), 벤더 협상력 확보, DR/BCP 구성 등 다양한 이유로 멀티클라우드 전략을 채택하는 기업이 증가하고 있습니다. Databricks는 이 시나리오에서 **유일하게 일관된 경험** 을 제공합니다.
{% endhint %}
