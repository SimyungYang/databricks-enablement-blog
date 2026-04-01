# Knowledge Assistant

---

## 개요

Knowledge Assistant는 **문서 기반 Q&A 챗봇**을 생성합니다. 기존 RAG보다 향상된 **Instructed Retriever**방식을 사용하며, 응답 시 출처(Citation)를 함께 제공합니다.

**적합한 유스케이스:**
- 제품 문서 Q&A
- HR 정책 질의
- 고객 지원 지식 베이스

---

## 추가 요구사항

공통 요구사항 외에 다음이 필요합니다.

- `databricks-gte-large-en` 임베딩 모델 엔드포인트
  - **AI Guardrails 비활성화**필수
  - **Rate Limits 비활성화**필수
- 입력 데이터: **UC 파일(Volume)**또는 **Vector Search Index**
- MLflow Production Monitoring (Beta) 활성화 (트레이싱 기능용)

---

## 생성 단계 (Step by Step)

### Step 1: 에이전트 설정

1. 좌측 메뉴에서 **Agents**> **Knowledge Assistant**> **Build**클릭
2. 기본 정보 입력:

| 항목 | 설명 |
|------|------|
| **Name**| 에이전트 고유 이름 |
| **Description**| 에이전트 목적과 기능 요약 |

3. **Knowledge Source**선택 (최대 10개까지 추가 가능):

**옵션 A: UC Files (Unity Catalog Volume)**

- Catalog > Volume 또는 디렉토리 선택
- 지원 형식: `txt`, `pdf`, `md`, `ppt/pptx`, `doc/docx`
- 파일 크기 제한: **50MB 이하**
- 언더스코어(`_`) 또는 마침표(`.`)로 시작하는 파일은 제외됨

**옵션 B: Vector Search Index**

- `databricks-gte-large-en` 임베딩을 사용하는 인덱스 선택
- **Text Column**: 검색 대상 텍스트 컬럼 지정
- **Doc URI Column**: 인용(Citation) 표시용 문서 URI 컬럼 지정

4. **Content Description**입력: 소스 데이터 활용 방법 안내
5. **Instructions**(선택): 응답 가이드라인 설정

{% hint style="warning" %}
**Knowledge Source 동기화**: Knowledge Assistant 생성자만 소스를 동기화할 수 있습니다. 소스 파일을 업데이트한 후 **Sync**아이콘을 클릭하면 변경 사항을 증분 처리합니다.
{% endhint %}

### Step 2: 에이전트 테스트

생성 후 **Build**탭 또는 **AI Playground**에서 품질을 검증합니다.

| 기능 | 설명 |
|------|------|
| **Chat Interface**| 직접 질문하고 응답 품질 확인 |
| **View Thoughts**| 에이전트의 추론 과정 확인 |
| **View Trace**| 전체 실행 트레이스 + 품질 라벨링 |
| **View Sources**| 인용 출처 검증 |

### Step 3: 품질 개선

**Examples**탭에서 자연어 피드백을 활용하여 품질을 향상시킵니다.

**데이터 수집 방법:**

1. **수동 추가**: "+ Add" 버튼으로 질문 직접 추가
2. **전문가 피드백**: 공유 설정 링크를 통해 SME(Subject Matter Expert)의 피드백 수집
3. **가이드라인 적용**: 질문별 가이드라인 설정
4. **UC 테이블 Import/Export**: 라벨링된 데이터셋을 Unity Catalog 테이블로 관리

**Import 스키마 형식:**

```
eval_id     : string        -- 평가 ID
request     : string        -- 질문
guidelines  : array<string> -- 가이드라인 배열
metadata    : string        -- 메타데이터
tags        : string        -- 태그
```

### Step 4: 배포 및 쿼리

에이전트는 자동으로 **Serving Endpoint**로 배포됩니다. "See Agent status"를 클릭하면 엔드포인트 상세 정보를 확인할 수 있습니다.

**Python SDK로 생성하기:**

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.knowledgeassistants import KnowledgeAssistant

w = WorkspaceClient()

knowledge_assistant = KnowledgeAssistant(
    display_name="HR 정책 도우미",
    description="사내 HR 정책 문서에 대한 Q&A 제공",
    instructions="한국어로 응답하세요. 정책 원문을 인용해주세요.",
)

created = w.knowledge_assistants.create_knowledge_assistant(
    knowledge_assistant=knowledge_assistant
)
```

**쿼리 방법:**
- **AI Playground**: 인터랙티브 테스트
- **REST API (curl)**: HTTP 요청으로 직접 호출
- **Python SDK**: 프로그래밍 방식 연동

---

## 권한 관리

기본적으로 생성자와 워크스페이스 관리자만 접근 가능합니다.

| 권한 수준 | 할 수 있는 일 |
|-----------|---------------|
| **Can Manage**| 설정 편집, 권한 관리, 품질 개선 |
| **Can Query**| AI Playground 또는 API를 통한 쿼리만 가능 |

> 권한 부여: 케밥 메뉴(...) > **Manage Permissions**> 사용자/그룹/서비스 프린시펄 선택

---

## 제한사항

- 영어만 지원
- 파일 크기: 50MB 이하
- UC 테이블 직접 지원 불가 (Volume 또는 Vector Search Index 사용)
- Vector Search는 `databricks-gte-large-en` 임베딩만 지원
- 임베딩 엔드포인트에 AI Guardrails/Rate Limits 비활성화 필수
