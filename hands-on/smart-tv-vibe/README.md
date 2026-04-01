# AI Vibe Coding Workshop — Smart TV 데이터 플랫폼 시나리오

> ** 최종 업데이트**: 2026-04 | ** 소요 시간**: 8~10시간 (1일 집중 또는 2일 분할)

---

## 개요

**Databricks Intelligence Platform** 의 핵심 기능 12가지를 하루 만에 체험하는 핸즈온 워크샵입니다. 스마트TV에서 발생하는 **170만 건 이상** 의 가상 로그 데이터를 기반으로, 데이터 엔지니어링부터 ML 모델 배포, GenAI 에이전트 구축까지 전 과정을 직접 구현합니다.

Databricks의 최신 AI 도구인 **Genie Code**(노트북 내장 AI)와 **AI Dev Kit**(Claude Code/Cursor 연동)를 활용하여 ** 자연어만으로** 대부분의 작업을 수행할 수 있음을 보여주는 것이 핵심 목표입니다.

{% hint style="info" %}
실제 고객 데이터 없이도 모든 실습이 가능합니다. 가상 데이터 생성 노트북(`02_generate_synthetic_data`)에서 170만 건의 시뮬레이션 데이터를 자동으로 생성합니다.
{% endhint %}

## 대상

* Databricks 신규 도입 고객 — 플랫폼 전체 기능 체험
* Data Engineer, Data Analyst, ML Engineer
* AI 코딩 도구(Vibe Coding)의 생산성 향상 효과를 검증하고 싶은 팀

## 사전 요구사항

| 항목 | 요구사항 | 비고 |
|------|---------|------|
| **Databricks Workspace**| Premium 이상 플랜 | Unity Catalog 활성화 필수 |
| ** 클러스터 권한**| 클러스터 생성 또는 서버리스 컴퓨트 접근 | 관리자에게 요청 |
| **Python**| 3.10+ (Track B 사용 시) | 로컬 설치 |
| **Claude Code**| 최신 버전 (Track B 사용 시) | `npm install -g @anthropic-ai/claude-code` |

{% hint style="success" %}
Track A(노트북 실행)와 Track C(Genie Code)는 Databricks 워크스페이스만 있으면 바로 시작할 수 있습니다. 로컬 설치가 필요 없습니다.
{% endhint %}

---

## 12가지 Databricks 핵심 기능

이 워크샵에서 체험하는 기능 목록입니다.

| # | Feature | 한 줄 설명 |
|---|---------|-----------|
| 1 | **Unity Catalog**| 3단계 네임스페이스(`catalog.schema.table`)로 데이터 거버넌스 통합 관리 |
| 2 | **Delta Lake**| ACID 트랜잭션, Time Travel, Schema Evolution 지원 오픈 테이블 포맷 |
| 3 | **SDP (Lakeflow Declarative Pipelines)**| 선언적 파이프라인으로 증분 처리와 데이터 품질 자동화 |
| 4 | **Auto Loader**| UC Volume 신규 파일 자동 감지, Exactly-once 처리 |
| 5 | **Structured Streaming**| 마이크로배치 기반 실시간 데이터 처리 파이프라인 |
| 6 | **AI/BI Dashboard**| SQL 기반 인터랙티브 대시보드 |
| 7 | **AI/BI Genie**| 자연어로 데이터 탐색 및 SQL 결과 조회 |
| 8 | **MLflow**| 실험 추적, 하이퍼파라미터 비교, 모델 레지스트리 |
| 9 | **Model Serving**| REST API 엔드포인트, Scale-to-zero 지원 |
| 10 | **Vector Search**| 콘텐츠 임베딩과 유사도 검색으로 RAG 기반 구축 |
| 11 | **Agent Bricks**| Knowledge Assistant + Genie + Supervisor 멀티 에이전트 |
| 12 | **Apps + Lakebase**| Databricks Apps 웹 앱 배포 + Lakebase(PostgreSQL 호환 OLTP) |

---

## 워크샵 커리큘럼

| 순서 | 노트북 | 주제 | 핵심 기능 | 소요시간 |
|------|--------|------|----------|----------|
| 1 | `01_setup_catalog_schema` | 환경 설정 | Unity Catalog, Schema, Volume | ~1분 |
| 2 | `02_generate_synthetic_data` | 가상 데이터 생성 (170만건) | PySpark, Delta Lake | ~10분 |
| 3 | `03_silver_gold_ctas` | Bronze->Silver->Gold 수동 변환 | CTAS, SQL, Medallion Architecture | ~30분 |
| 4 | `04_sdp_pipeline` | 동일 변환을 SDP로 자동화 | SDP (Lakeflow), Expectations | ~30분 |
| 5 | `05_aibi_dashboard_genie` | 대시보드 & 자연어 탐색 | AI/BI Dashboard, Genie Space | ~1시간 |
| 6 | `06_deploy_event_generator` | 실시간 이벤트 생성기 배포 | Databricks Apps, FastAPI | ~30분 |
| 7 | `07_structured_streaming` | 실시간 데이터 처리 | Auto Loader, Structured Streaming | ~1시간 |
| 8 | `08_ml_recommendation` | ML 추천 모델 & MLOps | Feature Store, LightGBM, MLflow, Model Serving | ~1.5시간 |
| 9 | `09_anomaly_detection` | 이미지 이상 탐지 | CNN, SHAP, 비정형 데이터 처리 | ~1시간 |
| 10 | `10_agent_bricks_lakebase` | GenAI 에이전트 & OLTP 연동 | Agent Bricks, Lakebase | ~2시간 |

---

## 3가지 학습 트랙

동일한 교육 내용을 세 가지 방식으로 진행할 수 있습니다.

### Track A — 노트북 직접 실행

노트북을 순서대로 열어 Run All을 실행합니다. 코드를 한 줄씩 읽으며 동작 원리를 이해하고 싶은 분에게 추천합니다. 추가 설치가 필요 없습니다.

### Track B — Claude Code + AI Dev Kit

Claude Code에 자연어 프롬프트를 입력하여 코드를 자동 생성합니다. [AI Dev Kit](https://github.com/databricks-solutions/ai-dev-kit)의 **MCP Server 50+ 도구** 와 **19개 Skills** 를 활용합니다.

```bash
# AI Dev Kit 설치
bash <(curl -sL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/install.sh)
# Claude Code 실행 후 PROMPT_GUIDE.md의 프롬프트를 복사하여 붙여넣기
claude
```

### Track C — Genie Code (Databricks 내장)

Databricks 노트북에서 `Cmd+I`로 Genie Code를 호출하여 자연어로 코드를 생성합니다. 별도 설치 없이 즉시 AI 코딩을 체험할 수 있습니다.

{% hint style="info" %}
트랙을 섞어서 진행해도 됩니다. 예를 들어, 데이터 엔지니어링(03~04)은 Track A로, ML(08~09)은 Track B로 진행하는 것도 좋은 방법입니다.
{% endhint %}

---

## 시나리오: Smart TV 데이터

모든 데이터는 노트북에서 자동 생성되므로 실제 고객 데이터가 불필요합니다.

| 테이블 | 건수 | 설명 |
|--------|------|------|
| `bronze.devices` | 10,000 | TV 디바이스 마스터 정보 |
| `bronze.viewing_logs` | 500,000 | 채널/앱 시청 기록 |
| `bronze.click_events` | 1,000,000 | 리모컨/UI 조작 이벤트 |
| `bronze.ad_impressions` | 200,000 | 광고 노출/클릭/전환 |

가상 데이터이지만 실제 패턴을 반영합니다: 저녁 프라임타임(19~23시) 시청 집중, Native 광고 CTR 4~7%, 지역별 가중치 등.

---

## 클러스터 설정 권장

| 모듈 | 컴퓨트 | 비고 |
|------|--------|------|
| Module 0~4 (데이터 엔지니어링) | Serverless | 추가 설정 불필요 |
| Module 5 (ML) | ML Runtime + GPU | 이미지 이상 탐지 시 필요 |
| Module 6 (GenAI) | Serverless + Model Serving | 서빙 엔드포인트 접근 권한 필요 |
| Module 7 (Apps) | Serverless | Lakebase 접근 권한 필요 |

---

## 참고 자료

| 주제 | 링크 |
|------|------|
| AI Dev Kit GitHub | [github.com/databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit) |
| Genie Code 소개 | [databricks.com/blog/introducing-genie-code](https://www.databricks.com/kr/blog/introducing-genie-code) |
| Agent Bricks 문서 | [docs.databricks.com/generative-ai/agent-bricks](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/) |
| Databricks GenAI Cookbook | [ai-cookbook.io](https://ai-cookbook.io/) |
| MLflow 공식 문서 | [mlflow.org/docs/latest](https://mlflow.org/docs/latest/) |
| Lakebase 문서 | [docs.databricks.com/database](https://docs.databricks.com/aws/en/database/) |
| SDP (Lakeflow) 문서 | [docs.databricks.com/delta-live-tables](https://docs.databricks.com/aws/en/delta-live-tables/) |
