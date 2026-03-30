# Builder App (AI Playground)

## Databricks Builder App이란?

Databricks **AI Playground**는 Workspace 내에서 생성형 AI 에이전트를 **노코드/로우코드**로 프로토타이핑하고 테스트할 수 있는 통합 환경입니다. 코드 한 줄 없이 LLM을 비교하고, Tool을 연결하고, 에이전트를 구축한 뒤 바로 배포할 수 있습니다.

{% hint style="info" %}
AI Playground는 이전에 "Agent Builder"로도 불렸으며, 현재는 Databricks Agent Framework의 노코드 진입점 역할을 합니다.
{% endhint %}

---

## 주요 기능

### 1. LLM 비교 & 테스트

- 다양한 Foundation Model(Meta Llama, Anthropic Claude, OpenAI GPT 등)을 선택하여 프롬프트를 전송합니다.
- **Side-by-side 비교**: 두 개 이상의 모델을 동시에 호출하고 결과를 나란히 비교할 수 있습니다.
- **Sync 모드**: 동일 프롬프트를 여러 모델에 동시 전송하여 품질을 비교합니다.

### 2. 에이전트 빌더 (No-Code Agent)

- **System Prompt** 작성 후, Tool을 추가하여 Tool-calling 에이전트를 즉시 생성합니다.
- 대화형 인터페이스에서 에이전트 동작을 반복적으로 테스트하고 개선합니다.
- 완성된 에이전트는 **Python 노트북으로 Export**하여 커스터마이징할 수 있습니다.

### 3. Tool 연결

- **Unity Catalog Functions**: SQL/Python 함수를 에이전트 도구로 등록
- **Vector Search Index**: RAG 기반 문서 검색
- **Genie Space**: 자연어 SQL 에이전트
- **MCP Servers**: 외부 도구 및 API 연동

---

## 무엇을 만들 수 있나?

| 활용 사례 | 핵심 Tool | 설명 |
|---|---|---|
| RAG 챗봇 | Vector Search | 사내 문서 기반 질의응답 |
| SQL 분석 에이전트 | Genie Space | 자연어로 데이터 분석 |
| 코드 실행 에이전트 | UC Function (`python_exec`) | Python 코드를 동적으로 실행 |
| 멀티 에이전트 시스템 | Supervisor Agent | 여러 에이전트를 오케스트레이션 |
| 외부 API 연동 | MCP (External) | 외부 서비스와 안전하게 통합 |

---

## Agent Framework과의 관계

AI Playground는 **Mosaic AI Agent Framework**의 노코드 프론트엔드입니다.

```
AI Playground (노코드)
    ↓ Export
Agent Framework (코드 기반)
    ↓ 배포
Model Serving Endpoint
    ↓ 모니터링
MLflow Tracing + Agent Evaluation
```

- **프로토타이핑**: AI Playground에서 빠르게 실험
- **커스터마이징**: Export 후 Python 코드로 세밀한 제어
- **프로덕션**: Agent Framework를 통해 Model Serving으로 배포
- **평가/모니터링**: MLflow Tracing과 Agent Evaluation으로 품질 관리

{% hint style="warning" %}
AI Playground에서 내보낸 에이전트는 Playground 내 동작과 다를 수 있습니다. 반드시 Export 후 평가 및 디버깅을 수행하세요.
{% endhint %}

---

## 참고 링크

- [Build gen AI apps on Databricks](https://docs.databricks.com/aws/en/generative-ai/agent-framework/build-genai-apps)
- [Get started: no-code GenAI](https://docs.databricks.com/aws/en/getting-started/gen-ai-llm-agent)
- [AI agent tools](https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-tool)
- [Author custom agents](https://docs.databricks.com/aws/en/generative-ai/agent-framework/author-agent)
- [MCP (Model Context Protocol)](https://docs.databricks.com/aws/en/generative-ai/mcp/)
- [Agent Bricks](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/)
