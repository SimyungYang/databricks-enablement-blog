# 사전 준비

## 개요

Databricks on AWS를 구성하기 전에 AWS 계정과 Databricks 계정 모두에서 필요한 선행 조건을 충족해야 합니다. 이 페이지는 누락되기 쉬운 항목들을 상세히 다룹니다.

## 사전 준비 체크리스트

| # | 항목 | 필수 | 확인 방법 |
|---|------|:----:|-----------|
| 1 | AWS IAM 권한 (Role, S3, VPC 생성) | O | IAM Console → 사용자 정책 확인 |
| 2 | STS 엔드포인트 활성화 (us-west-2) | O | IAM Console → Account Settings |
| 3 | SCP에서 sts:AssumeRole 허용 | O | Organizations → Policies |
| 4 | Databricks Account Admin 권한 | O | Account Console → User Management |
| 5 | Enterprise 티어 (PrivateLink 시) | 조건부 | Account Console → Settings |
| 6 | Service Principal (자동화 시) | 조건부 | Account Console → User Management |

## AWS 계정 요구사항

### 1. IAM 권한

Databricks 인프라를 구성하는 AWS 사용자/역할에 다음 권한이 필요합니다.

| 서비스 | 필요 권한 | 용도 |
|--------|-----------|------|
| **IAM** | `iam:CreateRole`, `iam:PutRolePolicy`, `iam:AttachRolePolicy` | Cross-account Role 생성 |
| **S3** | `s3:CreateBucket`, `s3:PutBucketPolicy`, `s3:PutEncryptionConfiguration` | Root Storage 버킷 생성 |
| **VPC** | `ec2:CreateVpc`, `ec2:CreateSubnet`, `ec2:CreateSecurityGroup` | 네트워크 구성 |
| **VPC Endpoint** | `ec2:CreateVpcEndpoint` | PrivateLink 구성 시 |
| **KMS** | `kms:CreateKey`, `kms:CreateAlias` | Customer Managed Key 사용 시 |

{% hint style="info" %}
**간편 설정**: 초기 구성 시에는 `AdministratorAccess` 정책을 임시로 부여하고, 구성 완료 후 최소 권한 원칙에 맞게 축소하는 것을 권장합니다.
{% endhint %}

### 2. STS 엔드포인트 활성화

Databricks는 AWS STS(Security Token Service)를 사용하여 Cross-account Role을 Assume합니다. **배포 리전과 무관하게**`us-west-2` 리전의 STS Regional Endpoint가 활성화되어 있어야 합니다.

#### 확인 및 활성화 방법

1. AWS Console 로그인 → **IAM** 서비스 이동
2. 좌측 메뉴 하단의 "** Account settings**" 클릭
3. "** Security Token Service (STS)**" 섹션에서 "** Endpoints**" 확인
4. `US West (Oregon) — us-west-2` 항목을 찾아 상태 확인
5. **Inactive** 상태라면 "** Activate**" 클릭

{% hint style="danger" %}
**중요**: `us-west-2`의 STS 엔드포인트가 비활성화되어 있으면 Workspace 생성이 실패합니다. 오류 메시지가 STS를 직접 언급하지 않아 원인 파악이 어려울 수 있으므로, 반드시 사전에 확인하세요.
{% endhint %}

{% hint style="info" %}
**추가로**, 실제 Workspace를 배포할 리전 (예: `ap-northeast-2`)의 STS 엔드포인트도 활성화해야 합니다. Global STS endpoint는 기본 활성화이지만, Regional endpoint는 수동 활성화가 필요합니다.
{% endhint %}

### 3. SCP(Service Control Policy) 확인

AWS Organizations를 사용하는 경우, SCP가 Databricks 운영에 필요한 API 호출을 차단하고 있지 않은지 확인합니다.

#### 확인 방법

1. AWS Console → **AWS Organizations** 이동
2. 좌측 메뉴에서 "** Policies**" → "** Service control policies**" 클릭
3. 적용 중인 SCP 목록 확인 → 각 정책의 **Statement** 검토

#### 필수 허용 항목

다음 API 호출이 SCP에 의해 **Deny** 되지 않아야 합니다:

```json
{
  "Effect": "Allow",
  "Action": [
    "sts:AssumeRole",
    "sts:GetCallerIdentity",
    "s3:*",
    "ec2:*",
    "iam:CreateRole",
    "iam:PassRole"
  ],
  "Resource": "*"
}
```

{% hint style="warning" %}
SCP에서 특정 리전만 허용하는 정책(`aws:RequestedRegion` 조건)이 있다면, Databricks가 사용하는 리전(배포 리전 + `us-west-2`)이 모두 포함되어야 합니다.
{% endhint %}

## Databricks 계정 요구사항

### 4. Account Admin 권한

Workspace 생성, 네트워크 구성, Unity Catalog 설정 등 Account-level 작업을 수행하려면 **Account Admin** 역할이 필요합니다.

- Marketplace 구독으로 계정을 생성한 경우: 최초 등록 이메일이 자동으로 Account Admin
- 기존 계정: Account Console → **User Management**→ 사용자 선택 → **Roles** 탭에서 확인

### 5. Enterprise 티어 (조건부)

| 기능 | Standard | Premium | Enterprise |
|------|:--------:|:-------:|:----------:|
| 기본 Workspace | O | O | O |
| Unity Catalog | O | O | O |
| PrivateLink | X | X | **O** |
| Customer Managed Keys | X | X | **O** |
| IP Access Lists | X | O | O |

{% hint style="warning" %}
**PrivateLink** 또는 **Customer Managed Key (CMK)** 를 사용하려면 반드시 **Enterprise 티어** 가 필요합니다. 티어 변경은 Databricks 영업팀에 문의하세요.
{% endhint %}

### 6. Service Principal 생성 (자동화 시)

Terraform, API 호출 등 자동화 도구로 Databricks를 관리할 때는 Service Principal을 사용합니다.

#### 생성 절차

1. Account Console 로그인 → **User Management** 메뉴 이동
2. "** Service principals**" 탭 클릭
3. "** Add service principal**" 클릭
4. **Name** 입력 (예: `sp-terraform-admin`)
5. **Add** 클릭 → Service Principal ID 생성됨

#### OAuth M2M 인증 설정

Service Principal에 대한 프로그래밍 방식 인증을 위해 OAuth M2M(Machine-to-Machine) 토큰을 설정합니다.

1. 생성된 Service Principal 클릭 → **Secrets** 탭 이동
2. "** Generate secret**" 클릭
3. **Client ID** 와 **Client Secret** 복사 및 안전한 곳에 저장

{% hint style="danger" %}
**Client Secret은 생성 시 한 번만 표시됩니다.** 닫으면 다시 확인할 수 없으므로 즉시 안전한 곳(AWS Secrets Manager, HashiCorp Vault 등)에 저장하세요.
{% endhint %}

4. Service Principal에 **Account Admin** 역할 부여 (필요 시):
   - **Roles** 탭 → **Account admin** 체크

## Databricks AWS Account ID (IAM Trust 설정용)

Cross-account IAM Role 생성 시, Trust Policy에 Databricks 측 AWS Account ID를 지정해야 합니다.

| 환경 | Account ID | 용도 |
|------|-----------|------|
| **Standard AWS** | `414351767826` | 대부분의 상용 환경 |
| **AWS GovCloud** | `044793339203` | 미국 정부 기관 |
| **GovCloud DoD** | `170661010020` | 미국 국방부 |

#### Trust Policy 예시

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::414351767826:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "<Databricks-Account-ID>"
        }
      }
    }
  ]
}
```

{% hint style="info" %}
`<Databricks-Account-ID>`는 Account Console → **Settings** 에서 확인할 수 있는 UUID 형식의 값입니다 (AWS Account ID와 다릅니다).
{% endhint %}

## 최종 체크리스트

구성 시작 전 아래 항목을 모두 확인하세요:

- [ ] AWS IAM 사용자에게 충분한 권한이 있는가?
- [ ] `us-west-2` STS Regional Endpoint가 활성화되어 있는가?
- [ ] 배포 리전 STS Regional Endpoint가 활성화되어 있는가?
- [ ] SCP에서 필요한 API 호출이 차단되지 않는가?
- [ ] Databricks Account Console에 Account Admin으로 로그인 가능한가?
- [ ] PrivateLink 사용 시 Enterprise 티어인가?
- [ ] 자동화 사용 시 Service Principal 및 OAuth Secret이 준비되었는가?

*참고: [Databricks account IDs for AWS trust policy](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials) · [Service Principals](https://docs.databricks.com/aws/en/admin/users-groups/service-principals)*
