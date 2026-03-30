# Table of contents

* [가이드 목록](README.md)

## 환경 구성 가이드

* [AWS Workspace 구성](platform-setup/aws/README.md)
  * [Marketplace 구독](platform-setup/aws/marketplace.md)
  * [사전 준비](platform-setup/aws/prerequisites.md)
  * [Credential 구성](platform-setup/aws/credential.md)
  * [Storage 구성](platform-setup/aws/storage.md)
  * [Network 구성](platform-setup/aws/network.md)
  * [Backend PrivateLink](platform-setup/aws/privatelink-backend.md)
  * [Frontend PrivateLink](platform-setup/aws/privatelink-frontend.md)
  * [Workspace 생성](platform-setup/aws/workspace.md)
  * [Unity Catalog](platform-setup/aws/unity-catalog.md)
  * [Serverless NCC](platform-setup/aws/serverless-ncc.md)
  * [기존 WS에 PrivateLink 추가](platform-setup/aws/privatelink-migration.md)
  * [Terraform 자동화](platform-setup/aws/terraform.md)
* [Azure Workspace 구성](platform-setup/azure/README.md)
  * [사전 준비](platform-setup/azure/prerequisites.md)
  * [Resource Group](platform-setup/azure/resource-group.md)
  * [Virtual Network](platform-setup/azure/vnet.md)
  * [Access Connector](platform-setup/azure/access-connector.md)
  * [Storage Account](platform-setup/azure/storage-account.md)
  * [Workspace 배포](platform-setup/azure/workspace.md)
  * [Backend Private Link](platform-setup/azure/privatelink.md)
  * [Unity Catalog](platform-setup/azure/unity-catalog.md)

## AI/BI & Analytics

* [Genie Space](guides/genie-space/README.md)
  * [Space 생성](guides/genie-space/create-space.md)
  * [데이터 구성](guides/genie-space/data-config.md)
  * [인스트럭션 작성](guides/genie-space/instructions.md)
  * [테스트 & 벤치마크](guides/genie-space/testing.md)
  * [공유 & 권한](guides/genie-space/sharing.md)
  * [모니터링](guides/genie-space/monitoring.md)
  * [MCP 연동](guides/genie-space/mcp.md)
* [Genie Code](guides/genie-code/README.md)
  * [사용법](guides/genie-code/usage.md)
  * [활용 시나리오](guides/genie-code/scenarios.md)
  * [MCP 연동](guides/genie-code/mcp.md)
  * [Space vs Code 비교](guides/genie-code/comparison.md)
* [Platform 비교](guides/platform-comparison/README.md)
  * [아키텍처](guides/platform-comparison/architecture.md)
  * [컴퓨팅](guides/platform-comparison/compute.md)
  * [데이터 엔지니어링](guides/platform-comparison/data-engineering.md)
  * [SQL & Analytics](guides/platform-comparison/sql-analytics.md)
  * [ML/AI](guides/platform-comparison/ml-ai.md)
  * [거버넌스](guides/platform-comparison/governance.md)
  * [가격 모델](guides/platform-comparison/pricing.md)

## GenAI & Agent

* [Agent Bricks](guides/agent-bricks/README.md)
  * [Knowledge Assistant](guides/agent-bricks/knowledge-assistant.md)
  * [Genie Agent](guides/agent-bricks/genie-agent.md)
  * [Supervisor Agent](guides/agent-bricks/supervisor.md)
  * [평가 & 배포](guides/agent-bricks/evaluation.md)
  * [베스트 프랙티스](guides/agent-bricks/best-practices.md)
* [AI Dev Kit](guides/ai-dev-kit/README.md)

## Compute & Apps

* [Databricks Apps](guides/apps/README.md)
  * [앱 생성](guides/apps/create-app.md)
  * [app.yaml 설정](guides/apps/app-yaml.md)
  * [인증](guides/apps/authentication.md)
  * [리소스 & 환경변수](guides/apps/resources.md)
  * [배포](guides/apps/deployment.md)
  * [예제 (Streamlit, FastAPI)](guides/apps/examples.md)

## 핵심 기술 개념

* [RAG (검색 증강 생성)](guides/rag/README.md)
  * [데이터 준비](guides/rag/data-preparation.md)
  * [청킹 전략](guides/rag/chunking-strategies.md)
  * [Vector Search 설정](guides/rag/vector-search.md)
  * [고급 Retrieval 전략](guides/rag/advanced-retrieval.md)
  * [한국어 RAG 최적화](guides/rag/korean-nlp.md)
  * [RAG 체인 구축](guides/rag/chain-building.md)
  * [RAG 평가](guides/rag/evaluation.md)
  * [RAG 배포](guides/rag/deployment.md)
* [MCP (Model Context Protocol)](guides/mcp/README.md)

## Hands-on Workshop

* [예지보전 & 이상탐지 MLOps](hands-on/predictive-maintenance/README.md)
  * [01. Overview](hands-on/predictive-maintenance/01-overview.md)
  * [02. Feature Engineering](hands-on/predictive-maintenance/02-feature-engineering.md)
  * [03. Model Training](hands-on/predictive-maintenance/03-model-training.md)
  * [04. Model Registration](hands-on/predictive-maintenance/04-model-registration.md)
  * [05. Challenger Validation](hands-on/predictive-maintenance/05-challenger-validation.md)
  * [06. Batch Inference](hands-on/predictive-maintenance/06-batch-inference.md)
  * [07. Anomaly Detection](hands-on/predictive-maintenance/07-anomaly-detection.md)
  * [08. Model Monitoring](hands-on/predictive-maintenance/08-model-monitoring.md)
  * [09. MLOps Agent](hands-on/predictive-maintenance/09-mlops-agent.md)
  * [10. Job Scheduling](hands-on/predictive-maintenance/10-job-scheduling.md)
* [AI Vibe Coding — Smart TV](hands-on/smart-tv-vibe/README.md)
  * [00. 환경 설정](hands-on/smart-tv-vibe/00-setup.md)
  * [01. Foundation](hands-on/smart-tv-vibe/01-foundation.md)
  * [02. Data Engineering](hands-on/smart-tv-vibe/02-data-engineering.md)
  * [03. Analytics](hands-on/smart-tv-vibe/03-analytics.md)
  * [04. Streaming](hands-on/smart-tv-vibe/04-streaming.md)
  * [05. ML](hands-on/smart-tv-vibe/05-ml.md)
  * [06. GenAI](hands-on/smart-tv-vibe/06-genai.md)
  * [07. Apps & Lakebase](hands-on/smart-tv-vibe/07-apps-lakebase.md)

## 참고 자료

* [Databricks 종합 교육 자료 (한글)](https://simyungyang.gitbook.io/databricks-training/)
* [슬라이드 & PDF 모음](https://simyungyang.github.io/databricks-enablement-blog/)
