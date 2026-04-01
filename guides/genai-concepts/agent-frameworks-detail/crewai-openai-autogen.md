# CrewAI, OpenAI Agents SDK & AutoGen

역할 기반 멀티에이전트(CrewAI), 핸드오프 패턴(OpenAI Agents SDK), 대화 기반 협업(AutoGen) 세 가지 프레임워크를 비교합니다. 각각의 설계 철학, 코드 예시, 장단점을 다룹니다.

---

## CrewAI -- 역할 기반 멀티에이전트

CrewAI는 "사람 팀처럼 동작하는 AI 에이전트 팀"이라는 직관적인 메타포를 기반으로 설계된 프레임워크입니다. 비개발자도 이해할 수 있는 선언적 API가 특징입니다.

### 설계 철학: 팀 메타포

{% hint style="success" %}
** 비유**: 회사 프로젝트를 수행할 때 팀장이 각 팀원에게 역할(리서처, 분석가, 작성자)을 부여하고 업무를 배분하듯이, CrewAI는 Agent에게 역할(role)을 부여하고 Task를 할당합니다.
{% endhint %}

| CrewAI 개념 | 팀 비유 | 설명 |
|-------------|---------|------|
| **Agent**| 팀원 | 역할, 목표, 배경 스토리를 가진 AI 작업자 |
| **Task**| 업무 | 구체적인 작업 지시 + 기대 결과물 |
| **Crew**| 팀 | Agent들을 모아 프로세스에 따라 실행 |
| **Process**| 업무 방식 | Sequential(순차) 또는 Hierarchical(계층) |

### 코드 예제: 리서치 + 보고서 작성 팀

```python
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# 도구 정의
search_tool = SerperDevTool()

# Agent 1: 리서처
researcher = Agent(
    role="시니어 데이터 리서처",
    goal="Databricks의 최신 기술 동향을 조사하여 핵심 인사이트를 도출한다",
    backstory=(
        "당신은 10년 경력의 데이터 플랫폼 분석가입니다. "
        "기술 트렌드를 빠르게 파악하고 비즈니스 임팩트를 연결하는 데 탁월합니다."
    ),
    tools=[search_tool],
    verbose=True,
)

# Agent 2: 보고서 작성자
writer = Agent(
    role="테크 라이터",
    goal="리서처의 조사 결과를 기반으로 경영진용 보고서를 작성한다",
    backstory=(
        "당신은 기술 콘텐츠를 비기술 임원이 이해할 수 있도록 "
        "변환하는 전문 테크 라이터입니다."
    ),
    verbose=True,
)

# Task 1: 조사
research_task = Task(
    description="2025년 Databricks의 주요 제품 업데이트와 시장 동향을 조사하세요.",
    expected_output="핵심 업데이트 5개와 각각의 비즈니스 임팩트 분석",
    agent=researcher,
)

# Task 2: 보고서 작성
writing_task = Task(
    description="리서치 결과를 기반으로 경영진용 1페이지 브리핑을 작성하세요.",
    expected_output="제목, 핵심 요약 3줄, 상세 분석 5개 항목의 구조화된 보고서",
    agent=writer,
)

# Crew 구성 및 실행
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,  # 순차 실행: 리서치 -> 작성
    verbose=True,
)

result = crew.kickoff()
print(result)
```

### Process 타입

| Process | 동작 방식 | 적합한 시나리오 |
|---------|----------|---------------|
| **Sequential**| Task를 순서대로 실행. 이전 Task 결과가 다음 Task의 입력 | 파이프라인형 작업 (조사 -> 분석 -> 보고서) |
| **Hierarchical**| Manager Agent가 하위 Agent에게 작업 위임 및 조율 | 복잡한 프로젝트 관리, 여러 전문가 협업 |

### CrewAI의 장점과 한계

** 장점:**
- ** 직관적**: 역할/팀 메타포가 명확하여 비개발자도 구조를 이해 가능
- ** 빠른 프로토타이핑**: 10분 내에 멀티에이전트 시스템 구축 가능
- ** 선언적 API**: 코드보다는 "설정"에 가까운 구성 방식

** 한계:**
- ** 세밀한 제어 어려움**: 에이전트 간 통신의 세부 흐름을 커스텀하기 어려움
- ** 조건 분기 제한**: LangGraph 대비 복잡한 분기/루프 표현 능력 부족
- ** 프로덕션 미성숙**: 에러 처리, 모니터링, 거버넌스 기능이 약함
- ** 비결정적 동작**: Agent의 "대화"가 매번 다르게 전개될 수 있음

---

## OpenAI Agents SDK -- Handoff 패턴의 정석

2025년 1월 출시된 OpenAI Agents SDK는 OpenAI가 직접 제공하는 공식 Agent 프레임워크입니다. **Handoff(대화 인계)**, **Guardrail(안전장치)**, **Tracing(추적)** 을 핵심 기능으로 내세웁니다.

### 핵심 개념

| 개념 | 설명 | 비유 |
|------|------|------|
| **Agent**| 시스템 프롬프트 + 도구 + 모델로 구성된 실행 단위 | 전문 상담원 |
| **Handoff**| Agent A가 대화 전체를 Agent B에게 넘기기 | 콜센터 상담 전환 |
| **Guardrail**| 입력/출력을 프레임워크 레벨에서 검증 | 보안 검색대 |
| **Tracing**| 전체 실행 과정을 자동으로 기록 | CCTV 녹화 |

### Handoff 패턴

Handoff는 OpenAI Agents SDK의 가장 독특한 기능입니다. Agent A가 자신의 전문 영역이 아닌 질문을 받으면, 대화 히스토리 전체를 포함하여 Agent B에게 인계합니다.

{% hint style="info" %}
**Handoff vs Tool Call**: Tool Call은 "특정 함수를 호출하고 결과를 받아오는 것"이고, Handoff는 "대화의 주도권 자체를 다른 Agent에게 넘기는 것"입니다. 콜센터에서 "잠시만요, 기술팀으로 연결해드리겠습니다"라고 하는 것이 Handoff입니다.
{% endhint %}

### 코드 예제: 고객 서비스 Agent (Handoff 포함)

```python
from openai import agents

# 전문 Agent 정의
billing_agent = agents.Agent(
    name="billing_agent",
    instructions=(
        "당신은 청구/결제 전문 상담원입니다. "
        "청구 관련 질문에만 답변하세요. "
        "기술 지원 질문은 tech_agent로 핸드오프하세요."
    ),
    model="gpt-4o",
)

tech_agent = agents.Agent(
    name="tech_agent",
    instructions=(
        "당신은 기술 지원 전문 상담원입니다. "
        "기술적인 문제에 대해 답변하세요. "
        "청구 관련 질문은 billing_agent로 핸드오프하세요."
    ),
    model="gpt-4o",
)

# Triage Agent -- 첫 진입점
triage_agent = agents.Agent(
    name="triage_agent",
    instructions=(
        "당신은 고객 문의를 분류하는 접수 담당입니다. "
        "고객의 질문을 파악하여 적절한 전문 상담원에게 연결하세요."
    ),
    model="gpt-4o",
    handoffs=[billing_agent, tech_agent],  # 핸드오프 대상 지정
)

# 실행
result = agents.run(
    triage_agent,
    messages=[{"role": "user", "content": "지난달 청구서가 이상합니다"}],
)

# triage_agent -> billing_agent로 자동 핸드오프됨
print(result.final_output)
```

### Guardrail (입력/출력 검증)

```python
from openai.agents import guardrail, GuardrailFunctionOutput

@guardrail
def no_pii_guardrail(text: str) -> GuardrailFunctionOutput:
    """개인정보(PII)가 포함된 입력을 차단"""
    import re
    # 주민등록번호 패턴 체크
    if re.search(r'\d{6}-\d{7}', text):
        return GuardrailFunctionOutput(
            output_info="주민등록번호가 감지되었습니다.",
            tripwire_triggered=True,  # 실행 중단
        )
    return GuardrailFunctionOutput(
        output_info="안전한 입력입니다.",
        tripwire_triggered=False,
    )

agent = agents.Agent(
    name="safe_agent",
    instructions="고객 문의에 답변하세요.",
    model="gpt-4o",
    input_guardrails=[no_pii_guardrail],  # 입력 가드레일 적용
)
```

### OpenAI Agents SDK의 장점과 한계

** 장점:**
- ** 간결한 API**: 최소한의 코드로 Agent 구축 가능
- **Handoff 패턴 내장**: 멀티에이전트 라우팅이 매우 깔끔
- **Guardrail 내장**: 별도 라이브러리 없이 입출력 검증
- ** 자동 Tracing**: OpenAI 대시보드에서 실행 과정 시각화
- ** 프로덕션 지향**: OpenAI 인프라와 긴밀하게 통합

** 한계:**
- **OpenAI 종속**: 기본적으로 OpenAI 모델만 지원 (커스텀 확장 필요)
- ** 복잡한 그래프 표현 제한**: LangGraph 수준의 복잡한 워크플로는 어려움
- ** 상태 관리 제한**: LangGraph Checkpoint 같은 장기 상태 관리 기능 부족
- ** 자체 호스팅 어려움**: OpenAI API 의존도가 높음

---

## AutoGen (Microsoft) -- 멀티에이전트 대화

AutoGen은 Microsoft Research에서 개발한 프레임워크로, Agent들이 자유롭게 "대화"하며 문제를 해결하는 패러다임을 제안합니다.

### 설계 철학

{% hint style="success" %}
** 비유**: 다른 프레임워크가 "조직도에 따른 업무 배분"이라면, AutoGen은 "회의실에서 자유 토론"에 가깝습니다. 참가자들이 돌아가며 발언하고, 서로의 의견에 반응하며, 합의에 도달합니다.
{% endhint %}

### 핵심 컴포넌트

| 컴포넌트 | 역할 |
|----------|------|
| **ConversableAgent**| 대화 가능한 Agent의 기본 클래스 |
| **AssistantAgent**| LLM 기반 Agent (추론 담당) |
| **UserProxyAgent**| 사용자를 대리하는 Agent (코드 실행, 승인 등) |
| **GroupChat**| 여러 Agent가 참여하는 그룹 대화 |
| **GroupChatManager**| 그룹 대화의 발언 순서와 종료 조건 관리 |

### 코드 예제: 코드 생성 + 리뷰 Agent

```python
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

# LLM 설정
config_list = [{"model": "gpt-4o", "api_key": "YOUR_API_KEY"}]

# Agent 1: 코드 작성자
coder = AssistantAgent(
    name="coder",
    system_message=(
        "당신은 시니어 Python 개발자입니다. "
        "요청받은 기능을 깔끔한 Python 코드로 구현하세요. "
        "코드 블록으로 감싸서 응답하세요."
    ),
    llm_config={"config_list": config_list},
)

# Agent 2: 코드 리뷰어
reviewer = AssistantAgent(
    name="reviewer",
    system_message=(
        "당신은 코드 리뷰 전문가입니다. "
        "coder가 작성한 코드를 리뷰하고 개선점을 제안하세요. "
        "보안, 성능, 가독성 관점에서 평가하세요."
    ),
    llm_config={"config_list": config_list},
)

# Agent 3: 사용자 대리 (코드 실행 가능)
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",  # 자동 실행 (사람 개입 없음)
    code_execution_config={"work_dir": "coding_output"},
    max_consecutive_auto_reply=3,
)

# 대화 시작: user_proxy가 coder에게 요청
user_proxy.initiate_chat(
    coder,
    message="Delta Lake 테이블의 변경 이력을 조회하는 Python 함수를 작성해주세요.",
)
```

### AutoGen의 장점과 한계

** 장점:**
- ** 코드 실행 내장**: Agent가 직접 Python/Shell 코드를 실행하고 결과 확인 가능
- ** 자유도 높은 대화**: 정해진 워크플로 없이 Agent들이 자율적으로 협업
- ** 연구/실험에 최적**: 다양한 에이전트 구성을 빠르게 실험 가능
- **GroupChat**: 3개 이상의 Agent가 동시에 참여하는 토론 가능

** 한계:**
- ** 비결정적 흐름**: 매번 다른 대화 흐름이 전개될 수 있어 프로덕션에서 예측 가능성 낮음
- ** 프로덕션 배포 복잡**: 모니터링, 에러 처리, 스케일링이 쉽지 않음
- ** 대화 비용**: 불필요한 왕복 대화로 토큰 비용 증가 가능
- ** 종료 조건 설정 어려움**: "언제 대화를 끝낼 것인가"의 판단이 까다로움

{% hint style="warning" %}
**AutoGen v0.4 주의사항**: AutoGen은 v0.2에서 v0.4로 대규모 리팩토링을 거쳤습니다. 이전 버전의 블로그/튜토리얼 코드는 v0.4에서 동작하지 않을 수 있습니다. 반드시 최신 공식 문서를 참고하세요.
{% endhint %}

---

[README로 돌아가기](README.md) | 다음: [Databricks Agent Framework](databricks-af.md)
