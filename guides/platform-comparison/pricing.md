# 가격 모델 비교

## 과금 구조

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **과금 단위**| DBU (Databricks Unit) | Credit | RPU (Serverless) / 노드 시간 (Provisioned) | Slot (Editions) / 스캔 바이트 (On-demand) | CU (Capacity Unit) |
| **컴퓨팅 과금**| 초 단위 과금, 유휴 시 자동 종료 | 초 단위 (최소 60초), 자동 일시중지 | Serverless: RPU 초단위, Provisioned: 시간당 | On-demand: $6.25/TB 스캔, Editions: 슬롯 시간 | 시간당 CU 과금 |
| **스토리지 과금**| 클라우드 네이티브 가격 (S3/ADLS/GCS 직접) | Snowflake 자체 가격 (마크업 포함) | S3 + Redshift Managed Storage | $0.02/GB/월 | OneLake 스토리지 가격 |
| **서버리스 옵션**| Serverless SQL Warehouse, Serverless Compute | 기본 서버리스 | Redshift Serverless | 기본 서버리스 | Fabric Capacity |
| **유휴 비용**| Zero (자동 종료) | Zero (자동 일시중지) | Serverless: Zero, Provisioned: 과금 | On-demand: Zero, Editions: 슬롯 유지 비용 | Capacity 유지 비용 |
| **비용 투명성**| 높음 — 스토리지/컴퓨팅 완전 분리, System Tables로 분석 | 중간 — Credit 기반, 스토리지 마크업 | 중간 — 서비스별 분산 | 높음 — 쿼리당 명확 | 중간 — CU 기반 |
| **예약 할인**| 커밋 사용 할인 (1년/3년) | 선불 Capacity (할인) | Reserved Instance | Committed Use (할인) | Reserved Capacity |

## 비용 최적화 포인트

| 최적화 요소 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **스토리지 비용**| 클라우드 네이티브 가격 그대로 — 마크업 없음 | 벤더 마크업 포함 | S3 가격 + 관리 스토리지 | 자체 가격 | OneLake 가격 |
| **쿼리 최적화**| Predictive I/O, Liquid Clustering 자동 | 자동 Reclustering | 수동 Sort/Distribution Key | 자동 최적화 | Direct Lake |
| **비용 모니터링**| System Tables — 비용을 SQL로 분석/알림 | Resource Monitors | Cost Explorer | Budget Alerts | 비용 관리 대시보드 |
| **데이터 이동 비용**| 오픈 포맷 — 이관 비용 최소 | 독점 포맷 — 이관 시 높은 비용 | AWS 내부 무료, 외부 과금 | GCP 내부 무료, 외부 과금 | Azure 내부 최적화 |

{% hint style="info" %}
**Databricks 비용 투명성**: 스토리지는 고객 클라우드(S3/ADLS/GCS) 직접 과금으로 마크업이 없고, 컴퓨팅은 DBU 기반 초 단위 과금입니다. System Tables를 통해 비용을 SQL로 직접 분석하고, 이상 비용에 대한 알림을 설정할 수 있습니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 가격 강점**: BigQuery On-demand는 쿼리 실행량이 적은 경우 매우 경제적입니다 (쿼리당 과금, 유휴 비용 Zero). Snowflake는 Auto-suspend로 유휴 비용을 쉽게 관리할 수 있으며, Credit 기반 예측이 직관적입니다. MS Fabric은 이미 Microsoft E5 라이선스가 있는 조직에 추가 비용 부담이 적을 수 있습니다.
{% endhint %}

---

## 부록: 개발자 경험 및 접근성

### 사용자 유형별 접근성

| 사용자 유형 | Databricks | Snowflake | AWS | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **비즈니스 사용자**| Genie Spaces + AI/BI Dashboard (자연어 OK) | Snowsight (SQL 필요) | QuickSight (설정 복잡) | Looker Studio | Power BI (직관적) |
| **SQL 분석가**| Databricks SQL + Genie Code | Snowflake SQL (직관적) | Redshift + Athena (선택 필요) | BigQuery SQL | T-SQL in Fabric |
| **데이터 엔지니어**| DLT + Notebooks + Assistant (선언적+AI 지원) | Snowpark (Python/SQL) | Glue + EMR (복잡한 설정) | Dataflow (Beam 학습 필요) | Data Factory + Dataflow Gen2 |
| **데이터 사이언티스트**| Notebooks + MLflow + AutoML (End-to-End) | Snowpark ML (제한적) | SageMaker (별도 서비스) | Vertex AI (별도 서비스) | Synapse ML (제한적) |
| **ML 엔지니어**| MLflow + Model Serving + AI Dev Kit | 미지원 | SageMaker Pipelines | Vertex AI Pipelines | 제한적 |
| **앱 개발자**| AI Dev Kit + Databricks Apps (로컬→배포) | Streamlit in Snowflake | Lambda + API Gateway | Cloud Run | Power Apps 연동 |

### AI 코딩 도구 비교

| 항목 | Databricks | Snowflake | AWS | GCP | MS Fabric |
|---|---|---|---|---|---|
| **플랫폼 내장 AI 어시스턴트**| Databricks Assistant (모든 에디터에 내장) | Snowflake Copilot | Amazon Q Developer | Gemini Code Assist | Copilot in Fabric |
| **자연어 → 코드 생성**| Genie Code (SQL + Python 생성 및 실행) | 미지원 | 미지원 | 미지원 | Copilot (제한적) |
| **로컬 IDE 통합**| AI Dev Kit (VS Code) + Databricks Connect | 제한적 IDE 지원 | AWS Toolkit | Cloud Code | VS Code 확장 |
| **로컬 Agent 개발**| AI Dev Kit — 로컬에서 Agent 개발/테스트/배포 | 미지원 | 미지원 | 미지원 | 미지원 |
| **워크스페이스 컨텍스트**| Unity Catalog 메타데이터 활용 (도메인 인식) | 스키마 인식 | 서비스별 분리 | 서비스별 분리 | Fabric 메타데이터 |

{% hint style="info" %}
**과거 Databricks의 약점으로 여겨졌던 "학습 곡선"은 Genie Code, AI Dev Kit, Databricks Assistant로 완전히 해소** 되었습니다. SQL만 아는 분석가부터 Python 개발자, 비즈니스 사용자까지 — 자연어로 즉시 생산적인 작업이 가능합니다.
{% endhint %}
