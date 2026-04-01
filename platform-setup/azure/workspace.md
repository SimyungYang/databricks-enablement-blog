# Workspace 배포

## Step 1 — Azure Databricks 리소스 만들기

1. Azure Portal → "**Azure Databricks**" 검색 → **+ 만들기**

## Step 2 — 기본 정보

| 필드 | 값 | 설명 |
|------|-----|------|
| ** 구독** | 동일 구독 | |
| ** 리소스 그룹** | `rg-databricks-prod` | |
| **Workspace 이름** | `dbw-prod-koreacentral` | |
| ** 리전** | Korea Central | |
| **Pricing Tier** | **Premium** | Private Link, UC 필수 |

{% hint style="danger" %}
**Pricing Tier은 반드시 Premium을 선택하세요.**Standard 티어에서는 VNet Injection, Private Link, Unity Catalog가 지원되지 않습니다. 프로덕션 환경에서는 반드시 Premium이 필요합니다.
{% endhint %}

## Step 3 — 네트워킹 탭

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
**Public network access** 는 초기에 Enabled로 설정하여 Workspace 접속 및 기본 검증을 완료한 후, Private Link 구성 완료 시 **Disabled** 로 전환하는 것을 권장합니다.
{% endhint %}

## Step 4 — 고급 탭 (선택)

| 필드 | 값 |
|------|-----|
| **Managed Resource Group 이름** | 자동 생성 (또는 직접 지정) |
| **Infrastructure Encryption** | 필요 시 사용 (Double Encryption) |

{% hint style="info" %}
**Managed Resource Group** 은 Databricks가 내부적으로 사용하는 리소스(Managed Disk, NSG 등)가 생성되는 별도 리소스 그룹입니다. 이름을 지정하지 않으면 `databricks-rg-{workspace-name}-{random}` 형식으로 자동 생성됩니다.
{% endhint %}

## Step 5 — 태그 + 검토 + 만들기

태그 설정 후 **검토 + 만들기** 클릭 → 유효성 검사 통과 확인 → **만들기** 클릭

배포에 약 **3~5분** 소요됩니다.

## Step 6 — 배포 확인

1. 배포 완료 후 **리소스로 이동** 클릭
2. **Workspace URL** 확인 — 형식: `adb-{workspace-id}.{random}.azuredatabricks.net`
3. **Launch Workspace** 클릭하여 Databricks UI 접속 확인

{% hint style="success" %}
**축하합니다!**Databricks Workspace가 VNet Injection과 함께 배포되었습니다. 이제 Private Link를 구성하여 보안을 강화합니다.
{% endhint %}

*참고: [Azure Databricks Workspace 만들기](https://learn.microsoft.com/azure/databricks/getting-started/#create-an-azure-databricks-workspace) · [VNet Injection을 통한 배포](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject)*
