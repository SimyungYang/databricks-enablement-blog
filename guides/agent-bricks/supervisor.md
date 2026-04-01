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
| **Genie Spaces**| 데이터 탐색 인터페이스 | Space 접근 + UC 객체 권한 |
| **Agent Endpoints**| Knowledge Assistant 엔드포인트만 지원 | `CAN QUERY` |
| **Unity Catalog Functions**| 커스텀 도구 (UC 함수) | `EXECUTE` |
| **External MCP Servers**| MCP 프로토콜 서버 (Bearer Token/OAuth) | `USE CONNECTION` (UC Connection) |

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
   - 각 서브 에이전트의 **이름**과 **Content Description** 입력
   - Description이 태스크 위임 로직에 직접 영향을 줌
4. **Instructions**(선택): Supervisor의 전체 동작 가이드라인

{% hint style="warning" %}
**Description이 라우팅의 핵심입니다.**Supervisor는 각 서브 에이전트의 Description을 기반으로 어떤 에이전트에 태스크를 위임할지 결정합니다. 가능한 한 상세하게 작성하세요.
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
| **Can Manage**| 설정 편집, 서브 에이전트 관리, 권한 관리 |
| **Can Query**| API/Playground를 통한 쿼리만 가능 (설정 확인 불가) |

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

복잡한 태스크의 경우, Supervisor Agent는 **Long-Running Task Mode**를 지원합니다. 이 모드는 복잡한 태스크를 여러 요청/응답 사이클로 자동 분할하여 **타임아웃을 방지** 합니다.

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
