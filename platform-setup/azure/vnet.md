# Virtual Network 생성

## 네트워크 설계 개요

Databricks VNet Injection에는 최소 2개의 전용 서브넷이 필요합니다. Private Link를 사용하려면 추가 서브넷도 필요합니다.

| 서브넷 | 용도 | 최소 크기 | 권장 크기 | Subnet Delegation |
|--------|------|-----------|-----------|-------------------|
| **Host Subnet**(Public Subnet) | 클러스터 드라이버/워커 호스트 | /26 | **/24** | 필수 |
| **Container Subnet**(Private Subnet) | 클러스터 컨테이너 네트워크 | /26 | **/24** | 필수 |
| **Private Link Subnet** | Private Endpoint 배치 | /28 | **/27** | 불필요 |

{% hint style="warning" %}
**CIDR 권장 사항**: VNet 전체는 `/22` 이상으로 생성하세요. 서브넷당 최소 `/26`이 필요하지만, 클러스터 규모에 따라 IP가 부족할 수 있으므로 `/24`를 권장합니다. 각 클러스터 노드는 Host Subnet과 Container Subnet에서 각각 1개의 IP를 사용합니다.
{% endhint %}

### IP 소요량 계산

| 서브넷 크기 | 사용 가능 IP | 동시 지원 노드 수 | 적합한 환경 |
|------------|-------------|------------------|------------|
| `/26` | 59개 | ~55개 | PoC, 소규모 |
| `/25` | 123개 | ~120개 | 중규모 |
| `/24` | 251개 | ~250개 | 프로덕션 권장 |
| `/23` | 507개 | ~500개 | 대규모 |

{% hint style="info" %}
Azure는 각 서브넷에서 5개의 IP를 예약합니다 (네트워크 주소, 기본 게이트웨이, DNS 매핑 2개, 브로드캐스트). 따라서 `/26`(64개)에서 실제 사용 가능한 IP는 59개입니다.
{% endhint %}

## Step 1 — VNet 만들기

1. Azure Portal 로그인
2. 상단 검색창에 " **가상 네트워크**" (또는 "Virtual networks") 입력
3. " **Virtual networks**" 서비스 클릭
4. " **+ 만들기**" (또는 "+ Create") 클릭

## Step 2 — 기본 정보 (Basics 탭)

| 필드 | 값 | 설명 |
|------|-----|------|
| **구독** | 동일 구독 | Databricks Workspace와 같은 구독 |
| **리소스 그룹** | `rg-databricks-prod` | 기존 RG 또는 새로 생성 |
| **이름** | `vnet-databricks-prod` | 명명 규칙에 맞게 설정 |
| **리전** | Korea Central | Workspace와 동일 리전 필수 |

{% hint style="warning" %}
**VNet의 리전은 Workspace 리전과 반드시 동일해야 합니다.** 다른 리전의 VNet에는 Workspace를 배포할 수 없습니다.
{% endhint %}

" **다음: IP 주소**" 클릭

## Step 3 — IP 주소 구성 (IP Addresses 탭)

### VNet 주소 공간

**IPv4 address space**: `10.0.0.0/22`

기본으로 생성된 `default` 서브넷이 있다면 삭제하고, 아래 서브넷들을 추가합니다.

### 서브넷 추가

" **+ 서브넷 추가**" 버튼을 클릭하여 각 서브넷을 생성합니다.

#### 서브넷 1: Host Subnet

| 필드 | 값 |
|------|-----|
| **서브넷 이름** | `snet-databricks-host` |
| **서브넷 주소 범위** | `10.0.0.0/24` |

#### 서브넷 2: Container Subnet

| 필드 | 값 |
|------|-----|
| **서브넷 이름** | `snet-databricks-container` |
| **서브넷 주소 범위** | `10.0.1.0/24` |

#### 서브넷 3: Private Link Subnet

| 필드 | 값 |
|------|-----|
| **서브넷 이름** | `snet-privatelink` |
| **서브넷 주소 범위** | `10.0.2.0/27` |

{% hint style="info" %}
Private Link Subnet은 Private Endpoint를 배포할 때만 필요합니다. Private Link를 사용하지 않을 계획이라면 나중에 추가해도 됩니다.
{% endhint %}

" **다음: 보안**" 클릭

## Step 4 — 보안 탭 (Security)

| 항목 | 설정 | 설명 |
|------|------|------|
| **Azure Bastion** | 사용 안 함 | VNet 내 VM 접속 필요 시에만 활성화 |
| **Azure Firewall** | 사용 안 함 | 별도 방화벽 정책이 있을 때 활성화 |
| **Azure DDoS Protection** | 기본값 유지 | 추가 비용 발생 (Standard 플랜) |

{% hint style="info" %}
Bastion과 Firewall은 조직의 보안 정책에 따라 나중에 추가할 수 있습니다. Databricks 구성 자체에는 불필요합니다. Azure Firewall을 사용하는 경우 Databricks Control Plane으로의 아웃바운드 규칙을 별도로 구성해야 합니다.
{% endhint %}

" **다음: 태그**" 클릭 → 필요 시 태그 추가 → " **다음: 검토 + 만들기**" 클릭

## Step 5 — 검토 + 만들기

1. 설정 요약을 확인합니다:
   - VNet 이름, 리전, 주소 공간
   - 서브넷 3개 (host, container, privatelink)
2. " **만들기**" (Create) 클릭
3. 배포 완료 대기 (~1-2분)
4. " **리소스로 이동**" 클릭하여 생성된 VNet 확인

## Step 6 — Subnet Delegation 설정

VNet 생성 후 Databricks 전용 서브넷(Host, Container)에 **Subnet Delegation** 을 설정해야 합니다.

### Subnet Delegation이란?

Subnet Delegation은 특정 Azure 서비스가 해당 서브넷을 전용으로 사용하도록 위임하는 것입니다. `Microsoft.Databricks/workspaces`로 위임하면:

- Databricks가 해당 서브넷에 클러스터 노드 VM을 배포할 수 있음
- 다른 Azure 서비스(App Service, SQL MI 등)는 해당 서브넷에 배포 불가
- Databricks가 필요한 NSG 규칙을 자동으로 관리할 수 있음

### 설정 절차

1. 생성된 VNet → 좌측 메뉴에서 " **서브넷**" (Subnets) 클릭
2. **`snet-databricks-host`** 클릭하여 설정 창 열기
3. " **서브넷 위임**" (Subnet delegation) 드롭다운에서 **`Microsoft.Databricks/workspaces`** 선택
4. " **저장**" (Save) 클릭
5. **`snet-databricks-container`** 클릭하여 동일하게 반복
6. " **서브넷 위임**" → **`Microsoft.Databricks/workspaces`** 선택 → " **저장**"

{% hint style="danger" %}
**반드시 두 서브넷 모두 위임 설정이 필요합니다.** Host Subnet과 Container Subnet 중 하나라도 `Microsoft.Databricks/workspaces`에 위임하지 않으면 Workspace 배포 시 다음 오류가 발생합니다:
```
Subnet 'snet-databricks-host' is not delegated to 'Microsoft.Databricks/workspaces'.
```
{% endhint %}

{% hint style="warning" %}
**Private Link Subnet에는 위임을 설정하지 마세요.**`snet-privatelink` 서브넷은 Private Endpoint 전용이며, Databricks 위임을 설정하면 Private Endpoint를 배포할 수 없게 됩니다.
{% endhint %}

### 위임 설정 확인

설정 완료 후 각 서브넷을 클릭하면 " **서브넷 위임**" 필드에 `Microsoft.Databricks/workspaces`가 표시되어야 합니다.

## Step 7 — NSG 자동 생성 확인

Databricks 서브넷에 위임을 설정하면, Workspace 배포 시 NSG가 **자동으로 생성** 되어 서브넷에 연결됩니다.

### NSG 관리 방식

| 방식 | 설명 | 권장 |
|------|------|------|
| **자동 생성 (기본)** | Workspace 배포 시 Databricks가 NSG 생성 및 규칙 관리 | O (대부분의 경우) |
| **수동 생성** | 사전에 빈 NSG를 만들어 서브넷에 연결 | 조직 정책상 필요 시 |

{% hint style="info" %}
수동으로 NSG를 미리 만들어 연결할 수도 있지만, **Databricks 필수 규칙을 직접 추가하지 마세요.** Workspace 배포 시 Databricks가 자동으로 필요한 규칙을 추가합니다. 수동으로 추가한 Databricks 규칙은 충돌을 일으킬 수 있습니다.
{% endhint %}

### 자동 생성되는 주요 NSG 규칙

| 방향 | 우선순위 | 이름 | 설명 |
|------|---------|------|------|
| Inbound | 100 | `databricks-worker-to-worker-inbound` | 클러스터 노드 간 통신 |
| Outbound | 100 | `databricks-worker-to-databricks-webapp` | Control Plane 통신 |
| Outbound | 101 | `databricks-worker-to-sql` | 메타스토어 접근 |
| Outbound | 102 | `databricks-worker-to-storage` | Azure Storage 접근 |
| Outbound | 103 | `databricks-worker-to-worker-outbound` | 클러스터 노드 간 통신 |
| Outbound | 104 | `databricks-worker-to-eventhub` | Log 전송 (진단 로그) |

{% hint style="warning" %}
**NSG에 커스텀 규칙을 추가할 때 주의하세요.** 위 Databricks 자동 규칙보다 높은 우선순위(낮은 숫자)로 Deny 규칙을 만들면 클러스터가 시작되지 않거나 정상 작동하지 않습니다. 커스텀 규칙은 우선순위 200 이상에서 추가하는 것을 권장합니다.
{% endhint %}

## VNet Peering 고려사항 (Hub-Spoke)

기존 Hub-Spoke 아키텍처에 Databricks VNet을 Spoke로 연결하는 경우:

### 구성 시 확인 사항

| 항목 | 확인 내용 |
|------|-----------|
| **CIDR 충돌** | Databricks VNet CIDR이 Hub VNet 및 다른 Spoke VNet과 겹치지 않아야 함 |
| **게이트웨이 전송** | Hub VNet에 VPN Gateway/ExpressRoute Gateway가 있으면 " **Use remote gateways**" 활성화 |
| **DNS 전달** | Hub에 Custom DNS 서버가 있으면 Databricks VNet에서도 해당 DNS를 사용하도록 설정 |
| **UDR (User Defined Route)** | Databricks 서브넷에 UDR 적용 시, Control Plane 통신이 차단되지 않도록 주의 |

### Peering 설정 절차

1. Azure Portal → " **가상 네트워크**" → Databricks VNet 선택
2. 좌측 메뉴에서 " **피어링**" (Peerings) 클릭
3. " **+ 추가**" 클릭
4. 다음 정보 입력:

| 필드 | 값 |
|------|-----|
| **이 가상 네트워크 → 피어링 링크 이름** | `peer-dbx-to-hub` |
| **원격 가상 네트워크 → 피어링 링크 이름** | `peer-hub-to-dbx` |
| **가상 네트워크** | Hub VNet 선택 |
| **원격 가상 네트워크의 게이트웨이 사용** | Hub에 Gateway가 있으면 체크 |

5. " **추가**" 클릭
6. 양쪽 Peering 상태가 " **Connected**"인지 확인

{% hint style="danger" %}
**UDR로 0.0.0.0/0을 방화벽으로 강제 터널링하는 경우**, Databricks Control Plane(Webapp, SCC Relay)으로의 통신을 방화벽에서 허용해야 합니다. 허용하지 않으면 클러스터 시작이 실패합니다. 필요한 FQDN은 [Databricks 공식 문서](https://learn.microsoft.com/azure/databricks/security/network/classic/udr-firewall)를 참고하세요.
{% endhint %}

*참고: [VNet Injection 요구사항](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject) · [NSG 규칙](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject#network-security-group-rules) · [UDR/Firewall](https://learn.microsoft.com/azure/databricks/security/network/classic/udr-firewall)*
