#!/usr/bin/env python3
"""
W컨셉 베스트 상품 크롤러 v2
실제 URL: https://display.wconcept.co.kr/rn/best?displayCategoryType=10101&displaySubCategoryType=10101201&gnbType=Y
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

class WConceptScraper:
    """W컨셉 베스트 상품 크롤러"""
    
    def __init__(self):
        self.url = "https://display.wconcept.co.kr/rn/best?displayCategoryType=10101&displaySubCategoryType=10101201&gnbType=Y"
        self.products = []
    
    async def scrape(self, max_products=200):
        """상품 데이터 크롤링"""
        
        print("=" * 70)
        print("W컨셉 베스트 상품 크롤링 시작")
        print("=" * 70)
        print(f"🎯 목표: {max_products}개 상품 수집")
        print(f"🔗 URL: {self.url}")
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
                print(f"📡 페이지 접속 중...")
                await page.goto(self.url, wait_until='domcontentloaded', timeout=30000)
                
                # 페이지 로딩 대기
                print("⏳ 페이지 로딩 대기...")
                await asyncio.sleep(5)
                
                # 상품이 로드될 때까지 대기
                try:
                    await page.wait_for_selector('div.product-item', timeout=10000)
                    print("✓ 상품 요소 로드됨")
                except:
                    print("⚠️  상품 요소 로드 타임아웃 (계속 진행)")
                
                # 스크롤하여 모든 상품 로드
                print(f"📜 스크롤하여 {max_products}개 상품 로딩...")
                await self._scroll_to_load_products(page, max_products)
                
                # 페이지 소스 가져오기
                content = await page.content()
                
                # BeautifulSoup으로 파싱
                print("🔍 HTML 파싱 중...")
                soup = BeautifulSoup(content, 'html.parser')
                
                # 상품 요소 찾기
                product_elements = soup.select('div.product-item')
                print(f"✅ 발견된 상품: {len(product_elements)}개")
                
                # 각 상품 정보 추출
                print("\n📦 상품 정보 추출 중...")
                for idx, elem in enumerate(product_elements[:max_products], 1):
                    try:
                        product = self._extract_product_info(elem, idx)
                        if product:
                            self.products.append(product)
                            if idx % 20 == 0:
                                print(f"   진행: {idx}/{max_products}...")
                    except Exception as e:
                        print(f"   ⚠️  상품 {idx} 추출 실패: {str(e)}")
                
                print(f"\n✅ 총 {len(self.products)}개 상품 수집 완료!")
                
                # 결과 저장
                self._save_results()
                
            except Exception as e:
                print(f"\n❌ 오류 발생: {str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                await browser.close()
                print("\n✅ 브라우저 종료")
        
        return self.products
    
    async def _scroll_to_load_products(self, page, target_count):
        """스크롤하여 상품 로드"""
        last_count = 0
        scroll_attempts = 0
        max_scrolls = 20  # 최대 스크롤 횟수
        
        while scroll_attempts < max_scrolls:
            # 현재 로드된 상품 수 확인
            current_count = await page.locator('div.product-item').count()
            
            if current_count >= target_count:
                print(f"   ✓ {current_count}개 상품 로드됨")
                break
            
            # 변화가 없으면 중단
            if current_count == last_count:
                scroll_attempts += 1
                if scroll_attempts >= 3:
                    print(f"   ⚠️  더 이상 로드되지 않음 (현재: {current_count}개)")
                    break
            else:
                scroll_attempts = 0
            
            last_count = current_count
            
            # 페이지 끝까지 스크롤
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1.5)
    
    def _extract_product_info(self, elem, rank):
        """상품 정보 추출"""
        
        # 브랜드명과 상품명 (prdc-title 안에 있음)
        title_section = elem.select_one('.prdc-title')
        if title_section:
            title_spans = title_section.select('span.text')
            brand_name = title_spans[0].get_text(strip=True) if len(title_spans) > 0 else "N/A"
            product_name = title_spans[1].get_text(strip=True) if len(title_spans) > 1 else "N/A"
        else:
            brand_name = "N/A"
            product_name = "N/A"
        
        # 가격 정보
        price_info = self._extract_price_info(elem)
        
        # 이미지
        img_elem = elem.select_one('img')
        image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else "N/A"
        
        # 상품 링크 (area-click 버튼에서 추출)
        link_elem = elem.select_one('button.area-click')
        product_url = "N/A"
        
        # 버튼에서 직접 URL을 가져올 수 없으므로 이미지 URL에서 ID 추출하여 구성
        if not link_elem:
            link_elem = elem.select_one('a')
            if link_elem:
                product_url = link_elem.get('href', "N/A")
                if product_url and product_url != "N/A" and not product_url.startswith('http'):
                    product_url = f"https://display.wconcept.co.kr{product_url}"
        
        # 상품 ID 추출 - 이미지 URL을 우선 사용
        product_id = None
        
        # 이미지 URL에서 상품 번호 추출 (예: 307602440_MA70111.jpg → 307602440)
        if image_url and image_url != "N/A":
            img_match = re.search(r'/(\d+)_[A-Z0-9]+\.jpg', image_url)
            if img_match:
                product_id = f"PROD_{img_match.group(1)}"
        
        # 이미지에서 실패하면 URL에서 시도
        if not product_id:
            product_id = self._extract_product_id(product_url)
        
        # 그래도 실패하면 rank와 브랜드/상품명 조합으로 고유 ID 생성
        if not product_id or product_id == "PROD_0":
            unique_str = f"{rank}_{brand_name}_{product_name}"
            product_id = f"PROD_{abs(hash(unique_str)) % 10000000:07d}"
        
        return {
            'rank': rank,
            'product_id': product_id,
            'product_name': product_name,
            'brand_name': brand_name,
            'original_price': price_info['original_price'],
            'sale_price': price_info['sale_price'],
            'discount_rate': price_info['discount_rate'],
            'image_url': image_url,
            'product_url': product_url,
            'collected_at': datetime.now().isoformat()
        }
    
    def _extract_price_info(self, elem):
        """가격 정보 추출"""
        price_info = {
            'original_price': None,
            'sale_price': None,
            'discount_rate': None
        }
        
        # 숫자만 추출하는 함수
        def extract_number(text):
            if not text:
                return None
            # 숫자와 쉼표만 추출
            numbers = re.findall(r'[\d,]+', text)
            if numbers:
                return int(numbers[0].replace(',', ''))
            return None
        
        # 가격 섹션 찾기
        price_section = elem.select_one('.prdc-price')
        if price_section:
            # 원가
            customer_price_elem = price_section.select_one('.customer-price')
            if customer_price_elem:
                price_info['original_price'] = extract_number(customer_price_elem.get_text(strip=True))
            
            # 할인율
            discount_elem = price_section.select_one('.final-discount em')
            if discount_elem:
                discount_match = re.search(r'(\d+)', discount_elem.get_text(strip=True))
                if discount_match:
                    price_info['discount_rate'] = int(discount_match.group(1))
            
            # 최종 판매가
            final_price_elem = price_section.select_one('.final-price strong')
            if final_price_elem:
                price_info['sale_price'] = extract_number(final_price_elem.get_text(strip=True))
        
        # 할인가가 없으면 판매가를 원가로
        if not price_info['sale_price'] and price_info['original_price']:
            price_info['sale_price'] = price_info['original_price']
        
        return price_info
    
    def _extract_product_id(self, url):
        """URL에서 상품 ID 추출"""
        if not url or url == "N/A":
            # URL이 없으면 이미지 URL에서 ID 추출 시도
            return None
        
        # URL 패턴에서 ID 추출 시도
        patterns = [
            r'/product/(\d+)',
            r'/goods/(\d+)',
            r'productId=(\d+)',
            r'goodsId=(\d+)',
            r'/(\d+)$',  # URL 끝의 숫자
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f"PROD_{match.group(1)}"
        
        # 추출 실패 시 URL 해시값 사용
        return f"PROD_{abs(hash(url)) % 1000000:06d}"
    
    def _save_results(self):
        """결과 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON 파일로 저장
        json_file = f'/home/user/webapp/wconcept_data_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'collected_at': datetime.now().isoformat(),
                'total_products': len(self.products),
                'products': self.products
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 데이터 저장: {json_file}")
        
        # 요약 통계
        self._print_summary()
    
    def _print_summary(self):
        """수집 결과 요약"""
        if not self.products:
            return
        
        print("\n" + "=" * 70)
        print("수집 결과 요약")
        print("=" * 70)
        
        # 브랜드별 집계
        brand_counts = {}
        for product in self.products:
            brand = product['brand_name']
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        # 상위 10개 브랜드
        top_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"\n📊 상위 10개 브랜드:")
        for i, (brand, count) in enumerate(top_brands, 1):
            print(f"   {i:2d}. {brand:30s} : {count:3d}개")
        
        # 가격 통계
        prices = [p['sale_price'] for p in self.products if p['sale_price']]
        if prices:
            print(f"\n💰 가격 통계:")
            print(f"   평균가: {sum(prices) / len(prices):,.0f}원")
            print(f"   최저가: {min(prices):,.0f}원")
            print(f"   최고가: {max(prices):,.0f}원")
        
        # 할인 통계
        discounted = [p for p in self.products if p['discount_rate']]
        if discounted:
            discount_rates = [p['discount_rate'] for p in discounted]
            print(f"\n🏷️  할인 통계:")
            print(f"   할인 상품: {len(discounted)}개 ({len(discounted)/len(self.products)*100:.1f}%)")
            print(f"   평균 할인율: {sum(discount_rates) / len(discount_rates):.1f}%")
            print(f"   최대 할인율: {max(discount_rates)}%")


async def main():
    """메인 함수"""
    scraper = WConceptScraper()
    products = await scraper.scrape(max_products=200)
    
    print(f"\n✅ 크롤링 완료! 총 {len(products)}개 상품 수집됨")
    
    # 샘플 출력
    if products:
        print("\n📦 샘플 상품 (첫 3개):")
        for product in products[:3]:
            print(f"\n   [{product['rank']}] {product['brand_name']} - {product['product_name'][:50]}")
            print(f"       가격: {product['sale_price']:,}원")
            if product['discount_rate']:
                print(f"       할인: {product['discount_rate']}% OFF")

if __name__ == "__main__":
    asyncio.run(main())
