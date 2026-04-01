# 한국어 RAG 최적화

한국어는 영어와 매우 다른 언어 구조를 가지고 있어, RAG 파이프라인의 각 단계에서 특별한 고려가 필요합니다. 이 가이드에서는 한국어 RAG 시스템의 품질을 높이기 위한 실전 기법을 다룹니다.

## 1. 한국어 RAG의 과제

### 토큰화 문제

한국어는 **교착어(膠着語)** 로, 어근에 조사·어미가 결합하여 단어를 형성합니다:

```
"데이터브릭스에서" → "데이터브릭스" + "에서"
"구축했습니다"     → "구축" + "했" + "습니다"
```

일반 토크나이저(tiktoken, SentencePiece 등)로 한국어를 처리하면:

- **토큰 수가 영어 대비 2~3배 증가**(비용 및 컨텍스트 길이 문제)
- 의미 단위가 아닌 바이트/서브워드 단위로 분절
- BM25 등 키워드 검색에서 ** 조사 때문에 동일 단어가 다르게 인식**됨

```
"데이터브릭스에서" ≠ "데이터브릭스를" ≠ "데이터브릭스의"
→ 모두 "데이터브릭스"를 포함하지만, 공백 기반 토크나이저로는 다른 단어로 처리
```

{% hint style="warning" %}
한국어 RAG에서 가장 흔한 실수는 영어 기준 파이프라인을 그대로 적용하는 것입니다. 특히 BM25 기반 키워드 검색은 형태소 분석 없이는 한국어에서 제대로 작동하지 않습니다.
{% endhint %}

## 2. Kiwi 한국어 형태소 분석기

### Kiwi란?

**Kiwi** 는 C++ 기반의 고속 한국어 형태소 분석기입니다. 정확도와 속도 모두 뛰어나며, Python 바인딩(`kiwipiepy`)을 통해 쉽게 사용할 수 있습니다.

### 설치

```bash
pip install kiwipiepy
```

### 기본 사용법

```python
from kiwipiepy import Kiwi

kiwi = Kiwi()

# 형태소 분석
result = kiwi.tokenize("Databricks에서 RAG 파이프라인을 구축합니다")
for token in result:
    print(f"{token.form}\t{token.tag}\t{token.start}-{token.end}")
# Databricks  NNP    0-11
# 에서         JKB    11-13
# RAG          SL     14-17
# 파이프라인    NNG    18-23
# 을           JKO    23-24
# 구축         NNG    25-27
# 합니다       XSV+EF 27-30
```

### 주요 품사 태그

| 태그 | 의미 | 예시 |
|------|------|------|
| **NNG** | 일반명사 | 파이프라인, 구축, 데이터 |
| **NNP** | 고유명사 | Databricks, Unity Catalog |
| **VV** | 동사 | 구축하다, 배포하다 |
| **VA** | 형용사 | 빠르다, 정확하다 |
| **SL** | 외국어 | RAG, LLM, API |
| **JK\*** | 조사 | 에서, 을, 의 |
| **E\*** | 어미 | 합니다, 했습니다 |

## 3. Kiwi 기반 BM25 Retriever

기본 BM25는 공백 기반으로 텍스트를 분절하므로, 한국어에서는 조사가 붙은 채로 토큰화됩니다. Kiwi로 형태소 분석 후 ** 명사/동사/외국어만 추출**하면 검색 품질이 크게 향상됩니다.

```python
from kiwipiepy import Kiwi
from langchain_community.retrievers import BM25Retriever

kiwi = Kiwi()

def kiwi_tokenize(text: str) -> list[str]:
    """Kiwi 형태소 분석기로 명사/동사/형용사/외국어만 추출"""
    tokens = kiwi.tokenize(text)
    # NNG(일반명사), NNP(고유명사), VV(동사), VA(형용사), SL(외국어)
    return [t.form for t in tokens if t.tag in ('NNG', 'NNP', 'VV', 'VA', 'SL')]

# Kiwi 토크나이저를 사용하는 BM25 Retriever
bm25_retriever = BM25Retriever.from_documents(
    documents,
    preprocess_func=kiwi_tokenize,
    k=5
)

# "데이터브릭스에서 RAG를 구축하는 방법" →
# kiwi_tokenize → ["데이터브릭스", "RAG", "구축", "방법"]
results = bm25_retriever.invoke("데이터브릭스에서 RAG를 구축하는 방법")
```

### Kiwi + Ensemble Retriever

한국어 RAG에서 가장 효과적인 조합은 **Kiwi BM25 + Dense (Vector Search)** 앙상블입니다:

```python
from langchain.retrievers import EnsembleRetriever
from langchain_databricks import DatabricksVectorSearch

# Kiwi 기반 BM25
bm25_retriever = BM25Retriever.from_documents(
    documents, preprocess_func=kiwi_tokenize, k=5
)

# Databricks Vector Search (다국어 임베딩)
vs_retriever = DatabricksVectorSearch(
    endpoint="vs-endpoint",
    index_name="catalog.schema.ko_docs_index",
    columns=["content", "source"]
).as_retriever(search_kwargs={"k": 5})

# 앙상블
ensemble = EnsembleRetriever(
    retrievers=[bm25_retriever, vs_retriever],
    weights=[0.4, 0.6]
)
```

{% hint style="tip" %}
한국어 전문 용어가 많은 도메인(법률, 의료 등)에서는 BM25 가중치를 `0.5~0.6`으로 높이면 정확한 용어 매칭이 강화됩니다.
{% endhint %}

## 4. 한국어 청킹 전략

| 전략 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **문장 기반 (KSS)** | 한국어 문장 경계 인식 | 자연스러운 분절 | 문장이 짧으면 청크가 너무 작음 |
| ** 형태소 기반** | Kiwi로 의미 단위 분절 | 정확한 의미 보존 | 구현 복잡 |
| **Semantic 청킹** | 임베딩 유사도 기반 경계 결정 | 의미 전환점 자동 감지 | 연산 비용 높음 |
| **Recursive + 한국어 구분자** | 한국어 종결어미 기반 분절 | 범용적, 구현 간단 | 구분자 설계 필요 |

### KSS (Korean Sentence Splitter) 활용

```python
# 설치: pip install kss
import kss

text = """Databricks는 데이터와 AI를 위한 통합 플랫폼입니다.
Delta Lake를 기반으로 데이터 레이크하우스 아키텍처를 제공합니다.
Unity Catalog로 데이터 거버넌스를 통합 관리할 수 있습니다."""

sentences = kss.split_sentences(text)
for s in sentences:
    print(s)
# Databricks는 데이터와 AI를 위한 통합 플랫폼입니다.
# Delta Lake를 기반으로 데이터 레이크하우스 아키텍처를 제공합니다.
# Unity Catalog로 데이터 거버넌스를 통합 관리할 수 있습니다.
```

### RecursiveCharacterTextSplitter + 한국어 구분자

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

korean_splitter = RecursiveCharacterTextSplitter(
    separators=[
        "\n\n",    # 문단 구분
        "\n",      # 줄바꿈
        "다. ",    # 평서문 종결
        "요. ",    # 존댓말 종결
        "까? ",    # 의문문 종결
        ". ",      # 일반 마침표
        " ",       # 공백
    ],
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)

chunks = korean_splitter.split_text(long_korean_text)
```

{% hint style="info" %}
한국어에서 `RecursiveCharacterTextSplitter`를 사용할 때는 종결어미(`다. `, `요. `)를 구분자에 추가하면 문장 중간에서 잘리는 것을 방지할 수 있습니다.
{% endhint %}

## 5. 한국어 임베딩 모델 비교

| 모델 | 차원 | 한국어 성능 | Databricks 지원 | 비고 |
|------|------|------------|----------------|------|
| **multilingual-e5-large-instruct** | 1024 | 우수 | Foundation Model API | 다국어, Databricks 기본 제공 |
| **bge-m3**(BAAI) | 1024 | 우수 | Model Serving 배포 | Dense + Sparse 하이브리드 지원 |
| **KoSimCSE**(SKT) | 768 | 매우 우수 | Model Serving 배포 | 한국어 특화, STS 벤치마크 상위 |
| **gte-multilingual-base**(Alibaba) | 768 | 우수 | Model Serving 배포 | 경량, 빠른 추론 속도 |

### Databricks Foundation Model API 활용

```python
from langchain_databricks import DatabricksEmbeddings

# Databricks에서 기본 제공하는 다국어 임베딩
embeddings = DatabricksEmbeddings(
    endpoint="databricks-gte-large-en"  # 또는 커스텀 배포 엔드포인트
)

# 한국어 텍스트 임베딩
vectors = embeddings.embed_documents([
    "Databricks에서 RAG 파이프라인을 구축합니다",
    "데이터 레이크하우스 아키텍처 개요"
])
```

{% hint style="tip" %}
한국어 전용 임베딩 모델(KoSimCSE 등)은 한국어 내부 유사도 측정에서는 뛰어나지만, 한영 혼용 문서가 많은 환경에서는 다국어 모델(`multilingual-e5-large-instruct`, `bge-m3`)이 더 적합합니다.
{% endhint %}

## 6. 한국어 RAG 베스트 프랙티스

### 권장 구성

| 단계 | 권장 도구/전략 | 이유 |
|------|--------------|------|
| ** 토크나이저** | Kiwi + KSS 조합 | 형태소 분석 + 문장 분리 |
| ** 청킹** | Recursive + 한국어 구분자 | 종결어미 기반 자연스러운 분절 |
| ** 임베딩** | multilingual-e5-large-instruct | Databricks 기본 제공, 한영 혼용 지원 |
| ** 검색** | Hybrid (Kiwi BM25 + Vector) | 키워드 + 의미 검색 결합 |
| ** 재정렬** | bge-reranker-v2-m3 | 다국어 Reranker, 한국어 지원 |

### 한국어 특화 전처리

```python
import re
from kiwipiepy import Kiwi

kiwi = Kiwi()

def preprocess_korean(text: str) -> str:
    """한국어 RAG를 위한 텍스트 전처리"""
    # 1. 불필요한 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()

    # 2. 특수문자 정리 (문장부호는 유지)
    text = re.sub(r'[^\w\s가-힣a-zA-Z0-9.,!?·\-()]', '', text)

    # 3. 한자 → 한글 변환 (Kiwi 내장 기능)
    # Kiwi는 분석 시 자동으로 한자를 한글로 매핑

    return text
```

### 평가 시 주의사항

- ** 한국어 평가 데이터셋을 직접 구축**해야 합니다. 영어 벤치마크 결과가 한국어 성능을 보장하지 않습니다.
- 평가 지표: Retrieval에는 **Recall@K**, **MRR**, 생성에는 ** 정확성**, ** 근거 충실도**를 측정합니다.
- MLflow Evaluate를 활용한 평가 방법은 [RAG 평가](evaluation.md) 가이드를 참조하세요.

{% hint style="warning" %}
한국어 RAG 시스템을 평가할 때, LLM-as-Judge를 사용한다면 평가 프롬프트도 한국어로 작성하거나, 한국어 이해도가 높은 모델(Claude, GPT-4 등)을 Judge로 사용해야 합니다.
{% endhint %}

## 참고 문서

- [Kiwi (kiwipiepy) 공식 문서](https://bab2min.github.io/kiwipiepy/)
- [KSS (Korean Sentence Splitter) GitHub](https://github.com/hyunwoongko/kss)
- [Databricks Foundation Model API](https://docs.databricks.com/aws/en/machine-learning/foundation-models/index.html)
- [LangChain Text Splitters 문서](https://python.langchain.com/docs/how_to/#text-splitters)
- [BGE-M3 (BAAI) HuggingFace](https://huggingface.co/BAAI/bge-m3)
- [KoSimCSE (SKT) HuggingFace](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
