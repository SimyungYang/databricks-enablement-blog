---
original_title: "AI/BI Genie is now Generally Available"
authors: "Databricks"
date: "2025-06-12"
category: "Product"
original_url: "https://www.databricks.com/blog/aibi-genie-now-generally-available"
translated_date: "2026-04-07"
note: "요청된 URL(introducing-genie-agent)은 404입니다. 'Genie Agent'(Deep Research/Agent Mode) 첫 공개 블로그인 'AI/BI Genie is now Generally Available'로 대체 번역합니다."
---

> **원문**: [AI/BI Genie is now Generally Available](https://www.databricks.com/blog/aibi-genie-now-generally-available)

---

# AI/BI Genie, 정식 출시(GA)

| 항목 | 내용 |
| --- | --- |
| **원문 제목** | AI/BI Genie is now Generally Available |
| **저자** | Databricks |
| **발행일** | 2025년 6월 12일 |
| **원문 URL** | https://www.databricks.com/blog/aibi-genie-now-generally-available |

---

![AI/BI Genie GA](https://www.databricks.com/sites/default/files/2025-06/DAIS25-AIBI-Genie-GA-OG-02.png?v=1749148389)

## 요약

- **AI/BI Genie가 정식 출시(GA)** 되었습니다. 자연어로 데이터 질문을 던지면 즉각적인 인사이트를 얻을 수 있습니다.
- **Genie Deep Research** 가 곧 출시됩니다. 리서치 플랜을 수립하고 여러 가설을 병렬로 분석하여, 결론에 대한 명확한 출처를 제시하는 복잡한 다단계 "왜(why)" 질문을 처리하도록 설계되었습니다.
- 차세대 Genie Knowledge Store와 Databricks One의 출시와 맞물려, AI/BI Genie는 조직 전반의 비즈니스 사용자에게 데이터 접근을 민주화하는 데 기여합니다.

---

![Genie Hero](https://www.databricks.com/sites/default/files/inline-images/Genie-Hero-1_0.gif?v=1749163689)

AI/BI Genie가 정식 출시(Generally Available)되어, 사용자가 자연어로 데이터에 관한 질문을 던지고 즉각적인 인사이트를 얻을 수 있게 되었습니다.

---

## Genie란 무엇인가?

현대 기업에서 비즈니스 의사결정자들이 데이터 인사이트를 원할 때, 보통 두 가지 방법 중 하나를 택합니다. 분석가에게 맞춤형 리포트를 요청하거나(느리고 병목이 생기기 쉬움), 직접 대시보드를 탐색하거나(복잡하고 자신이 원하는 답을 찾기 어려울 때가 많음)입니다.

AI/BI Genie는 이 문제를 해결합니다. Genie는 분석가가 특정 주제(예: 영업 파이프라인)에 집중한 Genie Space를 구성할 때, 데이터(테이블, 뷰 등)와 함께 시맨틱(메트릭 정의, 샘플 쿼리, 텍스트 지시사항, 인증된 자산 등)을 패키징하여 자연어 질의를 가능하게 합니다.

그 결과 비즈니스 사용자는 **자연어로 질문하고 데이터에서 즉각적인 인사이트를 얻을 수 있습니다.**

---

## 미리보기 이후 업데이트 내용

지난 6월 AI/BI Genie를 발표한 이후, Databricks는 Preview 고객들의 피드백을 바탕으로 더 많은 기능을 추가하고, 답변 품질을 높이며, 사용자 경험을 개선하는 데 집중해 왔습니다. 주요 업데이트 내용은 다음과 같습니다.

- **Unity Catalog Metric Views**: Genie는 Data Intelligence Platform 위에 네이티브로 구축되어 있으며, 이 기반을 계속 확장해 나가고 있습니다. 예를 들어, Unity Catalog Metrics 지원이 추가되어 고객이 거버넌스를 갖춘 신뢰할 수 있는 데이터 모델을 활용하여 중요한 사용 사례의 정확도를 보장할 수 있습니다. AI/BI Genie와 함께 Unity Catalog는 데이터와 시맨틱 모두에 대한 단일 정보 소스(Single Source of Truth) 역할을 하며, 중복된 모델링 작업이 필요 없어집니다.
- **Genie 파일 업로드를 통한 임시 분석**: 미리보기 기간 동안 발견한 공통적인 분석 패턴 중 하나는, 로컬 스프레드시트(예: 캠페인에서 얻은 리드 목록)와 Unity Catalog의 관리형 데이터셋(예: Salesforce 계정 및 연락처)을 결합하여 임시 작업을 완료해야 하는 필요성이었습니다. Genie 파일 업로드를 통해 Excel 또는 CSV 파일을 Genie에 드래그 앤 드롭하여, 자연어를 통한 포괄적인 분석을 완성할 수 있습니다.

또한 대시보드와 Genie가 서로 더 잘 연동됩니다. 모든 AI/BI Dashboard에는 내장된 Genie 버튼이 포함되어 있습니다. 개선된 시각화부터 최종 사용자가 분석을 안내받을 수 있는 재설계된 사용자 인터페이스에 이르기까지, 다양한 기타 향상 사항도 제공됩니다. Databricks는 GA 이후에도 이러한 높은 수준의 기능 속도를 유지할 계획이며, 출시 노트를 통해 업데이트 내용을 지속적으로 확인할 수 있습니다.

---

## Genie를 통한 실제 성과

고객사들이 Genie를 통해 거두고 있는 성과들이 계속 전해지고 있습니다.

> Genie는 HP 팀의 역량을 강화하는 방식을 바꾸고 있습니다. 직관적인 자연어 인터페이스를 통해 사용자들이 코딩 없이 즉시 핵심 데이터에 접근할 수 있도록 지원함으로써, 데이터 기반 인사이트를 더욱 빠르고 효율적으로 확보하고 있습니다.
>
> — Bruce Hillsberg, 부사장, 데이터 엔지니어링 & 인사이트, 기술 & 혁신, HP Inc.

> 사용자들이 분석가들에게 끊임없이 "지난해와 비교해 남서부 지역 매출이 어떻게 됐나요?"라고 묻고 있었습니다. 적절한 분석가를 찾아 헤매거나 올바른 답변을 받을 수 있을지 기다릴 필요 없이 그냥 Genie에게 물어볼 수 있다는 생각이 비즈니스 측면에서 매우 흥미롭습니다.
>
> — Shahmeer Mirza, 시니어 디렉터, 데이터, AI/ML 및 R&D, 7-Eleven

> 마케팅 및 재무 분야의 임원과 사업 부문 리더들이 Genie를 활용하여 평범한 영어로 필요한 데이터에 접근할 수 있습니다. 정말 놀랍습니다.
>
> — Felix Baker, 데이터 서비스 총괄, SEGA Europe

이 밖에도 Databricks에는 Genie를 통해 큰 성과를 거두고 있는 많은 고객사들이 있습니다.

---

## 차세대 Knowledge Store

![Knowledge Mining](https://www.databricks.com/sites/default/files/inline-images/Knowledge-mining-v1.gif?v=1749163689)

Genie의 핵심은 Knowledge Store입니다. 이는 Genie의 AI 시스템이 질문에 답할 때마다 참고하는 살아있는 시맨틱 모델입니다. Databricks는 이제 차세대 Knowledge Store를 출시합니다. 이를 통해 작성자들은 훨씬 적은 노력으로 훨씬 세밀한 수준에서 지식을 큐레이션할 수 있습니다.

작성자들은 컬럼 수준의 동의어 및 샘플 값, 기본 키/외래 키 조인이나 인증된 메트릭 등의 테이블 수준 컨텍스트를 포함하여 데이터 자산에 직접 지식을 추가할 수 있습니다. Genie의 복합 AI 시스템은 이 모든 신호를 활용하여 정확하고 의미 있는 응답을 생성합니다.

이러한 향상 기능에도 불구하고, 시맨틱 큐레이션은 여전히 번거로운 작업입니다. 이 과정을 훨씬 쉽게 만들기 위해 Genie는 이제 자동화된 지식 마이닝 및 추출 기능을 수행합니다.

### 지식 마이닝 (Knowledge Mining)

**지식 마이닝** 은 Genie가 Unity Catalog의 거버넌스 보장을 유지하면서, Unity Catalog의 계보(lineage)와 쿼리 히스토리를 분석하여 새로운 지시사항을 제안하거나 Knowledge Store로 승격할 가치가 있는 반복적인 패턴을 발견할 수 있도록 합니다. 이를 통해 Space 소유자의 수동 큐레이션 부담을 획기적으로 줄일 수 있습니다.

### 지식 추출 (Knowledge Extraction)

![Knowledge Extraction](https://www.databricks.com/sites/default/files/inline-images/Knowledge-extraction-v1.gif?v=1749163689)

또한 Databricks는 Knowledge Store를 부트스트랩할 기존 참조 자료가 없는 완전히 새로운 사용 사례에 Genie를 활용하는 많은 고객사들을 보유하고 있습니다. 이러한 케이스를 처리하기 위해, Genie의 **지식 추출** 기능을 강화하여 큐레이션이 일상적인 사용의 일부로 이루어지도록 했습니다.

모든 채팅 세션 중에 Genie는 시맨틱 정보를 추출하고, 간결한 지식 스니펫을 제안하며, 사용자가 승인하면 이를 Knowledge Store에 반영합니다. 내장된 활동 모니터링 및 피드백 루프와 결합되어, 일상적인 사용 자체가 주기적인 정비 없이도 Genie의 시맨틱 모델을 정확하게 유지하는 지속적인 학습 파이프라인이 됩니다.

---

## Genie Deep Research

![Deep Research](https://www.databricks.com/sites/default/files/inline-images/Deep-reasoning-v2.gif?v=1749346286)

Genie GA가 중요한 이정표이지만, Databricks는 AI 우선 접근법으로 BI를 재정의하는 여정을 멈추지 않습니다. **Genie Deep Research** 프리뷰를 발표하게 되어 기쁩니다. 이는 복잡한 다단계 질문을 처리하도록 설계된 Genie의 새로운 모드입니다.

기존 Genie는 단순한 데이터 조회("지난달 매출은?")나 계산 질문("Q1 대비 Q2 성장률은?")에 뛰어난 성능을 보여주었습니다. 그러나 "어떤 요인들이 지난 분기 수익 감소에 기여했는가?"와 같이 더 복잡한 "왜(why)" 질문에는 더 심층적인 분석이 필요합니다.

Databricks는 Genie Deep Research가 LLM 리서치의 최신 발전을 활용하여 이런 유형의 질문을 다룰 것이라고 예상합니다. 구체적으로는 리서치 플랜을 수립하고 여러 가설을 병렬로 분석한 뒤 결과를 요약하는 방식으로 진행됩니다. Genie의 나머지 기능과 마찬가지로, Deep Research도 정확하고 신뢰할 수 있는 결과를 제공하기 위해 Genie의 Knowledge Store를 기반으로 하고 확장할 것입니다. 또한 Genie는 도출한 결론에 대해 명시적인 출처를 제공하고, 진행 과정 중 수행된 작업을 손쉽게 살펴볼 수 있는 원클릭 경험도 제공할 것입니다.

Deep Research는 올 여름 말 Genie 고객들에게 실험적 기능으로 제공될 예정입니다.

---

## Databricks One을 통한 비즈니스 팀으로의 AI/BI Genie 확산

![Databricks One Genie](https://www.databricks.com/sites/default/files/inline-images/Databricks_One_Genie_v1_0.gif?v=1749163689)

고객들로부터 Genie를 광범위하게 배포할 때의 우려 사항 중 하나는, 지금까지 AI/BI에 접근하려면 기술적인 Databricks 워크스페이스를 탐색해야 했다는 점입니다. 이는 기술적이지 않은 비즈니스 사용자들에게 부담스럽게 느껴질 수 있습니다.

Data and AI Summit 발표의 일환으로, Databricks는 **Databricks One** 을 출시합니다. Databricks One은 조직의 모든 AI/BI 콘텐츠를 향한 단일 진입점을 제공하는 소비자 수준의 비즈니스 인텔리전스 앱입니다. 사용자들은 다음 작업을 손쉽게 수행할 수 있습니다.

- 자연어로 질문하고 데이터로부터 즉각적인 인사이트 받기
- 새로운 대시보드, Genie Space, 앱을 주제, 인기도, 작성자 기준으로 발견하기
- KPI를 추적하고 메트릭을 탐색하기 위한 AI/BI Dashboard 조회 및 상호작용
- 분석, AI, 워크플로우를 목적에 맞는 인터페이스로 결합한 Databricks Apps 활용

이 릴리스를 통해 비즈니스 사용자들은 수동 탐색이나 구전(tribal knowledge)에 의존하지 않고도 적합한 대시보드와 Genie Space를 발견하는 것이 더 쉬워집니다. 업데이트된 For You 페이지는 이제 최근 활동과 즐겨찾기를 보여주므로, 사용자들이 가장 많이 활용하는 콘텐츠에 항상 빠르게 접근할 수 있습니다. 또한 검색이 더욱 스마트해졌습니다.

---

## 지금 시작하기

AI/BI Genie 및 Dashboard는 현재 추가 라이선스 없이 Databricks SQL 고객에게 제공됩니다. 더 자세히 알아보려면 다음 자료들을 확인하세요.

- **문서**: 상세한 내용은 공식 문서에서 확인하세요.
- **데모**: 데모 비디오, 제품 투어, 핸즈온 튜토리얼을 통해 AI/BI 기능을 직접 확인하세요.
- **eBook**: Business Intelligence Meets AI eBook을 다운로드하세요.

기존 Databricks 고객이 아닌 경우, 무료 체험판에 가입하여 Genie 및 기타 Databricks 제품을 직접 경험해 볼 수 있습니다.

---

{% hint style="info" %}
**번역 노트**: 요청된 원문 URL `https://www.databricks.com/blog/introducing-genie-agent`는 현재 404(존재하지 않음) 상태이며, 아카이브에도 기록이 없습니다. "Genie Agent"는 Databricks Agent Bricks 제품군에서 Genie Space를 서브 에이전트로 활용하는 기능을 지칭하거나, Genie의 Deep Research(Agent Mode)를 가리킵니다. 이 번역은 Genie Agent Mode(Deep Research)가 처음 공개 발표된 블로그인 **"AI/BI Genie is now Generally Available"** (2025년 6월 12일)을 번역한 것입니다.
{% endhint %}
