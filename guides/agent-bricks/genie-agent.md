# Genie Spaces 연동

---

## 개요

Genie Spaces는 Unity Catalog에 등록된 **테이블 데이터를 자연어 챗봇**으로 변환합니다. 비즈니스 사용자가 SQL 없이도 데이터에 질문할 수 있으며, 내부적으로 자연어를 SQL로 변환하여 실행합니다.

**적합한 유스케이스:**
- 비즈니스 데이터 탐색 (매출, 재고, 고객 분석)
- 셀프 서비스 분석 (비기술 사용자가 직접 데이터 조회)
- KPI/메트릭 확인 (일별/월별 성과 지표)
- 임원 대시보드 대체 (자연어로 원하는 데이터를 즉시 조회)

---

## 작동 원리

Genie는 단일 LLM이 아닌 **복합 AI 시스템(Compound AI System)**입니다.

```
사용자 질문 (자연어)
    ↓
Genie 파싱 & 관련 데이터 소스 식별
    ↓
Unity Catalog 메타데이터 + Knowledge Store 컨텍스트 필터링
    ↓
읽기 전용 SQL 쿼리 생성
    ↓
SQL Warehouse에서 실행
    ↓
결과 반환 (테이블/차트)
```

**응답에 활용되는 컨텍스트:**
- Unity Catalog 테이블/컬럼 메타데이터
- Knowledge Store (작성자가 큐레이션한 공간 수준 컨텍스트)
- 예시 SQL 쿼리 및 SQL 함수
- 텍스트 지시사항 및 대화 이력

{% hint style="info" %}
Genie는 **읽기 전용 SQL만 생성**합니다. INSERT, UPDATE, DELETE 등의 쓰기 쿼리는 절대 실행되지 않으므로 데이터 안전성이 보장됩니다.
{% endhint %}

---

## 사전 요구사항

| 요구사항 | 설명 |
|----------|------|
| **SQL Warehouse**| Pro 또는 Serverless SQL Warehouse |
| **Unity Catalog**| 데이터가 UC에 등록되어 있어야 함 |
| **테이블 제한**| 공간당 최대 30개 테이블/뷰 |
| **처리량**| UI: 20 질문/분, API: 5 질문/분 (무료 티어) |
| **용량**| 공간당 10,000 대화, 대화당 10,000 메시지 |

**필요 권한:**
- Databricks SQL 워크스페이스 자격
- SQL Warehouse에 대한 `CAN USE` 접근
- 데이터 객체에 대한 `SELECT` 권한

---

## 생성 및 설정

### Step 1: Genie Space 생성

1. 좌측 메뉴에서 **Genie**> **New**클릭
2. Unity Catalog에서 데이터 소스 (테이블/뷰) 선택
3. **Create**클릭

### Step 2: Knowledge Store 설정

생성 후 반드시 Knowledge Store를 설정하세요. 이것이 Genie의 정확도를 결정합니다.

| 설정 항목 | 설명 | 예시 |
|-----------|------|------|
| **테이블/컬럼 설명**| 비즈니스 용어, 동의어 정의 | `order_amt` → "주문 금액 (원화, VAT 포함)" |
| **JOIN 관계**| 테이블 간 연결 정의 | `orders.customer_id = customers.id` |
| **재사용 가능 SQL 표현식**| 측정값, 필터, KPI용 표현식 | 월별 매출 합계, YoY 성장률 계산식 |
| **프롬프트 매칭**| 형식 지원, 엔터티 교정 | "매출" → `revenue`, "이번 달" → `CURRENT_MONTH` |

### Step 3: Instructions & Examples 추가 (최대 100개)

- 정적 또는 파라미터화된 SQL 쿼리 (자연어 제목 포함)
- Unity Catalog 함수 (복잡한 로직용)
- 텍스트 지시사항 (비즈니스 컨텍스트, 형식 규칙)

{% hint style="info" %}
**예시 등록 팁**: "이번 달 매출은?"이라는 질문에 대해 정확한 SQL을 등록해두면, 유사한 질문("이번 달 수익은?", "이달 매출 합계는?")에도 올바른 SQL이 생성됩니다.
{% endhint %}

### Step 4: 공간 설정

- 제목, 설명 (마크다운 지원)
- 기본 SQL Warehouse 설정
- 사용자 안내용 샘플 질문 등록
- 태그 분류

---

## 모니터링 및 개선

**Monitoring**탭에서 다음을 확인할 수 있습니다:
- 사용자가 질문한 모든 내용
- 사용자 피드백 (좋아요/싫어요)
- 플래그된 응답

이를 바탕으로 Knowledge Store와 Instructions를 반복적으로 개선합니다.

---

## Agent Bricks에서의 활용: Supervisor 서브 에이전트로 사용

Genie Spaces는 **Supervisor Agent의 서브 에이전트**로 사용할 수 있습니다. 이를 통해 문서 Q&A(Knowledge Assistant)와 데이터 분석(Genie)을 하나의 멀티 에이전트 시스템으로 통합할 수 있습니다.

### 전체 연결 흐름

```
1. Genie Space 생성 및 Knowledge Store 설정 완료
    ↓
2. Supervisor Agent 생성 화면에서 "Add Sub-Agent" 클릭
    ↓
3. 에이전트 유형으로 "Genie Space" 선택
    ↓
4. 연결할 Genie Space 선택
    ↓
5. Description 작성 (Supervisor가 언제 이 에이전트에 라우팅할지 판단하는 기준)
    ↓
6. 저장 후 테스트 — Supervisor에 데이터 관련 질문을 하면 Genie로 라우팅됨
```

### SQL 분석 에이전트로서의 활용 예시

**시나리오**: 사내 HR봇에 "우리 팀 인원 현황"을 질문하면 데이터로 답변

```
[Supervisor Agent]
├── [KA: HR 정책 문서] — "연차 정책 알려줘" → 문서 기반 답변
└── [Genie: HR 데이터] — "우리 팀 인원 현황" → SQL 실행 후 테이블 반환
```

Supervisor의 Description 예시:
- KA: "회사 HR 정책, 복리후생, 규정 관련 질문을 처리합니다"
- Genie: "직원 수, 부서별 인원, 입퇴사 현황 등 HR 데이터를 조회합니다"

---

## 제한사항과 해결 방법

| 제한사항 | 상세 | 해결 방법 |
|----------|------|-----------|
| **테이블 수 30개 제한**| 한 공간에 30개 초과 불가 | 비즈니스 도메인별로 Space를 분리하고 Supervisor로 통합 |
| **API 처리량 제한**| 무료 티어 기준 5 질문/분 | 프로비전된 처리량(Provisioned Throughput) 사용 검토 |
| **복잡한 JOIN**| 3단계 이상 JOIN은 정확도 저하 | 미리 JOIN된 뷰(View)를 생성하여 등록 |
| **비정형 데이터**| JSON, Array 등 복잡한 타입 지원 제한 | 정규화된 테이블로 변환 후 등록 |
| **실시간 데이터**| 스트리밍 데이터 직접 지원 안 함 | Delta Live Tables로 물리화 후 Genie에 연결 |
| **차트 커스터마이징**| 기본 차트만 제공, 세부 설정 제한 | Databricks Apps(Streamlit 등)와 연계하여 커스텀 시각화 구현 |

{% hint style="warning" %}
**Genie Space를 Supervisor에 연결하려면**해당 Space의 소유자이거나 `CAN MANAGE` 권한이 있어야 합니다. 또한 Supervisor의 서비스 프린시펄에게 Genie Space와 관련 테이블에 대한 접근 권한을 부여해야 합니다.
{% endhint %}
