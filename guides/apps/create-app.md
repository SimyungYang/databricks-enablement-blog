# 앱 생성하기 (UI 기반)

---

## 사전 준비

- Databricks 워크스페이스 접근 권한
- 앱에서 사용할 리소스(SQL Warehouse 등)에 대한 권한
- 로컬 개발 환경 (Python 또는 Node.js 설치)

---

## Step 1: 앱 생성

1. 워크스페이스 사이드바에서 **+ New** > **App** 클릭
2. 템플릿 선택 (예: `Streamlit`, `Gradio Hello world` 등) 또는 빈 앱 생성
3. 앱 이름 입력 (예: `my-dashboard-app`)
4. **Install** 클릭

앱이 자동으로 워크스페이스에 배포됩니다.

---

## Step 2: 배포 확인

배포 완료 후 **Overview** 페이지에서:

- 앱 URL 확인 (자동 생성)
- 실행 상태 확인
- 로그 확인

---

## Step 3: 소스 코드 다운로드

Overview 페이지의 **Sync the files** 섹션에서 제공하는 커맨드를 복사하여 실행합니다.

```bash
mkdir my-dashboard-app
cd my-dashboard-app
# Overview 페이지에서 제공하는 sync 커맨드 실행
```

다운로드되는 파일:

| 파일 | 역할 |
|------|------|
| `app.py` | 앱 기능 및 UI 구현 |
| `app.yaml` | 앱 설정 (런타임, 환경 변수, 리소스) |
| `requirements.txt` | Python 패키지 의존성 |

---

## Step 4: 로컬 개발 및 테스트

```bash
# 의존성 설치
pip install -r requirements.txt

# 로컬 실행
python app.py

# 또는 Databricks CLI로 로컬 실행 (디버그 모드)
databricks apps run-local --prepare-environment --debug
```

---

## Step 5: 재배포

Overview 페이지의 **Deploy to Databricks Apps** 커맨드를 복사하여 실행합니다.

```bash
# Overview 페이지에서 제공하는 deploy 커맨드 실행
databricks apps deploy <app-name> --source-code-path /path/to/local/app
```
