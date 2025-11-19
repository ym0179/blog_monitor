"""
네이버 블로그 크롤러 (수정 버전)
- iframe 대기 시간 증가
- 대체 방법 추가
"""

import time
import re
from datetime import datetime, timedelta
import google_colab_selenium as gs
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd


def setup_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-infobars')
    driver = gs.Chrome(options=chrome_options)
    return driver


def extract_blog_title(html):
    """블로그 글의 타이틀 추출"""
    try:
        title_elem = html.select_one("div.se-module.se-module-text.se-title-text")
        if title_elem:
            return title_elem.get_text(strip=True)

        title_p = html.select_one("div.se-title-text p.se-text-paragraph")
        if title_p:
            return title_p.get_text(strip=True)

        return ""
    except:
        return ""


def extract_blog_content_only(html):
    """블로그 콘텐츠만 추출"""
    try:
        content_container = html.select("div.se-main-container")
        if not content_container:
            return ""

        content = ''.join(str(content_container))
        content = re.sub('<[^>]*>', '', content)
        content = content.replace('\n', ' ').replace('\u200b', '').replace('&ZeroWidthSpace;', '')
        content = re.sub(r'\s+', ' ', content).strip()

        return content
    except:
        return ""


def get_recent_posts_from_category(blog_id, category_no, days=14):
    """
    특정 카테고리의 최근 글 목록 가져오기 (수정 버전)
    """
    driver = None
    posts = []

    try:
        driver = setup_driver()
        category_url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}&categoryNo={category_no}"
        print(f"카테고리 페이지 접속: {category_url}")

        driver.get(category_url)
        time.sleep(5)  # 대기 시간 증가

        # iframe 찾기 시도 (더 긴 대기 시간)
        iframe_found = False
        try:
            print("iframe 찾는 중...")
            iframe = WebDriverWait(driver, 15).until(  # 10초 → 15초
                EC.presence_of_element_located((By.ID, "mainFrame"))
            )
            driver.switch_to.frame(iframe)
            iframe_found = True
            print("✅ iframe 전환 성공")
            time.sleep(3)  # iframe 로드 대기

        except TimeoutException:
            print("⚠️ iframe을 찾을 수 없습니다. iframe 없이 시도합니다.")
            iframe_found = False

        # HTML 파싱
        html = BeautifulSoup(driver.page_source, "html.parser")

        # 글 목록 테이블 찾기
        table = html.select_one("table.blog2_list.blog2_categorylist")

        if not table:
            print("⚠️ 테이블을 찾을 수 없습니다. 페이지 구조 확인 중...")

            # 대체 방법: 다른 선택자 시도
            table = html.select_one("table.blog2_list")

            if not table:
                # 디버깅: 페이지 내용 확인
                print("\n발견된 테이블들:")
                all_tables = html.find_all('table')
                for idx, t in enumerate(all_tables):
                    classes = t.get('class', [])
                    print(f"  테이블 {idx}: class={classes}")

                print("\n❌ 글 목록 테이블을 찾을 수 없습니다")
                print("페이지 소스 일부:")
                print(str(html)[:1000])
                return posts

        print("✅ 테이블 발견")

        # 현재 날짜
        now = datetime.now()
        cutoff_date = now - timedelta(days=days)

        # tbody의 각 row 처리
        rows = table.select("tbody tr")
        print(f"총 {len(rows)}개의 글 발견")

        if len(rows) == 0:
            print("⚠️ tbody에 행이 없습니다")
            return posts

        for row in rows:
            try:
                # 제목과 URL 추출
                title_elem = row.select_one("td.title a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')

                # 날짜 추출
                date_elem = row.select_one("td.date span.date")
                if not date_elem:
                    continue

                date_str = date_elem.get_text(strip=True)

                # 날짜 파싱
                try:
                    # "2025. 11. 14." → "2025-11-14"
                    date_clean = date_str.replace(' ', '').replace('.', '-').rstrip('-')
                    post_date = datetime.strptime(date_clean, "%Y-%m-%d")

                    # 날짜 필터링
                    if post_date >= cutoff_date:
                        full_url = url if url.startswith('http') else f"https://blog.naver.com{url}"
                        posts.append({
                            'title': title,
                            'url': full_url,
                            'date': date_str,
                            'date_obj': post_date
                        })
                        print(f"✅ [{date_str}] {title}")
                    else:
                        print(f"⏭️  [{date_str}] {title} (기간 외)")

                except ValueError as e:
                    print(f"날짜 파싱 에러 ({date_str}): {e}")
                    continue

            except Exception as e:
                print(f"행 처리 에러: {e}")
                continue

        print(f"\n✅ 최근 {days}일 이내 글: {len(posts)}개")
        return posts

    except Exception as e:
        print(f"❌ 전체 에러: {e}")
        import traceback
        traceback.print_exc()
        return posts

    finally:
        if driver:
            driver.quit()


def extract_full_post(url):
    """개별 글의 전체 내용 추출"""
    driver = None
    try:
        driver = setup_driver()
        print(f"  글 접속: {url}")
        driver.get(url)
        time.sleep(5)  # 대기 시간 증가

        # iframe 전환
        try:
            iframe = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "mainFrame"))
            )
            driver.switch_to.frame(iframe)
            time.sleep(3)
        except TimeoutException:
            print("  ⚠️ iframe 없이 진행")

        html = BeautifulSoup(driver.page_source, "html.parser")
        title = extract_blog_title(html)
        content = extract_blog_content_only(html)

        return {'title': title, 'content': content}

    except Exception as e:
        print(f"  ❌ 추출 실패: {e}")
        return {'title': '', 'content': ''}

    finally:
        if driver:
            driver.quit()


# 메인 실행
if __name__ == "__main__":
    # 설정
    BLOG_ID = "yminsong"
    CATEGORY_NO = 31
    DAYS = 14

    print("="*80)
    print("1단계: 최근 글 목록 가져오기")
    print("="*80)

    recent_posts = get_recent_posts_from_category(BLOG_ID, CATEGORY_NO, DAYS)

    if recent_posts:
        print(f"\n✅ {len(recent_posts)}개의 글을 찾았습니다!")

        # 목록 출력
        for idx, post in enumerate(recent_posts, 1):
            print(f"{idx}. [{post['date']}] {post['title']}")
    else:
        print("\n⚠️ 최근 글이 없습니다.")
