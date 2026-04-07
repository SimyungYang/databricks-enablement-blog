---
original_title: "Announcing managed MCP servers with Unity Catalog and Mosaic AI Integration"
authors: "Databricks"
date: "2025-06-18"
category: "Product"
original_url: "https://www.databricks.com/blog/announcing-managed-mcp-servers-unity-catalog-and-mosaic-ai-integration"
translated_date: "2026-04-07"
note: "요청하신 URL(insights-deploying-mcp-scale-lessons-our-production-environment)은 404로 존재하지 않습니다. Databricks 공식 사이트맵 기준, MCP 관련 가장 유사한 포스트인 이 글로 대체합니다."
---

# Unity Catalog와 Mosaic AI가 통합된 관리형 MCP 서버 발표

> **원문**: [Announcing managed MCP servers with Unity Catalog and Mosaic AI Integration](https://www.databricks.com/blog/announcing-managed-mcp-servers-unity-catalog-and-mosaic-ai-integration)

**AI 모델이 강력한 거버넌스를 갖춘 채로 외부 도구와 데이터에 안전하게 접근할 수 있도록 합니다.**

## 요약

- Agent Bricks와 AI Playground를 사용하여 MCP로 에이전트를 빌드하고 배포하세요
- 도구를 포함한 에이전트를 빌드하고 배포하기 위해 자체 MCP 서버를 직접 호스팅하세요
- UC Functions, Genie 스페이스, Vector Search 인덱스에 대한 Databricks 관리형 서버를 활용하여 에이전트를 데이터에 연결하세요

Model Context Protocol(MCP)은 최근 몇 달 동안 LLM에 도구를 제공하기 위한 표준으로서 업계 전반에 걸쳐 열렬한 호응을 받으며 급부상했습니다. 이는 LLM이 보다 자연스러운 형태로 행동을 취하는 데 필요한 컨텍스트를 제공한다는 점에서 중요한 진보입니다. 그러나 전 세계의 기업들은 거버넌스, 보안, 검색 가능성을 희생하지 않고 MCP를 활용하는 방법을 고민하고 있습니다. 에이전트에 비즈니스 컨텍스트를 제공하면서도 데이터를 안전하게 유지해야 합니다. 인증 및 권한 부여, 접근, 제어에 관한 질문들이 소용돌이치고 있습니다.

저희는 MCP를 적극 수용하고 이를 Unity Catalog와 Mosaic AI의 강력함과 결합하게 되어 기쁩니다. 이를 통해 모든 것의 장점을 누릴 수 있습니다. 에이전트가 행동을 취하기 위한 MCP, 에이전트를 빌드하고 평가하기 위한 Mosaic AI, 그리고 거버넌스와 검색을 위한 Unity Catalog가 함께합니다. 이제 여러분은 조직의 보안과 거버넌스를 존중하는 방식으로 에이전트에 데이터 인텔리전스를 제공할 수 있습니다.

이번 출시를 통해 저희는 MCP의 어려운 부분을 여러분 대신 처리합니다. 저희의 관리형 서버는 기본적으로 사용자를 대신한(on-behalf-of-user) 인증을 지원하며, 이미 Unity Catalog에 설정한 거버넌스를 그대로 존중합니다. 또한 손쉬운 호스팅을 위해 Databricks Apps에서 OAuth를 표준으로 지원하며, Playground는 빠른 프로토타이핑을 위한 안전한 환경입니다.

## 안전한 데이터 접근을 위한 Databricks 관리형 서버 활용

저희의 초기 관리형 서버 세트는 Genie, Vector Search, UC Functions를 통해 Databricks의 데이터에 안전하게 접근할 수 있도록 합니다. 엔터프라이즈급 보안을 염두에 두고 구축된 저희의 관리형 MCP 서버는 자동으로 사용자 권한을 존중합니다. 즉, 여러분은 Unity Catalog에서 모든 데이터를 계속 관리하면서 별도의 관리 장소 없이 MCP를 활용할 수 있습니다.

통신사의 지원 담당자를 돕는 고객 지원 에이전트를 구축한다고 상상해 보세요. Unity Catalog의 정형 및 비정형 데이터를 활용하여 에이전트를 더욱 스마트하게 만들 수 있습니다.

- **Genie** 는 계정 및 요금제 정보와 같은 정형 데이터에 접근할 수 있도록 합니다
- **Vector Search** 는 지원 및 지식 베이스 문서와 같은 비정형 데이터에 접근할 수 있도록 합니다
- **UC Functions** 는 청구 관련 질문에 답하기 위한 결정론적 함수를 구축할 수 있게 합니다

![Databricks 관리형 MCP 서버 개요](https://www.databricks.com/sites/default/files/inline-images/image5_24.png?v=1750206659)

이 서버들은 또한 유지보수나 관리가 필요 없이 저희가 직접 관리합니다. MCP 표준이 계속 진화함에 따라 저희는 최신 기능을 지원하도록 업데이트할 것입니다. 이를 통해 여러분은 조직에서 중요한 것에 에너지를 집중할 수 있습니다.

## Databricks Apps로 자체 MCP 서버 안전하게 호스팅하기

통신사 지원 에이전트를 계속 구축해 보겠습니다. 현재 장애 상황을 알려주고 새 장애를 보고할 수 있는 내부 API가 있지만, 이 모든 정보는 에이전트가 접근하기 어려운 인프라 내부에 갇혀 있습니다.

바로 이 지점에서 Databricks Apps가 에이전트에 생명력을 불어넣습니다. 기본 제공되는 OAuth 지원, 간편한 Git 기반 배포, 내장된 권한 및 거버넌스를 갖춘 Databricks Apps를 통해 레거시 서비스와 API를 불과 몇 분 안에 MCP 서버로 전환할 수 있습니다. Databricks Apps는 저희의 서버리스 인프라 위에 직접 구축되어 있어, 에이전트 사용량이 늘어나더라도 확장성에 대해 걱정할 필요가 없습니다.

![Databricks Apps를 통한 MCP 서버 호스팅](https://www.databricks.com/sites/default/files/inline-images/image3_50.png?v=1750206659)

오늘 시작하려면 Marketplace에서 사용하기 쉬운 MCP 서버 템플릿을 사용해 보세요.

## Agent Bricks 또는 AI Playground로 MCP 에이전트 빌드 및 배포하기

Databricks는 MCP를 활용하여 에이전트를 빌드하고 배포하기 쉽게 만들어 줍니다. Agent Bricks의 Supervisor Agent는 Databricks Apps에서 구축한 MCP 서버를 지원하여, 단 버튼 클릭 한 번으로 에이전트를 내부 서비스와 연결할 수 있습니다.

![Agent Bricks Supervisor Agent와 MCP 통합](https://www.databricks.com/sites/default/files/inline-images/image6_14.png?v=1750206659)

또한 AI Playground를 사용하여 MCP로 에이전트를 프로토타이핑할 수 있어, 코드를 한 줄도 작성하기 전에 MCP 서버와 에이전트 로직을 모두 테스트할 수 있습니다. 도구 지원 LLM이 있는 경우 "Tools" 드롭다운을 사용하여 저희의 관리형 서버 또는 Databricks Apps를 통한 커스텀 서버를 시험해 보세요.

![AI Playground에서 MCP 프로토타이핑](https://www.databricks.com/sites/default/files/inline-images/image1_16.gif?v=1750206659)

Databricks를 사용하여 에이전트를 배포하면, MLflow와 Agent Evaluation을 통해 어떤 도구가 어떻게 사용되는지 쉽게 확인할 수 있습니다. 이를 통해 에이전트 로직이나 도구 로직을 사용 사례에 맞게 조정할 수 있으며, 에이전트가 어떻게 동작하는지 완전한 가시성을 확보할 수 있습니다.

![MLflow와 Agent Evaluation을 통한 에이전트 모니터링](https://www.databricks.com/sites/default/files/inline-images/image4_33.png?v=1750206659)

## 향후 확장 계획

저희는 이번에 출시하는 것들에 매우 흥분되어 있으며, 이제 막 시작에 불과합니다. 앞으로 DBSQL과 같은 다른 유형의 Databricks 리소스에 대한 관리형 서버 지원을 확장할 계획입니다. 또한 다른 회사와 서비스가 제공하는 MCP 서버를 관리, 검색, 거버넌스하기 위한 카탈로그 지원을 구축할 계획입니다. 이를 통해 오늘 작업하는 곳에서 모든 것을 중앙화할 수 있습니다.

## 시작하기

Databricks 관리형 MCP 서버는 현재 Beta로 제공됩니다. 관리형 서버에 연결하거나 Databricks Apps에서 자체 MCP 서버를 호스팅하는 방법에 대한 자세한 내용은 [공식 문서](https://docs.databricks.com/aws/en/generative-ai/mcp/)를 참조하세요.
