# OAuth M2M (서비스 인증)

## 개요

OAuth M2M(Machine-to-Machine)은 **Service Principal이 client_id와 client_secret으로 직접 인증** 하는 방식입니다. 사람의 개입 없이 완전 자동화된 환경에서 사용하며, CI/CD 파이프라인, 스케줄 Job, IaC(Infrastructure as Code), 외부 시스템 연동에 최적화되어 있습니다.

---

## Service Principal이란

Service Principal(SP)은 **자동화 전용 ID** 입니다. 사용자 계정과 달리 이메일, 비밀번호, MFA가 없으며, 오직 API 호출을 위해서만 존재합니다.

### 왜 Service Principal이 필요한가

다음 시나리오를 생각해 보세요.

> 팀에서 김철수 개발자의 PAT로 프로덕션 Job을 스케줄링하고 있었습니다. 김철수가 퇴사하자 PAT가 비활성화되고, 프로덕션 파이프라인이 즉시 중단되었습니다. 복구에 2시간이 걸렸고, 그 사이 SLA를 위반했습니다.

이 문제의 근본 원인은 **자동화 워크로드가 개인 계정에 의존** 했기 때문입니다.

| 개인 계정 사용 시 문제 | Service Principal의 해결 |
|-----------------------|------------------------|
| 직원 퇴사 → 자동화 중단 | SP는 사람과 독립적, 퇴사 영향 없음 |
| 과도한 권한 (개인 계정의 전체 권한) | SP에 최소 필요 권한만 부여 |
| 감사 로그에 "김철수" → 사람 vs 자동화 구분 불가 | "cicd-deployer" 등 명확한 식별 |
| 토큰 공유 → 누가 사용했는지 추적 불가 | SP별 독립 인증, 완전한 추적 |

{% hint style="info" %}
**핵심 원칙**: 자동화 워크로드에는 반드시 Service Principal을 사용하세요. **"사람 = 사용자 계정, 시스템 = Service Principal"** 이 기본 규칙입니다.
{% endhint %}

### Service Principal 역할

SP에는 다음과 같은 역할을 부여할 수 있습니다.

| 역할 | 설명 | 부여 위치 |
|------|------|----------|
| **Account Admin** | 전체 Account 관리 (최소한으로 사용) | Account Console |
| **Workspace Admin** | 특정 워크스페이스 관리 | Workspace Settings |
| **SP Manager** | 다른 SP를 관리할 수 있는 권한 | Account Console |
| **SP User** | SP를 사용할 수 있는 권한 (Job 실행 등) | Account Console |

### System Service Principal

Databricks는 내부 기능(Predictive Optimization, Lakehouse Monitoring 등)을 위해 **System SP** 를 자동 생성합니다. 이 SP들은 사용자가 관리할 수 없으며, Databricks가 직접 관리합니다. 감사 로그에서 `System-` 접두사로 식별할 수 있습니다.

---

## OAuth Secret 생성

### Account Console에서 생성

1. **Account Console** > **Service principals** 이동
2. 대상 SP 선택
3. **OAuth secrets** 탭 > **Generate secret** 클릭
4. `client_id`와 `client_secret`이 표시됨

{% hint style="warning" %}
**중요**: `client_secret`은 생성 시 **한 번만** 표시됩니다. 이 값을 안전한 곳(Vault, 환경변수)에 즉시 저장하세요. 분실하면 새 Secret을 생성해야 합니다.
{% endhint %}

### Secret 제한사항

| 항목 | 제한 |
|------|------|
| SP당 최대 Secret 수 | **5개** |
| Secret 최대 유효 기간 | **2년** |
| Secret 최소 유효 기간 | 없음 (즉시 유효) |

하나의 SP에 최대 5개의 Secret을 동시에 가질 수 있으므로, **Secret 로테이션** 시 새 Secret을 먼저 생성하고, 이전 Secret은 전환 완료 후 삭제하는 전략이 가능합니다.

### Databricks CLI로 생성

```bash
# SP의 OAuth Secret 생성
databricks service-principals secrets create \
  --service-principal-id <sp-id> \
  --profile ACCOUNT

# 출력 예시
# {
#   "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
#   "secret": "dose1234567890abcdef...",
#   "status": "ACTIVE",
#   "create_time": "2026-04-08T10:00:00.000Z",
#   "expire_time": "2028-04-08T10:00:00.000Z"
# }
```

---

## 토큰 교환 흐름

OAuth M2M은 **OAuth 2.0 Client Credentials Grant** 를 사용합니다. 브라우저 인증 없이, client_id와 client_secret만으로 직접 토큰을 발급받습니다.

```
Service Principal       Databricks 인증서버
       │                        │
       │  1. 토큰 요청            │
       │  (client_id +           │
       │   client_secret +       │
       │   grant_type=           │
       │   client_credentials)   │
       │───────────────────────▶│
       │                        │
       │                        │ 2. 자격 증명 검증
       │                        │    Secret 유효성 확인
       │                        │    SP 상태 확인 (Active?)
       │                        │
       │  3. access_token 발급   │
       │  (1시간 유효)            │
       │◀───────────────────────│
       │                        │
       │  4. API 호출            │
       │  (Authorization:        │
       │   Bearer <token>)       │
       │───────────────────────▶│ Databricks API
```

---

## Account vs Workspace 레벨

OAuth M2M은 **Account 레벨** 과 **Workspace 레벨** 두 가지 엔드포인트를 지원합니다.

| 레벨 | 토큰 엔드포인트 | 용도 |
|------|----------------|------|
| **Account** | `https://accounts.cloud.databricks.com/oidc/accounts/{account-id}/v1/token` | 워크스페이스 생성, Account 관리, 멀티 워크스페이스 작업 |
| **Workspace** | `https://{workspace-host}/oidc/v1/token` | 특정 워크스페이스 내 API 호출 |

**어떤 레벨을 사용해야 하는가**: 대부분의 자동화 작업(Job 실행, 데이터 접근, 모델 배포)은 **Workspace 레벨** 로 충분합니다. Account 레벨은 Terraform으로 워크스페이스를 프로비저닝하거나, 여러 워크스페이스에 걸쳐 작업할 때만 사용합니다.

---

## 코드 예시

### curl로 토큰 발급

```bash
# Workspace 레벨 토큰 발급
curl -X POST "https://<workspace-host>/oidc/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=<client-id>" \
  -d "client_secret=<client-secret>" \
  -d "scope=all-apis"

# 응답 예시
# {
#   "access_token": "eyJhbGciOiJSUzI1NiIs...",
#   "token_type": "Bearer",
#   "expires_in": 3600
# }
```

```bash
# Account 레벨 토큰 발급
curl -X POST "https://accounts.cloud.databricks.com/oidc/accounts/<account-id>/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=<client-id>" \
  -d "client_secret=<client-secret>" \
  -d "scope=all-apis"
```

### Python SDK

```python
from databricks.sdk import WorkspaceClient

# 환경변수 사용 (권장)
# DATABRICKS_HOST, DATABRICKS_CLIENT_ID, DATABRICKS_CLIENT_SECRET 설정 필요
w = WorkspaceClient()

# 또는 직접 지정
w = WorkspaceClient(
    host="https://<workspace-host>",
    client_id="<client-id>",
    client_secret="<client-secret>"
)

# Job 실행
run = w.jobs.run_now(job_id=12345)
print(f"Run ID: {run.run_id}")
```

```python
from databricks.sdk import AccountClient

# Account 레벨 클라이언트
a = AccountClient(
    host="https://accounts.cloud.databricks.com",
    account_id="<account-id>",
    client_id="<client-id>",
    client_secret="<client-secret>"
)

# 워크스페이스 목록
for ws in a.workspaces.list():
    print(f"{ws.workspace_name} ({ws.deployment_name})")
```

### Java SDK

```java
import com.databricks.sdk.WorkspaceClient;
import com.databricks.sdk.core.DatabricksConfig;

DatabricksConfig config = new DatabricksConfig()
    .setHost("https://<workspace-host>")
    .setClientId("<client-id>")
    .setClientSecret("<client-secret>");

WorkspaceClient w = new WorkspaceClient(config);

// 클러스터 목록
w.clusters().list().forEach(cluster ->
    System.out.println(cluster.getClusterName() + ": " + cluster.getState())
);
```

### Go SDK

```go
package main

import (
    "context"
    "fmt"
    "github.com/databricks/databricks-sdk-go"
    "github.com/databricks/databricks-sdk-go/service/compute"
)

func main() {
    w := databricks.Must(databricks.NewWorkspaceClient(&databricks.Config{
        Host:         "https://<workspace-host>",
        ClientID:     "<client-id>",
        ClientSecret: "<client-secret>",
    }))

    clusters, err := w.Clusters.ListAll(context.Background(),
        compute.ListClustersRequest{})
    if err != nil {
        panic(err)
    }
    for _, c := range clusters {
        fmt.Printf("%s: %s\n", c.ClusterName, c.State)
    }
}
```

### .databrickscfg 프로파일

```ini
# ~/.databrickscfg

[CICD]
host          = https://<workspace-host>
client_id     = <client-id>
client_secret = <client-secret>
```

```bash
# 프로파일로 CLI 사용
databricks clusters list --profile CICD
```

{% hint style="warning" %}
**보안 주의**: `.databrickscfg`에 `client_secret`을 직접 저장하는 것은 개발 환경에서만 사용하세요. 프로덕션 환경에서는 반드시 **환경변수** 또는 **Secret Manager** (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)를 사용하세요.
{% endhint %}

---

## 보안 모범 사례

### 1. Secret 수명 최소화

```
[권장] Secret 유효 기간: 90일 ~ 180일
[주의] Secret 유효 기간: 1년 이상
[금지] Secret 유효 기간: 2년 (최대값)
```

짧은 수명의 Secret을 주기적으로 로테이션하면, 유출 시 피해 범위를 최소화할 수 있습니다.

### 2. Secret 로테이션 전략

SP당 최대 5개의 Secret을 동시에 보유할 수 있으므로, **무중단 로테이션** 이 가능합니다.

```
1. 새 Secret 생성 (Secret #2)
2. 모든 시스템에 Secret #2 배포
3. Secret #2로 정상 동작 확인
4. 이전 Secret #1 삭제
```

### 3. 환경변수 저장

```bash
# CI/CD 환경에서 환경변수로 전달
export DATABRICKS_HOST="https://<workspace-host>"
export DATABRICKS_CLIENT_ID="<client-id>"
export DATABRICKS_CLIENT_SECRET="<client-secret>"
```

### 4. 최소 권한 원칙

SP에는 해당 자동화 작업에 필요한 **최소한의 권한** 만 부여하세요.

| 작업 | 필요 권한 |
|------|----------|
| Job 실행 | `CAN_MANAGE_RUN` on Job |
| 테이블 읽기 | `SELECT` on Table (Unity Catalog) |
| 모델 배포 | `CAN_MANAGE` on Model Serving Endpoint |
| 워크스페이스 관리 | Workspace Admin (최소한으로 사용) |

### 5. Vault 연동

프로덕션 환경에서는 Secret을 코드나 설정 파일에 저장하지 않고, Secret Manager에서 런타임에 가져오는 것을 권장합니다.

```python
import boto3
import json
from databricks.sdk import WorkspaceClient

# AWS Secrets Manager에서 Secret 가져오기
sm = boto3.client("secretsmanager")
secret = json.loads(
    sm.get_secret_value(SecretId="databricks/cicd-sp")["SecretString"]
)

w = WorkspaceClient(
    host=secret["host"],
    client_id=secret["client_id"],
    client_secret=secret["client_secret"]
)
```

---

## 트러블슈팅

### 401 Unauthorized

```json
{
  "error": "invalid_client",
  "error_description": "Client authentication failed"
}
```

**원인과 해결**:

| 가능한 원인 | 확인 방법 | 해결 |
|------------|----------|------|
| client_id 오류 | Account Console에서 SP 확인 | 정확한 client_id 복사 |
| client_secret 만료 | SP > OAuth secrets에서 확인 | 새 Secret 생성 |
| SP 비활성화 | SP 상태가 Active인지 확인 | SP 활성화 |
| 잘못된 엔드포인트 | Account vs Workspace URL 확인 | 올바른 URL 사용 |

### 403 Forbidden

```json
{
  "error_code": "PERMISSION_DENIED",
  "message": "User does not have permission..."
}
```

**원인**: 인증은 성공했지만 **권한이 부족** 합니다.

- SP에 필요한 Unity Catalog 권한 부여: `GRANT SELECT ON TABLE ... TO <sp-name>`
- 워크스페이스에 SP 추가 확인: Account Console > Workspace > Service Principals
- 리소스(Job, Cluster 등)에 대한 ACL 확인

### 토큰 만료 후 자동 갱신

OAuth M2M에서 `access_token`은 1시간 후 만료됩니다. Databricks SDK는 토큰 만료 시 **자동으로 client_credentials 요청을 다시 보내** 새 토큰을 발급받습니다. curl이나 직접 HTTP 호출을 사용하는 경우에는 이 로직을 직접 구현해야 합니다.

```python
# SDK 사용 시 — 자동 갱신, 별도 처리 불필요
w = WorkspaceClient(
    host="https://<workspace-host>",
    client_id="<client-id>",
    client_secret="<client-secret>"
)

# 1시간 이상 실행되는 작업도 문제없음
# SDK가 토큰 만료 감지 → 자동 재발급
for table in w.tables.list(catalog_name="main", schema_name="default"):
    process(table)  # 오래 걸려도 OK
```

---

## 한계와 주의사항

- **Secret 관리 부담**: client_secret을 안전하게 저장, 로테이션, 배포해야 합니다. 이 부담을 제거하려면 **Token Federation** 을 검토하세요.
- **SP당 Secret 5개 제한**: 대규모 환경에서 빈번한 로테이션 시 제한에 걸릴 수 있으므로, 로테이션 주기를 적절히 설정하세요.
- **Secret 최대 2년**: 보안 정책상 더 긴 수명이 필요한 경우 대안이 없으므로, 자동 로테이션 파이프라인을 구축해야 합니다.
- **네트워크 의존**: 토큰 발급 시 Databricks 인증 서버에 접근해야 하므로, PrivateLink 환경에서는 별도의 네트워크 경로가 필요할 수 있습니다.
