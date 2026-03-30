# 테이블 및 지식 저장소 구성

---

## 지식 저장소(Knowledge Store)란?

지식 저장소는 Genie가 정확한 응답을 생성하기 위해 참조하는 메타데이터와 비즈니스 로직의 모음입니다.

---

## 메타데이터 커스터마이징

Space 전용 테이블/컬럼 설명을 추가할 수 있습니다. Unity Catalog의 원본 설명을 덮어쓰지 않고, Space에만 적용되는 별도의 설명을 관리합니다.

**설정 방법:**

1. Configure > Data에서 테이블을 선택합니다.
2. 각 컬럼에 Space 전용 설명과 동의어(synonym)를 추가합니다.
3. 혼란을 줄 수 있는 불필요한 컬럼은 숨김(Hide) 처리합니다.

**좋은 컬럼 설명 예시:**

```
컬럼: status
설명: "주문 상태를 나타냅니다. 가능한 값: 'pending'(대기), 'shipped'(발송), 'delivered'(배송완료), 'cancelled'(취소)"
```

---

## 프롬프트 매칭(Prompt Matching)

프롬프트 매칭을 활성화하면 사용자의 입력 언어를 실제 데이터 값과 매칭합니다. 예를 들어, 사용자가 "서울"이라고 입력하면 데이터의 "Seoul" 값과 자동 매칭됩니다.

---

## 조인 관계 정의

테이블 간 연결 관계를 명시적으로 정의합니다.

**설정 방법:**

* 간단한 경우: 컬럼 동등 구문 사용

  ```
  accounts.id = opportunity.accountid
  ```

* 복잡한 경우: SQL 표현식으로 정의

  ```sql
  orders.customer_id = customers.id AND orders.region = customers.region
  ```

---

## SQL 표현식 (SQL Expressions)

비즈니스 로직을 재사용 가능한 **Measure, Filter, Dimension**으로 정의합니다.

| 유형 | 용도 | 예시 |
|------|------|------|
| **Measure** | 지표/메트릭 정의 | `SUM(order_total) AS total_revenue` |
| **Filter** | 자주 사용하는 필터 | `status = 'active' AND created_at > '2025-01-01'` |
| **Dimension** | 분석 차원 정의 | `CASE WHEN age < 30 THEN 'Young' ELSE 'Senior' END AS age_group` |

{% hint style="info" %}
SQL 표현식은 별도의 제한(최대 200개)이 적용됩니다. 텍스트 인스트럭션보다 SQL 표현식으로 비즈니스 로직을 정의하는 것이 더 정확한 결과를 얻을 수 있습니다.
{% endhint %}
