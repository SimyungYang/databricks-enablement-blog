# Databricks Geo (데이터 거주)

## 1. Databricks Geo란?

### 정의

**Databricks Geo** 는 고객 데이터의 처리 위치에 대한 **예측 가능성과 투명성** 을 제공하기 위해, Databricks가 클라우드 데이터센터 리전들을 논리적으로 그룹화한 제도입니다. 각 Geo는 하나 이상의 클라우드 리전을 포함하며, 고객은 자신의 워크스페이스가 어느 Geo에 속하는지에 따라 데이터가 처리되는 물리적 범위를 파악할 수 있습니다.

### 왜 등장했는가

데이터 주권(Data Sovereignty) 규제가 전 세계적으로 강화되면서, 기업은 데이터가 **어디에서 저장되고 어디에서 처리되는지** 를 명확히 통제해야 하는 요구에 직면했습니다.

- **EU GDPR**: 개인정보가 EEA 외부로 이전될 경우 적정성 결정 또는 표준 계약 조항(SCC) 등 법적 근거가 필요
- **한국 개인정보보호법**: 국외 이전 시 정보주체 동의 또는 보호위원회 인정이 필요
- **중국 PIPL, 브라질 LGPD** 등: 각국이 자국 내 데이터 처리를 요구하는 법안을 시행

기존에는 고객이 워크스페이스 리전을 선택하더라도, Databricks의 일부 관리형 서비스(AI 어시스턴트, Foundation Model API 등)가 **다른 리전에서 데이터를 처리** 할 수 있었고, 이에 대한 투명성이 부족했습니다. Databricks Geo는 이 문제를 해결하기 위해 도입되었습니다.

### 핵심 원칙

{% hint style="info" %}
**기본 동작**: 고객 데이터는 워크스페이스와 동일한 Geo 내에서만 처리됩니다. Cross-Geo 처리를 명시적으로 활성화하지 않는 한, 데이터는 해당 Geo 경계를 벗어나지 않습니다.
{% endhint %}

---

## 2. Geo 목록 및 포함 리전

Databricks는 현재 7개의 Geo를 정의하고 있습니다. 각 Geo에 속하는 국가/지역은 아래 테이블과 같습니다. 워크스페이스를 생성할 때 선택한 클라우드 리전이 어느 Geo에 매핑되는지 확인하여, 데이터 처리 범위를 파악할 수 있습니다.

| Geo | 포함 국가/지역 |
|-----|---------------|
| **Americas** | 미국, 브라질, 캐나다 |
| **Asia** | 홍콩, 인도네시아, 일본, 한국, 싱가포르 |
| **Australia and New Zealand** | 호주, 뉴질랜드 |
| **Europe** | EEA(유럽경제지역), 스위스, 영국 |
| **India** | 인도 |
| **Mainland China** | 중국 본토 |
| **Middle East and Africa** | 카타르, 남아프리카, UAE |

이 Geo 구분은 단순히 지리적 편의가 아니라, **데이터 거주(Data Residency) 정책의 법적 경계** 로 작동합니다. 예를 들어 한국에서 생성한 워크스페이스는 Asia Geo에 속하며, Cross-Geo가 비활성화된 상태에서는 일본, 싱가포르 등 Asia Geo 내 리전에서만 데이터가 처리됩니다.

---

## 3. Designated Services (지정 서비스)

### Designated Services란?

**Designated Services** 는 Databricks Geo 정책에 따라 데이터 거주를 관리하는 **특정 기능 및 서비스** 를 의미합니다. 이 서비스들은 Geo 설정에 따라 데이터를 처리하는 위치가 결정되며, 고객이 Cross-Geo 설정을 통해 제어할 수 있습니다.

Designated Services가 아닌 일반 기능(예: 노트북 실행, SQL 쿼리, Job 실행 등)은 항상 워크스페이스가 배치된 **클라우드 리전 내** 에서 처리되므로 Geo 설정과 무관합니다.

### 전체 서비스 가용성 매트릭스

아래 테이블은 각 Designated Service가 어느 Geo에서 사용 가능한지, 그리고 Cross-Geo 활성화가 필요한지를 보여줍니다. 서비스별로 모델 제공자가 다르며, 이에 따라 가용 범위가 달라집니다.

| 서비스 | 모델 제공자 | Americas | Asia | ANZ | Europe | India | China | MEA |
|--------|-----------|----------|------|-----|--------|-------|-------|-----|
| Pay-per-token Foundation Model APIs | 모델 의존 | ✅ | ✅† | ✅* | ✅ | ✅ | ❌ | ❌ |
| AI Functions (배치 추론) | 모델 의존 | ✅ | ✅† | ✅* | ✅ | ✅* | ❌ | ❌ |
| Provisioned Throughput APIs | 모델 의존 | ✅ | ✅† | ✅ | ✅ | ✅ | ❌ | ❌ |
| Knowledge Assistant & Supervisor Agent | 모델 의존 | ✅ | ✅* | ✅* | ✅ | ❌ | ❌ | ❌ |
| Foundation Model Fine-tuning | 모델 의존 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| AI-generated comments | Databricks | ✅§ | ✅‡ | ✅* | ✅§ | ✅* | ✅* | ✅* |
| AI-based autocomplete | Databricks | ✅ | ✅* | ✅* | ✅ | ✅* | ✅* | ✅* |
| Genie Code Agent mode | Anthropic | ✅ | ✅ | ✅ | ✅ | ✅* | ✅* | ✅* |
| Genie Code chat & cell | Azure AI | ✅§ | ✅§ | ✅ | ✅§ | ✅ | ✅* | ✅* |
| Genie | Azure AI | ✅§ | ✅¶ | ✅ | ✅§ | ✅ | ❌ | ✅* |
| Genie Spaces Agent mode | Anthropic | ✅ | ✅† | ✅ | ✅ | ✅* | ✅* | ✅* |
| AI/BI dashboards | Azure AI | ✅§ | ✅§ | ✅ | ✅§ | ✅ | ✅* | ✅* |
| Data classification | Databricks | ✅ | ✅* | ✅ | ✅ | ✅* | ✅* | ✅* |

### 범례

| 기호 | 의미 |
|------|------|
| ✅ | 해당 Geo 내에서 처리 |
| ✅* | **Cross-Geo 처리 활성화 필요** — 다른 Geo의 인프라를 사용하여 처리 |
| ✅† | 일본, 한국, 싱가포르 리전에서 처리 (Asia Geo 내 특정 리전) |
| ✅‡ | AI-generated comments의 Asia Geo 특수 처리 |
| ✅§ | 국가별(country-level) 처리 — 동일 Geo 내에서도 국가 단위로 처리 위치가 구분됨 |
| ✅¶ | 싱가포르 등 일부 아시아 리전은 Cross-Geo 활성화 필요 |
| ❌ | 해당 Geo에서 미지원 |

이 테이블에서 주목할 점은 **Americas와 Europe** 이 가장 광범위한 서비스를 지원하며, **Foundation Model Fine-tuning** 은 현재 Americas에서만 사용 가능하다는 것입니다. Asia Geo는 대부분의 핵심 AI 서비스를 사용할 수 있지만, 일부 서비스는 특정 리전(일본, 한국, 싱가포르)으로 한정됩니다.

---

## 4. Cross-Geo 처리 설정

### 기본 동작

Databricks는 기본적으로 Designated Services의 데이터를 **워크스페이스 Geo 내에서만** 처리합니다. 이는 데이터 주권 규제를 준수하기 위한 가장 보수적인 설정입니다.

{% hint style="warning" %}
**예외**: US/EU 외 지역에서 **Compliance Security Profile** 이 없는 워크스페이스는 기본적으로 Cross-Geo 처리가 활성화되어 있습니다. 규제 준수가 필요하다면 반드시 설정을 확인하세요.
{% endhint %}

### Cross-Geo 활성화 방법

Cross-Geo 처리를 활성화하면, 해당 Geo에서 직접 지원하지 않는 서비스를 다른 Geo의 인프라를 빌려 사용할 수 있습니다.

**Account Console 접근 방법:**

1. [https://accounts.cloud.databricks.com](https://accounts.cloud.databricks.com) 접속 (Account Admin 권한 필요)
2. 좌측 메뉴에서 **Workspaces** 클릭
3. 설정을 변경할 워크스페이스를 검색/선택
4. **Security and compliance** 탭 클릭
5. **"Enforce data processing within workspace Geography for Designated Services"** 항목 확인

{% hint style="warning" %}
이 설정은 **Account Admin** 권한이 있어야 볼 수 있습니다. Workspace Admin 권한으로는 접근할 수 없으므로, 설정 확인이 필요하면 Account Admin에게 요청하세요.
{% endhint %}

이 옵션을 **비활성화** 하면 Cross-Geo 처리가 **활성화** 됩니다 (이중 부정에 주의). 즉:

- **Enforce = ON** (기본값): 데이터가 Geo 내에서만 처리됨 → Cross-Geo **비활성화**
- **Enforce = OFF**: 데이터가 다른 Geo에서도 처리될 수 있음 → Cross-Geo **활성화**

### 데이터 저장 vs 데이터 처리

{% hint style="info" %}
**중요 보장**: Cross-Geo 처리를 활성화하더라도, 데이터 **저장(storage)** 은 항상 워크스페이스 Geo 내에 유지됩니다. Cross-Geo는 데이터 **처리(processing)** 에만 적용됩니다. 즉, AI 모델 추론 시 데이터가 일시적으로 다른 Geo의 GPU에서 처리될 수 있지만, 그 결과는 원래 Geo로 돌아와 저장됩니다.
{% endhint %}

### Cross-Geo 활성화가 필요한 대표적 시나리오

- **ANZ(호주/뉴질랜드)** 에서 Foundation Model APIs를 사용하려는 경우 (✅*)
- **India** 에서 AI-based autocomplete, Data classification을 사용하려는 경우 (✅*)
- **Asia** 에서 Knowledge Assistant & Supervisor Agent를 사용하려는 경우 (✅*)
- **MEA** 에서 대부분의 AI 서비스를 사용하려는 경우

---

## 5. 한국 고객을 위한 실전 가이드

### 한국의 Geo 위치

한국은 **Asia Geo** 에 속합니다. Asia Geo에는 홍콩, 인도네시아, 일본, 한국, 싱가포르가 포함되어 있으며, 한국 리전(ap-northeast-2)에서 생성한 워크스페이스는 자동으로 Asia Geo로 분류됩니다.

### 사용 가능한 서비스 요약

아래 테이블은 한국 고객이 Asia Geo에서 사용할 수 있는 서비스와 Cross-Geo 필요 여부를 정리한 것입니다.

| 서비스 | 한국에서 사용 가능? | Cross-Geo 필요? | 비고 |
|--------|-------------------|----------------|------|
| Pay-per-token Foundation Model APIs | ✅ | 불필요 | 일본/한국/싱가포르 리전에서 처리 |
| AI Functions (배치 추론) | ✅ | 불필요 | 일본/한국/싱가포르 리전에서 처리 |
| Provisioned Throughput APIs | ✅ | 불필요 | 일본/한국/싱가포르 리전에서 처리 |
| Knowledge Assistant & Supervisor Agent | ✅ | **필요** | Cross-Geo 활성화 시 사용 가능 |
| Foundation Model Fine-tuning | ❌ | — | Americas만 지원 |
| AI-generated comments | ✅ | 조건부 | Asia Geo 내 특수 처리 |
| AI-based autocomplete | ✅ | **필요** | Cross-Geo 활성화 시 사용 가능 |
| Genie Code Agent mode | ✅ | 불필요 | Anthropic 모델, Asia Geo 내 처리 |
| Genie Code chat & cell | ✅ | 불필요 | 국가별 처리 |
| Genie | ✅ | 조건부 | 싱가포르 등 일부 리전은 Cross-Geo 필요 |
| Genie Spaces Agent mode | ✅ | 불필요 | 일본/한국/싱가포르 리전에서 처리 |
| AI/BI dashboards | ✅ | 불필요 | 국가별 처리 |
| Data classification | ✅ | **필요** | Cross-Geo 활성화 시 사용 가능 |

한국 고객은 대부분의 핵심 AI 서비스를 Cross-Geo 없이 사용할 수 있으나, Knowledge Assistant, AI autocomplete, Data classification 등 일부 서비스는 Cross-Geo 활성화가 필요합니다.

### 개인정보보호법 관점에서의 고려사항

{% hint style="warning" %}
**한국 개인정보보호법 관련**: Cross-Geo를 비활성화(Enforce = ON)하면, 데이터가 Asia Geo 외부로 나가지 않으므로 국외 이전에 해당하지 않습니다. 단, Cross-Geo를 활성화하면 데이터가 Americas 또는 Europe Geo에서 처리될 수 있으므로, 개인정보가 포함된 데이터를 다루는 경우 **정보주체 동의** 또는 **보호위원회 인정** 등 법적 근거를 확보해야 합니다.
{% endhint %}

### 실전 트러블슈팅

**"AI 어시스턴트 기능이 동작하지 않습니다"**

1. **Cross-Geo 설정 확인**: Account Console에서 해당 워크스페이스의 Cross-Geo 설정을 확인합니다.
2. **서비스별 요구 확인**: 위 테이블에서 해당 서비스가 Cross-Geo를 필요로 하는지 확인합니다.
3. **Compliance Security Profile 확인**: 워크스페이스에 Compliance Security Profile이 설정되어 있다면, Cross-Geo가 기본적으로 비활성화되어 있을 수 있습니다.

**"Foundation Model Fine-tuning을 사용하고 싶습니다"**

- 현재 Americas Geo에서만 지원됩니다. 한국 리전에서는 사용할 수 없으며, Cross-Geo를 활성화해도 지원되지 않습니다.
- 대안: Americas 리전(예: us-west-2)에 별도의 워크스페이스를 생성하여 Fine-tuning을 수행하고, 결과 모델을 한국 리전의 Provisioned Throughput로 배포하는 방식을 고려할 수 있습니다.

---

## 6. Compute Plane과 데이터 처리 위치

Databricks Geo는 **Designated Services** 에 적용되는 정책이며, 일반적인 컴퓨팅 작업은 컴퓨트 플레인 유형에 따라 처리 위치가 결정됩니다.

### Classic Compute Plane

Classic compute는 고객의 클라우드 계정 내에서 실행됩니다. 데이터 처리는 워크스페이스가 배치된 **클라우드 리전 내** 에서만 이루어지며, Geo 설정과 무관하게 리전 경계를 벗어나지 않습니다.

### Serverless Compute

Serverless compute는 Databricks가 관리하는 인프라에서 실행되지만, 고객이 선택한 **클라우드 리전 내** 에서만 처리됩니다. Serverless SQL Warehouse, Serverless Notebook, Serverless Job 모두 동일한 원칙을 따릅니다.

### Preview 기능

{% hint style="info" %}
Public Preview 또는 Private Preview 단계의 기능은, 별도의 명시가 없는 한 워크스페이스의 **Geo 설정을 따릅니다** . 그러나 Preview 기능의 데이터 거주 보장은 GA(General Availability) 기능보다 제한적일 수 있으므로, 규제가 엄격한 환경에서는 Preview 기능의 데이터 처리 위치를 Databricks 지원팀에 확인하는 것을 권장합니다.
{% endhint %}

### 아키텍처 요약

| 컴퓨트 유형 | 데이터 처리 위치 | Geo 설정 적용 |
|------------|----------------|--------------|
| Classic Compute | 고객 클라우드 계정, 워크스페이스 리전 내 | 해당 없음 (리전 내 고정) |
| Serverless Compute | Databricks 관리 인프라, 선택 리전 내 | 해당 없음 (리전 내 고정) |
| Designated Services | Databricks 관리 인프라 | **Geo 설정 적용** |
| Preview 기능 | Databricks 관리 인프라 | Geo 설정 따름 (보장 수준 GA 대비 제한적) |

이 테이블이 보여주는 핵심은, Geo 설정이 실질적으로 영향을 미치는 것은 **Designated Services뿐** 이라는 점입니다. 일반 컴퓨팅 워크로드는 항상 선택한 리전 내에서 처리되므로, Geo 설정 변경이 기존 ETL, SQL, ML 파이프라인에 영향을 주지 않습니다.

---

## 참고 링크

- [Databricks Geographic Regions (Geos)](https://docs.databricks.com/en/resources/supported-regions.html#databricks-geographic-regions-geos)
- [Designated Services](https://docs.databricks.com/en/resources/supported-regions.html#designated-services)
- [Cross-Geo processing](https://docs.databricks.com/en/admin/workspace-settings/cross-geo.html)
