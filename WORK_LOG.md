# 작업 로그 — 2026-03-31 ~ 2026-04-01

> 이 문서는 이번 세션에서 수행한 모든 작업, 발생한 문제, 원인, 해결 방법을 기록합니다.

---

## 세션 요약

| 항목 | 수치 |
|------|------|
| ** 총 변경 파일 수**| 190+ 파일 |
| ** 총 추가 줄 수**| 15,000+ 줄 |
| ** 신규 생성 문서**| 60+ 파일 |
| ** 신규 생성 디렉토리**| 15+ 디렉토리 |
| ** 병렬 Agent 실행**| 50+ 회 |

---

## 1. 수행한 작업 목록

### Phase 1: 신규 문서 생성

| 작업 | 파일 | 설명 |
|------|------|------|
| NLP 발전사 | `genai-concepts/nlp-evolution.md` | 규칙 기반 → 통계 → Word2Vec → RNN/LSTM → Transformer 역사 |
| MCP 인기 서버 | `mcp/popular-servers.md` | 카테고리별 40+ MCP 서버, 실전 시나리오 10선 |
| Agent 프레임워크 | `genai-concepts/agent-frameworks.md` | LangChain/LangGraph/CrewAI/OpenAI/AutoGen/Databricks 비교 |
| Agent UI 스택 | `genai-concepts/agent-ui-stack.md` | Streamlit/Gradio/Chainlit/Dash/FastAPI + Databricks Apps |
| 추론 모델 | `llm-basics/reasoning.md` | o1/o3/R1/Claude Extended Thinking |
| 멀티모달 | `llm-basics/multimodal.md` | Vision-Language 모델, 업종별 활용 |
| AI 규제 | `ai-proficiency/regulation.md` | EU AI Act, 한국 AI 기본법 |
| MLOps 03a | `03a-ml-trends.md` | ML 70년 역사, 최신 기법 |
| MLOps 03d | `03d-retraining-strategies.md` | 13 Part 재학습 전략 |
| Agent Landscape 6개 | `agent-landscape/*.md` | OpenAI/Anthropic/Google/AWS/Databricks/트렌드 |

### Phase 2: 기존 문서 전문가 심화

| 문서 | Before → After | 추가 내용 |
|------|---------------|---------|
| `llm-basics.md` | 497 → 926줄 | 학습 3단계, MoE, 추론 최적화, Emergent Abilities |
| `agent-architecture.md` | 556 → 902줄 | Memory, Planning, 안전성, 디버깅, 안티패턴 |
| `prompt-engineering.md` | 492 → 1,008줄 | 디버깅, 체이닝, 한국어 최적화, 노하우 10선 |
| `evaluation.md` | 439 → 751줄 | Retrieval 메트릭, 데이터셋 설계, Offline/Online |
| `a2a.md` | 449 → 786줄 | 보안, Python 구현, 설계 패턴 카탈로그 |
| `ai-proficiency.md` | 360 → 603줄 | 안티패턴, ROI 측정, 팀 스킬, 변화 관리 |
| `nlp-evolution.md` | 732 → 1,040줄 | CNN NLP, BPE, ULMFiT, Scaling Laws, RLHF |
| `security.md` | 49 → 476줄 | OWASP Top 10, 다층 방어, Agent 보안 |
| `memory.md` | 49 → 738줄 | Vector Search/Lakebase 코드, 솔루션 비교 |

### Phase 3: 서브메뉴 분리

9개 단일 파일 → 9개 디렉토리, 51개 서브페이지:
- `llm-basics/` (7개), `agent-architecture/` (6개), `nlp-evolution/` (6개)
- `prompt-engineering/` (5개), `evaluation/` (4개), `a2a-protocol/` (3개)
- `agent-frameworks-detail/` (4개), `agent-ui-detail/` (4개), `ai-proficiency/` (3개+1개)

### Phase 4: 전체 섹션 심화

| 섹션 | 추가 줄 |
|------|-------|
| Databricks Apps | +1,099 |
| Genie Space | +802 |
| Platform Comparison | +1,711 |
| Agent Bricks | +1,262 |
| RAG + Builder App | +1,514 |
| Genie Code + MCP | +1,197 |
| MLOps 핸즈온 | +1,026 |
| Advanced RAG (PDF 기반) | +1,011 |

### Phase 5: 구조 개편

- Builder App → AI Dev Kit 하위로 통합
- `advanced-retrieval.md` → 7개 서브페이지 분리
- Agent Landscape에 Databricks 별도 분리

---

## 2. 발생한 문제와 해결

### 문제 1: 한국어 볼드 렌더링 깨짐 (가장 빈번)

** 증상**: GitBook에서 `** 텍스트**` 가 `** 텍스트**` 로 렌더링되거나, 볼드가 적용되지 않고 `**` 가 그대로 노출

** 원인**: GitBook의 마크다운 파서가 한국어 문자와 `**` 사이에 스페이스가 없으면 볼드로 인식하지 못함. 한국어의 유니코드 특성상 `** 텍스트** 한글` 에서 닫는 `**` 뒤에 한글이 바로 오면 파서가 단어 경계를 인식하지 못함.

** 해결**:
- 규칙 정립: `<space>** 볼드텍스트**<space>` — 여는 `**` 앞과 닫는 `**` 뒤에 반드시 스페이스
- `**` 바로 안쪽에는 스페이스 넣지 않음: `** 텍스트**` (O), `** 텍스트**` (X)
- Python 정규식으로 전체 프로젝트 일괄 수정 (총 3회, 17,000+ 수정)

** 재발 원인**: Agent가 새 콘텐츠를 생성할 때마다 동일 패턴 재발 → 매 커밋 전 일괄 수정 스크립트 실행 필요

**CLAUDE.md에 규칙 추가**: 향후 자동 준수

```python
# 수정 스크립트
import re
# 여는 ** 뒤 스페이스 제거
new = re.sub(r'\*\* ([^\s*])', r'**\1', content)
# 닫는 ** 뒤 한글 앞 스페이스 추가
new = re.sub(r'\*\*([가-힣])', r'**\1', new)
```

---

### 문제 2: ASCII 다이어그램 렌더링 깨짐

** 증상**: 코드 블록 안의 박스 드로잉 문자(┌┐└┘│)가 GitBook에서 정렬이 깨짐

** 원인**: GitBook의 monospace 폰트가 한국어 문자와 영어 문자의 너비를 다르게 렌더링. 한국어는 전각(2칸), 영어는 반각(1칸)이라 박스 드로잉의 정렬이 무너짐.

** 해결**:
- 한국어 포함 ASCII 다이어그램 → 마크다운 테이블 또는 설명 텍스트로 교체
- 영어만 포함된 ASCII 다이어그램은 유지 (렌더링 정상)
- 21개 파일에서 교체 수행

**CLAUDE.md 기존 규칙**: "ASCII 다이어그램 사용 금지 → 테이블 또는 이미지 사용"이 이미 있었으나, 코드 블록 안에서는 허용된다고 오해한 Agent들이 계속 생성

---

### 문제 3: 테이블만 단독으로 배치 (설명 부재)

** 증상**: 테이블이 제목 바로 아래에 설명 없이 나열되어, 독자가 "이 테이블이 무엇을 보여주는가"를 파악하기 어려움

** 원인**: Agent가 콘텐츠를 생성할 때 테이블을 빠르게 나열하는 경향이 있음. "왜"와 "시사점"을 생략하는 패턴.

** 해결**:
- 전체 프로젝트에서 "naked table" 패턴 탐색 후 도입/시사점 문장 추가
- 11개 파일, 20+ 테이블에 설명 추가
- CLAUDE.md에 "테이블 전후 설명 필수" 규칙 추가

---

### 문제 4: 서브페이지 분리 후 링크 깨짐

** 증상**: 파일을 디렉토리 구조로 분리한 후, 다른 파일에서 참조하는 링크가 기존 경로(예: `a2a.md`)를 가리킴

** 원인**: 서브페이지 분리 작업이 병렬로 진행되면서, 일부 Agent가 다른 Agent의 분리 결과를 반영하지 못함. 특히 `agent-landscape/*.md` 에서 `../a2a.md`, `../agent-frameworks.md` 등 이전 경로 참조가 남아있었음.

** 해결**:
- 최종 리뷰에서 깨진 링크 7건 발견
- `sed` 일괄 치환으로 수정:
  - `../a2a.md` → `../a2a-protocol/README.md`
  - `../agent-frameworks.md` → `../agent-frameworks-detail/README.md`
  - `../agent-ui-stack.md` → `../agent-ui-detail/README.md`

** 예방책**: 파일 이동/분리 후 `grep -r "이전경로"` 로 잔여 참조 확인 필수

---

### 문제 5: "프리미티브" 등 전문 용어 사용

** 증상**: "3가지 프리미티브" 같은 표현이 비개발자에게 생소

** 원인**: 영어 기술 문서를 번역할 때 "primitive"를 그대로 "프리미티브"로 표기

** 해결**: 전체 프로젝트에서 "프리미티브" → "기본 구성 요소" / "핵심 구성 요소"로 일괄 교체

---

### 문제 6: Agent 작업 중 인터넷 끊김

** 증상**: 3개 파일 동시 분리 작업(agent-frameworks, agent-ui, ai-proficiency) 중 Agent 연결 실패

** 원인**: 장시간 작업으로 API 연결 타임아웃 또는 네트워크 불안정

** 해결**:
- 생성된 파일 확인: 대부분 생성 완료, `ai-proficiency/governance.md` 만 누락
- 수동으로 governance.md 생성 (원본에서 해당 섹션 복사)
- 원본 파일 3개 수동 삭제
- SUMMARY.md 수동 업데이트

** 교훈**: 대규모 병렬 작업은 3~5개 이하로 제한하는 것이 안전

---

### 문제 7: SUMMARY.md 동시 수정 충돌

** 증상**: 여러 Agent가 동시에 SUMMARY.md를 수정하려고 할 때 충돌 발생

** 원인**: 병렬 Agent들이 각자 SUMMARY.md에 메뉴 항목을 추가하면서 동시 쓰기 충돌

** 해결**:
- Agent 작업 완료 후 메인에서 SUMMARY.md를 한 번에 수정
- Agent에게는 "SUMMARY.md 수정은 별도 요청 시에만" 지시

---

## 3. CLAUDE.md에 추가한 규칙

이번 세션에서 발견한 문제들을 기반으로 다음 규칙을 추가:

1. ** 콘텐츠 품질 기준**: 모든 문서는 전문가(Academy) 수준. "왜 → 어떻게 → 활용 → 한계" 필수 포함.
2. ** 한국어 볼드 렌더링**: `<space>** 텍스트**<space>` 형태 필수.
3. ** 테이블 전후 설명 필수**: 테이블만 단독 나열 금지.
4. **ASCII 다이어그램 금지**: 테이블 또는 이미지 사용 (기존 규칙 재확인).

---

## 4. 최종 프로젝트 구조

```
02-enablement-blog/
├── README.md
├── SUMMARY.md
├── CLAUDE.md
├── WORK_LOG.md (이 파일)
│
├── platform-setup/
│   ├── aws/ (12개 파일)
│   └── azure/ (8개 파일)
│
├── guides/
│   ├── genie-space/ (8개 파일)
│   ├── genie-code/ (5개 파일)
│   ├── platform-comparison/ (8개 파일)
│   ├── agent-bricks/ (6개 파일)
│   ├── ai-dev-kit/ (6개 파일, Builder App 통합)
│   ├── apps/ (7개 파일)
│   ├── rag/
│   │   ├── concepts/ (6개 파일)
│   │   ├── advanced-retrieval/ (7개 파일, 분리)
│   │   └── 기타 (8개 파일)
│   ├── mcp/ (5개 파일)
│   └── genai-concepts/
│       ├── README.md
│       ├── llm-basics/ (9개 파일)
│       ├── agent-architecture/ (7개 파일)
│       ├── nlp-evolution/ (7개 파일)
│       ├── prompt-engineering/ (6개 파일)
│       ├── evaluation/ (5개 파일)
│       ├── a2a-protocol/ (4개 파일)
│       ├── agent-frameworks-detail/ (5개 파일)
│       ├── agent-ui-detail/ (5개 파일)
│       ├── ai-proficiency/ (4개 파일)
│       └── agent-landscape/ (7개 파일)
│
├── hands-on/
│   ├── predictive-maintenance/
│   │   ├── notebooks/ (14개 .py + _resources)
│   │   └── 가이드 (14개 .md)
│   └── smart-tv-vibe/
│       ├── notebooks/ (common, track-a/b/c)
│       └── 가이드 (9개 .md)
│
└── slides/ (GitHub Pages)
```

---

## 5. 향후 권장 작업

| 우선순위 | 작업 | 이유 |
|---------|------|------|
| 높음 | Lakebase 독립 가이드 | Smart TV 워크샵에서 사용하지만 독립 가이드 없음 |
| 높음 | Unity Catalog 심층 가이드 | 거버넌스가 핵심 차별점인데 독립 가이드 없음 |
| 중간 | Agent Landscape 벤더 페이지 분량 조정 | 500~750줄 페이지들이 많음 |
| 중간 | Fine-tuning 실전 가이드 | Mosaic AI Training 활용 |
| 낮음 | 실습 노트북 추가 | GenAI 개념 섹션에 runnable notebook |
| 낮음 | Structured Streaming 가이드 | 독립 개념 가이드 |

---

## 6. 커밋 히스토리

| 커밋 | 내용 |
|------|------|
| `827c3a4` | (세션 시작 시점) Add Builder App deployment guide |
| `e58b1ec` | Major content expansion: GenAI concepts, Agent landscape, MLOps updates |
| `13776cd` | Expert-level content expansion + rendering fixes |
| `7367511` | Comprehensive expert-level deepening across entire project |
| (다음 커밋) | Final review fixes: broken links, menu naming, advanced-retrieval split |
