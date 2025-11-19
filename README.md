# 네이버 블로그 크롤러

네이버 블로그의 콘텐츠를 크롤링하여 텍스트를 추출하는 도구입니다.

## 주요 기능

- Selenium을 사용한 동적 페이지 크롤링
- 네이버 블로그의 iframe 구조 처리
- HTML 태그 제거 및 텍스트 정제
- 구글 Colab 환경 지원

## 설치 방법

### 로컬 환경

```bash
pip install -r requirements.txt
```

Chrome 브라우저와 ChromeDriver가 설치되어 있어야 합니다.

### 구글 Colab

Colab 노트북에서는 첫 번째 셀에서 다음을 실행하세요:

```bash
!apt-get update
!apt-get install -y chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
!pip install selenium beautifulsoup4
```

## 사용 방법

### 1. Python 스크립트 사용

```python
from naver_blog_scraper import scrape_naver_blog

# 단일 URL 크롤링
url = "https://blog.naver.com/yminsong/224075787010"
scrape_naver_blog(url)
```

### 2. 구글 Colab 노트북 사용

1. `naver_blog_scraper.ipynb` 파일을 구글 Colab에 업로드
2. 순서대로 셀을 실행
3. 마지막 셀에서 크롤링할 URL을 입력하고 실행

### 3. 명령줄에서 실행

```bash
python naver_blog_scraper.py
```

## 코드 예시

### 단일 URL 크롤링

```python
from naver_blog_scraper import extract_blog_content

url = "https://blog.naver.com/yminsong/224075787010"
content = extract_blog_content(url)
print(content)
```

### 여러 URL 크롤링

```python
from naver_blog_scraper import extract_blog_content

urls = [
    "https://blog.naver.com/yminsong/224075787010",
    "https://blog.naver.com/another_blog/123456789",
]

contents = []
for url in urls:
    content = extract_blog_content(url)
    if content:
        contents.append(content)
        print(f"추출 완료: {url}")
```

## 주요 함수

### `setup_driver()`
Chrome WebDriver를 설정하고 반환합니다.

**반환값:**
- `webdriver.Chrome`: 설정된 Chrome WebDriver 인스턴스

### `extract_blog_content(url, wait_time=5)`
네이버 블로그 URL에서 콘텐츠를 추출합니다.

**매개변수:**
- `url` (str): 네이버 블로그 URL
- `wait_time` (int): 페이지 로딩 대기 시간 (기본값: 5초)

**반환값:**
- `str`: 추출된 텍스트 내용

### `scrape_naver_blog(url)`
블로그를 크롤링하고 결과를 출력합니다.

**매개변수:**
- `url` (str): 네이버 블로그 URL

## 처리 과정

1. Chrome WebDriver 설정 (headless 모드)
2. 블로그 URL 접속
3. iframe으로 전환 (`mainFrame`)
4. HTML 소스 가져오기
5. `div.se-main-container` 영역에서 콘텐츠 추출
6. HTML 태그 제거
7. 특수문자 및 불필요한 패턴 제거
8. 텍스트 정제 (공백 정리)

## 텍스트 정제 내용

- HTML 태그 제거
- Zero-width space (`\u200b`, `&ZeroWidthSpace;`) 제거
- 연속된 공백을 단일 공백으로 변환
- 줄바꿈을 공백으로 변환

## 주의사항

1. **크롤링 속도**: 서버에 부담을 주지 않도록 적절한 대기 시간을 설정하세요.
2. **네트워크 속도**: `wait_time` 매개변수를 인터넷 속도에 맞게 조정하세요.
3. **저작권**: 크롤링한 콘텐츠의 저작권은 원저작자에게 있습니다.
4. **이용 약관**: 네이버의 이용 약관을 준수하여 사용하세요.

## 문제 해결

### ChromeDriver 오류
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```
**해결방법**: ChromeDriver를 설치하고 PATH에 추가하세요.

### iframe을 찾을 수 없음
```
NoSuchElementException: Unable to locate element: #mainFrame
```
**해결방법**:
- `wait_time`을 늘려보세요 (예: 10초)
- URL이 네이버 블로그 URL인지 확인하세요

### 콘텐츠를 찾을 수 없음
```
경고: 콘텐츠를 찾을 수 없습니다.
```
**해결방법**:
- 블로그 구조가 변경되었을 수 있습니다
- 해당 블로그가 비공개일 수 있습니다

## 라이선스

MIT License

## 기여

이슈나 개선 사항은 GitHub Issues를 통해 제안해주세요.
