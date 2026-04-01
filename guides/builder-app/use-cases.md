# 활용 사례

Builder App 에이전트와 대화하여 Databricks 워크스페이스를 자동으로 구성하는 실전 시나리오를 소개합니다.

---

## 시나리오 1: 자연어로 데이터 분석 환경 구축

> "**매출 데이터 분석 환경을 만들어줘**"

에이전트가 테이블 생성부터 대시보드 배포, Genie Space 구성까지 한 번의 대화로 자동 수행합니다.

### 에이전트 수행 흐름

```
사용자: "매출 데이터 분석 환경을 만들어줘.
       월별 매출 추이와 카테고리별 비중을 볼 수 있게 해줘."

에이전트 수행 단계:
1. [manage_uc_objects] → Catalog/Schema 생성
2. [execute_sql_multi] → 매출 테이블 생성 + 샘플 데이터 INSERT
3. [create_or_update_dashboard] → 월별 추이 차트 + 카테고리 파이 차트 구성
4. [publish_dashboard] → 대시보드 배포
5. [create_or_update_genie] → Genie Space 생성 (인스트럭션 + 테이블 매핑)
```

### 결과물

| 생성 리소스 | 설명 |
|---|---|
| `main.analytics.monthly_sales` | 월별 매출 집계 테이블 |
| AI/BI 대시보드 | 매출 추이 라인 차트 + 카테고리 파이 차트 |
| Genie Space | "이번 달 매출은?", "카테고리별 매출 비교" 등 자연어 질의 가능 |

{% hint style="tip" %}
에이전트는 `synthetic-data` 스킬을 활용하여 데모용 샘플 데이터도 자동 생성합니다. 실제 데이터가 없어도 바로 분석 환경을 체험할 수 있습니다.
{% endhint %}

---

## 시나리오 2: RAG 에이전트 구축

> "**고객 매뉴얼 기반 Q&A 챗봇을 만들어줘**"

에이전트가 문서 업로드, 벡터 인덱스 생성, Knowledge Assistant 배포까지 자동 수행합니다.

### 에이전트 수행 흐름

```
사용자: "products 폴더에 있는 PDF 매뉴얼을 기반으로
       고객이 제품 질문을 할 수 있는 RAG 챗봇을 만들어줘."

에이전트 수행 단계:
1. [manage_uc_objects] → Volume 생성
2. [upload_to_volume] → PDF 파일을 Volume에 업로드
3. [execute_sql] → 문서 파싱 + 청킹 테이블 생성
4. [create_or_update_vs_endpoint] → Vector Search Endpoint 생성
5. [create_or_update_vs_index] → 문서 벡터 인덱스 생성
6. [manage_ka] → Knowledge Assistant 생성 (VS Index 연결)
```

### 결과물

| 생성 리소스 | 설명 |
|---|---|
| UC Volume | 원본 PDF 문서 저장소 |
| 청킹 테이블 | 문서를 검색 가능한 청크 단위로 분할 |
| Vector Search Index | 문서 임베딩 기반 유사도 검색 |
| Knowledge Assistant | 배포된 RAG 챗봇 (Review App에서 테스트 가능) |

{% hint style="info" %}
에이전트는 `agent-bricks` 스킬과 `vector-search` 스킬을 참조하여 Databricks 권장 패턴에 맞는 RAG 파이프라인을 구성합니다.
{% endhint %}

---

## 시나리오 3: MLOps 파이프라인 구성

> "**모델 학습부터 배포까지 자동화 파이프라인을 구성해줘**"

에이전트가 노트북 생성, Job 스케줄링, 모니터링 설정을 자동 수행합니다.

### 에이전트 수행 흐름

```
사용자: "고객 이탈 예측 모델을 매일 재학습하고
       배포하는 파이프라인을 만들어줘."

에이전트 수행 단계:
1. [Write] → 피처 엔지니어링 노트북 생성 (Python)
2. [Write] → 모델 학습 노트북 생성 (MLflow 로깅 포함)
3. [Write] → 모델 평가 및 등록 노트북 생성
4. [upload_file] → 노트북을 Workspace에 업로드
5. [manage_jobs] → 멀티 태스크 DAG Job 생성:
   - Task 1: 피처 엔지니어링
   - Task 2: 모델 학습 (Task 1 완료 후)
   - Task 3: 모델 평가 및 배포 (Task 2 완료 후)
6. [manage_jobs] → 매일 06:00 스케줄 설정
```

### 결과물

| 생성 리소스 | 설명 |
|---|---|
| 노트북 3개 | 피처 엔지니어링, 모델 학습, 평가/배포 |
| Databricks Job | 멀티 태스크 DAG (매일 06:00 자동 실행) |
| MLflow Experiment | 학습 결과 추적 및 모델 비교 |

{% hint style="warning" %}
에이전트가 생성한 노트북은 템플릿 수준입니다. 실제 프로덕션 적용 전에 데이터 소스, 피처 로직, 모델 하이퍼파라미터를 반드시 검토하세요.
{% endhint %}

---

## 시나리오 4: 데모 환경 빠른 구축

> "**고객 미팅용 데모 환경을 30분 안에 만들어줘**"

에이전트가 합성 데이터 생성, 파이프라인 구성, 대시보드 배포까지 한 번에 수행합니다.

### 에이전트 수행 흐름

```
사용자: "리테일 고객에게 Databricks를 보여줄 데모 환경을 만들어줘.
       IoT 센서 데이터 → 파이프라인 → 대시보드 흐름으로 구성해줘."

에이전트 수행 단계:
1. [manage_uc_objects] → demo 카탈로그 + 스키마 생성
2. [execute_sql_multi] → IoT 센서 합성 데이터 테이블 생성
3. [Write + upload_file] → SDP 노트북 생성 및 업로드
   - Bronze: Raw 센서 데이터 수집
   - Silver: 데이터 정제 및 품질 검증
   - Gold: 집계 테이블 생성
4. [create_or_update_pipeline] → DLT 파이프라인 생성
5. [start_update] → 파이프라인 실행
6. [create_or_update_dashboard] → 실시간 모니터링 대시보드 생성
7. [publish_dashboard] → 대시보드 배포
8. [create_or_update_genie] → Genie Space 구성
```

### 결과물

| 생성 리소스 | 설명 |
|---|---|
| 합성 데이터 | IoT 센서 데이터 (온도, 습도, 압력) |
| DLT 파이프라인 | Bronze → Silver → Gold 메달리온 아키텍처 |
| AI/BI 대시보드 | 센서 현황, 이상치 알림, 추이 차트 |
| Genie Space | "지난 1시간 평균 온도는?" 등 자연어 질의 |

{% hint style="tip" %}
에이전트는 `sdp` 스킬을 참조하여 Spark Declarative Pipeline 패턴에 맞는 노트북을 생성합니다. 생성된 파이프라인은 실제 DLT 파이프라인으로 바로 실행할 수 있습니다.
{% endhint %}

---

## 시나리오별 난이도 및 소요 시간

| 시나리오 | 난이도 | 예상 소요 시간 | 주요 MCP 도구 |
|---|---|---|---|
| 데이터 분석 환경 | 낮음 | 5~10분 | execute_sql, dashboard, genie |
| RAG 에이전트 | 중간 | 15~20분 | upload_to_volume, vs_index, manage_ka |
| MLOps 파이프라인 | 중간 | 10~15분 | manage_jobs, upload_file |
| 데모 환경 구축 | 높음 | 20~30분 | 전체 도구 활용 |

{% hint style="info" %}
위 소요 시간은 에이전트가 자동 수행하는 시간입니다. 사람이 직접 구성하면 수 시간에서 수일이 걸리는 작업을 자연어 몇 문장으로 완료할 수 있습니다.
{% endhint %}

---

## 참고 링크

- [AI Dev Kit GitHub](https://github.com/databricks-solutions/ai-dev-kit)
- [Databricks MCP Server Tools](tools.md)
- [Genie Space 가이드](../genie-space/README.md)
- [Agent Bricks 가이드](../agent-bricks/README.md)
