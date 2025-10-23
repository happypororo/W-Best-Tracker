#!/usr/bin/env python3
"""
기존 JSON 데이터를 데이터베이스에 임포트하는 테스트 스크립트
"""

import json
from database import Database
from datetime import datetime

def import_json_to_db(json_file: str):
    """JSON 파일을 데이터베이스에 임포트"""
    
    print("=" * 70)
    print("JSON 데이터 → 데이터베이스 임포트")
    print("=" * 70)
    print()
    
    # JSON 파일 읽기
    print(f"📂 파일 읽기: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ {data['total_products']}개 상품 데이터 로드 완료")
    print(f"   수집 시간: {data['collected_at']}")
    
    # 데이터베이스에 저장
    print("\n💾 데이터베이스에 저장 중...")
    db = Database()
    
    start_time = datetime.now()
    saved_count = db.save_products(data['products'])
    end_time = datetime.now()
    
    execution_time = (end_time - start_time).total_seconds()
    
    # 크롤링 로그 저장
    db.log_scraping_job(
        started_at=datetime.fromisoformat(data['collected_at']),
        status='success',
        products_collected=saved_count,
        execution_time=int(execution_time)
    )
    
    print(f"\n✅ 데이터베이스 저장 완료!")
    print(f"   저장된 상품: {saved_count}개")
    print(f"   소요 시간: {execution_time:.2f}초")
    
    # 데이터베이스 통계 확인
    print("\n" + "=" * 70)
    print("데이터베이스 통계")
    print("=" * 70)
    
    stats = db.get_database_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 최신 Top 10 조회
    print("\n" + "=" * 70)
    print("최신 Top 10 상품")
    print("=" * 70)
    
    top_products = db.get_latest_rankings(limit=10)
    for product in top_products:
        print(f"\n   [{product['ranking']}] {product['brand_name']} - {product['product_name'][:50]}")
        print(f"       가격: {product['sale_price']:,}원 (할인: {product['discount_rate']}%)")
    
    # 브랜드 통계 조회
    print("\n" + "=" * 70)
    print("브랜드 통계 Top 10")
    print("=" * 70)
    
    brand_stats = db.get_brand_statistics(hours=24)
    for i, brand in enumerate(brand_stats[:10], 1):
        print(f"   {i:2d}. {brand['brand_name']:30s} : {brand['avg_product_count']:.0f}개 "
              f"(평균 순위: {brand['avg_ranking']:.1f}, 평균 가격: {brand['avg_price']:,.0f}원)")

if __name__ == "__main__":
    # 최신 JSON 파일 찾기
    import os
    import glob
    
    json_files = sorted(glob.glob('/home/user/webapp/wconcept_data_*.json'))
    
    if json_files:
        latest_file = json_files[-1]
        import_json_to_db(latest_file)
    else:
        print("❌ JSON 파일을 찾을 수 없습니다.")
