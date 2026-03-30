# 사전 준비

## 필수 요건

| 항목 | 요구 사항 | 비고 |
|------|-----------|------|
| **Azure Subscription** | 활성 상태 | PAYG, EA, CSP 모두 가능 |
| **Pricing Tier** | **Premium** | Private Link, Unity Catalog 사용 시 필수 |
| **Azure Portal 권한** | Contributor 이상 | 리소스 그룹, VNet, Storage Account 생성 권한 |
| **리전** | Korea Central 권장 | 국내 고객 기준, 다른 리전도 동일 절차 |
| **Azure AD (Entra ID)** | 테넌트 접근 가능 | Managed Identity 생성에 필요 |

{% hint style="warning" %}
**Pricing Tier 주의**: Standard 티어에서는 VNet Injection, Private Link, Unity Catalog를 사용할 수 없습니다. **반드시 Premium 이상**으로 선택하세요.
{% endhint %}

## Databricks Account Console 접근

Azure Databricks는 AWS와 달리 Account Console 접근이 자동으로 설정됩니다.

1. Azure Portal에서 Databricks Workspace를 최초 배포하면 Databricks Account가 자동 생성됨
2. Account Console URL: `https://accounts.azuredatabricks.net`
3. Azure AD(Entra ID) SSO로 로그인

*참고: [Azure Databricks Account Console](https://learn.microsoft.com/azure/databricks/admin/account-settings/)*
