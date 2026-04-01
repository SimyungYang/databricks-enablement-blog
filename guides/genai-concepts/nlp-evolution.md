# NLP에서 LLM까지: 언어 모델의 발전사

현대 LLM(Large Language Model)은 하루아침에 탄생하지 않았습니다. 수십 년에 걸친 자연어처리(NLP) 연구의 축적 위에 서 있습니다. 이 가이드는 **규칙 기반 시스템부터 Transformer까지**, 각 기술이 왜 등장했고, 어떤 문제를 해결했으며, 어떤 한계가 다음 혁신을 이끌었는지를 전문가 수준으로 정리합니다.

{% hint style="info" %}
**학습 목표**
- Transformer 이전 NLP 기술의 발전 흐름과 각 단계의 핵심 돌파구를 설명할 수 있다
- 각 모델의 등장 배경, 해결한 문제, 남은 한계를 구분할 수 있다
- 현대 LLM이 왜 Transformer 기반인지 역사적 맥락에서 이해한다
- 고객에게 "AI가 어떻게 여기까지 왔는지"를 체계적으로 설명할 수 있다
{% endhint %}

---

## 한눈에 보는 NLP 발전 타임라인

| 시기 | 패러다임 | 대표 기술 | 핵심 돌파구 | 치명적 한계 |
|------|---------|----------|------------|-----------|
| 1950~1990 | 규칙 기반 | ELIZA, 전문가 시스템 | 구조화된 언어 처리 | 규칙 수작업, 확장 불가 |
| 1990~2000 | 통계적 NLP | N-gram, HMM, TF-IDF | 데이터에서 패턴 학습 | 의미 이해 불가, 희소성 |
| 2003 | 신경망 언어 모델 | NNLM (Bengio) | 단어를 벡터로 표현 | 학습 속도 느림 |
| 2013~2014 | 분산 표현 | Word2Vec, GloVe | 효율적 단어 임베딩 | 다의어 처리 불가 |
| 2014~2015 | 시퀀스 모델링 | RNN, LSTM, GRU | 가변 길이 시퀀스 처리 | 장거리 의존성, 병렬화 불가 |
| 2014 | 시퀀스-투-시퀀스 | Seq2Seq | 입출력 길이 독립적 | 고정 길이 벡터 병목 |
| 2015 | 어텐션 메커니즘 | Bahdanau Attention | 입력 전체를 동적 참조 | 여전히 순차 처리 |
| 2017 | **Transformer** | Self-Attention | 완전 병렬화 + 장거리 의존성 해결 | 계산량 O(N²) |
| 2018~ | **사전학습 시대** | BERT, GPT, T5 | 범용 언어 이해/생성 | 대규모 컴퓨팅 필요 |

---

## 1. 규칙 기반 NLP (1950~1990년대)

### 등장 배경

컴퓨터가 처음 등장했을 때, 연구자들은 **인간이 정한 문법 규칙**으로 언어를 처리할 수 있다고 믿었습니다. Noam Chomsky의 형식 문법(Formal Grammar) 이론이 이 시기 NLP의 이론적 기반이었습니다.

### 대표 시스템

| 시스템 | 연도 | 개발자 | 목적 | 작동 방식 |
|--------|------|--------|------|----------|
| **ELIZA** | 1966 | Weizenbaum (MIT) | 심리 상담 시뮬레이션 | 패턴 매칭 + 규칙 기반 응답 |
| **SHRDLU** | 1971 | Winograd (MIT) | 가상 세계 조작 | 문법 파싱 + 의미 추론 |
| **전문가 시스템** | 1970~80 | 다수 | 의료 진단, 법률 자문 | if-then 규칙 체인 |

**ELIZA 작동 예시:**

```
사용자: "나는 어머니가 걱정돼요"
규칙:  "나는 {X}가 걱정돼요" → "{X}에 대해 더 말해주세요"
ELIZA: "어머니에 대해 더 말해주세요"
```

### 성과와 한계

| 성과 | 한계 |
|------|------|
| 제한된 도메인에서 높은 정확도 | 규칙을 **수작업**으로 작성해야 함 |
| 명확한 해석 가능성 (왜 이 답인지 추적 가능) | 새로운 도메인마다 전부 다시 구축 |
| 표준화된 형식의 입력 처리에 강함 | 자연어의 **모호성, 비문, 은어**를 처리 못함 |
| | 규칙 수가 수만 개를 넘으면 **관리 불가능** |

{% hint style="warning" %}
**교훈**: "언어는 규칙으로 정의할 수 있다"는 가정 자체가 틀렸습니다. 자연어는 예외가 규칙보다 많습니다. 이 깨달음이 통계적 접근의 시작점이 됩니다.
{% endhint %}

---

## 2. 통계적 NLP (1990~2000년대)

### 등장 배경

규칙 기반의 한계를 목격한 연구자들은 발상을 전환합니다: **규칙을 사람이 쓰는 대신, 데이터에서 통계적 패턴을 학습**하자. 인터넷의 등장으로 대량의 텍스트 데이터가 확보 가능해지면서, 이 접근이 실용적이 됩니다.

### 핵심 기술

#### N-gram 언어 모델

**N-gram**은 연속된 N개의 단어 조합의 출현 빈도를 세어, 다음 단어의 확률을 추정하는 모델입니다.

```
"오늘 날씨가" 다음에 올 단어 확률:
  P("좋다" | "오늘 날씨가") = 0.35  ← 학습 데이터에서 35% 빈도
  P("덥다" | "오늘 날씨가") = 0.20
  P("나쁘다" | "오늘 날씨가") = 0.15
```

| N | 이름 | 예시 | 특징 |
|---|------|------|------|
| 1 | Unigram | "날씨" | 단어 독립 — 문맥 무시 |
| 2 | Bigram | "날씨가 좋다" | 직전 1단어만 참고 |
| 3 | Trigram | "오늘 날씨가 좋다" | 직전 2단어 참고 |

**한계 — 데이터 희소성 (Sparsity)**:
- N이 커질수록 조합 수가 폭발적으로 증가 (어휘 V개 → V^N 조합)
- 학습 데이터에 한 번도 등장하지 않은 조합은 확률 0 → 실제로는 가능한 문장을 "불가능"으로 판단
- Smoothing(라플라스, Kneser-Ney 등)으로 완화하지만, 근본적 해결은 불가

#### TF-IDF (Term Frequency - Inverse Document Frequency)

**문서 검색**과 **텍스트 분류**를 위한 단어 가중치 기법입니다.

```
TF-IDF(단어, 문서) = TF(단어, 문서) × IDF(단어)

TF  = 해당 문서에서 단어가 나온 횟수 / 총 단어 수
IDF = log(전체 문서 수 / 해당 단어가 포함된 문서 수)
```

**핵심 아이디어**: 특정 문서에서 자주 나오지만(TF 높음), 전체 문서에서는 드문 단어(IDF 높음)가 그 문서를 가장 잘 대표합니다.

| 단어 | TF (문서 A) | IDF | TF-IDF | 해석 |
|------|------------|-----|--------|------|
| "Databricks" | 0.05 | 3.2 | 0.16 | 이 문서의 핵심 주제 |
| "데이터" | 0.08 | 0.3 | 0.024 | 너무 흔한 단어 — 구별력 낮음 |
| "은/는/이/가" | 0.12 | 0.01 | 0.0012 | 조사 — 의미 없음 |

**활용**: 검색 엔진 랭킹, 문서 분류, 키워드 추출 → 오늘날에도 BM25(TF-IDF 발전형)로 **Elasticsearch, Databricks Vector Search 하이브리드 검색**에서 현역으로 사용

#### Hidden Markov Model (HMM)

**순차적 데이터**에서 숨겨진 상태를 추론하는 확률 모델입니다. NLP에서는 **품사 태깅(POS Tagging)**과 **개체명 인식(NER)**에 핵심적으로 사용되었습니다.

```
관측:    "나는    회사에서   점심을   먹었다"
숨겨진:  대명사   명사       명사     동사    ← HMM이 추론
```

### 성과와 한계

| 성과 | 한계 |
|------|------|
| 규칙 없이 데이터에서 자동 학습 | 단어를 **이산 기호**로 취급 — "왕"과 "임금"이 관련 없음 |
| 검색, 분류, 번역 품질 대폭 향상 | **의미적 유사성**을 전혀 포착 못함 |
| Google 번역 초기 버전의 기반 | N-gram의 고차원 희소성 문제 |
| 대규모 코퍼스 활용 가능 | 문맥에 따른 단어 의미 변화 처리 불가 |

{% hint style="info" %}
**현재까지 살아있는 기술**: TF-IDF의 발전형인 **BM25**는 2025년 현재도 검색 시스템의 핵심입니다. Databricks Vector Search의 하이브리드 검색도 BM25 + 벡터 검색을 결합합니다. 기초 기술이 완전히 사라지는 것이 아니라, 새로운 기술과 결합되어 발전합니다.
{% endhint %}

---

## 3. 단어 임베딩 혁명 (2003~2014)

### 등장 배경 — "단어를 숫자로 표현하는 방법"의 진화

통계적 NLP의 가장 큰 한계는 단어를 **이산적 기호(discrete symbol)**로 취급한 것입니다. "고양이"와 "강아지"는 의미적으로 가까운데, 컴퓨터에게는 완전히 다른 ID일 뿐이었습니다.

```
One-Hot Encoding (기존):
  고양이 = [1, 0, 0, 0, 0, ...]   ← 5만 차원
  강아지 = [0, 1, 0, 0, 0, ...]   ← 완전히 다른 벡터, 유사도 = 0

Distributed Representation (목표):
  고양이 = [0.2, 0.8, -0.1, 0.5]   ← 저차원, 의미 내포
  강아지 = [0.3, 0.7, -0.2, 0.6]   ← 유사한 벡터, 유사도 ≈ 0.95
```

### NNLM — Neural Network Language Model (Bengio, 2003)

Yoshua Bengio의 2003년 논문 "A Neural Probabilistic Language Model"은 **단어를 저차원 연속 벡터(임베딩)**로 표현하는 아이디어를 최초로 실용화했습니다.

| 항목 | 내용 |
|------|------|
| **핵심 아이디어** | 단어마다 학습 가능한 벡터를 부여하고, 신경망으로 다음 단어를 예측 |
| **혁신** | 비슷한 문맥에서 등장하는 단어는 비슷한 벡터를 갖게 됨 |
| **한계** | 학습이 매우 느림 (대규모 데이터 처리 어려움) |

### Word2Vec (Mikolov et al., Google, 2013)

NLP 역사상 가장 영향력 있는 논문 중 하나입니다. **단순한 얕은 신경망**으로 고품질 단어 임베딩을 **매우 빠르게** 학습할 수 있음을 보여주었습니다.

#### 두 가지 학습 방식

| 방식 | 원리 | 예시 |
|------|------|------|
| **CBOW** (Continuous Bag of Words) | 주변 단어들로 가운데 단어를 예측 | "오늘 ___ 좋다" → "날씨가" |
| **Skip-gram** | 가운데 단어로 주변 단어들을 예측 | "날씨가" → "오늘", "좋다" |

#### 놀라운 발견 — 벡터 산술

```
king - man + woman ≈ queen
Paris - France + Korea ≈ Seoul
```

단어 벡터 사이의 덧셈/뺄셈으로 **의미적 관계**가 포착된다는 사실은 큰 충격이었습니다. 이는 임베딩이 단순한 연관성이 아닌, 추상적 의미 구조를 학습했다는 증거입니다.

### GloVe (Pennington et al., Stanford, 2014)

**Global Vectors for Word Representation**. Word2Vec이 로컬 문맥(주변 N개 단어)만 보는 반면, GloVe는 **전체 코퍼스의 동시 출현 행렬(co-occurrence matrix)**을 활용합니다.

| 비교 | Word2Vec | GloVe |
|------|---------|-------|
| 학습 방식 | 예측 기반 (predictive) | 통계 기반 (count-based) |
| 활용 정보 | 로컬 문맥 윈도우 | 전체 코퍼스 통계 |
| 속도 | 대규모 코퍼스에서 빠름 | 행렬 분해 한 번으로 학습 |
| 결과 품질 | 비슷한 수준 | 비슷한 수준 |

### 성과와 한계

| 성과 | 한계 |
|------|------|
| 단어를 의미 있는 벡터로 표현 (NLP의 패러다임 전환) | **다의어 처리 불가**: "배" → 과일? 선박? 신체 부위? 하나의 벡터만 가짐 |
| 전이 학습의 시작 — 사전학습된 임베딩을 다운스트림 태스크에 활용 | **문장/문서 수준 표현 부재**: 단어 벡터의 단순 평균은 의미를 정확히 담지 못함 |
| 후속 모든 NLP 연구의 기반이 됨 | **문맥 무시**: 동일 단어는 어떤 문장에서든 같은 벡터 |

{% hint style="warning" %}
**다의어 문제의 심각성**: "나는 배가 고프다" vs "나는 배를 타고 갔다" — Word2Vec에서 "배"는 두 문장 모두에서 동일한 벡터입니다. 이 문제를 해결한 것이 바로 **문맥 임베딩(Contextual Embedding)**, 즉 ELMo → BERT로 이어지는 흐름입니다.
{% endhint %}

### 서브워드 토큰화 — BPE (Byte Pair Encoding)

Word2Vec과 GloVe는 강력했지만, 한 가지 고질적인 문제가 남아 있었습니다: **OOV(Out-of-Vocabulary) 문제**. 학습 시 한 번도 보지 못한 단어는 처리할 수 없었습니다.

```
학습 데이터에 있는 단어:  happy, unhappy, happiness
학습 데이터에 없는 단어:  unhappiness → ??? (OOV — 벡터 없음!)

문제: 신조어, 전문 용어, 오타 등이 모두 처리 불가
```

#### BPE의 핵심 원리 (Sennrich et al., 2016)

BPE는 **문자(character) 수준에서 시작**하여, 가장 빈번한 문자 쌍을 **반복적으로 병합**해 나가는 방식입니다.

```
1단계: 모든 단어를 문자로 분해
   "unhappiness" → [u, n, h, a, p, p, i, n, e, s, s]

2단계: 가장 빈번한 문자 쌍을 병합 (반복)
   (s, s) → ss    [u, n, h, a, p, p, i, n, e, ss]
   (p, p) → pp    [u, n, h, a, pp, i, n, e, ss]
   (h, a) → ha    [u, n, ha, pp, i, n, e, ss]
   (ha, pp) → happ [u, n, happ, i, n, e, ss]
   (n, e) → ne    [u, n, happ, i, ne, ss]
   (ne, ss) → ness [u, n, happ, i, ness]
   (happ, i) → happi [u, n, happi, ness]
   (u, n) → un    [un, happi, ness]

최종 결과: "unhappiness" → ["un", "happi", "ness"]
```

각 서브워드 조각("un", "happi", "ness")은 **의미를 가진 단위**입니다. "un-"은 부정, "happi"는 행복, "-ness"는 명사화 접미사.

#### 한국어에서의 BPE

```
"데이터브릭스" → ["데이터", "브", "릭", "스"]  또는  ["데이터", "브릭스"]
"데이터엔지니어" → ["데이터", "엔지니어"]  ← "데이터" 토큰 재활용!

영어 대비 한국어의 차이:
  "Databricks" → ["Data", "bricks"]       ← 2토큰
  "데이터브릭스" → ["데이터", "브", "릭", "스"] ← 4토큰 (토큰 효율성 낮음)
```

#### BPE 변형과 현재

| 알고리즘 | 개발사 | 특징 | 사용 모델 |
|---------|--------|------|----------|
| **BPE** | Sennrich et al. | 빈도 기반 병합 | GPT-2, GPT-3, GPT-4 |
| **WordPiece** | Google | 우도(likelihood) 기반 병합 | BERT, DistilBERT |
| **SentencePiece** | Google | 언어 독립적, 공백도 토큰화 | T5, Llama, ALBERT |
| **Unigram** | Kudo (2018) | 확률적 서브워드 선택 | XLNet, mBART |

{% hint style="success" %}
**현대 LLM과의 연결**: 오늘날 **모든 주요 LLM**(GPT-4, Claude, Llama, Gemini)은 BPE 또는 그 변형을 사용합니다. Word2Vec 시대의 "단어 단위" 처리에서 BPE의 "서브워드 단위" 처리로의 전환은, 단어 임베딩 시대와 Transformer 시대를 잇는 중요한 다리입니다. OOV 문제 해결 없이는 범용 언어 모델이 불가능했을 것입니다.
{% endhint %}

---

## 4. 순환 신경망의 시대 (2014~2017)

### RNN (Recurrent Neural Network)

#### 등장 배경

Word2Vec은 단어 수준의 표현은 해결했지만, **문장이나 문서 전체**를 이해하려면 단어의 **순서(sequence)**를 처리할 수 있는 모델이 필요했습니다.

#### 핵심 원리

RNN은 **이전 시간 단계의 출력을 다음 시간 단계의 입력에 연결**하는 순환 구조입니다:

```
입력:  x₁("나는") → x₂("오늘") → x₃("회사에") → x₄("간다")
              ↓              ↓              ↓             ↓
은닉:  h₁ ────────→ h₂ ────────→ h₃ ────────→ h₄
              ↓              ↓              ↓             ↓
출력:  y₁            y₂            y₃            y₄
```

각 시간 단계에서:
```
h_t = tanh(W_hh · h_{t-1} + W_xh · x_t + b)
```

이전 은닉 상태 `h_{t-1}`이 현재 계산에 참여하므로, 이론적으로는 **과거의 모든 정보**를 기억할 수 있습니다.

#### 치명적 문제 — 기울기 소실 (Vanishing Gradient)

실제로는 역전파(Backpropagation) 과정에서 기울기가 시간을 거슬러 올라갈수록 **기하급수적으로 작아집니다**:

```
문장: "서울에서 태어나고 부산에서 자란 김철수는 ... (50단어) ... 한국어를 유창하게 말한다"

RNN이 "한국어"를 예측할 때, "서울"이라는 단서는 50단계 전에 있음
→ 기울기가 50번 곱해지면서 0에 수렴 → "서울" 정보가 학습에 반영되지 않음
```

### LSTM (Long Short-Term Memory, Hochreiter & Schmidhuber, 1997)

RNN의 기울기 소실 문제를 해결하기 위해 고안된 아키텍처입니다. 실제로 널리 활용된 것은 2014년 이후입니다.

#### 핵심 아이디어 — 게이트 메커니즘

LSTM은 **세 개의 게이트**로 정보의 흐름을 정교하게 제어합니다:

| 게이트 | 역할 | 비유 |
|--------|------|------|
| **Forget Gate** (망각 게이트) | 이전 정보 중 버릴 것을 결정 | 불필요한 기억을 삭제하는 기능 |
| **Input Gate** (입력 게이트) | 새로운 정보 중 저장할 것을 결정 | 중요한 새 정보만 기억에 추가 |
| **Output Gate** (출력 게이트) | 현재 출력에 사용할 정보를 결정 | 상황에 맞는 기억만 꺼내 사용 |

```
Cell State (장기 기억): ──────────────────────→ (고속도로처럼 정보가 직통으로 전달)
                    ↑ forget    ↑ input
                    게이트       게이트         ↓ output 게이트
Hidden State:      h_{t-1} ──────────────→ h_t (단기 기억/출력)
```

{% hint style="success" %}
**비유**: RNN이 "메모장 한 장"에 모든 것을 적다 보니 앞 내용이 지워지는 것이라면, LSTM은 **서류 캐비닛**입니다. 어떤 서류를 보관하고(Input Gate), 어떤 서류를 폐기하고(Forget Gate), 어떤 서류를 꺼낼지(Output Gate)를 판단합니다.
{% endhint %}

### GRU (Gated Recurrent Unit, Cho et al., 2014)

LSTM의 **경량화 버전**입니다. 세 개의 게이트를 **두 개(Reset, Update)**로 줄여 더 빠른 학습을 가능하게 했습니다.

| 비교 | LSTM | GRU |
|------|------|-----|
| 게이트 수 | 3개 (Forget, Input, Output) | 2개 (Reset, Update) |
| 파라미터 수 | 더 많음 | ~25% 적음 |
| 학습 속도 | 느림 | 빠름 |
| 성능 | 긴 시퀀스에서 약간 우세 | 짧은 시퀀스에서 동등 또는 우세 |
| 실무 선택 | 복잡한 의존성이 중요한 작업 | 빠른 실험, 리소스 제한 환경 |

### CNN 기반 NLP — TextCNN (Yoon Kim, 2014)

RNN/LSTM이 시퀀스 처리의 주류로 자리잡던 시기에, **합성곱 신경망(CNN)**으로도 텍스트를 효과적으로 처리할 수 있다는 연구가 등장합니다. 컴퓨터 비전에서 이미지 패턴을 포착하던 CNN을 NLP에 적용한 것입니다.

#### 핵심 아이디어

TextCNN은 다양한 크기의 **1D 합성곱 필터**를 텍스트 위로 슬라이딩하여, **로컬 N-gram 패턴**을 포착합니다.

```
입력: "이 영화는 정말 재미있다"
      [이] [영화는] [정말] [재미있다]
       ↓      ↓      ↓      ↓
      임베딩 벡터들 (행렬)

필터 크기 2: [이, 영화는] [영화는, 정말] [정말, 재미있다]  ← bigram 패턴
필터 크기 3: [이, 영화는, 정말] [영화는, 정말, 재미있다]   ← trigram 패턴

→ 각 필터의 최대값(Max Pooling) → 최종 분류
```

#### RNN vs CNN for NLP

| 비교 항목 | RNN/LSTM | TextCNN |
|----------|----------|---------|
| **처리 방식** | 순차적 (한 토큰씩) | **병렬적** (모든 필터 동시 적용) |
| **학습 속도** | 느림 (순차 의존성) | **빠름** (GPU 병렬화 용이) |
| **장거리 의존성** | LSTM으로 부분 해결 | **약함** — 필터 크기 내의 로컬 패턴만 포착 |
| **강점 태스크** | 번역, 텍스트 생성, 요약 | **텍스트 분류, 감성 분석** |
| **시퀀스 생성** | 가능 (Decoder로 활용) | 부적합 — 순서 정보 약함 |

{% hint style="info" %}
**TextCNN의 의의**: RNN만이 텍스트를 처리할 수 있다는 고정관념을 깨고, **분류 태스크에서는 CNN이 더 빠르고 동등한 성능**을 보일 수 있음을 입증했습니다. 다만 CNN은 **시퀀스 생성(번역, 요약)**에는 적합하지 않아, RNN이 생성 태스크에서는 주류를 유지했습니다. 이 "병렬 처리가 가능한 모델이 더 효율적"이라는 통찰은 이후 **Transformer의 Self-Attention**으로 완성됩니다.
{% endhint %}

### 성과와 공통 한계

**성과**:
- 기계 번역, 감성 분석, 음성 인식 등에서 획기적 성능 향상
- Google 번역이 2016년 통계 기반에서 LSTM 기반 신경망 번역으로 전환
- 가변 길이 시퀀스를 자연스럽게 처리

**공통 한계**:
| 한계 | 설명 | 영향 |
|------|------|------|
| **순차 처리** | 토큰을 하나씩 순서대로 처리해야 함 | GPU 병렬 처리 불가 → 학습 속도 느림 |
| **장거리 의존성** | LSTM도 수백 토큰 이상에서는 정보 손실 | 긴 문서 처리에 한계 |
| **고정 차원 은닉 상태** | 아무리 긴 문장도 하나의 고정 크기 벡터에 압축 | 정보 병목 (bottleneck) |

---

## 5. Seq2Seq과 Attention의 등장 (2014~2016)

### Seq2Seq (Sequence-to-Sequence, Sutskever et al., 2014)

#### 등장 배경

기계 번역에서는 입력 시퀀스(소스 언어)와 출력 시퀀스(타겟 언어)의 **길이가 다릅니다**. 기존 RNN/LSTM으로는 이를 처리하기 어려웠습니다.

#### 구조: Encoder-Decoder

```
                    Context Vector (고정 길이)
                           ↓
입력: "I love you"     [Encoder LSTM]  →  c  →  [Decoder LSTM]     출력: "나는 너를 사랑해"
       ↑                                                               ↑
  하나씩 순서대로 읽기                                           하나씩 순서대로 생성
```

- **Encoder**: 입력 시퀀스를 하나의 고정 길이 벡터(Context Vector)로 압축
- **Decoder**: Context Vector를 받아 출력 시퀀스를 하나씩 생성

#### 치명적 한계 — 정보 병목 (Information Bottleneck)

아무리 긴 입력이라도 **하나의 고정 크기 벡터**로 압축해야 합니다. "1000단어짜리 문단을 256차원 벡터 하나에 담아라" — 당연히 정보가 손실됩니다.

```
"The agreement on the European Economic Area was signed in
Porto on 2 May 1992 and entered into force on 1 January 1994"

→ 이 전체 문장을 [0.12, -0.34, 0.56, ...] (256차원) 하나로 압축?
→ 번역할 때 "Porto"나 "1992" 같은 세부 정보를 놓침
```

### Bahdanau Attention (2015)

#### 핵심 아이디어

Decoder가 출력을 생성할 때, **Encoder의 모든 은닉 상태를 직접 참조**하도록 합니다. 고정 길이 Context Vector 대신, **매 출력 단계마다 입력의 어디를 볼지 동적으로 결정**합니다.

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

## 6. Transformer의 탄생 (2017)

### "Attention Is All You Need"

2017년 Google의 Vaswani et al.이 발표한 이 논문은 NLP 역사의 분수령입니다. 핵심 주장: **RNN/LSTM 없이 Attention만으로 시퀀스를 처리할 수 있다.**

### 이전 기술의 한계를 어떻게 극복했는가

| 이전 기술의 한계 | Transformer의 해결책 |
|----------------|---------------------|
| RNN의 순차 처리 → 병렬화 불가 | **Self-Attention**: 모든 토큰 쌍을 동시에 계산 → GPU 완전 병렬화 |
| LSTM도 장거리에서 정보 손실 | **직접 참조**: 1번째 토큰과 1000번째 토큰도 한 번의 Attention으로 연결 |
| Seq2Seq의 고정 벡터 병목 | **모든 위치의 표현**을 유지 — 압축하지 않음 |
| Bahdanau Attention은 RNN에 의존 | **Self-Attention만으로 전체 모델 구성** — RNN 완전 제거 |

### 성능 비교

| 모델 | WMT14 영-독 BLEU | 학습 시간 | 비고 |
|------|-----------------|----------|------|
| Seq2Seq + Attention (LSTM) | 25.16 | 수 주 | 순차 학습 |
| ConvS2S (CNN 기반) | 25.16 | 수 일 | 병렬화 일부 가능 |
| **Transformer** | **28.4** | **12시간** (8 GPU) | 완전 병렬화 |

{% hint style="success" %}
Transformer는 성능과 학습 속도를 **동시에** 크게 개선했습니다. 이것이 모든 후속 LLM이 Transformer를 기반으로 삼는 이유입니다.
{% endhint %}

---

## 7. 사전학습 시대의 개막 (2018~)

### ULMFiT — 사전학습-파인튜닝 패러다임의 원형 (Howard & Ruder, 2018)

Transformer 기반 모델들이 등장하기 직전, Jeremy Howard와 Sebastian Ruder는 **ULMFiT(Universal Language Model Fine-tuning)**을 통해 "사전학습 → 파인튜닝" 패러다임을 최초로 실용적으로 입증했습니다.

#### 3단계 전이 학습 프로세스

| 단계 | 이름 | 내용 | 데이터 |
|------|------|------|--------|
| 1단계 | **General LM Pre-training** | 대규모 일반 텍스트(Wikipedia 등)로 언어 모델 학습 | 수백만 문서 (라벨 불필요) |
| 2단계 | **Target Domain Fine-tuning** | 목표 도메인 텍스트로 언어 모델 추가 학습 | 도메인 문서 (라벨 불필요) |
| 3단계 | **Task Fine-tuning** | 실제 분류 태스크용 라벨 데이터로 최종 학습 | **소량 라벨 데이터 (100개도 가능!)** |

```
1단계: Wikipedia로 "영어란 이런 것" 학습 (범용 언어 이해)
        ↓
2단계: IMDb 영화 리뷰 텍스트로 "리뷰란 이런 것" 추가 학습 (도메인 적응)
        ↓
3단계: "긍정/부정" 라벨 100개로 감성 분류 학습 → 기존 최고 성능 달성!
```

#### 왜 중요한가

| 기존 접근 | ULMFiT |
|----------|--------|
| 각 태스크마다 처음부터 모델 학습 | **사전학습 모델을 재활용** — 전이 학습 |
| 대량의 라벨 데이터 필요 (수만~수십만) | **라벨 100개로도** 최고 성능 달성 |
| 태스크마다 아키텍처 설계 필요 | 동일한 프로세스를 모든 텍스트 분류에 적용 |

{% hint style="success" %}
**ULMFiT의 역사적 의의**: ULMFiT은 컴퓨터 비전의 ImageNet 사전학습 → 파인튜닝 패러다임을 NLP에 처음으로 성공적으로 이식했습니다. 이 "사전학습 → 파인튜닝" 공식은 직후 등장한 **GPT-1**(2018.06)과 **BERT**(2018.10)에 직접적인 영감을 주었으며, 현재까지 모든 LLM의 기본 패러다임으로 자리잡았습니다.
{% endhint %}

Transformer의 등장 이후, NLP는 **사전학습(Pre-training) → 파인튜닝(Fine-tuning)** 패러다임으로 전환됩니다. 대규모 데이터로 범용 언어 이해를 학습한 뒤, 소량의 작업별 데이터로 특화시키는 방식입니다.

### Transformer 기반 모델의 세 계보

| 계보 | 구조 | 대표 모델 | 학습 목표 | 강점 |
|------|------|----------|----------|------|
| **Encoder-only** | Encoder만 사용 | BERT, RoBERTa | 마스킹된 단어 예측 (MLM) | 텍스트 이해, 분류, NER |
| **Decoder-only** | Decoder만 사용 | GPT 시리즈, Llama, Claude | 다음 토큰 예측 (CLM) | 텍스트 생성, 대화, 코드 |
| **Encoder-Decoder** | 둘 다 사용 | T5, BART | 손상된 텍스트 복원 | 번역, 요약, Q&A |

### 주요 이정표

| 모델 | 연도 | 개발사 | 파라미터 | 핵심 기여 |
|------|------|--------|----------|----------|
| **ELMo** | 2018.02 | Allen AI | 94M | 문맥 의존 임베딩 (양방향 LSTM 기반) |
| **ULMFiT** | 2018.01 | fast.ai | - | 사전학습→파인튜닝 패러다임 최초 실용화. 라벨 100개로 SOTA |
| **GPT-1** | 2018.06 | OpenAI | 117M | Transformer Decoder + 사전학습 |
| **BERT** | 2018.10 | Google | 340M | 양방향 Transformer Encoder + MLM |
| **GPT-2** | 2019.02 | OpenAI | 1.5B | 스케일링의 힘 입증, Zero-shot 가능성 |
| **T5** | 2019.10 | Google | 11B | 모든 NLP를 Text-to-Text로 통일 |
| **GPT-3** | 2020.06 | OpenAI | 175B | Few-shot 학습, 프롬프트 엔지니어링 시대 개막 |
| **ChatGPT** | 2022.11 | OpenAI | - | RLHF, 대화형 AI 대중화 |
| **GPT-4** | 2023.03 | OpenAI | 비공개 (MoE) | 멀티모달, 추론 능력 대폭 향상 |

{% hint style="info" %}
**ELMo의 중요성**: Word2Vec의 "하나의 단어 = 하나의 벡터" 한계를 깨고, **같은 단어라도 문맥에 따라 다른 벡터**를 생성한 최초의 모델입니다. 다만 LSTM 기반이라 느렸고, BERT가 Transformer로 이를 계승하면서 대체되었습니다.
{% endhint %}

### 스케일링 법칙과 대형 모델 경쟁

2020년 OpenAI의 Kaplan et al.은 **스케일링 법칙(Scaling Laws)**을 발견합니다. 모델의 성능(손실 함수 값)이 **모델 크기, 데이터 양, 컴퓨팅 자원**에 대해 **예측 가능한 거듭제곱 법칙(power law)**을 따른다는 것입니다.

```
Loss ∝ N^(-α)

N = 모델 파라미터 수
α ≈ 0.076 (경험적 상수)

즉, 파라미터를 10배 늘리면 → 손실이 일정하게 감소
    파라미터를 100배 늘리면 → 더 감소
    ... 예측 가능한 개선!
```

#### 스케일링 법칙이 가져온 변화

| 이전 | 이후 |
|------|------|
| "더 큰 모델이 좋을까?"는 실험해봐야 알았음 | **수학적으로 예측 가능** — 투자 대비 성능 향상을 사전 계산 |
| 모델 크기를 보수적으로 결정 | "더 크게, 더 많이"가 이론적으로 정당화 → GPT-3(175B), PaLM(540B) |
| 연구자 개인의 아키텍처 창의성이 핵심 | **컴퓨팅 자원 확보**가 경쟁력의 핵심으로 변화 |

{% hint style="warning" %}
**Chinchilla의 반론 (Hoffmann et al., Google DeepMind, 2022)**: 스케일링 법칙이 "무조건 크게"를 의미하지는 않습니다. Chinchilla 연구는 **모델 크기와 학습 데이터 양의 균형**이 중요하다는 것을 보여주었습니다. 70B 파라미터 모델이 1.4T 토큰으로 학습했을 때, 280B 파라미터 모델(Gopher)보다 더 좋은 성능을 달성했습니다. 핵심 교훈: **데이터 효율성**도 스케일링의 중요한 축입니다.
{% endhint %}

### RLHF: LLM을 "유용하게" 만드는 기술

사전학습만으로는 LLM이 "텍스트를 잘 이어쓰는 엔진"에 불과합니다. "수도가 어디인가요?"라고 물으면, 답 대신 비슷한 질문을 더 생성할 수도 있습니다. **사전학습 모델을 유용한 어시스턴트로 전환**한 것이 RLHF(Reinforcement Learning from Human Feedback)입니다.

#### 3단계 파이프라인

| 단계 | 이름 | 내용 | 비유 |
|------|------|------|------|
| 1단계 | **사전학습 (Pre-training)** | 인터넷 텍스트 수조 토큰으로 다음 단어 예측 학습 | 백과사전을 통째로 읽은 학생 |
| 2단계 | **SFT (Supervised Fine-Tuning)** | 인간이 작성한 (질문, 모범 답변) 쌍으로 미세 조정 | 선생님이 "이런 식으로 답하라"고 교육 |
| 3단계 | **RLHF** | 인간 선호도를 학습한 보상 모델로 PPO 강화학습 | 학생의 답을 채점하고 더 나은 답을 유도 |

#### RLHF 상세 과정

```
1. 보상 모델 학습:
   질문: "한국의 수도는?"
   답변 A: "서울입니다. 대한민국의 수도로, 한강이 도시를 관통합니다."
   답변 B: "한국 수도 서울 부산 대구 인천..."
   인간 평가: A > B → 보상 모델이 A에 높은 점수를 주도록 학습

2. PPO 강화학습:
   LLM이 답변 생성 → 보상 모델이 점수 산출 → 높은 점수를 받는 방향으로 LLM 업데이트
```

#### InstructGPT → ChatGPT

| 모델 | 연도 | 핵심 |
|------|------|------|
| **InstructGPT** | 2022.01 | RLHF를 GPT-3에 적용한 최초 논문. 1.3B InstructGPT가 175B GPT-3보다 **인간이 선호하는 답변** 생성 |
| **ChatGPT** | 2022.11 | InstructGPT 기법을 GPT-3.5에 적용 + 대화형 인터페이스 → **AI 대중화** |

{% hint style="success" %}
**RLHF의 핵심 의의**: 모델 크기를 키우는 것(스케일링)이 "똑똑함"을 개선했다면, RLHF는 "유용함"과 "안전함"을 개선했습니다. 이 두 축의 결합이 ChatGPT 모먼트를 만들었습니다.
{% endhint %}

{% hint style="info" %}
**DPO (Direct Preference Optimization)**: RLHF의 보상 모델 학습 + PPO 단계가 복잡하고 불안정하다는 문제를 해결하기 위해, Rafailov et al. (2023)이 제안한 방법입니다. 보상 모델 없이 **인간 선호도 데이터로 직접 LLM을 최적화**합니다. 수학적으로 RLHF와 동등하면서 구현이 훨씬 간단합니다. Meta의 Llama 2, Anthropic의 Claude 등 최신 모델에서 널리 채택되고 있습니다.
{% endhint %}

---

## 전체 발전 흐름 요약

각 기술이 이전 기술의 **어떤 한계**를 극복하며 등장했는지를 정리합니다:

```
규칙 기반 NLP
  │  한계: 규칙 수작업, 확장 불가
  ▼
통계적 NLP (N-gram, TF-IDF, HMM)
  │  한계: 의미 이해 불가, 단어를 이산 기호로 취급
  ▼
단어 임베딩 (Word2Vec, GloVe)
  │  한계: 다의어 처리 불가, 문맥 무시
  ▼
RNN / LSTM / GRU
  │  한계: 순차 처리 → 느림, 장거리 의존성 여전히 부족
  ▼
Seq2Seq + Attention
  │  한계: 여전히 RNN에 의존, 순차 처리
  ▼
Transformer (2017) ← "Attention만으로 충분하다"
  │  완전 병렬화 + 장거리 의존성 해결
  ▼
사전학습 LLM (BERT → GPT → Claude/Llama/...)
  │  대규모 사전학습 → 범용 언어 이해/생성
  ▼
현재: Agent, MCP, Multi-Modal, Reasoning 모델
```

---

## 현재 기술의 미해결 과제

Transformer와 LLM이 혁명적이지만, 아직 해결되지 않은 문제들이 있습니다:

| 과제 | 설명 | 연구 방향 |
|------|------|----------|
| **O(N²) 계산 복잡도** | 컨텍스트 윈도우가 2배 → 계산 4배 | Linear Attention, Ring Attention, Sparse Attention |
| **Hallucination** | 학습 패턴 기반 생성 → 사실과 다른 내용 | RAG, Grounding, Fact-checking |
| **추론 (Reasoning)** | 복잡한 논리적 사고에 여전히 취약 | Chain-of-Thought, o1/R1 추론 모델 |
| **지식 업데이트** | 학습 이후 새로운 정보 반영 불가 | RAG, Continual Learning |
| **다국어 편향** | 영어 중심 학습 → 한국어 등 성능 격차 | 다국어 사전학습, 한국어 특화 모델 |
| **비용** | 대규모 모델의 학습/추론 비용 | MoE, 양자화(Quantization), 증류(Distillation) |

---

## 고객이 자주 묻는 질문

{% hint style="info" %}
**Q: "AI가 갑자기 나타난 건가요?"**

아닙니다. AI와 NLP는 **70년 이상의 역사**를 가지고 있습니다. 1950년대 규칙 기반 시스템 → 1990년대 통계적 NLP → 2013년 Word2Vec → 2017년 Transformer → 2022년 ChatGPT로 이어지는 긴 축적의 결과입니다. ChatGPT가 "갑자기" 나타난 것이 아니라, 수십 년간의 연구가 임계점을 넘은 것입니다.
{% endhint %}

{% hint style="info" %}
**Q: "왜 지금 갑자기 AI가 핵심이 됐나요?"**

세 가지가 동시에 맞아떨어졌기 때문입니다:

| 요소 | 시기 | 기여 |
|------|------|------|
| **Transformer 아키텍처** | 2017 | 완전 병렬화로 대규모 학습 가능 |
| **스케일링 법칙** | 2020 | "더 크게 만들면 더 좋아진다"의 이론적 근거 |
| **RLHF** | 2022 | 텍스트 생성 엔진을 "유용한 어시스턴트"로 전환 |

Transformer만으로는 학술 논문 수준이었고, 스케일링만으로는 비용 정당화가 어려웠으며, RLHF 없이는 일반인이 쓸 수 없었습니다. **세 기술의 결합**이 ChatGPT 모먼트를 만들었습니다.
{% endhint %}

{% hint style="warning" %}
**Q: "한국어 AI가 영어보다 성능이 낮은 이유는?"**

두 가지 핵심 원인이 있습니다:

1. **학습 데이터 편향**: 대부분의 LLM 사전학습 데이터에서 영어가 80~90%를 차지합니다. 한국어 데이터는 전체의 1~3%에 불과합니다. 모델은 많이 본 언어를 더 잘 이해합니다.

2. **토큰화 효율성**: BPE 토크나이저는 영어 위주로 학습되어, 영어 "Hello"는 1토큰인 반면 "안녕하세요"는 3~5토큰으로 분절됩니다. 같은 의미를 전달하는 데 더 많은 토큰이 필요하면:
   - 동일 컨텍스트 윈도우에 더 적은 내용이 들어감
   - 추론 비용이 더 높아짐
   - 토큰 간 의미 연결이 어려워짐

이 때문에 한국어 특화 모델(예: HyperCLOVA, Solar)이나 다국어 균형 학습이 중요합니다.
{% endhint %}

---

## 연습 문제

1. 통계적 NLP에서 N-gram 모델의 "데이터 희소성" 문제가 무엇이며, Word2Vec은 이를 어떻게 해결했나요?
2. LSTM의 세 가지 게이트(Forget, Input, Output)의 역할을 "도서관 사서"에 비유하여 설명하세요.
3. Seq2Seq 모델의 "정보 병목" 문제가 무엇이며, Attention이 이를 어떻게 해결했나요?
4. Word2Vec에서 `king - man + woman ≈ queen`이 가능한 이유를 설명하세요.
5. Transformer가 RNN/LSTM을 대체한 핵심 이유 두 가지를 학습 속도와 성능 관점에서 설명하세요.
6. "배가 고프다"와 "배를 타고 갔다"에서 "배"를 다르게 처리할 수 있는 최초의 모델은 무엇이며, 이후 어떤 모델로 발전했나요?

---

## 참고 자료

- [Bengio et al., "A Neural Probabilistic Language Model" (2003)](https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf)
- [Mikolov et al., "Efficient Estimation of Word Representations in Vector Space" (2013)](https://arxiv.org/abs/1301.3781) — Word2Vec
- [Pennington et al., "GloVe: Global Vectors for Word Representation" (2014)](https://nlp.stanford.edu/pubs/glove.pdf)
- [Hochreiter & Schmidhuber, "Long Short-Term Memory" (1997)](https://www.bioinf.jku.at/publications/older/2604.pdf) — LSTM
- [Cho et al., "Learning Phrase Representations using RNN Encoder-Decoder" (2014)](https://arxiv.org/abs/1406.1078) — GRU
- [Sutskever et al., "Sequence to Sequence Learning with Neural Networks" (2014)](https://arxiv.org/abs/1409.3215) — Seq2Seq
- [Bahdanau et al., "Neural Machine Translation by Jointly Learning to Align and Translate" (2015)](https://arxiv.org/abs/1409.0473) — Attention
- [Vaswani et al., "Attention Is All You Need" (2017)](https://arxiv.org/abs/1706.03762) — Transformer
- [Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers" (2018)](https://arxiv.org/abs/1810.04805)
- [Peters et al., "Deep contextualized word representations" (2018)](https://arxiv.org/abs/1802.05365) — ELMo
- [Kim, "Convolutional Neural Networks for Sentence Classification" (2014)](https://arxiv.org/abs/1408.5882) — TextCNN
- [Sennrich et al., "Neural Machine Translation of Rare Words with Subword Units" (2016)](https://arxiv.org/abs/1508.07909) — BPE
- [Howard & Ruder, "Universal Language Model Fine-tuning for Text Classification" (2018)](https://arxiv.org/abs/1801.06146) — ULMFiT
- [Kaplan et al., "Scaling Laws for Neural Language Models" (2020)](https://arxiv.org/abs/2001.08361) — Scaling Laws
- [Hoffmann et al., "Training Compute-Optimal Large Language Models" (2022)](https://arxiv.org/abs/2203.15556) — Chinchilla
- [Ouyang et al., "Training language models to follow instructions with human feedback" (2022)](https://arxiv.org/abs/2203.02155) — InstructGPT / RLHF
- [Rafailov et al., "Direct Preference Optimization" (2023)](https://arxiv.org/abs/2305.18290) — DPO
