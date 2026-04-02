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
이 노트북은 **GPU 클러스터**(g5.2xlarge 또는 g4dn.2xlarge)에서 실행해야 합니다.
{% endhint %}

## 1. MVTec AD 데이터 모듈 설정

Anomalib은 MVTec AD 데이터셋을 자동 다운로드하며, 이미지는 **Unity Catalog Volume** 에 저장됩니다.

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

비정형 모델도 정형 모델과 **동일한 UC 거버넌스 체계** 로 관리합니다.

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
**모델 선택 가이드**— 정확도 우선이면 PatchCore(AUROC 99.1%), 속도/비용 우선이면 EfficientAD, 실시간 추론이면 Reverse Distillation을 권장합니다.
{% endhint %}

---

## 4. Anomalib 모델 비교 및 최신 트렌드

> **전체 노트북 코드**: [07_unstructured_anomaly_detection.py (Section 8)](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/07_unstructured_anomaly_detection.py)

### Anomalib 지원 모델 비교

Anomalib은 PatchCore 외에도 **20개 이상의 이상탐지 알고리즘** 을 제공합니다. 동일한 코드 구조에서 **모델 클래스만 교체** 하면 즉시 비교 실험이 가능합니다.

| 모델 | 정확도 (AUROC) | 추론 속도 | 메모리 | 적합 시나리오 |
|------|---------------|----------|--------|-------------|
| **PatchCore** | 99.1% | 보통 | 높음 | 정확도 최우선 (오프라인 배치 검사) |
| **EfficientAD** | 98.8% | 가장 빠름 | 가장 낮음 | 실시간 인라인 검사 / 엣지 디바이스 |
| **Reverse Distillation** | 98.5% | 빠름 | 낮음 | 속도-정확도 균형이 필요한 경우 |
| **PADIM** | 97.9% | 빠름 | 보통 | 빠른 PoC / 프로토타이핑 |
| **FastFlow** | 98.4% | 빠름 | 보통 | Normalizing Flow 기반 (확률적 해석 필요 시) |

```python
# 모델 교체 예시 — 코드 한 줄만 변경
from anomalib.models import EfficientAd
model = EfficientAd()  # PatchCore 대신 EfficientAD
# 나머지 코드(학습, 평가, 등록)는 완전히 동일!
```

{% hint style="info" %}
**모델 선택 가이드**: PoC 단계에서는 **PatchCore**(정확도 최고)로 시작하고, 양산 적용 시 추론 속도 요구사항에 따라 **EfficientAD**(실시간) 또는 **Reverse Distillation**(균형)으로 전환을 검토합니다.
{% endhint %}

### VisA 데이터셋 — 전자부품 검사용

MVTec AD 외에 **VisA (Visual Anomaly)** 데이터셋은 PCB 보드 4종(pcb1~pcb4)을 포함하여 전자부품 검사에 특화되어 있습니다.

```python
# MVTec AD 대신 VisA 사용 (PCB 보드 4종 포함!)
from anomalib.data import Visa

datamodule = Visa(
    root="/Volumes/catalog/schema/volume/visa",
    category="pcb1",  # pcb1, pcb2, pcb3, pcb4 — 전자부품 특화!
    image_size=(256, 256),
)
# 나머지 코드는 완전히 동일하게 사용 가능
```

### Foundation Model 기반 이상탐지 (2023-2025 트렌드)

최근 AI 분야의 가장 큰 변화인 **Foundation Model(기반 모델)** 이 이상탐지에도 적용되고 있습니다.

| 기술 | 논문/년도 | 핵심 아이디어 | 장점 |
|------|----------|-------------|------|
| **WinCLIP** | 2023 | CLIP의 윈도우 기반 이상 탐지 | Zero-shot 가능 (학습 없이 텍스트로 결함 설명만 하면 탐지) |
| **AnomalyCLIP** | 2024 | CLIP을 이상탐지에 특화하여 Fine-tuning | 여러 도메인에 범용적으로 적용 가능 |
| **SAM + 이상탐지** | 2024 | Segment Anything Model로 결함 영역 정밀 분할 | 픽셀 수준 결함 경계 정확도 향상 |
| **AnomalyGPT** | 2024 | LLM + 비전 모델 결합, 대화형 이상 분석 | "이 결함의 원인이 무엇인가?"에 텍스트로 답변 |

{% hint style="success" %}
Foundation Model 기반 접근은 아직 연구 단계이지만, 향후 "카메라 모듈에서 렌즈 스크래치를 찾아줘"라는 **자연어 지시만으로** 결함을 탐지하는 것이 가능해질 것입니다. Databricks의 GPU 클러스터와 MLflow 인프라가 이러한 최신 모델의 실험/배포를 지원합니다.
{% endhint %}

**다음 단계**: [08. 모델 모니터링](08-model-monitoring.md)
