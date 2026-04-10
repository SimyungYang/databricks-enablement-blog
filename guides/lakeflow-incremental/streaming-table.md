# Streaming Table 증분 처리

## Streaming Table의 핵심 동작 원리

Streaming Table(ST)은 **append-only** 처리 모델입니다. 소스에서 새로 도착하는 데이터만 읽어서 대상 테이블에 추가합니다. "어디까지 읽었는가"를 **체크포인트(checkpoint)** 에 기록하며, 이 체크포인트가 증분 처리의 핵심입니다.

Full Refresh는 이 체크포인트를 **완전히 삭제** 하고, 소스의 처음부터 다시 읽는 것을 의미합니다. 소스가 Kafka처럼 보존 기간이 제한된 시스템이라면, 이미 만료된 데이터는 복구할 수 없습니다.

{% hint style="warning" %}
Full Refresh를 실행하면 기존 데이터가 **삭제된 후** 소스부터 다시 수집합니다. 소스 데이터가 이미 만료(TTL 초과, 파일 삭제 등)되었다면 **데이터 손실이 영구적** 입니다.
{% endhint %}

---

## Full Refresh가 발생하는 조건

아래 변경을 적용하면 파이프라인 업데이트 시 Full Refresh가 **필수** 로 요구됩니다. 시스템이 증분 처리를 이어갈 수 없는 구조적 변경이기 때문입니다.

| 변경 유형 | 예시 | Full Refresh 필요 여부 |
|-----------|------|----------------------|
| **Stateful 연산자 추가/제거** | `dropDuplicates`, `window`, `flatMapGroupsWithState` 추가 또는 제거 | 필수 |
| **Stateful 연산자의 파라미터 변경** | `dropDuplicates`의 컬럼 목록 변경, watermark 간격 변경 | 필수 |
| **소스 변경** | 읽어오는 테이블/토픽/경로 자체를 변경 | 필수 |
| **소스 스키마 호환 불가 변경** | 기존 컬럼의 타입 변경, 컬럼 삭제 | 필수 |
| **대상 테이블 이름 변경** | ST 정의에서 테이블 이름을 변경 | 필수 (새 테이블로 인식) |

왜 이런 조건이 있을까요? Structured Streaming의 체크포인트에는 현재 쿼리 플랜의 "서명"이 저장됩니다. Stateful 연산자를 추가하면 서명이 달라지므로, 기존 체크포인트와 호환되지 않습니다. 이것은 Spark Structured Streaming의 근본적인 제약이며, Lakeflow가 임의로 우회할 수 없습니다.

---

## Full Refresh 없이 가능한 변경

다음 변경은 체크포인트와 호환되므로 Full Refresh 없이 적용됩니다. 단, 중요한 주의사항이 있습니다.

| 변경 유형 | 동작 | 주의사항 |
|-----------|------|---------|
| **SELECT 변환 로직 변경** | 새 행부터 새 로직 적용 | 기존 행은 이전 로직 결과 그대로 유지 |
| **WHERE 필터 변경** | 새 행부터 새 필터 적용 | 기존에 필터링되지 않은 행은 남아있음 |
| **새 컬럼 추가** | 기존 행은 해당 컬럼이 NULL | 기존 행과 새 행의 값 불일치 |
| **기존 컬럼 삭제** (호환 가능 시) | 메타데이터에서만 제거 | 물리적 데이터는 남아있을 수 있음 |

{% hint style="warning" %}
Full Refresh 없이 변환 로직을 변경하면, **기존 행에는 이전 로직, 새 행에는 새 로직** 이 적용된 상태가 됩니다. 이 "혼합 상태"가 비즈니스적으로 허용 가능한지 반드시 판단해야 합니다. 예를 들어, 금액 계산 공식을 변경했다면 기존 행의 금액은 여전히 이전 공식으로 계산된 값입니다.
{% endhint %}

---

## Full Refresh 실행 방법

의도적으로 Full Refresh가 필요한 경우(로직 변경 후 전체 재처리 등), 세 가지 방법으로 실행할 수 있습니다.

### 방법 1: Pipeline UI

Pipeline 상세 페이지에서 **Start** 버튼 옆 드롭다운 > **Full refresh all** 을 선택합니다. 특정 테이블만 선택적으로 Full Refresh하려면 **Full refresh selection** 을 사용합니다.

### 방법 2: REST API

```bash
# 전체 테이블 Full Refresh
curl -X POST "https://<workspace-url>/api/2.0/pipelines/<pipeline-id>/updates" \
  -H "Authorization: Bearer <token>" \
  -d '{"full_refresh": true}'

# 특정 테이블만 Full Refresh
curl -X POST "https://<workspace-url>/api/2.0/pipelines/<pipeline-id>/updates" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "full_refresh_selection": ["catalog.schema.target_table"]
  }'
```

### 방법 3: Databricks CLI

```bash
# 전체 Full Refresh
databricks pipelines start-update <pipeline-id> --full-refresh

# 특정 테이블만 Full Refresh
databricks pipelines start-update <pipeline-id> \
  --full-refresh-selection "catalog.schema.target_table"
```

{% hint style="info" %}
**선택적 Full Refresh** (`full_refresh_selection`)를 활용하면 영향 범위를 최소화할 수 있습니다. 전체 파이프라인이 아닌, 변경이 필요한 테이블만 지정하세요.
{% endhint %}

---

## Full Refresh 방지: `pipelines.reset.allowed`

프로덕션 파이프라인에서 실수로 Full Refresh가 실행되는 것을 막으려면, 테이블 정의에 **보호 설정** 을 추가합니다.

```sql
CREATE OR REFRESH STREAMING TABLE orders
TBLPROPERTIES ('pipelines.reset.allowed' = 'false')
AS SELECT * FROM STREAM(raw_orders);
```

```python
@dlt.table(
    table_properties={"pipelines.reset.allowed": "false"}
)
def orders():
    return spark.readStream.table("raw_orders")
```

이 설정이 적용된 테이블에 Full Refresh를 시도하면 **파이프라인 업데이트가 실패** 합니다. UI에서도, API에서도, CLI에서도 마찬가지입니다.

{% hint style="info" %}
이 설정은 "실수 방지"가 목적입니다. Full Refresh가 정말로 필요한 경우에는 해당 프로퍼티를 임시로 `true`로 변경한 후 실행하고, 다시 `false`로 되돌리면 됩니다.
{% endhint %}

---

## Append Flow: Full Refresh 없이 소스 추가하기

파이프라인 운영 중 **새로운 소스를 추가** 해야 할 때, 기존 방식으로는 소스를 변경하는 것이므로 Full Refresh가 필요합니다. **Append Flow** 는 이 문제를 해결합니다.

### Append Flow란?

Append Flow는 하나의 Streaming Table에 **여러 소스의 데이터를 독립적으로** 추가할 수 있는 패턴입니다. 각 소스는 별도의 체크포인트를 유지하므로, 새 소스를 추가해도 기존 소스의 처리 상태에 영향을 주지 않습니다.

### 기본 패턴 (SQL)

```sql
-- 대상 테이블 정의 (스키마만, 소스 없음)
CREATE OR REFRESH STREAMING TABLE all_orders (
  order_id BIGINT,
  product STRING,
  amount DECIMAL(10,2),
  region STRING,
  order_date DATE
);

-- Flow 1: 한국 주문
CREATE FLOW korea_orders
AS INSERT INTO all_orders BY NAME
SELECT * FROM STREAM(raw_korea_orders);

-- Flow 2: 미국 주문 (나중에 추가 — 기존 Flow에 영향 없음)
CREATE FLOW us_orders
AS INSERT INTO all_orders BY NAME
SELECT * FROM STREAM(raw_us_orders);
```

### 일회성 백필(Backfill) 패턴

Append Flow의 강력한 활용법 중 하나는 **일회성 과거 데이터 적재** 입니다. `ONCE` 키워드를 사용하면 해당 Flow는 한 번만 실행되고 이후 비활성화됩니다.

```sql
-- 과거 데이터를 한 번만 적재 (배치 소스 사용 가능)
CREATE FLOW backfill_legacy_orders
  ONCE
AS INSERT INTO all_orders BY NAME
SELECT
  order_id,
  product,
  amount,
  region,
  order_date
FROM legacy_orders_archive  -- STREAM 없이 배치로 읽기
WHERE order_date < '2025-01-01';
```

{% hint style="info" %}
`ONCE` Flow는 **배치 소스** 도 읽을 수 있습니다 (`STREAM` 키워드 없이). 이를 통해 과거 아카이브 데이터를 Streaming Table에 한 번만 백필할 수 있습니다.
{% endhint %}

### Python에서의 Append Flow

```python
import dlt
from pyspark.sql.functions import *

# 대상 테이블 정의
dlt.create_streaming_table("all_orders")

# Flow 1: 한국 주문
@dlt.append_flow(target="all_orders")
def korea_orders():
    return spark.readStream.table("raw_korea_orders")

# Flow 2: 미국 주문
@dlt.append_flow(target="all_orders")
def us_orders():
    return spark.readStream.table("raw_us_orders")

# 일회성 백필
@dlt.append_flow(target="all_orders", once=True)
def backfill_legacy():
    return spark.read.table("legacy_orders_archive") \
        .filter("order_date < '2025-01-01'")
```

---

## 체크포인트 복구 옵션

Full Refresh 후 소스부터 다시 읽을 때, 소스 유형에 따라 **시작 지점을 조정** 할 수 있습니다. 이를 통해 불필요한 재처리를 줄일 수 있습니다.

아래 테이블은 소스 유형별로 사용할 수 있는 복구 옵션을 정리합니다.

| 소스 유형 | 옵션 | 설명 | 예시 |
|-----------|------|------|------|
| **Auto Loader** (클라우드 파일) | `modifiedAfter` | 지정 시점 이후 변경된 파일만 처리 | `"modifiedAfter": "2026-01-01T00:00:00Z"` |
| **Kafka** | `startingOffsets` | 특정 offset부터 시작 | `"startingOffsets": "earliest"` 또는 `{"topic":{"0":100}}` |
| **Delta Streaming** | `startingVersion` | 특정 Delta 버전부터 읽기 | `.option("startingVersion", 42)` |
| **Delta Streaming** | `startingTimestamp` | 특정 시점 이후 변경분만 읽기 | `.option("startingTimestamp", "2026-01-01")` |

### Auto Loader 복구 예시

```sql
CREATE OR REFRESH STREAMING TABLE raw_events
AS SELECT *
FROM cloud_files(
  's3://bucket/events/',
  'json',
  map(
    'cloudFiles.modifiedAfter', '2026-01-01T00:00:00.000Z',
    'cloudFiles.inferColumnTypes', 'true'
  )
);
```

### Delta Streaming 복구 예시

```python
@dlt.table
def processed_events():
    return spark.readStream \
        .option("startingVersion", 42) \
        .table("catalog.schema.raw_events")
```

{% hint style="warning" %}
체크포인트 복구 옵션은 **Full Refresh 후** 의 시작 지점을 조정하는 것이지, Full Refresh 자체를 방지하는 것이 아닙니다. Full Refresh 방지에는 `pipelines.reset.allowed = false`를 사용하세요.
{% endhint %}

---

## 요약: Streaming Table 증분 처리 전략

1. **설계 단계**: Stateful 연산자가 정말 필요한지 신중하게 판단합니다. 한번 추가하면 변경 시 Full Refresh가 불가피합니다.
2. **보호 설정**: 프로덕션 테이블에는 반드시 `pipelines.reset.allowed = false`를 설정합니다.
3. **소스 추가**: 새 소스 추가 시 기존 ST를 수정하지 말고, **Append Flow** 패턴을 사용합니다.
4. **백필**: 과거 데이터 적재가 필요하면 `ONCE` Append Flow를 활용합니다.
5. **복구 준비**: Full Refresh가 불가피한 경우를 대비해, 소스별 복구 옵션(`modifiedAfter`, `startingVersion` 등)을 사전에 파악해 둡니다.
