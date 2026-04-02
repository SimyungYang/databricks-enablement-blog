# Databricks notebook source
# MAGIC %md
# MAGIC # 팀 ML 개발 가이드 — 협업 시 꼭 알아야 할 것들
# MAGIC
# MAGIC 이 노트북에서는 여러 명이 **동시에 ML 모델을 개발** 할 때 발생하는 문제와 해결 방법을 다룹니다.
# MAGIC 한 명이 개발할 때는 몰랐던 **충돌, 자원 경쟁, 데이터 오염** 문제가 팀 개발에서는 반드시 발생합니다.
# MAGIC
# MAGIC > **현장 경험담:** "제가 학습 돌리고 있었는데 갑자기 클러스터가 느려졌어요" — 옆 동료도 같은 클러스터에서
# MAGIC > 대규모 데이터 전처리를 돌리고 있었습니다. 서로 몰랐습니다. 이런 상황은 팀이 3명만 넘어가면 반드시 생깁니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 이 노트북에서 배우는 내용
# MAGIC
# MAGIC | 주제 | 핵심 |
# MAGIC |------|------|
# MAGIC | **워크스페이스 구조** | 개인 폴더 vs 공유 폴더, 언제 뭘 쓸까 |
# MAGIC | **클러스터 공유** | 같은 클러스터를 쓸 때 조심할 점 |
# MAGIC | **데이터 충돌 방지** | 테이블/모델 이름 충돌 해결 |
# MAGIC | **MLflow 실험 관리** | 팀원 간 실험 분리와 비교 |
# MAGIC | **절대 하지 말 것** | 사고를 유발하는 행동 목록 |

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 1. 워크스페이스 폴더 구조 — 개인 vs 공유
# MAGIC
# MAGIC ### Databricks 워크스페이스 구조
# MAGIC
# MAGIC ```
# MAGIC Workspace/
# MAGIC ├── Users/                          ← 개인 폴더 (사용자별 자동 생성)
# MAGIC │   ├── alice@company.com/
# MAGIC │   │   ├── my_experiment.py        ← Alice만 수정 가능
# MAGIC │   │   └── scratch/               ← 실험용 임시 코드
# MAGIC │   └── bob@company.com/
# MAGIC │       └── my_experiment.py        ← Bob만 수정 가능
# MAGIC │
# MAGIC ├── Shared/                         ← 공유 폴더 (모든 사용자 접근 가능)
# MAGIC │   └── lgit-mlops-poc/
# MAGIC │       ├── _resources/             ← 공통 설정
# MAGIC │       ├── predictive_maintenance/ ← 정형 파이프라인
# MAGIC │       └── visual_inspection/      ← 비정형 파이프라인
# MAGIC │
# MAGIC └── Repos/                          ← Git 연동 폴더
# MAGIC     └── alice/lgit-mlops/           ← Git 브랜치 기반 협업
# MAGIC ```
# MAGIC
# MAGIC ### 언제 어디를 쓸까?
# MAGIC
# MAGIC | 폴더 | 용도 | 적합한 작업 |
# MAGIC |------|------|-----------|
# MAGIC | **Users/{내 이메일}** | 개인 실험, 탐색 | 모델 프로토타이핑, 데이터 분석 |
# MAGIC | **Shared/** | 팀 공유 코드 | 운영 파이프라인, 공통 유틸리티 |
# MAGIC | **Repos/** | Git 기반 협업 | 코드 리뷰, 브랜치별 개발, CI/CD (Continuous Integration/Continuous Delivery) |

# COMMAND ----------

# MAGIC %md
# MAGIC ### ⚠️ Shared 폴더 사용 시 주의사항
# MAGIC
# MAGIC | 규칙 | 이유 | 사고 사례 |
# MAGIC |------|------|----------|
# MAGIC | **동시 편집 금지** | 마지막 저장이 덮어씀 | Alice와 Bob이 같은 노트북을 동시에 수정 → Alice의 변경사항 소실 |
# MAGIC | **직접 실행 주의** | `%run` 경로가 사용자별로 다를 수 있음 | 절대 경로 대신 상대 경로 사용 (`./` 또는 `../`) |
# MAGIC | **운영 코드 직접 수정 금지** | 검증 없이 배포되는 셈 | 누군가 "잠깐 테스트"하고 원복을 깜빡함 → 운영 Job 실패 |
# MAGIC
# MAGIC > **권장:** Shared 폴더의 운영 코드는 **Repos (Git)** 를 통해서만 수정하세요.
# MAGIC > 개인 브랜치에서 수정 → PR(Pull Request) → 리뷰 → 머지 → Shared에 배포.
# MAGIC > 이게 제조업의 "ECR (Engineering Change Request, 설계 변경 요청서)" 프로세스와 동일합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 2. 클러스터 공유 — 자원 경쟁 관리
# MAGIC
# MAGIC ### 클러스터 공유 모드
# MAGIC
# MAGIC | 모드 | 설명 | 장점 | 단점 |
# MAGIC |------|------|------|------|
# MAGIC | **Single User** | 한 사람만 사용 | 자원 독점, 충돌 없음 | 비용 비효율 (안 쓸 때도 과금) |
# MAGIC | **Shared (다중 사용자)** | 여러 명이 동시 사용 | 비용 절약 | 자원 경쟁, 라이브러리 충돌 |
# MAGIC | **No Isolation Shared** | 격리 없이 공유 | 가장 저렴 | 보안/안정성 위험 |
# MAGIC
# MAGIC > **권장:** 개발 단계에서는 **Single User** 클러스터를 각자 만들되, Auto Termination을 10~20분으로 설정하세요.
# MAGIC > 비용이 걱정되면 **Shared** 모드를 쓰되, 아래 규칙을 반드시 지키세요.

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🚨 같은 클러스터 공유 시 반드시 지킬 것
# MAGIC
# MAGIC #### 1. `%pip install` 은 다른 사람에게 영향을 줍니다
# MAGIC
# MAGIC ```python
# MAGIC # ❌ 위험: 공유 클러스터에서 이렇게 하면 다른 사람의 노트북도 영향 받음
# MAGIC %pip install pandas==1.5.0   # 다른 사람이 pandas 2.x를 쓰고 있었다면 깨짐
# MAGIC
# MAGIC # ✅ 안전: Notebook-scoped library (노트북 단위 격리)
# MAGIC # Databricks에서 %pip은 기본적으로 notebook-scoped이지만,
# MAGIC # %restart_python 후에는 클러스터 레벨 패키지가 복원됩니다.
# MAGIC # 따라서 다른 사람이 같은 패키지를 다른 버전으로 설치하면 충돌 가능
# MAGIC ```
# MAGIC
# MAGIC > **결론:** 라이브러리 버전이 중요한 작업은 **Single User 클러스터** 를 사용하세요.

# COMMAND ----------

# MAGIC %md
# MAGIC #### 2. GPU 클러스터는 절대 공유하지 마세요
# MAGIC
# MAGIC ```
# MAGIC ❌ GPU 공유 시나리오:
# MAGIC   Alice: PatchCore 학습 (GPU 메모리 14GB 사용)
# MAGIC   Bob:   같은 클러스터에서 다른 모델 학습 시도
# MAGIC   결과:  CUDA OOM (Out of Memory) → 둘 다 실패
# MAGIC
# MAGIC ✅ 올바른 방법:
# MAGIC   Alice: 자신의 GPU 클러스터에서 학습 (Auto Termination 10분)
# MAGIC   Bob:   자신의 GPU 클러스터에서 학습
# MAGIC   결과:  각각 성공, 안 쓸 때 자동 종료 → 비용도 최적화
# MAGIC ```
# MAGIC
# MAGIC > **이유:** GPU 메모리(VRAM)는 CPU 메모리와 달리 **스왑(Swap)이 불가능** 합니다.
# MAGIC > 하나라도 초과하면 즉시 OOM으로 프로세스가 죽습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC #### 3. 장시간 작업은 반드시 Job으로 실행
# MAGIC
# MAGIC ```python
# MAGIC # ❌ 위험: 인터랙티브 클러스터에서 3시간 학습
# MAGIC # - 클러스터 비용이 계속 발생
# MAGIC # - 실수로 브라우저를 닫으면 결과 유실
# MAGIC # - 다른 사람이 클러스터를 쓸 수 없음
# MAGIC
# MAGIC # ✅ 올바른 방법: Databricks Job으로 제출
# MAGIC # - 전용 Job 클러스터가 자동 생성/종료
# MAGIC # - 실패 시 자동 재시도 가능
# MAGIC # - 브라우저를 닫아도 계속 실행
# MAGIC # - 비용 추적이 명확 (Job별 과금)
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 3. 데이터 충돌 방지 — 테이블/모델 이름 관리
# MAGIC
# MAGIC ### 문제: 같은 이름의 테이블을 여러 명이 쓰면?
# MAGIC
# MAGIC ```
# MAGIC Alice: spark.sql("CREATE TABLE results AS SELECT ...")  ← results 테이블 생성
# MAGIC Bob:   spark.sql("CREATE TABLE results AS SELECT ...")  ← Alice의 results를 덮어씀!
# MAGIC Alice: "내 결과가 왜 바뀌었지??" 😱
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### 해결: 사용자별 네임스페이스 분리
# MAGIC
# MAGIC 이 PoC에서 사용하는 방법 — **카탈로그 분리** :
# MAGIC
# MAGIC ```python
# MAGIC # _resources/00-setup.py 에서 자동 설정
# MAGIC catalog = "alice_kim"      # Alice의 카탈로그
# MAGIC catalog = "bob_park"       # Bob의 카탈로그
# MAGIC
# MAGIC # 같은 코드를 실행해도 서로 다른 테이블에 저장
# MAGIC # Alice: alice_kim.lgit_mlops_poc.lgit_pm_training
# MAGIC # Bob:   bob_park.lgit_mlops_poc.lgit_pm_training
# MAGIC ```
# MAGIC
# MAGIC | 분리 방식 | 예시 | 격리 수준 | 추천 |
# MAGIC |----------|------|----------|------|
# MAGIC | **카탈로그 분리** | `alice.schema.table` | 완전 분리 | ✅ 교육/개발 |
# MAGIC | **스키마 분리** | `catalog.alice_dev.table` | 중간 분리 | ✅ 스테이징 |
# MAGIC | **접두사 분리** | `catalog.schema.alice_table` | 약한 분리 | △ 임시용 |
# MAGIC
# MAGIC > **이 PoC에서는 카탈로그 분리** 를 사용합니다.
# MAGIC > `00-setup` 노트북에서 사용자 이메일 기반으로 카탈로그가 자동 생성됩니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 4. MLflow 실험 관리 — 팀원 간 실험 분리와 비교
# MAGIC
# MAGIC ### 실험 이름 규칙
# MAGIC
# MAGIC ```python
# MAGIC # ❌ 나쁜 예: 실험 이름이 모호함
# MAGIC mlflow.set_experiment("my_experiment")  # 누구의? 무슨 실험?
# MAGIC
# MAGIC # ✅ 좋은 예: 사용자/프로젝트/날짜가 명확
# MAGIC mlflow.set_experiment(f"/Users/{current_user}/lgit_predictive_maintenance")
# MAGIC ```
# MAGIC
# MAGIC ### 팀원 간 실험 비교
# MAGIC
# MAGIC MLflow UI에서 여러 사람의 실험을 비교할 수 있습니다:
# MAGIC
# MAGIC ```python
# MAGIC import mlflow
# MAGIC
# MAGIC # Alice와 Bob의 실험 결과를 한꺼번에 검색
# MAGIC all_runs = mlflow.search_runs(
# MAGIC     experiment_names=[
# MAGIC         "/Users/alice@company.com/lgit_predictive_maintenance",
# MAGIC         "/Users/bob@company.com/lgit_predictive_maintenance",
# MAGIC     ],
# MAGIC     order_by=["metrics.val_f1_score DESC"],
# MAGIC     max_results=10,
# MAGIC )
# MAGIC display(all_runs[["run_id", "tags.mlflow.runName", "metrics.val_f1_score"]])
# MAGIC ```
# MAGIC
# MAGIC > **Databricks 장점:** MLflow 실험은 사용자 폴더별로 자동 분리되지만,
# MAGIC > `search_runs` API로 **팀 전체의 실험을 한 눈에 비교** 할 수 있습니다.
# MAGIC > "누가 가장 좋은 모델을 만들었는가"를 코드 한 줄로 확인할 수 있습니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 5. Git 연동 (Repos) — 코드 협업의 정석
# MAGIC
# MAGIC ### 왜 Git이 필요한가?
# MAGIC
# MAGIC | 문제 | Git 없이 | Git으로 |
# MAGIC |------|---------|--------|
# MAGIC | 코드 충돌 | "누가 내 코드 바꿨어?" | 브랜치별 독립 작업 + 머지 |
# MAGIC | 이력 추적 | 되돌리기 불가능 | `git log`로 모든 변경 이력 확인 |
# MAGIC | 코드 리뷰 | "그냥 Shared에 올렸어요" | PR → 리뷰 → 승인 → 머지 |
# MAGIC | 운영 배포 | 수동 복사 | CI/CD (Continuous Integration/Continuous Delivery) 자동 배포 |
# MAGIC
# MAGIC ### Databricks Repos 사용 흐름
# MAGIC
# MAGIC ```
# MAGIC 1. Repos에서 Git 저장소 연결
# MAGIC 2. 개인 브랜치 생성 (feature/alice-new-model)
# MAGIC 3. 노트북에서 코드 수정 + 커밋
# MAGIC 4. GitHub/GitLab에서 PR (Pull Request) 생성
# MAGIC 5. 팀원 리뷰 → 승인 → 머지
# MAGIC 6. main 브랜치 → Shared 폴더에 자동 배포 (CI/CD)
# MAGIC ```
# MAGIC
# MAGIC > **현장 경험담:** "Git 도입하면 느려진다"는 반론을 많이 받습니다. 하지만 Git 없이 운영하다 코드 사고가 나면
# MAGIC > 복구하는 데 며칠이 걸립니다. Git 도입 초기에 1~2시간 투자하면, 나중에 수십 시간을 절약합니다.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 6. 🚫 하지 말 것 → ✅ 대신 이렇게 하세요
# MAGIC
# MAGIC ### 사고를 유발하는 행동 TOP 5와 올바른 대안
# MAGIC
# MAGIC | # | 금기 사항 | 사고 사례 |
# MAGIC |---|----------|----------|
# MAGIC | 1 | **운영 테이블에 직접 DELETE/UPDATE** | `DELETE FROM prod_table WHERE 1=1` 실수 → 전체 삭제 |
# MAGIC | 2 | **Shared 노트북 직접 수정** | 동시 편집 → 코드 충돌 → 6시간 작업 소실 |
# MAGIC | 3 | **GPU 클러스터 공유** | 두 사람이 동시에 학습 → CUDA OOM → 둘 다 실패 |
# MAGIC | 4 | **API 키/비밀번호 코드에 직접 입력** | Git에 커밋되면 즉시 노출 |
# MAGIC | 5 | **다른 사람의 모델을 @Champion으로 변경** | 검증 안 된 모델이 운영에 배포 |

# COMMAND ----------

# MAGIC %md
# MAGIC ### ✅ 올바른 대안 — "그러면 어떻게 해야 하나요?"
# MAGIC
# MAGIC #### 1번 대안: 운영 테이블 수정이 필요할 때
# MAGIC
# MAGIC ```python
# MAGIC # ❌ 절대 금지: 운영 테이블에 직접 DELETE/UPDATE
# MAGIC spark.sql("DELETE FROM prod_schema.sensor_data WHERE date = '2026-03-01'")
# MAGIC
# MAGIC # ✅ 방법 1: 개발 스키마에서 먼저 테스트
# MAGIC # 1) 개발 환경에서 동일한 쿼리를 먼저 실행하여 영향 범위 확인
# MAGIC spark.sql("SELECT COUNT(*) FROM dev_schema.sensor_data WHERE date = '2026-03-01'")
# MAGIC # 2) 영향 행 수를 확인한 후, 코드 리뷰를 거쳐 운영에 적용
# MAGIC
# MAGIC # ✅ 방법 2: Delta Lake Time Travel로 안전망 확보
# MAGIC # 1) 변경 전에 현재 버전 번호를 기록해둡니다
# MAGIC spark.sql("DESCRIBE HISTORY prod_schema.sensor_data LIMIT 1")
# MAGIC # 2) DELETE/UPDATE 실행
# MAGIC # 3) 문제가 생기면 RESTORE로 즉시 복구 (30초면 끝)
# MAGIC # spark.sql("RESTORE TABLE prod_schema.sensor_data TO VERSION AS OF 42")
# MAGIC
# MAGIC # ✅ 방법 3: DELETE/UPDATE 전에 반드시 SELECT로 영향 범위 확인 (습관화!)
# MAGIC # WHERE 조건 실수가 대부분의 사고 원인이므로, 같은 WHERE절로 먼저 SELECT
# MAGIC spark.sql("SELECT COUNT(*) FROM prod_schema.sensor_data WHERE date = '2026-03-01'")
# MAGIC # → "3건이 삭제 대상" 확인 후 → 같은 WHERE절로 DELETE 실행
# MAGIC # → 만약 10만 건이 나왔다면? WHERE 조건이 잘못된 것 → DELETE 하지 않고 수정
# MAGIC ```
# MAGIC
# MAGIC #### 2번 대안: 팀 공유 코드를 수정해야 할 때
# MAGIC
# MAGIC ```
# MAGIC ❌ Shared 폴더의 노트북을 직접 열어서 수정
# MAGIC
# MAGIC ✅ Git 기반 워크플로우:
# MAGIC   1. Repos에서 개인 브랜치 생성 → feature/alice-fix-pipeline
# MAGIC   2. 개인 브랜치에서 코드 수정 + 테스트
# MAGIC   3. PR(Pull Request) 생성 → 팀원 코드 리뷰
# MAGIC   4. 승인 후 main 브랜치에 머지 → Shared에 자동 반영
# MAGIC
# MAGIC ✅ Git이 없는 경우 (임시 대안):
# MAGIC   1. 원본 노트북을 내 개인 폴더에 복사
# MAGIC   2. 복사본에서 수정 + 테스트
# MAGIC   3. 팀원에게 슬랙으로 공유 → 확인 후 원본에 반영
# MAGIC   4. 절대로 원본을 직접 수정하지 않기
# MAGIC ```
# MAGIC
# MAGIC #### 3번 대안: GPU가 필요한 학습을 해야 할 때
# MAGIC
# MAGIC ```python
# MAGIC # ❌ 다른 사람의 GPU 클러스터에서 학습 실행
# MAGIC
# MAGIC # ✅ 방법 1: 개인 GPU 클러스터 생성 (Auto Termination 10분)
# MAGIC # Compute → Create Cluster → GPU 인스턴스 선택 → Auto Termination = 10분
# MAGIC # 학습이 끝나면 10분 후 자동 종료 → 비용 최소화
# MAGIC
# MAGIC # ✅ 방법 2: Databricks Job으로 GPU 학습 제출 (권장)
# MAGIC # Job으로 제출하면 전용 클러스터가 자동 생성 → 학습 완료 → 자동 종료
# MAGIC # 브라우저를 닫아도 학습이 계속 진행됩니다
# MAGIC # Workflows → Create Job → 노트북 지정 → GPU 클러스터 설정
# MAGIC ```
# MAGIC
# MAGIC #### 4번 대안: API 키/비밀번호를 사용해야 할 때
# MAGIC
# MAGIC ```python
# MAGIC # ❌ 절대 금지: 코드에 직접 작성
# MAGIC api_key = "sk-abc123..."  # Git에 커밋되면 즉시 노출!
# MAGIC
# MAGIC # ✅ Databricks Secrets 사용 (권장)
# MAGIC # 1) 관리자가 Secret Scope를 생성 (1회)
# MAGIC #    databricks secrets create-scope lgit-secrets
# MAGIC # 2) Secret 저장 (1회)
# MAGIC #    databricks secrets put-secret lgit-secrets openai-api-key
# MAGIC # 3) 코드에서 안전하게 읽기 (display해도 [REDACTED]로 마스킹됨)
# MAGIC api_key = dbutils.secrets.get(scope="lgit-secrets", key="openai-api-key")
# MAGIC ```
# MAGIC
# MAGIC #### 5번 대안: 더 좋은 모델을 만들어서 Champion을 교체하고 싶을 때
# MAGIC
# MAGIC ```python
# MAGIC # ❌ 직접 Champion alias를 변경
# MAGIC # client.set_registered_model_alias(model_name, "champion", my_version)
# MAGIC
# MAGIC # ✅ Challenger 검증 프로세스를 거치세요
# MAGIC # 1) 새 모델을 @Challenger alias로 등록
# MAGIC client.set_registered_model_alias(model_name, "challenger", my_version)
# MAGIC
# MAGIC # 2) A/B 테스트 또는 동일 데이터셋으로 성능 비교
# MAGIC # champion_f1 = 0.87, challenger_f1 = 0.91
# MAGIC
# MAGIC # 3) 성능이 확인되면 팀 리뷰 후 Champion 교체
# MAGIC # → 04_challenger_validation 노트북 참조
# MAGIC
# MAGIC # 4) 교체 이력을 MLflow에 기록
# MAGIC # mlflow.log_param("promotion_reason", "F1 0.87→0.91, 팀 리뷰 완료")
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### 추가 주의사항과 올바른 대안
# MAGIC
# MAGIC | # | 주의 사항 | 올바른 방법 |
# MAGIC |---|----------|-----------|
# MAGIC | 6 | **클러스터를 끄지 않고 퇴근** | Auto Termination 반드시 설정 (10~20분) |
# MAGIC | 7 | **`DROP TABLE`을 운영 스키마에서 실행** | 개발 스키마에서만 DROP 허용. 운영은 권한으로 보호 |
# MAGIC | 8 | **대용량 데이터를 `collect()`로 Driver에 로드** | `display()` 또는 `limit()` 사용 |
# MAGIC | 9 | **클러스터 로그를 확인하지 않고 "안 돼요" 보고** | Spark UI, Driver Logs 먼저 확인 |
# MAGIC | 10 | **모델 버전 태그 없이 등록** | 반드시 성능 지표, 데이터 소스, 담당자 태그 추가 |

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 7. 실무 체크리스트
# MAGIC
# MAGIC ### 매일 개발 시작 전
# MAGIC
# MAGIC - [ ] 내 클러스터가 켜져 있는지 확인 (다른 사람 클러스터에 붙지 않았는지)
# MAGIC - [ ] 내 카탈로그/스키마에서 작업하고 있는지 확인
# MAGIC - [ ] Git 브랜치가 최신 상태인지 `git pull`
# MAGIC
# MAGIC ### 모델 등록/배포 전
# MAGIC
# MAGIC - [ ] MLflow에 실험 결과가 기록되어 있는지
# MAGIC - [ ] 메타데이터(태그)가 빠짐없이 달려 있는지
# MAGIC - [ ] Champion 교체 전 Challenger 검증을 완료했는지
# MAGIC - [ ] 팀원/관리자에게 공유했는지
# MAGIC
# MAGIC ### 퇴근 전
# MAGIC
# MAGIC - [ ] 클러스터 Auto Termination이 설정되어 있는지
# MAGIC - [ ] 임시 테이블/파일을 정리했는지
# MAGIC - [ ] 변경사항을 Git에 커밋했는지

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 요약
# MAGIC
# MAGIC | 원칙 | 실천 방법 |
# MAGIC |------|----------|
# MAGIC | **격리** | 카탈로그 분리, Single User 클러스터, 개인 실험 폴더 |
# MAGIC | **공유** | MLflow로 실험 비교, Shared 폴더는 읽기 위주, Git으로 코드 협업 |
# MAGIC | **보호** | Auto Termination, `dbutils.secrets`, Champion 변경 권한 제한 |
# MAGIC | **추적** | 모델 태그 필수, Git 이력, MLflow 자동 기록 |
# MAGIC
# MAGIC > **핵심 한 줄:** "내 실험은 내 공간에서, 운영 변경은 리뷰를 거쳐서."
# MAGIC >
# MAGIC > 다음 단계: [00_overview]($./00_overview) 에서 전체 PoC 아키텍처를 확인합니다.
