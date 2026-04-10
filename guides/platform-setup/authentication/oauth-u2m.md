# OAuth U2M (사용자 인증)

## 개요

OAuth U2M(User-to-Machine)은 **사용자가 브라우저로 로그인하면, 도구(CLI/SDK/IDE)가 사용자를 대신하여 Databricks API를 호출** 하는 인증 방식입니다. "대화형(Interactive) 인증"이라고도 부릅니다.

### 왜 OAuth U2M이 필요한가

기존에 개발자들은 PAT(Personal Access Token)를 발급받아 환경변수나 설정 파일에 저장하고 사용했습니다. 이 방식에는 근본적인 문제가 있습니다.

| PAT 방식의 문제 | OAuth U2M의 해결 |
|----------------|-----------------|
| 토큰이 평문으로 설정 파일에 저장됨 | 토큰이 메모리에만 존재, 디스크에 저장하지 않음 |
| 토큰 수명이 길어 유출 시 피해 큼 | 1시간 수명, 자동 갱신 |
| 토큰 공유/복사가 쉬움 | 브라우저 인증 필수, 복사 불가 |
| 수동 갱신 필요 | refresh_token으로 자동 갱신 |
| 워크스페이스 레벨만 지원 | Account + Workspace 레벨 모두 지원 |

이 테이블이 보여주듯, OAuth U2M은 PAT의 모든 보안 약점을 구조적으로 해결합니다.

---

## 동작 원리: PKCE 흐름

OAuth U2M은 **Authorization Code Flow with PKCE** 를 사용합니다. PKCE(Proof Key for Code Exchange, 발음: "pixie")는 OAuth 2.0의 보안 확장으로, 원래 모바일 앱처럼 **client_secret을 안전하게 저장할 수 없는 환경** 을 위해 설계되었습니다.

### PKCE가 필요한 이유

표준 Authorization Code Flow에서는 인증 서버가 브라우저에 `authorization_code`를 전달하고, 클라이언트가 이 코드를 `access_token`으로 교환합니다. 문제는 이 과정에서 **Authorization Code Interception Attack** 이 가능하다는 것입니다.

- 악성 앱이 같은 디바이스에서 redirect URI를 가로챌 수 있음
- 가로챈 authorization_code로 토큰을 탈취할 수 있음

PKCE는 이 공격을 **암호학적으로 차단** 합니다.

### 전체 흐름

```
사용자          CLI/SDK            브라우저          Databricks 인증서버
  │               │                  │                    │
  │  명령 실행     │                  │                    │
  │──────────────▶│                  │                    │
  │               │                  │                    │
  │               │ 1. code_verifier │                    │
  │               │    (43~128자 랜덤 문자열 생성)          │
  │               │                  │                    │
  │               │ 2. code_challenge│                    │
  │               │    = SHA256(code_verifier)            │
  │               │    → Base64URL 인코딩                  │
  │               │                  │                    │
  │               │ 3. 브라우저 오픈   │                    │
  │               │─────────────────▶│                    │
  │               │                  │ 4. 인증 요청        │
  │               │                  │  (code_challenge   │
  │               │                  │   + client_id)     │
  │               │                  │───────────────────▶│
  │               │                  │                    │
  │  5. 로그인 + 동의                 │◀───────────────────│
  │◀─────────────────────────────────│   로그인 페이지     │
  │  ID/PW 입력 + 권한 동의           │                    │
  │──────────────────────────────────▶                    │
  │               │                  │                    │
  │               │                  │ 6. authorization_  │
  │               │                  │    code 발급       │
  │               │                  │◀───────────────────│
  │               │                  │                    │
  │               │ 7. 토큰 교환 요청 │                    │
  │               │  (authorization_code                  │
  │               │   + code_verifier)                    │
  │               │───────────────────────────────────────▶
  │               │                  │                    │
  │               │                  │  8. 서버가 검증:    │
  │               │                  │  SHA256(code_      │
  │               │                  │  verifier) ==      │
  │               │                  │  code_challenge?   │
  │               │                  │                    │
  │               │ 9. access_token + refresh_token       │
  │               │◀───────────────────────────────────────│
  │               │                  │                    │
  │  결과 반환     │                  │                    │
  │◀──────────────│                  │                    │
```

### 핵심 보안 메커니즘

위 흐름에서 보안의 핵심은 **step 1-2와 step 7-8** 입니다.

1. CLI가 `code_verifier`(랜덤 문자열)를 생성하고, 그 **SHA256 해시값** (`code_challenge`)만 인증 서버에 전송
2. authorization_code를 토큰으로 교환할 때, CLI가 **원본 `code_verifier`** 를 전송
3. 인증 서버가 `SHA256(code_verifier) == code_challenge`인지 검증

{% hint style="warning" %}
**왜 안전한가**: 공격자가 authorization_code를 가로채더라도, `code_verifier`를 모르면 토큰 교환이 불가능합니다. `code_challenge`에서 `code_verifier`를 역산하는 것은 SHA256의 단방향성 때문에 사실상 불가능합니다.
{% endhint %}

---

## On-Behalf-Of 메커니즘

OAuth U2M으로 발급된 토큰은 **사용자의 ID와 권한** 을 담고 있습니다. CLI/SDK가 이 토큰으로 API를 호출하면:

- Databricks는 요청을 **사용자 본인의 요청** 으로 처리
- Unity Catalog 권한, 워크스페이스 ACL 등 **사용자에게 부여된 권한** 만 적용
- 감사 로그에 **사용자 이름** 으로 기록

이것이 "On-Behalf-Of(대리 인증)"의 핵심입니다. 도구는 독립적인 권한을 갖지 않으며, 항상 사용자의 권한 범위 내에서만 동작합니다.

---

## 지원 도구

다음 도구들이 OAuth U2M을 기본 지원합니다.

| 도구 | 설정 방법 | 비고 |
|------|----------|------|
| **Databricks CLI** | `databricks auth login` | v0.200+ 기본 인증 |
| **Python SDK** | `Config(auth_type="databricks-cli")` | databricks-sdk 패키지 |
| **Java SDK** | `DatabricksConfig.setAuthType("databricks-cli")` | databricks-sdk-java |
| **Go SDK** | `databricks.Config{AuthType: "databricks-cli"}` | databricks-sdk-go |
| **Terraform** | `provider "databricks" {}` (기본) | databricks provider |
| **VS Code** | Databricks Extension 설정 | UI에서 로그인 |
| **Databricks Connect** | SparkSession 연결 시 자동 | Spark Remote 프로토콜 |

---

## 설정 방법

### 1. Databricks CLI로 프로파일 생성

가장 일반적인 설정 방법은 Databricks CLI의 `auth login` 명령입니다.

```bash
# Account 레벨 인증
databricks auth login \
  --host https://accounts.cloud.databricks.com \
  --account-id <account-id> \
  --profile ACCOUNT

# Workspace 레벨 인증
databricks auth login \
  --host https://<workspace-url> \
  --profile DEV
```

이 명령은 다음을 수행합니다.
1. 브라우저를 열어 Databricks 로그인 페이지로 이동
2. 사용자가 로그인하면 OAuth 토큰을 안전하게 저장
3. `~/.databrickscfg` 파일에 프로파일 정보 기록

생성된 프로파일 파일 예시:

```ini
# ~/.databrickscfg

[ACCOUNT]
host       = https://accounts.cloud.databricks.com
account_id = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

[DEV]
host = https://adb-1234567890.12.azuredatabricks.net
```

{% hint style="info" %}
**토큰은 어디에 저장되는가**: OAuth 토큰은 `~/.databrickscfg`에 저장되지 **않습니다.** 토큰은 OS의 보안 자격 증명 저장소(macOS Keychain, Windows Credential Manager, Linux keyring)에 암호화되어 저장됩니다. `.databrickscfg`에는 호스트 URL과 프로파일 이름만 기록됩니다.
{% endhint %}

### 2. 환경변수 방식

프로파일 파일 대신 환경변수로도 설정할 수 있습니다.

```bash
# Workspace 레벨
export DATABRICKS_HOST=https://<workspace-url>

# Account 레벨
export DATABRICKS_HOST=https://accounts.cloud.databricks.com
export DATABRICKS_ACCOUNT_ID=<account-id>
```

환경변수를 설정한 후 `databricks auth login`을 실행하면, 해당 호스트에 대한 OAuth 인증이 시작됩니다.

### 3. Python SDK 코드 예시

```python
from databricks.sdk import WorkspaceClient

# 프로파일 사용
w = WorkspaceClient(profile="DEV")

# 또는 직접 지정
w = WorkspaceClient(
    host="https://<workspace-url>",
    auth_type="databricks-cli"
)

# API 호출 — 사용자 본인의 권한으로 실행됨
clusters = w.clusters.list()
for c in clusters:
    print(f"{c.cluster_name}: {c.state}")
```

```python
from databricks.sdk import AccountClient

# Account 레벨 클라이언트
a = AccountClient(
    host="https://accounts.cloud.databricks.com",
    account_id="<account-id>",
    profile="ACCOUNT"
)

# 워크스페이스 목록 조회
workspaces = a.workspaces.list()
for ws in workspaces:
    print(f"{ws.workspace_name}: {ws.workspace_id}")
```

---

## 토큰 갱신 메커니즘

OAuth U2M의 가장 큰 장점 중 하나는 **토큰 자동 갱신** 입니다.

### 동작 방식

1. 최초 인증 시 `access_token`(1시간)과 `refresh_token`을 함께 발급
2. `access_token`이 만료되면, SDK/CLI가 자동으로 `refresh_token`을 사용하여 새 토큰 발급
3. 이 과정은 사용자에게 투명하게 진행됨 (재로그인 불필요)

```
access_token (1시간) ──── 만료 ────▶ refresh_token으로 자동 갱신
                                         │
                                         ▼
                                    새 access_token (1시간)
                                         │
                                         ▼ (반복)
```

### scope에 offline_access 포함

자동 갱신이 가능하려면 OAuth 인증 요청 시 `scope`에 `offline_access`가 포함되어야 합니다. Databricks CLI와 SDK는 이를 기본으로 포함하므로, 사용자가 별도로 설정할 필요가 없습니다.

```
# 내부적으로 사용되는 scope 예시
scope=all-apis+offline_access
```

### 토큰 상태 확인

```bash
# 현재 토큰 상태 확인
databricks auth token --profile DEV

# 출력 예시
# {
#   "access_token": "eyJhbG...",
#   "token_type": "Bearer",
#   "expiry": "2026-04-08T15:30:00.000Z"
# }
```

```bash
# 인증 상태 진단
databricks auth describe --profile DEV

# 프로파일 목록 확인
databricks auth profiles
```

{% hint style="warning" %}
**refresh_token도 만료됩니다**: refresh_token의 수명은 Databricks Account 관리자가 설정합니다. 기본값은 비교적 길지만 무한하지 않으므로, 오랜 기간 사용하지 않은 프로파일은 재로그인이 필요할 수 있습니다. `databricks auth login --profile <name>`으로 갱신하세요.
{% endhint %}

---

## Unified Client Authentication

Databricks SDK는 **Unified Client Authentication** 이라는 통합 인증 체계를 제공합니다. 이 체계 덕분에 동일한 설정으로 CLI, Python SDK, Java SDK, Terraform 등 모든 도구에서 인증할 수 있습니다.

인증 우선순위(위에서 아래로):

1. **직접 구성** — 코드에서 `Config(host=..., token=...)` 등으로 명시
2. **환경변수** — `DATABRICKS_HOST`, `DATABRICKS_TOKEN` 등
3. **프로파일** — `~/.databrickscfg`의 `[DEFAULT]` 또는 지정 프로파일
4. **자동 탐색** — Azure MSI, GCP WIF 등 클라우드 네이티브 인증

이 우선순위는 모든 Databricks SDK/도구에서 동일하게 적용됩니다. 한 번 `.databrickscfg`를 설정하면, CLI에서도 Python에서도 Terraform에서도 같은 프로파일로 인증됩니다.

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| 브라우저가 열리지 않음 | 헤드리스 환경 (서버, 컨테이너) | OAuth M2M으로 전환, 또는 `--login-timeout` 설정 후 URL 수동 복사 |
| `Token refresh failed` | refresh_token 만료 | `databricks auth login`으로 재인증 |
| `Permission denied` | 사용자 권한 부족 | Unity Catalog GRANT 확인, Workspace Admin에게 권한 요청 |
| `Invalid host` | 잘못된 워크스페이스 URL | `https://`를 포함한 전체 URL 확인 |
| 프로파일 충돌 | 환경변수와 프로파일 동시 설정 | `unset DATABRICKS_HOST` 등으로 환경변수 제거 |

---

## 한계와 주의사항

- **헤드리스 환경 불가**: 브라우저가 없는 서버, Docker 컨테이너, CI/CD 파이프라인에서는 사용할 수 없습니다. 이 경우 OAuth M2M을 사용하세요.
- **자동화에 부적합**: 사람의 개입(브라우저 로그인)이 필요하므로, 무인 실행이 필요한 Job이나 파이프라인에는 적합하지 않습니다.
- **SSO 의존**: 조직이 SAML/OIDC SSO를 사용하는 경우, IdP 장애 시 로그인이 불가능할 수 있습니다.
- **멀티 워크스페이스**: 여러 워크스페이스를 사용하는 경우, 각 워크스페이스마다 별도 프로파일을 만들어야 합니다.
