# ML 핵심 개념

이 섹션은 머신러닝의 기초부터 최신 기법까지, GenAI 이전의 **전통적 ML/DL** 지식을 체계적으로 정리합니다. GenAI가 주목받는 시대에도, 예측 모델링, 이상 탐지, 추천 시스템 등 많은 비즈니스 문제는 여전히 전통 ML로 해결됩니다.

{% hint style="info" %}
**학습 경로**: GenAI가 처음이라면 [GenAI 핵심 개념](../genai-concepts/README.md)부터 시작하세요. ML 모델링 경험이 있고 최신 기법/운영 전략이 필요하다면 이 섹션이 적합합니다.
{% endhint %}

---

## 왜 ML 핵심 개념이 필요한가?

| GenAI (LLM, Agent) | 전통 ML |
|---------------------|---------|
| 자연어 이해/생성, 대화, 코드 | 수치 예측, 분류, 이상 탐지, 추천 |
| 범용 — 하나의 모델로 다양한 작업 | 특화 — 작업별 최적 모델 필요 |
| 대규모 데이터 사전학습 필요 | 수천~수만 건으로 학습 가능 |
| API 호출 비용 (토큰당) | 자체 호스팅 가능 (한번 학습 후 추론 저렴) |

많은 제조, 금융, 유통 프로젝트에서 GenAI와 전통 ML을 **함께** 사용합니다. 예: 이상 탐지(전통 ML) + 원인 분석 보고서 생성(GenAI).

---

## 대상 독자

| 대상 | 읽어야 할 문서 | 이유 |
|------|------------|------|
| **데이터 사이언티스트** | ML 트렌드, 재학습 전략 모두 | 알고리즘 선택, HPO, 앙상블 등 실무 기법 |
| **ML 엔지니어** | 재학습 전략 중심 | 운영 모델 성능 유지 자동화 |
| **프로젝트 매니저** | 각 문서의 개요/로드맵 | PoC 계획 시 기법별 난이도/소요 시간 |
| **SE/SA** | 전체 | 고객 대응 시 ML 기법 추천 근거 |

---

## 주요 가이드

| 가이드 | 설명 | 난이도 |
|--------|------|--------|
| [ML 트렌드 & 최신 기법](ml-trends.md) | 알고리즘 70년 진화, Gradient Boosting 비교, 불균형 데이터, HPO, AutoML, 앙상블, Feature Selection, 이상탐지 트렌드 | 중급~고급 |
| [재학습 전략](retraining-strategies.md) | Data/Concept Drift, 재학습 트리거, Incremental/Continual/Online Learning, Active Learning, RL 기반 전략 자동 선택 | 중급~고급 |

---

## Databricks ML 기능과의 매핑

| ML 개념 | Databricks 기능 |
|--------|---------------|
| 실험 관리 | MLflow Tracking |
| 모델 레지스트리 | Unity Catalog Models |
| 하이퍼파라미터 튜닝 | Optuna + MLflow |
| AutoML | Databricks AutoML |
| Feature 관리 | Feature Engineering (Feature Store) |
| 모델 서빙 | Model Serving (실시간/배치) |
| 모델 모니터링 | Lakehouse Monitoring |
| GPU 학습 | ML Runtime + GPU Cluster |

---

## 다음 단계

- ML을 실전에 적용하고 싶다면 → [MLOps 핸즈온 워크샵](../../hands-on/predictive-maintenance/README.md)
- GenAI를 배우고 싶다면 → [GenAI 핵심 개념](../genai-concepts/README.md)
- RAG 시스템을 만들고 싶다면 → [RAG 가이드](../rag/README.md)
