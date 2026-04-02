# 고급 청킹

## 청킹 전략 심층 비교

청킹(Chunking)은 RAG 파이프라인의 **첫 번째 관문** 으로, 검색 품질에 결정적인 영향을 미칩니다. 잘못된 청킹은 아무리 좋은 검색 알고리즘과 Re-ranking을 사용해도 보완할 수 없습니다.

아래 표는 주요 청킹 기법을 비교합니다.

| 청킹 기법 | 설명 | ML 모델 필요 | Databricks 지원 | 난이도 |
|---------|------|------------|--------------|------|
| **고정 크기 (Fixed-size)** | 토큰/글자 수 기준으로 기계적 분할. 간단하지만 문맥이 중간에서 끊길 위험 | N/A | ✅ | 낮음 |
| **Recursive** | 문단 → 문장 → 단어 순으로 재귀적 분할. **가장 표준적**. 문맥 보존율이 높음 | N/A | ✅ | 낮음 |
| **부모/자식 (Parent-Child)** | Parent(큰 단위)로 LLM에 전달하고, Child(작은 단위)로 검색. 환각 방지에 효과적 | N/A | ✅ | 중간 |
| **의미 기반 (Semantic)** | 문장별 임베딩 후 코사인 유사도가 크게 변하는 지점에서 분할 | Embedding | ✅ | 중간 |
| **명제 기반 (Proposition)** | LLM으로 각 문장을 "독립적 명제(self-contained proposition)"로 변환 후 분할. 정보 밀도 극대화 | LLM | ✅ | 높음 |

## 부모/자식 청킹 상세

부모/자식(Parent-Child) 청킹은 **검색 정확도와 문맥 풍부함** 이라는 두 가지 상충하는 요구사항을 동시에 해결하는 전략입니다.

**핵심 원리:**

- **Child 청크**(작은 단위, 100~200 토큰): Vector Store에 저장되어 **검색** 에 사용. 작은 크기 덕분에 정보 밀도가 높아 검색 정확도가 높음
- **Parent 청크**(큰 단위, 500~1000 토큰): 검색된 Child의 상위 문맥으로, **LLM에 전달** 되어 풍부한 맥락 제공
- 결과적으로 **"작은 청크의 높은 검색 정확도 + 큰 청크의 풍부한 문맥"** 을 동시에 확보

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from langchain_databricks import DatabricksVectorSearch

# Child 청크용 스플리터 (검색용 - 작은 크기)
child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30,
    separators=["\n\n", "\n", ".", "!", "?", " "]
)

# Parent 청크용 스플리터 (LLM 전달용 - 큰 크기)
parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", "!", "?", " "]
)

# Parent Document Retriever 설정
store = InMemoryStore()  # Parent 청크 저장소 (프로덕션에서는 Redis/Delta 사용)

parent_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,        # Child 청크가 저장된 벡터 스토어
    docstore=store,                 # Parent 청크 저장소
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# 문서 추가 (자동으로 Parent/Child 분할)
parent_retriever.add_documents(documents)

# 검색: Child로 매칭, Parent를 반환
results = parent_retriever.invoke("Unity Catalog 권한 설정 방법")
# → Child 크기(200토큰)로 정확한 매칭 수행
# → 해당 Child의 Parent(1000토큰)를 반환하여 LLM에 풍부한 문맥 제공
```

## 의미 기반 청킹 상세

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_databricks import DatabricksEmbeddings

embeddings = DatabricksEmbeddings(endpoint="databricks-bge-large-en")

# 의미 기반 청킹: 코사인 유사도 변화 지점에서 분할
semantic_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",  # 유사도 변화가 상위 N%일 때 분할
    breakpoint_threshold_amount=95,          # 상위 5% 변화 지점에서 분할
)

chunks = semantic_splitter.create_documents([long_document_text])
print(f"의미 기반 분할 결과: {len(chunks)}개 청크")
```
