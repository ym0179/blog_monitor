# 구글 Colab 사용 가이드

네이버 블로그 크롤러를 구글 Colab에서 사용하는 방법입니다.

## 🚀 빠른 시작

### 방법 1: Jupyter 노트북 사용 (추천)

1. **Google Colab 접속**
   - https://colab.research.google.com/ 접속

2. **노트북 업로드**
   - 파일 > 노트북 업로드
   - `naver_blog_scraper.ipynb` 파일 선택

3. **셀 실행**
   - 첫 번째 셀부터 순서대로 실행 (Shift + Enter)
   - 5번째 셀에서 URL을 변경하여 원하는 블로그 크롤링

### 방법 2: 코드 직접 입력

새 Colab 노트북에서 아래 코드를 복사하여 실행하세요.

#### 1️⃣ 라이브러리 설치

```python
!pip install selenium beautifulsoup4 webdriver-manager
```

#### 2️⃣ 코드 실행

```python
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def extract_blog_content(url, wait_time=5):
    """네이버 블로그 콘텐츠 추출"""
    driver = None
    try:
        driver = setup_driver()

        print(f"블로그 접속 중: {url}")
        driver.get(url)
        time.sleep(wait_time)

        # iframe 전환
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mainFrame"))
        )
        driver.switch_to.frame(iframe)

        # 콘텐츠 추출
        source = driver.page_source
        html = BeautifulSoup(source, "html.parser")
        content_container = html.select("div.se-main-container")

        if not content_container:
            return ""

        # 텍스트 정제
        content = ''.join(str(content_container))
        content = re.sub('<[^>]*>', '', content)
        content = content.replace('\n', ' ')
        content = content.replace('\u200b', '')
        content = content.replace('&ZeroWidthSpace;', '')
        content = re.sub(r'\s+', ' ', content).strip()

        print("✅ 콘텐츠 추출 완료!")
        return content

    except Exception as e:
        print(f"❌ 에러: {str(e)}")
        return ""
    finally:
        if driver:
            driver.quit()


# 사용 예시
url = "https://blog.naver.com/yminsong/224075787010"
content = extract_blog_content(url)

if content:
    print("=" * 80)
    print("추출된 콘텐츠:")
    print("=" * 80)
    print(content)
    print("\n" + f"총 {len(content)}자")
else:
    print("콘텐츠 추출 실패")
```

## ⚙️ 주요 변경사항

### ❌ 이전 방식 (작동 안 함)
```python
# Chrome 및 ChromeDriver 설치
!apt-get update
!apt-get install -y chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
```

### ✅ 새로운 방식 (권장)
```python
# webdriver-manager 사용
!pip install webdriver-manager

from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
```

## 🔧 문제 해결

### 문제 1: ChromeDriver 에러
```
SessionNotCreatedException: Chrome instance exited
```

**해결책:**
- `webdriver-manager`를 사용하세요 (위의 새로운 방식)
- 이 패키지가 자동으로 올바른 ChromeDriver를 다운로드합니다

### 문제 1-1: DevToolsActivePort 에러
```
Chrome failed to start: exited abnormally
DevToolsActivePort file doesn't exist
```

**해결책:**
1. **런타임 재시작** (가장 효과적)
   - Colab 메뉴: Runtime > Restart runtime
   - 재시작 후 모든 셀을 다시 실행하세요

2. **Chrome 브라우저 직접 설치**
   ```python
   !apt-get update
   !apt-get install -y chromium-browser chromium-chromedriver
   ```

3. **최신 코드 사용**
   - 제공된 최신 코드는 DevToolsActivePort 에러를 해결하는 다양한 옵션을 포함하고 있습니다:
     - `--remote-debugging-port=9222`
     - `--disable-dev-shm-usage`
     - `--no-sandbox`
     - 등 20+ 개의 안정성 옵션

### 문제 2: 콘텐츠를 찾을 수 없음
```
경고: 콘텐츠를 찾을 수 없습니다.
```

**해결책:**
- `wait_time`을 늘려보세요 (기본 5초 → 10초)
- URL이 올바른 네이버 블로그 URL인지 확인하세요
- 해당 블로그가 비공개가 아닌지 확인하세요

```python
content = extract_blog_content(url, wait_time=10)  # 대기 시간 증가
```

### 문제 3: iframe을 찾을 수 없음
```
NoSuchElementException: Unable to locate element: #mainFrame
```

**해결책:**
- 페이지 로딩 시간을 늘리세요
- URL이 네이버 블로그 형식(`https://blog.naver.com/아이디/글번호`)인지 확인하세요

## 📝 여러 URL 크롤링

```python
urls = [
    "https://blog.naver.com/yminsong/224075787010",
    "https://blog.naver.com/다른아이디/글번호",
]

results = []
for url in urls:
    print(f"\n처리 중: {url}")
    content = extract_blog_content(url)
    if content:
        results.append({
            'url': url,
            'content': content,
            'length': len(content)
        })
        print(f"✅ 완료: {len(content)}자")
    else:
        print(f"❌ 실패")
    print("-" * 80)

print(f"\n총 {len(results)}개 크롤링 완료!")
```

## 💡 팁

1. **대기 시간 조절**
   - 인터넷 속도가 느리면 `wait_time`을 늘리세요
   - 너무 짧으면 페이지가 완전히 로드되지 않습니다

2. **서버 부담 최소화**
   - 연속 크롤링 시 URL 사이에 추가 대기 시간을 넣으세요
   ```python
   for url in urls:
       content = extract_blog_content(url)
       time.sleep(2)  # 각 요청 사이 2초 대기
   ```

3. **결과 저장**
   ```python
   import pandas as pd

   df = pd.DataFrame(results)
   df.to_csv('blog_contents.csv', index=False, encoding='utf-8-sig')
   print("CSV 파일로 저장 완료!")
   ```

## ⚠️ 주의사항

1. **저작권**: 크롤링한 콘텐츠의 저작권은 원저작자에게 있습니다
2. **이용 약관**: 네이버의 이용 약관을 준수하세요
3. **과도한 요청 금지**: 서버에 부담을 주지 않도록 적절한 대기 시간을 설정하세요
4. **개인정보**: 개인정보가 포함된 콘텐츠는 주의하여 다루세요

## 📚 추가 자료

- [Selenium 공식 문서](https://www.selenium.dev/documentation/)
- [BeautifulSoup 문서](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager)
