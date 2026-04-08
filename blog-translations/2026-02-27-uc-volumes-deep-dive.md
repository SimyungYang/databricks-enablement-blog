---
original_title: "Unity Catalog Volumes Deep Dive: Unstructured Data Management"
authors: "Databricks"
date: "2024-02-27"
category: "Data Governance"
original_url: "https://www.databricks.com/blog/unity-catalog-volumes-deep-dive-unstructured-data-management"
translated_date: "2026-04-07"
---

# Unity Catalog Volumes 심층 분석: 비정형 데이터 관리

> **원문**: [Unity Catalog Volumes Deep Dive: Unstructured Data Management](https://www.databricks.com/blog/unity-catalog-volumes-deep-dive-unstructured-data-management)

{% hint style="warning" %}
이 포스트의 원본 URL은 현재 접근이 불가한 상태입니다. 본 번역은 Databricks 공식 블로그의 Unity Catalog Volumes GA 발표(2024년 2월) 및 공식 문서를 기반으로 작성되었습니다.
{% endhint %}

---

{% hint style="info" %}
**요약**

- Unity Catalog Volumes는 테이블과 동일한 3단계 네임스페이스 구조 안에서 비정형·비테이블 데이터를 거버닝하는 객체입니다.
- Managed Volumes(관리형 볼륨)과 External Volumes(외부 볼륨) 두 가지 유형이 있으며, 각각 다른 스토리지 수명 주기와 액세스 패턴을 제공합니다.
- Auto Loader, Delta Live Tables, Delta Sharing과 통합되어 비정형 데이터에 대한 End-to-End 리니지 추적, 접근 제어, 데이터 공유가 가능합니다.
{% endhint %}

---

## Volumes란 무엇인가

Unity Catalog가 처음 등장했을 때, 그 거버넌스 체계는 주로 테이블, 즉 행과 열로 구성된 정형 데이터를 중심으로 설계되었습니다. 그런데 실제 데이터 플랫폼에서 다루는 데이터의 상당 부분은 테이블 형태가 아닙니다. 이미지, 동영상, 오디오, PDF, 로그 파일, 체크포인트 파일, Python 패키지(.whl), JAR 라이브러리, IoT 센서 원시 데이터 등 비정형·반정형 데이터는 클라우드 오브젝트 스토리지 어딘가에 흩어져 있지만, 통일된 거버넌스 없이 관리되어 왔습니다.

**Unity Catalog Volumes** 는 이 문제를 해결하기 위해 도입된 객체 유형입니다. Volumes는 클라우드 오브젝트 스토리지 위의 논리적 스토리지 단위로, 어떤 포맷의 파일이든 액세스·저장·거버닝·조직화할 수 있는 능력을 제공합니다. 테이블이 정형 데이터를 거버닝한다면, Volumes는 정형·반정형·비정형을 포함한 **모든 비테이블 데이터** 를 거버닝합니다.

Databricks는 비테이블 데이터에 대한 모든 액세스를 관리하기 위해 Volumes를 사용하도록 권장하고 있습니다.

---

## Unity Catalog 3단계 네임스페이스에서의 위치

Volumes는 Unity Catalog의 3단계 네임스페이스 구조(`catalog.schema.volume`)에서 세 번째 레벨에 위치합니다. 이는 테이블과 동일한 계층 구조이므로, 기존에 Unity Catalog를 사용하던 팀이라면 익숙한 패턴으로 Volumes를 다룰 수 있습니다.

볼륨 내 파일에 접근하는 경로 형식은 다음과 같습니다.

```
/Volumes/<catalog>/<schema>/<volume>/<path>/<file-name>
```

Apache Spark와 함께 사용할 때는 `dbfs:/` 스킴도 지원됩니다.

```
dbfs:/Volumes/<catalog>/<schema>/<volume>/<path>/<file-name>
```

이 경로의 `/<catalog>/<schema>/<volume>` 부분은 Unity Catalog가 자동으로 관리하는 읽기 전용 디렉토리입니다. 파일시스템 명령어로는 직접 생성하거나 삭제할 수 없습니다.

이 표준화된 경로 체계는 중요한 의미를 갖습니다. Apache Spark, SQL, Python, PySpark, Databricks CLI, REST API 등 어떤 인터페이스를 사용하더라도 동일한 경로로 파일에 접근할 수 있기 때문입니다. 과거처럼 DBFS 경로(`dbfs:/mnt/...`)나 클라우드 네이티브 URI(`s3://`, `abfss://`) 사이에서 혼란을 겪을 필요가 없어집니다.

---

## Volumes의 두 가지 유형: Managed vs External

Volumes는 크게 두 가지 유형으로 구분됩니다. 스토리지 위치, 데이터 수명 주기, 액세스 제어 방식에서 차이가 있으며, 어떤 유형을 선택하느냐에 따라 운영 방식이 달라집니다.

아래 표는 두 유형의 핵심 차이점을 정리한 것입니다.

| 항목 | Managed Volumes | External Volumes |
|---|---|---|
| **스토리지 위치** | UC가 관리하는 스키마 스토리지 내부에 생성 | 기존 클라우드 오브젝트 스토리지 경로에 등록 |
| **데이터 수명 주기** | UC가 레이아웃과 삭제를 관리 (삭제 시 7일 보존) | 볼륨을 Drop해도 데이터는 클라우드 스토리지에 그대로 유지 |
| **액세스 제어** | 모든 액세스가 UC를 통해 이루어짐 | UC가 거버닝하지만, 외부 도구는 직접 URI로도 접근 가능 |
| **마이그레이션 필요 여부** | 불필요 | 불필요 - 기존 스토리지 경로를 그대로 사용 |
| **주요 사용 사례** | Databricks 전용 워크로드의 가장 간단한 선택 | Databricks와 외부 시스템이 함께 접근하는 혼합 워크로드 |

Managed Volumes와 External Volumes는 Databricks 도구, UI, API를 사용할 때 거의 동일한 경험을 제공합니다. 차이는 스토리지 위치와 수명 주기 관리에 있습니다.

### Managed Volumes를 선택하는 경우

Managed Volumes는 다음과 같은 이점을 제공합니다.

- Databricks 워크로드의 기본 선택지입니다.
- 클라우드 자격증명이나 스토리지 경로를 직접 관리할 필요가 없습니다.
- 거버닝된 스토리지 위치를 빠르게 생성하는 가장 간단한 방법입니다.

Managed Volume을 생성하는 방법은 다음과 같습니다.

```sql
CREATE VOLUME IF NOT EXISTS my_catalog.my_schema.my_volume
COMMENT 'Managed volume for unstructured data files';
```

Python에서도 동일하게 생성할 수 있습니다.

```python
spark.sql("""
    CREATE VOLUME IF NOT EXISTS my_catalog.my_schema.my_volume
    COMMENT 'Managed volume for unstructured data files'
""")
```

### External Volumes를 선택하는 경우

External Volumes는 기존 클라우드 오브젝트 스토리지 디렉토리에 Unity Catalog 거버넌스를 추가할 때 적합합니다. 다음과 같은 상황에서 유용합니다.

- 데이터를 복사하지 않고 기존 위치에 거버넌스를 추가하는 경우
- 다른 시스템이 생성하는 파일을 Databricks에서 수집·접근해야 하는 경우
- Databricks에서 생성한 데이터를 외부 시스템이 직접 클라우드 스토리지에서 읽어야 하는 경우

External Volume을 생성하려면 먼저 외부 스토리지 자격증명(Storage Credential)과 외부 위치(External Location)가 설정되어 있어야 합니다.

```sql
CREATE EXTERNAL VOLUME my_catalog.my_schema.my_external_volume
LOCATION 's3://my-bucket/my-prefix/volumes/'
COMMENT 'External volume pointing to existing S3 storage';
```

{% hint style="warning" %}
Databricks는 Databricks와 외부 시스템 모두가 읽고 쓰는 비테이블 데이터 파일을 저장할 때 External Volumes를 사용하도록 권장합니다. Unity Catalog는 외부 시스템이 클라우드 오브젝트 스토리지에 직접 수행하는 읽기/쓰기를 거버닝하지 않으므로, 외부 시스템에서도 데이터 거버넌스 정책이 준수되도록 클라우드 계정에서 별도의 정책과 자격증명을 구성해야 합니다.
{% endhint %}

---

## 주요 사용 사례

Volumes를 활용할 수 있는 대표적인 사용 사례는 다음과 같습니다.

**ETL 파이프라인 랜딩 존 등록**: 외부 시스템에서 생성된 원시 데이터의 랜딩 영역을 등록하여 ETL 파이프라인 초기 단계에서 처리를 지원합니다.

**데이터 수집 스테이징 위치**: Auto Loader, `COPY INTO`, `CREATE TABLE AS` 등의 수집 도구를 위한 스테이징 위치로 활용합니다.

**데이터 과학자·분석가를 위한 파일 스토리지**: 탐색적 데이터 분석 및 기타 데이터 사이언스 작업에 사용할 파일 스토리지를 제공합니다.

**비정형 데이터 접근**: 감시 시스템이나 IoT 기기가 캡처한 이미지, 오디오, 동영상, PDF 등 대규모 비정형 데이터 컬렉션에 대한 접근을 제공합니다.

**라이브러리 파일 관리**: 로컬 의존성 관리 시스템이나 CI/CD 파이프라인에서 가져온 JAR 파일과 Python wheel 파일을 저장합니다.

**운영 데이터 저장**: 로그 파일이나 체크포인트 파일과 같은 운영 데이터를 저장합니다.

---

## 파일 작업: 다양한 인터페이스 지원

Volumes의 파일은 여러 인터페이스를 통해 접근하고 관리할 수 있습니다.

### Catalog Explorer UI

Catalog Explorer UI에서는 파일 업로드(최대 5GB), 다운로드, 디렉토리 생성, 파일 삭제 등의 작업을 대화형으로 수행할 수 있습니다. 또한 볼륨 내 파일로부터 직접 Unity Catalog 관리형 테이블을 생성하는 기능도 지원합니다.

### Python / dbutils

```python
# 파일 업로드
dbutils.fs.cp(
    "dbfs:/databricks-datasets/flower_photos/roses/10090824183_d02c613f10_m.jpg",
    "/Volumes/my_catalog/raw/files_volume/rose.jpg"
)

# 파일 목록 확인
files = dbutils.fs.ls("/Volumes/my_catalog/raw/files_volume/")
for f in files:
    print(f"{f.name}\t{f.size} bytes")

# 파일 삭제
dbutils.fs.rm("/Volumes/my_catalog/raw/files_volume/old_file.jpg")

# 디렉토리 재귀 삭제
dbutils.fs.rm("/Volumes/my_catalog/raw/files_volume/old_dir/", recurse=True)
```

### SQL

SQL에서는 `LIST`, `PUT INTO`, `GET`, `REMOVE` 명령어로 파일을 관리할 수 있습니다.

```sql
-- 파일 목록 확인
LIST '/Volumes/my_catalog/raw/files_volume/';

-- 파일 메타데이터 조회
SELECT
  path,
  _metadata.file_name,
  _metadata.file_size,
  _metadata.file_modification_time
FROM read_files(
  '/Volumes/my_catalog/raw/files_volume/',
  format => 'binaryFile'
);
```

### Databricks CLI

```bash
# 파일 목록
databricks fs ls dbfs:/Volumes/my_catalog/raw/files_volume/

# 파일 삭제
databricks fs rm dbfs:/Volumes/my_catalog/raw/files_volume/old_file.jpg

# 디렉토리 재귀 삭제
databricks fs rm -r dbfs:/Volumes/my_catalog/raw/files_volume/old_dir/
```

### 표준 Python 파일 I/O

Volumes는 표준 Python `open()` 함수로도 직접 읽고 쓸 수 있습니다. 이는 pandas, PIL, PyPDF2 등 외부 라이브러리와의 통합을 매우 간단하게 만들어 줍니다.

```python
# 텍스트 파일 쓰기
with open("/Volumes/my_catalog/raw/files_volume/hello.txt", "w") as f:
    f.write("Hello, Volumes!")

# 텍스트 파일 읽기
with open("/Volumes/my_catalog/raw/files_volume/hello.txt", "r") as f:
    content = f.read()
    print(content)

# 이진 파일 읽기 (예: 이미지)
import os
os.remove("/Volumes/my_catalog/raw/files_volume/old_file.jpg")
```

---

## 비정형 데이터 처리: AI 함수와의 통합

Volumes의 강력한 활용 사례 중 하나는 AI 함수와의 통합입니다. `read_files()` 테이블 값 함수(table-valued function)와 `ai_query()`, `ai_parse_document()` 같은 AI 함수를 결합하면, SQL 한 줄로 PDF 문서를 파싱하거나 이미지를 분석할 수 있습니다.

### PDF 문서 파싱

```sql
SELECT
  path AS file_path,
  ai_parse_document(content, map('version', '2.0')) AS parsed_content
FROM read_files(
  '/Volumes/my_catalog/raw/files_volume/',
  format => 'binaryFile',
  fileNamePattern => '*.pdf'
);
```

AI 함수를 사용할 수 없는 환경이라면, PyPDF2와 같은 라이브러리로 UDF를 작성할 수도 있습니다.

```python
%pip install PyPDF2

from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from PyPDF2 import PdfReader
import io

@udf(returnType=StringType())
def extract_pdf_text(content):
    if content is None:
        return None
    try:
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        return f"Error: {str(e)}"

df = spark.read.format("binaryFile") \
    .option("pathGlobFilter", "*.pdf") \
    .load("/Volumes/my_catalog/raw/files_volume/")
result_df = df.withColumn("text_content", extract_pdf_text("content"))
display(result_df.select("path", "text_content"))
```

### 이미지 분석

```sql
SELECT
  path,
  ai_query(
    'databricks-llama-4-maverick',
    'Describe this image in one sentence:',
    files => content
  ) AS description
FROM read_files(
  '/Volumes/my_catalog/raw/files_volume/',
  format => 'binaryFile',
  fileNamePattern => '*.{jpg,jpeg,png}'
)
WHERE _metadata.file_size < 5000000;
```

### 파일 메타데이터와 정형 테이블의 조인

Volumes의 파일을 정형 테이블의 데이터와 결합하는 것도 가능합니다. 예를 들어 파일 경로와 파일명을 기준으로 비정형 파일과 구조화된 메타데이터를 연결할 수 있습니다.

```sql
WITH files_with_row AS (
  SELECT
    path,
    SPLIT(path, '/')[SIZE(SPLIT(path, '/')) - 1] AS file_name,
    length,
    ROW_NUMBER() OVER (ORDER BY path) AS file_row
  FROM read_files(
    '/Volumes/my_catalog/raw/files_volume/',
    format => 'binaryFile'
  )
)
SELECT
  f.path,
  f.file_name,
  f.length
FROM files_with_row f
LIMIT 10;
```

---

## 증분 수집: Auto Loader 및 Streaming Tables

새로운 파일이 Volume에 추가될 때 자동으로 테이블을 업데이트하려면 Auto Loader나 Streaming Tables를 활용할 수 있습니다.

### Auto Loader (PySpark Structured Streaming)

```python
from pyspark.sql.functions import current_timestamp, col

dbutils.fs.mkdirs("/Volumes/my_catalog/raw/files_volume/incoming/")

df = spark.readStream.format("cloudFiles") \
    .option("cloudFiles.format", "binaryFile") \
    .option("pathGlobFilter", "*.pdf") \
    .load("/Volumes/my_catalog/raw/files_volume/incoming/")

df_enriched = df \
    .withColumn("ingestion_time", current_timestamp()) \
    .withColumn("source_file", col("_metadata.file_path"))

query = df_enriched.writeStream \
    .option("checkpointLocation",
            "/Volumes/my_catalog/raw/files_volume/_checkpoints/docs") \
    .trigger(availableNow=True) \
    .toTable("my_catalog.processed.document_ingestion")

query.awaitTermination()
```

### Streaming Table (SQL / DLT)

Delta Live Tables를 사용하면 스케줄 기반으로 Volume을 자동 감시하고 새 파일을 수집하는 파이프라인을 간결하게 정의할 수 있습니다.

```sql
CREATE OR REFRESH STREAMING TABLE document_ingestion
SCHEDULE EVERY 1 HOUR
AS SELECT
  path,
  modificationTime,
  length,
  content,
  _metadata,
  current_timestamp() AS ingestion_time
FROM STREAM(read_files(
  '/Volumes/my_catalog/raw/files_volume/incoming/',
  format => 'binaryFile'
));
```

이 패턴은 COPY INTO 명령어와 함께 사용하면 랜딩 존에서 Delta 테이블로 데이터를 멱등적으로 수집하는 표준적인 파이프라인을 구성할 수 있습니다.

---

## 접근 제어: 세밀한 권한 관리

Volumes는 Unity Catalog의 표준 GRANT/REVOKE 체계로 세밀하게 권한을 관리할 수 있습니다. 주요 권한 유형은 `READ VOLUME`(읽기), `WRITE VOLUME`(읽기+쓰기), `ALL PRIVILEGES`(모든 권한)입니다.

```sql
-- 읽기 권한 부여
GRANT READ VOLUME ON VOLUME my_catalog.raw.files_volume
TO `data-science-team`;

-- 읽기 및 쓰기 권한 부여
GRANT READ VOLUME, WRITE VOLUME ON VOLUME my_catalog.raw.files_volume
TO `data-engineering-team`;

-- 모든 권한 부여
GRANT ALL PRIVILEGES ON VOLUME my_catalog.raw.files_volume
TO `admin-group`;

-- 현재 부여된 권한 조회
SHOW GRANTS ON VOLUME my_catalog.raw.files_volume;
```

Python에서도 동일하게 수행할 수 있습니다.

```python
spark.sql("""
    GRANT READ VOLUME ON VOLUME my_catalog.raw.files_volume
    TO `data-science-team`
""")
```

Unity Catalog의 거버넌스 체계 덕분에 계정 관리자, 워크스페이스 관리자, 메타스토어 관리자 등 세 가지 관리 계층에서 최소 권한 원칙(least-privilege principle)에 따라 액세스를 제어할 수 있습니다.

---

## Delta Sharing을 통한 Volumes 공유

Unity Catalog Volumes는 Delta Sharing과 통합되어 클라우드, 리전, 계정 경계를 넘어 비정형 데이터를 안전하게 공유할 수 있습니다. 이는 GA 출시와 함께 도입된 주요 기능 중 하나입니다.

PDF, 이미지, 동영상, 오디오 파일, 기타 문서 자산 등 대규모 비정형 데이터 컬렉션을 테이블, 노트북, AI 모델과 함께 공유할 수 있습니다.

```sql
-- Share 생성
CREATE SHARE IF NOT EXISTS unstructured_data_share
COMMENT 'Document files for partner organizations';

-- Volume 추가
ALTER SHARE unstructured_data_share
ADD VOLUME my_catalog.raw.files_volume;

-- Recipient 생성
CREATE RECIPIENT IF NOT EXISTS partner_org
USING ID '<recipient-sharing-identifier>';

-- 액세스 권한 부여
GRANT SELECT ON SHARE unstructured_data_share
TO RECIPIENT partner_org;
```

수신 측에서는 공유된 Volume을 다음과 같이 사용합니다.

```sql
-- 사용 가능한 Share 조회
SHOW SHARES IN PROVIDER <provider_name>;

-- Share로부터 카탈로그 생성
CREATE CATALOG IF NOT EXISTS shared_documents
FROM SHARE <provider_name>.unstructured_data_share;

-- 공유된 파일 쿼리
SELECT * EXCEPT (content), _metadata
FROM read_files(
  '/Volumes/shared_documents/raw/files_volume/',
  format => 'binaryFile'
)
LIMIT 10;
```

---

## End-to-End 리니지 추적

Volumes의 또 다른 중요한 기능은 리니지(lineage) 추적입니다. AI 애플리케이션에서 데이터 리니지는 이제 엔터프라이즈 지식 기반(Unity Catalog Volumes 및 테이블)에서 시작하여, 데이터 파이프라인, 모델 파인튜닝 및 커스터마이징 단계를 거쳐 모델 서빙 엔드포인트나 RAG 체인을 호스팅하는 엔드포인트에 이르기까지 전 구간을 추적할 수 있습니다. 이를 통해 AI 애플리케이션의 완전한 추적 가능성, 감사 가능성, 근본 원인 분석 가속화가 실현됩니다.

Catalog Explorer의 리니지 UI를 통해 볼륨에서 파생된 테이블의 업스트림·다운스트림 관계를 시각적으로 확인할 수 있습니다.

---

## Credential Vending: 외부 접근 보안

Unity Catalog API는 Credential Vending(자격증명 대여)을 지원합니다. 클라이언트의 기반 클라우드 스토리지 액세스를 게이트웨이로 제어하여, 거버넌스를 카탈로그 서버에 중앙 집중화합니다. 이로써 Daft, Ray 같은 AI/ML 워크플로우 도구에서도 비정형 데이터를 안전하게 접근할 수 있습니다.

---

## 컴퓨트 요구 사항 및 제한 사항

Volumes를 사용하려면 Unity Catalog가 활성화된 컴퓨트를 사용해야 합니다. 구체적으로는 SQL Warehouse 또는 Databricks Runtime 13.3 LTS 이상의 클러스터가 필요합니다(Catalog Explorer 같은 Databricks UI는 예외).

다음 표는 Databricks Runtime 버전별 주요 제한 사항을 정리한 것입니다.

| Databricks Runtime 버전 | 제한 사항 |
|---|---|
| 모든 지원 버전 공통 | Executor로 분산되는 `dbutils.fs` 명령어 미지원 / RDD에서 볼륨 접근 불가 / JAR 파일을 사용하는 레거시 spark-submit 태스크 미지원 / Unity Catalog UDF에서 볼륨 경로 접근 불가 / `%sh mv`는 볼륨 간 파일 이동에 미지원 (대신 `dbutils.fs.mv` 또는 `%sh cp` 사용) |
| 14.3 LTS 이상 | Dedicated 액세스 모드에서 Scala 스레드/서브프로세스에서 볼륨 접근 불가 |
| 14.2 이하 | Standard 액세스 모드에서 UDF의 볼륨 접근 불가 / Dedicated 액세스 모드에서 Scala FUSE 및 Scala I/O 코드의 볼륨 경로 접근 불가 |

{% hint style="info" %}
볼륨은 `dbfs:/Volumes` 및 `/Volumes` 경로를 예약 경로로 사용합니다. 이 경로들은 Databricks Runtime 12.2 LTS 이하에서는 클러스터에 임시 연결된 디스크에 데이터를 쓸 수 있으므로, 반드시 Runtime 13.3 LTS 이상을 사용해야 합니다.
{% endhint %}

---

## 정형 데이터와의 통합 아키텍처 패턴

Volumes는 Delta 테이블과 함께 사용할 때 가장 강력합니다. 대표적인 통합 패턴은 다음과 같습니다.

**메달리온 아키텍처에서의 활용**: 원시 비정형 데이터를 Volume Bronze 레이어에 랜딩하고, 처리 결과를 Delta 테이블 Silver/Gold 레이어로 이동시키는 패턴입니다.

**ML 파이프라인에서의 Feature Store 연동**: 이미지나 오디오 파일은 Volume에 저장하고, 추출된 피처(특징)는 Delta 테이블에 저장하여 Feature Store와 연동하는 패턴입니다.

**RAG 아키텍처에서의 지식 베이스**: PDF, HTML, 텍스트 파일 등 문서를 Volume에 저장하고, 임베딩 파이프라인을 통해 Vector Search 인덱스로 변환하는 패턴입니다.

**라이브러리 및 아티팩트 관리**: 사용자 정의 라이브러리(.whl, .jar)나 ML 모델 아티팩트를 Volume에 저장하고, 클러스터 초기화 스크립트에서 참조하는 패턴입니다.

---

## 명명 규칙 및 설계 권고 사항

Volume을 실제 운영 환경에서 효과적으로 활용하기 위한 설계 권고 사항을 정리합니다.

**카탈로그·스키마 구조**: 환경(`dev`, `stg`, `prd`), 비즈니스 단위, 데이터 레이어를 반영한 명명 규칙을 사용합니다. 예: `dev_finance_bronze`, `prd_ml_raw`.

**Volume 경로 겹침 주의**: Volume 경로는 겹치면 안 됩니다. 예를 들어 `parent/child_one` 경로의 볼륨이 있으면 `parent` 경로의 볼륨은 생성할 수 없습니다. 반면 `parent/child_one`과 `parent/child_two`는 겹치지 않으므로 허용됩니다.

**날짜 기반 파티셔닝**: 서브디렉토리를 `YYYY-MM-DD` 형식의 날짜로 구성하여 디버깅과 데이터 관리를 용이하게 합니다.

**민감 데이터(PII) 처리**: 민감 데이터는 프로덕션 환경에서 머신 ID(Service Principal, Managed Identity)를 통해서만 저장하도록 제한합니다. 반드시 필요한 경우에는 저장 전 토큰화하고, 컬럼 수준 보안(CLS) 또는 행 수준 보안(RLS)을 적용합니다.

**External Volumes의 Azure ADLS 요구 사항**: Azure에서 External Volume을 사용할 때는 계층적 네임스페이스(Hierarchical Namespace)가 활성화된 스토리지 계정(Azure Data Lake Storage Gen 2)이 필요합니다. Azure Blob Storage Gen 1은 지원되지 않습니다.

---

## 다음 단계

Unity Catalog Volumes의 더 깊은 내용을 탐색하려면 다음 공식 리소스를 참고하세요.

- [Unity Catalog Volumes란?](https://docs.databricks.com/aws/en/volumes/) — 공식 개요 문서
- [비정형 데이터를 Volumes로 처리하기](https://docs.databricks.com/aws/en/volumes/unstructured-data-tutorial) — 실습 튜토리얼
- [Unity Catalog Volumes GA 발표](https://www.databricks.com/blog/announcing-general-availability-unity-catalog-volumes) — GA 블로그 포스트
- [Delta Sharing으로 데이터와 AI 자산 안전하게 공유하기](https://docs.databricks.com/aws/en/delta-sharing/) — Delta Sharing 공식 문서
