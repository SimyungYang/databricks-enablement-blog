# Azure Workspace 구성 가이드

Azure Portal 기반으로 Databricks Workspace를 처음부터 구성하는 전체 가이드입니다. VNet Injection, Private Link, Unity Catalog까지 엔터프라이즈 환경에 필요한 모든 단계를 다룹니다.

## 대상

* Azure에 Databricks를 신규 도입하는 고객
* Private Link 구성이 필요한 엔터프라이즈 고객
* AWS Databricks 경험이 있고 Azure 차이점을 파악하려는 고객

## 목차

| # | 단계 | 설명 |
|---|------|------|
| 1 | Azure Databricks 아키텍처 | Control Plane / Compute Plane, Azure 특화 구조 |
| 2 | [사전 준비](prerequisites.md) | 구독, 권한, 리전 |
| 3 | [Resource Group 생성](resource-group.md) | 리소스 그룹 구성 |
| 4 | [Virtual Network (VNet) 생성](vnet.md) | VNet, Subnet, NSG 위임 |
| 5 | [Access Connector 생성](access-connector.md) | Managed Identity 기반 스토리지 접근 |
| 6 | [Storage Account 생성 (ADLS Gen2)](storage-account.md) | Unity Catalog용 스토리지 |
| 7 | [Workspace 배포](workspace.md) | Azure Portal에서 Workspace 프로비저닝 |
| 8 | [Backend Private Link](privatelink.md) | Private Endpoint + DNS Zone |
| 9 | [Unity Catalog](unity-catalog.md) | Metastore + Catalog & Schema |
| 비교 | AWS vs Azure 차이점 요약 | 아래 참고 |

---

## Azure Databricks 아키텍처

### 전체 아키텍처 — Control Plane + Compute Plane 분리 구조

Azure Databricks도 AWS와 동일하게 **Control Plane**과 **Compute Plane**이 분리되어 있습니다. 핵심 차이점은 Azure Databricks가 **1st-party Azure 서비스** 라는 점입니다.

| 항목 | Control Plane (Databricks 관리) | Compute Plane (고객 VNet) |
|------|------|------|
| **위치**| Databricks Azure 리전 인프라 | 고객 Azure Subscription VNet |
| **구성요소**| Web UI, REST API, Cluster Manager, Jobs Scheduler | VM 인스턴스 (클러스터 노드) |
| **데이터**| Notebook 메타데이터, Unity Catalog 메타데이터 | DBFS Root Storage, 고객 데이터 (ADLS Gen2) |
| **통신**| Azure Backbone 네트워크 | VNet 내부 + Azure Backbone |

{% hint style="info" %}
**AWS와의 핵심 차이**: AWS에서는 Databricks가 별도 AWS 계정에서 Control Plane을 운영하고 Cross-Account IAM Role로 권한을 위임받습니다. Azure에서는 **Azure Backbone**위에서 직접 통신하며, **1st-party 서비스** 로서 Azure Portal에서 바로 배포합니다.
{% endhint %}

### Secure Cluster Connectivity (SCC)

Azure Databricks는 **SCC(Secure Cluster Connectivity)** 가 기본 활성화되어 있습니다.

| 항목 | 설명 |
|------|------|
| **SCC 역할**| 클러스터 노드가 Control Plane에 **아웃바운드 전용** 으로 연결 |
| **인바운드 포트**| 열지 않음 — Public IP 불필요 |
| **NAT**| 고객 VNet의 NAT Gateway 또는 Azure Load Balancer 사용 |
| **기본값**| Azure Databricks에서 **기본 활성화**(별도 설정 불필요) |

{% hint style="success" %}
SCC 덕분에 클러스터 노드에 Public IP를 부여하지 않아도 됩니다. AWS에서는 이를 위해 별도의 SCC Relay VPC Endpoint를 구성해야 하지만, Azure에서는 기본 동작입니다.
{% endhint %}

### VNet Injection 개요

VNet Injection은 Databricks 클러스터를 **고객이 소유한 VNet** 에 배포하는 방식입니다.

* 고객 VNet 내 두 개의 전용 서브넷(Host Subnet, Container Subnet)에 클러스터 노드가 생성됨
* NSG(Network Security Group)를 통해 트래픽을 제어할 수 있음
* 서브넷은 **Microsoft.Databricks/workspaces** 에 위임(delegation)해야 함
* Private Endpoint와 결합하여 완전한 프라이빗 환경 구현 가능

*참고: [Azure Databricks 아키텍처 개요](https://learn.microsoft.com/azure/databricks/getting-started/overview) · [VNet Injection](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject)*

---

## AWS vs Azure 차이점 요약

기존 AWS Databricks 경험이 있는 고객을 위한 비교표입니다.

| 항목 | AWS | Azure |
|------|-----|-------|
| **서비스 유형**| 3rd-party (Marketplace 구독) | **1st-party Azure 서비스**|
| **배포 방법**| Databricks Account Console | **Azure Portal**|
| **인증 방식**| Cross-Account IAM Role + Trust Policy | **Access Connector (Managed Identity)**|
| **스토리지**| S3 + Bucket Policy | **ADLS Gen2 + RBAC 역할 할당**|
| **네트워크**| VPC + Private Subnet + Security Group | **VNet + Subnet + NSG (위임)**|
| **서브넷 위임**| 불필요 | **Microsoft.Databricks/workspaces 위임 필수**|
| **SCC (Secure Cluster Connectivity)**| 별도 SCC Relay VPC Endpoint 필요 | **기본 활성화 (추가 구성 불필요)**|
| **Private Link — Backend**| VPC Endpoint 2개 (REST API + SCC Relay) | **Private Endpoint 2개 (UI/API + Browser Auth)**|
| **Private Link — Frontend**| Transit VPC + Route 53 DNS | **동일 VNet의 Private Endpoint**|
| **DNS**| Route 53 Private Hosted Zone | **Azure Private DNS Zone**|
| **Managed Resource Group**| 없음 (고객 계정 내 직접 관리) | **자동 생성 (Databricks 내부 리소스용)**|
| **UC Storage Credential**| IAM Role ARN | **Access Connector Resource ID**|
| **Workspace 생성 소요 시간**| 약 5~10분 | **약 3~5분**|

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
