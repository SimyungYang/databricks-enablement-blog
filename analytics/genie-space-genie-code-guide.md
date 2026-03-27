# Databricks Genie Space & Genie Code 실전 가이드

> **최종 업데이트**: 2026-03-27

---

## 목차

1. [Genie Space 개요](#1-genie-space-개요)
2. [Genie Space 생성하기](#2-genie-space-생성하기)
3. [테이블 및 지식 저장소 구성](#3-테이블-및-지식-저장소-구성)
4. [인스트럭션 작성 가이드](#4-인스트럭션-작성-가이드)
5. [샘플 질문 및 벤치마크](#5-샘플-질문-및-벤치마크)
6. [공유 및 권한 관리](#6-공유-및-권한-관리)
7. [모니터링 및 피드백](#7-모니터링-및-피드백)
8. [Agent Mode](#8-agent-mode)
9. [Genie Space 베스트 프랙티스](#9-genie-space-베스트-프랙티스)
10. [Genie Code 개요](#10-genie-code-개요)
11. [Genie Code 사용법](#11-genie-code-사용법)
12. [Genie Code 활용 시나리오](#12-genie-code-활용-시나리오)
13. [Genie Space vs Genie Code 비교](#13-genie-space-vs-genie-code-비교)
14. [MCP(Model Context Protocol)와 Genie Code 연동](#14-mcpmodel-context-protocol와-genie-code-연동)

---

## 1. Genie Space 개요

### Genie Space란?

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

### 동작 원리

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

### 필수 요구 사항

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

## 2. Genie Space 생성하기

### Step 1: Genie Space 만들기

1. Databricks 워크스페이스 좌측 사이드바에서 **Genie**를 클릭합니다.
2. 우측 상단의 **New** 버튼을 클릭합니다.
3. 데이터 소스(테이블/뷰)를 선택합니다.
4. **Create** 버튼을 클릭합니다.

### Step 2: 기본 설정 구성

**Configure > Settings** 메뉴에서 다음을 설정합니다:

| 설정 항목 | 설명 |
|-----------|------|
| **Title** | Space 이름 (워크스페이스 브라우저에 표시) |
| **Default Warehouse** | 쿼리 실행에 사용할 SQL Warehouse 선택 |
| **Description** | Space 목적 설명 (Markdown 지원) |
| **Sample Questions** | 사용자에게 보여줄 예시 질문 |
| **Tags** | 조직/분류를 위한 태그 |
| **File Uploads** | CSV/Excel 파일 업로드 허용 여부 |

{% hint style="warning" %}
Description은 사용자가 Space를 열 때 가장 먼저 보는 텍스트입니다. Space의 목적, 다루는 데이터 범위, 사용 팁 등을 Markdown 형식으로 명확하게 작성하세요.
{% endhint %}

### Step 3: 데이터 객체 추가

1. **Configure > Data** 메뉴로 이동합니다.
2. **Add** 버튼으로 테이블/뷰를 추가합니다.
3. Overview 탭에서 컬럼 이름, 데이터 타입, 설명을 확인합니다.
4. Sample data 탭에서 실제 데이터를 미리 확인합니다.
5. 불필요한 테이블은 휴지통 아이콘으로 제거합니다.

{% hint style="tip" %}
테이블은 **5개 이하**로 시작하는 것을 권장합니다. 최대 30개까지 추가할 수 있지만, 적을수록 정확도가 높아집니다.
{% endhint %}

---

## 3. 테이블 및 지식 저장소 구성

### 지식 저장소(Knowledge Store)란?

지식 저장소는 Genie가 정확한 응답을 생성하기 위해 참조하는 메타데이터와 비즈니스 로직의 모음입니다.

### 3.1 메타데이터 커스터마이징

Space 전용 테이블/컬럼 설명을 추가할 수 있습니다. Unity Catalog의 원본 설명을 덮어쓰지 않고, Space에만 적용되는 별도의 설명을 관리합니다.

**설정 방법:**

1. Configure > Data에서 테이블을 선택합니다.
2. 각 컬럼에 Space 전용 설명과 동의어(synonym)를 추가합니다.
3. 혼란을 줄 수 있는 불필요한 컬럼은 숨김(Hide) 처리합니다.

**좋은 컬럼 설명 예시:**

```
컬럼: status
설명: "주문 상태를 나타냅니다. 가능한 값: 'pending'(대기), 'shipped'(발송), 'delivered'(배송완료), 'cancelled'(취소)"
```

### 3.2 프롬프트 매칭(Prompt Matching)

프롬프트 매칭을 활성화하면 사용자의 입력 언어를 실제 데이터 값과 매칭합니다. 예를 들어, 사용자가 "서울"이라고 입력하면 데이터의 "Seoul" 값과 자동 매칭됩니다.

### 3.3 조인 관계 정의

테이블 간 연결 관계를 명시적으로 정의합니다.

**설정 방법:**

* 간단한 경우: 컬럼 동등 구문 사용

  ```
  accounts.id = opportunity.accountid
  ```

* 복잡한 경우: SQL 표현식으로 정의

  ```sql
  orders.customer_id = customers.id AND orders.region = customers.region
  ```

### 3.4 SQL 표현식 (SQL Expressions)

비즈니스 로직을 재사용 가능한 **Measure, Filter, Dimension**으로 정의합니다.

| 유형 | 용도 | 예시 |
|------|------|------|
| **Measure** | 지표/메트릭 정의 | `SUM(order_total) AS total_revenue` |
| **Filter** | 자주 사용하는 필터 | `status = 'active' AND created_at > '2025-01-01'` |
| **Dimension** | 분석 차원 정의 | `CASE WHEN age < 30 THEN 'Young' ELSE 'Senior' END AS age_group` |

{% hint style="info" %}
SQL 표현식은 별도의 제한(최대 200개)이 적용됩니다. 텍스트 인스트럭션보다 SQL 표현식으로 비즈니스 로직을 정의하는 것이 더 정확한 결과를 얻을 수 있습니다.
{% endhint %}

---

## 4. 인스트럭션 작성 가이드

### 인스트럭션 우선순위

Genie에 비즈니스 로직을 전달할 때는 다음 우선순위를 따르세요:

```
1순위: SQL 표현식 (가장 정확)
   ↓
2순위: 예제 SQL 쿼리 (복잡한 시나리오)
   ↓
3순위: 텍스트 인스트럭션 (최후의 수단)
```

### 4.1 예제 SQL 쿼리 추가

**Configure > SQL Queries** 탭에서 추가합니다.

**작성 규칙:**

* 제목은 사용자가 실제로 물어볼 법한 **가장 일반적인 표현**으로 작성
* 파라미터화된 쿼리는 **Trusted** 마크가 부여됨
* 복잡한 로직은 Unity Catalog에 **커스텀 함수**로 등록 가능

**예시:**

```sql
-- 제목: "이번 분기 매출 상위 10개 제품은?"
SELECT
    product_name,
    SUM(amount) as total_sales
FROM sales.transactions
WHERE quarter = QUARTER(CURRENT_DATE())
  AND year = YEAR(CURRENT_DATE())
GROUP BY product_name
ORDER BY total_sales DESC
LIMIT 10
```

### 4.2 SQL 함수 등록

복잡한 비즈니스 로직은 Unity Catalog에 커스텀 함수로 등록하고, Genie Space에서 참조합니다. 함수를 사용한 응답은 **Trusted**로 표시됩니다.

### 4.3 텍스트 인스트럭션 작성

**Configure > Text Instructions** 탭에서 추가합니다.

**좋은 예시와 나쁜 예시:**

| 구분 | 예시 |
|------|------|
| **나쁜 예** | "매출에 대해 질문하면 명확히 해달라고 물어봐" |
| **좋은 예** | "사용자가 매출 지표를 질문하면서 제품명이나 판매 채널을 명시하지 않은 경우, 다음과 같이 확인 질문을 해라: '분석할 제품명과 판매 채널을 지정해 주세요.'" |

### 4.4 명확화 질문(Clarification) 인스트럭션

4가지 구성 요소로 작성합니다:

1. **트리거 조건**: "사용자가 팀 성과 분석을 요청하면..."
2. **누락 정보**: "...기간, 팀명, KPI를 명시하지 않았을 때..."
3. **필요 행동**: "...반드시 확인 질문을 먼저 해라..."
4. **예시**: "분석할 기간과 팀명, 확인하고 싶은 KPI를 알려주세요."

{% hint style="warning" %}
명확화 인스트럭션은 일반 가이드 뒤에 배치하세요. 전체 General Instructions 텍스트 블록은 100개 인스트럭션 제한 중 **1개**로 계산됩니다.
{% endhint %}

### 4.5 요약(Summary) 커스터마이징

"인스트럭션 중 요약 생성 시 반드시 따를 규칙" 섹션을 별도로 추가할 수 있습니다:

* 응답 언어 지정 (예: "항상 한국어로 요약해라")
* 포맷 요구사항 (불릿 포인트, 인용 포함 등)
* 데이터 범위 명시

{% hint style="info" %}
텍스트 인스트럭션만 요약에 영향을 미칩니다. SQL 예제와 SQL 표현식은 요약 생성에 반영되지 않습니다.
{% endhint %}

---

## 5. 샘플 질문 및 벤치마크

### 샘플 질문

샘플 질문은 사용자가 채팅 창을 열었을 때 표시되는 예시 질문입니다.

**설정 방법:**

1. Configure > Settings에서 **Sample Questions** 섹션으로 이동합니다.
2. Space가 다루는 주제를 대표하는 질문을 추가합니다.

**좋은 샘플 질문 예시:**

* "지난 달 매출 상위 5개 지역은?"
* "올해 신규 고객 수 추이를 보여줘"
* "제품 카테고리별 반품률을 비교해줘"

### 벤치마크

검증된 질문-응답 쌍을 벤치마크로 등록하여 Space의 정확도를 체계적으로 평가할 수 있습니다.

**벤치마크 추가 방법:**

1. 채팅에서 질문을 입력하고 응답을 확인합니다.
2. 응답이 정확하면 케밥 메뉴(⋮)에서 **Add as benchmark**를 선택합니다.
3. 다양한 표현으로 같은 질문을 테스트합니다.

---

## 6. 공유 및 권한 관리

### 권한 레벨

| 권한 | 설명 |
|------|------|
| **CAN MANAGE** | Space 설정, 인스트럭션, 모니터링 전체 관리 |
| **CAN EDIT** | 인스트럭션 및 설정 편집 |
| **CAN RUN** | 질문 실행 및 결과 확인 |
| **CAN VIEW** | Space 내용 열람만 가능 |

### 공유 방법

1. Space 우측 상단의 **Share** 버튼을 클릭합니다.
2. 사용자 또는 그룹을 검색하여 추가합니다.
3. 적절한 권한 레벨을 선택합니다.
4. 공유하면 해당 사용자에게 **이메일 알림**이 발송됩니다.
5. **Copy link** 버튼으로 공유 링크를 생성할 수도 있습니다.

{% hint style="tip" %}
새로 생성된 Space는 기본적으로 생성자의 사용자 폴더에 저장됩니다. 팀 공용으로 사용할 경우 공유 폴더로 이동하는 것을 권장합니다.
{% endhint %}

---

## 7. 모니터링 및 피드백

### 모니터링 탭

CAN MANAGE 권한을 가진 사용자는 **Monitoring** 탭에서 다음을 확인할 수 있습니다:

* 사용자들이 던진 질문 목록
* 각 질문에 대한 응답 내용
* 사용자 피드백 (좋아요/싫어요)
* 시간, 평점, 사용자, 상태별 필터링

### 피드백 메커니즘

모든 응답에는 **"Is this correct?"** 프롬프트가 표시됩니다:

| 옵션 | 동작 |
|------|------|
| **Yes** | 응답이 정확함을 확인 |
| **Fix it** | 오류를 설명하고 재시도 요청 |
| **Request review** | Space 관리자에게 검토 요청 (코멘트 추가 가능) |

### 응답 활용

각 응답에서 다음 작업이 가능합니다:

* **Show code**: 생성된 SQL 쿼리 확인
* **CSV 다운로드**: 최대 약 1GB의 결과 데이터를 CSV로 다운로드
* **Copy CSV**: 클립보드에 CSV 데이터 복사
* **Add as instruction**: 검증된 응답을 인스트럭션으로 추가
* **Add as benchmark**: 벤치마크로 등록
* **Refresh data**: 데이터 새로고침
* **Regenerate response**: 응답 재생성

### 반복 개선 프로세스

```
1. 모니터링 탭에서 사용자 질문 패턴 분석
   ↓
2. 오답이나 부정확한 응답 식별
   ↓
3. 해당 질문에 대한 인스트럭션/예제 쿼리 추가
   ↓
4. 벤치마크로 등록하여 정확도 추적
   ↓
5. 반복
```

---

## 8. Agent Mode

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

## 9. Genie Space 베스트 프랙티스

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

## 10. Genie Code 개요

### Genie Code란?

Genie Code는 Databricks에 내장된 **자율형 AI 코딩 파트너**입니다. Genie Space가 비즈니스 사용자를 위한 자연어 질의 도구라면, Genie Code는 **데이터 엔지니어, 데이터 사이언티스트, 분석가**를 위한 AI 코딩 어시스턴트입니다.

### 핵심 차별점

| 특징 | 설명 |
|------|------|
| **Unity Catalog 통합** | 테이블, 컬럼, 리니지 등 전체 데이터 환경 이해 |
| **컨텍스트 인식** | 조직의 메타데이터, 인기 데이터 자산을 참조하여 개인화된 응답 |
| **멀티 스텝 자동화** | 복잡한 다단계 작업을 자율적으로 수행 |
| **거버넌스 준수** | 기존 접근 제어 및 거버넌스 정책 자동 적용 |
| **추가 비용 없음** | 모든 기능 무료, 컴퓨팅 리소스 비용만 부과 |

### 지원 제품 영역

| 영역 | Genie Code 기능 |
|------|-----------------|
| **Notebooks** | 탐색적 데이터 분석(EDA), 모델 학습 자동화 |
| **Lakeflow Pipelines Editor** | ETL 워크로드 자동화, Spark Declarative Pipeline 구축 |
| **Dashboards** | 프로덕션 수준 대시보드 계획 및 생성 |
| **MLflow** | GenAI 앱 이해, 디버깅, 개선 |
| **SQL Editor** | 데이터 탐색 및 분석 |
| **File Editor** | 코드 파일 편집 지원 |

---

## 11. Genie Code 사용법

### 11.1 Genie Code 패널 열기

페이지 우측 상단의 **Sparkle 아이콘**을 클릭하면 Genie Code 패널이 열립니다.

### 11.2 두 가지 모드

Genie Code는 **Chat 모드**와 **Agent 모드**를 제공합니다:

| 모드 | 기능 | 적합한 상황 | 예시 프롬프트 |
|------|------|-------------|---------------|
| **Chat** | 질문 답변, 코드 생성/실행 | 코드 설명, 개념 학습, 간단한 코드 생성 | "이 함수는 뭘 하는 거야?", "Unity Catalog가 뭐야?", "이 함수의 단위 테스트 작성해줘" |
| **Agent** | 다단계 워크플로 자동화, 솔루션 계획, 자산 탐색, 코드 실행, 오류 자동 수정 | EDA, 노트북 정리, 대시보드 생성, 파이프라인 구축 | "`@example_table`에 대해 EDA 수행하고 인사이트 요약해줘", "이 데이터로 대시보드를 만들어줘", "매일 `@example_table`을 업데이트하는 파이프라인 만들어줘" |

{% hint style="warning" %}
Agent 모드는 일부 제품 영역에서만 사용 가능합니다. Notebooks, Dashboards, Lakeflow Pipelines Editor 등에서 지원됩니다.
{% endhint %}

### 11.3 주요 기능

#### 인라인 코드 제안 및 자동완성

코드를 작성하는 동안 Genie Code가 실시간으로 코드 제안을 제공합니다. Python과 SQL에서 지원됩니다.

#### Quick Fix

기본적인 코드 오류를 자동 감지하고 수정 제안을 표시합니다. **Accept and run**을 클릭하면 즉시 적용됩니다.

#### Diagnose Error

복잡한 오류(환경 오류 포함)를 분석하고 수정을 시도합니다.

#### Slash 명령어

자주 사용하는 프롬프트를 빠르게 입력할 수 있습니다:

| 명령어 | 기능 |
|--------|------|
| `/explain` | 선택한 코드 설명 |
| `/fix` | 코드 오류 수정 |
| `/optimize` | 코드 최적화 |
| `/test` | 단위 테스트 생성 |
| `/doc` | 문서/주석 생성 |

#### 자연어 데이터 필터링

데이터 테이블에서 자연어로 필터 조건을 지정할 수 있습니다.

#### 문서 기반 응답

Databricks 공식 문서를 검색하여 답변합니다. 응답에 **Searched documentation** 단계가 표시되며, 출처 링크를 요청할 수 있습니다.

### 11.4 패널 설정

| 설정 | 설명 |
|------|------|
| **Docked** | 하단에 고정 (드래그 앤 드롭으로 이동 가능) |
| **Side** | 우측에 고정 |
| **History** | 이전 대화 스레드 조회/삭제 |
| **Custom Instructions** | 사용자/워크스페이스 수준 커스텀 인스트럭션 설정 |

### 11.5 피드백

응답 하단에 마우스를 올리면 **Useful/Not useful** 버튼이 표시됩니다. 적극적인 피드백이 서비스 품질 향상에 기여합니다.

---

## 12. Genie Code 활용 시나리오

### 시나리오 1: 데이터 사이언스 (Notebooks)

Genie Code는 전문 ML 엔지니어처럼 동작하여 전체 ML 워크플로를 자동화합니다.

**활용 예시:**

```
프롬프트: "@customers 테이블에 대해 고객 세그멘테이션 분석을 수행해줘.
         K-means 클러스터링을 사용하고 MLflow에 실험을 기록해줘."
```

Genie Code가 수행하는 작업:
1. 테이블 스키마 분석 및 EDA
2. 피처 엔지니어링
3. 최적 클러스터 수 결정 (Elbow method)
4. 모델 학습 및 MLflow 실험 로깅
5. 결과 시각화 및 인사이트 요약

### 시나리오 2: 데이터 엔지니어링 (Lakeflow Pipelines)

ETL 워크로드를 자동화하고 Lakeflow Spark Declarative Pipeline을 구축합니다.

**활용 예시:**

```
프롬프트: "raw_orders와 raw_customers 테이블을 조인하여
         daily_order_summary 테이블을 업데이트하는 파이프라인을 만들어줘."
```

### 시나리오 3: 분석 및 대시보드 (Dashboards)

데이터 자산을 탐색하고 프로덕션 수준 대시보드를 자동 생성합니다.

**활용 예시:**

```
프롬프트: "@sales_data를 분석하고 월별 매출 추이,
         지역별 성과, 상위 제품을 보여주는 대시보드를 만들어줘."
```

### 시나리오 4: GenAI 앱 디버깅 (MLflow)

GenAI 애플리케이션을 이해하고, 디버깅하며, 성능을 개선합니다.

**활용 예시:**

```
프롬프트: "이 RAG 체인의 evaluation 결과를 분석하고
         응답 품질이 낮은 케이스를 식별해줘."
```

---

## 13. Genie Space vs Genie Code 비교

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

## 14. MCP(Model Context Protocol)와 Genie Code 연동

### 14.1 MCP 개요

#### MCP란 무엇인가?

MCP(Model Context Protocol)는 **Anthropic이 개발한 오픈소스 프로토콜**로, AI 에이전트가 외부 도구, 데이터 소스, 워크플로에 접근하기 위한 **표준 인터페이스**입니다. USB-C가 다양한 전자기기를 하나의 규격으로 연결하듯, MCP는 AI 애플리케이션과 외부 시스템을 하나의 표준으로 연결합니다.

#### 핵심 아키텍처

MCP는 **클라이언트-서버 아키텍처**를 따르며, 세 가지 핵심 참여자로 구성됩니다:

| 참여자 | 역할 | Databricks 예시 |
|--------|------|-----------------|
| **MCP Host** | AI 애플리케이션. 하나 이상의 MCP Client를 관리 | Genie Code, AI Playground |
| **MCP Client** | MCP Server와의 연결을 유지하고 컨텍스트를 획득 | Genie Code 내부 클라이언트 |
| **MCP Server** | 도구, 리소스, 프롬프트 등 컨텍스트를 제공하는 프로그램 | GitHub MCP, Unity Catalog Functions 등 |

#### MCP 서버가 제공하는 3가지 프리미티브

| 프리미티브 | 설명 | 예시 |
|-----------|------|------|
| **Tools** | AI가 호출할 수 있는 실행 가능한 함수 | 파일 검색, API 호출, DB 쿼리 |
| **Resources** | AI에 컨텍스트를 제공하는 데이터 소스 | 파일 내용, DB 레코드, API 응답 |
| **Prompts** | LLM과의 상호작용을 구조화하는 재사용 가능한 템플릿 | 시스템 프롬프트, Few-shot 예시 |

#### MCP 통신 방식

MCP는 **JSON-RPC 2.0** 기반의 데이터 계층과 두 가지 전송 메커니즘을 지원합니다:

| 전송 방식 | 설명 | 사용 환경 |
|----------|------|----------|
| **Stdio** | 표준 입출력 스트림을 통한 로컬 프로세스 통신 | 로컬 개발 환경 |
| **Streamable HTTP** | HTTP POST + Server-Sent Events | 원격 서버 통신 (Databricks 기본) |

{% hint style="info" %}
Databricks에서 외부 MCP 서버를 연결하려면 해당 서버가 **Streamable HTTP 전송 방식**을 지원해야 합니다.
{% endhint %}

---

### 14.2 Databricks에서 MCP 서버 설정

Databricks는 세 가지 유형의 MCP 서버를 지원합니다:

#### 유형 1: Managed MCP (관리형)

Databricks가 사전 구성한 즉시 사용 가능한 MCP 서버입니다. Unity Catalog 권한이 자동으로 적용됩니다.

| 서버 | 용도 | 엔드포인트 패턴 |
|------|------|----------------|
| **Unity Catalog Functions** | 사전 정의된 SQL 함수 실행 | `/api/2.0/mcp/functions/{catalog}/{schema}/{function}` |
| **Vector Search** | 벡터 검색 인덱스 쿼리 | `/api/2.0/mcp/vector-search/{catalog}/{schema}/{index}` |
| **Genie Space** | 자연어 데이터 분석 (읽기 전용) | `/api/2.0/mcp/genie/{genie_space_id}` |
| **Databricks SQL** | AI 생성 SQL 실행 (읽기/쓰기) | `/api/2.0/mcp/sql` |

#### 유형 2: External MCP (외부)

Unity Catalog Connection을 통해 외부 MCP 서버에 안전하게 연결합니다. 자격 증명이 직접 노출되지 않으며, 관리형 프록시를 통해 통신합니다.

**지원되는 연결 방법:**

| 방법 | 설명 |
|------|------|
| **Managed OAuth (권장)** | Databricks가 OAuth 흐름을 관리. GitHub, Glean, Google Drive, SharePoint 등 지원 |
| **Databricks Marketplace** | 마켓플레이스에서 사전 빌드된 통합 설치 |
| **Custom HTTP Connection** | Streamable HTTP를 지원하는 모든 MCP 서버에 커스텀 연결 생성 |
| **Dynamic Client Registration (실험적)** | RFC7591 지원 서버의 자동 OAuth 등록 |

외부 MCP 서버의 프록시 엔드포인트 형식:

```
https://<workspace-hostname>/api/2.0/mcp/external/{connection_name}
```

**인증 방식:**

* **공유 인증(Shared Principal)**: Bearer 토큰, OAuth M2M, 공유 OAuth U2M
* **사용자별 인증(Per-user)**: 리소스별 개별 사용자 자격 증명

#### 유형 3: Custom MCP (커스텀)

자체 MCP 서버를 **Databricks App**으로 호스팅합니다. Streamable HTTP 전송 방식을 구현해야 합니다.

**배포 절차:**

1. MCP 서버 코드 작성 (`pyproject.toml`, `app.yaml` 구성)
2. Databricks App 생성: `databricks apps create <app-name>`
3. 소스 코드 업로드 및 배포
4. MCP 엔드포인트: `https://<app-url>/mcp`

{% hint style="warning" %}
커스텀 MCP 앱은 **stateless 아키텍처**로 구현해야 하며, 동일 워크스페이스 내에 배포해야 합니다. CORS 이슈 방지를 위해 워크스페이스 URL을 허용 오리진에 추가하세요.
{% endhint %}

#### MCP 서버 확인 방법

워크스페이스에서 사용 가능한 MCP 서버를 확인하려면:

1. 워크스페이스의 **Agents** 섹션으로 이동합니다.
2. **MCP Servers** 탭을 선택합니다.
3. 등록된 서버 목록과 상태를 확인할 수 있습니다.

---

### 14.3 Genie Code에서 MCP 활용

#### MCP 서버를 Genie Code에 연결하기

{% hint style="warning" %}
MCP 서버는 **Genie Code Agent 모드에서만** 지원됩니다. Chat 모드에서는 사용할 수 없습니다.
{% endhint %}

**설정 단계:**

1. Genie Code 패널을 열고 **설정 아이콘**을 클릭합니다.
2. **MCP Servers** 섹션에서 **Add Server**를 선택합니다.
3. 사용할 서버 유형을 선택합니다:
   * Unity Catalog Functions
   * Vector Search Indexes
   * Genie Spaces
   * Unity Catalog Connections (외부 MCP)
   * Databricks Apps (커스텀 MCP)
4. **Save**를 클릭하면 즉시 사용 가능합니다.

#### 사용 방식

MCP 서버가 추가되면, Genie Code는 **자동으로** 관련 서버의 도구를 활용합니다. 프롬프트나 인스트럭션을 변경할 필요가 없습니다. Agent 모드에서 질문을 하면 Genie Code가 필요에 따라 적절한 MCP 서버의 도구를 호출합니다.

#### 활용 예시: GitHub MCP 서버

GitHub MCP 서버를 연결하면 Genie Code에서 엔터프라이즈 코드 검색이 가능합니다.

**설정 순서:**

1. **GitHub App 생성**: GitHub > Settings > Developer settings에서 앱 생성
   * Callback URL: `https://<databricks-workspace-url>/login/oauth/http.html`
2. **Unity Catalog Connection 생성**:
   * Auth type: OAuth User to Machine
   * Host: `https://api.githubcopilot.com`
   * OAuth scope: `mcp:access read:user user:email repo read:org`
   * Base path: `/mcp`
   * "Is mcp connection" 체크박스 활성화
3. **Genie Code에서 연결 추가**: Settings > MCP Servers > Add Server

**사용 가능한 도구:**

| 도구 | 기능 |
|------|------|
| `search_code` | 리포지토리에서 코드 패턴 검색 |
| `get_file_contents` | 리포지토리의 파일 내용 조회 |

**사용 예시:**

```
프롬프트: "우리 리포지토리에서 데이터 처리 파이프라인 관련 코드를 찾아줘"
프롬프트: "main 브랜치의 config.yaml 파일 내용을 보여줘"
```

{% hint style="tip" %}
특정 리포지토리를 대상으로 검색하려면 Genie Code 인스트럭션 파일에 `repo: repository_name, owner: username` 형식으로 지정할 수 있습니다.
{% endhint %}

#### 활용 예시: 기타 외부 서비스

| 서비스 | 활용 시나리오 |
|--------|-------------|
| **Glean** | 내부 문서 검색, 사전 사례 참조 |
| **Google Drive** | 팀 문서에서 필요한 정보 추출 |
| **SharePoint** | 조직 내부 문서 및 데이터 접근 |
| **Genie Space** | 자연어로 데이터 분석 (Agent 모드에서 MCP를 통해 호출) |
| **Vector Search** | RAG 패턴으로 관련 문서 검색 후 분석에 활용 |

#### 제한 사항

| 제한 | 상세 |
|------|------|
| **Agent 모드 전용** | MCP 서버는 Agent 모드에서만 사용 가능 |
| **도구 수 제한** | 전체 MCP 서버에 걸쳐 **최대 20개 도구**만 사용 가능 |
| **전송 방식** | 외부 MCP 서버는 Streamable HTTP만 지원 |
| **도구 이름 하드코딩 금지** | 도구 목록이 변경될 수 있으므로 동적 탐색 권장 |
| **출력 형식 비보장** | 도구 출력 형식이 안정적이지 않으므로 프로그래밍적 파싱 비권장 |

{% hint style="info" %}
MCP 서버가 제공하는 도구가 20개를 초과하는 경우, Genie Code 설정에서 특정 도구나 서버를 선택적으로 활성화/비활성화하여 20개 한도 내에서 관리할 수 있습니다.
{% endhint %}

---

### 14.4 MCP 비용 구조

MCP 서버 사용 시 각 리소스 유형에 따라 컴퓨팅 비용이 발생합니다:

| 리소스 | 비용 유형 |
|--------|----------|
| Unity Catalog Functions | Serverless General Compute |
| Genie Spaces | Serverless SQL Compute |
| Databricks SQL | SQL 전용 가격 |
| Vector Search Indexes | Vector Search 가격 |
| Custom MCP Servers | Databricks Apps 가격 |

{% hint style="info" %}
MCP 프로토콜 자체에 대한 추가 비용은 없습니다. 실제 도구를 실행할 때 사용되는 컴퓨팅 리소스에 대해서만 비용이 부과됩니다.
{% endhint %}

---

### 14.5 MCP 에이전트 개발 베스트 프랙티스

MCP를 활용한 에이전트를 개발할 때 다음 권장 사항을 따르세요:

1. **도구 이름 하드코딩 금지**: MCP 서버의 도구 목록은 변경될 수 있으므로, 에이전트가 런타임에 `tools/list`를 호출하여 **동적으로 도구를 탐색**하도록 구현합니다.
2. **출력 파싱 금지**: 도구 출력 형식은 안정적이지 않으므로, 결과 해석은 **LLM에 위임**합니다.
3. **LLM 기반 도구 선택**: 어떤 도구를 호출할지는 LLM이 사용자 요청에 따라 자동으로 결정하도록 합니다.

**프로그래밍 방식으로 MCP 서버 연결하기 (로컬 개발):**

```bash
# 1. OAuth 인증
databricks auth login --host https://<workspace-hostname>

# 2. 의존성 설치
pip install -U "mcp>=1.9" "databricks-sdk[openai]" "mlflow>=3.1.0" \
    "databricks-agents>=1.0.0" "databricks-mcp"
```

```python
# 3. DatabricksMCPClient를 사용한 연결
from databricks_mcp import DatabricksMCPClient

client = DatabricksMCPClient(
    server_url="https://<hostname>/api/2.0/mcp/functions/{catalog}/{schema}/{func}",
    databricks_cli_profile="DEFAULT"
)
```

---

## 참고 자료

* [Databricks Genie Space 공식 문서](https://docs.databricks.com/aws/en/genie/)
* [Genie Space 설정 가이드](https://docs.databricks.com/aws/en/genie/set-up)
* [Genie Space 베스트 프랙티스](https://docs.databricks.com/aws/en/genie/best-practices)
* [Genie Code 공식 문서](https://docs.databricks.com/aws/en/genie-code/)
* [Genie Code 사용법 (Azure)](https://learn.microsoft.com/en-us/azure/databricks/genie-code/use-genie-code)
* [Genie Agent Mode](https://docs.databricks.com/aws/en/genie/agent-mode)
* [MCP on Databricks 공식 문서](https://docs.databricks.com/aws/en/generative-ai/mcp/)
* [Genie Code MCP 연결 가이드](https://docs.databricks.com/aws/en/genie-code/mcp)
* [Databricks Managed MCP 서버](https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp)
* [외부 MCP 서버 연결](https://docs.databricks.com/aws/en/generative-ai/mcp/external-mcp)
* [커스텀 MCP 서버 호스팅](https://docs.databricks.com/aws/en/generative-ai/mcp/custom-mcp)
* [GitHub MCP 서버 연동](https://docs.databricks.com/aws/en/genie-code/github-mcp)
* [MCP 공식 사이트](https://modelcontextprotocol.io/introduction)
