# Agent Memory 시스템

[← AI Agent 아키텍처 개요](README.md)

---

Agent가 맥락을 유지하고 과거 경험으로부터 학습하려면 **메모리(Memory)** 가 필요합니다. 인간의 기억 체계와 유사하게, Agent의 메모리도 여러 유형으로 나뉩니다.

## 메모리 유형

**Short-term Memory (단기 기억)**

현재 대화의 히스토리(메시지 목록)를 의미합니다. LLM의 Context Window 크기에 의해 제한되며, 모든 Agent가 기본적으로 가지는 가장 기본적인 메모리입니다.

**Long-term Memory (장기 기억)**

세션을 넘어 영속적으로 저장되는 정보입니다. 일반적으로 Vector DB나 외부 데이터베이스로 구현하며, Agent가 관련성이 있을 때 과거 상호작용을 검색하여 활용합니다.

**Episodic Memory (에피소드 기억)**

과거 문제 해결 과정의 기록입니다. "지난번에 비슷한 오류가 발생했을 때, 이렇게 해결했다..."와 같은 경험 기반 학습을 가능하게 합니다.

**Working Memory (작업 기억)**

현재 진행 중인 추론을 위한 임시 메모장입니다. 계획(Plan), 중간 결과, 현재 상태 등을 저장하며, Agent State로 구현되는 경우가 많습니다.

---

## 메모리 유형별 비교

| 메모리 유형 | 저장 메커니즘 | Databricks 도구 | 예시 |
|------------|-------------|----------------|------|
| **Short-term**| LLM Context Window (메시지 리스트) | ChatAgent messages 파라미터 | 현재 대화의 이전 질문/답변 참조 |
| **Long-term**| Vector DB / 외부 DB | Vector Search, Lakebase (PostgreSQL) | 3개월 전 고객 문의 내역 검색 |
| **Episodic**| 구조화된 로그 저장소 | MLflow Tracking, Delta Table | "지난번 ETL 실패는 스키마 변경 때문이었음" |
| **Working**| Agent State (인메모리) | LangGraph State, ChatAgent context | 현재 5단계 중 3단계 진행 중, 중간 계산 결과 |

{% hint style="success" %}
** 예시**: 고객 지원 Agent가 "지난번에 문의하신 환불 건은 어떻게 되셨나요?"라고 물을 수 있으려면 **Long-term Memory** 가 필요합니다. 현재 세션의 대화만으로는 이전 세션의 맥락을 알 수 없기 때문입니다.
{% endhint %}

{% hint style="warning" %}
현재 대부분의 Agent는 **Short-term Memory만** 가집니다. Long-term Memory는 Vector Search나 Lakebase(PostgreSQL)를 활용하여 별도 구현해야 합니다. Agent 프레임워크가 자동으로 제공하는 것이 아닙니다.
{% endhint %}

---

[다음: Multi-Agent 패턴 →](multi-agent.md)
