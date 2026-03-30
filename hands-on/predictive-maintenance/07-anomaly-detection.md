# 07. 비정형 이상탐지 (Anomalib PatchCore)

> **전체 노트북 코드**: [07_unstructured_anomaly_detection.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/07_unstructured_anomaly_detection.py)


**목적**: MVTec AD 이미지 데이터로 PatchCore 비지도 학습 기반 이상탐지 모델을 학습하고, 이상 위치를 히트맵으로 시각화합니다.

**사용 Databricks 기능**: `Volumes` (이미지 관리), `GPU Cluster`, `MLflow` 아티팩트 추적, `UC Model Registry`

---

## PatchCore 모델 원리

- **비지도 학습**: 정상 이미지만으로 학습 (이상 데이터 불필요)
- 사전학습된 CNN(ResNet)의 중간 레이어 피처를 패치 단위로 추출
- 메모리 뱅크에 정상 패턴을 저장하고, 테스트 시 거리 기반 이상 점수 산출

{% hint style="warning" %}
이 노트북은 **GPU 클러스터** (g5.2xlarge 또는 g4dn.2xlarge)에서 실행해야 합니다.
{% endhint %}

## 1. MVTec AD 데이터 모듈 설정

Anomalib은 MVTec AD 데이터셋을 자동 다운로드하며, 이미지는 **Unity Catalog Volume**에 저장됩니다.

```python
from anomalib.data import MVTec

datamodule = MVTec(
    root=f"/Volumes/{catalog}/{db}/lgit_images/mvtec_ad",
    category="bottle",        # 15개 카테고리 중 선택
    image_size=(256, 256),
    train_batch_size=32,
    eval_batch_size=32,
    num_workers=4,
)
datamodule.prepare_data()
datamodule.setup()
print(f"학습: {len(datamodule.train_data)}장 (정상만), 테스트: {len(datamodule.test_data)}장")
```

## 2. PatchCore 모델 학습

PatchCore는 피처 추출 기반이므로 **1 epoch만** 학습하면 됩니다.

```python
from anomalib.models import Patchcore
from anomalib.engine import Engine

with mlflow.start_run(run_name=f"patchcore_bottle") as run:
    mlflow.log_params({
        "model": "PatchCore", "backbone": "wide_resnet50_2",
        "category": "bottle", "coreset_sampling_ratio": 0.1,
    })

    model = Patchcore(
        backbone="wide_resnet50_2",
        layers_to_extract=["layer2", "layer3"],
        coreset_sampling_ratio=0.1,
    )

    engine = Engine(max_epochs=1, accelerator="auto", devices=1)
    engine.fit(model=model, datamodule=datamodule)
    test_results = engine.test(model=model, datamodule=datamodule)

    # 메트릭 기록 (AUROC 등)
    for metric_name, metric_value in test_results[0].items():
        if isinstance(metric_value, (int, float)):
            mlflow.log_metric(metric_name.replace("/", "_"), metric_value)
```

## 3. Unity Catalog에 비정형 모델 등록

비정형 모델도 정형 모델과 **동일한 UC 거버넌스 체계**로 관리합니다.

```python
unstructured_model_name = f"{catalog}.{db}.lgit_anomaly_detection"

model_details = mlflow.register_model(
    model_uri=f"runs:/{run.info.run_id}/model",
    name=unstructured_model_name
)

client.update_registered_model(
    name=unstructured_model_name,
    description="""비전 기반 이상탐지 모델. PatchCore (Anomalib).
    입력: 제품 표면 이미지 (256x256). 출력: 이상 점수, 이상 위치 히트맵"""
)

client.set_registered_model_alias(
    name=unstructured_model_name, alias="Champion", version=model_details.version
)
```

{% hint style="success" %}
비정형 모델도 정형 모델과 **동일한 Unity Catalog 거버넌스** 체계로 관리됩니다. 에일리어스, 태그, 접근 제어 모두 통일된 방식으로 적용됩니다.
{% endhint %}

{% hint style="info" %}
**모델 선택 가이드** — 정확도 우선이면 PatchCore(AUROC 99.1%), 속도/비용 우선이면 EfficientAD, 실시간 추론이면 Reverse Distillation을 권장합니다.
{% endhint %}

**다음 단계**: [08. 모델 모니터링](08-model-monitoring.md)
