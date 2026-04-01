# Storage Account (ADLS Gen2)

## 용도

Unity Catalog의 **Managed Storage** 로 사용할 ADLS Gen2 스토리지 계정을 생성합니다. UC 메타스토어가 관리하는 테이블 데이터가 이 스토리지에 저장됩니다.

## Step 1 — 스토리지 계정 만들기

1. Azure Portal → "**스토리지 계정**" 검색 → **+ 만들기**

## Step 2 — 기본 정보

| 필드 | 값 | 설명 |
|------|-----|------|
| **구독**| 동일 구독 | |
| **리소스 그룹**| `rg-databricks-prod` | |
| **스토리지 계정 이름**| `stadatabricksprod` | 소문자/숫자만, 전역 고유 |
| **리전**| Korea Central | |
| **성능**| Standard | Premium은 불필요 |
| **중복**| LRS 또는 GRS | 프로덕션은 GRS 권장 |

## Step 3 — 고급 설정

| 필드 | 값 | 중요도 |
|------|-----|--------|
| **계층 구조 네임스페이스**| **사용**| **필수**— 이것이 ADLS Gen2를 활성화하는 설정 |
| **Blob 공용 액세스**| 사용 안 함 | 보안 |
| **최소 TLS 버전**| TLS 1.2 | 보안 |

{% hint style="danger" %}
**계층 구조 네임스페이스(Hierarchical Namespace)를 반드시 "사용"으로 설정하세요.** 이 옵션이 ADLS Gen2를 활성화합니다. 일반 Blob Storage로 생성하면 Unity Catalog에서 사용할 수 없으며, 스토리지 계정 생성 후에는 이 설정을 변경할 수 없습니다.
{% endhint %}

## Step 4 — 네트워킹

| 필드 | 값 |
|------|-----|
| **네트워크 액세스**| 모든 네트워크에서 퍼블릭 액세스 사용 (초기 설정용) |

{% hint style="info" %}
초기 구성 완료 후 네트워크 액세스를 **선택한 가상 네트워크 및 IP 주소에서 퍼블릭 액세스 사용**또는 **퍼블릭 액세스 사용 안 함** 으로 변경하여 보안을 강화할 수 있습니다.
{% endhint %}

## Step 5 — 검토 + 만들기

설정 확인 후 **만들기** 클릭

## Step 6 — Container 생성

1. 생성된 스토리지 계정 → **컨테이너** 메뉴
2. **+ 컨테이너** 클릭
3. 이름: `uc-metastore` (Unity Catalog 메타스토어용)
4. 공용 액세스 수준: **프라이빗**(기본값)

## Step 7 — Access Connector에 RBAC 역할 부여

Access Connector의 Managed Identity가 이 스토리지에 접근할 수 있도록 역할을 부여합니다.

1. 스토리지 계정 → **액세스 제어(IAM)** 메뉴
2. **+ 역할 할당 추가** 클릭
3. 역할: **Storage Blob Data Contributor**
4. 구성원 → **관리 ID**선택 → **Access Connector for Azure Databricks** 선택
5. 앞서 생성한 `ac-databricks-prod` 선택
6. **검토 + 할당** 클릭

{% hint style="warning" %}
**Storage Blob Data Contributor** 역할이 정확해야 합니다. `Storage Blob Data Reader`는 읽기만 가능하므로 Unity Catalog가 테이블을 생성/수정할 수 없습니다. `Storage Account Contributor`는 데이터 접근 권한이 아닌 관리 권한이므로 올바르지 않습니다.
{% endhint %}

*참고: [Unity Catalog에 Azure 스토리지 사용](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/azure-managed-identities#step-2-grant-the-managed-identity-access-to-the-storage-account)*
