# Tool 목록 및 상세

Builder App 에이전트가 사용하는 MCP 도구, 빌트인 도구, 스킬 시스템의 전체 목록과 설명입니다.

## Tool 설계 철학

Builder App의 도구 시스템은 세 가지 설계 원칙을 따릅니다:

### 1. 최소 권한 원칙 (Principle of Least Privilege)

각 도구는 **필요한 최소한의 API 권한만** 사용합니다. 예를 들어 `execute_sql` 도구는 SQL 실행 권한만 있으면 되고, 클러스터 관리 권한은 필요하지 않습니다. 사용자의 Databricks 토큰에 설정된 권한 범위 내에서만 도구가 작동합니다.

### 2. 멱등성 (Idempotency)

`create_or_update_*` 패턴의 도구들은 **멱등적** 으로 설계되었습니다. 같은 요청을 여러 번 실행해도 결과가 동일합니다. 대시보드, Genie Space, 파이프라인 등을 `create_or_update`로 만들면, 이미 존재하면 업데이트하고 없으면 생성합니다. 이는 에이전트가 실패 후 재시도할 때 **부작용 없이 안전하게 실행** 할 수 있게 합니다.

### 3. 비동기 장시간 작업 처리

10초 이상 소요되는 작업(파이프라인 실행, 대규모 SQL 등)은 **백그라운드 스레드** 에서 실행됩니다. 에이전트는 `operation_id`를 받아 주기적으로 상태를 폴링하고, 완료되면 결과를 수신합니다. 이 패턴 덕분에 에이전트가 장시간 작업을 기다리는 동안 **다른 작업을 병렬로 수행** 할 수 있습니다.

### 각 Tool의 내부 작동 방식

MCP 도구가 호출되면 내부적으로 다음 과정이 진행됩니다:

```
에이전트 → MCP Protocol → MCP Server → 입력 검증 → Databricks SDK 호출 → 결과 포매팅 → 반환
```

1. **입력 검증**: 파라미터 타입, 필수값, 범위를 검증합니다
2. **Databricks SDK 호출**: `databricks-sdk-py`를 사용하여 REST API를 호출합니다
3. **에러 처리**: API 오류 시 사용자 친화적 메시지로 변환합니다
4. **결과 포매팅**: JSON 응답을 에이전트가 이해할 수 있는 텍스트로 변환합니다

---

## Databricks MCP Server Tools

`databricks-mcp-server`에서 제공하는 30개 이상의 도구가 `mcp__databricks__<tool_name>` 형태로 에이전트에 로드됩니다.

### SQL 실행

| Tool | 설명 |
|---|---|
| `execute_sql` | SQL Warehouse에서 단일 SQL 쿼리 실행 |
| `execute_sql_multi` | 여러 SQL 문을 순차 실행 |

```
"main 카탈로그의 sales 스키마에 있는 테이블 목록을 보여줘"
→ execute_sql: SHOW TABLES IN main.sales
```

### Compute 관리

| Tool | 설명 |
|---|---|
| `list_clusters` | 워크스페이스 내 클러스터 목록 조회 |
| `get_best_cluster` | 사용 가능한 최적 클러스터 자동 선택 |
| `get_cluster_status` | 특정 클러스터 상태 확인 |
| `start_cluster` | 종료된 클러스터 시작 |
| `list_warehouses` | SQL Warehouse 목록 조회 |
| `get_best_warehouse` | 사용 가능한 최적 Warehouse 자동 선택 |

### DLT 파이프라인

| Tool | 설명 |
|---|---|
| `create_pipeline` | 새 DLT 파이프라인 생성 |
| `create_or_update_pipeline` | 파이프라인 생성 또는 업데이트 |
| `update_pipeline` | 기존 파이프라인 설정 변경 |
| `start_update` | 파이프라인 실행(업데이트) 시작 |
| `get_pipeline` | 파이프라인 상세 정보 조회 |
| `get_pipeline_events` | 파이프라인 이벤트 로그 조회 |
| `get_update` | 특정 업데이트 실행 상태 조회 |
| `find_pipeline_by_name` | 이름으로 파이프라인 검색 |
| `stop_pipeline` | 실행 중인 파이프라인 중지 |
| `delete_pipeline` | 파이프라인 삭제 |

### 파일 관리

| Tool | 설명 |
|---|---|
| `upload_file` | Workspace에 파일 업로드 |
| `upload_to_volume` | Unity Catalog Volume에 파일 업로드 |
| `upload_folder` | 폴더 전체 업로드 |
| `download_from_volume` | Volume에서 파일 다운로드 |
| `list_volume_files` | Volume 내 파일 목록 조회 |
| `get_volume_file_info` | Volume 파일 메타데이터 조회 |
| `create_volume_directory` | Volume 디렉토리 생성 |
| `delete_volume_file` | Volume 파일 삭제 |
| `delete_volume_directory` | Volume 디렉토리 삭제 |

### Jobs 관리

| Tool | 설명 |
|---|---|
| `manage_jobs` | Job 생성, 조회, 수정, 삭제 |
| `manage_job_runs` | Job Run 실행, 모니터링, 취소 |

### Genie Space

| Tool | 설명 |
|---|---|
| `create_or_update_genie` | Genie Space 생성 또는 업데이트 |
| `ask_genie` | Genie Space에 자연어 질문 전송 |
| `get_genie` | Genie Space 상세 정보 조회 |
| `delete_genie` | Genie Space 삭제 |

### 대시보드

| Tool | 설명 |
|---|---|
| `create_or_update_dashboard` | AI/BI 대시보드 생성 또는 업데이트 |
| `get_dashboard` | 대시보드 상세 정보 조회 |
| `publish_dashboard` | 대시보드를 공개 상태로 배포 |
| `delete_dashboard` | 대시보드 삭제 |

### Model Serving

| Tool | 설명 |
|---|---|
| `query_serving_endpoint` | Serving Endpoint에 추론 요청 전송 |
| `get_serving_endpoint_status` | Endpoint 상태 및 설정 조회 |
| `list_serving_endpoints` | 전체 Serving Endpoint 목록 조회 |

### Unity Catalog

| Tool | 설명 |
|---|---|
| `manage_uc_objects` | Catalog, Schema, Table, Volume 등 UC 객체 관리 |
| `manage_uc_grants` | UC 객체에 대한 권한(GRANT/REVOKE) 관리 |
| `manage_uc_tags` | UC 객체 태그 관리 |
| `manage_uc_connections` | 외부 연결 관리 |
| `manage_uc_storage` | 스토리지 자격 증명 및 외부 위치 관리 |
| `manage_uc_sharing` | Delta Sharing 관리 |
| `manage_uc_monitors` | 테이블 모니터 관리 |
| `manage_uc_security_policies` | 보안 정책 관리 |

### Vector Search

| Tool | 설명 |
|---|---|
| `create_or_update_vs_endpoint` | Vector Search Endpoint 생성/업데이트 |
| `create_or_update_vs_index` | Vector Search Index 생성/업데이트 |
| `query_vs_index` | 벡터 인덱스에 유사도 검색 실행 |
| `manage_vs_data` | 인덱스 데이터 동기화 관리 |
| `get_vs_endpoint` | Endpoint 상태 조회 |
| `get_vs_index` | Index 상태 조회 |

### 기타

| Tool | 설명 |
|---|---|
| `manage_workspace` | Workspace 객체(노트북, 폴더) 관리 |
| `manage_ka` | Knowledge Assistant 관리 |
| `manage_mas` | Multi-Agent System 관리 |
| `manage_metric_views` | Metric View 관리 |
| `get_current_user` | 현재 사용자 정보 조회 |
| `create_or_update_app` | Databricks App 생성/업데이트 |
| `execute_databricks_command` | 클러스터에서 명령 실행 |
| `run_python_file_on_databricks` | Python 파일을 클러스터에서 실행 |

---

## Built-in Tools (Claude Agent SDK)

에이전트가 프로젝트 파일을 직접 조작하는 데 사용하는 빌트인 도구입니다.

| Tool | 설명 |
|---|---|
| **Read** | 파일 내용 읽기 |
| **Write** | 새 파일 생성 |
| **Edit** | 기존 파일 수정 (diff 기반) |
| **Glob** | 파일 패턴 검색 |
| **Grep** | 파일 내용 정규식 검색 |
| **Skill** | 스킬 파일 로드 및 실행 |

{% hint style="info" %}
Built-in Tools로 에이전트는 프로젝트 디렉토리 내에서 노트북, SQL 파일, Python 스크립트 등을 직접 생성하고 편집할 수 있습니다.
{% endhint %}

---

## Skills System

29개의 마크다운 기반 스킬 파일이 에이전트에게 Databricks 작업 수행 패턴을 가르칩니다. 에이전트는 `/skill` 명령으로 필요한 스킬을 로드합니다.

### 주요 스킬 목록

| 스킬 | 설명 |
|---|---|
| **synthetic-data** | 합성 데이터 생성 가이드 |
| **dashboard** | AI/BI 대시보드 생성 패턴 |
| **genie-space** | Genie Space 구성 및 인스트럭션 작성 |
| **sdp** | Spark Declarative Pipeline(SDP) 패턴 |
| **unity-catalog** | UC 객체 생성 및 권한 관리 |
| **python-sdk** | Databricks Python SDK 사용 패턴 |
| **agent-bricks** | Knowledge Assistant, Genie Agent 등 Agent Bricks 구축 |
| **lakebase** | Lakebase(PostgreSQL) 설정 및 사용 |
| **jobs** | Databricks Jobs 생성 및 스케줄링 |
| **dabs** | Databricks Asset Bundles 구성 |
| **apps** | Databricks Apps 풀스택 개발(APX 프레임워크) |
| **mlflow** | MLflow 실험 및 모델 평가 |
| **model-serving** | Model Serving Endpoint 구성 |
| **vector-search** | Vector Search Index 생성 및 RAG 패턴 |

{% hint style="tip" %}
스킬은 에이전트의 "사전 지식"입니다. 예를 들어 "대시보드를 만들어줘"라고 요청하면, 에이전트가 `dashboard` 스킬을 로드한 후 올바른 Lakeview 대시보드 JSON 구조를 생성합니다.
{% endhint %}

### 커스텀 스킬 추가

프로젝트 디렉토리의 `skills/` 폴더에 마크다운 파일을 추가하면 에이전트가 해당 스킬을 인식합니다.

```markdown
<!-- skills/my-custom-skill.md -->
# My Custom Skill

## 개요
이 스킬은 특정 비즈니스 로직을 수행하는 방법을 안내합니다.

## 단계
1. 먼저 데이터를 조회합니다.
2. 필요한 변환을 수행합니다.
3. 결과를 저장합니다.
```

---

## 도구 사용 패턴

에이전트가 도구를 조합하여 복잡한 작업을 수행하는 대표적인 패턴입니다.

### 순차 실행 패턴

이전 도구의 출력이 다음 도구의 입력이 되는 패턴입니다.

```
manage_uc_objects (스키마 생성) → execute_sql (테이블 생성) → create_or_update_dashboard (대시보드 생성)
```

### 조건 분기 패턴

이전 도구의 결과에 따라 다음 행동을 결정하는 패턴입니다.

```
list_clusters (클러스터 목록 조회)
  ├─ 실행 중인 클러스터 있음 → get_best_cluster → execute_databricks_command
  └─ 없음 → start_cluster → (대기) → execute_databricks_command
```

### 반복 확인 패턴

장시간 작업의 완료를 대기하는 패턴입니다.

```
start_update (파이프라인 실행)
  → get_update (상태 확인) → RUNNING → (대기) → get_update
  → get_update (상태 확인) → COMPLETED → 결과 보고
```

{% hint style="info" %}
에이전트는 이러한 패턴을 **스킬 파일** 에서 학습합니다. 예를 들어 `sdp` 스킬은 파이프라인 생성 → 실행 → 상태 확인의 전체 흐름을 안내합니다.
{% endhint %}

---

## 참고 링크

- [Databricks MCP Server](https://github.com/databricks-solutions/ai-dev-kit/tree/main/databricks-mcp-server)
- [Databricks Skills](https://github.com/databricks-solutions/ai-dev-kit/tree/main/databricks-skills)
- [Claude Agent SDK 도구 문서](https://docs.anthropic.com/en/docs/agents)
- [MCP Protocol 규격](https://modelcontextprotocol.io/)
