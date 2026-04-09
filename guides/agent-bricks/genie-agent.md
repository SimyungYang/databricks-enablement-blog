# Genie Spaces 연동

---

## 개요

Genie Spaces는 Unity Catalog에 등록된 **테이블 데이터를 자연어 챗봇** 으로 변환합니다. 비즈니스 사용자가 SQL 없이도 데이터에 질문할 수 있으며, 내부적으로 자연어를 SQL로 변환하여 실행합니다.

**적합한 유스케이스:**
- 비즈니스 데이터 탐색 (매출, 재고, 고객 분석)
- 셀프 서비스 분석 (비기술 사용자가 직접 데이터 조회)
- KPI/메트릭 확인 (일별/월별 성과 지표)
- 임원 대시보드 대체 (자연어로 원하는 데이터를 즉시 조회)

---

## 작동 원리

Genie는 단일 LLM이 아닌 **복합 AI 시스템(Compound AI System)** 입니다.

```
사용자 질문 (자연어)
    ↓
Genie 파싱 & 관련 데이터 소스 식별
    ↓
Unity Catalog 메타데이터 + Knowledge Store 컨텍스트 필터링
    ↓
읽기 전용 SQL 쿼리 생성
    ↓
SQL Warehouse에서 실행
    ↓
결과 반환 (테이블/차트)
```

**응답에 활용되는 컨텍스트:**
- Unity Catalog 테이블/컬럼 메타데이터
- Knowledge Store (작성자가 큐레이션한 공간 수준 컨텍스트)
- 예시 SQL 쿼리 및 SQL 함수
- 텍스트 지시사항 및 대화 이력

{% hint style="info" %}
Genie는 **읽기 전용 SQL만 생성** 합니다. INSERT, UPDATE, DELETE 등의 쓰기 쿼리는 절대 실행되지 않으므로 데이터 안전성이 보장됩니다.
{% endhint %}

---

## 사전 요구사항

| 요구사항 | 설명 |
|----------|------|
| **SQL Warehouse** | Pro 또는 Serverless SQL Warehouse |
| **Unity Catalog** | 데이터가 UC에 등록되어 있어야 함 |
| **테이블 제한** | 공간당 최대 30개 테이블/뷰 |
| **처리량** | UI: 20 질문/분, API: 5 질문/분 (무료 티어) |
| **용량** | 공간당 10,000 대화, 대화당 10,000 메시지 |

**필요 권한:**
- Databricks SQL 워크스페이스 자격
- SQL Warehouse에 대한 `CAN USE` 접근
- 데이터 객체에 대한 `SELECT` 권한

---

## 생성 및 설정

### Step 1: Genie Space 생성

1. 좌측 메뉴에서 **Genie**> **New** 클릭
2. Unity Catalog에서 데이터 소스 (테이블/뷰) 선택
3. **Create** 클릭

### Step 2: Knowledge Store 설정

생성 후 반드시 Knowledge Store를 설정하세요. 이것이 Genie의 정확도를 결정합니다.

| 설정 항목 | 설명 | 예시 |
|-----------|------|------|
| **테이블/컬럼 설명** | 비즈니스 용어, 동의어 정의 | `order_amt` → "주문 금액 (원화, VAT 포함)" |
| **JOIN 관계** | 테이블 간 연결 정의 | `orders.customer_id = customers.id` |
| **재사용 가능 SQL 표현식** | 측정값, 필터, KPI용 표현식 | 월별 매출 합계, YoY 성장률 계산식 |
| **프롬프트 매칭** | 형식 지원, 엔터티 교정 | "매출" → `revenue`, "이번 달" → `CURRENT_MONTH` |

### Step 3: Instructions & Examples 추가 (최대 100개)

- 정적 또는 파라미터화된 SQL 쿼리 (자연어 제목 포함)
- Unity Catalog 함수 (복잡한 로직용)
- 텍스트 지시사항 (비즈니스 컨텍스트, 형식 규칙)

{% hint style="info" %}
**예시 등록 팁**: "이번 달 매출은?"이라는 질문에 대해 정확한 SQL을 등록해두면, 유사한 질문("이번 달 수익은?", "이달 매출 합계는?")에도 올바른 SQL이 생성됩니다.
{% endhint %}

### Step 4: 공간 설정

- 제목, 설명 (마크다운 지원)
- 기본 SQL Warehouse 설정
- 사용자 안내용 샘플 질문 등록
- 태그 분류

---

## 모니터링 및 개선

**Monitoring** 탭에서 다음을 확인할 수 있습니다:
- 사용자가 질문한 모든 내용
- 사용자 피드백 (좋아요/싫어요)
- 플래그된 응답

이를 바탕으로 Knowledge Store와 Instructions를 반복적으로 개선합니다.

---

## Agent Bricks에서의 활용: Supervisor 서브 에이전트로 사용

Genie Spaces는 **Supervisor Agent의 서브 에이전트** 로 사용할 수 있습니다. 이를 통해 문서 Q&A(Knowledge Assistant)와 데이터 분석(Genie)을 하나의 멀티 에이전트 시스템으로 통합할 수 있습니다.

### 전체 연결 흐름

```
1. Genie Space 생성 및 Knowledge Store 설정 완료
    ↓
2. Supervisor Agent 생성 화면에서 "Add Sub-Agent" 클릭
    ↓
3. 에이전트 유형으로 "Genie Space" 선택
    ↓
4. 연결할 Genie Space 선택
    ↓
5. Description 작성 (Supervisor가 언제 이 에이전트에 라우팅할지 판단하는 기준)
    ↓
6. 저장 후 테스트 — Supervisor에 데이터 관련 질문을 하면 Genie로 라우팅됨
```

### SQL 분석 에이전트로서의 활용 예시

**시나리오**: 사내 HR봇에 "우리 팀 인원 현황"을 질문하면 데이터로 답변

```
[Supervisor Agent]
├── [KA: HR 정책 문서] — "연차 정책 알려줘" → 문서 기반 답변
└── [Genie: HR 데이터] — "우리 팀 인원 현황" → SQL 실행 후 테이블 반환
```

Supervisor의 Description 예시:
- KA: "회사 HR 정책, 복리후생, 규정 관련 질문을 처리합니다"
- Genie: "직원 수, 부서별 인원, 입퇴사 현황 등 HR 데이터를 조회합니다"

---

## 제한사항과 해결 방법

| 제한사항 | 상세 | 해결 방법 |
|----------|------|-----------|
| **테이블 수 30개 제한** | 한 공간에 30개 초과 불가 | 비즈니스 도메인별로 Space를 분리하고 Supervisor로 통합 |
| **API 처리량 제한** | 무료 티어 기준 5 질문/분 | 프로비전된 처리량(Provisioned Throughput) 사용 검토 |
| **복잡한 JOIN** | 3단계 이상 JOIN은 정확도 저하 | 미리 JOIN된 뷰(View)를 생성하여 등록 |
| **비정형 데이터** | JSON, Array 등 복잡한 타입 지원 제한 | 정규화된 테이블로 변환 후 등록 |
| **실시간 데이터** | 스트리밍 데이터 직접 지원 안 함 | Delta Live Tables로 물리화 후 Genie에 연결 |
| **차트 커스터마이징** | 기본 차트만 제공, 세부 설정 제한 | Databricks Apps(Streamlit 등)와 연계하여 커스텀 시각화 구현 |

{% hint style="warning" %}
**Genie Space를 Supervisor에 연결하려면** 해당 Space의 소유자이거나 `CAN MANAGE` 권한이 있어야 합니다. 또한 Supervisor의 서비스 프린시펄에게 Genie Space와 관련 테이블에 대한 접근 권한을 부여해야 합니다.
{% endhint %}

---

## SQL 생성 메커니즘 심층 분석

Genie가 자연어를 SQL로 변환하는 과정은 단순한 "텍스트 → SQL" 변환이 아닙니다. 여러 단계의 AI 처리 파이프라인을 거치며, 각 단계에서 정확도를 높이기 위한 다양한 기법이 적용됩니다.

### SQL 생성 파이프라인 상세

```
사용자 질문: "지난달 VIP 고객의 평균 주문 금액은?"
    ↓
[1단계: Intent Classification]
    - 질문 유형 분류: 데이터 조회 / 메타데이터 질문 / 대화형 질문
    - "지난달 VIP 고객의 평균 주문 금액" → 데이터 조회로 분류
    ↓
[2단계: Entity Resolution]
    - "VIP 고객" → customers 테이블의 tier = 'VIP' 매핑
    - "주문 금액" → orders 테이블의 order_amount 컬럼 매핑
    - "지난달" → DATE_TRUNC('month', CURRENT_DATE) - INTERVAL 1 MONTH 변환
    - Knowledge Store의 컬럼 설명, 동의어, 비즈니스 용어를 참조
    ↓
[3단계: Schema Selection]
    - 관련 테이블 식별: orders, customers
    - JOIN 관계 확인: orders.customer_id = customers.id
    - 필요한 컬럼 선택: order_amount, tier, order_date
    ↓
[4단계: SQL Generation]
    - Instructions의 SQL 표현식, 예시 쿼리를 참고
    - 읽기 전용 SQL 생성 (SELECT만 허용)
    - 생성된 SQL:
      SELECT AVG(o.order_amount) AS avg_order_amount
      FROM sales.orders o
      JOIN sales.customers c ON o.customer_id = c.id
      WHERE c.tier = 'VIP'
        AND o.order_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL 1 MONTH
        AND o.order_date < DATE_TRUNC('month', CURRENT_DATE)
    ↓
[5단계: SQL Validation]
    - 문법 검증 (Syntax Check)
    - 테이블/컬럼 존재 여부 확인
    - 읽기 전용 여부 확인 (DML 차단)
    ↓
[6단계: Execution & Response]
    - SQL Warehouse에서 실행
    - 결과를 자연어 + 테이블/차트로 포맷팅
    - 실행된 SQL 쿼리도 함께 표시
```

### SQL 생성 정확도에 영향을 미치는 요소

| 요소 | 영향도 | 설명 |
|------|--------|------|
| **컬럼/테이블 설명** | 매우 높음 | Genie가 엔터티를 매핑하는 핵심 근거. "amt"보다 "주문 금액 (원화, VAT 포함)"이 훨씬 정확 |
| **JOIN 관계 정의** | 높음 | 사전 정의된 JOIN이 없으면 잘못된 조인이 생성될 수 있음 |
| **예시 SQL** | 높음 | 유사한 패턴의 질문에 대해 정확한 SQL을 학습 |
| **데이터 타입** | 중간 | 날짜가 STRING 타입이면 날짜 연산 SQL이 부정확해짐 |
| **테이블 수** | 중간 | 테이블이 많을수록 스키마 선택 단계에서 혼란 발생 |
| **컬럼 네이밍** | 중간 | `col1`, `val` 같은 모호한 이름은 매핑 정확도를 떨어뜨림 |

---

## Genie Space와 Genie Code의 관계

Genie Space와 Genie Code는 모두 "자연어 → SQL" 기능을 제공하지만, 위치와 용도가 다릅니다.

| 구분 | Genie Space | Genie Code |
|------|------------|------------|
| **위치** | 독립 애플리케이션 (좌측 메뉴 > Genie) | AI/BI Dashboard, 노트북 내장 |
| **대상 사용자** | 비즈니스 사용자 (비기술) | 데이터 분석가, 엔지니어 |
| **데이터 범위** | 사전 등록된 테이블만 (최대 30개) | Unity Catalog 전체 테이블 접근 가능 |
| **출력 형식** | 자연어 응답 + 테이블 + 차트 | SQL 코드 + 실행 결과 |
| **거버넌스** | Space 수준 접근 제어 | UC 권한 기반 |
| **Agent Bricks 연동** | Supervisor 서브 에이전트로 사용 가능 | 직접 연동 불가 |
| **Knowledge Store** | 작성자가 큐레이션한 비즈니스 컨텍스트 | UC 메타데이터 자동 활용 |
| **맞춤 설정** | Instructions, Sample Questions, SQL 표현식 | 프롬프트 수준 설정 |

{% hint style="info" %}
**사용 시나리오 구분**: 비기술 사용자가 반복적으로 같은 데이터를 조회한다면 **Genie Space**, 분석가가 탐색적으로 다양한 데이터를 조회한다면 **Genie Code** 가 적합합니다. 두 기능은 경쟁 관계가 아닌 **보완 관계** 입니다.
{% endhint %}

---

## 데이터 보안: 사용자 권한 기반 SQL 실행

Genie Space의 가장 중요한 보안 특성은 **"사용자 권한으로 SQL이 실행된다"** 는 점입니다. 이를 통해 동일한 Genie Space를 여러 사용자가 공유하면서도, 각 사용자는 자신에게 허용된 데이터만 볼 수 있습니다.

### 권한 실행 모델

```
[사용자 A: 영업팀 — 자기 리전 데이터만 접근 가능]
    ↓ "이번 달 매출은?"
    ↓ SQL 실행 → SELECT ... WHERE region = '서울' (사용자 A의 UC 권한에 의해 필터)
    ↓ 결과: 서울 리전 매출만 반환

[사용자 B: 재무팀 — 전체 데이터 접근 가능]
    ↓ "이번 달 매출은?"
    ↓ SQL 실행 → SELECT ... (전체 데이터 조회 가능)
    ↓ 결과: 전 리전 매출 반환
```

### 보안 레이어 구조

| 레이어 | 적용 대상 | 설명 |
|--------|----------|------|
| **Genie Space 접근 권한** | Space 자체 | CAN VIEW / CAN MANAGE / CAN RUN — Space에 접근할 수 있는지 |
| **SQL Warehouse 권한** | 쿼리 실행 | CAN USE — SQL Warehouse를 사용할 수 있는지 |
| **Unity Catalog 권한** | 데이터 객체 | SELECT, USE CATALOG/SCHEMA — 테이블/뷰에 접근할 수 있는지 |
| **행 수준 보안(RLS)** | 데이터 행 | Dynamic View 또는 Row Filter로 행 단위 필터링 |
| **열 수준 보안(CLS)** | 데이터 열 | Column Mask로 민감 컬럼 마스킹 |

{% hint style="warning" %}
**Supervisor Agent를 통한 접근 시**: Supervisor Agent에서 Genie Space를 서브 에이전트로 사용할 때에도 **On-Behalf-Of-User** 모드가 적용됩니다. 즉, Supervisor에 질문한 사용자의 권한으로 Genie의 SQL이 실행되므로, 권한 없는 데이터에는 접근할 수 없습니다.
{% endhint %}

### 보안 설계 시 고려사항

1. **테이블 권한은 UC에서 관리**: Genie Space에서 별도 보안 설정을 하는 것이 아니라, UC의 GRANT/REVOKE로 관리
2. **Dynamic View 활용**: 부서별/리전별로 다른 데이터를 보여줘야 한다면, 행 수준 보안이 적용된 Dynamic View를 생성하여 Genie Space에 등록
3. **민감 컬럼 마스킹**: 고객 개인정보(이름, 전화번호 등)는 Column Mask를 적용하여 권한 없는 사용자에게 마스킹

---

## 멀티테이블 분석 시 성능 고려사항

Genie Space에서 여러 테이블을 조합한 분석을 수행할 때, 성능과 정확도에 영향을 미치는 요소들을 이해해야 합니다.

### JOIN 복잡도에 따른 정확도 변화

| JOIN 단계 | 정확도 예상 | 설명 |
|-----------|-----------|------|
| **단일 테이블** | 90%+ | 단순 필터링, 집계. 거의 정확 |
| **2테이블 JOIN** | 80~90% | JOIN 관계가 명확하면 높은 정확도 |
| **3테이블 JOIN** | 60~80% | JOIN 순서, 조건이 복잡해지면서 오류 가능성 증가 |
| **4테이블+ JOIN** | 50% 이하 | 권장하지 않음 — 뷰(View)로 사전 조합 필요 |

### 성능 최적화 전략

| 전략 | 설명 | 적용 시점 |
|------|------|-----------|
| **사전 조합 뷰(Materialized View)** | 자주 사용되는 JOIN을 미리 뷰로 생성 | 3테이블 이상 JOIN이 빈번할 때 |
| **스타 스키마 설계** | 팩트 테이블 + 디멘전 테이블 구조로 정규화 | 새로운 데이터 모델 설계 시 |
| **집계 테이블** | 일별/월별 집계를 미리 계산한 테이블 생성 | 대용량 원본 테이블의 집계 쿼리가 느릴 때 |
| **파티셔닝** | 날짜, 리전 등으로 테이블 파티셔닝 | 대용량 테이블 스캔이 빈번할 때 |
| **불필요한 테이블 제거** | Space에 등록된 테이블 중 사용빈도 낮은 것 제거 | 스키마 선택 단계 혼란 방지 |

### 대용량 데이터 처리 시 SQL Warehouse 설정

| 설정 | 권장값 | 이유 |
|------|--------|------|
| **Warehouse 크기** | Medium 이상 (대용량 데이터) | 복잡한 JOIN + 집계 쿼리에 충분한 리소스 |
| **Auto Stop** | 10분 | 비용과 응답 속도의 균형 (Cold Start 방지) |
| **Serverless** | 권장 | 자동 스케일링으로 부하에 유연하게 대응 |
| **쿼리 타임아웃** | 300초 | 비효율적 SQL의 무한 실행 방지 |

{% hint style="info" %}
**Genie의 쿼리 최적화 팁**: Genie가 생성한 SQL이 비효율적이라면, Monitoring 탭에서 해당 쿼리를 확인하고, 더 효율적인 SQL을 **Instructions의 예시 쿼리** 로 등록하세요. 유사한 질문에 대해 Genie가 최적화된 SQL 패턴을 학습합니다.
{% endhint %}

---

## Genie Space 운영 성숙도 모델

Genie Space를 처음 생성한 후 지속적으로 개선하는 과정을 4단계로 정리합니다.

| 단계 | 이름 | 활동 | 목표 정확도 |
|------|------|------|------------|
| **Level 1** | 초기 설정 | 테이블 등록, 기본 컬럼 설명 추가, 2~3개 예시 쿼리 | 50~60% |
| **Level 2** | 컨텍스트 보강 | 상세 컬럼 설명, JOIN 관계 정의, 10개 이상 예시 쿼리, 텍스트 지시사항 | 70~80% |
| **Level 3** | 피드백 반영 | Monitoring 탭 분석, 실패 쿼리 원인 수정, 동의어/약어 추가, 20개 이상 예시 | 80~90% |
| **Level 4** | 운영 최적화 | 사전 조합 뷰, 집계 테이블, 정기 피드백 루프, 비용 모니터링 | 90%+ |

{% hint style="warning" %}
**Level 1에서 바로 프로덕션 배포하지 마세요.** 최소 Level 2 이상의 컨텍스트 보강을 완료한 후 배포해야 합니다. 컬럼 설명과 JOIN 관계 없이 배포하면 SQL 생성 정확도가 매우 낮아 사용자 신뢰를 잃게 됩니다.
{% endhint %}
