# Reranking 전략

## 개념

Re-ranking은 초기 검색 결과를 **Cross-encoder** 모델로 재정렬하여 정밀도를 높이는 2단계 검색 전략입니다.

```
[쿼리] → Retriever (Top-K 후보) → Reranker (재정렬) → 최종 Top-N
```

- **1단계 (Retriever)**: 빠르게 후보군을 추출 (recall 중심, Top-20~50)
- **2단계 (Reranker)**: 후보군을 정밀하게 재정렬 (precision 중심, Top-3~5)

## Reranking 전략 심층 비교

아래 표는 주요 Reranking 전략을 비교합니다.

| 전략 | 설명 | ML 모델 | Databricks 지원 | 속도 | 정확도 |
|------|------|--------|--------------|------|-------|
| **Learning to Rank** | XGBoost/LightGBM으로 메타 피처(최신성, 인기도, 클릭률)를 결합하여 최종 순위 예측 | Classic ML | ✅ | 빠름 | 보통 |
| **Collaborative Filtering** | 사용자 과거 검색/선호 기반 개인 맞춤 재배치. Cold Start 문제 있음 | Classic ML | ✅ | 빠름 | 보통 |
| **Cross-Encoder** | 쿼리+문서를 함께 트랜스포머에 입력. **가장 정확하지만 느림**. BGE-Reranker, Cohere Rerank | Embedding | ✅ | 느림 | 높음 |
| **ColBERT (Late Interaction)** | 토큰 단위 벡터를 미리 계산하고, 쿼리 시 MaxSim 연산으로 비교. Cross-Encoder에 준하는 정확도 + 빠른 속도 | Embedding | ✅ | 빠름 | 높음 |
| **LLM 기반 (RankGPT)** | LLM이 직접 문서 목록을 읽고 순위를 정렬. 최고 수준의 문맥 이해. 비용이 가장 높음 | LLM | ✅ | 매우 느림 | 매우 높음 |

## Cross-encoder vs Bi-encoder

| 구분 | Bi-encoder (Retriever) | Cross-encoder (Reranker) |
|------|----------------------|------------------------|
| 입력 | 쿼리와 문서를 각각 인코딩 | 쿼리-문서 쌍을 함께 인코딩 |
| 속도 | 빠름 (벡터 유사도 연산) | 느림 (쌍별 추론) |
| 정확도 | 상대적으로 낮음 | 높음 (쿼리-문서 상호작용 포착) |
| 용도 | 대규모 후보 검색 | 소규모 후보 재정렬 |

## Cohere Reranker 활용

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

# Cohere Reranker 설정
reranker = CohereRerank(
    model="rerank-v3.5",
    top_n=5  # 최종 반환 문서 수
)

# 기존 Retriever + Reranker 결합
compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=ensemble_retriever  # 앙상블 Retriever에서 후보 추출
)

results = compression_retriever.invoke("Unity Catalog 권한 설정 방법")
```

## BGE Reranker 활용 (오픈소스)

```python
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker

# BGE Reranker (오픈소스, 로컬 실행 가능)
cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
reranker = CrossEncoderReranker(model=cross_encoder, top_n=5)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=ensemble_retriever
)
```

{% hint style="tip" %}
`bge-reranker-v2-m3`는 다국어를 지원하므로 한국어 문서에도 효과적입니다. Databricks Model Serving에 배포하여 사용할 수도 있습니다.
{% endhint %}

## ColBERT (Late Interaction) 활용

ColBERT는 Cross-Encoder의 정확도와 Bi-Encoder의 속도를 절충한 **Late Interaction** 방식입니다.

```python
# ColBERT는 토큰 단위 벡터를 미리 계산 (인덱싱 시)
# 검색 시에는 MaxSim (Maximum Similarity) 연산으로 빠르게 비교

# RAGatouille 라이브러리를 통한 ColBERT 활용
from ragatouille import RAGPretrainedModel

# ColBERT 모델 로드
colbert = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

# 문서 인덱싱 (토큰 단위 벡터 사전 계산)
colbert.index(
    collection=[doc.page_content for doc in documents],
    index_name="korean_docs_colbert",
)

# 검색 (MaxSim 연산으로 빠른 비교)
results = colbert.search(query="Unity Catalog 권한 설정", k=5)
```

## LLM 기반 Reranking (RankGPT)

```python
def llm_rerank(query: str, documents: list, top_n: int = 5) -> list:
    """LLM이 직접 문서 순위를 정렬 (RankGPT 방식)"""
    doc_list = "\n".join([
        f"[{i+1}] {doc.page_content[:300]}"
        for i, doc in enumerate(documents)
    ])

    prompt = f"""다음 질문에 가장 관련성이 높은 문서 순서대로 번호를 나열하세요.
상위 {top_n}개만 선택하세요.

질문: {query}

문서 목록:
{doc_list}

관련성 높은 순서 (번호만): """

    response = llm.invoke(prompt)
    # 응답에서 번호 추출하여 재정렬
    ranked_indices = [int(x.strip()) - 1 for x in response.content.split(",")[:top_n]]
    return [documents[i] for i in ranked_indices if i < len(documents)]
```

{% hint style="warning" %}
LLM 기반 Reranking은 문맥 이해가 가장 뛰어나지만, **비용과 지연 시간이 매우 높습니다**(문서당 수백~수천 토큰 소비). 고가치 쿼리나 배치 처리에만 사용하고, 실시간 서비스에는 Cross-Encoder나 ColBERT를 권장합니다.
{% endhint %}

## Re-ranking 전략 상세: 언제, 얼마나 Rerank할 것인가

Re-ranking의 효과를 극대화하려면 **초기 검색 범위** 와 **최종 반환 수** 를 적절히 설정해야 합니다.

| 설정 | 권장값 | 이유 |
|------|--------|------|
| **초기 검색 (Top-K)** | 20~50 | 너무 적으면 관련 문서를 놓치고, 너무 많으면 Reranker 비용 증가 |
| **최종 반환 (Top-N)** | 3~5 | LLM 컨텍스트 윈도우와 비용을 고려한 최적 범위 |
| **Reranker 모델** | bge-reranker-v2-m3 | 다국어 지원, 비용 효율적, Databricks에 배포 가능 |

```python
# 실전 Reranking 파이프라인: 50개 후보 → 5개 최종 선택
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker

# 1단계: 넓은 범위로 후보 검색
base_retriever = ensemble_retriever  # 또는 vs_retriever
base_retriever.search_kwargs = {"k": 50}

# 2단계: Cross-encoder로 정밀 재정렬
cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
reranker = CrossEncoderReranker(model=cross_encoder, top_n=5)

# 결합
final_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=base_retriever
)
```

{% hint style="warning" %}
Reranker는 쿼리-문서 쌍별로 추론을 수행하므로, 초기 검색 결과가 많을수록 지연 시간이 증가합니다. P95 지연 시간 목표를 기준으로 Top-K를 설정하세요. 일반적으로 K=20이면 Reranking에 100~300ms가 추가됩니다.
{% endhint %}
