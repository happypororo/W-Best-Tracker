#!/usr/bin/env python3
"""
W컨셉 베스트 상품 크롤링 가능 여부 테스트 스크립트
"""

import requests
from bs4 import BeautifulSoup
import json
import time

def test_basic_request():
    """기본 HTTP 요청 테스트"""
    print("=" * 60)
    print("1. 기본 HTTP 요청 테스트")
    print("=" * 60)
    
    url = "https://www.wconcept.co.kr/Product/Best"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✓ 상태 코드: {response.status_code}")
        print(f"✓ 응답 길이: {len(response.text)} bytes")
        print(f"✓ Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        # 응답 내용 일부 출력
        print(f"\n응답 내용 샘플 (첫 500자):")
        print(response.text[:500])
        
        return response
    except Exception as e:
        print(f"✗ 오류 발생: {str(e)}")
        return None

def test_api_endpoint():
    """API 엔드포인트 테스트"""
    print("\n" + "=" * 60)
    print("2. API 엔드포인트 테스트")
    print("=" * 60)
    
    # W컨셉이 사용할 가능성이 있는 API 엔드포인트들
    api_urls = [
        "https://www.wconcept.co.kr/api/Product/Best",
        "https://api.wconcept.co.kr/product/best",
        "https://www.wconcept.co.kr/Product/BestList",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    for api_url in api_urls:
        print(f"\n테스트 중: {api_url}")
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            print(f"  ✓ 상태 코드: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ 응답 타입: {response.headers.get('Content-Type', 'N/A')}")
                print(f"  ✓ 응답 샘플: {response.text[:200]}")
        except Exception as e:
            print(f"  ✗ 오류: {str(e)}")

def test_html_structure(response):
    """HTML 구조 분석"""
    print("\n" + "=" * 60)
    print("3. HTML 구조 분석")
    print("=" * 60)
    
    if not response:
        print("✗ 분석할 응답이 없습니다.")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 주요 요소 찾기
    print("\n주요 HTML 요소 탐색:")
    
    # 상품 관련 요소들
    selectors = [
        ('div.product-item', '상품 아이템 div'),
        ('div.product-list', '상품 리스트 div'),
        ('li.product', '상품 리스트 아이템'),
        ('div[class*="product"]', '상품 관련 div (와일드카드)'),
        ('a[class*="product"]', '상품 링크'),
        ('div[id*="product"]', '상품 관련 ID div'),
    ]
    
    for selector, description in selectors:
        elements = soup.select(selector)
        print(f"  - {description}: {len(elements)}개 발견")
        if len(elements) > 0 and len(elements) <= 3:
            print(f"    샘플: {str(elements[0])[:200]}...")
    
    # JavaScript에서 데이터를 로드하는지 확인
    scripts = soup.find_all('script')
    print(f"\n✓ JavaScript 태그: {len(scripts)}개")
    
    # 데이터가 JSON으로 임베드되어 있는지 확인
    for script in scripts[:10]:  # 처음 10개만 확인
        script_text = script.string if script.string else ""
        if any(keyword in script_text for keyword in ['product', 'ranking', 'best', 'data']):
            print(f"  - 관련 스크립트 발견 (샘플): {script_text[:150]}...")
            break

def test_with_selenium():
    """Selenium을 사용한 동적 페이지 로딩 테스트"""
    print("\n" + "=" * 60)
    print("4. Selenium 가능 여부 확인")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✓ Selenium 라이브러리 사용 가능")
        print("  → 동적 페이지 크롤링 가능")
    except ImportError:
        print("✗ Selenium 라이브러리 없음")
        print("  → pip install selenium 필요")

def main():
    print("\n" + "=" * 60)
    print("W컨셉 베스트 상품 크롤링 가능성 분석")
    print("=" * 60)
    print()
    
    # 1. 기본 요청 테스트
    response = test_basic_request()
    
    # 2. API 엔드포인트 테스트
    test_api_endpoint()
    
    # 3. HTML 구조 분석
    if response:
        test_html_structure(response)
    
    # 4. Selenium 확인
    test_with_selenium()
    
    # 결론
    print("\n" + "=" * 60)
    print("분석 결과 및 제안")
    print("=" * 60)
    print("""
요청하신 기능 구현 가능성:

1. Top 200개 브랜드 & 제품 정보 수집:
   → 가능 (단, 페이지 구조에 따라 다름)
   → Selenium + BeautifulSoup 조합 추천

2. 브랜드별 제품 개수 집계:
   → 가능 (1번이 되면 자동으로 가능)
   → 데이터베이스에 저장 후 GROUP BY 사용

3. 가격 변화 추적:
   → 가능 (시계열 데이터로 저장)
   → PostgreSQL 또는 SQLite 사용 추천

4. 정해진 시간마다 반복:
   → 가능 (스케줄러 사용)
   → APScheduler 또는 Celery + Redis 추천
   → 또는 cron job 사용

권장 기술 스택:
- 크롤링: Selenium + BeautifulSoup4
- 데이터베이스: PostgreSQL or SQLite
- 스케줄링: APScheduler
- API: FastAPI
- 프론트엔드: React or Vue.js
- 데이터 시각화: Chart.js or Plotly
    """)

if __name__ == "__main__":
    main()
