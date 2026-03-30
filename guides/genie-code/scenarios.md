# Genie Code 활용 시나리오

## 시나리오 1: 데이터 사이언스 (Notebooks)

Genie Code는 전문 ML 엔지니어처럼 동작하여 전체 ML 워크플로를 자동화합니다.

**활용 예시:**

```
프롬프트: "@customers 테이블에 대해 고객 세그멘테이션 분석을 수행해줘.
         K-means 클러스터링을 사용하고 MLflow에 실험을 기록해줘."
```

Genie Code가 수행하는 작업:
1. 테이블 스키마 분석 및 EDA
2. 피처 엔지니어링
3. 최적 클러스터 수 결정 (Elbow method)
4. 모델 학습 및 MLflow 실험 로깅
5. 결과 시각화 및 인사이트 요약

## 시나리오 2: 데이터 엔지니어링 (Lakeflow Pipelines)

ETL 워크로드를 자동화하고 Lakeflow Spark Declarative Pipeline을 구축합니다.

**활용 예시:**

```
프롬프트: "raw_orders와 raw_customers 테이블을 조인하여
         daily_order_summary 테이블을 업데이트하는 파이프라인을 만들어줘."
```

## 시나리오 3: 분석 및 대시보드 (Dashboards)

데이터 자산을 탐색하고 프로덕션 수준 대시보드를 자동 생성합니다.

**활용 예시:**

```
프롬프트: "@sales_data를 분석하고 월별 매출 추이,
         지역별 성과, 상위 제품을 보여주는 대시보드를 만들어줘."
```

## 시나리오 4: GenAI 앱 디버깅 (MLflow)

GenAI 애플리케이션을 이해하고, 디버깅하며, 성능을 개선합니다.

**활용 예시:**

```
프롬프트: "이 RAG 체인의 evaluation 결과를 분석하고
         응답 품질이 낮은 케이스를 식별해줘."
```
