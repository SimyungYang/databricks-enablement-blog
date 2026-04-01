# Databricks notebook source
# MAGIC %md
# MAGIC # 모델 모니터링 (Model Monitoring)
# MAGIC
# MAGIC ## 왜 모델 모니터링이 필요한가?
# MAGIC
# MAGIC AI 모델은 소프트웨어와 다릅니다. 소프트웨어는 한 번 배포하면 로직이 변하지 않지만,
# MAGIC **AI 모델은 시간이 지나면서 성능이 저하**될 수 있습니다. 이것을 **모델 드리프트(Model Drift)** 라고 합니다.
# MAGIC
# MAGIC > **반도체 제조 비유**: 반도체 Fab에서 웨이퍼 온도 센서의 평균값이 계절마다 2~3도씩 달라집니다.
# MAGIC > 여름에 학습된 모델은 겨울 데이터의 패턴을 제대로 이해하지 못할 수 있습니다.
# MAGIC > 또한, 새로운 배치(Batch)의 원자재가 이전과 다른 열적 특성을 가지면,
# MAGIC > 모델이 "처음 보는 상황"에서 예측해야 하므로 정확도가 떨어집니다.
# MAGIC
# MAGIC > **LG이노텍 예시**: 카메라 모듈 생산 라인에서 신규 렌즈 공급업체 전환 후,
# MAGIC > 렌즈 정렬 센서값의 분포가 미세하게 달라질 수 있습니다.
# MAGIC > 모니터링 없이는 이런 변화를 감지하지 못하고, 모델 성능이 서서히 저하됩니다.
# MAGIC
# MAGIC **모니터링은 MLOps의 핵심입니다.** 학습 → 검증 → 배포까지는 모델을 "만드는" 단계이고,
# MAGIC 모니터링은 모델을 "관리하는" 단계입니다. 운영 중인 모델의 건강 상태를 지속적으로 체크하여,
# MAGIC 문제가 발생하기 전에 선제 대응합니다.
# MAGIC
# MAGIC > **솔직한 이야기**: 모니터링은 ML 프로젝트에서 가장 무시당하는 단계입니다.
# MAGIC > 모든 팀이 모델 학습에는 열정적이지만, 배포 후 모니터링은 "나중에 하자"고 합니다.
# MAGIC > 그리고 3개월 후에 모델이 쓰레기 예측을 하고 있는 것을 발견합니다.
# MAGIC > 제가 20년간 봐온 ML 프로젝트의 절반 이상이 이 패턴으로 실패했습니다.
# MAGIC > 모델 학습은 "출산"이고, 모니터링은 "양육"입니다. 양육 없는 출산은 무책임합니다.
# MAGIC
# MAGIC ## Databricks 핵심 기능
# MAGIC
# MAGIC | 기능 | 설명 | 전통적 방법과 비교 |
# MAGIC |------|------|-------------------|
# MAGIC | **Data Quality Monitoring(구 Data Quality Monitoring)** | 데이터 품질 및 모델 성능 자동 모니터링 | Grafana + Prometheus 직접 구축 필요 |
# MAGIC | **Delta Lake Time Travel** | 시점별 데이터 비교 (과거 데이터 즉시 조회) | 별도 스냅샷 관리 필요 |
# MAGIC | **SQL Analytics** | 모니터링 대시보드를 SQL로 간편하게 구축 | Kibana/Superset 별도 설치 필요 |
# MAGIC | **Alerts** | 임계값 초과 시 이메일/Slack 자동 알림 | 알림 서버 별도 구축 필요 |

# COMMAND ----------

# MAGIC %md
# MAGIC ### ⚠️ 전제조건
# MAGIC - 이 노트북을 실행하기 전에 **06_batch_inference** 노트북을 먼저 실행해야 합니다
# MAGIC - `lgit_pm_inference_results` 테이블이 존재해야 합니다

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ### 이 노트북의 목적과 중요성
# MAGIC
# MAGIC AI 모델은 한 번 배포하면 끝이 아닙니다. 공장 환경에서는 ** 계절 변화, 설비 노후화, 원자재 변경,
# MAGIC 공정 조건 변경** 등으로 인해 센서 데이터의 패턴이 조금씩 달라집니다.
# MAGIC 모델이 학습할 때 보지 못한 새로운 패턴이 생기면 예측 정확도가 떨어집니다.
# MAGIC
# MAGIC **모델 성능 저하의 실제 원인 예시 (제조 환경):**
# MAGIC
# MAGIC | 원인 | 영향받는 센서 | 드리프트 정도 | 발생 빈도 |
# MAGIC |------|-------------|-------------|-----------|
# MAGIC | 계절 변화 (여름→겨울) | 공기온도, 공정온도 | 중간 (5~15%) | 연 2~4회 |
# MAGIC | 신규 설비 도입 | 회전속도, 토크 | 높음 (20% 이상) | 비정기적 |
# MAGIC | 절삭유/윤활유 교체 | 토크, 온도 | 낮음~중간 | 월 1~2회 |
# MAGIC | 공구(Tool) 일괄 교체 | 공구 마모도, 토크 | 높음 | 주기적 |
# MAGIC | 원자재 로트(Lot) 변경 | 전반적 센서값 | 낮음~중간 | 수시 |
# MAGIC
# MAGIC > **LG이노텍 구체적 시나리오**: 반도체 패키징 공정에서 새로운 에폭시(Epoxy) 수지로 전환했을 때,
# MAGIC > 경화 온도 프로파일이 달라지면서 온도 센서의 분포가 변합니다. 모델이 이전 수지 기준으로 학습되었기 때문에,
# MAGIC > 새로운 수지 환경에서는 고장 예측 정확도가 떨어질 수 있습니다.
# MAGIC > 모니터링이 이 변화를 조기에 감지하면, 새 데이터로 모델을 재학습하여 정확도를 회복할 수 있습니다.
# MAGIC
# MAGIC > **제조업 드리프트 원인 TOP 3**: 제조업에서 드리프트가 발생하는 가장 흔한 원인 3가지를 말씀드리겠습니다.
# MAGIC > **(1) 계절 변화** — 여름/겨울 온도 차이가 공기온도, 공정온도 센서에 직접 영향을 줍니다. 연 2~4회 발생.
# MAGIC > **(2) 원자재 로트 변경** — 새 로트의 물성이 미세하게 달라서 토크, 온도 분포가 변합니다. 수시로 발생.
# MAGIC > **(3) 설비 교체 후 센서 특성 변화** — 신규 설비의 센서 캘리브레이션이 기존과 다릅니다. 비정기적.
# MAGIC > 이 세 가지만 모니터링해도 대부분의 드리프트를 잡을 수 있습니다.
# MAGIC > 20년간 수십 개 공장을 돌면서 확인한 경험적 사실입니다.
# MAGIC
# MAGIC 이 노트북에서는 다음을 수행합니다:
# MAGIC 1. **데이터 드리프트 탐지** - 운영 데이터가 학습 데이터와 얼마나 달라졌는지 수치로 측정
# MAGIC 2. **모델 성능 추이 관찰** - 시간에 따른 예측 분포 변화를 SQL로 확인
# MAGIC 3. **자동 모니터링 설정** - Databricks Data Quality Monitoring으로 24/7 상시 감시 체계 구축
# MAGIC
# MAGIC > **Databricks 장점**: 전통적인 모니터링은 별도의 모니터링 서버(Prometheus), 대시보드(Grafana),
# MAGIC > 알림 시스템(PagerDuty) 등을 각각 구축하고 연결해야 합니다. 이것만으로도 수주~수개월의 인프라 작업이 필요합니다.
# MAGIC > Databricks에서는 **Data Quality Monitoring** 기능이 플랫폼에 내장되어 있어,
# MAGIC > 코드 몇 줄로 자동화된 모니터링 대시보드, 드리프트 탐지, 알림 설정까지 한 번에 완료됩니다.

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC > **위 셀 설명**: 환경 설정 스크립트를 실행합니다. 실행 후 다음 변수를 사용할 수 있습니다:
# MAGIC > - `catalog`: Unity Catalog 이름 (예: `simyung_yang`)
# MAGIC > - `db`: 스키마 이름 (예: `lgit_mlops_poc`)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 모니터링 대상 데이터 확인
# MAGIC
# MAGIC ### 이 섹션에서 하는 일
# MAGIC 모니터링을 시작하기 전에, 먼저 **어떤 데이터를 모니터링할 것인지** 확인합니다.
# MAGIC
# MAGIC `lgit_pm_inference_results` 테이블은 06_batch_inference 노트북에서 생성된 테이블로,
# MAGIC 모델이 실제 운영 환경에서 예측한 결과들이 저장되어 있습니다.
# MAGIC
# MAGIC **포함된 정보:**
# MAGIC - 입력으로 사용된 센서 값들 (온도, 회전속도, 토크, 공구 마모도)
# MAGIC - 모델이 예측한 고장 확률 (`failure_probability`)
# MAGIC - 예측 결과 (`predicted_failure`: 0=정상, 1=고장 예측)
# MAGIC - 예측 시각 (`inference_timestamp`)
# MAGIC - 어떤 버전의 모델이 예측했는지 (`model_version`)
# MAGIC
# MAGIC 이 데이터를 분석해서 모델이 안정적으로 작동하고 있는지 파악합니다.

# COMMAND ----------

# DBTITLE 1,추론 결과 테이블 확인
display(spark.table("lgit_pm_inference_results").limit(10))  # 추론 결과 테이블에서 상위 10개 행을 가져와 화면에 표시합니다

# COMMAND ----------

# MAGIC %md
# MAGIC ### 위 결과 해석 방법
# MAGIC
# MAGIC 표에서 확인해야 할 내용:
# MAGIC - **`failure_probability` 컬럼**: 고장 확률 값 (0.0 ~ 1.0). 0에 가까울수록 정상, 1에 가까울수록 고장 위험
# MAGIC - **`predicted_failure` 컬럼**: 최종 예측 결과. 일반적으로 고장 확률 0.5 이상이면 1(고장)로 분류
# MAGIC - **`inference_timestamp` 컬럼**: 언제 예측했는지. 시간대별 예측 패턴을 파악할 수 있습니다
# MAGIC - **`model_version` 컬럼**: 어떤 버전 모델이 사용되었는지. 버전 변경 시 성능 비교에 활용
# MAGIC
# MAGIC **정상 범위**: 실제 공정에서 고장률이 ~3% 수준이라면, `predicted_failure = 1`인 행의 비율도 비슷해야 합니다.
# MAGIC 갑자기 예측 고장률이 20%를 넘는다면 데이터 문제 또는 모델 문제를 의심해야 합니다.
# MAGIC
# MAGIC > **멘토 팁**: 예측 고장률의 "정상 범위"를 미리 정의해두는 것이 중요합니다.
# MAGIC > 보통 학습 데이터의 고장률 +/- 50%를 1차 경고선으로 잡습니다.
# MAGIC > 예: 학습 데이터 고장률 3% → 정상 범위 1.5%~4.5% → 이 범위를 벗어나면 조사 시작.
# MAGIC > 이 기준을 SQL Alert로 설정해두면 자동으로 알림이 옵니다.
# MAGIC
# MAGIC 다음 섹션에서는 이 데이터와 학습 데이터를 비교하여 데이터 분포가 얼마나 변했는지 수치로 측정합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. 데이터 드리프트 탐지
# MAGIC
# MAGIC ### 데이터 드리프트(Data Drift)란?
# MAGIC
# MAGIC **데이터 드리프트** 는 운영 데이터의 통계적 분포가 모델 학습 시점의 데이터와 달라지는 현상입니다.
# MAGIC 쉽게 말해, **모델이 "공부"할 때 본 시험 문제와 실제 시험 문제가 다른 유형인 상황** 입니다.
# MAGIC
# MAGIC > **일상 비유**: 서울 날씨로 학습한 일기예보 AI를 부산에 적용하면 정확도가 떨어집니다.
# MAGIC > 기온, 습도, 풍속의 분포가 다르기 때문입니다. 이것이 바로 데이터 드리프트입니다.
# MAGIC
# MAGIC > **LG이노텍 구체적 예시**:
# MAGIC > - **신규 설비 도입**: CNC 선반을 신규 모델로 교체하면 회전속도(RPM)의 범위와 진동 패턴이 달라집니다
# MAGIC > - **절삭유 교체**: 새로운 절삭유는 열전도율이 다르므로 공정 온도 분포가 변합니다
# MAGIC > - **계절 변화**: 여름과 겨울의 공장 내부 온도 차이가 센서값에 영향을 미칩니다
# MAGIC > - **원자재 로트 변경**: 새로운 로트의 원자재는 미세한 물성 차이를 가질 수 있습니다
# MAGIC
# MAGIC ### 이 섹션에서 하는 일
# MAGIC
# MAGIC 모델은 **학습 데이터의 패턴** 을 학습합니다. 운영 데이터가 학습 데이터와 다른 분포를 가지면,
# MAGIC 모델은 "처음 보는 상황"에서 예측을 해야 하므로 성능이 저하됩니다.
# MAGIC
# MAGIC 이를 탐지하기 위해 두 가지 방법을 단계적으로 사용합니다:
# MAGIC 1. **기초 통계 비교** (이번 셀): 평균(mean)과 표준편차(std)로 전체적인 차이를 "빠르게" 확인
# MAGIC 2. **PSI 지수 계산** (다음 셀): 분포 전체를 정밀하게 비교하는 통계적 지표
# MAGIC
# MAGIC > **왜 두 가지 방법을 모두 사용하는가?**
# MAGIC > 평균/표준편차만으로는 분포의 "모양" 변화를 놓칠 수 있습니다.
# MAGIC > 예: 평균은 같지만, 데이터가 양 극단으로 분산된 경우 (이봉 분포). PSI는 이런 변화도 감지합니다.
# MAGIC
# MAGIC > **Databricks 장점**: Delta Lake에 학습 데이터와 추론 데이터가 모두 저장되어 있어,
# MAGIC > `spark.table()` 한 줄로 즉시 데이터를 불러와 비교할 수 있습니다.
# MAGIC > 전통적인 방법에서는 학습 데이터를 CSV/Parquet 파일로 따로 관리하고,
# MAGIC > 스토리지 경로를 기억해서 수동으로 불러와야 했습니다.

# COMMAND ----------

# DBTITLE 1,학습 vs 추론 데이터 분포 비교
import pyspark.sql.functions as F  # PySpark의 집계 함수(평균, 표준편차 등)를 사용하기 위해 임포트

# 모니터링할 센서 피처 컬럼 목록 정의
feature_columns = [
    "air_temperature_k",      # 공기 온도 (켈빈)
    "process_temperature_k",  # 공정 온도 (켈빈)
    "rotational_speed_rpm",   # 회전 속도 (RPM)
    "torque_nm",              # 토크 (뉴턴미터)
    "tool_wear_min"           # 공구 마모 시간 (분)
]

# 학습 데이터의 각 피처별 평균과 표준편차를 계산
train_stats = (
    spark.table("lgit_pm_training")       # Delta Lake에서 학습 데이터 테이블 로드
    .filter("split = 'train'")            # 학습용 데이터만 필터링 (검증/테스트 제외)
    .select([F.mean(c).alias(f"{c}_mean") for c in feature_columns] +   # 각 피처의 평균 계산
            [F.stddev(c).alias(f"{c}_std") for c in feature_columns])   # 각 피처의 표준편차 계산
)

# 추론(운영) 데이터의 각 피처별 평균과 표준편차를 계산
inference_stats = (
    spark.table("lgit_pm_inference_results")  # Delta Lake에서 추론 결과 테이블 로드
    .select([F.mean(c).alias(f"{c}_mean") for c in feature_columns] +   # 각 피처의 평균 계산
            [F.stddev(c).alias(f"{c}_std") for c in feature_columns])   # 각 피처의 표준편차 계산
)

print("=== 학습 데이터 통계 ===")
display(train_stats)   # 학습 데이터 통계 테이블 출력
print("=== 추론 데이터 통계 ===")
display(inference_stats)  # 추론 데이터 통계 테이블 출력

# COMMAND ----------

# MAGIC %md
# MAGIC ### 통계 비교 결과 해석 방법
# MAGIC
# MAGIC 위에 두 개의 표가 출력됩니다 - **학습 데이터**와 **추론(운영) 데이터** 의 통계입니다.
# MAGIC
# MAGIC **확인 포인트:**
# MAGIC | 상황 | 의미 | 조치 |
# MAGIC |------|------|------|
# MAGIC | 평균값 차이가 10% 이내 | 정상 - 데이터 분포가 유사함 | 계속 모니터링 |
# MAGIC | 평균값 차이가 10~30% | 주의 - 데이터 패턴 변화 시작 | 원인 조사 |
# MAGIC | 평균값 차이가 30% 초과 | 경고 - 데이터 드리프트 발생 | 모델 재학습 검토 |
# MAGIC
# MAGIC **예시**: `air_temperature_k_mean`이 학습 데이터에서 300K였는데 추론 데이터에서 330K라면,
# MAGIC 공정 온도가 크게 높아진 것이므로 모델 재학습이 필요할 수 있습니다.
# MAGIC
# MAGIC 평균/표준편차만으로는 전체 분포 변화를 포착하기 어렵습니다.
# MAGIC 다음 섹션에서 더 정확한 측정 방법인 **PSI** 를 사용합니다.
# MAGIC
# MAGIC > **실무 팁**: 평균/표준편차 비교는 "1차 스크리닝"으로 매우 유용합니다.
# MAGIC > 계산이 빠르고 직관적이니까요. 하지만 함정이 있습니다.
# MAGIC > 예를 들어 학습 데이터의 토크가 균일하게 20~60Nm이었는데, 운영 데이터에서 10Nm와 70Nm에 집중되면
# MAGIC > 평균은 40Nm으로 동일하지만, 모델이 보는 세계는 완전히 달라진 겁니다.
# MAGIC > 이것이 PSI가 필요한 이유입니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### PSI (Population Stability Index) 란?
# MAGIC
# MAGIC **PSI**는 두 데이터 분포가 얼마나 다른지를 **하나의 숫자** 로 나타내는 통계 지표입니다.
# MAGIC 금융업계에서 신용평가 모델의 안정성을 측정하기 위해 개발되었으며, 현재는 모든 ML 모니터링에서 표준적으로 사용됩니다.
# MAGIC
# MAGIC > **멘토 조언**: PSI를 쓰는 이유가 있습니다. KL Divergence도 좋지만 PSI가 업계 표준이 된 것은
# MAGIC > 해석이 직관적이기 때문입니다. **< 0.1 안정, 0.1~0.2 주의, > 0.2 경고** — 이 기준을 외우면 됩니다.
# MAGIC > 20년간 수백 번 써봤지만 이 기준이 틀린 적이 거의 없습니다.
# MAGIC > KL Divergence는 비대칭이라 "학습→운영"과 "운영→학습" 비교 결과가 다르고, 해석이 까다롭습니다.
# MAGIC > PSI는 대칭적이고, 업계 전체가 같은 기준을 쓰기 때문에 팀 간 소통이 쉽습니다.
# MAGIC > 경영진에게 "PSI가 0.3입니다"라고 하면 한마디로 통합니다.
# MAGIC
# MAGIC #### 쉬운 비유: 학생 시험 점수 분포
# MAGIC
# MAGIC 1학기 시험 점수 분포(= 학습 데이터)와 2학기 시험 점수 분포(= 운영 데이터)를 비교한다고 생각해보세요.
# MAGIC
# MAGIC **분포가 비슷한 경우 (PSI 낮음):**
# MAGIC ```
# MAGIC 1학기: [0~60점: 10%] [60~70점: 20%] [70~80점: 40%] [80~90점: 20%] [90~100점: 10%]
# MAGIC 2학기: [0~60점: 12%] [60~70점: 18%] [70~80점: 38%] [80~90점: 22%] [90~100점: 10%]
# MAGIC → PSI ≈ 0.01 (거의 동일한 분포)
# MAGIC ```
# MAGIC
# MAGIC **분포가 크게 다른 경우 (PSI 높음):**
# MAGIC ```
# MAGIC 1학기: [0~60점: 10%] [60~70점: 20%] [70~80점: 40%] [80~90점: 20%] [90~100점: 10%]
# MAGIC 2학기: [0~60점:  2%] [60~70점:  5%] [70~80점: 13%] [80~90점: 30%] [90~100점: 50%]
# MAGIC → PSI ≈ 0.85 (분포가 완전히 달라짐)
# MAGIC ```
# MAGIC
# MAGIC > **LG이노텍 예시로 바꾸면**: 학습 시 회전속도(RPM) 분포가 1000~2000 RPM에 집중되어 있었는데,
# MAGIC > 신규 설비 도입 후 운영 데이터에서 2500~3000 RPM 구간의 데이터가 급증하면 PSI가 높아집니다.
# MAGIC > 이는 모델이 학습하지 않은 RPM 범위의 데이터가 많아졌다는 의미이며, 모델 재학습이 필요할 수 있습니다.
# MAGIC
# MAGIC #### PSI 공식 의미
# MAGIC ```
# MAGIC PSI = Σ (실제비율 - 기대비율) x ln(실제비율 / 기대비율)
# MAGIC ```
# MAGIC - **기대비율**: 학습 데이터에서 각 구간(bin)에 해당하는 데이터 비율 (= 모델이 "알고 있는" 분포)
# MAGIC - **실제비율**: 운영 데이터에서 각 구간에 해당하는 데이터 비율 (= 현재 실제 분포)
# MAGIC - **ln(실제/기대)**: 두 비율의 차이를 로그 스케일로 측정. 차이가 클수록 가중치를 더 부여합니다
# MAGIC - **Σ (합산)**: 모든 구간의 차이를 합산하여 전체적인 분포 변화량을 계산합니다
# MAGIC
# MAGIC #### `np.maximum(..., 0.001)` 이 필요한 이유
# MAGIC 어떤 구간에 데이터가 하나도 없으면 비율이 0이 됩니다.
# MAGIC `ln(0)`은 **-무한대** 가 되어 계산이 불가능합니다.
# MAGIC 따라서 0 대신 매우 작은 값(0.001, 즉 0.1%)을 사용하여 **0으로 나누기 오류를 방지** 합니다.
# MAGIC 이것은 수학적 안전장치이며, 결과에 미치는 영향은 무시할 수 있을 정도로 작습니다.
# MAGIC
# MAGIC #### PSI 결과 해석 기준
# MAGIC | PSI 값 | 상태 | 의미 | 제조 현장 대응 |
# MAGIC |--------|------|------|---------------|
# MAGIC | **< 0.1** | 안정 (초록) | 분포 변화 거의 없음 | 정상 모니터링 계속. 모델 성능 양호 |
# MAGIC | **0.1 ~ 0.2** | 주의 (노랑) | 분포 약간 변화 시작 | 원인 분석 시작. 공정 변화, 원자재 변경 여부 확인 |
# MAGIC | **> 0.2**| 경고 (빨강) | 유의미한 드리프트 감지 | **모델 재학습 검토**. 해당 피처 관련 공정 변경 이력 확인 |
# MAGIC
# MAGIC > **Databricks 장점**: 실무에서는 Data Quality Monitoring이 PSI를 **자동으로** 계산하고
# MAGIC > 임계값 초과 시 알림을 보냅니다. 아래 코드는 **PSI의 원리를 이해하기 위한 교육용** 예제입니다.
# MAGIC > 실제 운영에서는 섹션 4의 Data Quality Monitoring 설정만으로 충분합니다.

# COMMAND ----------

# DBTITLE 1,PSI (Population Stability Index) 계산
import numpy as np   # 수치 계산 라이브러리 임포트
import pandas as pd  # 데이터프레임 처리 라이브러리 임포트

def calculate_psi(expected, actual, bins=10):
    """Population Stability Index 계산

    Args:
        expected: 학습(기준) 데이터 배열
        actual: 추론(비교) 데이터 배열
        bins: 구간 분할 수 (기본 10개 구간으로 분포 비교)
    Returns:
        psi: 0에 가까울수록 분포가 유사, 클수록 드리프트 심각
    """
    # 학습/추론 데이터 전체를 커버하는 구간 경계값 생성 (10개 구간 = 11개 경계점)
    breakpoints = np.linspace(min(expected.min(), actual.min()),
                             max(expected.max(), actual.max()), bins + 1)

    # 각 구간에 해당하는 데이터 비율 계산 (전체 데이터 수로 나누어 비율로 변환)
    expected_counts = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_counts = np.histogram(actual, bins=breakpoints)[0] / len(actual)

    # 0 방지: 특정 구간에 데이터가 없으면 0이 되는데, log(0)은 계산 불가능
    # np.maximum()으로 0 대신 최솟값 0.001을 사용하여 안정적인 계산 보장
    expected_counts = np.maximum(expected_counts, 0.001)
    actual_counts = np.maximum(actual_counts, 0.001)

    # PSI 공식: Σ (실제비율 - 기대비율) × ln(실제비율 / 기대비율)
    psi = np.sum((actual_counts - expected_counts) * np.log(actual_counts / expected_counts))
    return psi

# Delta Lake 테이블에서 학습 데이터를 Pandas DataFrame으로 변환 (PSI는 Pandas로 계산)
train_pdf = spark.table("lgit_pm_training").filter("split='train'").select(*feature_columns).toPandas()
# 추론 결과 테이블에서 피처 컬럼만 선택하여 Pandas DataFrame으로 변환
infer_pdf = spark.table("lgit_pm_inference_results").select(*feature_columns).toPandas()

print("=== PSI (Population Stability Index) ===")
print("PSI < 0.1: 안정 | 0.1~0.2: 주의 | > 0.2: 드리프트 감지")
print("─" * 50)

drift_detected = False  # 드리프트 감지 여부 플래그 (기본값: 드리프트 없음)

# 각 피처 컬럼에 대해 PSI를 계산하고 상태를 출력
for col in feature_columns:
    psi = calculate_psi(train_pdf[col].values, infer_pdf[col].values)  # PSI 계산
    # PSI 임계값에 따라 상태 분류
    status = "안정" if psi < 0.1 else ("주의" if psi < 0.2 else "드리프트!")
    if psi >= 0.2:
        drift_detected = True  # 하나라도 0.2 이상이면 드리프트 발생으로 표시
    print(f"  {col:30s}: PSI = {psi:.4f} ({status})")

# 전체 요약 메시지 출력
if drift_detected:
    print("\n⚠️ 데이터 드리프트가 감지되었습니다. 모델 재학습을 검토하세요.")
else:
    print("\n✅ 데이터 분포가 안정적입니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2-1. 드리프트 감지 결과 → 재학습 트리거 (Level 2 자동화)
# MAGIC
# MAGIC > **20년차 실무 팁**: 드리프트를 감지하는 것과 "자동으로 행동하는 것"은 완전히 다른 레벨입니다.
# MAGIC > Level 1에서는 사람이 PSI 리포트를 보고 재학습을 결정합니다.
# MAGIC > **Level 2에서는 시스템이 자동으로 재학습을 트리거합니다.**
# MAGIC >
# MAGIC > 이 셀이 바로 Level 1과 Level 2를 나누는 경계선입니다.

# COMMAND ----------

# DBTITLE 1,드리프트 감지 → 재학습 트리거 자동화
# --- Level 2 핵심: 드리프트 감지 시 다음 태스크로 플래그 전달 ---

# PSI 결과를 다시 수집 (이전 셀의 변수들이 스코프에 남아있음)
psi_results = {}
for col in feature_columns:
    psi_results[col] = calculate_psi(train_pdf[col].values, infer_pdf[col].values)

# PSI 결과에서 드리프트 여부 판단
drift_features = []
PSI_THRESHOLD = 0.2  # 업계 표준 임계값 (20년간 검증된 기준)

for feature, psi_value in psi_results.items():
    if psi_value > PSI_THRESHOLD:
        drift_features.append(f"{feature} (PSI={psi_value:.3f})")

# Databricks Jobs taskValues로 다음 태스크에 플래그 전달
# 이것이 Level 2 자동화의 핵심 메커니즘입니다
try:
    dbutils.jobs.taskValues.set(key="drift_detected", value=drift_detected)
    dbutils.jobs.taskValues.set(key="drift_features", value=str(drift_features))
    dbutils.jobs.taskValues.set(key="max_psi", value=float(max(psi_results.values())) if psi_results else 0.0)
    print(f"✅ taskValues 설정 완료 (Jobs 파이프라인 내에서 자동 전달)")
except Exception:
    # 노트북 단독 실행 시에는 taskValues 사용 불가 (정상)
    print(f"ℹ️ 노트북 단독 실행 중 (taskValues는 Job 파이프라인에서만 동작)")

if drift_detected:
    print(f"\n🔴 드리프트 감지! 재학습이 필요합니다.")
    print(f"   감지된 피처: {', '.join(drift_features)}")
    print(f"   → Level 2 파이프라인: 자동으로 재학습 태스크가 트리거됩니다.")
else:
    print(f"\n🟢 드리프트 없음. 모델이 안정적으로 운영 중입니다.")
    print(f"   모든 피처 PSI < {PSI_THRESHOLD}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### PSI 결과 해석 및 다음 단계
# MAGIC
# MAGIC **결과 읽는 법:**
# MAGIC 각 피처(센서)별로 PSI 값과 상태(안정/주의/드리프트!)가 출력됩니다.
# MAGIC 예를 들어 `rotational_speed_rpm: PSI = 0.2534 (드리프트!)`라고 나오면,
# MAGIC 회전속도 데이터의 분포가 학습 당시와 유의미하게 달라졌다는 뜻입니다.
# MAGIC
# MAGIC **이 결과로 무엇을 알 수 있나?**
# MAGIC - **어떤 센서가** 학습 당시와 가장 많이 달라졌는지 → 원인 추적의 출발점
# MAGIC - **특정 피처에서만** 드리프트 발생 → 해당 센서 관련 설비/공정만 점검하면 됨
# MAGIC - **모든 피처에서** 드리프트 발생 → 전체적인 공정 환경 변화, 모델 재학습 필요
# MAGIC
# MAGIC **드리프트 발생 시 체계적 대응 절차 (5단계):**
# MAGIC
# MAGIC | 단계 | 행동 | 담당 | 예시 |
# MAGIC |------|------|------|------|
# MAGIC | **1. 식별** | PSI > 0.2인 피처 확인 | 데이터 엔지니어 | "torque_nm PSI = 0.35" |
# MAGIC | **2. 원인 조사** | 해당 기간의 공정 변경 이력 확인 | 공정 엔지니어 | "지난주 절삭유 교체" |
# MAGIC | **3. 영향 평가** | 드리프트가 모델 성능에 미치는 영향 측정 | ML 엔지니어 | "F1 Score 0.95 → 0.87 하락" |
# MAGIC | **4. 재학습** | 새 데이터 포함하여 모델 재학습 | ML 엔지니어 | 04번 노트북 재실행 |
# MAGIC | **5. 재배포** | 검증 후 새 모델 배포 | MLOps | 05번 → 06번 자동 실행 |
# MAGIC
# MAGIC > **LG이노텍 실무 팁**: 드리프트가 감지되었다고 해서 반드시 모델이 나빠진 것은 아닙니다.
# MAGIC > 공정이 **개선** 되어 데이터 분포가 바뀐 경우도 있습니다 (예: 불량률이 낮아져서 정상 데이터 비율 증가).
# MAGIC > 따라서 드리프트 원인을 반드시 공정팀과 함께 분석해야 합니다.
# MAGIC
# MAGIC > **실전 사례**: 한 반도체 공장에서 PSI가 갑자기 0.4로 뛴 적이 있습니다.
# MAGIC > ML 팀은 "모델 재학습이 필요하다"고 판단했지만, 공정 엔지니어와 함께 분석해보니
# MAGIC > 원인이 "절삭유 교체"였습니다. 절삭유 교체 후 2주간의 데이터를 추가로 수집하고
# MAGIC > 재학습했더니 PSI가 0.05로 안정되었습니다.
# MAGIC > 교훈: **드리프트 감지 → 즉시 재학습이 아니라, 드리프트 감지 → 원인 파악 → 데이터 안정화 → 재학습** 순서입니다.
# MAGIC > 원인도 모르고 재학습하면 같은 문제가 반복됩니다.
# MAGIC
# MAGIC 다음 섹션에서는 시간대별 예측 결과 추이를 SQL로 조회합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 모델 성능 모니터링
# MAGIC
# MAGIC 실제 고장 레이블이 확보된 경우, 모델의 운영 성능을 추적합니다.
# MAGIC
# MAGIC ### 이 섹션에서 하는 일
# MAGIC
# MAGIC 시간대별로 모델의 예측 패턴이 어떻게 변하는지 추적합니다.
# MAGIC 갑작스러운 변화가 있다면 공정 이상 또는 모델 문제의 신호일 수 있습니다.
# MAGIC
# MAGIC > **실무에서 자주 하는 실수**: 모델 성능 모니터링에서 가장 어려운 부분은 사실 "정답 레이블을 얻는 것"입니다.
# MAGIC > 예지보전에서 실제 고장 여부(ground truth)는 고장이 발생한 후에야 알 수 있고,
# MAGIC > 예방 정비로 고장을 막았다면 정답 자체가 존재하지 않습니다("예측했기 때문에 고장이 안 난 건지,
# MAGIC > 원래 안 날 건지"를 구분할 수 없음). 이것을 **Counterfactual Problem** 이라고 합니다.
# MAGIC > 그래서 실무에서는 정답 레이블 기반의 정확도 추적보다, 이 섹션처럼 **예측 분포 추이** 를
# MAGIC > 모니터링하는 것이 더 현실적입니다.
# MAGIC
# MAGIC **조회하는 정보:**
# MAGIC - `prediction_hour`: 시간대별 집계 (1시간 단위)
# MAGIC - `total_predictions`: 해당 시간에 처리한 총 예측 건수
# MAGIC - `predicted_failures`: 고장으로 예측된 건수
# MAGIC - `avg_failure_prob`: 평균 고장 확률 (시간대별 위험도 추이)
# MAGIC - `model_version`: 사용된 모델 버전 (버전별 성능 차이 비교 가능)
# MAGIC
# MAGIC > **Databricks 장점**: 추론 결과가 Delta Lake에 저장되어 있기 때문에,
# MAGIC > 별도의 데이터베이스 설정 없이 바로 SQL로 분석할 수 있습니다.
# MAGIC > 또한 `date_trunc`와 같은 시계열 함수를 SQL에서 직접 사용할 수 있습니다.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 예측 결과 분포 추이: 시간대별로 예측 건수, 고장 예측 건수, 평균 고장 확률을 집계
# MAGIC SELECT
# MAGIC   date_trunc('hour', inference_timestamp) as prediction_hour,  -- 시각을 1시간 단위로 절삭 (분/초 제거)
# MAGIC   COUNT(*) as total_predictions,                               -- 해당 시간대에 수행된 총 예측 건수
# MAGIC   SUM(predicted_failure) as predicted_failures,                -- 고장(1)으로 예측된 건수 합계
# MAGIC   ROUND(AVG(failure_probability), 4) as avg_failure_prob,      -- 시간대별 평균 고장 확률 (소수 4자리)
# MAGIC   model_version                                                 -- 사용된 모델 버전
# MAGIC FROM lgit_pm_inference_results
# MAGIC GROUP BY date_trunc('hour', inference_timestamp), model_version  -- 시간+버전 기준으로 그룹화
# MAGIC ORDER BY prediction_hour DESC                                   -- 최신 시간대가 위에 오도록 내림차순 정렬
# MAGIC LIMIT 24                                                        -- 최근 24시간 데이터만 표시

# COMMAND ----------

# MAGIC %md
# MAGIC ### 시계열 모니터링 결과 해석
# MAGIC
# MAGIC **확인해야 할 패턴:**
# MAGIC
# MAGIC | 패턴 | 의미 | 조치 |
# MAGIC |------|------|------|
# MAGIC | `avg_failure_prob`이 일정하게 낮음 (< 0.1) | 정상 운영 중 | 계속 모니터링 |
# MAGIC | 특정 시간대에 `avg_failure_prob` 급등 | 해당 시간에 공정 이상 | 설비 점검 |
# MAGIC | `predicted_failures`가 점점 증가 추세 | 설비 노후화 가능성 | 예방 정비 계획 |
# MAGIC | 모델 버전 변경 후 결과가 크게 달라짐 | 모델 변화 효과 | 성능 비교 분석 |
# MAGIC
# MAGIC **실제 활용 예**: 야간 작업 시간대(22시~06시)에 고장 확률이 높다면, 야간 교대 근무자를 위한
# MAGIC 집중 모니터링 알림을 설정할 수 있습니다.
# MAGIC
# MAGIC > **실무 경험**: 시계열 모니터링에서 가장 가치 있는 패턴은 **"서서히 올라가는 고장 확률"** 입니다.
# MAGIC > 한 공장에서 `avg_failure_prob`이 매주 0.01씩 올라가는 것을 발견한 적이 있습니다.
# MAGIC > 원인은 공구 마모의 누적이었습니다. 이 추세를 6주 전에 발견해서 계획된 공구 교체를 했고,
# MAGIC > 비계획 정지를 막았습니다. 만약 모니터링이 없었다면 8주차에 공구가 파손되어 라인이 정지했을 겁니다.
# MAGIC > 이것이 모니터링의 실제 ROI입니다.
# MAGIC
# MAGIC 다음 섹션에서는 이 모든 모니터링을 **자동화** 하는 Data Quality Monitoring을 설정합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Data Quality Monitoring 설정
# MAGIC
# MAGIC ### Data Quality Monitoring이란?
# MAGIC
# MAGIC 지금까지 위 섹션에서 직접 코드로 PSI를 계산하고, 통계를 비교하고, SQL로 추이를 분석했습니다.
# MAGIC **Data Quality Monitoring**은 이 모든 작업을 **자동으로, 지속적으로**수행해주는 Databricks **내장 기능** 입니다.
# MAGIC
# MAGIC > **비유**: 직접 혈압을 매일 재고 수첩에 기록하는 것(= 위의 코드)과,
# MAGIC > 스마트워치가 **24시간 자동으로** 심박수, 혈압, 산소포화도를 측정하고
# MAGIC > 이상이 감지되면 **즉시 알림** 을 보내는 것(= Data Quality Monitoring)의 차이입니다.
# MAGIC
# MAGIC > **경험담**: 예전에 수동 모니터링을 운영한 적이 있습니다.
# MAGIC > 매주 금요일에 데이터 사이언티스트가 모니터링 스크립트를 돌리고 결과를 정리해서 보고하는 방식이었죠.
# MAGIC > 문제는 **그 사람이 휴가를 가면 2주간 모니터링이 안 된다는 것** 입니다.
# MAGIC > 실제로 휴가 기간에 드리프트가 발생했는데, 복귀 후에야 발견했습니다. 그 사이 2주간의 예측 결과가 전부 불량이었습니다.
# MAGIC > Data Quality Monitoring 같은 자동화 시스템은 "사람에 의존하지 않는 모니터링"이라는 점에서 결정적인 장점이 있습니다.
# MAGIC
# MAGIC ### 수동 모니터링 vs Data Quality Monitoring 비교
# MAGIC
# MAGIC | 항목 | 수동 모니터링 (위의 코드) | Data Quality Monitoring |
# MAGIC |------|-------------------------|---------------------|
# MAGIC | **실행 방식** | 사람이 노트북을 실행해야 함 | 자동으로 스케줄 실행 |
# MAGIC | **드리프트 지표** | PSI만 직접 구현 | PSI, JS Divergence, KL Divergence 등 자동 계산 |
# MAGIC | **데이터 품질** | 별도 코드 필요 | 결측값, 범위 이탈, 중복 등 자동 측정 |
# MAGIC | **대시보드** | 없음 | 자동 생성, 실시간 업데이트 |
# MAGIC | **알림** | 없음 | 임계값 초과 시 이메일/Slack 자동 알림 |
# MAGIC | **이력 관리** | 결과를 별도 저장해야 함 | 모니터링 결과가 Delta 테이블에 자동 누적 |
# MAGIC
# MAGIC ### 파라미터 설명
# MAGIC
# MAGIC | 파라미터 | 값 | 의미 |
# MAGIC |----------|-----|------|
# MAGIC | `table_name` | `catalog.db.lgit_pm_inference_results` | 모니터링할 Delta 테이블 전체 경로 (3단계 네임스페이스) |
# MAGIC | `assets_dir` | `/Workspace/Users/.../lgit_monitoring` | 자동 생성되는 대시보드가 저장될 위치 |
# MAGIC | `output_schema_name` | `catalog.db` | 모니터링 통계 결과가 저장될 스키마 (카탈로그.스키마) |
# MAGIC | `model_id_col` | `"model_name"` | 모델 식별자 컬럼. 여러 모델 비교 시 필수 |
# MAGIC | `prediction_col` | `"failure_probability"` | 모델 예측값 컬럼. 이 값의 분포 변화를 추적 |
# MAGIC | `timestamp_col` | `"inference_timestamp"` | 시계열 분석의 기준이 되는 시각 컬럼 |
# MAGIC | `problem_type` | `PROBLEM_TYPE_CLASSIFICATION` | 분류(Classification) 문제임을 명시. 회귀 문제라면 REGRESSION |
# MAGIC
# MAGIC ### 결과 확인 방법 (Databricks UI 단계별 안내)
# MAGIC
# MAGIC **방법 1 - Unity Catalog 탐색기에서 확인 (권장):**
# MAGIC 1. Databricks 워크스페이스 좌측 메뉴에서 **`Catalog`** 아이콘 클릭
# MAGIC 2. 좌측 트리에서 **카탈로그명** → **스키마명** → **`lgit_pm_inference_results`** 테이블 클릭
# MAGIC 3. 상단 탭에서 **`Quality`** 탭 클릭
# MAGIC 4. 모니터링 대시보드가 표시됩니다: 드리프트 지표, 데이터 품질, 예측 분포 등
# MAGIC
# MAGIC **방법 2 - 자동 생성 대시보드:**
# MAGIC 1. 좌측 메뉴에서 **`Workspace`** 클릭
# MAGIC 2. **`Users`** → **`{본인 이메일}`** → **`lgit_monitoring`** 폴더 열기
# MAGIC 3. 자동 생성된 Databricks 대시보드 파일을 클릭하면 시각화된 모니터링 결과 확인
# MAGIC
# MAGIC **방법 3 - 자동 생성된 모니터링 테이블 직접 조회:**
# MAGIC - `lgit_pm_inference_results_profile_metrics`: 시간대별 각 피처의 통계 프로파일 (평균, 표준편차, 최솟값, 최댓값 등)
# MAGIC - `lgit_pm_inference_results_drift_metrics`: 시간대별 드리프트 지표 (PSI, JS Divergence 등)
# MAGIC
# MAGIC > **Databricks 장점**: 수동 모니터링 인프라를 구축하려면 Prometheus(메트릭 수집) + Grafana(시각화) +
# MAGIC > AlertManager(알림) 등 여러 오픈소스를 설치하고 연결해야 합니다. 이것만으로도 1~2주의 DevOps 작업이 필요합니다.
# MAGIC > Databricks Data Quality Monitoring은 **코드 5줄** 로 이 모든 것이 즉시 설정됩니다.

# COMMAND ----------

# DBTITLE 1,Data Quality Monitor 생성 (프로그래밍 방식)
from databricks.sdk import WorkspaceClient  # Databricks SDK를 통해 워크스페이스 기능에 접근하기 위해 임포트

w = WorkspaceClient()  # 현재 Databricks 워크스페이스에 연결하는 클라이언트 객체 생성

# 모니터링할 테이블의 전체 경로 구성 (Unity Catalog 형식: catalog.schema.table)
inference_table_full = f"{catalog}.{db}.lgit_pm_inference_results"

# 기존에 동일한 테이블에 모니터가 있다면 삭제 (재생성 시 충돌 방지)
try:
    w.quality_monitors.delete(table_name=inference_table_full)  # 기존 모니터 삭제 시도
    print(f"기존 모니터 삭제: {inference_table_full}")
except Exception as e:
    print(f"기존 모니터 없음: {e}")  # 모니터가 없는 경우 정상적으로 넘어감

# 새 모니터 생성
try:
    monitor = w.quality_monitors.create(
        table_name=inference_table_full,                          # 모니터링할 테이블 지정
        assets_dir=f"/Workspace/Users/{current_user}/lgit_monitoring",  # 대시보드 저장 경로
        output_schema_name=f"{catalog}.{db}",                    # 모니터링 통계 결과가 저장될 스키마
        inference_log={
            "model_id_col": "model_name",                        # 모델 이름/버전 식별 컬럼
            "prediction_col": "failure_probability",             # 모델 예측값 컬럼 (고장 확률)
            "timestamp_col": "inference_timestamp",              # 예측 시각 컬럼 (시계열 분석용)
            "problem_type": "PROBLEM_TYPE_CLASSIFICATION",       # 분류 문제 타입 지정
        },
    )
    print(f"Data Quality Monitor 생성 완료: {inference_table_full}")
    print(f"대시보드 경로: /Workspace/Users/{current_user}/lgit_monitoring")
except Exception as e:
    print(f"Monitor 생성 참고: {e}")
    print("참고: Data Quality Monitoring은 워크스페이스에서 수동으로도 설정 가능합니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Data Quality Monitor 생성 후 확인 방법
# MAGIC
# MAGIC 모니터가 정상 생성되면 다음과 같이 확인하세요:
# MAGIC
# MAGIC **방법 1 - Unity Catalog UI에서 확인:**
# MAGIC 1. 좌측 메뉴에서 `Catalog` 아이콘 클릭
# MAGIC 2. `{catalog}` → `{db}` → `lgit_pm_inference_results` 테이블 클릭
# MAGIC 3. 상단 탭에서 `Quality` 클릭 → 모니터링 대시보드 확인
# MAGIC
# MAGIC **방법 2 - 자동 생성된 대시보드:**
# MAGIC 1. 좌측 메뉴에서 `Workspace` 클릭
# MAGIC 2. `Users` → `{본인 이메일}` → `lgit_monitoring` 폴더 열기
# MAGIC 3. 자동 생성된 Databricks 대시보드 파일 클릭
# MAGIC
# MAGIC **자동으로 추적되는 항목들:**
# MAGIC - 각 피처의 평균, 최솟값, 최댓값, 표준편차 (시간대별)
# MAGIC - PSI, JS Divergence 등 드리프트 지표
# MAGIC - 고장 확률 분포 변화
# MAGIC - 결측값 비율
# MAGIC
# MAGIC > **팁**: 모니터 첫 실행 후 결과가 표시되기까지 몇 분이 걸릴 수 있습니다.
# MAGIC > `REFRESH` 버튼을 클릭하거나 페이지를 새로고침해보세요.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 요약
# MAGIC
# MAGIC ### 이 노트북에서 수행한 작업
# MAGIC
# MAGIC | 단계 | 수행 내용 | 핵심 개념 | Databricks 기능 |
# MAGIC |------|-----------|-----------|----------------|
# MAGIC | **1** | 모니터링 대상 데이터 확인 | 추론 결과 테이블 구조 이해 | Delta Lake, SQL |
# MAGIC | **2** | 데이터 드리프트 탐지 | PSI로 분포 변화 측정 | PySpark, Pandas |
# MAGIC | **3** | 모델 성능 추이 관찰 | 시간대별 예측 패턴 분석 | SQL Analytics |
# MAGIC | **4** | 자동 모니터링 설정 | 24/7 상시 감시 체계 구축 | Data Quality Monitoring |
# MAGIC
# MAGIC ### 전체 MLOps 파이프라인에서의 위치
# MAGIC
# MAGIC ```
# MAGIC 데이터 수집 → 전처리 → 모델 학습 → 검증 → 배포 → 추론 → [모니터링] → (이상 시) 재학습
# MAGIC                                                                  ↑
# MAGIC                                                             현재 노트북
# MAGIC ```
# MAGIC
# MAGIC 모니터링은 MLOps 파이프라인의 **마지막이자 첫 번째** 단계입니다.
# MAGIC 이상을 감지하면 다시 데이터 수집과 모델 재학습으로 이어지는 **지속적인 개선 사이클(Continuous Improvement Cycle)** 을 형성합니다.
# MAGIC 이것이 바로 제조업의 **PDCA(Plan-Do-Check-Act)** 사이클과 동일한 철학입니다.
# MAGIC
# MAGIC > **20년 경험의 마지막 조언**: 모니터링의 궁극적 목표는 "모델이 언제 재학습이 필요한지를 자동으로 판단하는 것"입니다.
# MAGIC > PSI > 0.2가 3일 연속 → 자동 재학습 트리거 → 자동 검증 → 자동 배포. 이것이 진정한 MLOps입니다.
# MAGIC > 여기까지 도달하면, ML 엔지니어는 "모델 만드는 사람"이 아니라 "시스템을 설계하는 사람"이 됩니다.
# MAGIC > 모델은 자동으로 학습되고, 자동으로 검증되고, 자동으로 배포되고, 자동으로 모니터링됩니다.
# MAGIC > 사람은 시스템이 정상 작동하는지만 가끔 확인하면 됩니다.
# MAGIC > 이것이 제가 20년간 추구해온 "Self-Healing ML System"의 비전입니다.
# MAGIC
# MAGIC > **LG이노텍에서의 모니터링 가치**:
# MAGIC > 모니터링이 없으면, 모델 성능 저하를 "고장 예측을 놓쳤을 때(실제 다운타임 발생)" 비로소 알게 됩니다.
# MAGIC > 모니터링이 있으면, 데이터 드리프트 단계에서 **사전에**감지하여 실제 성능 저하가 발생하기 **전에** 대응할 수 있습니다.
# MAGIC > 이것은 "고장이 난 후 수리"와 "고장 징후를 감지하고 예방 정비"의 차이와 같습니다 - 바로 예지보전의 철학입니다.
# MAGIC
# MAGIC ### Databricks가 제공하는 모니터링 자동화 요약
# MAGIC
# MAGIC | 작업 | 전통적 방법 | Databricks | 절감 효과 |
# MAGIC |------|------------|------------|-----------|
# MAGIC | 드리프트 탐지 | PSI 계산 코드 직접 작성 | Data Quality Monitoring 자동 계산 | 개발 시간 80% 절감 |
# MAGIC | 대시보드 | Grafana/Kibana 별도 구축 | 자동 생성 대시보드 | 인프라 구축 불필요 |
# MAGIC | 데이터 저장 | 별도 시계열 DB (InfluxDB 등) | Delta Lake에 자동 저장 | 추가 DB 비용 없음 |
# MAGIC | 알림 | AlertManager/PagerDuty 별도 구축 | Databricks Alerts 내장 | 추가 서비스 비용 없음 |
# MAGIC | 통합 관리 | 여러 도구를 연결하는 글루 코드 필요 | 단일 플랫폼에서 모두 해결 | 유지보수 비용 대폭 절감 |
# MAGIC
# MAGIC **다음 단계:** [MLOps Agent]($./09_mlops_agent) - AI Agent를 활용한 MLOps 자동화
