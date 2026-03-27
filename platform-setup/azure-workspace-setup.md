# Azure Databricks Workspace 구성 가이드

Azure Portal 기반으로 Databricks Workspace를 처음부터 구성하는 전체 가이드입니다. VNet Injection, Private Link, Unity Catalog까지 엔터프라이즈 환경에 필요한 모든 단계를 다룹니다.

## 대상

* Azure에 Databricks를 신규 도입하는 고객
* Private Link 구성이 필요한 엔터프라이즈 고객
* AWS Databricks 경험이 있고 Azure 차이점을 파악하려는 고객

## 목차

| # | 단계 | 설명 |
|---|------|------|
| 1 | Azure Databricks 아키텍처 | Control Plane / Compute Plane, Azure 특화 구조 |
| 2 | 사전 준비 | 구독, 권한, 리전 |
| 3 | Resource Group 생성 | 리소스 그룹 구성 |
| 4 | Virtual Network (VNet) 생성 | VNet, Subnet, NSG 위임 |
| 5 | Access Connector 생성 | Managed Identity 기반 스토리지 접근 |
| 6 | Storage Account 생성 (ADLS Gen2) | Unity Catalog용 스토리지 |
| 7 | Databricks Workspace 배포 | Azure Portal에서 Workspace 프로비저닝 |
| 8 | Backend Private Link 구성 | Private Endpoint + DNS Zone |
| 9 | Unity Catalog Metastore 구성 | 메타스토어 생성 및 Workspace 할당 |
| 10 | Catalog & Schema 생성 | External Location, Catalog, Schema, 테이블 테스트 |
| 비교 | AWS vs Azure 차이점 요약 | 클라우드별 주요 차이 비교표 |

---

## Part 1. Azure Databricks 아키텍처

### 전체 아키텍처 — Control Plane + Compute Plane 분리 구조

Azure Databricks도 AWS와 동일하게 **Control Plane**과 **Compute Plane**이 분리되어 있습니다. 핵심 차이점은 Azure Databricks가 **1st-party Azure 서비스**라는 점입니다.

| 항목 | Control Plane (Databricks 관리) | Compute Plane (고객 VNet) |
|------|------|------|
| **위치** | Databricks Azure 리전 인프라 | 고객 Azure Subscription VNet |
| **구성요소** | Web UI, REST API, Cluster Manager, Jobs Scheduler | VM 인스턴스 (클러스터 노드) |
| **데이터** | Notebook 메타데이터, Unity Catalog 메타데이터 | DBFS Root Storage, 고객 데이터 (ADLS Gen2) |
| **통신** | Azure Backbone 네트워크 | VNet 내부 + Azure Backbone |

{% hint style="info" %}
**AWS와의 핵심 차이**: AWS에서는 Databricks가 별도 AWS 계정에서 Control Plane을 운영하고 Cross-Account IAM Role로 권한을 위임받습니다. Azure에서는 **Azure Backbone** 위에서 직접 통신하며, **1st-party 서비스**로서 Azure Portal에서 바로 배포합니다.
{% endhint %}

### Secure Cluster Connectivity (SCC)

Azure Databricks는 **SCC(Secure Cluster Connectivity)**가 기본 활성화되어 있습니다.

| 항목 | 설명 |
|------|------|
| **SCC 역할** | 클러스터 노드가 Control Plane에 **아웃바운드 전용**으로 연결 |
| **인바운드 포트** | 열지 않음 — Public IP 불필요 |
| **NAT** | 고객 VNet의 NAT Gateway 또는 Azure Load Balancer 사용 |
| **기본값** | Azure Databricks에서 **기본 활성화** (별도 설정 불필요) |

{% hint style="success" %}
SCC 덕분에 클러스터 노드에 Public IP를 부여하지 않아도 됩니다. AWS에서는 이를 위해 별도의 SCC Relay VPC Endpoint를 구성해야 하지만, Azure에서는 기본 동작입니다.
{% endhint %}

### VNet Injection 개요

VNet Injection은 Databricks 클러스터를 **고객이 소유한 VNet**에 배포하는 방식입니다.

* 고객 VNet 내 두 개의 전용 서브넷(Host Subnet, Container Subnet)에 클러스터 노드가 생성됨
* NSG(Network Security Group)를 통해 트래픽을 제어할 수 있음
* 서브넷은 **Microsoft.Databricks/workspaces**에 위임(delegation)해야 함
* Private Endpoint와 결합하여 완전한 프라이빗 환경 구현 가능

*참고: [Azure Databricks 아키텍처 개요](https://learn.microsoft.com/azure/databricks/getting-started/overview) · [VNet Injection](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject)*

---

## Part 2. 사전 준비

### 필수 요건

| 항목 | 요구 사항 | 비고 |
|------|-----------|------|
| **Azure Subscription** | 활성 상태 | PAYG, EA, CSP 모두 가능 |
| **Pricing Tier** | **Premium** | Private Link, Unity Catalog 사용 시 필수 |
| **Azure Portal 권한** | Contributor 이상 | 리소스 그룹, VNet, Storage Account 생성 권한 |
| **리전** | Korea Central 권장 | 국내 고객 기준, 다른 리전도 동일 절차 |
| **Azure AD (Entra ID)** | 테넌트 접근 가능 | Managed Identity 생성에 필요 |

{% hint style="warning" %}
**Pricing Tier 주의**: Standard 티어에서는 VNet Injection, Private Link, Unity Catalog를 사용할 수 없습니다. **반드시 Premium 이상**으로 선택하세요.
{% endhint %}

### Databricks Account Console 접근

Azure Databricks는 AWS와 달리 Account Console 접근이 자동으로 설정됩니다.

1. Azure Portal에서 Databricks Workspace를 최초 배포하면 Databricks Account가 자동 생성됨
2. Account Console URL: `https://accounts.azuredatabricks.net`
3. Azure AD(Entra ID) SSO로 로그인

*참고: [Azure Databricks Account Console](https://learn.microsoft.com/azure/databricks/admin/account-settings/)*

---

## Part 3. Resource Group 생성

### Step 1 — Azure Portal 접속

Azure Portal(`https://portal.azure.com`)에 로그인합니다.

### Step 2 — 리소스 그룹 만들기

1. 상단 검색창에서 **"리소스 그룹"** 검색 → **리소스 그룹** 클릭
2. **+ 만들기** 클릭

### Step 3 — 기본 정보 입력

| 필드 | 값 | 설명 |
|------|-----|------|
| **구독** | 사용할 Azure 구독 선택 | |
| **리소스 그룹 이름** | `rg-databricks-prod` | 명명 규칙에 맞게 조정 |
| **리전** | Korea Central | 모든 리소스를 동일 리전에 배치 |

### Step 4 — 태그 설정

| 태그 키 | 값 (예시) |
|---------|-----------|
| `Owner` | `data-engineering-team` |
| `Environment` | `production` |
| `Project` | `databricks-platform` |

{% hint style="info" %}
태그는 비용 관리와 거버넌스에 중요합니다. 조직의 태깅 정책에 맞게 설정하세요.
{% endhint %}

### Step 5 — 검토 + 만들기

**검토 + 만들기** 클릭 → 유효성 검사 통과 확인 → **만들기** 클릭

---

## Part 4. Virtual Network (VNet) 생성

### 네트워크 설계 개요

Databricks VNet Injection에는 최소 2개의 전용 서브넷이 필요합니다. Private Link를 사용하려면 추가 서브넷도 필요합니다.

| 서브넷 | 용도 | 최소 크기 | 권장 크기 | NSG 위임 |
|--------|------|-----------|-----------|----------|
| **Host Subnet** (Public Subnet) | 클러스터 드라이버/워커 호스트 | /26 | /24 | 필수 |
| **Container Subnet** (Private Subnet) | 클러스터 컨테이너 네트워크 | /26 | /24 | 필수 |
| **Private Link Subnet** | Private Endpoint 배치 | /28 | /27 | 불필요 |

{% hint style="warning" %}
**CIDR 권장 사항**: VNet 전체는 `/22` 이상으로 생성하세요. 서브넷당 최소 `/26`이 필요하지만, 클러스터 규모에 따라 IP가 부족할 수 있으므로 `/24`를 권장합니다. 각 클러스터 노드는 Host Subnet과 Container Subnet에서 각각 1개의 IP를 사용합니다.
{% endhint %}

### Step 1 — VNet 만들기

1. Azure Portal → 상단 검색창에서 **"가상 네트워크"** 검색
2. **+ 만들기** 클릭

### Step 2 — 기본 정보

| 필드 | 값 |
|------|-----|
| **구독** | 동일 구독 |
| **리소스 그룹** | `rg-databricks-prod` |
| **이름** | `vnet-databricks-prod` |
| **리전** | Korea Central |

### Step 3 — IP 주소 구성

**VNet 주소 공간**: `10.0.0.0/22`

| 서브넷 이름 | 주소 범위 | 용도 |
|------------|-----------|------|
| `snet-databricks-host` | `10.0.0.0/24` | Host Subnet (Public) |
| `snet-databricks-container` | `10.0.1.0/24` | Container Subnet (Private) |
| `snet-privatelink` | `10.0.2.0/27` | Private Endpoint용 |

### Step 4 — 보안 탭

| 항목 | 설정 |
|------|------|
| **Azure Bastion** | 사용 안 함 (선택 사항) |
| **Azure Firewall** | 사용 안 함 (선택 사항) |
| **Azure DDoS Protection** | 기본값 유지 |

{% hint style="info" %}
Bastion과 Firewall은 조직의 보안 정책에 따라 나중에 추가할 수 있습니다. Databricks 구성 자체에는 불필요합니다.
{% endhint %}

### Step 5 — 검토 + 만들기

설정 확인 후 **만들기** 클릭

### Step 6 — 서브넷에 NSG 위임 설정

VNet 생성 후 Databricks 전용 서브넷(Host, Container)에 위임을 설정해야 합니다.

1. 생성된 VNet → **서브넷** 메뉴 클릭
2. `snet-databricks-host` 클릭
3. **서브넷 위임** → **Microsoft.Databricks/workspaces** 선택 → 저장
4. `snet-databricks-container`에도 동일하게 반복

{% hint style="danger" %}
**반드시 위임 설정 필요**: 두 서브넷 모두 `Microsoft.Databricks/workspaces`에 위임하지 않으면 Workspace 배포 시 실패합니다. 위임은 해당 서브넷을 Databricks 전용으로 사용하겠다는 의미입니다.
{% endhint %}

### Step 7 — NSG 자동 생성 확인

Databricks 서브넷에 위임을 설정하면, Workspace 배포 시 NSG가 **자동으로 생성**되어 서브넷에 연결됩니다. 수동으로 NSG를 미리 만들어 연결할 수도 있지만, Databricks가 필요한 규칙을 자동 추가하므로 기본 동작을 권장합니다.

**자동 생성되는 주요 NSG 규칙**:

| 방향 | 우선순위 | 이름 | 설명 |
|------|---------|------|------|
| Inbound | 100 | `databricks-worker-to-worker-inbound` | 클러스터 노드 간 통신 |
| Outbound | 100 | `databricks-worker-to-databricks-webapp` | Control Plane 통신 |
| Outbound | 101 | `databricks-worker-to-sql` | 메타스토어 접근 |
| Outbound | 102 | `databricks-worker-to-storage` | Azure Storage 접근 |
| Outbound | 103 | `databricks-worker-to-worker-outbound` | 클러스터 노드 간 통신 |
| Outbound | 104 | `databricks-worker-to-eventhub` | Log 전송 |

*참고: [VNet Injection 요구사항](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject) · [NSG 규칙](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject#network-security-group-rules)*

---

## Part 5. Access Connector 생성

### Access Connector란?

Access Connector는 Azure Databricks가 ADLS Gen2 등 Azure 리소스에 접근할 때 사용하는 **Managed Identity** 컨테이너입니다.

| 항목 | 설명 |
|------|------|
| **역할** | Unity Catalog가 ADLS Gen2에 접근하는 브릿지 |
| **인증 방식** | System-assigned Managed Identity (자동 생성) |
| **AWS 대응** | Cross-Account IAM Role + UC Storage IAM Role |

{% hint style="info" %}
**AWS vs Azure 인증 차이**: AWS에서는 Cross-Account IAM Role과 Trust Policy를 수동으로 구성해야 합니다. Azure에서는 Access Connector를 생성하면 **System-assigned Managed Identity**가 자동으로 생성되어 훨씬 간단합니다.
{% endhint %}

### Step 1 — Access Connector 만들기

1. Azure Portal → 상단 검색창에서 **"Azure Databricks용 액세스 커넥터"** 검색
   * 영문: **"Access Connector for Azure Databricks"**
2. **+ 만들기** 클릭

### Step 2 — 기본 정보 입력

| 필드 | 값 |
|------|-----|
| **구독** | 동일 구독 |
| **리소스 그룹** | `rg-databricks-prod` |
| **이름** | `ac-databricks-prod` |
| **리전** | Korea Central |

### Step 3 — 관리 ID 확인

* **System-assigned Managed Identity**: **사용** (기본값)
* 생성 후 **개요** 페이지에서 **Managed Identity Object ID** 확인 가능

### Step 4 — 태그 설정

| 태그 키 | 값 (예시) |
|---------|-----------|
| `Owner` | `data-engineering-team` |
| `Purpose` | `unity-catalog-access` |

### Step 5 — 검토 + 만들기

설정 확인 후 **만들기** 클릭

{% hint style="warning" %}
**Access Connector Resource ID를 메모하세요**: Unity Catalog Metastore 구성 시 필요합니다. 형식: `/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Databricks/accessConnectors/{name}`
{% endhint %}

*참고: [Access Connector for Azure Databricks](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/azure-managed-identities)*

---

## Part 6. Storage Account 생성 (ADLS Gen2)

### 용도

Unity Catalog의 **Managed Storage**로 사용할 ADLS Gen2 스토리지 계정을 생성합니다. UC 메타스토어가 관리하는 테이블 데이터가 이 스토리지에 저장됩니다.

### Step 1 — 스토리지 계정 만들기

1. Azure Portal → **"스토리지 계정"** 검색 → **+ 만들기**

### Step 2 — 기본 정보

| 필드 | 값 | 설명 |
|------|-----|------|
| **구독** | 동일 구독 | |
| **리소스 그룹** | `rg-databricks-prod` | |
| **스토리지 계정 이름** | `stadatabricksprod` | 소문자/숫자만, 전역 고유 |
| **리전** | Korea Central | |
| **성능** | Standard | Premium은 불필요 |
| **중복** | LRS 또는 GRS | 프로덕션은 GRS 권장 |

### Step 3 — 고급 설정

| 필드 | 값 | 중요도 |
|------|-----|--------|
| **계층 구조 네임스페이스** | **사용** | **필수** — 이것이 ADLS Gen2를 활성화하는 설정 |
| **Blob 공용 액세스** | 사용 안 함 | 보안 |
| **최소 TLS 버전** | TLS 1.2 | 보안 |

{% hint style="danger" %}
**계층 구조 네임스페이스(Hierarchical Namespace)를 반드시 "사용"으로 설정하세요.** 이 옵션이 ADLS Gen2를 활성화합니다. 일반 Blob Storage로 생성하면 Unity Catalog에서 사용할 수 없으며, 스토리지 계정 생성 후에는 이 설정을 변경할 수 없습니다.
{% endhint %}

### Step 4 — 네트워킹

| 필드 | 값 |
|------|-----|
| **네트워크 액세스** | 모든 네트워크에서 퍼블릭 액세스 사용 (초기 설정용) |

{% hint style="info" %}
초기 구성 완료 후 네트워크 액세스를 **선택한 가상 네트워크 및 IP 주소에서 퍼블릭 액세스 사용** 또는 **퍼블릭 액세스 사용 안 함**으로 변경하여 보안을 강화할 수 있습니다.
{% endhint %}

### Step 5 — 검토 + 만들기

설정 확인 후 **만들기** 클릭

### Step 6 — Container 생성

1. 생성된 스토리지 계정 → **컨테이너** 메뉴
2. **+ 컨테이너** 클릭
3. 이름: `uc-metastore` (Unity Catalog 메타스토어용)
4. 공용 액세스 수준: **프라이빗** (기본값)

### Step 7 — Access Connector에 RBAC 역할 부여

Access Connector의 Managed Identity가 이 스토리지에 접근할 수 있도록 역할을 부여합니다.

1. 스토리지 계정 → **액세스 제어(IAM)** 메뉴
2. **+ 역할 할당 추가** 클릭
3. 역할: **Storage Blob Data Contributor**
4. 구성원 → **관리 ID** 선택 → **Access Connector for Azure Databricks** 선택
5. 앞서 생성한 `ac-databricks-prod` 선택
6. **검토 + 할당** 클릭

{% hint style="warning" %}
**Storage Blob Data Contributor** 역할이 정확해야 합니다. `Storage Blob Data Reader`는 읽기만 가능하므로 Unity Catalog가 테이블을 생성/수정할 수 없습니다. `Storage Account Contributor`는 데이터 접근 권한이 아닌 관리 권한이므로 올바르지 않습니다.
{% endhint %}

*참고: [Unity Catalog에 Azure 스토리지 사용](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/azure-managed-identities#step-2-grant-the-managed-identity-access-to-the-storage-account)*

---

## Part 7. Databricks Workspace 배포

### Step 1 — Azure Databricks 리소스 만들기

1. Azure Portal → **"Azure Databricks"** 검색 → **+ 만들기**

### Step 2 — 기본 정보

| 필드 | 값 | 설명 |
|------|-----|------|
| **구독** | 동일 구독 | |
| **리소스 그룹** | `rg-databricks-prod` | |
| **Workspace 이름** | `dbw-prod-koreacentral` | |
| **리전** | Korea Central | |
| **Pricing Tier** | **Premium** | Private Link, UC 필수 |

{% hint style="danger" %}
**Pricing Tier은 반드시 Premium을 선택하세요.** Standard 티어에서는 VNet Injection, Private Link, Unity Catalog가 지원되지 않습니다. 프로덕션 환경에서는 반드시 Premium이 필요합니다.
{% endhint %}

### Step 3 — 네트워킹 탭

| 필드 | 값 | 설명 |
|------|-----|------|
| **Network connectivity** | **No Public IP (NPIP)** | SCC 활성화, Public IP 미사용 |
| **Virtual Network** | `vnet-databricks-prod` 선택 | 앞서 생성한 VNet |
| **Public Subnet Name** | `snet-databricks-host` | Host Subnet |
| **Public Subnet CIDR** | `10.0.0.0/24` | 자동 입력됨 |
| **Private Subnet Name** | `snet-databricks-container` | Container Subnet |
| **Private Subnet CIDR** | `10.0.1.0/24` | 자동 입력됨 |
| **Public network access** | **Enabled** | 초기 검증용, 이후 Disabled 전환 |

{% hint style="info" %}
**Public network access**는 초기에 Enabled로 설정하여 Workspace 접속 및 기본 검증을 완료한 후, Private Link 구성 완료 시 **Disabled**로 전환하는 것을 권장합니다.
{% endhint %}

### Step 4 — 고급 탭 (선택)

| 필드 | 값 |
|------|-----|
| **Managed Resource Group 이름** | 자동 생성 (또는 직접 지정) |
| **Infrastructure Encryption** | 필요 시 사용 (Double Encryption) |

{% hint style="info" %}
**Managed Resource Group**은 Databricks가 내부적으로 사용하는 리소스(Managed Disk, NSG 등)가 생성되는 별도 리소스 그룹입니다. 이름을 지정하지 않으면 `databricks-rg-{workspace-name}-{random}` 형식으로 자동 생성됩니다.
{% endhint %}

### Step 5 — 태그 + 검토 + 만들기

태그 설정 후 **검토 + 만들기** 클릭 → 유효성 검사 통과 확인 → **만들기** 클릭

배포에 약 **3~5분** 소요됩니다.

### Step 6 — 배포 확인

1. 배포 완료 후 **리소스로 이동** 클릭
2. **Workspace URL** 확인 — 형식: `adb-{workspace-id}.{random}.azuredatabricks.net`
3. **Launch Workspace** 클릭하여 Databricks UI 접속 확인

{% hint style="success" %}
**축하합니다!** Databricks Workspace가 VNet Injection과 함께 배포되었습니다. 이제 Private Link를 구성하여 보안을 강화합니다.
{% endhint %}

*참고: [Azure Databricks Workspace 만들기](https://learn.microsoft.com/azure/databricks/getting-started/#create-an-azure-databricks-workspace) · [VNet Injection을 통한 배포](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject)*

---

## Part 8. Backend Private Link 구성

### Private Link 아키텍처 개요

Azure Databricks Private Link는 고객 VNet에서 Databricks Control Plane으로의 통신을 **Azure 프라이빗 네트워크**를 통해 수행합니다.

| Private Endpoint 유형 | Sub-resource | 용도 |
|----------------------|--------------|------|
| **databricks_ui_api** | `databricks_ui_api` | REST API + Web UI 접근 |
| **browser_authentication** | `browser_authentication` | SSO 인증 리다이렉트 |

{% hint style="info" %}
**AWS와의 차이**: AWS에서는 REST API용 VPC Endpoint와 SCC Relay용 VPC Endpoint 두 개를 생성합니다. Azure에서는 `databricks_ui_api`(UI/API)와 `browser_authentication`(인증) 두 개의 Private Endpoint를 생성합니다.
{% endhint %}

### Step 1 — Private Endpoint 생성 (databricks_ui_api)

1. Azure Portal → **"프라이빗 엔드포인트"** 검색 → **+ 만들기**

#### 기본 탭

| 필드 | 값 |
|------|-----|
| **구독** | 동일 구독 |
| **리소스 그룹** | `rg-databricks-prod` |
| **이름** | `pe-databricks-ui-api` |
| **네트워크 인터페이스 이름** | 자동 생성 |
| **리전** | Korea Central |

#### 리소스 탭

| 필드 | 값 |
|------|-----|
| **연결 방법** | 내 디렉터리의 Azure 리소스에 연결 |
| **구독** | 동일 구독 |
| **리소스 종류** | `Microsoft.Databricks/workspaces` |
| **리소스** | `dbw-prod-koreacentral` |
| **대상 하위 리소스** | `databricks_ui_api` |

#### 가상 네트워크 탭

| 필드 | 값 |
|------|-----|
| **가상 네트워크** | `vnet-databricks-prod` |
| **서브넷** | `snet-privatelink` |
| **프라이빗 IP 구성** | 동적으로 IP 주소 할당 |

#### DNS 탭

| 필드 | 값 |
|------|-----|
| **프라이빗 DNS 영역과 통합** | **예** |
| **프라이빗 DNS 영역** | `privatelink.azuredatabricks.net` (자동 생성) |

**검토 + 만들기** 클릭

### Step 2 — Private Endpoint 생성 (browser_authentication)

동일한 절차로 두 번째 Private Endpoint를 생성합니다.

| 필드 | 값 |
|------|-----|
| **이름** | `pe-databricks-browser-auth` |
| **대상 하위 리소스** | `browser_authentication` |
| **나머지 설정** | 위와 동일 (같은 VNet, 같은 서브넷, 같은 DNS 영역) |

{% hint style="warning" %}
**browser_authentication Private Endpoint는 리전당 1개만 필요합니다.** 동일 리전에 여러 Workspace가 있어도 browser_authentication PE는 하나로 공유할 수 있습니다. databricks_ui_api PE는 Workspace마다 별도로 생성해야 합니다.
{% endhint %}

### Step 3 — Private DNS Zone 확인

Private Endpoint 생성 시 **프라이빗 DNS 영역과 통합: 예**를 선택했다면 자동으로 구성됩니다.

확인 사항:
1. Azure Portal → **프라이빗 DNS 영역** → `privatelink.azuredatabricks.net`
2. **가상 네트워크 링크**: `vnet-databricks-prod`가 연결되어 있는지 확인
3. **레코드 집합**: Workspace URL에 대한 A 레코드가 Private IP를 가리키는지 확인

### Step 4 — NSG 규칙 참고 사항

{% hint style="danger" %}
**Private Link 서브넷에는 NSG 규칙을 정의하지 마세요.** Private Endpoint가 위치한 서브넷(`snet-privatelink`)에는 별도의 NSG 인바운드/아웃바운드 규칙이 불필요합니다. Azure Private Link 트래픽은 NSG 규칙과 무관하게 작동합니다.
{% endhint %}

### Step 5 — nslookup 검증

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

### Step 6 — Public Network Access 비활성화

Private Link 검증 완료 후 Public 접근을 차단합니다.

1. Azure Portal → Databricks Workspace → **네트워킹** 메뉴
2. **Public network access** → **Disabled** 변경
3. **저장** 클릭

{% hint style="warning" %}
Public network access를 Disabled로 변경하면 Private Link 경로를 통해서만 Workspace에 접근할 수 있습니다. VPN 또는 ExpressRoute를 통해 VNet에 연결된 환경에서만 접속 가능합니다. **반드시 Private Link 접속이 확인된 후 변경하세요.**
{% endhint %}

*참고: [Azure Databricks Private Link](https://learn.microsoft.com/azure/databricks/security/network/classic/private-link-standard) · [Private Endpoint 구성](https://learn.microsoft.com/azure/databricks/security/network/classic/private-link-standard#step-3-create-private-endpoints)*

---

## Part 9. Unity Catalog Metastore 구성

### Metastore란?

Unity Catalog의 **최상위 컨테이너**입니다. 리전당 1개의 Metastore를 생성하고, 해당 리전의 Workspace들을 할당합니다.

| 항목 | 설명 |
|------|------|
| **단위** | 리전당 1개 |
| **역할** | Catalog, Schema, Table 등의 메타데이터 관리 |
| **스토리지** | ADLS Gen2 Container (앞서 생성) |
| **인증** | Access Connector (Managed Identity) |

### Step 1 — Account Console 접속

1. `https://accounts.azuredatabricks.net` 접속
2. Azure AD(Entra ID)로 로그인
3. 좌측 메뉴 → **Catalog** 클릭

### Step 2 — Metastore 생성

1. **Create metastore** 클릭

| 필드 | 값 | 설명 |
|------|-----|------|
| **Name** | `metastore-koreacentral` | 리전을 포함한 이름 권장 |
| **Region** | Korea Central | Workspace와 동일 리전 |
| **ADLS Gen2 path** | `abfss://uc-metastore@stadatabricksprod.dfs.core.windows.net/` | 컨테이너 경로 |
| **Access Connector ID** | `/subscriptions/{sub-id}/resourceGroups/rg-databricks-prod/providers/Microsoft.Databricks/accessConnectors/ac-databricks-prod` | Access Connector Resource ID |

{% hint style="warning" %}
**ADLS Gen2 경로 형식에 주의하세요.** `abfss://{container}@{storage-account}.dfs.core.windows.net/` 형식이어야 합니다. `blob.core.windows.net`이 아닌 `dfs.core.windows.net`을 사용해야 합니다.
{% endhint %}

### Step 3 — Workspace 할당

1. 생성된 Metastore 클릭
2. **Workspaces** 탭 → **Assign to workspaces** 클릭
3. `dbw-prod-koreacentral` 선택 → **Assign**

{% hint style="success" %}
Metastore가 Workspace에 할당되면, 해당 Workspace에서 Unity Catalog 기능을 사용할 수 있습니다.
{% endhint %}

*참고: [Unity Catalog Metastore 생성](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/create-metastore)*

---

## Part 10. Catalog & Schema 생성

### Step 1 — External Location 생성 (선택)

Managed Storage 외에 추가 스토리지를 연결하려면 External Location을 생성합니다.

1. Workspace UI → **Catalog** → **External Locations** → **Create external location**

| 필드 | 값 |
|------|-----|
| **Name** | `ext-loc-data-lake` |
| **URL** | `abfss://{container}@{storage-account}.dfs.core.windows.net/{path}` |
| **Storage Credential** | Access Connector 기반 Credential 선택 |

{% hint style="info" %}
**Storage Credential**은 Metastore 생성 시 지정한 Access Connector를 통해 자동으로 생성됩니다. 추가 Storage Account를 연결하려면 해당 Storage Account에도 동일하게 Access Connector의 RBAC 역할을 부여해야 합니다.
{% endhint %}

### Step 2 — Catalog 생성

1. Workspace UI → **Catalog** → **+ Add** → **Add a catalog**

| 필드 | 값 |
|------|-----|
| **Name** | `prod_catalog` |
| **Type** | Standard |
| **Managed Location** | 기본값 (Metastore 스토리지) 또는 External Location 지정 |

```sql
-- SQL로도 생성 가능
CREATE CATALOG IF NOT EXISTS prod_catalog;
```

### Step 3 — Schema 생성

1. 생성된 Catalog 하위에서 **+ Add** → **Add a schema**

| 필드 | 값 |
|------|-----|
| **Name** | `bronze` |
| **Managed Location** | 기본값 |

```sql
-- SQL로도 생성 가능
CREATE SCHEMA IF NOT EXISTS prod_catalog.bronze;
```

### Step 4 — 테이블 생성 테스트

Unity Catalog 전체 파이프라인이 정상 작동하는지 검증합니다.

```sql
-- 테스트 테이블 생성
CREATE TABLE IF NOT EXISTS prod_catalog.bronze.test_table (
  id BIGINT GENERATED ALWAYS AS IDENTITY,
  name STRING,
  created_at TIMESTAMP DEFAULT current_timestamp()
);

-- 데이터 삽입
INSERT INTO prod_catalog.bronze.test_table (name)
VALUES ('Azure Databricks 테스트');

-- 조회 확인
SELECT * FROM prod_catalog.bronze.test_table;
```

{% hint style="success" %}
테이블 생성, 데이터 삽입, 조회가 모두 성공하면 Unity Catalog 구성이 완료된 것입니다. ADLS Gen2에 데이터가 Delta 형식으로 저장되었는지 Storage Account에서도 확인해 보세요.
{% endhint %}

### 3-Level Namespace

Unity Catalog는 **3-Level Namespace** 구조를 사용합니다.

```
metastore
  └── catalog
        └── schema
              └── table / view / function
```

| 레벨 | 예시 | 설명 |
|------|------|------|
| **Catalog** | `prod_catalog` | 데이터 도메인 또는 환경 단위 |
| **Schema** | `bronze` | 데이터 레이어 또는 팀 단위 |
| **Table** | `test_table` | 실제 데이터 오브젝트 |

*참고: [Unity Catalog 오브젝트 모델](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/#the-unity-catalog-object-model)*

---

## AWS vs Azure 차이점 요약

기존 AWS Databricks 경험이 있는 고객을 위한 비교표입니다.

| 항목 | AWS | Azure |
|------|-----|-------|
| **서비스 유형** | 3rd-party (Marketplace 구독) | **1st-party Azure 서비스** |
| **배포 방법** | Databricks Account Console | **Azure Portal** |
| **인증 방식** | Cross-Account IAM Role + Trust Policy | **Access Connector (Managed Identity)** |
| **스토리지** | S3 + Bucket Policy | **ADLS Gen2 + RBAC 역할 할당** |
| **네트워크** | VPC + Private Subnet + Security Group | **VNet + Subnet + NSG (위임)** |
| **서브넷 위임** | 불필요 | **Microsoft.Databricks/workspaces 위임 필수** |
| **SCC (Secure Cluster Connectivity)** | 별도 SCC Relay VPC Endpoint 필요 | **기본 활성화 (추가 구성 불필요)** |
| **Private Link — Backend** | VPC Endpoint 2개 (REST API + SCC Relay) | **Private Endpoint 2개 (UI/API + Browser Auth)** |
| **Private Link — Frontend** | Transit VPC + Route 53 DNS | **동일 VNet의 Private Endpoint** |
| **DNS** | Route 53 Private Hosted Zone | **Azure Private DNS Zone** |
| **Managed Resource Group** | 없음 (고객 계정 내 직접 관리) | **자동 생성 (Databricks 내부 리소스용)** |
| **UC Storage Credential** | IAM Role ARN | **Access Connector Resource ID** |
| **Workspace 생성 소요 시간** | 약 5~10분 | **약 3~5분** |

{% hint style="info" %}
**핵심 차이점 3가지**:
1. **배포**: AWS는 Account Console에서, Azure는 Azure Portal에서 배포
2. **인증**: AWS는 IAM Role 수동 구성, Azure는 Managed Identity 자동 생성
3. **네트워크**: AWS는 SG 기반, Azure는 NSG + 서브넷 위임 기반
{% endhint %}

---

## 참고 문서

| 주제 | 링크 |
|------|------|
| Azure Databricks 아키텍처 개요 | [learn.microsoft.com/azure/databricks/getting-started/overview](https://learn.microsoft.com/azure/databricks/getting-started/overview) |
| VNet Injection | [learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject) |
| Private Link 표준 배포 | [learn.microsoft.com/azure/databricks/security/network/classic/private-link-standard](https://learn.microsoft.com/azure/databricks/security/network/classic/private-link-standard) |
| Unity Catalog 구성 | [learn.microsoft.com/azure/databricks/data-governance/unity-catalog/create-metastore](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/create-metastore) |
| Access Connector | [learn.microsoft.com/azure/databricks/data-governance/unity-catalog/azure-managed-identities](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/azure-managed-identities) |
| NSG 규칙 요구사항 | [learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject#network-security-group-rules](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject#network-security-group-rules) |
| Account Console | [accounts.azuredatabricks.net](https://accounts.azuredatabricks.net) |
