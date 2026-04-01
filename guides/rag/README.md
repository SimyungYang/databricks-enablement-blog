# RAG (검색 증강 생성) 개요

## RAG란 무엇인가?

RAG(Retrieval-Augmented Generation)는 LLM(대규모 언어 모델)이 응답을 생성하기 전에 외부 지식 소스에서 관련 정보를 검색하여 답변의 정확성과 최신성을 높이는 기술입니다.

LLM은 학습 데이터에만 의존하므로, 조직 내부 문서나 최신 정보에 대해 정확한 답변을 제공하기 어렵습니다. RAG는 이 한계를 해결합니다.

### RAG의 핵심 가치

- **최신 정보 반영**: 학습 데이터 이후의 정보도 활용 가능
- **조직 내부 지식 활용**: 사내 문서, 정책, 기술 문서 등 독점 데이터 기반 답변
- **출처 추적 가능**: 답변의 근거 문서를 명시하여 신뢰도 향상
- **환각(Hallucination) 감소**: 검색된 실제 데이터 기반으로 답변 생성

## RAG vs Fine-tuning 비교

| 항목 | RAG | Fine-tuning |
|------|-----|-------------|
| **데이터 업데이트**| 실시간 반영 (인덱스만 갱신) | 모델 재학습 필요 |
| **비용**| 인프라 비용만 발생 | GPU 학습 비용 높음 |
| **구현 난이도**| 상대적으로 쉬움 | 학습 데이터 준비/튜닝 복잡 |
| **적합한 케이스**| 지식 기반 Q&A, 문서 검색 | 특정 스타일/형식 학습 |
| **출처 제공**| 가능 (검색 문서 참조) | 불가 |

{% hint style="info" %}
대부분의 엔터프라이즈 사용 사례에서는 RAG가 더 실용적인 선택입니다. Fine-tuning은 모델의 "행동 패턴"을 바꿔야 할 때 적합합니다.
{% endhint %}

## Databricks RAG 아키텍처

Databricks는 RAG 파이프라인의 모든 구성 요소를 통합 플랫폼에서 제공합니다.

```
┌─────────────────────────────────────────────────────┐
│                  Unity Catalog                       │
│  (데이터 거버넌스 · 권한 관리 · 리니지 추적)          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐   ┌───────────────┐   ┌────────────┐ │
│  │ Delta     │──▶│ Vector Search │──▶│ Foundation │ │
│  │ Lake      │   │ Index         │   │ Model API  │ │
│  └──────────┘   └───────────────┘   └────────────┘ │
│       │                │                   │        │
│       ▼                ▼                   ▼        │
│  ┌──────────┐   ┌───────────────┐   ┌────────────┐ │
│  │ 데이터    │   │ Embedding     │   │ Model      │ │
│  │ 파이프라인│   │ 모델          │   │ Serving    │ │
│  └──────────┘   └───────────────┘   └────────────┘ │
│                                                      │
│  MLflow (실험 추적 · 평가 · 모니터링 · 트레이싱)      │
└─────────────────────────────────────────────────────┘
```

### 핵심 구성 요소

| 구성 요소 | 역할 |
|-----------|------|
| **Delta Lake**| 원본 문서 및 청크 데이터 저장 |
| **Vector Search**| 임베딩 벡터 인덱싱 및 유사도 검색 |
| **Foundation Model API**| 임베딩 생성 및 LLM 응답 생성 |
| **Unity Catalog**| 데이터 거버넌스, 접근 제어, 리니지 추적 |
| **MLflow**| 체인 로깅, 평가, 배포, 모니터링 |

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

## 참고 문서

- [Databricks RAG 공식 문서](https://docs.databricks.com/aws/en/generative-ai/retrieval-augmented-generation.html)
- [Vector Search 공식 문서](https://docs.databricks.com/aws/en/generative-ai/vector-search/index.html)
- [Agent Framework 공식 문서](https://docs.databricks.com/aws/en/generative-ai/create-log-agent.html)
- [MLflow 공식 문서](https://mlflow.org/docs/latest/)
