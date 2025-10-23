#!/usr/bin/env python3
"""
모든 카테고리의 데이터를 수집하는 스크립트
"""
import asyncio
from wconcept_scraper_v2 import WConceptScraper
from database import Database
import json
from datetime import datetime

async def crawl_all_categories():
    """모든 카테고리 크롤링"""
    
    categories = ['outer', 'dress', 'blouse', 'shirt', 'tshirt', 'knit', 'skirt', 'underwear']
    db = Database('wconcept_tracking.db')
    
    print("=" * 70)
    print("W컨셉 전체 카테고리 크롤링 시작")
    print("=" * 70)
    print(f"수집할 카테고리: {len(categories)}개")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_products = []
    
    for idx, category in enumerate(categories, 1):
        print(f"\n[{idx}/{len(categories)}] {category.upper()} 카테고리 크롤링 중...")
        print("-" * 70)
        
        try:
            scraper = WConceptScraper(category_key=category)
            products = await scraper.scrape(max_products=200)
            
            if products:
                print(f"✅ {len(products)}개 상품 수집 완료")
                all_products.extend(products)
                
                # 데이터베이스에 저장
                saved_count = db.save_products(products)
                print(f"💾 데이터베이스에 {saved_count}개 저장됨")
            else:
                print(f"⚠️  상품을 수집하지 못했습니다")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            continue
    
    print("\n" + "=" * 70)
    print("전체 크롤링 완료!")
    print("=" * 70)
    print(f"총 수집 상품: {len(all_products)}개")
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

if __name__ == "__main__":
    asyncio.run(crawl_all_categories())
