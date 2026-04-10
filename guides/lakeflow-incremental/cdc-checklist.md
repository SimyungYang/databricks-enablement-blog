# CDC & 실전 체크리스트

## CDC 기반 증분 처리: APPLY CHANGES

데이터 소스에서 INSERT뿐 아니라 UPDATE, DELETE가 발생하는 경우, 단순한 Streaming Table(append-only)로는 정확한 현재 상태를 유지할 수 없습니다. **APPLY CHANGES** (AUTO CDC)는 CDC(Change Data Capture) 레코드를 Streaming Table에 자동으로 적용하여 이 문제를 해결합니다.

### APPLY CHANGES가 해결하는 문제

전통적인 CDC 파이프라인을 직접 구현하면 다음과 같은 복잡성이 생깁니다.

- **중복 제거**: 같은 키에 대한 여러 변경 레코드 중 최신 것만 적용
- **순서 보장**: 네트워크 지연 등으로 레코드가 순서대로 도착하지 않을 때 올바른 순서로 적용
- **Late-arriving 데이터**: 뒤늦게 도착한 과거 레코드를 정확히 처리
- **SCD 유형 관리**: Type 1(덮어쓰기) vs Type 2(이력 유지) 선택

APPLY CHANGES는 이 모든 것을 **선언적으로** 처리합니다.

{% hint style="info" %}
APPLY CHANGES는 내부적으로 Streaming Table 위에서 동작하지만, 대상 테이블을 **자동으로 MERGE** 하므로 append-only가 아닌 **upsert** 가 가능합니다.
{% endhint %}

---

## SCD Type 1: 현재 상태만 유지

SCD Type 1은 변경이 발생하면 기존 행을 **덮어씁니다**. 항상 최신 상태만 유지하므로 변경 이력은 보존되지 않습니다. 가장 일반적인 CDC 패턴입니다.

### SQL 예시

```sql
-- 대상 테이블 정의
CREATE OR REFRESH STREAMING TABLE customers;

-- CDC 적용 (SCD Type 1)
APPLY CHANGES INTO customers
FROM STREAM(raw_customer_cdc)
  KEYS (customer_id)
  SEQUENCE BY updated_at
  COLUMNS * EXCEPT (_rescued_data)
  STORED AS SCD TYPE 1;
```

### Python 예시

```python
import dlt

dlt.create_streaming_table("customers")

dlt.apply_changes(
    target="customers",
    source="raw_customer_cdc",
    keys=["customer_id"],
    sequence_by="updated_at",
    except_column_list=["_rescued_data"],
    stored_as_scd_type=1
)
```

### 동작 설명

| 구성 요소 | 역할 |
|-----------|------|
| `KEYS (customer_id)` | 이 컬럼으로 기존 행을 찾아 UPDATE/DELETE 적용 |
| `SEQUENCE BY updated_at` | 같은 키에 여러 레코드가 있으면 이 값 기준으로 최신 것만 적용 |
| `STORED AS SCD TYPE 1` | 기존 행을 최신 값으로 덮어씀 |

SEQUENCE BY가 왜 중요한가? CDC 소스(예: Kafka)에서 같은 고객의 레코드가 `[v1, v3, v2]` 순서로 도착할 수 있습니다. `SEQUENCE BY updated_at`를 지정하면, v3이 v2보다 나중이므로 v2가 뒤에 도착해도 무시됩니다. 이 순서 보장이 없으면 데이터가 과거 버전으로 덮어씌워질 수 있습니다.

---

## SCD Type 2: 변경 이력 유지

SCD Type 2는 변경이 발생하면 기존 행을 **종료(close)** 하고 새 행을 **추가(insert)** 합니다. 모든 변경 이력이 보존되므로, "이 고객의 주소가 언제 변경되었는가?"와 같은 시점 질의가 가능합니다.

### SQL 예시

```sql
-- 대상 테이블 정의
CREATE OR REFRESH STREAMING TABLE customers_history;

-- CDC 적용 (SCD Type 2)
APPLY CHANGES INTO customers_history
FROM STREAM(raw_customer_cdc)
  KEYS (customer_id)
  SEQUENCE BY updated_at
  COLUMNS * EXCEPT (_rescued_data)
  STORED AS SCD TYPE 2;
```

### SCD Type 2 결과 테이블 구조

APPLY CHANGES가 SCD Type 2로 동작하면, 대상 테이블에 자동으로 다음 컬럼이 추가됩니다.

| 자동 추가 컬럼 | 설명 |
|---------------|------|
| `__START_AT` | 이 버전이 유효해진 시점 (SEQUENCE BY 값 기준) |
| `__END_AT` | 이 버전이 종료된 시점 (NULL이면 현재 유효) |

아래는 SCD Type 2의 동작 예시입니다. 고객 A의 주소가 두 번 변경된 경우를 보여줍니다.

| customer_id | name | address | __START_AT | __END_AT |
|-------------|------|---------|------------|----------|
| A | Kim | Seoul | 2025-01-01 | 2025-06-15 |
| A | Kim | Busan | 2025-06-15 | 2026-02-01 |
| A | Kim | Jeju | 2026-02-01 | NULL |

`__END_AT`이 NULL인 행이 현재 유효한 최신 버전입니다. 시점 질의 예시:

```sql
-- 2025년 9월 기준 고객 A의 주소
SELECT * FROM customers_history
WHERE customer_id = 'A'
  AND __START_AT <= '2025-09-01'
  AND (__END_AT > '2025-09-01' OR __END_AT IS NULL);
-- 결과: Busan
```

### SCD Type 2 + 특정 컬럼만 추적

모든 컬럼 변경이 아닌, **특정 컬럼이 변경될 때만** 새 버전을 생성하려면 `TRACK HISTORY ON` 절을 사용합니다.

```sql
APPLY CHANGES INTO customers_history
FROM STREAM(raw_customer_cdc)
  KEYS (customer_id)
  SEQUENCE BY updated_at
  COLUMNS * EXCEPT (_rescued_data)
  STORED AS SCD TYPE 2
  TRACK HISTORY ON (address, membership_level);
```

이 경우 `name`이 변경되어도 새 버전이 생기지 않고, `address`나 `membership_level`이 변경될 때만 새 버전이 추가됩니다.

---

## APPLY CHANGES의 장점 요약

| 기능 | 직접 구현 | APPLY CHANGES |
|------|----------|---------------|
| 중복 제거 | MERGE + ROW_NUMBER 직접 구현 | `SEQUENCE BY`로 자동 |
| 순서 보장 | 복잡한 watermark + 상태 관리 | `SEQUENCE BY`로 자동 |
| Late-arriving 처리 | 커스텀 로직 필요 | 자동 처리 |
| SCD Type 1/2 | 전체 MERGE 로직 직접 작성 | 선언적 1줄 |
| DELETE 전파 | 별도 DELETE 로직 필요 | `APPLY AS DELETE WHEN` 절로 선언적 처리 |

직접 구현 시 수백 줄의 복잡한 코드가 필요한 작업을, APPLY CHANGES는 선언적 정의 몇 줄로 해결합니다. 또한 Databricks가 내부 최적화를 지속적으로 개선하므로, 버전 업그레이드 시 자동으로 성능 향상을 받을 수 있습니다.

---

## 실전 체크리스트

### 파이프라인 설계 시

- [ ] **ST vs MV 선택**: Append-only 소스 → ST, 전체 결과를 선언적으로 관리 → MV
- [ ] **Stateful 연산자 최소화**: ST에서 `dropDuplicates`, window 등은 나중에 변경 시 Full Refresh가 필수이므로 신중하게 결정
- [ ] **소스 테이블 전제조건**: MV의 소스 테이블에 Row Tracking 활성화 여부 확인
- [ ] **비결정적 함수 위치**: `CURRENT_DATE()`, `RAND()` 등은 MV가 아닌 소스(ST)에서 처리
- [ ] **JOIN 개수 제한**: MV에서 JOIN은 2개 이하로, 3개 이상이면 중간 MV 분리
- [ ] **Window 함수 대안**: 가능하면 `GROUP BY` + 집계 함수로 대체
- [ ] **CDC 패턴 결정**: UPDATE/DELETE가 있는 소스 → APPLY CHANGES 사용, SCD Type 1 vs 2 결정
- [ ] **Append Flow 설계**: 향후 소스 추가 가능성이 있으면, 처음부터 Append Flow 패턴으로 설계

### 파이프라인 수정 시

- [ ] **변경 영향 분석**: 수정하려는 내용이 Full Refresh를 유발하는지 확인 (이 가이드의 조건표 참조)
- [ ] **EXPLAIN 사전 검증**: MV 수정 시 `EXPLAIN MATERIALIZED VIEW FOR`로 incremental 가능 여부 확인
- [ ] **보호 설정 확인**: 프로덕션 ST에 `pipelines.reset.allowed = false`가 설정되어 있는지 확인
- [ ] **선택적 Refresh**: 전체가 아닌 특정 테이블만 Full Refresh 필요한 경우 `full_refresh_selection` 사용
- [ ] **소스 만료 확인**: Full Refresh가 불가피한 경우, 소스 데이터(Kafka retention, S3 lifecycle 등)가 살아있는지 확인
- [ ] **체크포인트 복구 옵션 준비**: Full Refresh 후 시작 지점 조정이 필요하면 `modifiedAfter`, `startingVersion` 등 사전 설정

### 모니터링

- [ ] **Refresh 유형 확인**: Pipeline 이벤트 로그에서 각 MV의 refresh 유형(incremental/full)을 주기적으로 확인
- [ ] **비용 모니터링**: 예상보다 높은 DBU 소비가 발생하면 full recompute 발생 여부 확인
- [ ] **처리 시간 추적**: MV 업데이트 시간이 갑자기 증가하면 full recompute로 전환되었을 가능성
- [ ] **소스 변경률 모니터링**: 소스 테이블의 변경 비율이 높아지면 Enzyme이 full을 선택할 가능성 증가
- [ ] **Delta 로그 보존**: 소스 테이블의 Delta 로그 보존 기간이 충분한지 확인 (`delta.logRetentionDuration`)
- [ ] **Row Tracking 상태**: 새로 추가된 소스 테이블에 Row Tracking이 활성화되어 있는지 확인

---

## 주요 트러블슈팅

아래 테이블은 현장에서 자주 발생하는 문제와 원인, 해결 방법을 정리합니다.

| 증상 | 가능한 원인 | 해결 방법 |
|------|-----------|----------|
| MV 업데이트가 갑자기 느려짐 | Full recompute로 전환됨 | 이벤트 로그에서 refresh 유형 확인, 소스 Row Tracking 확인 |
| ST Full Refresh 후 데이터 누락 | 소스(Kafka/S3)의 데이터가 만료됨 | `pipelines.reset.allowed = false` 사전 설정, 소스 보존 기간 확인 |
| 파이프라인 업데이트 실패 (ST 변경 시) | Stateful 연산자 변경으로 Full Refresh 필요하나, `reset.allowed = false` | 의도적이면 프로퍼티 임시 해제 후 Full Refresh, 비의도적이면 변경 롤백 |
| MV incremental인데 비용이 높음 | Enzyme이 partition-level refresh로 넓은 범위 재계산 | 파티션 키 최적화, 변경이 넓게 분포되는지 확인 |
| APPLY CHANGES 후 데이터 불일치 | `SEQUENCE BY` 컬럼에 중복 값 존재 | SEQUENCE BY에 고유하고 단조 증가하는 컬럼 사용 (예: `updated_at` + `sequence_number`) |
| 새 소스 추가 후 기존 ST가 Full Refresh | 기존 ST의 소스를 직접 변경함 | Append Flow 패턴으로 새 소스를 독립적으로 추가 |

{% hint style="info" %}
파이프라인 이벤트 로그는 **Pipeline UI > Events** 탭에서 확인할 수 있으며, `system.lakeflow.events` 시스템 테이블에서 SQL로 쿼리할 수도 있습니다.
{% endhint %}
