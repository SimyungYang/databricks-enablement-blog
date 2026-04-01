# Credential 구성

## Cross-Account IAM Role — 개요

Databricks가 고객 AWS 계정에 EC2를 프로비저닝하기 위한 역할입니다.

### AWS Console 작업 순서

1. **IAM → Roles → Create role** 에서 Cross-Account Role 생성
2. Trust Policy 설정 (Databricks AWS 계정 신뢰)
3. Permission Policy 부여 (EC2/VPC 관련 권한)
4. **Account Console**→ **Cloud resources**→ **Credential configuration**→ **Add** 에서 Role ARN 등록

*참고: [Create a cross-account IAM role](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials)*

## Cross-Account IAM Role — Policy 유형

고객 VPC 관리 방식에 따라 3가지 정책:

| Policy Type | 설명 | 사용 시점 |
|---|---|---|
| `managed` | Databricks가 VPC 생성/관리 | PoC, 빠른 시작 |
| `customer` | **고객이 VPC 생성**, Databricks는 EC2만 관리 | **프로덕션 권장**|
| `restricted` | customer + ARN 조건 제한 (VPC ID, SG ID 등) | 엄격 보안 요건 |

*참고: [Terraform: databricks_aws_crossaccount_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_crossaccount_policy)*

## Cross-Account IAM Role — Trust Policy

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
| **Principal**| `414351767826` | Databricks Standard AWS Account |
| **ExternalId**| Databricks Account UUID | Account Console 상단에서 확인 |

*참고: [Trust policy](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials) · [Terraform: databricks_aws_assume_role_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_assume_role_policy)*

## Cross-Account IAM Role — Permission Policy (전체 JSON)

customer 타입 (Customer-Managed VPC용):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EC2Actions",
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:CreateVolume",
        "ec2:DeleteVolume",
        "ec2:AttachVolume",
        "ec2:DetachVolume",
        "ec2:CreateTags",
        "ec2:DeleteTags",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups",
        "ec2:RequestSpotInstances",
        "ec2:CancelSpotInstanceRequests",
        "ec2:DescribeSpotInstanceRequests",
        "ec2:DescribeSpotPriceHistory"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SpotServiceLinkedRole",
      "Effect": "Allow",
      "Action": [
        "iam:CreateServiceLinkedRole",
        "iam:PutRolePolicy"
      ],
      "Resource": "arn:aws:iam::*:role/aws-service-role/spot.amazonaws.com/AWSServiceRoleForEC2Spot"
    }
  ]
}
```

{% hint style="info" %}
Terraform `databricks_aws_crossaccount_policy` data source를 사용하면 최신 Policy JSON을 자동 생성할 수 있습니다.
{% endhint %}

*참고: [Cross-account policy](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials) · [Terraform: databricks_aws_crossaccount_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_crossaccount_policy)*

## Credential 등록 — Account Console

Databricks Account Console에서 등록합니다.

### 절차

1. **accounts.cloud.databricks.com** 로그인
2. 좌측 메뉴: **Cloud resources**→ **Credential configuration** 탭
3. **Add credential configuration** 클릭
4. 입력:
   - **Credential configuration name**: 식별 이름 (예: `prod-crossaccount-cred`)
   - **Role ARN**: 위에서 생성한 IAM Role ARN (예: `arn:aws:iam::123456789012:role/databricks-crossaccount`)
5. **Add** 클릭

### 결과

- **Credential ID** 생성됨 → Workspace 생성 시 사용

{% hint style="warning" %}
IAM Role 생성 직후 등록 시 **eventual consistency** 문제로 실패할 수 있음 — 10~30초 대기 후 재시도
{% endhint %}
