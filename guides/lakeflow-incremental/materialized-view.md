# Materialized View 증분 처리

## Materialized View와 Enzyme 엔진

Materialized View(MV)는 Streaming Table과 근본적으로 다른 처리 모델을 사용합니다. MV는 SQL 쿼리의 **결과를 물리적으로 저장** 하고, 소스 데이터가 변경되면 결과를 **자동으로 갱신** 합니다.

이때 핵심적인 역할을 하는 것이 **Enzyme** (Databricks 내부 최적화 엔진)입니다. Enzyme은 매 업데이트마다 "변경된 부분만 계산(incremental refresh)"할지, "전체를 다시 계산(full recompute)"할지를 **자동으로 판단** 합니다.

### Enzyme의 판단 기준

Enzyme은 다음 요소를 종합적으로 고려합니다.

1. **쿼리의 SQL 연산자** 가 incremental refresh를 지원하는가?
2. **소스 테이블** 이 변경 추적(Change Tracking) 전제조건을 충족하는가?
3. **비용 모델** 에서 incremental이 full보다 효율적인가?

세 조건이 모두 충족될 때만 incremental refresh가 실행됩니다. 하나라도 실패하면 full recompute로 폴백합니다.

---

## Full Recompute 유발 원인 5가지

Enzyme이 full recompute를 선택하는 원인은 크게 5가지로 분류됩니다. 각각의 원인을 이해하면 최적화 전략을 세울 수 있습니다.

### 원인 A: 지원되지 않는 SQL 연산자

Enzyme이 incremental refresh를 지원하는 연산자 목록은 제한적입니다. 아래 테이블은 주요 연산자의 지원 여부를 정리합니다.

| 연산자 | Incremental 지원 | 비고 |
|--------|:----------------:|------|
| `SELECT`, `WHERE`, `UNION ALL` | O | 기본 연산 |
| `JOIN` (INNER, LEFT, RIGHT, FULL) | O | 2개 이하 권장 |
| `GROUP BY` + 집계함수 | O | SUM, COUNT, MIN, MAX, AVG 등 |
| `DISTINCT` | O | GROUP BY로 내부 변환 |
| `HAVING` | O | 집계 후 필터 |
| `ORDER BY` (최종 결과) | X | Full recompute 유발 |
| `LIMIT` | X | Full recompute 유발 |
| Window 함수 (`ROW_NUMBER`, `RANK` 등) | X | Full recompute 유발 |
| 서브쿼리 (비상관) | 부분 지원 | 구조에 따라 다름 |
| `LATERAL VIEW` / `EXPLODE` | X | Full recompute 유발 |

왜 일부 연산자가 지원되지 않을까요? `ORDER BY`나 `LIMIT`는 전체 데이터셋에 대한 전역(global) 연산이므로, 부분 변경만으로 결과를 정확히 갱신할 수 없습니다. Window 함수도 마찬가지로, 한 행의 변경이 다른 모든 행의 rank/row_number를 바꿀 수 있습니다.

### 원인 B: 비결정적(Non-deterministic) 함수

비결정적 함수는 같은 입력에 대해 실행 시점마다 다른 결과를 반환합니다. Enzyme은 "소스 변경 → 결과 변경"의 인과관계를 추적해야 하는데, 비결정적 함수가 있으면 이 추적이 불가능합니다.

| 함수 | 문제 | 해결 방법 |
|------|------|----------|
| `CURRENT_DATE()`, `CURRENT_TIMESTAMP()` | 매 실행 시 다른 값 반환 | 소스 테이블에 `etl_date` 컬럼으로 미리 저장 |
| `RAND()`, `RANDOM()` | 매 실행 시 다른 값 반환 | 소스에서 사전 생성하거나, 해시 기반 대체 |
| `UUID()` | 매 실행 시 다른 값 반환 | 소스에서 사전 생성 |
| `NOW()` | `CURRENT_TIMESTAMP()`와 동일 | 소스에서 처리 |

핵심 원칙: 비결정적 함수는 MV 정의가 아닌 **소스 테이블(ST 또는 업스트림 MV)** 에서 실행하세요.

```sql
-- BAD: MV에서 비결정적 함수 사용 → Full Recompute
CREATE OR REFRESH MATERIALIZED VIEW daily_summary
AS SELECT
  product,
  SUM(amount) AS total,
  CURRENT_DATE() AS report_date  -- 비결정적!
FROM orders
GROUP BY product;

-- GOOD: 소스 ST에서 날짜를 미리 기록
CREATE OR REFRESH STREAMING TABLE orders_enriched
AS SELECT
  *,
  CURRENT_DATE() AS etl_date  -- ST에서는 문제 없음 (새 행에만 적용)
FROM STREAM(raw_orders);

CREATE OR REFRESH MATERIALIZED VIEW daily_summary
AS SELECT
  product,
  SUM(amount) AS total,
  etl_date AS report_date  -- 결정적 참조
FROM orders_enriched
GROUP BY product, etl_date;
```

### 원인 C: 소스 테이블 전제조건 미충족

Enzyme이 incremental refresh를 수행하려면, 소스 테이블에서 **"어떤 행이 변경되었는가"** 를 알 수 있어야 합니다. 이를 위해 소스 테이블에 다음 기능들이 활성화되어 있어야 합니다.

| 전제조건 | 역할 | 자동 활성화 여부 | 수동 설정 방법 |
|----------|------|:---------------:|--------------|
| **Row Tracking** | 개별 행 수준의 변경 추적 | X (수동만 가능) | `ALTER TABLE t SET TBLPROPERTIES ('delta.enableRowTracking' = 'true')` |
| **Deletion Vectors** (DV) | 삭제/업데이트를 효율적으로 기록 | O (대부분 자동) | `ALTER TABLE t SET TBLPROPERTIES ('delta.enableDeletionVectors' = 'true')` |
| **Change Data Feed** (CDF) | 변경 이력을 별도 피드로 제공 | X (선택적) | `ALTER TABLE t SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')` |

{% hint style="warning" %}
**Row Tracking** 은 자동으로 활성화되지 않습니다. MV의 소스가 되는 테이블에 **반드시 수동으로 설정** 해야 합니다. 이것이 누락되면, 쿼리가 아무리 최적화되어 있어도 Enzyme은 full recompute를 선택합니다.
{% endhint %}

### Row Tracking이 왜 필요한가?

Delta Lake는 기본적으로 파일 수준에서 변경을 추적합니다. 파일 하나에 수천~수만 행이 있는데, 그중 1행만 UPDATE되어도 Delta는 "이 파일이 변경됨"만 알 수 있습니다. Row Tracking을 활성화하면 **행 단위** 로 변경을 추적하므로, Enzyme이 정확히 어떤 행이 바뀌었는지 알 수 있습니다.

### Deletion Vectors의 역할

DELETE나 UPDATE가 발생하면, 기존 방식은 해당 행이 포함된 파일 전체를 다시 쓰는 Copy-on-Write를 사용합니다. Deletion Vectors는 "이 파일에서 N번째 행은 삭제됨"이라는 메타데이터만 기록하여, 실제 파일 재작성 없이 삭제를 처리합니다. 이를 통해 Enzyme이 변경 범위를 정확히 파악할 수 있습니다.

### 전제조건 일괄 설정 예시

```sql
-- 소스 테이블에 incremental refresh 전제조건 설정
ALTER TABLE catalog.schema.source_table
SET TBLPROPERTIES (
  'delta.enableRowTracking' = 'true',
  'delta.enableDeletionVectors' = 'true',
  'delta.enableChangeDataFeed' = 'true'
);
```

{% hint style="info" %}
Lakeflow Pipeline **내부** 에서 생성된 테이블(다른 ST/MV)은 Deletion Vectors가 자동으로 활성화됩니다. 하지만 **외부 소스 테이블** (파이프라인 밖에서 관리되는 Delta 테이블)은 수동 설정이 필요합니다.
{% endhint %}

### 원인 D: Enzyme 비용 모델 판단

연산자도 지원되고, 소스 전제조건도 충족되었지만, Enzyme의 비용 모델이 "full recompute가 더 효율적"이라고 판단하면 full recompute를 실행합니다.

이런 상황은 주로 다음 경우에 발생합니다.

- 소스 데이터의 **대부분이 변경** 된 경우 (예: 전체 행의 80% 이상 UPDATE)
- MV의 결과 크기 대비 **변경된 소스 행이 매우 많은** 경우
- Incremental refresh의 오버헤드(변경 추적 + 부분 재계산)가 full보다 클 것으로 추정되는 경우

이것은 Enzyme의 정상 동작이며, 대부분의 경우 비용 모델의 판단이 정확합니다. 다만, 항상 incremental을 강제하고 싶다면 `REFRESH POLICY INCREMENTAL STRICT`(Beta)를 사용할 수 있습니다.

### 원인 E: 기타 원인

- **MV 정의 자체가 변경** 된 경우 (쿼리 수정 → full recompute 1회)
- **소스 테이블이 재생성** 된 경우 (DROP + CREATE)
- **Delta 로그가 만료** 된 경우 (변경 추적 불가)
- **시스템 업그레이드** 후 내부 메타데이터 호환성 문제

---

## Enzyme Incremental Refresh 기법

Enzyme은 상황에 따라 다른 incremental refresh 기법을 선택합니다. 어떤 기법이 사용되는지 이해하면, 쿼리를 더 효과적으로 최적화할 수 있습니다.

| 기법 | 적용 상황 | 동작 방식 |
|------|----------|----------|
| **Row-level Merge** | 소스에서 소수의 행이 변경됨 | 변경된 행만 대상 MV에서 찾아 갱신 |
| **Partition-level Refresh** | 변경이 특정 파티션에 집중됨 | 해당 파티션만 재계산 |
| **Aggregation Recompute** | GROUP BY + 집계에서 일부 그룹의 소스가 변경됨 | 변경된 그룹의 집계만 재계산 |
| **Join Incremental** | JOIN의 한쪽 소스만 변경됨 | 변경된 쪽의 행만 반대쪽과 다시 JOIN |

Enzyme은 이 기법들 중 비용 모델 기준으로 가장 효율적인 것을 자동 선택합니다. 사용자가 직접 기법을 지정할 수는 없지만, 쿼리 구조와 소스 설정을 통해 Enzyme이 더 나은 선택을 하도록 유도할 수 있습니다.

---

## 쿼리 설계 원칙

### 원칙 1: 비결정적 함수를 소스로 이동

앞서 원인 B에서 설명한 대로, `CURRENT_DATE()`, `RAND()`, `UUID()` 같은 비결정적 함수는 MV가 아닌 소스(ST 또는 업스트림 MV)에서 실행합니다.

### 원칙 2: 복잡한 쿼리를 단계별 MV로 분리

하나의 MV에 너무 많은 로직을 넣으면, Enzyme이 incremental refresh를 적용하기 어렵습니다. 복잡한 변환을 여러 단계의 MV로 분리하면, 각 단계에서 Enzyme이 독립적으로 최적화할 수 있습니다.

```sql
-- BAD: 하나의 MV에 모든 로직
CREATE OR REFRESH MATERIALIZED VIEW final_report
AS SELECT
  o.region,
  p.category,
  SUM(o.amount) AS total_sales,
  COUNT(DISTINCT o.customer_id) AS unique_customers,
  AVG(r.rating) AS avg_rating
FROM orders o
JOIN products p ON o.product_id = p.id
JOIN reviews r ON o.order_id = r.order_id
GROUP BY o.region, p.category;

-- GOOD: 단계별 MV 분리
CREATE OR REFRESH MATERIALIZED VIEW order_product
AS SELECT
  o.order_id,
  o.region,
  o.amount,
  o.customer_id,
  p.category
FROM orders o
JOIN products p ON o.product_id = p.id;

CREATE OR REFRESH MATERIALIZED VIEW order_with_review
AS SELECT
  op.order_id,
  op.region,
  op.amount,
  op.customer_id,
  op.category,
  r.rating
FROM order_product op
LEFT JOIN reviews r ON op.order_id = r.order_id;

CREATE OR REFRESH MATERIALIZED VIEW final_report
AS SELECT
  region,
  category,
  SUM(amount) AS total_sales,
  COUNT(DISTINCT customer_id) AS unique_customers,
  AVG(rating) AS avg_rating
FROM order_with_review
GROUP BY region, category;
```

### 원칙 3: JOIN은 2개 이하로 유지

Enzyme은 2개 이하의 소스를 JOIN하는 쿼리에서 가장 효율적으로 incremental refresh를 수행합니다. 3개 이상의 테이블을 JOIN해야 한다면, 중간 MV를 만들어 2-way JOIN의 체인으로 구성하세요.

### 원칙 4: Window 함수 대신 집계 함수 활용

Window 함수(`ROW_NUMBER`, `RANK`, `LAG` 등)는 incremental refresh가 불가능합니다. 가능하다면 `GROUP BY` + 집계 함수로 대체하세요.

```sql
-- BAD: Window 함수 → Full Recompute
CREATE OR REFRESH MATERIALIZED VIEW latest_orders
AS SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
  FROM orders
) WHERE rn = 1;

-- GOOD: 집계 함수로 대체 (마지막 주문 날짜 기준)
CREATE OR REFRESH MATERIALIZED VIEW latest_order_dates
AS SELECT
  customer_id,
  MAX(order_date) AS latest_order_date,
  MAX_BY(order_id, order_date) AS latest_order_id,
  MAX_BY(amount, order_date) AS latest_amount
FROM orders
GROUP BY customer_id;
```

---

## REFRESH POLICY (Beta)

기본적으로 Enzyme은 incremental과 full 중 최적의 방법을 자동으로 선택합니다. 하지만 **명시적으로 incremental을 강제** 하고 싶은 경우, `REFRESH POLICY`를 사용할 수 있습니다.

{% hint style="warning" %}
REFRESH POLICY는 현재 **Beta** 기능입니다. 프로덕션 환경에서 사용 전 충분한 테스트를 권장합니다.
{% endhint %}

### REFRESH POLICY INCREMENTAL

Enzyme에게 "가능하면 incremental로 처리하라"는 힌트를 줍니다. 불가능한 경우에는 여전히 full recompute로 폴백합니다.

```sql
CREATE OR REFRESH MATERIALIZED VIEW daily_sales
REFRESH POLICY INCREMENTAL
AS SELECT
  sale_date,
  region,
  SUM(amount) AS total
FROM sales
GROUP BY sale_date, region;
```

### REFRESH POLICY INCREMENTAL STRICT

"반드시 incremental로만 처리하라"는 강제 설정입니다. Incremental이 불가능한 경우 **업데이트가 실패** 합니다. 비용 통제가 중요한 프로덕션 환경에서 유용합니다.

```sql
CREATE OR REFRESH MATERIALIZED VIEW daily_sales
REFRESH POLICY INCREMENTAL STRICT
AS SELECT
  sale_date,
  region,
  SUM(amount) AS total
FROM sales
GROUP BY sale_date, region;
```

### EXPLAIN MATERIALIZED VIEW FOR

MV가 incremental로 처리될 수 있는지 **사전에 확인** 하는 명령입니다. 문제가 있으면 구체적인 이유를 알려줍니다.

```sql
EXPLAIN MATERIALIZED VIEW FOR
SELECT
  sale_date,
  region,
  SUM(amount) AS total,
  CURRENT_DATE() AS report_date  -- 문제를 미리 발견
FROM sales
GROUP BY sale_date, region;
```

실행 결과 예시:

```
Cannot incrementally refresh: Non-deterministic function CURRENT_DATE() detected.
Recommendation: Move CURRENT_DATE() to the source table.
```

{% hint style="info" %}
새로운 MV를 정의하기 전에 `EXPLAIN MATERIALIZED VIEW FOR`로 incremental refresh 가능 여부를 확인하는 것을 습관화하세요. 배포 후 발견하는 것보다 훨씬 비용이 적습니다.
{% endhint %}

---

## 요약: Materialized View 최적화 전략

1. **소스 테이블 준비**: Row Tracking(수동), Deletion Vectors(대부분 자동), CDF(선택적)를 활성화합니다.
2. **쿼리 설계**: 비결정적 함수 제거, JOIN 2개 이하, Window 함수 대신 집계 함수, 복잡 쿼리는 단계별 MV로 분리합니다.
3. **사전 검증**: `EXPLAIN MATERIALIZED VIEW FOR`로 incremental refresh 가능 여부를 확인합니다.
4. **비용 통제**: 중요한 MV에는 `REFRESH POLICY INCREMENTAL STRICT`(Beta)를 적용하여 예상치 못한 full recompute를 방지합니다.
5. **모니터링**: Pipeline 이벤트 로그에서 각 MV의 refresh 유형(incremental/full)을 주기적으로 확인합니다.
