# AWS & Microsoft AI 동향 분석 (2026년 초 기준)

{% hint style="info" %}
**이 문서의 범위**: Amazon/AWS와 Microsoft의 AI 전략, 모델, 클라우드 AI 플랫폼을 종합 분석합니다. Agent 전략 상세는 [AWS, Microsoft & Meta AI Agent 전략](../guides/genai-concepts/agent-landscape/aws-others.md)을 참고하세요.
{% endhint %}

---

# Part 1: Amazon / AWS

## 1. 개요

Amazon은 **클라우드(AWS) + 자체 모델(Nova) + 커스텀 칩(Trainium) + AI 어시스턴트(Q)** 의 수직 통합 전략을 추구하며, 특히 **Anthropic에 대한 대규모 투자** 를 통해 최고 성능 모델 접근권을 확보하고 있습니다.

---

## 2. Amazon Nova 모델 패밀리

2024년 12월 AWS re:Invent에서 발표된 **Amazon Nova** 는 AWS 자체 개발 Foundation Model 시리즈입니다.

### 2.1 모델 라인업

| 모델 | 유형 | 핵심 특성 |
|------|------|----------|
| **Nova Micro** | 텍스트 전용 | 최저 지연, 분류/요약 |
| **Nova Lite** | 멀티모달 | 이미지/비디오/텍스트 입력, 비용 효율 |
| **Nova Pro** | 멀티모달 | 균형잡힌 성능/비용, Agent에 최적 |
| **Nova Premier** | 멀티모달 | 최고 성능, 복잡한 추론 |
| **Nova Canvas** | 이미지 생성 | 텍스트→이미지, 워터마크 내장 |
| **Nova Reel** | 비디오 생성 | 텍스트→비디오 (최대 6초) |

### 2.2 Nova의 포지셔닝

Nova의 전략적 목적은 **"Anthropic/OpenAI에 대한 의존도를 줄이면서, Bedrock에서의 기본 선택지가 되는 것"** 입니다.

| 비교 | Nova Pro | Claude 3.5 Sonnet | GPT-4o |
|------|---------|-------------------|--------|
| 성능 | 중상 | 최상 | 최상 |
| Bedrock 통합 | **네이티브** | 우수 | Azure 기반 |
| 비용 | **가장 저렴** | 중간 | 중간 |
| Agent 최적화 | Bedrock Agent 특화 | 범용 | 범용 |

---

## 3. AWS Bedrock — AI 플랫폼

### 3.1 Bedrock의 진화

Bedrock은 AWS의 **관리형 AI 플랫폼** 으로, 다양한 Foundation Model을 단일 API로 접근할 수 있게 합니다.

**주요 기능 (2025년 기준):**

| 기능 | 설명 |
|------|------|
| **Model Selection** | Anthropic, Meta, Mistral, Cohere, Stability, Amazon 등 20+ 모델 |
| **Bedrock Agents** | 도구 사용 + 오케스트레이션 에이전트 구축 |
| **Knowledge Bases** | RAG 파이프라인 자동 구성 |
| **Guardrails** | 입출력 필터링, PII 마스킹, 주제 제한 |
| **Model Evaluation** | 모델 성능 자동 평가 |
| **Fine-tuning** | 모델 커스터마이징 |
| **Prompt Management** | 프롬프트 버전 관리/테스트 |
| **Flows** | 비주얼 워크플로 빌더 |

### 3.2 Bedrock Agents

| 기능 | 설명 |
|------|------|
| **Action Groups** | Lambda 함수, API 연동 |
| **Knowledge Base 통합** | RAG 자동 연결 |
| **Multi-Agent Collaboration** | 에이전트 간 작업 위임 (Supervisor/Route 모드) |
| **Code Interpreter** | 코드 실행 환경 |
| **Session Memory** | 대화 히스토리 자동 관리 |
| **Inline Agents** | 런타임에 동적으로 Agent 구성 |

### 3.3 Bedrock vs 경쟁 플랫폼

| 비교 | AWS Bedrock | Azure AI | Google Vertex AI | Databricks |
|------|-----------|----------|-----------------|-----------|
| **모델 다양성** | 최다 (20+) | OpenAI + OSS | Gemini + OSS | OSS + External |
| **Agent 기능** | Agents + Flows | AI Studio | Agent Builder + ADK | Agent Bricks |
| **데이터 통합** | S3, RDS, DynamoDB | Cosmos DB, Blob | BigQuery, GCS | Unity Catalog, Delta |
| **차별점** | 모델 선택 최대 | OpenAI 독점 | 자체 모델 최강 | 데이터 레이크 통합 |

---

## 4. Amazon Q — AI 어시스턴트

### 4.1 Q 제품군

| 제품 | 대상 | 핵심 기능 |
|------|------|----------|
| **Amazon Q Developer** | 개발자 | 코드 생성, 디버깅, 테스트, 코드 변환 (Java 8→17 등) |
| **Amazon Q Business** | 비즈니스 사용자 | 기업 데이터 검색/요약, 40+ 데이터 소스 커넥터 |
| **Amazon Q in QuickSight** | 분석가 | 자연어→차트, 자동 대시보드 생성 |
| **Amazon Q in Connect** | 고객 서비스 | 실시간 에이전트 보조, 고객 응대 추천 |

### 4.2 Q Developer 상세

| 기능 | 설명 |
|------|------|
| **코드 생성** | 인라인 제안, 블록 단위 생성 |
| **/transform** | Java 8→17, .NET→크로스플랫폼 등 자동 변환 |
| **/review** | 코드 리뷰 + 보안 취약점 탐지 |
| **/test** | 유닛 테스트 자동 생성 |
| **CLI 통합** | 터미널에서 자연어로 AWS 명령 |
| **Agent 모드** | 멀티파일 변경, 자율적 작업 수행 |

---

## 5. 커스텀 칩 전략

### 5.1 Trainium2

| 항목 | 내용 |
|------|------|
| **목적** | AI 모델 학습 최적화 |
| **성능** | Trainium1 대비 4배, NVIDIA H100과 경쟁 |
| **클러스터** | UltraCluster — 수만 칩 연결 |
| **비용** | NVIDIA GPU 대비 **30-50% 비용 절감** 목표 |

### 5.2 Inferentia2

| 항목 | 내용 |
|------|------|
| **목적** | AI 추론 최적화 |
| **성능** | Inferentia1 대비 3배 |
| **지원** | PyTorch, TensorFlow, Hugging Face 네이티브 |
| **비용** | GPU 대비 추론 비용 최대 40% 절감 |

---

## 6. Anthropic 파트너십

| 항목 | 내용 |
|------|------|
| **총 투자** | $8B+ (2023~2025 누적) |
| **주요 조건** | Anthropic은 AWS를 주요 클라우드로 사용, Trainium에서 모델 학습 |
| **전략적 의미** | OpenAI-Microsoft 축에 대응하는 Anthropic-AWS 축 형성 |
| **경쟁 관계** | Bedrock에서 Claude가 가장 인기 있는 모델, Nova와 미묘한 경쟁 |

---

# Part 2: Microsoft

## 7. 개요

Microsoft는 **OpenAI 독점 파트너십 + Azure AI 인프라 + Copilot 제품군 + 소형 모델(Phi)** 를 통해 엔터프라이즈 AI 시장을 공략하고 있습니다. Office 365 사용자 기반이 가장 강력한 차별점입니다.

---

## 8. Azure OpenAI Service

| 항목 | 내용 |
|------|------|
| **제공 모델** | GPT-4o, GPT-4.1, o3, o4-mini, DALL-E 3, Whisper |
| **차별점** | Azure 보안/규정 준수 하에서 OpenAI 모델 사용 |
| **리전** | 글로벌 20+ 리전 배포 |
| **통합** | Azure Cognitive Services, Bing Search, Azure AI Search |

---

## 9. Copilot 생태계

### 9.1 제품별 Copilot

| 제품 | 대상 | 기능 |
|------|------|------|
| **Microsoft 365 Copilot** | 오피스 사용자 | Word/Excel/PPT/Outlook/Teams AI 보조 |
| **GitHub Copilot** | 개발자 | 코드 생성, Agent 모드, Workspace |
| **Copilot Studio** | 비즈니스 | 노코드 에이전트 빌더, 커스텀 Copilot |
| **Windows Copilot** | PC 사용자 | OS 레벨 AI 어시스턴트 |
| **Dynamics 365 Copilot** | 비즈니스 | CRM/ERP AI 보조 |
| **Security Copilot** | 보안 팀 | 보안 이벤트 분석, 위협 탐지 |

### 9.2 GitHub Copilot 진화

| 버전/기능 | 설명 |
|-----------|------|
| **Copilot Chat** | IDE 내 대화형 코딩 도우미 |
| **Copilot Workspace** | 이슈→계획→코드→PR 전체 워크플로 |
| **Agent Mode** | 자율적 멀티파일 편집, 터미널 명령 실행 |
| **코드 리뷰** | PR 자동 리뷰, 보안 취약점 탐지 |
| **모델 선택** | GPT-4o, Claude 3.5, Gemini 등 선택 가능 |
| **MCP 지원** | MCP 서버 연결로 외부 도구 통합 |

---

## 10. Phi 시리즈 — 소형 모델

| 모델 | 크기 | 핵심 |
|------|------|------|
| Phi-1 | 1.3B | 코드 생성 특화 |
| Phi-2 | 2.7B | 범용 추론 |
| Phi-3 mini/small/medium | 3.8B/7B/14B | **GPT-3.5 수준 성능**, 모바일 실행 가능 |
| Phi-3.5 MoE | 42B | MoE 아키텍처 도입 |
| **Phi-4** | 14B | **수학/추론 특화**, GPT-4 수준의 특정 태스크 |
| Phi-4-mini | 3.8B | 모바일/엣지 최적화 |

Phi 시리즈의 전략적 의미는 **"소형 모델로도 충분한 작업에 대해 비용 효율적 대안을 제공"** 하는 것입니다. 온디바이스 AI, 프라이버시 중시 환경에서 특히 유용합니다.

---

## 11. 인프라 투자

| 항목 | 내용 |
|------|------|
| CapEx (2025) | **$80B+** (Azure AI 인프라) |
| OpenAI 투자 | 총 $13B+ |
| 자체 칩 | **Maia 100** (AI 가속기), **Cobalt** (ARM CPU) |
| 데이터센터 | 전 세계 60+ 리전 |
| 에너지 | 원자력/핵융합 전력 계약 (Three Mile Island 재가동 등) |

---

## 12. 경쟁 구도 비교

| 영역 | AWS | Microsoft/Azure | Google Cloud | Databricks |
|------|-----|----------------|-------------|-----------|
| **AI 모델** | Nova + Anthropic | OpenAI | Gemini (자체) | OSS + External |
| **Agent 플랫폼** | Bedrock Agents | Copilot Studio | Agent Builder | Agent Bricks |
| **개발자 도구** | Q Developer | GitHub Copilot | Jules | AI Dev Kit |
| **자체 칩** | Trainium2/Inferentia2 | Maia 100 | TPU v6 | N/A |
| **클라우드 점유율** | **32% (1위)** | 23% (2위) | 12% (3위) | 데이터 플랫폼 |
| **차별점** | 모델 다양성 + 인프라 | Office 통합 + OpenAI | 수직 통합 + 연구 | 데이터 레이크 |

---

## 13. 향후 전망

### AWS

| 영역 | 전망 |
|------|------|
| Nova 모델 | 성능 지속 향상, Premier 정식 출시 |
| Trainium3 | NVIDIA B200 경쟁 |
| Bedrock | Agent 고도화, MCP 지원 확대 |
| Anthropic | Claude 차세대 모델 Bedrock 독점 초기 제공 |

### Microsoft

| 영역 | 전망 |
|------|------|
| Copilot | 더 많은 Office 제품에 확산, Agent 자율성 증가 |
| GitHub Copilot | Codex/Claude Code 경쟁에서 Agent 모드 강화 |
| Phi-5 | 소형 모델 성능 한계 지속 돌파 |
| OpenAI 관계 | 영리 전환 후 파트너십 재정의 |

{% hint style="info" %}
**Databricks 시사점**: Databricks는 클라우드 중립적 데이터 플랫폼으로, AWS/Azure/GCP 모두에서 동일하게 운영됩니다. AI Gateway를 통해 OpenAI, Anthropic, Google 모델을 통합 관리할 수 있으며, 이는 특정 클라우드의 AI 서비스에 종속되지 않는 핵심 차별점입니다. Unity Catalog + Delta Lake 위에서 AI Agent를 구축하면 데이터 거버넌스와 AI를 동시에 해결할 수 있습니다.
{% endhint %}

---

**참고 자료:**
- [AWS re:Invent 2024 블로그](https://aws.amazon.com/blogs/aws/)
- [Amazon Nova 발표](https://aws.amazon.com/ai/generative-ai/nova/)
- [Amazon Bedrock 문서](https://docs.aws.amazon.com/bedrock/)
- [Microsoft Copilot](https://copilot.microsoft.com/)
- [GitHub Copilot](https://github.com/features/copilot)
- [Phi-4 기술 보고서](https://www.microsoft.com/en-us/research/publication/phi-4-technical-report/)
- [AI Agent 업계 동향 — AWS, Microsoft & Meta](../guides/genai-concepts/agent-landscape/aws-others.md)
