# Databricks notebook source
# MAGIC %md
# MAGIC # 비정형 이상탐지: MVTec AD + Anomalib PatchCore
# MAGIC
# MAGIC 본 노트북에서는 **제품 표면 이미지** 기반의 이상탐지 모델을 학습합니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC - **Volumes**: 비정형 데이터(이미지) 관리
# MAGIC - **GPU Cluster**: 딥러닝 모델 학습 (g5.2xlarge / g4dn.2xlarge)
# MAGIC - **MLflow**: 비정형 모델의 실험 추적 및 아티팩트 관리
# MAGIC - **Unity Catalog**: 이미지 모델도 동일한 거버넌스 체계로 관리
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 데이터: MVTec AD
# MAGIC | 항목 | 상세 |
# MAGIC |------|------|
# MAGIC | 데이터셋 | MVTec AD — Industrial Inspection 벤치마크 |
# MAGIC | 카테고리 | bottle (데모용, 15개 중 1개 선택) |
# MAGIC | 구조 | 정상 이미지로 학습, 이상 이미지로 테스트 |
# MAGIC | 출력 | 정상/이상, 이상 점수, 이상 위치 heatmap |
# MAGIC
# MAGIC ### 모델: Anomalib PatchCore
# MAGIC - **비지도 학습** 기반: 정상 데이터만으로 학습
# MAGIC - 사전학습된 CNN(ResNet)의 중간 레이어 피처를 패치 단위로 추출
# MAGIC - 메모리 뱅크에 정상 패턴을 저장하고, 테스트 시 거리 기반 이상 점수 산출
# MAGIC
# MAGIC > **참고**: 이 노트북은 **GPU 클러스터** (g5.2xlarge 또는 g4dn.2xlarge)에서 실행해야 합니다.

# COMMAND ----------

# MAGIC %pip install --quiet anomalib mlflow torchvision lightning --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 데이터 준비: MVTec AD 다운로드
# MAGIC
# MAGIC Anomalib은 MVTec AD 데이터셋을 자동으로 다운로드하는 기능을 제공합니다.
# MAGIC 다운로드된 이미지는 **Unity Catalog Volume**에 저장하여 중앙 관리합니다.

# COMMAND ----------

# DBTITLE 1,MVTec AD 데이터 모듈 설정
import os
import torch
import mlflow

# Volume 경로 설정
volume_path = f"/Volumes/{catalog}/{db}/lgit_images"
data_path = f"{volume_path}/mvtec_ad"
os.makedirs(data_path, exist_ok=True)

# GPU 확인
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"디바이스: {device}")
if device == "cpu":
    print("경고: GPU가 없습니다. CPU에서 실행되며 속도가 느릴 수 있습니다.")

# COMMAND ----------

# DBTITLE 1,Anomalib 데이터 모듈 생성
from anomalib.data import MVTec

# MVTec AD 'bottle' 카테고리 사용 (데모용)
# 다른 카테고리: carpet, grid, leather, tile, wood, cable, capsule, hazelnut, metal_nut, pill, screw, toothbrush, transistor, zipper
CATEGORY = "bottle"

datamodule = MVTec(
    root=data_path,
    category=CATEGORY,
    image_size=(256, 256),
    train_batch_size=32,
    eval_batch_size=32,
    num_workers=4,
)

datamodule.prepare_data()
datamodule.setup()

print(f"카테고리: {CATEGORY}")
print(f"학습 이미지: {len(datamodule.train_data)} 장 (정상만)")
print(f"테스트 이미지: {len(datamodule.test_data)} 장 (정상 + 이상)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. PatchCore 모델 학습
# MAGIC
# MAGIC **PatchCore**는 비지도 학습 기반의 이상탐지 모델입니다.
# MAGIC - 정상 이미지의 피처를 추출하여 메모리 뱅크에 저장
# MAGIC - 테스트 시 새로운 이미지의 피처와 메모리 뱅크 간 거리를 계산
# MAGIC - 거리가 큰 영역 = 이상 (Anomaly)

# COMMAND ----------

# DBTITLE 1,MLflow 실험 설정
xp_name = "lgit_anomaly_detection"
xp_path = f"/Users/{current_user}"
experiment_name = f"{xp_path}/{xp_name}"

try:
    experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
except:
    experiment_id = mlflow.create_experiment(
        name=experiment_name,
        tags={"project": "lgit-mlops-poc", "domain": "anomaly-detection"}
    )

mlflow.set_experiment(experiment_name)
print(f"실험: {experiment_name}")

# COMMAND ----------

# DBTITLE 1,PatchCore 모델 학습
from anomalib.models import Patchcore
from anomalib.engine import Engine
from lightning.pytorch.callbacks import ModelCheckpoint

with mlflow.start_run(run_name=f"patchcore_{CATEGORY}") as run:
    # 하이퍼파라미터 기록
    mlflow.log_params({
        "model": "PatchCore",
        "backbone": "wide_resnet50_2",
        "category": CATEGORY,
        "image_size": 256,
        "coreset_sampling_ratio": 0.1,
    })

    # PatchCore 모델 생성
    model = Patchcore(
        backbone="wide_resnet50_2",
        layers_to_extract=["layer2", "layer3"],
        coreset_sampling_ratio=0.1,
    )

    # Engine으로 학습 (Anomalib의 학습 인터페이스)
    engine = Engine(
        max_epochs=1,  # PatchCore는 1 epoch만 필요 (피처 추출)
        accelerator="auto",
        devices=1,
        default_root_dir=f"{volume_path}/anomalib_results",
    )

    engine.fit(model=model, datamodule=datamodule)

    # 테스트 수행
    test_results = engine.test(model=model, datamodule=datamodule)

    # 메트릭 기록
    if test_results:
        for metric_name, metric_value in test_results[0].items():
            if isinstance(metric_value, (int, float)):
                mlflow.log_metric(metric_name.replace("/", "_"), metric_value)
                print(f"  {metric_name}: {metric_value:.4f}")

    # 모델 아티팩트 저장
    model_path = f"{volume_path}/anomalib_results/patchcore_{CATEGORY}"
    os.makedirs(model_path, exist_ok=True)

    # 모델 상태 저장
    torch.save(model.state_dict(), f"{model_path}/model.pth")
    mlflow.log_artifact(f"{model_path}/model.pth", "model")

    print(f"\nRun ID: {run.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 이상탐지 결과 시각화
# MAGIC
# MAGIC 테스트 이미지에 대한 이상 점수 및 **히트맵(Heatmap)** 을 시각화합니다.

# COMMAND ----------

# DBTITLE 1,이상탐지 결과 시각화
import matplotlib.pyplot as plt
import numpy as np
from torchvision.utils import make_grid

# 테스트 데이터에서 예측 수행
model.eval()
predictions = engine.predict(model=model, datamodule=datamodule)

# 시각화: 원본 이미지 + 이상 히트맵
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
fig.suptitle(f"MVTec AD - {CATEGORY}: 이상탐지 결과", fontsize=14)

test_dl = datamodule.test_dataloader()
batch = next(iter(test_dl))

for i in range(min(4, len(batch["image"]))):
    # 원본 이미지
    img = batch["image"][i].permute(1, 2, 0).cpu().numpy()
    img = (img - img.min()) / (img.max() - img.min())
    axes[0][i].imshow(img)
    label = "이상" if batch["label"][i].item() == 1 else "정상"
    axes[0][i].set_title(f"원본 ({label})")
    axes[0][i].axis("off")

    # 이상 히트맵 (anomaly_map이 있는 경우)
    if "anomaly_maps" in batch:
        heatmap = batch["anomaly_maps"][i].squeeze().cpu().numpy()
        axes[1][i].imshow(img)
        axes[1][i].imshow(heatmap, cmap="jet", alpha=0.5)
        axes[1][i].set_title("이상 히트맵")
    else:
        axes[1][i].imshow(img)
        axes[1][i].set_title("히트맵 (학습 후 생성)")
    axes[1][i].axis("off")

plt.tight_layout()

# MLflow에 시각화 기록
with mlflow.start_run(run_id=run.info.run_id):
    mlflow.log_figure(fig, "anomaly_detection_results.png")

plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Unity Catalog에 모델 등록
# MAGIC
# MAGIC 비정형 모델도 정형 모델과 동일한 **Unity Catalog 거버넌스** 체계로 관리합니다.

# COMMAND ----------

# DBTITLE 1,비정형 모델 UC 등록
from mlflow import MlflowClient

unstructured_model_name = f"{catalog}.{db}.lgit_anomaly_detection"
client = MlflowClient()

# 모델 등록
model_details = mlflow.register_model(
    model_uri=f"runs:/{run.info.run_id}/model",
    name=unstructured_model_name
)

# 메타데이터 추가
client.update_registered_model(
    name=unstructured_model_name,
    description=f"""LG Innotek 비전 기반 이상탐지 모델.
    모델: PatchCore (Anomalib)
    데이터: MVTec AD - {CATEGORY} 카테고리
    입력: 제품 표면 이미지 (256x256)
    출력: 이상 점수, 이상/정상 분류, 이상 위치 히트맵"""
)

# Champion 에일리어스 설정
client.set_registered_model_alias(
    name=unstructured_model_name,
    alias="Champion",
    version=model_details.version
)

print(f"모델 등록 완료: {unstructured_model_name} v{model_details.version} (@Champion)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC 이 노트북에서 수행한 작업:
# MAGIC 1. **MVTec AD** 이미지 데이터 다운로드 및 **Volume** 저장
# MAGIC 2. **Anomalib PatchCore** 모델 학습 (비지도 학습)
# MAGIC 3. 이상탐지 결과 **히트맵** 시각화
# MAGIC 4. MLflow로 메트릭/아티팩트 추적
# MAGIC 5. **Unity Catalog** 에 모델 등록 (정형 모델과 동일한 거버넌스)
# MAGIC
# MAGIC **다음 단계:** [모델 모니터링]($./08_model_monitoring)
