# LLM 기초 (Large Language Model)

LLM은 대규모 텍스트 데이터로 학습된 딥러닝 모델로, 자연어를 이해하고 생성할 수 있습니다. GenAI의 핵심 기반 기술입니다.

**Large Language Model (대규모 언어 모델)** 은 수십억~수조 개의 파라미터를 가진 신경망 모델입니다. 대량의 텍스트 데이터에서 언어 패턴을 학습하여, 주어진 입력(Prompt)에 대해 자연스러운 텍스트를 생성합니다.

핵심 원리는 놀라울 정도로 단순합니다: "** 다음에 올 가장 적절한 토큰을 예측한다.**" 이 간단한 원리가 수십억 개의 파라미터와 방대한 학습 데이터를 만나면, 마치 "이해"하는 것처럼 보이는 출력을 생성합니다.

### LLM의 주요 능력

- **텍스트 생성**: 자연스러운 문장, 코드, 요약 생성
- **질의응답**: 지식 기반 Q&A
- **추론**: 논리적 사고와 문제 해결
- **번역**: 다국어 텍스트 변환
- **코드 생성**: 프로그래밍 코드 작성 및 디버깅

{% hint style="info" %}
**학습 목표**
- Transformer 아키텍처와 Self-Attention의 핵심 원리를 설명할 수 있다
- 토큰화 과정과 컨텍스트 윈도우의 제한 이유를 이해한다
- Hallucination의 발생 원인과 해결 방법(RAG/Grounding)을 설명할 수 있다
- 주요 LLM 모델을 비교하고 용도에 맞게 선택할 수 있다
- Fine-tuning, Prompting, RAG의 트레이드오프를 판단할 수 있다
{% endhint %}

---

## 목차

| 페이지 | 내용 |
|--------|------|
| [Transformer 아키텍처](transformer.md) | Self-Attention, Multi-Head Attention, Positional Encoding, Encoder vs Decoder |
| [핵심 개념](core-concepts.md) | Token, 토큰화 알고리즘, Context Window, Temperature, Top-p |
| [LLM 학습 과정](training.md) | Pre-training, SFT, RLHF/DPO 3단계 |
| [LLM 내부 작동 직관적 이해](internals.md) | 패턴 매칭, 세계 모델, Scaling, 비유 모음 |
| [Hallucination](hallucination.md) | 유형, 원인, 해결, 업종별 리스크 |
| [주요 LLM 모델 비교](models.md) | 모델 비교표, MoE 아키텍처, Emergent Abilities |
| [실전 가이드](practical.md) | Fine-tuning vs RAG vs Prompting, 추론 최적화, 비용 최적화, 모델 선택, 고객 FAQ |
| [추론 모델](reasoning.md) | o1, o3, R1, Extended Thinking, Test-time Compute Scaling |
