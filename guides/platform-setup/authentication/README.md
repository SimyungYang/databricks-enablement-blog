# 인증 종합 가이드

## 왜 인증이 중요한가

Databricks는 데이터 레이크하우스의 모든 자산 — 테이블, 모델, 노트북, Job — 에 대한 접근을 **API 기반** 으로 제어합니다. 웹 UI에서 클릭하든, CLI에서 명령을 실행하든, CI/CD 파이프라인이 자동으로 배포하든, 결국은 REST API 호출이 발생하고, 그 호출에는 반드시 **"누가(Who) 어떤 권한(What)으로 요청하는가"** 를 증명하는 인증 토큰이 필요합니다.

인증이 부실하면 다음과 같은 문제가 연쇄적으로 발생합니다.

| 문제 | 결과 |
|------|------|
| 공유 계정/토큰 사용 | 감사 추적 불가, 사고 발생 시 책임 소재 불분명 |
| 장기 유효 토큰 유출 | 외부 공격자가 전체 워크스페이스에 무제한 접근 |
| 직원 퇴사 후 토큰 미회수 | 전직 직원의 권한이 그대로 남아 보안 사각지대 형성 |
| 인증과 인가 혼동 | 과도한 권한 부여로 최소 권한 원칙(Principle of Least Privilege) 위반 |

이 가이드에서 다루는 모든 인증 방법의 공통 목표는 하나입니다: **Zero Trust 보안 모델 하에서, 모든 요청에 대해 신원을 검증하고, 최소한의 권한만 부여하며, 자격 증명의 수명을 최소화하는 것** 입니다.

---

## 인증 방법 전체 비교

아래 테이블은 Databricks가 지원하는 네 가지 인증 방법의 핵심 차이를 한눈에 보여줍니다.

| 인증 방법 | 대상 | 보안 수준 | 토큰 수명 | 자동 갱신 | Account 레벨 | 권장 용도 |
|-----------|------|----------|----------|----------|------------|----------|
| **OAuth U2M** | 사용자 | 높음 | 1시간 | ✅ | ✅ | 대화형 도구 (CLI, SDK, IDE) |
| **OAuth M2M** | Service Principal | 높음 | 1시간 | ✅ (재발급) | ✅ | CI/CD, 자동화, 스케줄 Job |
| **OAuth Token Federation** | 외부 워크로드 | 매우 높음 | 1시간 | ✅ | ✅ | GitHub Actions, Cloud 워크로드 |
| **PAT** | 사용자/SP | 보통 | 설정 가능 (최대 무기한) | ❌ | ❌ | 레거시 통합, 빠른 테스트 |

**핵심 시사점**: OAuth 기반 인증(U2M, M2M, Token Federation)은 모두 **1시간 수명의 단기 토큰** 을 사용합니다. 토큰이 유출되더라도 1시간 후 자동 만료되므로 피해 범위가 제한됩니다. 반면 PAT는 사용자가 설정한 수명(최대 무기한)까지 유효하며, 유출 시 수동으로 폐기하기 전까지 악용될 수 있습니다. Databricks는 모든 시나리오에서 **OAuth를 강력히 권장** 합니다.

---

## 어떤 인증을 선택해야 하는가?

의사결정은 **"누가 인증하는가"** 와 **"어떤 환경에서 실행되는가"** 두 가지 축으로 결정됩니다.

```
                    ┌─────────────────────┐
                    │  인증 주체가 누구인가?  │
                    └────────┬────────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
           사람(User)    자동화 시스템    빠른 테스트
                │            │            │
                ▼            │            ▼
          OAuth U2M          │        PAT (단기)
        (CLI, SDK, IDE)      │      ⚠️ 프로덕션 사용 자제
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
              외부 IdP 있음?      외부 IdP 없음
           (GitHub, Azure AD,         │
            AWS IAM 등)               ▼
                    │            OAuth M2M
                    ▼         (client_credentials)
            Token Federation
           (Secret 관리 불필요)
```

### 시나리오별 가이드

아래 테이블은 실무에서 자주 만나는 시나리오와 적합한 인증 방법을 매핑합니다.

| 시나리오 | 권장 인증 | 이유 |
|---------|----------|------|
| 개발자가 로컬에서 Databricks CLI 사용 | **OAuth U2M** | 브라우저 로그인 한 번으로 토큰 자동 관리 |
| VS Code + Databricks Extension | **OAuth U2M** | IDE가 브라우저 인증 흐름을 자동 처리 |
| GitHub Actions에서 Unity Catalog 배포 | **Token Federation** | GitHub OIDC 토큰으로 Secret 없이 인증 |
| Jenkins에서 Job 트리거 | **OAuth M2M** | Service Principal + client_credentials |
| Terraform으로 워크스페이스 프로비저닝 | **OAuth M2M** | IaC 파이프라인에 SP 인증 적용 |
| Airflow에서 Databricks Operator 사용 | **OAuth M2M** | Connection에 SP client_id/secret 설정 |
| 빠른 API 테스트 (일회성) | **PAT** | 발급이 빠르지만, 프로덕션 전환 시 OAuth로 교체 |
| 외부 SaaS에서 Databricks API 호출 | **OAuth M2M** | SaaS가 SP로 인증, 최소 권한 부여 |

위 테이블에서 알 수 있듯이, **프로덕션 환경에서는 PAT를 사용하는 시나리오가 없습니다.** PAT는 개발 초기 단계의 빠른 검증용으로만 활용하고, 반드시 OAuth로 전환해야 합니다.

---

## On-Behalf-Of (위임 인증) 개념

Databricks 인증에서 가장 중요하면서도 자주 혼동되는 개념이 **On-Behalf-Of (OBO)** 입니다.

### 핵심 아이디어

사용자가 Databricks CLI를 실행하면, CLI 자체가 Databricks에 접근하는 것이 아닙니다. CLI는 **사용자를 대신하여(on behalf of)** API를 호출합니다. 즉:

- **인증 주체**: 사용자 본인 (브라우저로 로그인)
- **실행 주체**: CLI/SDK/IDE (도구)
- **권한**: 사용자 본인의 권한 그대로 적용

이것이 의미하는 바는 다음과 같습니다.

| 관점 | 설명 |
|------|------|
| 감사 로그 | API 호출이 "CLI"가 아닌 **사용자 이름** 으로 기록됨 |
| 권한 범위 | 도구가 사용자보다 더 많은 권한을 가질 수 없음 |
| 토큰 수명 | 사용자 세션에 연동, 로그아웃하면 토큰 무효화 |

이 설명이 보여주듯, OBO는 보안과 감사의 핵심입니다. 도구에 독립적인 권한을 부여하지 않으므로, **사용자 퇴사 = 도구 접근 자동 차단** 이 됩니다.

### OBO vs Service Principal

| 구분 | On-Behalf-Of (U2M) | Service Principal (M2M) |
|------|--------------------|-----------------------|
| 인증 주체 | 사람 | 시스템 ID |
| 권한 소유 | 사용자 본인 | SP에 별도 부여 |
| 감사 로그 | 사용자 이름 | SP 이름 |
| 사용자 퇴사 시 | 자동 차단 | 영향 없음 (의도된 동작) |
| 대표 사용 | CLI, IDE, 노트북 | CI/CD, 스케줄 Job, IaC |

---

## 다음 단계

각 인증 방법의 동작 원리, 설정 방법, 코드 예시를 상세히 다루는 서브페이지로 이동하세요.

| 가이드 | 내용 |
|--------|------|
| [OAuth U2M (사용자 인증)](oauth-u2m.md) | PKCE 흐름, 브라우저 인증, 토큰 갱신, CLI/SDK 설정 |
| [OAuth M2M (서비스 인증)](oauth-m2m.md) | Service Principal, client_credentials, 코드 예시 |
| [PAT & Token Federation](pat-federation.md) | PAT 생성/관리, Token Federation 개념, GitHub Actions 연동 |

{% hint style="info" %}
**권장 읽기 순서**: 개발자라면 OAuth U2M → OAuth M2M → PAT & Token Federation 순서로 읽으세요. 플랫폼 관리자라면 이 README의 비교 테이블을 기준으로 팀에 적합한 인증 정책을 먼저 결정한 후, 해당 방법의 상세 가이드를 참고하세요.
{% endhint %}
