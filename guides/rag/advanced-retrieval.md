# 고급 Retrieval 전략

RAG 시스템의 성능은 ** 검색(Retrieval) 품질** 에 가장 크게 좌우됩니다. 이 가이드에서는 기본 Dense Retrieval을 넘어, 검색 기술의 진화 과정부터 한국어 하이브리드 검색, 고급 전처리/후처리 전략, 그리고 Databricks 환경에서의 프로덕션 구현 로드맵까지 포괄적으로 다룹니다.

---

## 검색의 진화: 키워드에서 대화형 검색까지

현대 RAG 시스템을 이해하려면 ** 검색 기술이 어떻게 진화해 왔는지** 를 먼저 파악해야 합니다. 검색은 단순한 키워드 매칭에서 시작하여 점점 더 지능적인 방향으로 발전해 왔습니다.

아래 표는 검색 기술의 5단계 진화 과정을 요약합니다.

| 단계 | 검색 유형 | 핵심 기술 | 대표 서비스 | 한계 |
|------|----------|----------|-----------|------|
| **1단계**| 키워드 검색 | TF-IDF, BM25, 역색인(Inverted Index) | 초기 Google, Elasticsearch | 동의어/문맥 이해 불가. "자동차" 검색 시 "차량" 문서 누락 |
| **2단계**| 개인화 검색 | 사용자 행동 로그, 클릭률, Collaborative Filtering | Google PageRank, Amazon | 콜드 스타트 문제. 새 사용자/콘텐츠에 취약 |
| **3단계**| 시맨틱 검색 | 벡터 임베딩, ANN(근사 최근접 이웃), BERT/Sentence-BERT | Pinecone, Weaviate, Databricks VS | 정확한 키워드 매칭 약함. 고유명사/코드/숫자 검색 실패 |
| **4단계**| 하이브리드 검색 | Dense + Sparse 결합, RRF, Re-ranking | Databricks VS Hybrid, Elasticsearch 8.x | 가중치 튜닝 필요. 다국어 토크나이저 문제 |
| **5단계**| 대화형 검색 | LLM + RAG, Query Rewrite, Agentic RAG, Tool Use | ChatGPT + Retrieval, Databricks Agent | 비용 높음. 환각(Hallucination) 위험 |

### 왜 키워드 검색이 여전히 필요한가 - "코끼리 식당" 문제

시맨틱(벡터) 검색이 아무리 발전해도 ** 키워드 검색을 완전히 대체할 수는 없습니다.** 그 이유를 "코끼리 식당"이라는 실제 상호명 검색 시나리오로 살펴봅시다.

** 벡터 검색의 한계:**

- 사용자가 "코끼리 식당"을 검색하면, 벡터 검색은 "코끼리"를 ** 동물** 로 이해합니다
- 결과: "동물원 근처 식당", "아프리카 테마 레스토랑" 같은 ** 의미적으로 유사하지만 전혀 다른 문서** 를 반환
- 임베딩 모델은 단어의 의미를 압축하므로, 고유명사의 ** 문자열 그 자체** 를 매칭하는 데 약함

** 키워드 검색의 강점:**

- BM25/TF-IDF 기반 검색은 "코끼리 식당"이라는 ** 정확한 문자열** 이 포함된 문서를 찾음
- 에러 코드(`DELTA_TABLE_NOT_FOUND`), 제품명(`DBR 15.4`), 법령 번호(`제42조`) 등 ** 정확 매칭이 필수** 인 경우에 탁월

{% hint style="info" %}
** 핵심 인사이트:** 벡터 검색은 "무엇을 의미하는가"를 이해하고, 키워드 검색은 "정확히 무엇이라고 쓰여 있는가"를 찾습니다. 프로덕션 RAG 시스템에서는 ** 둘 다 필요** 합니다.
{% endhint %}

### 생성형 AI와 검색의 상호 보완 관계

LLM과 검색은 서로의 약점을 보완하는 ** 공생 관계** 입니다.

**LLM이 검색에 제공하는 가치:**

- ** 문맥 파악 능력**: "사과"가 과일인지 사과(謝過)인지 대화 맥락에서 판단
- **Query Rewrite**: 모호한 질문을 검색에 최적화된 형태로 재작성
- ** 의도 분류**: 질문의 의도에 따라 적합한 데이터 소스로 라우팅

** 검색이 LLM에 제공하는 가치:**

- ** 최신 정보**: LLM의 학습 데이터 컷오프 이후 정보를 실시간으로 제공
- ** 사실 근거(Grounding)**: 환각을 줄이고, 출처를 명시할 수 있는 근거 문서 제공
- ** 도메인 지식**: 기업 내부 문서, 규정, 매뉴얼 등 LLM이 학습하지 못한 전문 지식 제공

---

## 한국어 하이브리드 검색의 도전

### Databricks Vector Search의 한국어 제약

Databricks Vector Search의 **Full Text Search (Beta)** 기능은 현재 **Standard(영어) 분석기** 만 지원합니다. 이는 한국어 환경에서 심각한 검색 품질 저하를 초래합니다.

### 한국어 형태소 분석의 중요성

한국어는 ** 교착어** 로, 어근에 조사/어미가 결합되어 하나의 어절을 형성합니다. 형태소 분석 없이는 올바른 키워드 검색이 불가능합니다.

아래 예시를 통해 Standard 분석기와 한국어 형태소 분석기(Nori)의 차이를 비교합니다.

| 입력 텍스트 | Standard 분석기 | Nori 분석기 |
|-----------|---------------|------------|
| "동해물과 백두산이" | `["동해물과", "백두산이"]` (2토큰) | `["동해", "물", "과", "백두", "산", "이"]` (6토큰) |
| "마르고 닳도록" | `["마르고", "닳도록"]` (2토큰) | `["마르", "고", "닳", "도록"]` (4토큰) |

** 검색 실패 시나리오:**

1. 사용자가 **"동해"** 로 검색
2. Standard 인덱스에는 `"동해물과"` 라는 토큰만 존재
3. `"동해"` != `"동해물과"` → ** 매칭 실패**
4. Nori 인덱스에는 `"동해"` 토큰이 별도로 존재 → ** 매칭 성공**

{% hint style="warning" %}
**Standard 분석기의 한국어 처리 문제**: Standard 분석기는 공백과 구두점 기반으로만 토큰을 분리합니다. 한국어의 조사(`이/가/을/를/에서`), 어미(`~하다/~한/~했던`) 등을 분리하지 못하므로, 형태소 단위 검색이 사실상 불가능합니다.
{% endhint %}

### 오픈소스 한국어 형태소 분석기 비교

한국어 하이브리드 검색을 구현하려면 적절한 형태소 분석기를 선택해야 합니다. 아래 표는 주요 오픈소스 분석기를 비교합니다.

| 분석기 | 개발 언어 | 속도 | 정확도 | 특징 | 추천 용도 |
|-------|---------|------|-------|------|---------|
| **Mecab-ko**| C++ | 매우 빠름 | 보통~높음 | 일본어 Mecab 포팅. CRF 기반. 설치가 까다로움 (C++ 빌드 필요) | 대용량 빠른 처리, 서버 환경 |
| **Kiwi**| C++ | 빠름 | 높음 | 최근 가장 활발한 개발. 띄어쓰기/오탈자 자동 교정. `pip install kiwipiepy`로 간편 설치 | **RAG 추천**. 신조어 많은 데이터, Databricks 환경 |
| **Okt (Open Korean Text)**| Scala/Java | 빠름 | 보통 | 트위터(X) 한국어 분석기 기반. 비표준어/신조어에 강함 | SNS, 구어체, 채팅 데이터 |
| **Komoran**| Java | 보통 | 보통 | 순수 자바 구현. 외부 의존성 없음 | Java 기반 시스템 |
| **Hannanum**| Java | 느림 | 높음 | KAIST 개발. 학술적으로 정확 | 학술 연구, 정확성 우선 |

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

## 1. Retriever 유형 비교

| Retriever | 방식 | 장점 | 단점 | 적합 시나리오 |
|-----------|------|------|------|--------------|
| **Dense Retriever**| 벡터 유사도 검색 (임베딩) | 의미적 유사성 포착, 동의어 처리 | 정확한 키워드 매칭 약함 | 일반 Q&A, 자연어 질의 |
| **Sparse Retriever**(BM25/TF-IDF) | 키워드 빈도 기반 검색 | 정확한 용어 매칭, 빠른 속도 | 동의어·문맥 이해 불가 | 전문 용어, 코드 검색 |
| **Hybrid Retriever**| Dense + Sparse 결합 | 두 방식의 장점 통합 | 가중치 튜닝 필요 | 대부분의 프로덕션 환경 |
| **Multi-Query Retriever**| 하나의 질문을 여러 쿼리로 변환 | 검색 recall 향상 | LLM 호출 비용 추가 | 복잡한 질문, 모호한 질의 |
| **Parent Document Retriever**| 작은 청크로 검색, 큰 문서로 반환 | 검색 정밀도 + 풍부한 컨텍스트 | 인덱스 구조 복잡 | 긴 문서 기반 Q&A |
| **Self-Query Retriever**| 메타데이터 필터를 자동 추출 | 구조화된 필터링 가능 | LLM 의존, 메타데이터 설계 필요 | 날짜·카테고리 기반 필터링 |

{% hint style="info" %}
실무에서는 **Hybrid Retriever + Reranking** 조합이 가장 균형 잡힌 성능을 제공합니다. 단일 Retriever만으로는 다양한 쿼리 패턴을 커버하기 어렵습니다.
{% endhint %}

## 2. 하이브리드 검색이 왜 순수 벡터 검색보다 나은가

순수 벡터 검색(Dense Retrieval)만으로는 모든 쿼리 패턴을 커버하기 어렵습니다. 구체적인 한계를 살펴봅시다.

### Dense Retrieval의 약점

| 쿼리 유형 | 예시 | Dense 검색 결과 | 문제 |
|-----------|------|----------------|------|
| ** 정확한 용어 매칭**| "에러 코드 DELTA_TABLE_NOT_FOUND" | 유사한 의미의 문서를 반환하지만 정확한 에러 코드 포함 문서를 놓침 | 임베딩은 의미를 압축하므로 특정 문자열 매칭에 약함 |
| ** 약어/코드명**| "DBSQL" 또는 "UC" | "Databricks SQL"이나 "Unity Catalog"과 연결하지 못할 수 있음 | 약어와 풀네임의 임베딩 거리가 멀 수 있음 |
| ** 숫자/버전 검색**| "DBR 15.4" | 다른 DBR 버전 문서를 반환 | 숫자의 미세한 차이를 구별하기 어려움 |
| ** 불용어 의존 쿼리**| "NOT" 조건 포함 질문 | 부정 의미를 무시하고 관련 문서를 반환 | 임베딩은 부정 표현을 잘 반영하지 못함 |

### Hybrid 검색이 해결하는 문제

하이브리드 검색은 **Dense (의미 이해) + Sparse (정확 매칭)** 을 결합하여 양쪽의 약점을 보완합니다:

- **Dense가 강한 경우**: "데이터 품질을 관리하는 방법" → 의미적으로 유사한 "데이터 거버넌스", "데이터 검증" 문서를 찾음
- **Sparse가 강한 경우**: "DELTA_TABLE_NOT_FOUND 해결법" → 정확히 해당 에러 코드가 포함된 문서를 찾음
- ** 둘 다 필요한 경우**: "Unity Catalog에서 외부 테이블 접근 권한 에러 수정" → 의미 검색 + 키워드 매칭 조합

### 하이브리드 검색 핵심 개념 3가지

하이브리드 검색을 제대로 구현하려면 ** 조합, 정규화, 가중치** 라는 3가지 핵심 개념을 반드시 이해해야 합니다.

#### 조합 (Combination)

두 가지 이상의 검색 결과를 하나로 합치는 방법입니다.

- ** 순위 기반 (Rank-based)**: 각 문서의 실제 점수를 무시하고, **"몇 등인가"** 만 봅니다. 대표적으로 **RRF (Reciprocal Rank Fusion)** 가 있습니다. 서로 다른 스케일의 검색 시스템을 통합할 때 가장 안정적입니다.
- ** 점수 기반 (Score-based)**: 각 검색 시스템의 실제 유사도 점수를 활용하여 가중 합산합니다. 더 정밀하지만, 점수 스케일을 맞추는 정규화 작업이 반드시 선행되어야 합니다.

#### 정규화 (Normalization)

서로 다른 두 검색 시스템의 점수 스케일을 동일한 범위로 맞추는 작업입니다. 점수 기반 조합을 사용할 때 ** 필수적** 입니다.

- ** 벡터 검색 점수**: 코사인 유사도 기준 0.0 ~ 1.0 (비교적 좁은 범위)
- **BM25 점수**: 0.0 ~ 무한대 (문서 길이, 용어 빈도에 따라 크게 변동)
- 이 두 점수를 직접 비교하면, BM25 점수가 압도적으로 크므로 벡터 검색 결과가 사실상 무시됨

아래 표는 주요 정규화 방법을 비교합니다.

| 정규화 방법 | 수식 | 특징 |
|-----------|------|------|
| **Min-Max**| `(x - min) / (max - min)` | 가장 직관적. 0~1 범위로 변환. 이상치에 민감 |
| **L2 (유클리드)**| `x / sqrt(sum(x^2))` | 벡터 정규화에 적합. 크기 보존 |
| **Z-score**| `(x - mean) / std` | 평균 0, 표준편차 1로 변환. 분포 기반 |

#### 가중치 (Weight)

각 검색 기법의 ** 중요도(비중)** 를 비즈니스 요건에 맞게 조정합니다.

- ** 정확한 결과가 중요할 때**(에러 코드, 법령 번호 검색): 키워드 검색 가중치를 높게 (예: keyword 0.7, semantic 0.3)
- ** 다양한 표현을 지원할 때**(일반 Q&A, 자연어 질의): 시맨틱 검색 가중치를 높게 (예: keyword 0.3, semantic 0.7)
- ** 균형 잡힌 검색**: 동일 가중치 (keyword 0.5, semantic 0.5)

{% hint style="info" %}
가중치는 ** 고정값이 아닙니다.** 도메인과 쿼리 패턴에 따라 최적값이 달라지므로, 평가 데이터셋을 활용한 실험을 통해 튜닝해야 합니다.
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

- 점수의 절대값이 아니라 ** 순위** 만 사용하므로, 서로 다른 스케일의 검색 시스템을 ** 정규화 없이** 통합 가능
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
- `weights=[0.7, 0.3]`: BM25 비중을 높이면 ** 정확한 키워드 매칭** 강화
- `weights=[0.3, 0.7]`: Vector Search 비중을 높이면 ** 의미적 유사성** 강화

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
- 내장 키워드 검색은 ** 영어 기반 토크나이저** 를 사용하여, 한국어 형태소를 제대로 분리하지 못함
- 따라서 한국어 환경에서는 VS 내장 하이브리드보다 ** 외부 BM25 (Kiwi 기반) + VS Dense를 EnsembleRetriever로 결합** 하는 것이 더 효과적

** 해결 전략:**
1. ** 소규모 문서 (10만건 이하)**: LangChain BM25Retriever (Kiwi 토크나이저) + VS Dense → EnsembleRetriever
2. ** 대규모 문서**: Elasticsearch/OpenSearch에 Kiwi 분석기 설정 → BM25 서빙 + VS Dense → EnsembleRetriever
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
| **1**| PDF 파싱 + 청킹 | 원본 문서를 파싱하고 적절한 크기로 분할 | Unstructured, PyMuPDF, LangChain TextSplitter |
| **2**| 한국어 형태소 분석 | 오픈소스 분석기로 청크 텍스트를 형태소 단위로 분리 | **Kiwi (추천)**, Mecab-ko, Okt |
| **3**| 원본 텍스트 저장 | 원본 청크 텍스트를 `content_raw` 컬럼에 저장 | Delta Lake |
| **4**| 분석된 텍스트 저장 | 형태소 분석된 텍스트를 `content_analyzed` 컬럼에 저장 | Delta Lake |
| **5**| 벡터 임베딩 생성 | 원본 텍스트를 임베딩하여 `content_vector` 컬럼에 저장 | bge-m3, multilingual-e5 |
| **6**| 키워드 검색 실행 | 분석된 텍스트 컬럼 대상 Full Text Search (Custom Retriever) | BM25Retriever + Kiwi |
| **7**| 벡터 검색 실행 | 벡터 컬럼 대상 의미 검색 | Databricks Vector Search |
| **8**| 결과 조합 | RRF 기반 검색 결과 병합 | EnsembleRetriever |
| **9**| 최종 결과 반환 | 조합된 결과를 LLM에 전달 | LangChain Chain |

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

---

## 청킹 전략 심층 비교

청킹(Chunking)은 RAG 파이프라인의 ** 첫 번째 관문** 으로, 검색 품질에 결정적인 영향을 미칩니다. 잘못된 청킹은 아무리 좋은 검색 알고리즘과 Re-ranking을 사용해도 보완할 수 없습니다.

아래 표는 주요 청킹 기법을 비교합니다.

| 청킹 기법 | 설명 | ML 모델 필요 | Databricks 지원 | 난이도 |
|---------|------|------------|--------------|------|
| ** 고정 크기 (Fixed-size)**| 토큰/글자 수 기준으로 기계적 분할. 간단하지만 문맥이 중간에서 끊길 위험 | N/A | ✅ | 낮음 |
| **Recursive**| 문단 → 문장 → 단어 순으로 재귀적 분할. ** 가장 표준적**. 문맥 보존율이 높음 | N/A | ✅ | 낮음 |
| ** 부모/자식 (Parent-Child)**| Parent(큰 단위)로 LLM에 전달하고, Child(작은 단위)로 검색. 환각 방지에 효과적 | N/A | ✅ | 중간 |
| ** 의미 기반 (Semantic)**| 문장별 임베딩 후 코사인 유사도가 크게 변하는 지점에서 분할 | Embedding | ✅ | 중간 |
| ** 명제 기반 (Proposition)**| LLM으로 각 문장을 "독립적 명제(self-contained proposition)"로 변환 후 분할. 정보 밀도 극대화 | LLM | ✅ | 높음 |

### 부모/자식 청킹 상세

부모/자식(Parent-Child) 청킹은 ** 검색 정확도와 문맥 풍부함** 이라는 두 가지 상충하는 요구사항을 동시에 해결하는 전략입니다.

** 핵심 원리:**

- **Child 청크**(작은 단위, 100~200 토큰): Vector Store에 저장되어 ** 검색** 에 사용. 작은 크기 덕분에 정보 밀도가 높아 검색 정확도가 높음
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

### 의미 기반 청킹 상세

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

## 3. Query Expansion (쿼리 확장)

사용자의 원래 쿼리를 확장하거나 변형하여 검색 recall을 높이는 기법입니다.

### HyDE (Hypothetical Document Embeddings)

LLM이 질문에 대한 ** 가상의 답변** 을 생성하고, 그 답변의 임베딩으로 검색합니다. 질문보다 답변이 실제 문서와 임베딩 공간에서 더 가까운 경향을 이용합니다.

```python
from langchain_databricks import ChatDatabricks

llm = ChatDatabricks(endpoint="databricks-meta-llama-3-3-70b-instruct")

def hyde_query_expansion(question: str) -> str:
    """HyDE: 가상의 답변을 생성하여 검색 쿼리로 사용"""
    prompt = f"""다음 질문에 대해 가상의 답변을 작성하세요.
실제 정확성은 중요하지 않으며, 관련 문서와 유사한 스타일과 용어를 사용하세요.

질문: {question}

가상의 답변:"""
    response = llm.invoke(prompt)
    return response.content

# "Delta Lake 최적화 방법" →
# "Delta Lake를 최적화하려면 Z-ORDER BY를 사용하여 데이터를 정렬하고,
#  OPTIMIZE 명령으로 작은 파일을 병합하며, AUTO COMPACTION을 활성화합니다..."
hypothetical_doc = hyde_query_expansion("Delta Lake 최적화 방법")
results = vs_retriever.invoke(hypothetical_doc)
```

### Step-back Prompting

구체적인 질문을 더 일반적인 질문으로 변환하여 검색합니다.

```python
def stepback_query(question: str) -> str:
    """구체적 질문을 일반적 질문으로 변환"""
    prompt = f"""다음 질문의 핵심 개념을 파악하고,
더 일반적인 형태의 질문으로 변환하세요.

원래 질문: {question}
일반화된 질문:"""
    response = llm.invoke(prompt)
    return response.content

# "DLT 파이프라인에서 SCD Type 2를 구현하는 방법" →
# "Delta Live Tables의 데이터 변환 패턴은?"
```

{% hint style="info" %}
Query Expansion은 검색 recall을 높이지만, LLM 호출 비용이 추가됩니다. Multi-Query, HyDE, Step-back 중 하나를 선택하여 적용하고, 평가를 통해 효과를 검증하세요.
{% endhint %}

---

## 전처리 기법 (Pre-Query Processing)

검색 쿼리가 Retriever에 도달하기 ** 전에** 수행하는 최적화 기법들입니다. 적절한 전처리는 검색 품질을 극적으로 향상시킬 수 있습니다.

아래 표는 주요 전처리 전략을 비교합니다.

| 전략 | 설명 | ML 모델 | Databricks 지원 |
|------|------|--------|--------------|
| ** 메타데이터 사전 필터링**| "2023년", "영업팀" 등 조건을 LLM으로 추출 후 벡터 검색 전에 필터 적용. 탐색 범위를 대폭 축소 | LLM | ✅ |
| **Query Rewrite**| 모호하거나 불완전한 질문을 검색에 최적화된 형태로 재작성. 대화 맥락 반영 | LLM | ✅ |
| **Contextual Retrieval**| Anthropic 제안. 각 청크에 전체 문서의 문맥 요약을 Prepend. 청킹 시 손실되는 정보를 보완 | LLM | ✅ |
| **Query Routing**| 질문의 의도를 분류하여 적합한 데이터 소스(SQL DB, 벡터 DB, 웹)로 라우팅 | LLM | ✅ |
| ** 다중 쿼리 분해**| 복잡한 질문을 여러 하위 질문으로 분해, 각각 검색 후 결과를 병합 | LLM | ✅ |

### 메타데이터 사전 필터링 (Self-Query)

```python
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain_databricks import ChatDatabricks

llm = ChatDatabricks(endpoint="databricks-claude-sonnet-4")

# 메타데이터 필드 정의
metadata_field_info = [
    AttributeInfo(name="year", description="문서 작성 연도", type="integer"),
    AttributeInfo(name="department", description="부서명 (영업팀, 개발팀, HR 등)", type="string"),
    AttributeInfo(name="doc_type", description="문서 유형 (정책, 매뉴얼, FAQ)", type="string"),
]

self_query_retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents="회사 내부 문서",
    metadata_field_info=metadata_field_info,
)

# "2024년 영업팀 정책 문서에서 출장 규정" →
#   필터: year=2024, department="영업팀", doc_type="정책"
#   쿼리: "출장 규정"
results = self_query_retriever.invoke("2024년 영업팀 정책 문서에서 출장 규정을 알려줘")
```

### Query Rewrite

```python
def rewrite_query(question: str, chat_history: list = None) -> str:
    """대화 맥락을 반영하여 검색 쿼리를 재작성"""
    history_context = ""
    if chat_history:
        history_context = "\n".join(
            [f"사용자: {h['user']}\n어시스턴트: {h['assistant']}" for h in chat_history[-3:]]
        )

    prompt = f"""다음 대화 기록과 최신 질문을 바탕으로,
검색에 최적화된 독립적인 쿼리를 작성하세요.
대명사("그것", "이전 것")를 구체적인 용어로 바꾸세요.

대화 기록:
{history_context}

최신 질문: {question}

검색 최적화 쿼리:"""
    response = llm.invoke(prompt)
    return response.content

# 대화 맥락:
#   사용자: "Unity Catalog란 뭐야?"
#   어시스턴트: "Unity Catalog는 Databricks의 통합 거버넌스 솔루션입니다..."
#   사용자: "그거 권한 설정은 어떻게 해?"
# → 재작성: "Unity Catalog 권한(ACL) 설정 방법"
```

### Contextual Retrieval (Anthropic 제안)

**Contextual Retrieval** 은 Anthropic이 제안한 기법으로, 각 청크에 ** 전체 문서의 맥락 요약** 을 앞에 붙여(prepend) 청킹 과정에서 손실되는 문맥 정보를 보완합니다.

```python
def add_context_to_chunk(chunk_text: str, full_document: str) -> str:
    """각 청크에 전체 문서 문맥을 Prepend"""
    prompt = f"""다음은 전체 문서에서 추출한 하나의 청크입니다.
이 청크가 전체 문서에서 어떤 맥락에 위치하는지 간결하게 설명하세요 (2~3문장).

전체 문서 (요약):
{full_document[:2000]}

청크:
{chunk_text}

문맥 설명:"""
    response = llm.invoke(prompt)
    context = response.content

    # 문맥 요약을 청크 앞에 추가
    return f"[문맥: {context}]\n\n{chunk_text}"

# 예시:
# 원본 청크: "GRANT SELECT ON TABLE TO user@email.com"
# 문맥 추가 후: "[문맥: 이 청크는 Unity Catalog의 권한 관리 섹션에서
#               테이블 수준 접근 권한을 부여하는 SQL 명령어를 설명합니다.]
#               GRANT SELECT ON TABLE TO user@email.com"
```

{% hint style="info" %}
Contextual Retrieval은 청킹 단계에서 ** 한 번만** 수행하면 되므로, 검색 시점에 추가 LLM 호출이 발생하지 않습니다. 초기 인덱싱 비용은 증가하지만, 검색 품질 향상 효과가 큽니다. Anthropic의 벤치마크에서 ** 검색 실패율을 49% 감소** 시킨 것으로 보고되었습니다.
{% endhint %}

### Query Routing

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_databricks import ChatDatabricks

llm = ChatDatabricks(endpoint="databricks-claude-sonnet-4")

def route_query(question: str) -> dict:
    """질문 의도를 분류하여 적합한 데이터 소스로 라우팅"""
    prompt = f"""다음 질문을 분석하여 가장 적합한 데이터 소스를 선택하세요.

데이터 소스 옵션:
- VECTOR_DB: 일반 문서, 매뉴얼, FAQ 검색
- SQL_DB: 수치 데이터, 통계, 집계 쿼리 (매출, 건수 등)
- WEB_SEARCH: 최신 뉴스, 외부 기술 문서
- GENIE: Databricks Genie를 통한 자연어 SQL 쿼리

질문: {question}

JSON 형식으로 응답:
{{"source": "데이터소스명", "reason": "이유"}}"""

    response = llm.invoke(prompt)
    return eval(response.content)

# "지난 분기 매출이 얼마야?" → {{"source": "SQL_DB", "reason": "수치 집계 쿼리"}}
# "Delta Lake 최적화 방법은?" → {{"source": "VECTOR_DB", "reason": "기술 문서 검색"}}
# "오늘 나온 Databricks 블로그 있어?" → {{"source": "WEB_SEARCH", "reason": "최신 정보"}}
```

### 다중 쿼리 분해 (Query Decomposition)

```python
def decompose_query(question: str) -> list[str]:
    """복잡한 질문을 여러 하위 질문으로 분해"""
    prompt = f"""다음 질문을 검색 가능한 2~4개의 하위 질문으로 분해하세요.
각 하위 질문은 독립적으로 검색 가능해야 합니다.

원래 질문: {question}

하위 질문들 (하나씩 줄바꿈):"""
    response = llm.invoke(prompt)
    return [q.strip() for q in response.content.strip().split("\n") if q.strip()]

# "Databricks에서 Unity Catalog를 설정하고 Delta Live Tables로
#  데이터 파이프라인을 구축한 후 ML 모델을 배포하는 방법" →
#   1. "Unity Catalog 초기 설정 방법"
#   2. "Delta Live Tables 파이프라인 구축 방법"
#   3. "Databricks에서 ML 모델 배포 방법"

sub_questions = decompose_query(complex_question)
all_results = []
for sq in sub_questions:
    results = ensemble_retriever.invoke(sq)
    all_results.extend(results)

# 중복 제거 후 LLM에 전달
unique_results = deduplicate(all_results)
```

---

## 4. Re-ranking

### 개념

Re-ranking은 초기 검색 결과를 **Cross-encoder** 모델로 재정렬하여 정밀도를 높이는 2단계 검색 전략입니다.

```
[쿼리] → Retriever (Top-K 후보) → Reranker (재정렬) → 최종 Top-N
```

- **1단계 (Retriever)**: 빠르게 후보군을 추출 (recall 중심, Top-20~50)
- **2단계 (Reranker)**: 후보군을 정밀하게 재정렬 (precision 중심, Top-3~5)

### Reranking 전략 심층 비교

아래 표는 주요 Reranking 전략을 비교합니다.

| 전략 | 설명 | ML 모델 | Databricks 지원 | 속도 | 정확도 |
|------|------|--------|--------------|------|-------|
| **Learning to Rank**| XGBoost/LightGBM으로 메타 피처(최신성, 인기도, 클릭률)를 결합하여 최종 순위 예측 | Classic ML | ✅ | 빠름 | 보통 |
| **Collaborative Filtering**| 사용자 과거 검색/선호 기반 개인 맞춤 재배치. Cold Start 문제 있음 | Classic ML | ✅ | 빠름 | 보통 |
| **Cross-Encoder**| 쿼리+문서를 함께 트랜스포머에 입력. ** 가장 정확하지만 느림**. BGE-Reranker, Cohere Rerank | Embedding | ✅ | 느림 | 높음 |
| **ColBERT (Late Interaction)**| 토큰 단위 벡터를 미리 계산하고, 쿼리 시 MaxSim 연산으로 비교. Cross-Encoder에 준하는 정확도 + 빠른 속도 | Embedding | ✅ | 빠름 | 높음 |
| **LLM 기반 (RankGPT)**| LLM이 직접 문서 목록을 읽고 순위를 정렬. 최고 수준의 문맥 이해. 비용이 가장 높음 | LLM | ✅ | 매우 느림 | 매우 높음 |

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

### ColBERT (Late Interaction) 활용

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

### LLM 기반 Reranking (RankGPT)

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
LLM 기반 Reranking은 문맥 이해가 가장 뛰어나지만, ** 비용과 지연 시간이 매우 높습니다**(문서당 수백~수천 토큰 소비). 고가치 쿼리나 배치 처리에만 사용하고, 실시간 서비스에는 Cross-Encoder나 ColBERT를 권장합니다.
{% endhint %}

### Re-ranking 전략 상세: 언제, 얼마나 Rerank할 것인가

Re-ranking의 효과를 극대화하려면 ** 초기 검색 범위** 와 ** 최종 반환 수** 를 적절히 설정해야 합니다.

| 설정 | 권장값 | 이유 |
|------|--------|------|
| ** 초기 검색 (Top-K)**| 20~50 | 너무 적으면 관련 문서를 놓치고, 너무 많으면 Reranker 비용 증가 |
| ** 최종 반환 (Top-N)**| 3~5 | LLM 컨텍스트 윈도우와 비용을 고려한 최적 범위 |
| **Reranker 모델**| bge-reranker-v2-m3 | 다국어 지원, 비용 효율적, Databricks에 배포 가능 |

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

---

## 후처리 기법 (Post-Processing)

검색 결과를 LLM에 전달한 ** 이후** 에 수행하는 품질 개선 기법들입니다. 환각(Hallucination)을 줄이고 답변의 신뢰성을 높이는 데 핵심적인 역할을 합니다.

아래 표는 주요 후처리 전략을 비교합니다.

| 전략 | 설명 | ML 모델 | Databricks 지원 | 환각 감소 효과 |
|------|------|--------|--------------|------------|
| **Self-RAG**| LLM이 스스로 검색 관련성, 답변 충실도, 질문 충족도를 평가하고 반복. 자기 교정 메커니즘 | LLM | ✅ | 높음 |
| **Corrective RAG (CRAG)**| 검색 결과를 "정확/모호/틀림"으로 분류. 틀리면 외부 웹 검색으로 보완 | LLM/Classic | ✅ | 높음 |
| **FLARE**| 생성 중 확신도가 낮은 부분에서 자동으로 추가 검색 수행. 긴 문서 작업에 효과적 | LLM | ✅ | 중간 |
| ** 출력 가드레일**| JSON 포맷 검증, 보안 가이드라인 위반 체크, 편향성/욕설 필터링 | Classic | ✅ | - |

### Self-RAG (자기 교정 RAG)

Self-RAG는 LLM이 ** 스스로 검색 결과의 관련성과 답변의 품질을 평가** 하고, 필요하면 재검색하는 반복적 자기 교정 프로세스입니다.

```python
def self_rag(question: str, retriever, llm, max_iterations: int = 3) -> str:
    """Self-RAG: 자기 교정 반복 검색-생성 파이프라인"""

    for iteration in range(max_iterations):
        # 1단계: 검색
        docs = retriever.invoke(question)
        context = "\n\n".join([d.page_content for d in docs])

        # 2단계: 관련성 평가
        relevance_prompt = f"""다음 검색 결과가 질문에 관련이 있는지 평가하세요.

질문: {question}
검색 결과: {context[:2000]}

평가 (RELEVANT / NOT_RELEVANT):"""
        relevance = llm.invoke(relevance_prompt).content.strip()

        if "NOT_RELEVANT" in relevance:
            # 검색 결과가 관련 없으면 쿼리를 재작성하여 재검색
            question = rewrite_query(question)
            continue

        # 3단계: 답변 생성
        answer_prompt = f"""다음 검색 결과를 바탕으로 질문에 답변하세요.
검색 결과에 없는 내용은 "정보가 부족합니다"라고 답하세요.

질문: {question}
검색 결과: {context}

답변:"""
        answer = llm.invoke(answer_prompt).content

        # 4단계: 충실도 평가 (답변이 검색 결과에 근거하는지)
        faithfulness_prompt = f"""답변이 검색 결과에 근거하는지 평가하세요.
검색 결과에 없는 정보가 답변에 포함되어 있으면 NOT_FAITHFUL입니다.

검색 결과: {context[:2000]}
답변: {answer}

평가 (FAITHFUL / NOT_FAITHFUL):"""
        faithfulness = llm.invoke(faithfulness_prompt).content.strip()

        if "FAITHFUL" in faithfulness and "NOT" not in faithfulness:
            return answer

    return "충분한 정보를 찾지 못했습니다. 질문을 더 구체적으로 바꿔주세요."
```

### Corrective RAG (CRAG)

Corrective RAG는 검색 결과를 **"정확/모호/틀림"**3단계로 분류하고, 결과가 부정확하면 ** 외부 웹 검색으로 보완** 하는 전략입니다.

```python
def corrective_rag(question: str, docs: list, llm) -> dict:
    """Corrective RAG: 검색 결과 품질에 따른 보정 전략"""

    # 1단계: 검색 결과 품질 분류
    grading_prompt = f"""다음 검색 결과가 질문에 대한 답변을 포함하는지 평가하세요.

질문: {question}
검색 결과: {docs[0].page_content[:1000] if docs else "없음"}

분류:
- CORRECT: 질문에 대한 정확한 답변을 포함
- AMBIGUOUS: 부분적으로 관련 있지만 불완전
- INCORRECT: 질문과 관련 없거나 잘못된 정보

분류 결과 (CORRECT/AMBIGUOUS/INCORRECT):"""

    grade = llm.invoke(grading_prompt).content.strip()

    if "CORRECT" in grade:
        # 검색 결과를 그대로 사용하여 답변 생성
        return {"strategy": "use_retrieval", "docs": docs}

    elif "AMBIGUOUS" in grade:
        # 검색 결과 + 웹 검색 결과를 결합
        web_results = web_search(question)  # 외부 웹 검색
        combined_docs = docs + web_results
        return {"strategy": "combine", "docs": combined_docs}

    else:  # INCORRECT
        # 검색 결과를 버리고 웹 검색으로 대체
        web_results = web_search(question)
        return {"strategy": "web_only", "docs": web_results}
```

### FLARE (Forward-Looking Active REtrieval)

FLARE는 LLM이 답변을 생성하는 ** 도중에** 확신도가 낮은 부분을 감지하고, 해당 부분에 대해 ** 추가 검색을 자동 수행** 하는 기법입니다. 특히 긴 문서를 생성할 때 효과적입니다.

```python
def flare_generate(question: str, retriever, llm) -> str:
    """FLARE: 생성 중 확신도 낮은 부분에서 추가 검색"""

    # 초기 검색 + 부분 답변 생성
    initial_docs = retriever.invoke(question)
    context = "\n".join([d.page_content for d in initial_docs])

    # 답변을 문장 단위로 생성하며 확신도 체크
    prompt = f"""질문: {question}
참고 자료: {context}

답변을 생성하되, 확신이 낮은 부분은 [LOW_CONFIDENCE: 추가 검색 쿼리] 형식으로 표시하세요.

답변:"""

    partial_answer = llm.invoke(prompt).content

    # [LOW_CONFIDENCE: ...] 부분이 있으면 추가 검색 수행
    import re
    low_conf_pattern = r'\[LOW_CONFIDENCE: (.+?)\]'
    matches = re.findall(low_conf_pattern, partial_answer)

    for match in matches:
        # 추가 검색 수행
        additional_docs = retriever.invoke(match)
        additional_context = additional_docs[0].page_content if additional_docs else ""

        # 확신도 낮은 부분을 추가 검색 결과로 교체
        replacement_prompt = f"""다음 정보를 바탕으로 한 문장으로 답변하세요:
{additional_context}

질문: {match}
답변:"""
        replacement = llm.invoke(replacement_prompt).content
        partial_answer = partial_answer.replace(f"[LOW_CONFIDENCE: {match}]", replacement)

    return partial_answer
```

### 출력 가드레일

```python
import json
import re

def apply_guardrails(answer: str, question: str) -> dict:
    """출력 가드레일: 답변 품질 및 안전성 검증"""

    checks = {
        "format_valid": True,
        "no_pii": True,
        "no_harmful_content": True,
        "has_source_citation": True,
    }

    # 1. PII (개인정보) 검출
    pii_patterns = [
        r'\d{3}-\d{2}-\d{5}',        # SSN
        r'\d{6}-[1-4]\d{6}',          # 주민등록번호
        r'[\w.-]+@[\w.-]+\.\w+',      # 이메일 (경고만)
    ]
    for pattern in pii_patterns:
        if re.search(pattern, answer):
            checks["no_pii"] = False
            answer = re.sub(pattern, "[개인정보 마스킹]", answer)

    # 2. 출처 인용 확인
    if "출처" not in answer and "참고" not in answer and "근거" not in answer:
        checks["has_source_citation"] = False
        answer += "\n\n*주의: 이 답변에 명시적 출처가 포함되지 않았습니다.*"

    return {"answer": answer, "checks": checks}
```

---

## 5. 적용 가이드

### 시나리오별 추천 전략

| 시나리오 | 추천 전략 | 이유 |
|----------|-----------|------|
| ** 일반 Q&A**| Dense + Reranking | 의미 검색으로 후보 추출 후 정밀 재정렬 |
| ** 전문 용어가 많은 문서**| Hybrid (BM25 + Dense) | 정확한 용어 매칭과 의미 검색을 동시에 |
| ** 한국어 문서**| Kiwi 토크나이저 + Hybrid | 형태소 분석 기반 BM25로 한국어 키워드 검색 강화 |
| ** 법률/의료 문서**| Self-Query + Metadata Filter | 날짜, 카테고리, 법령 번호 등 구조화된 필터링 |
| ** 긴 문서 기반 Q&A**| Parent Document Retriever | 작은 청크로 검색하되 큰 컨텍스트 반환 |
| ** 대규모 문서셋 (100K+)**| Vector Search + Reranking | 서버 사이드 검색으로 확장성 확보 |

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

## Databricks Advanced RAG 구현 로드맵

실무에서 Advanced RAG를 구현할 때는 ** 단계적 접근** 이 중요합니다. 한 번에 모든 기법을 적용하기보다, 기본부터 시작하여 점진적으로 고도화하는 것을 권장합니다.

### Phase 1: 기본 (Baseline)

** 목표**: 동작하는 RAG 파이프라인 구축

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

### Phase 2: 중급 (Enhanced)

** 목표**: 한국어 검색 품질 강화 + 정밀도 향상

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

### Phase 3: 고급 (Advanced)

** 목표**: 자기 교정 + 멀티 소스 + Agentic RAG

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
    return {**state, "route": route["source"]}

def retrieve(state: RAGState) -> RAGState:
    """라우팅된 소스에서 검색"""
    if state["route"] == "VECTOR_DB":
        docs = final_retriever.invoke(state["rewritten_query"])
    elif state["route"] == "SQL_DB":
        docs = sql_retriever.invoke(state["rewritten_query"])
    else:
        docs = web_retriever.invoke(state["rewritten_query"])
    return {**state, "documents": docs}

def grade_documents(state: RAGState) -> RAGState:
    """검색 결과 품질 평가 (CRAG)"""
    result = corrective_rag(state["question"], state["documents"], llm)
    return {**state, "grade": result["strategy"], "documents": result["docs"]}

def generate(state: RAGState) -> RAGState:
    """답변 생성 + 충실도 검증 (Self-RAG)"""
    answer = self_rag(state["question"], final_retriever, llm)
    return {**state, "answer": answer}

# LangGraph 워크플로 구성
workflow = StateGraph(RAGState)
workflow.add_node("rewrite", lambda s: {**s, "rewritten_query": rewrite_query(s["question"])})
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
** 로드맵 적용 팁**: 각 Phase를 넘어갈 때마다 반드시 ** 평가 메트릭** 을 비교하세요. Phase 2가 Phase 1보다 검색 정밀도(Precision@5)에서 최소 10% 이상 개선되지 않는다면, 기존 Phase의 튜닝(가중치, 청크 크기, 임베딩 모델)에 더 투자하는 것이 효율적입니다.
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
