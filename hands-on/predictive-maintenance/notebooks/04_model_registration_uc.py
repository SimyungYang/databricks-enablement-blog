# Databricks notebook source
# MAGIC %md
# MAGIC # Unity Catalog 모델 레지스트리 등록
# MAGIC
# MAGIC 최적의 모델을 **Unity Catalog 모델 레지스트리** 에 등록하고, 에일리어스(Alias)를 통해 모델의 생애 주기를 관리합니다.
# MAGIC
# MAGIC ### 모델 레지스트리란?
# MAGIC
# MAGIC **모델 레지스트리(Model Registry)** 는 학습이 완료된 AI 모델을 안전하게 보관하고 관리하는 **중앙 창고** 입니다.
# MAGIC
# MAGIC **제조 비유:** 공장에서 완성된 금형(Mold)을 관리하는 것과 같습니다.
# MAGIC - 금형마다 **버전 번호** 가 있고 (v1, v2, v3...)
# MAGIC - 현재 생산에 사용 중인 금형과 테스트 중인 금형이 구분되며
# MAGIC - 누가 언제 만들었는지, 어떤 사양인지 기록이 남아 있고
# MAGIC - 허가된 사람만 금형을 교체할 수 있습니다
# MAGIC
# MAGIC AI 모델도 마찬가지입니다. 모델을 "그냥 파일로 저장"하면 버전 관리, 권한 관리, 이력 추적이 불가능합니다.
# MAGIC Unity Catalog 모델 레지스트리는 이 모든 것을 자동으로 관리합니다.
# MAGIC
# MAGIC > **현장 경험담:** 모델 레지스트리 없이 ML을 운영하는 곳을 정말 많이 봤습니다. `model_v2_final_final_진짜최종.pkl` 같은 파일이 서버에 널려 있는 상황이요. 6개월 후에 어떤 모델이 운영 중인지 아무도 모릅니다. 담당자가 퇴사하면 그 모델은 "미아"가 됩니다. 누가 만들었는지, 어떤 데이터로 학습했는지, 성능이 얼마인지 전혀 알 수 없게 됩니다. 이것은 기술 부채가 아니라 **운영 리스크** 입니다. 모델 레지스트리는 이 문제를 근본적으로 해결합니다.
# MAGIC
# MAGIC ### Databricks 핵심 기능
# MAGIC
# MAGIC | 기능 | 설명 | 제조 현장 가치 |
# MAGIC |------|------|----------------|
# MAGIC | **Unity Catalog Model Registry** | 모델 버전의 중앙 관리 | 모델이 여기저기 흩어지지 않고, 한 곳에서 체계적으로 관리됩니다 |
# MAGIC | **모델 에일리어스 (Alias)** | Champion/Challenger 패턴으로 안전한 배포 | 운영 중인 모델을 중단 없이 새 모델로 교체할 수 있습니다 |
# MAGIC | **모델 계보 (Lineage)** | 데이터 → 실험 → 모델 간 전체 추적 | 문제 발생 시 원인을 끝까지 추적할 수 있습니다 |
# MAGIC | **접근 제어** | 모델에 대한 세분화된 권한 관리 | 모델 등록은 ML 엔지니어만, 배포 승인은 관리자만 가능하도록 설정 |
# MAGIC
# MAGIC > **기존 방식 vs Databricks:** 전통적으로는 모델을 `.pkl` 파일로 저장하여 공유 폴더에 넣었습니다.
# MAGIC > "최종_모델_v3_수정_최종2.pkl" 같은 파일명으로 관리하면 어떤 것이 실제 운영 모델인지 혼란스럽고,
# MAGIC > 누가 언제 만들었는지, 어떤 데이터로 학습했는지 알 수 없습니다.
# MAGIC > Unity Catalog는 이 모든 문제를 해결합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### ⚠️ 사전 요구사항
# MAGIC - **03_structured_model_training** 노트북을 먼저 실행해야 합니다
# MAGIC - MLflow 실험에 최소 1개의 완료된 Run이 있어야 합니다 (03번에서 생성됨)
# MAGIC - Run이 없으면 최적 모델 검색 시 오류가 발생합니다

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 주요 변수 안내
# MAGIC
# MAGIC 아래 코드에서 사용되는 주요 변수들은 `00-setup` 노트북에서 자동으로 설정됩니다.
# MAGIC 매번 수동으로 입력할 필요 없이, 환경에 맞게 자동으로 감지됩니다.
# MAGIC
# MAGIC | 변수 | 의미 | 예시 |
# MAGIC |------|------|------|
# MAGIC | `catalog` | Unity Catalog 카탈로그 이름 | `lgit_mlops` |
# MAGIC | `db` | 스키마(데이터베이스) 이름 | `default` |
# MAGIC | `current_user` | 현재 로그인한 사용자 이메일 | `user@lgit.com` |
# MAGIC
# MAGIC > **Unity Catalog 3-Level 네임스페이스** : Databricks에서 모든 데이터 객체(테이블, 뷰, 모델 등)는
# MAGIC > `카탈로그.스키마.객체명` 형식으로 관리됩니다.
# MAGIC > 마치 `공장.생산라인.설비` 처럼 계층적으로 구조화되어 있어,
# MAGIC > 개발/스테이징/운영 환경을 명확히 분리하고, 권한을 세밀하게 제어할 수 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 최적 모델 검색
# MAGIC
# MAGIC ### 왜 자동 검색이 필요한가?
# MAGIC
# MAGIC 이전 노트북(03번)에서 총 4번의 학습(Baseline + HPO 3회)을 실행했습니다.
# MAGIC 각 실행은 MLflow에 자동으로 기록되어 있으므로, 이제 **프로그래밍 방식으로** 가장 성능이 좋은 모델을 찾습니다.
# MAGIC
# MAGIC MLflow의 `search_runs` API는 SQL과 비슷한 문법으로 실험 결과를 검색합니다.
# MAGIC 마치 데이터베이스에서 "점수가 가장 높은 학생을 찾아라"와 같이, "F1 점수가 가장 높은 모델을 찾아라"라고 쿼리합니다.
# MAGIC
# MAGIC > **수동 vs 자동:** 실험이 4개일 때는 눈으로 비교할 수 있지만, 수십~수백 개의 실험이 있을 때는 자동 검색이 필수입니다.
# MAGIC > 이 자동화 방식은 나중에 CI/CD 파이프라인에서도 그대로 활용됩니다.
# MAGIC
# MAGIC > **현장 경험담:** 많은 팀이 "가장 좋은 모델"을 수동으로 찾아서 수동으로 배포합니다. 사람이 하니까 실수가 생깁니다. "이 Run이 제일 좋았지?"라고 기억에 의존하다가 잘못된 모델을 배포한 사례를 실제로 봤습니다. `search_runs` API를 사용한 프로그래밍 방식의 검색은 **사람의 실수를 시스템으로 방지** 하는 것입니다. 이것이 MLOps의 핵심 원칙입니다.

# COMMAND ----------

# DBTITLE 1,최적 실험 Run 검색
import mlflow
from mlflow import MlflowClient

# MlflowClient는 MLflow의 저수준(Low-level) API입니다.
# mlflow.xxx() 함수보다 세밀한 조작이 필요할 때 사용합니다.
# 예: 모델 버전 관리, 에일리어스 설정, 태그 추가 등.
client = MlflowClient()
model_name = f"{catalog}.{db}.lgit_predictive_maintenance"

# 실험 검색
xp_name = "lgit_predictive_maintenance"
xp_path = f"/Users/{current_user}"
mlflow.set_experiment(f"{xp_path}/{xp_name}")

# filter_string은 SQL과 비슷한 문법입니다.
# - "name LIKE '...%'" → 이름이 특정 패턴으로 시작하는 실험 검색
# - "last_update_time DESC" → 최근에 업데이트된 실험 순으로 정렬
experiment_id = mlflow.search_experiments(
    filter_string=f"name LIKE '{xp_path}/{xp_name}%'",
    order_by=["last_update_time DESC"]
)[0].experiment_id

# 최적 모델 검색 (val_f1_score 기준)
# "metrics.val_f1_score DESC" → F1 점수 내림차순 정렬 (가장 높은 점수가 첫 번째)
# max_results=1 → 최상위 1개만 가져옴
# filter_string="status = 'FINISHED'" → 정상적으로 완료된 Run만 검색 (실패/실행중 제외)
best_run = mlflow.search_runs(
    experiment_ids=experiment_id,
    order_by=["metrics.val_f1_score DESC"],
    max_results=1,
    filter_string="status = 'FINISHED'"
)

print(f"=== 최적 모델 ===")
print(f"Run ID: {best_run.iloc[0]['run_id']}")
print(f"Run Name: {best_run.iloc[0]['tags.mlflow.runName']}")
print(f"Val F1: {best_run.iloc[0]['metrics.val_f1_score']:.4f}")
print(f"Val AUC: {best_run.iloc[0]['metrics.val_auc']:.4f}")

display(best_run)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Unity Catalog에 모델 등록
# MAGIC
# MAGIC ### 모델 등록이란?
# MAGIC
# MAGIC 모델을 레지스트리에 "등록"한다는 것은, 학습이 완료된 모델을 **공식적으로 관리 대상에 포함시키는** 행위입니다.
# MAGIC
# MAGIC **제조 비유:** 시제품을 만든 후, 양산 승인을 위해 **BOM(Bill of Materials) 시스템에 정식 등록** 하는 것과 같습니다.
# MAGIC 등록 전까지는 "실험실의 시제품"이지만, 등록 후에는 "관리 대상 자산"이 됩니다.
# MAGIC
# MAGIC ### Unity Catalog 3-Level 네임스페이스
# MAGIC
# MAGIC 등록된 모델은 **`카탈로그.스키마.모델명`** (예: `lgit_mlops.default.lgit_predictive_maintenance`) 형식으로 관리됩니다.
# MAGIC
# MAGIC ```
# MAGIC lgit_mlops (카탈로그)          ← 조직/프로젝트 단위
# MAGIC ```
# MAGIC  +-- default (스키마)           ← 환경 단위 (dev/staging/prod)
# MAGIC       +-- lgit_predictive_maintenance (모델)  ← 모델 자체
# MAGIC            +-- Version 1       ← 첫 번째 학습 결과
# MAGIC            +-- Version 2       ← 파라미터 변경 후 재학습
# MAGIC            +-- Version 3       ← 새 데이터로 재학습
# MAGIC
# MAGIC 이 구조 덕분에 데이터 테이블과 모델이 **동일한 거버넌스 체계** 아래에서 관리되며,
# MAGIC 개발/스테이징/운영 환경을 명확히 분리할 수 있습니다.
# MAGIC
# MAGIC > **현장 경험담:**3-Level 네임스페이스의 진짜 가치는 **환경 분리** 입니다. 실무에서는 `lgit_mlops_dev.default.model`, `lgit_mlops_staging.default.model`, `lgit_mlops_prod.default.model` 식으로 카탈로그 수준에서 환경을 분리합니다. 이렇게 하면 개발 환경에서 아무리 실험해도 운영 모델에 영향을 주지 않습니다. 또한 권한 관리도 카탈로그 단위로 걸 수 있어서, 주니어 엔지니어는 dev 카탈로그에만 접근하고, prod 카탈로그는 시니어 승인을 거치도록 설정할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,모델 등록
run_id = best_run.iloc[0]['run_id']
print(f"모델 등록: {model_name}")

model_details = mlflow.register_model(
    model_uri=f"runs:/{run_id}/xgboost_model",
    name=model_name
)

print(f"등록 완료 — 모델: {model_details.name}, 버전: {model_details.version}")

# 등록 완료! Databricks UI에서 확인하는 방법:
# 좌측 사이드바 > [Models] 아이콘 클릭 > 모델명 검색 또는 목록에서 확인
# 또는 상단 메뉴 > Catalog > 해당 카탈로그 > 스키마 > Models 탭

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 모델 메타데이터 추가
# MAGIC
# MAGIC ### 메타데이터란?
# MAGIC
# MAGIC **메타데이터(Metadata)** 란 "데이터에 대한 데이터", 즉 모델 자체에 대한 **부가 정보** 입니다.
# MAGIC
# MAGIC **제조 비유:** 제품에 붙이는 라벨과 같습니다. 제품 자체(모델)도 중요하지만,
# MAGIC 라벨에 적힌 정보(제조일, 원산지, 성분, 유효기간 등)가 없으면 관리가 불가능합니다.
# MAGIC
# MAGIC ### 왜 메타데이터가 거버넌스에 중요한가?
# MAGIC
# MAGIC 6개월 후, 누군가 이 모델을 보고 다음 질문을 할 수 있습니다:
# MAGIC - "이 모델은 무엇을 예측하는 모델인가?" → **모델 설명(Description)** 으로 답변
# MAGIC - "성능이 얼마나 좋은가?" → **태그(Tags)** 로 F1, AUC 값 확인
# MAGIC - "어떤 데이터로 학습했는가?" → **데이터 소스 태그** 로 확인
# MAGIC - "어떤 프로젝트에 속하는가?" → **도메인 태그** 로 분류
# MAGIC
# MAGIC 이런 정보가 없으면 모델이 "미아"가 됩니다. 누가 만들었는지, 왜 만들었는지, 써도 되는지 아무도 모르게 됩니다.
# MAGIC
# MAGIC > **Databricks 장점:** Unity Catalog에서는 태그 정책(Tag Policy)을 설정하여,
# MAGIC > 모든 모델에 필수 태그(예: `domain`, `owner`)가 반드시 포함되도록 강제할 수 있습니다.
# MAGIC > 이를 통해 조직 전체의 ML 자산을 체계적으로 관리할 수 있습니다.
# MAGIC
# MAGIC > **현장 경험담:** 메타데이터의 중요성은 모델이 10개를 넘어가면 절실히 느낍니다. "이 모델 누가 만들었지?", "어떤 용도지?", "아직 쓰는 건가?" 라는 질문에 답하지 못하면, 결국 아무도 건드리지 못하는 "유령 모델"이 됩니다. 실제로 한 고객사에서 운영 서버에 모델이 30개 이상 돌고 있었는데, 절반은 더 이상 필요 없는 모델이었습니다. 하지만 아무도 확신이 없어서 끌 수 없었습니다. 메타데이터를 처음부터 잘 달아두면 이런 상황을 방지할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,모델 설명 추가
# 모델 전체 설명
client.update_registered_model(
    name=model_name,
    description="""LG Innotek 예지보전(Predictive Maintenance) 모델.
    AI4I 2020 데이터셋 기반 XGBoost 분류기.
    입력: 설비 센서값 (온도, 회전속도, 토크, 공구 마모 등)
    출력: 고장 발생 확률 및 이진 분류 결과.
    용도: 제조 설비의 고장을 사전에 예측하여 예방 정비 수행."""
)

# 버전별 상세 정보
best_f1 = best_run.iloc[0]['metrics.val_f1_score']
best_auc = best_run.iloc[0]['metrics.val_auc']
run_name = best_run.iloc[0]['tags.mlflow.runName']

client.update_model_version(
    name=model_name,
    version=model_details.version,
    description=f"XGBoost 모델 (Run: {run_name}). Val F1: {best_f1:.4f}, Val AUC: {best_auc:.4f}."
)

# 태그 추가
client.set_model_version_tag(name=model_name, version=model_details.version, key="val_f1_score", value=f"{best_f1:.4f}")
client.set_model_version_tag(name=model_name, version=model_details.version, key="val_auc", value=f"{best_auc:.4f}")
# 참고: 워크스페이스에 태그 정책이 설정된 경우, 허용된 값만 사용 가능합니다.
# 태그 정책 오류 방지를 위해 try-except 처리
# 아래 try/except 블록: 워크스페이스 태그 정책에 의해 허용되지 않는 태그 키/값이 있을 수 있습니다.
# 이 오류가 발생하면 무시해도 실습에 영향 없습니다 (워크스페이스 태그 정책에 의한 제한).
# 실제 운영에서는 조직이 정의한 표준 태그만 사용해야 합니다.
try:
    client.set_model_version_tag(name=model_name, version=model_details.version, key="domain", value="customer_demo")
except Exception as e:
    print(f"domain 태그 설정 참고: {e}")

try:
    client.set_model_version_tag(name=model_name, version=model_details.version, key="data_source", value="ai4i_2020")
except Exception as e:
    print(f"data_source 태그 설정 참고: {e}")

print("모델 메타데이터 추가 완료")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. 모델 에일리어스 (Alias) 설정
# MAGIC
# MAGIC ### 에일리어스란?
# MAGIC
# MAGIC **에일리어스(Alias)** 는 특정 모델 버전에 붙이는 **별명(닉네임)** 입니다.
# MAGIC 버전 번호(v1, v2, v3) 대신 의미 있는 이름으로 모델을 참조할 수 있게 해줍니다.
# MAGIC
# MAGIC ### Champion/Challenger 패턴 - 스포츠 비유
# MAGIC
# MAGIC 이 패턴은 스포츠의 **주전 선수 교체** 와 동일합니다:
# MAGIC
# MAGIC - **Champion (주전 선수):** 현재 경기(운영 환경)에서 뛰고 있는 선수. 실제 예측에 사용되는 모델입니다.
# MAGIC - **Challenger (후보 선수):** 훈련(검증)에서 좋은 성적을 보이고 있어, 주전에 도전하는 선수. 아직 운영에 투입되지는 않았습니다.
# MAGIC
# MAGIC > **현장 경험담:** 이 패턴은 A/B 테스트에서 왔지만, **제조업에서 더 중요합니다.**웹 서비스에서 A/B 테스트가 실패하면 클릭률이 조금 떨어지는 정도이지만, 제조에서 잘못된 모델이 배포되면 **라인이 멈춥니다.**실제로 한 고객사에서 검증 없이 새 모델을 바로 운영에 올렸다가, 오탐(False Positive)이 급증해서 정상 설비를 계속 멈추게 한 사례가 있었습니다. 생산 손실이 하루에 수천만 원이었습니다. Champion/Challenger 패턴은 이런 사고를 방지하는 **안전장치** 입니다.
# MAGIC
# MAGIC **교체 과정:**
# MAGIC 1. 새 모델을 학습합니다
# MAGIC 2. "Challenger" 에일리어스를 부여합니다
# MAGIC 3. 검증을 거쳐 기존 Champion보다 성능이 좋으면
# MAGIC 4. "Champion" 에일리어스를 새 모델로 옮깁니다 → **운영 모델 교체 완료!**
# MAGIC
# MAGIC | 에일리어스 | 역할 | 제조 비유 |
# MAGIC |-----------|------|----------|
# MAGIC | `Baseline` | 최초 등록 시 부여되는 기준 모델 | 초기 양산 조건 |
# MAGIC | `Challenger` | 검증 대기 중인 후보 모델 | 파일럿 라인에서 테스트 중인 새 공정 |
# MAGIC | `Champion` | 현재 운영 중인 모델 | 양산 라인에서 가동 중인 현행 공정 |
# MAGIC
# MAGIC ### 무중단 배포 (Zero-Downtime Deployment)
# MAGIC
# MAGIC 에일리어스의 가장 큰 장점은 **코드 변경 없이 모델을 교체** 할 수 있다는 것입니다.
# MAGIC
# MAGIC 운영 시스템은 항상 "Champion"이라는 이름으로 모델을 호출합니다:
# MAGIC ```python
# MAGIC model = mlflow.pyfunc.load_model(f"models:/{model_name}@Champion")
# MAGIC
# MAGIC 에일리어스를 v1에서 v2로 변경하면, 운영 코드는 한 줄도 수정하지 않고도 자동으로 새 모델을 사용하게 됩니다.
# MAGIC 이를 **무중단 배포** 라고 하며, 생산 라인을 멈추지 않고 모델을 교체할 수 있습니다.
# MAGIC
# MAGIC > **현장 경험담:** 에일리어스의 진짜 가치는 **무중단 배포** 입니다. 코드에서 `@Champion`으로 참조하면, 모델이 v5에서 v6으로 바뀌어도 **코드는 한 줄도 안 바꿔도 됩니다.**이것이 가능한 이유는 에일리어스가 모델 버전에 대한 **포인터(pointer)** 역할을 하기 때문입니다. 마치 DNS가 IP 주소를 도메인 이름으로 추상화하는 것과 같습니다. 운영 코드를 수정한다는 것은 곧 **배포를 다시 해야 한다** 는 뜻이고, 배포는 항상 리스크를 수반합니다. 에일리어스는 이 리스크를 없앱니다. 또한, 문제가 생기면 에일리어스만 이전 버전으로 되돌리면 **즉시 롤백** 됩니다. 코드 롤백, 재배포 같은 복잡한 과정이 필요 없습니다.

# COMMAND ----------

# DBTITLE 1,Challenger 에일리어스 설정
# [Champion/Challenger 패턴 안내]
# 처음 실행 시에는 Champion이 없으므로 Challenger가 자동으로 Champion도 됩니다.
# 재실행 시(모델을 새로 학습했을 때)에는 기존 Champion과 성능을 비교합니다.
# 이 패턴의 장점: 코드를 수정하지 않고 에일리어스만 변경하면 운영 모델 교체 완료!

# 새 모델을 Challenger로 설정
client.set_registered_model_alias(
    name=model_name,
    alias="Challenger",
    version=model_details.version
)

print(f"모델 '{model_name}' v{model_details.version} → Challenger 에일리어스 설정 완료")

# Champion이 없는 경우 바로 Champion으로도 설정
try:
    champion = client.get_model_version_by_alias(model_name, "Champion")
    print(f"기존 Champion 존재: v{champion.version}")
except:
    print("기존 Champion이 없으므로, 이 버전을 Champion으로도 설정합니다.")
    client.set_registered_model_alias(
        name=model_name,
        alias="Champion",
        version=model_details.version
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Databricks UI 확인 포인트
# MAGIC
# MAGIC 1. **좌측 사이드바 > Models** 클릭 (또는 Catalog > 카탈로그 > 스키마 > Models)
# MAGIC 2. `lgit_predictive_maintenance` 모델 클릭
# MAGIC 3. **Versions** 탭: 모델 버전 목록 확인 (v1, v2, ...)
# MAGIC 4. **Aliases** 확인: Champion/Challenger 에일리어스가 어떤 버전을 가리키는지
# MAGIC 5. 특정 버전 클릭 > **Lineage** 탭: 이 모델이 어떤 데이터/실험에서 왔는지 그래프로 확인
# MAGIC 6. **Schema** 탭: 모델의 입력/출력 스키마 확인 (어떤 피처를 입력해야 하는지)
# MAGIC 7. **Description** 과 **Tags**: 메타데이터 확인
# MAGIC
# MAGIC > **드릴다운 팁**: Lineage 그래프에서 `lgit_pm_training` 테이블을 클릭하면 02번 노트북의 피처 테이블로 바로 이동합니다. 이것이 전체 파이프라인의 추적성입니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. 등록된 모델 확인
# MAGIC
# MAGIC ### 모델 계보 (Lineage) - 탐정의 수사 기록
# MAGIC
# MAGIC Unity Catalog Explorer에서 모델의 버전, 에일리어스, 계보(Lineage)를 시각적으로 확인할 수 있습니다.
# MAGIC
# MAGIC **모델 계보(Lineage)** 는 모델의 전체 이력을 추적하는 기능입니다.
# MAGIC
# MAGIC **탐정 비유:** 모델이 잘못된 예측을 했을 때, 계보는 **탐정이 단서를 따라가는 수사 기록** 과 같습니다:
# MAGIC
# MAGIC 1. "이 모델은 어떤 실험(Run)에서 나왔는가?" → 실험 ID로 추적
# MAGIC 2. "그 실험에서 어떤 데이터를 사용했는가?" → 데이터 계보로 추적
# MAGIC 3. "그 데이터는 어떤 테이블의 몇 번째 버전인가?" → Delta Lake 버전으로 추적
# MAGIC 4. "그 데이터에 문제가 있었는가?" → 데이터 품질 확인
# MAGIC
# MAGIC 이렇게 **모델 → 실험 → 데이터** 까지 끝에서 끝까지(End-to-End) 추적할 수 있어,
# MAGIC 문제의 근본 원인을 신속하게 파악할 수 있습니다.
# MAGIC
# MAGIC > **현장 경험담:** 규제 산업(자동차, 의료기기, 반도체)에서 일해보면 Lineage가 왜 중요한지 절실히 느낍니다. "이 모델은 어떤 데이터로 학습되었나요?"라는 감사(Audit) 질문에 **즉시** 답할 수 있어야 합니다. LG이노텍은 자동차 부품 비중이 크기 때문에, IATF 16949 같은 품질 표준에서 이 추적성(Traceability)을 요구합니다. AI 모델도 예외가 아닙니다. "이 모델의 예측을 근거로 공정을 변경했는데, 그 모델은 어떤 데이터 기반이었나요?"라는 질문에 5분 안에 답하지 못하면 감사에서 지적사항이 됩니다. Lineage는 이것을 **자동으로** 해결합니다.
# MAGIC
# MAGIC > **Databricks UI에서 확인:** 좌측 사이드바 > **Catalog**> 해당 카탈로그 > 스키마 > **Models** 탭에서
# MAGIC > 모델을 클릭하면 버전 목록, 에일리어스, 계보 그래프를 시각적으로 볼 수 있습니다.

# COMMAND ----------

# DBTITLE 1,등록된 모델 정보 조회
model_info = client.get_registered_model(model_name)
print(f"모델: {model_info.name}")
print(f"설명: {model_info.description[:100]}...")

if model_info.aliases:
    for alias_info in model_info.aliases:
        # alias_info가 문자열인 경우와 객체인 경우 모두 처리
        alias_name = alias_info.alias if hasattr(alias_info, 'alias') else str(alias_info)
        try:
            version = client.get_model_version_by_alias(model_name, alias_name)
            print(f"\n에일리어스: {alias_name}")
            print(f"  버전: {version.version}")
            print(f"  상태: {version.status}")
            desc = version.description or "N/A"
            print(f"  설명: {desc[:80]}...")
        except Exception as e:
            print(f"\n에일리어스 {alias_name} 조회 오류: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC ### 이 노트북에서 수행한 작업
# MAGIC
# MAGIC | 단계 | 작업 내용 | 핵심 가치 |
# MAGIC |------|----------|----------|
# MAGIC | 1 | MLflow에서 **최적 모델 자동 검색** (val_f1_score 기준) | 수작업 비교 대신 프로그래밍 방식으로 최적 모델 식별 |
# MAGIC | 2 | **Unity Catalog 모델 레지스트리** 에 모델 등록 | 모델이 공식 관리 자산으로 등록되어 버전 관리 시작 |
# MAGIC | 3 | 모델 **설명, 태그** 등 메타데이터 추가 (거버넌스) | 6개월 후에도 모델의 목적, 성능, 출처를 즉시 파악 가능 |
# MAGIC | 4 | **Challenger/Champion 에일리어스** 설정 | 코드 변경 없이 운영 모델을 안전하게 교체하는 패턴 확립 |
# MAGIC
# MAGIC ### 핵심 메시지
# MAGIC
# MAGIC Unity Catalog 모델 레지스트리를 사용하면, AI 모델도 제조 현장의 자산처럼 **체계적으로 관리** 할 수 있습니다.
# MAGIC - **누가** 만들었는지, **어떤 데이터** 로 학습했는지, **성능** 이 어떤지 모두 기록됩니다
# MAGIC - Champion/Challenger 패턴으로 **안전하게** 모델을 교체할 수 있습니다
# MAGIC - 문제 발생 시 계보(Lineage)를 통해 **근본 원인까지 추적** 할 수 있습니다
# MAGIC
# MAGIC 이것이 "실험실의 모델"을 "운영 가능한 AI 자산"으로 전환하는 **MLOps의 핵심** 입니다.
# MAGIC
# MAGIC > **현장 경험담:** 많은 ML 프로젝트가 "모델 학습까지는 잘 되는데, 운영이 안 됩니다"라고 합니다. 그 이유의 대부분은 이 노트북에서 다룬 것들이 없기 때문입니다. 버전 관리 없이 모델 파일만 복사하고, 메타데이터 없이 "이건 좋은 모델이야"라고만 말하고, 안전장치 없이 바로 배포합니다. 모델 레지스트리, 메타데이터, Champion/Challenger, Lineage - 이 네 가지는 **ML을 "실험"에서 "운영"으로 넘기는 다리** 입니다. 이 다리 없이 운영에 뛰어들면 반드시 사고가 납니다.
# MAGIC
# MAGIC **다음 단계:** [챌린저 모델 검증]($./05_challenger_validation) - Challenger 모델이 실제로 Champion보다 나은지 체계적으로 검증하는 과정을 진행합니다.
