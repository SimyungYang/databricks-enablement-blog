# RAG 평가

RAG 시스템의 품질을 체계적으로 측정하고 개선하는 것은 프로덕션 배포 전 필수 단계입니다. Databricks는 MLflow Evaluate를 통해 RAG 전용 평가 프레임워크를 제공합니다.

## 1. 평가가 필요한 이유

RAG 시스템은 검색과 생성 두 단계로 구성되므로, 각 단계별로 품질을 측정해야 합니다.

```
검색 품질 (Retrieval)     +    생성 품질 (Generation)    =    전체 RAG 품질
- 관련 문서를 찾았는가?         - 답변이 정확한가?
- 불필요한 문서가 포함?         - 환각이 없는가?
                                - 출처와 일치하는가?
```

## 2. 주요 평가 메트릭

| 메트릭 | 설명 | 측정 대상 |
|--------|------|-----------|
| **Faithfulness**| 답변이 검색된 컨텍스트에 근거하는가 | 생성 품질 |
| **Relevance**| 답변이 질문에 관련 있는가 | 생성 품질 |
| **Correctness**| 답변이 정답(ground truth)과 일치하는가 | 전체 품질 |
| **Chunk Relevance**| 검색된 청크가 질문에 관련 있는가 | 검색 품질 |

{% hint style="info" %}
**Faithfulness** 는 RAG에서 가장 중요한 메트릭입니다. 이 수치가 낮으면 LLM이 검색 결과를 무시하고 자체 지식으로 답변(환각)하고 있다는 의미입니다.
{% endhint %}

## 3. 평가 데이터셋 구축

평가를 위해 질문-정답 쌍(Ground Truth)이 필요합니다.

```python
import pandas as pd

eval_dataset = pd.DataFrame([
    {
        "request": "Databricks Vector Search의 최대 벡터 차원은?",
        "expected_response": "최대 4,096차원까지 지원합니다.",
    },
    {
        "request": "Delta Sync Index와 Direct Vector Access Index의 차이는?",
        "expected_response": "Delta Sync Index는 소스 Delta Table과 자동 동기화되며, Direct Vector Access Index는 REST API로 수동 관리합니다.",
    },
    {
        "request": "Vector Search 엔드포인트당 최대 인덱스 수는?",
        "expected_response": "엔드포인트당 최대 50개 인덱스를 생성할 수 있습니다.",
    },
    {
        "request": "하이브리드 검색에서 사용하는 결과 병합 알고리즘은?",
        "expected_response": "Reciprocal Rank Fusion(RRF) 알고리즘을 사용합니다.",
    },
    {
        "request": "Foundation Model API에서 제공하는 임베딩 모델은?",
        "expected_response": "databricks-gte-large-en과 databricks-bge-large-en 모델을 제공합니다.",
    }
])
```

{% hint style="warning" %}
평가 데이터셋은 최소 20~50개 이상의 질문-정답 쌍을 포함하는 것이 좋습니다. 다양한 난이도와 주제를 포함하세요.
{% endhint %}

## 4. MLflow Evaluate 실행

### RAG 체인 평가

```python
import mlflow

# 모델이 이미 로깅된 경우
model_uri = "models:/catalog.schema.rag_agent/1"

results = mlflow.evaluate(
    model=model_uri,
    data=eval_dataset,
    model_type="databricks-agent",
)

# 전체 메트릭 확인
print(results.metrics)
```

### 사전 수집된 답변으로 평가

체인을 매번 실행하지 않고, 이미 생성된 답변을 평가할 수도 있습니다.

```python
# 답변이 이미 포함된 데이터셋
eval_with_responses = pd.DataFrame([
    {
        "request": "Vector Search의 최대 벡터 차원은?",
        "response": "Databricks Vector Search는 최대 4,096차원의 벡터를 지원합니다.",
        "retrieved_context": [
            {"content": "임베딩 차원은 최대 4,096까지 지원됩니다."}
        ],
        "expected_response": "최대 4,096차원까지 지원합니다."
    }
])

results = mlflow.evaluate(
    data=eval_with_responses,
    model_type="databricks-agent",
)

# 요청별 상세 결과 확인
display(results.tables["eval_results"])
```

## 5. 평가 결과 분석

```python
eval_table = results.tables["eval_results"]
low_faith = eval_table[eval_table["response/llm_judged/faithfulness/rating"] == "no"]
low_rel = eval_table[eval_table["response/llm_judged/relevance_to_query/rating"] == "no"]
print(f"환각 의심: {len(low_faith)}건 | 관련성 부족: {len(low_rel)}건")
```

## 6. 반복 개선 사이클

**반복 개선 사이클:** 평가 실행 → 취약점 분석 → 개선 적용 → 재평가 → (반복)

### 일반적인 개선 방법

| 문제 | 원인 | 해결 방법 |
|------|------|-----------|
| Faithfulness 낮음 | 프롬프트가 컨텍스트 무시 유도 | 프롬프트에 "컨텍스트만 사용" 강조 |
| Relevance 낮음 | 검색 결과 품질 부족 | 청킹 전략 변경, k값 조정 |
| Correctness 낮음 | 소스 데이터 부족 | 문서 추가, 청크 크기 조정 |
| 검색 누락 | 임베딩 품질 문제 | 다른 임베딩 모델 시도 |

{% hint style="success" %}
평가 결과는 MLflow Experiment UI에서 시각적으로 비교할 수 있습니다. 여러 버전의 체인을 비교하여 최적의 설정을 찾으세요.
{% endhint %}

## 다음 단계

평가가 완료되면 [RAG 배포](deployment.md)에서 프로덕션 환경에 배포합니다.
