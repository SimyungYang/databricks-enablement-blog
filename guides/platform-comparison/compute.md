# 컴퓨팅 비교

## Serverless, Clusters, Scaling

| 항목 | Databricks | Snowflake | AWS Redshift | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| ** 쿼리 엔진**| Photon (C++ 벡터화, 최대 12x) | 독점 MPP 엔진 | AQUA 가속 MPP | Dremel (서버리스) | Spark + Direct Lake |
| ** 서버리스 모드**| Serverless SQL Warehouse (즉시 시작) | 기본 서버리스 | Redshift Serverless (RPU) | On-demand / Editions | Fabric Capacity |
| ** 웜업 시간**| Serverless: 초 단위 | 수 초 ~ 수 분 | 분 단위 | 즉시 | 초 ~ 분 단위 |
| ** 자동 확장**| 지능형 자동 스케일링 + Queue 관리 | Multi-cluster Auto-scale | Concurrency Scaling (추가 비용) | Slot 기반 자동 확장 | Capacity Unit 기반 |
| ** 워크로드 격리**| SQL Warehouse별 독립 클러스터 | Warehouse별 격리 | WLM Queues (공유 리소스) | Reservation 기반 | Capacity 기반 분리 |
| ** 자동 최적화**| Predictive I/O + AI 기반 최적화 | 자동 쿼리 최적화 | Automatic WLM | 자동 최적화 | 자동 튜닝 |
| ** 인덱싱/클러스터링**| Liquid Clustering (자동 데이터 레이아웃) | Micro-partition Pruning | Sort Key, Distribution Key (수동) | Clustering (자동/수동) | 자동 관리 |
| ** 유휴 시 비용**| 자동 종료, 유휴 비용 Zero | 자동 일시중지 | Serverless: 자동, Provisioned: 과금 | On-demand: 쿼리당, Editions: 슬롯 | Capacity 단위 과금 |

{% hint style="info" %}
**Databricks Photon 엔진**: C++ 네이티브 벡터화 실행 엔진으로, TPC-DS 100TB 벤치마크에서 업계 최고 수준의 가격 대비 성능을 달성합니다. **Liquid Clustering** 은 파티셔닝의 진화로, 데이터 레이아웃을 자동 최적화하여 수동 OPTIMIZE 없이 최적의 쿼리 성능을 유지합니다.
{% endhint %}

{% hint style="warning" %}
** 경쟁사 장점**: BigQuery는 프로비저닝 없이 완전 서버리스로 동작하여 관리 오버헤드가 가장 낮습니다. Snowflake는 Auto-suspend/Auto-resume이 매우 직관적이며, 멀티 클러스터 자동 확장이 간단합니다.
{% endhint %}

---

## Photon 엔진 상세

### Photon이란?

**Photon** 은 Databricks가 자체 개발한 **C++ 네이티브 벡터화 쿼리 실행 엔진** 입니다. Apache Spark의 JVM 기반 엔진을 대체하여 SQL 및 DataFrame 워크로드에서 ** 최대 12배 성능 향상** 을 달성합니다.

| 특성 | Spark 기본 엔진 (JVM) | Photon (C++ 네이티브) |
|---|---|---|
| ** 언어**| Java/Scala (JVM) | C++ (네이티브) |
| ** 실행 방식**| Volcano 모델 (Row-at-a-time) | 벡터화 (Batch-at-a-time, SIMD 활용) |
| ** 메모리 관리**| JVM GC 의존 (일시 정지 발생) | 직접 메모리 관리 (GC 없음) |
| **CPU 활용**| JVM 오버헤드로 비효율 | CPU 캐시 최적화, SIMD 연산 |
| **I/O 최적화**| 기본 Parquet/Delta 리더 | Predictive I/O (AI 기반 I/O 최적화) |
| ** 호환성**| Spark SQL 100% | Spark SQL 100% (투명한 대체) |

### Photon 성능 벤치마크

| 벤치마크 | 결과 |
|---|---|
| **TPC-DS 100TB**| 업계 최고 수준의 가격 대비 성능 (공식 기록) |
| ** 일반 SQL 워크로드**| Spark 기본 대비 평균 3-8x 빠름 |
| ** 조인 집약 쿼리**| 최대 12x 성능 향상 |
| ** 문자열 처리**| C++ 네이티브로 JVM 대비 5-10x |
| ** 집계 연산**| 벡터화로 3-5x 향상 |

{% hint style="info" %}
**Photon은 추가 설정 없이 자동 적용** 됩니다. SQL Warehouse에서는 기본 활성화되어 있으며, All-Purpose Cluster에서도 Photon 옵션을 켜면 즉시 적용됩니다. 기존 Spark SQL 코드를 수정할 필요가 없습니다.
{% endhint %}

### 경쟁사 쿼리 엔진과의 비교

| 항목 | Databricks Photon | Snowflake 엔진 | Redshift AQUA | BigQuery Dremel |
|---|---|---|---|---|
| ** 엔진 유형**| C++ 벡터화 | 독점 MPP (마이크로 파티션) | FPGA 가속 캐시 계층 | 서버리스 분산 엔진 |
| ** 오픈소스 여부**| 비공개 (Delta Lake는 오픈소스) | 비공개 | 비공개 | 비공개 |
| ** 벡터화 실행**| 네이티브 SIMD | 일부 | 일부 (AQUA) | 컬럼 기반 벡터화 |
| ** 적응형 쿼리 실행**| AQE (Adaptive Query Execution) | 자동 최적화 | 자동 WLM | 자동 최적화 |
| ** 캐싱 계층**| Delta Cache + Disk Cache + Result Cache | Result Cache + Local Disk | Result Cache + AQUA Cache | Result Cache (24시간) |
| ** 동시성 처리**| Warehouse별 독립 + 자동 스케일링 | Multi-cluster Warehouse | Concurrency Scaling (추가 비용) | Slot 기반 자동 |

---

## Serverless vs Classic 컴퓨팅 상세

### Databricks 컴퓨팅 옵션

| 옵션 | 용도 | 관리 수준 | 시작 시간 | 비용 특성 |
|---|---|---|---|---|
| **Serverless SQL Warehouse**| SQL 분석, BI 쿼리 | 완전 관리형 | 초 단위 | DBU/초, 유휴 시 Zero |
| **Serverless Compute**| Notebooks, Jobs, DLT | 완전 관리형 | 초 단위 | DBU/초, 유휴 시 Zero |
| **Classic SQL Warehouse**| SQL 분석 (커스터마이징 필요 시) | 반자동 | 분 단위 | DBU/초 + 인스턴스 비용 |
| **All-Purpose Cluster**| 대화형 개발, 탐색 분석 | 수동/반자동 | 분 단위 | DBU/초 + 인스턴스 비용 |
| **Job Cluster**| 스케줄 Job 전용 (일회성) | 자동 생성/종료 | 분 단위 | DBU/초 + 인스턴스 비용 (Job 종료 시 자동 삭제) |

### Serverless 선택 가이드

```
워크로드 특성에 따른 Databricks 컴퓨팅 선택:

SQL 분석/BI 쿼리
  └─ Serverless SQL Warehouse (기본 권장)

ETL/배치 Job
  └─ Serverless Compute (권장) 또는 Job Cluster (커스터마이징 필요 시)

대화형 개발/탐색
  └─ Serverless Compute (권장) 또는 All-Purpose Cluster (라이브러리 필요 시)

ML 학습 (GPU)
  └─ All-Purpose Cluster 또는 Job Cluster (GPU 인스턴스 지정)

스트리밍 (24/7)
  └─ Classic Cluster (Always-on) — Serverless 대비 예약 인스턴스로 비용 절감
```

### 경쟁사 서버리스 비교

| 항목 | Databricks Serverless | Snowflake | Redshift Serverless | BigQuery | MS Fabric |
|---|---|---|---|---|---|
| ** 프로비저닝**| 불필요 | 불필요 | 불필요 | 불필요 | Capacity 설정 필요 |
| ** 시작 시간**| 초 단위 (웜 풀) | 수 초 ~ 수 분 | 수십 초 ~ 수 분 | 즉시 | 초 ~ 분 |
| ** 자동 종료**| 비활성 시 즉시 종료 | Auto-suspend (최소 60초) | 비활성 시 종료 | 항상 대기 (On-demand) | Capacity 유지 |
| ** 스케일 업**| 자동 (쿼리 복잡도 기반) | Warehouse 크기 변경 (수동/자동) | RPU 자동 조절 | Slot 자동 확장 (Editions) | Capacity 변경 |
| ** 스케일 아웃**| 자동 (동시성 기반) | Multi-cluster 자동 | 자동 | Slot 추가 | Capacity 추가 |
| ** 최소 과금**| 초 단위 (최소 없음) | 60초 최소 | RPU 초 단위 | 10MB 최소 스캔 | 시간 단위 |
| **GPU 지원**| 네이티브 (ML/AI 워크로드) | Container Services (제한적) | N/A | N/A (Vertex AI 별도) | 제한적 |
| ** 워크로드 범위**| SQL + ETL + ML + Notebooks | SQL Only | SQL Only | SQL Only | SQL + Spark |

---

## 자동 스케일링 메커니즘 비교

### Databricks 지능형 자동 스케일링

| 기능 | 설명 |
|---|---|
| **SQL Warehouse 자동 스케일링**| 동시 쿼리 수에 따라 클러스터 수를 자동 조절 (Min/Max 설정) |
| **Queue 관리**| 리소스 부족 시 쿼리를 큐에 대기시키고, 스케일 아웃 후 자동 처리 |
| **Spot Instance 활용**| Worker 노드에 Spot/Preemptible 인스턴스 혼용으로 비용 절감 |
| **Cluster Autoscaling**| 작업 부하에 따라 Worker 수 자동 조절 (Min/Max Workers 설정) |
| **Predictive Optimization**| 과거 패턴 기반으로 최적 클러스터 크기 사전 추천 |

### 경쟁사 자동 스케일링

| 플랫폼 | 스케일링 방식 | 장점 | 단점 |
|---|---|---|---|
| **Snowflake Multi-cluster**| Warehouse 개수를 자동 확장 (Economy/Standard 모드) | 설정 간단, 직관적 | 스케일 업은 수동, 크기 변경 시 재시작 |
| **Redshift Concurrency Scaling**| 동시성 초과 시 임시 클러스터 자동 추가 | AWS 네이티브 | ** 추가 비용 발생**(무료 크레딧 소진 후) |
| **BigQuery Slot Autoscaling**| Edition 모드에서 슬롯 자동 조절 | 완전 자동, 관리 불필요 | 비용 예측 어려움 (피크 시 급증) |
| **Fabric Capacity**| Capacity Unit 기반 고정 할당 | 예측 가능 | 탄력성 부족, 버스트 시 스로틀링 |

### 스케일링 시나리오별 동작 비교

** 시나리오: 동시 쿼리 50→200으로 급증 (월말 보고서)**

| 플랫폼 | 동작 | 소요 시간 | 추가 비용 |
|---|---|---|---|
| **Databricks**| Serverless SQL Warehouse가 자동 클러스터 추가 | 초 단위 | 사용한 만큼만 (DBU) |
| **Snowflake**| Multi-cluster Warehouse 자동 확장 (Max 설정 필요) | 수 분 | 추가 Warehouse 크레딧 |
| **Redshift**| Concurrency Scaling 활성화 (임시 클러스터) | 수 분 | 추가 비용 (무료 크레딧 초과 시) |
| **BigQuery**| Slot Autoscaling (Editions) 또는 큐 대기 (On-demand) | 즉시 (슬롯 내) | Editions: 추가 슬롯 비용 |
| **Fabric**| Capacity 초과 시 스로틀링 → 수동 업그레이드 | 분 ~ 시간 | Capacity 업그레이드 비용 |

---

## 비용 모델 상세: DBU vs 크레딧 vs 슬롯

### 과금 단위 개념 비교

| 항목 | Databricks DBU | Snowflake Credit | BigQuery Slot | Redshift RPU |
|---|---|---|---|---|
| ** 정의**| 처리 능력의 정규화된 단위 | 가상 웨어하우스 사용량 단위 | 쿼리 실행 컴퓨팅 단위 | 서버리스 컴퓨팅 단위 |
| ** 과금 기준**| 초 단위 | 초 단위 (최소 60초) | 초 단위 (Editions) / TB 스캔 (On-demand) | 초 단위 |
| ** 가격 범위 (리스트)**| $0.07-0.65/DBU (워크로드별) | $2-4/Credit (에디션별) | $0.04/Slot-hour (Editions) / $6.25/TB (On-demand) | $0.375/RPU-hour |
| ** 워크로드별 차등**| SQL: 낮음, ML: 높음, Photon: 중간 | 동일 (Warehouse 크기로 조절) | 동일 (슬롯 수로 조절) | 동일 (RPU 수로 조절) |
| ** 유휴 비용**| Zero (자동 종료) | Zero (Auto-suspend) | On-demand: Zero / Editions: Baseline 유지비 | Zero (Serverless) |
| ** 예약 할인**| 1년: ~25% / 3년: ~40% | Capacity: ~15-25% | Commitment: ~25-40% | Reserved: ~30-40% |

### Databricks DBU 워크로드별 가격 (참고)

| 워크로드 유형 | DBU 단가 범위 (리스트) | 특징 |
|---|---|---|
| **Jobs Compute**| $0.10-0.15/DBU | ETL, 배치 처리 — 가장 저렴 |
| **Jobs Compute (Serverless)**| $0.07-0.10/DBU | 서버리스 Job — 관리 비용 절감 |
| **All-Purpose Compute**| $0.40-0.55/DBU | 대화형 개발 — 가장 비쌈 |
| **SQL Warehouse (Serverless)**| $0.22-0.30/DBU | SQL 분석 — 중간 |
| **SQL Warehouse (Classic)**| $0.22-0.30/DBU | SQL 분석 — 인스턴스 비용 별도 |
| **Model Serving**| $0.06-0.10/DBU | 모델 추론 — 저렴 |
| **Serverless Real-Time Inference**| $0.07/DBU | 실시간 추론 |

{% hint style="warning" %}
** 가격은 클라우드(AWS/Azure/GCP)와 리전에 따라 다릅니다.** 위 수치는 참고용이며, 정확한 가격은 [Databricks Pricing 페이지](https://www.databricks.com/product/pricing)에서 확인하세요. 커밋 사용(PAYGO/Commit) 계약으로 추가 할인이 가능합니다.
{% endhint %}

---

## Liquid Clustering vs 경쟁사 데이터 레이아웃

### 데이터 레이아웃 최적화 비교

| 항목 | Databricks Liquid Clustering | Snowflake Micro-partition | Redshift Sort Key | BigQuery Clustering |
|---|---|---|---|---|
| ** 방식**| 자동 인크리멘탈 클러스터링 | 자동 마이크로 파티셔닝 + 자동 Reclustering | 수동 Sort Key / Distribution Key 설정 | 수동/자동 클러스터링 칼럼 설정 |
| ** 변경 용이성**| 언제든 클러스터링 키 변경 가능 (ALTER TABLE) | 자동 (변경 불필요) | Sort Key 변경 시 테이블 재구성 필요 | 클러스터링 칼럼 변경 시 재생성 |
| ** 자동 관리**| 증분 자동 (새 데이터에만 적용) | 완전 자동 | 수동 VACUUM 필요 | 자동 Re-clustering |
| ** 추가 비용**| 없음 (쓰기 시 자동 적용) | Reclustering 크레딧 소모 | VACUUM/ANALYZE 시간 | 없음 |
| ** 파티셔닝 대체**| Liquid Clustering이 파티셔닝을 완전 대체 | 마이크로 파티셔닝이 기본 | 파티셔닝 별도 | 파티셔닝 + 클러스터링 병행 |

{% hint style="info" %}
**Liquid Clustering의 혁신**: 기존 Hive-style 파티셔닝의 문제점(파티션 키 변경 불가, 소규모 파티션 문제, Z-Order 비용)을 완전히 해결합니다. `ALTER TABLE ... CLUSTER BY (col1, col2)` 한 줄로 적용되며, 기존 데이터는 점진적으로 재배치됩니다.
{% endhint %}

---

## GPU 컴퓨팅 및 ML 학습 인프라 비교

| 항목 | Databricks | Snowflake | AWS SageMaker | GCP Vertex AI | MS Fabric |
|---|---|---|---|---|---|
| **GPU 클러스터**| 네이티브 지원 (A100, H100, L4 등) | Snowpark Container Services (제한적) | 네이티브 지원 (광범위 GPU 옵션) | 네이티브 지원 (TPU 포함) | 제한적 |
| ** 분산 학습**| Spark + Horovod / DeepSpeed / Ray | 미지원 | SageMaker 분산 학습 | Vertex AI 분산 학습 | 미지원 |
| ** 모델 서빙 GPU**| GPU Model Serving Endpoint | Container Services (제한적) | SageMaker Endpoints | Vertex AI Endpoints | 제한적 |
| ** 스팟 GPU**| Spot Instance 지원으로 비용 절감 | N/A | Spot Training 지원 | Preemptible VM 지원 | N/A |
| **MLflow 통합**| 네이티브 (실험→레지스트리→서빙) | 미지원 | SageMaker Experiments (별도) | Vertex AI Experiments (별도) | MLflow 연동 가능 |
| ** 데이터 접근**| 동일 플랫폼 (복사 불필요) | 제한적 (Snowpark 내) | S3에서 복사 필요 | GCS에서 복사 필요 | 제한적 |

### GPU 인스턴스 유형별 용도

| GPU 유형 | Databricks 지원 | 주요 용도 | 비용 수준 |
|---|---|---|---|
| **NVIDIA T4**| 지원 (AWS/Azure/GCP) | 추론, 경량 학습 | 저렴 |
| **NVIDIA A10G**| 지원 (AWS) | 중간 규모 학습/추론 | 중간 |
| **NVIDIA L4**| 지원 (GCP/AWS) | 추론 최적화 | 중간 |
| **NVIDIA A100 (40/80GB)**| 지원 (AWS/Azure/GCP) | 대규모 학습, 파인튜닝 | 높음 |
| **NVIDIA H100**| 지원 (AWS/Azure) | 초대규모 학습, LLM 파인튜닝 | 매우 높음 |

{% hint style="success" %}
**SA/SE 핵심 메시지**: Databricks는 ** 동일 플랫폼에서 CPU(SQL/ETL)와 GPU(ML/AI) 워크로드를 모두 실행** 할 수 있으며, Unity Catalog로 데이터→모델→서빙 전체 거버넌스를 통합합니다. SageMaker나 Vertex AI는 데이터 플랫폼과 분리되어 있어 데이터 복사와 거버넌스 이중화가 불가피합니다.
{% endhint %}

---

## 워크로드 격리 및 리소스 관리

### 워크로드 격리 방식 비교

| 항목 | Databricks | Snowflake | Redshift | BigQuery | Fabric |
|---|---|---|---|---|---|
| ** 격리 단위**| SQL Warehouse / Cluster (완전 독립) | Virtual Warehouse (완전 독립) | WLM Queue (공유 리소스) | Reservation / Slot Pool | Capacity (공유) |
| ** 물리적 격리**| 독립 VM 클러스터 | 독립 컴퓨팅 리소스 | 동일 클러스터 내 큐 | 논리적 슬롯 분리 | 논리적 분리 |
| ** 상호 영향**| Zero (완전 격리) | Zero (완전 격리) | 있음 (WLM 공유) | 있음 (슬롯 공유 가능) | 있음 (Capacity 공유) |
| ** 설정 편의성**| SQL Warehouse 생성만으로 격리 | Warehouse 생성만으로 격리 | WLM 규칙 설정 복잡 | Reservation 설정 | Capacity 분리 설정 |

### Databricks 워크로드 격리 베스트 프랙티스

```
권장 구성 (중대형 조직):

1. BI/리포팅용 SQL Warehouse (Serverless, Small, Auto-scale 1-3)
   └─ 주 사용자: 비즈니스 분석가, BI 도구

2. Ad-hoc 분석용 SQL Warehouse (Serverless, Medium, Auto-scale 1-5)
   └─ 주 사용자: 데이터 분석가, Genie Code 사용자

3. ETL/배치용 Serverless Compute
   └─ 주 사용자: 데이터 엔지니어, 스케줄 Job

4. ML 학습용 GPU Cluster (Job Cluster, 필요 시 생성)
   └─ 주 사용자: 데이터 사이언티스트, ML 엔지니어

5. 개발/테스트용 All-Purpose Cluster (소규모, Auto-terminate 30분)
   └─ 주 사용자: 개발자, 탐색 분석
```

{% hint style="info" %}
** 비용 최적화 팁**: SQL Warehouse와 Serverless Compute는 유휴 시 자동 종료되므로 비용이 사용량에 정확히 비례합니다. All-Purpose Cluster는 Auto-terminate를 반드시 설정하여 유휴 비용을 방지하세요.
{% endhint %}
