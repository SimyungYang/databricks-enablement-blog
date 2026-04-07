> **원문**: [Introducing Genie Code](https://www.databricks.com/blog/introducing-genie-code)

---

# Genie Code 소개

| 항목 | 내용 |
| --- | --- |
| **원문 제목** | Introducing Genie Code |
| **저자** | Patrick Wendell, Matei Zaharia, Weston Hutchins, Gal Oshri |
| **발행일** | 2026년 3월 11일 |
| **원문 URL** | https://www.databricks.com/blog/introducing-genie-code |

---

![Introducing Genie Code](https://www.databricks.com/sites/default/files/2026-03/Announcement-GenieCode-Databricks-PR-OG-02.png?v=1772830491)

## 요약

- Genie Code는 데이터를 위해 특별히 설계된 최첨단 AI 에이전트입니다. 실제 데이터 사이언스 작업을 대상으로 한 내부 벤치마크에서, Genie Code는 선도적인 코딩 에이전트 대비 성공률을 2배 이상 달성했습니다.
- Lakeflow 파이프라인과 AI 모델을 백그라운드에서 능동적으로 유지·최적화하며, 장애를 분류하고 이상 징후를 조사합니다. 사람이 개입하기 전에 에이전트 트레이스를 자율적으로 분석하여 환각(hallucination)을 수정하고 리소스 할당을 튜닝합니다.
- Genie Code는 데이터가 어디에 있든 함께 작동합니다. Unity Catalog와 Lakehouse Federation을 통해 Databricks, 외부 플랫폼, 온프레미스 시스템에 걸친 데이터를 완전한 거버넌스와 함께 이해합니다. MCP를 통해 Jira, Confluence, GitHub 같은 외부 도구에 연결함으로써, Databricks 워크스페이스를 넘어서는 자율적인 워크플로우를 가능하게 합니다.

---

Databricks Genie 제품군의 최신 구성원인 **Genie Code** 를 발표하게 되어 기쁩니다. 지난 6개월 동안 에이전틱 코딩 도구는 소프트웨어 엔지니어링을 근본적으로 변화시켰으며, Genie Code는 그와 동일한 변혁을 데이터 팀에 가져옵니다. Genie Code는 파이프라인 구축, 장애 디버깅, 대시보드 배포, 프로덕션 시스템 유지 관리 등 복잡한 작업을 자율적으로 수행할 수 있습니다.

단순히 코드 작성에만 집중하는 에이전트와 달리, Genie Code는 능동적인 프로덕션 에이전트로서도 동작합니다. 백그라운드에서 Lakeflow 파이프라인과 AI 모델을 모니터링하고, 팀이 인지하기 전에 장애를 분류하고, 정기적인 DBR 업그레이드를 처리하며, 이상 징후를 조사합니다.

이 모든 것은 Unity Catalog와의 긴밀한 통합을 통해 이루어지며, 덕분에 Genie Code는 기업의 데이터, 시맨틱, 거버넌스 정책을 깊이 이해합니다. Genie Code는 실제 데이터 사이언스 작업에서 선도적인 코딩 에이전트를 2배 이상 뛰어넘는 성능을 보입니다.

---

## 에이전틱 데이터 작업의 부상

에이전틱 코딩 도구는 소프트웨어 엔지니어링을 변혁했으며, 개발자들을 자동완성을 넘어 에이전트 주도 개발로 이동시켰습니다. 단 하나의 프롬프트만으로 엔지니어는 이제 수초 내에 기능을 스캐폴딩하고, 코드를 리팩터링하며, 프로토타입을 배포할 수 있습니다. 이러한 변화는 LLM의 발전과 현대 소프트웨어 코드베이스의 복잡한 컨텍스트를 해석할 수 있는 에이전틱 시스템에 의해 이끌어졌습니다.

시중의 대부분의 에이전트는 코드 자체를 최종 산출물로 봅니다. 그러나 데이터 팀에게 코드는 단지 기저의 데이터를 조작하고 이해하기 위한 수단일 뿐입니다. 이것이 바로 소프트웨어 중심 에이전트가 데이터 작업에서 종종 어려움을 겪는 이유입니다. 데이터 생태계에서 컨텍스트는 스크립트뿐만 아니라 사용 패턴, 리니지(lineage), 비즈니스 시맨틱에도 존재합니다.

이 컨텍스트에 접근하는 것은 매우 중요합니다. 왜냐하면 그 결과가 높은 영향을 미치기 때문입니다. 대시보드는 비즈니스 의사결정을 이끌고, 파이프라인은 프로덕션 시스템을 가동하며, 머신러닝 모델은 실제 세계의 결과에 영향을 미칩니다. 데이터 팀에게 에이전트가 제공하는 속도와 레버리지는 절대적인 정확성, 재현성, 거버넌스와 반드시 함께해야 합니다.

Genie Code는 데이터를 위해 특별히 설계된 AI 에이전트입니다. Unity Catalog를 활용하여 작업 중 가장 관련성 높은 데이터와 콘텐츠를 자동으로 선별합니다. 개인화된 검색 인덱스, 커스텀 지침, 지식 저장소를 생성하고, 리니지로부터 사용 패턴을 추출합니다. 무엇보다도, 팀이 더 많이 사용할수록 더 스마트해집니다. Unity Catalog와의 이 깊은 통합은 단순히 외부에서 데이터를 읽는 어떤 시스템보다도 훨씬 우월합니다.

Databricks에서는 기술적 사용자와 비기술적 사용자 모두에 걸쳐 Genie와 Genie Code의 영향을 직접 경험했습니다. 영업팀은 미팅 전에 모든 고객의 완전한 현황을 파악하기 위해 이를 활용하며, 주요 소비 지표, 지원 티켓, 최근 인터랙션을 몇 초 만에 요약합니다. 제품 관리자들은 Genie Code를 사용해 차트와 그래프의 손으로 그린 스케치에서 대시보드를 구축합니다. 재무팀은 예산 대비 실적 분석과 고급 ROI 모델링을 수행합니다. 경영진은 전략적 논의 중 실시간으로 데이터 질문에 답하며, 후속 작업을 줄이고 복잡한 의사결정을 가속화합니다. 회사 전반에 걸쳐 이 도구들은 우리가 데이터를 다루는 방식을 변화시켰습니다.

---

## Genie Code가 하는 일

- **전문 머신러닝 엔지니어로서 활동**: Genie Code는 엔드-투-엔드로 전체 ML 워크플로우를 처리합니다. 복잡한 문제를 추론하여 모델을 계획·작성·배포하며, MLflow에 실험을 기록하고 피크 성능을 위해 서빙 엔드포인트를 파인튜닝합니다.
- **깊은 데이터 엔지니어링 전문성**: 초보 엔지니어가 테스트 데이터에서만 작동하는 스크립트를 작성하는 것과 달리, Genie Code는 시니어 아키텍트처럼 설계합니다. 스테이징과 프로덕션 환경의 차이를 고려하고, 변경 데이터 캡처(CDC) 워크플로우를 구축하며 데이터 품질 기대치를 적용합니다.
- **능동적인 유지 관리 및 최적화**: Genie Code는 백그라운드에서 Lakeflow 파이프라인과 AI 모델을 모니터링하여 장애를 분류하고 이상 징후를 조사합니다. 사람이 개입하기 전에 에이전트 트레이스를 자율적으로 분석하여 환각을 수정하고 리소스 할당을 튜닝합니다.
- **기업 컨텍스트 이해**: Unity Catalog와 통합되어 Genie Code는 기존 거버넌스 정책과 접근 제어를 준수합니다. 비즈니스 시맨틱과 감사 요건을 이해하고, 외부 플랫폼의 데이터를 포함한 엔터프라이즈 데이터를 페더레이션합니다.
- **시간이 지날수록 개선**: Genie Code는 팀이 더 많이 사용할수록 더 스마트해집니다. 지속적인 메모리를 통해 과거의 인터랙션과 코딩 선호도를 기반으로 내부 지침을 자동으로 업데이트합니다. 내부 데이터 사이언스 작업에서 Genie Code는 선도적인 코딩 에이전트를 77.1% 대 32.1%의 품질 점수로 능가합니다.

Genie Code를 통해 데이터 팀은 코파일럿에게 프롬프트를 입력하는 것에서 실제 업무를 위임하는 것으로 전환합니다: 파이프라인 구축, 장애 디버깅, 대시보드 배포, 프로덕션 시스템 유지 관리를 자율적으로, 엔드-투-엔드로 수행합니다.

{% hint style="info" %}
**SiriusXM 고객 사례**

"SiriusXM에서 Genie Code는 노트북 작성과 복잡한 SQL부터 테이블 관계 추론 및 파이프라인 디버깅까지 모든 것을 지원합니다. 데이터 팀이 더 짧은 시간에 고품질 작업을 제공할 수 있도록 돕는 실질적인 개발 파트너 역할을 합니다."

— Bernie Graham, Vice President, Data, Sirius XM
{% endhint %}

---

## 데이터와 AI 작업을 위한 최고 품질의 에이전트

Genie Code는 단일 모델로 구동되지 않습니다. 여러 모델과 도구에 걸쳐 작업을 라우팅하는 에이전틱 시스템으로, 프런티어 LLM, 오픈소스 모델, Databricks에서 호스팅되는 커스텀 모델 등 각 작업에 가장 적합한 모델을 자동으로 선택합니다. 이를 통해 사용자는 수동으로 모델을 전환하거나 어떤 모델이 최선의 결과를 낼지 추측할 필요가 없습니다.

Genie Code는 또한 Databricks API와 깊이 통합되어 있어, 올바른 데이터 에셋을 식별하고 풍부한 컨텍스트를 조합하며 더 높은 품질의 쿼리를 생성합니다. Databricks Research는 선도적인 AI 랩의 최신 모델을 플랫폼에서 실행되는 커스텀 모델과 함께 벤치마킹하며 시스템을 지속적으로 튜닝합니다.

내부 사용자로부터 수집된 실제 데이터 사이언스 및 분석 작업에 대한 최근 성능 벤치마킹에서, Genie Code는 Databricks MCP(Model Context Protocol) 서버를 장착한 선도적인 코딩 에이전트를 크게 능가했습니다.

![Genie Code solved 77.1% of tasks vs other coding agents](https://www.databricks.com/sites/default/files/inline-images/genie-code-task-completions-chart-2x_2.png)

아래 표는 두 에이전트의 성능 비교를 보여줍니다. Genie Code가 선도적인 코딩 에이전트 대비 작업 해결률에서 2배 이상 높은 성과를 달성했음을 확인할 수 있습니다.

| 에이전트 | 작업 해결률 |
| --- | --- |
| **Genie Code** | **77.1%** |
| Leading Coding Agent + Databricks MCP | 32.1% |

이 결과는 단순한 코드 생성 능력의 차이가 아니라, 데이터 생태계 전반에 대한 깊은 이해와 통합이 얼마나 중요한지를 보여줍니다.

---

## Genie Code가 지원하는 데이터 작업의 전체 라이프사이클

### 머신러닝 모델 학습 및 평가

![Use Genie Code to train and evaluate Machine Learning models](https://www.databricks.com/sites/default/files/inline-images/ML_150zoom_0.png)

Genie Code는 워크플로우에 내장된 전담 ML 엔지니어 역할을 합니다. "판매 예측 모델을 @sales_table 을 사용하여 학습해줘"라고 요청하면, 전체 파이프라인을 추론하여 실행합니다:

- 특성을 식별하고 프로파일링
- 훈련, 검증, 테스트 데이터셋을 올바르게 분리
- 여러 모델 유형을 학습하고 비교하며, 가능한 최선의 모델을 학습하기 위해 하이퍼파라미터 탐색 실행
- AUC, F1, RMSE, R² 등의 지표 전반에 걸쳐 결과 평가
- 특성 중요도, 혼동 행렬, ROC 커브에 대한 플롯 생성
- MLflow에 실험 추적
- 모델 진단을 기반으로 개선 사항 권장

Databricks Model Serving에 배포된 후에도 Genie Code는 계속 관여합니다: 엔드포인트 상태를 확인하고, 트레이스를 분석하며, 최적화를 권장합니다. 이에 대한 자세한 내용은 아래의 "코드에서 프로덕션으로: Genie Code를 활용한 옵저버빌리티" 섹션에서 확인할 수 있습니다.

{% hint style="info" %}
**Repsol 고객 사례**

"Genie Code는 우리 데이터 팀의 운영 방식을 변화시킵니다. 노트북, 파이프라인, 모델을 수동으로 연결하는 대신, 우리의 데이터, 거버넌스, 비즈니스 컨텍스트, 그리고 Repsol Artificial Intelligence Products 같은 내부 라이브러리를 이해하는 AI 파트너에게 복잡한 워크플로우를 위임할 수 있습니다. 엄격함과 통제를 희생하지 않고 시계열 예측부터 프로덕션 배포까지 모든 것을 가속화합니다."

— Emilio Martín Gallardo, Principal Data Scientist, Data Management & Analytics, Repsol
{% endhint %}

---

### 프로덕션 수준의 데이터 파이프라인 생성

![Create Lakeflow Spark Declarative Pipelines with Genie Code](https://www.databricks.com/sites/default/files/inline-images/Pipelines_150zoom_option2_1.png)

Genie Code는 안정적인 데이터 파이프라인을 설계하고 발전시킬 수 있도록 돕는 전문 데이터 엔지니어입니다.

- **자연어로 파이프라인 생성**: 필요한 것을 설명하면 Genie Code가 수집, 변환, 데이터 품질 기대치가 내장된 완전한 Spark Declarative Pipeline을 생성합니다.
- **기존 파이프라인 확장**: 현재 파이프라인의 컨텍스트 내에서 데이터셋 추가, 변환 수정, AutoCDC 플로우 작성, Auto Loader 구성, 데이터 품질 기대치 적용이 모두 가능합니다.
- **파이프라인 동작 이해**: 출력을 검사하고, 다운스트림 테이블로의 데이터 흐름을 추적하며, 행 수나 스키마의 예상치 못한 변경 사항을 표면화합니다.

{% hint style="info" %}
**글로벌 인프라 기술 기업 고객 사례**

"Genie Code는 우리를 보조적인 코딩을 넘어 진정한 에이전틱 데이터 엔지니어링으로 이동시켰습니다. Lakeflow 파이프라인을 분석하고, 다중 파일 변경 사항을 diff와 함께 제안하며, 안전장치를 갖추고 실행하고, 문제가 해결될 때까지 장애를 반복적으로 해결합니다. 자동완성이라기보다는 워크플로우에 내장된 협력자처럼 느껴집니다."

— Nishit Gajjar, Tech Lead, Global Infrastructure Technology Provider
{% endhint %}

---

### 재사용 가능한 시맨틱 정의로 대시보드 생성

![Create AI/BI Dashboards with Genie Code](https://www.databricks.com/sites/default/files/inline-images/Dashboard_150zoom_0.png)

Genie Code는 시각화를 생성하고, 필터를 구성하며, 재사용 가능한 시맨틱 정의와 함께 다중 페이지 대시보드 레이아웃을 구성할 수 있습니다. 이러한 정의를 대시보드가 성장하면서 확장되는 필터, 계산, 레이아웃에 연결함으로써, 팀이 더 빠르게 움직이는 동시에 일관성을 유지하도록 돕습니다.

{% hint style="info" %}
**Bechtel Corporation 고객 사례**

"Genie Code를 통해 우리 팀은 몇 달이 아닌 몇 주 만에 AI 기반 분석과 자동화된 워크플로우를 제공하고 있습니다. 로우코드 에이전트는 거버넌스에 맞게 정렬된 상태를 유지하면서 더 빠르게 움직일 수 있게 해주며, 프로젝트 및 엔지니어링 팀이 배포 속도를 늦추지 않고 복잡한 데이터에서 자연어 인사이트를 얻을 수 있도록 합니다."

— Russell Singer, Chief Data Architect, Bechtel Corporation
{% endhint %}

---

### 자율적인 다단계 계획 및 실행

![Genie Code performs autonomous multi-step planning and execution](https://www.databricks.com/sites/default/files/inline-images/agentplan_0.png)

"항공편 지연 위험을 식별하고 모니터링 대시보드를 구축해"와 같은 고수준 목표를 제공하면, Genie Code가 요건을 추론하고, 다단계 계획을 수립하며, 단일 대화 스레드에서 모든 Databricks Notebook, AI/BI Dashboard, Lakeflow에 걸쳐 실행합니다.

{% hint style="info" %}
**Danfoss 고객 사례**

"Danfoss에서 우리가 보고 있는 것은 Genie Code가 데이터 팀 내 역할을 변화시키며, 디지털화와 AI에 대한 우리의 전략적 초점을 지원한다는 것입니다. 데이터 과학자들은 여전히 방향을 제시하고 검토하지만, 엔지니어, 분석가, 도메인 전문가들이 이제 어시스턴트와 함께 노트북에서 능동적으로 작업하고 고급 분석 워크플로우에 기여할 수 있습니다. 데이터 사이언스를 훨씬 더 협력적인 팀 활동으로 만들어줍니다."

— Radu Dragusin, Principal Engineer, Data & AI, Danfoss
{% endhint %}

---

### 깊은 컨텍스트 검색을 통한 탐색적 데이터 분석

![Use Genie Code to perform exploratory data analysis](https://www.databricks.com/sites/default/files/inline-images/EDA_150zoom_0.png)

Genie Code는 인기도, 리니지, 코드 샘플, Unity Catalog 메타데이터를 사용하여 모든 분석에 가장 관련성 높은 데이터셋을 찾습니다. 이 깊은 컨텍스트 검색은 데이터를 수동으로 찾는 번거로운 작업을 없애주고, 조직 내에서 가장 정확하고 자주 사용되는 테이블을 기반으로 작업이 이루어지도록 보장합니다.

{% hint style="info" %}
**Sundt Construction 고객 사례**

"정말 매혹적입니다. Genie Code는 데이터 작업이 어떻게 이루어질 것인지 미래를 엿보는 것 같습니다."

— Sameer Yasser, Sr. Data Engineer, Sundt Construction
{% endhint %}

---

## 커스터마이제이션과 확장성

Genie Code는 팀의 특정 기준과 외부 기술 스택에 맞게 조정할 수 있도록 설계된 유연한 플랫폼입니다. 그 역량을 확장하는 세 가지 주요 방법이 있습니다.

### MCP(Model Context Protocol)를 통한 외부 도구 연결

![Genie Code supports MCP](https://www.databricks.com/sites/default/files/inline-images/Jira_edited_condensed_0.png)

Genie Code는 **MCP(Model Context Protocol)** 를 지원합니다. MCP는 외부 도구, API, 문서와 안전하게 상호작용할 수 있도록 하는 개방형 표준입니다. 이를 통해 Databricks 워크스페이스를 넘어서는 자율적인 워크플로우가 가능합니다.

예를 들어, 새로운 ML 모델을 학습하라는 Jira 작업이 할당되면, Genie Code는 자동으로 컨텍스트를 수집하고, 작업을 수행하며, 결과로 티켓을 업데이트할 수 있습니다.

MCP를 통해 내부 Confluence, Google Drive, GitHub, 또는 Notion에 Genie를 연결하면, 문제 해결 시 팀의 특정 런북(runbook)과 데이터 사전을 참조할 수 있습니다.

### Agent Skills: 도메인별 역량 정의

도메인별 역량을 정의하여 Genie Code에게 복잡한 작업을 일관되게 수행하는 방법을 가르칩니다. 회사가 PII 마스킹을 처리하는 특정 방식이든, 데이터 검증을 위한 커스텀 프레임워크든, Skills는 AI가 조직의 모범 사례를 매번 따르도록 보장합니다. Skills는 오픈 Agent Skills 형식을 따릅니다.

### Memory: 사용할수록 더 스마트해지는 에이전트

Genie Code는 더 많이 사용할수록 더 스마트해집니다. 지속적인 메모리를 통해 에이전트는 과거의 인터랙션을 기반으로 내부 지침을 자동으로 업데이트합니다. 코딩 선호도를 학습하고, 가장 자주 사용하는 데이터셋을 기억하며, 세션에 걸쳐 컨텍스트를 유지합니다.

---

## 코드에서 프로덕션으로: Genie Code를 활용한 옵저버빌리티

코드 작성은 첫 번째 단계에 불과합니다. 코드를 유지 관리하는 것이 진짜 도전입니다. Genie Code는 옵저버빌리티 에이전트로서 데이터 및 AI 워크플로우를 건강하게 유지합니다. 수천 명의 고객이 정교한 AI 애플리케이션을 서빙하기 위해 Databricks를 사용하지만, 프로덕션에서 이러한 모델을 디버깅하는 것은 종종 라이프사이클에서 가장 시간이 많이 소요되는 부분입니다.

Genie Code는 이제 Databricks Model Serving과 MLflow 3.0과 직접 통합하여 이 프로세스를 자동화합니다. 로그와 트레이스를 수동으로 검색하는 대신, 다음을 위해 Genie를 활용할 수 있습니다:

![Perform endpoint health checks using Genie Code](https://www.databricks.com/sites/default/files/inline-images/genie-observability-demo_0.png)

- **엔드포인트 상태 확인**: 단일 프롬프트로 컴퓨팅, 요청 처리, 서버 로그 전반에 걸친 전체 상태 보고서를 얻습니다.
- **에이전트 품질 분석**: 복잡한 에이전트 트레이스에 걸쳐 환각, 잘못된 도구 호출, 사용자 불만 패턴과 같은 미묘한 문제를 실시간으로 표면화합니다.
- **프로덕션 문제 해결**: 인시던트가 발생하면, Genie는 서버 로그와 지표를 교차 참조하여 1차 진단을 자동화하고 해결 시간을 단축합니다.
- **엔드포인트 최적화**: Databricks 모범 사례를 기반으로 프로비저닝된 동시성, 하드웨어 구성, 자동 확장에 대한 권장 사항을 제공합니다.

![Perform agent quality analysis with Genie Code](https://www.databricks.com/sites/default/files/inline-images/tracing-agent-updated_0.png)

위 이미지는 Genie Code가 에이전트 트레이스를 분석하여 품질 문제를 식별하는 방식을 보여줍니다. 복잡한 멀티-에이전트 시스템에서도 환각이나 잘못된 도구 호출과 같은 문제를 자동으로 식별하고 수정 방안을 제안합니다.

---

## 워크로드를 건강하게 유지하는 백그라운드 에이전트

Genie Code는 백그라운드에서 작동하도록 설계되어, 노트북을 닫은 후에도 데이터가 건강하게 유지됩니다. 여러 에이전트를 병렬로 배포하여 데이터 엔지니어의 한 주를 전형적으로 소비하는 운영 작업을 처리할 수 있습니다. 이러한 백그라운드 에이전트는 작업 장애에 대응하고 정기적인 업그레이드를 관리하는 등 반복적인 작업을 처리함으로써, 반응적인 지원을 넘어 능동적인 유지 관리로 나아갑니다. 파이프라인이 중단되면, 에이전트는 근본 원인을 파악하고 안전한 샌드박스 환경에서 검증한 후에만 수정 방안을 제안합니다.

예를 들어, 컬럼이 INT(150)에서 STRING("150 USD")로 변경되는 등의 스키마 불일치로 인해 프로덕션 파이프라인이 실패하면, Genie Code는 장애를 정확히 파악하고 손상된 파이프라인을 자동으로 수정합니다.

{% hint style="warning" %}
**백그라운드 에이전트는 곧 출시될 예정입니다.**
{% endhint %}

---

## Unity Catalog 기반: 통합 보안 및 거버넌스

Genie Code는 Unity Catalog 위에 직접 구축되었습니다. 이 통합을 통해 에이전트는 Databricks 플랫폼의 나머지 부분과 동일한 보안 및 거버넌스 규칙을 따릅니다.

Genie Code가 데이터를 검색할 때, 사용자가 접근 권한을 가진 에셋만 표면화합니다. 파이프라인을 구축할 때는 기존 리니지와 접근 제어를 준수합니다.

- **기본 제공 리비전 히스토리**: 모든 편집은 Databricks 버전 관리 시스템을 통해 추적됩니다. 노트북, 쿼리, 파일, Lakeflow 파이프라인에 걸쳐 전체적인 신뢰로 변경 사항을 롤백할 수 있습니다.
- **내장 가드레일**: Genie Code는 기저 테이블을 수정할 수 있는 코드를 실행하기 전에 능동적으로 확인을 요청하도록 설계되었습니다.
- **접근 제어 시행**: Genie Code는 사용자가 볼 권한이 없는 데이터 에셋을 절대 노출하지 않습니다.
- **포괄적인 감사 로깅**: 조직은 기존 감사 인프라를 통해 Genie Code가 어떻게 사용되고 있는지에 대한 완전한 가시성을 유지합니다.

---

## 지금 바로 워크스페이스에서 사용 가능

Genie Code는 지금 바로 Databricks 워크스페이스에서 **일반 제공(Generally Available)** 됩니다. 복잡한 구성 없이도 오늘 노트북, SQL 편집기, Lakeflow Pipelines 편집기에서 Genie Code 패널을 찾을 수 있습니다.

---

## 더 알아보기

Genie Code에 대해 더 알고 싶다면:

- **웹 페이지 방문**: Genie Code의 주요 기능과 사용 사례를 이해하고, Databricks 플랫폼 전반에서 어떻게 작동하는지 알아보세요.
- **데모 시청**: Genie Code가 실제 데이터 워크플로우를 엔드-투-엔드로 계획하고 실행하는 것을 확인하세요.
- **문서 읽기**: 오늘 자신의 워크스페이스에서 Genie Code를 사용하기 시작하세요.

Genie Code로 무엇을 구축할지, 그리고 자율적인 에이전트가 Databricks에서 데이터 팀의 작업 방식을 어떻게 재편할지 기대됩니다.
