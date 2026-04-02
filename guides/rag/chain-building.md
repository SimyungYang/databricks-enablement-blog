# RAG 체인 구축

이 장에서는 LangChain과 Databricks를 통합하여 검색-증강-생성 체인을 구축하는 방법을 다룹니다.

## RAG 체인 아키텍처 이해

RAG 체인은 크게 **세 가지 핵심 컴포넌트** 로 구성됩니다. 각 컴포넌트의 역할과 연결 방식을 이해하면 체인 설계와 디버깅이 수월해집니다.

```
[사용자 질문]
     │
     ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Retriever  │ → │   Augmenter  │ → │  Generator  │
│ (검색기)     │    │ (증강기)      │    │ (생성기)     │
│             │    │              │    │             │
│ Vector Search   │  프롬프트에     │    │ LLM이 답변   │
│ 에서 관련 청크  │  검색 결과를    │    │ 생성         │
│ 검색           │  주입           │    │             │
└─────────────┘    └──────────────┘    └─────────────┘
```

| 컴포넌트 | 역할 | Databricks 구현 | 품질 영향도 |
|----------|------|----------------|-----------|
| **Retriever** | 관련 문서 검색 | DatabricksVectorSearch, EnsembleRetriever | 매우 높음 (60%) |
| **Augmenter** | 프롬프트 설계 + 컨텍스트 포매팅 | ChatPromptTemplate, format_docs | 높음 (25%) |
| **Generator** | 최종 답변 생성 | ChatDatabricks (Foundation Model API) | 중간 (15%) |

{% hint style="info" %}
RAG 품질 문제의 대부분은 **Retriever 단계** 에서 발생합니다. 답변이 부정확하다면 LLM을 바꾸기 전에 검색 결과의 품질을 먼저 점검하세요. MLflow Tracing으로 각 단계의 입출력을 확인할 수 있습니다.
{% endhint %}

### LCEL (LangChain Expression Language)이란?

LangChain Expression Language(LCEL)는 체인의 각 컴포넌트를 **파이프(`|`) 연산자** 로 연결하는 선언적 체인 구성 방식입니다. LCEL의 핵심 장점은 다음과 같습니다:

- **스트리밍 지원**: `chain.stream()`으로 토큰 단위 스트리밍이 자동 지원됩니다
- **비동기 지원**: `chain.ainvoke()`로 비동기 실행이 가능합니다
- **배치 처리**: `chain.batch()`로 여러 입력을 병렬 처리할 수 있습니다
- **트레이싱 호환**: MLflow Tracing과 자동으로 통합됩니다

### Databricks Agent Framework와의 통합

Databricks Agent Framework는 RAG 체인을 **프로덕션 서비스** 로 전환하기 위한 표준 인터페이스를 제공합니다.

- **ChatAgent 인터페이스**: `predict()` 메서드 하나로 Model Serving, Review App, MLflow Tracing과 호환
- **agents.deploy()**: 한 줄의 코드로 서빙 엔드포인트 + Review App + 피드백 테이블 생성
- **의존성 자동 관리**: RAG 체인이 참조하는 Vector Search 인덱스, Model Serving 엔드포인트 등의 의존성을 자동 추적

```python
# Agent Framework 통합의 핵심: ChatAgent 인터페이스
# 이 인터페이스를 구현하면 Databricks 생태계 전체와 호환됩니다
from mlflow.pyfunc import ChatAgent

class MyRAGAgent(ChatAgent):
    def predict(self, messages, context=None, custom_inputs=None):
        # 여기에 RAG 로직 구현
        pass
```

## 1. 필수 패키지 설치

```python
%pip install langchain langchain-community databricks-vectorsearch mlflow
dbutils.library.restartPython()
```

## 2. 핵심 구성 요소

### ChatDatabricks (Foundation Model API)

```python
from langchain_community.chat_models import ChatDatabricks

llm = ChatDatabricks(
    endpoint="databricks-meta-llama-3-3-70b-instruct",
    temperature=0.1, max_tokens=1024
)
response = llm.invoke("Databricks란 무엇인가요?")
```

### DatabricksVectorSearch Retriever

Vector Search 인덱스를 LangChain Retriever로 래핑합니다.

```python
from databricks.vector_search.client import VectorSearchClient
from langchain_community.vectorstores import DatabricksVectorSearch

client = VectorSearchClient()
index = client.get_index(endpoint_name="rag-vs-endpoint",
                          index_name="catalog.schema.document_chunks_index")

retriever = DatabricksVectorSearch(
    index=index, text_column="content", columns=["chunk_id", "content", "source"]
).as_retriever(search_kwargs={"k": 5})

docs = retriever.invoke("Vector Search 설정 방법")
```

{% hint style="info" %}
`search_kwargs`에서 `k` 값은 검색할 문서 수입니다. 너무 크면 컨텍스트가 길어져 비용이 증가하고, 너무 작으면 관련 정보를 놓칠 수 있습니다. 3~5개가 적절합니다.
{% endhint %}

## 3. Prompt Template 설계

RAG 체인에서 프롬프트 설계는 답변 품질에 직접적인 영향을 줍니다. 프롬프트는 LLM에게 **"어떻게 행동해야 하는가" ** 를 지시하는 설계도입니다.

### 프롬프트 설계가 생성 품질에 미치는 영향

프롬프트의 각 요소가 RAG 답변 품질에 미치는 영향을 구체적으로 살펴봅니다.

| 프롬프트 요소 | 없을 때의 문제 | 포함 시 효과 |
|-------------|--------------|-------------|
| **"컨텍스트만 사용하라" ** | LLM이 자체 지식으로 답변 → 환각 발생 | Faithfulness 지표 20~30% 향상 |
| **출처 명시 지시** | 답변의 근거를 알 수 없음 | 사용자 신뢰도 향상, 감사 추적 가능 |
| **응답 언어 지정** | 한영 혼용 답변 | 일관된 한국어 답변 |
| **"모른다고 말하라" ** | 모르는 내용도 답변 시도 → 환각 | 환각 50%+ 감소 |
| **응답 형식 지정** | 장황하거나 비구조적 답변 | 일관되고 읽기 쉬운 답변 |

### 프롬프트 안티 패턴

```python
# 나쁜 예: 지시가 모호하고 환각 방지 장치가 없음
bad_prompt = "다음 컨텍스트를 참고해서 답변해줘: {context}\n질문: {question}"

# 좋은 예: 명확한 역할, 제약 조건, 출력 형식 지정
good_prompt = """당신은 Databricks 기술 문서를 기반으로 답변하는 도우미입니다.

규칙:
- 제공된 컨텍스트 정보만을 사용하여 답변하세요.
- 컨텍스트에 없는 내용은 "해당 정보를 찾을 수 없습니다"라고 답변하세요.
- 답변에 출처 문서를 명시하세요.
- 한국어로 답변하세요.

컨텍스트:
{context}"""
```

### 실전 프롬프트 설계

```python
from langchain_core.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """당신은 Databricks 기술 문서를 기반으로 답변하는 도우미입니다.

규칙:
- 제공된 컨텍스트 정보만을 사용하여 답변하세요.
- 컨텍스트에 없는 내용은 "해당 정보를 찾을 수 없습니다"라고 답변하세요.
- 답변에 출처 문서를 명시하세요.
- 한국어로 답변하세요.

컨텍스트:
{context}"""),
    ("human", "{question}")
])
```

{% hint style="warning" %}
프롬프트에 "컨텍스트에 없는 내용은 답변하지 마라"는 지시를 반드시 포함하세요. 이것이 LLM의 환각(Hallucination)을 줄이는 핵심 방법입니다.
{% endhint %}

## 4. RAG 체인 조립

### LCEL (LangChain Expression Language) 방식

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def format_docs(docs):
    return "\n\n---\n\n".join([
        f"[출처: {doc.metadata.get('source', 'N/A')}]\n{doc.page_content}"
        for doc in docs
    ])

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt_template
    | llm
    | StrOutputParser()
)

# 체인 실행
answer = rag_chain.invoke("Databricks에서 Vector Search Index를 생성하는 방법은?")
print(answer)
```

### ChatAgent 클래스 방식 (배포용 권장)

```python
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatAgentResponse

class DatabricksRAGAgent(ChatAgent):
    def __init__(self):
        self.llm = ChatDatabricks(endpoint="databricks-meta-llama-3-3-70b-instruct", temperature=0.1)
        client = VectorSearchClient()
        index = client.get_index(endpoint_name="rag-vs-endpoint",
                                  index_name="catalog.schema.document_chunks_index")
        self.retriever = DatabricksVectorSearch(
            index=index, text_column="content", columns=["chunk_id", "content", "source"]
        ).as_retriever(search_kwargs={"k": 5})

    def predict(self, messages, context=None, custom_inputs=None):
        question = messages[-1]["content"]
        docs = self.retriever.invoke(question)
        ctx = "\n\n".join([d.page_content for d in docs])
        prompt = prompt_template.invoke({"context": ctx, "question": question})
        response = self.llm.invoke(prompt)
        return ChatAgentResponse(
            messages=[ChatAgentMessage(role="assistant", content=response.content)]
        )
```

## 5. MLflow로 체인 로깅

```python
import mlflow
mlflow.set_registry_uri("databricks-uc")

with mlflow.start_run(run_name="rag-chain-v1"):
    model_info = mlflow.pyfunc.log_model(
        artifact_path="rag_chain",
        python_model=DatabricksRAGAgent(),
        input_example={"messages": [{"role": "user", "content": "Vector Search란?"}]},
        registered_model_name="catalog.schema.rag_agent"
    )
print(f"모델 URI: {model_info.model_uri}")
```

{% hint style="success" %}
`ChatAgent` 인터페이스를 사용하면 Model Serving, Review App, MLflow Tracing과 자동으로 호환됩니다.
{% endhint %}

## 6. RAG 체인 디버깅 팁

### MLflow Tracing으로 병목 찾기

RAG 체인에서 문제가 발생하면, MLflow Tracing으로 각 단계의 입출력과 소요 시간을 확인할 수 있습니다.

```python
import mlflow
mlflow.langchain.autolog()  # LangChain 체인 자동 트레이싱

# 체인 실행 시 각 스팬이 자동 기록됨
# - retriever: 검색된 문서 목록, 소요 시간
# - prompt: 최종 프롬프트 내용
# - llm: LLM 입력/출력, 토큰 수, 소요 시간
answer = rag_chain.invoke("Vector Search 인덱스 유형을 설명해주세요")
```

### 일반적인 문제와 해결 방법

| 증상 | 원인 | 디버깅 방법 | 해결 |
|------|------|-----------|------|
| **답변이 부정확** | 검색 결과에 관련 문서 없음 | Tracing에서 retriever 출력 확인 | 청킹 전략 변경, k값 증가 |
| **환각 발생** | LLM이 컨텍스트를 무시 | Tracing에서 prompt 내용 확인 | 프롬프트에 "컨텍스트만 사용" 강조 |
| **응답 시간 느림** | LLM 추론 시간 과다 | Tracing에서 각 스팬 소요 시간 확인 | 더 빠른 모델 사용, 컨텍스트 길이 축소 |
| **"정보를 찾을 수 없습니다" ** | 검색 결과 빈 배열 | Vector Search 인덱스 상태 확인 | 인덱스 동기화 실행, 임베딩 모델 확인 |

{% hint style="tip" %}
MLflow Tracing은 프로덕션 환경에서도 활성화하세요. 문제 발생 시 특정 요청의 전체 실행 경로를 재현할 수 있어 디버깅이 훨씬 수월해집니다.
{% endhint %}

## 다음 단계

체인이 구축되면 [RAG 평가](evaluation.md)에서 품질을 측정하고 개선합니다.
