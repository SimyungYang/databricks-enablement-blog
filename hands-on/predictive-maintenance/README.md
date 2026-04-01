# Databricks MLOps 완전 가이드: 예지보전 & 이상탐지 파이프라인

> **최종 업데이트**: 2026-03-27 | **대상**: Databricks Lakehouse 기반 MLOps 구축을 위한 실전 가이드

> **전체 노트북 코드**: [GitHub — notebooks/](https://github.com/SimyungYang/databricks-enablement-blog/tree/main/hands-on/predictive-maintenance/notebooks)

---

## MLOps 개요

### MLOps란?

MLOps(Machine Learning Operations)는 ML 모델의 **개발 → 배포 → 운영 → 모니터링** 을 자동화하는 엔지니어링 프랙티스입니다. 데이터 사이언스와 운영(Ops)을 연결하여, 모델이 실험실을 벗어나 실제 비즈니스 가치를 창출하도록 합니다.

### 왜 MLOps가 필요한가?

- **재현성**: 동일한 데이터와 코드로 동일한 결과를 보장
- **자동화**: 수동 작업을 줄이고 반복 가능한 파이프라인 구축
- **거버넌스**: 모델의 계보(Lineage), 버전, 접근 권한을 중앙에서 관리
- **모니터링**: 운영 중 모델 성능 저하(Data Drift, Concept Drift)를 자동 탐지

### Databricks MLOps 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MLOps 파이프라인 아키텍처                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │  정형 데이터   │    │ 비정형 데이터  │    │   Unity Catalog      │  │
│  │  (AI4I 2020)  │    │ (MVTec AD)   │    │   (거버넌스/계보)     │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────────────────┘  │
│         │                   │                                       │
│         ▼                   ▼                                       │
│  ┌──────────────┐    ┌──────────────┐                              │
│  │ Feature Eng.  │    │ Image Proc.  │                              │
│  │ (Spark/Pandas)│    │ (Anomalib)   │                              │
│  └──────┬───────┘    └──────┬───────┘                              │
│         │                   │                                       │
│         ▼                   ▼                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │ XGBoost Train │    │ PatchCore    │    │   MLflow Tracking    │  │
│  │ + SHAP        │    │ Train        │    │   (실험/메트릭/모델)  │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────────────────┘  │
│         │                   │                                       │
│         ▼                   ▼                                       │
│  ┌─────────────────────────────────────┐                           │
│  │     UC Model Registry                │                           │
│  │  (Champion / Challenger 에일리어스)    │                           │
│  └──────────────┬──────────────────────┘                           │
│         ┌───────┴───────┐                                          │
│         ▼               ▼                                          │
│  ┌──────────────┐ ┌──────────────┐    ┌──────────────────────┐    │
│  │ Batch Predict │ │ Model Serve  │    │  Lakehouse Monitor   │    │
│  │ (일 4회)      │ │ (실시간)     │    │  (드리프트 탐지)      │    │
│  └──────────────┘ └──────────────┘    └──────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              MLOps Agent + Databricks Workflows               │   │
│  │     운영: 주1회 재학습 + 일4회 배치예측                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 핵심 Databricks 기능 매핑

| 기능 영역 | Databricks 서비스 | 역할 |
|-----------|------------------|------|
| 데이터 관리 | Delta Lake, Unity Catalog, Volumes | ACID 트랜잭션, 거버넌스, 비정형 데이터 |
| 실험 추적 | MLflow Tracking, Autolog | 파라미터/메트릭/아티팩트 자동 기록 |
| 모델 관리 | UC Model Registry | 버전 관리, Alias(Champion/Challenger) |
| 추론 | PySpark UDF, Model Serving | 배치/실시간 예측 |
| 모니터링 | Lakehouse Monitoring | 데이터 드리프트, 성능 추적 |
| 자동화 | Workflows, AI Agent | 파이프라인 스케줄링, 자동 오케스트레이션 |

---

## 전체 파이프라인 흐름

### End-to-End 데이터 흐름

```
[데이터 수집]
    │
    ▼
02. 피처 엔지니어링 ──────────── Delta Lake 테이블 저장
    │                              (Unity Catalog 계보 추적)
    ▼
03. 모델 학습 ────────────────── MLflow 실험 추적
    │  (XGBoost / LightGBM /       (Autolog, SHAP, HPO)
    │   CatBoost / Stacking)
    ▼
04. 모델 등록 ────────────────── UC Model Registry
    │                              (Challenger 에일리어스)
    ▼
05. 챌린저 검증 ──────────────── 4단계 검증
    │  (문서화/추론/성능/KPI)        통과 시 Champion 승급
    ▼
06. 배치 추론 ────────────────── PySpark UDF 분산 추론
    │  (일 4회 자동 실행)            결과 Delta Lake 저장
    ▼
08. 모니터링 ─────────────────── Lakehouse Monitoring
    │  (PSI 드리프트 탐지)           성능 저하 시 알림
    ▼
09. MLOps Agent ──────────────── 자동 오케스트레이션
    │  (드리프트 → 재학습 트리거)
    ▼
10. Job 스케줄링 ─────────────── Databricks Workflows
    (운영/개발 환경 분리)
```

### 비정형 데이터 흐름 (병렬)

```
이미지 데이터 (UC Volumes)
    │
    ▼
07. Anomalib PatchCore 학습 ──── GPU Cluster
    │                              MLflow 아티팩트 추적
    ▼
UC Model Registry ────────────── 정형 모델과 동일 거버넌스
```

{% hint style="info" %}
정형 모델과 비정형 모델이 **동일한 Unity Catalog**내에서 관리되므로, 향후 두 모델의 예측을 결합한 **복합 판단 시스템(Compound AI System)** 으로 확장할 수 있습니다.
{% endhint %}

---

## 참고 문서

### Databricks 공식 문서

| 주제 | 링크 |
|------|------|
| MLflow Experiment Tracking | [docs.databricks.com/mlflow/tracking](https://docs.databricks.com/en/mlflow/tracking-and-model-registry.html) |
| Unity Catalog Model Registry | [docs.databricks.com/machine-learning/manage-model-lifecycle](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/index.html) |
| Lakehouse Monitoring | [docs.databricks.com/lakehouse-monitoring](https://docs.databricks.com/en/lakehouse-monitoring/index.html) |
| Databricks AutoML | [docs.databricks.com/machine-learning/automl](https://docs.databricks.com/en/machine-learning/automl/index.html) |
| Feature Engineering | [docs.databricks.com/machine-learning/feature-store](https://docs.databricks.com/en/machine-learning/feature-store/index.html) |
| Model Serving | [docs.databricks.com/machine-learning/model-serving](https://docs.databricks.com/en/machine-learning/model-serving/index.html) |
| Databricks Workflows | [docs.databricks.com/workflows](https://docs.databricks.com/en/workflows/index.html) |
| AI Agent Framework | [docs.databricks.com/generative-ai/agent-framework](https://docs.databricks.com/en/generative-ai/agent-framework/index.html) |

### 외부 참고 자료

| 주제 | 링크 |
|------|------|
| MLflow 공식 문서 | [mlflow.org/docs/latest](https://mlflow.org/docs/latest/index.html) |
| XGBoost 문서 | [xgboost.readthedocs.io](https://xgboost.readthedocs.io/) |
| Anomalib (이상탐지) | [github.com/openvinotoolkit/anomalib](https://github.com/openvinotoolkit/anomalib) |
| SHAP (모델 해석) | [shap.readthedocs.io](https://shap.readthedocs.io/) |
| Optuna (HPO) | [optuna.readthedocs.io](https://optuna.readthedocs.io/) |
| imbalanced-learn (SMOTE) | [imbalanced-learn.org](https://imbalanced-learn.org/) |
