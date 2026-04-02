# 03d. 재학습 전략 (Retraining Strategies)

> **전체 노트북 코드**: [03d\_retraining\_strategies.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/03d_retraining_strategies.py)

**목적**: ML 모델의 지속적 성능 유지를 위한 재학습 전략을 기초부터 최신 기법까지 체계적으로 다룹니다. 드리프트 탐지, Full Retraining, Incremental/Continual/Online Learning, 강화학습 기반 전략 자동 선택, Active Learning까지 **13개 Part** 로 구성됩니다.

**사용 Databricks 기능**: `MLflow Experiment Tracking`, `Unity Catalog Model Registry`, `Delta Lake Time Travel`, `Databricks Workflow`, `Data Quality Monitoring`, `Structured Streaming`

---

## Part 1: 재학습이 필요한 이유

ML 모델은 **학습 시점의 데이터 패턴** 을 기반으로 예측합니다. 하지만 제조 현장은 끊임없이 변하며, 이 변화를 " ** 드리프트(Drift)**"라고 부릅니다. 구글의 연구(2015, "Hidden Technical Debt in ML Systems")에 따르면, ML 시스템 운영 비용의 **90% 이상이 모델 배포 후 유지보수** 에 소요됩니다.

### 1.1 Data Drift (데이터 드리프트)

모델에 입력되는 데이터의 **통계적 분포 P(X)** 가 학습 시점과 달라지는 현상입니다.

- **계절 변화**: 공장 내부 온도/습도가 외기 온도에 영향받음
- **원자재 변경**: 새 공급사의 기판, 렌즈 등의 물리적 특성이 다름
- **설비 노후화**: 센서 교정 주기에 따라 측정값 범위가 점진적으로 이동(Sensor Drift)
- **생산 물량 변동**: 풀 가동 vs 부분 가동에 따라 설비 열적 특성이 달라짐

### 1.2 Concept Drift (개념 드리프트)

입력(X)과 출력(Y) 간의 **관계 자체 P(Y|X)** 가 변하는 현상으로, Data Drift보다 **더 심각** 합니다.

- **공정 레시피 업데이트**: DOE 결과를 반영하여 공정 조건 최적화 → 이전 고장 패턴 무효화
- **설비 부품 교체**: 핵심 부품(모터, 베어링, 히터) 교체 후 고장 메커니즘 자체가 변화
- **품질 기준 변경**: 고객 요구사항 강화로 이전에 정상이었던 것이 불량으로 재분류

{% hint style="warning" %}
Data Drift는 입력 데이터 모니터링으로 감지할 수 있지만, Concept Drift는 **데이터 분포는 같아 보이는데 모델 예측이 틀리기 시작** 하는 현상이므로 성능 모니터링(F1, AUC 추적)이 필수입니다.
{% endhint %}

### 1.3 드리프트 시뮬레이션 실습

노트북에서는 테스트 데이터에 점진적 온도 오프셋을 추가하여 Data Drift에 따른 성능 저하를 실측합니다.

```python
drift_levels = [0, 0.5, 1.0, 2.0, 3.0, 5.0]

for drift in drift_levels:
    X_drifted = X_test.copy()
    X_drifted["air_temperature_k"] += drift
    X_drifted["process_temperature_k"] += drift * 0.8
    X_drifted["temp_diff"] = X_drifted["process_temperature_k"] - X_drifted["air_temperature_k"]

    dtest = xgb.DMatrix(X_drifted)
    pred = (model_original.predict(dtest) > 0.5).astype(int)
    f1 = f1_score(Y_test, pred)
```

{% hint style="info" %}
제조 현장에서 ML 모델의 평균 유효 수명은 **1~3개월** 입니다. 공정 변경이 빈번한 라인에서는 **매주 재학습** 이 권장됩니다.
{% endhint %}

---

## Part 2: 재학습 트리거 전략

"언제 재학습을 해야 하는가?"는 MLOps에서 가장 어려운 질문입니다. 너무 자주 하면 불필요한 비용이, 너무 드물게 하면 성능 저하를 방치하게 됩니다.

### 전략 1: 스케줄 기반 (Time-based)

매주 월요일 새벽 2시에 재학습 (Databricks Workflow 스케줄 트리거). 구현이 가장 쉽고 운영 예측이 가능합니다. MLOps 초기 도입 단계에서 **가장 좋은 시작점** 입니다.

### 전략 2: 성능 기반 (Performance-based)

모델의 F1 Score가 0.7 아래로 떨어지면 재학습합니다. 진짜 필요할 때만 재학습하므로 비용 효율적이지만, **실제 레이블(정답)이 필요** 합니다.

### 전략 3: 드리프트 기반 (Drift-based)

입력 데이터의 PSI(Population Stability Index)가 0.2를 넘으면 재학습합니다. **레이블 없이도** 센서 데이터만으로 탐지 가능하지만, Concept Drift는 감지하지 못합니다.

### 전략 4: 하이브리드 (권장)

여러 조건을 조합하여 우선순위별로 판단합니다.

```
IF (PSI > 0.2)           → 즉시 재학습 (긴급) — 데이터 분포 급변
ELIF (F1 < 0.7)          → 즉시 재학습 (긴급) — 성능 임계치 이탈
ELIF (마지막 학습 > 7일)  → 정기 재학습 (일반) — 안전망
ELIF (새 데이터 > 5000건) → 추가 학습 고려 (낮음) — Incremental Learning
ELSE                      → 현재 모델 유지
```

{% hint style="info" %}
MLOps 초기에는 **전략 1(스케줄 기반, 주 1회)** 로 시작하고, Data Quality Monitoring 구축 후 **전략 4(하이브리드)** 로 고도화하는 단계적 접근을 권장합니다.
{% endhint %}

### PSI (Population Stability Index) — 드리프트 정량 탐지

PSI는 금융업계에서 개발되어 ML 전반으로 확산된 데이터 분포 변화 수치화 지표입니다. Databricks Data Quality Monitoring에서도 핵심 드리프트 지표로 사용됩니다.

| PSI 범위 | 해석 | 조치 |
|----------|------|------|
| < 0.1 | 변화 없음 (안정) | 재학습 불필요 |
| 0.1 ~ 0.2 | 약간의 변화 (주의) | 모니터링 빈도 증가, 원인 조사 |
| 0.2 ~ 0.5 | 유의미한 변화 (경고) | 재학습 권장 |
| > 0.5 | 심각한 변화 (위험) | 즉시 재학습 + 모델 예측 중단 검토 |

```python
def calculate_psi(expected, actual, bins=10):
    breakpoints = np.linspace(
        min(expected.min(), actual.min()),
        max(expected.max(), actual.max()),
        bins + 1
    )
    expected_counts = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_counts = np.histogram(actual, bins=breakpoints)[0] / len(actual)
    expected_counts = np.maximum(expected_counts, 0.001)
    actual_counts = np.maximum(actual_counts, 0.001)
    psi = np.sum((actual_counts - expected_counts) * np.log(actual_counts / expected_counts))
    return psi
```

---

## Part 3: Full Retraining 실전 구현

Full Retraining은 가장 기본적이면서 **가장 확실한** 재학습 방법입니다. 전체 데이터로 모델을 **처음부터 다시 학습** 합니다. Databricks Workflow의 하나의 Task로 등록하여 스케줄 또는 이벤트 트리거로 자동 실행합니다.

### 재학습 파이프라인 전체 흐름

| Step | 내용 | 상세 |
|------|------|------|
| **Step 1** | 학습 데이터 준비 | Delta Lake에서 최신 데이터 로드, Sliding Window로 기간 선택 |
| **Step 2** | 새 모델 학습 | 기존과 동일한 알고리즘 + 하이퍼파라미터, MLflow에 실험 기록 |
| **Step 3** | Champion 비교 검증 | 기존 Champion 모델과 성능 비교 |
| **Step 4** | 배포 결정 | 새 모델 > 기존 모델이면 Champion 교체, 아니면 기존 유지 |

```python
def full_retrain_pipeline(reason="scheduled"):
    # Step 1: 학습 데이터 준비 (Sliding Window)
    train_data = spark.table("lgit_pm_training").filter("split='train'") \
                      .select(*feature_columns, label_col).toPandas()

    # Step 2: MLflow 실험에 기록하면서 모델 학습
    with mlflow.start_run(run_name=f"retrain_{reason}_{datetime.now().strftime('%Y%m%d')}") as run:
        mlflow.log_param("retrain_reason", reason)
        mlflow.log_param("training_data_size", len(X_tr))

        new_model = xgb.train(retrain_params, dtrain, num_boost_round=200)

        # 성능 평가
        new_f1 = f1_score(Y_te, pred)
        new_auc = roc_auc_score(Y_te, proba)
        mlflow.log_metrics({"test_f1_score": new_f1, "test_auc": new_auc})
        mlflow.xgboost.log_model(new_model, "xgboost_model", signature=signature)

    # Step 3: Champion 비교
    champion_info = client.get_model_version_by_alias(model_name, "Champion")
    champion_f1 = mlflow.get_run(champion_info.run_id).data.metrics.get("test_f1_score", 0)

    # Step 4: 배포 결정
    if new_f1 >= champion_f1:
        model_details = mlflow.register_model(
            f"runs:/{run.info.run_id}/xgboost_model", model_name
        )
        client.set_registered_model_alias(
            name=model_name, alias="Champion", version=model_details.version
        )
```

---

## Part 4: Delta Lake 기반 학습 데이터 관리

재학습의 성패는 **어떤 데이터를 사용하느냐** 에 달려 있습니다. Delta Lake의 고유 기능(Time Travel, 버전 관리)을 활용하면 학습 데이터를 체계적이고 재현 가능하게 관리할 수 있습니다.

### 4.1 Sliding Window (슬라이딩 윈도우)

**최근 N일의 데이터만** 사용하여 학습합니다. 오래된 데이터는 현재 패턴과 다를 수 있으므로 자연스럽게 제외합니다.

### 4.2 Delta Lake Time Travel

특정 시점/버전의 데이터를 정확히 조회하여 **학습 재현성과 감사(Audit) 추적** 을 보장합니다.

```sql
-- 특정 버전의 데이터 조회
SELECT * FROM lgit_pm_training VERSION AS OF 5

-- 특정 시점의 데이터 조회
SELECT * FROM lgit_pm_training TIMESTAMP AS OF '2024-01-01'

-- 최근 30일 데이터만 조회 (Sliding Window)
SELECT * FROM lgit_pm_inference_results
WHERE inference_timestamp >= current_date() - INTERVAL 30 DAYS
```

{% hint style="info" %}
다른 데이터 플랫폼에서는 DVC 같은 별도 도구가 필요한 데이터 버전 관리를 Delta Lake에서는 **네이티브 기능** 으로 제공합니다. 최적 윈도우 크기는 **최근 60~90일** 로 시작하여 성능을 보며 조정하는 것을 권장합니다.
{% endhint %}

---

## Part 5: 모델 버전 관리 & 롤백

재학습된 새 모델이 항상 더 좋다는 보장은 없습니다. **즉시 이전 모델로 되돌릴 수 있는 능력** 은 운영 안정성의 핵심입니다.

### Unity Catalog 에일리어스 기반 롤백

코드를 변경하지 않고 **에일리어스만 변경** 하면 즉시 롤백이 가능합니다. 배치 추론 코드는 항상 `models:/model_name@Champion` 참조를 사용합니다.

```python
def rollback_model(model_name, target_version=None):
    current = client.get_model_version_by_alias(model_name, "Champion")
    current_version = int(current.version)

    if target_version is None:
        target_version = max(1, current_version - 1)

    # 현재 Champion에 태그 추가
    client.set_model_version_tag(
        name=model_name, version=str(current_version),
        key="rolled_back", value="true"
    )

    # 에일리어스 변경 → 즉시 롤백 완료
    client.set_registered_model_alias(
        name=model_name, alias="Champion", version=target_version
    )
```

{% hint style="warning" %}
롤백이 필요한 상황: (1) 새 모델의 운영 성능이 검증 성능보다 현저히 낮은 경우, (2) 특정 데이터 구간에서 심각한 오류를 보이는 경우, (3) 규제/컴플라이언스 이슈로 이전 모델 복구가 필요한 경우.
{% endhint %}

---

## Part 6: Incremental Learning (점진적 학습)

Full Retraining은 확실하지만, 데이터가 수억 건으로 커지면 학습 시간과 비용이 과도해집니다. **Incremental Learning** 은 기존 모델을 폐기하지 않고 **새 데이터만으로 모델을 보강** 합니다.

### XGBoost의 Warm-start Incremental Learning

XGBoost는 트리를 순차적으로 추가하는 방식이므로, 기존 트리를 유지하면서 **새로운 트리만 추가** 할 수 있습니다.

```python
# Batch 1: 초기 모델 학습 (100 trees)
model_inc = xgb.train(params, dtrain1, num_boost_round=100)

# Batch 2: 기존 모델에 추가 학습 (50 trees 추가)
# 핵심: xgb_model 파라미터로 기존 모델 전달
model_inc = xgb.train(params, dtrain2, num_boost_round=50, xgb_model=model_inc)

# Batch 3: 계속 추가 학습
model_inc = xgb.train(params, dtrain3, num_boost_round=50, xgb_model=model_inc)
```

| 비교 항목 | Full Retraining | Incremental Learning |
|----------|----------------|---------------------|
| 데이터 | 전체 (예: 1년치 100만건) | 새 데이터만 (예: 1주일치) |
| 시간 | 오래 걸림 (예: 2시간) | 빠름 (예: 10분) |
| 비용 | 높음 | 낮음 |
| 정확도 | 최고 | 양호 |
| 사용 시점 | 데이터 변화가 점진적일 때, 빈번한 업데이트가 필요할 때 | 학습 시간/비용 절감이 필요할 때 |

---

## Part 7: Continual Learning (연속 학습)

Incremental Learning의 심각한 부작용이 있습니다: **Catastrophic Forgetting(파국적 망각)**. 새 데이터만으로 모델을 학습하면 이전에 학습한 패턴을 잊어버릴 수 있습니다.

### 해결책: Experience Replay (경험 재생)

이전 데이터의 **대표 샘플을 Replay Buffer에 보관** 하고, 새 데이터와 함께 학습합니다.

```python
class ReplayBuffer:
    def __init__(self, max_size=2000):
        self.buffer = []
        self.max_size = max_size

    def add(self, X, Y):
        data = list(zip(X.values.tolist(), Y.values.tolist()))
        self.buffer.extend(data)
        if len(self.buffer) > self.max_size:
            self.buffer = random.sample(self.buffer, self.max_size)

    def get_replay_data(self, n_samples=500):
        samples = random.sample(self.buffer, min(n_samples, len(self.buffer)))
        X = pd.DataFrame([s[0] for s in samples], columns=feature_columns)
        Y = pd.Series([s[1] for s in samples])
        return X, Y


# Continual Learning: 새 데이터 + 리플레이 데이터 결합
replay = ReplayBuffer(max_size=2000)

for batch in batches:
    X_rep, Y_rep = replay.get_replay_data(500)
    X_combined = pd.concat([X_batch, X_rep], ignore_index=True)
    Y_combined = pd.concat([Y_batch, Y_rep], ignore_index=True)

    model_cl = xgb.train(params, xgb.DMatrix(X_combined, label=Y_combined), num_boost_round=150)
    replay.add(X_batch, Y_batch)
```

{% hint style="info" %}
**다중 생산 라인, 다중 제품** 을 하나의 모델로 관리하는 환경에서는 Experience Replay가 특히 중요합니다. 실제 운영에서는 Replay Buffer를 **Delta Lake 테이블** 로 관리합니다.
{% endhint %}

---

## Part 8: Online Learning (River 라이브러리)

지금까지의 모든 기법(Full Retrain, Incremental, Continual)은 **배치(Batch) 방식** 입니다. **Online Learning** 은 데이터가 들어올 때마다 즉시 모델을 업데이트하여 **실시간으로 적응** 합니다.

### River 라이브러리

Python의 **River**(creme + scikit-multiflow 통합)는 Online Learning 전용 프레임워크입니다. **Hoeffding Adaptive Tree** 는 드리프트를 자동 감지하고 트리 구조를 동적으로 변경합니다.

```python
from river import tree, metrics, preprocessing, compose

model_online = compose.Pipeline(
    preprocessing.StandardScaler(),         # 실시간 표준화
    tree.HoeffdingAdaptiveTreeClassifier(seed=42)
)
metric = metrics.F1()

for _, row in data.iterrows():
    x = {col: row[col] for col in feature_columns}
    y = int(row[label_col])

    y_pred = model_online.predict_one(x)        # 1. 현재 모델로 예측
    if y_pred is not None:
        metric.update(y, y_pred)                 # 2. 메트릭 업데이트
    model_online.learn_one(x, y)                 # 3. 이 한 건으로 모델 업데이트
```

{% hint style="warning" %}
Online Learning은 단독 사용보다 " ** 보조 모델**"로 활용하는 것을 권장합니다. 주력 모델(XGBoost Batch)은 주 1회 재학습하고, Online 모델은 실시간 트렌드를 파악하는 **조기 경보 시스템** 역할을 합니다. Databricks Structured Streaming과 결합하면 실시간 파이프라인 구축이 가능합니다.
{% endhint %}

---

## Part 9: RL 기반 재학습 전략 자동 선택 (Contextual Bandit)

" ** 지금 이 상황에서 어떤 재학습 전략을 써야 하는가?**" 를 AI가 자동으로 학습하게 합니다. Contextual Bandit은 강화학습(RL)의 간소화 버전으로, **현재 상황(Context)을 보고 최적의 행동(Action)을 선택** 하는 기법입니다.

### Thompson Sampling 기반 전략 선택기

```python
class RetrainingBandit:
    def __init__(self):
        self.actions = ["no_action", "incremental", "sliding_window", "full_retrain"]
        self.alpha = {a: 1.0 for a in self.actions}  # Beta 분포 파라미터
        self.beta_ = {a: 1.0 for a in self.actions}

    def select_action(self, context):
        scores = {}
        drift = context.get("drift_level", 0)
        for action in self.actions:
            base_score = np.random.beta(self.alpha[action], self.beta_[action])
            # 컨텍스트 기반 보정
            if action == "full_retrain" and drift > 0.2:
                base_score += 0.3
            elif action == "incremental" and 0.05 < drift <= 0.2:
                base_score += 0.2
            elif action == "no_action" and drift < 0.05:
                base_score += 0.3
            scores[action] = base_score
        return max(scores, key=scores.get), scores

    def update(self, action, reward):
        if reward > 0:
            self.alpha[action] += reward
        else:
            self.beta_[action] += abs(reward)
```

{% hint style="info" %}
Contextual Bandit은 MLOps 자동화의 **최종 단계** 에 해당하며, 현재 최신 연구 분야입니다. 숙련된 공정 엔지니어의 **경험 기반 의사결정** 을 AI가 학습하는 것으로 이해할 수 있습니다.
{% endhint %}

---

## Part 10: Active Learning (라벨링 비용 최소화)

ML 모델의 성능은 레이블 데이터의 양과 질에 의존합니다. 하지만 제조 현장에서 정확한 레이블 확보는 매우 비용이 큽니다 (설비 분해 점검, 비파괴 검사 등). **Active Learning** 은 모델이 " ** 판단이 어려운 샘플**"을 선별하여 전문가에게 레이블링을 요청하는 방식으로, **전체의 10~20%만 레이블링** 해도 동등한 성능을 달성합니다.

### 불확실성 기반 샘플 선택 (Uncertainty Sampling)

```python
# 모델의 예측 확률로 불확실성 측정
probas = model_full.predict(xgb.DMatrix(full_df[feature_columns]))
uncertainty = np.abs(probas - 0.5)  # 0.5에 가까울수록 불확실

# 가장 불확실한 500건을 우선 레이블링
n_query = 500
active_idx = np.argsort(uncertainty)[:n_query]

# Active Learning으로 선택한 500건으로 학습
X_sel = full_df.iloc[active_idx][feature_columns]
Y_sel = full_df.iloc[active_idx][label_col]
model_al = xgb.train(params, xgb.DMatrix(X_sel, label=Y_sel), num_boost_round=150)
```

| 방법 | 학습 데이터 | 레이블링 비용 | 성능 |
|------|-----------|-------------|------|
| Active Learning | 불확실한 500건 | 최소 | Random 대비 우수 |
| Random Sampling | 랜덤 500건 | 최소 | Active 대비 열등 |
| Full Training | 전체 데이터 | 최대 | 최고 |

---

## Part 11: Warm-start vs Cold-start

재학습 시 가장 먼저 결정해야 할 것: **기존 모델의 학습 결과를 활용할 것인가, 버릴 것인가?**

| 방법 | 설명 | 장점 | 단점 | 적용 시나리오 |
|------|------|------|------|------------|
| **Cold-start** | 모델을 처음부터 새로 학습 | 오래된 패턴 완전 제거 | 시간/비용 큼 | Concept Drift (공정 레시피 변경, 설비 대체) |
| **Warm-start** | 기존 모델을 시작점으로 추가 학습 | 빠름, 기존 지식 보존 | 오래된 패턴 잔존 | Data Drift (계절 변화, 원자재 미세 변경) |

### 결정 기준

```
IF Concept Drift 의심 (PSI > 0.5 또는 F1 급락)
  → Cold-start (처음부터)
ELIF Data Drift만 (PSI 0.1~0.5)
  → Warm-start (기존 모델 + 새 데이터)
ELIF 변화 없음 (PSI < 0.1)
  → 재학습 불필요
```

```python
# Cold-start: 전체 데이터로 처음부터
model_cold = xgb.train(params, dtrain, num_boost_round=200)

# Warm-start: 기존 모델에서 새 데이터로 추가 학습 (훨씬 빠름)
model_warm = xgb.train(params, dtrain_new, num_boost_round=50, xgb_model=model_cold)
```

---

## Part 12: 프로덕션 아키텍처

Part 1~11의 모든 기법을 **하나의 통합 아키텍처** 로 조합합니다. Databricks의 Workflow, Data Quality Monitoring, Delta Lake, Unity Catalog, MLflow를 유기적으로 연결합니다.

### 전략별 적용 가이드

| 상황 | 권장 전략 | Databricks 구현 | 적용 예시 |
|------|----------|----------------|----------|
| 정기 재학습 (주 1회) | Sliding Window Full Retrain | Workflow 스케줄 | 양산 라인 예지보전 모델 |
| 급격한 드리프트 | Cold-start Full Retrain | Monitoring Alert → Workflow 트리거 | 공정 레시피 대폭 변경 |
| 점진적 드리프트 | Warm-start Incremental | 이벤트 기반 Workflow | 계절 변화 미세 조정 |
| 실시간 적응 | Online Learning (보조) | Structured Streaming + River | 실시간 설비 상태 모니터링 |
| 레이블 부족 | Active Learning | Human-in-the-loop 파이프라인 | 신규 라인/제품 초기 데이터 수집 |
| 다중 라인/설비 | Continual (Replay) | Delta Lake 기반 Replay Buffer | 여러 모듈 라인 통합 모델 |
| 자동 전략 선택 | Contextual Bandit | MLOps Agent 통합 | 성숙한 MLOps 환경의 최종 목표 |

### MLOps 도입 로드맵

| Phase | 기간 | 내용 |
|-------|------|------|
| **Phase 1** | 1~2개월 | 스케줄 기반 Full Retrain (주 1회) + Champion/Challenger 비교 |
| **Phase 2** | 3~4개월 | PSI 기반 드리프트 탐지 + 성능 기반 트리거 (하이브리드) |
| **Phase 3** | 5~6개월 | Warm-start Incremental + Active Learning + Continual Learning |
| **Phase 4** | 6개월+ | Online Learning (보조) + Contextual Bandit (자동 전략 선택) |

### 핵심 요약

| 기법 | 한 줄 요약 | 비용 | 정확도 | 도입 우선순위 |
|------|----------|------|--------|------------|
| **Full Retrain** | 전체 데이터로 처음부터 학습 | 높음 | 최고 | 1순위 (필수) |
| **Sliding Window** | 최근 N일 데이터만 사용 | 중간 | 높음 | 1순위 (필수) |
| **Warm-start** | 기존 모델에서 출발하여 추가 학습 | 낮음 | 양호 | 2순위 |
| **Incremental** | 기존 모델 + 새 데이터로 보강 | 낮음 | 양호 | 2순위 |
| **Continual (Replay)** | 과거 대표 샘플 + 새 데이터 | 중간 | 높음 | 3순위 |
| **Active Learning** | 불확실한 샘플만 레이블링 | 레이블 비용 최소 | 효율적 | 3순위 |
| **Online** | 데이터 1건씩 즉시 학습 | 매우 낮음 | 보통 | 4순위 (선택) |
| **RL (Bandit)** | AI가 전략을 자동 선택 | 자동화 | 적응적 | 4순위 (선택) |

{% hint style="info" %}
**최신 트렌드 (2024~2025)**: Federated Learning(연합 학습), Delta Live Tables + Workflow 기반 Continuous Learning Pipelines, LLMOps(LLM Fine-tuning/RAG 재학습), AI Agent 기반 자율 MLOps 아키텍처가 주목받고 있습니다.
{% endhint %}

---

## Part 13: Level 2 자동 재학습 (Jobs trigger with taskValues)

Databricks Jobs에서 **모니터링 노트북(08)이 드리프트를 감지하면, taskValues를 통해 이 노트북을 자동 호출** 합니다. 사람 개입 없는 완전 자동 재학습 — 이것이 **Level 2 MLOps의 핵심** 입니다.

### Level 2 자동 재학습 아키텍처

| 단계 | 노트북 | 동작 |
|------|--------|------|
| 1 | 08 모니터링 | PSI > 0.2 감지 → `taskValues("drift_detected"=True)` |
| 2 | 03d 재학습 | taskValues 수신 → `full_retrain_pipeline()` 자동 실행 |
| 3 | 05 검증 | Champion vs Challenger 자동 비교 |
| 4 | 06 추론 | 새 Champion으로 배치 예측 자동 실행 |

```python
# Jobs 파이프라인에서 호출될 때 자동 실행
drift_detected = dbutils.jobs.taskValues.get(
    taskKey="model_monitoring",
    key="drift_detected",
    default=False
)
max_psi = dbutils.jobs.taskValues.get(
    taskKey="model_monitoring",
    key="max_psi",
    default=0.0
)

if drift_detected:
    # 자동 재학습 실행
    result = full_retrain_pipeline(reason=f"auto_drift_psi_{max_psi:.2f}")

    # 결과를 다음 태스크(검증)에 전달
    dbutils.jobs.taskValues.set(key="retrain_completed", value=True)
    dbutils.jobs.taskValues.set(key="new_model_version", value=result.get("version", ""))
```

{% hint style="warning" %}
처음에는 드리프트 감지 시 **Slack 알림만 보내고 사람이 확인 후 재학습** 하는 "반자동" 모드로 시작하세요. 3개월간 시스템을 신뢰할 수 있게 된 후 완전 자동(Level 2)으로 전환하는 것이 안전합니다.
{% endhint %}

---

**다음 단계**: [04. 모델 등록](04-model-registration.md)
