# 테이블 및 지식 저장소 구성

---

## 개요

Genie Space의 응답 품질은 데이터 구성과 메타데이터의 풍부함에 직접적으로 비례합니다. 이 가이드에서는 테이블 관리, 메타데이터 커스터마이징, 프롬프트 매칭, Knowledge Store의 구조를 상세히 설명합니다.

---

## 지식 저장소(Knowledge Store)란?

지식 저장소는 Genie가 정확한 응답을 생성하기 위해 참조하는 **모든 메타데이터와 비즈니스 로직의 총체** 입니다. 아래 요소들이 Knowledge Store를 구성합니다:

| 구성 요소 | 위치 | 설명 | 제한 |
|-----------|------|------|------|
| ** 테이블/뷰**| Configure > Data | Genie가 쿼리할 데이터 소스 | 최대 30개 |
| ** 컬럼 설명**| Configure > Data > 테이블 선택 | 각 컬럼의 비즈니스 의미 | 테이블당 무제한 |
| ** 동의어(Synonyms)**| Configure > Data > 컬럼 선택 | 컬럼의 별칭 | 컬럼당 무제한 |
| ** 텍스트 인스트럭션**| Configure > Instructions | 자연어 비즈니스 규칙 | 최대 200개 |
| ** 예제 쿼리**| Configure > Instructions | 질문-SQL 쌍 | 최대 200개 |
| **SQL Expressions**| Configure > Data > Expressions | Measure, Filter, Dimension | 최대 200개 |
| ** 조인 관계**| Configure > Data > Joins | 테이블 간 연결 관계 | 무제한 |
| ** 프롬프트 매칭**| Configure > Data > 컬럼 선택 | 입력값-데이터값 자동 매핑 | 컬럼당 1개 설정 |

{% hint style="info" %}
Genie는 사용자 질문을 받으면 이 Knowledge Store를 종합적으로 참조하여 최적의 SQL을 생성합니다. Knowledge Store가 풍부할수록 응답 정확도가 높아집니다.
{% endhint %}

---

## 테이블 추가/제거

### 테이블 추가 절차

1. **Configure > Data** 메뉴로 이동합니다.
2. **Add** 버튼을 클릭합니다.
3. Unity Catalog 브라우저에서 Catalog > Schema > Table을 탐색합니다.
   - _화면 설명: 3단계 트리 구조의 카탈로그 브라우저가 나타나며, 검색 기능도 제공됩니다._
4. 추가할 테이블/뷰를 선택하고 **Add** 를 클릭합니다.
5. Overview 탭에서 컬럼 정보를 확인합니다.
6. Sample data 탭에서 실제 데이터를 미리 확인합니다.

### 테이블 제거 절차

1. **Configure > Data** 에서 제거할 테이블을 찾습니다.
2. 테이블 우측의 ** 휴지통 아이콘** 을 클릭합니다.
3. 확인 다이얼로그에서 **Remove** 를 클릭합니다.

{% hint style="warning" %}
테이블을 제거하면 해당 테이블에 설정한 ** 컬럼 설명, 동의어, 프롬프트 매칭, SQL Expression이 모두 삭제** 됩니다. 임시로 비활성화하려면 제거 대신 컬럼을 숨기는 것을 고려하세요.
{% endhint %}

### 테이블 선택 가이드

| 권장 사항 | 비권장 사항 | 이유 |
|-----------|------------|------|
| 5개 이하로 시작 | 10개 이상 한꺼번에 추가 | 테이블이 많으면 잘못된 테이블 선택 확률 증가 |
| 뷰(View) 활용 | 원본 테이블 직접 사용 | 뷰로 필요한 컬럼만 노출하면 정확도 향상 |
| 비정규화된 넓은 테이블 | 과도하게 정규화된 테이블 | 조인 수가 적을수록 Genie 정확도 향상 |
| 명확한 컬럼명의 테이블 | 약어/코드로 된 컬럼명 | 의미가 명확할수록 정확한 SQL 생성 |

---

## 컬럼 숨기기(Hide Columns)

불필요한 컬럼을 숨기면 Genie가 혼란을 줄이고 더 정확한 SQL을 생성합니다.

### 숨겨야 할 컬럼 유형

| 컬럼 유형 | 예시 | 숨기는 이유 |
|-----------|------|-----------|
| ** 내부 시스템 ID**| `_id`, `_etl_timestamp`, `_row_hash` | 비즈니스 의미가 없음 |
| ** 기술적 메타데이터**| `created_by`, `modified_at`, `partition_key` | 사용자 질문과 무관 |
| ** 더 이상 사용하지 않는 컬럼**| `old_status`, `legacy_code` | 혼란 유발 |
| ** 민감 정보**| `ssn`, `credit_card`, `password_hash` | 보안 (단, UC 권한이 우선) |
| ** 중복 컬럼**| `full_name`과 `first_name + last_name` | 어떤 컬럼을 사용할지 혼동 |

### 숨기기 절차

1. **Configure > Data** 에서 테이블을 선택합니다.
2. 숨길 컬럼의 **Visibility** 토글을 끕니다.
   - _화면 설명: 각 컬럼 행 우측에 눈 모양 아이콘이 있으며, 클릭하면 회색으로 변하면서 숨겨집니다._
3. 숨긴 컬럼은 Genie가 SQL 생성 시 참조하지 않습니다.

{% hint style="tip" %}
테이블의 컬럼이 20개 이상이면, 사용자 질문에 관련된 핵심 컬럼 10-15개만 남기고 나머지는 숨기세요. 이것만으로도 정확도가 크게 향상됩니다.
{% endhint %}

---

## 메타데이터 커스터마이징

### 컬럼 설명 (Description)

Space 전용 테이블/컬럼 설명을 추가할 수 있습니다. Unity Catalog의 원본 설명을 ** 덮어쓰지 않고**, Space에만 적용되는 별도의 설명을 관리합니다.

** 좋은 컬럼 설명 작성 원칙:**

| 원칙 | 좋은 예시 | 나쁜 예시 |
|------|-----------|-----------|
| ** 가능한 값 나열**| `"주문 상태. 가능한 값: 'pending', 'shipped', 'delivered', 'cancelled'"` | `"주문 상태"` |
| ** 비즈니스 의미 설명**| `"순매출. 총매출에서 할인과 반품을 제외한 금액 (단위: 원)"` | `"매출"` |
| ** 계산 방법 명시**| `"고객 등급. 연간 구매액 기준 — Gold: 1000만원 이상, Silver: 500만원 이상, Bronze: 그 외"` | `"등급"` |
| ** 데이터 형식 명시**| `"주문일. YYYY-MM-DD 형식. 한국 시간(KST) 기준"` | `"날짜"` |

### 동의어(Synonyms)

컬럼에 동의어를 추가하면 사용자가 다양한 표현으로 질문해도 올바른 컬럼을 찾습니다.

| 컬럼명 | 추가할 동의어 |
|--------|-------------|
| `revenue` | 매출, 수익, 매출액, sales |
| `customer_count` | 고객수, 고객 수, 회원수 |
| `order_date` | 주문일, 주문 날짜, 구매일 |
| `region` | 지역, 권역, 리전, area |

** 설정 방법:**

1. Configure > Data에서 테이블을 선택합니다.
2. 컬럼을 클릭하여 상세 패널을 엽니다.
3. **Synonyms** 필드에 쉼표로 구분하여 입력합니다.

---

## 프롬프트 매칭(Prompt Matching) 상세

프롬프트 매칭은 사용자의 입력 언어를 실제 데이터 값과 자동으로 매칭하는 기능입니다.

### 왜 필요한가?

| 사용자 입력 | 실제 데이터 값 | 프롬프트 매칭 없이 | 프롬프트 매칭 있으면 |
|------------|---------------|-------------------|---------------------|
| "서울" | "Seoul" | 매칭 실패 → 결과 없음 | "서울" → "Seoul" 자동 변환 |
| "삼성전자" | "Samsung Electronics" | 매칭 실패 | 자동 매칭 |
| "2분기" | "Q2" | 매칭 실패 | 자동 매칭 |

### 설정 방법

1. **Configure > Data** 에서 테이블을 선택합니다.
2. 프롬프트 매칭이 필요한 컬럼을 클릭합니다.
3. **Prompt Matching** 섹션에서 **Enable** 을 클릭합니다.
   - _화면 설명: 프롬프트 매칭을 활성화하면 해당 컬럼의 고유 값 목록이 로드되며, Genie가 사용자 입력과 데이터 값을 자동 매핑합니다._

### 자동 값 매핑 vs 수동 매핑

| 방식 | 설명 | 사용 사례 |
|------|------|----------|
| ** 자동 매핑**| 컬럼의 고유 값을 Genie가 자동으로 인덱싱 | 값이 명확한 컬럼 (국가, 제품명 등) |
| ** 수동 정규식 패턴**| 사용자가 정규식으로 매칭 규칙 정의 | 약어, 다국어, 복합 패턴 |

### 정규식 패턴 예시

| 패턴 | 설명 | 매칭 결과 |
|------|------|----------|
| `서울\|Seoul\|SEL` | 서울의 다양한 표현 매칭 | → "Seoul" |
| `Q[1-4]\|[1-4]분기` | 분기 표현 매칭 | → "Q1", "Q2" 등 |
| `삼성.*\|Samsung.*` | 삼성 관련 회사 매칭 | → "Samsung Electronics" |

{% hint style="warning" %}
프롬프트 매칭은 **카디널리티(고유 값 수)가 낮은 컬럼** 에 적합합니다. 고유 값이 수만 개 이상인 컬럼(예: 주문번호)에는 사용하지 마세요. 인덱싱 시간이 길어지고 효과도 미미합니다.
{% endhint %}

---

## 조인 관계 정의

테이블 간 연결 관계를 명시적으로 정의합니다. Genie는 이 정보를 참고하여 정확한 JOIN 쿼리를 생성합니다.

### 설정 방법

** 간단한 경우**— 컬럼 동등 구문 사용:

```
accounts.id = opportunity.accountid
```

** 복합 키 조인:**

```sql
orders.customer_id = customers.id AND orders.region = customers.region
```

** 조건부 조인:**

```sql
events.user_id = users.id AND events.event_date >= users.created_date
```

{% hint style="tip" %}
조인 관계를 정의하지 않으면 Genie가 컬럼명을 기반으로 ** 추론** 합니다. 대부분 정확하지만, 컬럼명이 모호한 경우(예: 여러 테이블에 `id` 컬럼이 있는 경우) 명시적 정의가 필요합니다.
{% endhint %}

---

## SQL 표현식 (SQL Expressions)

비즈니스 로직을 재사용 가능한 **Measure, Filter, Dimension** 으로 정의합니다. 텍스트 인스트럭션보다 SQL로 명확하게 정의하는 것이 더 정확한 결과를 얻을 수 있습니다.

| 유형 | 용도 | 예시 |
|------|------|------|
| **Measure**| 지표/메트릭 정의 | `SUM(order_total) AS total_revenue` |
| **Filter**| 자주 사용하는 필터 | `status = 'active' AND created_at > '2025-01-01'` |
| **Dimension**| 분석 차원 정의 | `CASE WHEN age < 30 THEN 'Young' ELSE 'Senior' END AS age_group` |

### SQL Expression 작성 예시

| 비즈니스 요구사항 | 유형 | SQL Expression |
|------------------|------|---------------|
| "순매출" 지표 | Measure | `SUM(amount) - SUM(discount) - SUM(refund) AS net_revenue` |
| "활성 고객" 필터 | Filter | `last_purchase_date >= DATE_ADD(CURRENT_DATE(), -90)` |
| "매출 구간" 차원 | Dimension | `CASE WHEN revenue < 1000000 THEN 'Small' WHEN revenue < 10000000 THEN 'Medium' ELSE 'Large' END AS revenue_tier` |
| "전년 동기 대비" 지표 | Measure | `SUM(CASE WHEN YEAR(order_date) = YEAR(CURRENT_DATE()) THEN amount ELSE 0 END) - SUM(CASE WHEN YEAR(order_date) = YEAR(CURRENT_DATE()) - 1 THEN amount ELSE 0 END) AS yoy_diff` |

{% hint style="info" %}
SQL 표현식은 최대 **200개** 까지 추가할 수 있습니다. 텍스트 인스트럭션으로 "순매출은 총매출에서 할인과 반품을 빼세요"라고 쓰는 것보다, SQL Expression으로 정확한 공식을 정의하는 것이 훨씬 안정적입니다.
{% endhint %}

---

## 데이터 구성 베스트 프랙티스

| 항목 | 권장 사항 |
|------|----------|
| ** 테이블 수**| 5개 이하로 시작, 필요 시 점진적 확장 |
| ** 컬럼 설명**| 가능한 값, 단위, 계산 방법 포함 |
| ** 동의어**| 한국어/영어 모두 등록 |
| ** 숨김 컬럼**| 비즈니스 의미 없는 컬럼은 모두 숨김 |
| ** 프롬프트 매칭**| 카디널리티가 낮은 카테고리 컬럼에 적용 |
| ** 조인 관계**| 모호한 경우 반드시 명시적 정의 |
| **SQL Expression**| 핵심 비즈니스 지표는 Measure로 정의 |
| ** 뷰 활용**| 복잡한 조인/변환은 뷰로 사전 처리 |
