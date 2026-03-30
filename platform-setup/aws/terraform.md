# Terraform 자동화

## Terraform으로 자동화하기

위 매뉴얼 과정을 IaC로 전환할 수 있습니다.

### Provider — Account-Level (MWS) + AWS

```hcl
provider "databricks" {
  alias = "mws"
  host  = "https://accounts.cloud.databricks.com"
  account_id = var.databricks_account_id
  client_id = var.client_id       # Service Principal OAuth
  client_secret = var.client_secret
}
```

## Terraform 리소스 매핑

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

## Terraform Helper Data Sources

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

## Terraform 리소스 의존성 흐름

Workspace 생성까지의 리소스 생성 순서:

| 순서 | AWS 리소스 | Terraform (Databricks) | 의존 대상 |
|------|---------|----------------------|---------|
| 1 | IAM Role + Policy | `databricks_mws_credentials` | — |
| 2 | S3 Bucket + Policy | `databricks_mws_storage_configurations` | — |
| 3 | VPC + Subnet + SG | — | — |
| 4 | VPC Endpoint (REST) | `databricks_mws_vpc_endpoint` | VPC |
| 5 | VPC Endpoint (Relay) | `databricks_mws_vpc_endpoint` | VPC |
| 6 | — | `databricks_mws_networks` | VPC + Endpoints |
| 7 | — | `databricks_mws_private_access_settings` | — |
| 8 | — | **`databricks_mws_workspaces`** | 1 + 2 + 6 + 7 |

## Terraform 공식 예제 & 참고

### GitHub 저장소

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
