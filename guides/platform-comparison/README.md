# Analytics Platform 비교 가이드

> **최종 업데이트**: 2026-03 | **대상**: 플랫폼 도입/마이그레이션을 검토하는 의사결정자, 아키텍트, 데이터 엔지니어

## 개요

이 가이드는 **Databricks** 와 주요 데이터/분석 플랫폼을 8가지 핵심 영역에서 비교합니다.

| 플랫폼 | 포지셔닝 | 핵심 접근 방식 |
|---|---|---|
| **Databricks**| Data Intelligence Platform | Lakehouse — DW + Lake + ML + GenAI 통합 |
| **Snowflake**| AI Data Cloud | SQL 분석 중심 클라우드 DW |
| **AWS Redshift**| Cloud Data Warehouse | MPP 기반 DW + S3 연동 |
| **Google BigQuery**| Serverless Analytics | 서버리스 우선 분석 엔진 |
| **Microsoft Fabric/Synapse**| Unified Analytics Platform | OneLake 기반 SaaS 통합 분석 |

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
| **데이터 + AI 통합 (ETL → ML → Agent)**| **Databricks**| 유일하게 데이터-AI 전체 라이프사이클을 하나의 플랫폼에서 통합 |
| **멀티클라우드 전략**| **Databricks**| AWS, Azure, GCP 동일 경험. Unity Catalog로 크로스 클라우드 거버넌스 |
| **벤더 종속 회피 (오픈 포맷)**| **Databricks**| Delta Lake(오픈소스) + 고객 소유 스토리지 + UniForm Iceberg 호환 |
| **GenAI Agent 구축 + 평가**| **Databricks**| Agent Framework + Agent Evaluation + 데이터 거버넌스 통합 |
| **SQL 분석 중심 (소규모 팀)**| **Snowflake**| SQL 편의성 최고, 관리 부담 최소, 빠른 온보딩 |
| **조직 간 데이터 공유**| **Snowflake**| Data Sharing / Data Clean Room이 가장 성숙 |
| **AWS 올인 전략**| **AWS Redshift**| AWS 서비스 에코시스템(S3, Kinesis, Lambda 등)과 깊은 통합 |
| **ad-hoc 쿼리 중심 (간헐적 분석)**| **BigQuery**| On-demand 모드로 쿼리당 과금, 유휴 비용 Zero |
| **서버리스 최우선**| **BigQuery**| 프로비저닝 완전 불필요, 가장 낮은 관리 오버헤드 |
| **Microsoft 생태계 (M365 + Power BI)**| **MS Fabric**| Power BI 네이티브 통합, Teams/Excel/SharePoint 연동 |
| **비개발자 셀프서비스 분석**| **Databricks**또는 **MS Fabric**| Genie Code(자연어) / Power BI Copilot |

### 종합 역량 비교 매트릭스

| 영역 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **SQL 분석**| ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★★☆ |
| **데이터 엔지니어링**| ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ |
| **ML / AI**| ★★★★★ | ★★☆☆☆ | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| **GenAI / Agent**| ★★★★★ | ★★☆☆☆ | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| **거버넌스**| ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ |
| **개방성 (벤더 종속 회피)**| ★★★★★ | ★★☆☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★☆☆ |
| **멀티클라우드**| ★★★★★ | ★★★★☆ | ★☆☆☆☆ | ★★☆☆☆ | ★★★☆☆ |
| **관리 편의성**| ★★★★☆ | ★★★★★ | ★★★☆☆ | ★★★★★ | ★★★★☆ |
| **BI 통합**| ★★★★☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| **비용 투명성**| ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★★★☆☆ |

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
**결론**: SQL만 필요하다면 모든 플랫폼이 경쟁력 있습니다. 하지만 **데이터와 AI를 통합**하고, **오픈 포맷으로 벤더 종속을 탈피**하며, **자연어로 누구나 접근 가능** 하게 하려면 — Databricks가 현재 유일하게 이 모든 요구를 충족하는 플랫폼입니다.
{% endhint %}

## 참고 자료

* [Databricks Platform Overview](https://docs.databricks.com/aws/en/getting-started/overview.html)
* [Databricks Lakehouse Architecture](https://docs.databricks.com/en/lakehouse/index.html)
* [Unity Catalog Documentation](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
* [Mosaic AI Agent Framework](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
* [Delta Lake Open Source](https://delta.io/)
* [MLflow Open Source](https://mlflow.org/)
