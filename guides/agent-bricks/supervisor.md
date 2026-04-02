# Supervisor Agent (Multi-Agent)

---

## 개요

Supervisor Agent는 여러 전문 에이전트를 **조율(Orchestrate)하여 복합 업무를 처리** 하는 멀티 에이전트 시스템입니다.

**핵심 기능:**
- 에이전트 간 상호작용 관리
- 태스크 위임(Delegation)
- 결과 종합(Synthesis)
- 사용자 권한 기반 라우팅

**적합한 유스케이스:**
- 시장 분석 (데이터 + 문서 결합)
- 사내 프로세스 자동화
- 고객 서비스 (여러 지식 소스 통합)

---

## 지원하는 서브 에이전트 유형

최대 **20개** 의 서브 에이전트를 등록할 수 있습니다.

| 서브 에이전트 유형 | 설명 | 필요 권한 |
|-------------------|------|-----------|
| **Genie Spaces** | 데이터 탐색 인터페이스 | Space 접근 + UC 객체 권한 |
| **Agent Endpoints** | Knowledge Assistant 엔드포인트만 지원 | `CAN QUERY` |
| **Unity Catalog Functions** | 커스텀 도구 (UC 함수) | `EXECUTE` |
| **External MCP Servers** | MCP 프로토콜 서버 (Bearer Token/OAuth) | `USE CONNECTION` (UC Connection) |

{% hint style="info" %}
**중요**: Agent Endpoints는 Knowledge Assistant로 만든 엔드포인트만 지원합니다. 일반 Agent Framework 엔드포인트는 사용할 수 없습니다.
{% endhint %}

---

## 추가 요구사항

공통 요구사항 외에 다음이 필요합니다.

- **On-Behalf-Of-User Authorization** 활성화
- 최소 1개의 서브 에이전트 또는 도구
- Enhanced Security and Compliance 워크스페이스는 미지원

---

## 생성 단계 (Step by Step)

### Step 1: 서브 에이전트 생성 및 권한 부여

Supervisor를 만들기 전에 먼저 서브 에이전트를 준비합니다.

**예시: KA + Genie 조합**

```
1. Knowledge Assistant 생성 → 엔드포인트 확인
   - 엔드 유저에게 CAN QUERY 권한 부여

2. Genie Space 생성 → Space ID 확인
   - 엔드 유저에게 Space 접근 + UC 테이블 SELECT 권한 부여

3. (선택) UC Function 생성
   - 엔드 유저에게 EXECUTE 권한 부여

4. (선택) MCP Server 연결
   - UC Connection 생성 후 USE CONNECTION 권한 부여
```

### Step 2: Supervisor 설정

1. **Agents**> **Supervisor Agent**> **Build** 클릭
2. 기본 정보 입력:
   - **Name**: Supervisor 고유 이름
   - **Description**: 전체 시스템 목적 설명
3. **서브 에이전트 추가**(최대 20개):
   - 각 서브 에이전트의 **이름** 과 **Content Description** 입력
   - Description이 태스크 위임 로직에 직접 영향을 줌
4. **Instructions**(선택): Supervisor의 전체 동작 가이드라인

{% hint style="warning" %}
**Description이 라우팅의 핵심입니다.** Supervisor는 각 서브 에이전트의 Description을 기반으로 어떤 에이전트에 태스크를 위임할지 결정합니다. 가능한 한 상세하게 작성하세요.
{% endhint %}

### Step 3: 테스트

1. **Test Your Agent** 패널에서 대화형 테스트
2. 올바른 서브 에이전트로 태스크가 위임되는지 확인
3. **AI Playground** 에서 고급 평가 기능 활용:
   - **AI Judge**: 자동 품질 평가
   - **Synthetic Task Generation**: 합성 태스크로 테스트

### Step 4: 품질 개선

- **Examples** 탭에서 라벨링된 질문/태스크 시나리오 추가
- SME에게 공유 링크 전달하여 피드백 수집
- 자연어 가이드라인 추가 (저장 즉시 적용)
- 재테스트로 개선 효과 검증

### Step 5: 권한 관리

| 권한 수준 | 할 수 있는 일 |
|-----------|---------------|
| **Can Manage** | 설정 편집, 서브 에이전트 관리, 권한 관리 |
| **Can Query** | API/Playground를 통한 쿼리만 가능 (설정 확인 불가) |

### Step 6: 엔드포인트 쿼리

배포된 Supervisor에 다음 방법으로 접근할 수 있습니다:
- **AI Playground** 인터랙티브 인터페이스
- **REST API**(curl)
- **Python SDK**

---

## 라우팅 로직과 접근 제어

Supervisor Agent는 **사용자 인식(User-Aware) 라우팅** 을 구현합니다.

```
사용자 질문 입력
    ↓
사용자의 서브 에이전트 접근 권한 확인
    ↓
┌─ 모든 서브 에이전트 접근 불가 → 대화 종료
├─ 일부 서브 에이전트 접근 가능 → 접근 불가한 에이전트 자동 회피
└─ 모든 서브 에이전트 접근 가능 → Description 기반 최적 에이전트 선택
    ↓
선택된 서브 에이전트에 태스크 위임
    ↓
결과 종합 후 응답
```

이 방식은 사용자가 권한 없는 데이터나 에이전트에 접근하는 것을 원천적으로 차단합니다.

---

## Long-Running Task Mode

복잡한 태스크의 경우, Supervisor Agent는 **Long-Running Task Mode** 를 지원합니다. 이 모드는 복잡한 태스크를 여러 요청/응답 사이클로 자동 분할하여 **타임아웃을 방지** 합니다.

---

## 실전 예제: KA + Genie + Supervisor 조합

### 시나리오

> "고객 지원팀을 위한 AI 어시스턴트를 만들자.
> - 제품 매뉴얼/FAQ는 Knowledge Assistant로 처리
> - 주문/매출 데이터 조회는 Genie Space로 처리
> - 두 에이전트를 Supervisor Agent로 통합"

### 구축 순서

```
Step 1: Knowledge Assistant 생성
  ├── 이름: "product-support-ka"
  ├── Knowledge Source: UC Volume (product_docs/)
  │   ├── product_manual.pdf
  │   ├── faq.md
  │   └── troubleshooting_guide.docx
  └── Instructions: "고객 질문에 친절하게 응답. 반드시 출처 인용."

Step 2: Genie Space 생성
  ├── 이름: "order-analytics-genie"
  ├── 테이블: sales.orders, sales.customers, sales.products
  ├── Knowledge Store:
  │   ├── 컬럼 설명: "order_date = 주문일, revenue = 매출액"
  │   └── JOIN 정의: orders.customer_id = customers.id
  └── Sample Questions: "이번 달 매출은?", "Top 10 고객 리스트"

Step 3: Supervisor Agent 생성
  ├── 이름: "customer-support-supervisor"
  ├── 서브 에이전트 1: product-support-ka
  │   └── Description: "제품 사용법, FAQ, 문제 해결 가이드 관련 질문 처리"
  ├── 서브 에이전트 2: order-analytics-genie
  │   └── Description: "주문, 매출, 고객 데이터 조회 및 분석"
  └── Instructions:
      "고객 지원팀을 위한 통합 어시스턴트.
       제품 관련 질문은 product-support-ka로,
       데이터 조회 질문은 order-analytics-genie로 라우팅."

Step 4: 테스트
  ├── "이 제품 설정 방법이 뭐야?" → KA 라우팅 확인
  ├── "지난달 매출 합계 알려줘" → Genie 라우팅 확인
  └── "VIP 고객의 제품 이용 가이드를 정리해줘" → 복합 라우팅 확인

Step 5: 권한 부여 및 배포
  ├── 고객지원팀에 CAN QUERY 권한 부여
  └── AI Playground 또는 API로 서비스
```

---

## 제한사항

- 영어만 지원
- Supervisor당 최대 20개 서브 에이전트
- Agent Endpoints는 Knowledge Assistant만 지원
- Enhanced Security and Compliance 워크스페이스 미지원
- 에이전트 삭제 시 임시 저장 데이터도 함께 삭제

---

## 오케스트레이션 메커니즘 심층 분석

Supervisor Agent의 핵심은 **"올바른 서브 에이전트에게 올바른 작업을 위임하는 것" ** 입니다. 이 오케스트레이션이 내부적으로 어떻게 작동하는지 이해하면, 라우팅 오류를 예방하고 복잡한 멀티 에이전트 시스템을 안정적으로 운영할 수 있습니다.

### 오케스트레이션 루프 상세

```
[사용자 질문 수신]
    ↓
[Phase 1: 권한 필터링]
    - 질문한 사용자의 ID 확인
    - 각 서브 에이전트에 대한 사용자의 접근 권한 확인
    - 접근 불가한 서브 에이전트를 후보 목록에서 제외
    - 모든 서브 에이전트가 접근 불가 → "권한이 없습니다" 응답 후 종료
    ↓
[Phase 2: 의도 분석 & 라우팅]
    - Supervisor LLM이 질문의 의도를 분석
    - 접근 가능한 서브 에이전트들의 Description을 컨텍스트로 제공
    - Instructions(있는 경우)를 참고하여 라우팅 규칙 적용
    - 최적의 서브 에이전트 1개 선택 (또는 복합 질문 시 순차적으로 여러 개)
    ↓
[Phase 3: 태스크 위임]
    - 선택된 서브 에이전트에 질문(또는 변환된 서브 태스크) 전달
    - 서브 에이전트 유형에 따른 호출 방식:
      · KA Endpoint → REST API 호출
      · Genie Space → Genie API 호출 (사용자 권한으로)
      · UC Function → 함수 실행
      · MCP Server → MCP 프로토콜 호출
    ↓
[Phase 4: 응답 수신 & 종합]
    - 서브 에이전트의 응답 수신
    - 복합 질문인 경우 여러 서브 에이전트의 응답을 종합(Synthesis)
    - 최종 응답 포맷팅
    ↓
[Phase 5: 추가 작업 판단]
    - LLM이 "추가 서브 에이전트 호출이 필요한가?"를 판단
    - 필요하면 Phase 2로 돌아감 (반복)
    - 불필요하면 최종 응답 반환
    ↓
[최종 응답 반환]
```

### 단일 질문 vs 복합 질문 처리

| 질문 유형 | 예시 | 처리 방식 |
|-----------|------|-----------|
| **단일 도메인** | "연차 정책 알려줘" | KA 하나에 직접 라우팅 → 응답 반환 |
| **단일 도메인 (데이터)** | "이번 달 매출은?" | Genie 하나에 직접 라우팅 → SQL 실행 → 응답 반환 |
| **복합 질문** | "VIP 고객 리스트를 뽑아서, 각 고객에게 보낼 맞춤 제안서를 작성해줘" | Genie(VIP 고객 조회) → KA(제안서 템플릿) → 종합 응답 |
| **모호한 질문** | "우리 회사 현황 알려줘" | Supervisor가 가장 관련성 높은 에이전트를 추론하여 라우팅 |

---

## 라우팅 전략: 키워드 vs LLM 판단

Supervisor의 라우팅은 **Description 기반의 LLM 추론** 으로 작동합니다. 이 과정에서 키워드 매칭과 의미론적 판단이 모두 활용됩니다.

### Description이 라우팅에 미치는 영향

Supervisor는 라우팅 시 각 서브 에이전트의 **Description** 을 LLM의 컨텍스트로 제공하고, "이 질문을 어떤 에이전트에 위임해야 하는가?"를 LLM에게 판단하게 합니다. 따라서 Description의 품질이 라우팅 정확도를 직접 결정합니다.

**Description 작성 수준별 비교:**

| 수준 | Description 예시 | 라우팅 정확도 |
|------|-----------------|-------------|
| **나쁨** | "HR 관련 처리" | 50% 이하 — "HR"이 포함된 모든 질문이 여기로 라우팅 |
| **보통** | "사내 HR 정책 문서에 대한 Q&A를 처리합니다" | 70% — 정책 질문은 잘 라우팅되나, 데이터 요청도 잘못 라우팅 |
| **좋음** | "사내 HR 정책(연차, 복리후생, 채용, 평가) 관련 문서 기반 질문에 답변합니다. 정책 규정, 절차, 기준 등 텍스트 정보를 제공하며, 수치 데이터 조회는 처리하지 않습니다." | 90%+ — 역할이 명확하여 데이터 질문과 정확히 구분 |

### 겹치는 도메인 처리 전략

서브 에이전트 간 도메인이 부분적으로 겹칠 때, 라우팅 혼란을 방지하는 전략입니다.

| 문제 상황 | 해결 전략 | Description 작성 예시 |
|-----------|----------|---------------------|
| **KA와 Genie가 동일 도메인** | "문서 기반" vs "데이터 기반" 으로 명확히 구분 | KA: "...텍스트 정보 제공" / Genie: "...수치 데이터 조회" |
| **두 KA의 문서 범위가 겹침** | 담당 문서 유형을 구체적으로 나열 | KA1: "제품 A 매뉴얼" / KA2: "제품 B 매뉴얼" |
| **모호한 질문이 빈번** | Supervisor Instructions에 라우팅 규칙 명시 | "매출, 수량 등 숫자가 포함된 질문은 반드시 Genie로 라우팅" |

### Supervisor Instructions를 활용한 라우팅 제어

Supervisor의 **Instructions** 필드는 전체 시스템의 동작 규칙을 정의합니다. 여기에 라우팅 규칙을 명시하면 LLM 판단의 정확도를 높일 수 있습니다.

**좋은 Instructions 예시:**

```
당신은 고객지원 통합 AI 어시스턴트입니다.

라우팅 규칙:
1. 제품 사용법, FAQ, 문제 해결 관련 질문 → product-support-ka
2. 주문, 매출, 고객 데이터 조회 관련 질문 → order-analytics-genie
3. 외부 시스템(JIRA, Slack) 관련 작업 → external-tools-mcp
4. 위 어디에도 해당하지 않는 질문 → "죄송합니다, 해당 질문은 처리할 수 없습니다"

주의사항:
- 하나의 질문이 여러 에이전트에 해당할 수 있음. 이 경우 순차적으로 호출.
- 데이터 관련 질문은 반드시 Genie로 라우팅 (KA로 보내지 말 것)
- 응답은 항상 한국어로
```

---

## 하위 Agent 간 컨텍스트 전달 방식

Supervisor Agent에서 서브 에이전트 간 데이터와 컨텍스트가 어떻게 전달되는지 이해하는 것은 복합 태스크 처리의 핵심입니다.

### 컨텍스트 전달 모델

```
[Supervisor]
    │
    ├── 질문: "VIP 고객 리스트를 뽑고 이들의 구매 패턴을 분석해줘"
    │
    ├── [1차 호출: Genie Space]
    │   ├── 전달: "VIP 고객 리스트를 조회해줘"
    │   └── 응답: 고객 ID, 이름, 등급, 총 구매액 테이블
    │
    ├── [Supervisor 중간 처리]
    │   ├── Genie 응답을 컨텍스트에 추가
    │   └── 다음 서브 에이전트 호출 판단
    │
    ├── [2차 호출: KA]
    │   ├── 전달: "다음 VIP 고객들의 구매 패턴을 분석해줘: [Genie 결과 요약]"
    │   └── 응답: 구매 패턴 분석 (문서 기반)
    │
    └── [최종 종합]
        └── 두 응답을 결합한 최종 답변
```

### 컨텍스트 전달 시 주의사항

| 항목 | 설명 | 대응 방법 |
|------|------|-----------|
| **토큰 제한** | 서브 에이전트 응답이 길면 다음 호출의 컨텍스트가 넘칠 수 있음 | Instructions에 "간결하게 응답" 지시 |
| **정보 손실** | Supervisor가 응답을 요약할 때 핵심 정보가 누락될 수 있음 | 서브 에이전트에 구조화된 출력 요청 (테이블, JSON) |
| **순서 의존성** | 2차 호출이 1차 결과에 의존하는 경우 순차 실행 필요 | Long-Running Task Mode 활용 |
| **에러 전파** | 1차 서브 에이전트가 실패하면 2차도 실패 | Instructions에 에러 시 대체 동작 정의 |

---

## 디버깅 방법

Supervisor Agent는 여러 컴포넌트가 연결되어 있어 디버깅이 복잡합니다. 체계적인 디버깅 방법을 알아봅니다.

### MLflow Trace를 활용한 디버깅

Supervisor Agent의 Trace는 전체 오케스트레이션 과정을 시각적으로 보여줍니다.

```
Trace 구조 예시:

[Supervisor] ─── 총 소요: 8.2초
├── [Phase 1: 권한 확인] ─── 0.1초
│   └── 접근 가능 에이전트: KA, Genie (MCP 제외)
├── [Phase 2: 라우팅 판단] ─── 1.2초
│   ├── LLM 호출: "이 질문은 데이터 조회 → Genie 선택"
│   └── 선택된 에이전트: order-analytics-genie
├── [Phase 3: Genie 호출] ─── 6.5초
│   ├── SQL 생성: SELECT ... FROM ...
│   ├── SQL 실행: 5.1초
│   └── 결과: 15행 반환
└── [Phase 4: 응답 종합] ─── 0.4초
    └── 최종 응답 생성
```

### 일반적인 문제와 진단 방법

| 문제 증상 | 원인 진단 (Trace 확인 포인트) | 해결 방법 |
|-----------|---------------------------|-----------|
| **잘못된 에이전트로 라우팅** | Phase 2에서 LLM의 판단 근거 확인 | Description을 더 구체적으로 수정 |
| **서브 에이전트 응답이 빈 값** | Phase 3에서 서브 에이전트의 에러 확인 | 서브 에이전트를 단독으로 테스트 |
| **"권한 없음" 에러** | Phase 1에서 권한 확인 결과 | 사용자에게 서브 에이전트 접근 권한 부여 |
| **타임아웃** | 각 Phase의 소요 시간 확인 | Long-Running Task Mode 활성화 또는 서브 에이전트 최적화 |
| **복합 질문에 일부만 답변** | Phase 5에서 추가 호출 판단 확인 | Instructions에 복합 질문 처리 규칙 명시 |
| **응답 언어가 일관되지 않음** | Phase 4에서 종합 프롬프트 확인 | Instructions에 "반드시 한국어로 응답" 명시 |

### 단계별 디버깅 체크리스트

```
1. 서브 에이전트 단독 테스트
   □ 각 서브 에이전트(KA, Genie)를 AI Playground에서 개별 테스트
   □ 단독으로 잘 작동하는지 확인 → 문제가 있으면 서브 에이전트 자체를 수정

2. 라우팅 테스트
   □ 각 서브 에이전트 전용 질문으로 Supervisor 테스트
   □ 올바른 에이전트로 라우팅되는지 Trace에서 확인
   □ 잘못 라우팅되면 Description 수정

3. 복합 질문 테스트
   □ 여러 에이전트가 필요한 질문으로 테스트
   □ 순차 호출이 올바르게 이루어지는지 확인
   □ 컨텍스트 전달이 제대로 되는지 확인

4. 에지 케이스 테스트
   □ 어떤 에이전트에도 해당하지 않는 질문
   □ 권한 없는 사용자의 질문
   □ 매우 긴 질문 또는 다국어 질문
```

---

## Supervisor Agent 아키텍처 패턴

실제 프로덕션 환경에서 자주 사용되는 Supervisor 아키텍처 패턴을 정리합니다.

### 패턴 1: 문서 + 데이터 통합

가장 기본적이고 흔한 패턴입니다.

```
[Supervisor]
├── [KA: 정책/매뉴얼] — 텍스트 기반 Q&A
└── [Genie: 운영 데이터] — 데이터 기반 분석
```

**적합한 유스케이스**: HR봇, 고객지원봇, 영업지원봇

### 패턴 2: 도메인별 전문 에이전트

여러 전문 도메인을 하나의 인터페이스로 통합합니다.

```
[Supervisor]
├── [KA: 제품 A 문서]
├── [KA: 제품 B 문서]
├── [KA: 공통 FAQ]
└── [Genie: 제품별 성과 데이터]
```

**적합한 유스케이스**: 멀티 제품 고객지원, 멀티 부서 사내 포털

### 패턴 3: 외부 시스템 연동

MCP Servers와 UC Functions를 활용하여 외부 시스템과 연동합니다.

```
[Supervisor]
├── [KA: 내부 문서]
├── [Genie: 내부 데이터]
├── [MCP: Slack 알림 전송]
├── [MCP: JIRA 티켓 생성]
└── [UC Function: 이메일 전송]
```

**적합한 유스케이스**: 업무 자동화, IT 헬프데스크

### 패턴 4: 계층적 Supervisor (Nested)

복잡한 조직 구조에 맞춰 Supervisor를 계층적으로 구성합니다.

```
[최상위 Supervisor]
├── [하위 Supervisor: 영업팀]
│   ├── [KA: 영업 매뉴얼]
│   └── [Genie: 영업 데이터]
├── [하위 Supervisor: 마케팅팀]
│   ├── [KA: 마케팅 가이드]
│   └── [Genie: 마케팅 성과]
└── [KA: 공통 HR 정책]
```

{% hint style="warning" %}
**계층적 Supervisor 주의사항**: 현재 Agent Bricks의 Supervisor는 다른 Supervisor를 직접 서브 에이전트로 등록할 수 없습니다. 이 패턴을 구현하려면 하위 Supervisor를 **Agent Framework(코드 기반)** 으로 구축하고, Model Serving Endpoint로 배포한 후 연결해야 합니다. 다만 Agent Endpoints는 KA만 지원하므로, 이 패턴은 현재 **UC Function 또는 MCP** 를 통한 간접 연결로만 가능합니다.
{% endhint %}
