# Databricks Agent Bricks 실전 가이드

> **Agent Bricks**는 Databricks Mosaic AI 기반의 선언형(Declarative) AI 에이전트 빌더입니다.
> 코드 없이도 프로덕션 수준의 AI 에이전트를 빠르게 구축, 평가, 배포할 수 있습니다.

---

## Agent Bricks란?

Agent Bricks는 기술/비기술 팀 모두가 자사의 데이터를 **프로덕션 수준의 AI 에이전트**로 운영할 수 있도록 해주는 플랫폼입니다. 핵심 특징은 다음과 같습니다.

| 특징 | 설명 |
|------|------|
| **선언형 에이전트 빌드** | 자연어와 사전 구성된 템플릿으로 에이전트 정의 |
| **내장 MLflow 평가** | 에이전트 품질을 자동으로 측정 |
| **Unity Catalog 거버넌스** | 데이터 접근 권한을 통합 관리 |
| **AI Gateway 모델 유연성** | 다양한 모델/프레임워크 지원 |
| **MCP 카탈로그 통합** | 외부 도구 확장 가능 |
| **자동 최적화** | 모델 선택, 파인 튜닝, 하이퍼파라미터 최적화를 백그라운드에서 자동 수행 |

---

## 작동 원리 (3단계)

```
1단계: 유스케이스와 데이터 정의
    ↓
2단계: 시스템이 자동으로 모델 테스트, 파인 튜닝, 최적화
    ↓
3단계: 백그라운드에서 지속 최적화 (더 나은 모델 발견 시 알림)
```

---

## 에이전트 유형 비교

Agent Bricks에서 지원하는 에이전트 유형은 6가지입니다.

| 유형 | 설명 | 주요 용도 |
|------|------|-----------|
| **Knowledge Assistant** | 문서 기반 Q&A 챗봇 (RAG + 인용) | 제품 문서, HR 정책, 고객지원 |
| **Genie Spaces** | 테이블을 자연어 챗봇으로 변환 | 데이터 탐색, 비즈니스 분석 |
| **Supervisor Agent** | 여러 에이전트를 조율하는 멀티 에이전트 시스템 | 복합 업무 자동화, 시장 분석 |
| **Information Extraction** (Beta) | 비정형 문서에서 구조화된 데이터 추출 | 분류, 데이터 구조화 |
| **Custom LLM** (Beta) | 요약, 텍스트 변환 | 문서 요약, 텍스트 처리 |
| **Code Your Own Agent** | 오픈소스 라이브러리와 Agent Framework 활용 | 완전 맞춤형 에이전트 |

### 어떤 유형을 선택해야 하나?

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

---

## 사전 요구사항

모든 Agent Bricks 유형에 공통으로 필요한 조건입니다.

- **Mosaic AI Agent Bricks Preview (Beta)** 가 워크스페이스에서 활성화
- **Unity Catalog** 활성화
- **Serverless Compute** 사용 가능 (Unity Catalog 활성화 시 기본 제공)
- **Foundation Model** 접근 가능 (`system.ai` 스키마)
- **Serverless Budget Policy** 에 0이 아닌 예산 할당
- **리전**: `us-east-1` 또는 `us-west-2`

---

## 참고 자료

- [Agent Bricks 공식 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/)
- [Knowledge Assistant 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/knowledge-assistant)
- [Supervisor Agent 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor)
- [Genie Spaces 설정 가이드](https://docs.databricks.com/aws/en/genie/set-up)
- [Genie 개요](https://docs.databricks.com/aws/en/genie/)
- [Agent Framework 멀티 에이전트 가이드](https://docs.databricks.com/aws/en/generative-ai/agent-framework/multi-agent-apps)
- [에이전트 시스템 디자인 패턴](https://docs.databricks.com/aws/en/generative-ai/guide/agent-system-design-patterns)
