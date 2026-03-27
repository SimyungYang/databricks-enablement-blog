# 01. Overview — 전체 아키텍처 소개

**목적**: PoC 시나리오 정의 및 전체 파이프라인 아키텍처를 소개합니다.

**주요 개념**:
- **정형 데이터**: UCI AI4I 2020 Predictive Maintenance Dataset (10,000건) — XGBoost 기반 설비 고장 예측
- **비정형 데이터**: MVTec AD 산업용 이미지 — Anomalib PatchCore 기반 표면 이상탐지
- **운영 환경**: 주 1회 재학습 + 일 4회 배치 예측

{% hint style="info" %}
이 데모는 제조 현장의 예지보전(Predictive Maintenance)과 비전 기반 이상탐지를 하나의 MLOps 파이프라인으로 통합합니다. 정형/비정형 모델 모두 동일한 Unity Catalog 거버넌스 체계로 관리됩니다.
{% endhint %}
