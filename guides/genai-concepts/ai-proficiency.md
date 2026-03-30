# AI Proficiency & 성숙도 모델

AI Proficiency는 조직이 AI를 얼마나 효과적으로 활용하고 있는지를 측정하는 성숙도 프레임워크입니다. 현재 위치를 진단하고, 다음 단계로 나아가기 위한 로드맵을 수립하는 데 활용합니다.

{% hint style="info" %}
성숙도 진단은 기술뿐 아니라 **조직 문화, 프로세스, 거버넌스**를 함께 평가해야 합니다.
{% endhint %}

---

## AI Proficiency란?

AI Proficiency는 단순히 "AI 기술을 사용하는가"가 아니라, **AI를 비즈니스 가치로 전환하는 조직 역량**을 의미합니다.

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

## 단계별 Databricks 기능 매핑

### Level 1: Exploring (탐색)

| 활동 | Databricks 기능 |
|------|-----------------|
| LLM 실험 | AI Playground — 다양한 모델을 UI에서 테스트 |
| 데이터 탐색 | Unity Catalog — 사내 데이터 자산 탐색 |
| 빠른 프로토타입 | Notebooks + Foundation Model APIs |
| 팀 학습 | Databricks Academy, 가이드 문서 |

### Level 2: Building (구축)

| 활동 | Databricks 기능 |
|------|-----------------|
| RAG 개발 | Vector Search + Agent Framework |
| Agent 구축 | Mosaic AI Agent Framework |
| 모델 커스텀 | Fine-tuning (Mosaic AI Training) |
| 실험 추적 | MLflow Tracking & Tracing |
| 프롬프트 관리 | MLflow Prompt Registry |

### Level 3: Scaling (확장)

| 활동 | Databricks 기능 |
|------|-----------------|
| 모델 배포 | Model Serving (Serverless) |
| 성능 모니터링 | Lakehouse Monitoring, Inference Tables |
| 품질 평가 | MLflow Evaluate, Review App |
| 접근 제어 | Unity Catalog 권한 관리 |
| 비용 관리 | Serverless 자동 스케일링, 예산 모니터링 |

### Level 4: Transforming (전환)

| 활동 | Databricks 기능 |
|------|-----------------|
| 멀티에이전트 시스템 | Supervisor Agent, A2A 연동 |
| 업무 자동화 | Databricks Workflows + Agent |
| 셀프서비스 AI | Genie Space, Databricks Apps |
| AI 거버넌스 | Unity Catalog, AI Guardrails |

---

## 조직 AI 성숙도 진단 체크리스트

{% hint style="warning" %}
아래 체크리스트는 자가 진단용입니다. 각 항목에 해당하는지 체크하고, 가장 많이 해당하는 레벨이 현재 수준입니다.
{% endhint %}

### Level 1 진단

- [ ] LLM 또는 GenAI 도구를 업무에 사용한 경험이 있다
- [ ] AI/ML에 관심있는 팀원이 있다
- [ ] 데이터가 중앙 저장소에 관리되고 있다
- [ ] AI PoC 프로젝트를 1개 이상 진행했다

### Level 2 진단

- [ ] RAG 또는 Agent 기반 애플리케이션을 개발했다
- [ ] MLflow로 실험을 추적하고 있다
- [ ] 사내 데이터를 활용한 AI 서비스가 있다
- [ ] 프롬프트를 체계적으로 관리하고 있다

### Level 3 진단

- [ ] AI 모델이 프로덕션 환경에서 서빙되고 있다
- [ ] 모델 성능을 정기적으로 모니터링한다
- [ ] AI 시스템에 대한 접근 제어와 감사 로그가 있다
- [ ] CI/CD 파이프라인으로 모델을 배포한다

### Level 4 진단

- [ ] AI가 핵심 비즈니스 프로세스에 통합되어 있다
- [ ] 비기술 부서도 AI 도구를 일상적으로 사용한다
- [ ] 멀티에이전트 시스템이 운영되고 있다
- [ ] AI 관련 거버넌스 정책이 수립되어 있다

---

## 참고 자료

- [Databricks Generative AI 문서](https://docs.databricks.com/en/generative-ai/index.html)
- [Gartner AI Maturity Model](https://www.gartner.com/en/articles/an-ai-maturity-model-to-help-plan-enterprise-ai)
- [McKinsey - The State of AI](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)
