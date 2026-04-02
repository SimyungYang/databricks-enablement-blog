# ML 심화 가이드

> **대상**: ML 알고리즘의 원리, 최신 기법, 재학습 전략에 대해 **깊이 있게** 이해하고 싶은 분

---

## 왜 이 내용이 중요한가?

핸즈온 파이프라인(01~10)은 **예지보전 & 이상탐지** 에 집중하여, "무엇을 만드는가"를 다룹니다. 이 심화 가이드는 **"왜 이렇게 만드는가"** 와 **"더 잘 만들려면 어떻게 해야 하는가"** 에 대한 답을 제공합니다.

---

## 누가 읽어야 하는가?

| 대상 | 읽어야 할 문서 | 이유 |
|------|--------------|------|
| **데이터 사이언티스트** | ML 트렌드, 재학습 전략 모두 | 알고리즘 선택, HPO, 앙상블 등 실무 기법 습득 |
| **ML 엔지니어** | 재학습 전략 중심 | 운영 환경에서 모델 성능 유지를 위한 자동화 전략 |
| **프로젝트 매니저** | 각 문서의 개요/로드맵 부분 | PoC 계획 수립 시 기법별 난이도, 소요 시간 파악 |
| **설비/품질 엔지니어** | ML 트렌드의 제조업 적용 부분 | 도메인 관점에서 ML이 어떤 문제를 푸는지 이해 |

---

## 심화 가이드 목차

### [ML 트렌드 & 최신 기법](ml-trends.md)

ML 알고리즘의 70년 진화사부터 AutoML, 앙상블, Feature Selection, 비정형 이상탐지, MLOps 자동화까지 **제조 예지보전에 필요한 전 영역** 을 다룹니다.

- ML 알고리즘 진화 (Perceptron → XGBoost → Foundation Models)
- Gradient Boosting 계열 비교 (XGBoost, LightGBM, CatBoost)
- 불균형 데이터 처리 (SMOTE, ADASYN, Focal Loss)
- HPO 최신 기법 (Optuna, Hyperopt, FLAML)
- AutoML -- Databricks AutoML 활용법
- 앙상블 기법 (Stacking, Weighted Voting)
- Feature Selection (Boruta, SHAP, RFE)
- 비정형 이상탐지 트렌드 (Anomalib, Zero-shot)
- MLOps 자동화 (Feature Store, Model Monitoring, LLMOps)

### [재학습 전략](retraining-strategies.md)

ML 모델의 지속적 성능 유지를 위한 재학습 전략을 기초부터 최신 기법까지 **13개 Part** 로 체계적으로 다룹니다.

- Data Drift & Concept Drift 이해
- 재학습 트리거 전략 (스케줄/성능/드리프트/하이브리드)
- Full Retraining 실전 구현
- Delta Lake 기반 학습 데이터 관리
- 모델 버전 관리 & 롤백
- Incremental / Continual / Online Learning
- RL 기반 재학습 전략 자동 선택 (Contextual Bandit)
- Active Learning (레이블링 비용 최소화)
- 프로덕션 아키텍처 & 도입 로드맵

---

{% hint style="info" %}
핸즈온 파이프라인을 먼저 완료한 후 이 심화 가이드를 읽으면, 각 기법이 **파이프라인의 어느 단계에 적용되는지** 더 명확하게 이해할 수 있습니다.
{% endhint %}
