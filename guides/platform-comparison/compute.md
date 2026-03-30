# 컴퓨팅 비교

## Serverless, Clusters, Scaling

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| **쿼리 엔진** | Photon (C++ 벡터화, 최대 12x) | 독점 MPP 엔진 | AQUA 가속 MPP | Dremel (서버리스) | Spark + Direct Lake |
| **서버리스 모드** | Serverless SQL Warehouse (즉시 시작) | 기본 서버리스 | Redshift Serverless (RPU) | On-demand / Editions | Fabric Capacity |
| **웜업 시간** | Serverless: 초 단위 | 수 초 ~ 수 분 | 분 단위 | 즉시 | 초 ~ 분 단위 |
| **자동 확장** | 지능형 자동 스케일링 + Queue 관리 | Multi-cluster Auto-scale | Concurrency Scaling (추가 비용) | Slot 기반 자동 확장 | Capacity Unit 기반 |
| **워크로드 격리** | SQL Warehouse별 독립 클러스터 | Warehouse별 격리 | WLM Queues (공유 리소스) | Reservation 기반 | Capacity 기반 분리 |
| **자동 최적화** | Predictive I/O + AI 기반 최적화 | 자동 쿼리 최적화 | Automatic WLM | 자동 최적화 | 자동 튜닝 |
| **인덱싱/클러스터링** | Liquid Clustering (자동 데이터 레이아웃) | Micro-partition Pruning | Sort Key, Distribution Key (수동) | Clustering (자동/수동) | 자동 관리 |
| **유휴 시 비용** | 자동 종료, 유휴 비용 Zero | 자동 일시중지 | Serverless: 자동, Provisioned: 과금 | On-demand: 쿼리당, Editions: 슬롯 | Capacity 단위 과금 |

{% hint style="info" %}
**Databricks Photon 엔진**: C++ 네이티브 벡터화 실행 엔진으로, TPC-DS 100TB 벤치마크에서 업계 최고 수준의 가격 대비 성능을 달성합니다. **Liquid Clustering**은 파티셔닝의 진화로, 데이터 레이아웃을 자동 최적화하여 수동 OPTIMIZE 없이 최적의 쿼리 성능을 유지합니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: BigQuery는 프로비저닝 없이 완전 서버리스로 동작하여 관리 오버헤드가 가장 낮습니다. Snowflake는 Auto-suspend/Auto-resume이 매우 직관적이며, 멀티 클러스터 자동 확장이 간단합니다.
{% endhint %}
