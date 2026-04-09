# 후처리 기법

## 개요

검색 결과를 LLM에 전달한 **이후** 에 수행하는 품질 개선 기법들입니다. 환각(Hallucination)을 줄이고 답변의 신뢰성을 높이는 데 핵심적인 역할을 합니다.

아래 표는 주요 후처리 전략을 비교합니다.

| 전략 | 설명 | ML 모델 | Databricks 지원 | 환각 감소 효과 |
|------|------|--------|--------------|------------|
| **Self-RAG** | LLM이 스스로 검색 관련성, 답변 충실도, 질문 충족도를 평가하고 반복. 자기 교정 메커니즘 | LLM | ✅ | 높음 |
| **Corrective RAG (CRAG)** | 검색 결과를 "정확/모호/틀림"으로 분류. 틀리면 외부 웹 검색으로 보완 | LLM/Classic | ✅ | 높음 |
| **FLARE** | 생성 중 확신도가 낮은 부분에서 자동으로 추가 검색 수행. 긴 문서 작업에 효과적 | LLM | ✅ | 중간 |
| **출력 가드레일** | JSON 포맷 검증, 보안 가이드라인 위반 체크, 편향성/욕설 필터링 | Classic | ✅ | - |

위 전략들은 서로 배타적이지 않으며, 조합하여 사용할 수 있습니다. 일반적으로 **Self-RAG + 출력 가드레일** 이 가장 실용적인 조합이며, 외부 소스 연동이 필요한 경우 CRAG를 추가합니다. FLARE는 긴 보고서 생성 등 특수한 시나리오에 적합합니다.

## Self-RAG (자기 교정 RAG)

Self-RAG는 2023년 워싱턴대학교에서 발표한 기법(논문: "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection")으로, LLM이 **스스로 검색 결과의 관련성과 답변의 품질을 평가** 하고, 필요하면 재검색하는 반복적 자기 교정 프로세스입니다.

**왜 필요한가?** 기본 RAG는 검색 결과를 무조건 신뢰하고 답변을 생성합니다. 그러나 검색 결과가 질문과 무관하거나, LLM이 검색 결과에 없는 내용을 지어내는(환각) 경우가 빈번합니다. Self-RAG는 이 두 가지 문제를 **생성 후 자체 검증** 을 통해 해결합니다.

**동작 원리 (4단계 반복 루프):**
1. **검색(Retrieve)**: 질문에 대해 관련 문서를 검색합니다
2. **관련성 평가(Relevance Check)**: 검색된 문서가 질문에 실제로 관련 있는지 LLM이 판단합니다. 관련 없으면 쿼리를 재작성하여 1단계로 돌아갑니다
3. **답변 생성(Generate)**: 관련 문서를 기반으로 답변을 생성합니다
4. **충실도 평가(Faithfulness Check)**: 생성된 답변이 검색 결과에 **근거** 하는지 검증합니다. 검색 결과에 없는 정보가 답변에 포함되어 있으면 환각으로 판단하고, 재생성하거나 반복합니다

이 루프를 최대 N회(보통 2~3회) 반복하며, 관련성과 충실도를 모두 통과한 답변만 최종 출력합니다.

```python
def self_rag(question: str, retriever, llm, max_iterations: int = 3) -> str:
    """Self-RAG: 자기 교정 반복 검색-생성 파이프라인"""

    for iteration in range(max_iterations):
        # 1단계: 검색
        docs = retriever.invoke(question)
        context = "\n\n".join([d.page_content for d in docs])

        # 2단계: 관련성 평가
        relevance_prompt = f"""다음 검색 결과가 질문에 관련이 있는지 평가하세요.

질문: {question}
검색 결과: {context[:2000]}

평가 (RELEVANT / NOT_RELEVANT):"""
        relevance = llm.invoke(relevance_prompt).content.strip()

        if "NOT_RELEVANT" in relevance:
            # 검색 결과가 관련 없으면 쿼리를 재작성하여 재검색
            question = rewrite_query(question)
            continue

        # 3단계: 답변 생성
        answer_prompt = f"""다음 검색 결과를 바탕으로 질문에 답변하세요.
검색 결과에 없는 내용은 "정보가 부족합니다"라고 답하세요.

질문: {question}
검색 결과: {context}

답변:"""
        answer = llm.invoke(answer_prompt).content

        # 4단계: 충실도 평가 (답변이 검색 결과에 근거하는지)
        faithfulness_prompt = f"""답변이 검색 결과에 근거하는지 평가하세요.
검색 결과에 없는 정보가 답변에 포함되어 있으면 NOT_FAITHFUL입니다.

검색 결과: {context[:2000]}
답변: {answer}

평가 (FAITHFUL / NOT_FAITHFUL):"""
        faithfulness = llm.invoke(faithfulness_prompt).content.strip()

        if "FAITHFUL" in faithfulness and "NOT" not in faithfulness:
            return answer

    return "충분한 정보를 찾지 못했습니다. 질문을 더 구체적으로 바꿔주세요."
```

## Corrective RAG (CRAG)

Corrective RAG는 2024년 발표된 기법(논문: "Corrective Retrieval Augmented Generation")으로, 검색 결과를 **"정확/모호/틀림"** 3단계로 분류하고, 결과가 부정확하면 **외부 웹 검색으로 보완** 하는 전략입니다.

**왜 필요한가?** 기본 RAG와 Self-RAG는 내부 벡터 DB에서만 검색합니다. 내부 문서에 답이 없는 질문이 들어오면, 관련 없는 문서를 억지로 참고하여 부정확한 답변을 생성하게 됩니다. CRAG는 **검색 결과의 품질을 먼저 진단** 하고, 내부 검색으로 충분하지 않으면 외부 소스(웹 검색 등)로 자동 전환합니다.

**왜 3단계 분류인가?**
- **CORRECT(정확)**: 검색 결과가 질문에 대한 답을 직접 포함 → 그대로 사용
- **AMBIGUOUS(모호)**: 부분적으로 관련 있지만 불완전 → 내부 검색 결과 + 외부 검색 결과를 **결합** 하여 보완
- **INCORRECT(틀림)**: 질문과 무관하거나 잘못된 정보 → 내부 결과를 **폐기** 하고 외부 검색으로 완전 대체

이 3단계 구분이 중요한 이유는, 단순 이진 분류(맞다/틀리다)와 달리 **"부분적으로 유용한 정보"를 버리지 않고 활용** 할 수 있기 때문입니다.

```python
def corrective_rag(question: str, docs: list, llm) -> dict:
    """Corrective RAG: 검색 결과 품질에 따른 보정 전략"""

    # 1단계: 검색 결과 품질 분류
    grading_prompt = f"""다음 검색 결과가 질문에 대한 답변을 포함하는지 평가하세요.

질문: {question}
검색 결과: {docs[0].page_content[:1000] if docs else "없음"}

분류:
- CORRECT: 질문에 대한 정확한 답변을 포함
- AMBIGUOUS: 부분적으로 관련 있지만 불완전
- INCORRECT: 질문과 관련 없거나 잘못된 정보

분류 결과 (CORRECT/AMBIGUOUS/INCORRECT):"""

    grade = llm.invoke(grading_prompt).content.strip()

    if "CORRECT" in grade:
        # 검색 결과를 그대로 사용하여 답변 생성
        return {"strategy": "use_retrieval", "docs": docs}

    elif "AMBIGUOUS" in grade:
        # 검색 결과 + 웹 검색 결과를 결합
        web_results = web_search(question)  # 외부 웹 검색
        combined_docs = docs + web_results
        return {"strategy": "combine", "docs": combined_docs}

    else:  # INCORRECT
        # 검색 결과를 버리고 웹 검색으로 대체
        web_results = web_search(question)
        return {"strategy": "web_only", "docs": web_results}
```

## FLARE (Forward-Looking Active REtrieval)

FLARE는 2023년 CMU에서 발표한 기법(논문: "Active Retrieval Augmented Generation")으로, LLM이 답변을 생성하는 **도중에** 확신도가 낮은 부분을 감지하고, 해당 부분에 대해 **추가 검색을 자동 수행** 하는 기법입니다. 특히 긴 문서를 생성할 때 효과적입니다.

**왜 필요한가?** Self-RAG와 CRAG는 답변을 **생성한 후** 전체를 평가합니다. 그러나 긴 답변을 생성할 때, 앞부분은 정확하지만 뒷부분에서 환각이 발생하는 경우가 흔합니다. FLARE는 답변을 **문장 단위로 생성하면서 실시간으로** 확신도를 모니터링하고, 불확실한 부분이 나타나면 즉시 추가 검색을 수행합니다.

**"확신도"는 어떻게 측정하는가?** 원래 논문에서는 LLM이 생성하는 각 토큰의 **생성 확률(logit probability)** 을 관찰합니다. 특정 토큰의 확률이 임계값(보통 0.5) 아래로 떨어지면, 해당 문장을 "확신도 낮음"으로 판정합니다. 아래 구현 예시에서는 이를 단순화하여 LLM에게 직접 불확실한 부분을 표시하도록 프롬프트합니다.

**동작 흐름:**
1. LLM이 답변을 문장 단위로 생성합니다
2. 각 문장 생성 시 토큰 확률을 확인합니다
3. 확률이 낮은(불확실한) 문장이 발견되면, 해당 문장의 내용으로 **추가 검색 쿼리** 를 생성합니다
4. 추가 검색 결과를 컨텍스트에 추가하고, 해당 문장을 재생성합니다
5. 이 과정을 답변이 완성될 때까지 반복합니다

```python
def flare_generate(question: str, retriever, llm) -> str:
    """FLARE: 생성 중 확신도 낮은 부분에서 추가 검색"""

    # 초기 검색 + 부분 답변 생성
    initial_docs = retriever.invoke(question)
    context = "\n".join([d.page_content for d in initial_docs])

    # 답변을 문장 단위로 생성하며 확신도 체크
    prompt = f"""질문: {question}
참고 자료: {context}

답변을 생성하되, 확신이 낮은 부분은 [LOW_CONFIDENCE: 추가 검색 쿼리] 형식으로 표시하세요.

답변:"""

    partial_answer = llm.invoke(prompt).content

    # [LOW_CONFIDENCE: ...] 부분이 있으면 추가 검색 수행
    import re
    low_conf_pattern = r'\[LOW_CONFIDENCE: (.+?)\]'
    matches = re.findall(low_conf_pattern, partial_answer)

    for match in matches:
        # 추가 검색 수행
        additional_docs = retriever.invoke(match)
        additional_context = additional_docs[0].page_content if additional_docs else ""

        # 확신도 낮은 부분을 추가 검색 결과로 교체
        replacement_prompt = f"""다음 정보를 바탕으로 한 문장으로 답변하세요:
{additional_context}

질문: {match}
답변:"""
        replacement = llm.invoke(replacement_prompt).content
        partial_answer = partial_answer.replace(f"[LOW_CONFIDENCE: {match}]", replacement)

    return partial_answer
```

## 출력 가드레일

**왜 필요한가?** RAG 시스템이 정확한 답변을 생성하더라도, 그 답변이 **안전하고 적절한 형태** 로 사용자에게 전달되는지는 별도로 검증해야 합니다. 답변에 개인정보(PII)가 포함되어 있거나, 보안 가이드라인을 위반하거나, 출처 없이 단정적으로 주장하는 경우가 있을 수 있습니다. 출력 가드레일은 LLM이 아닌 **규칙 기반(Classic ML/정규식)** 으로 동작하므로 빠르고 결정적(deterministic)이며, 환각이나 판단 오류가 없습니다.

**주요 검증 항목:**
- **PII 감지/마스킹**: 주민등록번호, 이메일, 전화번호 등 개인정보를 정규식으로 탐지하여 자동 마스킹
- **출처 인용 확인**: 답변에 근거 문서에 대한 출처가 명시되어 있는지 확인
- **유해 콘텐츠 필터**: 편향, 차별, 욕설 등 부적절한 내용을 ML 분류기 또는 키워드로 탐지
- **포맷 검증**: JSON, SQL 등 구조화된 출력의 형식 유효성 검사

```python
import json
import re

def apply_guardrails(answer: str, question: str) -> dict:
    """출력 가드레일: 답변 품질 및 안전성 검증"""

    checks = {
        "format_valid": True,
        "no_pii": True,
        "no_harmful_content": True,
        "has_source_citation": True,
    }

    # 1. PII (개인정보) 검출
    pii_patterns = [
        r'\d{3}-\d{2}-\d{5}',        # SSN
        r'\d{6}-[1-4]\d{6}',          # 주민등록번호
        r'[\w.-]+@[\w.-]+\.\w+',      # 이메일 (경고만)
    ]
    for pattern in pii_patterns:
        if re.search(pattern, answer):
            checks["no_pii"] = False
            answer = re.sub(pattern, "[개인정보 마스킹]", answer)

    # 2. 출처 인용 확인
    if "출처" not in answer and "참고" not in answer and "근거" not in answer:
        checks["has_source_citation"] = False
        answer += "\n\n*주의: 이 답변에 명시적 출처가 포함되지 않았습니다.*"

    return {"answer": answer, "checks": checks}
```
