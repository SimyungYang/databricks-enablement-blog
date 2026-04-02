# Databricks Apps 완벽 가이드

> Databricks 플랫폼 위에서 데이터 & AI 애플리케이션을 직접 호스팅하고 배포하는 Databricks Apps의 실전 가이드

---

## Databricks Apps란?

Databricks Apps는 **Databricks 인프라 위에서 직접 데이터 및 AI 애플리케이션을 개발, 배포, 호스팅** 할 수 있는 플랫폼 기능입니다. 별도의 서버나 클라우드 인프라를 구성할 필요 없이, 서버리스 환경에서 앱이 실행됩니다.

기존에 Databricks 데이터를 외부 앱에서 사용하려면 별도의 웹 서버를 프로비저닝하고, 인증을 설정하고, 네트워크를 구성해야 했습니다. Databricks Apps는 이 모든 인프라 복잡성을 제거하고, **코드만 작성하면 즉시 배포** 할 수 있는 환경을 제공합니다.

---

## 왜 Databricks Apps인가? 기존 배포 방식과의 비교

데이터 팀이 웹 앱을 만들어야 할 때, 전통적으로는 클라우드 인프라를 직접 구성해야 했습니다. **EC2 인스턴스를 프로비저닝하고, 보안 그룹을 설정하고, SSL 인증서를 발급받고, 로드 밸런서를 구성하고, Databricks API 인증 토큰을 관리** 하는 등의 작업이 필요했습니다. 이 과정에서 데이터 엔지니어가 인프라 엔지니어의 역할까지 맡게 되는 상황이 빈번하게 발생합니다.

Databricks Apps는 이러한 인프라 복잡성을 완전히 제거합니다. 아래 표는 기존 배포 방식과 Databricks Apps의 차이를 비교합니다.

| 비교 항목 | EC2 / VM 직접 배포 | ECS / Fargate / Cloud Run | Heroku / PaaS | **Databricks Apps** |
|-----------|-------------------|--------------------------|---------------|---------------------|
| **인프라 설정** | VPC, 보안그룹, ALB 등 직접 구성 | 컨테이너 정의, 태스크 정의 필요 | 최소 설정 | **설정 불필요** |
| **Databricks 인증** | PAT/OAuth 토큰 직접 관리 | IAM Role + Secret Manager | 환경변수로 PAT 관리 | **서비스 프린시펄 자동 생성** |
| **Unity Catalog 접근** | API 토큰 + SDK 설정 필요 | API 토큰 + SDK 설정 필요 | API 토큰 + SDK 설정 필요 | **자동 통합, 거버넌스 자동 적용** |
| **SSL/HTTPS** | ACM + ALB 또는 Certbot 구성 | ALB 또는 Cloud CDN 구성 | 자동 | **자동** |
| **사용자 인증** | Cognito/Auth0 등 별도 구축 | 별도 구축 필요 | 별도 구축 필요 | **워크스페이스 SSO 자동 적용** |
| **네트워크 보안** | Security Group, NACLs 직접 설정 | VPC 설정 필요 | 제한적 | **컨트롤 플레인 내 자동 격리** |
| **배포 소요 시간** | 초기 설정 수 시간~수 일 | 초기 설정 1~2시간 | 수 분 | **2~5분** |
| **비용 모델** | 인스턴스 상시 과금 | 컨테이너 실행 시간 과금 | Dyno 과금 | **DBU 기반, 중지 시 비과금** |

{% hint style="info" %}
**핵심 차별점**: Databricks Apps의 가장 큰 장점은 인프라가 아니라 **Databricks 생태계와의 네이티브 통합** 입니다. Unity Catalog 거버넌스가 자동으로 적용되고, 서비스 프린시펄이 자동 생성되며, SQL Warehouse와 Model Serving에 별도 인증 없이 접근할 수 있습니다. 일반적인 PaaS가 "서버 관리 불필요"를 제공한다면, Databricks Apps는 "데이터 플랫폼 인증과 거버넌스 관리 불필요"를 제공합니다.
{% endhint %}

---

### 주요 특징

아래 표는 Databricks Apps의 핵심 기능을 정리합니다. 각 특징이 실무에서 어떤 의미를 갖는지 함께 설명합니다.

| 특징 | 설명 |
|------|------|
| **서버리스 호스팅** | 별도 인프라 관리 없이 Databricks가 컨테이너 기반으로 앱을 실행 |
| **Unity Catalog 통합** | 데이터 거버넌스와 접근 제어가 자동으로 적용 |
| **OAuth 기반 인증** | 서비스 프린시펄 및 사용자 인증 모두 지원 |
| **자동 URL 생성** | `https://<app-name>-<workspace-id>.<region>.databricksapps.com` |
| **과금 모델** | 실행 중인 시간 기준, 프로비저닝된 용량에 따라 DBU 과금 |
| **Databricks CLI 지원** | 로컬 개발, 테스트, 배포까지 CLI로 완전 자동화 가능 |

이 특징들의 조합이 의미하는 바는 명확합니다. **데이터 엔지니어나 데이터 사이언티스트가 인프라 전문 지식 없이도 프로덕션 수준의 웹 앱을 배포** 할 수 있다는 것입니다. 기존에는 "앱을 만들고 싶다"는 요구에 "DevOps 팀에 티켓을 올려야 한다"로 답해야 했지만, 이제는 코드만 작성하면 됩니다.

---

## 아키텍처: 컨테이너 기반 서버리스 실행

Databricks Apps는 **컨테이너화된 서버리스 서비스** 로 실행됩니다. 이 아키텍처를 이해하면 앱의 동작 방식, 제약 사항, 성능 특성을 예측할 수 있습니다.

| 계층 | 구성 요소 | 설명 |
|------|----------|------|
| **Databricks Control Plane** | 전체 실행 환경 | 컨트롤 플레인 내에서 앱 컨테이너 실행 |
| **App Container** | App Code (app.py) | 사용자가 작성한 애플리케이션 코드 |
| | Runtime (Python / Node.js) | 앱 실행 런타임 환경 |
| | Service Principal (자동 생성) | 앱 전용 서비스 프린시펄 — UC, Warehouse 접근에 사용 |
| **플랫폼 서비스** | SQL Warehouse | 데이터 조회 및 분석 |
| | Model Serving | AI/ML 모델 엔드포인트 |
| | Unity Catalog | 데이터 거버넌스 및 접근 제어 |

**핵심 아키텍처 특성:**
- 전용 컴퓨트 리소스, 네트워크 분리, 저장/전송 암호화 적용
- 서버리스 컴퓨트와 동일한 격리 계층(isolation layer)에서 동작
- 컨트롤 플레인 서비스로서 데이터 플레인 서비스에 접근
- 앱 간 완전한 네트워크 격리 보장

{% hint style="info" %}
**아키텍처가 의미하는 것**: 앱이 **컨트롤 플레인 내부** 에서 실행된다는 것은 중요한 의미를 갖습니다. 첫째, 데이터 플레인(고객 VPC)에 있는 리소스에 접근할 때 Databricks의 내부 네트워크를 통하므로 퍼블릭 인터넷을 거치지 않습니다. 둘째, 각 앱은 독립된 Kubernetes 네임스페이스에서 실행되어 다른 앱의 트래픽이나 장애에 영향을 받지 않습니다. 셋째, 서버리스 컴퓨트와 동일한 보안 격리 수준이 적용되므로 엔터프라이즈 보안 요구사항을 충족합니다.
{% endhint %}

---

## 서비스 프린시펄 자동 생성 동작 방식

앱 생성 시 Databricks가 **전용 서비스 프린시펄(SP)** 을 자동으로 생성합니다. 이 SP가 앱의 영구적인 아이덴티티로 동작합니다.

이 자동 생성 메커니즘이 왜 중요한지 이해하려면, 기존 방식을 먼저 떠올려 보세요. 일반적으로 외부 앱에서 Databricks에 접근하려면 **개인 액세스 토큰(PAT)** 을 생성하고, 이를 환경변수나 Secret Manager에 저장하고, 주기적으로 로테이션해야 합니다. PAT는 특정 사용자에게 귀속되므로 그 사용자가 퇴사하면 토큰이 무효화됩니다. 서비스 프린시펄은 이러한 문제를 근본적으로 해결합니다.

| 특성 | 설명 |
|------|------|
| **자동 생성** | 앱 생성 시 1:1로 매핑되는 SP가 자동 생성됨 |
| **전용** | 다른 앱과 공유하거나 변경할 수 없음 |
| **권한 관리** | 이 SP에 UC 테이블, SQL Warehouse 등의 접근 권한을 부여 |
| **라이프사이클** | 앱 삭제 시 SP도 함께 삭제됨 |

이 표에서 **전용** 이라는 특성이 특히 중요합니다. 각 앱이 독립된 SP를 가지므로, 한 앱의 권한 변경이 다른 앱에 영향을 주지 않습니다. 또한 앱 삭제 시 SP가 함께 삭제되므로 "더 이상 사용하지 않는데 권한만 남아있는" 고아 서비스 계정 문제가 발생하지 않습니다.

{% hint style="warning" %}
**중요**: 앱의 서비스 프린시펄에 필요한 권한을 반드시 부여해야 합니다. 예를 들어 앱에서 UC 테이블을 조회하려면 해당 SP에 `SELECT` 권한을, SQL Warehouse를 사용하려면 `CAN USE` 권한을 부여해야 합니다.
{% endhint %}

{% hint style="info" %}
**SP 권한 부여 방법**: 앱 생성 후 Overview 페이지에서 SP 이름을 확인할 수 있습니다. 이 SP에 Unity Catalog 권한을 부여하는 SQL은 다음과 같습니다: `GRANT SELECT ON TABLE catalog.schema.table TO <sp-application-id>`. SQL Warehouse 접근 권한은 Warehouse 설정 UI에서 해당 SP를 추가하면 됩니다.
{% endhint %}

---

## 앱 상태 라이프사이클

앱은 다음 상태를 거칩니다. 각 상태의 의미와 전이 조건을 정확히 이해하면, 운영 중 발생하는 상황에 빠르게 대응할 수 있습니다.

**상태 전이 흐름:**
- **생성**→ `Deploying` → `Running` (정상 실행)
- `Running` ↔ `Stopped` (수동 중지/재시작)
- `Running` → `Crashed` (오류 발생) → 코드 수정 후 재배포 → `Deploying` → `Running`

| 상태 | 설명 | 과금 여부 |
|------|------|-----------|
| `Deploying` | 배포 진행 중 (컨테이너 빌드, 의존성 설치) | 과금 |
| `Running` | 정상 실행 중, URL로 접속 가능 | 과금 |
| `Stopped` | 사용자가 수동으로 중지, URL 접속 불가 | **비과금** |
| `Crashed` | 오류로 비정상 종료 (코드 에러, OOM 등) | 비과금 |

각 상태에서 알아야 할 핵심 사항이 있습니다. **Deploying** 상태에서도 과금이 발생한다는 점에 주의하세요. 의존성 설치에 시간이 오래 걸리면(예: 대용량 ML 라이브러리) 배포 비용이 증가합니다. **Running** 상태에서는 실제 트래픽이 없더라도 과금됩니다. 이는 컨테이너가 항상 대기 상태로 유지되기 때문입니다. **Crashed** 상태에서는 자동 복구가 되지 않으므로, 로그를 확인하고 코드를 수정한 뒤 재배포해야 합니다.

{% hint style="warning" %}
인메모리 상태는 재시작 시 초기화됩니다. 영속적 데이터는 Unity Catalog 테이블, Volume, 또는 Lakebase를 사용하세요.
{% endhint %}

{% hint style="info" %}
**비용 절감 팁**: 사용하지 않는 앱은 `Stopped` 상태로 전환하세요. `Running` 상태에서는 트래픽이 없더라도 DBU가 과금됩니다. 개발/테스트 앱은 업무 시간 외에 자동으로 중지하는 스크립트를 구성하면 비용을 크게 절감할 수 있습니다.
{% endhint %}

---

## 언제 Databricks Apps를 쓰고, 언제 안 쓰는가

모든 도구에는 적합한 사용 사례가 있습니다. Databricks Apps가 빛을 발하는 상황과 다른 솔루션이 더 나은 상황을 구분하는 것이 중요합니다.

### 적합한 사용 사례

| 사용 사례 | 왜 적합한가 |
|-----------|-----------|
| **AI Agent UI** | Model Serving과 직접 통합, 인증 자동 처리. Gradio 챗봇 UI를 수 분 내에 배포 가능 |
| **내부 데이터 대시보드** | Unity Catalog 거버넌스가 자동 적용되어 사용자별 데이터 접근 제어가 가능 |
| **데이터 입력/편집 폼** | 현업 사용자가 UC 테이블에 직접 데이터를 입력. 별도 백엔드 구축 불필요 |
| **ML 모델 데모** | Serving Endpoint를 감싸는 UI를 빠르게 구축하여 stakeholder에게 시연 |
| **내부 도구/관리 페이지** | 워크스페이스 SSO로 인증이 자동 처리되어 별도 로그인 시스템 불필요 |

### 부적합한 사용 사례

| 사용 사례 | 왜 부적합한가 | 대안 |
|-----------|-------------|------|
| **고트래픽 외부 서비스** | 스케일링에 제한이 있고, 항상 워크스페이스 인증이 필요 | ECS/Fargate, Cloud Run |
| **퍼블릭 웹사이트** | 모든 접근자에게 Databricks 워크스페이스 계정이 필요 | Vercel, Netlify, S3 호스팅 |
| **실시간 양방향 통신** | WebSocket 지원이 제한적 | EC2 + WebSocket 서버 |
| **대용량 파일 서빙** | 개별 파일 10MB 제한 | S3/Blob Storage + CloudFront |
| **복잡한 마이크로서비스** | 단일 컨테이너 아키텍처, 서비스 간 통신 제한 | EKS/AKS + Service Mesh |

{% hint style="warning" %}
**판단 기준**: "이 앱의 사용자가 Databricks 워크스페이스에 접근할 수 있는가?"가 첫 번째 판단 기준입니다. 외부 고객이나 Databricks 계정이 없는 사용자가 접근해야 한다면, Databricks Apps는 적합하지 않습니다.
{% endhint %}

---

## 지원 프레임워크별 장단점 비교

프레임워크 선택은 앱의 목적에 따라 달라집니다. 아래 표는 각 프레임워크의 특성을 정리하여 선택 기준을 제공합니다.

### Python 프레임워크

| 프레임워크 | 장점 | 단점 | 추천 용도 |
|------------|------|------|-----------|
| **Streamlit** | 가장 빠른 프로토타이핑, 풍부한 위젯 | 복잡한 레이아웃 제한, 세션 상태 관리 | 데이터 대시보드, 데이터 입력 폼 |
| **Dash** | Plotly 차트 통합, 콜백 기반 인터랙션 | 학습 곡선 높음 | 인터랙티브 분석 대시보드 |
| **Gradio** | AI/ML 데모에 최적화, 챗봇 UI 내장 | 범용 웹앱으로는 제한적 | AI/ML 모델 데모, 챗봇 UI |
| **Flask** | 유연한 라우팅, 방대한 생태계 | 프론트엔드 직접 구현 필요 | 커스텀 웹 앱, REST API |
| **FastAPI** | 고성능 비동기, 자동 API 문서 생성 | 프론트엔드 직접 구현 필요 | 고성능 REST API |

### Node.js 프레임워크

| 프레임워크 | 장점 | 단점 | 추천 용도 |
|------------|------|------|-----------|
| **React** | 거대한 생태계, 컴포넌트 재사용 | 초기 설정 복잡 | SPA (Single Page Application) |
| **Angular** | 엔터프라이즈 기능 내장 | 학습 곡선 가장 높음 | 엔터프라이즈 웹 앱 |
| **Svelte** | 가장 경량, 빠른 빌드 | 생태계 상대적으로 작음 | 경량 웹 앱 |
| **Express** | 미니멀, 유연함 | 프론트엔드 직접 구현 필요 | 서버사이드 API |

> 기본 실행 커맨드: Python 앱은 `python <my-app.py>`, Node.js 앱은 `npm run start`

{% hint style="info" %}
**프레임워크 선택 가이드**: 처음 시작한다면 **Streamlit** 을 추천합니다. 가장 적은 코드로 가장 빠르게 결과물을 만들 수 있습니다. AI/ML 모델 데모가 목적이라면 **Gradio** 의 챗봇 UI가 최적입니다. 외부 시스템과 API 연동이 필요하다면 **FastAPI** 의 자동 문서 생성(Swagger UI)이 큰 도움이 됩니다.
{% endhint %}

---

## 활용 사례 5가지

### 1. 인터랙티브 대시보드
Streamlit/Dash로 실시간 데이터 시각화. SQL Warehouse에서 데이터를 조회하여 차트와 필터를 제공합니다.

### 2. RAG 챗봇 UI
Gradio로 검색 증강 생성 AI 챗 인터페이스를 구축합니다. Model Serving 엔드포인트를 호출하여 대화형 AI를 제공합니다.

### 3. 데이터 입력 폼
현업 사용자가 직접 데이터를 입력/수정할 수 있는 폼을 제공합니다. 입력된 데이터는 Unity Catalog 테이블에 저장됩니다.

### 4. ML 모델 서빙 UI
Model Serving 엔드포인트를 감싸는 웹 인터페이스를 제공합니다. 사용자가 입력값을 넣으면 예측 결과를 시각화합니다.

### 5. REST API 게이트웨이
FastAPI/Flask로 데이터 파이프라인 트리거 또는 조회 API를 제공합니다. 외부 시스템과의 통합 지점으로 활용합니다.

---

## 비용 구조와 최적화

Databricks Apps의 비용은 **DBU(Databricks Unit)** 기반으로 과금됩니다. 비용을 정확히 이해하고 최적화하는 것은 프로덕션 운영에서 필수적입니다.

| 컴퓨트 사이즈 | DBU/시간 | 월간 예상 비용 (24/7 실행 기준) | 비고 |
|--------------|----------|-------------------------------|------|
| **Medium**(2 vCPU, 6GB) | 0.5 DBU/hr | ~360 DBU/월 | 대부분의 앱에 충분 |
| **Large**(4 vCPU, 12GB) | 1.0 DBU/hr | ~720 DBU/월 | 고부하 앱에만 사용 |

{% hint style="info" %}
**비용 최적화 전략**:
1. **개발/테스트 앱은 사용하지 않을 때 반드시 중지** 하세요. `Running` 상태에서는 트래픽이 없어도 과금됩니다.
2. **Medium 사이즈로 시작** 하세요. 성능 문제가 실제로 발생한 후에 Large로 업그레이드해도 늦지 않습니다.
3. **CI/CD로 자동 중지/시작 스케줄** 을 구성하세요. 예: 퇴근 시간에 자동 중지, 출근 시간에 자동 시작.
4. **SQL Warehouse는 Serverless를 사용** 하세요. Classic Warehouse는 항상 켜져 있어야 하지만, Serverless는 쿼리가 없으면 자동 중지됩니다.
{% endhint %}

---

## 제한 사항

아래 표는 Databricks Apps의 기술적 제한 사항을 정리합니다. 앱을 설계하기 전에 반드시 확인하여 나중에 아키텍처를 변경해야 하는 상황을 방지하세요.

| 항목 | 제한 |
|------|------|
| **파일 크기** | 개별 파일 최대 10 MB (초과 시 배포 실패) |
| **워크스페이스당 앱 수** | 워크스페이스 쿼터에 따름 |
| **컴퓨트 사이즈** | Medium (2 vCPU/6 GB) 또는 Large (4 vCPU/12 GB)만 선택 가능 |
| **앱 URL** | 생성 후 변경 불가 |
| **인메모리 상태** | 재시작 시 초기화됨 |
| **셸 기능** | `command`에서 파이프, 리다이렉트 등 셸 기능 사용 불가 |
| **Free Edition** | 추가 제한 사항 적용 |
| **사용자 인증** | Public Preview 상태 |

{% hint style="warning" %}
**실무에서 가장 자주 겪는 제한**: 파일 크기 10MB 제한은 ML 모델 가중치 파일이나 대용량 데이터셋을 앱에 포함시킬 수 없음을 의미합니다. 이런 파일은 **Unity Catalog Volume** 에 업로드하고, 앱 시작 시 런타임에 다운로드하는 패턴을 사용하세요. 인메모리 상태 초기화는 세션 데이터, 캐시 등을 앱 프로세스 메모리에 저장하면 안 된다는 의미입니다. Lakebase(PostgreSQL 호환)나 UC 테이블을 영속 저장소로 사용하세요.
{% endhint %}

---

## 보안 베스트 프랙티스

보안은 앱 개발의 모든 단계에서 고려해야 합니다. 아래 원칙들은 단순한 권장사항이 아니라, Databricks 환경에서 반드시 준수해야 할 필수 사항입니다.

1. **PAT 하드코딩 금지**— 절대로 개인 액세스 토큰을 코드에 직접 넣지 마세요. 자동 주입되는 서비스 프린시펄 인증을 사용하세요.
2. **최소 권한 원칙**— 앱에 필요한 최소한의 권한만 부여하세요.
3. **시크릿은 리소스로 관리**— `valueFrom`을 사용하여 런타임에 안전하게 주입하세요.
4. **앱 간 자격 증명 공유 금지**— 각 앱은 독립적인 서비스 프린시펄을 사용합니다.
5. **코드 리뷰 시 스코프와 권한 정합성 검증**
6. **프로덕션 배포 전 피어 리뷰 필수**
7. **사용자 액션에 대한 구조화된 감사 로그 기록**

{% hint style="warning" %}
**가장 흔한 보안 실수**: PAT를 `app.yaml`의 `value` 필드에 직접 넣는 것입니다. 이 파일은 Git 리포지토리에 커밋되므로 토큰이 노출됩니다. 반드시 **Secret** 리소스와 `valueFrom`을 사용하세요.
{% endhint %}

---

## 개발 베스트 프랙티스

1. **로컬 테스트 먼저**— `databricks apps run-local`로 배포 전 검증
2. **리소스 하드코딩 금지**— `valueFrom`을 사용하여 환경 간 이식성 확보
3. **상태는 외부 저장소에**— Unity Catalog, Volume, Lakebase 사용
4. **의존성 버전 명시**— `requirements.txt`에 버전을 명시하여 재현 가능한 빌드
5. **에러 핸들링**— 연결 실패, 권한 오류 등에 대한 적절한 에러 처리
6. **Medium 사이즈로 시작**— 성능 이슈가 확인될 때만 Large로 업그레이드

---

## 참고 자료

- [Databricks Apps 공식 문서](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)
- [앱 개발 가이드](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development)
- [인증 설정](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/auth)
- [리소스 설정](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/resources)
- [Streamlit 튜토리얼](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/tutorial-streamlit)
- [앱 런타임 설정 (app.yaml)](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-runtime)
- [컴퓨트 사이즈](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/compute-size)
- [환경 변수](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/environment-variables)
