# AWS Account & Workspace 구성 가이드

> **최종 업데이트**: 2026-03-27

## 개요

AWS Marketplace 구독부터 Backend/Frontend PrivateLink까지, Databricks Workspace를 처음부터 구성하는 전체 가이드입니다.

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
| A | Terraform 자동화 | IaC 전환 참고 (Appendix) |

## 슬라이드

* [AWS Workspace 구성 가이드 (HTML 슬라이드)](https://simyung-yang.github.io/enablement-blog/platform-setup/aws-workspace-setup-guide.html)

## 참고 문서

| 주제 | 링크 |
|------|------|
| Databricks 아키텍처 | [High-Level Architecture](https://docs.databricks.com/aws/en/getting-started/high-level-architecture) |
| Credential 구성 | [Cross-Account IAM Role](https://docs.databricks.com/aws/en/admin/account-settings-e2/credentials) |
| Storage 구성 | [Configure Storage](https://docs.databricks.com/aws/en/admin/account-settings-e2/storage) |
| Network 구성 | [Configure Network](https://docs.databricks.com/aws/en/admin/account-settings-e2/networks) |
| PrivateLink | [Enable PrivateLink](https://docs.databricks.com/aws/en/security/network/classic/privatelink) |
| PrivateLink DNS | [DNS Config](https://docs.databricks.com/aws/en/security/network/classic/privatelink-dns) |
| 리전별 Endpoint | [IP & Domain Info](https://docs.databricks.com/aws/en/resources/ip-domain-region) |
| Terraform Provider | [Databricks Provider](https://registry.terraform.io/providers/databricks/databricks/latest) |
| Terraform 예제 | [terraform-databricks-examples](https://github.com/databricks/terraform-databricks-examples) |
