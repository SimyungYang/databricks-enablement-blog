# AWS Account & Workspace 구성 가이드

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
| 1 | AWS Marketplace 구독 | Marketplace vs Direct 계약, 기존 계정 연결 |
| 2 | 사전 준비 | IAM 권한, STS 엔드포인트, Enterprise 티어 |
| 3 | Credential 구성 | Cross-Account IAM Role — Trust Policy, Permission Policy |
| 4 | Storage 구성 | Root S3 Bucket, Bucket Policy |
| 5 | Network 구성 | VPC, Private Subnet, Security Group, AWS Service Endpoints |
| 6 | Backend PrivateLink | VPC Endpoint (REST API + SCC Relay), Private Access Settings |
| 7 | Frontend PrivateLink (옵션) | Transit VPC, Route 53 DNS, Inbound Resolver |
| 8 | Workspace 생성 | Account Console에서 프로비저닝 |
| 9 | Unity Catalog Metastore | UC 최상위 컨테이너, 리전당 1개 |
| 10 | Serverless Networking — NCC | Serverless Compute 네트워크 제어 |
| 11 | 기존 Workspace에 PrivateLink 추가 | 운영 중 Workspace에 PrivateLink 사후 적용 |
| A | Terraform 자동화 | IaC 전환 참고 (Appendix) |

---

## Part 0. Databricks on AWS 아키텍처

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

---

## Part 1. AWS Marketplace 구독

### 구독 절차

AWS Console에서 수동으로 진행합니다.

#### Step 1 — Marketplace 접속

- AWS Marketplace에서 **"Databricks"** 검색
- 또는 직접 접속: `aws.amazon.com/marketplace` → Databricks Data Intelligence Platform

#### Step 2 — 구독 및 계정 생성

1. **"Subscribe"** 클릭 → EULA 동의
2. **"Set up your account"** → Databricks 등록 페이지로 리다이렉트
3. 회사명, 이메일, 비밀번호 입력 → 계정 생성 완료
4. AWS Marketplace로 돌아와 **"Continue to Databricks"** 클릭

#### Step 3 — 결과

- Databricks Account 생성 + AWS Marketplace 과금 연결
- **Serverless Workspace** 즉시 사용 가능

*참고: [Subscribe via AWS Marketplace](https://docs.databricks.com/aws/en/admin/account-settings/account) · [AWS Marketplace Listing](https://aws.amazon.com/marketplace/pp/prodview-wtyi5lgtce6n6)*

### Marketplace vs Direct 계약

고객 상황에 따른 최적 선택:

| 항목 | Marketplace (PAYG) | Marketplace (Private Offer) | Direct 계약 |
|------|---|---|---|
| **과금** | AWS 인보이스 통합 | AWS 인보이스 통합 | Databricks 별도 인보이스 |
| **EDP 적용** | **O** — AWS EDP 소진 가능 | **O** | X |
| **가격** | 리스트 가격 | 협상 할인가 | 협상 할인가 |
| **약정** | 없음 (종량제) | 연간/다년 약정 | 연간/다년 약정 |
| **셋업 속도** | 수분 (셀프서비스) | 수일~수주 | 수일~수주 |

{% hint style="info" %}
**핵심**: AWS EDP 잔여 크레딧이 있는 고객은 Marketplace 구독이 유리 — Databricks 비용이 EDP 소진에 포함됨
{% endhint %}

### 기존 계정에 Marketplace 연결

이미 Databricks 계정이 있는 경우:

#### 연결 절차

1. Databricks Account Console 로그인
2. **Settings** → **Subscription & billing**
3. **"Add payment method"** → **AWS Marketplace account** 선택
4. AWS Marketplace로 리다이렉트 → 구독 완료
5. 메뉴에서 **"Set to primary payment method"** 선택

#### 주의사항

{% hint style="warning" %}
- **1 AWS Marketplace 계정 = 1 Databricks 계정** 매핑 (N:1은 가능)
- "You've already accepted this offer" 오류 → 이미 다른 Databricks 계정에 연결됨
- 구독 취소 ≠ Databricks 계정 삭제 (과금 수단만 제거)
{% endhint %}

---

## Part 2. 사전 준비 (Prerequisites)

### 사전 준비 체크리스트

구성 시작 전 반드시 확인해야 합니다.

#### AWS 계정 요구사항

- IAM Role, S3, VPC 생성 권한 보유
- **STS 엔드포인트**: `us-west-2` 리전 활성화 필수 (배포 리전과 무관)
- **SCP**: `sts:AssumeRole` 허용 확인

#### Databricks 계정 요구사항

- **Account Admin** 권한
- **Enterprise 티어** (PrivateLink 사용 시 필수)

#### Databricks AWS Account ID (IAM Trust 설정용)

| 환경 | Account ID |
|------|-----------|
| **Standard AWS** | `414351767826` |
| **AWS GovCloud** | `044793339203` |
| **GovCloud DoD** | `170661010020` |

*참고: [Databricks account IDs for AWS trust policy](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials)*

---

## Part 3. Credential 구성

### Cross-Account IAM Role — 개요

Databricks가 고객 AWS 계정에 EC2를 프로비저닝하기 위한 역할입니다.

#### AWS Console 작업 순서

1. **IAM → Roles → Create role** 에서 Cross-Account Role 생성
2. Trust Policy 설정 (Databricks AWS 계정 신뢰)
3. Permission Policy 부여 (EC2/VPC 관련 권한)
4. **Account Console** → **Cloud resources** → **Credential configuration** → **Add** 에서 Role ARN 등록

*참고: [Create a cross-account IAM role](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials)*

### Cross-Account IAM Role — Policy 유형

고객 VPC 관리 방식에 따라 3가지 정책:

| Policy Type | 설명 | 사용 시점 |
|---|---|---|
| `managed` | Databricks가 VPC 생성/관리 | PoC, 빠른 시작 |
| `customer` | **고객이 VPC 생성**, Databricks는 EC2만 관리 | **프로덕션 권장** |
| `restricted` | customer + ARN 조건 제한 (VPC ID, SG ID 등) | 엄격 보안 요건 |

*참고: [Terraform: databricks_aws_crossaccount_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_crossaccount_policy)*

### Cross-Account IAM Role — Trust Policy

IAM → Roles → Trust relationships 에서 설정합니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "AWS": "arn:aws:iam::414351767826:root" },
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": { "sts:ExternalId": "<YOUR-DATABRICKS-ACCOUNT-ID>" }
    }
  }]
}
```

| 필드 | 값 | 설명 |
|------|---|------|
| **Principal** | `414351767826` | Databricks Standard AWS Account |
| **ExternalId** | Databricks Account UUID | Account Console 상단에서 확인 |

*참고: [Trust policy](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials) · [Terraform: databricks_aws_assume_role_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_assume_role_policy)*

### Cross-Account IAM Role — Permission Policy

customer 타입 주요 권한 (Customer-Managed VPC용):

#### EC2 관련 Actions

- `ec2:RunInstances`, `TerminateInstances`, `DescribeInstances`, `DescribeVolumes`
- `ec2:CreateVolume`, `DeleteVolume`, `AttachVolume`, `DetachVolume`
- `ec2:CreateTags`, `DeleteTags`, `DescribeSubnets`, `DescribeSecurityGroups`
- `ec2:RequestSpotInstances`, `CancelSpotInstanceRequests`, `DescribeSpotPriceHistory`

#### Spot Service-Linked Role

- `iam:CreateServiceLinkedRole`, `iam:PutRolePolicy` on `AWSServiceRoleForEC2Spot`

{% hint style="info" %}
Terraform `databricks_aws_crossaccount_policy` data source로 최신 Policy JSON 자동 생성 가능
{% endhint %}

*참고: [Cross-account policy](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials) · [Terraform: databricks_aws_crossaccount_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_crossaccount_policy)*

### Credential 등록 — Account Console

Databricks Account Console에서 등록합니다.

#### 절차

1. **accounts.cloud.databricks.com** 로그인
2. 좌측 메뉴: **Cloud resources** → **Credential configuration** 탭
3. **Add credential configuration** 클릭
4. 입력:
   - **Credential configuration name**: 식별 이름 (예: `prod-crossaccount-cred`)
   - **Role ARN**: 위에서 생성한 IAM Role ARN (예: `arn:aws:iam::123456789012:role/databricks-crossaccount`)
5. **Add** 클릭

#### 결과

- **Credential ID** 생성됨 → Workspace 생성 시 사용

{% hint style="warning" %}
IAM Role 생성 직후 등록 시 **eventual consistency** 문제로 실패할 수 있음 — 10~30초 대기 후 재시도
{% endhint %}

---

## Part 4. Storage 구성

### Root S3 Bucket — 생성 요건

AWS Console → S3 → Create bucket

#### 필수 설정

| 항목 | 설정값 |
|------|--------|
| **Bucket Region** | Workspace와 **동일 리전** (예: `ap-northeast-2`) |
| **Block all public access** | **On** (모두 체크) |
| **Server-side encryption** | **AES-256** (SSE-S3) 또는 SSE-KMS |
| **Bucket versioning** | Disabled (선택) |
| **ACL** | ACLs disabled (권장) |

*참고: [Configure storage for workspace](https://docs.databricks.com/aws/en/admin/account-settings-e2/storage) · [Terraform: databricks_aws_bucket_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_bucket_policy)*

### Root S3 Bucket — Bucket Policy

S3 → Bucket → Permissions → Bucket policy 에서 설정합니다.

```json
{
  "Sid": "Grant Databricks Access",
  "Effect": "Allow",
  "Principal": { "AWS": "arn:aws:iam::414351767826:root" },
  "Action": [
    "s3:GetObject", "s3:GetObjectVersion", "s3:PutObject",
    "s3:DeleteObject", "s3:ListBucket", "s3:GetBucketLocation"
  ],
  "Resource": ["arn:aws:s3:::<BUCKET>/*", "arn:aws:s3:::<BUCKET>"],
  "Condition": {
    "StringEquals": {
      "aws:PrincipalTag/DatabricksAccountId": ["<ACCOUNT-ID>"]
    }
  }
}
```

{% hint style="warning" %}
`<BUCKET>` = S3 버킷 이름, `<ACCOUNT-ID>` = Databricks Account UUID — 반드시 교체
{% endhint %}

### Storage 등록 — Account Console

Databricks Account Console에서 등록합니다.

#### 절차

1. **accounts.cloud.databricks.com** 로그인
2. 좌측 메뉴: **Cloud resources** → **Storage configuration** 탭
3. **Add storage configuration** 클릭
4. 입력:
   - **Storage configuration name**: 식별 이름 (예: `prod-root-storage`)
   - **Bucket name**: S3 Bucket 이름 (ARN 아님, 이름만)
5. **Add** 클릭

#### 결과

- **Storage Configuration ID** 생성됨 → Workspace 생성 시 사용

{% hint style="warning" %}
이 설정은 **수정 불가** — 변경 필요 시 삭제 후 재생성 (Workspace가 연결된 경우 삭제 불가)
{% endhint %}

*참고: [Configure storage](https://docs.databricks.com/aws/en/admin/account-settings-e2/storage) · [Terraform: databricks_mws_storage_configurations](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_storage_configurations)*

---

## Part 5. Network 구성

### VPC 생성 — 요구사항

AWS Console → VPC → Create VPC

| 항목 | 설정값 |
|------|--------|
| **CIDR** | `/16` ~ `/17` 권장 (예: `10.4.0.0/16`) |
| **DNS hostnames** | **Enabled** |
| **DNS resolution** | **Enabled** |
| **예약 CIDR (충돌 회피)** | `127.187.216.0/24`, `192.168.216.0/24`, `198.18.216.0/24`, `172.17.0.0/16` |

#### Subnet 구성

| Subnet | 수량 | 용도 | 비고 |
|--------|------|------|------|
| **Private** | 2개+ | Databricks 클러스터 | 서로 다른 AZ, netmask `/17`~`/25` |
| **Public** | 1개 | NAT GW + IGW | 아웃바운드 인터넷 |
| **VPC Endpoint** | 1개 | PrivateLink 전용 | local route만, NAT 없음 |

*참고: [Configure customer-managed VPC](https://docs.databricks.com/aws/en/admin/account-settings-e2/networks)*

### Security Group — 필수 규칙

AWS Console → VPC → Security Groups → Create security group

#### Egress (아웃바운드) 규칙

| Port | Protocol | Destination | 용도 |
|------|----------|-------------|------|
| All | TCP/UDP | Self (동일 SG) | 클러스터 내부 통신 |
| 443 | TCP | 0.0.0.0/0 | Control Plane, 외부 라이브러리 |
| 3306 | TCP | 0.0.0.0/0 | Legacy Hive Metastore |
| 6666 | TCP | 0.0.0.0/0 | SCC Relay 통신 |
| 8443-8451 | TCP | 0.0.0.0/0 | Compute → Control Plane API |
| 2443 | TCP | 0.0.0.0/0 | FIPS (Compliance Security Profile) |

#### Ingress (인바운드) 규칙

| Port | Protocol | Source | 용도 |
|------|----------|--------|------|
| All TCP | TCP | Self (동일 SG) | 노드 간 통신 |
| All UDP | UDP | Self (동일 SG) | 노드 간 통신 |

*참고: [Security group rules](https://docs.databricks.com/aws/en/admin/account-settings-e2/networks)*

### NACL (Network ACL) 설정

AWS Console → VPC → Network ACLs

Security Group과 별도로 서브넷 레벨에서 트래픽을 제어하는 Network ACL을 설정합니다.

#### Inbound Rules

| Rule # | Type | Protocol | Port | Source | Action |
|--------|------|----------|------|--------|--------|
| 100 | All traffic | All | All | 0.0.0.0/0 | ALLOW |

#### Outbound Rules

| Rule # | Type | Protocol | Port | Destination | Action |
|--------|------|----------|------|-------------|--------|
| 100 | All traffic | All | All | VPC CIDR | ALLOW |
| 110 | HTTPS | TCP | 443 | 0.0.0.0/0 | ALLOW |
| 120 | Custom TCP | TCP | 3306 | 0.0.0.0/0 | ALLOW |
| 130 | Custom TCP | TCP | 6666 | 0.0.0.0/0 | ALLOW |
| 140 | Custom TCP | TCP | 8443-8451 | 0.0.0.0/0 | ALLOW |
| 150 | Custom TCP | TCP | 2443 | 0.0.0.0/0 | ALLOW |

{% hint style="warning" %}
**NACL은 stateless** — Security Group과 달리 인바운드/아웃바운드 규칙을 모두 명시적으로 설정해야 합니다. 응답 트래픽도 자동 허용되지 않으므로 양방향 규칙이 필수입니다.
{% endhint %}

*참고: [Network configuration](https://docs.databricks.com/aws/en/admin/account-settings-e2/networks)*

### 권장 AWS Service VPC Endpoints

AWS Console → VPC → Endpoints → Create endpoint

| Service | Type | Service Name | Private DNS | 용도 |
|---------|------|-------------|-------------|------|
| **S3** | Gateway | `com.amazonaws.ap-northeast-2.s3` | N/A | DBFS, Delta Lake |
| **STS** | Interface | `com.amazonaws.ap-northeast-2.sts` | Enabled | IAM 인증 |
| **Kinesis** | Interface | `com.amazonaws.ap-northeast-2.kinesis-streams` | Enabled | 로그 전송 |

- **S3 Gateway**: Route Table에 연결 (Private Subnet의 Route Table)
- **STS/Kinesis Interface**: Private Subnet에 배치, Security Group 필요 (443 inbound)

### Network 등록 — 사전 조건

Security → Networking → Classic network configurations

{% hint style="warning" %}
**순서 주의**: Network Configuration 생성 시 **VPC Endpoint를 지정**해야 함 → **Part 6의 VPC Endpoint 등록을 먼저 완료** 후 진행
{% endhint %}

#### 입력 항목 요약

| 항목 | 값 |
|------|---|
| **Network configuration name** | 식별 이름 |
| **VPC ID** | `vpc-xxxxxxxx` |
| **Subnet IDs** | Private Subnet 2개 (서로 다른 AZ) |
| **Security Group IDs** | SG ID (최대 5개) |
| **VPC Endpoints — REST API** | 등록된 Workspace Endpoint 선택 |
| **VPC Endpoints — Dataplane relay** | 등록된 SCC Relay Endpoint 선택 |

### Network 등록 — 절차

Security → Networking → Classic network configurations

1. **Add network configuration** 클릭
2. 이전 항목 입력 + VPC Endpoints 지정
3. **Add** → **Network ID** 생성됨 → Workspace 생성 시 사용

{% hint style="info" %}
Network configuration은 **수정 불가** — 변경 시 새로 생성 후 Workspace에서 교체 (3단계 프로세스)
{% endhint %}

---

## Part 6. Backend PrivateLink 구성

### PrivateLink 개요 — Backend vs Frontend 비교

| 항목 | Backend (Classic) — 필수 권장 | Frontend (Inbound) — 옵션 |
|------|------|------|
| **방향** | Compute → Control Plane | 사용자 → Workspace |
| **용도** | 클러스터가 API/Relay에 접근 | Web UI, REST API, DB Connect |
| **VPC Endpoint** | **2개** (REST API + SCC Relay) | **1개** (REST API만) |
| **배치 위치** | Compute VPC | Transit VPC (또는 동일 VPC) |
| **DNS 추가 구성** | 불필요 (private DNS enabled) | Route 53 Private Hosted Zone 필요 |
| **핵심 이점** | 인터넷 없이 클러스터 운영 | End-to-End 프라이빗 접근 |

{% hint style="warning" %}
**Enterprise 티어 필수** — Customer-Managed VPC + SCC 활성화 필요
{% endhint %}

*참고: [PrivateLink Concepts](https://docs.databricks.com/aws/en/security/network/classic/privatelink-concepts) · [Enable PrivateLink](https://docs.databricks.com/aws/en/security/network/classic/privatelink)*

### ap-northeast-2 (서울) VPC Endpoint Service Names

이 값으로 AWS VPC Endpoint를 생성합니다.

#### Workspace (REST API) Endpoint

```
com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e
```

#### SCC Relay Endpoint

```
com.amazonaws.vpce.ap-northeast-2.vpce-svc-0dc0e98a5800db5c4
```

{% hint style="info" %}
AWS Console → VPC → Endpoints → **"Find service by name"** 에 위 값을 붙여넣기 → **Verify service** 클릭
{% endhint %}

*출처: [Databricks regional endpoint service names](https://docs.databricks.com/aws/en/resources/ip-domain-region) · [Terraform: databricks_mws_vpc_endpoint](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_vpc_endpoint)*

### 전체 리전 VPC Endpoint Service Names

모든 리전 복사용 참조표:

| Region | Workspace (REST API) | SCC Relay |
|--------|---------------------|-----------|
| **ap-northeast-2** | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e` | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0dc0e98a5800db5c4` |
| ap-northeast-1 | `com.amazonaws.vpce.ap-northeast-1.vpce-svc-02691fd610d24fd64` | `com.amazonaws.vpce.ap-northeast-1.vpce-svc-02aa633bda3edbec0` |
| us-east-1 | `com.amazonaws.vpce.us-east-1.vpce-svc-09143d1e626de2f04` | `com.amazonaws.vpce.us-east-1.vpce-svc-00018a8c3ff62ffdf` |
| us-east-2 | `com.amazonaws.vpce.us-east-2.vpce-svc-041dc2b4d7796b8d3` | `com.amazonaws.vpce.us-east-2.vpce-svc-090a8fab0d73e39a6` |
| us-west-2 | `com.amazonaws.vpce.us-west-2.vpce-svc-0129f463fcfbc46c5` | `com.amazonaws.vpce.us-west-2.vpce-svc-0158114c0c730c3bb` |
| eu-central-1 | `com.amazonaws.vpce.eu-central-1.vpce-svc-081f78503812597f7` | `com.amazonaws.vpce.eu-central-1.vpce-svc-08e5dfca9572c85c4` |
| eu-west-1 | `com.amazonaws.vpce.eu-west-1.vpce-svc-0da6ebf1461278016` | `com.amazonaws.vpce.eu-west-1.vpce-svc-09b4eb2bc775f4e8c` |
| ap-southeast-1 | `com.amazonaws.vpce.ap-southeast-1.vpce-svc-02535b257fc253ff4` | `com.amazonaws.vpce.ap-southeast-1.vpce-svc-0557367c6fc1a0c5c` |

*전체 리전: [IP addresses and domains](https://docs.databricks.com/aws/en/resources/ip-domain-region)*

### Step 1: VPC Endpoint Subnet 생성

AWS Console → VPC → Subnets → Create subnet

#### 요구사항

| 항목 | 설정값 |
|------|--------|
| **VPC** | Databricks Compute VPC |
| **CIDR** | 최소 `/27` (예: `10.4.100.0/24`) |
| **용도** | VPC Endpoint 전용 (워크스페이스 서브넷과 분리) |

#### Route Table 설정

- **새 Route Table 생성** → VPC Endpoint Subnet에 연결
- **Local route만** 유지 — NAT GW route 추가하지 않음

| Destination | Target |
|-------------|--------|
| `10.4.0.0/16` (VPC CIDR) | local |

{% hint style="warning" %}
VPC Endpoint Subnet에는 NAT Gateway 라우트를 넣지 않음 — local 전용
{% endhint %}

### Step 2: VPC Endpoint Security Group

AWS Console → VPC → Security Groups → Create

규칙 — 양방향 TCP 포트 443, 2443, 6666:

**Inbound Rules:**

| Port | Protocol | Source | 용도 |
|------|----------|--------|------|
| **443** | TCP | VPC CIDR (예: `10.4.0.0/16`) | REST API (HTTPS) |
| **2443** | TCP | VPC CIDR | FIPS / Compliance |
| **6666** | TCP | VPC CIDR | SCC Relay |

**Outbound Rules:**

| Port | Protocol | Destination | 용도 |
|------|----------|-------------|------|
| **443** | TCP | VPC CIDR | REST API return |
| **2443** | TCP | VPC CIDR | FIPS return |
| **6666** | TCP | VPC CIDR | Relay return |

*참고: [PrivateLink security group requirements](https://docs.databricks.com/aws/en/security/network/classic/privatelink)*

### Step 3: AWS VPC Endpoint 생성

AWS Console → VPC → Endpoints → Create endpoint (x2)

#### Endpoint 1: Workspace (REST API)

| 항목 | 설정값 |
|------|--------|
| **Service category** | Other endpoint services |
| **Service name** | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e` |
| **VPC** | Compute VPC |
| **Subnets** | VPC Endpoint Subnet |
| **Security groups** | VPC Endpoint SG (443/2443/6666) |
| **Enable DNS name** | **Yes** (Enable private DNS names) |

#### Endpoint 2: SCC Relay

| 항목 | 설정값 |
|------|--------|
| **Service name** | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0dc0e98a5800db5c4` |
| 나머지 | Workspace Endpoint와 동일 설정 |

{% hint style="info" %}
"Verify service" 클릭 시 **"Service name verified"** 확인 후 진행. `private_dns_enabled = true` 필수
{% endhint %}

### Step 4: Databricks에 VPC Endpoint 등록

Account Console → Security → Networking → VPC endpoints

#### 절차 (2회 반복 — REST API, Relay 각각)

1. **Security** → **Networking** → **VPC endpoints** → **Register VPC endpoint**
2. 입력:
   - **VPC endpoint name**: 식별 이름 (예: `prod-rest-vpce`, `prod-relay-vpce`)
   - **VPC endpoint ID**: `vpce-xxxxxxxx` (AWS에서 생성한 ID)
   - **Region**: `ap-northeast-2`
3. **Register** 클릭

#### 이후: Network Configuration 생성 시 연결

- VPC Endpoint 등록 완료 후 → **Part 5의 Network 등록 단계**에서 Network Configuration 생성 시 VPC Endpoint를 지정
- Network Configuration 생성 화면에서 REST API / Dataplane relay Endpoint 선택

*참고: [Register VPC endpoints](https://docs.databricks.com/aws/en/security/network/classic/privatelink)*

### Step 5: Private Access Settings

Account Console → Security → Networking → Private access settings

#### 설정

1. **Add private access settings** 클릭
2. 입력:
   - **Name**: 식별 이름
   - **Region**: `ap-northeast-2`
   - **Public access**: 단계적 전환 권장

#### 접근 수준 옵션

| 설정 | Public access | Access level | 결과 |
|------|---|---|---|
| **하이브리드** (검증 기간) | Enabled | ACCOUNT | 퍼블릭 + PrivateLink 모두 허용 |
| **프라이빗 전용** | Disabled | ACCOUNT | 계정 내 모든 VPC Endpoint 허용 |
| **특정 Endpoint만** | Disabled | ENDPOINT | 지정된 Endpoint만 허용 |

{% hint style="warning" %}
처음에는 **Public access = Enabled**로 시작 → 검증 완료 후 **Disabled**로 전환 권장
{% endhint %}

*참고: [Private access settings](https://docs.databricks.com/aws/en/security/network/classic/privatelink) · [Terraform: databricks_mws_private_access_settings](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_private_access_settings)*

---

## Part 7. Frontend PrivateLink 구성 (옵션)

### Frontend PrivateLink — 왜 필요한가?

사용자 → Workspace 접근을 프라이빗하게 만듭니다.

| 구성 | 사용자 접근 경로 |
|------|---------------|
| **Backend만** | 사용자 → **인터넷** → Workspace → PrivateLink → Compute |
| **Backend + Frontend** | 사용자 → **VPN/DX** → Transit VPC → **PrivateLink** → Workspace → PrivateLink → Compute |

{% hint style="info" %}
**적용 시점**: VPN/DirectConnect로 AWS에 접근하는 고객, 퍼블릭 인터넷 접근 정책상 불가한 환경. End-to-End 프라이빗 연결 — 인터넷 경유 Zero
{% endhint %}

*참고: [Inbound PrivateLink](https://docs.databricks.com/aws/en/security/network/front-end/front-end-private-connect) · [PrivateLink DNS](https://docs.databricks.com/aws/en/security/network/classic/privatelink-dns)*

### Frontend — Backend과의 차이점

| 항목 | Backend | Frontend (추가분) |
|------|---------|-----------------|
| **VPC** | Compute VPC | **Transit VPC** (별도 또는 동일) |
| **VPC Endpoint** | 2개 (REST + Relay) | **1개** (REST API만) |
| **SG 포트** | 443, 2443, 6666 | **443만** |
| **DNS** | private DNS enabled | **Route 53 Private Hosted Zone** |
| **추가** | 없음 | **Route 53 Inbound Resolver** (On-prem) |

#### Single VPC vs Dual VPC

| 방식 | 설명 | 적합 시나리오 |
|------|------|-------------|
| **Single VPC** | Compute VPC에 Frontend도 배치, REST API Endpoint 겸용 | PoC, 소규모 |
| **Dual VPC** (권장) | Transit VPC(Frontend) + Compute VPC(Backend) 분리 | 프로덕션, 대규모 |

### Step 1: Transit VPC 생성

#### Transit VPC + Security Group

| 항목 | 설정값 |
|------|--------|
| **CIDR** | 예: `10.5.0.0/16` |
| **DNS hostnames / resolution** | 둘 다 **Enabled** |
| **Security Group Inbound** | TCP 443 from Corporate CIDR (예: `10.0.0.0/8`) |
| **Security Group Outbound** | TCP 443 to Corporate CIDR |

### Step 1b: VPC Endpoint 생성

AWS Console → VPC → Endpoints → Create endpoint

| 항목 | 설정값 |
|------|--------|
| **Service name** | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e` |
| **VPC** | Transit VPC |
| **Subnet** | Transit Endpoint Subnet |
| **Enable private DNS names** | **No** (Route 53으로 관리) |

{% hint style="warning" %}
Frontend Endpoint는 반드시 **Enable private DNS names = No**
{% endhint %}

### Step 2: Databricks 등록

Account Console에서 등록합니다.

#### VPC Endpoint 등록

1. **Security** → **Networking** → **VPC endpoints** → **Register VPC endpoint**
2. 입력:
   - **VPC endpoint name**: `prod-frontend-rest-vpce`
   - **VPC endpoint ID**: Transit VPC의 `vpce-xxxxxxxx`
   - **Region**: `ap-northeast-2`
3. **Register** 클릭

#### Private Access Settings — Allowed Endpoints 추가

- Frontend Endpoint도 **Allowed VPC endpoint IDs**에 추가 필요
- Public access = Disabled 전환 시 Backend + Frontend 모두 등록

### Step 3: Route 53 DNS 구성

Route 53 → Hosted zones → Create hosted zone (Private)

| 항목 | 설정값 |
|------|--------|
| **Domain name** | `cloud.databricks.com` |
| **Type** | Private hosted zone |
| **Associated VPC** | Transit VPC |

#### A Record (Alias) 추가

| Record name | Type | Alias Target |
|-------------|------|-------------|
| `<workspace-deployment-name>` | A (Alias) | Frontend VPC Endpoint |

DNS 흐름: `<ws>.cloud.databricks.com` → Private Hosted Zone → Endpoint Private IP

*참고: [PrivateLink DNS](https://docs.databricks.com/aws/en/security/network/classic/privatelink-dns)*

### Step 4: Route 53 Inbound Resolver

On-Premises에서 Private Hosted Zone 해석 (VPN/DX 사용 시):

| 항목 | 설정값 |
|------|--------|
| **VPC** | Transit VPC |
| **Security Group** | TCP/UDP 53 from Corporate Network |
| **IP addresses** | 2개+ (서로 다른 AZ) |

#### Corporate DNS Conditional Forwarder

| Domain | Forward To |
|--------|-----------|
| `*.cloud.databricks.com` | Resolver IP |
| `*.aws.databricksapps.com` | Resolver IP |

검증: `nslookup <ws>.cloud.databricks.com` → `10.x.x.x` 반환 시 정상

{% hint style="warning" %}
**SSO/Unified Login** 시 CNAME 추가: `accounts-pl-auth.privatelink.cloud.databricks.com`
{% endhint %}

### Frontend PrivateLink — 구성 체크리스트

놓치기 쉬운 항목들:

| # | 체크 항목 |
|---|----------|
| 1 | Transit VPC DNS Hostnames/Resolution 활성화 |
| 2 | VPC Endpoint 생성 (REST API, port 443) |
| 3 | Enable private DNS names = **No** |
| 4 | Databricks Account Console에 VPC Endpoint 등록 |
| 5 | Route 53 Private Hosted Zone 생성 (`cloud.databricks.com`) |
| 6 | A Record (Alias) → VPC Endpoint 매핑 |
| 7 | Route 53 Inbound Resolver 생성 (On-prem 접근 시) |
| 8 | Corporate DNS Conditional Forwarder 설정 |
| 9 | `nslookup` 검증 — Private IP 반환 확인 |
| 10 | Private Access Settings — Public access = Disabled 전환 |
| 11 | SSO/Unified Login CNAME 추가 (필요시) |
| 12 | `*.aws.databricksapps.com` DNS 포워딩 (Apps 사용시) |

---

## Part 8. Workspace 생성

### Workspace 생성 — Account Console

accounts.cloud.databricks.com → Workspaces → Create workspace

#### 입력 항목

| 항목 | 설정값 |
|------|--------|
| **Workspace name** | 식별 이름 (예: `prod-workspace-apne2`) |
| **Region** | `ap-northeast-2` (Seoul) |
| **Credential configuration** | Part 3에서 생성한 Credential 선택 |
| **Storage configuration** | Part 4에서 생성한 Storage 선택 |
| **Network configuration** | Part 5-6에서 생성한 Network 선택 (PrivateLink 포함) |
| **Private access settings** | Part 6에서 생성한 PAS 선택 |
| **Pricing tier** | **Enterprise** (PrivateLink 사용 시 필수) |
| **CMK** (선택) | Managed services CMK / Storage CMK |

**Create workspace** 클릭 → 프로비저닝 시작

*참고: [Create a workspace](https://docs.databricks.com/aws/en/admin/account-settings-e2/workspaces) · [Terraform: databricks_mws_workspaces](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_workspaces)*

### Workspace 생성 후 확인

프로비저닝 완료까지 대기합니다.

#### 상태 확인

| 상태 | 의미 |
|------|------|
| **PROVISIONING** | 생성 중 |
| **RUNNING** | 정상 — 사용 가능 |
| **FAILED** | 실패 — 에러 메시지 확인 |

#### 소요 시간

| 단계 | 시간 |
|------|------|
| Workspace 프로비저닝 | ~5-7분 |
| PrivateLink DNS 전파 | +10-20분 |
| **클러스터 생성 가능** | 프로비저닝 후 **최소 20분 대기** |

{% hint style="warning" %}
PrivateLink 워크스페이스는 프로비저닝 완료 후 **20분 대기** 필요 — DNS 전파 시간. 로컬 DNS 캐시 플러시: `sudo killall -HUP mDNSResponder` (macOS) 또는 `ipconfig /flushdns` (Windows)
{% endhint %}

### Unity Catalog Storage Credential

Workspace와 별개로 UC용 IAM Role이 필요합니다.

#### Trust Policy Principals

| Principal | ARN |
|-----------|-----|
| **UC Master Role** | `arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL` |
| **Self-Assume** | `arn:aws:iam::<YOUR-ACCOUNT>:role/<THIS-ROLE>` |

*ExternalId: Databricks Account UUID*

#### 필요 Permission

| 서비스 | Actions |
|--------|---------|
| **S3** | GetObject, PutObject, DeleteObject, ListBucket (`/unity-catalog/*`) |
| **KMS** | Decrypt, Encrypt, GenerateDataKey (CMK 사용 시) |
| **STS** | AssumeRole (self-assume) |
| **SNS/SQS** | File Events 자동화 (권장) |

*참고: [Storage credential for AWS](https://docs.databricks.com/aws/en/connect/unity-catalog/storage-credentials) · [Managed storage](https://docs.databricks.com/aws/en/data-governance/unity-catalog/create-metastore)*

---

### External Location — File Events IAM 권한

#### 개요

External Location을 생성하면 **File Events가 기본적으로 활성화**됩니다. File Events는 S3 버킷의 파일 변경 사항을 SQS/SNS를 통해 Databricks에 알려주는 기능으로, Auto Loader (File Notification 모드)와 Job File-Arrival Trigger에서 사용됩니다.

{% hint style="warning" %}
External Location 생성 시 **File Events가 기본 활성화**되어 있습니다. IAM Role에 SQS/SNS 권한이 없으면 **Test Connection의 "File Events Read" 체크가 실패**합니다. File Events가 불필요한 경우 External Location → Advanced Options에서 비활성화할 수 있습니다.
{% endhint %}

#### SQS/SNS 권한이 필요한 이유

Databricks는 File Events를 위해 `csms-*` prefix가 붙은 SQS Queue와 SNS Topic을 자동 생성합니다. 이 리소스를 생성·관리하려면 IAM Role에 해당 권한이 포함되어야 합니다.

#### File Events 필요 여부

| 기능 | File Events 필요 |
|------|-----------------|
| 기본 S3 읽기/쓰기 | 불필요 |
| Auto Loader (Directory Listing 모드) | 불필요 |
| Auto Loader (File Notification 모드) | **필수** |
| Job File-Arrival Trigger | **필수** |

#### 전체 IAM Policy (S3 + SQS/SNS + STS Self-Assume)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:GetBucketNotification",
        "s3:PutBucketNotification"
      ],
      "Resource": [
        "arn:aws:s3:::<YOUR-BUCKET>",
        "arn:aws:s3:::<YOUR-BUCKET>/*"
      ]
    },
    {
      "Sid": "SNSAccess",
      "Effect": "Allow",
      "Action": [
        "sns:CreateTopic",
        "sns:TagResource",
        "sns:Publish",
        "sns:Subscribe",
        "sns:GetTopicAttributes",
        "sns:SetTopicAttributes",
        "sns:ListSubscriptionsByTopic"
      ],
      "Resource": "arn:aws:sns:*:*:csms-*"
    },
    {
      "Sid": "SQSAccess",
      "Effect": "Allow",
      "Action": [
        "sqs:CreateQueue",
        "sqs:DeleteMessage",
        "sqs:ReceiveMessage",
        "sqs:SendMessage",
        "sqs:GetQueueUrl",
        "sqs:GetQueueAttributes",
        "sqs:SetQueueAttributes",
        "sqs:TagQueue"
      ],
      "Resource": "arn:aws:sqs:*:*:csms-*"
    },
    {
      "Sid": "STSSelfAssume",
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::<YOUR-ACCOUNT>:role/<THIS-ROLE>"
    }
  ]
}
```

{% hint style="info" %}
`csms-*` prefix는 Databricks가 자동 생성·관리하는 리소스 (Customer-Side Managed Service)를 의미합니다. Resource scope를 `csms-*`로 제한하면 Databricks 관련 리소스에만 권한이 부여됩니다.
{% endhint %}

#### File Events 비활성화 방법

File Events가 불필요한 경우 (예: Directory Listing 모드만 사용):

1. Databricks Workspace에서 **Catalog → External Locations** 이동
2. 해당 External Location 선택
3. **Advanced Options** → **File Events** 비활성화

*참고: [External Location manual setup (S3)](https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-storage/s3/s3-external-location-manual)*

---

## Unity Catalog Metastore 구성

### Metastore 개요

Metastore는 Unity Catalog의 최상위 컨테이너로, 데이터 거버넌스의 기본 단위입니다. **리전당 1개의 Metastore**가 존재하며, 해당 리전의 모든 Workspace가 공유합니다.

{% hint style="info" %}
이미 동일 리전(예: `ap-northeast-2`)에 Metastore가 존재하면 새로 생성할 필요 없이 기존 Metastore에 Workspace를 할당하면 됩니다.
{% endhint %}

### 사전 준비

| 항목 | 설명 |
|------|------|
| **UC 전용 S3 Bucket** | Metastore 관리 데이터 저장용 (Root Storage와 별도) |
| **UC IAM Role** | Self-assume + Databricks UC Master Role trust 설정 |

#### UC IAM Role Trust Policy 핵심

- **UC Master Role** (`arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL`)을 Principal로 신뢰
- **Self-assume** — 동일 Role ARN을 Principal에 추가 (AssumeRole 권한)
- **ExternalId**: Databricks Account UUID

### Metastore 생성 절차

Account Console에서 생성합니다.

1. **accounts.cloud.databricks.com** 로그인
2. 좌측 메뉴: **Catalog** → **Create metastore**
3. 입력:
   - **Name**: 식별 이름 (예: `apne2-metastore`)
   - **Region**: `ap-northeast-2` (Workspace와 동일 리전)
   - **S3 path**: UC 전용 S3 Bucket 경로 (예: `s3://my-uc-metastore-bucket/unity-catalog`)
   - **IAM Role ARN**: UC IAM Role ARN
4. **Create** 클릭

### Workspace에 Metastore 할당

1. Account Console → **Catalog** → 생성한 Metastore 선택
2. **Assign to workspace** 클릭
3. 할당할 Workspace 선택 → **Assign**

{% hint style="warning" %}
1개 Workspace는 **1개 Metastore에만** 할당 가능합니다. 할당 변경 시 기존 데이터 접근 권한이 초기화될 수 있으므로 주의하세요.
{% endhint %}

*참고: [Create a Unity Catalog metastore](https://docs.databricks.com/aws/en/data-governance/unity-catalog/create-metastore)*

---

## Serverless Networking — NCC (Network Connectivity Configuration)

### NCC 개요

NCC(Network Connectivity Configuration)는 Serverless Compute의 네트워크 제어를 위한 **Account-level 구성**입니다. Serverless SQL Warehouse, Serverless Notebook 등이 외부 리소스에 프라이빗하게 접근해야 할 때 사용합니다.

{% hint style="info" %}
Classic Compute(고객 VPC)와 달리, Serverless Compute는 Databricks 관리 VPC에서 실행됩니다. NCC를 통해 Serverless 환경에서도 프라이빗 연결을 구성할 수 있습니다.
{% endhint %}

### NCC 제한 사항

| 항목 | 제한 |
|------|------|
| **리전당 최대 NCC 수** | 10개 |
| **NCC당 최대 Workspace 수** | 50개 |
| **S3 Private Endpoint** | 리전당 최대 30개 (S3 bucket name 지정) |
| **VPC Resource Endpoint (via NLB)** | 리전당 최대 100개 |

### NCC 구성 절차

Account Console → Security → Networking → Network connectivity configurations

#### Step 1: NCC 생성

1. **Network connectivity configurations** → **Create**
2. 입력:
   - **Name**: 식별 이름 (예: `apne2-serverless-ncc`)
   - **Region**: `ap-northeast-2`
3. **Create** 클릭

#### Step 2: Private Endpoint Rule 추가

NCC 생성 후 프라이빗 엔드포인트 규칙을 추가합니다.

**S3 Private Endpoint:**
- **Add private endpoint rule** → S3 유형 선택
- S3 Bucket name 지정 (예: `my-data-bucket`)
- Serverless Compute에서 해당 S3 Bucket으로의 프라이빗 접근 허용

**VPC Resource Endpoint (NLB 경유):**
- 고객 VPC 내 리소스(RDS, Kafka 등)에 접근 시 사용
- NLB(Network Load Balancer) ARN 지정

#### Step 3: Workspace에 NCC 연결

1. Account Console → **Workspaces** → 해당 Workspace 선택
2. **Update** → **Network connectivity configuration** 항목에서 NCC 선택
3. **Confirm update**

{% hint style="warning" %}
NCC를 Workspace에 연결/변경하면 Serverless Compute 재시작이 필요할 수 있습니다.
{% endhint %}

*참고: [Serverless private connectivity](https://docs.databricks.com/aws/en/security/network/serverless-network-security/serverless-private-connectivity)*

---

## 주의사항 & 트러블슈팅

### IAM Role 등록 실패

- IAM Role 생성 직후 Databricks 등록 시 **eventual consistency** 문제
- **10~30초 대기 후 재시도** (Terraform 사용 시 `time_sleep` 리소스)

### Network 수정 시 3단계 프로세스

1. 새 Network Configuration 생성
2. Workspace에서 새 Network로 교체
3. 기존 Network Configuration 삭제
- *직접 수정 → `INVALID_STATE` 에러*

### PrivateLink 워크스페이스 접근 불가

- DNS 캐시 플러시: `sudo killall -HUP mDNSResponder` / `ipconfig /flushdns`
- `nslookup <workspace>.cloud.databricks.com` → Private IP 확인
- VPC Endpoint 상태: `available` 확인 (AWS Console → VPC → Endpoints)
- Security Group: 443, 6666 양방향 확인

---

## 기존 Workspace에 PrivateLink 추가

### 개요

이미 운영 중인 Workspace에 PrivateLink를 사후 추가하는 절차입니다. 초기에 PrivateLink 없이 생성한 Workspace를 프라이빗 연결로 전환할 때 사용합니다.

{% hint style="warning" %}
**기존 Network Configuration은 직접 수정 불가** — VPC Endpoint를 포함한 새 Network Configuration을 생성한 후 Workspace에서 교체해야 합니다.
{% endhint %}

### 절차

#### Step 1: AWS VPC Endpoint 생성

AWS Console → VPC → Endpoints → Create endpoint

- **REST API Endpoint**: `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e`
- **SCC Relay Endpoint**: `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0dc0e98a5800db5c4`
- 설정 방법은 Part 6 (Backend PrivateLink 구성) 참고

#### Step 2: Databricks에 VPC Endpoint 등록

Account Console → Security → Networking → VPC endpoints

1. **Register VPC endpoint** 클릭
2. REST API, SCC Relay 각각 등록 (VPC Endpoint ID 입력)

#### Step 3: 새 Network Configuration 생성

Account Console → Security → Networking → Classic network configurations

1. **Add network configuration** 클릭
2. 기존 VPC, Subnet, Security Group 정보 입력
3. **VPC Endpoints** 항목에서 Step 2에서 등록한 REST API / Dataplane relay Endpoint 선택
4. **Add** 클릭 → 새 Network Configuration ID 생성

#### Step 4: Private Access Settings 생성

Account Console → Security → Networking → Private access settings

1. **Add private access settings** 클릭
2. Region, Public access 설정 (초기에는 **Public access = Enabled** 권장)

#### Step 5: Workspace 업데이트

Account Console → Workspaces → 해당 Workspace 선택

1. **Update** 클릭
2. **Network configuration** → Step 3에서 생성한 새 Network Configuration 선택
3. **Private access settings** → Step 4에서 생성한 설정 선택
4. **Confirm update** 클릭
5. 프로비저닝 시작 (~5-10분 소요)

{% hint style="warning" %}
**변경 중 클러스터 및 실행 중인 작업이 중단됩니다.** 반드시 유지보수 윈도우(maintenance window)에 수행하세요. 사전에 모든 클러스터를 종료하고 실행 중인 Job을 중지하는 것을 권장합니다.
{% endhint %}

{% hint style="info" %}
업데이트 완료 후 PrivateLink DNS 전파까지 추가로 10-20분이 소요될 수 있습니다. `nslookup <workspace>.cloud.databricks.com`으로 Private IP 반환을 확인한 후 접속하세요.
{% endhint %}

*참고: [Update a workspace](https://docs.databricks.com/aws/en/admin/account-settings-e2/workspaces)*

---

## 구성 완료 체크리스트

전체 과정 최종 확인:

| # | 단계 | AWS 리소스 | Databricks 등록 |
|---|------|-----------|----------------|
| 1 | Marketplace 구독 | AWS Marketplace 구독 | Databricks 계정 생성 |
| 2 | Credential | IAM Cross-Account Role | Credential Configuration |
| 3 | Storage | S3 Bucket + Bucket Policy | Storage Configuration |
| 4 | Network | VPC + 2 Private Subnets + SG | Network Configuration |
| 5 | Backend PL | 2x VPC Endpoints (REST + Relay) | VPC Endpoint 등록 + Network 연결 |
| 6 | Access Settings | — | Private Access Settings |
| 7 | Workspace | — | Workspace 생성 (RUNNING 확인) |
| 8 | [옵션] Frontend | Transit VPC + 1x Endpoint + R53 | VPC Endpoint 등록 |
| 9 | UC Storage | IAM Role + S3 | Storage Credential |
| 10 | 최종 검증 | — | 브라우저 접속 + 클러스터 생성 |

---

## Appendix: Terraform 자동화

### Terraform으로 자동화하기

위 매뉴얼 과정을 IaC로 전환할 수 있습니다.

#### Provider — Account-Level (MWS) + AWS

```hcl
provider "databricks" {
  alias = "mws"
  host  = "https://accounts.cloud.databricks.com"
  account_id = var.databricks_account_id
  client_id = var.client_id       # Service Principal OAuth
  client_secret = var.client_secret
}
```

### Terraform 리소스 매핑

AWS Console 작업 → Terraform Resource:

| AWS Console 작업 | Terraform Resource |
|-----------------|-------------------|
| IAM Role 생성 | `aws_iam_role` + `aws_iam_role_policy` |
| S3 Bucket 생성 | `aws_s3_bucket` + `aws_s3_bucket_policy` |
| VPC/Subnet/SG | `aws_vpc` / `aws_subnet` / `aws_security_group` |
| VPC Endpoint | `aws_vpc_endpoint` |
| Credential 등록 | `databricks_mws_credentials` |
| Storage 등록 | `databricks_mws_storage_configurations` |
| Network 등록 | `databricks_mws_networks` |
| VPC Endpoint 등록 | `databricks_mws_vpc_endpoint` |
| Private Access | `databricks_mws_private_access_settings` |
| Workspace | `databricks_mws_workspaces` |

### Terraform Helper Data Sources

Policy JSON 자동 생성 — 매뉴얼 복사-붙여넣기 실수 방지:

| Data Source | 용도 |
|-------------|------|
| `databricks_aws_assume_role_policy` | Trust Policy JSON 생성 |
| `databricks_aws_crossaccount_policy` | IAM Permission Policy JSON 생성 (`customer`/`managed`/`restricted`) |
| `databricks_aws_bucket_policy` | S3 Bucket Policy JSON 생성 |

```hcl
data "databricks_aws_crossaccount_policy" "this" {
  provider    = databricks.mws
  policy_type = "customer"
}
```

*참고: [crossaccount_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_crossaccount_policy) · [assume_role_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_assume_role_policy) · [bucket_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_bucket_policy)*

### Terraform 리소스 의존성 흐름

전체 Dependency Chain:

```
IAM Role → databricks_mws_credentials ─────────┐
                                                 │
S3 Bucket → databricks_mws_storage_configs ─────┤
                                                 │
VPC/Subnet/SG                                    │
  ├─ aws_vpc_endpoint(REST) → mws_vpc_endpoint ┐│
  ├─ aws_vpc_endpoint(Relay)→ mws_vpc_endpoint ┤│
  └─ databricks_mws_networks(vpc_endpoints) ────┤
                                                 │
databricks_mws_private_access_settings ─────────┤
                                                 ▼
                        databricks_mws_workspaces
```

### Terraform 공식 예제 & 참고

#### GitHub 저장소

| 예제 | 설명 |
|------|------|
| `aws-workspace-basic` | 기본 워크스페이스 |
| `aws-databricks-modular-privatelink` | **PrivateLink 모듈화 구성** |
| `aws-databricks-uc` | Unity Catalog 포함 |
| `aws-workspace-with-firewall` | Egress 방화벽 포함 |
| `aws-exfiltration-protection` | 데이터 유출 방지 |

- **Examples**: [github.com/databricks/terraform-databricks-examples](https://github.com/databricks/terraform-databricks-examples)
- **SRA**: [github.com/databricks/terraform-databricks-sra](https://github.com/databricks/terraform-databricks-sra)

---

## 참고 문서

### Databricks 공식 문서

- **아키텍처 개요**: [High-Level Architecture](https://docs.databricks.com/aws/en/getting-started/high-level-architecture)
- **Credential 구성**: [Create a cross-account IAM role](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials)
- **Storage 구성**: [Configure storage](https://docs.databricks.com/aws/en/admin/account-settings-e2/storage)
- **Network 구성**: [Configure network](https://docs.databricks.com/aws/en/admin/account-settings-e2/networks)
- **Workspace 생성**: [Create a workspace](https://docs.databricks.com/aws/en/admin/account-settings-e2/workspaces)
- **PrivateLink 구성**: [Enable PrivateLink](https://docs.databricks.com/aws/en/security/network/classic/privatelink)
- **PrivateLink 개념**: [PrivateLink Concepts](https://docs.databricks.com/aws/en/security/network/classic/privatelink-concepts)
- **PrivateLink DNS**: [DNS Config](https://docs.databricks.com/aws/en/security/network/classic/privatelink-dns)
- **Frontend PrivateLink**: [Inbound PrivateLink](https://docs.databricks.com/aws/en/security/network/front-end/front-end-private-connect)
- **리전별 Endpoint**: [IP & Domain Info](https://docs.databricks.com/aws/en/resources/ip-domain-region)
- **UC Storage Credential**: [Storage Credentials](https://docs.databricks.com/aws/en/connect/unity-catalog/storage-credentials)

### Terraform Provider 문서

- **Provider 홈**: [registry.terraform.io/providers/databricks/databricks](https://registry.terraform.io/providers/databricks/databricks/latest)
- **mws_credentials**: [Docs](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_credentials)
- **mws_storage_configurations**: [Docs](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_storage_configurations)
- **mws_networks**: [Docs](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_networks)
- **mws_vpc_endpoint**: [Docs](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_vpc_endpoint)
- **mws_private_access_settings**: [Docs](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_private_access_settings)
- **mws_workspaces**: [Docs](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_workspaces)
- **PrivateLink Guide**: [Terraform AWS PrivateLink Guide](https://registry.terraform.io/providers/databricks/databricks/latest/docs/guides/aws-private-link-workspace)

### GitHub 예제 저장소

- **Terraform Examples**: [github.com/databricks/terraform-databricks-examples](https://github.com/databricks/terraform-databricks-examples)
- **Security Ref Architecture**: [github.com/databricks/terraform-databricks-sra](https://github.com/databricks/terraform-databricks-sra)

*이 가이드는 Databricks 공식 문서와 Terraform Provider 소스 기반으로 검증되었습니다 · 2026년 3월*
