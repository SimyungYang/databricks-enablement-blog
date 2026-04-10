# PAT & Token Federation

이 페이지에서는 두 가지 인증 방법을 다룹니다. **Personal Access Token(PAT)** 은 가장 오래된 Databricks 인증 방식으로, 간단하지만 보안 한계가 있습니다. **OAuth Token Federation** 은 가장 최신 방식으로, Secret 관리 부담을 완전히 제거합니다.

---

## Part 1: Personal Access Token (PAT)

### PAT란

PAT(Personal Access Token)는 **워크스페이스 레벨에서 발급되는 문자열 기반 토큰** 입니다. HTTP 요청의 `Authorization: Bearer <token>` 헤더에 포함하여 인증합니다. Databricks 초기부터 지원된 가장 단순한 인증 방식입니다.

### 언제 PAT를 사용하는가

{% hint style="warning" %}
**Databricks는 PAT 대신 OAuth를 강력히 권장합니다.** PAT는 다음과 같은 제한적 상황에서만 사용하세요.
{% endhint %}

| 상황 | 사유 |
|------|------|
| **빠른 API 테스트** | curl로 즉시 테스트, 프로덕션 전환 시 OAuth로 교체 |
| **레거시 시스템 연동** | OAuth를 지원하지 않는 구형 도구/라이브러리 |
| **학습/교육 목적** | 인증 개념을 이해하기 위한 가장 단순한 예시 |

---

### PAT 생성

#### UI에서 생성

1. Workspace > **Settings** > **Developer** > **Access tokens** 이동
2. **Generate new token** 클릭
3. Comment(설명)와 Lifetime(수명) 입력
4. **Generate** 클릭 → 토큰이 한 번만 표시됨

#### CLI로 생성

```bash
# 사용자 본인의 PAT 생성
databricks tokens create \
  --comment "API 테스트용" \
  --lifetime-seconds 86400 \
  --profile DEV

# 출력 예시
# {
#   "token_info": {
#     "token_id": "dapi...",
#     "creation_time": 1712563200000,
#     "expiry_time": 1712649600000,
#     "comment": "API 테스트용"
#   },
#   "token_value": "dapi1234567890abcdef..."
# }
```

#### Service Principal용 OBO Token

Service Principal은 직접 UI에 로그인할 수 없으므로, 관리자가 **On-Behalf-Of(OBO)** 방식으로 SP의 PAT를 대리 발급합니다.

```bash
# SP 대신 PAT 생성 (관리자 권한 필요)
databricks token-management create-obo-token \
  --application-id <sp-application-id> \
  --comment "CI/CD 파이프라인용" \
  --lifetime-seconds 7776000 \
  --profile ADMIN
```

{% hint style="info" %}
**OBO Token vs OAuth M2M**: SP용 PAT(OBO Token)보다는 OAuth M2M(client_credentials)을 권장합니다. OAuth M2M은 토큰 자동 갱신을 지원하고, Secret 로테이션이 더 유연합니다.
{% endhint %}

---

### Scoped PAT (권한 범위 제한)

PAT는 기본적으로 사용자의 **전체 권한** 으로 동작합니다. Scoped PAT를 사용하면 특정 API 범위로만 제한할 수 있습니다.

지원되는 scope는 다음과 같습니다.

| Scope | 접근 가능 API |
|-------|-------------|
| `sql` | SQL Warehouse, Query 실행 |
| `unity-catalog` | Unity Catalog 메타데이터 관리 |
| `scim` | 사용자/그룹 관리 (SCIM API) |
| `clusters` | 클러스터 생성/관리 |
| `workspace` | 노트북, 디렉토리 관리 |

Scoped PAT를 사용하면, 토큰이 유출되더라도 지정된 API 범위 밖의 작업은 수행할 수 없어 피해를 제한할 수 있습니다.

---

### PAT 보안 관리

#### 자동 폐기 정책

Databricks는 **90일간 미사용된 PAT를 자동 폐기** 합니다. 이는 "잊혀진 토큰"이 무한히 유효한 상태로 남는 것을 방지합니다.

#### 워크스페이스 관리자 정책

관리자는 다음을 설정할 수 있습니다.

| 정책 | 설명 |
|------|------|
| **PAT 비활성화** | 워크스페이스 전체에서 PAT 사용 금지 |
| **최대 수명 제한** | 예: 최대 90일까지만 유효한 토큰 발급 허용 |
| **특정 사용자만 허용** | PAT 발급 권한을 관리자에게만 제한 |

```bash
# 워크스페이스의 PAT 정책 확인
databricks workspace-conf get-status \
  --keys "enableTokensConfig,maxTokenLifetimeDays" \
  --profile DEV
```

#### 토큰 모니터링

```bash
# 현재 활성 토큰 목록 (관리자)
databricks token-management list --profile ADMIN

# 특정 사용자의 토큰
databricks token-management list \
  --created-by-id <user-id> \
  --profile ADMIN
```

---

### PAT vs OAuth: 상세 비교

아래 테이블은 PAT와 OAuth의 핵심 차이를 비교합니다.

| 항목 | PAT | OAuth (U2M/M2M) |
|------|-----|-----------------|
| **토큰 수명** | 사용자 지정 (무기한 가능) | 1시간 (고정) |
| **자동 갱신** | ❌ 수동 재발급 | ✅ 자동 |
| **Account 레벨** | ❌ 워크스페이스만 | ✅ Account + Workspace |
| **토큰 저장** | 평문 문자열 (파일, 환경변수) | OS 보안 저장소 (U2M) 또는 메모리 (M2M) |
| **유출 시 피해** | 토큰 수명 동안 무제한 접근 | 최대 1시간 (자동 만료) |
| **감사 추적** | 토큰 ID로 추적 | OAuth 세션으로 추적 |
| **멀티 워크스페이스** | 워크스페이스별 별도 토큰 | 프로파일로 통합 관리 |
| **PKCE 보호** | ❌ | ✅ (U2M) |

이 비교가 명확히 보여주듯, **OAuth는 모든 보안 지표에서 PAT보다 우수합니다.** PAT의 유일한 장점은 "단순함"이지만, Databricks CLI/SDK의 OAuth 지원이 성숙해진 현재, 이 장점도 크게 희석되었습니다.

---

### PAT 사용 예시 (참고용)

```bash
# curl로 API 호출
curl -X GET "https://<workspace-host>/api/2.0/clusters/list" \
  -H "Authorization: Bearer dapi1234567890abcdef..."

# .databrickscfg에 PAT 설정
# [DEV-PAT]
# host  = https://<workspace-host>
# token = dapi1234567890abcdef...
```

```python
from databricks.sdk import WorkspaceClient

# PAT로 인증
w = WorkspaceClient(
    host="https://<workspace-host>",
    token="dapi1234567890abcdef..."
)

clusters = w.clusters.list()
```

---

## Part 2: OAuth Token Federation

### 개념

OAuth Token Federation은 **외부 IdP(Identity Provider)가 발급한 OIDC 토큰으로 Databricks에 인증** 하는 방식입니다. 핵심 아이디어는 단순합니다:

> "이미 신뢰할 수 있는 외부 시스템이 발급한 신원 증명을 Databricks가 그대로 수용한다."

이를 통해 **Databricks Secret(client_secret)을 전혀 관리하지 않고도** 인증할 수 있습니다.

### 왜 혁신적인가

OAuth M2M의 가장 큰 운영 부담은 **Secret 관리** 입니다.

| OAuth M2M의 Secret 관리 과제 | Token Federation의 해결 |
|-----------------------------|------------------------|
| Secret 생성/저장/로테이션 | Secret 자체가 없음 |
| Secret 유출 위험 (CI/CD 변수, 설정 파일) | 유출 가능한 Secret이 존재하지 않음 |
| Secret 만료 시 서비스 중단 | 외부 IdP가 매번 새 토큰 발급 |
| 멀티 환경(dev/staging/prod) Secret 관리 | 환경별 외부 토큰 자동 발급 |

{% hint style="info" %}
**비유**: 호텔에서 체크인할 때 여권(외부 IdP 토큰)을 보여주면, 호텔(Databricks)이 객실 키(access_token)를 발급하는 것과 같습니다. 여권은 이미 신뢰할 수 있는 기관(정부 = IdP)이 발급했으므로, 호텔이 별도의 회원 카드(client_secret)를 요구하지 않습니다.
{% endhint %}

---

### 동작 원리

```
외부 워크로드          외부 IdP              Databricks
(GitHub Actions)    (GitHub OIDC)         인증서버
       │                │                    │
       │ 1. OIDC 토큰    │                    │
       │    요청          │                    │
       │───────────────▶│                    │
       │                │                    │
       │ 2. OIDC 토큰    │                    │
       │    발급          │                    │
       │◀───────────────│                    │
       │                │                    │
       │ 3. Databricks 토큰 교환 요청          │
       │    (외부 OIDC 토큰 +                  │
       │     grant_type=                      │
       │     urn:ietf:params:oauth:           │
       │     grant-type:token-exchange)       │
       │──────────────────────────────────────▶
       │                                      │
       │                    4. 외부 토큰 검증    │
       │                    - 발급자(issuer)    │
       │                      확인             │
       │                    - 서명 검증         │
       │                    - audience 확인    │
       │                    - 매핑된 SP 찾기    │
       │                                      │
       │ 5. Databricks access_token 발급       │
       │    (1시간, SP의 권한)                  │
       │◀──────────────────────────────────────│
       │                                      │
       │ 6. API 호출 (Bearer token)            │
       │──────────────────────────────────────▶│
```

### 핵심 구성 요소

| 구성 요소 | 설명 |
|----------|------|
| **Federation Policy** | 어떤 외부 IdP를 신뢰할지 정의 (issuer URL, audience) |
| **Service Principal Mapping** | 외부 토큰의 subject를 어떤 SP에 매핑할지 정의 |
| **OIDC Token** | 외부 IdP가 발급하는 JWT (JSON Web Token) |
| **Token Exchange** | 외부 OIDC 토큰을 Databricks access_token으로 교환하는 과정 |

---

### 지원 시나리오

Token Federation은 **OIDC를 지원하는 모든 외부 IdP** 와 연동할 수 있습니다.

아래 테이블은 주요 사용 사례와 외부 IdP를 보여줍니다.

| 시나리오 | 외부 IdP | OIDC Issuer 예시 |
|---------|---------|-----------------|
| **GitHub Actions** | GitHub OIDC Provider | `https://token.actions.githubusercontent.com` |
| **Azure DevOps** | Azure AD (Entra ID) | `https://login.microsoftonline.com/{tenant}/v2.0` |
| **AWS 워크로드** | AWS STS (OIDC) | `https://sts.amazonaws.com` |
| **GCP 워크로드** | Google OIDC | `https://accounts.google.com` |
| **Kubernetes** | K8s Service Account | 클러스터별 OIDC issuer URL |
| **GitLab CI** | GitLab OIDC | `https://gitlab.com` |

---

### GitHub Actions 연동 예시

GitHub Actions는 Token Federation의 가장 대표적인 사용 사례입니다.

#### 1단계: Service Principal 생성

Account Console에서 CI/CD용 SP를 생성하고, 필요한 권한을 부여합니다.

#### 2단계: Federation Policy 생성

Databricks Account Console 또는 API에서 Federation Policy를 구성합니다.

```json
{
  "name": "github-actions-federation",
  "issuer": "https://token.actions.githubusercontent.com",
  "audiences": ["https://accounts.cloud.databricks.com"],
  "subject_claim": "sub",
  "subject": "repo:MyOrg/MyRepo:ref:refs/heads/main"
}
```

| 필드 | 설명 |
|------|------|
| `issuer` | GitHub OIDC Provider의 URL |
| `audiences` | 토큰이 사용될 대상 (Databricks) |
| `subject_claim` | JWT에서 subject를 추출할 claim 이름 |
| `subject` | 허용할 subject 값 (특정 repo/branch로 제한) |

이 설정이 의미하는 바는 명확합니다: **MyOrg/MyRepo 리포지토리의 main 브랜치에서 실행되는 GitHub Actions 워크플로우만** 이 SP로 인증할 수 있습니다. 다른 리포지토리나 브랜치는 거부됩니다.

#### 3단계: GitHub Actions 워크플로우

```yaml
name: Deploy to Databricks

on:
  push:
    branches: [main]

permissions:
  id-token: write   # OIDC 토큰 발급 권한
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # GitHub OIDC 토큰 자동 발급
      - name: Get OIDC Token
        id: oidc
        uses: actions/github-script@v7
        with:
          script: |
            const token = await core.getIDToken('https://accounts.cloud.databricks.com');
            core.setOutput('token', token);

      # Databricks CLI 설치 및 인증
      - name: Setup Databricks CLI
        uses: databricks/setup-cli@main

      - name: Deploy
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN_FEDERATION: ${{ steps.oidc.outputs.token }}
        run: |
          databricks bundle deploy --target production
```

{% hint style="info" %}
**Secret이 전혀 없습니다**: 위 워크플로우에서 `DATABRICKS_HOST`는 URL(공개 정보)일 뿐이고, OIDC 토큰은 GitHub가 매 실행마다 자동 발급합니다. `client_secret`이나 PAT를 GitHub Secrets에 저장할 필요가 없습니다.
{% endhint %}

---

### Token Federation vs OAuth M2M 비교

두 방식 모두 Service Principal로 인증하지만, Secret 관리 방식에서 근본적인 차이가 있습니다.

| 항목 | OAuth M2M | Token Federation |
|------|-----------|-----------------|
| **인증 자격** | client_id + client_secret | 외부 OIDC 토큰 |
| **Secret 관리** | 필요 (생성, 저장, 로테이션) | 불필요 |
| **유출 위험** | client_secret 유출 가능 | 유출 가능한 자격 증명 없음 |
| **설정 복잡도** | 낮음 | 중간 (Federation Policy 설정) |
| **외부 IdP 의존** | 없음 | 있음 (IdP 장애 시 인증 불가) |
| **적용 범위** | 모든 자동화 환경 | OIDC 지원 환경만 |

이 비교에서 보듯, Token Federation은 보안 면에서 확실히 우수하지만, **외부 IdP에 대한 의존성** 이 추가됩니다. 외부 IdP가 OIDC를 지원하는 환경(GitHub Actions, Azure DevOps, AWS 등)이라면 Token Federation을, 그렇지 않은 환경이라면 OAuth M2M을 선택하세요.

---

### Token Federation의 한계

- **초기 설정 복잡도**: Federation Policy, SP Mapping 등 초기 구성이 OAuth M2M보다 복잡합니다. 하지만 한 번 설정하면 운영 부담이 거의 없습니다.
- **외부 IdP 의존**: GitHub, Azure AD 등 외부 서비스 장애 시 인증이 불가능합니다.
- **OIDC 필수**: 외부 시스템이 OIDC 토큰을 발급할 수 있어야 합니다. 모든 시스템이 이를 지원하지는 않습니다.
- **디버깅 어려움**: 인증 실패 시 외부 IdP 토큰의 claim 값, Federation Policy 매핑 등 확인할 요소가 많습니다.

---

## 인증 방법 최종 정리

아래 테이블은 네 가지 인증 방법의 선택 기준을 최종 정리합니다.

| 질문 | 답변 → 인증 방법 |
|------|----------------|
| 개발자가 로컬에서 작업하는가? | **OAuth U2M** |
| 자동화이고, 외부 IdP(GitHub 등)가 OIDC를 지원하는가? | **Token Federation** |
| 자동화이고, 외부 IdP가 없거나 OIDC 미지원인가? | **OAuth M2M** |
| 5분 안에 빠르게 API 테스트해야 하는가? | **PAT** (임시용) |

{% hint style="warning" %}
**프로덕션 환경에서 PAT는 사용하지 마세요.** PAT는 개발/테스트 단계의 임시 수단입니다. 프로덕션으로 전환할 때는 반드시 OAuth 기반 인증으로 교체하세요. 조직의 보안 감사(Audit)에서 PAT 사용은 거의 항상 지적 사항입니다.
{% endhint %}
