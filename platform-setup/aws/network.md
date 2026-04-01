# Network 구성

## VPC 생성 — 요구사항

AWS Console → VPC → Create VPC

| 항목 | 설정값 |
|------|--------|
| **CIDR**| `/16` ~ `/17` 권장 (예: `10.4.0.0/16`) |
| **DNS hostnames**| **Enabled**|
| **DNS resolution**| **Enabled**|
| **예약 CIDR (충돌 회피)**| `127.187.216.0/24`, `192.168.216.0/24`, `198.18.216.0/24`, `172.17.0.0/16` |

### Subnet 구성

| Subnet | 수량 | 용도 | 비고 |
|--------|------|------|------|
| **Private**| 2개+ | Databricks 클러스터 | 서로 다른 AZ, netmask `/17`~`/25` |
| **Public**| 1개 | NAT GW + IGW | 아웃바운드 인터넷 |
| **VPC Endpoint**| 1개 | PrivateLink 전용 | local route만, NAT 없음 |

*참고: [Configure customer-managed VPC](https://docs.databricks.com/aws/en/admin/account-settings-e2/networks)*

## Security Group — 필수 규칙

AWS Console → VPC → Security Groups → Create security group

### Egress (아웃바운드) 규칙

| Port | Protocol | Destination | 용도 |
|------|----------|-------------|------|
| All | TCP/UDP | Self (동일 SG) | 클러스터 내부 통신 |
| 443 | TCP | 0.0.0.0/0 | Control Plane, 외부 라이브러리 |
| 3306 | TCP | 0.0.0.0/0 | Legacy Hive Metastore |
| 6666 | TCP | 0.0.0.0/0 | SCC Relay 통신 |
| 8443-8451 | TCP | 0.0.0.0/0 | Compute → Control Plane API |
| 2443 | TCP | 0.0.0.0/0 | FIPS (Compliance Security Profile) |

### Ingress (인바운드) 규칙

| Port | Protocol | Source | 용도 |
|------|----------|--------|------|
| All TCP | TCP | Self (동일 SG) | 노드 간 통신 |
| All UDP | UDP | Self (동일 SG) | 노드 간 통신 |

*참고: [Security group rules](https://docs.databricks.com/aws/en/admin/account-settings-e2/networks)*

## NACL (Network ACL) 설정

AWS Console → VPC → Network ACLs

Security Group과 별도로 서브넷 레벨에서 트래픽을 제어하는 Network ACL을 설정합니다.

### Inbound Rules

| Rule # | Type | Protocol | Port | Source | Action |
|--------|------|----------|------|--------|--------|
| 100 | All traffic | All | All | 0.0.0.0/0 | ALLOW |

### Outbound Rules

| Rule # | Type | Protocol | Port | Destination | Action |
|--------|------|----------|------|-------------|--------|
| 100 | All traffic | All | All | VPC CIDR | ALLOW |
| 110 | HTTPS | TCP | 443 | 0.0.0.0/0 | ALLOW |
| 120 | Custom TCP | TCP | 3306 | 0.0.0.0/0 | ALLOW |
| 130 | Custom TCP | TCP | 6666 | 0.0.0.0/0 | ALLOW |
| 140 | Custom TCP | TCP | 8443-8451 | 0.0.0.0/0 | ALLOW |
| 150 | Custom TCP | TCP | 2443 | 0.0.0.0/0 | ALLOW |

{% hint style="warning" %}
**NACL은 stateless**— Security Group과 달리 인바운드/아웃바운드 규칙을 모두 명시적으로 설정해야 합니다. 응답 트래픽도 자동 허용되지 않으므로 양방향 규칙이 필수입니다.
{% endhint %}

*참고: [Network configuration](https://docs.databricks.com/aws/en/admin/account-settings-e2/networks)*

## 권장 AWS Service VPC Endpoints

AWS Console → VPC → Endpoints → Create endpoint

| Service | Type | Service Name | Private DNS | 용도 |
|---------|------|-------------|-------------|------|
| **S3**| Gateway | `com.amazonaws.ap-northeast-2.s3` | N/A | DBFS, Delta Lake |
| **STS**| Interface | `com.amazonaws.ap-northeast-2.sts` | Enabled | IAM 인증 |
| **Kinesis**| Interface | `com.amazonaws.ap-northeast-2.kinesis-streams` | Enabled | 로그 전송 |

- **S3 Gateway**: Route Table에 연결 (Private Subnet의 Route Table)
- **STS/Kinesis Interface**: Private Subnet에 배치, Security Group 필요 (443 inbound)

## Network 등록 — 사전 조건

Security → Networking → Classic network configurations

{% hint style="warning" %}
**순서 주의**: Network Configuration 생성 시 **VPC Endpoint를 지정**해야 함 → **Backend PrivateLink의 VPC Endpoint 등록을 먼저 완료** 후 진행
{% endhint %}

### 입력 항목 요약

| 항목 | 값 |
|------|---|
| **Network configuration name**| 식별 이름 |
| **VPC ID**| `vpc-xxxxxxxx` |
| **Subnet IDs**| Private Subnet 2개 (서로 다른 AZ) |
| **Security Group IDs**| SG ID (최대 5개) |
| **VPC Endpoints — REST API**| 등록된 Workspace Endpoint 선택 |
| **VPC Endpoints — Dataplane relay**| 등록된 SCC Relay Endpoint 선택 |

## Network 등록 — 절차

Security → Networking → Classic network configurations

1. **Add network configuration** 클릭
2. 이전 항목 입력 + VPC Endpoints 지정
3. **Add**→ **Network ID** 생성됨 → Workspace 생성 시 사용

{% hint style="info" %}
Network configuration은 **수정 불가**— 변경 시 새로 생성 후 Workspace에서 교체 (3단계 프로세스)
{% endhint %}
