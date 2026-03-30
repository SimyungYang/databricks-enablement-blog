# 배포 워크플로우

---

## 전체 흐름

```
[로컬 개발] → [로컬 테스트] → [워크스페이스 배포] → [설정/리소스 연결] → [운영]
```

---

## 1. 로컬 개발

선호하는 IDE(VS Code, PyCharm, IntelliJ 등)에서 개발합니다. Databricks VS Code Extension 사용을 권장합니다.

```bash
# 프로젝트 구조
my-app/
├── app.py              # 앱 코드
├── app.yaml            # 앱 설정
├── requirements.txt    # Python 의존성
└── static/             # 정적 파일 (선택)
```

---

## 2. 로컬 테스트

```bash
# Databricks CLI 로컬 실행
databricks apps run-local --prepare-environment --debug
```

또는 프레임워크별로 직접 실행:

```bash
# Streamlit
streamlit run app.py

# Flask
gunicorn app:app -w 4

# FastAPI
uvicorn app:app --reload

# Gradio
python app.py
```

---

## 3. 워크스페이스 배포

```bash
# Databricks CLI를 통한 배포
databricks apps deploy <app-name> --source-code-path /path/to/local/app
```

---

## 4. 환경 간 이동

리소스를 하드코딩하지 않고 `app.yaml`의 `valueFrom`을 사용하면, 코드 수정 없이 다른 워크스페이스로 앱을 이동할 수 있습니다.

---

## 의존성 관리

| 언어 | 파일 |
|------|------|
| Python (pip) | `requirements.txt` |
| Python (uv) | `pyproject.toml` |
| Node.js | `package.json` |

{% hint style="warning" %}
**파일 크기 제한**: 앱 파일은 개별 10 MB를 초과할 수 없습니다. 초과 시 배포가 실패합니다.
{% endhint %}
