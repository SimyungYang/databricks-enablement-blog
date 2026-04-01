# Frontend PrivateLink

## Frontend PrivateLink — 왜 필요한가?

사용자 → Workspace 접근을 프라이빗하게 만듭니다.

| 구성 | 사용자 접근 경로 |
|------|---------------|
| **Backend만**| 사용자 → **인터넷**→ Workspace → PrivateLink → Compute |
| **Backend + Frontend**| 사용자 → **VPN/DX**→ Transit VPC → **PrivateLink**→ Workspace → PrivateLink → Compute |

{% hint style="info" %}
**적용 시점**: VPN/DirectConnect로 AWS에 접근하는 고객, 퍼블릭 인터넷 접근 정책상 불가한 환경. End-to-End 프라이빗 연결 — 인터넷 경유 Zero
{% endhint %}

*참고: [Inbound PrivateLink](https://docs.databricks.com/aws/en/security/network/front-end/front-end-private-connect) · [PrivateLink DNS](https://docs.databricks.com/aws/en/security/network/classic/privatelink-dns)*

## Frontend — Backend과의 차이점

| 항목 | Backend | Frontend (추가분) |
|------|---------|-----------------|
| **VPC**| Compute VPC | **Transit VPC**(별도 또는 동일) |
| **VPC Endpoint**| 2개 (REST + Relay) | **1개**(REST API만) |
| **SG 포트**| 443, 2443, 6666 | **443만**|
| **DNS**| private DNS enabled | **Route 53 Private Hosted Zone**|
| **추가**| 없음 | **Route 53 Inbound Resolver**(On-prem) |

### Single VPC vs Dual VPC

| 방식 | 설명 | 적합 시나리오 |
|------|------|-------------|
| **Single VPC**| Compute VPC에 Frontend도 배치, REST API Endpoint 겸용 | PoC, 소규모 |
| **Dual VPC**(권장) | Transit VPC(Frontend) + Compute VPC(Backend) 분리 | 프로덕션, 대규모 |

## Step 1: Transit VPC 생성

### Transit VPC + Security Group

| 항목 | 설정값 |
|------|--------|
| **CIDR**| 예: `10.5.0.0/16` |
| **DNS hostnames / resolution**| 둘 다 **Enabled**|
| **Security Group Inbound**| TCP 443 from Corporate CIDR (예: `10.0.0.0/8`) |
| **Security Group Outbound**| TCP 443 to Corporate CIDR |

## Step 1b: VPC Endpoint 생성

AWS Console → VPC → Endpoints → Create endpoint

| 항목 | 설정값 |
|------|--------|
| **Service name**| `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e` |
| **VPC**| Transit VPC |
| **Subnet**| Transit Endpoint Subnet |
| **Enable private DNS names**| **No**(Route 53으로 관리) |

{% hint style="warning" %}
Frontend Endpoint는 반드시 **Enable private DNS names = No**
{% endhint %}

## Step 2: Databricks 등록

Account Console에서 등록합니다.

### VPC Endpoint 등록

1. **Security**→ **Networking**→ **VPC endpoints**→ **Register VPC endpoint**
2. 입력:
   - **VPC endpoint name**: `prod-frontend-rest-vpce`
   - **VPC endpoint ID**: Transit VPC의 `vpce-xxxxxxxx`
   - **Region**: `ap-northeast-2`
3. **Register**클릭

### Private Access Settings — Allowed Endpoints 추가

- Frontend Endpoint도 **Allowed VPC endpoint IDs**에 추가 필요
- Public access = Disabled 전환 시 Backend + Frontend 모두 등록

## Step 3: Route 53 DNS 구성

Route 53 → Hosted zones → Create hosted zone (Private)

| 항목 | 설정값 |
|------|--------|
| **Domain name**| `cloud.databricks.com` |
| **Type**| Private hosted zone |
| **Associated VPC**| Transit VPC |

### A Record (Alias) 추가

| Record name | Type | Alias Target |
|-------------|------|-------------|
| `<workspace-deployment-name>` | A (Alias) | Frontend VPC Endpoint |

DNS 흐름: `<ws>.cloud.databricks.com` → Private Hosted Zone → Endpoint Private IP

*참고: [PrivateLink DNS](https://docs.databricks.com/aws/en/security/network/classic/privatelink-dns)*

## Step 4: Route 53 Inbound Resolver

On-Premises에서 Private Hosted Zone 해석 (VPN/DX 사용 시):

| 항목 | 설정값 |
|------|--------|
| **VPC**| Transit VPC |
| **Security Group**| TCP/UDP 53 from Corporate Network |
| **IP addresses**| 2개+ (서로 다른 AZ) |

### Corporate DNS Conditional Forwarder

| Domain | Forward To |
|--------|-----------|
| `*.cloud.databricks.com` | Resolver IP |
| `*.aws.databricksapps.com` | Resolver IP |

검증: `nslookup <ws>.cloud.databricks.com` → `10.x.x.x` 반환 시 정상

{% hint style="warning" %}
**SSO/Unified Login**시 CNAME 추가: `accounts-pl-auth.privatelink.cloud.databricks.com`
{% endhint %}

## Frontend PrivateLink — 구성 체크리스트

놓치기 쉬운 항목들:

| # | 체크 항목 |
|---|----------|
| 1 | Transit VPC DNS Hostnames/Resolution 활성화 |
| 2 | VPC Endpoint 생성 (REST API, port 443) |
| 3 | Enable private DNS names = **No**|
| 4 | Databricks Account Console에 VPC Endpoint 등록 |
| 5 | Route 53 Private Hosted Zone 생성 (`cloud.databricks.com`) |
| 6 | A Record (Alias) → VPC Endpoint 매핑 |
| 7 | Route 53 Inbound Resolver 생성 (On-prem 접근 시) |
| 8 | Corporate DNS Conditional Forwarder 설정 |
| 9 | `nslookup` 검증 — Private IP 반환 확인 |
| 10 | Private Access Settings — Public access = Disabled 전환 |
| 11 | SSO/Unified Login CNAME 추가 (필요시) |
| 12 | `*.aws.databricksapps.com` DNS 포워딩 (Apps 사용시) |
