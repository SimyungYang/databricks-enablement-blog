# AI 관측성 & 평가 도구

## 왜 GenAI에서 관측성이 특히 중요한가

LLM 기반 애플리케이션은 전통적인 소프트웨어와 **근본적으로 다른 품질 보장 문제** 를 안고 있습니다. 이 차이를 이해하지 못하면 "왜 관측성에 투자해야 하는가"라는 질문에 답할 수 없습니다.

전통적 소프트웨어는 **결정론적(deterministic)** 입니다. 같은 입력에 같은 출력이 나오고, 버그가 발생하면 스택 트레이스로 원인을 찾고, 단위 테스트로 수정을 검증합니다. 그러나 LLM 앱은 **비결정론적(non-deterministic)** 입니다. 같은 프롬프트에 다른 답변이 나오고, 환각(hallucination)이 간헐적으로 발생하며, 프롬프트의 미묘한 변경이 출력 품질을 크게 바꿀 수 있습니다.

**이것이 의미하는 것은, 전통적 소프트웨어의 품질 보장 방법론(단위 테스트, 통합 테스트, 코드 리뷰)만으로는 LLM 앱의 품질을 보장할 수 없다는 것입니다.** 구체적으로:

- **테스트의 한계**: "정답"이 하나가 아니므로 assert 문으로 검증할 수 없음. "좋은 답변"의 기준 자체가 주관적이고 다차원적 (정확성, 완전성, 관련성, 톤, 안전성)
- **재현 불가능한 버그**: temperature > 0이면 같은 프롬프트에 다른 출력이 나옴. "어제 잘 되던 것이 오늘 안 된다"는 보고가 빈번하지만, 정확한 재현이 불가능
- **숨겨진 비용 폭주**: LLM 호출 체인이 복잡해지면 예상치 못한 토큰 소비가 발생. RAG 검색 → Re-ranking → LLM 생성의 각 단계에서 비용이 누적
- **품질 드리프트**: 모델 제공업체의 업데이트(모델 버전 변경, 가격 변동)로 인해 동일 코드에서 출력 품질이 변화

이 문제를 해결하려면 세 가지가 필요합니다.

1. **트레이싱(Tracing)**: LLM 호출, RAG 검색, 도구 사용 등 각 단계의 입출력을 기록하여 "어디서 문제가 발생했는가"를 진단
2. **평가(Evaluation)**: 출력 품질을 체계적으로 측정 (정확도, 관련성, 안전성 등). 사람의 주관적 판단을 스케일러블하게 자동화
3. **모니터링(Monitoring)**: 프로덕션에서의 성능, 비용, 품질을 실시간 추적하여 이상 징후를 조기 감지

이 세 기능을 통합 제공하는 것이 **AI 관측성(AI Observability)** 도구입니다.

---

## 핵심 개념

### 트레이싱 (Tracing)

트레이싱은 LLM 앱의 각 실행 단계를 **스팬(Span)** 이라는 단위로 기록합니다. 하나의 사용자 요청에 대해 여러 스팬이 트리 구조로 연결됩니다.

예를 들어, RAG 기반 챗봇의 트레이스는 다음과 같은 구조입니다.

```
[사용자 요청] (루트 스팬)
├── [쿼리 재작성] - 입력: "DB 비교" → 출력: "Databricks vs Snowflake 아키텍처 비교"
├── [벡터 검색] - 쿼리: "Databricks vs Snowflake..." → 결과: 5개 문서 청크
├── [Re-ranking] - 입력: 5개 청크 → 출력: 상위 3개 청크
└── [LLM 생성] - 프롬프트: 시스템 + 컨텍스트 + 질문 → 응답: "..."
    ├── 모델: claude-4-sonnet
    ├── 토큰: 입력 2,450 / 출력 680
    ├── 지연시간: 1.8초
    └── 비용: $0.012
```

이 트레이스를 통해 **어디서 문제가 발생했는지** 를 정확히 파악할 수 있습니다. 답변 품질이 낮다면 검색 결과가 부적절한 것인지, LLM의 생성이 부정확한 것인지, 프롬프트가 문제인지를 구분할 수 있습니다.

### 평가 (Evaluation)

LLM 출력의 품질을 측정하는 방법은 크게 세 가지입니다.

1. **코드 기반 평가**: BLEU, ROUGE 등 자동 메트릭. 빠르지만 깊이가 부족
2. **LLM-as-Judge**: 다른 LLM이 출력을 평가. 비용 효율적이고 스케일러블
3. **Human Evaluation**: 사람이 직접 평가. 가장 정확하지만 비용이 높고 느림

실무에서는 **LLM-as-Judge** 가 가장 많이 사용됩니다. 예를 들어, GPT-4가 Claude의 출력을 "정확성 1~5점"으로 평가하는 방식입니다.

### 모니터링 (Monitoring)

프로덕션 환경에서의 실시간 추적 지표입니다.

- **지연시간 (Latency)**: 요청~응답 시간. P50/P95/P99 분포
- **비용 (Cost)**: 토큰 사용량 기반 비용 추적
- **에러율**: 실패한 요청 비율, 타임아웃 비율
- **품질 드리프트**: 시간이 지남에 따라 출력 품질이 변하는지 감지

---

## 주요 도구 비교

아래 테이블은 2025년 기준 주요 AI 관측성 & 평가 도구를 비교합니다.

| 도구 | 개발사 | 유형 | 핵심 특징 | 가격 | 오픈소스 |
|------|--------|------|----------|------|---------|
| **MLflow Tracing** | Databricks (LF) | 트레이싱/평가 | OpenTelemetry 기반, UC 통합, 30+ 프레임워크 자동 계측 | 무료 (오픈소스) | O |
| **LangSmith** | LangChain | 트레이싱/평가/모니터링 | LangChain 네이티브, 데이터셋 관리, 회귀 테스트 | 무료 / $39~(Plus) | X |
| **Weights & Biases** | W&B | 실험 추적/Weave | ML 실험 추적의 사실상 표준, Weave(LLM 관측성) | 무료(개인) / 유료(팀) | X (Weave는 O) |
| **Braintrust** | Braintrust | 평가 특화 | LLM 평가 전문, 프롬프트 관리, A/B 테스트 | 무료(시작) / 유료 | X |
| **Phoenix** | Arize AI | 트레이싱/평가 | 오픈소스, OpenTelemetry 기반, 실시간 트레이싱 | 무료 (오픈소스) | O |
| **Langfuse** | Langfuse | 트레이싱/분석 | 오픈소스, 셀프호스팅, 프롬프트 관리 | 무료(셀프호스팅) / 유료(클라우드) | O |

이 비교에서 핵심적인 선택 기준은 **기존 스택과의 통합** 입니다. Databricks 환경이라면 MLflow Tracing이 자연스럽고, LangChain을 주로 사용한다면 LangSmith가 편리하며, ML 실험 추적도 함께 필요하다면 W&B가 통합적입니다.

---

## 주요 도구 상세

### MLflow Tracing (Databricks)

MLflow는 ML 라이프사이클 관리의 **오픈소스 표준** 으로, 2024년부터 LLM 관측성 기능(Tracing)을 대폭 강화했습니다. Databricks가 핵심 기여자이며, Unity Catalog와 긴밀히 통합됩니다.

**동작 원리:**

MLflow Tracing은 **OpenTelemetry(OTel)** 기반으로 구현되어 있습니다. OpenTelemetry는 CNCF(Cloud Native Computing Foundation)가 관리하는 분산 시스템 관측성의 **오픈 표준** 으로, Kubernetes, Prometheus, Envoy와 같은 레벨의 업계 표준입니다. MLflow가 OTel을 채택한 것은 전략적으로 중요합니다: OTel 호환 모든 백엔드(Jaeger, Zipkin, Datadog, New Relic 등)로 트레이스 데이터를 내보낼 수 있어 **벤더 락인이 없습니다**.

**자동 계측(Auto-instrumentation)** 은 MLflow Tracing의 핵심 편의 기능입니다. `mlflow.openai.autolog()` 한 줄만 추가하면, OpenAI SDK의 모든 호출이 자동으로 트레이스됩니다. 내부적으로는 Python의 monkey-patching으로 SDK의 핵심 메서드를 래핑(wrapping)하여, 원본 코드를 전혀 수정하지 않고 입출력, 토큰 수, 지연시간 등을 캡처합니다.

```python
import mlflow

# 자동 계측: 한 줄로 모든 LLM 호출 트레이싱
mlflow.openai.autolog()      # OpenAI SDK 호출 자동 추적
mlflow.langchain.autolog()   # LangChain 체인 실행 자동 추적

# 수동 계측: 세밀한 제어가 필요한 경우
@mlflow.trace
def rag_pipeline(question: str) -> str:
    with mlflow.start_span(name="retrieval") as span:
        docs = vector_search(question)
        span.set_inputs({"question": question})
        span.set_outputs({"num_docs": len(docs)})

    with mlflow.start_span(name="generation") as span:
        response = llm.invoke(question, context=docs)
        span.set_outputs({"response": response})

    return response
```

**핵심 강점:**
- **30+ 프레임워크 자동 계측**: OpenAI, Anthropic, LangChain, LlamaIndex 등
- **Unity Catalog 통합**: 트레이스 데이터가 UC에 저장되어 거버넌스/접근 제어 적용
- **Inference Table**: Model Serving의 모든 요청/응답을 자동 로깅
- **평가 API**: `mlflow.evaluate()`로 다양한 메트릭 자동 계산
- **오픈소스**: 벤더 락인 없음, 어디서든 실행 가능

**한계:**
- LangSmith 대비 UI/UX가 아직 발전 중
- 실시간 모니터링 대시보드가 제한적 (Lakehouse Monitoring으로 보완)

### LangSmith (LangChain)

LangChain 생태계의 **공식 관측성 도구** 입니다. LangChain으로 구축한 앱의 트레이싱, 평가, 모니터링을 통합 제공합니다. LangChain이 "LLM 앱 구축의 표준 프레임워크" 지위를 유지하는 데 LangSmith의 역할이 큽니다.

**핵심 강점:**
- **LangChain 네이티브**: `LANGCHAIN_TRACING_V2=true` 환경 변수 하나로 모든 LangChain 체인 실행이 자동 트레이싱. 코드 변경 불필요
- **Hub 기반 프롬프트 버저닝**: LangChain Hub에 프롬프트를 저장/관리하고, **시맨틱 버저닝** 을 적용합니다. `hub.pull("rag-prompt:v2.1")`처럼 코드에서 특정 버전의 프롬프트를 참조하므로, 프롬프트 변경의 영향을 추적하고 롤백할 수 있습니다.
- **데이터셋 관리**: 평가용 골든 데이터셋 생성/관리. 프로덕션 트레이스에서 "좋은 예시"를 선별하여 데이터셋에 추가하는 워크플로 지원
- **Online Evaluation 파이프라인**: 프로덕션 트래픽에 **LLM-as-Judge를 자동 적용** 합니다. 예를 들어, 모든 RAG 응답에 대해 "답변이 검색된 문서와 일치하는가(faithfulness)"를 GPT-4가 자동 평가하고, 점수가 기준 이하이면 알림을 발생시킵니다. 이것이 비결정론적 LLM 앱의 품질을 프로덕션에서 보장하는 핵심 메커니즘입니다.
- **회귀 테스트**: 프롬프트 변경 시 동일 데이터셋에 대해 이전 버전과 새 버전을 자동 비교

**한계:**
- LangChain 외 프레임워크(LlamaIndex, DSPy 등) 지원이 상대적으로 부족. 최근 개선 중이나 네이티브 통합 깊이는 차이
- 클라우드 전용 (셀프호스팅 불가, 2025년 기준). 데이터 주권이 중요한 조직에서는 MLflow나 Langfuse가 대안
- 유료 플랜 비용이 트레이스 볼륨에 비례하여 급증. 높은 트래픽 서비스에서 월 수백~수천 달러 발생 가능

### Weights & Biases (W&B) + Weave

W&B는 ML 실험 추적(Experiment Tracking)의 **사실상 표준** 입니다. 2024년부터 **Weave** 라는 LLM 관측성 도구를 추가하여 GenAI 영역으로 확장했습니다.

**W&B 핵심 기능:**
- **실험 추적**: 하이퍼파라미터, 메트릭, 모델 아티팩트 자동 로깅
- **시각화**: 실험 간 비교, 하이퍼파라미터 스윕, 메트릭 대시보드
- **모델 레지스트리**: 모델 버전 관리, 아티팩트 추적
- **Reports**: 실험 결과를 공유 가능한 리포트로 작성

**Weave (LLM 관측성):**
- LLM 호출 트레이싱 (OpenAI, Anthropic 등)
- 평가 파이프라인 구축
- 프롬프트 버전 관리
- 오픈소스로 공개

**한계:**
- LLM 관측성(Weave)은 MLflow/LangSmith 대비 후발주자
- 기존 W&B 사용자가 아니면 진입 장벽이 있을 수 있음

### Braintrust

**LLM 평가에 특화** 된 도구입니다. 트레이싱보다는 **"AI 출력 품질을 어떻게 체계적으로 측정하고 개선할 것인가"** 에 집중합니다.

**핵심 강점:**
- **평가 프레임워크**: 다양한 평가 메트릭(정확도, 관련성, 충실도 등) 내장
- **프롬프트 관리**: 프롬프트 버전 관리 + A/B 테스트
- **데이터셋 관리**: 골든 데이터셋 생성, Human-in-the-loop 어노테이션
- **CI/CD 통합**: PR마다 자동으로 LLM 평가 실행

### Phoenix (Arize AI)

Arize AI가 개발한 **오픈소스 LLM 관측성 도구** 입니다. OpenTelemetry 기반으로 MLflow와 유사한 접근 방식을 취합니다.

**핵심 강점:**
- **완전 오픈소스**: 셀프호스팅 가능, 벤더 락인 없음
- **OpenTelemetry 네이티브**: 표준 기반 트레이싱으로 이식성 높음
- **임베딩 시각화**: 벡터 임베딩을 시각적으로 분석하여 RAG 품질 진단
- **다양한 프레임워크 지원**: OpenAI, LangChain, LlamaIndex, DSPy 등

---

## Databricks 관측성 통합 아키텍처

Databricks는 **MLflow + Inference Table + Lakehouse Monitoring** 의 3가지 도구를 결합하여 엔드투엔드 AI 관측성을 제공합니다.

아래 테이블은 Databricks의 AI 관측성 스택에서 각 구성 요소의 역할을 보여줍니다.

| 구성 요소 | 역할 | 데이터 소스 |
|----------|------|-----------|
| **MLflow Tracing** | 개발/테스트 단계 트레이싱, 평가 | 개발 환경의 LLM 호출 |
| **Inference Table** | 프로덕션 요청/응답 자동 로깅 | Model Serving 엔드포인트 |
| **Lakehouse Monitoring** | 프로덕션 품질/드리프트 모니터링 | Inference Table의 Delta 테이블 |
| **Unity Catalog** | 거버넌스, 접근 제어, 리니지 | 모든 관측성 데이터 |

이 아키텍처의 핵심 장점은 **모든 관측성 데이터가 Delta 테이블에 저장** 된다는 것입니다. 즉, SQL로 직접 쿼리하여 커스텀 분석을 수행하거나, Databricks SQL 대시보드로 시각화하거나, 다른 데이터 파이프라인에 통합할 수 있습니다. LangSmith나 W&B 같은 외부 도구는 데이터가 해당 서비스에 저장되므로 이런 유연성이 제한적입니다.

### 실전 워크플로 예시

```python
import mlflow

# 1. 개발 단계: MLflow Tracing으로 디버깅
mlflow.langchain.autolog()
chain = build_rag_chain()
result = chain.invoke({"question": "Delta Lake의 Time Travel 사용법은?"})
# → MLflow UI에서 트레이스 확인, 검색 결과 품질 검토

# 2. 평가 단계: mlflow.evaluate()로 품질 측정
eval_data = mlflow.data.load_delta(table_name="evaluation_dataset")
results = mlflow.evaluate(
    model=chain,
    data=eval_data,
    targets="expected_answer",
    model_type="question-answering",
    evaluators="default"
)
# → 정확도, 관련성, 충실도 등 자동 계산

# 3. 프로덕션 배포: Model Serving + Inference Table
# → 모든 요청/응답이 자동으로 Delta 테이블에 저장

# 4. 모니터링: Lakehouse Monitoring
# → 품질 드리프트, 지연시간 이상, 비용 급증 알림
```

{% hint style="info" %}
Databricks의 관측성 스택은 **오픈소스(MLflow) + 네이티브 통합(Inference Table, Lakehouse Monitoring)** 의 조합입니다. 외부 관측성 도구(LangSmith, W&B)와 병행 사용도 가능하지만, 데이터 통합과 거버넌스 관점에서는 Databricks 네이티브 스택이 유리합니다.
{% endhint %}

---

## 관측성 도구 선택 가이드

### Databricks 환경이라면

**MLflow Tracing** 을 기본 관측성 도구로 사용하세요. Unity Catalog 통합, Inference Table 연동, 오픈소스라는 세 가지 장점이 있습니다.

### LangChain 기반 앱을 운영한다면

**LangSmith** 가 가장 자연스러운 선택입니다. 코드 변경 없이 환경 변수 설정만으로 트레이싱이 시작되고, LangChain 생태계의 모든 기능과 깊이 통합됩니다.

### ML 실험 추적과 LLM 관측성을 통합하고 싶다면

**W&B + Weave** 를 사용하세요. 전통적 ML 모델의 실험 추적과 LLM 앱의 관측성을 하나의 플랫폼에서 관리할 수 있습니다.

### 평가에 특화된 도구가 필요하다면

**Braintrust** 를 추천합니다. 프롬프트 A/B 테스트, CI/CD 통합 평가 등 평가 파이프라인 구축에 특화되어 있습니다.

### 오픈소스 + 셀프호스팅이 필수라면

**Phoenix** 또는 **Langfuse** 를 선택하세요. 두 도구 모두 오픈소스로 자체 인프라에 배포할 수 있으며, OpenTelemetry 기반으로 이식성이 높습니다.

{% hint style="warning" %}
관측성 도구 선택보다 중요한 것은 **"관측성을 하는 것 자체"** 입니다. 많은 팀이 LLM 앱을 프로덕션에 배포한 후 관측성 없이 운영하다가, 품질 저하나 비용 급증을 뒤늦게 발견합니다. 어떤 도구든 하나를 선택하여 최소한의 트레이싱과 평가를 시작하는 것이 가장 중요합니다.
{% endhint %}
