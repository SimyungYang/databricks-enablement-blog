# ML/AI 비교

## ML 플랫폼

| 항목 | Databricks | Snowflake | AWS (SageMaker/Bedrock) | GCP (Vertex AI) | MS Fabric |
|---|---|---|---|---|---|
| **ML 플랫폼**| Mosaic AI + MLflow (End-to-End 통합) | Snowpark ML + Cortex (후발) | SageMaker (독립 서비스) | Vertex AI (독립 서비스) | Synapse ML (제한적) |
| ** 실험 추적**| MLflow Tracking (업계 표준 OSS, 19K+ GitHub Stars) | 자체 도구 없음 | SageMaker Experiments | Vertex AI Experiments | MLflow 연동 가능 |
| ** 모델 레지스트리**| Unity Catalog Models (거버넌스 통합) | Snowflake Model Registry (초기) | SageMaker Model Registry | Vertex AI Model Registry | 제한적 |
| **Feature Store**| Unity Catalog Feature Store (온라인+오프라인 통합) | 미지원 | SageMaker Feature Store | Vertex AI Feature Store | 미지원 |
| **AutoML**| Databricks AutoML (Glass-box, 코드 생성) | 미지원 | SageMaker Autopilot | Vertex AI AutoML | 제한적 |
| ** 데이터-ML 거버넌스**| 학습 데이터→모델→서빙 전체 리니지 (유일) | 분리 (데이터/ML 별도) | 분리 (Lake Formation↔SageMaker) | 분리 (Dataplex↔Vertex AI) | 부분적 |

## GenAI / LLM / Agent

| 항목 | Databricks | Snowflake | AWS Bedrock | GCP Vertex AI | MS Fabric |
|---|---|---|---|---|---|
| **Foundation Model API**| 다양한 모델 (DBRX, Llama, Mixtral 등) — Pay-per-token | Cortex LLM Functions (제한된 모델) | Bedrock (다양한 모델) | Gemini + 다양한 모델 | Azure OpenAI 연동 |
| ** 모델 파인튜닝**| Foundation Model Fine-tuning (GUI + API) | 미지원 | Bedrock Custom Model | Vertex AI Tuning | Azure OpenAI Fine-tuning |
| ** 자체 모델 호스팅**| GPU Model Serving — 어떤 모델이든 호스팅 | Snowpark Container Services (초기) | SageMaker Endpoints | Vertex AI Endpoints | 제한적 |
| ** 벡터 검색**| Vector Search — Unity Catalog 통합, Delta Sync 자동 갱신 | Cortex Search | OpenSearch / Bedrock KB (별도) | Vertex AI Vector Search (별도) | Azure AI Search 연동 |
| **RAG 구축**| Vector Search + Delta Sync + ai_parse_document() | Cortex Search (제한적) | Bedrock Knowledge Base | Vertex AI RAG | Azure AI 연동 필요 |
| **Agent 프레임워크**| Mosaic AI Agent Framework (업계 최선두) | Cortex Analyst (SQL 전용) | Bedrock Agents | Vertex AI Agent Builder | Azure AI Agent Service |
| **Agent 평가**| Agent Evaluation — 자동 품질 측정 | 미지원 | 제한적 (수동) | 제한적 (수동) | 제한적 |
| **Agent 도구 연결**| Unity Catalog Functions as Tools (거버넌스 통합) | 제한적 | Lambda Functions | Cloud Functions | Azure Functions |

{% hint style="success" %}
**Databricks AI 핵심 차별화**: 데이터가 있는 곳에서 바로 ML 학습, 모델 서빙, GenAI Agent 구축, 평가까지 수행합니다. MLflow(업계 표준 OSS)로 전 과정을 추적하고, Agent Evaluation으로 체계적 품질 측정이 가능합니다. ** 데이터 복사나 서비스 전환 없이 End-to-End AI를 구현하는 유일한 플랫폼** 입니다.
{% endhint %}

{% hint style="warning" %}
** 경쟁사 장점**: AWS Bedrock은 가장 다양한 외부 LLM 모델(Anthropic Claude, Meta Llama, Cohere 등)을 지원합니다. GCP Vertex AI는 Gemini 모델과의 긴밀한 통합, 멀티모달 AI에서 강점이 있습니다. MS Fabric은 Azure OpenAI와 네이티브 연동되어 GPT-4 계열 모델을 쉽게 활용할 수 있습니다.
{% endhint %}

---

## MLflow — 업계 표준 ML 라이프사이클 관리

### MLflow 상세 비교

**MLflow** 는 Databricks가 만든 오픈소스 ML 라이프사이클 관리 플랫폼으로, **19K+ GitHub Stars** 와 **1,600만+ 월간 다운로드** 를 기록하는 업계 표준입니다.

| MLflow 기능 | 설명 | SageMaker 대응 | Vertex AI 대응 |
|---|---|---|---|
| **MLflow Tracking**| 실험 파라미터, 메트릭, 아티팩트 자동 기록 | SageMaker Experiments | Vertex AI Experiments |
| **MLflow Models**| 모델 패키징 (다양한 프레임워크 지원) | SageMaker Model | Vertex AI Model |
| **MLflow Model Registry**| 모델 버전 관리, 스테이지 전환 (UC 통합) | SageMaker Model Registry | Vertex AI Model Registry |
| **MLflow Evaluate**| 모델 품질 자동 평가 (분류/회귀/LLM) | 수동 | 수동 |
| **MLflow Recipes**| ML 파이프라인 템플릿 | SageMaker Pipelines | Vertex AI Pipelines |
| **MLflow Deployments**| 모델 서빙 관리 | SageMaker Endpoints | Vertex AI Endpoints |
| ** 오픈소스**| ** 완전 오픈소스 (Apache 2.0)**| 비공개 | 비공개 |
| ** 벤더 종속**| **Zero**— 어디서든 MLflow 사용 가능 | AWS 종속 | GCP 종속 |

### MLflow와 Unity Catalog 통합의 가치

```
[데이터-ML 통합 거버넌스 — Databricks만 가능]

Unity Catalog
  ├─ 학습 데이터 (catalog.schema.training_data)
  │   └─ 접근 제어: GRANT SELECT ON TABLE ...
  │
  ├─ Feature Table (catalog.schema.features)
  │   └─ 온라인/오프라인 Feature Store 통합
  │
  ├─ ML 모델 (catalog.schema.model_name)
  │   ├─ 버전 관리 (v1, v2, ...)
  │   ├─ 스테이지 (Staging → Production)
  │   ├─ 리니지: 어떤 데이터로 학습했는지 자동 추적
  │   └─ 접근 제어: GRANT EXECUTE ON MODEL ...
  │
  └─ Serving Endpoint
      ├─ 모델 v2를 서빙 중
      ├─ 트래픽 분할 (A/B 테스트)
      └─ 사용 로그 → System Tables에 자동 기록
```

{% hint style="info" %}
** 경쟁사와의 핵심 차이**: SageMaker에서는 학습 데이터(S3) → 모델(SageMaker Registry) → 서빙(SageMaker Endpoint)이 ** 각각 다른 거버넌스** 를 가집니다. Lake Formation은 데이터만, SageMaker는 모델만 관리하며, 둘 사이의 리니지는 수동으로 추적해야 합니다.
{% endhint %}

---

## Feature Engineering 비교

### Feature Store 상세 비교

| 항목 | Databricks Feature Store | SageMaker Feature Store | Vertex AI Feature Store | Snowflake | Fabric |
|---|---|---|---|---|---|
| ** 오프라인 Store**| Unity Catalog 테이블 (Delta Lake) | S3 기반 | BigQuery/Bigtable | 미지원 | 미지원 |
| ** 온라인 Store**| DynamoDB / CosmosDB / Cloud Bigtable 자동 동기화 | DynamoDB | Bigtable | 미지원 | 미지원 |
| ** 온라인-오프라인 동기화**| 자동 (Serverless 파이프라인) | 수동/스케줄 | 수동/스케줄 | N/A | N/A |
| **Feature 거버넌스**| Unity Catalog 통합 (접근 제어, 리니지) | 별도 (IAM) | 별도 (IAM) | N/A | N/A |
| **Point-in-Time 조회**| 자동 (시간 기반 조인) | 수동 구현 | 자동 | N/A | N/A |
| **Feature 공유**| Catalog 간 공유 (Delta Sharing) | AWS 계정 내 | GCP 프로젝트 내 | N/A | N/A |
| **Feature 계산**| SQL 또는 Python으로 정의 | Python SDK | Python SDK | N/A | N/A |
| ** 모델 연결**| 모델이 어떤 Feature를 사용했는지 자동 추적 | 수동 | 수동 | N/A | N/A |

### Feature Engineering 워크플로

| 단계 | Databricks | AWS (SageMaker) | GCP (Vertex AI) |
|---|---|---|---|
| **Feature 정의**| SQL/Python으로 DLT에서 정의 | Python SDK | Python SDK |
| **Feature 저장**| Unity Catalog 테이블로 자동 등록 | Feature Store API로 저장 | Feature Store API로 저장 |
| ** 학습 데이터 생성**| `FeatureEngineeringClient.create_training_set()` | `FeatureGroup.create_dataset()` | `FeatureOnlineStoreService` |
| ** 온라인 서빙**| Model Serving에서 자동 Feature Lookup | SageMaker Endpoint + Feature Store | Vertex AI Endpoint + Feature Store |
| ** 모니터링**| Lakehouse Monitor로 Feature 드리프트 감지 | 수동 | 수동 |

{% hint style="success" %}
**Feature Store의 핵심 가치**: Databricks Feature Store는 **Unity Catalog에 통합** 되어 있으므로, Feature 테이블도 일반 테이블과 동일한 접근 제어, 리니지, 감사가 적용됩니다. SageMaker/Vertex AI의 Feature Store는 데이터 카탈로그와 ** 분리** 되어 있어, Feature에 대한 거버넌스가 별도로 필요합니다.
{% endhint %}

---

## Foundation Model APIs 상세

### 모델 제공 방식 비교

| 항목 | Databricks Foundation Model APIs | AWS Bedrock | GCP Vertex AI | Azure OpenAI |
|---|---|---|---|---|
| ** 제공 모델**| Llama 3.1, DBRX, Mixtral, Claude 등 | Claude, Llama, Cohere, Mistral 등 | Gemini, Claude, Llama 등 | GPT-4, GPT-3.5 |
| ** 과금 방식**| Pay-per-token | Pay-per-token | Pay-per-token / Character | Pay-per-token |
| ** 파인튜닝**| GUI + API (모든 지원 모델) | Bedrock Custom Models (일부) | Vertex AI Tuning (일부) | Fine-tuning (일부) |
| ** 자체 모델 호스팅**| GPU Model Serving (어떤 모델이든) | SageMaker Endpoints | Vertex AI Endpoints | Azure ML Endpoints |
| ** 프로비저닝**| Serverless (즉시) 또는 Provisioned Throughput | Serverless / Provisioned | Serverless / Dedicated | Provisioned |
| ** 데이터 프라이버시**| 데이터가 고객 VPC에 유지 | AWS 리전 내 | GCP 리전 내 | Azure 리전 내 |
| ** 거버넌스**| Unity Catalog로 엔드포인트 관리 | IAM | IAM | Azure AD |

### Databricks의 모델 호스팅 유연성

| 호스팅 옵션 | 설명 | 용도 |
|---|---|---|
| **Foundation Model APIs (Serverless)**| Databricks가 관리하는 모델 즉시 사용 | 빠른 프로토타이핑, 일반 AI 작업 |
| **Provisioned Throughput**| 전용 GPU 할당으로 안정적 처리량 보장 | 프로덕션 워크로드, SLA 필요 |
| **External Models**| 외부 API (OpenAI, Anthropic 등) 프록시 | 특정 모델 필요 시 |
| **Custom Model Serving**| 자체 학습 모델 GPU 서빙 | 커스텀 ML 모델, 파인튜닝 모델 |

---

## Agent Framework 심층 비교

### AI Agent 구축 프레임워크 비교

| 항목 | Databricks Agent Framework | AWS Bedrock Agents | GCP Vertex AI Agent Builder | Azure AI Agent Service |
|---|---|---|---|---|
| **Agent 정의**| Python 코드 (LangChain/LlamaIndex 호환) | Bedrock Console + API | Agent Builder Console + API | Azure AI Studio |
| ** 도구 연결**| Unity Catalog Functions as Tools (거버넌스 통합) | Lambda Functions | Cloud Functions | Azure Functions |
| ** 도구 거버넌스**| UC 접근 제어 자동 적용 | IAM (수동 설정) | IAM (수동 설정) | Azure AD (수동 설정) |
| ** 데이터 접근**| Unity Catalog 테이블 직접 접근 | S3/DynamoDB (설정 필요) | BigQuery/GCS (설정 필요) | Azure Storage (설정 필요) |
| ** 벡터 검색**| Vector Search (Delta Sync 자동 갱신) | Bedrock Knowledge Base | Vertex AI RAG | Azure AI Search |
| ** 평가**| **Agent Evaluation (자동 품질 측정)**| 수동 테스트 | 수동 테스트 | 수동 테스트 |
| ** 배포**| Model Serving Endpoint (원클릭) | Bedrock Agent 배포 | Agent Builder 배포 | Azure AI 배포 |
| ** 모니터링**| MLflow + System Tables (추적/비용) | CloudWatch | Cloud Monitoring | Azure Monitor |
| **MCP 지원**| Genie를 MCP Tool로 노출 | 미지원 | 미지원 | 미지원 |

### Agent Evaluation — Databricks만의 고유 기능

| 평가 항목 | 설명 | 경쟁사 |
|---|---|---|
| ** 정확성 (Correctness)**| Agent 응답이 정답과 일치하는지 자동 평가 | 수동 |
| ** 근거 (Groundedness)**| 응답이 검색된 문서에 근거하는지 검증 | 수동 |
| ** 관련성 (Relevance)**| 검색된 문서가 질문과 관련 있는지 평가 | 수동 |
| ** 안전성 (Safety)**| 유해/부적절한 응답 자동 탐지 | 수동 |
| ** 지연 시간 (Latency)**| 응답 시간 자동 측정 | CloudWatch 등 별도 |
| ** 비용 (Cost)**| 토큰 사용량 + 도구 호출 비용 자동 추적 | 수동 계산 |
| ** 자동 벤치마크**| 테스트 셋 기반 반복 평가 자동화 | 수동 스크립트 |

```python
# Agent Evaluation 코드 예시
import mlflow

results = mlflow.evaluate(
    model="models:/my-agent/production",
    data=eval_dataset,  # 질문 + 기대 답변
    model_type="databricks-agent",
    evaluators="default"  # 정확성, 근거, 관련성, 안전성 자동 평가
)

# 결과 확인
print(results.metrics)
# {'correctness': 0.85, 'groundedness': 0.92, 'relevance': 0.88, 'safety': 1.0}
```

{% hint style="success" %}
**Agent Evaluation은 프로덕션 AI Agent의 필수 요소** 입니다. Agent를 배포한 후에도 지속적으로 품질을 모니터링하고, 모델/프롬프트 변경 시 성능 저하를 조기 감지해야 합니다. 경쟁사에서는 이를 수동으로 구축해야 하며, Databricks는 **MLflow 한 줄로 자동화** 합니다.
{% endhint %}

---

## RAG (Retrieval-Augmented Generation) 구축 비교

### RAG 파이프라인 구성 요소

| 구성 요소 | Databricks | AWS | GCP | Snowflake |
|---|---|---|---|---|
| ** 문서 파싱**| `ai_parse_document()` (PDF, 이미지 등) | Textract | Document AI | 미지원 |
| ** 청킹**| 내장 유틸리티 + Python | 수동 | 수동 | 미지원 |
| ** 임베딩 생성**| Foundation Model APIs (내장) | Bedrock / Titan | Vertex AI Embeddings | Cortex Embed |
| ** 벡터 저장**| Vector Search (Unity Catalog 통합) | OpenSearch / Bedrock KB | Vertex AI Vector Search | Cortex Search |
| ** 자동 동기화**| **Delta Sync (소스 테이블 변경 시 자동 갱신)**| 수동/스케줄 | 수동/스케줄 | 수동 |
| ** 검색**| Vector Search API + 메타데이터 필터 | OpenSearch Query / Bedrock KB | Vector Search API | Cortex Search |
| ** 거버넌스**| UC 접근 제어 (벡터 인덱스도 관리) | IAM (서비스별 분리) | IAM (서비스별 분리) | Snowflake 접근 제어 |

### Databricks RAG의 핵심 차별점: Delta Sync

**Delta Sync** 는 Vector Search 인덱스를 소스 Delta 테이블과 ** 자동으로 동기화** 하는 기능입니다.

```
소스 Delta 테이블 (문서/텍스트)
  │
  │  [Delta Sync - 자동]
  │  ├─ 새 레코드 추가 → 자동 임베딩 + 인덱스 추가
  │  ├─ 레코드 업데이트 → 자동 재임베딩 + 인덱스 갱신
  │  └─ 레코드 삭제 → 자동 인덱스에서 제거
  │
  ▼
Vector Search 인덱스 (항상 최신 상태)
```

경쟁사에서는 문서가 추가/변경될 때마다 ** 수동으로 재임베딩 + 인덱스 갱신 파이프라인** 을 구축해야 합니다.

---

## AutoML 비교

### AutoML 접근 방식 차이

| 항목 | Databricks AutoML | SageMaker Autopilot | Vertex AI AutoML | BigQuery ML |
|---|---|---|---|---|
| ** 접근 방식**| **Glass-box**(생성된 코드를 완전 공개) | Black-box (모델만 반환) | Black-box | SQL 기반 |
| ** 코드 생성**| 완전한 노트북 코드 생성 (수정/학습 가능) | 미지원 | 미지원 | SQL 코드 |
| ** 지원 유형**| 분류, 회귀, 예측, 텍스트 분류 | 분류, 회귀 | 분류, 회귀, 이미지, 텍스트, 비디오 | 분류, 회귀, 시계열 |
| **Feature Engineering**| 자동 (코드로 투명하게 공개) | 자동 (비공개) | 자동 (비공개) | 제한적 |
| ** 하이퍼파라미터 튜닝**| 자동 (Optuna/Hyperopt 기반, 코드 공개) | 자동 | 자동 | 자동 |
| ** 모델 설명**| SHAP 값 자동 생성 | SHAP 지원 | Feature Importance | 제한적 |
| **MLflow 통합**| 자동 (모든 실험 자동 기록) | SageMaker Experiments | Vertex AI Experiments | 미지원 |

{% hint style="info" %}
**Glass-box AutoML의 가치**: Databricks AutoML은 모델뿐 아니라 ** 전체 코드를 생성** 합니다. 데이터 사이언티스트는 이 코드를 기반으로 커스터마이징할 수 있으며, 블랙박스 모델에 대한 우려 없이 ** 모든 과정이 투명** 합니다. 규제 산업(금융, 의료)에서는 이 투명성이 필수 요구사항입니다.
{% endhint %}

---

## 모델 서빙 비교

### 모델 서빙 아키텍처

| 항목 | Databricks Model Serving | SageMaker Endpoints | Vertex AI Endpoints | Snowflake Container Services |
|---|---|---|---|---|
| ** 서빙 유형**| 실시간 + 배치 | 실시간 + 배치 + 비동기 | 실시간 + 배치 | 실시간 (제한적) |
| **GPU 서빙**| 네이티브 (다양한 GPU) | 네이티브 (다양한 GPU) | 네이티브 (GPU + TPU) | 제한적 |
| ** 자동 스케일링**| 트래픽 기반 자동 (Scale to Zero 지원) | 트래픽 기반 자동 | 트래픽 기반 자동 | Warehouse 기반 |
| **Scale to Zero**| ** 지원 (유휴 비용 Zero)**| 지원 (웜업 시간 분 단위) | 지원 (웜업 시간) | N/A |
| **A/B 테스트**| 트래픽 분할 내장 | 트래픽 분할 지원 | 트래픽 분할 지원 | 미지원 |
| **Feature Lookup**| Serving 시 자동 Feature Store 조회 | 수동 구현 | 수동 구현 | 미지원 |
| ** 모니터링**| MLflow + System Tables | CloudWatch | Cloud Monitoring | 제한적 |
| ** 거버넌스**| Unity Catalog (엔드포인트도 관리) | IAM | IAM | Snowflake 접근 제어 |

### 엔드포인트 유형별 비교 (Databricks)

| 엔드포인트 유형 | 용도 | 비용 | 특징 |
|---|---|---|---|
| **Foundation Model API**| LLM 호출 (Llama, DBRX 등) | Pay-per-token | 즉시 사용, 관리 불필요 |
| **Provisioned Throughput**| 프로덕션 LLM (안정적 처리량) | 시간당 고정 | SLA 보장, 전용 GPU |
| **Custom Model Serving (CPU)**| 경량 ML 모델 | DBU/초 | Scale to Zero |
| **Custom Model Serving (GPU)**| 대규모 ML/DL 모델 | GPU DBU/초 | 높은 처리량 |
| **External Model**| 외부 API 프록시 (OpenAI 등) | 사용량 기반 | 통합 관리/모니터링 |

{% hint style="success" %}
**SA/SE 핵심 메시지**: Databricks Model Serving은 ** 데이터가 있는 곳에서 바로 모델을 서빙** 합니다. Feature Store 자동 조회, Unity Catalog 거버넌스, System Tables 모니터링이 통합되어 있어, SageMaker Endpoint처럼 데이터를 복사하거나 별도 거버넌스를 구축할 필요가 없습니다.
{% endhint %}
