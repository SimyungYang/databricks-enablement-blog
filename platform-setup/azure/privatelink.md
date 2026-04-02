# Backend Private Link

## Private Link 아키텍처 개요

Azure Databricks Private Link는 고객 VNet에서 Databricks Control Plane으로의 통신을 **Azure 프라이빗 네트워크** 를 통해 수행합니다. 인터넷을 경유하지 않으므로 데이터 유출 위험을 줄이고 보안 컴플라이언스를 충족할 수 있습니다.

| Private Endpoint 유형 | Sub-resource | 용도 | 수량 |
|----------------------|--------------|------|------|
| **databricks_ui_api** | `databricks_ui_api` | REST API + Web UI 접근 | Workspace마다 1개 |
| **browser_authentication** | `browser_authentication` | SSO 인증 리다이렉트 | 리전당 1개 (공유 가능) |

{% hint style="info" %}
**AWS와의 차이**: AWS에서는 REST API용 VPC Endpoint와 SCC Relay용 VPC Endpoint 두 개를 생성합니다. Azure에서는 `databricks_ui_api`(UI/API)와 `browser_authentication`(인증) 두 개의 Private Endpoint를 생성합니다.
{% endhint %}

## Private Link 배포 유형

| 유형 | 설명 | 사용 사례 |
|------|------|-----------|
| **Backend Private Link** | Workspace VNet에서 Control Plane으로의 백엔드 통신 | 클러스터 ↔ Control Plane |
| **Frontend Private Link** | 사용자가 Workspace UI/API에 접근하는 프론트엔드 통신 | 사용자 브라우저 ↔ Workspace |
| **Backend + Frontend** | 백엔드와 프론트엔드 모두 Private Link 사용 | 완전한 프라이빗 환경 |

{% hint style="info" %}
**대부분의 보안 요구사항에서는 Backend + Frontend 모두 구성합니다.** Backend만 구성하면 클러스터 통신은 프라이빗이지만, 사용자의 웹 접근은 여전히 인터넷을 경유합니다. Frontend Private Link는 Transit VNet(Hub VNet)에 Private Endpoint를 배치하여 구성합니다.
{% endhint %}

## 사전 준비

- [ ] Premium 티어 Workspace 생성 완료
- [ ] VNet Injection으로 Workspace 배포 완료 (자체 VNet에 배포)
- [ ] Private Link Subnet 준비 (`snet-privatelink`, `/27` 이상)
- [ ] Contributor + Network Contributor RBAC 역할

## Step 1 — Private Endpoint 생성 (databricks_ui_api)

1. Azure Portal → 상단 검색창에 " **프라이빗 엔드포인트**" (Private endpoints) 입력
2. " **+ 만들기**" (Create) 클릭

### 기본 탭 (Basics)

| 필드 | 값 | 설명 |
|------|-----|------|
| **구독** | 동일 구독 | Workspace와 같은 구독 |
| **리소스 그룹** | `rg-databricks-prod` | Workspace와 같은 RG 권장 |
| **이름** | `pe-databricks-ui-api` | 명명 규칙에 맞게 |
| **네트워크 인터페이스 이름** | 자동 생성 (변경 가능) | `pe-databricks-ui-api-nic` |
| **리전** | Korea Central | Workspace와 동일 리전 필수 |

" **다음: 리소스**" 클릭

### 리소스 탭 (Resource)

| 필드 | 값 | 설명 |
|------|-----|------|
| **연결 방법** | 내 디렉터리의 Azure 리소스에 연결 | 같은 테넌트 |
| **구독** | 동일 구독 | |
| **리소스 종류** | `Microsoft.Databricks/workspaces` | 드롭다운에서 선택 |
| **리소스** | `dbw-prod-koreacentral` | 대상 Workspace 선택 |
| **대상 하위 리소스** | `databricks_ui_api` | 드롭다운에서 선택 |

{% hint style="warning" %}
**리소스 목록에 Workspace가 보이지 않는 경우**: Workspace가 Premium 티어인지, VNet Injection으로 배포되었는지 확인하세요. Standard 티어나 Managed VNet Workspace에서는 Private Link를 사용할 수 없습니다.
{% endhint %}

" **다음: 가상 네트워크**" 클릭

### 가상 네트워크 탭 (Virtual Network)

| 필드 | 값 | 설명 |
|------|-----|------|
| **가상 네트워크** | `vnet-databricks-prod` | Workspace VNet |
| **서브넷** | `snet-privatelink` | Private Link 전용 서브넷 |
| **프라이빗 IP 구성** | 동적으로 IP 주소 할당 | 기본값 유지 |

{% hint style="info" %}
**Backend Private Link는 Workspace VNet에 배치합니다.** Frontend Private Link는 사용자가 접속하는 Transit VNet(Hub VNet)에 별도로 생성합니다.
{% endhint %}

" **다음: DNS**" 클릭

### DNS 탭

| 필드 | 값 | 설명 |
|------|-----|------|
| **프라이빗 DNS 영역과 통합** | **예** | 자동으로 DNS 레코드 생성 |
| **프라이빗 DNS 영역** | `privatelink.azuredatabricks.net` | 자동 생성 또는 기존 선택 |

{% hint style="info" %}
**"예"를 선택하면** Azure가 자동으로:
1. `privatelink.azuredatabricks.net` Private DNS Zone 생성 (없는 경우)
2. VNet에 DNS Zone 링크 생성
3. Workspace URL에 대한 A 레코드 생성 (Private IP 매핑)
{% endhint %}

" **다음: 태그**" → " **다음: 검토 + 만들기**" → " **만들기**" 클릭

배포 완료 대기 (~2-3분)

## Step 2 — Private Endpoint 생성 (browser_authentication)

동일한 절차로 두 번째 Private Endpoint를 생성합니다.

| 필드 | 값 | 변경 사항 |
|------|-----|-----------|
| **이름** | `pe-databricks-browser-auth` | 다른 이름 |
| **대상 하위 리소스** | `browser_authentication` | sub-resource 변경 |
| **가상 네트워크** | `vnet-databricks-prod` | 동일 |
| **서브넷** | `snet-privatelink` | 동일 |
| **프라이빗 DNS 영역** | `privatelink.azuredatabricks.net` | 동일 (기존 Zone 재사용) |

{% hint style="warning" %}
**browser_authentication Private Endpoint는 리전당 1개만 필요합니다.** 동일 리전에 여러 Workspace가 있어도 browser_authentication PE는 하나로 공유할 수 있습니다. `databricks_ui_api` PE는 Workspace마다 별도로 생성해야 합니다.
{% endhint %}

{% hint style="info" %}
**browser_authentication이 없으면?** SSO 로그인 시 인증 리다이렉트가 Public 경로를 통하게 됩니다. Public Network Access를 Disabled로 설정한 경우, browser_authentication PE가 없으면 로그인 자체가 불가능해집니다.
{% endhint %}

## Step 3 — Private DNS Zone 확인

Private Endpoint 생성 시 **프라이빗 DNS 영역과 통합: 예** 를 선택했다면 자동으로 구성됩니다. 수동으로 확인합니다.

### 3-1. DNS Zone 확인

1. Azure Portal → 검색창에 " **프라이빗 DNS 영역**" (Private DNS zones) 입력
2. **`privatelink.azuredatabricks.net`** 클릭
3. **Overview** 탭에서 A 레코드 확인:

| 이름 | 유형 | 값 |
|------|------|-----|
| `adb-{workspace-id}.{random}` | A | `10.0.2.4` (Private IP) |
| `adb-{workspace-id}.{random}.{region}` | A | `10.0.2.5` (Private IP) |

### 3-2. VNet 링크 확인

1. `privatelink.azuredatabricks.net` DNS Zone → 좌측 메뉴 " **가상 네트워크 링크**" (Virtual network links)
2. `vnet-databricks-prod`가 링크되어 있는지 확인
3. 상태가 " **Completed**"인지 확인

{% hint style="danger" %}
**VNet 링크가 없으면 DNS 해석이 작동하지 않습니다.** Private Endpoint를 생성했어도 VNet 링크가 없으면 VNet 내에서 Workspace URL이 Public IP로 해석됩니다. 수동으로 링크를 추가하세요:
1. DNS Zone → "가상 네트워크 링크" → "+ 추가"
2. 링크 이름 입력 → VNet 선택 → "확인"
{% endhint %}

### 3-3. Hub VNet 링크 (Hub-Spoke 환경)

Hub-Spoke 아키텍처에서 Hub VNet의 VM이나 VPN 클라이언트에서도 Private Link로 접근하려면:

1. `privatelink.azuredatabricks.net` DNS Zone → " **가상 네트워크 링크**" → " **+ 추가**"
2. Hub VNet도 링크에 추가
3. 또는 Hub의 Custom DNS 서버에서 `privatelink.azuredatabricks.net`을 Azure DNS(`168.63.129.16`)로 전달하도록 설정

## Step 4 — NSG 규칙 참고 사항

{% hint style="info" %}
**Private Link 서브넷에는 별도의 NSG 규칙이 불필요합니다.** Private Endpoint가 위치한 서브넷(`snet-privatelink`)의 트래픽은 Azure Private Link 내부 메커니즘으로 처리되며, NSG 규칙과 무관하게 작동합니다. 단, 조직 정책상 NSG를 연결해야 한다면 빈 NSG(기본 규칙만 있는)를 연결해도 됩니다.
{% endhint %}

## Step 5 — nslookup 검증

Private Link 구성 후 DNS 해석이 올바른지 확인합니다.

### VNet 내부에서 검증

VNet 내부 VM, Bastion, 또는 VPN 연결된 환경에서 실행:

```bash
# Workspace URL 확인
nslookup adb-{workspace-id}.{random}.azuredatabricks.net

# 기대 결과 (Private IP 반환):
# Name:    adb-1234567890.12.azuredatabricks.net
# Address:  10.0.2.4

# CNAME 체인 확인:
# adb-1234567890.12.azuredatabricks.net
#   → adb-1234567890.12.privatelink.azuredatabricks.net
#   → 10.0.2.4
```

### 결과 해석

| 결과 | 의미 | 조치 |
|------|------|------|
| Private IP (`10.x.x.x`) 반환 | Private Link 정상 | 다음 단계 진행 |
| Public IP (`20.x.x.x`, `52.x.x.x`) 반환 | DNS 해석 실패 | DNS Zone VNet 링크 확인 |
| NXDOMAIN | DNS Zone 미생성 | Private DNS Zone 및 A 레코드 확인 |

{% hint style="warning" %}
**VNet 외부(인터넷)에서 nslookup을 실행하면 항상 Public IP가 반환됩니다.** 이는 정상입니다. Private DNS Zone은 링크된 VNet 내부에서만 해석됩니다.
{% endhint %}

## Step 6 — Frontend Private Link (Transit VNet)

사용자가 VPN/ExpressRoute를 통해 Hub VNet에 접속하고, 거기서 Databricks Workspace에 접근하는 구성입니다.

### Frontend PE 구성

Hub VNet(Transit VNet)에 추가 Private Endpoint를 생성합니다.

1. **databricks_ui_api** PE를 Hub VNet의 서브넷에 생성 (절차는 Step 1과 동일, VNet/서브넷만 변경)
2. `privatelink.azuredatabricks.net` DNS Zone에 Hub VNet 링크 추가 (Step 3-3 참고)

{% hint style="info" %}
Frontend Private Link를 구성하면 사용자의 웹 브라우저 → Workspace UI 통신도 프라이빗 네트워크를 통합니다. VPN 클라이언트에서 `nslookup`으로 Private IP가 반환되는지 확인하세요.
{% endhint %}

## Step 7 — 방화벽 + WSA Private Endpoint

Azure Firewall 또는 NVA(Network Virtual Appliance)를 사용하는 환경에서 추가로 필요한 설정입니다.

### Web App Authentication (WSA) Private Endpoint

Public Network Access를 Disabled로 설정하고 방화벽이 있는 환경에서는 **WSA(Web App Authentication) Private Endpoint** 가 추가로 필요할 수 있습니다.

{% hint style="warning" %}
방화벽에서 `login.microsoftonline.com` 등 인증 관련 FQDN을 차단하는 경우, SSO 로그인이 실패합니다. 방화벽 규칙에서 다음 FQDN을 허용하세요:
- `login.microsoftonline.com`
- `aadcdn.msauth.net`
- `login.live.com`
{% endhint %}

## Step 8 — Public Network Access 비활성화

Private Link 검증이 완료된 후 Public 접근을 차단합니다.

1. Azure Portal → 대상 Databricks Workspace 이동
2. 좌측 메뉴에서 " **네트워킹**" (Networking) 클릭
3. " **Public network access**" → " **Disabled**" 변경
4. " **저장**" (Save) 클릭

{% hint style="danger" %}
**Public network access를 Disabled로 변경하면**:
- Private Link 경로를 통해서만 Workspace에 접근 가능
- VPN/ExpressRoute를 통해 VNet에 연결되지 않은 사용자는 접속 불가
- Databricks REST API 호출도 Private Link 경로에서만 가능
- **반드시 Private Link 접속이 확인된 후 변경하세요**
{% endhint %}

### 단계적 전환 권장

| 단계 | Public Access | 설명 |
|------|:------------:|------|
| 1 | Enabled | Private Endpoint 생성 및 DNS 확인 |
| 2 | Enabled | Private Link를 통한 접속 테스트 |
| 3 | **Disabled** | 모든 사용자가 Private Link로 접속 가능 확인 후 변경 |

## Troubleshooting

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| nslookup에서 Public IP 반환 | DNS Zone에 VNet 링크 없음 | DNS Zone → 가상 네트워크 링크 추가 |
| Private Endpoint 상태 "Pending" | 자동 승인 실패 | Workspace 리소스에서 PE 연결 승인 |
| SSO 로그인 실패 | browser_authentication PE 미생성 | browser_authentication PE 추가 |
| "403 Forbidden" 오류 | Public access Disabled + Private Link 미연결 | nslookup으로 경로 확인, Public access 임시 활성화 |
| 클러스터 시작 실패 | Backend PE만 있고 Frontend PE 없음 | Backend PE 상태 확인, NSG 규칙 검토 |

*참고: [Azure Databricks Private Link](https://learn.microsoft.com/azure/databricks/security/network/classic/private-link-standard) · [Private Endpoint 구성](https://learn.microsoft.com/azure/databricks/security/network/classic/private-link-standard#step-3-create-private-endpoints)*
