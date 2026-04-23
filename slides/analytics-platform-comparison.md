---
marp: true
title: "클라우드 분석 플랫폼 비교 — Databricks vs Snowflake vs AWS vs GCP"
paginate: true
style: |
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
  :root {
    --db-orange: #FF3621; --db-dark: #1B3139; --db-text: #1B3139;
    --db-green: #00A972; --db-gray: #618794; --db-bg: #F9F7F4;
    --db-bg-light: #EEEDE9; --db-inactive: #DCE0E2; --db-accent: #032E61;
    --snow-blue: #29B5E8; --aws-orange: #FF9900; --gcp-blue: #4285F4;
  }
  section { font-family: 'DM Sans', -apple-system, sans-serif; font-size: 28px; padding: 60px 80px 44px; color: var(--db-text); background: var(--db-bg); line-height: 1.6; display: flex; flex-direction: column; justify-content: center; }
  section::after { content: attr(data-marpit-pagination); font-size: 11px; color: var(--db-gray); position: absolute; bottom: 28px; right: 50px; }
  section.cover { background: #fff; color: var(--db-dark); padding: 48px 70px; display: flex; flex-direction: column; justify-content: flex-start; position: relative; overflow: hidden; }
  section.cover::after { color: var(--db-inactive); }
  section.cover .logos { display: flex; align-items: center; gap: 16px; margin-bottom: 48px; }
  section.cover .title-box { border: 2.5px solid var(--db-dark); padding: 28px 36px; display: inline-block; margin-bottom: 28px; max-width: 720px; }
  section.cover .title-box h1 { font-size: 48px; color: var(--db-dark); margin: 0; line-height: 1.15; }
  section.cover .subtitle { color: var(--db-orange); font-size: 24px; font-weight: 500; line-height: 1.5; margin-bottom: auto; }
  section.cover .date-line { margin-top: auto; }
  section.cover .date-sep { width: 46px; height: 3px; background: var(--db-orange); margin-bottom: 6px; }
  section.cover .date { color: var(--db-orange); font-size: 14px; }
  section.cover .deco1 { position: absolute; right: -80px; top: -80px; width: 360px; height: 360px; border-radius: 50%; background: var(--db-bg-light); opacity: .55; }
  section.cover .deco2 { position: absolute; right: 50px; top: 50px; width: 240px; height: 240px; border-radius: 50%; background: #fff; opacity: .8; }
  section.cover .deco3 { position: absolute; right: -40px; bottom: -60px; width: 280px; height: 280px; border-radius: 50%; background: var(--db-bg-light); opacity: .35; }
  section.divider { background: var(--db-dark); color: #fff; padding: 60px 70px; }
  section.divider::after { color: rgba(255,255,255,0.3); }
  section.divider h1 { font-size: 40px; font-weight: 700; color: #fff; margin: 0 0 8px; }
  section.divider h2 { color: rgba(255,255,255,0.6); font-size: 20px; margin: 0; }
  h1 { font-size: 36px; font-weight: 700; color: var(--db-dark); margin: 0 0 6px; line-height: 1.25; flex-shrink: 0; }
  h2 { font-size: 18px; font-weight: 400; color: var(--db-gray); margin: 0 0 24px; flex-shrink: 0; }
  h3 { font-size: 20px; font-weight: 700; color: var(--db-dark); margin: 18px 0 8px; padding: 5px 14px; border-left: 4px solid var(--db-orange); background: rgba(255,54,33,0.04); border-radius: 0 6px 6px 0; }
  p { margin: 6px 0; color: var(--db-text); font-size: 22px; }
  ul { margin: 4px 0 4px 24px; padding: 0; }
  li { margin: 5px 0; line-height: 1.5; color: var(--db-text); font-size: 21px; }
  li::marker { color: var(--db-orange); }
  strong { color: var(--db-dark); font-weight: 700; text-decoration: underline; text-decoration-color: var(--db-orange); text-underline-offset: 4px; text-decoration-thickness: 2.5px; }
  em { font-style: normal; color: var(--db-gray); font-size: 16px; }
  blockquote { border: none; background: var(--db-dark); color: #fff; padding: 14px 24px; border-radius: 8px; margin: 14px 0; font-size: 19px; }
  blockquote p { color: #fff; font-size: 19px; }
  blockquote strong { color: var(--db-orange); text-decoration: none; }
  table { font-size: 17px; border-collapse: collapse; width: 100%; margin: 10px 0; }
  th { background: var(--db-dark); color: #fff; padding: 8px 14px; text-align: left; font-weight: 500; }
  td { padding: 7px 14px; border-bottom: 1px solid var(--db-bg-light); }
  tr:nth-child(even) td { background: rgba(0,0,0,0.02); }
  hr { border: none; border-top: 3px solid var(--db-orange); margin: 0 0 16px; width: 60px; }
  .cols { display: flex; gap: 40px; }
  .col { flex: 1; }
  .stat { font-size: 48px; font-weight: 700; color: var(--db-orange); line-height: 1.1; }
  .stat-label { font-size: 15px; color: var(--db-gray); margin-top: 4px; }
  .win { color: var(--db-green); font-weight: 700; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 13px; font-weight: 600; background: var(--db-orange); color: #fff; vertical-align: middle; }
  .highlight { background: rgba(255,54,33,0.06); border-radius: 6px; padding: 12px 18px; margin: 8px 0; border-left: 4px solid var(--db-orange); }
  .highlight p { font-size: 20px; margin: 4px 0; }
  .ref { font-size: 12px; color: var(--db-gray); position: absolute; bottom: 32px; left: 80px; }
---

<!-- _class: cover -->
<div class="deco1"></div><div class="deco2"></div><div class="deco3"></div>
<div class="logos">
<img src="https://www.databricks.com/wp-content/uploads/2022/06/db-nav-logo.svg" style="height:34px;">
</div>
<div class="title-box"><h1>클라우드 분석 플랫폼<br>비교 2026</h1></div>
<div class="subtitle">Databricks vs Snowflake vs AWS vs GCP<br>하나의 플랫폼에서 모든 데이터 & AI를 통합</div>
<div class="date-line"><div class="date-sep"></div><div class="date">2026 March</div></div>

---

<!-- _class: divider -->
# 왜 Databricks인가?
## 통합 플랫폼 · AI 접근성 · 오픈소스 & 멀티클라우드

---

# 핵심 차별화 포인트

---

### 통합 플랫폼

- DW + Data Lake + ML + GenAI — **하나의 플랫폼, 하나의 데이터 사본, 하나의 거버넌스**
- 데이터 복사 제거로 **스토리지 60~70% 절감**

### AI로 사라지는 학습 곡선

- **Genie Code** — 자연어 → SQL/Python 자동 생성 및 실행 <span class="badge">NEW</span>
- **AI Dev Kit** — VS Code에서 Agent 개발 → 원클릭 배포 <span class="badge">NEW</span>
- **Assistant** — 플랫폼 전반 실시간 코딩 지원

### 오픈소스 & 멀티클라우드

- Delta Lake, MLflow, Unity Catalog — **모두 오픈소스**
- AWS, Azure, GCP에서 **동일한 경험**

---

# 비교 대상 플랫폼

| 플랫폼 | 포지셔닝 | 핵심 특징 |
|--------|---------|----------|
| **Databricks** | Data Intelligence Platform | Lakehouse 아키텍처, 데이터+AI 통합의 유일한 선택 |
| **Snowflake** | AI Data Cloud | SQL 분석 중심 SaaS, ML/AI는 후발 주자 |
| **AWS Analytics** | 서비스 조합형 | Redshift + EMR + Glue + Athena, 높은 운영 복잡성 |
| **GCP Analytics** | 서버리스 중심 | BigQuery + Vertex AI, 엔터프라이즈 점유율 낮음 |

---

# 핵심 차별화 한눈에 보기

| 항목 | Databricks | Snowflake | AWS | GCP |
|------|-----------|-----------|-----|-----|
| DW + Lake 통합 | <span class="win">Lakehouse 네이티브</span> | SQL DW만 | 별도 서비스 | 별도 서비스 |
| AI / GenAI Agent | <span class="win">Agent Framework + Eval</span> | Cortex (SQL만) | Bedrock | Vertex AI |
| 통합 거버넌스 | <span class="win">UC (데이터+AI+모델)</span> | Horizon (데이터만) | 분산 (IAM+LF) | 분산 (IAM+Dataplex) |
| 멀티클라우드 | <span class="win">AWS/Azure/GCP</span> | AWS/Azure/GCP | AWS Only | GCP Only |
| 오픈소스 | <span class="win">Delta, MLflow, UC</span> | 독점 엔진 | 일부 OSS | 일부 OSS |
| 자연어 개발 | <span class="win">Genie Code + AI Dev Kit</span> | 미지원 | 미지원 | 미지원 |
| 벤더 종속 | <span class="win">최소 (고객 스토리지)</span> | 높음 (독점 포맷) | 클라우드 종속 | 클라우드 종속 |

---

# "학습 곡선? 이제는 옛말"

## Databricks의 AI 도구들이 모든 사용자의 진입장벽을 제거합니다

### Genie Code <span class="badge">NEW</span>

- 자연어 → SQL/Python 코드 **자동 생성 및 실행**
- Spark 몰라도 복잡한 분석을 수행

### AI Dev Kit <span class="badge">NEW</span>

- VS Code에서 Agent 개발 → 테스트 → 원클릭 배포
- MLflow Tracing으로 디버깅

### Databricks Assistant

- 플랫폼 전반 AI 어시스턴트
- `/fix` `/explain` `/optimize` 명령으로 실시간 코딩 지원

> **자연어만으로도** Databricks의 모든 기능을 활용할 수 있습니다

---

# End-to-End Data Journey

## 하나의 플랫폼에서 데이터 수집부터 AI Agent 배포까지

| 단계 | 도구 | 역할 |
|------|------|------|
| **수집** | Lakeflow Connect / Auto Loader | 외부 데이터 소스 자동 연결 |
| **변환** | SDP (선언적 파이프라인) | Bronze → Silver → Gold 자동화 |
| **분석** | Databricks SQL + Genie | SQL 분석 + 자연어 탐색 |
| **ML/AI** | MLflow + Agent Framework | 모델 학습/평가/에이전트 구축 |
| **서빙** | Model Serving | 실시간 추론 엔드포인트 |
| **앱** | Databricks Apps | 최종 사용자 웹 앱 |

<div class="highlight">
<p><strong>Unity Catalog</strong> — 전 과정 통합 거버넌스, 리니지 자동 추적</p>
<p><strong>Delta Lake</strong> — 오픈 포맷, ACID 트랜잭션, Time Travel, UniForm</p>
</div>

---

<!-- _class: divider -->
# 결론

---

# 어떤 플랫폼을 선택해야 하는가?

SQL 분석만 필요하다면 선택지가 있습니다.

하지만 **데이터와 AI를 하나의 플랫폼** 에서,
**멀티클라우드** 로, **오픈소스 기반** 으로,
**Genie Code** 와 **AI Dev Kit** 으로 누구나 접근 가능하게 —

> **Databricks Data Intelligence Platform**

<div class="ref">2026년 3월 기준 공개 정보 기반</div>
