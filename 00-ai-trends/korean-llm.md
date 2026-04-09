# 한국어 LLM 및 다국어 AI 동향 (2026년 초 기준)

{% hint style="info" %}
**이 문서의 범위**: 한국어 특화 LLM, 중국계 모델의 한국어 지원, 한국어 NLP 기술 과제, 벤치마크, 정부 정책을 종합 분석합니다. 한국어 RAG 최적화 상세는 [한국어 RAG 최적화](../guides/rag/korean-nlp.md)를 참고하세요.
{% endhint %}

---

## 1. 개요

2026년 초 현재, 한국어 LLM 생태계는 **세 가지 축** 으로 빠르게 재편되고 있습니다.

1. **국내 기업의 자체 모델 고도화**: NAVER HyperCLOVA X, LG EXAONE, Upstage SOLAR 등
2. **글로벌 오픈소스 모델의 한국어 성능 급상승**: Qwen, DeepSeek, Llama 등
3. **MoE 아키텍처의 주류화**: K-EXAONE 236B, Qwen 3.5 397B 등

핵심 배경은 **토큰화 효율성 개선, 학습 데이터 다양화, MoE를 통한 비용 효율적 스케일링** 입니다.

---

## 2. 주요 한국 AI 기업별 동향

### 2.1 NAVER — HyperCLOVA X

NAVER는 한국어 LLM 시장의 선두주자로, **HyperCLOVA X** 시리즈를 CLOVA Studio API로 제공합니다. 모델 가중치를 공개하지 않는 폐쇄형 전략을 취하고 있습니다.

| 항목 | 내용 |
|------|------|
| **제공 방식** | NAVER Cloud CLOVA Studio API |
| **모델 공개** | 비공개 (가중치 미공개) |
| **강점** | 한국어 문화적 맥락 이해 (존비어, 관용 표현, 법률/의료 도메인) |
| **서비스** | NAVER 검색, 쇼핑, 뉴스 등 자사 서비스에 통합 |

### 2.2 LG AI Research — EXAONE 시리즈 (가장 주목할 행보)

#### K-EXAONE 236B (Active 23B) — 한국어 MoE 플래그십

K-EXAONE은 **한국어 최적화 MoE 아키텍처** 의 대표 모델입니다.

| 항목 | 스펙 |
|------|------|
| **전체/활성 파라미터** | 236B / 23B |
| **아키텍처** | Fine-grained MoE + Multi-Token Prediction |
| **Expert 구조** | 128 Expert 중 8개 활성 + 1 Shared Expert |
| **컨텍스트** | 256K 토큰 |
| **어휘** | 150K (SuperBPE — 한국어 토큰 효율 ~30% 향상) |
| **Attention** | Hybrid (3 Sliding Window + 1 Global, 반복) |

**한국어 벤치마크 성능:**

| 벤치마크 | 점수 | 설명 |
|----------|------|------|
| KMMLU-Pro | 67.3 | 전문 지식 |
| KoBALT | 61.8 | 한국어 이해력 |
| CLIcK | 83.9 | 한국 문화/역사 |
| HRM8K | 90.9 | 한국어 수학 |
| Ko-LongBench | 86.8 | 장문 이해 |
| KGC-Safety | 96.1 | 한국어 안전성 |

#### EXAONE-Deep 시리즈 — 추론 특화

| 모델 | 크기 | 핵심 성과 |
|------|------|----------|
| EXAONE-Deep-32B | 32B | 한국 수능 수학 2025 **94.5%**, AIME 2025 65.8% |
| EXAONE-Deep-7.8B | 7.8B | 경량 추론 모델 |
| EXAONE-Deep-2.4B | 2.4B | 엣지/모바일용 |

LG AI Research는 한국어 평가 데이터셋도 공개: KMMLU-Pro(2,820건), KMMLU-Redux(2,590건), Ko-LongRAG(600건).

### 2.3 Upstage — SOLAR 시리즈

| 모델 | 크기 | 핵심 |
|------|------|------|
| SOLAR-10.7B | 10.7B | **DUS(Depth Up-Scaling)** 기법, 한국어 특화 |
| Solar Pro Preview | 22B | 성능 향상 |
| Solar Open 100B | 100B | 2025년 1월 공개 |

Upstage는 **Open Ko-LLM Leaderboard** 와 **Ko-FreshQA Leaderboard** 를 운영하며 한국어 LLM 벤치마크 표준화에 기여하고 있습니다.

### 2.4 NCSOFT — VARCO 시리즈

| 모델 | 핵심 |
|------|------|
| VARCO-VISION-2.0-14B/1.7B | 한국어 멀티모달 |
| VARCO-VISION-2.0-1.7B-OCR | 한국어 OCR 특화 |
| Llama-VARCO-8B-Instruct | Llama 기반 한국어 텍스트 |

한국어 비전-언어 벤치마크도 공개: K-MMStar, K-SEED, K-DTCBench, K-LLaVA-W, K-MMBench.

### 2.5 KRAFTON — Raon (한국어 음성 AI)

| 모델 | 핵심 |
|------|------|
| Raon-Speech-9B | Any-to-Any 음성 AI |
| Raon-SpeechChat-9B | 음성 대화 |
| Raon-OpenTTS-0.3B | 오픈소스 TTS |

한국어 음성 AI의 오픈소스 공백을 메우는 역할을 하고 있습니다.

### 2.6 기타

| 기업/프로젝트 | 모델 | 핵심 |
|-------------|------|------|
| **EleutherAI** | Polyglot-Ko-12.8B | 863GB 한국어 데이터, Apache 2.0 |
| **Kakao Brain** | KoGPT | 2024년 이후 업데이트 중단, COYO-700M 데이터셋은 활용 |
| **SKT** | A.X | 자사 서비스 내재화 |

---

## 3. 중국계 모델의 한국어 지원

### 3.1 Qwen (Alibaba) — 한국어 공식 지원 최강 오픈소스

| 모델 | 크기 | 한국어 지원 | 핵심 |
|------|------|-----------|------|
| Qwen 2.5 | ~72B | **공식 (29+ 언어)** | 128K 컨텍스트, GQA, JSON 출력 |
| Qwen 3.5 | 397B MoE (17B Active) | 공식 | 멀티모달 통합, ASR/TTS 전문 모델 |

Qwen은 한국어를 **공식 지원 언어** 에 포함하고 있으며, 한국어 테이블 이해, 구조화 출력 등에서도 잘 작동합니다. 오픈소스 모델 중 한국어 성능이 가장 높은 선택지 중 하나입니다.

### 3.2 DeepSeek — 범용 최강, 한국어는 비공식

| 모델 | 한국어 지원 | 특징 |
|------|-----------|------|
| DeepSeek-V3.2 (685B) | 비공식 (다국어 학습) | 범용 최강, 코딩/수학 |
| DeepSeek-OCR/OCR-2 (3B) | 가능 | 한국어 문서 OCR |

한국어를 공식 지원하지 않지만, 대규모 다국어 데이터 학습으로 한국어 처리가 가능합니다. 한국 문화 맥락 이해는 국내 모델 대비 열세입니다.

{% hint style="warning" %}
**중국 AI 모델 사용 시 주의**: 데이터 주권, 콘텐츠 검열, 규제 리스크를 고려해야 합니다. 금융/공공/방위산업 등 민감 도메인에서는 셀프호스팅하더라도 보안 정책 확인이 필수입니다.
{% endhint %}

---

## 4. 한국어 NLP 기술 과제

### 4.1 토큰화 방식 비교

| 방식 | 설명 | 장점 | 단점 | 대표 모델 |
|------|------|------|------|-----------|
| **BPE** | 빈도 기반 서브워드 | 범용, OOV 최소 | 형태소 경계 무시 | GPT, Llama |
| **형태소 기반** | 형태소 단위 분리 | 언어학적 정확 | 분석기 의존, 느림 | HyperCLOVA X |
| **자소(Jamo) 단위** | 초성/중성/종성 분리 | 미등록어 강력 | 시퀀스 3배 | 연구 모델 |
| **SuperBPE** | BPE 확장, 다국어 최적화 | 한국어 효율 30%↑ | 검증 초기 | K-EXAONE |

한국어 전용 토크나이저는 범용 대비 **동일 비용으로 약 1.5~2배 더 많은 한국어 텍스트** 를 처리할 수 있습니다.

### 4.2 한국어 RAG 최적화 과제

| 과제 | 상세 | 해결 방향 |
|------|------|----------|
| 불규칙 띄어쓼기 | 청킹 어려움 | 형태소 분석기 전처리 |
| 조사 변화 | BM25 매칭 방해 | 어간 추출, 하이브리드 검색 |
| 임베딩 모델 | 한국어 특화 모델 부족 | BGE-M3, multilingual-e5 활용 |

**한국어 RAG용 임베딩 모델 추천:**

| 모델 | 차원 | 최대 길이 | 특징 |
|------|------|----------|------|
| **BGE-M3** (BAAI) | 1024 | 8192 | Dense+Sparse+Multi-Vector, 100+ 언어 |
| **multilingual-e5-large** | 1024 | 512 | 100 언어, XLM-RoBERTa 기반 |
| **KoSimCSE** | 768 | 512 | 한국어 전용 SimCSE |

더 자세한 한국어 RAG 전략은 [한국어 RAG 최적화](../guides/rag/korean-nlp.md) 문서를 참고하세요.

---

## 5. 한국어 벤치마크 & 평가

| 벤치마크 | 평가 영역 | 특징 |
|----------|-----------|------|
| **KLUE** | 8개 NLU 태스크 | 한국어 GLUE |
| **KoBEST** | BoolQ/COPA/WiC/HellaSwag/SentiNeg | 한국어판 SuperGLUE |
| **KMMLU** | 50+ 전문 분야 | 한국어 MMLU, Human Accuracy 포함 |
| **KMMLU-Pro** | 50+ 분야 (2,820건) | LG AI Research |
| **CLIcK** | 한국 문화/역사 지식 | 한국 고유 지식 평가 |
| **HRM8K** | 한국어 수학 (8,000건) | 수학 추론 |
| **Ko-LongBench** | 장문 이해 | 긴 한국어 문서 |
| **KGC-Safety** | 한국어 안전성 | 한국 문화 맥락 |
| **Open Ko-LLM Leaderboard** | 종합 | Upstage 운영, 커뮤니티 |

KMMLU는 각 문항에 **Human_Accuracy** 가 포함되어 "AI가 인간 전문가 수준에 도달했는가"를 판단할 수 있습니다.

---

## 6. 정부 정책 & 산업 동향

### 6.1 주요 정책

| 정책 | 내용 |
|------|------|
| AI 일상화 전략 | AI 기술의 전 산업 확산 |
| AI 반도체 육성 | HBM, NPU 등 AI 칩 국산화 |
| AI 데이터댐 | 대규모 한국어 학습 데이터 구축 |
| AI 윤리 가이드라인 | 공공 AI 서비스 기준 |
| 초거대 AI 경쟁력 확보 | R&D 지원, 컴퓨팅 인프라 투자 |

### 6.2 데이터 인프라

| 자원 | 설명 |
|------|------|
| **AI Hub** (NIA) | 수백 TB, 음성/텍스트/이미지 한국어 데이터 |
| **모두의 말뭉치** (국립국어원) | 한국어 언어 자원 |
| **KorQuAD** | 10만+ 한국어 질의응답 데이터 |

### 6.3 산업별 AI 도입 현황

| 산업 | 도입 수준 | 주요 활용 |
|------|----------|----------|
| **금융** | 활발 (KB, 신한, 하나) | 고객 서비스, 문서 분석, 리스크 평가 |
| **의료** | 초기 | 의료 영상, 임상 문서 |
| **법률** | 성장 중 | 판례 검색, 계약서 분석 |
| **제조** | 활발 | 품질 예측, 설비 모니터링 |
| **공공** | 성장 | **국산 모델 우선 정책** |
| **커머스** | 성숙 | 추천, 검색, 고객 응대 |

{% hint style="info" %}
공공 부문은 **데이터 주권** 이슈로 국산 AI 모델/국내 클라우드 우선 도입 정책이 강화되고 있습니다.
{% endhint %}

---

## 7. Databricks와 한국어 AI

### 7.1 세 가지 접근법

| 접근법 | 설명 | 적합 시나리오 |
|--------|------|-------------|
| **External Model Serving** | AI Gateway → GPT-4o/Claude 4/Qwen API | PoC, 프로토타이핑 |
| **Provisioned Throughput** | Llama/Qwen 한국어 Fine-tuned 배포 | 프로덕션, 민감 데이터 |
| **한국어 RAG 파이프라인** | 문서 → 형태소 분석 → BGE-M3 → Vector Search → LLM | 기업 지식 기반 |

### 7.2 한국어 모델 선택 가이드 (Databricks 기준)

| 시나리오 | 1순위 | 2순위 |
|----------|------|------|
| 한국어 범용 챗봇 | GPT-4o / Claude 4 Sonnet | Qwen 2.5-72B |
| 한국 문화/역사 특화 | HyperCLOVA X | K-EXAONE |
| 한국어 RAG | Qwen 2.5-72B + BGE-M3 | Llama 3.3-70B + BGE-M3 |
| 한국어 수학/추론 | K-EXAONE-236B | EXAONE-Deep-32B |
| 엣지/모바일 | Qwen 3.5-2B | EXAONE-Deep-2.4B |
| 한국어 OCR | DeepSeek-OCR-2 (3B) | VARCO-VISION-1.7B-OCR |
| 한국어 음성 | Raon-Speech-9B | Qwen3-ASR/TTS |
| 공공/규제 환경 | HyperCLOVA X | K-EXAONE (자체 배포) |

---

## 8. 향후 전망

### 단기 (2026)

- MoE 기반 한국어 모델 보편화
- 한국어 멀티모달 (비전+텍스트) 모델 확대
- 한국어 음성 AI (TTS/ASR/대화) 성장

### 중기 (2026~2028)

- 3B~7B 한국어 도메인 특화 모델 고도화
- SuperBPE급 토크나이저 표준화
- MCP/A2A 기반 한국어 에이전트 생태계 성숙
- 공공 AI 전환 가속

### 핵심 과제

| 과제 | 상세 |
|------|------|
| **학습 데이터 부족** | 영어 대비 10~20배 적은 고품질 데이터 |
| **토큰화 비효율** | 범용 토크나이저의 한국어 처리 오버헤드 |
| **벤치마크 신뢰성** | 한국어 벤치마크의 다양성/깊이 확대 필요 |
| **인재 부족** | AI 연구자/엔지니어 부족 |
| **GPU 인프라** | NVIDIA GPU 확보 경쟁 |

---

**참고 자료:**
- [K-EXAONE-236B-A23B (HuggingFace)](https://huggingface.co/LGAI-EXAONE/K-EXAONE-236B-A23B)
- [EXAONE-Deep-32B (HuggingFace)](https://huggingface.co/LGAI-EXAONE/EXAONE-Deep-32B)
- [Qwen2.5-72B-Instruct (HuggingFace)](https://huggingface.co/Qwen/Qwen2.5-72B-Instruct)
- [SOLAR-10.7B (HuggingFace)](https://huggingface.co/upstage/SOLAR-10.7B-Instruct-v1.0)
- [Open Ko-LLM Leaderboard](https://huggingface.co/spaces/upstage/open-ko-llm-leaderboard)
- [BGE-M3 (HuggingFace)](https://huggingface.co/BAAI/bge-m3)
- [KMMLU (HuggingFace)](https://huggingface.co/datasets/HAERAE-HUB/KMMLU)
- [한국어 RAG 최적화 가이드](../guides/rag/korean-nlp.md)
