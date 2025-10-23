#!/usr/bin/env python3
"""
데이터 분석 및 통계 도구
"""

from database import Database
from datetime import datetime, timedelta
import json

class Analytics:
    """데이터 분석 클래스"""
    
    def __init__(self):
        self.db = Database()
    
    def print_current_rankings(self, limit: int = 20):
        """현재 순위 출력"""
        print("\n" + "=" * 70)
        print(f"현재 Top {limit} 상품")
        print("=" * 70)
        
        products = self.db.get_latest_rankings(limit=limit)
        
        if not products:
            print("데이터가 없습니다.")
            return
        
        print(f"\n수집 시간: {products[0]['collected_at']}")
        print()
        
        for product in products:
            print(f"[{product['ranking']:3d}위] {product['brand_name']:20s} | {product['product_name'][:45]}")
            print(f"        가격: {product['sale_price']:,}원", end="")
            if product['discount_rate']:
                print(f" ({product['discount_rate']}% 할인)")
            else:
                print()
    
    def print_brand_statistics(self, hours: int = 24, limit: int = 20):
        """브랜드 통계 출력"""
        print("\n" + "=" * 70)
        print(f"브랜드 통계 (최근 {hours}시간)")
        print("=" * 70)
        
        stats = self.db.get_brand_statistics(hours=hours)
        
        if not stats:
            print("데이터가 없습니다.")
            return
        
        print(f"\n{'순위':4s} {'브랜드명':25s} {'제품수':8s} {'평균순위':10s} {'평균가격':12s} {'평균할인율':10s}")
        print("-" * 70)
        
        for i, brand in enumerate(stats[:limit], 1):
            discount = brand['avg_discount_rate'] if brand['avg_discount_rate'] else 0
            print(f"{i:3d}. {brand['brand_name']:25s} "
                  f"{brand['avg_product_count']:7.1f}개 "
                  f"{brand['avg_ranking']:9.1f} "
                  f"{brand['avg_price']:11,.0f}원 "
                  f"{discount:9.1f}%")
    
    def print_product_history(self, product_id: str, days: int = 7):
        """특정 상품의 이력 출력"""
        print("\n" + "=" * 70)
        print(f"상품 이력 (최근 {days}일)")
        print("=" * 70)
        
        history = self.db.get_product_history(product_id, days=days)
        
        if not history:
            print(f"상품 ID '{product_id}'의 데이터가 없습니다.")
            return
        
        print(f"\n{'수집 시간':20s} {'순위':6s} {'원가':12s} {'판매가':12s} {'할인율':8s}")
        print("-" * 70)
        
        for record in history:
            print(f"{record['collected_at']:20s} "
                  f"{record['ranking']:5d}위 "
                  f"{record['original_price']:11,}원 "
                  f"{record['sale_price']:11,}원 "
                  f"{record['discount_rate']:7.0f}%")
        
        # 변동 분석
        if len(history) >= 2:
            first = history[0]
            last = history[-1]
            
            rank_change = first['ranking'] - last['ranking']
            price_change = last['sale_price'] - first['sale_price']
            
            print("\n변동 분석:")
            if rank_change > 0:
                print(f"  ▲ 순위 {rank_change}계단 상승")
            elif rank_change < 0:
                print(f"  ▼ 순위 {abs(rank_change)}계단 하락")
            else:
                print(f"  - 순위 변동 없음")
            
            if price_change != 0:
                price_change_pct = (price_change / first['sale_price'] * 100)
                print(f"  가격 변동: {price_change:+,}원 ({price_change_pct:+.1f}%)")
    
    def print_ranking_movers(self, change_type: str = 'up', limit: int = 10):
        """순위 급변동 상품 출력"""
        type_name = "급상승" if change_type == 'up' else "급하락"
        
        print("\n" + "=" * 70)
        print(f"순위 {type_name} Top {limit} (최근 24시간)")
        print("=" * 70)
        
        movers = self.db.get_ranking_movers(change_type=change_type, limit=limit)
        
        if not movers:
            print(f"순위 {type_name} 데이터가 없습니다.")
            return
        
        print(f"\n{'순위':4s} {'브랜드명':20s} {'상품명':30s} {'이전→현재':12s} {'변동':8s}")
        print("-" * 70)
        
        for i, mover in enumerate(movers, 1):
            change_symbol = "▲" if mover['change_amount'] > 0 else "▼"
            print(f"{i:3d}. {mover['brand_name']:20s} "
                  f"{mover['product_name'][:28]:30s} "
                  f"{mover['previous_ranking']:3d}→{mover['current_ranking']:3d}위 "
                  f"{change_symbol}{abs(mover['change_amount']):3d}위")
    
    def print_price_changes(self, hours: int = 24):
        """가격 변동 분석 출력"""
        print("\n" + "=" * 70)
        print(f"가격 변동 분석 (최근 {hours}시간)")
        print("=" * 70)
        
        changes = self.db.get_price_changes(hours=hours)
        
        # 가격 인상
        print("\n💰 가격 인상 Top 10:")
        if changes['price_increased']:
            for i, item in enumerate(changes['price_increased'][:10], 1):
                print(f"{i:2d}. {item['brand_name']:20s} | {item['product_name'][:35]}")
                print(f"    {item['previous_sale_price']:,}원 → {item['current_sale_price']:,}원 "
                      f"(+{item['price_change_percentage']:.1f}%)")
        else:
            print("   (없음)")
        
        # 가격 인하
        print("\n💸 가격 인하 Top 10:")
        if changes['price_decreased']:
            for i, item in enumerate(changes['price_decreased'][:10], 1):
                print(f"{i:2d}. {item['brand_name']:20s} | {item['product_name'][:35]}")
                print(f"    {item['previous_sale_price']:,}원 → {item['current_sale_price']:,}원 "
                      f"({item['price_change_percentage']:.1f}%)")
        else:
            print("   (없음)")
    
    def print_database_stats(self):
        """데이터베이스 통계 출력"""
        print("\n" + "=" * 70)
        print("데이터베이스 통계")
        print("=" * 70)
        
        stats = self.db.get_database_stats()
        
        print(f"\n📊 전체 통계:")
        print(f"   총 제품 수: {stats['total_products']}개")
        print(f"   총 브랜드 수: {stats['total_brands']}개")
        print(f"   총 데이터 포인트: {stats['total_data_points']}개")
        
        print(f"\n📅 수집 기간:")
        print(f"   첫 수집: {stats['first_collection']}")
        print(f"   최근 수집: {stats['last_collection']}")
        
        print(f"\n🤖 크롤링 작업:")
        print(f"   총 작업 수: {stats['total_scraping_jobs']}회")
        print(f"   성공한 작업: {stats['successful_jobs']}회")
        if stats['total_scraping_jobs'] > 0:
            success_rate = (stats['successful_jobs'] / stats['total_scraping_jobs'] * 100)
            print(f"   성공률: {success_rate:.1f}%")
    
    def export_to_json(self, filename: str = None):
        """현재 데이터를 JSON으로 내보내기"""
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'exported_at': datetime.now().isoformat(),
            'current_rankings': self.db.get_latest_rankings(limit=200),
            'brand_statistics': self.db.get_brand_statistics(hours=24),
            'database_stats': self.db.get_database_stats()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n✅ 데이터 내보내기 완료: {filename}")
        return filename


def main():
    """메인 함수"""
    import sys
    
    analytics = Analytics()
    
    if len(sys.argv) < 2:
        command = 'menu'
    else:
        command = sys.argv[1]
    
    if command == 'rankings' or command == '1':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        analytics.print_current_rankings(limit=limit)
    
    elif command == 'brands' or command == '2':
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        analytics.print_brand_statistics(hours=hours)
    
    elif command == 'history' or command == '3':
        if len(sys.argv) < 3:
            print("❌ 상품 ID를 입력하세요.")
            print("   예: python analytics.py history PROD_307602440")
            return
        product_id = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        analytics.print_product_history(product_id, days=days)
    
    elif command == 'movers-up' or command == '4':
        analytics.print_ranking_movers(change_type='up')
    
    elif command == 'movers-down' or command == '5':
        analytics.print_ranking_movers(change_type='down')
    
    elif command == 'prices' or command == '6':
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        analytics.print_price_changes(hours=hours)
    
    elif command == 'stats' or command == '7':
        analytics.print_database_stats()
    
    elif command == 'export' or command == '8':
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        analytics.export_to_json(filename)
    
    elif command == 'all' or command == '9':
        analytics.print_database_stats()
        analytics.print_current_rankings(limit=10)
        analytics.print_brand_statistics(hours=24, limit=10)
        analytics.print_ranking_movers(change_type='up', limit=5)
        analytics.print_price_changes(hours=24)
    
    else:
        # 메뉴 표시
        print("\n" + "=" * 70)
        print("W컨셉 데이터 분석 도구")
        print("=" * 70)
        print("\n사용법:")
        print("  python analytics.py <command> [options]")
        print("\n명령어:")
        print("  1. rankings [limit]        현재 순위 표시 (기본: 20개)")
        print("  2. brands [hours]          브랜드 통계 (기본: 24시간)")
        print("  3. history <product_id>    상품 이력 조회")
        print("  4. movers-up               순위 급상승 Top 10")
        print("  5. movers-down             순위 급하락 Top 10")
        print("  6. prices [hours]          가격 변동 분석 (기본: 24시간)")
        print("  7. stats                   데이터베이스 통계")
        print("  8. export [filename]       JSON으로 내보내기")
        print("  9. all                     전체 리포트 표시")
        print("\n예제:")
        print("  python analytics.py rankings 50")
        print("  python analytics.py brands 48")
        print("  python analytics.py history PROD_307602440")
        print("  python analytics.py movers-up")
        print("  python analytics.py all")


if __name__ == "__main__":
    main()
