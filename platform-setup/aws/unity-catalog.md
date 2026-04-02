# Unity Catalog

## Unity Catalog Storage Credential

Workspace와 별개로 UC용 IAM Role이 필요합니다.

### Trust Policy (전체 JSON)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL",
          "arn:aws:iam::<YOUR-AWS-ACCOUNT>:role/<THIS-ROLE-NAME>"
        ]
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "<DATABRICKS-ACCOUNT-ID>"
        }
      }
    }
  ]
}
```

{% hint style="info" %}
- `<YOUR-AWS-ACCOUNT>`: 고객 AWS Account ID
- `<THIS-ROLE-NAME>`: 이 IAM Role 자체 이름 (self-assume)
- `<DATABRICKS-ACCOUNT-ID>`: Databricks Account UUID (Account Console 상단에서 확인)
{% endhint %}

### Permission Policy (전체 JSON)

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
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::<UC-BUCKET>/unity-catalog/*",
        "arn:aws:s3:::<UC-BUCKET>"
      ]
    },
    {
      "Sid": "KMSAccess",
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:GenerateDataKey*"
      ],
      "Resource": ["arn:aws:kms:<REGION>:<ACCOUNT>:key/<KMS-KEY-ID>"]
    },
    {
      "Sid": "SelfAssume",
      "Effect": "Allow",
      "Action": ["sts:AssumeRole"],
      "Resource": ["arn:aws:iam::<YOUR-AWS-ACCOUNT>:role/<THIS-ROLE-NAME>"]
    }
  ]
}
```

{% hint style="warning" %}
- KMS Statement는 S3 버킷이 KMS 암호화를 사용하는 경우에만 필요
- Self-Assume은 2025년 1월부터 필수
- File Events (SNS/SQS) 권한은 다음 섹션 참조
{% endhint %}

*참고: [Storage credential for AWS](https://docs.databricks.com/aws/en/connect/unity-catalog/storage-credentials) · [Managed storage](https://docs.databricks.com/aws/en/data-governance/unity-catalog/create-metastore)*

---

## External Location — File Events IAM 권한

### 개요

External Location을 생성하면 **File Events가 기본적으로 활성화** 됩니다. File Events는 S3 버킷의 파일 변경 사항을 SQS/SNS를 통해 Databricks에 알려주는 기능으로, Auto Loader (File Notification 모드)와 Job File-Arrival Trigger에서 사용됩니다.

{% hint style="warning" %}
External Location 생성 시 **File Events가 기본 활성화** 되어 있습니다. IAM Role에 SQS/SNS 권한이 없으면 **Test Connection의 "File Events Read" 체크가 실패** 합니다. File Events가 불필요한 경우 External Location → Advanced Options에서 비활성화할 수 있습니다.
{% endhint %}

### SQS/SNS 권한이 필요한 이유

Databricks는 File Events를 위해 `csms-*` prefix가 붙은 SQS Queue와 SNS Topic을 자동 생성합니다. 이 리소스를 생성·관리하려면 IAM Role에 해당 권한이 포함되어야 합니다.

### File Events 필요 여부

| 기능 | File Events 필요 |
|------|-----------------|
| 기본 S3 읽기/쓰기 | 불필요 |
| Auto Loader (Directory Listing 모드) | 불필요 |
| Auto Loader (File Notification 모드) | **필수** |
| Job File-Arrival Trigger | **필수** |

### 전체 IAM Policy (S3 + SQS/SNS + STS Self-Assume)

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

### File Events 비활성화 방법

File Events가 불필요한 경우 (예: Directory Listing 모드만 사용):

1. Databricks Workspace에서 **Catalog → External Locations** 이동
2. 해당 External Location 선택
3. **Advanced Options**→ **File Events** 비활성화

*참고: [External Location manual setup (S3)](https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-storage/s3/s3-external-location-manual)*

---

## Metastore 구성

### Metastore 개요

Metastore는 Unity Catalog의 최상위 컨테이너로, 데이터 거버넌스의 기본 단위입니다. **리전당 1개의 Metastore** 가 존재하며, 해당 리전의 모든 Workspace가 공유합니다.

{% hint style="info" %}
이미 동일 리전(예: `ap-northeast-2`)에 Metastore가 존재하면 새로 생성할 필요 없이 기존 Metastore에 Workspace를 할당하면 됩니다.
{% endhint %}

### 사전 준비

| 항목 | 설명 |
|------|------|
| **UC 전용 S3 Bucket** | Metastore 관리 데이터 저장용 (Root Storage와 별도) |
| **UC IAM Role** | Self-assume + Databricks UC Master Role trust 설정 |

#### UC IAM Role Trust Policy (전체 JSON)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL",
          "arn:aws:iam::<YOUR-AWS-ACCOUNT>:role/<THIS-UC-ROLE>"
        ]
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "<DATABRICKS-ACCOUNT-ID>"
        }
      }
    }
  ]
}
```

{% hint style="info" %}
- 첫 번째 Principal: Databricks UC Master Role (고정값)
- 두 번째 Principal: 이 IAM Role 자신 (self-assume, 2025.01부터 필수)
- ExternalId: Databricks Account UUID
{% endhint %}

### Metastore 생성 절차

Account Console에서 생성합니다.

1. **accounts.cloud.databricks.com** 로그인
2. 좌측 메뉴: **Catalog**→ **Create metastore**
3. 입력:
   - **Name**: 식별 이름 (예: `apne2-metastore`)
   - **Region**: `ap-northeast-2` (Workspace와 동일 리전)
   - **S3 path**: UC 전용 S3 Bucket 경로 (예: `s3://my-uc-metastore-bucket/unity-catalog`)
   - **IAM Role ARN**: UC IAM Role ARN
4. **Create** 클릭

### Workspace에 Metastore 할당

1. Account Console → **Catalog**→ 생성한 Metastore 선택
2. **Assign to workspace** 클릭
3. 할당할 Workspace 선택 → **Assign**

{% hint style="warning" %}
1개 Workspace는 **1개 Metastore에만** 할당 가능합니다. 할당 변경 시 기존 데이터 접근 권한이 초기화될 수 있으므로 주의하세요.
{% endhint %}

*참고: [Create a Unity Catalog metastore](https://docs.databricks.com/aws/en/data-governance/unity-catalog/create-metastore)*
