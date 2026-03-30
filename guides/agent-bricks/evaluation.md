# 평가 & 배포

---

## MLflow 기반 평가

Agent Bricks는 MLflow와 긴밀하게 통합되어 에이전트 품질을 체계적으로 평가합니다.

| 기능 | 설명 |
|------|------|
| **Tracing** | 에이전트 실행의 전체 과정을 추적 (Production Monitoring for MLflow 활성화 필요) |
| **AI Judge** | LLM 기반 자동 품질 판정 |
| **Synthetic Task Generation** | 합성 데이터로 대규모 테스트 |
| **라벨링된 데이터셋** | UC 테이블로 Import/Export하여 체계적 관리 |

---

## 평가 워크플로우

```
1. 에이전트 생성 후 Build 탭에서 수동 테스트
    ↓
2. AI Playground에서 View Trace로 실행 과정 확인
    ↓
3. Examples 탭에서 라벨링된 질문/가이드라인 추가
    ↓
4. SME에게 공유 링크 전달 → 전문가 피드백 수집
    ↓
5. AI Judge + Synthetic Task Generation으로 자동 평가
    ↓
6. 가이드라인 조정 → 재테스트 → 반복
```

---

## 모니터링 포인트

배포 후 지속적으로 모니터링해야 할 항목:

- **응답 품질**: AI Judge 점수 추이
- **라우팅 정확도** (Supervisor): 올바른 서브 에이전트로 위임되는 비율
- **인용 정확도** (KA): 출처가 올바르게 참조되는 비율
- **사용자 피드백**: 좋아요/싫어요 비율
- **응답 지연**: 엔드포인트 응답 시간
- **오류율**: 실패한 쿼리 비율

---

## 배포 아키텍처

```
┌─────────────────────────────────────────────────┐
│                 Model Serving                     │
│  ┌───────────────────────────────────────────┐   │
│  │         Supervisor Agent Endpoint          │   │
│  │                                           │   │
│  │  ┌─────────────┐  ┌─────────────────────┐│   │
│  │  │ KA Endpoint  │  │ Genie Space (API)   ││   │
│  │  └──────┬──────┘  └──────────┬──────────┘│   │
│  │         │                     │           │   │
│  │  ┌──────┴──────┐  ┌──────────┴──────────┐│   │
│  │  │Vector Search│  │  SQL Warehouse      ││   │
│  │  │   Index     │  │  (UC Tables)        ││   │
│  │  └─────────────┘  └─────────────────────┘│   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │ UC Functions│  │ MCP Servers│  │  MLflow    │ │
│  └────────────┘  └────────────┘  │  Monitoring │ │
│                                   └────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 엔드포인트 연동 방법

에이전트가 배포되면 다음 방식으로 연동할 수 있습니다.

**REST API (curl) 예시:**

```bash
curl -X POST \
  https://<workspace-url>/serving-endpoints/<endpoint-name>/invocations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "이번 달 매출 현황 알려줘"}
    ]
  }'
```

**Python SDK 예시:**

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="<endpoint-name>",
    messages=[
        {"role": "user", "content": "이번 달 매출 현황 알려줘"}
    ]
)

print(response.choices[0].message.content)
```

---

## 워크스페이스 간 마이그레이션

Knowledge Assistant를 다른 워크스페이스로 복제해야 할 경우:

1. 타겟 워크스페이스에 필요한 리소스를 먼저 생성 (Vector Search Index, Volume 등)
2. 소스 워크스페이스에서 SDK로 설정 정보 조회
3. 타겟 워크스페이스에서 `create_knowledge_source` API로 재생성
