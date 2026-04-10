# 설정 & 모범사례

> **최종 업데이트**: 2026-04-08

---

Genie Code를 처음 열면 프롬프트 입력만 보이지만, 설정을 제대로 구성하면 **동일한 프롬프트에서도 완전히 다른 수준의 결과** 를 얻을 수 있습니다. 이 가이드는 Genie Code의 모든 설정 항목을 체계적으로 설명하고, 역할별 최적 구성과 실전 운영 모범사례를 다룹니다.

---

## 1. 설정 화면 구성 요소

Genie Code 패널 상단의 **톱니바퀴(Settings)** 아이콘을 클릭하면 다섯 가지 설정 영역이 나타납니다. 각 영역이 Genie Code의 동작에 미치는 영향을 이해하는 것이 효과적 활용의 출발점입니다.

| 설정 항목 | 역할 | 영향 범위 | 누가 설정하는가 |
|-----------|------|-----------|----------------|
| **MCP 서버** | 외부 도구 연동 (Slack, JIRA, GitHub 등) | 해당 사용자의 Agent 모드 세션 | 개인 사용자 |
| **패널 뷰** | Docked(하단 고정) / Side(우측 패널) 전환 | UI 레이아웃만 변경 | 개인 사용자 |
| **User Instructions** | 개인용 지속적 지침 — 모든 대화에 자동 적용 | 해당 사용자의 모든 Genie Code 세션 | 개인 사용자 |
| **Workspace Instructions** | 조직 전체 지침 — 모든 사용자에게 적용 | 워크스페이스 전체 | 워크스페이스 관리자 |
| **Skills** | 재사용 가능한 작업 템플릿 (Agent 모드 전용) | User 스킬은 개인, Workspace 스킬은 전체 | 개인 또는 관리자 |

이 다섯 가지 중 **User Instructions, Workspace Instructions, Skills** 가 Genie Code의 응답 품질에 직접적인 영향을 미칩니다. MCP 서버는 Agent 모드의 활용 범위를 결정하고, 패널 뷰는 순수하게 UI 편의 설정입니다.

{% hint style="info" %}
Genie Code는 응답 생성 시 **Workspace Instructions를 User Instructions보다 우선** 적용합니다. 두 지침이 충돌하면 Workspace Instructions가 이깁니다. 이는 조직의 보안 정책이 개인 선호보다 항상 우선하도록 설계된 것입니다.
{% endhint %}

---

## 2. User Instructions 작성법

### 2.1 User Instructions란?

User Instructions는 Genie Code에게 **"나는 이런 사람이고, 이렇게 일해줬으면 좋겠어"** 라고 지속적으로 알려주는 개인화 지침입니다. 한 번 설정하면 새 대화를 열 때마다 자동으로 적용되므로, 매번 같은 요구사항을 반복할 필요가 없어집니다.

### 2.2 생성 방법

User Instructions를 설정하는 두 가지 방법이 있습니다.

**방법 1: UI에서 직접 설정**

1. Genie Code 패널 상단의 **톱니바퀴(Settings)** 아이콘 클릭
2. **User instructions** 섹션 찾기
3. **"지침 파일 추가(Add instruction file)"** 클릭
4. 마크다운 에디터에 지침 작성 후 저장

**방법 2: 파일 직접 생성**

사용자 디렉토리에 `.assistant_instructions.md` 파일을 생성합니다:

```
/Workspace/Users/{your-email}/.assistant_instructions.md
```

{% hint style="warning" %}
User Instructions의 최대 길이는 **20,000자** 입니다. 이 안에서 가장 중요한 지침을 상위에 배치하세요. LLM은 지침의 앞부분에 더 높은 가중치를 부여하는 경향이 있습니다.
{% endhint %}

### 2.3 효과적인 User Instructions 구조

좋은 User Instructions는 **구조화된 마크다운** 으로 작성됩니다. 헤딩(`##`)으로 카테고리를 나누고, 불릿(`-`)으로 구체적 규칙을 나열하면 Genie Code가 각 규칙을 명확하게 구분하여 적용합니다.

### 2.4 좋은 User Instructions 예시

다음은 데이터 엔지니어를 위한 실전 User Instructions 예시입니다:

```markdown
## 내 역할과 컨텍스트
- 나는 데이터 엔지니어이며, 주로 Delta Lake 파이프라인과 SQL 분석 작업을 합니다
- 우리 팀의 프로덕션 카탈로그는 `main_catalog`이고, 개발용은 `dev_catalog`입니다
- 사용하는 클라우드: AWS (S3, Glue, Redshift 연동)

## 코딩 스타일
- Python 코드는 PEP 8을 따르세요
- SQL은 대문자 키워드를 사용하세요 (SELECT, FROM, WHERE)
- 변수명은 snake_case를 사용하세요
- 함수에는 반드시 docstring을 포함하세요
- 타입 힌트를 사용하세요 (Python 3.10+ 스타일)

## 선호 라이브러리 & 프레임워크
- 데이터 처리: PySpark (pandas 대신)
- 시각화: Plotly (matplotlib 대신)
- ML: MLflow + scikit-learn
- 테스트: pytest + Great Expectations

## 보안 규칙 (절대 위반 금지)
- 프로덕션 테이블(main_catalog.prod.*)은 절대 수정하지 마세요
- DROP TABLE, DELETE, UPDATE 문은 생성하지 마세요
- 임시 결과는 dev_catalog.sandbox.simyung 스키마에 저장하세요
- 민감 컬럼(ssn, email, phone)은 마스킹 처리하세요
- 자격 증명(password, token, key)을 코드에 하드코딩하지 마세요

## 응답 스타일
- 코드 블록 앞에 간단한 설명을 붙여주세요
- 복잡한 쿼리에는 인라인 주석을 추가하세요
- 한국어로 응답하세요
```

이 예시가 효과적인 이유는 다음과 같습니다:

1. **역할과 도메인을 명시** 해서 Genie Code가 적절한 수준과 맥락으로 응답합니다
2. **구체적 카탈로그/스키마 이름을 포함** 해서 생성되는 코드가 실제 환경에 맞습니다
3. **금지 사항을 명확히 구분** 해서 위험한 작업을 사전에 차단합니다
4. **선호 라이브러리를 지정** 해서 일관된 기술 스택으로 코드를 생성합니다

### 2.5 나쁜 User Instructions와 개선 방향

다음은 흔히 저지르는 실수와 왜 비효과적인지를 보여줍니다.

**나쁜 예시 1: 너무 모호한 지침**

```markdown
좋은 코드를 작성해주세요.
버그 없이 짜주세요.
빠른 코드를 만들어주세요.
```

"좋은", "빠른" 같은 추상적 형용사는 LLM에게 구체적 행동 변화를 유도하지 못합니다. **무엇이 "좋은" 것인지 구체적으로 정의** 해야 합니다.

**나쁜 예시 2: 상충되는 지침**

```markdown
- 코드를 최대한 간결하게 작성하세요
- 모든 에러 케이스를 처리하세요
- 모든 함수에 상세한 docstring을 추가하세요
- 한 줄이라도 줄여주세요
```

간결함과 상세한 에러 처리/문서화는 본질적으로 상충합니다. 우선순위를 정하거나 상황별로 구분해야 합니다.

**나쁜 예시 3: 역할과 무관한 과잉 지침**

```markdown
## JavaScript 규칙
- React 18을 사용하세요
- TypeScript strict 모드를 적용하세요

## CSS 규칙
- Tailwind CSS를 사용하세요
- BEM 네이밍을 따르세요

## DevOps 규칙
- Docker multi-stage build를 사용하세요
```

Genie Code는 **Databricks 환경의 데이터 작업** 에 특화되어 있습니다. JavaScript, CSS, DevOps 관련 지침은 의미가 없을 뿐 아니라, 20,000자 제한 내에서 실제로 필요한 지침의 자리를 차지합니다.

{% hint style="tip" %}
User Instructions는 **자주 반복하게 되는 지침** 만 포함하세요. 일회성 요구사항은 프롬프트에서 직접 지시하는 것이 더 효과적입니다. 지침이 너무 많으면 오히려 핵심 규칙이 희석됩니다.
{% endhint %}

---

## 3. Workspace Instructions 설정

### 3.1 왜 Workspace Instructions가 필요한가?

User Instructions는 개인 선호이므로 사람마다 다릅니다. 하지만 조직에는 **모든 사람이 반드시 따라야 하는 규칙** 이 있습니다. 보안 정책, 네이밍 컨벤션, 데이터 접근 규칙 등이 그것입니다. Workspace Instructions는 이러한 조직 수준의 규칙을 한 곳에서 관리하고, 모든 사용자의 Genie Code 세션에 **자동으로 강제 적용** 합니다.

User Instructions가 "나는 이렇게 해줘"라면, Workspace Instructions는 **"우리 조직에서는 반드시 이렇게 해야 해"** 입니다.

### 3.2 생성 방법

워크스페이스 관리자가 다음 경로에 파일을 생성합니다:

```
/Workspace/.assistant_workspace_instructions.md
```

{% hint style="warning" %}
Workspace Instructions는 **워크스페이스 관리자만 생성하고 수정** 할 수 있습니다. 일반 사용자는 이 파일을 읽을 수 있지만 변경할 수 없습니다. 이는 보안 정책이 개인에 의해 우회되는 것을 방지하기 위한 설계입니다.
{% endhint %}

### 3.3 효과적인 Workspace Instructions 예시

다음은 데이터 팀을 위한 실전 Workspace Instructions입니다:

```markdown
## 조직 코딩 표준
- 모든 테이블 참조는 Unity Catalog 3-level 네이밍을 사용하세요 (catalog.schema.table)
- 2-level 네이밍(schema.table)이나 1-level 네이밍(table)은 사용하지 마세요
- 파이프라인 코드에는 반드시 try-except 에러 핸들링을 포함하세요
- 로깅은 Python logging 모듈을 사용하고, print()로 디버깅하지 마세요

## 데이터 레이어 네이밍 컨벤션
- Bronze 테이블: raw_{소스시스템}_{엔티티} (예: raw_sap_orders)
- Silver 테이블: clean_{도메인}_{엔티티} (예: clean_sales_orders)
- Gold 테이블: agg_{비즈니스영역}_{메트릭} (예: agg_revenue_daily)
- 임시 테이블: tmp_{작성자}_{목적} (예: tmp_simyung_test_join)

## 데이터 접근 정책
- PII 테이블 목록: hr.employees, crm.contacts, crm.customers
- 위 테이블 접근 시 반드시 마스킹 함수 적용: mask_pii(column_name)
- 프로덕션 카탈로그(prod_catalog)에 대해 DDL/DML 문 생성 금지
- 개발 작업은 반드시 dev_catalog 내에서 수행

## SQL 스타일 가이드
- 키워드는 대문자: SELECT, FROM, WHERE, JOIN, GROUP BY
- 테이블 alias는 의미 있는 약어 사용 (o for orders, c for customers)
- 서브쿼리 대신 CTE(WITH 절)를 우선 사용
- 쿼리에는 반드시 LIMIT 절을 포함 (개발 단계에서는 기본 1000)

## 보안 필수 규칙
- 자격 증명, 비밀번호, API 키를 코드에 절대 포함하지 마세요
- Databricks Secrets를 사용하세요: dbutils.secrets.get(scope, key)
- 외부 API 호출 시 반드시 타임아웃을 설정하세요 (기본 30초)
```

이 Workspace Instructions가 효과적인 이유는 조직의 핵심 규칙을 **구조화된 카테고리** 로 분류하고, 각 규칙에 **구체적 예시** 를 포함하여 해석의 모호함을 제거했기 때문입니다. 특히 네이밍 컨벤션에 실제 패턴과 예시를 함께 제공하면, Genie Code가 새 테이블이나 파이프라인을 생성할 때 자동으로 이 패턴을 따릅니다.

### 3.4 User Instructions와 Workspace Instructions의 역할 분리

두 지침의 목적이 다르므로, 내용도 명확히 구분해야 합니다.

| 구분 | User Instructions에 적합 | Workspace Instructions에 적합 |
|------|------------------------|------------------------------|
| **코딩 스타일** | 개인 선호 (들여쓰기 스타일, 주석 언어) | 조직 표준 (네이밍 컨벤션, 필수 에러 처리) |
| **라이브러리** | 선호 라이브러리 (Plotly vs matplotlib) | 금지 라이브러리 (보안 취약 패키지) |
| **데이터 접근** | 자주 쓰는 스키마/테이블 | PII 정책, 프로덕션 접근 제한 |
| **응답 형식** | 언어 선호, 상세도 | 로깅/문서화 의무 사항 |
| **보안** | 개인 sandbox 스키마 | 조직 전체 보안 규칙 |

개인 선호와 조직 규칙이 같은 곳에 섞이면 관리가 어렵고, 규칙 충돌 시 어떤 것이 우선인지 혼란이 생깁니다. **조직이 강제해야 할 규칙은 Workspace Instructions에, 개인이 선택할 수 있는 선호는 User Instructions에** 분리하는 것이 원칙입니다.

---

## 4. Skills 생성 및 활용

### 4.1 Skills란?

Skills는 **재사용 가능한 작업 템플릿** 입니다. User Instructions가 "이렇게 해줘"라는 **규칙** 이라면, Skills는 "이 작업을 할 때는 이 절차를 따라라"라는 **레시피** 입니다. Agent 모드에서만 동작하며, Genie Code가 사용자의 요청을 분석하여 관련 스킬을 자동으로 로드하거나, 사용자가 `@스킬명` 으로 직접 호출할 수 있습니다.

Skills가 필요한 상황의 핵심 판단 기준은 다음과 같습니다: **같은 유형의 작업을 여러 번 반복하면서 매번 동일한 절차와 규칙을 프롬프트에 작성하고 있다면, 그것은 스킬로 만들어야 합니다.**

### 4.2 폴더 구조

Skills는 정해진 디렉토리 구조를 따릅니다:

**Workspace 스킬** (모든 사용자 공유):

```
/Workspace/.assistant/skills/{skill-name}/
├── SKILL.md           # 스킬 정의 (필수)
├── template.py        # 관련 스크립트 (선택)
└── examples/          # 참고 파일 (선택)
    └── sample.sql
```

**User 스킬** (개인 전용):

```
/Workspace/Users/{email}/.assistant/skills/{skill-name}/
├── SKILL.md           # 스킬 정의 (필수)
└── ...
```

### 4.3 SKILL.md 작성법

모든 스킬은 `SKILL.md` 파일로 정의됩니다. YAML frontmatter에 메타데이터를 넣고, 본문에 상세 지침을 작성합니다:

```markdown
---
name: data-quality-check
description: 테이블의 데이터 품질을 검증하고 리포트를 생성합니다
---

# 데이터 품질 검증 스킬

## 이 스킬을 사용하는 경우
- 사용자가 테이블의 데이터 품질을 확인하고 싶을 때
- 새로운 데이터 소스를 수집한 후 품질 검증이 필요할 때
- 정기적인 데이터 품질 리포트를 생성할 때

## 실행 절차

### 1단계: 테이블 프로파일링
대상 테이블에 대해 다음 항목을 분석하세요:
- 전체 행 수, 컬럼 수
- 각 컬럼의 null 비율
- 각 컬럼의 고유값(distinct) 수
- 숫자 컬럼의 min/max/mean/std
- 문자 컬럼의 최소/최대 길이

### 2단계: 품질 규칙 점검
다음 규칙을 점검하고 위반 건수를 집계하세요:
- PK 컬럼의 중복 여부
- NOT NULL이어야 하는 컬럼의 null 존재 여부
- 날짜 컬럼이 합리적 범위 내인지 (미래 날짜 없음)
- 숫자 컬럼이 비정상 범위가 아닌지 (음수 매출 등)

### 3단계: 리포트 생성
분석 결과를 다음 형식으로 정리하세요:
- 요약: 전체 점수 (통과율 %)
- 상세: 각 규칙별 통과/실패 건수
- 권장 조치: 실패한 항목에 대한 조치 방안
```

### 4.4 실전 스킬 예시

#### 예시 1: 파이프라인 템플릿 생성 스킬

```markdown
---
name: pipeline-template
description: Bronze/Silver/Gold 레이어별 DLT 파이프라인 코드를 생성합니다
---

# 파이프라인 템플릿 생성

## 이 스킬을 사용하는 경우
- 새로운 데이터 소스를 위한 파이프라인을 구축할 때
- 기존 배치 파이프라인을 DLT로 마이그레이션할 때

## 필수 입력
사용자에게 다음 정보를 확인하세요:
1. 소스 시스템 (S3, JDBC, Kafka 등)
2. 대상 카탈로그와 스키마
3. 증분 처리 여부 (전체 로드 vs CDC)
4. 스케줄 주기

## 생성 규칙
- Bronze: 소스를 있는 그대로 수집. 컬럼 추가: _ingested_at, _source_file
- Silver: 타입 캐스팅, null 처리, 중복 제거. 컬럼 추가: _processed_at
- Gold: 비즈니스 로직 적용, 집계 테이블 생성
- 모든 테이블은 DLT @dlt.table() 데코레이터 사용
- Expectations 정의 포함 (null 검사, 범위 검사)
- 네이밍: Workspace Instructions의 컨벤션을 반드시 따를 것
```

#### 예시 2: 대시보드 생성 스킬

```markdown
---
name: dashboard-builder
description: 분석 결과를 AI/BI 대시보드로 구성합니다
---

# 대시보드 생성

## 이 스킬을 사용하는 경우
- 분석 결과를 시각화하여 공유할 때
- 정기 리포트용 대시보드를 만들 때

## 실행 절차

### 1단계: 데이터 확인
- 대시보드에 표시할 테이블/뷰의 스키마를 확인하세요
- 시간 축이 될 날짜 컬럼을 식별하세요
- 주요 차원(dimension)과 측정값(measure)을 구분하세요

### 2단계: 시각화 구성
다음 순서로 위젯을 구성하세요:
1. 상단: KPI 카드 (핵심 지표 3~5개)
2. 중단: 트렌드 차트 (시계열 라인/바 차트)
3. 하단: 상세 테이블 (드릴다운용)

### 3단계: SQL 쿼리 작성 규칙
- 각 위젯별 독립 SQL 쿼리 작성
- 파라미터 위젯으로 날짜 범위 필터 추가
- 쿼리에 반드시 주석으로 위젯 목적 설명 포함

### 4단계: 발행
- Databricks AI/BI 대시보드 형식으로 생성
- 권한 설정: 팀 그룹에 VIEW 권한 부여
```

#### 예시 3: 데이터 품질 모니터링 스킬

```markdown
---
name: quality-monitor
description: Unity Catalog 모니터를 설정하고 알림 규칙을 구성합니다
---

# 데이터 품질 모니터링 설정

## 이 스킬을 사용하는 경우
- 프로덕션 테이블에 지속적 품질 모니터링을 설정할 때
- 데이터 드리프트 감지가 필요할 때

## 실행 절차

### 1단계: 모니터 대상 분석
- 대상 테이블의 스키마와 데이터 특성 파악
- 시간 기준 컬럼(timestamp column) 식별
- 모니터링할 핵심 컬럼 선정

### 2단계: Lakehouse Monitor 생성
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

# 스냅샷 모니터 또는 시계열 모니터 생성
monitor = w.quality_monitors.create(
    table_name="catalog.schema.table",
    assets_dir="/Workspace/Users/{email}/monitors",
    output_schema_name="catalog.monitoring",
    schedule={"quartz_cron_expression": "0 0 8 * * ?"}  # 매일 08시
)
```

### 3단계: 커스텀 메트릭 추가
- 비즈니스 규칙에 맞는 커스텀 메트릭 정의
- 예: null 비율, 범위 이탈 비율, 고유값 변화율

### 4단계: 알림 규칙 설정
- 임계값 위반 시 Slack/이메일 알림 구성
- 심각도별 분류: WARNING (>5% 이탈), CRITICAL (>20% 이탈)
```

### 4.5 Workspace 스킬 vs User 스킬 선택 기준

스킬을 어디에 배치할지는 **누가 사용하는가** 와 **표준화가 필요한가** 로 결정합니다.

| 판단 기준 | Workspace 스킬 | User 스킬 |
|-----------|---------------|-----------|
| **사용 범위** | 팀 전체가 동일한 절차를 따라야 할 때 | 개인 업무에 특화된 반복 작업 |
| **표준화 필요성** | 파이프라인 템플릿, 배포 절차 등 일관성이 중요한 작업 | 개인 분석 패턴, 실험 워크플로 |
| **관리 권한** | 관리자가 버전 관리하며 업데이트 | 개인이 자유롭게 수정 |
| **예시** | 데이터 품질 검증, DLT 파이프라인 생성, 대시보드 표준 | 개인 리포트 자동화, 실험 결과 정리 |

{% hint style="tip" %}
처음에는 User 스킬로 만들어서 개인적으로 검증한 뒤, 팀에 유용하다고 판단되면 Workspace 스킬로 승격시키는 것이 안전한 접근법입니다. Workspace 스킬은 모든 사용자에게 영향을 미치므로, 충분히 검증된 절차만 올려야 합니다.
{% endhint %}

---

## 5. MCP 서버 연동

### 5.1 MCP 서버 추가 방법

MCP 서버는 Genie Code가 외부 도구를 호출할 수 있게 해주는 연결 통로입니다. Agent 모드에서만 동작합니다.

**설정 경로:**

1. Genie Code 패널 > **Settings** > **MCP servers**
2. **"Add MCP server"** 클릭
3. MCP 서버 이름, URL, 인증 정보 입력
4. 연결 테스트 후 저장

{% hint style="info" %}
MCP 서버 연동의 상세 설정 방법과 아키텍처는 [MCP 연동](mcp.md) 페이지에서 자세히 다룹니다. 이 섹션에서는 **어떤 서버를 어떻게 조합하면 효과적인지** 에 집중합니다.
{% endhint %}

### 5.2 유용한 MCP 서버 조합

단일 MCP 서버도 유용하지만, 여러 서버를 **조합** 하면 워크플로 자동화의 진정한 가치가 드러납니다. 다음은 역할별로 검증된 조합입니다.

**데이터 엔지니어 추천 조합:**

| MCP 서버 | 활용 시나리오 |
|----------|-------------|
| **Databricks MCP** | Unity Catalog 탐색, SQL 실행, 파이프라인 관리 |
| **GitHub MCP** | 파이프라인 코드 검색, PR 생성, 코드 리뷰 |
| **Slack MCP** | 파이프라인 실패 알림, 팀 채널에 결과 공유 |

이 조합으로 가능한 워크플로 예시: "파이프라인 실패 원인을 분석하고, 수정 코드를 GitHub PR로 올리고, #data-eng 채널에 요약을 공유해줘"

**데이터 분석가 추천 조합:**

| MCP 서버 | 활용 시나리오 |
|----------|-------------|
| **Databricks MCP** | 테이블 탐색, 쿼리 실행, 대시보드 생성 |
| **Slack MCP** | 분석 결과를 팀/경영진 채널에 공유 |
| **JIRA MCP** | 분석 요청 티켓 관리, 완료 보고 |

**ML 엔지니어 추천 조합:**

| MCP 서버 | 활용 시나리오 |
|----------|-------------|
| **Databricks MCP** | 실험 관리, 모델 레지스트리, 서빙 엔드포인트 |
| **GitHub MCP** | 학습 코드 버전 관리, 모델 배포 파이프라인 |
| **Slack MCP** | 학습 완료 알림, 모델 성능 리포트 공유 |

---

## 6. Agent 모드 실전 팁

Agent 모드에서 Genie Code는 단순한 코드 생성기에서 **자율적으로 계획하고, 실행하고, 검증하는 AI 에이전트** 로 변환됩니다. 이 자율성은 강력하지만, 제대로 다루지 않으면 의도하지 않은 결과를 초래할 수 있습니다.

### 6.1 컨텍스트 격리 전략

Genie Code의 대화 세션은 **컨텍스트 윈도우** 를 공유합니다. 하나의 세션에서 여러 작업을 처리하면 이전 작업의 맥락이 새 작업에 영향을 줍니다.

**원칙: 하나의 세션 = 하나의 작업 단위**

| 상황 | 권장 행동 |
|------|----------|
| 새로운 데이터셋을 분석할 때 | 새 채팅 세션 시작 |
| 이전 분석과 관련 없는 코드를 작성할 때 | 새 채팅 세션 시작 |
| 이전 분석 결과를 기반으로 후속 작업할 때 | 같은 세션에서 계속 |
| 에러가 반복되어 세션이 혼란스러울 때 | 새 채팅 세션에서 문제를 깔끔하게 재정의 |

{% hint style="warning" %}
브라우저 탭을 전환하면 Agent 모드가 **일시정지** 됩니다. 장시간 작업을 실행 중일 때 탭을 떠나면 작업이 중단될 수 있습니다. 또한 **브라우저 새로고침** 은 현재 세션의 실행 상태를 초기화합니다.
{% endhint %}

### 6.2 권한 관리: "Always Allow" 주의

Agent 모드에서 Genie Code가 도구를 호출하거나 코드를 실행할 때, 사용자에게 **승인(Approve)** 을 요청합니다. 이때 **"Always Allow"** 옵션이 표시됩니다.

**"Always Allow"를 사용해도 되는 경우:**
- 읽기 전용 작업 (테이블 스키마 조회, SELECT 쿼리)
- sandbox/dev 환경에서의 개발 작업

**"Always Allow"를 사용하면 안 되는 경우:**
- 프로덕션 데이터에 대한 쓰기 작업
- 외부 시스템으로의 데이터 전송 (Slack 메시지, JIRA 티켓 생성)
- DROP, DELETE, UPDATE 등 파괴적 작업이 포함될 수 있는 경우

{% hint style="warning" %}
"Always Allow"는 편리하지만 **안전망을 제거** 합니다. Agent가 자율적으로 판단하여 실행하는 작업의 범위가 넓어질수록, 개별 액션 확인이 더 중요해집니다. 특히 프로덕션 환경에서는 매 액션을 직접 확인하는 것을 원칙으로 하세요.
{% endhint %}

### 6.3 작업 정의 방식: 목표 중심 + 제한 설정

Agent 모드에서는 **단계별 지시** 보다 **최종 목표 + 제한 조건** 을 주는 것이 더 효과적입니다. Agent가 스스로 최적 경로를 찾도록 하되, 넘지 말아야 할 경계를 명확히 하는 것입니다.

**비효과적인 프롬프트 (단계별 지시):**

```
1. orders 테이블을 읽어줘
2. customer_id로 그룹핑해줘
3. 매출 합계를 계산해줘
4. 상위 10개를 정렬해줘
5. 결과를 차트로 보여줘
```

**효과적인 프롬프트 (목표 + 제한):**

```
@main_catalog.sales.orders 테이블에서 상위 10 고객의 매출 분석 대시보드를 만들어줘.

제한사항:
- 최근 90일 데이터만 사용
- 개발 중에는 1000행으로 제한하여 먼저 테스트
- 결과는 dev_catalog.sandbox.simyung에 저장
- Plotly 차트 사용
```

이 접근법이 더 나은 이유는, Agent가 중간 단계에서 최적화할 여지를 갖게 되기 때문입니다. 예를 들어 데이터 크기에 따라 파티셔닝 전략을 자율적으로 결정하거나, 더 효율적인 집계 방식을 선택할 수 있습니다.

### 6.4 보안 제한 설정

Agent 모드에서 가장 중요한 것은 **위험한 작업을 사전에 차단** 하는 것입니다. 프롬프트에 명시적 제한을 포함하세요:

```
분석 진행하되 다음 규칙을 반드시 지켜줘:
- DROP TABLE, DELETE, UPDATE, ALTER 문을 실행하지 마
- 프로덕션 카탈로그(prod_catalog)에 절대 쓰기하지 마
- 외부 API 호출 시 민감 데이터를 전송하지 마
- 모든 중간 결과는 dev_catalog.sandbox.{내이름}에만 저장해
```

{% hint style="tip" %}
이 보안 규칙들은 User Instructions에 한 번 설정해두면 매 프롬프트에 반복하지 않아도 됩니다. 하지만 특히 민감한 작업에서는 **프롬프트에서 한 번 더 강조** 하는 이중 방어가 안전합니다.
{% endhint %}

### 6.5 개발/테스트 시 제한 설정

Agent가 대규모 테이블에 대해 작업할 때, 처음부터 전체 데이터를 처리하면 시간과 비용이 낭비됩니다:

```
먼저 1000행 샘플로 로직을 검증한 뒤, 확인되면 전체 데이터로 실행해줘.
```

이 한 줄이 클러스터 비용을 크게 절약합니다. Agent가 로직을 완성하고 사용자의 확인을 받은 후에만 전체 스케일로 확장하기 때문입니다.

### 6.6 무한 루프 대응

Agent 모드에서 드물게 **오류 → 수정 → 오류 → 수정** 의 무한 루프에 빠질 수 있습니다. 같은 에러가 2-3번 반복되면 Agent가 스스로 벗어나지 못할 가능성이 높습니다.

**대응 방법:**
1. 즉시 **Stop** 버튼으로 실행 중단
2. 현재까지의 에러 메시지를 복사
3. **새 채팅 세션** 을 열어서 에러 원인을 텍스트로 설명하고 해결 방향을 질문
4. Agent에게 단계별로 실행시키되, 각 단계를 확인한 후 다음으로 진행

{% hint style="warning" %}
무한 루프가 발생하면 **같은 세션에서 계속 시도하지 마세요.** 세션의 컨텍스트가 이미 에러 정보로 가득 차 있어서, Agent가 잘못된 맥락에서 벗어나기 어렵습니다. 깔끔한 새 세션에서 문제를 다시 정의하는 것이 훨씬 빠릅니다.
{% endhint %}

---

## 7. 추천 설정 조합 (역할별)

모든 설정을 처음부터 완벽하게 구성할 필요는 없습니다. 역할에 맞는 핵심 설정부터 시작하고, 사용하면서 점진적으로 확장하세요.

다음 표는 Databricks 데이터 팀의 주요 역할별로 검증된 설정 조합을 보여줍니다.

| 역할 | User Instructions 중점 | 추천 Workspace 스킬 | 추천 MCP 서버 |
|------|----------------------|-------------------|-------------|
| **데이터 엔지니어** | PySpark 패턴, DLT 규칙, 에러 핸들링 표준 | 파이프라인 템플릿, 데이터 품질 검증 | Databricks, GitHub, Slack |
| **데이터 분석가** | SQL 스타일, 시각화 선호, 리포트 형식 | 대시보드 생성, 리포트 자동화 | Databricks, Slack |
| **ML 엔지니어** | MLflow 규칙, 실험 네이밍, 모델 문서화 | 모델 배포 절차, 피처 엔지니어링 | Databricks, GitHub, Slack |
| **데이터 과학자** | 탐색 분석 패턴, 통계 검정 절차 | EDA 템플릿, 실험 결과 정리 | Databricks, Slack |
| **플랫폼 관리자** | 거버넌스 규칙, 리소스 관리 정책 | 권한 감사, 비용 분석 | Databricks, JIRA, Slack |

이 표에서 모든 역할에 **Databricks MCP** 와 **Slack MCP** 가 공통으로 포함된 것에 주목하세요. Databricks MCP는 워크스페이스 내 자원에 접근하는 기본 도구이고, Slack MCP는 결과를 팀과 공유하는 가장 빈번한 채널이기 때문입니다. GitHub MCP는 코드를 직접 관리하는 역할(엔지니어)에게 특히 유용합니다.

### 설정 우선순위 가이드

처음 Genie Code를 사용한다면, 다음 순서로 설정하는 것을 권장합니다:

1. **Workspace Instructions 확인**: 관리자가 이미 설정했는지 확인하고, 내용을 숙지합니다
2. **User Instructions 작성**: 자신의 역할, 선호 라이브러리, 보안 규칙을 정의합니다
3. **MCP 서버 추가**: Databricks MCP부터 시작하고, 필요에 따라 Slack/GitHub를 추가합니다
4. **Skills 생성**: 반복 작업이 2-3번 이상 발생하면 스킬로 만듭니다

{% hint style="info" %}
설정은 **살아있는 문서** 입니다. 처음에 완벽할 필요 없습니다. 사용하면서 "이걸 매번 말하고 있네"라고 느끼는 순간이 User Instructions에 추가할 타이밍이고, "이 절차를 또 설명하고 있네"라고 느끼는 순간이 스킬을 만들 타이밍입니다.
{% endhint %}

---

## 관련 가이드

- [Genie Code 사용법](usage.md) — 기본 사용법과 인터페이스 가이드
- [활용 시나리오](scenarios.md) — 역할별 실전 사용 사례
- [프롬프트 쿡북](prompt-cookbook.md) — 검증된 프롬프트 템플릿 모음
- [MCP 연동](mcp.md) — MCP 서버 상세 설정과 아키텍처
