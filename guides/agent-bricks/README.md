# Databricks Agent Bricks 실전 가이드

> **Agent Bricks**는 Databricks Mosaic AI 기반의 선언형(Declarative) AI 에이전트 빌더입니다.
> 코드 없이도 프로덕션 수준의 AI 에이전트를 빠르게 구축, 평가, 배포할 수 있습니다.

---

## Agent Bricks란?

Agent Bricks는 기술/비기술 팀 모두가 자사의 데이터를 **프로덕션 수준의 AI 에이전트**로 운영할 수 있도록 해주는 플랫폼입니다. 기존의 에이전트 개발이 프롬프트 엔지니어링, 모델 선택, RAG 파이프라인 구축, 평가 프레임워크 설정 등 수많은 단계를 요구했다면, Agent Bricks는 이 모든 것을 **선언형 인터페이스**뒤에서 자동으로 처리합니다.

핵심 특징은 다음과 같습니다.

| 특징 | 설명 |
|------|------|
| **선언형 에이전트 빌드**| 자연어와 사전 구성된 템플릿으로 에이전트 정의 — 코드 불필요 |
| **내장 MLflow 평가**| AI Judge, Synthetic Task Generation으로 에이전트 품질을 자동 측정 |
| **Unity Catalog 거버넌스**| 데이터 접근 권한을 통합 관리, 엔드 유저 수준의 세밀한 제어 |
| **AI Gateway 모델 유연성**| Claude, GPT-4o, Llama 등 다양한 모델/프레임워크 지원 |
| **MCP 카탈로그 통합**| 외부 도구(Slack, JIRA, GitHub 등)를 MCP 서버로 확장 |
| **자동 최적화**| 모델 선택, 파인 튜닝, 하이퍼파라미터 최적화를 백그라운드에서 자동 수행 |

{% hint style="info" %}
Agent Bricks는 **Mosaic AI Agent Framework**위에 구축되어 있습니다. Agent Framework의 MLflow Tracing, Model Serving, 평가 인프라를 그대로 활용하면서, UI 기반의 선언형 빌더를 추가한 것입니다.
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
| **Knowledge Assistant**| 문서 기반 Q&A 챗봇 (RAG + 인용) | 제품 문서, HR 정책, 고객지원 | 낮음 |
| **Genie Spaces**| 테이블을 자연어 챗봇으로 변환 | 데이터 탐색, 비즈니스 분석 | 낮음 |
| **Supervisor Agent**| 여러 에이전트를 조율하는 멀티 에이전트 시스템 | 복합 업무 자동화, 시장 분석 | 중간 |
| **Information Extraction**(Beta) | 비정형 문서에서 구조화된 데이터 추출 | 분류, 데이터 구조화 | 낮음 |
| **Custom LLM**(Beta) | 요약, 텍스트 변환 | 문서 요약, 텍스트 처리 | 낮음 |
| **Code Your Own Agent**| 오픈소스 라이브러리와 Agent Framework 활용 | 완전 맞춤형 에이전트 | 높음 |

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
**단독 에이전트 vs 멀티 에이전트**: 단일 도메인의 단순한 작업이라면 Knowledge Assistant 또는 Genie Spaces 하나로 충분합니다. Supervisor Agent는 **서로 다른 데이터 소스/역할을 조합**해야 할 때만 사용하세요. 불필요하게 복잡한 아키텍처는 라우팅 오류와 디버깅 비용을 증가시킵니다.
{% endhint %}

---

## 사전 요구사항 체크리스트

모든 Agent Bricks 유형에 공통으로 필요한 조건입니다. 시작 전 아래 항목을 확인하세요.

| # | 요구사항 | 확인 방법 |
|---|----------|-----------|
| 1 | **Mosaic AI Agent Bricks Preview**활성화 | 워크스페이스 관리자에게 요청 또는 Preview 페이지에서 활성화 |
| 2 | **Unity Catalog**활성화 | 워크스페이스 설정 > Data Access Configuration 확인 |
| 3 | **Serverless Compute**사용 가능 | UC 활성화 시 기본 제공 |
| 4 | **Foundation Model**접근 가능 | `system.ai` 스키마에 대한 `USE SCHEMA` 권한 확인 |
| 5 | **Serverless Budget Policy**설정 | 0이 아닌 예산이 할당되어 있어야 함 |
| 6 | **리전**확인 | `us-east-1` 또는 `us-west-2`에서만 사용 가능 |
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
**Knowledge Assistant가 가장 쉽습니다.**문서(PDF, MD)만 업로드하면 즉시 RAG 기반 Q&A 챗봇이 생성됩니다. 먼저 KA로 Agent Bricks의 전체 워크플로우를 경험한 후, Genie Spaces나 Supervisor Agent로 확장하는 것을 권장합니다.
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
