# Lakeflow 증분 처리 가이드

## 왜 이 가이드가 필요한가

Lakeflow Declarative Pipeline(구 DLT)은 선언적으로 데이터 파이프라인을 정의하는 강력한 도구입니다. 하지만 파이프라인을 운영하다 보면, 사소한 수정 하나가 **전체 데이터를 처음부터 다시 처리(Full Refresh)** 하는 상황을 만들 수 있습니다.

이 문제는 단순히 "시간이 오래 걸린다"는 수준이 아닙니다.

{% hint style="warning" %}
**Streaming Table** 의 Full Refresh는 체크포인트가 초기화되어 **데이터 손실 또는 중복** 위험이 있습니다. **Materialized View** 의 Full Recompute는 전체 소스를 다시 읽어 **비용이 수십~수백 배 폭증** 할 수 있습니다.
{% endhint %}

실제 프로덕션 환경에서 테라바이트급 테이블의 Full Refresh가 발생하면, 수 시간의 다운타임과 수천 달러의 추가 비용이 발생합니다. 이 가이드는 Full Refresh가 **언제, 왜** 발생하는지 정확히 이해하고, 이를 **방지하거나 안전하게 관리** 하는 전략을 제공합니다.

---

## Streaming Table vs Materialized View: Full Refresh 비교

두 테이블 유형은 Full Refresh의 의미와 위험도가 근본적으로 다릅니다. 아래 테이블은 핵심 차이를 요약합니다.

| 구분 | Streaming Table (ST) | Materialized View (MV) |
|------|---------------------|----------------------|
| **처리 모델** | Append-only, 체크포인트 기반 | 전체 결과를 선언적으로 정의 |
| **Full Refresh 의미** | 체크포인트 삭제 → 소스부터 전체 재수집 | 기존 결과 삭제 → 전체 소스 재계산 |
| **데이터 손실 위험** | 높음 (소스가 만료/삭제된 경우 복구 불가) | 낮음 (소스 데이터가 살아있으면 재계산 가능) |
| **비용 영향** | 소스 재수집 + 재처리 비용 | 전체 소스 스캔 + 재계산 비용 |
| **자동 발생 여부** | 특정 변경 시 시스템이 강제 요구 | Enzyme 엔진이 자동으로 full/incremental 선택 |
| **사용자 제어** | `pipelines.reset.allowed = false`로 방지 가능 | `REFRESH POLICY INCREMENTAL STRICT`(Beta)로 강제 가능 |

핵심 시사점: Streaming Table은 "방지"에 집중해야 하고, Materialized View는 "최적화"에 집중해야 합니다. ST는 Full Refresh 자체를 막아야 하며, MV는 Enzyme이 incremental로 처리할 수 있도록 쿼리와 소스를 설계해야 합니다.

---

## 가이드 구성

이 가이드는 세 개의 서브페이지로 구성됩니다.

### [Streaming Table 증분 처리](streaming-table.md)

Streaming Table에서 Full Refresh가 발생하는 정확한 조건, Full Refresh 없이 가능한 변경, 보호 설정(`pipelines.reset.allowed`), Append Flow 패턴, 체크포인트 복구 옵션을 다룹니다.

### [Materialized View 증분 처리](materialized-view.md)

Enzyme(Databricks 내부 최적화 엔진)의 동작 원리, Full Recompute를 유발하는 5가지 원인, 소스 테이블 전제조건(Row Tracking, Deletion Vectors, CDF), 쿼리 설계 원칙, REFRESH POLICY(Beta)를 다룹니다.

### [CDC & 실전 체크리스트](cdc-checklist.md)

APPLY CHANGES(AUTO CDC)를 활용한 SCD Type 1/2 패턴과, 파이프라인 설계/수정/모니터링을 위한 실전 체크리스트를 제공합니다.

---

## 참고 자료

| 문서 | 링크 |
|------|------|
| Pipeline Updates (공식 문서) | [docs.databricks.com/ldp/updates](https://docs.databricks.com/aws/en/ldp/updates) |
| Checkpoint Recovery | [docs.databricks.com/ldp/recover-streaming](https://docs.databricks.com/aws/en/ldp/recover-streaming) |
| Incremental Refresh | [docs.databricks.com/optimizations/incremental-refresh](https://docs.databricks.com/aws/en/optimizations/incremental-refresh) |
| Append Flows | [docs.databricks.com/ldp/flows](https://docs.databricks.com/aws/en/ldp/flows) |
| Optimizing MV Recomputes (블로그) | [databricks.com/blog/optimizing-materialized-views-recomputes](https://www.databricks.com/blog/optimizing-materialized-views-recomputes) |
| APPLY CHANGES API | [docs.databricks.com/ldp/cdc](https://docs.databricks.com/aws/en/ldp/cdc) |

이 참고 자료들은 각 서브페이지에서도 맥락에 맞게 링크됩니다.
