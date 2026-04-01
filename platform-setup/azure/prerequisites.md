# 사전 준비

## 개요

Azure Databricks를 구성하기 전에 Azure 구독, 권한, 네트워크 설계를 사전에 준비해야 합니다. 이 페이지는 누락되기 쉬운 선행 조건을 상세히 다룹니다.

## 사전 준비 체크리스트

| # | 항목 | 필수 | 확인 방법 |
|---|------|:----:|-----------|
| 1 | Azure Subscription 활성 상태 | O | Azure Portal → Subscriptions |
| 2 | Pricing Tier: Premium | O | Workspace 생성 시 선택 |
| 3 | RBAC 역할: Contributor + User Access Administrator | O | IAM → Role assignments |
| 4 | 리전 결정 | O | 팀 합의 |
| 5 | Entra ID (Azure AD) 테넌트 접근 | O | Entra ID Portal |
| 6 | 네트워크 CIDR 설계 | O | 네트워크 팀 협의 |
| 7 | Resource Provider 등록 | O | Subscriptions → Resource providers |

## 1. Azure 구독 확인

### 구독 상태 확인 방법

1. Azure Portal 로그인 → 상단 검색창에 "** 구독**" 입력
2. **Subscriptions** 서비스 클릭
3. 사용할 구독 선택 → ** 상태** 가 "**Active**"인지 확인

| 구독 유형 | Databricks 지원 | 비고 |
|-----------|:--------------:|------|
| **Pay-As-You-Go (PAYG)**| O | 종량제, 소규모 PoC에 적합 |
| **Enterprise Agreement (EA)**| O | 대규모 기업, 할인 적용 |
| **CSP (Cloud Solution Provider)**| O | 파트너를 통한 구매 |
| **MSDN/Visual Studio**| 제한적 | 개발/테스트 용도만, 프로덕션 부적합 |
| **Free Trial**| X | Databricks 리소스 생성 제한 |

{% hint style="warning" %}
** 무료 평가판(Free Trial) 구독에서는 Databricks Workspace를 생성할 수 없습니다.**PAYG로 업그레이드한 후 진행하세요.
{% endhint %}

### Resource Provider 등록

Databricks 배포에 필요한 Resource Provider가 등록되어 있는지 확인합니다.

1. Azure Portal → **Subscriptions**→ 구독 선택
2. 좌측 메뉴에서 "**Resource providers**" 클릭
3. 다음 Provider가 "**Registered**" 상태인지 확인:

| Resource Provider | 용도 |
|-------------------|------|
| `Microsoft.Databricks` | Databricks Workspace |
| `Microsoft.Compute` | VM (클러스터 노드) |
| `Microsoft.Network` | VNet, NSG, Private Endpoint |
| `Microsoft.Storage` | Storage Account (DBFS) |
| `Microsoft.ManagedIdentity` | Managed Identity |

4. "**NotRegistered**" 상태인 Provider가 있으면 선택 후 "**Register**" 클릭

## 2. 필요한 RBAC 역할

Databricks Workspace 및 관련 Azure 리소스를 생성/관리하려면 다음 RBAC 역할이 필요합니다.

| RBAC 역할 | 범위 | 용도 |
|-----------|------|------|
| **Contributor**| Subscription 또는 Resource Group | VNet, Storage, Databricks Workspace 생성 |
| **User Access Administrator**| Subscription 또는 Resource Group | Managed Identity 역할 할당 |
| **Network Contributor**| VNet이 있는 Resource Group | VNet Injection 시 서브넷 위임, NSG 관리 |

### RBAC 역할 확인 방법

1. Azure Portal → 대상 **Subscription** 또는 **Resource Group** 이동
2. 좌측 메뉴에서 "**Access control (IAM)**" 클릭
3. "**Role assignments**" 탭에서 본인 계정의 역할 확인

{% hint style="info" %}
** 간편 설정**: 초기 구성 시 **Owner** 역할을 사용하면 위 모든 권한이 포함됩니다. 구성 완료 후 최소 권한 원칙에 맞게 역할을 축소하세요.
{% endhint %}

{% hint style="warning" %}
**Custom Role 사용 시 주의**: Contributor 역할이 조직 정책으로 제한된 경우, 최소한 `Microsoft.Databricks/*`, `Microsoft.Network/*`, `Microsoft.Storage/*`, `Microsoft.Compute/*` 액션이 허용되어야 합니다.
{% endhint %}

## 3. Azure 리전 선택

### 한국 고객 리전 가이드

| 리전 | 위치 | Databricks 지원 | 지연 시간 (서울 기준) | 권장 용도 |
|------|------|:--------------:|---------------------|-----------|
| **Korea Central**| 서울 | O | ~1ms | 프로덕션 (1순위) |
| **Korea South**| 부산 | O | ~5ms | DR 용도 |
| **Japan East**| 도쿄 | O | ~30ms | Korea Central 미지원 기능 시 대안 |
| **East Asia**| 홍콩 | O | ~50ms | 아시아 태평양 허브 |

{% hint style="info" %}
**Korea Central을 1순위로 권장합니다.** 데이터 주권(Data Residency) 요구사항이 있는 경우 반드시 Korea Central 또는 Korea South를 선택하세요. Unity Catalog 메타스토어의 리전도 Workspace 리전과 동일하게 설정하는 것이 좋습니다.
{% endhint %}

### 리전별 기능 가용성 확인

모든 Databricks 기능이 모든 리전에서 동시에 출시되지 않습니다. 특정 기능의 리전 가용성은 [Azure Databricks 리전 가용성](https://learn.microsoft.com/azure/databricks/resources/supported-regions)에서 확인하세요.

## 4. Entra ID (Azure AD) 설정

Azure Databricks는 Entra ID(구 Azure AD)를 통해 사용자 인증을 처리합니다.

### 확인 사항

1. ** 테넌트 접근**: Entra ID 포털 (`https://entra.microsoft.com`)에 로그인 가능한지 확인
2. ** 사용자 생성 권한**: 필요 시 Databricks 전용 서비스 계정 생성 가능해야 함
3. ** 앱 등록 권한**: Service Principal(앱 등록) 생성이 필요한 경우 `Application Administrator` 역할 필요

### SCIM 프로비저닝 (선택)

Entra ID에서 Databricks로 사용자/그룹을 자동 동기화하려면:

1. Entra ID → **Enterprise applications**→ **New application**→ "Azure Databricks SCIM Provisioning" 검색
2. 또는 Account Console에서 SCIM 토큰 생성 후 Entra ID에 연결

{% hint style="info" %}
SCIM 프로비저닝은 초기 구성 시 필수는 아니지만, 50명 이상의 사용자를 관리할 때 강력히 권장합니다. 수동 사용자 관리의 부담을 크게 줄여줍니다.
{% endhint %}

## 5. 네트워크 설계 사전 계획

VNet Injection을 사용하려면 사전에 CIDR 블록과 서브넷 크기를 계획해야 합니다.

### 권장 CIDR 설계

| 구성 요소 | CIDR | IP 수 | 용도 |
|-----------|------|--------|------|
| **VNet**| `/22` 이상 | 1,024+ | 전체 주소 공간 |
| **Host Subnet**| `/24` | 254 | 클러스터 드라이버/워커 호스트 |
| **Container Subnet**| `/24` | 254 | 클러스터 컨테이너 네트워크 |
| **Private Link Subnet**| `/27` 이상 | 30+ | Private Endpoint 배치 |

### IP 소요량 계산

- 각 클러스터 노드는 **Host Subnet에서 1개 IP**+ **Container Subnet에서 1개 IP** 사용
- `/24` 서브넷 = 최대 254개 IP = 최대 ~250개 동시 노드 지원
- `/26` 서브넷 = 최대 62개 IP = 소규모 환경에 적합

{% hint style="warning" %}
** 기존 Hub-Spoke 네트워크와 겹치지 않도록 CIDR을 선택하세요.**VNet Peering 시 CIDR 충돌이 있으면 연결이 실패합니다. 네트워크 팀과 사전 협의하여 사용 가능한 주소 범위를 확인하세요.
{% endhint %}

### 예시 설계

```
VNet: 10.0.0.0/22

├── snet-databricks-host:      10.0.0.0/24   (Host Subnet)
├── snet-databricks-container:  10.0.1.0/24   (Container Subnet)
├── snet-privatelink:           10.0.2.0/27   (Private Endpoint)
└── 예비:                       10.0.2.32/27~ (향후 확장용)
```

## 6. Databricks Account Console 접근

Azure Databricks는 AWS와 달리 Account Console 접근이 자동으로 설정됩니다.

1. Azure Portal에서 Databricks Workspace를 최초 배포하면 Databricks Account가 자동 생성됨
2. Account Console URL: `https://accounts.azuredatabricks.net`
3. Entra ID SSO로 로그인
4. 최초 Workspace를 생성한 사용자가 자동으로 Account Admin이 됨

{% hint style="info" %}
**Account Console은 Workspace 생성 전에는 접근할 수 없습니다.** 최초 Workspace를 Azure Portal에서 생성한 후 Account Console에 로그인할 수 있습니다. 이후 추가 Workspace 생성이나 Unity Catalog 설정은 Account Console에서 수행합니다.
{% endhint %}

## 최종 체크리스트

구성 시작 전 아래 항목을 모두 확인하세요:

- [ ] Azure Subscription이 Active 상태인가?
- [ ] 필요한 Resource Provider가 모두 Registered 상태인가?
- [ ] Contributor + User Access Administrator RBAC 역할이 있는가?
- [ ] 리전이 결정되었는가? (Korea Central 권장)
- [ ] Entra ID 테넌트에 접근 가능한가?
- [ ] VNet CIDR 블록이 설계되었는가? (기존 네트워크와 충돌 없음 확인)
- [ ] Pricing Tier: Premium으로 선택할 것인가?
- [ ] Private Link 사용 시 Premium 티어인가?

*참고: [Azure Databricks 사전 요구사항](https://learn.microsoft.com/azure/databricks/admin/account-settings/) · [VNet 요구사항](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject)*
