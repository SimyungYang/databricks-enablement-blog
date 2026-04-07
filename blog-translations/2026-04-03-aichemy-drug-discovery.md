# AiChemy: MCP, Skills, 맞춤형 데이터를 활용한 신약 개발을 위한 차세대 에이전트

**저자**: Yen Low, Sean Zhang
**날짜**: 2026년 4월 3일
**원문**: [Databricks Blog](https://www.databricks.com/blog/aichemy-next-generation-agent-mcp-skills-and-custom-data-drug-discovery)

![AiChemy Hero Image](https://www.databricks.com/sites/default/files/2026-04/aichemy-next-generation-agent-mcp-skills-custom-data-drug-discovery-blog-og.png)

---

**요약**: Databricks 위에서 외부 지식 베이스(OpenTargets, PubChem, PubMed)를 Model Context Protocol(MCP)을 통해 Databricks의 정형/비정형 데이터와 통합하는 멀티 에이전트 시스템, AiChemy를 구축하는 방법을 안내합니다. 이 시스템이 해결하는 과제는 다양한 AI 에이전트들의 자율적인 협업을 통해 방대하고 이질적인 데이터셋을 분석하고 추적 가능한 근거 기반의 결과를 제공함으로써 학제 간 신약 개발 연구를 가속화하는 것입니다. 연구자들은 질환 타겟을 식별하고, 약물 후보를 평가하며, 상세한 특성 정보를 검색하고, 안전성 평가를 수행할 수 있어 보다 효율적인 신약 개발 및 리드(lead) 발굴이 가능해집니다.

---

## 멀티 에이전트 시스템이 학제 간 연구를 가속화한다

여러 분야의 전문가 팀처럼 협업하는 멀티 에이전트 AI 시스템이 방대한 데이터셋을 자율적으로 탐색하여 새로운 패턴과 가설을 발견하는 모습을 상상해보세요. 이제 이것은 Model Context Protocol(MCP) 덕분에 손쉽게 실현 가능합니다. MCP는 다양한 데이터 소스와 도구를 쉽게 통합하기 위한 새로운 표준입니다. 지식 베이스부터 리포트 생성기까지, 점점 성장하는 MCP 서버 생태계는 무한한 가능성을 제공합니다.

### AiChemy란 무엇인가

AiChemy를 소개합니다. AiChemy는 OpenTargets, PubChem, PubMed와 같은 외부 MCP 서버를 Databricks 위의 자체 화학 라이브러리와 결합하여, 통합된 지식 베이스를 함께 분석하고 해석할 수 있게 해주는 멀티 에이전트 어시스턴트입니다. 또한 선택적으로 로드할 수 있는 Skills를 통해 연구, 규제, 또는 비즈니스 목적에 맞게 일관된 형식의 태스크 특화 리포트를 작성하기 위한 상세한 지침을 제공합니다.

주요 기능으로는 질환 타겟 및 약물 후보 식별, 상세한 화학적·약동학적 특성 검색, 안전성 및 독성 평가가 있습니다. 특히 AiChemy는 검증 가능한 데이터 소스까지 추적 가능한 근거를 기반으로 결과를 제시하므로 연구 목적에 최적화되어 있습니다.

### 활용 사례 1: 질환 메커니즘 이해, 약물 가능 타겟 발굴 및 리드 생성

Guided Tasks 패널은 질환 → 타겟 → 약물 → 문헌 검증이라는 신약 개발 워크플로우의 핵심 단계를 수행하기 위한 필요한 프롬프트와 에이전트 Skills를 제공합니다.

**치료 타겟 식별**: 에스트로겐 수용체 양성(ER+)/HER2 음성(HER2-) 유방암(ER과 HER2는 주요 단백질 바이오마커)과 같은 특정 질환 서브타입에서 시작하여, 관련 치료 타겟(예: ESR1)을 찾습니다.

**연관 약물 탐색**: 식별된 타겟(예: ESR1)을 사용하여 잠재적인 약물 후보를 찾습니다.

**문헌을 통한 검증**: 특정 약물 후보(예: camizestrant)에 대해 이를 뒷받침하는 근거를 과학 문헌에서 확인합니다.

### 활용 사례 2: 화학적 유사성을 이용한 리드 생성

2023년 승인된 경구용 선택적 에스트로겐 수용체 조절제(SERM)인 Elacestrant의 후속 약물을 찾기 위해 화학적 유사성을 활용할 수 있습니다. 정량적 구조-활성 관계(QSAR) 원리에 따르면 구조적으로 유사한 분자는 유사한 특성을 공유할 것으로 예측되므로, Elacestrant와 구조적으로 유사한 약물 유사 분자를 대규모 ZINC15 화학 라이브러리에서 검색합니다. 이는 Databricks Vector Search를 쿼리함으로써 구현되는데, Elacestrant의 1024비트 Extended-Connectivity Fingerprint(ECFP) 분자 임베딩을 쿼리 벡터로 사용하여 ZINC의 25만 분자 인덱스 내에서 가장 유사한 임베딩을 찾습니다.

---

## 나만의 연구용 멀티 에이전트 수퍼바이저 구축하기

공개 MCP 서버와 Databricks의 자체 데이터를 통합하여 Databricks 위에서 멀티 에이전트 수퍼바이저를 커스터마이징합니다. 이를 위해 노코드(no-code) Agent Bricks 또는 Notebooks와 같은 코딩 방식을 선택할 수 있습니다. Databricks Playground를 활용하면 에이전트의 빠른 프로토타이핑과 반복 실험이 가능합니다.

### Step 1: 멀티 에이전트 수퍼바이저 구성 요소 준비

멀티 에이전트 시스템은 5개의 워커(worker)로 구성됩니다:

1. **OpenTargets**: 질환-타겟-약물 지식 그래프의 외부 MCP 서버
2. **PubMed**: 생의학 문헌의 외부 MCP 서버
3. **PubChem**: 화학 화합물의 외부 MCP 서버
4. **Drug Library (Genie)**: 정형화된 약물 특성을 담은 화학 라이브러리로, text-to-SQL 기능을 제공하는 Genie 스페이스로 구성
5. **Chemical Library (Vector Search)**: 분자 지문(fingerprint) 임베딩이 포함된 비정형 화학 데이터의 자체 라이브러리로, 임베딩 기반 유사도 검색을 위한 벡터 인덱스로 구성

**Step 1a**: UI 또는 Databricks Notebook(예: `4_connect_ext_mcp_opentarget.py`)에서 Unity Catalog(UC) 연결을 통해 공개 MCP 서버에 안전하게 연결합니다.

**Step 1b**: 정형 테이블(예: DrugBank)이 UI에서 text-to-SQL 기능을 갖춘 Genie 스페이스로 변환되어 있는지 확인합니다.

**Step 1c**: 비정형 화학 라이브러리가 UI 또는 Notebook에서 유사도 검색을 위한 벡터 인덱스로 생성되어 있는지 확인합니다.

### Step 2 (간편 방식): 노코드 Supervisor Agent로 2분 만에 멀티 에이전트 수퍼바이저 구축

구성 요소를 조합하려면 노코드 Agent Bricks를 사용해보세요. UI를 통해 위의 구성 요소들로 수퍼바이저 에이전트를 구축하고 REST API 엔드포인트로 배포하는 모든 과정이 몇 분 안에 완료됩니다.

### Step 2 (고급 방식): Databricks Notebooks를 사용한 멀티 에이전트 수퍼바이저 구축

에이전트 메모리(agentic memory)와 Skills 같은 고급 기능을 원한다면, Databricks Notebooks에서 Langgraph 수퍼바이저를 개발하여 Databricks Serverless Postgres 데이터베이스인 Lakebase와 통합합니다. 이 코드 저장소를 확인하면 `config.yml`에서 멀티 에이전트 구성 요소를 간단하게 정의할 수 있습니다. `config.yml`이 정의되면 멀티 에이전트 수퍼바이저를 React 웹 사용자 인터페이스(UI)를 갖춘 MLflow AgentServer(FastAPI 래퍼)로 배포할 수 있습니다. UI 또는 Databricks CLI를 통해 Databricks Apps에 두 가지를 모두 배포하세요. 사용자가 Databricks App을 사용할 수 있도록, 그리고 앱의 서비스 프린시펄(service principal)이 기반 리소스에 접근할 수 있도록 적절한 권한을 설정합니다.

### Step 3: 에이전트 평가 및 모니터링

에이전트에 대한 모든 호출은 OpenTelemetry 표준을 사용하여 Databricks MLflow 실험에 자동으로 로깅되고 추적됩니다. 이를 통해 에이전트를 지속적으로 개선하기 위한 오프라인 또는 온라인 응답 평가가 쉽게 가능해집니다. 또한 배포된 멀티 에이전트는 AI Gateway 뒤에 있는 LLM을 사용하므로 중앙 집중식 거버넌스, 내장된 안전장치, 그리고 프로덕션 준비 상태를 위한 완전한 가시성의 이점을 누릴 수 있습니다.

---

## 다음 단계

AiChemy 웹 앱(https://aichemy-1.onrender.com/)과 Github 저장소(https://github.com/databricks-industry-solutions/aichemy)를 탐색해보시기 바랍니다. Databricks의 직관적인 노코드 Agent Bricks 프레임워크로 나만의 멀티 에이전트 시스템을 구축하기 시작하세요. 이제 방대한 데이터를 일일이 뒤지는 것을 멈추고 진정한 발견을 시작할 수 있습니다!

**주요 링크**:

- **Agent Bricks**: https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor
- **Lakebase**: https://docs.databricks.com/aws/en/generative-ai/agent-framework/stateful-agents
- **MLflow traces**: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/
- **AI Gateway**: https://www.databricks.com/product/artificial-intelligence/ai-gateway
