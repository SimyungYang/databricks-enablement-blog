# 고급 Retrieval 전략

RAG 시스템의 성능은 **검색(Retrieval) 품질**에 가장 크게 좌우됩니다. 이 가이드에서는 기본 Dense Retrieval을 넘어 다양한 고급 검색 전략을 소개합니다.

## 1. Retriever 유형 비교

| Retriever | 방식 | 장점 | 단점 | 적합 시나리오 |
|-----------|------|------|------|--------------|
| **Dense Retriever** | 벡터 유사도 검색 (임베딩) | 의미적 유사성 포착, 동의어 처리 | 정확한 키워드 매칭 약함 | 일반 Q&A, 자연어 질의 |
| **Sparse Retriever** (BM25/TF-IDF) | 키워드 빈도 기반 검색 | 정확한 용어 매칭, 빠른 속도 | 동의어·문맥 이해 불가 | 전문 용어, 코드 검색 |
| **Hybrid Retriever** | Dense + Sparse 결합 | 두 방식의 장점 통합 | 가중치 튜닝 필요 | 대부분의 프로덕션 환경 |
| **Multi-Query Retriever** | 하나의 질문을 여러 쿼리로 변환 | 검색 recall 향상 | LLM 호출 비용 추가 | 복잡한 질문, 모호한 질의 |
| **Parent Document Retriever** | 작은 청크로 검색, 큰 문서로 반환 | 검색 정밀도 + 풍부한 컨텍스트 | 인덱스 구조 복잡 | 긴 문서 기반 Q&A |
| **Self-Query Retriever** | 메타데이터 필터를 자동 추출 | 구조화된 필터링 가능 | LLM 의존, 메타데이터 설계 필요 | 날짜·카테고리 기반 필터링 |

{% hint style="info" %}
실무에서는 **Hybrid Retriever + Reranking** 조합이 가장 균형 잡힌 성능을 제공합니다. 단일 Retriever만으로는 다양한 쿼리 패턴을 커버하기 어렵습니다.
{% endhint %}

## 2. 앙상블 Retriever (Ensemble Retriever)

### 개념

앙상블 Retriever는 서로 다른 특성의 Retriever를 결합하여 각각의 약점을 보완합니다. 가장 일반적인 조합은 **BM25 (키워드) + Vector Search (의미)**입니다.

### Reciprocal Rank Fusion (RRF) 알고리즘

앙상블 Retriever는 RRF 알고리즘으로 결과를 병합합니다:

```
RRF_score(d) = Σ 1 / (k + rank_i(d))
```

- `k`: 상수 (기본값 60), 순위가 낮은 문서의 영향력 조절
- `rank_i(d)`: i번째 Retriever에서 문서 d의 순위
- 여러 Retriever에서 모두 높은 순위를 받은 문서가 최종 상위로 올라감

### 가중치 조절

- `weights=[0.5, 0.5]`: 두 Retriever를 동등하게 반영
- `weights=[0.7, 0.3]`: BM25 비중을 높이면 **정확한 키워드 매칭** 강화
- `weights=[0.3, 0.7]`: Vector Search 비중을 높이면 **의미적 유사성** 강화

### LangChain EnsembleRetriever 코드 예제

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_databricks import DatabricksVectorSearch

# BM25 Retriever (키워드 기반)
bm25_retriever = BM25Retriever.from_documents(documents, k=5)

# Vector Search Retriever (의미 기반)
vs_retriever = DatabricksVectorSearch(
    endpoint="vs-endpoint",
    index_name="catalog.schema.index",
    columns=["content", "source"]
).as_retriever(search_kwargs={"k": 5})

# 앙상블 (RRF)
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vs_retriever],
    weights=[0.4, 0.6]  # Vector Search에 더 높은 가중치
)

# 검색 실행
results = ensemble_retriever.invoke("Databricks에서 Delta Lake 사용법")
for doc in results:
    print(f"[{doc.metadata.get('source', 'N/A')}] {doc.page_content[:100]}...")
```

{% hint style="warning" %}
**Databricks Vector Search 하이브리드 검색의 제약사항:**

- Databricks VS의 "Hybrid Search"는 **Dense (임베딩 유사도) + 키워드 필터**를 결합하는 방식이며, 전통적인 **BM25 Sparse Retrieval과는 다릅니다**
- 내장 키워드 검색은 **영어 기반 토크나이저**를 사용하여, 한국어 형태소를 제대로 분리하지 못함
- 따라서 한국어 환경에서는 VS 내장 하이브리드보다 **외부 BM25 (Kiwi 기반) + VS Dense를 EnsembleRetriever로 결합**하는 것이 더 효과적

**해결 전략:**
1. **소규모 문서 (10만건 이하)**: LangChain BM25Retriever (Kiwi 토크나이저) + VS Dense → EnsembleRetriever
2. **대규모 문서**: Elasticsearch/OpenSearch에 Kiwi 분석기 설정 → BM25 서빙 + VS Dense → EnsembleRetriever
3. **VS만 사용**: 임베딩 모델을 한국어에 강한 모델(bge-m3, multilingual-e5)로 선택하여 Dense 검색 품질을 최대한 높임
{% endhint %}

### Multi-Query Retriever 예제

하나의 질문을 LLM이 여러 관점의 쿼리로 변환하여 검색 recall을 높입니다:

```python
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_databricks import ChatDatabricks

llm = ChatDatabricks(endpoint="databricks-claude-sonnet-4")

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=vs_retriever,
    llm=llm,
)

# "Delta Lake 성능 최적화" →
#   1. "Delta Lake 쿼리 속도를 높이는 방법"
#   2. "Delta Lake Z-Order와 파티셔닝 전략"
#   3. "Delta Lake 파일 최적화 설정"
results = multi_query_retriever.invoke("Delta Lake 성능 최적화 방법은?")
```

## 3. Re-ranking

### 개념

Re-ranking은 초기 검색 결과를 **Cross-encoder** 모델로 재정렬하여 정밀도를 높이는 2단계 검색 전략입니다.

```
[쿼리] → Retriever (Top-K 후보) → Reranker (재정렬) → 최종 Top-N
```

- **1단계 (Retriever)**: 빠르게 후보군을 추출 (recall 중심, Top-20~50)
- **2단계 (Reranker)**: 후보군을 정밀하게 재정렬 (precision 중심, Top-3~5)

### Cross-encoder vs Bi-encoder

| 구분 | Bi-encoder (Retriever) | Cross-encoder (Reranker) |
|------|----------------------|------------------------|
| 입력 | 쿼리와 문서를 각각 인코딩 | 쿼리-문서 쌍을 함께 인코딩 |
| 속도 | 빠름 (벡터 유사도 연산) | 느림 (쌍별 추론) |
| 정확도 | 상대적으로 낮음 | 높음 (쿼리-문서 상호작용 포착) |
| 용도 | 대규모 후보 검색 | 소규모 후보 재정렬 |

### Cohere Reranker 활용

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

### BGE Reranker 활용 (오픈소스)

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

## 4. 적용 가이드

### 시나리오별 추천 전략

| 시나리오 | 추천 전략 | 이유 |
|----------|-----------|------|
| **일반 Q&A** | Dense + Reranking | 의미 검색으로 후보 추출 후 정밀 재정렬 |
| **전문 용어가 많은 문서** | Hybrid (BM25 + Dense) | 정확한 용어 매칭과 의미 검색을 동시에 |
| **한국어 문서** | Kiwi 토크나이저 + Hybrid | 형태소 분석 기반 BM25로 한국어 키워드 검색 강화 |
| **법률/의료 문서** | Self-Query + Metadata Filter | 날짜, 카테고리, 법령 번호 등 구조화된 필터링 |
| **긴 문서 기반 Q&A** | Parent Document Retriever | 작은 청크로 검색하되 큰 컨텍스트 반환 |
| **대규모 문서셋 (100K+)** | Vector Search + Reranking | 서버 사이드 검색으로 확장성 확보 |

### 전략 선택 플로우

```
문서에 전문 용어가 많은가?
  ├─ Yes → Hybrid Retriever (BM25 + Dense)
  │         └─ 한국어인가? → Yes → Kiwi 토크나이저 적용
  └─ No → Dense Retriever
              └─ 정밀도가 중요한가?
                   ├─ Yes → + Reranking 추가
                   └─ No → Dense만으로 충분
```

{% hint style="info" %}
처음에는 **Dense Retriever + Reranking** 조합으로 시작하고, 평가 결과에 따라 Hybrid나 Multi-Query를 점진적으로 추가하는 것을 권장합니다.
{% endhint %}

## 참고 문서

- [Databricks Vector Search 공식 문서](https://docs.databricks.com/aws/en/generative-ai/vector-search/index.html)
- [LangChain Retrievers 문서](https://python.langchain.com/docs/how_to/#retrievers)
- [LangChain EnsembleRetriever](https://python.langchain.com/docs/how_to/ensemble_retriever/)
- [Cohere Rerank API 문서](https://docs.cohere.com/docs/rerank)
- [BGE Reranker (BAAI)](https://huggingface.co/BAAI/bge-reranker-v2-m3)
