# 일반 MCP 설정 가이드

## 개요

이 페이지에서는 Claude Desktop, Claude Code, Cursor, VS Code 등 다양한 MCP 클라이언트에서 MCP 서버를 설정하는 방법을 안내합니다. 각 클라이언트마다 설정 방식이 다른 이유와, 팀 단위로 MCP 설정을 효율적으로 공유하는 전략도 함께 다룹니다.

### 왜 클라이언트마다 설정 방식이 다른가

MCP는 프로토콜 자체만 표준화했을 뿐, **설정 파일 형식** 은 각 클라이언트가 자유롭게 결정합니다. 이는 의도적 설계입니다:

- **Claude Desktop**: `claude_desktop_config.json` — 데스크톱 앱이므로 중앙 설정 파일 사용
- **Claude Code**: `.mcp.json` 또는 CLI 명령어 — CLI 도구이므로 프로젝트별/글로벌 설정 지원
- **Cursor**: `.cursor/mcp.json` — IDE이므로 프로젝트 디렉토리 내 설정
- **VS Code**: `.vscode/mcp.json` — VS Code의 기존 설정 패턴을 따름
- **Databricks Genie Code**: UI에서 설정 — 엔터프라이즈 환경이므로 Unity Catalog Connection 기반

이 차이가 중요한 이유는, **같은 MCP 서버를 여러 클라이언트에서 사용** 할 때 각각의 설정 방식을 알아야 하기 때문입니다. MCP 서버 자체는 동일하지만, 클라이언트에게 "이 서버를 이런 방식으로 실행하라"고 알려주는 설정만 다릅니다.

{% hint style="info" %}
**전송 방식에 따른 차이**: 로컬 클라이언트(Claude Desktop, Claude Code, Cursor)는 **stdio** 와 **Streamable HTTP** 를 모두 지원하지만, 원격 클라이언트(Databricks Genie Code)는 **Streamable HTTP만** 지원합니다. stdio는 로컬 프로세스 통신이므로 원격 환경에서는 사용할 수 없습니다.
{% endhint %}

---

## MCP 서버 찾기

MCP 서버를 찾을 수 있는 주요 디렉토리입니다:

| 디렉토리 | URL | 특징 |
|----------|-----|------|
| **공식 서버 목록** | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | Anthropic이 관리하는 레퍼런스 서버 |
| **Smithery** | [smithery.ai](https://smithery.ai) | 커뮤니티 서버 마켓플레이스, 원클릭 설치 |
| **MCP.so** | [mcp.so](https://mcp.so) | 서버 검색 및 비교 |

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

### 설정 파일 구조 이해

Claude Desktop 설정 파일의 각 필드의 의미를 정확히 이해하면 문제 해결이 쉬워집니다:

```json
{
  "mcpServers": {
    "서버별칭": {                           // Claude에서 표시될 이름
      "command": "npx",                    // 실행할 명령어 (npx, python, uv 등)
      "args": ["-y", "패키지명", "추가인자"], // 명령어 인자
      "env": {                             // 환경변수 (API 키 등)
        "API_KEY": "값"
      }
    }
  }
}
```

**자주 발생하는 문제:**

| 증상 | 원인 | 해결 |
|------|------|------|
| 서버가 목록에 안 나옴 | JSON 문법 오류 (쉼표, 중괄호) | JSON 검증 도구로 확인 |
| 서버 연결 실패 | `command` 경로가 잘못됨 | `which npx` 등으로 절대 경로 확인 |
| 인증 오류 | API 키가 잘못되거나 만료됨 | 키 재발급 후 교체 |
| 도구가 0개 | 패키지 버전 불일치 | `npx -y` 대신 특정 버전 지정 |

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

### 보안 고려사항: 스코프 계층 이해

Claude Code는 MCP 서버를 세 가지 스코프로 등록할 수 있습니다:

| 스코프 | 저장 위치 | 적용 범위 | 사용 시나리오 |
|--------|----------|----------|-------------|
| **project** | `.mcp.json` (프로젝트 루트) | 해당 프로젝트에서만 활성화 | 프로젝트 전용 DB, 프로젝트 리포 |
| **user** | `~/.claude/` | 모든 프로젝트에서 활성화 | Slack, 개인 GitHub, 웹 검색 등 범용 도구 |

```bash
# 프로젝트 스코프 (기본값)
claude mcp add my-db -- npx -y @modelcontextprotocol/server-postgres "postgresql://..."

# 글로벌 스코프
claude mcp add --scope user slack -e SLACK_BOT_TOKEN=xoxb-xxx -- npx -y @modelcontextprotocol/server-slack
```

{% hint style="warning" %}
**보안 원칙**: 데이터베이스 접속 정보가 포함된 MCP 서버는 **반드시 project 스코프** 로 등록하세요. 글로벌 스코프에 등록하면 관련 없는 프로젝트에서도 해당 DB에 접근할 수 있게 됩니다.
{% endhint %}

---

## Cursor / VS Code에서 MCP 설정

### 왜 IDE별로 설정 파일 위치가 다른가

IDE마다 프로젝트 설정 파일의 관례가 다르기 때문입니다. Cursor는 `.cursor/` 디렉토리, VS Code는 `.vscode/` 디렉토리를 사용합니다. MCP 프로토콜은 전송 방식과 메시지 형식만 표준화하고, 설정 파일 형식은 각 클라이언트에 위임했습니다.

**실전 팁**: 같은 프로젝트에서 Cursor와 VS Code를 모두 사용하는 팀이라면, 두 설정 파일을 모두 만들어 git에 커밋하세요. MCP 서버 설정은 동일하고 파일 위치만 다르므로, 하나를 작성하고 복사하면 됩니다.

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

{% hint style="info" %}
VS Code에서는 `"servers"` 키를 사용하지만, Claude Desktop과 Cursor에서는 `"mcpServers"` 키를 사용합니다. 설정 파일을 복사할 때 이 차이를 주의하세요.
{% endhint %}

### Databricks Genie Code에서 MCP 설정

Databricks Genie Code는 위의 로컬 클라이언트와 전혀 다른 방식으로 MCP를 설정합니다. JSON 파일이 아니라 **UI** 에서 설정하며, Unity Catalog Connection을 통해 인증을 관리합니다.

```
Genie Code 패널 > 설정 아이콘 > MCP Servers > Add Server
→ Managed MCP: Unity Catalog Functions, Vector Search, Genie Space 등 선택
→ External MCP: Unity Catalog Connection 선택
→ Custom MCP: Databricks App URL 입력
```

이 방식의 장점은 **개별 사용자가 API 키를 관리할 필요가 없다** 는 것입니다. 관리자가 Unity Catalog Connection을 한 번 설정하면, 워크스페이스의 모든 사용자가 해당 MCP 서버를 사용할 수 있습니다.

자세한 내용은 [Databricks MCP 활용](databricks-mcp.md) 페이지를 참고하세요.

---

## 인기 MCP 서버 목록

| 서버 | 패키지 | 주요 기능 |
|------|--------|----------|
| **GitHub** | `@modelcontextprotocol/server-github` | 리포 검색, Issue/PR 관리, 코드 검색 |
| **Slack** | `@modelcontextprotocol/server-slack` | 메시지 전송, 채널 관리, 검색 |
| **Google Drive** | `@modelcontextprotocol/server-gdrive` | 파일 검색, 문서 읽기 |
| **PostgreSQL** | `@modelcontextprotocol/server-postgres` | DB 스키마 조회, SQL 쿼리 실행 |
| **Filesystem** | `@modelcontextprotocol/server-filesystem` | 로컬 파일 읽기/쓰기/검색 |
| **Brave Search** | `@modelcontextprotocol/server-brave-search` | 웹 검색, 로컬 검색 |
| **Notion** | `@notionhq/notion-mcp-server` | 페이지/DB 관리, 검색, 댓글 |
| **Jira** | `@anthropic/jira-mcp-server` | 이슈 생성/검색/관리 |

{% hint style="info" %}
위 패키지들은 `npx -y <패키지명>`으로 바로 실행할 수 있습니다. Node.js 18+ 가 설치되어 있어야 합니다.
{% endhint %}

### 서버 설치 전 확인사항

MCP 서버를 설치하기 전에 다음 환경이 준비되어 있는지 확인하세요:

| 필요 환경 | 확인 명령어 | 최소 버전 |
|----------|-----------|----------|
| **Node.js** | `node --version` | 18.0+ (대부분의 MCP 서버 기본 요구) |
| **npm/npx** | `npx --version` | Node.js와 함께 설치됨 |
| **Python** | `python --version` | 3.10+ (Python MCP 서버 사용 시) |
| **uv**(선택)| `uv --version` | 최신 (Python MCP 개발 시 권장) |

```bash
# Node.js 설치 확인 및 MCP 서버 테스트
node --version           # v18.0.0 이상 필요
npx --version            # npx 사용 가능 확인

# 간단한 MCP 서버 테스트 (Filesystem)
npx -y @modelcontextprotocol/server-filesystem /tmp
# 정상이면 JSON-RPC 메시지가 stdout에 출력됨
```

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

## 팀 설정 공유 전략

### 전략 1: `.mcp.json` + 환경변수 (권장)

팀 전체가 같은 MCP 서버를 사용하도록 프로젝트 루트에 `.mcp.json`을 커밋하되, 실제 인증 정보는 환경변수로 분리합니다:

```
프로젝트 리포지토리에 포함 (git 커밋):
├── .mcp.json                  ← MCP 서버 구성 (토큰 없이)
├── .env.example               ← 환경변수 템플릿 (실제 값 없이)
└── README.md                  ← MCP 설정 가이드 링크

각 팀원의 로컬 환경:
└── .env                       ← 실제 토큰 값 (.gitignore에 추가)
```

### 전략 2: 문서 기반 공유

CI/CD 시크릿 매니저(GitHub Secrets, AWS Secrets Manager 등)와 연동하여, 팀 위키에 설정 절차를 문서화합니다. 새 팀원 온보딩 시 문서를 따라 설정하면 됩니다.

### 전략 3: Databricks Unity Catalog Connection (엔터프라이즈)

Databricks 환경에서는 Unity Catalog Connection으로 MCP 서버를 중앙 관리합니다. 관리자가 한 번 Connection을 생성하면, 워크스페이스의 모든 사용자가 해당 MCP 서버를 사용할 수 있습니다. 개별 사용자가 API 키를 관리할 필요가 없어 **가장 안전하고 효율적인 방법** 입니다.

{% hint style="info" %}
**권장 조합**: 로컬 개발에서는 `.mcp.json` + 환경변수, Databricks 환경에서는 Unity Catalog Connection. 두 환경에서 같은 MCP 서버를 사용하되, 인증 방식만 다르게 설정합니다.
{% endhint %}

---

## 다음 단계

- [Databricks MCP 활용](databricks-mcp.md): Databricks 환경에서 Managed/External/Custom MCP 활용하기
- [베스트 프랙티스](best-practices.md): 보안, Tool 설계, 디버깅 팁
