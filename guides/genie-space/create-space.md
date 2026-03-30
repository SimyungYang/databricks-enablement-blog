# Space 생성하기

---

## Step 1: Genie Space 만들기

1. Databricks 워크스페이스 좌측 사이드바에서 **Genie**를 클릭합니다.
2. 우측 상단의 **New** 버튼을 클릭합니다.
3. 데이터 소스(테이블/뷰)를 선택합니다.
4. **Create** 버튼을 클릭합니다.

---

## Step 2: 기본 설정 구성

**Configure > Settings** 메뉴에서 다음을 설정합니다:

| 설정 항목 | 설명 |
|-----------|------|
| **Title** | Space 이름 (워크스페이스 브라우저에 표시) |
| **Default Warehouse** | 쿼리 실행에 사용할 SQL Warehouse 선택 |
| **Description** | Space 목적 설명 (Markdown 지원) |
| **Sample Questions** | 사용자에게 보여줄 예시 질문 |
| **Tags** | 조직/분류를 위한 태그 |
| **File Uploads** | CSV/Excel 파일 업로드 허용 여부 |

{% hint style="warning" %}
Description은 사용자가 Space를 열 때 가장 먼저 보는 텍스트입니다. Space의 목적, 다루는 데이터 범위, 사용 팁 등을 Markdown 형식으로 명확하게 작성하세요.
{% endhint %}

---

## Step 3: 데이터 객체 추가

1. **Configure > Data** 메뉴로 이동합니다.
2. **Add** 버튼으로 테이블/뷰를 추가합니다.
3. Overview 탭에서 컬럼 이름, 데이터 타입, 설명을 확인합니다.
4. Sample data 탭에서 실제 데이터를 미리 확인합니다.
5. 불필요한 테이블은 휴지통 아이콘으로 제거합니다.

{% hint style="tip" %}
테이블은 **5개 이하**로 시작하는 것을 권장합니다. 최대 30개까지 추가할 수 있지만, 적을수록 정확도가 높아집니다.
{% endhint %}
