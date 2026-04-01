# 거버넌스 비교

## 거버넌스 범위

| 거버넌스 대상 | Databricks Unity Catalog | Snowflake Horizon | AWS Lake Formation | GCP Dataplex | MS Purview/Fabric |
|---|---|---|---|---|---|
| **테이블 / 뷰** | 지원 | 지원 | 지원 | 지원 | 지원 |
| **ML 모델** | 지원 (모델 레지스트리 통합) | 미지원 | 미지원 (SageMaker 별도) | 미지원 (Vertex AI 별도) | 부분적 |
| **Feature Table** | 지원 (Feature Store 통합) | 미지원 | 미지원 | 미지원 | 미지원 |
| **Vector Search Index** | 지원 (벡터 인덱스도 UC 관리) | 미지원 | 미지원 | 미지원 | 미지원 |
| **AI Agent / Function** | 지원 (Agent도 UC에 등록) | 미지원 | 미지원 | 미지원 | 미지원 |
| ** 비정형 파일 (PDF, 이미지)** | 지원 (Volumes) | 미지원 | 미지원 | 제한적 | 부분적 |
| **External Connections** | 지원 (외부 DB 연결 관리) | 제한적 | 제한적 | 제한적 | 지원 |

## 접근 제어 및 리니지

| 항목 | Databricks | Snowflake | AWS | BigQuery/GCP | MS Fabric |
|---|---|---|---|---|---|
| ** 접근 제어 모델** | 3-level namespace (Catalog.Schema.Object) | Database.Schema.Object | Lake Formation TBAC / IAM | IAM + Dataplex | OneLake + Purview |
| **Row-Level Security** | Row Filter 함수 (동적) | Row Access Policy | Lake Formation Row-Level | BigQuery Row-Level | RLS in Power BI |
| **Column Masking** | Column Mask 함수 (동적) | Column Masking Policy | Lake Formation Column-Level | Policy Tags | Dynamic Data Masking |
| **Attribute-Based Access (ABAC)** | Tags 기반 동적 접근 제어 | Tag-based Masking | TBAC (Lake Formation) | Policy Tags | Sensitivity Labels |
| ** 자동 리니지** | 테이블→컬럼→모델→Agent 전체 추적 | Object Dependencies (테이블만) | 미지원 (별도 도구 필요) | Dataplex Lineage (제한적) | Purview Lineage |
| ** 컬럼 레벨 리니지** | 자동 지원 | 미지원 | 미지원 | 제한적 | 지원 |
| **ML 모델 리니지** | 학습 데이터→모델→서빙까지 추적 (유일) | 미지원 | SageMaker에서 별도 | Vertex AI에서 별도 | 부분적 |
| ** 감사 로그** | System Tables — SQL로 직접 분석 | Access History, Query History | CloudTrail (JSON) | Cloud Audit Logs | 통합 감사 로그 |
| ** 사용량 모니터링** | System Tables (Billing, Usage) — SQL 분석 | Resource Monitors | Cost Explorer + CloudWatch | Billing Export + BigQuery | 비용 관리 대시보드 |

{% hint style="success" %}
**Unity Catalog는 업계 유일의 데이터 + AI 통합 거버넌스 솔루션** 입니다. 테이블, ML 모델, Feature, Vector Index, AI Agent, 비정형 파일을 하나의 카탈로그에서 통합 관리하며, 컬럼 레벨까지의 End-to-End 리니지를 자동 추적합니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: Snowflake Horizon은 SQL 중심 데이터 거버넌스에서 성숙도가 높고 Data Clean Room 기능이 강력합니다. MS Purview는 Microsoft 365 생태계 전체에 걸친 거버넌스를 제공하며, 이미 MS 환경을 사용하는 조직에 자연스럽습니다. AWS Lake Formation은 IAM 기반의 세밀한 접근 제어가 가능합니다.
{% endhint %}
