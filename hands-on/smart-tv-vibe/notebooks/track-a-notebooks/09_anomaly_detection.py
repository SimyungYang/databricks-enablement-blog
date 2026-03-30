# Databricks notebook source
# MAGIC %md
# MAGIC # 09. 비정형 데이터 — 이미지 기반 이상 탐지 (Anomaly Detection)
# MAGIC
# MAGIC 이 노트북에서는 **비정형 데이터(이미지)** 를 활용한 ML 파이프라인을 구축합니다.
# MAGIC Smart TV 제조 라인에서 **디스플레이 패널 결함을 자동 탐지** 하는 시나리오입니다.
# MAGIC
# MAGIC ### 08번 노트북과의 관계
# MAGIC
# MAGIC | | 08번 (정형 데이터) | 09번 (비정형 데이터) |
# MAGIC |---|---|---|
# MAGIC |**데이터**| 사용자 행동 로그 (테이블) | 디스플레이 패널 이미지 |
# MAGIC |**모델**| LightGBM (분류) | CNN 기반 Anomaly Detection |
# MAGIC |**Input**| 센서/행동 피처 | 제품 표면 이미지 |
# MAGIC |**Output**| 클릭 확률, 위험 점수 | 정상/이상, 이상 점수, 히트맵 |
# MAGIC |**컴퓨트**| CPU (m5.large) | GPU (g5.2xlarge) |
# MAGIC |**재학습**| 주 1회 (운영) | 새 결함 유형 발견 시 |
# MAGIC
# MAGIC ### 전체 아키텍처
# MAGIC
# MAGIC ```
# MAGIC ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
# MAGIC │ UC Volume  │  │ Data Module │  │ Model Train │  │ Inference  │
# MAGIC │ /images/   │───→│ 이미지 로딩 │───→│ AutoEncoder │───→│ 이상 점수  │
# MAGIC │ normal/   │  │ 전처리    │  │ or PatchCore │  │ + 히트맵   │
# MAGIC │ anomaly/   │  │ 증강     │  │ + MLflow   │  │       │
# MAGIC └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
# MAGIC                        │
# MAGIC                    ┌──────┴──────┐
# MAGIC                    │ UC Registry │
# MAGIC                    │ + Serving  │
# MAGIC                    └─────────────┘
# MAGIC ```
# MAGIC
# MAGIC ### Anomaly Detection 접근법
# MAGIC
# MAGIC | 방법 | 설명 | 장점 |
# MAGIC |------|------|------|
# MAGIC |**AutoEncoder**| 정상 이미지를 재구성하도록 학습 → 이상 이미지는 재구성 오차가 큼 | 구현 간단, 해석 용이 |
# MAGIC |**PatchCore**| 정상 이미지의 패치 특성을 메모리에 저장 → 테스트 시 거리 기반 이상 탐지 | SOTA 성능, 소량 데이터 |
# MAGIC |**Reverse Distillation**| Teacher-Student 네트워크 → 이상 영역에서 차이 발생 | 높은 정확도 |
# MAGIC
# MAGIC 이 교육에서는 **AutoEncoder** 로 핵심 개념을 이해하고,
# MAGIC 실무에서는 [Anomalib](https://github.com/openvinotoolkit/anomalib)의 PatchCore를 권장합니다.
# MAGIC
# MAGIC**사전 조건:**GPU 클러스터 필요 (g5.2xlarge 또는 g4dn.2xlarge)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 0: 필수 라이브러리 설치

# COMMAND ----------

# MAGIC %pip install torch torchvision Pillow --quiet

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: 환경 설정

# COMMAND ----------

import re
username = spark.sql("SELECT current_user()").first()[0]
user_prefix = re.sub(r'[^a-zA-Z0-9]', '_', username.split('@')[0])
CATALOG = f"{user_prefix}_smarttv_training"
spark.sql(f"USE CATALOG {CATALOG}")
print(f"카탈로그: {CATALOG}")

# Volume 경로
VOLUME_PATH = f"/Volumes/{CATALOG}/bronze/landing"
IMAGE_PATH = f"{VOLUME_PATH}/display_images"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: 합성 이미지 데이터 생성
# MAGIC
# MAGIC 실제 MVTec AD 데이터셋 대신,**합성 디스플레이 패널 이미지** 를 생성합니다.
# MAGIC 정상 이미지와 결함 이미지(스크래치, 얼룩, 데드픽셀)를 프로그래밍으로 만듭니다.
# MAGIC
# MAGIC >**실무에서는:**UC Volume에 실제 제조 라인 카메라 이미지를 적재합니다.
# MAGIC > MVTec AD 데이터셋을 사용하려면: `pip install anomalib` 후 데이터 로더 활용

# COMMAND ----------

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import io
import os

def generate_normal_panel(size=224):
  """정상 디스플레이 패널 이미지 생성 (균일한 밝기, 약간의 노이즈)"""
  base_color = np.random.randint(180, 220)
  img = np.full((size, size, 3), base_color, dtype=np.uint8)
  noise = np.random.normal(0, 3, img.shape).astype(np.int16)
  img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
  # 약간의 그라디언트 (실제 패널처럼)
  gradient = np.linspace(0, 10, size).reshape(1, -1, 1).astype(np.uint8)
  img = np.clip(img.astype(np.int16) + gradient, 0, 255).astype(np.uint8)
  return Image.fromarray(img)

def add_scratch(img):
  """스크래치 결함 추가"""
  draw = ImageDraw.Draw(img)
  x1, y1 = np.random.randint(20, 180, 2)
  length = np.random.randint(40, 120)
  angle = np.random.uniform(-0.5, 0.5)
  x2 = x1 + int(length * np.cos(angle))
  y2 = y1 + int(length * np.sin(angle))
  width = np.random.randint(1, 4)
  color = np.random.randint(50, 120)
  draw.line([(x1, y1), (x2, y2)], fill=(color, color, color), width=width)
  return img

def add_stain(img):
  """얼룩 결함 추가"""
  draw = ImageDraw.Draw(img)
  cx, cy = np.random.randint(40, 180, 2)
  rx, ry = np.random.randint(10, 40, 2)
  color = np.random.randint(100, 160)
  draw.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=(color, color, color+20))
  return img.filter(ImageFilter.GaussianBlur(radius=2))

def add_dead_pixel(img):
  """데드픽셀 결함 추가"""
  arr = np.array(img)
  n_pixels = np.random.randint(3, 15)
  for _ in range(n_pixels):
    x, y = np.random.randint(10, 210, 2)
    size = np.random.randint(2, 6)
    arr[y:y+size, x:x+size] = 0 # 검은 픽셀
  return Image.fromarray(arr)

DEFECT_TYPES = {
  "scratch": add_scratch,
  "stain": add_stain,
  "dead_pixel": add_dead_pixel,
}

print("이미지 생성 함수 준비 완료")
print(f"결함 유형: {list(DEFECT_TYPES.keys())}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 이미지 데이터 생성 및 Volume 저장

# COMMAND ----------

import json
from datetime import datetime

# 디렉토리 생성
for subdir in ["normal", "anomaly/scratch", "anomaly/stain", "anomaly/dead_pixel"]:
  dbutils.fs.mkdirs(f"{IMAGE_PATH}/{subdir}")

# 정상 이미지 생성 (200장 — 학습용)
normal_count = 200
print(f"정상 이미지 {normal_count}장 생성 중...")
for i in range(normal_count):
  img = generate_normal_panel()
  buf = io.BytesIO()
  img.save(buf, format="PNG")
  path = f"{IMAGE_PATH}/normal/panel_{i:04d}.png"
  dbutils.fs.put(path, buf.getvalue().decode("latin-1"), overwrite=True)

# 이상 이미지 생성 (결함 유형별 30장 — 테스트용)
anomaly_count = 30
for defect_name, defect_fn in DEFECT_TYPES.items():
  print(f"{defect_name} 결함 이미지 {anomaly_count}장 생성 중...")
  for i in range(anomaly_count):
    img = generate_normal_panel()
    img = defect_fn(img)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    path = f"{IMAGE_PATH}/anomaly/{defect_name}/panel_{i:04d}.png"
    dbutils.fs.put(path, buf.getvalue().decode("latin-1"), overwrite=True)

# 메타데이터 테이블 생성
metadata = []
for i in range(normal_count):
  metadata.append({"image_path": f"{IMAGE_PATH}/normal/panel_{i:04d}.png",
           "label": "normal", "defect_type": None, "split": "train" if i < 160 else "test"})
for defect_name in DEFECT_TYPES:
  for i in range(anomaly_count):
    metadata.append({"image_path": f"{IMAGE_PATH}/anomaly/{defect_name}/panel_{i:04d}.png",
             "label": "anomaly", "defect_type": defect_name, "split": "test"})

df_meta = spark.createDataFrame(metadata)
df_meta.write.mode("overwrite").saveAsTable(f"{CATALOG}.bronze.display_inspection_images")

total = df_meta.count()
print(f"\n✅ 이미지 데이터 생성 완료: {total}장")
display(df_meta.groupBy("label", "defect_type", "split").count().orderBy("label", "defect_type"))

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Step 3: AutoEncoder 모델 학습
# MAGIC
# MAGIC ### AutoEncoder 기반 이상 탐지 원리
# MAGIC
# MAGIC ```
# MAGIC 정상 이미지 → [Encoder] → 잠재 벡터 → [Decoder] → 재구성 이미지
# MAGIC                           ↕ 비교
# MAGIC                          원본 이미지
# MAGIC                           ↓
# MAGIC                       재구성 오차 (MSE)
# MAGIC                           ↓
# MAGIC                    정상: 오차 작음 ← → 이상: 오차 큼
# MAGIC ```
# MAGIC
# MAGIC**핵심 아이디어:** 정상 이미지로만 학습 → 이상 이미지는 재구성할 수 없어 오차가 크다

# COMMAND ----------

import mlflow
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms

# MLflow 실험 설정
experiment_name = f"/Users/{username}/smarttv_demo/display_anomaly_detection"
mlflow.set_experiment(experiment_name)

# 하이퍼파라미터
IMG_SIZE = 64 # 교육용으로 축소 (실무: 224)
LATENT_DIM = 32
BATCH_SIZE = 32
EPOCHS = 20
LR = 1e-3

# AutoEncoder 정의
class ConvAutoEncoder(nn.Module):
  """
  Convolutional AutoEncoder for Anomaly Detection

  Encoder: 이미지 → 압축된 잠재 벡터 (bottleneck)
  Decoder: 잠재 벡터 → 원본과 유사한 이미지 재구성

  정상 이미지로만 학습하면, 이상 이미지는 재구성 품질이 낮아
  재구성 오차가 크게 나타남 → 이상 탐지
  """
  def __init__(self, latent_dim=32):
    super().__init__()
    # Encoder: 이미지 압축
    self.encoder = nn.Sequential(
      nn.Conv2d(3, 32, 3, stride=2, padding=1),  # 64→32
      nn.ReLU(),
      nn.Conv2d(32, 64, 3, stride=2, padding=1), # 32→16
      nn.ReLU(),
      nn.Conv2d(64, 128, 3, stride=2, padding=1), # 16→8
      nn.ReLU(),
      nn.Flatten(),
      nn.Linear(128 * 8 * 8, latent_dim),
    )
    # Decoder: 이미지 복원
    self.decoder = nn.Sequential(
      nn.Linear(latent_dim, 128 * 8 * 8),
      nn.Unflatten(1, (128, 8, 8)),
      nn.ConvTranspose2d(128, 64, 3, stride=2, padding=1, output_padding=1), # 8→16
      nn.ReLU(),
      nn.ConvTranspose2d(64, 32, 3, stride=2, padding=1, output_padding=1),  # 16→32
      nn.ReLU(),
      nn.ConvTranspose2d(32, 3, 3, stride=2, padding=1, output_padding=1),  # 32→64
      nn.Sigmoid(),
    )

  def forward(self, x):
    z = self.encoder(x)
    return self.decoder(z)

print(f"모델 파라미터: {sum(p.numel() for p in ConvAutoEncoder().parameters()):,}개")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 데이터 로딩 및 학습

# COMMAND ----------

# 간단한 Dataset (Volume에서 이미지 로드)
class PanelDataset(Dataset):
  def __init__(self, paths, transform):
    self.paths = paths
    self.transform = transform

  def __len__(self):
    return len(self.paths)

  def __getitem__(self, idx):
    # Volume 경로에서 이미지 로드
    path = self.paths[idx]
    try:
      data = dbutils.fs.head(path, 50000) # 바이너리 읽기 (간략화)
      img = Image.open(io.BytesIO(data.encode("latin-1"))).convert("RGB")
    except:
      img = generate_normal_panel(IMG_SIZE) # fallback
    return self.transform(img)

transform = transforms.Compose([
  transforms.Resize((IMG_SIZE, IMG_SIZE)),
  transforms.ToTensor(),
])

# 학습 데이터: 정상 이미지만 (train split)
train_paths = [row.image_path for row in
  spark.sql(f"SELECT image_path FROM {CATALOG}.bronze.display_inspection_images WHERE split='train' AND label='normal'").collect()]

# 간략화: 실제 Volume I/O 대신 합성 데이터 직접 사용
print(f"학습 데이터: {len(train_paths)}장 (정상 이미지만)")

# 합성 데이터로 학습 (교육 시간 단축)
train_tensors = torch.stack([transform(generate_normal_panel(IMG_SIZE)) for _ in range(160)])
train_loader = DataLoader(train_tensors, batch_size=BATCH_SIZE, shuffle=True)

# 모델 학습
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"디바이스: {device}")

model = ConvAutoEncoder(LATENT_DIM).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=LR)
criterion = nn.MSELoss()

with mlflow.start_run(run_name="autoencoder_v1"):
  mlflow.log_params({
    "model_type": "ConvAutoEncoder",
    "latent_dim": LATENT_DIM,
    "img_size": IMG_SIZE,
    "epochs": EPOCHS,
    "batch_size": BATCH_SIZE,
    "learning_rate": LR,
    "train_images": len(train_tensors),
    "device": str(device),
  })

  for epoch in range(EPOCHS):
    total_loss = 0
    for batch in train_loader:
      batch = batch.to(device)
      recon = model(batch)
      loss = criterion(recon, batch)
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()
      total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)
    mlflow.log_metric("train_loss", avg_loss, step=epoch)
    if (epoch + 1) % 5 == 0:
      print(f" Epoch {epoch+1}/{EPOCHS}: Loss={avg_loss:.6f}")

  # 모델 저장
  mlflow.pytorch.log_model(model, "model")
  print(f"\n✅ AutoEncoder 학습 완료 (최종 Loss: {avg_loss:.6f})")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Step 4: 이상 탐지 추론 — 이상 점수 & 히트맵
# MAGIC
# MAGIC ### 출력 3가지
# MAGIC 1.**정상/이상 판정**(binary)
# MAGIC 2.**이상 점수**(anomaly score, 0~1 연속값)
# MAGIC 3.**이상 위치 히트맵**(pixel-level, 어디가 결함인지)

# COMMAND ----------

model.eval()

def compute_anomaly_score(model, img_tensor, device):
  """
  이상 점수 계산: 원본과 재구성 이미지의 픽셀별 MSE

  Returns:
    anomaly_score: 전체 이미지의 이상 점수 (float)
    heatmap: 픽셀별 이상 정도 (numpy array)
  """
  with torch.no_grad():
    img = img_tensor.unsqueeze(0).to(device)
    recon = model(img)
    # 픽셀별 재구성 오차
    diff = (img - recon).squeeze().cpu().numpy()
    heatmap = np.mean(diff**2, axis=0) # 채널 평균
    anomaly_score = float(np.mean(heatmap))
  return anomaly_score, heatmap

# 정상 이미지 스코어
normal_scores = []
for _ in range(40):
  img = transform(generate_normal_panel(IMG_SIZE))
  score, _ = compute_anomaly_score(model, img, device)
  normal_scores.append(score)

# 이상 이미지 스코어
anomaly_scores = {"scratch": [], "stain": [], "dead_pixel": []}
for defect_name, defect_fn in DEFECT_TYPES.items():
  for _ in range(30):
    img_pil = generate_normal_panel(IMG_SIZE)
    img_pil = defect_fn(img_pil)
    img = transform(img_pil)
    score, heatmap = compute_anomaly_score(model, img, device)
    anomaly_scores[defect_name].append(score)

# 결과 요약
print("=== 이상 탐지 결과 ===\n")
print(f" 정상 이미지 평균 점수:   {np.mean(normal_scores):.6f} (±{np.std(normal_scores):.6f})")
for defect, scores in anomaly_scores.items():
  print(f" {defect:15s} 평균 점수: {np.mean(scores):.6f} (±{np.std(scores):.6f})")

# 임계값 설정 (정상 평균 + 3σ)
threshold = np.mean(normal_scores) + 3 * np.std(normal_scores)
print(f"\n 임계값 (3σ): {threshold:.6f}")
print(f" → 이 값 초과 시 '이상'으로 판정")

# COMMAND ----------

# 탐지 성능 평가
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

all_scores = normal_scores + [s for scores in anomaly_scores.values() for s in scores]
all_labels = [0] * len(normal_scores) + [1] * sum(len(s) for s in anomaly_scores.values())
all_preds = [1 if s > threshold else 0 for s in all_scores]

print("=== 탐지 성능 ===\n")
print(f" Accuracy: {accuracy_score(all_labels, all_preds):.3f}")
print(f" Precision: {precision_score(all_labels, all_preds):.3f}")
print(f" Recall:  {recall_score(all_labels, all_preds):.3f}")
print(f" F1 Score: {f1_score(all_labels, all_preds):.3f}")

# 결과를 테이블로 저장
results = []
for i, (score, label) in enumerate(zip(all_scores, all_labels)):
  results.append({
    "image_id": f"panel_{i:04d}",
    "anomaly_score": float(score),
    "is_anomaly": bool(score > threshold),
    "actual_label": "anomaly" if label == 1 else "normal",
    "threshold": float(threshold),
    "scored_at": datetime.now().isoformat(),
  })

df_results = spark.createDataFrame(results)
df_results.write.mode("overwrite").saveAsTable(f"{CATALOG}.gold.display_inspection_results")
print(f"\n✅ 검사 결과 저장: {CATALOG}.gold.display_inspection_results ({len(results)}건)")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Step 5: 모델 등록 및 재학습 전략
# MAGIC
# MAGIC ### 비정형 데이터 재학습 전략
# MAGIC
# MAGIC | | 정형 데이터 (08번) | 비정형 데이터 (09번) |
# MAGIC |---|---|---|
# MAGIC |**재학습 트리거**| 스케줄 (주 1회) | 새 결함 유형 발견 시 |
# MAGIC |**데이터 증분**| 새 로그 자동 축적 | 새 이미지 수동/자동 수집 |
# MAGIC |**학습 비용**| 낮음 (CPU, 분 단위) | 높음 (GPU, 시간 단위) |
# MAGIC |**컴퓨트**| m5.large / c6i.large | g5.2xlarge / g4dn.2xlarge |
# MAGIC
# MAGIC ### 권장 컴퓨트 리소스
# MAGIC
# MAGIC | 데이터 유형 | 학습 | 추론 | 비용 최적화 |
# MAGIC |-----------|------|------|-----------|
# MAGIC | 정형 (LightGBM) | m5.large (2 vCPU, 8GB) | c6i.large (Serverless) | Spot 인스턴스 |
# MAGIC | 비정형 (AutoEncoder) | g5.2xlarge (1 GPU, 32GB) | g4dn.2xlarge (1 GPU) | 학습 시만 GPU |
# MAGIC
# MAGIC ### 실무 권장: Anomalib PatchCore
# MAGIC
# MAGIC ```python
# MAGIC # pip install anomalib
# MAGIC from anomalib.data import MVTec
# MAGIC from anomalib.models import Patchcore
# MAGIC from anomalib.engine import Engine
# MAGIC
# MAGIC # 15분 만에 SOTA 이상 탐지 모델 구축
# MAGIC datamodule = MVTec(root="./data", category="transistor")
# MAGIC model = Patchcore()
# MAGIC engine = Engine()
# MAGIC engine.fit(model=model, datamodule=datamodule)
# MAGIC engine.test(model=model, datamodule=datamodule)
# MAGIC ```

# COMMAND ----------

# 모델을 UC에 등록
model_name_ad = f"{CATALOG}.gold.display_anomaly_detector"
try:
  mlflow.set_registry_uri("databricks-uc")
  experiment = mlflow.get_experiment_by_name(experiment_name)
  runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id], order_by=["metrics.train_loss ASC"])
  best_run_id = runs.iloc[0]["run_id"]

  result = mlflow.register_model(f"runs:/{best_run_id}/model", model_name_ad)
  print(f"✅ 모델 등록: {model_name_ad} v{result.version}")
except Exception as e:
  print(f"⚠️ 모델 등록: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 학습 정리
# MAGIC
# MAGIC | 단계 | 내용 |
# MAGIC |------|------|
# MAGIC |**데이터 준비**| UC Volume에 정상/이상 이미지 저장, 메타데이터 테이블 |
# MAGIC |**모델 학습**| ConvAutoEncoder, 정상 이미지만으로 학습 (one-class) |
# MAGIC |**이상 탐지**| 재구성 오차 기반 anomaly score + 히트맵 |
# MAGIC |**임계값**| 정상 분포의 3σ 기준 자동 설정 |
# MAGIC |**결과 저장**| gold.display_inspection_results 테이블 |
# MAGIC |**재학습**| 새 결함 유형 발견 시 트리거 (Agent 연동 가능) |
# MAGIC |**컴퓨트**| 학습: GPU (g5.2xlarge), 추론: GPU (g4dn.2xlarge) |
