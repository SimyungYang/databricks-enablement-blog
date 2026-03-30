# Genie Spaces 연동

---

## 개요

Genie Spaces는 Unity Catalog에 등록된 **테이블 데이터를 자연어 챗봇**으로 변환합니다. 비즈니스 사용자가 SQL 없이도 데이터에 질문할 수 있으며, 내부적으로 자연어를 SQL로 변환하여 실행합니다.

**적합한 유스케이스:**
- 비즈니스 데이터 탐색
- 셀프 서비스 분석
- KPI/메트릭 확인

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

---

## 사전 요구사항

| 요구사항 | 설명 |
|----------|------|
| **SQL Warehouse** | Pro 또는 Serverless SQL Warehouse |
| **Unity Catalog** | 데이터가 UC에 등록되어 있어야 함 |
| **테이블 제한** | 공간당 최대 30개 테이블/뷰 |
| **처리량** | UI: 20 질문/분, API: 5 질문/분 (무료 티어) |
| **용량** | 공간당 10,000 대화, 대화당 10,000 메시지 |

**필요 권한:**
- Databricks SQL 워크스페이스 자격
- SQL Warehouse에 대한 `CAN USE` 접근
- 데이터 객체에 대한 `SELECT` 권한

---

## 생성 및 설정

### Step 1: Genie Space 생성

1. 좌측 메뉴에서 **Genie** > **New** 클릭
2. Unity Catalog에서 데이터 소스 (테이블/뷰) 선택
3. **Create** 클릭

### Step 2: Knowledge Store 설정

생성 후 반드시 Knowledge Store를 설정하세요. 이것이 Genie의 정확도를 결정합니다.

| 설정 항목 | 설명 |
|-----------|------|
| **테이블/컬럼 설명** | 비즈니스 용어, 동의어 정의 |
| **JOIN 관계** | 테이블 간 연결 정의 (복합 SQL 표현식 지원) |
| **재사용 가능 SQL 표현식** | 측정값, 필터, KPI용 표현식 |
| **프롬프트 매칭** | 형식 지원, 엔터티 교정 |

### Step 3: Instructions & Examples 추가 (최대 100개)

- 정적 또는 파라미터화된 SQL 쿼리 (자연어 제목 포함)
- Unity Catalog 함수 (복잡한 로직용)
- 텍스트 지시사항 (비즈니스 컨텍스트, 형식 규칙)

### Step 4: 공간 설정

- 제목, 설명 (마크다운 지원)
- 기본 SQL Warehouse 설정
- 사용자 안내용 샘플 질문 등록
- 태그 분류

---

## 모니터링 및 개선

**Monitoring** 탭에서 다음을 확인할 수 있습니다:
- 사용자가 질문한 모든 내용
- 사용자 피드백 (좋아요/싫어요)
- 플래그된 응답

이를 바탕으로 Knowledge Store와 Instructions를 반복적으로 개선합니다.

---

## Agent Bricks에서의 활용

Genie Spaces는 **Supervisor Agent의 서브 에이전트**로 사용됩니다. Genie API를 통해 프로그래밍 방식으로 접근할 수 있으며, 멀티 에이전트 시스템에서 데이터 탐색을 담당합니다.
