# 후처리 기법

## 개요

검색 결과를 LLM에 전달한 ** 이후** 에 수행하는 품질 개선 기법들입니다. 환각(Hallucination)을 줄이고 답변의 신뢰성을 높이는 데 핵심적인 역할을 합니다.

아래 표는 주요 후처리 전략을 비교합니다.

| 전략 | 설명 | ML 모델 | Databricks 지원 | 환각 감소 효과 |
|------|------|--------|--------------|------------|
| **Self-RAG**| LLM이 스스로 검색 관련성, 답변 충실도, 질문 충족도를 평가하고 반복. 자기 교정 메커니즘 | LLM | ✅ | 높음 |
| **Corrective RAG (CRAG)**| 검색 결과를 "정확/모호/틀림"으로 분류. 틀리면 외부 웹 검색으로 보완 | LLM/Classic | ✅ | 높음 |
| **FLARE**| 생성 중 확신도가 낮은 부분에서 자동으로 추가 검색 수행. 긴 문서 작업에 효과적 | LLM | ✅ | 중간 |
| ** 출력 가드레일**| JSON 포맷 검증, 보안 가이드라인 위반 체크, 편향성/욕설 필터링 | Classic | ✅ | - |

## Self-RAG (자기 교정 RAG)

Self-RAG는 LLM이 ** 스스로 검색 결과의 관련성과 답변의 품질을 평가** 하고, 필요하면 재검색하는 반복적 자기 교정 프로세스입니다.

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

Corrective RAG는 검색 결과를 **"정확/모호/틀림"**3단계로 분류하고, 결과가 부정확하면 ** 외부 웹 검색으로 보완** 하는 전략입니다.

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

FLARE는 LLM이 답변을 생성하는 ** 도중에** 확신도가 낮은 부분을 감지하고, 해당 부분에 대해 ** 추가 검색을 자동 수행** 하는 기법입니다. 특히 긴 문서를 생성할 때 효과적입니다.

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
