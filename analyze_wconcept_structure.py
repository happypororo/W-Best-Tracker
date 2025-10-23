#!/usr/bin/env python3
"""
W컨셉 페이지 구조 분석 도구
Playwright를 사용하여 실제 페이지를 분석합니다.
"""

import asyncio
import json
from datetime import datetime

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright가 설치되지 않았습니다.")
    print("   설치 명령: pip install playwright && playwright install chromium")


async def analyze_wconcept_page():
    """W컨셉 베스트 페이지 구조 분석"""
    
    if not PLAYWRIGHT_AVAILABLE:
        print("\n❌ Playwright를 먼저 설치해주세요:")
        print("   pip install playwright")
        print("   playwright install chromium")
        return
    
    print("=" * 70)
    print("W컨셉 베스트 상품 페이지 구조 분석")
    print("=" * 70)
    print()
    
    async with async_playwright() as p:
        # 브라우저 실행
        print("🌐 브라우저 실행 중...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            # 페이지 접속
            url = "https://www.wconcept.co.kr/Product/Best"
            print(f"📡 페이지 접속 중: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 페이지 기본 정보
            title = await page.title()
            current_url = page.url
            
            print(f"\n✅ 페이지 로딩 완료")
            print(f"   제목: {title}")
            print(f"   URL: {current_url}")
            
            # JavaScript 실행 대기
            print("\n⏳ 페이지 렌더링 대기 중...")
            await asyncio.sleep(3)
            
            # 스크롤하여 더 많은 상품 로드
            print("📜 페이지 스크롤 중...")
            for i in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
            
            # HTML 구조 분석
            print("\n" + "=" * 70)
            print("HTML 구조 분석")
            print("=" * 70)
            
            # 다양한 셀렉터로 상품 요소 찾기
            selectors = [
                'div.product-item',
                'div.product-card',
                'li.product',
                'div[class*="product"]',
                'div[class*="item"]',
                'div[class*="card"]',
                'a[href*="/Product/"]',
                'article',
                '[data-product-id]',
                '[data-item-id]',
            ]
            
            print("\n📦 상품 컨테이너 탐색:")
            found_selectors = []
            
            for selector in selectors:
                try:
                    count = await page.locator(selector).count()
                    if count > 0:
                        print(f"  ✓ {selector:40s} : {count:4d}개")
                        found_selectors.append((selector, count))
                except Exception as e:
                    pass
            
            if not found_selectors:
                print("  ⚠️  기본 셀렉터로 상품을 찾을 수 없습니다.")
                print("  🔍 페이지 소스 분석 중...")
                
                # 페이지 소스 저장
                content = await page.content()
                with open('/home/user/webapp/wconcept_page_source.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  💾 페이지 소스 저장됨: wconcept_page_source.html ({len(content)} bytes)")
            
            # 가장 많이 발견된 셀렉터로 샘플 추출
            if found_selectors:
                best_selector, count = max(found_selectors, key=lambda x: x[1])
                print(f"\n🎯 최적 셀렉터: {best_selector} ({count}개)")
                
                # 첫 3개 요소 분석
                print("\n📋 샘플 상품 데이터 추출 (첫 3개):")
                for i in range(min(3, count)):
                    element = page.locator(best_selector).nth(i)
                    
                    # 텍스트 추출
                    text = await element.inner_text()
                    # HTML 추출
                    html = await element.inner_html()
                    
                    print(f"\n  [{i+1}] 상품 정보:")
                    print(f"      텍스트: {text[:100]}...")
                    print(f"      HTML 구조 샘플: {html[:200]}...")
            
            # 이미지 분석
            print("\n" + "=" * 70)
            print("이미지 분석")
            print("=" * 70)
            
            images = page.locator('img')
            img_count = await images.count()
            print(f"\n🖼️  총 이미지: {img_count}개")
            
            if img_count > 0:
                print("\n샘플 이미지 (첫 5개):")
                for i in range(min(5, img_count)):
                    img = images.nth(i)
                    src = await img.get_attribute('src')
                    alt = await img.get_attribute('alt')
                    print(f"  [{i+1}] src: {src[:80] if src else 'N/A'}...")
                    print(f"      alt: {alt[:80] if alt else 'N/A'}")
            
            # 링크 분석
            print("\n" + "=" * 70)
            print("링크 분석")
            print("=" * 70)
            
            product_links = page.locator('a[href*="/Product/"]')
            link_count = await product_links.count()
            print(f"\n🔗 상품 링크: {link_count}개")
            
            if link_count > 0:
                print("\n샘플 링크 (첫 5개):")
                for i in range(min(5, link_count)):
                    link = product_links.nth(i)
                    href = await link.get_attribute('href')
                    text = await link.inner_text()
                    print(f"  [{i+1}] href: {href}")
                    print(f"      text: {text[:50] if text.strip() else '(이미지 링크)'}...")
            
            # 가격 정보 분석
            print("\n" + "=" * 70)
            print("가격 정보 분석")
            print("=" * 70)
            
            price_patterns = [
                'span[class*="price"]',
                'div[class*="price"]',
                'strong[class*="price"]',
                '[class*="Price"]',
                '[class*="cost"]',
            ]
            
            print("\n💰 가격 요소 탐색:")
            for pattern in price_patterns:
                try:
                    count = await page.locator(pattern).count()
                    if count > 0:
                        print(f"  ✓ {pattern:40s} : {count:4d}개")
                        
                        # 샘플 추출
                        for i in range(min(3, count)):
                            elem = page.locator(pattern).nth(i)
                            text = await elem.inner_text()
                            if text.strip():
                                print(f"      샘플: {text.strip()}")
                except Exception:
                    pass
            
            # 네트워크 요청 분석
            print("\n" + "=" * 70)
            print("네트워크 요청 분석")
            print("=" * 70)
            
            # 새로운 페이지로 네트워크 모니터링
            print("\n🌐 API 호출 감지 중...")
            
            api_calls = []
            
            async def handle_request(request):
                url = request.url
                if any(keyword in url.lower() for keyword in ['api', 'product', 'best', 'ranking']):
                    api_calls.append({
                        'url': url,
                        'method': request.method,
                        'resource_type': request.resource_type
                    })
            
            page.on('request', handle_request)
            
            # 페이지 새로고침하여 네트워크 요청 캡처
            await page.reload(wait_until='networkidle')
            await asyncio.sleep(2)
            
            if api_calls:
                print(f"\n✅ API 호출 발견: {len(api_calls)}개")
                for i, call in enumerate(api_calls[:10], 1):
                    print(f"\n  [{i}] {call['method']} - {call['resource_type']}")
                    print(f"      {call['url']}")
            else:
                print("\n⚠️  명확한 API 호출을 감지하지 못했습니다.")
                print("   → HTML에 데이터가 직접 포함되어 있을 가능성")
            
            # 스크린샷 캡처
            print("\n📸 스크린샷 캡처 중...")
            await page.screenshot(path='/home/user/webapp/wconcept_screenshot.png', full_page=True)
            print("   💾 저장됨: wconcept_screenshot.png")
            
            # 최종 결과 요약
            print("\n" + "=" * 70)
            print("분석 결과 요약")
            print("=" * 70)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'url': current_url,
                'title': title,
                'selectors_found': len(found_selectors),
                'product_links': link_count,
                'images': img_count,
                'api_calls': len(api_calls),
                'best_selector': best_selector if found_selectors else None,
                'selector_details': [{'selector': s, 'count': c} for s, c in found_selectors],
                'api_endpoints': [call['url'] for call in api_calls]
            }
            
            with open('/home/user/webapp/analysis_result.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"""
✅ 분석 완료!

📊 결과:
   - 발견된 셀렉터: {len(found_selectors)}개
   - 상품 링크: {link_count}개
   - 이미지: {img_count}개
   - API 호출: {len(api_calls)}개

💾 저장된 파일:
   - analysis_result.json (분석 결과)
   - wconcept_page_source.html (페이지 소스)
   - wconcept_screenshot.png (스크린샷)

🎯 다음 단계:
   1. analysis_result.json을 확인하여 최적 셀렉터 파악
   2. wconcept_page_source.html에서 데이터 구조 분석
   3. 실제 크롤러 구현 시작
            """)
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
            print("\n✅ 브라우저 종료됨")


def main():
    """메인 함수"""
    if not PLAYWRIGHT_AVAILABLE:
        print("\n" + "=" * 70)
        print("설치 가이드")
        print("=" * 70)
        print("""
Playwright 설치가 필요합니다:

1. Playwright 라이브러리 설치:
   pip install playwright

2. 브라우저 설치:
   playwright install chromium

3. 스크립트 재실행:
   python analyze_wconcept_structure.py
        """)
        return
    
    # 비동기 함수 실행
    asyncio.run(analyze_wconcept_page())


if __name__ == "__main__":
    main()
