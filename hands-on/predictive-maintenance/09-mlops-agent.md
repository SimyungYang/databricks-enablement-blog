# 09. MLOps Agent

> **전체 노트북 코드**: [09_mlops_agent.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/09_mlops_agent.py)


**목적**: AI Agent가 Trigger에 따라 MLOps Tool을 자동 호출하여 학습/예측/모니터링을 오케스트레이션합니다.

**사용 Databricks 기능**: `AI Agent (ChatAgent)`, `UC Functions as Tools`, `Model Serving`, `MLflow Tracing`

---

## AI Agent(에이전트)란 무엇인가?

**AI Agent** 란 주어진 목표를 달성하기 위해 **스스로 상황을 관찰(Observe)하고, 판단(Decide)하고, 행동(Act)하는 자율형 AI 시스템** 입니다.

### 제조 현장 비유: Agent = 자동화된 공장 관리자(Supervisor)

숙련된 공장 관리자는 설비 소리만 듣고도 이상을 감지하고, 적절한 조치를 즉시 취합니다. AI Agent도 마찬가지입니다. 데이터를 보고, 이상 여부를 판단하고, 필요한 조치를 자동으로 수행합니다.

| 공장 관리자의 역할 | AI Agent의 역할 | 구체적 예시 |
|-------------------|----------------|-----------|
| **상황 파악**(현장 순회) | 관찰 (Observation) | 센서 데이터 드리프트 확인, 모델 성능 지표 조회 |
| **판단**(이상 여부 결정) | 의사결정 (Decision) | "드리프트가 임계치를 초과했으므로 재학습이 필요하다" |
| **조치**(정비 지시, 라인 변경) | 행동 (Action) | 재학습 Job 실행, 배치 예측 수행, 알림 발송 |
| **보고**(일일 보고서 작성) | 결과 기록 (Logging) | 수행 결과를 JSON으로 반환, MLflow에 기록 |

### 자동화의 발전 역사

기존 자동화는 "미리 정해진 규칙"대로만 동작합니다. AI Agent는 **자연어로 된 지침(System Prompt)** 을 이해하고, 상황에 맞게 **어떤 Tool을 어떤 순서로 호출할지 스스로 결정** 합니다. 자동화의 발전 단계를 정리하면 다음과 같습니다.

| 단계 | 방식 | 설명 |
|------|------|------|
| 1단계 | 규칙 기반 자동화 | "온도 > 100도이면 알림 발송" (단순 If-Else 조건) |
| 2단계 | 스크립트 파이프라인 | "매일 06:00에 학습 → 평가 → 배포 순서로 실행" (고정된 순서) |
| 3단계 | 조건부 파이프라인 | "드리프트가 감지되면 재학습, 아니면 건너뜀" (분기 로직) |
| **4단계** | **AI Agent (현재)** | **상황을 종합적으로 판단하여 최적의 행동을 스스로 선택**(자율 판단) |

---

## Databricks에서 Agent를 만드는 이점

Databricks는 **Mosaic AI Agent Framework** 를 통해 엔터프라이즈급 AI Agent를 쉽게 구축할 수 있습니다.

| 기능 | 설명 | 이점 |
|------|------|------|
| **ChatAgent 인터페이스** | MLflow의 표준 Agent 인터페이스 | 코드 몇 줄로 Agent를 정의하고 배포 가능 |
| **UC Functions as Tools** | Unity Catalog 함수를 Agent의 도구로 등록 | 기존 SQL/Python 함수를 그대로 Agent가 호출 가능 |
| **Model Serving 배포** | Agent를 REST API 엔드포인트로 배포 | 외부 시스템에서 HTTP 요청으로 Agent 호출 가능 |
| **Guardrails (안전 장치)** | Agent의 행동 범위를 제한 | 위험한 작업(예: 운영 모델 삭제)을 방지 |
| **Evaluation (평가)** | Agent 성능을 체계적으로 평가 | Agent가 올바른 판단을 내리는지 검증 |

---

## Agent가 수행하는 작업

이 PoC에서 Agent가 수행하는 작업을 정리하면 다음과 같습니다. 각 트리거는 제조 현장에서 실제로 발생하는 상황을 모델링한 것입니다.

| # | 트리거 (Trigger) | Agent의 판단 | Agent의 행동 | 제조 비유 |
|---|-----------------|-------------|-------------|----------|
| 1 | 데이터 드리프트 감지 시 | "센서 데이터 분포가 변했다. 기존 모델이 부정확해질 수 있다" | 재학습 트리거 | 원재료 로트가 변경되어 공정 조건 재설정 필요 |
| 2 | 스케줄(일 4회) 도래 시 | "정해진 시간이 되었다. 최신 데이터로 예측해야 한다" | 배치 예측 실행 | 교대조(Shift) 시작 시 품질 예측 수행 |
| 3 | 모델 성능 저하 감지 시 | "예측 정확도가 임계치 이하로 떨어졌다" | 알림 및 자동 롤백 | SPC 관리 한계 초과 시 라인 정지 및 조치 |
| 4 | 새 데이터 유입 시 | "새로운 센서 데이터가 들어왔다. 피처를 업데이트해야 한다" | 피처 파이프라인 실행 | 새 원재료 입고 시 수입 검사 수행 |

## 1. MLOps Tool 함수 정의

### Tool(도구)이란?

AI Agent에서 **Tool** 이란 Agent가 호출할 수 있는 **구체적인 기능(함수)** 을 말합니다. 제조 현장에 비유하면, 공장 관리자(Agent)가 사용할 수 있는 **장비와 시스템** 입니다. Agent는 상황에 따라 이 Tool들을 **자율적으로 선택하여 호출** 합니다. 어떤 Tool을 어떤 순서로 호출할지는 Agent가 판단합니다.

실제 운영 환경에서는 이 함수들을 **Unity Catalog Function** 으로 등록하여 사용합니다. 그러면 Databricks의 권한 관리(Governance)가 적용되어, 누가 어떤 Tool을 호출했는지 추적(Audit)할 수 있습니다.

다음 표는 4개 Tool과 제조 현장 비유를 정리한 것입니다.

| Tool 함수 | 역할 | 제조 현장 비유 |
|-----------|------|-------------|
| `check_data_drift` | 데이터 이상 감지 (PSI 기반) | SPC 모니터링 시스템 |
| `trigger_retraining` | 모델 재학습 명령 | MES 재작업 지시 시스템 |
| `run_batch_prediction` | 대량 예측 수행 | 자동 검사 장비 |
| `get_model_status` | 현재 모델 상태 확인 | 설비 상태 모니터 |

### Tool 1: check_data_drift (데이터 드리프트 확인)

학습 데이터와 최신 추론 데이터의 분포를 비교하여 "드리프트"를 탐지합니다. **드리프트(Drift)** 란 시간이 지남에 따라 데이터의 통계적 분포가 변하는 현상입니다. 제조 비유로 설명하면, 원재료 로트가 바뀌면 원재료의 특성(경도, 순도 등)이 달라지듯이, 센서 데이터도 계절, 설비 노후화 등으로 분포가 변합니다. 모델은 "옛날 데이터"로 학습했으므로, 데이터가 변하면 예측 정확도가 떨어집니다.

**PSI(Population Stability Index) 판정 기준** 은 다음과 같습니다.

| PSI 범위 | 판정 | 행동 |
|----------|------|------|
| < 0.1 | 안정 | 관찰만 |
| 0.1 ~ 0.2 | 주의 | 경미한 변화, 관찰 필요 |
| > 0.2 | **드리프트 감지** | **재학습 권장**(이 PoC의 임계치) |
| > 0.25 | 심각 | 즉시 재학습 필요 |

```python
def check_data_drift(table_name: str = "lgit_pm_inference_results") -> dict:
    """PSI 기반 데이터 드리프트 확인"""
    import numpy as np

    feature_columns = ["air_temperature_k", "process_temperature_k",
                       "rotational_speed_rpm", "torque_nm", "tool_wear_min"]

    train_pdf = spark.table("lgit_pm_training").filter("split='train'").select(*feature_columns).toPandas()

    try:
        infer_pdf = spark.table(table_name).select(*feature_columns).toPandas()
    except Exception:
        return {"drift_detected": False, "message": "추론 테이블이 없습니다.", "psi_values": {}}

    psi_values = {}
    for col in feature_columns:
        breakpoints = np.linspace(
            min(train_pdf[col].min(), infer_pdf[col].min()),
            max(train_pdf[col].max(), infer_pdf[col].max()), 11)
        expected = np.maximum(np.histogram(train_pdf[col], bins=breakpoints)[0] / len(train_pdf), 0.001)
        actual = np.maximum(np.histogram(infer_pdf[col], bins=breakpoints)[0] / len(infer_pdf), 0.001)
        psi_values[col] = float(np.sum((actual - expected) * np.log(actual / expected)))
    drift_detected = any(v > 0.2 for v in psi_values.values())
    return {"drift_detected": drift_detected, "psi_values": psi_values,
            "timestamp": datetime.now().isoformat()}
```

### Tool 2: trigger_retraining (모델 재학습 트리거)

모델 재학습 파이프라인을 실행합니다. 실제 환경에서는 Databricks Jobs API(`w.jobs.run_now()`)를 호출하여 피처 엔지니어링 → 학습 → 등록 → 검증까지 전체 파이프라인을 수행합니다. 제조 비유로 설명하면, 공정 조건이 변경되었을 때 MES 시스템이 자동으로 새로운 조건에 맞는 레시피(Recipe)를 다시 계산하고 설비에 적용하는 것과 같습니다.

트리거 사유(reason)에 따라 다음과 같이 구분됩니다.

| 사유 | 설명 |
|------|------|
| `scheduled` | 정기 스케줄에 의한 재학습 (예: 매주 월요일) |
| `data_drift_detected` | 드리프트 감지로 인한 긴급 재학습 |
| `performance_degradation` | 모델 성능 저하로 인한 재학습 |

```python
def trigger_retraining(reason: str = "scheduled") -> dict:
    """모델 재학습 트리거 — 실제 환경에서는 w.jobs.run_now() 호출"""
    print(f"재학습 트리거 — 사유: {reason}")
    return {"status": "triggered", "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "message": f"재학습이 트리거되었습니다. 사유: {reason}"}
```

{% hint style="info" %}
**실제 운영 환경에서의 trigger_retraining 구현**: 위의 함수는 교육용 시뮬레이션입니다. 실제 운영에서는 Databricks SDK로 Job을 직접 트리거합니다:
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
run = w.jobs.run_now(
    job_id=178771619413732,  # LGIT_MLOps_PoC_Structured_Pipeline
    notebook_params={"retrain_reason": reason}
)
```
UC Function으로 등록하면 Agent가 SQL로 직접 호출할 수도 있습니다: `SELECT trigger_retraining('data_drift_detected')`
{% endhint %}

### Tool 3: run_batch_prediction (배치 예측 실행)

Champion(현재 운영 중인 최고 성능) 모델을 사용하여 최신 센서 데이터 전체에 대해 한꺼번에 고장 예측을 수행합니다. 배치 예측은 대량의 데이터를 정해진 시간에 한꺼번에 처리하는 방식입니다. 제조 비유로 설명하면, 교대조(Shift) 시작 시 전체 설비 상태를 한꺼번에 점검하는 것에 해당합니다.

기술적 동작 순서는 다음과 같습니다.

1. MLflow에서 Champion 별칭(Alias)이 부여된 모델을 로드
2. Spark UDF(User Defined Function)로 변환하여 분산 처리
3. 전체 데이터에 대해 병렬로 예측 수행 (수백만 건도 가능)

```python
def run_batch_prediction() -> dict:
    """Champion 모델로 배치 예측 실행"""
    champion_udf = mlflow.pyfunc.spark_udf(spark, model_uri=f"models:/{model_name}@Champion")
    inference_df = spark.table("lgit_pm_training").select("udi", "type", *feature_columns)
    preds = inference_df.withColumn("failure_probability", champion_udf(*feature_columns))
    count = preds.count()
    return {"status": "success", "predictions_count": count,
            "timestamp": datetime.now().isoformat()}
```

### Tool 4: get_model_status (현재 모델 상태 확인)

Unity Catalog에 등록된 Champion 모델의 현재 상태를 조회합니다. 모델 버전, 성능 지표(F1 Score, AUC) 등을 반환합니다. 제조 비유로 설명하면, 설비 관리 시스템에서 현재 가동 중인 설비의 상태(가동률, 최근 정비 이력, 잔여 수명 등)를 조회하는 것과 같습니다.

반환되는 지표의 의미는 다음과 같습니다.

| 지표 | 설명 | 범위 |
|------|------|------|
| **F1 Score** | 정밀도(Precision)와 재현율(Recall)의 조화 평균 | 0~1 (1에 가까울수록 좋음) |
| **AUC** | 모델의 분류 능력을 종합적으로 평가하는 지표 | 0.5 = 동전 던지기 수준, 1.0 = 완벽한 분류 |

```python
def get_model_status() -> dict:
    """현재 Champion 모델의 상태를 확인합니다."""
    from mlflow import MlflowClient
    client = MlflowClient()
    champion = client.get_model_version_by_alias(model_name, "Champion")
    run = mlflow.get_run(champion.run_id)
    return {
        "model_name": model_name,
        "champion_version": champion.version,
        "val_f1_score": run.data.metrics.get("val_f1_score", "N/A"),
        "val_auc": run.data.metrics.get("val_auc", "N/A"),
        "status": "active"
    }
```

## 2. Agent 시스템 프롬프트 및 Tool 매핑

### 시스템 프롬프트(System Prompt)란?

**시스템 프롬프트** 는 AI Agent에게 주어지는 **역할 정의서이자 업무 지침서** 입니다. 제조 현장에 비유하면, 새로 부임한 공장 관리자에게 전달하는 **"직무 기술서(Job Description) + 업무 매뉴얼" **입니다.

시스템 프롬프트를 잘 작성하면 Agent의 행동이 정확해지고, 잘못 작성하면 예기치 않은 행동을 할 수 있습니다. 마치 업무 매뉴얼이 명확해야 직원이 올바른 판단을 내리는 것과 같습니다. Agent는 이 시스템 프롬프트와 **Tool 목록** 을 기반으로, 주어진 상황에서 어떤 Tool을 어떤 순서로 호출할지 자동으로 판단하여 작업을 수행합니다.

```python
SYSTEM_PROMPT = """당신은 LG Innotek 제조 현장의 MLOps Agent입니다.
다음 도구를 사용하여 예지보전 모델의 운영을 자동화합니다:

1. check_data_drift: 데이터 드리프트 확인
2. trigger_retraining: 모델 재학습 트리거
3. run_batch_prediction: 배치 예측 실행
4. get_model_status: 현재 모델 상태 확인

주요 자동화 규칙:
- 데이터 드리프트가 감지되면 자동으로 재학습을 트리거합니다.
- 스케줄에 따라 배치 예측을 실행합니다.
- 모델 성능이 임계값 이하이면 알림을 생성합니다."""

TOOLS = {
    "check_data_drift": check_data_drift,
    "trigger_retraining": trigger_retraining,
    "run_batch_prediction": run_batch_prediction,
    "get_model_status": get_model_status,
}
```

## 3. Agent 실행 시뮬레이션

이제 Agent가 실제 운영 환경에서 마주칠 수 있는 **세 가지 대표적인 시나리오** 를 시뮬레이션합니다. 각 시나리오는 제조 현장에서 실제로 발생하는 상황을 모델링한 것입니다.

| 시나리오 | 제조 현장 상황 | Agent의 대응 |
|---------|-------------|-------------|
| **시나리오 1: 정기 상태 점검** | 교대조 인수인계 시 설비 상태 확인 | 현재 Champion 모델의 버전, 성능 지표 등을 조회 |
| **시나리오 2: 드리프트 기반 재학습** | 계절 변화로 원재료 특성이 바뀜 | 데이터 분포 변화를 감지하고, 변화가 크면 자동으로 재학습을 실행 |
| **시나리오 3: 배치 예측** | 근무조(Shift) 시작 시 전체 설비 상태 점검 | Champion 모델로 전체 센서 데이터에 대해 고장 확률을 예측 |

```python
# 시나리오 1: 정기 상태 점검
status = get_model_status()
print(f"모델 상태: {json.dumps(status, indent=2, ensure_ascii=False)}")

# 시나리오 2: 드리프트 기반 자동 재학습
drift_result = check_data_drift()
if drift_result["drift_detected"]:
    retrain_result = trigger_retraining(reason="data_drift_detected")

# 시나리오 3: 스케줄 기반 배치 예측
pred_result = run_batch_prediction()
```

## 4. Agent를 ChatAgent로 패키징 (배포용)

### 왜 패키징이 필요한가?

위에서 시뮬레이션한 Agent 로직을 **실제 운영 환경** 에서 사용하려면, 이 Agent를 하나의 **독립된 서비스** 로 배포해야 합니다. 제조 비유로 설명하면, 수동으로 버튼을 눌러 Agent를 실행하는 것에서, Agent가 24시간 자동으로 대기하며 이벤트가 발생하면 스스로 작동하는 API 서비스로 전환하는 것입니다. 이것은 공장에서 **수동 검사 장비를 인라인(In-line) 자동 검사 장비로 교체** 하는 것과 같습니다.

배포 옵션은 다음과 같습니다.

| 배포 방식 | 설명 | 사용 시점 |
|----------|------|----------|
| **Model Serving 엔드포인트** | REST API로 Agent를 호출 | 외부 시스템(ERP, MES)에서 Agent를 호출할 때 |
| **Workflow Task** | Databricks Job의 태스크로 Agent를 실행 | 정기 스케줄에 따라 Agent를 실행할 때 |
| **Trigger 기반** | 특정 이벤트(테이블 업데이트, 알림 등) 발생 시 자동 실행 | 새 데이터 유입, 드리프트 감지 등 이벤트 기반 자동화 |

### Agent 전체 워크플로우

드리프트 확인 → 재학습 판단 → 배치 예측 → 상태 보고를 하나의 흐름으로 실행합니다.

```python
def mlops_agent_workflow(trigger_type: str = "full_cycle"):
    """
    MLOps Agent의 전체 워크플로우를 실행합니다.

    Args:
        trigger_type: 트리거 유형
            - "scheduled": 정기 스케줄 (배치 예측 + 상태 점검)
            - "drift_check": 드리프트 확인 및 필요 시 재학습
            - "full_cycle": 전체 주기 (드리프트 → 재학습 → 예측)
    """
    results = {"trigger_type": trigger_type, "timestamp": datetime.now().isoformat()}

    if trigger_type in ["scheduled", "full_cycle"]:
        results["batch_prediction"] = run_batch_prediction()

    if trigger_type in ["drift_check", "full_cycle"]:
        drift = check_data_drift()
        results["drift_check"] = drift
        if drift["drift_detected"]:
            results["retraining"] = trigger_retraining(reason="auto_drift_detection")

    results["model_status"] = get_model_status()
    return results
```

{% hint style="info" %}
실제 운영에서는 이 Agent를 **Model Serving 엔드포인트** 로 배포하여, Workflow Trigger나 API 호출로 자동 실행할 수 있습니다. MLflow Tracing으로 Agent의 모든 Tool 호출 이력이 추적됩니다.
{% endhint %}

---

## 5. Databricks에서 오픈소스 Agent 프레임워크 활용

AI Agent 구현은 반드시 특정 프레임워크에 묶일 필요가 없습니다. Databricks Compute 환경에서는 **LangChain, LangGraph, CrewAI, AutoGen** 등 오픈소스 프레임워크를 `%pip install` 한 줄로 설치하고 그대로 실행할 수 있습니다. 이것이 Databricks의 큰 장점입니다 -- 플랫폼에 종속되지 않으면서도, UC Function/MLflow/Model Serving 등 Databricks 고유 기능과 자연스럽게 통합됩니다.

### 프레임워크 선택 가이드

다음 표는 주요 Agent 프레임워크의 특징과 적합한 상황을 비교한 것입니다.

| 프레임워크 | 핵심 특징 | 적합한 상황 | 난이도 |
|-----------|---------|-----------|:---:|
| **LangChain** | 가장 넓은 생태계, Tool/Chain/Agent 추상화 | 단순한 Tool 호출, RAG, 챗봇 | 낮음 |
| **LangGraph** | 상태 머신 기반 워크플로우, 조건 분기/루프 | MLOps Agent처럼 복잡한 판단 로직 | 중간 |
| **CrewAI** | 역할 기반 멀티 에이전트 협업 | 여러 전문가가 협업해야 하는 작업 | 중간 |
| **AutoGen**(Microsoft) | 에이전트 간 대화 기반 문제 해결 | 토론/합의 기반 의사결정 | 높음 |
| **Databricks Agent SDK** | Databricks 네이티브, UC 완전 통합 | 운영 배포 최적화, 거버넌스 필수 | 낮음 |

**권장 경로** 는 LangChain으로 프로토타입 → LangGraph로 복잡한 워크플로우 구현 → Databricks Agent SDK로 운영 배포입니다.

### Databricks + LangChain/LangGraph 통합 아키텍처

Databricks 환경에서 LangChain/LangGraph를 사용할 때의 핵심 통합 포인트를 정리합니다.

| 계층 | 역할 | Databricks 기능 |
|------|------|----------------|
| **LLM (두뇌)** | 상황 판단, Tool 선택 | Foundation Model API (Llama, DBRX) -- API 키 불필요 |
| **Tools (손)** | 실제 행동 수행 | UC Function -- SQL/Python 함수를 Tool로 등록 |
| **Memory (기억)** | 이전 대화/판단 기록 | Delta Table, MLflow Tracing |
| **Orchestration (지휘)** | 워크플로우 관리 | LangGraph StateGraph 또는 CrewAI |
| **Deployment (배포)** | Agent를 서비스로 운영 | Model Serving REST API, Lakeflow Jobs |
| **Monitoring (감시)** | 판단 과정 추적/디버깅 | MLflow Tracing (자동 계측) |

핵심 통합 코드 예시는 다음과 같습니다.

```python
# 1. Foundation Model API — 별도 API 키 없이 Databricks 내장 LLM 사용
from langchain_databricks import ChatDatabricks
llm = ChatDatabricks(endpoint="databricks-meta-llama-3-1-70b-instruct")

# 2. UC Function as Tool — SQL 함수를 Agent Tool로 직접 연결
from databricks_langchain import UCFunctionToolkit
tools = UCFunctionToolkit(function_names=["mlops.tools.check_drift", "mlops.tools.trigger_retrain"])

# 3. MLflow Tracing — Agent의 모든 판단을 자동 기록
import mlflow
mlflow.langchain.autolog()  # 이 한 줄로 LangChain/LangGraph 전체 추적!
```

### LangGraph로 MLOps Agent 구현 예시

아래는 LangGraph를 사용하여 드리프트 감지 → 재학습 → 보고까지 자동으로 수행하는 Agent의 구조입니다. `observe → decide → act → report` 4단계 워크플로우를 그래프로 정의하고, `add_conditional_edges` 로 "재학습이 필요하면 act로, 아니면 바로 report로" 분기합니다.

```python
from langgraph.graph import StateGraph, END
from langchain_databricks import ChatDatabricks
from typing import TypedDict

# 1. Agent 상태 정의
class MLOpsState(TypedDict):
    drift_detected: bool
    max_psi: float
    retrain_needed: bool
    retrain_result: dict
    report: str

# 2. 각 노드(단계) 정의
def observe(state):
    result = check_data_drift()
    return {"drift_detected": result["drift_detected"], "max_psi": result["max_psi"]}

def decide(state):
    return {"retrain_needed": state["drift_detected"] and state["max_psi"] > 0.2}

def act(state):
    if state["retrain_needed"]:
        result = trigger_retraining(reason=f"drift_psi_{state['max_psi']:.2f}")
        return {"retrain_result": result}
    return {"retrain_result": {"status": "skipped"}}

def report(state):
    llm = ChatDatabricks(endpoint="databricks-meta-llama-3-1-70b-instruct")
    summary = llm.invoke(f"MLOps 상태 보고: 드리프트={state['drift_detected']}, "
                         f"PSI={state['max_psi']}, 재학습={state['retrain_result']}")
    return {"report": summary.content}

# 3. 워크플로우 그래프 구성
graph = StateGraph(MLOpsState)
graph.add_node("observe", observe)
graph.add_node("decide", decide)
graph.add_node("act", act)
graph.add_node("report", report)

graph.set_entry_point("observe")
graph.add_edge("observe", "decide")
graph.add_conditional_edges("decide",
    lambda s: "act" if s["retrain_needed"] else "report",
    {"act": "act", "report": "report"})
graph.add_edge("act", "report")
graph.add_edge("report", END)

# 4. Agent 실행
agent = graph.compile()
result = agent.invoke({"drift_detected": False, "max_psi": 0.0,
                       "retrain_needed": False, "retrain_result": {}, "report": ""})
```

{% hint style="info" %}
이것이 단순 if-else 스크립트와 LangGraph Agent의 차이입니다 -- LLM이 상황에 맞게 판단합니다. 실제 실행하려면 `%pip install langchain langgraph langchain-databricks` 설치가 필요합니다.
{% endhint %}

---

## 요약

### 이 노트북에서 배운 내용

| # | 학습 항목 | 핵심 내용 | 제조 비유 |
|---|---------|---------|----------|
| 1 | **MLOps Tool 함수** 정의 | 드리프트 확인, 재학습, 배치 예측, 상태 확인 4가지 Tool | 공장 관리자가 사용하는 장비/시스템 |
| 2 | **Agent 시스템 프롬프트** | Agent의 역할과 행동 규칙을 자연어로 정의 | 직무 기술서 + SOP(표준작업절차서) |
| 3 | **시나리오별 시뮬레이션** | 정기 점검, 드리프트 재학습, 배치 예측 시나리오 | 교대조 인수인계, 원재료 변경 대응, 생산 시작 점검 |
| 4 | **Agent 워크플로우 패키징** | Agent를 API 서비스로 배포하기 위한 준비 | 수동 검사 → 인라인 자동 검사 전환 |
| 5 | **오픈소스 프레임워크 활용** | LangChain, LangGraph, CrewAI 등과 Databricks 통합 | 표준 장비 + 자사 시스템 연동 |

### 핵심 포인트

AI Agent는 단순한 자동화 스크립트가 아닙니다. **상황을 이해하고, 판단하고, 최적의 행동을 선택** 하는 자율형 시스템입니다. 이를 통해 ML 모델 운영에 필요한 반복적인 작업(모니터링, 재학습 판단, 예측 수행)을 사람의 개입 없이 자동화할 수 있습니다.

### 최신 트렌드: AI Agent의 미래

- **Multi-Agent 시스템**: 여러 Agent가 협업하여 더 복잡한 작업을 수행 (예: 정형 데이터 Agent + 비정형 데이터 Agent + 보고서 Agent)
- **Human-in-the-Loop**: 중요한 결정(예: Champion 모델 교체)은 사람의 승인을 받고 실행
- **Autonomous MLOps**: 2025~2026년 트렌드로, Agent가 전체 ML 생명주기를 자율적으로 관리

**다음 단계**: [10. Job 스케줄링](10-job-scheduling.md)
