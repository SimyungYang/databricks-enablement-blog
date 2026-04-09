# Vector Search 설정

Databricks Vector Search는 서버리스 벡터 데이터베이스로, 임베딩 벡터의 저장/인덱싱/검색을 통합 제공합니다. HNSW 알고리즘 기반의 고성능 유사도 검색을 지원합니다.

## Vector Search의 핵심 개념

벡터 검색은 **텍스트를 수학적 공간의 점(벡터)으로 변환** 하여, 의미가 유사한 텍스트끼리 가까이 위치하도록 만드는 기술입니다. 전통적인 키워드 검색과 달리, "자동차"와 "차량"이 의미적으로 유사하다는 것을 이해할 수 있습니다.

### HNSW (Hierarchical Navigable Small World) 알고리즘

Databricks Vector Search는 **HNSW** 알고리즘을 사용합니다. 이 알고리즘이 선택된 이유를 이해하면 인덱스 튜닝에 도움이 됩니다.

- **계층적 그래프 구조**: 벡터들을 여러 계층의 그래프로 연결합니다. 상위 계층은 "고속도로"처럼 먼 거리를 빠르게 이동하고, 하위 계층은 "일반 도로"처럼 정밀하게 탐색합니다.
- **근사 최근접 이웃 (ANN)**: 정확한 최근접 이웃을 찾는 것이 아니라, 매우 높은 확률로 가장 유사한 벡터를 빠르게 찾습니다. 정확도는 99%+ 수준입니다.
- **시간 복잡도**: O(log N)으로, 벡터 수가 10배 증가해도 검색 시간은 소폭만 증가합니다.

| ANN 알고리즘 | 검색 속도 | 인덱스 빌드 속도 | 메모리 사용 | Databricks 지원 |
|-------------|----------|----------------|-----------|----------------|
| **HNSW** | 매우 빠름 | 보통 | 높음 | 기본 사용 |
| **IVF** | 빠름 | 빠름 | 낮음 | 미지원 |
| **Annoy** | 보통 | 빠름 | 보통 | 미지원 |

HNSW가 다른 ANN 알고리즘 대비 메모리 사용량이 높은 이유는 각 노드가 여러 계층에 걸쳐 연결 정보를 유지하기 때문입니다. 하지만 검색 속도와 정확도의 균형이 가장 우수하여, 대부분의 상용 벡터 DB(Pinecone, Weaviate, Qdrant 등)에서도 HNSW를 기본 알고리즘으로 채택하고 있습니다.

{% hint style="info" %}
Databricks Vector Search는 HNSW 알고리즘의 파라미터를 자동 최적화합니다. 사용자가 `ef_construction`이나 `M` 값을 직접 설정할 필요가 없으므로, 인덱스 유형과 임베딩 모델 선택에 집중하면 됩니다.
{% endhint %}

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
| **최대 벡터 수** | ~3.2억 (768차원) | 10억+ (768차원) |
| **인덱싱 속도** | 기본 | 10~20배 빠름 |
| **쿼리 지연** | 낮음 | ~250ms 추가 |
| **적합한 케이스** | 일반 RAG | 대규모 문서 컬렉션 |

{% hint style="info" %}
대부분의 RAG 사용 사례에서는 **Standard** 엔드포인트로 충분합니다. 워크스페이스당 최대 100개 엔드포인트, 엔드포인트당 최대 50개 인덱스를 생성할 수 있습니다.
{% endhint %}

## 2. Vector Search Index 유형

### Delta Sync Index (자동 동기화, 권장)

소스 Delta Table이 변경되면 인덱스가 **자동으로 동기화** 됩니다. 두 가지 임베딩 관리 방식이 있습니다.

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

Delta Sync Index와 달리, REST API로 직접 벡터를 삽입/업데이트합니다. 소스가 Delta Table이 아닌 경우(예: 외부 API에서 실시간으로 수집되는 데이터, 자체 임베딩 파이프라인이 있는 경우)에 적합합니다. 동기화 파이프라인이 없으므로 벡터의 추가/삭제를 애플리케이션 코드에서 직접 관리해야 합니다.

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

임베딩(embedding) 모델은 텍스트를 고정 길이의 숫자 벡터로 변환하는 모델입니다. 의미가 유사한 텍스트는 벡터 공간에서 가까운 위치에 배치되므로, 벡터 간 거리(코사인 유사도)를 계산하면 의미적 유사도를 측정할 수 있습니다. 모델 선택은 검색 품질에 직접적으로 영향을 미칩니다.

Foundation Model API에서 제공하는 임베딩 모델은 다음과 같습니다.

| 모델 | 차원 | 특징 |
|------|------|------|
| `databricks-gte-large-en` | 1024 | 영어 특화, MTEB 벤치마크 상위권, 의미 검색에 최적화 |
| `databricks-bge-large-en` | 1024 | 영어 특화, 범용적 용도에 적합 |

GTE(General Text Embeddings)와 BGE(BAAI General Embedding)는 모두 트랜스포머 기반 모델이며, 1024차원의 벡터를 생성합니다. **한국어 문서가 포함된 경우** 에는 다국어 임베딩 모델(예: `multilingual-e5-large`, 외부 모델 서빙 필요)이나 한국어 특화 모델을 Model Serving에 직접 배포하여 사용하는 것이 더 나은 검색 품질을 보일 수 있습니다. [한국어 RAG 최적화](korean-nlp.md) 가이드에서 자세히 다룹니다.

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

하이브리드 검색은 **벡터 유사도 검색** 과 **BM25 키워드 검색** 을 동시에 수행하고 결과를 병합합니다. 벡터 검색은 "자동차"와 "차량"의 의미적 유사성을 잡아내는 데 강하지만, 정확한 고유명사나 코드명 검색에는 약합니다. 반대로 키워드 검색은 정확한 용어 매칭에 강합니다. 두 방식을 결합하면 단독 사용 대비 검색 재현율(recall)이 10~20% 향상됩니다.

결과 병합에는 **RRF(Reciprocal Rank Fusion)** 알고리즘이 사용됩니다. RRF는 각 검색 방식에서 문서의 순위(rank)를 기반으로 점수를 계산합니다: `score = 1 / (k + rank)` (k는 상수, 보통 60). 두 검색 방식 모두에서 상위에 랭크된 문서가 가장 높은 점수를 받으며, 한쪽에서만 검색된 문서도 결과에 포함됩니다.

```python
results = index.similarity_search(
    query_text="Delta Lake ACID 트랜잭션",
    columns=["chunk_id", "content"],
    num_results=5,
    query_type="HYBRID"   # RRF로 결과 병합, 최대 200개
)
```

## 5. 인덱스 튜닝 가이드

### pipeline_type 선택

Delta Sync Index의 동기화 방식은 데이터 업데이트 빈도와 비용 허용 범위에 따라 선택합니다.

| 옵션 | 동기화 방식 | 비용 | 적합한 케이스 |
|------|-----------|------|-------------|
| **TRIGGERED** | 수동 트리거 또는 스케줄 | 낮음 | 배치 업데이트, 일 단위 갱신 |
| **CONTINUOUS** | 실시간 자동 동기화 | 높음 | 실시간 데이터, 자주 변경되는 문서 |

```python
# TRIGGERED: 수동으로 동기화 실행
index.sync()

# CONTINUOUS: 소스 테이블 변경 시 자동 동기화 (CDF 기반)
# pipeline_type="CONTINUOUS"로 생성 시 자동 활성화
```

{% hint style="tip" %}
대부분의 RAG 사용 사례에서는 **TRIGGERED** 모드로 충분합니다. 문서가 자주 변경되지 않는 경우 불필요한 CONTINUOUS 동기화 비용을 절약할 수 있습니다. 일 단위 갱신이면 Databricks Job으로 `index.sync()`를 스케줄링하세요.
{% endhint %}

### 인덱스 상태 모니터링

```python
# 인덱스 상태 확인
status = index.describe()
print(f"상태: {status.get('status', {}).get('ready')}")
print(f"벡터 수: {status.get('status', {}).get('num_rows')}")
print(f"마지막 동기화: {status.get('status', {}).get('last_sync_time')}")

# 동기화 진행 상황 확인 (TRIGGERED 모드)
sync_status = index.wait_until_ready(timeout=timedelta(minutes=30))
```

## 6. 비용 최적화 가이드

### Standard vs Storage-Optimized 선택 기준

| 기준 | Standard | Storage-Optimized |
|------|----------|-------------------|
| **문서 수** | < 100만 청크 | 100만+ 청크 |
| **쿼리 빈도** | 높음 (실시간 서빙) | 낮음~중간 (배치 검색) |
| **응답 시간 요구** | P95 < 200ms | P95 < 500ms 허용 |
| **비용 우선순위** | 성능 > 비용 | 비용 > 성능 |
| **인덱스 빌드** | 소규모 빠르게 | 대규모 효율적으로 |

### 비용 절감 팁

1. **불필요한 컬럼 제거**: 인덱스에 포함하는 컬럼(columns)을 최소화합니다. 검색에 필요한 컬럼만 포함하세요.
2. **Triggered Sync 사용**: Continuous 대신 Triggered를 사용하고, 필요할 때만 동기화합니다.
3. **임베딩 차원 최적화**: 1024차원 대신 768차원 모델을 사용하면 스토리지 비용이 25% 절감됩니다. 품질 차이가 미미한 경우가 많습니다.
4. **엔드포인트 통합**: 여러 인덱스를 하나의 엔드포인트에서 서빙합니다. 엔드포인트당 최대 50개 인덱스를 지원합니다.
5. **문서 수명 관리**: 더 이상 필요 없는 문서는 소스 테이블에서 삭제하여 인덱스 크기를 줄입니다.

{% hint style="warning" %}
Storage-Optimized 엔드포인트는 쿼리 지연이 약 250ms 추가되지만, 대규모 데이터셋에서 인덱싱 비용이 크게 절감됩니다. 10만 건 이하에서는 Standard가 비용 효율적이고, 100만 건 이상에서는 Storage-Optimized를 고려하세요.
{% endhint %}

## 다음 단계

Vector Search 인덱스가 준비되면, [RAG 체인 구축](chain-building.md)에서 검색 결과를 LLM과 연결하는 체인을 만듭니다.

## 참고 문서

- [Vector Search 공식 문서](https://docs.databricks.com/aws/en/generative-ai/vector-search/index.html)
- [Vector Search 가격 정책](https://www.databricks.com/product/pricing/vector-search)
- [Vector Search API 레퍼런스](https://docs.databricks.com/api/workspace/vectorsearchindexes)
