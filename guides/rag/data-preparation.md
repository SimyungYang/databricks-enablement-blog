# 데이터 준비

RAG 시스템의 품질은 데이터 준비 단계에서 결정됩니다. 이 장에서는 문서 수집부터 Delta Table 저장까지의 전체 과정을 다룹니다.

## 1. 문서 수집

Databricks에서 원본 문서를 수집하는 주요 방법입니다.

### UC Volumes (권장)

```python
# UI: Catalog > Volumes > Upload Files
# CLI: databricks fs cp ./documents/ dbfs:/Volumes/catalog/schema/docs/ --recursive
```

### 클라우드 스토리지 (S3 / ADLS)

```python
df = spark.read.format("binaryFile") \
    .option("pathGlobFilter", "*.pdf") \
    .load("s3://my-bucket/documents/")  # External Location 설정 필요
```

### REST API를 통한 수집

```python
import requests
docs = requests.get("https://api.example.com/documents").json()
spark.createDataFrame(docs).write.mode("overwrite").saveAsTable("catalog.schema.raw_documents")
```

{% hint style="info" %}
UC Volumes 사용을 권장합니다. Unity Catalog의 거버넌스(접근 제어, 감사 로그, 리니지)가 자동 적용됩니다.
{% endhint %}

## 2. 문서 파싱

### ai_parse_document (Databricks 내장, 권장)

```python
from pyspark.sql.functions import col

# ai_parse_document으로 PDF/이미지/Office 문서 파싱
parsed_df = spark.sql("""
    SELECT
        path,
        ai_parse_document(content, 'markdown') AS parsed_text
    FROM read_files(
        '/Volumes/catalog/schema/docs/',
        format => 'binaryFile'
    )
""")
```

### PyPDF (Python 라이브러리)

```python
from pypdf import PdfReader

def parse_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join([page.extract_text() for page in reader.pages])
```

{% hint style="warning" %}
`ai_parse_document`는 테이블, 이미지 포함 문서도 정확하게 파싱합니다. 복잡한 레이아웃의 PDF라면 이 함수를 우선 사용하세요.
{% endhint %}

## 3. 청킹 전략

텍스트를 적절한 크기의 조각(청크)으로 분할하는 것은 RAG 품질에 직접적인 영향을 줍니다.

### Fixed-size Chunking (고정 크기)

```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separator="\n"
)
chunks = splitter.split_text(document_text)
```

### Recursive Chunking (재귀적 분할, 권장)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " "]
)
chunks = splitter.split_text(document_text)
```

### Semantic Chunking (의미 기반)

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import DatabricksEmbeddings

embeddings = DatabricksEmbeddings(endpoint="databricks-gte-large-en")
splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
chunks = splitter.create_documents([document_text])
```

### 청크 사이즈 가이드

| 청크 크기 | 특징 | 적합한 케이스 |
|-----------|------|-------------|
| 256 토큰 | 정밀한 검색, 맥락 부족 가능 | FAQ, 짧은 정의 |
| **512~1024 토큰**| **균형 잡힌 선택 (권장)**| **일반 문서, 기술 문서**|
| 2048 토큰 | 풍부한 맥락, 검색 정확도 저하 가능 | 긴 서술형 문서 |

{% hint style="success" %}
**권장 설정**: `chunk_size=1000`, `chunk_overlap=200` (Recursive 방식). 대부분의 기술 문서에서 좋은 성능을 보입니다.
{% endhint %}

## 4. Delta Table로 저장

```python
import pandas as pd

chunk_data = [{"chunk_id": f"doc_{d}_chunk_{i}", "content": c, "source": doc_sources[d]}
              for d, doc_chunks in enumerate(all_chunks) for i, c in enumerate(doc_chunks)]

chunks_df = spark.createDataFrame(pd.DataFrame(chunk_data))

# Delta Table로 저장 (Change Data Feed 활성화 필수)
chunks_df.write.format("delta") \
    .option("delta.enableChangeDataFeed", "true") \
    .mode("overwrite").saveAsTable("catalog.schema.document_chunks")
```

{% hint style="danger" %}
Vector Search Delta Sync Index를 사용하려면 소스 테이블에 **Change Data Feed**가 반드시 활성화되어야 합니다. 테이블 생성 시 `delta.enableChangeDataFeed = true` 옵션을 잊지 마세요.
{% endhint %}

## 다음 단계

데이터가 Delta Table에 저장되었으면, [Vector Search 설정](vector-search.md)으로 진행하여 임베딩 인덱스를 생성합니다.
