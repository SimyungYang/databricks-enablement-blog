# 04. 모델 등록 (Unity Catalog Model Registry)

> **전체 노트북 코드**: [04_model_registration_uc.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/04_model_registration_uc.py)


** 목적**: 최적 모델을 UC 모델 레지스트리에 등록하고, Alias를 통해 모델 생애 주기를 관리합니다.

** 사용 Databricks 기능**: `Unity Catalog Model Registry`, `Model Lineage`, `태그 기반 거버넌스`

---

## 1. 최적 모델 자동 검색

MLflow `search_runs` API로 val_f1_score 기준 최적 모델을 프로그래밍 방식으로 찾습니다.

```python
# 최적 모델 검색 (val_f1_score 기준 정렬)
best_run = mlflow.search_runs(
    experiment_ids=experiment_id,
    order_by=["metrics.val_f1_score DESC"],
    max_results=1,
    filter_string="status = 'FINISHED'"
)
run_id = best_run.iloc[0]['run_id']
print(f"최적 모델 Run: {run_id}, Val F1: {best_run.iloc[0]['metrics.val_f1_score']:.4f}")
```

## 2. Unity Catalog에 모델 등록

`mlflow.register_model()`로 모델을 UC에 등록합니다. ** 카탈로그.스키마.모델명**3-Level 네임스페이스로 관리됩니다.

```python
model_name = f"{catalog}.{db}.lgit_predictive_maintenance"

# UC 모델 레지스트리에 등록
model_details = mlflow.register_model(
    model_uri=f"runs:/{run_id}/xgboost_model",
    name=model_name
)
print(f"등록 완료 — 모델: {model_details.name}, 버전: {model_details.version}")
```

## 3. 모델 메타데이터 및 거버넌스

등록된 모델에 설명, 태그를 추가하여 거버넌스를 강화합니다.

```python
client = MlflowClient()

# 모델 설명 추가
client.update_registered_model(
    name=model_name,
    description="""LG Innotek 예지보전 모델. AI4I 2020 기반 XGBoost 분류기.
    입력: 설비 센서값 (온도, 회전속도, 토크, 공구 마모 등)
    출력: 고장 발생 확률 및 이진 분류 결과."""
)

# 버전별 성능 태그 추가
client.set_model_version_tag(name=model_name, version=model_details.version,
                              key="val_f1_score", value=f"{best_f1:.4f}")
```

## 4. Champion/Challenger 에일리어스 설정

에일리어스(Alias)는 모델의 생애 주기 단계를 나타냅니다. 배포 시 에일리어스를 참조하므로, ** 코드 변경 없이** 모델 교체가 가능합니다.

| 에일리어스 | 설명 |
|-----------|------|
| `Baseline` | 최초 등록 시 부여 |
| `Challenger` | 검증 대기 중인 후보 모델 |
| `Champion` | 현재 운영 중인 모델 |

```python
# Challenger 에일리어스 설정
client.set_registered_model_alias(
    name=model_name, alias="Challenger", version=model_details.version
)

# Champion이 없으면 바로 Champion으로도 설정
try:
    champion = client.get_model_version_by_alias(model_name, "Champion")
    print(f"기존 Champion 존재: v{champion.version}")
except:
    client.set_registered_model_alias(name=model_name, alias="Champion", version=model_details.version)
    print("첫 번째 모델 → Champion 설정 완료")
```

{% hint style="info" %}
Unity Catalog Explorer에서 모델의 버전, 에일리어스, ** 계보(Lineage)** 를 시각적으로 확인할 수 있습니다. 학습 데이터 테이블 → MLflow 실험 → 등록된 모델 간의 전체 추적이 자동으로 생성됩니다.
{% endhint %}

** 다음 단계**: [05. 챌린저 검증](05-challenger-validation.md)
