# 가격 모델 비교

## 과금 구조

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **과금 단위** | DBU (Databricks Unit) | Credit | RPU (Serverless) / 노드 시간 (Provisioned) | Slot (Editions) / 스캔 바이트 (On-demand) | CU (Capacity Unit) |
| **컴퓨팅 과금** | 초 단위 과금, 유휴 시 자동 종료 | 초 단위 (최소 60초), 자동 일시중지 | Serverless: RPU 초단위, Provisioned: 시간당 | On-demand: $6.25/TB 스캔, Editions: 슬롯 시간 | 시간당 CU 과금 |
| **스토리지 과금** | 클라우드 네이티브 가격 (S3/ADLS/GCS 직접) | Snowflake 자체 가격 (마크업 포함) | S3 + Redshift Managed Storage | $0.02/GB/월 | OneLake 스토리지 가격 |
| **서버리스 옵션** | Serverless SQL Warehouse, Serverless Compute | 기본 서버리스 | Redshift Serverless | 기본 서버리스 | Fabric Capacity |
| **유휴 비용** | Zero (자동 종료) | Zero (자동 일시중지) | Serverless: Zero, Provisioned: 과금 | On-demand: Zero, Editions: 슬롯 유지 비용 | Capacity 유지 비용 |
| **비용 투명성** | 높음 — 스토리지/컴퓨팅 완전 분리, System Tables로 분석 | 중간 — Credit 기반, 스토리지 마크업 | 중간 — 서비스별 분산 | 높음 — 쿼리당 명확 | 중간 — CU 기반 |
| **예약 할인** | 커밋 사용 할인 (1년/3년) | 선불 Capacity (할인) | Reserved Instance | Committed Use (할인) | Reserved Capacity |

## 비용 최적화 포인트

| 최적화 요소 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **스토리지 비용** | 클라우드 네이티브 가격 그대로 — 마크업 없음 | 벤더 마크업 포함 | S3 가격 + 관리 스토리지 | 자체 가격 | OneLake 가격 |
| **쿼리 최적화** | Predictive I/O, Liquid Clustering 자동 | 자동 Reclustering | 수동 Sort/Distribution Key | 자동 최적화 | Direct Lake |
| **비용 모니터링** | System Tables — 비용을 SQL로 분석/알림 | Resource Monitors | Cost Explorer | Budget Alerts | 비용 관리 대시보드 |
| **데이터 이동 비용** | 오픈 포맷 — 이관 비용 최소 | 독점 포맷 — 이관 시 높은 비용 | AWS 내부 무료, 외부 과금 | GCP 내부 무료, 외부 과금 | Azure 내부 최적화 |

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
| **비즈니스 사용자** | Genie Spaces + AI/BI Dashboard (자연어 OK) | Snowsight (SQL 필요) | QuickSight (설정 복잡) | Looker Studio | Power BI (직관적) |
| **SQL 분석가** | Databricks SQL + Genie Code | Snowflake SQL (직관적) | Redshift + Athena (선택 필요) | BigQuery SQL | T-SQL in Fabric |
| **데이터 엔지니어** | DLT + Notebooks + Assistant (선언적+AI 지원) | Snowpark (Python/SQL) | Glue + EMR (복잡한 설정) | Dataflow (Beam 학습 필요) | Data Factory + Dataflow Gen2 |
| **데이터 사이언티스트** | Notebooks + MLflow + AutoML (End-to-End) | Snowpark ML (제한적) | SageMaker (별도 서비스) | Vertex AI (별도 서비스) | Synapse ML (제한적) |
| **ML 엔지니어** | MLflow + Model Serving + AI Dev Kit | 미지원 | SageMaker Pipelines | Vertex AI Pipelines | 제한적 |
| **앱 개발자** | AI Dev Kit + Databricks Apps (로컬→배포) | Streamlit in Snowflake | Lambda + API Gateway | Cloud Run | Power Apps 연동 |

### AI 코딩 도구 비교

| 항목 | Databricks | Snowflake | AWS | GCP | MS Fabric |
|---|---|---|---|---|---|
| **플랫폼 내장 AI 어시스턴트** | Databricks Assistant (모든 에디터에 내장) | Snowflake Copilot | Amazon Q Developer | Gemini Code Assist | Copilot in Fabric |
| **자연어 → 코드 생성** | Genie Code (SQL + Python 생성 및 실행) | 미지원 | 미지원 | 미지원 | Copilot (제한적) |
| **로컬 IDE 통합** | AI Dev Kit (VS Code) + Databricks Connect | 제한적 IDE 지원 | AWS Toolkit | Cloud Code | VS Code 확장 |
| **로컬 Agent 개발** | AI Dev Kit — 로컬에서 Agent 개발/테스트/배포 | 미지원 | 미지원 | 미지원 | 미지원 |
| **워크스페이스 컨텍스트** | Unity Catalog 메타데이터 활용 (도메인 인식) | 스키마 인식 | 서비스별 분리 | 서비스별 분리 | Fabric 메타데이터 |

{% hint style="info" %}
**과거 Databricks의 약점으로 여겨졌던 "학습 곡선"은 Genie Code, AI Dev Kit, Databricks Assistant로 완전히 해소** 되었습니다. SQL만 아는 분석가부터 Python 개발자, 비즈니스 사용자까지 — 자연어로 즉시 생산적인 작업이 가능합니다.
{% endhint %}

---

## TCO (Total Cost of Ownership) 분석 프레임워크

### TCO 구성 요소

플랫폼 비용 비교 시 **컴퓨팅/스토리지 비용만** 보면 안 됩니다. **숨은 비용** 을 포함한 전체 TCO를 평가해야 합니다.

| TCO 구성 요소 | 설명 | Databricks | Snowflake | AWS 조합 | BigQuery |
|---|---|---|---|---|---|
| **컴퓨팅 비용** | SQL, ETL, ML 실행 비용 | DBU × 단가 | Credit × 단가 | 서비스별 합산 | Slot/TB 과금 |
| **스토리지 비용** | 데이터 저장 비용 | 클라우드 직접 (마크업 Zero) | **벤더 마크업 포함** | S3 + 관리형 | 자체 가격 |
| **데이터 이동 비용** | 플랫폼 간 데이터 복사 | Zero (단일 플랫폼) | Snowflake↔SageMaker 복사 | 서비스 간 전송 | GCP→외부 전송 |
| **거버넌스 도구 비용** | 카탈로그, 리니지, 감사 | 포함 (Unity Catalog) | 포함 (Horizon) | Lake Formation + CloudTrail | Dataplex (추가) |
| **3rd Party 도구** | dbt, Fivetran, Monte Carlo 등 | 최소화 가능 | dbt 필요 (Dynamic Tables 한계) | 다수 필요 | 다수 필요 |
| **인력 비용** | 플랫폼 운영/개발 인력 | 1개 플랫폼 = 적은 인력 | 2-3개 플랫폼 조합 = 많은 인력 | 5-10개 서비스 = 가장 많음 | 중간 |
| **교육/학습 비용** | 팀 온보딩, 교육 | 1개 플랫폼 학습 | SQL 중심 (빠른 온보딩) | 서비스별 별도 학습 | SQL 중심 |
| **벤더 종속 비용** | 미래 이관 비용 | 최소 (오픈 포맷) | **높음 (독점 포맷)** | 중간 (AWS 종속) | 중간-높음 |
| **다운타임 비용** | 장애 시 비즈니스 영향 | 서비스별 SLA | 높은 가용성 | 서비스별 SLA | 높은 가용성 |

### 3년 TCO 시나리오 비교

**시나리오: 데이터 + AI 통합 플랫폼 (중견기업, 50TB 데이터)**

| 비용 항목 | Databricks | Snowflake + SageMaker | AWS 조합 (Redshift + Glue + SageMaker) |
|---|---|---|---|
| **컴퓨팅 (3년)** | $540,000 | $720,000 | $648,000 |
| **스토리지 (3년)** | $27,000 (S3 직접) | $54,000 (마크업) | $27,000 (S3) |
| **데이터 이동 (3년)** | $0 | $36,000 (Snowflake↔SageMaker) | $18,000 (서비스 간) |
| **3rd Party 도구 (3년)** | $36,000 (최소) | $108,000 (dbt + Fivetran + Monte Carlo) | $72,000 (dbt + 기타) |
| **인력 (3년, 추가 인력)** | $0 (기존 팀) | $360,000 (1명 추가) | $720,000 (2명 추가) |
| **교육 비용** | $30,000 | $45,000 (2개 플랫폼) | $60,000 (3-5개 서비스) |
| **이관 리스크 (NPV)** | $0 | $150,000 | $75,000 |
| **3년 TCO 합계** | **$633,000** | **$1,473,000** | **$1,620,000** |
| **연간 TCO** | **$211,000** | **$491,000** | **$540,000** |

{% hint style="warning" %}
**주의**: 위 수치는 가상 시나리오이며, 실제 비용은 워크로드, 데이터 크기, 리전, 계약 조건에 따라 크게 달라집니다. **PoC를 통한 실제 비용 측정** 을 권장합니다.
{% endhint %}

{% hint style="success" %}
**핵심 메시지**: 컴퓨팅 비용만 보면 플랫폼 간 차이가 크지 않을 수 있습니다. 하지만 **데이터 이동, 3rd party 도구, 추가 인력, 벤더 종속 비용** 을 포함하면 Databricks의 **단일 플랫폼 전략** 이 TCO 기준으로 가장 경제적입니다.
{% endhint %}

---

## 워크로드별 비용 비교 시나리오

### 시나리오 1: SQL 분석 전용 (소규모 팀)

| 조건 | 값 |
|---|---|
| **팀 규모** | 분석가 5명 |
| **일일 쿼리** | 200건, 평균 스캔 5GB |
| **데이터 크기** | 5TB |
| **사용 시간** | 일 8시간, 주 5일 |

| 플랫폼 | 월 비용 (추정) | 비고 |
|---|---|---|
| **BigQuery On-demand** | ~$130 | 쿼리당 과금, **가장 저렴** |
| **Databricks DBSQL Serverless (2X-Small)** | ~$800 | ML/AI 확장 가능 |
| **Snowflake (X-Small)** | ~$1,200 | SQL 편의성 최고 |
| **Redshift Serverless** | ~$1,000 | AWS 생태계 통합 |

**결론**: SQL만 필요하고 쿼리 빈도가 낮으면 BigQuery On-demand가 가장 경제적. 다만 ML/AI 확장 가능성을 고려하면 Databricks가 장기적으로 유리.

### 시나리오 2: ETL + SQL 분석 (중규모 팀)

| 조건 | 값 |
|---|---|
| **팀 규모** | 엔지니어 5명 + 분석가 10명 |
| **일일 ETL** | 500GB 처리 |
| **일일 쿼리** | 1,000건, 평균 스캔 10GB |
| **데이터 크기** | 50TB |
| **스트리밍** | Kafka 소스 3개 (24/7) |

| 플랫폼 | 월 비용 (추정) | 비고 |
|---|---|---|
| **Databricks (DLT + DBSQL)** | ~$8,000 | 단일 플랫폼, 스트리밍 포함 |
| **Snowflake + dbt** | ~$12,000 | Snowflake Credit + dbt Cloud 라이선스 |
| **AWS (Glue + Redshift + MSK)** | ~$15,000 | 3개 서비스 조합, 운영 복잡 |
| **BigQuery + Dataflow** | ~$10,000 | Dataflow 운영 비용 높음 |

### 시나리오 3: 데이터 + AI 풀스택 (대규모 조직)

| 조건 | 값 |
|---|---|
| **팀 규모** | 엔지니어 10명 + 분석가 20명 + DS 5명 + ML Eng 3명 |
| **일일 ETL** | 2TB 처리 |
| **일일 쿼리** | 5,000건 |
| **ML 학습** | GPU 클러스터 (주 3회, 각 4시간) |
| **모델 서빙** | 3개 모델 24/7 |
| **Agent** | 1개 Agent 운영 |
| **데이터 크기** | 200TB |

| 플랫폼 조합 | 월 비용 (추정) | 인력 | 총 비용 |
|---|---|---|---|
| **Databricks (All-in-One)** | ~$35,000 | 기존 팀 | **~$35,000** |
| **Snowflake + SageMaker + Bedrock** | ~$40,000 | +1명 | **~$55,000** |
| **AWS Full (Redshift + Glue + SageMaker + Bedrock + Lake Formation)** | ~$38,000 | +2명 | **~$68,000** |
| **BigQuery + Vertex AI** | ~$36,000 | +1명 | **~$51,000** |

{% hint style="info" %}
**핵심 포인트**: 워크로드가 SQL만이면 BigQuery/Snowflake가 경쟁력 있습니다. 하지만 **ETL + SQL + ML + AI를 모두 수행** 하는 경우, Databricks의 단일 플랫폼 전략이 **인력 비용 포함 TCO에서 가장 경제적** 입니다.
{% endhint %}

---

## 비용 최적화 전략

### Databricks 비용 최적화 체크리스트

| 최적화 영역 | 전략 | 예상 절감 |
|---|---|---|
| **Serverless 전환** | Classic → Serverless SQL Warehouse/Compute | 20-40% (유휴 비용 제거) |
| **Spot Instance 활용** | Worker 노드에 Spot/Preemptible 인스턴스 | 40-70% (인스턴스 비용) |
| **Job Cluster 사용** | All-Purpose → Job Cluster (배치 작업) | 30-50% (DBU 단가 차이) |
| **Auto-terminate 설정** | 유휴 클러스터 자동 종료 (30분) | 변동 (유휴 시간에 비례) |
| **Liquid Clustering** | 수동 OPTIMIZE/Z-ORDER 대체 | 10-30% (I/O 감소) |
| **커밋 사용 계약** | 1년/3년 선약 할인 | 25-40% |
| **Photon 활성화** | SQL 워크로드 Photon 활용 | 성능 3-8x → 동일 작업 비용 절감 |
| **System Tables 분석** | 비용 이상 탐지 + 최적화 기회 식별 | 지속적 개선 |
| **Predictive Optimization** | AI 기반 자동 최적화 (OPTIMIZE, VACUUM, ANALYZE) | 10-20% (수동 관리 비용 제거) |

### 경쟁사별 비용 최적화 대응

| 플랫폼 | 주요 최적화 전략 | 한계 |
|---|---|---|
| **Snowflake** | Warehouse 크기 최적화, Auto-suspend, Resource Monitors | Credit 기반으로 세밀한 제어 어려움, 스토리지 마크업 불가피 |
| **Redshift** | Reserved Instance, Concurrency Scaling 제어, AQUA 활용 | Provisioned는 유휴 비용 발생, 수동 최적화 필요 |
| **BigQuery** | On-demand vs Editions 선택, Partitioning, Clustering | On-demand는 대규모에서 비용 폭증, 슬롯 예측 어려움 |
| **Fabric** | Capacity 크기 최적화, Reserved Capacity | Capacity 고정 비용, 탄력성 부족 |

---

## 숨은 비용 분석

### 직접 비교에서 놓치기 쉬운 비용

| 숨은 비용 | Databricks | Snowflake | AWS 조합 | BigQuery |
|---|---|---|---|---|
| **스토리지 마크업** | 없음 (클라우드 직접) | **있음 (~2-3x 마크업)** | 없음 (S3 직접) | 있음 (자체 가격) |
| **데이터 이동** | Zero (단일 플랫폼) | **Snowflake↔SageMaker 복사** | 서비스 간 전송 | GCP→외부 Egress |
| **3rd Party ETL** | 불필요 (Lakeflow) | dbt Cloud (~$100/user/월) | 선택적 | Fivetran/Airbyte 필요 |
| **3rd Party 데이터 품질** | 불필요 (DLT Expectations + Monitor) | Monte Carlo (~$10K+/월) | Deequ/Great Expectations | 별도 도구 |
| **추가 인력** | 최소 (1개 플랫폼) | 중간 (2-3개 도구) | 높음 (5-10개 서비스) | 중간 |
| **벤더 종속 탈출 비용** | 최소 (오픈 포맷) | **높음 (독점 → UNLOAD → 재적재)** | 중간 (AWS 종속) | 중간-높음 |
| **컨설팅/파트너 비용** | Databricks 파트너 에코시스템 | Snowflake 파트너 | AWS 파트너 | GCP 파트너 |
| **Reclustering 비용** | 없음 (Liquid Clustering) | **Snowflake Credit 소모** | 수동 VACUUM | 자동 (무료) |

{% hint style="warning" %}
**Snowflake 숨은 비용 주의**: (1) 스토리지 마크업은 대규모 데이터에서 수천만 원 차이가 납니다. (2) Automatic Reclustering은 백그라운드에서 Credit을 소모합니다. (3) ML 워크로드 추가 시 SageMaker + 데이터 복사 비용이 발생합니다. (4) 독점 포맷이므로 이관 시 UNLOAD + 재적재 비용이 큽니다.
{% endhint %}

---

## 비용 모니터링 도구 비교

### System Tables vs 경쟁사 비용 관리 도구

| 항목 | Databricks System Tables | Snowflake Resource Monitors | AWS Cost Explorer | BigQuery Budget | Fabric Cost Mgmt |
|---|---|---|---|---|---|
| **분석 방식** | SQL (자유로운 분석) | UI + 알림 | UI + API | UI + 알림 | UI |
| **세분화** | SKU/워크스페이스/클러스터/사용자별 | Warehouse별 | 서비스/태그별 | 프로젝트/데이터셋별 | Capacity별 |
| **실시간성** | 준실시간 (~15분) | 준실시간 | 수 시간 지연 | 준실시간 | 지연 있음 |
| **커스텀 알림** | SQL 기반 자유 설정 (Slack/Email) | Credit 한도 알림 | Budget 알림 | Budget 알림 | 기본 알림 |
| **예측** | SQL로 추세 분석 가능 | 미지원 | 비용 예측 | 미지원 | 미지원 |
| **BI 통합** | AI/BI Dashboard 또는 외부 BI | 내장 UI | QuickSight | Looker Studio | Power BI |
| **추가 비용** | 없음 | 없음 | 없음 | 없음 | 없음 |

### 비용 거버넌스 베스트 프랙티스

| 단계 | 활동 | Databricks 도구 |
|---|---|---|
| **가시화** | 워크스페이스/팀/사용자별 비용 대시보드 | System Tables + AI/BI Dashboard |
| **알림** | 일/주/월 비용 임계치 초과 시 알림 | System Tables + SQL Alert |
| **할당** | 팀별 비용 태깅 및 차지백(Chargeback) | Custom Tags + System Tables |
| **최적화** | 비효율 클러스터/쿼리 식별 및 개선 | Query History + Cluster Events |
| **예측** | 월말/분기말 비용 예측 | System Tables 추세 분석 |
| **정책** | 클러스터 크기 제한, Auto-terminate 강제 | Cluster Policies |

{% hint style="success" %}
**SA/SE 핵심 메시지**: Databricks는 **비용 투명성이 업계 최고** 입니다. (1) 스토리지는 클라우드 직접 과금으로 마크업 Zero. (2) System Tables로 DBU 단위까지 비용을 SQL로 분석. (3) 비용 이상 감지를 자동화. Snowflake는 Credit 기반으로 실제 비용 매핑이 어렵고, AWS는 5-10개 서비스의 비용을 각각 모니터링해야 합니다.
{% endhint %}
