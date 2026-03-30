# RAG 체인 구축

이 장에서는 LangChain과 Databricks를 통합하여 검색-증강-생성 체인을 구축하는 방법을 다룹니다.

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

RAG 체인에서 프롬프트 설계는 답변 품질에 직접적인 영향을 줍니다.

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

## 다음 단계

체인이 구축되면 [RAG 평가](evaluation.md)에서 품질을 측정하고 개선합니다.
