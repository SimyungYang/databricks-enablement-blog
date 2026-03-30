# Re-ranking — "1차 검색 결과를 정밀하게 재정렬"

> 1차 검색(Retrieval)은 수백만 문서에서 후보를 빠르게 추려내는 단계입니다. 하지만 속도를 위해 정밀도를 희생합니다. Re-ranking은 추려낸 소수의 후보를 더 정교한 모델로 재평가하여, 최종적으로 LLM에 전달할 최고의 문서를 선별합니다.

---

## 2단계 검색 패턴: Recall과 Precision의 분리

RAG 검색은 두 단계로 나뉩니다:

```
[100만 문서]
     ↓ 1단계: Retrieval (Bi-encoder) — Recall 중시
[상위 20개 후보]
     ↓ 2단계: Re-ranking (Cross-encoder) — Precision 중시
[상위 5개 문서]
     ↓ LLM에 전달
[최종 답변 생성]
```

- **1단계 (Recall 중시)**: "관련 있을 수 있는 문서를 하나도 빠뜨리지 말자" → 빠르지만 다소 부정확
- **2단계 (Precision 중시)**: "이 후보들 중 진짜 관련 있는 것만 골라내자" → 느리지만 매우 정확

{% hint style="info" %}
**왜 한 번에 정밀하게 하지 않는가?** 100만 문서를 Cross-encoder로 평가하면 한 쿼리당 수 분이 걸립니다. 20개 문서만 평가하면 수백 밀리초면 충분합니다. **비용 대비 효과**를 최적화하는 것이 2단계 패턴의 핵심입니다.
{% endhint %}

---

## Bi-encoder vs Cross-encoder: 깊이 있는 비교

### Bi-encoder (1차 검색용)

질문과 문서를 **각각 독립적으로** 임베딩합니다:

```
질문: "Databricks에서 벡터 검색 설정하는 방법" → [0.23, -0.41, ...] (768차원)
문서: "Vector Search 인덱스 생성 가이드"       → [0.25, -0.39, ...] (768차원)

→ 코사인 유사도 계산: 0.93
```

**핵심 특성**: 질문 벡터와 문서 벡터가 서로에 대한 정보 없이 독립적으로 생성됩니다. 문서 벡터는 **미리 계산해서 저장**해둘 수 있습니다 (오프라인 인덱싱).

**한계**: 질문과 문서 사이의 **세밀한 상호작용**을 포착하지 못합니다. 예를 들어, 질문의 특정 단어가 문서의 특정 구절과 정확히 대응되는지 판단하기 어렵습니다.

### Cross-encoder (Re-ranking용)

질문과 문서를 **하나의 입력으로 결합**하여 Transformer에 통째로 넣습니다:

```
입력: "[CLS] Databricks에서 벡터 검색 설정하는 방법 [SEP] Vector Search 인덱스 생성 가이드 [SEP]"

Transformer 내부:
- "벡터 검색" ←→ "Vector Search" 사이의 Attention 발생
- "설정하는 방법" ←→ "생성 가이드" 사이의 Attention 발생
- 이런 교차 상호작용을 통해 정밀한 관련성 점수 산출

→ 관련성 점수: 0.97
```

**핵심 특성**: 질문의 모든 토큰이 문서의 모든 토큰과 **직접 상호작용(Cross-attention)**합니다. 이를 통해 "질문의 이 부분이 문서의 저 부분과 정확히 대응된다"는 세밀한 판단이 가능합니다.

**한계**: 질문-문서 쌍마다 전체 Transformer를 실행해야 하므로 **매우 느립니다**. 사전 계산이 불가능합니다.

### 비유로 이해하기

| 관점 | Bi-encoder | Cross-encoder |
|------|-----------|---------------|
| 채용 비유 | **이력서 키워드 스크리닝**: 이력서와 채용 공고를 각각 분석하여 키워드 매칭. 빠르지만 맥락 파악 불가 | **심층 면접**: 지원자와 면접관이 직접 대화하며 적합성 평가. 느리지만 정밀 |
| 번역 비유 | 두 문장을 각각 요약한 뒤 요약끼리 비교 | 두 문장을 나란히 놓고 단어 대 단어로 대조 |
| 속도 | 100만 문서: ~100ms | 20 문서: ~200ms |
| 정확도 | 좋음 | 매우 좋음 |

---

## 주요 Re-ranking 모델 비교

| 모델 | 제공자 | 특징 | 한국어 지원 |
|------|--------|------|------------|
| **Cohere Reranker** | Cohere | API 방식, 높은 정확도, 다국어 지원 | 좋음 |
| **BGE Reranker v2** | BAAI | 오픈소스, Self-hosting 가능 | 좋음 |
| **Jina Reranker** | Jina AI | 오픈소스, 가벼움 | 보통 |
| **ms-marco MiniLM** | Microsoft | 가벼움, 영어 특화 | 미지원 |

{% hint style="info" %}
**Databricks에서의 선택**: Cohere Reranker는 Foundation Model API를 통해 쉽게 사용할 수 있습니다. 오픈소스를 선호한다면 BGE Reranker v2를 Model Serving Endpoint로 배포하여 사용할 수 있습니다.
{% endhint %}

---

## 성능 영향: Re-ranking이 만드는 차이

### 실험 결과 (일반적인 벤치마크 기준)

```
검색 방식                          | Top-5 Precision | Top-5 Recall
----------------------------------|-----------------|-------------
Dense만 (Bi-encoder)              | 62%             | 78%
Dense + BM25 하이브리드            | 71%             | 85%
Dense + BM25 + Re-ranking         | 84%             | 88%
                                     ↑ +13%p 향상!
```

Re-ranking을 추가하면 Top-5 Precision이 **10-30%p** 향상되는 것이 일반적입니다. 특히 질문이 모호하거나, 비슷한 주제의 문서가 많은 경우 Re-ranking의 효과가 극대화됩니다.

### 왜 이런 차이가 나는가?

1차 검색(Bi-encoder)에서는 "대략적으로 관련 있는 20개"를 뽑습니다. 이 중에는:
- **진짜 관련 있는 문서 5개**: 질문에 정확히 답할 수 있는 문서
- **약간 관련 있는 문서 10개**: 주제는 비슷하지만 직접적 답변이 아닌 문서
- **거의 관련 없는 문서 5개**: 키워드만 겹치는 문서

Re-ranking의 Cross-encoder가 이 20개를 정밀하게 재평가하면, **"진짜 관련 있는 5개"가 상위에 올라오고 나머지는 밀려납니다.**

---

## 실무 파이프라인: Retrieve 20 → Rerank → Top 5

### 권장 설정

```python
# 1단계: 넓게 검색 (Recall 중시)
initial_results = vs_index.similarity_search(
    query_text=question,
    num_results=20,           # 넉넉하게 20개 후보 추출
    query_type="hybrid"       # Dense + BM25 하이브리드
)

# 2단계: 정밀 재정렬 (Precision 중시)
reranked = reranker.rerank(
    query=question,
    documents=initial_results,
    top_n=5                   # 최종 5개만 선택
)

# 3단계: LLM에 전달
context = "\n\n".join([doc.text for doc in reranked])
answer = llm.generate(prompt_template.format(context=context, question=question))
```

### 숫자의 의미

| 파라미터 | 값 | 이유 |
|----------|-----|------|
| 1차 검색 수 | 20 | Recall을 충분히 확보. 30-50으로 늘려도 되지만 Re-ranking 시간 증가 |
| Re-ranking 결과 수 | 5 | LLM 컨텍스트 윈도우를 고려한 최적값. 3-7 범위 권장 |

{% hint style="warning" %}
**지연 시간 고려**: Re-ranking은 20개 문서 기준 약 100-300ms가 추가됩니다. 실시간 챗봇에서는 전체 응답 시간에 영향을 줄 수 있으므로, Re-ranking 대상 수(1차 검색 결과 수)를 적절히 조절하세요. 50개 이상은 대부분 불필요합니다.
{% endhint %}

---

## Re-ranking 없이 성능을 높이는 대안

Re-ranking 도입이 어려운 경우 다음 대안을 고려하세요:

1. **임베딩 모델 업그레이드**: 더 좋은 Bi-encoder 모델로 1차 검색 품질 자체를 높임
2. **청킹 최적화**: 적절한 크기와 오버랩으로 검색 단위 자체의 품질 향상
3. **쿼리 확장**: 사용자 질문을 LLM으로 확장/변환하여 검색 (HyDE, Query Expansion)
4. **메타데이터 필터링**: 카테고리, 날짜 등으로 검색 범위를 사전에 좁힘

---

> **이전으로 돌아가기**: [핵심 개념 사전 목록](README.md)
