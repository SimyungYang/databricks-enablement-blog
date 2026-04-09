# 한국어 RAG 최적화

한국어는 영어와 매우 다른 언어 구조를 가지고 있어, RAG 파이프라인의 각 단계에서 특별한 고려가 필요합니다. 이 가이드에서는 한국어 RAG 시스템의 품질을 높이기 위한 실전 기법을 다룹니다.

## 1. 한국어 RAG의 과제

### 한국어 RAG의 구조적 어려움

한국어 RAG는 영어 RAG와 근본적으로 다른 문제를 해결해야 합니다. 이는 한국어의 **언어학적 특성** 에서 비롯됩니다.

**1. 교착어 (Agglutinative Language) 특성**

한국어는 어근에 조사, 어미, 접사가 결합하여 하나의 단어를 형성합니다. 영어가 단어 순서(어순)로 문법적 관계를 표현하는 것과 달리, 한국어는 **접사의 결합** 으로 표현합니다. 이로 인해 동일한 의미의 단어가 수십 가지 형태로 변화합니다.

```
"데이터브릭스" (원형)
→ "데이터브릭스가" (주격), "데이터브릭스를" (목적격)
→ "데이터브릭스에서" (처소격), "데이터브릭스의" (관형격)
→ "데이터브릭스로" (도구격), "데이터브릭스와" (공동격)
→ 영어: "Databricks" 하나의 형태로 모든 문법적 관계 표현
```

**2. 띄어쓰기 불규칙성**

한국어는 띄어쓰기 규칙이 복잡하고, 실제 문서에서 띄어쓰기 오류가 빈번합니다. "데이터 분석"과 "데이터분석"이 혼재하는 경우가 많아, 공백 기반 토큰화에 의존하면 검색 품질이 저하됩니다.

**3. 한영 혼용 텍스트**

한국어 기술 문서에는 영어 용어가 빈번하게 등장합니다. "Databricks 워크스페이스에서 Delta Lake 테이블을 생성합니다"처럼 **한국어와 영어가 한 문장에 혼재** 합니다. 단일 언어 모델로는 양쪽 모두를 잘 처리하기 어렵습니다.

**4. 상대적으로 적은 학습 데이터**

대부분의 임베딩 모델과 LLM은 영어 데이터로 주로 학습됩니다. 한국어 데이터의 비중은 전체 학습 데이터의 1~3%에 불과한 경우가 많아, 한국어에 대한 **의미 표현 능력이 영어보다 떨어질 수 있습니다**.

### 이 문제들이 RAG에 미치는 실제 영향

위 특성들이 결합되면, 영어 기준으로 설계된 RAG 파이프라인은 한국어에서 심각한 성능 저하를 겪습니다:

- **BM25 키워드 검색 실패**: 조사가 붙은 채로 토큰화되어 "데이터브릭스에서" ≠ "데이터브릭스를"로 처리됨
- **토큰 비용 급증**: 일반 토크나이저(tiktoken, SentencePiece)로 한국어를 처리하면 영어 대비 **2~3배 많은 토큰** 소비
- **임베딩 품질 저하**: 한국어 학습 데이터 부족으로 의미 벡터의 정밀도가 떨어질 수 있음

이 문제들의 해결책은 다음 섹션에서 다루는 **형태소 분석** 에서 시작됩니다.

{% hint style="warning" %}
한국어 RAG에서 가장 흔한 실수는 영어 기준 파이프라인을 그대로 적용하는 것입니다. 특히 BM25 기반 키워드 검색은 형태소 분석 없이는 한국어에서 제대로 작동하지 않습니다.
{% endhint %}

## 2. Kiwi 한국어 형태소 분석기

### 형태소 분석이란? — 한국어 RAG의 핵심 전처리

**형태소(Morpheme)** 는 의미를 가진 최소 언어 단위입니다. 영어에서는 단어 사이의 공백(space)이 곧 의미 단위의 경계이지만, 한국어는 하나의 **어절(띄어쓰기 단위)** 안에 여러 형태소가 결합되어 있습니다. 형태소 분석은 이 어절을 의미 단위로 분해하는 작업입니다.

```
영어: "I   love   Databricks"   → 공백으로 나누면 3개 단어, 각각이 의미 단위
한국어: "데이터브릭스에서"         → 1개 어절이지만, 2개 형태소
       → "데이터브릭스" (고유명사, 의미 핵심) + "에서" (조사, 문법 기능)
```

**형태소 분석이 앞서 언급한 문제를 어떻게 해결하는가?**

섹션 1에서 설명한 교착어 특성 — "데이터브릭스에서", "데이터브릭스를", "데이터브릭스의"가 모두 다른 토큰으로 처리되는 문제 — 의 해결책이 바로 형태소 분석입니다. 핵심 아이디어는 간단합니다: **어절을 형태소로 분해한 뒤, 의미를 담당하는 형태소(명사, 동사 등)만 추출하고 문법 기능만 하는 형태소(조사, 어미)는 버리는 것** 입니다.

```
형태소 분석 + 의미 형태소 추출:
  "데이터브릭스에서" → [데이터브릭스, 에서] → "데이터브릭스" ✓
  "데이터브릭스를"   → [데이터브릭스, 를]   → "데이터브릭스" ✓
  "데이터브릭스의"   → [데이터브릭스, 의]   → "데이터브릭스" ✓
  → 조사가 달라도 동일한 검색 토큰으로 통일!
```

이 처리는 BM25 키워드 검색뿐 아니라 **하이브리드 검색** 전체의 품질을 높입니다. BM25 쪽의 품질이 떨어지면 앙상블 가중치를 아무리 조정해도 최종 검색 성능이 제한되기 때문입니다.

**형태소 분석의 동작 원리:**

형태소 분석기는 단순한 규칙 기반이 아닌 **확률 모델** 을 사용하여 어절을 분해합니다:

1. **사전 탐색**: 내장 사전에서 가능한 형태소 조합 후보를 탐색합니다. 예를 들어 "구축했습니다"는 "구축+했+습니다"로도, "구+축했+습니다"로도 분해할 수 있습니다.
2. **확률 모델 적용**: 여러 후보 중 **가장 자연스러운 조합** 을 통계적으로 선택합니다. 대규모 한국어 코퍼스에서 학습된 확률 분포를 기반으로, "구축+했+습니다"가 훨씬 자연스러운 분해임을 판단합니다.
3. **미등록어 처리**: 사전에 없는 신조어(예: "데이터브릭스", "레이크하우스")도 주변 문맥과 문자 패턴을 기반으로 품사를 추정합니다. 이 능력이 기술 문서 처리에서 특히 중요합니다.

다음은 실제 분석 과정의 예시입니다:

```
입력: "데이터브릭스에서 머신러닝 파이프라인을 구축했습니다"

분석 결과:
  데이터브릭스 (NNP, 고유명사) — 의미 핵심 ✓
  에서       (JKB, 부사격 조사) — 문법 기능, 검색에 불필요
  머신러닝    (NNG, 일반명사) — 의미 핵심 ✓
  파이프라인   (NNG, 일반명사) — 의미 핵심 ✓
  을         (JKO, 목적격 조사) — 문법 기능, 검색에 불필요
  구축       (NNG, 일반명사) — 의미 핵심 ✓
  했         (XSA, 과거 시제 접사) — 문법 기능, 검색에 불필요
  습니다      (EF, 종결 어미) — 문법 기능, 검색에 불필요

→ 검색용 토큰: ["데이터브릭스", "머신러닝", "파이프라인", "구축"]
```

RAG에서는 **명사(NNG, NNP)**, **동사 어근(VV)**, **형용사 어근(VA)**, **외국어(SL)** 만 추출하여 검색에 사용합니다. 조사, 어미 등 문법 기능 형태소를 제거함으로써 **핵심 의미만으로 매칭** 할 수 있게 됩니다.

### Kiwi란?

**Kiwi** 는 C++ 기반의 고속 한국어 형태소 분석기입니다. 다른 한국어 형태소 분석기(KoNLPy의 Mecab, Komoran 등)와 비교했을 때 **정확도와 속도 모두** 뛰어나며, 특히 신조어와 미등록어 처리에 강합니다. Python 바인딩(`kiwipiepy`)을 통해 쉽게 사용할 수 있습니다.

| 형태소 분석기 | 속도 | 정확도 | 설치 편의성 | 미등록어 처리 |
|-------------|------|--------|-----------|------------|
| **Kiwi** | 매우 빠름 (C++) | 높음 | `pip install` 한 줄 | 통계 기반 추정 |
| Mecab (KoNLPy) | 빠름 (C) | 높음 | 시스템 의존성 복잡 | 사전 추가 필요 |
| Komoran (KoNLPy) | 보통 (Java) | 보통 | JVM 필요 | 사전 추가 필요 |
| Okt (KoNLPy) | 느림 (Java) | 보통 | JVM 필요 | 제한적 |

Kiwi를 권장하는 이유는 **Databricks 환경과의 호환성** 때문이기도 합니다. 순수 Python 패키지로 설치되므로 클러스터에 별도 시스템 라이브러리를 설치할 필요가 없고, UDF로 감싸 대규모 배치 처리에도 사용할 수 있습니다.

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

기본 BM25는 공백 기반으로 텍스트를 분절하므로, 한국어에서는 조사가 붙은 채로 토큰화됩니다. Kiwi로 형태소 분석 후 **명사/동사/외국어만 추출** 하면 검색 품질이 크게 향상됩니다.

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
| **형태소 기반** | Kiwi로 의미 단위 분절 | 정확한 의미 보존 | 구현 복잡 |
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

## 5. 한국어 임베딩 모델 선택 가이드

임베딩 모델 선택은 RAG 검색 품질에 직접적인 영향을 미칩니다. 한국어 환경에서는 **다국어 모델** 과 **한국어 특화 모델** 중 사용 환경에 맞는 것을 선택해야 합니다.

### multilingual-e5 vs KoSimCSE: 언제 어떤 모델을 선택할 것인가

| 기준 | multilingual-e5-large-instruct | KoSimCSE (SKT) | bge-m3 (BAAI) |
|------|-------------------------------|----------------|---------------|
| **한영 혼용 문서** | 최적 | 영어 성능 약함 | 우수 |
| **순수 한국어 문서** | 우수 | 최적 | 우수 |
| **Databricks 기본 제공** | 가능 (Foundation Model API) | 불가 (직접 배포 필요) | 불가 (직접 배포 필요) |
| **운영 복잡도** | 낮음 | 높음 (Model Serving 배포) | 높음 (Model Serving 배포) |
| **추론 속도** | 보통 | 빠름 (768차원) | 보통 |
| **Dense + Sparse** | Dense만 | Dense만 | 둘 다 지원 |

**권장 선택 기준:**

1. **빠른 시작 + 한영 혼용**: `multilingual-e5-large-instruct` (Databricks 기본 제공, 추가 배포 불필요)
2. **순수 한국어 + 최고 품질**: `KoSimCSE-roberta-multitask` (한국어 STS 벤치마크 최상위)
3. **하이브리드 검색 내장**: `bge-m3` (Dense + Sparse 벡터를 하나의 모델에서 동시 생성)
4. **비용 최적화**: `gte-multilingual-base` (768차원, 빠른 추론, 스토리지 절약)

### 모델 비교 테이블

| 모델 | 차원 | 한국어 성능 | Databricks 지원 | 비고 |
|------|------|------------|----------------|------|
| **multilingual-e5-large-instruct** | 1024 | 우수 | Foundation Model API | 다국어, Databricks 기본 제공 |
| **bge-m3**(BAAI) | 1024 | 우수 | Model Serving 배포 | Dense + Sparse 하이브리드 지원 |
| **KoSimCSE**(SKT) | 768 | 매우 우수 | Model Serving 배포 | 한국어 특화, STS 벤치마크 상위 |
| **gte-multilingual-base**(Alibaba) | 768 | 우수 | Model Serving 배포 | 경량, 빠른 추론 속도 |

### KoSimCSE를 Model Serving에 배포하는 방법

한국어 특화 모델을 사용하려면 Databricks Model Serving에 직접 배포해야 합니다.

```python
import mlflow
from sentence_transformers import SentenceTransformer

# 1. 모델 로드 및 MLflow에 로깅
model = SentenceTransformer("BM-K/KoSimCSE-roberta-multitask")

with mlflow.start_run():
    mlflow.sentence_transformers.log_model(
        model=model,
        artifact_path="kosimcse",
        registered_model_name="catalog.schema.kosimcse_embedding",
        input_example=["한국어 임베딩 테스트"],
    )

# 2. Model Serving Endpoint 생성
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedEntityInput

w = WorkspaceClient()
w.serving_endpoints.create_and_wait(
    name="kosimcse-embedding",
    config=EndpointCoreConfigInput(
        served_entities=[
            ServedEntityInput(
                entity_name="catalog.schema.kosimcse_embedding",
                entity_version="1",
                workload_size="Small",
                scale_to_zero_enabled=True,
            )
        ]
    ),
)
```

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
| **토크나이저** | Kiwi + KSS 조합 | 형태소 분석 + 문장 분리 |
| **청킹** | Recursive + 한국어 구분자 | 종결어미 기반 자연스러운 분절 |
| **임베딩** | multilingual-e5-large-instruct | Databricks 기본 제공, 한영 혼용 지원 |
| **검색** | Hybrid (Kiwi BM25 + Vector) | 키워드 + 의미 검색 결합 |
| **재정렬** | bge-reranker-v2-m3 | 다국어 Reranker, 한국어 지원 |

### 왜 Re-ranking이 한국어 RAG에서 특히 중요한가

위 테이블에서 **재정렬(Re-ranking)** 을 권장하는 이유를 깊이 살펴봅니다. Re-ranking은 단순히 "검색 결과를 더 잘 정렬하는 것"이 아니라, **LLM이 최종 답변을 생성하는 품질에 직접적으로 영향** 을 미칩니다.

**"Lost in the Middle" 문제: LLM은 컨텍스트의 위치에 민감하다**

2023년 스탠포드 연구("Lost in the Middle: How Language Models Use Long Contexts")에서 밝혀진 핵심 발견은, LLM이 긴 컨텍스트를 받았을 때 **처음과 끝에 있는 정보는 잘 활용하지만, 중간에 있는 정보는 간과하는 경향** 이 있다는 것입니다.

```
LLM에 전달되는 컨텍스트 (5개 문서):

  [문서 1] ← 높은 활용도 ✅  (컨텍스트의 시작)
  [문서 2] ← 보통
  [문서 3] ← 가장 낮은 활용도 ❌  (컨텍스트의 중간 = "사각지대")
  [문서 4] ← 보통
  [문서 5] ← 높은 활용도 ✅  (컨텍스트의 끝)
```

이것이 의미하는 바는 명확합니다: **가장 관련성 높은 문서가 상위(1~2위)에 위치해야 LLM이 이를 최대한 활용하여 정확한 답변을 생성** 합니다. 만약 1차 검색에서 가장 관련 있는 문서가 3위나 4위에 있다면, LLM은 그 정보를 놓칠 수 있습니다.

**Re-ranking 전후 비교 예시:**

```
질문: "Databricks에서 Delta Lake 테이블의 OPTIMIZE 명령 실행 주기는?"

── Re-ranking 없이 (1차 검색 결과 그대로) ──
1위: Delta Lake 개요 및 특징 소개          ← 주제는 맞지만 답변 없음
2위: OPTIMIZE와 VACUUM 명령어 상세 가이드   ← 정답이 여기에! (2위)
3위: Delta Lake 트랜잭션 로그 구조          ← 관련은 있지만 답변 없음
4위: Databricks SQL로 테이블 관리하기       ← 간접 관련
5위: 파티셔닝 전략과 Z-ORDER               ← 간접 관련

── Re-ranking 후 (Cross-encoder가 재정렬) ──
1위: OPTIMIZE와 VACUUM 명령어 상세 가이드   ← 정답! 최상위로 올라옴 ✅
2위: 파티셔닝 전략과 Z-ORDER               ← OPTIMIZE와 직접 연관
3위: Delta Lake 개요 및 특징 소개
4위: Databricks SQL로 테이블 관리하기
5위: Delta Lake 트랜잭션 로그 구조
```

Cross-encoder(질문과 문서를 하나의 입력으로 결합하여 Transformer에 통째로 넣는 방식)는 질문과 각 문서를 **함께 읽고** 교차 비교하기 때문에, "OPTIMIZE 실행 주기"라는 질문의 의도와 문서 내용의 대응 관계를 Bi-encoder(질문과 문서를 각각 독립적으로 벡터화하여 비교하는 방식)보다 훨씬 정밀하게 파악합니다.

**한국어에서 Re-ranking이 특히 효과적인 이유:**

한국어는 앞서 설명한 교착어 특성, 띄어쓰기 불규칙성, 한영 혼용 등의 이유로 **1차 검색(Bi-encoder + BM25)의 순위 정확도가 영어보다 낮은 경향** 이 있습니다. 구체적으로:

1. **조사 변형에 의한 노이즈**: 형태소 분석을 적용해도, 1차 검색 단계의 임베딩 모델은 "데이터브릭스에서"와 "데이터브릭스를"에 미세하게 다른 벡터를 부여할 수 있습니다. Cross-encoder는 이런 표면적 차이를 무시하고 핵심 의미만으로 판단합니다.

2. **한영 혼용 매칭**: "벡터 검색"과 "Vector Search"가 동일 개념임을 Bi-encoder는 불완전하게 포착하지만, Cross-encoder는 질문-문서 쌍을 통째로 읽으므로 **교차 언어 의미 매칭** 이 더 정확합니다.

3. **전문 용어 문맥 이해**: "Unity Catalog 권한 설정"이라는 질문에서, Bi-encoder는 "권한"이라는 키워드와 매칭되는 모든 문서를 비슷한 점수로 반환하지만, Cross-encoder는 "Unity Catalog의 권한"이라는 **구체적 문맥** 을 이해하여 정밀하게 순위를 매깁니다.

{% hint style="info" %}
**실전 수치**: 한국어 기술 문서 RAG에서 Re-ranking을 추가하면 Top-5 Precision이 일반적으로 **10~25%p 향상** 됩니다. 특히 유사한 주제의 문서가 많은 도메인(예: Databricks 공식 문서처럼 여러 기능이 비슷한 키워드를 공유하는 경우)에서 효과가 두드러집니다. Re-ranking의 구체적인 구현 방법과 모델 비교는 [Re-ranking 개념](concepts/reranking.md) 및 [Reranking 전략](advanced-retrieval/reranking.md) 페이지를 참조하세요.
{% endhint %}

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

- **한국어 평가 데이터셋을 직접 구축** 해야 합니다. 영어 벤치마크 결과가 한국어 성능을 보장하지 않습니다.
- 평가 지표: Retrieval에는 **Recall@K** (상위 K개 결과 중 정답이 포함된 비율), **MRR(Mean Reciprocal Rank, 정답 문서가 몇 번째에 위치하는지의 역수 평균)**, 생성에는 **정확성**, **근거 충실도(Faithfulness, 답변이 제공된 컨텍스트에 근거하는 정도)** 를 측정합니다.
- MLflow Evaluate를 활용한 평가 방법은 [RAG 평가](evaluation.md) 가이드를 참조하세요.

{% hint style="warning" %}
한국어 RAG 시스템을 평가할 때, LLM-as-Judge를 사용한다면 평가 프롬프트도 한국어로 작성하거나, 한국어 이해도가 높은 모델(Claude, GPT-4 등)을 Judge로 사용해야 합니다.
{% endhint %}

## 7. 한국어 RAG 실전 트러블슈팅

### 자주 발생하는 문제와 해결법

| 문제 | 원인 | 해결 방법 |
|------|------|-----------|
| **"데이터브릭스"를 검색하면 "데이터브릭스에서"가 포함된 문서가 안 나옴** | 공백 기반 BM25에서 조사 결합 형태를 다른 단어로 인식 | Kiwi 토크나이저를 적용한 BM25 사용 |
| **한영 혼용 문서에서 영어 키워드 검색이 안 됨** | 한국어 특화 임베딩 모델이 영어 표현을 잘 이해하지 못함 | 다국어 모델(multilingual-e5, bge-m3) 사용 |
| **청크 중간에서 문장이 잘림** | 영어 기반 구분자만 사용 | 한국어 종결어미 구분자 추가 ("다. ", "요. ") |
| **토큰 비용이 예상보다 높음** | 한국어가 영어 대비 2~3배 많은 토큰 소비 | 청크 크기를 문자 수로 관리, 컨텍스트 길이 최적화 |
| **검색 결과는 좋은데 답변이 부자연스러움** | LLM의 한국어 생성 품질 문제 | Claude 또는 GPT-4 등 한국어 성능이 좋은 모델 사용 |
| **동의어/유의어 검색이 안 됨** | "자동차"와 "차량" 등 동의어의 임베딩 거리가 멀 수 있음 | Query Expansion 또는 Multi-Query Retriever 적용 |

### 성능 벤치마크 참고값

한국어 기술 문서 기반 RAG 시스템의 일반적인 성능 범위입니다 (참고용):

| 지표 | 양호 | 우수 | 최적화 목표 |
|------|------|------|-----------|
| **Recall@5** | > 0.75 | > 0.85 | > 0.90 |
| **Faithfulness** | > 0.80 | > 0.90 | > 0.95 |
| **Answer Relevancy** | > 0.80 | > 0.85 | > 0.90 |
| **검색 지연** | < 500ms | < 200ms | < 100ms |
| **전체 응답 시간** | < 8초 | < 5초 | < 3초 |

{% hint style="info" %}
위 수치는 한국어 기술 문서 기준의 참고값입니다. 도메인(법률, 의료 등)에 따라 기대치가 다를 수 있으며, 반드시 해당 도메인의 평가 데이터셋으로 측정해야 합니다.
{% endhint %}

## 참고 문서

- [Kiwi (kiwipiepy) 공식 문서](https://bab2min.github.io/kiwipiepy/)
- [KSS (Korean Sentence Splitter) GitHub](https://github.com/hyunwoongko/kss)
- [Databricks Foundation Model API](https://docs.databricks.com/aws/en/machine-learning/foundation-models/index.html)
- [LangChain Text Splitters 문서](https://python.langchain.com/docs/how_to/#text-splitters)
- [BGE-M3 (BAAI) HuggingFace](https://huggingface.co/BAAI/bge-m3)
- [KoSimCSE (SKT) HuggingFace](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
