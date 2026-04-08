---
title: "Lakehouse Federation: 외부 데이터를 이동 없이 쿼리하기"
date: 2023-06-28
author: "Databricks"
original_url: "https://www.databricks.com/blog/introducing-lakehouse-federation-capabilities-unity-catalog"
tags: [lakehouse-federation, unity-catalog, query-federation, data-governance, databricks]
---

> **원문**: [Introducing Lakehouse Federation Capabilities in Unity Catalog](https://www.databricks.com/blog/introducing-lakehouse-federation-capabilities-unity-catalog)

{% hint style="info" %}
요청하신 URL(`lakehouse-federation-querying-external-data`)은 현재 404 오류를 반환합니다. 광범위한 검색 결과, 해당 슬러그의 블로그 포스트는 존재하지 않으며, 동일한 주제(Lakehouse Federation + 외부 데이터 쿼리)를 다루는 가장 유사한 공식 포스트들을 종합하여 번역합니다. 주요 출처: Databricks 공식 블로그(2023년 6월 발표, 2024년 8월 GA 발표), 공식 보도자료(PR Newswire), 공식 문서(docs.databricks.com).
{% endhint %}

# Lakehouse Federation: 외부 데이터를 이동 없이 쿼리하기

**Unity Catalog를 통해 MySQL, PostgreSQL, Snowflake, BigQuery 등 외부 데이터 플랫폼을 단일 인터페이스로 통합·거버넌스하는 방법**

**게시일**: 2023년 6월 28일 (Data + AI Summit 발표) | **GA 발표**: 2024년 8월 1일

---

- Lakehouse Federation은 데이터를 이동·복사하지 않고도 MySQL, PostgreSQL, Snowflake, Amazon Redshift, Azure Synapse, Google BigQuery 등 외부 플랫폼을 Unity Catalog에서 단일 인터페이스로 쿼리·거버넌스할 수 있습니다.
- **Query Federation** (JDBC 기반 푸시다운 쿼리)과 **Catalog Federation** (오브젝트 스토리지 직접 접근)의 두 가지 방식을 제공하며, 각각 용도에 맞게 선택할 수 있습니다.
- 2024년 8월 GA 전환 시점에 이미 **5,000개 이상의 Databricks 고객**이 Lakehouse Federation을 활용하고 있으며, 행·열 수준 접근 제어, 데이터 리니지, 태그 등 Unity Catalog의 거버넌스 기능이 외부 소스에도 일관되게 적용됩니다.

---

## 1. 문제의 본질: 분산된 데이터 사일로

대부분의 조직에서 데이터는 운영 시스템과 분석 시스템 전반에 걸쳐 여러 곳에 분산되어 있습니다. 이런 분산 구조는 데이터 팀이 필요한 정보를 찾기 어렵게 만들고, 컴플라이언스 팀이 일관된 거버넌스를 유지하기 힘들게 합니다. 더 나아가, 이 데이터를 통합하려면 복잡한 데이터 엔지니어링 작업이 필요하고, 이는 데이터 가용성을 지연시켜 결국 혁신 속도를 떨어뜨립니다.

현실적으로 기업은 기존 시스템을 하루아침에 Databricks로 마이그레이션할 수 없습니다. 레거시 데이터베이스, 전용 데이터 웨어하우스, SaaS 플랫폼 등은 각각의 이유로 유지되어야 합니다. 그렇다면 이 모든 데이터를 어떻게 하나의 통합된 뷰로 다룰 수 있을까요?

Databricks의 답은 **Lakehouse Federation** 입니다.

---

## 2. Lakehouse Federation이란?

**Lakehouse Federation** 은 Databricks의 쿼리 연합(Query Federation) 플랫폼으로, 데이터를 통합 시스템으로 마이그레이션하지 않고도 여러 데이터 소스에 대해 쿼리를 실행할 수 있게 해주는 기능의 집합입니다.

Unity Catalog의 Lakehouse Federation 기능을 활용하면 데이터를 이동하거나 복사하지 않고도 Databricks 내에서 다양한 데이터 플랫폼에 걸쳐 데이터를 **발견(Discover), 쿼리(Query), 거버넌스(Govern)** 할 수 있습니다.

Matei Zaharia(Databricks 공동 창업자, Chief Technologist)는 이렇게 말합니다:

> "우리는 Databricks를 데이터, 분석, AI를 위한 가장 개방적이고 유연한 레이크하우스 플랫폼으로 만들어가고 있습니다. 데이터가 어디에 있든, 어떤 형식이든 상관없이 모든 데이터를 통합하도록 돕겠다는 것을 분명히 밝히고 싶습니다. 하나의 시스템을 통해 필요한 모든 데이터에 접근할 수 있게 함으로써 더 많은 혁신이 이루어질 것이며, 그 혁신이 보안을 희생하지 않는다는 점이 가장 중요합니다."

---

## 3. 두 가지 연합 방식

Lakehouse Federation은 사용 목적에 따라 두 가지 방식을 제공합니다.

아래 표는 각 방식의 작동 원리와 적합한 시나리오를 비교합니다.

| 구분 | Query Federation | Catalog Federation |
|------|-----------------|-------------------|
| **작동 방식** | Unity Catalog 쿼리를 JDBC를 통해 외부 데이터베이스로 푸시다운 | 외부 카탈로그의 테이블을 오브젝트 스토리지에서 직접 접근 |
| **컴퓨팅 위치** | Databricks + 원격 컴퓨팅 모두 사용 | Databricks 컴퓨팅만 사용 |
| **적합한 시나리오** | 애드혹 리포팅, PoC, 데이터 이동 최소화 | 점진적 Unity Catalog 마이그레이션, 하이브리드 모델 |
| **데이터 이동** | 없음 (인플레이스 쿼리) | 없음 (직접 스토리지 접근) |
| **쓰기 지원** | 읽기 전용 (Hive 메타스토어 제외) | 읽기 전용 |

Query Federation은 데이터를 그 자리에서 쿼리하고 복잡하고 시간이 많이 소요되는 ETL 처리를 피하고 싶을 때 적합합니다. Catalog Federation은 기존 Databricks Hive 메타스토어, 외부 Hive 메타스토어, AWS Glue 메타스토어 등을 Unity Catalog 내 외부 카탈로그로 마운트할 때 활용합니다.

---

## 4. 지원 데이터 소스

아래 표는 각 Federation 방식이 지원하는 데이터 소스를 정리한 것입니다.

### Query Federation 지원 소스

| 데이터 소스 | 연결 방식 | GA 상태 |
|------------|----------|--------|
| MySQL | JDBC | GA |
| PostgreSQL | JDBC | GA |
| Amazon Redshift | JDBC | GA |
| Snowflake | JDBC | GA |
| Microsoft SQL Server | JDBC | GA |
| Azure Synapse (SQL Data Warehouse) | JDBC | GA |
| Azure SQL Database | JDBC | GA |
| Google BigQuery | JDBC | GA |
| Teradata | JDBC | Public Preview |
| Oracle | JDBC | Public Preview |
| Salesforce Data Cloud | 전용 커넥터 | GA |
| Databricks (다른 워크스페이스) | Delta Sharing | GA |

### Catalog Federation 지원 소스

| 데이터 소스 | 설명 |
|------------|------|
| Legacy Databricks Hive 메타스토어 | 기존 HMS를 Unity Catalog 외부 카탈로그로 마운트 |
| 외부 Hive 메타스토어 | 자체 관리 HMS 연결 |
| AWS Glue 메타스토어 | AWS Glue Data Catalog 연결 |
| Salesforce Data 360 | Salesforce 데이터 클라우드 직접 접근 |
| Snowflake | Snowflake 테이블 직접 접근 |

지원 소스 목록은 계속 확장되고 있으며, 지금까지 나열한 소스들의 GA 전환은 단계적으로 이루어졌습니다. Google BigQuery는 2025년 3월 GA로 전환되었고, Teradata와 Oracle은 Public Preview 상태입니다.

---

## 5. 핵심 구성 요소

Lakehouse Federation을 구성하는 두 가지 핵심 Unity Catalog 객체가 있습니다.

### Connection (연결)

**Connection** 은 외부 데이터베이스 시스템에 대한 경로와 자격 증명을 지정하는 Unity Catalog의 보안 가능한 객체입니다. 연결을 생성하면 여러 외부 카탈로그에서 재사용할 수 있습니다.

```sql
-- PostgreSQL 연결 생성 예시
CREATE CONNECTION my_postgresql_conn
TYPE postgresql
OPTIONS (
  host '<postgresql-host>',
  port '5432',
  user secret ('<secret-scope>', '<secret-key-user>'),
  password secret ('<secret-scope>', '<secret-key-password>')
);

-- 연결에 대한 사용 권한 부여
GRANT USE CONNECTION ON CONNECTION my_postgresql_conn TO `data-engineers@company.com`;
```

보안 강화를 위해 자격 증명은 Databricks Secrets로 관리하는 것을 권장합니다. 2024년 GA 발표 시점부터는 Azure AD/Entra ID 기반 패스워드리스 인증(Azure 소스)과 OAuth 기반 인증(Snowflake)도 지원됩니다.

### Foreign Catalog (외부 카탈로그)

**Foreign Catalog** 는 외부 데이터베이스를 미러링하는 Unity Catalog 카탈로그로, Unity Catalog 거버넌스가 적용된 읽기 전용 쿼리를 가능하게 합니다.

```sql
-- PostgreSQL 외부 카탈로그 생성 (데이터베이스 지정 필요)
CREATE FOREIGN CATALOG my_postgresql_catalog
USING CONNECTION my_postgresql_conn
OPTIONS (database 'my_database');

-- MySQL 외부 카탈로그 생성 (데이터베이스 지정 불필요 - 2레이어 네임스페이스)
CREATE FOREIGN CATALOG my_mysql_catalog
USING CONNECTION my_mysql_conn;

-- 카탈로그 접근 권한 부여
GRANT USE CATALOG ON CATALOG my_postgresql_catalog TO `analysts@company.com`;
GRANT SELECT ON ALL TABLES IN CATALOG my_postgresql_catalog TO `analysts@company.com`;
```

외부 카탈로그가 생성되면 Databricks 노트북, SQL 워크벤치, BI 도구에서 일반 Unity Catalog 테이블처럼 쿼리할 수 있습니다. 외부 데이터베이스의 데이터나 메타데이터 변경 사항은 캐싱 없이 실시간으로 반영됩니다.

---

## 6. 실전 쿼리: 여러 소스 조인하기

Lakehouse Federation의 가장 강력한 기능 중 하나는 서로 다른 외부 소스의 데이터를 단일 SQL 쿼리로 조인할 수 있다는 것입니다.

```sql
-- SQL Server의 고객 데이터와 MySQL의 주문 데이터를 조인
SELECT
  c.customer_id,
  c.customer_name,
  c.region,
  COUNT(o.order_id) AS total_orders,
  SUM(o.order_amount) AS total_revenue
FROM my_sqlserver_catalog.sales.customers c
JOIN my_mysql_catalog.orders.order_history o
  ON c.customer_id = o.customer_id
WHERE c.region = 'APAC'
  AND o.order_date >= '2024-01-01'
GROUP BY c.customer_id, c.customer_name, c.region
ORDER BY total_revenue DESC;
```

이 쿼리에서 `WHERE` 절의 필터 조건(`region = 'APAC'`, `order_date >= '2024-01-01'`)은 각 외부 데이터베이스로 **푸시다운(Predicate Pushdown)** 되어 원본 시스템에서 먼저 필터링이 이루어집니다. 이를 통해 Databricks로 전송되는 데이터 양을 최소화하고 쿼리 성능을 향상시킵니다.

실제 성능 비교 사례를 살펴보면, 플랫폼 필터링이 적용된 쿼리는 273,405행을 4.5초에 처리한 반면, 필터링 없이 처리 시 352,722행을 5.5초에 처리하여 데이터 전송량과 처리 시간 모두에서 차이가 발생했습니다.

---

## 7. Unity Catalog를 통한 통합 거버넌스

Lakehouse Federation의 핵심 가치 중 하나는 Unity Catalog의 거버넌스 기능이 외부 소스에도 일관되게 적용된다는 점입니다.

아래 표는 Lakehouse Federation 환경에서 적용 가능한 거버넌스 기능을 정리합니다.

| 기능 | 설명 | 적용 레벨 |
|------|------|----------|
| **행 수준 보안** | 특정 사용자/그룹에게 특정 행만 노출 | 테이블 |
| **열 수준 보안** | 민감 컬럼 마스킹 또는 숨김 | 컬럼 |
| **태그(Tags)** | 데이터 자산에 메타데이터 태그 부착 | 카탈로그/스키마/테이블/컬럼 |
| **데이터 리니지** | 데이터 흐름 추적 및 시각화 | 자동 캡처 |
| **감사 로그** | 데이터 접근 기록 | 자동 캡처 |
| **권한 관리** | GRANT/REVOKE를 통한 세밀한 접근 제어 | 카탈로그/스키마/테이블 |

이처럼 외부 데이터 소스에도 단일 권한 모델을 적용할 수 있어, 조직 전체의 데이터 거버넌스를 일관되게 유지할 수 있습니다. 데이터 팀은 더 이상 각 시스템별로 별도의 접근 제어를 관리할 필요가 없습니다.

---

## 8. 성능 최적화: 구체화된 뷰(Materialized Views)

자주 접근하는 외부 데이터의 경우, **구체화된 뷰(Materialized View)** 를 생성하여 쿼리 결과를 캐시함으로써 성능을 크게 향상시킬 수 있습니다.

```sql
-- 외부 소스를 기반으로 한 구체화된 뷰 생성
CREATE MATERIALIZED VIEW main.analytics.customer_orders_mv AS
SELECT
  c.customer_id,
  c.customer_name,
  COUNT(o.order_id) AS order_count,
  SUM(o.revenue) AS total_revenue
FROM my_postgresql_catalog.prod.customers c
JOIN my_mysql_catalog.orders.transactions o
  ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name;
```

실제 성능 측정 결과에 따르면, 동일한 조인 쿼리가 최초 실행 시 5.7초에서 1.8초로 개선되었고, 이후 캐시된 결과는 744ms 수준으로 처리되었습니다. 빈번하게 액세스하는 데이터에 대해 ETL 없이 성능을 확보할 수 있는 실용적인 방법입니다.

---

## 9. 시스템 요구 사항

Lakehouse Federation을 사용하려면 아래 요건을 충족해야 합니다.

| 요건 | 세부 사항 |
|------|----------|
| **Unity Catalog** | 워크스페이스에 Unity Catalog가 활성화되어 있어야 함 |
| **컴퓨팅** | Databricks Runtime 13.3 LTS 이상 (Standard/Dedicated 모드) 또는 Pro/Serverless SQL 웨어하우스 (2023.40+) |
| **네트워크** | Databricks 컴퓨팅과 대상 데이터베이스 간 네트워크 연결 |
| **권한** | `CREATE CONNECTION` 권한 (metastore 수준), `CREATE CATALOG` 권한 |
| **자격 증명** | 각 외부 시스템에 대한 적절한 데이터베이스 자격 증명 |

{% hint style="warning" %}
**알려진 제한 사항:**

- 대부분의 외부 소스에 대한 쿼리는 **읽기 전용** 입니다 (Hive 메타스토어 연합 제외).
- Databricks 쿼리 캐싱은 연합 쿼리에서 지원되지 않습니다.
- 결과 집합이 너무 크면 executor 메모리 문제가 발생할 수 있습니다. 이런 경우 구체화된 뷰나 필터링을 통해 데이터 양을 줄이는 것을 권장합니다.
- 파일 기반 외부 데이터(S3, ADLS 등)의 경우 Lakehouse Federation보다 Unity Catalog의 외부 테이블(External Tables), 뷰, 볼륨(Volumes)이 더 적합합니다.
{% endhint %}

---

## 10. 실제 고객 사례

### Bayer — 농업 IoT 데이터 통합

Bayer의 PlantBalance 센서 및 데이터 솔루션은 온실 재배업자들이 식물 행동을 지속적으로 모니터링하고 성장 문제를 조기에 감지할 수 있도록 돕습니다. Tech Lead Jelle de Jong은 이렇게 말합니다:

> "Databricks의 Lakehouse Federation을 통해 데이터 과학자와 비즈니스 사용자 모두 일관된 권한 관리와 통합 사용자 인터페이스로 다양한 데이터 소스에 접근할 수 있게 되었습니다. 우리는 데이터 형식을 Delta Lake로 표준화하는 작업을 진행 중이지만, 쿼리 연합 덕분에 데이터 추출에 투자하기 전에 민첩하게 반복 작업을 할 수 있어서 매우 만족스럽습니다."

### SEGA Europe — 게임 데이터 통합

SEGA Europe에서는 게임 사용량, 판매, 텔레메트리 데이터 등 다양한 소스와 클라우드에 걸친 데이터를 하나의 장소에서 결합하고 조회합니다. Head of Data Services Felix Baker는 이렇게 말합니다:

> "Lakehouse Federation은 여러 소스와 여러 클라우드에 걸친 데이터를 결합하여 한 곳에서 모두 조회할 수 있는 능력을 제공합니다. 이제 데이터를 원본 소스에 남겨두면서도 Databricks Lakehouse에서 활용할 수 있습니다. 자주 새로 고침되는 재무 데이터를 더 이상 이동할 필요가 없어 소중한 시간을 아낄 수 있고, 이 시간을 소비자에게 최고의 게임 경험을 제공하는 데 집중할 수 있습니다."

### Shell — 에너지 전환 데이터 관리

Shell은 에너지 산업의 거대한 전환 과정에서 데이터가 비즈니스를 더 효율적으로 만드는 중요한 지원자임을 강조합니다. Chief Digital Technology Advisor Bryce Bartmann은 이렇게 말합니다:

> "Lakehouse Federation을 통해 기존 데이터 환경을 Unity Catalog로 통합하는 작업을 더 빠르게 진행할 수 있게 되었습니다. 덕분에 Shell의 데이터 거버넌스가 단순해졌습니다. 더 많은 데이터 세트가 한 곳에서 발견 가능해지고, 인증이 표준화되며, 공통 프로그래밍 언어로 데이터 세트 전반에 걸친 쿼리가 가능해졌습니다."

---

## 11. GA 발표 (2024년 8월): 새로운 기능

2024년 8월 1일, Databricks는 Lakehouse Federation의 **일반 공개(General Availability)** 를 AWS, Azure, GCP 전 클라우드에서 선언했습니다. GA 시점의 주요 신규 기능은 다음과 같습니다.

### 향상된 푸시다운(Pushdown) 지원

SQL Server, PostgreSQL, MySQL, Snowflake, Redshift, Synapse 연결에서 표현식(Expression)과 연산자(Operator)의 **푸시다운 커버리지** 가 대폭 확대되었습니다. 더 복잡한 쿼리 로직이 원본 시스템에서 실행될 수 있어 데이터 전송량을 최소화합니다.

### 패스워드리스 인증

Azure 에코시스템 소스와 Snowflake를 시작으로 **패스워드리스 인증** 옵션이 추가되었습니다:

- Azure SQL/Synapse: **Azure AD/Entra ID** 기반 인증
- Snowflake: **OAuth** 기반 인증

자격 증명 관리의 보안 리스크를 줄이고, 기업 SSO 정책과의 통합을 용이하게 합니다.

### 개선된 Query Profile

연합 쿼리에 특화된 메타데이터와 통계를 지원하는 **Query Profile** 이 개선되어, 관리자가 연합 워크로드를 더 효과적으로 모니터링하고 감사할 수 있습니다.

### 광범위한 고객 채택

GA 시점에 이미 **5,000개 이상의 Databricks 고객** 이 Lakehouse Federation을 활용하여 데이터 에스테이트를 통합하고 일관된 데이터 발견과 거버넌스를 확보하고 있습니다.

---

## 12. Hive 메타스토어 인터페이스: 광범위한 연결성

Lakehouse Federation과 함께 Databricks는 **Unity Catalog를 위한 Hive 메타스토어(HMS) 인터페이스** 도 발표했습니다. 이 인터페이스는 Apache Hive와 호환 가능한 모든 소프트웨어가 Unity Catalog에 연결할 수 있도록 합니다.

이를 통해 조직은 Unity Catalog에서 데이터 관리, 발견, 거버넌스를 중앙화하고, 다양한 컴퓨팅 플랫폼에서 이에 연결할 수 있습니다:

- Amazon EMR
- Apache Spark (자체 관리)
- Amazon Athena
- Presto
- Trino
- 기타 HMS 호환 플랫폼

이 새로운 인터페이스는 여러 데이터 카탈로그를 유지 관리할 필요를 없애고 이러한 플랫폼 전반에 걸쳐 일관된 데이터 거버넌스를 보장합니다. Lakehouse Federation 기능과의 결합은 고객에게 데이터 메시(Data Mesh) 아키텍처를 위한 일관된 데이터 서빙 및 거버넌스 레이어를 제공합니다.

---

## 13. 데이터 민주화와 비즈니스 가치

Lakehouse Federation이 제공하는 비즈니스 가치는 기술적 편의성을 넘어섭니다.

**데이터 민주화와 발견 가능성:** Databricks는 사용자에게 구조화된 데이터와 비구조화된 데이터 모두를, 데이터가 어디에 있든 안전하게 발견하고 탐색할 수 있는 공통 접근 방식을 제공합니다. 이제 단일 쿼리로 데이터 사일로를 넘나들 수 있습니다.

**데이터에 더 빠른 접근:** 조직은 수집(Ingestion) 없이도 도메인 소유 데이터 소스를 데이터, 분석, AI 사용 사례에 신속하게 노출할 수 있습니다. Databricks Lakehouse의 캐싱과 최적화 기능을 통해 대화형 쿼리를 효율적으로 가속할 수 있습니다.

**모든 데이터 소스에 걸친 통합 거버넌스:** 전체 데이터 에스테이트에 단일 권한 모델만 필요하게 되어, 내장된 데이터 리니지와 감사 가능성을 갖춘 통합 데이터 거버넌스를 전체 데이터 메시에 걸쳐 제공합니다.

---

## 14. 관련 리소스

Lakehouse Federation에 대해 더 깊이 탐구하려면 아래 공식 자료를 참고하세요.

- [What is Lakehouse Federation? (공식 문서 - AWS)](https://docs.databricks.com/aws/en/query-federation/)
- [What is query federation? (공식 문서)](https://docs.databricks.com/aws/en/query-federation/database-federation)
- [Announcing General Availability of Lakehouse Federation (2024년 8월 GA 블로그)](https://www.databricks.com/blog/announcing-general-availability-lakehouse-federation)
- [GA for BigQuery & Preview for Teradata/Oracle (2025년 3월 블로그)](https://www.databricks.com/blog/announcing-general-availability-lakehouse-federation-google-bigquery-and-public-preview)
- [Lakehouse Federation Product Tour (데모)](https://www.databricks.com/resources/demos/tours/governance/query-federation-product-tour)
