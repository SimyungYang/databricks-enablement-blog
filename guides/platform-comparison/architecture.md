# 아키텍처 비교

## 아키텍처 패러다임

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric/Synapse |
|---|---|---|---|---|---|
| **아키텍처 유형**| Lakehouse | Cloud DW | Cloud DW (MPP) | Serverless DW | Lakehouse (OneLake) |
| ** 스토리지 포맷**| Delta Lake (오픈소스, Linux Foundation) | 독점 포맷 (Iceberg 전환 중) | 독점 + S3 외부 테이블 | BigQuery Storage (독점) + BigLake | Delta Lake (OneLake) |
| ** 컴퓨팅-스토리지 분리**| 완전 분리 | 분리 (내부적) | RA3: 분리, DC: 결합 | 완전 분리 | 분리 (OneLake) |
| ** 데이터 저장 위치**| 고객 클라우드 스토리지 (S3/ADLS/GCS) | Snowflake 관리형 스토리지 | AWS 관리형 + S3 | Google 관리형 | OneLake (ADLS 기반) |
| ** 오픈 포맷**| Delta Lake + UniForm(Iceberg 호환) | Iceberg 전환 중 (독점 우선) | Iceberg/Hudi 외부 지원 | BigLake로 제한적 지원 | Delta Lake |
| ** 멀티클라우드**| AWS, Azure, GCP 동일 경험 | AWS, Azure, GCP 지원 | AWS Only | GCP Only (Omni 제한적) | Azure 중심 (일부 멀티클라우드) |
| ** 벤더 종속 리스크**| 최소 (오픈 포맷 + 고객 소유 스토리지) | 높음 (독점 포맷, 이관 시 COPY 필요) | 중간 (AWS 종속) | 중간-높음 (GCP 종속 + 독점 포맷) | 중간 (Azure/MS 생태계 종속) |

{% hint style="success" %}
**Databricks 차별점**: 데이터를 ** 고객의 클라우드 스토리지에 오픈 포맷(Delta Lake)** 으로 저장하므로, 다른 엔진(Spark, Trino, Flink 등)에서도 직접 읽을 수 있습니다. UniForm을 통해 Iceberg 호환도 자동 보장됩니다.
{% endhint %}

{% hint style="warning" %}
** 경쟁사 장점**: Snowflake는 완전 관리형 SaaS로 인프라 관리 부담이 거의 없고, BigQuery는 서버리스 아키텍처로 프로비저닝 자체가 불필요합니다. MS Fabric은 Microsoft 365/Power BI와의 긴밀한 통합이 강점입니다.
{% endhint %}

## 데이터 소유권 및 개방성

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| ** 데이터 소유권**| 고객 소유 (S3/ADLS/GCS) | 벤더 관리 스토리지 | AWS 관리형 | Google 관리형 | MS 관리형 (OneLake) |
| ** 포맷 잠금(Lock-in)**| Zero — 오픈 포맷 | 높음 — 독점 포맷 | 중간 | 중간-높음 | 낮음 (Delta Lake) |
| ** 데이터 공유 프로토콜**| Delta Sharing (오픈, 크로스 플랫폼) | Secure Data Sharing (Snowflake 내부) | Data Exchange (유료) | Analytics Hub | OneLake Sharing |
| ** 크로스 플랫폼 공유**| Spark, Pandas, Power BI, Tableau 등 수십 개 클라이언트 | Snowflake 계정 간만 | AWS 내부 | GCP 내부 + 제한적 외부 | MS 생태계 중심 |
