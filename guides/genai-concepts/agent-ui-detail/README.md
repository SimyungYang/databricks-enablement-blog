# AI Agent UI & 배포 기술 스택

AI Agent를 사용자에게 전달하려면 "무엇을 만들 것인가"만큼이나 "어떻게 보여줄 것인가"가 중요합니다. 이 가이드는 Agent 프로젝트에서 사용되는 UI/UX 프레임워크와 배포 기술을 비교하고, 프로젝트 단계별 최적의 기술 스택을 선택하는 기준을 제공합니다.

{% hint style="info" %}
**학습 목표**
- Agent 프로젝트에서 UI/UX 기술 선택 기준을 이해한다
- Streamlit, Gradio, Chainlit, Dash, FastAPI의 특성과 적합한 사용 사례를 구분할 수 있다
- Databricks Apps를 활용한 프로덕션 배포 아키텍처를 설계할 수 있다
- PoC → 파일럿 → 프로덕션 단계별 적합한 기술 스택을 선택할 수 있다
{% endhint %}

---

## 서브 페이지 구성

| 페이지 | 설명 |
|--------|------|
| [Streamlit & Gradio](streamlit-gradio.md) | Python 기반 빠른 프로토타이핑 도구. 채팅 UI 구현, 스트리밍, 비교 |
| [Chainlit & Dash](chainlit-dash.md) | Agent 추론 시각화 전용 UI(Chainlit), 데이터 대시보드 특화(Dash) |
| [FastAPI 백엔드](fastapi-backend.md) | REST API, SSE 스트리밍, WebSocket 양방향 통신, Frontend 분리 아키텍처 |
| [Databricks Apps & 종합 가이드](databricks-apps.md) | Databricks Apps 배포, 단계별 기술 스택 선택, 종합 비교, 고객 FAQ, 연습문제 |

---

## 왜 Agent에 UI가 필요한가?

AI Agent는 API만으로도 동작합니다. `curl`로 엔드포인트를 호출하면 응답이 돌아오고, 노트북에서 함수를 실행하면 결과를 확인할 수 있습니다. 그런데 왜 UI를 만들어야 할까요?

### 채택(Adoption)의 벽

Agent의 기술적 완성도와 실제 사용률은 별개입니다. 아무리 정교한 RAG 파이프라인과 Tool Calling 로직을 구현해도, 사용자가 접근할 수 없으면 의미가 없습니다.

| 사용자 유형 | 선호 인터페이스 | 이유 |
|------------|---------------|------|
| **개발자**| API / CLI / SDK | 자동화 파이프라인에 Agent를 통합해야 하므로 프로그래밍 인터페이스가 자연스러움 |
| **데이터 분석가**| 노트북 (Databricks, Jupyter) | 이미 노트북 환경에서 작업하므로, Agent를 함수 호출로 사용 가능 |
| **현업 사용자**| 웹 앱 (채팅, 대시보드) | CLI나 노트북을 사용할 수 없으므로 브라우저 기반 인터페이스가 유일한 접점 |
| **경영진**| 데모 화면 (웹 앱) | 투자 의사결정을 위해 "동작하는 화면"을 봐야 확신 |

{% hint style="warning" %}
**PoC의 성패를 UI가 좌우한다**: 기술적으로 완벽한 Agent라도, 경영진 데모에서 터미널에 JSON을 보여주면 프로젝트 승인이 어렵습니다. 반대로, 간단한 채팅 UI 하나만 있어도 "이걸 우리 팀도 쓸 수 있겠는데?"라는 반응을 이끌어낼 수 있습니다. UI는 기술이 아니라 커뮤니케이션 도구입니다.
{% endhint %}

### UI의 세 가지 역할

1. **접근성 확보**: 비기술 사용자가 Agent를 사용할 수 있는 유일한 경로
2. **신뢰 구축**: Agent의 추론 과정, Tool 호출 결과, 출처를 투명하게 보여줌으로써 사용자 신뢰 확보
3. **피드백 수집**: 사용자가 "좋아요/싫어요", 수정 요청 등의 피드백을 남길 수 있는 인터페이스 제공

---

다음 페이지: [Streamlit & Gradio](streamlit-gradio.md)
