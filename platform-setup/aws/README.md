# AWS Workspace 구성 가이드

Marketplace 구독부터 PrivateLink까지, AWS Console 기반으로 Databricks Workspace를 처음부터 구성하는 전체 가이드입니다.

> **슬라이드 버전**: [AWS Workspace 구성 가이드 (웹 슬라이드)](https://simyungyang.github.io/databricks-enablement-blog/aws-workspace-setup.html)

{% embed url="https://simyungyang.github.io/databricks-enablement-blog/aws-workspace-setup.html" %}

## 대상

* AWS에 Databricks를 신규 도입하는 고객
* PrivateLink(프라이빗 연결) 구성이 필요한 엔터프라이즈 고객

## 목차

| # | 단계 | 설명 |
|---|------|------|
| 0 | Databricks on AWS 아키텍처 | Control Plane / Compute Plane 구조, PrivateLink 아키텍처 |
| 1 | [AWS Marketplace 구독](marketplace.md) | Marketplace vs Direct 계약, 기존 계정 연결 |
| 2 | [사전 준비](prerequisites.md) | IAM 권한, STS 엔드포인트, Enterprise 티어 |
| 3 | [Credential 구성](credential.md) | Cross-Account IAM Role — Trust Policy, Permission Policy |
| 4 | [Storage 구성](storage.md) | Root S3 Bucket, Bucket Policy |
| 5 | [Network 구성](network.md) | VPC, Private Subnet, Security Group, AWS Service Endpoints |
| 6 | [Backend PrivateLink](privatelink-backend.md) | VPC Endpoint (REST API + SCC Relay), Private Access Settings |
| 7 | [Frontend PrivateLink (옵션)](privatelink-frontend.md) | Transit VPC, Route 53 DNS, Inbound Resolver |
| 8 | [Workspace 생성](workspace.md) | Account Console에서 프로비저닝 |
| 9 | [Unity Catalog](unity-catalog.md) | UC Metastore + Storage Credential + File Events IAM |
| 10 | [Serverless NCC](serverless-ncc.md) | Serverless Compute 네트워크 제어 |
| 11 | [기존 WS에 PrivateLink 추가](privatelink-migration.md) | 운영 중 Workspace에 PrivateLink 사후 적용 |
| A | [Terraform 자동화](terraform.md) | IaC 전환 참고 (Appendix) |

---

## Databricks on AWS 아키텍처

### 전체 아키텍처 — Control Plane + Compute Plane 분리 구조

![Databricks on AWS Architecture](https://docs.databricks.com/aws/en/assets/images/architecture-c2c83d23e2f7870f30137e97aaadea0b.png)

*출처: [Databricks High-Level Architecture](https://docs.databricks.com/aws/en/getting-started/high-level-architecture)*

### Control Plane vs Compute Plane

| 항목 | Control Plane (Databricks 관리) | Compute Plane (고객 AWS 계정) |
|------|------|------|
| **위치** | Databricks AWS 계정 | 고객 AWS 계정 VPC |
| **구성요소** | Web UI, REST API, Cluster Manager | EC2 인스턴스 (클러스터 노드) |
| **데이터** | Notebook, Unity Catalog 메타데이터 | DBFS Root Storage (S3), 고객 데이터 |
| **역할** | 오케스트레이션, IAM | 실제 연산 수행, 데이터 접근 |

{% hint style="info" %}
**핵심**: 고객 데이터는 **고객 AWS 계정**에 머무름 — Control Plane은 메타데이터와 오케스트레이션만 담당
{% endhint %}

*참고: [Databricks Concepts](https://docs.databricks.com/aws/en/getting-started/concepts)*

### Classic vs Serverless Workspace

| 항목 | Classic Workspace | Serverless Workspace |
|------|------------------|---------------------|
| **Compute 위치** | **고객 VPC** 내 EC2 | **Databricks 관리** VPC |
| **고객 구성** | IAM Role, S3, VPC, SG 직접 구성 | 구성 불필요 |
| **네트워크 제어** | 완전 제어 가능 | NCC로 관리 |
| **PrivateLink** | 구성 가능 (Backend + Frontend) | NCC 기반 별도 구성 |
| **적합 시나리오** | 프로덕션, 보안 요건 | PoC, 빠른 시작 |

{% hint style="info" %}
**이 가이드는 Classic Workspace 구성**을 다룹니다 — 고객이 AWS 리소스를 직접 구성하는 방식
{% endhint %}

### Serverless Workspace 아키텍처

![Serverless Workspace Architecture](https://docs.databricks.com/aws/en/assets/images/serverless-workspaces-1634da84fc840966875dfee6e9f613e0.png)

*출처: [Serverless Compute Overview](https://docs.databricks.com/aws/en/getting-started/high-level-architecture)*

### Workspace 구성에 필요한 AWS 리소스

Classic Workspace 기준 — 고객이 준비해야 할 것:

| 분류 | AWS 리소스 | 용도 | Databricks 등록 |
|------|-----------|------|----------------|
| **IAM** | Cross-Account IAM Role | EC2 프로비저닝 권한 위임 | Credential Configuration |
| **IAM** | UC Storage IAM Role | Unity Catalog 데이터 접근 | Storage Credential |
| **S3** | Root Storage Bucket | DBFS 워크스페이스 데이터 | Storage Configuration |
| **S3** | UC Managed Storage Bucket | Unity Catalog 관리 데이터 | External Location |
| **VPC** | VPC + Private Subnet x2 | Databricks 클러스터 실행 | Network Configuration |
| **VPC** | Public Subnet + NAT GW | 아웃바운드 인터넷 접근 | — |
| **VPC** | Security Group | 클러스터 통신 포트 제어 | Network Configuration |
| **VPC** | VPC Endpoints (PrivateLink) | 프라이빗 연결 | VPC Endpoint |
| **KMS** | Customer Managed Key (선택) | 노트북/DBFS 암호화 | CMK Configuration |

*참고: [Create a workspace using the account console](https://docs.databricks.com/aws/en/admin/account-settings-e2/workspaces)*

### PrivateLink 아키텍처 — Backend

Compute Plane → Control Plane 프라이빗 연결:

![Backend PrivateLink Architecture](https://docs.databricks.com/aws/en/assets/images/pl-aws-be-89d73d019437bb90e32610dd5e82ade9.png)

*출처: [PrivateLink Concepts — Classic Compute](https://docs.databricks.com/aws/en/security/network/classic/privatelink-concepts)*

### PrivateLink 아키텍처 — Frontend

사용자 → Workspace 프라이빗 접근:

![Frontend PrivateLink Architecture](https://docs.databricks.com/aws/en/assets/images/pl-aws-fe-84ca114d753c6130f407c6f9b776956d.png)

*출처: [PrivateLink Concepts — Front-End](https://docs.databricks.com/aws/en/security/network/classic/privatelink-concepts)*

### 구성 단계 전체 흐름

AWS Console + Databricks Account Console 매핑:

| 단계 | AWS Console 작업 | Databricks Account Console 등록 | 참고 문서 |
|------|-----------------|-------------------------------|----------|
| 1. **Credential** | IAM Role + Policy 생성 | Cloud resources → Credential configuration | [Docs](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials) |
| 2. **Storage** | S3 Bucket + Policy 생성 | Cloud resources → Storage configuration | [Docs](https://docs.databricks.com/aws/en/admin/account-settings-e2/storage) |
| 3. **VPC/Subnet/SG** | VPC + Subnets + SG 생성 | AWS Console (VPC) | [Docs](https://docs.databricks.com/aws/en/admin/account-settings-e2/networks) |
| 4. **VPC Endpoints** | PrivateLink Endpoint 생성 | AWS Console + Security → Networking → VPC endpoints | [Docs](https://docs.databricks.com/aws/en/security/network/classic/privatelink) |
| 5. **Network** | Endpoint 포함 Network 등록 | Security → Networking → Classic network configurations | [Docs](https://docs.databricks.com/aws/en/admin/account-settings-e2/networks) |
| 6. **Access** | Private Access 설정 | Security → Networking → Private access settings | [Docs](https://docs.databricks.com/aws/en/security/network/classic/privatelink) |
| 7. **Workspace** | Workspace 생성 | Workspaces → Create workspace | [Docs](https://docs.databricks.com/aws/en/admin/account-settings-e2/workspaces) |
