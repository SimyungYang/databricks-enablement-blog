# 외부 서비스 PrivateLink 연결

> **최종 업데이트**: 2026-04-08

---

## 개요

MicroStrategy, Tableau Server, Power BI, Informatica 등 외부 BI/ETL 서비스가 Databricks SQL Warehouse에 접속할 때, 인터넷 대신 **AWS PrivateLink를 통한 프라이빗 연결** 을 구성하는 방법을 다룹니다.

이 가이드는 다음 두 가지 방향의 연결을 모두 설명합니다:

| 방향 | 설명 | 사용 사례 |
|------|------|----------|
| **외부 서비스 → Databricks** | 외부 서비스가 Databricks에 JDBC/ODBC로 접속하여 쿼리 실행 | BI 대시보드, 리포팅, 데이터 조회 |
| **Databricks Serverless → 외부 서비스** | Databricks Serverless 컴퓨팅에서 외부 VPC 리소스에 접근 | 외부 DB 연동, 역방향 데이터 푸시 |

{% hint style="info" %}
이 가이드는 **AWS 환경** 기준입니다. Azure의 경우 Private Endpoint 구성이 다르며, 별도 가이드를 참고하세요.
{% endhint %}

---

## 외부 서비스가 Databricks에 접속하는 방식

BI/ETL 도구는 **JDBC 또는 ODBC 드라이버** 를 통해 Databricks SQL Warehouse에 연결합니다. 어떤 외부 서비스든 접속 방식은 동일합니다.

| 항목 | 내용 |
|------|------|
| **프로토콜** | JDBC (주), ODBC (보조) |
| **드라이버** | Databricks JDBC Driver (구 Simba Spark JDBC Driver) |
| **접속 대상** | Databricks workspace 도메인 (`adb-xxxx.cloud.databricks.com`) |
| **포트** | HTTPS 443 |
| **인증** | Personal Access Token (PAT), OAuth, Service Principal |
| **SQL Warehouse** | Classic / Pro / **Serverless 모두 동일하게 지원** |

JDBC Connection String 형식은 다음과 같습니다:

```
jdbc:databricks://<workspace-host>:443;httpPath=/sql/1.0/warehouses/<warehouse-id>;SSL=1;AuthMech=3;UID=token;PWD=<personal-access-token>
```

외부 서비스 입장에서 Databricks workspace 도메인에 HTTPS(443)로 접속하는 것이 전부이므로, SQL Warehouse가 Classic이든 **Serverless** 든 접속 경로와 PrivateLink 구성은 동일합니다.

{% hint style="tip" %}
각 BI 도구별 상세 설정은 Databricks 공식 파트너 문서를 참고하세요:
- [MicroStrategy 연결](https://docs.databricks.com/aws/en/partners/bi/microstrategy)
- [Tableau 연결](https://docs.databricks.com/aws/en/partners/bi/tableau)
- [Power BI 연결](https://docs.databricks.com/aws/en/partners/bi/power-bi)
- [JDBC 드라이버 설정](https://docs.databricks.com/aws/en/integrations/jdbc/configure)
{% endhint %}

---

## 방향 1: 외부 서비스 → Databricks (Frontend PrivateLink)

### Frontend PrivateLink란?

Databricks workspace에 접속하는 경로를 인터넷 대신 **AWS 내부 네트워크(PrivateLink)** 로 전환하는 구성입니다.

Databricks는 각 리전에 **VPC Endpoint Service** 를 이미 운영하고 있습니다. 외부 서비스의 VPC에 이 서비스를 가리키는 **Interface VPC Endpoint** 를 생성하면, 해당 VPC 내에서 Databricks workspace 도메인으로 향하는 트래픽이 인터넷이 아닌 **VPC Endpoint의 Private IP → AWS PrivateLink → Databricks Control Plane** 경로로 전달됩니다.

### PrivateLink 유무에 따른 접속 경로 비교

| 구성 | 접속 경로 |
|------|----------|
| **PrivateLink 없음** | 외부 서비스 → **인터넷** → Databricks workspace → SQL Warehouse |
| **Frontend PrivateLink 적용** | 외부 서비스 → **VPC Endpoint (Private IP) → AWS PrivateLink** → Databricks workspace → SQL Warehouse |

PrivateLink를 적용하면 트래픽이 인터넷을 경유하지 않으므로, **보안 정책상 인터넷 아웃바운드가 차단된 환경** 에서도 Databricks에 접속할 수 있습니다.

{% hint style="info" %}
**핵심 포인트**: 외부 서비스(MicroStrategy, Tableau 등) 입장에서는 JDBC connection string의 호스트 주소가 동일합니다. PrivateLink 구성 후에도 `adb-xxxx.cloud.databricks.com`으로 접속하며, DNS가 해당 도메인을 VPC Endpoint의 Private IP로 resolving하여 프라이빗 경로로 라우팅합니다.
{% endhint %}

### 구성 절차

#### Step 1: 외부 서비스 VPC에서 Interface VPC Endpoint 생성

AWS Console → VPC → Endpoints → Create endpoint

| 항목 | 설정값 |
|------|--------|
| **Service name** | 리전별 Databricks Endpoint Service name (아래 표 참조) |
| **VPC** | 외부 서비스가 위치한 VPC |
| **Subnet** | 외부 서비스가 접근 가능한 서브넷 |
| **Security Group** | Inbound TCP 443 허용 |
| **Enable private DNS names** | **No** (Route 53으로 별도 관리) |

서울 리전 (ap-northeast-2) Endpoint Service name:

```
com.amazonaws.vpce.ap-northeast-2.vpce-svc-0babb9bde64f34d7e
```

{% hint style="info" %}
다른 리전의 Endpoint Service name은 [Databricks 리전별 엔드포인트 목록](https://docs.databricks.com/aws/en/resources/ip-domain-region) 문서를 참고하세요.
{% endhint %}

#### Step 2: Databricks Account Console에 VPC Endpoint 등록

1. Account Console → **Security** → **Networking** → **VPC endpoints**
2. **Register VPC endpoint** 클릭
3. 입력:
   - **VPC endpoint name**: 식별 가능한 이름 (예: `mstr-frontend-vpce`)
   - **VPC endpoint ID**: Step 1에서 생성한 `vpce-xxxxxxxx`
   - **Region**: `ap-northeast-2`
4. **Register** 클릭

{% hint style="warning" %}
Workspace의 **Private Access Settings** 에서 Public access가 Disabled인 경우, 이 VPC Endpoint ID를 **Allowed VPC endpoint IDs** 목록에도 추가해야 합니다. 그렇지 않으면 VPC Endpoint를 등록해도 접근이 차단됩니다.
{% endhint %}

#### Step 3: DNS 구성

외부 서비스 VPC에서 Databricks workspace 도메인이 VPC Endpoint의 Private IP로 resolving 되도록 **Route 53 Private Hosted Zone** 을 설정합니다.

1. Route 53 → Private Hosted Zone 생성
   - Domain: `cloud.databricks.com` (또는 workspace의 도메인)
   - VPC 연결: 외부 서비스 VPC
2. A 레코드 (Alias) 추가
   - Name: workspace 호스트명 (예: `adb-1234567890123456.18`)
   - Alias Target: VPC Endpoint의 DNS name

{% hint style="tip" %}
기존에 동일 VPC에서 이미 Databricks Frontend PrivateLink를 사용 중이라면, DNS가 이미 구성되어 있으므로 Step 3은 생략 가능합니다. 새로운 VPC라면 반드시 DNS를 구성해야 합니다.
{% endhint %}

### 구성 완료 후 확인

외부 서비스 VPC 내에서 다음을 확인합니다:

```bash
# DNS가 Private IP로 resolving 되는지 확인
nslookup adb-xxxx.cloud.databricks.com

# VPC Endpoint를 통해 접속되는지 확인
curl -v https://adb-xxxx.cloud.databricks.com
```

Private IP(10.x.x.x 등)로 resolving 되면 PrivateLink가 정상 동작하는 것입니다.

---

## 방향 2: Databricks Serverless → 외부 서비스 VPC (NCC 경유)

### 언제 필요한가?

일반적인 BI 연결(외부 서비스가 Databricks에 쿼리를 보내고 결과를 받는 구조)에서는 **방향 1만으로 충분** 합니다.

방향 2는 다음과 같은 경우에만 필요합니다:

| 사용 사례 | 설명 |
|----------|------|
| **외부 DB 연동** | Databricks Serverless에서 외부 VPC의 RDS/Aurora 등에 접근 |
| **역방향 데이터 푸시** | Databricks에서 외부 VPC의 API/서비스에 데이터 전송 |
| **온프레미스 연동** | Databricks Serverless에서 VPN/DX로 연결된 온프레미스 리소스에 접근 |

### NCC(Network Connectivity Configuration) 개요

Serverless Compute는 Databricks 관리 VPC에서 실행되므로, 외부 VPC 리소스에 접근하려면 **NCC** 를 통해 프라이빗 터널을 구성해야 합니다.

구조는 다음과 같습니다:

| 구성 | 접속 경로 |
|------|----------|
| **NCC 적용** | Databricks Serverless → **NCC VPC Endpoint → AWS PrivateLink** → 외부 VPC의 NLB → 대상 리소스 |

### 구성 절차

#### Step 1: 외부 서비스 VPC 측 준비

1. **NLB(Network Load Balancer) 생성**
   - 대상 리소스(DB, API 서버 등)를 Target Group에 등록
   - Listener: 대상 서비스 포트 (예: 3306, 5432, 443 등)

2. **VPC Endpoint Service 생성**
   - AWS Console → VPC → Endpoint Services → Create
   - NLB를 연결
   - **Require acceptance**: 활성화 (수동 승인)

3. **Allow Principals 추가**
   - Databricks 계정이 Endpoint에 접근할 수 있도록 허용
   - Principal: Databricks 서비스 계정 ARN

#### Step 2: Databricks NCC 구성

1. Account Console → **Security** → **Networking** → **Network connectivity configurations**
2. NCC 선택 (또는 신규 생성)
3. **Private endpoint rules** 탭 → **Add private endpoint rule**
4. 입력:
   - **Type**: VPC Resource
   - **Endpoint Service name**: Step 1에서 생성한 VPC Endpoint Service name
5. **Add** 클릭

Databricks가 자동으로 VPC Endpoint를 생성합니다.

#### Step 3: 연결 승인

외부 서비스 VPC 측에서:

1. AWS Console → VPC → Endpoint Services → 해당 서비스 선택
2. **Endpoint connections** 탭에서 Databricks가 생성한 연결을 확인
3. 상태가 **Pending Acceptance** → **Accept** 클릭

승인 후 수 분 내에 NCC의 상태가 **ESTABLISHED** 로 변경됩니다.

{% hint style="info" %}
NCC 구성에 대한 상세 가이드는 [Serverless NCC 가이드](serverless-ncc.md) 페이지를 참고하세요.
{% endhint %}

---

## 정리: 방향별 구성 요약

| 방향 | 용도 | 필요 여부 | 구성 주체 | 구성 요약 |
|------|------|----------|----------|----------|
| **외부 → Databricks** (Frontend PrivateLink) | 외부 서비스가 SQL Warehouse에 JDBC/ODBC로 쿼리 실행 | **필수** (프라이빗 연결 시) | 외부 서비스 VPC + Databricks 관리자 | VPC Endpoint 생성 → Databricks 등록 → DNS 구성 |
| **Databricks → 외부** (NCC) | Databricks Serverless에서 외부 VPC 리소스 접근 | BI 연결에서는 불필요 | 외부 VPC (NLB+Endpoint Service) + Databricks NCC | NLB 구성 → NCC에서 연결 → 승인 |

{% hint style="tip" %}
대부분의 BI 도구 연결은 **방향 1(Frontend PrivateLink)만 구성하면 됩니다.** 외부 서비스가 Databricks에 쿼리를 보내고 결과를 받는 일반적인 패턴에서는 Databricks → 외부 방향의 연결이 필요 없습니다.
{% endhint %}

---

## FAQ

| 질문 | 답변 |
|------|------|
| **SQL Warehouse가 Serverless여도 Frontend PrivateLink가 동작하나요?** | 네. Serverless SQL Warehouse도 동일한 workspace 엔드포인트를 사용하므로 Frontend PrivateLink 구성이 동일합니다. |
| **외부 서비스 VPC에서 VPC Endpoint Service를 별도로 만들어야 하나요?** | 아니요. Databricks가 이미 Endpoint Service를 제공합니다. 외부 VPC에서 Interface VPC Endpoint만 생성하면 됩니다. |
| **여러 외부 서비스가 동일 Databricks workspace에 접속하려면?** | 각 외부 서비스 VPC에 각각 VPC Endpoint를 생성하고, 각각을 Databricks Account Console에 등록하면 됩니다. |
| **기존 Backend PrivateLink와 충돌하지 않나요?** | 충돌하지 않습니다. Backend PrivateLink(Compute → Control Plane)와 Frontend PrivateLink(외부 → Workspace)는 독립적입니다. |
| **Cross-account에서도 VPC Endpoint를 만들 수 있나요?** | 네. Databricks Endpoint Service는 cross-account 접근이 가능합니다. 외부 서비스가 다른 AWS 계정에 있어도 VPC Endpoint를 생성할 수 있습니다. |

---

## 참고 자료

### 외부 서비스 연결
* [Connect to MicroStrategy](https://docs.databricks.com/aws/en/partners/bi/microstrategy)
* [Connect to Tableau](https://docs.databricks.com/aws/en/partners/bi/tableau)
* [Connect to Power BI](https://docs.databricks.com/aws/en/partners/bi/power-bi)
* [JDBC 드라이버 설정](https://docs.databricks.com/aws/en/integrations/jdbc/configure)

### Frontend PrivateLink (외부 → Databricks)
* [Enable AWS PrivateLink connections](https://docs.databricks.com/aws/en/security/network/classic/privatelink)
* [Configure private connectivity from your VPC (Frontend)](https://docs.databricks.com/aws/en/security/network/front-end/front-end-private-connect)
* [리전별 VPC Endpoint Service 목록](https://docs.databricks.com/aws/en/resources/ip-domain-region)

### NCC / Serverless Private Connectivity (Databricks → 외부)
* [Configure serverless private connectivity (NCC)](https://docs.databricks.com/aws/en/security/network/serverless-network-security/serverless-private-connectivity)
* [Serverless NCC 가이드 (본 블로그)](serverless-ncc.md)
