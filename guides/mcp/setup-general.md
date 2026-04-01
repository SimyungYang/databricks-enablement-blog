# 일반 MCP 설정 가이드

## MCP 서버 찾기

MCP 서버를 찾을 수 있는 주요 디렉토리입니다:

| 디렉토리 | URL | 특징 |
|----------|-----|------|
| **공식 서버 목록**| [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | Anthropic이 관리하는 레퍼런스 서버 |
| **Smithery**| [smithery.ai](https://smithery.ai) | 커뮤니티 서버 마켓플레이스, 원클릭 설치 |
| **MCP.so**| [mcp.so](https://mcp.so) | 서버 검색 및 비교 |

---

## Claude Desktop에서 MCP 설정

### 설정 파일 위치

| OS | 경로 |
|----|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

### 설정 예시

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-xxx"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/data"]
    }
  }
}
```

{% hint style="warning" %}
설정 파일 수정 후 Claude Desktop을 **재시작** 해야 MCP 서버가 활성화됩니다. 메뉴 바에서 완전 종료 후 다시 실행하세요.
{% endhint %}

---

## Claude Code (CLI)에서 MCP 설정

Claude Code는 두 가지 방식으로 MCP 서버를 등록할 수 있습니다:

### 방법 1: CLI 명령어

```bash
# stdio 기반 로컬 서버 추가
claude mcp add github -- npx -y @modelcontextprotocol/server-github

# 환경변수와 함께 추가
claude mcp add slack -e SLACK_BOT_TOKEN=xoxb-xxx -- npx -y @modelcontextprotocol/server-slack

# 등록된 서버 목록 확인
claude mcp list
```

### 방법 2: 프로젝트 설정 파일 (.mcp.json)

프로젝트 루트에 `.mcp.json` 파일을 생성하면 팀원들과 MCP 설정을 공유할 수 있습니다:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost:5432/mydb"]
    }
  }
}
```

{% hint style="tip" %}
`.mcp.json`에서 `${ENV_VAR}` 구문을 사용하면 실제 토큰 값을 파일에 넣지 않고 환경변수에서 읽을 수 있습니다. 이 파일은 git에 커밋해도 안전합니다.
{% endhint %}

---

## Cursor / VS Code에서 MCP 설정

### Cursor

프로젝트 루트에 `.cursor/mcp.json` 파일을 생성합니다:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"
      }
    }
  }
}
```

### VS Code (GitHub Copilot)

프로젝트 루트에 `.vscode/mcp.json` 파일을 생성합니다:

```json
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"
      }
    }
  }
}
```

---

## 인기 MCP 서버 목록

| 서버 | 패키지 | 주요 기능 |
|------|--------|----------|
| **GitHub**| `@modelcontextprotocol/server-github` | 리포 검색, Issue/PR 관리, 코드 검색 |
| **Slack**| `@modelcontextprotocol/server-slack` | 메시지 전송, 채널 관리, 검색 |
| **Google Drive**| `@modelcontextprotocol/server-gdrive` | 파일 검색, 문서 읽기 |
| **PostgreSQL**| `@modelcontextprotocol/server-postgres` | DB 스키마 조회, SQL 쿼리 실행 |
| **Filesystem**| `@modelcontextprotocol/server-filesystem` | 로컬 파일 읽기/쓰기/검색 |
| **Brave Search**| `@modelcontextprotocol/server-brave-search` | 웹 검색, 로컬 검색 |
| **Notion**| `@notionhq/notion-mcp-server` | 페이지/DB 관리, 검색, 댓글 |
| **Jira**| `@anthropic/jira-mcp-server` | 이슈 생성/검색/관리 |

{% hint style="info" %}
위 패키지들은 `npx -y <패키지명>`으로 바로 실행할 수 있습니다. Node.js 18+ 가 설치되어 있어야 합니다.
{% endhint %}

---

## 커스텀 MCP 서버 만들기 (Python)

Python MCP SDK(`mcp`)를 사용하면 간단하게 자체 MCP 서버를 만들 수 있습니다.

### 환경 설정

```bash
# uv 사용 (권장)
uv init my-mcp-server && cd my-mcp-server
uv venv && source .venv/bin/activate
uv add "mcp[cli]"

# 또는 pip 사용
pip install "mcp[cli]"
```

### 서버 코드 작성

```python
# server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-tools")

@mcp.tool()
async def search_products(query: str) -> str:
    """제품 카탈로그에서 검색합니다.

    Args:
        query: 검색할 제품명 또는 키워드
    """
    # 실제 비즈니스 로직 (DB 조회, API 호출 등)
    results = [
        {"name": "노트북 Pro", "price": 1200000},
        {"name": "노트북 Air", "price": 900000},
    ]
    return str([r for r in results if query.lower() in r["name"].lower()])

@mcp.tool()
async def get_order_status(order_id: str) -> str:
    """주문 상태를 조회합니다.

    Args:
        order_id: 주문 번호
    """
    return f"주문 {order_id}: 배송 중 (예상 도착일: 2026-04-02)"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 테스트 및 디버깅

```bash
# MCP Inspector로 대화형 테스트
mcp dev server.py

# Claude Desktop에 등록
# claude_desktop_config.json에 추가:
```

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/my-mcp-server", "server.py"]
    }
  }
}
```

{% hint style="tip" %}
`mcp dev server.py` 명령어는 브라우저에서 MCP Inspector를 열어, 서버의 도구를 대화형으로 테스트할 수 있게 해줍니다. 개발 중 반드시 활용하세요.
{% endhint %}

---

## 다음 단계

- [Databricks MCP 활용](databricks-mcp.md): Databricks 환경에서 Managed/External/Custom MCP 활용하기
- [베스트 프랙티스](best-practices.md): 보안, Tool 설계, 디버깅 팁
