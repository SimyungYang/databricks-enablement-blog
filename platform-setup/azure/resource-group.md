# Resource Group 생성

## Step 1 — Azure Portal 접속

Azure Portal(`https://portal.azure.com`)에 로그인합니다.

## Step 2 — 리소스 그룹 만들기

1. 상단 검색창에서 "** 리소스 그룹**" 검색 → **리소스 그룹** 클릭
2. **+ 만들기** 클릭

## Step 3 — 기본 정보 입력

| 필드 | 값 | 설명 |
|------|-----|------|
| **구독** | 사용할 Azure 구독 선택 | |
| **리소스 그룹 이름** | `rg-databricks-prod` | 명명 규칙에 맞게 조정 |
| **리전** | Korea Central | 모든 리소스를 동일 리전에 배치 |

## Step 4 — 태그 설정

| 태그 키 | 값 (예시) |
|---------|-----------|
| `Owner` | `data-engineering-team` |
| `Environment` | `production` |
| `Project` | `databricks-platform` |

{% hint style="info" %}
태그는 비용 관리와 거버넌스에 중요합니다. 조직의 태깅 정책에 맞게 설정하세요.
{% endhint %}

## Step 5 — 검토 + 만들기

**검토 + 만들기** 클릭 → 유효성 검사 통과 확인 → **만들기** 클릭
