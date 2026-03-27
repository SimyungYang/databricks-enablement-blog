# 10. Job 스케줄링 (Databricks Workflows)

**목적**: 운영/개발 환경별 MLOps 파이프라인을 Databricks Workflows로 스케줄링합니다.

**주요 개념**:
- Multi-task Jobs: 여러 노트북을 DAG로 연결
- 환경별 분리: 운영(주 1회 재학습, 일 4회 추론) / 개발(일 4회 재학습)

**운영 워크플로우 구조**:

```
[주 1회 재학습]
 02_Feature_Eng → 03_Model_Train → 04_Model_Reg → 05_Validation

[일 4회 배치 예측]
 06_Batch_Infer → 08_Monitoring
```

**스케줄 요약**:

| Job | 환경 | Cron (KST) | 설명 |
|-----|------|------------|------|
| Prod Weekly Retraining | 운영 | `0 2 * * 1` | 매주 월 02:00 재학습 |
| Prod Batch Inference | 운영 | `0 0,6,12,18 * * *` | 일 4회 배치 예측 |
| Dev Daily Retraining | 개발 | `0 0,6,12,18 * * *` | 일 4회 실험 재학습 |

**사용 Databricks 기능**: Databricks Workflows, Serverless Compute, 이메일/Slack 알림
