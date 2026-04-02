# 평가 & 배포

---

## MLflow 기반 평가

Agent Bricks는 MLflow와 긴밀하게 통합되어 에이전트 품질을 체계적으로 평가합니다.

| 기능 | 설명 |
|------|------|
| **Tracing** | 에이전트 실행의 전체 과정을 추적 (Production Monitoring for MLflow 활성화 필요) |
| **AI Judge** | LLM 기반 자동 품질 판정 |
| **Synthetic Task Generation** | 합성 데이터로 대규모 테스트 |
| **라벨링된 데이터셋** | UC 테이블로 Import/Export하여 체계적 관리 |

---

## MLflow Tracing으로 에이전트 동작 추적

Tracing은 에이전트의 각 단계(검색, LLM 호출, 도구 실행 등)를 시각적으로 추적합니다.

### 활성화 방법

1. 워크스페이스에서 **Production Monitoring for MLflow** 활성화
2. 에이전트 Build 탭에서 질문 입력 후 **View Trace** 클릭

### Trace에서 확인할 수 있는 정보

| 항목 | 설명 |
|------|------|
| **Retrieval** | 어떤 문서/청크가 검색되었는지, 유사도 점수 |
| **LLM Call** | 어떤 프롬프트가 전송되었는지, 토큰 사용량 |
| **Tool Execution** | UC Function, MCP 서버 호출 결과 |
| **Routing Decision** | Supervisor가 어떤 서브 에이전트를 선택했는지, 그 이유 |
| **Latency** | 각 단계별 소요 시간 |

{% hint style="info" %}
**디버깅 팁**: 에이전트가 엉뚱한 답변을 하면, Trace에서 Retrieval 단계를 먼저 확인하세요. 관련 없는 문서가 검색되고 있다면 Knowledge Source의 Content Description을 조정해야 합니다.
{% endhint %}

---

## AI Judge (LLM-as-Judge) 설정

AI Judge는 LLM을 평가자로 사용하여 에이전트 응답의 품질을 자동으로 판정합니다.

### 평가 메트릭

| 메트릭 | 설명 | 측정 대상 |
|--------|------|-----------|
| **Correctness** | 응답이 기대 답변과 일치하는지 | 라벨링된 기대 답변 대비 정확도 |
| **Groundedness** | 응답이 검색된 문서에 근거하는지 | 환각(hallucination) 방지 |
| **Relevance** | 질문에 대한 응답의 관련성 | 주제 이탈 방지 |
| **Safety** | 유해하거나 부적절한 내용이 없는지 | 안전성 검증 |
| **Chunk Relevance** | 검색된 청크가 질문과 관련 있는지 | RAG 검색 품질 |

### 설정 방법

1. **Examples 탭** 에서 라벨링된 질문-답변 쌍 추가 (최소 20개 권장)
2. **Evaluate** 버튼 클릭
3. 각 메트릭별 점수와 세부 피드백 확인
4. 점수가 낮은 항목의 Trace를 분석하여 원인 파악

---

## Synthetic Task Generation — 자동 평가 데이터셋 생성

수동으로 수백 개의 테스트 질문을 작성하는 것은 비현실적입니다. Synthetic Task Generation은 Knowledge Source를 분석하여 자동으로 질문-답변 쌍을 생성합니다.

### 사용 방법

1. Examples 탭에서 **Generate synthetic tasks** 클릭
2. Knowledge Source 기반으로 다양한 질문이 자동 생성됨
3. 생성된 질문을 검토하고 필요에 따라 수정
4. AI Judge로 자동 평가 실행

{% hint style="warning" %}
**주의**: Synthetic Task는 출발점일 뿐입니다. 반드시 도메인 전문가(SME)가 생성된 질문의 품질을 검토하고, 실제 사용자 질문 패턴을 반영하여 보완해야 합니다.
{% endhint %}

### 평가 데이터셋 관리

- 생성된 데이터셋은 **Unity Catalog 테이블** 로 Export하여 버전 관리
- 여러 버전의 에이전트를 동일한 데이터셋으로 비교 평가
- 프로덕션에서 수집된 사용자 질문을 Import하여 데이터셋 보강

---

## 평가 워크플로우

```
1. 에이전트 생성 후 Build 탭에서 수동 테스트 (5~10개 질문)
    ↓
2. AI Playground에서 View Trace로 실행 과정 확인
    ↓
3. Examples 탭에서 라벨링된 질문/가이드라인 추가 (20개 이상)
    ↓
4. Synthetic Task Generation으로 테스트 질문 자동 생성 (50개 이상)
    ↓
5. AI Judge로 전체 평가 실행 → 메트릭 점수 확인
    ↓
6. SME에게 공유 링크 전달 → 전문가 피드백 수집
    ↓
7. 가이드라인/Knowledge Source 조정 → 재테스트 → 반복
    ↓
8. 목표 점수 달성 시 배포 진행
```

---

## 프로덕션 모니터링 포인트

배포 후 지속적으로 모니터링해야 할 항목:

| 카테고리 | 모니터링 항목 | 기준 |
|----------|-------------|------|
| **품질** | AI Judge 점수 추이 | Correctness 80% 이상 유지 |
| **품질** | 인용 정확도 (KA) | 출처가 올바르게 참조되는 비율 |
| **라우팅** | 라우팅 정확도 (Supervisor) | 올바른 서브 에이전트로 위임되는 비율 |
| **사용자** | 좋아요/싫어요 비율 | 부정 피드백 20% 초과 시 즉시 개선 |
| **성능** | 응답 지연 (Latency) | P95 기준 10초 이내 |
| **안정성** | 오류율 | 실패한 쿼리 비율 5% 미만 |
| **비용** | 토큰 사용량 | 일별 DBU 소비량 추적 |

{% hint style="info" %}
**알림 설정**: Databricks SQL Alert 또는 외부 모니터링 도구(Datadog, PagerDuty 등)와 연동하여 임계값 초과 시 자동 알림을 받도록 설정하세요.
{% endhint %}

---

## 배포 절차: Review App → Model Serving → REST API

### Step 1: Review App으로 SME 검증

1. 에이전트 설정 페이지에서 **Share** 클릭
2. 공유 링크를 도메인 전문가에게 전달
3. SME가 직접 질문하고 피드백 제출
4. 피드백을 반영하여 에이전트 개선

### Step 2: Model Serving 엔드포인트 배포

1. 에이전트 페이지에서 **Deploy** 클릭
2. 엔드포인트 이름, 컴퓨트 사이즈 설정
3. 배포 완료 후 엔드포인트 상태가 `Ready`인지 확인

### Step 3: REST API로 연동

**REST API (curl) 예시:**

```bash
curl -X POST \
  https://<workspace-url>/serving-endpoints/<endpoint-name>/invocations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "이번 달 매출 현황 알려줘"}
    ]
  }'
```

**Python SDK 예시:**

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="<endpoint-name>",
    messages=[
        {"role": "user", "content": "이번 달 매출 현황 알려줘"}
    ]
)

print(response.choices[0].message.content)
```

---

## 배포 아키텍처

```
┌─────────────────────────────────────────────────┐
│                 Model Serving                     │
│  ┌───────────────────────────────────────────┐   │
│  │         Supervisor Agent Endpoint          │   │
│  │                                           │   │
│  │  ┌─────────────┐  ┌─────────────────────┐│   │
│  │  │ KA Endpoint  │  │ Genie Space (API)   ││   │
│  │  └──────┬──────┘  └──────────┬──────────┘│   │
│  │         │                     │           │   │
│  │  ┌──────┴──────┐  ┌──────────┴──────────┐│   │
│  │  │Vector Search│  │  SQL Warehouse      ││   │
│  │  │   Index     │  │  (UC Tables)        ││   │
│  │  └─────────────┘  └─────────────────────┘│   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │ UC Functions│  │ MCP Servers│  │  MLflow    │ │
│  └────────────┘  └────────────┘  │  Monitoring │ │
│                                   └────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 워크스페이스 간 마이그레이션

Knowledge Assistant를 다른 워크스페이스로 복제해야 할 경우:

1. 타겟 워크스페이스에 필요한 리소스를 먼저 생성 (Vector Search Index, Volume 등)
2. 소스 워크스페이스에서 SDK로 설정 정보 조회
3. 타겟 워크스페이스에서 `create_knowledge_source` API로 재생성
4. Instructions, Examples 데이터도 Export/Import하여 이전
5. 타겟 워크스페이스에서 AI Judge로 동일한 품질 수준인지 검증

---

## 평가가 Agent Bricks에서 특히 중요한 이유

일반적인 소프트웨어에서는 유닛 테스트와 통합 테스트로 품질을 보장합니다. 하지만 AI 에이전트는 **비결정적(non-deterministic)** 시스템이므로, 동일한 입력에도 다른 출력이 나올 수 있습니다. 이 특성이 Agent Bricks에서 평가를 특히 중요하게 만드는 이유입니다.

### AI 에이전트 평가의 고유한 어려움

| 어려움 | 설명 | Agent Bricks 대응 |
|--------|------|-------------------|
| **비결정적 출력** | 같은 질문에 다른 답변이 생성될 수 있음 | AI Judge가 "의미적 동등성"으로 평가 (단어 일치가 아닌 의미 일치) |
| **주관적 품질** | "좋은 답변"의 기준이 도메인마다 다름 | Guidelines로 도메인별 품질 기준 정의 가능 |
| **다단계 파이프라인** | 검색 실패 vs 생성 실패를 구분해야 함 | Tracing으로 각 단계별 품질을 개별 추적 |
| **멀티 에이전트 복잡성** | 라우팅 오류, 컨텍스트 전달 실패 등 다양한 실패 모드 | Supervisor Trace에서 라우팅 판단 과정 확인 |
| **시간 경과에 따른 변화** | 데이터 업데이트, 모델 변경으로 품질이 변동 | 자동 최적화 + 정기 평가 루프 |

### 평가하지 않으면 발생하는 문제

```
에이전트 배포 → 사용자 불만 접수 → 원인 파악 불가 → 긴급 패치 →
다른 질문 품질 저하 → 사용자 신뢰 상실 → 프로젝트 폐기

vs.

에이전트 구축 → 평가 데이터셋 준비 → AI Judge 자동 평가 →
목표 미달 항목 개선 → 재평가 통과 → 배포 → 정기 모니터링 →
지속적 품질 유지
```

{% hint style="danger" %}
**평가 없이 배포하는 것은 테스트 없이 코드를 프로덕션에 배포하는 것과 같습니다.** Agent Bricks의 AI Judge는 이 과정을 자동화해주므로, 반드시 활용하세요. 최소 50개 이상의 테스트 케이스로 평가한 후 배포하는 것을 권장합니다.
{% endhint %}

---

## 평가 데이터셋 설계 전략

평가의 품질은 **평가 데이터셋의 품질** 에 의해 결정됩니다. 좋은 평가 데이터셋을 설계하는 전략을 상세히 알아봅니다.

### 데이터셋 구성 원칙

| 원칙 | 설명 | 예시 |
|------|------|------|
| **대표성** | 실제 사용자 질문 패턴을 반영 | 단순 조회, 비교 질문, 복합 질문을 균등 배분 |
| **다양성** | 다양한 주제, 난이도, 형식을 포함 | 쉬운 FAQ + 어려운 분석 질문 + 에지 케이스 |
| **균형** | 긍정/부정 케이스를 모두 포함 | 답변 가능한 질문 + "문서에 없는" 질문 |
| **현실성** | 인위적이지 않은 자연스러운 질문 | 오타, 약어, 구어체 포함 |
| **추적 가능성** | 각 테스트 케이스의 출처와 의도 기록 | 태그: "FAQ", "에지케이스", "다국어" 등 |

### 질문 카테고리별 비율 권장사항

| 카테고리 | 비율 | 설명 | 예시 질문 |
|----------|------|------|-----------|
| **직접 조회** | 30% | 문서/데이터에 명확한 답이 있는 질문 | "연차 일수는 몇 일인가요?" |
| **추론 필요** | 20% | 여러 정보를 종합해야 하는 질문 | "3년차 직원의 연차 + 특별 휴가 합계는?" |
| **비교/분석** | 15% | 두 가지 이상을 비교하는 질문 | "A 정책과 B 정책의 차이점은?" |
| **범위 외 질문** | 15% | 에이전트가 답변할 수 없어야 하는 질문 | "내일 날씨는?" (HR봇에 대한 질문) |
| **모호한 질문** | 10% | 의도가 불명확한 질문 | "그거 알려줘" |
| **에지 케이스** | 10% | 극단적이거나 예외적인 질문 | 매우 긴 질문, 특수문자 포함, 다국어 혼합 |

### Synthetic Task Generation 활용 전략

Synthetic Task Generation은 Knowledge Source를 분석하여 질문을 자동 생성합니다. 그러나 이것만으로는 충분하지 않습니다.

**효과적인 활용 방법:**

```
1단계: Synthetic Task Generation으로 50~100개 초기 질문 생성
    ↓
2단계: SME가 생성된 질문을 검토
    - 부자연스러운 질문 삭제 (약 20~30%)
    - 실제 사용자 질문 패턴에 맞게 수정
    ↓
3단계: SME가 누락된 카테고리의 질문 수동 추가
    - 범위 외 질문 (Synthetic에서 잘 생성되지 않음)
    - 모호한 질문
    - 에지 케이스
    ↓
4단계: 각 질문에 Guidelines 추가
    - "응답에 정책명이 포함되어야 합니다"
    - "수치 데이터가 정확해야 합니다"
    - "인용 출처가 올바르게 매핑되어야 합니다"
    ↓
5단계: UC 테이블로 Export하여 버전 관리
    - 에이전트 업데이트 시 동일 데이터셋으로 회귀 테스트
```

### Guidelines 작성 가이드

Guidelines는 AI Judge가 응답을 평가할 때 사용하는 **도메인 특화 기준** 입니다. 잘 작성된 Guidelines는 평가의 정확도를 크게 높입니다.

| Guidelines 유형 | 설명 | 예시 |
|----------------|------|------|
| **내용 기준** | 응답에 포함되어야 할 정보 | "연차 일수와 사용 기한이 모두 포함되어야 합니다" |
| **형식 기준** | 응답의 형식 요구사항 | "표 형태로 정리되어야 합니다" |
| **인용 기준** | 출처 인용 요구사항 | "정책명과 조항 번호가 인용되어야 합니다" |
| **부정 기준** | 포함되면 안 되는 내용 | "개인적인 의견이나 추측이 포함되면 안 됩니다" |
| **거부 기준** | 답변을 거부해야 하는 조건 | "문서에 없는 내용이면 '확인 불가'로 답해야 합니다" |

---

## MLflow Evaluate 통합 패턴

Agent Bricks의 내장 평가 기능 외에, **MLflow Evaluate API** 를 직접 사용하면 더 세밀하고 자동화된 평가 파이프라인을 구축할 수 있습니다.

### Agent Bricks UI vs MLflow Evaluate API

| 기능 | Agent Bricks UI | MLflow Evaluate API |
|------|----------------|-------------------|
| **평가 실행** | Examples 탭에서 Evaluate 클릭 | Python 코드로 실행 |
| **데이터셋 관리** | UI에서 수동 관리 | UC 테이블로 프로그래밍 관리 |
| **커스텀 메트릭** | 기본 5가지 메트릭 | 사용자 정의 메트릭 추가 가능 |
| **자동화** | 수동 실행 | CI/CD 파이프라인 연동 가능 |
| **비교 평가** | 제한적 | 여러 버전의 에이전트를 동시 비교 |
| **이력 관리** | 기본 이력 | MLflow Experiment로 전체 이력 추적 |

### MLflow Evaluate를 활용한 자동 평가 파이프라인

```python
import mlflow
from databricks.sdk import WorkspaceClient

# 에이전트 엔드포인트 설정
w = WorkspaceClient()
endpoint_name = "customer-support-supervisor"

# 평가 데이터셋 로드 (UC 테이블에서)
eval_df = spark.table("ml.evaluation.agent_eval_dataset").toPandas()

# 에이전트 응답 수집 함수
def get_agent_response(question):
    response = w.serving_endpoints.query(
        name=endpoint_name,
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content

# 응답 수집
eval_df["predictions"] = eval_df["request"].apply(get_agent_response)

# MLflow Evaluate 실행
with mlflow.start_run(run_name="agent-eval-v2.1"):
    results = mlflow.evaluate(
        data=eval_df,
        predictions="predictions",
        targets="expected_response",
        model_type="question-answering",
        extra_metrics=[
            mlflow.metrics.genai.relevance(),
            mlflow.metrics.genai.faithfulness(),
        ],
        evaluator_config={
            "col_mapping": {
                "inputs": "request",
                "context": "retrieved_context",
            }
        },
    )

    # 결과 확인
    print(f"Relevance: {results.metrics['relevance/mean']:.2f}")
    print(f"Faithfulness: {results.metrics['faithfulness/mean']:.2f}")
```

### CI/CD 연동 패턴

에이전트 설정 변경(Instructions, Knowledge Source 등) 시 자동으로 평가를 실행하는 파이프라인입니다.

```
에이전트 설정 변경 (Instructions 수정, Knowledge Source 업데이트)
    ↓
자동 트리거: MLflow Evaluate 실행 (50개 이상 테스트 케이스)
    ↓
┌─ 모든 메트릭이 임계값 이상 → 자동 배포 (또는 승인 요청)
└─ 하나라도 임계값 미만 → 알림 + 배포 차단
    ↓
    임계값 예시:
    - Correctness ≥ 0.80
    - Groundedness ≥ 0.85
    - Relevance ≥ 0.80
    - Safety = 1.00 (안전성은 100% 필수)
```

{% hint style="info" %}
**임계값 설정 팁**: 처음에는 낮은 임계값(예: Correctness 0.70)으로 시작하고, 에이전트 품질이 개선됨에 따라 점진적으로 높이세요. 처음부터 높은 임계값을 설정하면 배포가 계속 차단되어 팀의 개발 속도가 저하됩니다.
{% endhint %}

---

## 에이전트 유형별 평가 전략

각 에이전트 유형에 따라 중점적으로 평가해야 할 메트릭과 전략이 다릅니다.

### Knowledge Assistant 평가 전략

| 메트릭 | 중요도 | 평가 포인트 |
|--------|--------|------------|
| **Groundedness** | 최우선 | 환각 방지가 KA의 핵심 가치 — 문서에 없는 내용을 만들어내지 않는지 |
| **Correctness** | 높음 | 기대 답변과 실제 답변의 의미적 일치도 |
| **Chunk Relevance** | 높음 | 검색된 청크가 질문과 관련 있는지 — RAG 파이프라인 품질 지표 |
| **Relevance** | 중간 | 질문에 대한 답변의 관련성 |
| **Safety** | 필수 | 유해 콘텐츠 생성 여부 |

**KA 특화 평가 시나리오:**

- 문서에 있는 내용에 대한 직접 질문 → Correctness + Groundedness
- 문서에 없는 내용에 대한 질문 → 거부 응답 생성 여부
- 여러 문서에 걸친 종합 질문 → 올바른 소스 인용 여부
- 최신 문서 vs 구버전 문서 → 최신 정보 우선 검색 여부

### Genie Space 평가 전략

| 메트릭 | 중요도 | 평가 포인트 |
|--------|--------|------------|
| **SQL 정확도** | 최우선 | 생성된 SQL이 의도한 결과를 반환하는지 |
| **결과 정확도** | 높음 | SQL 실행 결과가 기대값과 일치하는지 |
| **응답 시간** | 중간 | SQL 실행 + 응답 생성까지의 총 소요 시간 |
| **에러율** | 필수 | SQL 문법 오류, 실행 실패 비율 |

### Supervisor Agent 평가 전략

| 메트릭 | 중요도 | 평가 포인트 |
|--------|--------|------------|
| **라우팅 정확도** | 최우선 | 올바른 서브 에이전트로 위임되는지 |
| **종합 응답 품질** | 높음 | 여러 서브 에이전트 응답을 잘 종합하는지 |
| **에러 처리** | 중간 | 서브 에이전트 실패 시 적절하게 대응하는지 |
| **권한 준수** | 필수 | 권한 없는 에이전트에 접근하지 않는지 |

---

## 평가 결과 분석 및 개선 루프

평가 결과를 분석하고 에이전트를 개선하는 체계적인 프로세스입니다.

### 점수가 낮은 항목 분석 흐름

```
AI Judge 평가 결과 확인
    ↓
[점수가 낮은 질문 식별]
    ↓
┌─ Groundedness 낮음
│   └→ Trace에서 Retrieval 확인 → 관련 없는 청크가 검색되었는지?
│       ├── 검색 문제 → Content Description 수정, 문서 재구조화
│       └── 생성 문제 → Instructions에 "문서에 없으면 모른다고 답하라" 추가
│
├─ Correctness 낮음
│   └→ 기대 답변과 실제 답변 비교 → 어디서 차이가 발생하는지?
│       ├── 검색은 올바른데 답변이 부정확 → Instructions 수정, Examples 추가
│       └── 검색 자체가 잘못됨 → Knowledge Source 보강, 동의어 추가
│
├─ Relevance 낮음
│   └→ 답변이 질문과 무관한 내용을 포함하는지?
│       └── Instructions에 "질문에 직접 관련된 내용만 답변하라" 추가
│
└─ Chunk Relevance 낮음
    └→ 검색된 청크가 질문과 관련 없는지?
        ├── 문서 구조 문제 → 헤딩/섹션 구조 개선
        ├── 동의어 문제 → Content Description에 동의어 추가
        └── 검색 설정 문제 → Top-K 조정, 유사도 임계값 조정
```

### 평가 이력 관리와 트렌드 분석

정기적인 평가를 통해 에이전트 품질의 트렌드를 추적합니다.

| 주기 | 활동 | 목적 |
|------|------|------|
| **매주** | AI Judge 자동 평가 실행 (기존 데이터셋) | 회귀(Regression) 감지 |
| **격주** | 프로덕션 로그에서 실패 질문 수집 → 데이터셋 보강 | 데이터셋 현실성 유지 |
| **매월** | SME 리뷰 + 데이터셋 대규모 업데이트 | 도메인 변화 반영 |
| **분기** | 전체 평가 보고서 작성 + 목표 재설정 | 장기 품질 트렌드 관리 |
