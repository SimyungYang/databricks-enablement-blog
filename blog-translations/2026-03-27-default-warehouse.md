# Default Warehouse로 성능을 보호하고 예상치 못한 비용을 줄이세요

**관리자가 임시(ad hoc) 워크로드에 최적화된 웨어하우스를 설정해, 사용자는 분석에만 집중할 수 있게 합니다**

작성자: JooHo Yeo, Gabriel Dutra Dias | 2026년 3월 27일

> **원문**: [Protect Performance and Reduce Surprise Costs with Default Warehouse](https://www.databricks.com/blog/protect-performance-and-reduce-surprise-costs-default-warehouse)

![Default Warehouse OG Image](https://www.databricks.com/sites/default/files/2026-03/DW_OG.png?v=1774648931)

---

{% hint style="info" %}
**요약**
- 대규모 프로덕션 웨어하우스가 임시 브라우징으로 불필요하게 시작되는 것을 방지합니다
- 임시 쿼리가 의도된 웨어하우스로 라우팅되어 핵심 워크로드가 성능 경합 없이 실행될 수 있도록 합니다
- SQL Editor, Catalog Explorer, AI/BI Dashboards, Alerts, Genie Spaces 등 임시 SQL 서피스 전반에 걸쳐 기본 동작을 표준화하여 비용 및 워크로드 거버넌스를 대규모로 개선합니다
{% endhint %}

---

**Default Warehouse** 는 이제 Databricks SQL에서 일반 공급(GA)되며, 관리자가 임시 환경에서 자동으로 선택될 SQL 웨어하우스를 지정할 수 있도록 합니다. Default Warehouse는 사용자가 어떤 웨어하우스를 선택해야 하는지 알지 않아도, 탐색 쿼리가 올바른 컴퓨팅에서 적절한 비용으로 실행되도록 보장합니다.

의도치 않은 웨어하우스 시작 감소, 더 나은 워크로드 격리, 그리고 예측 가능한 성능과 지출이 실현됩니다.

## 오늘날 웨어하우스 선택의 문제점

Databricks SQL 도입이 확대될수록 워크스페이스 내 웨어하우스 수도 늘어납니다. 고객들은 ETL, BI, 임시 쿼리 등 목적에 따라 별도의 웨어하우스를 프로비저닝하고, 필요한 가격 대비 성능 목표에 맞게 크기(예: T-shirt 사이즈, 최대 클러스터 수)를 조정하는 것이 일반적입니다.

프로덕션 ETL 및 BI 워크로드의 경우 특정 웨어하우스가 관련 자산이나 도구에 연결되어 있습니다. 그러나 임시 쿼리의 경우 사전에 지정된 웨어하우스가 없어, 사용자가 직접 수동으로 선택해야 합니다.

구성 가능한 기본값이 없으면 시스템은 "Last Selected(마지막 선택)" 동작이나 알파벳 순서로 폴백(fallback)됩니다. 이로 인해 다음과 같은 문제가 발생할 수 있습니다:

- **성능 저하** — 임시 쿼리가 대형 프로덕션 웨어하우스에 떨어져 핵심 워크로드와 리소스를 두고 경합하게 됩니다
- **예측 불가한 비용** — 가벼운 탐색 쿼리를 위해 대형 웨어하우스가 불필요하게 시작됩니다
- **거버넌스 문제** — 탐색 목적의 쿼리가 팀 전용 또는 애플리케이션 전용 웨어하우스에서 실행됩니다

Default Warehouse는 이 문제를 직접적으로 해결합니다.

## 해결책: Default Warehouse

Default Warehouse는 관리자가 SQL Editor, Catalog Explorer, AI/BI Dashboards, Alerts, Genie Spaces를 포함한 임시 SQL 서피스에 대해 워크스페이스 수준의 단일 기본 SQL 웨어하우스를 설정할 수 있도록 합니다.

사용자는 필요한 경우(예: 전용 웨어하우스를 가진 파워 유저) 자신의 Default Warehouse를 커스터마이즈할 수 있습니다. 관리자는 사용자가 설정한 Default Warehouse에 대한 가시성과 최종 제어권을 가집니다.

이를 통해 두 수준 모두에서 유연성이 확보됩니다:

- 관리자는 대부분의 임시 워크로드를 의도한 웨어하우스로 유도합니다.
- 대부분의 사용자는 웨어하우스 선택을 고민하지 않아도 되고, 파워 유저는 자신의 워크플로우에 맞는 Default Warehouse를 직접 선택할 수 있습니다.

결과적으로 임시 워크로드는 의도된 웨어하우스에서 실행되어 관리자에게는 비용 절감을, 사용자에게는 시간 절약을 가져다줍니다.

## 고객을 통해 검증된 효과

이미 300개 이상의 고객이 Default Warehouse를 사용했으며, 그 가치는 명확하고 일관되게 나타났습니다:

- **탐색 쿼리 비용 절감에 효과적**: 관리자가 Default Warehouse를 소형 웨어하우스로 설정한 워크스페이스에서, Catalog Explorer 쿼리가 소형 웨어하우스로 라우팅되는 비율이 **77%에서 96%** 로 증가했습니다.
- **수동 웨어하우스 선택 필요성 감소에 효과적**: 여러 웨어하우스에서 임시 SQL을 실행하는 사용자 수가 **15% 감소** 했습니다. 사용자는 이제 컴퓨팅 선택이 아니라 분석에 집중할 수 있습니다.

고객들은 프로덕션 워크로드에서 이미 실질적인 효과를 체감하고 있습니다.

> "Default Warehouse 설정을 사용함으로써, 프로덕션 대시보드 SQL 웨어하우스의 부적절한 사용을 거의 완전히 없앨 수 있었습니다. 성능 문제를 분류하는 속도도 훨씬 빨라졌습니다."
>
> — Michael Woffendin, Senior Engineering Manager, Rivian

---

{% hint style="info" %}
**가이드**

현대 분석을 위한 간결한 가이드

[지금 읽기](https://www.databricks.com/resources/ebook/compact-guide-to-modern-analytics)
{% endhint %}

---

## 기능 상세

### 1. 관리자를 위한 워크스페이스 수준 기본값 설정

관리자는 **Workspace Settings → Compute** 에서 단일 기본 SQL 웨어하우스를 구성할 수 있습니다.

- 임시 SQL 서피스 전체에 적용됩니다
- 기존 거버넌스 및 액세스 제어를 준수하며 serverless, pro, classic SQL 웨어하우스를 지원합니다
- 옵트인 방식 (워크스페이스 수준 기본값이 설정되지 않은 경우 "Last Selected" 동작)
- 새로 생성되는 자산에 자동으로 선택됩니다

![compute level default warehouse](https://www.databricks.com/sites/default/files/inline-images/image4_8.gif?v=1774895778)

### 2. 유연성을 위한 사용자 수준 커스터마이제이션

사용자는 **Warehouse Dropdown → Customize your default warehouse** 에서 자신만의 재정의(override)를 구성할 수 있습니다:

- 워크스페이스 기본 웨어하우스 확인 (스크린샷의 "alp-sql-controltower")
- 옵트아웃 (override가 설정되지 않은 경우 워크스페이스 수준 기본값을 따름)
- 다른 웨어하우스로 재정의하거나, 원하는 경우 "Last Selected" 선택 가능

![user level default warehouse](https://www.databricks.com/sites/default/files/inline-images/image1_27.gif?v=1774895778)

### 3. 커스터마이제이션 및 거버넌스를 위한 관리자 API

관리자가 각 사용자에게 서로 다른 웨어하우스를 할당할 수 있도록, 사용자 수준 기본값을 조회하고 설정하는 API를 새롭게 추가했습니다. 이를 통해 관리자는 다음을 수행할 수 있습니다:

- 사용자가 속한 팀에 따라 프로그래밍 방식으로 각 사용자에게 다른 웨어하우스 설정
- 사용자 수준 재정의를 설정한 사용자 감사(audit)
- 각 사용자의 Default Warehouse 선택에 대한 최종 제어권 확보

**예제 1**: "finance" 그룹의 모든 사용자에 대해 Default Warehouse 설정

**예제 2**: 자신의 Default Warehouse를 직접 설정한 모든 사용자 감사

전체 API 레퍼런스는 [Databricks 공식 문서](https://docs.databricks.com/aws/en/sql/user/warehouses/default-warehouse.html)를 참조하세요.

이 API는 [Terraform 리소스](https://registry.terraform.io/providers/databricks/databricks/latest/docs)로도 사용 가능합니다.

## 다음 단계

저희는 Default Warehouse를 Databricks UI를 넘어 MLflow, Lakeflow CLI, DBSQL MCP 등 플랫폼 외부(off-platform) 소스를 포함한 임시 워크로드까지 지원하도록 확장하고 있습니다.

Databricks SQL 관리 경험을 더욱 개선하기 위해 원하시는 기능이 있다면 언제든지 알려주세요!

## 지금 바로 Default Warehouse를 사용해 보세요

핵심 워크로드의 성능을 보호하고 예상치 못한 비용을 줄이려면, Default Warehouse를 사용하여 임시 쿼리를 올바른 웨어하우스로 유도하세요. Default Warehouse는 현재 일반 공급(GA) 상태입니다. 시작하려면 [Databricks 공식 문서](https://docs.databricks.com/aws/en/sql/user/warehouses/default-warehouse.html)를 참조하세요.
