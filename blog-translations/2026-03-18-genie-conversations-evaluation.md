# Genie Space에 대한 신뢰 구축: Benchmarks와 Ask for Review

**Benchmarks와 Request Review 기능으로 AI 데이터 분석가의 응답 정확도를 체계적으로 평가하고 검증합니다**

작성자: Hanlin Sun, Richard Tomlinson | 2024년 10월 16일

> **원문**: [Building Confidence in Your Genie Space with Benchmarks and Ask for Review](https://www.databricks.com/blog/building-confidence-your-genie-space-benchmarks-and-ask-review)

![Building Confidence in Genie Space Blog OG Image](https://www.databricks.com/sites/default/files/2024-11/building-confidence-in-your-genie-space-blog-og.png.png?v=1731084352)

---

**AI/BI Genie** 는 비즈니스 팀이 자연어를 통해 데이터에서 인사이트를 셀프 서비스로 얻을 수 있는 대화형 경험입니다. Genie는 조직의 데이터, 사용 패턴, 비즈니스 개념에 맞게 조율된 생성형 AI를 활용하며, 사용자 피드백으로부터 지속적으로 학습합니다. 이를 통해 비기술 사용자들은 숙련된 동료에게 질문하듯 자연스럽게 질문하고, 기업 데이터에서 직접 관련성 높고 정확한 응답을 받을 수 있습니다.

Genie space의 도입이 빠르게 확산됨에 따라, **사용자들이 제공되는 인사이트의 정확성에 대해 신뢰를 갖는 것** 이 필수적입니다. 이 신뢰는 Genie가 제공하는 인사이트를 바탕으로 가장 잘 정보에 입각한 의사결정을 내릴 수 있도록 하는 데 매우 중요합니다.

비즈니스 팀을 위해 Genie space를 작성하고 유지 관리하는 데이터 실무자들은 일반적으로 두 가지 핵심 요구사항을 언급합니다:

1. Genie space에서 유지 관리하는 지침(instructions)과 예시들이 전반적인 정확도를 효과적으로 향상시키는지 확인할 수 있는 능력
2. 요청 시 Genie가 생성한 응답이 정확한지 검증하고 그 피드백을 최종 사용자에게 전달할 수 있는 능력

이러한 요구사항을 해결하기 위해, AI/BI Genie에 반환된 답변의 정확성에 대한 신뢰를 높이는 두 가지 새로운 기능을 소개합니다:

- **Benchmarks** — Genie 작성자가 이제 테스트 질문을 생성하여 Genie space의 지침과 설정을 업데이트할 때 전반적인 정확도를 추적할 수 있습니다.
- **Request Review** — 최종 사용자가 이제 Genie 작성자에게 응답 검증 또는 수정을 요청하고, 확인 결과를 전달받을 수 있습니다.

---

## Benchmarks

Benchmarks(벤치마크)는 Genie 작성자가 Genie space의 정확도를 체계적으로 평가할 수 있게 해줍니다. 잘 구성된 벤치마크 질문 세트는 가장 자주 묻는 사용자 질문들을 포함해야 하며, 표현 방식의 변형을 2~3개 추가하는 것이 좋습니다. 그런 다음 작성자는 이 벤치마크를 시간이 지남에 따라 실행하여, space에 대한 편집이 전반적인 정확도를 효과적으로 향상시키는지 판단할 수 있습니다.

### Benchmarks 사용 방법

Benchmarks로 Genie space의 정확도를 더 잘 평가하려면 다음 단계를 따르세요:

**1. 준비 (Prepare)**

Genie space에 깔끔한 테이블과 메타데이터가 포함되어 있는지 확인합니다. 몇 가지 일반적인 사용자 질문을 수동으로 테스트하고, 기준 정확도를 높이기 위한 지침을 추가하는 것부터 시작합니다.

**2. Benchmarks 추가 (Add Benchmarks)**

추가하는 Benchmarks는 사용자들이 묻는 일반적인 질문의 다양한 표현과 버전을 반영해야 합니다. 예를 들어, 사용자들이 "올해 총 매출 기준 상위 10개 고객"을 자주 묻는다면, `"Top 10 customers by revenue FY2024"` 와 `"Show me top 10 customers this year by revenue"` 같은 몇 가지 버전을 벤치마킹하는 것이 도움이 됩니다. 그런 다음 벤치마크 질문에 정확하게 답하는 SQL 구문을 추가합니다. 이는 평가 함수가 각 질문에 대해 Genie의 응답을 기준(source of truth)과 비교하는 데 도움이 됩니다.

**3. Benchmarks 실행 및 평가 (Run Benchmarks + Evaluate)**

대표적인 Benchmarks 세트를 구성한 후, 'Run Benchmarks'를 클릭하여 모든 벤치마크 질문에 대해 Genie를 자동으로 평가합니다. 각 질문은 **Correct(정확)** 또는 **Needs Review(검토 필요)** 라는 평가 레이블을 받게 됩니다. Genie의 쿼리 결과가 벤치마크의 쿼리 결과와 정확히 일치하면 Correct로 표시됩니다.

**4. 개선 (Enhance)**

특정 질문을 더블클릭하여 Genie가 어디에서 개선이 필요한지 파악합니다. Genie space가 어려워하는 특정 질문을 파악한 후, space를 개선합니다. 예를 들어, Genie에게 "아시아 최고 영업 담당자"를 계산하는 방법을 가르치는 지침을 추가해야 한다는 것을 발견할 수 있습니다. 그런 다음 지침 페이지로 가서 이 질문에 올바르게 답하는 방법을 보여주는 예시 SQL 쿼리를 추가합니다.

**5. Benchmarks 재실행 (Rerun Benchmarks)**

Space의 지침을 개선한 후, Benchmarks 세트를 다시 실행하여 전반적인 정확도가 향상되었는지 확인합니다. Evaluations 탭에서 시간이 지남에 따른 Genie space의 정확도 변화를 추적할 수 있습니다. 최종 사용자들이 묻는 일반적인 질문들을 계속 추가하면서 Benchmark 질문을 확대해 나갑니다.

---

## Request Review

Genie는 비기술 사용자가 후속 질문을 통해 전문가의 도움 없이 데이터에서 새로운 인사이트를 얻을 수 있게 해주는 강력한 탐색적 데이터 분석 도구입니다. 그러나 Excel과 같은 다른 도구에서의 분석과 마찬가지로, 결과를 사실로 발표하기 전에 제2의 의견을 구하고 싶을 때가 있습니다.

**Request Review** 기능을 통해 최종 사용자는 이 검토 사이클을 Genie 내에서 직접 완료할 수 있습니다. Slack이나 Teams에서 스크린샷을 주고받으며 반복적인 커뮤니케이션을 할 필요가 없습니다.

### Request Review 사용 방법

**1. Request 버튼 클릭**

사용자가 검증하고 싶은 답변을 받으면 Request 아이콘을 클릭하여 검토를 시작할 수 있습니다. Genie space 관리자에게 자신의 요청을 설명하는 코멘트를 추가하는 것을 권장합니다.

**2. 관리자 검토 (Admin Review)**

요청이 전송된 후, Genie space 관리자는 기록(History) 페이지에서 이를 검토할 수 있습니다. 원래의 프롬프트, 생성된 SQL, 첨부된 코멘트를 확인하고, SQL을 정확하다고 표시하거나 비즈니스 사용자를 위해 수정할 수 있습니다.

**3. 요청자에게 통보 (Requestor Notified)**

관리자가 생성된 SQL을 검증하거나 수정한 후, 최종 사용자는 이 검증에 대한 알림을 받습니다. 그런 다음 기록(History) 페이지에서 이를 확인할 수 있습니다.

---

## 결론

Benchmarks와 Request Review의 도입으로, AI/BI Genie는 사용자들이 받는 답변의 정확성과 신뢰성에 대한 확신을 크게 강화합니다. Benchmarks는 시간이 지남에 따른 정확도 향상을 체계적으로 추적할 수 있게 하여, 지침 편집이 효과적인지 확인할 수 있습니다. Request Review는 사용자들이 중요한 응답을 검증하는 원활한 방법을 제공하여, Genie가 생성하는 인사이트에 대한 신뢰를 형성합니다. 이 두 가지 새로운 기능은 비즈니스 팀이 일상 업무에서 필요한 중요한 의사결정을 내리기 위해 Genie를 자신감 있게 활용할 수 있도록 역량을 강화합니다.

아직 Genie space를 만들지 않으셨다면 지금 시작해 보세요. [AI/BI Genie 공식 문서](https://docs.databricks.com/ko/ai-bi/index.html)를 꼭 읽어보시고, AI/BI Dashboards와 Genie가 실제로 어떻게 작동하는지 확인하려면 [데모](https://www.databricks.com/product/business-intelligence/genie)를 시청하고 [제품 투어](https://www.databricks.com/product/demos/databricks-ai-bi)를 체험해 보세요.

Databricks 팀은 항상 AI/BI Genie 경험을 개선하기 위해 노력하고 있으며, 여러분의 피드백을 기다리고 있습니다!

---

{% hint style="info" %}
**관련 자료**

이 블로그 포스트는 Genie space 평가의 기초 개념을 다룹니다. 더 심층적인 실전 사례로는 **[Genie Space를 프로덕션 수준으로 구축하는 방법](https://www.databricks.com/blog/how-build-production-ready-genie-spaces-and-build-trust-along-way)** 블로그를 참고하세요. 해당 포스트에서는 벤치마크 기반의 반복적 개발 방법론을 통해 0%에서 100% 정확도까지 도달하는 엔드투엔드 실전 사례를 자세히 다룹니다.
{% endhint %}
