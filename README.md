# 네이버 블로그 크롤러

네이버 블로그의 콘텐츠를 크롤링하여 텍스트를 추출하는 도구입니다.

## ✨ 주요 기능

- **google-colab-selenium** 사용으로 Colab에서 한 줄로 설정 완료
- Selenium을 사용한 동적 페이지 크롤링
- 네이버 블로그의 iframe 구조 자동 처리
- HTML 태그 제거 및 텍스트 정제
- 구글 Colab 및 로컬 환경 모두 지원

## 🚀 빠른 시작 (Google Colab)

### 1단계: 패키지 설치

```python
!pip install -q google-colab-selenium beautifulsoup4
```

### 2단계: 코드 실행

```python
import time
import re
import google_colab_selenium as gs
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-infobars')
    driver = gs.Chrome(options=chrome_options)
    return driver


def extract_blog_content(url):
    driver = None
    try:
        driver = setup_driver()
        driver.get(url)
        time.sleep(5)

        # iframe 전환
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mainFrame"))
        )
        driver.switch_to.frame(iframe)

        # 콘텐츠 추출
        html = BeautifulSoup(driver.page_source, "html.parser")
        content = html.select("div.se-main-container")

        # 텍스트 정제
        text = ''.join(str(content))
        text = re.sub('<[^>]*>', '', text)
        text = text.replace('\n', ' ').replace('\u200b', '')
        text = re.sub(r'\s+', ' ', text).strip()

        return text
    finally:
        if driver:
            driver.quit()


# 사용 예시
url = "https://blog.naver.com/yminsong/224075787010"
content = extract_blog_content(url)
print(content)
```

**끝!** 더 이상 복잡한 설정 필요 없습니다! 🎉

## 📦 설치 방법

### Google Colab (권장)

```bash
!pip install google-colab-selenium beautifulsoup4
```

`google-colab-selenium`이 Chrome과 ChromeDriver를 자동으로 설정해줍니다.

### 로컬 환경

```bash
pip install -r requirements.txt
```

로컬에서는 Chrome 브라우저와 ChromeDriver가 필요합니다.

## 📖 사용 방법

### 1. Jupyter 노트북 사용 (가장 쉬움)

1. `naver_blog_scraper.ipynb` 파일을 Google Colab에 업로드
2. 순서대로 셀을 실행
3. URL을 변경하여 원하는 블로그 크롤링

### 2. Python 스크립트 사용

```python
from naver_blog_scraper import extract_blog_content

url = "https://blog.naver.com/yminsong/224075787010"
content = extract_blog_content(url)
print(content)
```

### 3. 여러 URL 크롤링

```python
urls = [
    "https://blog.naver.com/yminsong/224075787010",
    "https://blog.naver.com/another_blog/123456789",
]

for url in urls:
    content = extract_blog_content(url)
    print(f"추출 완료: {len(content)}자")
    time.sleep(2)  # 서버 부담 최소화
```

## 🎯 주요 함수

### `setup_driver()`
Chrome WebDriver를 설정하고 반환합니다.

- **Colab**: `google-colab-selenium` 사용
- **로컬**: 일반 selenium 사용

### `extract_blog_content(url, wait_time=5)`
네이버 블로그 URL에서 콘텐츠를 추출합니다.

**매개변수:**
- `url` (str): 네이버 블로그 URL
- `wait_time` (int): 페이지 로딩 대기 시간 (기본값: 5초)

**반환값:**
- `str`: 추출된 텍스트 내용

## 🔧 처리 과정

1. Chrome WebDriver 자동 설정 (`google-colab-selenium` 사용)
2. 블로그 URL 접속
3. iframe(`mainFrame`)으로 자동 전환
4. HTML 소스 가져오기
5. `div.se-main-container` 영역에서 콘텐츠 추출
6. HTML 태그 제거
7. 특수문자 및 불필요한 패턴 제거
8. 텍스트 정제 (공백 정리)

## 🎨 텍스트 정제 내용

- HTML 태그 완전 제거
- Zero-width space (`\u200b`, `&ZeroWidthSpace;`) 제거
- 연속된 공백을 단일 공백으로 변환
- 줄바꿈을 공백으로 변환
- 앞뒤 공백 제거

## 💡 장점

### 기존 방법의 문제점
```python
# ❌ 복잡하고 에러 발생
!apt-get update
!apt-get install -y chromium-browser chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
# + 20줄의 Chrome 옵션 설정...
```

### google-colab-selenium 사용
```python
# ✅ 간단하고 안정적
!pip install google-colab-selenium
import google_colab_selenium as gs
driver = gs.Chrome()
```

**차이점:**
- ✅ 설치 명령 1줄
- ✅ ChromeDriver 자동 관리
- ✅ 버전 호환성 자동 처리
- ✅ 에러 발생률 최소화

## ⚠️ 주의사항

1. **크롤링 속도**: 서버에 부담을 주지 않도록 적절한 대기 시간을 설정하세요.
2. **네트워크 속도**: `wait_time` 매개변수를 인터넷 속도에 맞게 조정하세요.
3. **저작권**: 크롤링한 콘텐츠의 저작권은 원저작자에게 있습니다.
4. **이용 약관**: 네이버의 이용 약관을 준수하여 사용하세요.

## 🆚 비교

| 항목 | 기존 방법 | google-colab-selenium |
|------|-----------|----------------------|
| 설치 복잡도 | 매우 높음 | 매우 낮음 |
| 에러 발생률 | 높음 | 낮음 |
| 설정 라인 수 | 50+ | 2 |
| 버전 관리 | 수동 | 자동 |
| Colab 호환성 | 불안정 | 완벽 |

## 📚 참고 자료

- [google-colab-selenium GitHub](https://github.com/jpjacobpadilla/Google-Colab-Selenium)
- [Selenium 공식 문서](https://www.selenium.dev/documentation/)
- [BeautifulSoup 문서](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## 📝 라이선스

MIT License

## 🤝 기여

이슈나 개선 사항은 GitHub Issues를 통해 제안해주세요.
