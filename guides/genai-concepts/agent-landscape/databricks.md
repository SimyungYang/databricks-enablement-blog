# Databricks의 AI Agent 전략

Databricks의 Agent 전략은 다른 벤더와 근본적으로 다릅니다. AWS/Microsoft/Google이 "Agent 인프라/모델을 제공하는" 포지션인 반면, Databricks는 "** 데이터와 Agent의 통합 거버넌스**"를 핵심 가치로 제시합니다.

{% hint style="info" %}
** 학습 목표**
- Databricks Agent 전략의 핵심 차별점("데이터 중심 Agent")을 설명할 수 있다
- Agent Bricks, Supervisor Agent, Mosaic AI Gateway, MLflow 3.0의 역할을 이해한다
- TAO/ALHF 자동 최적화가 기존 Agent 개발과 어떻게 다른지 설명할 수 있다
- 멀티클라우드 환경에서 Databricks Agent 아키텍처를 설계할 수 있다
{% endhint %}

{% hint style="success" %}
** 핵심 메시지**: "Agent의 품질은 데이터의 품질에 의해 결정된다. Databricks는 데이터 준비에서 Agent 배포, 모니터링까지 전체 라이프사이클을 하나의 플랫폼에서 관리한다."
{% endhint %}

---

## 1. 전략 개요 — 데이터 중심 Agent

Databricks의 근본적인 차별화:

| 다른 벤더 | Databricks |
|----------|-----------|
| Agent 빌딩 도구 제공 | Agent가 사용하는 ** 데이터** 까지 통합 관리 |
| 모델 API만 제공 | 데이터 전처리 → 임베딩 → Agent → 평가 ** 전체 파이프라인**|
| 거버넌스는 별도 서비스 | **Unity Catalog 하나로** 데이터 + 모델 + Agent 거버넌스 통합 |
| Agent 품질은 수동 프롬프트 튜닝 | **TAO/ALHF로 자동 최적화**|
| 특정 클라우드에 종속 | **AWS, Azure, GCP 멀티클라우드**|

### 전략 스택

| 계층 | 구성 요소 | 역할 |
|------|----------|------|
| ** 인터페이스**| Databricks Apps, Genie Code, Genie Space | 사용자/애플리케이션 접점 |
| **Agent 빌드 (노코드)**| Agent Bricks (KA, Genie Agent, Supervisor) | 코드 없이 Agent 구축 |
| **Agent 빌드 (프로코드)**| Agent Framework (ChatAgent, LangGraph 통합) | 코드 기반 Agent 개발 |
| ** 모델 관리**| Mosaic AI Gateway (멀티모델 라우팅, Fallback) | 모델 라우팅 및 폴백 |
| ** 배포**| Model Serving (서버리스, 자동 스케일링) | Agent 엔드포인트 배포 |
| ** 관측**| MLflow 3.0 (Tracing, Evaluate, Monitoring) | 추적, 평가, 모니터링 |
| ** 거버넌스**| Unity Catalog (데이터 + 모델 + Agent 거버넌스) | 통합 거버넌스 |
| ** 데이터**| Vector Search, Delta Lake, Lakebase | 데이터 저장 및 검색 |

---

## 2. Agent Bricks — 자동 최적화 Agent 빌더

Agent Bricks는 Databricks의 ** 노코드 Agent 빌더** 로, 2025년 6월 Data+AI Summit에서 GA되었습니다. 가장 혁신적인 기능은 **TAO** 와 **ALHF** 입니다.

### 제품 구성

| 제품 | 설명 | 핵심 기능 |
|------|------|----------|
| **Knowledge Assistant**| RAG 기반 Q&A Agent | Unity Catalog의 테이블/문서를 자동 인덱싱, 검색, 답변 |
| **Genie Agent**| 자연어 → SQL 변환 Agent | Genie Space를 Tool로 호출하여 데이터 분석 |
| **Supervisor Agent**| 멀티에이전트 오케스트레이터 | 하위 Agent들을 코드 없이 조율 |

### TAO (Tool-Augmented Optimization)

기존 Agent 프레임워크에서 Agent의 Tool 선택 정확도를 높이려면 프롬프트를 수동으로 조정해야 합니다. TAO는 이를 ** 자동화** 합니다:

1. Agent가 도구를 호출할 때마다 성공/실패를 추적
2. Tool 선택 패턴을 분석하여 전략을 자동 조정
3. 도메인 특화 합성 데이터를 자동 생성하여 벤치마크 구축

{% hint style="info" %}
** 비유**: TAO는 "Agent의 자동 코치"입니다. 매 경기(Tool 호출)를 분석하고, 전략(프롬프트)을 자동 개선합니다. 코치(프롬프트 엔지니어)가 직접 개입할 필요가 없습니다.
{% endhint %}

### ALHF (Automated Learning from Human Feedback)

최종 사용자가 Agent 응답에 "좋아요/싫어요" 피드백을 남기면:
- ** 좋아요**: 해당 추론 경로(Tool 선택 → 응답 생성)가 강화
- ** 싫어요**: 해당 추론 경로가 약화

{% hint style="success" %}
** 핵심 가치**: 별도 Fine-tuning 파이프라인 없이, ** 프로덕션에서 Agent가 자동으로 개선** 됩니다. RLHF의 엔터프라이즈 버전이라고 볼 수 있습니다.
{% endhint %}

---

## 3. Supervisor Agent — 노코드 멀티에이전트

Supervisor Agent는 Agent Bricks 내에서 ** 코드 없이 멀티에이전트 시스템을 구축** 할 수 있는 기능입니다.

| 구성 요소 | 역할 | 설명 |
|----------|------|------|
| **Supervisor Agent**| 오케스트레이터 | 사용자 요청을 분석하고 하위 Agent에 분배 |
| Knowledge Assistant | 문서 QA | RAG 기반 사내 문서 검색 및 답변 |
| Genie Agent | 데이터 분석 | 자연어 → SQL 변환, Genie Space 활용 |
| Custom Agent | API 연동 | 외부 API 호출, 커스텀 로직 실행 |
| **Unity Catalog**| 통합 거버넌스 | 모든 Agent의 데이터 접근 제어 및 리니지 추적 |

### 설정 과정

1. 하위 Agent(Knowledge Assistant, Genie Agent 등)를 각각 생성
2. Supervisor Agent 생성 시 하위 Agent를 "도구"로 등록
3. 라우팅 규칙(자동/수동) 설정
4. 평가 세트로 전체 시스템 품질 검증
5. Model Serving Endpoint로 배포

### 연결 가능한 도구 유형

| 도구 유형 | 예시 |
|----------|------|
| **Knowledge Assistant**| 사내 문서 Q&A, 규정 검색 |
| **Genie Agent**| 자연어 데이터 분석, BI 질의 |
| **Agent Endpoint**| 커스텀 Agent (ChatAgent/LangGraph) |
| **Unity Catalog Function**| SQL/Python 함수 직접 호출 |
| **MCP Server**| 외부 시스템 연동 (Slack, GitHub, JIRA 등) |

---

## 4. Mosaic AI Gateway — 멀티모델 관리

Mosaic AI Gateway는 Databricks의 ** 중앙집중형 AI 모델 관리 계층** 입니다.

| 기능 | 설명 |
|------|------|
| ** 통합 엔드포인트**| OpenAI, Anthropic, AWS Bedrock, Azure OpenAI, 자체 모델을 하나의 API로 통합 |
| **Rate Limiting**| 사용자/팀별 토큰 할당량 관리 |
| **Cost Tracking**| 모델별, Agent별, 팀별 비용 추적 |
| **Fallback**| Primary 모델 장애 시 자동 Fallback (예: GPT-4o → Claude → Llama 4) |
| **Guardrails**| Unity Catalog 기반 입출력 필터링 |
| **Audit Log**| 모든 LLM 호출 이력을 Unity Catalog에 자동 기록 |

{% hint style="warning" %}
** 왜 Gateway가 중요한가?**

멀티에이전트 시스템에서 각 Agent가 서로 다른 모델을 사용할 수 있습니다. Gateway 없이는:
- 비용 추적이 불가능 (어떤 Agent가 얼마나 소비하는지?)
- 모델 교체가 어려움 (코드 변경 필요)
- 거버넌스 사각지대 (어떤 데이터가 어떤 모델로 흘러갔는지?)

Gateway는 이 모든 문제를 ** 인프라 계층에서 해결** 합니다.
{% endhint %}

---

## 5. MLflow 3.0 — GenAI Observability

MLflow 3.0은 기존 ML 실험 추적 도구에서 **GenAI/Agent 전문 관측 도구** 로 진화했습니다.

| 기능 | 설명 |
|------|------|
| **Trace**| Agent의 전체 실행 흐름을 시각화. Tool 호출, LLM 추론, 검색 결과를 트리 구조로 표시 |
| **GenAI Metrics**| 답변 정확도, 관련성, 충실도, 유해성 등 자동 평가 (@scorer 패턴) |
| **Experiment Tracking**| 프롬프트 버전, 모델 버전, Tool 구성 등을 실험 단위로 관리 |
| **Prompt Registry**| 프롬프트를 코드처럼 버전 관리, 팀 협업 |
| **Model Registry**| Agent를 버전 관리하고, 스테이지(Staging → Production)를 전환 |
| **Production Monitoring**| 배포 후 실시간 품질 드리프트 감지, 알럿 |

{% hint style="info" %}
**MLflow 3.0의 Agent 추적 예시**: Agent가 "지난 분기 매출 분석해줘"라는 요청을 처리할 때, Trace에서 다음을 확인할 수 있습니다:
1. LLM이 요청을 분석한 추론 과정
2. SQL 도구를 선택한 이유
3. 실행된 SQL 쿼리와 결과
4. 최종 응답 생성 과정
5. 각 단계의 토큰 사용량과 지연시간
{% endhint %}

---

## 6. 멀티에이전트 아키텍처

Databricks의 멀티에이전트 전략은 "** 데이터 중심 오케스트레이션**"입니다.

| 계층 | 구성 요소 | 역할 |
|------|----------|------|
| ** 데이터**| Unity Catalog, Delta Lake, Vector Search | Agent가 사용하는 모든 데이터의 단일 소스 |
| ** 빌드**| Agent Bricks, Agent Framework, AI Dev Kit | 노코드/프로코드 Agent 개발 |
| ** 서빙**| Model Serving, Mosaic AI Gateway | 배포, 라우팅, 폴백 |
| ** 관측**| MLflow 3.0, Lakehouse Monitoring | 추적, 평가, 드리프트 감지 |
| ** 거버넌스**| Unity Catalog ACL, Audit Log | 권한, 감사, 리니지 |

### 다른 벤더와의 통합 패턴

Databricks는 모델 중립적이므로, 다른 벤더의 모델/서비스와 자연스럽게 결합됩니다:

| 통합 패턴 | 설명 |
|----------|------|
| **OpenAI 모델 + Databricks**| GPT-4.1/Claude를 Gateway 경유로 호출, Agent Bricks에서 백엔드 모델로 사용 |
| **AWS Bedrock + Databricks**| Bedrock 모델을 External Model로 등록, Unity Catalog 거버넌스 적용 |
| **Llama 4 자체 호스팅**| Model Serving에 Llama 4 배포, 데이터 주권 확보 |
| **LangGraph + Databricks**| LangGraph로 복잡한 워크플로 구축, Databricks에서 배포/모니터링 |
| **MCP + Genie Code**| 외부 MCP 서버를 Genie Code에 연결, Unity Catalog Connection 경유 |

---

## 7. 차별점 요약 — 왜 Databricks인가?

| 차별점 | 설명 | 다른 벤더 대비 |
|--------|------|--------------|
| ** 데이터-Agent 통합**| 데이터 준비에서 Agent 배포까지 하나의 플랫폼 | AWS/Azure는 데이터와 Agent 서비스가 분리 |
| **Unity Catalog 거버넌스**| 데이터, 모델, Agent, Feature를 하나의 카탈로그로 관리 | 타 벤더는 데이터 거버넌스와 AI 거버넌스가 별도 |
| **TAO/ALHF 자동 최적화**| 프로덕션에서 Agent가 자동으로 개선 | 타 벤더는 수동 프롬프트 튜닝 의존 |
| ** 모델 중립**| 어떤 Foundation Model이든 사용 가능 (Gateway 경유) | AWS는 Bedrock 모델 중심, MS는 OpenAI 중심 |
| **MLflow 3.0**| 오픈소스 기반 GenAI 관측의 사실상 표준 | 타 벤더는 독자 모니터링 도구 |
| ** 멀티클라우드**| AWS, Azure, GCP 어디서든 동일한 Agent 경험 | AWS/Azure/GCP 각각 자사 클라우드 종속 |

---

## 8. 고객 시나리오별 권장 아키텍처

| 시나리오 | 권장 구성 | 이유 |
|---------|----------|------|
| ** 사내 문서 Q&A 챗봇**| Knowledge Assistant + Vector Search | 가장 빠른 구현, 노코드, UC 권한 자동 적용 |
| ** 데이터 분석 챗봇**| Genie Agent + SQL Warehouse | 자연어 → SQL, 기존 데이터 자산 활용 |
| ** 복합 업무 자동화**| Supervisor Agent (KA + Genie + Custom) | 문서 검색 + 데이터 분석 + API 호출 통합 |
| ** 코딩 에이전트**| Genie Code + MCP 서버 | GitHub, Slack, JIRA 연동 |
| ** 커스텀 Agent**| ChatAgent + LangGraph + MLflow | 최대 유연성, 복잡한 워크플로 |
| ** 멀티클라우드 통합**| Gateway + Agent Bricks + MLflow | 클라우드 간 일관된 Agent 경험 |

---

## 9. 고객이 자주 묻는 질문

### Q1: "Agent Bricks vs Agent Framework — 뭘 써야 하나요?"

{% hint style="info" %}
- **Agent Bricks**: 노코드, 빠른 구현, RAG/SQL/멀티에이전트의 표준 패턴에 적합. ** 대부분의 사용 사례는 여기서 해결**.
- **Agent Framework (ChatAgent)**: 코드 기반, 커스텀 로직이 필요한 경우. LangGraph 통합, 복잡한 조건 분기, 외부 API 연동.
- ** 권장**: Agent Bricks로 시작 → 한계가 느껴지면 Agent Framework로 전환.
{% endhint %}

### Q2: "Databricks가 모델도 만드나요? DBRX는?"

{% hint style="info" %}
DBRX는 Databricks가 만든 오픈웨이트 모델이지만, Databricks의 Agent 전략은 ** 모델 중립** 입니다. GPT-4.1, Claude, Gemini, Llama 4 등 어떤 모델이든 Gateway를 통해 사용할 수 있습니다.

Databricks의 핵심 가치는 "최고의 모델을 만드는 것"이 아니라, "어떤 모델을 쓰든 데이터 거버넌스와 Agent 품질을 보장하는 것"입니다.
{% endhint %}

### Q3: "MLflow 3.0은 LangSmith와 뭐가 다른가요?"

{% hint style="info" %}
| 비교 | MLflow 3.0 | LangSmith |
|------|-----------|-----------|
| 라이선스 | 오픈소스 | 상용 |
| 프레임워크 | 프레임워크 무관 | LangChain/LangGraph 최적화 |
| 데이터 거버넌스 | Unity Catalog 통합 | 없음 |
| 실험 추적 | ML + GenAI 통합 | GenAI 전용 |
| 모델 레지스트리 | 포함 | 없음 |

LangGraph를 사용하더라도, **Databricks 환경에서는 MLflow 3.0을 권장** 합니다. Unity Catalog와의 통합으로 데이터 리니지까지 추적할 수 있습니다.
{% endhint %}

### Q4: "타 벤더 Agent 플랫폼과 비교했을 때 Databricks를 선택해야 하는 결정적 이유는?"

{% hint style="info" %}
** 한 문장 요약**: "Agent가 아무리 잘 만들어져도, 사용하는 데이터가 잘못되면 쓸모없다."

Databricks만이 ** 데이터 준비(ETL) → 임베딩/벡터화 → Agent 개발 → 평가 → 배포 → 모니터링 → 거버넌스** 전체를 하나의 플랫폼에서 관리합니다. 다른 벤더는 각 단계마다 다른 서비스를 조합해야 합니다.

특히 **Unity Catalog 하나로** 데이터 접근 제어, 모델 거버넌스, Agent 감사가 통합되는 것은 규제 환경(금융, 의료, 공공)에서 결정적 장점입니다.
{% endhint %}

---

## 10. 참고 자료

- [Databricks Agent Bricks 문서](https://docs.databricks.com/en/generative-ai/agent-bricks/index.html)
- [Databricks Supervisor Agent](https://docs.databricks.com/en/generative-ai/agent-bricks/multi-agent-supervisor.html)
- [Mosaic AI Gateway](https://docs.databricks.com/en/generative-ai/external-models/index.html)
- [MLflow 3.0 GenAI](https://mlflow.org/docs/latest/genai/index.html)
- [Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
- [Databricks Agent Framework (ChatAgent)](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
- [Agent Bricks TAO/ALHF (InfoQ)](https://www.infoq.com/news/2025/07/databricks-agent-bricks-platform/)
- [Mosaic AI Announcements at Data+AI Summit 2025](https://www.databricks.com/blog/mosaic-ai-announcements-data-ai-summit-2025)

---

## 다음 단계

- [Agent Bricks 상세 가이드](../../agent-bricks/README.md): Knowledge Assistant, Genie Agent, Supervisor 구축 가이드
- [Agent 프레임워크 생태계](../agent-frameworks.md): LangGraph, CrewAI 등과의 비교
- [Agent UI & 배포](../agent-ui-stack.md): Streamlit, Databricks Apps로 Agent 배포
- [MCP 활용](../../mcp/databricks-mcp.md): Databricks 환경에서 MCP 서버 연동
