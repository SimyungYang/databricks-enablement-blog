# Databricks ML/AI 기능 전체 가이드

Databricks는 단순한 데이터 플랫폼이 아니라, **데이터 준비부터 모델 학습, 배포, 모니터링까지 ML 라이프사이클 전체** 를 하나의 플랫폼에서 관리할 수 있는 통합 ML/AI 환경입니다. 이 가이드는 Databricks가 제공하는 ML/AI 관련 기능을 체계적으로 정리하여, 각 기능이 왜 필요하고 어떻게 작동하며 실전에서 어떻게 활용되는지를 전문가 수준으로 설명합니다.

{% hint style="info" %}
이 가이드는 Databricks ML/AI **플랫폼 기능** 에 초점을 맞춥니다. ML 알고리즘/기법 자체에 대한 이론은 [ML 트렌드 & 최신 기법](ml-trends.md)을, GenAI/LLM 이론은 [GenAI 핵심 개념](../genai-concepts/README.md)을 참고하세요.
{% endhint %}

---

## 1. Databricks ML/AI 플랫폼 전체 아키텍처

### Data Intelligence Platform에서 ML의 위치

Databricks는 **Data Intelligence Platform** 이라는 비전 아래 데이터 엔지니어링, 분석, ML/AI를 하나의 Lakehouse 위에서 통합합니다. ML은 이 플랫폼의 핵심 축으로, 다음과 같은 이점을 제공합니다.

| 전통적 ML 환경 (분리된 도구) | Databricks Lakehouse ML |
|------------------------------|-------------------------|
| 데이터를 별도 ML 플랫폼으로 복사 | Delta Lake에 저장된 데이터를 직접 사용 |
| 실험 관리 도구 별도 구축 (자체 MLflow 서버) | MLflow가 Workspace에 내장 |
| 모델 레지스트리를 별도 운영 | Unity Catalog에 모델을 데이터와 함께 거버넌스 |
| 서빙 인프라 별도 구축 (K8s, SageMaker 등) | Model Serving Endpoint 내장 |
| 피처 스토어 별도 운영 (Feast, Tecton 등) | Feature Engineering in Unity Catalog |

이 통합의 핵심 가치는 **데이터 이동 최소화** 와 **거버넌스 통합** 입니다. 데이터 엔지니어가 만든 테이블을 데이터 사이언티스트가 바로 사용하고, 학습된 모델을 ML 엔지니어가 같은 플랫폼에서 배포하며, 모든 자산(데이터, 피처, 모델, 엔드포인트)이 Unity Catalog라는 단일 거버넌스 레이어로 관리됩니다.

### Classic ML vs GenAI: 두 축의 역할

Databricks ML/AI 기능은 크게 두 축으로 나뉩니다.

| 구분 | Classic ML | GenAI |
|------|-----------|-------|
| **대표 작업** | 수치 예측, 분류, 이상 탐지, 추천 | 자연어 이해/생성, 대화, 코드 생성, 이미지 분석 |
| **모델 유형** | XGBoost, LightGBM, RandomForest, PyTorch | LLM (GPT, Claude, Llama), Embedding 모델 |
| **데이터 요구** | 정형 데이터 수천~수만 건 | 비정형 데이터 (텍스트, 이미지) + 대규모 사전학습 |
| **Databricks 기능** | AutoML, MLflow, Feature Store, ML Runtime | Foundation Model APIs, Agent Framework, Vector Search |
| **비용 구조** | 학습 1회 후 추론 저렴 | API 호출 시 토큰당 과금 또는 GPU 서빙 비용 |

실전에서는 두 축을 **함께** 사용하는 경우가 많습니다. 예를 들어, 제조 공정에서 이상 탐지(Classic ML)가 알람을 발생시키면 GenAI Agent가 원인을 분석하고 대응 보고서를 자동 생성하는 파이프라인이 가능합니다.

---

## 2. 데이터 준비 & Feature Engineering

### 왜 Feature Store가 필요한가

ML 모델의 성능은 알고리즘보다 **피처(feature)의 품질** 에 의해 결정되는 경우가 많습니다. 그러나 실전에서는 세 가지 근본 문제가 반복적으로 발생합니다.

1. **Training-Serving Skew**: 학습 시에는 배치로 계산한 피처를 사용하고, 서빙 시에는 다른 코드로 실시간 계산하면서 미묘한 불일치가 발생합니다. 예를 들어, 학습 데이터에서는 "최근 30일 평균 구매액"을 SQL로 계산했는데, 서빙 코드에서는 API 호출 시점 기준으로 계산하여 윈도우가 달라지는 경우입니다.
2. **피처 중복 개발**: 데이터 사이언티스트 A가 만든 `avg_purchase_amount` 피처를 팀원 B가 모르고 다시 개발합니다. 조직 규모가 커질수록 동일한 비즈니스 개념에 대해 N개의 서로 다른 피처가 존재하게 됩니다.
3. **피처 거버넌스 부재**: 어떤 모델이 어떤 피처를 사용하는지, 피처 정의가 언제 변경되었는지 추적이 불가능합니다.

**Workspace Feature Store에서 UC 기반으로 전환한 이유**: 초기 Databricks Feature Store는 워크스페이스 단위로 격리되어 있어, 워크스페이스 간 피처 공유가 불가능했고 데이터 테이블과 별도의 거버넌스 체계를 사용했습니다. Unity Catalog 기반으로 전환하면서 피처 테이블이 **일반 Delta 테이블과 동일한 3-level 네임스페이스** (`catalog.schema.table`)로 관리되고, GRANT/REVOKE 권한, Lineage 추적, 크로스 워크스페이스 접근이 모두 통합되었습니다.

Databricks는 이 문제를 **Feature Engineering in Unity Catalog** 로 해결합니다.

### Feature Engineering in Unity Catalog

| 구성 요소 | 설명 |
|-----------|------|
| **Feature Table** | Unity Catalog에 등록된 Delta 테이블. 일반 테이블과 동일하게 SQL로 조회 가능하며, 기본 키(primary key)를 통해 피처 룩업이 가능 |
| **Feature Function** | Unity Catalog에 등록된 Python UDF를 피처로 직접 사용. **학습 시와 서빙 시 동일한 함수가 실행** 되어 training-serving skew를 원천적으로 방지. 예: `calculate_bmi(height, weight)` 함수를 한 번 등록하면 배치 학습과 실시간 추론에서 동일한 로직이 적용됨 |
| **Feature Spec** | 모델이 사용하는 피처 테이블 + 피처 함수의 조합을 정의한 메타데이터. 모델과 함께 Unity Catalog에 저장 |

**작동 원리**: `FeatureEngineeringClient`를 사용하여 학습 데이터셋을 생성할 때, 라벨 데이터와 피처 테이블을 자동으로 조인합니다. 이때 어떤 피처 테이블에서 어떤 키로 조인했는지가 모델에 기록되어, 서빙 시 동일한 피처를 자동으로 조회합니다.

```python
from databricks.feature_engineering import FeatureEngineeringClient, FeatureLookup

fe = FeatureEngineeringClient()

# 피처 룩업 정의
feature_lookups = [
    FeatureLookup(
        table_name="catalog.schema.sensor_features",
        feature_names=["avg_temperature", "vibration_rms"],
        lookup_key="device_id"
    )
]

# 학습 데이터셋 생성 (라벨 + 피처 자동 조인)
training_set = fe.create_training_set(
    df=labels_df,
    feature_lookups=feature_lookups,
    label="failure"
)
```

### Feature Serving (온라인 추론용)

배치 추론은 Delta 테이블에서 직접 피처를 읽으면 되지만, **실시간 추론** 에서는 밀리초 단위의 응답이 필요합니다. Delta Lake는 분석 워크로드에 최적화된 열 기반(Columnar) 스토리지이므로, 단일 키로 한 행을 빠르게 조회하는 Point Lookup에는 적합하지 않습니다.

Databricks **Online Table** 은 이 문제를 해결합니다. Delta 테이블의 데이터를 **자동으로 고성능 키-값 저장소(내부적으로 RocksDB 기반)에 동기화** 하여, Primary Key 기반 서브밀리초 수준의 조회를 가능하게 합니다. 사용자는 별도의 캐시 레이어(Redis, DynamoDB 등)를 구축할 필요 없이, Unity Catalog UI에서 클릭 몇 번으로 Online Table을 생성할 수 있습니다.

| 동기화 모드 | 설명 | 적합한 경우 |
|-------------|------|------------|
| **Snapshot** | 주기적으로 전체 테이블 복사 | 피처 변경이 드문 경우 |
| **Triggered** | 수동 또는 API 트리거로 증분 동기화 | 배치 파이프라인 완료 후 동기화 |
| **Continuous** | Delta 변경 사항을 실시간(초 단위) 반영 | 실시간 피처 업데이트가 필요한 경우 |

{% hint style="warning" %}
Online Table은 Unity Catalog 관리형 테이블에서만 생성 가능합니다. 외부 테이블(External Table)에서는 지원되지 않습니다.
{% endhint %}

---

## 3. 모델 학습 (Training)

### Databricks Runtime ML

Databricks Runtime ML은 표준 런타임에 **ML/DL 라이브러리가 사전 설치된 특수 런타임** 입니다. 직접 라이브러리를 설치하고 버전 충돌을 해결하는 고통을 없애줍니다.

주요 사전 설치 라이브러리는 다음과 같습니다.

| 카테고리 | 라이브러리 |
|----------|-----------|
| **Classic ML** | scikit-learn, XGBoost, LightGBM, CatBoost |
| **Deep Learning** | PyTorch, TensorFlow, Keras |
| **분산 학습** | Horovod, DeepSpeed, PyTorch Distributed |
| **실험 관리** | MLflow (Workspace에 자동 연결) |
| **데이터 처리** | pandas, NumPy, SciPy, Spark MLlib |
| **시각화** | matplotlib, seaborn, plotly |
| **GPU 지원** | CUDA, cuDNN (GPU 클러스터 선택 시) |

Runtime ML 버전은 Databricks Runtime 버전과 동일한 넘버링을 따르며 (예: DBR 16.x ML), 분기마다 새로운 버전이 출시됩니다.

### AutoML

**왜 등장했는가**: 데이터 사이언티스트가 새 데이터셋에 대해 적합한 알고리즘, 하이퍼파라미터, 전처리 방법을 찾는 데 수일~수주가 걸립니다. AutoML은 이 탐색 과정을 자동화합니다.

**Databricks AutoML의 차별점**: Google AutoML, AWS SageMaker Autopilot 등 대부분의 AutoML 도구는 결과 모델만 반환하는 **블랙박스** 방식입니다. Databricks AutoML은 근본적으로 다릅니다 -- 각 시도(trial)가 **완전한 실행 가능 노트북** 으로 생성되고, 모든 전처리/학습/평가 코드가 투명하게 공개됩니다. 이 노트북을 기반으로 도메인 지식을 반영한 수정이 가능하므로, AutoML이 **출발점(starting point)** 역할을 하고 데이터 사이언티스트가 **전문성을 더하는** 워크플로가 됩니다.

**내부 탐색 과정**: AutoML은 내부적으로 다음 단계를 자동 수행합니다.

1. **데이터 프로파일링**: 각 컬럼의 타입, 분포, 결측률을 분석하여 데이터 탐색 노트북 생성
2. **전처리 자동화**: 수치형 컬럼의 결측치를 중앙값/평균으로 대체, 범주형 컬럼에 원-핫 인코딩, 날짜 컬럼에서 요일/월/시간 등 파생 피처 추출
3. **알고리즘 탐색**: LightGBM, XGBoost, RandomForest, LogisticRegression/ElasticNet 등을 순차적으로 시도
4. **하이퍼파라미터 최적화**: Hyperopt(TPE 알고리즘, Tree-structured Parzen Estimator) 기반으로 각 알고리즘의 최적 하이퍼파라미터를 탐색
5. **앙상블 시도**: 상위 모델들의 가중 투표(Weighted Voting) 앙상블도 자동 시도

아래 표는 Databricks AutoML의 주요 기능을 정리한 것입니다.

| 기능 | 설명 |
|------|------|
| **지원 문제 유형** | 분류, 회귀, 시계열 예측 (Prophet, ARIMA 포함) |
| **탐색 알고리즘** | LightGBM, XGBoost, sklearn (RandomForest, LogisticRegression 등) + Hyperopt TPE |
| **자동 전처리** | 결측치 처리, 범주형 인코딩, 날짜 피처 추출, 텍스트 피처 TF-IDF |
| **출력물** | 베스트 모델 노트북 + MLflow Experiment + 데이터 탐색 노트북 |
| **사용 방법** | UI (Experiments > Create AutoML Experiment) 또는 Python API |
| **제한사항** | 딥러닝 모델은 탐색하지 않음, 이미지/텍스트 전용 태스크 미지원, 대규모 데이터셋(수백GB 이상)에서는 샘플링 필요 |

```python
from databricks import automl

summary = automl.classify(
    dataset=train_df,
    target_col="failure",
    primary_metric="f1",
    timeout_minutes=30
)

# 최고 성능 모델의 노트북 경로
print(summary.best_trial.notebook_path)
```

{% hint style="info" %}
AutoML은 **baseline 모델** 을 빠르게 확보하는 용도로 가장 효과적입니다. 생성된 노트북을 기반으로 도메인 지식을 반영한 피처 추가, 커스텀 전처리 등을 수행하는 것이 일반적인 워크플로입니다.
{% endhint %}

### 분산 학습

Databricks 클러스터의 분산 컴퓨팅 능력을 ML 학습에 활용하는 방법은 여러 가지입니다.

| 방법 | 적합한 경우 | 작동 방식 |
|------|------------|-----------|
| **Spark MLlib** | 대규모 정형 데이터, 클래식 ML 알고리즘 | Spark DataFrame 기반 분산 학습 |
| **pandas UDF + Spark** | 그룹별 독립 모델 학습 (예: 매장별 수요 예측) | `applyInPandas()`로 그룹별 pandas 모델 병렬 학습 |
| **Horovod / TorchDistributor** | 대규모 딥러닝 모델 (CNN, Transformer) | 데이터 병렬(Data Parallel) 분산 학습 |
| **DeepSpeed** | 초대형 모델 (수십억 파라미터) | ZeRO 최적화로 메모리 효율적 분산 학습 |
| **단일 노드 멀티 GPU** | 중간 규모 DL 모델 | PyTorch DDP 또는 Horovod 사용 |

**TorchDistributor의 동작 원리**: Spark 클러스터는 일반적으로 데이터 처리를 위해 설계되었지만, TorchDistributor는 **Spark 워커 노드를 PyTorch 분산 학습 노드로 전환** 합니다. 내부적으로 다음 과정이 일어납니다.

1. Spark 드라이버가 각 워커에 PyTorch 학습 프로세스를 시작하도록 지시
2. 각 워커에서 `torch.distributed` 백엔드(NCCL for GPU, Gloo for CPU)가 초기화되어 프로세스 간 통신 채널 구성
3. 데이터 병렬(Data Parallel) 방식으로 각 노드가 전체 모델의 복사본을 보유하고, 미니배치를 분할하여 학습
4. 그래디언트를 AllReduce 연산으로 동기화하여 모델 파라미터를 일치시킴

이 접근의 핵심 가치는 **Spark 클러스터 하나로 데이터 처리와 딥러닝 학습을 모두 수행** 할 수 있다는 것입니다. 별도의 Kubernetes 기반 학습 인프라(Kubeflow, Ray Train 등)를 구축할 필요가 없습니다.

```python
from pyspark.ml.torch.distributor import TorchDistributor

def train_fn():
    import torch
    import torch.distributed as dist
    # torch.distributed가 자동으로 초기화됨
    # 일반 PyTorch DDP 학습 코드 작성
    ...

distributor = TorchDistributor(
    num_processes=4,       # 총 GPU 프로세스 수
    local_mode=False,      # True면 드라이버 노드만 사용
    use_gpu=True           # GPU 사용 여부
)
distributor.run(train_fn)
```

**DeepSpeed ZeRO 최적화**: 수십억 파라미터 모델(예: Llama 7B 파인튜닝)은 단순 데이터 병렬로는 단일 GPU 메모리에 모델이 들어가지 않습니다. DeepSpeed의 **ZeRO(Zero Redundancy Optimizer)** 는 3단계로 메모리 사용을 최적화합니다.

| ZeRO Stage | 분산 대상 | 메모리 절감 | 통신 오버헤드 |
|------------|----------|-----------|-------------|
| **Stage 1** | Optimizer States (Adam의 momentum, variance) | ~4x | 낮음 |
| **Stage 2** | + Gradients | ~8x | 중간 |
| **Stage 3** | + Model Parameters | ~N배 (N=GPU 수) | 높음 (파라미터 수집 필요) |

Databricks ML Runtime에 DeepSpeed가 사전 설치되어 있으므로, TorchDistributor와 결합하여 대규모 모델의 파인튜닝을 수행할 수 있습니다.

### GPU 클러스터 활용

Databricks는 AWS(p4d, p5, g5), Azure(NC, ND 시리즈), GCP의 GPU 인스턴스를 지원합니다. GPU 클러스터 사용 시 고려사항은 다음과 같습니다.

| 고려사항 | 권장 사항 |
|---------|----------|
| **인스턴스 선택** | 학습: A100/H100 (고대역폭). 추론: T4/A10G (비용 효율) |
| **Runtime 선택** | 반드시 ML Runtime (GPU 버전) 선택 |
| **스팟 인스턴스** | 학습 시 비용 절감 가능. 체크포인트 저장 필수 |
| **단일 vs 멀티 노드** | 모델 크기 < GPU 메모리이면 단일 노드로 충분 |

---

## 4. 실험 관리 & 모델 레지스트리

### MLflow Tracking

**왜 필요한가**: ML 프로젝트에서는 수십~수백 번의 실험을 수행합니다. 어떤 하이퍼파라미터 조합이 최적이었는지, 어떤 전처리를 적용했는지를 체계적으로 기록하지 않으면 재현이 불가능합니다.

Databricks에는 **Managed MLflow** 가 내장되어 있어 별도 서버 구축 없이 바로 사용할 수 있습니다.

| MLflow 구성 요소 | 역할 |
|------------------|------|
| **Experiment** | 관련 실험(Run)의 논리적 그룹. 프로젝트나 문제 단위로 생성 |
| **Run** | 하나의 학습 실행. 파라미터, 메트릭, 아티팩트, 소스 코드를 기록 |
| **Parameter** | 하이퍼파라미터 (learning_rate, n_estimators 등) |
| **Metric** | 평가 지표 (accuracy, f1, rmse 등). 스텝별 기록 가능 |
| **Artifact** | 모델 파일, 그래프, 데이터 샘플 등 모든 바이너리 |
| **Tag** | 실행에 대한 메타데이터 (팀, 버전, 환경 등) |

```python
import mlflow

with mlflow.start_run(run_name="xgboost-v2"):
    mlflow.log_param("max_depth", 6)
    mlflow.log_param("learning_rate", 0.1)

    model = train_model(...)

    mlflow.log_metric("f1_score", 0.92)
    mlflow.log_metric("auc", 0.95)

    # 모델 + 피처 정보 함께 저장
    mlflow.sklearn.log_model(model, "model")
```

Databricks MLflow는 오픈소스 MLflow와 호환되면서도, **자동 로깅(Autolog)** 기능이 강화되어 있습니다. `mlflow.autolog()`를 호출하면 scikit-learn, XGBoost, PyTorch, TensorFlow 등의 학습을 자동으로 추적합니다.

### Unity Catalog 모델 레지스트리

**왜 등장했는가**: 기존 Workspace 레벨 모델 레지스트리는 워크스페이스 간 모델 공유가 어렵고, 데이터 거버넌스와 분리되어 있었습니다. Unity Catalog 모델 레지스트리는 모델을 **데이터와 동일한 거버넌스 체계** 로 관리합니다.

| 기능 | Workspace 레지스트리 (Legacy) | Unity Catalog 레지스트리 |
|------|------------------------------|-------------------------|
| **네임스페이스** | 워크스페이스 내 | `catalog.schema.model_name` (3-level) |
| **접근 제어** | 워크스페이스 단위 | Unity Catalog 권한 (GRANT/REVOKE) |
| **크로스 워크스페이스** | 불가 | 동일 메타스토어 내 모든 워크스페이스에서 접근 |
| **Lineage** | 제한적 | 데이터 테이블 → 피처 → 모델 → 엔드포인트 전체 추적 |
| **스테이지 관리** | Staging/Production/Archived | Alias (Champion, Challenger 등 자유 지정) |

Unity Catalog 모델 레지스트리의 핵심 개념인 **Alias** 는 기존의 고정된 스테이지(Staging, Production) 대신 유연한 태그 시스템을 제공합니다. 기존 스테이지 방식은 Staging → Production → Archived라는 고정 경로만 허용했으나, Alias는 **임의의 이름** 을 자유롭게 부여할 수 있어 다양한 배포 전략을 지원합니다.

예를 들어, `Champion`(현재 프로덕션 모델)과 `Challenger`(검증 중인 후보 모델) Alias를 지정하여 A/B 테스트를 구성하거나, `region-kr`, `region-us`처럼 지역별 모델을 관리할 수도 있습니다. Model Serving Endpoint가 Alias를 참조하므로, Alias를 다른 버전으로 이동시키면 **엔드포인트가 자동으로 새 모델 버전을 로드** 합니다 -- 제로 다운타임 배포가 가능합니다.

```python
import mlflow

# Unity Catalog에 모델 등록
mlflow.set_registry_uri("databricks-uc")
model_uri = "runs:/abc123/model"
mlflow.register_model(model_uri, "catalog.schema.fraud_detection")

# Alias 지정
from mlflow import MlflowClient
client = MlflowClient()
client.set_registered_model_alias(
    name="catalog.schema.fraud_detection",
    alias="Champion",
    version=3
)
```

### 모델 버전 관리 워크플로

아래 표는 일반적인 모델 라이프사이클에서 각 단계별 Databricks 기능 매핑을 보여줍니다.

| 라이프사이클 단계 | 활동 | Databricks 기능 |
|------------------|------|----------------|
| **실험** | 여러 알고리즘/파라미터 시도 | MLflow Experiment + Autolog |
| **등록** | 최적 모델을 레지스트리에 등록 | `mlflow.register_model()` |
| **검증** | Challenger 모델과 Champion 비교 | Alias + 평가 노트북 |
| **승격** | 검증 통과 시 Champion으로 변경 | `client.set_registered_model_alias()` |
| **배포** | 서빙 엔드포인트에 반영 | Model Serving (Alias 기반 자동 업데이트) |
| **폐기** | 더 이상 사용하지 않는 버전 정리 | `client.delete_registered_model_alias()` |

---

## 5. 모델 배포 (Serving)

### Model Serving Endpoints (실시간 추론)

**왜 등장했는가**: ML 모델을 프로덕션 API로 노출하려면 컨테이너 이미지 빌드, 로드 밸런서 구성, 오토스케일링 설정 등 인프라 작업이 필요합니다. Databricks Model Serving은 이 복잡성을 **완전 관리형 서비스** 로 추상화합니다.

| 기능 | 설명 |
|------|------|
| **원클릭 배포** | Unity Catalog 모델을 선택하면 REST API 엔드포인트 자동 생성 |
| **오토스케일링** | 트래픽에 따라 인스턴스 자동 확장/축소. Scale-to-zero 지원 |
| **A/B 테스팅** | 하나의 엔드포인트에 여러 모델 버전을 트래픽 비율로 라우팅 |
| **GPU 서빙** | GPU 인스턴스를 선택하여 DL 모델 서빙 가능 |
| **피처 자동 조회** | Feature Spec이 등록된 모델은 서빙 시 Online Table에서 피처를 자동 조회 |
| **환경 버전 관리** | 모델이 기록된 시점의 Python 환경(conda.yaml)을 자동으로 재현하여 "내 로컬에서는 됐는데" 문제 방지 |

```python
import requests

# 서빙 엔드포인트 호출 예시
endpoint_url = "https://<workspace-url>/serving-endpoints/<endpoint-name>/invocations"
headers = {"Authorization": f"Bearer {token}"}

payload = {
    "dataframe_records": [
        {"device_id": "sensor-001", "temperature": 85.2, "pressure": 1.2}
    ]
}

response = requests.post(endpoint_url, json=payload, headers=headers)
print(response.json())
```

### Batch Inference (대규모 배치 추론)

실시간 응답이 필요하지 않은 경우, **배치 추론** 이 비용 효율적입니다. Databricks에서 배치 추론을 수행하는 대표적인 방법은 다음과 같습니다.

| 방법 | 적합한 경우 | 장점 |
|------|------------|------|
| **`mlflow.pyfunc.spark_udf()`** | 대규모 데이터 (수백만~수십억 건) | Spark 병렬 처리, Delta 테이블에 직접 쓰기 |
| **MLflow `predict()`** | 소규모 데이터 (pandas DataFrame) | 간단한 코드, 로컬 테스트 용이 |
| **Feature Store `score_batch()`** | 피처 테이블 조인이 필요한 경우 | 피처 자동 조회 + 추론 한 번에 |

```python
import mlflow

# Spark UDF로 대규모 배치 추론
model_uri = "models:/catalog.schema.fraud_detection@Champion"
predict_udf = mlflow.pyfunc.spark_udf(spark, model_uri)

predictions = (
    spark.table("catalog.schema.transactions")
    .withColumn("prediction", predict_udf())
)
predictions.write.mode("overwrite").saveAsTable("catalog.schema.predictions")
```

### Foundation Model APIs

**왜 등장했는가**: LLM을 사용하려면 모델을 직접 호스팅하거나 외부 API를 호출해야 합니다. Databricks **Foundation Model APIs** 는 오픈소스 LLM을 Databricks 인프라에서 최적화된 상태로 제공하는 서버리스 API입니다.

아래 표는 두 가지 제공 유형의 차이와 각각 적합한 시나리오를 비교합니다.

| 구분 | Pay-per-token | Provisioned Throughput |
|------|--------------|----------------------|
| **과금 방식** | 입출력 토큰 수 기반 종량제 | 시간당 처리량(토큰/초) 단위 예약 |
| **지원 모델** | 사전 배포된 인기 모델 (DBRX, Llama, Mixtral 등) | Foundation 모델 + **커스텀 파인튜닝 모델** |
| **레이턴시** | 공유 인프라이므로 피크 시 변동 가능 | 전용 GPU 할당으로 **일관된 레이턴시 보장** |
| **적합한 경우** | PoC, 개발/테스트, 간헐적 호출 | 프로덕션 워크로드, SLA가 중요한 서비스, 높은 동시 요청 |
| **콜드 스타트** | 없음 (항상 준비됨) | 최초 배포 시 수분 소요 후 즉시 응답 |
| **비용 효율** | 낮은 사용량에서 유리 | 지속적/대량 호출에서 유리 (토큰당 단가가 낮아짐) |

{% hint style="info" %}
**선택 기준**: 월 토큰 사용량이 수백만 토큰 이하이면 Pay-per-token이 경제적입니다. 프로덕션 서비스에서 초당 수십~수백 요청을 처리하거나, 파인튜닝한 커스텀 모델을 서빙해야 한다면 Provisioned Throughput을 선택하세요.
{% endhint %}

Foundation Model APIs는 **OpenAI 호환 API** 를 지원하므로, 기존 OpenAI SDK 코드를 최소한의 변경으로 마이그레이션할 수 있습니다.

```python
from openai import OpenAI

client = OpenAI(
    api_key=databricks_token,
    base_url="https://<workspace-url>/serving-endpoints"
)

response = client.chat.completions.create(
    model="databricks-meta-llama-3-1-70b-instruct",
    messages=[{"role": "user", "content": "매출 하락 원인을 분석해주세요."}]
)
```

### External Models

**External Models** 는 Azure OpenAI, Anthropic Claude, Amazon Bedrock 등 **외부 LLM 제공자를 Databricks 엔드포인트로 프록시** 하는 기능입니다.

| 이점 | 설명 |
|------|------|
| **중앙 집중 거버넌스** | 모든 LLM 호출을 Unity Catalog 권한으로 제어 |
| **사용량 추적** | AI Gateway를 통해 토큰 사용량, 비용, 레이턴시를 모니터링 |
| **Rate Limiting** | 사용자/팀별 호출 한도 설정 |
| **API 키 관리** | 개별 사용자가 아닌 플랫폼 수준에서 API 키를 안전하게 관리 |
| **폴백(Fallback)** | 한 제공자가 실패하면 다른 제공자로 자동 전환 |

이 아키텍처의 핵심 가치는 **모델 제공자를 추상화** 하는 것입니다. 애플리케이션 코드에서는 Databricks 엔드포인트만 호출하고, 실제로 어떤 LLM이 뒤에서 동작하는지는 엔드포인트 설정에서 변경할 수 있습니다.

**AI Gateway의 실제 역할**: External Models 기능의 핵심은 **AI Gateway** 레이어입니다. 이것은 단순 프록시가 아니라, 엔터프라이즈 환경에서 LLM 사용을 통제하고 관찰하기 위한 핵심 인프라입니다.

| AI Gateway 기능 | 동작 방식 | 실전 가치 |
|----------------|----------|----------|
| **트래픽 라우팅** | 하나의 엔드포인트에 여러 제공자(예: GPT-4o + Claude)를 설정하고 가중치로 분배 | A/B 테스트, 점진적 마이그레이션 |
| **Rate Limiting** | 사용자/그룹/엔드포인트별 분당/시간당 토큰 한도 설정 | 비용 폭주 방지, 공정한 리소스 배분 |
| **Fallback** | 주 제공자 실패(timeout, 5xx) 시 자동으로 백업 제공자로 전환 | 서비스 가용성 보장 |
| **Guardrails** | 입력/출력에 안전성 필터 적용 (PII 마스킹, 유해 콘텐츠 차단) | 규정 준수, 보안 |
| **사용량 로깅** | 모든 요청/응답의 토큰 수, 레이턴시, 비용을 시스템 테이블에 자동 기록 | 비용 최적화, 감사(Audit) |

---

## 6. 모델 모니터링

### Lakehouse Monitoring

**왜 필요한가**: 프로덕션에 배포된 모델은 시간이 지남에 따라 성능이 저하됩니다. 입력 데이터의 분포가 변하거나(Data Drift), 입력과 출력 간의 관계가 변하면(Concept Drift) 모델의 예측 정확도가 떨어집니다.

Databricks **Lakehouse Monitoring** 은 테이블 단위의 모니터링 솔루션으로, 데이터 품질과 모델 성능을 자동으로 추적합니다.

| 모니터링 유형 | 대상 | 감지 항목 |
|--------------|------|----------|
| **Snapshot** | 정적 테이블 (현재 상태) | 프로필 통계, 컬럼별 분포 |
| **TimeSeries** | 시계열 데이터 | 시간에 따른 분포 변화 (Drift) |
| **InferenceLog** | 모델 추론 결과 테이블 | 예측 분포 변화, 입력 드리프트, 모델 성능 지표 |

**드리프트 감지 메커니즘**: Lakehouse Monitoring은 단순 통계 비교를 넘어, 통계적 검정(statistical test)에 기반한 체계적인 드리프트 감지를 수행합니다.

| 데이터 유형 | 검정 방법 | 의미 |
|------------|----------|------|
| **수치형** | KS 검정 (Kolmogorov-Smirnov) | 두 분포 간 최대 차이를 측정. p-value < 0.05이면 분포가 유의하게 변화 |
| **범주형** | 카이제곱 검정 (Chi-squared) | 범주별 빈도 분포의 차이를 측정 |
| **공통** | Jensen-Shannon Divergence | 두 확률 분포 간 거리를 0~1 사이 값으로 수치화 |

Lakehouse Monitoring이 생성하는 **두 개의 출력 테이블** 을 이해하는 것이 중요합니다.

| 출력 테이블 | 내용 | 활용 |
|-----------|------|------|
| **Profile Metrics Table** | 각 윈도우(시간 구간)별 컬럼 프로파일 (평균, 분산, null 비율, 분포 등) | 시간에 따른 데이터 품질 추이 확인 |
| **Drift Metrics Table** | 현재 윈도우 vs 기준(baseline) 윈도우 간 드리프트 통계량 | 알림 설정, 재학습 트리거 조건으로 활용 |

이 테이블들은 일반 Delta 테이블이므로, SQL로 쿼리하거나 Databricks Jobs에서 드리프트 임계값을 확인하여 **재학습 파이프라인을 자동 트리거** 하는 것이 가능합니다.

Lakehouse Monitoring이 생성하는 **자동 대시보드** 에서는 다음을 확인할 수 있습니다.

- 각 컬럼의 분포 변화를 시각화한 히스토그램
- 드리프트 감지 통계량과 p-value
- 모델 성능 지표의 시간별 추이 (InferenceLog 프로필)

### Inference Table (추론 테이블)

Model Serving Endpoint에 **Inference Table** 을 활성화하면, 모든 요청(입력)과 응답(출력)이 자동으로 Delta 테이블에 기록됩니다.

| 기록 항목 | 설명 |
|-----------|------|
| **요청 본문** | 입력 피처 값 |
| **응답 본문** | 모델 예측 결과 |
| **타임스탬프** | 요청 시각 |
| **레이턴시** | 응답 시간 |
| **모델 버전** | 어떤 모델 버전이 응답했는지 |
| **상태 코드** | 성공/실패 여부 |

이 테이블에 Lakehouse Monitoring의 InferenceLog 프로필을 연결하면, **실시간 추론 모니터링 파이프라인** 이 완성됩니다.

{% hint style="info" %}
Inference Table의 데이터는 **Ground Truth 라벨링** 에도 활용됩니다. 시간이 지나 실제 결과가 확인되면, Inference Table에 라벨을 조인하여 모델의 실제 성능을 계산할 수 있습니다.
{% endhint %}

---

## 7. GenAI & Agent 기능

### Foundation Model APIs

앞서 5장에서 설명한 Foundation Model APIs는 GenAI 워크로드의 기반이 됩니다. 추가로 GenAI 특화 기능을 정리합니다.

| 기능 | 설명 |
|------|------|
| **Chat Completions** | 대화형 LLM 호출 (system/user/assistant 메시지) |
| **Embeddings** | 텍스트를 벡터로 변환 (RAG, 유사도 검색용) |
| **Completions** | 텍스트 생성 (레거시 API) |

### Vector Search

**왜 필요한가**: RAG(검색 증강 생성) 파이프라인에서 관련 문서를 빠르게 검색하려면 벡터 유사도 검색이 필수입니다. 별도의 벡터 DB(Pinecone, Weaviate 등)를 운영하면 **데이터 이중 관리** 문제가 발생합니다 -- 원본 문서가 업데이트되면 벡터 DB도 수동으로 동기화해야 하고, 삭제된 문서의 임베딩이 남아 "유령 검색 결과"를 반환하는 문제가 생깁니다.

Databricks **Vector Search** 는 Delta 테이블을 **Single Source of Truth** 로 유지하면서 자동 동기화되는 벡터 인덱스를 제공합니다. 원본 Delta 테이블에서 행이 추가/수정/삭제되면 인덱스가 자동으로 반영되므로, 데이터 정합성이 보장됩니다.

| 인덱스 유형 | 설명 |
|-------------|------|
| **Delta Sync Index** | Delta 테이블의 변경 사항을 자동으로 임베딩하고 인덱싱. 소스 테이블이 업데이트되면 인덱스도 자동 업데이트 |
| **Direct Vector Access Index** | 사전 계산된 임베딩 벡터를 직접 업로드. 커스텀 임베딩 파이프라인 사용 시 적합 |

Delta Sync Index는 두 가지 모드를 지원합니다.

| 모드 | 동작 |
|------|------|
| **Managed Embeddings** | 소스 텍스트 컬럼을 지정하면 Databricks가 자동으로 임베딩 생성 |
| **Self-managed Embeddings** | 사용자가 미리 계산한 임베딩 컬럼을 사용 |

### Agent Framework (ChatAgent)

Databricks **Agent Framework** 는 LLM 기반 AI Agent를 개발, 테스트, 배포하기 위한 통합 프레임워크입니다.

**ChatAgent 인터페이스가 왜 중요한가**: MLflow 3.0에서 도입된 `ChatAgent`는 Agent 생태계의 **표준 계약(contract)** 역할을 합니다. 기존에는 LangChain으로 만든 Agent, LlamaIndex로 만든 Agent, 순수 Python Agent가 각각 다른 입출력 형식을 가져서, 배포/평가/모니터링 도구를 프레임워크별로 따로 만들어야 했습니다.

ChatAgent는 **OpenAI Chat Completions 형식** (`messages` 리스트, `role`/`content` 구조)을 표준으로 채택하여, 어떤 프레임워크로 내부를 구현하든 동일한 인터페이스로 배포하고 평가할 수 있게 합니다. 이 덕분에 다음이 가능해집니다.

- **프레임워크 교체 투명성**: LangChain에서 순수 Python으로 Agent 내부를 교체해도 배포 엔드포인트, 평가 코드, UI가 변경 없이 동작
- **통합 평가**: `mlflow.evaluate()`가 모든 ChatAgent에 동일하게 적용
- **AI Playground 호환**: ChatAgent 인터페이스를 구현한 Agent는 AI Playground에서 즉시 테스트 가능
- **Streaming 지원**: `predict_stream()` 메서드를 구현하면 토큰 단위 스트리밍 응답 자동 지원

| 구성 요소 | 역할 |
|-----------|------|
| **ChatAgent 인터페이스** | Agent의 표준 입출력 인터페이스. `predict(messages)` + `predict_stream(messages)` 메서드 구현 |
| **Agent 도구 (Tools)** | Vector Search 검색, SQL 실행, Genie Space 질의 등 Agent가 사용하는 도구. UC Function으로도 정의 가능 |
| **MLflow를 통한 로깅** | Agent를 MLflow 모델로 기록하여 버전 관리 및 배포 |
| **Model Serving 배포** | Agent를 REST API 엔드포인트로 배포. Review App으로 SME 피드백 수집 가능 |

```python
import mlflow
from databricks.agents import ChatAgent

class MyRAGAgent(ChatAgent):
    def predict(self, messages, context=None):
        # 1. 사용자 질문에서 검색 쿼리 추출
        query = messages[-1]["content"]

        # 2. Vector Search로 관련 문서 검색
        docs = vector_search.similarity_search(query, num_results=5)

        # 3. LLM에 컨텍스트와 함께 질문
        response = llm.chat(
            system="검색된 문서를 기반으로 답변하세요.",
            context=docs,
            question=query
        )
        return response

# Agent를 MLflow에 기록
with mlflow.start_run():
    mlflow.pyfunc.log_model("agent", python_model=MyRAGAgent())
```

### Agent Evaluation (MLflow 기반)

Agent의 품질을 객관적으로 측정하기 위한 **mlflow.evaluate()** 기반 평가 프레임워크입니다. 단순히 메트릭 숫자를 보여주는 것을 넘어, **어떤 기준으로 왜 그 점수가 나왔는지** 를 추적할 수 있는 체계적인 Scorer 시스템을 제공합니다.

**Scorer 시스템**: Agent Evaluation은 **내장 Scorer(Built-in Scorer)** 와 **커스텀 Scorer** 를 조합하여 평가합니다. 각 Scorer는 독립적으로 동작하여, 필요한 평가 항목만 선택적으로 사용할 수 있습니다.

아래 표는 주요 내장 Scorer의 역할과 평가 방식을 정리한 것입니다.

| Scorer | 평가 대상 | 방식 | Ground Truth 필요 여부 |
|--------|----------|------|---------------------|
| **Correctness** | 답변이 정답(expected_response)과 의미적으로 일치하는지 | LLM Judge | 필요 |
| **Groundedness** | 답변이 검색된 문서(retrieved_context)에 근거하는지 | LLM Judge | 불필요 |
| **Relevance** | 검색된 문서가 질문과 관련 있는지 | LLM Judge | 불필요 |
| **Safety** | 답변에 유해하거나 부적절한 내용이 포함되었는지 | LLM Judge | 불필요 |
| **Chunk Relevance** | 검색된 각 청크(chunk)가 개별적으로 관련 있는지 | LLM Judge | 불필요 |
| **Latency** | 응답 시간 (초 단위) | 측정 | 불필요 |
| **Token Count** | 입출력 토큰 사용량 | 측정 | 불필요 |

평가는 **LLM-as-a-Judge** 방식으로 자동화됩니다. Databricks가 제공하는 강력한 Judge LLM이 Agent의 답변을 채점하며, 각 점수에 대한 **이유(rationale)** 도 함께 반환하여 디버깅이 가능합니다.

```python
import mlflow

results = mlflow.evaluate(
    model="runs:/abc123/agent",
    data=eval_dataset,            # 질문 + (선택) 정답 + (선택) 검색 문서
    model_type="databricks-agent"  # Agent 전용 평가 모드 활성화
)

# 전체 메트릭 확인
print(results.metrics)

# 개별 행 단위 상세 결과 (점수 + 이유)
display(results.tables["eval_results"])
```

{% hint style="info" %}
Ground Truth가 없는 초기 단계에서도 **Groundedness, Relevance, Safety** 는 평가 가능합니다. 이후 사용자 피드백이나 SME 리뷰를 통해 Ground Truth를 점진적으로 구축하면 Correctness 평가를 추가할 수 있습니다.
{% endhint %}

### AI Playground

**AI Playground** 는 Databricks UI에서 다양한 LLM을 즉시 테스트할 수 있는 대화형 인터페이스입니다. Foundation Model APIs, External Models, 파인튜닝한 커스텀 모델 등 Model Serving에 배포된 모든 모델을 별도 코드 없이 비교 테스트할 수 있습니다.

| 활용 시나리오 | 설명 |
|--------------|------|
| **모델 비교** | 동일 프롬프트로 여러 모델의 응답 품질을 나란히 비교 |
| **프롬프트 튜닝** | System prompt, temperature 등을 실시간으로 조정하며 최적 설정 탐색 |
| **Tool Use 테스트** | Agent 도구(Function) 호출 동작 확인 |
| **프로토타이핑** | 코드 없이 빠르게 PoC 수준의 대화 흐름 검증 |

---

## 8. MLOps 파이프라인

### Databricks Jobs (스케줄링)

ML 모델을 프로덕션에서 운영하려면, 데이터 수집 → 피처 엔지니어링 → 학습 → 평가 → 배포라는 파이프라인이 **자동으로 반복 실행** 되어야 합니다.

Databricks **Jobs** 는 노트북, Python 스크립트, JAR 등을 DAG(방향 비순환 그래프) 형태로 연결하고 스케줄링하는 워크플로 오케스트레이터입니다.

| 기능 | 설명 |
|------|------|
| **멀티태스크 워크플로** | 여러 태스크를 순차/병렬로 구성 |
| **트리거 방식** | Cron 스케줄, API 트리거, 파일 도착 트리거 |
| **조건부 실행** | 이전 태스크 결과에 따라 분기 (if/else) |
| **파라미터 전달** | 태스크 간 파라미터 전달 (`dbutils.jobs.taskValues`) |
| **재시도 정책** | 태스크 실패 시 자동 재시도 설정 |
| **알림** | 성공/실패 시 이메일, Slack 알림 |
| **서버리스** | Serverless Compute로 클러스터 관리 없이 실행 |

### Databricks Asset Bundles (CI/CD)

**왜 등장했는가**: ML 파이프라인을 Git 기반으로 관리하고 개발/스테이징/프로덕션 환경을 분리하여 배포하려면 Infrastructure as Code 도구가 필요합니다.

**Databricks Asset Bundles (DABs)** 는 Databricks 리소스(Jobs, Pipelines, Model Serving 등)를 YAML 파일로 정의하고 CLI로 배포하는 IaC 도구입니다.

```yaml
# databricks.yml 예시
bundle:
  name: fraud-detection-pipeline

resources:
  jobs:
    training_job:
      name: "fraud-detection-training"
      tasks:
        - task_key: feature_engineering
          notebook_task:
            notebook_path: ./notebooks/01_feature_engineering.py
        - task_key: model_training
          depends_on:
            - task_key: feature_engineering
          notebook_task:
            notebook_path: ./notebooks/02_model_training.py

targets:
  dev:
    workspace:
      host: https://dev-workspace.cloud.databricks.com
  prod:
    workspace:
      host: https://prod-workspace.cloud.databricks.com
    run_as:
      service_principal_name: "ml-pipeline-sp"
```

```bash
# CLI로 배포
databricks bundle deploy --target prod
databricks bundle run training_job --target prod
```

### 전체 MLOps 워크플로

아래 표는 Databricks에서의 전체 MLOps 워크플로를 단계별로 정리한 것입니다.

| 단계 | 환경 | 활동 | Databricks 기능 |
|------|------|------|----------------|
| **1. 개발** | Dev Workspace | 탐색적 분석, 피처 엔지니어링, 모델 프로토타이핑 | Notebooks, AutoML, MLflow Experiment |
| **2. 코드 관리** | Git (GitHub/Azure DevOps) | 코드 리뷰, 버전 관리 | Git Integration, Repos |
| **3. 테스트** | Staging Workspace | 단위 테스트, 통합 테스트, 모델 검증 | DABs (`--target staging`), pytest |
| **4. 등록** | Unity Catalog | 검증된 모델을 레지스트리에 등록 | UC Model Registry, Alias |
| **5. 배포** | Prod Workspace | 서빙 엔드포인트 업데이트, 배치 추론 스케줄링 | Model Serving, Jobs |
| **6. 모니터링** | Prod Workspace | 데이터/모델 드리프트 감지, 알림 | Lakehouse Monitoring, Inference Table |
| **7. 재학습** | Prod Workspace | 드리프트 감지 시 자동 재학습 트리거 | Jobs (API 트리거), Webhooks |

이 워크플로를 관통하는 핵심 원칙은 **환경 분리** (Dev/Staging/Prod), **코드 기반 관리** (Git + DABs), **자동화** (Jobs + 트리거)입니다.

{% hint style="warning" %}
MLOps 워크플로의 성숙도는 조직마다 다릅니다. 처음에는 수동 배포(Level 0)로 시작하고, 점진적으로 CI/CD 자동화(Level 1), 자동 재학습(Level 2)으로 발전시키는 것이 현실적입니다.
{% endhint %}

---

## 9. Databricks ML 기능 매핑 테이블

아래 표는 ML 라이프사이클의 각 단계에서 사용되는 Databricks 기능을 한눈에 보여줍니다. 새로운 ML 프로젝트를 시작할 때 이 표를 참고하여 필요한 기능을 빠르게 파악할 수 있습니다.

| ML 라이프사이클 단계 | Databricks 기능 | 카테고리 | 비고 |
|---------------------|----------------|---------|------|
| **데이터 저장** | Delta Lake, Unity Catalog | 플랫폼 기반 | Lakehouse의 기반 |
| **데이터 탐색** | Notebooks, SQL Editor, AI/BI Dashboard | 분석 | EDA, 시각화 |
| **피처 엔지니어링** | Feature Engineering in UC | 데이터 준비 | Feature Table + Feature Function |
| **피처 서빙** | Online Tables | 데이터 준비 | 실시간 피처 조회 |
| **자동 ML** | AutoML | 학습 | 투명한 노트북 생성 |
| **모델 학습** | Runtime ML, GPU Clusters | 학습 | 사전 설치 라이브러리 |
| **분산 학습** | TorchDistributor, Horovod, DeepSpeed | 학습 | Spark 클러스터 활용 |
| **실험 관리** | MLflow Tracking | 실험 | 파라미터, 메트릭, 아티팩트 |
| **모델 레지스트리** | Unity Catalog Models | 거버넌스 | 3-level 네임스페이스, Alias |
| **실시간 추론** | Model Serving Endpoints | 배포 | 오토스케일링, A/B 테스트 |
| **배치 추론** | Spark UDF, Jobs | 배포 | 대규모 병렬 처리 |
| **LLM 호출** | Foundation Model APIs | GenAI | Pay-per-token, Provisioned |
| **외부 LLM** | External Models (AI Gateway) | GenAI | 거버넌스, 비용 추적 |
| **벡터 검색** | Vector Search | GenAI | Delta Sync, RAG 기반 |
| **AI Agent** | Agent Framework (ChatAgent) | GenAI | 개발 → 평가 → 배포 |
| **Agent 평가** | MLflow Evaluate | GenAI | LLM-as-a-Judge |
| **LLM 테스트** | AI Playground | GenAI | 코드 없이 모델 비교 |
| **모델 모니터링** | Lakehouse Monitoring | 운영 | 드리프트 감지, 자동 대시보드 |
| **추론 로깅** | Inference Tables | 운영 | 요청/응답 자동 기록 |
| **워크플로 관리** | Jobs (Workflows) | MLOps | DAG, 스케줄링, 트리거 |
| **CI/CD** | Asset Bundles (DABs) | MLOps | YAML 기반 IaC |
| **앱 배포** | Databricks Apps | 배포 | Streamlit/FastAPI 호스팅 |

---

## 10. 한계와 트레이드오프

모든 플랫폼에는 제약이 있으며, Databricks ML/AI도 예외는 아닙니다. 아래 표는 주요 고려사항을 정리한 것입니다.

| 고려사항 | 설명 | 대안/완화 방법 |
|---------|------|---------------|
| **벤더 종속** | Databricks 전용 기능(AutoML, Feature Store UI 등) 사용 시 이식성 감소 | MLflow는 오픈소스이므로 모델/실험은 이식 가능 |
| **비용** | GPU 클러스터, Model Serving은 비용이 높을 수 있음 | Spot 인스턴스, Scale-to-zero, Serverless 활용 |
| **실시간 학습** | 온라인 학습(실시간 모델 업데이트)은 네이티브 지원 미흡 | Structured Streaming + 주기적 재학습으로 대체 |
| **엣지 배포** | 온프레미스/엣지 디바이스 배포는 직접 지원하지 않음 | MLflow 모델을 export하여 별도 서빙 인프라에 배포 |
| **커스텀 서빙** | 복잡한 전/후처리 로직이 필요한 경우 서빙 제약 | Custom Container 또는 Databricks Apps로 해결 |
| **소규모 팀** | 전체 MLOps 파이프라인 구축은 소규모 팀에게 과한 투자일 수 있음 | AutoML + 수동 배포로 시작, 점진적으로 자동화 |

이 한계를 이해하고 프로젝트 요구사항에 맞는 기능을 선택적으로 도입하는 것이 중요합니다.

---

## 다음 단계

- **Classic ML 실습**: [예지보전 & 이상탐지 MLOps 핸즈온](../../hands-on/predictive-maintenance/README.md) — 전체 MLOps 파이프라인을 직접 구축
- **GenAI 이론**: [GenAI 핵심 개념](../genai-concepts/README.md) — LLM, Agent, Prompt Engineering 이론
- **RAG 구축**: [RAG 가이드](../rag/README.md) — Vector Search + Agent 실전 구축
- **ML 알고리즘**: [ML 트렌드 & 최신 기법](ml-trends.md) — 알고리즘 선택, 앙상블, 이상탐지 기법
- **모델 운영**: [재학습 전략](retraining-strategies.md) — Drift 감지, 재학습 자동화 전략
