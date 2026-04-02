# RAG 배포

평가를 통과한 RAG 체인을 프로덕션 환경에 배포하고, 지속적으로 모니터링하는 방법을 다룹니다.

## Model Serving으로 배포하는 방법과 이유

### 왜 Model Serving인가?

RAG 체인을 프로덕션에서 서비스하려면 **안정적이고 확장 가능한 인프라** 가 필요합니다. Databricks Model Serving은 이를 위해 설계된 서버리스 플랫폼입니다.

| 직접 구축 (Flask/FastAPI) | Databricks Model Serving |
|--------------------------|-------------------------|
| 서버 프로비저닝, 스케일링 직접 관리 | 서버리스 자동 스케일링 |
| 로드 밸런싱 직접 구성 | 내장 로드 밸런싱 |
| 인증/권한 관리 직접 구현 | Unity Catalog 기반 권한 관리 |
| 모니터링 시스템 직접 구축 | MLflow Tracing + 인퍼런스 테이블 내장 |
| 모델 버전 관리 직접 구현 | UC 기반 모델 레지스트리 + A/B 테스트 |
| 콜드 스타트 최적화 직접 | Scale-to-zero 자동 지원 |

### 서버리스 스케일링의 작동 방식

Model Serving 엔드포인트는 트래픽에 따라 자동으로 스케일합니다:

- **Scale-to-zero**: 트래픽이 없으면 인스턴스를 0으로 줄여 비용을 절감합니다
- **자동 스케일 아웃**: 트래픽 증가 시 인스턴스를 자동 추가합니다
- **콜드 스타트**: Scale-to-zero에서 첫 요청 시 10~30초 소요됩니다
- **Warm 상태 유지**: `scale_to_zero_enabled=False`로 설정하면 항상 최소 1개 인스턴스가 유지됩니다

```python
# 비용 vs 성능 트레이드오프
# 개발/테스트: scale_to_zero=True (비용 절감 우선)
# 프로덕션: scale_to_zero=False (응답 속도 우선)
```

{% hint style="info" %}
RAG 체인은 LLM 호출, Vector Search 쿼리, 리랭킹 등 여러 외부 서비스를 호출하므로, Model Serving 자체의 콜드 스타트보다 **외부 서비스 호출 지연** 이 전체 응답 시간의 대부분을 차지합니다. Scale-to-zero 사용 시 콜드 스타트는 첫 요청에만 영향을 미칩니다.
{% endhint %}

## 1. Model Serving Endpoint 배포

MLflow에 로깅된 모델을 서버리스 Model Serving Endpoint로 배포합니다.

### SDK를 통한 배포

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import (
    EndpointCoreConfigInput,
    ServedEntityInput,
)

w = WorkspaceClient()

w.serving_endpoints.create_and_wait(
    name="rag-agent-endpoint",
    config=EndpointCoreConfigInput(
        served_entities=[
            ServedEntityInput(
                entity_name="catalog.schema.rag_agent",
                entity_version="1",
                scale_to_zero_enabled=True,
                workload_size="Small",
                workload_type="GPU_SMALL",
            )
        ]
    ),
)
```

{% hint style="info" %}
`scale_to_zero_enabled=True`로 설정하면 트래픽이 없을 때 비용이 발생하지 않습니다. 단, 콜드 스타트 시 첫 요청에 수십 초가 걸릴 수 있습니다.
{% endhint %}

### 엔드포인트 호출 테스트

```python
import mlflow.deployments

deploy_client = mlflow.deployments.get_deploy_client("databricks")

response = deploy_client.predict(
    endpoint="rag-agent-endpoint",
    inputs={
        "messages": [
            {"role": "user", "content": "Vector Search Index 유형을 설명해주세요."}
        ]
    }
)

print(response["choices"][0]["message"]["content"])
```

## 2. Agent Framework 활용

### deploy() 함수로 간편 배포

```python
from databricks import agents

# 모델을 서빙 엔드포인트로 배포 + Review App 자동 생성
deployment = agents.deploy(
    model_name="catalog.schema.rag_agent",
    model_version="1",
)

print(f"엔드포인트: {deployment.endpoint_name}")
print(f"Review App URL: {deployment.review_app_url}")
```

{% hint style="success" %}
`agents.deploy()`는 서빙 엔드포인트 생성, Review App 설정, 피드백 테이블 생성을 한 번에 처리합니다. 가장 간편한 배포 방법입니다.
{% endhint %}

## 3. Review App으로 피드백 수집

Review App은 SME(Subject Matter Expert)가 RAG 답변의 품질을 평가할 수 있는 웹 UI입니다.

SME(Subject Matter Expert)가 답변에 대해 정확/부정확 판정 및 수정된 정답을 제공할 수 있습니다.

```python
from databricks import agents

# 특정 사용자에게 리뷰 권한 부여
agents.set_permissions(
    model_name="catalog.schema.rag_agent",
    users=["reviewer1@company.com", "reviewer2@company.com"],
    permission_level=agents.PermissionLevel.CAN_QUERY,
)

# 피드백 데이터 조회 (Unity Catalog 테이블에 자동 저장)
feedback_df = spark.sql("""
    SELECT request, response, feedback.rating, feedback.comment
    FROM catalog.schema.rag_agent_payload_table
    WHERE feedback IS NOT NULL ORDER BY timestamp DESC
""")
display(feedback_df)
```

## 4. 프로덕션 모니터링

### MLflow Tracing

모든 요청의 검색/생성 과정을 추적하여 병목 지점과 오류를 파악합니다.

```python
import mlflow
mlflow.langchain.autolog()  # LangChain 체인 자동 트레이싱

# 또는 수동 트레이싱
@mlflow.trace
def rag_pipeline(question: str) -> str:
    with mlflow.start_span(name="retrieval") as span:
        docs = retriever.invoke(question)
        span.set_outputs({"num_docs": len(docs)})
    with mlflow.start_span(name="generation") as span:
        answer = rag_chain.invoke(question)
    return answer
```

{% hint style="warning" %}
프로덕션 환경에서 트레이싱은 반드시 활성화하세요. 문제 발생 시 검색 단계에서 오류인지 생성 단계에서 오류인지 빠르게 파악할 수 있습니다.
{% endhint %}

### 모니터링 대시보드 핵심 지표

| 지표 | 설명 | 임계값 예시 |
|------|------|------------|
| **지연 시간 (Latency)** | 요청-응답 전체 시간 | P95 < 5초 |
| **검색 지연** | Vector Search 쿼리 시간 | P95 < 500ms |
| **토큰 사용량** | LLM 입출력 토큰 수 | 비용 기준 설정 |
| **오류율** | 실패한 요청 비율 | < 1% |
| **피드백 점수** | 사용자 만족도 | 긍정 > 80% |

## 5. 프로덕션 모니터링 상세

### 인퍼런스 테이블 활용

Model Serving 엔드포인트에 인퍼런스 테이블을 활성화하면, 모든 요청/응답 데이터가 Delta Table에 자동 저장됩니다. 이를 활용하여 지속적인 품질 모니터링이 가능합니다.

```python
# 인퍼런스 테이블에서 품질 지표 추출
quality_metrics = spark.sql("""
    SELECT
        date_trunc('hour', timestamp) AS hour,
        COUNT(*) AS total_requests,
        AVG(response_latency_ms) AS avg_latency_ms,
        PERCENTILE(response_latency_ms, 0.95) AS p95_latency_ms,
        AVG(total_tokens) AS avg_tokens,
        SUM(CASE WHEN status_code != 200 THEN 1 ELSE 0 END) AS error_count
    FROM catalog.schema.rag_agent_endpoint_inference_table
    WHERE timestamp > current_timestamp() - INTERVAL 24 HOURS
    GROUP BY 1 ORDER BY 1
""")
display(quality_metrics)
```

### 알림 설정

프로덕션 환경에서는 **이상 징후를 조기에 감지** 하는 것이 중요합니다. 다음 지표에 대한 알림을 설정하세요.

| 알림 조건 | 임계값 예시 | 조치 |
|-----------|-----------|------|
| **P95 지연 시간 급증** | > 10초 (평소 3초) | Vector Search 또는 LLM 엔드포인트 상태 확인 |
| **오류율 증가** | > 5% (평소 < 1%) | 로그 확인, 서빙 엔드포인트 재시작 |
| **토큰 사용량 급증** | 평소 대비 200%+ | 프롬프트 또는 검색 결과 수(k) 확인 |
| **피드백 점수 하락** | 긍정 비율 < 70% | 평가 재실행, 취약 쿼리 패턴 분석 |

### 지속적 개선 루프

```
프로덕션 서빙 → 인퍼런스 테이블 수집 → 품질 분석
       ↑                                    │
       │                                    ▼
  재배포 ←── 개선 적용 ←── 취약점 식별 + 평가
```

1. **인퍼런스 테이블에서 낮은 품질 응답 식별**: 짧은 답변, 높은 지연, 사용자 피드백 부정적
2. **해당 쿼리로 오프라인 평가 실행**: MLflow Evaluate로 상세 메트릭 확인
3. **원인에 맞는 개선 적용**: 청킹 전략, 프롬프트, 임베딩 모델, k값 등
4. **새 버전 평가 후 배포**: A/B 테스트로 점진적 전환

{% hint style="tip" %}
프로덕션 RAG 시스템은 **"배포하면 끝"이 아닙니다**. 문서가 추가/변경되고, 사용자 질문 패턴이 변화하므로, 지속적인 모니터링과 개선이 필수입니다.
{% endhint %}

## 6. 프로덕션 운영 체크리스트

- [ ] Model Serving Endpoint 배포 및 호출 테스트 완료
- [ ] Review App 설정 및 리뷰어 권한 부여
- [ ] MLflow Tracing 활성화
- [ ] 인퍼런스 테이블 모니터링 및 알림 규칙 설정
- [ ] Vector Search Index 자동 동기화 확인
- [ ] 평가 데이터셋 구축 완료 (최소 50개 질문-정답 쌍)
- [ ] 기본 메트릭 기준값(Baseline) 기록
- [ ] 에러 알림 채널 설정 (Slack, Email 등)
- [ ] 모델 롤백 절차 문서화

## 7. 모델 버전 관리 및 롤백

### A/B 테스트로 안전한 업데이트

새로운 RAG 체인 버전을 배포할 때, 기존 버전과 A/B 테스트를 수행하여 안전하게 전환할 수 있습니다.

```python
# Model Serving에서 트래픽 분할 설정
w.serving_endpoints.update_config(
    name="rag-agent-endpoint",
    served_entities=[
        ServedEntityInput(
            entity_name="catalog.schema.rag_agent",
            entity_version="1",    # 기존 버전
            scale_to_zero_enabled=False,
            workload_size="Small",
            traffic_percentage=90,  # 90% 트래픽
        ),
        ServedEntityInput(
            entity_name="catalog.schema.rag_agent",
            entity_version="2",    # 새 버전
            scale_to_zero_enabled=False,
            workload_size="Small",
            traffic_percentage=10,  # 10% 트래픽으로 카나리 배포
        ),
    ],
)
```

### 롤백 절차

새 버전에 문제가 발생하면 트래픽을 이전 버전으로 전환합니다:

```python
# 즉시 롤백: 새 버전 트래픽을 0%로 변경
w.serving_endpoints.update_config(
    name="rag-agent-endpoint",
    served_entities=[
        ServedEntityInput(
            entity_name="catalog.schema.rag_agent",
            entity_version="1",    # 이전 안정 버전
            traffic_percentage=100,
            workload_size="Small",
            scale_to_zero_enabled=False,
        ),
    ],
)
```

{% hint style="warning" %}
프로덕션 환경에서는 롤백 절차를 **사전에 문서화하고 테스트** 해야 합니다. 문제 발생 시 빠르게 대응할 수 있도록 롤백 명령을 스크립트로 준비해 두세요.
{% endhint %}

## 참고 문서

- [Agent Framework 공식 문서](https://docs.databricks.com/aws/en/generative-ai/create-log-agent.html)
- [Model Serving 공식 문서](https://docs.databricks.com/aws/en/machine-learning/model-serving/index.html)
- [MLflow Tracing 공식 문서](https://mlflow.org/docs/latest/llms/tracing/index.html)
- [Model Serving A/B 테스트 문서](https://docs.databricks.com/aws/en/machine-learning/model-serving/model-serving-traffic-split.html)
