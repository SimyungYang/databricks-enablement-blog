# 00. 팀 협업 가이드

> **전체 노트북 코드**: [00\_team\_collaboration.py](https://github.com/SimyungYang/databricks-enablement-blog/blob/main/hands-on/predictive-maintenance/notebooks/00_team_collaboration.py)

**목적**: 여러 명이 **동시에 ML 모델을 개발** 할 때 발생하는 충돌, 자원 경쟁, 데이터 오염 문제와 해결 방법을 다룹니다.

> **현장 경험담:** "제가 학습 돌리고 있었는데 갑자기 클러스터가 느려졌어요" -- 옆 동료도 같은 클러스터에서 대규모 데이터 전처리를 돌리고 있었습니다. 서로 몰랐습니다. 이런 상황은 팀이 3명만 넘어가면 반드시 생깁니다.

---

## 이 가이드에서 배우는 내용

| 주제 | 핵심 |
|------|------|
| **워크스페이스 구조** | 개인 폴더 vs 공유 폴더, 언제 뭘 쓸까 |
| **클러스터 공유** | 같은 클러스터를 쓸 때 조심할 점 |
| **데이터 충돌 방지** | 테이블/모델 이름 충돌 해결 |
| **MLflow 실험 관리** | 팀원 간 실험 분리와 비교 |
| **절대 하지 말 것** | 사고를 유발하는 행동 목록 |

---

## 1. 워크스페이스 폴더 구조 -- 개인 vs 공유

### Databricks 워크스페이스 구조

```
Workspace/
├── Users/                          ← 개인 폴더 (사용자별 자동 생성)
│   ├── alice@company.com/
│   │   ├── my_experiment.py        ← Alice만 수정 가능
│   │   └── scratch/               ← 실험용 임시 코드
│   └── bob@company.com/
│       └── my_experiment.py        ← Bob만 수정 가능
│
├── Shared/                         ← 공유 폴더 (모든 사용자 접근 가능)
│   └── lgit-mlops-poc/
│       ├── _resources/             ← 공통 설정
│       ├── predictive_maintenance/ ← 정형 파이프라인
│       └── visual_inspection/      ← 비정형 파이프라인
│
└── Repos/                          ← Git 연동 폴더
    └── alice/lgit-mlops/           ← Git 브랜치 기반 협업
```

### 언제 어디를 쓸까?

| 폴더 | 용도 | 적합한 작업 |
|------|------|-----------|
| **Users/{내 이메일}** | 개인 실험, 탐색 | 모델 프로토타이핑, 데이터 분석 |
| **Shared/** | 팀 공유 코드 | 운영 파이프라인, 공통 유틸리티 |
| **Repos/** | Git 기반 협업 | 코드 리뷰, 브랜치별 개발, CI/CD |

### Shared 폴더 사용 시 주의사항

| 규칙 | 이유 | 사고 사례 |
|------|------|----------|
| **동시 편집 금지** | 마지막 저장이 덮어씀 | Alice와 Bob이 같은 노트북을 동시에 수정 → Alice의 변경사항 소실 |
| **직접 실행 주의** | `%run` 경로가 사용자별로 다를 수 있음 | 절대 경로 대신 상대 경로 사용 (`./` 또는 `../`) |
| **운영 코드 직접 수정 금지** | 검증 없이 배포되는 셈 | 누군가 "잠깐 테스트"하고 원복을 깜빡함 → 운영 Job 실패 |

{% hint style="info" %}
**권장:** Shared 폴더의 운영 코드는 **Repos (Git)** 를 통해서만 수정하세요. 개인 브랜치에서 수정 → PR(Pull Request) → 리뷰 → 머지 → Shared에 배포. 이게 제조업의 "ECR (Engineering Change Request, 설계 변경 요청서)" 프로세스와 동일합니다.
{% endhint %}

---

## 2. 클러스터 공유 -- 자원 경쟁 관리

### 클러스터 공유 모드

| 모드 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **Single User** | 한 사람만 사용 | 자원 독점, 충돌 없음 | 비용 비효율 (안 쓸 때도 과금) |
| **Shared (다중 사용자)** | 여러 명이 동시 사용 | 비용 절약 | 자원 경쟁, 라이브러리 충돌 |
| **No Isolation Shared** | 격리 없이 공유 | 가장 저렴 | 보안/안정성 위험 |

{% hint style="info" %}
**권장:** 개발 단계에서는 **Single User** 클러스터를 각자 만들되, Auto Termination을 10~20분으로 설정하세요. 비용이 걱정되면 **Shared** 모드를 쓰되, 아래 규칙을 반드시 지키세요.
{% endhint %}

### 같은 클러스터 공유 시 반드시 지킬 것

#### `%pip install` 은 다른 사람에게 영향을 줍니다

```python
# ❌ 위험: 공유 클러스터에서 이렇게 하면 다른 사람의 노트북도 영향 받음
%pip install pandas==1.5.0   # 다른 사람이 pandas 2.x를 쓰고 있었다면 깨짐

# ✅ 안전: Notebook-scoped library (노트북 단위 격리)
# Databricks에서 %pip은 기본적으로 notebook-scoped이지만,
# %restart_python 후에는 클러스터 레벨 패키지가 복원됩니다.
# 따라서 다른 사람이 같은 패키지를 다른 버전으로 설치하면 충돌 가능
```

> **결론:** 라이브러리 버전이 중요한 작업은 **Single User 클러스터** 를 사용하세요.

#### GPU 클러스터는 절대 공유하지 마세요

```
❌ GPU 공유 시나리오:
  Alice: PatchCore 학습 (GPU 메모리 14GB 사용)
  Bob:   같은 클러스터에서 다른 모델 학습 시도
  결과:  CUDA OOM (Out of Memory) → 둘 다 실패

✅ 올바른 방법:
  Alice: 자신의 GPU 클러스터에서 학습 (Auto Termination 10분)
  Bob:   자신의 GPU 클러스터에서 학습
  결과:  각각 성공, 안 쓸 때 자동 종료 → 비용도 최적화
```

{% hint style="warning" %}
GPU 메모리(VRAM)는 CPU 메모리와 달리 **스왑(Swap)이 불가능** 합니다. 하나라도 초과하면 즉시 OOM으로 프로세스가 죽습니다.
{% endhint %}

#### 장시간 작업은 반드시 Job으로 실행

```python
# ❌ 위험: 인터랙티브 클러스터에서 3시간 학습
# - 클러스터 비용이 계속 발생
# - 실수로 브라우저를 닫으면 결과 유실
# - 다른 사람이 클러스터를 쓸 수 없음

# ✅ 올바른 방법: Databricks Job으로 제출
# - 전용 Job 클러스터가 자동 생성/종료
# - 실패 시 자동 재시도 가능
# - 브라우저를 닫아도 계속 실행
# - 비용 추적이 명확 (Job별 과금)
```

---

## 3. 데이터 충돌 방지 -- 테이블/모델 이름 관리

### 문제: 같은 이름의 테이블을 여러 명이 쓰면?

```
Alice: spark.sql("CREATE TABLE results AS SELECT ...")  ← results 테이블 생성
Bob:   spark.sql("CREATE TABLE results AS SELECT ...")  ← Alice의 results를 덮어씀!
Alice: "내 결과가 왜 바뀌었지??"
```

### 해결: 사용자별 네임스페이스 분리

이 PoC에서 사용하는 방법 -- **카탈로그 분리** :

```python
# _resources/00-setup.py 에서 자동 설정
catalog = "alice_kim"      # Alice의 카탈로그
catalog = "bob_park"       # Bob의 카탈로그

# 같은 코드를 실행해도 서로 다른 테이블에 저장
# Alice: alice_kim.lgit_mlops_poc.lgit_pm_training
# Bob:   bob_park.lgit_mlops_poc.lgit_pm_training
```

| 분리 방식 | 예시 | 격리 수준 | 추천 |
|----------|------|----------|------|
| **카탈로그 분리** | `alice.schema.table` | 완전 분리 | 교육/개발 |
| **스키마 분리** | `catalog.alice_dev.table` | 중간 분리 | 스테이징 |
| **접두사 분리** | `catalog.schema.alice_table` | 약한 분리 | 임시용 |

{% hint style="info" %}
이 PoC에서는 **카탈로그 분리** 를 사용합니다. `00-setup` 노트북에서 사용자 이메일 기반으로 카탈로그가 자동 생성됩니다.
{% endhint %}

---

## 4. MLflow 실험 관리 -- 팀원 간 실험 분리와 비교

### 실험 이름 규칙

```python
# ❌ 나쁜 예: 실험 이름이 모호함
mlflow.set_experiment("my_experiment")  # 누구의? 무슨 실험?

# ✅ 좋은 예: 사용자/프로젝트/날짜가 명확
mlflow.set_experiment(f"/Users/{current_user}/lgit_predictive_maintenance")
```

### 팀원 간 실험 비교

MLflow UI에서 여러 사람의 실험을 비교할 수 있습니다:

```python
import mlflow

# Alice와 Bob의 실험 결과를 한꺼번에 검색
all_runs = mlflow.search_runs(
    experiment_names=[
        "/Users/alice@company.com/lgit_predictive_maintenance",
        "/Users/bob@company.com/lgit_predictive_maintenance",
    ],
    order_by=["metrics.val_f1_score DESC"],
    max_results=10,
)
display(all_runs[["run_id", "tags.mlflow.runName", "metrics.val_f1_score"]])
```

{% hint style="info" %}
**Databricks 장점:** MLflow 실험은 사용자 폴더별로 자동 분리되지만, `search_runs` API로 **팀 전체의 실험을 한 눈에 비교** 할 수 있습니다. "누가 가장 좋은 모델을 만들었는가"를 코드 한 줄로 확인할 수 있습니다.
{% endhint %}

---

## 5. Git 연동 (Repos) -- 코드 협업의 정석

### 왜 Git이 필요한가?

| 문제 | Git 없이 | Git으로 |
|------|---------|--------|
| 코드 충돌 | "누가 내 코드 바꿨어?" | 브랜치별 독립 작업 + 머지 |
| 이력 추적 | 되돌리기 불가능 | `git log`로 모든 변경 이력 확인 |
| 코드 리뷰 | "그냥 Shared에 올렸어요" | PR → 리뷰 → 승인 → 머지 |
| 운영 배포 | 수동 복사 | CI/CD 자동 배포 |

### Databricks Repos 사용 흐름

```
1. Repos에서 Git 저장소 연결
2. 개인 브랜치 생성 (feature/alice-new-model)
3. 노트북에서 코드 수정 + 커밋
4. GitHub/GitLab에서 PR (Pull Request) 생성
5. 팀원 리뷰 → 승인 → 머지
6. main 브랜치 → Shared 폴더에 자동 배포 (CI/CD)
```

{% hint style="info" %}
**현장 경험담:** "Git 도입하면 느려진다"는 반론을 많이 받습니다. 하지만 Git 없이 운영하다 코드 사고가 나면 복구하는 데 며칠이 걸립니다. Git 도입 초기에 1~2시간 투자하면, 나중에 수십 시간을 절약합니다.
{% endhint %}

---

## 6. 절대 하지 말 것 -- 사고를 유발하는 행동 TOP 5

| # | 금기 사항 | 사고 사례 |
|---|----------|----------|
| 1 | **운영 테이블에 직접 DELETE/UPDATE** | `DELETE FROM prod_table WHERE 1=1` 실수 → 전체 삭제 |
| 2 | **Shared 노트북 직접 수정** | 동시 편집 → 코드 충돌 → 6시간 작업 소실 |
| 3 | **GPU 클러스터 공유** | 두 사람이 동시에 학습 → CUDA OOM → 둘 다 실패 |
| 4 | **API 키/비밀번호 코드에 직접 입력** | Git에 커밋되면 즉시 노출 |
| 5 | **다른 사람의 모델을 @Champion으로 변경** | 검증 안 된 모델이 운영에 배포 |

### 올바른 대안

#### 1번: 운영 테이블 수정이 필요할 때

```python
# ❌ 절대 금지: 운영 테이블에 직접 DELETE/UPDATE
spark.sql("DELETE FROM prod_schema.sensor_data WHERE date = '2026-03-01'")

# ✅ 방법 1: 개발 스키마에서 먼저 테스트
spark.sql("SELECT COUNT(*) FROM dev_schema.sensor_data WHERE date = '2026-03-01'")

# ✅ 방법 2: Delta Lake Time Travel로 안전망 확보
spark.sql("DESCRIBE HISTORY prod_schema.sensor_data LIMIT 1")

# ✅ 방법 3: DELETE/UPDATE 전에 반드시 SELECT로 영향 범위 확인
spark.sql("SELECT COUNT(*) FROM prod_schema.sensor_data WHERE date = '2026-03-01'")
```

#### 2번: 팀 공유 코드를 수정해야 할 때

```
❌ Shared 폴더의 노트북을 직접 열어서 수정

✅ Git 기반 워크플로우:
  1. Repos에서 개인 브랜치 생성 → feature/alice-fix-pipeline
  2. 개인 브랜치에서 코드 수정 + 테스트
  3. PR(Pull Request) 생성 → 팀원 코드 리뷰
  4. 승인 후 main 브랜치에 머지 → Shared에 자동 반영
```

#### 3번: GPU가 필요한 학습을 해야 할 때

```python
# ❌ 다른 사람의 GPU 클러스터에서 학습 실행

# ✅ 방법 1: 개인 GPU 클러스터 생성 (Auto Termination 10분)
# ✅ 방법 2: Databricks Job으로 GPU 학습 제출 (권장)
```

#### 4번: API 키/비밀번호를 사용해야 할 때

```python
# ❌ 절대 금지: 코드에 직접 작성
api_key = "sk-abc123..."  # Git에 커밋되면 즉시 노출!

# ✅ Databricks Secrets 사용 (권장)
api_key = dbutils.secrets.get(scope="lgit-secrets", key="openai-api-key")
```

#### 5번: 더 좋은 모델을 만들어서 Champion을 교체하고 싶을 때

```python
# ❌ 직접 Champion alias를 변경

# ✅ Challenger 검증 프로세스를 거치세요
# 1) 새 모델을 @Challenger alias로 등록
# 2) A/B 테스트 또는 동일 데이터셋으로 성능 비교
# 3) 성능이 확인되면 팀 리뷰 후 Champion 교체
# → 05_challenger_validation 노트북 참조
```

### 추가 주의사항

| # | 주의 사항 | 올바른 방법 |
|---|----------|-----------|
| 6 | **클러스터를 끄지 않고 퇴근** | Auto Termination 반드시 설정 (10~20분) |
| 7 | **`DROP TABLE`을 운영 스키마에서 실행** | 개발 스키마에서만 DROP 허용. 운영은 권한으로 보호 |
| 8 | **대용량 데이터를 `collect()`로 Driver에 로드** | `display()` 또는 `limit()` 사용 |
| 9 | **클러스터 로그를 확인하지 않고 "안 돼요" 보고** | Spark UI, Driver Logs 먼저 확인 |
| 10 | **모델 버전 태그 없이 등록** | 반드시 성능 지표, 데이터 소스, 담당자 태그 추가 |

---

## 실무 체크리스트

### 매일 개발 시작 전

- [ ] 내 클러스터가 켜져 있는지 확인 (다른 사람 클러스터에 붙지 않았는지)
- [ ] 내 카탈로그/스키마에서 작업하고 있는지 확인
- [ ] Git 브랜치가 최신 상태인지 `git pull`

### 모델 등록/배포 전

- [ ] MLflow에 실험 결과가 기록되어 있는지
- [ ] 메타데이터(태그)가 빠짐없이 달려 있는지
- [ ] Champion 교체 전 Challenger 검증을 완료했는지
- [ ] 팀원/관리자에게 공유했는지

### 퇴근 전

- [ ] 클러스터 Auto Termination이 설정되어 있는지
- [ ] 임시 테이블/파일을 정리했는지
- [ ] 변경사항을 Git에 커밋했는지

---

## 요약

| 원칙 | 실천 방법 |
|------|----------|
| **격리** | 카탈로그 분리, Single User 클러스터, 개인 실험 폴더 |
| **공유** | MLflow로 실험 비교, Shared 폴더는 읽기 위주, Git으로 코드 협업 |
| **보호** | Auto Termination, `dbutils.secrets`, Champion 변경 권한 제한 |
| **추적** | 모델 태그 필수, Git 이력, MLflow 자동 기록 |

{% hint style="info" %}
**핵심 한 줄:** "내 실험은 내 공간에서, 운영 변경은 리뷰를 거쳐서."
{% endhint %}

---

**다음 단계**: [01. Overview](01-overview.md) 에서 전체 PoC 아키텍처를 확인합니다.
