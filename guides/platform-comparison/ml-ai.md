# ML/AI 비교

## ML 플랫폼

| 항목 | Databricks | Snowflake | AWS (SageMaker/Bedrock) | GCP (Vertex AI) | MS Fabric |
|---|---|---|---|---|---|
| **ML 플랫폼**| Mosaic AI + MLflow (End-to-End 통합) | Snowpark ML + Cortex (후발) | SageMaker (독립 서비스) | Vertex AI (독립 서비스) | Synapse ML (제한적) |
| **실험 추적**| MLflow Tracking (업계 표준 OSS, 19K+ GitHub Stars) | 자체 도구 없음 | SageMaker Experiments | Vertex AI Experiments | MLflow 연동 가능 |
| **모델 레지스트리**| Unity Catalog Models (거버넌스 통합) | Snowflake Model Registry (초기) | SageMaker Model Registry | Vertex AI Model Registry | 제한적 |
| **Feature Store**| Unity Catalog Feature Store (온라인+오프라인 통합) | 미지원 | SageMaker Feature Store | Vertex AI Feature Store | 미지원 |
| **AutoML**| Databricks AutoML (Glass-box, 코드 생성) | 미지원 | SageMaker Autopilot | Vertex AI AutoML | 제한적 |
| **데이터-ML 거버넌스**| 학습 데이터→모델→서빙 전체 리니지 (유일) | 분리 (데이터/ML 별도) | 분리 (Lake Formation↔SageMaker) | 분리 (Dataplex↔Vertex AI) | 부분적 |

## GenAI / LLM / Agent

| 항목 | Databricks | Snowflake | AWS Bedrock | GCP Vertex AI | MS Fabric |
|---|---|---|---|---|---|
| **Foundation Model API**| 다양한 모델 (DBRX, Llama, Mixtral 등) — Pay-per-token | Cortex LLM Functions (제한된 모델) | Bedrock (다양한 모델) | Gemini + 다양한 모델 | Azure OpenAI 연동 |
| **모델 파인튜닝**| Foundation Model Fine-tuning (GUI + API) | 미지원 | Bedrock Custom Model | Vertex AI Tuning | Azure OpenAI Fine-tuning |
| **자체 모델 호스팅**| GPU Model Serving — 어떤 모델이든 호스팅 | Snowpark Container Services (초기) | SageMaker Endpoints | Vertex AI Endpoints | 제한적 |
| **벡터 검색**| Vector Search — Unity Catalog 통합, Delta Sync 자동 갱신 | Cortex Search | OpenSearch / Bedrock KB (별도) | Vertex AI Vector Search (별도) | Azure AI Search 연동 |
| **RAG 구축**| Vector Search + Delta Sync + ai_parse_document() | Cortex Search (제한적) | Bedrock Knowledge Base | Vertex AI RAG | Azure AI 연동 필요 |
| **Agent 프레임워크**| Mosaic AI Agent Framework (업계 최선두) | Cortex Analyst (SQL 전용) | Bedrock Agents | Vertex AI Agent Builder | Azure AI Agent Service |
| **Agent 평가**| Agent Evaluation — 자동 품질 측정 | 미지원 | 제한적 (수동) | 제한적 (수동) | 제한적 |
| **Agent 도구 연결**| Unity Catalog Functions as Tools (거버넌스 통합) | 제한적 | Lambda Functions | Cloud Functions | Azure Functions |

{% hint style="success" %}
**Databricks AI 핵심 차별화**: 데이터가 있는 곳에서 바로 ML 학습, 모델 서빙, GenAI Agent 구축, 평가까지 수행합니다. MLflow(업계 표준 OSS)로 전 과정을 추적하고, Agent Evaluation으로 체계적 품질 측정이 가능합니다. **데이터 복사나 서비스 전환 없이 End-to-End AI를 구현하는 유일한 플랫폼**입니다.
{% endhint %}

{% hint style="warning" %}
**경쟁사 장점**: AWS Bedrock은 가장 다양한 외부 LLM 모델(Anthropic Claude, Meta Llama, Cohere 등)을 지원합니다. GCP Vertex AI는 Gemini 모델과의 긴밀한 통합, 멀티모달 AI에서 강점이 있습니다. MS Fabric은 Azure OpenAI와 네이티브 연동되어 GPT-4 계열 모델을 쉽게 활용할 수 있습니다.
{% endhint %}
