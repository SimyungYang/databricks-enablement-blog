# 활용 사례

Builder App(AI Playground)으로 구현할 수 있는 주요 비즈니스 시나리오를 소개합니다.

---

## 1. 고객 지원 챗봇 (RAG + Vector Search)

사내 문서, FAQ, 매뉴얼을 기반으로 고객 질문에 자동 응답하는 RAG 챗봇입니다.

### 구성 요소

| 구성 | 설명 |
|---|---|
| **모델** | Claude Sonnet 또는 GPT-4o |
| **Tool** | Vector Search Index (사내 문서 인덱스) |
| **추가 Tool** | UC Function (티켓 조회, 고객 정보 조회) |

### 구현 흐름

```
고객 질문 입력
    ↓
Vector Search로 관련 문서 검색
    ↓
검색 결과 + 질문을 LLM에 전달
    ↓
출처(Citation) 포함 답변 생성
```

### System Prompt 예시

```text
당신은 [회사명] 고객 지원 전문가입니다.
- 고객 질문에 대해 내부 문서를 검색하여 정확한 답변을 제공합니다.
- 답변 시 반드시 출처 문서를 명시합니다.
- 문서에 없는 내용은 추측하지 않고, 상담원 연결을 안내합니다.
- 개인정보(주민번호, 카드번호 등)는 절대 노출하지 않습니다.
```

{% hint style="tip" %}
Vector Search Index에 문서 제목, 카테고리 등 메타데이터를 함께 인덱싱하면 검색 품질이 향상됩니다.
{% endhint %}

---

## 2. 데이터 분석 어시스턴트 (Genie Space 연동)

비기술 사용자가 자연어로 데이터를 분석할 수 있는 SQL 에이전트입니다.

### 구성 요소

| 구성 | 설명 |
|---|---|
| **모델** | Llama 4 Maverick 또는 GPT-4o |
| **Tool** | Genie Space (매출/재무/운영 데이터) |
| **추가 Tool** | UC Function (`python_exec` - 차트 생성) |

### 활용 시나리오

- **경영진**: "이번 분기 매출을 지역별로 보여줘"
- **마케팅팀**: "최근 3개월 캠페인별 전환율을 비교해줘"
- **운영팀**: "지난주 물류 지연 건수와 원인을 분석해줘"

### System Prompt 예시

```text
당신은 데이터 분석 전문가입니다.
- 사용자의 자연어 질문을 분석하여 적절한 데이터를 조회합니다.
- 결과를 요약하고, 핵심 인사이트를 제공합니다.
- 수치는 천 단위 구분 기호와 적절한 단위를 포함합니다.
- 추가 분석이 필요하면 후속 질문을 제안합니다.
```

{% hint style="info" %}
Genie Space에 사전에 **인스트럭션**과 **샘플 질문**을 설정해두면, 에이전트가 더 정확한 SQL을 생성합니다. [Genie Space 가이드](../genie-space/README.md)를 참고하세요.
{% endhint %}

---

## 3. 내부 업무 자동화 (UC Functions)

반복적인 내부 업무를 자동화하는 에이전트입니다.

### 구성 요소

| 구성 | 설명 |
|---|---|
| **모델** | Claude Sonnet |
| **Tool** | UC Functions (다수의 업무 함수) |
| **추가 Tool** | External MCP (Slack, Jira 등) |

### 활용 시나리오

- **HR**: "신규 입사자 온보딩 체크리스트를 생성하고 Slack으로 공유해줘"
- **영업**: "이번 주 미팅 예정인 고객사 리스트와 최근 거래 내역을 정리해줘"
- **IT**: "서버 모니터링 알림을 확인하고 장애 티켓을 생성해줘"

### UC Function 예시

```sql
-- 온보딩 체크리스트 생성
CREATE OR REPLACE FUNCTION main.hr.create_onboarding_checklist(
  employee_name STRING COMMENT '신규 입사자 이름',
  department STRING COMMENT '부서명',
  start_date DATE COMMENT '입사일'
)
RETURNS STRING
COMMENT '신규 입사자의 온보딩 체크리스트를 생성하고 작업 ID를 반환합니다.'
LANGUAGE PYTHON
AS $$
  # 비즈니스 로직 구현
  return f"Onboarding checklist created for {employee_name}"
$$;
```

{% hint style="warning" %}
UC Function에서 외부 API를 호출해야 하는 경우, 보안 정책에 따라 **네트워크 설정**이 필요할 수 있습니다.
{% endhint %}

---

## 4. 멀티 에이전트 오케스트레이션 (Supervisor)

여러 전문 에이전트를 하나의 Supervisor 에이전트가 조율하는 고급 패턴입니다.

### 아키텍처

```
사용자 질문
    ↓
Supervisor Agent (라우터)
    ├── 고객 지원 Agent (RAG)
    ├── 데이터 분석 Agent (Genie)
    └── 업무 자동화 Agent (UC Functions)
```

### 구성 방법

1. **AI Playground**에서 각 전문 에이전트를 개별적으로 프로토타이핑합니다.
2. 각 에이전트를 **코드로 Export**합니다.
3. **Agent Bricks의 Supervisor Agent** 또는 커스텀 코드로 오케스트레이션을 구성합니다.
4. Supervisor가 사용자 의도를 분석하고 적합한 하위 에이전트에 위임합니다.

### Supervisor 장점

- 각 에이전트가 특정 도메인에 특화되어 품질 향상
- 새로운 에이전트를 독립적으로 추가/수정 가능
- 복잡한 요청을 여러 에이전트가 협력하여 처리

{% hint style="info" %}
멀티 에이전트 시스템은 **Agent Bricks**의 Supervisor 패턴을 활용하면 쉽게 구현할 수 있습니다. [Agent Bricks 가이드](../agent-bricks/supervisor.md)를 참고하세요.
{% endhint %}

---

## 사례별 권장 시작점

| 사례 | 난이도 | 시작 방법 |
|---|---|---|
| RAG 챗봇 | 낮음 | AI Playground + Vector Search |
| 데이터 분석 | 낮음 | AI Playground + Genie Space |
| 업무 자동화 | 중간 | AI Playground + UC Functions |
| 멀티 에이전트 | 높음 | AI Playground Export + Agent Bricks |

---

## 참고 링크

- [Build gen AI apps on Databricks](https://docs.databricks.com/aws/en/generative-ai/agent-framework/build-genai-apps)
- [Agent Bricks](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/)
- [Agent Evaluation](https://docs.databricks.com/aws/en/generative-ai/agent-evaluation/)
- [MLflow Tracing](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/)
