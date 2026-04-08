---
title: "MLflow 3 출시 발표"
date: 2025-06-09
author: "MLflow Maintainers"
original_url: "https://mlflow.org/blog/mlflow-3-launch"
tags: [mlflow, genai, tracing, evaluation, mlops]
---

> **원문**: [Announcing MLflow 3](https://mlflow.org/blog/mlflow-3-launch)

{% hint style="info" %}
요청하신 URL(`databricks.com/blog/mlflow-3-release`)은 404 오류를 반환합니다. 동일한 주제를 다루는 공식 MLflow 블로그의 출시 공지 포스트를 번역합니다.
{% endhint %}

# MLflow 3 출시 발표

**게시일**: 2025년 6월 9일 · 읽기 약 6분

**작성자**: MLflow Maintainers

---

오픈 소스 MLflow 커뮤니티가 중요한 이정표에 도달했습니다. 오늘, 수백만 명의 개발자가 ML 운영에 신뢰하는 플랫폼에 프로덕션 수준의 Generative AI 기능을 제공하는 **MLflow 3** 를 출시합니다.

이것은 단순한 기능 업데이트가 아닙니다. MLflow 3는 오픈 소스 ML 툴링으로 가능한 것을 근본적으로 확장하며, GenAI 배포를 마치 믿음의 도약처럼 느끼게 만들었던 **Observability** 와 품질 문제를 해결합니다.

---

## GenAI가 기존 MLOps를 어렵게 만드는 이유

전통적인 머신러닝은 예측 가능한 패턴을 따릅니다. Ground truth 레이블이 있는 데이터셋, 성공 또는 실패를 명확하게 나타내는 메트릭, 그리고 수평적으로 확장되는 배포 파이프라인이 있습니다. GenAI는 강력한 기능으로 혁신적일 뿐만 아니라, 품질과 안정성을 측정하고 보장하는 방법에도 근본적인 변화를 가져옵니다.

간단한 질문을 하나 생각해봅시다. "RAG 시스템이 올바르게 작동하고 있다는 것을 어떻게 알 수 있을까요?" 전통적인 ML에서는 테스트 셋에 대한 정확도를 확인할 것입니다. GenAI에서는 다음과 같은 문제들을 다루게 됩니다.

- **복잡한 실행 흐름**: 여러 번의 LLM 호출, 검색, 툴 상호작용을 포함
- **주관적인 출력 품질**: "올바른" 답이 수십 가지의 서로 다른 유효한 응답을 의미할 수 있음
- **레이턴시 및 비용 문제**: 사용자 경험을 좌우하는 핵심 요소
- **디버깅의 어려움**: 다단계 추론 체인 깊은 곳에서 문제가 발생했을 때의 혼란

현재의 해결책은? 대부분의 팀이 서로 다른 벤더의 모니터링 도구, 평가 스크립트, 배포 파이프라인을 조합하여 사용합니다. 그 결과는 시스템 간에 중요한 정보가 유실되는 파편화된 워크플로우입니다.

---

## GenAI 인프라에 대한 다른 접근법

MLflow 3는 다른 방식을 취합니다. 또 다른 전문화된 GenAI 플랫폼을 구축하는 대신, MLflow의 검증된 기반을 확장하여 기존 ML 워크플로우와의 호환성을 유지하면서 Generative AI의 고유한 요구사항을 처리합니다.

이는 Transformer 훈련 파이프라인과 멀티 에이전트 RAG 시스템을 동일한 도구로 계측하고, 동일한 Registry를 통해 배포하며, 통합된 Observability 인프라로 모니터링할 수 있음을 의미합니다.

---

## MLflow Tracing을 통한 심층 Observability

MLflow 3의 핵심은 전체 GenAI 에코시스템에서 작동하는 포괄적인 Tracing입니다. 기본적인 입출력만 캡처하는 로깅 프레임워크와 달리, MLflow Tracing은 복잡한 실행 흐름에 대한 계층적 가시성을 제공합니다.

```python
import mlflow
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma

# 한 줄로 전체 애플리케이션 계측
mlflow.langchain.autolog()

@mlflow.trace(name="customer_support")
def answer_question(question, customer_tier="standard"):
    vectorstore = Chroma.from_documents(documents, embeddings)
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0),
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
    # Tracing이 전체 실행 트리를 자동으로 캡처
    result = qa_chain({"query": question})
    # 트레이스에 비즈니스 컨텍스트 추가
    mlflow.update_current_trace(
        tags={
            "customer_tier": customer_tier,
            "question_category": classify_question(question)
        }
    )
    return result["result"]
```

이것이 강력한 이유는 자동 계측 때문입니다. `answer_question()`이 실행될 때, MLflow Tracing은 다음을 캡처합니다.

- 쿼리 처리를 위한 초기 LLM 호출
- 임베딩 계산을 포함한 Vector Database 검색
- 문서 순위 지정 및 선택 로직
- 토큰 사용량을 포함한 최종 답변 생성
- 모든 중간 입력, 출력 및 타이밍 정보
- 오류 발생 시 스택 트레이스를 포함한 상세하고 포괄적인 오류 메시지

이를 통해 문제가 발생했을 때 드릴다운할 수 있는 완전한 실행 타임라인이 생성됩니다. RAG 시스템이 왜 관련 없는 문서를 반환했는지, 또는 응답 시간이 왜 급증했는지 더 이상 추측할 필요가 없습니다.

---

## 체계적인 품질 평가

GenAI 품질 평가는 전통적으로 확장되지 않는 수동 검토 프로세스를 의미했습니다. MLflow 3에는 품질 차원을 체계적으로 평가할 수 있는 포괄적인 평가 프레임워크가 포함되어 있습니다.

평가 하네스는 직접 평가(MLflow가 애플리케이션을 호출하여 새로운 트레이스를 생성)와 답안지 평가(사전 계산된 출력용) 모두를 지원합니다. 또한 `@scorer` 데코레이터를 사용하여 도메인별 요구사항에 맞는 커스텀 Scorer를 구축하여 평가 요구사항을 완전히 커스터마이징할 수 있습니다.

---

## 애플리케이션 생명주기 관리

GenAI 애플리케이션은 단순한 모델 그 이상입니다. 프롬프트, 검색 로직, 툴 통합, 오케스트레이션 코드를 포함하는 복잡한 시스템입니다. MLflow 3는 이러한 애플리케이션을 버전 관리, 등록, 원자적 배포가 가능한 일급 아티팩트(first-class artifact)로 취급합니다.

```python
import mlflow.pyfunc

class CustomerServiceBot(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        # GenAI 애플리케이션의 모든 컴포넌트 로드
        self.llm = load_model_from_artifacts(context.artifacts["llm_config"])
        self.vector_store = initialize_vector_store(context.artifacts["knowledge_base"])
        self.prompt_template = load_prompt_template(context.artifacts["prompt_template"])

    def predict(self, context, model_input):
        # 애플리케이션 로직
        query = model_input["query"][0]
        relevant_docs = self.vector_store.similarity_search(query, k=3)
        formatted_prompt = self.prompt_template.format(
            query=query,
            context="\n".join([doc.page_content for doc in relevant_docs])
        )
        response = self.llm.predict(formatted_prompt)
        return {
            "response": response,
            "sources": [doc.metadata for doc in relevant_docs]
        }

# 완전한 애플리케이션을 패키징하고 버전 관리
with mlflow.start_run():
    model_info = mlflow.pyfunc.log_model(
        artifact_path="customer_service_bot",
        python_model=CustomerServiceBot(),
        artifacts={
            "llm_config": "configs/llm_config.yaml",
            "knowledge_base": "data/knowledge_embeddings.pkl",
            "prompt_template": "prompts/customer_service_v2.txt"
        },
        pip_requirements=["openai", "langchain", "chromadb"],
        signature=mlflow.models.infer_signature(example_input, example_output)
    )
    # 배포를 위해 Model Registry에 등록
    registered_model = mlflow.register_model(
        model_uri=model_info.model_uri,
        name="customer_service_bot",
        tags={"version": "v2.1", "eval_score": "0.87"}
    )
```

이 접근 방식은 고객 서비스 봇의 버전 2.1을 배포할 때, 테스트한 것과 정확히 동일한 모델 가중치, 프롬프트, 검색 로직, 의존성 조합을 배포한다는 것을 보장합니다. "개발 환경에서는 잘 됐는데"라는 배포 문제는 이제 없습니다.

---

## 전통적인 ML 및 딥러닝 기능 강화

GenAI 기능이 주요 특징이지만, MLflow 3에는 전통적인 머신러닝과 딥러닝 워크플로우를 위한 중요한 개선 사항도 포함되어 있습니다.

- **향상된 Model Registry**: GenAI 애플리케이션을 처리하는 것과 동일한 버전 관리 및 배포 인프라가 이제 모든 모델 유형에 대해 더 나은 계보 추적(lineage tracking)을 제공합니다. 딥러닝 실무자들은 향상된 체크포인트 관리와 실험 구성의 혜택을 받습니다.
- **통합 평가 프레임워크**: 평가 시스템이 GenAI를 넘어 컴퓨터 비전, NLP, 테이블 형식 데이터 모델을 위한 커스텀 메트릭을 지원하도록 확장됩니다. 팀은 이제 서로 다른 모델 유형에 걸쳐 평가 프로세스를 표준화할 수 있습니다.
- **개선된 배포 워크플로우**: 품질 게이트와 자동화된 테스트 기능이 scikit-learn 분류기든 멀티모달 파운데이션 모델이든 모든 MLflow 모델에 적용됩니다.

---

## 지금 바로 시작하기

MLflow 3는 지금 바로 사용 가능하며 기존 ML 인프라와 함께 작동하도록 설계되었습니다. 시작하는 방법은 다음과 같습니다.

### 설치

```bash
pip install -U mlflow
```

### 첫 번째 단계

```python
import mlflow

# 첫 번째 GenAI 실험 생성
mlflow.set_experiment("my_genai_prototype")

# OpenAI에 대한 자동 Tracing 활성화
# (지원되는 20개 이상의 Tracing 통합 중 하나를 선택하여 자동 Tracing 활성화)
mlflow.openai.autolog()

# 기존 GenAI 코드가 이제 자동으로 트레이스를 생성합니다.
# 지원되는 라이브러리에는 추가 계측이 필요 없습니다.
```

---

## 앞으로의 로드맵

MLflow 3는 GenAI 개발을 보다 체계적이고 신뢰할 수 있게 만드는 데 있어 중요한 진전을 나타냅니다. 하지만 이것은 시작에 불과합니다. 오픈 소스 커뮤니티는 새로운 통합, 평가 메트릭, 배포 패턴으로 지속적인 혁신을 이끌고 있습니다.

**참여하는 방법:**

- **코드 기여**: 버그 수정부터 새로운 통합까지 모든 규모의 기여를 환영합니다.
- **사용 사례 공유**: MLflow 구현 사례를 문서화하여 다른 사람들이 배울 수 있도록 도움을 주세요.
- **이슈 리포트**: 버그를 보고하고 기능을 요청하여 개선에 기여하세요.
- **토론 참여**: 기술 토론 및 로드맵 계획에 참여하세요.

AI 개발의 미래는 통합되고, 관찰 가능하며, 신뢰할 수 있습니다. MLflow 3는 그 미래를 오늘 오픈 소스 커뮤니티에 가져옵니다.

---

MLflow 3를 사용해볼 준비가 됐나요? [전체 문서](https://mlflow.org/docs/latest/index.html)를 탐색하여 무엇이 가능한지 확인해보세요.

*MLflow는 Apache 2.0 라이선스 하의 오픈 소스 프로젝트로, 글로벌 ML 커뮤니티의 기여로 만들어집니다.*
