# 07. 비정형 이상탐지 (Anomalib PatchCore)

**목적**: MVTec AD 이미지 데이터로 PatchCore 비지도 학습 기반 이상탐지 모델을 학습합니다.

**주요 개념**:
- PatchCore — 정상 이미지의 CNN 피처를 메모리 뱅크에 저장, 거리 기반 이상 점수 산출
- Unity Catalog Volumes — 이미지 데이터 중앙 관리
- GPU 클러스터 필수 (g5.2xlarge 권장)

**핵심 코드**:

```python
from anomalib.data import MVTec
from anomalib.models import Patchcore
from anomalib.engine import Engine

datamodule = MVTec(root=data_path, category="bottle", image_size=(256, 256))

model = Patchcore(
    backbone="wide_resnet50_2",
    layers_to_extract=["layer2", "layer3"],
    coreset_sampling_ratio=0.1,
)

engine = Engine(max_epochs=1, accelerator="auto")
engine.fit(model=model, datamodule=datamodule)
test_results = engine.test(model=model, datamodule=datamodule)
```

**사용 Databricks 기능**: Volumes (이미지 관리), GPU Cluster, MLflow 아티팩트 추적, UC 모델 등록

{% hint style="success" %}
비정형 모델도 정형 모델과 **동일한 Unity Catalog 거버넌스** 체계로 관리됩니다. 에일리어스, 태그, 접근 제어 모두 통일된 방식으로 적용됩니다.
{% endhint %}
