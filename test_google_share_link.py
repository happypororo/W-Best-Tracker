#!/usr/bin/env python3
"""
Google 공유 링크를 통한 실제 URL 추적
"""

import asyncio
from playwright.async_api import async_playwright

async def follow_redirect(url):
    """리다이렉트를 따라가서 최종 URL 확인"""
    
    print(f"🔗 원본 URL: {url}")
    print("=" * 70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        try:
            # 리다이렉트 추적
            redirects = []
            
            page.on('response', lambda response: redirects.append({
                'url': response.url,
                'status': response.status,
            }))
            
            print("📡 페이지 접속 중...")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            final_url = page.url
            title = await page.title()
            
            print(f"\n✅ 최종 URL: {final_url}")
            print(f"📄 페이지 제목: {title}")
            
            if redirects:
                print(f"\n🔄 리다이렉트 경로 ({len(redirects)}단계):")
                for i, redirect in enumerate(redirects[:10], 1):
                    print(f"  [{i}] {redirect['status']} - {redirect['url'][:100]}")
            
            # 페이지 소스 일부 저장
            content = await page.content()
            print(f"\n📏 페이지 크기: {len(content):,} bytes")
            
            # 상품 요소 찾기
            print("\n🔍 상품 요소 탐색:")
            selectors = [
                'div[class*="product"]',
                'li[class*="product"]',
                'div[class*="item"]',
                'a[href*="/Product/"]',
                'img[alt]',
            ]
            
            for selector in selectors:
                count = await page.locator(selector).count()
                if count > 0:
                    print(f"  ✓ {selector:40s} : {count}개")
            
            # 스크린샷
            await page.screenshot(path='/home/user/webapp/final_page.png', full_page=False)
            print("\n📸 스크린샷 저장: final_page.png")
            
            # 페이지 소스 저장
            with open('/home/user/webapp/final_page_source.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("💾 페이지 소스 저장: final_page_source.html")
            
            return final_url
            
        except Exception as e:
            print(f"\n❌ 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await browser.close()

async def main():
    url = "https://share.google/HxQfDFfSgTeLZrnoe"
    await follow_redirect(url)

if __name__ == "__main__":
    asyncio.run(main())
