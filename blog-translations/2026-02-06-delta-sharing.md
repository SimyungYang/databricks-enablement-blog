---
original_title: "New Delta Sharing Features, Data Collaboration Ecosystem Growth, Databricks Clean Rooms in Public Preview, Marketplace Momentum"
authors: "Zaheera Valani, Tianyi Huang, Darshana Sivakumar, Giselle Goicochea, Harish Gaur"
date: "2024-06-13"
category: "Data Sharing & Collaboration"
original_url: "https://www.databricks.com/blog/whats-new-data-sharing-and-collaboration"
translated_date: "2026-02-06"
note: "원문 URL(delta-sharing-data-collaboration)은 404로 확인되지 않아, 동일 주제의 가장 근접한 공식 블로그 포스트로 대체하였습니다."
---

# 새로운 Delta Sharing 기능, 데이터 협업 생태계 성장, Databricks Clean Rooms Public Preview, Marketplace 모멘텀

> **원문**: [New Delta Sharing Features, Data Collaboration Ecosystem Growth, Databricks Clean Rooms in Public Preview, Marketplace Momentum](https://www.databricks.com/blog/whats-new-data-sharing-and-collaboration)

_Data + AI Summit 2024에서 발표된 Delta Sharing 신규 기능, 생태계 성장 지표, Clean Rooms Public Preview, Databricks Marketplace 확장을 소개합니다_

**게시일:** 2024년 6월 13일 | **카테고리:** Data Sharing & Collaboration

**저자:** Zaheera Valani, Tianyi Huang, Darshana Sivakumar, Giselle Goicochea, Harish Gaur

---

Databricks 고객들은 벤더 종속(vendor lock-in) 없이 유연하고 안전하며 개방된 생태계에서 파트너 및 고객과 크로스 플랫폼, 크로스 클라우드 협업을 이끌어가고 있습니다. Delta Sharing 오픈 프로토콜은 고객들이 데이터와 AI 자산을 손쉽고 안전하게 공유하여 혁신을 가속할 수 있도록 지원합니다. Databricks Marketplace는 데이터, 분석, AI에 관한 모든 니즈를 충족시키는 개방형 마켓플레이스로, 파트너들이 다양한 데이터 및 AI 자산을 공유하고 데이터 소비자들이 혁신을 실현할 수 있게 합니다.

Data + AI Summit 2024에서 Databricks는 Delta Sharing, Clean Rooms, Databricks Marketplace에 걸친 여러 중요한 업데이트를 발표했습니다. 이번 글에서는 데이터 협업 생태계의 놀라운 성장 지표와 함께, 이러한 기능들이 어떻게 고객들에게 더욱 강력하고 안전하며 유연한 협업 환경을 제공하는지 살펴보겠습니다.

## Databricks 데이터 협업 생태계의 놀라운 성장

Databricks는 혁신과 협업에 대한 지속적인 투자가 지난 한 해 동안 생태계 전반에 걸쳐 인상적인 성과를 거뒀음을 확인할 수 있었습니다.

- 16,000명 이상의 데이터 수신자(data recipient)가 클라우드, 플랫폼, 리전을 가로질러 데이터와 AI 자산을 주고받기 위해 Delta Sharing을 채택했습니다.
- 데이터 제공자(data provider)와 수신자 간의 활성 Delta Share 수가 전년 대비 **300% 이상 성장** 했습니다.
- Databricks Marketplace에서 2,000개 이상의 데이터셋, AI 모델, 솔루션 액셀러레이터 리스팅이 제공되고 있습니다.
- Databricks Marketplace의 리스팅 수가 전년 대비 **320% 증가** 했습니다.
- Delta Sharing 연결의 40%가 오픈 커넥터를 통해 Apache Spark, Excel, pandas, PowerBI, Tableau 등 비(非)Databricks 플랫폼과 이루어지고 있습니다.

이러한 수치는 Databricks의 개방형 데이터 협업 비전이 시장에서 강력하게 받아들여지고 있음을 보여줍니다. 경쟁사들의 폐쇄적인 공유 방식과 달리, Databricks의 개방형 플랫폼은 조직들이 리전, 클라우드, 플랫폼에 걸쳐 데이터와 AI 자산을 손쉽고 안전하게 공유할 수 있도록 합니다.

## 새로운 Delta Sharing 기능

Delta Sharing은 클라우드, 플랫폼, 리전을 가로질러 어떤 수신자에게든 라이브 데이터를 공유하기 위한 개방적이고 유연하며 안전한 접근 방식입니다. Data + AI Summit 2024에서 Databricks는 여러 혁신적인 Delta Sharing 신규 기능을 발표했습니다.

### Cross-Platform View Sharing (크로스 플랫폼 뷰 공유)

Databricks는 **Cross-Platform View Sharing** 의 Public Preview 출시를 발표했습니다. 이를 통해 데이터 제공자는 서로 다른 환경에서도 뷰(view)를 원활하게 공유할 수 있습니다. 데이터 소비자는 모든 유형의 Databricks 클러스터를 활용하거나 오픈 Delta Sharing 클라이언트를 사용하여 공유된 뷰에 접근하고 쿼리할 수 있습니다. 이는 게임 체인저입니다. 데이터 제공자의 도달 범위를 확대하고, 데이터 소비자에게는 벤더 종속의 부담 없이 더 쉽고 빠른 협업 환경을 제공하기 때문입니다.

### Secure Open Sharing with OpenID Connect (OIDC를 활용한 안전한 오픈 공유)

**OIDC Token Federation** 을 활용한 안전한 오픈 공유가 게이티드 Public Preview(gated public preview)로 제공됩니다. 이를 통해 오픈 수신자(open recipient)는 OpenID Connect 또는 OAuth 토큰을 사용하여 자신이 선호하는 Identity Provider를 통해 인증할 수 있습니다. 비(非)Databricks 수신자와 공유할 때 민감한 정보를 직접 교환할 필요가 없어지므로, 노출 리스크가 줄어들고 보안이 강화됩니다.

### History Sharing (히스토리 공유)

**History Sharing** 은 테이블 읽기 성능을 향상시키기 위해 도입된 기능입니다. 데이터 제공자가 수신자와 테이블 히스토리를 공유할 수 있게 하여, 수신자 측에서 더 효율적인 증분 읽기(incremental read)가 가능해집니다. 이는 대규모 데이터셋을 반복적으로 동기화해야 하는 시나리오에서 특히 큰 성능 개선 효과를 발휘합니다.

### Serverless Egress Controls (서버리스 이그레스 제어)

새롭게 도입된 **Serverless Egress Controls** 는 데이터 제공자가 서버리스 환경에서도 데이터 이그레스(egress)를 세밀하게 통제할 수 있게 합니다. 이를 통해 불필요한 데이터 전송 비용을 줄이고 보안 정책을 일관되게 적용할 수 있습니다.

### Lakehouse Federation Sharing (레이크하우스 페더레이션 공유)

**Lakehouse Federation Sharing** 은 현재 Private Preview로 제공되며 곧 더 넓게 출시될 예정입니다. 이 기능을 통해 데이터 제공자는 Snowflake, BigQuery, Redshift, MySQL, PostgreSQL 등 자신의 데이터 웨어하우스나 데이터베이스에 저장된 데이터에 대한 접근 권한을 손쉽게 부여할 수 있습니다. Databricks 고객은 제공자 측에 추가적인 오버헤드 없이 가장 넓은 범위의 데이터셋에 접근할 수 있게 됩니다. 이는 조직들이 기존 데이터 인프라를 그대로 유지하면서도 개방된 협업을 실현할 수 있음을 의미합니다.

### Materialized Views 및 Streaming Tables 공유

Private Preview로 **Materialized Views 및 Streaming Tables 공유** 가 제공됩니다. 이를 통해 고객은 추가 복사본이나 파이프라인을 유지할 필요 없이 Delta Live Tables 파이프라인 출력 결과를 손쉽게 공유할 수 있습니다.

### Cloudflare R2 지원

Delta Sharing이 이제 **Cloudflare R2** 를 지원합니다. Cloudflare R2와의 전략적 파트너십을 통해 고객은 제로 이그레스 피(zero egress fee) 혜택으로 상당한 비용 절감을 실현할 수 있습니다. Volume Sharing과 Cloudflare R2 지원 두 가지 기능 모두 이전에 Public Preview 상태였다가 현재 일반 공개(Generally Available) 되었습니다.

## Databricks Clean Rooms: 프라이버시 안전 협업

Databricks Clean Rooms는 민감한 데이터에 직접 접근하지 않고도 조직 경계를 넘어 안전하게 협업하기 위한 프라이버시 안전(privacy-safe) 환경을 제공합니다. 시장의 다른 데이터 클린룸(data clean room) 솔루션들과 달리, Databricks Clean Rooms는 Python을 통한 ML 및 AI에 대한 네이티브 지원을 포함해 모든 언어와 워크로드를 지원합니다. 이 유연하고 상호 운용 가능하며 확장 가능한 솔루션을 통해 조직들은 데이터 복제 없이 어떤 클라우드나 플랫폼에서도 누구와든 안전하게 협업할 수 있습니다.

Databricks Clean Rooms는 AWS와 Azure에서 **Public Preview** 로 제공될 예정입니다. 이번 발표와 함께 새로운 Clean Rooms 기능들도 소개되었습니다.

### 크로스 클라우드 페더레이션 공유 (Federated Sharing Across Clouds)

Clean Rooms에서 이제 클라우드 간 페더레이션 공유를 지원합니다. 서로 다른 클라우드 환경에 있는 협업 파트너들도 데이터 복제 없이 하나의 Clean Room 내에서 안전하게 공동 작업할 수 있습니다.

### HIPAA 지원

의료 산업을 위한 **HIPAA 컴플라이언스 지원** 이 추가되었습니다. 헬스케어 기업들이 환자 데이터의 프라이버시와 규제 요건을 준수하면서도 연구 및 분석 협업을 수행할 수 있게 됩니다.

### Management API

자동화를 위한 **Management API** 가 제공됩니다. 기업의 IT 팀과 데이터 엔지니어링 팀이 Clean Rooms의 생성, 관리, 모니터링을 프로그래밍 방식으로 자동화할 수 있습니다.

### 단일 메타스토어 내 자기 협업 (Self-Collaboration)

단일 메타스토어 내에서 **자기 협업(self-collaboration)** 이 가능해졌습니다. 같은 조직 내의 서로 다른 팀이나 사업부가 Clean Room 환경을 통해 내부 데이터를 프라이버시 안전하게 공유하고 분석할 수 있습니다.

{% hint style="info" %}
Databricks Clean Rooms는 LiveRamp, Habu 등 주요 파트너와 통합을 지원합니다. LiveRamp의 마이크 모로(Mike Moreau) 운영 부사장은 "LiveRamp와 Databricks Clean Rooms는 마케터들이 프라이버시를 보호하면서도 훌륭한 고객 경험을 창출하는 데 필요한 도구를 제공합니다"라고 말했습니다.
{% endhint %}

## Databricks Marketplace: 지속적인 성장과 혁신

2023년 6월에 출시된 Databricks Marketplace는 데이터, 분석, AI에 관한 모든 니즈를 충족하는 개방형 플랫폼으로 자리잡았습니다. Delta Sharing을 기반으로 하는 Marketplace는 다양한 데이터셋, AI 모델, 노트북, 솔루션을 제공하며, 지난 한 해 동안 놀라운 성장을 기록했습니다.

지난 한 해 동안 Marketplace에는 여러 혁신적인 기능이 추가되었습니다.

- **AI Model Sharing on Marketplace**: 마켓플레이스에서 AI 모델을 공유하고 검색할 수 있는 기능
- **Volume Sharing on Marketplace**: 이미지, 오디오, 비디오, PDF 등 비정형 또는 비테이블형 데이터를 대량으로 공유할 수 있는 기능으로 현재 일반 공개(GA) 상태
- **Databricks to Open Sharing**: Databricks에서 비(非)Databricks 수신자에게 직접 데이터를 공유하는 기능
- **Private Exchanges**: 데이터 소비자가 데이터 제품을 더 빠르게 발견하고 평가할 수 있도록 지원하는 프라이빗 교환 기능
- **Solution Accelerators**: 다양한 산업 및 사용 사례에 맞춘 솔루션 액셀러레이터

Databricks Marketplace는 리스팅 수가 전년 대비 320% 증가하여 2,000개 이상의 리스팅을 보유하게 되었습니다. 이는 파트너 생태계가 얼마나 빠르게 성장하고 있는지를 잘 보여줍니다.

## 새로운 전략적 파트너십 확대

Databricks는 업계 선도 기업들과의 새로운 전략적 파트너십을 맺어 Delta Sharing 개방형 생태계의 범위를 넓히고 있습니다. 여기에는 데이터 공유 솔루션 구축을 위한 신규 전략적 파트너십 체결, 새로운 기능을 위한 기존 Built-On 파트너십 확대, 플랫폼 간 원활한 공유를 돕는 기술 파트너십 강화가 포함됩니다.

이번에 새롭게 합류한 파트너로는 **Acxiom, Amperity, Atlassian, Aveva, HealthVerity, Shutterstock, Stocktwits, T-Mobile, TetraScience, The Trade Desk** 가 있으며, **Epsilon, LiveRamp, S&P Global, Tableau** 와의 파트너십도 확대되었습니다.

### Acxiom

Acxiom의 글로벌 아이덴티티 부문 수석 부사장 카일 홀러웨이(Kyle Hollaway)는 다음과 같이 말했습니다. "Databricks Delta Sharing을 활용하여 시장에서 가장 안전하고 최고 성능을 자랑하는 데이터 위생(data hygiene) 및 아이덴티티 해석 제품인 Real ID 제품군의 도달 범위와 접근성을 확대할 수 있습니다. Databricks Marketplace에 합류함으로써 고객들이 기술 장벽 없이 당사 기술에 접근할 수 있는 맞춤형 솔루션을 제공할 수 있게 되었습니다. Real ID에 대한 원활한 직접 접근을 통해 고객들은 Databricks 환경 내에서 고급 오디언스 구성, 개인화 마케팅, 상세 성과 측정 등을 실행할 수 있습니다."

### Atlassian

Atlassian의 데이터 플랫폼 제품 책임자 수레시 라만(Suresh Raman)은 다음과 같이 전했습니다. "Atlassian Analytics는 최근 Delta Sharing을 활용한 Data Shares를 출시하여 고객의 유연성을 높이고 인사이트 도출 시간을 단축하였습니다. 사용자들이 Atlassian Analytics 내에서 작업하든, 기존에 익숙한 대시보드를 계속 활용하든, Tableau, PowerBI, Spark를 포함한 Delta Sharing의 개방형 커넥터 생태계를 통해 Atlassian Data Lake의 데이터로 자신들의 환경을 손쉽게 구동할 수 있습니다."

### HealthVerity

HealthVerity의 CEO 앤드루 크레스(Andrew Kress)는 다음과 같이 말했습니다. "Databricks와의 파트너십을 심화하고 Databricks Marketplace를 통해 존재감을 확대하게 되어 기쁩니다. 이번 협력을 통해 제약사, 정부 기관, 의료 기관 등 우리 고객들이 국내 최대 실세계 헬스케어 데이터 생태계에서 포괄적이고 비식별화된 헬스케어 데이터에 손쉽게 접근할 수 있게 됩니다. 이를 통해 과학적 발견을 가속하고 혁신적인 의료 성과를 달성할 수 있습니다. 함께 우리는 헬스케어 데이터 프라이버시, 거버넌스, 상호 운용성의 새로운 기준을 세우고 있습니다."

### S&P Global

S&P Global Market Intelligence의 유통 솔루션 책임자 데이비드 콜루치오(David Coluccio)는 다음과 같이 전했습니다. "개방형 생태계를 제공하는 Databricks의 Delta Sharing 플랫폼을 통해 데이터 배포 역량을 강화하고 S&P Global의 다양한 콘텐츠를 고객들이 더욱 원활하게 이용할 수 있도록 지속 협력하게 되어 기쁩니다. 이는 S&P Global Capital IQ Workbench를 시작으로 한 Databricks와의 협력을 한층 더 발전시키는 것입니다."

### Shutterstock

Shutterstock의 최고 기업 책임자 에이미 이건(Aimee Egan)은 다음과 같이 말했습니다. "Shutterstock은 거의 10억 개에 달하는 크리에이티브 콘텐츠 자산을 개방형 데이터 및 AI 협업을 지향하는 플랫폼인 Databricks Marketplace에 출시합니다. 이번 통합을 통해 윤리적으로 수집된 방대한 비주얼 콘텐츠 라이브러리에 대한 탁월한 접근성을 제공하여, 다양한 산업에서 책임 있는 AI 및 ML 이니셔티브를 이끌어갈 수 있습니다. Delta Sharing을 데이터 제공 방식으로 추가하게 되어 기쁩니다."

### T-Mobile

T-Mobile의 최고 데이터 및 AI 책임자(SVP) 그랜트 레이스(Grant Reis)는 다음과 같이 밝혔습니다. "T-Mobile은 Databricks Marketplace에 출시하게 되어 기쁩니다. Databricks 고객들은 이제 당사 역량을 활용하여 마케팅 전략을 고도화하고, 고객 참여를 최적화하며, 고객과 잠재 고객에 대한 더 깊은 이해를 통해 비즈니스 성장을 이끌 수 있습니다."

### Tableau

Tableau의 첨단 분석 부문 SVP 알리 토레(Ali Tore)는 다음과 같이 전했습니다. "Tableau와 Databricks의 동맹은 고객들에게 큰 도약이며, 데이터에서 더 높은 가치를 창출하려는 기업들에게 게임 체인저입니다. 새로운 Delta Sharing 커넥터는 고급 분석과 개방적이고 안전한 데이터 공유·협업 방식의 장점을 결합하여, 수천 명의 Tableau 사용자들이 인사이트 도출 시간을 줄이고 거버넌스 방식으로 보다 정보에 기반한 의사결정을 내릴 수 있는 길을 열어줍니다."

### TetraScience

TetraScience의 CEO 패트릭 그레이디(Patrick Grady)는 다음과 같이 말했습니다. "과학 AI는 더 효과적이고 안전한 치료제 개발을 시작으로 인류의 거대한 도전들을 해결하는 열쇠입니다. Databricks와의 파트너십은 AI가 혁신의 속도와 품질을 향상시켜 이 중요한 산업의 경제를 변화시키는 촉매 역할을 하도록 보장하는 데 필수적입니다. Delta Sharing을 통해 과학자와 데이터 과학자들이 더 빠르게 'AI 네이티브'를 달성하고 데이터에서 더 빠른 ROI를 실현할 수 있도록 지원합니다."

### The Trade Desk

The Trade Desk의 데이터 파트너십 부사장 제이 고벨(Jay Goebel)은 다음과 같이 전했습니다. "Databricks와의 파트너십은 고객들이 디지털 미디어 구매에서 데이터를 활용하는 방식을 혁신하여, 더 효과적인 광고 캠페인을 위한 실시간 인사이트 활용 역량을 강화합니다. Databricks Delta Sharing의 개방형 생태계, Databricks Data Intelligence Platform의 강력한 예측 분석 역량, 그리고 The Trade Desk의 업계 선도적인 광고 기술이 결합되어, 마케터들이 캠페인을 최적화하고 전례 없는 수준의 정밀도와 효율성을 달성할 수 있도록 지원합니다."

## CTO의 말: 개방형 협업의 미래

Databricks의 공동 창업자 겸 CTO 마테이 자하리아(Matei Zaharia)는 다음과 같이 말했습니다. "오늘날 모든 기업이 선택한 플랫폼이나 클라우드에 관계없이 파트너 및 고객과 데이터 및 AI에 관해 협업할 수 있어야 하는 것이 필수적입니다. Databricks Data Intelligence Platform은 개방형 공유와 협업을 위해 구축되었습니다. Clean Rooms에 대한 지속적인 제품 혁신에 투자하고 전략적 파트너들을 우리의 개방형 생태계에 환영하게 되어 기쁩니다. 우리는 고객들에게 크로스 플랫폼 공유와 협업을 단순화하는 최고의 역량을 계속 제공해 나가겠습니다."

## 마치며: 개방형 데이터 협업의 새로운 장

이번 Data + AI Summit 2024에서 발표된 기능들은 Databricks가 단순한 데이터 플랫폼을 넘어 진정한 개방형 데이터 협업 생태계를 구축하고 있음을 보여줍니다. Delta Sharing의 오픈 프로토콜을 중심으로 한 이 생태계는 다음과 같은 핵심 가치를 제공합니다.

첫째, **개방성(Openness)** 입니다. 벤더 종속 없이 어떤 플랫폼, 클라우드, 도구와도 연동됩니다.

둘째, **보안(Security)** 입니다. OIDC 기반 인증, 세밀한 이그레스 제어, Clean Rooms 환경을 통해 데이터 공유 전 과정에서 보안을 유지합니다.

셋째, **확장성(Scale)** 입니다. 16,000명 이상의 수신자와 300% 이상의 성장이 입증하듯, 엔터프라이즈 규모의 협업을 지원합니다.

데이터가 기업 경쟁력의 핵심 자원이 되는 시대에, 데이터를 안전하고 효율적으로 공유하고 협업하는 능력은 그 자체로 중요한 경쟁 우위가 됩니다. Databricks의 Delta Sharing 생태계는 이 새로운 시대를 위한 인프라를 제공합니다.

Delta Sharing, Clean Rooms, Databricks Marketplace에 대한 자세한 내용은 [Databricks 공식 문서](https://docs.databricks.com/aws/en/delta-sharing/)를 참고하세요.
