# Marketplace 구독

## 개요

AWS Marketplace를 통해 Databricks를 구독하면 AWS 인보이스에 Databricks 사용료가 통합됩니다. 특히 AWS EDP(Enterprise Discount Program) 크레딧이 있는 고객에게 유리한 구매 경로입니다.

{% hint style="info" %}
**왜 Marketplace인가?**AWS EDP 잔여 크레딧이 있으면 Databricks 비용이 EDP 소진에 포함됩니다. 즉, 이미 약정한 AWS 지출에 Databricks를 포함시켜 추가 비용 없이 활용할 수 있습니다.
{% endhint %}

## 필요한 IAM 권한

Marketplace 구독을 진행하는 AWS 사용자에게 다음 권한이 필요합니다.

| IAM 권한 | 용도 |
|----------|------|
| `aws-marketplace:Subscribe` | Marketplace 제품 구독 |
| `aws-marketplace:Unsubscribe` | 구독 취소 |
| `aws-marketplace:ViewSubscriptions` | 기존 구독 조회 |

{% hint style="warning" %}
**AWS 관리형 정책 사용 권장**: `AWSMarketplaceManageSubscriptions` 정책을 IAM 사용자/역할에 연결하면 위 권한이 모두 포함됩니다. SCP(Service Control Policy)에서 `aws-marketplace:*` 액션을 차단하고 있지 않은지도 확인하세요.
{% endhint %}

## 구독 절차

### Step 1 — Marketplace 접속

1. AWS Console 로그인 → 상단 검색창에 "**AWS Marketplace**" 입력
2. **AWS Marketplace Subscriptions**클릭 → 좌측 메뉴에서 "**Discover products**" 선택
3. 검색창에 "**Databricks**" 입력 → "**Databricks Data Intelligence Platform**" 선택
4. 제품 상세 페이지에서 **Pricing**, **Usage**, **Support** 탭을 확인할 수 있음

{% hint style="info" %}
직접 URL로도 접근 가능합니다: [AWS Marketplace - Databricks](https://aws.amazon.com/marketplace/pp/prodview-wtyi5lgtce6n6)
{% endhint %}

### Step 2 — 구독 시작

1. 제품 상세 페이지 우측 상단의 "**Continue to Subscribe**" 클릭
2. **Terms and Conditions** 화면에서 EULA를 검토
   - Databricks 서비스 이용 약관, 데이터 처리 부속서(DPA) 등이 표시됨
3. "**Accept Terms**" 클릭
4. 구독 처리 중 화면이 표시됨 — 보통 1-2분 소요
5. 상태가 "**Subscription active**"로 변경되면 "**Set up your account**" 버튼 활성화

### Step 3 — Databricks 계정 생성

1. "**Set up your account**" 클릭 → Databricks 등록 페이지로 리다이렉트
2. 다음 정보 입력:
   - **Company name**: 회사명 (정확한 법인명 권장)
   - **Email**: 관리자 이메일 (이 이메일이 Account Admin이 됨)
   - **Full name**: 관리자 이름
   - **Password**: 비밀번호 설정
3. "**Get started**" 클릭 → 이메일 인증 메일 수신
4. 이메일 인증 완료 후 Databricks Account Console 접근 가능

### Step 4 — 결과 확인

1. AWS Marketplace → "**Manage Subscriptions**" 메뉴에서 Databricks 구독 활성 상태 확인
2. Databricks Account Console (`https://accounts.cloud.databricks.com`) 로그인
3. **Settings → Subscription & billing**메뉴에서 **AWS Marketplace** 결제 수단 확인

{% hint style="info" %}
구독 완료 즉시 **Serverless Workspace** 를 사용할 수 있습니다. Classic Workspace를 생성하려면 별도의 AWS 인프라 구성(VPC, IAM Role 등)이 필요합니다.
{% endhint %}

## 구독 후 첫 번째 해야 할 일

1. **Account Console 접속**→ `https://accounts.cloud.databricks.com`
2. **추가 Account Admin 지정**— Settings → User Management → 사용자 추가 후 Account Admin 역할 부여
3. **Unity Catalog 메타스토어 생성**— Catalog → 리전에 맞는 메타스토어 생성
4. **첫 Workspace 생성**— Workspaces 메뉴에서 Serverless 또는 Classic Workspace 생성
5. **비용 알림 설정**— Settings → Usage → Budget alert 구성

## Marketplace vs Direct 계약

고객 상황에 따른 최적 선택:

| 항목 | Marketplace (PAYG) | Marketplace (Private Offer) | Direct 계약 |
|------|---|---|---|
| **과금**| AWS 인보이스 통합 | AWS 인보이스 통합 | Databricks 별도 인보이스 |
| **EDP 적용**| **O**— AWS EDP 소진 가능 | **O**| X |
| **가격**| 리스트 가격 | 협상 할인가 | 협상 할인가 |
| **약정**| 없음 (종량제) | 연간/다년 약정 | 연간/다년 약정 |
| **셋업 속도**| 수분 (셀프서비스) | 수일~수주 (Databricks 영업팀 협의) | 수일~수주 |
| **계약 유연성**| 언제든 취소 가능 | 약정 기간 고정 | 약정 기간 고정 |
| **기술 지원**| Standard 포함 | 약정에 따라 Premium 가능 | Premium 포함 가능 |

### 선택 가이드

- **PoC / 소규모 팀**: Marketplace PAYG — 즉시 시작, 종량제, 리스크 없음
- **AWS EDP 잔여 크레딧 보유**: Marketplace (PAYG 또는 Private Offer) — EDP 소진 활용
- **대규모 도입 + 할인 필요**: Marketplace Private Offer — EDP 혜택 + 볼륨 할인
- **멀티 클라우드 통합 계약**: Direct 계약 — Azure/GCP 포함 단일 계약 가능

{% hint style="info" %}
**EDP(Enterprise Discount Program)란?**AWS와 일정 기간 최소 사용량을 약정하고 할인을 받는 프로그램입니다. Marketplace를 통한 Databricks 지출이 이 약정 금액에 포함되므로, EDP 소진율을 높이는 효과가 있습니다.
{% endhint %}

## 기존 계정에 Marketplace 연결

이미 Databricks 계정이 있는 경우 (Direct 계약에서 전환 등):

### 연결 절차

1. Databricks Account Console 로그인 (`https://accounts.cloud.databricks.com`)
2. **Settings**→ **Subscription & billing** 메뉴 이동
3. "**Add payment method**" 클릭 → "**AWS Marketplace account**" 선택
4. AWS Console로 리다이렉트 → Marketplace 구독 절차 진행 (위 Step 1-2와 동일)
5. 구독 완료 후 Account Console로 복귀
6. "**Set to primary payment method**" 클릭하여 기본 결제 수단 변경

### Troubleshooting

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| "**You've already accepted this offer**" 오류 | 해당 AWS 계정이 이미 다른 Databricks 계정에 연결됨 | 기존 연결을 해제하거나 다른 AWS 계정 사용 |
| **리다이렉트 후 빈 화면**| 팝업 차단 또는 3rd-party 쿠키 차단 | 브라우저 팝업 허용, 쿠키 설정 확인 |
| **구독 완료 후 Account Console에 미반영**| 전파 지연 (최대 24시간) | 24시간 대기 후 재확인, 지속 시 Databricks 지원팀 문의 |
| **Payment method 변경 불가**| Account Admin 권한 부재 | Account Admin 역할 보유 사용자로 로그인 |

### 주의사항

{% hint style="warning" %}
- **1 AWS Marketplace 계정 = 1 Databricks 계정** 매핑 (N:1은 가능: 여러 AWS 계정 → 하나의 Databricks 계정)
- Marketplace 구독 취소 ≠ Databricks 계정 삭제 (과금 수단만 제거됨, 데이터/Workspace는 유지)
- Direct 계약에서 Marketplace로 전환 시, 기존 약정 잔여 기간을 확인하세요. 중복 과금이 발생할 수 있습니다.
- Marketplace Private Offer 전환은 Databricks 영업팀과 별도 협의가 필요합니다.
{% endhint %}

*참고: [Subscribe via AWS Marketplace](https://docs.databricks.com/aws/en/admin/account-settings/account) · [AWS Marketplace Listing](https://aws.amazon.com/marketplace/pp/prodview-wtyi5lgtce6n6)*
