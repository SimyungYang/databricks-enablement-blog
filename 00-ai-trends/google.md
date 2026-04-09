# Google / DeepMind 동향 분석 (2026년 초 기준)

{% hint style="info" %}
**이 문서의 범위**: Google과 DeepMind의 AI 전략, 모델 라인업, Agent 생태계, 연구 성과, 인프라 전략을 종합 분석합니다. A2A 프로토콜 기술 상세는 [A2A (Agent-to-Agent)](../guides/genai-concepts/a2a-protocol/README.md), Agent 전략 상세는 [Google AI Agent 전략](../guides/genai-concepts/agent-landscape/google.md)을 참고하세요.
{% endhint %}

---

## 1. 개요 — Google AI의 현재 위치

Google은 2024~2025년 사이 AI 전략의 근본적인 전환을 이루었습니다. **"AI-first"** 에서 **"Agent-first"** 로의 패러다임 전환이 핵심입니다. Sundar Pichai는 "우리는 이제 AI를 만드는 것이 아니라, AI가 일하는 세상을 만들고 있다"고 선언했습니다.

### Google AI 전략의 5대 축

| 축 | 핵심 | 대표 제품/기술 |
|---|------|---------------|
| **모델** | 최고 성능의 Foundation Model | Gemini 2.5 Pro/Flash, Gemma |
| **프로토콜** | Agent 간 통신 표준 | A2A (Agent-to-Agent) |
| **플랫폼** | 개발자 + 엔터프라이즈 도구 | Vertex AI, ADK, Agent Builder |
| **연구** | 과학적 돌파구 | AlphaFold 3, AlphaProteo, GenCast |
| **제품** | 소비자 + 엔터프라이즈 Agent | Gemini App, Jules, Mariner, Astra |

### 왜 Google이 Agent에 올인하는가

Google의 핵심 수익원인 **검색 광고 모델** 이 AI Agent 시대에 근본적으로 위협받고 있습니다. 사용자가 "Google에서 검색"하는 대신 "Agent에게 질문"하는 패턴으로 전환되면, 기존 비즈니스 모델이 무의미해집니다.

---

## 2. Gemini 모델 라인업

### 2.1 모델 진화 타임라인

| 시기 | 모델 | 핵심 변화 |
|------|------|----------|
| 2023.12 | Gemini 1.0 (Ultra/Pro/Nano) | Google의 멀티모달 LLM 첫 공개 |
| 2024.02 | Gemini 1.5 Pro | **100만 토큰 컨텍스트 최초 도입** |
| 2024.05 | Gemini 1.5 Flash | 경량화 모델, 비용 효율 극대화 |
| 2024.09 | Gemini 1.5 Pro 업데이트 | 200만 토큰 컨텍스트 |
| 2024.12 | Gemini 2.0 Flash | Agent 네이티브 설계, 멀티모달 출력 |
| 2025.03 | **Gemini 2.5 Pro** | **Thinking Model**, Deep Think, 최고 성능 |
| 2025.05 | Gemini 2.5 Flash | Thinking 지원 + 비용 효율 |

### 2.2 Gemini 2.5 Pro — "생각하는 모델"

Gemini 2.5 Pro는 Google의 현재 **플래그십 모델** 로, 가장 중요한 혁신은 **Thinking Model** 개념의 도입입니다.

| 특성 | 상세 |
|------|------|
| **Thinking** | 답변 전 내부 추론 수행, 복잡한 수학/코딩/논리에서 정확도 대폭 향상 |
| **Deep Think** | 특히 어려운 문제에 더 오래, 더 깊이 추론하는 모드 |
| **컨텍스트** | 100만 토큰 이상 |
| **멀티모달** | 텍스트, 이미지, 오디오, 비디오 동시 처리 |
| **네이티브 Tool Use** | Function Calling이 학습 과정에 내장 |

**벤치마크 성능 (2025년 3월 기준):**

| 벤치마크 | Gemini 2.5 Pro | GPT-4o | Claude 3.5 Sonnet | 설명 |
|----------|---------------|--------|-------------------|------|
| MMLU-Pro | 82.1% | 74.0% | 78.0% | 전문 지식 |
| GPQA Diamond | 68.9% | 53.6% | 65.0% | 대학원 수준 과학 |
| MATH | 92.0% | 76.6% | 78.3% | 수학 추론 |
| SWE-bench Verified | 63.8% | 38.4% | 53.1% | 실제 코딩 |

{% hint style="info" %}
**핵심 시사점**: Gemini 2.5 Pro는 발표 시점 기준 대부분의 벤치마크에서 최고 성능을 기록했습니다. 다만 Claude 4 Sonnet/Opus, GPT-4.1 등 후속 모델들이 빠르게 격차를 줄이고 있으며, 벤치마크 리더십은 수주 단위로 바뀌고 있습니다.
{% endhint %}

### 2.3 Gemini 2.5 Flash — 실용주의의 승리

| 특성 | Gemini 2.5 Pro | Gemini 2.5 Flash |
|------|---------------|-----------------|
| **성능** | 최고 (Deep Think 포함) | Pro 대비 ~80-85% |
| **속도** | 보통 | 매우 빠름 (2~3배) |
| **가격** | ~$10/1M 입력 토큰 | ~$1/1M 입력 토큰 |
| **최적 용도** | 복잡한 추론, 연구, 코드 생성 | 대량 처리, 실시간 응답, 분류 |

{% hint style="warning" %}
**실전 가이드**: 프로덕션 환경에서는 **먼저 Flash로 시작** 하고, 품질이 부족한 특정 태스크에만 Pro를 적용하는 것이 비용 대비 최적의 전략입니다.
{% endhint %}

---

## 3. Agent 생태계 — A2A, ADK, Agentspace

### 3.1 A2A (Agent-to-Agent) 프로토콜

AI Agent가 멀티에이전트 시스템으로 진화하면서, 이기종 Agent 간 통신 표준이 필요해졌습니다.

| 항목 | 내용 |
|------|------|
| **공개** | 2025년 4월 (v0.1) → v0.2 → v0.3 (gRPC 지원) |
| **주도** | Google → 2025년 11월 Linux Foundation에 기부 |
| **참여** | 150+ 조직 (Salesforce, SAP, Atlassian, MongoDB, Databricks 등) |

#### 핵심 개념

1. **Agent Card** — `/.well-known/agent.json`에 능력/인증을 기술한 자기 소개서
2. **Task** — 상태 머신: `submitted → working → input-required → completed/failed/canceled`
3. **Message & Part** — 멀티모달 통신 단위
4. **Artifact** — Task 실행 결과물
5. **Streaming** — SSE + gRPC 기반 실시간 통신

#### A2A vs MCP 비교

| 비교 항목 | A2A | MCP (Anthropic) |
|-----------|-----|-----------------|
| **목적** | Agent ↔ Agent 대화 (수평적) | Agent → 도구 사용 (수직적) |
| **관계** | 대등한 피어(peer-to-peer) | 클라이언트-서버 |
| **추상화** | 고수준 (Task, 대화, 협업) | 저수준 (함수 호출, 데이터 조회) |
| **상태 관리** | Task 상태 머신 내장 | Stateless |
| **표준화** | Linux Foundation | 오픈 소스 (Anthropic 주도) |

A2A와 MCP는 **경쟁이 아닌 보완** 관계입니다. 더 자세한 내용은 [A2A 프로토콜 가이드](../guides/genai-concepts/a2a-protocol/README.md)를 참고하세요.

### 3.2 ADK (Agent Development Kit)

| 항목 | 내용 |
|------|------|
| **출시** | 2025년 4월 |
| **라이선스** | Apache 2.0 |
| **언어** | Python, TypeScript, Java |
| **모델** | 비종속 — Gemini, GPT, Claude, Llama 모두 지원 |

**4가지 멀티에이전트 패턴:**

| 패턴 | 설명 | 최적 유스케이스 |
|------|------|----------------|
| **Sequential** | A → B → C 순차 실행 | 데이터 ETL, 보고서 파이프라인 |
| **Dispatcher** | Router가 전문 Agent로 라우팅 | 고객 서비스, 멀티도메인 |
| **Generator-Critic** | 생성 + 평가 반복 | 코드 생성, 콘텐츠 품질 개선 |
| **Parallel** | 동시 실행 후 결과 병합 | 시장 조사, 경쟁 분석 |

### 3.3 Vertex AI Agent Builder

2025년 3월 GA된 **엔터프라이즈 Agent 구축 플랫폼** 입니다.

| 구성 요소 | 역할 |
|-----------|------|
| **Agent Engine** | 런타임 + 세션 + 메모리 + 로깅 |
| **Agent Designer** | 노코드 Agent 빌더 |
| **Tool Governance** | Agent별 Tool 접근 제어 (IAM 연동) |
| **Agent Identity** | OAuth/OIDC 인증, 감사 추적 |

### 3.4 Agentspace → Gemini Enterprise

2025년 10월 Agentspace를 **Gemini Enterprise** 로 리브랜딩. Agent Gallery, Enterprise Search(100+ 커넥터), 데이터 커넥터(SAP, Salesforce 등)를 통합한 엔터프라이즈 플랫폼입니다.

---

## 4. 소비자 Agent 제품군

| 제품 | 핵심 | 가격 |
|------|------|------|
| **Jules** | GitHub 이슈 자동 해결, PR 생성 (코딩 Agent) | Free ~ $249.99/월 |
| **Project Mariner** | 브라우저 자율 조작 Agent | AI Ultra 구독 |
| **Project Astra** | 실시간 멀티모달 비서 (카메라+마이크+음성) | 데모/제한 공개 |
| **NotebookLM** | 문서 기반 연구 도우미, Audio Overview | 무료 |
| **Deep Research** | 자동 다단계 웹 리서치 + 보고서 생성 | Gemini App 내장 |

---

## 5. DeepMind 연구 성과

### 주요 성과

| 프로젝트 | 발표 | 핵심 | 의의 |
|----------|------|------|------|
| **AlphaFold 3** | 2024.05 | 단백질+DNA+RNA 복합체 3D 구조 예측 | **2024 노벨 화학상 수상** |
| **AlphaProteo** | 2024.09 | 타겟 단백질에 결합하는 새 단백질 AI 설계 | 3~300배 강한 결합력 |
| **GenCast** | 2024.12 | 확률적 기상 예측 AI | 15일 예측 97.2% 우수 |
| **Veo 2** | 2024.12 | 4K 영상 생성, 물리 법칙/영화 기법 이해 | 영상 생성 품질 최고 수준 |
| **Willow** | 2024.12 | 105-큐비트 양자 칩, 에러율 임계값 돌파 | 양자 컴퓨팅 이정표 |

---

## 6. 오픈소스 — Gemma 패밀리

### Gemma 진화

| 모델 | 출시 | 크기 | 특징 |
|------|------|------|------|
| **Gemma 1.0** | 2024.02 | 2B, 7B | 최초 오픈 모델 |
| **Gemma 2** | 2024.06 | 2B, 9B, 27B | 지식 증류로 대폭 성능 향상 |
| **Gemma 3** | 2025.03 | 1B, 4B, 12B, 27B | **멀티모달**, 128K 컨텍스트, 100+ 언어 |
| **Gemma 3n** | 2025 | 2B, 4B 효과 | 온디바이스 최적화, 음성/영상 |

Gemma 3 27B는 **Llama 3.3 70B와 동등 성능** 이면서 단일 GPU(RTX 4090)에서 실행 가능합니다.

---

## 7. 인프라 — TPU v6 (Trillium)

| 항목 | 내용 |
|------|------|
| **성능** | TPU v5e 대비 학습 처리량 4.7배, 에너지 효율 67% 향상 |
| **메모리** | HBM3, 대역폭 대폭 확대 |
| **스케일** | 최대 256칩 Pod |
| **용도** | Gemini 2.5 시리즈 학습에 사용 |

### 클라우드 경쟁 비교

| 항목 | Google Cloud | AWS | Azure | Databricks |
|------|-------------|-----|-------|-----------|
| **자체 모델** | Gemini (최고 수준) | 없음 | GPT-4o (OpenAI) | DBRX |
| **자체 칩** | TPU v6 (강력) | Trainium2 | Maia (초기) | 없음 |
| **Agent 플랫폼** | Agent Builder + ADK | Bedrock Agents | AI Studio + Copilot | Agent Bricks |
| **차별점** | 검색+모델+칩 수직통합 | 클라우드 1위 인프라 | Office 통합 | 데이터 레이크하우스 |

---

## 8. Google Search AI (AI Overviews)

| 항목 | 내용 |
|------|------|
| **기반** | Gemini (맞춤 최적화) |
| **적용** | 미국 검색의 ~30%, 전 세계 200+ 국가, 40+ 언어 |
| **영향** | SEO 전략 재편, 원본 사이트 클릭률 감소 우려 |

---

## 9. 경쟁 구도

| 항목 | Google/DeepMind | OpenAI | Anthropic |
|------|----------------|--------|-----------|
| **최강 모델** | Gemini 2.5 Pro | o3 / GPT-4.1 | Claude 4 Opus |
| **Agent 프로토콜** | A2A | 없음 | MCP |
| **오픈소스** | Gemma 3 (적극적) | 없음 | 없음 |
| **자체 칩** | TPU v6 | Azure 의존 | AWS/GCP 의존 |
| **연구 깊이** | **최고 (노벨상)** | 높음 | 높음 (안전성) |
| **강점** | 수직 통합 | 브랜드/사용자 | 코딩/Agent 품질 |
| **약점** | 제품 파편화 | 인프라 의존 | 엔터프라이즈 규모 |

---

## 10. 향후 전망

| 영역 | 전망 |
|------|------|
| **Gemini 3.0** | 2026년 중 예상, 더 강력한 추론 + 네이티브 Agent 능력 |
| **A2A v1.0** | Linux Foundation 하에서 표준화, 프로덕션 도입 시작 |
| **Astra** | 스마트 글래스/웨어러블 결합 소비자 제품 출시 예상 |
| **TPU v7** | NVIDIA B200과 성능 경쟁 본격화 |
| **AlphaFold 후속** | 소분자 약물 설계까지 확장, 제약 산업 혁명 가속 |

{% hint style="info" %}
**Databricks 시사점**: Gemini 모델은 Databricks Foundation Model API 또는 External Model Serving에서 사용 가능합니다. Gemma 3는 오픈소스이므로 Model Serving에 직접 배포하여 프라이빗 AI를 구축할 수 있습니다. A2A 프로토콜은 Databricks Agent Bricks와 향후 통합될 가능성이 있어 모니터링이 필요합니다.
{% endhint %}

---

**참고 자료:**
- [Google AI 블로그](https://blog.google/technology/ai/)
- [Gemini 2.5 발표](https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/)
- [A2A 프로토콜 사양](https://google.github.io/A2A/)
- [ADK 문서](https://google.github.io/adk-docs/)
- [DeepMind 연구](https://deepmind.google/research/)
- [AI Agent 업계 동향 — Google](../guides/genai-concepts/agent-landscape/google.md)
- [A2A 프로토콜 가이드](../guides/genai-concepts/a2a-protocol/README.md)
