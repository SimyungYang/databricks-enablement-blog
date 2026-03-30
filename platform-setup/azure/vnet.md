# Virtual Network 생성

## 네트워크 설계 개요

Databricks VNet Injection에는 최소 2개의 전용 서브넷이 필요합니다. Private Link를 사용하려면 추가 서브넷도 필요합니다.

| 서브넷 | 용도 | 최소 크기 | 권장 크기 | NSG 위임 |
|--------|------|-----------|-----------|----------|
| **Host Subnet** (Public Subnet) | 클러스터 드라이버/워커 호스트 | /26 | /24 | 필수 |
| **Container Subnet** (Private Subnet) | 클러스터 컨테이너 네트워크 | /26 | /24 | 필수 |
| **Private Link Subnet** | Private Endpoint 배치 | /28 | /27 | 불필요 |

{% hint style="warning" %}
**CIDR 권장 사항**: VNet 전체는 `/22` 이상으로 생성하세요. 서브넷당 최소 `/26`이 필요하지만, 클러스터 규모에 따라 IP가 부족할 수 있으므로 `/24`를 권장합니다. 각 클러스터 노드는 Host Subnet과 Container Subnet에서 각각 1개의 IP를 사용합니다.
{% endhint %}

## Step 1 — VNet 만들기

1. Azure Portal → 상단 검색창에서 **"가상 네트워크"** 검색
2. **+ 만들기** 클릭

## Step 2 — 기본 정보

| 필드 | 값 |
|------|-----|
| **구독** | 동일 구독 |
| **리소스 그룹** | `rg-databricks-prod` |
| **이름** | `vnet-databricks-prod` |
| **리전** | Korea Central |

## Step 3 — IP 주소 구성

**VNet 주소 공간**: `10.0.0.0/22`

| 서브넷 이름 | 주소 범위 | 용도 |
|------------|-----------|------|
| `snet-databricks-host` | `10.0.0.0/24` | Host Subnet (Public) |
| `snet-databricks-container` | `10.0.1.0/24` | Container Subnet (Private) |
| `snet-privatelink` | `10.0.2.0/27` | Private Endpoint용 |

## Step 4 — 보안 탭

| 항목 | 설정 |
|------|------|
| **Azure Bastion** | 사용 안 함 (선택 사항) |
| **Azure Firewall** | 사용 안 함 (선택 사항) |
| **Azure DDoS Protection** | 기본값 유지 |

{% hint style="info" %}
Bastion과 Firewall은 조직의 보안 정책에 따라 나중에 추가할 수 있습니다. Databricks 구성 자체에는 불필요합니다.
{% endhint %}

## Step 5 — 검토 + 만들기

설정 확인 후 **만들기** 클릭

## Step 6 — 서브넷에 NSG 위임 설정

VNet 생성 후 Databricks 전용 서브넷(Host, Container)에 위임을 설정해야 합니다.

1. 생성된 VNet → **서브넷** 메뉴 클릭
2. `snet-databricks-host` 클릭
3. **서브넷 위임** → **Microsoft.Databricks/workspaces** 선택 → 저장
4. `snet-databricks-container`에도 동일하게 반복

{% hint style="danger" %}
**반드시 위임 설정 필요**: 두 서브넷 모두 `Microsoft.Databricks/workspaces`에 위임하지 않으면 Workspace 배포 시 실패합니다. 위임은 해당 서브넷을 Databricks 전용으로 사용하겠다는 의미입니다.
{% endhint %}

## Step 7 — NSG 자동 생성 확인

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
