# Databricks notebook source
# MAGIC %md
# MAGIC # 비정형 이상탐지: 이미지 기반 제품 표면 검사
# MAGIC
# MAGIC 본 노트북에서는 **제품 표면 이미지**를 사용하여 **이상(결함)** 을 자동으로 탐지하는 모델을 학습합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 이 노트북에서 배우는 내용
# MAGIC
# MAGIC | 단계 | 내용 | Databricks 기능 |
# MAGIC |------|------|----------------|
# MAGIC | **데이터** | MVTec AD 이미지 데이터셋 다운로드 및 관리 | **Unity Catalog Volumes** |
# MAGIC | **탐색** | 정상/이상 이미지 시각화 및 분석 | 노트북 시각화 |
# MAGIC | **학습** | Anomalib PatchCore 모델 학습 | **GPU Cluster**, MLflow |
# MAGIC | **평가** | 이상 점수, 히트맵, AUROC 메트릭 | **MLflow Tracking** |
# MAGIC | **등록** | 모델을 Unity Catalog에 등록 | **UC Model Registry** |
# MAGIC | **추론** | 새 이미지에 대한 이상탐지 수행 | MLflow pyfunc |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 사전 지식: 비전 기반 이상탐지란?
# MAGIC
# MAGIC ### 왜 이미지 이상탐지가 필요한가?
# MAGIC
# MAGIC 제조 라인에서 사람의 눈으로 결함을 검사하는 것은:
# MAGIC - **느림**: 초당 수 개의 제품만 검사 가능
# MAGIC - **일관성 없음**: 피로도, 주관적 판단에 따라 결과가 달라짐
# MAGIC - **비용**: 숙련된 검사원 인건비
# MAGIC
# MAGIC AI 기반 비전 검사는:
# MAGIC - **빠름**: 초당 수백 개의 제품 검사 가능
# MAGIC - **일관성**: 24시간 동일한 기준으로 검사
# MAGIC - **확장 가능**: 라인 추가 시 카메라만 설치하면 됨
# MAGIC
# MAGIC ### 비지도 학습 기반 이상탐지
# MAGIC
# MAGIC ```
# MAGIC 일반 지도학습:                         비지도 이상탐지:
# MAGIC   정상 이미지 1000장  ┐                  정상 이미지 1000장 → 학습
# MAGIC   결함 이미지 1000장  ┘→ 학습             (결함 이미지 불필요!)
# MAGIC
# MAGIC   문제: 결함 이미지 수집이 어려움         장점: 정상 데이터만으로 학습 가능
# MAGIC         결함 유형이 다양하고 예측 불가     새로운 유형의 결함도 탐지 가능
# MAGIC ```
# MAGIC
# MAGIC **핵심 아이디어**: "정상이 어떤 것인지만 학습하고, 정상과 다르면 이상으로 판단"
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## PatchCore 알고리즘 설명
# MAGIC
# MAGIC **PatchCore**는 현재 산업용 이상탐지에서 **가장 높은 정확도**를 보이는 알고리즘입니다.
# MAGIC
# MAGIC ### 동작 원리
# MAGIC
# MAGIC ```
# MAGIC Step 1: 피처 추출 (Feature Extraction)
# MAGIC ┌──────────────┐     ┌─────────────┐     ┌──────────────────┐
# MAGIC │ 정상 이미지    │ ──→ │ 사전학습 CNN │ ──→ │ 중간 레이어 피처   │
# MAGIC │ (256×256)     │     │ (ResNet50)  │     │ (패치 단위 추출)  │
# MAGIC └──────────────┘     └─────────────┘     └──────────────────┘
# MAGIC
# MAGIC   - 사전학습된 ResNet50의 중간 레이어에서 패치(patch) 단위로 피처를 추출
# MAGIC   - 각 패치는 이미지의 작은 영역(예: 32×32 픽셀)의 특성을 담고 있음
# MAGIC
# MAGIC Step 2: 메모리 뱅크 구축 (Memory Bank)
# MAGIC ┌──────────────────┐     ┌──────────────────┐
# MAGIC │ 모든 정상 이미지의 │ ──→ │ Core-set 선택     │ ──→ 메모리 뱅크
# MAGIC │ 패치 피처 수집    │     │ (대표 샘플 선택)   │     (정상 패턴 사전)
# MAGIC └──────────────────┘     └──────────────────┘
# MAGIC
# MAGIC   - 정상 이미지에서 추출한 수만 개의 패치 피처를 수집
# MAGIC   - Core-set Sampling으로 대표적인 피처만 선택 (메모리 효율화)
# MAGIC   - 이것이 곧 "정상 패턴의 사전(Dictionary)"
# MAGIC
# MAGIC Step 3: 이상 탐지 (Anomaly Detection)
# MAGIC ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
# MAGIC │ 새 이미지     │ ──→ │ 피처 추출     │ ──→ │ 메모리 뱅크와     │
# MAGIC │ (테스트)      │     │ (동일 방식)   │     │ 거리(Distance) 계산│
# MAGIC └──────────────┘     └──────────────┘     └────────┬─────────┘
# MAGIC                                                     │
# MAGIC                                          거리가 크면 = 이상!
# MAGIC                                          거리가 작으면 = 정상
# MAGIC                                                     │
# MAGIC                                             ┌───────▼───────┐
# MAGIC                                             │ 이상 점수 맵    │
# MAGIC                                             │ (Anomaly Map)  │
# MAGIC                                             │ = 히트맵       │
# MAGIC                                             └───────────────┘
# MAGIC ```
# MAGIC
# MAGIC ### 왜 PatchCore가 좋은가?
# MAGIC - **학습 시간이 매우 짧음**: 1 epoch만 필요 (피처 추출 + 메모리 저장)
# MAGIC - **정확도 최고**: MVTec AD 벤치마크 AUROC 99.1%
# MAGIC - **새로운 결함 유형도 탐지**: 학습하지 않은 결함도 "정상과 다르다"는 것을 감지
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 데이터: MVTec AD
# MAGIC
# MAGIC | 항목 | 상세 |
# MAGIC |------|------|
# MAGIC | **이름** | MVTec Anomaly Detection Dataset |
# MAGIC | **카테고리** | 15종 (bottle, cable, capsule, carpet, grid, hazelnut, leather, metal_nut, pill, screw, tile, toothbrush, transistor, wood, zipper) |
# MAGIC | **규모** | 5,354 이미지 (학습 3,629 + 테스트 1,725) |
# MAGIC | **해상도** | 700×700 ~ 1024×1024 |
# MAGIC | **구조** | 학습: 정상 이미지만 / 테스트: 정상 + 이상 (픽셀 레벨 마스크 포함) |
# MAGIC | **라이선스** | CC BY-NC-SA 4.0 (연구/교육 목적) |
# MAGIC
# MAGIC > **참고**: LG Innotek 전자부품에 더 적합한 **VisA** 데이터셋(PCB 보드 4종 포함)도 Anomalib에서 지원합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC > **주의**: 이 노트북은 **GPU 클러스터** (g5.2xlarge 또는 g4dn.2xlarge)에서 실행해야 합니다.

# COMMAND ----------

# MAGIC %pip install --quiet anomalib mlflow torchvision lightning --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 환경 확인 및 데이터 준비
# MAGIC
# MAGIC ### GPU 확인
# MAGIC 딥러닝 모델 학습에는 GPU가 필요합니다.
# MAGIC Databricks에서는 GPU 클러스터를 생성하여 사용합니다.
# MAGIC
# MAGIC **권장 인스턴스**:
# MAGIC - 학습: `g5.2xlarge` (NVIDIA A10G, 24GB)
# MAGIC - 추론 (비용 절약): `g4dn.2xlarge` (NVIDIA T4, 16GB)

# COMMAND ----------

# DBTITLE 1,GPU 확인
import os
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_mem / 1e9
    print(f"GPU 사용 가능: {gpu_name} ({gpu_memory:.1f} GB)")
else:
    print("경고: GPU가 없습니다. CPU에서 실행됩니다 (속도 느림).")
    print("GPU 클러스터 (g5.2xlarge 등)로 전환을 권장합니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Unity Catalog Volumes
# MAGIC
# MAGIC **Volumes**은 Unity Catalog에서 **비정형 데이터(이미지, 오디오, 비디오 등)** 를 관리하는 기능입니다.
# MAGIC
# MAGIC ```
# MAGIC Unity Catalog 구조:
# MAGIC
# MAGIC Catalog (카탈로그)
# MAGIC  └── Schema (스키마)
# MAGIC       ├── Table (정형 데이터)     ← Delta Lake 테이블
# MAGIC       ├── Model (ML 모델)         ← MLflow 모델
# MAGIC       └── Volume (비정형 데이터)   ← 이미지, 파일 등 ★
# MAGIC
# MAGIC Volume 경로: /Volumes/{catalog}/{schema}/{volume_name}/
# MAGIC ```
# MAGIC
# MAGIC **장점**:
# MAGIC - 이미지도 정형 데이터와 **동일한 거버넌스** (권한, 감사, 계보)
# MAGIC - 클러스터에서 로컬 파일처럼 직접 접근 가능
# MAGIC - 워크스페이스 간 공유 가능

# COMMAND ----------

# DBTITLE 1,Volume 경로 설정 및 데이터 다운로드
import mlflow

# Volume 경로
volume_path = f"/Volumes/{catalog}/{db}/lgit_images"
data_path = f"{volume_path}/mvtec_ad"
os.makedirs(data_path, exist_ok=True)
print(f"이미지 저장 경로 (Volume): {volume_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. MVTec AD 데이터셋 로드
# MAGIC
# MAGIC Anomalib은 MVTec AD를 **자동 다운로드**하는 기능을 내장하고 있습니다.
# MAGIC `prepare_data()` 호출 시 자동으로 데이터를 다운로드하고 구조를 맞춥니다.

# COMMAND ----------

# DBTITLE 1,Anomalib 데이터 모듈 생성
from anomalib.data import MVTec

# 'bottle' 카테고리 사용 (데모용)
# 다른 카테고리도 동일한 방법으로 학습 가능:
#   transistor, metal_nut, screw 등은 전자부품에 적합
CATEGORY = "bottle"

datamodule = MVTec(
    root=data_path,
    category=CATEGORY,
    image_size=(256, 256),    # 모든 이미지를 256×256으로 리사이즈
    train_batch_size=32,       # 한 번에 32장씩 학습
    eval_batch_size=32,
    num_workers=4,             # 데이터 로딩 병렬화
)

# 데이터 다운로드 (첫 실행 시에만)
print("데이터 준비 중 (첫 실행 시 다운로드)...")
datamodule.prepare_data()
datamodule.setup()

print(f"\n=== 데이터셋 정보 ===")
print(f"  카테고리: {CATEGORY}")
print(f"  학습 이미지: {len(datamodule.train_data)} 장 (정상만)")
print(f"  테스트 이미지: {len(datamodule.test_data)} 장 (정상 + 이상)")
print(f"  이미지 크기: 256×256 pixels")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 데이터 탐색 (EDA)
# MAGIC
# MAGIC 학습 전 이미지 데이터를 시각적으로 확인합니다.
# MAGIC - **정상 이미지**: 학습에 사용될 이미지
# MAGIC - **이상 이미지**: 테스트에 사용될 결함 이미지 + 결함 위치 마스크

# COMMAND ----------

# DBTITLE 1,정상/이상 이미지 시각화
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(2, 5, figsize=(20, 8))
fig.suptitle(f"MVTec AD - {CATEGORY}: 정상 vs 이상 이미지", fontsize=16)

# 정상 이미지 (학습 데이터)
axes[0][0].set_ylabel("정상\n(학습 데이터)", fontsize=12, fontweight='bold')
train_dl = datamodule.train_dataloader()
train_batch = next(iter(train_dl))
for i in range(5):
    img = train_batch["image"][i].permute(1, 2, 0).cpu().numpy()
    img = (img - img.min()) / (img.max() - img.min() + 1e-8)
    axes[0][i].imshow(img)
    axes[0][i].set_title("정상")
    axes[0][i].axis("off")

# 이상 이미지 (테스트 데이터)
axes[1][0].set_ylabel("이상\n(테스트 데이터)", fontsize=12, fontweight='bold')
test_dl = datamodule.test_dataloader()
test_batch = next(iter(test_dl))
anomaly_count = 0
for i in range(len(test_batch["image"])):
    if anomaly_count >= 5:
        break
    if test_batch["label"][i].item() == 1:  # 이상 이미지만 선택
        img = test_batch["image"][i].permute(1, 2, 0).cpu().numpy()
        img = (img - img.min()) / (img.max() - img.min() + 1e-8)
        axes[1][anomaly_count].imshow(img)
        axes[1][anomaly_count].set_title("이상 (결함)")
        axes[1][anomaly_count].axis("off")
        anomaly_count += 1

plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. PatchCore 모델 학습
# MAGIC
# MAGIC ### 학습 과정
# MAGIC
# MAGIC PatchCore는 일반적인 딥러닝 모델과 다르게:
# MAGIC 1. 수백 epoch의 반복 학습이 **불필요**
# MAGIC 2. **1 epoch만** 실행 (정상 이미지의 피처를 추출하여 메모리 뱅크에 저장)
# MAGIC 3. 학습 시간이 매우 짧음 (수 분 이내)
# MAGIC
# MAGIC ### MLflow Tracking
# MAGIC
# MAGIC 비정형 모델도 정형 모델과 **동일한 방식**으로 MLflow에 기록합니다.
# MAGIC - 하이퍼파라미터 (backbone, coreset_sampling_ratio 등)
# MAGIC - 메트릭 (AUROC, F1, Precision, Recall)
# MAGIC - 아티팩트 (모델 가중치, 시각화 결과)

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
        tags={"project": "lgit-mlops-poc", "domain": "anomaly-detection", "data_type": "image"}
    )

mlflow.set_experiment(experiment_name)
print(f"실험: {experiment_name}")

# COMMAND ----------

# DBTITLE 1,PatchCore 모델 학습
from anomalib.models import Patchcore
from anomalib.engine import Engine

with mlflow.start_run(run_name=f"patchcore_{CATEGORY}") as run:
    # ─── 하이퍼파라미터 기록 ───
    hparams = {
        "model": "PatchCore",
        "backbone": "wide_resnet50_2",
        "layers": "layer2, layer3",
        "coreset_sampling_ratio": 0.1,
        "category": CATEGORY,
        "image_size": 256,
        "train_batch_size": 32,
    }
    mlflow.log_params(hparams)

    # ─── PatchCore 모델 생성 ───
    model = Patchcore(
        backbone="wide_resnet50_2",                # 사전학습된 ResNet50 (Wide 버전)
        layers_to_extract=["layer2", "layer3"],     # 중간 레이어 피처 추출
        coreset_sampling_ratio=0.1,                 # 메모리 뱅크 크기 (10%)
    )

    # ─── 학습 엔진 설정 ───
    engine = Engine(
        max_epochs=1,                  # PatchCore는 1 epoch만 필요!
        accelerator="auto",           # GPU 자동 감지
        devices=1,
        default_root_dir=f"{volume_path}/anomalib_results",
    )

    # ─── 학습 실행 ───
    print("PatchCore 학습 시작...")
    print("  (정상 이미지에서 피처를 추출하여 메모리 뱅크를 구축합니다)")
    engine.fit(model=model, datamodule=datamodule)
    print("학습 완료!")

    # ─── 테스트 (성능 평가) ───
    print("\n테스트 수행 (정상 + 이상 이미지에서 성능 측정)...")
    test_results = engine.test(model=model, datamodule=datamodule)

    # ─── 메트릭 기록 ───
    if test_results:
        print(f"\n=== 테스트 결과 ===")
        for metric_name, metric_value in test_results[0].items():
            if isinstance(metric_value, (int, float)):
                clean_name = metric_name.replace("/", "_")
                mlflow.log_metric(clean_name, metric_value)
                print(f"  {metric_name}: {metric_value:.4f}")

    # ─── 모델 저장 ───
    model_save_path = f"{volume_path}/anomalib_results/patchcore_{CATEGORY}"
    os.makedirs(model_save_path, exist_ok=True)
    torch.save(model.state_dict(), f"{model_save_path}/model.pth")
    mlflow.log_artifact(f"{model_save_path}/model.pth", "model")

    run_id = run.info.run_id
    print(f"\nMLflow Run ID: {run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. 이상탐지 결과 시각화
# MAGIC
# MAGIC 모델이 **어떤 영역**을 이상으로 판단했는지 **히트맵(Heatmap)** 으로 시각화합니다.
# MAGIC
# MAGIC ### 히트맵 해석
# MAGIC ```
# MAGIC   파란색/초록색: 정상 영역 (메모리 뱅크와 유사)
# MAGIC   노란색:       주의 영역 (약간 다름)
# MAGIC   빨간색:       이상 영역 (메모리 뱅크와 크게 다름) → 결함!
# MAGIC ```

# COMMAND ----------

# DBTITLE 1,이상탐지 히트맵 시각화
# 테스트 데이터에서 예측 수행
model.eval()
predictions = engine.predict(model=model, datamodule=datamodule)

# 예측 결과에서 배치 가져오기
pred_dl = datamodule.test_dataloader()
pred_batch = next(iter(pred_dl))

fig, axes = plt.subplots(3, 4, figsize=(16, 12))
fig.suptitle(f"MVTec AD - {CATEGORY}: 이상탐지 결과", fontsize=16)

# 열 제목
col_titles = ["원본 이미지", "이상 히트맵", "원본 이미지", "이상 히트맵"]
for j, title in enumerate(col_titles):
    axes[0][j].set_title(title, fontsize=11, fontweight='bold')

sample_idx = 0
for row in range(3):
    for col_pair in range(2):
        col_base = col_pair * 2

        # 이미지 찾기
        while sample_idx < len(pred_batch["image"]):
            idx = sample_idx
            sample_idx += 1

            img = pred_batch["image"][idx].permute(1, 2, 0).cpu().numpy()
            img = (img - img.min()) / (img.max() - img.min() + 1e-8)
            label = "이상" if pred_batch["label"][idx].item() == 1 else "정상"

            # 원본 이미지
            axes[row][col_base].imshow(img)
            axes[row][col_base].set_ylabel(f"{label}", fontsize=10,
                                           color='red' if label == "이상" else 'green')
            axes[row][col_base].axis("off")

            # 히트맵 (anomaly_map이 있는 경우)
            if "anomaly_maps" in pred_batch and pred_batch["anomaly_maps"] is not None:
                heatmap = pred_batch["anomaly_maps"][idx].squeeze().cpu().numpy()
                axes[row][col_base+1].imshow(img)
                axes[row][col_base+1].imshow(heatmap, cmap="jet", alpha=0.5)
            else:
                axes[row][col_base+1].imshow(img, cmap='gray')
                axes[row][col_base+1].text(0.5, 0.5, "Predict 후\n생성", ha='center',
                                           va='center', transform=axes[row][col_base+1].transAxes)
            axes[row][col_base+1].axis("off")
            break

plt.tight_layout()

# MLflow에 시각화 저장
with mlflow.start_run(run_id=run_id):
    mlflow.log_figure(fig, "anomaly_detection_heatmaps.png")

plt.show()
print("히트맵 설명:")
print("  빨간 영역 = 모델이 '정상과 다르다'고 판단한 위치 (결함 후보)")
print("  파란 영역 = 정상 패턴과 일치하는 위치")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Unity Catalog에 모델 등록
# MAGIC
# MAGIC 비정형(이미지) 모델도 정형 모델과 **동일한 Unity Catalog 거버넌스** 체계로 관리합니다.
# MAGIC
# MAGIC ```
# MAGIC Unity Catalog Model Registry:
# MAGIC
# MAGIC simyung_yang (카탈로그)
# MAGIC  └── lgit_mlops_poc (스키마)
# MAGIC       ├── lgit_predictive_maintenance   ← 정형 모델 (XGBoost)
# MAGIC       └── lgit_anomaly_detection        ← 비정형 모델 (PatchCore) ★
# MAGIC
# MAGIC 두 모델 모두 동일한:
# MAGIC  - 버전 관리 (v1, v2, ...)
# MAGIC  - 에일리어스 (Champion, Challenger)
# MAGIC  - 접근 제어 (GRANT/REVOKE)
# MAGIC  - 계보 추적 (데이터 → 모델 → 추론)
# MAGIC ```

# COMMAND ----------

# DBTITLE 1,비정형 모델 UC 등록
from mlflow import MlflowClient

unstructured_model_name = f"{catalog}.{db}.lgit_anomaly_detection"
client = MlflowClient()

# 모델 등록
model_details = mlflow.register_model(
    model_uri=f"runs:/{run_id}/model",
    name=unstructured_model_name
)

# 모델 설명 추가
client.update_registered_model(
    name=unstructured_model_name,
    description=f"""LG Innotek 비전 기반 이상탐지 모델.

모델: PatchCore (Anomalib)
백본: Wide ResNet-50-2 (ImageNet 사전학습)
데이터: MVTec AD - {CATEGORY} 카테고리
입력: 제품 표면 이미지 (256×256 RGB)
출력: 이상 점수 (0~1), 이상/정상 분류, 이상 위치 히트맵

용도: 제조 라인의 제품 표면 자동 검사.
정상 이미지만으로 학습하여 새로운 유형의 결함도 탐지 가능."""
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
# MAGIC ## 7. 새 이미지에 대한 추론 (Inference)
# MAGIC
# MAGIC 등록된 모델을 사용하여 **새로운 이미지**에 대한 이상탐지를 수행합니다.
# MAGIC 실제 운영에서는 이 코드가 **배치 추론 파이프라인**으로 스케줄링됩니다.

# COMMAND ----------

# DBTITLE 1,단일 이미지 추론 예시
# 테스트 이미지 하나를 가져와서 추론
model.eval()
with torch.no_grad():
    test_sample = next(iter(datamodule.test_dataloader()))
    sample_img = test_sample["image"][0:1]  # 첫 번째 이미지

    # 추론 수행
    if device == "cuda":
        sample_img = sample_img.cuda()
        model = model.cuda()

    output = model(sample_img)

    # 결과 해석
    if isinstance(output, dict):
        anomaly_score = output.get("pred_scores", output.get("anomaly_maps", None))
        if anomaly_score is not None:
            score = anomaly_score.mean().item()
        else:
            score = 0.0
    else:
        score = 0.0

    actual_label = "이상" if test_sample["label"][0].item() == 1 else "정상"
    predicted = "이상" if score > 0.5 else "정상"

    print(f"=== 단일 이미지 추론 결과 ===")
    print(f"  실제 레이블: {actual_label}")
    print(f"  이상 점수:   {score:.4f}")
    print(f"  예측 결과:   {predicted}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. 다른 모델과의 비교 (참고)
# MAGIC
# MAGIC Anomalib은 PatchCore 외에도 다양한 이상탐지 모델을 제공합니다.
# MAGIC 동일한 코드 구조로 모델만 교체하여 비교할 수 있습니다.
# MAGIC
# MAGIC | 모델 | 정확도 (AUROC) | 추론 속도 | 메모리 | 적합 시나리오 |
# MAGIC |------|---------------|----------|--------|-------------|
# MAGIC | **PatchCore** | 99.1% | 보통 | 높음 | 정확도 최우선 |
# MAGIC | **EfficientAD** | 98.8% | 가장 빠름 | 가장 낮음 | 실시간 / 엣지 |
# MAGIC | **Reverse Distillation** | 98.5% | 빠름 | 낮음 | 속도-정확도 균형 |
# MAGIC | **PADIM** | 97.9% | 빠름 | 보통 | 빠른 프로토타이핑 |
# MAGIC
# MAGIC ```python
# MAGIC # 모델 교체 예시 (코드 한 줄만 변경)
# MAGIC from anomalib.models import EfficientAd
# MAGIC model = EfficientAd()  # PatchCore 대신 EfficientAD
# MAGIC # 나머지 코드는 동일!
# MAGIC ```
# MAGIC
# MAGIC ### VisA 데이터셋 사용 (전자부품 특화)
# MAGIC
# MAGIC ```python
# MAGIC # MVTec AD 대신 VisA 사용 (PCB 보드 카테고리 포함)
# MAGIC from anomalib.data import Visa
# MAGIC
# MAGIC datamodule = Visa(
# MAGIC     root="/Volumes/catalog/schema/volume/visa",
# MAGIC     category="pcb1",  # pcb1, pcb2, pcb3, pcb4 (전자부품!)
# MAGIC     image_size=(256, 256),
# MAGIC )
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC ### 이 노트북에서 수행한 작업:
# MAGIC
# MAGIC | 단계 | 내용 | Databricks 기능 |
# MAGIC |------|------|----------------|
# MAGIC | 1 | GPU 확인 및 Volume 설정 | GPU Cluster, UC Volumes |
# MAGIC | 2 | MVTec AD 이미지 데이터 다운로드 | Anomalib 자동 다운로드 |
# MAGIC | 3 | 정상/이상 이미지 시각화 (EDA) | 노트북 시각화 |
# MAGIC | 4 | PatchCore 모델 학습 (1 epoch) | MLflow Tracking |
# MAGIC | 5 | 이상 히트맵 시각화 | MLflow Artifacts |
# MAGIC | 6 | Unity Catalog 모델 등록 | UC Model Registry |
# MAGIC | 7 | 단일 이미지 추론 | MLflow pyfunc |
# MAGIC
# MAGIC ### 핵심 포인트:
# MAGIC - **정상 데이터만으로 학습** → 새로운 유형의 결함도 탐지 가능
# MAGIC - **히트맵 출력** → 결함 **위치**까지 파악 가능
# MAGIC - **정형 모델과 동일한 거버넌스** → Unity Catalog로 통합 관리
# MAGIC - **코드 한 줄**로 모델/데이터셋 교체 → 빠른 실험
# MAGIC
# MAGIC **다음 단계:** [모델 모니터링]($./08_model_monitoring)
