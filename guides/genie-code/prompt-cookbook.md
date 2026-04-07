# Genie Code 프롬프트 쿡북

> **최종 업데이트**: 2026-04-07

---

## 이 가이드의 목적

Genie Code는 Databricks 워크스페이스에 내장된 자율형 AI 파트너입니다. 하지만 **"뭘 시킬 수 있는지"** 를 모르면 그 잠재력의 10%도 활용하지 못합니다.

이 페이지는 Databricks의 **모든 주요 기능 영역** 에서 Genie Code에게 요청할 수 있는 자연어 프롬프트를 체계적으로 정리한 **실전 레시피북** 입니다. 각 영역별로 "이런 것도 되나요?"라는 질문에 구체적인 프롬프트 예시로 답합니다.

{% hint style="info" %}
모든 프롬프트는 **Agent 모드** 에서 사용하는 것을 기본으로 합니다. Chat 모드에서만 사용해야 하는 경우 별도로 표시했습니다. Agent 모드에서 Genie Code는 계획 수립 → 코드 생성 → 실행 → 결과 확인 → 오류 수정을 **자율적으로 반복** 합니다.
{% endhint %}

### 효과적인 프롬프트의 3가지 원칙

Genie Code에게 요청할 때 다음 원칙을 기억하면 응답 품질이 크게 향상됩니다:

| 원칙 | 설명 | 예시 |
|------|------|------|
| **`@` 참조로 컨텍스트 제공** | 테이블을 자연어로 언급하지 말고 `@catalog.schema.table` 형태로 직접 참조 | "매출 테이블에서..." → "`@sales.prod.orders` 에서..." |
| **목표 + 제약 조건 명시** | 단계별 지시 대신 최종 목표와 지켜야 할 제약만 전달 | "PySpark만 사용하고, 결과를 Delta 테이블로 저장해줘" |
| **출력 형태 지정** | 원하는 결과물의 형태를 구체적으로 명시 | "인사이트를 마크다운으로 요약하고, 차트 3개를 포함해줘" |

{% hint style="tip" %}
**프롬프트는 지시서가 아니라 계약서처럼 작성하세요.** "1번 해, 2번 해, 3번 해"보다 "최종 결과물은 이것이고, 이 조건을 지켜"가 훨씬 효과적입니다. Agent는 실행 계획을 스스로 수립하므로, 목표만 명확하면 최적의 경로를 알아서 찾습니다.
{% endhint %}

---

## 1. 가상 데이터 생성 (Synthetic Data Generation)

데모, 테스트, PoC를 위한 샘플 데이터를 Genie Code로 빠르게 생성할 수 있습니다. 테이블 스키마를 직접 정의하거나, 기존 테이블의 패턴을 참조하여 유사한 데이터를 만들 수 있습니다.

### 기본 프롬프트

```
전자상거래 분석용 샘플 데이터를 생성해줘.
- customers (10,000행): 고객 ID, 이름, 지역, 가입일, 등급
- orders (50,000행): 주문 ID, 고객 ID, 주문일, 금액, 상태
- products (500행): 제품 ID, 카테고리, 가격, 제조사
모든 테이블을 my_catalog.sandbox에 Delta 테이블로 저장해줘.
```

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **IoT 센서 데이터** | "공장 설비 모니터링용 IoT 센서 데이터를 생성해줘. 온도, 진동, 압력 센서 100개, 1분 간격, 30일치 데이터. 10% 정도 이상치를 포함하고, 일부 센서는 점진적으로 값이 증가하는 패턴(고장 징후)을 넣어줘." |
| **금융 거래 데이터** | "신용카드 거래 데이터를 생성해줘. 100만 건, 정상 거래 97%, 사기 거래 3%. 사기 거래는 심야 시간대, 고액, 해외 가맹점 패턴을 포함해줘." |
| **의료 데이터** | "환자 진료 기록 샘플 데이터를 만들어줘. 환자 5,000명, 진료 기록 50,000건. 진단코드(ICD-10), 처방, 입퇴원일, 보험 정보를 포함하고, PII는 Faker로 가명 처리해줘." |
| **기존 테이블 기반** | "@prod.sales.orders 테이블의 스키마와 데이터 분포를 분석해서 동일한 패턴의 테스트 데이터 10,000행을 dev.sandbox.orders_test에 생성해줘." |
| **시계열 데이터** | "주식 시장 데이터를 생성해줘. 종목 50개, 일별 OHLCV(시가/고가/저가/종가/거래량), 5년치. 상승장, 하락장, 횡보장 패턴을 섞어줘." |
| **다국어 텍스트** | "고객 리뷰 데이터를 생성해줘. 한국어 60%, 영어 30%, 일본어 10%. 긍정/부정/중립 분류 라벨과 별점(1~5)을 포함해줘." |

### 고급 프롬프트

```
@prod.retail.transactions 테이블의 통계적 특성(컬럼별 분포, 상관관계, 결측치 비율)을
분석하고, 동일한 통계적 특성을 유지하면서 PII가 제거된 합성 데이터 100,000행을 생성해줘.
원본과 합성 데이터의 분포 비교 차트도 만들어줘.
```

{% hint style="info" %}
Genie Code는 PySpark, Pandas, Faker, dbldatagen 등의 라이브러리를 활용하여 데이터를 생성합니다. 대용량(100만 행 이상) 생성 시 `"Spark의 분산 처리를 활용해줘"` 라고 명시하면 dbldatagen 기반 코드가 생성되어 클러스터 리소스를 효율적으로 사용합니다.
{% endhint %}

---

## 2. 데이터 파이프라인 구축 (Lakeflow / SDP)

Genie Code의 **가장 강력한 기능 영역** 중 하나입니다. Lakeflow Pipelines Editor에서 Agent 모드를 사용하면, Bronze → Silver → Gold 전체 Medallion 아키텍처 파이프라인을 한 번의 프롬프트로 생성할 수 있습니다. 파이프라인 파일 생성, 편집, 실행, 오류 수정까지 자율적으로 수행합니다.

### 기본 프롬프트

```
my_catalog.my_schema의 transactions와 customers 테이블을 사용하여
사기 탐지를 위한 Medallion 아키텍처 파이프라인을 빌드하고 실행해줘.
```

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **전체 Medallion 구축** | "S3의 raw_events 데이터를 Auto Loader로 수집하고, Bronze → Silver(정제/조인) → Gold(집계) 파이프라인을 SDP로 만들어줘. 데이터 품질 규칙도 각 레이어에 추가해줘." |
| **CDC 파이프라인** | "@raw.cdc_events 테이블에서 CDC(Change Data Capture) 데이터를 읽어서 SCD Type 2로 고객 이력을 관리하는 SDP 파이프라인을 만들어줘." |
| **Auto Loader 수집** | "S3 버킷 s3://my-bucket/logs/ 에서 JSON 로그를 Auto Loader로 수집하고, 중첩 JSON을 자동으로 플랫닝하는 Bronze 테이블을 만들어줘." |
| **데이터 품질 규칙** | "@silver.orders 파이프라인에 다음 품질 규칙을 추가해줘: 1) order_amount > 0, 2) order_date는 미래가 아닐 것, 3) customer_id가 null이 아닐 것. 위반 행은 격리 테이블로 분리해줘." |
| **기존 파이프라인 설명** | "이 파이프라인의 모든 단계를 설명해줘." |
| **파이프라인 오류 수정** | "이 파이프라인의 실패를 수정해줘." |
| **증분 처리 전환** | "이 배치 파이프라인을 Structured Streaming 기반 증분 처리로 전환해줘. 워터마크와 중복 제거 로직도 추가해줘." |

### 고급 프롬프트

```
다음 요구사항에 맞는 Lakeflow SDP 파이프라인을 만들어줘:

[데이터 소스]
- S3: s3://data-lake/raw/clickstream/ (JSON, 시간별 파티션)
- Kafka: broker01:9092 토픽 user_events

[파이프라인 구조]
- Bronze: Auto Loader + Kafka 수집, 원본 보존
- Silver: 두 소스 조인, 세션화(30분 비활동 기준), PII 마스킹
- Gold: 일별 활성 사용자(DAU), 세션당 평균 페이지뷰, 전환율

[품질 규칙]
- Bronze: 스키마 검증 (필수 필드 존재)
- Silver: timestamp 유효성, user_id NOT NULL
- Gold: DAU는 음수 불가

데이터 품질 위반은 quarantine 테이블로 분리해줘.
```

{% hint style="warning" %}
파이프라인 생성 시 Genie Code는 Lakeflow Pipelines Editor에서 **파일을 직접 생성하고 실행** 합니다. 프로덕션 카탈로그를 대상으로 할 때는 반드시 Agent가 표시하는 계획을 검토한 후 승인하세요. 개발/테스트 시에는 `"sandbox 카탈로그에만 저장해줘"` 제약을 추가하는 것이 안전합니다.
{% endhint %}

---

## 3. AI/BI 대시보드 생성 (Dashboards)

Genie Code Agent 모드에서 대시보드를 생성하면, 데이터셋 생성 → SQL 작성 → 시각화 유형 선택 → 위젯 배치 → 필터 설정까지 **전체 과정을 자동화** 합니다. 손으로 그린 스케치 이미지를 첨부해서 대시보드를 만들 수도 있습니다.

### 기본 프롬프트

```
@sales.prod.transactions 테이블을 분석하고
매출 성과를 보여주는 대시보드를 만들어줘.
```

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **경영진 대시보드** | "@sales_data를 사용해서 경영진 보고용 대시보드를 만들어줘. 총매출/주문수/평균객단가 KPI 카드, 월별 매출 추이 라인차트, 지역별 매출 비교 바차트, 상위 10 제품 테이블을 포함해줘." |
| **운영 모니터링** | "@system.billing.usage 데이터로 Databricks 비용 모니터링 대시보드를 만들어줘. 일별 DBU 소비 추이, 워크스페이스별 비용 분포, 가장 비싼 job Top 10을 보여줘." |
| **고객 분석** | "@customers와 @orders를 조인해서 고객 분석 대시보드를 만들어줘. 리텐션율, 이탈률, 고객 생애가치(LTV) 분포, 코호트 분석을 포함해줘." |
| **시각화 추가** | "이 대시보드에 시간대별 매출 추이를 보여주는 라인 차트를 추가해줘." |
| **필터 추가** | "대시보드 전체에 날짜 범위 필터와 지역 선택 필터를 추가해줘." |
| **멀티페이지** | "지역별 성과를 보여주는 새 페이지를 추가해줘." |
| **레이아웃 조정** | "시각화들을 2열 레이아웃으로 정리해줘." |
| **데이터셋 생성** | "@sales_transactions에서 주별/제품별 매출 집계 데이터셋을 만들어줘." |
| **스케치 기반 생성** | (이미지 첨부 후) "이 스케치를 기반으로 대시보드를 만들어줘. 왼쪽 상단은 KPI 카드, 오른쪽은 추이 차트, 하단은 테이블이야." |

### 고급 프롬프트

```
다음 요구사항에 맞는 영업 성과 대시보드를 만들어줘:

[데이터 소스]
- @analytics.sales.daily_metrics
- @analytics.sales.customer_segments
- @analytics.sales.product_performance

[페이지 1: 요약]
- KPI 카드: 총매출(전월 대비 %), 신규 고객 수, 평균 객단가, 전환율
- 월별 매출 추이 (전년 동기 비교 오버레이)
- 지역별 매출 히트맵

[페이지 2: 제품 분석]
- 카테고리별 매출 비교 (바 차트)
- 상위 20 제품 테이블 (매출, 마진율, 재고 회전율)
- 제품 카테고리 파이 차트

[필터]
- 날짜 범위 (기본값: 이번 달)
- 지역 선택 (다중 선택)
- 제품 카테고리 (다중 선택)

대시보드 이름은 'Q2 2026 영업 성과'로 설정해줘.
```

{% hint style="tip" %}
**스케치 기반 생성** 이 매우 강력합니다. 화이트보드에 그린 대시보드 레이아웃을 사진으로 찍어 Genie Code에 첨부하면, 스케치의 배치를 해석하여 실제 대시보드를 생성합니다. 고객 미팅에서 아이디어를 바로 프로토타입으로 전환하는 데 매우 효과적입니다.
{% endhint %}

---

## 4. Genie Space 활용 (MCP 연동)

Genie Code에서 MCP(Model Context Protocol)를 통해 Genie Space를 도구로 연동하면, **코드를 작성하면서 동시에 Genie Space에 자연어 질의** 를 할 수 있습니다. 또한 Genie Space 구성을 위한 데이터 준비 작업을 Genie Code로 자동화할 수 있습니다.

### Genie Space 연동 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **Genie Space 데이터 준비** | "@raw.orders와 @raw.customers를 조인하여 Genie Space용 분석 뷰를 만들어줘. 비기술 사용자가 자연어로 질의할 수 있도록 모든 컬럼에 한국어 COMMENT를 추가해줘." |
| **메트릭 뷰 생성** | "영업팀 Genie Space에서 사용할 표준 KPI를 정의하는 뷰를 만들어줘. 총매출, 순매출, 주문 수, 평균 객단가, 반품률을 포함해줘." |
| **품질 기준 뷰** | "경영진이 Genie Space에서 '이번 달 매출은?' 같은 질문을 할 때 정확한 답을 주도록, 회계 기준에 맞는 매출 집계 뷰를 만들어줘. 세금, 할인, 반품을 정확히 반영해줘." |
| **MCP를 통한 질의** | "(MCP Genie Space 연동 후) Genie Space에 '지난 주 상위 5개 고객의 매출은 얼마야?'라고 질문하고, 결과를 이 노트북에 가져와서 추가 분석해줘." |

{% hint style="info" %}
Genie Code가 Genie Space를 **직접 생성** 하지는 않습니다. 하지만 Genie Space에 추가할 **뷰, 메트릭 테이블, 컬럼 설명** 을 자동으로 생성할 수 있으므로, Genie Space 구축의 가장 시간이 많이 걸리는 데이터 준비 단계를 크게 가속합니다. MCP로 Genie Space를 연동하면 Agent 모드에서 Space에 질의도 가능합니다.
{% endhint %}

---

## 5. Databricks Apps 개발 코드 생성

Genie Code로 Databricks Apps(Streamlit, Gradio, FastAPI 등)의 **코드를 생성** 할 수 있습니다. 앱 로직, UI 구성, 데이터 연결 코드를 노트북에서 작성한 후, 앱으로 배포하는 워크플로에 활용됩니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **Streamlit 앱** | "@analytics.customer_360 테이블을 조회하는 Streamlit 대시보드 앱 코드를 만들어줘. 고객 검색, 세그먼트별 필터링, 매출 추이 차트를 포함해줘. Databricks SQL Warehouse에 연결하는 코드도 포함해줘." |
| **Gradio 챗봇** | "RAG 체인을 호출하는 Gradio 챗봇 UI 코드를 만들어줘. 모델 서빙 엔드포인트 호출, 대화 히스토리 유지, 소스 문서 표시 기능을 포함해줘." |
| **FastAPI 백엔드** | "@prod.ml.predictions 테이블에서 예측 결과를 조회하는 REST API를 FastAPI로 만들어줘. GET /predictions/{customer_id} 엔드포인트와 인증 미들웨어를 포함해줘." |
| **app.yaml 생성** | "이 Streamlit 앱을 Databricks Apps로 배포하기 위한 app.yaml 설정 파일을 만들어줘. SQL Warehouse와 서빙 엔드포인트를 리소스로 추가해줘." |

### 고급 프롬프트

```
다음 요구사항의 Databricks App 코드를 만들어줘:

[프레임워크] Streamlit
[기능]
1. 사이드바: 날짜 범위, 제품 카테고리 필터
2. 메인 페이지: KPI 카드 3개 + 매출 추이 차트 + 제품별 비교 차트
3. 두 번째 탭: @prod.ml.churn_predictions의 이탈 위험 고객 목록
4. SQL Warehouse 연결 (databricks-sql-connector 사용)

[제약 조건]
- OAuth 인증 사용 (사용자 권한으로 데이터 접근)
- 한국어 UI
- 에러 핸들링 포함
```

{% hint style="warning" %}
Genie Code는 앱 **코드를 생성** 하지만, Databricks Apps 플랫폼에 **직접 배포** 하지는 않습니다. 생성된 코드를 워크스페이스 파일이나 Git 리포지토리에 저장한 후, Databricks Apps UI 또는 CLI로 배포해야 합니다.
{% endhint %}

---

## 6. 노트북 생성 및 구성 (Notebooks)

Genie Code의 **핵심 작업 공간** 입니다. 노트북에서 Agent 모드를 사용하면, 셀 생성/실행/수정을 자율적으로 수행하며 완성된 분석 노트북을 만들어냅니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **EDA 노트북** | "@sales.prod.transactions 테이블에 대해 종합 EDA를 수행해줘. 기본 통계, 결측치 분석, 분포 시각화, 상관관계 분석, 이상치 탐지를 포함하고, 각 단계마다 인사이트를 마크다운으로 요약해줘." |
| **데이터 정제 노트북** | "@raw.events 테이블을 정제하는 노트북을 만들어줘. 중복 제거, null 처리, 날짜 포맷 통일, 이상치 제거를 순서대로 수행하고, 각 단계에서 변환 전후 건수를 표시해줘." |
| **비교 분석** | "@prod.sales.orders_2025와 @prod.sales.orders_2024를 비교 분석해줘. 매출, 주문수, 고객수의 YoY 변화와 주요 드라이버를 식별해줘." |
| **노트북 정리** | "이 노트북의 각 셀에 의미 있는 이름을 붙여줘." |
| **요약 셀 생성** | "이 노트북의 분석 결과를 요약하는 새 셀을 만들어줘." |
| **코드 문서화** | (셀 선택 후) "/doc" |
| **코드 설명** | (셀 선택 후) "/explain" |
| **코드 최적화** | (셀 선택 후) "/optimize" |
| **단위 테스트** | (함수 선택 후) "/test" |
| **테이블 검색** | "/findTables 고객 거래 데이터 관련 테이블 찾아줘" |

### 고급 프롬프트

```
@prod.retail.transactions 테이블을 기반으로
완전한 RFM(Recency, Frequency, Monetary) 분석 노트북을 만들어줘.

1. 데이터 로드 및 기본 검증
2. RFM 점수 계산 (각 지표별 5분위)
3. RFM 기반 고객 세그먼트 정의 (Champions, Loyal, At Risk 등)
4. 세그먼트별 특성 비교 시각화
5. 각 세그먼트에 대한 마케팅 전략 제안
6. 결과를 analytics.marketing.rfm_segments 테이블로 저장

PySpark를 사용하고, 차트는 plotly로 만들어줘.
각 셀에 한국어 마크다운 설명을 포함해줘.
```

---

## 7. MLOps 워크플로 (모델 학습 → 평가 → 배포)

Genie Code는 전체 ML 라이프사이클을 자동화할 수 있습니다. 데이터 준비, 피처 엔지니어링, 모델 학습, 하이퍼파라미터 튜닝, 모델 평가, MLflow 로깅까지 Agent 모드에서 자율적으로 수행합니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **분류 모델** | "@customer_data 데이터셋으로 고객 이탈 예측 모델을 만들어줘. target은 'churned' 컬럼이야. 정확도와 AUC로 평가하고, MLflow에 기록해줘." |
| **회귀 모델** | "@housing_prices 데이터셋으로 주택 가격 예측 회귀 모델을 만들어줘. 하이퍼파라미터 튜닝도 수행해서 예측 오차를 개선해줘." |
| **클러스터링** | "@sales_leads 데이터셋으로 클러스터링 모델을 만들어서 고객 세그먼트를 식별해줘. 각 클러스터의 특성을 요약해줘." |
| **시계열 예측** | "@incidents 데이터셋으로 향후 2주간 일별 사건 수를 예측해줘. 예측 결과를 데이터 테이블과 인터랙티브 차트로 보여줘." |
| **피처 엔지니어링** | "이 데이터셋을 모델 학습에 적합하게 전처리해줘. 범주형 인코딩, 결측치 처리, 스케일링, 피처 선택을 수행해줘." |
| **하이퍼파라미터 튜닝** | "이 XGBoost 모델의 하이퍼파라미터를 Optuna로 튜닝해줘. 50회 시도하고, 최적 파라미터와 성능 개선폭을 보고해줘." |
| **모델 비교** | "LogisticRegression, RandomForest, XGBoost, LightGBM 4가지 모델을 학습하고 비교해줘. 각 모델의 AUC, 정밀도, 재현율을 표로 정리하고, 최적 모델을 MLflow에 등록해줘." |
| **피처 중요도** | "학습된 모델의 피처 중요도를 시각화하고, 상위 10개 피처의 비즈니스 의미를 설명해줘." |

### 고급 프롬프트 — 전체 MLOps 파이프라인

```
다음 요구사항으로 전체 MLOps 워크플로를 구축해줘:

[데이터] @prod.manufacturing.sensor_readings
[목표] 설비 고장 예측 (failure 컬럼이 target)

[수행 단계]
1. EDA: 데이터 특성 파악, 클래스 불균형 확인
2. 피처 엔지니어링: 롤링 통계(1h, 6h, 24h), lag 피처, 피처 상호작용
3. 모델 학습: XGBoost + LightGBM + Random Forest 비교
4. 클래스 불균형 처리: SMOTE 또는 클래스 가중치 적용
5. 하이퍼파라미터 튜닝: 최적 모델에 대해 Optuna 100회
6. 평가: Precision/Recall/F1/AUC + 혼동 행렬 시각화
7. MLflow 로깅: 모든 실험, 최적 모델 등록

[제약 조건]
- PySpark로 피처 엔지니어링
- 모델 학습은 sklearn 또는 xgboost
- 한국어 주석
```

---

## 8. 모델 서빙 & 엔드포인트 관리

모델 서빙 페이지에서 Genie Code를 사용하면, 엔드포인트의 **건강 상태 확인, 성능 분석, 장애 진단** 을 할 수 있습니다. 현재는 **읽기 전용 어드바이저** 역할로, 구성 변경은 직접 수행해야 합니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **헬스 체크** | "이 엔드포인트의 건강 상태를 확인해줘." |
| **구성 검토** | "이 엔드포인트가 올바르게 구성되어 있는지 확인해줘." |
| **스케일링 검토** | "이 엔드포인트의 스케일링 구성을 검토해줘." |
| **배포 실패 진단** | "/diagnose" 또는 "왜 배포가 실패했어?" |
| **레이턴시 분석** | "왜 레이턴시가 이렇게 높은 거야?" |
| **레이턴시 스파이크** | "오늘 아침의 레이턴시 스파이크를 분석해줘." |
| **최근 성능** | "지난 24시간 성능 메트릭을 보여줘." |
| **구성 변경 비교** | "대기 중인 구성에서 뭐가 변경되었어?" |
| **에러 패턴** | "지난 주의 에러 패턴을 분석해줘." |
| **최근 요청 확인** | "이 엔드포인트에 대한 최근 요청을 보여줘." |
| **동시성 검토** | "이 동시성 설정이 프로덕션에 적합한가?" |

{% hint style="warning" %}
모델 서빙 영역의 Genie Code는 **읽기 전용 어드바이저** 입니다. 엔드포인트 구성을 변경하거나 배포를 직접 수행하지는 않습니다. 최적화 권장사항을 제시하면 사용자가 직접 적용해야 합니다. 현재 **Custom 모델 서빙 엔드포인트** 에서만 지원됩니다.
{% endhint %}

---

## 9. GenAI / RAG 개발

노트북에서 RAG 체인 구축, 프롬프트 엔지니어링, 벡터 검색 설정, 에이전트 디버깅까지 GenAI 워크플로 전반을 지원합니다. MLflow 페이지에서는 Trace 분석과 품질 평가를 수행합니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **RAG 체인 구축** | "@prod.docs.knowledge_base 테이블을 기반으로 RAG 체인을 만들어줘. Vector Search 인덱스 조회 → 프롬프트 구성 → LLM 호출 → 응답 생성 파이프라인을 LangChain으로 구현해줘." |
| **임베딩 생성** | "@raw.documents 테이블의 text 컬럼에 대해 임베딩을 생성하고, Vector Search 인덱스에 저장하는 코드를 만들어줘." |
| **청킹 최적화** | "이 문서 데이터에 대해 여러 청킹 전략(고정 크기, 문장 기반, 의미 기반)을 비교하고, 검색 품질이 가장 높은 전략을 추천해줘." |
| **프롬프트 최적화** | "이 RAG 체인의 시스템 프롬프트를 개선해줘. 환각을 줄이고, 소스를 인용하며, 모르는 것은 모른다고 답하도록 해줘." |
| **Trace 분석** | "이 에이전트의 tool calling에서 문제가 있는 trace를 찾아줘." |
| **실패 패턴** | "지난 주 가장 흔한 실패 패턴이 뭐야?" |
| **사용자 만족도** | "피드백 점수가 가장 낮은 세션은 어떤 거야?" |
| **토큰 사용량** | "토큰 사용량 패턴과 비용을 분석해줘." |
| **레이턴시 분석** | "P50/P95/P99 레이턴시를 분석하고, 병목 지점을 찾아줘." |
| **평가 실행** | "이 RAG 체인에 대해 faithfulness, relevance, toxicity 평가를 실행하고, 저품질 케이스의 원인을 분류해줘." |

### 고급 프롬프트

```
다음 요구사항으로 RAG 기반 Q&A 시스템을 구축해줘:

[데이터] @prod.docs.product_manuals (PDF 파싱된 텍스트)

[구축 단계]
1. 문서 청킹 (500 토큰, 50 토큰 오버랩)
2. 임베딩 생성 (Databricks Foundation Model)
3. Vector Search 인덱스 생성
4. LangChain RAG 체인 구성
5. 평가 데이터셋 20개 Q&A 쌍 생성
6. MLflow로 평가 실행 (faithfulness, relevance)
7. 결과 분석 및 개선 제안

시스템 프롬프트는 한국어로, 소스 문서를 반드시 인용하도록 설정해줘.
```

---

## 10. Unity Catalog 작업

Genie Code는 Unity Catalog의 메타데이터를 깊이 이해하며, 테이블/뷰/함수의 생성, 관리, 메타데이터 작성을 지원합니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **테이블 생성** | "다음 스키마로 Delta 테이블을 만들어줘: customer_id (BIGINT), name (STRING), email (STRING), signup_date (DATE). Liquid Clustering을 signup_date로 설정해줘." |
| **뷰 생성** | "@raw.orders와 @raw.customers를 조인하여 주문 상세 뷰를 만들어줘. 컬럼별 한국어 COMMENT를 추가해줘." |
| **메타데이터 작성** | "@prod.sales 스키마의 모든 테이블에 대해 테이블 설명과 컬럼 설명(COMMENT)을 자동 생성해줘. 컬럼 이름과 샘플 데이터를 기반으로 의미를 추론해줘." |
| **테이블 검색** | "/findTables 고객 구매 이력 관련 테이블" |
| **스키마 분석** | "@prod.analytics 스키마에 있는 모든 테이블의 구조, 행 수, 최종 업데이트 시간을 정리해줘." |
| **테이블 최적화** | "@prod.sales.orders 테이블에 OPTIMIZE와 VACUUM을 실행하고, Z-ORDER 적용이 필요한 컬럼을 추천해줘." |
| **리니지 분석** | "@gold.revenue_summary 테이블이 어떤 원본 테이블에서 왔는지 데이터 리니지를 추적해줘." |

---

## 11. Structured Streaming

노트북에서 Structured Streaming 코드를 생성하고, 스트리밍 파이프라인을 구성할 수 있습니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **Kafka 수집** | "Kafka 토픽 'user_events' (broker: kafka01:9092)에서 JSON 메시지를 읽어서 Bronze 테이블에 저장하는 Structured Streaming 코드를 만들어줘." |
| **윈도우 집계** | "스트리밍 데이터에서 5분 텀블링 윈도우로 이벤트 수를 집계하는 코드를 만들어줘. 워터마크는 10분으로 설정해줘." |
| **스트림-스트림 조인** | "주문 스트림과 결제 스트림을 order_id 기준으로 조인하는 스트림-스트림 조인 코드를 만들어줘." |
| **Auto Loader** | "S3 경로 s3://data/incoming/ 에서 CSV 파일을 Auto Loader로 실시간 수집하는 코드를 만들어줘. 스키마 진화도 처리해줘." |
| **체크포인트 관리** | "이 스트리밍 잡의 체크포인트가 손상된 것 같아. 안전하게 재시작하는 방법을 알려줘." |

---

## 12. Delta Lake 작업

Delta Lake 테이블의 최적화, 유지보수, 고급 기능을 활용하는 코드를 생성합니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **테이블 최적화** | "@prod.sales.orders 테이블을 OPTIMIZE하고, order_date와 region으로 Z-ORDER를 적용해줘." |
| **VACUUM** | "@prod.sales.orders의 오래된 파일을 정리해줘. 7일 이전 파일만 삭제하고, 실행 전에 dry-run으로 정리 대상을 먼저 보여줘." |
| **타임 트래블** | "@prod.sales.orders 테이블의 이력을 확인하고, 3일 전 버전의 데이터와 현재 데이터를 비교해줘. 변경된 행 수를 알려줘." |
| **Liquid Clustering** | "@prod.logs.events 테이블에 Liquid Clustering을 적용해줘. 자주 필터링되는 컬럼을 분석해서 최적의 클러스터링 키를 추천해줘." |
| **스키마 진화** | "@bronze.raw_data 테이블에 새 컬럼을 추가하는 스키마 진화 코드를 만들어줘." |
| **MERGE** | "@staging.daily_updates의 데이터를 @prod.master_table에 MERGE(upsert)하는 코드를 만들어줘. customer_id가 매칭 키이고, 변경된 행만 업데이트해줘." |

---

## 13. Job 스케줄링 & 워크플로

노트북에서 Job 실행 코드를 생성하거나, 워크플로 구성에 필요한 코드를 작성할 수 있습니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **노트북 스케줄링 코드** | "이 노트북을 매일 오전 6시에 실행하는 Job을 Databricks SDK로 생성하는 코드를 만들어줘." |
| **멀티태스크 워크플로** | "3개 노트북을 순차 실행하는 워크플로 Job 생성 코드를 만들어줘: 01_ingest → 02_transform → 03_aggregate. 각 태스크 사이에 의존성을 설정해줘." |
| **실패 알림** | "Job 실패 시 Slack 웹훅으로 알림을 보내는 코드를 만들어줘." |
| **실행 모니터링** | "현재 실행 중인 Job의 상태를 확인하는 코드를 만들어줘." |
| **재시도 로직** | "이 노트북에 실패 시 3회 재시도하는 로직을 추가해줘. 재시도 간격은 지수 백오프로 해줘." |

---

## 14. 데이터 품질 & 모니터링

데이터 테이블의 건강 상태를 점검하고, 이상을 탐지하는 노트북을 자동 생성합니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **종합 품질 점검** | "@prod.sales.orders의 데이터 품질을 종합 점검해줘. null 비율, 중복, 날짜 유효성, 금액 범위를 체크하고, 이상이 있으면 보고서를 만들어줘." |
| **이상 탐지** | "@prod.metrics.daily_kpi에서 최근 7일 데이터의 이상치를 탐지해줘. Z-score와 IQR 방법을 모두 사용하고, 결과를 비교해줘." |
| **데이터 프로파일링** | "@raw.events 테이블의 모든 컬럼에 대해 데이터 프로파일을 생성해줘. 분포, 유니크값 수, 최빈값, 결측률을 포함해줘." |
| **SLA 모니터링** | "@bronze.transactions의 데이터 신선도를 확인해줘. 마지막 데이터가 1시간 이상 지연되면 경고를 표시해줘." |
| **드리프트 감지** | "@prod.features.customer_features의 피처 분포를 1주 전과 비교해서 드리프트가 있는 컬럼을 식별해줘." |

---

## 15. 코드 마이그레이션 & 변환

레거시 코드를 Databricks 환경에 최적화된 코드로 변환합니다. Chat 모드에서 사용하는 것이 안전합니다.

### 시나리오별 프롬프트 (Chat 모드 권장)

| 시나리오 | 프롬프트 |
|----------|---------|
| **Pandas → PySpark** | "이 pandas 코드를 PySpark로 변환해줘. 분산 처리에 최적화하고, apply() 대신 내장 함수를 사용해줘." |
| **SAS → PySpark** | "이 SAS PROC SQL을 PySpark SQL로 변환해줘." |
| **Hive → Unity Catalog** | "이 Hive DDL을 Unity Catalog 호환 DDL로 변환해줘. Managed Table 형태로 바꾸고, Delta 포맷을 적용해줘." |
| **레거시 SQL** | "이 Oracle PL/SQL을 Databricks SQL로 변환해줘. 구문 차이를 설명하고, 최적화도 적용해줘." |
| **R → PySpark** | "이 R dplyr 코드를 PySpark DataFrame API로 변환해줘." |
| **Spark 2 → Spark 3** | "이 Spark 2.x 코드를 Spark 3.x + Databricks 런타임 15.x에 맞게 업그레이드해줘. deprecated API가 있으면 대체 API를 사용해줘." |

---

## 16. 디버깅 & 오류 진단

Genie Code의 **가장 즉각적인 생산성 향상** 기능입니다. 복잡한 오류를 자동으로 분석하고 수정 방안을 제시합니다.

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **Quick Fix** | (오류 발생 시 자동으로 표시되는 Quick Fix 버튼 클릭) |
| **오류 진단** | "Diagnose with Genie" 버튼 클릭 또는 "/fix" |
| **OOM 분석** | "이 코드가 OutOfMemoryError를 일으키는 이유를 분석하고, 메모리 사용을 줄이는 방법을 제안해줘." |
| **성능 분석** | (느린 코드 선택 후) "/optimize" |
| **환경 오류** | "/repairEnvironment" |
| **권한 오류** | "이 AccessDenied 오류를 해결하려면 어떤 권한이 필요한지 알려줘." |
| **Spark 오류** | "이 AnalysisException의 원인을 분석하고 수정해줘." |

---

## 17. MCP 외부 도구 연동

Agent 모드에서 MCP 서버를 통해 외부 도구를 호출할 수 있습니다. 코딩 작업과 커뮤니케이션/문서화를 한 공간에서 처리합니다.

### 지원되는 MCP 서버 유형

| 서버 유형 | 용도 | 예시 |
|-----------|------|------|
| **Unity Catalog Functions** | 사전 정의된 SQL 함수 실행 | 비즈니스 로직 캡슐화 |
| **Vector Search Indexes** | 문서 검색 | RAG 체인에서 관련 문서 조회 |
| **Genie Spaces** | 자연어 데이터 질의 | 분석 중 비즈니스 지표 확인 |
| **UC Connections** | 외부 MCP 서버 연동 | Jira, GitHub, Slack, Confluence |
| **Databricks Apps** | 커스텀 도구 | 내부 API, 자체 개발 도구 |

### 시나리오별 프롬프트

| 시나리오 | 프롬프트 |
|----------|---------|
| **Slack 알림** | "이 분석 결과를 요약해서 #data-team Slack 채널에 보내줘." |
| **Jira 티켓** | "이 데이터 품질 이슈로 Jira ES 티켓을 생성해줘. 심각도는 High, 재현 단계와 영향 범위를 포함해줘." |
| **GitHub 코드** | "GitHub 리포지토리에서 이 함수의 최신 버전을 가져와줘." |
| **Confluence 문서** | "이 분석 결과를 Confluence 페이지로 작성해줘." |
| **Vector Search** | "Vector Search에서 '반품 정책'과 관련된 문서를 검색해줘." |

{% hint style="info" %}
MCP 서버는 **최대 20개 도구** 까지 연동할 수 있으며, **Agent 모드에서만** 작동합니다. Genie Code 설정(톱니바퀴 아이콘) → MCP Servers에서 서버를 추가하고 개별 도구를 활성화/비활성화할 수 있습니다.
{% endhint %}

---

## 18. Agent Skills (도메인 확장)

Agent Skills를 통해 조직 고유의 워크플로를 Genie Code에 학습시킬 수 있습니다. SKILL.md 파일로 정의하면, 관련 작업 시 자동으로 로드됩니다.

### Skill 활용 예시

| Skill 예시 | 설명 | 프롬프트 |
|------------|------|---------|
| **PII 마스킹** | 개인정보 처리 표준 | "이 테이블의 PII를 마스킹해줘"` → Skill이 자동 로드되어 조직 표준에 맞게 처리 |
| **데이터 품질 표준** | 회사별 검증 규칙 | "이 테이블의 품질을 검사해줘"` → 조직의 품질 기준이 자동 적용 |
| **ML 워크플로** | 팀의 모델 학습 절차 | "새 모델을 학습해줘"` → 표준 실험 설정, 로깅 규칙이 적용 |
| **ETL 패턴** | 조직의 파이프라인 템플릿 | "수집 파이프라인을 만들어줘"` → 회사 표준 패턴(명명규칙, 품질규칙)이 적용 |

### Skill 구성 방법

```
# Workspace Skill (전체 공유)
Workspace/.assistant/skills/pii-masking/
├── SKILL.md          # 스킬 정의 (이름, 설명, 단계별 가이드)
├── patterns.md       # PII 패턴 목록
└── scripts/
    └── mask_pii.py   # 실행 스크립트

# User Skill (개인용)
/Users/user@company.com/.assistant/skills/my-etl/
├── SKILL.md
└── etl-template.py
```

{% hint style="tip" %}
Skills는 Agent 모드에서만 작동합니다. `@skill-name` 으로 수동 호출하거나, 관련 작업 시 자동으로 로드됩니다. 조직의 코딩 컨벤션, 거버넌스 정책, 도메인 지식을 Skill로 정의하면 모든 팀원이 일관된 품질의 코드를 생성할 수 있습니다.
{% endhint %}

---

## 19. Custom Instructions로 기본 행동 설정

모든 프롬프트에 매번 반복해야 하는 지시사항은 Custom Instructions에 한 번만 설정하면 됩니다.

### 권장 Custom Instructions 예시

```markdown
# 코딩 규칙
- 코드에 한국어 주석을 포함해주세요
- PySpark DataFrame API를 기본으로 사용하세요 (pandas 변환 최소화)
- 변수명은 snake_case, 클래스명은 PascalCase
- 차트는 plotly를 기본으로 사용하세요

# 데이터 규칙
- 결과 테이블은 항상 dev.sandbox 카탈로그에 저장하세요
- 프로덕션 테이블을 수정하지 마세요
- 쿼리 실행 전 LIMIT 1000으로 먼저 테스트하세요

# 응답 형식
- 각 분석 단계마다 마크다운 요약을 포함하세요
- MLflow에 모든 실험을 기록하세요
```

Custom Instructions는 두 가지 수준으로 설정됩니다:

| 수준 | 파일 위치 | 관리 주체 |
|------|-----------|----------|
| **사용자 수준** | `/Users/<username>/.assistant_instructions.md` | 개인 |
| **워크스페이스 수준** | `Workspace/.assistant_workspace_instructions.md` | 관리자 |

워크스페이스 수준 설정이 사용자 수준보다 우선합니다. 각 파일의 최대 크기는 20,000자입니다.

---

## 20. Slash Commands 전체 레퍼런스

빠른 작업을 위한 전체 Slash Command 목록입니다. 채팅 입력란에 `/` 를 입력하면 목록이 나타납니다.

| 명령어 | 기능 | 사용 시점 |
|--------|------|----------|
| `/explain` | 선택한 코드를 자연어로 설명 | 동료 코드 리뷰, 레거시 코드 이해 |
| `/fix` | 코드 오류 분석 및 수정 제안 | 실행 오류 발생 시 |
| `/optimize` | 코드 성능 최적화 제안 | 쿼리/코드가 느릴 때 |
| `/test` | 단위 테스트 자동 생성 | 함수 작성 후 |
| `/doc` | 문서/주석(docstring) 자동 생성 | 코드 문서화 시 |
| `/findTables` | Unity Catalog 테이블 검색 | 데이터 탐색 시 |
| `/findQueries` | Unity Catalog 쿼리 검색 | 기존 쿼리 재활용 시 |
| `/prettify` | 코드 가독성 포맷팅 | 코드 정리 시 |
| `/rename` | 셀/요소 이름 제안 | 노트북 정리 시 |
| `/settings` | 노트북 설정 조정 | 환경 설정 변경 시 |
| `/repairEnvironment` | 라이브러리 설치 오류 해결 | 환경 오류 발생 시 |
| `/diagnose` | 복잡한 오류 심층 진단 | 모델 서빙 오류 시 |

---

## 기능 지원 매트릭스

각 Databricks 제품 영역에서 Genie Code가 지원하는 기능을 한눈에 정리합니다. 제품 영역에 따라 사용 가능한 모드와 기능이 다릅니다.

| 기능 영역 | Notebooks | SQL Editor | Dashboards | Pipelines | MLflow | Model Serving |
|-----------|:---------:|:----------:|:----------:|:---------:|:------:|:-------------:|
| **Chat 모드** | O | O | O | O | O | O |
| **Agent 모드** | O | O | O | O | - | O |
| **인라인 자동완성** | O | O | - | O | - | - |
| **Quick Fix** | O | O | - | - | - | - |
| **Diagnose Error** | O | O | - | O | - | O |
| **MCP 연동** | O | - | - | - | - | - |
| **Slash 명령어** | O | O | - | - | - | O |
| **이미지 첨부** | O | - | O | - | - | - |
| **Agent Skills** | O | - | - | - | - | - |

{% hint style="info" %}
이 매트릭스에서 **가장 풍부한 기능** 을 제공하는 영역은 **Notebooks** 입니다. Chat/Agent 모드, 인라인 자동완성, MCP 연동, Skills, 이미지 첨부까지 모든 기능을 사용할 수 있습니다. Genie Code를 최대한 활용하려면 Notebook을 중심으로 작업하세요.
{% endhint %}

---

## 프로덕션 운영 팁

실전에서 Genie Code를 효과적으로 사용하기 위한 핵심 원칙들입니다:

| 원칙 | 설명 | 이유 |
|------|------|------|
| **세션 분리** | 서로 다른 작업(재무 분석 vs 로그 파이프라인)은 New Chat으로 분리 | Agent는 대화 내 결정 트리를 구축하므로, 주제 혼합 시 컨텍스트 혼란 발생 |
| **데이터 제한 우선** | "먼저 1,000행으로 제한해서 로직을 테스트해줘" | 전체 데이터셋 실행 전 로직 검증으로 컴퓨팅 비용 절약 |
| **프로덕션 보호** | "프로덕션 테이블을 수정하지 말고 sandbox에만 저장해줘" | Agent의 자동 실행이 프로덕션 데이터를 변경하는 것을 방지 |
| **루프 감시** | Agent가 같은 접근을 반복하면 즉시 중단 | 실패한 접근을 반복하면 비용만 소모 |
| **탭 유지** | Agent 작업 중 다른 탭으로 전환하지 않기 | 탭 전환 시 Agent가 일시 정지됨 |
| **메타데이터가 핵심** | Unity Catalog의 테이블/컬럼 COMMENT 품질이 응답 품질을 결정 | COMMENT가 없으면 Genie Code가 컬럼 의미를 추측해야 하므로 정확도 하락 |

---

## 참고 자료

### 공식 문서
* [Genie Code 개요](https://docs.databricks.com/aws/en/genie-code/)
* [Genie Code 사용법](https://docs.databricks.com/aws/en/genie-code/use-genie-code)
* [응답 개선 팁](https://docs.databricks.com/aws/en/genie-code/tips)
* [데이터 사이언스용 Agent](https://docs.databricks.com/aws/en/notebooks/ds-agent)
* [파이프라인용 Agent](https://docs.databricks.com/aws/en/ldp/de-agent)
* [대시보드 Agent](https://docs.databricks.com/aws/en/dashboards/manage/dashboard-agent)
* [Agent Observability](https://docs.databricks.com/aws/en/mlflow3/genai/getting-started/genie-code)
* [모델 서빙 Observability](https://docs.databricks.com/aws/en/machine-learning/model-serving/model-serving-genie-code)
* [Agent Skills](https://docs.databricks.com/aws/en/genie-code/skills)
* [MCP 연동](https://docs.databricks.com/aws/en/genie-code/mcp)
* [Custom Instructions](https://docs.databricks.com/aws/en/genie-code/instructions)

### 블로그 & 실전 가이드
* [Genie Code Full Practice Guide (Medium)](https://medium.com/dbsql-sme-engineering/databricks-genie-code-full-practice-guide-f3bcb13596f2)
* [Genie Code Pricing (Medium)](https://medium.com/dbsql-sme-engineering/genie-code-databricks-agentic-ai-the-price-of-intelligence-32a7bc477cba)
* [Two Weeks in Production (SunnyData)](https://www.sunnydata.ai/blog/databricks-genie-code-production-review)
* [Get to Know Genie Code (데모 영상)](https://www.databricks.com/resources/demos/videos/get-know-genie-code)
