# MCP 베스트 프랙티스

MCP를 효과적으로 활용하기 위한 실전 가이드입니다.

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

---

## Tool 설계 원칙

### 이름과 설명이 핵심

LLM은 Tool의 **이름**과 **설명(description)**을 보고 어떤 도구를 호출할지 결정합니다. 명확하게 작성하세요:

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

### Tool 수 제한

{% hint style="info" %}
Databricks Genie Code는 전체 MCP 서버에 걸쳐 **최대 20개 도구**만 사용할 수 있습니다. Claude Desktop 등 다른 클라이언트에서도 도구가 많을수록 LLM의 선택 정확도가 떨어집니다.
{% endhint %}

권장 사항:
- 자주 사용하는 핵심 도구만 등록하세요
- 유사한 기능은 하나의 도구로 통합하세요
- 사용하지 않는 MCP 서버는 비활성화하세요

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
Tool이 에러를 반환할 때는 LLM이 이해할 수 있는 **자연어 메시지**로 반환하세요. LLM이 에러 내용을 파악하고 사용자에게 적절히 안내할 수 있습니다.
{% endhint %}

### 출력 파싱 금지

도구의 출력 형식은 안정적이지 않을 수 있습니다. 결과 해석은 항상 **LLM에 위임**하세요:

```python
# 나쁜 예 - 출력을 직접 파싱
result = call_tool("search_code", {"query": "auth"})
files = json.loads(result)["files"]  # 형식이 변경되면 깨짐

# 좋은 예 - LLM에게 해석 위임
result = call_tool("search_code", {"query": "auth"})
llm_response = llm.chat(f"다음 검색 결과를 분석해줘: {result}")
```

---

## 비용 최적화

각 MCP 도구 호출은 LLM 토큰을 소비합니다:

- **도구 정의**: 등록된 모든 도구의 이름/설명/파라미터가 매 요청의 시스템 프롬프트에 포함됨
- **도구 호출 결과**: 결과가 대화 컨텍스트에 추가됨

따라서:
- 불필요한 도구는 제거하여 시스템 프롬프트 토큰을 절약하세요
- 도구의 반환값이 너무 크지 않도록 페이지네이션이나 요약을 적용하세요

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
