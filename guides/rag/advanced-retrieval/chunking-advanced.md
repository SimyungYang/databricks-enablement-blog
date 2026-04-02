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
- 결과적으로 **"작은 청크의 높은 검색 정확도 + 큰 청크의 풍부한 문맥" ** 을 동시에 확보

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

---

## 명제 기반 청킹 (Proposition-based Chunking)

명제 기반 청킹은 원본 텍스트를 **독립적으로 이해 가능한 명제(self-contained proposition)** 로 변환한 후 분할하는 기법입니다. 정보 밀도가 가장 높은 청킹 방법이지만, LLM 호출이 필요하므로 비용이 높습니다.

### 핵심 아이디어

일반적인 문장은 문맥(context)에 의존합니다. "그 회사는 2023년에 설립되었다"에서 "그 회사"가 무엇인지는 앞 문장을 봐야 알 수 있습니다. 명제 기반 청킹은 이런 문장을 **"Databricks는 2013년에 설립되었다" ** 와 같이 독립적으로 변환합니다.

### LLM 프롬프트 + Python 구현

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

PROPOSITION_PROMPT = """다음 텍스트를 독립적 명제(self-contained proposition)들로 분해하세요.

규칙:
1. 각 명제는 다른 명제 없이도 완전히 이해 가능해야 합니다
2. 대명사를 구체적 명사로 교체하세요 ("그것" → 실제 대상)
3. 암묵적 주어/목적어를 명시하세요
4. 각 명제는 하나의 사실만 포함하세요
5. 원본의 의미를 변경하지 마세요

텍스트:
{text}

JSON 형식으로 출력:
{{"propositions": ["명제1", "명제2", ...]}}
"""

def extract_propositions(text: str) -> list[str]:
    """텍스트에서 독립적 명제를 추출"""
    response = w.serving_endpoints.query(
        name="databricks-claude-sonnet-4",
        messages=[{"role": "user", "content": PROPOSITION_PROMPT.format(text=text)}],
        temperature=0.0,
    )
    import json
    result = json.loads(response.choices[0].message.content)
    return result["propositions"]

# 사용 예시
text = """Unity Catalog는 Databricks의 통합 거버넌스 솔루션이다.
이것은 2022년에 출시되었으며, 기존의 Hive Metastore를 대체한다.
주요 기능으로 3단계 네임스페이스(catalog.schema.table)와
행/열 수준의 접근 제어를 제공한다."""

propositions = extract_propositions(text)
# 결과:
# [
#   "Unity Catalog는 Databricks의 통합 거버넌스 솔루션이다",
#   "Unity Catalog는 2022년에 출시되었다",
#   "Unity Catalog는 기존의 Hive Metastore를 대체한다",
#   "Unity Catalog는 3단계 네임스페이스(catalog.schema.table)를 제공한다",
#   "Unity Catalog는 행 수준의 접근 제어를 제공한다",
#   "Unity Catalog는 열 수준의 접근 제어를 제공한다"
# ]
```

{% hint style="warning" %}
**비용 주의**: 명제 기반 청킹은 모든 문서를 LLM으로 처리해야 하므로, 대규모 문서에서는 비용이 급증합니다. **고가치 문서(법률 계약서, 기술 사양서)** 에만 선택적으로 적용하고, 일반 문서는 Semantic 또는 Recursive 청킹을 사용하세요.
{% endhint %}

---

## Late Chunking

Jina AI가 2024년에 제안한 기법으로, **기존 청킹의 문맥 손실 문제** 를 근본적으로 해결합니다.

### 기존 방식 vs Late Chunking

| 단계 | 기존 방식 | Late Chunking |
|------|----------|---------------|
| **1단계** | 문서를 청크로 분할 | 문서 전체를 임베딩 모델에 입력 |
| **2단계** | 각 청크를 독립적으로 임베딩 | 모델이 전체 문맥을 보고 토큰별 벡터 생성 |
| **3단계** | 벡터 저장 | 토큰 벡터를 청크 구간별로 평균(pooling) |
| **결과** | 각 청크의 임베딩이 전체 문맥을 모름 | 각 청크의 임베딩이 **전체 문서 문맥을 반영** |

```
기존: [청크1 임베딩] [청크2 임베딩] [청크3 임베딩]
       ↑ 청크1만 봄    ↑ 청크2만 봄    ↑ 청크3만 봄

Late: [============ 전체 문서 임베딩 ============]
       [청크1 pooling]  [청크2 pooling]  [청크3 pooling]
       ↑ 전체 문맥 반영  ↑ 전체 문맥 반영  ↑ 전체 문맥 반영
```

### Late Chunking의 장점

- **문맥 보존**: "그것", "이 회사" 같은 대명사의 참조 대상이 임베딩에 반영됨
- **경계 문제 완화**: 청크 경계에서 잘린 정보도 전체 문맥에서 보완됨
- **추가 비용 없음**: LLM 호출 불필요 (임베딩 모델만 사용)

{% hint style="info" %}
**제약 사항**: Late Chunking은 임베딩 모델의 **최대 입력 길이** 에 제한됩니다. 대부분의 임베딩 모델은 512~8192 토큰이므로, 긴 문서는 섹션별로 나누어 Late Chunking을 적용해야 합니다. Jina의 jina-embeddings-v3는 8192 토큰까지 지원합니다.
{% endhint %}

---

## 청크 크기 최적화: 경험적 실험 방법

"최적 청크 크기"는 문서 유형과 질의 패턴에 따라 다릅니다. **데이터 기반으로** 최적값을 찾아야 합니다.

### RAGAS 메트릭으로 청크 크기 비교

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 평가 데이터셋 (질문, 정답, 원본 문서)
eval_dataset = [...]  # 50~100개의 Q&A 쌍

chunk_sizes = [100, 200, 500, 1000, 2000]
results = {}

for size in chunk_sizes:
    # 1. 청킹
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size, chunk_overlap=int(size * 0.2)
    )
    chunks = splitter.split_documents(documents)

    # 2. 임베딩 + 벡터 저장
    vectorstore = create_vectorstore(chunks)

    # 3. RAG 파이프라인으로 답변 생성
    answers = [rag_pipeline(q, vectorstore) for q in eval_dataset]

    # 4. RAGAS 평가
    score = evaluate(
        dataset=answers,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    )
    results[size] = score

# 5. 결과 비교
for size, score in results.items():
    print(f"Chunk {size}: Faithfulness={score['faithfulness']:.3f}, "
          f"Recall={score['context_recall']:.3f}, "
          f"Precision={score['context_precision']:.3f}")
```

### 청크 크기별 특성

| 청크 크기 | Context Precision | Context Recall | Faithfulness | 비고 |
|----------|------------------|---------------|-------------|------|
| **100 토큰** | 높음 | 낮음 | 중간 | 정보 단편화. 맥락 부족 |
| **200 토큰** | 높음 | 중간 | 중간~높음 | 사실 기반 Q&A에 적합 |
| **500 토큰** | 중간 | 높음 | 높음 | **대부분의 경우 최적** |
| **1000 토큰** | 중간 | 높음 | 높음 | 긴 설명이 필요한 문서에 적합 |
| **2000 토큰** | 낮음 | 높음 | 중간 | 노이즈 증가. LLM이 핵심을 놓칠 수 있음 |

{% hint style="info" %}
**경험적 가이드**: 특별한 이유가 없다면 **500 토큰 + 20% 오버랩** 으로 시작하세요. 이후 RAGAS 메트릭 기반으로 미세 조정합니다.
{% endhint %}

---

## 문서 유형별 청킹 전략

### 테이블 (표 구조 보존)

표를 단순 텍스트로 변환하면 구조 정보가 손실됩니다. **표 전체를 하나의 청크로** 유지하는 것이 핵심입니다.

```python
# Databricks ai_parse_document로 표 추출
# SQL에서 직접 사용 가능
"""
SELECT ai_parse_document(
  content,
  'tables'  -- 표 구조를 별도로 추출
) AS parsed
FROM raw_documents
"""
```

| 전략 | 설명 |
|------|------|
| **표 전체를 하나의 청크** | 행/열 구조를 마크다운 테이블 형식으로 보존 |
| **표 + 캡션 결합** | "표 3: 2024년 분기별 매출" + 표 내용을 하나의 청크로 |
| **셀 단위 분할** | 비추천. 구조 정보 완전 손실 |

### 코드 (함수/클래스 단위)

```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

# Python 코드 전용 스플리터
code_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=100,
)
# 함수, 클래스 경계를 인식하여 분할
```

### PDF (레이아웃 인식)

```python
# Databricks ai_parse_document를 활용한 PDF 레이아웃 인식 파싱
# 헤더, 본문, 표, 이미지 캡션을 구조적으로 분리

"""
SELECT ai_parse_document(
  pdf_content,
  'layout'  -- 레이아웃 인식 모드
) AS parsed
FROM pdf_documents
"""
# 결과: 헤더별 섹션, 표, 이미지 설명이 구조화된 형태로 추출
```

---

## 오버랩(Overlap) 전략

### 왜 오버랩이 중요한가?

청크 경계에서 **문맥이 단절** 되면, 해당 경계에 걸친 정보는 검색할 수 없게 됩니다.

```
오버랩 없음 (chunk_overlap=0):
  [Unity Catalog는 3단계 네임스페이스를] | [제공한다. catalog.schema.table 형식이다.]
  → "Unity Catalog의 네임스페이스 형식은?" 검색 시,
    청크1은 "형식"이 없고, 청크2는 "Unity Catalog"가 없어 매칭 실패

오버랩 있음 (chunk_overlap=20%):
  [Unity Catalog는 3단계 네임스페이스를 제공한다.]
                           [네임스페이스를 제공한다. catalog.schema.table 형식이다.]
  → 오버랩 구간에 핵심 정보 보존 → 검색 성공
```

### 권장 오버랩 비율

| 오버랩 비율 | 저장 용량 증가 | 검색 정확도 | 권장 상황 |
|-----------|-------------|-----------|----------|
| **0%** | 없음 | 낮음 | 비추천 |
| **10%** | ~10% | 중간 | 비용 절약이 중요할 때 |
| **20%** | ~20% | 높음 | **기본 권장값** |
| **30%+** | ~30%+ | 높음 (수확 체감) | 중요 문서에만 선택적 |

---

## 청킹 품질 평가: Retrieval Recall@K

청킹 전략이 좋은지 나쁜지는 **검색 품질** 로 측정합니다. 가장 직관적인 메트릭은 **Retrieval Recall@K** 입니다.

### 정의

```
Retrieval Recall@K = (상위 K개 검색 결과에 정답 청크가 포함된 비율)
```

### 측정 방법

```python
def evaluate_chunking_recall(questions, ground_truth_chunks, vectorstore, k=5):
    """청킹 전략의 Retrieval Recall@K 측정"""
    hits = 0
    for question, gt_chunk in zip(questions, ground_truth_chunks):
        results = vectorstore.similarity_search(question, k=k)
        retrieved_texts = [r.page_content for r in results]

        # ground truth 청크가 검색 결과에 포함되었는가?
        if any(gt_chunk in text for text in retrieved_texts):
            hits += 1

    recall = hits / len(questions)
    return recall

# 청킹 전략별 비교
for strategy_name, vectorstore in strategies.items():
    recall = evaluate_chunking_recall(questions, gt_chunks, vectorstore, k=5)
    print(f"{strategy_name}: Recall@5 = {recall:.3f}")

# 예시 결과:
# Fixed(500):     Recall@5 = 0.72
# Recursive(500): Recall@5 = 0.81
# Semantic:       Recall@5 = 0.85
# Parent-Child:   Recall@5 = 0.88
# Proposition:    Recall@5 = 0.91
```

{% hint style="info" %}
**실무 팁**: Recall@5 기준으로 **0.85 이상** 이면 양호한 청킹입니다. 0.80 미만이면 청킹 전략을 재검토하세요. 평가 데이터셋은 최소 **50~100개의 Q&A 쌍** 이 필요합니다.
{% endhint %}
