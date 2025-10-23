#!/usr/bin/env python3
"""
Selenium을 사용한 W컨셉 베스트 상품 페이지 크롤링 테스트
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time

def setup_driver():
    """Selenium WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"✗ Chrome WebDriver 초기화 실패: {str(e)}")
        return None

def test_page_load(driver):
    """페이지 로딩 테스트"""
    print("=" * 60)
    print("1. Selenium을 통한 페이지 로딩 테스트")
    print("=" * 60)
    
    url = "https://www.wconcept.co.kr/Product/Best"
    
    try:
        print(f"페이지 접속 중: {url}")
        driver.get(url)
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        print(f"✓ 페이지 제목: {driver.title}")
        print(f"✓ 현재 URL: {driver.current_url}")
        print(f"✓ 페이지 소스 길이: {len(driver.page_source)} bytes")
        
        # 페이지 소스 일부 출력
        print(f"\n페이지 소스 샘플 (첫 500자):")
        print(driver.page_source[:500])
        
        return True
    except Exception as e:
        print(f"✗ 페이지 로딩 실패: {str(e)}")
        return False

def analyze_page_structure(driver):
    """페이지 구조 분석"""
    print("\n" + "=" * 60)
    print("2. 페이지 구조 상세 분석")
    print("=" * 60)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 다양한 셀렉터로 상품 요소 찾기
    selectors = [
        ('div.product-item', '상품 아이템 div'),
        ('div.product-card', '상품 카드 div'),
        ('li.product', '상품 리스트 아이템'),
        ('div[class*="product"]', '상품 관련 div (부분 일치)'),
        ('div[class*="item"]', '아이템 관련 div (부분 일치)'),
        ('div[class*="card"]', '카드 관련 div (부분 일치)'),
        ('a[href*="/Product/"]', '상품 상세 링크'),
        ('img[alt*=""]', '상품 이미지'),
    ]
    
    print("\n주요 HTML 요소 탐색:")
    for selector, description in selectors:
        elements = soup.select(selector)
        print(f"  - {description}: {len(elements)}개")
        
        if len(elements) > 0 and len(elements) <= 5:
            print(f"    샘플 (첫 번째 요소의 클래스): {elements[0].get('class', 'N/A')}")
    
    # 특정 ID나 클래스 찾기
    print("\n\n주요 컨테이너 요소:")
    container_selectors = [
        '#productList',
        '#bestList',
        '.product-list',
        '.best-list',
        '[id*="product"]',
        '[id*="best"]',
    ]
    
    for selector in container_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"  ✓ 발견: {selector} → {len(elements)}개")
            for idx, elem in enumerate(elements[:2]):
                print(f"    [{idx+1}] ID: {elem.get('id', 'N/A')}, Class: {elem.get('class', 'N/A')}")

def extract_sample_products(driver):
    """샘플 상품 데이터 추출 시도"""
    print("\n" + "=" * 60)
    print("3. 샘플 상품 데이터 추출 시도")
    print("=" * 60)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 다양한 방법으로 상품 정보 추출 시도
    print("\n방법 1: 링크에서 상품 URL 추출")
    product_links = soup.select('a[href*="/Product/"]')
    print(f"  → 상품 링크 {len(product_links)}개 발견")
    if product_links:
        for i, link in enumerate(product_links[:3]):
            print(f"    [{i+1}] {link.get('href', 'N/A')}")
    
    print("\n방법 2: 이미지에서 상품 정보 추출")
    images = soup.select('img[src*="image"]')
    print(f"  → 이미지 {len(images)}개 발견")
    if images:
        for i, img in enumerate(images[:3]):
            print(f"    [{i+1}] Alt: {img.get('alt', 'N/A')[:50]}")
    
    print("\n방법 3: 가격 정보 추출")
    price_selectors = [
        '[class*="price"]',
        '[class*="Price"]',
        '[class*="cost"]',
        'span.price',
        'div.price',
        'strong[class*="price"]',
    ]
    
    for selector in price_selectors:
        prices = soup.select(selector)
        if prices:
            print(f"  ✓ {selector}: {len(prices)}개 발견")
            for i, price in enumerate(prices[:3]):
                print(f"    [{i+1}] {price.get_text(strip=True)[:50]}")
            break

def check_dynamic_loading(driver):
    """동적 로딩 확인"""
    print("\n" + "=" * 60)
    print("4. 동적 컨텐츠 로딩 확인")
    print("=" * 60)
    
    # 초기 페이지 소스 길이
    initial_length = len(driver.page_source)
    print(f"초기 페이지 소스 길이: {initial_length} bytes")
    
    # 스크롤 다운
    print("페이지 하단으로 스크롤 중...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # 스크롤 후 페이지 소스 길이
    after_scroll_length = len(driver.page_source)
    print(f"스크롤 후 페이지 소스 길이: {after_scroll_length} bytes")
    
    if after_scroll_length > initial_length:
        print("✓ 동적 로딩 감지됨 (무한 스크롤 가능성)")
    else:
        print("→ 추가 로딩 없음")

def analyze_network_requests(driver):
    """네트워크 요청 분석 (가능한 경우)"""
    print("\n" + "=" * 60)
    print("5. 네트워크 요청 분석")
    print("=" * 60)
    
    # 브라우저 로그 확인
    try:
        logs = driver.get_log('performance')
        print(f"✓ Performance 로그: {len(logs)}개 이벤트")
        
        # API 호출 찾기
        api_calls = []
        for entry in logs:
            message = json.loads(entry['message'])
            if 'Network.requestWillBeSent' in message['message']['method']:
                url = message['message']['params']['request']['url']
                if 'api' in url.lower() or 'product' in url.lower():
                    api_calls.append(url)
        
        if api_calls:
            print(f"✓ API 호출 발견: {len(api_calls)}개")
            for i, url in enumerate(api_calls[:5]):
                print(f"    [{i+1}] {url}")
        else:
            print("→ 명확한 API 호출 없음")
            
    except Exception as e:
        print(f"✗ 네트워크 로그 분석 불가: {str(e)}")

def main():
    print("\n" + "=" * 60)
    print("W컨셉 베스트 상품 Selenium 크롤링 테스트")
    print("=" * 60)
    print()
    
    # WebDriver 설정
    driver = setup_driver()
    
    if not driver:
        print("\n✗ WebDriver 초기화 실패 - 테스트 중단")
        return
    
    try:
        # 1. 페이지 로딩 테스트
        if not test_page_load(driver):
            print("\n✗ 페이지 로딩 실패 - 추가 테스트 불가")
            return
        
        # 2. 페이지 구조 분석
        analyze_page_structure(driver)
        
        # 3. 샘플 데이터 추출
        extract_sample_products(driver)
        
        # 4. 동적 로딩 확인
        check_dynamic_loading(driver)
        
        # 5. 네트워크 분석
        # analyze_network_requests(driver)  # 추가 설정 필요
        
        # 최종 결론
        print("\n" + "=" * 60)
        print("최종 분석 결과")
        print("=" * 60)
        print("""
✓ Selenium을 통한 접근: 가능
✓ 페이지 로딩: 확인됨
✓ HTML 파싱: 가능

다음 단계:
1. 정확한 셀렉터 찾기 (개발자 도구로 확인 필요)
2. 상품 데이터 구조 파악
3. 페이징/무한스크롤 처리 로직 구현
4. 데이터베이스 스키마 설계
5. 스케줄러 구현

권장 구현 방식:
- Selenium으로 페이지 렌더링
- BeautifulSoup으로 HTML 파싱
- SQLite/PostgreSQL에 시계열 데이터 저장
- APScheduler로 주기적 실행
- FastAPI로 데이터 조회 API 제공
- React/Vue로 대시보드 구현
        """)
        
    finally:
        driver.quit()
        print("\n✓ WebDriver 종료됨")

if __name__ == "__main__":
    main()
