# 기존 Workspace에 PrivateLink 추가

## 개요

이미 운영 중인 Workspace에 PrivateLink를 사후 추가하는 절차입니다. 초기에 PrivateLink 없이 생성한 Workspace를 프라이빗 연결로 전환할 때 사용합니다.

{% hint style="warning" %}
**기존 Network Configuration은 직접 수정 불가**— VPC Endpoint를 포함한 새 Network Configuration을 생성한 후 Workspace에서 교체해야 합니다. 기존 Network Config을 편집하여 VPC Endpoint를 추가하는 것은 지원되지 않습니다.
{% endhint %}

## 전체 절차 요약 (7단계)

| 단계 | 작업 | 소요 시간 | 다운타임 |
|------|------|-----------|----------|
| Step 1 | AWS VPC Endpoint 생성 | ~5분 | 없음 |
| Step 2 | VPC Endpoint 상태 확인 | ~10분 | 없음 |
| Step 3 | Databricks에 VPC Endpoint 등록 | ~3분 | 없음 |
| Step 4 | 새 Network Configuration 생성 | ~3분 | 없음 |
| Step 5 | Private Access Settings 생성 | ~2분 | 없음 |
| Step 6 | Workspace 업데이트 | ~10-15분 | **있음** |
| Step 7 | DNS 검증 및 접속 확인 | ~10-20분 | 없음 |

{% hint style="danger" %}
**Step 6에서 다운타임 발생**: Workspace 업데이트 중 실행 중인 클러스터와 Job이 모두 중단됩니다. 반드시 유지보수 윈도우에 수행하세요.
{% endhint %}

## 다운타임 최소화 전략

- **사전 작업**: Step 1~5는 다운타임 없이 수행 가능 → 미리 준비
- **유지보수 윈도우**: Step 6만 유지보수 시간에 실행
- **사전 클러스터 종료**: Step 6 시작 전 모든 클러스터를 수동 종료하고 실행 중인 Job을 중지
- **알림**: 사용자에게 사전 공지 (예상 다운타임: 15-30분)

## Step 1: AWS VPC Endpoint 생성

AWS Console → **VPC**→ **Endpoints**→ **Create endpoint**

두 개의 VPC Endpoint를 생성합니다.

### 1-1. REST API Endpoint

| 필드 | 값 |
|------|-----|
| **Name tag** | `vpce-databricks-rest-api` |
| **Service category** | Other endpoint services |
| **Service name** | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e` |
| **VPC** | Databricks Workspace가 배포된 VPC |
| **Subnets** | Workspace가 사용하는 서브넷과 동일한 AZ의 서브넷 선택 |
| **Security groups** | Databricks SG 또는 443 인바운드 허용 SG |
| **Enable DNS name** | 체크하지 않음 (Private DNS는 수동 설정) |

{% hint style="info" %}
**Service name은 리전마다 다릅니다.** 위 예시는 `ap-northeast-2` (서울) 기준입니다. 다른 리전의 Service name은 [Databricks 공식 문서](https://docs.databricks.com/aws/en/security/network/classic/privatelink#step-2-create-aws-vpc-endpoints)에서 확인하세요.
{% endhint %}

### 1-2. SCC Relay Endpoint

| 필드 | 값 |
|------|-----|
| **Name tag** | `vpce-databricks-scc-relay` |
| **Service category** | Other endpoint services |
| **Service name** | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0dc0e98a5800db5c4` |
| **나머지 설정** | REST API Endpoint와 동일 |

"** Verify service**" 클릭 → "** Service name verified**" 메시지 확인 후 "** Create endpoint**" 클릭

## Step 2: VPC Endpoint 상태 확인

생성 직후 상태는 "** Pending**"입니다.

1. AWS Console → VPC → Endpoints
2. 두 VPC Endpoint의 상태가 "** Available**"로 변경될 때까지 대기 (통상 5-10분)
3. 각 Endpoint의 **VPC Endpoint ID**(`vpce-xxxxxxxxxxxxxxxxx`)를 메모

{% hint style="warning" %}
상태가 "** Failed**" 또는 "** Rejected**"인 경우:
- Service name이 올바른지 확인
- VPC의 리전과 Service name의 리전이 일치하는지 확인
- Security Group에서 TCP 443 인바운드가 허용되는지 확인
{% endhint %}

## Step 3: Databricks에 VPC Endpoint 등록

Account Console → **Security**→ **Networking**→ **VPC endpoints**

1. "** Register VPC endpoint**" 클릭
2. REST API Endpoint 등록:

| 필드 | 값 |
|------|-----|
| **Name** | `vpce-rest-api-apne2` |
| **Region** | `ap-northeast-2` |
| **AWS VPC endpoint ID** | Step 2에서 메모한 REST API VPC Endpoint ID |

3. "** Register**" 클릭
4. SCC Relay Endpoint도 동일하게 등록

| 필드 | 값 |
|------|-----|
| **Name** | `vpce-scc-relay-apne2` |
| **Region** | `ap-northeast-2` |
| **AWS VPC endpoint ID** | Step 2에서 메모한 SCC Relay VPC Endpoint ID |

5. 등록 후 상태가 "** Available**"인지 확인

## Step 4: 새 Network Configuration 생성

Account Console → **Security**→ **Networking**→ **Classic network configurations**

{% hint style="danger" %}
**기존 Network Configuration을 수정하지 마세요.** 반드시 새로 생성해야 합니다. 기존 것을 삭제하면 Workspace가 손상될 수 있습니다.
{% endhint %}

1. "** Add network configuration**" 클릭
2. 다음 정보 입력:

| 필드 | 값 | 설명 |
|------|-----|------|
| **Name** | `network-config-privatelink-apne2` | 식별 이름 |
| **VPC ID** | 기존 Workspace와 동일한 VPC ID | 변경 불가 |
| **Subnet IDs** | 기존 Workspace와 동일한 Subnet IDs | 변경 불가 |
| **Security Group IDs** | 기존 Workspace와 동일한 SG IDs | 변경 불가 |
| **REST API VPC Endpoint** | Step 3에서 등록한 REST API Endpoint 선택 | 신규 추가 |
| **Dataplane relay VPC Endpoint** | Step 3에서 등록한 SCC Relay Endpoint 선택 | 신규 추가 |

3. "** Add**" 클릭 → 새 Network Configuration ID 생성

{% hint style="warning" %}
VPC, Subnet, Security Group은 **기존 Workspace와 반드시 동일한 값** 을 입력해야 합니다. 다른 VPC로 변경하면 Workspace가 제대로 작동하지 않습니다.
{% endhint %}

## Step 5: Private Access Settings 생성

Account Console → **Security**→ **Networking**→ **Private access settings**

1. "** Add private access settings**" 클릭
2. 다음 정보 입력:

| 필드 | 값 | 설명 |
|------|-----|------|
| **Name** | `pas-apne2` | 식별 이름 |
| **Region** | `ap-northeast-2` | Workspace 리전 |
| **Public access** | **Enabled** | 초기에는 Enabled 권장 |
| **Private access level** | **Any** | VPC Endpoint에서의 접근 허용 수준 |

{% hint style="info" %}
**초기에는 Public access를 Enabled로 설정하세요.** PrivateLink 연결이 완전히 검증된 후 Disabled로 변경합니다. 처음부터 Disabled로 설정하면 DNS 전파가 완료되기 전에 접근이 차단되어 트러블슈팅이 어려워집니다.
{% endhint %}

## Step 6: Workspace 업데이트

{% hint style="danger" %}
**이 단계에서 다운타임이 발생합니다.** 사전에 다음을 수행하세요:
- 모든 Interactive 클러스터 종료
- 실행 중인 Job 중지 또는 완료 대기
- 사용자에게 사전 공지
{% endhint %}

Account Console → **Workspaces**→ 대상 Workspace 선택

1. "** Update**" 클릭
2. **Network configuration**→ Step 4에서 생성한 새 Network Configuration 선택
3. **Private access settings**→ Step 5에서 생성한 설정 선택
4. "** Confirm update**" 클릭
5. 프로비저닝 시작 (~10-15분 소요)
6. 상태가 "** Running**"으로 변경될 때까지 대기

{% hint style="warning" %}
**업데이트 중 Workspace 상태가 "Provisioning"으로 표시됩니다.** 이 동안 Workspace에 접근할 수 없으며, 실행 중이던 모든 클러스터와 작업이 중단됩니다.
{% endhint %}

## Step 7: DNS 검증 및 접속 확인

업데이트 완료 후 PrivateLink DNS 전파까지 추가로 10-20분이 소요될 수 있습니다.

### DNS 확인 방법

VPC 내부 또는 VPN 연결된 환경에서 실행:

```bash
# Workspace URL 확인
nslookup <workspace-url>.cloud.databricks.com

# 기대 결과 (Private IP 반환):
# Address: 10.x.x.x

# 잘못된 결과 (Public IP 반환):
# Address: 52.x.x.x → DNS 전파 미완료 또는 설정 오류
```

```bash
# REST API Endpoint 확인
nslookup <workspace-url>.cloud.databricks.com

# SCC Relay Endpoint 확인
nslookup tunnel.<workspace-url>.cloud.databricks.com
```

### 접속 검증

1. VPN 또는 VPC 내부 환경에서 Workspace URL로 브라우저 접속
2. 로그인 성공 확인
3. 클러스터 시작 → 노트북에서 간단한 명령 실행 (`spark.range(10).show()`)
4. SQL Warehouse 시작 → 쿼리 실행 확인

{% hint style="info" %}
DNS 전파가 완료되지 않은 상태에서는 Public access가 Enabled이므로 기존 경로(인터넷)로 접속됩니다. `nslookup`에서 Private IP가 반환되는 것을 확인한 후 Step 8로 진행하세요.
{% endhint %}

## Step 8 (선택): Public Access 비활성화

PrivateLink 접속이 완전히 검증된 후:

1. Account Console → Workspaces → 대상 Workspace → "** Update**"
2. Private Access Settings의 **Public access**→ **Disabled** 변경
3. "** Confirm update**" 클릭

{% hint style="danger" %}
**Public access를 Disabled로 변경하면 인터넷을 통한 Workspace 접근이 완전히 차단됩니다.** VPN/DirectConnect를 통해 VPC에 연결되지 않은 사용자는 접속할 수 없게 됩니다. 반드시 모든 사용자의 접속 환경을 확인한 후 변경하세요.
{% endhint %}

## 롤백 방법

PrivateLink 전환 후 문제가 발생한 경우:

1. Account Console → Workspaces → 대상 Workspace → "** Update**"
2. **Network configuration**→ **기존** Network Configuration (PrivateLink 없는 버전)으로 되돌림
3. **Private access settings**→ 제거 또는 Public access: Enabled로 변경
4. "** Confirm update**" 클릭
5. 다시 프로비저닝 (~10-15분 소요, 추가 다운타임 발생)

{% hint style="warning" %}
롤백 시에도 다운타임이 발생합니다. 따라서 최초 전환 전에 충분한 테스트를 수행하는 것이 중요합니다. Non-production Workspace에서 먼저 테스트하는 것을 강력히 권장합니다.
{% endhint %}

## Troubleshooting

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| nslookup에서 Public IP 반환 | DNS 전파 미완료 | 20분 대기 후 재확인, VPC DNS 설정 확인 |
| Workspace 접속 불가 (timeout) | Security Group에서 443 차단 | VPC Endpoint에 연결된 SG의 인바운드 규칙 확인 |
| 클러스터 시작 실패 | SCC Relay Endpoint 미설정 또는 오류 | SCC Relay VPC Endpoint 상태 확인 |
| "UPDATE_FAILED" 상태 | Network Config 정보 불일치 | VPC, Subnet, SG가 기존과 동일한지 확인 |
| Public access Disabled 후 접속 불가 | PrivateLink 경로 미확보 | Public access를 다시 Enabled로 변경 후 원인 파악 |

*참고: [Update a workspace](https://docs.databricks.com/aws/en/admin/account-settings-e2/workspaces) · [PrivateLink](https://docs.databricks.com/aws/en/security/network/classic/privatelink)*
