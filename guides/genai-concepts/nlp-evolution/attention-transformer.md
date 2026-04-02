# Seq2Seq, Attention, Transformer (2014~2017)

## Seq2Seq (Sequence-to-Sequence, Sutskever et al., 2014)

### 등장 배경

기계 번역에서는 입력 시퀀스(소스 언어)와 출력 시퀀스(타겟 언어)의 **길이가 다릅니다**. 기존 RNN/LSTM으로는 이를 처리하기 어려웠습니다.

### 구조: Encoder-Decoder

```
                    Context Vector (고정 길이)
                           ↓
입력: "I love you"     [Encoder LSTM]  →  c  →  [Decoder LSTM]     출력: "나는 너를 사랑해"
       ↑                                                               ↑
  하나씩 순서대로 읽기                                           하나씩 순서대로 생성
```

- **Encoder**: 입력 시퀀스를 하나의 고정 길이 벡터(Context Vector)로 압축
- **Decoder**: Context Vector를 받아 출력 시퀀스를 하나씩 생성

### 치명적 한계 — 정보 병목 (Information Bottleneck)

아무리 긴 입력이라도 **하나의 고정 크기 벡터** 로 압축해야 합니다. "1000단어짜리 문단을 256차원 벡터 하나에 담아라" — 당연히 정보가 손실됩니다.

```
"The agreement on the European Economic Area was signed in
Porto on 2 May 1992 and entered into force on 1 January 1994"

→ 이 전체 문장을 [0.12, -0.34, 0.56, ...] (256차원) 하나로 압축?
→ 번역할 때 "Porto"나 "1992" 같은 세부 정보를 놓침
```

---

## Bahdanau Attention (2015)

### 핵심 아이디어

Decoder가 출력을 생성할 때, **Encoder의 모든 은닉 상태를 직접 참조** 하도록 합니다. 고정 길이 Context Vector 대신, **매 출력 단계마다 입력의 어디를 볼지 동적으로 결정** 합니다.

```
Encoder 은닉 상태들:  h₁  h₂  h₃  h₄  h₅
                       ↑   ↑   ↑   ↑   ↑
Attention 가중치:     0.1 0.1 0.5 0.2 0.1  ← "이 단어를 번역할 때 h₃에 집중"
                                    ↓
                            가중 합 = context
                                    ↓
                            Decoder가 다음 단어 생성
```

| Seq2Seq (기존) | Seq2Seq + Attention |
|---------------|---------------------|
| 고정 Context Vector 1개 | 매 출력마다 다른 Context 생성 |
| 긴 문장에서 정보 손실 | 필요한 부분에 "주목"하여 정보 보존 |
| BLEU 26.75 (영-불 번역) | BLEU 36.15 — **35% 향상** |

{% hint style="info" %}
**Attention이 Transformer의 직접적 조상입니다.** Bahdanau Attention은 아직 RNN 위에 얹은 "보조 장치"였습니다. "Attention만으로 모델 전체를 만들면 어떨까?" — 이 질문의 답이 2017년의 Transformer입니다.
{% endhint %}

---

## Transformer의 탄생 (2017)

### "Attention Is All You Need"

2017년 Google의 Vaswani et al.이 발표한 이 논문은 NLP 역사의 분수령입니다. 핵심 주장: **RNN/LSTM 없이 Attention만으로 시퀀스를 처리할 수 있다.**

### 이전 기술의 한계를 어떻게 극복했는가

| 이전 기술의 한계 | Transformer의 해결책 |
|----------------|---------------------|
| RNN의 순차 처리 → 병렬화 불가 | **Self-Attention**: 모든 토큰 쌍을 동시에 계산 → GPU 완전 병렬화 |
| LSTM도 장거리에서 정보 손실 | **직접 참조**: 1번째 토큰과 1000번째 토큰도 한 번의 Attention으로 연결 |
| Seq2Seq의 고정 벡터 병목 | **모든 위치의 표현** 을 유지 — 압축하지 않음 |
| Bahdanau Attention은 RNN에 의존 | **Self-Attention만으로 전체 모델 구성**— RNN 완전 제거 |

### 성능 비교

| 모델 | WMT14 영-독 BLEU | 학습 시간 | 비고 |
|------|-----------------|----------|------|
| Seq2Seq + Attention (LSTM) | 25.16 | 수 주 | 순차 학습 |
| ConvS2S (CNN 기반) | 25.16 | 수 일 | 병렬화 일부 가능 |
| **Transformer** | **28.4** | **12시간**(8 GPU) | 완전 병렬화 |

{% hint style="success" %}
Transformer는 성능과 학습 속도를 **동시에** 크게 개선했습니다. 이것이 모든 후속 LLM이 Transformer를 기반으로 삼는 이유입니다.
{% endhint %}

### 왜 Google이 Transformer를 만들었는가

Transformer의 탄생은 순수한 학술적 호기심이 아니라, **비즈니스 니즈** 에서 출발했습니다.

2016년 Google은 통계 기반 번역에서 LSTM 기반 신경망 번역(GNMT)으로 전환하며 큰 성능 향상을 이뤘습니다. 하지만 GNMT에는 근본적 한계가 있었습니다.

```
Google 번역의 LSTM 기반 문제:
  1. 긴 문장(30단어 이상)에서 번역 품질 급격히 저하
  2. 한 문장을 번역하는 데 순차 처리 → 속도가 느림
  3. GPU를 아무리 추가해도 병렬화가 안 되어 속도 개선에 한계

하루 1,430억 단어를 번역하는 Google에게 이 속도는 비용 문제이기도 했습니다.
```

Google 연구진이 해결해야 했던 두 가지 요구사항:

| 요구사항 | 이유 | 기존 기술의 한계 |
|---------|------|----------------|
| **병렬화** | 수십억 건의 번역 요청을 처리해야 함 | LSTM은 순차 처리 — GPU 병렬화 불가 |
| **장거리 의존성** | 법률/기술 문서의 긴 문장 번역 품질 | LSTM도 수십 단어 이상에서 정보 손실 |

Attention은 장거리 의존성을 해결했지만 여전히 RNN 위에서 작동했습니다. "Attention은 좋은데, RNN이 병목이다. Attention만으로 모델을 만들면 두 문제를 동시에 해결할 수 있지 않을까?" — 이것이 "Attention Is All You Need"의 핵심 아이디어입니다.

{% hint style="info" %}
**비즈니스가 기술 혁신을 이끈 사례**: Transformer는 "학문적으로 흥미로운 구조"가 아니라, Google 번역의 **실용적 병목** 을 해결하기 위해 탄생했습니다. 이처럼 가장 영향력 있는 기술 혁신은 종종 현실의 구체적 문제에서 출발합니다.
{% endhint %}

### Transformer 이후 세상이 바뀐 3가지

Transformer는 단순히 "더 좋은 번역 모델"이 아니었습니다. NLP와 AI 전체의 판도를 바꿨습니다.

**1) 학습 속도 100배 향상 → 모델 크기 100배 증가 가능**

RNN/LSTM은 순차 처리 때문에 GPU를 추가해도 학습 속도가 비례하여 증가하지 않았습니다. Transformer의 완전 병렬화는 GPU를 추가한 만큼 학습 속도가 향상됩니다.

```
동일 데이터 기준 학습 시간:
  LSTM 기반 (순차):     수 주 ~ 수 개월
  Transformer (병렬):   수 시간 ~ 수 일

→ 같은 컴퓨팅 예산으로 100배 큰 모델을 학습할 수 있게 됨
→ GPT-2(1.5B), GPT-3(175B), PaLM(540B)이 현실적으로 가능해진 이유
```

**2) 사전학습 패러다임(BERT/GPT)의 탄생**

Transformer의 효율적 학습이 없었다면, 수천억 토큰으로 대규모 사전학습을 하는 것은 비용적으로 불가능했습니다. BERT와 GPT는 모두 Transformer 위에 세워진 건물이며, 그 건물의 기반은 **병렬 학습 가능성** 입니다.

**3) NLP 이외 분야로의 확장**

Transformer의 Self-Attention은 "시퀀스"라면 무엇이든 처리할 수 있습니다. 이미지도, 단백질 구조도, 음악도 시퀀스로 표현할 수 있습니다.

| 분야 | 모델 | 핵심 |
|------|------|------|
| **컴퓨터 비전** | Vision Transformer (ViT, 2020) | 이미지를 패치 시퀀스로 처리 → CNN을 대체하기 시작 |
| **단백질 구조 예측** | AlphaFold 2 (2021) | 아미노산 시퀀스 간 Attention → 단백질 3D 구조 예측 |
| **음성 인식** | Whisper (2022) | 오디오를 스펙트로그램 시퀀스로 처리 |
| **멀티모달** | GPT-4V, Gemini (2023~) | 텍스트 + 이미지를 동일한 Transformer로 처리 |

{% hint style="warning" %}
**Transformer의 범용성**: Transformer가 NLP만의 기술이 아니라 **범용 시퀀스 처리 아키텍처** 로 확장된 것은, 원래 설계 의도를 넘어선 결과입니다. 이는 "좋은 아키텍처는 원래 문제를 넘어 일반화된다"는 AI 연구의 중요한 교훈입니다.
{% endhint %}
