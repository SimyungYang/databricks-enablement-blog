# Getting Started — 시작하기

## 소스코드 다운로드

이 핸즈온의 전체 노트북 소스코드는 GitHub에서 다운로드할 수 있습니다.

### 방법 1: Git Clone

```bash
git clone https://github.com/SimyungYang/databricks-enablement-blog.git
cd databricks-enablement-blog/hands-on/predictive-maintenance/notebooks/
```

### 방법 2: ZIP 다운로드

[GitHub에서 ZIP 다운로드](https://github.com/SimyungYang/databricks-enablement-blog/archive/refs/heads/main.zip) → 압축 해제 → `hands-on/predictive-maintenance/notebooks/` 폴더 사용

### 방법 3: Databricks Workspace에서 직접 Import

1. Databricks Workspace → **Repos** 메뉴
2. **Add Repo**→ URL: `https://github.com/SimyungYang/databricks-enablement-blog.git`
3. `hands-on/predictive-maintenance/notebooks/` 경로에서 노트북 실행

---

## 노트북 목록

| # | 파일명 | 내용 | 링크 |
|---|--------|------|------|
| 01 | `01_overview.py` | 전체 아키텍처 소개 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/01_overview.py) |
| 02 | `02_structured_feature_engineering.py` | 피처 엔지니어링 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/02_structured_feature_engineering.py) |
| 03 | `03_structured_model_training.py` | XGBoost 모델 학습 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/03_structured_model_training.py) |
| 03a | `03a_ml_trends_and_techniques.py` | ML 트렌드 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/03a_ml_trends_and_techniques.py) |
| 03b | `03b_multi_algorithm_comparison.py` | 다중 알고리즘 비교 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/03b_multi_algorithm_comparison.py) |
| 03c | `03c_advanced_techniques.py` | 고급 기법 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/03c_advanced_techniques.py) |
| 03d | `03d_retraining_strategies.py` | 재학습 전략 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/03d_retraining_strategies.py) |
| 04 | `04_model_registration_uc.py` | UC 모델 등록 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/04_model_registration_uc.py) |
| 05 | `05_challenger_validation.py` | 챌린저 검증 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/05_challenger_validation.py) |
| 06 | `06_batch_inference.py` | 배치 추론 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/06_batch_inference.py) |
| 07 | `07_unstructured_anomaly_detection.py` | 비정형 이상탐지 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/07_unstructured_anomaly_detection.py) |
| 08 | `08_model_monitoring.py` | 모델 모니터링 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/08_model_monitoring.py) |
| 09 | `09_mlops_agent.py` | MLOps 에이전트 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/09_mlops_agent.py) |
| 10 | `10_job_scheduling.py` | Job 스케줄링 | [GitHub](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/10_job_scheduling.py) |

---

## 사전 요구사항

| 항목 | 요구사항 |
|------|---------|
| **Workspace** | Databricks Premium 이상 |
| **Unity Catalog** | 활성화 필수 |
| **Compute** | ML Runtime 15.4+ (GPU: 07번 노트북) |
| **권한** | Catalog/Schema 생성 권한 |

{% hint style="warning" %}
노트북 01번을 먼저 실행하여 Catalog, Schema, 샘플 데이터를 생성해야 합니다.
{% endhint %}
