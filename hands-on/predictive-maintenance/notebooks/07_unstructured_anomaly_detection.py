# Databricks notebook source
# MAGIC %md
# MAGIC # 비정형 이상탐지: 이미지 기반 제품 표면 검사
# MAGIC
# MAGIC 본 노트북에서는 **제품 표면 이미지**를 사용하여 **이상(결함)** 을 자동으로 탐지하는 AI 모델을 학습합니다.
# MAGIC 정형 데이터(센서값) 기반의 예지보전(03a~03d)과 함께, **비정형 데이터(이미지)** 기반의 비전 검사를 Databricks 플랫폼에서 통합 구현합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 이 노트북에서 배우는 내용
# MAGIC
# MAGIC | 단계 | 내용 | Databricks 기능 | 제조 현장 가치 |
# MAGIC |------|------|----------------|-------------|
# MAGIC | **데이터**| MVTec AD 이미지 데이터셋 다운로드 및 관리 | **Unity Catalog Volumes** | 이미지 데이터도 정형 데이터와 동일한 거버넌스 |
# MAGIC | **탐색** | 정상/이상 이미지 시각화 및 분석 | 노트북 시각화 | 결함 유형 파악, 데이터 품질 확인 |
# MAGIC | **학습**| Anomalib PatchCore 모델 학습 | **GPU Cluster**, MLflow | 정상 이미지만으로 학습 → 결함 데이터 수집 불필요 |
# MAGIC | **평가**| 이상 점수, 히트맵, AUROC 메트릭 | **MLflow Tracking** | 결함 위치까지 시각적으로 파악 |
# MAGIC | **등록**| 모델을 Unity Catalog에 등록 | **UC Model Registry** | 정형/비정형 모델 통합 관리 |
# MAGIC | **추론** | 새 이미지에 대한 이상탐지 수행 | MLflow pyfunc | 생산 라인 자동 검사 자동화 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 사전 지식: 비전 기반 이상탐지란?
# MAGIC
# MAGIC ### 왜 이미지 이상탐지가 필요한가?
# MAGIC
# MAGIC LG Innotek의 카메라 모듈, PCB, 전자부품 생산 라인에서는 **외관 검사(Visual Inspection)** 가 품질 관리의 핵심입니다.
# MAGIC 현재 대부분의 외관 검사는 **숙련된 검사원의 육안**또는 **Rule-based 머신비전 시스템** 에 의존하고 있습니다.
# MAGIC
# MAGIC | 검사 방식 | 처리 속도 | 일관성 | 비용 | 새 결함 대응 |
# MAGIC |----------|----------|--------|------|------------|
# MAGIC | **육안 검사** | 초당 2~5개 | 낮음 (피로, 주관) | 높음 (인건비) | 즉각 대응 가능 |
# MAGIC | **Rule-based 비전** | 초당 수십 개 | 높음 | 중간 (개발비) | 새 규칙 개발 필요 (수 주) |
# MAGIC | **AI 비전 검사** | 초당 수백 개 | 매우 높음 | 낮음 (학습만) | 정상 데이터만으로 자동 대응 |
# MAGIC
# MAGIC AI 기반 비전 검사의 핵심 장점:
# MAGIC - **24시간 일관된 검사**: 사람과 달리 피로도, 집중력 저하 없음
# MAGIC - **확장 용이**: 새 라인에 카메라만 설치하면 동일 모델 적용 가능
# MAGIC - **결함 위치 시각화**: 어디가 결함인지 **히트맵(Heatmap)** 으로 표시 → 원인 분석에 활용
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 비전 검사 기술의 발전 역사
# MAGIC
# MAGIC | 시기 | 기술 | 원리 | 한계 |
# MAGIC |------|------|------|------|
# MAGIC | 1980년대 | **Rule-based 비전** | 밝기, 엣지, 크기 등 규칙으로 판정 | 조명 변화에 민감, 규칙 작성 어려움 |
# MAGIC | 2012~2018 | **CNN 지도학습** | 정상/불량 이미지를 대량으로 학습 | 불량 이미지 수천 장 필요 → 수집 어려움 |
# MAGIC | 2018~2020 | **오토인코더** | 정상 이미지 복원을 학습, 복원 오차로 이상 탐지 | 정확도 한계 (AUROC 90% 수준) |
# MAGIC | 2020~2022 | **지식 증류** | Teacher-Student 네트워크로 이상 영역 탐지 | 학습 시간 길고 튜닝 어려움 |
# MAGIC | 2022~ | **PatchCore** | 사전학습 피처 + 메모리 뱅크 (학습 불필요) | 메모리 사용량 높음 (Core-set으로 해결) |
# MAGIC | 2023~ | **Foundation Model** | WinCLIP, AnomalyCLIP 등 언어-비전 모델 활용 | 연구 단계, 실무 적용 초기 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 비지도 학습 기반 이상탐지 — 제조 현장의 게임 체인저
# MAGIC
# MAGIC ```
# MAGIC 일반 지도학습 (Supervised):               비지도 이상탐지 (Unsupervised):
# MAGIC   정상 이미지 1000장  ┐                      정상 이미지 1000장 → 학습
# MAGIC   결함 이미지 1000장  ┘→ 학습                 (결함 이미지 불필요!)
# MAGIC
# MAGIC   문제점:                                  장점:
# MAGIC   ✗ 결함 이미지 수집이 매우 어려움            ✓ 정상 데이터만으로 학습 가능
# MAGIC     (불량률 1%면 결함 1000장 수집에            ✓ 새로운 유형의 결함도 탐지 가능
# MAGIC      정상 10만장 필요)                         (학습하지 않은 결함도 감지)
# MAGIC   ✗ 새 결함 유형 등장 시 재수집 필요          ✓ 결함 유형별 레이블링 불필요
# MAGIC   ✗ 결함 유형별 레이블링 비용 막대           ✓ 결함 위치(히트맵)까지 자동 표시
# MAGIC ```
# MAGIC
# MAGIC **핵심 아이디어**: "정상이 어떤 것인지만 학습하고, 정상과 다르면 이상으로 판단"
# MAGIC
# MAGIC > **LG Innotek 가치**: 카메라 모듈의 렌즈 스크래치, 센서 오염, PCB 납땜 불량 등 **결함 유형이 다양하고 예측 불가능** 한 환경에서, 비지도 이상탐지는 새로운 결함 유형에도 자동 대응할 수 있어 매우 유용합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## PatchCore 알고리즘 — 산업용 이상탐지의 표준
# MAGIC
# MAGIC **PatchCore**(CVPR 2022, Roth et al.)는 현재 산업용 이미지 이상탐지에서 **가장 높은 정확도** 를 보이는 알고리즘입니다.
# MAGIC
# MAGIC ### 동작 원리 — 공장 비유로 이해하기
# MAGIC
# MAGIC PatchCore의 원리를 **숙련된 품질 검사원의 사고 과정** 에 비유하면:
# MAGIC
# MAGIC ```
# MAGIC 숙련 검사원의 검사 과정:
# MAGIC 1. 수천 개의 정상 제품을 보면서 "정상은 이렇게 생겼다"는 기준을 머릿속에 형성
# MAGIC 2. 새 제품을 볼 때, 제품의 각 부분을 머릿속 기준과 비교
# MAGIC 3. 기준과 크게 다른 부분이 있으면 → "이 부분이 결함!"
# MAGIC
# MAGIC PatchCore 알고리즘:
# MAGIC 1. 정상 이미지의 피처를 추출하여 "메모리 뱅크"에 저장 (검사원의 경험)
# MAGIC 2. 새 이미지의 피처를 추출하여 메모리 뱅크와 비교 (검사)
# MAGIC 3. 거리(Distance)가 큰 영역 → 이상 (결함 발견)
# MAGIC ```
# MAGIC
# MAGIC ### 기술적 동작 원리
# MAGIC
# MAGIC ```
# MAGIC Step 1: 피처 추출 (Feature Extraction) — "제품의 DNA를 읽는다"
# MAGIC ┌──────────────┐     ┌─────────────┐     ┌──────────────────┐
# MAGIC │ 정상 이미지    │ ──→ │ 사전학습 CNN │ ──→ │ 중간 레이어 피처   │
# MAGIC │ (256×256)     │     │ (ResNet50)  │     │ (패치 단위 추출)  │
# MAGIC └──────────────┘     └─────────────┘     └──────────────────┘
# MAGIC
# MAGIC   - ImageNet(1400만 이미지)으로 사전학습된 Wide ResNet-50을 사용
# MAGIC   - 최종 레이어가 아닌 **중간 레이어(layer2, layer3)** 에서 피처 추출
# MAGIC     → 왜? 중간 레이어는 텍스처, 엣지, 패턴 등 **범용적 시각 특성** 을 담고 있음
# MAGIC     → 최종 레이어는 "고양이", "자동차" 같은 **분류 특화** 정보라 이상탐지에 부적합
# MAGIC   - 이미지를 패치(예: 32×32 픽셀) 단위로 분할하여 각 패치의 피처를 독립 추출
# MAGIC
# MAGIC Step 2: 메모리 뱅크 구축 (Memory Bank) — "정상 패턴 사전을 만든다"
# MAGIC ┌──────────────────┐     ┌──────────────────┐
# MAGIC │ 모든 정상 이미지의 │ ──→ │ Core-set 선택     │ ──→ 메모리 뱅크
# MAGIC │ 패치 피처 수집    │     │ (대표 샘플 선택)   │     (정상 패턴 사전)
# MAGIC └──────────────────┘     └──────────────────┘
# MAGIC
# MAGIC   - 정상 이미지에서 추출한 수만~수십만 개의 패치 피처를 수집
# MAGIC   - **Core-set Sampling**: 중복을 제거하고 대표적인 피처만 10% 선택 (메모리 효율화)
# MAGIC     → 원래 10만 개 피처 → 1만 개로 축소해도 정확도 손실 거의 없음
# MAGIC   - 이것이 곧 "이 제품의 정상 상태는 이런 것이다"라는 **정상 패턴의 사전(Dictionary)**
# MAGIC
# MAGIC Step 3: 이상 탐지 (Anomaly Detection) — "새 제품을 사전과 비교한다"
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
# MAGIC ### 왜 PatchCore가 제조 현장에 최적인가?
# MAGIC - **학습 시간이 매우 짧음**: 1 epoch만 필요 (피처 추출 + 메모리 저장). 일반 딥러닝은 수백 epoch 필요
# MAGIC - **정확도 최고**: MVTec AD 벤치마크 **Image-level AUROC 99.1%** (2022년 기준 SOTA)
# MAGIC - **새로운 결함 유형도 탐지**: 학습하지 않은 결함도 "정상과 다르다"는 것을 감지 → **Unknown Defect Detection**
# MAGIC - **결함 위치 표시**: 히트맵으로 정확히 **어디가 결함인지** 시각화 → 엔지니어의 원인 분석 지원
# MAGIC - **학습 데이터 부담 최소**: 정상 이미지 200~300장이면 충분한 성능 확보
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 데이터: MVTec AD — 산업용 이상탐지의 표준 벤치마크
# MAGIC
# MAGIC **MVTec Anomaly Detection Dataset**은 독일 뮌헨 공과대학(TUM)과 MVTec Software GmbH가 2019년에 공개한 데이터셋으로, 산업용 이상탐지 연구의 **사실상의 표준(De facto standard)** 입니다. 모든 이상탐지 논문이 이 데이터셋에서의 성능을 보고합니다.
# MAGIC
# MAGIC | 항목 | 상세 |
# MAGIC |------|------|
# MAGIC | **이름** | MVTec Anomaly Detection Dataset (MVTec AD) |
# MAGIC | **카테고리** | 15종: 5개 텍스처(carpet, grid, leather, tile, wood) + 10개 객체(bottle, cable, capsule, hazelnut, metal_nut, pill, screw, toothbrush, transistor, zipper) |
# MAGIC | **규모** | 5,354 이미지 (학습 3,629 + 테스트 1,725) |
# MAGIC | **해상도** | 700x700 ~ 1024x1024 (고해상도 산업 이미지) |
# MAGIC | **구조**| 학습: **정상 이미지만** / 테스트: 정상 + 다양한 유형의 이상 (픽셀 레벨 GT 마스크 포함) |
# MAGIC | **결함 유형** | 스크래치, 구멍, 오염, 변색, 균열, 누락, 형상 불량 등 73종 이상 |
# MAGIC | **라이선스** | CC BY-NC-SA 4.0 (연구/교육 목적 무료) |
# MAGIC
# MAGIC > **LG Innotek에 더 적합한 데이터셋**: **VisA (Visual Anomaly) Dataset**(2022, Amazon)는 **PCB 보드 4종**(pcb1~pcb4), 커넥터, 칩 등 **전자부품 특화** 이미지를 포함합니다. Anomalib에서 동일한 코드로 VisA를 사용할 수 있습니다. 실제 LG Innotek 적용 시에는 VisA의 PCB 카테고리 또는 자체 촬영 이미지를 사용하는 것을 권장합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC > **주의**: 이 노트북은 **GPU 클러스터** 에서 실행해야 합니다.
# MAGIC > - 권장: `g5.2xlarge` (NVIDIA A10G, 24GB VRAM) 또는 `g4dn.2xlarge` (NVIDIA T4, 16GB)
# MAGIC > - CPU에서도 실행 가능하지만, 학습 시간이 **10~20배 이상** 느려집니다
# MAGIC > - **왜 GPU가 필요한가?**: PatchCore의 피처 추출에 사용되는 Wide ResNet-50은 수천만 개의 연산(행렬 곱셈)을 수행합니다. GPU는 이 연산을 **수천 개의 코어에서 병렬 처리** 하여 CPU 대비 10~100배 빠릅니다.

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
# MAGIC ### GPU 확인 — 딥러닝의 필수 인프라
# MAGIC
# MAGIC 딥러닝 모델은 대량의 **행렬 연산(Matrix Multiplication)**을 수행합니다. 이 연산은 GPU(Graphics Processing Unit)에서 **수천 개의 코어를 동시에 사용** 하여 병렬 처리할 때 효율적입니다.
# MAGIC
# MAGIC ```
# MAGIC CPU vs GPU 비교:
# MAGIC   CPU: 고성능 코어 8~16개 → 순차적 처리에 강함 (일반 프로그래밍)
# MAGIC   GPU: 소형 코어 수천 개  → 병렬 처리에 강함 (딥러닝, 이미지 처리)
# MAGIC
# MAGIC   예: 이미지 256×256 = 65,536 픽셀의 피처 추출
# MAGIC   CPU: 65,536개를 8개 코어로 순차 처리 → 느림
# MAGIC   GPU: 65,536개를 5,000개 코어로 동시 처리 → 수십 배 빠름
# MAGIC ```
# MAGIC
# MAGIC > **Databricks 장점**: Databricks에서는 클러스터 생성 시 인스턴스 타입만 선택하면 GPU 드라이버, CUDA, cuDNN이 **자동으로 설치** 됩니다. 별도의 GPU 환경 설정이 필요 없습니다.
# MAGIC
# MAGIC **권장 인스턴스**:
# MAGIC - 학습: `g5.2xlarge` (NVIDIA A10G, 24GB VRAM) — 최신 Ampere 아키텍처, 학습 최적
# MAGIC - 추론 (비용 절약): `g4dn.2xlarge` (NVIDIA T4, 16GB VRAM) — 추론 최적화, 비용 50% 절감

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
# MAGIC ### Unity Catalog Volumes — 이미지 데이터의 체계적 관리
# MAGIC
# MAGIC 제조 현장에서 비전 검사 이미지는 **하루에 수만~수십만 장** 이 생성됩니다. 이 이미지들을 체계적으로 관리하지 않으면:
# MAGIC - 누가 어떤 이미지에 접근했는지 추적 불가 (보안 문제)
# MAGIC - 학습에 사용된 이미지가 어떤 것인지 재현 불가 (감사 문제)
# MAGIC - 팀 간 이미지 공유가 어려움 (협업 문제)
# MAGIC
# MAGIC **Unity Catalog Volumes**은 이 문제를 해결합니다. **비정형 데이터(이미지, 오디오, 비디오 등)**를 정형 데이터와 **동일한 거버넌스 체계** 로 관리합니다.
# MAGIC
# MAGIC ```
# MAGIC Unity Catalog 구조 — 정형/비정형 데이터 통합 관리:
# MAGIC
# MAGIC Catalog (카탈로그) — 예: simyung_yang
# MAGIC  └── Schema (스키마) — 예: lgit_mlops_poc
# MAGIC       ├── Table (정형 데이터)     ← Delta Lake 테이블 (센서 데이터, 공정 데이터)
# MAGIC       ├── Model (ML 모델)         ← MLflow 모델 (XGBoost, PatchCore)
# MAGIC       └── Volume (비정형 데이터)   ← 이미지, 파일 등 ★
# MAGIC            └── lgit_images/
# MAGIC                 └── mvtec_ad/
# MAGIC                      ├── bottle/
# MAGIC                      ├── transistor/
# MAGIC                      └── metal_nut/
# MAGIC
# MAGIC Volume 경로: /Volumes/{catalog}/{schema}/{volume_name}/
# MAGIC ```
# MAGIC
# MAGIC **Databricks Volumes의 핵심 장점**:
# MAGIC - **통합 거버넌스**: 이미지도 정형 데이터와 **동일한 권한(GRANT/REVOKE), 감사 로그, 계보 추적** 적용
# MAGIC - **로컬 파일 접근**: 클러스터에서 `/Volumes/...` 경로로 **로컬 파일처럼 직접 접근** — S3 인증 설정 불필요
# MAGIC - **워크스페이스 간 공유**: 다른 팀, 다른 워크스페이스에서도 권한만 있으면 동일 이미지 접근 가능
# MAGIC - **대규모 확장**: 수 TB의 이미지 데이터도 클라우드 스토리지 기반으로 비용 효율적으로 저장

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
# MAGIC **Anomalib**(Intel 개발, 오픈소스)은 산업용 이상탐지를 위한 **포괄적인 프레임워크** 입니다.
# MAGIC PatchCore를 포함한 20개 이상의 이상탐지 알고리즘, MVTec AD/VisA 등 주요 벤치마크 데이터셋을 **통합 제공** 합니다.
# MAGIC
# MAGIC `prepare_data()` 호출 시 MVTec AD를 자동으로 다운로드하고, 학습/테스트 분할까지 자동으로 처리합니다.
# MAGIC 다운로드된 이미지는 Unity Catalog Volume에 저장되어 **영구 보존 및 거버넌스 관리** 됩니다.

# COMMAND ----------

# DBTITLE 1,Anomalib 데이터 모듈 생성
from anomalib.data import MVTec

# 'transistor' 카테고리 사용 (LG이노텍 전자부품 특성에 적합)
# 다른 카테고리도 동일한 방법으로 학습 가능:
#   transistor, metal_nut, screw 등은 전자부품에 적합
CATEGORY = "transistor"

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
# MAGIC ## 3. 데이터 탐색 (EDA) — 데이터를 눈으로 확인하는 단계
# MAGIC
# MAGIC ML 모델 학습 전에 **반드시** 데이터를 시각적으로 확인해야 합니다. 이는 정형 데이터에서 통계량을 확인하는 것과 동일한 중요성을 가집니다.
# MAGIC
# MAGIC 확인할 사항:
# MAGIC - **정상 이미지**: 학습에 사용될 이미지. 일관된 품질인가? 조명 조건은 균일한가?
# MAGIC - **이상 이미지**: 테스트에 사용될 결함 이미지. 어떤 유형의 결함이 있는가? 결함의 크기와 위치는?
# MAGIC - **이미지 품질**: 해상도, 밝기, 초점이 적절한가? 노이즈가 과도하지 않은가?
# MAGIC
# MAGIC > **실무 팁**: LG Innotek 자체 이미지를 사용할 때, 정상 이미지의 **일관성** 이 매우 중요합니다. 조명 조건, 카메라 각도, 제품 위치가 일정해야 모델이 "정상 패턴"을 정확히 학습할 수 있습니다.

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
# MAGIC ### 학습 과정 — 일반 딥러닝과 완전히 다른 방식
# MAGIC
# MAGIC PatchCore는 일반적인 딥러닝 모델(CNN, Transformer)과 **근본적으로 다른 학습 방식** 을 사용합니다:
# MAGIC
# MAGIC | 비교 항목 | 일반 딥러닝 | PatchCore |
# MAGIC |----------|-----------|-----------|
# MAGIC | 학습 방식 | 역전파(Backpropagation)로 가중치 최적화 | 사전학습 모델에서 피처 추출 후 메모리에 저장 |
# MAGIC | 필요 Epoch | 수십~수백 epoch | **1 epoch만** 필요 |
# MAGIC | 학습 시간 | 수 시간~수 일 | **수 분** (GPU 기준) |
# MAGIC | 가중치 업데이트 | 매 배치마다 가중치 변경 | 가중치 변경 없음 (Frozen backbone) |
# MAGIC | 하이퍼파라미터 | 학습률, 배치 크기, 에폭 수 등 다수 | backbone, coreset_ratio 정도 (매우 적음) |
# MAGIC
# MAGIC > **왜 1 epoch인가?**: PatchCore는 **이미 학습된 ResNet의 피처 추출 능력** 을 그대로 활용합니다. 새로 학습할 것이 없고, 정상 이미지의 피처를 한 번 읽어서 메모리 뱅크에 저장하는 것이 전부입니다. 이것이 PatchCore의 실용적 강점입니다.
# MAGIC
# MAGIC ### MLflow Tracking — 비정형 모델도 동일한 실험 관리
# MAGIC
# MAGIC **Databricks의 핵심 가치**: 정형 데이터 모델(XGBoost, 03a~03d)과 비정형 데이터 모델(PatchCore)을 **동일한 MLflow 인터페이스**로 관리합니다. 이는 MLOps의 중요한 원칙인 **통합 실험 관리** 를 구현합니다.
# MAGIC
# MAGIC 기록 항목:
# MAGIC - **하이퍼파라미터**: backbone(Wide ResNet-50), coreset_sampling_ratio(10%), 이미지 크기 등
# MAGIC - **메트릭**: AUROC(이미지 수준), F1, Precision, Recall, 픽셀 수준 AUROC
# MAGIC - **아티팩트**: 모델 가중치(.pth), 이상 히트맵 시각화, 학습 로그

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
# MAGIC ## 5. 이상탐지 결과 시각화 — 히트맵 해석법
# MAGIC
# MAGIC PatchCore의 가장 강력한 출력은 **이상 히트맵(Anomaly Heatmap)** 입니다.
# MAGIC 단순히 "이상/정상"만 판정하는 것이 아니라, **이미지의 어떤 영역이 이상인지** 픽셀 수준으로 시각화합니다.
# MAGIC
# MAGIC 이는 제조 현장에서 매우 중요합니다:
# MAGIC - **결함 위치 파악**: 엔지니어가 결함의 물리적 위치를 즉시 확인
# MAGIC - **원인 분석 지원**: 결함 위치가 특정 공정 단계와 연관됨을 파악 (예: 좌측 상단에 결함 집중 → 특정 노즐 문제)
# MAGIC - **검사 결과 문서화**: 히트맵을 MLflow 아티팩트로 저장하여 품질 감사 시 증빙 자료로 활용
# MAGIC
# MAGIC ### 히트맵 해석 방법
# MAGIC
# MAGIC ```
# MAGIC 히트맵 색상 의미 (jet colormap 기준):
# MAGIC
# MAGIC   파란색/초록색: 정상 영역 — 메모리 뱅크(정상 패턴 사전)와 매우 유사
# MAGIC                  → 이 영역은 정상 제품과 동일한 패턴
# MAGIC
# MAGIC   노란색:       주의 영역 — 메모리 뱅크와 약간 다름
# MAGIC                  → 경미한 변이 (정상 범위 내일 수도, 초기 결함일 수도)
# MAGIC
# MAGIC   빨간색:       이상 영역 — 메모리 뱅크와 크게 다름 → 결함!
# MAGIC                  → 정상 제품에서는 절대 볼 수 없는 패턴
# MAGIC                  → 이 위치에 스크래치, 오염, 변형 등이 존재
# MAGIC
# MAGIC 실무 활용:
# MAGIC   빨간색 영역이 없으면 → 정상 판정 ✓
# MAGIC   빨간색 영역이 있으면 → 이상 판정 + 위치 정보 제공
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
# MAGIC ## 6. Unity Catalog에 모델 등록 — 정형/비정형 모델 통합 관리
# MAGIC
# MAGIC **Databricks의 핵심 차별점**: 정형 데이터 모델(XGBoost, LightGBM)과 비정형 데이터 모델(PatchCore, 컴퓨터 비전)을 **동일한 Unity Catalog 거버넌스 체계** 로 관리합니다. 이는 다른 플랫폼에서는 별도의 모델 저장소를 운영해야 하는 것과 대비되는 강점입니다.
# MAGIC
# MAGIC ```
# MAGIC Unity Catalog Model Registry — 통합 모델 관리:
# MAGIC
# MAGIC simyung_yang (카탈로그)
# MAGIC  └── lgit_mlops_poc (스키마)
# MAGIC       ├── lgit_predictive_maintenance   ← 정형 모델 (XGBoost) — 센서 기반 예지보전
# MAGIC       └── lgit_anomaly_detection        ← 비정형 모델 (PatchCore) ★ — 이미지 기반 외관 검사
# MAGIC
# MAGIC 두 모델 모두 동일한 거버넌스 적용:
# MAGIC  - 버전 관리 (v1, v2, ...) — 모든 모델 이력 추적
# MAGIC  - 에일리어스 (Champion, Challenger) — 안전한 배포/롤백
# MAGIC  - 접근 제어 (GRANT/REVOKE) — 팀별 권한 관리
# MAGIC  - 계보 추적 (이미지 데이터 → PatchCore 학습 → 모델 배포 → 추론 결과)
# MAGIC ```
# MAGIC
# MAGIC > **LG Innotek 가치**: 품질 감사 시 "이 모델이 어떤 데이터로 학습되었고, 언제 배포되었으며, 어떤 성능을 보이는지"를 **Unity Catalog 한 곳에서** 모두 확인할 수 있습니다. IATF 16949, ISO 9001 등 품질 경영 시스템의 추적성(Traceability) 요구사항을 자연스럽게 충족합니다.

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
# MAGIC ## 7. 새 이미지에 대한 추론 (Inference) — 실제 운영 활용
# MAGIC
# MAGIC 등록된 모델을 사용하여 **새로운 이미지** 에 대한 이상탐지를 수행합니다.
# MAGIC
# MAGIC **실제 운영 시나리오**:
# MAGIC - **배치 추론**: Databricks Workflow에서 매 시간/교대마다 촬영된 검사 이미지를 일괄 처리
# MAGIC - **실시간 추론**: Model Serving Endpoint를 통해 REST API로 이미지를 전송하면 즉시 결과 반환
# MAGIC - **엣지 추론**: ONNX/TensorRT로 모델 변환 후 라인 옆 엣지 디바이스에서 초고속 추론 (미래 구현)
# MAGIC
# MAGIC > **참고**: 아래 코드는 배치 추론의 기본 형태입니다. 실제 운영에서는 이 코드를 Databricks Workflow의 Task로 등록하여 스케줄링합니다.

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
# MAGIC ## 8. 다른 모델과의 비교 및 최신 트렌드
# MAGIC
# MAGIC ### Anomalib 지원 모델 비교
# MAGIC
# MAGIC Anomalib은 PatchCore 외에도 **20개 이상의 이상탐지 알고리즘** 을 제공합니다.
# MAGIC 동일한 코드 구조에서 **모델 클래스만 교체** 하면 즉시 비교 실험이 가능합니다.
# MAGIC
# MAGIC | 모델 | 정확도 (AUROC) | 추론 속도 | 메모리 | LG Innotek 적합 시나리오 |
# MAGIC |------|---------------|----------|--------|----------------------|
# MAGIC | **PatchCore** | 99.1% | 보통 | 높음 | 정확도 최우선 (오프라인 배치 검사) |
# MAGIC | **EfficientAD** | 98.8% | 가장 빠름 | 가장 낮음 | 실시간 인라인 검사 / 엣지 디바이스 |
# MAGIC | **Reverse Distillation** | 98.5% | 빠름 | 낮음 | 속도-정확도 균형이 필요한 경우 |
# MAGIC | **PADIM** | 97.9% | 빠름 | 보통 | 빠른 PoC / 프로토타이핑 |
# MAGIC | **FastFlow** | 98.4% | 빠름 | 보통 | Normalizing Flow 기반 (확률적 해석 필요 시) |
# MAGIC
# MAGIC > **모델 선택 가이드**: PoC 단계에서는 **PatchCore**(정확도 최고)로 시작하고, 양산 적용 시 추론 속도 요구사항에 따라 **EfficientAD**(실시간) 또는 **Reverse Distillation** (균형)으로 전환을 검토합니다.
# MAGIC
# MAGIC ```python
# MAGIC # 모델 교체 예시 — 코드 한 줄만 변경하면 됩니다!
# MAGIC from anomalib.models import EfficientAd
# MAGIC model = EfficientAd()  # PatchCore 대신 EfficientAD
# MAGIC # 나머지 코드(학습, 평가, 등록)는 완전히 동일!
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### VisA 데이터셋 — LG Innotek 전자부품에 최적
# MAGIC
# MAGIC ```python
# MAGIC # MVTec AD 대신 VisA 사용 (PCB 보드 4종 포함!)
# MAGIC from anomalib.data import Visa
# MAGIC
# MAGIC datamodule = Visa(
# MAGIC     root="/Volumes/catalog/schema/volume/visa",
# MAGIC     category="pcb1",  # pcb1, pcb2, pcb3, pcb4 — 전자부품 특화!
# MAGIC     image_size=(256, 256),
# MAGIC )
# MAGIC # 나머지 코드는 완전히 동일하게 사용 가능
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 최신 트렌드: Foundation Model 기반 이상탐지 (2023~2025)
# MAGIC
# MAGIC 최근 AI 분야의 가장 큰 변화인 **Foundation Model(기반 모델)** 이 이상탐지에도 적용되고 있습니다:
# MAGIC
# MAGIC | 기술 | 논문/년도 | 핵심 아이디어 | 장점 |
# MAGIC |------|----------|-------------|------|
# MAGIC | **WinCLIP** | 2023 | CLIP(언어-비전 모델)의 윈도우 기반 이상 탐지 | Zero-shot 가능 (학습 없이 텍스트로 결함 설명만 하면 탐지) |
# MAGIC | **AnomalyCLIP** | 2024 | CLIP을 이상탐지에 특화하여 Fine-tuning | 여러 도메인에 범용적으로 적용 가능 |
# MAGIC | **SAM + 이상탐지** | 2024 | Segment Anything Model로 결함 영역 정밀 분할 | 픽셀 수준 결함 경계 정확도 향상 |
# MAGIC | **AnomalyGPT** | 2024 | LLM + 비전 모델 결합, 대화형 이상 분석 | "이 결함의 원인이 무엇인가?"에 텍스트로 답변 |
# MAGIC
# MAGIC > **LG Innotek 미래 비전**: Foundation Model 기반 접근은 아직 연구 단계이지만, 향후 "카메라 모듈에서 렌즈 스크래치를 찾아줘"라는 **자연어 지시만으로** 결함을 탐지하는 것이 가능해질 것입니다. Databricks의 GPU 클러스터와 MLflow 인프라가 이러한 최신 모델의 실험/배포를 지원합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC ### 이 노트북에서 수행한 작업
# MAGIC
# MAGIC | 단계 | 내용 | Databricks 기능 | 제조 현장 가치 |
# MAGIC |------|------|----------------|-------------|
# MAGIC | 1 | GPU 확인 및 Volume 설정 | GPU Cluster, UC Volumes | 딥러닝 인프라 자동 구성 |
# MAGIC | 2 | MVTec AD 이미지 데이터 다운로드 | Anomalib 자동 다운로드 | 산업 표준 벤치마크로 PoC 검증 |
# MAGIC | 3 | 정상/이상 이미지 시각화 (EDA) | 노트북 시각화 | 데이터 품질 확인, 결함 유형 파악 |
# MAGIC | 4 | PatchCore 모델 학습 (1 epoch) | MLflow Tracking | 수 분 만에 AUROC 99%+ 모델 확보 |
# MAGIC | 5 | 이상 히트맵 시각화 | MLflow Artifacts | 결함 위치 시각화 → 원인 분석 지원 |
# MAGIC | 6 | Unity Catalog 모델 등록 | UC Model Registry | 정형/비정형 모델 통합 거버넌스 |
# MAGIC | 7 | 단일 이미지 추론 | MLflow pyfunc | 배치/실시간 추론 파이프라인의 기초 |
# MAGIC
# MAGIC ### 핵심 포인트
# MAGIC
# MAGIC - **정상 데이터만으로 학습** → 결함 이미지 수집/레이블링 비용 제거 + 새로운 유형의 결함도 자동 탐지
# MAGIC - **히트맵 출력** → 결함의 **위치와 심각도** 를 시각적으로 파악 → 엔지니어의 원인 분석 지원
# MAGIC - **정형 모델과 동일한 거버넌스** → Unity Catalog로 센서 모델(XGBoost)과 비전 모델(PatchCore)을 **통합 관리**
# MAGIC - **코드 한 줄** 로 모델(PatchCore → EfficientAD)/데이터셋(MVTec → VisA) 교체 → 빠른 실험 반복
# MAGIC
# MAGIC ### LG Innotek 적용 로드맵 (권장)
# MAGIC
# MAGIC ```
# MAGIC Phase 1: PoC (이 노트북)
# MAGIC   └── MVTec AD로 PatchCore 학습/평가 → "AI 비전 검사가 가능한가?" 검증
# MAGIC
# MAGIC Phase 2: 파일럿 (1~2개월)
# MAGIC   └── 실제 카메라 모듈/PCB 이미지로 PatchCore 학습
# MAGIC   └── VisA 데이터셋의 PCB 카테고리로 추가 벤치마크
# MAGIC   └── 기존 Rule-based 비전 시스템과 성능 비교
# MAGIC
# MAGIC Phase 3: 양산 적용 (3~6개월)
# MAGIC   └── Databricks Workflow로 배치 추론 자동화 (교대별 검사 이미지 일괄 처리)
# MAGIC   └── Model Serving Endpoint로 실시간 API 제공 (인라인 검사 연동)
# MAGIC   └── Data Quality Monitoring(구 Data Quality Monitoring)으로 모델 성능 지속 추적
# MAGIC ```
# MAGIC
# MAGIC **다음 단계:** [모델 모니터링]($./08_model_monitoring)
