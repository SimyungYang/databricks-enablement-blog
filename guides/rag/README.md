# RAG (검색 증강 생성) 개요

## RAG란 무엇인가?

RAG(Retrieval-Augmented Generation)는 LLM(대규모 언어 모델)이 응답을 생성하기 전에 외부 지식 소스에서 관련 정보를 검색하여 답변의 정확성과 최신성을 높이는 기술입니다.

LLM은 학습 데이터에만 의존하므로, 조직 내부 문서나 최신 정보에 대해 정확한 답변을 제공하기 어렵습니다. RAG는 이 한계를 해결합니다.

### 왜 RAG인가? — 전략적 관점

엔터프라이즈 환경에서 RAG가 사실상 표준(de facto standard)으로 자리잡은 이유는 다음과 같습니다.

**1. 데이터 주권과 보안**

조직의 내부 데이터를 외부 모델 학습에 노출하지 않으면서도 LLM의 능력을 활용할 수 있습니다. Fine-tuning은 모델 학습 과정에서 데이터가 모델에 내재화되지만, RAG는 검색 시점에만 데이터를 참조하므로 **데이터 거버넌스와 접근 제어를 기존 인프라(Unity Catalog)로 그대로 적용** 할 수 있습니다.

**2. 투자 대비 효과 (ROI)**

Fine-tuning 대비 구현 비용이 10분의 1 수준이며, 데이터 업데이트가 실시간으로 반영됩니다. 모델을 재학습할 필요 없이 인덱스만 갱신하면 되므로, **지식이 빠르게 변하는 환경**(정책 문서, 제품 매뉴얼, 법규 등)에서 특히 유리합니다.

**3. 설명 가능성과 감사 추적**

규제 산업(금융, 의료, 법률)에서는 AI 답변의 근거를 명시해야 합니다. RAG는 답변에 사용된 원본 문서를 **출처로 제공** 할 수 있어, 규제 준수와 내부 감사에 필수적인 **설명 가능성(Explainability)** 을 보장합니다.

**4. 점진적 확장 가능**

소규모 문서(수백 건)에서 시작하여 대규모 문서(수백만 건)까지 동일한 아키텍처로 확장할 수 있습니다. Databricks Vector Search의 서버리스 특성 덕분에 인프라 관리 부담 없이 스케일 아웃이 가능합니다.

### RAG의 핵심 가치

- **최신 정보 반영**: 학습 데이터 이후의 정보도 활용 가능
- **조직 내부 지식 활용**: 사내 문서, 정책, 기술 문서 등 독점 데이터 기반 답변
- **출처 추적 가능**: 답변의 근거 문서를 명시하여 신뢰도 향상
- **환각(Hallucination) 감소**: 검색된 실제 데이터 기반으로 답변 생성

## RAG vs Fine-tuning vs Long Context 의사결정 가이드

LLM을 조직 데이터에 연결하는 세 가지 접근법을 비교합니다. 각 방식은 배타적이 아니라 **상호 보완적** 으로 사용할 수 있습니다.

| 항목 | RAG | Fine-tuning | Long Context |
|------|-----|-------------|--------------|
| **데이터 업데이트** | 실시간 반영 (인덱스만 갱신) | 모델 재학습 필요 | 매 요청마다 전체 전달 |
| **비용** | 인프라 비용만 발생 | GPU 학습 비용 높음 | 토큰 비용 매우 높음 |
| **구현 난이도** | 상대적으로 쉬움 | 학습 데이터 준비/튜닝 복잡 | 가장 쉬움 (프롬프트에 붙이기만) |
| **적합한 케이스** | 지식 기반 Q&A, 문서 검색 | 특정 스타일/형식 학습 | 소규모 문서, 단일 문서 분석 |
| **출처 제공** | 가능 (검색 문서 참조) | 불가 | 가능 (문서 전체가 컨텍스트에 포함) |
| **데이터 규모** | 수천~수백만 건 | 수천~수만 건 (학습 데이터) | 수십 건 이하 (컨텍스트 윈도우 제한) |
| **지연 시간** | 검색 + 생성 (1~5초) | 생성만 (빠름) | 긴 컨텍스트 처리 (느릴 수 있음) |

### 의사결정 플로우

```
데이터가 자주 변경되는가?
  ├─ Yes → RAG (인덱스 갱신만으로 최신 상태 유지)
  └─ No → 데이터 규모가 컨텍스트 윈도우 내에 들어가는가?
            ├─ Yes → Long Context (가장 간단한 구현)
            └─ No → 모델의 "행동 패턴"을 바꿔야 하는가?
                      ├─ Yes → Fine-tuning + RAG 조합
                      └─ No → RAG 단독
```

### RAG + Fine-tuning 하이브리드 전략

실무에서는 두 방식을 결합하는 경우도 있습니다:

- **Fine-tuning으로 모델의 응답 스타일을 조정**(예: 고객 응대 톤, 전문 용어 사용, 구조화된 출력 형식)
- **RAG로 최신 지식을 주입**(예: 최신 제품 정보, 변경된 정책, 실시간 데이터)

이 조합은 도메인 특화 챗봇(의료 상담, 법률 자문 등)에서 특히 효과적입니다.

{% hint style="info" %}
대부분의 엔터프라이즈 사용 사례에서는 RAG가 가장 실용적인 시작점입니다. Fine-tuning은 모델의 "행동 패턴"을 바꿔야 할 때, Long Context는 소규모 문서의 전체 분석이 필요할 때 적합합니다.
{% endhint %}

## 2025 RAG 트렌드

RAG 기술은 빠르게 진화하고 있습니다. 2025년 현재 주목해야 할 주요 트렌드를 소개합니다.

### Agentic RAG

기존 RAG는 "질문 → 검색 → 생성"의 단순한 파이프라인이지만, **Agentic RAG** 는 에이전트가 검색 전략을 **스스로 판단** 합니다.

- **쿼리 분해**: 복잡한 질문을 여러 하위 질문으로 분해하여 각각 검색
- **반복 검색**: 첫 번째 검색 결과가 불충분하면 쿼리를 수정하여 재검색
- **도구 선택**: 벡터 검색, SQL 쿼리, API 호출 중 최적의 데이터 소스를 자동 선택
- **Databricks 적용**: Agent Bricks의 Supervisor 패턴으로 여러 검색 에이전트를 오케스트레이션

```python
# Agentic RAG 개념 예시: 에이전트가 검색 전략을 동적으로 결정
# Databricks Agent Framework + LangGraph 활용
from langgraph.graph import StateGraph

def should_retrieve(state):
    """에이전트가 검색이 필요한지 판단"""
    if state["confidence"] < 0.7:
        return "retrieve_more"
    return "generate"
```

### GraphRAG

문서 간의 **관계(relationship)** 를 그래프로 모델링하여, 단순 유사도 검색으로는 찾기 어려운 **간접적 연결** 을 포착합니다.

- **엔티티 추출**: 문서에서 사람, 조직, 개념, 이벤트 등 엔티티를 추출
- **관계 매핑**: 엔티티 간의 관계를 그래프 엣지로 표현
- **커뮤니티 요약**: 관련 엔티티 클러스터를 요약하여 고수준 질문에 답변
- **적합한 케이스**: "이 프로젝트에 관련된 모든 의사결정과 참여자를 알려줘"와 같은 복합 질문

### Self-RAG (자기 반성 RAG)

LLM이 **스스로 검색 결과의 품질을 평가** 하고, 필요 시 검색을 반복하거나 답변을 수정합니다.

- **검색 필요성 판단**: 질문이 LLM 내부 지식만으로 답변 가능한지 먼저 판단
- **관련성 평가**: 검색된 문서가 질문에 관련 있는지 LLM이 직접 평가
- **답변 검증**: 생성된 답변이 검색 결과에 충실한지 자체 검증
- **환각 감소**: 자기 반성 과정을 통해 Faithfulness 지표가 크게 향상

### Corrective RAG (CRAG)

검색 결과의 품질에 따라 **보정 전략** 을 다르게 적용합니다.

- **정확한 문서 검색됨**→ 그대로 사용
- **모호한 결과**→ 웹 검색 등 보조 소스로 보충
- **관련 없는 결과**→ 쿼리를 재구성하여 재검색

{% hint style="info" %}
이러한 트렌드는 RAG의 **"검색 품질을 높이는 방법"** 에 대한 발전입니다. 기본 RAG를 먼저 구축한 후, 평가 결과를 기반으로 고급 패턴을 점진적으로 도입하는 것을 권장합니다.
{% endhint %}

## Databricks RAG 아키텍처

Databricks는 RAG 파이프라인의 모든 구성 요소를 통합 플랫폼에서 제공합니다.

| 계층 | 구성 요소 | 역할 |
|------|----------|------|
| **거버넌스** | Unity Catalog | 데이터 거버넌스, 권한 관리, 리니지 추적 |
| **데이터** | Delta Lake → 데이터 파이프라인 | 원본 데이터 저장 및 전처리 |
| **검색** | Vector Search Index → Embedding 모델 | 문서 임베딩 및 벡터 검색 |
| **모델** | Foundation Model API → Model Serving | LLM 호출 및 서빙 |
| **관측** | MLflow | 실험 추적, 평가, 모니터링, 트레이싱 |

### 핵심 구성 요소

| 구성 요소 | 역할 |
|-----------|------|
| **Delta Lake** | 원본 문서 및 청크 데이터 저장 |
| **Vector Search** | 임베딩 벡터 인덱싱 및 유사도 검색 |
| **Foundation Model API** | 임베딩 생성 및 LLM 응답 생성 |
| **Unity Catalog** | 데이터 거버넌스, 접근 제어, 리니지 추적 |
| **MLflow** | 체인 로깅, 평가, 배포, 모니터링 |

## RAG 파이프라인 전체 흐름

```
Document → Parse → Chunk → Embed → Index → Query → Retrieve → Augment → Generate
```

### 단계별 설명

1. **문서 수집 (Document)**: UC Volumes, S3, ADLS 등에서 원본 문서 수집
2. **파싱 (Parse)**: PDF, HTML, Word 등을 텍스트로 변환
3. **청킹 (Chunk)**: 텍스트를 적절한 크기의 조각으로 분할
4. **임베딩 (Embed)**: 각 청크를 벡터로 변환 (Foundation Model API)
5. **인덱싱 (Index)**: Vector Search Index에 벡터 저장
6. **쿼리 (Query)**: 사용자 질문을 벡터로 변환
7. **검색 (Retrieve)**: 유사한 청크를 Vector Search로 검색
8. **증강 (Augment)**: 검색 결과를 프롬프트에 추가
9. **생성 (Generate)**: LLM이 증강된 프롬프트로 답변 생성

{% hint style="warning" %}
RAG 품질은 "검색 품질"에 크게 좌우됩니다. 청킹 전략과 임베딩 모델 선택이 전체 시스템 성능의 핵심입니다.
{% endhint %}

## 다음 단계

이 가이드 시리즈에서는 Databricks에서 RAG 시스템을 구축하는 전체 과정을 다룹니다:

1. [데이터 준비](data-preparation.md) - 문서 수집, 파싱, 청킹
2. [청킹 전략](chunking-strategies.md) - 청킹 방식별 비교 및 구현
3. [Vector Search 설정](vector-search.md) - 엔드포인트 및 인덱스 생성
4. [고급 Retrieval 전략](advanced-retrieval.md) - 앙상블, Reranking, Hybrid 검색
5. [한국어 RAG 최적화](korean-nlp.md) - Kiwi 형태소 분석, 한국어 임베딩
6. [RAG 체인 구축](chain-building.md) - LangChain 기반 체인 구현
7. [RAG 평가](evaluation.md) - MLflow 기반 품질 측정
8. [RAG 배포](deployment.md) - 프로덕션 서빙 및 모니터링

## RAG 프로젝트 성공을 위한 체크리스트

RAG 프로젝트를 시작하기 전에 확인해야 할 핵심 항목입니다:

### 데이터 준비도

- [ ] 대상 문서가 디지털 형태(PDF, Markdown, HTML 등)로 존재하는가?
- [ ] 문서의 총 규모(건수, 총 크기)를 파악했는가?
- [ ] 문서 업데이트 빈도를 확인했는가? (실시간, 일 단위, 주 단위)
- [ ] 문서에 테이블, 이미지 등 복잡한 레이아웃이 포함되어 있는가?
- [ ] 한국어/영어 혼용 비율을 확인했는가?

### 인프라 준비도

- [ ] Databricks Premium 이상 워크스페이스가 준비되었는가?
- [ ] Unity Catalog가 활성화되어 있는가?
- [ ] SQL Warehouse (Serverless 권장)가 사용 가능한가?
- [ ] Vector Search Endpoint 생성 권한이 있는가?
- [ ] Model Serving Endpoint 생성 권한이 있는가?

### 평가 준비도

- [ ] RAG 시스템이 답변해야 할 대표 질문 목록이 있는가? (최소 20개)
- [ ] 각 질문에 대한 정답(Ground Truth)을 확보했는가?
- [ ] 품질 기준(Faithfulness > 0.9, Relevance > 0.85 등)을 정의했는가?

## 참고 문서

- [Databricks RAG 공식 문서](https://docs.databricks.com/aws/en/generative-ai/retrieval-augmented-generation.html)
- [Vector Search 공식 문서](https://docs.databricks.com/aws/en/generative-ai/vector-search/index.html)
- [Agent Framework 공식 문서](https://docs.databricks.com/aws/en/generative-ai/create-log-agent.html)
- [MLflow 공식 문서](https://mlflow.org/docs/latest/)
- [RAGAS 프레임워크 문서](https://docs.ragas.io/en/latest/)
- [LangChain RAG 튜토리얼](https://python.langchain.com/docs/tutorials/rag/)
