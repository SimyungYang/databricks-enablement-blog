# 전처리 기법

## Query Expansion (쿼리 확장)

사용자의 원래 쿼리를 확장하거나 변형하여 검색 recall을 높이는 기법입니다.

### HyDE (Hypothetical Document Embeddings)

LLM이 질문에 대한 **가상의 답변** 을 생성하고, 그 답변의 임베딩으로 검색합니다.

**왜 효과적인가?** 질문과 답변은 구조적으로 다릅니다. 질문("Delta Lake를 어떻게 최적화하나요?")은 짧고 의문형이지만, 실제 문서는 서술형("Z-ORDER BY를 사용하여 데이터를 정렬하고...")입니다. 임베딩 모델은 **형태가 유사한 텍스트** 끼리 벡터 공간에서 가까이 배치하는 경향이 있으므로, 서술형 가상 답변이 서술형 실제 문서와 더 가까운 벡터를 갖게 됩니다. 가상 답변의 사실 여부는 중요하지 않습니다. 핵심은 관련 용어와 문체가 실제 문서와 유사해지는 것입니다.

```python
from langchain_databricks import ChatDatabricks

llm = ChatDatabricks(endpoint="databricks-meta-llama-3-3-70b-instruct")

def hyde_query_expansion(question: str) -> str:
    """HyDE: 가상의 답변을 생성하여 검색 쿼리로 사용"""
    prompt = f"""다음 질문에 대해 가상의 답변을 작성하세요.
실제 정확성은 중요하지 않으며, 관련 문서와 유사한 스타일과 용어를 사용하세요.

질문: {question}

가상의 답변:"""
    response = llm.invoke(prompt)
    return response.content

# "Delta Lake 최적화 방법" →
# "Delta Lake를 최적화하려면 Z-ORDER BY를 사용하여 데이터를 정렬하고,
#  OPTIMIZE 명령으로 작은 파일을 병합하며, AUTO COMPACTION을 활성화합니다..."
hypothetical_doc = hyde_query_expansion("Delta Lake 최적화 방법")
results = vs_retriever.invoke(hypothetical_doc)
```

### Step-back Prompting

구체적인 질문을 더 **일반적인(추상화된) 질문** 으로 변환하여 검색하는 기법입니다. Google DeepMind가 2023년에 제안했습니다.

**왜 필요한가?** 지나치게 구체적인 질문은 검색 공간을 좁혀 관련 문서를 놓칠 수 있습니다. 예를 들어 "DLT에서 SCD Type 2 구현 방법"이라는 질문은 SCD Type 2와 DLT를 동시에 다루는 문서가 없으면 검색에 실패합니다. 반면 "Delta Live Tables의 데이터 변환 패턴"이라는 일반화된 질문은 더 넓은 범위의 관련 문서를 검색할 수 있고, 그 안에서 SCD Type 2 관련 내용을 찾을 가능성이 높아집니다.

**동작 원리:** LLM이 원래 질문에서 핵심 개념을 추출하고, 해당 개념의 **상위 카테고리** 에 해당하는 질문을 생성합니다. 원래 질문과 Step-back 질문 **모두** 로 검색을 수행한 뒤 결과를 합치면, 구체적 매칭과 넓은 범위의 문맥을 동시에 확보할 수 있습니다.

```python
def stepback_query(question: str) -> str:
    """구체적 질문을 일반적 질문으로 변환"""
    prompt = f"""다음 질문의 핵심 개념을 파악하고,
더 일반적인 형태의 질문으로 변환하세요.

원래 질문: {question}
일반화된 질문:"""
    response = llm.invoke(prompt)
    return response.content

# "DLT 파이프라인에서 SCD Type 2를 구현하는 방법" →
# "Delta Live Tables의 데이터 변환 패턴은?"
```

### Multi-Query (다중 쿼리 생성)

하나의 질문을 **관점이 다른 여러 질문** 으로 변환한 뒤, 각각에 대해 검색을 수행하고 결과를 합치는 기법입니다.

**왜 필요한가?** 동일한 정보 요구(information need)라도 표현 방식에 따라 검색 결과가 크게 달라집니다. 예를 들어 "Delta Lake 성능 개선"과 "Delta Lake 최적화 방법"은 같은 의도지만, 임베딩 공간에서 서로 다른 위치에 놓일 수 있습니다. 여러 표현으로 검색하면 단일 쿼리로는 놓칠 수 있는 관련 문서를 추가로 확보할 수 있습니다.

**동작 원리:** LLM에게 원래 질문과 의미는 같지만 표현이 다른 3~5개의 변형 질문을 생성하도록 요청합니다. 각 변형 질문으로 독립적으로 검색을 수행한 뒤, 모든 결과를 합치고 중복을 제거합니다. LangChain의 `MultiQueryRetriever`가 이 패턴을 내장 지원합니다.

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

multi_retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=llm,
)

# "Delta Lake 성능 개선" →
#   1. "Delta Lake 최적화 방법은?"
#   2. "Delta Lake 테이블 성능을 향상시키는 기법은?"
#   3. "Delta Lake에서 쿼리 속도를 높이려면?"
# → 3개 질문으로 각각 검색 → 결과 합치기 → 중복 제거
results = multi_retriever.invoke("Delta Lake 성능 개선")
```

{% hint style="info" %}
Query Expansion은 검색 recall(재현율, 관련 문서를 빠뜨리지 않는 비율)을 높이지만, LLM 호출 비용이 추가됩니다. Multi-Query, HyDE, Step-back 중 하나를 선택하여 적용하고, 평가를 통해 효과를 검증하세요. 일반적으로 Multi-Query는 범용적이고, HyDE는 질문-문서 간 어휘 격차가 큰 경우에, Step-back은 지나치게 구체적인 질문이 많은 경우에 효과적입니다.
{% endhint %}

---

## Pre-Query Processing (쿼리 전처리)

검색 쿼리가 Retriever에 도달하기 **전에** 수행하는 최적화 기법들입니다. Query Expansion이 "같은 의미를 여러 표현으로" 검색하는 데 초점을 맞춘다면, Pre-Query Processing은 **쿼리 자체를 변환하거나, 검색 대상을 사전에 좁히거나, 질문을 적합한 소스로 라우팅** 하는 등 검색 환경 전체를 최적화합니다.

아래 표는 주요 전처리 전략을 비교합니다.

| 전략 | 설명 | ML 모델 | Databricks 지원 |
|------|------|--------|--------------|
| **메타데이터 사전 필터링** | "2023년", "영업팀" 등 조건을 LLM으로 추출 후 벡터 검색 전에 필터 적용. 탐색 범위를 대폭 축소 | LLM | ✅ |
| **Query Rewrite** | 모호하거나 불완전한 질문을 검색에 최적화된 형태로 재작성. 대화 맥락 반영 | LLM | ✅ |
| **Contextual Retrieval** | Anthropic 제안. 각 청크에 전체 문서의 문맥 요약을 Prepend. 청킹 시 손실되는 정보를 보완 | LLM | ✅ |
| **Query Routing** | 질문의 의도를 분류하여 적합한 데이터 소스(SQL DB, 벡터 DB, 웹)로 라우팅 | LLM | ✅ |
| **다중 쿼리 분해** | 복잡한 질문을 여러 하위 질문으로 분해, 각각 검색 후 결과를 병합 | LLM | ✅ |

### 메타데이터 사전 필터링 (Self-Query)

```python
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain_databricks import ChatDatabricks

llm = ChatDatabricks(endpoint="databricks-claude-sonnet-4")

# 메타데이터 필드 정의
metadata_field_info = [
    AttributeInfo(name="year", description="문서 작성 연도", type="integer"),
    AttributeInfo(name="department", description="부서명 (영업팀, 개발팀, HR 등)", type="string"),
    AttributeInfo(name="doc_type", description="문서 유형 (정책, 매뉴얼, FAQ)", type="string"),
]

self_query_retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents="회사 내부 문서",
    metadata_field_info=metadata_field_info,
)

# "2024년 영업팀 정책 문서에서 출장 규정" →
#   필터: year=2024, department="영업팀", doc_type="정책"
#   쿼리: "출장 규정"
results = self_query_retriever.invoke("2024년 영업팀 정책 문서에서 출장 규정을 알려줘")
```

### Query Rewrite

**Query Rewrite(쿼리 재작성)** 는 사용자의 원래 질문을 검색 엔진이 더 잘 이해할 수 있는 형태로 변환하는 기법입니다.

**왜 필요한가?** 사용자가 챗봇에 입력하는 질문은 대부분 검색에 최적화되어 있지 않습니다. 특히 **멀티턴 대화** 에서 "그거 어떻게 해?", "이전 거랑 비교해줘" 같은 **대명사와 생략** 이 빈번하게 등장합니다. 이런 질문을 그대로 벡터 검색에 넣으면, "그거"가 무엇인지 모르기 때문에 관련 없는 문서가 반환됩니다.

**어떻게 동작하는가?** LLM에게 대화 이력과 최신 질문을 함께 제공하고, 대명사를 구체적 용어로 치환하고 생략된 맥락을 복원하여 **독립적으로 검색 가능한 쿼리** 로 변환하도록 지시합니다.

```
대화 이력:
  사용자: "Unity Catalog란 뭐야?"
  어시스턴트: "Unity Catalog는 Databricks의 통합 거버넌스 솔루션입니다..."

사용자 최신 질문: "그거 권한 설정은 어떻게 해?"
                   ↓ Query Rewrite
재작성된 쿼리: "Unity Catalog 권한(ACL) 설정 방법"
  → "그거"가 "Unity Catalog"로 치환되어 검색 가능한 형태가 됨
```

**한계와 트레이드오프:**

- LLM 호출이 **매 검색마다 추가** 되므로 지연 시간과 비용이 증가합니다 (일반적으로 200~500ms 추가)
- 재작성 과정에서 사용자 의도가 왜곡될 수 있으므로, 원래 질문도 함께 검색하는 **폴백(fallback) 전략** 을 권장합니다
- 단일 턴 대화에서는 효과가 제한적이며, **멀티턴 대화에서 가장 큰 효과** 를 발휘합니다

```python
def rewrite_query(question: str, chat_history: list = None) -> str:
    """대화 맥락을 반영하여 검색 쿼리를 재작성"""
    history_context = ""
    if chat_history:
        history_context = "\n".join(
            [f"사용자: {h['user']}\n어시스턴트: {h['assistant']}" for h in chat_history[-3:]]
        )

    prompt = f"""다음 대화 기록과 최신 질문을 바탕으로,
검색에 최적화된 독립적인 쿼리를 작성하세요.
대명사("그것", "이전 것")를 구체적인 용어로 바꾸세요.

대화 기록:
{history_context}

최신 질문: {question}

검색 최적화 쿼리:"""
    response = llm.invoke(prompt)
    return response.content

# 대화 맥락:
#   사용자: "Unity Catalog란 뭐야?"
#   어시스턴트: "Unity Catalog는 Databricks의 통합 거버넌스 솔루션입니다..."
#   사용자: "그거 권한 설정은 어떻게 해?"
# → 재작성: "Unity Catalog 권한(ACL) 설정 방법"
```

### Contextual Retrieval (Anthropic 제안)

**Contextual Retrieval** 은 Anthropic이 제안한 기법으로, 각 청크에 **전체 문서의 맥락 요약** 을 앞에 붙여(prepend) 청킹 과정에서 손실되는 문맥 정보를 보완합니다.

```python
def add_context_to_chunk(chunk_text: str, full_document: str) -> str:
    """각 청크에 전체 문서 문맥을 Prepend"""
    prompt = f"""다음은 전체 문서에서 추출한 하나의 청크입니다.
이 청크가 전체 문서에서 어떤 맥락에 위치하는지 간결하게 설명하세요 (2~3문장).

전체 문서 (요약):
{full_document[:2000]}

청크:
{chunk_text}

문맥 설명:"""
    response = llm.invoke(prompt)
    context = response.content

    # 문맥 요약을 청크 앞에 추가
    return f"[문맥: {context}]\n\n{chunk_text}"

# 예시:
# 원본 청크: "GRANT SELECT ON TABLE TO user@email.com"
# 문맥 추가 후: "[문맥: 이 청크는 Unity Catalog의 권한 관리 섹션에서
#               테이블 수준 접근 권한을 부여하는 SQL 명령어를 설명합니다.]
#               GRANT SELECT ON TABLE TO user@email.com"
```

{% hint style="info" %}
Contextual Retrieval은 청킹 단계에서 **한 번만** 수행하면 되므로, 검색 시점에 추가 LLM 호출이 발생하지 않습니다. 초기 인덱싱 비용은 증가하지만, 검색 품질 향상 효과가 큽니다. Anthropic의 벤치마크에서 **검색 실패율을 49% 감소** 시킨 것으로 보고되었습니다.
{% endhint %}

### Query Routing

**왜 필요한가?** 실제 기업 환경에서는 정보가 벡터 DB, SQL 데이터베이스, 웹, API 등 **여러 소스에 분산** 되어 있습니다. "지난 분기 매출"을 벡터 DB에서 검색하면 관련 문서는 찾을 수 있지만 정확한 숫자는 얻기 어렵고, "Delta Lake 최적화 방법"을 SQL DB에서 검색하면 아무 결과도 없습니다. Query Routing은 질문의 **의도를 분류** 하여 각 질문에 가장 적합한 데이터 소스로 자동 연결합니다.

**동작 원리:** LLM이 질문을 분석하여 (1) 수치/집계가 필요한 질문은 SQL DB로, (2) 개념 설명/방법론 질문은 벡터 DB로, (3) 최신 정보 질문은 웹 검색으로 라우팅합니다. 분류 기준은 프롬프트로 정의하며, 필요에 따라 Few-shot 예시를 추가하여 정확도를 높일 수 있습니다.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_databricks import ChatDatabricks

llm = ChatDatabricks(endpoint="databricks-claude-sonnet-4")

def route_query(question: str) -> dict:
    """질문 의도를 분류하여 적합한 데이터 소스로 라우팅"""
    prompt = f"""다음 질문을 분석하여 가장 적합한 데이터 소스를 선택하세요.

데이터 소스 옵션:
- VECTOR_DB: 일반 문서, 매뉴얼, FAQ 검색
- SQL_DB: 수치 데이터, 통계, 집계 쿼리 (매출, 건수 등)
- WEB_SEARCH: 최신 뉴스, 외부 기술 문서
- GENIE: Databricks Genie를 통한 자연어 SQL 쿼리

질문: {question}

JSON 형식으로 응답:
{{"source": "데이터소스명", "reason": "이유"}}"""

    response = llm.invoke(prompt)
    return eval(response.content)

# "지난 분기 매출이 얼마야?" → {{"source": "SQL_DB", "reason": "수치 집계 쿼리"}}
# "Delta Lake 최적화 방법은?" → {{"source": "VECTOR_DB", "reason": "기술 문서 검색"}}
# "오늘 나온 Databricks 블로그 있어?" → {{"source": "WEB_SEARCH", "reason": "최신 정보"}}
```

### 다중 쿼리 분해 (Query Decomposition)

**왜 필요한가?** 사용자의 질문이 여러 하위 주제를 포함하는 복합 질문일 때, 하나의 쿼리로 모든 정보를 검색하면 각 하위 주제에 대한 검색 정확도가 떨어집니다. 각 하위 질문에 대해 개별적으로 검색하면, 더 정확하고 완전한 정보를 수집할 수 있습니다.

**동작 원리:** LLM이 복합 질문을 분석하여 독립적으로 검색 가능한 2~4개의 하위 질문으로 분해합니다. 각 하위 질문에 대해 별도로 검색을 수행한 뒤, 결과를 병합하고 중복을 제거합니다. 최종적으로 모든 검색 결과를 LLM에 전달하여 원래의 복합 질문에 대한 종합적인 답변을 생성합니다. 이 기법은 앞서 다룬 Multi-Query와 유사하지만, Multi-Query가 "같은 의미를 다른 표현으로" 바꾸는 것이라면, Query Decomposition은 "다른 의미의 하위 질문들로 분해" 하는 것입니다.

```python
def decompose_query(question: str) -> list[str]:
    """복잡한 질문을 여러 하위 질문으로 분해"""
    prompt = f"""다음 질문을 검색 가능한 2~4개의 하위 질문으로 분해하세요.
각 하위 질문은 독립적으로 검색 가능해야 합니다.

원래 질문: {question}

하위 질문들 (하나씩 줄바꿈):"""
    response = llm.invoke(prompt)
    return [q.strip() for q in response.content.strip().split("\n") if q.strip()]

# "Databricks에서 Unity Catalog를 설정하고 Delta Live Tables로
#  데이터 파이프라인을 구축한 후 ML 모델을 배포하는 방법" →
#   1. "Unity Catalog 초기 설정 방법"
#   2. "Delta Live Tables 파이프라인 구축 방법"
#   3. "Databricks에서 ML 모델 배포 방법"

sub_questions = decompose_query(complex_question)
all_results = []
for sq in sub_questions:
    results = ensemble_retriever.invoke(sq)
    all_results.extend(results)

# 중복 제거 후 LLM에 전달
unique_results = deduplicate(all_results)
```
