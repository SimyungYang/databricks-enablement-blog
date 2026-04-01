# 평가 & 배포

---

## MLflow 기반 평가

Agent Bricks는 MLflow와 긴밀하게 통합되어 에이전트 품질을 체계적으로 평가합니다.

| 기능 | 설명 |
|------|------|
| **Tracing**| 에이전트 실행의 전체 과정을 추적 (Production Monitoring for MLflow 활성화 필요) |
| **AI Judge**| LLM 기반 자동 품질 판정 |
| **Synthetic Task Generation**| 합성 데이터로 대규모 테스트 |
| **라벨링된 데이터셋**| UC 테이블로 Import/Export하여 체계적 관리 |

---

## MLflow Tracing으로 에이전트 동작 추적

Tracing은 에이전트의 각 단계(검색, LLM 호출, 도구 실행 등)를 시각적으로 추적합니다.

### 활성화 방법

1. 워크스페이스에서 **Production Monitoring for MLflow**활성화
2. 에이전트 Build 탭에서 질문 입력 후 **View Trace**클릭

### Trace에서 확인할 수 있는 정보

| 항목 | 설명 |
|------|------|
| **Retrieval**| 어떤 문서/청크가 검색되었는지, 유사도 점수 |
| **LLM Call**| 어떤 프롬프트가 전송되었는지, 토큰 사용량 |
| **Tool Execution**| UC Function, MCP 서버 호출 결과 |
| **Routing Decision**| Supervisor가 어떤 서브 에이전트를 선택했는지, 그 이유 |
| **Latency**| 각 단계별 소요 시간 |

{% hint style="info" %}
**디버깅 팁**: 에이전트가 엉뚱한 답변을 하면, Trace에서 Retrieval 단계를 먼저 확인하세요. 관련 없는 문서가 검색되고 있다면 Knowledge Source의 Content Description을 조정해야 합니다.
{% endhint %}

---

## AI Judge (LLM-as-Judge) 설정

AI Judge는 LLM을 평가자로 사용하여 에이전트 응답의 품질을 자동으로 판정합니다.

### 평가 메트릭

| 메트릭 | 설명 | 측정 대상 |
|--------|------|-----------|
| **Correctness**| 응답이 기대 답변과 일치하는지 | 라벨링된 기대 답변 대비 정확도 |
| **Groundedness**| 응답이 검색된 문서에 근거하는지 | 환각(hallucination) 방지 |
| **Relevance**| 질문에 대한 응답의 관련성 | 주제 이탈 방지 |
| **Safety**| 유해하거나 부적절한 내용이 없는지 | 안전성 검증 |
| **Chunk Relevance**| 검색된 청크가 질문과 관련 있는지 | RAG 검색 품질 |

### 설정 방법

1. **Examples 탭**에서 라벨링된 질문-답변 쌍 추가 (최소 20개 권장)
2. **Evaluate**버튼 클릭
3. 각 메트릭별 점수와 세부 피드백 확인
4. 점수가 낮은 항목의 Trace를 분석하여 원인 파악

---

## Synthetic Task Generation — 자동 평가 데이터셋 생성

수동으로 수백 개의 테스트 질문을 작성하는 것은 비현실적입니다. Synthetic Task Generation은 Knowledge Source를 분석하여 자동으로 질문-답변 쌍을 생성합니다.

### 사용 방법

1. Examples 탭에서 **Generate synthetic tasks**클릭
2. Knowledge Source 기반으로 다양한 질문이 자동 생성됨
3. 생성된 질문을 검토하고 필요에 따라 수정
4. AI Judge로 자동 평가 실행

{% hint style="warning" %}
**주의**: Synthetic Task는 출발점일 뿐입니다. 반드시 도메인 전문가(SME)가 생성된 질문의 품질을 검토하고, 실제 사용자 질문 패턴을 반영하여 보완해야 합니다.
{% endhint %}

### 평가 데이터셋 관리

- 생성된 데이터셋은 **Unity Catalog 테이블**로 Export하여 버전 관리
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
| **품질**| AI Judge 점수 추이 | Correctness 80% 이상 유지 |
| **품질**| 인용 정확도 (KA) | 출처가 올바르게 참조되는 비율 |
| **라우팅**| 라우팅 정확도 (Supervisor) | 올바른 서브 에이전트로 위임되는 비율 |
| **사용자**| 좋아요/싫어요 비율 | 부정 피드백 20% 초과 시 즉시 개선 |
| **성능**| 응답 지연 (Latency) | P95 기준 10초 이내 |
| **안정성**| 오류율 | 실패한 쿼리 비율 5% 미만 |
| **비용**| 토큰 사용량 | 일별 DBU 소비량 추적 |

{% hint style="info" %}
**알림 설정**: Databricks SQL Alert 또는 외부 모니터링 도구(Datadog, PagerDuty 등)와 연동하여 임계값 초과 시 자동 알림을 받도록 설정하세요.
{% endhint %}

---

## 배포 절차: Review App → Model Serving → REST API

### Step 1: Review App으로 SME 검증

1. 에이전트 설정 페이지에서 **Share**클릭
2. 공유 링크를 도메인 전문가에게 전달
3. SME가 직접 질문하고 피드백 제출
4. 피드백을 반영하여 에이전트 개선

### Step 2: Model Serving 엔드포인트 배포

1. 에이전트 페이지에서 **Deploy**클릭
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
