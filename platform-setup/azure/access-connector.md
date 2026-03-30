# Access Connector 생성

## Access Connector란?

Access Connector는 Azure Databricks가 ADLS Gen2 등 Azure 리소스에 접근할 때 사용하는 **Managed Identity** 컨테이너입니다.

| 항목 | 설명 |
|------|------|
| **역할** | Unity Catalog가 ADLS Gen2에 접근하는 브릿지 |
| **인증 방식** | System-assigned Managed Identity (자동 생성) |
| **AWS 대응** | Cross-Account IAM Role + UC Storage IAM Role |

{% hint style="info" %}
**AWS vs Azure 인증 차이**: AWS에서는 Cross-Account IAM Role과 Trust Policy를 수동으로 구성해야 합니다. Azure에서는 Access Connector를 생성하면 **System-assigned Managed Identity**가 자동으로 생성되어 훨씬 간단합니다.
{% endhint %}

## Step 1 — Access Connector 만들기

1. Azure Portal → 상단 검색창에서 **"Azure Databricks용 액세스 커넥터"** 검색
   * 영문: **"Access Connector for Azure Databricks"**
2. **+ 만들기** 클릭

## Step 2 — 기본 정보 입력

| 필드 | 값 |
|------|-----|
| **구독** | 동일 구독 |
| **리소스 그룹** | `rg-databricks-prod` |
| **이름** | `ac-databricks-prod` |
| **리전** | Korea Central |

## Step 3 — 관리 ID 확인

* **System-assigned Managed Identity**: **사용** (기본값)
* 생성 후 **개요** 페이지에서 **Managed Identity Object ID** 확인 가능

## Step 4 — 태그 설정

| 태그 키 | 값 (예시) |
|---------|-----------|
| `Owner` | `data-engineering-team` |
| `Purpose` | `unity-catalog-access` |

## Step 5 — 검토 + 만들기

설정 확인 후 **만들기** 클릭

{% hint style="warning" %}
**Access Connector Resource ID를 메모하세요**: Unity Catalog Metastore 구성 시 필요합니다. 형식: `/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Databricks/accessConnectors/{name}`
{% endhint %}

*참고: [Access Connector for Azure Databricks](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/azure-managed-identities)*
