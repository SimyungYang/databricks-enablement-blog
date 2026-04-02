# Databricks Advanced RAG 구현 로드맵

## 적용 가이드

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

---

## Phase 1: 기본 (Baseline)

**목표**: 동작하는 RAG 파이프라인 구축

| 구성 요소 | 기술 선택 | 비고 |
|---------|---------|------|
| 검색 | Databricks Vector Search + `query_type="hybrid"` | 내장 하이브리드 검색 활용 |
| 청킹 | Recursive Character Text Splitter (500~1000 토큰) | 가장 범용적인 전략 |
| 임베딩 | `databricks-bge-large-en` 또는 `bge-m3` | 다국어 지원 모델 선택 |
| LLM | `databricks-claude-sonnet-4` 또는 `databricks-meta-llama-3-3-70b-instruct` | Foundation Model API |
| 평가 | Databricks Agent Evaluation (기본 메트릭) | 검색 정밀도, 답변 정확도 |

```python
# Phase 1 구현 예시
from langchain_databricks import DatabricksVectorSearch, ChatDatabricks
from langchain.chains import RetrievalQA

# 기본 Vector Search Retriever
retriever = DatabricksVectorSearch(
    endpoint="vs-endpoint",
    index_name="catalog.schema.docs_index",
    columns=["content", "source"],
).as_retriever(search_kwargs={"k": 5, "query_type": "hybrid"})

# 기본 RAG 체인
llm = ChatDatabricks(endpoint="databricks-claude-sonnet-4")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
)

result = qa_chain.invoke({"query": "Unity Catalog 권한 설정 방법"})
```

## Phase 2: 중급 (Enhanced)

**목표**: 한국어 검색 품질 강화 + 정밀도 향상

| 구성 요소 | 기술 선택 | Phase 1 대비 변화 |
|---------|---------|----------------|
| 한국어 처리 | Kiwi 형태소 분석기 + Custom BM25 Retriever | 한국어 키워드 검색 정확도 대폭 향상 |
| 검색 | EnsembleRetriever (Kiwi BM25 + VS Dense) | 하이브리드 검색 직접 구현 |
| Re-ranking | Cross-Encoder (bge-reranker-v2-m3) | 검색 정밀도 30~50% 향상 기대 |
| 청킹 | Parent-Child 또는 Semantic 청킹 | 문맥 보존 + 검색 정확도 향상 |
| 전처리 | Query Rewrite (대화 맥락 반영) | 멀티턴 대화 지원 |

```python
# Phase 2 구현 예시
from kiwipiepy import Kiwi
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker

kiwi = Kiwi()

# 1. Kiwi 기반 BM25 Retriever
bm25 = BM25Retriever.from_documents(
    documents,
    preprocess_func=lambda t: [tok.form for tok in kiwi.tokenize(t)
                                if tok.tag in {"NNG","NNP","VV","VA","SL"}],
    k=20
)

# 2. Vector Search Retriever
vs = DatabricksVectorSearch(
    endpoint="vs-endpoint",
    index_name="catalog.schema.docs_index",
    columns=["content", "source"],
).as_retriever(search_kwargs={"k": 20})

# 3. 앙상블 (RRF)
ensemble = EnsembleRetriever(retrievers=[bm25, vs], weights=[0.4, 0.6])

# 4. Cross-Encoder Reranking
cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
reranker = CrossEncoderReranker(model=cross_encoder, top_n=5)

# 5. 최종 Retriever
final_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=ensemble,
)
```

## Phase 3: 고급 (Advanced)

**목표**: 자기 교정 + 멀티 소스 + Agentic RAG

| 구성 요소 | 기술 선택 | Phase 2 대비 변화 |
|---------|---------|----------------|
| 전처리 | Contextual Retrieval + Query Routing | 문맥 보존 극대화 + 멀티 소스 라우팅 |
| 후처리 | Self-RAG + Corrective RAG | 환각 대폭 감소 |
| 에이전트 | Agentic RAG (Genie 연동, Tool Use) | 동적 검색 전략 결정 |
| 평가 | LLM-as-Judge + Human Evaluation | 정량/정성 평가 결합 |
| 모니터링 | Databricks Lakehouse Monitoring + MLflow | 프로덕션 품질 지속 관리 |

```python
# Phase 3: Agentic RAG with LangGraph
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated

class RAGState(TypedDict):
    question: str
    rewritten_query: str
    route: str
    documents: list
    grade: str
    answer: str
    iteration: int

def route_question(state: RAGState) -> RAGState:
    """질문 의도 분석 → 라우팅"""
    route = route_query(state["question"])
    return {** state, "route": route["source"]}

def retrieve(state: RAGState) -> RAGState:
    """라우팅된 소스에서 검색"""
    if state["route"] == "VECTOR_DB":
        docs = final_retriever.invoke(state["rewritten_query"])
    elif state["route"] == "SQL_DB":
        docs = sql_retriever.invoke(state["rewritten_query"])
    else:
        docs = web_retriever.invoke(state["rewritten_query"])
    return {** state, "documents": docs}

def grade_documents(state: RAGState) -> RAGState:
    """검색 결과 품질 평가 (CRAG)"""
    result = corrective_rag(state["question"], state["documents"], llm)
    return {** state, "grade": result["strategy"], "documents": result["docs"]}

def generate(state: RAGState) -> RAGState:
    """답변 생성 + 충실도 검증 (Self-RAG)"""
    answer = self_rag(state["question"], final_retriever, llm)
    return {** state, "answer": answer}

# LangGraph 워크플로 구성
workflow = StateGraph(RAGState)
workflow.add_node("rewrite", lambda s: {** s, "rewritten_query": rewrite_query(s["question"])})
workflow.add_node("route", route_question)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade", grade_documents)
workflow.add_node("generate", generate)

workflow.set_entry_point("rewrite")
workflow.add_edge("rewrite", "route")
workflow.add_edge("route", "retrieve")
workflow.add_edge("retrieve", "grade")
workflow.add_edge("grade", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()
```

{% hint style="info" %}
**로드맵 적용 팁**: 각 Phase를 넘어갈 때마다 반드시 **평가 메트릭** 을 비교하세요. Phase 2가 Phase 1보다 검색 정밀도(Precision@5)에서 최소 10% 이상 개선되지 않는다면, 기존 Phase의 튜닝(가중치, 청크 크기, 임베딩 모델)에 더 투자하는 것이 효율적입니다.
{% endhint %}

---

## 참고 문서

- [Databricks Vector Search 공식 문서](https://docs.databricks.com/aws/en/generative-ai/vector-search/index.html)
- [LangChain Retrievers 문서](https://python.langchain.com/docs/how_to/#retrievers)
- [LangChain EnsembleRetriever](https://python.langchain.com/docs/how_to/ensemble_retriever/)
- [Cohere Rerank API 문서](https://docs.cohere.com/docs/rerank)
- [BGE Reranker (BAAI)](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- [Anthropic Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [Self-RAG 논문](https://arxiv.org/abs/2310.11511)
- [Corrective RAG (CRAG) 논문](https://arxiv.org/abs/2401.15884)
- [FLARE 논문](https://arxiv.org/abs/2305.06983)
- [ColBERT v2](https://arxiv.org/abs/2112.01488)
- [Kiwi 한국어 형태소 분석기](https://github.com/bab2min/Kiwi)
- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
