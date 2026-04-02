# Analytics Platform 비교 가이드

> **최종 업데이트**: 2026-03 | **대상**: 플랫폼 도입/마이그레이션을 검토하는 의사결정자, 아키텍트, 데이터 엔지니어

## 개요

이 가이드는 **Databricks** 와 주요 데이터/분석 플랫폼을 8가지 핵심 영역에서 비교합니다.

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

## 목차

| 페이지 | 설명 |
|--------|------|
| [아키텍처](architecture.md) | Lakehouse vs 전통 DW vs Lake, 데이터 소유권 |
| [컴퓨팅](compute.md) | Serverless, Clusters, Scaling |
| [데이터 엔지니어링](data-engineering.md) | ETL, 스트리밍, CDC, 데이터 품질 |
| [SQL & Analytics](sql-analytics.md) | SQL 엔진 및 BI |
| [ML/AI](ml-ai.md) | Built-in ML, GenAI, Model Serving, Agent |
| [거버넌스](governance.md) | Catalog, Lineage, Sharing |
| [가격 모델](pricing.md) | 과금 구조, 비용 최적화 |

## 플랫폼 선택 가이드

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
**결론**: SQL만 필요하다면 모든 플랫폼이 경쟁력 있습니다. 하지만 **데이터와 AI를 통합** 하고, **오픈 포맷으로 벤더 종속을 탈피** 하며, **자연어로 누구나 접근 가능** 하게 하려면 — Databricks가 현재 유일하게 이 모든 요구를 충족하는 플랫폼입니다.
{% endhint %}

---

## 왜 플랫폼 비교가 중요한가

### 데이터 플랫폼 선택은 5-10년 전략적 의사결정

데이터 플랫폼은 단순한 기술 도구가 아닙니다. 한번 도입하면 **데이터 파이프라인, 분석 워크플로, ML 모델, 조직 역량** 모두가 해당 플랫폼에 의존하게 됩니다. 잘못된 선택은 다음과 같은 비용을 초래합니다.

| 리스크 | 영향 | 규모 |
|---|---|---|
| **벤더 종속 (Lock-in)** | 데이터 이관 시 수개월 프로젝트 + 서비스 중단 위험 | 수억 원 ~ 수십억 원 |
| **기능 갭** | ML/AI 도입 시 별도 플랫폼 추가 → 통합 비용 폭증 | 연간 수억 원 |
| **스킬 단절** | 플랫폼별 전문 인력 확보 난이도 차이 → 채용/교육 비용 | 연간 수천만 원 |
| **확장성 한계** | 데이터 증가 시 아키텍처 재설계 필요 | 6-12개월 + 인력 투입 |
| **거버넌스 공백** | 데이터/AI가 분리된 플랫폼에서 관리될 때 규제 대응 비용 | 컴플라이언스 위반 리스크 |

{% hint style="warning" %}
**실제 사례**: 국내 대기업 A사는 Snowflake로 DW를 구축한 후 ML 워크로드가 필요해져 SageMaker를 추가 도입했습니다. 결과적으로 데이터 복사 비용(월 수천만 원), 거버넌스 이중화, 팀 간 사일로가 발생하여 2년 후 Databricks로 통합 마이그레이션을 결정했습니다.
{% endhint %}

### 각 벤더의 핵심 철학 차이

플랫폼 선택의 핵심은 **벤더의 철학과 로드맵 방향** 을 이해하는 것입니다. 각 벤더는 서로 다른 출발점에서 시작했고, 그 DNA가 제품 전략에 깊이 반영되어 있습니다.

#### Databricks — "Data + AI, Open by Default"

- **출발점**: Apache Spark 창시자들이 설립 (UC Berkeley AMPLab)
- **핵심 신념**: 데이터와 AI는 분리할 수 없다. 오픈 포맷과 오픈소스가 고객의 자유를 보장한다
- **전략 방향**: Lakehouse = DW + Lake + ML + GenAI를 **하나의 플랫폼, 하나의 거버넌스** 로 통합
- **오픈소스 기여**: Delta Lake, MLflow, Apache Spark, Unity Catalog(오픈소스화), Mosaic AI
- **강점**: 데이터-AI 전체 라이프사이클 통합, 벤더 종속 최소화, 멀티클라우드
- **약점(과거)**: SQL 분석 편의성 — Genie Code, DBSQL Serverless로 대폭 개선됨

#### Snowflake — "Data Cloud, SQL-First"

- **출발점**: Oracle 출신 엔지니어들이 클라우드 네이티브 DW를 재발명
- **핵심 신념**: SQL이 데이터의 공용어다. 관리 부담 Zero가 핵심 가치
- **전략 방향**: SQL 분석 중심에서 Snowpark(Python), Cortex(AI)로 확장 중
- **강점**: SQL 사용 편의성 최고, Data Sharing/Clean Room 성숙도, 빠른 온보딩
- **약점**: ML/AI는 후발, 독점 포맷으로 벤더 종속 높음, 컴퓨팅 비용 예측 어려움

#### AWS Redshift — "AWS 생태계의 핵심 DW"

- **출발점**: ParAccel(PostgreSQL 기반 MPP) 인수로 시작
- **핵심 신념**: AWS 서비스 에코시스템과의 깊은 통합이 가치
- **전략 방향**: Redshift Serverless + S3 Auto-copy + AQUA 가속
- **강점**: AWS 서비스(S3, Kinesis, Lambda, Glue)와 완벽 통합, PostgreSQL 호환
- **약점**: AWS 단일 클라우드 종속, ML은 SageMaker로 분리, 관리 복잡도 높음

#### Google BigQuery — "Serverless Analytics, Zero Management"

- **출발점**: Google 내부 Dremel 엔진의 상용화
- **핵심 신념**: 서버리스가 기본이다. 인프라 관리는 사용자의 일이 아니다
- **전략 방향**: BigQuery + Vertex AI + Gemini 통합, BigLake로 오픈 포맷 지원 확대
- **강점**: 완전 서버리스, 쿼리당 과금(On-demand), 관리 오버헤드 최소
- **약점**: GCP 종속, 독점 포맷, ML은 Vertex AI로 분리, 국내 GCP 점유율 낮음

#### Microsoft Fabric — "Microsoft 365 + Power BI 중심 통합"

- **출발점**: Azure Synapse + Power BI + Data Factory를 하나로 통합(2023)
- **핵심 신념**: 이미 Microsoft 생태계에 있는 조직에게 자연스러운 통합을 제공
- **전략 방향**: OneLake(ADLS 기반) + Copilot(AI) + Power BI 네이티브 통합
- **강점**: Power BI 최고 수준 통합, M365/Teams 연동, Copilot AI
- **약점**: 아직 성숙도 초기(2023 GA), ML/AI 역량 부족, Azure 종속

### 기업 의사결정 프레임워크

플랫폼 선택 시 다음 **6가지 축** 을 기준으로 평가하는 것을 권장합니다.

#### 1단계: 전략적 요구사항 평가

| 평가 축 | 핵심 질문 | 가중치(예시) |
|---|---|---|
| **워크로드 범위** | SQL만? ETL+SQL? ML/AI까지? GenAI Agent까지? | 25% |
| **클라우드 전략** | 단일 클라우드? 멀티클라우드? 하이브리드? | 15% |
| **벤더 종속 허용도** | 오픈 포맷 필수? 이관 가능성 고려? | 15% |
| **팀 역량** | SQL만 가능? Python 가능? ML 전문가 있음? | 15% |
| **TCO (총소유비용)** | 초기 비용? 3년 TCO? 숨은 비용(이관, 학습)? | 20% |
| **생태계 통합** | 기존 BI 도구? 클라우드 서비스? 사내 시스템? | 10% |

#### 2단계: 스코어카드 작성

각 평가 축에 대해 후보 플랫폼을 1-5점으로 채점하고, 가중 합산으로 최종 순위를 도출합니다.

```
예시: 데이터+AI 통합이 핵심인 금융사

                    Databricks  Snowflake  Redshift  BigQuery  Fabric
워크로드 범위(25%)      5×0.25     3×0.25    3×0.25   3×0.25   3×0.25
클라우드 전략(15%)      5×0.15     4×0.15    2×0.15   2×0.15   3×0.15
벤더 종속(15%)         5×0.15     2×0.15    3×0.15   2×0.15   3×0.15
팀 역량(15%)           4×0.15     5×0.15    3×0.15   4×0.15   4×0.15
TCO(20%)              4×0.20     3×0.20    3×0.20   4×0.20   3×0.20
생태계 통합(10%)       4×0.10     4×0.10    4×0.10   3×0.10   5×0.10
────────────────────────────────────────────────────────────────────
가중 합산              4.55       3.30      2.90     3.05     3.30
```

#### 3단계: PoC (Proof of Concept) 실행

스코어카드 상위 2개 플랫폼에 대해 **2-4주 PoC** 를 실행합니다.

| PoC 항목 | 평가 기준 |
|---|---|
| **데이터 수집** | Auto Loader vs Snowpipe — 설정 시간, 스키마 진화 대응 |
| **ETL 파이프라인** | DLT vs Dynamic Tables — 복잡도, 오류 처리, CDC |
| **SQL 쿼리 성능** | 동일 쿼리 세트로 응답 시간/비용 비교 |
| **ML 워크플로** | 학습→등록→서빙 전체 과정의 복잡도와 소요 시간 |
| **거버넌스** | 접근 제어 설정, 리니지 확인, 감사 로그 |
| **비용** | 동일 워크로드에 대한 실제 청구 비용 비교 |

### 산업별 플랫폼 선택 트렌드

| 산업 | 주요 요구사항 | 권장 플랫폼 | 이유 |
|---|---|---|---|
| **금융 (은행/보험)** | 규제 준수, AI 리스크 관리, 멀티클라우드 | **Databricks** | Unity Catalog 거버넌스 + Agent Evaluation + 멀티클라우드 |
| **제조** | 예지보전, IoT 스트리밍, MLOps | **Databricks** | Structured Streaming + MLflow + Feature Store 통합 |
| **리테일/이커머스** | 실시간 추천, 고객 360, 빠른 분석 | **Databricks** 또는 **Snowflake** | AI 중심이면 Databricks, SQL 분석 중심이면 Snowflake |
| **게임** | 실시간 이벤트 분석, 서버리스 | **BigQuery** 또는 **Databricks** | ad-hoc 분석이면 BigQuery, ML 파이프라인이면 Databricks |
| **공공/헬스케어** | 데이터 주권, 규제, 감사 | **Databricks** 또는 **Redshift** | 멀티클라우드면 Databricks, AWS 전용이면 Redshift |
| **미디어/광고** | 대규모 로그 분석, 실시간 타겟팅 | **Databricks** | Delta Lake 대규모 데이터 처리 + Structured Streaming |
| **MS 중심 기업** | M365, Teams, SharePoint 통합 | **MS Fabric** | Power BI 네이티브 + Copilot + M365 연동 |

### 마이그레이션 고려사항

기존 플랫폼에서 Databricks로 마이그레이션을 고려하는 경우.

| 원천 플랫폼 | 마이그레이션 난이도 | 핵심 고려사항 |
|---|---|---|
| **Snowflake → Databricks** | 중간 | 독점 포맷 UNLOAD 필요, SQL 호환성 높음, Snowpark → PySpark 전환 |
| **Redshift → Databricks** | 중간-낮음 | S3 데이터는 그대로 활용, PostgreSQL SQL은 대부분 호환 |
| **BigQuery → Databricks** | 중간 | BigQuery Export → GCS → Delta Lake, GoogleSQL 차이 주의 |
| **Hadoop/Spark → Databricks** | 낮음 | Spark 코드 거의 그대로 실행, Hive 메타스토어 마이그레이션 |
| **MS Fabric → Databricks** | 중간 | OneLake(Delta) 포맷 호환, Power BI 연동은 DBSQL로 대체 |

{% hint style="info" %}
**Databricks Lakeflow Connect** 를 활용하면 기존 플랫폼의 데이터를 증분 방식으로 Databricks Lakehouse에 동기화할 수 있어, 빅뱅 마이그레이션 없이 점진적 전환이 가능합니다.
{% endhint %}

---

## Databricks의 최근 주요 혁신 (2025-2026)

SA/SE가 경쟁 상황에서 언급해야 할 Databricks의 최근 핵심 발표.

| 시기 | 혁신 | 경쟁 영향 |
|---|---|---|
| **2025 Q1** | **Lakeflow Connect GA**— SaaS 데이터 수집 자동화 | Snowflake Connectors, Fivetran 대체 가능 |
| **2025 Q1** | **Agent Framework + Evaluation GA** | Bedrock Agents, Vertex AI Agent 대비 평가 체계 우위 |
| **2025 Q2** | **Genie Code GA**— 자연어→SQL+Python 실행 | Cortex Analyst(SQL만) 대비 Python 분석까지 가능 |
| **2025 Q2** | **Unity Catalog 오픈소스화** | 업계 유일 오픈소스 통합 거버넌스 |
| **2025 Q3** | **Serverless Compute for All**— 모든 워크로드 서버리스 | BigQuery 수준의 서버리스 경험 달성 |
| **2025 Q4** | **AI/BI Dashboard GA**— AI 기반 자동 시각화 | Power BI Copilot, Looker 대비 데이터 플랫폼 내장 BI |
| **2026 Q1** | **Lakebase GA**— 트랜잭셔널 데이터베이스 | RDS/Aurora 워크로드까지 Lakehouse로 통합 |
| **2026 Q1** | **AI Dev Kit GA**— 로컬 Agent 개발/테스트/배포 | 개발자 경험 혁신, VS Code 네이티브 통합 |

---

## 경쟁 PT/미팅 시 핵심 메시지

### 3가지 킬러 메시지

1. **"하나의 플랫폼, 하나의 거버넌스" **— ETL, SQL, ML, GenAI를 Unity Catalog 아래 통합하는 유일한 플랫폼. 경쟁사는 최소 2-3개 서비스를 조합해야 합니다.

2. **"오픈 포맷, 고객 소유 데이터" **— Delta Lake(오픈소스) + 고객 클라우드 스토리지에 저장. 벤더 종속 Zero. Snowflake는 독점 포맷에 벤더 관리 스토리지입니다.

3. **"데이터가 있는 곳에서 바로 AI" **— 데이터 복사 없이 같은 플랫폼에서 ML 학습→서빙→Agent 구축→평가. SageMaker/Vertex AI는 데이터를 복사해야 합니다.

### 경쟁사별 핵심 반박 포인트

| 경쟁사 주장 | Databricks 반박 |
|---|---|
| "Snowflake가 SQL 분석에서 더 낫다" | DBSQL Photon 엔진은 TPC-DS 100TB에서 업계 최고 성능. Genie Code로 자연어 분석까지 가능 |
| "BigQuery는 관리할 것이 없다" | Databricks Serverless도 프로비저닝 불필요. 추가로 ML/AI까지 통합 |
| "Redshift는 AWS 생태계와 완벽 통합" | Databricks도 AWS 네이티브(S3, IAM, PrivateLink). 추가로 멀티클라우드와 오픈 포맷 제공 |
| "Fabric은 Power BI와 통합된다" | Databricks도 Power BI Direct Lake 모드 지원. 추가로 ML/AI와 오픈 거버넌스 제공 |
| "Databricks는 비싸다" | 스토리지 마크업 Zero + Serverless 자동 종료. 3년 TCO 기준 경쟁력 우위 (System Tables로 증명 가능) |

---

## 참고 자료

* [Databricks Platform Overview](https://docs.databricks.com/aws/en/getting-started/overview.html)
* [Databricks Lakehouse Architecture](https://docs.databricks.com/en/lakehouse/index.html)
* [Unity Catalog Documentation](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
* [Mosaic AI Agent Framework](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
* [Delta Lake Open Source](https://delta.io/)
* [MLflow Open Source](https://mlflow.org/)
* [Databricks vs Snowflake — Lakehouse vs Data Cloud](https://www.databricks.com/compare/databricks-vs-snowflake)
* [TPC-DS Benchmark Results](https://www.databricks.com/blog/2021/11/02/databricks-sets-official-data-warehousing-performance-record.html)
* [Gartner Magic Quadrant for Cloud Database Management Systems](https://www.gartner.com/reviews/market/cloud-database-management-systems)
* [Forrester Wave: Cloud Data Platforms](https://www.forrester.com/report/the-forrester-wave-cloud-data-platforms)
