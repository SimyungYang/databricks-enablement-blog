# Backend PrivateLink

## PrivateLink 개요 — Backend vs Frontend 비교

| 항목 | Backend (Classic) — 필수 권장 | Frontend (Inbound) — 옵션 |
|------|------|------|
| **방향** | Compute → Control Plane | 사용자 → Workspace |
| **용도** | 클러스터가 API/Relay에 접근 | Web UI, REST API, DB Connect |
| **VPC Endpoint** | **2개**(REST API + SCC Relay) | **1개**(REST API만) |
| **배치 위치** | Compute VPC | Transit VPC (또는 동일 VPC) |
| **DNS 추가 구성** | 불필요 (private DNS enabled) | Route 53 Private Hosted Zone 필요 |
| **핵심 이점** | 인터넷 없이 클러스터 운영 | End-to-End 프라이빗 접근 |

{% hint style="warning" %}
**Enterprise 티어 필수**— Customer-Managed VPC + SCC 활성화 필요
{% endhint %}

*참고: [PrivateLink Concepts](https://docs.databricks.com/aws/en/security/network/classic/privatelink-concepts) · [Enable PrivateLink](https://docs.databricks.com/aws/en/security/network/classic/privatelink)*

## ap-northeast-2 (서울) VPC Endpoint Service Names

이 값으로 AWS VPC Endpoint를 생성합니다.

### Workspace (REST API) Endpoint

```
com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e
```

### SCC Relay Endpoint

```
com.amazonaws.vpce.ap-northeast-2.vpce-svc-0dc0e98a5800db5c4
```

{% hint style="info" %}
AWS Console → VPC → Endpoints → "**Find service by name**" 에 위 값을 붙여넣기 → **Verify service** 클릭
{% endhint %}

*출처: [Databricks regional endpoint service names](https://docs.databricks.com/aws/en/resources/ip-domain-region) · [Terraform: databricks_mws_vpc_endpoint](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_vpc_endpoint)*

## 전체 리전 VPC Endpoint Service Names

모든 리전 복사용 참조표:

| Region | Workspace (REST API) | SCC Relay |
|--------|---------------------|-----------|
| **ap-northeast-2** | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e` | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0dc0e98a5800db5c4` |
| ap-northeast-1 | `com.amazonaws.vpce.ap-northeast-1.vpce-svc-02691fd610d24fd64` | `com.amazonaws.vpce.ap-northeast-1.vpce-svc-02aa633bda3edbec0` |
| us-east-1 | `com.amazonaws.vpce.us-east-1.vpce-svc-09143d1e626de2f04` | `com.amazonaws.vpce.us-east-1.vpce-svc-00018a8c3ff62ffdf` |
| us-east-2 | `com.amazonaws.vpce.us-east-2.vpce-svc-041dc2b4d7796b8d3` | `com.amazonaws.vpce.us-east-2.vpce-svc-090a8fab0d73e39a6` |
| us-west-2 | `com.amazonaws.vpce.us-west-2.vpce-svc-0129f463fcfbc46c5` | `com.amazonaws.vpce.us-west-2.vpce-svc-0158114c0c730c3bb` |
| eu-central-1 | `com.amazonaws.vpce.eu-central-1.vpce-svc-081f78503812597f7` | `com.amazonaws.vpce.eu-central-1.vpce-svc-08e5dfca9572c85c4` |
| eu-west-1 | `com.amazonaws.vpce.eu-west-1.vpce-svc-0da6ebf1461278016` | `com.amazonaws.vpce.eu-west-1.vpce-svc-09b4eb2bc775f4e8c` |
| ap-southeast-1 | `com.amazonaws.vpce.ap-southeast-1.vpce-svc-02535b257fc253ff4` | `com.amazonaws.vpce.ap-southeast-1.vpce-svc-0557367c6fc1a0c5c` |

*전체 리전: [IP addresses and domains](https://docs.databricks.com/aws/en/resources/ip-domain-region)*

## Step 1: VPC Endpoint Subnet 생성

AWS Console → VPC → Subnets → Create subnet

### 요구사항

| 항목 | 설정값 |
|------|--------|
| **VPC** | Databricks Compute VPC |
| **CIDR** | 최소 `/27` (예: `10.4.100.0/24`) |
| **용도** | VPC Endpoint 전용 (워크스페이스 서브넷과 분리) |

### Route Table 설정

- **새 Route Table 생성**→ VPC Endpoint Subnet에 연결
- **Local route만** 유지 — NAT GW route 추가하지 않음

| Destination | Target |
|-------------|--------|
| `10.4.0.0/16` (VPC CIDR) | local |

{% hint style="warning" %}
VPC Endpoint Subnet에는 NAT Gateway 라우트를 넣지 않음 — local 전용
{% endhint %}

## Step 2: VPC Endpoint Security Group

AWS Console → VPC → Security Groups → Create

규칙 — 양방향 TCP 포트 443, 2443, 6666:

**Inbound Rules:**

| Port | Protocol | Source | 용도 |
|------|----------|--------|------|
| **443** | TCP | VPC CIDR (예: `10.4.0.0/16`) | REST API (HTTPS) |
| **2443** | TCP | VPC CIDR | FIPS / Compliance |
| **6666** | TCP | VPC CIDR | SCC Relay |

**Outbound Rules:**

| Port | Protocol | Destination | 용도 |
|------|----------|-------------|------|
| **443** | TCP | VPC CIDR | REST API return |
| **2443** | TCP | VPC CIDR | FIPS return |
| **6666** | TCP | VPC CIDR | Relay return |

*참고: [PrivateLink security group requirements](https://docs.databricks.com/aws/en/security/network/classic/privatelink)*

## Step 3: AWS VPC Endpoint 생성

AWS Console → VPC → Endpoints → Create endpoint (x2)

### Endpoint 1: Workspace (REST API)

| 항목 | 설정값 |
|------|--------|
| **Service category** | Other endpoint services |
| **Service name** | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e` |
| **VPC** | Compute VPC |
| **Subnets** | VPC Endpoint Subnet |
| **Security groups** | VPC Endpoint SG (443/2443/6666) |
| **Enable DNS name** | **Yes**(Enable private DNS names) |

### Endpoint 2: SCC Relay

| 항목 | 설정값 |
|------|--------|
| **Service name** | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0dc0e98a5800db5c4` |
| 나머지 | Workspace Endpoint와 동일 설정 |

{% hint style="info" %}
"Verify service" 클릭 시 "**Service name verified**" 확인 후 진행. `private_dns_enabled = true` 필수
{% endhint %}

## Step 4: Databricks에 VPC Endpoint 등록

Account Console → Security → Networking → VPC endpoints

### 절차 (2회 반복 — REST API, Relay 각각)

1. **Security**→ **Networking**→ **VPC endpoints**→ **Register VPC endpoint**
2. 입력:
   - **VPC endpoint name**: 식별 이름 (예: `prod-rest-vpce`, `prod-relay-vpce`)
   - **VPC endpoint ID**: `vpce-xxxxxxxx` (AWS에서 생성한 ID)
   - **Region**: `ap-northeast-2`
3. **Register** 클릭

### 이후: Network Configuration 생성 시 연결

- VPC Endpoint 등록 완료 후 → **Network 등록 단계** 에서 Network Configuration 생성 시 VPC Endpoint를 지정
- Network Configuration 생성 화면에서 REST API / Dataplane relay Endpoint 선택

*참고: [Register VPC endpoints](https://docs.databricks.com/aws/en/security/network/classic/privatelink)*

## Step 5: Private Access Settings

Account Console → Security → Networking → Private access settings

### 설정

1. **Add private access settings** 클릭
2. 입력:
   - **Name**: 식별 이름
   - **Region**: `ap-northeast-2`
   - **Public access**: 단계적 전환 권장

### 접근 수준 옵션

| 설정 | Public access | Access level | 결과 |
|------|---|---|---|
| **하이브리드**(검증 기간) | Enabled | ACCOUNT | 퍼블릭 + PrivateLink 모두 허용 |
| **프라이빗 전용** | Disabled | ACCOUNT | 계정 내 모든 VPC Endpoint 허용 |
| **특정 Endpoint만** | Disabled | ENDPOINT | 지정된 Endpoint만 허용 |

{% hint style="warning" %}
처음에는 **Public access = Enabled** 로 시작 → 검증 완료 후 **Disabled** 로 전환 권장
{% endhint %}

*참고: [Private access settings](https://docs.databricks.com/aws/en/security/network/classic/privatelink) · [Terraform: databricks_mws_private_access_settings](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_private_access_settings)*
