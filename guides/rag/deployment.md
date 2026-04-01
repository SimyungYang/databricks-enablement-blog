# RAG 배포

평가를 통과한 RAG 체인을 프로덕션 환경에 배포하고, 지속적으로 모니터링하는 방법을 다룹니다.

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
| **지연 시간 (Latency)**| 요청-응답 전체 시간 | P95 < 5초 |
| ** 검색 지연**| Vector Search 쿼리 시간 | P95 < 500ms |
| ** 토큰 사용량**| LLM 입출력 토큰 수 | 비용 기준 설정 |
| ** 오류율**| 실패한 요청 비율 | < 1% |
| ** 피드백 점수**| 사용자 만족도 | 긍정 > 80% |

## 5. 프로덕션 운영 체크리스트

- [ ] Model Serving Endpoint 배포 및 호출 테스트 완료
- [ ] Review App 설정 및 리뷰어 권한 부여
- [ ] MLflow Tracing 활성화
- [ ] 인퍼런스 테이블 모니터링 및 알림 규칙 설정
- [ ] Vector Search Index 자동 동기화 확인

## 참고 문서

- [Agent Framework 공식 문서](https://docs.databricks.com/aws/en/generative-ai/create-log-agent.html)
- [Model Serving 공식 문서](https://docs.databricks.com/aws/en/machine-learning/model-serving/index.html)
- [MLflow Tracing 공식 문서](https://mlflow.org/docs/latest/llms/tracing/index.html)
