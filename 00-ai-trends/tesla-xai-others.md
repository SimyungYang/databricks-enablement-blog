# Tesla, xAI & 기타 AI 기업 동향 (2026년 초 기준)

{% hint style="info" %}
**이 문서의 범위**: Tesla의 물리적 AI, xAI(Grok), 그리고 Mistral, DeepSeek, Perplexity 등 주목할 AI 기업들을 분석합니다.
{% endhint %}

---

# Part 1: Tesla AI

## 1. 개요

Tesla는 다른 AI 기업과 근본적으로 다른 위치에 있습니다. **물리적 세계에서 작동하는 AI** 에 집중하며, 자율주행(FSD), 휴머노이드 로봇(Optimus), 에너지 관리 AI를 핵심 제품으로 합니다. 연간 수백만 대의 차량에서 수집되는 실제 주행 데이터가 가장 큰 자산입니다.

---

## 2. FSD (Full Self-Driving) — 자율주행 AI

### 2.1 FSD 진화

| 버전 | 시기 | 핵심 변화 |
|------|------|----------|
| FSD v11 | 2023 | End-to-End 신경망 도입, 규칙 기반 코드 제거 시작 |
| FSD v12 | 2024 초 | **완전 End-to-End** — 카메라 입력 → 직접 주행 명령 출력 |
| FSD v13 | 2024 말~2025 초 | 성능 대폭 향상, 인터벤션 감소, 고속도로/도심 통합 |
| FSD v13.x | 2025 | 지속적 OTA 업데이트, 안전성 개선 |

### 2.2 End-to-End AI 접근의 의미

기존 자율주행 시스템(Waymo 등)은 **감지 → 인식 → 예측 → 계획 → 제어** 의 파이프라인 구조를 사용합니다. Tesla FSD v12+는 이 모든 과정을 **단일 신경망** 으로 대체했습니다.

| 구분 | 파이프라인 방식 (Waymo 등) | End-to-End (Tesla) |
|------|------------------------|-------------------|
| 구조 | 각 단계 별도 모듈 | 단일 대형 신경망 |
| 입력 | 카메라 + LiDAR + HD Map | **카메라만** (8대) |
| 장점 | 디버깅 용이, 각 모듈 독립 개선 | 데이터 증가에 비례하는 성능 향상, 코너케이스 자연 해결 |
| 단점 | 모듈 간 오류 누적, 수작업 규칙 필요 | 블랙박스, 디버깅 어려움, 대규모 데이터 필요 |
| 데이터 | 제한적 (고가의 테스트 차량) | **수백만 차량의 실시간 데이터** |

### 2.3 Robotaxi 계획

| 항목 | 내용 |
|------|------|
| **차량** | Cybercab — 스티어링 휠/페달 없는 전용 차량 (2026년 생산 시작 예상) |
| **서비스** | Tesla Network — 개인 차량 공유 + Cybercab 운영 |
| **규제** | 미국 일부 주에서 감독 없는 자율주행 허가 획득 목표 |
| **경쟁** | Waymo (Google) — Phoenix, SF, LA에서 이미 상용 운영 |

---

## 3. Optimus — 휴머노이드 로봇

| 항목 | 현황 (2025) |
|------|------------|
| **세대** | Gen 2 (2024 공개), Gen 3 (2025 개발 중) |
| **작업 능력** | 물건 분류, 운반, 간단한 조립 작업 |
| **AI** | FSD와 동일한 End-to-End 신경망 기반 |
| **가격 목표** | $20,000~$30,000 (장기, 양산 후) |
| **Tesla 내부 사용** | 공장에서 부품 분류 등 제한적 투입 (2025) |
| **외부 판매** | 2027년 이후 예상 |

Optimus의 핵심 기술 과제는 **Manipulation(손 제어)** 입니다. 이동(locomotion)은 상대적으로 해결되고 있지만, 인간 수준의 손재주(dexterity)는 아직 갈 길이 멀습니다.

---

## 4. Dojo 슈퍼컴퓨터

| 항목 | 내용 |
|------|------|
| **목적** | FSD/Optimus 학습 전용 슈퍼컴퓨터 |
| **칩** | D1 (자체 설계, TSMC 7nm, 362 TFLOPS BF16) |
| **상태** | 초기 버전 배포, 주력은 여전히 NVIDIA GPU |
| **전략 변화** | NVIDIA H100/B200 대량 구매 병행, Dojo는 보조적 역할 |

Tesla는 Dojo에 대한 투자를 줄이고 NVIDIA GPU에 더 의존하는 방향으로 전환했습니다. 이는 자체 칩 개발의 어려움과 NVIDIA 생태계의 압도적 우위를 반영합니다.

---

# Part 2: xAI & Grok

## 5. xAI 개요

Elon Musk가 2023년 설립한 AI 기업으로, **"우주의 진정한 본질을 이해하는 AI"** 를 미션으로 합니다. X(구 Twitter) 플랫폼과 통합되어 있습니다.

---

## 6. Grok 모델 시리즈

| 모델 | 출시 | 핵심 |
|------|------|------|
| Grok-1 | 2023.11 | 최초 모델, 314B MoE, 오픈소스 |
| Grok-1.5 | 2024.03 | 128K 컨텍스트, 비전 지원 |
| Grok-2 | 2024.08 | Claude 3.5 Sonnet 경쟁 수준 |
| **Grok-3** | 2025.02 | **Colossus 학습, 최고 성능 주장** |
| Grok-3 mini | 2025.02 | 경량 추론 모델 |

### 6.1 Grok-3 상세

| 항목 | 내용 |
|------|------|
| **학습 인프라** | Colossus — 200,000+ H100 GPU (세계 최대 단일 클러스터) |
| **성능** | AIME 2025에서 93.3% (출시 시점 최고), SWE-bench 상위 |
| **특징** | DeepSearch (심층 검색), Think 모드 (추론), X 데이터 접근 |
| **X 통합** | X 포스트 실시간 분석, 트렌드 파악, 뉴스 요약 |
| **가격** | X Premium+ ($16/월) 또는 SuperGrok ($30/월) |

### 6.2 Colossus 슈퍼컴퓨터

| 항목 | 내용 |
|------|------|
| **위치** | 미국 멤피스 테네시 |
| **GPU** | 200,000+ H100 (NVIDIA) |
| **특징** | 세계 최대 단일 AI 학습 클러스터 |
| **건설** | 약 4개월 만에 초기 100K GPU 클러스터 구축 (2024) |
| **확장** | 1M+ GPU로 확장 계획 |

### 6.3 xAI의 과제

| 과제 | 상세 |
|------|------|
| 브랜드 리스크 | Elon Musk의 정치적 발언/논란이 기업 이미지에 영향 |
| X 데이터 의존 | X 사용자 감소 시 데이터 우위 약화 |
| 개발자 생태계 | OpenAI/Anthropic 대비 API/도구 생태계 미성숙 |
| 엔터프라이즈 | B2B 시장 진입 초기, 신뢰 구축 필요 |

---

# Part 3: 기타 주목할 AI 기업

## 7. DeepSeek (중국)

### 7.1 개요

**중국 퀀트 헤지펀드 High-Flyer** 에서 분사한 AI 연구소로, 2025년 1월 발표한 DeepSeek-R1이 AI 업계를 충격에 빠뜨렸습니다.

### 7.2 주요 모델

| 모델 | 시기 | 핵심 |
|------|------|------|
| DeepSeek-V2 | 2024.05 | 236B MoE, 128K 컨텍스트, **MLA(Multi-Head Latent Attention)** 혁신 |
| DeepSeek-V3 | 2024.12 | 685B MoE (37B Active), **학습비용 $5.5M** (GPT-4 대비 1/100 수준) |
| **DeepSeek-R1** | 2025.01 | 추론 모델, o1과 동등 성능, **오픈소스**, 증류(distillation) 모델 공개 |
| DeepSeek-V3.2 | 2025.12 | V3 후속, 성능 향상 |

### 7.3 왜 DeepSeek가 충격적인가

| 요인 | 상세 |
|------|------|
| **비용 효율** | V3 학습에 $5.5M — GPT-4 학습비($100M+)의 1/20 이하 |
| **하드웨어 제약 극복** | 미국의 대중국 GPU 수출 규제(H100 금지) 하에서 H800으로 달성 |
| **오픈소스** | MIT 라이선스로 완전 공개, 누구나 사용 가능 |
| **MLA 혁신** | Multi-Head Latent Attention으로 KV 캐시 메모리 93% 절감 |
| **추론 모델** | R1은 별도 SFT 없이 **순수 강화학습(RL)만으로** 추론 능력 획득 |

{% hint style="warning" %}
**주의**: 중국 AI 모델은 **데이터 주권, 콘텐츠 검열, 규제 리스크** 를 고려해야 합니다. 중국 정부의 요구에 따라 특정 주제(천안문, 대만, 티베트 등)에서 편향된 답변을 할 수 있으며, 기업 환경에서는 자체 배포 시에도 보안 검토가 필요합니다.
{% endhint %}

---

## 8. Mistral AI (프랑스)

### 8.1 개요

2023년 설립된 **유럽 최고의 AI 기업** 으로, 프랑스 정부의 전폭적 지원을 받고 있습니다. Meta 출신 연구원들이 핵심입니다.

### 8.2 주요 모델

| 모델 | 크기 | 핵심 |
|------|------|------|
| Mistral 7B | 7B | **오픈소스 소형 모델의 기준점** |
| Mixtral 8x7B | 46.7B (MoE) | **오픈소스 MoE의 선구자** |
| Mistral Large | 비공개 | GPT-4 경쟁 수준 |
| Mistral Medium | 비공개 | 비용/성능 균형 |
| **Mistral Small (v25.01)** | 24B | 경량 고성능, 코딩 강점 |
| Codestral | 22B | 코드 생성 특화, 80+ 언어 |
| Pixtral | 비공개 | 멀티모달 (이미지 이해) |

### 8.3 Mistral의 차별점

| 차별점 | 상세 |
|--------|------|
| **유럽 기반** | EU AI Act 준수, GDPR 친화적 — 유럽 기업의 선호도 높음 |
| **Le Chat** | 자체 AI 챗 인터페이스, 빠른 응답 |
| **La Plateforme** | API 서비스, Agent 기능 |
| **다국어** | 프랑스어, 독일어, 스페인어 등 유럽 언어 강점 |

---

## 9. Perplexity AI

| 항목 | 내용 |
|------|------|
| **설립** | 2022년 |
| **제품** | AI 기반 검색 엔진 (Answer Engine) |
| **핵심** | 질문에 대해 소스 인용과 함께 구조화된 답변 제공 |
| **MAU** | 1억 명+ (2025년 기준) |
| **기업 가치** | $9B+ (2025년 초) |
| **경쟁** | Google Search, ChatGPT Search, Bing AI |
| **차별점** | 검색 결과의 출처 투명성, 광고 없는 경험 |

---

## 10. Stability AI / 이미지 생성 생태계

| 모델/기업 | 핵심 |
|-----------|------|
| **Stable Diffusion 3.5** | 오픈소스 이미지 생성 표준 |
| **FLUX (Black Forest Labs)** | Stability AI 창립자가 만든 차세대 모델 |
| **Midjourney** | 최고 품질 이미지 생성 (디스코드 기반) |
| **DALL-E 3** / GPT-4o | OpenAI 통합 이미지 생성 |
| **Imagen 3** | Google의 포토리얼 이미지 생성 |

이미지 생성 시장은 2025~2026년에 **비디오 생성** 으로 빠르게 확장되고 있으며, Sora(OpenAI), Veo 2(Google), Kling(중국 Kuaishou), Runway Gen-3 등이 경쟁하고 있습니다.

---

## 11. AI 하드웨어 경쟁

| 기업 | 칩/제품 | 용도 |
|------|--------|------|
| **NVIDIA** | B200 (Blackwell), GB200 NVL72 | 학습 + 추론 (압도적 시장 점유) |
| **AMD** | MI300X, MI350 | NVIDIA 대안, 가격 경쟁력 |
| **Google** | TPU v6 (Trillium) | Gemini 학습, GCP 전용 |
| **AWS** | Trainium2, Inferentia2 | Bedrock 최적화 |
| **Apple** | M4 Ultra | 온디바이스 AI, Mac 로컬 추론 |
| **Groq** | LPU | **초고속 추론 전용** (10x 속도) |
| **Cerebras** | WSE-3 (Wafer Scale) | 초대형 모델 학습 |
| **SambaNova** | SN40L | 엔터프라이즈 AI 추론 |

---

## 12. 전체 AI 생태계 종합 비교

| 기업 | 모델 전략 | Agent 전략 | 인프라 | 차별점 |
|------|----------|-----------|--------|--------|
| **OpenAI** | 클로즈드 (GPT+o) | Agents SDK | Azure + Stargate | 브랜드, 사용자 규모 |
| **Anthropic** | 클로즈드 (Claude) | MCP + Claude Code | AWS/GCP | 안전성, 코딩 품질 |
| **Google** | 하이브리드 (Gemini+Gemma) | A2A + ADK | TPU + GCP | 수직 통합, 연구 |
| **Meta** | 오픈소스 (Llama) | Llama Stack | 자체 GPU | 생태계, 사용자 |
| **Tesla/xAI** | 특수 목적 + Grok | FSD, Optimus | Colossus, Dojo | 물리적 AI, X 데이터 |
| **DeepSeek** | 오픈소스 | 없음 | H800 (제한적) | 극한 비용 효율 |
| **Mistral** | 하이브리드 | La Plateforme | 클라우드 의존 | 유럽 거점, EU 친화 |

---

## 13. 향후 전망

| 영역 | 전망 |
|------|------|
| **물리적 AI** | Tesla Optimus/FSD, Figure AI, Nvidia Isaac 등 로봇+AI 융합 가속 |
| **DeepSeek** | V4 발표 예상, 비용 효율 혁신 지속, 미국 수출 규제와의 기술 경쟁 |
| **Mistral** | 유럽 시장 선도, EU 공공부문 AI 도입의 핵심 파트너 |
| **AI 칩** | NVIDIA B200 독주 vs AMD/Google/AWS 추격, 전력 소비가 핵심 병목 |
| **규제** | EU AI Act 시행(2025.08), 미국 연방 AI 규제 논의 |

{% hint style="info" %}
**Databricks 시사점**: Databricks는 모델 제공자에 종속되지 않는 플랫폼으로, DeepSeek, Mistral 등 오픈소스 모델을 Model Serving에 자유롭게 배포할 수 있습니다. 특히 DeepSeek의 비용 효율적 모델과 Databricks의 데이터 레이크하우스를 결합하면, 최소 비용으로 프라이빗 AI를 구축할 수 있습니다.
{% endhint %}

---

**참고 자료:**
- [Tesla AI Day 발표](https://www.tesla.com/AI)
- [xAI 공식](https://x.ai/)
- [DeepSeek-V3 기술 보고서](https://arxiv.org/abs/2412.19437)
- [DeepSeek-R1 기술 보고서](https://arxiv.org/abs/2501.12948)
- [Mistral AI 공식](https://mistral.ai/)
- [Perplexity AI](https://www.perplexity.ai/)
