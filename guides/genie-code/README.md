# Genie Code 사용 가이드

> **최종 업데이트**: 2026-03-27

---

## Genie Code란?

Databricks Genie Code는 Databricks 워크스페이스에 내장된 **AI 기반 코딩 어시스턴트**입니다. 자연어로 코드를 생성하고, 디버깅하고, 최적화할 수 있으며, 복잡한 다단계 워크플로를 자율적으로 수행하는 Agent 모드도 지원합니다.

Genie Code는 단순한 코드 자동완성 도구가 아닙니다. **Unity Catalog의 메타데이터를 이해**하고, Databricks 런타임에서 코드를 직접 실행하며, 오류가 발생하면 스스로 진단하고 수정할 수 있는 **컨텍스트 인식 코딩 파트너**입니다.

---

## 지원 제품 영역

Genie Code는 Databricks의 여러 제품 영역에서 사용할 수 있습니다. 제품에 따라 지원되는 모드가 다릅니다.

| 제품 영역 | Chat 모드 | Agent 모드 | 주요 활용 |
|-----------|-----------|------------|----------|
| **Notebooks**| O | O | 데이터 분석, ML 모델링, EDA, 코드 생성/디버깅 |
| **SQL Editor**| O | - | SQL 쿼리 작성, 최적화, 스키마 탐색 |
| **Dashboards**| O | O | 대시보드 자동 생성, 시각화 SQL 최적화 |
| **Lakeflow Pipelines Editor**| O | O | ETL 파이프라인 구축, SDP 코드 생성 |
| **MLflow**| O | - | 실험 분석, 모델 비교, Tracing 디버깅 |

---

## Chat 모드 vs Agent 모드 비교

| 비교 항목 | Chat 모드 | Agent 모드 |
|-----------|-----------|------------|
| **동작 방식**| 사용자 질문에 1회 응답 | 계획 수립 후 다단계 자율 실행 |
| **코드 실행**| 사용자가 수동으로 실행 | Genie가 자동으로 실행 |
| **오류 처리**| 오류 내용 설명 | 자동으로 오류 감지 및 수정 시도 |
| **파일/자산 생성**| 코드 제안만 제공 | 노트북 셀, 대시보드, 파이프라인 직접 생성 |
| **MCP 도구 호출**| 불가 | 가능 (외부 도구 연동) |
| **적합한 작업**| 코드 설명, 개념 학습, 간단한 코드 생성 | EDA, 대시보드 생성, 파이프라인 구축, 노트북 정리 |
| **실행 시간**| 수 초 | 수 분 (복잡도에 따라) |

{% hint style="warning" %}
Agent 모드는 **Notebooks, Dashboards, Lakeflow Pipelines Editor**에서만 사용 가능합니다. SQL Editor와 MLflow에서는 Chat 모드만 지원됩니다.
{% endhint %}

---

## 주요 기능 목록

### 대화형 기능

| 기능 | 설명 |
|------|------|
| **자연어 코드 생성**| "이 테이블에서 월별 매출 추이를 구해줘"와 같은 자연어로 코드 생성 |
| **코드 설명**| 기존 코드의 동작을 자연어로 설명 |
| **디버깅**| 오류 원인 분석 및 수정 방법 제안 |
| **문서 기반 응답**| Databricks 공식 문서를 검색하여 기술 질문에 답변 |
| **자연어 데이터 필터링**| 데이터 테이블에서 자연어로 필터 조건 지정 |

### 인라인 기능

| 기능 | 동작 | 트리거 |
|------|------|--------|
| **코드 자동완성**| 입력 중 실시간 코드 제안 | 자동 (타이핑 시) |
| **Quick Fix**| 기본 코드 오류 자동 감지 및 수정 제안 | 오류 발생 시 자동 |
| **Diagnose Error**| 복잡한 오류(환경 오류 포함) 분석 및 수정 | 오류 발생 시 버튼 클릭 |

### Slash 명령어

| 명령어 | 기능 |
|--------|------|
| `/explain` | 선택한 코드를 자연어로 설명 |
| `/fix` | 코드 오류를 분석하고 수정 |
| `/optimize` | 코드 성능 최적화 제안 |
| `/test` | 단위 테스트 자동 생성 |
| `/doc` | 문서/주석 자동 생성 |

---

## 목차

| 페이지 | 설명 |
|--------|------|
| [사용법](usage.md) | Chat/Agent 모드, 인라인 제안, Quick Fix, Slash 명령어 상세 사용법 |
| [활용 시나리오](scenarios.md) | 데이터 사이언스, DE, 대시보드, GenAI 시나리오별 예시 |
| [MCP 연동](mcp.md) | MCP 개요, 서버 설정, Genie Code에서 MCP 활용 |
| [Space vs Code 비교](comparison.md) | Genie Space와 Genie Code의 상세 비교 |

---

## 참고 자료

* [Databricks Genie Code 공식 문서](https://docs.databricks.com/aws/en/genie-code/)
* [Genie Code 사용법 (Azure)](https://learn.microsoft.com/en-us/azure/databricks/genie-code/use-genie-code)
* [Genie Agent Mode](https://docs.databricks.com/aws/en/genie/agent-mode)
* [Databricks Genie Space 공식 문서](https://docs.databricks.com/aws/en/genie/)
* [Genie Space 설정 가이드](https://docs.databricks.com/aws/en/genie/set-up)
* [Genie Space 베스트 프랙티스](https://docs.databricks.com/aws/en/genie/best-practices)
