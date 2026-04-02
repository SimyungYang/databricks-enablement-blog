# Databricks Enablement Blog — 프로젝트 지침

## 프로젝트 개요

- **목적**: Databricks 고객을 위한 실전 가이드 & 핸즈온 워크샵 GitBook
- **GitBook**: https://simyungyang.gitbook.io/databricks-enablement-resources/
- **GitHub**: https://github.com/SimyungYang/databricks-enablement-blog
- **Slides**: https://simyungyang.github.io/databricks-enablement-blog/ (GitHub Pages)
- **GitBook API Token**: gb_api_Dzk6HjVVvViyfSDG6Cr0O7DzGOvOyMzjKsJqAGwr
- **Org ID**: 8RMLMcNGbXOmLsKKiQuE / **Space ID**: 2psMwA4xV0JS95ir1vYF / **Site ID**: site_6HFwR

## 관련 프로젝트

- **Databricks 종합 교육 자료**(한글 문서 대체용): https://github.com/SimyungYang/simyung-dbx-training
  - GitBook: https://simyungyang.gitbook.io/databricks-training/
  - 이 enablement blog와 역할 분리: 교육 자료 = 전체 문서 / enablement = 시나리오별 가이드 & 핸즈온

## 디렉토리 구조

```
02-enablement-blog/
├── README.md                          # Home — 가이드 목록 (날짜순)
├── SUMMARY.md                         # GitBook 좌측 메뉴 구조
├── .gitbook.yaml                      # GitBook 설정
├── platform-setup/                    # 환경 구성 가이드
│   ├── aws-workspace-setup.md         # AWS Workspace (PrivateLink, UC 포함)
│   ├── azure-workspace-setup.md       # Azure Workspace (VNet injection, PE 포함)
│   └── databricks-apps-guide.md       # Databricks Apps 사용법
├── analytics/
│   ├── genie-space-genie-code-guide.md # Genie Space 운영 가이드 (MCP 포함)
│   └── platform-comparison.md         # Databricks vs Snowflake/Redshift/BigQuery/Fabric
├── genai/
│   ├── genie-code.md                  # Genie Code 사용법 (MCP 연동)
│   ├── agent-bricks-guide.md          # Agent Bricks (KA, Genie Agent, Supervisor)
│   └── genie-code-ai-dev-kit.md       # AI Dev Kit 소개
├── hands-on/
│   ├── predictive-maintenance/        # MLOps 핸즈온 — 예지보전 & 이상탐지
│   │   ├── README.md                  # 개요 + 파이프라인 흐름
│   │   ├── 01-overview.md ~ 10-job-scheduling.md  # 노트북별 서브페이지
│   │   └── notebooks/                 # 실제 .py 노트북 파일 (14개)
│   └── smart-tv-vibe/                 # AI Vibe Workshop — Smart TV 시나리오
│       ├── README.md                  # 개요 + 모듈/트랙 설명
│       ├── 00-setup.md ~ 07-apps-lakebase.md  # 모듈별 서브페이지
│       └── notebooks/                 # 실제 노트북 파일 (common, track-a/b/c)
├── slides/                            # GitHub Pages 호스팅 (슬라이드/PDF)
│   ├── index.html                     # 슬라이드 목록 페이지
│   ├── aws-workspace-setup.html       # Marp 슬라이드
│   └── *.pdf                          # PDF 자료
└── .github/workflows/pages.yml        # GitHub Pages 자동 배포
```

## 콘텐츠 작성 규칙

### 콘텐츠 품질 기준 (최우선 원칙)
- 모든 문서는 **전문가(Academy) 수준** 으로 작성한다. 표면적 소개나 개요 수준에서 멈추지 않는다.
- 각 기술/개념에 대해 반드시 다음을 포함한다:
  - **왜 등장했는가**(이전 기술의 한계, 해결하려는 문제)
  - **어떻게 작동하는가**(핵심 메커니즘, 아키텍처, 동작 원리)
  - **실전에서 어떻게 활용되는가**(구체적 사용 사례, 구성 예시, 코드)
  - **한계와 트레이드오프**(알려진 제약, 대안, 주의사항)
- 비유, 구체적 예시, 비교 테이블을 적극 활용하여 깊은 이해를 돕는다.
- "입문 → 중급 → 고급" 내용이 한 문서 안에 자연스럽게 연결되도록 구성한다.
- 단순히 "무엇이다"를 나열하지 말고, **"왜"와 "어떻게" ** 에 집중한다.

### GitBook 마크다운
- `{% hint style="info" %}` / `{% hint style="warning" %}` 사용
- IAM Policy, Trust Policy 등 권한 관련 → **반드시 전체 JSON** 형태로 작성 (테이블/불릿 금지)
- ASCII 다이어그램 사용 금지 → 테이블 또는 이미지 사용
- 한 페이지 너무 길면 서브페이지로 분리 (SUMMARY.md 들여쓰기)
- **테이블 전후 설명 필수**: 테이블만 단독으로 나열하지 않는다. 테이블 앞에 해당 테이블이 무엇을 보여주는지 1~2줄 도입 문장을, 테이블 뒤에는 핵심 시사점이나 "왜 이것이 중요한지" 요약 문장을 반드시 포함한다. 표는 데이터를 보여주는 도구이고, 텍스트는 그 데이터의 의미를 전달한다.
- **한국어 볼드 렌더링 규칙 (중요)**: GitBook에서 한국어 볼드가 깨지지 않으려면 `<space>** 볼드텍스트**<space>` 형태여야 함. 즉 여는 `**` 앞과 닫는 `**` 뒤에 반드시 스페이스를 넣을 것. 예: `문장에서 **표준 인터페이스** 입니다` (O), `문장에서** 표준 인터페이스** 입니다` (X). `**` 바로 안쪽에는 스페이스를 넣지 않음: `** 텍스트**` (X), `** 텍스트**` (O)

### 핸즈온 워크샵
- `hands-on/<시나리오명>/` 디렉토리 구조
- README.md (개요) + 모듈별 서브페이지 + notebooks/ (실제 코드)
- 각 서브페이지에 노트북 GitHub 링크 포함
- 노트북 원본은 반드시 `notebooks/` 디렉토리에 포함

### Marp 슬라이드 (별도 프로젝트)
- AWS 구성 가이드 슬라이드: `/Users/simyung.yang/Dev/00-databricks-projects/01-customers/20260327-aws-workspace-setup/`
- 슬라이드에서는 JSON 대신 테이블 형태 사용 (가독성)
- 빌드: `npx @marp-team/marp-cli *.md --html --allow-local-files -o *.html`

### 노트북 소스 위치 (원본)
- MLOps: `/Users/simyung.yang/Dev/00-databricks-projects/01-customers/20260327-lgit-mlops/notebooks/`
- AI Vibe: `/Users/simyung.yang/Dev/00-databricks-projects/01-customers/202604-lge-ms-vibe/notebooks/`
- 변경 시 `02-enablement-blog` 쪽으로도 동기화 필요

### 새 가이드 추가 시
1. 해당 디렉토리에 .md 파일 생성
2. SUMMARY.md에 메뉴 항목 추가
3. README.md 가이드 목록 테이블에 추가
4. `git push` → GitBook 자동 동기화

### Account Console UI 경로 (AWS — 실제 메뉴 기준)
- Credential / Storage: **Cloud resources**→ Credential configuration | Storage configuration
- VPC Endpoints: **Security**→ Networking → VPC endpoints
- Network Configuration: **Security**→ Networking → Classic network configurations
- Private Access Settings: **Security**→ Networking → Private access settings
