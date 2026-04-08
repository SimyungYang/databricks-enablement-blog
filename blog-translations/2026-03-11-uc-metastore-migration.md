# 엔터프라이즈 규모 거버넌스: Hive Metastore에서 Unity Catalog로 마이그레이션

**대규모·복잡한 워크로드를 Hive Metastore에서 Unity Catalog로 마이그레이션하는 방법 — 데이터 거버넌스와 성능 최적화를 중단 없이 달성하기**

작성자: Josh Bae, Dhaval Bagadia | 2025년 10월 17일

> **원문**: [Enterprise-Scale Governance: Migrating from Hive Metastore to Unity Catalog](https://www.databricks.com/blog/enterprise-scale-governance-migrating-hive-metastore-unity-catalog)

![Enterprise-Scale Governance Hero Image](https://www.databricks.com/sites/default/files/2025-10/enterprise-scale-governance-og.png?v=1759930657)

---

{% hint style="info" %}
**요약**

- 조직이 성장할수록 레거시 Hive Metastore(HMS)는 거버넌스 공백, 사일로화된 접근, 운영 병목을 초래합니다. Unity Catalog(UC)는 모든 데이터 및 AI 자산에 대한 통합 거버넌스 모델을 제공합니다.
- 신중한 Metastore 및 Catalog 설계, Infrastructure as Code(IaC)를 활용한 자동화, 파일럿 기반 단계적 도입을 통해 마이그레이션 위험을 최소화할 수 있습니다.
- HMS Federation을 통한 Soft Migration은 코드 변경 없이 Unity Catalog 거버넌스를 단계적으로 채택하게 해주며, Hard Migration은 Unity Catalog의 모든 기능을 완전히 활용하고 HMS를 완전히 퇴역시킬 수 있게 합니다.
{% endhint %}

---

## 데이터 환경의 복잡성

기업이 디지털·데이터 역량을 계속해서 확장함에 따라 데이터 인프라의 복잡성은 커지고, 지속적인 가치 창출은 시기 적절하고 신뢰할 수 있으며 접근 가능한 정보에 달려 있습니다. 그러나 레거시 Hive Metastore(HMS) 환경에서는 조직들이 분산된 접근 제어, 불일치하는 메타데이터, 끝없이 이어지는 권한 검토라는 문제를 안고 씨름하는 경우가 많습니다.

HMS는 근본적으로 리니지(lineage) 추적, 다중 워크스페이스 거버넌스, 현대적인 보안 제어 기능이 부족합니다. 예를 들어, 레거시 Databricks 워크스페이스별 HMS에 의존하는 사용자들은 중복된 정책과 파편화된 접근 가시성 문제를 겪습니다.

Unity Catalog(UC)는 Databricks Data Intelligence Platform의 모든 데이터 및 AI 자산에 대한 통합 거버넌스 모델을 도입함으로써 이러한 과제들을 해결합니다. 세분화된 접근 제어, 중앙화된 감사, 엔드투엔드 리니지를 갖춘 Unity Catalog는 엔터프라이즈 데이터 거버넌스의 새로운 기준을 정의합니다.

### 지금 이 시점이 중요한 이유

이 마이그레이션 가이드가 나온 시점은 매우 중요합니다. 지난 수년간 Unity Catalog로 마이그레이션하는 데 필요한 것들에 대한 이해와 툴링이 크게 발전했습니다. 이 블로그는 대규모의 복잡한 워크로드를 마이그레이션하기 위한 최신 지침을 요약한 것입니다.

이 블로그는 레거시 Databricks 워크스페이스별 HMS(내부 HMS라고 함) 및 외부 HMS(AWS Glue 등)에서 마이그레이션하기 위한 가이드를 제공하며, 다음 주제를 다룹니다:

- 통제권을 포기하지 않으면서 자율성을 지원하는 거버넌스 모델 평가
- 위험과 중단을 최소화하는 확장 가능한 아키텍처 설계 및 실행
- 안전한 셀프서비스 데이터 접근을 지원하는 거버넌스 운영화
- 데이터 자산 마이그레이션 전에 Unity Catalog를 사용하는 새로운 워크로드 구축
- 마이그레이션 및 전환(cutover) 기간 중 중단 최소화

---

## 핵심 아키텍처 고려사항

HMS에서 Unity Catalog로 마이그레이션하는 것은 조직에게 데이터 아키텍처를 현대화할 기회를 제공합니다. 그러나 Unity Catalog의 완전한 가치를 실현하려면 세심한 설계 결정이 필요하며, 특히 Metastore와 Catalog 구조에서 그렇습니다.

전반적인 원칙은 동일하게 유지되지만, 특정 툴과 마이그레이션 방식은 Metastore의 유형에 따라 다르게 동작할 수 있습니다. 이러한 차이점으로 인해 마이그레이션 전에 툴 호환성과 기능 가용성을 평가하는 것이 중요합니다.

### Metastore 설계

Unity Catalog에서 메타데이터를 위한 최상위 컨테이너인 Metastore는 거버넌스 모델의 토대입니다. 카탈로그를 주요 격리 단위로 정의함으로써 계정의 접근 제어 프레임워크를 고정합니다.

이 섹션은 Metastore 설계 원칙에 중점을 둡니다. Infrastructure as Code(IaC)를 통해 Unity Catalog Metastore를 프로비저닝하는 기술적 세부사항은 이후 "Infrastructure as Code를 통한 자동화 배포" 섹션에서 다룹니다.

Unity Catalog 개념(Metastore, 관리 스토리지, 접근 제어 포함)에 대한 배경 정보는 [What is Unity Catalog?](https://docs.databricks.com/aws/en/data-governance/unity-catalog/) (AWS | Azure | GCP)를 참조하세요.

Unity Catalog는 리전당 하나의 Metastore를 지원하지만, 데이터 도메인 전반에 걸쳐 논리적·물리적 격리를 적용하는 여러 메커니즘을 제공합니다. 이를 통해 단일 Metastore 전략이 규모에 맞게 실용적으로 운영될 수 있습니다.

실제로 대부분의 팀은 단일 Metastore를 채택하고, 엄격한 지역적 격리가 규제 또는 컴플라이언스 요구사항이 아닌 한 여러 Metastore를 프로비저닝하는 대신 카탈로그와 스키마를 사용하여 경계를 적용합니다.

지역 간 또는 클라우드 플랫폼 간 데이터 공유 방법은 [Cross-region and cross-platform sharing](https://docs.databricks.com/aws/en/delta-sharing/index.html) (AWS | Azure | GCP)을 참조하세요.

#### 핵심 격리 메커니즘

Unity Catalog는 단일 Metastore 아키텍처 내에서 데이터 경계를 강제하고 분산 거버넌스를 가능하게 하기 위해 함께 작동하는 네 가지 핵심 격리 메커니즘을 제공합니다.

아래 표는 각 메커니즘의 기능을 요약한 것입니다. 이 네 가지가 어떻게 서로를 보완하는지 이해하는 것이 효과적인 Metastore 설계의 출발점입니다.

| 기능 | 목적 |
|---|---|
| 관리 위임 (Delegation of Management) | Unity Catalog 객체 소유권 모델을 통해 카탈로그, 스키마, 테이블의 소유권과 관리 제어를 도메인별 팀에 위임 |
| 워크스페이스-카탈로그 바인딩 (Workspace-Catalog Binding) | 특정 워크스페이스가 접근할 수 있는 카탈로그를 제한하여 개발과 프로덕션 워크로드 간의 환경 분리 보장 |
| 세분화된 접근 제어 (Fine-Grained Access Control) | 계층적 권한, 행 필터, 열 마스크를 적용하여 테이블 및 열 수준에서 정확한 데이터 보안 요구사항 강제 |
| 스토리지 격리 (Storage Isolation) | 관리 스토리지 위치를 통해 카탈로그를 전용 클라우드 스토리지 컨테이너에 매핑하여 데이터 자산의 물리적 분리 제공 |

이 네 가지 메커니즘을 적절히 조합하면, 단일 Metastore만으로도 엔터프라이즈 수준의 격리와 거버넌스를 구현할 수 있습니다.

![Unity Catalog 격리 옵션](https://www.databricks.com/sites/default/files/inline-images/enterprise-scale-governance-image-1.png)

**관리 위임 (Admin Isolation)**

Unity Catalog의 객체 소유권 모델은 각 카탈로그, 스키마, 테이블에 단일 소유자를 할당하면서 제어된 위임을 허용합니다. 객체 소유자 또는 메타스토어 관리자는 다른 사용자나 그룹에 권한을 부여할 수 있어 중앙화된 감독을 유지하면서 도메인별 관리가 가능합니다.

**워크스페이스-카탈로그 바인딩**

Unity Catalog는 [워크스페이스-카탈로그 바인딩](https://docs.databricks.com/aws/en/data-governance/unity-catalog/workspace-catalog-binding.html) (AWS | Azure | GCP)을 사용하여 어떤 워크스페이스가 어떤 카탈로그에 접근할 수 있는지를 정밀하게 제한합니다. 예를 들어 프로덕션 데이터 카탈로그는 프로덕션 워크스페이스에서만 접근 가능하도록 하여 개발 또는 스테이징 환경의 우발적인 접근을 방지할 수 있습니다.

**Unity Catalog 접근 제어**

Unity Catalog는 관리자가 메타스토어, 카탈로그, 스키마, 테이블 수준에서 정확한 권한을 부여할 수 있는 세분화되고 계층적인 역할 기반 접근 제어(RBAC)를 지원합니다.

- **권한 및 소유권**: 보안 가능한 객체에 권한을 부여하고 객체 소유권을 관리하여 누가 무엇에 접근할 수 있는지 정의합니다.
- **속성 기반 접근 제어(Beta)**: 태그와 유연한 중앙화 정책을 사용하여 사용자, 리소스 또는 환경 속성을 동적으로 평가하는 접근 제어를 구현합니다.
- **테이블 수준 필터링 및 마스킹**: 데이터에 직접 적용되는 행 수준 필터와 열 마스크를 통해 사용자가 테이블 내에서 볼 수 있는 데이터를 제어합니다.

자세한 내용은 [Access Control in Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/) (AWS | Azure | GCP)를 참조하세요.

**스토리지 격리**

Metastore가 지역적 격리를 제공하는 반면, 데이터 격리는 일반적으로 카탈로그 수준에서 이루어집니다. Databricks는 각 카탈로그에 자체 관리 스토리지 컨테이너를 할당할 것을 권장합니다.

- 외부 위치(external location)는 해당 자격증명을 특정 클라우드 경로 또는 컨테이너에 연결합니다. 외부 위치에 대한 권한이 부여된 사용자만 해당 경로의 데이터를 읽거나 쓸 수 있습니다.

이들은 특정 워크스페이스에 바인딩될 수도 있어, 권한이 있는 사용자만 민감한 데이터 경로에 접근할 수 있도록 보장합니다.

자세한 내용은 [Connect to cloud object storage using Unity Catalog](https://docs.databricks.com/aws/en/connect/unity-catalog/storage/) (AWS | Azure | GCP)를 참조하세요.

### Catalog 설계

잘 계획된 Metastore가 갖춰지면, 다음은 Catalog 설계로 관심이 옮겨집니다. 여기서 거버넌스 결정은 일상적인 데이터 사용과 만나게 됩니다. Metastore가 전반적인 접근 제어 평면을 확립하는 반면, Catalog는 도메인별 소유권과 데이터 제품 수명주기를 구성하는 수단입니다.

각 Catalog는 일반적으로 비즈니스 단위(BU), 기능적 도메인, 프로젝트 경계에 해당합니다. 이 매핑을 통해 팀은 거버넌스 표준과의 정합성을 유지하면서 데이터에 대한 자율성을 갖게 됩니다.

효과적인 카탈로그 전략은 비즈니스 도메인 경계와 소프트웨어 수명주기 단계를 반영합니다. 널리 채택되고 확장 가능한 패턴은 다음과 같습니다:

```
<비즈니스 단위>_<환경> → finance_dev, sales_stg, datascience_prod
```

이 명명 규칙은 다음을 가능하게 합니다:

- **명확한 소유권**: 각 Catalog는 전담 팀이 관리하는 BU 또는 도메인에 매핑됩니다.
- **환경 격리**: 데이터 제품은 제어된 단계(dev → staging → prod)를 통해 개발, 검증, 승격됩니다.
- **정책 세분성**: 접근 제어, 암호화, 보존 정책을 Catalog 수준에서 적용할 수 있습니다.

이 구조를 통해 팀은 데이터 제품의 전체 수명주기를 관리하면서 환경을 격리된 상태로 유지할 수 있습니다. 개발자는 변경사항을 테스트하고, 동료 검토를 수행하며, 변경이 프로덕션에 영향을 미치기 전에 점진적으로 자산을 승격할 수 있습니다.

엄격한 보안이나 컴플라이언스 요구사항이 있는 조직의 경우, 환경 격리는 종종 논리적 경계를 넘어 확장됩니다. 이 경우 각 환경은 별도의 스토리지 컨테이너, 서비스 주체, 외부 위치로 지원될 수 있어 Catalog 수준에서 물리적 데이터 격리를 제공합니다.

Unity Catalog를 비즈니스 및 환경 세분화를 반영하도록 정렬함으로써, 조직은 거버넌스의 일관성을 달성하고, 승인 및 배포 워크플로우를 간소화하며, 데이터 이니셔티브를 확장할 수 있습니다.

추가 지침은 [Unity Catalog best practices](https://docs.databricks.com/aws/en/data-governance/unity-catalog/best-practices.html) (AWS | Azure | GCP)를 참조하세요.

![Unity Catalog 하의 샘플 BU에 대한 Catalog 설계](https://www.databricks.com/sites/default/files/inline-images/enterprise-scale-governance-image-2.png)

### 거버넌스 모델: 중앙 집중형 vs. 분산형 소유권

Catalog 설계가 데이터 도메인과 환경을 위한 구조적 경계를 정의하는 반면, 거버넌스 모델은 그 경계 안에서 누가 결정 권한을 갖는지를 확립합니다. 중앙 집중형과 분산형(또는 연합형) 거버넌스 간의 선택은 큰 영향을 미칩니다.

간단히 말하면, Catalog는 데이터 소유권이 어디에 위치하는지를 정의하고, 거버넌스 모델은 그 소유권을 어떻게, 누가 관리하는지를 정의합니다.

![분산형 vs. 중앙 집중형 퍼블리싱](https://www.databricks.com/sites/default/files/inline-images/enterprise-scale-governance-image-3.png)

#### 중앙 집중형 모델

중앙 집중형 거버넌스 모델에서는 전담 플랫폼 또는 데이터 거버넌스 팀이 Unity Catalog Metastore를 관리하고 카탈로그를 통해 접근 경계를 적용합니다. 이 팀은 카탈로그를 BU별 또는 도메인별 컨테이너로 정의하고, 각 팀에게 자신의 영역 내에서 데이터를 게시하고 접근 권한을 요청하는 방법을 안내합니다.

이 중앙 팀은 또한 공유 데이터셋을 큐레이션하고 모든 도메인에 걸쳐 컴플라이언스, 품질, 메타데이터 표준을 유지하여 조직 전체에 걸쳐 일관된 정책을 보장합니다. 이 모델은 컴플라이언스 요구사항이 엄격하고 감사 추적이 필수적인 환경에서 특히 규제 산업에 적합합니다.

예를 들어, 중앙 집중형 거버넌스 모델을 채택한 일부 글로벌 제조 조직들은 지역 간 소통을 간소화하고, 일관된 품질 표준을 적용하며, 운영 효율성을 최적화할 수 있습니다.

#### 분산형 모델

반대로, 분산형(또는 연합형) 거버넌스 모델은 개별 BU들이 카탈로그와 데이터 제품을 end-to-end로 소유할 수 있도록 권한을 부여함으로써 제어권을 분산시킵니다. 중앙 플랫폼 팀이 전반적인 표준을 관리할 수 있지만, 각 도메인 팀은 자체 데이터의 게시, 버전 관리, 접근 승인에 대한 책임을 집니다.

분산형 방식은 소유권이 분산되어 있기 때문에 데이터 자산이 커질수록 잘 확장됩니다. 각 팀은 데이터의 품질, 리니지, 문서화에 직접 책임을 지므로 더 강한 책임감을 조성하고 도메인별 데이터 활용에 대한 더 깊은 전문성을 키웁니다.

이 모델은 현지화된 컴플라이언스를 필요로 하는 다양한 사업 포트폴리오를 가진 조직이나 서로 다른 규제 요구사항이 있는 여러 지역에 걸쳐 운영하는 조직에 적합한 경우가 많습니다.

#### 어떤 모델을 선택해야 하나?

대부분의 조직은 Unity Catalog를 사용하여 중앙 집중형 거버넌스 모델로 시작하는 것이 실용적이라고 생각합니다. 이는 일관된 정책, 단순화된 컴플라이언스, 모든 데이터 자산에 걸친 통합된 감독을 제공하기 때문입니다.

최종적으로 선택은 조직 구조, 규제 요구사항, 데이터 성숙도, 협업 필요성 등의 요소에 달려 있습니다. 아래는 각 방식의 강점과 트레이드오프를 요약한 것입니다. 이 비교를 통해 조직의 현재 상황과 미래 방향성에 맞는 모델을 선택하는 데 도움을 받을 수 있습니다.

| 측면 | 중앙 집중형 거버넌스 | 분산형 거버넌스 |
|---|---|---|
| 통제 및 컴플라이언스 | 강력한 중앙 집중 통제로 감사 및 규제 컴플라이언스가 간단합니다. | 명확한 가드레일이 필요하지만 유연성을 제공합니다. 중앙 팀이 가드레일을 관리하고 데이터 접근은 관리하지 않습니다. |
| 속도 및 민첩성 | 승인 병목과 중앙화된 워크플로우로 인해 느립니다. | BU가 데이터 수명주기와 접근 관리를 소유하므로 더 빠른 혁신이 가능합니다. |
| 소유권 및 책임 | 중앙 팀이 데이터 품질과 메타데이터 일관성에 책임을 집니다. | 도메인 팀이 데이터 품질, 문서화, 게시를 소유하여 책임감을 증진합니다. |
| 복잡성 및 규모 | 초기에 관리하기 쉽지만 규모가 커지면 병목이 생길 수 있습니다. | 성장하는 데이터 자산과 함께 잘 확장되지만 성숙한 정책과 모니터링이 필요합니다. |
| 협업 | 협업은 중앙에서 관리하는 워크스페이스-카탈로그 바인딩을 통해 제어됩니다. | 공유 정책을 통해 협업이 활성화됩니다. 팀은 카탈로그 경계 내에서 자율적으로 운영됩니다. |
| 이상적인 대상 | 권위 있는 거버넌스 결정을 내릴 핵심 그룹이 있는 조직. | 자체 프로세스를 따르는 자율적인 도메인 팀을 보유한 조직. |

어떤 방식을 선택하든, 효과적인 거버넌스를 위해서는 Catalog에 대한 소유권의 명확한 매핑, 강력한 접근 제어, 투명한 협업 메커니즘이 필요합니다. 이를 통해 보안과 혁신이 조화를 이룰 수 있습니다.

---

## 기술적 솔루션 분석

거버넌스와 아키텍처의 개념적 기반이 확립되면, 다음은 실제 데이터 자산을 UC로 마이그레이션하는 데 관련된 실질적인 엔지니어링 작업으로 초점이 옮겨집니다. 상위 수준의 원칙들은 간단해 보일 수 있지만, 실제 HMS 환경은 수백 개의 워크스페이스, 수천 개의 테이블, 레거시 워크로드와의 복잡한 의존성을 포함하는 경우가 많습니다.

이러한 복잡성을 해결하기 위해, 다음 섹션에서는 현대 데이터 조직을 위한 세 가지 핵심 기술적 고려사항을 깊이 살펴봅니다: 현재 자산을 파악하기 위한 마이그레이션 전 데이터 탐색, 일관된 Unity Catalog 설정을 위한 IaC 기반 자동화 배포, 그리고 위험을 최소화하는 단계적 마이그레이션 전략입니다.

### 1. 마이그레이션 전 데이터 탐색

Hive 테이블을 마이그레이션하고 워크로드를 업데이트하기 전에, 팀은 기존 데이터 환경을 파악해야 합니다. 이 탐색 단계는 마이그레이션 범위를 정의하고, 위험 영역을 파악하며, 과도한 마이그레이션 또는 미완성 마이그레이션을 방지하는 데 도움을 줍니다.

이 과정에는 HMS의 활성 테이블, 뷰, 잡(job), 권한, 팀을 매핑하여 Unity Catalog로 변환해야 할 것을 결정하는 작업이 포함됩니다. 여러 워크스페이스와 방대한 데이터 볼륨을 가진 대규모 조직의 경우, 이 발견 작업은 수동으로 수행하기가 어렵습니다.

#### UCX를 활용한 데이터 탐색

이 문제를 해결하기 위해 Databricks Labs는 [UCX](https://docs.databricks.com/aws/en/data-governance/unity-catalog/ucx.html) (AWS | Azure | GCP)를 개발했습니다. UCX는 데이터 탐색, 준비 평가, 마이그레이션 계획을 자동화하는 오픈소스 툴입니다. 배포되면, UCX는 레거시 HMS 구성, 테이블, 잡, 노트북을 스캔하여 Unity Catalog 이전(pre-migration) 평가를 위한 상세하고 실행 가능한 리포트를 생성합니다.

UCX 출력을 검토할 때, 조직은 원시 수치와 준비 점수 외에도 다음과 같은 정보에 주목하여 정보에 기반한 결정을 내려야 합니다:

- 오래되었거나 중복된 테이블을 식별하고 제외함으로써 마이그레이션 범위 줄이기
- 최종 접근 시간이나 최종 업데이트 시간 같은 활동 신호를 확인하여 중요한 워크로드와 미사용 데이터 구분
- 마이그레이션 전에 겹치는 스키마를 통합하거나 명명을 표준화하여 자산 합리화
- 하위 파이프라인, BI 대시보드, 규제 요구사항이 먼저 이동해야 할 것을 결정하는 의존성 우선순위화

이 자동화된 탐색 프로세스를 통해 조직은 다음과 같은 가치를 얻습니다:

- BU, 팀, 그들의 데이터 제품의 완전한 범위 파악
- 사용자, 그룹, 자산 간의 접근 제어 및 의존성 매핑
- 활발히 사용되는 테이블/뷰와 아카이빙 후보 식별
- 다른 워크로드를 단계적으로 퇴역시키면서 중요한 레거시 워크플로우 우선순위화

수십 개에서 수백 개의 Databricks 워크스페이스를 관리하는 조직의 경우, UCX는 탐색을 자동화하고 마이그레이션 범위를 명확히 함으로써 엔지니어링 노력을 줄여줍니다. 인적 오류를 최소화하고, 불확실성을 없애고, 모든 구성 요소가 고려되었다는 확신을 줍니다.

UCX 소개는 [Use the UCX utilities to upgrade your workspace to Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/ucx.html) (AWS | Azure | GCP)를 참조하세요.

### 2. Infrastructure as Code(IaC)를 통한 자동화 배포

데이터 탐색이 기존 자산, 의존성, 접근 패턴에 대한 종합적인 그림을 제공하면, 다음 과제는 이를 지원하는 Unity Catalog 환경을 프로비저닝하는 것입니다. 수동 구성은 워크스페이스가 늘어날수록 오류가 발생하기 쉽고, 감사하기 어려우며, 유지 관리하기 힘듭니다. Infrastructure as Code(IaC), 특히 Databricks Terraform 프로바이더를 사용하는 방식은 이러한 문제를 해결합니다.

Terraform을 사용하면 팀은 지원되는 모든 클라우드 플랫폼에서 Unity Catalog 리소스 생성 및 구성을 자동화하여 마이그레이션 프로세스를 재현 가능하고 감사 가능하게 만들 수 있습니다. 예를 들어, 수동 구성 오류나 불일치를 방지하기 위해 [Databricks Terraform 프로바이더](https://registry.terraform.io/providers/databricks/databricks/latest/docs) 사용이 강력히 권장됩니다.

커스텀 Terraform 모듈 배포에 대한 완전한 가이드는 [Automate Unity Catalog setup using Terraform](https://docs.databricks.com/aws/en/dev-tools/terraform/unity-catalog.html) (AWS | Azure | GCP)을 참조하세요.

Unity Catalog 마이그레이션에서, 이 방식은 팀이 다음을 수행할 수 있도록 필요한 인프라를 구축하는 데 특히 강력함이 입증되었습니다:

- 거버넌스 표준이 환경 전반에 걸쳐 일관되게 적용되도록 보장
- 마이그레이션 중 잘못된 구성 위험 최소화
- 미래 확장을 위한 거버넌스 인프라의 지속적 제공 가능

![Terraform 인프라 워크플로우](https://www.databricks.com/sites/default/files/inline-images/enterprise-scale-governance-image-4_0.png)

### 3. 마이그레이션 전략

HMS 자산의 완전한 목록과 IaC를 통해 프로비저닝된 Unity Catalog 워크스페이스가 갖춰지면, 초점은 설정에서 제어되고 위험이 낮은 워크로드 마이그레이션으로 이동합니다. 조직은 파일럿 기반 단계적 도입, 대규모 실행을 위한 구조적 전략, 두 가지의 조합 중 하나를 선택할 수 있습니다.

대부분의 조직이 단계적 도입 방식으로 시작하는 것이 좋지만, 초기 파일럿을 넘어 확장하려면 신중한 계획과 구조적 실행이 필요합니다. 대규모 Unity Catalog 마이그레이션을 계획하고 실행하는 조직은 Databricks Delivery Solutions Architects(DSA)와 협력하는 것을 강력히 권장합니다.

#### 파일럿 방식의 단계적 도입

대부분의 프로덕션 환경에서 "빅뱅(big-bang)" 마이그레이션은 거의 실용적이지 않습니다. 대신, Databricks는 파일럿 마이그레이션으로 시작할 것을 권장합니다. 즉, 일반적인 사용 패턴을 반영하는 대표적인 BU 또는 팀의 워크로드를 먼저 마이그레이션합니다. 이를 통해 실제 플랫폼에서 전체 마이그레이션 접근 방식을 검증하고, 광범위한 배포 전에 워크플로우를 세밀하게 조정하고, 초기 성공 사례와 이해관계자 지지를 구축할 수 있습니다.

거기서부터 조직은 단계적으로 전체 채택으로 확장할 수 있으며, 플랫폼 안정성을 유지하고, 이해관계자의 신뢰를 구축하며, 예측 가능한 진행을 가능하게 합니다. 이는 일괄 전환(cutover) 방식으로는 달성하기 어려운 이점들입니다.

Databricks는 워크로드를 HMS에서 Unity Catalog로 이동하기 위한 두 가지 단계적 접근 방식을 권장합니다.

**옵션 A: 파이프라인별 마이그레이션**

이 방식은 관련된 테이블, 잡, 대시보드, 의존성을 포함한 하나의 파이프라인을 다음으로 진행하기 전에 Unity Catalog로 마이그레이션합니다. 각 마이그레이션 단위를 자체 포함 워크스트림(workstream)으로 캡슐화함으로써, 팀은 범위가 명확하게 정의된 파이프라인 수준에서 리소스를 집중하고 진행 상황을 추적하며 문제를 격리할 수 있습니다. 이 접근 방식은 파이프라인 의존성이 잘 문서화되어 있고 BU들이 독립적으로 운영되는 조직에 가장 적합합니다.

**옵션 B: 레이어별 마이그레이션 (Gold → Silver → Bronze)**

메달리온(medallion) 아키텍처에 기반한 레이어별 전략은 고유한 레이어를 통해 Unity Catalog 마이그레이션을 진행하도록 권장합니다. Gold(사용자 대면 분석 출력물), Silver(정제 및 비즈니스 규칙이 적용된 데이터), Bronze(원시 인제스트된 데이터) 순으로 진행합니다.

옵션 B의 마이그레이션 순서:

1. **Gold 레이어 먼저**: Gold 테이블을 Unity Catalog로 먼저 마이그레이션한 다음, 중요한 대시보드, BI 도구, 임시 쿼리가 Unity Catalog의 대체 테이블을 가리키도록 재정렬합니다. 이러한 자산들은 자주 액세스되고 조직적 가치가 높은 경향이 있으므로, 비즈니스 이해관계자들에게 Unity Catalog의 즉각적인 가시성을 제공합니다.
2. **Silver 레이어 다음**: Gold 소비자가 Unity Catalog에서 검증되면, 이를 공급하는 변환 잡과 테이블(일반적으로 Silver 레이어)을 업데이트합니다. 이 단계는 더 광범위한 데이터 정제 및 집계 로직을 포함합니다.
3. **Bronze 레이어 마지막**: 외부 인제스트 잡과 원시 랜딩 테이블을 Unity Catalog로 마이그레이션하여 사이클을 완성합니다. 업스트림 인제스트이 통합되면, 전체 데이터 스택의 리니지가 Unity Catalog로 통합됩니다.

Databricks는 위의 마이그레이션 전략들을 훈련된 운영 관행으로 보완할 것을 권장합니다. 예를 들어, 레거시 HMS 테이블에 해당 Unity Catalog 대응 테이블을 참조하는 주석을 달면 사용자와 파이프라인이 잘못된 소스로 연결되는 것을 방지하는 데 도움이 됩니다. 전환 중에는 향상된 모니터링을 활성화하고, 결과를 HMS 기준선과 교차 검증하며, 성능 지표를 추적하는 것이 중요합니다.

다음 섹션에서는 단계적 방식을 보완하는 두 가지 일반적인 마이그레이션 경로(Soft vs. Hard)를 비교합니다.

---

## 마이그레이션 경로: "Soft" vs. "Hard"

정의된 프레임워크 내에서 두 가지 뚜렷한 마이그레이션 패턴이 있습니다. HMS Federation을 통한 Soft Migration은 레거시 HMS를 그대로 유지하면서 연합된 HMS에 대해 Unity Catalog의 고급 거버넌스 기능에 접근할 수 있게 하는 것이고, Hard Migration은 HMS를 완전히 퇴역시키는 것입니다.

![HMS Federation을 사용한 단계적 마이그레이션](https://www.databricks.com/sites/default/files/inline-images/enterprise-scale-governance-image-5.png)

### HMS Federation을 통한 Soft Migration

Soft Migration은 레거시 HMS를 그대로 유지하면서 팀이 Unity Catalog 거버넌스 기능을 채택할 수 있게 해주는 "마이그레이션 브리지" 역할을 하는 하이브리드 방식입니다. Hive Metastore Federation은 Unity Catalog 카탈로그 내의 연합 카탈로그(federated catalog)를 통해 HMS 테이블에 대한 통합 접근을 가능하게 합니다.

연합된 데이터를 Unity Catalog에서 관리하고 상호작용하는 방법은 HMS가 내부인지 외부인지에 따라 다릅니다. Federation 커넥터는 내부 HMS 인스턴스의 테이블에 대한 읽기 및 쓰기 접근을 지원하는 반면, 외부 HMS 테이블은 읽기 전용으로 연합됩니다.

HMS Federation을 통한 Soft Migration이 Unity Catalog 채택을 위한 낮은 중단 경로를 제공하지만, HMS를 완전히 퇴역시키려는 조직은 결국 연합된 자산의 Hard Migration을 수행해야 합니다. 비록 처음에는 코드 변경이 최소화되지만, Federation은 HMS 의존성을 유지하며 완전한 Unity Catalog 기능을 즉시 잠금 해제하지는 않습니다.

또한, UCX는 테이블 마이그레이션 프로세스의 대안으로 HMS Federation을 활성화하는 CLI 툴을 제공합니다.

레거시 워크스페이스 HMS, 외부 HMS 또는 AWS Glue Metastore를 위한 HMS Federation 설정 방법은 [How do you use Hive metastore federation during migration to Unity Catalog?](https://docs.databricks.com/aws/en/data-governance/unity-catalog/hms-federation.html) (AWS | Azure | GCP)를 참조하세요.

### Hard Migration

Hard Migration은 HMS에서 Unity Catalog로의 포괄적인 업그레이드로, 테이블의 메타데이터(및 관리형 테이블의 경우 데이터)를 새로운 Metastore로 변환합니다. 이 방식은 SYNC(또는 UCX)와 같은 툴, Upgrade Wizard, CREATE TABLE CLONE, 그리고 외부 테이블의 경우 CTAS 등을 결합하여 HMS에서 Unity Catalog로 완전한 데이터 전송을 수행하지만, 더 광범위한 계획 및 팀 간 조율이 필요합니다.

HMS에 마이그레이션이 필요한 대량의 데이터가 있는 조직의 경우, Databricks는 대부분의 테이블에 대해 아래에 나열된 수동 방법보다 UCX의 자동화된 테이블 마이그레이션 워크플로우를 권장합니다.

**외부 테이블 업그레이드**

외부 테이블은 SYNC 명령 또는 Upgrade Wizard를 사용하여 업그레이드할 수 있습니다. 이들은 메타데이터 전용 작업으로, 데이터를 복사하거나 이동하지 않습니다.

- **SYNC**: HMS에서 Unity Catalog로 테이블 메타데이터를 전송하고 HMS 테이블에 북키핑(bookkeeping) 속성을 추가하는 SQL 명령입니다. 테이블 또는 스키마 수준에서 적용할 수 있어 SQL 우선 팀에 유연성을 제공합니다.
- **Upgrade Wizard**: 시각적 워크플로우로 SYNC 기능을 감싼 Catalog Explorer 인터페이스입니다. 포인트 앤 클릭 방식의 단순함이 채택을 가속화하는 대량 스키마 마이그레이션에 이상적입니다.

HMS와 Unity Catalog 테이블이 동일한 클라우드 스토리지를 참조하기 때문에, 전환 중에 하이브리드 설정이 실행될 수 있습니다. 예약된 SYNC는 마이그레이션이 완료될 때까지 두 시스템 간의 메타데이터 동기화를 유지합니다.

**관리형 테이블 업그레이드**

관리형(managed) 테이블은 관리 스토리지 위치에 있기 때문에 데이터 이동이 필요합니다([What is a managed storage location?](https://docs.databricks.com/aws/en/data-governance/unity-catalog/managed-storage.html) [AWS | Azure | GCP] 참조). 따라서 CREATE TABLE CLONE 또는 CTAS를 사용하여 업그레이드해야 합니다.

- **CREATE TABLE CLONE(Deep Clone)**: 이 방법은 데이터와 메타데이터를 스토리지 레이어에 직접 복사합니다. 파티셔닝, 형식, 불변성, null 허용 여부 및 기타 메타데이터를 자동으로 보존합니다. 또한 관리형 테이블의 데이터를 Databricks 관리 스토리지에서 동일하거나 다른 Unity Catalog Metastore로 전송하는 데도 사용할 수 있습니다.
- **CREATE TABLE AS SELECT(CTAS)**: 관리형 Hive 테이블이 클로닝 요구사항을 충족하지 않을 때(예: Delta 형식이 아닐 때) 유용합니다. CTAS는 쿼리 결과에서 테이블을 재구성하여 선택적 마이그레이션이나 변환을 가능하게 합니다.

관리형 테이블 마이그레이션에는 CLONE이 강력히 권장되며, CTAS는 소스 테이블에 조정이 필요할 때 유연성을 제공합니다.

**뷰 업그레이드**

뷰는 참조된 모든 테이블이 마이그레이션된 후 수동으로 재생성해야 합니다. 세 단계 네임스페이스(catalog.schema.table)에 따라 테이블의 Unity Catalog 버전을 참조하는 CREATE VIEW 구문을 사용하세요.

테이블과 뷰 마이그레이션을 위한 다양한 옵션에 대한 자세한 내용은 [Upgrade Hive tables and views to Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/migrate.html) (AWS | Azure | GCP)를 참조하세요.

**HMS 접근 비활성화**

모든 HMS 자산이 Unity Catalog로 마이그레이션되거나 HMS가 Unity Catalog 하의 연합 카탈로그(federated catalog)로 Federation된 후에는, 통합된 거버넌스를 시행하고 잠재적 우회 경로를 차단하기 위해 레거시 HMS에 대한 직접 접근을 비활성화하는 것이 필수적입니다.

Databricks는 균일한 거버넌스를 시행하고 잠재적인 우회 경로를 차단하기 위해 모든 클러스터와 워크로드에서 직접 HMS 접근을 한 번에 비활성화할 것을 권장합니다. 단계적 롤아웃을 선호하는 조직의 경우, 클러스터 정책을 통해 특정 클러스터 유형이나 팀에 대해 접근을 선택적으로 비활성화할 수 있습니다.

레거시 Metastore를 비활성화할 때의 영향을 이해하려면 [What happens when you disable the legacy metastore?](https://docs.databricks.com/aws/en/data-governance/unity-catalog/disable-hms.html) (AWS | Azure | GCP)를 참조하세요.

---

## 실제 사례

Databricks를 사용하는 한 글로벌 유통업체는 수천 개의 테이블과 노트북을 관리하는 대규모 환경을 운영하며 데이터 거버넌스와 크로스 팀 협업에서 상당한 어려움을 겪었습니다. 데이터는 워크스페이스 전반에 걸쳐 사일로화되어 있었고, 권한 관리는 중앙화되지 않았으며, 팀들은 중복된 데이터 제품과 불일치하는 메타데이터로 인한 문제로 어려움을 겪었습니다.

이 블로그에 설명된 기본 원칙에 따라, 조직은 대상 아키텍처를 정의하는 것으로 시작했습니다. 이는 비즈니스 도메인이 자체 데이터와 접근 정책을 소유하고 관리하면서 중앙화된 거버넌스 시행을 유지하는 분산형 Data Mesh 구조였습니다. UCX를 사용하여 기존 워크로드와 자산을 탐색하고, Terraform으로 Unity Catalog Metastore를 자동화하며, 파일럿을 통해 가장 중요한 데이터 파이프라인의 마이그레이션을 검증했습니다.

마이그레이션 이후, 조직은 Unity Catalog를 통한 중앙화된 거버넌스를 확립하면서 비즈니스 도메인이 데이터와 접근 정책을 자율적으로 관리할 수 있는 분산형 아키텍처를 유지했습니다. 결과적으로 데이터 탐색 용이성이 크게 향상되었고, 컴플라이언스 가시성이 개선되었으며, 팀들은 더 빠르게 데이터 제품을 구축하고 게시할 수 있게 되었습니다.

---

## 핵심 요약

- **확장 가능한 거버넌스의 필수성**: 데이터 중심 조직이 성장함에 따라, HMS와 같은 레거시 Metastore는 현대적인 거버넌스 요구를 지원하기 어렵습니다. Unity Catalog는 세분화된 접근 제어, 엔드투엔드 리니지, 모든 데이터 및 AI 자산에 걸친 통합 감사를 통해 통합된 거버넌스를 제공합니다.
- **모듈식 거버넌스 아키텍처**: Unity Catalog는 중앙 집중형과 분산형(연합형) 거버넌스를 모두 지원합니다. 중앙 집중형 모델은 규제 산업에서 컴플라이언스와 감사를 간소화하는 반면, 분산형 모델은 도메인 팀의 자율성을 높이고 확장성을 향상시킵니다.
- **Metastore와 Catalog 설계의 중요성**: 신중한 Metastore와 Catalog 설계는 확장 가능한 거버넌스의 토대를 형성합니다. Catalog 기반 격리를 갖춘 단일 Metastore 전략(일관된 명명 규칙 및 스토리지 경계와 결합)은 권한을 단순화하고, 자율성을 증진하며, 안전한 협업을 가능하게 합니다.
- **자동화되고 위험을 인식하는 마이그레이션**: 마이그레이션 전 탐색과 Infrastructure as Code(IaC)를 결합하면 일관된 Unity Catalog 설정을 보장하고, 수동 오류를 줄이며, 배포를 가속화합니다. 대표적인 파일럿으로 시작하는 단계적 도입은 확신과 이해관계자의 지지를 구축하면서 중단을 최소화합니다.
- **유연한 마이그레이션 경로**: HMS Federation을 통한 Soft Migration은 즉각적인 코드 변경 없이 단계적으로 Unity Catalog 거버넌스를 채택할 수 있게 해주는 반면, Hard Migration은 Unity Catalog의 모든 기능을 제공하고 HMS의 완전한 퇴역을 가능하게 합니다.

---

## 결론

Hive Metastore에서 Unity Catalog로의 마이그레이션은 통합되고 확장 가능한 거버넌스와 최적화된 데이터 운영을 통해 진정한 데이터 인텔리전스를 실현하려는 기업에게 필요한 기초적 단계입니다. 성공적인 마이그레이션은 단순히 데이터를 이동시키는 것이 아니라, 데이터 자산이 어떻게 소유되고, 접근되고, 거버닝되는지를 재설계하는 것입니다.

이 블로그에 설명된 전략들을 채택함으로써 조직들은 거버넌스 격차를 줄이고, 셀프서비스 데이터 접근을 활성화하며, 확장 가능한 데이터 운영의 기반을 마련할 수 있습니다. Databricks의 도구들과 권장되는 아키텍처 패턴들은 조직들이 이러한 전환을 자신감 있게, 그리고 확신을 갖고 탐색할 수 있도록 설계되었습니다.

---

## 다음 단계 및 리소스

Unity Catalog 마이그레이션을 효과적으로 시작하려면, 위에 설명된 전략들을 적용하고 상세하고 최신화된 가이던스를 위해 공식 Databricks 문서를 참조하세요.

### Unity Catalog 마이그레이션 트래커

이 트래커는 Unity Catalog 마이그레이션을 관리하기 위한 구조화된 템플릿을 제공하며, 문서 및 툴링에 대한 내장 링크와 마일스톤 달성 시 추적하기 위한 상태 필드를 포함합니다.

마이그레이션 트래커: [Github](https://github.com/databricks/unity-catalog-migration-toolkit)

### Unity Catalog 시작하기

Unity Catalog에 대한 기초 전문성을 쌓으려면, 다음 인터랙티브 자기 주도 학습 Databricks Academy 강좌를 활용하세요(Databricks 계정 또는 이메일로 로그인 필요):

- Introduction to Unity Catalog
- Data Administration in Databricks
- Data Access Control in Unity Catalog
- Compute Resources & Unity Catalog
- Unity Catalog Patterns & Best Practices

### 실제 시나리오에서 배우기

2025 Data + AI Summit에서 소개된 고객 성공 사례 및 심화 기술 세션을 통해 실질적인 인사이트를 얻으세요:

**Databricks 주도 세션:**
- Unity Catalog Deep Dive: Practitioner's Guide to Best Practices and Patterns - Data + AI Summit 2025 | Databricks
- Unity Catalog Upgrades Made Easy. Step-by-Step Guide for Databricks Labs UCX - Data + AI Summit 2025
- Demystifying Upgrading to Unity Catalog — Challenges, Design and Execution - Data + AI Summit 2025 | Databricks (Celebal Technologies와 함께)

**고객 사례:**
- Schiphol Group's Transformation to Unity Catalog - Data + AI Summit 2025 | Databricks (Schiphol Group과 Databricks)
- Story of a Unity Catalog (UC) Migration: Using UCX at 7-Eleven to Reorient a Complex UC Migration - Data + AI Summit 2025 | Databricks (7-Eleven과 Databricks)
- Unlocking Enterprise Potential: Key Insights from P&G's Deployment of Unity Catalog at Scale - Data + AI Summit 2025 | Databricks (P&G)

### DSA: 전문 마이그레이션 가이던스

Databricks Delivery Solutions Architects(DSA)는 조직이 Unity Catalog 마이그레이션을 진행하는 데 중추적인 역할을 합니다. 전략적 어드바이저로서 DSA는 실행 계획 설계를 지원하고, 기술적 위험을 탐색하며, 비즈니스 성과에 맞게 마이그레이션을 조율합니다.
