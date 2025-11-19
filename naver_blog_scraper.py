"""
네이버 블로그 크롤러
구글 Colab 환경에서 실행 가능
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def setup_driver():
    """
    Chrome WebDriver 설정 (구글 Colab용)
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 백그라운드 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_blog_content(url, wait_time=5):
    """
    네이버 블로그 콘텐츠 추출

    Args:
        url (str): 네이버 블로그 URL
        wait_time (int): 페이지 로딩 대기 시간 (초)

    Returns:
        str: 추출된 블로그 텍스트 내용
    """
    driver = None
    try:
        # 드라이버 설정
        driver = setup_driver()

        # 페이지 열기
        print(f"블로그 URL 접속 중: {url}")
        driver.get(url)
        time.sleep(wait_time)

        # iframe 찾기 및 전환
        print("iframe으로 전환 중...")
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mainFrame"))
        )
        driver.switch_to.frame(iframe)

        # 페이지 소스 가져오기
        source = driver.page_source
        html = BeautifulSoup(source, "html.parser")

        # 콘텐츠 추출
        print("콘텐츠 추출 중...")
        content_container = html.select("div.se-main-container")

        if not content_container:
            print("경고: 콘텐츠를 찾을 수 없습니다.")
            return ""

        # 텍스트만 추출
        content = ''.join(str(content_container))

        # HTML 태그 제거
        pattern1 = '<[^>]*>'
        content = re.sub(pattern=pattern1, repl='', string=content)

        # 불필요한 패턴 제거
        pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
        content = content.replace(pattern2, '')

        # 텍스트 정제
        content = content.replace('\n', ' ')
        content = content.replace('\u200b', '')  # Zero-width space 제거
        content = content.replace('&ZeroWidthSpace;', '')

        # 연속된 공백 제거
        content = re.sub(r'\s+', ' ', content).strip()

        print("콘텐츠 추출 완료!")
        return content

    except Exception as e:
        print(f"에러 발생: {str(e)}")
        return ""

    finally:
        if driver:
            driver.quit()


def scrape_naver_blog(url):
    """
    네이버 블로그 스크래핑 메인 함수

    Args:
        url (str): 네이버 블로그 URL
    """
    print("=" * 80)
    print("네이버 블로그 크롤링 시작")
    print("=" * 80)

    content = extract_blog_content(url)

    if content:
        print("\n" + "=" * 80)
        print("추출된 콘텐츠:")
        print("=" * 80)
        print(content)
        print("\n" + "=" * 80)
        print(f"총 텍스트 길이: {len(content)} 자")
        print("=" * 80)
    else:
        print("콘텐츠를 추출하지 못했습니다.")


if __name__ == "__main__":
    # 테스트 URL
    test_url = "https://blog.naver.com/yminsong/224075787010"
    scrape_naver_blog(test_url)
