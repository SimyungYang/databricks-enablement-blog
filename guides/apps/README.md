# Databricks Apps 완벽 가이드

> Databricks 플랫폼 위에서 데이터 & AI 애플리케이션을 직접 호스팅하고 배포하는 Databricks Apps의 실전 가이드

---

## Databricks Apps란?

Databricks Apps는 **Databricks 인프라 위에서 직접 데이터 및 AI 애플리케이션을 개발, 배포, 호스팅**할 수 있는 플랫폼 기능입니다. 별도의 서버나 클라우드 인프라를 구성할 필요 없이, 서버리스 환경에서 앱이 실행됩니다.

### 주요 특징

| 특징 | 설명 |
|------|------|
| **서버리스 호스팅** | 별도 인프라 관리 없이 Databricks가 컨테이너 기반으로 앱을 실행 |
| **Unity Catalog 통합** | 데이터 거버넌스와 접근 제어가 자동으로 적용 |
| **OAuth 기반 인증** | 서비스 프린시펄 및 사용자 인증 모두 지원 |
| **자동 URL 생성** | `https://<app-name>-<workspace-id>.<region>.databricksapps.com` |
| **과금 모델** | 실행 중인 시간 기준, 프로비저닝된 용량에 따라 DBU 과금 |

### 활용 사례

- **인터랙티브 대시보드** — Streamlit/Dash로 실시간 데이터 시각화
- **RAG 챗봇** — Gradio로 검색 증강 생성 AI 챗 인터페이스
- **데이터 입력 폼** — 현업 사용자가 직접 데이터를 입력/수정
- **ML 모델 서빙 UI** — 모델 서빙 엔드포인트를 감싸는 웹 인터페이스
- **REST API** — FastAPI/Flask로 데이터 파이프라인 트리거 또는 조회 API 제공

---

## 핵심 개념

### 아키텍처

Databricks Apps는 **컨테이너화된 서버리스 서비스**로 실행됩니다.

- 전용 컴퓨트 리소스, 네트워크 분리, 저장/전송 암호화 적용
- 서버리스 컴퓨트와 동일한 격리 계층(isolation layer)에서 동작
- 컨트롤 플레인 서비스로서 데이터 플레인 서비스에 접근

### 서비스 프린시펄 (Service Principal)

- 앱 생성 시 **전용 서비스 프린시펄이 자동 생성**됨
- 앱의 영구적인 아이덴티티로 동작
- 다른 앱과 공유하거나 변경할 수 없음
- 앱 삭제 시 함께 삭제됨

### 앱 상태 (Lifecycle)

| 상태 | 설명 |
|------|------|
| `Running` | 정상 실행 중 |
| `Deploying` | 배포 진행 중 |
| `Stopped` | 중지됨 |
| `Crashed` | 오류로 비정상 종료 |

{% hint style="warning" %}
인메모리 상태는 재시작 시 초기화됩니다. 영속적 데이터는 Unity Catalog 테이블, Volume, 또는 Lakebase를 사용하세요.
{% endhint %}

---

## 지원 프레임워크

### Python 프레임워크

| 프레임워크 | 용도 | 기본 실행 커맨드 |
|------------|------|-----------------|
| **Streamlit** | 데이터 대시보드, 데이터 입력 폼 | `streamlit run app.py` |
| **Dash** | 인터랙티브 분석 대시보드 | `python app.py` |
| **Gradio** | AI/ML 모델 데모, 챗봇 UI | `python app.py` |
| **Flask** | 커스텀 웹 앱, REST API | `gunicorn app:app` |
| **FastAPI** | 고성능 REST API | `uvicorn app:app` |

### Node.js 프레임워크

| 프레임워크 | 용도 |
|------------|------|
| **React** | SPA (Single Page Application) |
| **Angular** | 엔터프라이즈 웹 앱 |
| **Svelte** | 경량 웹 앱 |
| **Express** | 서버사이드 API |

> 기본 실행 커맨드: Python 앱은 `python <my-app.py>`, Node.js 앱은 `npm run start`

---

## 제한 사항 및 베스트 프랙티스

### 제한 사항

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

### 보안 베스트 프랙티스

1. **PAT 하드코딩 금지** — 절대로 개인 액세스 토큰을 코드에 직접 넣지 마세요. 자동 주입되는 서비스 프린시펄 인증을 사용하세요.
2. **최소 권한 원칙** — 앱에 필요한 최소한의 권한만 부여하세요.
3. **시크릿은 리소스로 관리** — `valueFrom`을 사용하여 런타임에 안전하게 주입하세요.
4. **앱 간 자격 증명 공유 금지** — 각 앱은 독립적인 서비스 프린시펄을 사용합니다.

### 사용자 인증 보안 베스트 프랙티스

1. 앱 코드를 **소유자/신뢰할 수 있는 사용자만 접근 가능한 폴더**에 저장
2. `CAN MANAGE` 권한은 **신뢰할 수 있는 시니어 개발자**에게만 부여
3. `CAN USE` 권한은 **승인된 사용자/그룹**에게만 부여
4. **토큰을 절대 출력, 로깅, 파일에 기록하지 않기**
5. 최소 필요 스코프만 요청
6. 코드 리뷰 시 스코프와 권한 정합성 검증
7. 프로덕션 배포 전 **피어 리뷰** 필수
8. 사용자 액션에 대한 **구조화된 감사 로그** 기록

### 개발 베스트 프랙티스

1. **로컬 테스트 먼저** — `databricks apps run-local`로 배포 전 검증
2. **리소스 하드코딩 금지** — `valueFrom`을 사용하여 환경 간 이식성 확보
3. **상태는 외부 저장소에** — Unity Catalog, Volume, Lakebase 사용
4. **의존성 버전 명시** — `requirements.txt`에 버전을 명시하여 재현 가능한 빌드
5. **에러 핸들링** — 연결 실패, 권한 오류 등에 대한 적절한 에러 처리
6. **Medium 사이즈로 시작** — 성능 이슈가 확인될 때만 Large로 업그레이드

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
