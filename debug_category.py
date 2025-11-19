# 디버깅용 코드 - Colab에서 실행하세요

import time
import google_colab_selenium as gs
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# WebDriver 설정
chrome_options = Options()
chrome_options.add_argument('--window-size=1920,1080')
driver = gs.Chrome(options=chrome_options)

# 카테고리 페이지 접속
blog_id = "yminsong"
category_no = 31
url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}&categoryNo={category_no}"

print(f"접속: {url}")
driver.get(url)
time.sleep(5)

# 페이지 소스 확인
html = BeautifulSoup(driver.page_source, "html.parser")

# iframe 찾기
print("\n=== iframe 찾기 ===")
iframes = html.find_all('iframe')
print(f"발견된 iframe 개수: {len(iframes)}")
for idx, iframe in enumerate(iframes):
    print(f"iframe {idx}: id={iframe.get('id')}, name={iframe.get('name')}")

# 직접 테이블 찾기 (iframe 없이)
print("\n=== 직접 테이블 찾기 (iframe 없이) ===")
table = html.select_one("table.blog2_list.blog2_categorylist")
if table:
    print("✅ iframe 없이 테이블 발견!")
    rows = table.select("tbody tr")
    print(f"행 개수: {len(rows)}")
else:
    print("❌ iframe 없이는 테이블을 찾을 수 없음")

# iframe 전환 후 찾기
print("\n=== iframe 전환 후 찾기 ===")
try:
    # mainFrame 찾기
    iframe_elem = driver.find_element(By.ID, "mainFrame")
    driver.switch_to.frame(iframe_elem)
    print("✅ mainFrame으로 전환 성공")

    time.sleep(2)
    html2 = BeautifulSoup(driver.page_source, "html.parser")
    table2 = html2.select_one("table.blog2_list.blog2_categorylist")

    if table2:
        print("✅ iframe 안에서 테이블 발견!")
        rows2 = table2.select("tbody tr")
        print(f"행 개수: {len(rows2)}")

        # 첫 번째 행 정보 출력
        if rows2:
            first_row = rows2[0]
            title_elem = first_row.select_one("td.title a")
            date_elem = first_row.select_one("td.date span.date")
            if title_elem:
                print(f"\n첫 번째 글:")
                print(f"  제목: {title_elem.get_text(strip=True)}")
                print(f"  날짜: {date_elem.get_text(strip=True) if date_elem else '없음'}")
    else:
        print("❌ iframe 안에도 테이블 없음")

except Exception as e:
    print(f"❌ iframe 전환 실패: {e}")

driver.quit()
print("\n디버깅 완료!")