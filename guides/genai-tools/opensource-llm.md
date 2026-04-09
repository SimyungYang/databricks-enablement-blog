# 오픈소스 LLM 생태계

## 왜 오픈소스 LLM인가

상용 LLM API(OpenAI, Anthropic 등)는 강력하지만 **세 가지 근본적인 제약** 이 있습니다.

1. **데이터 주권(Data Sovereignty)**: API 호출 시 데이터가 외부 서버로 전송됩니다. 금융, 의료, 정부 등 규제 산업에서는 이것만으로도 사용이 불가능할 수 있습니다.
2. **비용 예측 불가**: 토큰 기반 종량제는 사용량 증가 시 비용이 기하급수적으로 증가합니다. 대량 배치 처리나 높은 트래픽에서 월 수만 달러의 API 비용이 발생할 수 있습니다.
3. **커스터마이징 한계**: 상용 모델은 파인튜닝이 제한적이거나 불가능합니다. 특정 도메인(법률, 의학, 제조)에 최적화된 모델이 필요한 경우 오픈소스가 유일한 선택입니다.

오픈소스 LLM 생태계는 이 세 가지 제약을 해결합니다. 모델을 자체 인프라에서 실행하면 데이터가 외부로 나가지 않고, GPU 비용만으로 무제한 추론이 가능하며, 모델을 자유롭게 파인튜닝할 수 있습니다.

---

## 실행 & 서빙 도구

오픈소스 모델을 실제로 사용하려면 **"모델을 로드하고 실행하는 도구"** 가 필요합니다. 이 도구들은 크게 **로컬 실행용** 과 **프로덕션 서빙용** 으로 나뉩니다.

### 주요 도구 비교

아래 테이블은 오픈소스 LLM을 실행하고 서빙하는 주요 도구를 비교합니다.

| 도구 | 유형 | 핵심 특징 | 대상 사용자 | GPU 필요 |
|------|------|----------|-----------|---------|
| **Ollama** | 로컬 실행 | 원클릭 설치, `ollama run llama3` 한 줄로 실행 | 개인/개발자 | CPU 가능 (GPU 권장) |
| **LM Studio** | 로컬 실행 (GUI) | 데스크톱 앱, 모델 다운로드/실행/채팅 GUI | 비개발자/입문자 | CPU 가능 (GPU 권장) |
| **vLLM** | 프로덕션 서빙 | PagedAttention, 최고 처리량, OpenAI 호환 API | 인프라 엔지니어 | GPU 필수 |
| **Hugging Face TGI** | 프로덕션 서빙 | HF 생태계 통합, 간편한 배포, 텐서 병렬화 | ML 엔지니어 | GPU 필수 |
| **llama.cpp** | 로컬 실행 (C++) | CPU 최적화, 양자화 모델 실행, 경량 | 개발자/임베디드 | CPU 가능 |

이 비교에서 핵심 선택 기준은 **"어디서, 어떤 규모로 실행할 것인가"** 입니다. 개인 PC에서 실험하는 경우 Ollama나 LM Studio가 적합하고, 팀이나 서비스에서 사용하는 경우 vLLM이나 TGI가 필요합니다.

### Ollama 상세

Ollama는 **"Docker for LLMs"** 에 비유되는 도구입니다. 복잡한 환경 설정 없이 한 줄 명령어로 오픈소스 LLM을 로컬에서 실행할 수 있습니다.

**동작 원리:**
1. `ollama pull llama3.2` — 모델 다운로드 (양자화된 GGUF 포맷)
2. `ollama run llama3.2` — 모델 로드 + 대화형 인터페이스 시작
3. 내부적으로 llama.cpp 기반 추론 엔진 사용
4. `http://localhost:11434` 에서 OpenAI 호환 API 제공

**GGUF 포맷과 양자화(Quantization):**

Ollama가 사용하는 **GGUF(GPT-Generated Unified Format)** 는 llama.cpp 프로젝트에서 정의한 모델 저장 포맷입니다. 이 포맷의 핵심은 **양자화** 를 네이티브로 지원한다는 것입니다.

양자화란 모델의 가중치(weight)를 원래의 32비트/16비트 부동소수점에서 **4비트, 5비트, 8비트 등 더 낮은 정밀도** 로 변환하는 기법입니다. 예를 들어, 7B 모델의 원본 크기는 약 14GB(FP16)이지만, 4비트 양자화(Q4_K_M)를 적용하면 약 4.1GB로 줄어듭니다. 이로 인해 **일반 노트북(16GB RAM)에서도 7B 모델을 실행** 할 수 있습니다.

양자화의 트레이드오프는 정밀도 손실입니다. 일반적으로 Q4(4비트)에서 원본 대비 2~5%의 성능 하락이 발생하고, Q5(5비트)에서는 1~3% 수준입니다. 대부분의 실용적 사용에서 이 차이는 체감하기 어렵지만, 수학이나 코딩 같은 정밀한 작업에서는 영향이 커질 수 있습니다.

**핵심 강점:**
- **설치 간편**: macOS, Linux, Windows 모두 원클릭 설치. Apple Silicon Mac에서 Metal API를 통한 GPU 가속 자동 적용
- **모델 라이브러리**: `ollama.com/library`에서 수백 개 모델 즉시 다운로드. 양자화 수준별 변형(Q4, Q5, Q8)을 태그로 선택
- **Modelfile**: Dockerfile처럼 커스텀 모델 구성 파일 작성. 시스템 프롬프트, 파라미터(temperature, top_p), 모델 어댑터(LoRA) 등을 정의
- **OpenAI 호환 API**: 기존 OpenAI SDK 코드를 `base_url`만 변경하여 로컬 모델로 전환. AI 코딩 어시스턴트(Continue, Cursor 등)의 로컬 모델 백엔드로 활용 가능

```bash
# Ollama 기본 사용법
ollama pull llama3.2        # 모델 다운로드
ollama run llama3.2         # 대화형 실행
ollama serve                # API 서버 모드

# Python에서 OpenAI SDK로 로컬 모델 호출
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
response = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "PySpark 윈도우 함수 예시"}]
)
```

**한계:**
- 프로덕션 서빙에는 부적합 (동시 요청 처리, 모니터링 부족)
- 대형 모델(70B+)은 고사양 하드웨어 필요
- 파인튜닝 기능 없음 (추론 전용)

### vLLM 상세

vLLM은 UC Berkeley에서 개발한 **고성능 LLM 서빙 엔진** 입니다. **PagedAttention** 이라는 혁신적 메모리 관리 기법으로 기존 대비 2~4배 높은 처리량을 달성합니다.

**PagedAttention — 왜 혁신인가:**

LLM 서빙의 핵심 병목은 **KV Cache(Key-Value Cache)** 관리입니다. LLM은 이전에 생성한 모든 토큰의 정보를 KV Cache에 저장하고, 다음 토큰을 생성할 때 이를 참조합니다. 문제는 전통적 방식에서 각 요청에 대해 **최대 출력 길이만큼 메모리를 미리 할당** 해야 한다는 것입니다. 예를 들어, 최대 2048 토큰 출력을 허용하면 실제로 100토큰만 생성하더라도 2048토큰 분량의 메모리가 점유됩니다. 연구에 따르면 이로 인해 **60~80%의 GPU 메모리가 낭비** 됩니다.

PagedAttention은 운영체제의 **가상 메모리 페이징(Virtual Memory Paging)** 기법을 KV Cache에 적용한 것입니다. 구체적으로:

1. KV Cache를 고정 크기의 **블록(Page)** 으로 분할 (기본 16토큰 단위)
2. 토큰이 생성될 때마다 필요한 블록만 **동적으로 할당**
3. 요청이 끝나면 블록을 즉시 **반환하여 재활용**
4. 블록이 물리적으로 비연속적이어도 **논리적 테이블로 매핑** (OS의 페이지 테이블과 동일 원리)

이 접근 방식으로 메모리 낭비가 4% 미만으로 감소하고, 같은 GPU에서 **2~4배 많은 동시 요청** 을 처리할 수 있습니다. 추가로 **Prefix Caching** (공통 시스템 프롬프트의 KV Cache를 요청 간 공유)도 지원하여, 동일 프롬프트를 반복 사용하는 시나리오에서 추가 속도 향상을 제공합니다.

**Continuous Batching — 처리량 극대화:**

전통적 배칭은 배치 내 가장 긴 요청이 끝날 때까지 모든 요청이 대기해야 합니다. vLLM의 **Continuous Batching** 은 개별 요청이 완료되는 즉시 새 요청을 배치에 추가합니다. 이는 GPU 유휴 시간을 최소화하여 처리량을 추가로 30~50% 향상시킵니다.

**핵심 강점:**
- **최고 처리량**: PagedAttention + Continuous Batching으로 업계 최고 수준. 동일 GPU에서 HuggingFace TGI 대비 2~3배 높은 throughput
- **OpenAI 호환 API**: `python -m vllm.entrypoints.openai.api_server` 한 줄로 OpenAI 호환 서버 시작. 기존 코드 변경 없이 전환
- **텐서 병렬화(Tensor Parallelism)**: 여러 GPU에 모델의 각 레이어를 분산하여 대형 모델(70B+) 서빙
- **양자화 지원**: AWQ, GPTQ, FP8, BitsAndBytes 등 다양한 양자화 포맷으로 GPU 메모리 요구량 감소

**한계:**
- GPU 서버 운영 전문 지식 필요. CUDA 버전, 드라이버, PyTorch 호환성 관리가 복잡
- 모델 로딩 시간이 수 분 걸릴 수 있음 (콜드 스타트). 프로덕션에서는 모델을 미리 로드하는 warm pool 전략 필요
- 설정 최적화(배치 크기, 최대 시퀀스 길이, GPU 메모리 비율 등)에 경험이 필요하며, 잘못된 설정은 OOM(Out of Memory) 에러로 이어짐

### Hugging Face 생태계

Hugging Face는 오픈소스 AI의 **GitHub** 과 같은 플랫폼입니다.

**주요 구성 요소:**
- **Hub**: 80만+ 모델, 15만+ 데이터셋 호스팅. 모델 카드로 성능/한계 문서화
- **Transformers**: 가장 널리 사용되는 ML 라이브러리. `from_pretrained()`로 어떤 모델이든 로드
- **TGI (Text Generation Inference)**: 프로덕션 서빙 엔진. vLLM의 대안
- **Spaces**: 데모 앱 호스팅 (Gradio, Streamlit 기반)
- **PEFT**: LoRA 등 효율적 파인튜닝 라이브러리

### LM Studio 상세

LM Studio는 **GUI 기반 로컬 LLM 도구** 입니다. Ollama의 GUI 버전이라고 생각할 수 있습니다.

**핵심 강점:**
- **데스크톱 앱**: macOS, Windows, Linux에서 설치 후 바로 사용
- **모델 탐색**: Hugging Face에서 호환 모델을 검색/다운로드
- **채팅 UI**: ChatGPT와 유사한 인터페이스에서 로컬 모델과 대화
- **로컬 서버**: OpenAI 호환 API를 로컬에서 제공

**한계:**
- CLI/자동화에는 Ollama가 더 적합
- 기업 환경 배포에는 부적합

---

## 주요 오픈소스 모델 비교

아래 테이블은 2025년 4월 기준 주요 오픈소스 LLM 모델을 비교합니다.

| 모델 | 개발사 | 파라미터 | 컨텍스트 | 라이선스 | 핵심 강점 |
|------|--------|---------|---------|---------|----------|
| **Llama 4 Maverick** | Meta | 400B (MoE, 활성 17B) | 1M | Llama 라이선스 | MoE로 효율적, 128개 전문가 |
| **Llama 4 Scout** | 10M | 109B (MoE) | 10M | Llama 라이선스 | 최장 컨텍스트 (10M 토큰) |
| **Mistral Large** | Mistral | 123B | 128K | Apache 2.0 | 다국어, Function Calling |
| **Qwen 2.5** | Alibaba | 0.5B~72B | 128K | Apache 2.0 | 다양한 크기, 코딩 강점 |
| **Gemma 2** | Google | 2B / 9B / 27B | 8K | Gemma 라이선스 | Google 최적화, 경량 |
| **DeepSeek V3** | DeepSeek | 671B (MoE) | 128K | MIT | GPT-4급 성능, MoE 효율 |
| **DeepSeek R1** | DeepSeek | 671B (MoE) | 128K | MIT | 추론 특화, CoT 학습 |
| **Phi-4** | Microsoft | 14B | 16K | MIT | 소형 모델 최고 성능 |
| **DBRX** | Databricks | 132B (MoE) | 32K | Databricks Open | Databricks 최적화, MoE |

이 비교에서 가장 중요한 트렌드는 **MoE(Mixture of Experts) 아키텍처의 보편화** 입니다. Llama 4, DeepSeek V3, DBRX 모두 MoE를 사용합니다. MoE는 전체 파라미터 중 일부 전문가만 활성화하여 추론하므로, 대형 모델의 성능을 소형 모델의 비용으로 달성할 수 있습니다.

{% hint style="info" %}
모델 선택 시 파라미터 수만 보지 말고 **활성 파라미터 수** 를 확인하세요. Llama 4 Maverick은 400B 모델이지만 활성 파라미터는 17B로, 실제 추론 비용은 17B 모델과 유사합니다.
{% endhint %}

---

## Databricks에서 오픈소스 LLM 활용

Databricks는 오픈소스 LLM을 **엔터프라이즈 수준** 으로 배포하고 관리하는 기능을 제공합니다.

### Model Serving으로 배포

Databricks Model Serving은 내부적으로 vLLM 기반의 최적화된 서빙 인프라를 제공합니다.

**배포 방법:**
1. **Foundation Model APIs**: Databricks가 사전 배포한 오픈소스 모델(Llama, Mistral, DBRX 등) 즉시 사용
2. **Provisioned Throughput**: 전용 GPU에 모델을 배포하여 일관된 성능 보장
3. **커스텀 모델 배포**: 파인튜닝한 모델을 MLflow로 패키징하여 배포

```python
import mlflow

# 파인튜닝된 모델을 MLflow에 로깅
with mlflow.start_run():
    mlflow.transformers.log_model(
        transformers_model=fine_tuned_model,
        artifact_path="model",
        registered_model_name="my-custom-llama"
    )

# Unity Catalog에 등록된 모델을 Model Serving으로 배포
# Databricks UI 또는 API로 서빙 엔드포인트 생성
```

### 파인튜닝

Databricks에서 오픈소스 모델을 파인튜닝하는 방법은 두 가지입니다.

**1. Mosaic AI Fine-tuning:**
- UI에서 몇 번의 클릭으로 파인튜닝 실행
- 학습 데이터를 Delta 테이블에서 직접 로드
- LoRA/QLoRA 기반 효율적 파인튜닝

**2. 커스텀 학습 코드:**
- Databricks 클러스터에서 직접 학습 코드 실행
- Hugging Face Transformers + PEFT 라이브러리 활용
- MLflow로 실험 추적 및 모델 관리

### 거버넌스

Unity Catalog를 통해 모델의 전체 라이프사이클을 관리합니다.

- **모델 레지스트리**: 모델 버전 관리, 스테이징/프로덕션 승격
- **접근 제어**: 누가 어떤 모델을 사용할 수 있는지 세밀한 권한 관리
- **리니지 추적**: 모델이 어떤 데이터로 학습되었는지, 어디서 사용되는지 추적
- **Inference Table**: 모든 추론 요청/응답을 자동 로깅하여 모니터링과 디버깅에 활용

{% hint style="warning" %}
오픈소스 모델의 **라이선스** 를 반드시 확인하세요. Llama 4는 Meta의 커뮤니티 라이선스로 상업적 사용은 허용되지만 월 7억 활성 사용자 이상일 경우 별도 라이선스가 필요합니다. Apache 2.0(Mistral, Qwen)은 제한 없이 사용 가능합니다. MIT(DeepSeek, Phi)도 마찬가지입니다.
{% endhint %}

---

## 로컬 vs 클라우드 실행 선택 가이드

아래 테이블은 오픈소스 LLM을 어디서 실행할지 결정하는 데 도움을 줍니다.

| 기준 | 로컬 (Ollama/LM Studio) | Databricks Model Serving | 자체 GPU 서버 (vLLM) |
|------|------------------------|-------------------------|---------------------|
| **설정 난이도** | 매우 쉬움 | 쉬움 (UI/API) | 어려움 |
| **비용** | 무료 (기존 PC) | 종량제/고정 | GPU 서버 비용 |
| **확장성** | 1명 사용 | 오토스케일링 | 수동 스케일링 |
| **거버넌스** | 없음 | Unity Catalog 통합 | 직접 구축 |
| **모델 크기** | ~13B (일반 PC) | 제한 없음 | GPU에 따라 |
| **적합 용도** | 개인 실험, 프로토타이핑 | 프로덕션 서비스 | 대규모 자체 운영 |

이 표의 핵심 메시지는 **"규모와 거버넌스 요구사항에 따라 선택"** 입니다. 개인 실험에는 Ollama, 팀/프로덕션에는 Databricks, 대규모 자체 운영에는 vLLM이 최적입니다.

### 자체 vLLM 서빙 vs Databricks Model Serving: 언제 무엇이 유리한가

이 질문은 오픈소스 LLM 도입 시 가장 자주 논의되는 의사결정입니다.

**Databricks Model Serving이 유리한 경우:**
- **GPU 인프라 전문 인력이 없는 팀**: Databricks가 GPU 프로비저닝, 스케일링, 장애 대응을 모두 처리
- **거버넌스가 핵심 요구사항**: Unity Catalog 통합으로 모델 접근 제어, 추론 로그 자동 저장, 리니지 추적이 기본 제공
- **가변적 트래픽**: 오토스케일링으로 트래픽에 따라 GPU를 자동 조정. 야간에는 0으로 축소하여 비용 절감
- **빠른 시작**: Provisioned Throughput 엔드포인트를 수 분 내에 생성하여 즉시 서빙 시작

**자체 vLLM 서빙이 유리한 경우:**
- **GPU 비용 최적화가 최우선**: 예약 인스턴스(Reserved Instance)나 스팟 인스턴스를 직접 관리하면 Databricks 대비 30~50% 비용 절감 가능
- **극도로 높은 커스터마이징 필요**: vLLM의 모든 파라미터를 직접 튜닝, 커스텀 sampling 전략 적용, 특수한 모델 아키텍처 지원
- **멀티 클라우드/온프레미스**: AWS, GCP, Azure, 온프레미스 GPU 서버 등 어디서든 동일한 방식으로 배포
- **이미 Kubernetes 전문 팀이 있는 경우**: vLLM + KServe/Triton 조합으로 대규모 서빙 인프라 구축 가능

{% hint style="info" %}
실무에서 가장 흔한 패턴은 **"개발/실험은 Databricks, 대규모 프로덕션은 자체 vLLM"** 입니다. Databricks에서 모델 파인튜닝과 평가를 수행하고, 검증된 모델을 MLflow로 패키징하여 자체 vLLM 클러스터에 배포하는 하이브리드 접근입니다.
{% endhint %}
