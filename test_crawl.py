#!/usr/bin/env python3
"""
테스트용 간단한 크롤링 스크립트
1개 카테고리, 50개 제품만 수집
"""

import asyncio
import sys
from datetime import datetime
from wconcept_scraper_v2 import WConceptScraper
from database import Database

async def test_crawl():
    """테스트 크롤링 - 1개 카테고리만"""
    print("\n" + "=" * 80)
    print(f"🧪 테스트 크롤링 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    try:
        print(f"\n📦 outer 카테고리 크롤링 중 (최대 50개)...")
        scraper = WConceptScraper(category_key='outer')
        products = await scraper.scrape(max_products=50)
        print(f"✅ outer: {len(products)}개 수집 완료")
        
        # 데이터베이스에 저장
        if products:
            print(f"\n💾 데이터베이스 저장 중... (총 {len(products)}개)")
            db = Database()
            db.save_products(products)
            print(f"✅ {len(products)}개 제품 저장 완료!")
        else:
            print("\n⚠️  수집된 제품이 없습니다.")
        
        print("\n" + "=" * 80)
        print(f"✅ 테스트 크롤링 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")
        
        return len(products)
    
    except Exception as e:
        print(f"❌ 크롤링 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    result = asyncio.run(test_crawl())
    sys.exit(0 if result > 0 else 1)
