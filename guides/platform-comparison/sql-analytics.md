# SQL & Analytics 비교

## SQL 엔진 및 BI

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **ANSI SQL 호환**| 완전 호환 | 완전 호환 | PostgreSQL 호환 | GoogleSQL (일부 비표준) | T-SQL 호환 |
| **내장 BI**| AI/BI Dashboard (AI 기반 자동 시각화) | Snowsight | QuickSight | Looker + Looker Studio | Power BI (네이티브 통합) |
| **자연어 분석**| Genie Spaces + Genie Code (SQL+Python 생성/실행) | Cortex Analyst (SQL 전용) | QuickSight Q (제한적) | BigQuery NL Query (제한적) | Copilot in Power BI |
| **외부 BI 연동**| Tableau, Power BI, Looker 등 완전 호환 | 완전 호환 | 완전 호환 | 완전 호환 | Power BI 최적화, 타 BI 가능 |
| **AI 함수 in SQL**| `AI_QUERY`, `AI_GENERATE` 등 SQL 내 AI 호출 | Cortex LLM Functions | 미지원 (별도 서비스) | BigQuery ML (제한적) | 제한적 |
| **캐싱**| Delta Cache + Disk Cache + Result Cache | Result Cache + Local Disk Cache | Result Cache | BigQuery Cache (24h) | Direct Lake + 캐시 |
| **동시성**| SQL Warehouse별 독립, 자동 스케일링 | Multi-cluster Warehouse | Concurrency Scaling (추가 비용) | Slot 기반 | Capacity 기반 |
| **TPC-DS 성능**| 100TB 기준 업계 최고 수준 (Photon) | 상위권 | 상위권 | 상위권 | 상위권 |

{% hint style="info" %}
**Genie Code**: 비즈니스 사용자가 자연어로 "지난달 매출 트렌드를 분석해줘"라고 질문하면, SQL/Python 코드를 자동 생성하고 실행합니다. Cortex Analyst는 SQL만 생성하는 반면, Genie Code는 Python 분석까지 가능합니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: Snowflake는 SQL 중심 워크플로에서 가장 직관적인 사용 경험을 제공하며, Data Sharing이 매우 간편합니다. MS Fabric은 Power BI와의 네이티브 통합이 압도적이고 Direct Lake 모드로 데이터 복사 없이 대시보드를 구성합니다. BigQuery는 프로비저닝 없이 즉시 SQL을 실행할 수 있습니다.
{% endhint %}
