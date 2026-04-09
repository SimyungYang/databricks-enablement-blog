# LLM 학습 과정 3단계

[< LLM 기초 목차로 돌아가기](README.md)

---

LLM이 "똑똑한 챗봇"이 되기까지는 세 단계의 학습 과정을 거칩니다. 각 단계는 목적, 데이터, 비용이 완전히 다릅니다.

## Stage 1: Pre-training (사전학습)

인터넷, 도서, 코드 저장소 등 **수조 토큰 규모의 텍스트 데이터** 를 사용하여 **"다음 토큰 예측(Next-Token Prediction)"** 과제를 학습합니다.

- **데이터**: 인터넷 크롤링 (Common Crawl), 위키피디아, 책, GitHub 코드 등
- **규모**: 수천 대의 GPU를 수 주~수 개월간 사용
- **비용**: 수백만~수천만 달러 (Llama 3 405B 학습에 GPU 약 16,000대 사용 추정)
- **결과**: 언어 패턴, 문법, 세계 지식을 학습하지만, 아직 **"도움이 되는 어시스턴트"가 아님**

이 단계의 모델은 프롬프트를 주면 단순히 텍스트를 이어서 생성할 뿐, 질문에 답하거나 지시를 따르지 못합니다.

## Stage 2: Supervised Fine-Tuning (SFT, 지도 미세조정)

사람이 직접 작성한 **(지시, 이상적인 응답)** 쌍 데이터로 학습합니다.

- **데이터**: 인간 전문가(Demonstrator)가 작성한 고품질 (instruction, ideal_response) 쌍 — 수천~수만 개
- **목적**: 모델이 **지시를 이해하고, 도움이 되는 방식으로 응답** 하도록 행동을 정렬
- **예시**: "서울의 인구는?" → "서울의 인구는 약 950만 명입니다. (2024년 기준)"
- **비용**: Pre-training 대비 매우 적음 (GPU 수십 대, 수 일)

## Stage 3: RLHF / DPO (인간 피드백 강화학습)

사람이 모델의 두 가지 출력을 비교하여 **더 나은 응답을 선택** 하는 선호 데이터를 수집하고, 이를 바탕으로 모델을 최적화합니다.

- **RLHF (Reinforcement Learning from Human Feedback)**: 선호 데이터로 **보상 모델(Reward Model)** 을 학습 → PPO(Proximal Policy Optimization) 알고리즘으로 LLM 최적화
- **DPO (Direct Preference Optimization)**: 보상 모델 없이 선호 데이터로 직접 LLM을 최적화하는 간소화된 방법
- **효과**: 안전성, 유용성, 무해성을 강화 — GPT-3를 ChatGPT로 변환한 핵심 단계
- **비용**: SFT와 유사하거나 약간 높음

## 3단계 비교 요약

| 항목 | Stage 1: Pre-training | Stage 2: SFT | Stage 3: RLHF/DPO |
|------|----------------------|--------------|-------------------|
| **목적** | 언어 패턴 학습 | 지시 수행 능력 부여 | 응답 품질·안전성 향상 |
| **데이터** | 수조 토큰 (인터넷, 도서, 코드) | 수천~수만 (지시, 응답) 쌍 | 수만 (응답 A vs B 선호) 쌍 |
| **컴퓨팅 비용** | 수천 GPU × 수 개월 (수백만~수천만 달러) | 수십 GPU × 수 일 (수만 달러) | 수십 GPU × 수 일 (수만 달러) |
| **모델이 배우는 것** | "다음에 올 단어가 뭘까?" | "질문에 어떻게 답해야 하지?" | "어떤 답변이 더 좋을까?" |
| **비유** | 수만 권의 책을 읽은 학생 | 선생님의 시범을 보고 따라하는 학생 | 피드백을 받고 답변을 개선하는 학생 |

{% hint style="info" %}
**실무 포인트**: 대부분의 기업은 Stage 1을 직접 하지 않습니다. Foundation Model API를 통해 이미 학습된 모델을 사용하고, 필요시 Stage 2(Fine-tuning)만 수행합니다. Databricks의 Mosaic AI Training은 Stage 2를 위한 관리형 환경을 제공합니다.
{% endhint %}

---

## Stage 1.5: Continued Pre-Training (CPT, 도메인 특화 사전학습)

Stage 1(사전학습)과 Stage 2(SFT) 사이에 위치하는 **선택적 단계** 입니다. 범용 모델이 특정 도메인의 언어, 용어, 패턴을 충분히 학습하지 못한 경우, **도메인 특화 데이터로 추가 사전학습** 을 수행합니다.

### 왜 CPT가 필요한가?

범용 LLM은 인터넷 텍스트로 학습되었기 때문에, 특정 도메인의 전문 용어나 패턴에 약할 수 있습니다.

| 도메인 | 범용 모델의 한계 | CPT 학습 데이터 예시 |
|--------|----------------|---------------------|
| **금융** | 재무제표 형식, 금융 규제 용어 이해 부족 | 10-K/10-Q 보고서, 금융감독원 공시, 신용평가 보고서 |
| **법률** | 법률 조항 인용 형식, 판례 구조 미숙 | 판례 전문, 법률 조문, 계약서 샘플 |
| **의료** | 의학 약어(Dx, Rx), 임상 기록 형식 미숙 | PubMed 논문, 임상 노트, 약물 데이터베이스 |
| **제조** | 설비 코드, 품질 검사 용어 미숙 | 설비 매뉴얼, 품질 보고서, 센서 로그 설명서 |

### CPT 수행 방법

```python
# Databricks Mosaic AI Training으로 CPT 수행 (개념 예시)
from databricks.model_training import foundation_model as fm

# 1. 도메인 데이터를 Delta 테이블에 준비
# 테이블: catalog.schema.finance_corpus (text 컬럼)

# 2. CPT 학습 실행
run = fm.create(
    model="meta-llama/Llama-3.3-70B",
    train_data_path="dbfs:/Volumes/catalog/schema/training/finance_corpus",
    task_type="CONTINUED_PRETRAIN",  # CPT 모드
    register_to="catalog.schema.finance_llama",
    training_duration="1ep",  # 1 epoch
    learning_rate="5e-6",     # 낮은 학습률로 기존 지식 보존
)
```

{% hint style="warning" %}
**CPT의 리스크**: 학습률이 너무 높거나 데이터가 편향되면 **Catastrophic Forgetting(파괴적 망각)** 이 발생합니다. 모델이 도메인 지식을 얻는 대신 범용 능력을 잃는 현상입니다. 학습률을 낮게 설정하고(5e-6 이하), 도메인 데이터와 범용 데이터를 혼합하는 것이 좋습니다.
{% endhint %}

---

## SFT 심화: 파라미터 효율적 파인튜닝 (PEFT)

### Full Fine-Tuning의 문제

70B 모델을 Full Fine-Tuning하려면 **수백 GB의 GPU 메모리** 가 필요합니다. 대부분의 기업에게 현실적이지 않습니다.

### LoRA (Low-Rank Adaptation)

LoRA는 **원본 모델의 가중치를 동결(freeze)** 하고, 각 레이어에 **작은 행렬 쌍(A, B)** 만 추가하여 학습합니다.

| 항목 | Full Fine-Tuning | LoRA | QLoRA |
|------|-----------------|------|-------|
| **학습 파라미터** | 전체 (100%) | 0.1~1% | 0.1~1% |
| **GPU 메모리 (70B 기준)** | ~280GB (FP16) | ~80GB | ~24GB |
| **학습 품질** | 최고 | Full FT의 95~99% | LoRA의 ~98% |
| **학습 속도** | 느림 | 빠름 | 빠름 |

```python
# Databricks Mosaic AI Training에서 LoRA SFT
run = fm.create(
    model="meta-llama/Llama-3.3-70B",
    train_data_path="dbfs:/Volumes/catalog/schema/training/sft_data",
    task_type="INSTRUCTION_FINETUNE",
    register_to="catalog.schema.my_finetuned_model",
    training_duration="3ep",
    learning_rate="1e-4",
    # LoRA는 기본 활성화됨 — Mosaic AI Training이 자동으로 PEFT 적용
)
```

### QLoRA (Quantized LoRA)

QLoRA는 LoRA에 **양자화(Quantization)** 를 결합합니다. 원본 모델을 4-bit로 양자화하여 메모리를 극적으로 줄이고, LoRA 어댑터만 16-bit로 학습합니다. 단일 A100 80GB GPU로 70B 모델 파인튜닝이 가능해집니다.

### 데이터 품질 vs 양: 무엇이 더 중요한가?

SFT에서 **데이터 품질이 양보다 압도적으로 중요합니다.**

| 연구 | 핵심 발견 |
|------|----------|
| **LIMA (Zhou et al., 2023)** | 고품질 1,000개 예시로 SFT한 모델이 52K RLHF 데이터로 학습한 모델과 동등한 성능 |
| **Alpaca (Stanford, 2023)** | GPT-3.5가 생성한 52K 합성 데이터로도 유의미한 SFT 가능 |
| **Quality is All You Need** | 데이터 10배 증가보다 품질 2배 향상이 성능에 더 큰 영향 |

{% hint style="info" %}
**실무 가이드**: SFT 데이터는 **1,000~10,000개의 고품질 (instruction, response) 쌍** 으로 시작하세요. 1만 개를 채우려고 품질을 낮추는 것보다, 1,000개를 도메인 전문가가 직접 작성하는 것이 훨씬 효과적입니다.
{% endhint %}

### Catastrophic Forgetting 방지 전략

파인튜닝 시 모델이 기존에 학습한 범용 능력을 잃는 현상을 **파괴적 망각(Catastrophic Forgetting)** 이라고 합니다.

- **낮은 학습률 사용**: 1e-5 ~ 5e-5 범위. 너무 높으면 기존 지식을 빠르게 덮어씀
- **학습 데이터 혼합**: 도메인 데이터(70%) + 범용 데이터(30%)를 섞어 학습
- **LoRA 사용**: 원본 가중치를 동결하므로 본질적으로 망각 위험이 낮음
- **조기 종료(Early Stopping)**: 검증 세트의 성능이 떨어지기 시작하면 학습 중단

---

## RLHF 이후 기법: 더 단순해지는 Alignment

RLHF는 강력하지만 복잡합니다. **보상 모델 학습 → PPO 최적화** 라는 2단계 파이프라인이 불안정하고 하이퍼파라미터에 민감합니다. 이를 개선하기 위해 다양한 대안 기법이 등장했습니다.

### 주요 Alignment 기법 비교

| 기법 | 필요한 것 | 보상 모델 | 핵심 아이디어 | 복잡도 |
|------|----------|----------|--------------|--------|
| **RLHF (PPO)** | 선호 쌍 데이터 | 필요 | 보상 모델 학습 → PPO로 정책 최적화 | 매우 높음 |
| **DPO** | 선호 쌍 데이터 | 불필요 | 선호 데이터로 직접 LLM 최적화 (closed-form 해) | 중간 |
| **KTO** | 좋음/나쁨 레이블만 | 불필요 | 쌍이 아닌 개별 응답에 좋다/나쁘다 레이블만으로 학습 | 낮음 |
| **ORPO** | 선호 쌍 데이터 | 불필요 | SFT + Alignment를 한 단계로 통합 | 낮음 |
| **SimPO** | 선호 쌍 데이터 | 불필요 | DPO를 단순화. 참조 모델(reference model) 불필요 | 낮음 |

### 트렌드: 점점 단순해지는 Alignment

```
RLHF (2022) → DPO (2023) → KTO/ORPO (2024) → SimPO (2024)
   복잡              ← - - - - - - - - →              단순
```

- **RLHF**: 보상 모델 + PPO. 4개의 모델을 동시에 관리 (기본 모델, 참조 모델, 보상 모델, 정책 모델)
- **DPO**: 보상 모델 제거. 2개의 모델만 필요 (기본 모델, 참조 모델)
- **SimPO**: 참조 모델도 제거. 1개의 모델만 필요

{% hint style="info" %}
**실무적 선택**: 2025년 기준, **DPO가 가장 보편적인 선택** 입니다. RLHF 대비 구현이 간단하면서 성능은 동등합니다. KTO는 선호 쌍을 구성하기 어려운 경우(예: 고객 피드백 "좋아요/싫어요")에 유용합니다.
{% endhint %}

---

## 합성 데이터로 SFT 데이터 생성

고품질 SFT 데이터를 사람이 직접 작성하는 것은 비용이 높습니다. **강력한 모델(Teacher)** 을 활용하여 SFT 데이터를 자동 생성하는 기법이 널리 사용됩니다.

### Self-Instruct

1. 소수의 시드(seed) instruction을 작성 (수십 개)
2. LLM이 시드를 참고하여 **새로운 instruction을 생성**
3. 각 instruction에 대해 LLM이 **응답을 생성**
4. 품질 필터링 (중복 제거, 길이 필터, 독성 검사)

### Evol-Instruct (WizardLM)

기존 instruction을 **점진적으로 복잡하게 진화** 시킵니다.

```
원본: "서울의 인구를 알려주세요"
  ↓ 깊이 진화 (Deepening)
진화 1: "서울의 인구 변화 추이를 10년 단위로 설명하고, 감소 원인을 분석하세요"
  ↓ 너비 진화 (Widening)
진화 2: "서울과 도쿄의 인구 변화를 비교하고, 도시화 정책의 차이를 논하세요"
```

### Databricks에서의 합성 데이터 파이프라인

```python
import mlflow
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# 1. 시드 데이터 준비 (소수의 고품질 예시)
seed_instructions = [
    {"instruction": "...", "response": "..."},
    # 50~100개
]

# 2. Foundation Model API로 합성 데이터 생성
def generate_synthetic_pair(seed):
    prompt = f"""다음 예시를 참고하여, 유사한 스타일의 새로운 instruction과 response 쌍을 생성하세요.

예시:
Instruction: {seed['instruction']}
Response: {seed['response']}

새로운 쌍을 JSON으로 출력:"""

    response = w.serving_endpoints.query(
        name="databricks-claude-sonnet-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    return response.choices[0].message.content

# 3. 대량 생성 후 Delta 테이블에 저장
# 4. 품질 필터링 (중복 제거, 독성 검사, 길이 필터)
# 5. SFT 학습 데이터로 사용
```

{% hint style="warning" %}
**합성 데이터 주의사항**: 합성 데이터만으로 학습하면 **Model Collapse** 현상이 발생할 수 있습니다. Teacher 모델의 편향이 증폭되어 다양성이 감소합니다. 반드시 **인간 작성 데이터와 혼합**(최소 20~30%)하는 것을 권장합니다.
{% endhint %}

---

## Databricks에서의 학습 단계별 활용

| 학습 단계 | Databricks 지원 | 대상 기업 | 비고 |
|----------|----------------|----------|------|
| **Stage 1: Pre-training** | Mosaic AI Training (대규모) | AI 연구 기관, 대기업 AI 랩 | 수천만 달러 소요. 대부분의 기업은 불필요 |
| **Stage 1.5: CPT** | Mosaic AI Training | 도메인 특화가 필수인 기업 (법률, 의료) | 수백만 달러. 필요성 신중히 검토 |
| **Stage 2: SFT (LoRA)** | Mosaic AI Training | **대부분의 기업** | 수만 달러. 가장 실용적인 커스텀 방법 |
| **Stage 3: DPO** | Mosaic AI Training | 응답 품질/안전성이 중요한 기업 | SFT 이후 추가 정렬 |
| **합성 데이터 생성** | Foundation Model API + Spark | SFT 데이터가 부족한 기업 | 비용 효율적 데이터 확보 |
| **Fine-tuning 없이 사용** | Foundation Model API + RAG | **가장 많은 기업** | 80%+ 사용 사례에 충분 |

{% hint style="info" %}
**현실적 가이드**: 대부분의 기업 GenAI 프로젝트는 **Fine-tuning 없이 Foundation Model API + RAG + Prompt Engineering** 으로 시작하는 것이 올바른 접근입니다. SFT는 RAG로 해결할 수 없는 **형식/스타일/도메인 용어** 문제가 있을 때만 고려하세요.
{% endhint %}

---

[< 이전: 핵심 개념](core-concepts.md) | [다음: LLM 내부 작동 직관적 이해 >](internals.md)
