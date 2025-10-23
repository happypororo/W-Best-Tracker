#!/usr/bin/env python3
"""
데이터베이스 모델 및 ORM
SQLite 기반 시계열 데이터 저장
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
import json

class Database:
    """데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = "wconcept_tracking.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. 제품 기본 정보 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id VARCHAR(100) UNIQUE NOT NULL,
                    product_name TEXT,
                    brand_name VARCHAR(200),
                    category VARCHAR(50),
                    category_key VARCHAR(50),
                    image_url TEXT,
                    product_url TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. 순위 및 가격 이력 테이블 (시계열 데이터)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ranking_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id VARCHAR(100) NOT NULL,
                    ranking INTEGER NOT NULL,
                    original_price INTEGER,
                    sale_price INTEGER,
                    discount_rate DECIMAL(5,2),
                    collected_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            """)
            
            # 3. 브랜드 정보 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand_name VARCHAR(200) UNIQUE NOT NULL,
                    total_products INTEGER DEFAULT 0,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 4. 브랜드 통계 이력 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brand_stats_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand_name VARCHAR(200) NOT NULL,
                    product_count INTEGER NOT NULL,
                    avg_ranking DECIMAL(10,2),
                    avg_price DECIMAL(10,2),
                    min_price INTEGER,
                    max_price INTEGER,
                    avg_discount_rate DECIMAL(5,2),
                    collected_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (brand_name) REFERENCES brands(brand_name)
                )
            """)
            
            # 5. 순위 변동 로그 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ranking_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id VARCHAR(100) NOT NULL,
                    previous_ranking INTEGER,
                    current_ranking INTEGER,
                    change_amount INTEGER,
                    change_type VARCHAR(20),
                    changed_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            """)
            
            # 6. 가격 변동 로그 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id VARCHAR(100) NOT NULL,
                    previous_sale_price INTEGER,
                    current_sale_price INTEGER,
                    price_change_amount INTEGER,
                    price_change_percentage DECIMAL(5,2),
                    previous_discount_rate DECIMAL(5,2),
                    current_discount_rate DECIMAL(5,2),
                    changed_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            """)
            
            # 7. 크롤링 작업 로그 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraping_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    status VARCHAR(50) NOT NULL,
                    products_collected INTEGER DEFAULT 0,
                    error_message TEXT,
                    execution_time_seconds INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 인덱스 생성 (성능 최적화)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ranking_history_collected_at 
                ON ranking_history(collected_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ranking_history_product_time 
                ON ranking_history(product_id, collected_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ranking_history_ranking 
                ON ranking_history(ranking)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_brand_stats_collected_at 
                ON brand_stats_history(collected_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ranking_changes_changed_at 
                ON ranking_changes(changed_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_price_changes_changed_at 
                ON price_changes(changed_at)
            """)
            
            print("✅ 데이터베이스 초기화 완료")
    
    def save_products(self, products: List[Dict]) -> int:
        """크롤링한 상품 데이터 저장"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            saved_count = 0
            collected_at = datetime.now()
            
            for product in products:
                try:
                    # 1. 제품 기본 정보 저장/업데이트
                    cursor.execute("""
                        INSERT INTO products (product_id, product_name, brand_name, category, category_key, image_url, product_url, last_seen, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(product_id) DO UPDATE SET
                            product_name = excluded.product_name,
                            brand_name = excluded.brand_name,
                            category = excluded.category,
                            category_key = excluded.category_key,
                            image_url = excluded.image_url,
                            product_url = excluded.product_url,
                            last_seen = excluded.last_seen,
                            updated_at = excluded.updated_at
                    """, (
                        product['product_id'],
                        product['product_name'],
                        product['brand_name'],
                        product.get('category', 'N/A'),
                        product.get('category_key', 'unknown'),
                        product['image_url'],
                        product['product_url'],
                        collected_at,
                        collected_at
                    ))
                    
                    # 2. 순위 및 가격 이력 저장
                    cursor.execute("""
                        INSERT INTO ranking_history (
                            product_id, ranking, original_price, sale_price, 
                            discount_rate, collected_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        product['product_id'],
                        product['rank'],
                        product['original_price'],
                        product['sale_price'],
                        product['discount_rate'],
                        collected_at
                    ))
                    
                    # 3. 브랜드 정보 저장/업데이트
                    if product['brand_name'] and product['brand_name'] != 'N/A':
                        cursor.execute("""
                            INSERT INTO brands (brand_name, last_updated)
                            VALUES (?, ?)
                            ON CONFLICT(brand_name) DO UPDATE SET
                                last_updated = excluded.last_updated
                        """, (product['brand_name'], collected_at))
                    
                    # 4. 순위 변동 감지 및 저장
                    self._detect_ranking_change(cursor, product, collected_at)
                    
                    # 5. 가격 변동 감지 및 저장
                    self._detect_price_change(cursor, product, collected_at)
                    
                    saved_count += 1
                    
                except Exception as e:
                    print(f"⚠️  상품 저장 실패 ({product.get('product_id', 'unknown')}): {str(e)}")
                    continue
            
            # 6. 브랜드 통계 저장
            self._save_brand_stats(cursor, collected_at)
            
            print(f"✅ {saved_count}개 상품 데이터베이스에 저장 완료")
            return saved_count
    
    def _detect_ranking_change(self, cursor, product: Dict, current_time: datetime):
        """순위 변동 감지"""
        
        # 이전 순위 조회 (가장 최근 데이터)
        cursor.execute("""
            SELECT ranking FROM ranking_history
            WHERE product_id = ?
            AND collected_at < ?
            ORDER BY collected_at DESC
            LIMIT 1
        """, (product['product_id'], current_time))
        
        result = cursor.fetchone()
        
        if result:
            previous_ranking = result[0]
            current_ranking = product['rank']
            
            if previous_ranking != current_ranking:
                change_amount = previous_ranking - current_ranking  # 양수: 순위 상승, 음수: 순위 하락
                change_type = 'up' if change_amount > 0 else 'down'
                
                cursor.execute("""
                    INSERT INTO ranking_changes (
                        product_id, previous_ranking, current_ranking,
                        change_amount, change_type, changed_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    product['product_id'],
                    previous_ranking,
                    current_ranking,
                    change_amount,
                    change_type,
                    current_time
                ))
    
    def _detect_price_change(self, cursor, product: Dict, current_time: datetime):
        """가격 변동 감지"""
        
        # 이전 가격 조회
        cursor.execute("""
            SELECT sale_price, discount_rate FROM ranking_history
            WHERE product_id = ?
            AND collected_at < ?
            ORDER BY collected_at DESC
            LIMIT 1
        """, (product['product_id'], current_time))
        
        result = cursor.fetchone()
        
        if result:
            previous_price = result[0]
            previous_discount = result[1]
            current_price = product['sale_price']
            current_discount = product['discount_rate']
            
            if previous_price and current_price and previous_price != current_price:
                price_change = current_price - previous_price
                price_change_pct = (price_change / previous_price * 100) if previous_price else 0
                
                cursor.execute("""
                    INSERT INTO price_changes (
                        product_id, previous_sale_price, current_sale_price,
                        price_change_amount, price_change_percentage,
                        previous_discount_rate, current_discount_rate, changed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product['product_id'],
                    previous_price,
                    current_price,
                    price_change,
                    price_change_pct,
                    previous_discount,
                    current_discount,
                    current_time
                ))
    
    def _save_brand_stats(self, cursor, collected_at: datetime):
        """브랜드별 통계 저장"""
        
        cursor.execute("""
            SELECT 
                p.brand_name,
                COUNT(*) as product_count,
                AVG(rh.ranking) as avg_ranking,
                AVG(rh.sale_price) as avg_price,
                MIN(rh.sale_price) as min_price,
                MAX(rh.sale_price) as max_price,
                AVG(rh.discount_rate) as avg_discount_rate
            FROM ranking_history rh
            JOIN products p ON rh.product_id = p.product_id
            WHERE rh.collected_at = ?
            AND p.brand_name IS NOT NULL
            AND p.brand_name != 'N/A'
            GROUP BY p.brand_name
        """, (collected_at,))
        
        stats = cursor.fetchall()
        
        for stat in stats:
            cursor.execute("""
                INSERT INTO brand_stats_history (
                    brand_name, product_count, avg_ranking, avg_price,
                    min_price, max_price, avg_discount_rate, collected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stat[0],  # brand_name
                stat[1],  # product_count
                stat[2],  # avg_ranking
                stat[3],  # avg_price
                stat[4],  # min_price
                stat[5],  # max_price
                stat[6],  # avg_discount_rate
                collected_at
            ))
    
    def log_scraping_job(self, started_at: datetime, status: str, 
                        products_collected: int = 0, 
                        error_message: str = None,
                        execution_time: int = None) -> int:
        """크롤링 작업 로그 저장"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO scraping_logs (
                    started_at, completed_at, status, products_collected,
                    error_message, execution_time_seconds
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                started_at,
                datetime.now(),
                status,
                products_collected,
                error_message,
                execution_time
            ))
            
            return cursor.lastrowid
    
    def get_latest_rankings(self, limit: int = 200) -> List[Dict]:
        """최신 순위 조회"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    rh.ranking,
                    p.product_id,
                    p.product_name,
                    p.brand_name,
                    rh.original_price,
                    rh.sale_price,
                    rh.discount_rate,
                    p.image_url,
                    p.product_url,
                    rh.collected_at
                FROM ranking_history rh
                JOIN products p ON rh.product_id = p.product_id
                WHERE rh.collected_at = (SELECT MAX(collected_at) FROM ranking_history)
                ORDER BY rh.ranking
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_brand_statistics(self, hours: int = 24) -> List[Dict]:
        """브랜드별 통계 조회"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    brand_name,
                    AVG(product_count) as avg_product_count,
                    AVG(avg_ranking) as avg_ranking,
                    AVG(avg_price) as avg_price,
                    AVG(avg_discount_rate) as avg_discount_rate
                FROM brand_stats_history
                WHERE collected_at >= datetime('now', '-' || ? || ' hours')
                GROUP BY brand_name
                ORDER BY avg_product_count DESC
            """, (hours,))
            
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_product_history(self, product_id: str, days: int = 7) -> List[Dict]:
        """특정 상품의 순위/가격 변동 이력"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    ranking,
                    original_price,
                    sale_price,
                    discount_rate,
                    collected_at
                FROM ranking_history
                WHERE product_id = ?
                AND collected_at >= datetime('now', '-' || ? || ' days')
                ORDER BY collected_at ASC
            """, (product_id, days))
            
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_ranking_movers(self, change_type: str = 'up', limit: int = 20) -> List[Dict]:
        """순위 급변동 상품 조회"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            order = 'DESC' if change_type == 'up' else 'ASC'
            
            cursor.execute(f"""
                SELECT 
                    rc.product_id,
                    p.product_name,
                    p.brand_name,
                    rc.previous_ranking,
                    rc.current_ranking,
                    rc.change_amount,
                    rc.changed_at
                FROM ranking_changes rc
                JOIN products p ON rc.product_id = p.product_id
                WHERE rc.changed_at >= datetime('now', '-24 hours')
                AND rc.change_type = ?
                ORDER BY ABS(rc.change_amount) {order}
                LIMIT ?
            """, (change_type, limit))
            
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_price_changes(self, hours: int = 24) -> Dict:
        """가격 변동 분석"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 가격 인상
            cursor.execute("""
                SELECT 
                    pc.product_id,
                    p.product_name,
                    p.brand_name,
                    pc.previous_sale_price,
                    pc.current_sale_price,
                    pc.price_change_amount,
                    pc.price_change_percentage
                FROM price_changes pc
                JOIN products p ON pc.product_id = p.product_id
                WHERE pc.changed_at >= datetime('now', '-' || ? || ' hours')
                AND pc.price_change_amount > 0
                ORDER BY pc.price_change_percentage DESC
                LIMIT 20
            """, (hours,))
            
            price_increased = [dict(row) for row in cursor.fetchall()]
            
            # 가격 인하
            cursor.execute("""
                SELECT 
                    pc.product_id,
                    p.product_name,
                    p.brand_name,
                    pc.previous_sale_price,
                    pc.current_sale_price,
                    pc.price_change_amount,
                    pc.price_change_percentage
                FROM price_changes pc
                JOIN products p ON pc.product_id = p.product_id
                WHERE pc.changed_at >= datetime('now', '-' || ? || ' hours')
                AND pc.price_change_amount < 0
                ORDER BY pc.price_change_percentage ASC
                LIMIT 20
            """, (hours,))
            
            price_decreased = [dict(row) for row in cursor.fetchall()]
            
            return {
                'price_increased': price_increased,
                'price_decreased': price_decreased
            }
    
    def get_database_stats(self) -> Dict:
        """데이터베이스 통계"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # 총 제품 수
            cursor.execute("SELECT COUNT(*) FROM products")
            stats['total_products'] = cursor.fetchone()[0]
            
            # 총 브랜드 수
            cursor.execute("SELECT COUNT(*) FROM brands")
            stats['total_brands'] = cursor.fetchone()[0]
            
            # 총 데이터 포인트 수
            cursor.execute("SELECT COUNT(*) FROM ranking_history")
            stats['total_data_points'] = cursor.fetchone()[0]
            
            # 첫 수집 시간
            cursor.execute("SELECT MIN(collected_at) FROM ranking_history")
            stats['first_collection'] = cursor.fetchone()[0]
            
            # 최근 수집 시간
            cursor.execute("SELECT MAX(collected_at) FROM ranking_history")
            stats['last_collection'] = cursor.fetchone()[0]
            
            # 총 크롤링 작업 수
            cursor.execute("SELECT COUNT(*) FROM scraping_logs")
            stats['total_scraping_jobs'] = cursor.fetchone()[0]
            
            # 성공한 작업 수
            cursor.execute("SELECT COUNT(*) FROM scraping_logs WHERE status = 'success'")
            stats['successful_jobs'] = cursor.fetchone()[0]
            
            return stats


if __name__ == "__main__":
    # 데이터베이스 초기화 테스트
    print("=" * 70)
    print("데이터베이스 초기화 테스트")
    print("=" * 70)
    print()
    
    db = Database()
    
    print("\n✅ 데이터베이스 생성 완료!")
    print(f"   파일 위치: {db.db_path}")
    
    # 통계 확인
    stats = db.get_database_stats()
    print("\n📊 데이터베이스 통계:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
