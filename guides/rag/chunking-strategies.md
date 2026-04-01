# 청킹 전략 상세

RAG 시스템에서 문서를 어떻게 분할(청킹)하느냐에 따라 검색 품질과 생성 품질이 크게 달라집니다. 이 가이드에서는 다양한 청킹 전략을 비교하고, 각 전략의 구현 방법을 다룹니다.

## 1. 청킹이 RAG 품질에 미치는 영향

청크 크기는 RAG 파이프라인 전반에 영향을 미칩니다:

| 청크 크기 | 검색 정밀도 | 컨텍스트 품질 | 토큰 비용 |
|-----------|------------|-------------|----------|
| **너무 작음**(< 100 토큰) | 높음 | 컨텍스트 부족, 의미 불완전 | 낮음 |
| **적정**(256~1024 토큰) | 적정 | 충분한 컨텍스트 | 적정 |
| **너무 큼**(> 2000 토큰) | 낮음 (노이즈 포함) | 관련 없는 정보 혼재 | 높음 |

{% hint style="info" %}
일반적으로 **256~1024 토큰** 이 적정 범위이지만, 도메인과 문서 특성에 따라 달라집니다. 반드시 평가를 통해 최적 크기를 찾아야 합니다.
{% endhint %}

## 2. 전략별 비교

| 전략 | 방식 | 장점 | 단점 | 추천 상황 |
|------|------|------|------|----------|
| **Fixed-size**| 고정 문자/토큰 수로 분할 | 구현 간단, 예측 가능 | 문장/의미 중간에서 잘림 | 빠른 프로토타이핑 |
| **Recursive**| 구분자 우선순위로 재귀 분할 | 범용적, 구조 보존 | 최적 구분자 설계 필요 | 대부분의 프로덕션 환경 |
| **Semantic**| 임베딩 유사도로 경계 결정 | 의미 전환점 자동 감지 | 연산 비용 높음, 임베딩 의존 | 주제가 다양한 문서 |
| **Document-structure**| 헤딩/섹션 기반 분할 | 문서 구조 완벽 보존 | 구조화된 문서에만 적용 | Markdown, HTML 문서 |

## 3. 각 전략 코드 예제

### RecursiveCharacterTextSplitter (가장 범용적)

LangChain에서 가장 많이 사용되는 텍스트 분할기입니다. 구분자 우선순위에 따라 재귀적으로 분할합니다.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=500,       # 청크 최대 크기 (문자 수)
    chunk_overlap=50,     # 청크 간 오버랩
    length_function=len,  # 또는 토큰 기반 길이 함수
)

chunks = splitter.split_text(document_text)
```

**동작 원리:**
1. `\n\n` (문단)으로 먼저 분할 시도
2. 청크가 여전히 크면 `\n` (줄바꿈)으로 재분할
3. 그래도 크면 `. ` (문장)으로 재분할
4. 최종적으로 공백, 문자 단위까지 분할

### SemanticChunker (의미 기반)

임베딩 유사도가 급격히 변하는 지점을 경계로 청크를 분할합니다.

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_databricks import DatabricksEmbeddings

embeddings = DatabricksEmbeddings(endpoint="databricks-gte-large-en")

semantic_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",  # 또는 "standard_deviation"
    breakpoint_threshold_amount=95,          # 상위 5% 변화점에서 분할
)

chunks = semantic_splitter.split_text(document_text)
```

{% hint style="warning" %}
SemanticChunker는 모든 문장에 대해 임베딩을 계산하므로, 대규모 문서셋에서는 비용과 시간이 크게 증가합니다. 문서 수가 적고 품질이 중요한 경우에 적합합니다.
{% endhint %}

### MarkdownHeaderTextSplitter (문서 구조 기반)

Markdown 문서의 헤딩을 기준으로 분할하며, 헤딩 정보를 메타데이터로 보존합니다.

```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]

md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)

chunks = md_splitter.split_text(markdown_text)
# 각 청크에 {"h1": "...", "h2": "...", "h3": "..."} 메타데이터 포함
```

### 토큰 기반 분할

문자 수 대신 토큰 수 기반으로 분할하면 LLM 컨텍스트 윈도우를 더 정확하게 관리할 수 있습니다.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# tiktoken 기반 토큰 카운팅
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=256,       # 256 토큰
    chunk_overlap=30,     # 30 토큰 오버랩
)

chunks = splitter.split_text(document_text)
```

## 4. 청크 오버랩 전략

오버랩은 인접 청크 간에 겹치는 영역을 두어 경계에서의 정보 손실을 방지합니다.

| 오버랩 비율 | 장점 | 단점 |
|------------|------|------|
| **0%**| 중복 없음, 인덱스 크기 최소 | 경계에서 문맥 단절 |
| **10~20%**(권장) | 경계 문맥 보존, 검색 품질 향상 | 약간의 인덱스 증가 |
| **30% 이상**| 문맥 보존 극대화 | 중복 과다, 비용 증가, 검색 노이즈 |

```python
# 권장: chunk_size의 10~20% 오버랩
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=75,  # 15% 오버랩
)
```

{% hint style="tip" %}
오버랩이 너무 크면 동일한 내용이 여러 청크에 포함되어 검색 결과가 중복될 수 있습니다. **10~20%** 를 시작점으로 설정하고 평가를 통해 조정하세요.
{% endhint %}

## 5. 메타데이터 첨부

청크에 메타데이터를 첨부하면 검색 시 필터링으로 정밀도를 높일 수 있습니다.

### 권장 메타데이터 필드

| 필드 | 용도 | 예시 |
|------|------|------|
| `source` | 원본 파일 경로/이름 | `"policies/hr-guide.pdf"` |
| `page` | 페이지 번호 | `3` |
| `section` | 섹션/챕터 제목 | `"휴가 정책"` |
| `doc_type` | 문서 유형 | `"policy"`, `"faq"`, `"manual"` |
| `created_at` | 문서 생성/수정 일자 | `"2025-01-15"` |

### 메타데이터 첨부 예제

```python
from langchain.schema import Document

def create_chunks_with_metadata(file_path, text, splitter):
    """청크 생성 시 메타데이터 첨부"""
    chunks = splitter.split_text(text)
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "source": file_path,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "doc_type": "guide",
                "created_at": "2025-06-15",
            }
        )
        documents.append(doc)
    return documents

docs = create_chunks_with_metadata(
    "guides/rag-overview.md", long_text, splitter
)
```

### 메타데이터 기반 필터 검색

```python
from langchain_databricks import DatabricksVectorSearch

vs = DatabricksVectorSearch(
    endpoint="vs-endpoint",
    index_name="catalog.schema.docs_index",
    columns=["content", "source", "doc_type", "created_at"]
)

retriever = vs.as_retriever(
    search_kwargs={
        "k": 5,
        "filters": {"doc_type": "policy"}  # 정책 문서만 검색
    }
)
```

{% hint style="info" %}
Databricks Vector Search는 메타데이터 필터를 서버 사이드에서 처리하므로, 대규모 인덱스에서도 효율적으로 필터링됩니다. Self-Query Retriever와 결합하면 사용자의 자연어 질문에서 자동으로 필터를 추출할 수 있습니다.
{% endhint %}

## 참고 문서

- [LangChain Text Splitters 문서](https://python.langchain.com/docs/how_to/#text-splitters)
- [LangChain SemanticChunker](https://python.langchain.com/docs/how_to/semantic-chunker/)
- [Databricks Vector Search 필터링](https://docs.databricks.com/aws/en/generative-ai/vector-search/query-vector-search-index.html)
- [Chunking 전략 비교 (LangChain Blog)](https://blog.langchain.dev/evaluating-rag-pipelines-with-ragas-langsmith/)
