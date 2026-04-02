# 멀티모달 AI (Multimodal)

[< LLM 기초 목차로 돌아가기](README.md)

---

텍스트만 처리하던 LLM이 **이미지, 오디오, 비디오** 까지 이해하고 생성하는 시대입니다. 멀티모달 AI는 실세계 데이터를 그대로 다룰 수 있는 차세대 AI의 핵심 역량입니다.

{% hint style="info" %}
**학습 목표**
- 멀티모달 AI의 개념과 현재 수준을 이해한다
- Vision-Language 모델의 작동 원리와 활용 사례를 파악한다
- 제조/품질/의료 등 업종별 멀티모달 적용 가능성을 판단할 수 있다
{% endhint %}

---

## 1. 멀티모달 AI란?

**Multimodal AI** 는 텍스트뿐 아니라 이미지, 오디오, 비디오 등 **여러 형태(modality)의 데이터** 를 동시에 이해하고 생성할 수 있는 AI를 말합니다.

### 왜 중요한가?

실세계 데이터의 **80% 이상은 비정형** 입니다. 공장의 제품 사진, 콜센터의 음성 녹음, CCTV 영상, 스캔된 계약서 등 기업이 다루는 데이터 대부분은 텍스트가 아닙니다. 텍스트만 처리하는 LLM으로는 이런 데이터를 활용할 수 없었습니다.

멀티모달 AI는 이 한계를 돌파합니다. 이미지를 보고 설명하고, 음성을 듣고 답변하며, 문서를 읽고 요약합니다.

{% hint style="info" %}
**비유**: 기존 LLM이 "눈과 귀가 없는 천재"였다면, 멀티모달 AI는 **"눈과 귀가 달린 LLM" **입니다. 텍스트라는 하나의 감각만 가졌던 모델이, 이제 시각과 청각까지 갖추게 된 것입니다.
{% endhint %}

### 멀티모달의 범위

| 모달리티 | 입력 예시 | 출력 예시 |
|----------|----------|----------|
| **텍스트** | 질문, 지시, 문서 | 답변, 요약, 코드 |
| **이미지** | 사진, 차트, 스크린샷, 의료 영상 | 이미지 설명, 이미지 생성 |
| **오디오** | 음성 녹음, 음악, 환경음 | 텍스트 변환, 음성 합성 |
| **비디오** | 영상 클립, CCTV, 화상회의 녹화 | 요약, 이벤트 탐지 |
| **문서** | PDF, 스캔 이미지, 표 | 구조화된 데이터 추출 |

---

## 2. 현재 멀티모달 모델 비교

2025~2026년 기준, 주요 멀티모달 모델의 역량을 비교합니다.

| 모델 | 입력 | 출력 | 핵심 기능 |
|------|------|------|----------|
| **GPT-4o** | 텍스트+이미지+오디오 | 텍스트+오디오 | 실시간 음성 대화, 이미지 분석, 네이티브 멀티모달 |
| **GPT-4.1** | 텍스트+이미지 | 텍스트 | 코딩/Agent 최적화, 긴 컨텍스트(1M) |
| **Claude 4 Opus/Sonnet** | 텍스트+이미지+PDF | 텍스트 | 문서 분석, 차트 해석, 코드 생성 |
| **Gemini 2.5 Pro** | 텍스트+이미지+비디오+오디오 | 텍스트 | 가장 넓은 멀티모달, 1M 컨텍스트 |
| **Llama 4 Scout/Maverick** | 텍스트+이미지+비디오 | 텍스트 | 오픈소스 멀티모달, 10M 컨텍스트(Scout) |

{% hint style="warning" %}
**주의**: 멀티모달 역량은 모델 버전에 따라 빠르게 변합니다. 위 표는 2026년 3월 기준이며, 최신 정보는 각 공급사 문서를 확인하세요.
{% endhint %}

### 모델 선택 가이드

- **범용 멀티모달 (이미지+오디오+비디오)**: Gemini 2.5 Pro가 가장 넓은 범위
- **문서 분석 (PDF, 차트, 표)**: Claude 4 Opus/Sonnet이 강점
- **실시간 음성 대화**: GPT-4o가 네이티브 지원
- **오픈소스/온프레미스 필요**: Llama 4 시리즈
- **코딩/Agent 작업 + 이미지 이해**: GPT-4.1

---

## 3. 작동 원리 (직관적 설명)

멀티모달 모델이 이미지를 이해하는 과정을 직관적으로 설명합니다. 핵심은 **"이미지를 텍스트와 같은 토큰 시퀀스로 변환한다" **는 것입니다.

### 3단계 처리 과정

**Step 1. Vision Encoder**--- 이미지를 토큰으로 변환

이미지를 작은 패치(patch)로 나누고, 각 패치를 벡터(숫자 배열)로 변환합니다. 대표적으로 **ViT (Vision Transformer)** 가 사용됩니다.

- 예: 224x224 이미지 → 16x16 패치 196개 → 196개의 이미지 토큰

**Step 2. Projection Layer**--- 이미지 토큰을 텍스트 공간으로 매핑

Vision Encoder가 만든 이미지 토큰은 텍스트 토큰과 **차원(dimension)** 이 다릅니다. 프로젝션 레이어(Linear Layer 또는 MLP)가 이미지 토큰을 텍스트 토큰과 동일한 임베딩 공간으로 변환합니다.

**Step 3. LLM 통합 처리**--- 텍스트+이미지 토큰을 함께 추론

변환된 이미지 토큰이 텍스트 토큰과 **하나의 시퀀스** 로 결합되어 LLM에 입력됩니다. LLM은 Self-Attention을 통해 텍스트와 이미지 정보를 함께 처리하여 답변을 생성합니다.

### 처리 흐름

| 단계 | 입력 | 처리 | 출력 |
|------|------|------|------|
| 1. Vision Encoder | 원본 이미지 | 패치 분할 + ViT | 이미지 토큰 (예: 196개) |
| 2. Projection | 이미지 토큰 | 차원 매핑 (Linear/MLP) | 텍스트 공간의 이미지 토큰 |
| 3. LLM | [이미지 토큰] + [텍스트 토큰] | Self-Attention | 텍스트 답변 |

{% hint style="info" %}
**비유**: 이미지를 "외국어"라고 생각하세요. Vision Encoder는 **번역기** 입니다. 이미지라는 외국어를 LLM이 이해할 수 있는 토큰 언어로 번역합니다. 번역이 끝나면 LLM은 텍스트든 이미지든 동일하게 처리합니다.
{% endhint %}

### 오디오/비디오는?

동일한 원리가 적용됩니다.

- **오디오**: Audio Encoder(예: Whisper)가 음성을 토큰으로 변환 → LLM 입력
- **비디오**: 프레임을 추출하여 각 프레임을 Vision Encoder로 처리 → 시간 순서대로 토큰 나열

---

## 4. 업종별 멀티모달 활용 사례

멀티모달 AI가 실제 비즈니스에서 어떻게 활용되는지, 업종별 사례를 정리합니다.

| 업종 | 사용 사례 | 입력 | 기대 효과 |
|------|----------|------|----------|
| **제조/품질** | 외관 검사 자동화 | 제품 이미지 | 불량률 감소, 검사 속도 10배 향상 |
| **의료** | X-ray/CT 판독 보조 | 의료 이미지 | 진단 시간 단축, 2차 소견 제공 |
| **유통** | 상품 분류/태깅 | 상품 사진 | 카탈로그 자동화, 수작업 90% 절감 |
| **건설** | 현장 안전 모니터링 | CCTV 영상 | 사고 예방, 실시간 알림 |
| **금융** | 문서 자동 처리 | 스캔 문서/PDF | 수작업 80% 절감, 처리 시간 단축 |
| **보험** | 사고 현장 사진 분석 | 차량/건물 사진 | 손해 사정 자동화, 심사 시간 단축 |
| **물류** | 패키지 라벨 인식 | 박스 사진 | 분류 자동화, 오배송 감소 |

### 제조 분야 심화: 외관 검사 자동화

제조업에서 가장 빠르게 도입되는 멀티모달 사용 사례입니다.

**기존 방식의 문제점**:
- Rule-based 비전 시스템: 새로운 불량 유형 발생 시 규칙 수동 추가 필요
- 전통 ML 모델: 불량 유형별 수천 장의 라벨링 데이터 필요
- 사람 검사: 피로도에 따른 품질 편차, 속도 제한

**멀티모달 AI 접근**:
- 이미지를 LLM에 전달하며 "이 제품 이미지에서 스크래치, 변색, 크랙 등의 불량이 있는지 분석하세요"라고 프롬프트
- 새로운 불량 유형도 **라벨링 없이** 프롬프트 수정만으로 대응
- 불량 판정뿐 아니라 **자연어로 불량 원인과 위치 설명** 가능

{% hint style="warning" %}
**주의**: 멀티모달 LLM은 "1차 스크리닝"에 적합합니다. 마이크로 단위의 **미세 결함 탐지** 는 여전히 전문 비전 모델(YOLO, Segment Anything 등)이 더 정확합니다. 두 접근을 **병행** 하는 것이 현실적입니다.
{% endhint %}

---

## 5. 한계와 주의사항

멀티모달 AI는 강력하지만, 현재 기술 수준의 한계를 정확히 이해해야 합니다.

### Vision Hallucination

텍스트 LLM의 Hallucination과 마찬가지로, 멀티모달 모델도 **이미지에 없는 내용을 생성** 합니다.

| 유형 | 예시 | 위험도 |
|------|------|--------|
| **객체 환각** | 이미지에 없는 물체를 "있다"고 답변 | 높음 |
| **속성 환각** | 빨간 자동차를 "파란 자동차"라고 설명 | 중간 |
| **관계 환각** | 두 물체의 위치 관계를 잘못 설명 | 중간 |
| **텍스트 환각** | OCR 결과를 잘못 읽음 (특히 한국어) | 높음 |

### 정확도 한계

- **세밀한 OCR**: 작은 글씨, 손글씨, 한국어 세로쓰기 등은 전문 OCR 엔진이 더 정확
- **미세 결함 탐지**: 픽셀 단위 분석은 전문 CV 모델이 우수
- **계수(counting)**: 이미지 내 객체 수를 정확히 세는 것은 여전히 약점

### 비용

이미지 토큰은 텍스트 토큰보다 **수량이 많고 비용이 높습니다**.

| 입력 유형 | 토큰 수 (대략) | 비용 영향 |
|----------|--------------|----------|
| 텍스트 질문 (100자) | ~50 토큰 | 기본 |
| 저해상도 이미지 (512x512) | ~85 토큰 | 텍스트의 ~2배 |
| 고해상도 이미지 (2048x2048) | ~1,000+ 토큰 | 텍스트의 ~20배 |
| 비디오 (1분, 1fps 샘플링) | ~60,000+ 토큰 | 텍스트의 ~1,000배 |

{% hint style="warning" %}
**비용 최적화 팁**: 불필요하게 고해상도 이미지를 전달하지 마세요. 대부분의 분석 작업은 **512x512 ~ 1024x1024** 해상도로 충분합니다. 이미지 크기를 줄이는 전처리만으로 비용을 50% 이상 절감할 수 있습니다.
{% endhint %}

### 프라이버시

- **의료 이미지**: 환자 개인정보가 포함될 수 있으며, 외부 API로 전송 시 규정 위반 가능
- **얼굴 이미지**: 개인정보보호법 적용 대상
- **기업 기밀 문서**: 스캔 이미지로 전달 시 데이터 유출 리스크

{% hint style="info" %}
**대응 전략**: 민감 이미지를 다룰 때는 (1) 온프레미스/VPC 내 모델 배포, (2) 이미지 익명화 전처리, (3) Databricks Model Serving의 데이터 격리 기능을 활용하세요.
{% endhint %}

---

## 6. Databricks에서 멀티모달 활용

Databricks 플랫폼에서 멀티모달 AI를 활용하는 3가지 방법입니다.

### Foundation Model APIs

Databricks **Foundation Model APIs** 를 통해 GPT-4o, Claude 4 등 멀티모달 모델을 바로 호출할 수 있습니다.

```python
# Databricks Foundation Model API로 이미지 분석 예시
import base64
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# 이미지를 base64로 인코딩
with open("product_image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

response = w.serving_endpoints.query(
    name="databricks-claude-sonnet-4",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "이 제품 이미지에서 불량이 있는지 분석하세요."},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}"
            }}
        ]
    }]
)
print(response.choices[0].message.content)
```

### 이미지 기반 이상탐지 (MLOps 핸즈온 연계)

본 Enablement 블로그의 [예지보전 MLOps 핸즈온](../../../hands-on/predictive-maintenance/07-anomaly-detection.md)에서 실제 **이미지 기반 이상탐지** 파이프라인을 구현합니다. 센서 데이터뿐 아니라 제품 이미지를 활용한 이상탐지가 멀티모달의 대표적인 실전 사례입니다.

### 대규모 이미지 전처리 파이프라인

Spark를 활용하면 수백만 장의 이미지를 **분산 처리** 한 뒤 LLM에 전달할 수 있습니다.

```python
# Spark로 대규모 이미지 전처리 후 LLM 분석 파이프라인
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType

# Unity Catalog Volume에서 이미지 로드
images_df = spark.read.format("binaryFile") \
    .load("dbfs:/Volumes/catalog/schema/images/*.jpg")

# 이미지 리사이즈 UDF
@udf(returnType=StringType())
def analyze_image(content):
    # Foundation Model API 호출
    import base64
    image_b64 = base64.b64encode(content).decode()
    # ... API 호출 로직
    return result

# 분산 처리로 수만 장 분석
results_df = images_df.withColumn(
    "analysis", analyze_image(col("content"))
)
results_df.write.saveAsTable("catalog.schema.image_analysis_results")
```

{% hint style="info" %}
**아키텍처 포인트**: Spark DataFrame으로 이미지를 분산 로드 → UDF 내에서 Foundation Model API 호출 → 결과를 Delta Table에 저장하는 패턴이 Databricks에서의 표준 멀티모달 파이프라인입니다.
{% endhint %}

---

## 7. 고객 FAQ

{% hint style="info" %}
아래는 고객 미팅에서 자주 받는 멀티모달 관련 질문과 권장 답변입니다.
{% endhint %}

### "멀티모달 AI로 기존 비전 시스템을 대체할 수 있나요?"

**완전 대체는 아직 어렵고, "보완"이 현실적입니다.**

| 영역 | 멀티모달 LLM | 전문 비전 모델 | 권장 |
|------|-------------|--------------|------|
| 일반 분류/설명 | 우수 | 보통 | **멀티모달 LLM** |
| 미세 결함 탐지 | 보통 | 우수 | **전문 모델** |
| 새로운 불량 유형 대응 | 우수 (프롬프트 수정) | 약함 (재학습 필요) | **멀티모달 LLM** |
| 실시간 대량 처리 | 느림 | 빠름 | **전문 모델** |
| 분석 결과 설명 | 우수 (자연어) | 약함 (수치만) | **멀티모달 LLM** |

권장 접근: 전문 비전 모델로 **1차 탐지**→ 멀티모달 LLM으로 **2차 분석 및 설명 생성** 의 2단계 파이프라인이 가장 실용적입니다.

### "이미지 처리 비용이 너무 높지 않나요?"

비용을 관리하는 **5가지 전략** 입니다.

1. **이미지 해상도 축소**: 대부분의 분석은 512x512로 충분 (비용 50~70% 절감)
2. **관심 영역(ROI) 크롭**: 전체 이미지 대신 분석이 필요한 영역만 전달
3. **배치 처리**: 실시간이 불필요하면 Batch API 활용 (50% 할인)
4. **캐싱**: 동일/유사 이미지 분석 결과를 캐싱하여 중복 호출 방지
5. **모델 선택**: 간단한 분류는 경량 모델, 정밀 분석만 대형 모델 사용

### "민감한 이미지(의료/개인정보)를 처리하려면?"

**데이터 주권(Data Sovereignty)** 을 보장하는 3가지 방법입니다.

1. **Databricks Model Serving**: VPC 내에서 오픈소스 멀티모달 모델(Llama 4 등)을 직접 호스팅. 데이터가 외부로 나가지 않음
2. **이미지 익명화 전처리**: 얼굴 블러, 개인정보 마스킹을 전처리 파이프라인에서 수행 후 API 호출
3. **Azure OpenAI / AWS Bedrock 연동**: Databricks에서 고객 전용 엔드포인트로 호출. 데이터가 공유되지 않음

---

## 8. 참고 자료

- [OpenAI GPT-4o 기술 블로그](https://openai.com/index/hello-gpt-4o/)
- [Google Gemini 2.5 Pro](https://deepmind.google/technologies/gemini/)
- [Meta Llama 4 공개](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)
- [Liu et al., "Visual Instruction Tuning (LLaVA)" (2023)](https://arxiv.org/abs/2304.08485)
- [Databricks Foundation Model APIs](https://docs.databricks.com/en/machine-learning/foundation-models/index.html)
- [Databricks Model Serving](https://docs.databricks.com/en/machine-learning/model-serving/index.html)

---

[< 이전: 실전 가이드](practical.md) | [LLM 기초 목차로 돌아가기](README.md)
