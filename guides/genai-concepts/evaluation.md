# GenAI 평가 방법론

GenAI 시스템의 품질을 측정하고 개선하는 것은 프로덕션 배포의 필수 과정입니다. 전통적인 ML과 달리 LLM 평가는 정답이 명확하지 않아 체계적인 접근이 필요합니다.

{% hint style="info" %}
Databricks MLflow Evaluate를 사용하면 코드 몇 줄로 LLM 출력을 자동 평가할 수 있습니다.
{% endhint %}

---

## LLM 평가가 어려운 이유

| 기존 ML | GenAI/LLM |
|---------|-----------|
| 정답(레이블)이 명확 | "좋은 답변"의 기준이 주관적 |
| Accuracy, F1 등 정량 메트릭 | 유창성, 관련성, 안전성 등 정성 메트릭 |
| 테스트셋으로 일괄 평가 | 동일 질문에 다른 응답 가능 |
| 모델 출력이 수치/범주 | 모델 출력이 자유 형식 텍스트 |

{% hint style="warning" %}
"잘 동작하는 것 같다"라는 주관적 판단만으로 프로덕션에 배포하면, 환각(Hallucination)이나 유해 응답 문제가 발생할 수 있습니다. 반드시 체계적으로 평가하세요.
{% endhint %}

---

## 핵심 평가 메트릭

### 정확성 메트릭

| 메트릭 | 설명 | 측정 방법 |
|--------|------|-----------|
| **Faithfulness** (충실도) | 응답이 제공된 컨텍스트에 근거하는지 | 컨텍스트 대비 응답 내용 검증 |
| **Correctness** (정확성) | 응답이 사실적으로 정확한지 | 정답 레이블 대비 비교 |
| **Relevance** (관련성) | 응답이 질문에 적절히 답하는지 | 질문-응답 쌍 평가 |
| **Groundedness** (근거성) | 출처에 기반한 응답인지 | RAG에서 검색 문서와 응답 비교 |

### 안전성 메트릭

| 메트릭 | 설명 |
|--------|------|
| **Toxicity** (유해성) | 욕설, 혐오, 차별 표현 포함 여부 |
| **Bias** (편향) | 성별, 인종, 국적 등에 대한 편향 여부 |
| **PII Leakage** | 개인정보 노출 여부 |

### 운영 메트릭

| 메트릭 | 설명 | 목표 |
|--------|------|------|
| **Latency** (지연시간) | 응답 생성까지 소요 시간 | < 3초 (대화형) |
| **Cost** (비용) | 토큰당 비용 | 사용 사례별 예산 내 |
| **Throughput** (처리량) | 초당 처리 요청 수 | 동시 사용자 기준 |

---

## LLM-as-Judge 패턴

사람 대신 **다른 LLM을 평가자로 활용**하는 패턴입니다. 대량 평가를 자동화할 수 있어 실무에서 가장 많이 사용됩니다.

### 동작 원리

| 단계 | 설명 |
|------|------|
| 1. 평가 기준 정의 | "1~5점 척도로 관련성을 평가하세요" |
| 2. 평가 프롬프트 작성 | 질문, 응답, 컨텍스트를 Judge 모델에 전달 |
| 3. Judge 모델 실행 | GPT-4, Claude 등 강력한 모델이 점수와 이유 생성 |
| 4. 결과 집계 | 메트릭별 평균 점수, 분포 분석 |

{% hint style="success" %}
**팁**: Judge 모델은 평가 대상 모델보다 **같거나 더 강력한 모델**을 사용하세요. 약한 모델이 강한 모델을 평가하면 신뢰도가 낮습니다.
{% endhint %}

### LLM-as-Judge의 한계

- Judge 모델 자체의 편향이 평가에 영향
- 위치 편향(Position Bias): 먼저 제시된 응답에 높은 점수 경향
- 장문 편향: 긴 응답에 높은 점수를 주는 경향
- 해결책: 여러 Judge를 사용하거나, 인간 평가와 병행

---

## Databricks MLflow Evaluate

MLflow Evaluate는 Databricks에서 제공하는 LLM 평가 통합 도구입니다.

| 기능 | 설명 |
|------|------|
| 내장 메트릭 | Faithfulness, Relevance, Toxicity 등 사전 정의 |
| 커스텀 메트릭 | 비즈니스 요구에 맞는 평가 기준 추가 |
| LLM-as-Judge | GPT-4 등을 Judge로 자동 평가 |
| 비교 평가 | 여러 모델/프롬프트 버전 간 성능 비교 |
| 시각화 | MLflow UI에서 결과 대시보드 확인 |

### 기본 사용 예시

```python
import mlflow

results = mlflow.evaluate(
    model=my_agent,
    data=eval_dataset,
    model_type="databricks-agent",
)

# 결과 확인
print(results.metrics)
# {'faithfulness/v1/mean': 0.85, 'relevance/v1/mean': 0.92, ...}
```

---

## Human-in-the-Loop (Review App)

자동 평가만으로는 한계가 있으므로, **인간 피드백**을 체계적으로 수집하는 것이 중요합니다.

Databricks Review App은 다음 기능을 제공합니다.

| 기능 | 설명 |
|------|------|
| 웹 UI | 비기술 인력도 쉽게 피드백 제공 |
| 엄지 척 평가 | 좋음/나쁨 간단 피드백 |
| 상세 피드백 | 텍스트 코멘트, 올바른 답변 제공 |
| 데이터 수집 | 피드백이 Inference Table에 자동 저장 |
| 평가셋 구축 | 수집된 피드백을 평가 데이터셋으로 활용 |

{% hint style="info" %}
**권장 워크플로우**: MLflow Evaluate로 자동 평가 → 낮은 점수의 응답만 Review App에서 인간 검토 → 피드백으로 프롬프트/모델 개선
{% endhint %}

---

## 참고 자료

- [Databricks MLflow Evaluate 문서](https://docs.databricks.com/en/mlflow/llm-evaluate.html)
- [Databricks Review App 문서](https://docs.databricks.com/en/generative-ai/agent-evaluation/review-app.html)
- [Zheng et al., "Judging LLM-as-a-Judge" (2023)](https://arxiv.org/abs/2306.05685)
- [RAGAS: Evaluation Framework for RAG](https://docs.ragas.io/)
