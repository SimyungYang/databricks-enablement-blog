# Databricks notebook source
# MAGIC %md
# MAGIC # 모델 재학습 전략 완전 가이드 (Retraining Strategies)
# MAGIC
# MAGIC ## 왜 이 노트북이 중요한가?
# MAGIC
# MAGIC ML 모델을 개발하여 배포하는 것은 MLOps 여정의 **시작** 에 불과합니다. 실제 운영 환경에서는 **시간이 지남에 따라 모델 성능이 반드시 저하** 됩니다. 이를 방치하면 AI/ML 프로젝트는 **"처음엔 잘 되다가 나중에 안 되는 것"** 이라는 인식을 심어주게 됩니다.
# MAGIC
# MAGIC LG Innotek 제조 현장에서 예를 들면:
# MAGIC - 겨울에 학습한 모델이 여름에는 정확도가 떨어짐 (온도/습도 변화)
# MAGIC - 새로운 원자재 공급사로 변경 후 불량 패턴이 달라짐
# MAGIC - 설비 PM(예방보전) 후 센서 값 범위가 달라짐
# MAGIC - 공정 레시피 업데이트 후 기존 고장 패턴이 더 이상 유효하지 않음
# MAGIC
# MAGIC 이 노트북은 **"모델을 어떻게 지속적으로 최신 상태로 유지하는가?"** 라는 MLOps의 핵심 질문에 대해, 기초부터 최신 기법까지 **12개 Part** 로 체계적으로 답합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 이 노트북에서 배우는 내용
# MAGIC
# MAGIC | Part | 주제 | 핵심 질문 | 난이도 |
# MAGIC |------|------|----------|--------|
# MAGIC | **Part 1** | 재학습이 필요한 이유 | 왜 모델 성능이 저하되는가? | 기초 |
# MAGIC | **Part 2** | 재학습 트리거 전략 | 언제 재학습을 시작해야 하는가? | 기초 |
# MAGIC | **Part 3** | Full Retraining 실전 구현 | 전체 재학습을 어떻게 자동화하는가? | 중급 |
# MAGIC | **Part 4** | 학습 데이터 관리 | Delta Lake로 학습 데이터를 어떻게 관리하는가? | 중급 |
# MAGIC | **Part 5** | 모델 버전 관리와 롤백 | 새 모델이 나쁘면 어떻게 되돌리는가? | 중급 |
# MAGIC | **Part 6** | Incremental Learning | 전체 데이터 없이 모델을 업데이트하는 방법? | 고급 |
# MAGIC | **Part 7** | Continual Learning | 이전 지식을 잊지 않으면서 학습하는 방법? | 고급 |
# MAGIC | **Part 8** | Online Learning | 실시간으로 모델을 적응시키는 방법? | 고급 |
# MAGIC | **Part 9** | 강화학습 기반 재학습 | AI가 재학습 전략을 스스로 선택하는 방법? | 최신 연구 |
# MAGIC | **Part 10** | Active Learning | 레이블링 비용을 최소화하는 방법? | 고급 |
# MAGIC | **Part 11** | Warm-start vs Cold-start | 기존 모델을 활용할 것인가, 처음부터 학습할 것인가? | 중급 |
# MAGIC | **Part 12** | 운영 환경 종합 아키텍처 | 위 기법들을 어떻게 조합하여 운영하는가? | 종합 |
# MAGIC
# MAGIC > **권장 학습 경로** : Part 1~5는 **모든 MLOps 구축에 필수** 입니다. Part 6~11은 운영 환경의 복잡성에 따라 선택적으로 적용합니다. Part 12에서 전체를 통합합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 사전 지식
# MAGIC
# MAGIC 이 노트북을 이해하기 위해 필요한 기본 개념:
# MAGIC
# MAGIC | 용어 | 설명 | 제조 현장 비유 |
# MAGIC |------|------|-------------|
# MAGIC | **모델 학습(Training)** | 데이터를 사용하여 패턴을 학습하는 과정 | 신규 설비에 최적 공정 조건을 세팅하는 것 |
# MAGIC | **추론(Inference)** | 학습된 모델로 새 데이터를 예측 | 세팅된 조건으로 양산하는 것 |
# MAGIC | **드리프트(Drift)** | 시간에 따라 데이터/관계가 변하는 현상 | 설비 노후화, 계절 변화, 원자재 변경 |
# MAGIC | **MLflow** | 모델의 학습 과정을 기록/관리하는 도구 | 공정 이력 관리 시스템(MES)과 유사 |
# MAGIC | **Unity Catalog** | 데이터/모델의 거버넌스 시스템 | 품질 관리 체계(QMS)의 디지털 버전 |

# COMMAND ----------

# MAGIC %pip install --quiet mlflow xgboost river --upgrade
# MAGIC
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./_resources/00-setup

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 1: 재학습이 필요한 이유
# MAGIC
# MAGIC ## 모델은 왜 시간이 지나면 성능이 떨어지는가?
# MAGIC
# MAGIC ML 모델은 **학습 시점의 데이터 패턴** 을 기반으로 예측합니다.
# MAGIC 하지만 제조 현장은 **끊임없이 변합니다**. 이 변화를 통계학에서는 **"드리프트(Drift)"** 라고 부르며, 이것이 모델 성능 저하의 근본 원인입니다.
# MAGIC
# MAGIC > **핵심 통찰** : 구글의 연구(2015, "Hidden Technical Debt in ML Systems")에 따르면, ML 시스템 운영 비용의 **90% 이상이 모델 배포 후 유지보수** 에 소요됩니다. 모델 개발 자체는 전체의 5~10%에 불과합니다. 재학습 전략은 이 90%를 효율적으로 관리하는 핵심입니다.
# MAGIC
# MAGIC ### 1.1 Data Drift (데이터 드리프트) — 입력 데이터의 분포가 변함
# MAGIC
# MAGIC **정의** : 모델에 입력되는 데이터의 **통계적 분포(P(X))** 가 학습 시점과 달라지는 현상
# MAGIC
# MAGIC ```
# MAGIC [학습 시점: 1월 겨울]                 [6개월 후: 7월 여름]
# MAGIC 공장 내부 온도: 평균 300K, 편차 2K  →  평균 305K, 편차 3K
# MAGIC 외부 습도: 평균 40%, 편차 5%        →  평균 75%, 편차 10%
# MAGIC
# MAGIC 모델은 "300K 근처, 습도 40% 근처"의 패턴을 학습했으므로,
# MAGIC "305K, 습도 75%"라는 처음 보는 영역에서는 예측 정확도가 급격히 떨어짐
# MAGIC ```
# MAGIC
# MAGIC **LG Innotek 제조 현장의 Data Drift 원인** :
# MAGIC - **계절 변화** : 공장 내부 온도/습도가 외기 온도에 영향받음 (특히 클린룸 외부 구역)
# MAGIC - **원자재 변경** : 새 공급사의 기판, 렌즈, 접착제 등의 물리적 특성이 미묘하게 다름
# MAGIC - **설비 노후화** : 센서 교정 주기에 따라 측정값 범위가 점진적으로 이동(Sensor Drift)
# MAGIC - **생산 물량 변동** : 풀 가동 vs 부분 가동에 따라 설비 열적 특성이 달라짐
# MAGIC
# MAGIC ### 1.2 Concept Drift (개념 드리프트) — 입력과 출력의 관계가 변함
# MAGIC
# MAGIC **정의** : 입력(X)과 출력(Y) 간의 **관계 자체(P(Y|X))** 가 변하는 현상. Data Drift보다 **더 심각** 합니다.
# MAGIC
# MAGIC ```
# MAGIC [학습 시점: 베어링 노후]                [6개월 후: 베어링 교체 완료]
# MAGIC 토크 > 50Nm → 고장 확률 80%            토크 > 50Nm → 고장 확률 20%
# MAGIC   (이유: 오래된 베어링의 마찰 증가)        (이유: 새 베어링은 고토크에도 정상)
# MAGIC
# MAGIC 동일한 토크 값(50Nm)이지만, 고장과의 관계가 완전히 바뀜
# MAGIC → 데이터 분포는 같아 보이는데 모델 예측이 틀리기 시작
# MAGIC → Data Drift 모니터링으로는 감지 불가!
# MAGIC ```
# MAGIC
# MAGIC **LG Innotek 제조 현장의 Concept Drift 원인** :
# MAGIC - **공정 레시피 업데이트** : DOE(실험계획법) 결과를 반영하여 공정 조건 최적화 → 이전 고장 패턴 무효화
# MAGIC - **설비 부품 교체** : 핵심 부품(모터, 베어링, 히터) 교체 후 고장 메커니즘 자체가 변화
# MAGIC - **품질 기준 변경** : 고객 요구사항 강화로 이전에 정상이었던 것이 불량으로 재분류
# MAGIC - **신규 제품 투입** : 동일 라인에서 새 모델의 카메라 모듈 생산 시작
# MAGIC
# MAGIC ### 1.3 성능 저하 시각화
# MAGIC
# MAGIC ```
# MAGIC F1 Score
# MAGIC  1.0 ┃
# MAGIC      ┃ ████
# MAGIC  0.8 ┃     ████                    ← 학습 직후: 최고 성능
# MAGIC      ┃         ████
# MAGIC  0.6 ┃             ████            ← 점진적 저하 (Data Drift) — 계절 변화, 설비 노후화
# MAGIC      ┃                 ██
# MAGIC  0.4 ┃                   ██████    ← 급격한 저하 (Concept Drift) — 공정 변경, 부품 교체
# MAGIC      ┃                         ██
# MAGIC  0.2 ┃                           ██ ← 재학습 필요! 모델이 현장과 완전히 괴리
# MAGIC      ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAGIC       배포    1개월   3개월   6개월
# MAGIC ```
# MAGIC
# MAGIC > **실무 경험** : 제조 현장에서 ML 모델의 평균 유효 수명은 **1~3개월** 입니다. 이 기간 이후에는 반드시 재학습이 필요하며, 공정 변경이 빈번한 라인에서는 **매주 재학습** 이 권장됩니다.

# COMMAND ----------

# DBTITLE 1,실습: 드리프트 시뮬레이션 및 성능 저하 관찰
import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

feature_columns = [
    "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "temp_diff", "power", "tool_wear_rate", "strain",
    "overheat_flag", "product_quality", "risk_score"
]
label_col = "machine_failure"

# 학습 데이터 로드
full_df = spark.table("lgit_pm_training").filter("split='train'").select(*feature_columns, label_col).toPandas()
test_df = spark.table("lgit_pm_training").filter("split='test'").select(*feature_columns, label_col).toPandas()
X_train, Y_train = full_df[feature_columns], full_df[label_col]
X_test, Y_test = test_df[feature_columns], test_df[label_col]

# 1. 원본 데이터로 모델 학습
params = {"max_depth": 6, "learning_rate": 0.1, "objective": "binary:logistic",
          "eval_metric": "logloss", "seed": 42,
          "scale_pos_weight": (Y_train == 0).sum() / max((Y_train == 1).sum(), 1)}
dtrain = xgb.DMatrix(X_train, label=Y_train)
model_original = xgb.train(params, dtrain, num_boost_round=200)

# 2. 드리프트 시뮬레이션: 테스트 데이터에 점진적 노이즈 추가
drift_levels = [0, 0.5, 1.0, 2.0, 3.0, 5.0]
f1_scores = []

print("=== 데이터 드리프트에 따른 모델 성능 변화 ===\n")
print(f"{'드리프트 수준':>15s} | {'F1 Score':>10s} | {'변화':>10s} | 의미")
print("-" * 70)

for drift in drift_levels:
    # 드리프트 적용: 온도와 회전속도에 오프셋 추가
    X_drifted = X_test.copy()
    X_drifted["air_temperature_k"] += drift
    X_drifted["process_temperature_k"] += drift * 0.8
    X_drifted["temp_diff"] = X_drifted["process_temperature_k"] - X_drifted["air_temperature_k"]

    dtest = xgb.DMatrix(X_drifted)
    pred = (model_original.predict(dtest) > 0.5).astype(int)
    f1 = f1_score(Y_test, pred)
    f1_scores.append(f1)

    change = f1 - f1_scores[0]
    if drift == 0:
        meaning = "기준선 (학습 직후)"
    elif abs(change) < 0.02:
        meaning = "안정적"
    elif abs(change) < 0.05:
        meaning = "경미한 저하"
    elif abs(change) < 0.10:
        meaning = "주의 필요"
    else:
        meaning = "재학습 필요!"

    print(f"{drift:>15.1f}K | {f1:>10.4f} | {change:>+10.4f} | {meaning}")

print(f"\n결론: 온도가 {drift_levels[-1]}K 변하면 F1이 {f1_scores[0]:.4f} → {f1_scores[-1]:.4f}로 저하")
print("  → 이것이 바로 Data Drift로 인한 모델 성능 저하입니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 2: 재학습 트리거 전략
# MAGIC
# MAGIC ## "언제 재학습을 해야 하는가?" — MLOps에서 가장 어려운 질문
# MAGIC
# MAGIC 너무 자주 재학습하면 **불필요한 계산 비용** 이 발생하고, 너무 드물게 하면 **성능 저하를 방치** 하게 됩니다. 최적의 재학습 시점을 결정하는 것은 MLOps의 핵심 역량입니다.
# MAGIC
# MAGIC 재학습을 트리거하는 4가지 전략을 소개합니다.
# MAGIC
# MAGIC ### 전략 1: 스케줄 기반 (Time-based) — 가장 단순하고 안정적
# MAGIC
# MAGIC ```
# MAGIC "매주 월요일 새벽 2시에 재학습" (Databricks Workflow 스케줄 트리거)
# MAGIC
# MAGIC 장점: 구현이 가장 쉬움, 운영 예측 가능, 팀 프로세스에 통합 용이
# MAGIC 단점: 드리프트 없어도 불필요한 재학습 발생, 급격한 변화에 최대 7일 지연 대응
# MAGIC
# MAGIC LG Innotek 적합 시나리오:
# MAGIC   - 공정 조건이 안정적인 양산 라인
# MAGIC   - 계절 변화에 따른 점진적 드리프트 대응
# MAGIC   - MLOps 초기 도입 단계에서 먼저 적용 (가장 쉬운 시작점)
# MAGIC
# MAGIC ### 전략 2: 성능 기반 (Performance-based) — 가장 정확하지만 레이블 필요
# MAGIC
# MAGIC ```
# MAGIC "모델의 F1 Score가 0.7 아래로 떨어지면 재학습"
# MAGIC
# MAGIC 장점: 진짜 필요할 때만 재학습 (비용 효율적)
# MAGIC 단점: 실제 레이블(정답)이 필요 → 품질 검사 완료까지 시간 지연 (지연 레이블 문제)
# MAGIC
# MAGIC LG Innotek 적합 시나리오:
# MAGIC   - 출하 검사 결과가 24시간 내 확보되는 라인
# MAGIC   - 고객 클레임/반품 데이터가 빠르게 피드백되는 제품
# MAGIC   - Data Quality Monitoring으로 자동 성능 추적 구축 완료 시
# MAGIC
# MAGIC ### 전략 3: 드리프트 기반 (Drift-based) — 레이블 없이도 가능
# MAGIC
# MAGIC ```
# MAGIC "입력 데이터의 PSI가 0.2를 넘으면 재학습"
# MAGIC
# MAGIC 장점: 레이블(정답) 없이도 탐지 가능 — 센서 데이터만으로 판단
# MAGIC 단점: Concept Drift 감지 불가 (데이터 분포는 같은데 관계만 바뀐 경우)
# MAGIC
# MAGIC LG Innotek 적합 시나리오:
# MAGIC   - 센서 데이터가 실시간으로 Delta Lake에 적재되는 환경
# MAGIC   - 원자재 변경, 계절 변화 등 입력 데이터 변화가 주 원인인 경우
# MAGIC   - Databricks Data Quality Monitoring의 자동 PSI 계산 활용
# MAGIC
# MAGIC ### 전략 4: 하이브리드 (권장) — 실무 최적
# MAGIC
# MAGIC ```
# MAGIC 여러 조건을 조합하여 우선순위별 판단 (Databricks Workflow 조건부 분기):
# MAGIC
# MAGIC   IF (PSI > 0.2)           → 즉시 재학습 (긴급) — 데이터 분포 급변
# MAGIC   ELIF (F1 < 0.7)          → 즉시 재학습 (긴급) — 성능 임계치 이탈
# MAGIC   ELIF (마지막 학습 > 7일)  → 정기 재학습 (일반) — 안전망
# MAGIC   ELIF (새 데이터 > 5000건) → 추가 학습 고려 (낮음) — Incremental Learning
# MAGIC   ELSE                      → 현재 모델 유지 ✓
# MAGIC ```
# MAGIC
# MAGIC > **LG Innotek 권장** : MLOps 초기에는 **전략 1(스케줄 기반, 주 1회)** 로 시작하고, Data Quality Monitoring 구축 후 **전략 4(하이브리드)** 로 고도화하는 단계적 접근을 권장합니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 전략 선택 의사결정 가이드
# MAGIC
# MAGIC - **레이블 확보 가능?**
# MAGIC   - **Yes** → 24시간 이내 확보?
# MAGIC     - Yes → **성능 기반 (전략 2)**
# MAGIC     - No → **하이브리드 (전략 4)**
# MAGIC   - **No** → 센서 데이터 실시간?
# MAGIC     - Yes → **드리프트 기반 (전략 3)**
# MAGIC     - No → **스케줄 기반 (전략 1)**

# COMMAND ----------

# DBTITLE 1,실습: PSI (Population Stability Index) 계산 - 드리프트 탐지
# MAGIC %md
# MAGIC ### PSI(Population Stability Index)란?
# MAGIC
# MAGIC PSI는 **금융업계에서 신용평가 모델 모니터링** 을 위해 개발된 지표로, 이후 ML 전반에서 **데이터 분포 변화를 수치화** 하는 표준 도구로 자리잡았습니다. 두 시점(학습 vs 운영)의 데이터 분포를 비교하여 드리프트를 정량적으로 탐지합니다.
# MAGIC
# MAGIC > **Databricks Data Quality Monitoring** 에서도 PSI를 핵심 드리프트 탐지 지표로 사용합니다.
# MAGIC
# MAGIC ```
# MAGIC PSI 계산 방법 (제조 비유: SPC 관리도와 유사한 개념):
# MAGIC
# MAGIC 1. 학습 데이터의 분포를 10개 구간(bin)으로 나눔
# MAGIC    → SPC에서 규격 구간을 나누는 것과 유사
# MAGIC 2. 운영 데이터도 같은 구간으로 나눔
# MAGIC 3. 각 구간의 비율 차이를 계산 (KL Divergence의 대칭 버전)
# MAGIC
# MAGIC PSI = Σ (운영_비율 - 학습_비율) × ln(운영_비율 / 학습_비율)
# MAGIC
# MAGIC 해석 기준 (업계 표준):
# MAGIC   PSI < 0.1  : 변화 없음 (안정)      → 재학습 불필요 ✓
# MAGIC   PSI 0.1~0.2: 약간의 변화 (주의)    → 모니터링 빈도 증가, 원인 조사
# MAGIC   PSI > 0.2  : 유의미한 변화 (경고)  → 재학습 권장 (데이터 원인 파악 필수)
# MAGIC   PSI > 0.5  : 심각한 변화 (위험)    → 즉시 재학습 + 모델 예측 중단 검토
# MAGIC
# MAGIC **LG Innotek 실무 적용 예시** :
# MAGIC - 온도 센서의 PSI가 0.3 → "원인: 여름철 외기 온도 상승으로 공장 내부 온도 변화" → 재학습 실행
# MAGIC - 토크 센서의 PSI가 0.15 → "원인: 공구 마모에 따른 점진적 변화" → 모니터링 유지, 0.2 도달 시 재학습
# MAGIC - 전체 피처 PSI가 0.05 이하 → "안정적" → 현재 모델 유지

# COMMAND ----------

# DBTITLE 1,PSI 계산 함수 및 실습
def calculate_psi(expected, actual, bins=10):
    """
    Population Stability Index를 계산합니다.

    Args:
        expected: 학습 데이터의 피처 값 (기준 분포)
        actual: 운영 데이터의 피처 값 (비교 분포)
        bins: 히스토그램 구간 수

    Returns:
        float: PSI 값
    """
    # 1. 히스토그램 구간 생성 (학습 데이터 기준)
    breakpoints = np.linspace(
        min(expected.min(), actual.min()),
        max(expected.max(), actual.max()),
        bins + 1
    )

    # 2. 각 구간의 비율 계산
    expected_counts = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_counts = np.histogram(actual, bins=breakpoints)[0] / len(actual)

    # 3. 0 방지 (log 계산 오류 방지)
    expected_counts = np.maximum(expected_counts, 0.001)
    actual_counts = np.maximum(actual_counts, 0.001)

    # 4. PSI 계산
    psi = np.sum((actual_counts - expected_counts) * np.log(actual_counts / expected_counts))
    return psi


# 실습: 학습 데이터 vs 추론 데이터 PSI 비교
print("=== PSI 기반 드리프트 탐지 ===\n")
print(f"{'피처':>30s} | {'PSI':>8s} | {'판정':>10s}")
print("-" * 60)

monitor_features = ["air_temperature_k", "process_temperature_k",
                    "rotational_speed_rpm", "torque_nm", "tool_wear_min"]

try:
    infer_pdf = spark.table("lgit_pm_inference_results").select(*monitor_features).toPandas()
    data_source = "추론 테이블"
except:
    infer_pdf = X_test  # 추론 테이블이 없으면 테스트 데이터로 대체
    data_source = "테스트 데이터"

print(f"비교 대상: 학습 데이터 vs {data_source}\n")

any_drift = False
for col in monitor_features:
    psi = calculate_psi(X_train[col].values, infer_pdf[col].values)
    if psi < 0.1:
        status = "안정"
    elif psi < 0.2:
        status = "주의"
    elif psi < 0.5:
        status = "경고"
        any_drift = True
    else:
        status = "위험!"
        any_drift = True
    print(f"{col:>30s} | {psi:>8.4f} | {status:>10s}")

print(f"\n종합 판단: {'드리프트 감지 → 재학습 권장' if any_drift else '안정 → 현재 모델 유지'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 3: Full Retraining 실전 구현
# MAGIC
# MAGIC ## "재학습을 실제로 어떻게 하는가?"
# MAGIC
# MAGIC Full Retraining은 가장 기본적이면서도 **가장 확실한** 재학습 방법입니다.
# MAGIC 전체 데이터(또는 최근 일정 기간의 데이터)로 모델을 **처음부터 다시 학습** 합니다.
# MAGIC
# MAGIC 제조 현장 비유: 설비 세팅을 완전히 초기화하고, 최신 공정 조건으로 처음부터 다시 최적화하는 것과 같습니다. 시간은 걸리지만 **가장 확실한 성능 회복 방법** 입니다.
# MAGIC
# MAGIC > **Databricks 구현** : 아래 파이프라인은 **Databricks Workflow** 의 하나의 Task로 등록하여, 스케줄(매주 월요일) 또는 이벤트(Monitoring Alert)로 자동 실행할 수 있습니다.
# MAGIC
# MAGIC ### 재학습 파이프라인 전체 흐름
# MAGIC
# MAGIC ```
# MAGIC Step 1: 재학습 트리거 감지
# MAGIC   |  (스케줄/드리프트/성능 저하)
# MAGIC   v
# MAGIC Step 2: 학습 데이터 준비
# MAGIC   |  (Delta Lake에서 최신 데이터 로드)
# MAGIC   |  (Sliding Window로 기간 선택)
# MAGIC   v
# MAGIC Step 3: 새 모델 학습
# MAGIC   |  (기존과 동일한 알고리즘 + 하이퍼파라미터)
# MAGIC   |  (MLflow에 실험 기록)
# MAGIC   v
# MAGIC Step 4: 새 모델 검증
# MAGIC ```
# MAGIC   |  (기존 Champion 모델과 성능 비교)
# MAGIC   |  (비즈니스 KPI 확인)
# MAGIC   v
# MAGIC Step 5: 배포 결정
# MAGIC ```
# MAGIC   |  IF 새 모델 > 기존 모델 → Champion 교체
# MAGIC   |  ELSE → 기존 모델 유지 (또는 알림)
# MAGIC   v
# MAGIC Step 6: 모니터링 재시작
# MAGIC   |  (새 모델 기준으로 드리프트 모니터링 리셋)

# COMMAND ----------

# DBTITLE 1,실전: 자동 재학습 파이프라인 구현
import mlflow
from mlflow import MlflowClient
from sklearn.metrics import f1_score, roc_auc_score, classification_report
from datetime import datetime

client = MlflowClient()
model_name = f"{catalog}.{db}.lgit_predictive_maintenance"

def full_retrain_pipeline(reason="scheduled"):
    """
    Full Retraining Pipeline: 전체 재학습 프로세스를 자동화합니다.

    이 함수는 Databricks Workflow의 Task로 등록하여
    스케줄(주 1회) 또는 이벤트(드리프트 감지) 시 자동 실행됩니다.

    Args:
        reason: 재학습 사유 ("scheduled", "drift_detected", "performance_degraded")
    """
    print(f"{'='*60}")
    print(f"  재학습 파이프라인 시작")
    print(f"  시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  사유: {reason}")
    print(f"{'='*60}\n")

    # ─── Step 1: 학습 데이터 준비 ───
    print("Step 1: 학습 데이터 준비...")

    # Sliding Window: 전체 데이터 사용 (실제 운영에서는 최근 N일)
    # 실제 코드: spark.sql("SELECT * FROM lgit_pm_training WHERE date >= current_date() - INTERVAL 90 DAYS")
    train_data = spark.table("lgit_pm_training").filter("split='train'").select(*feature_columns, label_col).toPandas()
    test_data = spark.table("lgit_pm_training").filter("split='test'").select(*feature_columns, label_col).toPandas()
    X_tr, Y_tr = train_data[feature_columns], train_data[label_col]
    X_te, Y_te = test_data[feature_columns], test_data[label_col]

    print(f"  학습 데이터: {len(X_tr)}건, 테스트 데이터: {len(X_te)}건")
    print(f"  고장 비율: {Y_tr.mean():.4f}")

    # ─── Step 2: MLflow 실험에 기록하면서 모델 학습 ───
    print("\nStep 2: 새 모델 학습 (MLflow 추적)...")

    xp_name = "lgit_predictive_maintenance"
    xp_path = f"/Users/{current_user}"
    mlflow.set_experiment(f"{xp_path}/{xp_name}")

    with mlflow.start_run(run_name=f"retrain_{reason}_{datetime.now().strftime('%Y%m%d')}") as run:
        # 재학습 메타데이터 기록
        mlflow.log_param("retrain_reason", reason)
        mlflow.log_param("retrain_timestamp", datetime.now().isoformat())
        mlflow.log_param("training_data_size", len(X_tr))

        # 불균형 보정 가중치
        sw = (Y_tr == 0).sum() / max((Y_tr == 1).sum(), 1)

        # XGBoost 학습
        retrain_params = {
            "max_depth": 6, "learning_rate": 0.1, "objective": "binary:logistic",
            "eval_metric": "logloss", "seed": 42, "scale_pos_weight": sw,
            "subsample": 0.8, "colsample_bytree": 0.8
        }

        dtrain = xgb.DMatrix(X_tr, label=Y_tr)
        new_model = xgb.train(retrain_params, dtrain, num_boost_round=200)

        # 테스트 성능 평가
        dtest = xgb.DMatrix(X_te)
        pred = (new_model.predict(dtest) > 0.5).astype(int)
        proba = new_model.predict(dtest)
        new_f1 = f1_score(Y_te, pred)
        new_auc = roc_auc_score(Y_te, proba)

        mlflow.log_metrics({"test_f1_score": new_f1, "test_auc": new_auc})

        # 모델 저장 시 Signature 필수 (Unity Catalog 요구사항)
        from mlflow.models import infer_signature
        signature = infer_signature(X_tr, proba)
        mlflow.xgboost.log_model(new_model, "xgboost_model", signature=signature)

        print(f"  새 모델 성능 - F1: {new_f1:.4f}, AUC: {new_auc:.4f}")

    # ─── Step 3: 기존 Champion 모델과 비교 ───
    print("\nStep 3: Champion 모델과 성능 비교...")

    try:
        champion_info = client.get_model_version_by_alias(model_name, "Champion")
        champion_f1 = mlflow.get_run(champion_info.run_id).data.metrics.get("test_f1_score", 0)
        champion_auc = mlflow.get_run(champion_info.run_id).data.metrics.get("test_auc", 0)
        print(f"  기존 Champion (v{champion_info.version}) - F1: {champion_f1:.4f}, AUC: {champion_auc:.4f}")
        print(f"  새 모델                       - F1: {new_f1:.4f}, AUC: {new_auc:.4f}")
        champion_exists = True
    except:
        print("  기존 Champion 없음 → 새 모델을 Champion으로 등록")
        champion_exists = False
        champion_f1 = 0

    # ─── Step 4: 배포 결정 ───
    print("\nStep 4: 배포 결정...")

    should_deploy = not champion_exists or new_f1 >= champion_f1

    if should_deploy:
        # 새 모델 등록 및 Champion 승급
        model_details = mlflow.register_model(
            f"runs:/{run.info.run_id}/xgboost_model", model_name
        )

        client.set_registered_model_alias(
            name=model_name, alias="Champion", version=model_details.version
        )

        improvement = new_f1 - champion_f1 if champion_exists else new_f1
        print(f"  결정: 새 모델 배포 (v{model_details.version})")
        print(f"  F1 개선: {improvement:+.4f}")

        # 태그 기록
        try:
            client.set_model_version_tag(name=model_name, version=model_details.version,
                                        key="retrain_reason", value=reason)
        except:
            pass

        return {"deployed": True, "version": model_details.version, "f1": new_f1}
    else:
        print(f"  결정: 기존 모델 유지 (새 모델 F1 {new_f1:.4f} < Champion F1 {champion_f1:.4f})")
        return {"deployed": False, "f1": new_f1}


# 재학습 실행
result = full_retrain_pipeline(reason="scheduled")
print(f"\n{'='*60}")
print(f"  재학습 파이프라인 완료: {'배포됨' if result['deployed'] else '기존 유지'}")
print(f"{'='*60}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 4: 학습 데이터 관리 — Delta Lake 활용
# MAGIC
# MAGIC ## "어떤 데이터로 재학습해야 하는가?"
# MAGIC
# MAGIC 재학습의 성패는 **어떤 데이터를 사용하느냐** 에 달려 있습니다.
# MAGIC 너무 오래된 데이터를 포함하면 현재 패턴과 맞지 않고, 너무 최신 데이터만 사용하면 희소한 이벤트(드물게 발생하는 고장 유형)를 놓칠 수 있습니다.
# MAGIC
# MAGIC **Databricks Delta Lake** 의 고유 기능(Time Travel, 버전 관리, 스키마 진화)을 활용하면 학습 데이터를 **체계적이고 재현 가능하게** 관리할 수 있습니다. 이는 다른 데이터 플랫폼에서는 별도의 데이터 버전 관리 도구(DVC 등)를 설치해야 하는 기능입니다.
# MAGIC
# MAGIC ### 4.1 Sliding Window (슬라이딩 윈도우)
# MAGIC
# MAGIC **최근 N일의 데이터만** 사용하여 학습하는 방법입니다.
# MAGIC 오래된 데이터는 현재 패턴과 다를 수 있으므로 자연스럽게 제외합니다.
# MAGIC
# MAGIC ```
# MAGIC 시간 →  1월   2월   3월   4월   5월   6월   7월
# MAGIC
# MAGIC 3월 학습: [========90일========]
# MAGIC 4월 학습:       [========90일========]
# MAGIC 5월 학습:             [========90일========]
# MAGIC
# MAGIC 각 학습마다 최근 90일 데이터만 사용
# MAGIC → 오래된 패턴 자동 제거, 최신 패턴 반영
# MAGIC ```
# MAGIC
# MAGIC ### 4.2 Delta Lake Time Travel
# MAGIC
# MAGIC **Delta Lake의 Time Travel** 기능을 사용하면 **특정 시점의 데이터** 를 조회할 수 있습니다.
# MAGIC 이를 통해 학습 데이터의 재현성과 감사(Audit) 추적이 가능합니다.
# MAGIC
# MAGIC ```sql
# MAGIC -- 특정 버전의 데이터 조회
# MAGIC SELECT * FROM lgit_pm_training VERSION AS OF 5
# MAGIC
# MAGIC -- 특정 시점의 데이터 조회
# MAGIC SELECT * FROM lgit_pm_training TIMESTAMP AS OF '2024-01-01'
# MAGIC
# MAGIC -- 최근 30일 데이터만 조회 (Sliding Window)
# MAGIC SELECT * FROM lgit_pm_inference_results
# MAGIC WHERE inference_timestamp >= current_date() - INTERVAL 30 DAYS

# COMMAND ----------

# DBTITLE 1,실습: Delta Lake 기반 학습 데이터 관리
# Delta Lake Time Travel 실습

# 현재 테이블 버전 확인
history = spark.sql(f"DESCRIBE HISTORY {catalog}.{db}.lgit_pm_training").select(
    "version", "timestamp", "operation", "operationMetrics"
)
print("=== lgit_pm_training 테이블 히스토리 ===")
display(history)

# COMMAND ----------

# DBTITLE 1,학습 데이터 윈도우 전략 비교
# 서로 다른 데이터 윈도우로 학습 → 성능 비교
print("=== 학습 데이터 윈도우별 성능 비교 ===\n")

# 전체 데이터를 3개 기간으로 나눔 (시뮬레이션)
n = len(full_df)
periods = {
    "최근 1/3 (최신 데이터만)": full_df.iloc[2*n//3:],
    "최근 2/3 (중간 + 최신)": full_df.iloc[n//3:],
    "전체 데이터": full_df,
}

print(f"{'데이터 윈도우':>25s} | {'학습 건수':>10s} | {'F1':>8s} | {'AUC':>8s}")
print("-" * 65)

for name, data in periods.items():
    X = data[feature_columns]
    Y = data[label_col]
    dt = xgb.DMatrix(X, label=Y)
    m = xgb.train(params, dt, num_boost_round=200, verbose_eval=False)
    dtest = xgb.DMatrix(X_test)
    pred = (m.predict(dtest) > 0.5).astype(int)
    proba = m.predict(dtest)
    f1 = f1_score(Y_test, pred)
    auc = roc_auc_score(Y_test, proba)
    print(f"{name:>25s} | {len(data):>10d} | {f1:>8.4f} | {auc:>8.4f}")

print(f"\n일반적으로:")
print(f"  - 데이터가 많을수록 성능이 좋지만, 오래된 데이터는 오히려 해로울 수 있음")
print(f"  - 최적 윈도우 크기는 데이터 변화 속도에 따라 결정")
print(f"  - 권장: 최근 60~90일 데이터로 시작, 성능을 보며 조정")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 5: 모델 버전 관리와 롤백
# MAGIC
# MAGIC ## "새 모델이 나쁘면 어떻게 되돌리는가?" — 안전한 배포의 핵심
# MAGIC
# MAGIC 재학습된 새 모델이 항상 더 좋다는 보장은 없습니다. 학습 데이터에 문제가 있거나, 특정 구간에서 기존 모델보다 성능이 나빠질 수 있습니다. 이때 **즉시 이전 모델로 되돌릴 수 있는 능력** 은 운영 안정성의 핵심입니다.
# MAGIC
# MAGIC 제조 현장 비유: 공정 조건을 변경했는데 불량률이 증가하면, **즉시 이전 레시피로 복구** 하는 것과 같습니다. 이를 위해 모든 레시피 이력을 관리하듯이, 모든 모델 버전을 Unity Catalog에서 관리합니다.
# MAGIC
# MAGIC ### Unity Catalog 에일리어스를 활용한 안전한 배포
# MAGIC
# MAGIC ```
# MAGIC 배포 전:                     배포 후 (문제 없음):           롤백 시:
# MAGIC ```
# MAGIC +------------+              +------------+              +------------+
# MAGIC | v3 Champion|              | v4 Champion|              | v3 Champion| ← 되돌림!
# MAGIC | v4 Challgr |              | v3 Previous|              | v4 Failed  |
# MAGIC +------------+              +------------+              +------------+
# MAGIC ```
# MAGIC
# MAGIC 핵심: 코드를 변경하지 않고 에일리어스만 변경하면 즉시 롤백 가능
# MAGIC       배치 추론 코드: models:/model_name@Champion ← 항상 이 참조 사용
# MAGIC ```
# MAGIC
# MAGIC ### 롤백이 필요한 상황:
# MAGIC 1. 새 모델의 운영 성능이 검증 성능보다 현저히 낮은 경우
# MAGIC 2. 새 모델이 특정 데이터 구간에서 심각한 오류를 보이는 경우
# MAGIC 3. 규제/컴플라이언스 이슈로 이전 모델로 복구해야 하는 경우

# COMMAND ----------

# DBTITLE 1,실습: 모델 롤백 구현
def rollback_model(model_name, target_version=None):
    """
    모델을 이전 버전으로 롤백합니다.

    Unity Catalog의 에일리어스(Alias) 기능을 사용하므로,
    배포 코드(models:/model_name@Champion)를 변경할 필요 없이
    에일리어스만 변경하면 즉시 롤백됩니다.

    Args:
        model_name: UC 모델 전체 이름
        target_version: 롤백할 버전 (None이면 직전 버전)
    """
    try:
        # 현재 Champion 버전 확인
        current = client.get_model_version_by_alias(model_name, "Champion")
        current_version = int(current.version)
        print(f"현재 Champion: v{current_version}")

        if target_version is None:
            # 직전 버전으로 롤백
            target_version = max(1, current_version - 1)

        if target_version == current_version:
            print("롤백 대상이 현재 버전과 동일합니다.")
            return

        # 롤백 실행
        print(f"롤백: v{current_version} → v{target_version}")

        # 현재 Champion에 "Rolled_Back" 태그 추가
        try:
            client.set_model_version_tag(
                name=model_name, version=str(current_version),
                key="rolled_back", value="true"
            )
        except:
            pass

        # 에일리어스 변경 → 즉시 롤백 완료
        client.set_registered_model_alias(
            name=model_name, alias="Champion", version=target_version
        )

        print(f"롤백 완료! 새 Champion: v{target_version}")
        print(f"배포 코드 변경 불필요 (models:/{model_name}@Champion)")
    except Exception as e:
        print(f"롤백 참고: {e}")


# 롤백 시뮬레이션 (실제로는 문제 발견 시에만 실행)
print("=== 롤백 시뮬레이션 ===\n")
print("현재 모델 버전:")
try:
    champion = client.get_model_version_by_alias(model_name, "Champion")
    print(f"  Champion: v{champion.version}")
    print(f"\n[참고] 롤백이 필요한 경우 다음을 실행:")
    print(f"  rollback_model('{model_name}', target_version={max(1, int(champion.version)-1)})")
except Exception as e:
    print(f"  모델 조회 참고: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 6: Incremental Learning (점진적 학습)
# MAGIC
# MAGIC ## "전체 데이터 없이 모델을 업데이트하는 방법"
# MAGIC
# MAGIC Full Retraining은 확실하지만, 데이터가 수억 건으로 커지면 **학습 시간과 비용이 과도** 해집니다.
# MAGIC **Incremental Learning** 은 기존 모델을 폐기하지 않고, **새 데이터만으로 모델을 보강** 합니다.
# MAGIC
# MAGIC 제조 현장 비유: 설비 세팅을 처음부터 다시 하는 것(Full Retrain)이 아니라, 현재 세팅에서 **미세 조정(Fine-tuning)** 만 하는 것과 같습니다. 기존의 좋은 세팅은 유지하면서 최신 변화에만 적응합니다.
# MAGIC
# MAGIC ### Full Retraining vs Incremental Learning
# MAGIC
# MAGIC ```
# MAGIC Full Retraining (전체 재학습):
# MAGIC ```
# MAGIC   +----------------------------------+
# MAGIC ```
# MAGIC   | 전체 데이터 (1년치 100만건)        | → 새 모델 (처음부터)
# MAGIC ```
# MAGIC   +----------------------------------+
# MAGIC ```
# MAGIC   시간: 2시간 | 비용: 높음 | 정확도: 최고
# MAGIC
# MAGIC Incremental Learning (점진적 학습):
# MAGIC ```
# MAGIC   +------------+
# MAGIC ```
# MAGIC ```
# MAGIC   | 기존 모델    | + +--------------+ → 업데이트된 모델
# MAGIC ```
# MAGIC   +------------+   | 새 데이터 (1주) |
# MAGIC                    +--------------+
# MAGIC ```
# MAGIC ```
# MAGIC   시간: 10분 | 비용: 낮음 | 정확도: 양호
# MAGIC
# MAGIC ### XGBoost의 Incremental Learning 원리
# MAGIC
# MAGIC XGBoost는 **트리를 순차적으로 추가** 하는 방식이므로,
# MAGIC 기존 트리를 유지하면서 **새로운 트리만 추가** 할 수 있습니다.
# MAGIC
# MAGIC ```python
# MAGIC # 기존 모델에 새 데이터로 트리 50개 추가
# MAGIC updated_model = xgb.train(
# MAGIC     params,
# MAGIC     new_data,
# MAGIC     num_boost_round=50,      # 새로 추가할 트리 수
# MAGIC     xgb_model=existing_model  # 기존 모델을 시작점으로
# MAGIC )
# MAGIC ```

# COMMAND ----------

# DBTITLE 1,실습: Incremental Learning 단계별 구현
# 데이터를 3개 배치로 나눔 (시간순 시뮬레이션)
batch_size = len(full_df) // 3
batches = [full_df.iloc[i*batch_size:(i+1)*batch_size] for i in range(3)]
dtest = xgb.DMatrix(X_test)

print("=== Incremental Learning 단계별 실습 ===\n")

# ─── Batch 1: 초기 모델 학습 ───
print("▶ Batch 1: 초기 모델 학습")
X1, Y1 = batches[0][feature_columns], batches[0][label_col]
dtrain1 = xgb.DMatrix(X1, label=Y1)
model_inc = xgb.train(params, dtrain1, num_boost_round=100)
f1_b1 = f1_score(Y_test, (model_inc.predict(dtest) > 0.5).astype(int))
print(f"  데이터: {len(X1)}건 | 트리 수: {model_inc.num_boosted_rounds()} | F1: {f1_b1:.4f}")

# ─── Batch 2: 기존 모델에 추가 학습 ───
print("\n▶ Batch 2: Incremental Learning (기존 모델 + 새 데이터)")
X2, Y2 = batches[1][feature_columns], batches[1][label_col]
dtrain2 = xgb.DMatrix(X2, label=Y2)

# 핵심: xgb_model 파라미터로 기존 모델 전달
model_inc = xgb.train(params, dtrain2, num_boost_round=50, xgb_model=model_inc)
f1_b2 = f1_score(Y_test, (model_inc.predict(dtest) > 0.5).astype(int))
print(f"  추가 데이터: {len(X2)}건 | 총 트리 수: {model_inc.num_boosted_rounds()} | F1: {f1_b2:.4f}")

# ─── Batch 3: 추가 학습 ───
print("\n▶ Batch 3: Incremental Learning (계속)")
X3, Y3 = batches[2][feature_columns], batches[2][label_col]
dtrain3 = xgb.DMatrix(X3, label=Y3)
model_inc = xgb.train(params, dtrain3, num_boost_round=50, xgb_model=model_inc)
f1_b3 = f1_score(Y_test, (model_inc.predict(dtest) > 0.5).astype(int))
print(f"  추가 데이터: {len(X3)}건 | 총 트리 수: {model_inc.num_boosted_rounds()} | F1: {f1_b3:.4f}")

# ─── 비교: Full Retraining ───
print("\n▶ 비교: Full Retraining (전체 데이터 처음부터)")
dtrain_full = xgb.DMatrix(X_train, label=Y_train)
model_full = xgb.train(params, dtrain_full, num_boost_round=200)
f1_full = f1_score(Y_test, (model_full.predict(dtest) > 0.5).astype(int))
print(f"  전체 데이터: {len(X_train)}건 | 트리 수: 200 | F1: {f1_full:.4f}")

# 요약
print(f"\n{'='*50}")
print(f"  Incremental (3배치): F1 = {f1_b3:.4f}")
print(f"  Full Retrain:        F1 = {f1_full:.4f}")
print(f"  차이: {abs(f1_full - f1_b3):.4f}")
print(f"{'='*50}")
print(f"\n언제 Incremental을 사용하나?")
print(f"  - 학습 시간/비용을 줄여야 할 때")
print(f"  - 데이터 변화가 점진적일 때")
print(f"  - 실시간에 가까운 빈번한 업데이트가 필요할 때")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 7: Continual Learning (연속 학습)
# MAGIC
# MAGIC ## "이전에 배운 것을 잊지 않으면서 새로운 것을 배우는 방법"
# MAGIC
# MAGIC Incremental Learning(Part 6)의 심각한 부작용이 있습니다: **Catastrophic Forgetting(파국적 망각)** .
# MAGIC 이는 신경과학에서 유래한 용어로, 새로운 정보를 학습하면서 **이전에 학습한 정보를 잊어버리는 현상** 입니다.
# MAGIC
# MAGIC ### 문제: Catastrophic Forgetting (파국적 망각)
# MAGIC
# MAGIC 새 데이터만으로 모델을 학습하면, **이전에 학습한 패턴을 잊어버릴** 수 있습니다.
# MAGIC
# MAGIC ```
# MAGIC LG Innotek 시나리오:
# MAGIC
# MAGIC   1월: 카메라 모듈 라인 A의 "열 스트레스" 고장 패턴을 학습
# MAGIC   4월: 라인 B의 "기계적 마모" 고장 데이터만으로 Incremental Learning
# MAGIC   결과: 라인 A의 "열 스트레스" 고장 패턴을 완전히 잊어버림!
# MAGIC        → 여름에 라인 A에서 열 스트레스 고장이 발생해도 탐지 불가
# MAGIC ```
# MAGIC
# MAGIC 이 문제는 **다중 생산 라인, 다중 제품** 을 하나의 모델로 관리하는 LG Innotek 같은 환경에서 특히 심각합니다.
# MAGIC
# MAGIC ### 해결책: Experience Replay (경험 재생)
# MAGIC
# MAGIC **이전 데이터의 대표 샘플을 보관** 하고, 새 데이터와 함께 학습합니다.
# MAGIC
# MAGIC ```
# MAGIC ```
# MAGIC ```
# MAGIC ```
# MAGIC +---------------------+
# MAGIC | Replay Buffer        | ← 이전 데이터 중 대표 2000건 보관
# MAGIC |  (과거 학습 데이터)   |
# MAGIC +----------+----------+
# MAGIC ```
# MAGIC            |
# MAGIC            v
# MAGIC ```
# MAGIC ```
# MAGIC ```
# MAGIC +------------------------------+
# MAGIC | 새 데이터 + 리플레이 데이터    | → 모델 학습
# MAGIC | (이번 주)   (과거 대표 샘플)   |    → 새 패턴 학습 + 과거 패턴 유지!
# MAGIC +------------------------------+
# MAGIC ```
# MAGIC ```

# COMMAND ----------

# DBTITLE 1,실습: Replay Buffer 기반 Continual Learning
import random

class ReplayBuffer:
    """
    Experience Replay Buffer (경험 재생 버퍼)

    과거 학습 데이터의 대표 샘플을 보관합니다.
    새 데이터와 함께 학습하여 Catastrophic Forgetting을 방지합니다.

    저장소: 실제 운영에서는 Delta Lake 테이블로 관리
      CREATE TABLE replay_buffer AS
      SELECT * FROM lgit_pm_training
      ORDER BY RAND()
      LIMIT 2000
    """

    def __init__(self, max_size=2000):
        self.buffer = []
        self.max_size = max_size
        print(f"  Replay Buffer 생성 (최대 {max_size}건)")

    def add(self, X, Y):
        """새 배치에서 대표 샘플을 버퍼에 추가"""
        data = list(zip(X.values.tolist(), Y.values.tolist()))
        self.buffer.extend(data)
        # 버퍼 크기 초과 시 랜덤 샘플링으로 다양성 유지
        if len(self.buffer) > self.max_size:
            self.buffer = random.sample(self.buffer, self.max_size)

    def get_replay_data(self, n_samples=500):
        """리플레이 데이터를 추출"""
        if not self.buffer:
            return None, None
        samples = random.sample(self.buffer, min(n_samples, len(self.buffer)))
        X = pd.DataFrame([s[0] for s in samples], columns=feature_columns)
        Y = pd.Series([s[1] for s in samples])
        return X, Y


# ─── Continual Learning 시뮬레이션 ───
print("=== Continual Learning (Replay Buffer) ===\n")
replay = ReplayBuffer(max_size=2000)

for i, batch in enumerate(batches):
    X_b = batch[feature_columns]
    Y_b = batch[label_col]

    # 리플레이 데이터 + 새 데이터 결합
    X_rep, Y_rep = replay.get_replay_data(500)
    if X_rep is not None:
        X_combined = pd.concat([X_b, X_rep], ignore_index=True)
        Y_combined = pd.concat([Y_b, Y_rep], ignore_index=True)
        print(f"  Batch {i+1}: 새 데이터 {len(X_b)}건 + 리플레이 {len(X_rep)}건")
    else:
        X_combined = X_b
        Y_combined = Y_b
        print(f"  Batch {i+1}: 새 데이터 {len(X_b)}건 (첫 배치)")

    # 모델 학습 (처음부터, 하지만 과거 데이터 포함)
    dt = xgb.DMatrix(X_combined, label=Y_combined)
    model_cl = xgb.train(params, dt, num_boost_round=150)
    pred = (model_cl.predict(dtest) > 0.5).astype(int)
    f1 = f1_score(Y_test, pred)
    print(f"    → F1: {f1:.4f}\n")

    # 현재 배치를 버퍼에 추가
    replay.add(X_b, Y_b)

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 8: Online Learning (온라인 학습)
# MAGIC
# MAGIC ## "데이터가 들어올 때마다 즉시 모델을 업데이트" — 실시간 적응
# MAGIC
# MAGIC 지금까지의 모든 기법(Full Retrain, Incremental, Continual)은 **배치(Batch) 방식** 입니다. 데이터를 모아서 일괄 학습합니다. 하지만 제조 현장에서는 센서 데이터가 **매 초 실시간으로** 들어옵니다. 이 데이터를 즉시 반영하여 모델을 실시간으로 적응시킬 수는 없을까요?
# MAGIC
# MAGIC 이것이 **Online Learning** 입니다.
# MAGIC
# MAGIC ### Batch Learning vs Online Learning
# MAGIC
# MAGIC ```
# MAGIC Batch Learning (기존 방식):
# MAGIC   데이터 1주일 모음 → 한 번에 학습 → 다음 주까지 모델 고정
# MAGIC   [수집...수집...수집] → [학습!] → [예측...예측...예측]
# MAGIC   특징: 안정적, 검증 가능, 하지만 최대 7일의 적응 지연
# MAGIC
# MAGIC Online Learning (실시간 학습):
# MAGIC   데이터 1건 도착 → 예측 → 정답 확인 → 즉시 모델 업데이트
# MAGIC   [도착→예측→학습] → [도착→예측→학습] → [도착→예측→학습]
# MAGIC   특징: 즉각적 적응, 하지만 노이즈에 민감, 검증 어려움
# MAGIC
# MAGIC Mini-batch Online Learning (실무 권장):
# MAGIC   데이터 100건 모음 → 예측 → 학습 → 100건 모음 → 반복
# MAGIC   [100건 수집] → [예측+학습] → [100건 수집] → [예측+학습]
# MAGIC   특징: 실시간 적응과 안정성의 균형
# MAGIC ```
# MAGIC
# MAGIC > **실무 적용** : Online Learning은 단독으로 사용하기보다는 **"보조 모델"** 로 활용합니다. 주력 모델(XGBoost Batch)은 주 1회 재학습하고, Online 모델은 실시간 트렌드를 파악하는 **조기 경보 시스템** 역할을 합니다. Databricks Structured Streaming과 결합하면 실시간 파이프라인을 구축할 수 있습니다.
# MAGIC
# MAGIC ### River 라이브러리
# MAGIC
# MAGIC Python의 **River** (2020년 creme + scikit-multiflow 통합)는 Online Learning 전용 프레임워크입니다.
# MAGIC - 데이터를 한 건씩 처리하는 **스트리밍 ML 알고리즘** 제공
# MAGIC - **Hoeffding Tree** : 스트리밍 결정 트리 — 데이터를 **한 번만 봐도** 학습 가능 (메모리 효율적)
# MAGIC - **Hoeffding Adaptive Tree** : 드리프트를 자동 감지하고 **트리 구조를 동적으로 변경** (ADWIN 알고리즘 내장)
# MAGIC - 제조 현장의 센서 스트리밍 데이터에 적합

# COMMAND ----------

# DBTITLE 1,실습: Online Learning (River)
from river import tree, metrics, preprocessing, compose

# River의 Hoeffding Adaptive Tree
# - 데이터를 한 건씩 처리
# - 드리프트를 자동으로 탐지하고 트리 구조를 적응
model_online = compose.Pipeline(
    preprocessing.StandardScaler(),  # 실시간 표준화 (평균/분산을 온라인으로 계산)
    tree.HoeffdingAdaptiveTreeClassifier(seed=42)
)

metric = metrics.F1()
checkpoint_f1s = []

print("=== Online Learning 시뮬레이션 ===\n")
print("데이터를 한 건씩 처리하며 모델을 실시간 업데이트합니다.\n")

for i, (_, row) in enumerate(full_df.iterrows()):
    x = {col: row[col] for col in feature_columns}
    y = int(row[label_col])

    # 1단계: 현재 모델로 예측 (학습 전)
    y_pred = model_online.predict_one(x)

    # 2단계: 실제 정답과 비교하여 메트릭 업데이트
    if y_pred is not None:
        metric.update(y, y_pred)

    # 3단계: 이 한 건으로 모델 업데이트 (Online Learning의 핵심)
    model_online.learn_one(x, y)

    # 진행 출력 (1000건마다)
    if (i + 1) % 1000 == 0:
        current_f1 = metric.get()
        checkpoint_f1s.append(current_f1)
        print(f"  {i+1:>6d}건 처리: F1 = {current_f1:.4f}")

print(f"\n최종 Online Learning F1: {metric.get():.4f}")
print(f"Batch XGBoost F1:       {f1_full:.4f}")
print(f"\n실무 적용:")
print(f"  - Online Learning은 '보조 모델'로 활용 (실시간 경향 파악)")
print(f"  - 주력 모델은 Batch로 학습, Online으로 빠른 적응 보완")
print(f"  - Databricks Structured Streaming으로 실시간 파이프라인 구축 가능")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 9: 강화학습 기반 재학습 전략 자동 선택
# MAGIC
# MAGIC ## "AI가 최적의 재학습 전략을 스스로 선택" — MLOps의 최종 목표
# MAGIC
# MAGIC Part 2에서 재학습 트리거 전략(스케줄/성능/드리프트/하이브리드)을 배웠고, Part 6~8에서 다양한 재학습 방법(Full/Incremental/Online)을 배웠습니다. 하지만 **"지금 이 상황에서 어떤 전략을 써야 하는가?"** 를 매번 사람이 판단해야 할까요?
# MAGIC
# MAGIC **Contextual Bandit** 은 이 의사결정 자체를 **AI가 자동으로 학습** 하게 합니다. 이는 MLOps 자동화의 최종 단계에 해당하며, 현재 **최신 연구 분야** 입니다.
# MAGIC
# MAGIC ### Contextual Bandit이란?
# MAGIC
# MAGIC 강화학습(Reinforcement Learning)의 간소화 버전으로, **현재 상황(Context)을 보고 최적의 행동(Action)을 선택** 하는 기법입니다. 여러 재학습 전략 중 **현재 상황에 가장 적합한 전략** 을 자동으로 선택합니다.
# MAGIC
# MAGIC 제조 현장 비유: 숙련된 공정 엔지니어가 "이 상황이면 이렇게 대응한다"는 **경험 기반 의사결정** 을 하는 것을 AI가 학습하는 것입니다.
# MAGIC
# MAGIC ```
# MAGIC 상황 (Context):                 선택 가능한 전략 (Action):
# MAGIC  - 드리프트 수준: 0.3           1. Full Retrain
# MAGIC  - 새 데이터: 5000건             2. Incremental
# MAGIC  - 마지막 학습: 5일 전            3. Sliding Window
# MAGIC  - 현재 F1: 0.75                 4. No Action
# MAGIC
# MAGIC Bandit이 과거 경험에 기반하여 최적 전략 선택:
# MAGIC  → "드리프트가 크고 새 데이터가 많으므로 Full Retrain 선택"
# MAGIC
# MAGIC 재학습 후 성능 변화로 보상(Reward) 계산:
# MAGIC  → F1이 0.75 → 0.85로 개선 → 보상 +0.10
# MAGIC  → 다음에 비슷한 상황이면 Full Retrain 확률 증가
# MAGIC ```

# COMMAND ----------

# DBTITLE 1,실습: Contextual Bandit 재학습 전략 선택기
class RetrainingBandit:
    """
    Contextual Bandit 기반 재학습 전략 자동 선택기.

    Thompson Sampling을 사용하여 탐색(Exploration)과 활용(Exploitation)을 균형합니다.
    - 탐색: 아직 잘 모르는 전략도 가끔 시도
    - 활용: 좋은 결과를 준 전략을 더 자주 선택
    """

    def __init__(self):
        self.actions = ["no_action", "incremental", "sliding_window", "full_retrain"]
        # Beta 분포의 파라미터 (성공/실패 횟수)
        self.alpha = {a: 1.0 for a in self.actions}
        self.beta_ = {a: 1.0 for a in self.actions}
        self.history = []

    def select_action(self, context):
        """현재 상황에서 최적의 재학습 전략을 선택합니다."""
        scores = {}
        drift = context.get("drift_level", 0)

        for action in self.actions:
            # Beta 분포에서 기대 보상 샘플링 (Thompson Sampling)
            base_score = np.random.beta(self.alpha[action], self.beta_[action])

            # 컨텍스트 기반 보정
            if action == "full_retrain" and drift > 0.2:
                base_score += 0.3
            elif action == "incremental" and 0.05 < drift <= 0.2:
                base_score += 0.2
            elif action == "no_action" and drift < 0.05:
                base_score += 0.3

            scores[action] = base_score

        best = max(scores, key=scores.get)
        return best, scores

    def update(self, action, reward):
        """보상에 따라 분포를 업데이트합니다."""
        if reward > 0:
            self.alpha[action] += reward
        else:
            self.beta_[action] += abs(reward)
        self.history.append({"action": action, "reward": reward})


# 시뮬레이션
bandit = RetrainingBandit()
scenarios = [
    {"drift_level": 0.01, "desc": "안정 상태 (드리프트 거의 없음)"},
    {"drift_level": 0.12, "desc": "경미한 드리프트 (주의 수준)"},
    {"drift_level": 0.35, "desc": "심각한 드리프트 (즉시 대응 필요)"},
    {"drift_level": 0.05, "desc": "미미한 변화"},
    {"drift_level": 0.28, "desc": "중간 드리프트"},
]

print("=== Contextual Bandit 재학습 전략 자동 선택 ===\n")
for s in scenarios:
    action, scores = bandit.select_action(s)
    # 보상 시뮬레이션
    reward = 1 if (s["drift_level"] > 0.1 and action != "no_action") else \
             (0.5 if action == "no_action" and s["drift_level"] < 0.05 else -0.5)
    bandit.update(action, reward)

    print(f"  상황: {s['desc']}")
    print(f"    선택: {action:20s} (보상: {reward:+.1f})")
    print()

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 10: Active Learning (능동 학습)
# MAGIC
# MAGIC ## "어떤 데이터를 우선 레이블링해야 하는가?" — 레이블링 비용 최소화
# MAGIC
# MAGIC ML 모델의 성능은 **레이블(정답) 데이터의 양과 질** 에 직접적으로 의존합니다. 하지만 제조 현장에서 **정확한 레이블을 확보하는 것은 매우 비용이 큽니다** :
# MAGIC
# MAGIC LG Innotek 사례:
# MAGIC - **설비 고장 레이블** : 설비를 멈추고 전문 기술자가 분해 점검해야 확인 가능 (생산 손실 + 인건비)
# MAGIC - **제품 불량 레이블** : 비파괴 검사(X-ray, CT) 또는 파괴 검사(단면 분석) 필요 (장비비 + 시간)
# MAGIC - **이미지 결함 레이블** : 숙련된 검사원이 픽셀 단위로 결함 위치를 표시해야 함 (건당 수 분 소요)
# MAGIC
# MAGIC 만약 10,000건의 데이터를 모두 레이블링하는 데 **1건당 10분** 이 걸린다면, 총 **1,667시간(약 70일)** 이 필요합니다. 현실적으로 불가능합니다.
# MAGIC
# MAGIC **Active Learning** 은 이 문제를 해결합니다. 모델이 **"이 데이터는 정상인지 고장인지 판단이 어렵습니다. 전문가의 확인이 필요합니다"** 라고 요청하는 방식으로, **가장 정보가 많은 소수의 샘플만 레이블링** 하여 동등한 성능을 달성합니다.
# MAGIC
# MAGIC > **연구 결과** : Active Learning으로 전체 데이터의 **10~20%만 레이블링** 해도 전체 레이블링과 비슷한 모델 성능을 얻을 수 있습니다 (Settles, 2009).
# MAGIC
# MAGIC ```
# MAGIC 모델의 예측 확률:
# MAGIC   샘플 A: 0.95 (거의 확실히 정상)  → 레이블링 불필요
# MAGIC   샘플 B: 0.02 (거의 확실히 고장)  → 레이블링 불필요
# MAGIC   샘플 C: 0.48 (정상? 고장? 모름)  → 이 샘플을 레이블링! ★
# MAGIC   샘플 D: 0.52 (정상? 고장? 모름)  → 이 샘플을 레이블링! ★
# MAGIC
# MAGIC 불확실한 샘플을 레이블링하면 모델이 가장 많이 배움
# MAGIC ```

# COMMAND ----------

# DBTITLE 1,실습: Active Learning 불확실성 기반 샘플 선택
print("=== Active Learning: 불확실성 기반 샘플 선택 ===\n")

# 모델의 예측 확률로 불확실성 측정
probas = model_full.predict(xgb.DMatrix(full_df[feature_columns]))
uncertainty = np.abs(probas - 0.5)  # 0.5에 가까울수록 불확실

# 500건만 레이블링할 수 있다면?
n_query = 500

# 방법 1: Active Learning (가장 불확실한 500건)
active_idx = np.argsort(uncertainty)[:n_query]

# 방법 2: Random Sampling (랜덤 500건)
random_idx = np.random.choice(len(full_df), n_query, replace=False)

# 각 방법으로 학습하여 비교
for name, idx in [("Active Learning", active_idx), ("Random Sampling", random_idx)]:
    X_sel = full_df.iloc[idx][feature_columns]
    Y_sel = full_df.iloc[idx][label_col]
    dt = xgb.DMatrix(X_sel, label=Y_sel)
    m = xgb.train(params, dt, num_boost_round=150)
    pred = (m.predict(dtest) > 0.5).astype(int)
    f1 = f1_score(Y_test, pred)
    print(f"  {name:20s}: {n_query}건 학습 → F1 = {f1:.4f}")

print(f"  Full Training:       {len(full_df)}건 학습 → F1 = {f1_full:.4f}")
print(f"\n결론: Active Learning으로 {n_query}건만 레이블링해도")
print(f"  Random {n_query}건보다 더 좋은 모델을 얻을 수 있습니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 11: Warm-start vs Cold-start
# MAGIC
# MAGIC ## "기존 모델에서 출발할 것인가, 처음부터 학습할 것인가?"
# MAGIC
# MAGIC 재학습 시 가장 먼저 결정해야 할 것: **기존 모델의 학습 결과를 활용할 것인가, 버릴 것인가?**
# MAGIC 이 결정은 드리프트의 종류에 따라 달라집니다.
# MAGIC
# MAGIC | 방법 | 설명 | 장점 | 단점 | LG Innotek 적용 시나리오 |
# MAGIC |------|------|------|------|----------------------|
# MAGIC | **Cold-start** | 모델을 처음부터 새로 학습 | 오래된 패턴 완전 제거 | 시간/비용 큼 | 공정 레시피 변경, 설비 대체(Concept Drift) |
# MAGIC | **Warm-start** | 기존 모델을 시작점으로 추가 학습 | 빠름, 기존 지식 보존 | 오래된 패턴 잔존 | 계절 변화, 원자재 미세 변경(Data Drift) |
# MAGIC
# MAGIC Cold-start:                     Warm-start:
# MAGIC ```
# MAGIC ```
# MAGIC +--------+                      +--------+
# MAGIC | 랜덤   | → 학습 (오래 걸림)    | 기존   | → 추가 학습 (빠름)
# MAGIC | 초기화 |                      | 모델   |
# MAGIC +--------+                      +--------+
# MAGIC ```
# MAGIC
# MAGIC 결정 기준:
# MAGIC   IF Concept Drift 의심 (PSI > 0.5 또는 F1 급락)
# MAGIC     → Cold-start (처음부터)
# MAGIC   ELIF Data Drift만 (PSI 0.1~0.5)
# MAGIC     → Warm-start (기존 모델 + 새 데이터)
# MAGIC   ELIF 변화 없음 (PSI < 0.1)
# MAGIC     → 재학습 불필요
# MAGIC ```
# MAGIC ```

# COMMAND ----------

# DBTITLE 1,실습: Warm-start vs Cold-start 비교
import time

print("=== Warm-start vs Cold-start 비교 ===\n")

# Cold-start: 처음부터 학습
start = time.time()
dtrain = xgb.DMatrix(X_train, label=Y_train)
model_cold = xgb.train(params, dtrain, num_boost_round=200)
cold_time = time.time() - start
f1_cold = f1_score(Y_test, (model_cold.predict(dtest) > 0.5).astype(int))

# Warm-start: 기존 모델에서 추가 학습
start = time.time()
# 새 데이터만 사용 (최근 1/3)
X_new = full_df.iloc[2*len(full_df)//3:][feature_columns]
Y_new = full_df.iloc[2*len(full_df)//3:][label_col]
dtrain_new = xgb.DMatrix(X_new, label=Y_new)
model_warm = xgb.train(params, dtrain_new, num_boost_round=50, xgb_model=model_cold)
warm_time = time.time() - start
f1_warm = f1_score(Y_test, (model_warm.predict(dtest) > 0.5).astype(int))

print(f"  {'방법':>12s} | {'학습 시간':>10s} | {'F1':>8s} | 설명")
print(f"  {'-'*55}")
print(f"  {'Cold-start':>12s} | {cold_time:>8.2f}초 | {f1_cold:>8.4f} | 전체 데이터 처음부터")
print(f"  {'Warm-start':>12s} | {warm_time:>8.2f}초 | {f1_warm:>8.4f} | 기존 모델 + 새 데이터")
print(f"  {'속도 차이':>12s} | {cold_time/max(warm_time,0.001):>7.1f}배 | {f1_warm-f1_cold:>+8.4f} |")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # Part 12: 운영 환경 종합 아키텍처
# MAGIC
# MAGIC ## 모든 기법을 어떻게 조합하는가? — LG Innotek 운영 환경 권장 구성
# MAGIC
# MAGIC Part 1~11에서 학습한 모든 기법을 **하나의 통합 아키텍처** 로 조합합니다.
# MAGIC 이 아키텍처는 Databricks 플랫폼의 Workflow, Data Quality Monitoring, Delta Lake, Unity Catalog, MLflow를 **유기적으로 연결** 하여 구현됩니다.
# MAGIC
# MAGIC ```
# MAGIC ```
# MAGIC ```
# MAGIC +----------------------------------------------------------------+
# MAGIC |                    종합 재학습 아키텍처                        |
# MAGIC +----------------------------------------------------------------+
# MAGIC |                                                                |
# MAGIC |  [센서 데이터]                                                 |
# MAGIC |       |                                                        |
# MAGIC |       +-→ [Delta Lake 저장]                                    |
# MAGIC |       |       |                                                |
# MAGIC |       |       +-→ [Data Quality Monitoring]                       |
# MAGIC |       |       |       |                                        |
# MAGIC |       |       |   PSI > 0.2?  --Yes--→ [재학습 트리거]         |
# MAGIC |       |       |       |                     |                  |
# MAGIC |       |       |      No                     v                  |
# MAGIC |       |       |       |              [Contextual Bandit]       |
# MAGIC |       |       |       v              전략 자동 선택            |
# MAGIC |       |       |  [스케줄 체크]              |                  |
# MAGIC |       |       |  주 1회 도래?  -Yes-→  +----+----+            |
# MAGIC |       |       |       |                | Strategy |            |
# MAGIC |       |       |      No                +----------+            |
# MAGIC |       |       |       v                | Full     |            |
# MAGIC |       |       |  [현재 모델 유지]      | Incr.    |            |
# MAGIC |       |       |                        | Window   |            |
# MAGIC |       |       |                        +----+----+            |
# MAGIC |       |       |                             |                  |
# MAGIC |       |       |                             v                  |
# MAGIC |       |       |                   [모델 학습 + MLflow]         |
# MAGIC |       |       |                             |                  |
# MAGIC |       |       |                             v                  |
# MAGIC |       |       |                   [Champion 비교 검증]         |
# MAGIC |       |       |                        |         |             |
# MAGIC |       |       |                     통과        실패           |
# MAGIC |       |       |                        |         |             |
# MAGIC |       |       |                        v         v             |
# MAGIC |       |       |                   [Champion   [기존 모델       |
# MAGIC |       |       |                    교체]       유지]           |
# MAGIC |       |       |                                                |
# MAGIC |       +-→ [배치 추론] (일 4회)                                 |
# MAGIC |               |                                                |
# MAGIC |               +-→ [추론 결과 저장] → [대시보드]                |
# MAGIC |                                                                |
# MAGIC +----------------------------------------------------------------+
# MAGIC ```
# MAGIC
# MAGIC ## 전략별 적용 가이드
# MAGIC
# MAGIC | 상황 | 권장 전략 | Databricks 구현 | LG Innotek 적용 예시 |
# MAGIC |------|----------|----------------|-------------------|
# MAGIC | 정기 재학습 (주 1회) | Sliding Window Full Retrain | Workflow 스케줄 | 양산 라인 예지보전 모델 |
# MAGIC | 급격한 드리프트 | Cold-start Full Retrain | Monitoring Alert → Workflow 트리거 | 공정 레시피 대폭 변경 시 |
# MAGIC | 점진적 드리프트 | Warm-start Incremental | 이벤트 기반 Workflow | 계절 변화에 따른 미세 조정 |
# MAGIC | 실시간 적응 필요 | Online Learning (보조) | Structured Streaming + River | 실시간 설비 상태 모니터링 |
# MAGIC | 레이블 부족 | Active Learning | Human-in-the-loop 파이프라인 | 신규 라인/제품 초기 데이터 수집 |
# MAGIC | 다중 라인/설비 | Continual (Replay) | Delta Lake 기반 Replay Buffer | 여러 카메라 모듈 라인 통합 모델 |
# MAGIC | 자동 전략 선택 | Contextual Bandit | MLOps Agent 통합 | 성숙한 MLOps 환경의 최종 목표 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## LG Innotek MLOps 도입 로드맵 (권장)
# MAGIC
# MAGIC ```
# MAGIC Phase 1 (1~2개월): 기초 구축
# MAGIC   - 스케줄 기반 Full Retrain (주 1회) + Champion/Challenger 비교
# MAGIC   - Databricks Workflow + MLflow + Unity Catalog
# MAGIC
# MAGIC Phase 2 (3~4개월): 모니터링 고도화
# MAGIC   - PSI 기반 드리프트 탐지 + 성능 기반 트리거 추가 (하이브리드)
# MAGIC   - Data Quality Monitoring 자동 대시보드
# MAGIC
# MAGIC Phase 3 (5~6개월): 효율화
# MAGIC   - Warm-start Incremental Learning (빠른 적응)
# MAGIC   - Active Learning (레이블링 비용 최소화)
# MAGIC   - Continual Learning (다중 라인 통합 모델)
# MAGIC
# MAGIC Phase 4 (6개월+): 자율 운영
# MAGIC   - Online Learning (실시간 보조 모델)
# MAGIC   - Contextual Bandit (자동 전략 선택)
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 핵심 요약
# MAGIC
# MAGIC | 기법 | 한 줄 요약 | 비용 | 정확도 | 도입 우선순위 |
# MAGIC |------|----------|------|--------|------------|
# MAGIC | **Full Retrain** | 전체 데이터로 처음부터 학습 | 높음 | 최고 | 1순위 (필수) |
# MAGIC | **Sliding Window** | 최근 N일 데이터만 사용 | 중간 | 높음 | 1순위 (필수) |
# MAGIC | **Warm-start** | 기존 모델에서 출발하여 추가 학습 | 낮음 | 양호 | 2순위 |
# MAGIC | **Incremental** | 기존 모델 + 새 데이터로 보강 | 낮음 | 양호 | 2순위 |
# MAGIC | **Continual (Replay)** | 과거 대표 샘플 + 새 데이터 | 중간 | 높음 | 3순위 |
# MAGIC | **Active Learning** | 불확실한 샘플만 레이블링 | 레이블 비용 최소 | 효율적 | 3순위 |
# MAGIC | **Online** | 데이터 1건씩 즉시 학습 | 매우 낮음 | 보통 | 4순위 (선택) |
# MAGIC | **RL (Bandit)** | AI가 전략을 자동 선택 | 자동화 | 적응적 | 4순위 (선택) |
# MAGIC
# MAGIC ### 최신 트렌드 (2024~2025)
# MAGIC
# MAGIC - **Federated Learning (연합 학습)** : 여러 공장/라인의 데이터를 중앙으로 모으지 않고, 각 현장에서 모델을 학습한 후 **모델 파라미터만 공유** 하여 통합. 데이터 보안과 프라이버시를 보장하면서 글로벌 모델 구축 가능
# MAGIC - **Continuous Learning Pipelines** : Databricks의 Delta Live Tables + Workflow를 결합하여 데이터 수집부터 모델 재학습까지 **완전 자동화된 파이프라인** 구축
# MAGIC - **LLMOps** : 대규모 언어 모델(LLM)의 Fine-tuning과 RAG(검색 증강 생성)에도 유사한 재학습 전략 적용
# MAGIC - **AI Agent 기반 MLOps** : AI Agent가 모니터링, 재학습, 배포를 자율적으로 관리하는 차세대 MLOps 아키텍처
# MAGIC
# MAGIC **다음 단계:** [04: 모델 등록]($./04_model_registration_uc) 또는 [03b: 멀티 알고리즘 비교]($./03b_multi_algorithm_comparison)

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Part 13: Level 2 자동 재학습 (Jobs 트리거)
# MAGIC
# MAGIC > **이 섹션은 Databricks Jobs에서 자동으로 실행됩니다.**
# MAGIC > 모니터링 노트북(08)에서 드리프트가 감지되면, Job 파이프라인이 이 노트북을 자동으로 호출합니다.
# MAGIC > 이것이 **Level 2 MLOps의 핵심** — 사람 개입 없는 자동 재학습입니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Level 2 자동 재학습 아키텍처
# MAGIC
# MAGIC [08 모니터링] → PSI > 0.2 감지 → taskValues("drift_detected"=True)
# MAGIC     ↓
# MAGIC [03d 재학습] → taskValues 수신 → full_retrain_pipeline() 자동 실행
# MAGIC     ↓
# MAGIC [05 검증] → Champion vs Challenger 자동 비교
# MAGIC     ↓
# MAGIC [06 추론] → 새 Champion으로 배치 예측 자동 실행
# MAGIC ```
# MAGIC
# MAGIC > **현업 팁** : 처음에는 드리프트 감지 시 Slack 알림만 보내고 사람이 확인 후 재학습하는 "반자동" 모드로 시작하세요.
# MAGIC > 3개월간 시스템을 신뢰할 수 있게 된 후 완전 자동(Level 2)으로 전환하는 것이 안전합니다.

# COMMAND ----------

# DBTITLE 1,Level 2: 드리프트 기반 자동 재학습
# --- Jobs 파이프라인에서 호출될 때 자동 실행 ---
try:
    # 모니터링 태스크에서 전달된 드리프트 정보 수신
    drift_detected = dbutils.jobs.taskValues.get(
        taskKey="model_monitoring",
        key="drift_detected",
        default=False
    )
    drift_features = dbutils.jobs.taskValues.get(
        taskKey="model_monitoring",
        key="drift_features",
        default="[]"
    )
    max_psi = dbutils.jobs.taskValues.get(
        taskKey="model_monitoring",
        key="max_psi",
        default=0.0
    )

    if drift_detected:
        print(f"🔴 드리프트 감지됨 — 자동 재학습을 시작합니다!")
        print(f"   감지 피처: {drift_features}")
        print(f"   최대 PSI: {max_psi:.3f}")
        print(f"   재학습 사유: auto_drift_detection")

        # 자동 재학습 실행
        result = full_retrain_pipeline(reason=f"auto_drift_psi_{max_psi:.2f}")

        # 결과를 다음 태스크(검증)에 전달
        dbutils.jobs.taskValues.set(key="retrain_completed", value=True)
        dbutils.jobs.taskValues.set(key="new_model_version", value=result.get("version", ""))

        print(f"\n✅ 재학습 완료!")
        print(f"   새 모델 버전: {result.get('version', 'N/A')}")
        print(f"   배포 여부: {'✅ Champion 승급' if result.get('deployed') else '❌ 기존 유지'}")
    else:
        print(f"🟢 드리프트 없음 — 재학습을 건너뜁니다.")
        dbutils.jobs.taskValues.set(key="retrain_completed", value=False)

except Exception as e:
    # 노트북 단독 실행 시 (Jobs 외부)
    print(f"ℹ️ 노트북 단독 실행 중입니다.")
    print(f"   Jobs 파이프라인에서 실행하면 드리프트 기반 자동 재학습이 동작합니다.")
    print(f"   수동 재학습을 하려면 위의 full_retrain_pipeline() 셀을 직접 실행하세요.")
