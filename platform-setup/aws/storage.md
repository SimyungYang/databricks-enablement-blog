# Storage 구성

## Root S3 Bucket — 생성 요건

AWS Console → S3 → Create bucket

### 필수 설정

| 항목 | 설정값 |
|------|--------|
| **Bucket Region** | Workspace와 **동일 리전** (예: `ap-northeast-2`) |
| **Block all public access** | **On** (모두 체크) |
| **Server-side encryption** | **AES-256** (SSE-S3) 또는 SSE-KMS |
| **Bucket versioning** | Disabled (선택) |
| **ACL** | ACLs disabled (권장) |

*참고: [Configure storage for workspace](https://docs.databricks.com/aws/en/admin/account-settings-e2/storage) · [Terraform: databricks_aws_bucket_policy](https://registry.terraform.io/providers/databricks/databricks/latest/docs/data-sources/aws_bucket_policy)*

## Root S3 Bucket — Bucket Policy

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

## Storage 등록 — Account Console

Databricks Account Console에서 등록합니다.

### 절차

1. **accounts.cloud.databricks.com** 로그인
2. 좌측 메뉴: **Cloud resources** → **Storage configuration** 탭
3. **Add storage configuration** 클릭
4. 입력:
   - **Storage configuration name**: 식별 이름 (예: `prod-root-storage`)
   - **Bucket name**: S3 Bucket 이름 (ARN 아님, 이름만)
5. **Add** 클릭

### 결과

- **Storage Configuration ID** 생성됨 → Workspace 생성 시 사용

{% hint style="warning" %}
이 설정은 **수정 불가** — 변경 필요 시 삭제 후 재생성 (Workspace가 연결된 경우 삭제 불가)
{% endhint %}

*참고: [Configure storage](https://docs.databricks.com/aws/en/admin/account-settings-e2/storage) · [Terraform: databricks_mws_storage_configurations](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_storage_configurations)*
