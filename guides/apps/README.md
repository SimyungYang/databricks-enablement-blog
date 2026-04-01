# Databricks Apps 완벽 가이드

> Databricks 플랫폼 위에서 데이터 & AI 애플리케이션을 직접 호스팅하고 배포하는 Databricks Apps의 실전 가이드

---

## Databricks Apps란?

Databricks Apps는 **Databricks 인프라 위에서 직접 데이터 및 AI 애플리케이션을 개발, 배포, 호스팅** 할 수 있는 플랫폼 기능입니다. 별도의 서버나 클라우드 인프라를 구성할 필요 없이, 서버리스 환경에서 앱이 실행됩니다.

기존에 Databricks 데이터를 외부 앱에서 사용하려면 별도의 웹 서버를 프로비저닝하고, 인증을 설정하고, 네트워크를 구성해야 했습니다. Databricks Apps는 이 모든 인프라 복잡성을 제거하고, **코드만 작성하면 즉시 배포** 할 수 있는 환경을 제공합니다.

### 주요 특징

| 특징 | 설명 |
|------|------|
| **서버리스 호스팅**| 별도 인프라 관리 없이 Databricks가 컨테이너 기반으로 앱을 실행 |
| **Unity Catalog 통합**| 데이터 거버넌스와 접근 제어가 자동으로 적용 |
| **OAuth 기반 인증**| 서비스 프린시펄 및 사용자 인증 모두 지원 |
| **자동 URL 생성**| `https://<app-name>-<workspace-id>.<region>.databricksapps.com` |
| **과금 모델**| 실행 중인 시간 기준, 프로비저닝된 용량에 따라 DBU 과금 |
| **Databricks CLI 지원**| 로컬 개발, 테스트, 배포까지 CLI로 완전 자동화 가능 |

---

## 아키텍처: 컨테이너 기반 서버리스 실행

Databricks Apps는 **컨테이너화된 서버리스 서비스** 로 실행됩니다.

| 계층 | 구성 요소 | 설명 |
|------|----------|------|
| **Databricks Control Plane**| 전체 실행 환경 | 컨트롤 플레인 내에서 앱 컨테이너 실행 |
| **App Container**| App Code (app.py) | 사용자가 작성한 애플리케이션 코드 |
| | Runtime (Python / Node.js) | 앱 실행 런타임 환경 |
| | Service Principal (자동 생성) | 앱 전용 서비스 프린시펄 — UC, Warehouse 접근에 사용 |
| **플랫폼 서비스**| SQL Warehouse | 데이터 조회 및 분석 |
| | Model Serving | AI/ML 모델 엔드포인트 |
| | Unity Catalog | 데이터 거버넌스 및 접근 제어 |

**핵심 아키텍처 특성:**
- 전용 컴퓨트 리소스, 네트워크 분리, 저장/전송 암호화 적용
- 서버리스 컴퓨트와 동일한 격리 계층(isolation layer)에서 동작
- 컨트롤 플레인 서비스로서 데이터 플레인 서비스에 접근
- 앱 간 완전한 네트워크 격리 보장

---

## 서비스 프린시펄 자동 생성 동작 방식

앱 생성 시 Databricks가 **전용 서비스 프린시펄(SP)** 을 자동으로 생성합니다. 이 SP가 앱의 영구적인 아이덴티티로 동작합니다.

| 특성 | 설명 |
|------|------|
| **자동 생성**| 앱 생성 시 1:1로 매핑되는 SP가 자동 생성됨 |
| **전용**| 다른 앱과 공유하거나 변경할 수 없음 |
| **권한 관리**| 이 SP에 UC 테이블, SQL Warehouse 등의 접근 권한을 부여 |
| **라이프사이클**| 앱 삭제 시 SP도 함께 삭제됨 |

{% hint style="warning" %}
**중요**: 앱의 서비스 프린시펄에 필요한 권한을 반드시 부여해야 합니다. 예를 들어 앱에서 UC 테이블을 조회하려면 해당 SP에 `SELECT` 권한을, SQL Warehouse를 사용하려면 `CAN USE` 권한을 부여해야 합니다.
{% endhint %}

---

## 앱 상태 라이프사이클

앱은 다음 상태를 거칩니다.

**상태 전이 흐름:**
- **생성**→ `Deploying` → `Running` (정상 실행)
- `Running` ↔ `Stopped` (수동 중지/재시작)
- `Running` → `Crashed` (오류 발생) → 코드 수정 후 재배포 → `Deploying` → `Running`

| 상태 | 설명 | 과금 여부 |
|------|------|-----------|
| `Deploying` | 배포 진행 중 (컨테이너 빌드, 의존성 설치) | 과금 |
| `Running` | 정상 실행 중, URL로 접속 가능 | 과금 |
| `Stopped` | 사용자가 수동으로 중지, URL 접속 불가 | **비과금**|
| `Crashed` | 오류로 비정상 종료 (코드 에러, OOM 등) | 비과금 |

{% hint style="warning" %}
인메모리 상태는 재시작 시 초기화됩니다. 영속적 데이터는 Unity Catalog 테이블, Volume, 또는 Lakebase를 사용하세요.
{% endhint %}

{% hint style="info" %}
**비용 절감 팁**: 사용하지 않는 앱은 `Stopped` 상태로 전환하세요. `Running` 상태에서는 트래픽이 없더라도 DBU가 과금됩니다.
{% endhint %}

---

## 지원 프레임워크별 장단점 비교

### Python 프레임워크

| 프레임워크 | 장점 | 단점 | 추천 용도 |
|------------|------|------|-----------|
| **Streamlit**| 가장 빠른 프로토타이핑, 풍부한 위젯 | 복잡한 레이아웃 제한, 세션 상태 관리 | 데이터 대시보드, 데이터 입력 폼 |
| **Dash**| Plotly 차트 통합, 콜백 기반 인터랙션 | 학습 곡선 높음 | 인터랙티브 분석 대시보드 |
| **Gradio**| AI/ML 데모에 최적화, 챗봇 UI 내장 | 범용 웹앱으로는 제한적 | AI/ML 모델 데모, 챗봇 UI |
| **Flask**| 유연한 라우팅, 방대한 생태계 | 프론트엔드 직접 구현 필요 | 커스텀 웹 앱, REST API |
| **FastAPI**| 고성능 비동기, 자동 API 문서 생성 | 프론트엔드 직접 구현 필요 | 고성능 REST API |

### Node.js 프레임워크

| 프레임워크 | 장점 | 단점 | 추천 용도 |
|------------|------|------|-----------|
| **React**| 거대한 생태계, 컴포넌트 재사용 | 초기 설정 복잡 | SPA (Single Page Application) |
| **Angular**| 엔터프라이즈 기능 내장 | 학습 곡선 가장 높음 | 엔터프라이즈 웹 앱 |
| **Svelte**| 가장 경량, 빠른 빌드 | 생태계 상대적으로 작음 | 경량 웹 앱 |
| **Express**| 미니멀, 유연함 | 프론트엔드 직접 구현 필요 | 서버사이드 API |

> 기본 실행 커맨드: Python 앱은 `python <my-app.py>`, Node.js 앱은 `npm run start`

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

## 제한 사항

| 항목 | 제한 |
|------|------|
| **파일 크기**| 개별 파일 최대 10 MB (초과 시 배포 실패) |
| **워크스페이스당 앱 수**| 워크스페이스 쿼터에 따름 |
| **컴퓨트 사이즈**| Medium (2 vCPU/6 GB) 또는 Large (4 vCPU/12 GB)만 선택 가능 |
| **앱 URL**| 생성 후 변경 불가 |
| **인메모리 상태**| 재시작 시 초기화됨 |
| **셸 기능**| `command`에서 파이프, 리다이렉트 등 셸 기능 사용 불가 |
| **Free Edition**| 추가 제한 사항 적용 |
| **사용자 인증**| Public Preview 상태 |

---

## 보안 베스트 프랙티스

1. **PAT 하드코딩 금지**— 절대로 개인 액세스 토큰을 코드에 직접 넣지 마세요. 자동 주입되는 서비스 프린시펄 인증을 사용하세요.
2. **최소 권한 원칙**— 앱에 필요한 최소한의 권한만 부여하세요.
3. **시크릿은 리소스로 관리**— `valueFrom`을 사용하여 런타임에 안전하게 주입하세요.
4. **앱 간 자격 증명 공유 금지**— 각 앱은 독립적인 서비스 프린시펄을 사용합니다.
5. **코드 리뷰 시 스코프와 권한 정합성 검증**
6. **프로덕션 배포 전 피어 리뷰 필수**
7. **사용자 액션에 대한 구조화된 감사 로그 기록**

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
