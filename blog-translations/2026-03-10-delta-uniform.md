---
original_title: "Delta UniForm: a universal format for lakehouse interoperability"
authors: "Bilal Obeidat, Sirui Sun, Adam Wasserman, Susan Pierce, Fred Liu, Ryan Johnson, Himanshu Raja"
date: "2023-08-14"
category: "Engineering"
original_url: "https://www.databricks.com/blog/delta-uniform-universal-format-lakehouse-interoperability"
translated_date: "2026-04-07"
---

# Delta UniForm: 레이크하우스 상호운용성을 위한 범용 포맷

> **원문**: [Delta UniForm: a universal format for lakehouse interoperability](https://www.databricks.com/blog/delta-uniform-universal-format-lakehouse-interoperability)

{% hint style="info" %}
**업데이트**: BigQuery는 이제 BigLake를 통해 Delta Lake를 네이티브로 지원합니다. 자세한 내용은 [문서](https://cloud.google.com/bigquery/docs)를 참고하세요.
{% endhint %}

오픈 데이터 레이크하우스를 도입할 때 조직이 직면하는 핵심 과제 중 하나는 데이터에 최적화된 포맷을 선택하는 것입니다. Linux Foundation Delta Lake, Apache Iceberg, Apache Hudi는 모두 데이터 민주화와 상호운용성을 가능하게 하는 훌륭한 스토리지 포맷입니다. 이 세 가지 포맷 중 어느 것을 선택하든 독점 포맷에 데이터를 저장하는 것보다는 낫습니다. 그러나 단일 스토리지 포맷으로 표준화하는 것은 결정 피로(decision fatigue)와 돌이킬 수 없는 결과에 대한 두려움을 야기할 수 있는 쉽지 않은 작업입니다.

**Delta UniForm** (Delta Lake Universal Format의 약자)은 추가적인 데이터 복사본이나 사일로를 생성하지 않고 테이블 포맷을 간단하고 쉽게 원활하게 통합하는 솔루션을 제공합니다. 이 블로그에서는 다음 내용을 다룹니다:

- Delta UniForm 소개 및 그 이점
- Delta UniForm을 Iceberg 테이블로 읽기
  - Iceberg Metadata Path 방식
  - Iceberg REST Catalog API 방식

## 여러 포맷, 단일 데이터 복사본

Delta UniForm은 Delta Lake, Iceberg, Hudi가 모두 Apache Parquet 데이터 파일 위에 구축되어 있다는 사실을 활용합니다. 포맷 간의 주요 차이점은 메타데이터 레이어에 있으며, 그 차이도 미묘한 수준입니다. 세 포맷의 메타데이터는 모두 동일한 목적을 수행하며 겹치는 정보 집합을 포함합니다.

Delta UniForm 출시 이전에는 오픈 테이블 포맷 간 전환 방식이 복사 또는 변환 기반이었고, 특정 시점의 데이터 뷰만 제공했습니다. 반면 Delta UniForm은 포맷에 관계없이 모든 리더에게 데이터의 실시간 뷰를 제공함으로써 상호운용성 요구를 더 우아하게 해결합니다.

내부적으로 Delta UniForm은 단일 Parquet 데이터 복사본에 대해 Delta Lake와 함께 Iceberg 및 Hudi 메타데이터를 자동으로 생성하는 방식으로 동작합니다. 그 결과 팀은 각 데이터 워크로드에 가장 적합한 도구를 사용하면서도 모두 단일 데이터 소스에서 작동할 수 있으며, 세 가지 생태계 전반에 걸쳐 완벽한 상호운용성을 확보할 수 있습니다.

아래 다이어그램은 이 핵심 아이디어를 보여줍니다. Delta UniForm이 활성화된 테이블에 쓰기가 발생하면, 동일한 Parquet 파일을 바탕으로 Delta Lake, Iceberg, Hudi 각각의 메타데이터 레이어가 자동으로 생성됩니다.

![Delta UniForm Architecture](https://www.databricks.com/sites/default/files/2023-08/engineering-04.png)

## 빠른 설정, 최소한의 오버헤드

Delta UniForm은 설정이 매우 간단하며, 한 번 활성화하면 원활하고 자동으로 작동합니다.

먼저 Iceberg 메타데이터를 생성하기 위한 Delta UniForm 테이블을 만들어 보겠습니다:

```sql
CREATE TABLE my_catalog.my_schema.my_table (
  col1 INT,
  col2 STRING
)
TBLPROPERTIES (
  'delta.columnMapping.mode' = 'name',
  'delta.enableIcebergCompatV2' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg'
);
```

Delta UniForm 테이블에서는 추가 포맷에 대한 메타데이터가 테이블 생성 시 자동으로 생성되고, 테이블이 수정될 때마다 업데이트됩니다. 따라서 수동 새로 고침 명령이나 테이블 포맷 변환을 위한 불필요한 컴퓨팅 실행이 필요 없습니다. 예를 들어, 이 테이블에 행을 써 보겠습니다:

```sql
INSERT INTO my_catalog.my_schema.my_table VALUES (1, 'hello');
```

이 명령은 Delta Lake 커밋을 트리거하고, 그런 다음 자동으로 비동기적으로 이 테이블에 대한 Iceberg 메타데이터를 생성합니다. 이를 통해 Delta UniForm은 데이터 파이프라인이 중단 없이 실행되도록 하며, 모든 리더가 최신 정보에 원활하게 접근할 수 있도록 합니다.

Delta UniForm은 무시할 수 있는 수준의 성능 및 리소스 오버헤드를 가지며, 컴퓨팅 리소스를 최적으로 활용합니다. 페타바이트 규모의 테이블이라도 메타데이터는 일반적으로 데이터 파일 크기의 극히 일부에 불과합니다. 또한 Delta UniForm은 이전 커밋 이후 변경 사항에만 한정된 메타데이터를 증분 생성할 수 있습니다.

테이블의 현재 Iceberg 메타데이터 경로는 다음 명령으로 확인할 수 있습니다:

```sql
DESCRIBE EXTENDED my_catalog.my_schema.my_table;
```

## Delta UniForm을 Iceberg로 읽기

Delta UniForm은 Apache Iceberg 사양에 따라 Iceberg 메타데이터를 생성합니다. 즉, Delta UniForm 테이블에 데이터를 쓰면, 오픈소스 Iceberg 사양을 준수하는 Iceberg 생태계의 모든 클라이언트에서 Iceberg로 읽을 수 있습니다.

Iceberg 사양에 따르면 리더 클라이언트는 Iceberg 테이블의 최신 상태를 나타내는 Iceberg 메타데이터를 파악해야 합니다. Iceberg 생태계 전반에서 클라이언트들은 이를 위해 두 가지 접근 방식을 취하며, UniForm은 두 가지 모두를 지원합니다. 여기서는 그 차이를 설명하고 다음 섹션에서 예시를 제공하겠습니다.

일부 Iceberg 리더는 사용자가 Iceberg 테이블의 최신 스냅샷을 나타내는 메타데이터 파일의 경로를 제공해야 합니다. 이 방식은 테이블이 변경될 때마다 사용자가 업데이트된 메타데이터 파일 경로를 제공해야 하므로 번거로울 수 있습니다.

대안으로, Iceberg 커뮤니티는 REST Catalog API 사용을 권장합니다. 클라이언트는 카탈로그에 접속하여 테이블의 최신 상태를 가져오므로, 사용자는 수동 새로 고침이나 메타데이터 경로에 대한 걱정 없이 Iceberg 테이블의 최신 상태를 읽을 수 있습니다.

Unity Catalog는 이제 Apache Iceberg 사양에 따라 오픈 Iceberg Catalog REST API를 구현합니다. 이는 오픈 API 지원에 대한 Unity Catalog의 의지와 일치하며, Unity Catalog의 HMS API 지원의 모멘텀 위에 구축된 것입니다. Unity Catalog Iceberg REST API는 Databricks 컴퓨팅 비용 없이 Iceberg 포맷으로 UniForm 테이블에 대한 오픈 액세스를 제공하면서, 최신 데이터에 액세스하기 위한 상호운용성과 자동 새로 고침 지원을 허용합니다. 부가적으로, 이를 통해 다른 카탈로그들이 Unity Catalog에 연합(federate)하고 Delta UniForm 테이블을 지원할 수 있게 될 것입니다.

Apache Iceberg 클라이언트 라이브러리에는 Iceberg REST API Catalog와 인터페이스하는 기능이 사전 패키지화되어 있습니다. 이는 Apache Iceberg 표준을 완전히 구현하고 카탈로그 엔드포인트 구성을 지원하는 모든 클라이언트가 Unity Catalog Iceberg REST API Catalog에 쉽게 액세스하고 테이블의 최신 메타데이터를 가져올 수 있음을 의미합니다. 이로써 테이블 메타데이터 관리 작업이 사라집니다.

다음 섹션에서는 메타데이터 경로와 Iceberg REST Catalog API 방식 모두에 대한 Delta UniForm 지원 예시를 살펴보겠습니다.

## 예시: 메타데이터 위치를 지정하여 BigQuery에서 Delta Lake를 Iceberg로 읽기

기존 카탈로그에서 Iceberg를 읽을 때, BigQuery는 최신 Iceberg 스냅샷을 나타내는 JSON 파일에 대한 포인터를 제공해야 합니다([BigQuery 문서](https://cloud.google.com/bigquery/docs) 참조). 예를 들면 다음과 같습니다:

BigQuery에서:

```sql
CREATE EXTERNAL TABLE my_project.my_dataset.my_iceberg_table
OPTIONS (
  format = 'ICEBERG',
  uris = ['gs://my-bucket/path/to/iceberg/metadata/v1.metadata.json']
);
```

Delta UniForm과 Unity Catalog를 함께 사용하면 필요한 Iceberg 메타데이터 파일 경로를 쉽게 찾을 수 있습니다. Unity Catalog는 이 경로를 포함한 다수의 Delta Lake 테이블 속성을 노출합니다. UI 또는 API를 통해 Delta UniForm 테이블의 메타데이터 위치를 조회할 수 있습니다.

**UI로 Delta UniForm Iceberg 메타데이터 경로 조회:**

Databricks Data Explorer에서 Delta UniForm 테이블로 이동한 후, **Details** 탭을 클릭합니다. 거기서 메타데이터 경로가 포함된 Delta UniForm Iceberg 행을 확인할 수 있습니다.

Databricks에서:

```sql
DESCRIBE EXTENDED my_catalog.my_schema.my_table;
```

**API로 Delta UniForm Iceberg 메타데이터 위치 조회:**

선택한 도구에서 다음 GET 요청을 제출하여 Delta UniForm 테이블의 Iceberg 메타데이터 위치를 조회합니다:

```bash
GET https://{DATABRICKS_WORKSPACE_URL}/api/2.1/unity-catalog/tables/{full_table_name}
```

응답의 `delta_uniform_iceberg.metadata_location` 필드에 최신 Iceberg 스냅샷의 메타데이터 위치가 포함되어 있습니다.

UI 또는 API 방법으로 얻은 위치를 앞서 언급한 BigQuery 명령에 붙여넣으면, BigQuery는 해당 스냅샷을 Iceberg로 읽습니다.

테이블이 업데이트되면 최신 데이터를 읽기 위해 BigQuery에 업데이트된 메타데이터 위치를 제공해야 합니다. 프로덕션 사용 사례의 경우, Delta UniForm 테이블에 쓸 때마다 최신 Iceberg 메타데이터 경로(들)로 BigQuery를 업데이트하는 단계를 수집 파이프라인에 추가해야 합니다. 이 메타데이터 경로 업데이트의 필요성은 이 방식의 일반적인 제한 사항이며, UniForm에만 한정된 것이 아닙니다.

## 예시: REST Catalog API를 통해 Trino에서 Delta Lake를 Iceberg로 읽기

이제 Unity Catalog의 Iceberg REST Catalog API를 사용하여 Trino를 통해 앞서 만든 동일한 Delta UniForm 테이블을 읽어 보겠습니다.

{% hint style="info" %}
**참고**: Trino는 Delta 테이블을 직접 지원하므로 Trino에서 Delta 테이블을 읽기 위해 UniForm이 반드시 필요한 것은 아닙니다. 이 예시는 UniForm이 오픈소스 생태계에서 상호운용성을 어떻게 더 확장하는지를 보여주기 위한 것입니다.
{% endhint %}

[Trino를 설정](https://trino.io/docs/current/installation.html)한 후, `etc/catalog/iceberg.properties` 파일을 업데이트하여 Unity Catalog의 Iceberg REST API Catalog 엔드포인트를 사용하도록 Trino를 구성할 수 있습니다:

```properties
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=<UNITY_CATALOG_ICEBERG_URL>
iceberg.rest-catalog.security=OAUTH2
iceberg.rest-catalog.oauth2.token=<PERSONAL_ACCESS_TOKEN>
iceberg.rest-catalog.warehouse=<CATALOG_NAME>
```

각 변수의 의미:

- `UNITY_CATALOG_ICEBERG_URL` — Unity Catalog의 Iceberg REST API 엔드포인트 URL로, 다음 형태를 취합니다: `https://{DATABRICKS_WORKSPACE_URL}/api/2.1/unity-catalog/iceberg`
  - `DATABRICKS_WORKSPACE_URL` — 웹 브라우저에서 Databricks 워크스페이스로 이동하면 확인할 수 있는 워크스페이스 URL로, `mydatabricksworkspace.cloud.databricks.com/?o=1231231231231231` 형태입니다.
- `PERSONAL_ACCESS_TOKEN` — [이 지침](https://docs.databricks.com/dev-tools/auth.html#personal-access-tokens-for-users)에 따라 Databricks 워크스페이스에서 생성할 수 있는 Databricks Personal Access Token

properties 파일 구성이 완료되면 Trino CLI를 실행하고 Delta UniForm 테이블에 Iceberg 쿼리를 실행할 수 있습니다:

```sql
SELECT * FROM my_catalog.my_schema.my_table;
```

Trino는 Apache Iceberg REST Catalog API를 구현하므로, 외부 테이블을 생성하거나 최신 Iceberg 메타데이터 파일의 경로를 제공할 필요가 없었습니다. Trino는 UC에서 최신 Iceberg 메타데이터를 자동으로 가져온 다음 Delta UniForm 테이블의 최신 데이터를 읽습니다.

중요한 점은 Trino의 관점에서 여기서 Delta UniForm에 특화된 작업은 전혀 없다는 것입니다. Trino는 사양에 맞게 메타데이터가 생성된 Iceberg 테이블을 읽고, 표준 REST API 호출로 Iceberg 카탈로그에서 해당 메타데이터를 가져오고 있습니다.

이것이 바로 Delta UniForm의 단순함입니다. Delta Lake 라이터와 리더에게 Delta UniForm 테이블은 Delta Lake 테이블입니다. Iceberg 리더에게 Delta UniForm 테이블은 Iceberg 테이블입니다 — 모두 불필요한 데이터 복사본이나 테이블 없이 단일 데이터 파일 세트 위에서 이루어집니다.

## Delta UniForm의 영향

Preview 기간 동안 이미 많은 고객이 Delta UniForm을 통해 오픈 데이터 레이크하우스 상호운용성을 향해 빠르게 나아갈 수 있도록 지원했습니다. 조직들은 Delta Lake에 한 번 쓰고, ETL, BI, AI 등 다양한 워크로드에 걸쳐 최적의 성능, 비용 효율성, 데이터 유연성을 달성하면서 이 데이터에 어떤 방식으로든 액세스할 수 있습니다 — 비용이 많이 들고 복잡한 마이그레이션의 부담 없이 말입니다.

> "Instacart에서 우리의 비전은 모든 컴퓨팅 플랫폼과 상호운용 가능한 단일 데이터 복사본을 가진 오픈 데이터 레이크하우스를 보유하는 것입니다. Delta UniForm은 그 목표에 있어 핵심적입니다. Delta UniForm을 통해 Delta Lake 또는 Iceberg로 읽을 수 있는 테이블을 빠르고 쉽게 생성하여 에코시스템의 모든 도구와의 상호운용성을 실현할 수 있습니다."
>
> — Instacart의 시니어 스태프 소프트웨어 엔지니어 Doug Hyde가 Delta UniForm 경험을 공유하며

Databricks의 사명은 데이터 팀이 세상에서 가장 어려운 문제를 해결할 수 있도록 돕는 것이며, 이는 데이터 복사본을 만들 필요 없이 적합한 작업에 적합한 도구를 사용할 수 있는 것에서 시작합니다. Delta UniForm이 가져오는 상호운용성 개선에 기대가 크며, 앞으로도 수년간 이 분야에 지속적으로 투자할 것입니다.

Delta UniForm은 [Delta Lake 3.0 미리 보기 릴리스 후보](https://www.databricks.com/blog/announcing-delta-lake-30-new-universal-format-and-liquid-clustering)의 일부로 제공됩니다. Databricks 고객은 또한 Databricks Runtime 버전 13.2 또는 Databricks SQL 2023.35 미리 보기 채널로 Delta UniForm을 미리 사용해볼 수 있습니다.
