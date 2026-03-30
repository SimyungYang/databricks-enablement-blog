# AI Proficiency & 성숙도 모델

AI Proficiency는 조직이 AI를 얼마나 효과적으로 활용하고 있는지를 측정하는 성숙도 프레임워크입니다. 현재 위치를 진단하고, 다음 단계로 나아가기 위한 로드맵을 수립하는 데 활용합니다.

{% hint style="info" %}
**학습 목표**
- AI Proficiency의 4단계 모델을 설명하고 각 단계의 특징을 구분할 수 있다
- 조직의 현재 AI 성숙도를 자가 진단할 수 있다
- 다음 단계로의 전환에 필요한 구체적 요건을 파악할 수 있다
- 각 성숙도 단계에 적합한 Databricks 기능을 매핑할 수 있다
{% endhint %}

---

## AI Proficiency란?

AI Proficiency는 단순히 "AI 기술을 사용하는가"가 아니라, **AI를 비즈니스 가치로 전환하는 조직 역량**을 의미합니다.

{% hint style="success" %}
**비유**: 영어를 배우는 것에 비유하면, Level 1은 "Hello"를 아는 수준, Level 2는 일상 대화가 가능한 수준, Level 3은 비즈니스 영어를 구사하는 수준, Level 4는 영어로 협상하고 계약을 체결하는 수준입니다.
{% endhint %}

| 차원 | 설명 |
|------|------|
| **기술 인프라** | 데이터 플랫폼, 컴퓨팅 자원, MLOps 파이프라인 |
| **인력 역량** | AI/ML 전문가, 시민 개발자, AI 리터러시 |
| **프로세스** | 실험 → 개발 → 배포 → 모니터링 워크플로우 |
| **거버넌스** | 데이터 품질, 보안, 규정 준수, 윤리 |

---

## AI 성숙도 4단계 모델

| Level | 단계 | 설명 | 주요 활동 |
|-------|------|------|-----------|
| **1** | Exploring (탐색) | AI 가능성 탐색 | PoC, AI Playground, 프로토타이핑 |
| **2** | Building (구축) | 첫 AI 애플리케이션 개발 | RAG 챗봇, Agent 개발, 파인튜닝 |
| **3** | Scaling (확장) | 프로덕션 AI 시스템 운영 | MLOps, 거버넌스, 모니터링, CI/CD |
| **4** | Transforming (전환) | AI가 비즈니스 프로세스 핵심 | 자동화 워크플로우, AI-native 의사결정 |

---

## 각 레벨별 구체적 기업 사례

### Level 1: Exploring — "AI가 뭔지 알아보는 단계"

**실제 모습**: 데이터팀 리더가 ChatGPT를 써보고 "우리도 이런 거 만들어볼까?"라고 제안. AI Playground에서 여러 모델을 테스트하며 가능성을 탐색.

| 조직 특징 | 설명 |
|-----------|------|
| AI 담당자 | 지정된 AI 담당자 없음, 관심 있는 개인이 실험 |
| 데이터 상태 | 데이터가 여러 시스템에 산재, 통합되지 않음 |
| 사용 방식 | 개인적 ChatGPT/Copilot 사용, 조직 차원 활용 없음 |
| 대표 활동 | PoC 1~2개 진행, 경영진 데모, 기술 학습 |

### Level 2: Building — "첫 번째 AI 앱을 만드는 단계"

**실제 모습**: 데이터팀이 사내 문서 기반 Q&A 챗봇(RAG)을 개발. Vector Search를 구축하고, Agent Framework로 프로토타입 완성. 일부 팀에서 파일럿 사용 중.

| 조직 특징 | 설명 |
|-----------|------|
| AI 담당자 | 2~3명의 ML/AI 엔지니어가 전담 |
| 데이터 상태 | Unity Catalog로 데이터 통합 시작 |
| 사용 방식 | 팀 내부용 AI 앱 1~3개 운영 |
| 대표 활동 | RAG 챗봇, 문서 요약, 코드 리뷰 자동화 |

### Level 3: Scaling — "프로덕션에서 AI를 운영하는 단계"

**실제 모습**: AI 챗봇이 전사 고객 지원에 활용됨. MLflow로 모델 버전 관리, Inference Table로 성능 모니터링. 월간 평가 리포트를 경영진에 보고.

| 조직 특징 | 설명 |
|-----------|------|
| AI 담당자 | AI/MLOps 팀 (5명+) 구성 |
| 데이터 상태 | 통합 거버넌스, 데이터 품질 관리 체계 |
| 사용 방식 | 프로덕션 AI 시스템 3개+ 운영, SLA 관리 |
| 대표 활동 | CI/CD 파이프라인, A/B 테스트, 모니터링 대시보드 |

### Level 4: Transforming — "AI가 비즈니스의 핵심인 단계"

**실제 모습**: 고객 문의 → AI Agent가 자동 분류 → 전문 Agent에 라우팅 → 80%는 자동 처리, 20%만 인간 에스컬레이션. 비기술 부서도 Genie로 데이터 분석을 일상적으로 수행.

| 조직 특징 | 설명 |
|-----------|------|
| AI 담당자 | AI CoE(Center of Excellence) + 각 팀별 AI 챔피언 |
| 데이터 상태 | Data Mesh, 셀프서비스 데이터 접근 |
| 사용 방식 | 비즈니스 프로세스에 AI가 깊이 내재 |
| 대표 활동 | Multi-Agent 시스템, AI 의사결정, 전사 AI 거버넌스 |

---

## 레벨 전환에 필요한 것

### Level 1 → Level 2 전환

| 필요 요소 | 구체적 행동 |
|-----------|------------|
| **데이터 파이프라인** | 핵심 데이터를 Unity Catalog에 통합 |
| **첫 번째 모델/앱** | RAG 챗봇 또는 간단한 Agent PoC → 파일럿 전환 |
| **전담 인력** | AI/ML 엔지니어 1~2명 확보 또는 기존 인력 교육 |
| **실험 환경** | AI Playground + Notebook 기반 실험 환경 구축 |
| **비즈니스 사례** | 경영진이 납득할 ROI 있는 첫 번째 사용 사례 선정 |

### Level 2 → Level 3 전환

| 필요 요소 | 구체적 행동 |
|-----------|------------|
| **MLOps 체계** | MLflow로 실험 추적, 모델 레지스트리, 배포 파이프라인 구축 |
| **거버넌스** | Unity Catalog 권한 관리, 감사 로그, 데이터 리니지 설정 |
| **평가 체계** | MLflow Evaluate로 자동 평가 + Review App으로 인간 피드백 수집 |
| **모니터링** | Inference Table + Lakehouse Monitoring으로 프로덕션 성능 추적 |
| **CI/CD** | 코드 변경 → 자동 테스트 → 자동 배포 파이프라인 |

### Level 3 → Level 4 전환

| 필요 요소 | 구체적 행동 |
|-----------|------------|
| **AI 에이전트** | Multi-Agent 시스템 설계 및 운영 (Supervisor/Swarm 패턴) |
| **비즈니스 프로세스 통합** | 핵심 업무 프로세스에 AI Agent를 임베드 |
| **셀프서비스** | Genie Space, Databricks Apps로 비기술 부서 AI 접근 확대 |
| **AI 거버넌스** | 전사 AI 윤리 정책, Guardrails, 규정 준수 프레임워크 |
| **조직 문화** | "AI-first" 사고방식, 모든 팀에 AI 챔피언 배치 |

---

## 단계별 Databricks 기능 매핑 (상세)

### Level 1: Exploring (탐색)

| 활동 | Databricks 기능 | 구체적 사용 |
|------|-----------------|-------------|
| LLM 실험 | AI Playground | 모델 비교, 프롬프트 테스트, 파라미터 조정 |
| 데이터 탐색 | Unity Catalog | 사내 데이터 자산 검색, 메타데이터 확인 |
| 빠른 프로토타입 | Notebooks + Foundation Model APIs | Python으로 LLM 호출, 간단한 챗봇 프로토타입 |
| 팀 학습 | Databricks Academy | GenAI 기초 과정, 핸즈온 랩 |

### Level 2: Building (구축)

| 활동 | Databricks 기능 | 구체적 사용 |
|------|-----------------|-------------|
| RAG 개발 | Vector Search + Agent Framework | 문서 임베딩, 검색 인덱스 구축, RAG 체인 구현 |
| Agent 구축 | Mosaic AI Agent Framework | ChatAgent 구현, Tool 등록, MLflow Tracing |
| 모델 커스텀 | Fine-tuning (Mosaic AI Training) | 도메인 특화 모델 학습 |
| 실험 추적 | MLflow Tracking & Tracing | 실험 비교, 최적 하이퍼파라미터 탐색 |
| 프롬프트 관리 | MLflow Prompt Registry | 프롬프트 버전 관리, 팀 공유 |

### Level 3: Scaling (확장)

| 활동 | Databricks 기능 | 구체적 사용 |
|------|-----------------|-------------|
| 모델 배포 | Model Serving (Serverless) | 원클릭 배포, 자동 스케일링, A/B 라우팅 |
| 성능 모니터링 | Lakehouse Monitoring + Inference Tables | 지연시간, 토큰 사용량, 오류율 추적 |
| 품질 평가 | MLflow Evaluate + Review App | 자동 평가 + 인간 피드백 수집 |
| 접근 제어 | Unity Catalog 권한 관리 | 테이블/모델/함수별 세밀한 접근 제어 |
| 비용 관리 | Serverless 자동 스케일링 | 사용량 기반 과금, 예산 알림 |

### Level 4: Transforming (전환)

| 활동 | Databricks 기능 | 구체적 사용 |
|------|-----------------|-------------|
| 멀티에이전트 시스템 | Supervisor Agent + A2A 연동 | 복합 작업 자동화, 에이전트 오케스트레이션 |
| 업무 자동화 | Databricks Workflows + Agent | 데이터 파이프라인과 AI Agent 통합 실행 |
| 셀프서비스 AI | Genie Space, Databricks Apps | 비기술 부서 자연어 데이터 분석 |
| AI 거버넌스 | Unity Catalog + AI Guardrails | 전사 AI 정책 적용, 입출력 필터링 |

---

## 조직 AI 성숙도 자가 진단 체크리스트

{% hint style="warning" %}
아래 체크리스트에서 **Yes가 4개 이상**인 레벨이 현재 수준입니다. 현재 레벨의 모든 항목을 충족한 후 다음 레벨로 나아가세요.
{% endhint %}

### Level 1 진단 (Exploring)

| # | 항목 | Yes/No |
|---|------|--------|
| 1 | LLM 또는 GenAI 도구를 업무에 사용한 경험이 있다 | [ ] |
| 2 | AI/ML에 관심있는 팀원이 3명 이상 있다 | [ ] |
| 3 | 데이터가 중앙 저장소(Data Warehouse/Lakehouse)에 관리되고 있다 | [ ] |
| 4 | AI PoC 프로젝트를 1개 이상 진행했다 | [ ] |
| 5 | AI 활용 대상 업무를 3개 이상 식별했다 | [ ] |

### Level 2 진단 (Building)

| # | 항목 | Yes/No |
|---|------|--------|
| 1 | RAG 또는 Agent 기반 애플리케이션을 개발했다 | [ ] |
| 2 | MLflow로 실험을 추적하고 있다 | [ ] |
| 3 | 사내 데이터를 활용한 AI 서비스가 1개 이상 있다 | [ ] |
| 4 | 프롬프트를 체계적으로 관리하고 있다 (버전 관리) | [ ] |
| 5 | Vector Search 또는 유사 임베딩 검색을 구축했다 | [ ] |

### Level 3 진단 (Scaling)

| # | 항목 | Yes/No |
|---|------|--------|
| 1 | AI 모델이 프로덕션 환경에서 서빙되고 있다 (SLA 관리) | [ ] |
| 2 | 모델 성능을 정기적으로 모니터링한다 (대시보드 존재) | [ ] |
| 3 | AI 시스템에 대한 접근 제어와 감사 로그가 있다 | [ ] |
| 4 | CI/CD 파이프라인으로 모델/Agent를 배포한다 | [ ] |
| 5 | MLflow Evaluate 또는 유사 도구로 자동 품질 평가를 수행한다 | [ ] |

### Level 4 진단 (Transforming)

| # | 항목 | Yes/No |
|---|------|--------|
| 1 | AI가 핵심 비즈니스 프로세스에 통합되어 있다 (비용 절감/매출 증가 측정) | [ ] |
| 2 | 비기술 부서도 AI 도구를 일상적으로 사용한다 (Genie 등) | [ ] |
| 3 | 멀티에이전트 시스템이 운영되고 있다 | [ ] |
| 4 | AI 관련 거버넌스 정책이 전사적으로 수립되어 있다 | [ ] |
| 5 | AI CoE(Center of Excellence) 또는 전담 조직이 있다 | [ ] |

---

## 흔한 오해 (Common Misconceptions)

| 오해 | 사실 |
|------|------|
| "Level 4가 반드시 목표여야 한다" | 모든 조직이 Level 4에 도달할 필요는 없습니다. 비즈니스 특성에 따라 Level 3이 최적인 경우도 많습니다. |
| "기술만 갖추면 성숙도가 올라간다" | 기술은 필요조건일 뿐, 프로세스와 조직 문화가 함께 변해야 실질적 성숙도가 향상됩니다. |
| "한 번에 여러 단계를 뛰어넘을 수 있다" | 각 단계는 누적적입니다. Level 1의 기반 없이 Level 3의 MLOps를 구축하면 기술 부채가 쌓입니다. |
| "도구를 구매하면 자동으로 성숙해진다" | Databricks를 도입했다고 자동으로 성숙도가 올라가지 않습니다. 도구를 활용하는 인력과 프로세스가 핵심입니다. |

---

## 연습 문제

1. 현재 소속 조직(또는 고객사)의 AI 성숙도를 자가 진단하고, 근거를 3가지 이상 제시하세요.
2. Level 2에서 Level 3으로 전환할 때 가장 큰 장벽은 무엇이며, 어떻게 극복할 수 있을까요?
3. "AI CoE(Center of Excellence)"의 역할과 구성을 설계하세요. 어떤 직무가 필요하며, 어떤 권한이 필요할까요?
4. Level 1 조직에게 첫 번째 AI PoC 사용 사례를 추천한다면 어떤 것을 제안하겠습니까? 이유와 함께 설명하세요.

---

## 참고 자료

- [Databricks Generative AI 문서](https://docs.databricks.com/en/generative-ai/index.html)
- [Gartner AI Maturity Model](https://www.gartner.com/en/articles/an-ai-maturity-model-to-help-plan-enterprise-ai)
- [McKinsey - The State of AI](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)
- [Databricks AI Cookbook](https://docs.databricks.com/en/generative-ai/tutorials/ai-cookbook/index.html)
