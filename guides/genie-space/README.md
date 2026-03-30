# Genie Space 실전 가이드

> **최종 업데이트**: 2026-03-27

---

## Genie Space란?

Genie Space는 Databricks의 AI 기반 자연어 데이터 분석 인터페이스입니다. 비즈니스 사용자가 **SQL을 몰라도** 자연어로 질문하면, AI가 SQL 쿼리를 자동 생성하고 결과를 반환합니다.

### 핵심 특징

| 특징 | 설명 |
|------|------|
| **자연어 질의** | 일상 언어로 데이터에 질문 |
| **SQL 자동 생성** | AI가 질문을 분석하여 정확한 SQL 쿼리 생성 |
| **도메인 맞춤** | 조직 고유의 용어와 비즈니스 로직 반영 가능 |
| **거버넌스 내장** | Unity Catalog 기반 행/열 수준 보안 적용 |
| **신뢰도 표시** | Trusted 마크로 검증된 응답 식별 |
| **다국어 지원** | 한국어 포함 다양한 언어로 질문 가능 |

---

## 동작 원리

Genie는 단일 LLM이 아닌 복합 AI 시스템(Compound AI System)으로, 다음 요소를 종합적으로 참조합니다:

* 테이블/컬럼 메타데이터
* Primary/Foreign Key 관계
* 예제 SQL 쿼리
* 작성자가 제공한 인스트럭션
* 대화 히스토리

### 지원 데이터 소스

* Unity Catalog의 Managed 및 External 테이블
* Foreign 테이블
* 뷰(View) 및 Materialized View
* 파일 업로드 (CSV, Excel) — Public Preview

---

## 필수 요구 사항

**Space 생성자:**

* Databricks SQL 워크스페이스 권한 (Entitlement)
* Pro 또는 Serverless SQL Warehouse에 대한 CAN USE 권한
* Unity Catalog 데이터 객체에 대한 SELECT 권한

**최종 사용자:**

* Consumer Access 또는 Databricks SQL 워크스페이스 권한
* 관련 데이터 객체에 대한 SELECT 권한
* Genie Space에 대한 최소 CAN VIEW/CAN RUN 권한

{% hint style="info" %}
최종 사용자는 SQL Warehouse에 대한 직접적인 권한이 필요하지 않습니다. Space 설정에서 지정한 Default Warehouse의 자격 증명이 자동으로 적용됩니다.
{% endhint %}

---

## Agent Mode

### Agent Mode란?

Agent Mode(이전 명칭: Research Agent)는 Genie Space의 고급 기능으로, 단순 쿼리를 넘어 **다단계 추론과 가설 검증**을 통해 깊이 있는 인사이트를 도출합니다.

### 주요 기능

* **연구 계획 수립**: 복잡한 질문에 대한 구조화된 접근 방식 및 가설 개발
* **다중 쿼리 실행**: 여러 SQL 쿼리를 실행하여 다각도로 데이터 수집
* **반복 학습**: 발견한 내용을 기반으로 분석 방법론 지속 조정
* **종합 보고서**: 인용, 시각화, 지원 테이블이 포함된 상세 요약 제공

### 사용 방법

1. Genie Space를 엽니다.
2. 채팅 입력란의 **Agent Mode 아이콘**을 클릭합니다.
3. 질문을 입력하고 전송합니다.
4. Agent가 필요 시 확인 질문을 하고, 완료 후 종합 보고서를 제공합니다.

### 적합한 질문 예시

* "이번 분기 매출이 급증한 원인은 무엇인가?"
* "가장 수익성 높은 고객 세그먼트는?"
* "마케팅 캠페인 중 ROI가 가장 높은 것은? 그 이유는?"

{% hint style="info" %}
Agent Mode는 현재 Public Preview이며, 표준 Warehouse 컴퓨팅 비용 외 추가 비용은 없습니다. 보고서는 PDF로 내보내기가 가능합니다.
{% endhint %}

---

## 베스트 프랙티스

### 핵심 원칙

Genie를 **신입 데이터 분석가**라고 생각하세요. 명확한 컨텍스트, 구조화된 메타데이터, 예제 쿼리를 제공해야 합니다.

### 테이블 구성

| 원칙 | 상세 |
|------|------|
| **작게 시작** | 5개 이하 테이블로 시작, 필요 시 확장 |
| **사전 조인** | 관련 테이블을 뷰로 미리 조인하여 복잡도 감소 |
| **30개 제한** | 최대 30개 테이블, 초과 시 뷰로 통합 |
| **Metric View 활용** | 지표, 차원, 집계를 Metric View로 정의 |
| **불필요 컬럼 숨김** | 혼란을 줄 수 있는 컬럼은 Hide 처리 |

### 컬럼 설명

* **명확하고 구체적인** 컬럼 이름과 설명 작성
* AI 생성 설명을 사용할 경우 반드시 **검증** 후 적용
* 모호하거나 불필요한 세부사항 제거
* Space 전용 메타데이터와 동의어(synonym) 추가

### 인스트럭션 작성

```
우선순위:
1. SQL 표현식 → 비즈니스 용어를 정확한 SQL로 정의
2. 예제 SQL 쿼리 → 복잡한 다단계 질문에 대한 답변 시연
3. 텍스트 인스트럭션 → 글로벌 컨텍스트만 (최후의 수단)
```

**일관성 유지**: 예제, 표현식, 텍스트 인스트럭션 간 **모순되는 지침이 없도록** 주의하세요.

### 개발 접근법

1. **목적 정의**: 특정 대상과 주제에 집중 (범용 X)
2. **최소 시작**: 최소한의 인스트럭션과 제한된 질문으로 시작
3. **직접 테스트**: Space의 첫 번째 사용자가 되어 직접 테스트
4. **SQL 검증**: 생성된 SQL을 꼼꼼히 검토
5. **점진적 확장**: 피드백 기반으로 인스트럭션을 점진적으로 추가
6. **도메인 전문가 참여**: SQL에 능통한 데이터 분석가가 구축

### 사용자 테스트 가이드

* 사용자에게 **개선 협업**임을 미리 안내
* Space가 정의한 **주제 범위** 내에서 테스트하도록 안내
* **좋아요/싫어요** 피드백 적극 활용 유도
* 추가 피드백은 작성자에게 직접 공유

---

## Genie Space vs Genie Code 비교

| 비교 항목 | Genie Space | Genie Code |
|-----------|-------------|------------|
| **대상 사용자** | 비즈니스 사용자, 비기술 인력 | 데이터 엔지니어, 사이언티스트, 분석가 |
| **주요 목적** | 자연어 데이터 질의 | AI 기반 코딩 지원 및 자동화 |
| **인터페이스** | 전용 채팅 공간 | 워크스페이스 전체에 내장된 패널 |
| **입력 방식** | 자연어 질문 | 자연어 + 코드 + Slash 명령어 |
| **출력** | SQL 결과 테이블, 시각화, 요약 | 코드, 노트북 셀, 대시보드, 파이프라인 |
| **설정** | 도메인 전문가가 테이블/인스트럭션 사전 구성 | 별도 설정 불필요 (Unity Catalog 자동 참조) |
| **거버넌스** | Space 단위 권한 관리 | 워크스페이스 및 Unity Catalog 권한 |
| **비용** | SQL Warehouse 컴퓨팅 | 노트북/쿼리/작업 컴퓨팅 |
| **Agent Mode** | 다단계 연구 분석, PDF 보고서 | 다단계 워크플로 자동화, 코드 생성/실행 |
| **적합한 사용 사례** | "지난 달 매출은 얼마야?" | "ETL 파이프라인을 만들어줘" |

### 언제 무엇을 사용할까?

**Genie Space를 사용하세요:**

* 비기술 사용자가 데이터에 접근해야 할 때
* 반복적인 비즈니스 질의를 셀프서비스로 제공할 때
* 도메인 특화된 데이터 질의 환경이 필요할 때
* SQL을 모르는 팀원도 데이터 분석을 해야 할 때

**Genie Code를 사용하세요:**

* 복잡한 데이터 파이프라인을 구축할 때
* ML 모델을 학습하고 배포할 때
* 대시보드를 생성하고 관리할 때
* 코드 디버깅과 최적화가 필요할 때
* GenAI 애플리케이션을 개발할 때

---

## 참고 자료

* [Databricks Genie Space 공식 문서](https://docs.databricks.com/aws/en/genie/)
* [Genie Space 설정 가이드](https://docs.databricks.com/aws/en/genie/set-up)
* [Genie Space 베스트 프랙티스](https://docs.databricks.com/aws/en/genie/best-practices)
* [Genie Code 공식 문서](https://docs.databricks.com/aws/en/genie-code/)
* [Genie Code 사용법 (Azure)](https://learn.microsoft.com/en-us/azure/databricks/genie-code/use-genie-code)
* [Genie Agent Mode](https://docs.databricks.com/aws/en/genie/agent-mode)
* [MCP on Databricks 공식 문서](https://docs.databricks.com/aws/en/generative-ai/mcp/)
