# 거버넌스 비교

## 거버넌스 범위

| 거버넌스 대상 | Databricks Unity Catalog | Snowflake Horizon | AWS Lake Formation | GCP Dataplex | MS Purview/Fabric |
|---|---|---|---|---|---|
| **테이블 / 뷰** | 지원 | 지원 | 지원 | 지원 | 지원 |
| **ML 모델** | 지원 (모델 레지스트리 통합) | 미지원 | 미지원 (SageMaker 별도) | 미지원 (Vertex AI 별도) | 부분적 |
| **Feature Table** | 지원 (Feature Store 통합) | 미지원 | 미지원 | 미지원 | 미지원 |
| **Vector Search Index** | 지원 (벡터 인덱스도 UC 관리) | 미지원 | 미지원 | 미지원 | 미지원 |
| **AI Agent / Function** | 지원 (Agent도 UC에 등록) | 미지원 | 미지원 | 미지원 | 미지원 |
| **비정형 파일 (PDF, 이미지)** | 지원 (Volumes) | 미지원 | 미지원 | 제한적 | 부분적 |
| **External Connections** | 지원 (외부 DB 연결 관리) | 제한적 | 제한적 | 제한적 | 지원 |

## 접근 제어 및 리니지

| 항목 | Databricks | Snowflake | AWS | BigQuery/GCP | MS Fabric |
|---|---|---|---|---|---|
| **접근 제어 모델** | 3-level namespace (Catalog.Schema.Object) | Database.Schema.Object | Lake Formation TBAC / IAM | IAM + Dataplex | OneLake + Purview |
| **Row-Level Security** | Row Filter 함수 (동적) | Row Access Policy | Lake Formation Row-Level | BigQuery Row-Level | RLS in Power BI |
| **Column Masking** | Column Mask 함수 (동적) | Column Masking Policy | Lake Formation Column-Level | Policy Tags | Dynamic Data Masking |
| **Attribute-Based Access (ABAC)** | Tags 기반 동적 접근 제어 | Tag-based Masking | TBAC (Lake Formation) | Policy Tags | Sensitivity Labels |
| **자동 리니지** | 테이블→컬럼→모델→Agent 전체 추적 | Object Dependencies (테이블만) | 미지원 (별도 도구 필요) | Dataplex Lineage (제한적) | Purview Lineage |
| **컬럼 레벨 리니지** | 자동 지원 | 미지원 | 미지원 | 제한적 | 지원 |
| **ML 모델 리니지** | 학습 데이터→모델→서빙까지 추적 (유일) | 미지원 | SageMaker에서 별도 | Vertex AI에서 별도 | 부분적 |
| **감사 로그** | System Tables — SQL로 직접 분석 | Access History, Query History | CloudTrail (JSON) | Cloud Audit Logs | 통합 감사 로그 |
| **사용량 모니터링** | System Tables (Billing, Usage) — SQL 분석 | Resource Monitors | Cost Explorer + CloudWatch | Billing Export + BigQuery | 비용 관리 대시보드 |

{% hint style="success" %}
**Unity Catalog는 업계 유일의 데이터 + AI 통합 거버넌스 솔루션** 입니다. 테이블, ML 모델, Feature, Vector Index, AI Agent, 비정형 파일을 하나의 카탈로그에서 통합 관리하며, 컬럼 레벨까지의 End-to-End 리니지를 자동 추적합니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: Snowflake Horizon은 SQL 중심 데이터 거버넌스에서 성숙도가 높고 Data Clean Room 기능이 강력합니다. MS Purview는 Microsoft 365 생태계 전체에 걸친 거버넌스를 제공하며, 이미 MS 환경을 사용하는 조직에 자연스럽습니다. AWS Lake Formation은 IAM 기반의 세밀한 접근 제어가 가능합니다.
{% endhint %}

---

## Unity Catalog 심층 분석

### Unity Catalog 아키텍처

**Unity Catalog** 는 Databricks의 **통합 거버넌스 레이어** 로, 데이터와 AI 자산을 하나의 네임스페이스에서 관리합니다.

```
Account Level
  └─ Unity Catalog Metastore (리전별 1개)
      ├─ Catalog: prod
      │   ├─ Schema: sales
      │   │   ├─ Table: orders (Delta Lake)
      │   │   ├─ View: v_monthly_revenue
      │   │   ├─ Function: calculate_tax()
      │   │   └─ Volume: raw_files (PDF, 이미지)
      │   ├─ Schema: ml_models
      │   │   ├─ Model: churn_predictor (v1, v2, v3)
      │   │   ├─ Feature Table: customer_features
      │   │   └─ Vector Search Index: doc_embeddings
      │   └─ Schema: agents
      │       ├─ Agent: customer_support_agent
      │       └─ Function: search_knowledge_base()  ← Agent 도구
      ├─ Catalog: dev
      ├─ Catalog: staging
      └─ External Connections
          ├─ PostgreSQL (외부 DB)
          ├─ Snowflake (연합 쿼리)
          └─ MySQL (외부 DB)
```

### Unity Catalog 관리 대상 (경쟁사 대비)

| 관리 대상 | Unity Catalog | Snowflake Horizon | Lake Formation | Dataplex | Purview |
|---|---|---|---|---|---|
| **테이블/뷰** | 지원 | 지원 | 지원 | 지원 | 지원 |
| **함수/프로시저** | 지원 (UDF, Agent 도구 포함) | 지원 | 미지원 | 미지원 | 제한적 |
| **ML 모델** | **지원 (버전 관리 + 리니지)** | 미지원 | 미지원 | 미지원 | 제한적 |
| **Feature Table** | **지원 (온라인+오프라인)** | 미지원 | 미지원 | 미지원 | 미지원 |
| **Vector Search Index** | **지원** | 미지원 | 미지원 | 미지원 | 미지원 |
| **AI Agent** | **지원 (Agent도 UC에 등록)** | 미지원 | 미지원 | 미지원 | 미지원 |
| **비정형 파일** | **지원 (Volumes)** | Stage (제한적) | 미지원 | 제한적 | 제한적 |
| **외부 연결** | **지원 (연합 쿼리)** | 미지원 | 제한적 | 제한적 | 지원 |
| **Model Serving Endpoint** | **지원** | 미지원 | 미지원 | 미지원 | 미지원 |

{% hint style="success" %}
**Unity Catalog는 "데이터 + AI 거버넌스"의 업계 유일 솔루션** 입니다. 경쟁사 카탈로그는 테이블/뷰만 관리하는 반면, Unity Catalog는 ML 모델, Feature, Vector Index, Agent까지 **동일한 접근 제어, 리니지, 감사** 를 적용합니다.
{% endhint %}

---

## 데이터 리니지 상세 비교

### 리니지 추적 범위

| 리니지 유형 | Databricks | Snowflake | AWS | GCP | MS Fabric |
|---|---|---|---|---|---|
| **테이블 레벨** | 자동 (어떤 테이블이 어떤 테이블을 참조) | Object Dependencies | 미지원 (별도 도구) | Dataplex Lineage | Purview Lineage |
| **컬럼 레벨** | **자동 (어떤 컬럼이 어떤 컬럼에서 파생)** | 미지원 | 미지원 | 제한적 | 지원 |
| **ML 모델 리니지** | **자동 (학습 데이터 → 모델 → 서빙)** | 미지원 | SageMaker에서 수동 | Vertex AI에서 수동 | 제한적 |
| **Agent 리니지** | **자동 (Agent가 사용하는 도구/데이터 추적)** | 미지원 | 미지원 | 미지원 | 미지원 |
| **노트북 리니지** | 자동 (어떤 노트북이 어떤 테이블을 생성) | 미지원 | 미지원 | 미지원 | 제한적 |
| **파이프라인 리니지** | 자동 (DLT 파이프라인 → 테이블) | Dynamic Table 의존성 | Glue 내부만 | Composer 내부만 | Data Factory 내부 |

### 리니지 활용 시나리오

| 시나리오 | Unity Catalog 리니지 활용 | 경쟁사 |
|---|---|---|
| **영향도 분석** | "이 테이블을 변경하면 어떤 뷰/모델/대시보드에 영향?" → 자동 확인 | 수동 조사 또는 별도 도구 |
| **데이터 출처 추적** | "이 ML 모델은 어떤 데이터로 학습되었나?" → 자동 추적 | SageMaker/Vertex AI에서 별도 조회 |
| **규제 대응** | "개인정보가 포함된 테이블의 모든 하류 사용처" → SQL 한 줄 | 수동 문서화 |
| **디버깅** | "이 컬럼의 값이 이상한데, 어디서 변환되었나?" → 컬럼 리니지 확인 | 코드 리뷰로 수동 추적 |
| **AI 감사** | "이 Agent가 어떤 데이터에 접근했나?" → System Tables 조회 | 수동 로그 분석 |

---

## 접근 제어 모델 심층 비교

### RBAC vs ABAC 접근 제어

| 항목 | Databricks Unity Catalog | Snowflake | AWS Lake Formation | GCP | MS Purview |
|---|---|---|---|---|---|
| **RBAC (역할 기반)** | GRANT/REVOKE on Catalog/Schema/Table | GRANT/REVOKE | IAM Role + Lake Formation | IAM Role | Azure AD Role |
| **ABAC (속성 기반)** | **Tags 기반 동적 접근 제어** | Tag-based Masking | TBAC (Lake Formation) | Policy Tags | Sensitivity Labels |
| **Row-Level Security** | **Row Filter 함수 (동적, SQL 기반)** | Row Access Policy | Row-Level (Lake Formation) | BigQuery Row-Level | RLS in Power BI |
| **Column Masking** | **Column Mask 함수 (동적, SQL 기반)** | Column Masking Policy | Column-Level | Policy Tags | Dynamic Data Masking |
| **동적 마스킹** | 사용자/그룹에 따라 다른 값 반환 | 사용자/역할 기반 | IAM 기반 | Policy 기반 | 라벨 기반 |

### Row Filter / Column Mask 예시 (Databricks)

```sql
-- Row Filter: 사용자 부서에 해당하는 행만 조회
CREATE FUNCTION catalog.schema.region_filter(region STRING)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('admin'), true, region = CURRENT_USER_ATTRIBUTE('department'));

ALTER TABLE catalog.schema.sales SET ROW FILTER catalog.schema.region_filter ON (region);

-- Column Mask: PII 데이터 동적 마스킹
CREATE FUNCTION catalog.schema.mask_email(email STRING)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('pii_viewer'), email, REGEXP_REPLACE(email, '(.).*@', '$1***@'));

ALTER TABLE catalog.schema.customers ALTER COLUMN email SET MASK catalog.schema.mask_email;
```

**결과**: `pii_viewer` 그룹은 원본 이메일을, 다른 사용자는 `j***@example.com` 형태를 봅니다.

{% hint style="info" %}
**Row Filter/Column Mask의 핵심 장점**: SQL 함수로 정의하므로 **비즈니스 로직을 유연하게 구현** 할 수 있습니다. 예: 현재 사용자의 부서, 역할, 심지어 외부 API 호출 결과에 따라 동적으로 접근을 제어할 수 있습니다. Snowflake의 Masking Policy도 유사하지만, **ML 모델/Agent에는 적용되지 않습니다.**
{% endhint %}

---

## 감사 로그 및 모니터링 비교

### System Tables vs 경쟁사 감사 도구

| 항목 | Databricks System Tables | Snowflake Access/Query History | AWS CloudTrail | GCP Cloud Audit | MS Purview |
|---|---|---|---|---|---|
| **형태** | Delta 테이블 (SQL로 직접 분석) | 뷰 (SQL로 조회) | JSON 로그 (S3에 저장) | JSON 로그 (Cloud Logging) | 별도 포털 |
| **쿼리 방식** | SQL (DBSQL/Notebook) | SQL (Snowflake) | Athena/CloudWatch Insights | BigQuery | Purview UI/API |
| **보존 기간** | 365일 (기본) | 1년 (Enterprise+) | 무제한 (S3) | 400일 (기본) | 90일 (기본) |
| **실시간성** | 준실시간 (~15분) | 준실시간 | 수 분 지연 | 수 분 지연 | 지연 있음 |
| **비용** | 포함 (별도 비용 없음) | 포함 | CloudTrail + S3 + Athena 비용 | Cloud Logging 비용 | 포함 |

### System Tables 주요 테이블

| System Table | 용도 | SQL 예시 |
|---|---|---|
| `system.access.audit` | 모든 API 호출, 데이터 접근 기록 | `SELECT * FROM system.access.audit WHERE action = 'SELECT'` |
| `system.billing.usage` | DBU 사용량 + 비용 상세 | `SELECT sku_name, SUM(usage_quantity) FROM system.billing.usage GROUP BY 1` |
| `system.billing.list_prices` | SKU별 리스트 가격 | 비용 계산 시 JOIN |
| `system.compute.clusters` | 클러스터 이벤트 (생성, 크기 조절, 종료) | 비효율 클러스터 식별 |
| `system.lakeflow.events` | DLT 파이프라인 이벤트 | 파이프라인 오류 분석 |
| `system.query.history` | 쿼리 실행 이력 + 성능 지표 | 느린 쿼리 식별/최적화 |
| `system.serving.served_entities` | 모델 서빙 이벤트 | 서빙 엔드포인트 모니터링 |

### 비용 모니터링 대시보드 예시

```sql
-- 워크스페이스별 일별 비용 추이
SELECT
  date_trunc('day', usage_date) AS day,
  workspace_id,
  sku_name,
  SUM(usage_quantity * list_price) AS estimated_cost
FROM system.billing.usage u
JOIN system.billing.list_prices p ON u.sku_name = p.sku_name
WHERE usage_date >= date_sub(current_date(), 30)
GROUP BY 1, 2, 3
ORDER BY 1;

-- 비정상 비용 알림 (이전 주 대비 50% 이상 증가)
WITH weekly_cost AS (
  SELECT
    date_trunc('week', usage_date) AS week,
    SUM(usage_quantity * list_price) AS cost
  FROM system.billing.usage u
  JOIN system.billing.list_prices p ON u.sku_name = p.sku_name
  GROUP BY 1
)
SELECT *
FROM weekly_cost
WHERE cost > LAG(cost) OVER (ORDER BY week) * 1.5;
```

{% hint style="success" %}
**System Tables의 핵심 가치**: 비용, 감사, 성능, 파이프라인 이벤트를 **모두 SQL로 분석** 할 수 있습니다. 별도 도구(CloudTrail → Athena, Cost Explorer 등)를 조합할 필요 없이, Databricks 안에서 통합 모니터링 대시보드를 구성할 수 있습니다.
{% endhint %}

---

## 데이터 공유 비교

### Delta Sharing vs 경쟁사 데이터 공유

| 항목 | Databricks Delta Sharing | Snowflake Secure Data Sharing | AWS Data Exchange | BigQuery Analytics Hub | Fabric OneLake Sharing |
|---|---|---|---|---|---|
| **프로토콜** | 오픈 프로토콜 (REST API) | 독점 프로토콜 | AWS Marketplace | Google Marketplace | OneLake API |
| **수신자 요구사항** | **Databricks 불필요**(Spark, Pandas, Power BI 등) | **Snowflake 계정 필수** | AWS 계정 필수 | GCP 계정 필수 | Azure 계정 필수 |
| **크로스 플랫폼** | **지원 (클라우드/엔진 무관)** | Snowflake 내부만 | AWS 내부 | GCP 내부 | Azure 중심 |
| **데이터 복사** | 복사 없이 직접 접근 | 복사 없이 직접 접근 | 복사 발생 | 복사 또는 직접 | OneLake 직접 |
| **거버넌스** | UC 접근 제어 적용 | Snowflake 접근 제어 | IAM | IAM | Purview |
| **Clean Room** | Databricks Clean Rooms | **Snowflake Clean Room (성숙)** | AWS Clean Rooms | BigQuery Clean Room | 제한적 |
| **비용** | 수신자: 컴퓨팅만 부담 | 수신자: Snowflake Credit | 데이터 전송 비용 | 데이터 전송 비용 | Azure 비용 |

{% hint style="info" %}
**Delta Sharing의 핵심 차별화**: **오픈 프로토콜** 이므로 수신자가 Databricks를 사용하지 않아도 됩니다. Spark, Pandas, Power BI, R 등 수십 개 클라이언트에서 직접 읽을 수 있습니다. 반면 Snowflake Data Sharing은 수신자도 **반드시 Snowflake 계정** 이 필요합니다.
{% endhint %}

---

## AI 거버넌스 — 규제 대응

### AI 거버넌스가 필요한 이유

2024-2025년 EU AI Act, 한국 AI 기본법 등 **AI 규제가 본격화** 되면서, AI 모델과 Agent에 대한 거버넌스가 필수 요구사항이 되고 있습니다.

| 규제 요구사항 | Databricks 대응 | 경쟁사 대응 |
|---|---|---|
| **모델 투명성** | MLflow + Unity Catalog로 학습 데이터/파라미터/성능 추적 | 서비스별 분리, 수동 문서화 |
| **데이터 출처** | End-to-End 리니지 (원천→학습→모델→서빙) | 서비스 경계에서 단절 |
| **편향 감지** | Lakehouse Monitor + Agent Evaluation | 별도 도구 필요 |
| **접근 통제** | Unity Catalog (모델, Agent, 데이터 통합 제어) | 서비스별 별도 IAM |
| **감사 추적** | System Tables (모든 AI 활동 SQL로 조회) | CloudTrail/Cloud Audit (JSON 로그) |
| **모델 버전 관리** | Unity Catalog Models (v1, v2, ... + 스테이지) | 서비스별 별도 관리 |
| **위험 평가** | Agent Evaluation (자동 품질/안전성 측정) | 수동 테스트 |

### AI 거버넌스 체크리스트

| 항목 | Databricks Unity Catalog | 충족 여부 |
|---|---|---|
| 학습 데이터의 출처와 품질을 추적할 수 있는가? | 리니지 자동 추적 + Lakehouse Monitor | 충족 |
| 모델의 입출력을 로깅하고 감사할 수 있는가? | System Tables + MLflow | 충족 |
| 모델에 대한 접근 권한을 세밀하게 제어할 수 있는가? | GRANT/REVOKE on MODEL | 충족 |
| 모델 성능 저하/편향을 자동 감지할 수 있는가? | Lakehouse Monitor + Agent Evaluation | 충족 |
| AI Agent가 접근하는 데이터/도구를 통제할 수 있는가? | UC Functions as Tools | 충족 |
| 규제 기관에 감사 보고서를 제출할 수 있는가? | System Tables SQL 쿼리로 즉시 생성 | 충족 |

{% hint style="success" %}
**SA/SE 핵심 메시지**: AI 규제 시대에 **"데이터 거버넌스와 AI 거버넌스를 하나로 통합" **하는 것은 선택이 아니라 필수입니다. Unity Catalog는 **유일하게 데이터, ML 모델, Feature, Vector Index, AI Agent를 하나의 카탈로그에서 통합 관리** 하는 솔루션입니다. 경쟁사에서는 데이터 거버넌스(Lake Formation/Dataplex)와 AI 거버넌스(SageMaker/Vertex AI)가 분리되어 있어, 통합 감사와 리니지가 불가능합니다.
{% endhint %}
