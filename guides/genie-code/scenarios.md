# Genie Code 활용 시나리오

---

## 개요

Genie Code는 다양한 Databricks 제품 영역에서 AI 기반 코딩 지원을 제공합니다. 이 페이지에서는 주요 활용 시나리오별로 구체적인 대화 예시와 Genie Code의 동작을 상세히 설명합니다.

---

## 시나리오 1: 데이터 사이언스 (Notebooks)

Genie Code는 전문 ML 엔지니어처럼 동작하여 전체 ML 워크플로를 자동화합니다.

### 활용 예시: 고객 세그멘테이션 분석

**사용자 프롬프트:**

```
@customers 테이블에 대해 고객 세그멘테이션 분석을 수행해줘.
K-means 클러스터링을 사용하고 MLflow에 실험을 기록해줘.
```

**Genie Code가 수행하는 작업 (Agent 모드):**

| 단계 | 작업 | 생성되는 코드 |
|------|------|-------------|
| 1 | 테이블 스키마 분석 | `spark.table("customers").printSchema()` |
| 2 | EDA 수행 | 결측치 분석, 분포 확인, 상관관계 히트맵 |
| 3 | 피처 엔지니어링 | 범주형 인코딩, 스케일링, 피처 선택 |
| 4 | 최적 클러스터 수 결정 | Elbow method, Silhouette score |
| 5 | 모델 학습 | K-means 학습 + MLflow 실험 로깅 |
| 6 | 결과 시각화 | 클러스터별 분포, 특성 비교 차트 |
| 7 | 인사이트 요약 | 각 클러스터의 비즈니스 특성 설명 |

### 대화 흐름 예시

```
사용자: @customers 테이블에서 고객 이탈 예측 모델을 만들어줘.
       target 컬럼은 'churned'야.

Genie: 고객 이탈 예측 모델을 구축하겠습니다.
       [계획]
       1. 데이터 로드 및 EDA
       2. 피처 엔지니어링
       3. 학습/테스트 데이터 분리
       4. 여러 모델 학습 (LogisticRegression, RandomForest, XGBoost)
       5. 모델 비교 및 최적 모델 선택
       6. MLflow에 실험 로깅

       실행을 시작합니다...

       [셀 1] 데이터 로드 — 50,000행, 23개 컬럼 확인
       [셀 2] EDA — churned 비율: 18.3%, 클래스 불균형 발견
       [셀 3] 피처 엔지니어링 — 15개 피처 선택, SMOTE로 오버샘플링
       [셀 4] 모델 학습 결과:
         - LogisticRegression: AUC 0.82
         - RandomForest: AUC 0.89
         - XGBoost: AUC 0.91 ← 최적
       [셀 5] XGBoost 모델을 MLflow에 등록했습니다.

사용자: 피처 중요도를 시각화해줘.

Genie: XGBoost 모델의 피처 중요도 차트를 생성합니다...
       [차트] 상위 10개 피처: contract_length, monthly_charges, tenure...
```

{% hint style="tip" %}
`@테이블명` 구문으로 Unity Catalog 테이블을 직접 참조하면, Genie Code가 스키마 정보를 자동으로 로드하여 더 정확한 코드를 생성합니다.
{% endhint %}

---

## 시나리오 2: 데이터 엔지니어링 (Lakeflow Pipelines)

ETL 워크로드를 자동화하고 Lakeflow Spark Declarative Pipeline(SDP)을 구축합니다.

### 활용 예시: 주문 요약 파이프라인

**사용자 프롬프트:**

```
raw_orders와 raw_customers 테이블을 조인하여
daily_order_summary 테이블을 업데이트하는 SDP 파이프라인을 만들어줘.
데이터 품질 검증도 포함해줘.
```

**Genie Code가 생성하는 파이프라인 구조:**

| 레이어 | 테이블 | 설명 |
|--------|--------|------|
| Bronze | `raw_orders` | 원본 주문 데이터 (Auto Loader) |
| Bronze | `raw_customers` | 원본 고객 데이터 |
| Silver | `cleaned_orders` | 데이터 품질 검증 후 정제된 주문 |
| Gold | `daily_order_summary` | 일별 주문 요약 (조인 + 집계) |

### 대화 흐름 예시

```
사용자: raw_orders에서 daily_order_summary까지의 SDP 파이프라인을 만들어줘.

Genie: Lakeflow SDP 파이프라인을 생성하겠습니다.

       [생성된 코드]

       # Bronze 레이어: Auto Loader로 원본 데이터 수집
       @dlt.table(comment="원본 주문 데이터")
       def raw_orders():
           return spark.readStream.format("cloudFiles")...

       # Silver 레이어: 데이터 품질 검증
       @dlt.table(comment="정제된 주문 데이터")
       @dlt.expect_or_drop("valid_amount", "amount > 0")
       @dlt.expect_or_drop("valid_date", "order_date IS NOT NULL")
       def cleaned_orders():
           return dlt.read("raw_orders").join(...)

       # Gold 레이어: 일별 요약
       @dlt.table(comment="일별 주문 요약")
       def daily_order_summary():
           return dlt.read("cleaned_orders")
               .groupBy("order_date", "region")
               .agg(...)

사용자: 데이터 품질 규칙을 더 추가해줘. 주문 금액은 0보다 크고 100만 이하여야 해.

Genie: 데이터 품질 규칙을 업데이트합니다...
       @dlt.expect_or_drop("valid_amount_range", "amount > 0 AND amount <= 1000000")
```

---

## 시나리오 3: 분석 및 대시보드 (Dashboards)

데이터 자산을 탐색하고 프로덕션 수준 대시보드를 자동 생성합니다.

### 활용 예시: 영업 성과 대시보드

**사용자 프롬프트:**

```
@sales_data를 분석하고 월별 매출 추이, 지역별 성과,
상위 제품을 보여주는 대시보드를 만들어줘.
```

**Genie Code가 생성하는 대시보드 구성:**

| 위젯 | SQL 쿼리 유형 | 시각화 |
|------|-------------|--------|
| 월별 매출 추이 | 시계열 집계 + LAG 함수로 전월 대비 | 꺾은선 + 막대 복합 차트 |
| 지역별 매출 비교 | GROUP BY region + 비율 계산 | 수평 막대 차트 |
| 상위 10 제품 | ORDER BY revenue DESC LIMIT 10 | 테이블 + 조건부 서식 |
| KPI 카드 | 총 매출, 주문 수, 평균 객단가 | 숫자 카드 |

### SQL 최적화 예시

Genie Code는 대시보드 SQL을 자동으로 최적화합니다:

```
사용자: 이 대시보드 쿼리가 느려. 최적화해줘.

Genie: 쿼리를 분석한 결과, 다음 최적화를 적용합니다:

       1. 서브쿼리 → CTE(Common Table Expression)로 변환
       2. 불필요한 DISTINCT 제거
       3. WHERE 절에 파티션 프루닝 조건 추가
       4. 집계 전 필터링으로 처리 데이터량 감소

       예상 성능 개선: 쿼리 시간 70% 감소
```

{% hint style="info" %}
Agent 모드에서 대시보드를 생성하면, Genie Code가 데이터를 분석하고, SQL을 작성하고, 시각화 유형을 선택하고, 대시보드를 구성하는 **전체 과정을 자동으로 수행**합니다.
{% endhint %}

---

## 시나리오 4: GenAI 앱 디버깅 (MLflow)

GenAI 애플리케이션의 성능을 분석하고, 문제를 진단하며, 개선 방안을 제시합니다.

### 활용 예시: RAG 체인 디버깅

**사용자 프롬프트:**

```
이 RAG 체인의 evaluation 결과를 분석하고
응답 품질이 낮은 케이스를 식별해줘.
```

**Genie Code가 수행하는 분석:**

| 분석 단계 | 내용 | 출력 |
|-----------|------|------|
| 1. Evaluation 결과 로드 | MLflow experiment에서 평가 결과 조회 | 테이블 형태의 결과 요약 |
| 2. 품질 지표 분석 | faithfulness, relevance, toxicity 점수 분포 | 히스토그램, 박스플롯 |
| 3. 저품질 케이스 식별 | 점수가 임계값 미만인 케이스 필터링 | 문제 케이스 목록 |
| 4. Trace 분석 | 저품질 케이스의 MLflow Trace 추적 | 각 단계별 입출력 확인 |
| 5. 원인 분류 | 검색 실패, 컨텍스트 부족, 환각 등 분류 | 원인별 빈도 차트 |
| 6. 개선 제안 | 원인별 해결 방안 제시 | 우선순위별 액션 아이템 |

### 대화 흐름 예시

```
사용자: 이 RAG 체인에서 faithfulness 점수가 낮은 케이스를 분석해줘.

Genie: MLflow experiment에서 평가 결과를 로드합니다...

       전체 200개 테스트 중 faithfulness < 0.5인 케이스: 23개 (11.5%)

       원인 분류:
       - 검색된 문서가 질문과 무관: 12건 (52%)
       - 검색 결과는 맞지만 LLM이 환각: 7건 (30%)
       - 컨텍스트 길이 초과로 잘림: 4건 (18%)

       주요 개선 제안:
       1. 임베딩 모델 변경 (현재 e5-small → e5-large)
       2. 청크 크기 조정 (현재 500 → 300 토큰)
       3. Retrieval에 reranker 추가

사용자: 검색 실패 케이스의 trace를 자세히 보여줘.

Genie: 검색 실패 12건의 MLflow Trace를 분석합니다...

       [Trace 1] 질문: "반품 정책은?"
         → Retriever: "배송 정책" 문서 3개 반환 (관련성 0.3)
         → 원인: "반품"과 "배송"이 같은 임베딩 공간에 위치
         → 제안: 반품 관련 문서에 키워드 메타데이터 추가
```

{% hint style="warning" %}
MLflow 관련 기능은 **Chat 모드에서만**사용 가능합니다. 복잡한 분석이 필요하면 Notebook으로 이동하여 Agent 모드를 활용하세요.
{% endhint %}

---

## 시나리오별 권장 모드

| 시나리오 | 권장 모드 | 이유 |
|----------|----------|------|
| 간단한 쿼리 작성 | Chat | 1회 응답으로 충분 |
| 코드 설명/학습 | Chat | 대화형 Q&A에 적합 |
| EDA 수행 | Agent | 여러 셀을 자동 생성/실행 |
| ML 파이프라인 구축 | Agent | 다단계 워크플로 자동화 |
| 대시보드 전체 생성 | Agent | SQL + 시각화 + 레이아웃 자동 구성 |
| SDP 파이프라인 생성 | Agent | Bronze-Silver-Gold 전체 구조 생성 |
| 코드 디버깅 | Chat 또는 Quick Fix | 특정 오류에 대한 즉시 대응 |
| 코드 최적화 | Chat (`/optimize`) | 기존 코드 분석 후 개선 제안 |
