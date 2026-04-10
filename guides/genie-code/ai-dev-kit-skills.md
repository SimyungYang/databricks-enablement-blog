# AI Dev Kit 스킬 연동

> **최종 업데이트**: 2026-04-08

---

Genie Code는 기본적으로 관리형 MCP 서버(Unity Catalog Functions, Vector Search, Genie Spaces, GitHub 등)를 통해 워크스페이스 리소스를 직접 조작합니다. 하지만 "어떻게 만들어야 하는가"에 대한 **도메인 지식** -- 예를 들어 메달리온 아키텍처 패턴, SDP 파이프라인 구성법, MLflow 평가 워크플로 같은 베스트 프랙티스 -- 은 기본 제공되지 않습니다.

**AI Dev Kit 스킬** 은 이 지식 갭을 채워줍니다. 30개 이상의 `SKILL.md` 파일이 Genie Code의 Agent 모드에 로드되어, 요청에 맞는 코드 패턴과 워크플로를 자동으로 안내합니다. MCP 서버가 Genie Code의 **"손"** (실행 능력)이라면, AI Dev Kit 스킬은 **"머리"** (도메인 지식)에 해당합니다.

{% hint style="info" %}
AI Dev Kit GitHub: [databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit)
{% endhint %}

---

## 1. AI Dev Kit 스킬이란?

### 1.1 스킬의 본질

AI Dev Kit 스킬은 `SKILL.md` 형태의 **마크다운 지식 파일** 입니다. 각 스킬에는 세 가지 핵심 요소가 포함됩니다.

| 구성 요소 | 역할 | 예시 |
|-----------|------|------|
| **description** | Genie Code가 언제 이 스킬을 로드할지 결정하는 매칭 키워드 | "Delta Lake, Iceberg, UniForm, IRC 관련 작업" |
| **instructions** | 해당 도메인의 베스트 프랙티스, 권장 패턴, 코드 템플릿 | SDP 파이프라인에서 Bronze/Silver/Gold 테이블 구성법 |
| **tools** | 스킬이 참조하는 MCP 도구 목록 (선택사항) | `execute_sql`, `create_or_update_pipeline` |

이 구조 덕분에 Genie Code는 사용자의 요청을 분석하여 관련 스킬을 자동으로 로드하고, 그 지식을 바탕으로 정확한 코드와 워크플로를 생성합니다.

### 1.2 기본 MCP 서버와의 차이

Genie Code의 기본 MCP 서버와 AI Dev Kit 스킬은 서로 다른 차원에서 동작합니다. 아래 표는 두 가지의 핵심 차이를 보여줍니다.

| 구분 | Genie Code 기본 MCP 서버 | AI Dev Kit 스킬 |
|------|-------------------------|----------------|
| **성격** | 실행 도구 (API 호출, 데이터 조회) | 지식 가이드 (패턴, 베스트 프랙티스, 코드 예시) |
| **동작 방식** | Function Calling으로 직접 실행 | 컨텍스트로 로드되어 응답 품질 향상 |
| **제한** | MCP 도구 최대 20개 | 스킬 수 제한 없음 |
| **설치** | 자동 제공 (관리형) | 수동 설치 필요 |
| **업데이트** | Databricks가 관리 | 사용자가 `install_skills.sh` 재실행 |

두 가지가 상호 보완적으로 동작하는 구체적인 예를 보면, "SDP 파이프라인을 만들어줘"라고 요청했을 때 **스킬** 이 메달리온 아키텍처 패턴과 SDP 구문을 안내하고, **MCP 서버** 가 실제 `create_or_update_pipeline` API를 호출하여 파이프라인을 생성합니다.

### 1.3 기능 커버리지 비교

아래 표는 각 기능 영역에서 기본 MCP와 AI Dev Kit 스킬이 각각 무엇을 제공하는지 정리합니다.

| 기능 영역 | Genie Code 기본 MCP | AI Dev Kit 스킬 |
|-----------|:------------------:|:--------------:|
| **UC Functions** | 관리형 도구 제공 | MCP 도구로 가이드 |
| **Vector Search** | 관리형 도구 제공 | 스킬로 가이드 |
| **Genie Spaces** | 관리형 도구 제공 | 스킬로 가이드 |
| **Apps** | 관리형 도구 제공 | 스킬로 가이드 |
| **GitHub** | UC Connection으로 제공 | -- |
| **파이프라인 (SDP, Jobs, Streaming)** | -- | 스킬로 가이드 |
| **대시보드 (AI/BI)** | -- | 스킬로 가이드 |
| **ML/Agent (MLflow, Agent Bricks, Model Serving)** | -- | 스킬로 가이드 |
| **Iceberg / Lakebase** | -- | 스킬로 가이드 |

이 표에서 핵심 시사점은 명확합니다. 기본 MCP만으로는 실행은 가능하지만 "올바른 방법으로" 만드는 것이 어렵고, AI Dev Kit 스킬을 추가하면 데이터 엔지니어링, ML, 대시보드 등 Genie Code가 기본적으로 가이드하지 못하는 영역까지 전문가 수준의 지원을 받을 수 있습니다.

---

## 2. 설치 방법

### 2.1 사전 요구사항

AI Dev Kit 스킬을 설치하려면 **Databricks CLI** 가 로컬 환경에 설치되어 있고, 대상 워크스페이스에 인증이 설정되어 있어야 합니다.

```bash
# Databricks CLI 설치 확인
databricks --version

# 인증 프로필 확인
databricks auth profiles
```

{% hint style="warning" %}
Databricks CLI가 설치되어 있지 않다면, [공식 문서](https://docs.databricks.com/dev-tools/cli/install.html)를 참고하여 먼저 설치하세요. `pip install databricks-cli`가 아닌 **새로운 Databricks CLI** (`databricks` 명령어)가 필요합니다.
{% endhint %}

### 2.2 원클릭 설치 (권장)

레포를 클론하지 않고 스크립트를 직접 다운로드하여 실행하는 가장 간단한 방법입니다.

```bash
curl -sSL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/databricks-skills/install_skills.sh \
  | bash -s -- --install-to-genie
```

이 명령이 수행하는 작업은 다음과 같습니다.

1. AI Dev Kit 레포에서 모든 스킬 파일(`SKILL.md`)을 다운로드
2. MLflow 스킬 레포(`mlflow/skills`)에서 추가 스킬을 다운로드
3. Databricks CLI를 사용하여 `/Workspace/Users/<현재사용자>/.assistant/skills/` 경로에 업로드
4. Genie Code 설정 > 스킬 목록에 자동 등록

### 2.3 레포 클론 후 설치

로컬에서 스킬 파일을 확인하거나 커스터마이징하고 싶다면 레포를 먼저 클론합니다.

```bash
git clone https://github.com/databricks-solutions/ai-dev-kit.git
cd ai-dev-kit
./databricks-skills/install_skills.sh --local --install-to-genie
```

`--local` 플래그는 원격에서 다시 다운로드하지 않고 로컬 파일을 사용하도록 지시합니다.

### 2.4 특정 프로필 지정

여러 워크스페이스를 관리하는 경우 `--profile` 옵션으로 대상 워크스페이스를 지정합니다.

```bash
./databricks-skills/install_skills.sh --install-to-genie --profile MY_PROFILE
```

### 2.5 설치 확인

설치가 완료되면 두 곳에서 확인할 수 있습니다.

**방법 1: 워크스페이스 파일 탐색기**

워크스페이스 좌측 패널에서 `Users > {내 이름} > .assistant > skills` 경로를 열면 스킬 폴더가 나열됩니다. 각 폴더 안에 `SKILL.md` 파일이 있으면 정상입니다.

**방법 2: Genie Code 설정 확인**

1. Genie Code 패널 상단의 **톱니바퀴(Settings)** 아이콘 클릭
2. **Skills** 섹션에서 **User skills** 탭 확인
3. 설치된 스킬 목록이 표시되면 정상

{% hint style="info" %}
스킬은 **User 레벨** 로 설치됩니다. 팀 전체에 공유하려면 설치 후 스킬 파일을 `/Workspace/.assistant/skills/` (워크스페이스 루트)로 복사하면 **Workspace 스킬** 로 등록됩니다.
{% endhint %}

---

## 3. 스킬 전체 목록

AI Dev Kit에 포함된 30개 이상의 스킬을 카테고리별로 정리합니다. 각 스킬이 어떤 요청에 매칭되는지 이해하면, 프롬프트를 작성할 때 원하는 스킬이 로드되도록 유도할 수 있습니다.

### 3.1 AI & Agent

AI 함수, 에이전트 구성, 모델 배포 등 GenAI 관련 작업을 지원하는 스킬입니다.

| 스킬 이름 | 용도 | 매칭되는 요청 예시 |
|-----------|------|-------------------|
| **databricks-ai-functions** | `ai_classify`, `ai_extract`, `ai_summarize` 등 내장 AI 함수 활용 | "리뷰 데이터에서 감성 분류해줘" |
| **databricks-agent-bricks** | Knowledge Assistant, Genie Agent, Supervisor Agent 구성 | "고객 문의 처리 에이전트를 만들어줘" |
| **databricks-genie** | Genie Space 생성, 쿼리, 설정 | "매출 데이터용 Genie Space를 만들어줘" |
| **databricks-model-serving** | 모델/에이전트 서빙 엔드포인트 배포 | "학습된 모델을 서빙 엔드포인트로 배포해줘" |
| **databricks-vector-search** | 벡터 인덱스 생성, RAG/시맨틱 검색 구성 | "문서 기반 검색 시스템을 구축해줘" |

### 3.2 MLflow

실험 추적, 모델 평가, 에이전트 관측성 등 MLflow 생태계 스킬입니다. 이 스킬들은 `mlflow/skills` 레포에서 가져옵니다.

| 스킬 이름 | 용도 | 매칭되는 요청 예시 |
|-----------|------|-------------------|
| **agent-evaluation** | 에이전트/RAG 평가 워크플로 (correctness, groundedness 등) | "에이전트 응답 품질을 평가해줘" |
| **instrumenting-with-mlflow-tracing** | 기존 코드에 MLflow 트레이싱 추가 | "이 체인에 트레이싱을 추가해줘" |
| **mlflow-onboarding** | MLflow 실험/모델 레지스트리 시작 가이드 | "MLflow로 실험을 관리하고 싶어" |
| **querying-mlflow-metrics** | System Tables에서 메트릭 집계/분석 | "지난달 모델 추론 메트릭을 분석해줘" |
| **retrieving-mlflow-traces** | 저장된 트레이스 검색 및 분석 | "특정 요청의 트레이스를 찾아줘" |
| **databricks-mlflow-evaluation** | MLflow 기반 모델 평가 (분류, 회귀, LLM) | "모델 성능을 체계적으로 평가해줘" |

### 3.3 Analytics & Dashboard

데이터 분석 및 시각화 관련 스킬입니다.

| 스킬 이름 | 용도 | 매칭되는 요청 예시 |
|-----------|------|-------------------|
| **databricks-aibi-dashboards** | AI/BI 대시보드 생성 (SQL 검증, 레이아웃 구성 포함) | "매출 추이 대시보드를 만들어줘" |
| **databricks-unity-catalog** | 시스템 테이블 활용 (lineage, audit log, billing) | "테이블 리니지를 조회해줘" |
| **databricks-metric-views** | 비즈니스 메트릭 정의 및 관리 | "월별 매출 메트릭을 정의해줘" |
| **databricks-dbsql** | SQL 기능 활용 (고급 SQL, 함수 등) | "윈도우 함수로 누적 합계를 구해줘" |

### 3.4 Data Engineering

데이터 파이프라인, 스트리밍, 인제스트 관련 스킬입니다.

| 스킬 이름 | 용도 | 매칭되는 요청 예시 |
|-----------|------|-------------------|
| **databricks-spark-declarative-pipelines** | SDP(Spark Declarative Pipelines, 구 DLT) 파이프라인 구성 | "메달리온 아키텍처 파이프라인을 만들어줘" |
| **databricks-jobs** | Workflows 작업, 트리거, 스케줄 설정 | "매일 새벽 3시에 ETL 실행되게 해줘" |
| **databricks-spark-structured-streaming** | 실시간 스트리밍 파이프라인 구성 | "Kafka 스트림을 Delta 테이블로 수집해줘" |
| **databricks-synthetic-data-gen** | Faker 기반 테스트/합성 데이터 생성 | "100만 건의 테스트 주문 데이터를 생성해줘" |
| **databricks-iceberg** | Iceberg 테이블, UniForm, Iceberg REST Catalog | "Iceberg 테이블로 만들어줘" |
| **databricks-zerobus-ingest** | Zerobus 기반 데이터 인제스트 | "S3에서 데이터를 자동으로 수집해줘" |

### 3.5 Development & Deployment

앱 개발, CI/CD, 인증, 데이터베이스 관련 스킬입니다.

| 스킬 이름 | 용도 | 매칭되는 요청 예시 |
|-----------|------|-------------------|
| **databricks-bundles** | DABs(Databricks Asset Bundles) 기반 CI/CD | "번들로 프로젝트를 구성해줘" |
| **databricks-app-python** | Python 웹 앱 (Dash, Streamlit, Flask, Gradio) | "Streamlit 대시보드 앱을 만들어줘" |
| **databricks-python-sdk** | Python SDK, Databricks Connect, CLI 활용 | "Python SDK로 클러스터를 관리해줘" |
| **databricks-config** | 프로필 인증 설정 및 관리 | "Databricks 인증을 설정해줘" |
| **databricks-lakebase-provisioned** | Lakebase 관리형 PostgreSQL 설정 | "Lakebase 데이터베이스를 생성해줘" |
| **databricks-lakebase-autoscale** | Lakebase 오토스케일링 구성 | "Lakebase를 오토스케일 모드로 설정해줘" |

### 3.6 Reference

문서 인덱스 등 범용 참조 스킬입니다.

| 스킬 이름 | 용도 | 매칭되는 요청 예시 |
|-----------|------|-------------------|
| **databricks-docs** | Databricks 공식 문서 인덱스 (`llms.txt` 기반) | 모든 요청에서 공식 문서 참조 시 자동 활용 |

이 목록은 AI Dev Kit의 지속적인 업데이트로 확장됩니다. `install_skills.sh`를 재실행하면 새로 추가된 스킬도 자동으로 설치됩니다.

---

## 4. 활용 예시

### 4.1 자동 매칭 (Agent 모드)

Genie Code의 Agent 모드에서는 사용자의 요청 내용을 분석하여 관련 스킬의 `description`과 매칭한 후 자동으로 로드합니다. 별도의 조작 없이 자연스러운 대화로 스킬이 활성화됩니다.

**예시 1: 데이터 파이프라인 구축**

```
프롬프트: "IoT 센서 데이터를 실시간으로 수집하고 메달리온 아키텍처로 처리하는 파이프라인을 만들어줘"
```

Genie Code가 자동으로 로드하는 스킬:
- `databricks-spark-structured-streaming` -- 실시간 수집 패턴
- `databricks-spark-declarative-pipelines` -- 메달리온 아키텍처 SDP 구성
- `databricks-jobs` -- 파이프라인 스케줄링

**예시 2: AI/BI 대시보드 생성**

```
프롬프트: "매출 데이터로 월별 추이와 제품별 비교를 보여주는 AI/BI 대시보드를 만들어줘"
```

Genie Code가 자동으로 로드하는 스킬:
- `databricks-aibi-dashboards` -- 대시보드 레이아웃 및 SQL 검증
- `databricks-dbsql` -- 분석 SQL 패턴

**예시 3: MLflow 기반 모델 배포**

```
프롬프트: "학습된 분류 모델을 서빙 엔드포인트로 배포하고 평가 메트릭을 모니터링해줘"
```

Genie Code가 자동으로 로드하는 스킬:
- `databricks-model-serving` -- 엔드포인트 배포 패턴
- `databricks-mlflow-evaluation` -- 모델 평가 워크플로
- `querying-mlflow-metrics` -- 메트릭 모니터링 쿼리

### 4.2 수동 호출 (@멘션)

자동 매칭이 원하는 스킬을 로드하지 않을 때는 `@` 기호로 직접 지정할 수 있습니다.

```
@databricks-iceberg UniForm v2로 Iceberg 테이블을 생성하고 외부 엔진에서 읽을 수 있게 설정해줘
```

```
@databricks-bundles 이 프로젝트를 DABs 구조로 변환해줘
```

{% hint style="info" %}
`@` 멘션은 해당 스킬을 **강제 로드** 합니다. 자동 매칭과 달리 description이 일치하지 않아도 로드됩니다. 특정 스킬의 지식이 반드시 필요한 경우에 유용합니다.
{% endhint %}

---

## 5. 스킬 동작 메커니즘

### 5.1 로드 과정

스킬이 실제로 어떻게 동작하는지 이해하면 더 효과적으로 활용할 수 있습니다.

1. **요청 분석** -- 사용자가 프롬프트를 입력하면 Genie Code가 요청 의도를 파악합니다.
2. **스킬 매칭** -- 설치된 모든 스킬의 `description` 필드와 요청 내용을 비교하여 관련 스킬을 선별합니다.
3. **컨텍스트 주입** -- 매칭된 스킬의 `instructions` 내용이 Genie Code의 컨텍스트에 추가됩니다.
4. **응답 생성** -- 확장된 컨텍스트를 바탕으로 코드, 설명, 실행 계획을 생성합니다.
5. **도구 실행** -- 필요한 경우 MCP 도구를 호출하여 실제 작업을 수행합니다.

### 5.2 스킬과 MCP 도구의 관계

스킬과 MCP 도구는 별개의 메커니즘입니다. 이 구분이 중요합니다.

| 항목 | MCP 도구 | 스킬 |
|------|---------|------|
| **제한** | 세션당 최대 20개 | 제한 없음 |
| **동작** | Function Calling으로 API 호출 | 컨텍스트로 지식 주입 |
| **설정 위치** | Genie Code 설정 > MCP 서버 | Genie Code 설정 > 스킬 |
| **모드** | Agent 모드 전용 | Agent 모드 전용 |

스킬은 MCP 도구의 20개 제한에 포함되지 않습니다. 따라서 30개 이상의 스킬을 모두 설치해도 MCP 도구 슬롯을 소비하지 않습니다.

---

## 6. 커스텀 스킬 작성

### 6.1 왜 커스텀 스킬인가?

AI Dev Kit의 기본 스킬은 Databricks 플랫폼의 범용 베스트 프랙티스를 제공합니다. 하지만 실제 업무에서는 조직 고유의 네이밍 규칙, 데이터 모델, 파이프라인 패턴이 있습니다. 커스텀 스킬을 만들면 이러한 **조직 특화 지식** 을 Genie Code에 주입할 수 있습니다.

### 6.2 SKILL.md 템플릿

```markdown
---
description: |
  이 스킬이 언제 로드되어야 하는지 설명합니다.
  예: "사내 고객 데이터 파이프라인, customer_360 테이블, 고객 세그먼트 관련 작업"
tools:
  - execute_sql
  - create_or_update_pipeline
---

# 고객 360 파이프라인 가이드

## 개요
우리 조직의 고객 360 테이블은 다음 구조를 따릅니다...

## 네이밍 규칙
- 카탈로그: `prod_analytics`
- 스키마: `customer_360`
- Bronze 테이블: `raw_` 접두사
- Silver 테이블: `cleaned_` 접두사
- Gold 테이블: 접두사 없이 비즈니스 명칭 사용

## 파이프라인 패턴
```sql
-- Bronze: 원본 데이터 수집
CREATE OR REFRESH STREAMING TABLE raw_customer_events
AS SELECT * FROM STREAM read_files('/Volumes/landing/customer/events/');

-- Silver: 정제 및 타입 캐스팅
CREATE OR REFRESH MATERIALIZED VIEW cleaned_customer_events AS
SELECT
  CAST(event_id AS BIGINT),
  CAST(customer_id AS STRING),
  CAST(event_timestamp AS TIMESTAMP),
  event_type
FROM LIVE.raw_customer_events
WHERE event_id IS NOT NULL;
```

## 주의사항
- PII 컬럼은 반드시 `ai_mask()` 함수로 마스킹
- 일별 파이프라인은 KST 기준 새벽 2시 실행
```

### 6.3 배포 방법

커스텀 스킬을 배포하는 두 가지 경로가 있습니다.

**개인 스킬 (User Skills)**

```bash
# 워크스페이스 사용자 디렉토리에 업로드
databricks workspace mkdirs /Workspace/Users/<your-email>/.assistant/skills/my-custom-skill
databricks workspace import /Workspace/Users/<your-email>/.assistant/skills/my-custom-skill/SKILL.md \
  --file ./my-custom-skill/SKILL.md --overwrite
```

**팀 전체 공유 (Workspace Skills)**

```bash
# 워크스페이스 루트에 업로드 (관리자 권한 필요)
databricks workspace mkdirs /Workspace/.assistant/skills/my-custom-skill
databricks workspace import /Workspace/.assistant/skills/my-custom-skill/SKILL.md \
  --file ./my-custom-skill/SKILL.md --overwrite
```

{% hint style="warning" %}
Workspace 스킬은 해당 워크스페이스의 **모든 Genie Code 사용자** 에게 자동 적용됩니다. 조직 전체에 영향을 미치므로 배포 전 충분한 검토가 필요합니다.
{% endhint %}

---

## 7. 주의사항 & 트러블슈팅

### 7.1 Agent 모드 필수

AI Dev Kit 스킬은 **Agent 모드에서만** 동작합니다. Edit 모드나 Chat 모드에서는 스킬이 로드되지 않습니다. Genie Code 프롬프트 입력창 좌측에서 모드가 Agent로 설정되어 있는지 확인하세요.

### 7.2 스킬이 자동 로드되지 않을 때

스킬의 `description` 필드가 사용자의 요청과 충분히 매칭되지 않으면 자동 로드가 실패할 수 있습니다. 이 경우 두 가지 해결 방법이 있습니다.

1. **@멘션으로 강제 로드**: `@databricks-iceberg` 처럼 스킬 이름을 직접 지정
2. **프롬프트에 키워드 추가**: description에 포함된 키워드를 프롬프트에 명시적으로 포함

### 7.3 스킬 업데이트

AI Dev Kit은 지속적으로 업데이트됩니다. 최신 스킬을 받으려면 설치 스크립트를 다시 실행하세요.

```bash
# 최신 버전으로 업데이트 (기존 스킬 덮어쓰기)
curl -sSL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/databricks-skills/install_skills.sh \
  | bash -s -- --install-to-genie
```

### 7.4 스킬 비활성화

특정 스킬이 불필요하거나 의도치 않게 로드되는 경우, 해당 스킬 폴더를 워크스페이스에서 삭제하면 됩니다.

```bash
databricks workspace delete /Workspace/Users/<your-email>/.assistant/skills/databricks-synthetic-data-gen --recursive
```

### 7.5 설치 실패 시

설치 스크립트가 실패하는 주요 원인과 해결 방법입니다.

| 증상 | 원인 | 해결 |
|------|------|------|
| `databricks: command not found` | Databricks CLI 미설치 | `curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh \| sh` |
| `Error: auth: cannot configure default credentials` | 인증 미설정 | `databricks auth login --host https://<workspace-url>` |
| `Error: Path already exists` | 이전 설치 잔재 | `--install-to-genie` 플래그가 자동 덮어쓰기 처리 |
| 일부 스킬만 설치됨 | 네트워크 타임아웃 | 스크립트 재실행 (멱등성 보장) |

이 표에서 알 수 있듯이, 대부분의 설치 문제는 Databricks CLI 설정과 관련되어 있습니다. CLI 인증이 정상이면 스킬 설치는 거의 실패하지 않습니다.

{% hint style="info" %}
스킬 설치 스크립트는 **멱등(idempotent)** 합니다. 여러 번 실행해도 동일한 결과를 보장하므로, 문제가 발생하면 안심하고 재실행하세요.
{% endhint %}

---

## 8. 정리

AI Dev Kit 스킬은 Genie Code를 단순한 코드 생성 도구에서 **Databricks 전문가 수준의 AI 어시스턴트** 로 업그레이드합니다. 핵심 포인트를 요약합니다.

| 항목 | 요약 |
|------|------|
| **설치** | `curl` 한 줄로 30개+ 스킬 일괄 설치 |
| **동작** | Agent 모드에서 요청에 따라 자동 로드 |
| **역할** | 기본 MCP(실행)를 보완하는 도메인 지식(가이드) |
| **커스텀** | `SKILL.md` 작성으로 조직 맞춤 지식 추가 |
| **업데이트** | `install_skills.sh` 재실행으로 최신 버전 유지 |
| **제한** | Agent 모드 전용, MCP 도구 제한과는 별개 |
