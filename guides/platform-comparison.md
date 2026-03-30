# Analytics Platform 비교 가이드

> **최종 업데이트**: 2026-03 | **대상**: 플랫폼 도입/마이그레이션을 검토하는 의사결정자, 아키텍트, 데이터 엔지니어

---

## 개요

이 가이드는 **Databricks**와 주요 데이터/분석 플랫폼을 8가지 핵심 영역에서 비교합니다.

| 플랫폼 | 포지셔닝 | 핵심 접근 방식 |
|---|---|---|
| **Databricks** | Data Intelligence Platform | Lakehouse — DW + Lake + ML + GenAI 통합 |
| **Snowflake** | AI Data Cloud | SQL 분석 중심 클라우드 DW |
| **AWS Redshift** | Cloud Data Warehouse | MPP 기반 DW + S3 연동 |
| **Google BigQuery** | Serverless Analytics | 서버리스 우선 분석 엔진 |
| **Microsoft Fabric/Synapse** | Unified Analytics Platform | OneLake 기반 SaaS 통합 분석 |

{% hint style="info" %}
**핵심 메시지**: Databricks는 업계 유일하게 DW + Data Lake + ML + GenAI를 **하나의 플랫폼, 하나의 거버넌스(Unity Catalog)** 아래에서 통합합니다. 경쟁 플랫폼은 SQL 분석 또는 개별 영역에서 강점이 있지만, 전체 데이터-AI 라이프사이클을 하나로 아우르지는 못합니다.
{% endhint %}

---

## 1. 아키텍처 비교 (Lakehouse vs 전통 DW vs Lake)

### 아키텍처 패러다임

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
**Databricks 차별점**: 데이터를 **고객의 클라우드 스토리지에 오픈 포맷(Delta Lake)**으로 저장하므로, 다른 엔진(Spark, Trino, Flink 등)에서도 직접 읽을 수 있습니다. UniForm을 통해 Iceberg 호환도 자동 보장됩니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: Snowflake는 완전 관리형 SaaS로 인프라 관리 부담이 거의 없고, BigQuery는 서버리스 아키텍처로 프로비저닝 자체가 불필요합니다. MS Fabric은 Microsoft 365/Power BI와의 긴밀한 통합이 강점입니다.
{% endhint %}

### 데이터 소유권 및 개방성

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **데이터 소유권** | 고객 소유 (S3/ADLS/GCS) | 벤더 관리 스토리지 | AWS 관리형 | Google 관리형 | MS 관리형 (OneLake) |
| **포맷 잠금(Lock-in)** | Zero — 오픈 포맷 | 높음 — 독점 포맷 | 중간 | 중간-높음 | 낮음 (Delta Lake) |
| **데이터 공유 프로토콜** | Delta Sharing (오픈, 크로스 플랫폼) | Secure Data Sharing (Snowflake 내부) | Data Exchange (유료) | Analytics Hub | OneLake Sharing |
| **크로스 플랫폼 공유** | Spark, Pandas, Power BI, Tableau 등 수십 개 클라이언트 | Snowflake 계정 간만 | AWS 내부 | GCP 내부 + 제한적 외부 | MS 생태계 중심 |

---

## 2. 컴퓨팅 비교 (Serverless, Clusters, Scaling)

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **쿼리 엔진** | Photon (C++ 벡터화, 최대 12x) | 독점 MPP 엔진 | AQUA 가속 MPP | Dremel (서버리스) | Spark + Direct Lake |
| **서버리스 모드** | Serverless SQL Warehouse (즉시 시작) | 기본 서버리스 | Redshift Serverless (RPU) | On-demand / Editions | Fabric Capacity |
| **웜업 시간** | Serverless: 초 단위 | 수 초 ~ 수 분 | 분 단위 | 즉시 | 초 ~ 분 단위 |
| **자동 확장** | 지능형 자동 스케일링 + Queue 관리 | Multi-cluster Auto-scale | Concurrency Scaling (추가 비용) | Slot 기반 자동 확장 | Capacity Unit 기반 |
| **워크로드 격리** | SQL Warehouse별 독립 클러스터 | Warehouse별 격리 | WLM Queues (공유 리소스) | Reservation 기반 | Capacity 기반 분리 |
| **자동 최적화** | Predictive I/O + AI 기반 최적화 | 자동 쿼리 최적화 | Automatic WLM | 자동 최적화 | 자동 튜닝 |
| **인덱싱/클러스터링** | Liquid Clustering (자동 데이터 레이아웃) | Micro-partition Pruning | Sort Key, Distribution Key (수동) | Clustering (자동/수동) | 자동 관리 |
| **유휴 시 비용** | 자동 종료, 유휴 비용 Zero | 자동 일시중지 | Serverless: 자동, Provisioned: 과금 | On-demand: 쿼리당, Editions: 슬롯 | Capacity 단위 과금 |

{% hint style="info" %}
**Databricks Photon 엔진**: C++ 네이티브 벡터화 실행 엔진으로, TPC-DS 100TB 벤치마크에서 업계 최고 수준의 가격 대비 성능을 달성합니다. **Liquid Clustering**은 파티셔닝의 진화로, 데이터 레이아웃을 자동 최적화하여 수동 OPTIMIZE 없이 최적의 쿼리 성능을 유지합니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: BigQuery는 프로비저닝 없이 완전 서버리스로 동작하여 관리 오버헤드가 가장 낮습니다. Snowflake는 Auto-suspend/Auto-resume이 매우 직관적이며, 멀티 클러스터 자동 확장이 간단합니다.
{% endhint %}

---

## 3. 데이터 엔지니어링 비교 (ETL, 스트리밍, CDC)

### ETL 파이프라인

| 항목 | Databricks | Snowflake | AWS Redshift/Glue | BigQuery/Dataflow | MS Fabric |
|---|---|---|---|---|---|
| **파이프라인 엔진** | Lakeflow (DLT) — 선언적 | Dynamic Tables / Snowpark | Glue (Spark 기반) | Dataflow (Apache Beam) | Data Factory + Dataflow Gen2 |
| **프로그래밍 모델** | 선언적 ("무엇을" 정의하면 자동 실행) | Dynamic Tables: 선언적(SQL만), Snowpark: 명령적 | 명령적 (모든 단계를 코드로) | 명령적 (Beam Pipeline) | GUI 기반 + Spark |
| **언어 지원** | SQL + Python | SQL (Dynamic Tables), Python/Java/Scala (Snowpark) | Python, Scala (Glue) | Java, Python (Beam) | SQL + Python + GUI |
| **자동 오류 복구** | 자동 재시도, 체크포인트, idempotent 보장 | 제한적 | 수동 구현 필요 | Beam Checkpoint | 제한적 |
| **의존성 관리** | 자동 DAG 생성 및 실행 순서 결정 | Dynamic Tables: 자동 | Glue: 수동 / Step Functions | 수동 (Composer) | Data Factory 오케스트레이션 |

### 데이터 수집 및 CDC

| 항목 | Databricks | Snowflake | AWS | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **파일 수집** | Auto Loader — 증분 자동 감지, 스키마 진화 자동 | Snowpipe (파일 기반) | Glue Crawler + S3 이벤트 | Load / Transfer Service | Dataflow Gen2 |
| **스트리밍 수집** | Structured Streaming + Kafka 네이티브 | Snowpipe Streaming | Kinesis + MSK (별도 서비스) | Pub/Sub + Dataflow | Event Streams |
| **CDC** | `APPLY CHANGES` — SCD Type 1/2 자동, 코드 한 줄 | Streams + Tasks (다단계) | DMS + Glue (복잡) | Datastream (별도 서비스) | Mirroring |
| **스키마 진화** | Auto Loader 자동 스키마 감지/진화 | 수동 ALTER TABLE | Glue Crawler (주기적 스캔) | 자동 스키마 감지 | 자동 감지 |
| **배치/스트리밍 통합** | 동일 코드로 배치↔스트리밍 전환 | 별도 구현 필요 | Glue(배치) vs Kinesis(스트리밍) 분리 | Dataflow 통합 가능 (복잡) | 분리 |
| **Exactly-once** | Delta Lake 트랜잭션 보장 | At-least-once | 서비스마다 상이 | Dataflow: Exactly-once | 제한적 |
| **SaaS 커넥터** | Lakeflow Connect (Salesforce, Workday 등) | Snowflake Connectors (제한적) | Glue + AppFlow | Transfer Service | Data Factory 커넥터 |

### 데이터 품질

| 항목 | Databricks | Snowflake | AWS | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **품질 검증** | DLT Expectations (파이프라인 내장, 선언적) | Data Metric Functions | Glue Data Quality (Deequ) | Dataplex Data Quality | 제한적 |
| **위반 처리** | FAIL / DROP / WARN 선택 가능 | 알림만 | 중단 또는 로그 | 알림만 | 알림 기반 |
| **자동 모니터링** | Expectation 메트릭 자동 수집 + 대시보드 | 수동 모니터링 | CloudWatch 연동 | Dataplex 대시보드 | 제한적 |
| **Lakehouse Monitor** | 프로파일링 + 드리프트 감지 + 알림 | 미지원 | 미지원 | 미지원 | 미지원 |

{% hint style="success" %}
**Databricks Lakeflow(DLT)의 핵심**: "무엇을" 원하는지만 선언하면, 실행 계획, 오류 복구, 데이터 품질 검증, 의존성 관리를 플랫폼이 자동 처리합니다. `APPLY CHANGES`는 CDC를 코드 한 줄로 해결하며, 배치와 스트리밍도 동일한 코드로 통합됩니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: Snowflake의 Dynamic Tables는 SQL만으로 선언적 파이프라인을 구성할 수 있어 SQL 전문가에게 친숙합니다. MS Fabric의 Data Factory는 GUI 기반 파이프라인 설계로 코딩이 부담스러운 팀에게 적합합니다. BigQuery의 완전 서버리스 특성은 인프라 관리 부담을 최소화합니다.
{% endhint %}

---

## 4. SQL & Analytics 비교

### SQL 엔진 및 BI

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **ANSI SQL 호환** | 완전 호환 | 완전 호환 | PostgreSQL 호환 | GoogleSQL (일부 비표준) | T-SQL 호환 |
| **내장 BI** | AI/BI Dashboard (AI 기반 자동 시각화) | Snowsight | QuickSight | Looker + Looker Studio | Power BI (네이티브 통합) |
| **자연어 분석** | Genie Spaces + Genie Code (SQL+Python 생성/실행) | Cortex Analyst (SQL 전용) | QuickSight Q (제한적) | BigQuery NL Query (제한적) | Copilot in Power BI |
| **외부 BI 연동** | Tableau, Power BI, Looker 등 완전 호환 | 완전 호환 | 완전 호환 | 완전 호환 | Power BI 최적화, 타 BI 가능 |
| **AI 함수 in SQL** | `AI_QUERY`, `AI_GENERATE` 등 SQL 내 AI 호출 | Cortex LLM Functions | 미지원 (별도 서비스) | BigQuery ML (제한적) | 제한적 |
| **캐싱** | Delta Cache + Disk Cache + Result Cache | Result Cache + Local Disk Cache | Result Cache | BigQuery Cache (24h) | Direct Lake + 캐시 |
| **동시성** | SQL Warehouse별 독립, 자동 스케일링 | Multi-cluster Warehouse | Concurrency Scaling (추가 비용) | Slot 기반 | Capacity 기반 |
| **TPC-DS 성능** | 100TB 기준 업계 최고 수준 (Photon) | 상위권 | 상위권 | 상위권 | 상위권 |

{% hint style="info" %}
**Genie Code**: 비즈니스 사용자가 자연어로 "지난달 매출 트렌드를 분석해줘"라고 질문하면, SQL/Python 코드를 자동 생성하고 실행합니다. Cortex Analyst는 SQL만 생성하는 반면, Genie Code는 Python 분석까지 가능합니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: Snowflake는 SQL 중심 워크플로에서 가장 직관적인 사용 경험을 제공하며, Data Sharing이 매우 간편합니다. MS Fabric은 Power BI와의 네이티브 통합이 압도적이고 Direct Lake 모드로 데이터 복사 없이 대시보드를 구성합니다. BigQuery는 프로비저닝 없이 즉시 SQL을 실행할 수 있습니다.
{% endhint %}

---

## 5. ML/AI 비교 (Built-in ML, GenAI, Model Serving)

### ML 플랫폼

| 항목 | Databricks | Snowflake | AWS (SageMaker/Bedrock) | GCP (Vertex AI) | MS Fabric |
|---|---|---|---|---|---|
| **ML 플랫폼** | Mosaic AI + MLflow (End-to-End 통합) | Snowpark ML + Cortex (후발) | SageMaker (독립 서비스) | Vertex AI (독립 서비스) | Synapse ML (제한적) |
| **실험 추적** | MLflow Tracking (업계 표준 OSS, 19K+ GitHub Stars) | 자체 도구 없음 | SageMaker Experiments | Vertex AI Experiments | MLflow 연동 가능 |
| **모델 레지스트리** | Unity Catalog Models (거버넌스 통합) | Snowflake Model Registry (초기) | SageMaker Model Registry | Vertex AI Model Registry | 제한적 |
| **Feature Store** | Unity Catalog Feature Store (온라인+오프라인 통합) | 미지원 | SageMaker Feature Store | Vertex AI Feature Store | 미지원 |
| **AutoML** | Databricks AutoML (Glass-box, 코드 생성) | 미지원 | SageMaker Autopilot | Vertex AI AutoML | 제한적 |
| **데이터-ML 거버넌스** | 학습 데이터→모델→서빙 전체 리니지 (유일) | 분리 (데이터/ML 별도) | 분리 (Lake Formation↔SageMaker) | 분리 (Dataplex↔Vertex AI) | 부분적 |

### GenAI / LLM / Agent

| 항목 | Databricks | Snowflake | AWS Bedrock | GCP Vertex AI | MS Fabric |
|---|---|---|---|---|---|
| **Foundation Model API** | 다양한 모델 (DBRX, Llama, Mixtral 등) — Pay-per-token | Cortex LLM Functions (제한된 모델) | Bedrock (다양한 모델) | Gemini + 다양한 모델 | Azure OpenAI 연동 |
| **모델 파인튜닝** | Foundation Model Fine-tuning (GUI + API) | 미지원 | Bedrock Custom Model | Vertex AI Tuning | Azure OpenAI Fine-tuning |
| **자체 모델 호스팅** | GPU Model Serving — 어떤 모델이든 호스팅 | Snowpark Container Services (초기) | SageMaker Endpoints | Vertex AI Endpoints | 제한적 |
| **벡터 검색** | Vector Search — Unity Catalog 통합, Delta Sync 자동 갱신 | Cortex Search | OpenSearch / Bedrock KB (별도) | Vertex AI Vector Search (별도) | Azure AI Search 연동 |
| **RAG 구축** | Vector Search + Delta Sync + ai_parse_document() | Cortex Search (제한적) | Bedrock Knowledge Base | Vertex AI RAG | Azure AI 연동 필요 |
| **Agent 프레임워크** | Mosaic AI Agent Framework (업계 최선두) | Cortex Analyst (SQL 전용) | Bedrock Agents | Vertex AI Agent Builder | Azure AI Agent Service |
| **Agent 평가** | Agent Evaluation — 자동 품질 측정 | 미지원 | 제한적 (수동) | 제한적 (수동) | 제한적 |
| **Agent 도구 연결** | Unity Catalog Functions as Tools (거버넌스 통합) | 제한적 | Lambda Functions | Cloud Functions | Azure Functions |

{% hint style="success" %}
**Databricks AI 핵심 차별화**: 데이터가 있는 곳에서 바로 ML 학습, 모델 서빙, GenAI Agent 구축, 평가까지 수행합니다. MLflow(업계 표준 OSS)로 전 과정을 추적하고, Agent Evaluation으로 체계적 품질 측정이 가능합니다. **데이터 복사나 서비스 전환 없이 End-to-End AI를 구현하는 유일한 플랫폼**입니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: AWS Bedrock은 가장 다양한 외부 LLM 모델(Anthropic Claude, Meta Llama, Cohere 등)을 지원합니다. GCP Vertex AI는 Gemini 모델과의 긴밀한 통합, 멀티모달 AI에서 강점이 있습니다. MS Fabric은 Azure OpenAI와 네이티브 연동되어 GPT-4 계열 모델을 쉽게 활용할 수 있습니다.
{% endhint %}

---

## 6. 거버넌스 비교 (Catalog, Lineage, Sharing)

### 거버넌스 범위

| 거버넌스 대상 | Databricks Unity Catalog | Snowflake Horizon | AWS Lake Formation | GCP Dataplex | MS Purview/Fabric |
|---|---|---|---|---|---|
| **테이블 / 뷰** | 지원 | 지원 | 지원 | 지원 | 지원 |
| **ML 모델** | 지원 (모델 레지스트리 통합) | 미지원 | 미지원 (SageMaker 별도) | 미지원 (Vertex AI 별도) | 부분적 |
| **Feature Table** | 지원 (Feature Store 통합) | 미지원 | 미지원 | 미지원 | 미지원 |
| **Vector Search Index** | 지원 (벡터 인덱스도 UC 관리) | 미지원 | 미지원 | 미지원 | 미지원 |
| **AI Agent / Function** | 지원 (Agent도 UC에 등록) | 미지원 | 미지원 | 미지원 | 미지원 |
| **비정형 파일 (PDF, 이미지)** | 지원 (Volumes) | 미지원 | 미지원 | 제한적 | 부분적 |
| **External Connections** | 지원 (외부 DB 연결 관리) | 제한적 | 제한적 | 제한적 | 지원 |

### 접근 제어 및 리니지

| 항목 | Databricks | Snowflake | AWS | BigQuery/GCP | MS Fabric |
|---|---|---|---|---|---|
| **접근 제어 모델** | 3-level namespace (Catalog.Schema.Object) | Database.Schema.Object | Lake Formation TBAC / IAM | IAM + Dataplex | OneLake + Purview |
| **Row-Level Security** | Row Filter 함수 (동적) | Row Access Policy | Lake Formation Row-Level | BigQuery Row-Level | RLS in Power BI |
| **Column Masking** | Column Mask 함수 (동적) | Column Masking Policy | Lake Formation Column-Level | Policy Tags | Dynamic Data Masking |
| **Attribute-Based Access (ABAC)** | Tags 기반 동적 접근 제어 | Tag-based Masking | TBAC (Lake Formation) | Policy Tags | Sensitivity Labels |
| **자동 리니지** | 테이블→컬럼→모델→Agent 전체 추적 | Object Dependencies (테이블만) | 미지원 (별도 도구 필요) | Dataplex Lineage (제한적) | Purview Lineage |
| **컬럼 레벨 리니지** | 자동 지원 | 미지원 | 미지원 | 제한적 | 지원 |
| **ML 모델 리니지** | 학습 데이터→모델→서빙까지 추적 (유일) | 미지원 | SageMaker에서 별도 | Vertex AI에서 별도 | 부분적 |
| **감사 로그** | System Tables — SQL로 직접 분석 | Access History, Query History | CloudTrail (JSON) | Cloud Audit Logs | 통합 감사 로그 |
| **사용량 모니터링** | System Tables (Billing, Usage) — SQL 분석 | Resource Monitors | Cost Explorer + CloudWatch | Billing Export + BigQuery | 비용 관리 대시보드 |

{% hint style="success" %}
**Unity Catalog는 업계 유일의 데이터 + AI 통합 거버넌스 솔루션**입니다. 테이블, ML 모델, Feature, Vector Index, AI Agent, 비정형 파일을 하나의 카탈로그에서 통합 관리하며, 컬럼 레벨까지의 End-to-End 리니지를 자동 추적합니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: Snowflake Horizon은 SQL 중심 데이터 거버넌스에서 성숙도가 높고 Data Clean Room 기능이 강력합니다. MS Purview는 Microsoft 365 생태계 전체에 걸친 거버넌스를 제공하며, 이미 MS 환경을 사용하는 조직에 자연스럽습니다. AWS Lake Formation은 IAM 기반의 세밀한 접근 제어가 가능합니다.
{% endhint %}

---

## 7. 가격 모델 비교

### 과금 구조

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **과금 단위** | DBU (Databricks Unit) | Credit | RPU (Serverless) / 노드 시간 (Provisioned) | Slot (Editions) / 스캔 바이트 (On-demand) | CU (Capacity Unit) |
| **컴퓨팅 과금** | 초 단위 과금, 유휴 시 자동 종료 | 초 단위 (최소 60초), 자동 일시중지 | Serverless: RPU 초단위, Provisioned: 시간당 | On-demand: $6.25/TB 스캔, Editions: 슬롯 시간 | 시간당 CU 과금 |
| **스토리지 과금** | 클라우드 네이티브 가격 (S3/ADLS/GCS 직접) | Snowflake 자체 가격 (마크업 포함) | S3 + Redshift Managed Storage | $0.02/GB/월 | OneLake 스토리지 가격 |
| **서버리스 옵션** | Serverless SQL Warehouse, Serverless Compute | 기본 서버리스 | Redshift Serverless | 기본 서버리스 | Fabric Capacity |
| **유휴 비용** | Zero (자동 종료) | Zero (자동 일시중지) | Serverless: Zero, Provisioned: 과금 | On-demand: Zero, Editions: 슬롯 유지 비용 | Capacity 유지 비용 |
| **비용 투명성** | 높음 — 스토리지/컴퓨팅 완전 분리, System Tables로 분석 | 중간 — Credit 기반, 스토리지 마크업 | 중간 — 서비스별 분산 | 높음 — 쿼리당 명확 | 중간 — CU 기반 |
| **예약 할인** | 커밋 사용 할인 (1년/3년) | 선불 Capacity (할인) | Reserved Instance | Committed Use (할인) | Reserved Capacity |

### 비용 최적화 포인트

| 최적화 요소 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **스토리지 비용** | 클라우드 네이티브 가격 그대로 — 마크업 없음 | 벤더 마크업 포함 | S3 가격 + 관리 스토리지 | 자체 가격 | OneLake 가격 |
| **쿼리 최적화** | Predictive I/O, Liquid Clustering 자동 | 자동 Reclustering | 수동 Sort/Distribution Key | 자동 최적화 | Direct Lake |
| **비용 모니터링** | System Tables — 비용을 SQL로 분석/알림 | Resource Monitors | Cost Explorer | Budget Alerts | 비용 관리 대시보드 |
| **데이터 이동 비용** | 오픈 포맷 — 이관 비용 최소 | 독점 포맷 — 이관 시 높은 비용 | AWS 내부 무료, 외부 과금 | GCP 내부 무료, 외부 과금 | Azure 내부 최적화 |

{% hint style="info" %}
**Databricks 비용 투명성**: 스토리지는 고객 클라우드(S3/ADLS/GCS) 직접 과금으로 마크업이 없고, 컴퓨팅은 DBU 기반 초 단위 과금입니다. System Tables를 통해 비용을 SQL로 직접 분석하고, 이상 비용에 대한 알림을 설정할 수 있습니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 가격 강점**: BigQuery On-demand는 쿼리 실행량이 적은 경우 매우 경제적입니다 (쿼리당 과금, 유휴 비용 Zero). Snowflake는 Auto-suspend로 유휴 비용을 쉽게 관리할 수 있으며, Credit 기반 예측이 직관적입니다. MS Fabric은 이미 Microsoft E5 라이선스가 있는 조직에 추가 비용 부담이 적을 수 있습니다.
{% endhint %}

---

## 8. 플랫폼 선택 가이드 — 언제 어떤 플랫폼을 선택할 것인가

### 워크로드별 최적 플랫폼

| 워크로드 / 요구사항 | 최적 플랫폼 | 이유 |
|---|---|---|
| **데이터 + AI 통합 (ETL → ML → Agent)** | **Databricks** | 유일하게 데이터-AI 전체 라이프사이클을 하나의 플랫폼에서 통합 |
| **멀티클라우드 전략** | **Databricks** | AWS, Azure, GCP 동일 경험. Unity Catalog로 크로스 클라우드 거버넌스 |
| **벤더 종속 회피 (오픈 포맷)** | **Databricks** | Delta Lake(오픈소스) + 고객 소유 스토리지 + UniForm Iceberg 호환 |
| **GenAI Agent 구축 + 평가** | **Databricks** | Agent Framework + Agent Evaluation + 데이터 거버넌스 통합 |
| **SQL 분석 중심 (소규모 팀)** | **Snowflake** | SQL 편의성 최고, 관리 부담 최소, 빠른 온보딩 |
| **조직 간 데이터 공유** | **Snowflake** | Data Sharing / Data Clean Room이 가장 성숙 |
| **AWS 올인 전략** | **AWS Redshift** | AWS 서비스 에코시스템(S3, Kinesis, Lambda 등)과 깊은 통합 |
| **ad-hoc 쿼리 중심 (간헐적 분석)** | **BigQuery** | On-demand 모드로 쿼리당 과금, 유휴 비용 Zero |
| **서버리스 최우선** | **BigQuery** | 프로비저닝 완전 불필요, 가장 낮은 관리 오버헤드 |
| **Microsoft 생태계 (M365 + Power BI)** | **MS Fabric** | Power BI 네이티브 통합, Teams/Excel/SharePoint 연동 |
| **비개발자 셀프서비스 분석** | **Databricks** 또는 **MS Fabric** | Genie Code(자연어) / Power BI Copilot |

### 종합 역량 비교 매트릭스

| 영역 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **SQL 분석** | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★★☆ |
| **데이터 엔지니어링** | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ |
| **ML / AI** | ★★★★★ | ★★☆☆☆ | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| **GenAI / Agent** | ★★★★★ | ★★☆☆☆ | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| **거버넌스** | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ |
| **개방성 (벤더 종속 회피)** | ★★★★★ | ★★☆☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★☆☆ |
| **멀티클라우드** | ★★★★★ | ★★★★☆ | ★☆☆☆☆ | ★★☆☆☆ | ★★★☆☆ |
| **관리 편의성** | ★★★★☆ | ★★★★★ | ★★★☆☆ | ★★★★★ | ★★★★☆ |
| **BI 통합** | ★★★★☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| **비용 투명성** | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★★★☆☆ |

### 의사결정 플로우

```
질문 1: 데이터 + AI를 하나의 플랫폼에서 통합해야 하는가?
  ├─ YES → Databricks (유일한 End-to-End 통합)
  └─ NO → 질문 2로

질문 2: SQL 분석이 주 워크로드인가?
  ├─ YES → 질문 3으로
  └─ NO (ML/AI 중심) → Databricks 또는 클라우드 네이티브 ML (SageMaker/Vertex AI)

질문 3: 멀티클라우드가 필요한가?
  ├─ YES → Databricks 또는 Snowflake
  └─ NO → 질문 4로

질문 4: 어떤 클라우드를 사용하는가?
  ├─ AWS → Redshift (AWS 올인) 또는 Databricks (확장 고려)
  ├─ GCP → BigQuery (서버리스 우선) 또는 Databricks
  ├─ Azure → MS Fabric (MS 생태계) 또는 Databricks
  └─ 멀티 → Databricks 또는 Snowflake

질문 5: 벤더 종속이 우려되는가?
  ├─ YES → Databricks (오픈 포맷 + 고객 소유 스토리지)
  └─ NO → 편의성/기존 생태계 기준으로 선택
```

{% hint style="success" %}
**결론**: SQL만 필요하다면 모든 플랫폼이 경쟁력 있습니다. 하지만 **데이터와 AI를 통합**하고, **오픈 포맷으로 벤더 종속을 탈피**하며, **자연어로 누구나 접근 가능**하게 하려면 — Databricks가 현재 유일하게 이 모든 요구를 충족하는 플랫폼입니다.
{% endhint %}

---

## 부록: 개발자 경험 및 접근성

### 사용자 유형별 접근성

| 사용자 유형 | Databricks | Snowflake | AWS | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **비즈니스 사용자** | Genie Spaces + AI/BI Dashboard (자연어 OK) | Snowsight (SQL 필요) | QuickSight (설정 복잡) | Looker Studio | Power BI (직관적) |
| **SQL 분석가** | Databricks SQL + Genie Code | Snowflake SQL (직관적) | Redshift + Athena (선택 필요) | BigQuery SQL | T-SQL in Fabric |
| **데이터 엔지니어** | DLT + Notebooks + Assistant (선언적+AI 지원) | Snowpark (Python/SQL) | Glue + EMR (복잡한 설정) | Dataflow (Beam 학습 필요) | Data Factory + Dataflow Gen2 |
| **데이터 사이언티스트** | Notebooks + MLflow + AutoML (End-to-End) | Snowpark ML (제한적) | SageMaker (별도 서비스) | Vertex AI (별도 서비스) | Synapse ML (제한적) |
| **ML 엔지니어** | MLflow + Model Serving + AI Dev Kit | 미지원 | SageMaker Pipelines | Vertex AI Pipelines | 제한적 |
| **앱 개발자** | AI Dev Kit + Databricks Apps (로컬→배포) | Streamlit in Snowflake | Lambda + API Gateway | Cloud Run | Power Apps 연동 |

### AI 코딩 도구 비교

| 항목 | Databricks | Snowflake | AWS | GCP | MS Fabric |
|---|---|---|---|---|---|
| **플랫폼 내장 AI 어시스턴트** | Databricks Assistant (모든 에디터에 내장) | Snowflake Copilot | Amazon Q Developer | Gemini Code Assist | Copilot in Fabric |
| **자연어 → 코드 생성** | Genie Code (SQL + Python 생성 및 실행) | 미지원 | 미지원 | 미지원 | Copilot (제한적) |
| **로컬 IDE 통합** | AI Dev Kit (VS Code) + Databricks Connect | 제한적 IDE 지원 | AWS Toolkit | Cloud Code | VS Code 확장 |
| **로컬 Agent 개발** | AI Dev Kit — 로컬에서 Agent 개발/테스트/배포 | 미지원 | 미지원 | 미지원 | 미지원 |
| **워크스페이스 컨텍스트** | Unity Catalog 메타데이터 활용 (도메인 인식) | 스키마 인식 | 서비스별 분리 | 서비스별 분리 | Fabric 메타데이터 |

{% hint style="info" %}
**과거 Databricks의 약점으로 여겨졌던 "학습 곡선"은 Genie Code, AI Dev Kit, Databricks Assistant로 완전히 해소**되었습니다. SQL만 아는 분석가부터 Python 개발자, 비즈니스 사용자까지 — 자연어로 즉시 생산적인 작업이 가능합니다.
{% endhint %}

---

## 참고 자료

* [Databricks Platform Overview](https://docs.databricks.com/aws/en/getting-started/overview.html)
* [Databricks Lakehouse Architecture](https://docs.databricks.com/en/lakehouse/index.html)
* [Unity Catalog Documentation](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
* [Mosaic AI Agent Framework](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
* [Delta Lake Open Source](https://delta.io/)
* [MLflow Open Source](https://mlflow.org/)
