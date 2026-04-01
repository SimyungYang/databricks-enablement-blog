# Workspace 생성

## Workspace 생성 — Account Console

accounts.cloud.databricks.com → Workspaces → Create workspace

### 입력 항목

| 항목 | 설정값 |
|------|--------|
| **Workspace name**| 식별 이름 (예: `prod-workspace-apne2`) |
| **Region**| `ap-northeast-2` (Seoul) |
| **Credential configuration**| Credential 구성에서 생성한 Credential 선택 |
| **Storage configuration**| Storage 구성에서 생성한 Storage 선택 |
| **Network configuration**| Network 구성에서 생성한 Network 선택 (PrivateLink 포함) |
| **Private access settings**| Backend PrivateLink에서 생성한 PAS 선택 |
| **Pricing tier**| **Enterprise**(PrivateLink 사용 시 필수) |
| **CMK**(선택) | Managed services CMK / Storage CMK |

**Create workspace**클릭 → 프로비저닝 시작

*참고: [Create a workspace](https://docs.databricks.com/aws/en/admin/account-settings-e2/workspaces) · [Terraform: databricks_mws_workspaces](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/mws_workspaces)*

## Workspace 생성 후 확인

프로비저닝 완료까지 대기합니다.

### 상태 확인

| 상태 | 의미 |
|------|------|
| **PROVISIONING**| 생성 중 |
| **RUNNING**| 정상 — 사용 가능 |
| **FAILED**| 실패 — 에러 메시지 확인 |

### 소요 시간

| 단계 | 시간 |
|------|------|
| Workspace 프로비저닝 | ~5-7분 |
| PrivateLink DNS 전파 | +10-20분 |
| **클러스터 생성 가능**| 프로비저닝 후 **최소 20분 대기**|

{% hint style="warning" %}
PrivateLink 워크스페이스는 프로비저닝 완료 후 **20분 대기**필요 — DNS 전파 시간. 로컬 DNS 캐시 플러시: `sudo killall -HUP mDNSResponder` (macOS) 또는 `ipconfig /flushdns` (Windows)
{% endhint %}

## 구성 완료 체크리스트

전체 과정 최종 확인:

| # | 단계 | AWS 리소스 | Databricks 등록 |
|---|------|-----------|----------------|
| 1 | Marketplace 구독 | AWS Marketplace 구독 | Databricks 계정 생성 |
| 2 | Credential | IAM Cross-Account Role | Credential Configuration |
| 3 | Storage | S3 Bucket + Bucket Policy | Storage Configuration |
| 4 | Network | VPC + 2 Private Subnets + SG | Network Configuration |
| 5 | Backend PL | 2x VPC Endpoints (REST + Relay) | VPC Endpoint 등록 + Network 연결 |
| 6 | Access Settings | — | Private Access Settings |
| 7 | Workspace | — | Workspace 생성 (RUNNING 확인) |
| 8 | [옵션] Frontend | Transit VPC + 1x Endpoint + R53 | VPC Endpoint 등록 |
| 9 | UC Storage | IAM Role + S3 | Storage Credential |
| 10 | 최종 검증 | — | 브라우저 접속 + 클러스터 생성 |

## 주의사항 & 트러블슈팅

### IAM Role 등록 실패

- IAM Role 생성 직후 Databricks 등록 시 **eventual consistency**문제
- **10~30초 대기 후 재시도**(Terraform 사용 시 `time_sleep` 리소스)

### Network 수정 시 3단계 프로세스

1. 새 Network Configuration 생성
2. Workspace에서 새 Network로 교체
3. 기존 Network Configuration 삭제
- *직접 수정 → `INVALID_STATE` 에러*

### PrivateLink 워크스페이스 접근 불가

- DNS 캐시 플러시: `sudo killall -HUP mDNSResponder` / `ipconfig /flushdns`
- `nslookup <workspace>.cloud.databricks.com` → Private IP 확인
- VPC Endpoint 상태: `available` 확인 (AWS Console → VPC → Endpoints)
- Security Group: 443, 6666 양방향 확인
