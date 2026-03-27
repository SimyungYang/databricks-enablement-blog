# <img src="https://www.databricks.com/wp-content/uploads/2022/06/db-nav-logo.svg" alt="Databricks" width="160"> Enablements

Databricks 고객을 위한 기술 가이드, 핸즈온 자료, 아키텍처 레퍼런스 모음입니다.

> **Databricks Korea Field Engineering**

---

## 이 프로젝트에 대하여

### 목적

Databricks를 도입하거나 운영 중인 고객이 **직접 참고할 수 있는 실전 가이드**를 제공합니다. 공식 문서(docs.databricks.com)의 내용을 기반으로 하되, 실제 구성 절차와 운영 노하우를 한국어로 정리하여 고객의 빠른 온보딩을 지원합니다.

### 대상 독자

* Databricks를 신규 도입하는 고객 (인프라/플랫폼 팀)
* Databricks 기능을 평가하거나 PoC를 진행하는 팀
* 운영 중인 고객 중 신규 기능(Genie, Agent Bricks, Apps 등)을 검토하는 팀

### 콘텐츠 구성

| 카테고리 | 설명 |
|---------|------|
| **Platform Setup** | AWS/Azure 환경에서 Workspace 구성, PrivateLink, Unity Catalog 등 인프라 셋업 가이드 |
| **GenAI & Tools** | Genie Space, Genie Code, Agent Bricks, AI Dev Kit 등 AI 기능 사용 가이드 |
| **Analytics** | 플랫폼 비교, SQL 분석, 대시보드 등 분석 관련 가이드 |

### 특징

* **매뉴얼 설치 기준** — AWS Console + Databricks Account Console 기반 (Terraform은 Appendix)
* **근거 문서 링크** — 모든 섹션에 Databricks 공식 문서 링크 포함
* **ap-northeast-2 (서울) 리전 기준** — VPC Endpoint Service Name 등 리전별 값 명시
* **슬라이드 + 문서** — 주요 가이드는 웹 슬라이드(Marp) 또는 PDF로도 제공
* **지속 업데이트** — 고객 요청 및 신규 기능에 따라 가이드 추가

### 관련 프로젝트

| 프로젝트 | 설명 |
|---------|------|
| [Databricks 종합 교육 자료](https://github.com/SimyungYang/simyung-dbx-training) | 데이터 기초부터 AI 에이전트까지 — Databricks 공식 문서 대체용 교육 자료 (GitBook) |
| [슬라이드 & PDF 모음](https://simyungyang.github.io/databricks-enablement-blog/) | 가이드별 웹 슬라이드 및 PDF 다운로드 (GitHub Pages) |

---

## 가이드 목록

| 날짜 | 가이드 | 주제 | 슬라이드/PDF |
|------|--------|------|-------------|
| 2026-03-27 | [AWS Workspace 구성 가이드](platform-setup/aws-workspace-setup.md) | Platform Setup | [슬라이드](https://simyungyang.github.io/databricks-enablement-blog/aws-workspace-setup.html) |
| 2026-03-27 | [Databricks Apps 사용 가이드](platform-setup/databricks-apps-guide.md) | Platform Setup | — |
| 2026-03-27 | [Genie Space & Genie Code 사용 가이드](analytics/genie-space-genie-code-guide.md) | GenAI & Tools | [PDF](https://simyungyang.github.io/databricks-enablement-blog/genai-intro.pdf) |
| 2026-03-27 | [Agent Bricks 사용 가이드](genai/agent-bricks-guide.md) | GenAI & Tools | — |
| 2026-03-27 | [Analytics Platform 비교](analytics/platform-comparison.md) | Analytics | [슬라이드](https://simyungyang.github.io/databricks-enablement-blog/analytics-platform-comparison.html) |
| 2026-03-18 | [Databricks GenAI 소개 — AI Dev Kit](genai/genie-code-ai-dev-kit.md) | GenAI & Tools | [PDF](https://simyungyang.github.io/databricks-enablement-blog/ai-dev-kit-guide.pdf) |
