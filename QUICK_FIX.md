# 🚨 Colab Chrome 에러 빠른 해결

Chrome 관련 에러가 발생하면 아래 방법을 **순서대로** 시도하세요.

## 📋 에러 종류

### 1. "Chrome instance exited"
### 2. "DevToolsActivePort file doesn't exist"
### 3. "chrome not reachable"

모두 같은 원인: Chrome/ChromeDriver 설정 문제

---

## ✅ 해결 방법 (성공률 순서)

### 🥇 방법 1: apt-get으로 직접 설치 (90% 성공률)

**Colab에서 다음 코드를 복사해서 실행하세요:**

```python
# 1. Chrome 설치
!apt-get update -qq
!apt-get install -y -qq chromium-browser chromium-chromedriver

# 2. 패키지 설치
!pip install -q selenium beautifulsoup4

# 3. ChromeDriver 경로 설정
!cp /usr/lib/chromium-browser/chromedriver /usr/bin

print("✅ 설치 완료!")
print("⚠️ 중요: Runtime > Restart runtime을 클릭하세요!")
```

**런타임 재시작 후** 다음 코드로 테스트:

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


def setup_driver():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium-browser"  # 중요!

    # 필수 옵션
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--remote-debugging-port=9222')

    # ChromeDriver 경로 직접 지정
    service = Service('/usr/bin/chromedriver')

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def extract_blog_content(url):
    driver = None
    try:
        driver = setup_driver()
        print(f"✅ Chrome 시작 성공!")
        print(f"접속 중: {url}")

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

        if not content:
            return ""

        # 텍스트 정제
        text = ''.join(str(content))
        text = re.sub('<[^>]*>', '', text)
        text = text.replace('\n', ' ').replace('\u200b', '').replace('&ZeroWidthSpace;', '')
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    except Exception as e:
        print(f"❌ 에러: {str(e)}")
        return ""
    finally:
        if driver:
            driver.quit()


# 테스트
url = "https://blog.naver.com/yminsong/224075787010"
content = extract_blog_content(url)

if content:
    print("\n" + "="*80)
    print("추출 성공!")
    print("="*80)
    print(content[:500] + "...")
    print(f"\n총 {len(content)}자")
else:
    print("추출 실패")
```

---

### 🥈 방법 2: 기존 Chrome 프로세스 종료 후 재시도

```python
# 1. 실행 중인 Chrome 프로세스 모두 종료
!pkill -9 chrome
!pkill -9 chromium

# 2. 잠시 대기
import time
time.sleep(2)

# 3. 위의 코드 다시 실행
```

---

### 🥉 방법 3: 문제 진단

정확한 에러 원인을 파악하려면:

```python
# Chrome 설치 확인
!which chromium-browser
!chromium-browser --version

# ChromeDriver 확인
!which chromedriver
!chromedriver --version

# 실행 중인 프로세스 확인
!ps aux | grep chrome
```

---

## 🔍 진단 도구 사용

정확한 문제를 파악하려면 진단 노트북을 사용하세요:

1. `colab_diagnose.ipynb` 파일을 Colab에 업로드
2. 순서대로 셀 실행
3. 에러 메시지 확인

---

## 💡 핵심 포인트

### ✅ 중요한 3가지

1. **Chrome 바이너리 위치 직접 지정**
   ```python
   chrome_options.binary_location = "/usr/bin/chromium-browser"
   ```

2. **ChromeDriver 경로 직접 지정**
   ```python
   service = Service('/usr/bin/chromedriver')
   ```

3. **필수 Chrome 옵션**
   ```python
   --headless
   --no-sandbox
   --disable-dev-shm-usage
   ```

---

## 🚫 흔한 실수

### ❌ 하지 말아야 할 것

1. **webdriver-manager만 사용** → Colab에서 불안정
2. **런타임 재시작 안 함** → 이전 프로세스 충돌
3. **바이너리 경로 지정 안 함** → Chrome을 찾지 못함

---

## 📞 여전히 안 되면?

### 최후의 수단: 완전 초기화

```python
# 1. 모든 Chrome 제거
!apt-get remove -y chromium-browser chromium-chromedriver
!apt-get autoremove -y

# 2. 재설치
!apt-get update
!apt-get install -y chromium-browser chromium-chromedriver

# 3. 런타임 재시작
# Runtime > Restart runtime

# 4. 위의 방법 1 코드 실행
```

---

## ✅ 성공 확인

이 메시지가 나오면 성공:
```
✅ Chrome 시작 성공!
접속 중: https://blog.naver.com/...
추출 성공!
```

---

## 📚 관련 문서

- [COLAB_GUIDE.md](COLAB_GUIDE.md) - 상세 사용법
- [colab_diagnose.ipynb](colab_diagnose.ipynb) - 진단 도구
- [README.md](README.md) - 전체 문서
