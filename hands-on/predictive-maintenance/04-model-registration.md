# 04. 모델 등록 (Unity Catalog Model Registry)

**목적**: 최적 모델을 UC 모델 레지스트리에 등록하고, Alias를 통해 생애 주기를 관리합니다.

**주요 개념**:
- `mlflow.search_runs()` 로 최적 모델 자동 검색
- `mlflow.register_model()` 로 UC 등록
- Challenger/Champion 에일리어스를 통한 안전한 배포

**핵심 코드**:

```python
# 최적 모델 검색 (val_f1_score 기준)
best_run = mlflow.search_runs(
    experiment_ids=experiment_id,
    order_by=["metrics.val_f1_score DESC"],
    max_results=1,
)

# Unity Catalog에 모델 등록
model_details = mlflow.register_model(
    model_uri=f"runs:/{run_id}/xgboost_model",
    name=f"{catalog}.{db}.lgit_predictive_maintenance"
)

# Challenger 에일리어스 설정
client.set_registered_model_alias(
    name=model_name, alias="Challenger", version=model_details.version
)
```

**사용 Databricks 기능**: Unity Catalog Model Registry, Model Lineage, 태그 기반 거버넌스
