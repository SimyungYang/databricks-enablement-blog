# 청킹 전략 상세

RAG 시스템에서 문서를 어떻게 분할(청킹)하느냐에 따라 검색 품질과 생성 품질이 크게 달라집니다. 이 가이드에서는 다양한 청킹 전략을 비교하고, 각 전략의 구현 방법을 다룹니다.

## 1. 청킹이 RAG 품질에 미치는 영향

청크 크기는 RAG 파이프라인 전반에 영향을 미칩니다:

| 청크 크기 | 검색 정밀도 | 컨텍스트 품질 | 토큰 비용 |
|-----------|------------|-------------|----------|
| ** 너무 작음**(< 100 토큰) | 높음 | 컨텍스트 부족, 의미 불완전 | 낮음 |
| ** 적정**(256~1024 토큰) | 적정 | 충분한 컨텍스트 | 적정 |
| ** 너무 큼**(> 2000 토큰) | 낮음 (노이즈 포함) | 관련 없는 정보 혼재 | 높음 |

{% hint style="info" %}
일반적으로 **256~1024 토큰** 이 적정 범위이지만, 도메인과 문서 특성에 따라 달라집니다. 반드시 평가를 통해 최적 크기를 찾아야 합니다.
{% endhint %}

### 각 청킹 전략의 "왜"와 트레이드오프

청킹은 단순한 텍스트 분할이 아니라, ** 검색 정밀도와 컨텍스트 품질 사이의 트레이드오프** 를 관리하는 작업입니다.

** 작은 청크 (< 256 토큰)**
- ** 왜 좋은가**: 검색 정밀도가 높아집니다. 질문에 정확히 매칭되는 문장을 찾을 확률이 높습니다.
- ** 왜 나쁜가**: LLM에 전달되는 컨텍스트가 부족합니다. "Unity Catalog의 접근 제어"라는 청크만으로는 전체 맥락을 이해할 수 없습니다.
- ** 적합한 경우**: FAQ, 용어 정의, 짧은 규정 조항

** 큰 청크 (> 1500 토큰)**
- ** 왜 좋은가**: 충분한 컨텍스트를 제공하여 LLM이 맥락을 이해하고 완전한 답변을 생성할 수 있습니다.
- ** 왜 나쁜가**: 청크 내에 관련 없는 내용이 혼재하여 임베딩 벡터의 의미가 희석됩니다. 검색 시 노이즈가 증가합니다.
- ** 적합한 경우**: 긴 서술형 문서, 법률 조항, 기술 사양서

** 적정 청크 (512~1024 토큰)**
- ** 왜 권장되는가**: 대부분의 기술 문서에서 하나의 개념이나 절차를 설명하는 자연스러운 단위입니다.
- ** 트레이드오프**: 모든 문서 유형에 최적은 아닙니다. 반드시 평가를 통해 검증해야 합니다.

### 한국어 특화 청킹 고려사항

한국어 텍스트는 영어와 다른 특성을 가지므로, 청킹 시 추가 고려가 필요합니다:

- ** 토큰 수 차이**: 동일한 의미의 텍스트가 영어 대비 2~3배 많은 토큰을 소비합니다. `chunk_size`를 문자 수 기반으로 설정하면 더 예측 가능합니다.
- ** 조사 결합**: "데이터브릭스에서", "데이터브릭스를" 등 조사가 붙어 동일 단어가 다르게 토큰화됩니다. 형태소 분석기(Kiwi)를 활용한 전처리가 효과적입니다.
- ** 종결어미 기반 분절**: 한국어 문장은 "~합니다.", "~입니다.", "~하세요." 등의 종결어미로 끝납니다. 이를 구분자로 활용하면 자연스러운 문장 경계에서 분할됩니다.

```python
# 한국어 최적화 RecursiveCharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

korean_splitter = RecursiveCharacterTextSplitter(
    separators=[
        "\n\n",      # 문단 경계 (최우선)
        "\n",        # 줄바꿈
        "다. ",      # 평서문 종결
        "요. ",      # 존댓말 종결
        "까? ",      # 의문문 종결
        ". ",        # 일반 마침표
        " ",         # 공백
        "",          # 최후 수단
    ],
    chunk_size=800,    # 한국어는 영어보다 약간 크게 설정
    chunk_overlap=100,
    length_function=len,
)
```

### 최적 청크 크기 실험 결과

실제 한국어 기술 문서(Databricks 가이드, 정책 문서)로 실험한 결과입니다. 동일한 평가 데이터셋(50개 질문)에 대해 각 청크 크기별 성능을 비교했습니다.

| 청크 크기 (문자) | Recall@5 | Faithfulness | 평균 답변 길이 | 비고 |
|-----------------|----------|-------------|--------------|------|
| 200 | 0.72 | 0.85 | 짧음 | 맥락 부족으로 불완전한 답변 빈번 |
| 500 | 0.81 | 0.88 | 적정 | FAQ 스타일 문서에 적합 |
| **800**| **0.86**| **0.91**| ** 적정**| ** 한국어 기술 문서 최적**|
| 1000 | 0.84 | 0.90 | 풍부 | 영어 기술 문서에 적합 |
| 1500 | 0.78 | 0.87 | 매우 풍부 | 노이즈 증가, 비용 상승 |
| 2000 | 0.71 | 0.83 | 매우 풍부 | 관련 없는 정보 혼재 |

{% hint style="tip" %}
한국어 문서에서는 **800 문자**(chunk_overlap=100)가 좋은 시작점입니다. 이는 영어의 1000 토큰과 유사한 의미 밀도를 가집니다. 단, 이 결과는 기술 문서 기준이므로 도메인에 따라 다를 수 있습니다.
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

** 동작 원리:**
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

## 6. 청킹 전략 선택 플로우

어떤 청킹 전략을 선택할지 결정하는 데 도움이 되는 가이드입니다:

```
문서의 구조가 명확한가? (Markdown, HTML 등)
  ├─ Yes → MarkdownHeaderTextSplitter (구조 보존)
  │         └─ 섹션이 너무 긴가?
  │              └─ Yes → + RecursiveCharacterTextSplitter (2차 분할)
  └─ No → 문서의 주제가 자주 전환되는가?
            ├─ Yes → SemanticChunker (의미 경계 자동 감지)
            │         └─ 문서 수가 많은가? (10K+)
            │              └─ Yes → 비용 문제 → Recursive로 전환
            └─ No → RecursiveCharacterTextSplitter (범용적)
                     └─ 한국어인가?
                          ├─ Yes → 종결어미 구분자 추가
                          └─ No → 기본 구분자 사용
```

### 프로덕션 환경 권장 설정

| 환경 | 전략 | chunk_size | chunk_overlap | 비고 |
|------|------|-----------|--------------|------|
| ** 영어 기술 문서**| Recursive | 1000 | 200 | 기본 구분자 |
| ** 한국어 기술 문서**| Recursive + 한국어 구분자 | 800 | 100 | 종결어미 구분자 추가 |
| **Markdown 문서**| MarkdownHeader + Recursive | 800 | 100 | 2단계 분할 |
| **FAQ 문서**| Fixed-size | 300 | 0 | 짧은 청크, 오버랩 불필요 |
| ** 법률/의료 문서**| Semantic | 1200 | 150 | 의미 경계 중요 |

{% hint style="success" %}
** 핵심 원칙**: 완벽한 청킹 전략은 없습니다. 평가 데이터셋을 만들고, 여러 전략을 비교 실험하여 해당 도메인에 최적인 설정을 찾으세요. MLflow Evaluate로 Recall@K, Faithfulness를 측정하면 객관적인 비교가 가능합니다.
{% endhint %}

## 참고 문서

- [LangChain Text Splitters 문서](https://python.langchain.com/docs/how_to/#text-splitters)
- [LangChain SemanticChunker](https://python.langchain.com/docs/how_to/semantic-chunker/)
- [Databricks Vector Search 필터링](https://docs.databricks.com/aws/en/generative-ai/vector-search/query-vector-search-index.html)
- [Chunking 전략 비교 (LangChain Blog)](https://blog.langchain.dev/evaluating-rag-pipelines-with-ragas-langsmith/)
