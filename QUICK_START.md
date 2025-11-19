# 🚀 빠른 시작 가이드

Google Colab에서 네이버 블로그를 크롤링하는 가장 쉬운 방법!

## ✅ 단 2단계로 완료!

### 1️⃣ 패키지 설치 (5초)

Colab에서 새 노트북을 만들고 첫 번째 셀에 입력:

```python
!pip install -q google-colab-selenium beautifulsoup4
```

### 2️⃣ 코드 실행 (복사 & 붙여넣기)

두 번째 셀에 아래 코드를 복사:

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
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-infobars')
    driver = gs.Chrome(options=chrome_options)
    return driver


def extract_blog_content(url, wait_time=5):
    """네이버 블로그 콘텐츠 추출"""
    driver = None
    try:
        driver = setup_driver()
        print(f"✅ 블로그 접속 중: {url}")

        driver.get(url)
        time.sleep(wait_time)

        # iframe 전환
        print("iframe 전환 중...")
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mainFrame"))
        )
        driver.switch_to.frame(iframe)

        # 콘텐츠 추출
        print("콘텐츠 추출 중...")
        html = BeautifulSoup(driver.page_source, "html.parser")
        content = html.select("div.se-main-container")

        if not content:
            print("⚠️ 콘텐츠를 찾을 수 없습니다")
            return ""

        # 텍스트 정제
        text = ''.join(str(content))
        text = re.sub('<[^>]*>', '', text)
        text = text.replace('\n', ' ').replace('\u200b', '').replace('&ZeroWidthSpace;', '')
        text = re.sub(r'\s+', ' ', text).strip()

        print("✅ 추출 완료!")
        return text

    except Exception as e:
        print(f"❌ 에러: {str(e)}")
        return ""
    finally:
        if driver:
            driver.quit()


# 🎯 사용 예시
url = "https://blog.naver.com/yminsong/224075787010"
content = extract_blog_content(url)

if content:
    print("\n" + "="*80)
    print("📝 추출된 콘텐츠:")
    print("="*80)
    print(content[:500] + "..." if len(content) > 500 else content)
    print("\n" + "="*80)
    print(f"✅ 총 {len(content):,}자 추출 성공!")
    print("="*80)
else:
    print("\n❌ 콘텐츠 추출 실패")
```

**끝!** 🎉

---

## 📋 여러 URL 크롤링

여러 블로그를 한 번에 크롤링하려면:

```python
# 크롤링할 URL 리스트
urls = [
    "https://blog.naver.com/yminsong/224075787010",
    "https://blog.naver.com/anotheruser/123456789",
    # 추가 URL...
]

results = []

for idx, url in enumerate(urls, 1):
    print(f"\n[{idx}/{len(urls)}] 처리 중...")
    content = extract_blog_content(url)

    if content:
        results.append({
            'url': url,
            'content': content,
            'length': len(content)
        })
        print(f"✅ 성공: {len(content):,}자")
    else:
        print("❌ 실패")

    # 서버 부담 최소화
    if idx < len(urls):
        time.sleep(2)

print(f"\n🎉 완료! 총 {len(results)}개 크롤링 성공")
```

---

## 💾 CSV로 저장

크롤링 결과를 CSV 파일로 저장하려면:

```python
import pandas as pd

# DataFrame 생성
df = pd.DataFrame(results)

# CSV 저장
df.to_csv('blog_contents.csv', index=False, encoding='utf-8-sig')

# 파일 다운로드 (Colab)
from google.colab import files
files.download('blog_contents.csv')

print("✅ CSV 파일 다운로드 완료!")
```

---

## 🔧 커스터마이징

### 대기 시간 조절

인터넷이 느리거나 페이지 로딩이 느리면:

```python
content = extract_blog_content(url, wait_time=10)  # 10초로 증가
```

### Chrome 옵션 추가

특정 Chrome 옵션을 추가하려면:

```python
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--incognito')  # 시크릿 모드
    driver = gs.Chrome(options=chrome_options)
    return driver
```

---

## ❓ 문제 해결

### Q: "콘텐츠를 찾을 수 없습니다" 에러

**A:** 다음을 확인하세요:
- URL이 올바른지 확인 (네이버 블로그 URL 형식: `https://blog.naver.com/아이디/글번호`)
- 블로그가 비공개가 아닌지 확인
- `wait_time`을 늘려보세요 (기본 5초 → 10초)

### Q: 에러가 발생했어요

**A:** 대부분의 경우 다음으로 해결됩니다:
1. Colab 런타임 재시작: `Runtime > Restart runtime`
2. 모든 셀을 다시 실행

### Q: 크롤링이 너무 느려요

**A:**
- 이미지를 로드하지 않도록 설정하면 빨라집니다
- 여러 URL을 크롤링할 때는 각 요청 사이에 대기 시간을 두세요

---

## 💡 왜 google-colab-selenium을 사용하나요?

### 기존 방법 (복잡함)
```python
# ❌ 10줄 이상의 설정 필요
!apt-get update
!apt-get install -y chromium-browser chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
# + ChromeDriver 버전 호환성 문제
# + 다양한 에러 발생 가능
```

### google-colab-selenium (간단함)
```python
# ✅ 단 1줄!
!pip install google-colab-selenium
import google_colab_selenium as gs
driver = gs.Chrome()
```

**장점:**
- 🚀 설치 및 설정 자동화
- ✅ ChromeDriver 버전 자동 관리
- 🔧 Colab 환경에 최적화
- 🛡️ 에러 발생률 최소화

---

## 📚 더 알아보기

- 전체 문서: [README.md](README.md)
- Jupyter 노트북: [naver_blog_scraper.ipynb](naver_blog_scraper.ipynb)
- google-colab-selenium: [GitHub](https://github.com/jpjacobpadilla/Google-Colab-Selenium)

---

**Happy Crawling! 🎉**
