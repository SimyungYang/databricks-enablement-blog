# Getting Started

AI Playground를 사용하여 노코드로 에이전트를 생성하고 배포하는 단계별 가이드입니다.

---

## 사전 요구 사항

{% hint style="info" %}
- Databricks Workspace에 접근 가능한 계정
- Foundation Model API가 활성화된 Workspace
- Unity Catalog가 설정되어 있을 것 (Tool 사용 시)
{% endhint %}

---

## AI Playground 접근 방법

1. Databricks Workspace에 로그인합니다.
2. 좌측 사이드바에서 **Machine Learning** > **Playground**를 클릭합니다.
3. AI Playground 인터페이스가 열립니다.

{% hint style="tip" %}
Workspace 상단 검색바에서 "Playground"를 검색해도 바로 접근할 수 있습니다.
{% endhint %}

---

## 단계 1: LLM 비교 테스트

에이전트를 만들기 전에, 먼저 다양한 모델의 성능을 비교합니다.

1. Playground 화면에서 **모델 선택** 드롭다운을 클릭합니다.
2. 사용 가능한 모델 중 하나를 선택합니다:
   - **Meta Llama 4 Maverick** - 오픈소스 대형 모델
   - **Anthropic Claude Sonnet** - 분석/추론에 강점
   - **OpenAI GPT-4o** - 범용 고성능 모델
   - 기타 Foundation Model API에서 제공하는 모델
3. 프롬프트를 입력하고 응답을 확인합니다.
4. **+ 버튼**을 클릭하여 두 번째 모델을 추가합니다.
5. **Sync** 체크박스를 활성화하면, 동일 프롬프트가 두 모델에 동시 전송됩니다.

---

## 단계 2: System Prompt 작성

에이전트의 역할과 동작 규칙을 정의합니다.

1. Playground 좌측 패널에서 **System Prompt** 섹션을 찾습니다.
2. 에이전트의 역할, 톤, 제약 조건을 작성합니다.

```text
당신은 고객 지원 전문가입니다.
- 항상 한국어로 응답합니다.
- 모르는 내용은 "확인 후 답변드리겠습니다"라고 말합니다.
- 제품 관련 질문에는 내부 문서를 검색하여 답변합니다.
- 민감한 개인정보는 절대 노출하지 않습니다.
```

{% hint style="warning" %}
System Prompt는 에이전트 품질의 핵심입니다. 구체적이고 명확한 지시를 작성할수록 에이전트의 동작이 안정적입니다.
{% endhint %}

---

## 단계 3: Tool 추가

에이전트에 실행 능력을 부여합니다.

1. **Tools enabled** 라벨이 있는 모델을 선택합니다.
2. **Tools** > **+ Add tool**을 클릭합니다.
3. Tool 유형을 선택합니다:

### UC Function

Unity Catalog에 등록된 SQL/Python 함수를 도구로 사용합니다.

- 기본 제공: `system.ai.python_exec` (Python 코드 실행)
- 커스텀 함수도 등록 가능

### Vector Search

Vector Search Index를 연결하여 RAG 검색을 수행합니다.

- 인덱스 선택 후 자동으로 검색 Tool이 추가됩니다.
- 검색 결과에 **출처(Source Citation)**가 포함됩니다.

### Genie Space

Genie Space를 연결하여 자연어 SQL 분석을 수행합니다.

### MCP Server

외부 또는 커스텀 MCP 서버를 연결합니다.

- **Managed MCP**: Databricks 기본 제공 (UC, Genie, Vector Search 등)
- **External MCP**: 외부 서비스 연결
- **Custom MCP**: Databricks Apps로 호스팅하는 자체 MCP 서버

---

## 단계 4: 테스트 & 반복

Tool을 추가한 후, 대화를 통해 에이전트를 테스트합니다.

1. Tool 호출이 필요한 질문을 입력합니다.
   - 예: "최근 매출 데이터를 분석해줘" (Genie Space)
   - 예: "환불 정책에 대해 알려줘" (Vector Search)
2. 에이전트가 올바른 Tool을 선택하는지 확인합니다.
3. 응답 품질이 부족하면:
   - System Prompt를 수정합니다.
   - Tool 설명(Description)을 개선합니다.
   - 다른 모델로 변경합니다.

{% hint style="tip" %}
Tool의 **이름**과 **설명**이 명확할수록 LLM이 올바른 도구를 선택합니다. Tool 설명을 자세히 작성하세요.
{% endhint %}

---

## 단계 5: 코드 Export & 배포

프로토타이핑이 완료되면 프로덕션으로 전환합니다.

### 코드 Export

1. **Get code** > **Create agent notebook**을 클릭합니다.
2. Python 노트북이 자동 생성됩니다.
3. 생성된 코드에는 다음이 포함됩니다:
   - `ResponsesAgent` 정의
   - Tool 설정
   - MLflow 로깅
   - Model 등록 & 배포 코드

### 배포 흐름

```
AI Playground에서 Export
    ↓
Python 노트북에서 커스터마이징
    ↓
MLflow에 모델 등록
    ↓
Model Serving Endpoint로 배포
    ↓
Review App으로 품질 평가
    ↓
프로덕션 릴리스
```

### Review App

- 배포된 에이전트를 **Review App**에서 팀원들과 테스트합니다.
- SME(Subject Matter Expert)의 피드백을 수집합니다.
- Agent Evaluation으로 품질 메트릭을 측정합니다.

{% hint style="warning" %}
AI Playground에서 내보낸 에이전트는 Playground 내 동작과 다를 수 있습니다. Export 후 반드시 평가(Evaluation)를 수행하고, 필요 시 코드를 수정하세요.
{% endhint %}

---

## 다음 단계

- [Tool 연결 상세 가이드](tools.md) - 각 Tool 유형별 상세 설정 방법
- [활용 사례](use-cases.md) - 실제 비즈니스 시나리오
- [Agent Bricks](../agent-bricks/README.md) - 도메인 특화 에이전트 빌더

---

## 참고 링크

- [Get started: no-code GenAI](https://docs.databricks.com/aws/en/getting-started/gen-ai-llm-agent)
- [Author custom agents](https://docs.databricks.com/aws/en/generative-ai/agent-framework/author-agent)
- [Agent Evaluation](https://docs.databricks.com/aws/en/generative-ai/agent-evaluation/)
