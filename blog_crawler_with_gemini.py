"""
네이버 블로그 크롤러 + Gemini AI 분석
- 특정 카테고리의 최근 글 목록 가져오기
- 각 글의 title, content, date 추출
- 엑셀로 저장
- Gemini API로 투자 콘텐츠 생성
"""

import time
import re
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Colab 환경 감지
try:
    import google.colab
    IN_COLAB = True
    import google_colab_selenium as gs
except ImportError:
    IN_COLAB = False
    from selenium import webdriver


def setup_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--ignore-certificate-errors')

    if IN_COLAB:
        print("✅ Google Colab 환경 감지")
        driver = gs.Chrome(options=chrome_options)
    else:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=chrome_options)

    return driver


def extract_blog_title(html):
    """블로그 글의 타이틀 추출"""
    try:
        # 타이틀 영역 찾기
        title_elem = html.select_one("div.se-module.se-module-text.se-title-text")
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            return title_text

        # 대체 방법: p 태그에서 직접 추출
        title_p = html.select_one("div.se-title-text p.se-text-paragraph")
        if title_p:
            return title_p.get_text(strip=True)

        return ""
    except Exception as e:
        print(f"타이틀 추출 에러: {e}")
        return ""


def extract_blog_content_only(html):
    """블로그 콘텐츠만 추출 (타이틀 제외)"""
    try:
        content_container = html.select("div.se-main-container")
        if not content_container:
            return ""

        # 텍스트만 추출
        content = ''.join(str(content_container))

        # HTML 태그 제거
        content = re.sub('<[^>]*>', '', content)

        # 텍스트 정제
        content = content.replace('\n', ' ')
        content = content.replace('\u200b', '')
        content = content.replace('&ZeroWidthSpace;', '')
        content = re.sub(r'\s+', ' ', content).strip()

        return content
    except Exception as e:
        print(f"콘텐츠 추출 에러: {e}")
        return ""


def get_recent_posts_from_category(blog_id, category_no, days=14):
    """
    특정 카테고리의 최근 글 목록 가져오기

    Args:
        blog_id: 블로그 ID (예: 'yminsong')
        category_no: 카테고리 번호 (예: 31)
        days: 최근 며칠 이내 글 (기본: 14일)

    Returns:
        list: {'title', 'url', 'date'} 딕셔너리 리스트
    """
    driver = None
    posts = []

    try:
        driver = setup_driver()

        # 카테고리 페이지 URL
        category_url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}&categoryNo={category_no}"
        print(f"카테고리 페이지 접속: {category_url}")

        driver.get(category_url)
        time.sleep(3)

        # iframe 전환
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mainFrame"))
        )
        driver.switch_to.frame(iframe)
        time.sleep(2)

        # HTML 파싱
        html = BeautifulSoup(driver.page_source, "html.parser")

        # 글 목록 테이블 찾기
        table = html.select_one("table.blog2_list.blog2_categorylist")
        if not table:
            print("⚠️ 글 목록 테이블을 찾을 수 없습니다")
            return posts

        # 현재 날짜
        now = datetime.now()
        cutoff_date = now - timedelta(days=days)

        # tbody의 각 row 처리
        rows = table.select("tbody tr")
        print(f"총 {len(rows)}개의 글 발견")

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

                # 날짜 파싱 (형식: "2025. 11. 14.")
                try:
                    # "2025. 11. 14." → "2025.11.14"
                    date_clean = date_str.replace(' ', '').replace('.', '-').rstrip('-')
                    post_date = datetime.strptime(date_clean, "%Y-%m-%d")

                    # 날짜 필터링
                    if post_date >= cutoff_date:
                        posts.append({
                            'title': title,
                            'url': url if url.startswith('http') else f"https://blog.naver.com{url}",
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
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return posts

    finally:
        if driver:
            driver.quit()


def extract_full_post(url):
    """
    개별 글의 전체 내용 추출 (title + content)

    Args:
        url: 블로그 글 URL

    Returns:
        dict: {'title', 'content'}
    """
    driver = None
    try:
        driver = setup_driver()

        print(f"  글 접속 중: {url}")
        driver.get(url)
        time.sleep(3)

        # iframe 전환
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mainFrame"))
        )
        driver.switch_to.frame(iframe)
        time.sleep(2)

        # HTML 파싱
        html = BeautifulSoup(driver.page_source, "html.parser")

        # 타이틀 추출
        title = extract_blog_title(html)

        # 콘텐츠 추출
        content = extract_blog_content_only(html)

        return {
            'title': title,
            'content': content
        }

    except Exception as e:
        print(f"  ❌ 추출 실패: {e}")
        return {'title': '', 'content': ''}

    finally:
        if driver:
            driver.quit()


def crawl_category_posts(blog_id, category_no, days=14):
    """
    카테고리의 최근 글을 크롤링하여 전체 내용 가져오기

    Args:
        blog_id: 블로그 ID
        category_no: 카테고리 번호
        days: 최근 며칠 이내 글

    Returns:
        list: 글 정보 딕셔너리 리스트
    """
    print("="*80)
    print("1단계: 최근 글 목록 가져오기")
    print("="*80)

    # 최근 글 목록 가져오기
    recent_posts = get_recent_posts_from_category(blog_id, category_no, days)

    if not recent_posts:
        print("최근 글이 없습니다.")
        return []

    print("\n" + "="*80)
    print("2단계: 각 글의 전체 내용 추출")
    print("="*80)

    # 각 글의 전체 내용 추출
    results = []

    for idx, post in enumerate(recent_posts, 1):
        print(f"\n[{idx}/{len(recent_posts)}] {post['title']}")

        # 전체 내용 추출
        full_post = extract_full_post(post['url'])

        results.append({
            'title': full_post['title'] or post['title'],
            'content': full_post['content'],
            'date': post['date'],
            'url': post['url']
        })

        print(f"  ✅ 완료 (본문 {len(full_post['content'])}자)")

        # 서버 부담 최소화
        if idx < len(recent_posts):
            time.sleep(2)

    return results


def save_to_excel(posts, filename='naver_blog_posts.xlsx'):
    """
    크롤링한 글을 엑셀로 저장

    Args:
        posts: 글 정보 리스트
        filename: 저장할 파일명
    """
    print("\n" + "="*80)
    print("3단계: 엑셀 저장")
    print("="*80)

    if not posts:
        print("저장할 데이터가 없습니다.")
        return None

    # DataFrame 생성
    df = pd.DataFrame(posts)

    # 엑셀 저장
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"✅ 엑셀 파일 저장 완료: {filename}")
    print(f"   총 {len(posts)}개 글 저장")

    # Colab이면 파일 다운로드
    if IN_COLAB:
        from google.colab import files
        files.download(filename)
        print(f"✅ 파일 다운로드 시작: {filename}")

    return df


def analyze_with_gemini(posts, api_key):
    """
    Gemini API를 사용하여 블로그 글 분석

    Args:
        posts: 글 정보 리스트
        api_key: Gemini API 키

    Returns:
        str: 생성된 콘텐츠
    """
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ google-generativeai 패키지가 필요합니다.")
        print("설치: !pip install google-generativeai")
        return None

    print("\n" + "="*80)
    print("4단계: Gemini AI 분석")
    print("="*80)

    # Gemini 설정
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    # 글 내용을 LLM이 이해하기 쉬운 형식으로 변환
    formatted_content = "# 블로그 글 모음\n\n"

    for idx, post in enumerate(posts, 1):
        formatted_content += f"## 글 {idx}\n"
        formatted_content += f"**제목:** {post['title']}\n"
        formatted_content += f"**날짜:** {post['date']}\n"
        formatted_content += f"**내용:**\n{post['content'][:1000]}...\n"  # 처음 1000자만
        formatted_content += "\n" + "-"*80 + "\n\n"

    # 프롬프트
    prompt = f"""
# 지시문

첨부한 파일의 실제 토론 내용을 바탕으로 리테일 투자자(개미 투자자)들의 관심을 끌고, 장기적으로 유용한 지식을 제공할 수 있는 콘텐츠를 작성.

# 콘텐츠 구조: "미국 개미들의 투자노트"

이 구조는 단순한 뉴스 요약을 넘어, 실제 투자자들의 생생한 고민과 토론을 바탕으로 '실패에서 배우고, 깊이 있는 분석으로 기회를 찾으며, 시장의 다양한 신호를 놓치지 않는 것'에 초점을 맞춥니다.

## 1. 금주의 가장 뜨거운 질문 (The Big Question)
목표: 한 주간 커뮤니티에서 가장 논쟁적이었던 주제를 제시하여 독자의 흥미를 즉각적으로 유발합니다.

## 2. 이번 주 집중 분석 (Deep Dive of the Week)
목표: 특정 기업이나 산업에 대한 깊이 있는 분석을 공유합니다.

## 3. 타산지석: 실패에서 배우는 교훈 (The Cautionary Tale)
목표: 리테일 투자자들이 가장 공감하는 '실패 사례'를 통해 실질적인 교훈을 전달합니다.

## 4. 놓치면 안 될 시장의 신호들 (Market Radar)
목표: 큰 이슈는 아니지만, 미래의 투자 아이디어나 리스크가 될 수 있는 작은 신호들을 포착하여 공유합니다.

## 5. 핵심 요약 및 다음 주 관전 포인트 (Final Takeaway)
목표: 이번 주 콘텐츠의 핵심 교훈을 3~4줄로 요약하고, 다음 주에 주목해야 할 이벤트를 제시합니다.

# 분석할 블로그 글

{formatted_content}

위 블로그 글들을 바탕으로 "미국 개미들의 투자노트" 형식의 콘텐츠를 작성해주세요.
"""

    print("Gemini API 호출 중...")
    try:
        response = model.generate_content(prompt)
        result = response.text

        print("\n" + "="*80)
        print("✅ Gemini AI 분석 완료!")
        print("="*80)

        return result

    except Exception as e:
        print(f"❌ Gemini API 에러: {e}")
        return None


# 메인 실행 함수
def main(blog_id, category_no, days=14, gemini_api_key=None):
    """
    전체 프로세스 실행

    Args:
        blog_id: 블로그 ID (예: 'yminsong')
        category_no: 카테고리 번호 (예: 31)
        days: 최근 며칠 이내 글 (기본: 14일)
        gemini_api_key: Gemini API 키 (선택사항)
    """
    print("="*80)
    print("네이버 블로그 크롤러 + Gemini AI 분석")
    print("="*80)
    print(f"블로그 ID: {blog_id}")
    print(f"카테고리: {category_no}")
    print(f"기간: 최근 {days}일")
    print("="*80)

    # 1. 크롤링
    posts = crawl_category_posts(blog_id, category_no, days)

    if not posts:
        print("\n크롤링된 글이 없습니다.")
        return

    # 2. 엑셀 저장
    df = save_to_excel(posts)

    # 3. Gemini 분석 (API 키가 있는 경우)
    if gemini_api_key:
        result = analyze_with_gemini(posts, gemini_api_key)

        if result:
            # 결과 저장
            with open('gemini_analysis.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\n✅ 분석 결과 저장: gemini_analysis.txt")

            if IN_COLAB:
                from google.colab import files
                files.download('gemini_analysis.txt')

            print("\n" + "="*80)
            print("생성된 콘텐츠:")
            print("="*80)
            print(result)
    else:
        print("\n⚠️ Gemini API 키가 없어 분석을 건너뜁니다.")
        print("   API 키를 제공하면 AI 분석이 가능합니다.")

    print("\n" + "="*80)
    print("✅ 모든 작업 완료!")
    print("="*80)


if __name__ == "__main__":
    # 사용 예시
    BLOG_ID = "yminsong"
    CATEGORY_NO = 31
    DAYS = 14

    # Gemini API 키 (선택사항)
    # GEMINI_API_KEY = "your-api-key-here"
    GEMINI_API_KEY = None

    main(BLOG_ID, CATEGORY_NO, DAYS, GEMINI_API_KEY)
