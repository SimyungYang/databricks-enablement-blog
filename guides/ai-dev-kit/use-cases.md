# 활용 사례

Builder App 에이전트와 대화하여 Databricks 워크스페이스를 자동으로 구성하는 실전 시나리오를 소개합니다.

## 각 사용 사례의 구현 전략

Builder App이 자연어 요청을 실제 Databricks 리소스로 변환하는 과정에는 일관된 전략이 있습니다:

### 에이전트의 의사결정 과정

1. **요청 분석**: 사용자의 자연어 요청에서 목표, 제약 조건, 선호도를 추출합니다
2. **스킬 로드**: 관련 스킬 파일을 로드하여 Databricks 권장 패턴을 참조합니다
3. **실행 계획 수립**: 필요한 도구 호출 순서와 의존성을 결정합니다
4. **순차 실행**: 각 도구를 호출하고, 이전 결과를 다음 단계의 입력으로 사용합니다
5. **검증**: 생성된 리소스의 상태를 확인하고 사용자에게 보고합니다

### 아키텍처 설계 고려사항

에이전트가 리소스를 생성할 때 고려하는 핵심 원칙들입니다:

| 원칙 | 적용 예시 |
|------|-----------|
| **Unity Catalog 기반** | 모든 테이블, Volume, 함수를 3-level 네임스페이스(catalog.schema.object)로 생성 |
| **메달리온 아키텍처** | DLT 파이프라인은 항상 Bronze → Silver → Gold 패턴으로 구성 |
| **Change Data Feed** | RAG용 테이블에는 반드시 CDF를 활성화하여 Vector Search 동기화 지원 |
| **서버리스 우선** | SQL Warehouse, Model Serving 등 서버리스 리소스를 우선 사용 |
| **거버넌스 내장** | 생성되는 모든 리소스에 적절한 권한과 태그를 자동 설정 |

{% hint style="info" %}
에이전트가 생성하는 모든 리소스는 **Databricks 베스트 프랙티스를 따릅니다**. 이는 29개의 스킬 파일에 인코딩된 패턴 덕분입니다. 하지만 프로덕션 환경에 적용하기 전에 반드시 검토하세요.
{% endhint %}

---

## 시나리오 1: 자연어로 데이터 분석 환경 구축

> " **매출 데이터 분석 환경을 만들어줘**"

에이전트가 테이블 생성부터 대시보드 배포, Genie Space 구성까지 한 번의 대화로 자동 수행합니다.

### 구현 전략

이 시나리오에서 에이전트는 다음 전략으로 작업을 수행합니다:
- **`synthetic-data` 스킬** 을 로드하여 현실적인 샘플 데이터를 생성합니다
- **`dashboard` 스킬** 을 참조하여 Lakeview 대시보드 JSON 구조를 올바르게 생성합니다
- **`genie-space` 스킬** 을 활용하여 인스트럭션과 테이블 매핑을 자동 구성합니다

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

> " **고객 매뉴얼 기반 Q&A 챗봇을 만들어줘**"

에이전트가 문서 업로드, 벡터 인덱스 생성, Knowledge Assistant 배포까지 자동 수행합니다.

### 구현 전략

RAG 에이전트 구축은 여러 서비스(Volume, Vector Search, Knowledge Assistant)를 순차적으로 연결해야 하는 복잡한 작업입니다. 에이전트는 다음 전략을 사용합니다:
- **`vector-search` 스킬** 로 올바른 인덱스 설정(Delta Sync, Databricks 관리 임베딩)을 결정합니다
- **`agent-bricks` 스킬** 로 Knowledge Assistant의 인스트럭션을 작성하고 Vector Search Index를 연결합니다
- 각 단계에서 이전 단계의 **출력(Volume 경로, Index 이름 등)을 다음 단계의 입력으로 전달** 합니다

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

> " **모델 학습부터 배포까지 자동화 파이프라인을 구성해줘**"

에이전트가 노트북 생성, Job 스케줄링, 모니터링 설정을 자동 수행합니다.

### 구현 전략

MLOps 파이프라인은 **코드 생성 + 인프라 구성** 을 동시에 수행해야 하는 시나리오입니다:
- **Built-in Write 도구** 로 Python 노트북 코드를 생성합니다 (MLflow 로깅, 모델 평가 등 포함)
- **`upload_file` MCP 도구** 로 생성된 노트북을 Workspace에 업로드합니다
- **`manage_jobs` MCP 도구** 로 멀티 태스크 DAG Job을 구성하고 스케줄을 설정합니다
- 에이전트는 **태스크 간 의존성**(피처 엔지니어링 → 학습 → 배포)을 자동으로 설정합니다

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

> " **고객 미팅용 데모 환경을 30분 안에 만들어줘**"

에이전트가 합성 데이터 생성, 파이프라인 구성, 대시보드 배포까지 한 번에 수행합니다.

### 구현 전략

데모 환경 구축은 **가장 많은 도구를 조합** 하는 시나리오입니다. 에이전트의 아키텍처 설계 전략:
- **카탈로그 격리**: 데모용 전용 카탈로그/스키마를 생성하여 기존 데이터와 분리합니다
- **현실적 합성 데이터**: `synthetic-data` 스킬이 업종별(리테일, 제조, 금융 등) 현실적인 데이터 패턴을 생성합니다
- **메달리온 아키텍처**: `sdp` 스킬로 Bronze-Silver-Gold 패턴의 DLT 노트북을 생성합니다
- **엔드투엔드 스토리라인**: 데이터 수집 → 정제 → 분석 → 시각화 → 자연어 질의까지 완전한 데모 흐름을 구성합니다

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

## 효과적인 활용을 위한 팁

### 에이전트에게 더 좋은 결과를 얻는 방법

| 팁 | 설명 | 예시 |
|-----|------|------|
| **목표를 명확히** | 최종 결과물의 형태를 구체적으로 설명 | "매출 추이 라인 차트 + 카테고리 파이 차트" |
| **제약 조건 명시** | 사용할 카탈로그, 스키마, 클러스터 등을 지정 | "main.demo 스키마에 만들어줘" |
| **단계별 검증** | 각 단계 결과를 확인 후 다음 진행 | "먼저 테이블만 만들어줘... 좋아, 이제 대시보드를 만들어" |
| **수정 요청** | 결과가 마음에 들지 않으면 구체적으로 수정 요청 | "파이 차트 대신 바 차트로 바꿔줘" |

### 주의사항

- 에이전트가 생성한 리소스는 **프로덕션 적용 전 반드시 검토** 하세요
- 합성 데이터는 데모/테스트 용도이며, 실제 데이터를 대체하지 않습니다
- 삭제 작업(`delete_*`)은 **되돌릴 수 없으므로** 신중하게 요청하세요
- 대규모 작업(수십 개 테이블 생성 등)은 단계별로 나누어 실행하는 것이 안정적입니다

## 참고 링크

- [AI Dev Kit GitHub](https://github.com/databricks-solutions/ai-dev-kit)
- [Databricks MCP Server Tools](tools.md)
- [Genie Space 가이드](../genie-space/README.md)
- [Agent Bricks 가이드](../agent-bricks/README.md)
