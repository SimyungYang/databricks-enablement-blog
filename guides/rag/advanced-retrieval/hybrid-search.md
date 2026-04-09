# 하이브리드 검색

## 한국어 하이브리드 검색의 도전

### Databricks Vector Search의 한국어 제약

Databricks Vector Search의 **Full Text Search (Beta)** 기능은 현재 **Standard(영어) 분석기** 만 지원합니다. 이는 한국어 환경에서 심각한 검색 품질 저하를 초래합니다.

### 한국어 형태소 분석의 중요성

한국어는 **교착어** 로, 어근에 조사/어미가 결합되어 하나의 어절을 형성합니다. 형태소 분석 없이는 올바른 키워드 검색이 불가능합니다.

아래 예시를 통해 Standard 분석기와 한국어 형태소 분석기(Nori)의 차이를 비교합니다.

| 입력 텍스트 | Standard 분석기 | Nori 분석기 |
|-----------|---------------|------------|
| "동해물과 백두산이" | `["동해물과", "백두산이"]` (2토큰) | `["동해", "물", "과", "백두", "산", "이"]` (6토큰) |
| "마르고 닳도록" | `["마르고", "닳도록"]` (2토큰) | `["마르", "고", "닳", "도록"]` (4토큰) |

**검색 실패 시나리오:**

1. 사용자가 **"동해"** 로 검색
2. Standard 인덱스에는 `"동해물과"` 라는 토큰만 존재
3. `"동해"` != `"동해물과"` → **매칭 실패**
4. Nori 인덱스에는 `"동해"` 토큰이 별도로 존재 → **매칭 성공**

{% hint style="warning" %}
**Standard 분석기의 한국어 처리 문제**: Standard 분석기는 공백과 구두점 기반으로만 토큰을 분리합니다. 한국어의 조사(`이/가/을/를/에서`), 어미(`~하다/~한/~했던`) 등을 분리하지 못하므로, 형태소 단위 검색이 사실상 불가능합니다.
{% endhint %}

### 오픈소스 한국어 형태소 분석기 비교

한국어 하이브리드 검색을 구현하려면 적절한 형태소 분석기를 선택해야 합니다. 아래 표는 주요 오픈소스 분석기를 비교합니다.

| 분석기 | 개발 언어 | 속도 | 정확도 | 특징 | 추천 용도 |
|-------|---------|------|-------|------|---------|
| **Mecab-ko** | C++ | 매우 빠름 | 보통~높음 | 일본어 Mecab 포팅. CRF 기반. 설치가 까다로움 (C++ 빌드 필요) | 대용량 빠른 처리, 서버 환경 |
| **Kiwi** | C++ | 빠름 | 높음 | 최근 가장 활발한 개발. 띄어쓰기/오탈자 자동 교정. `pip install kiwipiepy`로 간편 설치 | **RAG 추천**. 신조어 많은 데이터, Databricks 환경 |
| **Okt (Open Korean Text)** | Scala/Java | 빠름 | 보통 | 트위터(X) 한국어 분석기 기반. 비표준어/신조어에 강함 | SNS, 구어체, 채팅 데이터 |
| **Komoran** | Java | 보통 | 보통 | 순수 자바 구현. 외부 의존성 없음 | Java 기반 시스템 |
| **Hannanum** | Java | 느림 | 높음 | KAIST 개발. 학술적으로 정확 | 학술 연구, 정확성 우선 |

{% hint style="info" %}
**Databricks 환경에서의 추천**: **Kiwi** 를 권장합니다. `pip install kiwipiepy`만으로 설치가 완료되고, C++ 바인딩으로 속도가 빠르며, 띄어쓰기 오류와 오탈자를 자동 교정하는 기능이 있어 실무 데이터에 강합니다.
{% endhint %}

### Kiwi 형태소 분석기 활용 예제

```python
from kiwipiepy import Kiwi

kiwi = Kiwi()

# 기본 형태소 분석
text = "Databricks에서 Unity Catalog 권한을 설정하는 방법"
tokens = kiwi.tokenize(text)
for token in tokens:
    print(f"{token.form}\t{token.tag}\t{token.start}~{token.end}")

# 출력:
# Databricks  SL   0~10
# 에서         JKB  10~12
# Unity       SL   13~18
# Catalog     SL   19~26
# 권한         NNG  27~29
# 을          JKO  29~30
# 설정         NNG  31~33
# 하           XSV  33~34
# 는          ETM  34~35
# 방법         NNG  36~38

# BM25용 토크나이저 함수
def kiwi_tokenizer(text: str) -> list[str]:
    """Kiwi 기반 한국어 토크나이저 - BM25 Retriever에 사용"""
    tokens = kiwi.tokenize(text)
    # 명사(NNG, NNP), 동사 어근(VV), 형용사 어근(VA), 외국어(SL) 추출
    meaningful_tags = {"NNG", "NNP", "NNB", "VV", "VA", "SL", "SN"}
    return [t.form for t in tokens if t.tag in meaningful_tags]

# 테스트
print(kiwi_tokenizer("Databricks에서 Unity Catalog 권한을 설정하는 방법"))
# ['Databricks', 'Unity', 'Catalog', '권한', '설정', '하', '방법']
```

---

## Retriever 유형 비교

| Retriever | 방식 | 장점 | 단점 | 적합 시나리오 |
|-----------|------|------|------|--------------|
| **Dense Retriever** | 벡터 유사도 검색 (임베딩) | 의미적 유사성 포착, 동의어 처리 | 정확한 키워드 매칭 약함 | 일반 Q&A, 자연어 질의 |
| **Sparse Retriever**(BM25/TF-IDF) | 키워드 빈도 기반 검색 | 정확한 용어 매칭, 빠른 속도 | 동의어·문맥 이해 불가 | 전문 용어, 코드 검색 |
| **Hybrid Retriever** | Dense + Sparse 결합 | 두 방식의 장점 통합 | 가중치 튜닝 필요 | 대부분의 프로덕션 환경 |
| **Multi-Query Retriever** | 하나의 질문을 여러 쿼리로 변환 | 검색 recall 향상 | LLM 호출 비용 추가 | 복잡한 질문, 모호한 질의 |
| **Parent Document Retriever** | 작은 청크로 검색, 큰 문서로 반환 | 검색 정밀도 + 풍부한 컨텍스트 | 인덱스 구조 복잡 | 긴 문서 기반 Q&A |
| **Self-Query Retriever** | 메타데이터 필터를 자동 추출 | 구조화된 필터링 가능 | LLM 의존, 메타데이터 설계 필요 | 날짜·카테고리 기반 필터링 |

{% hint style="info" %}
실무에서는 **Hybrid Retriever + Reranking** 조합이 가장 균형 잡힌 성능을 제공합니다. 단일 Retriever만으로는 다양한 쿼리 패턴을 커버하기 어렵습니다.
{% endhint %}

## 하이브리드 검색이 왜 순수 벡터 검색보다 나은가

순수 벡터 검색(Dense Retrieval)만으로는 모든 쿼리 패턴을 커버하기 어렵습니다. 구체적인 한계를 살펴봅시다.

### Dense Retrieval의 약점

| 쿼리 유형 | 예시 | Dense 검색 결과 | 문제 |
|-----------|------|----------------|------|
| **정확한 용어 매칭** | "에러 코드 DELTA_TABLE_NOT_FOUND" | 유사한 의미의 문서를 반환하지만 정확한 에러 코드 포함 문서를 놓침 | 임베딩은 의미를 압축하므로 특정 문자열 매칭에 약함 |
| **약어/코드명** | "DBSQL" 또는 "UC" | "Databricks SQL"이나 "Unity Catalog"과 연결하지 못할 수 있음 | 약어와 풀네임의 임베딩 거리가 멀 수 있음 |
| **숫자/버전 검색** | "DBR 15.4" | 다른 DBR 버전 문서를 반환 | 숫자의 미세한 차이를 구별하기 어려움 |
| **불용어 의존 쿼리** | "NOT" 조건 포함 질문 | 부정 의미를 무시하고 관련 문서를 반환 | 임베딩은 부정 표현을 잘 반영하지 못함 |

### Hybrid 검색이 해결하는 문제

하이브리드 검색은 **Dense (의미 이해) + Sparse (정확 매칭)** 을 결합하여 양쪽의 약점을 보완합니다:

- **Dense가 강한 경우**: "데이터 품질을 관리하는 방법" → 의미적으로 유사한 "데이터 거버넌스", "데이터 검증" 문서를 찾음
- **Sparse가 강한 경우**: "DELTA_TABLE_NOT_FOUND 해결법" → 정확히 해당 에러 코드가 포함된 문서를 찾음
- **둘 다 필요한 경우**: "Unity Catalog에서 외부 테이블 접근 권한 에러 수정" → 의미 검색 + 키워드 매칭 조합

### 하이브리드 검색 핵심 개념 3가지

하이브리드 검색을 제대로 구현하려면 **조합, 정규화, 가중치** 라는 3가지 핵심 개념을 반드시 이해해야 합니다.

#### 조합 (Combination)

두 가지 이상의 검색 결과를 하나로 합치는 방법입니다.

- **순위 기반 (Rank-based)**: 각 문서의 실제 점수를 무시하고, **"몇 등인가"** 만 봅니다. 대표적으로 **RRF (Reciprocal Rank Fusion)** 가 있습니다. RRF는 각 검색 시스템에서 문서가 받은 순위의 역수(1/순위)를 합산하여 최종 점수를 구합니다. 예를 들어 벡터 검색에서 2등, 키워드 검색에서 3등인 문서는 `1/2 + 1/3 = 0.83`의 점수를 받습니다. 점수가 아닌 순위만 사용하기 때문에, 서로 다른 스케일의 검색 시스템을 **정규화 없이** 통합할 수 있어 가장 안정적입니다. (자세한 수식과 계산 예시는 아래 [RRF 상세](#rrf-reciprocal-rank-fusion-상세) 섹션을 참조)
- **점수 기반 (Score-based)**: 각 검색 시스템의 실제 유사도 점수를 활용하여 가중 합산합니다. RRF보다 정밀할 수 있지만, 벡터 검색(0~1 범위)과 BM25(0~무한대 범위)처럼 점수 스케일이 다른 시스템을 합산하려면, **정규화(Normalization)** 로 스케일을 통일하는 작업이 반드시 선행되어야 합니다. 정규화 없이 합산하면 BM25 점수가 압도적으로 커서 벡터 검색 결과가 사실상 무시됩니다.

#### 정규화 (Normalization)

서로 다른 두 검색 시스템의 점수 스케일을 동일한 범위로 맞추는 작업입니다. 점수 기반 조합을 사용할 때 **필수적** 입니다.

- **벡터 검색 점수**: 코사인 유사도 기준 0.0 ~ 1.0 (비교적 좁은 범위)
- **BM25 점수**: 0.0 ~ 무한대 (문서 길이, 용어 빈도에 따라 크게 변동)
- 이 두 점수를 직접 비교하면, BM25 점수가 압도적으로 크므로 벡터 검색 결과가 사실상 무시됨

아래 표는 주요 정규화 방법을 비교합니다.

| 정규화 방법 | 수식 | 특징 |
|-----------|------|------|
| **Min-Max** | `(x - min) / (max - min)` | 가장 직관적. 0~1 범위로 변환. 이상치에 민감 |
| **L2 (유클리드)** | `x / sqrt(sum(x^2))` | 벡터 정규화에 적합. 크기 보존 |
| **Z-score** | `(x - mean) / std` | 평균 0, 표준편차 1로 변환. 분포 기반 |

#### 가중치 (Weight)

각 검색 기법의 **중요도(비중)** 를 비즈니스 요건에 맞게 조정합니다.

- **정확한 결과가 중요할 때**(에러 코드, 법령 번호 검색): 키워드 검색 가중치를 높게 (예: keyword 0.7, semantic 0.3)
- **다양한 표현을 지원할 때**(일반 Q&A, 자연어 질의): 시맨틱 검색 가중치를 높게 (예: keyword 0.3, semantic 0.7)
- **균형 잡힌 검색**: 동일 가중치 (keyword 0.5, semantic 0.5)

{% hint style="info" %}
가중치는 **고정값이 아닙니다.** 도메인과 쿼리 패턴에 따라 최적값이 달라지므로, 평가 데이터셋을 활용한 실험을 통해 튜닝해야 합니다.
{% endhint %}

### RRF (Reciprocal Rank Fusion) 상세

RRF는 하이브리드 검색에서 가장 널리 사용되는 결과 조합 알고리즘입니다. 핵심 수식은 다음과 같습니다.

```
Final_score(d) = Σ weight_i * (1 / (rank_i(d) + rank_constant))
```

- `rank_i(d)`: i번째 검색 시스템에서 문서 d의 순위 (1부터 시작)
- `rank_constant`: 상수 (기본값 60). 순위가 낮은 문서의 영향력을 조절
- `weight_i`: i번째 검색 시스템의 가중치

**RRF의 핵심 장점:**

- 점수의 절대값이 아니라 **순위** 만 사용하므로, 서로 다른 스케일의 검색 시스템을 **정규화 없이** 통합 가능
- Databricks Vector Search의 `query_type="hybrid"` 가 내부적으로 RRF를 사용
- 구현이 간단하고, 대부분의 경우 점수 기반 방법과 비슷하거나 더 나은 성능

**RRF 계산 예시:**

```
문서 A: 벡터 검색 1등, 키워드 검색 3등
  → 0.5 * (1/(1+60)) + 0.5 * (1/(3+60)) = 0.5 * 0.0164 + 0.5 * 0.0159 = 0.01615

문서 B: 벡터 검색 5등, 키워드 검색 1등
  → 0.5 * (1/(5+60)) + 0.5 * (1/(1+60)) = 0.5 * 0.0154 + 0.5 * 0.0164 = 0.01590

문서 C: 벡터 검색 2등, 키워드 검색 2등
  → 0.5 * (1/(2+60)) + 0.5 * (1/(2+60)) = 0.5 * 0.0161 + 0.5 * 0.0161 = 0.01613

최종 순위: A > C > B (양쪽에서 모두 높은 순위를 받은 문서가 유리)
```

## 앙상블 Retriever (Ensemble Retriever)

### 개념

앙상블 Retriever는 서로 다른 특성의 Retriever를 결합하여 각각의 약점을 보완합니다. 가장 일반적인 조합은 **BM25 (키워드) + Vector Search (의미)** 입니다.

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

LangChain의 **EnsembleRetriever** 는 여러 리트리버를 하나로 묶어 하이브리드 검색을 수행하며, 각 리트리버에 개별 가중치를 부여할 수 있습니다.

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

- Databricks VS의 "Hybrid Search"는 **Dense (임베딩 유사도) + 키워드 필터** 를 결합하는 방식이며, 전통적인 **BM25 Sparse Retrieval과는 다릅니다**
- 내장 키워드 검색은 **영어 기반 토크나이저** 를 사용하여, 한국어 형태소를 제대로 분리하지 못함
- 따라서 한국어 환경에서는 VS 내장 하이브리드보다 **외부 BM25 (Kiwi 기반) + VS Dense를 EnsembleRetriever로 결합** 하는 것이 더 효과적

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

---

## Databricks에서 한국어 하이브리드 검색 구현

### 솔루션 아키텍처: 9단계 워크플로

한국어 하이브리드 검색을 Databricks 환경에서 구현하기 위한 전체 파이프라인은 다음 9단계로 구성됩니다.

| 단계 | 작업 | 설명 | 도구/기술 |
|------|------|------|----------|
| **1** | PDF 파싱 + 청킹 | 원본 문서를 파싱하고 적절한 크기로 분할 | Unstructured, PyMuPDF, LangChain TextSplitter |
| **2** | 한국어 형태소 분석 | 오픈소스 분석기로 청크 텍스트를 형태소 단위로 분리 | **Kiwi (추천)**, Mecab-ko, Okt |
| **3** | 원본 텍스트 저장 | 원본 청크 텍스트를 `content_raw` 컬럼에 저장 | Delta Lake |
| **4** | 분석된 텍스트 저장 | 형태소 분석된 텍스트를 `content_analyzed` 컬럼에 저장 | Delta Lake |
| **5** | 벡터 임베딩 생성 | 원본 텍스트를 임베딩하여 `content_vector` 컬럼에 저장 | bge-m3, multilingual-e5 |
| **6** | 키워드 검색 실행 | 분석된 텍스트 컬럼 대상 Full Text Search (Custom Retriever) | BM25Retriever + Kiwi |
| **7** | 벡터 검색 실행 | 벡터 컬럼 대상 의미 검색 | Databricks Vector Search |
| **8** | 결과 조합 | RRF 기반 검색 결과 병합 | EnsembleRetriever |
| **9** | 최종 결과 반환 | 조합된 결과를 LLM에 전달 | LangChain Chain |

### Databricks Vector Search 한국어 설정

```python
from databricks.vector_search.client import VectorSearchClient

vsc = VectorSearchClient()

# 1. Vector Search 엔드포인트 생성
vsc.create_endpoint(name="korean-rag-endpoint", endpoint_type="STANDARD")

# 2. Delta Sync 인덱스 생성 (한국어 지원 설정)
index = vsc.create_delta_sync_index(
    endpoint_name="korean-rag-endpoint",
    index_name="catalog.schema.korean_docs_index",
    source_table_name="catalog.schema.korean_docs",
    primary_key="doc_id",
    pipeline_type="TRIGGERED",
    embedding_source_column="content_raw",        # 원본 텍스트로 임베딩
    embedding_model_endpoint_name="databricks-bge-large-en",  # 또는 bge-m3
    columns_to_sync=["content_raw", "content_analyzed", "source", "metadata"]
)
```

### 한국어 Custom BM25 Retriever 구현

```python
from kiwipiepy import Kiwi
from langchain_community.retrievers import BM25Retriever
from langchain.schema import Document

kiwi = Kiwi()

def kiwi_tokenizer(text: str) -> list[str]:
    """Kiwi 기반 한국어 토크나이저"""
    tokens = kiwi.tokenize(text)
    meaningful_tags = {"NNG", "NNP", "NNB", "VV", "VA", "SL", "SN"}
    return [t.form for t in tokens if t.tag in meaningful_tags]

# 문서 로드 (Delta Lake에서 읽어온 청크들)
documents = [
    Document(page_content=row["content_raw"], metadata={"source": row["source"]})
    for row in spark.table("catalog.schema.korean_docs").collect()
]

# Kiwi 토크나이저를 적용한 BM25 Retriever
bm25_retriever = BM25Retriever.from_documents(
    documents,
    preprocess_func=kiwi_tokenizer,  # 한국어 형태소 분석 적용
    k=10
)

# 벡터 검색 + BM25 앙상블
from langchain.retrievers import EnsembleRetriever
from langchain_databricks import DatabricksVectorSearch

vs_retriever = DatabricksVectorSearch(
    endpoint="korean-rag-endpoint",
    index_name="catalog.schema.korean_docs_index",
    columns=["content_raw", "source"]
).as_retriever(search_kwargs={"k": 10})

# 최종 앙상블 Retriever
korean_hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vs_retriever],
    weights=[0.4, 0.6]  # 도메인에 따라 조정
)
```

### Databricks Vector Search Hybrid Query 활용

Databricks Vector Search 자체의 hybrid 쿼리도 활용할 수 있습니다. 영어 콘텐츠가 혼합된 경우 유용합니다.

```python
# Databricks VS 내장 하이브리드 검색 (영어 콘텐츠에 적합)
results = index.similarity_search(
    query_text="How to set up Unity Catalog permissions",
    query_type="hybrid",    # Dense + Full Text Search 결합
    num_results=10,
    columns=["content_raw", "source"]
)

# Full Text Search만 사용 (키워드 검색만 필요한 경우)
results = index.similarity_search(
    query_text="DELTA_TABLE_NOT_FOUND",
    query_type="FULL_TEXT",  # 키워드 검색만
    num_results=10,
    columns=["content_raw", "source"]
)
```

{% hint style="info" %}
Databricks Vector Search 인덱스 생성 시 `default_language = "KOREAN"` 설정과, 데이터 싱크 시 `Language = ["KOREAN", "ENGLISH"]` 설정을 통해 한국어 지원을 활성화할 수 있습니다. 단, 현재 Beta 단계이므로 형태소 분석 품질은 외부 분석기(Kiwi)에 비해 제한적입니다.
{% endhint %}
