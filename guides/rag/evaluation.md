# RAG 평가

RAG 시스템의 품질을 체계적으로 측정하고 개선하는 것은 프로덕션 배포 전 필수 단계입니다. Databricks는 MLflow Evaluate를 통해 RAG 전용 평가 프레임워크를 제공합니다.

## RAG 평가의 특수성: 검색과 생성을 분리하여 평가해야 하는 이유

RAG 시스템의 평가는 일반 LLM 평가와 근본적으로 다릅니다. **두 개의 독립적인 단계**(검색 + 생성)가 결합되어 있기 때문에, 문제의 원인을 정확히 파악하려면 각 단계를 **독립적으로** 평가해야 합니다.

### 왜 분리 평가가 중요한가?

"답변이 부정확하다"는 증상의 원인은 크게 세 가지입니다:

| 원인 | 검색 품질 | 생성 품질 | 해결 방법 |
|------|----------|----------|-----------|
| **관련 문서를 못 찾음** | 낮음 | 높음 | 임베딩 모델 변경, 청킹 전략 수정, 하이브리드 검색 도입 |
| **관련 문서를 찾았지만 LLM이 무시** | 높음 | 낮음 | 프롬프트 수정, "컨텍스트만 사용" 강조, 모델 변경 |
| **소스 데이터에 정보 자체가 없음** | 해당 없음 | 해당 없음 | 문서 추가, 데이터 소스 확장 |

만약 검색과 생성을 분리하지 않고 최종 답변만 평가한다면, "답변이 틀렸다"는 것은 알 수 있지만 **어디를 고쳐야 하는지** 는 알 수 없습니다.

### RAGAS (RAG Assessment) 프레임워크

RAGAS는 RAG 시스템 평가를 위한 업계 표준 프레임워크입니다. Databricks MLflow Evaluate는 RAGAS의 핵심 메트릭을 내장하고 있습니다.

| RAGAS 메트릭 | 측정 대상 | 계산 방법 | MLflow 대응 |
|-------------|----------|-----------|------------|
| **Faithfulness** | 답변이 컨텍스트에 근거하는가 | 답변의 각 주장이 컨텍스트에서 추론 가능한지 검증 | `response/llm_judged/faithfulness` |
| **Answer Relevancy** | 답변이 질문에 관련 있는가 | 답변에서 역으로 질문을 생성하여 원래 질문과 비교 | `response/llm_judged/relevance_to_query` |
| **Context Precision** | 검색된 컨텍스트 중 관련 있는 것의 비율 | 각 컨텍스트의 관련성을 평가하여 정밀도 계산 | `retrieval/llm_judged/chunk_relevance` |
| **Context Recall** | 정답에 필요한 정보가 컨텍스트에 포함되는가 | Ground Truth의 각 문장이 컨텍스트에서 찾아지는지 확인 | Ground Truth 비교로 간접 측정 |

{% hint style="info" %}
RAGAS의 핵심 통찰은 **"LLM을 Judge로 사용하여 LLM을 평가한다" **는 점입니다. 이를 **LLM-as-Judge** 패턴이라고 합니다. 사람의 판단과 높은 상관관계를 보이며, 대규모 평가를 자동화할 수 있습니다.
{% endhint %}

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
| **Faithfulness** | 답변이 검색된 컨텍스트에 근거하는가 | 생성 품질 |
| **Relevance** | 답변이 질문에 관련 있는가 | 생성 품질 |
| **Correctness** | 답변이 정답(ground truth)과 일치하는가 | 전체 품질 |
| **Chunk Relevance** | 검색된 청크가 질문에 관련 있는가 | 검색 품질 |

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

## 7. 실전 평가 파이프라인

프로덕션 RAG 시스템을 위한 체계적인 평가 파이프라인을 구축하는 방법입니다.

### 평가 파이프라인 구성

```
1. 평가 데이터셋 준비 (50~100개 질문-정답 쌍)
     │
2. RAG 체인 실행 → 답변 + 검색 결과 수집
     │
3. MLflow Evaluate 실행 → 메트릭 산출
     │
4. 결과 분석 → 취약점 식별
     │
5. 개선 적용 (청킹/프롬프트/모델 변경)
     │
6. 재평가 → 개선 효과 확인
     │
7. (반복) 목표 메트릭 달성 시 배포
```

### 평가 데이터셋 구축 전략

좋은 평가 데이터셋은 RAG 시스템의 품질을 결정합니다. 다음 전략으로 구축하세요:

**1. 난이도 분포**

| 난이도 | 비율 | 예시 |
|--------|------|------|
| **쉬움**(단일 청크에서 답변 가능) | 30% | "Vector Search의 최대 차원은?" |
| **보통**(여러 청크 종합 필요) | 40% | "Delta Sync Index와 Direct Access Index의 차이점은?" |
| **어려움**(추론 필요) | 20% | "대규모 한국어 문서에 최적의 RAG 아키텍처는?" |
| **답변 불가**(소스에 정보 없음) | 10% | "Databricks의 2026년 로드맵은?" |

**2. LLM을 활용한 평가 데이터 자동 생성**

```python
from langchain_databricks import ChatDatabricks

llm = ChatDatabricks(endpoint="databricks-meta-llama-3-3-70b-instruct")

def generate_eval_questions(chunk: str, num_questions: int = 3) -> list:
    """청크 텍스트에서 평가용 질문-정답 쌍을 자동 생성"""
    prompt = f"""다음 텍스트를 읽고, 이 텍스트로 답변할 수 있는 질문-정답 쌍을 {num_questions}개 생성하세요.

텍스트:
{chunk}

JSON 형식으로 출력하세요:
[{{"question": "질문", "answer": "정답"}}]"""

    response = llm.invoke(prompt)
    return response.content
```

{% hint style="warning" %}
자동 생성된 평가 데이터는 반드시 **사람이 검토** 해야 합니다. LLM이 생성한 질문은 너무 쉽거나, 원문을 그대로 반복하는 경우가 많습니다. 최소 20%는 사람이 직접 작성한 질문을 포함하세요.
{% endhint %}

### A/B 테스트로 설정 비교

여러 RAG 설정을 체계적으로 비교하는 방법입니다.

```python
import mlflow

configs = [
    {"name": "baseline", "chunk_size": 500, "model": "gte-large-en", "k": 3},
    {"name": "larger_chunks", "chunk_size": 1000, "model": "gte-large-en", "k": 3},
    {"name": "more_results", "chunk_size": 500, "model": "gte-large-en", "k": 7},
    {"name": "korean_optimized", "chunk_size": 800, "model": "multilingual-e5", "k": 5},
]

for config in configs:
    with mlflow.start_run(run_name=config["name"]):
        # 설정에 따라 RAG 체인 구성
        chain = build_rag_chain(** config)

        # 평가 실행
        results = mlflow.evaluate(
            model=chain,
            data=eval_dataset,
            model_type="databricks-agent",
        )

        # 설정 파라미터 로깅
        mlflow.log_params(config)
        print(f"{config['name']}: {results.metrics}")
```

{% hint style="success" %}
MLflow Experiment UI에서 여러 Run을 시각적으로 비교할 수 있습니다. 메트릭 차트에서 각 설정의 Faithfulness, Relevance, Correctness를 한눈에 비교하세요.
{% endhint %}

## 다음 단계

평가가 완료되면 [RAG 배포](deployment.md)에서 프로덕션 환경에 배포합니다.
