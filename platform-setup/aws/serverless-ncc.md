# Serverless NCC

## NCC 개요

NCC(Network Connectivity Configuration)는 Serverless Compute의 네트워크 제어를 위한 **Account-level 구성** 입니다. Serverless SQL Warehouse, Serverless Notebook, Model Serving 등이 외부 리소스에 프라이빗하게 접근해야 할 때 사용합니다.

{% hint style="info" %}
Classic Compute(고객 VPC)와 달리, Serverless Compute는 Databricks 관리 VPC에서 실행됩니다. NCC를 통해 Serverless 환경에서도 프라이빗 연결을 구성할 수 있습니다.
{% endhint %}

## NCC vs Classic PrivateLink 비교

| 항목 | NCC (Serverless) | Classic PrivateLink |
|------|------------------|---------------------|
| **적용 대상** | Serverless Compute (SQL Warehouse, Notebook, Model Serving) | Classic Compute (고객 VPC 내 클러스터) |
| **VPC 관리** | Databricks 관리 VPC | 고객 관리 VPC |
| **구성 위치** | Account Console → Networking | AWS Console + Account Console |
| **AWS 리소스 생성** | 불필요 (Databricks가 관리) | VPC Endpoint, Subnet 등 직접 생성 |
| **연결 대상** | S3, 고객 VPC 리소스 (NLB 경유) | Databricks Control Plane |
| **구성 난이도** | 낮음 (UI에서 수분 내 완료) | 높음 (AWS + Databricks 양쪽 구성) |
| **Stable IP 지원** | NCC에 Stable IP 활성화 가능 | N/A (고객 VPC IP 사용) |

{% hint style="info" %}
**NCC와 Classic PrivateLink는 상호 보완적입니다.** NCC는 Serverless → 외부 리소스 방향, Classic PrivateLink는 고객 VPC → Databricks Control Plane 방향입니다. 보안 요구사항에 따라 둘 다 구성할 수 있습니다.
{% endhint %}

## NCC 제한 사항

| 항목 | 제한 | 비고 |
|------|------|------|
| **리전당 최대 NCC 수** | 10개 | Account 단위 |
| **NCC당 최대 Workspace 수** | 50개 | 하나의 NCC를 여러 Workspace가 공유 가능 |
| **S3 Private Endpoint** | 리전당 최대 30개 | S3 bucket name 단위로 지정 |
| **VPC Resource Endpoint (NLB)** | 리전당 최대 100개 | NLB ARN 단위로 지정 |
| **Stable IP** | NCC당 고정 IP 수 제한 있음 | 방화벽 허용 목록에 활용 |

{% hint style="warning" %}
**제한 초과 시**: 리전당 NCC 수(10개)나 엔드포인트 수가 부족한 경우 Databricks 지원팀에 한도 상향을 요청할 수 있습니다. 단, S3 엔드포인트의 경우 와일드카드는 지원하지 않으며 버킷 이름을 정확히 지정해야 합니다.
{% endhint %}

## NCC 구성 절차

### Step 1: NCC 생성

Account Console → **Security**→ **Networking**→ **Network connectivity configurations**

1. " ** Create**" 버튼 클릭
2. 다음 정보 입력:

| 필드 | 값 | 설명 |
|------|-----|------|
| **Name** | `apne2-serverless-ncc` | 식별 이름 (리전 + 용도 조합 권장) |
| **Region** | `ap-northeast-2` | Workspace가 위치한 리전과 동일해야 함 |

3. " ** Create**" 클릭 → NCC ID 생성됨

{% hint style="warning" %}
**NCC의 리전은 변경할 수 없습니다.** 생성 후 리전을 바꿀 수 없으므로, Workspace 리전과 동일한 리전으로 생성하세요.
{% endhint %}

### Step 2: S3 Private Endpoint 추가

Serverless Compute에서 특정 S3 버킷에 프라이빗 네트워크 경로로 접근하도록 설정합니다.

1. 생성된 NCC 클릭 → " ** Private endpoint rules**" 탭 이동
2. " ** Add private endpoint rule**" 클릭
3. 다음 정보 입력:

| 필드 | 값 | 설명 |
|------|-----|------|
| **Type** | `S3` | S3 버킷 접근용 |
| **S3 bucket name** | `my-data-bucket` | 대상 S3 버킷 이름 (와일드카드 불가) |

4. " ** Add**" 클릭

{% hint style="info" %}
**Unity Catalog 관리 스토리지 버킷** 은 NCC 없이도 자동으로 프라이빗 연결됩니다. NCC에 추가해야 하는 것은 **External Location** 이나 직접 접근하는 S3 버킷입니다.
{% endhint %}

#### 여러 버킷 추가 시

- 버킷마다 개별 엔드포인트 규칙을 생성해야 합니다
- 리전당 최대 30개까지 가능
- 버킷 이름을 정확히 입력 (예: `my-data-bucket`, `s3://` 접두사 불필요)

### Step 3: VPC Resource Endpoint 추가 (NLB 경유)

고객 VPC 내 리소스(RDS, Kafka, Elasticsearch 등)에 Serverless Compute에서 접근해야 할 때 사용합니다.

#### 사전 준비 (고객 AWS 계정에서)

1. 대상 리소스 앞에 **NLB(Network Load Balancer)** 생성
   - AWS Console → EC2 → Load Balancers → Create Load Balancer → **Network Load Balancer**
   - **Scheme**: Internal
   - **Target Group**: 대상 리소스(RDS 등)의 IP 또는 인스턴스 등록
2. NLB에 **VPC Endpoint Service** 생성
   - AWS Console → VPC → Endpoint Services → Create
   - Load balancer: 위에서 생성한 NLB 선택
   - **Acceptance required**: No (또는 수동 승인 원하면 Yes)
3. Databricks Account ID (`414351767826`)를 **Allowed principals** 에 추가

#### NCC에 엔드포인트 규칙 추가

1. NCC → " ** Private endpoint rules**" 탭 → " ** Add private endpoint rule**" 클릭
2. 다음 정보 입력:

| 필드 | 값 | 설명 |
|------|-----|------|
| **Type** | `VPC endpoint` | VPC 리소스 접근용 |
| **Resource ID** | VPC Endpoint Service의 서비스 이름 | `com.amazonaws.vpce.ap-northeast-2.vpce-svc-xxxx` 형태 |

3. " ** Add**" 클릭
4. 상태가 " ** Pending**" → " ** Established**"로 변경될 때까지 대기 (수 분 소요)

{% hint style="warning" %}
Endpoint Service에서 **Acceptance required: Yes** 로 설정한 경우, AWS Console → VPC → Endpoint Services → Endpoint connections에서 Databricks의 연결 요청을 **수동 승인** 해야 합니다.
{% endhint %}

### Step 4: Workspace에 NCC 연결

1. Account Console → **Workspaces**→ 대상 Workspace 클릭
2. " ** Update**" 버튼 클릭
3. " ** Network connectivity configuration**" 드롭다운에서 Step 1에서 생성한 NCC 선택
4. " ** Confirm update**" 클릭
5. 프로비저닝 완료 대기 (수 분 소요)

{% hint style="warning" %}
**NCC 연결/변경 시 주의사항**:
- 실행 중인 Serverless Compute가 재시작됩니다
- 진행 중인 Serverless SQL 쿼리가 중단될 수 있습니다
- 유지보수 윈도우에 수행하는 것을 권장합니다
{% endhint %}

{% hint style="info" %}
**하나의 NCC를 여러 Workspace에서 공유할 수 있습니다.** 동일 리전에 여러 Workspace가 있고 동일한 네트워크 정책을 적용하려면 NCC를 공유하는 것이 관리 효율적입니다 (최대 50개 Workspace/NCC).
{% endhint %}

## NCC 검증

NCC 구성 후 연결이 정상 작동하는지 확인합니다.

1. Workspace에서 **Serverless SQL Warehouse** 시작
2. S3 엔드포인트 검증:
   ```sql
   SELECT * FROM delta.`s3://my-data-bucket/path/to/table` LIMIT 10;
   ```
3. VPC Resource 엔드포인트 검증:
   - 대상 리소스에 대한 쿼리 실행 (예: JDBC를 통한 RDS 접근)

{% hint style="info" %}
연결 실패 시 확인 사항:
- NCC의 엔드포인트 규칙 상태가 " ** Established**"인지 확인
- S3 버킷 이름이 정확한지 확인 (오타 주의)
- VPC Endpoint Service의 **Allowed principals** 에 Databricks Account ID가 포함되어 있는지 확인
- 대상 리소스의 Security Group이 NLB로부터의 트래픽을 허용하는지 확인
{% endhint %}

*참고: [Serverless private connectivity](https://docs.databricks.com/aws/en/security/network/serverless-network-security/serverless-private-connectivity) · [NCC limits](https://docs.databricks.com/aws/en/security/network/serverless-network-security/serverless-private-connectivity#limits)*
