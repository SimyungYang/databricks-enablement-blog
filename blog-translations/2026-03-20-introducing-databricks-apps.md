---
original_title: "Introducing Databricks Apps: The fastest and most secure way to build data and AI applications"
authors: "Andre Furlan Bueno, Patrick Wendell, Shanku Niyogi, Akhil Gupta, Nick Kramer, Jackie Zhang"
date: "2024-10-08"
category: "Platform & Products & Announcements"
original_url: "https://www.databricks.com/blog/introducing-databricks-apps"
translated_date: "2026-04-07"
---

> **원문**: [Introducing Databricks Apps: The fastest and most secure way to build data and AI applications](https://www.databricks.com/blog/introducing-databricks-apps)

# Databricks Apps 소개: 데이터 및 AI 애플리케이션을 구축하는 가장 빠르고 안전한 방법

**게시일**: 2024년 10월 8일
**저자**: Andre Furlan Bueno, Patrick Wendell, Shanku Niyogi, Akhil Gupta, Nick Kramer, Jackie Zhang
**카테고리**: Platform & Products & Announcements | 6분 읽기

---

![Introducing Databricks Apps](https://www.databricks.com/sites/default/files/2025-04/introducing-databricks-apps-2x.png?v=1743579510)

## 요약

- **Databricks Apps** — 내부 데이터 및 AI 애플리케이션을 빌드하고 배포하는 새로운 방법이 AWS 및 Azure에서 **Public Preview**로 출시되었습니다.
- 이상적인 사용 사례로는 데이터 시각화, AI 애플리케이션, 셀프 서비스 분석, 데이터 품질 모니터링이 있습니다.
- Dash, Shiny, Gradio, Streamlit, Flask 등의 앱 개발 프레임워크를 지원합니다.
- 서버리스(Serverless) 컴퓨팅의 자동 프로비저닝으로 손쉬운 앱 배포가 가능합니다.
- Unity Catalog를 통한 내장 거버넌스(Governance), OIDC/OAuth 2.0 및 SSO를 통한 안전한 사용자 인증을 제공합니다.

---

오늘, 저희는 **Databricks Apps** 의 Public Preview 출시를 발표하게 되어 매우 기쁩니다. Databricks Apps는 데이터 및 AI 팀이 Databricks Data Intelligence Platform 위에서 내부 애플리케이션을 직접 빌드하고 배포하는 가장 빠른 방법입니다. Databricks Apps를 사용하면 개발자들이 Dash, Shiny, Gradio, Streamlit, Flask와 같은 인기 있는 프레임워크를 통해 Databricks 환경 내에서 네이티브하게 앱을 구축할 수 있습니다.

Databricks Apps의 핵심 장점 중 하나는 SQL 대신 코드를 사용하여 비기술적 사용자를 위한 데이터 애플리케이션을 제작할 수 있다는 점입니다. 이를 통해 조직 내 더 넓은 구성원에게 복잡한 데이터 인사이트를 전달할 수 있는 새로운 가능성이 열립니다. 예를 들어, 마케팅 팀은 Databricks Apps를 활용해 캠페인 성과 지표를 시각화하는 맞춤형 대시보드를 만들 수 있고, 기술적 배경이 없는 팀원들도 데이터를 쉽게 해석하고 행동에 옮길 수 있습니다.

나아가 Databricks Apps는 AI 컴포넌트를 통합할 수 있어, 더 많은 유연성이 필요할 때 개발자가 특정 AI 모델을 호출하는 것이 가능합니다. 이러한 AI 역량의 통합으로 고객 피드백에 대한 감성 분석이나 매출 예측을 위한 예측 모델링 같은 고도화된 작업을 수행하는 정교한 애플리케이션 개발이 가능해지며, 비기술적 사용자를 위한 데이터 인사이트의 가치를 한층 높여줍니다.

한번 빌드된 앱은 Databricks 내에서 완전히 배포되고 관리되어, 팀이 인프라를 구성·관리하는 수고를 덜어줍니다. 이 앱들은 Unity Catalog에 이미 구성된 데이터 접근 제어를 준수하며 완전히 거버넌스되고, 동일한 통합 거버넌스 모델을 사용하여 사용자에 대한 배포를 제어합니다. Databricks Apps를 통해 조직은 Databricks 환경 내에서 원활하게 실행되는 커스텀 애플리케이션을 만들어 데이터와 AI 투자의 완전한 잠재력을 이끌어낼 수 있습니다.

---

## 데이터 애플리케이션 구축의 어려움

오늘날 데이터 중심의 세계에서, 조직들은 데이터 자산에서 더 많은 가치를 추출하는 방법을 찾고 있습니다. 하지만 내부 데이터 애플리케이션을 구축하고 배포하는 것은 전통적으로 복잡하고 시간이 많이 걸리는 과정이었습니다. 개발자들은 앱 개발에 집중하는 대신 인프라 관리에 시간을 소비해야 합니다. 데이터 거버넌스와 컴플라이언스는 접근 제어의 수동 구현을 요구합니다. 게다가 앱 공유 및 권한 관리는 다른 데이터 자산과 분리되어 처리되어, 파편화된 거버넌스 경험을 만들어냅니다.

---

## Databricks Apps: 빠르고 안전한 데이터 애플리케이션 구축

Databricks Apps는 이러한 과제들을 정면으로 해결하며, 내부 데이터 애플리케이션을 구축하기 위한 강력하면서도 단순한 경험을 제공합니다. Databricks Apps를 도입함으로써 조직은 다양한 이점을 누릴 수 있습니다.

### 간편한 구축 (Simple to Build)

![firstgif](https://www.databricks.com/sites/default/files/inline-images/smallersizetopImage.gif)

Databricks Apps는 Databricks 환경 내에서 직접 실행되는 앱을 구축하는 데 도움을 줍니다. 개발자들은 **Visual Studio Code** 나 **PyCharm** 같은 도구를 사용하여 데이터와 AI 모델에 원활하게 접근할 수 있습니다. Databricks Apps를 통해 데이터 과학자와 엔지니어들은 Dash, Gradio, Streamlit 같은 익숙한 Python 프레임워크를 사용하여 앱을 신속하게 구축하고 반복할 수 있습니다. 또한 유연한 앱을 빠르게 만들 수 있는 사전 제작 Python 템플릿(Pre-built Python Template)을 선택할 수도 있습니다.

> "Databricks Apps는 제 RAG(Retrieval-Augmented Generation) 개념 증명(Proof of Concept)을 세련되고 브랜딩된 애플리케이션으로 전환하는 데 도움을 주었습니다. 저희는 회사의 방대한 지식 베이스를 활용하여 사용자 질문에 답변하는 RAG 시스템을 구축했습니다."
>
> — **Heather Gomer**, SAE International

### 프로덕션 준비 및 자동화된 배포 (Production Ready and Automated Deployment)

![production](https://www.databricks.com/sites/default/files/inline-images/productionready.gif)

Databricks Apps는 개발자가 추가 인프라를 구축할 필요가 없습니다. 앱은 자동으로 프로비저닝되는 서버리스 컴퓨팅(Serverless Compute) 위에서 실행되어 손쉬운 배포가 가능합니다. 또한 Databricks Apps는 업계 최고 수준의 개발 관행을 수용하여, 선호하는 워크플로우와의 원활한 통합을 제공합니다. Databricks 워크스페이스 내에서 직접 작업하든 즐겨 쓰는 IDE를 활용하든, Git 버전 관리와 CI/CD 파이프라인을 지원하여 내부 앱이 프로덕션 준비 상태임을 보장합니다.

일단 생성되면, Databricks Apps는 발견과 접근을 단순화합니다. 앱이 배포되면 개발자가 의도한 사용자들과 쉽게 공유할 수 있는 고유 URL이 생성되어 애플리케이션에 직접 접근할 수 있습니다.

![discover](https://www.databricks.com/sites/default/files/inline-images/discover_0.png)

또한 조직 내 사용자들은 "compute" 탭으로 이동한 다음 "apps" 탭을 선택하여 동료들이 만든 앱을 발견할 수 있어, 내부 앱 탐색이 가능해집니다.

> "Databricks Apps의 DevOps 프로세스와의 원활한 통합 덕분에 사용자에게 새로운 기능을 빠르게 시연하고 테스트할 수 있으면서도, 추가 인프라 없이 내부 애플리케이션을 위한 안전하고 프로덕션 준비된 프론트엔드를 제공할 수 있었습니다."
>
> — **Lukas Heidegger**, E.ON Digital Technology

### 내장 거버넌스 (Built-in Governance)

![diagram](https://www.databricks.com/sites/default/files/inline-images/diagram.png)

Databricks Apps를 사용하면 데이터는 사용자가 공유를 선택하지 않는 한 Databricks 환경 밖으로 나가지 않습니다. 각 앱은 다음을 포함한 강력한 보안 조치로 강화됩니다:

- **세분화된 접근 제어(Granular Access Control)**: 정밀한 데이터 권한 보장
- **자동 관리 서비스 프린시펄(Automatically Managed Service Principal)**: 애플리케이션 간 안전한 통신
- **자동 사용자 인증(Automatic User Authentication)**: OIDC/OAuth 2.0 및 SSO를 활용한 원활하고 안전한 사용자 접근

나아가 Unity Catalog의 리니지(Lineage) 기능을 통합하여 애플리케이션의 데이터 출처, 변환, 사용에 대한 포괄적인 가시성을 제공하며, 데이터 추적성과 컴플라이언스를 강화합니다. 이 통합된 접근 방식은 데이터 애플리케이션이 조직 정책과 규제 요건을 준수하는 동시에 팀 간 데이터 발견과 데이터 활용을 촉진합니다.

> "Databricks Apps를 사용함으로써 보안 및 인프라 팀과의 수많은 검토 과정을 절약하고, 프로덕션 환경의 이해관계자들과 즉시 앱을 공유할 수 있었습니다."
>
> — **Cesar Augusto Charalla Olazo**, Addi

---

## 일반적인 앱 패턴 (Common App Patterns)

Databricks Apps는 다양한 내부 애플리케이션을 구축하는 데 활용할 수 있습니다:

- **커스텀 데이터 시각화(Custom Data Visualization)**: 비즈니스 사용자가 데이터를 실시간으로 탐색하고 분석할 수 있는 동적이고 데이터 기반의 시각화를 만듭니다.
- **AI 앱(AI Apps)**: 예지보전(Predictive Maintenance), 고객 세분화(Customer Segmentation), 사기 탐지(Fraud Detection) 같은 작업을 위해 머신러닝 모델을 활용하는 애플리케이션을 개발합니다.
- **셀프 서비스 분석(Self-Service Analytics)**: 사용자 친화적인 인터페이스를 통해 비즈니스 사용자가 복잡한 분석을 수행할 수 있게 하여, 데이터 팀의 부담을 줄입니다.
- **데이터 품질 모니터(Data Quality Monitors)**: 데이터 품질을 추적하고 개선하기 위한 커스텀 도구를 구축합니다.

> "저희는 Databricks Apps를 활용하여 Health, Safety & Environment Intelligence Platform의 사용자 대면 데이터 인터페이스를 완전히 구현했습니다. 현재 시맨틱 검색 도구를 포함한 Streamlit 대시보드와 다양한 다른 대시보드를 호스팅하고 있습니다."
>
> — **Lukas Heidegger**, E.ON Digital Technology

---

## 파트너 의견

> "Posit(2024 Databricks Developer Tools Partner of the Year 수상)은 코드 우선(Code-First) 도구를 사용하여 애플리케이션을 만들어 조직이 데이터에서 인사이트를 도출하도록 돕는 힘을 오랫동안 믿어왔습니다. 이 믿음이 R용 Shiny, Python용 Shiny, Posit Connect의 탄생을 이끌었으며, 다양한 애플리케이션을 지원하기 위한 Databricks Apps와의 협력으로 이어졌습니다. 코드 우선 도구를 최대한 보편적이고 접근 가능하게 만들기 위해 Databricks와의 지속적인 파트너십을 기대합니다."
>
> — **Tareef Kawaf**, CEO, Posit

> "Plotly(2024 Databricks Customer Impact Partner of the Year 수상)는 Databricks Apps의 출시를 환영하며 분석 전문가들이 비즈니스 사용자를 지원할 수 있게 된 것을 축하합니다. Databricks Apps는 Databricks 고객들이 Plotly의 Dash 오픈 소스 라이브러리와 함께 Databricks를 사용하여 Plotly의 Dash Enterprise 제품이 제공하는 다양한 정교한 프로덕션급 데이터 앱 사용 사례를 향해 나아가는 여정을 시작하기 쉬운 방법을 제공합니다."
>
> — **Dave Gibbon**, Sr. Director - Strategic Partnerships, Plotly

---

## Databricks Apps 시작하기

![getstarted](https://www.databricks.com/sites/default/files/inline-images/getstarted.png)

Databricks Apps는 이제 지원 리전의 모든 워크스페이스에서 사용 가능합니다. 첫 번째 앱을 작성하려면 **+ New** 로 이동하여 **Apps** 를 클릭하세요. 화면의 안내를 따르고, 즐겨 사용하는 소스 코드 편집기로 변경 사항을 적용한 후 배포하면 됩니다! 모든 기능에 대한 자세한 내용은 문서(리전 가용성: [AWS](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/), [Azure](https://docs.databricks.com/azure/en/dev-tools/databricks-apps/))를 참고하세요.

Databricks Apps로 무엇을 만드실지 기대가 됩니다. 지금 바로 강력하고 데이터 기반의 애플리케이션 구축을 시작하여 조직을 위한 새로운 가능성을 열어보세요.

실제 동작을 보고 싶으신가요? **Databricks Apps Product Tour** 를 통해 Dash, Shiny, Gradio, Streamlit, Flask 등의 인기 프레임워크를 사용하여 Databricks에서 네이티브하게 앱을 빌드해보세요.
