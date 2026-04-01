# Databricks notebook source
# MAGIC %md
# MAGIC > **사전 요구사항** : 이 노트북 실행 전 `04_model_registration_uc` 노트북을 먼저 실행해야 합니다.
# MAGIC > 04번 노트북에서 모델을 Unity Catalog에 등록하고 Challenger 에일리어스를 설정해야 이 노트북이 정상 작동합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC # 챌린저(Challenger) 모델 검증
# MAGIC
# MAGIC ## 왜 모델 검증이 필요한가?
# MAGIC
# MAGIC 새로운 AI 모델을 운영 환경에 배포하기 전에, 반드시 **체계적인 검증** 을 거쳐야 합니다.
# MAGIC 이것은 제조 현장의 **품질 검사(QC)** 와 완전히 동일한 개념입니다.
# MAGIC
# MAGIC > **현장 이야기** : 모델 검증을 건너뛰는 팀이 정말 많습니다. "학습 메트릭이 좋으니까 바로 배포하자"는 것이죠.
# MAGIC > 제가 겪었던 가장 큰 사고 중 하나가 이것 때문이었습니다. 학습 데이터에서 F1 0.95였던 모델이
# MAGIC > 운영에서 F1 0.3으로 떨어진 적이 있습니다. 과적합(Overfitting)이었죠.
# MAGIC > 학습 데이터의 패턴을 "외워버린" 모델이, 실제 운영 데이터에서는 완전히 무력해진 겁니다.
# MAGIC > 그 사고 이후로 저는 검증 없는 배포를 절대 허용하지 않습니다.
# MAGIC
# MAGIC > **제조 비유** : LG이노텍에서 새로운 부품을 양산 라인에 투입하기 전에, 시제품을 만들고
# MAGIC > 각종 품질 테스트(내구성, 치수 정밀도, 신뢰성 시험 등)를 거치는 것과 같습니다.
# MAGIC > AI 모델도 마찬가지로, 운영에 투입하기 전에 "이 모델이 정말 기존 모델보다 나은가?",
# MAGIC > "실제 운영 데이터에서도 잘 작동하는가?", "비즈니스 관점에서 가치가 있는가?"를 검증합니다.
# MAGIC
# MAGIC ### Champion-Challenger 패턴이란?
# MAGIC
# MAGIC MLOps에서 널리 사용되는 모델 배포 전략입니다:
# MAGIC - **Champion (챔피언)** : 현재 운영 중인 모델. 검증을 통과해서 "현역"으로 일하고 있는 모델입니다.
# MAGIC - **Challenger (챌린저)** : 새로 학습된 모델. Champion의 자리를 "도전"하는 후보 모델입니다.
# MAGIC - Challenger가 모든 검증을 통과하면 Champion으로 **승급** 되어 운영에 투입됩니다.
# MAGIC - 기존 Champion은 자연스럽게 퇴역합니다.
# MAGIC
# MAGIC > **스포츠 비유** : 현재 레귤러 선수(Champion)가 있고, 유망한 신인 선수(Challenger)가 입단했습니다.
# MAGIC > 신인이 바로 경기에 뛰는 것이 아니라, 체력 테스트, 연습 경기, 전술 이해도 테스트 등을 거쳐
# MAGIC > "기존 선수보다 낫다"고 판명되어야 비로소 주전이 됩니다. 이것이 Champion-Challenger 패턴입니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC
# MAGIC | 기능 | 설명 | 장점 |
# MAGIC |------|------|------|
# MAGIC | **모델 에일리어스** | `@Champion`, `@Challenger` 태그로 모델 역할 관리 | 코드 변경 없이 모델 교체 가능 |
# MAGIC | **mlflow.evaluate()** | 혼동행렬, ROC, PR 등 표준 평가 자동 수행 | 평가 코드를 매번 작성할 필요 없음 |
# MAGIC | **태그 기반 검증 추적** | 각 테스트 결과를 모델 메타데이터로 기록 | 나중에 "왜 이 모델이 승급/거부되었는지" 추적 가능 |
# MAGIC | **Workflows 통합** | 검증 노트북을 Job으로 자동 실행 | 사람 개입 없이 자동 검증 파이프라인 구축 |
# MAGIC
# MAGIC > **Databricks 장점** : 전통적인 방법에서는 모델 검증을 위해 별도의 A/B 테스트 서버를 구축하거나,
# MAGIC > 수동으로 스크립트를 실행해야 했습니다. Databricks에서는 Unity Catalog의 에일리어스 시스템과
# MAGIC > MLflow의 평가 프레임워크가 통합되어 있어, 이 노트북 하나로 전체 검증 프로세스가 완료됩니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 검증 체크리스트 (4가지 관문)
# MAGIC 1. **모델 문서화 확인** - 모델에 대한 설명이 충분히 작성되어 있는가?
# MAGIC 2. **운영 데이터 추론 테스트** - 실제 데이터에서 에러 없이 예측이 되는가?
# MAGIC 3. **Champion 대비 성능 비교** - 기존 모델보다 성능이 같거나 더 좋은가?
# MAGIC 4. **비즈니스 KPI 평가** - 비즈니스 관점에서 순이익을 가져오는가?

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## 검증 프로세스 개요
# MAGIC
# MAGIC 이 노트북은 새 모델(Challenger)을 운영에 배포하기 전 **4단계 검증** 을 자동으로 수행합니다.
# MAGIC 제조 현장의 **게이트 검사(Gate Review)** 와 같은 구조입니다 - 각 단계(Gate)를 통과해야 다음으로 진행할 수 있습니다.
# MAGIC
# MAGIC | 단계 | 검증 항목 | 통과 기준 | 제조 비유 |
# MAGIC |------|-----------|-----------|-----------|
# MAGIC | **Check 1** | 모델 문서화 확인 | 모델 설명이 20자 이상 작성되어야 함 | 제품 사양서가 작성되어 있는지 확인 |
# MAGIC | **Check 2** | 운영 데이터 추론 테스트 | 에러 없이 예측이 정상 수행되어야 함 | 시제품이 실제 라인에서 문제없이 조립되는지 확인 |
# MAGIC | **Check 3** | Champion 대비 성능 비교 | Challenger F1 >= Champion F1 | 새 공정이 기존 공정보다 수율이 높은지 비교 |
# MAGIC | **Check 4** | 비즈니스 KPI 평가 | 예상 순 비즈니스 가치 > 0 | 새 공정 도입 시 총 비용 대비 이익이 양수인지 확인 |
# MAGIC
# MAGIC **핵심 원칙: 4가지 검증을 모두 통과해야만 Champion으로 승급됩니다.**
# MAGIC 하나라도 실패하면 Challenger는 "rejected(거부)" 태그가 붙고, 기존 Champion이 계속 운영됩니다.
# MAGIC 이것이 바로 **안전망(Safety Net)** 입니다 - 성능이 나쁜 모델이 절대로 운영에 투입되지 않습니다.
# MAGIC
# MAGIC > **Lakeflow Jobs 연동** : 이 검증 프로세스를 Workflows의 Job Task로 등록하면,
# MAGIC > 새 모델이 학습될 때마다 자동으로 검증이 실행되고, 통과 시 자동 승급됩니다.
# MAGIC > 사람이 매번 확인할 필요 없이 **완전 자동화된 CI/CD for ML** 파이프라인을 구축할 수 있습니다.

# COMMAND ----------

import mlflow
from mlflow import MlflowClient

client = MlflowClient()
model_name = f"{catalog}.{db}.lgit_predictive_maintenance"
model_alias = "Challenger"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 모델 정보 가져오기
# MAGIC
# MAGIC Unity Catalog에 등록된 Challenger 모델의 상세 정보를 조회합니다.
# MAGIC
# MAGIC **에일리어스(Alias)** 란 모델 버전에 붙이는 "이름표"입니다.
# MAGIC 예를 들어 모델 v3에 `@Challenger` 에일리어스를 붙이면, 코드에서 버전 번호(v3) 대신
# MAGIC `@Challenger`라는 이름으로 참조할 수 있습니다. 나중에 v4가 Challenger가 되면
# MAGIC 에일리어스만 옮기면 되므로, 코드를 수정할 필요가 없습니다.
# MAGIC
# MAGIC > **제조 비유** : 공장에서 "현재 사용 중인 금형"이라고 표시하는 태그와 같습니다.
# MAGIC > 금형이 교체되면 태그만 새 금형으로 옮기면 되고, 작업 지시서는 바꿀 필요가 없습니다.

# COMMAND ----------

# DBTITLE 1,Challenger 모델 정보 조회
model_details = client.get_model_version_by_alias(model_name, model_alias)
model_version = int(model_details.version)
model_run_id = model_details.run_id

print(f"검증 대상: {model_name} v{model_version} (@{model_alias})")
print(f"Run ID: {model_run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. 검증 체크 (Validation Checks)
# MAGIC
# MAGIC 이제부터 4가지 검증을 순서대로 수행합니다.
# MAGIC 각 검증의 결과(통과/실패)는 Unity Catalog의 **모델 태그(Tag)** 로 기록됩니다.
# MAGIC 이렇게 하면 나중에 "이 모델이 왜 승급/거부되었는지" 이력을 추적할 수 있습니다.
# MAGIC
# MAGIC ### Check 1: 모델 문서화 확인
# MAGIC
# MAGIC **왜 문서화가 중요한가?**
# MAGIC
# MAGIC AI 모델은 "블랙박스"가 될 위험이 있습니다. 6개월 후에 "이 모델은 어떤 데이터로 학습했지?",
# MAGIC "어떤 알고리즘을 썼지?", "왜 이 하이퍼파라미터를 선택했지?"라는 질문에 답할 수 없다면,
# MAGIC 모델을 유지보수하거나 개선하는 것이 불가능해집니다.
# MAGIC
# MAGIC > **제조 비유** : 제품에 대한 **BOM(Bill of Materials)** 이나 **공정 문서** 가 없다면,
# MAGIC > 문제 발생 시 원인을 추적할 수 없는 것과 같습니다. ISO 품질 인증에서도 문서화는 필수입니다.
# MAGIC
# MAGIC > **실무 경험** : 문서화를 "귀찮은 행정 업무"로 생각하는 분들이 많습니다. 하지만 제가 20년간 봐온 ML 프로젝트에서,
# MAGIC > 문서화가 없어서 1년 뒤에 모델을 아무도 건드리지 못하고 처음부터 다시 만드는 경우를 수십 번 목격했습니다.
# MAGIC > 모델 하나 다시 만드는 데 보통 2~3개월이 걸립니다. 문서화에 30분 투자하면 3개월을 아끼는 겁니다.
# MAGIC
# MAGIC 여기서는 최소 20자 이상의 모델 설명이 작성되어 있는지 확인합니다.

# COMMAND ----------

# DBTITLE 1,문서화 검증
has_description = bool(model_details.description and len(model_details.description) > 20)
print(f"모델 설명 존재: {has_description}")
if has_description:
    print(f"  → {model_details.description[:100]}...")
else:
    print("  → 경고: 모델에 충분한 설명이 없습니다. 최소 20자 이상 작성해주세요.")

client.set_model_version_tag(
    name=model_name, version=str(model_version),
    key="validation_has_description", value=str(has_description)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Check 2: 운영 데이터 추론 테스트
# MAGIC
# MAGIC **왜 추론 테스트가 필요한가?**
# MAGIC
# MAGIC 모델이 학습 환경에서는 잘 작동하더라도, 운영 환경의 데이터에서는 에러가 발생할 수 있습니다.
# MAGIC 예를 들어:
# MAGIC - 운영 데이터에 학습 시 없던 **결측값(NULL)** 이 있는 경우
# MAGIC - 센서 데이터의 **단위가 다른** 경우 (예: 학습은 섭씨, 운영은 화씨)
# MAGIC - 피처(입력 변수)의 **컬럼 순서** 가 달라진 경우
# MAGIC - 모델이 기대하는 **데이터 타입** 과 실제 데이터 타입이 다른 경우
# MAGIC
# MAGIC 이 검증에서는 실제 테스트 데이터를 모델에 넣어보고, 에러 없이 예측 결과가 나오는지 확인합니다.
# MAGIC
# MAGIC > **제조 비유** : 새로운 설비를 도입할 때, 실제 원자재를 투입해서 **시운전(Trial Run)** 을 하는 것과 같습니다.
# MAGIC > 설계 스펙상 문제가 없더라도, 실제 환경에서 예상치 못한 문제가 발생할 수 있기 때문입니다.
# MAGIC
# MAGIC > **실무 팁** : 추론 테스트에서 가장 흔하게 터지는 문제 3가지가 있습니다.
# MAGIC > (1) 학습 때 없던 NULL 값 — 센서가 일시적으로 끊기면 NULL이 들어옵니다.
# MAGIC > (2) 피처 순서 불일치 — 테이블 스키마가 바뀌면 모델이 엉뚱한 컬럼을 읽습니다.
# MAGIC > (3) 데이터 타입 변경 — integer가 string으로 바뀌는 것만으로 모델이 깨집니다.
# MAGIC > 이 세 가지를 이 단계에서 잡아내지 못하면, 운영 중에 갑자기 에러가 터지게 됩니다.

# COMMAND ----------

# DBTITLE 1,추론 테스트
import pandas as pd

# 테스트 데이터 로드
test_df = spark.table("lgit_pm_training").filter("split = 'test'")
feature_columns = [
    "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "temp_diff", "power", "tool_wear_rate", "strain",
    "overheat_flag", "product_quality", "risk_score"
]

try:
    # @Challenger 에일리어스로 모델을 참조합니다.
    # 에일리어스의 장점: 모델 버전이 바뀌어도 코드 변경 없이 새 모델로 자동 교체 가능.
    # result_type='double': 예측값을 실수(소수점 포함) 형식으로 반환 (0.0 ~ 1.0 확률값)
    model_udf = mlflow.pyfunc.spark_udf(
        spark,
        model_uri=f"models:/{model_name}@{model_alias}",
        result_type="double"
    )
    preds_df = test_df.withColumn("prediction", model_udf(*feature_columns))
    pred_count = preds_df.count()

    inference_passed = pred_count > 0
    print(f"추론 테스트 통과: {pred_count}건 정상 예측")

    # 추가 검증: 예측값 범위 및 분포 확인
    pred_values = preds_df.select("prediction").toPandas()["prediction"]
    null_count = pred_values.isna().sum()
    out_of_range = ((pred_values < 0) | (pred_values > 1)).sum()
    all_same = pred_values.nunique() <= 1

    if null_count > 0:
        print(f"  ⚠️ NULL 예측값: {null_count}건")
        inference_passed = False
    if out_of_range > 0:
        print(f"  ⚠️ 범위 이탈 예측값 (0~1 밖): {out_of_range}건")
        inference_passed = False
    if all_same:
        print(f"  ⚠️ 모든 예측값이 동일 — 모델 오류 의심")
        inference_passed = False

    if inference_passed:
        print(f"  ✅ 예측값 품질 검증 통과 (NULL={null_count}, 범위이탈={out_of_range})")
    display(preds_df.select(*feature_columns[:5], "machine_failure", "prediction").limit(10))
except Exception as e:
    inference_passed = False
    print(f"추론 테스트 실패: {e}")

client.set_model_version_tag(
    name=model_name, version=str(model_version),
    key="validation_inference_passed", value=str(inference_passed)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Check 3: Champion 대비 성능 비교
# MAGIC
# MAGIC **F1 Score란?**
# MAGIC
# MAGIC F1 Score는 모델의 **정밀도(Precision)** 와 **재현율(Recall)** 을 종합한 성능 지표입니다 (0~1, 높을수록 좋음).
# MAGIC - **정밀도(Precision)** : "고장이라고 예측한 것 중 실제 고장인 비율" (오탐을 줄이는 능력)
# MAGIC - **재현율(Recall)** : "실제 고장 중 모델이 잡아낸 비율" (미탐지를 줄이는 능력)
# MAGIC - **F1 Score** : 정밀도와 재현율의 조화 평균. 두 지표의 균형을 나타냅니다.
# MAGIC
# MAGIC > **제조 비유** : 품질 검사에서 정밀도는 "불량 판정한 제품 중 진짜 불량 비율"이고,
# MAGIC > 재현율은 "전체 불량품 중 검사에서 잡아낸 비율"입니다. F1은 이 둘의 균형입니다.
# MAGIC
# MAGIC > **멘토 조언** : F1 Score는 편리한 지표이지만, 제조업에서는 **Recall(재현율)에 더 가중치를 두는 것** 을 권장합니다.
# MAGIC > 고장을 놓치는 것(FN)이 오탐(FP)보다 훨씬 치명적이기 때문입니다. 실무에서는 F1 대신 F-beta Score(beta=2)를
# MAGIC > 사용해서 Recall에 더 높은 가중치를 주는 경우도 많습니다. 다만 이 교육에서는 이해의 편의를 위해 F1을 사용합니다.
# MAGIC
# MAGIC **비교 로직:**
# MAGIC - Challenger의 F1 Score가 Champion의 F1 Score보다 **같거나 높으면** 통과
# MAGIC - Champion이 아직 없는 경우(첫 번째 모델)는 자동으로 통과 처리
# MAGIC - 이 비교는 학습 시 기록된 **검증 데이터(validation set)** 기준의 F1을 사용합니다

# COMMAND ----------

# DBTITLE 1,성능 비교 검증
challenger_f1 = mlflow.get_run(model_run_id).data.metrics.get('val_f1_score', 0)

try:
    champion_model = client.get_model_version_by_alias(model_name, "Champion")
    if champion_model.version != model_details.version:
        champion_f1 = mlflow.get_run(champion_model.run_id).data.metrics.get('val_f1_score', 0)
        print(f"Champion F1: {champion_f1:.4f} vs Challenger F1: {challenger_f1:.4f}")
        metric_passed = challenger_f1 >= champion_f1
    else:
        print("Challenger = Champion (동일 버전). 첫 번째 모델이므로 승인합니다.")
        metric_passed = True
except Exception:
    print("Champion 모델이 없습니다. 첫 번째 모델이므로 승인합니다.")
    metric_passed = True

print(f"성능 검증 통과: {metric_passed}")

client.set_model_version_tag(
    name=model_name, version=str(model_version),
    key="validation_metric_passed", value=str(metric_passed)
)

# COMMAND ----------

# MAGIC %md
# MAGIC > **현업 팁** : 전체 성능만 보면 안 됩니다. 제품 유형(L/M/H)별, 교대 시간대별, 특정 설비별로
# MAGIC > 성능을 슬라이스해서 봐야 합니다. 전체 F1이 0.9여도 특정 제품 유형에서 F1이 0.3이면
# MAGIC > 그 유형의 설비는 사실상 보호받지 못하고 있는 것입니다.
# MAGIC > 이것을 **Slice-based Evaluation** 이라고 하며, Responsible AI의 핵심 요소입니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Check 4: 비즈니스 KPI 평가
# MAGIC
# MAGIC **왜 ML 성능 지표만으로는 부족한가?**
# MAGIC
# MAGIC > **핵심 교훈** : 순수 ML 메트릭만으로 모델을 평가하면 현업에서 외면받습니다.
# MAGIC > "정확도 92%입니다"는 경영진에게 아무 의미가 없어요.
# MAGIC > "이 모델을 배포하면 연간 예방정비 비용 3억을 절감하면서 돌발 고장은 70% 줄일 수 있습니다"라고 해야 합니다.
# MAGIC > 20년간 수십 개 제조사에서 일하면서 배운 것 — **ML 엔지니어가 비즈니스 언어를 못 하면 프로젝트는 1년 안에 사라집니다.**
# MAGIC
# MAGIC F1 Score가 0.95로 매우 높은 모델이라도, 비즈니스 관점에서는 손해를 볼 수 있습니다.
# MAGIC 예를 들어, 모델이 99%의 정확도를 보이지만 **가장 비용이 큰 고장 유형을 놓치는 경우**,
# MAGIC 전체적인 정확도는 높지만 실제 비용은 더 크게 발생할 수 있습니다.
# MAGIC
# MAGIC > **LG이노텍 예시** : 카메라 모듈 생산 라인에서 "렌즈 정렬 불량"은 전체 불량의 2%에 불과하지만,
# MAGIC > 하나당 폐기 비용이 일반 불량의 10배입니다. 이 2%를 놓치면 전체 불량 검출률은 98%로 높지만,
# MAGIC > 비용 관점에서는 오히려 손해가 됩니다.
# MAGIC
# MAGIC 이 검증에서는 **혼동행렬(Confusion Matrix)** 을 기반으로 각 예측 결과의 비즈니스 비용/이익을 계산합니다.
# MAGIC
# MAGIC ### 혼동행렬과 비즈니스 비용 매핑
# MAGIC
# MAGIC > **멘토 조언** : 혼동행렬을 볼 때 가장 중요한 것은 **FN(False Negative)** 입니다.
# MAGIC > 고장을 놓치는 것이 오탐(FP)보다 훨씬 치명적입니다. 자동차 부품 검사에서 불량을 놓치면 리콜입니다.
# MAGIC > LG Innotek의 카메라 모듈도 마찬가지 — 불량이 고객사까지 가면 비용이 100배로 뛰어요.
# MAGIC > FP는 "불필요한 점검 비용"이지만, FN은 "라인 정지 + 납기 지연 + 고객 클레임"입니다.
# MAGIC > 제가 본 최악의 케이스는, FN 1건 때문에 라인이 48시간 정지되고 납기가 1주일 밀린 적이 있습니다.
# MAGIC
# MAGIC **혼동행렬을 화재 경보기에 비유하면:**
# MAGIC
# MAGIC | | 예측: 정상 (0) | 예측: 고장 (1) |
# MAGIC |---|---|---|
# MAGIC | **실제: 정상 (0)**| **TN (True Negative)**- 화재 없는데 경보도 안 울림. 정상 상황. 비용 없음 | **FP (False Positive, 오탐)**- 화재 없는데 경보가 울림. 소방차 출동, 라인 중단 등 **불필요한 비용** 발생 |
# MAGIC | **실제: 고장 (1)**| **FN (False Negative, 미탐지)**- 실제 화재인데 경보가 안 울림. **가장 위험!** 설비 파손, 대규모 다운타임 발생 | **TP (True Positive, 정탐)**- 실제 화재인데 경보가 울림. 초기 진압 성공. **예방 정비로 큰 손실 방지** |
# MAGIC
# MAGIC **LG이노텍 생산 라인에서의 비용 임팩트:**
# MAGIC - **FN (미탐지) = 가장 비싼 실수** : 설비가 고장 나는데 모델이 "정상"이라고 판단 → 갑작스러운 라인 중단, 후속 공정 지연, 납기 지연까지 이어질 수 있음
# MAGIC - **FP (오탐) = 낭비 비용** : 정상 설비인데 모델이 "고장 예측" → 불필요한 정비 인력 투입, 생산 중단
# MAGIC - **TP (정탐) = 가장 큰 가치** : 고장을 사전에 감지 → 계획된 정비로 대처, 다운타임 최소화
# MAGIC - **TN (정상 판정) = 기본** : 정상 상태를 정상으로 판단 → 비용 없음

# COMMAND ----------

# DBTITLE 1,비즈니스 가치 평가
from sklearn.metrics import confusion_matrix
import numpy as np

# [비용 파라미터 안내]
# 이 비용 파라미터는 교육용 예시값입니다.
# 실제 현장에서는 LG Innotek의 실제 비용 데이터를 반영해야 합니다.
# (예: 설비 다운타임 시간당 비용, 실제 정비 인건비/부품비 등)
# 비용 파라미터 (제조 현장 기준)
COST_DOWNTIME = 50000       # 미탐지 고장으로 인한 다운타임 비용 (원)
COST_PREVENTIVE = 5000      # 예방 정비 비용 (원)
COST_FALSE_ALARM = 3000     # 오탐으로 인한 불필요 정비 비용 (원)
SAVING_PREVENTED = 45000    # 예방 정비로 절감한 비용 (원)

# 예측 수행
preds_pd = preds_df.select("machine_failure", "prediction").toPandas()
preds_pd["pred_label"] = (preds_pd["prediction"] > 0.5).astype(int)

# 혼동행렬(Confusion Matrix) 이해하기:
# 실제값과 예측값의 일치/불일치를 2x2 표로 나타낸 것입니다.
#
#               예측: 정상(0)   예측: 고장(1)
#  실제: 정상(0)    tn (정확)       fp (오탐)
#  실제: 고장(1)    fn (미탐지)     tp (정확)
#
# tn = True Negative  : 실제 정상 → 정상으로 예측 (올바름)
# fp = False Positive : 실제 정상 → 고장으로 예측 (오탐, 불필요한 정비 발생)
# fn = False Negative : 실제 고장 → 정상으로 예측 (미탐지, 설비 다운타임 발생 - 가장 위험!)
# tp = True Positive  : 실제 고장 → 고장으로 예측 (올바름, 예방 정비 가능)
tn, fp, fn, tp = confusion_matrix(preds_pd["machine_failure"], preds_pd["pred_label"]).ravel()

# 비즈니스 가치 계산
business_value = (
    tp * SAVING_PREVENTED          # 예방 성공
    - fp * COST_FALSE_ALARM        # 오탐 비용
    - fn * COST_DOWNTIME           # 미탐지 비용
    - tp * COST_PREVENTIVE         # 정비 비용
)

print(f"=== 비즈니스 가치 분석 ===")
print(f"True Positive (예방 성공):  {tp}건 → 절감: {tp * SAVING_PREVENTED:,}원")
print(f"False Positive (오탐):      {fp}건 → 비용: {fp * COST_FALSE_ALARM:,}원")
print(f"False Negative (미탐지):    {fn}건 → 비용: {fn * COST_DOWNTIME:,}원")
print(f"True Negative (정상):       {tn}건")
print(f"────────────────────────────────────")
print(f"예상 순 비즈니스 가치: {business_value:,}원")

business_kpi_passed = business_value > 0
print(f"\n비즈니스 KPI 통과: {business_kpi_passed}")

client.set_model_version_tag(
    name=model_name, version=str(model_version),
    key="validation_business_value", value=f"{business_value}"
)
client.set_model_version_tag(
    name=model_name, version=str(model_version),
    key="validation_business_kpi_passed", value=str(business_kpi_passed)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 종합 검증 결과 및 Champion 승급
# MAGIC
# MAGIC 모든 검증이 끝났습니다. 이제 4가지 검증 결과를 종합하여 **최종 판정** 을 내립니다.
# MAGIC
# MAGIC **승급 로직:**
# MAGIC - 4가지 검증이 **모두 PASS** 이면 → Challenger를 Champion으로 **자동 승급**
# MAGIC - 하나라도 **FAIL** 이면 → Challenger는 **거부(rejected)** 처리, 기존 Champion 유지
# MAGIC
# MAGIC > **안전망 설계 철학** : 이 검증 시스템은 "하나라도 문제가 있으면 통과시키지 않는" 보수적 접근입니다.
# MAGIC > 제조 현장에서 품질 이상이 발견되면 라인을 멈추는 **안돈(Andon) 시스템** 과 같은 철학입니다.
# MAGIC > 모델이 조금이라도 의심스러우면 기존의 검증된 Champion을 유지하는 것이 안전합니다.
# MAGIC
# MAGIC 승급/거부 결과는 모델 태그로 기록되어, Unity Catalog에서 언제든 이력을 확인할 수 있습니다.

# COMMAND ----------

# DBTITLE 1,검증 결과 종합 및 승급 결정
# [Champion 승급 조건 안내]
# 아래 4가지 조건을 모두 충족해야 Champion으로 자동 승급됩니다.
# 하나라도 실패하면 'rejected' 태그가 붙고 Champion 승급이 거부됩니다.
#  1. has_description    - 모델에 충분한 설명(문서)이 있는가?
#  2. inference_passed   - 운영 데이터에서 에러 없이 예측이 되는가?
#  3. metric_passed      - 기존 Champion보다 성능이 같거나 더 좋은가?
#  4. business_kpi_passed - 비즈니스 관점에서 순 가치가 플러스인가?
all_passed = all([has_description, inference_passed, metric_passed, business_kpi_passed])

print(f"=== 검증 결과 종합 ===")
print(f"  문서화 확인:     {'PASS' if has_description else 'FAIL'}")
print(f"  추론 테스트:     {'PASS' if inference_passed else 'FAIL'}")
print(f"  성능 비교:       {'PASS' if metric_passed else 'FAIL'}")
print(f"  비즈니스 KPI:    {'PASS' if business_kpi_passed else 'FAIL'}")
print(f"────────────────────────────────────")
print(f"  최종 결과:       {'PASS — Champion 승급!' if all_passed else 'FAIL — 재검토 필요'}")

if all_passed:
    # Champion으로 승급
    client.set_registered_model_alias(
        name=model_name,
        alias="Champion",
        version=model_version
    )
    client.set_model_version_tag(
        name=model_name, version=str(model_version),
        key="validation_status", value="approved"
    )
    print(f"\n모델 v{model_version}이 Champion으로 승급되었습니다!")
else:
    client.set_model_version_tag(
        name=model_name, version=str(model_version),
        key="validation_status", value="rejected"
    )
    print(f"\n모델 v{model_version}은 검증에 실패했습니다. 재검토가 필요합니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Databricks UI 확인 포인트
# MAGIC
# MAGIC 1. **Models > lgit_predictive_maintenance** 다시 확인
# MAGIC 2. **Aliases** 가 변경되었는지 확인: Challenger가 Champion으로 승급했다면 alias가 이동
# MAGIC 3. 이전 Champion 버전의 **Tags**: `validation_status = passed` 또는 `rejected` 확인
# MAGIC 4. 새 Champion 버전의 **Tags**: `promoted_from = challenger`, `validation_date` 확인
# MAGIC
# MAGIC > **팁**: Tags를 보면 "이 모델이 왜 Champion이 되었는지" 이력을 추적할 수 있습니다

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC ### 이 노트북에서 수행한 작업
# MAGIC
# MAGIC | 단계 | 검증 내용 | 의미 |
# MAGIC |------|-----------|------|
# MAGIC | **Check 1** | 모델 문서화 확인 | 모델의 추적 가능성 보장 |
# MAGIC | **Check 2** | 운영 데이터 추론 테스트 | 실제 환경에서의 안정성 확인 |
# MAGIC | **Check 3** | Champion-Challenger 성능 비교 | ML 성능 기준 통과 확인 |
# MAGIC | **Check 4** | 비즈니스 KPI 평가 | 제조 현장 비용 관점의 가치 검증 |
# MAGIC | **최종** | Champion 자동 승급/거부 | 안전한 모델 배포 보장 |
# MAGIC
# MAGIC ### 핵심 포인트
# MAGIC
# MAGIC - **ML 성능(F1 Score)과 비즈니스 가치(비용 분석)를 모두 평가** 합니다. 둘 다 통과해야 승급됩니다.
# MAGIC - 모든 검증 결과는 **Unity Catalog 태그로 기록** 되어 감사 추적(Audit Trail)이 가능합니다.
# MAGIC - Lakeflow Jobs와 연동하면 **모델 학습 → 검증 → 승급** 이 완전 자동화됩니다.
# MAGIC - 검증 실패 시 기존 Champion이 유지되므로, 운영 서비스에 영향이 없습니다 (** 무중단 배포**).
# MAGIC
# MAGIC > **20년 경험의 한 마디** : 이 검증 파이프라인이 가장 큰 가치를 발휘하는 순간은, 누군가 "급하니까 검증 생략하고
# MAGIC > 바로 배포합시다"라고 할 때입니다. 그 유혹을 이겨내는 것이 프로와 아마추어의 차이입니다.
# MAGIC > 저도 "이번 한 번만"이라고 검증을 생략했다가, 운영 모델이 3일간 쓰레기 예측을 한 경험이 있습니다.
# MAGIC > 그 3일 동안의 손실은, 검증에 필요한 30분의 1,000배였습니다.
# MAGIC
# MAGIC **다음 단계:** [배치 추론]($./06_batch_inference) - Champion으로 승급된 모델이 실제 운영 데이터에 대해 예측을 수행합니다.
