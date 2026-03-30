# Marketplace 구독

## 구독 절차

AWS Console에서 수동으로 진행합니다.

### Step 1 — Marketplace 접속

- AWS Marketplace에서 **"Databricks"** 검색
- 또는 직접 접속: `aws.amazon.com/marketplace` → Databricks Data Intelligence Platform

### Step 2 — 구독 및 계정 생성

1. **"Subscribe"** 클릭 → EULA 동의
2. **"Set up your account"** → Databricks 등록 페이지로 리다이렉트
3. 회사명, 이메일, 비밀번호 입력 → 계정 생성 완료
4. AWS Marketplace로 돌아와 **"Continue to Databricks"** 클릭

### Step 3 — 결과

- Databricks Account 생성 + AWS Marketplace 과금 연결
- **Serverless Workspace** 즉시 사용 가능

*참고: [Subscribe via AWS Marketplace](https://docs.databricks.com/aws/en/admin/account-settings/account) · [AWS Marketplace Listing](https://aws.amazon.com/marketplace/pp/prodview-wtyi5lgtce6n6)*

## Marketplace vs Direct 계약

고객 상황에 따른 최적 선택:

| 항목 | Marketplace (PAYG) | Marketplace (Private Offer) | Direct 계약 |
|------|---|---|---|
| **과금** | AWS 인보이스 통합 | AWS 인보이스 통합 | Databricks 별도 인보이스 |
| **EDP 적용** | **O** — AWS EDP 소진 가능 | **O** | X |
| **가격** | 리스트 가격 | 협상 할인가 | 협상 할인가 |
| **약정** | 없음 (종량제) | 연간/다년 약정 | 연간/다년 약정 |
| **셋업 속도** | 수분 (셀프서비스) | 수일~수주 | 수일~수주 |

{% hint style="info" %}
**핵심**: AWS EDP 잔여 크레딧이 있는 고객은 Marketplace 구독이 유리 — Databricks 비용이 EDP 소진에 포함됨
{% endhint %}

## 기존 계정에 Marketplace 연결

이미 Databricks 계정이 있는 경우:

### 연결 절차

1. Databricks Account Console 로그인
2. **Settings** → **Subscription & billing**
3. **"Add payment method"** → **AWS Marketplace account** 선택
4. AWS Marketplace로 리다이렉트 → 구독 완료
5. 메뉴에서 **"Set to primary payment method"** 선택

### 주의사항

{% hint style="warning" %}
- **1 AWS Marketplace 계정 = 1 Databricks 계정** 매핑 (N:1은 가능)
- "You've already accepted this offer" 오류 → 이미 다른 Databricks 계정에 연결됨
- 구독 취소 ≠ Databricks 계정 삭제 (과금 수단만 제거)
{% endhint %}
