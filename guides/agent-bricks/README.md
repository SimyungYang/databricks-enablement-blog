# Databricks Agent Bricks 실전 가이드

> **Agent Bricks** 는 Databricks Mosaic AI 기반의 선언형(Declarative) AI 에이전트 빌더입니다.
> 코드 없이도 프로덕션 수준의 AI 에이전트를 빠르게 구축, 평가, 배포할 수 있습니다.

---

## Agent Bricks란?

Agent Bricks는 기술/비기술 팀 모두가 자사의 데이터를 **프로덕션 수준의 AI 에이전트** 로 운영할 수 있도록 해주는 플랫폼입니다. 기존의 에이전트 개발이 프롬프트 엔지니어링, 모델 선택, RAG 파이프라인 구축, 평가 프레임워크 설정 등 수많은 단계를 요구했다면, Agent Bricks는 이 모든 것을 **선언형 인터페이스** 뒤에서 자동으로 처리합니다.

핵심 특징은 다음과 같습니다.

| 특징 | 설명 |
|------|------|
| **선언형 에이전트 빌드** | 자연어와 사전 구성된 템플릿으로 에이전트 정의 — 코드 불필요 |
| **내장 MLflow 평가** | AI Judge, Synthetic Task Generation으로 에이전트 품질을 자동 측정 |
| **Unity Catalog 거버넌스** | 데이터 접근 권한을 통합 관리, 엔드 유저 수준의 세밀한 제어 |
| **AI Gateway 모델 유연성** | Claude, GPT-4o, Llama 등 다양한 모델/프레임워크 지원 |
| **MCP 카탈로그 통합** | 외부 도구(Slack, JIRA, GitHub 등)를 MCP 서버로 확장 |
| **자동 최적화** | 모델 선택, 파인 튜닝, 하이퍼파라미터 최적화를 백그라운드에서 자동 수행 |

{% hint style="info" %}
Agent Bricks는 **Mosaic AI Agent Framework** 위에 구축되어 있습니다. Agent Framework의 MLflow Tracing, Model Serving, 평가 인프라를 그대로 활용하면서, UI 기반의 선언형 빌더를 추가한 것입니다.
{% endhint %}

---

## 작동 원리 (3단계)

```
1단계: 유스케이스와 데이터 정의
    ↓  에이전트 유형 선택, 데이터 소스 연결, 인스트럭션 작성
2단계: 시스템이 자동으로 모델 테스트, 파인 튜닝, 최적화
    ↓  백그라운드에서 여러 모델/설정 조합을 평가
3단계: 백그라운드에서 지속 최적화 (더 나은 모델 발견 시 알림)
    ↓  새 모델 출시, 데이터 변경 시 자동 재최적화
```

---

## 에이전트 유형 비교

Agent Bricks에서 지원하는 에이전트 유형은 6가지입니다.

| 유형 | 설명 | 주요 용도 | 난이도 |
|------|------|-----------|--------|
| **Knowledge Assistant** | 문서 기반 Q&A 챗봇 (RAG + 인용) | 제품 문서, HR 정책, 고객지원 | 낮음 |
| **Genie Spaces** | 테이블을 자연어 챗봇으로 변환 | 데이터 탐색, 비즈니스 분석 | 낮음 |
| **Supervisor Agent** | 여러 에이전트를 조율하는 멀티 에이전트 시스템 | 복합 업무 자동화, 시장 분석 | 중간 |
| **Information Extraction**(Beta) | 비정형 문서에서 구조화된 데이터 추출 | 분류, 데이터 구조화 | 낮음 |
| **Custom LLM**(Beta) | 요약, 텍스트 변환 | 문서 요약, 텍스트 처리 | 낮음 |
| **Code Your Own Agent** | 오픈소스 라이브러리와 Agent Framework 활용 | 완전 맞춤형 에이전트 | 높음 |

---

## 어떤 유형을 선택해야 하나? (의사결정 플로우차트)

```
시작: "어떤 AI 에이전트가 필요한가?"
│
├─ "사내 문서에 대해 질문/답변이 필요하다"
│   └→ Knowledge Assistant
│
├─ "테이블 데이터를 자연어로 탐색하고 싶다"
│   └→ Genie Spaces
│
├─ "여러 에이전트를 조합해 복잡한 업무를 처리해야 한다"
│   └→ Supervisor Agent (Multi-Agent)
│       ├─ 문서 Q&A + 데이터 분석 조합 → KA + Genie를 서브 에이전트로
│       └─ 문서 Q&A + 외부 API 호출 → KA + UC Function/MCP 조합
│
├─ "비정형 문서에서 정보를 추출해 테이블로 만들고 싶다"
│   └→ Information Extraction
│
├─ "텍스트 요약/변환 파이프라인이 필요하다"
│   └→ Custom LLM
│
└─ "위 유형에 해당하지 않는 커스텀 로직이 필요하다"
    └→ Code Your Own Agent
        (LangGraph, CrewAI, AutoGen 등 자유롭게 사용)
```

{% hint style="warning" %}
**단독 에이전트 vs 멀티 에이전트**: 단일 도메인의 단순한 작업이라면 Knowledge Assistant 또는 Genie Spaces 하나로 충분합니다. Supervisor Agent는 **서로 다른 데이터 소스/역할을 조합** 해야 할 때만 사용하세요. 불필요하게 복잡한 아키텍처는 라우팅 오류와 디버깅 비용을 증가시킵니다.
{% endhint %}

---

## 사전 요구사항 체크리스트

모든 Agent Bricks 유형에 공통으로 필요한 조건입니다. 시작 전 아래 항목을 확인하세요.

| # | 요구사항 | 확인 방법 |
|---|----------|-----------|
| 1 | **Mosaic AI Agent Bricks Preview** 활성화 | 워크스페이스 관리자에게 요청 또는 Preview 페이지에서 활성화 |
| 2 | **Unity Catalog** 활성화 | 워크스페이스 설정 > Data Access Configuration 확인 |
| 3 | **Serverless Compute** 사용 가능 | UC 활성화 시 기본 제공 |
| 4 | **Foundation Model** 접근 가능 | `system.ai` 스키마에 대한 `USE SCHEMA` 권한 확인 |
| 5 | **Serverless Budget Policy** 설정 | 0이 아닌 예산이 할당되어 있어야 함 |
| 6 | **리전** 확인 | `us-east-1` 또는 `us-west-2`에서만 사용 가능 |
| 7 | **SQL Warehouse**(Genie 사용 시) | Pro 또는 Serverless SQL Warehouse 필요 |
| 8 | **Vector Search Endpoint**(KA 사용 시) | 자동 생성되지만 기존 엔드포인트 사용도 가능 |

{% hint style="danger" %}
**리전 제한**: Agent Bricks는 현재 `us-east-1`과 `us-west-2`에서만 사용 가능합니다. 다른 리전의 워크스페이스에서는 Agent Bricks 메뉴가 표시되지 않습니다.
{% endhint %}

---

## 빠른 시작 가이드

Agent Bricks를 처음 사용한다면 다음 순서를 추천합니다.

| 단계 | 작업 | 소요 시간 |
|------|------|-----------|
| 1 | 사전 요구사항 확인 (위 체크리스트) | 10분 |
| 2 | Knowledge Assistant로 첫 에이전트 생성 | 15분 |
| 3 | Build 탭에서 수동 테스트 (5~10개 질문) | 10분 |
| 4 | View Trace로 동작 원리 이해 | 5분 |
| 5 | Instructions/Examples 추가로 품질 개선 | 20분 |
| 6 | AI Judge로 평가 → 배포 | 15분 |

{% hint style="info" %}
**Knowledge Assistant가 가장 쉽습니다.** 문서(PDF, MD)만 업로드하면 즉시 RAG 기반 Q&A 챗봇이 생성됩니다. 먼저 KA로 Agent Bricks의 전체 워크플로우를 경험한 후, Genie Spaces나 Supervisor Agent로 확장하는 것을 권장합니다.
{% endhint %}

---

## 참고 자료

- [Agent Bricks 공식 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/)
- [Knowledge Assistant 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/knowledge-assistant)
- [Supervisor Agent 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor)
- [Genie Spaces 설정 가이드](https://docs.databricks.com/aws/en/genie/set-up)
- [Genie 개요](https://docs.databricks.com/aws/en/genie/)
- [Agent Framework 멀티 에이전트 가이드](https://docs.databricks.com/aws/en/generative-ai/agent-framework/multi-agent-apps)
- [에이전트 시스템 디자인 패턴](https://docs.databricks.com/aws/en/generative-ai/guide/agent-system-design-patterns)

---

## 왜 노코드 Agent 빌더가 필요한가?

AI 에이전트를 프로덕션에 배포하는 것은 **프로토타입 만들기와 전혀 다른 차원** 의 문제입니다. 실제 기업 환경에서 에이전트를 운영하려면 아래와 같은 복합적인 엔지니어링 과제를 모두 해결해야 합니다.

| 단계 | 코드 기반(Agent Framework) | Agent Bricks (노코드) |
|------|---------------------------|----------------------|
| **RAG 파이프라인** | Vector Search Index 생성, 청킹 전략 설계, 임베딩 모델 선택을 직접 코딩 | 문서 업로드만 하면 자동 구성 |
| **프롬프트 엔지니어링** | System Prompt, Few-shot Example, Chain-of-Thought 등을 수동 설계 | Instructions와 Examples를 UI에서 입력 |
| **모델 선택** | 각 모델의 가격/성능/지연 시간을 비교 테스트 | 시스템이 자동으로 여러 모델을 테스트하고 최적 선택 |
| **평가** | MLflow Evaluate 코드 작성, 평가 데이터셋 수동 생성 | AI Judge + Synthetic Task Generation 내장 |
| **배포** | Model Serving 엔드포인트 코드, 스케일링 설정 | 자동 배포, 자동 스케일링 |
| **모니터링** | Tracing 코드 삽입, 대시보드 구축 | 내장 Tracing + Production Monitoring |
| **거버넌스** | UC 권한 관리 코드 작성 | Unity Catalog 자동 통합 |

이 모든 작업을 코드로 직접 구현하면 **최소 2~4주** 의 개발 기간이 필요합니다. Agent Bricks는 이를 **15분** 으로 단축합니다. 단, 이것이 "코드 기반이 불필요하다"는 의미는 아닙니다. 아래에서 두 접근법의 선택 기준을 설명합니다.

---

## Agent Bricks vs Agent Framework: 선택 기준

Databricks는 AI 에이전트 구축을 위해 **두 가지 경로** 를 제공합니다. **Agent Bricks**(선언형, 노코드)와 **Agent Framework**(코드 기반, 프로그래밍)입니다. 둘 다 동일한 Mosaic AI 인프라(MLflow, Model Serving, Unity Catalog) 위에서 작동하지만, 사용 방식과 적합한 시나리오가 다릅니다.

### 비교표

| 기준 | Agent Bricks | Agent Framework |
|------|-------------|----------------|
| **개발 방식** | UI 기반 선언형 — 코드 불필요 | Python 코드 기반 — LangGraph, CrewAI, AutoGen 등 |
| **대상 사용자** | 비즈니스 분석가, 도메인 전문가, 시민 개발자 | ML 엔지니어, 소프트웨어 엔지니어 |
| **커스터마이징** | Instructions, Examples, Knowledge Source로 제어 | 코드 수준의 완전한 제어 (프롬프트, 체인, 도구 호출 로직) |
| **지원 에이전트 유형** | 6가지 사전 정의 유형 (KA, Genie, Supervisor 등) | 제한 없음 — 모든 아키텍처 가능 |
| **RAG 파이프라인** | 자동 구성 (문서 업로드 → 자동 청킹/인덱싱) | 직접 설계 (청킹 전략, 임베딩 모델, 검색 파라미터 제어) |
| **멀티 에이전트** | Supervisor Agent (최대 20개 서브 에이전트) | 무제한 에이전트 조합, 커스텀 오케스트레이션 |
| **외부 도구** | UC Functions + MCP Servers | UC Functions + MCP + 임의의 Python 함수 |
| **자동 최적화** | 모델 선택, 파인 튜닝 자동 수행 | 수동으로 실험 및 최적화 |
| **배포 속도** | 수십 분 | 수일~수주 |
| **유지보수** | 인프라 관리 불필요 | 코드 유지보수, 의존성 관리 필요 |

### 시나리오별 권장 경로

| 시나리오 | 권장 경로 | 이유 |
|----------|----------|------|
| 사내 문서 Q&A 챗봇 (첫 AI 프로젝트) | **Agent Bricks** | KA로 15분 만에 프로덕션 수준 RAG 챗봇 구축 가능 |
| 비즈니스 데이터 자연어 탐색 | **Agent Bricks** | Genie Space가 이 유스케이스에 최적화 |
| 3~5개 에이전트 조합 멀티 에이전트 | **Agent Bricks** | Supervisor Agent로 노코드 오케스트레이션 |
| 복잡한 조건 분기 + 외부 API 연동 | **Agent Framework** | 커스텀 체인 로직, 조건부 도구 호출 필요 |
| 실시간 스트리밍 데이터 처리 에이전트 | **Agent Framework** | Agent Bricks는 스트리밍 미지원 |
| 기존 LangChain/LangGraph 앱 마이그레이션 | **Agent Framework** | 기존 코드를 그대로 활용 가능 |
| 커스텀 파인 튜닝 + 모델 앙상블 | **Agent Framework** | 모델 레벨 제어 필요 |
| 빠른 POC 후 점진적 고도화 | **Agent Bricks → Framework** | Bricks로 빠르게 검증 후, 한계에 부딪히면 Framework로 전환 |

{% hint style="info" %}
**하이브리드 접근법**: Agent Bricks의 Supervisor Agent에서 **Code Your Own Agent** 유형을 서브 에이전트로 연결할 수 있습니다. 즉, 대부분의 에이전트는 노코드로 구축하고, 특수한 로직이 필요한 부분만 코드로 작성하는 **하이브리드 아키텍처** 가 가능합니다.
{% endhint %}

---

## Agent Bricks의 전략적 포지셔닝

### Databricks AI 전략에서의 위치

Agent Bricks는 Databricks의 **"AI를 민주화한다"** 는 비전의 핵심 실행 수단입니다. 기존에는 ML 엔지니어만 AI 에이전트를 구축할 수 있었지만, Agent Bricks를 통해 **비즈니스 분석가, 도메인 전문가, 데이터 분석가** 도 프로덕션 수준의 에이전트를 직접 만들 수 있게 됩니다.

```
Databricks AI 스택 전체 구조

┌─────────────────────────────────────────────────────────┐
│  소비 계층 (Consumption Layer)                            │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  │
│  │ Agent Bricks │  │  Genie Code   │  │  AI/BI       │  │
│  │  (노코드)    │  │  (자연어→코드)│  │  Dashboard   │  │
│  └──────┬───────┘  └───────┬───────┘  └──────┬───────┘  │
├─────────┼──────────────────┼──────────────────┼──────────┤
│  개발 계층 (Development Layer)                            │
│  ┌──────┴──────────────────┴──────────────────┴───────┐  │
│  │          Mosaic AI Agent Framework                  │  │
│  │  (MLflow, Model Serving, Tracing, Evaluation)      │  │
│  └──────────────────────┬─────────────────────────────┘  │
├─────────────────────────┼────────────────────────────────┤
│  인프라 계층 (Infrastructure Layer)                       │
│  ┌──────────────────────┴─────────────────────────────┐  │
│  │  Unity Catalog · Vector Search · AI Gateway        │  │
│  │  Foundation Models · MCP Catalog · Serverless      │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 경쟁 플랫폼과의 비교

| 비교 항목 | Databricks Agent Bricks | AWS Bedrock Agents | Azure AI Agent Service | Google Vertex AI Agent Builder |
|-----------|------------------------|-------------------|----------------------|------------------------------|
| **거버넌스** | Unity Catalog 통합 (행/열 수준 보안) | IAM 기반 | Entra ID 기반 | IAM 기반 |
| **데이터 접근** | Lakehouse 네이티브 (Delta, UC) | S3 + Knowledge Base | Cosmos DB, Azure Search | BigQuery, Vertex Search |
| **멀티 에이전트** | Supervisor Agent (내장) | Step Functions 조합 | Semantic Kernel 기반 | Agent-to-Agent Protocol |
| **SQL 분석** | Genie Space (네이티브) | Athena 연동 필요 | Fabric 연동 필요 | BigQuery 연동 필요 |
| **자동 최적화** | 모델 자동 선택 + 파인 튜닝 | 수동 | 수동 | 수동 |
| **평가** | AI Judge + Synthetic Tasks 내장 | 외부 도구 필요 | 외부 도구 필요 | 외부 도구 필요 |
| **오픈소스 호환** | MLflow, LangGraph, CrewAI 등 | 독점 API | Semantic Kernel | LangChain 통합 |

{% hint style="info" %}
Agent Bricks의 가장 큰 차별점은 **Lakehouse 네이티브** 라는 점입니다. 데이터가 이미 Databricks에 있다면, 별도의 ETL이나 데이터 복사 없이 바로 에이전트로 활용할 수 있습니다. Unity Catalog의 거버넌스가 에이전트까지 자동 확장되므로 **데이터 보안과 규제 준수** 가 기본으로 보장됩니다.
{% endhint %}

### 도입 전략: 단계적 확장 로드맵

Agent Bricks를 조직에 성공적으로 도입하려면 단계적으로 확장하는 것이 중요합니다.

| 단계 | 기간 | 목표 | 세부 활동 |
|------|------|------|-----------|
| **1단계: POC** | 1~2주 | 가치 검증 | 단일 유스케이스(KA 또는 Genie)로 빠르게 구축, SME 피드백 수집 |
| **2단계: 파일럿** | 2~4주 | 품질 확보 | 평가 체계 구축(AI Judge + 50개 이상 테스트), Instructions 최적화 |
| **3단계: 확장** | 1~2개월 | 멀티 에이전트 | Supervisor로 여러 에이전트 통합, MCP/UC Function 연동 |
| **4단계: 거버넌스** | 지속 | 운영 안정화 | 모니터링 대시보드, 비용 관리, 권한 체계 확립, 장애 대응 절차 |

### 성공적인 Agent Bricks 프로젝트의 3가지 핵심 조건

1. **데이터 품질이 곧 에이전트 품질**: Agent Bricks가 아무리 잘 만들어져도, 원본 데이터(문서, 테이블)가 부실하면 에이전트도 부실합니다. 먼저 데이터 정리와 메타데이터 보강에 투자하세요.
2. **평가 체계를 먼저 구축**: 에이전트를 만들기 전에 "무엇이 좋은 응답인가"를 정의하세요. AI Judge의 Correctness, Groundedness 기준을 명확히 하고, 최소 50개의 테스트 케이스를 준비하세요.
3. **점진적 복잡도 증가**: KA 하나로 시작 → 평가 통과 → Genie 추가 → Supervisor 통합 순서로 진행하세요. 처음부터 멀티 에이전트를 구축하면 디버깅이 극도로 어려워집니다.
