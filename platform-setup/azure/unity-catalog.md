# Unity Catalog

## Metastore란?

Unity Catalog의 **최상위 컨테이너**입니다. 리전당 1개의 Metastore를 생성하고, 해당 리전의 Workspace들을 할당합니다.

| 항목 | 설명 |
|------|------|
| **단위**| 리전당 1개 |
| **역할**| Catalog, Schema, Table 등의 메타데이터 관리 |
| **스토리지**| ADLS Gen2 Container (앞서 생성) |
| **인증**| Access Connector (Managed Identity) |

## Step 1 — Account Console 접속

1. `https://accounts.azuredatabricks.net` 접속
2. Azure AD(Entra ID)로 로그인
3. 좌측 메뉴 → **Catalog**클릭

## Step 2 — Metastore 생성

1. **Create metastore**클릭

| 필드 | 값 | 설명 |
|------|-----|------|
| **Name**| `metastore-koreacentral` | 리전을 포함한 이름 권장 |
| **Region**| Korea Central | Workspace와 동일 리전 |
| **ADLS Gen2 path**| `abfss://uc-metastore@stadatabricksprod.dfs.core.windows.net/` | 컨테이너 경로 |
| **Access Connector ID**| `/subscriptions/{sub-id}/resourceGroups/rg-databricks-prod/providers/Microsoft.Databricks/accessConnectors/ac-databricks-prod` | Access Connector Resource ID |

{% hint style="warning" %}
**ADLS Gen2 경로 형식에 주의하세요.**`abfss://{container}@{storage-account}.dfs.core.windows.net/` 형식이어야 합니다. `blob.core.windows.net`이 아닌 `dfs.core.windows.net`을 사용해야 합니다.
{% endhint %}

## Step 3 — Workspace 할당

1. 생성된 Metastore 클릭
2. **Workspaces**탭 → **Assign to workspaces**클릭
3. `dbw-prod-koreacentral` 선택 → **Assign**

{% hint style="success" %}
Metastore가 Workspace에 할당되면, 해당 Workspace에서 Unity Catalog 기능을 사용할 수 있습니다.
{% endhint %}

*참고: [Unity Catalog Metastore 생성](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/create-metastore)*

---

## Catalog & Schema 생성

### Step 1 — External Location 생성 (선택)

Managed Storage 외에 추가 스토리지를 연결하려면 External Location을 생성합니다.

1. Workspace UI → **Catalog**→ **External Locations**→ **Create external location**

| 필드 | 값 |
|------|-----|
| **Name**| `ext-loc-data-lake` |
| **URL**| `abfss://{container}@{storage-account}.dfs.core.windows.net/{path}` |
| **Storage Credential**| Access Connector 기반 Credential 선택 |

{% hint style="info" %}
**Storage Credential**은 Metastore 생성 시 지정한 Access Connector를 통해 자동으로 생성됩니다. 추가 Storage Account를 연결하려면 해당 Storage Account에도 동일하게 Access Connector의 RBAC 역할을 부여해야 합니다.
{% endhint %}

### Step 2 — Catalog 생성

1. Workspace UI → **Catalog**→ **+ Add**→ **Add a catalog**

| 필드 | 값 |
|------|-----|
| **Name**| `prod_catalog` |
| **Type**| Standard |
| **Managed Location**| 기본값 (Metastore 스토리지) 또는 External Location 지정 |

```sql
-- SQL로도 생성 가능
CREATE CATALOG IF NOT EXISTS prod_catalog;
```

### Step 3 — Schema 생성

1. 생성된 Catalog 하위에서 **+ Add**→ **Add a schema**

| 필드 | 값 |
|------|-----|
| **Name**| `bronze` |
| **Managed Location**| 기본값 |

```sql
-- SQL로도 생성 가능
CREATE SCHEMA IF NOT EXISTS prod_catalog.bronze;
```

### Step 4 — 테이블 생성 테스트

Unity Catalog 전체 파이프라인이 정상 작동하는지 검증합니다.

```sql
-- 테스트 테이블 생성
CREATE TABLE IF NOT EXISTS prod_catalog.bronze.test_table (
  id BIGINT GENERATED ALWAYS AS IDENTITY,
  name STRING,
  created_at TIMESTAMP DEFAULT current_timestamp()
);

-- 데이터 삽입
INSERT INTO prod_catalog.bronze.test_table (name)
VALUES ('Azure Databricks 테스트');

-- 조회 확인
SELECT * FROM prod_catalog.bronze.test_table;
```

{% hint style="success" %}
테이블 생성, 데이터 삽입, 조회가 모두 성공하면 Unity Catalog 구성이 완료된 것입니다. ADLS Gen2에 데이터가 Delta 형식으로 저장되었는지 Storage Account에서도 확인해 보세요.
{% endhint %}

### 3-Level Namespace

Unity Catalog는 **3-Level Namespace**구조를 사용합니다.

```
metastore
  └── catalog
        └── schema
              └── table / view / function
```

| 레벨 | 예시 | 설명 |
|------|------|------|
| **Catalog**| `prod_catalog` | 데이터 도메인 또는 환경 단위 |
| **Schema**| `bronze` | 데이터 레이어 또는 팀 단위 |
| **Table**| `test_table` | 실제 데이터 오브젝트 |

*참고: [Unity Catalog 오브젝트 모델](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/#the-unity-catalog-object-model)*
