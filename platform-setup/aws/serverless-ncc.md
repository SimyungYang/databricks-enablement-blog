# Serverless NCC

## NCC 개요

NCC(Network Connectivity Configuration)는 Serverless Compute의 네트워크 제어를 위한 **Account-level 구성**입니다. Serverless SQL Warehouse, Serverless Notebook 등이 외부 리소스에 프라이빗하게 접근해야 할 때 사용합니다.

{% hint style="info" %}
Classic Compute(고객 VPC)와 달리, Serverless Compute는 Databricks 관리 VPC에서 실행됩니다. NCC를 통해 Serverless 환경에서도 프라이빗 연결을 구성할 수 있습니다.
{% endhint %}

## NCC 제한 사항

| 항목 | 제한 |
|------|------|
| **리전당 최대 NCC 수** | 10개 |
| **NCC당 최대 Workspace 수** | 50개 |
| **S3 Private Endpoint** | 리전당 최대 30개 (S3 bucket name 지정) |
| **VPC Resource Endpoint (via NLB)** | 리전당 최대 100개 |

## NCC 구성 절차

Account Console → Security → Networking → Network connectivity configurations

### Step 1: NCC 생성

1. **Network connectivity configurations** → **Create**
2. 입력:
   - **Name**: 식별 이름 (예: `apne2-serverless-ncc`)
   - **Region**: `ap-northeast-2`
3. **Create** 클릭

### Step 2: Private Endpoint Rule 추가

NCC 생성 후 프라이빗 엔드포인트 규칙을 추가합니다.

**S3 Private Endpoint:**
- **Add private endpoint rule** → S3 유형 선택
- S3 Bucket name 지정 (예: `my-data-bucket`)
- Serverless Compute에서 해당 S3 Bucket으로의 프라이빗 접근 허용

**VPC Resource Endpoint (NLB 경유):**
- 고객 VPC 내 리소스(RDS, Kafka 등)에 접근 시 사용
- NLB(Network Load Balancer) ARN 지정

### Step 3: Workspace에 NCC 연결

1. Account Console → **Workspaces** → 해당 Workspace 선택
2. **Update** → **Network connectivity configuration** 항목에서 NCC 선택
3. **Confirm update**

{% hint style="warning" %}
NCC를 Workspace에 연결/변경하면 Serverless Compute 재시작이 필요할 수 있습니다.
{% endhint %}

*참고: [Serverless private connectivity](https://docs.databricks.com/aws/en/security/network/serverless-network-security/serverless-private-connectivity)*
