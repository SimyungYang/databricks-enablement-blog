# Databricks Agent Bricks 실전 가이드

> **Agent Bricks**는 Databricks Mosaic AI 기반의 선언형(Declarative) AI 에이전트 빌더입니다.
> 코드 없이도 프로덕션 수준의 AI 에이전트를 빠르게 구축, 평가, 배포할 수 있습니다.

---

## 1. Agent Bricks 개요

### 1.1 Agent Bricks란?

Agent Bricks는 기술/비기술 팀 모두가 자사의 데이터를 **프로덕션 수준의 AI 에이전트**로 운영할 수 있도록 해주는 플랫폼입니다. 핵심 특징은 다음과 같습니다.

| 특징 | 설명 |
|------|------|
| **선언형 에이전트 빌드** | 자연어와 사전 구성된 템플릿으로 에이전트 정의 |
| **내장 MLflow 평가** | 에이전트 품질을 자동으로 측정 |
| **Unity Catalog 거버넌스** | 데이터 접근 권한을 통합 관리 |
| **AI Gateway 모델 유연성** | 다양한 모델/프레임워크 지원 |
| **MCP 카탈로그 통합** | 외부 도구 확장 가능 |
| **자동 최적화** | 모델 선택, 파인 튜닝, 하이퍼파라미터 최적화를 백그라운드에서 자동 수행 |

### 1.2 작동 원리 (3단계)

```
1단계: 유스케이스와 데이터 정의
    ↓
2단계: 시스템이 자동으로 모델 테스트, 파인 튜닝, 최적화
    ↓
3단계: 백그라운드에서 지속 최적화 (더 나은 모델 발견 시 알림)
```

### 1.3 에이전트 유형 비교

Agent Bricks에서 지원하는 에이전트 유형은 6가지입니다.

| 유형 | 설명 | 주요 용도 |
|------|------|-----------|
| **Knowledge Assistant** | 문서 기반 Q&A 챗봇 (RAG + 인용) | 제품 문서, HR 정책, 고객지원 |
| **Genie Spaces** | 테이블을 자연어 챗봇으로 변환 | 데이터 탐색, 비즈니스 분석 |
| **Supervisor Agent** | 여러 에이전트를 조율하는 멀티 에이전트 시스템 | 복합 업무 자동화, 시장 분석 |
| **Information Extraction** (Beta) | 비정형 문서에서 구조화된 데이터 추출 | 분류, 데이터 구조화 |
| **Custom LLM** (Beta) | 요약, 텍스트 변환 | 문서 요약, 텍스트 처리 |
| **Code Your Own Agent** | 오픈소스 라이브러리와 Agent Framework 활용 | 완전 맞춤형 에이전트 |

### 1.4 어떤 유형을 선택해야 하나?

```
"사내 문서에 대해 질문/답변이 필요하다"
    → Knowledge Assistant

"테이블 데이터를 자연어로 탐색하고 싶다"
    → Genie Spaces

"여러 에이전트를 조합해 복잡한 업무를 처리해야 한다"
    → Supervisor Agent (Multi-Agent)

"비정형 문서에서 정보를 추출해 테이블로 만들고 싶다"
    → Information Extraction

"텍스트 요약/변환 파이프라인이 필요하다"
    → Custom LLM

"위 유형에 해당하지 않는 커스텀 로직이 필요하다"
    → Code Your Own Agent
```

### 1.5 사전 요구사항

모든 Agent Bricks 유형에 공통으로 필요한 조건입니다.

- **Mosaic AI Agent Bricks Preview (Beta)** 가 워크스페이스에서 활성화
- **Unity Catalog** 활성화
- **Serverless Compute** 사용 가능 (Unity Catalog 활성화 시 기본 제공)
- **Foundation Model** 접근 가능 (`system.ai` 스키마)
- **Serverless Budget Policy** 에 0이 아닌 예산 할당
- **리전**: `us-east-1` 또는 `us-west-2`

---

## 2. Knowledge Assistant (KA)

### 2.1 개요

Knowledge Assistant는 **문서 기반 Q&A 챗봇**을 생성합니다. 기존 RAG보다 향상된 **Instructed Retriever** 방식을 사용하며, 응답 시 출처(Citation)를 함께 제공합니다.

**적합한 유스케이스:**
- 제품 문서 Q&A
- HR 정책 질의
- 고객 지원 지식 베이스

### 2.2 추가 요구사항

공통 요구사항 외에 다음이 필요합니다.

- `databricks-gte-large-en` 임베딩 모델 엔드포인트
  - **AI Guardrails 비활성화** 필수
  - **Rate Limits 비활성화** 필수
- 입력 데이터: **UC 파일(Volume)** 또는 **Vector Search Index**
- MLflow Production Monitoring (Beta) 활성화 (트레이싱 기능용)

### 2.3 생성 단계 (Step by Step)

#### Step 1: 에이전트 설정

1. 좌측 메뉴에서 **Agents** > **Knowledge Assistant** > **Build** 클릭
2. 기본 정보 입력:

| 항목 | 설명 |
|------|------|
| **Name** | 에이전트 고유 이름 |
| **Description** | 에이전트 목적과 기능 요약 |

3. **Knowledge Source** 선택 (최대 10개까지 추가 가능):

**옵션 A: UC Files (Unity Catalog Volume)**

- Catalog > Volume 또는 디렉토리 선택
- 지원 형식: `txt`, `pdf`, `md`, `ppt/pptx`, `doc/docx`
- 파일 크기 제한: **50MB 이하**
- 언더스코어(`_`) 또는 마침표(`.`)로 시작하는 파일은 제외됨

**옵션 B: Vector Search Index**

- `databricks-gte-large-en` 임베딩을 사용하는 인덱스 선택
- **Text Column**: 검색 대상 텍스트 컬럼 지정
- **Doc URI Column**: 인용(Citation) 표시용 문서 URI 컬럼 지정

4. **Content Description** 입력: 소스 데이터 활용 방법 안내
5. **Instructions** (선택): 응답 가이드라인 설정

{% hint style="warning" %}
**Knowledge Source 동기화**: Knowledge Assistant 생성자만 소스를 동기화할 수 있습니다. 소스 파일을 업데이트한 후 **Sync** 아이콘을 클릭하면 변경 사항을 증분 처리합니다.
{% endhint %}

#### Step 2: 에이전트 테스트

생성 후 **Build** 탭 또는 **AI Playground**에서 품질을 검증합니다.

| 기능 | 설명 |
|------|------|
| **Chat Interface** | 직접 질문하고 응답 품질 확인 |
| **View Thoughts** | 에이전트의 추론 과정 확인 |
| **View Trace** | 전체 실행 트레이스 + 품질 라벨링 |
| **View Sources** | 인용 출처 검증 |

#### Step 3: 품질 개선

**Examples** 탭에서 자연어 피드백을 활용하여 품질을 향상시킵니다.

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

#### Step 4: 배포 및 쿼리

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

### 2.4 권한 관리

기본적으로 생성자와 워크스페이스 관리자만 접근 가능합니다.

| 권한 수준 | 할 수 있는 일 |
|-----------|---------------|
| **Can Manage** | 설정 편집, 권한 관리, 품질 개선 |
| **Can Query** | AI Playground 또는 API를 통한 쿼리만 가능 |

> 권한 부여: 케밥 메뉴(⋮) > **Manage Permissions** > 사용자/그룹/서비스 프린시펄 선택

### 2.5 제한사항

- 영어만 지원
- 파일 크기: 50MB 이하
- UC 테이블 직접 지원 불가 (Volume 또는 Vector Search Index 사용)
- Vector Search는 `databricks-gte-large-en` 임베딩만 지원
- 임베딩 엔드포인트에 AI Guardrails/Rate Limits 비활성화 필수

---

## 3. Genie Spaces

### 3.1 개요

Genie Spaces는 Unity Catalog에 등록된 **테이블 데이터를 자연어 챗봇**으로 변환합니다. 비즈니스 사용자가 SQL 없이도 데이터에 질문할 수 있으며, 내부적으로 자연어를 SQL로 변환하여 실행합니다.

**적합한 유스케이스:**
- 비즈니스 데이터 탐색
- 셀프 서비스 분석
- KPI/메트릭 확인

### 3.2 작동 원리

Genie는 단일 LLM이 아닌 **복합 AI 시스템(Compound AI System)**입니다.

```
사용자 질문 (자연어)
    ↓
Genie 파싱 & 관련 데이터 소스 식별
    ↓
Unity Catalog 메타데이터 + Knowledge Store 컨텍스트 필터링
    ↓
읽기 전용 SQL 쿼리 생성
    ↓
SQL Warehouse에서 실행
    ↓
결과 반환 (테이블/차트)
```

**응답에 활용되는 컨텍스트:**
- Unity Catalog 테이블/컬럼 메타데이터
- Knowledge Store (작성자가 큐레이션한 공간 수준 컨텍스트)
- 예시 SQL 쿼리 및 SQL 함수
- 텍스트 지시사항 및 대화 이력

### 3.3 사전 요구사항

| 요구사항 | 설명 |
|----------|------|
| **SQL Warehouse** | Pro 또는 Serverless SQL Warehouse |
| **Unity Catalog** | 데이터가 UC에 등록되어 있어야 함 |
| **테이블 제한** | 공간당 최대 30개 테이블/뷰 |
| **처리량** | UI: 20 질문/분, API: 5 질문/분 (무료 티어) |
| **용량** | 공간당 10,000 대화, 대화당 10,000 메시지 |

**필요 권한:**
- Databricks SQL 워크스페이스 자격
- SQL Warehouse에 대한 `CAN USE` 접근
- 데이터 객체에 대한 `SELECT` 권한

### 3.4 생성 및 설정

#### Step 1: Genie Space 생성

1. 좌측 메뉴에서 **Genie** > **New** 클릭
2. Unity Catalog에서 데이터 소스 (테이블/뷰) 선택
3. **Create** 클릭

#### Step 2: Knowledge Store 설정

생성 후 반드시 Knowledge Store를 설정하세요. 이것이 Genie의 정확도를 결정합니다.

| 설정 항목 | 설명 |
|-----------|------|
| **테이블/컬럼 설명** | 비즈니스 용어, 동의어 정의 |
| **JOIN 관계** | 테이블 간 연결 정의 (복합 SQL 표현식 지원) |
| **재사용 가능 SQL 표현식** | 측정값, 필터, KPI용 표현식 |
| **프롬프트 매칭** | 형식 지원, 엔터티 교정 |

#### Step 3: Instructions & Examples 추가 (최대 100개)

- 정적 또는 파라미터화된 SQL 쿼리 (자연어 제목 포함)
- Unity Catalog 함수 (복잡한 로직용)
- 텍스트 지시사항 (비즈니스 컨텍스트, 형식 규칙)

#### Step 4: 공간 설정

- 제목, 설명 (마크다운 지원)
- 기본 SQL Warehouse 설정
- 사용자 안내용 샘플 질문 등록
- 태그 분류

### 3.5 모니터링 및 개선

**Monitoring** 탭에서 다음을 확인할 수 있습니다:
- 사용자가 질문한 모든 내용
- 사용자 피드백 (좋아요/싫어요)
- 플래그된 응답

이를 바탕으로 Knowledge Store와 Instructions를 반복적으로 개선합니다.

### 3.6 Agent Bricks에서의 활용

Genie Spaces는 **Supervisor Agent의 서브 에이전트**로 사용됩니다. Genie API를 통해 프로그래밍 방식으로 접근할 수 있으며, 멀티 에이전트 시스템에서 데이터 탐색을 담당합니다.

---

## 4. Supervisor Agent (Multi-Agent)

### 4.1 개요

Supervisor Agent는 여러 전문 에이전트를 **조율(Orchestrate)하여 복합 업무를 처리**하는 멀티 에이전트 시스템입니다.

**핵심 기능:**
- 에이전트 간 상호작용 관리
- 태스크 위임(Delegation)
- 결과 종합(Synthesis)
- 사용자 권한 기반 라우팅

**적합한 유스케이스:**
- 시장 분석 (데이터 + 문서 결합)
- 사내 프로세스 자동화
- 고객 서비스 (여러 지식 소스 통합)

### 4.2 지원하는 서브 에이전트 유형

최대 **20개**의 서브 에이전트를 등록할 수 있습니다.

| 서브 에이전트 유형 | 설명 | 필요 권한 |
|-------------------|------|-----------|
| **Genie Spaces** | 데이터 탐색 인터페이스 | Space 접근 + UC 객체 권한 |
| **Agent Endpoints** | Knowledge Assistant 엔드포인트만 지원 | `CAN QUERY` |
| **Unity Catalog Functions** | 커스텀 도구 (UC 함수) | `EXECUTE` |
| **External MCP Servers** | MCP 프로토콜 서버 (Bearer Token/OAuth) | `USE CONNECTION` (UC Connection) |

{% hint style="info" %}
**중요**: Agent Endpoints는 Knowledge Assistant로 만든 엔드포인트만 지원합니다. 일반 Agent Framework 엔드포인트는 사용할 수 없습니다.
{% endhint %}

### 4.3 추가 요구사항

공통 요구사항 외에 다음이 필요합니다.

- **On-Behalf-Of-User Authorization** 활성화
- 최소 1개의 서브 에이전트 또는 도구
- Enhanced Security and Compliance 워크스페이스는 미지원

### 4.4 생성 단계 (Step by Step)

#### Step 1: 서브 에이전트 생성 및 권한 부여

Supervisor를 만들기 전에 먼저 서브 에이전트를 준비합니다.

**예시: KA + Genie 조합**

```
1. Knowledge Assistant 생성 → 엔드포인트 확인
   - 엔드 유저에게 CAN QUERY 권한 부여

2. Genie Space 생성 → Space ID 확인
   - 엔드 유저에게 Space 접근 + UC 테이블 SELECT 권한 부여

3. (선택) UC Function 생성
   - 엔드 유저에게 EXECUTE 권한 부여

4. (선택) MCP Server 연결
   - UC Connection 생성 후 USE CONNECTION 권한 부여
```

#### Step 2: Supervisor 설정

1. **Agents** > **Supervisor Agent** > **Build** 클릭
2. 기본 정보 입력:
   - **Name**: Supervisor 고유 이름
   - **Description**: 전체 시스템 목적 설명
3. **서브 에이전트 추가** (최대 20개):
   - 각 서브 에이전트의 **이름**과 **Content Description** 입력
   - Description이 태스크 위임 로직에 직접 영향을 줌
4. **Instructions** (선택): Supervisor의 전체 동작 가이드라인

{% hint style="warning" %}
**Description이 라우팅의 핵심입니다.** Supervisor는 각 서브 에이전트의 Description을 기반으로 어떤 에이전트에 태스크를 위임할지 결정합니다. 가능한 한 상세하게 작성하세요.
{% endhint %}

#### Step 3: 테스트

1. **Test Your Agent** 패널에서 대화형 테스트
2. 올바른 서브 에이전트로 태스크가 위임되는지 확인
3. **AI Playground**에서 고급 평가 기능 활용:
   - **AI Judge**: 자동 품질 평가
   - **Synthetic Task Generation**: 합성 태스크로 테스트

#### Step 4: 품질 개선

- **Examples** 탭에서 라벨링된 질문/태스크 시나리오 추가
- SME에게 공유 링크 전달하여 피드백 수집
- 자연어 가이드라인 추가 (저장 즉시 적용)
- 재테스트로 개선 효과 검증

#### Step 5: 권한 관리

| 권한 수준 | 할 수 있는 일 |
|-----------|---------------|
| **Can Manage** | 설정 편집, 서브 에이전트 관리, 권한 관리 |
| **Can Query** | API/Playground를 통한 쿼리만 가능 (설정 확인 불가) |

#### Step 6: 엔드포인트 쿼리

배포된 Supervisor에 다음 방법으로 접근할 수 있습니다:
- **AI Playground** 인터랙티브 인터페이스
- **REST API** (curl)
- **Python SDK**

### 4.5 라우팅 로직과 접근 제어

Supervisor Agent는 **사용자 인식(User-Aware) 라우팅**을 구현합니다.

```
사용자 질문 입력
    ↓
사용자의 서브 에이전트 접근 권한 확인
    ↓
┌─ 모든 서브 에이전트 접근 불가 → 대화 종료
├─ 일부 서브 에이전트 접근 가능 → 접근 불가한 에이전트 자동 회피
└─ 모든 서브 에이전트 접근 가능 → Description 기반 최적 에이전트 선택
    ↓
선택된 서브 에이전트에 태스크 위임
    ↓
결과 종합 후 응답
```

이 방식은 사용자가 권한 없는 데이터나 에이전트에 접근하는 것을 원천적으로 차단합니다.

### 4.6 Long-Running Task Mode

복잡한 태스크의 경우, Supervisor Agent는 **Long-Running Task Mode**를 지원합니다. 이 모드는 복잡한 태스크를 여러 요청/응답 사이클로 자동 분할하여 **타임아웃을 방지**합니다.

### 4.7 제한사항

- 영어만 지원
- Supervisor당 최대 20개 서브 에이전트
- Agent Endpoints는 Knowledge Assistant만 지원
- Enhanced Security and Compliance 워크스페이스 미지원
- 에이전트 삭제 시 임시 저장 데이터도 함께 삭제

---

## 5. 실전 예제: KA + Genie + Supervisor 조합

### 5.1 시나리오

> "고객 지원팀을 위한 AI 어시스턴트를 만들자.
> - 제품 매뉴얼/FAQ는 Knowledge Assistant로 처리
> - 주문/매출 데이터 조회는 Genie Space로 처리
> - 두 에이전트를 Supervisor Agent로 통합"

### 5.2 구축 순서

```
Step 1: Knowledge Assistant 생성
  ├── 이름: "product-support-ka"
  ├── Knowledge Source: UC Volume (product_docs/)
  │   ├── product_manual.pdf
  │   ├── faq.md
  │   └── troubleshooting_guide.docx
  └── Instructions: "고객 질문에 친절하게 응답. 반드시 출처 인용."

Step 2: Genie Space 생성
  ├── 이름: "order-analytics-genie"
  ├── 테이블: sales.orders, sales.customers, sales.products
  ├── Knowledge Store:
  │   ├── 컬럼 설명: "order_date = 주문일, revenue = 매출액"
  │   └── JOIN 정의: orders.customer_id = customers.id
  └── Sample Questions: "이번 달 매출은?", "Top 10 고객 리스트"

Step 3: Supervisor Agent 생성
  ├── 이름: "customer-support-supervisor"
  ├── 서브 에이전트 1: product-support-ka
  │   └── Description: "제품 사용법, FAQ, 문제 해결 가이드 관련 질문 처리"
  ├── 서브 에이전트 2: order-analytics-genie
  │   └── Description: "주문, 매출, 고객 데이터 조회 및 분석"
  └── Instructions:
      "고객 지원팀을 위한 통합 어시스턴트.
       제품 관련 질문은 product-support-ka로,
       데이터 조회 질문은 order-analytics-genie로 라우팅."

Step 4: 테스트
  ├── "이 제품 설정 방법이 뭐야?" → KA 라우팅 확인
  ├── "지난달 매출 합계 알려줘" → Genie 라우팅 확인
  └── "VIP 고객의 제품 이용 가이드를 정리해줘" → 복합 라우팅 확인

Step 5: 권한 부여 및 배포
  ├── 고객지원팀에 CAN QUERY 권한 부여
  └── AI Playground 또는 API로 서비스
```

---

## 6. 평가와 모니터링

### 6.1 MLflow 기반 평가

Agent Bricks는 MLflow와 긴밀하게 통합되어 에이전트 품질을 체계적으로 평가합니다.

| 기능 | 설명 |
|------|------|
| **Tracing** | 에이전트 실행의 전체 과정을 추적 (Production Monitoring for MLflow 활성화 필요) |
| **AI Judge** | LLM 기반 자동 품질 판정 |
| **Synthetic Task Generation** | 합성 데이터로 대규모 테스트 |
| **라벨링된 데이터셋** | UC 테이블로 Import/Export하여 체계적 관리 |

### 6.2 평가 워크플로우

```
1. 에이전트 생성 후 Build 탭에서 수동 테스트
    ↓
2. AI Playground에서 View Trace로 실행 과정 확인
    ↓
3. Examples 탭에서 라벨링된 질문/가이드라인 추가
    ↓
4. SME에게 공유 링크 전달 → 전문가 피드백 수집
    ↓
5. AI Judge + Synthetic Task Generation으로 자동 평가
    ↓
6. 가이드라인 조정 → 재테스트 → 반복
```

### 6.3 모니터링 포인트

배포 후 지속적으로 모니터링해야 할 항목:

- **응답 품질**: AI Judge 점수 추이
- **라우팅 정확도** (Supervisor): 올바른 서브 에이전트로 위임되는 비율
- **인용 정확도** (KA): 출처가 올바르게 참조되는 비율
- **사용자 피드백**: 좋아요/싫어요 비율
- **응답 지연**: 엔드포인트 응답 시간
- **오류율**: 실패한 쿼리 비율

---

## 7. 배포 및 운영

### 7.1 배포 아키텍처

```
┌─────────────────────────────────────────────────┐
│                 Model Serving                     │
│  ┌───────────────────────────────────────────┐   │
│  │         Supervisor Agent Endpoint          │   │
│  │                                           │   │
│  │  ┌─────────────┐  ┌─────────────────────┐│   │
│  │  │ KA Endpoint  │  │ Genie Space (API)   ││   │
│  │  └──────┬──────┘  └──────────┬──────────┘│   │
│  │         │                     │           │   │
│  │  ┌──────┴──────┐  ┌──────────┴──────────┐│   │
│  │  │Vector Search│  │  SQL Warehouse      ││   │
│  │  │   Index     │  │  (UC Tables)        ││   │
│  │  └─────────────┘  └─────────────────────┘│   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │ UC Functions│  │ MCP Servers│  │  MLflow    │ │
│  └────────────┘  └────────────┘  │  Monitoring │ │
│                                   └────────────┘ │
└─────────────────────────────────────────────────┘
```

### 7.2 엔드포인트 연동 방법

에이전트가 배포되면 다음 방식으로 연동할 수 있습니다.

**REST API (curl) 예시:**

```bash
curl -X POST \
  https://<workspace-url>/serving-endpoints/<endpoint-name>/invocations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "이번 달 매출 현황 알려줘"}
    ]
  }'
```

**Python SDK 예시:**

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="<endpoint-name>",
    messages=[
        {"role": "user", "content": "이번 달 매출 현황 알려줘"}
    ]
)

print(response.choices[0].message.content)
```

### 7.3 워크스페이스 간 마이그레이션

Knowledge Assistant를 다른 워크스페이스로 복제해야 할 경우:

1. 타겟 워크스페이스에 필요한 리소스를 먼저 생성 (Vector Search Index, Volume 등)
2. 소스 워크스페이스에서 SDK로 설정 정보 조회
3. 타겟 워크스페이스에서 `create_knowledge_source` API로 재생성

---

## 8. 베스트 프랙티스

### 8.1 Knowledge Assistant

| 항목 | 권장사항 |
|------|----------|
| **문서 크기** | 50MB 이하로 분할, 큰 문서는 섹션별로 나누기 |
| **문서 형식** | 구조화된 마크다운(md) 또는 잘 포맷된 PDF 권장 |
| **Content Description** | 문서의 도메인, 용도, 대상 사용자를 구체적으로 명시 |
| **Instructions** | 응답 언어, 톤, 인용 규칙 등을 명확히 지정 |
| **Knowledge Source 수** | 관련성 높은 소스만 선별 (최대 10개이지만 적을수록 정확) |
| **동기화** | 문서 업데이트 후 반드시 Sync 실행 |

### 8.2 Genie Spaces

| 항목 | 권장사항 |
|------|----------|
| **테이블/컬럼 설명** | 비즈니스 용어와 동의어를 풍부하게 등록 |
| **JOIN 관계** | 자주 사용되는 조인을 미리 정의 |
| **Sample Questions** | 실제 비즈니스 질문 패턴을 등록 |
| **Instructions** | 응답 형식, 단위(원/달러), 날짜 형식 등 명시 |
| **테이블 수** | 30개 이하, 핵심 테이블만 포함 |
| **모니터링** | 정기적으로 Monitoring 탭 확인 후 Knowledge Store 업데이트 |

### 8.3 Supervisor Agent

| 항목 | 권장사항 |
|------|----------|
| **서브 에이전트 Description** | 담당 업무를 최대한 상세하게 작성 (라우팅 정확도에 직결) |
| **서브 에이전트 수** | 필요한 만큼만 등록 (많을수록 라우팅 복잡도 증가) |
| **권한 설계** | 엔드 유저의 서브 에이전트별 접근 권한을 사전에 설계 |
| **테스트** | 다양한 시나리오로 라우팅 정확도를 검증 |
| **Long-Running Mode** | 복잡한 태스크는 Long-Running Task Mode 활용 |

### 8.4 공통 권장사항

1. **반복적 개선**: 배포 후에도 Examples 탭에서 지속적으로 피드백을 수집하고 가이드라인을 업데이트
2. **권한 최소화**: 필요한 사용자에게만 최소한의 권한 부여
3. **트레이싱 활성화**: Production Monitoring for MLflow를 활성화하여 실행 과정 추적
4. **체계적 평가**: AI Judge + Synthetic Task Generation으로 정기적 품질 측정
5. **리전 확인**: 현재 `us-east-1` 또는 `us-west-2`에서만 사용 가능

---

## 9. 참고 자료

- [Agent Bricks 공식 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/)
- [Knowledge Assistant 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/knowledge-assistant)
- [Supervisor Agent 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor)
- [Genie Spaces 설정 가이드](https://docs.databricks.com/aws/en/genie/set-up)
- [Genie 개요](https://docs.databricks.com/aws/en/genie/)
- [Agent Framework 멀티 에이전트 가이드](https://docs.databricks.com/aws/en/generative-ai/agent-framework/multi-agent-apps)
- [에이전트 시스템 디자인 패턴](https://docs.databricks.com/aws/en/generative-ai/guide/agent-system-design-patterns)
