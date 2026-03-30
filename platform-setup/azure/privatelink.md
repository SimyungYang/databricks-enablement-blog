# Backend Private Link

## Private Link 아키텍처 개요

Azure Databricks Private Link는 고객 VNet에서 Databricks Control Plane으로의 통신을 **Azure 프라이빗 네트워크**를 통해 수행합니다.

| Private Endpoint 유형 | Sub-resource | 용도 |
|----------------------|--------------|------|
| **databricks_ui_api** | `databricks_ui_api` | REST API + Web UI 접근 |
| **browser_authentication** | `browser_authentication` | SSO 인증 리다이렉트 |

{% hint style="info" %}
**AWS와의 차이**: AWS에서는 REST API용 VPC Endpoint와 SCC Relay용 VPC Endpoint 두 개를 생성합니다. Azure에서는 `databricks_ui_api`(UI/API)와 `browser_authentication`(인증) 두 개의 Private Endpoint를 생성합니다.
{% endhint %}

## Step 1 — Private Endpoint 생성 (databricks_ui_api)

1. Azure Portal → **"프라이빗 엔드포인트"** 검색 → **+ 만들기**

### 기본 탭

| 필드 | 값 |
|------|-----|
| **구독** | 동일 구독 |
| **리소스 그룹** | `rg-databricks-prod` |
| **이름** | `pe-databricks-ui-api` |
| **네트워크 인터페이스 이름** | 자동 생성 |
| **리전** | Korea Central |

### 리소스 탭

| 필드 | 값 |
|------|-----|
| **연결 방법** | 내 디렉터리의 Azure 리소스에 연결 |
| **구독** | 동일 구독 |
| **리소스 종류** | `Microsoft.Databricks/workspaces` |
| **리소스** | `dbw-prod-koreacentral` |
| **대상 하위 리소스** | `databricks_ui_api` |

### 가상 네트워크 탭

| 필드 | 값 |
|------|-----|
| **가상 네트워크** | `vnet-databricks-prod` |
| **서브넷** | `snet-privatelink` |
| **프라이빗 IP 구성** | 동적으로 IP 주소 할당 |

### DNS 탭

| 필드 | 값 |
|------|-----|
| **프라이빗 DNS 영역과 통합** | **예** |
| **프라이빗 DNS 영역** | `privatelink.azuredatabricks.net` (자동 생성) |

**검토 + 만들기** 클릭

## Step 2 — Private Endpoint 생성 (browser_authentication)

동일한 절차로 두 번째 Private Endpoint를 생성합니다.

| 필드 | 값 |
|------|-----|
| **이름** | `pe-databricks-browser-auth` |
| **대상 하위 리소스** | `browser_authentication` |
| **나머지 설정** | 위와 동일 (같은 VNet, 같은 서브넷, 같은 DNS 영역) |

{% hint style="warning" %}
**browser_authentication Private Endpoint는 리전당 1개만 필요합니다.** 동일 리전에 여러 Workspace가 있어도 browser_authentication PE는 하나로 공유할 수 있습니다. databricks_ui_api PE는 Workspace마다 별도로 생성해야 합니다.
{% endhint %}

## Step 3 — Private DNS Zone 확인

Private Endpoint 생성 시 **프라이빗 DNS 영역과 통합: 예**를 선택했다면 자동으로 구성됩니다.

확인 사항:
1. Azure Portal → **프라이빗 DNS 영역** → `privatelink.azuredatabricks.net`
2. **가상 네트워크 링크**: `vnet-databricks-prod`가 연결되어 있는지 확인
3. **레코드 집합**: Workspace URL에 대한 A 레코드가 Private IP를 가리키는지 확인

## Step 4 — NSG 규칙 참고 사항

{% hint style="danger" %}
**Private Link 서브넷에는 NSG 규칙을 정의하지 마세요.** Private Endpoint가 위치한 서브넷(`snet-privatelink`)에는 별도의 NSG 인바운드/아웃바운드 규칙이 불필요합니다. Azure Private Link 트래픽은 NSG 규칙과 무관하게 작동합니다.
{% endhint %}

## Step 5 — nslookup 검증

Private Link 구성 후 DNS 확인을 수행합니다.

```bash
# VNet 내부 VM 또는 VPN 연결된 환경에서 실행
nslookup adb-{workspace-id}.{random}.azuredatabricks.net

# 기대 결과: Private IP (10.0.2.x) 반환
# 잘못된 결과: Public IP 반환 → DNS 영역 연결 확인 필요
```

{% hint style="info" %}
`nslookup` 결과가 Private IP를 반환하면 Private Link가 정상 작동하는 것입니다. Public IP가 반환되면 Private DNS Zone과 VNet의 링크가 올바르게 설정되었는지 확인하세요.
{% endhint %}

## Step 6 — Public Network Access 비활성화

Private Link 검증 완료 후 Public 접근을 차단합니다.

1. Azure Portal → Databricks Workspace → **네트워킹** 메뉴
2. **Public network access** → **Disabled** 변경
3. **저장** 클릭

{% hint style="warning" %}
Public network access를 Disabled로 변경하면 Private Link 경로를 통해서만 Workspace에 접근할 수 있습니다. VPN 또는 ExpressRoute를 통해 VNet에 연결된 환경에서만 접속 가능합니다. **반드시 Private Link 접속이 확인된 후 변경하세요.**
{% endhint %}

*참고: [Azure Databricks Private Link](https://learn.microsoft.com/azure/databricks/security/network/classic/private-link-standard) · [Private Endpoint 구성](https://learn.microsoft.com/azure/databricks/security/network/classic/private-link-standard#step-3-create-private-endpoints)*
