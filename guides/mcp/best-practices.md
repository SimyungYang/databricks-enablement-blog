# MCP 베스트 프랙티스

MCP를 효과적으로 활용하기 위한 실전 가이드입니다. 보안부터 Tool 설계, 비용 최적화, 프로덕션 운영까지 실무에서 축적된 노하우를 공유합니다.

{% hint style="info" %}
이 페이지의 내용은 MCP를 "사용"하는 것을 넘어 "잘 사용"하기 위한 가이드입니다. MCP 서버를 처음 설정하는 단계에서는 [일반 MCP 설정](setup-general.md)을, 이미 사용 중이며 품질을 높이고 싶을 때 이 페이지를 참고하세요.
{% endhint %}

---

## 보안

### API 키 관리

| 환경 | 권장 방법 |
|------|----------|
| 로컬 개발 | 환경변수 (`export GITHUB_TOKEN=...`) |
| CI/CD | 시크릿 매니저 (GitHub Secrets, AWS Secrets Manager) |
| Databricks | Databricks Secrets (`dbutils.secrets.get`) |
| 팀 공유 설정 | `.mcp.json`에서 `${ENV_VAR}` 참조 |

{% hint style="warning" %}
API 키를 설정 파일에 직접 하드코딩하지 마세요. 특히 `.mcp.json`이나 `claude_desktop_config.json`을 git에 커밋할 때 토큰이 포함되지 않도록 주의하세요.
{% endhint %}

### 최소 권한 원칙

MCP 서버에 부여하는 권한은 필요한 최소한으로 제한합니다:

- GitHub: 읽기 전용이 필요하면 `repo:read` 스코프만 부여
- Slack: 메시지 읽기만 필요하면 `channels:read` 스코프만 부여
- Filesystem: 특정 디렉토리만 접근 가능하도록 경로 제한

### 데이터 유출 방지

AI 에이전트가 MCP를 통해 외부 시스템에 데이터를 전송할 수 있으므로, 민감 데이터의 유출에 주의해야 합니다:

| 위험 시나리오 | 대응 방법 |
|-------------|----------|
| DB 쿼리 결과가 Slack에 전송됨 | 개인정보(이름, 이메일 등)가 포함된 쿼리에는 마스킹 적용 |
| 소스 코드가 외부 검색 엔진에 전송됨 | 내부 코드 검색은 GitHub MCP, 외부 검색은 Brave Search로 분리 |
| API 키가 대화 컨텍스트에 노출됨 | 환경변수나 시크릿 매니저 사용, 절대 프롬프트에 직접 입력 금지 |

{% hint style="warning" %}
특히 ** 쓰기 권한이 있는 MCP 서버**(Slack 메시지 전송, JIRA 티켓 생성, DB 쓰기 등)는 더욱 주의가 필요합니다. AI 에이전트가 의도치 않게 잘못된 정보를 외부에 전송할 수 있습니다. 프로덕션에서는 쓰기 작업 전 사용자 확인 단계를 추가하는 것을 권장합니다.
{% endhint %}

---

## Tool 설계 원칙

### LLM이 Tool을 선택하는 메커니즘 이해하기

MCP Tool 설계를 올바르게 하려면, 먼저 **LLM이 어떻게 Tool을 선택하는지** 이해해야 합니다:

1. **Tool 목록 주입**: 모든 등록된 Tool의 이름, 설명, 파라미터 스키마가 LLM의 ** 시스템 프롬프트에 포함** 됩니다
2. ** 사용자 요청 분석**: LLM이 사용자의 자연어 요청을 분석합니다
3. ** 매칭 결정**: LLM이 요청과 Tool 설명을 비교하여, 가장 적절한 Tool을 선택합니다
4. ** 파라미터 추출**: 사용자 요청에서 Tool의 파라미터에 해당하는 값을 추출합니다
5. ** 호출 실행**: 선택한 Tool을 추출한 파라미터로 호출합니다

이 과정에서 LLM이 참고하는 정보는 ** 오직 Tool의 이름과 설명** 뿐입니다. 내부 구현 코드는 전혀 보지 못합니다. 따라서 Tool 설계의 핵심은 "LLM이 이 도구가 무엇을 하는지 정확히 이해할 수 있도록 이름과 설명을 작성하는 것"입니다.

### 이름과 설명이 핵심

LLM은 Tool의 ** 이름** 과 ** 설명(description)** 을 보고 어떤 도구를 호출할지 결정합니다. 명확하게 작성하세요:

```python
# 나쁜 예
@mcp.tool()
async def search(q: str) -> str:
    """검색"""
    ...

# 좋은 예
@mcp.tool()
async def search_customer_by_name(customer_name: str) -> str:
    """고객 데이터베이스에서 이름으로 고객을 검색합니다.
    부분 일치를 지원하며, 이름/성/풀네임으로 검색 가능합니다.

    Args:
        customer_name: 검색할 고객 이름 (예: '김철수', '철수')
    """
    ...
```

### Tool 이름 작성 규칙

| 규칙 | 좋은 예 | 나쁜 예 |
|------|--------|--------|
| ** 동작을 포함**| `search_customer`, `create_ticket` | `customer`, `ticket` |
| ** 대상을 명시**| `search_customer_by_email` | `search` |
| **snake_case 사용**| `get_order_status` | `getOrderStatus` |
| ** 축약어 자제**| `search_repository` | `srch_repo` |

### Tool 수 제한

{% hint style="info" %}
Databricks Genie Code는 전체 MCP 서버에 걸쳐 ** 최대 20개 도구** 만 사용할 수 있습니다. Claude Desktop 등 다른 클라이언트에서도 도구가 많을수록 LLM의 선택 정확도가 떨어집니다.
{% endhint %}

권장 사항:
- 자주 사용하는 핵심 도구만 등록하세요
- 유사한 기능은 하나의 도구로 통합하세요
- 사용하지 않는 MCP 서버는 비활성화하세요

### Tool 파라미터 설계

Tool의 파라미터도 LLM이 올바르게 값을 채울 수 있도록 설계해야 합니다:

```python
# 나쁜 예 — 파라미터가 모호
@mcp.tool()
async def query(q: str, opts: dict) -> str:
    """데이터를 조회합니다."""
    ...

# 좋은 예 — 파라미터가 명확하고 타입이 구체적
@mcp.tool()
async def search_orders(
    customer_name: str,
    start_date: str,
    end_date: str,
    status: str = "all"
) -> str:
    """고객의 주문 이력을 기간별로 조회합니다.

    Args:
        customer_name: 고객 이름 (부분 일치 지원, 예: '김철수')
        start_date: 조회 시작일 (YYYY-MM-DD 형식, 예: '2025-01-01')
        end_date: 조회 종료일 (YYYY-MM-DD 형식, 예: '2025-12-31')
        status: 주문 상태 필터 ('all', 'completed', 'pending', 'cancelled')
    """
    ...
```

** 핵심 원칙**: LLM은 사용자의 자연어에서 파라미터 값을 추출해야 합니다. "김철수의 올해 완료된 주문"이라는 요청에서 `customer_name="김철수"`, `start_date="2026-01-01"`, `end_date="2026-12-31"`, `status="completed"`를 정확히 추출하려면, 파라미터의 이름과 설명이 충분히 구체적이어야 합니다.

---

## 도구 이름 하드코딩 금지

에이전트를 프로그래밍 방식으로 개발할 때, 특정 도구 이름을 코드에 직접 넣지 마세요:

```python
# 나쁜 예 - 도구 이름이 변경되면 코드가 깨짐
if tool_name == "search_code":
    result = call_tool("search_code", params)

# 좋은 예 - LLM이 동적으로 도구를 선택하도록 위임
tools = await client.list_tools()
# LLM에게 tools 목록과 사용자 요청을 전달하여 자동 선택
```

---

## 에러 핸들링

### MCP 서버 측

```python
@mcp.tool()
async def query_database(sql: str) -> str:
    """데이터베이스에 SQL 쿼리를 실행합니다."""
    try:
        result = await db.execute(sql)
        return str(result)
    except ConnectionError:
        return "데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해주세요."
    except Exception as e:
        return f"쿼리 실행 중 오류가 발생했습니다: {str(e)}"
```

{% hint style="tip" %}
Tool이 에러를 반환할 때는 LLM이 이해할 수 있는 ** 자연어 메시지** 로 반환하세요. LLM이 에러 내용을 파악하고 사용자에게 적절히 안내할 수 있습니다.
{% endhint %}

### 출력 파싱 금지

도구의 출력 형식은 안정적이지 않을 수 있습니다. 결과 해석은 항상 **LLM에 위임** 하세요:

```python
# 나쁜 예 - 출력을 직접 파싱
result = call_tool("search_code", {"query": "auth"})
files = json.loads(result)["files"]  # 형식이 변경되면 깨짐

# 좋은 예 - LLM에게 해석 위임
result = call_tool("search_code", {"query": "auth"})
llm_response = llm.chat(f"다음 검색 결과를 분석해줘: {result}")
```

---

### Tool 설명 작성 고급 팁

| 팁 | 설명 | 예시 |
|-----|------|------|
| ** 입력/출력 명시**| Tool이 무엇을 받고 무엇을 반환하는지 명확히 기술 | "고객 이름으로 검색하여 ID, 이메일, 가입일을 반환합니다" |
| ** 부정 조건 포함**| 이 Tool을 사용하면 안 되는 경우를 명시 | "실시간 데이터에는 사용하지 마세요. 일별 배치 데이터만 포함됩니다" |
| ** 연관 Tool 언급**| 함께 사용하면 좋은 Tool을 설명에 포함 | "검색 후 상세 정보가 필요하면 get_customer_detail을 사용하세요" |
| ** 예시 입력 포함**| 파라미터 설명에 구체적 예시 추가 | `date_range: '2025-01-01~2025-03-31' 형식` |

---

## 비용 최적화

### Tool 수와 토큰 소비의 관계

각 MCP 도구 호출은 LLM 토큰을 소비합니다. 이 비용 구조를 정확히 이해하면 불필요한 지출을 크게 줄일 수 있습니다:

** 고정 비용 (매 요청마다 발생):**
- 등록된 ** 모든 도구의 이름/설명/파라미터 스키마** 가 시스템 프롬프트에 포함됩니다
- 도구 하나당 약 **100-500 토큰** 을 차지합니다 (설명 길이에 따라)
- 20개 도구가 등록되면, 매 요청마다 **2,000-10,000 토큰** 이 도구 정의에만 소비됩니다

** 변동 비용 (도구 호출 시 발생):**
- 도구 호출 결과가 대화 컨텍스트에 추가됩니다
- 큰 JSON 응답을 반환하면 수천 토큰이 추가로 소비됩니다

** 비용 최적화 전략:**

| 전략 | 효과 | 구현 방법 |
|------|------|----------|
| ** 불필요한 도구 제거**| 고정 비용 절감 | 사용하지 않는 MCP 서버 비활성화 |
| ** 도구 설명 간결화**| 고정 비용 절감 | 핵심 정보만 남기고 불필요한 설명 제거 |
| ** 반환값 요약**| 변동 비용 절감 | 대량 데이터 반환 시 상위 N건만 반환하거나 요약 제공 |
| ** 유사 도구 통합**| 고정 비용 절감 | `search_by_name`, `search_by_email`을 `search_customer(query, field)` 하나로 통합 |
| ** 페이지네이션 구현**| 변동 비용 절감 | 결과가 많을 때 10건씩 반환하고 "더 보기" 옵션 제공 |

{% hint style="warning" %}
** 도구 수의 임계점**: Databricks Genie Code는 최대 20개 도구로 제한되어 있지만, 실무적으로는 **10개 이하** 가 최적입니다. 도구가 많아질수록 LLM의 도구 선택 정확도가 떨어지고, 잘못된 도구를 호출하여 재시도하는 비용이 추가됩니다.
{% endhint %}

---

## 디버깅

### MCP Inspector

MCP SDK에 포함된 Inspector를 사용하면 서버를 대화형으로 테스트할 수 있습니다:

```bash
# Python 서버 테스트
mcp dev server.py

# npx 기반 서버 테스트
npx @modelcontextprotocol/inspector npx -y @modelcontextprotocol/server-github
```

Inspector는 브라우저에서 열리며, 도구 목록 조회, 도구 호출, 결과 확인을 UI로 수행할 수 있습니다.

### Claude Desktop 로그 확인

Claude Desktop에서 MCP 서버 연결에 문제가 있을 때:

```bash
# macOS - Claude Desktop 로그 확인
tail -f ~/Library/Logs/Claude/mcp*.log
```

{% hint style="info" %}
MCP 서버가 Claude Desktop에서 인식되지 않으면: (1) JSON 문법 오류가 없는지 확인, (2) `command` 경로가 올바른지 확인, (3) Claude Desktop을 완전 재시작해 보세요.
{% endhint %}

---

## 프로덕션 운영 가이드

MCP를 개인 실험을 넘어 팀/조직 단위로 프로덕션에 운영할 때 고려할 사항입니다.

### 모니터링 및 관측성

| 모니터링 대상 | 지표 | 임계치 예시 | 대응 |
|-------------|------|-----------|------|
| **MCP 서버 가용성**| 응답 시간, 에러율 | 응답 > 5초 또는 에러율 > 5% | 서버 상태 점검, 재시작 |
| ** 도구 호출 빈도**| 도구별 호출 수/일 | 비정상적 급증 시 | 무한 루프 또는 잘못된 사용 패턴 확인 |
| ** 토큰 소비**| 일별 총 토큰 사용량 | 예산 대비 80% 초과 시 | 불필요한 도구 제거, 응답 크기 최적화 |
| ** 인증 실패**| 인증 에러 수/시간 | 갑작스러운 증가 시 | OAuth 토큰 만료, API 키 갱신 확인 |

### 장애 대응 패턴

MCP 서버 장애 시 AI 에이전트의 동작을 예측하고 대비해야 합니다:

```
시나리오: Slack MCP 서버가 일시적으로 다운

1. Agent가 Slack 메시지 전송을 시도
2. MCP 서버 연결 실패 → 에러 반환
3. LLM이 에러를 인식하고 사용자에게 안내:
   "Slack 메시지 전송에 실패했습니다. 나중에 다시 시도하거나,
    결과를 직접 복사하여 Slack에 붙여넣으시겠습니까?"
```

{% hint style="tip" %}
**Tool의 에러 메시지가 중요한 이유**: MCP 서버가 에러를 반환할 때, 그 메시지는 LLM에게 전달됩니다. LLM은 이 에러 메시지를 읽고 사용자에게 적절한 안내를 합니다. 따라서 에러 메시지를 "Error: 500" 대신 "데이터베이스 연결에 실패했습니다. 네트워크 상태를 확인하거나 잠시 후 다시 시도해주세요."처럼 자연어로 작성하면, 사용자 경험이 크게 향상됩니다.
{% endhint %}

### 업그레이드 전략

MCP 서버를 업그레이드할 때 주의할 점:

| 주의사항 | 설명 |
|---------|------|
| **Tool 이름 변경 금지**| 기존 에이전트 코드나 인스트럭션에서 특정 Tool 이름을 참조할 수 있음 |
| ** 하위 호환성 유지**| 기존 파라미터는 유지하고, 새 파라미터는 선택적(optional)으로 추가 |
| ** 단계적 롤아웃**| 한 번에 모든 사용자에게 적용하지 말고, 소수 사용자로 테스트 후 확대 |
| ** 변경 로그 기록**| Tool 추가/수정/삭제를 문서화하여 팀에 공유 |

### 거버넌스 체크리스트 (조직 단위 배포 시)

- [ ] 모든 MCP 서버에 대한 ** 소유자(Owner)** 가 지정되어 있는가?
- [ ] 각 MCP 서버의 ** 접근 권한 정책** 이 문서화되어 있는가?
- [ ] ** 감사 로그** 가 활성화되어 있고, 정기적으로 검토하는가?
- [ ] MCP 서버 장애 시 ** 알림 체계** 가 구축되어 있는가?
- [ ] ** 비용 모니터링** 이 설정되어 있고, 예산 초과 시 알림이 발생하는가?
- [ ] ** 정기 보안 검토** 일정이 잡혀 있는가? (분기별 권장)
