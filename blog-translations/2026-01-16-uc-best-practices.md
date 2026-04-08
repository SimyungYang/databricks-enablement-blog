---
original_title: "Unity Catalog Best Practices"
authors: "Databricks"
date: "2026-02-03"
category: "Data Governance"
original_url: "https://docs.databricks.com/aws/en/data-governance/unity-catalog/best-practices"
translated_date: "2026-04-07"
---

# Unity Catalog 모범 사례 (Best Practices)

> **원문**: [Unity Catalog best practices](https://docs.databricks.com/aws/en/data-governance/unity-catalog/best-practices)

{% hint style="info" %}
**요약**

- Unity Catalog의 ID 관리, 권한 할당, 메타스토어 구성, 카탈로그·스키마 설계, 스토리지 전략, 컴퓨트 설정에 걸친 포괄적인 모범 사례를 제공합니다.
- Managed Tables(관리형 테이블)·Volumes 우선 사용, 그룹 기반 소유권 관리, SCIM 프로비저닝, Delta Sharing 기반 크로스 리전 공유가 핵심 권장 사항입니다.
- External Locations(외부 위치)는 최소 권한 원칙으로 관리하고, 엔드유저에게는 External Tables·Volumes를 통해 접근 권한을 부여하는 것을 권장합니다.
{% endhint %}

---

이 문서는 Unity Catalog를 활용하여 데이터 거버넌스 요구사항을 가장 효과적으로 충족하기 위한 권장 사항을 제공합니다. Databricks의 데이터 거버넌스 소개는 **Data governance with Databricks** 를, Unity Catalog 소개는 **What is Unity Catalog?** 를 참고하시기 바랍니다.

---

## ID 관리 (Identities)

사용자(Users), 그룹(Groups), 서비스 주체(Service Principals) 등 Principal(보안 주체)은 Unity Catalog 보안 개체에 권한을 할당받으려면 반드시 Databricks **계정(Account) 수준** 에서 정의되어야 합니다. Databricks는 IdP(Identity Provider, ID 공급자)에서 SCIM(System for Cross-domain Identity Management)을 통해 Databricks 계정으로 Principal을 프로비저닝하도록 권장합니다.

**모범 사례:**

- **워크스페이스 수준의 SCIM 프로비저닝을 사용하지 않고, 기존에 설정된 경우 비활성화합니다.** 워크스페이스에 직접 Principal을 프로비저닝하는 방식은 Unity Catalog가 활성화되지 않은 레거시 워크스페이스에서만 사용해야 합니다. 프로비저닝은 전적으로 계정 수준에서 관리해야 합니다.

- **IdP에서 그룹을 정의하고 관리합니다.** 그룹은 조직의 그룹 정의와 일치해야 합니다.

  그룹은 사용자 및 서비스 주체와 동작 방식이 다릅니다. 워크스페이스에 추가한 사용자와 서비스 주체는 Databricks 계정에 자동으로 동기화되지만, 워크스페이스 로컬 그룹은 그렇지 않습니다. 워크스페이스 로컬 그룹이 있다면, 가능하면 IdP에 복제한 후 계정 수준으로 수동 마이그레이션하는 것이 좋습니다.

- **그룹을 효과적으로 활용하여 데이터 및 기타 Unity Catalog 보안 개체에 대한 접근 권한을 부여합니다.** 개별 사용자에게 직접 권한을 부여하는 방식은 가능하면 피합니다.

- **대부분의 보안 개체 소유권은 그룹에 할당합니다.**

- **사용자를 계정 또는 워크스페이스에 수동으로 추가하거나, Databricks에서 그룹을 직접 수정하지 않습니다.** IdP를 통해 관리하십시오.

- **잡(Job)을 실행할 때는 서비스 주체(Service Principal)를 사용합니다.** 서비스 주체는 잡 자동화를 가능하게 합니다. 사용자가 프로덕션 데이터에 쓰는 잡을 실행할 경우, 실수로 프로덕션 데이터를 덮어쓸 위험이 있습니다.

자세한 내용은 **Manage users, service principals, and groups** 및 **Sync users and groups from your identity provider using SCIM** 을 참고하십시오.

---

## 관리자 역할과 강력한 권한 (Admin roles and powerful privileges)

`ALL PRIVILEGES`, `MANAGE` 와 같은 관리자 역할 및 강력한 권한을 할당할 때는 신중해야 합니다:

- **Account Admin, Workspace Admin, Metastore Admin의 권한 차이를 이해한 후 할당합니다.** 자세한 내용은 **Admin privileges in Unity Catalog** 를 참고하십시오.

- **가능한 한 이러한 역할은 그룹에 할당합니다.**

- **Metastore Admin은 선택 사항입니다.** 필요한 경우에만 할당하십시오. 자세한 내용은 **(Optional) Assign the metastore admin role** 을 참고하십시오.

- **객체 소유권은 그룹에 할당합니다.** 특히 프로덕션에서 사용되는 객체는 더욱 그렇습니다. 객체를 생성한 사람이 첫 번째 소유자가 됩니다. 생성자는 소유권을 적절한 그룹에 재할당해야 합니다.

- **`MANAGE` 권한 할당은 신중하게 합니다.** Metastore Admin, 소유자, 그리고 객체에 대해 `MANAGE` 권한을 가진 사용자만 해당 객체에 대한 권한을 부여할 수 있습니다. 상위 카탈로그 및 스키마의 소유자도 카탈로그 또는 스키마 내 모든 객체에 대한 권한을 부여할 수 있습니다. 소유권 및 `MANAGE` 권한 할당은 최소한으로 유지하십시오.

- **`ALL PRIVILEGES` 할당은 신중하게 합니다.** `ALL PRIVILEGES` 는 `MANAGE`, `EXTERNAL USE LOCATION`, `EXTERNAL USE SCHEMA` 를 제외한 모든 권한을 포함합니다.

---

## 권한 할당 (Privilege assignment)

Unity Catalog의 보안 개체는 계층적으로 구성되어 있으며, 권한은 하위 계층으로 상속됩니다. 이 상속 계층 구조를 활용하여 효과적인 권한 모델을 개발하십시오.

**모범 사례:**

### `USE CATALOG` 및 `USE SCHEMA` 권한의 역할 이해

- `USE CATALOG | SCHEMA` 는 카탈로그 또는 스키마에서 데이터를 볼 수 있는 권한을 부여합니다. 단독으로는 카탈로그나 스키마 내부 객체에 대한 `SELECT` 또는 `READ` 권한을 부여하지 않지만, 해당 접근 권한을 부여하기 위한 **전제 조건** 입니다. 카탈로그 또는 스키마에서 데이터를 볼 수 있어야 하는 사용자에게만 이 권한을 부여하십시오.

- `USE CATALOG | SCHEMA` 는 카탈로그 또는 스키마에 대한 접근을 제한함으로써, 객체 소유자(예: 테이블 생성자)가 해당 객체(테이블)에 대한 접근 권한을 권한이 없는 사용자에게 실수로 부여하는 것을 방지합니다. 일반적으로 팀별로 스키마를 생성하고, 해당 팀에게만 `USE SCHEMA` 및 `CREATE TABLE` 을 부여하는 패턴(상위 카탈로그에 `USE CATALOG` 포함)이 권장됩니다.

### `BROWSE` 권한의 역할 이해

- `BROWSE` 는 사용자가 Catalog Explorer, 스키마 브라우저, 검색, 리니지 그래프, `information_schema`, REST API를 통해 카탈로그 내 객체의 **메타데이터를 볼 수 있는 권한** 을 부여합니다. 데이터 자체에 대한 접근 권한은 부여하지 않습니다.

- `BROWSE` 는 `USE CATALOG` 또는 `USE SCHEMA` 권한이 없더라도 사용자가 데이터를 **발견하고 접근 요청** 을 할 수 있게 합니다.

- Databricks는 데이터 검색성을 높이고 접근 요청을 지원하기 위해, 카탈로그 수준에서 `All account users` 그룹에 `BROWSE` 권한을 부여하도록 권장합니다.

### 접근 요청 대상(Destination) 설정으로 셀프서비스 접근 지원

- 접근 요청 대상이 설정되어 있지 않으면, 사용자가 객체를 발견하더라도 접근 요청을 할 수 없습니다.

- Databricks는 다른 대상이 설정되지 않은 경우 카탈로그 소유자 또는 객체 소유자에게 자동으로 요청이 전송되도록 **기본 이메일 대상을 활성화** 하도록 권장합니다.

- 대상은 이메일 주소, Slack, Microsoft Teams, PagerDuty, 웹훅, 또는 조직의 요청 시스템으로 리다이렉트하는 URL로 설정할 수 있습니다.

### 객체 소유권과 `MANAGE` 권한의 차이 이해

- 객체의 소유자는 테이블의 `SELECT` 및 `MODIFY` 와 같이 해당 객체에 대한 모든 권한을 가지며, 다른 Principal에게 보안 개체에 대한 권한을 부여하거나 소유권을 이전할 수 있습니다.

- 소유자는 `MANAGE` 권한을 부여하여 다른 Principal에게 객체에 대한 소유자 권한의 일부를 위임할 수 있습니다.

- 카탈로그 및 스키마의 소유자는 카탈로그 또는 스키마 내 모든 객체의 소유권을 이전할 수 있습니다.

- 객체의 권한 관리를 담당하는 그룹에 소유권을 설정하거나 `MANAGE` 권한을 부여하는 것이 모범 사례입니다.

### 뷰 및 메트릭 뷰의 협업 편집을 위한 그룹 소유권 활용

- 기본적으로 뷰(View) 또는 메트릭 뷰(Metric View)의 소유자만 해당 정의를 편집할 수 있습니다. 이는 편집자가 뷰를 수정하여 권한 없는 데이터에 접근할 수 있는 권한 상승(Privilege Escalation)을 방지합니다.

- 여러 사용자가 동일한 뷰 또는 메트릭 뷰를 안전하게 편집할 수 있도록 하려면, 소유권을 그룹에 이전하고 해당 그룹에 소스 테이블에 대한 접근 권한을 부여하십시오. 그러면 모든 그룹 멤버가 정의를 편집할 수 있으며, 데이터 접근은 그룹이 볼 수 있는 범위로 제한됩니다.

- 자세한 내용은 **Enable collaborative editing** 을 참고하십시오.

- **프로덕션 테이블에 대한 직접적인 `MODIFY` 접근은 서비스 주체(Service Principal)로 제한합니다.**

자세한 내용은 **Manage privileges in Unity Catalog** 를 참고하십시오.

---

## 메타스토어 (Metastores)

메타스토어 생성 및 관리에 대한 규칙과 모범 사례는 다음과 같습니다:

- **리전당 하나의 메타스토어만 존재할 수 있습니다.** 해당 리전의 모든 워크스페이스가 동일한 메타스토어를 공유합니다. 리전 간 데이터 공유는 **Cross-region and cross-platform sharing** 을 참고하십시오.

- **메타스토어는 리전 격리를 제공하지만, 기본적인 데이터 격리 단위로 설계된 것은 아닙니다.** 데이터 격리는 일반적으로 카탈로그 수준에서 시작됩니다. 다만, 더 중앙화된 거버넌스 모델을 선호한다면 메타스토어 수준의 관리형 스토리지를 생성할 수 있습니다. 권장 사항은 **Managed storage** 를 참고하십시오.

- **Metastore Admin 역할은 선택 사항입니다.** 할당 여부에 대한 권장 사항은 **Admin roles and powerful privileges** 를 참고하십시오.

{% hint style="warning" %}
**중요**: 자주 접근되는 테이블을 둘 이상의 메타스토어에 External Table로 등록하지 마십시오. 이렇게 할 경우, 메타스토어 A에 대한 쓰기 결과로 발생한 스키마, 테이블 속성, 주석 및 기타 메타데이터 변경 사항이 메타스토어 B에 전혀 반영되지 않습니다. 또한 Databricks 커밋 서비스(Commit Service)에 일관성 문제가 발생할 수 있습니다.
{% endhint %}

---

## 카탈로그 및 스키마 (Catalogs and schemas)

카탈로그(Catalog)는 일반적인 Unity Catalog 데이터 거버넌스 모델에서 **데이터 격리의 기본 단위** 입니다. 스키마(Schema)는 추가적인 조직화 레이어를 제공합니다.

**카탈로그 및 스키마 사용에 대한 모범 사례:**

- **데이터 및 AI 객체를 조직의 부서와 프로젝트를 반영하는 카탈로그 및 스키마로 구성합니다.** 일반적으로 카탈로그는 환경 범위(dev/test/prod), 팀, 사업 단위, 또는 이들의 조합에 대응됩니다. 이렇게 하면 권한 계층 구조를 활용하여 접근 권한을 효과적으로 관리하기가 더 쉬워집니다.

- **작업 환경과 데이터가 동일한 격리 요구사항을 가질 때, 카탈로그를 특정 워크스페이스에 바인딩할 수 있습니다.** 이 경우 제한된 워크스페이스 집합으로 범위를 지정할 수 있는 카탈로그를 생성하십시오.

- **프로덕션 카탈로그와 스키마의 소유권은 항상 개인 사용자가 아닌 그룹에 할당합니다.**

- **`USE CATALOG` 및 `USE SCHEMA` 는 해당 카탈로그 또는 스키마에 포함된 데이터를 보거나 쿼리할 수 있어야 하는 사용자에게만 부여합니다.**

카탈로그 및 스키마에 대한 권한 부여에 대한 추가 권장 사항은 **Privilege assignment** 를 참고하십시오.

---

## 관리형 스토리지 (Managed storage)

Managed Tables(관리형 테이블)와 Volumes(볼륨)은 수명 주기가 Unity Catalog에 의해 완전히 관리되는 객체로, **관리형 스토리지(Managed Storage)** 라고 불리는 기본 스토리지 위치에 저장됩니다. 관리형 스토리지는 메타스토어, 카탈로그, 스키마 수준에서 설정할 수 있습니다. 데이터는 계층 구조에서 가장 하위의 사용 가능한 위치에 저장됩니다. 자세한 내용은 **Managed storage location hierarchy** 및 **Specify a managed storage location in Unity Catalog** 를 참고하십시오.

**관리형 스토리지 위치에 대한 모범 사례:**

- **데이터 격리의 기본 단위로 카탈로그 수준의 스토리지를 우선적으로 사용합니다.**

  메타스토어 수준의 스토리지는 초기 Unity Catalog 환경에서 필수였지만, 현재는 더 이상 필수가 아닙니다.

- **메타스토어 수준의 관리형 위치를 생성하기로 선택한 경우, 전용 버킷(Bucket)을 사용합니다.**

- **Unity Catalog 외부에서 접근할 수 있는 버킷을 사용하지 않습니다.**

  외부 서비스나 Principal이 Unity Catalog를 우회하여 관리형 스토리지 위치의 데이터에 접근하면, 관리형 테이블 및 볼륨에 대한 접근 제어와 감사 가능성(Auditability)이 손상됩니다.

- **DBFS 루트 파일 시스템에 사용되었거나 현재 사용 중인 버킷을 재사용하지 않습니다.**

---

## 관리형 테이블과 외부 테이블 (Managed and external tables)

**Managed Tables(관리형 테이블)** 은 Unity Catalog가 완전히 관리하는 테이블로, Unity Catalog가 각 테이블의 거버넌스와 기반 데이터 파일을 모두 관리합니다. 항상 Delta 또는 Apache Iceberg 형식입니다.

**External Tables(외부 테이블)** 은 Databricks에서의 접근은 Unity Catalog가 관리하지만, 데이터 수명 주기와 파일 레이아웃은 클라우드 제공업체 및 기타 데이터 플랫폼을 사용하여 관리되는 테이블입니다. Databricks에서 External Table을 생성할 때 위치를 지정해야 하며, 이 위치는 Unity Catalog **External Location(외부 위치)** 에 정의된 경로에 있어야 합니다.

이 두 테이블 유형의 선택은 단순한 스토리지 결정이 아니라 거버넌스 전략의 핵심입니다. 아래 기준을 참고하여 사용 상황에 맞는 유형을 선택하십시오.

### Managed Tables(관리형 테이블) 사용 권장 상황

- **대부분의 사용 사례에 적합합니다.** Databricks는 Unity Catalog 거버넌스 기능과 성능 최적화를 최대한 활용할 수 있는 Managed Tables와 Volumes를 권장합니다:

  - Auto Compaction(자동 압축)
  - Auto Optimize(자동 최적화)
  - Faster metadata reads(메타데이터 캐싱을 통한 빠른 읽기)
  - Intelligent file size optimizations(지능형 파일 크기 최적화)

  새로운 Databricks 기능은 Managed Tables를 우선적으로 지원합니다.

- **모든 신규 테이블에 사용합니다.**

### External Tables(외부 테이블) 사용 권장 상황

- **기존에 사용 중이며 Hive Metastore에서 Unity Catalog로 업그레이드하는 경우:**

  - External Tables를 사용하면 데이터를 이동하지 않고도 빠르고 원활한 "원클릭" 업그레이드가 가능합니다.
  - Databricks는 결국 External Tables를 Managed Tables로 마이그레이션할 것을 권장합니다.

- **이 데이터에 대한 재해 복구(Disaster Recovery) 요구사항이 있어 Managed Tables로 충족할 수 없는 경우:**

  Managed Tables는 동일한 클라우드 내 여러 메타스토어에 등록할 수 없습니다.

- **외부 리더 또는 라이터가 Databricks 외부에서 데이터와 상호작용해야 하는 경우:**

  일반적으로 Unity Catalog에 등록된 External Tables에도 외부 접근은 허용하지 않는 것이 좋습니다. 외부 접근은 Unity Catalog의 접근 제어, 감사, 리니지를 우회합니다. Delta Sharing을 사용하여 관리형 테이블을 유지하고 리전 또는 클라우드 제공업체 간에 데이터를 공유하는 것이 더 나은 방법입니다. 외부 접근을 허용해야 한다면 읽기만 허용하고, 모든 쓰기는 Databricks와 Unity Catalog를 통해 이루어지도록 제한하십시오.

- **Parquet, Avro, ORC 등 Delta 또는 Iceberg가 아닌 테이블 형식을 지원해야 하는 경우.**

**External Tables 사용 시 추가 권장 사항:**

- Databricks는 스키마당 하나의 External Location을 사용하여 External Tables를 생성하도록 권장합니다.

- Databricks는 일관성 문제의 위험으로 인해 테이블을 둘 이상의 메타스토어에 External Table로 등록하는 것을 강하게 **권장하지 않습니다.** 예를 들어, 한 메타스토어에서 스키마를 변경해도 두 번째 메타스토어에는 반영되지 않습니다. 메타스토어 간 데이터 공유에는 Delta Sharing을 사용하십시오. 자세한 내용은 **Cross-region and cross-platform sharing** 을 참고하십시오.

자세한 내용은 **Databricks tables** 를 참고하십시오.

---

## 관리형 볼륨과 외부 볼륨 (Managed and external volumes)

**Managed Volumes(관리형 볼륨)** 은 Unity Catalog가 완전히 관리하는 볼륨으로, Unity Catalog가 클라우드 제공업체 계정의 볼륨 스토리지 위치에 대한 접근을 관리합니다. **External Volumes(외부 볼륨)** 은 Databricks 외부에서 관리되는 스토리지 위치에 있는 기존 데이터를 나타내지만, Databricks 내부에서의 접근을 제어하고 감사하기 위해 Unity Catalog에 등록됩니다. Databricks에서 External Volume을 생성할 때 위치를 지정해야 하며, 이 위치는 Unity Catalog **External Location** 에 정의된 경로에 있어야 합니다.

### Managed Volumes(관리형 볼륨) 사용 권장 상황

- **대부분의 사용 사례에서 Unity Catalog 거버넌스 기능을 최대한 활용하기 위해 사용합니다.**

- **`COPY INTO` 또는 CTAS(`CREATE TABLE AS`) 문 없이 볼륨의 파일에서 시작하는 테이블을 생성하려는 경우에 사용합니다.**

### External Volumes(외부 볼륨) 사용 권장 상황

- **외부 시스템에서 생성된 원시 데이터의 랜딩 영역(Landing Area)을 등록하여 ETL 파이프라인 초기 단계에서 처리를 지원하는 경우에 사용합니다.**

- **Auto Loader, `COPY INTO`, 또는 CTAS 문을 사용하는 수집(Ingestion)의 스테이징 위치를 등록하는 경우에 사용합니다.**

- **데이터 과학자, 데이터 분석가, 머신러닝 엔지니어에게 탐색적 데이터 분석 및 기타 데이터 사이언스 작업에 사용할 파일 스토리지 위치를 제공하는 경우(Managed Volumes를 사용할 수 없을 때)에 사용합니다.**

- **다른 시스템이 클라우드 스토리지에 저장한 임의의 파일에 Databricks 사용자가 접근할 수 있도록 하는 경우에 사용합니다.** 예를 들어, 감시 시스템이나 IoT 기기가 캡처한 대규모 비정형 데이터(이미지, 오디오, 비디오, PDF 파일), 또는 로컬 의존성 관리 시스템이나 CI/CD 파이프라인에서 내보낸 라이브러리 파일(JAR 및 Python wheel 파일)이 이에 해당합니다.

- **Managed Volumes를 사용할 수 없을 때, 로깅이나 체크포인팅 파일과 같은 운영 데이터를 저장하는 경우에 사용합니다.**

**External Volumes 사용 시 추가 권장 사항:**

- Databricks는 하나의 스키마 내 하나의 External Location에서 External Volumes를 생성하도록 권장합니다.

{% hint style="info" %}
**팁**: 데이터가 다른 위치로 복사되는 수집 사용 사례(예: Auto Loader 또는 `COPY INTO` 사용)에는 External Volumes를 사용하십시오. 복사 없이 데이터를 테이블로 직접 쿼리하려면 External Tables를 사용하십시오.
{% endhint %}

자세한 내용은 **Managed versus external volumes** 및 **External locations** 를 참고하십시오.

---

## 외부 위치 (External locations)

External Location(외부 위치) 보안 개체는 스토리지 자격증명(Storage Credentials)과 스토리지 경로를 결합하여 스토리지 접근에 대한 강력한 제어와 감사 가능성을 제공합니다. Unity Catalog가 제공하는 접근 제어를 우회하여 External Location으로 등록된 버킷에 사용자가 직접 접근하는 것을 방지하는 것이 중요합니다.

**External Locations를 효과적으로 활용하기 위한 방법:**

- **External Location으로 사용되는 버킷에 직접 접근할 수 있는 사용자 수를 제한합니다.**

- **External Location으로도 사용되는 스토리지 계정은 DBFS에 마운트하지 않습니다.** Databricks는 Catalog Explorer를 사용하여 클라우드 스토리지 위치의 마운트를 Unity Catalog의 External Locations로 마이그레이션할 것을 권장합니다.

- **External Location 생성 권한은 Unity Catalog와 클라우드 스토리지 간 연결 설정을 담당하는 관리자 또는 신뢰할 수 있는 데이터 엔지니어에게만 부여합니다.**

  External Location은 클라우드 스토리지 내 광범위한 위치(예: 전체 버킷 `s3://mycompany-hr-prod` 또는 광범위한 하위 경로 `s3://mycompany-hr-prod/unity-catalog`)에 대한 접근을 Unity Catalog 내에서 제공합니다. 의도된 패턴은 클라우드 관리자가 몇 개의 External Location을 설정한 후, 해당 위치 관리 책임을 조직 내 Databricks 관리자에게 위임하는 것입니다. Databricks 관리자는 External Location 내 특정 접두사(Prefix)에 External Volumes 또는 External Tables를 등록하여 더 세분화된 권한으로 외부 위치를 구성할 수 있습니다.

  External Location은 매우 광범위한 범위를 가지기 때문에, Databricks는 `CREATE EXTERNAL LOCATION` 권한을 Unity Catalog와 클라우드 스토리지 간 연결 설정을 담당하는 관리자나 신뢰할 수 있는 데이터 엔지니어에게만 부여하도록 권장합니다. 다른 사용자에게 더 세분화된 접근을 제공하려면 External Location 위에 External Tables 또는 Volumes를 등록하고 사용자에게 볼륨 또는 테이블을 통해 데이터 접근 권한을 부여하는 것이 좋습니다. 테이블과 볼륨은 카탈로그 및 스키마의 하위 객체이므로, 카탈로그 또는 스키마 관리자가 접근 권한에 대한 최종 제어권을 갖습니다.

  또한 External Location을 특정 워크스페이스에 바인딩하여 접근을 제어할 수 있습니다. 자세한 내용은 **Assign an external location to specific workspaces** 를 참고하십시오.

- **엔드유저에게 External Locations에 대한 일반적인 `READ FILES` 또는 `WRITE FILES` 권한을 부여하지 않습니다.**

  사용자는 테이블, 볼륨 또는 관리형 위치 생성 외에는 External Location을 사용해서는 안 됩니다. 데이터 사이언스 또는 기타 비테이블 데이터 사용 사례에 대한 경로 기반 접근에 External Location을 사용해서는 안 됩니다.

  비테이블 데이터에 대한 경로 기반 접근에는 Volumes를 사용하십시오. 볼륨 경로 아래의 데이터에 대한 클라우드 URI 접근은 External Location에 부여된 권한이 아닌, 볼륨에 부여된 권한에 의해 제어됩니다.

  Volumes는 SQL 명령어, `dbutils`, Spark API, REST API, Terraform, 그리고 파일 탐색, 업로드, 다운로드를 위한 UI를 사용하여 파일을 다룰 수 있게 합니다. 또한 Volumes는 `/Volumes/<catalog_name>/<schema_name>/<volume_name>/` 경로 아래 로컬 파일 시스템에서 접근 가능한 FUSE 마운트를 제공합니다. 이 FUSE 마운트를 통해 데이터 과학자와 ML 엔지니어는 많은 머신러닝 또는 운영체제 라이브러리에서 요구하는 것처럼 파일을 로컬 파일 시스템에 있는 것처럼 접근할 수 있습니다.

  External Location의 파일에 직접 접근을 허용해야 하는 경우(예: 사용자가 External Table 또는 Volume 생성 전에 클라우드 스토리지의 파일을 탐색하는 경우), `READ FILES` 를 부여할 수 있습니다. `WRITE FILES` 를 부여하는 사용 사례는 드뭅니다.

- **경로 충돌을 피하기 위해 External Location의 루트에 External Volumes 또는 Tables를 생성하지 않습니다.**

  External Location 루트에 External Volumes 또는 Tables를 생성하면, 해당 External Location에 추가 External Volumes나 Tables를 생성할 수 없습니다. 대신 External Location 내부의 하위 디렉토리에 External Volumes 또는 Tables를 생성하십시오.

  External Location과 워크스페이스 기본 Unity Catalog 스토리지 간 스토리지 충돌이 발생하면, **Resolve storage path conflicts** 를 참고하십시오.

- **최적의 파일 처리 성능을 위해 파일 이벤트(File Events)를 활성화합니다.**

  External Location에 파일 이벤트가 활성화되면, Databricks는 클라우드 제공업체의 변경 알림을 처리하여 수집 메타데이터를 추적합니다. 이를 통해 파일 도착 트리거 및 Auto Loader와 같은 다운스트림 기능의 성능과 안정성이 향상됩니다.

**External Location은 다음 목적으로만 사용해야 합니다:**

- `CREATE EXTERNAL VOLUME` 또는 `CREATE TABLE` 명령어를 사용하여 External Tables 및 Volumes를 등록하는 것.

- 위치를 관리형 스토리지로 등록하는 것. `CREATE MANAGED STORAGE` 권한이 전제 조건입니다.

- 특정 접두사에 External Table 또는 Volume을 생성하기 전에 클라우드 스토리지에서 기존 파일을 탐색하는 것. `READ FILES` 권한이 전제 조건이며, 이 권한은 신중하게 할당하십시오.

### External Locations와 External Volumes 비교

Volumes가 출시되기 전, 일부 Unity Catalog 구현에서는 데이터 탐색을 위해 External Location에 직접 `READ FILES` 접근을 할당했습니다. 정형, 반정형, 비정형 데이터를 포함한 모든 형식의 파일을 등록하는 Volumes의 가용성으로 인해, 테이블, 볼륨, 또는 관리형 위치를 생성하는 것 외에 External Location을 직접 사용할 이유가 실질적으로 없어졌습니다. External Location을 사용해야 하는 경우와 Volumes를 사용해야 하는 경우에 대한 자세한 내용은 **Managed and external volumes** 및 **External locations** 를 참고하십시오.

---

## 크로스 리전 및 크로스 플랫폼 공유 (Cross-region and cross-platform sharing)

리전당 하나의 메타스토어만 가질 수 있습니다. 다른 리전의 워크스페이스 간에 데이터를 공유하려면 **Databricks-to-Databricks Delta Sharing** 을 사용하십시오.

**모범 사례:**

- **모든 소프트웨어 개발 수명 주기(SDLC) 범위와 비즈니스 단위(예: dev, test, prod, sales, marketing)에 단일 리전 메타스토어를 사용합니다.** 자주 공유 데이터에 접근해야 하는 워크스페이스가 동일한 리전에 위치하도록 하십시오.

- **클라우드 리전 또는 클라우드 제공업체 간에는 Databricks-to-Databricks Delta Sharing을 사용합니다.**

- **접근 빈도가 낮은 테이블에는 Delta Sharing을 사용합니다.** 클라우드 리전 간 이그레스(Egress) 비용을 직접 부담해야 하기 때문입니다. 리전 또는 클라우드 제공업체 간에 자주 접근하는 데이터를 공유해야 하는 경우, **Monitor and manage Delta Sharing egress costs (for providers)** 를 참고하십시오.

**Databricks-to-Databricks 공유 사용 시 다음 제한 사항을 유의하십시오:**

- **리니지 그래프(Lineage Graph)는 메타스토어 수준에서 생성되며 리전 또는 플랫폼 경계를 넘지 않습니다.** 이는 동일한 Databricks 계정 내 메타스토어 간에 리소스를 공유하는 경우에도 마찬가지입니다. 소스의 리니지 정보는 대상에서 볼 수 없으며, 그 반대도 마찬가지입니다.

- **접근 제어(Access Control)는 메타스토어 수준에서 정의되며 리전 또는 플랫폼 경계를 넘지 않습니다.** 리소스에 권한이 할당되어 있고 해당 리소스가 계정 내 다른 메타스토어에 공유되더라도, 해당 리소스의 권한은 대상 공유(Destination Share)에 적용되지 않습니다. 대상에서 대상 공유에 대한 권한을 별도로 부여해야 합니다.

---

## 컴퓨트 설정 (Compute configurations)

Databricks는 규칙 집합을 기반으로 클러스터 구성 능력을 제한하기 위해 **컴퓨트 정책(Compute Policies)** 을 사용하도록 권장합니다. 컴퓨트 정책을 사용하면 사용자가 Unity Catalog가 활성화된 클러스터, 즉 **Standard Access Mode** (이전의 Shared Access Mode) 또는 **Dedicated Access Mode** (이전의 Single-User 또는 Assigned Access Mode)를 사용하는 클러스터만 생성하도록 제한할 수 있습니다.

이러한 접근 모드 중 하나를 사용하는 클러스터만 Unity Catalog의 데이터에 접근할 수 있습니다. 모든 서버리스(Serverless) 컴퓨트 및 DBSQL 컴퓨트는 Unity Catalog를 지원합니다.

Databricks는 **모든 워크로드에 Standard Access Mode를 권장합니다.** 필요한 기능이 Standard Access Mode에서 지원되지 않는 경우에만 Dedicated Access Mode를 사용하십시오. 자세한 내용은 **Access modes** 를 참고하십시오.

---

*© Databricks 2026. All rights reserved. Apache, Apache Spark, Spark 및 Spark 로고는 Apache Software Foundation의 상표입니다.*
