# SQL & Analytics 비교

## SQL 엔진 및 BI

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **ANSI SQL 호환** | 완전 호환 | 완전 호환 | PostgreSQL 호환 | GoogleSQL (일부 비표준) | T-SQL 호환 |
| **내장 BI** | AI/BI Dashboard (AI 기반 자동 시각화) | Snowsight | QuickSight | Looker + Looker Studio | Power BI (네이티브 통합) |
| **자연어 분석** | Genie Spaces + Genie Code (SQL+Python 생성/실행) | Cortex Analyst (SQL 전용) | QuickSight Q (제한적) | BigQuery NL Query (제한적) | Copilot in Power BI |
| **외부 BI 연동** | Tableau, Power BI, Looker 등 완전 호환 | 완전 호환 | 완전 호환 | 완전 호환 | Power BI 최적화, 타 BI 가능 |
| **AI 함수 in SQL** | `AI_QUERY`, `AI_GENERATE` 등 SQL 내 AI 호출 | Cortex LLM Functions | 미지원 (별도 서비스) | BigQuery ML (제한적) | 제한적 |
| **캐싱** | Delta Cache + Disk Cache + Result Cache | Result Cache + Local Disk Cache | Result Cache | BigQuery Cache (24h) | Direct Lake + 캐시 |
| **동시성** | SQL Warehouse별 독립, 자동 스케일링 | Multi-cluster Warehouse | Concurrency Scaling (추가 비용) | Slot 기반 | Capacity 기반 |
| **TPC-DS 성능** | 100TB 기준 업계 최고 수준 (Photon) | 상위권 | 상위권 | 상위권 | 상위권 |

{% hint style="info" %}
**Genie Code**: 비즈니스 사용자가 자연어로 "지난달 매출 트렌드를 분석해줘"라고 질문하면, SQL/Python 코드를 자동 생성하고 실행합니다. Cortex Analyst는 SQL만 생성하는 반면, Genie Code는 Python 분석까지 가능합니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: Snowflake는 SQL 중심 워크플로에서 가장 직관적인 사용 경험을 제공하며, Data Sharing이 매우 간편합니다. MS Fabric은 Power BI와의 네이티브 통합이 압도적이고 Direct Lake 모드로 데이터 복사 없이 대시보드를 구성합니다. BigQuery는 프로비저닝 없이 즉시 SQL을 실행할 수 있습니다.
{% endhint %}

---

## SQL Warehouse 아키텍처 상세

### Databricks SQL Warehouse 유형

| 항목 | Serverless SQL Warehouse | Classic SQL Warehouse (Pro) | Classic SQL Warehouse (Classic) |
|---|---|---|---|
| **인프라 관리** | 완전 관리형 (Databricks) | 고객 VPC 내 | 고객 VPC 내 |
| **시작 시간** | 초 단위 (웜 풀) | 분 단위 | 분 단위 |
| **Photon 엔진** | 기본 활성화 | 기본 활성화 (Pro) | 미포함 |
| **자동 스케일링** | 자동 (클러스터 수 조절) | Min/Max 클러스터 설정 | Min/Max 클러스터 설정 |
| **유휴 비용** | Zero (즉시 종료) | Auto-stop 설정 필요 | Auto-stop 설정 필요 |
| **네트워크** | Databricks 관리형 VPC | 고객 VPC (PrivateLink 가능) | 고객 VPC |
| **SQL 기능** | 전체 기능 | 전체 기능 | 기본 SQL만 |
| **Genie/AI 함수** | 지원 | 지원 (Pro) | 미지원 |
| **비용** | DBU 단가 다소 높음, 인스턴스 비용 없음 | DBU 단가 + 인스턴스 비용 | DBU 단가 (낮음) + 인스턴스 비용 |

### SQL Warehouse 크기별 성능 가이드

| Warehouse 크기 | 클러스터 크기 | 권장 사용 시나리오 | 동시 쿼리 수 (목안) |
|---|---|---|---|
| **2X-Small** | 최소 | 개발/테스트, 소규모 ad-hoc | 1-5 |
| **X-Small** | 소규모 | 소규모 팀 분석, 간단한 BI | 5-10 |
| **Small** | 중소규모 | 일반 분석 팀 (10-20명) | 10-20 |
| **Medium** | 중규모 | 대규모 테이블 조인, 복잡 쿼리 | 20-50 |
| **Large** | 대규모 | 대규모 BI 워크로드 | 50-100 |
| **X-Large ~ 4X-Large** | 최대규모 | 엔터프라이즈 BI, 수백 동시 사용자 | 100+ |

{% hint style="info" %}
**크기 선택 팁**: **Serverless SQL Warehouse** 를 사용하면 크기를 고민할 필요 없이 Databricks가 쿼리 복잡도에 따라 자동으로 최적 리소스를 할당합니다. 자동 스케일링도 클러스터 수 기반으로 동시성을 자동 관리합니다.
{% endhint %}

---

## Genie Space vs 경쟁사 자연어 분석

### 자연어 분석 기능 심층 비교

| 항목 | Databricks Genie Spaces + Genie Code | Snowflake Cortex Analyst | BigQuery NL Query | Power BI Copilot | QuickSight Q |
|---|---|---|---|---|---|
| **자연어 → SQL** | 지원 | 지원 | 지원 (제한적) | 지원 | 지원 (제한적) |
| **자연어 → Python** | **지원 (Genie Code 고유)** | 미지원 | 미지원 | 미지원 | 미지원 |
| **코드 실행** | 자동 생성 + 즉시 실행 | SQL 생성만 (실행은 수동) | 쿼리 제안 | 시각화 제안 | 쿼리 실행 |
| **비즈니스 컨텍스트** | Genie Space에 도메인 지식 설정 | Semantic Model (YAML) | 제한적 | Semantic Model | 제한적 |
| **데이터 시각화** | 자동 (적절한 차트 자동 선택) | 미지원 | 제한적 | Power BI 시각화 | QuickSight 시각화 |
| **대화형 분석** | 후속 질문으로 분석 심화 | 후속 질문 지원 | 제한적 | 대화형 | 대화형 |
| **거버넌스 통합** | Unity Catalog 접근 제어 적용 | Snowflake 접근 제어 | IAM | Power BI RLS | QuickSight RLS |
| **MCP 통합** | Genie를 MCP Tool로 노출 (Agent 연동) | 미지원 | 미지원 | 미지원 | 미지원 |

### Genie Space 설정과 운영

**Genie Space** 는 비즈니스 도메인별로 자연어 분석 환경을 구성하는 기능입니다.

| 설정 항목 | 설명 | 경쟁사 대응 |
|---|---|---|
| **데이터 소스** | Unity Catalog 테이블/뷰 지정 | 모든 플랫폼 유사 |
| **비즈니스 용어 정의** | "매출" = revenue 컬럼, "활성 고객" = status='active' | Cortex Analyst Semantic Model |
| **샘플 질문** | 자주 묻는 질문 등록으로 정확도 향상 | 일부 지원 |
| **SQL 예시** | 복잡한 비즈니스 로직을 SQL로 사전 정의 | Cortex Analyst에서 유사 |
| **접근 제어** | Unity Catalog 권한 자동 적용 (RLS/Column Mask 포함) | 플랫폼별 상이 |
| **신뢰할 수 있는 자산** | 검증된 테이블만 Genie에 노출 (데이터 신뢰성 보장) | 제한적 |

{% hint style="success" %}
**Genie Code의 핵심 차별화**: Cortex Analyst는 **SQL만 생성** 하지만, Genie Code는 **SQL + Python** 을 생성하고 실행합니다. 이는 단순 쿼리를 넘어 **통계 분석, 시계열 예측, 이상치 탐지** 등 고급 분석까지 자연어로 가능하게 합니다. 또한 Genie를 **MCP Tool로 노출** 하여 AI Agent가 Genie의 분석 능력을 활용할 수 있습니다.
{% endhint %}

---

## 쿼리 성능 비교

### SQL 성능 영향 요소

| 요소 | Databricks (Photon) | Snowflake | Redshift | BigQuery |
|---|---|---|---|---|
| **엔진 최적화** | C++ 벡터화, SIMD, Predictive I/O | 마이크로 파티션 프루닝 | AQUA 가속, MPP 분산 | Dremel 컬럼 기반 |
| **데이터 레이아웃** | Liquid Clustering (자동) | 자동 마이크로 파티셔닝 | Sort Key/Distribution Key (수동) | 자동/수동 클러스터링 |
| **캐싱** | Delta Cache (SSD) + Result Cache | Result Cache + Local Disk | Result Cache | 24시간 결과 캐시 |
| **동시성** | Warehouse별 독립 + 자동 스케일링 | Multi-cluster 자동 | WLM + Concurrency Scaling | Slot 기반 |
| **적응형 최적화** | AQE (런타임 재최적화) | 자동 | 자동 WLM | 자동 |
| **통계 수집** | 자동 (Delta Lake 파일 통계) | 자동 (마이크로 파티션 메타데이터) | 수동 ANALYZE 필요 | 자동 |

### 쿼리 유형별 성능 특성

| 쿼리 유형 | 최적 플랫폼 | 이유 |
|---|---|---|
| **포인트 쿼리 (단일 행 조회)** | Snowflake, BigQuery | 마이크로 파티션/클러스터링으로 빠른 스캔 |
| **대규모 집계 (GROUP BY)** | Databricks (Photon), BigQuery | C++ 벡터화 / Dremel 컬럼 스캔 |
| **복잡한 조인 (다중 테이블)** | Databricks (Photon) | 벡터화 해시 조인, AQE 스큐 처리 |
| **풀 테이블 스캔** | Databricks, BigQuery | 분산 스캔 + 컬럼 프루닝 |
| **서브쿼리/CTE 집약** | 모든 플랫폼 유사 | 옵티마이저 차이보다 데이터 크기 영향 |
| **반구조화 데이터 (JSON)** | Databricks, Snowflake | 네이티브 JSON 처리 |

---

## AI 함수 in SQL

### SQL 내 AI 호출 기능 비교

Databricks는 SQL 안에서 직접 AI 모델을 호출할 수 있는 **AI Functions** 를 제공합니다.

| 함수 | 설명 | Databricks | Snowflake | BigQuery | Redshift |
|---|---|---|---|---|---|
| **텍스트 생성** | LLM으로 텍스트 생성 | `AI_QUERY()` | `SNOWFLAKE.CORTEX.COMPLETE()` | `ML.GENERATE_TEXT()` | 미지원 |
| **분류** | 텍스트 카테고리 분류 | `AI_CLASSIFY()` | `CORTEX.CLASSIFY_TEXT()` | `ML.PREDICT()` (BQML) | 미지원 |
| **감성 분석** | 텍스트 감성 판별 | `AI_QUERY()` + 프롬프트 | `CORTEX.SENTIMENT()` | `ML.PREDICT()` (BQML) | 미지원 |
| **번역** | 다국어 번역 | `AI_QUERY()` + 프롬프트 | `CORTEX.TRANSLATE()` | `ML.TRANSLATE()` | 미지원 |
| **요약** | 텍스트 요약 | `AI_QUERY()` + 프롬프트 | `CORTEX.SUMMARIZE()` | 미지원 | 미지원 |
| **임베딩 생성** | 벡터 임베딩 | `AI_QUERY()` | `CORTEX.EMBED_TEXT()` | 미지원 | 미지원 |
| **유사도 검색** | 벡터 유사도 | Vector Search 통합 | `CORTEX.SEARCH()` | 미지원 | 미지원 |
| **커스텀 모델** | 자체 모델 호출 | `AI_QUERY(endpoint, ...)` | 미지원 | BQML 모델만 | 미지원 |

### AI_QUERY 활용 예시

```sql
-- SQL에서 직접 LLM 호출 (고객 리뷰 감성 분석)
SELECT
  review_id,
  review_text,
  AI_QUERY(
    'databricks-meta-llama-3-1-70b-instruct',
    CONCAT('다음 리뷰의 감성을 "긍정", "부정", "중립" 중 하나로 분류해주세요: ', review_text)
  ) AS sentiment
FROM catalog.schema.customer_reviews;

-- 커스텀 모델 서빙 엔드포인트 호출
SELECT
  product_id,
  AI_QUERY(
    'my-custom-recommendation-model',
    NAMED_STRUCT('user_id', user_id, 'context', browsing_history)
  ) AS recommendation
FROM catalog.schema.user_sessions;
```

{% hint style="info" %}
**AI_QUERY의 전략적 가치**: SQL 분석가가 **Python 없이도 AI를 활용** 할 수 있습니다. Foundation Model API든 커스텀 모델이든 SQL 한 줄로 호출 가능합니다. Snowflake Cortex도 유사한 함수를 제공하지만, **커스텀 모델 호출은 Databricks만 가능** 합니다.
{% endhint %}

---

## BI 도구 통합 비교

### 외부 BI 연동 방식

| BI 도구 | Databricks 연동 | Snowflake 연동 | Redshift 연동 | BigQuery 연동 | Fabric 연동 |
|---|---|---|---|---|---|
| **Tableau** | JDBC/ODBC + Partner Connect | JDBC/ODBC + Native | JDBC/ODBC | BigQuery Connector | 가능 |
| **Power BI** | DirectQuery + Direct Lake | DirectQuery | DirectQuery | DirectQuery | **네이티브 (최적)** |
| **Looker** | JDBC/ODBC | JDBC/ODBC | JDBC/ODBC | **네이티브 (최적)** | 가능 |
| **Qlik** | JDBC/ODBC | JDBC/ODBC | JDBC/ODBC | JDBC/ODBC | 가능 |
| **내장 BI** | **AI/BI Dashboard** | Snowsight | QuickSight | Looker Studio | Power BI |

### AI/BI Dashboard vs 경쟁사 내장 BI

| 항목 | Databricks AI/BI Dashboard | Snowsight | QuickSight | Looker Studio | Power BI |
|---|---|---|---|---|---|
| **AI 기반 자동 시각화** | 데이터 특성에 맞는 차트 자동 추천 | 기본 차트 | AI 기반 인사이트 | 자동 추천 | AI 기반 인사이트 |
| **데이터 소스** | Unity Catalog 테이블 직접 | Snowflake 테이블 | 다양한 소스 | Google 서비스 | 다양한 소스 |
| **거버넌스** | UC 접근 제어 자동 적용 | Snowflake 접근 제어 | IAM | IAM | Power BI RLS |
| **자연어 질문** | Genie Code와 통합 | 미지원 | Q (제한적) | Explore Assistant | Copilot |
| **임베딩/공유** | 내장 공유 + 스케줄 알림 | Snowsight 공유 | 임베딩 가능 | 공유 링크 | 임베딩 + 공유 |
| **커스터마이징** | Markdown + SQL + 시각화 위젯 | 제한적 | 풍부한 위젯 | 풍부한 위젯 | **가장 풍부** |

{% hint style="success" %}
**SA/SE 핵심 메시지**: Databricks는 **AI/BI Dashboard로 간단한 대시보드를 플랫폼 내에서 직접 구성** 할 수 있고, 고급 BI가 필요하면 **Tableau, Power BI, Looker와 완벽 연동** 됩니다. 특히 Power BI Direct Lake 모드로 데이터 복사 없이 대규모 대시보드를 구성할 수 있습니다.
{% endhint %}

---

## DBSQL vs BigQuery vs Redshift Serverless

### 서버리스 SQL 분석 비교

| 항목 | DBSQL Serverless | BigQuery (On-demand) | BigQuery (Editions) | Redshift Serverless |
|---|---|---|---|---|
| **과금 모델** | DBU/초 (Warehouse 크기 기반) | $6.25/TB 스캔 | Slot-hour 기반 | RPU-hour 기반 |
| **프로비저닝** | 불필요 (웜 풀) | 불필요 | 슬롯 수 설정 | RPU 범위 설정 |
| **시작 시간** | 초 단위 | 즉시 | 즉시 | 수십 초 |
| **유휴 비용** | Zero | Zero (On-demand) | Baseline 유지 | Zero (기본) |
| **동시성** | 자동 스케일링 (클러스터 수) | 2,000 동시 슬롯 (기본) | Autoscaling 슬롯 | 자동 RPU 조절 |
| **SQL 호환** | ANSI SQL + Spark SQL 확장 | GoogleSQL (일부 비표준) | 동일 | PostgreSQL |
| **AI 함수** | AI_QUERY, AI_CLASSIFY 등 | ML.PREDICT (BQML) | 동일 | 미지원 |
| **결과 캐시** | Delta Cache + Result Cache | 24시간 캐시 | 동일 | Result Cache |
| **최소 과금** | 초 단위 (최소 없음) | 10MB 최소 | 슬롯 최소 단위 | RPU 최소 단위 |

### 비용 효율성 시나리오

**소규모 팀 (일 50 쿼리, 평균 10GB 스캔)**

| 플랫폼 | 월 비용 (추정) | 특징 |
|---|---|---|
| BigQuery On-demand | ~$65 (50쿼리 × 10GB × $6.25/TB × 20일) | **가장 저렴**(소량 쿼리) |
| DBSQL Serverless (2X-Small) | ~$300 | ML/AI 통합 가능 |
| Redshift Serverless | ~$500 | AWS 생태계 통합 |

**대규모 팀 (일 5,000 쿼리, 평균 50GB 스캔)**

| 플랫폼 | 월 비용 (추정) | 특징 |
|---|---|---|
| BigQuery On-demand | ~$31,250 (비용 폭증) | **대규모에서 비쌈** |
| BigQuery Editions | ~$5,000 (500 슬롯) | 슬롯 기반이 경제적 |
| DBSQL Serverless (Medium) | ~$4,500 | ML/AI 통합 + 자동 스케일링 |
| Redshift Serverless | ~$4,000 | AWS 네이티브 |

{% hint style="info" %}
**핵심 인사이트**: BigQuery On-demand는 **쿼리 빈도가 극히 낮은 경우** 에만 경제적입니다. 일정 규모 이상에서는 DBSQL Serverless나 BigQuery Editions가 더 경제적이며, DBSQL은 추가로 **AI 함수, Genie Code, ML 통합** 이라는 가치를 제공합니다.
{% endhint %}
