# Module 6: GenAI & Agent Bricks - AI 에이전트 구축

## 이 가이드 사용 방법

>**이 교육 자료는 Claude Code (또는 Cursor)와 함께 사용합니다.**>
> 1. 터미널에서 프로젝트 디렉토리로 이동: `cd ~/smarttv-training`
> 2. Claude Code 실행: `claude`
> 3. 각 Step의 "**Claude에게 요청하기**" 박스 내용을 복사하여 Claude에게 붙여넣기
> 4. Claude가 코드를 생성하고 Databricks에서 실행합니다
> 5. 결과를 확인하고 궁금한 점은 바로 질문하세요
>
>** 이 모듈의 특별한 점:** 이전 모듈에서 만든 Gold 테이블을 활용하여
> GenAI 기반 개인화 추천 시스템과 Agent Bricks를 구축합니다.

---

## 학습 목표

- Databricks Vector Search를 활용한 콘텐츠 유사도 검색
- Foundation Model API를 통한 LLM 활용
- RAG(Retrieval-Augmented Generation) 패턴 구현
- Agent Bricks를 활용한 AI 에이전트 구축 (Knowledge Assistant, Genie, Supervisor)
- MLflow Tracing으로 에이전트 관찰성 확보

---

## 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│          Supervisor Agent (MAS)           │
│       "스마트TV 통합 어시스턴트"             │
├─────────────┬──────────────┬──────────────┬────────────────┤
│       │       │       │         │
│ Knowledge  │  Genie   │ 추천    │  광고 성과   │
│ Assistant  │  Space   │ Endpoint  │  분석 함수   │
│       │       │       │         │
│ TV 사용   │ SQL 기반   │ Vector    │ UC Function  │
│ 가이드 Q&A │ 데이터 탐색 │ Search +   │ 광고 KPI   │
│       │       │ LLM 추천   │ 자동 계산   │
│ (문서 RAG) │ (Gold 테이블)│ (개인화)   │ (SQL 함수)  │
├─────────────┴──────────────┴──────────────┴────────────────┤
│           Databricks Platform           │
│ Unity Catalog | Vector Search | Model Serving | MLflow   │
└─────────────────────────────────────────────────────────────┘
```

---

## Part A: Vector Search 기반 콘텐츠 추천

### Step 1: 콘텐츠 메타데이터 & 임베딩 테이블 생성

#### Claude에게 요청하기

```
개인화 콘텐츠 추천을 위한 콘텐츠 메타데이터 테이블을 만들어줘.

테이블: {catalog}.gold.content_metadata
레코드 수: 500개

컬럼:
- content_id: 고유 ID (content_001 ~ content_500)
- title: 콘텐츠 제목 (한국어 - 드라마, 예능, 뉴스 등 실제 느낌)
- content_type: live_tv, vod, app, fasttv
- channel_or_app: 채널명/앱명
- genre: 장르
- sub_genre: 세부 장르 (로맨스, 액션, 시사, 스포츠하이라이트 등)
- description: 콘텐츠 설명 (2~3문장, 한국어)
- target_audience: 타겟 시청층 (family, young_adult, male_30s, female_20s 등)
- language: 언어 (ko, en, ja 등)
- release_year: 출시년도
- rating: 평점 (1.0 ~ 5.0)
- tags: 키워드 태그 배열 (["로맨스", "20대", "트렌디"] 등)

description을 현실적으로 작성해줘. 이 텍스트가 Vector Search 임베딩에 사용됩니다.
생성 후 장르별 분포와 샘플 5건을 보여줘.
```

---

### Step 2: Vector Search 인덱스 생성

#### Claude에게 요청하기

```
콘텐츠 추천을 위한 Vector Search 인덱스를 만들어줘.

1. Vector Search Endpoint 생성 (없으면):
  - 이름: smarttv_vs_endpoint

2. content_metadata의 description 컬럼을 임베딩할 Delta Sync Index 생성:
  - 인덱스 이름: {catalog}.gold.content_search_index
  - 소스 테이블: {catalog}.gold.content_metadata
  - 임베딩 컬럼: description
  - 임베딩 모델: databricks-gte-large-en (또는 사용 가능한 모델)
  - 동기화 모드: TRIGGERED

생성 후 인덱스 상태를 확인해줘.
Vector Search가 뭔지, Delta Sync가 어떻게 동작하는지 설명도 해줘.
```

### 핵심 개념: Vector Search

```
┌──────────────────────────────────────────┐
│     Delta Sync Index         │
│                      │
│ 소스 테이블     Vector Index     │
│ (Delta Table)    (자동 동기화)     │
│                      │
│ ┌─────────┐    ┌──────────────┐   │
│ │content │──────→│ Embedding  │   │
│ │metadata │ Sync │ Vectors   │   │
│ │     │    │       │   │
│ │description───→ │ [0.1, 0.3,.. │   │
│ │     │    │ 0.7, 0.2]  │   │
│ └─────────┘    └──────────────┘   │
│              │        │
│           Similarity Search   │
│           "로맨스 드라마 추천"  │
│              ↓        │
│           Top-K 유사 콘텐츠   │
└──────────────────────────────────────────┘
```

---

### Step 3: 개인화 추천 함수 생성

#### Claude에게 요청하기

```
사용자 프로필 기반 개인화 콘텐츠 추천 함수를 Unity Catalog에 만들어줘.

함수: {catalog}.gold.recommend_content

입력:
- device_id (STRING): 디바이스 ID
- user_profile_id (STRING): 사용자 프로필 ID
- num_recommendations (INT, default 5): 추천 개수

로직:
1. gold.user_profiles에서 해당 사용자의 프로필 조회
  (favorite_genre, top3_genres, preferred_time_slot, preferred_ad_category)
2. 사용자 프로필을 자연어 설명으로 변환
  예: "로맨스, 드라마를 좋아하는 저녁 시간대 시청자"
3. Vector Search로 유사한 콘텐츠 검색
4. Foundation Model API (DBRX 또는 Llama)로 추천 이유 생성
5. 결과를 JSON으로 반환: [{content_id, title, genre, score, reason}]

먼저 이 로직을 SQL 쿼리로 테스트하고, 잘 동작하면 UC Function으로 등록해줘.
특정 사용자 1명에 대해 추천 결과를 보여줘.
```

---

### Step 4: Foundation Model API 활용

#### Claude에게 요청하기

```
Foundation Model API를 직접 활용해서 콘텐츠 추천 설명을 생성해볼게.

1. 현재 워크스페이스에서 사용 가능한 Foundation Model 목록을 보여줘

2. ai_query 함수를 사용해서 추천 이유를 생성해줘:
  SELECT ai_query(
   'databricks-meta-llama-3-3-70b-instruct',
   CONCAT(
    '당신은 Smart TV의 콘텐츠 추천 AI입니다. ',
    '사용자 프로필: ', user_profile_description,
    ' 추천 콘텐츠: ', content_title,
    ' 이 콘텐츠를 추천하는 이유를 한국어로 2문장으로 설명해주세요.'
   )
  ) as recommendation_reason

3. gold.user_profiles에서 랜덤 5명의 사용자에 대해 실행하고 결과를 보여줘

ai_query가 어떻게 동작하는지, 어떤 모델들을 사용할 수 있는지 설명해줘.
```

---

## Part B: Agent Bricks - AI 에이전트 구축

### Step 5: Knowledge Assistant 생성 - TV 사용 가이드

#### Claude에게 요청하기

```
Agent Bricks의 Knowledge Assistant를 만들어볼게.
Smart TV 사용 가이드 Q&A 봇을 만들자.

=== Step 5-1: 문서 데이터 준비 ===
먼저 Unity Catalog Volume에 TV 사용 가이드 문서를 생성해줘.

볼륨: {catalog}.gold.tv_guide_docs

아래 주제의 마크다운 문서 5개를 생성해줘 (각 500~1000자):

1. fasttv_guide.md - FastTV 사용 가이드
  - FastTV란 무엇인지, 채널 목록, 즐겨찾기 설정법
  - 무료 콘텐츠 이용 방법

2. personalization_guide.md - 개인화 설정 가이드
  - 사용자 프로필 생성/전환 방법
  - 추천 알고리즘 설명 (시청 이력 기반)
  - 관심사 직접 설정 방법

3. ad_settings_guide.md - 광고 설정 및 개인정보
  - 맞춤형 광고 설정/해제 방법
  - 광고 데이터 수집 범위
  - 개인정보 보호 설정

4. voice_control_guide.md - 음성 제어 가이드
  - ThinQ AI 음성 명령어 목록
  - "채널 변경", "볼륨 조절", "앱 실행" 등
  - 자주 묻는 질문

5. troubleshooting_guide.md - 문제 해결 가이드
  - 화면이 안 나올 때
  - 인터넷 연결 문제
  - 앱 오류 해결법
  - 리모컨 페어링

문서를 Volume에 업로드해줘.
```

#### Claude에게 요청하기 (계속)

```
=== Step 5-2: Knowledge Assistant 생성 ===
이제 업로드한 문서로 Knowledge Assistant를 만들어줘.

이름: SmartTV Guide Assistant
설명: Smart TV 사용법과 FastTV에 대한 질문에 답변하는 AI 어시스턴트

Instructions:
- 한국어로 답변
- 문서에 있는 내용만 기반으로 답변 (환각 방지)
- 친절하고 단계별로 설명
- 문서에 없는 내용이면 "해당 정보를 찾을 수 없습니다. Smart TV OEM 고객센터(1544-7777)에 문의해주세요" 안내

생성 후 다음 질문으로 테스트해줘:
1. "FastTV에서 무료로 볼 수 있는 채널이 뭐야?"
2. "맞춤형 광고를 끄고 싶은데 어떻게 해?"
3. "리모컨이 안 되는데 어떻게 해야 돼?"

각 답변의 품질도 평가해줘.
```

### 핵심 개념: Knowledge Assistant

```
┌──────────────────────────────────────────┐
│     Knowledge Assistant        │
│                      │
│ 사용자 질문                │
│ "FastTV에서 무료 채널 뭐 있어?"      │
│     │                 │
│     ▼                 │
│ ┌─────────────┐   ┌──────────────┐  │
│ │ Instructed │────→│ UC Volume  │  │
│ │ Retriever  │   │ Documents  │  │
│ │ (검색)   │   │ (5개 가이드) │  │
│ └──────┬──────┘   └──────────────┘  │
│     │                 │
│     ▼                 │
│ ┌──────────────┐             │
│ │ LLM 답변   │             │
│ │ 생성     │             │
│ │ (문서 기반)  │             │
│ └──────────────┘             │
│                      │
│ "FastTV에서는 뉴스, 스포츠, 영화 등    │
│  100개 이상의 무료 채널을 제공합니다..."  │
└──────────────────────────────────────────┘
```

---

### Step 6: Genie Space 생성 - 데이터 탐색

#### Claude에게 요청하기

```
Agent Bricks의 Genie Space를 만들어서
비즈니스 사용자가 자연어로 스마트TV 데이터를 탐색할 수 있게 해줘.

Genie Space 이름: SmartTV Analytics

연결 테이블:
- {catalog}.gold.daily_viewing_summary
- {catalog}.gold.user_profiles
- {catalog}.gold.ad_performance
- {catalog}.gold.content_rankings

Instructions:
- 한국어 질문을 이해하고 SQL로 변환
- 결과를 비즈니스 관점에서 해석
- 가능하면 시각화 제안

Sample Questions (사용자 온보딩용):
1. "이번 달 가장 인기 있는 콘텐츠 Top 10은?"
2. "주말과 평일의 시청 패턴 차이를 보여줘"
3. "FastTV 광고 중 CTR이 가장 높은 광고 형식은?"
4. "Korea 지역의 프라임타임 시청률 추이는?"
5. "premium 티어 사용자의 시청 행동이 entry 사용자와 어떻게 달라?"

Genie Space 생성 후 위 샘플 질문 중 2개로 테스트해줘.
Genie Space가 어떤 SQL을 생성하는지도 보여줘.
```

### 핵심 개념: Genie Space

```
┌──────────────────────────────────────────┐
│      Genie Space          │
│                      │
│ "이번 달 인기 콘텐츠 Top 10은?"     │
│     │                 │
│     ▼                 │
│ ┌─────────────┐   ┌──────────────┐  │
│ │ NL → SQL  │────→│ Gold Tables │  │
│ │ 변환 엔진  │   │ (Unity Cat.) │  │
│ └──────┬──────┘   └──────────────┘  │
│     │                 │
│     ▼                 │
│ SELECT channel_or_app,          │
│     SUM(daily_unique_viewers) as total │
│ FROM gold.content_rankings        │
│ WHERE viewing_date >= '2025-02-01'    │
│ GROUP BY 1 ORDER BY 2 DESC LIMIT 10   │
│     │                 │
│     ▼                 │
│ ┌──────────────┐             │
│ │ 결과 + 해석  │             │
│ │ "Netflix가 1위, YouTube가 2위..."   │
│ └──────────────┘             │
└──────────────────────────────────────────┘
```

---

### Step 7: UC Function 생성 - 광고 성과 분석

#### Claude에게 요청하기

```
Supervisor Agent에서 사용할 UC Function을 만들어줘.
광고 성과를 자동 분석하는 함수야.

함수: {catalog}.gold.analyze_ad_performance

입력:
- advertiser (STRING): 광고주명 (NULL이면 전체)
- date_from (STRING): 시작일
- date_to (STRING): 종료일

반환: STRING (JSON 형태의 분석 결과)

분석 내용:
1. 기간 내 총 노출/클릭/전환 수
2. CTR, CVR 계산
3. 총 광고비 및 CPC, CPA
4. 광고 형식별 성과 비교
5. 시간대별 효율 분석
6. 전주/전월 대비 변화율

함수를 생성하고 테스트해줘:
- analyze_ad_performance('쿠팡', '2025-02-01', '2025-02-28')
- analyze_ad_performance(NULL, '2025-02-01', '2025-02-28')

결과를 보여주고, 이 함수가 Supervisor Agent에서 어떻게 활용되는지 설명해줘.
```

---

### Step 8: Supervisor Agent 생성 - 통합 어시스턴트

#### Claude에게 요청하기

```
이제 모든 에이전트를 통합하는 Supervisor Agent를 만들어줘.

이름: SmartTV 통합 어시스턴트
설명: Smart TV 관련 사용 가이드, 데이터 분석, 콘텐츠 추천, 광고 성과를 통합 지원하는 AI 어시스턴트

서브 에이전트:
1. TV 사용 가이드 (Knowledge Assistant)
  - 위에서 만든 "SmartTV Guide Assistant"
  - 설명: "TV 사용법, FastTV 가이드, 문제 해결 등 스마트TV 사용 관련 질문 답변"

2. 데이터 분석 (Genie Space)
  - 위에서 만든 "SmartTV Analytics"
  - 설명: "시청 데이터, 사용자 행동, 광고 성과 등 데이터 기반 질문에 SQL로 답변"

3. 광고 성과 분석 (UC Function)
  - 위에서 만든 analyze_ad_performance 함수
  - 설명: "특정 광고주나 기간의 광고 성과를 상세 분석"

Instructions:
 당신은 Smart TV의 스마트TV 통합 AI 어시스턴트입니다.

 라우팅 규칙:
 1. TV 사용법, 설정, 문제해결 질문 → TV 사용 가이드
 2. 데이터 조회, 통계, 트렌드 질문 → 데이터 분석 (Genie)
 3. 광고 성과 분석 요청 → 광고 성과 분석 함수

 한국어로 답변하고, 필요시 여러 서브에이전트를 조합하여 답변하세요.

Supervisor Agent를 생성하고 다음 질문으로 테스트해줘:
1. "FastTV에서 무료 채널 목록 알려줘" (→ KA 라우팅)
2. "이번 주 시청률 Top 5 보여줘" (→ Genie 라우팅)
3. "쿠팡 광고 2월 성과 어때?" (→ UC Function 라우팅)
4. "premium 사용자의 광고 반응이 좋은 시간대와 그 시간에 추천할 콘텐츠는?" (→ 복합 라우팅)

각 질문이 어디로 라우팅되는지, 답변 품질은 어떤지 보여줘.
```

### 핵심 개념: Supervisor Agent (MAS)

```
┌──────────────────────────────────────────────────┐
│       Supervisor Agent           │
│     "SmartTV 통합 어시스턴트"        │
│                          │
│ 사용자: "쿠팡 광고 2월 성과 어때?"        │
│     │                     │
│     ▼                     │
│ ┌──────────────┐                 │
│ │ Router    │ "광고 성과" → UC Function    │
│ │ (라우팅 엔진) │ "사용법"  → Knowledge Asst.  │
│ │       │ "데이터"  → Genie Space    │
│ └──────┬───────┘                 │
│     │                     │
│  ┌────┴────┬────────────┬──────────────┐    │
│  ▼     ▼      ▼       ▼    │
│ ┌────┐ ┌──────┐ ┌──────────┐ ┌──────────┐ │
│ │ KA │ │Genie │ │UC Func. │ │Endpoint │ │
│ │  │ │Space │ │(광고분석)│ │(추천)  │ │
│ └────┘ └──────┘ └──────────┘ └──────────┘ │
│             │             │
│             ▼             │
│ "쿠팡의 2월 광고 성과: CTR 3.2%, 노출 15,432건, │
│  CPC $0.02, 전월 대비 CTR 15% 상승..."     │
└──────────────────────────────────────────────────┘
```

---

### Step 9: MLflow Tracing으로 에이전트 모니터링

#### Claude에게 요청하기

```
Supervisor Agent의 동작을 MLflow Tracing으로 모니터링해줘.

1. MLflow Experiment 생성: /{catalog}/agent_traces

2. Supervisor Agent에 여러 질문을 보내고 trace를 수집해줘:
  - "FastTV 인기 채널 추천해줘"
  - "지난 주 광고 수익이 제일 높은 시간대는?"
  - "리모컨 문제가 있는데, 관련 이슈가 많이 보고되나?"

3. 수집된 trace에서 다음을 분석해줘:
  - 각 질문의 라우팅 경로
  - 응답 시간 (latency)
  - 토큰 사용량
  - 어떤 서브에이전트가 호출되었는지

4. 라우팅 정확도를 평가해줘:
  - 의도한 서브에이전트로 올바르게 라우팅되었는지
  - 잘못된 라우팅이 있다면 어떻게 개선할 수 있는지

MLflow Tracing이 왜 중요한지, 프로덕션 에이전트 운영에 어떻게 활용하는지 설명해줘.
```

---

### Step 10: Agent Evaluation - 에이전트 품질 평가

#### Claude에게 요청하기

```
Supervisor Agent의 품질을 체계적으로 평가해줘.

1. 평가 데이터셋 생성 (10개 질문):
  각 질문에 대해 expected_response와 expected_routing을 정의

  예시:
  - question: "FastTV에서 영화 채널 어떻게 찾아?"
   expected_routing: "knowledge_assistant"
   expected_facts: ["FastTV", "채널 가이드", "영화"]

  - question: "이번 달 CTR이 가장 높은 광고주는?"
   expected_routing: "genie_space"
   expected_facts: ["CTR", "광고주명", "수치"]

2. mlflow.evaluate()로 평가 실행:
  - 라우팅 정확도 (routing_accuracy)
  - 답변 관련성 (relevance)
  - 근거 기반 답변 (groundedness)
  - 안전성 (safety)

3. 평가 결과를 요약하고 개선 포인트를 제안해줘.

Agent Evaluation의 전체 워크플로우와
프로덕션에서 지속적으로 품질을 관리하는 방법을 설명해줘.
```

---

## Part C: 프로덕션 배포 (선택)

### Step 11: Databricks App으로 배포

#### Claude에게 요청하기

```
Supervisor Agent를 Databricks App으로 배포해줘.
사용자가 웹 브라우저에서 대화할 수 있는 챗봇 UI를 만들자.

앱 이름: smarttv-demo-assistant
프레임워크: Gradio (간단한 챗봇 UI)

기능:
- 채팅 인터페이스 (한국어)
- Supervisor Agent 엔드포인트 호출
- 대화 히스토리 유지
- 사이드바에 샘플 질문 목록 표시

배포 후:
1. 앱 URL 확인
2. 샘플 질문으로 테스트
3. 동작 확인

앱을 생성하고 배포해줘.
```

---

## Agent Bricks 프로젝트 관리 모범사례

### 프로젝트 구조 추천

```
smarttv-agents/
├── databricks.yml          # Asset Bundle 설정
├── resources/
│  ├── knowledge_assistants/
│  │  └── tv_guide_ka.yml     # KA 정의
│  ├── genie_spaces/
│  │  └── analytics_genie.yml   # Genie 정의
│  ├── functions/
│  │  └── ad_performance.sql    # UC Function 정의
│  └── supervisors/
│    └── main_supervisor.yml   # Supervisor 정의
├── documents/
│  ├── tv_guide/          # KA용 문서
│  └── evaluation/         # 평가 데이터셋
├── tests/
│  ├── test_routing.py       # 라우팅 테스트
│  ├── test_quality.py       # 품질 테스트
│  └── eval_dataset.json      # 평가 데이터
├── monitoring/
│  └── dashboard.sql        # 모니터링 대시보드
└── environments/
  ├── dev.yml           # 개발 환경
  ├── staging.yml         # 스테이징 환경
  └── prod.yml           # 프로덕션 환경
```

### 환경별 관리

| 환경 | 카탈로그 | 용도 |
|------|---------|------|
| dev | smarttv_dev | 개발/실험 |
| staging | smarttv_staging | 통합 테스트 |
| prod | smarttv_prod | 프로덕션 서비스 |

### CI/CD 파이프라인

```
코드 Push → 린트/검증 → 평가 실행 → Staging 배포 → 품질 게이트 → Prod 배포
              │              │
           mlflow.evaluate()      라우팅 정확도 > 95%
           품질 점수 체크       응답 시간 < 3초
```

### 모니터링 체크리스트

- [ ] MLflow Tracing 활성화 (모든 에이전트 호출 기록)
- [ ] 라우팅 정확도 대시보드
- [ ] 응답 시간 모니터링
- [ ] 토큰 사용량 & 비용 추적
- [ ] 사용자 피드백 수집 (thumbs up/down)
- [ ] 주간 품질 리포트 자동 생성

---

## 학습 정리

| 개념 | 실습 내용 |
|------|-----------|
|**Vector Search**| 콘텐츠 임베딩, Delta Sync Index, 유사도 검색 |
|**Foundation Model API**| ai_query로 LLM 호출, 추천 이유 생성 |
|**Knowledge Assistant**| 문서 기반 Q&A 봇 (RAG) |
|**Genie Space**| 자연어 → SQL 데이터 탐색 |
|**UC Function**| 재사용 가능한 분석 함수 |
|**Supervisor Agent**| 멀티에이전트 오케스트레이션 |
|**MLflow Tracing**| 에이전트 관찰성, 디버깅 |
|**Agent Evaluation**| 체계적 품질 평가 (라우팅, 관련성, 근거성) |

---

## 비즈니스 가치

이 GenAI 시스템을 통해 Smart TV는:

1.** 고객 지원 자동화**→ KA가 TV 사용법 질문의 80% 자동 응답
2.** 데이터 민주화**→ Genie로 비기술 직원도 데이터 분석 가능
3.** 광고 수익 최적화**→ AI 기반 광고 성과 분석으로 FastTV 수익 극대화
4.** 개인화 경험**→ Vector Search + LLM으로 사용자별 맞춤 콘텐츠 추천
5.** 통합 인텔리전스**→ Supervisor Agent가 모든 기능을 하나로 통합

---

## 참고 자료

- [Agent Bricks 공식 문서](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/)
- [Vector Search 문서](https://docs.databricks.com/aws/en/generative-ai/vector-search/)
- [Foundation Model APIs](https://docs.databricks.com/aws/en/machine-learning/model-serving/)
- [MLflow Tracing 문서](https://mlflow.org/docs/latest/tracing.html)
- [AI Dev Kit GitHub](https://github.com/databricks-solutions/ai-dev-kit)
