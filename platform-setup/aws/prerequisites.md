# 사전 준비

## 사전 준비 체크리스트

구성 시작 전 반드시 확인해야 합니다.

### AWS 계정 요구사항

- IAM Role, S3, VPC 생성 권한 보유
- **STS 엔드포인트**: `us-west-2` 리전 활성화 필수 (배포 리전과 무관)
- **SCP**: `sts:AssumeRole` 허용 확인

### Databricks 계정 요구사항

- **Account Admin** 권한
- **Enterprise 티어** (PrivateLink 사용 시 필수)

### Databricks AWS Account ID (IAM Trust 설정용)

| 환경 | Account ID |
|------|-----------|
| **Standard AWS** | `414351767826` |
| **AWS GovCloud** | `044793339203` |
| **GovCloud DoD** | `170661010020` |

*참고: [Databricks account IDs for AWS trust policy](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials)*
