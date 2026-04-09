# 고급 Retrieval 전략

RAG 시스템의 성능은 **검색(Retrieval) 품질** 에 가장 크게 좌우됩니다. 이 가이드에서는 기본 Dense Retrieval을 넘어, 검색 기술의 진화 과정부터 한국어 하이브리드 검색, 고급 전처리/후처리 전략, 그리고 Databricks 환경에서의 프로덕션 구현 로드맵까지 포괄적으로 다룹니다.

---

## 검색의 진화: 키워드에서 대화형 검색까지

현대 RAG 시스템을 이해하려면 **검색 기술이 어떻게 진화해 왔는지** 를 먼저 파악해야 합니다. 검색은 단순한 키워드 매칭에서 시작하여 점점 더 지능적인 방향으로 발전해 왔습니다.

아래 표는 검색 기술의 5단계 진화 과정을 요약합니다.

| 단계 | 검색 유형 | 핵심 기술 | 대표 서비스 | 한계 |
|------|----------|----------|-----------|------|
| **1단계** | 키워드 검색 | TF-IDF, BM25, 역색인(Inverted Index) | 초기 Google, Elasticsearch | 동의어/문맥 이해 불가. "자동차" 검색 시 "차량" 문서 누락 |
| **2단계** | 개인화 검색 | 사용자 행동 로그, 클릭률, Collaborative Filtering(유사한 사용자의 행동 패턴을 기반으로 추천하는 기법) | Google PageRank, Amazon | 콜드 스타트 문제. 새 사용자/콘텐츠에 취약 |
| **3단계** | 시맨틱 검색 | 벡터 임베딩, ANN(Approximate Nearest Neighbor, 정확한 최근접 이웃 대신 근사값을 빠르게 찾는 알고리즘), BERT/Sentence-BERT | Pinecone, Weaviate, Databricks VS | 정확한 키워드 매칭 약함. 고유명사/코드/숫자 검색 실패 |
| **4단계** | 하이브리드 검색 | Dense + Sparse 결합, RRF(Reciprocal Rank Fusion, 여러 검색 결과의 순위를 역수 합산으로 통합하는 알고리즘), Re-ranking | Databricks VS Hybrid, Elasticsearch 8.x | 가중치 튜닝 필요. 다국어 토크나이저 문제 |
| **5단계** | 대화형 검색 | LLM + RAG, Query Rewrite, Agentic RAG, Tool Use | ChatGPT + Retrieval, Databricks Agent | 비용 높음. 환각(Hallucination) 위험 |

### 왜 키워드 검색이 여전히 필요한가 - "코끼리 식당" 문제

시맨틱(벡터) 검색이 아무리 발전해도 **키워드 검색을 완전히 대체할 수는 없습니다.** 그 이유를 "코끼리 식당"이라는 실제 상호명 검색 시나리오로 살펴봅시다.

**벡터 검색의 한계:**

- 사용자가 "코끼리 식당"을 검색하면, 벡터 검색은 "코끼리"를 **동물** 로 이해합니다
- 결과: "동물원 근처 식당", "아프리카 테마 레스토랑" 같은 **의미적으로 유사하지만 전혀 다른 문서** 를 반환
- 임베딩 모델은 단어의 의미를 압축하므로, 고유명사의 **문자열 그 자체** 를 매칭하는 데 약함

**키워드 검색의 강점:**

- BM25/TF-IDF 기반 검색은 "코끼리 식당"이라는 **정확한 문자열** 이 포함된 문서를 찾음
- 에러 코드(`DELTA_TABLE_NOT_FOUND`), 제품명(`DBR 15.4`), 법령 번호(`제42조`) 등 **정확 매칭이 필수** 인 경우에 탁월

{% hint style="info" %}
**핵심 인사이트:** 벡터 검색은 "무엇을 의미하는가"를 이해하고, 키워드 검색은 "정확히 무엇이라고 쓰여 있는가"를 찾습니다. 프로덕션 RAG 시스템에서는 **둘 다 필요** 합니다.
{% endhint %}

### 생성형 AI와 검색의 상호 보완 관계

LLM과 검색은 서로의 약점을 보완하는 **공생 관계** 입니다.

**LLM이 검색에 제공하는 가치:**

- **문맥 파악 능력**: "사과"가 과일인지 사과(謝過)인지 대화 맥락에서 판단
- **Query Rewrite**: 모호한 질문을 검색에 최적화된 형태로 재작성
- **의도 분류**: 질문의 의도에 따라 적합한 데이터 소스로 라우팅

**검색이 LLM에 제공하는 가치:**

- **최신 정보**: LLM의 학습 데이터 컷오프 이후 정보를 실시간으로 제공
- **사실 근거(Grounding)**: 환각을 줄이고, 출처를 명시할 수 있는 근거 문서 제공
- **도메인 지식**: 기업 내부 문서, 규정, 매뉴얼 등 LLM이 학습하지 못한 전문 지식 제공

---

## 서브 페이지

| 페이지 | 설명 |
|--------|------|
| [하이브리드 검색](hybrid-search.md) | 핵심 3요소(RRF, 정규화, 가중치) + 한국어 하이브리드 검색 도전 + Databricks 구현 |
| [전처리 기법](preprocessing.md) | 메타데이터 필터링, Query Rewrite, Contextual Retrieval, Query Routing, 다중 쿼리 분해 |
| [Reranking 전략](reranking.md) | Learning to Rank, Collaborative Filtering, Cross-Encoder, ColBERT, LLM 재정렬 |
| [후처리 기법](postprocessing.md) | Self-RAG, Corrective RAG, FLARE, 출력 가드레일 |
| [고급 청킹](chunking-advanced.md) | 부모/자식, 의미 기반, 명제 기반 (심화 내용) |
| [구현 로드맵](implementation.md) | Databricks Advanced RAG 구현 로드맵 (Phase 1~3) |
