---
original_title: "Agentic AI Security: New Risks and Controls in the Databricks AI Security Framework (DASF v3.0)"
authors: "David Veuve, Omar Khawaja, Arun Pamulapati, Nishith Sinha, Caelin Kaplan"
date: "2026-03-20"
category: "Security and Trust"
original_url: "https://www.databricks.com/blog/agentic-ai-security-new-risks-and-controls-databricks-ai-security-framework-dasf-v30"
translated_date: "2026-04-07"
---

> **원문**: [Agentic AI Security: New Risks and Controls in the Databricks AI Security Framework (DASF v3.0)](https://www.databricks.com/blog/agentic-ai-security-new-risks-and-controls-databricks-ai-security-framework-dasf-v30)

# 에이전틱 AI 보안: Databricks AI 보안 프레임워크(DASF v3.0)의 새로운 위험과 통제

**데이터에 접근하고, 도구를 호출하며, 작업을 실행하는 에이전트를 위한 35가지 새로운 에이전틱 AI 위험과 6가지 완화 통제**

_Published: March 20, 2026 | 작성자: David Veuve, Omar Khawaja, Arun Pamulapati, Nishith Sinha, Caelin Kaplan_

![DASF v3.0 Agentic AI Security](https://www.databricks.com/sites/default/files/2026-03/2026-03-blog-secure-agentic-ai-with-the-databricks-ai-security-framework-og-1200x628.png?v=1774285996)

{% hint style="info" %}
**요약**

Databricks AI 보안 프레임워크(DASF)는 이제 에이전틱 AI(Agentic AI)를 13번째 시스템 컴포넌트로 다루며, 35가지 새로운 기술 보안 위험과 6가지 새로운 완화 통제를 추가함으로써 조직이 자율 에이전트를 안심하고 배포할 수 있도록 지원합니다. 이번 확장은 에이전트 메모리, 계획, 도구 사용의 고유한 위험을 다루며, 에이전트를 엔터프라이즈 도구에 연결하는 신흥 표준인 MCP(Model Context Protocol)가 도입하는 위협도 포함합니다. DASF Agentic AI Extension 백서와 업데이트된 컴펜디엄(Compendium)이 지금 바로 제공됩니다. 이를 다운로드하여 에이전트 아키텍처를 평가하고, 도구 에코시스템을 매핑하고, 자율성을 위해 특별히 설계된 심층 방어(Defense-in-Depth) 통제를 구현하세요.
{% endhint %}

Databricks AI 보안 프레임워크(DASF)의 **에이전틱 AI Extension 백서** 출시를 발표하게 되어 기쁩니다! Databricks 고객들은 이미 데이터베이스를 쿼리하고, 외부 API를 호출하며, 코드를 실행하고, 다른 에이전트와 협력하는 AI 에이전트를 배포하고 있습니다. 이러한 배포를 담당하는 팀들이 어려운 질문을 던지고 있음을 우리는 지속적으로 듣고 있습니다: AI가 단순히 말하는 것을 넘어 실제로 무언가를 **할 수 있을 때** 어떤 일이 일어날까요?

바로 그래서 우리가 DASF를 확장했습니다. 이번 업데이트를 통해 자율 AI 에이전트를 보안하기 위한 새로운 지침을 소개합니다:

- 에이전트 추론, 메모리, 도구 사용을 다루는 **35가지 새로운 에이전틱 AI 보안 위험**
- 최소 권한(Least Privilege), 샌드박싱(Sandboxing), 인간 감독(Human Oversight)을 포함하는 **6가지 새로운 완화 통제**
- MCP(Model Context Protocol) 도구 서버 및 클라이언트에 대한 보안 지침
- 멀티 에이전트 시스템 위험 및 에이전트 통신 위협에 대한 적용 범위

이러한 추가 사항들은 조직이 거버넌스, 관찰 가능성(Observability), 심층 방어 보안 통제를 유지하면서 AI 에이전트를 안전하게 배포할 수 있도록 지원합니다. 이로써 전체 프레임워크는 **97가지 위험과 73가지 통제**를 갖추게 되었습니다.

우리는 이러한 새로운 위험과 통제를 포함하고 산업 표준에 매핑하여 즉각적인 운영화를 촉진하는 DASF 컴펜디엄([Google Sheet](https://docs.google.com/), [Excel](https://microsoft.com/))을 업데이트했습니다. 이러한 추가 사항들은 "DASF Revision" 열 아래에 **DASF v3.0** 으로 분류되어 있습니다.

![DASF 13 Components](https://www.databricks.com/sites/default/files/inline-images/agentic-ai-security-risks-controls-databricks-ai-security-framework-blog-img-1.png)

_그림 1: 엔드투엔드 AI 시스템의 13가지 표준 컴포넌트. 에이전틱 AI가 13번째 컴포넌트로 도입되었습니다._

## AI 에이전트가 행동을 취할 수 있을 때의 보안 위험

기존의 RAG(Retrieval-Augmented Generation)와 같은 전통적인 AI 시스템은 대부분 **읽기 전용** 모드로 동작합니다. 하지만 AI 에이전트는 데이터베이스 쿼리, API 호출, 코드 실행, 외부 도구와의 상호작용 같은 **행동을 취할 수 있습니다.**

에이전트는 다르게 작동합니다. 사용자가 에이전트에게 작업을 요청하면, 모델은 루프를 시작합니다: 요청을 하위 작업으로 분해하고, 도구(예: "영업 데이터베이스 조회")를 선택하고, 실행하고, 결과를 평가한 다음, 다음에 다른 도구를 호출할지 결정합니다. 이 과정은 작업이 완료될 때까지 계속됩니다. 에이전트는 어떤 데이터에 접근하고 어떤 도구를 호출할지 실시간으로 결정하고 있습니다. 이는 과거에 사람이 직접 하거나 애플리케이션 로직에 하드코딩된 결정이었습니다.

이것이 우리가 **발견과 탐색(Discovery and Traversal)** 이라고 부르는 새로운 위험 클래스를 만들어냅니다. 솔루션을 찾도록 설계된 에이전트는 요청하는 사용자가 의도하지 않았던 데이터 경로와 도구 인터페이스를 탐색합니다. 이것은 버그를 악용하는 것이 아닙니다. 에이전트는 정확히 그것이 하도록 설계된 일을 하고 있습니다. 그러나 적절한 통제 없이는, 사용자가 자신의 권한 대신 에이전트의 권한을 사실상 상속받게 됩니다.

### 치명적 삼각형 (The Lethal Trifecta)

Meta의 "Agents Rule of Two"와 Simon Willison의 "Lethal Trifecta"를 포함한 최근 업계 연구는 이것이 위험해지는 조건을 강조합니다. 세 가지 조건이 동시에 존재할 때 위험 프로파일이 급격히 높아집니다:

1. **민감한 시스템 또는 개인 데이터에 대한 접근**: 에이전트가 개인 또는 제한된 데이터를 검색할 수 있습니다.
2. **신뢰할 수 없는 입력 처리**: 에이전트가 신뢰 경계 외부의 데이터를 처리합니다 — 사용자 프롬프트, 외부 웹사이트, 수신 이메일.
3. **상태 변경 또는 외부 통신**: 에이전트가 도구 또는 MCP 연결을 통해 상태를 수정할 수 있습니다 — 이메일 전송, SQL 실행, 코드 수정.

세 가지가 모두 충족되면, 신뢰할 수 없는 데이터에 삽입된 **간접 프롬프트 인젝션(Indirect Prompt Injection)** 이 에이전트의 전체 기능을 탈취하여, 악의적인 의도를 가진 승인된 행동을 수행하는 "혼란스러운 대리인(Confused Deputy)"으로 만들 수 있습니다.

권한 범위를 축소하고, 인간 체크포인트를 추가하고, 도구 선택 전에 의도를 검증하여 세 조건 중 하나라도 제거하면 공격 체인을 끊을 수 있습니다.

## 확장의 구성 방식

35가지 새로운 위험과 6가지 통제는 에이전트가 실제로 작동하는 방식에 매핑되는 세 가지 하위 컴포넌트를 중심으로 구성되어 있습니다.

### 13A: 에이전트 코어 (Agent Core) — 두뇌와 메모리

이 위험들은 에이전트의 추론 루프를 대상으로 합니다.

- **메모리 포이즈닝(Memory Poisoning, 위험 13.1)**: 현재 또는 미래의 결정을 변경하는 허위 컨텍스트를 도입합니다.
- **의도 파괴 및 목표 조작(Intent Breaking & Goal Manipulation, 위험 13.6)**: 에이전트를 목표에서 벗어나도록 강제합니다.
- **연쇄 환각 공격(Cascading Hallucination Attacks, 위험 13.5)**: 에이전트가 멀티턴 루프로 운영되기 때문에, 사소한 오류가 반복되면서 파괴적인 행동으로 확대될 수 있습니다.

### 13B: MCP 서버 위험 (MCP Server Risks) — 도구 인터페이스

에이전트는 도구를 통해 외부 시스템과 상호작용하며, 이는 점점 더 MCP(Model Context Protocol)를 통해 표준화되고 있습니다. 서버 측에서 공격자는 다음과 같은 위험을 야기할 수 있습니다:

- **도구 포이즈닝(Tool Poisoning, 위험 13.18)**: 도구 정의에 악성 동작을 주입합니다.
- **프롬프트 인젝션(Prompt Injection, 위험 13.16)**: 도구 설명 내에서 보안 통제를 우회하기 위한 프롬프트 인젝션을 활용합니다.

### 13C: MCP 클라이언트 위험 (MCP Client Risks) — 연결 레이어

클라이언트 측에서 에이전트가 악성 서버(Malicious Server, 위험 13.26)에 연결하거나 서버 응답의 유효성 검사에 실패하면, 다음과 같은 위험에 노출됩니다:

- **클라이언트 측 코드 실행(Client-Side Code Execution, 위험 13.32)**
- **데이터 유출(Data Leakage, 위험 13.30)**

MCP 채택이 증가함에 따라, 클라이언트-서버 경계를 보안하는 것은 에이전트의 추론 보안만큼 중요해졌습니다.

### 에이전트 간 역학 관계 (Inter-Agent Dynamics)

에이전트들은 점점 더 다른 에이전트와 통신하게 됩니다. 이것은 다음과 같은 위험을 만들어냅니다:

- **에이전트 통신 포이즈닝(Agent Communication Poisoning, 위험 13.12)**: 에이전트 간 메시지를 오염시킵니다.
- **멀티 에이전트 시스템 내 불량 에이전트(Rogue Agents in Multi-Agent Systems, 위험 13.13)**: 모니터링 경계 밖에서 운영되는 에이전트로, 규모가 커질수록 복잡한 문제를 야기합니다.

## AI 에이전트 및 자율 시스템 보안을 위한 통제

DASF는 항상 심층 방어(Defense-in-Depth)에 관한 것이었습니다. 하지만 AI 시스템이 행동을 취할 수 있을 때, 읽기 전용 접근 통제만으로는 충분하지 않습니다. 새로운 통제는 이 문제를 직접적으로 다룹니다:

### 도구에 대한 최소 권한 (DASF 5, DASF 57, DASF 64)

에이전트는 즉각적인 작업에 맞게 범위가 지정된 세분화된 권한이 필요합니다. 이는 RBAC(Role-Based Access Control)와 ABAC(Attribute-Based Access Control)가 사람의 권한을 제한하는 것과 같은 방식으로 피해 반경(Blast Radius)을 제한합니다. 에이전트가 HR 지표 도구를 호출할 수 있다고 해서, 영업 쿼리에 응답할 때 그렇게 해야 하는 것은 아닙니다.

### 인간 감독 루프 (Human-in-the-Loop Oversight, DASF 66)

고위험 행동의 경우 도구 실행 전 인간 검증을 요구합니다. 통제 설계는 **승인 피로(Approval Fatigue)** 를 고려합니다 — 인간 검토자를 압도하면 문제를 해결한 것이 아니라 새로운 취약점을 만든 것입니다.

### 샌드박싱 및 격리 (Sandboxing and Isolation, DASF 34, DASF 62)

에이전트가 생성한 코드는 일시적이고 격리된 환경에서 실행됩니다. 에이전트가 스크립트를 작성하고 실행하기로 결정한 경우, 해당 실행은 더 광범위한 시스템에 접근하거나 알 수 없는 목적지로 아웃바운드 연결이 되어서는 안 됩니다.

### AI 게이트웨이 및 가드레일 (AI Gateway and Guardrails, DASF 54)

에이전트는 에이전트가 노출해서는 안 되는 데이터를 표면화하도록 조작되는 시나리오로부터 보호받아야 합니다. 모니터링, 안전 필터링, PII 탐지와 같은 게이트웨이 및 가드레일을 통한 에이전트의 상호작용은 반드시 적용되어야 합니다. 이러한 가드레일은 에이전트의 입력 또는 출력(또는 둘 다)에 적용될 수 있습니다. 또한 에이전트가 실제로 반환하는 내용을 모니터링하는 것도 마찬가지로 중요합니다.

### 사고 관찰 가능성 (Observability of Thought, DASF 65)

표준 로깅은 무슨 일이 일어났는지 알려줍니다. **에이전틱 트레이싱(Agentic Tracing)** 은 왜 그런 일이 일어났는지를 포착합니다 — 계획 단계, 도구 선택 추론, 행동으로 이어진 사고 체인. 이것 없이는 에이전트의 결정을 감사하거나 추론이 손상된 시점을 탐지할 수 없습니다.

Databricks 고객을 위해, 컴펜디엄은 이러한 통제를 플랫폼 기능에 매핑합니다. 여기에는 에이전트 데이터 접근을 위한 Unity Catalog 거버넌스, Agent Bricks Framework, AI Gateway 가드레일, Vector Search 보안 설정이 포함됩니다.

## 커뮤니티와 함께 구축됨

이번 확장은 Atlassian, Experian, ComplyLeft 팀을 포함하여 Databricks와 보안 커뮤니티 전반의 검토자 및 기여자들의 의견을 반영했습니다. 또한 MITRE ATLAS, OWASP, NIST, 클라우드 보안 연합(Cloud Security Alliance)의 작업을 폭넓게 참조했으며, 업데이트된 컴펜디엄은 97가지 위험과 73가지 통제 모두를 이러한 산업 표준에 매핑합니다.

## 시작하기

전체 35가지 새로운 에이전틱 AI 위험과 6가지 새로운 통제를 모두 다루는 **DASF Agentic AI Extension 백서** 를 다운로드하고, 기존 DASF와 함께 에이전틱 위험 및 통제를 매핑하는 업데이트된 컴펜디엄([Google Sheet](https://docs.google.com/), [Excel](https://microsoft.com/))을 확인하세요.

이 리소스를 활용하여 다음을 수행할 수 있습니다:

- **현재 에이전트 아키텍처를 에이전틱 AI 위험 모델에 대해 평가합니다.** 에이전트가 어떤 도구에 접근하는지, 어떤 데이터를 처리하는지, 어떤 외부 시스템과 상호작용하는지 검토합니다.
- **MCP 서버와 클라이언트를 포함한 도구 에코시스템을 식별된 위협 벡터에 매핑합니다.** 연결된 각 도구 인터페이스를 잠재적인 공격 표면으로 파악합니다.
- **에이전트가 안전하고 거버넌스된 경계 내에서 작동하도록 권장 통제를 구현합니다.** 최소 권한 원칙부터 에이전틱 트레이싱까지, 각 통제가 에이전트 위험의 어떤 부분을 해결하는지 이해합니다.

더 깊은 컨텍스트를 위해 전체 DASF 백서를 읽고, Agent Bricks Framework 문서를 탐색하여 이러한 통제가 플랫폼에서 어떻게 작동하는지 확인하세요. Databricks 어카운트 팀에 문의하거나 피드백을 이메일로 보내주세요 — 이 프레임워크는 우리 것인 만큼 커뮤니티의 것이기도 합니다.
