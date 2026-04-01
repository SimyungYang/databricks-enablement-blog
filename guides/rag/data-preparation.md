# 데이터 준비

RAG 시스템의 품질은 데이터 준비 단계에서 결정됩니다. 이 장에서는 문서 수집부터 Delta Table 저장까지의 전체 과정을 다룹니다.

## 데이터 전처리가 RAG 품질의 70%를 결정하는 이유

RAG 시스템의 성능 병목은 대부분 **LLM이 아니라 데이터 품질** 에 있습니다. 아무리 뛰어난 임베딩 모델과 검색 알고리즘을 사용하더라도, 입력 데이터가 부정확하거나 노이즈가 많으면 최종 답변 품질은 낮아질 수밖에 없습니다.

### "Garbage In, Garbage Out" — RAG 버전

| 데이터 품질 문제 | RAG에 미치는 영향 | 해결 방법 |
|-----------------|-------------------|-----------|
| ** 깨진 PDF 파싱**| 텍스트가 누락되거나 순서가 뒤바뀜 | `ai_parse_document` 사용, OCR 품질 검증 |
| ** 중복 문서**| 검색 결과에 동일 내용 반복 | 문서 해시 기반 중복 제거 |
| ** 오래된 문서**| 폐기된 정책이 답변에 포함 | 문서 버전 관리, 유효 기간 메타데이터 |
| ** 헤더/푸터 노이즈**| 페이지 번호, 회사명 등이 청크에 포함 | 파싱 후 정규식 기반 노이즈 제거 |
| ** 테이블 데이터 손실**| 표 형태 정보가 일반 텍스트로 변환 | Markdown 테이블 형식으로 보존 |
| ** 이미지 내 텍스트**| OCR 미적용 시 텍스트 누락 | `ai_parse_document`의 OCR 기능 활용 |

{% hint style="warning" %}
실제 프로젝트에서 RAG 품질 개선에 투입하는 시간의 60~70%는 데이터 전처리에 할당됩니다. 모델이나 검색 알고리즘을 바꾸기 전에, 먼저 데이터 품질을 점검하세요.
{% endhint %}

### 데이터 품질 체크리스트

프로덕션 RAG 시스템 구축 전에 반드시 확인해야 할 항목입니다:

- [ ] 모든 문서가 정상적으로 파싱되었는가? (빈 텍스트, 깨진 인코딩 확인)
- [ ] 중복 문서가 제거되었는가? (동일 내용의 다른 버전)
- [ ] 문서의 최신 상태가 반영되었는가? (폐기된 문서 제외)
- [ ] 헤더/푸터/워터마크 등 노이즈가 제거되었는가?
- [ ] 테이블, 목록 등 구조화된 데이터가 적절히 보존되었는가?
- [ ] 메타데이터(출처, 날짜, 카테고리)가 정확히 추출되었는가?
- [ ] 인코딩이 통일되었는가? (UTF-8 권장)

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

### 문서 포맷별 처리 전략

각 문서 포맷에는 고유한 과제가 있습니다. 포맷별 최적의 파싱 전략을 선택해야 합니다.

| 포맷 | 주요 과제 | 권장 파싱 방법 | 주의사항 |
|------|-----------|---------------|----------|
| **PDF**| 레이아웃 복잡, 테이블/이미지 혼재 | `ai_parse_document` (Markdown 출력) | 스캔 PDF는 OCR 품질에 의존 |
| **Word (.docx)**| 스타일, 표, 차트 포함 | `python-docx` + 구조 보존 | 차트/그래프는 텍스트로 변환 불가 |
| **HTML**| 태그 노이즈, 스크립트 포함 | `BeautifulSoup` + 본문 추출 | 광고, 네비게이션 등 비본문 제거 필수 |
| **Markdown**| 구조가 명확 | `MarkdownHeaderTextSplitter` | 헤딩 기반 분할로 구조 보존 가능 |
| **CSV/Excel**| 행-열 구조, 수치 데이터 | 행 단위 텍스트 변환 + 컬럼명 포함 | 수치 데이터는 자연어 설명 추가 권장 |
| **JSON/XML**| 중첩 구조 | 구조별 텍스트 병합 | 키-값 쌍을 자연어 문장으로 변환 |
| ** 이미지 (PNG/JPG)**| 텍스트 직접 추출 불가 | `ai_parse_document` OCR | 이미지 품질이 OCR 정확도에 직결 |

### PDF 파싱 상세: ai_parse_document의 작동 원리

`ai_parse_document`는 Databricks에서 제공하는 AI 기반 문서 파서로, 단순 텍스트 추출을 넘어 ** 문서의 구조를 이해** 합니다.

```python
# ai_parse_document의 주요 장점
# 1. 레이아웃 인식: 다단 레이아웃에서도 올바른 읽기 순서 유지
# 2. 테이블 추출: 표를 Markdown 테이블 형식으로 변환
# 3. OCR 내장: 스캔된 문서도 텍스트 추출 가능
# 4. 이미지 설명: 이미지에 대한 텍스트 설명 생성

# 다양한 출력 포맷 지원
parsed_md = spark.sql("""
    SELECT path, ai_parse_document(content, 'markdown') AS parsed_text
    FROM read_files('/Volumes/catalog/schema/docs/', format => 'binaryFile')
""")

# JSON 형태로 구조화된 출력도 가능
parsed_json = spark.sql("""
    SELECT path, ai_parse_document(content, 'json') AS parsed_json
    FROM read_files('/Volumes/catalog/schema/docs/', format => 'binaryFile')
""")
```

### 메타데이터 추출의 중요성

메타데이터는 검색 시 ** 필터링** 과 ** 정밀도 향상** 에 핵심적인 역할을 합니다. 파싱 단계에서 최대한 많은 메타데이터를 추출해 두는 것이 좋습니다.

```python
import re
from datetime import datetime

def extract_metadata(file_path: str, parsed_text: str) -> dict:
    """파싱된 문서에서 메타데이터를 자동 추출"""
    metadata = {
        "source": file_path,
        "file_type": file_path.split(".")[-1].lower(),
        "parsed_at": datetime.now().isoformat(),
        "char_count": len(parsed_text),
        "word_count": len(parsed_text.split()),
    }

    # 문서 제목 추출 (첫 번째 헤딩)
    title_match = re.search(r'^#\s+(.+)', parsed_text, re.MULTILINE)
    if title_match:
        metadata["title"] = title_match.group(1).strip()

    # 날짜 패턴 추출 (YYYY-MM-DD 또는 YYYY.MM.DD)
    date_match = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', parsed_text)
    if date_match:
        metadata["document_date"] = date_match.group(1)

    # 카테고리 추론 (키워드 기반)
    text_lower = parsed_text.lower()
    if any(kw in text_lower for kw in ["정책", "규정", "지침"]):
        metadata["category"] = "policy"
    elif any(kw in text_lower for kw in ["api", "sdk", "코드", "함수"]):
        metadata["category"] = "technical"
    elif any(kw in text_lower for kw in ["faq", "자주 묻는"]):
        metadata["category"] = "faq"

    return metadata
```

{% hint style="tip" %}
메타데이터는 검색 품질을 높이는 ** 가장 비용 효율적인 방법** 입니다. 특히 `doc_type`, `created_at`, `department` 같은 필드는 Vector Search의 메타데이터 필터와 결합하여 검색 정밀도를 크게 향상시킵니다.
{% endhint %}

### 노이즈 제거 파이프라인

파싱 후 텍스트에는 다양한 노이즈가 포함될 수 있습니다. 체계적인 정제 파이프라인이 필요합니다.

```python
import re

def clean_parsed_text(text: str) -> str:
    """파싱된 텍스트에서 노이즈를 제거하는 정제 파이프라인"""

    # 1. 반복되는 헤더/푸터 제거 (페이지 번호, 회사명 등)
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'- \d+ -', '', text)  # 페이지 번호 패턴

    # 2. 과도한 공백 정리
    text = re.sub(r'\n{3,}', '\n\n', text)  # 3줄 이상 빈 줄 → 2줄로
    text = re.sub(r' {2,}', ' ', text)      # 연속 공백 → 단일 공백

    # 3. 특수 문자 정리 (유니코드 제어 문자 등)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

    # 4. URL 보존하되 트래킹 파라미터 제거
    text = re.sub(r'(\?utm_[^\s]+)', '', text)

    # 5. 빈 테이블 행 제거
    text = re.sub(r'\|[\s|]*\|', '', text)

    return text.strip()
```

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
| **512~1024 토큰**| ** 균형 잡힌 선택 (권장)**| ** 일반 문서, 기술 문서**|
| 2048 토큰 | 풍부한 맥락, 검색 정확도 저하 가능 | 긴 서술형 문서 |

{% hint style="success" %}
** 권장 설정**: `chunk_size=1000`, `chunk_overlap=200` (Recursive 방식). 대부분의 기술 문서에서 좋은 성능을 보입니다.
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
Vector Search Delta Sync Index를 사용하려면 소스 테이블에 **Change Data Feed** 가 반드시 활성화되어야 합니다. 테이블 생성 시 `delta.enableChangeDataFeed = true` 옵션을 잊지 마세요.
{% endhint %}

## 5. 데이터 파이프라인 자동화

프로덕션 환경에서는 문서 수집 → 파싱 → 청킹 → Delta Table 저장의 전체 과정을 ** 자동화** 해야 합니다. Databricks Jobs를 활용하여 새 문서가 추가될 때마다 파이프라인을 자동 실행할 수 있습니다.

### 증분 처리 패턴

매번 전체 문서를 재처리하는 것은 비효율적입니다. ** 새로 추가되거나 변경된 문서만** 처리하는 증분 패턴을 사용하세요.

```python
from pyspark.sql.functions import col, current_timestamp

# 마지막 처리 시점 이후에 추가/변경된 파일만 읽기
new_files = spark.sql(f"""
    SELECT path, content, modificationTime
    FROM read_files('/Volumes/catalog/schema/docs/', format => 'binaryFile')
    WHERE modificationTime > '{last_processed_time}'
""")

# 파싱 및 청킹 수행
# ... (기존 파싱/청킹 코드)

# 증분 저장 (append 모드)
new_chunks_df.write.format("delta") \
    .option("delta.enableChangeDataFeed", "true") \
    .mode("append").saveAsTable("catalog.schema.document_chunks")
```

{% hint style="tip" %}
증분 처리와 Delta Sync Index를 조합하면, 새 문서가 추가될 때마다 자동으로 임베딩이 계산되고 인덱스가 갱신됩니다. 이 패턴으로 ** 항상 최신 상태의 RAG 시스템** 을 유지할 수 있습니다.
{% endhint %}

## 다음 단계

데이터가 Delta Table에 저장되었으면, [Vector Search 설정](vector-search.md)으로 진행하여 임베딩 인덱스를 생성합니다.
