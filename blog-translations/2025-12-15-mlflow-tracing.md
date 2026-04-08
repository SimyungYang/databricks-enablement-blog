---
title: "MLflow Tracing: GenAI 애플리케이션을 위한 엔드투엔드 관측성"
date: 2025-12-15
author: "Databricks"
original_url: "https://www.databricks.com/blog/mlflow-tracing"
tags: [mlflow, tracing, genai, observability, opentelemetry, llm, agents]
---

> **원문**: [MLflow Tracing: End-to-End Observability for GenAI Applications](https://www.databricks.com/blog/mlflow-tracing)

{% hint style="warning" %}
요청하신 URL(`https://www.databricks.com/blog/mlflow-tracing`)은 현재 404 오류를 반환합니다. Databricks 공식 문서, MLflow 3.0 발표 블로그 포스트, 그리고 관련 기술 자료를 종합하여 MLflow Tracing의 전체 내용을 번역·정리합니다. 원문 참고 자료: [MLflow 3.0 블로그](https://www.databricks.com/blog/mlflow-30-unified-ai-experimentation-observability-and-governance), [MLflow Tracing 공식 문서](https://docs.databricks.com/aws/en/mlflow3/genai/tracing)
{% endhint %}

# MLflow Tracing: GenAI 애플리케이션을 위한 엔드투엔드 관측성

**게시일**: 2025년 12월 15일

---

GenAI (Generative AI) 애플리케이션이 프로덕션으로 확장될수록, 개발자들은 새로운 도전에 직면합니다. LLM (Large Language Model)이 예상치 못한 방식으로 응답하거나, 에이전트 (Agent)가 잘못된 도구를 호출하거나, 검색 품질이 저하되어도 어디서 문제가 발생했는지 파악하기 어렵습니다. 전통적인 소프트웨어 디버깅 도구는 자유 형식의 언어와 비결정론적(non-deterministic) 동작으로 구성된 GenAI 시스템에는 적합하지 않습니다.

**MLflow Tracing** 은 이 문제를 해결합니다. MLflow Tracing은 GenAI 애플리케이션과 에이전트를 포함한 복잡한 AI 시스템 전체에 걸쳐 완전한 관측성(observability)을 제공하며, 개발부터 프로덕션까지 모든 요청의 입력, 출력, 중간 단계, 메타데이터를 기록합니다.

---

## GenAI 관측성이 어려운 이유

기존 ML 모델과 달리, GenAI 애플리케이션은 여러 컴포넌트가 연결된 복잡한 체인 구조를 가집니다. 하나의 사용자 요청이 처리되는 동안 다음과 같은 일들이 발생합니다:

- **프롬프트 구성 (Prompt Construction)**: 시스템 프롬프트와 사용자 입력이 결합됩니다.
- **벡터 검색 (Vector Retrieval)**: 관련 문서나 컨텍스트가 데이터베이스에서 가져옵니다.
- **LLM 호출 (LLM Invocation)**: 대형 언어 모델이 실제 추론을 수행합니다.
- **도구 호출 (Tool Calls)**: 에이전트가 외부 API나 함수를 호출합니다.
- **결과 파싱 (Response Parsing)**: 모델 출력이 최종 응답 형식으로 변환됩니다.

이 체인의 어느 단계에서도 문제가 생길 수 있는데, 기존 로깅 방식으로는 여러 서비스에 분산된 중간 단계를 추적하거나, 어떤 프롬프트 버전이 어떤 응답을 만들었는지 연결하거나, 응답 품질과 지연 시간을 동시에 측정하기가 매우 어렵습니다. MLflow Tracing은 이 모든 복잡성을 단일하고 일관된 관측성 레이어로 해결합니다.

---

## MLflow Tracing이란?

MLflow Tracing은 GenAI 애플리케이션의 전체 실행 경로를 **스팬(Span)** 이라는 단위로 기록하고, 이를 계층 구조의 **트레이스(Trace)** 로 조직화하는 관측성 프레임워크입니다.

각 스팬은 다음 정보를 캡처합니다:

| 속성 | 설명 |
|------|------|
| 입력/출력 | 스팬에 전달된 데이터와 반환된 결과 |
| 지연 시간 | 각 단계의 실행 시간 (밀리초 단위) |
| 토큰 수 | LLM 호출 시 사용된 입력/출력 토큰 수 |
| 스팬 타입 | LLM, 검색, 도구 호출, 체인 등 단계 분류 |
| 메타데이터 | 모델 이름, 온도 설정, 커스텀 속성 등 |
| 상태 | 성공, 오류, 타임아웃 여부 |

트레이스는 단일 요청이 시스템을 통과하는 전체 여정을 나타내며, 부모-자식 관계로 중첩된 스팬들의 트리 구조로 표현됩니다. 이를 통해 개발자는 성능 병목 지점을 빠르게 식별하고, 특정 실패가 어느 컴포넌트에서 발생했는지 정확하게 파악할 수 있습니다.

---

## OpenTelemetry 기반 설계

MLflow Tracing은 업계 표준인 **OpenTelemetry (OTEL)** 위에 구축되었습니다. 이는 여러 측면에서 중요한 의미를 가집니다.

첫째, **벤더 중립성**입니다. OpenTelemetry 표준을 따르기 때문에 Databricks 외부에 배포된 에이전트, AWS, GCP, 온프레미스 환경에서도 동일한 방식으로 트레이스를 수집할 수 있습니다.

둘째, **기존 인프라와의 통합**입니다. 이미 Jaeger, Zipkin, Datadog 등 OTEL 호환 모니터링 솔루션을 사용하는 팀은 MLflow Tracing을 추가 비용 없이 통합할 수 있습니다.

셋째, **엔터프라이즈 규모의 확장성**입니다. `mlflow-tracing` 패키지는 성능에 최적화된 경량 라이브러리로, 프로덕션에서 대량의 트레이스를 빠르게 기록할 수 있도록 설계되었습니다.

---

## 핵심 기능

### 1. 자동 계측 (Automatic Instrumentation)

MLflow Tracing의 가장 강력한 기능 중 하나는 단 한 줄의 코드로 자동 계측을 활성화할 수 있다는 점입니다. OpenAI, LangChain, LangGraph, Anthropic, DSPy, AWS Bedrock, AutoGen 등 20개 이상의 GenAI 라이브러리를 지원합니다.

```python
import mlflow
from openai import OpenAI

# 단 한 줄로 OpenAI 자동 트레이싱 활성화
mlflow.openai.autolog()

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "당신은 도움이 되는 어시스턴트입니다."},
        {"role": "user", "content": "MLflow Tracing의 주요 기능은 무엇인가요?"}
    ]
)
```

위 코드를 실행하면 MLflow는 자동으로 다음을 기록합니다: 요청 메시지 전체, LLM 응답, 모델 파라미터(온도, 최대 토큰 수 등), 사용된 토큰 수, 지연 시간. 별도의 계측 코드를 작성할 필요가 없습니다.

### 2. 다중 프레임워크 동시 트레이싱

실제 GenAI 애플리케이션은 여러 라이브러리를 함께 사용하는 경우가 많습니다. MLflow Tracing은 여러 프레임워크를 동시에 추적하고, 이를 하나의 일관된 트레이스로 통합합니다.

```python
import mlflow
import openai
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from mlflow.entities import SpanType

# 여러 프레임워크 동시 자동 트레이싱
mlflow.openai.autolog()
mlflow.langchain.autolog()

client = openai.OpenAI()

@mlflow.trace(span_type=SpanType.CHAIN)
def multi_provider_workflow(query: str):
    # OpenAI 직접 호출로 쿼리 분석
    analysis = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "쿼리를 분석하여 핵심 주제를 추출하세요."},
            {"role": "user", "content": query}
        ]
    )
    topics = analysis.choices[0].message.content

    # LangChain으로 상세 응답 생성
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_template(
        "다음 주제들을 바탕으로: {topics}\n이 질문에 답하세요: {query}"
    )
    chain = prompt | llm
    response = chain.invoke({"topics": topics, "query": query})
    return response

result = multi_provider_workflow("양자 컴퓨팅을 설명해주세요")
```

이 예시에서 MLflow는 OpenAI 직접 호출과 LangChain 체인을 모두 추적하여, 두 프레임워크의 스팬이 하나의 상위 트레이스 안에 계층적으로 구성된 단일 뷰를 제공합니다.

### 3. 수동 계측 데코레이터 (Manual Instrumentation)

자동 계측으로 커버되지 않는 커스텀 비즈니스 로직을 추적하려면 `@mlflow.trace` 데코레이터를 사용합니다.

```python
import mlflow
import openai
from mlflow.entities import SpanType

mlflow.openai.autolog()
client = openai.OpenAI()

@mlflow.trace(span_type=SpanType.CHAIN)
def run(question: str):
    messages = build_messages(question)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=100,
        messages=messages,
    )
    return parse_response(response)

@mlflow.trace
def build_messages(question: str):
    # 커스텀 프롬프트 구성 로직
    return [
        {"role": "system", "content": "당신은 도움이 되는 챗봇입니다."},
        {"role": "user", "content": question},
    ]

@mlflow.trace
def parse_response(response):
    # 커스텀 응답 파싱 로직
    return response.choices[0].message.content

run("MLflow란 무엇인가요?")
```

자동 계측과 수동 데코레이터를 함께 사용하면, LLM 호출은 자동으로 추적되고 커스텀 비즈니스 로직도 동일한 트레이스 계층 구조 안에서 함께 추적됩니다. 이를 통해 AI 로직과 애플리케이션 코드 전체의 완전한 가시성을 확보할 수 있습니다.

---

## 트레이스 UI: 디버깅을 위한 인터랙티브 뷰

MLflow Tracing은 수집된 트레이스를 탐색하기 위한 풍부한 사용자 인터페이스를 제공합니다.

트레이스 UI의 주요 기능은 다음과 같습니다:

**인터랙티브 타임라인 뷰**는 각 스팬의 시작 시간과 지연 시간을 시각적으로 표시하여, 어떤 단계가 가장 많은 시간을 소비하는지 즉시 파악할 수 있게 합니다. 병목 현상이 검색 단계에 있는지, LLM 호출에 있는지, 아니면 후처리 단계에 있는지 한눈에 볼 수 있습니다.

**스팬 상세 정보 패널**을 통해 특정 스팬을 클릭하면 해당 단계의 입력, 출력, 메타데이터, 오류 메시지 전체를 확인할 수 있습니다. 복잡한 에이전트 시나리오에서 어떤 도구가 어떤 인자로 호출되었는지 정확하게 추적할 수 있습니다.

**버전 비교 기능**을 통해 서로 다른 프롬프트 버전, 모델 설정, 또는 에이전트 로직으로 생성된 트레이스를 나란히 비교할 수 있습니다. A/B 테스트 결과를 데이터 기반으로 분석하는 데 필수적입니다.

**In-Progress 트레이스 디스플레이**는 실행 중인 트레이스의 스팬을 실시간으로 표시하는 기능으로, 장시간 실행되는 에이전트 작업을 실시간으로 모니터링할 수 있습니다.

---

## 프로덕션 트레이싱: 개발을 넘어

MLflow Tracing의 진정한 가치는 프로덕션 환경에서 발휘됩니다. 개발 단계에서 디버깅 도구로 시작했지만, 프로덕션 관측성의 핵심 인프라로 진화했습니다.

### Databricks Agent Framework와의 통합

Databricks의 Mosaic AI Agent Framework를 사용하여 에이전트를 배포할 경우, MLflow Tracing은 **추가 설정 없이 자동으로 활성화**됩니다. 모든 프로덕션 요청이 자동으로 추적되어 연결된 MLflow 실험에 실시간으로 저장됩니다.

```python
import mlflow
from mlflow.entities import SpanType

mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/production-agent-experiment")

# 에이전트 배포 시 자동으로 트레이싱 활성화
# mlflow.langchain.autolog() 또는 mlflow.openai.autolog() 호출만으로 충분
```

### Unity Catalog와의 장기 보존 통합

MLflow Tracing은 Unity Catalog와 통합되어 장기적인 트레이스 보존과 거버넌스를 지원합니다. OpenTelemetry 형식의 트레이스를 Delta 테이블에 직접 수집하여 다음이 가능합니다:

- 대량의 프로덕션 트레이스에 대한 SQL 쿼리
- 장기 품질 트렌드 분석
- 컴플라이언스 및 감사 목적의 변경 불가 로그
- 트레이스 데이터를 기반으로 한 평가 데이터셋 자동 구축

---

## MLflow Tracing이 활성화하는 워크플로우

MLflow Tracing은 단순한 디버깅 도구를 넘어 GenAI 개발의 전체 품질 개선 사이클을 지원합니다.

다음 표는 트레이싱이 각 개발 단계에서 어떻게 활용되는지 보여줍니다:

| 개발 단계 | MLflow Tracing 활용 방식 |
|-----------|--------------------------|
| 개발 & 디버깅 | 예상치 못한 동작의 근본 원인을 스팬 레벨에서 정확하게 파악 |
| 평가 데이터셋 구축 | 프로덕션 트레이스에서 문제가 있거나 우수한 예시를 수집하여 평가 데이터 생성 |
| 품질 평가 | LLM-as-a-judge 평가자가 각 트레이스의 스팬을 검사하여 품질 점수 부여 |
| A/B 테스트 | 서로 다른 프롬프트나 모델 버전의 트레이스를 비교하여 개선 효과 측정 |
| 프로덕션 모니터링 | 지연 시간, 토큰 비용, 오류율을 실시간으로 추적하고 이상 감지 |
| 규정 준수 & 감사 | 모든 AI 결정의 완전한 감사 추적으로 컴플라이언스 요건 충족 |

이 워크플로우의 핵심은 **트레이스-평가-개선의 지속적 사이클**입니다. 프로덕션 트레이스를 기반으로 평가 데이터셋을 구축하고, LLM 판정자(LLM Judge)가 품질을 자동으로 측정하며, 식별된 문제를 바탕으로 다음 버전을 개선하는 방식입니다. 이 사이클을 반복함으로써 GenAI 애플리케이션은 실제 사용 패턴에 맞게 지속적으로 품질이 향상됩니다.

---

## 지원 통합 목록

MLflow Tracing은 단 한 줄의 코드(`mlflow.<library>.autolog()`)로 다음 라이브러리와 프레임워크를 자동 계측합니다:

다음 표는 현재 지원되는 주요 통합 목록입니다:

| 카테고리 | 지원 라이브러리 |
|----------|-----------------|
| LLM 프로바이더 | OpenAI, Anthropic, AWS Bedrock, Databricks Foundation Models |
| 오케스트레이션 | LangChain, LangGraph, LlamaIndex, DSPy |
| 멀티 에이전트 | AutoGen, CrewAI |
| 임베딩 & 검색 | OpenAI Embeddings, Cohere |
| 커스텀 로직 | `@mlflow.trace` 데코레이터 (모든 Python 코드) |

각 통합은 해당 라이브러리의 고유한 동작 방식을 이해하고 최적화된 방식으로 스팬을 생성합니다. 예를 들어 LangGraph 통합은 에이전트 그래프의 노드 순회 경로를 시각화하고, LlamaIndex 통합은 청크 검색과 재순위 결과를 별도의 스팬으로 분리합니다.

---

## 실전 예시: RAG 애플리케이션 트레이싱

RAG (Retrieval-Augmented Generation) 파이프라인은 MLflow Tracing의 가치를 가장 잘 보여주는 사례입니다. 검색 품질과 생성 품질이 모두 최종 응답에 영향을 미치기 때문에, 어느 단계가 문제인지 파악하는 것이 중요합니다.

```python
import mlflow
from mlflow.entities import SpanType
from openai import OpenAI
import numpy as np

mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/rag-pipeline-tracing")
mlflow.openai.autolog()

client = OpenAI()

@mlflow.trace(span_type=SpanType.CHAIN, name="rag_pipeline")
def rag_pipeline(question: str) -> str:
    """RAG 파이프라인 전체를 하나의 트레이스로 기록"""
    # 검색 단계
    retrieved_docs = retrieve_documents(question)

    # 프롬프트 구성 단계
    context = format_context(retrieved_docs)

    # 생성 단계 (자동으로 mlflow.openai.autolog()가 추적)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"다음 컨텍스트를 바탕으로 질문에 답하세요:\n\n{context}"
            },
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

@mlflow.trace(span_type=SpanType.RETRIEVER, name="vector_retrieval")
def retrieve_documents(query: str) -> list:
    """벡터 검색 단계를 별도 스팬으로 추적"""
    # 실제 벡터 DB 검색 로직 (예시)
    results = [
        {"content": "MLflow는 머신러닝 라이프사이클 관리 플랫폼입니다.", "score": 0.95},
        {"content": "MLflow Tracing은 GenAI 관측성을 제공합니다.", "score": 0.92},
    ]
    return results

@mlflow.trace(name="format_context")
def format_context(docs: list) -> str:
    """검색 결과 포매팅을 별도 스팬으로 추적"""
    return "\n".join([f"- {doc['content']}" for doc in docs])

# 실행
answer = rag_pipeline("MLflow Tracing이란 무엇인가요?")
print(answer)
```

위 코드를 실행하면 MLflow UI에서 다음과 같은 계층적 트레이스를 확인할 수 있습니다:

- `rag_pipeline` (전체 파이프라인)
  - `vector_retrieval` (검색 단계: 지연 시간, 반환된 문서 수)
  - `format_context` (포매팅 단계)
  - `openai.chat.completions` (LLM 호출: 토큰 수, 모델 파라미터)

이 구조를 통해 응답 품질이 낮을 때 검색 단계의 문제인지, 프롬프트 구성의 문제인지, 아니면 LLM 자체의 문제인지를 즉시 파악할 수 있습니다.

---

## Genie Code와의 통합: 자연어로 트레이스 분석

MLflow Tracing은 Databricks의 **Genie Code** 와 통합되어, 수집된 트레이스 데이터를 자연어로 분석할 수 있게 합니다.

프로덕션에서 수천 개의 트레이스가 쌓이면, 특정 패턴을 찾기 위해 각 트레이스를 수동으로 검토하는 것은 불가능합니다. Genie Code를 통해 다음과 같이 자연어로 질문할 수 있습니다:

- "지난 24시간 동안 평균 지연 시간이 5초를 초과한 트레이스를 모두 보여줘"
- "검색 단계에서 오류가 발생한 트레이스의 비율은 얼마야?"
- "토큰 비용이 가장 높은 상위 10개 트레이스를 찾아줘"

이를 통해 엔지니어가 아닌 비즈니스 이해관계자나 도메인 전문가도 AI 시스템의 동작을 이해하고 품질 문제를 식별할 수 있습니다.

---

## 보안 모범 사례

MLflow Tracing을 프로덕션에서 사용할 때는 다음 보안 지침을 따르는 것이 중요합니다.

{% hint style="warning" %}
**API 키를 절대 코드에 하드코딩하지 마세요.** 트레이스에는 LLM 호출의 전체 입력/출력이 포함되므로, API 키가 노출되면 심각한 보안 문제가 발생할 수 있습니다.
{% endhint %}

안전한 자격증명 관리를 위해 Databricks Secrets를 사용하는 방법은 다음과 같습니다:

```python
import mlflow
from databricks.sdk import WorkspaceClient

# Databricks Secrets를 통한 안전한 자격증명 관리
w = WorkspaceClient()
api_key = w.dbutils.secrets.get(scope="llm-secrets", key="openai-api-key")

import os
os.environ["OPENAI_API_KEY"] = api_key

mlflow.openai.autolog()
```

또한 Databricks AI Gateway를 통해 LLM API를 호출하면 중앙화된 자격증명 관리와 비용 추적이 가능합니다.

---

## MLflow Tracing vs. 기존 관측성 도구

MLflow Tracing이 Jaeger, Zipkin, Datadog APM 등 기존 분산 추적 도구와 어떻게 다른지 살펴보겠습니다.

다음 비교 표는 GenAI 워크로드 관점에서의 주요 차이점을 정리한 것입니다:

| 기능 | MLflow Tracing | 일반 APM/분산 추적 |
|------|----------------|-------------------|
| GenAI 라이브러리 자동 계측 | 20+ 라이브러리 지원 | 제한적 또는 없음 |
| LLM 토큰 비용 추적 | 기본 제공 | 별도 구현 필요 |
| 프롬프트/응답 기록 | 구조화된 방식으로 저장 | 일반 로그로만 처리 |
| 평가 데이터셋 구축 | 트레이스에서 직접 생성 | 불가능 |
| LLM 판정자(Judge) 통합 | MLflow Evaluate와 네이티브 통합 | 없음 |
| 버전 추적 | 코드/프롬프트/모델 버전과 연결 | 제한적 |
| Unity Catalog 거버넌스 | 네이티브 통합 | 없음 |
| 오픈소스 | 완전 오픈소스 | 대부분 독점 |

MLflow Tracing이 기존 도구보다 GenAI 특화 기능에서 압도적으로 앞서는 이유는, GenAI 관측성의 핵심 요구사항이 전통적인 분산 추적과 본질적으로 다르기 때문입니다. 단순한 지연 시간이나 오류율 추적을 넘어, 프롬프트 품질, 검색 관련성, 응답 정확성을 함께 측정해야 합니다. MLflow Tracing은 이 두 세계를 단일 플랫폼에서 통합합니다.

---

## 시작하기

MLflow Tracing을 시작하는 가장 빠른 방법은 다음과 같습니다:

**1단계: 패키지 설치**

```bash
pip install mlflow[databricks]>=3.1 openai>=1.0.0
```

**2단계: 실험 설정 및 자동 트레이싱 활성화**

```python
import mlflow

mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/my-genai-experiment")
mlflow.openai.autolog()  # 또는 mlflow.langchain.autolog() 등
```

**3단계: 애플리케이션 실행 및 트레이스 확인**

코드를 실행하면 Databricks Workspace의 MLflow Experiments UI에서 자동으로 트레이스가 생성된 것을 확인할 수 있습니다.

---

## 결론

MLflow Tracing은 GenAI 애플리케이션 개발의 핵심 인프라입니다. 단순한 디버깅 도구를 넘어, 개발-평가-프로덕션 모니터링-지속적 개선으로 이어지는 전체 AI 애플리케이션 라이프사이클을 지원하는 관측성 플랫폼입니다.

OpenTelemetry 표준 기반으로 구축되어 벤더 중립적이며, 20개 이상의 GenAI 라이브러리를 자동 계측하고, Unity Catalog와 통합된 엔터프라이즈 거버넌스를 제공합니다. MLflow Tracing을 도입함으로써 팀은 더 이상 블랙박스로 동작하는 AI 시스템을 막연히 운영하는 대신, 데이터 기반으로 품질을 측정하고 지속적으로 개선할 수 있게 됩니다.

---

## 관련 자료

- [MLflow Tracing 공식 문서 (Databricks)](https://docs.databricks.com/aws/en/mlflow3/genai/tracing)
- [MLflow 3.0 블로그 포스트](https://www.databricks.com/blog/mlflow-30-unified-ai-experimentation-observability-and-governance)
- [자동 트레이싱 가이드](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/app-instrumentation/automatic)
- [MLflow Tracing 통합 목록](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/)
- [프로덕션 트레이싱 배포 가이드](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/prod-tracing)
- [Managed MLflow 제품 페이지](https://www.databricks.com/product/managed-mlflow)
