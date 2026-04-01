# Getting Started — 시작하기

## 소스코드 다운로드

이 핸즈온의 전체 노트북 소스코드는 GitHub에서 다운로드할 수 있습니다.

### 방법 1: Git Clone

```bash
git clone https://github.com/SimyungYang/databricks-enablement-blog.git
cd databricks-enablement-blog/hands-on/smart-tv-vibe/notebooks/
```

### 방법 2: ZIP 다운로드

[GitHub에서 ZIP 다운로드](https://github.com/SimyungYang/databricks-enablement-blog/archive/refs/heads/main.zip) → 압축 해제 → `hands-on/smart-tv-vibe/notebooks/` 폴더 사용

### 방법 3: Databricks Workspace에서 직접 Import

1. Databricks Workspace → **Repos** 메뉴
2. **Add Repo**→ URL: `https://github.com/SimyungYang/databricks-enablement-blog.git`
3. `hands-on/smart-tv-vibe/notebooks/` 경로에서 노트북 실행

---

## 노트북 구조

### 공통 (Common) — 모든 트랙에서 먼저 실행

| # | 파일 | 내용 | 링크 |
|---|------|------|------|
| 01 | `common/01_setup_catalog_schema.py` | Catalog/Schema 생성 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/common/01_setup_catalog_schema.py) |
| 02 | `common/02_generate_synthetic_data.py` | 170만건 가상 데이터 생성 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/common/02_generate_synthetic_data.py) |

### Track A — 노트북 기반 (직접 코딩)

| # | 파일 | 내용 | 링크 |
|---|------|------|------|
| 03 | `track-a-notebooks/03_silver_gold_ctas.py` | Silver/Gold 레이어 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-a-notebooks/03_silver_gold_ctas.py) |
| 04 | `track-a-notebooks/04_sdp_pipeline.py` | SDP 파이프라인 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-a-notebooks/04_sdp_pipeline.py) |
| 05 | `track-a-notebooks/05_aibi_dashboard_genie.py` | AI/BI Dashboard & Genie | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-a-notebooks/05_aibi_dashboard_genie.py) |
| 06 | `track-a-notebooks/06_deploy_event_generator.py` | Event Generator 배포 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-a-notebooks/06_deploy_event_generator.py) |
| 07 | `track-a-notebooks/07_structured_streaming.py` | Structured Streaming | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-a-notebooks/07_structured_streaming.py) |
| 08 | `track-a-notebooks/08_ml_recommendation.py` | ML 추천 모델 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-a-notebooks/08_ml_recommendation.py) |
| 09 | `track-a-notebooks/09_anomaly_detection.py` | 이상 탐지 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-a-notebooks/09_anomaly_detection.py) |
| 10 | `track-a-notebooks/10_agent_bricks_lakebase.py` | Agent Bricks & Lakebase | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-a-notebooks/10_agent_bricks_lakebase.py) |

### Track B — AI 가이드 (프롬프트 기반)

| 파일 | 내용 | 링크 |
|------|------|------|
| `track-b-ai-guided/PROMPT_GUIDE.md` | AI 가이드 프롬프트 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-b-ai-guided/PROMPT_GUIDE.md) |
| `track-b-ai-guided/PROMPT_DETAILED.md` | 상세 프롬프트 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-b-ai-guided/PROMPT_DETAILED.md) |

### Track C — Genie Code (자연어 기반)

| 파일 | 내용 | 링크 |
|------|------|------|
| `track-c-genie-code/GENIE_CODE_GUIDE.md` | Genie Code 가이드 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/smart-tv-vibe/notebooks/track-c-genie-code/GENIE_CODE_GUIDE.md) |

---

## 사전 요구사항

| 항목 | 요구사항 |
|------|---------|
| **Workspace**| Databricks Premium 이상 |
| **Unity Catalog**| 활성화 필수 |
| **Compute**| Runtime 15.4+ (ML Runtime 권장) |
| **권한**| Catalog/Schema 생성 + Model Serving 권한 |
| **서비스**| Serverless SQL Warehouse (Genie/Dashboard용) |

{% hint style="warning" %}
반드시 **Common 노트북 (01, 02)** 을 먼저 실행하여 환경을 설정하세요. 이후 Track A/B/C 중 하나를 선택하여 진행합니다.
{% endhint %}

## 트랙 선택 가이드

| 트랙 | 대상 | 방식 | 난이도 |
|------|------|------|--------|
| **Track A**| 개발자, DE, DS | 노트북 직접 실행 & 코드 분석 | 중급 |
| **Track B**| AI에 관심 있는 분석가 | AI 프롬프트로 코드 생성 | 초급~중급 |
| **Track C**| 비개발자, BI 분석가 | Genie Code 자연어로 구현 | 초급 |
