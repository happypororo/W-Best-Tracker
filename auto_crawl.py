#!/usr/bin/env python3
"""
W Concept 자동 크롤링 스크립트
매 시간 16분에 자동으로 모든 카테고리 크롤링 실행
"""

import asyncio
import sys
from datetime import datetime
from wconcept_scraper_v2 import WConceptScraper
from database import Database

async def crawl_all_categories():
    """모든 카테고리 크롤링"""
    print("\n" + "=" * 80)
    print(f"🚀 자동 크롤링 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    categories = ['outer', 'dress', 'blouse', 'shirt', 'tshirt', 'knit', 'skirt', 'underwear']
    all_products = []
    
    for category_key in categories:
        try:
            print(f"\n📦 {category_key} 카테고리 크롤링 중...")
            scraper = WConceptScraper(category_key=category_key)
            products = await scraper.scrape(max_products=200)
            all_products.extend(products)
            print(f"✅ {category_key}: {len(products)}개 수집 완료")
        except Exception as e:
            print(f"❌ {category_key} 크롤링 실패: {str(e)}")
    
    # 데이터베이스에 저장
    if all_products:
        print(f"\n💾 데이터베이스 저장 중... (총 {len(all_products)}개)")
        db = Database()
        db.save_products(all_products)
        print(f"✅ {len(all_products)}개 제품 저장 완료!")
    else:
        print("\n⚠️  수집된 제품이 없습니다.")
    
    print("\n" + "=" * 80)
    print(f"✅ 크롤링 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(crawl_all_categories())
