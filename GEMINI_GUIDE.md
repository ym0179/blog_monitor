# 🤖 Gemini AI 통합 가이드

네이버 블로그 크롤링 + Gemini AI 분석으로 투자 콘텐츠를 자동 생성합니다.

## ✨ 주요 기능

1. **특정 카테고리 크롤링** - 카테고리 번호로 최근 N일 내 글만 선택적으로 크롤링
2. **제목 별도 추출** - `div.se-title-text`에서 제목 추출
3. **날짜 필터링** - "yyyy. mm. dd." 형식의 날짜로 최근 글만 필터링
4. **엑셀 저장** - title, content, date, url을 엑셀로 저장
5. **Gemini AI 분석** - 크롤링한 글을 바탕으로 투자 콘텐츠 자동 생성

---

## 🚀 빠른 시작 (Google Colab)

### 1단계: 패키지 설치

```python
!pip install -q google-colab-selenium beautifulsoup4 openpyxl google-generativeai
```

### 2단계: Gemini API 키 발급

1. https://makersuite.google.com/app/apikey 접속
2. "Create API Key" 클릭
3. API 키 복사

### 3단계: 설정

```python
# 크롤링 설정
BLOG_ID = "yminsong"        # 블로그 ID
CATEGORY_NO = 31            # 카테고리 번호
DAYS = 14                   # 최근 며칠 이내 글

# Gemini API 키
GEMINI_API_KEY = "여기에-API-키-입력"
```

### 4단계: 실행

#### 방법 1: Jupyter 노트북 사용 (추천)

1. `blog_crawler_gemini.ipynb`를 Google Colab에 업로드
2. 순서대로 셀 실행
3. 자동으로 엑셀 파일 & 분석 결과 다운로드

#### 방법 2: Python 스크립트 사용

```python
!python blog_crawler_with_gemini.py
```

또는 코드 내에서:

```python
from blog_crawler_with_gemini import main

main(
    blog_id="yminsong",
    category_no=31,
    days=14,
    gemini_api_key="your-api-key-here"
)
```

---

## 📋 사용 예시

### 예시 1: 카테고리 번호 찾기

네이버 블로그에서 카테고리 페이지에 들어가면 URL에서 확인할 수 있습니다:

```
https://blog.naver.com/PostList.naver?blogId=yminsong&categoryNo=31
                                                                  ^^
                                                         카테고리 번호
```

또는 HTML에서:

```html
<input type="hidden" value="31" name="categoryNo">
                             ^^
                      카테고리 번호
```

### 예시 2: 날짜 필터링

날짜 형식: `"yyyy. mm. dd."` (띄어쓰기 주의!)

```
2025. 11. 14.  ✅ 올바른 형식
2025.11.14     ❌ 잘못된 형식
```

기본값은 최근 14일이며, 원하는 기간으로 변경 가능:

```python
DAYS = 7   # 최근 7일
DAYS = 30  # 최근 30일
```

### 예시 3: 출력 형식

#### 엑셀 파일 (`naver_blog_posts.xlsx`)

| title | content | date | url |
|-------|---------|------|-----|
| 배당 투자는 이렇게 하셔요 | 와이민입니다... | 2025. 11. 14. | https://... |
| 뛰어난 경영자들 시리즈 | ... | 2025. 10. 27. | https://... |

#### Gemini 분석 결과 (`gemini_analysis.txt`)

```markdown
# 미국 개미들의 투자노트

## 1. 금주의 가장 뜨거운 질문
배당 투자 vs 성장주 투자, 어느 것이 더 나을까?

## 2. 이번 주 집중 분석
...
```

---

## 🔧 고급 사용법

### 커스텀 프롬프트

프롬프트를 수정하여 원하는 형식의 콘텐츠를 생성할 수 있습니다:

```python
prompt = """
당신은 전문 투자 애널리스트입니다.
아래 블로그 글들을 분석하여 다음 형식으로 요약해주세요:

1. 핵심 투자 아이디어 3가지
2. 위험 요소 분석
3. 투자 전략 제안

[글 내용]
{formatted_content}
"""
```

### 여러 카테고리 동시 크롤링

```python
categories = [31, 32, 33]  # 여러 카테고리

all_posts = []
for cat_no in categories:
    posts = crawl_category_posts("yminsong", cat_no, days=14)
    all_posts.extend(posts)

# 엑셀 저장
save_to_excel(all_posts, 'multi_category_posts.xlsx')
```

### 크롤링 속도 조절

```python
# extract_full_post 함수에서 대기 시간 조절
time.sleep(3)  # 기본: 3초
time.sleep(5)  # 느린 네트워크: 5초
time.sleep(1)  # 빠른 네트워크: 1초
```

---

## 📊 워크플로우

```
1. 카테고리 페이지 접속
   ↓
2. 최근 N일 내 글 목록 추출
   ↓
3. 각 글 URL로 접속
   ↓
4. 제목 + 본문 추출
   ↓
5. 엑셀 저장
   ↓
6. Gemini API로 분석
   ↓
7. 투자 콘텐츠 생성
```

---

## 🎯 Gemini 프롬프트 구조

현재 사용 중인 프롬프트는 "미국 개미들의 투자노트" 형식:

### 1. 금주의 가장 뜨거운 질문 (The Big Question)
- 논쟁적인 주제 제시
- 독자의 즉각적인 관심 유도

### 2. 이번 주 집중 분석 (Deep Dive of the Week)
- 특정 기업/산업 깊이 있는 분석
- 장기적 가치 판단 정보 제공

### 3. 타산지석: 실패에서 배우는 교훈 (The Cautionary Tale)
- 실제 실패 사례 공유
- 실질적인 교훈 전달

### 4. 놓치면 안 될 시장의 신호들 (Market Radar)
- 작은 신호 포착
- 미래의 투자 아이디어/리스크 제시

### 5. 핵심 요약 및 다음 주 관전 포인트 (Final Takeaway)
- 3~4줄 핵심 요약
- 다음 주 주목 이벤트 제시

---

## ⚙️ 설정 옵션

### Chrome 옵션

```python
chrome_options = Options()
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_argument('--ignore-certificate-errors')
```

### Gemini 모델 선택

```python
# 기본 모델
model = genai.GenerativeModel('gemini-pro')

# 더 큰 모델 (더 정확하지만 느림)
model = genai.GenerativeModel('gemini-ultra')  # 출시 시
```

---

## 💡 팁 & 트릭

### 1. 토큰 제한 주의

Gemini API는 입력 토큰 제한이 있습니다. 글이 많으면 요약해서 전달:

```python
# 각 글의 처음 1000자만 전달
formatted_content += f"**내용:**\n{post['content'][:1000]}...\n"
```

### 2. 비용 절약

- Gemini API는 무료 티어 제공
- 월 60회 요청 제한
- 필요한 경우에만 API 호출

### 3. 오류 처리

```python
try:
    response = model.generate_content(prompt)
    result = response.text
except Exception as e:
    print(f"API 에러: {e}")
    # 재시도 로직 추가
```

---

## 🔍 문제 해결

### Q: "카테고리를 찾을 수 없습니다"

**A:** 카테고리 번호가 올바른지 확인하세요:
- 블로그 카테고리 페이지 URL 확인
- HTML에서 `<input name="categoryNo">` 확인

### Q: "날짜 파싱 에러"

**A:** 날짜 형식이 "yyyy. mm. dd."인지 확인:
- 띄어쓰기 포함
- 마지막에 점(.) 포함

### Q: "Gemini API 에러"

**A:**
1. API 키가 올바른지 확인
2. 무료 티어 제한 (60회/월) 확인
3. 입력 텍스트가 너무 길지 않은지 확인

---

## 📚 API 키 관리

### 안전한 API 키 사용

```python
# ❌ 나쁜 예: 코드에 직접 입력
GEMINI_API_KEY = "AIzaSyAbc123..."

# ✅ 좋은 예: 환경 변수 사용
import os
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# ✅ Colab에서: Secret 사용
from google.colab import userdata
GEMINI_API_KEY = userdata.get('GEMINI_API_KEY')
```

---

## 🎨 결과물 예시

### 입력

```
제목: 배당 투자는 이렇게 하셔요
내용: 와이민입니다. 찬바람이 들면서... 배당의 계절이구나...
날짜: 2025. 11. 14.
```

### 출력 (Gemini 생성)

```markdown
# 미국 개미들의 투자노트 - 2025년 11월 3주차

## 1. 금주의 가장 뜨거운 질문

**"배당주 vs 성장주, 지금 시기에는 무엇이 유리할까?"**

최근 금리 인상기에 배당주에 대한 관심이 다시 높아지고 있습니다...

[계속]
```

---

## 🚀 다음 단계

1. **자동화**: GitHub Actions로 매일/매주 자동 크롤링
2. **알림**: 새 글 발견 시 이메일/Slack 알림
3. **DB 저장**: SQLite/MongoDB에 저장하여 이력 관리
4. **웹 대시보드**: Streamlit/Gradio로 시각화

---

## 📞 지원

- 이슈: [GitHub Issues](https://github.com/...)
- 문서: [README.md](README.md)
- 기본 가이드: [QUICK_START.md](QUICK_START.md)

---

**Happy Analyzing! 📈**
