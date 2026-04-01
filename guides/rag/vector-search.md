# Vector Search 설정

Databricks Vector Search는 서버리스 벡터 데이터베이스로, 임베딩 벡터의 저장/인덱싱/검색을 통합 제공합니다. HNSW 알고리즘 기반의 고성능 유사도 검색을 지원합니다.

## 1. Vector Search Endpoint 생성

Vector Search Endpoint는 인덱스를 서빙하는 서버리스 컴퓨팅 리소스입니다.

```python
from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient()

# 서버리스 엔드포인트 생성
client.create_endpoint(
    name="rag-vs-endpoint",
    endpoint_type="STANDARD"  # 또는 "STORAGE_OPTIMIZED"
)
```

### 엔드포인트 유형 비교

| 항목 | Standard | Storage-Optimized |
|------|----------|-------------------|
| **최대 벡터 수**| ~3.2억 (768차원) | 10억+ (768차원) |
| **인덱싱 속도**| 기본 | 10~20배 빠름 |
| **쿼리 지연**| 낮음 | ~250ms 추가 |
| **적합한 케이스**| 일반 RAG | 대규모 문서 컬렉션 |

{% hint style="info" %}
대부분의 RAG 사용 사례에서는 **Standard**엔드포인트로 충분합니다. 워크스페이스당 최대 100개 엔드포인트, 엔드포인트당 최대 50개 인덱스를 생성할 수 있습니다.
{% endhint %}

## 2. Vector Search Index 유형

### Delta Sync Index (자동 동기화, 권장)

소스 Delta Table이 변경되면 인덱스가 **자동으로 동기화**됩니다. 두 가지 임베딩 관리 방식이 있습니다.

#### Databricks 관리 임베딩 (권장)

Databricks가 임베딩을 자동 계산합니다. 소스 텍스트 컬럼만 지정하면 됩니다.

```python
index = client.create_delta_sync_index(
    endpoint_name="rag-vs-endpoint",
    index_name="catalog.schema.document_chunks_index",
    source_table_name="catalog.schema.document_chunks",
    pipeline_type="TRIGGERED",  # "TRIGGERED" 또는 "CONTINUOUS"
    primary_key="chunk_id",
    embedding_source_column="content",
    embedding_model_endpoint_name="databricks-gte-large-en"
)
```

#### 자체 관리 임베딩

직접 계산한 임베딩 벡터 컬럼이 소스 테이블에 있는 경우:

```python
index = client.create_delta_sync_index(
    endpoint_name="rag-vs-endpoint",
    index_name="catalog.schema.document_chunks_index",
    source_table_name="catalog.schema.document_chunks",
    pipeline_type="TRIGGERED",
    primary_key="chunk_id",
    embedding_dimension=1024,
    embedding_vector_column="embedding"
)
```

### Direct Vector Access Index (수동 관리)

REST API로 직접 벡터를 삽입/업데이트합니다. 자동 동기화가 불필요한 경우에 사용합니다.

```python
index = client.create_direct_access_index(
    endpoint_name="rag-vs-endpoint",
    index_name="catalog.schema.direct_index",
    primary_key="chunk_id", embedding_dimension=1024,
    embedding_vector_column="embedding",
    schema={"chunk_id": "string", "content": "string",
            "embedding": "array<float>", "source": "string"}
)
```

{% hint style="success" %}
**권장**: Delta Sync Index + Databricks 관리 임베딩 조합. 임베딩 계산과 인덱스 동기화가 자동으로 처리되어 운영 부담이 최소화됩니다.
{% endhint %}

## 3. Embedding 모델 선택

Foundation Model API에서 제공하는 임베딩 모델:

| 모델 | 차원 | 특징 |
|------|------|------|
| `databricks-gte-large-en` | 1024 | 영어 특화, 고성능 |
| `databricks-bge-large-en` | 1024 | 영어 특화, 범용 |

```python
# Foundation Model API로 임베딩 직접 호출
import mlflow.deployments

deploy_client = mlflow.deployments.get_deploy_client("databricks")

response = deploy_client.predict(
    endpoint="databricks-gte-large-en",
    inputs={"input": ["Databricks Vector Search란 무엇인가요?"]}
)
embeddings = response.data[0]["embedding"]
print(f"임베딩 차원: {len(embeddings)}")  # 1024
```

## 4. 인덱스 쿼리

### 유사도 검색

```python
results = index.similarity_search(
    query_text="Databricks에서 RAG를 구축하는 방법은?",
    columns=["chunk_id", "content", "source"],
    num_results=5
)

for doc in results.get("result", {}).get("data_array", []):
    print(f"[{doc[0]}] {doc[1][:100]}...")
```

### 메타데이터 필터링

```python
results = index.similarity_search(
    query_text="보안 설정 방법",
    columns=["chunk_id", "content", "source"],
    filters={"source": "security_guide.pdf"},
    num_results=3
)
```

### 하이브리드 검색 (유사도 + 키워드)

```python
results = index.similarity_search(
    query_text="Delta Lake ACID 트랜잭션",
    columns=["chunk_id", "content"],
    num_results=5,
    query_type="HYBRID"   # Reciprocal Rank Fusion(RRF)으로 결과 병합, 최대 200개
)
```

## 다음 단계

Vector Search 인덱스가 준비되면, [RAG 체인 구축](chain-building.md)에서 검색 결과를 LLM과 연결하는 체인을 만듭니다.

## 참고 문서

- [Vector Search 공식 문서](https://docs.databricks.com/aws/en/generative-ai/vector-search/index.html)
