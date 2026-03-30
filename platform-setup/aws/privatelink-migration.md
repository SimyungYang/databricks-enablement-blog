# 기존 Workspace에 PrivateLink 추가

## 개요

이미 운영 중인 Workspace에 PrivateLink를 사후 추가하는 절차입니다. 초기에 PrivateLink 없이 생성한 Workspace를 프라이빗 연결로 전환할 때 사용합니다.

{% hint style="warning" %}
**기존 Network Configuration은 직접 수정 불가** — VPC Endpoint를 포함한 새 Network Configuration을 생성한 후 Workspace에서 교체해야 합니다.
{% endhint %}

## 절차

### Step 1: AWS VPC Endpoint 생성

AWS Console → VPC → Endpoints → Create endpoint

- **REST API Endpoint**: `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e`
- **SCC Relay Endpoint**: `com.amazonaws.vpce.ap-northeast-2.vpce-svc-0dc0e98a5800db5c4`
- 설정 방법은 [Backend PrivateLink](privatelink-backend.md) 참고

### Step 2: Databricks에 VPC Endpoint 등록

Account Console → Security → Networking → VPC endpoints

1. **Register VPC endpoint** 클릭
2. REST API, SCC Relay 각각 등록 (VPC Endpoint ID 입력)

### Step 3: 새 Network Configuration 생성

Account Console → Security → Networking → Classic network configurations

1. **Add network configuration** 클릭
2. 기존 VPC, Subnet, Security Group 정보 입력
3. **VPC Endpoints** 항목에서 Step 2에서 등록한 REST API / Dataplane relay Endpoint 선택
4. **Add** 클릭 → 새 Network Configuration ID 생성

### Step 4: Private Access Settings 생성

Account Console → Security → Networking → Private access settings

1. **Add private access settings** 클릭
2. Region, Public access 설정 (초기에는 **Public access = Enabled** 권장)

### Step 5: Workspace 업데이트

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
