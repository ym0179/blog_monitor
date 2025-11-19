"""
Chrome/ChromeDriver 문제 진단 스크립트
구글 Colab에서 실행하여 문제를 파악합니다.
"""

import subprocess
import os
import sys


def run_command(cmd, description):
    """명령어 실행 및 결과 출력"""
    print(f"\n{'='*80}")
    print(f"🔍 {description}")
    print(f"{'='*80}")
    print(f"실행 명령어: {cmd}")
    print("-" * 80)
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(f"⚠️ 에러: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 실행 실패: {str(e)}")
        return False


def check_file_exists(filepath, description):
    """파일 존재 여부 확인"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists


def main():
    print("="*80)
    print("🔧 Chrome/ChromeDriver 환경 진단")
    print("="*80)

    # 1. Python 버전
    print(f"\n📌 Python 버전: {sys.version}")

    # 2. Chrome/Chromium 설치 확인
    print("\n" + "="*80)
    print("1️⃣ Chrome/Chromium 설치 상태")
    print("="*80)

    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/snap/bin/chromium"
    ]

    chrome_found = False
    chrome_path = None
    for path in chrome_paths:
        if check_file_exists(path, "Chrome 바이너리"):
            chrome_found = True
            chrome_path = path
            break

    if not chrome_found:
        print("\n⚠️ Chrome/Chromium이 설치되지 않았습니다!")
        print("해결: !apt-get install -y chromium-browser")

    # 3. Chrome 버전 확인
    if chrome_found:
        run_command(f"{chrome_path} --version", "Chrome 버전 확인")

    # 4. ChromeDriver 확인
    print("\n" + "="*80)
    print("2️⃣ ChromeDriver 설치 상태")
    print("="*80)

    driver_paths = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        "/usr/lib/chromium-browser/chromedriver"
    ]

    driver_found = False
    for path in driver_paths:
        if check_file_exists(path, "ChromeDriver"):
            driver_found = True
            run_command(f"{path} --version", "ChromeDriver 버전 확인")
            break

    if not driver_found:
        print("\n⚠️ ChromeDriver가 설치되지 않았습니다!")
        print("해결: webdriver-manager를 사용하거나 수동 설치 필요")

    # 5. Selenium 설치 확인
    print("\n" + "="*80)
    print("3️⃣ Python 패키지 설치 상태")
    print("="*80)

    try:
        import selenium
        print(f"✅ Selenium 버전: {selenium.__version__}")
    except ImportError:
        print("❌ Selenium이 설치되지 않았습니다!")

    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup4 설치됨")
    except ImportError:
        print("❌ BeautifulSoup4가 설치되지 않았습니다!")

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ webdriver-manager 설치됨")
    except ImportError:
        print("❌ webdriver-manager가 설치되지 않았습니다!")

    # 6. 환경 변수 확인
    print("\n" + "="*80)
    print("4️⃣ 환경 변수")
    print("="*80)

    important_vars = ['PATH', 'HOME', 'DISPLAY']
    for var in important_vars:
        value = os.environ.get(var, 'NOT SET')
        print(f"{var}: {value[:100]}")

    # 7. /tmp 디렉토리 확인
    print("\n" + "="*80)
    print("5️⃣ 임시 디렉토리 확인")
    print("="*80)

    run_command("ls -la /tmp | head -20", "/tmp 디렉토리 내용")
    run_command("df -h /tmp", "/tmp 디스크 공간")

    # 8. Chrome 실행 테스트
    print("\n" + "="*80)
    print("6️⃣ Chrome 직접 실행 테스트")
    print("="*80)

    if chrome_found:
        test_cmd = f"{chrome_path} --headless --no-sandbox --disable-gpu --dump-dom about:blank 2>&1 | head -5"
        run_command(test_cmd, "Chrome headless 모드 테스트")

    # 9. 프로세스 확인
    print("\n" + "="*80)
    print("7️⃣ 실행 중인 Chrome 프로세스")
    print("="*80)

    run_command("ps aux | grep -i chrome | grep -v grep", "Chrome 프로세스 확인")

    # 10. 권한 확인
    print("\n" + "="*80)
    print("8️⃣ 현재 사용자 및 권한")
    print("="*80)

    run_command("whoami", "현재 사용자")
    run_command("id", "사용자 정보")

    # 결과 요약
    print("\n" + "="*80)
    print("📋 진단 요약")
    print("="*80)

    issues = []

    if not chrome_found:
        issues.append("Chrome/Chromium이 설치되지 않았습니다")

    if not driver_found:
        issues.append("ChromeDriver가 설치되지 않았습니다")

    if issues:
        print("\n⚠️ 발견된 문제:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

        print("\n💡 권장 해결 방법 (Colab에서 실행):")
        print("\n# 방법 1: apt-get으로 설치 (권장)")
        print("!apt-get update")
        print("!apt-get install -y chromium-browser chromium-chromedriver")
        print("!pip install selenium beautifulsoup4")

        print("\n# 방법 2: webdriver-manager 사용")
        print("!pip install selenium beautifulsoup4 webdriver-manager")
    else:
        print("\n✅ 모든 기본 구성 요소가 설치되어 있습니다")
        print("Chrome 실행 옵션에 문제가 있을 수 있습니다")

    print("\n" + "="*80)
    print("진단 완료!")
    print("="*80)


if __name__ == "__main__":
    main()
