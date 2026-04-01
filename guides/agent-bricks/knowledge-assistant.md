# Knowledge Assistant

---

## 개요

Knowledge Assistant는 ** 문서 기반 Q&A 챗봇** 을 생성합니다. 기존 RAG보다 향상된 **Instructed Retriever** 방식을 사용하며, 응답 시 출처(Citation)를 함께 제공합니다.

** 적합한 유스케이스:**
- 제품 문서 Q&A
- HR 정책 질의
- 고객 지원 지식 베이스

---

## 추가 요구사항

공통 요구사항 외에 다음이 필요합니다.

- `databricks-gte-large-en` 임베딩 모델 엔드포인트
  - **AI Guardrails 비활성화** 필수
  - **Rate Limits 비활성화** 필수
- 입력 데이터: **UC 파일(Volume)** 또는 **Vector Search Index**
- MLflow Production Monitoring (Beta) 활성화 (트레이싱 기능용)

---

## 생성 단계 (Step by Step)

### Step 1: 에이전트 설정

1. 좌측 메뉴에서 **Agents**> **Knowledge Assistant**> **Build** 클릭
2. 기본 정보 입력:

| 항목 | 설명 |
|------|------|
| **Name**| 에이전트 고유 이름 |
| **Description**| 에이전트 목적과 기능 요약 |

3. **Knowledge Source** 선택 (최대 10개까지 추가 가능):

** 옵션 A: UC Files (Unity Catalog Volume)**

- Catalog > Volume 또는 디렉토리 선택
- 지원 형식: `txt`, `pdf`, `md`, `ppt/pptx`, `doc/docx`
- 파일 크기 제한: **50MB 이하**
- 언더스코어(`_`) 또는 마침표(`.`)로 시작하는 파일은 제외됨

** 옵션 B: Vector Search Index**

- `databricks-gte-large-en` 임베딩을 사용하는 인덱스 선택
- **Text Column**: 검색 대상 텍스트 컬럼 지정
- **Doc URI Column**: 인용(Citation) 표시용 문서 URI 컬럼 지정

4. **Content Description** 입력: 소스 데이터 활용 방법 안내
5. **Instructions**(선택): 응답 가이드라인 설정

{% hint style="warning" %}
**Knowledge Source 동기화**: Knowledge Assistant 생성자만 소스를 동기화할 수 있습니다. 소스 파일을 업데이트한 후 **Sync** 아이콘을 클릭하면 변경 사항을 증분 처리합니다.
{% endhint %}

### Step 2: 에이전트 테스트

생성 후 **Build** 탭 또는 **AI Playground** 에서 품질을 검증합니다.

| 기능 | 설명 |
|------|------|
| **Chat Interface**| 직접 질문하고 응답 품질 확인 |
| **View Thoughts**| 에이전트의 추론 과정 확인 |
| **View Trace**| 전체 실행 트레이스 + 품질 라벨링 |
| **View Sources**| 인용 출처 검증 |

### Step 3: 품질 개선

**Examples** 탭에서 자연어 피드백을 활용하여 품질을 향상시킵니다.

** 데이터 수집 방법:**

1. ** 수동 추가**: "+ Add" 버튼으로 질문 직접 추가
2. ** 전문가 피드백**: 공유 설정 링크를 통해 SME(Subject Matter Expert)의 피드백 수집
3. ** 가이드라인 적용**: 질문별 가이드라인 설정
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

에이전트는 자동으로 **Serving Endpoint** 로 배포됩니다. "See Agent status"를 클릭하면 엔드포인트 상세 정보를 확인할 수 있습니다.

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

** 쿼리 방법:**
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

---

## Knowledge Assistant 내부 작동 원리

Knowledge Assistant는 단순한 챗봇이 아니라 ** 여러 AI 컴포넌트가 연결된 복합 시스템(Compound AI System)** 입니다. 내부적으로 어떻게 작동하는지 이해하면, 품질 문제를 진단하고 최적화하는 데 큰 도움이 됩니다.

### 전체 파이프라인 흐름

```
사용자 질문 입력
    ↓
[1단계: Query Understanding]
    - 질문 분석 및 의도 파악
    - 검색에 최적화된 쿼리로 변환 (Query Rewriting)
    - 대화 이력이 있으면 컨텍스트를 반영하여 쿼리 확장
    ↓
[2단계: Instructed Retriever]
    - Vector Search Index에서 관련 청크 검색
    - Content Description과 Instructions를 참고하여 검색 범위 조정
    - 유사도 점수 기반으로 상위 K개 청크 선택
    - 중복 제거 및 관련성 재순위(Re-ranking)
    ↓
[3단계: Context Assembly]
    - 검색된 청크를 LLM 프롬프트에 삽입
    - Instructions를 System Prompt로 구성
    - 대화 이력을 포함하여 멀티턴 컨텍스트 유지
    ↓
[4단계: LLM Generation]
    - Foundation Model(Claude, GPT-4o, Llama 등)에 프롬프트 전송
    - 검색된 문서를 근거로 응답 생성
    - 인용(Citation) 마커를 응답에 삽입
    ↓
[5단계: Post-processing]
    - 인용 출처 매핑 (청크 → 원본 문서 + 위치)
    - 응답 포맷팅
    - Safety 필터 적용
    ↓
응답 반환 (텍스트 + 인용 + 소스 목록)
```

### Instructed Retriever vs 기존 RAG

Knowledge Assistant는 일반적인 RAG(Retrieval-Augmented Generation)가 아닌 **Instructed Retriever** 를 사용합니다. 이 방식은 기존 RAG 대비 다음과 같은 차이점이 있습니다.

| 구분 | 기존 RAG | Instructed Retriever |
|------|---------|---------------------|
| ** 검색 방식**| 벡터 유사도만 사용 | 벡터 유사도 + Content Description + Instructions 통합 |
| ** 쿼리 변환**| 사용자 질문 그대로 검색 | 질문을 분석하여 검색에 최적화된 형태로 변환 |
| ** 컨텍스트 인식**| 단일 턴 검색 | 대화 이력을 반영하여 검색 쿼리 확장 |
| ** 결과 필터링**| Top-K 단순 선택 | 관련성 재순위 + 중복 제거 + 다양성 보장 |

---

## RAG 품질을 좌우하는 핵심 요소

Knowledge Assistant의 응답 품질은 ** 검색 품질** 과 ** 생성 품질** 두 축으로 결정됩니다. 각 축을 좌우하는 요소를 상세히 알아봅니다.

### 1. 청킹(Chunking) 전략

청킹은 원본 문서를 검색 가능한 단위로 분할하는 과정입니다. Knowledge Assistant는 UC Files를 업로드하면 내부적으로 자동 청킹을 수행합니다.

| 청킹 파라미터 | 설명 | 권장 설정 |
|--------------|------|-----------|
| ** 청크 크기**| 하나의 청크에 포함되는 토큰 수 | FAQ: 256~512 토큰 / 기술문서: 512~1024 토큰 |
| ** 오버랩(Overlap)**| 인접 청크 간 겹치는 토큰 수 | 청크 크기의 10~20% (문맥 유지) |
| ** 분할 기준**| 문장, 단락, 섹션 등 | 문서 구조에 따라 자동 결정 |

** 청킹 품질이 나쁘면 발생하는 문제:**

- 청크가 너무 작으면: 문맥이 잘려서 LLM이 올바른 답변을 생성하지 못함
- 청크가 너무 크면: 관련 없는 내용이 함께 검색되어 답변의 정확도 저하
- 오버랩이 없으면: 문장이 두 청크 사이에서 잘려 의미가 손실됨

{% hint style="info" %}
**Vector Search Index를 직접 사용하는 경우**, 청킹 전략을 세밀하게 제어할 수 있습니다. UC Files 자동 청킹의 품질이 만족스럽지 않다면, 별도로 청킹 파이프라인을 구축하고 Vector Search Index를 Knowledge Source로 연결하는 것을 권장합니다.
{% endhint %}

### 2. 임베딩 모델

Knowledge Assistant는 현재 `databricks-gte-large-en` 임베딩 모델만 지원합니다. 이 모델의 특성을 이해하면 검색 품질을 예측할 수 있습니다.

| 특성 | 상세 |
|------|------|
| ** 모델 유형**| General Text Embeddings (GTE) — 범용 텍스트 임베딩 |
| ** 언어**| 영어에 최적화 (한국어는 성능 저하 가능) |
| ** 차원(Dimension)**| 1024차원 벡터 |
| ** 최대 입력 길이**| 8192 토큰 |
| ** 유사도 측정**| 코사인 유사도 |

** 임베딩 품질 영향 요소:**

- ** 도메인 특화 용어**: 의학, 법률 등 전문 용어가 많으면 범용 임베딩의 성능이 떨어질 수 있음
- ** 언어**: 영어 외 언어(한국어 포함)는 검색 정확도가 상대적으로 낮음
- ** 동의어/약어**: "LTV"와 "Life Time Value"가 동일한 의미임을 임베딩이 인식하지 못할 수 있음 → Content Description에 동의어를 명시적으로 포함

### 3. 검색 설정

| 파라미터 | 설명 | 영향 |
|----------|------|------|
| **Top-K**| 검색할 청크 수 | K가 크면 재현율(Recall) 증가하지만 잡음도 증가 |
| ** 유사도 임계값**| 최소 유사도 점수 | 너무 높으면 관련 문서 누락, 너무 낮으면 무관한 문서 포함 |
| ** 필터**| 메타데이터 기반 사전 필터링 | 문서 유형, 날짜, 부서 등으로 검색 범위 축소 |

### 4. Content Description과 Instructions의 역할

이 두 필드는 단순한 설명이 아니라 ** 검색과 생성 품질에 직접적으로 영향** 을 미치는 핵심 파라미터입니다.

| 필드 | 역할 | 작성 팁 |
|------|------|---------|
| **Content Description**| Instructed Retriever가 검색 범위와 우선순위를 결정하는 기준 | "이 문서는 [도메인]에 대한 [문서 유형]으로, [대상 사용자]가 [목적]을 위해 사용합니다" 형태로 작성 |
| **Instructions**| LLM이 응답을 생성할 때 참고하는 System Prompt | 응답 언어, 톤, 인용 규칙, 거부 조건, 형식을 구체적으로 명시 |

**Content Description 예시 (좋은 예 vs 나쁜 예):**

```
나쁜 예: "HR 문서"
좋은 예: "이 소스는 2024년도 사내 HR 정책 문서를 포함합니다. 연차 정책,
        복리후생, 채용 절차, 평가 제도에 관한 내용이 담겨 있으며,
        전 직원이 HR 관련 질문에 답을 찾기 위해 사용합니다.
        '연차', '휴가', '복지', '채용', '평가' 등의 키워드가 핵심입니다."
```

---

## 성능 최적화 팁

### 검색 정확도 향상

| 전략 | 설명 | 효과 |
|------|------|------|
| ** 문서 구조화**| 문서에 명확한 헤딩(H1, H2, H3)과 불릿 포인트 사용 | 청킹 품질 향상, 관련 내용이 같은 청크에 포함됨 |
| ** 메타데이터 보강**| 파일명에 주제, 날짜, 버전을 포함 | 검색 시 메타데이터 필터링 가능 |
| ** 동의어 맵핑**| Content Description에 동의어/약어를 명시 | "LTV = Life Time Value = 고객 생애 가치" |
| **Knowledge Source 분리**| 주제별로 별도 Volume 또는 Index로 분리 | 검색 범위 축소로 정확도 향상 |
| ** 불필요한 문서 제거**| 구버전, 중복 문서 정리 | 잡음 감소 |

### 응답 품질 향상

| 전략 | 설명 | 효과 |
|------|------|------|
| ** 구체적 Instructions**| "정책명과 조항 번호를 인용하세요" | 인용 정확도 향상 |
| ** 거부 조건 명시**| "문서에 없는 내용은 '확인되지 않았습니다'라고 답하세요" | 환각(Hallucination) 감소 |
| **Few-shot Examples**| Examples 탭에 좋은 응답 예시 등록 | 응답 스타일과 형식 일관성 |
| ** 언어 지정**| "반드시 한국어로 응답하세요" | 다국어 문서 사용 시 응답 언어 통일 |

### 지연 시간(Latency) 최적화

| 전략 | 설명 | 효과 |
|------|------|------|
| **Knowledge Source 수 최소화**| 필요한 소스만 연결 (10개 한도 중 3~5개 권장) | 검색 범위 축소로 응답 속도 향상 |
| ** 문서 크기 최적화**| 50MB 한도 내에서도 10MB 이하 권장 | 청킹/인덱싱 속도 향상 |
| **Vector Search Endpoint 스케일링**| 쿼리 부하에 맞는 엔드포인트 크기 선택 | 검색 지연 시간 감소 |
| ** 불필요한 오버랩 제거**| 문서 간 중복 내용 정리 | 검색 결과 중복 제거 시간 감소 |

---

## 실제 구축 사례

### 사례 1: 제조업 설비 매뉴얼 Q&A

** 배경**: 대형 제조사에서 수백 페이지의 설비 매뉴얼을 보유. 현장 엔지니어가 설비 문제 발생 시 매뉴얼을 찾아보는 데 평균 15분 소요.

** 구축 내용:**

| 항목 | 설정 |
|------|------|
| **Knowledge Source**| UC Volume에 설비별 매뉴얼 PDF 업로드 (32개 파일, 총 120MB → 50MB 이하로 분할) |
| **Content Description**| "공장 설비(CNC, 프레스, 로봇 등)의 운영 매뉴얼입니다. 설비 모델명, 에러 코드, 유지보수 절차, 부품 번호 등이 포함됩니다." |
| **Instructions**| "반드시 한국어로 응답. 에러 코드가 포함된 질문은 해당 에러의 원인, 조치 방법, 관련 부품 번호를 함께 안내. 안전 주의사항이 있으면 반드시 포함." |

** 결과:**

- 문제 해결 시간: 평균 15분 → 2분으로 단축
- AI Judge Correctness: 87%
- AI Judge Groundedness: 92%

### 사례 2: 금융사 규제 문서 Q&A

** 배경**: 금융 규제 문서(감독 규정, 시행세칙 등)를 기반으로 내부 직원이 규제 관련 질문에 답변을 얻어야 하는 상황.

** 구축 내용:**

| 항목 | 설정 |
|------|------|
| **Knowledge Source**| Vector Search Index 사용 (자체 청킹 파이프라인 — 조항 단위로 분할) |
| **Content Description**| "금융감독원 감독규정, 시행세칙, 금융위원회 고시 등 금융 규제 문서입니다. 조항 번호, 규제 대상, 준수 사항, 벌칙 등이 포함됩니다." |
| **Instructions**| "답변 시 반드시 관련 조항 번호와 규정명을 인용하세요. 규정 해석이 모호한 경우 '규제 전문가 확인이 필요합니다'라고 명시하세요. 법적 조언은 제공하지 마세요." |

** 핵심 최적화:**

- 조항 단위 청킹으로 검색 정확도 대폭 향상 (기본 청킹 대비 Correctness +15%)
- 규제 용어 동의어를 Content Description에 포함하여 검색 재현율 향상
- Examples 탭에 50개 이상의 실제 질문-답변 쌍 등록

### 사례 3: SaaS 기업 고객지원 챗봇

** 배경**: SaaS 제품의 고객 지원 문서(도움말, API 레퍼런스, 릴리즈 노트)를 기반으로 셀프 서비스 지원.

** 구축 내용:**

| 항목 | 설정 |
|------|------|
| **Knowledge Source 1**| UC Volume — 제품 도움말 문서 (마크다운) |
| **Knowledge Source 2**| UC Volume — API 레퍼런스 문서 (마크다운) |
| **Knowledge Source 3**| Vector Search Index — 릴리즈 노트 (자주 업데이트되므로 별도 인덱스) |
| **Instructions**| "코드 예시를 포함해 답변하세요. API 엔드포인트 관련 질문은 HTTP 메서드, URL, 파라미터, 응답 형식을 포함. 릴리즈 노트 관련 질문은 버전 번호를 명시." |

** 핵심 교훈:**

- 자주 업데이트되는 문서(릴리즈 노트)는 Vector Search Index로 분리하면 동기화가 더 유연
- Knowledge Source를 주제별로 분리하면 검색 정확도가 향상됨 (전체를 하나의 Volume에 넣는 것보다)
- 코드 예시가 포함된 문서는 마크다운 형식이 PDF보다 청킹 품질이 월등히 높음
